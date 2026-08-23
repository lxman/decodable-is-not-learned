# experiments/exp2g/tests/test_battery_2g.py
"""battery_2g: every literal re-asserted against the committed trees."""
import json

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg


def test_rung_sets_are_the_docs():
    assert bg.R_28 == ("antonym", "antonym6", "add_base8", "sub_base8",
                       "add3_mid", "sub3_mid", "arith_next")
    assert bg.R_12B == ("antonym", "antonym6", "add_base8", "sub_base8",
                        "add3_mid", "sub4_mid", "median5", "arith_next",
                        "count_div13")
    assert len(bg.PREDICTOR_RUNGS) == 11
    assert set(bg.R_28) | set(bg.R_12B) | {"odd6"} == set(bg.PREDICTOR_RUNGS)
    assert bg.sweep_rungs("2.8b") == tuple(bt.RUNGS)
    assert bg.sweep_rungs("12b") == bg.PREDICTOR_RUNGS


def test_grid_is_finding_b():
    assert bg.GRID["2.8b"][0] == 0 and bg.GRID["2.8b"][-1] == 143000
    assert 64000 not in bg.GRID["2.8b"] and 64000 in bg.EXCLUDED_GRID["2.8b"]
    assert bg.n_trained("2.8b") == 21 and bg.n_trained("12b") == 8
    assert bg.trained_steps("12b") == (1000, 4000, 16000, 32000, 64000,
                                       100000, 130000, 143000)
    assert bg.revision_of(143000) == "main" and bg.revision_of(1000) == "step1000"


def test_m4_counts_and_rung_sets_reproduce():
    floors = bg.load_floors()
    assert len(floors) == 34 and floors["antonym"] == 0.25
    c28 = bg.load_m4_counts("2.8b")
    assert c28 == bg.FINAL_COUNT_PIN["2.8b"] and len(c28) == 34
    c12 = bg.load_m4_counts("12b")
    assert c12 == bg.FINAL_COUNT_PIN["12b"] and len(c12) == 11
    assert bg.check_rung_sets(floors) == {"2.8b": list(bg.R_28),
                                         "12b": list(bg.R_12B)}
    assert all(c28[r] >= bg.ELIGIBILITY_MIN_POS for r in bg.R_28)
    assert c12["sub4_mid"] < bg.ELIGIBILITY_MIN_POS


def test_frozen_imports_and_digest_lists():
    bg.check_frozen_imports_2g()
    assert len(bg.FROZEN_IMPORT_SHA256_2G) == 14


@pytest.mark.parametrize("size", bg.PROBE_SIZES)
@pytest.mark.parametrize("mode", bg.MODES)
def test_probe_npz_pins(size, mode):
    for rung in bg.PREDICTOR_RUNGS:
        p = bg.probe_npz_path(size, mode, rung)
        assert bg.sha256_file(p) == bg.PROBE_NPZ_SHA_PIN[(rung, size, mode)]
        exp = "exp2b" if rung in bt.REUSED else "exp2c"
        txt = (bt.EXP2B if exp == "exp2b" else bt.EXP2C) / "results" / \
            "activations_sha256.txt"
        assert f"{bg.PROBE_NPZ_SHA_PIN[(rung, size, mode)]}  activations/" \
               f"{size}_{mode}/{rung}.npz" in txt.read_text()


def test_load_probe_acts_pins_labels():
    cap = bt.load_item_file("sub_base8")
    act, y, meta = bg.load_probe_acts(
        bg.probe_npz_path("1b", "trained", "sub_base8"), cap,
        sha_pin=bg.PROBE_NPZ_SHA_PIN[("sub_base8", "1b", "trained")])
    assert len(y) == 1000 and len(act) == 14      # 1b family
    assert y == [str(it["probe_label"]) for it in cap["probe_items"]]
    with pytest.raises(ValueError):
        bg.load_probe_acts(bg.probe_npz_path("1b", "trained", "sub_base8"),
                           cap, sha_pin="0" * 64)


def test_paths(tmp_path):
    assert bg.record_path(tmp_path, "2.8b", 1000, "antonym") == \
        tmp_path / "results" / "sweep" / "2.8b" / "step1000" / "antonym.json"
    assert bg.gate1_path(tmp_path, "12b").name == "gate1.json"
    assert bg.halt_marker_path(tmp_path, "2.8b").name == "HALTED"
    assert bg.predictor_path(tmp_path).name == "predictor.json"
