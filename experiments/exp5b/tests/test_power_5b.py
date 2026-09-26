import json

import numpy as np
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5 import power_5 as pw
from experiments.exp5b import battery_5b as b5b
from experiments.exp5b import power_5b as pw5b
from experiments.exp5b.tests import helpers_5b as hp

FLOORS = bg.load_floors()


def _cells5(n_rungs=9, per_rung=3, offset=30, seed=1):
    """Synthetic Experiment-5-shaped live cells (the keys `structure_5b` reads)."""
    rng = np.random.default_rng(seed)
    out = []
    for r in list(b5.RUNGS)[:n_rungs]:
        for i in range(per_rung):
            f = 100 + int(rng.integers(0, 50))
            a = f + offset + float(rng.integers(-5, 6))
            out.append({"small": "1b", "large": ("2.8b", "6.9b", "12b")[i], "rung": r,
                        "family": b5.FAMILY_OF[r], "type": b5.RUNG_TYPE_5[r], "f": f, "a": a,
                        "b_minus": a - 4.0, "b_plus": a + 3.0, "R": abs(a - f), "P": 3.5,
                        "c": (abs(a - f) - 3.5) / 500, "signed": (a - f) / 500, "live": True,
                        "defined_P": True, "class": "CONCORDANT", "lo": int(a), "hi": int(a),
                        "raw_reads": [f, int(a), int(a), int(a) - 4, int(a) - 4, int(a) + 3, int(a) + 3]})
    return out


def test_constants_are_exp5s_with_f_now_varied():
    assert pw5b.SIGMA_L_5B == pw.SIGMA_READ_ITEMS_5 and pw5b.DRIFT_5B == pw.DRIFT_SD_ITEMS_5
    assert pw5b.N_SIM_5B == 1000 and pw5b.SEED_5B == 0 and pw5b.POWER_BAR_5B == 0.75
    assert pw5b.ARMS_5B == ("null", "plugin", "shrunk", "exp5_spread")
    assert pw5b.OFFSET_SCALE_5B == {"null": 0.0, "plugin": 1.0, "shrunk": 0.5}
    assert pw5b.D_GRID_5B == pw.D_GRID_5 and pw5b.FRACTION_GRID_5B == (0.25, 0.5, 0.75, 1.0)
    assert pw5b.N_MEMBERS_5B == 3


def test_structure_keeps_every_live_cell_and_its_committed_offset():
    cells5 = _cells5()
    s = pw5b.structure_5b(cells5)
    assert len(s) == 27 and all(x["offset"] == x["a"] - x["f"] for x in s)
    assert pw5b.structure_sha256_5b(s) == pw5b.structure_sha256_5b(pw5b.structure_5b(cells5))


def test_simulate_reads_f_once_and_members_with_a_shared_drift():
    st_ = pw5b.structure_5b(_cells5())
    rng = np.random.default_rng(0)
    cells = pw5b.simulate_5b(st_, FLOORS, sigma_s=0.0, offset_scale=0.0, rng=rng)
    assert len(cells) == 27
    # ruling (Task 3): c["f"] IS the draw; the truth is the structure's f
    for c, s in zip(cells, st_):
        # sigma_s = 0: f_read == f, the members == f + the shared drift (rounded) — all three equal
        assert c["f_B"] == s["f"] and len(set(c["members"].values())) == 1
        assert set(c) >= {"c_exp5_sim", "c_naive", "c_sym", "small_reads", "small_sd"}
    # sigma_s > 0: f differs from its truth on some cells; the three members differ among themselves
    cells = pw5b.simulate_5b(st_, FLOORS, sigma_s=15.0, offset_scale=0.0, rng=np.random.default_rng(1))
    # ruling (Task 3): c["f"] IS the draw; the truth is the structure's f
    assert any(c["f_B"] != s["f"] for c, s in zip(cells, st_))
    assert any(len(set(c["members"].values())) > 1 for c in cells)


def test_null_arm_realized_alpha_of_exp5_rule_rises_with_small_side_noise():
    """Design §2: Experiment 5's rule fires on nothing once σ_s passes ≈ 11;
    the matched rule stays near nominal. Coarse, at n_sim 60."""
    s = pw5b.structure_5b(_cells5(offset=0))
    lo = pw5b.arm_5b(s, FLOORS, sigma_s=5.0, offset_scale=0.0, n_sim=60, rng=np.random.default_rng(0))
    hi = pw5b.arm_5b(s, FLOORS, sigma_s=45.0, offset_scale=0.0, n_sim=60, rng=np.random.default_rng(0))
    assert hi["P_fire_exp5"] > lo["P_fire_exp5"]
    assert hi["P_fire_5b"] <= 0.15 and lo["P_fire_5b"] <= 0.15
    assert hi["mean_T_5b"] <= 0.005 and lo["mean_T_5b"] <= 0.005     # at or below zero (the drifts)
    assert hi["sigma_hat_sim_mean"] > lo["sigma_hat_sim_mean"] > 0


def test_plugin_arm_fires_when_the_committed_offsets_are_large():
    s = pw5b.structure_5b(_cells5(offset=40))
    r = pw5b.arm_5b(s, FLOORS, sigma_s=15.0, offset_scale=1.0, n_sim=40, rng=np.random.default_rng(0))
    assert r["P_fire_5b"] >= 0.9 and r["mean_T_5b"] > 0.02


def test_compute_record_shape_axes_and_determinism():
    cells5 = _cells5(offset=25)
    a = pw5b.compute_5b(cells5, FLOORS, n_sim=12, seed=0)
    b = pw5b.compute_5b(cells5, FLOORS, n_sim=12, seed=0)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert [g["sigma_s"] for g in a["grid"]] == list(b5b.SIGMA_GRID_5B)
    assert len(a["sigma_hat_axis"]) == 6 and a["sigma_hat_axis"] == sorted(a["sigma_hat_axis"])
    for k in ("alpha_5b_axis", "alpha_exp5_axis", "alpha_naive_axis", "null_mean_5b_axis",
              "null_mean_exp5_axis", "null_mean_naive_axis", "null_sd_5b_axis"):
        assert len(a[k]) == 6
    assert set(a["grid"][0]["arms"]) == set(pw5b.ARMS_5B)
    assert a["deciding"] == {"sigma_s": 15, "arm": "plugin", "P_fire_5b": a["grid"][2]["arms"]["plugin"]["P_fire_5b"]}
    assert a["declaration"] in ("POWERED", "DECLARED UNDERPOWERED IN ADVANCE")
    assert [d["D"] for d in a["d_grid"]] == list(pw.D_GRID_5)
    assert [f["fraction"] for f in a["fraction_grid"]] == [0.25, 0.5, 0.75, 1.0]
    assert a["n_live"] == 27 and a["live_rungs"] == sorted({c["rung"] for c in cells5})
    assert a["prereg_tag"] == b5b.PREREG_TAG_5B and a["exp5_closed_tag"] == "exp5-closed"
    assert a["structure_sha256"] == pw5b.structure_sha256_5b(pw5b.structure_5b(cells5))
    assert a["n_members"] == 3 and a["sigma_l"] == pw.SIGMA_READ_ITEMS_5


def test_rng_order_is_fixed_grid_then_d_then_fractions():
    """A record at n_sim 12 and one at n_sim 12 with a different seed differ;
    the same seed reproduces; the grid's first arm at σ_s 5 equals a direct
    arm call on a fresh rng with the same seed."""
    cells5 = _cells5(offset=25)
    rec = pw5b.compute_5b(cells5, FLOORS, n_sim=12, seed=0)
    s = pw5b.structure_5b(cells5)
    direct = pw5b.arm_5b(s, FLOORS, sigma_s=5, offset_scale=0.0, n_sim=12, rng=np.random.default_rng(0))
    assert rec["grid"][0]["arms"]["null"] == direct
    assert json.dumps(pw5b.compute_5b(cells5, FLOORS, n_sim=12, seed=1), sort_keys=True) != \
        json.dumps(rec, sort_keys=True)


def test_load_cells5_live_reads_the_committed_verdict():
    live = pw5b.load_cells5_live_5b(b5b.EXP5)
    assert len(live) == 63 and all(c["live"] and c["defined_P"] for c in live)


def test_main_writes_once_and_requires_exp5_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(pw5b, "N_SIM_5B", 8)
    monkeypatch.setattr(b5b, "check_frozen_5b", lambda: None)
    monkeypatch.setattr(b5b, "check_imports_5b", lambda: None)
    inj = hp.tag_inj()
    rec = pw5b.main(tmp_path, **inj)
    assert b5b.power_path_5b(tmp_path).is_file() and rec["n_live"] == 63
    assert rec["exp5_verdict_sha256"] == b5b.EXP5_VERDICT_SHA256_5B
    with pytest.raises(RuntimeError, match="ONCE"):
        pw5b.main(tmp_path, **inj)
    with pytest.raises(RuntimeError, match="exp5-closed"):
        pw5b.main(tmp_path / "other", tag_exists=lambda t: False, blob_sha=inj["blob_sha"])
    assert not b5b.power_path_5b(tmp_path / "other").exists()
