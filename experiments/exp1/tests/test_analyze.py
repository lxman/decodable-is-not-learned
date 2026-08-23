"""Freeze-validation tests for analyze.py.

analyze.py is frozen against the RunRecord SCHEMA and proven here on SYNTHETIC records
whose truth-table membership is known by construction — never on real data. Each test
fabricates a scenario (clean PASS, or one of the reportable FAILs from design §4) and
asserts the verdict. This is what licenses tagging the analysis before M4 data.
"""

import numpy as np
import pytest

from analyze import analyze
from signatures.schema import (
    ForecastResult,
    GTCheck,
    ProbeResult,
    RunRecord,
    SamplingResult,
)

SIZES = ("1M", "10M", "100M")
SEEDS = range(5)


def _rec(system, size, seed, *, s1_acc, s1_present, s2_rate, s2_present,
         s2_absent, s3_present, axis):
    return RunRecord(
        system=system, size_bucket=size, seed=seed,
        git_sha="test", torch_version="t", transformers_version="t",
        gt_check=GTCheck(certified=True, method="synthetic"),
        s1=ProbeResult(
            present=s1_present, accuracy=s1_acc, chance=0.01, null_p=0.0,
            null_mean=0.01, ci95=(s1_acc - 0.01, s1_acc + 0.01), best_layer=0,
            best_token=-1, n_layers_tested=1, checkpoint_id="c", below_threshold=True,
        ),
        s2=SamplingResult(
            present=s2_present, absent=s2_absent, passes=0, n=100000,
            rate_point=s2_rate, cp_lower=max(0.0, s2_rate - 1e-4),
            cp_upper=s2_rate + 1e-4, guessing_floor=1e-5, argmax_fails=True,
            checkpoint_id="c",
        ),
        s3=ForecastResult(
            present=s3_present, predicted_transition=1.0, true_transition=1.0,
            interval90=(0.9, 1.1), rel_error=0.0, slope_ci=(0.5, 1.5),
            beats_no_transition_baseline=True, axis=axis,
        ),
    )


def _grok(size, seed, **kw):
    base = dict(s1_acc=0.90 + 0.005 * seed, s1_present=True,
                s2_rate=1e-3 + 1e-5 * seed, s2_present=True,
                s2_absent=False, s3_present=True, axis="training_steps")
    base.update(kw)
    return _rec("grokking", size, seed, **base)


def _lub_below(size, seed, **kw):
    base = dict(s1_acc=0.011 + 0.001 * seed, s1_present=False,
                s2_rate=0.0, s2_present=False,
                s2_absent=True, s3_present=False, axis="graph_param")
    base.update(kw)
    return _rec("lubana_below", size, seed, **base)


def _lub_above(size, seed, **kw):
    base = dict(s1_acc=0.88 + 0.005 * seed, s1_present=True,
                s2_rate=9e-4 + 1e-5 * seed, s2_present=True,
                s2_absent=False, s3_present=True, axis="training_steps")
    base.update(kw)
    return _rec("lubana_above", size, seed, **base)


def _clean_dataset(also_phaseA=False):
    recs = []
    for size in SIZES:
        for seed in SEEDS:
            recs += [_grok(size, seed), _lub_below(size, seed), _lub_above(size, seed)]
    if also_phaseA:
        recs.append(_rec("phaseA", "phaseA", 0, s1_acc=0.4, s1_present=True,
                         s2_rate=0.0, s2_present=False, s2_absent=True,
                         s3_present=False, axis="training_steps"))
    return recs


def test_clean_dataset_passes():
    report = analyze(_clean_dataset())
    assert report.verdict == "PASS", report.findings
    assert report.truth_table["grokking"] == {"S1": "present", "S2": "present", "S3": "present"}
    assert report.truth_table["lubana_below"] == {"S1": "absent", "S2": "absent", "S3": "absent"}
    assert report.sizes_evaluated == list(SIZES)


def test_phaseA_is_excluded_from_scoring():
    with_phase = analyze(_clean_dataset(also_phaseA=True))
    assert with_phase.verdict == "PASS"
    assert "phaseA" not in with_phase.truth_table


def test_s3_present_on_percolation_is_reportable_fail():
    recs = _clean_dataset()
    recs = [r for r in recs if not (r.system == "lubana_below" and r.size_bucket == "10M" and r.seed == 0)]
    recs.append(_lub_below("10M", 0, s3_present=True))  # off-diagonal
    report = analyze(recs)
    assert report.verdict == "FAIL"
    assert any("S3 present on Lubana-below" in f for f in report.findings)


def test_s1_absent_on_grokking_is_reportable_fail():
    recs = [r for r in _clean_dataset()
            if not (r.system == "grokking" and r.size_bucket == "1M" and r.seed == 2)]
    recs.append(_grok("1M", 2, s1_present=False))
    report = analyze(recs)
    assert report.verdict == "FAIL"
    assert any("S1 absent on grokking" in f for f in report.findings)


def test_leaky_separation_small_d_is_reportable_fail():
    """S1 accuracies close between rows -> d < 2 and overlapping CIs."""
    recs = []
    rng = np.random.default_rng(0)
    for size in SIZES:
        for seed in SEEDS:
            g = _grok(size, seed, s1_acc=float(0.50 + 0.05 * rng.standard_normal()))
            l = _lub_below(size, seed, s1_acc=float(0.48 + 0.05 * rng.standard_normal()),
                           s1_present=False)
            recs += [g, l, _lub_above(size, seed)]
    report = analyze(recs)
    assert report.verdict == "FAIL"
    assert any("S1" in f and ("d =" in f or "overlap" in f) for f in report.findings)


def test_control_divergence_is_reportable_fail():
    recs = [r for r in _clean_dataset()
            if not (r.system == "lubana_above" and r.size_bucket == "100M" and r.seed == 1)]
    recs.append(_lub_above("100M", 1, s1_present=False))  # control misses a present
    report = analyze(recs)
    assert report.verdict == "FAIL"
    assert any("control" in f.lower() for f in report.findings)


def test_insufficient_seeds_reports_insufficient():
    recs = []
    for size in SIZES:
        for seed in range(3):  # only 3 seeds, need 5
            recs += [_grok(size, seed), _lub_below(size, seed), _lub_above(size, seed)]
    report = analyze(recs)
    assert report.verdict == "INSUFFICIENT_DATA"


def test_insufficient_sizes_reports_insufficient():
    recs = []
    for size in ("1M", "10M"):  # only 2 sizes, need 3
        for seed in SEEDS:
            recs += [_grok(size, seed), _lub_below(size, seed), _lub_above(size, seed)]
    report = analyze(recs)
    assert report.verdict == "INSUFFICIENT_DATA"


def test_empty_is_insufficient():
    assert analyze([]).verdict == "INSUFFICIENT_DATA"
