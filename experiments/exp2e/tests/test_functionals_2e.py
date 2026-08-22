"""functionals_2e: the §5.1 family (F1 primary, F2, F3, B0), the
continuity constant, the §5.5 sensitivities, the paired bootstrap and
the §6 tree — pure functions on synthetic tallies."""
import math

import numpy as np
import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2d import stats_2d as st
from experiments.exp2e import functionals_2e as fn

RUNGS = ("a1", "a2", "b1", "b2", "c1")
SIZES = ("410m", "1b")


def _cells(verified: dict, n=32_000):
    """{(rung, size): verified} → 2d's tier-loader shape."""
    return {(r, s): {"verified": v, "n_draws": n, "rate": v / n}
            for (r, s), v in verified.items()}


def _floors(d):
    return {r: {"floor": c, "majority_floor": c} for r, c in d.items()}


# --------------------------------------------------------------- epsilon

def test_eps_is_half_a_draw():
    assert fn.eps_for(32_000) == 1 / 64_000
    assert fn.eps_for(4_000) == 1 / 8_000
    assert fn.EPS_MAIN == 1 / 64_000 and fn.EPS_PILOT == 1 / 8_000
    with pytest.raises(ValueError):
        fn.eps_for(0)


# ------------------------------------------------------------------- F1

def test_f1_zero_rate_is_log_eps_over_floor():
    cells = _cells({("a1", "410m"): 0, ("a1", "1b"): 0})
    t = fn.f1_table(cells, _floors({"a1": .02}), rungs=("a1",), sizes=SIZES)
    assert t["a1"]["score"] == pytest.approx(math.log((1 / 64_000) / .02))
    assert t["a1"]["per_size"]["410m"] == t["a1"]["per_size"]["1b"]


def test_f1_at_floor_is_log_one_plus_eps_over_floor():
    # rate exactly the floor: log(1 + ε/c), ≈ 0 (≤ .0078 at the
    # battery's smallest floor .002) — NOT exactly zero, disclosed
    cells = _cells({("a1", "410m"): 640, ("a1", "1b"): 640})   # rate .02
    t = fn.f1_table(cells, _floors({"a1": .02}), rungs=("a1",), sizes=SIZES)
    assert t["a1"]["score"] == pytest.approx(math.log(1 + (1 / 64_000) / .02))
    assert 0 < t["a1"]["score"] < .001


def test_f1_is_mean_over_sizes_and_signed():
    cells = _cells({("a1", "410m"): 6400, ("a1", "1b"): 64})   # .2 and .002
    t = fn.f1_table(cells, _floors({"a1": .02}), rungs=("a1",), sizes=SIZES)
    e = 1 / 64_000
    want = (math.log((.2 + e) / .02) + math.log((.002 + e) / .02)) / 2
    assert t["a1"]["score"] == pytest.approx(want)
    assert t["a1"]["per_size"]["410m"] > 0 > t["a1"]["per_size"]["1b"]


def test_f1_eps_override_and_n_draws_refusal():
    cells = _cells({("a1", "410m"): 0, ("a1", "1b"): 0})
    t = fn.f1_table(cells, _floors({"a1": .02}), rungs=("a1",), sizes=SIZES,
                    eps=1 / 3_200)
    assert t["a1"]["score"] == pytest.approx(math.log((1 / 3_200) / .02))
    bad = _cells({("a1", "410m"): 0}); bad[("a1", "1b")] = {"verified": 0, "n_draws": 4_000, "rate": 0.0}
    with pytest.raises(ValueError, match="n_draws"):
        fn.f1_table(bad, _floors({"a1": .02}), rungs=("a1",), sizes=SIZES)


def test_f1_majority_only_floor_variant():
    floors = {"a1": {"floor": .25, "majority_floor": .026}}
    cells = _cells({("a1", "410m"): 3200, ("a1", "1b"): 3200})   # .1
    t = fn.f1_table(cells, floors, rungs=("a1",), sizes=SIZES)
    t_maj = fn.f1_table(cells, floors, rungs=("a1",), sizes=SIZES,
                        floor_key="majority_floor")
    assert t["a1"]["score"] < 0 < t_maj["a1"]["score"]


# ------------------------------------------------------------------- F2

def test_f2_raw_log_rate_ignores_floor():
    cells = _cells({("a1", "410m"): 6400, ("a1", "1b"): 64})
    t = fn.f2_table(cells, rungs=("a1",), sizes=SIZES)
    e = 1 / 64_000
    assert t["a1"]["score"] == pytest.approx(
        (math.log(.2 + e) + math.log(.002 + e)) / 2)


# ------------------------------------------------------------------- B0

def test_b0_is_minus_log_floor():
    t = fn.b0_table(_floors({"a1": .02, "a2": .25}), rungs=("a1", "a2"))
    assert t["a1"]["score"] == pytest.approx(-math.log(.02))
    assert t["a2"]["score"] == pytest.approx(-math.log(.25))
    assert t["a1"]["score"] > t["a2"]["score"]


# ------------------------------------------------------------------- F3

def test_f3_rank_residual_zero_when_rate_ranks_track_floor_ranks():
    floors = _floors({"a1": .01, "a2": .02, "b1": .05, "b2": .10, "c1": .20})
    v = {}
    for i, r in enumerate(RUNGS):
        for s in SIZES:
            v[(r, s)] = 100 * (i + 1)
    t = fn.f3_table(_cells(v), floors, rungs=RUNGS, sizes=SIZES)
    for r in RUNGS:
        assert t[r]["score"] == pytest.approx(0.0, abs=1e-12)
    assert t[RUNGS[0]]["rank_rate"] == 1.0 and t[RUNGS[-1]]["rank_floor"] == 5.0


def test_f3_residuals_sum_to_zero_and_are_orthogonal_to_floor_rank():
    floors = _floors({"a1": .01, "a2": .02, "b1": .05, "b2": .10, "c1": .20})
    v = {("a1", "410m"): 500, ("a1", "1b"): 400, ("a2", "410m"): 0,
         ("a2", "1b"): 0, ("b1", "410m"): 900, ("b1", "1b"): 1000,
         ("b2", "410m"): 10, ("b2", "1b"): 10, ("c1", "410m"): 300,
         ("c1", "1b"): 300}
    t = fn.f3_table(_cells(v), floors, rungs=RUNGS, sizes=SIZES)
    res = np.array([t[r]["score"] for r in RUNGS])
    z = np.array([t[r]["rank_floor"] for r in RUNGS])
    assert res.sum() == pytest.approx(0.0, abs=1e-9)
    assert float(res @ (z - z.mean())) == pytest.approx(0.0, abs=1e-9)
    # the mean rate over sizes is what is ranked; ties take midranks
    assert t["a1"]["mean_rate"] == pytest.approx(450 / 32_000)
    assert t["a2"]["rank_rate"] == 1.0


def test_f3_uses_midranks_on_tied_rates():
    floors = _floors({"a1": .01, "a2": .02, "b1": .05})
    v = {(r, s): 0 for r in ("a1", "a2", "b1") for s in SIZES}
    t = fn.f3_table(_cells(v), floors, rungs=("a1", "a2", "b1"), sizes=SIZES)
    assert all(t[r]["rank_rate"] == 2.0 for r in ("a1", "a2", "b1"))
    assert all(abs(t[r]["score"]) < 1e-12 for r in ("a1", "a2", "b1"))


# ------------------------------------------------------ paired bootstrap

def test_paired_bootstrap_single_arm_matches_2d_exactly():
    rng = np.random.default_rng(3)
    fams = [bt.FAMILY_OF[r] for r in bt.RUNGS]
    x1 = rng.normal(size=34)
    x2 = rng.normal(size=34)
    y = np.array([1] * 11 + [0] * 23)
    rng.shuffle(y)
    counts = st.bootstrap_counts_matrix(bt.N_FAMILIES)
    ref1 = st.cluster_bootstrap_auc(x1, y, fams, counts=counts)
    ref2 = st.cluster_bootstrap_auc(x2, y, fams, counts=counts)
    got = fn.cluster_bootstrap_auc_paired(x1, x2, y, fams, counts=counts)
    assert got["ci_1"] == ref1["ci"] and got["ci_2"] == ref2["ci"]
    assert got["n_valid"] == ref1["n_valid"] == ref2["n_valid"]
    assert got["n_dropped"] == ref1["n_dropped"]
    assert got["ci_diff"][0] <= got["diff_obs"] <= got["ci_diff"][1]
    assert got["diff_obs"] == pytest.approx(st.auc(x1, y) - st.auc(x2, y))


def test_paired_bootstrap_identical_arms_give_zero_diff():
    fams = [bt.FAMILY_OF[r] for r in bt.RUNGS]
    x = np.arange(34, dtype=float)
    y = np.array([1] * 11 + [0] * 23)
    counts = st.bootstrap_counts_matrix(bt.N_FAMILIES, n_boot=500)
    got = fn.cluster_bootstrap_auc_paired(x, x, y, fams, counts=counts)
    assert got["ci_diff"] == [0.0, 0.0] and got["diff_obs"] == 0.0


# ----------------------------------------------------------------- tree

def test_tree_referent_failure_is_insufficient_data_first():
    v = fn.verdict_tree_2e(referent_failures=["manifest: x.json"],
                           auc_obs=1.0, block_p=1e-5, ci=[.9, 1.0])
    assert v["verdict"] == "INSUFFICIENT_DATA" and "x.json" in v["reason"]


def test_tree_fail_pass_indeterminate_are_2ds():
    assert fn.verdict_tree_2e(referent_failures=[], auc_obs=.7, block_p=.001,
                              ci=[.5, .9])["verdict"] == "FAIL"
    assert fn.verdict_tree_2e(referent_failures=[], auc_obs=.8, block_p=.001,
                              ci=[.6, .95])["verdict"] == "PASS"
    assert fn.verdict_tree_2e(referent_failures=[], auc_obs=.7, block_p=.001,
                              ci=[.55, .9])["verdict"] == "INDETERMINATE"
    assert fn.verdict_tree_2e(referent_failures=[], auc_obs=.8, block_p=.02,
                              ci=[.6, .95])["verdict"] == "INDETERMINATE"
    # the bars are 2d's constants, not copies
    assert fn.ALPHA is st.ALPHA and fn.AUC_BAR is st.AUC_BAR
    assert fn.WORLDS == st.WORLDS


def test_tree_undefined_ci_is_not_a_verdict():
    with pytest.raises(ValueError):
        fn.verdict_tree_2e(referent_failures=[], auc_obs=.8, block_p=.001,
                           ci=[None, None])


# ----------------------------------------------------- restricted layout

def test_drop_rungs_layout_recomputes_family_sizes():
    kept, sizes, fams = fn.drop_rungs_layout(("base12_digitsum", "base13"))
    assert len(kept) == 32 and sum(sizes) == 32
    assert "base12_digitsum" not in kept and "base7" in kept
    # base_repr shrinks from 4 to 2; every other family unchanged
    assert sizes[bt.FAMILY_ORDER.index("base_repr")] == 2
    assert len(fams) == 32 and fams[kept.index("base7")] == "base_repr"
