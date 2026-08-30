# experiments/exp2l/tests/test_stages_2l.py
"""The 2l stage runners' control flow with FAKE loaders — no torch, no
network, no frozen tree touched. The two predictor seals are faked by
`blobs_bound`/`tag_exists` injections (both are real git checks in
production; `test_predictor_seals_bind_for_real` runs the real ones
once against the committed 2k/2i trees). Mirrors 2i's test_sweep_2i /
test_stages_2i shape with 2l's deltas: two predictor seals + an
endpoint seal, gate 1 = the endpoint through the candidate loader vs
the committed stage1_final records, step 0 as a real checkpoint, no
twin."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g.run.sweep_2g import evaluate_items
from experiments.exp2g.tests.test_sweep_2g import FakeRunner
from experiments.exp2i import battery_2i as bi
from experiments.exp2i.run import endpoint_2i as ep2i
from experiments.exp2k import battery_2k as bk
from experiments.exp2l import battery_2l as bl
from experiments.exp2l.run import endpoint_2l as ep
from experiments.exp2l.run import preflight_2l as pf
from experiments.exp2l.run import sweep_2l as sw

SHORT_GRID = (1000, 2000, bl.ENDPOINT_STEP_13B)


@pytest.fixture(autouse=True)
def _blobs_that_exist(monkeypatch):
    subset = tuple(r for r in bl.INSTRUMENT_BLOBS_2L if (bl.REPO / r).is_file())
    monkeypatch.setattr(bl, "INSTRUMENT_BLOBS_2L", subset)
    monkeypatch.setattr(bl, "FROZEN_SHA256_2L", bl.frozen_from_disk(strict=False))


def _amap_and_battery():
    from harness import render_prompt
    battery = bg.load_battery()
    amap = {}
    for cap in battery.values():
        shots = [tuple(s) for s in cap["shots"]][:bg.N_SHOTS]
        for it in cap["eval_items"]:
            amap[render_prompt(it["question"], shots)] = it["answer"]
    return battery, amap


def _manifest():
    """The committed 13B manifest, unpinned for the tests (the pin is
    asserted in test_battery_2l); the grid shrunk to SHORT_GRID."""
    return json.loads(bl.CHECKPOINTS_PATH.read_text())


def _shrink_grid(monkeypatch):
    monkeypatch.setattr(bl, "GRID_13B", SHORT_GRID)
    monkeypatch.setattr(bl, "load_manifest_13b", lambda path, sha_pin: _manifest())


def _fake_seals():
    """tag_exists/blobs_bound injections: every tag exists, nothing
    drifts. `blob_sha` compares each instrument blob against itself."""
    return dict(tag_exists=lambda t: True,
                blob_sha=lambda tag, rel: bg.sha256_file(bl.REPO / rel) if (bl.REPO / rel).is_file() else None,
                blobs_bound=lambda tag, paths, repo_root=None: [])


def _endpoint_loaders(*, frac_by_which=None, digest="Dend", commit=None, raise_at_which=None):
    frac_by_which = frac_by_which or {}
    state = {"loads": [], "released": []}

    class M:
        def __init__(self, d): self.d = d

    def olmo13b(commit_, device):
        state["loads"].append(commit_)
        return M(commit_), object(), {"tensor_digest": digest, "commit": commit or commit_,
                                     "loading_info": {"missing_keys": 0, "unexpected_keys": 0,
                                                      "mismatched_keys": 0}}

    battery, amap = _amap_and_battery()

    def runner(tok, model):
        which = "stage1_final" if model.d == bl.entry_13b(_manifest(), bl.ENDPOINT_STEP_13B)["commit"] else "main"
        if raise_at_which == which:
            raise RuntimeError("boom")
        return FakeRunner(amap, frac_by_which.get(which, 0.5))

    return {"olmo13b": olmo13b, "runner": runner}, state


# ------------------------------------------------------- predictor seals

def test_require_predictor_seals_2l_rederives_predictor_sha_and_refuses_drift():
    got = ep.require_predictor_seals_2l(root_2i=bi.EXP2I, root_2k=bk.EXP2K, **{k: v for k, v in _fake_seals().items() if k != "blob_sha"})
    assert got["predictor_sha"] == bl.PREDICTOR_SHA_2L
    assert got["seal_2k"]["sha256"] == bl.SEAL_2K_SHA256 and got["seal_2i"]["sha256"] == bl.SEAL_2I_SHA256
    with pytest.raises(RuntimeError, match="does not bind"):
        ep.require_predictor_seals_2l(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: True,
                                      blobs_bound=lambda tag, paths, repo_root=None: ["x"] if tag == bk.SEAL_TAG_2K else [])
    with pytest.raises(RuntimeError, match="does not exist"):
        ep.require_predictor_seals_2l(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: t != bi.PREDICTOR_SEAL_TAG,
                                      blobs_bound=lambda tag, paths, repo_root=None: [])


def test_require_predictor_seals_2l_refuses_a_seal_off_its_literal(monkeypatch):
    monkeypatch.setattr(bl, "SEAL_2I_SHA256", "0" * 64)
    with pytest.raises(RuntimeError, match="literal"):
        ep.require_predictor_seals_2l(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: True,
                                      blobs_bound=lambda tag, paths, repo_root=None: [])


@pytest.mark.slow
def test_predictor_seals_bind_for_real():
    """Real git, real tags, the committed 2k/2i trees (≈ 15 s)."""
    got = ep.require_predictor_seals_2l(root_2i=bi.EXP2I, root_2k=bk.EXP2K)
    assert got["predictor_sha"] == bl.PREDICTOR_SHA_2L


# --------------------------------------------------------------- endpoint

def test_endpoint_refuses_without_tag_or_frozen_pin(tmp_path, monkeypatch):
    with pytest.raises(RuntimeError, match="does not exist"):
        ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=_endpoint_loaders()[0],
               tag_exists=lambda t: False, blob_sha=lambda t, r: None,
               blobs_bound=lambda tag, paths, repo_root=None: [])
    monkeypatch.setattr(bl, "FROZEN_SHA256_2L", {})
    with pytest.raises(RuntimeError, match="not pinned"):
        ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=_endpoint_loaders()[0],
               **_fake_seals())


def test_endpoint_writes_both_which_and_the_rung_set_from_stage1_final(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, state = _endpoint_loaders(frac_by_which={"stage1_final": 0.9, "main": 0.0})
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    man = _manifest()
    assert state["loads"] == [bl.entry_13b(man, bl.ENDPOINT_STEP_13B)["commit"], bl.entry_main_13b(man)["commit"]]
    for which in bl.ENDPOINT_WHICH:
        for r in bt.RUNGS:
            rec = json.loads(bl.endpoint_record_path(tmp_path, which, r).read_text())
            assert rec["which"] == which and rec["size"] == bl.SIZE_OUT and rec["family"] == bl.FAMILY
            assert rec["seal_tag"] == bl.PREDICTOR_TAGS_2L and rec["predictor_sha"] == bl.PREDICTOR_SHA_2L
            assert rec["n"] == bt.N_ITEMS and len(rec["bits"]) == bt.N_ITEMS
            assert rec["revision"] == (bl.REV_13B_ENDPOINT if which == "stage1_final" else "main")
            assert "step" not in rec
    rs = json.loads(bl.rung_set_path(tmp_path).read_text())
    assert set(rs) >= {"R_13B", "R_PRIMARY", "R_ELEVEN_EXTRA", "R_EXTRA", "per_rung",
                       "primary_is_the_nine", "endpoint_file_sha256"}
    stage1 = {r: json.loads(bl.endpoint_record_path(tmp_path, "stage1_final", r).read_text())["correct"]
              for r in bt.RUNGS}
    assert rs["R_13B"] == bl.rung_set_from_counts_2l(stage1, bg.load_floors())["R_13B"]
    assert rs["R_PRIMARY"] and set(rs["R_PRIMARY"]) <= set(bl.R_CAP_2K)
    assert len(rs["endpoint_file_sha256"]) == 68
    # main's counts (0.0) must NOT have driven the rung set
    assert all(json.loads(bl.endpoint_record_path(tmp_path, "main", r).read_text())["correct"] == 0
               for r in bt.RUNGS)


def test_endpoint_skip_if_exists_and_dry_run(tmp_path, monkeypatch, capsys):
    _shrink_grid(monkeypatch)
    loaders, state = _endpoint_loaders()
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, dry_run=True, **_fake_seals())
    assert state["loads"] == [] and "would run 68" in capsys.readouterr().out
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    n = len(state["loads"])
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    assert len(state["loads"]) == n            # nothing re-loaded
    assert "nothing to do" in capsys.readouterr().out


def test_endpoint_exception_mid_which_leaves_no_rung_set(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, _ = _endpoint_loaders(raise_at_which="main")
    with pytest.raises(RuntimeError, match="boom"):
        ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    assert not bl.rung_set_path(tmp_path).exists()
    assert all(bl.endpoint_record_path(tmp_path, "stage1_final", r).exists() for r in bt.RUNGS)


# ------------------------------------------------------------------ sweep

def _setup_endpoint(tmp_path, *, gate_frac=0.5, digest="Dend", commit=None):
    """All 68 endpoint records through the REAL evaluate_items +
    item_record_2i (the shape gate 1 diffs against), the rung set and
    a power-record placeholder, so the endpoint seal's existence check
    passes and `endpoint_sha256` is computable."""
    battery, amap = _amap_and_battery()
    verify_fn = a2d.load_verify()
    man = _manifest()
    e = bl.entry_13b(man, bl.ENDPOINT_STEP_13B)
    commit = commit if commit is not None else e["commit"]
    counts = {}
    for which in bl.ENDPOINT_WHICH:
        for rung in bt.RUNGS:
            cap = battery[rung]
            ev = evaluate_items(FakeRunner(amap, gate_frac if which == "stage1_final" else 0.0), cap, verify_fn)
            ckpt = {"revision": e["revision"] if which == "stage1_final" else "main",
                    "commit": commit, "kind": e["kind"], "files": list(e["files"]),
                    "weight_sha256": digest, "config_source": "cs", "tokenizer_source": "ts"}
            rec = ep2i.item_record_2i(rung=rung, family=bl.FAMILY, size=bl.SIZE_OUT, which=which, cap=cap,
                                      ev=ev, ckpt=ckpt, seal={"tag": bl.PREDICTOR_TAGS_2L, "sha256": bl.PREDICTOR_SHA_2L},
                                      t_s=0.0)
            p = bl.endpoint_record_path(tmp_path, which, rung)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(rec, indent=1))
            if which == "stage1_final":
                counts[rung] = rec["correct"]
    rs = bl.rung_set_from_counts_2l(counts, bg.load_floors())
    bl.rung_set_path(tmp_path).write_text(json.dumps({**rs, "endpoint_file_sha256": {}}))
    bl.power_path(tmp_path).write_text(json.dumps({"A": {"declared_status": "x"}, "B": {"declared_status": "x"}}))
    return {"battery": battery, "amap": amap, "manifest": man, "entry": e, "commit": commit, "digest": digest}


def _sweep_loaders(*, entry, gate_frac=0.5, digest_gate="Dend", commit_gate=None, frac_by_revision=None,
                   digest_gate_diff=False, commit_gate_diff=False, raise_at_revision=None):
    frac_by_revision = frac_by_revision or {}
    commit_gate = commit_gate if commit_gate is not None else entry["commit"]
    state = {"calls": [], "freed": [], "tok_commits": []}
    battery, amap = _amap_and_battery()

    class M:
        def __init__(self, d): self.d = d

    def checkpoint(e, cache_root, device):
        is_gate = e["revision"] == entry["revision"]
        digest = digest_gate if not (is_gate and digest_gate_diff) else "WRONG-DIGEST"
        commit = commit_gate if not (is_gate and commit_gate_diff) else "0" * 40
        return M(e["revision"]), {"tensor_digest": digest, "commit": commit,
                                  "config_source": f"cs-{e['revision']}", "sha256": dict(e.get("lfs_sha256", {})),
                                  "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}}

    def tokenizer(commit):
        state["tok_commits"].append(commit)
        return object()

    def runner(tok, model):
        state["calls"].append(model.d)
        if raise_at_revision == model.d:
            raise RuntimeError("boom")
        frac = gate_frac if model.d == entry["revision"] else frac_by_revision.get(model.d, 0.3)
        return FakeRunner(amap, frac)

    def free(revision, cache_root):
        state["freed"].append(revision)

    return {"checkpoint": checkpoint, "tokenizer": tokenizer, "runner": runner, "free": free}, state


def test_sweep_refuses_without_endpoint_seal_then_runs_gate1_step0_and_grid(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    man = _manifest()
    e = bl.entry_13b(man, bl.ENDPOINT_STEP_13B)
    loaders, state = _sweep_loaders(entry=e)
    with pytest.raises(RuntimeError, match="endpoint stage"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    _setup_endpoint(tmp_path)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    # order: gate 1 (endpoint), step 0, then the grid ascending minus the endpoint
    assert state["calls"] == [e["revision"], bl.REV_13B_STEP0, bl.entry_13b(man, 1000)["revision"],
                              bl.entry_13b(man, 2000)["revision"]]
    assert state["freed"] == state["calls"]       # every download freed under its own key
    g = json.loads(bl.gate1_path(tmp_path).read_text())
    assert set(bl.GATE1_FIELDS_2L) <= set(g) and g["prereg_tag"] == bl.PREREG_TAG_2L
    assert all(v == 0 for v in g["bit_diffs"].values()) and all(v == bt.N_ITEMS for v in g["continuations_compared"].values())
    assert bl.gate1_failures_13b(g, {r: json.loads(bl.endpoint_record_path(tmp_path, "stage1_final", r).read_text()) for r in bt.RUNGS}) == []
    esha = bl.endpoint_sha256(tmp_path)
    for step in SHORT_GRID + (bl.STEP0,):
        assert sw.records_complete_13b(tmp_path, step)
        rec = json.loads(bl.record_path(tmp_path, step, "antonym").read_text())
        assert rec["step"] == step and rec["seal_tag"] == bl.ENDPOINT_SEAL_TAG_2L
        assert rec["predictor_sha"] == bl.PREDICTOR_SHA_2L and rec["endpoint_sha256"] == esha
        cr = json.loads(bl.checkpoint_record_path(tmp_path, step).read_text())
        assert cr["size"] == bl.SIZE_OUT and cr["step"] == step and cr["loading_info"]["missing_keys"] == 0
        assert cr["sha256"] == bl.entry_13b(man, step)["lfs_sha256"]
    assert not bl.halt_marker_path(tmp_path).exists()


def test_sweep_gate1_diff_halts_with_marker_and_refuses_resume(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path, gate_frac=0.5)
    e = bl.entry_13b(_manifest(), bl.ENDPOINT_STEP_13B)
    # BUILD FINDING (Task 2, disclosed in task-2-report.md): the brief's
    # literal gate_frac here was 0.6. FakeRunner marks item i correct
    # iff (i % 1000) / 1000 < frac; with bt.N_ITEMS == 500, i only
    # reaches i/1000 == 0.499, so 0.5 and 0.6 are indistinguishable —
    # both mark all 500 items correct, both rungs' continuations come
    # out byte-identical, and gate 1 does not fail as the test
    # requires ("DID NOT RAISE" observed). Corrected to 0.4 (below the
    # 0.499 ceiling), matching 2i's own test_sweep_2i pattern (0.2 vs
    # 0.4, both under the ceiling) so the sweep's own eval genuinely
    # differs from the committed stage1_final endpoint.
    loaders, state = _sweep_loaders(entry=e, gate_frac=0.4)       # the sweep's own eval differs
    with pytest.raises(RuntimeError, match="gate 1 olmo13b FAILED"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert bl.halt_marker_path(tmp_path).exists()
    g = json.loads(bl.gate1_path(tmp_path).read_text())
    assert sum(g["bit_diffs"].values()) > 0
    assert state["calls"] == [e["revision"]] and state["freed"] == [e["revision"]]
    assert sw.records_complete_13b(tmp_path, bl.ENDPOINT_STEP_13B)   # the evidence is on disk
    with pytest.raises(RuntimeError, match="halted"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert state["calls"] == [e["revision"]]


@pytest.mark.parametrize("kw,needle", [(dict(digest_gate_diff=True), "tensor digest"),
                                       (dict(commit_gate_diff=True), "commit")])
def test_sweep_gate1_digest_or_commit_mismatch_halts(tmp_path, monkeypatch, kw, needle):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bl.entry_13b(_manifest(), bl.ENDPOINT_STEP_13B)
    loaders, _ = _sweep_loaders(entry=e, **kw)
    with pytest.raises(RuntimeError, match="gate 1 olmo13b FAILED"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert any(needle in x for x in bl.halt_marker_path(tmp_path).read_text().splitlines())


def test_sweep_resume_skips_complete_steps_and_reenters_incomplete_ones(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    man = _manifest()
    e = bl.entry_13b(man, bl.ENDPOINT_STEP_13B)
    loaders, state = _sweep_loaders(entry=e, raise_at_revision=bl.entry_13b(man, 2000)["revision"])
    with pytest.raises(RuntimeError, match="boom"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert state["freed"][-1] == bl.entry_13b(man, 2000)["revision"]   # freed in finally
    assert not sw.records_complete_13b(tmp_path, 2000)
    # a step with every rung record but no checkpoint record (2i R-3) is incomplete
    bl.checkpoint_record_path(tmp_path, 1000).unlink()
    assert not sw.records_complete_13b(tmp_path, 1000)
    loaders2, state2 = _sweep_loaders(entry=e)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders2, **_fake_seals())
    assert state2["calls"] == [bl.entry_13b(man, 1000)["revision"], bl.entry_13b(man, 2000)["revision"]]
    assert sw.records_complete_13b(tmp_path, 1000) and sw.records_complete_13b(tmp_path, 2000)


def test_sweep_dry_run_loads_nothing(tmp_path, monkeypatch, capsys):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bl.entry_13b(_manifest(), bl.ENDPOINT_STEP_13B)
    loaders, state = _sweep_loaders(entry=e)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, dry_run=True, **_fake_seals())
    assert state["calls"] == [] and "gate1, " in capsys.readouterr().out


def test_sweep_refuses_endpoint_seal_drift(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bl.entry_13b(_manifest(), bl.ENDPOINT_STEP_13B)
    loaders, _ = _sweep_loaders(entry=e)
    seals = _fake_seals()
    seals["blobs_bound"] = lambda tag, paths, repo_root=None: (["x"] if tag == bl.ENDPOINT_SEAL_TAG_2L else [])
    with pytest.raises(RuntimeError, match="exp2l-endpoint-sealed.*does not bind"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **seals)
    paths = sw.endpoint_seal_blob_paths(tmp_path)
    assert len(paths) == 70 and "results/endpoint/rung_set_2l.json" in paths and "results/endpoint/power_2l.json" in paths


# -------------------------------------------------------------- preflight

def test_preflight_prints_and_writes_nothing(tmp_path, monkeypatch, capsys):
    _shrink_grid(monkeypatch)
    battery, amap = _amap_and_battery()
    state = {"thin": 0, "ckpt": [], "freed": []}

    class M:
        d = "m"

    def thin(commit, device):
        state["thin"] += 1
        return M(), object(), {"tensor_digest": "D", "commit": commit}

    def checkpoint(entry, cache_root, device):
        state["ckpt"].append(entry["revision"])
        return M(), {"tensor_digest": "D", "commit": entry["commit"]}

    loaders = {"thin": thin, "checkpoint": checkpoint, "tokenizer": lambda c: object(),
               "runner": lambda tok, model: FakeRunner(amap, 0.5),
               "free": lambda rev, cache_root: state["freed"].append(rev),
               "check_tokenizer": lambda tok: None, "memory": lambda: 12345}
    pf.run(root=tmp_path, loaders=loaders, cache_root=tmp_path / "c", checkpoint_step=1000)
    out = capsys.readouterr().out
    assert state["thin"] == 1 and state["ckpt"] == [bl.entry_13b(_manifest(), 1000)["revision"]]
    assert state["freed"] == state["ckpt"]
    assert out.count("[2l preflight] antonym") == 20 and out.count("[2l preflight] add3_mid") == 20
    assert out.count("[2l preflight] ckpt antonym") == 20 and "verify=" in out
    assert "batch_size 16" in out and "mps_allocated_bytes 12345" in out
    assert not (tmp_path / "results").exists()


def test_preflight_refuses_if_it_wrote_under_results(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    battery, amap = _amap_and_battery()

    class M:
        d = "m"

    def thin(commit, device):
        (tmp_path / "results").mkdir(exist_ok=True)
        (tmp_path / "results" / "stray.json").write_text("{}")
        return M(), object(), {"tensor_digest": "D", "commit": commit}

    loaders = {"thin": thin, "checkpoint": lambda e, c, d: (M(), {"tensor_digest": "D", "commit": e["commit"]}),
               "tokenizer": lambda c: object(), "runner": lambda tok, model: FakeRunner(amap, 0.5),
               "free": lambda rev, cache_root: None, "check_tokenizer": lambda tok: None, "memory": lambda: 0}
    with pytest.raises(RuntimeError, match="preflight wrote under"):
        pf.run(root=tmp_path, loaders=loaders, cache_root=tmp_path / "c", checkpoint_step=1000)
