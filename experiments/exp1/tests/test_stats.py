"""M1 tests for the statistical primitives.

These pin the behaviour the preregistered decision rules depend on. If any of these
break after M3.5 freeze, the instrument's statistics changed and the freeze is void.
"""

import numpy as np
import pytest
from scipy.stats import beta

from signatures.stats import bonferroni, clopper_pearson, cohens_d, permutation_null


# --- clopper_pearson --------------------------------------------------------

def test_cp_zero_passes_gives_finite_nonzero_upper():
    """The 'never a claimed zero' guarantee: 0/n has a positive numeric ceiling."""
    lo, hi = clopper_pearson(0, 100)
    assert lo == 0.0
    assert hi > 0.0
    # exact value: upper = beta.ppf(0.975, 1, 100) ~= 0.0362 (the ~3/n rule)
    assert hi == pytest.approx(float(beta.ppf(0.975, 1, 100)), rel=1e-9)
    assert hi == pytest.approx(0.03621, abs=1e-4)


def test_cp_all_passes_gives_upper_one():
    lo, hi = clopper_pearson(100, 100)
    assert hi == 1.0
    assert lo < 1.0
    assert lo == pytest.approx(float(beta.ppf(0.025, 100, 1)), rel=1e-9)


def test_cp_brackets_true_rate_symmetric_case():
    lo, hi = clopper_pearson(50, 100)
    assert lo < 0.5 < hi
    assert lo == pytest.approx(0.3983, abs=1e-3)
    assert hi == pytest.approx(0.6017, abs=1e-3)


def test_cp_budget_floor_matches_design_note():
    """Design §4: 1e5-sample budget distinguishes rates down to ~3e-5."""
    lo, hi = clopper_pearson(0, 100_000)
    assert hi == pytest.approx(3.0e-5, abs=1e-5)


def test_cp_validates_inputs():
    with pytest.raises(ValueError):
        clopper_pearson(5, 0)
    with pytest.raises(ValueError):
        clopper_pearson(11, 10)
    with pytest.raises(ValueError):
        clopper_pearson(1, 10, alpha=0.0)


# --- cohens_d ---------------------------------------------------------------

def test_cohens_d_exact_hand_computed():
    # a=[2,4,6] mean 4 sd 2 ; b=[1,3,5] mean 3 sd 2 ; pooled sd 2 ; d=(4-3)/2=0.5
    assert cohens_d([2, 4, 6], [1, 3, 5]) == pytest.approx(0.5)


def test_cohens_d_sign_follows_a_minus_b():
    assert cohens_d([1, 3, 5], [2, 4, 6]) == pytest.approx(-0.5)


def test_cohens_d_large_separation_exceeds_pass_bar():
    a = [10.0, 10.1, 9.9, 10.0, 10.05]
    b = [0.0, 0.1, -0.1, 0.0, 0.05]
    assert cohens_d(a, b) > 2.0  # the design's clean-separation bar


def test_cohens_d_identical_groups_is_zero():
    assert cohens_d([1, 2, 3], [1, 2, 3]) == 0.0


def test_cohens_d_requires_two_per_group():
    with pytest.raises(ValueError):
        cohens_d([1.0], [1, 2, 3])


# --- bonferroni -------------------------------------------------------------

def test_bonferroni_scales_by_count_and_caps_at_one():
    assert bonferroni([0.01, 0.02, 0.5]) == pytest.approx([0.03, 0.06, 1.0])


def test_bonferroni_empty():
    assert bonferroni([]) == []


# --- permutation_null -------------------------------------------------------

def _mean_accuracy_fit(X, y):
    """Toy scorer: threshold the single feature at 0, accuracy vs binary labels.

    With a planted signal (feature correlated with y) accuracy is high; with a
    permuted y it collapses to chance.
    """
    pred = (X[:, 0] > 0).astype(int)
    return float((pred == y).mean())


def test_permutation_null_flags_planted_signal():
    rng = np.random.default_rng(0)
    n = 200
    y = rng.integers(0, 2, size=n)
    X = (y * 2 - 1 + 0.1 * rng.standard_normal(n)).reshape(-1, 1)  # strong signal
    p, null_mean, _ = permutation_null(_mean_accuracy_fit, X, y, n_perm=500, seed=1)
    assert p < 0.01
    assert null_mean == pytest.approx(0.5, abs=0.05)


def test_permutation_null_p_is_bounded_and_never_zero():
    rng = np.random.default_rng(2)
    n = 100
    y = rng.integers(0, 2, size=n)
    X = rng.standard_normal(n).reshape(-1, 1)  # no signal
    p, _, _ = permutation_null(_mean_accuracy_fit, X, y, n_perm=200, seed=3)
    assert 0.0 < p <= 1.0
    assert p >= 1.0 / (200 + 1)  # add-one estimator floor


def test_permutation_null_calibrated_under_null():
    """False-positive rate at alpha=0.05 should be roughly <= 0.05 on pure noise.

    Loose upper bound (0.20) to stay non-flaky while still catching a badly
    miscalibrated test.
    """
    rng = np.random.default_rng(42)
    false_positives = 0
    trials = 40
    for t in range(trials):
        n = 80
        y = rng.integers(0, 2, size=n)
        X = rng.standard_normal(n).reshape(-1, 1)
        p, _, _ = permutation_null(_mean_accuracy_fit, X, y, n_perm=200, seed=1000 + t)
        if p < 0.05:
            false_positives += 1
    assert false_positives / trials <= 0.20
