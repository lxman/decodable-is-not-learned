# experiments/exp4b/tests/test_totality_4b.py
"""Totality (Task 6 brief, carried item (d)): every `collect_total_4b`
call site in `analyze_4b.run()` -- 39 of them at the freeze (37 at
Task 6's first cut, 38 with the import-surface EXIT check, 39 with the
freeze's gate 6, whose own wrapper test is FAST and lives in
`test_analyze_4b.py`: an empty `root4` makes
`battery_4.gate1_rederive_4` raise, so no world is needed to reach
that site) -- AST-enumerated the same
way `experiments/exp4/tests/mutation_check.py`'s `_totality_mutants_4`
does (name check changed to `collect_total_4b`; see `mutation_check.py`
in this directory for the generator itself) -- gives `INSUFFICIENT_
DATA`, never a raise, when its own input fails.

Coverage is split three ways:

* A HANDFUL of sites are reached unconditionally, regardless of
  `root4` (`bt.load_battery`/`bg.load_floors` read real, shared,
  committed exp2d/exp2g bytes that exist independently of any exp4/
  exp4b tree) -- these are tested CHEAPLY, no synthetic world, by
  monkeypatching the frozen loader to raise.
* Most sites need a self-consistent exp4-shaped tree to reach at all
  (Exp 4's own committed verdict/eligibility/power records, a real
  sweep). These reuse `conftest.py`'s session-scoped `_leads_world_4b`
  (gates 1-5 all PASS on it, and the per-trajectory placebo-pool loop
  IS entered -- the design §4 feasibility floor only fires AFTER that
  loop, per `test_full_shape_4b.py`'s own build finding) -- corrupted
  via a `shutil.copytree` fresh copy per case, exactly `test_gate*_
  fails_when_*`'s own pattern in `test_analyze_4b.py`.
* The placebo-STAGE sites (`draw_batteries_4b` onward: p_cal, t_star,
  alpha_placebo, per_traj, per_type, S3-S5, S8, S1, S6, S7) are never
  reached on "leads" at all (the floor fires first) and have NO
  committed file backing them to corrupt -- there is no "placebo-stage
  input" on disk, only values freshly computed from already-validated
  exp4 data each run. These are reached on `conftest.py`'s session-
  scoped `_follows_world_4b` (the world that clears the floor and
  completes the pipeline) and probed by monkeypatching the underlying
  function to raise -- `experiments/exp4/tests/test_totality_4.py`'s
  own cases 12/13/19 precedent for a site that "never naturally raises
  on real data".

A site whose corruption/monkeypatch test lives in `test_analyze_4b.py`
already (gates 1/2/3/4, via `test_gate{1,2,3,4}_fails_when_*`) is not
duplicated here; gate (5) had no such test (Task 6 adds one below,
alongside its siblings)."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4b import analyze_4b as an4b  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402
from experiments.exp4b import levels_4b  # noqa: E402
from experiments.exp4b import placebo_4b  # noqa: E402
from experiments.exp4b import power_ext_4b  # noqa: E402
from experiments.exp4b.tests import full_shape_4b as fs4b  # noqa: E402
from experiments.exp4b.tests.conftest import fresh_copy_4b  # noqa: E402


def _run4b_kwargs(*, world=True):
    """See `test_analyze_4b.py`'s own copy."""
    kw = dict(tag_exists=lambda t: True, blob_sha=fs4b.blob_sha_4b,
             referents_sha=False, imports_pinned=False, frozen_check=lambda: None)
    if world:
        from experiments.exp4.tests import full_shape as fs
        kw["expected_n_sim"] = fs.WORLD_POWER_N_SIM_4
    return kw


# =================================================== cheap, no world needed


def test_frozen_check_raise_gives_insufficient_data(tmp_path):
    def _boom():
        raise RuntimeError("synthetic frozen-check failure (test-injected)")

    v = an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4", frozen_check=_boom,
                tag_exists=lambda t: True, blob_sha=fs4b.blob_sha_4b,
                referents_sha=False, imports_pinned=False)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b frozen (exp4-closed)" in v["reason"]


def test_import_surface_entry_check_raise_gives_insufficient_data(tmp_path, monkeypatch):
    """`imports_pinned=False` (used by every other test in this suite,
    and by `_run4b_kwargs()`) never calls `check_imports_4b` at all --
    this is the one test with `imports_pinned=True`, so the "4b import
    surface (entry)" `collect_total_4b` site is genuinely reached."""
    def _boom():
        raise RuntimeError("synthetic check_imports_4b failure (test-injected)")

    monkeypatch.setattr(an4b, "check_imports_4b", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4",
                tag_exists=lambda t: True, blob_sha=fs4b.blob_sha_4b,
                referents_sha=False, imports_pinned=True, frozen_check=lambda: None)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b import surface (entry)" in v["reason"]


def test_prereg_tag_missing_gives_insufficient_data(tmp_path):
    v = an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4",
                tag_exists=lambda t: False, blob_sha=fs4b.blob_sha_4b,
                referents_sha=False, imports_pinned=False, frozen_check=lambda: None)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b prereg tag" in v["reason"]


def test_referent_manifest_bad_pin_gives_insufficient_data(tmp_path):
    v = an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4",
                tag_exists=lambda t: True, blob_sha=fs4b.blob_sha_4b,
                referents_sha="0" * 64, imports_pinned=False, frozen_check=lambda: None)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b referent manifest" in v["reason"]


def test_battery_items_raise_gives_insufficient_data(tmp_path, monkeypatch):
    """`bt.load_battery` (real, committed exp2d bytes) is called
    UNCONDITIONALLY in `run()`, regardless of `root4` -- reached on an
    empty tree with no synthetic world needed."""
    def _boom():
        raise RuntimeError("synthetic load_battery failure (test-injected)")

    monkeypatch.setattr(an4b.bt, "load_battery", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4", **_run4b_kwargs(world=False))
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b battery items" in v["reason"]


def test_floors_raise_gives_insufficient_data(tmp_path, monkeypatch):
    """`bg.load_floors` -- also unconditional, same reasoning."""
    def _boom():
        raise RuntimeError("synthetic load_floors failure (test-injected)")

    monkeypatch.setattr(an4b.bg, "load_floors", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4", **_run4b_kwargs(world=False))
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b floors 2d" in v["reason"]


def test_outcome_raise_gives_insufficient_data(tmp_path, monkeypatch):
    """`battery_4.load_outcome_4` per trajectory -- reached once battery/
    floors load (both unconditional), still no synthetic world needed:
    the outcome read is real, committed exp2c/2g bytes, independent of
    `root4`."""
    def _boom(traj, *, battery=None):
        raise RuntimeError("synthetic load_outcome_4 failure (test-injected)")

    monkeypatch.setattr(an4b.battery_4, "load_outcome_4", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4", **_run4b_kwargs(world=False))
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b outcome" in v["reason"]


def test_rung_sets_raise_gives_insufficient_data(tmp_path, monkeypatch):
    def _boom(oc, floors):
        raise RuntimeError("synthetic rung_sets_4 failure (test-injected)")

    monkeypatch.setattr(an4b.battery_4, "rung_sets_4", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4", **_run4b_kwargs(world=False))
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b rung sets" in v["reason"]


# ================================================= "leads" world, corrupted


@pytest.mark.slow
def test_exp4_verdict_torn_json_gives_insufficient_data(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    battery_4.verdict_path(world).write_text('{"verdict": "LEADS", "primary": {"T": 0.4')
    v = an4b.run(root4b=tmp_path / "4b", root4=world, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b exp4 verdict" in v["reason"] and "JSONDecodeError" in v["reason"]


@pytest.mark.slow
def test_exp4_eligibility_torn_json_gives_insufficient_data(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    battery_4.eligibility_path(world).write_text('{"pythia_2.8b": {"R": {"antonym')
    v = an4b.run(root4b=tmp_path / "4b", root4=world, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b exp4 eligibility" in v["reason"] and "JSONDecodeError" in v["reason"]


@pytest.mark.slow
def test_exp4_power_torn_json_gives_insufficient_data(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    battery_4.power_path(world).write_text('{"n_sim": 20, "seed": 0, "phis": [0.0')
    v = an4b.run(root4b=tmp_path / "4b", root4=world, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b exp4 power" in v["reason"] and "JSONDecodeError" in v["reason"]


@pytest.mark.slow
def test_t4_from_verdict_non_numeric_gives_insufficient_data(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    vp = battery_4.verdict_path(world)
    rec = json.loads(vp.read_text())
    rec["primary"]["T"] = "not-a-number"          # not None, so load_exp4_verdict_4b's own
    vp.write_text(json.dumps(rec))                # "carries no primary" check does not fire here
    v = an4b.run(root4b=tmp_path / "4b", root4=world, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b T_4 from verdict" in v["reason"]


@pytest.mark.slow
def test_cells_from_verdict_off_grid_t_clear_gives_insufficient_data(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    vp = battery_4.verdict_path(world)
    rec = json.loads(vp.read_text())
    assert rec["cells"], "the committed verdict must carry at least one cell"
    rec["cells"][0]["t_clear"] = 999_999_999       # not on GRID_4[traj]
    vp.write_text(json.dumps(rec))
    v = an4b.run(root4b=tmp_path / "4b", root4=world, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b cells from verdict" in v["reason"]


@pytest.mark.slow
def test_real_design_raise_gives_insufficient_data(_leads_world_4b, tmp_path, monkeypatch):
    root4, v4 = _leads_world_4b

    def _boom(cells):
        raise RuntimeError("synthetic real_design_4b failure (test-injected)")

    monkeypatch.setattr(battery_4b, "real_design_4b", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b real design" in v["reason"]


@pytest.mark.slow
def test_stage_tables_torn_json_gives_insufficient_data(_leads_world_4b, tmp_path):
    """A reference key (`ref_pythia_12b`, one of `STAGE1_KEYS_4`) is
    read here BEFORE the per-trajectory loop, so corrupting it hits
    "4b stage tables", not "4b ref tables {traj}" (`load_stage_tables_4`
    calls `_load_one_unit_4` directly, never `collect_4.load_ref_
    tables_4` -- the two functions never share a call site, so the
    two totality sites are genuinely distinguishable by which reads
    fail where)."""
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    p = battery_4.load_record_path(world, "ref_pythia_12b")
    p.write_text('{"family": "pythia", "render": "plai')
    v = an4b.run(root4b=tmp_path / "4b", root4=world, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b stage tables" in v["reason"]


@pytest.mark.slow
def test_sweep_unit_missing_gives_insufficient_data(_leads_world_4b, tmp_path):
    """An INTERIOR grid step (not the first step, not the endpoint --
    both already loaded by "4b stage tables" via `STAGE1_FIRST_UNITS_4`/
    `endpoint_<traj>`) deleted outright: `_load_one_unit_4` raises
    `ValueError` for a missing `_load.json`, caught at "4b sweep
    tables {traj}"."""
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    traj = "pythia_2.8b"
    step = battery_4.GRID_4[traj][1]
    shutil.rmtree(battery_4.unit_dir(world, traj, step))
    v = an4b.run(root4b=tmp_path / "4b", root4=world, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b sweep tables pythia_2.8b" in v["reason"]


@pytest.mark.slow
def test_ref_tables_raise_gives_insufficient_data(_leads_world_4b, tmp_path, monkeypatch):
    """`collect_4.load_ref_tables_4` is called ONLY from the per-
    trajectory "4b ref tables {traj}" site -- `load_stage_tables_4`
    never calls it (see the "stage tables" test's own docstring) -- so
    monkeypatching it raises there and nowhere earlier."""
    root4, v4 = _leads_world_4b

    def _boom(root, ref_keys):
        raise RuntimeError("synthetic load_ref_tables_4 failure (test-injected)")

    monkeypatch.setattr(collect_4, "load_ref_tables_4", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b ref tables" in v["reason"]


@pytest.mark.slow
def test_alignment_series_raise_gives_insufficient_data(_leads_world_4b, tmp_path, monkeypatch):
    """No committed file corrupts `alignment_series_4` alone without
    also breaking the sweep/ref table reads it depends on -- reached
    only by monkeypatching the function itself (exp4's own cases
    12/13/19 precedent: a site with no natural failure mode on real
    data)."""
    root4, v4 = _leads_world_4b

    def _boom(root, traj, ref_tables, stage_tables):
        raise RuntimeError("synthetic alignment_series_4 failure (test-injected)")

    monkeypatch.setattr(an4b.an, "alignment_series_4", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b alignment series" in v["reason"]


@pytest.mark.slow
def test_s7_known_answer_gate_catches_a_corrupted_committed_t(_follows_world_4b, tmp_path,
                                                               monkeypatch):
    """Mutation harness finding (Task 6): `_s7`'s own internal
    known-answer check (`if committed_cas_T is not None and cas_T !=
    committed_cas_T: raise ValueError(...)`) had no test corrupting the
    committed `sensitivities.primary_clears_and_stays.T` it compares
    against -- every prior S7 site test (the parametrized `_FOLLOWS_
    SITES` one above) monkeypatches a FUNCTION to raise, never exercises
    this specific internal comparison on a genuinely mismatched but
    otherwise well-formed tree. S1/S6 are stubbed to their own minimal
    valid shape (never raised) so `run()` reaches S7 without paying
    S1's real 1000-simulation cost or S6's real overlap recomputation
    -- both must SUCCEED, cheaply, for the pipeline to get there at
    all; what is under test is `_s7`'s OWN raise, not S1/S6."""
    root4, v4 = _follows_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    vp = battery_4.verdict_path(world)
    rec = json.loads(vp.read_text())
    rec["sensitivities"]["primary_clears_and_stays"]["T"] += 0.999999
    vp.write_text(json.dumps(rec))

    def _fast_s1(elig, rung_sets, grids, lambda_by_traj, *, n_sim):
        return {"arms": {"observed_lambda": {"Ts": [], "P_LEADS": 0.0}, "4.0": {}, "6.0": {},
                        "8.0": {}, "12.0": {}, "rms_lambda": {}},
                "order": [], "seed": 0, "n_sim": 0, "lambda_by_traj": {}}

    monkeypatch.setattr(power_ext_4b, "extension_arms_4b", _fast_s1)
    monkeypatch.setattr(levels_4b, "ladder_4b", lambda root4: {})
    monkeypatch.setattr(levels_4b, "twins_4b", lambda root4: {})
    monkeypatch.setattr(levels_4b, "ceiling_4b", lambda root4: {})
    monkeypatch.setattr(levels_4b, "within_family_4b", lambda root4: {})
    monkeypatch.setattr(levels_4b, "max_over_pairs_4b", lambda root4, cells4: {})

    v = an4b.run(root4b=tmp_path / "4b", root4=world, power_gate="full", **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b S7" in v["reason"], v["reason"]


@pytest.mark.slow
def test_import_surface_exit_check_raise_gives_insufficient_data(_follows_world_4b, tmp_path,
                                                                  monkeypatch):
    """Mutation harness review finding 3: the import surface is
    checked at ENTRY only in Task 6's first cut -- exp4's own `analyze_
    4.run()` checks it twice (entry, then again at exit, "after every
    secondary/sensitivity has had the chance to import something the
    entry check never saw", 2j F-1). Mirrored in `analyze_4b.run()`
    right after S7. A STATEFUL monkeypatch is required here (not a
    plain `_boom`): `imports_pinned=True` means `check_imports_4b`
    fires at BOTH the entry and exit sites, and the entry call must
    succeed for real (real `sys.modules` scan) so the run gets far
    enough to reach the exit site at all -- only the SECOND call
    raises. S1/S6 stubbed cheap (the S7 test's own trick) so this
    doesn't pay S1's real simulation cost."""
    root4, v4 = _follows_world_4b

    def _fast_s1(elig, rung_sets, grids, lambda_by_traj, *, n_sim):
        return {"arms": {"observed_lambda": {"Ts": [], "P_LEADS": 0.0}, "4.0": {}, "6.0": {},
                        "8.0": {}, "12.0": {}, "rms_lambda": {}},
                "order": [], "seed": 0, "n_sim": 0, "lambda_by_traj": {}}

    monkeypatch.setattr(power_ext_4b, "extension_arms_4b", _fast_s1)
    monkeypatch.setattr(levels_4b, "ladder_4b", lambda root4: {})
    monkeypatch.setattr(levels_4b, "twins_4b", lambda root4: {})
    monkeypatch.setattr(levels_4b, "ceiling_4b", lambda root4: {})
    monkeypatch.setattr(levels_4b, "within_family_4b", lambda root4: {})
    monkeypatch.setattr(levels_4b, "max_over_pairs_4b", lambda root4, cells4: {})

    real_check = an4b.check_imports_4b
    calls = {"n": 0}

    def _flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            return real_check()
        raise RuntimeError("synthetic check_imports_4b failure (test-injected, exit site)")

    monkeypatch.setattr(an4b, "check_imports_4b", _flaky)

    from experiments.exp4.tests import full_shape as fs
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, power_gate="full",
                tag_exists=lambda t: True, blob_sha=fs4b.blob_sha_4b,
                referents_sha=False, imports_pinned=True, frozen_check=lambda: None,
                expected_n_sim=fs.WORLD_POWER_N_SIM_4)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b import surface (exit)" in v["reason"], v["reason"]
    assert calls["n"] == 2, calls


@pytest.mark.slow
def test_gate5_fails_when_a_gate0_fraction_is_perturbed(_leads_world_4b, tmp_path):
    """Task 6: gate (5) had no perturbation test in `test_analyze_4b.py`
    (only gates 1-4 did) -- added here, same shape as its siblings."""
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    vp = battery_4.verdict_path(world)
    rec = json.loads(vp.read_text())
    traj = next(iter(rec["gate0"]))
    rec["gate0"][traj]["fraction_below"] = -1.0     # not a real fraction_below value
    vp.write_text(json.dumps(rec))
    v = an4b.run(root4b=tmp_path / "4b", root4=world, stop_before="placebo", **_run4b_kwargs())
    assert v["gates"]["5"]["pass"] is False
    assert v["gates"]["1"]["pass"] is True
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["reason"] == "4b: stopped before the placebo null (pre-tag tool run)"


# Mutation harness finding (Task 6): the perturbation tests above (and
# their siblings in test_analyze_4b.py) make each gate*_rederive_4b
# function return a NORMAL `pass=False` -- they never make it RAISE,
# so stripping run()'s OWN `collect_total_4b(lambda: gate1_rederive_4b
# (...), "4b gate N")` wrapper around the CALL changes nothing
# observable (a wrapped call that never raises behaves identically
# unwrapped). These four monkeypatch the gate function itself to
# raise, testing the WRAPPER specifically -- exp4's own cases 12/13/19
# precedent.

@pytest.mark.slow
def test_gate1_wrapper_catches_a_raise_from_gate1_rederive_4b(_leads_world_4b, tmp_path,
                                                               monkeypatch):
    root4, v4 = _leads_world_4b

    def _boom(*a, **k):
        raise RuntimeError("synthetic gate1_rederive_4b failure (test-injected)")

    monkeypatch.setattr(an4b, "gate1_rederive_4b", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b gate 1" in v["reason"]


@pytest.mark.slow
def test_gate2_wrapper_catches_a_raise_from_gate2_rederive_4b(_leads_world_4b, tmp_path,
                                                               monkeypatch):
    root4, v4 = _leads_world_4b

    def _boom(*a, **k):
        raise RuntimeError("synthetic gate2_rederive_4b failure (test-injected)")

    monkeypatch.setattr(an4b, "gate2_rederive_4b", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b gate 2" in v["reason"]


@pytest.mark.slow
def test_gate3_wrapper_catches_a_raise_from_gate3_rederive_4b(_leads_world_4b, tmp_path,
                                                               monkeypatch):
    root4, v4 = _leads_world_4b

    def _boom(*a, **k):
        raise RuntimeError("synthetic gate3_rederive_4b failure (test-injected)")

    monkeypatch.setattr(an4b, "gate3_rederive_4b", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b gate 3" in v["reason"]


@pytest.mark.slow
def test_gate5_wrapper_catches_a_raise_from_gate5_rederive_4b(_leads_world_4b, tmp_path,
                                                               monkeypatch):
    root4, v4 = _leads_world_4b

    def _boom(*a, **k):
        raise RuntimeError("synthetic gate5_rederive_4b failure (test-injected)")

    monkeypatch.setattr(an4b, "gate5_rederive_4b", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b gate 5" in v["reason"]


@pytest.mark.slow
def test_placebo_pool_raise_gives_insufficient_data(_leads_world_4b, tmp_path, monkeypatch):
    """The per-trajectory placebo-pool loop IS reached on "leads"
    (gates all pass; the design §4 floor only fires AFTER this loop) --
    monkeypatched to raise unconditionally rather than corrupting a
    file, since `placebo_pool_4b` reads `series_by_traj`/its own
    per-item arrays, both built together by ONE upstream call
    (`alignment_series_4`) with no separate file to desynchronize."""
    root4, v4 = _leads_world_4b

    def _boom(series, pia_t1, pia_end, flat, *, n_boot, seed):
        raise RuntimeError("synthetic placebo_pool_4b failure (test-injected)")

    monkeypatch.setattr(placebo_4b, "placebo_pool_4b", _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b placebo pool" in v["reason"]


# ============================================ "follows" world, placebo stage
#
# None of these sites has a committed FILE behind it to corrupt: the
# placebo null is computed fresh from already-validated exp4 data on
# every run, with no on-disk "placebo-stage input" of its own until
# AFTER it is computed (`placebo_4b.json`/`power_ext_4b.json` are
# outputs, written only when `write=True`). Each site is therefore
# probed the same way exp4's own never-naturally-raises sites are
# (`test_totality_4.py` cases 12/13/19): monkeypatch the underlying
# function to raise, confirm `collect_total_4b` catches it rather than
# letting it propagate out of `run()`.

_FOLLOWS_SITES = [
    (placebo_4b, "draw_batteries_4b", "4b draw batteries"),
    (placebo_4b, "p_cal_4b", "4b p_cal"),
    (placebo_4b, "t_star_4b", "4b t_star"),
    (placebo_4b, "alpha_placebo_4b", "4b alpha_placebo"),
    (placebo_4b, "per_traj_4b", "4b per_traj"),
    (placebo_4b, "per_type_4b", "4b per_type"),
    (placebo_4b, "s3_shape_4b", "4b S3"),
    (placebo_4b, "s4_scatter_ratio_4b", "4b S4"),
    (placebo_4b, "s5_autocorr_4b", "4b S5"),
    (placebo_4b, "s8_curves_4b", "4b S8"),
    (power_ext_4b, "extension_arms_4b", "4b S1"),
    (levels_4b, "ladder_4b", "4b S6"),
    (an4b, "clears_and_stays_cells_4b", "4b S7"),
]


@pytest.mark.slow
@pytest.mark.parametrize("mod,attr,needle", _FOLLOWS_SITES,
                         ids=[s[2].replace(" ", "_") for s in _FOLLOWS_SITES])
def test_follows_world_placebo_stage_raise_is_collected(_follows_world_4b, tmp_path, monkeypatch,
                                                         mod, attr, needle):
    root4, v4 = _follows_world_4b
    assert v4["verdict"] == "FOLLOWS", v4["reason"]

    def _boom(*a, **k):
        raise RuntimeError(f"synthetic {attr} failure (test-injected)")

    monkeypatch.setattr(mod, attr, _boom)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, power_gate="full", **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert needle in v["reason"], v["reason"]


@pytest.mark.slow
def test_gate6_failure_refuses_the_verdict_on_a_world_where_everything_else_passes(
        _leads_world_4b, tmp_path, monkeypatch):
    """FREEZE F-1, the mutant its own fast tests could not see: on an
    EMPTY `root4` every earlier gate already fails, so removing gate
    6's `failures.append(...)` leaves the verdict INSUFFICIENT_DATA
    anyway (`mutation_freeze.log`, mutant #43 SURVIVED the fast pass).
    Here gates 1-5 all PASS on the cached world and gate 6 is the ONLY
    thing wrong -- reported as a clean `pass=False`, not a raise, so
    this tests the REFUSAL, not the wrapper -- and the verdict must
    still be INSUFFICIENT_DATA naming gate 6. The placebo stage is
    never reached (gate 6 runs before it), so this costs one world copy
    plus one gate pass."""
    root4, v4 = _leads_world_4b

    def _fails(root):
        return {"pass": False, "per_traj": {}, "bad": [f"synthetic disagreement on {root}"],
                "n_rungs_checked": 0}

    monkeypatch.setattr(an4b, "gate6_endpoint_identity_4b", _fails)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "4b gate 6" in v["reason"], v["reason"]
    assert v["gates"]["6"]["pass"] is False
    for n in ("1", "2", "3", "4", "5"):
        assert v["gates"][n]["pass"] is True, (n, v["gates"][n])
