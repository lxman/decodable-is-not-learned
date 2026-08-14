"""Fixture suite for 1c's primary test and verdict tree (design §5).

The verdict tree has a PRECEDENCE, and precedence is the thing that goes wrong
quietly: 2c reached FAIL on a branch adjudicated before the PASS branch was
ever tested, which is correct but only legible because the order was frozen in
advance. Every ordering rule here has its own test.
"""
import pytest

from experiments.exp1c import analyze_1c as a


# ------------------------------------------------------------------ builders

def blocks(margin_by_density, n=10):
    """n identical blocks, each mapping the four densities to a margin."""
    return [dict(margin_by_density) for _ in range(n)]


def rising(delta=0.10, n=10):
    """Margin rising linearly from 0 at 0.25 to `delta` at 0.85."""
    return blocks({d: delta * (d - 0.25) / 0.60 for d in a.DENSITIES}, n)


def flat(level=0.0, n=10):
    return blocks({d: level for d in a.DENSITIES}, n)


def sweep_cells(cls="silent", l0=0.0, depth=0.0):
    out = []
    for d in a.DENSITIES:
        for size in a.SIZES:
            for seed in a.SEEDS:
                out.append({"density": d, "size_bucket": size, "seed": seed,
                            "depth_margin": depth * (d - 0.25) / 0.60,
                            "l0_margin": l0, "class": cls})
    return out


def stage_a(passed=True):
    return {"pass": passed, "failures": [] if passed else ["above row 3/10"],
            "sd_depth_margin": 0.02}


# --------------------------------------------------------- the primary test

def test_a_clean_positive_trend_reaches_the_floor_p():
    out = a.slope_and_p(rising(0.10), n_draw=2000, seed=1)
    assert out["slope"] > 0
    assert out["p"] == pytest.approx(1 / 2001, rel=1e-6)


def test_a_flat_set_cannot_reject():
    """Every relabeling gives the same statistic, so p is exactly 1."""
    out = a.slope_and_p(flat(0.05), n_draw=2000, seed=1)
    assert out["slope"] == pytest.approx(0.0)
    assert out["p"] == pytest.approx(1.0)


def test_the_test_is_one_sided_and_a_negative_trend_cannot_pass():
    out = a.slope_and_p(rising(-0.10), n_draw=2000, seed=1)
    assert out["slope"] < 0
    assert out["p"] > 0.5


def test_a_constant_offset_is_not_a_trend():
    """Structure present at every density equally is not accumulation. The
    within-block relabeling null removes the level and keeps only the slope."""
    out = a.slope_and_p(flat(0.30), n_draw=2000, seed=1)
    assert out["p"] == pytest.approx(1.0)


def test_the_null_relabels_within_blocks_not_across_them():
    """A between-block null would treat (size, seed) variation as signal. Two
    blocks with opposite trends must cancel, not reinforce."""
    up = {d: (d - 0.25) for d in a.DENSITIES}
    down = {d: -(d - 0.25) for d in a.DENSITIES}
    out = a.slope_and_p([up, down] * 5, n_draw=2000, seed=1)
    assert out["slope"] == pytest.approx(0.0)
    assert out["p"] > 0.5


def test_slope_is_deterministic_under_a_fixed_seed():
    kw = dict(n_draw=500, seed=7)
    assert a.slope_and_p(rising(0.02), **kw) == a.slope_and_p(rising(0.02), **kw)


def test_slope_refuses_a_block_missing_a_density():
    bad = rising(0.10)
    del bad[3][0.65]
    with pytest.raises(ValueError, match="0.65"):
        a.slope_and_p(bad, n_draw=100, seed=1)


def test_slope_reports_the_number_of_live_blocks():
    """2c's epitaph: the power table assumed 16 blocks where 7 were live. The
    count that entered the test is reported, never inferred."""
    assert a.slope_and_p(rising(0.10), n_draw=100, seed=1)["n_blocks"] == 10


# ------------------------------------------------------ verdict tree order

def test_stage_a_failure_precedes_everything():
    out = a.verdict(stage_a(passed=False), sweep_cells(depth=0.10),
                    below_silent=True, n_draw=500, seed=1)
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "stage a" in out["reason"].lower()


def test_the_below_row_consistency_check_precedes_the_slope_test():
    """The sweep brackets the scored lubana_below row at 0.50 p_c. If the new
    measure implies structure where the closed 1b record found none, the
    measure is wrong — not the closed record."""
    out = a.verdict(stage_a(), sweep_cells(depth=0.10),
                    below_silent=False, n_draw=500, seed=1)
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "0.50" in out["reason"] or "consistency" in out["reason"].lower()


def test_attrition_below_eight_live_blocks_is_insufficient_data():
    cells = [c for c in sweep_cells(depth=0.10)
             if not (c["size_bucket"] == "10M" and c["seed"] in (102, 103, 104))]
    out = a.verdict(stage_a(), cells, below_silent=True, n_draw=500, seed=1)
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "block" in out["reason"].lower()


def test_exactly_eight_live_blocks_still_adjudicates():
    """The floor is FEWER than 8, per design §5. An off-by-one here would
    silently convert a reportable result into INSUFFICIENT_DATA."""
    cells = [c for c in sweep_cells(depth=0.10)
             if not (c["size_bucket"] == "10M" and c["seed"] in (103, 104))]
    out = a.verdict(stage_a(), cells, below_silent=True, n_draw=2000, seed=1)
    assert out["verdict"] == "PASS"


def test_a_block_missing_one_density_is_not_live():
    """A partial block cannot enter a within-block relabeling null."""
    cells = [c for c in sweep_cells(depth=0.10)
             if not (c["size_bucket"] == "10M" and c["density"] == 0.65)]
    out = a.verdict(stage_a(), cells, below_silent=True, n_draw=500, seed=1)
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert out["n_blocks"] == 5


def test_a_significant_positive_slope_passes():
    out = a.verdict(stage_a(), sweep_cells(depth=0.10), below_silent=True,
                    n_draw=2000, seed=1)
    assert out["verdict"] == "PASS"


def test_a_null_slope_fails():
    out = a.verdict(stage_a(), sweep_cells(depth=0.0), below_silent=True,
                    n_draw=2000, seed=1)
    assert out["verdict"] == "FAIL"


# ------------------------------------------- the frozen prediction's variants

def test_layer_zero_leakage_is_a_named_fail_with_its_mechanism_confirmed():
    """Michael's frozen prediction: depth null, L0 fires, L tracks pool size."""
    out = a.verdict(stage_a(), sweep_cells(cls="L0-only", l0=0.08, depth=0.0),
                    below_silent=True, natural_l0_tracks_pool=True,
                    n_draw=2000, seed=1)
    assert out["verdict"] == "FAIL"
    assert out["variant"] == "layer-0 leakage"


def test_layer_zero_without_the_pool_mechanism_is_a_distinct_result():
    out = a.verdict(stage_a(), sweep_cells(cls="L0-only", l0=0.08, depth=0.0),
                    below_silent=True, natural_l0_tracks_pool=False,
                    n_draw=2000, seed=1)
    assert out["verdict"] == "FAIL"
    assert out["variant"] == "layer-0, mechanism unconfirmed"


def test_a_plain_null_is_not_labelled_a_layer_zero_result():
    out = a.verdict(stage_a(), sweep_cells(cls="silent", l0=0.0, depth=0.0),
                    below_silent=True, n_draw=2000, seed=1)
    assert out["variant"] is None


def test_the_per_cell_table_is_reported_whatever_the_slope_returns():
    """1b's closeout lesson: a pooled statistic hid that 10/10 was really
    9/10. The per-cell classification ships with every verdict."""
    out = a.verdict(stage_a(), sweep_cells(cls="L0-only", l0=0.08),
                    below_silent=True, n_draw=500, seed=1)
    assert sum(out["classes"].values()) == 40
    assert out["classes"]["L0-only"] == 40
    assert set(out["classes_by_density"]) == set(a.DENSITIES)


def test_the_diagnostic_arm_cannot_touch_the_verdict():
    """Design §4 marks the natural-n arm verdict_touching: False. A pool
    mechanism must not turn a null slope into a PASS."""
    out = a.verdict(stage_a(), sweep_cells(depth=0.0), below_silent=True,
                    natural_l0_tracks_pool=True, n_draw=2000, seed=1)
    assert out["verdict"] == "FAIL"
    assert out["natural_arm_verdict_touching"] is False
