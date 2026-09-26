import math

import numpy as np
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5 import stats_5 as ss
from experiments.exp5b import battery_5b as b5b
from experiments.exp5b import stats_5b as st

FLOORS = bg.load_floors()


def _cell5(*, f, lo, hi, bm, bp, small="1b", large="2.8b", rung="antonym"):
    reads = {"lo": lo, "hi": hi, "a": (lo + hi) / 2, "b_minus": sum(bm) / 2, "b_plus": sum(bp) / 2,
             "raw": {"lo": lo, "hi": hi, "b_minus": list(bm), "b_plus": list(bp)}}
    c = ss.cell_5(f=f, reads=reads, floor=FLOORS[rung])
    c.update({"small": small, "large": large, "rung": rung, "family": b5.FAMILY_OF[rung],
              "type": b5.RUNG_TYPE_5[rung], "bracket": [30000, 31000], "b_minus_steps": [28000, 29000],
              "b_plus_steps": [32000, 33000], "residual_lo": 0.001, "residual_hi": 0.002})
    return c


def _small(f_B, members):
    return {"f_B": f_B, "members": {142000: members[0], 141000: members[1], 140000: members[2]}}


def test_small_reads_from_a_side_counts_table():
    counts = {143000: {"antonym": 100}, 142000: {"antonym": 90}, 140000: {"antonym": 95}}
    r = st.small_reads_5b(counts, "antonym")
    assert r == {"f_B": 100, "members": {142000: 90, 140000: 95}}   # 141000 absent → not a member


def test_placebo_terms_six_combinations_at_weight_one_over_sqrt2():
    c5 = _cell5(f=100, lo=120, hi=130, bm=(100, 110), bp=(140, 150))   # a=125, b-=105, b+=145
    small = _small(100, (96, 104, 100))
    terms = st.placebo_terms_5b(c5, small)
    assert len(terms) == 6
    # (a - b-) = 20 with (f_B - n) ∈ {4, -4, 0} → |24|,|16|,|20| /√2 ; (a - b+) = -20 → |-16|,|-24|,|-20| /√2
    want = sorted([24, 16, 20, 16, 24, 20])
    assert sorted(round(t * math.sqrt(2)) for t in terms) == want
    minus = st.placebo_terms_5b(c5, small, sign=-1)
    assert sorted(round(t * math.sqrt(2)) for t in minus) == want   # symmetric members here
    c5_one_side = _cell5(f=100, lo=120, hi=130, bm=(100, 110), bp=(140, 150))
    c5_one_side["b_plus"] = None
    assert len(st.placebo_terms_5b(c5_one_side, small)) == 3


def test_noiseless_small_side_reduces_to_P_over_sqrt2():
    """Design §2: with n_j = f_B for every member, M = P/√2 exactly."""
    c5 = _cell5(f=100, lo=120, hi=130, bm=(100, 110), bp=(140, 150))
    cell = st.cell_5b(c5, _small(100, (100, 100, 100)), FLOORS["antonym"])
    assert abs(cell["M"] - c5["P"] / math.sqrt(2)) < 1e-12
    assert cell["Q"] == 0.0 and cell["defined_M"] and cell["n_terms"] == 6
    assert abs(cell["c_sym"] - (c5["R"] - c5["P"] / math.sqrt(2)) / 500) < 1e-12
    assert cell["c_exp5"] == c5["c"] and cell["R"] == c5["R"] and cell["P"] == c5["P"]


def test_between_size_offset_enters_R_and_cancels_in_M():
    """Design §3.2: adding Δ to every large-side read moves R by Δ and leaves M unchanged."""
    base = _cell5(f=100, lo=120, hi=130, bm=(100, 110), bp=(140, 150))
    shifted = _cell5(f=100, lo=170, hi=180, bm=(150, 160), bp=(190, 200))
    small = _small(100, (96, 104, 100))
    a, b = st.cell_5b(base, small, FLOORS["antonym"]), st.cell_5b(shifted, small, FLOORS["antonym"])
    assert abs(a["M"] - b["M"]) < 1e-12 and abs(b["R"] - a["R"] - 50) < 1e-12


def test_cell_5b_sensitivity_forms_and_small_side_fields():
    c5 = _cell5(f=100, lo=120, hi=130, bm=(100, 110), bp=(140, 150))
    cell = st.cell_5b(c5, _small(100, (90, 110, 100)), FLOORS["antonym"])
    assert cell["Q"] == pytest.approx(20 / 3)
    assert cell["c_naive"] == pytest.approx((c5["R"] - 0.5 * (c5["P"] + 20 / 3)) / 500)
    assert cell["c_max"] == pytest.approx((c5["R"] - max(c5["P"], 20 / 3)) / 500)
    assert cell["c_minus"] == pytest.approx((c5["R"] - cell["M_minus"]) / 500)
    assert cell["small_reads"] == [100, 90, 110, 100]
    assert cell["small_sd"] == pytest.approx(float(np.std([100, 90, 110, 100], ddof=1)))
    assert cell["members"] == {"142000": 90, "141000": 110, "140000": 100}
    assert isinstance(cell["R_gt_M"], bool) and len(cell["small_clears"]) == 4


def test_cell_with_no_member_has_no_M_and_is_excluded_from_the_primary():
    c5 = _cell5(f=100, lo=120, hi=130, bm=(100, 110), bp=(140, 150))
    cell = st.cell_5b(c5, {"f_B": 100, "members": {}}, FLOORS["antonym"])
    assert cell["M"] is None and cell["c_sym"] is None and not cell["defined_M"] and cell["Q"] is None
    assert st.analysed_5b([cell]) == []


def _cells_for_flip(k_rungs=9, per_rung=3, offset=30, seed=0):
    rng = np.random.default_rng(seed)
    rungs = list(b5.RUNGS)[:k_rungs]
    out = []
    for r in rungs:
        for i in range(per_rung):
            f = 100 + int(rng.integers(0, 50))
            lo, hi = f + offset + int(rng.integers(-5, 6)), f + offset + int(rng.integers(-5, 6))
            c5 = _cell5(f=f, lo=lo, hi=hi, bm=(lo - 3, lo + 3), bp=(hi - 2, hi + 4), rung=r,
                        small="1b", large=("2.8b", "6.9b", "12b")[i])
            out.append(st.cell_5b(c5, _small(f, (f + 2, f - 3, f + 1)), FLOORS[r]))
    return out


def test_primary_uses_exp5_sign_flip_on_the_chosen_key():
    cells = _cells_for_flip()
    p = st.primary_5b(cells, key="c_sym", n_sample=100, seed=0)
    assert p["key"] == "c_sym" and p["n_cells"] == 27 and p["n_rungs"] == 9
    assert p["T"] == pytest.approx(float(np.mean([c["c_sym"] for c in cells])))
    assert p["rung_block"]["method"] == "enumerated" and p["rung_block"]["n_perms"] == 2 ** 9
    assert p["n_nonzero_blocks"] == 9 and p["p_min_attainable"] == 2 ** -9
    assert p["rung_block"]["p"] == ss.sign_flip_p_5(list(p["per_rung_sum"].values()), 27)["p"]
    q = st.primary_5b(cells, key="c_naive", n_sample=100, seed=0)
    assert q["key"] == "c_naive" and q["T"] != p["T"]


def test_sigma_hat_pooled_is_rms_of_per_cell_sample_sd():
    cells = _cells_for_flip()
    s = st.sigma_hat_5b(cells)
    want = math.sqrt(np.mean([c["small_sd"] ** 2 for c in cells]))
    assert s["pooled"] == pytest.approx(want) and s["n_cells"] == 27 and set(s["per_side"]) == {"1b"}


def _power_rec(axis=(5.2, 10.1, 15.1, 20.1, 30.0, 45.2), alpha=(.01, .012, .01, .011, .02, .03),
               null=(-.001, -.0008, -.0003, .0002, .001, .002)):
    return {"sigma_hat_axis": list(axis), "alpha_5b_axis": list(alpha), "null_mean_5b_axis": list(null),
            "alpha_exp5_axis": [.01, .03, .3, .7, .95, 1.0], "null_mean_exp5_axis": [-.007, -.004, .001, .006, .02, .04],
            "alpha_naive_axis": [.02, .01, .01, .015, .2, .9], "null_mean_naive_axis": [.001, 0, -.001, .001, .004, .010]}


def test_calibration_read_edges():
    rec = _power_rec()
    at_knot = st.calibration_read_5b(rec, 15.1, T_sym=0.03)
    assert at_knot["in_grid"] and not at_knot["below_grid"] and at_knot["alpha_realized"] == pytest.approx(.01)
    assert at_knot["null_mean_T"] == pytest.approx(-.0003) and at_knot["T_star"] == pytest.approx(0.0303)
    assert at_knot["cell"] == "CALIBRATED"
    between = st.calibration_read_5b(rec, 12.6, T_sym=0.03)      # halfway 10.1→15.1: α .011, null -.00055
    assert between["alpha_realized"] == pytest.approx(.011) and between["null_mean_T"] == pytest.approx(-.00055)
    below = st.calibration_read_5b(rec, 2.0, T_sym=0.03)
    assert below["in_grid"] and below["below_grid"] and below["alpha_realized"] == pytest.approx(.01)
    above = st.calibration_read_5b(rec, 60.0, T_sym=0.03)
    assert not above["in_grid"] and above["cell"] == "OFF-GRID"
    assert above["alpha_realized"] == pytest.approx(.03) and above["null_mean_T"] == pytest.approx(.002)
    inflated = st.calibration_read_5b(_power_rec(alpha=(.2,) * 6), 15.1, T_sym=0.03)
    assert inflated["cell"] == "INFLATED"
    exactly_alpha = st.calibration_read_5b(_power_rec(alpha=(.05,) * 6), 15.1, T_sym=0.03)
    assert exactly_alpha["cell"] == "INFLATED"                       # the rule is α < .05


def _prim(T, p, n=30, k=9):
    return {"T": T, "n_cells": n, "n_nonzero_blocks": k, "rung_block": {"p": p}}


def test_tree_every_cell():
    cal_ok = {"cell": "CALIBRATED"}
    assert st.tree_5b(failures=["5b x"], primary=_prim(.05, .001), calibration=cal_ok)["verdict"] == "INSUFFICIENT_DATA"
    assert st.tree_5b(failures=[], primary=_prim(.05, .001, n=19), calibration=cal_ok)["verdict"] == "UNDETERMINED"
    assert st.tree_5b(failures=[], primary=_prim(.05, .001, k=6), calibration=cal_ok)["verdict"] == "UNDETERMINED"
    t = st.tree_5b(failures=[], primary=_prim(.05, .001), calibration=cal_ok)
    assert (t["verdict"], t["cell"]) == ("SURVIVES", "CALIBRATED")
    t = st.tree_5b(failures=[], primary=_prim(.05, .001), calibration={"cell": "OFF-GRID"})
    assert (t["verdict"], t["cell"]) == ("SURVIVES", "OFF-GRID")
    t = st.tree_5b(failures=[], primary=_prim(.01, .0099), calibration={"cell": "INFLATED"})
    assert (t["verdict"], t["cell"]) == ("SURVIVES", "INFLATED")     # the bar is ≥ .01, α is < .01
    t = st.tree_5b(failures=[], primary=_prim(.004, .2), calibration=cal_ok)
    assert (t["verdict"], t["cell"]) == ("NOT-SURVIVED", "INSIDE")
    t = st.tree_5b(failures=[], primary=_prim(.004, .001), calibration=cal_ok)
    assert (t["verdict"], t["cell"]) == ("NOT-SURVIVED", "SIGN-ONLY")
    t = st.tree_5b(failures=[], primary=_prim(.02, .3), calibration=cal_ok)
    assert (t["verdict"], t["cell"]) == ("NOT-SURVIVED", "SIZE-ONLY")
    t = st.tree_5b(failures=[], primary=_prim(.0099, .001), calibration=cal_ok)
    assert t["cell"] == "SIGN-ONLY"
    t = st.tree_5b(failures=[], primary=_prim(.02, .01), calibration=cal_ok)
    assert t["cell"] == "SIZE-ONLY"                                   # p == α is not < α


def test_modifier_5b_selects_on_R_gt_M():
    cells = _cells_for_flip(offset=40)
    m = st.modifier_5b(cells)
    assert set(m) >= {"modifier", "n", "n_pos", "n_neg"} and m["n"] == sum(1 for c in cells if c["R_gt_M"])
    assert m["modifier"] == "LARGE-AHEAD"          # every simulated cell is large-ahead by 40


def test_secondaries_pure_parts():
    cells = _cells_for_flip() + [st.cell_5b(_cell5(f=200, lo=205, hi=206, bm=(200, 201), bp=(210, 211),
                                                    small="2.8b", large="12b", rung="sub3_mid"),
                                             _small(200, (199, 201, 200)), FLOORS["sub3_mid"])]
    s1 = st.s1_rows_5b(cells, n_sample=100, seed=0)
    assert set(s1["by_row"]) == {"1b", "2.8b"} and s1["outside_2p8b"]["n_cells"] == 27
    assert "p" in s1["outside_2p8b"] and s1["referents"] == b5b.EXP5_REFERENTS_5B
    s2 = st.s2_swaps_5b(cells, n_sample=100, seed=0)
    assert set(s2["targets"]) == {"f_B", "142000", "141000", "140000"}
    for k, v in s2["targets"].items():
        assert set(v) >= {"T", "p", "n_cells"}
    assert set(s2["designations"]) == {"142000", "141000", "140000"}
    s6 = st.s6_ledger_5b(cells)
    assert 0 <= s6["fraction_small_status_constant"] <= 1 and "named" in s6
    s7 = st.s7_by_type_5b(cells, n_sample=100, seed=0)
    assert set(s7) == {"arithmetic", "option", "string"} and s7["option"]["p"] is None  # 2 option rungs < 5
    s11 = {"1b": {r: {"s11": 100, "final": 100, "diff": 0} for r in b5.RUNGS},
           "2.8b": {r: {"s11": 200, "final": 200, "diff": 0} for r in b5.RUNGS}}
    s8 = st.s8_one_member_5b(cells, s11, n_sample=100, seed=0)
    assert set(s8) >= {"T1", "p1", "n_cells", "T_sym_minus_T1"}
    s9 = st.s9_spike_5b(cells, n_sample=100, seed=0)
    assert s9["n_cells"] == 27 and s9["excluded_pair"] == ["2.8b", "12b"]
    s10 = st.s10_forms_5b(cells, n_sample=100, seed=0)
    assert set(s10) == {"c_naive", "c_max", "c_minus"} and all("p" in v for v in s10.values())
    dead = [dict(_cell5(f=0, lo=0, hi=0, bm=(0, 0), bp=(0, 0), rung="caesar"), live=False, defined_P=True)]
    counts = {"1b": {143000: {"caesar": 0}, 142000: {"caesar": 400}, 141000: {"caesar": 0}, 140000: {"caesar": 0}}}
    s12 = st.s12_newly_live_5b(dead, counts, FLOORS)
    assert s12["n"] == 1 and s12["cells"][0]["rung"] == "caesar"
