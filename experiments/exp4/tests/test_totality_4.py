# experiments/exp4/tests/test_totality_4.py
"""Totality (Task 5 brief): every tree shape the runners/hand-editing
can leave gives `analyze_4.run()` INSUFFICIENT_DATA, never a raise.
Built on a SHARED, cheap `stage="reference_only"` base tree (19
reference-stage keys + 4 first units — `full_shape.build_world`'s own
documented minimum for `eligibility_table_4`), with eligibility_4.json
and a power stub added once, module-scoped; each case corrupts a fresh
copy. Deliberately NOT a `stage="full"` (92-point) world: `run()`'s
per-trajectory loop reads `STAGE1_KEYS_4`/`STAGE1_FIRST_UNITS_4` for
stage_tables/gate 0/eligibility/power (none of them touch an interior
sweep step), and its dict-comprehension load over `GRID_4[traj]` stops
at the FIRST bad step it meets — so a needle placed at the trajectory's
SECOND real grid step is reached without ever building the ~90 interior
points a full world would need. One case (`sweep unit with 33 rungs`)
needs exactly one extra unit at that second grid step; every other
case fires before the per-trajectory loop is even entered, or needs
only the already-present reference-stage/first-unit/endpoint files.

The control ("an untouched LEADS world still LEADS") is NOT rebuilt
here: `test_full_shape_4.py::test_leads_world_reaches_leads` already
covers it end to end on the real, full grid (Task 4, re-run this
session after the gate-0 fix); `_totality_base` unmodified is verified
below to still deliver a coherent, non-crashing verdict object as a
FAST pure-function check on this smaller tree (INSUFFICIENT_DATA is
still the correct verdict on a reference-only tree — it has no sweep
data — so this only asserts a real, well-formed verdict is produced,
not a specific world)."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp4 import analyze_4 as an
from experiments.exp4 import battery_4
from experiments.exp4.tests import full_shape as fs


def _blob_sha(tag, rel):
    p = battery_4.REPO / rel
    return bg.sha256_file(p) if p.is_file() else None


def _run_kwargs():
    return dict(tag_exists=lambda t: True, blob_sha=_blob_sha,
               blobs_bound=lambda tag, paths, repo_root=None: [],
               referents_sha=False, imports_pinned=False)


def _needle_in_failures(v, needle):
    ref = (v.get("referents") or {}).get("failures") or []
    text = " ".join(ref) + " " + (v.get("reason") or "")
    return needle.lower() in text.lower()


@pytest.fixture(scope="module")
def _totality_base(tmp_path_factory):
    root = tmp_path_factory.mktemp("totality_base")
    fs.build_world(root, "leads", seed=11, stage="reference_only")
    table = an.eligibility_table_4(root)
    battery_4.eligibility_path(root).parent.mkdir(parents=True, exist_ok=True)
    battery_4.eligibility_path(root).write_text(json.dumps(table, indent=1))
    fs._write_power_stub(root, table, battery_4.TRAJECTORIES_4)
    return root


def _fresh_copy(template_root, tmp_path):
    dst = tmp_path / "world"
    shutil.copytree(template_root, dst)
    return dst


# ---------------------------------------------------------------- control

def test_control_untouched_tree_gives_a_well_formed_verdict(_totality_base, tmp_path):
    # NOT the full-LEADS-world control (see module docstring) -- a
    # reference-only tree has no sweep data, so INSUFFICIENT_DATA is
    # itself the correct, expected verdict here; this only asserts the
    # run doesn't raise and returns the standard shape.
    root = _fresh_copy(_totality_base, tmp_path)
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] in an.WORLDS_4
    assert isinstance(v["referents"]["failures"], list)


# -------------------------------------------------------- 1. torn _load.json

@pytest.mark.slow
def test_torn_load_json_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    p = battery_4.load_record_path(root, "ref_pythia_12b")
    p.write_text('{"family": "pythia", "render": "plai')   # truncated JSON, torn mid-token
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    # `load_stage_tables_4` is wrapped as ONE `collect_total_4` site in
    # run() (over every STAGE1_KEYS_4/STAGE1_FIRST_UNITS_4 key at
    # once), so the failure names the mechanism, not the specific key.
    assert _needle_in_failures(v, "stage tables") and _needle_in_failures(v, "JSONDecodeError")


# ------------------------------------------------ 2. directory where a file belongs

@pytest.mark.slow
def test_directory_where_a_file_belongs_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    rung = battery_4.RUNGS[0]
    p = battery_4.sets_path(root, "ref_pythia_12b", rung)
    p.unlink()
    p.mkdir()
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "ref_pythia_12b")


# ---------------------------------------------------- 3. an npz that is not an npz

@pytest.mark.slow
def test_npz_that_is_not_an_npz_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    rung = battery_4.RUNGS[1]
    p = battery_4.sets_path(root, "ref_olmo2_7b", rung)
    p.write_bytes(b"this is not a zip archive at all, just plain bytes")
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "ref_olmo2_7b")


# -------------------------------------------------------- 4. a truncated npz

@pytest.mark.slow
def test_truncated_npz_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    rung = battery_4.RUNGS[2]
    p = battery_4.sets_path(root, "ref_smollm3_3b", rung)
    raw = p.read_bytes()
    p.write_bytes(raw[:len(raw) // 2])   # a valid zip header, corrupted/truncated body
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "ref_smollm3_3b")


# ----------------------------------------------------------- 5. gate1.json a list

@pytest.mark.slow
def test_gate1_json_list_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    battery_4.gate1_path(root, "pythia_2.8b").parent.mkdir(parents=True, exist_ok=True)
    battery_4.gate1_path(root, "pythia_2.8b").write_text(json.dumps([1, 2, 3]))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "gate 1 pythia_2.8b")


# --------------------------------------------------------------- 6. HALTED present

def test_halted_marker_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    battery_4.halt_marker_path(root, "olmo2_7b").parent.mkdir(parents=True, exist_ok=True)
    battery_4.halt_marker_path(root, "olmo2_7b").write_text("digest mismatch\n")
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "halted")


# ------------------------------------------------- 7. eligibility cell missing

def test_eligibility_cell_missing_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    elig_path = battery_4.eligibility_path(root)
    table = json.loads(elig_path.read_text())
    traj = "pythia_2.8b"
    r_dict = table[traj]["R"]
    assert r_dict, "the leads-mode reference tree must have >=1 R-rung eligibility entry"
    dropped = next(iter(r_dict))
    del r_dict[dropped]
    elig_path.write_text(json.dumps(table, indent=1))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "eligibility")


# ------------------------------------------- 8. power referencing a bogus rung

def test_power_record_references_a_rung_not_in_eligibility(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    power_path = battery_4.power_path(root)
    power = json.loads(power_path.read_text())
    power["rungs"] = list(power["rungs"]) + ["not_a_real_rung"]
    power_path.write_text(json.dumps(power, indent=1))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "power record")


# --------------------------------------------------- 9. sweep unit, 33 rungs

@pytest.mark.slow
def test_sweep_unit_with_33_rungs_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    traj = "pythia_2.8b"
    steps = list(battery_4.GRID_4[traj])
    second_step = steps[1]
    # `load_sweep_tables_4`'s dict comprehension over `GRID_4[traj]`
    # stops at the FIRST bad step; the first step is already valid
    # (reference_only), so a needle at the SECOND real step is the
    # first thing the sweep loader meets -- no need to populate the
    # rest of the (unshrinkable, per test_full_shape_4.py's own
    # finding) real grid.
    src = battery_4.unit_dir(root, traj, battery_4.ENDPOINT_STEP_4[traj])
    dst = battery_4.unit_dir(root, traj, second_step)
    shutil.copytree(src, dst)
    rec_path = dst / "_load.json"
    rec = json.loads(rec_path.read_text())
    rec["committed_digest"] = battery_4.committed_step_digest_4(traj, second_step)
    rec_path.write_text(json.dumps(rec, indent=1))
    missing_rung = battery_4.RUNGS[3]
    (dst / "sets" / f"{missing_rung}.npz").unlink()

    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, missing_rung)


# ----------------------------------------- 10. first unit lacks committed_digest

@pytest.mark.slow
def test_first_unit_lacks_committed_digest_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    traj = "comma_7b"
    first_step = battery_4.FIRST_STEP_4[traj]
    rec_path = battery_4.unit_dir(root, traj, first_step) / "_load.json"
    rec = json.loads(rec_path.read_text())
    del rec["committed_digest"]
    rec_path.write_text(json.dumps(rec, indent=1))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "committed_digest")


# --------------------------------------------- 11. reference sets sha off by one

@pytest.mark.slow
def test_reference_key_sets_sha_off_by_one_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    rung = battery_4.RUNGS[4]
    rec_path = battery_4.load_record_path(root, "ref_comma_7b")
    rec = json.loads(rec_path.read_text())
    sha = rec["sets_sha256"][rung]
    last = sha[-1]
    flipped = "0" if last != "0" else "1"
    rec["sets_sha256"][rung] = sha[:-1] + flipped
    rec_path.write_text(json.dumps(rec, indent=1))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "ref_comma_7b")
