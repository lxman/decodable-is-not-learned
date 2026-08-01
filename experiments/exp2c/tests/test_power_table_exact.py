# experiments/exp2c/tests/test_power_table_exact.py
"""Tests for the design Sec 5 preregistered fallback (ruling 2026-08-01):
the exact family-block permutation test and its power machinery. These
are NEW tests for NEW functions -- `simulate`/`_naive_perm_p*` and their
existing tests in test_power_table.py are untouched."""

import numpy as np
import pytest

from experiments.exp2c.run import power_table as pt


def test_exact_block_perms_2_1_1_exact_rows():
    # families=[2,1,1]: blocks are [0,1] (size 2), [2] (size 1), [3]
    # (size 1). Same-size groups: {size 2: 1 family} -> 1! = 1
    # reassignment (only the identity -- a lone family can only swap
    # with itself); {size 1: 2 families} -> 2! = 2 reassignments. Total
    # = 1! * 2! = 2 (NOT 2!*2!=4 -- there is only one size-2 family, so
    # that group contributes a factor of 1, not 2). The two
    # reassignments of the size-1 group are: identity (block 1 stays at
    # slot 1, block 2 stays at slot 2) and the swap (block 2's single
    # rung index 3 moves to slot 1's position, block 1's index 2 moves
    # to slot 2's position). Hand-derived expected rows:
    #   row 0 (identity):      [0, 1, 2, 3]
    #   row 1 (singletons swapped): [0, 1, 3, 2]
    perms = pt.exact_block_perms([2, 1, 1])
    expected = np.array([[0, 1, 2, 3],
                          [0, 1, 3, 2]])
    assert perms.shape == (2, 4)
    np.testing.assert_array_equal(perms, expected)


def test_exact_block_perms_2_2_1_multirung_block_swap():
    # Review hardening (2026-08-01): pin within-block-order preservation
    # on a GENUINE multi-rung block swap -- the [2,1,1] fixture above
    # only ever swaps singletons, which cannot distinguish "block moved
    # as a unit, order preserved" from an internal re-permutation.
    # families=[2,2,1]: blocks [0,1], [2,3], [4]. Same-size groups:
    # {size 2: 2 families} -> 2! = 2, {size 1: 1 family} -> 1! = 1;
    # total 2 rows. The swap row reassigns block 1's rungs (2,3) to
    # slot 0's positions IN ORDER (2 then 3, never 3 then 2) and block
    # 0's rungs (0,1) to slot 1's positions in order; the singleton
    # stays. Hand-derived full row set (row order deterministic:
    # identity first, per itertools lexicographic order):
    perms = pt.exact_block_perms([2, 2, 1])
    expected = np.array([[0, 1, 2, 3, 4],
                          [2, 3, 0, 1, 4]])
    np.testing.assert_array_equal(perms, expected)

    # Same property on a size-3 pair: families=[3,3], blocks [0,1,2]
    # and [3,4,5]; 2! = 2 rows; the swap moves each 3-rung block intact
    # (3,4,5 in order to the first slot; 0,1,2 in order to the second).
    perms3 = pt.exact_block_perms([3, 3])
    expected3 = np.array([[0, 1, 2, 3, 4, 5],
                           [3, 4, 5, 0, 1, 2]])
    np.testing.assert_array_equal(perms3, expected3)


def test_exact_block_p_length_mismatch_raises():
    # Review hardening (2026-08-01): a caller that mis-grouped its rung
    # arrays (len != sum(families)) must get a named ValueError, not a
    # matmul shape traceback -- the queued analyze.py amendment is the
    # intended beneficiary.
    with pytest.raises(ValueError, match="sum\\(families\\)=4"):
        pt.exact_block_p([1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [2, 1, 1])
    with pytest.raises(ValueError, match="len\\(y\\)=5"):
        pt.exact_block_p([1.0, 2.0, 3.0, 4.0],
                         [1.0, 2.0, 3.0, 4.0, 5.0], [2, 1, 1])


def test_exact_block_perms_guard_raises():
    # 11 singleton families -> one same-size group of 11 -> 11! =
    # 39,916,800 permutations, which exceeds EXACT_PERM_GUARD (5e6).
    # Must raise before attempting to enumerate/allocate.
    with pytest.raises(ValueError, match="exceeds the guard"):
        pt.exact_block_perms([1] * 11)


def test_exact_block_perms_within_guard_ok():
    # 10 singleton families -> 10! = 3,628,800 <= 5e6: must NOT raise,
    # and must return exactly that many rows.
    perms = pt.exact_block_perms([1] * 10)
    assert perms.shape == (3628800, 10)


def test_exact_block_p_hand_computed():
    # families=[1,1,1]: every rung is its own singleton family, so the
    # "exact block permutation" test degenerates to the full permutation
    # test over all 3! = 6 bijections of 3 elements -- hand-computable.
    # x = y = [1, 2, 3] (identical rank order, so rho_obs = 1.0).
    # Spearman's rho for n=3 via rho = 1 - 6*sum(d^2)/(n*(n^2-1)),
    # n*(n^2-1) = 24, over all 6 permutations of y against x=(1,2,3):
    #   y-perm      d=(x-y)      sum(d^2)   rho
    #   (1,2,3)     (0,0,0)      0          1.0   <- identity, = rho_obs
    #   (1,3,2)     (0,-1,1)     2          0.5
    #   (2,1,3)     (-1,1,0)     2          0.5
    #   (2,3,1)     (-1,-1,2)    6         -0.5
    #   (3,1,2)     (-2,1,1)     6         -0.5
    #   (3,2,1)     (-2,0,2)     8         -1.0
    # Only the identity itself reaches rho >= rho_obs=1.0, so
    # p = 1/6 exactly (identity counted, matching "min p = 1/n_perms").
    r = pt.exact_block_p([1, 2, 3], [1, 2, 3], [1, 1, 1])
    assert r["n_perms"] == 6
    assert r["resolution"] == pytest.approx(1 / 6)
    assert r["rho_obs"] == pytest.approx(1.0)
    assert r["p"] == pytest.approx(1 / 6)


def test_exact_block_p_deterministic_no_rng():
    x = np.array([2.0, 5.0, 1.0, 3.0])
    y = np.array([1.0, 4.0, 3.0, 2.0])
    r1 = pt.exact_block_p(x, y, [2, 1, 1])
    r2 = pt.exact_block_p(x, y, [2, 1, 1])
    assert r1 == r2

    p1 = pt.exact_block_perms([2, 2, 1, 1])
    p2 = pt.exact_block_perms([2, 2, 1, 1])
    np.testing.assert_array_equal(p1, p2)  # row order is deterministic too


def test_simulate_exact_alpha_bounded():
    # families=[2,2,2,1,1,1,1,1]: same-size groups {2: 3 families} -> 3!
    # = 6, {1: 5 families} -> 5! = 120; total = 6*120 = 720 permutations,
    # resolution = 1/720 ~ .00139. floor(.01*720)=7, so p<.01 is
    # achievable (count<=7 -> p<=7/720~.00972) -- unlike a shape with
    # <100 permutations (e.g. [2,2,1,1,1,1] -> 2!*4!=48, min p~.0208,
    # p<.01 is NEVER achievable there). Under exact-permutation
    # exchangeability (x, y independent when shared=0.0 in `_battery`),
    # true alpha = floor(.01*720)/720 = 7/720 ~ .0097 <= .01 by
    # construction; the observed rate over n_sims is a noisy estimate of
    # that, so we allow generous MC slack rather than asserting the
    # theoretical value exactly.
    r = pt.simulate_exact([2, 2, 2, 1, 1, 1, 1, 1], rho_family=0.5,
                          rho_true=0.6, n_sims=300, seed=0)
    assert r["n_perms"] == 720
    assert r["resolution"] == pytest.approx(1 / 720)
    assert r["alpha"] <= 0.05  # true rate ~.0097; generous slack for n_sims=300 MC noise


def test_simulate_exact_power_monotone_in_effect():
    lo = pt.simulate_exact([2, 2, 2, 1, 1, 1, 1, 1], rho_family=0.5,
                           rho_true=0.4, n_sims=300, seed=2)
    hi = pt.simulate_exact([2, 2, 2, 1, 1, 1, 1, 1], rho_family=0.5,
                           rho_true=0.8, n_sims=300, seed=2)
    assert hi["power"] > lo["power"]
