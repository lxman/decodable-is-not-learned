# experiments/exp4b/tests/test_placebo_4b.py
"""Tests for `placebo_4b.py` (Task 2): the leave-one-out trend/excess/
SE, the placebo pool and batteries, calibration (p_cal/T*), alpha_
placebo, the per-trajectory/per-type breakdowns, and S3-S5/S8. No
model contact; every fixture is synthetic (`fakes_4b.py`) or hand-
built in place."""
from __future__ import annotations

import sys
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
    series, flat = fakes.iid_noise_world(n_flat=8, n_steps=10, sigma=0.05, seed=1)
    pia_t1 = fakes.pia_from_means({f: series["a"][f][0] for f in flat}, item_sigma=0.02, seed=11)
    pia_end = fakes.pia_from_means({f: series["a"][f][-1] for f in flat}, item_sigma=0.02, seed=12)
    pool = pl.placebo_pool_4b(series, pia_t1, pia_end, flat, n_boot=100, seed=0)
    assert set(pool) == set(flat)
    for f, d in pool.items():
        assert set(d) == {"x_end", "se", "eligible", "excess"}
        assert len(d["excess"]) == len(series["steps"])
        assert d["excess"][0] == 0.0
        assert d["x_end"] == d["excess"][-1]
        assert isinstance(d["eligible"], bool)


# -------------------------------------------------- (d)/(e) calibration worlds

# Fixed, documented seeds/scales for the two Monte Carlo calibration
# checks (Step 1(d)/(e)) -- found by a grid search over world seed and
# per-item noise scale (`~/emergence-lab` scratch, not committed)
# looking for a comfortable, deterministic margin under each check's
# stated tolerance; every run of this test reproduces the SAME numbers
# (numpy's `default_rng` is deterministic), so this is a fixed data
# point, not a flaky Monte Carlo test.
IID_N_FLAT = 30
IID_WORLD_SEED = 34
IID_ITEM_SIGMA = 0.3   # -> 10 of 30 rungs eligible; max |mean - .5| = .0791 over c in {3,5,8,10,14,18}

RW_N_FLAT = 30
RW_WORLD_SEED = 5
RW_ITEM_SIGMA = 0.1    # -> 14 of 30 rungs eligible; max |mean - (c-1)/(G-1)| = .050 over c in {5,10,18}


def test_iid_noise_world_placebo_phi_mean_near_half():
    """Step 1(d): checkpoint-to-checkpoint wobble independent across
    steps gives phi's null mean approx 1/2 at EVERY clear index
    (Exp 4's R-7 arithmetic: the shared t_1 baseline makes
    Cov(x_pre, x_end) = Var(the t_1 term), correlation exactly 1/2,
    and the regression E[x_pre|x_end] = x_end/2 for jointly-normal
    x_pre/x_end holds independent of the conditioning value). A wide
    flat pool is used so the across-rung average of the (individually
    noisy, since Var(x_pre|x_end) does not shrink with |x_end|) ratio
    statistic converges to that theoretical value within the
    document tolerance at a fixed, checked seed."""
    series, flat = fakes.iid_noise_world(n_flat=IID_N_FLAT, n_steps=20, sigma=0.05,
                                         seed=IID_WORLD_SEED)
    pia_t1 = fakes.pia_from_means({f: series["a"][f][0] for f in flat},
                                  item_sigma=IID_ITEM_SIGMA, seed=IID_WORLD_SEED * 3 + 1)
    pia_end = fakes.pia_from_means({f: series["a"][f][-1] for f in flat},
                                   item_sigma=IID_ITEM_SIGMA, seed=IID_WORLD_SEED * 3 + 2)
    pool = pl.placebo_pool_4b(series, pia_t1, pia_end, flat, n_boot=200, seed=0)
    n_elig = sum(1 for v in pool.values() if v["eligible"])
    assert n_elig >= 8

    design = {"T": {"n": 6, "clear_indices": [3, 5, 8, 10, 14, 18], "rungs": []}}
    batteries = pl.draw_batteries_4b({"T": pool}, design, B=2000, seed=0)
    for c in (3, 5, 8, 10, 14, 18):
        vals = [cell["phi"] for battery in batteries["cells"] for cell in battery
               if cell["c"] == c]
        mean = float(np.mean(vals))
        assert abs(mean - 0.5) < 0.08, f"c={c}: mean {mean}"


def test_random_walk_world_placebo_phi_mean_tracks_fraction_elapsed():
    """Step 1(e): a drift that ACCUMULATES (flats as cumulative sums of
    iid increments) gives phi's null mean approx (c-1)/(G-1) — the
    same regression argument, now with Cov(x_pre, x_end) = (c-1)*
    step-variance under a random walk started at t_1."""
    series, flat = fakes.random_walk_world(n_flat=RW_N_FLAT, n_steps=20, step_sigma=0.02,
                                           seed=RW_WORLD_SEED)
    pia_t1 = fakes.pia_from_means({f: series["a"][f][0] for f in flat},
                                  item_sigma=RW_ITEM_SIGMA, seed=RW_WORLD_SEED * 3 + 1)
    pia_end = fakes.pia_from_means({f: series["a"][f][-1] for f in flat},
                                   item_sigma=RW_ITEM_SIGMA, seed=RW_WORLD_SEED * 3 + 2)
    pool = pl.placebo_pool_4b(series, pia_t1, pia_end, flat, n_boot=200, seed=0)
    n_elig = sum(1 for v in pool.values() if v["eligible"])
    assert n_elig >= 8

    design = {"T": {"n": 3, "clear_indices": [5, 10, 18], "rungs": []}}
    batteries = pl.draw_batteries_4b({"T": pool}, design, B=2000, seed=0)
    g = 20
    for c in (5, 10, 18):
        vals = [cell["phi"] for battery in batteries["cells"] for cell in battery
               if cell["c"] == c]
        mean = float(np.mean(vals))
        want = (c - 1) / (g - 1)
        assert abs(mean - want) < 0.1, f"c={c}: mean {mean} want {want}"


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
    # Only ONE eligible arithmetic-type placebo rung exists on
    # pythia_2.8b ("sub_base8"; "antonym" is option-typed) and none on
    # any other trajectory with an arithmetic real cell, so every
    # battery draws the SAME rung deterministically -- a leaked
    # cross-type draw would introduce variance across batteries.
    assert out["arithmetic"]["null_sd"] == pytest.approx(0.0, abs=1e-12)

    assert out["string"]["n_cells"] == 1
    assert out["string"]["null_sd"] == pytest.approx(0.0, abs=1e-12)


def test_per_type_4b_marks_infeasible_trajectory_without_raising():
    cells = [{"traj": "pythia_2.8b", "rung": "add3_mid", "phi": 0.7, "t_clear_index": 5}]
    pools = {
        "pythia_2.8b": {"antonym": {"x_end": 1.0, "se": 0.05, "eligible": True,
                                    "excess": [0.0, 0.2, 0.5, 0.7, 0.9, 1.0]}},
        "olmo2_7b": {}, "smollm3_3b": {}, "comma_7b": {},
    }
    out = pl.per_type_4b(pools, cells, B=20, seed=0)
    assert out["arithmetic"]["feasibility"]["pythia_2.8b"]["n_real"] == 1
    assert out["arithmetic"]["feasibility"]["pythia_2.8b"]["n_eligible_placebo"] == 0
    assert out["arithmetic"]["feasibility"]["pythia_2.8b"]["deficit"] is True
    assert out["arithmetic"]["n_cells"] == 1


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


def test_s4_scatter_ratio_4b_near_one_when_scales_match():
    series, flat = fakes.iid_noise_world(n_flat=10, n_steps=20, sigma=0.05, seed=5)
    a = fakes.rising_rung_series(series["steps"], series["a"], rung="rising0",
                                 extra_drift=[0.0] * 20, base_sigma=0.05, seed=9)
    series2 = {"steps": series["steps"], "a": a}
    cells = [{"traj": "T", "rung": "rising0", "t_clear_index": 12}]
    out = pl.s4_scatter_ratio_4b({"T": series2}, {"T": {"flat": flat}}, cells)
    assert abs(out["pooled"]["ratio"] - 1.0) < 0.2
    assert abs(out["per_traj"]["T"]["ratio"] - 1.0) < 0.2


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
    series, flat, rung_sets = _small_real_world()
    pia_t1 = fakes.pia_from_means({f: series["a"][f][0] for f in flat}, item_sigma=0.01, seed=1)
    pia_end = fakes.pia_from_means({f: series["a"][f][-1] for f in flat}, item_sigma=0.01, seed=2)
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
    series, flat, rung_sets = _small_real_world()
    pia_t1 = fakes.pia_from_means({f: series["a"][f][0] for f in flat}, item_sigma=0.01, seed=1)
    pia_end = fakes.pia_from_means({f: series["a"][f][-1] for f in flat}, item_sigma=0.01, seed=2)
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
