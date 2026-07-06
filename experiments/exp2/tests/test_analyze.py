"""Frozen-analysis logic tests: run BEFORE the freeze so the verdict machinery is
known-good (the analyze script itself is never edited after data collection)."""

import numpy as np
import pytest

from analyze import EVAL_MODELS, Report, analyze, bootstrap_ci, permutation_p, spearman


def _mk(caps, probe_vals, eval_means):
    probe = {c: {"probe_margin": v} for c, v in zip(caps, probe_vals)}
    evals = {c: {m: e for m in EVAL_MODELS} for c, e in zip(caps, eval_means)}
    return probe, evals


CAPS = [f"cap{i}" for i in range(12)]


def test_spearman_perfect_and_reversed():
    x = list(range(10))
    assert spearman(x, x) == pytest.approx(1.0)
    assert spearman(x, x[::-1]) == pytest.approx(-1.0)


def test_spearman_handles_ties():
    assert -1.0 <= spearman([1, 1, 2, 2], [1, 2, 3, 4]) <= 1.0


def test_perfect_correlation_passes():
    rng = np.random.default_rng(0)
    pv = rng.uniform(0, 1, 12)
    probe, evals = _mk(CAPS, pv, pv * 0.5 + 0.1)  # monotone map -> rho = 1
    r = analyze(probe, evals, CAPS)
    assert r.verdict == "PASS" and r.rho == pytest.approx(1.0) and r.n == 12


def test_no_correlation_fails():
    rng = np.random.default_rng(1)
    probe, evals = _mk(CAPS, rng.uniform(0, 1, 12), rng.uniform(0, 1, 12))
    r = analyze(probe, evals, CAPS)
    assert r.verdict in ("FAIL", "INDETERMINATE")  # seed-dependent weak rho
    assert r.ci95[0] <= r.rho <= r.ci95[1]


def test_anticorrelation_is_fail_not_pass():
    pv = np.arange(12, dtype=float)
    probe, evals = _mk(CAPS, pv, -pv)
    r = analyze(probe, evals, CAPS)
    assert r.verdict == "FAIL" and r.rho == pytest.approx(-1.0)


def test_small_battery_is_insufficient():
    pv = np.arange(9, dtype=float)
    probe, evals = _mk(CAPS[:9], pv, pv)
    r = analyze(probe, evals, CAPS[:9])
    assert r.verdict == "INSUFFICIENT_DATA" and r.n == 9


def test_missing_scores_drop_capability_with_note():
    pv = np.arange(12, dtype=float)
    probe, evals = _mk(CAPS, pv, pv)
    del evals["cap11"]["12b"]
    r = analyze(probe, evals, CAPS)
    assert r.n == 11 and "cap11" in r.notes[0]


def test_permutation_p_is_calibrated_under_null():
    """Under H0 (independent x, y), p should be ~uniform: check the mean over
    repeated draws is not extreme (a cheap calibration smoke test)."""
    rng = np.random.default_rng(2)
    ps = []
    for _ in range(20):
        x, y = rng.uniform(0, 1, 12), rng.uniform(0, 1, 12)
        ps.append(permutation_p(x, y, n_perm=999, seed=3))
    assert 0.2 < np.mean(ps) < 0.8


def test_bootstrap_ci_tightens_with_signal():
    x = np.arange(12, dtype=float)
    lo, hi = bootstrap_ci(x, x, n_boot=2000)
    assert lo > 0.5  # perfect monotone signal: CI stays well above zero


def test_verdicts_are_deterministic():
    pv = np.arange(12, dtype=float)
    probe, evals = _mk(CAPS, pv, pv)
    r1, r2 = analyze(probe, evals, CAPS), analyze(probe, evals, CAPS)
    assert (r1.rho, r1.perm_p, r1.ci95) == (r2.rho, r2.perm_p, r2.ci95)
