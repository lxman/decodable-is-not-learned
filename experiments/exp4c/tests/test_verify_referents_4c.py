# experiments/exp4c/tests/test_verify_referents_4c.py
"""Fix round 2, item 5: `verify_referents_4c.py`'s item 11 (`_c11`)
compares `results/power_4c.json` to a fresh `power_4c.compute()` the
same way `analyze_4c._reproduce_power_4c` does — restricted to the
keys `rec2` happens to have, so an extra committed key passed silently
before the byte comparison ever ran. `_c1` is exercised separately
(item 3) by the real cold battery, not here, since its whole point is
verifying the REAL committed 68-file pin set — a fast test would just
duplicate `bc.check_frozen_4c()`'s own coverage."""
from __future__ import annotations

import json

import pytest

from experiments.exp4c import verify_referents_4c as vr


def test_c11_catches_an_extra_key_in_the_committed_power_record(tmp_path, monkeypatch):
    monkeypatch.setattr(vr, "EXP4C", tmp_path)
    structure = vr.pw4c.cell_structure_4c()
    rec = vr.pw4c.compute(structure, n_sim=50, seed=0)
    rec["a_key_compute_never_produces"] = 1
    results = tmp_path / "results"
    results.mkdir()
    (results / "power_4c.json").write_text(json.dumps(rec))
    with pytest.raises(AssertionError, match="a_key_compute_never_produces"):
        vr._c11({})


def test_c11_catches_a_missing_key_in_the_committed_power_record(tmp_path, monkeypatch):
    monkeypatch.setattr(vr, "EXP4C", tmp_path)
    structure = vr.pw4c.cell_structure_4c()
    rec = vr.pw4c.compute(structure, n_sim=50, seed=0)
    del rec["arms"]
    results = tmp_path / "results"
    results.mkdir()
    (results / "power_4c.json").write_text(json.dumps(rec))
    with pytest.raises(AssertionError, match="arms"):
        vr._c11({})


def test_c11_skips_when_no_power_record_is_on_disk(tmp_path, monkeypatch):
    monkeypatch.setattr(vr, "EXP4C", tmp_path)
    assert vr._c11({}) == "SKIP"


# --------- FINAL REVIEW minor: item 6's 40 digests must be PAIRWISE DISTINCT

def _digest_stub_4c(mapping, default="a" * 64):
    def _d(traj, step):
        return mapping.get((traj, step), default)
    return _d


def _all_steps_4c():
    return [(traj, step) for traj in vr.bc.TRAJECTORIES_4C
            for step in (vr.bc.INIT_STEP_4C,) + tuple(vr.bc.GRID_4C[traj])]


def test_c6_passes_when_every_committed_digest_is_distinct(monkeypatch):
    steps = _all_steps_4c()
    assert len(steps) == 40
    mapping = {k: f"{i:064x}" for i, k in enumerate(steps)}
    monkeypatch.setattr(vr.bc, "committed_step_digest_4c", _digest_stub_4c(mapping))
    vr._c6({})


def test_c6_catches_a_unit_copied_from_one_step_to_another(monkeypatch):
    """A copied unit carries a digest that matches its OWN record, so
    every pin in the analyzer passes; only the pairwise comparison
    across the 40 committed checkpoints sees it."""
    steps = _all_steps_4c()
    mapping = {k: f"{i:064x}" for i, k in enumerate(steps)}
    mapping[steps[7]] = mapping[steps[3]]          # step 7's unit copied from step 3
    monkeypatch.setattr(vr.bc, "committed_step_digest_4c", _digest_stub_4c(mapping))
    with pytest.raises(AssertionError, match="shared by more than one step"):
        vr._c6({})


def test_c6_still_catches_a_malformed_digest(monkeypatch):
    monkeypatch.setattr(vr.bc, "committed_step_digest_4c", _digest_stub_4c({}, default="short"))
    with pytest.raises(AssertionError, match="not 64 hex chars"):
        vr._c6({})


# ------- FINAL REVIEW minor: item 12 decides its SKIP PER TRAJECTORY

def _c12_stubs_4c(monkeypatch, root, *, passes=True):
    from experiments.exp4 import collect_4
    from experiments.exp4c import analyze_4c as an4c
    monkeypatch.setattr(vr.bc, "EXP4C", root)
    monkeypatch.setattr(collect_4, "load_ref_tables_4",
                        lambda root4, refs: {r: {"sets": {}} for r in refs})
    monkeypatch.setattr(an4c, "_load_one_unit_4c", lambda root_, key: {"record": {}})
    monkeypatch.setattr(an4c, "gate0_4c",
                        lambda *a, **k: {"pass": passes, "fraction_below": 0.955,
                                         "n_cells": 100, "n_cells_excluded": 4})


def _make_sweep_dirs_4c(root, traj):
    for step in (vr.bc.INIT_STEP_4C, vr.bc.ENDPOINT_STEP_4C[traj]):
        vr.battery_4.unit_dir(root, traj, step).mkdir(parents=True, exist_ok=True)


def test_c12_skips_only_while_neither_run_is_on_disk(tmp_path, monkeypatch):
    _c12_stubs_4c(monkeypatch, tmp_path)
    assert vr._c12({}) == "SKIP"


def test_c12_checks_the_complete_run_while_the_other_is_still_absent(tmp_path, monkeypatch,
                                                                    capsys):
    """Between the two sweeps (6.9b complete, 13B not) the item used to
    decide its SKIP from `TRAJECTORIES_4C[0]` and then loop BOTH — so
    it reported a gate-0 FAILURE for a run that had not been collected
    at all."""
    done, todo = vr.bc.TRAJECTORIES_4C
    _make_sweep_dirs_4c(tmp_path, done)
    _c12_stubs_4c(monkeypatch, tmp_path)
    assert vr._c12({}) is None                     # ran, did not skip, did not raise
    printed = capsys.readouterr().out
    assert f"{done} 0.9550" in printed
    assert f"{todo} SKIP (sweep not run)" in printed


def test_c12_checks_the_second_trajectory_when_only_it_is_on_disk(tmp_path, monkeypatch,
                                                                  capsys):
    first, second = vr.bc.TRAJECTORIES_4C
    _make_sweep_dirs_4c(tmp_path, second)
    _c12_stubs_4c(monkeypatch, tmp_path)
    assert vr._c12({}) is None
    printed = capsys.readouterr().out
    assert f"{second} 0.9550" in printed and f"{first} SKIP (sweep not run)" in printed


def test_c12_still_fails_when_a_present_run_misses_gate_0(tmp_path, monkeypatch):
    done = vr.bc.TRAJECTORIES_4C[0]
    _make_sweep_dirs_4c(tmp_path, done)
    _c12_stubs_4c(monkeypatch, tmp_path, passes=False)
    with pytest.raises(AssertionError, match="gate 0"):
        vr._c12({})
