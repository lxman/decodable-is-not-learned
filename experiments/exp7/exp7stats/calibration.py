"""Frozen complete component-null calibration and selectivity envelope drivers.

No production invocation or empirical null-frequency estimate is authorized in
this authoring stage. Tests exercise generators and scripted accounting only.
"""
from dataclasses import dataclass, asdict
from fractions import Fraction as F
from math import comb
import numpy as np
from exp7core.scoring import Table, Score
from exp7core.strata import availability_buckets
from exp7core.inference import Cell, eligibility, mean
from exp7core.simulations import prompt_probabilities, expected_x, binomial_interval
from .common import SCHEMA, FAMILIES, PREDICTORS, require, stage, digest, KERNEL_VERSION
from .kernels import rng, primary, selectivity, require_runtime
from .saved_math import VERSION, pack, equal, BOUND_KEYS
from .envelope_math import envelope_record


def triple(*values):
    return tuple(F(str(v)) for v in values)


H = (
    (triple(1, 1, .5), triple(1, 1, .5)),
    (triple(.2, .1, .9), triple(.1, .2, .1)),
    (triple(.005, .02, .99), triple(.02, .005, .01)),
    (triple(.5, .05, .9), triple(.05, .5, .1)),
    (triple(0, .2, .9), triple(.2, 0, .1)),
)
ENVELOPE = (
    H[4],
    (triple(.005, .005, .5), triple(.005, .005, .5)),
    (triple(.01, .05, .9), triple(.05, .01, .1)),
    (triple(.05, .2, .99), triple(.2, .05, .01)),
    H[1],
    (triple(.5, .5, .5), triple(.5, .5, .5)),
    H[0],
    (triple(1, 1, .99), triple(1, 1, .01)),
)
DELTAS = (F(0), F(1, 40), F(1, 20), F(1, 10), F(1, 5))
CASES = tuple(f"N{i}" for i in range(1, 10))
TRUE_NULLS = {
    "N1": (("pythia_1b", "selectivity"), ("olmo2_1b", "selectivity"), ("pythia_1b", "forecast"), ("olmo2_1b", "forecast")),
    "N2": (("pythia_1b", "selectivity"), ("olmo2_1b", "selectivity")),
    "N3": (("pythia_1b", "selectivity"), ("olmo2_1b", "selectivity")),
    "N4": (("pythia_1b", "selectivity"), ("olmo2_1b", "selectivity"), ("pythia_1b", "forecast"), ("olmo2_1b", "forecast")),
    "N5": (("pythia_1b", "selectivity"), ("olmo2_1b", "forecast")),
    "N6": (("olmo2_1b", "selectivity"), ("pythia_1b", "forecast")),
    "N7": (("pythia_1b", "forecast"), ("olmo2_1b", "forecast")),
    "N8": (("pythia_1b", "forecast"), ("olmo2_1b", "forecast")),
    "N9": (("pythia_1b", "forecast"), ("olmo2_1b", "forecast")),
}


@dataclass(frozen=True)
class CalibrationSpec:
    n: int = 500
    replicates: int = 2000
    permutations: int = 10000
    envelope_replicates: int = 128

    def __post_init__(self):
        require(type(self.n) is int and self.n >= 120 and self.n % 5 == 0, "calibration block shape")
        require(all(type(v) is int and v > 0 for v in
                    (self.replicates, self.permutations, self.envelope_replicates)), "calibration counts")


SPEC = CalibrationSpec()


def sample_scores(patterns, delta, n, namespace):
    """Independent pair/render/qrow categorical streams, vectorized by pattern."""
    require(patterns and n > 0, "probability patterns")
    # Different render/qrow generators, PCG64DXSM, no shared target-label draw.
    arrays = []
    for render in range(2):
        matrices = [np.zeros((n, 3), dtype=np.int64), np.zeros((n, 3), dtype=np.int64)]
        for pattern_i, pattern in enumerate(patterns):
            ix = np.arange(pattern_i, n, len(patterns))
            s0, s1, prior = pattern[render]
            spec = prompt_probabilities(s0, s1, prior, delta)
            require(spec["status"] == "SUPPORTED", "impossible probability pattern")
            for qrow in range(2):
                probabilities = np.asarray([float(v) for v in spec["rows"][qrow]])
                matrices[qrow][ix] = rng(namespace, render, qrow, pattern_i).multinomial(64, probabilities, size=len(ix))
        arrays.append(tuple(Table(int(matrices[0][i, 0]), int(matrices[0][i, 1]),
                                  int(matrices[1][i, 0]), int(matrices[1][i, 1]), 64) for i in range(n)))
    return tuple(Score(a, b) for a, b in zip(*arrays))


def count_assignment(order, n, n_positive, max_count=26):
    require(0 < n_positive <= n and len(order) == n and len(set(int(v) for v in order)) == n,
            "outcome assignment coverage")
    y = [0]*n
    for rank, i in enumerate(order[:n_positive]):
        y[int(i)] = max_count - rank*max_count//n_positive
    return tuple(y)


def null_case(case, replicate, *, n=500):
    """Generate ONE case, never estimate a null frequency here."""
    require(case in CASES and type(replicate) is int and replicate >= 0 and n >= 120 and n % 5 == 0,
            "null case specification")
    base = tuple(f"base-{i//(n//5)}" for i in range(n))
    n_positive = n//4
    scores = {p: {} for p in PREDICTORS}
    strata = {p: {} for p in PREDICTORS}
    for f in FAMILIES:
        for p in PREDICTORS:
            if case in ("N7", "N9") and p == PREDICTORS[1]:
                scores[p][f] = scores[PREDICTORS[0]][f]  # declared perfect dependence fixture
            else:
                if case == "N1":
                    patterns, delta = (H[0],), F(0)
                elif case == "N2":
                    patterns, delta = (H[1],), F(0)
                elif case == "N3":
                    patterns, delta = H, F(0)
                elif case == "N4":
                    patterns, delta = (H[4],), F(0)
                elif case in ("N5", "N6"):
                    null_p = PREDICTORS[0] if case == "N5" else PREDICTORS[1]
                    patterns, delta = (H, F(0)) if p == null_p else ((H[0],), F(1, 5))
                elif case in ("N7", "N8"):
                    patterns, delta = (H[0],), F(1, 5)
                else:
                    patterns, delta = (H[0], H[1], H[3]), F(1, 10)
                scores[p][f] = sample_scores(patterns, delta, n, ("calibration", case, replicate, p, f))
            strata[p][f] = availability_buckets(base, tuple(s.u for s in scores[p][f]))[0]
    yy = {}
    structural = {}
    for f in FAMILIES:
        if case in ("N1", "N2", "N3", "N4"):
            order = sorted(range(n), key=lambda i: (i % 5, i), reverse=True)
            yy[f] = count_assignment(order, n, n_positive)
        elif case in ("N5", "N6"):
            null_p = PREDICTORS[0] if case == "N5" else PREDICTORS[1]
            xx = tuple(s.x for s in scores[null_p][f])
            tie = rng("calibration-outcome", case, replicate, f).random(n)
            order = sorted(range(n), key=lambda i: (xx[i], tie[i]), reverse=True)
            yy[f] = count_assignment(order, n, n_positive)
        elif case in ("N7", "N8"):
            order = rng("calibration-outcome", case, replicate, f).permutation(n)
            yy[f] = count_assignment(order, n, n_positive)
        else:
            from exp7core.inference import groups
            require(strata[PREDICTORS[0]][f] == strata[PREDICTORS[1]][f], "N9 shared partitions")
            values, block_info = [0]*n, []
            for j, ix in enumerate(groups(strata[PREDICTORS[0]][f])):
                order = rng("calibration-outcome", case, replicate, f, j).permutation(ix)
                positives = len(ix)//4
                for rank, i in enumerate(order[:positives]):
                    values[int(i)] = 26-rank*26//positives
                block_info.append({"indices": tuple(ix), "n_positive": positives,
                                   "y_multiset": sorted(values[i] for i in ix)})
            yy[f] = tuple(values)
            structural[f] = block_info
    cells_by = {}
    for p in PREDICTORS:
        cells_by[p] = tuple(Cell(f, tuple(range(n)), scores[p][f], yy[f], strata[p][f]) for f in FAMILIES)
        keep, _ = eligibility(cells_by[p])
        require(keep == FAMILIES, f"CASE_FAILURE {case}: eligible set is not structurally all four ({p})")
        for c in cells_by[p]:
            require(len(set(c.strata)) <= 10, "CASE_FAILURE: too many composite blocks")
            if case in ("N5", "N6"):
                require(sum(v > 0 for v in c.y) >= 20 and len(set(c.y)) > len(set(c.strata)),
                        "CASE_FAILURE N5/N6: all-four proof violated")
    return {"case": case, "replicate": replicate, "cells": cells_by, "true_nulls": TRUE_NULLS[case],
            "N9_blocks": structural,
            "proof": ("N9: conditional on realized shared partitions, each block's y multiset is assigned by an independent uniform permutation; invariant under every within-block predictor permutation."
                      if case == "N9" else "N5/N6: more outcome values than composite blocks proves informative outcomes for every family; positives>=20; no x-selected eligibility." if case in ("N5", "N6") else "See fixed case table.")}


def exact_binomial_tail(k, n, probability):
    require(type(n) is int and n > 0 and type(k) is int and 0 <= k <= n, "binomial counts")
    p = F(probability)
    require(0 <= p <= 1, "binomial probability")
    if p == 0:
        return F(k == 0)
    if p == 1:
        return F(1)
    a, b = p.numerator, p.denominator
    term, total = (b-a)**n, 0
    for j in range(n+1):
        if j >= k:
            total += term
        if j < n:
            term = term*(n-j)*a // ((j+1)*(b-a))
    return F(total, b**n)


def rate_summary(count, n, null_rate):
    excess = exact_binomial_tail(count, n, null_rate)
    return {"count": count, "N": n, "fraction": F(count, n),
            "interval95": binomial_interval(count, n), "null_rate": null_rate,
            "binomial_excess_p": excess, "defect": excess < F(1, 100)}


def evaluate_replicate(case, replicate, spec=SPEC):
    fixture = null_case(case, replicate, n=spec.n)
    readings = {p: primary(fixture["cells"][p], B=spec.permutations,
                           namespace=("calibration-test", case, replicate, p), full=False) for p in PREDICTORS}
    require(all(tuple(r["eligible"]) == FAMILIES for r in readings.values()), "CASE_FAILURE: primary changed family set")
    return {"components": {f"{p}/{component}": {"p_reject": readings[p][component]["reject"],
                                                "fires": readings[p][component]["fires"]}
                           for p, component in TRUE_NULLS[case]},
            "union": any(r["state"] == "INPUT-SENSITIVE-FORECAST" for r in readings.values())}


def case_record(case, spec=SPEC, *, evaluator=evaluate_replicate):
    require(callable(evaluator), "calibration evaluator")
    counts = {f"{p}/{c}": {"p_reject": 0, "fires": 0} for p, c in TRUE_NULLS[case]}
    union = 0
    for b in range(spec.replicates):
        try:
            got = evaluator(case, b, spec)
            require(set(got) == {"components", "union"} and set(got["components"]) == set(counts), "case component coverage")
            require(type(got["union"]) is bool, "union bit")
            union += got["union"]
            for name in counts:
                require(set(got["components"][name]) == {"p_reject", "fires"}, "component metrics")
                for key in counts[name]:
                    bit = got["components"][name][key]
                    require(type(bit) is bool, "component bit")
                    counts[name][key] += bit
        except Exception as e:
            return {"case": case, "status": "CASE_FAILURE", "failed_replicate": b,
                    "completed_replicates": b, "required_replicates": spec.replicates,
                    "reason": f"{type(e).__name__}: {e}", "frequencies": None}
    components = {name: {key: rate_summary(count, spec.replicates, F(1, 200))
                          for key, count in values.items()} for name, values in counts.items()}
    union_result = rate_summary(union, spec.replicates, F(1, 100))
    defect = union_result["defect"] or any(r["defect"] for c in components.values() for r in c.values())
    return {"case": case, "status": "DEFECT" if defect else "NO-DETECTED-DEFECT", "N": spec.replicates,
            "components": components, "either_predictor_joint": union_result,
            "note": "Casewise defect detection, not a proof of exact alpha; p-only tests are not masked by effect bars."}


def envelope_grid():
    for i, pattern in enumerate(ENVELOPE):
        for families in (3, 4):
            for delta in DELTAS:
                yield i, pattern, families, delta


def envelope_cell(index, pattern, family_count, delta, spec=SPEC):
    tables = [prompt_probabilities(*row[:2], row[2], delta) for row in pattern]
    if any(t["status"] != "SUPPORTED" for t in tables) or all(row[0] == 0 or row[1] == 0 for row in pattern):
        return envelope_record(index, pattern, family_count, delta, spec)
    name = f"E{index}/f{family_count}/delta{delta.numerator}_{delta.denominator}"
    samples, mc = [], []
    for b in range(spec.envelope_replicates):
        cs = []
        for f in FAMILIES[:family_count]:
            scores = sample_scores((pattern,), delta, spec.n, ("selectivity-envelope", name, b, f))
            cs.append(Cell(f, tuple(range(spec.n)), scores, (0,)*spec.n, ("all",)*spec.n))
        r = selectivity(tuple(cs), FAMILIES[:family_count], B=spec.permutations,
                        namespace=("selectivity-envelope-test", name, b), full=False)
        samples.append(pack([[v for t in (s.canonical, s.sham) for v in (t.n00, t.n01, t.n10, t.n11)]
                             for c in cs for s in c.scores]))
        mc.append({k: r[k] for k in BOUND_KEYS})
    return envelope_record(index, pattern, family_count, delta, spec, samples=samples, mc=mc)


def assemble(spec=SPEC, *, evaluator=evaluate_replicate, envelope_evaluator=envelope_cell):
    require(callable(evaluator) and callable(envelope_evaluator), "calibration dependencies")
    rows, failed = {}, False
    for case in CASES:
        row = {"case": case, "status": "NOT-RUN-AFTER-CASE-FAILURE"} if failed else case_record(case, spec, evaluator=evaluator)
        rows[case] = row
        failed |= row["status"] == "CASE_FAILURE"
    envelope = {}
    for index, pattern, families, delta in envelope_grid():
        name = f"E{index}/f{families}/delta{delta.numerator}_{delta.denominator}"
        if failed:
            row = {"id": name, "status": "NOT-RUN-AFTER-CASE-FAILURE"}
        else:
            try:
                row = envelope_evaluator(index, pattern, families, delta, spec)
                require(type(row) is dict and row.get("id") == name, "envelope row identity")
            except Exception as e:
                failed = True
                row = {"id": name, "status": "CASE_FAILURE", "reason": f"{type(e).__name__}: {e}"}
        envelope[name] = row
    require(len(envelope) == 80, "envelope coverage")
    defect = failed or any(r["status"] == "DEFECT" for r in rows.values())
    return {"schema": SCHEMA, "stage": "calibration",
            "saved_math_version": VERSION,
            "state": "CALIBRATION-FAILED" if defect else "NO-DETECTED-CALIBRATION-DEFECT",
            "spec": asdict(spec), "cases": rows, "selectivity_envelope": envelope,
            "case_table_sha256": digest({"H": H, "nulls": TRUE_NULLS, "E": ENVELOPE, "deltas": DELTAS}),
            "kernel": KERNEL_VERSION,
            "note": "No claim of joint power; every true component null and union case assessed separately."}


def run(campaign):
    """Full pre-tag production driver. NOT executed during this plan authoring."""
    def operation(provenance):
        runtime = require_runtime()
        require(digest(provenance.get("synthetic_spec")) == digest(frozen_cases()),
                "committed synthetic specification disagrees with executable cases")
        return {**assemble(), "statistical_runtime": runtime}
    return stage(campaign, "calibration", operation)


def frozen_cases():
    """Pure metadata; emitting this document is not a calibration execution."""
    return {"schema": "exp7.synthetic-cases.v1", "calibration_spec": asdict(SPEC), "case_order": CASES,
            "true_nulls": TRUE_NULLS, "H": H, "envelope": ENVELOPE, "deltas": DELTAS,
            "kernel": KERNEL_VERSION, "family_n": 500, "k": 64,
            "N5_N6_selection": "fixed all four via outcome-values > composite-blocks and positives>=20",
            "N9_exchangeability": "independent uniform permutation of fixed outcome multiset within each realized shared block"}


def verify_calibration_semantics(record):
    """Saved arithmetic/coverage checks only; never reruns simulations."""
    require(record.get("schema") == SCHEMA and record.get("stage") == "calibration"
            and record.get("state") == "NO-DETECTED-CALIBRATION-DEFECT"
            and record.get("production") is True, "calibration stage")
    require(record.get("saved_math_version") == VERSION, "calibration saved-math version")
    require(digest(record.get("spec")) == digest(asdict(SPEC)), "calibration specification")
    require(record.get("case_table_sha256") == digest({"H": H, "nulls": TRUE_NULLS, "E": ENVELOPE, "deltas": DELTAS}),
            "calibration case table")
    require(set(record.get("cases", {})) == set(CASES), "calibration cases")
    for case in CASES:
        row = record["cases"][case]
        require(row.get("status") == "NO-DETECTED-DEFECT" and row.get("N") == SPEC.replicates, "calibration case acceptance")
        wanted = {f"{p}/{c}" for p, c in TRUE_NULLS[case]}
        require(set(row.get("components", {})) == wanted, "calibration true components")
        for component in row["components"].values():
            require(set(component) == {"p_reject", "fires"}, "calibration independent p/fire readings")
            require(component["fires"]["count"] <= component["p_reject"]["count"], "calibration full/p-only consistency")
            for value in component.values():
                expected = rate_summary(value["count"], SPEC.replicates, F(1, 200))
                require(digest(value) == digest(expected) and not expected["defect"], "component calibration arithmetic")
        value = row["either_predictor_joint"]
        expected = rate_summary(value["count"], SPEC.replicates, F(1, 100))
        require(digest(value) == digest(expected) and not expected["defect"], "union calibration arithmetic")
    verify_envelope_semantics(record.get("selectivity_envelope"))


def verify_envelope_semantics(rows, *, spec=SPEC):
    require(type(rows) is dict and len(rows) == 80, "selectivity envelope coverage")
    expected_ids = set()
    for index, pattern, families, delta in envelope_grid():
        name = f"E{index}/f{families}/delta{delta.numerator}_{delta.denominator}"
        expected_ids.add(name)
        require(name in rows, "selectivity envelope ID")
        row = rows[name]
        expected = envelope_record(index, pattern, families, delta, spec,
                                   samples=row.get("score_counts"), mc=row.get("randomization_bounds"))
        equal(row, expected, "envelope probabilities/counts/support/score/p/interval arithmetic")
    require(set(rows) == expected_ids, "extra envelope row")
