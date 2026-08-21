"""stats_2d: the bar, the margin, the AUC, 2c's block group with the
AUC statistic, the dropped-and-counted bootstrap, the tree."""
import numpy as np
import pytest
from scipy.stats import binomtest

from experiments.exp2c.run import power_table as pt2c
from experiments.exp2d import battery_2d as bt
from experiments.exp2d import stats_2d as st

FAMS = [f for _, f in bt.RUNG_ORDER_2D]


# ------------------------------------------------------------ the bar

def test_binomial_bar_is_one_sided_exact_at_alpha():
    r = st.binomial_bar(102, 500, 0.158)          # count_div13 at 12b
    assert r["p"] == pytest.approx(
        binomtest(102, 500, 0.158, alternative="greater").pvalue)
    assert r["significant"]                       # p .0037 < .01
    r = st.binomial_bar(14, 500, 0.014)           # sub3_mid at 6.9b: .028
    assert r["p"] == pytest.approx(0.0117, abs=2e-3) and not r["significant"]
    r = st.binomial_bar(0, 32000, 0.002)
    assert r["p"] == 1.0 and not r["significant"]


def test_bar_requires_rate_above_floor_even_if_p_small():
    # p < alpha can only happen with rate > floor for a 'greater'
    # test, but the conjunction is explicit; a degenerate floor is refused
    with pytest.raises(ValueError):
        st.binomial_bar(1, 10, 0.0)
    with pytest.raises(ValueError):
        st.binomial_bar(11, 10, 0.5)


def test_corrected_margin_formula_and_zeroing():
    m = st.corrected_margin(264, 500, 0.014)      # sub3_mid 2.8b .528
    assert m["significant"]
    assert m["margin"] == pytest.approx((0.528 - 0.014) / (1 - 0.014))
    m = st.corrected_margin(11, 500, 0.014)       # .022, p .097
    assert not m["significant"] and m["margin"] == 0.0
    assert m["cp95"][0] > 0
    m = st.corrected_margin(0, 32000, 0.002)
    assert m["margin"] == 0.0 and m["cp95"] == [0.0, pytest.approx(
        st.clopper_pearson(0, 32000)[1])]


# ------------------------------------------------------------- the AUC

def test_auc_midrank_identities():
    assert st.auc([1, 2, 3, 4], [0, 0, 1, 1]) == 1.0
    assert st.auc([1, 2, 3, 4], [1, 1, 0, 0]) == 0.0
    assert st.auc([0, 0, 0, 0], [1, 0, 1, 0]) == 0.5     # all ties
    assert st.auc([0, 0, 1, 0], [1, 0, 1, 0]) == 0.75    # one separated
    with pytest.raises(ValueError):
        st.auc([1, 2], [1, 1])


def test_auc_equals_pairwise_matrix_form():
    rng = np.random.default_rng(3)
    for _ in range(100):
        x = rng.integers(0, 3, size=12) * rng.random(12)
        y = rng.integers(0, 2, size=12)
        if y.sum() in (0, 12):
            continue
        S = st.auc_pairwise_matrix(x)
        assert st.auc(x, y) == pytest.approx(
            (y @ S @ (1 - y)) / (y.sum() * (12 - y.sum())), abs=1e-12)


# ------------------------------------------ 2c's block group, AUC stat

def test_block_group_is_2cs_routing_and_matrix():
    g = st.block_perm_group(bt.FAMILY_SIZES)
    assert g["method"] == "sampled" and g["group_size"] == 52_254_720
    rng = np.random.default_rng(st.PERM_SEED)
    want = pt2c.sampled_block_perms(list(bt.FAMILY_SIZES), st.PERM_SAMPLE, rng)
    assert np.array_equal(g["perms"], want)
    g2 = st.block_perm_group([2, 2, 2])
    assert g2["method"] == "enumerated" and g2["perms"].shape == (6, 6)
    assert np.array_equal(g2["perms"][0], np.arange(6))    # identity row 0


def test_block_perm_auc_enumerated_conventions():
    # x perfectly separates y; the identity is the only row reaching
    # the observed AUC among 3! block swaps of size-2 families where
    # y = (1,1 | 0,0 | 0,0): swapping puts the rising block elsewhere
    x = [6, 5, 4, 3, 2, 1]
    y = [1, 1, 0, 0, 0, 0]
    r = st.block_perm_auc_p(x, y, [2, 2, 2])
    assert r["auc_obs"] == 1.0 and r["method"] == "enumerated"
    assert r["count_ge"] == 2 and r["p"] == pytest.approx(2 / 6)
    assert r["resolution"] == pytest.approx(1 / 6)


def test_block_perm_auc_matches_loop_reference():
    rng = np.random.default_rng(5)
    fams = [2, 2, 1, 2, 1]
    x = rng.random(8)
    y = np.array([1, 0, 1, 1, 0, 0, 0, 0])
    g = st.block_perm_group(fams)
    r = st.block_perm_auc_p(x, y, fams, group=g)
    ref = [st.auc(x, y[idx]) for idx in g["perms"]]
    assert r["count_ge"] == sum(v >= r["auc_obs"] for v in ref)
    assert r["auc_obs"] == pytest.approx(ref[0])


def test_block_perm_sampled_add_one_convention():
    fams = list(bt.FAMILY_SIZES)
    y = np.zeros(34, dtype=int)
    y[[1, 2, 3, 4, 5]] = 1
    x = y * 1.0
    r = st.block_perm_auc_p(x, y, fams)
    assert r["method"] == "sampled" and r["n_perms"] == st.PERM_SAMPLE
    assert r["p"] == pytest.approx((1 + r["count_ge"]) / (st.PERM_SAMPLE + 1))
    assert r["resolution"] == pytest.approx(1 / (st.PERM_SAMPLE + 1))


def test_block_perm_layout_mismatch_refused():
    with pytest.raises(ValueError, match="family-contiguous"):
        st.block_perm_auc_p([1, 2, 3], [1, 0, 1], [2, 2])


def test_block_perm_x_not_permuted():
    """x is fixed to rung identity; only y moves. A permutation that
    swaps blocks must change the statistic only through y."""
    x = np.array([5, 4, 3, 2, 1, 0], dtype=float)
    y = np.array([1, 1, 0, 0, 0, 0])
    g = st.block_perm_group([2, 2, 2])
    _, stats = st._auc_over_perms(x, y, g["perms"])
    # moving the rising block to positions 2,3 or 4,5 gives AUCs .5 and 0
    assert sorted(set(np.round(stats, 6))) == [0.0, 0.5, 1.0]


# ---------------------------------------------------------- bootstrap

def test_bootstrap_counts_matrix_is_2cs_draw_order():
    C = st.bootstrap_counts_matrix(16, 5, seed=0)
    rng = np.random.default_rng(0)
    for b in range(5):
        pick = rng.choice(16, size=16, replace=True)
        want = np.bincount(pick, minlength=16)
        assert np.array_equal(C[b], want)
    assert (C.sum(1) == 16).all()


def test_cluster_bootstrap_auc_equals_expanded_multiset():
    rng = np.random.default_rng(11)
    x = np.where(rng.random(34) < .5, 0.0, rng.random(34))
    y = (rng.random(34) < .4).astype(int)
    C = st.bootstrap_counts_matrix(16, 200, seed=1)
    res = st.cluster_bootstrap_auc(x, y, FAMS, counts=C)
    fams, M = st.family_membership(FAMS)
    vals = []
    for b in range(200):
        rc = C[b] @ M
        xx, yy = np.repeat(x, rc), np.repeat(y, rc)
        if 0 < yy.sum() < len(yy):
            vals.append(st.auc(xx, yy))
    assert res["n_valid"] == len(vals)
    assert res["n_dropped"] == 200 - len(vals)
    assert res["boot_mean"] == pytest.approx(np.mean(vals))
    assert res["ci"] == [pytest.approx(np.percentile(vals, 2.5)),
                         pytest.approx(np.percentile(vals, 97.5))]


def test_bootstrap_drops_are_counted_never_imputed():
    """All rising rungs in ONE family: any resample missing that family
    has no rising rung and must be dropped, not scored .5."""
    y = np.zeros(34, dtype=int)
    y[:4] = 1                               # mid_digit only
    x = y * 1.0
    res = st.cluster_bootstrap_auc(x, y, FAMS, n_boot=2000)
    assert res["n_dropped"] > 0
    assert res["n_valid"] + res["n_dropped"] == 2000
    assert res["ci"] == [1.0, 1.0]          # every valid resample is perfect
    res2 = st.cluster_bootstrap_spearman(x, y * 1.0, FAMS, n_boot=500)
    assert res2["n_dropped"] > 0 and res2["n_valid"] + res2["n_dropped"] == 500


def test_bootstrap_all_dropped_yields_undefined_ci():
    y = np.zeros(34, dtype=int)
    res = st.cluster_bootstrap_auc(np.zeros(34), y, FAMS, n_boot=50)
    assert res["n_valid"] == 0 and res["ci"] == [None, None]


# ------------------------------------------------------------ the tree

def test_verdict_tree_precedence():
    v = st.verdict_tree(gate1_diff_cells=["reverse_string/1b"], auc_obs=1.0,
                        block_p=0.0, ci=[0.9, 1.0])
    assert v["verdict"] == "INSUFFICIENT_DATA"
    v = st.verdict_tree(gate1_diff_cells=[], auc_obs=0.9, block_p=0.001,
                        ci=[0.45, 1.0])
    assert v["verdict"] == "FAIL"
    v = st.verdict_tree(gate1_diff_cells=[], auc_obs=0.9, block_p=0.001,
                        ci=[0.6, 1.0])
    assert v["verdict"] == "PASS"
    v = st.verdict_tree(gate1_diff_cells=[], auc_obs=0.74, block_p=0.001,
                        ci=[0.6, 0.9])
    assert v["verdict"] == "INDETERMINATE"
    v = st.verdict_tree(gate1_diff_cells=[], auc_obs=0.9, block_p=0.011,
                        ci=[0.6, 1.0])
    assert v["verdict"] == "INDETERMINATE"
    v = st.verdict_tree(gate1_diff_cells=[], auc_obs=0.2, block_p=0.99,
                        ci=[0.1, 0.4])
    assert v["verdict"] == "INDETERMINATE"   # anti-predictive: not FAIL
    with pytest.raises(ValueError):
        st.verdict_tree(gate1_diff_cells=[], auc_obs=0.9, block_p=0.0,
                        ci=[None, None])


def test_tree_bar_is_inclusive_and_alpha_strict():
    v = st.verdict_tree(gate1_diff_cells=[], auc_obs=0.75, block_p=0.0099,
                        ci=[0.6, 0.9])
    assert v["verdict"] == "PASS"
    v = st.verdict_tree(gate1_diff_cells=[], auc_obs=0.75, block_p=0.01,
                        ci=[0.6, 0.9])
    assert v["verdict"] == "INDETERMINATE"
    v = st.verdict_tree(gate1_diff_cells=[], auc_obs=0.9, block_p=0.0,
                        ci=[0.5, 0.9])
    assert v["verdict"] == "FAIL"            # CI touching .5 includes it


def test_primary_test_bundle():
    y = np.zeros(34, dtype=int)
    y[[0, 1, 4, 5, 6]] = 1
    x = y + 0.01 * np.arange(34)
    r = st.primary_test(x, y, bt.FAMILY_SIZES, FAMS)
    assert r["auc"] == 1.0 and r["n_rising"] == 5 and r["n_flat"] == 29
    assert r["block"]["method"] == "sampled"
    assert r["bootstrap"]["n_valid"] + r["bootstrap"]["n_dropped"] == st.N_BOOT


# ------------------------------------------------- literal pins (2c's)

def test_frozen_constants_are_2cs_literally():
    assert st.ALPHA == 0.01 and st.AUC_BAR == 0.75
    assert st.N_BOOT == 10_000 and st.BOOT_SEED == 0
    assert st.PERM_SAMPLE == 100_000 and st.PERM_SEED == 0
    assert pt2c.EXACT_PERM_GUARD == 5_000_000


def test_block_group_matches_2c_draws_at_literal_seed_and_size():
    g = st.block_perm_group(bt.FAMILY_SIZES)
    want = pt2c.sampled_block_perms(list(bt.FAMILY_SIZES), 100_000,
                                    np.random.default_rng(0))
    assert g["perms"].shape == (100_000, 34)
    assert np.array_equal(g["perms"], want)


def test_bootstrap_counts_match_literal_seed_and_count():
    C = st.bootstrap_counts_matrix(16)
    assert C.shape == (10_000, 16)
    rng = np.random.default_rng(0)
    for b in range(3):
        pick = rng.choice(16, size=16, replace=True)
        assert np.array_equal(C[b], np.bincount(pick, minlength=16))


def test_block_perm_rows_equal_loop_reference_on_a_sampled_group():
    """Row-for-row (not just as a multiset): the r-th sampled statistic
    is the AUC of x against y[perms[r]] — y is what moves, x stays on
    rung identity. (Permuting x's ranks by π instead gives the same
    multiset over a full group but different rows on a sampled one.)"""
    rng = np.random.default_rng(9)
    y = np.zeros(34, dtype=int)
    y[[0, 1, 2, 4, 5, 6, 17, 21, 22, 27, 28, 32, 33]] = 1
    x = np.where(rng.random(34) < .4, 0.0, rng.random(34))
    g = st.block_perm_group(bt.FAMILY_SIZES)
    _, stats = st._auc_over_perms(x, y, g["perms"])
    for r in range(0, 100_000, 9973):
        assert stats[r] == pytest.approx(st.auc(x, y[g["perms"][r]]))
