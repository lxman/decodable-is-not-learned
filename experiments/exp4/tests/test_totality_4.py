# experiments/exp4/tests/test_totality_4.py
"""Totality (Task 5 brief): every tree shape the runners/hand-editing
can leave gives `analyze_4.run()` INSUFFICIENT_DATA, never a raise.
Built on a SHARED, cheap `stage="reference_only"` base tree (19
reference-stage keys + 4 first units — `full_shape.build_world`'s own
documented minimum for `eligibility_table_4`), with eligibility_4.json
and a real power record (via `power_4.compute()`, review round 1's fix
-- the old stub is deleted) added once, module-scoped; each case corrupts a fresh
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


TOTALITY_POWER_N_SIM_4 = 10   # review round 1, IMPORTANT 3: a real (not stub) power record


def _run_kwargs():
    return dict(tag_exists=lambda t: True, blob_sha=_blob_sha,
               blobs_bound=lambda tag, paths, repo_root=None: [],
               referents_sha=False, imports_pinned=False,
               expected_n_sim=TOTALITY_POWER_N_SIM_4)


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
    # Review round 1, IMPORTANT 3: a REAL power_4.compute() record,
    # not a stub the analyzer's own shape check would now refuse.
    from experiments.exp4 import power_4
    rung_sets_by_traj = {traj: fs._rung_sets(traj) for traj in battery_4.TRAJECTORIES_4}
    grids = {traj: list(battery_4.GRID_4[traj]) for traj in battery_4.TRAJECTORIES_4}
    power_rec = power_4.compute(table, rung_sets_by_traj, grids, n_sim=TOTALITY_POWER_N_SIM_4,
                                seed=11, phis=(0.0, 0.25, 0.5))
    power_rec["eligibility_sha256"] = bg.sha256_file(battery_4.eligibility_path(root))
    power_rec["prereg_tag"] = battery_4.PREREG_TAG_4
    battery_4.power_path(root).write_text(json.dumps(power_rec, indent=1))
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


# ----------------------------------------------------- 5b. torn gate1.json
# (review round 1 follow-up: adding the `_check_power_matches_eligibility_4`
# collect_total_4 site earlier in run() shifted every totality mutant index
# by one, and re-running the renumbered mutant set surfaced a real gap --
# case 5 above writes VALID json (a list), which only exercises the
# gate1_failures_4 call site, not the json.loads(p.read_text()) call
# immediately before it; nothing previously corrupted gate1.json's raw
# bytes into unparseable JSON.)

@pytest.mark.slow
def test_gate1_json_torn_gives_insufficient_data(_totality_base, tmp_path):
    root = _fresh_copy(_totality_base, tmp_path)
    battery_4.gate1_path(root, "pythia_2.8b").parent.mkdir(parents=True, exist_ok=True)
    battery_4.gate1_path(root, "pythia_2.8b").write_text('{"activation_sha_equal": tr')
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "gate 1 pythia_2.8b") and _needle_in_failures(v, "JSONDecodeError")


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


# ------------------------------------------------- 12. _power_summary_4 raises
# (review round 2, IMPORTANT 1(b): `verdict_4`'s `collect_total_4(lambda:
# _power_summary_4(power), ...)` call site -- new to review round 1,
# never before run through totality. `_totality_base` reaches this site
# UNCONDITIONALLY every run (verdict_4 is called at the end of run() no
# matter what failures accumulated earlier, and the totality base's
# power file always loads to a valid dict), but `_power_summary_4`
# never naturally raises on real, well-formed data -- so the established
# pattern here is to monkeypatch the callee itself to raise, on the
# clean totality world, and confirm run() still returns a well-formed
# INSUFFICIENT_DATA verdict (the base's OWN verdict either way, since
# `world`/`tree` are decided before verdict_4 runs) with the failure
# caught and named, rather than propagating out of run() as a raise.)

@pytest.mark.slow
def test_power_summary_4_call_is_collected_not_raised(_totality_base, tmp_path, monkeypatch):
    root = _fresh_copy(_totality_base, tmp_path)

    def _boom(power):
        raise RuntimeError("synthetic _power_summary_4 failure (test-injected)")

    monkeypatch.setattr(an, "_power_summary_4", _boom)
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "power summary")


# ------------------------------------ 13. _check_power_matches_eligibility_4 raises
# Review round 2, IMPORTANT 1(b): the review's re-derived renumbering
# account names this site as the one existing before review round 1
# (old part-2 log, `--only=99`) but under DIFFERENT source text -- its
# call gained an `expected_n_sim=` keyword argument this task, so the
# exact substitution text the harness matches on has changed, and the
# old "killed" result no longer applies to the CURRENT text. Same
# monkeypatch pattern: this site is reached whenever both `power` and
# `eligibility` are present and non-None (true on `_totality_base`),
# which normally never raises on real data.

@pytest.mark.slow
def test_check_power_matches_eligibility_4_call_is_collected_not_raised(_totality_base, tmp_path,
                                                                        monkeypatch):
    root = _fresh_copy(_totality_base, tmp_path)

    def _boom(power, eligibility, eligibility_sha, *, expected_n_sim):
        raise RuntimeError("synthetic _check_power_matches_eligibility_4 failure (test-injected)")

    monkeypatch.setattr(an, "_check_power_matches_eligibility_4", _boom)
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "power vs eligibility")


# ---------------------------------- 16. FREEZE F-2: a pairing missing a reference

@pytest.mark.slow
def test_unit_pairing_missing_a_reference_gives_insufficient_data(_totality_base, tmp_path):
    """FREEZE F-2, through the production loader: the depth pairing was
    read off the record and never re-derived, and its KEY SET was
    unchecked — a unit whose `pairing` names two of its three `refs`
    made a_r a mean over two references instead of the design's three,
    with every gate passing and no cross-check firing (the stored
    `overlap_<ref>` arrays of the remaining two still agree)."""
    root = _fresh_copy(_totality_base, tmp_path)
    traj, step = "pythia_2.8b", battery_4.FIRST_STEP_4["pythia_2.8b"]
    p = battery_4.unit_dir(root, traj, step) / "_load.json"
    rec = json.loads(p.read_text())
    dropped = sorted(rec["pairing"])[0]
    rec["pairing"] = {r: v for r, v in rec["pairing"].items() if r != dropped}
    assert rec["refs"] == list(battery_4.REFS_FOR_4[traj])    # refs field untouched
    p.write_text(json.dumps(rec, indent=1))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "pairing keys"), v["referents"]["failures"][:5]


@pytest.mark.slow
def test_unit_pairing_rotated_gives_insufficient_data(_totality_base, tmp_path):
    """The same closure on the VALUES: caught downstream by
    `per_item_alignment_4`'s stored-overlap cross-check before this
    freeze, but never on the gate-0 path (`_gate0_site_means_4` makes
    no cross-check) — now refused at the loader, by re-derivation."""
    root = _fresh_copy(_totality_base, tmp_path)
    traj, step = "pythia_2.8b", battery_4.FIRST_STEP_4["pythia_2.8b"]
    p = battery_4.unit_dir(root, traj, step) / "_load.json"
    rec = json.loads(p.read_text())
    rec["pairing"] = {r: list(v[1:]) + [v[0]] for r, v in rec["pairing"].items()}
    p.write_text(json.dumps(rec, indent=1))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "depth pairing"), v["referents"]["failures"][:5]


# --------------------------- 17. a reference-STAGE halt marker (not a trajectory's)

@pytest.mark.slow
def test_reference_stage_halt_marker_gives_insufficient_data(_totality_base, tmp_path):
    """`run()` reads five halt paths; the world builder's `halted`
    route only ever writes a TRAJECTORY's. The reference stage's own
    marker (`collect_4.reference_halt_marker_path`, what
    `run/reference_4._halt_reference` writes on a digest mismatch) had
    no world or totality case."""
    from experiments.exp4 import collect_4 as c4
    root = _fresh_copy(_totality_base, tmp_path)
    p = c4.reference_halt_marker_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("endpoint_comma_7b: digest deadbeef != committed cafe\n")
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "the runner halted")


# ------------------- 18. FREEZE F-1: a measured digest that is not the committed one

@pytest.mark.slow
def test_unit_tensor_digest_not_the_committed_one_gives_insufficient_data(_totality_base, tmp_path):
    """FREEZE F-1 through the production loader: `committed_digest` is
    the runner's copy of the expectation, `tensor_digest` the loader's
    own measurement. A record naming ANOTHER trajectory's checkpoint in
    `tensor_digest` used to pass every analyzer check."""
    root = _fresh_copy(_totality_base, tmp_path)
    traj, step = "pythia_2.8b", battery_4.FIRST_STEP_4["pythia_2.8b"]
    p = battery_4.unit_dir(root, traj, step) / "_load.json"
    rec = json.loads(p.read_text())
    rec["tensor_digest"] = battery_4.committed_step_digest_4("olmo2_7b", 1000)
    assert rec["committed_digest"] == battery_4.committed_step_digest_4(traj, step)
    p.write_text(json.dumps(rec, indent=1))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "tensor_digest"), v["referents"]["failures"][:5]


# ------------------------- 19. RATIFICATION: licence_condition_4 raises
# The `collect_total_4(lambda: licence_condition_4(primary), "4 licence
# condition")` site inside `verdict_4` is new to the final review fix
# wave and was never run through totality: its auto-generated mutant
# (`totality_aac94f02b5`) SURVIVED the first ratification pass, because
# `licence_condition_4` never raises on real data. Same monkeypatch
# pattern as cases 12 and 13. The site is reached UNCONDITIONALLY —
# `verdict_4` runs at the end of `run()` whatever failures accumulated —
# so the base's own INSUFFICIENT_DATA verdict is the expected one either
# way; what is under test is that the raise is COLLECTED and named
# rather than propagating out of run().

@pytest.mark.slow
def test_licence_condition_4_call_is_collected_not_raised(_totality_base, tmp_path, monkeypatch):
    root = _fresh_copy(_totality_base, tmp_path)

    def _boom(primary):
        raise RuntimeError("synthetic licence_condition_4 failure (test-injected)")

    monkeypatch.setattr(an, "licence_condition_4", _boom)
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    # asserted on the failure list itself, not through
    # `_needle_in_failures`: that helper searches text that embeds the
    # world's PATH, and pytest names `tmp_path` after the test — so a
    # needle appearing in this test's own name would match the path and
    # pass for free. (Found here: a `lambda_hat` case written the same
    # way passed on a tree that never reaches the lambda_hat site.)
    assert any(f.startswith("4 licence condition:") for f in v["referents"]["failures"]), \
        v["referents"]["failures"]
