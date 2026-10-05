"""Saved power mathematics coupled to independently rederived sealed geometry."""
from dataclasses import asdict
from fractions import Fraction as F
from exp7core.simulations import binomial_interval
from .common import SCHEMA, PRODUCTION, FAMILIES, PREDICTORS, KERNEL_VERSION, require, pin, digest, decode
from .saved_math import VERSION, equal, validate_geometry, outcome_summary, checked_bound


def unrun_record(base, fit):
    return {**base, "status": "UNSUPPORTED", "fit": fit, "N": 0,
            "fire_count": None, "p_fires": None, "mean_D": None}


def verify_fit(fit, families, subset, n, m, target, spec):
    from .power import fit_target
    if target is None:
        expected = {"status": "SUPPORTED", "rho": 0.0, "note": "prespecified null arm"}
    else:
        require(type(fit) is dict and type(fit.get("evaluations")) in (tuple, list), "fit evaluation trace")
        trace, position = fit["evaluations"], [0]
        def replay(phase, rho):
            require(position[0] < len(trace), "missing fit evaluation")
            row = trace[position[0]]
            position[0] += 1
            require(type(row) is dict and set(row) == {"phase", "rho", "summary"}
                    and row["phase"] == phase and type(row["rho"]) is float and row["rho"] == rho, "fit bisection path/rho")
            summary = row["summary"]
            require(type(summary) is dict, "fit summary")
            expected_summary = outcome_summary(families, subset, summary.get("outcomes"),
                spec.n_cal if phase == "fit" else spec.n_validate, n, m, rho_one=rho == 1)[0]
            equal(summary, expected_summary, "fit D/count/scatter arithmetic")
            return expected_summary
        expected = fit_target(lambda rho: replay("fit", rho), lambda rho: replay("validation", rho), target, spec)
        require(position[0] == len(trace), "extra/retried fit evaluation")
    equal(fit, expected, "fit endpoint/final/validation status arithmetic")
    return expected


def main_record(base, fit, outcomes, mc, families, spec):
    subset, n, m, target = tuple(base["subset"]), base["n_positive"], base["max_count"], base["target_D"]
    summary, eligible, extrema = outcome_summary(families, subset, outcomes, spec.n_sim, n, m, rho_one=fit["rho"] == 1)
    require(type(mc) in (list, tuple) and len(mc) == spec.n_sim, "main MC trace count")
    fires = rejects = consumed = 0
    for d, e, limits, bound in zip(summary["Ds"], eligible, extrema, mc):
        if tuple(e["eligible"]) != subset:
            require(d is None, "subset loss must have undefined D")
            equal(bound, {"status": "EXACT_SUBSET_LOSS", "eligible": e["eligible"]}, "subset loss MC reading")
            continue
        require(d is not None, "exact subset cannot have undefined D")
        decision = checked_bound(bound, spec.permutations, all_ge=d == limits["low"])
        rejects += decision["reject"]
        fires += decision["reject"] and d >= F(1, 10)
        consumed += decision["consumed"]
    mean_d = summary["mean_D"]
    unsupported = target is not None and (mean_d is None or abs(mean_d-target) > spec.tolerance)
    return {**base, "status": "UNSUPPORTED" if unsupported else "SUPPORTED",
            "reason": "main mean D uninformative or outside target tolerance" if unsupported else None,
            "fit": fit, "N": spec.n_sim, "main_outcomes": outcomes,
            "fire_count": int(fires), "p_only_count": int(rejects), "p_fires": F(fires, spec.n_sim),
            "interval95": binomial_interval(fires, spec.n_sim), "p_only_interval95": binomial_interval(rejects, spec.n_sim),
            "mean_D": mean_d, "Ds": summary["Ds"], "D_scatter": summary["scatter"],
            "eligibility": eligible, "permutation_bounds": mc, "permutations_consumed": consumed,
            "eligible_set_counts": {"-".join(s): sum(tuple(e["eligible"]) == s for e in eligible)
                                    for s in sorted({tuple(e["eligible"]) for e in eligible})}}


def verify(record, seal_sha256, battery_sha256, *, geometry, spec):
    from .power import SPEC, grid, cell_id, declarations, SUBSETS
    geometry = validate_geometry(geometry, production=spec == SPEC)
    record = decode(record)
    require(type(record) is dict, "power record mapping")
    require(record.get("schema") == SCHEMA and record.get("stage") == "power" and record.get("state") == "COMPLETE"
            and record.get("production") is True and record.get("saved_math_version") == VERSION, "power saved-math version/stage")
    require(record.get("seal_sha256") == pin(seal_sha256) and record.get("battery_sha256") == pin(battery_sha256), "power identity")
    require(record.get("geometry_sha256") == digest(geometry), "independent geometry binding")
    equal(record.get("predictor_support"), geometry["support"], "independent predictor support")
    equal(record.get("spec"), asdict(spec), "power specification")
    equal(record.get("grid"), PRODUCTION.grid, "power grid")
    rows = record.get("rows")
    require(type(rows) is dict and set(rows) == {cell_id(*g) for g in grid(spec)}, "power full address coverage")
    for p, subset, n, m, target in grid(spec):
        name = cell_id(p, subset, n, m, target)
        row = rows[name]
        base = {"id": name, "predictor": p, "subset": subset, "n_positive": n, "max_count": m,
                "target_D": target, "kernel": KERNEL_VERSION}
        fit = verify_fit(row.get("fit"), geometry["predictors"][p], subset, n, m, target, spec)
        expected = (unrun_record(base, fit) if fit["status"] == "UNSUPPORTED" else
                    main_record(base, fit, row.get("main_outcomes"), row.get("permutation_bounds"), geometry["predictors"][p], spec))
        equal(row, expected, "power saved outcome/MC/count/interval/scatter/status arithmetic")
    expected_declarations = declarations(rows, spec)
    equal(record.get("declarations"), expected_declarations, "power declarations")
    equal(record.get("run_stop_required"), any(v["status"] != "FORECAST-POWERED" for v in expected_declarations.values()), "power run/stop")
    thin = {f"{p}/{'-'.join(s)}": {"state": "THIN", "predictor": p, "subset": s, "n_positive": 10, "eligible": (),
                                 "reason": "Every family has fewer than20 joint-positive pairs."} for p in PREDICTORS for s in SUBSETS}
    equal(record.get("thin_fixtures"), thin, "power THIN fixtures")
    require(type(record.get("source_bindings")) is dict and record["source_bindings"], "power source bindings")
    for sha in record["source_bindings"].values():
        pin(sha)
    if spec == SPEC:
        from .calibration import verify_envelope_semantics
        verify_envelope_semantics(record.get("selectivity_envelope"))
        for key in ("code_manifest", "source_manifest", "calibration", "contact_inventory"):
            pin(record["source_bindings"].get(key))
        require(pin(record.get("calibration_sha256")) == record["source_bindings"]["calibration"], "calibration binding")
    return record
