import numpy as np
import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp5 import battery_5 as b5
from experiments.exp5 import power_5 as pw


def _finals():
    f = {s: {r: 0 for r in bt.RUNGS} for s in b5.SIZES_5}
    f["1b"]["arith_next"] = 60
    f["410m"]["antonym6"] = 111
    for r, k in (("antonym", 272), ("antonym6", 149), ("add_base8", 40), ("sub_base8", 60),
                 ("add3_mid", 43), ("sub3_mid", 264), ("arith_next", 137)):
        f["2.8b"][r] = k
    for r, k in (("antonym", 286), ("antonym6", 143), ("add_base8", 29), ("sub_base8", 52),
                 ("add3_mid", 19), ("sub3_mid", 14), ("arith_next", 58), ("count_div13", 102),
                 ("odd6", 107)):
        f["6.9b"][r] = k
    return f


def test_sigma_pin_derivation():
    assert abs(pw.SIGMA_READ_ITEMS_5 - 17.0 * np.sqrt(np.pi / 2) / np.sqrt(2)) < 1e-9
    assert pw.NOISE_FACTORS_5 == (1.0, 0.5) and pw.DRIFT_SD_ITEMS_5 == 4.0
    assert pw.OFFSET_ITEMS_5 == 25 and pw.Q_5 == 0.5 and pw.POWER_BAR_5 == 0.75


def test_live_structure_is_small_side_clears_only():
    from experiments.exp2g import battery_2g as bg
    floors = bg.load_floors()
    st = pw.live_structure_5(_finals(), floors)
    keys = {(c["small"], c["large"], c["rung"]) for c in st}
    assert ("1b", "12b", "arith_next") in keys and ("410m", "6.9b", "antonym6") in keys
    assert ("2.8b", "12b", "antonym") in keys and ("2.8b", "6.9b", "sub3_mid") in keys
    assert all(c["small"] != "12b" for c in st)
    assert not any(k[2] == "caesar" for k in keys)
    n_28 = sum(1 for c in st if c["small"] == "2.8b")
    assert n_28 == 7 * 2                                      # seven rungs × two partners


def test_simulated_battery_reads_through_the_verdicts_own_code():
    from experiments.exp2g import battery_2g as bg
    from experiments.exp5 import stats_5 as ss
    floors = bg.load_floors()
    st = pw.live_structure_5(_finals(), floors)
    rng = np.random.default_rng(0)
    cells = pw.simulate_battery_5(st, floors, offset_cells=set(), sigma=15.0, drift=4.0, rng=rng)
    assert len(cells) == len(st) and all(set(c) >= {"c", "rung", "family", "live"} for c in cells)
    p = ss.primary_5(cells, n_sample=10, seed=0)
    assert p["n_cells"] <= len(st)


def test_compute_is_deterministic_and_declares():
    from experiments.exp2g import battery_2g as bg
    floors = bg.load_floors()
    a = pw.compute(_finals(), floors, n_sim=40, seed=0)
    b = pw.compute(_finals(), floors, n_sim=40, seed=0)
    assert a == b
    assert a["declaration"] in ("POWERED", "DECLARED UNDERPOWERED IN ADVANCE")
    arms = a["arms"]
    assert set(arms) == {"null", "spread", "concentrated"}
    for arm in arms.values():
        assert set(arm) == {"1.0", "0.5"} and all(0 <= v["P_fire"] <= 1 for v in arm.values())
    assert a["deciding_arm"] == {"arm": "spread", "noise_factor": 1.0, "D": 0.05, "q": 0.5}
    assert a["min_detectable_T"] is None or a["min_detectable_T"] > 0
    assert a["n_live_simulated"] == len(pw.live_structure_5(_finals(), floors))
    assert a["realized_alpha"]["1.0"] <= 0.5


def test_main_writes_once(tmp_path, monkeypatch):
    from experiments.exp2g import battery_2g as bg
    monkeypatch.setattr(pw, "N_SIM_5", 20)
    monkeypatch.setattr(pw, "load_finals_counts_5", lambda root: _finals())
    monkeypatch.setattr(pw, "finals_sha256_5", lambda root: "f" * 64)
    rec = pw.main(tmp_path)
    assert b5.power_path_5(tmp_path).is_file() and rec["finals_sha256"] == "f" * 64
    with pytest.raises(RuntimeError, match="ONCE"):
        pw.main(tmp_path)
