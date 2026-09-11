# experiments/exp4/tests/test_stages_4.py
"""The exp4 stage runners' control flow with FAKE loaders — no torch,
no network, no real checkpoint tree touched. `battery_4.RUNGS` (all 34)
is exercised on every load (it's a hardcoded loop inside `collect_4
.process_model_4`), backed by a tiny synthetic 12-item-per-rung battery
so a FakeModel-based unit exercises the real k-NN machinery (k=10 needs
n > 10) without real-battery cost. The four trajectories' grids are
shrunk to three points (1000/2000/3000) so the sweep tests run fast;
`committed_step_digest_4`/`committed_init_digest_4` are faked entirely
(no dependency on any real exp2g/2i/2m/2n committed tree)."""
from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp4 import battery_4
from experiments.exp4 import collect_4 as c4
from experiments.exp4.run import preflight_4 as pf
from experiments.exp4.run import reference_4 as rf
from experiments.exp4.run import sweep_4 as sw
from experiments.exp4.tests import fakes_4


# ------------------------------------------------------------- fixtures

@pytest.fixture(autouse=True)
def _blobs_that_exist(monkeypatch):
    subset = tuple(r for r in battery_4.INSTRUMENT_BLOBS_4 if (battery_4.REPO / r).is_file())
    monkeypatch.setattr(battery_4, "INSTRUMENT_BLOBS_4", subset)


def _fake_prereg():
    def blob_sha(tag, rel):
        p = battery_4.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None
    return dict(tag_exists=lambda t: True, blob_sha=blob_sha)


def _fake_auth(seal_tag_exists=True):
    """`require_prereg_4` and `require_reference_seal_4` share ONE
    `tag_exists` argument on `sweep_4.run` — differentiated here by the
    tag string each check passes (`PREREG_TAG_4` vs
    `REFERENCE_SEAL_TAG_4`), so a test can make the prereg tag exist
    while the reference seal tag does not (or vice-versa)."""
    def tag_exists(t):
        if t == battery_4.REFERENCE_SEAL_TAG_4:
            return seal_tag_exists
        return True
    return dict(tag_exists=tag_exists, blob_sha=_fake_prereg()["blob_sha"],
               blobs_bound=lambda tag, paths, repo_root=None: [])


def _shrink_all_grids(monkeypatch):
    grid = {traj: (1000, 2000, 3000) for traj in battery_4.TRAJECTORIES_4}
    endpoint = {traj: 3000 for traj in battery_4.TRAJECTORIES_4}
    first = {traj: 1000 for traj in battery_4.TRAJECTORIES_4}
    monkeypatch.setattr(battery_4, "GRID_4", grid)
    monkeypatch.setattr(battery_4, "ENDPOINT_STEP_4", endpoint)
    monkeypatch.setattr(battery_4, "FIRST_STEP_4", first)
    monkeypatch.setattr(battery_4, "STAGE1_FIRST_UNITS_4",
                        tuple((traj, first[traj]) for traj in battery_4.TRAJECTORIES_4))


_WORDS = ["cat", "dog", "blue", "fast", "moon", "tree", "gold", "iron", "leaf", "wave",
         "frost", "spark", "amber", "cliff", "delta", "ember", "quartz", "willow"]


def _tiny_battery(n=12):
    """12+ varied items per rung (k=10 needs n > k): a fixed-seed
    `random.Random` per rung picks a distinct word phrase per item so
    FakeModel's per-character embeddings don't collapse into
    near-duplicate rows (a degenerate CKA kernel otherwise, on such
    small synthetic prompts)."""
    import random
    battery = {}
    for r in battery_4.RUNGS:
        rng = random.Random(r)
        items = [{"question": " ".join(rng.choice(_WORDS) for _ in range(4)) + f" {i}",
                 "answer": str(i)} for i in range(n)]
        battery[r] = {"shots": [["amber cliff quartz willow", "2"], ["delta ember frost spark", "4"]],
                     "eval_items": items}
    return battery


def _n_hidden_by():
    out = dict(battery_4.N_HIDDEN_PIN_4)
    for traj in battery_4.TRAJECTORIES_4:
        out[traj] = battery_4.N_HIDDEN_PIN_4[f"endpoint_{traj}"]
    return out


class _Seeds:
    """Assigns every fake-loader-reachable key/unit a distinct seed and
    builds the matching `committed_step_digest_4`/`committed_init_digest_4`
    tables from those seeds' `fake_digest`, so a real loader call and the
    'committed' pin agree by construction unless a test deliberately
    perturbs one side."""

    def __init__(self):
        self.seed_by_key = {}
        self._next = 1000
        for ref in battery_4.REFERENCES_4:
            self._assign(ref)
        for traj in battery_4.TRAJECTORIES_4:
            self._assign(f"endpoint_{traj}")
            self._assign((traj, battery_4.FIRST_STEP_4[traj]))
            self._assign(battery_4.INIT_KEY_4[traj])
        for size in battery_4.LADDER_SIZES_4:
            if size != "12b":
                self._assign(f"ladder_pythia_{size}")
        # sweep steps: 2000 gets its own seed per traj; 3000 (the
        # endpoint) reuses the reference stage's endpoint_<traj> seed
        # (same real weights, a different loader path).
        for traj in battery_4.TRAJECTORIES_4:
            self._assign((traj, 2000))
            self.seed_by_key[(traj, 3000)] = self.seed_by_key[f"endpoint_{traj}"]

    def _assign(self, key):
        self.seed_by_key[key] = self._next
        self._next += 1

    def step_digest(self, traj, step):
        return fakes_4.fake_digest(self.seed_by_key[(traj, int(step))])

    def init_digest(self, traj):
        return fakes_4.fake_digest(self.seed_by_key[battery_4.INIT_KEY_4[traj]])

    def loaders(self):
        return fakes_4.fake_loaders(self.seed_by_key, n_hidden_by=_n_hidden_by())


def _install_digests(monkeypatch, seeds: _Seeds):
    monkeypatch.setattr(battery_4, "committed_step_digest_4", seeds.step_digest)
    monkeypatch.setattr(battery_4, "committed_init_digest_4", seeds.init_digest)


# ---------------------------------------------------------------- prereg

def test_reference_refuses_without_prereg_tag(tmp_path):
    with pytest.raises(RuntimeError, match="does not exist"):
        rf.run(root=tmp_path, loaders={}, tag_exists=lambda t: False,
              blob_sha=lambda tag, rel: None)


def test_reference_dry_run_loads_nothing(tmp_path, monkeypatch):
    _shrink_all_grids(monkeypatch)
    seeds = _Seeds()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4.run.reference_4.bt.load_battery", _tiny_battery)
    rf.run(root=tmp_path, dry_run=True, loaders=seeds.loaders(), **_fake_prereg())
    assert not (tmp_path / "results").exists()


# -------------------------------------------------- full reference stage

def _run_full_reference(tmp_path, monkeypatch):
    _shrink_all_grids(monkeypatch)
    seeds = _Seeds()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4.run.reference_4.bt.load_battery", _tiny_battery)
    written = {}

    def eligibility_fn(root):
        written["called"] = True
        return {"cells": []}

    rf.run(root=tmp_path, loaders=seeds.loaders(), eligibility_fn=eligibility_fn, **_fake_prereg())
    return seeds, written


def test_reference_runs_all_23_in_order_and_layout_is_complete(tmp_path, monkeypatch):
    seeds, written = _run_full_reference(tmp_path, monkeypatch)

    for key in battery_4.STAGE1_KEYS_4:
        assert battery_4.unit_complete_4(tmp_path, key), key
    for traj, step in battery_4.STAGE1_FIRST_UNITS_4:
        assert battery_4.unit_complete_4(tmp_path, (traj, step)), (traj, step)

    # the ladder's "12b" size is the ref_pythia_12b reference, not its
    # own ladder unit
    assert not (battery_4.reference_dir(tmp_path, "ladder_pythia_12b")).exists()
    assert battery_4.unit_complete_4(tmp_path, "ref_pythia_12b")

    # references get a global bank; a first unit does not
    assert battery_4.global_sets_path(tmp_path, "ref_pythia_12b").is_file()
    assert not (battery_4.unit_dir(tmp_path, "pythia_2.8b", 1000) / "global.npz").exists()

    # every reference-stage record stamps the prereg tag
    rec = json.loads(battery_4.load_record_path(tmp_path, "ref_pythia_12b").read_text())
    assert rec["prereg_tag"] == battery_4.PREREG_TAG_4

    assert written["called"] is True
    assert battery_4.eligibility_path(tmp_path).is_file()
    assert json.loads(battery_4.eligibility_path(tmp_path).read_text()) == {"cells": []}


def test_reference_skip_if_complete_is_idempotent(tmp_path, monkeypatch):
    seeds, _ = _run_full_reference(tmp_path, monkeypatch)
    before = battery_4.load_record_path(tmp_path, "ref_pythia_12b").read_text()

    def boom_battery():
        raise AssertionError("load_battery should not be needed again for a fully-complete run")

    # a second run with a loaders dict that explodes on any model call
    # proves nothing gets re-loaded
    def explode(*a, **k):
        raise AssertionError("no key should be re-loaded once complete")
    exploding_loaders = {"key": explode, "step": explode, "free_step": lambda *a, **k: None,
                         "release": lambda m: None}
    rf.run(root=tmp_path, loaders=exploding_loaders, eligibility_fn=lambda root: {"cells": []},
          **_fake_prereg())
    after = battery_4.load_record_path(tmp_path, "ref_pythia_12b").read_text()
    assert before == after


def test_cross_reference_4_fills_every_ref_with_three_others(tmp_path, monkeypatch):
    _run_full_reference(tmp_path, monkeypatch)
    for ref in battery_4.REFERENCES_4:
        align = json.loads(battery_4.align_path(tmp_path, ref).read_text())
        one_rung = next(iter(align.values()))
        assert set(one_rung) == {r for r in battery_4.REFERENCES_4 if r != ref}


def test_endpoint_digest_mismatch_halts_with_no_record(tmp_path, monkeypatch):
    _shrink_all_grids(monkeypatch)
    seeds = _Seeds()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4.run.reference_4.bt.load_battery", _tiny_battery)

    # complete only the four references first (endpoints need REFS_FOR_4
    # on disk; `only=` targets one key at a time)
    for ref in battery_4.REFERENCES_4:
        rf.run(root=tmp_path, loaders=seeds.loaders(), only=ref, **_fake_prereg())
        assert battery_4.unit_complete_4(tmp_path, ref)
    assert not battery_4.unit_complete_4(tmp_path, "endpoint_pythia_2.8b")

    # the loader is unchanged (still the real seed); the committed pin
    # disagrees with it
    def wrong_step_digest(traj, step):
        if traj == "pythia_2.8b" and int(step) == battery_4.ENDPOINT_STEP_4["pythia_2.8b"]:
            return "not-the-real-digest"
        return seeds.step_digest(traj, step)
    monkeypatch.setattr(battery_4, "committed_step_digest_4", wrong_step_digest)

    with pytest.raises(SystemExit) as ei:
        rf.run(root=tmp_path, loaders=seeds.loaders(), only="endpoint_pythia_2.8b", **_fake_prereg())
    assert ei.value.code == 2
    assert c4.reference_halt_marker_path(tmp_path).is_file()
    assert not battery_4.load_record_path(tmp_path, "endpoint_pythia_2.8b").is_file()


def test_init_twin_digest_mismatch_halts(tmp_path, monkeypatch):
    _shrink_all_grids(monkeypatch)
    seeds = _Seeds()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4.run.reference_4.bt.load_battery", _tiny_battery)
    rf.run(root=tmp_path, loaders=seeds.loaders(), **_fake_prereg())  # full run completes everything

    # wipe the init's record so it looks pending again, then make the
    # committed pin (only) disagree with the unchanged loader
    twin_key = battery_4.INIT_KEY_4["olmo2_7b"]
    (battery_4.reference_dir(tmp_path, twin_key) / "_load.json").unlink()
    assert not battery_4.unit_complete_4(tmp_path, twin_key)

    def wrong_init_digest(traj):
        if traj == "olmo2_7b":
            return "not-the-real-digest"
        return seeds.init_digest(traj)
    monkeypatch.setattr(battery_4, "committed_init_digest_4", wrong_init_digest)

    with pytest.raises(SystemExit) as ei:
        rf.run(root=tmp_path, loaders=seeds.loaders(), only=twin_key, **_fake_prereg())
    assert ei.value.code == 2
    assert c4.reference_halt_marker_path(tmp_path).is_file()
    assert not battery_4.load_record_path(tmp_path, twin_key).is_file()


def test_reference_refuses_when_any_halted_marker_present(tmp_path, monkeypatch):
    _shrink_all_grids(monkeypatch)
    seeds = _Seeds()
    _install_digests(monkeypatch, seeds)
    c4.reference_halt_marker_path(tmp_path).parent.mkdir(parents=True, exist_ok=True)
    c4.reference_halt_marker_path(tmp_path).write_text("halted\n")
    with pytest.raises(RuntimeError, match="HALTED"):
        rf.run(root=tmp_path, loaders=seeds.loaders(), **_fake_prereg())


# ------------------------------------------------------------------ sweep

def _full_root_for_sweep(tmp_path, monkeypatch):
    seeds, _ = _run_full_reference(tmp_path, monkeypatch)
    battery_4.eligibility_path(tmp_path).write_text(json.dumps({"cells": []}))
    battery_4.power_path(tmp_path).write_text(json.dumps({"power": 1.0}))
    return seeds


def test_sweep_refuses_without_reference_seal(tmp_path, monkeypatch):
    seeds = _full_root_for_sweep(tmp_path, monkeypatch)
    with pytest.raises(RuntimeError, match="reference seal"):
        sw.run(traj="pythia_2.8b", root=tmp_path, loaders=seeds.loaders(), **_fake_auth(seal_tag_exists=False))


def test_sweep_refuses_without_eligibility_or_power(tmp_path, monkeypatch):
    seeds, _ = _run_full_reference(tmp_path, monkeypatch)
    # eligibility/power never written this time
    with pytest.raises(RuntimeError, match="not present"):
        sw.run(traj="pythia_2.8b", root=tmp_path, loaders=seeds.loaders(), **_fake_auth())


def test_sweep_refuses_with_halt_marker(tmp_path, monkeypatch):
    seeds = _full_root_for_sweep(tmp_path, monkeypatch)
    battery_4.halt_marker_path(tmp_path, "pythia_2.8b").parent.mkdir(parents=True, exist_ok=True)
    battery_4.halt_marker_path(tmp_path, "pythia_2.8b").write_text("halted\n")
    with pytest.raises(RuntimeError, match="halted"):
        sw.run(traj="pythia_2.8b", root=tmp_path, loaders=seeds.loaders(), **_fake_auth())


def test_sweep_refuses_with_missing_first_unit(tmp_path, monkeypatch):
    seeds = _full_root_for_sweep(tmp_path, monkeypatch)
    import shutil
    shutil.rmtree(battery_4.unit_dir(tmp_path, "pythia_2.8b", 1000))
    with pytest.raises(RuntimeError, match="first grid point"):
        sw.run(traj="pythia_2.8b", root=tmp_path, loaders=seeds.loaders(), **_fake_auth())


def test_sweep_dry_run_loads_nothing(tmp_path, monkeypatch):
    seeds = _full_root_for_sweep(tmp_path, monkeypatch)
    sw.run(traj="pythia_2.8b", root=tmp_path, dry_run=True, loaders={}, **_fake_auth())
    assert not battery_4.gate1_path(tmp_path, "pythia_2.8b").exists()


def test_sweep_gate1_pass_writes_gate1_json_and_continues(tmp_path, monkeypatch):
    seeds = _full_root_for_sweep(tmp_path, monkeypatch)
    monkeypatch.setattr("experiments.exp4.run.sweep_4.bt.load_battery", _tiny_battery)
    sw.run(traj="pythia_2.8b", root=tmp_path, loaders=seeds.loaders(), **_fake_auth())

    g1 = json.loads(battery_4.gate1_path(tmp_path, "pythia_2.8b").read_text())
    assert battery_4.gate1_failures_4(g1, traj="pythia_2.8b") == []
    # the remaining grid step (2000) ran too
    assert battery_4.unit_complete_4(tmp_path, ("pythia_2.8b", 2000))
    rec2000 = json.loads((battery_4.unit_dir(tmp_path, "pythia_2.8b", 2000) / "_load.json").read_text())
    assert rec2000["prereg_tag"] == battery_4.PREREG_TAG_4
    assert rec2000["committed_digest"] == seeds.step_digest("pythia_2.8b", 2000)
    # sweep units never keep activations
    assert not (battery_4.unit_dir(tmp_path, "pythia_2.8b", 2000) / "activations").exists()
    assert not (battery_4.unit_dir(tmp_path, "pythia_2.8b", 3000) / "activations").exists()


def test_sweep_gate1_digest_mismatch_halts_before_any_step(tmp_path, monkeypatch):
    seeds = _full_root_for_sweep(tmp_path, monkeypatch)
    monkeypatch.setattr("experiments.exp4.run.sweep_4.bt.load_battery", _tiny_battery)
    # perturb the endpoint's seed used by the STEP loader only, so
    # gate 1's step-loader digest disagrees with the sealed reference
    seeds.seed_by_key[("pythia_2.8b", 3000)] += 1
    with pytest.raises(SystemExit) as ei:
        sw.run(traj="pythia_2.8b", root=tmp_path, loaders=seeds.loaders(), **_fake_auth())
    assert ei.value.code == 2
    assert battery_4.halt_marker_path(tmp_path, "pythia_2.8b").is_file()
    assert not battery_4.gate1_path(tmp_path, "pythia_2.8b").exists()
    assert not battery_4.unit_complete_4(tmp_path, ("pythia_2.8b", 2000))


def test_sweep_per_step_digest_mismatch_halts(tmp_path, monkeypatch):
    seeds = _full_root_for_sweep(tmp_path, monkeypatch)
    monkeypatch.setattr("experiments.exp4.run.sweep_4.bt.load_battery", _tiny_battery)

    def wrong_step_digest(traj, step):
        if traj == "pythia_2.8b" and int(step) == 2000:
            return "not-the-real-digest"
        return seeds.step_digest(traj, step)
    monkeypatch.setattr(battery_4, "committed_step_digest_4", wrong_step_digest)

    with pytest.raises(SystemExit) as ei:
        sw.run(traj="pythia_2.8b", root=tmp_path, loaders=seeds.loaders(), **_fake_auth())
    assert ei.value.code == 2
    assert battery_4.halt_marker_path(tmp_path, "pythia_2.8b").is_file()
    # gate 1 itself passed (its own digest was fine)
    assert battery_4.gate1_path(tmp_path, "pythia_2.8b").is_file()
    assert not battery_4.unit_complete_4(tmp_path, ("pythia_2.8b", 2000))


def test_sweep_resume_reenters_an_incomplete_unit(tmp_path, monkeypatch):
    seeds = _full_root_for_sweep(tmp_path, monkeypatch)
    monkeypatch.setattr("experiments.exp4.run.sweep_4.bt.load_battery", _tiny_battery)
    sw.run(traj="pythia_2.8b", root=tmp_path, loaders=seeds.loaders(), **_fake_auth())
    # corrupt the 2000 unit's record to look incomplete
    unit2000 = battery_4.unit_dir(tmp_path, "pythia_2.8b", 2000)
    (unit2000 / "_load.json").unlink()
    assert not battery_4.unit_complete_4(tmp_path, ("pythia_2.8b", 2000))
    sw.run(traj="pythia_2.8b", root=tmp_path, loaders=seeds.loaders(), **_fake_auth())
    assert battery_4.unit_complete_4(tmp_path, ("pythia_2.8b", 2000))


# --------------------------------------------------------------- preflight

def test_preflight_writes_nothing_and_prints_identity_line(tmp_path, monkeypatch, capsys):
    seeds = _Seeds()
    monkeypatch.setattr(battery_4, "committed_step_digest_4", seeds.step_digest)
    monkeypatch.setattr("experiments.exp4.run.preflight_4.bt.load_battery", _tiny_battery)
    (tmp_path / "results").mkdir()
    (tmp_path / "results" / "keep.txt").write_text("x")

    pf.run(root=tmp_path, loaders=seeds.loaders(), checkpoint_step=2000)

    out = capsys.readouterr().out
    assert "X byte-identical across the two passes = True" in out
    assert "set_tables_4 identical = True" in out
    assert (tmp_path / "results" / "keep.txt").read_text() == "x"
    assert not any((tmp_path / "results").rglob("*.npz"))


def test_preflight_raises_if_results_changed(tmp_path, monkeypatch):
    seeds = _Seeds()
    monkeypatch.setattr(battery_4, "committed_step_digest_4", seeds.step_digest)
    monkeypatch.setattr("experiments.exp4.run.preflight_4.bt.load_battery", _tiny_battery)
    loaders = seeds.loaders()
    real_release = loaders["release"]
    state = {"done": False}

    def sneaky_release(model):
        # writes AFTER run()'s own before-snapshot (release is called
        # mid-run) so the poisoned file lands inside the window the
        # assertion is meant to catch
        if not state["done"]:
            state["done"] = True
            (tmp_path / "results").mkdir(parents=True, exist_ok=True)
            (tmp_path / "results" / "oops.txt").write_text("x")
        return real_release(model)

    loaders["release"] = sneaky_release
    with pytest.raises(RuntimeError, match="preflight wrote"):
        pf.run(root=tmp_path, loaders=loaders, checkpoint_step=2000)


# ----------------------------------------------------------------- watcher

def test_commit_watcher_4_parses():
    import subprocess
    p = battery_4.EXP4 / "run" / "commit_watcher_4.sh"
    out = subprocess.run(["zsh", "-n", str(p)], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
