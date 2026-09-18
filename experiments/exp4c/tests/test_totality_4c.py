# experiments/exp4c/tests/test_totality_4c.py
"""Totality (Task 5 brief, step 4): every tree shape a corruption can
leave gives `analyze_4c.run()` INSUFFICIENT_DATA, never a raise — on a
COPY of the shared `replicates` world (`full_shape_4c.build_world`),
each case corrupting a fresh copy (`full_shape_4c.copy_world`). The
control (an untouched copy still REPLICATES) closes the module.

Several of the fourteen corruptions below name the SAME failure
mechanism `test_full_shape_4c.py`'s `MISSING_ROUTES_4C` already
exercises (halted, step0 missing, the exp4 reference record tampered,
a power record with the wrong n_sim, a discovery record off its pin)
— the brief lists them again here by name, on this file's own shared
world, so they are reproduced directly via `full_shape_4c.
apply_missing_4c` rather than re-implemented."""
from __future__ import annotations

import hashlib
import json

import pytest

from experiments.exp4 import battery_4
from experiments.exp4c import analyze_4c as an
from experiments.exp4c import battery_4c as bc
from experiments.exp4c.tests import full_shape_4c as fs4c

pytestmark = pytest.mark.slow


@pytest.fixture(autouse=True)
def _blobs_that_exist(monkeypatch):
    monkeypatch.setattr(bc, "INSTRUMENT_BLOBS_4C", fs4c.existing_instrument_blobs_4c())


@pytest.fixture(scope="module")
def _totality_base(tmp_path_factory):
    root = tmp_path_factory.mktemp("totality_base")
    return fs4c.build_world(root / "root4c", root / "root4", "replicates", seed=0)


def _needle_in_failures(v, needle):
    text = " ".join(v.get("failures") or []) + " " + (v.get("reason") or "")
    return needle.lower() in text.lower()


# ---------------------------------------------------------------- control

def test_control_untouched_copy_still_replicates(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]


# --------------------------------------------------------- 1. torn _load.json

def test_torn_load_json_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    traj = "pythia_6.9b"
    step = list(bc.GRID_4C[traj])[0]
    p = battery_4.unit_dir(w["root4c"], traj, step) / "_load.json"
    raw = p.read_text()
    p.write_text(raw[: len(raw) // 2])   # torn mid-token
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "JSONDecodeError")


# ---------------------------------------- 2. a directory where an npz belongs

def test_directory_where_an_npz_belongs_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    p = battery_4.sets_path(w["root4"], "ref_pythia_12b", "antonym")
    p.unlink()
    p.mkdir()
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]


# -------------------------------------------------------- 3. npz not a zip

def test_npz_not_a_zip_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    p = battery_4.sets_path(w["root4"], "ref_olmo2_7b", "antonym6")
    p.write_bytes(b"not a zip")
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]


# --------------------------------------------------------- 4. truncated npz

def test_truncated_npz_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    p = battery_4.sets_path(w["root4"], "ref_smollm3_3b", "arith_next")
    raw = p.read_bytes()
    p.write_bytes(raw[: len(raw) // 2])   # a valid zip header, corrupted/truncated body
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]


# ------------------------------------------------------ 5. gate1.json a list

def test_gate1_json_a_list_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    battery_4.gate1_path(w["root4c"], "pythia_6.9b").write_text(json.dumps([1, 2, 3]))
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]


# ----------------------------------------- 6. HALTED under sweep/olmo2_13b/

def test_halted_under_olmo2_13b_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    needle = fs4c.apply_missing_4c(w, "halted")
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, needle)


# ---------------------------- 7. thin endpoint's prereg_tag is exp4's

def test_thin_endpoint_wrong_prereg_tag_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    p = battery_4.reference_dir(w["root4c"], bc.THIN_ENDPOINT_KEY_4C) / "_load.json"
    rec = json.loads(p.read_text())
    assert rec["prereg_tag"] == bc.PREREG_TAG_4C
    rec["prereg_tag"] = "exp4-preregistered"
    p.write_text(json.dumps(rec, indent=1))
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "prereg_tag")


# ----------------------------------------------- 8. power_4c.json n_sim 39

def test_power_record_n_sim_39_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    p = w["root4c"] / "results" / "power_4c.json"
    rec = json.loads(p.read_text())
    rec["n_sim"] = 39
    p.write_text(json.dumps(rec))
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "n_sim")


# --------------------------------------- 9. power_4c.json probability edited

def test_power_record_probability_edited_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    p = w["root4c"] / "results" / "power_4c.json"
    rec = json.loads(p.read_text())
    rec["arms"]["null"]["P_01"] = 0.999
    p.write_text(json.dumps(rec))
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "power record")


# ------------------------------------- 10. grid unit missing roman_sum7.npz

def test_grid_unit_missing_a_rung_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    traj = "pythia_6.9b"
    step = list(bc.GRID_4C[traj])[0]
    p = battery_4.unit_dir(w["root4c"], traj, step) / "sets" / "roman_sum7.npz"
    p.unlink()
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "roman_sum7")


# ------------------------------------------------- 11. step 0 missing entirely

def test_step0_missing_entirely_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    needle = fs4c.apply_missing_4c(w, "step0_missing")
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, needle)


# --------------------------------- 12. the 2h manifest, one byte flipped

def test_2h_manifest_one_byte_flipped_gives_insufficient_data(_totality_base, tmp_path,
                                                               monkeypatch):
    from experiments.exp2h import battery_2h as bh
    w = fs4c.copy_world(_totality_base, tmp_path)
    real_path = bh.CHECKPOINTS_PATH_69
    raw = bytearray(real_path.read_bytes())
    # flip one bit in the middle of the file, safely inside the JSON
    # body (never the first/last byte) so the change is a byte flip,
    # not a truncation
    i = len(raw) // 2
    raw[i] ^= 0x01
    tampered = tmp_path / "checkpoints_2h_tampered.json"
    tampered.write_bytes(bytes(raw))
    assert hashlib.sha256(bytes(raw)).hexdigest() != hashlib.sha256(real_path.read_bytes()).hexdigest()
    monkeypatch.setattr(bh, "CHECKPOINTS_PATH_69", tampered)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "checkpoint manifests")


# --------------------------------- 13. Exp 4's ref_comma_7b sets sha changed

def test_exp4_ref_comma_7b_sets_sha_changed_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    needle = fs4c.apply_missing_4c(w, "exp4_ref_record_tampered")
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, needle)


# --------------------------------------- 14. discovery pin U off by 1e-9

def test_discovery_pin_u_off_by_a_nanounit_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)

    def bad_discovery(root4=None):
        rec = fs4c.discovery_stub_4c(root4)
        rec["U"] = rec["U"] + 1e-9
        return rec

    v = fs4c.run_world(w, discovery_check=bad_discovery)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "discovery gate")
