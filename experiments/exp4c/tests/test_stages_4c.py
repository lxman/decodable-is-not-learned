# experiments/exp4c/tests/test_stages_4c.py
"""Exp 4c's ONE stage runner's control flow with FAKE loaders — no
torch, no network, no real checkpoint tree touched. `battery_4c.
GRID_4C`/`ENDPOINT_STEP_4C`/`FIRST_STEP_4C` are shrunk to three points
per trajectory (1000/2000/3000, 3000 the endpoint) so the sweep tests
run fast; `committed_step_digest_4c` is faked entirely (no dependency
on any real exp2h/exp2l committed tree). `battery_4c.RUNGS` (all 34) is
exercised on every load (it's a hardcoded loop inside `collect_4c.
process_model_4c`), backed by a tiny synthetic 12-item-per-rung battery
(k=10 needs n > 10)."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp4 import battery_4
from experiments.exp4 import collect_4 as c4
from experiments.exp4 import metric_4
from experiments.exp4.tests import fakes_4
from experiments.exp4.tests import full_shape
from experiments.exp4c import analyze_4c as an4c
from experiments.exp4c import battery_4c
from experiments.exp4c import collect_4c
from experiments.exp4c.run import preflight_4c as pf
from experiments.exp4c.run import sweep_4c as sw

_WORDS = ["cat", "dog", "blue", "fast", "moon", "tree", "gold", "iron", "leaf", "wave",
         "frost", "spark", "amber", "cliff", "delta", "ember", "quartz", "willow"]

_REF_N_HIDDEN = {"ref_pythia_12b": 37, "ref_olmo2_7b": 33, "ref_smollm3_3b": 37,
                "ref_comma_7b": 33}
_REF_FAMILY = {"ref_pythia_12b": "pythia", "ref_olmo2_7b": "olmo2",
              "ref_smollm3_3b": "smollm3", "ref_comma_7b": "comma"}

_N_HIDDEN_BY = {"pythia_6.9b": 33, "olmo2_13b": 41, battery_4c.THIN_ENDPOINT_KEY_4C: 41,
               "ladder_pythia_6.9b": 33}


# ------------------------------------------------------------- fixtures

@pytest.fixture(autouse=True)
def _frozen_ok(monkeypatch):
    # FROZEN_SHA256_4C is `None` until Task 5 pins it (controller
    # ruling 1) — a stage test never asserts that pin, only that
    # `check_frozen_4c` does not refuse for a reason THIS task owns.
    monkeypatch.setattr(battery_4c, "FROZEN_SHA256_4C", {})


@pytest.fixture(autouse=True)
def _blobs_that_exist(monkeypatch):
    subset = tuple(r for r in battery_4c.INSTRUMENT_BLOBS_4C if (battery_4c.REPO / r).is_file())
    monkeypatch.setattr(battery_4c, "INSTRUMENT_BLOBS_4C", subset)


def _fake_prereg():
    def blob_sha(tag, rel):
        p = battery_4c.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None
    return dict(tag_exists=lambda t: True, blob_sha=blob_sha)


def _fake_auth():
    return dict(**_fake_prereg(), blobs_bound=lambda *a, **k: [])


def _shrink_grid(monkeypatch):
    grid = {traj: (1000, 2000, 3000) for traj in battery_4c.TRAJECTORIES_4C}
    endpoint = {traj: 3000 for traj in battery_4c.TRAJECTORIES_4C}
    first = {traj: 1000 for traj in battery_4c.TRAJECTORIES_4C}
    monkeypatch.setattr(battery_4c, "GRID_4C", grid)
    monkeypatch.setattr(battery_4c, "ENDPOINT_STEP_4C", endpoint)
    monkeypatch.setattr(battery_4c, "FIRST_STEP_4C", first)


def _tiny_battery(n=12):
    battery = {}
    for r in battery_4.RUNGS:
        rng = random.Random(r)
        items = [{"question": " ".join(rng.choice(_WORDS) for _ in range(4)) + f" {i}",
                 "answer": str(i)} for i in range(n)]
        battery[r] = {"shots": [["amber cliff quartz willow", "2"], ["delta ember frost spark", "4"]],
                     "eval_items": items}
    return battery


def _write_refs_under_root4(root4):
    """The four Exp 4 reference-stage units exp4c's own `REFS_FOR_4C`
    draws from, written through Exp 4's own frozen synthetic-unit
    writer (no model, no torch) — `refs=()`, so no cross-alignment
    among themselves."""
    for ref, n_hidden in _REF_N_HIDDEN.items():
        sites = metric_4.sites_4(n_hidden)
        rng = np.random.default_rng(abs(hash(ref)) % (2 ** 31))

        def provider(rung, _rng=rng, _n_sites=len(sites)):
            return _rng.standard_normal((12, _n_sites, 1, 8)).astype(np.float32)

        full_shape._write_synthetic_unit(
            root4, ref, family=_REF_FAMILY[ref], n_hidden=n_hidden, sites=sites,
            batch_size=battery_4.BATCH_4[ref], refs=(), ref_tables={},
            committed_digest=f"synthetic:{ref}", X_provider=provider, keep_activations=True)


def _write_ladder_69(root4, seed, battery, *, n_hidden=33, d=8):
    """The Pythia 6.9b gate-1 reference: Exp 4's OWN `ladder_pythia_6.
    9b` table (controller ruling 3) — written through Exp 4's frozen
    `collect_4.process_model_4` (not exp4c's wrapper) so a test can
    prove exp4c's byte rederivation actually compares against Exp 4's
    real construction. `refs = collect_4.non_pythia_refs_4()` (the same
    three exp4c's own `REFS_FOR_4C["pythia_6.9b"]` names), batch 16 (4c's
    own pin, and exp4's `BATCH_4["ladder_pythia_6.9b"]` too — a 6.9b
    weight class), a FakeModel of the SAME seed the fake step loader
    will give the sweep's own 6.9b endpoint step, so the two
    constructions' k-NN sets are byte-identical by construction."""
    model = fakes_4.FakeModel(seed=seed, n_hidden=n_hidden, d=d)
    tok = fakes_4.FakeTokenizer()
    info = {"n_hidden": n_hidden, "tensor_digest": fakes_4.fake_digest(seed), "commit": "fake-ladder",
           "revision": "main", "repo": "fake/pythia-6.9b", "kind": "2b",
           "config_source": "fake/pythia-6.9b@main",
           "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}}
    refs = c4.non_pythia_refs_4()
    ref_tables = c4.load_ref_tables_4(root4, refs)
    return c4.process_model_4(
        [model], tok, key_or_unit="ladder_pythia_6.9b", family="pythia", info=info, root=root4,
        battery=battery, ref_tables=ref_tables, ref_activation_paths={}, batch_size=16,
        device="cpu", keep_activations=False, sites=metric_4.sites_4(n_hidden), refs=refs,
        committed_digest=None, stack={"torch": "x", "transformers": "y"}, git_sha="0" * 40,
        release_model=None)


class _Seeds4c:
    """Assigns every fake-loader-reachable key/unit a distinct seed
    (the shrunk grid: steps 0/1000/2000/3000 per trajectory, plus the
    13B thin endpoint) and builds the matching `committed_step_digest_
    4c` table from those seeds' `fake_digest`, so a real loader call
    and the "committed" pin agree by construction unless a test
    deliberately perturbs one side. The 13B thin endpoint reuses the
    13B sweep endpoint's OWN seed by default (gate 1 byte-equal); a
    test wanting a mismatch overrides `seed_by_key` after construction."""

    def __init__(self):
        self.seed_by_key = {}
        self._next = 5000
        for traj in battery_4c.TRAJECTORIES_4C:
            for step in (0, 1000, 2000):
                self._assign((traj, step))
            self._assign((traj, 3000))
        self.seed_by_key[battery_4c.THIN_ENDPOINT_KEY_4C] = self.seed_by_key[("olmo2_13b", 3000)]

    def _assign(self, key):
        self.seed_by_key[key] = self._next
        self._next += 1

    def step_digest(self, traj, step):
        return fakes_4.fake_digest(self.seed_by_key[(traj, int(step))])

    def loaders(self, calls=None):
        base = fakes_4.fake_loaders(self.seed_by_key, n_hidden_by=_N_HIDDEN_BY)
        real_step, real_key, real_free, real_release = (base["step"], base["key"],
                                                         base["free_step"], base["release"])

        def step(traj, s, *, cache_root=None, device="mps"):
            if calls is not None:
                calls.append(f"step:{s}")
            return real_step(traj, s, cache_root=cache_root, device=device)

        def thin(key, *, device="mps"):
            if calls is not None:
                calls.append("thin")
            return real_key(key, device=device)

        return {"step": step, "thin": thin, "free_step": real_free, "release": real_release}


def _install_digests(monkeypatch, seeds: _Seeds4c):
    monkeypatch.setattr(battery_4c, "committed_step_digest_4c", seeds.step_digest)


# --------------------------------------------------------------- refusals

def test_sweep_refuses_without_prereg_tag(tmp_path):
    with pytest.raises(RuntimeError, match="does not exist"):
        sw.run(traj="pythia_6.9b", root=tmp_path, loaders={}, tag_exists=lambda t: False,
              blob_sha=lambda tag, rel: None, blobs_bound=lambda *a, **k: [])


def test_sweep_refuses_without_exp4_reference_seal(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    with pytest.raises(RuntimeError, match="exp4 reference seal"):
        sw.run(traj="pythia_6.9b", root=tmp_path, root4=tmp_path / "root4", loaders={},
              **_fake_prereg(), blobs_bound=lambda tag, paths, repo_root=None: ["boom"])


def test_sweep_refuses_without_the_power_record(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    with pytest.raises(RuntimeError, match="power_4c.main first"):
        sw.run(traj="pythia_6.9b", root=tmp_path, root4=tmp_path / "root4", loaders={},
              **_fake_auth())


def test_sweep_refuses_with_a_halt_marker(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    (tmp_path / "results").mkdir(parents=True)
    (tmp_path / "results" / "power_4c.json").write_text(json.dumps({"power": 1.0}))
    battery_4.halt_marker_path(tmp_path, "pythia_6.9b").parent.mkdir(parents=True, exist_ok=True)
    battery_4.halt_marker_path(tmp_path, "pythia_6.9b").write_text("halted\n")
    with pytest.raises(RuntimeError, match="halted"):
        sw.run(traj="pythia_6.9b", root=tmp_path, root4=tmp_path / "root4", loaders={},
              **_fake_auth())


def _powered_root(tmp_path):
    (tmp_path / "results").mkdir(parents=True, exist_ok=True)
    (tmp_path / "results" / "power_4c.json").write_text(json.dumps({"power": 1.0}))


def test_sweep_refuses_a_drifted_import_surface(tmp_path, monkeypatch):
    """FREEZE F-1 (THE CLASS DEFECT): the runner writes every set table
    the verdict is read on, and an interior checkpoint's tables have no
    comparator anywhere — gate 1 covers the endpoint only, and on
    `olmo2_13b` it compares two units this same code wrote. Before the
    closure the runner's whole refusal chain (prereg tag, frozen
    modules, Exp 4's seal, the power record, the halt marker) passed a
    two-line `experiments/exp4c/__init__.py` that repointed the
    collector, because those two package files sit in
    `IMPORTED_SHA256_4C`, which only the ANALYZER read."""
    _shrink_grid(monkeypatch)
    _powered_root(tmp_path)
    drifted = dict(an4c.IMPORTED_SHA256_4C)
    drifted[battery_4c.REPO / "experiments/exp4c/__init__.py"] = "0" * 64
    monkeypatch.setattr(an4c, "IMPORTED_SHA256_4C", drifted)
    with pytest.raises(RuntimeError, match="drifted from its pin"):
        sw.run(traj="pythia_6.9b", root=tmp_path, root4=tmp_path / "root4", dry_run=True,
              loaders={}, **_fake_auth())


def test_sweep_refuses_an_unpinned_module_on_its_own_import_surface(tmp_path, monkeypatch):
    """FREEZE F-1, the other half: a module under `experiments/` that no
    pin table covers refuses the RUNNER, not only the analyzer."""
    _shrink_grid(monkeypatch)
    _powered_root(tmp_path)
    thinned = {k: v for k, v in an4c.IMPORTED_SHA256_4C.items()
              if "exp4c/__init__.py" not in str(k)}
    monkeypatch.setattr(an4c, "IMPORTED_SHA256_4C", thinned)
    with pytest.raises(RuntimeError, match="unpinned module on the import surface"):
        sw.run(traj="pythia_6.9b", root=tmp_path, root4=tmp_path / "root4", dry_run=True,
              loaders={}, **_fake_auth())


def test_the_runners_own_import_surface_is_covered_by_the_analyzers_table(tmp_path, monkeypatch):
    """FREEZE F-1: the positive side — every module the runner's own
    import chain executes is covered by one of the pinned tables, so
    the new refusal is a real gate and not a permanent halt."""
    an4c.check_imports_4c()
    covered = {str(Path(x).resolve()) for x in battery_4.FROZEN_SHA256_4}
    covered |= {str((battery_4c.REPO / r).resolve())
               for t in (battery_4c.EXP4_CLOSED_SHA256_4C, battery_4c.EXP4B_CLOSED_SHA256_4C)
               for r in t}
    covered |= {str((battery_4c.REPO / r).resolve()) for r in battery_4c.INSTRUMENT_BLOBS_4C}
    covered |= {str(Path(k).resolve()) for k in an4c.IMPORTED_SHA256_4C}
    exp_root = str((battery_4c.REPO / "experiments").resolve())
    live = [str(Path(m.__file__).resolve()) for m in sys.modules.values()
           if getattr(m, "__file__", None)
           and str(Path(m.__file__).resolve()).startswith(exp_root + "/")
           and "tests" not in Path(m.__file__).resolve().parts]
    assert [p for p in live if p not in covered] == []


def test_sweep_dry_run_loads_nothing(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _powered_root(tmp_path)
    sw.run(traj="pythia_6.9b", root=tmp_path, root4=tmp_path / "root4", dry_run=True,
          loaders={}, **_fake_auth())
    assert not battery_4.gate1_path(tmp_path, "pythia_6.9b").exists()


# --------------------------------------------------------- 6.9b happy path

def test_sweep_6_9b_gate1_compares_against_exp4s_ladder_table(tmp_path, monkeypatch):
    root4c, root4 = tmp_path / "root4c", tmp_path / "root4"
    _shrink_grid(monkeypatch)
    seeds = _Seeds4c()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4c.run.sweep_4c.bt.load_battery", _tiny_battery)
    _write_refs_under_root4(root4)
    _write_ladder_69(root4, seeds.seed_by_key[("pythia_6.9b", 3000)], _tiny_battery())
    _powered_root(root4c)

    sw.run(traj="pythia_6.9b", root=root4c, root4=root4, loaders=seeds.loaders(), **_fake_auth())

    g1 = json.loads(battery_4.gate1_path(root4c, "pythia_6.9b").read_text())
    assert battery_4c.gate1_failures_4c(g1, traj="pythia_6.9b") == []
    assert g1["reference_root"] == "exp4" and g1["reference_key"] == "ladder_pythia_6.9b"
    assert battery_4.unit_complete_4(root4c, ("pythia_6.9b", 0))
    assert all(battery_4.unit_complete_4(root4c, ("pythia_6.9b", s))
              for s in battery_4c.GRID_4C["pythia_6.9b"])
    rec2000 = json.loads((battery_4.unit_dir(root4c, "pythia_6.9b", 2000) / "_load.json").read_text())
    assert rec2000["prereg_tag"] == battery_4c.PREREG_TAG_4C
    assert rec2000["committed_digest"] == seeds.step_digest("pythia_6.9b", 2000)
    assert not (battery_4.unit_dir(root4c, "pythia_6.9b", 2000) / "activations").exists()


def test_sweep_resume_skips_complete_units(tmp_path, monkeypatch):
    root4c, root4 = tmp_path / "root4c", tmp_path / "root4"
    _shrink_grid(monkeypatch)
    seeds = _Seeds4c()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4c.run.sweep_4c.bt.load_battery", _tiny_battery)
    _write_refs_under_root4(root4)
    _write_ladder_69(root4, seeds.seed_by_key[("pythia_6.9b", 3000)], _tiny_battery())
    _powered_root(root4c)

    sw.run(traj="pythia_6.9b", root=root4c, root4=root4, loaders=seeds.loaders(), **_fake_auth())

    calls2 = []
    sw.run(traj="pythia_6.9b", root=root4c, root4=root4, loaders=seeds.loaders(calls=calls2),
          **_fake_auth())
    assert calls2 == []


# -------------------------------------------------------- 13b happy path

def test_sweep_runs_thin_endpoint_then_gate1_then_step0_then_grid_for_13b(tmp_path, monkeypatch):
    root4c, root4 = tmp_path / "root4c", tmp_path / "root4"
    _shrink_grid(monkeypatch)
    seeds = _Seeds4c()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4c.run.sweep_4c.bt.load_battery", _tiny_battery)
    _write_refs_under_root4(root4)
    _powered_root(root4c)

    calls = []
    sw.run(traj="olmo2_13b", root=root4c, root4=root4, loaders=seeds.loaders(calls=calls),
          **_fake_auth())

    assert battery_4.unit_complete_4(root4c, battery_4c.THIN_ENDPOINT_KEY_4C)
    g1 = json.loads(battery_4.gate1_path(root4c, "olmo2_13b").read_text())
    assert g1["reference_key"] == battery_4c.THIN_ENDPOINT_KEY_4C
    assert g1["reference_root"] == "exp4c"
    assert battery_4c.gate1_failures_4c(g1, traj="olmo2_13b") == []
    assert battery_4.unit_complete_4(root4c, ("olmo2_13b", 0))
    assert all(battery_4.unit_complete_4(root4c, ("olmo2_13b", s))
              for s in battery_4c.GRID_4C["olmo2_13b"])
    assert calls == ["thin", "step:3000", "step:0", "step:1000", "step:2000"]


# ------------------------------------------------------------------ halts

def test_gate1_digest_mismatch_halts_before_any_processing(tmp_path, monkeypatch):
    root4c, root4 = tmp_path / "root4c", tmp_path / "root4"
    _shrink_grid(monkeypatch)
    seeds = _Seeds4c()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4c.run.sweep_4c.bt.load_battery", _tiny_battery)
    _write_refs_under_root4(root4)
    _write_ladder_69(root4, seeds.seed_by_key[("pythia_6.9b", 3000)], _tiny_battery())
    _powered_root(root4c)
    # perturb the endpoint's seed used by the STEP loader only, so the
    # step loader's digest disagrees with both the committed pin and
    # the ladder reference
    seeds.seed_by_key[("pythia_6.9b", 3000)] += 1

    with pytest.raises(SystemExit) as ei:
        sw.run(traj="pythia_6.9b", root=root4c, root4=root4, loaders=seeds.loaders(),
              **_fake_auth())
    assert ei.value.code == 2
    assert battery_4.halt_marker_path(root4c, "pythia_6.9b").is_file()
    assert not battery_4.gate1_path(root4c, "pythia_6.9b").exists()
    assert not battery_4.unit_complete_4(root4c, ("pythia_6.9b", 0))


def test_gate1_byte_mismatch_halts_with_the_record_written(tmp_path, monkeypatch):
    """Digests agree (the outer pin, and the reference's own attested
    `tensor_digest`) but the byte-level rederivation catches a real
    divergence — `gate1_rederive_4c` is patched to report ONE rung's
    `sets_equal` False, so `run_gate1` writes `gate1.json` (it writes
    the record BEFORE checking `gate1_failures_4c`) and only then
    halts."""
    root4c, root4 = tmp_path / "root4c", tmp_path / "root4"
    _shrink_grid(monkeypatch)
    seeds = _Seeds4c()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4c.run.sweep_4c.bt.load_battery", _tiny_battery)
    _write_refs_under_root4(root4)
    _write_ladder_69(root4, seeds.seed_by_key[("pythia_6.9b", 3000)], _tiny_battery())
    _powered_root(root4c)

    real_rederive = battery_4c.gate1_rederive_4c

    def bad_rederive(root, root4_, traj):
        out = real_rederive(root, root4_, traj)
        out = dict(out, sets_equal=dict(out["sets_equal"]))
        out["sets_equal"][battery_4.RUNGS[0]] = False
        return out

    monkeypatch.setattr(sw.battery_4c, "gate1_rederive_4c", bad_rederive)

    with pytest.raises(SystemExit) as ei:
        sw.run(traj="pythia_6.9b", root=root4c, root4=root4, loaders=seeds.loaders(),
              **_fake_auth())
    assert ei.value.code == 2
    assert battery_4.halt_marker_path(root4c, "pythia_6.9b").is_file()
    assert battery_4.gate1_path(root4c, "pythia_6.9b").is_file()   # written before the halt
    g1 = json.loads(battery_4.gate1_path(root4c, "pythia_6.9b").read_text())
    assert battery_4c.gate1_failures_4c(g1, traj="pythia_6.9b") != []
    assert not battery_4.unit_complete_4(root4c, ("pythia_6.9b", 0))


def test_step_digest_mismatch_halts_and_frees(tmp_path, monkeypatch):
    root4c, root4 = tmp_path / "root4c", tmp_path / "root4"
    _shrink_grid(monkeypatch)
    seeds = _Seeds4c()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4c.run.sweep_4c.bt.load_battery", _tiny_battery)
    _write_refs_under_root4(root4)
    _write_ladder_69(root4, seeds.seed_by_key[("pythia_6.9b", 3000)], _tiny_battery())
    _powered_root(root4c)

    def wrong_step_digest(traj, step):
        if traj == "pythia_6.9b" and int(step) == 2000:
            return "not-the-real-digest"
        return seeds.step_digest(traj, step)
    monkeypatch.setattr(battery_4c, "committed_step_digest_4c", wrong_step_digest)

    freed = []
    loaders = seeds.loaders()
    real_free = loaders["free_step"]

    def spy_free(traj, s, cache_root=None):
        freed.append((traj, s))
        return real_free(traj, s, cache_root=cache_root)
    loaders["free_step"] = spy_free

    with pytest.raises(SystemExit) as ei:
        sw.run(traj="pythia_6.9b", root=root4c, root4=root4, loaders=loaders, **_fake_auth())
    assert ei.value.code == 2
    assert battery_4.halt_marker_path(root4c, "pythia_6.9b").is_file()
    # gate 1 itself passed (its own digest was fine); step0 ran fine too
    assert battery_4.gate1_path(root4c, "pythia_6.9b").is_file()
    assert battery_4.unit_complete_4(root4c, ("pythia_6.9b", 0))
    assert not battery_4.unit_complete_4(root4c, ("pythia_6.9b", 2000))
    assert ("pythia_6.9b", 2000) in freed


# --------------------------------------------------------------- preflight

def test_preflight_writes_nothing_under_results(tmp_path, monkeypatch):
    seeds = _Seeds4c()
    _install_digests(monkeypatch, seeds)
    monkeypatch.setattr("experiments.exp4c.run.preflight_4c.bt.load_battery", _tiny_battery)
    (tmp_path / "results").mkdir()
    (tmp_path / "results" / "keep.txt").write_text("x")

    pf.run(root=tmp_path, loaders=seeds.loaders(),
          units=(("olmo2_13b", 1000), ("pythia_6.9b", 1000)))

    assert (tmp_path / "results" / "keep.txt").read_text() == "x"
    assert not any((tmp_path / "results").rglob("*.npz"))


# ----------------------------------------------------------------- watcher

def test_commit_watcher_4c_parses():
    import subprocess
    p = battery_4c.EXP4C / "run" / "commit_watcher_4c.sh"
    out = subprocess.run(["zsh", "-n", str(p)], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
