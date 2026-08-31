# experiments/exp2l/tests/test_totality_2l.py
"""Verdict-path totality (2k's lineage, applied to 2l's own readers and
forced-exception injection sites): every tree `analyze_2l.run()` can be
handed must reach a FROZEN TERMINAL (INSUFFICIENT_DATA), never an
uncaught exception, plus the control (an untouched world still reaches
SHARED).

Each `_insufficient` case asserts `v["verdict"] == "INSUFFICIENT_DATA"`
and the needle in the FULL `v["referents"]["failures"]` list (not
`v["reason"]`), `v["tests"] is None and v["secondaries"] is None`, and
never raises.

The `gate1.json`-a-directory case's needle differs from the
`gate1.json`-torn case's: a torn file reaches the `collect_total`-wrapped
`json.loads` inside `run()` (label `2l gate 1 olmo13b record`), while a
directory fails the earlier `g1p.is_file()` guard and is appended to
`failures` directly as `f"2l gate 1 olmo13b: record missing ({g1p})"` —
a different literal string (a colon separates `olmo13b` from `record`),
so the two cases cannot share one needle. Diagnosed by reading
`analyze_2l.run()`; no production code touched."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2k import analyze_2k as an2k
from experiments.exp2k import battery_2k as bk
from experiments.exp2l import analyze_2l as an
from experiments.exp2l import battery_2l as bl
from experiments.exp2l.tests import full_shape as fs

R0 = fs.bt.RUNGS[0]


@pytest.fixture(scope="module")
def base_world(tmp_path_factory):
    root = tmp_path_factory.mktemp("totality_base")
    seal = fs.write_world_2l(root, mode="a_only")
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
    # Task 5 dropped the imports_pinned=False and frozen_check=lambda: None
    # bypasses that used to default here: IMPORTED_SHA256_2L and
    # FROZEN_SHA256_2L are both pinned now, so the real checks run in
    # every totality case (a synthetic 13B tree under `root` does not
    # change which modules are imported or whether the frozen files on
    # disk still match their pins).
    return an.run(root_2l=root, root_2i=bi.EXP2I, root_2k=bk.EXP2K, **{**seal, **kw})


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
    bl.rung_set_path(root).write_text('{"R_13B": [')
    _insufficient(root, seal, "2l rung set file")


def test_rung_set_is_a_list(world):
    root, seal = world
    bl.rung_set_path(root).write_text("[]")
    _insufficient(root, seal, "2l rung set file")


# ----------------------------------------------------------------- power

def test_power_record_torn(world):
    root, seal = world
    bl.power_path(root).write_text('{"A": {')
    _insufficient(root, seal, "2l power record")


# -------------------------------------------------------------- endpoint

def test_endpoint_record_is_a_list(world):
    root, seal = world
    bl.endpoint_record_path(root, "stage1_final", R0).write_text("[]")
    _insufficient(root, seal, "2l endpoint stage1_final")


def test_endpoint_record_bits_a_string(world):
    root, seal = world
    p = bl.endpoint_record_path(root, "stage1_final", R0)
    rec = json.loads(p.read_text())
    rec["bits"] = "abc"
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "2l endpoint stage1_final")


# ------------------------------------------------------------------ gate 1

def test_gate1_torn(world):
    root, seal = world
    bl.gate1_path(root).write_text('{"rungs": [')
    _insufficient(root, seal, "2l gate 1 olmo13b record")


def test_gate1_is_a_directory(world):
    root, seal = world
    p = bl.gate1_path(root)
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "2l gate 1 olmo13b: record missing")


def test_halt_marker_is_a_directory(world):
    root, seal = world
    bl.halt_marker_path(root).mkdir()
    _insufficient(root, seal, "2l gate 1 olmo13b halt marker read")


# -------------------------------------------------------------------- sweep

def test_sweep_record_torn(world):
    root, seal = world
    bl.record_path(root, 64000, "antonym").write_text('{"rung": "a')
    _insufficient(root, seal, "2l sweep olmo13b")


def test_sweep_step_directory_is_a_file(world):
    root, seal = world
    step_dir = bl.sweep_dir(root) / "step64000"
    shutil.rmtree(step_dir)
    step_dir.write_text("x")
    _insufficient(root, seal, "2l sweep olmo13b")


def test_checkpoint_record_sha256_a_string(world):
    root, seal = world
    p = bl.checkpoint_record_path(root, 64000)
    rec = json.loads(p.read_text())
    rec["sha256"] = "abc"
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "2l sweep olmo13b")


# ---------------------------------------------------- forced-exception sites

def test_load_manifest_13b_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(bl, "load_manifest_13b", _raise_injected)
    _insufficient(root, seal, "2l checkpoint manifest 13B")


def test_load_tier_2k_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an2k, "load_tier_2k", _raise_injected)
    _insufficient(root, seal, "2l predictor 2k tier 1b load")


def test_sampler_counts_olmo_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(bi, "sampler_counts_olmo", _raise_injected)
    _insufficient(root, seal, "2l predictor x_B counts olmo1b")


def test_load_predictor_records_2i_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an2i, "load_predictor_records_2i", _raise_injected)
    _insufficient(root, seal, "2l predictor 2i olmo1b records")


def test_endpoint_sha256_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(bl, "endpoint_sha256", _raise_injected)
    _insufficient(root, seal, "2l endpoint composite sha")


def test_outcomes_13b_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an, "outcomes_13b", _raise_injected)
    _insufficient(root, seal, "2l primary olmo13b")


def test_check_power_claims_2l_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an, "check_power_claims_2l", _raise_injected)
    _insufficient(root, seal, "2l power claims")


def test_gate1_rederive_13b_forced_exception(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(bl, "gate1_rederive_13b", _raise_injected)
    _insufficient(root, seal, "2l gate 1 olmo13b re-derivation")


def test_tag_exists_raising(world):
    root, seal = world

    def _raising_tag_exists(t):
        raise RuntimeError("injected for a Task 4 totality test")

    _insufficient(root, seal, "2l endpoint seal binding", tag_exists=_raising_tag_exists)


def test_2k_predictor_halt_marker_present(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(bk, "halt_markers", lambda root_2k: [Path("x/y.HALTED")])
    _insufficient(root, seal, "2l predictor 2k tier HALTED marker present")


def test_rung_set_vs_endpoint_check_forced_exception(world, monkeypatch):
    """Mutation gap (Task 5, #100): _check_rung_set_vs_endpoint_2l reads
    a rung_set AND a stage1_final that are always well-formed on the
    real committed 2k/2i data path -- reachable only once both are
    present, which only a complete synthetic 13B tree provides."""
    root, seal = world
    monkeypatch.setattr(an, "_check_rung_set_vs_endpoint_2l",
                        lambda *a, **kw: (_ for _ in ()).throw(ValueError("injected")))
    _insufficient(root, seal, "2l rung set vs endpoint")


def test_rung_set_derivation_check_forced_exception(world, monkeypatch):
    """Mutation gap (Task 5, #108): same shape as #100, one check over."""
    root, seal = world
    monkeypatch.setattr(an, "_check_rung_set_derivation_2l",
                        lambda *a, **kw: (_ for _ in ()).throw(ValueError("injected")))
    _insufficient(root, seal, "2l rung set re-derivation")


def test_check_imports_2l_exit_forced_exception(world, monkeypatch):
    """Mutation gap (Task 5, #104): the EXIT import-surface re-check
    only runs once the core (A/B) has computed cleanly -- reachable
    only on a fully successful (SHARED-firing) world, unlike the ENTRY
    check the FAST suite already exercises. A call-counting mock lets
    the ENTRY call through so the pipeline reaches `core`, then fails
    only the second (exit) call."""
    root, seal = world
    calls = {"n": 0}
    real = an.check_imports_2l

    def _flaky():
        calls["n"] += 1
        if calls["n"] >= 2:
            raise ValueError("injected for a Task 5 totality test")
        return real()

    monkeypatch.setattr(an, "check_imports_2l", _flaky)
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert any("2l import surface (exit)" in f for f in v["referents"]["failures"])


def test_secondary_computation_forced_exception(world, monkeypatch):
    """Mutation gap (Task 5, #110): `_sec`'s own collect_total wrapping
    -- shared by all thirteen-odd named secondaries -- is reachable
    only once `core` has computed, same as #104. A failing secondary
    must be recorded gracefully (sec[name]["failed"]), not crash run()."""
    root, seal = world
    monkeypatch.setattr(an2k, "ladder_2k",
                        lambda *a, **kw: (_ for _ in ()).throw(ValueError("injected for a Task 5 totality test")))
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "SHARED", v["reason"]      # the main verdict is unaffected
    assert v["secondaries"]["failures"] and any("injected" in f for f in v["secondaries"]["failures"])
    assert v["secondaries"]["S1 ladder 1b"]["failed"] is not None


# ------------------------------------------------------------------ control

def test_untouched_world_still_reaches_shared(world):
    """n_perm=30's permutation p-value floor can never clear ALPHA
    regardless of T; only the control needs resolution enough to
    actually fire (2i's/2j's/2k's own totality control tests, same
    reason)."""
    root, seal = world
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "SHARED", v["reason"]
    assert v["tests"]["A"]["fires"] is True
