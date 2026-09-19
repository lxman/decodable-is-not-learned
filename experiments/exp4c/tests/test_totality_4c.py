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

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2i import analyze_2i as an2i
from experiments.exp4 import analyze_4 as a4
from experiments.exp4 import battery_4
from experiments.exp4b import placebo_4b
from experiments.exp4c import analyze_4c as an
from experiments.exp4c import battery_4c as bc
from experiments.exp4c import make_referents_4c as mkr
from experiments.exp4c import rank_4c as rk
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


# =============================================================================
# Task 5 fix round 1b: every remaining `collect_total_4c`-stripped totality
# mutant, and the two hand mutants that need the same machinery
# (`frozen_check`/`check_imports_4c`/`discovery_check` are TEST-ONLY
# injections `run()` already exposes; everything else is a monkeypatch of
# the real module attribute `run()` calls unqualified or through its own
# `a4`/`rk`/`bt`/`bg`/`an2i`/`placebo_4b`/`mkr` aliases — the SAME object
# `analyze_4c.py` itself holds, so patching it here reaches the call inside
# `run()`). Each raiser is a plain function so the totality machinery's
# `collect_total_4c` has something to catch under the REAL code; the
# mutation harness's own re-run of these same tests against the STRIPPED
# wrapper is what turns the catch into an uncaught raise out of `run()`
# (its own docstring's contract: "nothing raises out of this function"),
# which pytest reports as an error — still a kill.

def _raiser(*_a, **_k):
    raise RuntimeError("forced (Task 5 fix round 1b totality probe)")


# --------------------------------------------- halt marker read (unreadable)

def test_halt_marker_unreadable_gives_insufficient_data(_totality_base, tmp_path):
    """The halt marker path exists but is a directory, not a file —
    `.read_text()` raises `IsADirectoryError` rather than the marker
    simply being absent."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    p = battery_4.halt_marker_path(w["root4c"], "pythia_6.9b")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.mkdir()
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "halt marker")


# --------------------------------------------------------- frozen modules

def test_frozen_check_raising_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    v = fs4c.run_world(w, frozen_check=_raiser)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "frozen modules")


# ------------------------------------------------- import surface (entry)

def test_import_surface_entry_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                               monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an, "check_imports_4c", _raiser)
    v = fs4c.run_world(w, imports_pinned=True)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "import surface")


# --------------------------------------------------------- referent manifest

def test_referent_manifest_check_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                                  monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(mkr, "check_referents_4c", _raiser)
    v = fs4c.run_world(w, referents_sha="deadbeef")
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "referent manifest")


# --------------------------------------------------------- battery / floors

def test_load_battery_raising_gives_insufficient_data(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(bt, "load_battery", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "battery items")


def test_load_floors_raising_gives_insufficient_data(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(bg, "load_floors", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "floors")


# ------------------------------------------------- outcomes / rung sets

def test_load_outcome_per_traj_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                                monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(bc, "load_outcome_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "outcome")


def test_rung_sets_per_traj_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                             monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(bc, "rung_sets_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "rung sets")


def test_check_rung_set_pins_per_traj_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                                      monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(bc, "check_rung_set_pins_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "rung-set pins")


# --------------------------------------------------------------- reference seal

def test_reference_seal_raising_gives_insufficient_data(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an2i, "require_seal_2i", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "reference seal")


def test_reference_seal_failures_are_appended_gives_insufficient_data(_totality_base, tmp_path,
                                                                       monkeypatch):
    """`require_seal_2i` returns cleanly (no raise) WITH a non-empty
    `failures` list — the run() code must itself append them; a mutant
    dropping `if seal is not None and seal.get("failures"): ...`
    (Task 5 fix round 1b) would read the run as clean."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an2i, "require_seal_2i",
                        lambda *a_, **k_: {"failures": ["forced seal mismatch"]})
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "forced seal mismatch")


# --------------------------------------------------------------- discovery gate

def test_discovery_gate_raising_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    v = fs4c.run_world(w, discovery_check=_raiser)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "discovery gate")


def test_discovery_pins_check_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                               monkeypatch):
    """`discovery_check` is left at its default stub (so `discovery` is
    not None) and only the pin-check call itself raises."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(rk, "check_discovery_pins_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "discovery pins")


# --------------------------------------------------------------- power record

def test_power_module_import_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                              monkeypatch):
    """`expected_n_sim=None` (unset) forces the auto-discovery branch
    that imports `power_4c` through `_import_power_4c`."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an, "_import_power_4c", _raiser)
    v = fs4c.run_world(w, expected_n_sim=None)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]


def test_power_record_torn_json_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    p = an.power_path_4c(w["root4c"])
    raw = p.read_text()
    p.write_text(raw[: len(raw) // 2])
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "power record")


def test_power_record_fields_check_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                                    monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an, "_power_record_failures_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "power record")


def test_power_record_reproduction_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                                    monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an, "_reproduce_power_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "power record")


# --------------------------------------------------------------- gate 1 (6.9b)

def test_gate1_torn_json_gives_insufficient_data(_totality_base, tmp_path):
    w = fs4c.copy_world(_totality_base, tmp_path)
    p = battery_4.gate1_path(w["root4c"], "pythia_6.9b")
    raw = p.read_text()
    p.write_text(raw[: len(raw) // 2])
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "gate 1")


# ----------------------------------------------------- alignment series (x2)

def test_alignment_series_raising_gives_insufficient_data(_totality_base, tmp_path, monkeypatch):
    """One fake, unconditionally raising, covers BOTH call sites (the
    site-0-excluded default series and the site-0-included S4 series):
    whichever one a given mutant leaves unprotected is the one that
    lets the raise through uncaught."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(rk, "alignment_series_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "alignment series")


# ------------------------------------------- eligibility / per-item alignment

def test_per_item_alignment_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                             monkeypatch):
    """`a4.per_item_alignment_4` backs BOTH `eligibility_4c` (called
    directly in the per-traj loop) and the S4 `pia` dict built right
    after it; unconditionally raising covers both call sites the same
    way `alignment_series_4c` above covers its two."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(a4, "per_item_alignment_4", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]


# --------------------------------------------------------------- gate 0 (6.9b/13b)

def test_gate0_per_traj_raising_gives_insufficient_data(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an, "gate0_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "gate 0")


# --------------------------------------------------------------- cells / primary

def test_cells_4c_raising_gives_insufficient_data(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(rk, "cells_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "cells")


def test_primary_4c_raising_gives_insufficient_data(_totality_base, tmp_path, monkeypatch):
    """`rk.cells_4c` runs for real (unpatched) so `cells` is truthy and
    the main `primary_4c` call is reached."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an, "primary_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "primary")


def test_placebo_4c_raising_gives_insufficient_data(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(rk, "placebo_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "placebo")


def test_type_modifier_4c_raising_gives_insufficient_data(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(rk, "type_modifier_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "type modifier")


def test_gate7_ties_4c_raising_gives_insufficient_data(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an, "gate7_ties_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "gate 7")


def test_calibration_read_4c_raising_gives_insufficient_data(_totality_base, tmp_path,
                                                              monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(rk, "calibration_read_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "calibration")


# --------------------------------------------------------------- secondaries wrapper

def test_secondaries_wrapper_degrades_one_block_not_the_verdict(_totality_base, tmp_path,
                                                                 monkeypatch):
    """S1's underlying function raises; `_sec`'s own `collect_total_4c`
    wrapper (shared by every S1-S10 secondary) catches it — the verdict
    is untouched (secondaries are DESCRIPTIVE) and only `secondaries
    ["S1"]` degrades to `{"failed": [...]}`. A mutant stripping that
    ONE shared wrapper would instead let the raise escape `run()`
    entirely, on ANY secondary — S1 is enough to observe it."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an, "s1_per_run_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    assert v["secondaries"]["S1"].get("failed"), v["secondaries"]["S1"]


# --------------------------------------------------------------- S4 continuity (inner)

def _s4_dict(v):
    return v["secondaries"]["S4"]


def test_s4_cells_4_raising_collapses_only_s4(_totality_base, tmp_path, monkeypatch):
    """`a4.cells_4` (Exp 4's own, S4's continuity arm) raises; its OWN
    inner wrapper catches it and the REST of S4 (lambda_hat, the flat
    eligibility summary, the per-traj placebo pools) still computes
    independently. A mutant stripping only that inner wrapper collapses
    the WHOLE S4 block to `{"failed": [...]}` instead — this is what
    distinguishes it from every other S4-inner mutant below, which all
    share this same shape."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(a4, "cells_4", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    s4 = _s4_dict(v)
    assert not s4.get("failed"), s4
    assert s4["cells"] == [] and s4["primary"] is None
    assert "lambda_hat" in s4


def test_s4_primary_4_raising_collapses_only_s4(_totality_base, tmp_path, monkeypatch):
    """`a4.cells_4` runs for real so `cells` is truthy and the S4
    `primary_4` call is reached."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(a4, "primary_4", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    s4 = _s4_dict(v)
    assert not s4.get("failed"), s4
    assert s4["primary"] is None
    assert "lambda_hat" in s4


def test_s4_lambda_hat_4_raising_collapses_only_s4(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(a4, "lambda_hat_4", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    s4 = _s4_dict(v)
    assert not s4.get("failed"), s4
    assert s4["lambda_hat"] is None
    assert "cells" in s4 and s4["cells"] != []


def test_s4_placebo_pool_4b_raising_collapses_only_s4(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(placebo_4b, "placebo_pool_4b", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    s4 = _s4_dict(v)
    assert not s4.get("failed"), s4
    assert "lambda_hat" in s4
    assert s4["placebo_pool"] == {}


def test_s4_design_4c_raising_collapses_only_s4(_totality_base, tmp_path, monkeypatch):
    """Everything up to `design` runs for real (cells, primary,
    lambda_hat, placebo pools all succeed) and only the design call
    itself raises."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an, "_design_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    s4 = _s4_dict(v)
    assert not s4.get("failed"), s4
    assert "lambda_hat" in s4
    assert "design" not in s4


def test_s4_draw_batteries_4b_raising_collapses_only_s4(_totality_base, tmp_path, monkeypatch):
    """cells/primary/lambda_hat/pools/design all run for real; only the
    battery draw raises, so `design` is computed but never stored (the
    real code only assigns `out["design"]` inside the `if batteries is
    not None:` block)."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(placebo_4b, "draw_batteries_4b", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    s4 = _s4_dict(v)
    assert not s4.get("failed"), s4
    assert "lambda_hat" in s4
    assert "design" not in s4 and "p_cal" not in s4


def test_s4_p_cal_4b_raising_collapses_only_s4(_totality_base, tmp_path, monkeypatch):
    """Everything through `draw_batteries_4b` runs for real; only
    `p_cal_4b` raises. `t_star`/`alpha_placebo`/`design` are each their
    OWN independent `collect_total_4c` calls and still populate
    `out` — the real code writes all five keys unconditionally after
    the three calls."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(placebo_4b, "p_cal_4b", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    s4 = _s4_dict(v)
    assert not s4.get("failed"), s4
    assert s4.get("p_cal") is None
    assert "design" in s4 and "t_star" in s4


def test_s4_t_star_4b_raising_collapses_only_s4(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(placebo_4b, "t_star_4b", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    s4 = _s4_dict(v)
    assert not s4.get("failed"), s4
    assert s4.get("t_star") is None
    assert "design" in s4 and "p_cal" in s4


def test_s4_alpha_placebo_4b_raising_collapses_only_s4(_totality_base, tmp_path, monkeypatch):
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(placebo_4b, "alpha_placebo_4b", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    s4 = _s4_dict(v)
    assert not s4.get("failed"), s4
    assert s4.get("alpha_placebo") is None
    assert "design" in s4 and "p_cal" in s4 and "t_star" in s4


# --------------------------------------------------------------- licence block

def test_licence_block_raising_still_returns_the_tree_verdict(_totality_base, tmp_path,
                                                               monkeypatch):
    """`licence_block_4c` raises; `verdict_4c`'s own wrapper builds the
    documented default licence (a bare INSUFFICIENT_DATA sentence,
    modifier/bounded/reversed all None) WITHOUT changing the top-level
    verdict, which still reads the tree's real world (REPLICATES on an
    untouched world) — the licence block never gates the verdict."""
    w = fs4c.copy_world(_totality_base, tmp_path)
    monkeypatch.setattr(an, "licence_block_4c", _raiser)
    v = fs4c.run_world(w)
    assert v["verdict"] == "REPLICATES", v["reason"]
    assert v["licence"]["modifier"] is None
    assert v["licence"]["bounded"] is None
    assert v["licence"]["sentence"] == an.LICENSED_4C["INSUFFICIENT_DATA"]
