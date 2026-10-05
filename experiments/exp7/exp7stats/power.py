"""Once-only predictor-conditioned forecast power; never reads actual outcomes.

Production run() has frozen counts. Tests use the explicit miniature helpers
and scripted orchestration; the production grid must not run during BUILD.
"""
from dataclasses import dataclass, asdict
from fractions import Fraction as F
from itertools import combinations
import numpy as np
from exp7core.inference import Cell, eligibility, mean
from exp7core.simulations import binomial_interval
from exp7core.records import strict_json
from exp7core.guardio import safe_path
from .common import (SCHEMA, FAMILIES, PREDICTORS, POSITIVE_COUNTS, COUNT_RANGES,
                     D_TARGETS, PRODUCTION, Shape, require, pin, digest, receipt,
                     stage, require_protocol, require_preoutcome, decode, KERNEL_VERSION)
from .data import load_battery, load_predictors, predictor_support
from .kernels import rng, rank_codes, batch_somers, forecast, decision, require_runtime
from .saved_math import (VERSION, scatter, pack, predictor_geometry, outcome_summary,
                         BOUND_KEYS)

SUBSETS = tuple(combinations(FAMILIES, 3)) + (FAMILIES,)


@dataclass(frozen=True)
class PowerSpec:
    n_sim: int = 128
    n_cal: int = 64
    n_validate: int = 128
    iterations: int = 24
    permutations: int = 10000
    positive_counts: tuple = POSITIVE_COUNTS
    count_ranges: tuple = COUNT_RANGES
    targets: tuple = D_TARGETS
    tolerance: F = F(1, 200)

    def __post_init__(self):
        require(all(type(x) is int and x > 0 for x in
                    (self.n_sim, self.n_cal, self.n_validate, self.iterations, self.permutations)), "power counts")
        require(self.positive_counts and all(type(x) is int and x >= 20 for x in self.positive_counts), "positive grid")
        require(self.count_ranges and all(type(x) is int and 1 <= x <= 26 for x in self.count_ranges), "count ranges")
        require(self.targets and all(type(x) is F and 0 < x <= 1 for x in self.targets), "D targets")
        require(type(self.tolerance) is F and 0 < self.tolerance < 1, "target tolerance")


SPEC = PowerSpec()


def cell_id(predictor, subset, n_positive, max_count, target):
    effect = "null" if target is None else f"D{target.numerator}_{target.denominator}"
    return f"{predictor}/{'-'.join(subset)}/p{n_positive}/y{max_count}/{effect}"


def grid(spec=SPEC):
    for p in PREDICTORS:
        for subset in SUBSETS:
            for n in spec.positive_counts:
                for max_count in spec.count_ranges:
                    for target in (*spec.targets, None):
                        yield (p, subset, n, max_count, target)


def standardized_ranks(values):
    codes = rank_codes(values)
    counts = np.bincount(codes)
    ranks = np.cumsum(counts) - (counts+1)/2
    z = ranks[codes]
    sd = float(np.std(z))
    return (z - np.mean(z)) / sd if sd else np.zeros(len(z))


class LatentBank:
    """Fixed common noise within a fit; independent banks for validation/main."""
    def __init__(self, predictor, subset, *, n_reps, namespace):
        self.predictor, self.subset, self.n_reps = predictor, tuple(subset), n_reps
        self.z, self.noise, self.tie = {}, {}, {}
        for f in subset:
            x = tuple(s.x for s in predictor.family(f))
            self.z[f] = standardized_ranks(x)
            self.noise[f] = rng(namespace, f, "gaussian").standard_normal((n_reps, len(x)))
            self.tie[f] = rng(namespace, f, "tie").random((n_reps, len(x)))

    def outcomes(self, rho, n_positive, max_count):
        require(0 <= rho <= 1 and all(n_positive <= len(z) for z in self.z.values()), "latent domain")
        out = {}
        for f in self.subset:
            latent = rho*self.z[f][None, :] + np.sqrt(1-rho*rho)*self.noise[f]
            order = np.lexsort((self.tie[f], -latent), axis=1)[:, :n_positive]
            y = np.zeros_like(latent, dtype=np.int64)
            values = max_count - np.arange(n_positive)*max_count // n_positive
            np.put_along_axis(y, order, np.broadcast_to(values, order.shape), axis=1)
            out[f] = y
        return out

    def means(self, rho, n_positive, max_count):
        out = self.outcomes(rho, n_positive, max_count)
        return outcome_summary(local_geometry(self.predictor), self.subset,
                               {f: pack(v) for f, v in out.items()}, self.n_reps,
                               n_positive, max_count, rho_one=rho == 1)[0]


def local_geometry(predictor):
    from .common import dumps
    return {f: {"x": tuple(s.x for s in predictor.family(f)),
                "strata": tuple(dumps(s).decode().strip() for s in dict(predictor.strata)[f])}
            for f in FAMILIES}


def fit_target(evaluate, validate, target, spec):
    """Total at endpoints, interior, final AND validation; no replacement noise."""
    target = F(target)
    trace = []
    original_evaluate, original_validate = evaluate, validate
    def capture(function, phase, rho):
        value = function(rho)
        trace.append({"phase": phase, "rho": rho, "summary": value})
        return value
    evaluate = lambda rho: capture(original_evaluate, "fit", rho)
    validate = lambda rho: capture(original_validate, "validation", rho)
    low, high = evaluate(0.0), evaluate(1.0)
    record = {"target": target, "null_fit": low, "ceiling_fit": high,
              "tolerance": spec.tolerance, "iterations": spec.iterations, "evaluations": trace}
    def unsupported(reason, **extra):
        return {**record, "status": "UNSUPPORTED", "reason": reason, "rho": None,
                "mean_D": None, **extra}
    a, b = low["mean_D"], high["mean_D"]
    if a is None or b is None:
        return unsupported("uninformative endpoint outcome")
    if b < target-spec.tolerance or a > target+spec.tolerance:
        return unsupported("target outside frozen shape endpoint means")
    lo, hi = 0.0, 1.0
    for _ in range(spec.iterations):
        mid = (lo+hi)/2
        got = evaluate(mid)
        if got["mean_D"] is None:
            return unsupported("uninformative interior outcome")
        if got["mean_D"] < target:
            lo = mid
        else:
            hi = mid
    rho = (lo+hi)/2
    fitted = evaluate(rho)
    if fitted["mean_D"] is None:
        return unsupported("uninformative final outcome", final_fit=fitted)
    if abs(fitted["mean_D"]-target) > spec.tolerance:
        return unsupported("final mean D misses target", final_fit=fitted)
    validation = validate(rho)
    if validation["mean_D"] is None:
        return unsupported("uninformative validation outcome", final_fit=fitted, validation=validation)
    if abs(validation["mean_D"]-target) > spec.tolerance:
        return unsupported("independent validation mean D misses target", final_fit=fitted, validation=validation)
    return {**record, "status": "SUPPORTED", "rho": rho, "mean_D": validation["mean_D"],
            "final_fit": fitted, "validation": validation}


def simulate_cell(predictor, subset, n_positive, max_count, target, spec=SPEC):
    from .power_validation import main_record, unrun_record
    cid = cell_id(predictor.name, subset, n_positive, max_count, target)
    base = {"id": cid, "predictor": predictor.name, "subset": tuple(subset),
            "n_positive": n_positive, "max_count": max_count, "target_D": target,
            "kernel": KERNEL_VERSION}
    if target is None:
        fit = {"status": "SUPPORTED", "rho": 0.0, "note": "prespecified null arm"}
    else:
        cal = LatentBank(predictor, subset, n_reps=spec.n_cal, namespace=("power", cid, "fit"))
        val = LatentBank(predictor, subset, n_reps=spec.n_validate, namespace=("power", cid, "validation"))
        fit = fit_target(lambda rho: cal.means(rho, n_positive, max_count),
                         lambda rho: val.means(rho, n_positive, max_count), target, spec)
    if fit["status"] != "SUPPORTED":
        return unrun_record(base, fit)
    bank = LatentBank(predictor, subset, n_reps=spec.n_sim, namespace=("power", cid, "main"))
    yy = bank.outcomes(fit["rho"], n_positive, max_count)
    p_bounds = []
    for b in range(spec.n_sim):
        cs = tuple(Cell(f, tuple(range(len(predictor.family(f)))), predictor.family(f),
                        tuple(int(v) for v in yy[f][b]), dict(predictor.strata)[f]) for f in subset)
        keep, information = eligibility(cs)
        if tuple(keep) != tuple(subset):
            p_bounds.append({"status": "EXACT_SUBSET_LOSS", "eligible": keep})
            continue  # explicitly counted nonfire; no replacement draw
        result = forecast(cs, subset, B=spec.permutations, namespace=("power", cid, b), full=False)
        p_bounds.append({k: result[k] for k in ("p", "p_low", "p_high", "n_ge", "consumed", "B")})
    return main_record(base, fit, {f: pack(v) for f, v in yy.items()}, p_bounds,
                       local_geometry(predictor), spec)


def declarations(rows, spec=SPEC):
    result = {}
    for p in PREDICTORS:
        for subset in SUBSETS:
            key = f"{p}/{'-'.join(subset)}"
            ids = [cell_id(p, subset, n, m, F(3, 20)) for n in spec.positive_counts for m in spec.count_ranges]
            arms = [rows.get(k) for k in ids]
            supported = all(a and a["status"] == "SUPPORTED" and a.get("p_fires") is not None for a in arms)
            minimum = min(a["p_fires"] for a in arms) if supported else None
            result[key] = {"predictor": p, "subset": subset, "arm_ids": ids,
                           "status": "FORECAST-POWERED" if supported and minimum >= F(3, 4)
                                     else "DECLARED-UNDERPOWERED-OR-UNSUPPORTED",
                           "worst_p_fires_at_D15": minimum,
                           "note": "Exact subset and finite grid only; no selectivity or joint power claim."}
    return result


def thin_fixture(predictor, subset):
    """Required deterministic ten-positive fixture; never a power alternative."""
    cs = []
    for f in subset:
        n = len(predictor.family(f))
        require(n >= 20, "THIN fixture needs at least20 pairs")
        y = tuple(26-i*26//10 if i < 10 else 0 for i in range(n))
        cs.append(Cell(f, tuple(range(n)), predictor.family(f), y, dict(predictor.strata)[f]))
    keep, readings = eligibility(tuple(cs))
    require(not keep and all(r["n_positive"] == 10 for r in readings.values()), "ten-positive fixture did not refuse")
    return {"state": "THIN", "predictor": predictor.name, "subset": tuple(subset),
            "n_positive": 10, "eligible": keep, "reason": "Every family has fewer than20 joint-positive pairs."}


def assemble(predictors, battery, seal, provenance, *, spec=SPEC, evaluator=simulate_cell):
    require(callable(evaluator), "power evaluator injection")
    rows = {}
    for p, subset, n, m, target in grid(spec):
        row = evaluator(predictors[p], subset, n, m, target, spec)
        require(row["id"] == cell_id(p, subset, n, m, target), "power cell identity")
        rows[row["id"]] = row
    decl = declarations(rows, spec)
    return {"schema": SCHEMA, "stage": "power", "state": "COMPLETE",
            "saved_math_version": VERSION, "geometry_sha256": digest(predictor_geometry(predictors)),
            "seal_sha256": seal["seal_sha256"], "battery_sha256": battery.sha256,
            "source_bindings": provenance["input_sha256"], "spec": asdict(spec),
            "grid": PRODUCTION.grid, "rows": rows, "declarations": decl,
            "thin_fixtures": {f"{p}/{'-'.join(subset)}": thin_fixture(predictors[p], subset)
                              for p in PREDICTORS for subset in SUBSETS},
            "predictor_support": {p: predictor_support(predictors[p]) for p in PREDICTORS},
            "analysis_note": "Actual selectivity test was not computed. No outcomes read.",
            "shape_note": "Family-level average-tie rank/noise ITEM-level alternative, not a class-level mechanism.",
            "run_stop_required": any(d["status"] != "FORECAST-POWERED" for d in decl.values())}


def verify_power_semantics(record, seal_sha256, battery_sha256, *, geometry=None, spec=SPEC):
    """No RNG replay. Independent sealed geometry is mandatory; v1 traces refuse."""
    from .power_validation import verify
    return verify(record, seal_sha256, battery_sha256, geometry=geometry, spec=spec)


def realized_support(record, predictors, outcomes, primary):
    result = {}
    for p in PREDICTORS:
        subset = tuple(primary[p]["eligible"])
        key = f"{p}/{'-'.join(subset)}"
        declaration = record["declarations"].get(key)
        departures, families = [], {}
        positives = []
        for f in subset:
            values = [o["y"] for o in outcomes[f]]
            count = sum(v > 0 for v in values)
            positives.append(count)
            histogram = {str(v): values.count(v) for v in sorted(set(values))}
            families[f] = {"ever_joint_positive": count, "outcome_histogram": histogram,
                           "informative_blocks": sum(b["denominator"] > 0 for b in primary[p]["families"][f]["blocks"]),
                           "row_support": predictor_support(predictors[p])[f]}
            if count not in POSITIVE_COUNTS:
                departures.append(f"{f}: positive count {count} is not a grid value")
            matches = []
            for m in COUNT_RANGES:
                expected = [0]*(len(values)-count) + [m-j*m//count for j in range(count)] if count else [0]*len(values)
                if sorted(values) == sorted(expected):
                    matches.append(m)
            families[f]["matching_count_shapes"] = matches
            if not matches:
                departures.append(f"{f}: nonzero count histogram differs from both frozen rank-count shapes")
        if len(set(positives)) > 1:
            departures.append("families have different positive counts; grid uses one count across the subset")
        if subset and not set.intersection(*(set(families[f]["matching_count_shapes"]) for f in subset)):
            departures.append("no single count-shape arm matches every retained family")
        status = "UNDETERMINED" if len(subset) < 3 else "OUT-OF-ENVELOPE" if departures else declaration["status"]
        result[p] = {"eligible": subset, "frozen_declaration": declaration, "realized_status": status,
                     "departures": departures, "families": families,
                     "absence_licence": "No absence inference outside the exact subset/support alternative; no joint POWERED label."}
    return result


def run(campaign):
    """Production entry: fixed 320 cells; not executed by this plan author."""
    def operation(provenance):
        runtime = require_runtime()
        require_protocol(campaign, ("battery", "predictor_data", "verify_predictor_seal"))
        require_preoutcome(campaign.root)
        seal = receipt(campaign.verify_predictor_seal(), "seal_sha256")
        battery = load_battery(campaign.battery())
        require(seal.get("battery_sha256") == battery.sha256, "sealed battery")
        predictors = load_predictors(campaign.predictor_data(), battery)
        calibration_path = safe_path(campaign.root, "statistics/calibration/calibration.json")
        calibration_bytes = calibration_path.read_bytes()
        calibration_sha = pin(provenance["input_sha256"].get("calibration"))
        require(digest(calibration_bytes) == calibration_sha, "independently pinned calibration")
        calibration = decode(strict_json(calibration_bytes))
        require(calibration.get("state") == "NO-DETECTED-CALIBRATION-DEFECT" and
                calibration.get("production") is True, "calibration not certified")
        from .calibration import verify_calibration_semantics
        verify_calibration_semantics(calibration)
        result = assemble(predictors, battery, seal, provenance)
        return {**result, "calibration_sha256": calibration_sha,
                "statistical_runtime": runtime,
                "selectivity_envelope": calibration["selectivity_envelope"]}
    return stage(campaign, "power", operation)
