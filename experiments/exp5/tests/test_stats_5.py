# experiments/exp5/tests/test_stats_5.py
import math

import numpy as np
import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp5 import battery_5 as b5
from experiments.exp5 import stats_5 as ss

FLOOR = 0.026     # antonym's


def _plan(lo=50000, hi=51000, bm=(48000, 49000), bp=(52000, 53000)):
    return {"status": "done", "bracket": [lo, hi], "b_minus": list(bm), "b_plus": list(bp),
            "residual_lo": 0.01, "residual_hi": 0.02}


def _counts(**by_step):
    return {s: {"antonym": c} for s, c in by_step.items()}


def test_reads_take_means_and_keep_raw_counts():
    counts = {50000: {"antonym": 100}, 51000: {"antonym": 110}, 48000: {"antonym": 90},
              49000: {"antonym": 95}, 52000: {"antonym": 120}, 53000: {"antonym": 130}}
    r = ss.reads_5(counts, _plan(), "antonym")
    assert r["a"] == 105 and r["b_minus"] == 92.5 and r["b_plus"] == 125
    assert r["raw"] == {"lo": 100, "hi": 110, "b_minus": [90, 95], "b_plus": [120, 130]}


def test_reads_edge_sides_are_none():
    counts = {50000: {"antonym": 100}, 51000: {"antonym": 110}, 52000: {"antonym": 120}}
    r = ss.reads_5(counts, _plan(bm=(), bp=(52000,)), "antonym")
    assert r["b_minus"] is None and r["b_plus"] == 120


def test_cell_statistic_and_classes():
    reads = {"a": 105, "b_minus": 92.5, "b_plus": 125, "lo": 100, "hi": 110,
             "raw": {"lo": 100, "hi": 110, "b_minus": [90, 95], "b_plus": [120, 130]}}
    c = ss.cell_5(f=50, reads=reads, floor=FLOOR)
    assert c["live"] and c["defined_P"]
    assert c["R"] == 55 and c["P"] == (12.5 + 20) / 2 and math.isclose(c["c"], (55 - 16.25) / 500)
    assert c["signed"] == 55 / 500 and c["R_gt_P"]
    assert c["class"] == "CONCORDANT" and c["sigma"] and c["lambda_lo"] and c["lambda_hi"]
    l = ss.cell_5(f=5, reads=reads, floor=FLOOR)
    assert l["class"] == "L-AHEAD" and l["b_minus_clears_both"]
    s = ss.cell_5(f=200, reads={**reads, "a": 4, "lo": 3, "hi": 5,
                                "raw": {"lo": 3, "hi": 5, "b_minus": [2, 2], "b_plus": [3, 3]},
                                "b_minus": 2, "b_plus": 3}, floor=FLOOR)
    assert s["class"] == "S-AHEAD"
    u = ss.cell_5(f=5, reads={**reads, "lo": 5, "hi": 110, "a": 57.5,
                              "raw": {"lo": 5, "hi": 110, "b_minus": [90, 95], "b_plus": [120, 130]}},
                  floor=FLOOR)
    assert u["class"] == "UNSTABLE"
    dead = ss.cell_5(f=2, reads={"a": 2, "b_minus": 2, "b_plus": 2, "lo": 2, "hi": 2,
                                 "raw": {"lo": 2, "hi": 2, "b_minus": [2, 2], "b_plus": [2, 2]}},
                     floor=FLOOR)
    assert not dead["live"]
    placebo = ss.cell_5(f=2, reads={"a": 2, "b_minus": 2, "b_plus": 60, "lo": 2, "hi": 2,
                                    "raw": {"lo": 2, "hi": 2, "b_minus": [2, 2], "b_plus": [60, 60]}},
                        floor=FLOOR)
    assert placebo["live"] and placebo["class"] == "PLACEBO-ONLY"
    nop = ss.cell_5(f=50, reads={"a": 105, "b_minus": None, "b_plus": None, "lo": 100, "hi": 110,
                                 "raw": {"lo": 100, "hi": 110, "b_minus": [], "b_plus": []}}, floor=FLOOR)
    assert nop["live"] and not nop["defined_P"] and nop["c"] is None


def test_sign_flip_exact_enumeration_and_symmetry():
    out = ss.sign_flip_p_5([0.02, 0.03, -0.01, 0.0], n_cells=10, max_enumerate=20, n_sample=10, seed=0)
    assert out["method"] == "enumerated" and out["n_blocks"] == 3 and out["n_perms"] == 8
    assert math.isclose(out["T"], 0.004)
    # signings ≥ T: +++ (.004), ++- (.006), so p = 2/8
    assert math.isclose(out["p"], 2 / 8) and math.isclose(out["resolution"], 1 / 8)
    assert abs(out["null_mean"]) < 1e-12
    deg = ss.sign_flip_p_5([0.0, 0.0], n_cells=4, max_enumerate=20, n_sample=10, seed=0)
    assert deg["method"] == "degenerate" and deg["p"] == 1.0


def test_sign_flip_sampled_above_the_guard():
    sums = [0.001 * (i + 1) for i in range(25)]
    out = ss.sign_flip_p_5(sums, n_cells=100, max_enumerate=20, n_sample=1000, seed=0)
    assert out["method"] == "sampled" and out["n_perms"] == 1000
    assert out["p"] == (1 + out["count_ge"]) / 1001
    again = ss.sign_flip_p_5(sums, n_cells=100, max_enumerate=20, n_sample=1000, seed=0)
    assert again == out


def _cells(spec):
    """spec: list of (small, large, rung, f, lo, hi, bm_pair, bp_pair)."""
    floors = {r: 0.026 for r in bt.RUNGS}
    out = []
    for small, large, rung, f, lo, hi, bm, bp in spec:
        reads = {"lo": lo, "hi": hi, "a": (lo + hi) / 2,
                 "b_minus": (sum(bm) / len(bm)) if bm else None,
                 "b_plus": (sum(bp) / len(bp)) if bp else None,
                 "raw": {"lo": lo, "hi": hi, "b_minus": list(bm), "b_plus": list(bp)}}
        c = ss.cell_5(f=f, reads=reads, floor=floors[rung])
        c.update({"small": small, "large": large, "rung": rung, "family": bt.FAMILY_OF[rung],
                  "type": b5.RUNG_TYPE_5[rung], "bracket": [1, 2], "b_minus_steps": [], "b_plus_steps": [],
                  "residual_lo": 0.0, "residual_hi": 0.0})
        out.append(c)
    return out


def test_primary_blocks_by_rung_and_prints_family_and_cell_flips():
    spec = []
    for i, rung in enumerate(("antonym", "antonym6", "arith_next", "add_base8", "sub_base8", "odd6")):
        for small in ("1b", "2.8b"):
            spec.append((small, "12b", rung, 100, 130 + i, 132 + i, (128, 131), (129, 134)))
    cells = _cells(spec)
    p = ss.primary_5(cells, n_sample=100, seed=0)
    assert p["n_cells"] == 12 and p["n_rungs"] == 6
    assert set(p["rung_block"]) >= {"p", "method", "n_blocks", "T"}
    assert p["family_block"]["n_blocks"] <= 6 and p["cell_level"]["n_blocks"] == 12
    assert math.isclose(p["T"], np.mean([c["c"] for c in cells]))
    assert p["T"] > 0 and p["rung_block"]["p"] < 0.05


def test_primary_excludes_dead_and_undefined_P_cells():
    cells = _cells([("1b", "12b", "antonym", 100, 130, 132, (128, 131), (129, 134)),
                    ("1b", "12b", "antonym6", 100, 130, 132, (), ()),          # P undefined
                    ("1b", "12b", "odd6", 2, 2, 2, (2, 2), (2, 2))])          # dead
    p = ss.primary_5(cells, n_sample=10, seed=0)
    assert p["n_cells"] == 1 and p["n_excluded_dead"] == 1 and p["n_excluded_undefined_P"] == 1


def test_modifier():
    spec = [("1b", "12b", r, 100, 140, 142, (139, 141), (140, 143)) for r in bt.RUNGS[:10]]
    m = ss.modifier_5(_cells(spec))
    assert m["modifier"] == "LARGE-AHEAD" and m["n"] == 10 and m["n_pos"] == 10
    spec = [("1b", "12b", r, 100, 60, 62, (59, 61), (60, 63)) for r in bt.RUNGS[:10]]
    assert ss.modifier_5(_cells(spec))["modifier"] == "SMALL-AHEAD"
    spec = [("1b", "12b", r, 100, (140 if i % 2 else 60), (142 if i % 2 else 62),
            (139, 141) if i % 2 else (59, 61), (140, 143) if i % 2 else (60, 63))
            for i, r in enumerate(bt.RUNGS[:10])]
    assert ss.modifier_5(_cells(spec))["modifier"] == "MIXED"
    assert ss.modifier_5(_cells(spec[:7]))["modifier"] == "THIN"
    assert ss.modifier_5([])["modifier"] == "THIN"


def test_tree_precedence():
    ok = {"n_cells": 30, "n_rungs": 6, "T": 0.02, "rung_block": {"p": 0.001}}
    assert ss.tree_5(failures=["x"], primary=ok, modifier={"modifier": "MIXED"})["verdict"] == "INSUFFICIENT_DATA"
    assert ss.tree_5(failures=[], primary={**ok, "n_cells": 19}, modifier={"modifier": "MIXED"})["verdict"] == "UNDETERMINED"
    assert ss.tree_5(failures=[], primary={**ok, "n_rungs": 4}, modifier={"modifier": "MIXED"})["verdict"] == "UNDETERMINED"
    t = ss.tree_5(failures=[], primary=ok, modifier={"modifier": "LARGE-AHEAD"})
    assert t["verdict"] == "NOT-MATCHED" and t["modifier"] == "LARGE-AHEAD"
    assert ss.tree_5(failures=[], primary={**ok, "T": 0.009}, modifier={"modifier": "LARGE-AHEAD"})["verdict"] == "MATCHED"
    assert ss.tree_5(failures=[], primary={**ok, "rung_block": {"p": 0.011}}, modifier={"modifier": "LARGE-AHEAD"})["verdict"] == "MATCHED"


def test_signed_offset_ci_and_secondaries_run():
    spec = [(s, "12b", r, 100, 130, 132, (128, 131), (129, 134))
            for r in ("antonym", "antonym6", "arith_next", "add_base8", "sub_base8", "odd6")
            for s in ("1b", "2.8b")]
    cells = _cells(spec)
    ci = ss.signed_offset_ci_5(cells, n_boot=200, seed=0)
    assert ci["ci95"][0] <= ci["mean"] <= ci["ci95"][1] and ci["n_rungs"] == 6
    s4 = ss.s4_size_ratio_5(cells, {"1b": 1.0e9, "2.8b": 2.8e9, "12b": 1.2e10})
    assert "spearman" in s4 and len(s4["per_pair"]) == 2
    s5 = ss.s5_by_type_5(cells)
    assert s5["option"]["n_rungs"] == 3 and s5["option"]["p"] is None and "reason" in s5["option"]
    assert s5["arithmetic"]["n_rungs"] == 3
    s7 = ss.s7_by_pair_5(cells)
    assert set(s7) == {"1b→12b", "2.8b→12b"}
    led = ss.ledger_5(cells)
    assert led["n_live"] == 12 and led["classes"]["CONCORDANT"] == 12
