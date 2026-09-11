# experiments/exp4/tests/test_analyze_4.py
"""Pure-function tests for `analyze_4.py` (Task 4 brief Step 1) plus
the eligibility bootstrap, `per_item_alignment_4`'s cross-check, and
the S2 known-answer gate. No torch, no network, no model contact."""
from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp4 import analyze_4 as an
from experiments.exp4 import battery_4
from experiments.exp4 import collect_4
from experiments.exp4 import metric_4


# ----------------------------------------------------------- brief Step 1

def test_excess_is_zero_at_t1_and_trend_subtracts():
    steps = [1, 2, 3, 4]
    a = {"r": [0.10, 0.20, 0.30, 0.40], "f1": [0.10, 0.15, 0.20, 0.25], "f2": [0.10, 0.15, 0.20, 0.25]}
    tr = an.trend_4(a, ["f1", "f2"], steps)
    assert tr == pytest.approx([0.10, 0.15, 0.20, 0.25])
    x = an.excess_4(a, tr, steps)
    assert x["r"] == pytest.approx([0.0, 0.05, 0.10, 0.15]) and x["r"][0] == 0.0


def test_phi_reads_the_last_point_before_the_clear():
    x = [0.0, 0.05, 0.10, 0.15]
    assert an.phi_4(x, 3) == pytest.approx(0.10 / 0.15)      # t_clear at index 3 -> t- index 2
    assert an.phi_4(x, 2) == pytest.approx(0.05 / 0.15)
    assert an.phi_4(x, 1) is None and an.phi_4(x, 0) is None   # no window
    assert an.phi_4([0.0, 0.0, 0.0, 0.0], 3) is None            # no endpoint excess


def test_primary_exact_flips_and_bars():
    cells = [{"traj": "a", "rung": f"r{i}", "phi": 0.6} for i in range(6)] + \
            [{"traj": "b", "rung": f"r{i}", "phi": 0.5} for i in range(6)]
    p = an.primary_4(cells, n_boot=200, seed=0)
    assert p["flip_method"] == "exact" and p["n_flips"] == 2 ** 6 and p["n_rungs"] == 6 and p["n_cells"] == 12
    assert p["T"] == pytest.approx(0.55) and p["p_plus"] == pytest.approx(1 / 64) and p["p_minus"] == 1.0
    # every bootstrap resample of this degenerate case reduces to the
    # identical multiset {0.6, 0.5} x 6, so ci95 collapses to a point
    # at T -- float64 arithmetic lands it at 0.5499999999999999, not
    # the literal 0.55, so the containment check carries a ULP-scale
    # tolerance (primary_4's own arithmetic, unmodified: T itself is
    # asserted above only via pytest.approx for the same reason)
    assert p["ci95"][0] <= 0.55 + 1e-9 and 0.55 - 1e-9 <= p["ci95"][1]
    v = an.verdict_tree_4([], 12, 6, dict(p, p_plus=0.005))
    assert v["verdict"] == "LEADS"


def test_tree_cells():
    base = {"T": 0.3, "p_plus": 0.004, "p_minus": 1.0, "ci95": [0.1, 0.5]}
    assert an.verdict_tree_4([], 5, 4, base)["verdict"] == "LEADS"
    assert an.verdict_tree_4([], 5, 4, dict(base, T=0.15, ci95=[0.05, 0.24]))["verdict"] == "PARTIAL"
    assert an.verdict_tree_4([], 5, 4, dict(base, T=0.02, p_plus=0.4, ci95=[-0.05, 0.10]))["verdict"] == "FOLLOWS"
    assert an.verdict_tree_4([], 5, 4, dict(base, T=0.15, p_plus=0.2, ci95=[-0.1, 0.4]))["verdict"] == "UNDETERMINED"
    assert an.verdict_tree_4([], 2, 2, base)["verdict"] == "NO-CONVERGENCE"
    assert an.verdict_tree_4([], 5, 2, base)["verdict"] == "NO-CONVERGENCE"
    assert an.verdict_tree_4(["4 something"], 5, 4, base)["verdict"] == "INSUFFICIENT_DATA"


def test_sign_flip_sampled_above_the_enumeration_cap():
    cells = [{"traj": "a", "rung": f"r{i}", "phi": 0.3 + 0.01 * i} for i in range(25)]
    p = an.primary_4(cells, n_boot=100, seed=0)
    assert p["flip_method"] == "sampled" and p["n_flips"] == an.N_FLIP_SAMPLE_4


# ------------------------------------------------------------- RUNG_TYPE_4

def test_rung_type_4_covers_the_34_rungs_exactly():
    assert set(an.RUNG_TYPE_4) == set(bt.RUNGS)
    counts = {}
    for typ in an.RUNG_TYPE_4.values():
        counts[typ] = counts.get(typ, 0) + 1
    assert counts == {"arithmetic": 25, "option": 4, "string": 5}


# ------------------------------------------------------- per_item_alignment_4

def _two_site_pair():
    """A tiny hand-built (sets_m, sets_q, pairing) triple: 2 sites, 3
    items, k=2 out of n=4 (padded to n=4 so overlap counts are
    non-trivial)."""
    sets_m = np.array([
        [[0, 1], [1, 2], [2, 3]],   # site 0: item i's neighbours
        [[3, 0], [0, 1], [1, 2]],   # site 1
    ], dtype=np.uint16)
    sets_q = np.array([
        [[0, 1], [1, 3], [2, 3]],   # site 0 (matches m's site 0 partially)
        [[3, 1], [0, 2], [1, 2]],   # site 1
    ], dtype=np.uint16)
    pairing = [0, 1]
    return sets_m, sets_q, pairing


def test_per_item_alignment_4_equals_metric_4_on_a_two_site_pair():
    sets_m, sets_q, pairing = _two_site_pair()
    tables_m = {"sets": {r: sets_m for r in battery_4.RUNGS}, "overlaps": {}}
    ref_tables = {"refX": {r: sets_q for r in battery_4.RUNGS}}
    pairing_by_ref = {"refX": pairing}
    out = an.per_item_alignment_4(tables_m, ref_tables, pairing_by_ref)
    expect_site0 = metric_4.overlap_counts(sets_m[0], sets_q[0]).astype(np.float64) / metric_4.K_4
    expect_site1 = metric_4.overlap_counts(sets_m[1], sets_q[1]).astype(np.float64) / metric_4.K_4
    expect = np.mean(np.stack([expect_site0, expect_site1]), axis=0)
    for r in battery_4.RUNGS:
        assert out[r] == pytest.approx(expect)


def test_per_item_alignment_4_refuses_a_disagreeing_stored_overlap():
    sets_m, sets_q, pairing = _two_site_pair()
    real_overlap = metric_4.overlap_counts(sets_m[0], sets_q[0])
    tampered = real_overlap.copy()
    tampered[0] = (tampered[0] + 1) % (metric_4.K_4 + 1)
    stale = np.stack([tampered, metric_4.overlap_counts(sets_m[1], sets_q[1])])
    tables_m = {"sets": {r: sets_m for r in battery_4.RUNGS},
               "overlaps": {"refX": {r: stale for r in battery_4.RUNGS}}}
    ref_tables = {"refX": {r: sets_q for r in battery_4.RUNGS}}
    pairing_by_ref = {"refX": pairing}
    with pytest.raises(ValueError, match="stored overlap disagrees"):
        an.per_item_alignment_4(tables_m, ref_tables, pairing_by_ref)


# ------------------------------------------------------------- eligibility

def _synthetic_reference_tree_leads(tmp_path):
    """A tiny synthetic reference-stage-only tree (Task 4's own world
    generator, mode='leads', restricted to stage 1) so
    `eligibility_table_4` can be exercised without a full sweep."""
    from experiments.exp4.tests import full_shape as fs
    fs.build_world(tmp_path, "leads", seed=1, stage="reference_only")
    return tmp_path


@pytest.mark.slow
def test_eligibility_table_4_on_a_synthetic_reference_tree(tmp_path):
    root = _synthetic_reference_tree_leads(tmp_path)
    table = an.eligibility_table_4(root, n_boot=200, seed=0)
    for traj in battery_4.TRAJECTORIES_4:
        block = table[traj]
        from experiments.exp2g import battery_2g as bg
        outcome = battery_4.load_outcome_4(traj)
        rs = battery_4.rung_sets_4(outcome, bg.load_floors())
        assert set(block["R"]) == set(rs["R"])
        assert set(block["flat"]) == set(rs["flat"])
        for rung, e in block["R"].items():
            if e["eligible"]:
                assert e["x_end"] >= an.SE_MULTIPLE_4 * e["se"] - 1e-9
                assert e["t_clear_index"] is None or e["t_clear_index"] >= an.MIN_CLEAR_INDEX_4
            else:
                assert e["reason"] in ("endpoint excess below 2 SE",
                                      "no pre-clear window (t_clear at grid index < 2)")


# -------------------------------------------------------- S2 known-answer

def test_s2_known_answer_gates_4_reproduces_2d_and_2e():
    out = an.s2_known_answer_gates_4()
    assert abs(out["auc_2d"] - 0.5454545454545454) < 1e-12
    assert abs(out["auc_2e"] - 0.6126482213438735) < 1e-12
    assert out["no_alpha_claim"] is True
