# experiments/exp4b/tests/test_placebo_4b.py
"""Tests for `placebo_4b.py` (Task 2): the leave-one-out trend/excess/
SE, the placebo pool and batteries, calibration (p_cal/T*), alpha_
placebo, the per-trajectory/per-type breakdowns, and S3-S5/S8. No
model contact; every fixture is synthetic (`fakes_4b.py`) or hand-
built in place."""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4b import placebo_4b as pl  # noqa: E402
from experiments.exp4b.tests import fakes_4b as fakes  # noqa: E402


# ------------------------------------------------------------- (a) loo_trend


def test_loo_trend_4b_excludes_exactly_f_hand_numbers():
    a = {"a": [1.0, 2.0, 3.0], "b": [3.0, 4.0, 5.0], "c": [10.0, 20.0, 30.0]}
    flat = ["a", "b", "c"]
    steps = [0, 1, 2]
    assert pl.loo_trend_4b(a, flat, steps, "c") == [2.0, 3.0, 4.0]
    assert pl.loo_trend_4b(a, flat, steps, "a") == [6.5, 12.0, 17.5]


def test_loo_trend_4b_raises_on_empty_pool():
    a = {"only": [1.0, 2.0]}
    with pytest.raises(ValueError, match="leave-one-out pool empty for only"):
        pl.loo_trend_4b(a, ["only"], [0, 1], "only")


# ----------------------------------------------------------- (b) loo_excess


def test_loo_excess_4b_zero_at_t1_and_hand_value_at_end():
    a = {"a": [1.0, 2.0, 3.0], "b": [3.0, 4.0, 5.0], "c": [10.0, 20.0, 30.0]}
    flat = ["a", "b", "c"]
    steps = [0, 1, 2]
    x = pl.loo_excess_4b(a, flat, steps, "c")
    assert x[0] == 0.0
    assert x == pytest.approx([0.0, 9.0, 18.0])


def test_loo_excess_4b_raises_on_empty_pool():
    a = {"only": [1.0, 2.0]}
    with pytest.raises(ValueError, match="leave-one-out pool empty for only"):
        pl.loo_excess_4b(a, ["only"], [0, 1], "only")


def test_placebo_phi_4b_is_analyze_4_phi_4():
    x = [0.0, 3.0, 9.0]
    assert pl.placebo_phi_4b(x, 2) == an.phi_4(x, 2)
    assert pl.placebo_phi_4b(x, 1) is None  # index < MIN_CLEAR_INDEX_4


# --------------------------------------------------------- (c) placebo_se_4b


def test_placebo_se_4b_deterministic_and_matches_direct_reimplementation():
    flat = ["a", "b", "c"]
    pia_t1 = fakes.pia_from_means({"a": 0.30, "b": 0.32, "c": 0.50}, seed=1)
    pia_end = fakes.pia_from_means({"a": 0.40, "b": 0.42, "c": 0.90}, seed=2)

    se1 = pl.placebo_se_4b(pia_t1, pia_end, flat, "c", n_boot=50, seed=42)
    se2 = pl.placebo_se_4b(pia_t1, pia_end, flat, "c", n_boot=50, seed=42)
    assert se1 == se2

    # Direct reimplementation of eligibility_table_4's `boot` shape,
    # with the LOO pool (flat \ {"c"}) substituted for R.
    pool = ["a", "b"]
    n = battery_4.N_ITEMS
    rng = np.random.default_rng(42)

    def boot(r):
        idx = rng.integers(0, n, size=(50, n))
        return pia_t1[r][idx].mean(axis=1), pia_end[r][idx].mean(axis=1)

    pool_t1, pool_e = [], []
    for r in pool:
        a1, ae = boot(r)
        pool_t1.append(a1)
        pool_e.append(ae)
    trend_t1 = np.mean(pool_t1, axis=0)
    trend_e = np.mean(pool_e, axis=0)
    f_t1, f_e = boot("c")
    x_end_b = (f_e - f_t1) - (trend_e - trend_t1)
    want = float(np.std(x_end_b, ddof=1))
    assert se1 == pytest.approx(want)


def test_placebo_se_4b_raises_on_empty_loo_pool():
    pia = fakes.pia_from_means({"only": 0.5}, seed=0)
    with pytest.raises(ValueError, match="leave-one-out pool empty for only"):
        pl.placebo_se_4b(pia, pia, ["only"], "only", n_boot=10, seed=0)


def test_placebo_pool_4b_shape_and_p_m():
    series0, flat = fakes.iid_noise_world(n_flat=8, n_steps=10, sigma=0.05, seed=1)
    series, pia_t1, pia_end = fakes.matching_pia(series0, flat, item_sigma=0.02, seed=11)
    pool = pl.placebo_pool_4b(series, pia_t1, pia_end, flat, n_boot=100, seed=0)
    assert set(pool) == set(flat)
    for f, d in pool.items():
        assert set(d) == {"x_end", "se", "eligible", "excess"}
        assert len(d["excess"]) == len(series["steps"])
        assert d["excess"][0] == 0.0
        assert d["x_end"] == d["excess"][-1]
        assert isinstance(d["eligible"], bool)


def test_placebo_pool_4b_refuses_series_pia_mismatch():
    series0, flat = fakes.iid_noise_world(n_flat=4, n_steps=6, sigma=0.05, seed=2)
    series, pia_t1, pia_end = fakes.matching_pia(series0, flat, item_sigma=0.02, seed=3)
    # Perturb one rung's series endpoint so it no longer equals its
    # pia's mean -- exactly the "wrong checkpoint" scenario finding 2
    # guards against.
    bad_series = {"steps": series["steps"],
                 "a": {r: list(v) for r, v in series["a"].items()}}
    bad_series["a"][flat[0]][-1] += 0.01
    with pytest.raises(ValueError, match=f"series/pia mismatch for {flat[0]}"):
        pl.placebo_pool_4b(bad_series, pia_t1, pia_end, flat, n_boot=50, seed=0)


def test_placebo_pool_4b_eligibility_bar_pins_multiple_and_boundary():
    """Finding 3, round 2: the round-1 version fixed `se` at exactly
    `0.0` via constant pia arrays for EVERY rung, including f -- which
    collapses `SE_MULTIPLE_4 * se` to `0.0` for ANY multiple (so a
    mutant `multiple = 1.0` or `3.0` passed unnoticed), and put the
    "AT the bar" case's actual measured `x_end` (1.665e-16, a hair
    ABOVE zero) behind `pytest.approx(0.0, abs=1e-9)`, which cannot
    distinguish `>=` from `>` (a strictly-positive x_end clears either
    operator) while reading as if it proved the inclusive case.

    Fixed: f's own end-array carries REAL, seeded item-level
    dispersion (an `N(0, .02)` draw, fixed seed), so `se` -- read from
    a bootstrap, deterministic given the fixed seed -- is a genuine
    nonzero float, measured once as `se_ref` from an unshifted
    reference build. Every other placement shifts that SAME array by a
    constant (changing its realized MEAN, hence `x_end`, while leaving
    its DISPERSION -- hence `se` -- unchanged to floating precision),
    and every assertion reads the CONSTRUCTED pool's own fresh
    `x_end`/`se` back rather than assuming the target was hit exactly.
    Five placements: `2*se-1e-9` / `2*se+1e-9` pin the boundary at a
    resolvable (1e-9) scale (ineligible / eligible); `1.5*se` /
    `2.5*se` pin the MULTIPLE itself (ineligible under 2 but would be
    eligible under a mutant 1.0; eligible under 2 but would be
    ineligible under a mutant 3.0) -- the +-1e-9 cases alone cannot do
    this, since scaling `SE_MULTIPLE_4` by a wrong constant moves the
    bar without moving a FIXED 1e-9 offset off of "clearly one side or
    the other"; `2*se` itself (`at`) is placed as close to the bar as
    the construction can manage, WITHOUT claiming bit-exact equality --
    the realized residual is measured and asserted small (documented,
    not approximated away), and the assertion checks `eligible ==
    (residual >= 0)` (self-consistency against whichever side the
    residual actually lands on), NOT `eligible is True`, because the
    residual's sign is not controllable by this construction. This
    means the `at` case does NOT by itself distinguish `>=` from `>`
    (both operators agree on any nonzero residual) --
    `test_placebo_pool_4b_eligibility_bar_exact_equality_with_stubbed_se`
    below is the companion test that does, by removing the round trip
    entirely. `multiple=1.0`/`multiple=3.0` mutants each fail one
    assertion HERE (`below`/`above` respectively); see the fix report
    for the by-hand confirmation of all three named mutants."""
    n = battery_4.N_ITEMS
    flat = ["a", "b", "f"]

    def const_pia(v):
        arr = np.full(n, v, dtype=np.float64)
        return arr, float(arr.mean())  # the array's OWN realized mean

    pia_t1, pia_end_pool, realized_t1, realized_end_pool = {}, {}, {}, {}
    for name, t1_v, end_v in (("a", 0.40, 0.50), ("b", 0.42, 0.54)):
        arr_t1, m_t1 = const_pia(t1_v)
        arr_end, m_end = const_pia(end_v)
        pia_t1[name] = arr_t1
        pia_end_pool[name] = arr_end
        realized_t1[name] = m_t1
        realized_end_pool[name] = m_end

    arr_f_t1, f_t1 = const_pia(0.30)
    pia_t1["f"] = arr_f_t1

    trend_t1 = (realized_t1["a"] + realized_t1["b"]) / 2.0
    trend_end = (realized_end_pool["a"] + realized_end_pool["b"]) / 2.0

    # f's own end-array: real, seeded item-level dispersion -- the
    # SOLE source of a genuinely nonzero se (a, b, and f's t_1 array
    # are all constant, contributing zero bootstrap variance).
    base_f_end = 0.5 + np.random.default_rng(0).normal(0.0, 0.02, size=n)

    def build(a_f_end_array):
        pia_end = dict(pia_end_pool)
        pia_end["f"] = a_f_end_array
        series = {
            "steps": [0, 1],
            "a": {
                "a": [realized_t1["a"], realized_end_pool["a"]],
                "b": [realized_t1["b"], realized_end_pool["b"]],
                "f": [f_t1, float(a_f_end_array.mean())],
            },
        }
        return pl.placebo_pool_4b(series, pia_t1, pia_end, flat, n_boot=200, seed=0)

    def target_array(target_x_end):
        """f's end-array, shifted by a constant so `x_end` lands at
        `target_x_end` (up to floating precision): the shift preserves
        the array's dispersion (hence `se`) exactly, to floating
        precision, since every item moves by the SAME amount."""
        target_a_f_end = target_x_end + f_t1 + (trend_end - trend_t1)
        delta = target_a_f_end - float(base_f_end.mean())
        return base_f_end + delta

    ref = build(base_f_end)
    se_ref = ref["f"]["se"]
    assert se_ref > 0.0, "the reference se must be a genuine nonzero float"

    below = build(target_array(2.0 * se_ref - 1e-9))
    assert below["f"]["x_end"] < 2.0 * below["f"]["se"]
    assert below["f"]["eligible"] is False, (
        f"x_end {below['f']['x_end']!r} just below 2*se {2 * below['f']['se']!r} "
        f"must be ineligible")

    above = build(target_array(2.0 * se_ref + 1e-9))
    assert above["f"]["x_end"] > 2.0 * above["f"]["se"]
    assert above["f"]["eligible"] is True, (
        f"x_end {above['f']['x_end']!r} just above 2*se {2 * above['f']['se']!r} "
        f"must be eligible")

    at = build(target_array(2.0 * se_ref))
    residual = at["f"]["x_end"] - 2.0 * at["f"]["se"]
    # "At the bar, to the extent floating point allows": constructing
    # a_f(end) from a target x_end and then re-deriving x_end from
    # a_f(end) is a round trip through subtraction and re-subtraction
    # of the SAME t_1/trend terms, which floating point does not
    # guarantee is lossless -- the residual measured here is small
    # (order 1e-16 to 1e-9 depending on the run) but its SIGN is not
    # controllable by this construction, so the assertion is written
    # against whichever side the residual actually lands on (self-
    # consistency: `eligible` must track the sign of `x_end - 2*se`
    # exactly, whatever that sign is) rather than assuming the
    # eligible side. See the fix report for the residual measured when
    # this test was written and for what this case does and does not
    # prove about `>=` versus `>`.
    assert abs(residual) < 1e-9, f"residual {residual!r} (x_end - 2*se) larger than expected"
    assert at["f"]["eligible"] == (residual >= 0), (
        f"eligible {at['f']['eligible']} inconsistent with x_end {at['f']['x_end']!r} "
        f"vs 2*se {2 * at['f']['se']!r} (residual {residual!r}): `eligible` must equal "
        f"exactly `x_end >= 2*se`")

    below_multiple = build(target_array(1.5 * se_ref))
    assert below_multiple["f"]["eligible"] is False, (
        "1.5*se must be ineligible under SE_MULTIPLE_4 = 2.0 "
        "(would be eligible under a mutant multiple = 1.0)")

    above_multiple = build(target_array(2.5 * se_ref))
    assert above_multiple["f"]["eligible"] is True, (
        "2.5*se must be eligible under SE_MULTIPLE_4 = 2.0 "
        "(would be ineligible under a mutant multiple = 3.0)")


def test_placebo_pool_4b_eligibility_bar_exact_equality_with_stubbed_se(monkeypatch):
    """Companion to the test above: that test's `at` case cannot
    GUARANTEE `x_end == 2*se` to the bit (the construction round-trips
    a target through subtraction and re-subtraction of the t_1/trend
    terms, which floating point does not promise is lossless -- the
    measured residual there was -5.75e-17, i.e. NOT exactly zero, so a
    `>` mutant is indistinguishable from `>=` in that case and is NOT
    caught by it). This test removes the round trip: `placebo_se_4b`
    is monkeypatched to return a literal `0.25` (a dyadic fraction,
    exact in float64), and every other value (f's t_1, the trend, f's
    end value) is ALSO chosen as a dyadic fraction, so `x_end =
    (f_end - f_t1) - (trend_end - trend_t1) = (1.0 - 0.25) - (0.5 -
    0.25)` is bit-exact with no rounding at any step -- verified below
    with `==`, not `pytest.approx`. `x_end == 0.5 == 2*0.25` exactly,
    letting `>=` be told apart from `>` directly."""
    n = battery_4.N_ITEMS
    flat = ["a", "b", "f"]

    def const(v):
        return np.full(n, v, dtype=np.float64)

    pia_t1 = {"a": const(0.25), "b": const(0.25), "f": const(0.25)}
    monkeypatch.setattr(pl, "placebo_se_4b", lambda *a, **k: 0.25)

    def build(f_end):
        # Read the array's OWN realized mean back rather than assuming
        # `const(f_end).mean() == f_end` -- for `f_end` values very
        # close to 1.0 (the `just_below` case below) that assumption
        # is false by one ULP, which `placebo_pool_4b`'s series/pia
        # consistency check (finding 2) correctly refuses.
        arr_f_end = const(f_end)
        realized_f_end = float(arr_f_end.mean())
        pia_end = {"a": const(0.5), "b": const(0.5), "f": arr_f_end}
        series = {"steps": [0, 1],
                 "a": {"a": [0.25, 0.5], "b": [0.25, 0.5], "f": [0.25, realized_f_end]}}
        return pl.placebo_pool_4b(series, pia_t1, pia_end, flat, n_boot=1, seed=0)

    at = build(1.0)
    assert at["f"]["se"] == 0.25
    assert at["f"]["x_end"] == 0.5
    assert at["f"]["eligible"] is True, "x_end == 2*se exactly (0.5 == 2*0.25) must be eligible"

    just_below = build(np.nextafter(1.0, 0.0))  # the largest double strictly < 1.0
    assert just_below["f"]["x_end"] < 0.5
    assert just_below["f"]["eligible"] is False


def test_loo_vs_full_pool_construction_invariance_of_phi_and_eligibility():
    """Important 4 (final review): `loo_trend_4b`'s own docstring used
    to justify leaving f out of its own trend by claiming a self-
    included ("full-pool") construction would make f's excess
    identically zero. It would not -- `x_full(t) = ((n-1)/n) *
    x_loo(t)` EXACTLY (an algebraic identity in the realized data, not
    merely in expectation: proved by substituting `trend_full = (1/n)*
    (a_f + (n-1)*trend_loo)` into `excess_4`'s formula), and the SAME
    scale factor divides the item-bootstrap SE, so `phi` (a ratio of
    two excess values) and the eligibility decision (`x_end >= 2*SE`,
    both sides scaled identically) are INVARIANT to which construction
    f is read against -- design §10 dial (c)'s choice of leave-one-out
    is for the RESEMBLANCE to a rising rung's own construction (S4
    exists to measure that), not because the alternative would be
    degenerate.

    Verified numerically: the excess side compares the real `loo_
    excess_4b` against an independently hand-built self-inclusive
    excess (`an.trend_4`/`an.excess_4` over the FULL `flat` list, f
    included). The SE side builds ONE shared set of item-bootstrap
    resamples per rung so both the leave-one-out and self-inclusive
    SEs are computed from the IDENTICAL underlying draws -- the
    algebraic relation then holds to floating precision rather than
    only approximately (a fresh, independently-seeded bootstrap for
    each side would only agree in expectation, not per draw)."""
    series0, flat = fakes.iid_noise_world(n_flat=12, n_steps=20, sigma=0.05, seed=7)
    series, pia_t1, pia_end = fakes.matching_pia(series0, flat, item_sigma=0.02, seed=13)
    a, steps = series["a"], series["steps"]
    n_flat = len(flat)
    scale = (n_flat - 1) / n_flat
    n = battery_4.N_ITEMS
    n_boot = 300

    rng = np.random.default_rng(0)
    draws = {}
    for r in flat:
        idx = rng.integers(0, n, size=(n_boot, n))
        draws[r] = (pia_t1[r][idx].mean(axis=1), pia_end[r][idx].mean(axis=1))

    for f in flat:
        x_loo = pl.loo_excess_4b(a, flat, steps, f)
        trend_full = an.trend_4(a, flat, steps)          # f INCLUDED
        x_full = an.excess_4({f: a[f]}, trend_full, steps)[f]
        assert x_full[-1] == pytest.approx(x_loo[-1] * scale, rel=1e-9, abs=1e-12)

        c = 5   # an arbitrary clear index >= MIN_CLEAR_INDEX_4
        phi_loo = an.phi_4(x_loo, c)
        phi_full = an.phi_4(x_full, c)
        assert phi_full == pytest.approx(phi_loo, rel=1e-9)

        others = [r for r in flat if r != f]
        trend_t1_loo = np.mean([draws[r][0] for r in others], axis=0)
        trend_e_loo = np.mean([draws[r][1] for r in others], axis=0)
        f_t1, f_e = draws[f]
        x_end_b_loo = (f_e - f_t1) - (trend_e_loo - trend_t1_loo)
        se_loo = float(np.std(x_end_b_loo, ddof=1))

        trend_t1_full = np.mean([draws[r][0] for r in flat], axis=0)
        trend_e_full = np.mean([draws[r][1] for r in flat], axis=0)
        x_end_b_full = (f_e - f_t1) - (trend_e_full - trend_t1_full)
        se_full = float(np.std(x_end_b_full, ddof=1))
        assert se_full == pytest.approx(se_loo * scale, rel=1e-9)

        eligible_loo = x_loo[-1] >= an.SE_MULTIPLE_4 * se_loo
        eligible_full = x_full[-1] >= an.SE_MULTIPLE_4 * se_full
        assert eligible_full == eligible_loo


# -------------------------------------------------- (d)/(e) calibration worlds

# Review finding 5: a single world seed's placebo phi mean is NOT a
# law-of-large-numbers quantity in the battery count B -- draw_
# batteries_4b draws WHICH (already-computed, fixed) rung, not fresh
# noise, so redrawing 2000 batteries from one seed's small eligible-
# rung set does not converge any better than that one set's own
# average. Convergence to R-7's theoretical null is a LLN property of
# the number of DISTINCT eligible rungs sampled, so these two checks
# now pool every eligible rung's phi at each c across a FIXED,
# UNSEARCHED range of world seeds (never hand-picked -- range(60),
# checked once) instead of hand-picking one seed's battery draws.
N_WORLDS = 60
CAL_N_FLAT = 30
CAL_ITEM_SIGMA_IID = 0.3
CAL_ITEM_SIGMA_RW = 0.1
CAL_STEP_SIGMA_RW = 0.02


def _pooled_eligible_phi(world_fn, cs, item_sigma):
    """Runs `world_fn(seed=s)` for `s in range(N_WORLDS)`, pools every
    ELIGIBLE rung's phi at each c in `cs` across all worlds. Returns
    `{c: [phi, ...]}`."""
    per_c = {c: [] for c in cs}
    for world_seed in range(N_WORLDS):
        series0, flat = world_fn(seed=world_seed)
        series, pia_t1, pia_end = fakes.matching_pia(series0, flat, item_sigma=item_sigma,
                                                      seed=world_seed)
        pool = pl.placebo_pool_4b(series, pia_t1, pia_end, flat, n_boot=100, seed=0)
        for d in pool.values():
            if not d["eligible"]:
                continue
            for c in cs:
                phi = pl.placebo_phi_4b(d["excess"], c)
                if phi is not None:
                    per_c[c].append(phi)
    return per_c


def test_iid_noise_world_placebo_phi_mean_near_half_pooled_over_seeds():
    """Step 1(d), pooled over seeds (finding 5): checkpoint-to-
    checkpoint wobble independent across steps gives phi's null mean
    approx 1/2 at EVERY clear index (Exp 4's R-7 arithmetic: the
    shared t_1 baseline makes Cov(x_pre, x_end) = Var(the t_1 term),
    correlation exactly 1/2, and the regression E[x_pre|x_end] =
    x_end/2 for jointly-normal x_pre/x_end holds independent of the
    conditioning value). Individual placebo phi values are noisy
    (Var(x_pre|x_end) does not shrink with |x_end|), so this pools the
    eligible rungs' phi across `range(60)` world seeds -- never a
    single searched seed -- rather than redrawing many batteries from
    one seed's small eligible set, which does not converge (see the
    Task 2 fix report for the reviewer's per-seed numbers)."""
    per_c = _pooled_eligible_phi(
        lambda seed: fakes.iid_noise_world(n_flat=CAL_N_FLAT, n_steps=20, sigma=0.05, seed=seed),
        (3, 5, 8, 10, 14, 18), CAL_ITEM_SIGMA_IID)
    for c, vals in per_c.items():
        assert len(vals) >= 30, f"c={c}: only {len(vals)} pooled eligible draws"
        mean = float(np.mean(vals))
        assert abs(mean - 0.5) < 0.08, f"c={c}: pooled mean {mean} over {len(vals)} draws"


def test_random_walk_world_placebo_phi_mean_tracks_fraction_elapsed_pooled_over_seeds():
    """Step 1(e), pooled over seeds (finding 5): a drift that
    ACCUMULATES (flats as cumulative sums of iid increments) gives
    phi's null mean approx (c-1)/(G-1) — the same regression argument,
    now with Cov(x_pre, x_end) = (c-1)*step-variance under a random
    walk started at t_1. Pooled across `range(60)` world seeds for the
    same reason as the iid-noise check above."""
    g = 20
    per_c = _pooled_eligible_phi(
        lambda seed: fakes.random_walk_world(n_flat=CAL_N_FLAT, n_steps=g,
                                             step_sigma=CAL_STEP_SIGMA_RW, seed=seed),
        (5, 10, 18), CAL_ITEM_SIGMA_RW)
    for c, vals in per_c.items():
        assert len(vals) >= 30, f"c={c}: only {len(vals)} pooled eligible draws"
        mean = float(np.mean(vals))
        want = (c - 1) / (g - 1)
        assert abs(mean - want) < 0.1, f"c={c}: pooled mean {mean} want {want} over {len(vals)}"


# ----------------------------------------------------------- (f) draw_batteries


def _hand_pool():
    return {
        "T": {
            "f0": {"x_end": 1.0, "se": 0.1, "eligible": True,
                  "excess": [0.0, 0.1, 0.3, 0.6, 1.0]},
            "f1": {"x_end": 0.9, "se": 0.1, "eligible": True,
                  "excess": [0.0, 0.05, 0.2, 0.5, 0.9]},
            "f2": {"x_end": 0.0, "se": 0.1, "eligible": False,
                  "excess": [0.0, 0.0, 0.0, 0.0, 0.0]},
        }
    }


def test_draw_batteries_4b_counts_multiset_and_pool_restriction():
    pools = _hand_pool()
    design = {"T": {"n": 4, "clear_indices": [2, 3, 3, 4], "rungs": []}}
    batteries = pl.draw_batteries_4b(pools, design, B=200, seed=0)
    assert batteries["feasibility"]["T"]["n_real"] == 4
    assert batteries["feasibility"]["T"]["n_eligible_placebo"] == 2
    assert batteries["feasibility"]["T"]["deficit"] is True  # 2 < MIN_PLACEBO_PER_TRAJ_4B (3)
    assert batteries["P"]["T"] == ["f0", "f1"]
    for battery_cells in batteries["cells"]:
        assert len(battery_cells) == 4
        assert sorted(c["c"] for c in battery_cells) == [2, 3, 3, 4]
        assert all(c["rung"] in ("f0", "f1") for c in battery_cells)
        assert all(c["traj"] == "T" for c in battery_cells)


def test_draw_batteries_4b_raises_when_no_eligible_placebo_rung():
    pools = {"T": {"f0": {"x_end": 0.0, "se": 0.1, "eligible": False, "excess": [0.0, 0.0, 0.0]}}}
    design = {"T": {"n": 2, "clear_indices": [2, 2], "rungs": []}}
    with pytest.raises(ValueError, match="4b: no eligible placebo rung on T"):
        pl.draw_batteries_4b(pools, design, B=10, seed=0)


def test_draw_batteries_4b_skips_zero_n_trajectories():
    pools = {"T": _hand_pool()["T"], "U": {}}
    design = {"T": {"n": 2, "clear_indices": [2, 3], "rungs": []},
             "U": {"n": 0, "clear_indices": [], "rungs": []}}
    batteries = pl.draw_batteries_4b(pools, design, B=20, seed=0)
    assert np.all(np.isnan(batteries["per_traj_mean"]["U"]))
    assert not np.any(np.isnan(batteries["per_traj_mean"]["T"]))
    for battery_cells in batteries["cells"]:
        assert all(c["traj"] == "T" for c in battery_cells)


def test_draw_batteries_4b_rng_reused_when_given():
    pools = _hand_pool()
    design = {"T": {"n": 4, "clear_indices": [2, 3, 3, 4], "rungs": []}}
    rng_a = np.random.default_rng(7)
    rng_b = np.random.default_rng(7)
    out_a = pl.draw_batteries_4b(pools, design, B=50, seed=0, rng=rng_a)
    out_b = pl.draw_batteries_4b(pools, design, B=50, seed=0, rng=rng_b)
    assert out_a["cells"] == out_b["cells"]


def test_draw_batteries_4b_clear_index_assignment_is_permuted_per_draw():
    """Mutation harness finding (Task 6): the multiset check above
    (`sorted(c["c"] ...) == [2,3,3,4]`) holds whether or not `order =
    rng.permutation(n)` is a genuine per-draw permutation or the fixed
    identity `np.arange(n)` -- both produce the SAME set of `c` values
    on every battery, just paired with the picked rungs differently.
    Distinguishes by checking that the FIRST cell's `c` value (bound to
    `order[0]`) takes more than one distinct value across many draws --
    under the identity-order mutant, `order[0]` is always 0, so the
    first cell's `c` is always `clear_indices[0]` (2) on every one of
    the 300 draws; under a genuine permutation it varies."""
    pools = _hand_pool()
    design = {"T": {"n": 4, "clear_indices": [2, 3, 3, 4], "rungs": []}}
    batteries = pl.draw_batteries_4b(pools, design, B=300, seed=0)
    first_cs = {battery_cells[0]["c"] for battery_cells in batteries["cells"]}
    assert len(first_cs) > 1, first_cs


# ---------------------------------------------------------------- (g) p_cal_4b


def test_p_cal_4b_hand_example():
    T_b = np.array([0.1, 0.2, 0.3, 0.4])
    out = pl.p_cal_4b(T_b, 0.3)
    assert out["p_cal"] == pytest.approx((1 + 2) / 5)
    out2 = pl.p_cal_4b(T_b, 0.35)
    assert out2["p_cal"] == pytest.approx((1 + 1) / 5)

    out3 = pl.p_cal_4b(T_b, 0.2)
    assert out3["p_low"] == pytest.approx((1 + 2) / 5)  # .1,.2 <= .2
    assert out["B"] == 4


def test_p_cal_4b_p_low_boundary_at_exactly_t4_plus_eps():
    """Mutation harness finding (Task 6): `p_low`'s tolerance band is
    `T_b <= T4 + eps` (eps = 1e-15) -- weakening it to `<` is
    undetectable at any T_b value that is not EXACTLY `T4 + eps` (a
    T_b element equal to T4 itself, e.g. the hand example above's 0.2
    against T4=0.2, satisfies BOTH `0.2 <= 0.2+eps` and `0.2 <
    0.2+eps`, since floating-point addition of 1e-15 to 0.2 is itself
    representable as strictly larger). Constructed at T4=0.0 so `T4 +
    eps` IS exactly `1e-15` in float64, and the one T_b element is
    exactly that boundary value: `<=` counts it (p_low = (1+1)/2 = 1.0),
    `<` does not (p_low = (1+0)/2 = 0.5)."""
    out = pl.p_cal_4b(np.array([1e-15]), 0.0)
    assert out["p_low"] == pytest.approx(1.0)


# --------------------------------------------------------------- (h) t_star_4b


def test_t_star_4b_interval_ordering_and_quantiles():
    rng = np.random.default_rng(0)
    T_b = rng.normal(0.3, 0.05, size=500)
    out = pl.t_star_4b(T_b, 0.6)
    assert out["interval"][0] <= out["interval"][1]
    assert out["q99"] >= out["q95"]
    assert out["T_star"] == pytest.approx(0.6 - out["null_mean"])


# ----------------------------------------------------------- (i) alpha_placebo


def _all_phi_battery(phi_value, n_rungs=8, B=40):
    cells_all = []
    for _ in range(B):
        cells_all.append([{"traj": "T", "rung": f"r{i}", "phi": phi_value} for i in range(n_rungs)])
    return {"cells": cells_all}


def test_alpha_placebo_4b_all_ones_leads_every_battery():
    batteries = _all_phi_battery(1.0)
    out = pl.alpha_placebo_4b(batteries, seed=0)
    assert out["alpha_placebo"] == 1.0
    assert out["n_leads"] == out["n_batteries"] == 40
    assert out["world_counts"]["LEADS"] == 40


def test_alpha_placebo_4b_all_zeros_never_leads():
    batteries = _all_phi_battery(0.0)
    out = pl.alpha_placebo_4b(batteries, seed=0)
    assert out["alpha_placebo"] == 0.0
    assert out["n_leads"] == 0
    assert out["world_counts"]["LEADS"] == 0
    assert out["world_counts"]["UNDETERMINED"] + out["world_counts"]["FOLLOWS"] == 40


def test_alpha_placebo_4b_b_alpha_caps_batteries():
    batteries = _all_phi_battery(1.0, B=40)
    out = pl.alpha_placebo_4b(batteries, seed=0, b_alpha=10)
    assert out["n_batteries"] == 10
    assert out["n_leads"] == 10


# ---------------------------------------------------------------- per_traj_4b


def test_per_traj_4b_reads_v4_t_and_calibrates_against_per_traj_mean():
    T_b = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    batteries = {"per_traj_mean": {"T": T_b}}
    design = {"T": {"n": 4, "clear_indices": [2, 3, 4, 5], "rungs": []}}
    v4_per_traj = {"T": {"T": 0.6}}
    out = pl.per_traj_4b(batteries, design, v4_per_traj)
    assert out["T"]["T_obs"] == 0.6
    assert out["T"]["n_cells"] == 4
    want = pl.p_cal_4b(T_b, 0.6)
    assert out["T"]["p_cal"] == want["p_cal"]


def test_per_traj_4b_raises_on_nan_per_traj_mean():
    batteries = {"per_traj_mean": {"U": np.array([np.nan, np.nan])}}
    design = {"U": {"n": 0, "clear_indices": [], "rungs": []}}
    with pytest.raises(ValueError, match="carries NaN"):
        pl.per_traj_4b(batteries, design, {"U": {"T": 0.5}})


# ----------------------------------------------------------------- (j) per_type


def test_per_type_4b_uses_only_same_type_rungs_and_none_for_empty_type():
    cells = [
        {"traj": "pythia_2.8b", "rung": "add3_mid", "phi": 0.7, "t_clear_index": 5},
        {"traj": "olmo2_7b", "rung": "reverse_string", "phi": 0.6, "t_clear_index": 6},
    ]

    def mk_excess(x_end, n=8):
        return [0.0] + [x_end * i / (n - 1) for i in range(1, n)]

    pools = {
        "pythia_2.8b": {
            "sub_base8": {"x_end": 1.0, "se": 0.05, "eligible": True, "excess": mk_excess(1.0)},
            "antonym": {"x_end": 1.0, "se": 0.05, "eligible": True, "excess": mk_excess(1.0)},
        },
        "olmo2_7b": {
            "rev_string7": {"x_end": 1.0, "se": 0.05, "eligible": True, "excess": mk_excess(1.0)},
            "antonym6": {"x_end": 1.0, "se": 0.05, "eligible": True, "excess": mk_excess(1.0)},
        },
        "smollm3_3b": {},
        "comma_7b": {},
    }
    out = pl.per_type_4b(pools, cells, B=100, seed=0)
    assert out["option"] is None  # no real cells of type option

    assert out["arithmetic"]["n_cells"] == 1
    assert out["arithmetic"]["reason"] is None  # fully covered -- not a refusal
    # Only ONE eligible arithmetic-type placebo rung exists on
    # pythia_2.8b ("sub_base8"; "antonym" is option-typed) and none on
    # any other trajectory with an arithmetic real cell, so every
    # battery draws the SAME rung deterministically -- a leaked
    # cross-type draw would introduce variance across batteries.
    assert out["arithmetic"]["null_sd"] == pytest.approx(0.0, abs=1e-12)

    assert out["string"]["n_cells"] == 1
    assert out["string"]["reason"] is None
    assert out["string"]["null_sd"] == pytest.approx(0.0, abs=1e-12)


def test_per_type_4b_refuses_when_a_contributing_trajectory_has_no_null_coverage():
    """Finding 4: pythia_2.8b has a real arithmetic cell but its only
    eligible placebo rung is option-typed, so the arithmetic type
    battery would zero pythia_2.8b entirely -- the ONLY trajectory
    contributing to T_obs -- leaving an EMPTY null. per_type_4b must
    refuse (p_cal/T_star/etc. all None, with a reason) rather than
    compute a calibration against no draws, and must do so WITHOUT any
    RuntimeWarning (asserted here by turning warnings into errors, not
    merely by their absence going unchecked)."""
    cells = [{"traj": "pythia_2.8b", "rung": "add3_mid", "phi": 0.7, "t_clear_index": 5}]
    pools = {
        "pythia_2.8b": {"antonym": {"x_end": 1.0, "se": 0.05, "eligible": True,
                                    "excess": [0.0, 0.2, 0.5, 0.7, 0.9, 1.0]}},
        "olmo2_7b": {}, "smollm3_3b": {}, "comma_7b": {},
    }
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        out = pl.per_type_4b(pools, cells, B=20, seed=0)

    assert out["arithmetic"]["feasibility"]["pythia_2.8b"]["n_real"] == 1
    assert out["arithmetic"]["feasibility"]["pythia_2.8b"]["n_eligible_placebo"] == 0
    assert out["arithmetic"]["feasibility"]["pythia_2.8b"]["deficit"] is True
    assert out["arithmetic"]["n_cells"] == 1
    assert out["arithmetic"]["p_cal"] is None
    assert out["arithmetic"]["T_star"] is None
    assert out["arithmetic"]["interval"] is None
    assert out["arithmetic"]["null_mean"] is None
    assert out["arithmetic"]["null_sd"] is None
    assert out["arithmetic"]["reason"] is not None
    assert "pythia_2.8b" in out["arithmetic"]["reason"]


# ---------------------------------------------------------------- (k) s5


def test_s5_autocorr_4b_near_zero_on_iid_near_half_on_ar1():
    series0, flat0 = fakes.autocorr_world(n_flat=30, n_steps=20, rho=0.0, sigma=0.05, seed=3)
    out0 = pl.s5_autocorr_4b({"T": series0}, {"T": {"flat": flat0}})
    assert abs(out0["T"]["mean_of_rungs"]) < 0.15
    assert abs(out0["T"]["pooled"]) < 0.15

    series1, flat1 = fakes.autocorr_world(n_flat=30, n_steps=20, rho=0.5, sigma=0.05, seed=3)
    out1 = pl.s5_autocorr_4b({"T": series1}, {"T": {"flat": flat1}})
    assert abs(out1["T"]["mean_of_rungs"] - 0.5) < 0.15
    assert abs(out1["T"]["pooled"] - 0.5) < 0.15


# ---------------------------------------------------------------- (l) s4


def test_s4_scatter_ratio_4b_flat_side_scale_relationship_is_exact():
    """Important 3/4 (final review): the flat side's UNCORRECTED
    leave-one-out RMS (`rms_flat_loo`) and its CORRECTED value
    (`rms_flat`) satisfy `rms_flat_loo == rms_flat * loo_scale_factor`
    EXACTLY (Important 4's algebraic identity: `x_full(t) = ((n-1)/n) *
    x_loo(t)` holds pointwise for the SAME realized data, not merely in
    expectation, so this is a bit-level check, not a statistical one --
    a mutant that drops the division, or computes the factor as
    `(n-1)/n` instead of `n/(n-1)`, fails it deterministically).
    `loo_scale_factor` itself is independently re-derived from
    `len(flat)` here, not read back from the function's own output."""
    series, flat = fakes.iid_noise_world(n_flat=10, n_steps=20, sigma=0.05, seed=5)
    a = fakes.rising_rung_series(series["steps"], series["a"], rung="rising0",
                                 extra_drift=[0.0] * 20, base_sigma=0.05, seed=9)
    series2 = {"steps": series["steps"], "a": a}
    cells = [{"traj": "T", "rung": "rising0", "t_clear_index": 12}]
    out = pl.s4_scatter_ratio_4b({"T": series2}, {"T": {"flat": flat}}, cells)
    rec = out["per_traj"]["T"]
    n = len(flat)
    want_factor = n / (n - 1)
    assert rec["loo_scale_factor"] == pytest.approx(want_factor)
    assert rec["rms_flat_loo"] == pytest.approx(rec["rms_flat"] * want_factor)
    # sanity: the corrected value is strictly SMALLER than the raw LOO
    # value (n/(n-1) > 1 for n >= 2, so dividing shrinks it).
    assert rec["rms_flat"] < rec["rms_flat_loo"]


def test_s4_scatter_ratio_4b_near_one_when_scales_match_pooled_over_worlds():
    """Important 3, "the existing test (l) tightened accordingly": a
    single seed's ratio has substantial sampling noise (one rising rung
    contributes only `n_steps - 2` increments), so this pools rising/
    flat increments across `N_WORLDS` independent synthetic
    trajectories (the same `s4_scatter_ratio_4b` call, given many
    `series_by_traj`/`rung_sets`/`cells` entries, already pools every
    trajectory's increments into ONE `pooled` ratio -- this reuses that
    machinery rather than averaging per-world ratios by hand) before
    reading `pooled.ratio`, tightened from the original single-seed
    0.2 to 0.1 -- comfortably inside what a matched-scale world gives
    post-fix (empirically ~1.0-1.04 at n_flat=30/60 pooled worlds) and
    tighter than the pre-fix bias would have allowed (empirically
    ~0.98, itself close to 1 at this n_flat -- see
    `test_s4_scatter_ratio_4b_flat_side_scale_relationship_is_exact`
    above for the test that actually discriminates the fix, bit-exact
    rather than statistical)."""
    n_flat, n_worlds = 30, 60
    series_by_traj, rung_sets, cells = {}, {}, []
    for i in range(n_worlds):
        series, flat = fakes.iid_noise_world(n_flat=n_flat, n_steps=20, sigma=0.05, seed=i)
        a = fakes.rising_rung_series(series["steps"], series["a"], rung="rising0",
                                     extra_drift=[0.0] * 20, base_sigma=0.05, seed=i + 10_000)
        key = f"W{i}"
        series_by_traj[key] = {"steps": series["steps"], "a": a}
        rung_sets[key] = {"flat": flat}
        cells.append({"traj": key, "rung": "rising0", "t_clear_index": 12})
    out = pl.s4_scatter_ratio_4b(series_by_traj, rung_sets, cells)
    assert abs(out["pooled"]["ratio"] - 1.0) < 0.1


# --------------------------------------------------------------------- S3/S8


def _small_real_world():
    """A tiny hand world with one trajectory, three flat rungs and one
    real (rising) cell, for S3/S8 smoke tests."""
    steps = list(range(8))
    a = {
        "f0": [0.5, 0.55, 0.6, 0.62, 0.7, 0.8, 0.9, 1.0],
        "f1": [0.5, 0.52, 0.58, 0.65, 0.68, 0.75, 0.85, 0.95],
        "f2": [0.5, 0.48, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8],
        "rising0": [0.5, 0.6, 0.8, 1.0, 1.3, 1.6, 1.9, 2.2],
    }
    series = {"steps": steps, "a": a}
    flat = ["f0", "f1", "f2"]
    rung_sets = {"flat": flat, "R": ["rising0"]}
    return series, flat, rung_sets


def test_s3_shape_4b_per_cell_residual_and_pooled_bins():
    series0, flat, rung_sets = _small_real_world()
    series, pia_t1, pia_end = fakes.matching_pia(series0, flat, item_sigma=0.01, seed=1)
    pool = pl.placebo_pool_4b(series, pia_t1, pia_end, flat, n_boot=100, seed=0)
    design = {"T": {"n": 1, "clear_indices": [5], "rungs": ["rising0"]}}
    batteries = pl.draw_batteries_4b({"T": pool}, design, B=200, seed=0)

    trend = an.trend_4(series["a"], flat, steps=series["steps"])
    excess = an.excess_4(series["a"], trend, series["steps"])
    phi_obs = an.phi_4(excess["rising0"], 5)
    real_cells = [{"traj": "T", "rung": "rising0", "phi": phi_obs, "t_clear_index": 5}]

    out = pl.s3_shape_4b(batteries, design, real_cells)
    assert "T" in out["per_traj_c"] and 5 in out["per_traj_c"]["T"]
    assert out["per_traj_c"]["T"][5]["n"] == 200
    assert sum(b["n"] for b in out["pooled_bins"].values()) == 200
    assert len(out["per_cell"]) == 1
    cell = out["per_cell"][0]
    assert cell["phi_obs"] == pytest.approx(phi_obs)
    assert cell["e"] == pytest.approx(phi_obs - out["per_traj_c"]["T"][5]["mean"])
    assert 0.0 <= cell["quantile"] <= 1.0


def test_s8_curves_4b_per_index_quantile_curve():
    series0, flat, rung_sets = _small_real_world()
    series, pia_t1, pia_end = fakes.matching_pia(series0, flat, item_sigma=0.01, seed=1)
    pool = pl.placebo_pool_4b(series, pia_t1, pia_end, flat, n_boot=100, seed=0)
    design = {"T": {"n": 1, "clear_indices": [5], "rungs": ["rising0"]}}
    batteries = pl.draw_batteries_4b({"T": pool}, design, B=200, seed=0)

    trend = an.trend_4(series["a"], flat, steps=series["steps"])
    excess = an.excess_4(series["a"], trend, series["steps"])
    phi_obs = an.phi_4(excess["rising0"], 5)
    real_cells = [{"traj": "T", "rung": "rising0", "phi": phi_obs, "t_clear_index": 5}]

    out = pl.s8_curves_4b({"T": series}, {"T": rung_sets}, real_cells, {"T": pool}, batteries)
    assert len(out) == 1
    curve = out[0]["curve"]
    assert len(curve) == 5  # i in range(c=5)
    for point in curve:
        assert point["quantile"] is None or 0.0 <= point["quantile"] <= 1.0
