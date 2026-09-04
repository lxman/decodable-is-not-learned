# experiments/exp2m/tests/test_totality_2m.py
"""Verdict-path totality (2k's lineage, applied to 2m's own readers and
forced-exception injection sites): every tree `analyze_2m.run()` can be
handed must reach a FROZEN TERMINAL (INSUFFICIENT_DATA), never an
uncaught exception, plus the control (an untouched world still reaches
PYTHIA-ONLY).

Each `_insufficient` case asserts `v["verdict"] == "INSUFFICIENT_DATA"`
and the needle in the FULL `v["referents"]["failures"]` list (not
`v["reason"]`), `v["tests"] is None and v["secondaries"] is None`, and
never raises.

The `gate1.json`-a-directory case's needle differs from the
`gate1.json`-torn case's: a torn file reaches the `collect_total`-wrapped
`json.loads` inside `run()` (label `2m gate 1 smollm3_3b record`), while a
directory fails the earlier `g1p.is_file()` guard and is appended to
`failures` directly as `f"2m gate 1 smollm3_3b: record missing ({g1p})"` —
a different literal string (a colon separates `smollm3_3b` from `record`),
so the two cases cannot share one needle. Diagnosed by reading
`analyze_2m.run()`; no production code touched."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2g import battery_2g as bg
from experiments.exp2g import predictor_2g as pr
from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2k import analyze_2k as an2k
from experiments.exp2k import battery_2k as bk
from experiments.exp2m import analyze_2m as an
from experiments.exp2m import battery_2m as bm
from experiments.exp2m.tests import full_shape as fs

R0 = fs.bt.RUNGS[0]


@pytest.fixture(scope="module")
def base_world(tmp_path_factory):
    root = tmp_path_factory.mktemp("totality_base")
    seal = fs.write_world_2m(root, mode="pythia_only")
    return root, seal


@pytest.fixture
def world(base_world, tmp_path):
    root, seal = base_world
    shutil.copytree(root / "results", tmp_path / "results")
    return tmp_path, seal


def _run(root, seal, **kw):
    kw.setdefault("n_perm", 30)
    kw.setdefault("n_boot", 10)
    kw.setdefault("referents_sha", False)
    # Test-side correction (root cause: the brief's literal `_run` call
    # hardcodes `s8_loader=fs.s8_cached` as an explicit keyword AND
    # unpacks `**kw`, which raises "got multiple values for keyword
    # argument 's8_loader'" the moment a case passes s8_loader through
    # kw, as `test_s8_loader_forced_exception` below does. Defaulting it
    # through `kw.setdefault` instead keeps the same default for every
    # other case while letting that one case override it.
    kw.setdefault("s8_loader", fs.s8_cached)
    # Task 5: the frozen-module pin and the import pin both run for real
    # here now (FROZEN_SHA256_2M and IMPORTED_SHA256_2M are pinned), so
    # the bypasses this defaulted while they were empty are gone; only
    # `referents_sha=False` stays, because a synthetic tree is not the
    # real pre-campaign tree the manifest describes.
    return an.run(root_2m=root, root_2i=bi.EXP2I, root_2k=bk.EXP2K, **{**seal, **kw})


def _insufficient(root, seal, needle, **kw):
    v = _run(root, seal, **kw)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["verdict"]
    assert any(needle in f for f in v["referents"]["failures"]), v["referents"]["failures"]
    assert v["tests"] is None and v["secondaries"] is None
    return v


def _raise_injected(*a, **kw):
    raise ValueError("injected for a Task 4 totality test")


# ------------------------------------------------------------- rung set

def test_rung_set_torn(world):
    root, seal = world
    bm.rung_set_path(root).write_text('{"R_3B": [')
    _insufficient(root, seal, "2m rung set file")


def test_rung_set_is_a_list(world):
    root, seal = world
    bm.rung_set_path(root).write_text("[]")
    _insufficient(root, seal, "2m rung set file")


# ----------------------------------------------------------------- power

def test_power_record_torn(world):
    root, seal = world
    bm.power_path(root).write_text('{"A": {')
    _insufficient(root, seal, "2m power record")


# -------------------------------------------------------------- endpoint

def test_endpoint_record_is_a_list(world):
    root, seal = world
    bm.endpoint_record_path(root, "stage1_final", R0).write_text("[]")
    _insufficient(root, seal, "2m endpoint stage1_final")


def test_endpoint_record_bits_a_string(world):
    root, seal = world
    p = bm.endpoint_record_path(root, "stage1_final", R0)
    rec = json.loads(p.read_text())
    rec["bits"] = "abc"
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "2m endpoint stage1_final")


# ------------------------------------------------------------------ gate 1

def test_gate1_torn(world):
    root, seal = world
    bm.gate1_path(root).write_text('{"rungs": [')
    _insufficient(root, seal, "2m gate 1 smollm3_3b record")


def test_gate1_is_a_directory(world):
    root, seal = world
    p = bm.gate1_path(root)
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "2m gate 1 smollm3_3b: record missing")


def test_halt_marker_is_a_directory(world):
    root, seal = world
    bm.halt_marker_path(root).mkdir()
    _insufficient(root, seal, "2m gate 1 smollm3_3b halt marker read")


# -------------------------------------------------------------------- sweep

def test_sweep_record_torn(world):
    root, seal = world
    bm.record_path(root, 600000, "antonym").write_text('{"rung": "a')
    _insufficient(root, seal, "2m sweep smollm3_3b")


def test_sweep_step_directory_is_a_file(world):
    root, seal = world
    step_dir = bm.sweep_dir(root) / "step600000"
    shutil.rmtree(step_dir)
    step_dir.write_text("x")
    _insufficient(root, seal, "2m sweep smollm3_3b")


def test_checkpoint_record_sha256_a_string(world):
    root, seal = world
    p = bm.checkpoint_record_path(root, 600000)
    rec = json.loads(p.read_text())
    rec["sha256"] = "abc"
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "2m sweep smollm3_3b")


# ---------------------------------------------------- forced-exception sites

def test_load_manifest_3b_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(bm, "load_manifest_3b", _raise_injected)
    _insufficient(root, seal, "2m checkpoint manifest SmolLM3")


def test_upstream_frozen_import_thunk_forced_exception(world, monkeypatch):
    """Mutation closure (Task 5, #124): the five upstream frozen-pin
    thunks are called through one `collect_total` loop; a raise from any
    of them must be COLLECTED, not propagated."""
    root, seal = world
    monkeypatch.setattr(bg, "check_frozen_imports_2g", _raise_injected)
    _insufficient(root, seal, "2m upstream 2g frozen imports")


def test_load_battery_forced_exception(world, monkeypatch):
    """Mutation closure (Task 5, #110)."""
    root, seal = world
    monkeypatch.setattr(bg, "load_battery", _raise_injected)
    _insufficient(root, seal, "2m battery items")


def test_load_floors_forced_exception(world, monkeypatch):
    """Mutation closure (Task 5, #111)."""
    root, seal = world
    monkeypatch.setattr(bg, "load_floors", _raise_injected)
    _insufficient(root, seal, "2m floors 2d")


def test_load_verify_forced_exception(world, monkeypatch):
    """Mutation closure (Task 5, #112)."""
    root, seal = world
    monkeypatch.setattr(a2d, "load_verify", _raise_injected)
    _insufficient(root, seal, "2m verify criterion 3c")


def test_load_predictor_2g_forced_exception(world, monkeypatch):
    """Mutation closure (Task 5, #113): the strata source."""
    root, seal = world
    monkeypatch.setattr(pr, "load_predictor", _raise_injected)
    _insufficient(root, seal, "2m strata source 2g predictor")


def test_entry_which_3b_forced_exception(world, monkeypatch):
    """Mutation closure (Task 5, #126): the three endpoint entries."""
    root, seal = world
    monkeypatch.setattr(bm, "entry_which_3b", _raise_injected)
    _insufficient(root, seal, "2m SmolLM3 endpoint entries")


def test_load_tier_2k_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an2k, "load_tier_2k", _raise_injected)
    _insufficient(root, seal, "2m predictor 2k tier 1b load")


def test_sampler_counts_olmo_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(bi, "sampler_counts_olmo", _raise_injected)
    _insufficient(root, seal, "2m predictor x_B counts olmo1b")


def test_load_predictor_records_2i_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an2i, "load_predictor_records_2i", _raise_injected)
    _insufficient(root, seal, "2m predictor 2i olmo1b records")


def test_endpoint_sha256_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(bm, "endpoint_sha256", _raise_injected)
    _insufficient(root, seal, "2m endpoint composite sha")


def test_outcomes_3b_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an, "outcomes_3b", _raise_injected)
    _insufficient(root, seal, "2m primary smollm3_3b")


def test_check_power_claims_2m_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an, "check_power_claims_2m", _raise_injected)
    _insufficient(root, seal, "2m power claims")


def test_gate1_rederive_3b_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(bm, "gate1_rederive_3b", _raise_injected)
    _insufficient(root, seal, "2m gate 1 smollm3_3b re-derivation")


def test_tag_exists_raising(world):
    root, seal = world

    def _raising_tag_exists(t):
        raise RuntimeError("injected for a Task 4 totality test")

    _insufficient(root, seal, "2m endpoint seal binding", tag_exists=_raising_tag_exists)


def test_2k_predictor_halt_marker_present(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(bk, "halt_markers", lambda root_2k: [Path("x/y.HALTED")])
    _insufficient(root, seal, "2m predictor 2k tier HALTED marker present")


def test_rung_set_vs_endpoint_check_forced_exception(world, monkeypatch):
    """Mutation gap (Task 5, #100): _check_rung_set_vs_endpoint_2m reads
    a rung_set AND a stage1_final that are always well-formed on the
    real committed 2k/2i data path -- reachable only once both are
    present, which only a complete synthetic SmolLM3 tree provides."""
    root, seal = world
    monkeypatch.setattr(an, "_check_rung_set_vs_endpoint_2m",
                        lambda *a, **kw: (_ for _ in ()).throw(ValueError("injected")))
    _insufficient(root, seal, "2m rung set vs endpoint")


def test_rung_set_derivation_check_forced_exception(world, monkeypatch):
    """Mutation gap (Task 5, #108): same shape as #100, one check over."""
    root, seal = world
    monkeypatch.setattr(an, "_check_rung_set_derivation_2m",
                        lambda *a, **kw: (_ for _ in ()).throw(ValueError("injected")))
    _insufficient(root, seal, "2m rung set re-derivation")


def test_check_imports_2m_exit_forced_exception(world, monkeypatch):
    """Mutation gap (Task 5, #104): the EXIT import-surface re-check
    only runs once the core (A/B) has computed cleanly -- reachable
    only on a fully successful (PYTHIA-ONLY-firing) world, unlike the
    ENTRY check the FAST suite already exercises. A call-counting mock
    lets the ENTRY call through so the pipeline reaches `core`, then
    fails only the second (exit) call.

    Test-side correction (root cause, found running the FULL suite
    rather than this file alone): the brief's `real = an.
    check_imports_2m; ... return real()` pattern depends on the REAL
    `check_imports_2m()` succeeding on the passing calls, which in turn
    depends on which OTHER `experiments/*` modules already sit in
    `sys.modules` -- a property of pytest's collection order across
    the WHOLE `experiments/exp2m/tests` suite (e.g. `test_stages_2m.py`
    importing `run/preflight_2m.py`, not yet covered before Task 5),
    not of this file in isolation, where it passed. What these two
    cases exist to exercise is `run()`'s CALL-SITE SEQUENCING (entry ->
    exit -> post-secondaries) -- Task 5/the freeze's target -- not
    `check_imports_2m`'s own correctness, so the passing calls are a
    plain no-op and `imports_pinned=True` is passed explicitly (Task 5
    pinned IMPORTED_SHA256_2M, so this now agrees with the default; it
    is kept to state the intent at the call site)."""
    root, seal = world
    calls = {"n": 0}

    def _flaky():
        calls["n"] += 1
        if calls["n"] >= 2:
            raise ValueError("injected for a Task 5 totality test")
        return None

    monkeypatch.setattr(an, "check_imports_2m", _flaky)
    v = _run(root, seal, n_perm=200, n_boot=20, imports_pinned=True)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert any("2m import surface (exit)" in f for f in v["referents"]["failures"])


def test_rung_set_endpoint_shas_check_forced_exception(world, monkeypatch):
    """FREEZE F-3's call site: reachable only once the rung set loads,
    which only a complete synthetic SmolLM3 tree provides."""
    root, seal = world
    monkeypatch.setattr(an, "_check_rung_set_endpoint_shas_2m",
                        lambda *a, **kw: (_ for _ in ()).throw(ValueError("injected")))
    _insufficient(root, seal, "2m rung set endpoint shas")


def test_check_imports_2m_post_secondaries_forced_exception(world, monkeypatch):
    """FREEZE F-1's call site: the THIRD `check_imports_2m` call, after
    the secondaries. A call-counting mock lets the entry and exit calls
    through so the pipeline reaches the secondaries, then fails only the
    third — the frozen refusal terminal must still be delivered, with the
    tests and secondaries withdrawn.

    Same test-side correction as `test_check_imports_2m_exit_forced_
    exception` above, for the same reason (found in the full-suite run,
    not this file alone)."""
    root, seal = world
    calls = {"n": 0}

    def _flaky():
        calls["n"] += 1
        if calls["n"] >= 3:
            raise ValueError("injected for a freeze totality test")
        return None

    monkeypatch.setattr(an, "check_imports_2m", _flaky)
    v = _run(root, seal, n_perm=200, n_boot=20, imports_pinned=True)
    assert calls["n"] == 3
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert any("2m import surface (post-secondaries)" in f for f in v["referents"]["failures"])
    assert v["tests"] is None and v["secondaries"] is None


def test_secondary_computation_forced_exception(world, monkeypatch):
    """Mutation gap (Task 5, #110): `_sec`'s own collect_total wrapping
    -- shared by all thirteen-odd named secondaries -- is reachable
    only once `core` has computed, same as #104. A failing secondary
    must be recorded gracefully (sec[name]["failed"]), not crash run()."""
    root, seal = world
    monkeypatch.setattr(an2k, "ladder_2k",
                        lambda *a, **kw: (_ for _ in ()).throw(ValueError("injected for a Task 5 totality test")))
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "PYTHIA-ONLY", v["reason"]      # the main verdict is unaffected
    assert v["secondaries"]["failures"] and any("injected" in f for f in v["secondaries"]["failures"])
    assert v["secondaries"]["S1 ladder 1b"]["failed"] is not None


# -------------------------------------------------------------------- twin

def test_twin_record_torn(world):
    root, seal = world
    bm.record_path(root, bm.TWIN, "antonym").write_text('{"rung": "a')
    _insufficient(root, seal, "2m sweep smollm3_3b")


# ------------------------------------------------------------------ stage3

def test_stage3_endpoint_record_is_a_list(world):
    root, seal = world
    bm.endpoint_record_path(root, "stage3_final", R0).write_text("[]")
    _insufficient(root, seal, "2m endpoint stage3_final")


# ------------------------------------------------------------------------ S8

def test_s8_loader_forced_exception(world):
    """A failing S8 descriptive never moves the verdict (same shape as
    `test_secondary_computation_forced_exception`, above, but through
    the `s8_loader` injection point rather than a monkeypatched upstream
    reader)."""
    root, seal = world
    v = _run(root, seal, n_perm=200, n_boot=20, s8_loader=_raise_injected)
    assert v["verdict"] == "PYTHIA-ONLY", v["reason"]
    assert v["secondaries"]["S8 outcome order"]["failed"] is not None


# ------------------------------------------------------------------ control

def test_untouched_world_still_reaches_pythia_only(world):
    """n_perm=30's permutation p-value floor can never clear ALPHA
    regardless of T; only the control needs resolution enough to
    actually fire (2i's/2j's/2k's own totality control tests, same
    reason)."""
    root, seal = world
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "PYTHIA-ONLY", v["reason"]
    assert v["tests"]["A"]["fires"] is True
