# experiments/exp2m/tests/test_stages_2m.py
"""The 2m stage runners' control flow with FAKE loaders — no torch, no
network, no frozen tree touched. Mirrors 2l's test_stages_2l with 2m's
deltas: THREE thin loads at the endpoint stage (stage1_final,
stage3_final, base) from two repos; the rung set from stage1_final
only; the dtype override on every record; gate 1 = the endpoint through
the candidate loader vs the committed stage1_final records; the seeded
TWIN after gate 1 (its own record shapes, never freed — nothing was
downloaded); the preflight's two renders and its fp16 finiteness
check."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g.run.sweep_2g import evaluate_items
from experiments.exp2g.tests.test_sweep_2g import FakeRunner
from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2k import analyze_2k as an2k
from experiments.exp2k import battery_2k as bk
from experiments.exp2m import analyze_2m as an
from experiments.exp2m import battery_2m as bm
from experiments.exp2m.run import endpoint_2m as ep
from experiments.exp2m.run import preflight_2m as pf
from experiments.exp2m.run import sweep_2m as sw

SHORT_GRID = (40000, 80000, bm.ENDPOINT_STEP_2M)
SHORT_SUBSET = (40000, bm.ENDPOINT_STEP_2M)


@pytest.fixture(autouse=True)
def _blobs_that_exist(monkeypatch):
    subset = tuple(r for r in bm.INSTRUMENT_BLOBS_2M if (bm.REPO / r).is_file())
    monkeypatch.setattr(bm, "INSTRUMENT_BLOBS_2M", subset)
    if not bm.FROZEN_SHA256_2M:                      # until Task 5 pins the literal
        monkeypatch.setattr(bm, "FROZEN_SHA256_2M", bm.frozen_from_disk(strict=False))


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
    """The committed manifest, unpinned for the tests (the pin is
    asserted in test_battery_2m); the grid shrunk to SHORT_GRID."""
    return json.loads(bm.CHECKPOINTS_PATH.read_text())


def _shrink_grid(monkeypatch):
    monkeypatch.setattr(bm, "GRID_3B", SHORT_GRID)
    monkeypatch.setattr(bm, "LOG_HEAD_SUBSET_2M", SHORT_SUBSET)
    monkeypatch.setattr(bm, "load_manifest_3b", lambda path, sha_pin: _manifest())


def _fake_seals():
    return dict(tag_exists=lambda t: True,
                blob_sha=lambda tag, rel: bg.sha256_file(bm.REPO / rel) if (bm.REPO / rel).is_file() else None,
                blobs_bound=lambda tag, paths, repo_root=None: [])


def _which_of(repo, commit):
    man = _manifest()
    for which in bm.ENDPOINT_WHICH_2M:
        e = bm.entry_which_3b(man, which)
        if (e["repo"], e["commit"]) == (repo, commit):
            return which
    raise AssertionError((repo, commit))


def _endpoint_loaders(*, frac_by_which=None, digest="Dend", raise_at_which=None):
    frac_by_which = frac_by_which or {}
    state = {"loads": [], "released": []}

    class M:
        def __init__(self, d): self.d = d

    def thin(repo, commit, device):
        state["loads"].append((repo, commit))
        return M((repo, commit)), object(), {"repo": repo, "tensor_digest": digest, "commit": commit,
                                             "loading_info": {"missing_keys": 0, "unexpected_keys": 0,
                                                              "mismatched_keys": 0}}

    battery, amap = _amap_and_battery()

    def runner(tok, model):
        which = _which_of(*model.d)
        if raise_at_which == which:
            raise RuntimeError("boom")
        return FakeRunner(amap, frac_by_which.get(which, 0.5))

    return {"thin": thin, "runner": runner}, state


# ------------------------------------------------------- predictor seals

def test_require_predictor_seals_2m_rederives_predictor_sha_and_refuses_drift():
    got = ep.require_predictor_seals_2m(root_2i=bi.EXP2I, root_2k=bk.EXP2K,
                                        **{k: v for k, v in _fake_seals().items() if k != "blob_sha"})
    assert got["predictor_sha"] == bm.PREDICTOR_SHA_2M
    assert got["seal_2k"]["sha256"] == bm.SEAL_2K_SHA256 and got["seal_2i"]["sha256"] == bm.SEAL_2I_SHA256
    with pytest.raises(RuntimeError, match="does not bind"):
        ep.require_predictor_seals_2m(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: True,
                                      blobs_bound=lambda tag, paths, repo_root=None: ["x"] if tag == bk.SEAL_TAG_2K else [])
    with pytest.raises(RuntimeError, match="does not exist"):
        ep.require_predictor_seals_2m(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: t != bi.PREDICTOR_SEAL_TAG,
                                      blobs_bound=lambda tag, paths, repo_root=None: [])


@pytest.mark.parametrize("attr", ["SEAL_2I_SHA256", "SEAL_2K_SHA256"])
def test_require_predictor_seals_2m_refuses_a_seal_off_its_literal(monkeypatch, attr):
    monkeypatch.setattr(bm, attr, "0" * 64)
    with pytest.raises(RuntimeError, match="literal"):
        ep.require_predictor_seals_2m(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: True,
                                      blobs_bound=lambda tag, paths, repo_root=None: [])


def test_require_predictor_seals_2m_refuses_a_stale_composite(monkeypatch):
    monkeypatch.setattr(bm, "PREDICTOR_SHA_2M", "0" * 64)
    with pytest.raises(RuntimeError, match="does not re-derive"):
        ep.require_predictor_seals_2m(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: True,
                                      blobs_bound=lambda tag, paths, repo_root=None: [])


@pytest.mark.slow
def test_predictor_seals_bind_for_real():
    got = ep.require_predictor_seals_2m(root_2i=bi.EXP2I, root_2k=bk.EXP2K)
    assert got["predictor_sha"] == bm.PREDICTOR_SHA_2M


def test_endpoint_seal_path_sets_agree_three_ways(tmp_path):
    for p in an._endpoint_seal_paths_2m(tmp_path):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x")
    a = {str(p.relative_to(tmp_path)) for p in an._endpoint_seal_paths_2m(tmp_path)}
    b = set(bm.endpoint_files(tmp_path))
    c = set(sw.endpoint_seal_blob_paths(tmp_path))
    assert a == b == c
    assert len(a) == 2 + len(bm.ENDPOINT_WHICH_2M) * len(bt.RUNGS) == 104


# --------------------------------------------------------------- endpoint

def test_endpoint_refuses_without_tag_or_frozen_pin(tmp_path, monkeypatch):
    with pytest.raises(RuntimeError, match="does not exist"):
        ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=_endpoint_loaders()[0],
               tag_exists=lambda t: False, blob_sha=lambda t, r: None,
               blobs_bound=lambda tag, paths, repo_root=None: [])
    monkeypatch.setattr(bm, "FROZEN_SHA256_2M", {})
    with pytest.raises(RuntimeError, match="not pinned"):
        ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=_endpoint_loaders()[0], **_fake_seals())


def test_endpoint_writes_three_whichs_and_the_rung_set_from_stage1_final(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, state = _endpoint_loaders(frac_by_which={"stage1_final": 0.9, "stage3_final": 0.0, "base": 0.0})
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    man = _manifest()
    assert state["loads"] == [(bm.entry_which_3b(man, w)["repo"], bm.entry_which_3b(man, w)["commit"])
                              for w in bm.ENDPOINT_WHICH_2M]
    assert state["loads"][0][0] == bm.REPO_CKPT and state["loads"][2][0] == bm.REPO_BASE
    for which in bm.ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            rec = json.loads(bm.endpoint_record_path(tmp_path, which, r).read_text())
            assert rec["which"] == which and rec["size"] == bm.SIZE_OUT and rec["family"] == bm.FAMILY
            assert rec["seal_tag"] == bm.PREDICTOR_TAGS_2M and rec["predictor_sha"] == bm.PREDICTOR_SHA_2M
            assert rec["n"] == bt.N_ITEMS and len(rec["bits"]) == bt.N_ITEMS and "step" not in rec
            assert rec["dtype"] == bm.DTYPE_2M
            assert rec["revision"] == bm.entry_which_3b(man, which)["revision"]
    rs = json.loads(bm.rung_set_path(tmp_path).read_text())
    assert set(rs) >= {"R_3B", "R_PRIMARY", "R_ELEVEN_EXTRA", "R_EXTRA", "per_rung", "primary_is_the_nine",
                       "endpoint_file_sha256"}
    stage1 = {r: json.loads(bm.endpoint_record_path(tmp_path, "stage1_final", r).read_text())["correct"] for r in bt.RUNGS}
    assert rs["R_3B"] == bm.rung_set_from_counts_2m(stage1, bg.load_floors())["R_3B"]
    assert rs["R_PRIMARY"] and set(rs["R_PRIMARY"]) <= set(bm.R_CAP_2K)
    assert len(rs["endpoint_file_sha256"]) == 102
    for which in ("stage3_final", "base"):                     # the descriptive loads never drive the rung set
        assert all(json.loads(bm.endpoint_record_path(tmp_path, which, r).read_text())["correct"] == 0 for r in bt.RUNGS)


def test_endpoint_records_carry_the_dtype_constant(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    monkeypatch.setattr(bm, "DTYPE_2M", "float32")
    loaders, _ = _endpoint_loaders()
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    rec = json.loads(bm.endpoint_record_path(tmp_path, "base", "antonym").read_text())
    assert rec["dtype"] == "float32"


def test_endpoint_skip_if_exists_and_dry_run(tmp_path, monkeypatch, capsys):
    _shrink_grid(monkeypatch)
    loaders, state = _endpoint_loaders()
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, dry_run=True, **_fake_seals())
    assert state["loads"] == [] and "would run 102" in capsys.readouterr().out
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    n = len(state["loads"])
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    assert len(state["loads"]) == n
    assert "nothing to do" in capsys.readouterr().out


def test_endpoint_exception_mid_which_leaves_no_rung_set(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, _ = _endpoint_loaders(raise_at_which="base")
    with pytest.raises(RuntimeError, match="boom"):
        ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    assert not bm.rung_set_path(tmp_path).exists()
    assert all(bm.endpoint_record_path(tmp_path, "stage1_final", r).exists() for r in bt.RUNGS)
    assert all(bm.endpoint_record_path(tmp_path, "stage3_final", r).exists() for r in bt.RUNGS)


# ------------------------------------------------------------------ sweep

def _setup_endpoint(tmp_path, *, gate_frac=0.5, digest="Dend", commit=None):
    battery, amap = _amap_and_battery()
    verify_fn = a2d.load_verify()
    man = _manifest()
    e = bm.entry_3b(man, bm.ENDPOINT_STEP_2M)
    commit = commit if commit is not None else e["commit"]
    counts = {}
    for which in bm.ENDPOINT_WHICH_2M:
        ew = bm.entry_which_3b(man, which)
        for rung in bt.RUNGS:
            cap = battery[rung]
            ev = evaluate_items(FakeRunner(amap, gate_frac if which == "stage1_final" else 0.0), cap, verify_fn)
            ckpt = {"revision": ew["revision"], "commit": commit if which == "stage1_final" else ew["commit"],
                    "kind": ew["kind"], "files": list(ew["files"]), "weight_sha256": digest,
                    "config_source": "cs", "tokenizer_source": "ts"}
            rec = bm.endpoint_item_record_2m(rung=rung, cap=cap, ev=ev, ckpt=ckpt, which=which,
                                             seal={"tag": bm.PREDICTOR_TAGS_2M, "sha256": bm.PREDICTOR_SHA_2M}, t_s=0.0)
            p = bm.endpoint_record_path(tmp_path, which, rung)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(rec, indent=1))
            if which == "stage1_final":
                counts[rung] = rec["correct"]
    rs = bm.rung_set_from_counts_2m(counts, bg.load_floors())
    bm.rung_set_path(tmp_path).write_text(json.dumps({**rs, "endpoint_file_sha256": {}}))
    bm.power_path(tmp_path).write_text(json.dumps({"A": {"declared_status": "x"}, "B": {"declared_status": "x"}}))
    return {"battery": battery, "amap": amap, "manifest": man, "entry": e, "commit": commit, "digest": digest}


def _sweep_loaders(*, entry, gate_frac=0.5, digest_gate="Dend", commit_gate=None, frac_by_revision=None,
                   digest_gate_diff=False, commit_gate_diff=False, raise_at_revision=None):
    frac_by_revision = frac_by_revision or {}
    commit_gate = commit_gate if commit_gate is not None else entry["commit"]
    state = {"calls": [], "freed": [], "tok": [], "twin": []}
    battery, amap = _amap_and_battery()

    class M:
        def __init__(self, d): self.d = d

    def checkpoint(e, cache_root, device):
        is_gate = e["revision"] == entry["revision"]
        digest = digest_gate if not (is_gate and digest_gate_diff) else "WRONG-DIGEST"
        commit = commit_gate if not (is_gate and commit_gate_diff) else "0" * 40
        return M(e["revision"]), {"repo": e["repo"], "tensor_digest": digest, "commit": commit,
                                  "config_source": f"cs-{e['revision']}", "sha256": dict(e.get("lfs_sha256", {})),
                                  "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}}

    def twin(config_commit, device):
        state["twin"].append(config_commit)
        return M(bm.TWIN), {"repo": bm.REPO_CKPT, "revision": bm.TWIN, "seed": bm.TWIN_SEED,
                            "config_source": f"{bm.REPO_CKPT}@{config_commit}", "tensor_digest": "Dtwin"}

    def tokenizer(repo, commit):
        state["tok"].append((repo, commit))
        return object()

    def runner(tok, model):
        state["calls"].append(model.d)
        if raise_at_revision == model.d:
            raise RuntimeError("boom")
        frac = gate_frac if model.d == entry["revision"] else frac_by_revision.get(model.d, 0.3)
        return FakeRunner(amap, 0.0 if model.d == bm.TWIN else frac)

    def free(revision, cache_root):
        state["freed"].append(revision)

    return {"checkpoint": checkpoint, "twin": twin, "tokenizer": tokenizer, "runner": runner, "free": free}, state


def test_sweep_refuses_without_endpoint_seal_then_runs_gate1_twin_and_grid(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    man = _manifest()
    e = bm.entry_3b(man, bm.ENDPOINT_STEP_2M)
    loaders, state = _sweep_loaders(entry=e)
    with pytest.raises(RuntimeError, match="endpoint stage"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    _setup_endpoint(tmp_path)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    # order: gate 1 (endpoint), the twin, then the grid ascending minus the endpoint
    assert state["calls"] == [e["revision"], bm.TWIN, bm.entry_3b(man, 40000)["revision"], bm.entry_3b(man, 80000)["revision"]]
    assert state["freed"] == [e["revision"], bm.entry_3b(man, 40000)["revision"], bm.entry_3b(man, 80000)["revision"]]
    assert state["twin"] == [e["commit"]] and (bm.REPO_CKPT, e["commit"]) in state["tok"]
    g = json.loads(bm.gate1_path(tmp_path).read_text())
    assert set(bm.GATE1_FIELDS_2M) <= set(g) and g["prereg_tag"] == bm.PREREG_TAG_2M
    assert all(v == 0 for v in g["bit_diffs"].values()) and all(v == bt.N_ITEMS for v in g["continuations_compared"].values())
    assert bm.gate1_failures_3b(g, {r: json.loads(bm.endpoint_record_path(tmp_path, "stage1_final", r).read_text()) for r in bt.RUNGS}) == []
    esha = bm.endpoint_sha256(tmp_path)
    for step in SHORT_GRID:
        assert sw.records_complete_3b(tmp_path, step)
        rec = json.loads(bm.record_path(tmp_path, step, "antonym").read_text())
        assert rec["step"] == step and rec["seal_tag"] == bm.ENDPOINT_SEAL_TAG_2M and rec["dtype"] == bm.DTYPE_2M
        assert rec["predictor_sha"] == bm.PREDICTOR_SHA_2M and rec["endpoint_sha256"] == esha
        cr = json.loads(bm.checkpoint_record_path(tmp_path, step).read_text())
        assert cr["size"] == bm.SIZE_OUT and cr["step"] == step and cr["repo"] == bm.REPO_CKPT
        assert cr["sha256"] == bm.entry_3b(man, step)["lfs_sha256"] and cr["loading_info"]["missing_keys"] == 0
    assert sw.records_complete_3b(tmp_path, bm.TWIN)
    rt = json.loads(bm.record_path(tmp_path, bm.TWIN, "antonym").read_text())
    assert rt["step"] == bm.TWIN and rt["commit"] is None and rt["kind"] == "from_config" and rt["correct"] == 0
    assert rt["config_source"] == f"{bm.REPO_CKPT}@{e['commit']}" and rt["endpoint_sha256"] == esha
    ct = json.loads(bm.checkpoint_record_path(tmp_path, bm.TWIN).read_text())
    assert ct == bm.twin_checkpoint_record_2m(info={"repo": bm.REPO_CKPT, "revision": bm.TWIN, "seed": bm.TWIN_SEED,
                                                    "config_source": f"{bm.REPO_CKPT}@{e['commit']}", "tensor_digest": "Dtwin"})
    assert not bm.halt_marker_path(tmp_path).exists()


def test_sweep_gate1_diff_halts_with_marker_and_refuses_resume(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path, gate_frac=0.5)
    e = bm.entry_3b(_manifest(), bm.ENDPOINT_STEP_2M)
    loaders, state = _sweep_loaders(entry=e, gate_frac=0.4)       # 2l's finding: 0.4 differs from 0.5 under FakeRunner's 0.499 ceiling
    with pytest.raises(RuntimeError, match="gate 1 smollm3_3b FAILED"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert bm.halt_marker_path(tmp_path).exists()
    assert sum(json.loads(bm.gate1_path(tmp_path).read_text())["bit_diffs"].values()) > 0
    assert state["calls"] == [e["revision"]] and state["freed"] == [e["revision"]] and state["twin"] == []
    assert sw.records_complete_3b(tmp_path, bm.ENDPOINT_STEP_2M)
    with pytest.raises(RuntimeError, match="halted"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert state["calls"] == [e["revision"]]


@pytest.mark.parametrize("kw,needle", [(dict(digest_gate_diff=True), "tensor digest"),
                                       (dict(commit_gate_diff=True), "commit")])
def test_sweep_gate1_digest_or_commit_mismatch_halts(tmp_path, monkeypatch, kw, needle):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bm.entry_3b(_manifest(), bm.ENDPOINT_STEP_2M)
    loaders, _ = _sweep_loaders(entry=e, **kw)
    with pytest.raises(RuntimeError, match="gate 1 smollm3_3b FAILED"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert any(needle in x for x in bm.halt_marker_path(tmp_path).read_text().splitlines())


def test_sweep_resume_skips_complete_steps_and_reenters_incomplete_ones(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    man = _manifest()
    e = bm.entry_3b(man, bm.ENDPOINT_STEP_2M)
    loaders, state = _sweep_loaders(entry=e, raise_at_revision=bm.entry_3b(man, 80000)["revision"])
    with pytest.raises(RuntimeError, match="boom"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert state["freed"][-1] == bm.entry_3b(man, 80000)["revision"]
    assert not sw.records_complete_3b(tmp_path, 80000)
    bm.checkpoint_record_path(tmp_path, 40000).unlink()
    assert not sw.records_complete_3b(tmp_path, 40000)
    bm.checkpoint_record_path(tmp_path, bm.TWIN).unlink()      # the twin re-enters too (2i R-3)
    assert not sw.records_complete_3b(tmp_path, bm.TWIN)
    loaders2, state2 = _sweep_loaders(entry=e)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders2, **_fake_seals())
    assert state2["calls"] == [bm.TWIN, bm.entry_3b(man, 40000)["revision"], bm.entry_3b(man, 80000)["revision"]]
    assert all(sw.records_complete_3b(tmp_path, s) for s in (bm.TWIN, 40000, 80000))


def test_sweep_resume_reruns_gate1_failures_check_on_stale_disk_record(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bm.entry_3b(_manifest(), bm.ENDPOINT_STEP_2M)
    loaders, _ = _sweep_loaders(entry=e)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    g = json.loads(bm.gate1_path(tmp_path).read_text())
    g["prereg_tag"] = "exp2l-preregistered"
    bm.gate1_path(tmp_path).write_text(json.dumps(g))
    loaders2, state2 = _sweep_loaders(entry=e)
    with pytest.raises(RuntimeError, match="record on disk fails re-derivation"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders2, **_fake_seals())
    assert state2["calls"] == []


def test_sweep_dry_run_loads_nothing(tmp_path, monkeypatch, capsys):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bm.entry_3b(_manifest(), bm.ENDPOINT_STEP_2M)
    loaders, state = _sweep_loaders(entry=e)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, dry_run=True, **_fake_seals())
    out = capsys.readouterr().out
    assert state["calls"] == [] and "gate1, " in out and "'twin'" in out


def test_sweep_refuses_endpoint_seal_drift(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bm.entry_3b(_manifest(), bm.ENDPOINT_STEP_2M)
    loaders, _ = _sweep_loaders(entry=e)
    seals = _fake_seals()
    seals["blobs_bound"] = lambda tag, paths, repo_root=None: (["x"] if tag == bm.ENDPOINT_SEAL_TAG_2M else [])
    with pytest.raises(RuntimeError, match="exp2m-endpoint-sealed.*does not bind"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **seals)
    paths = sw.endpoint_seal_blob_paths(tmp_path)
    assert len(paths) == 104 and "results/endpoint/rung_set_2m.json" in paths and "results/endpoint/power_2m.json" in paths


# -------------------------------------------------------------- preflight

def _preflight_loaders(tmp_path, *, nonfinite=0, write_stray=False):
    battery, amap = _amap_and_battery()
    # FakeRunner's frac=0.5 always looks up self.answers[p] for the first
    # 20 items regardless of render (i/1000 < 0.5 for i in 0..19), and
    # preflight's own runner is shared across the plain and bos-prefixed
    # passes (one loader["runner"] call per model load) — so the
    # BOS-prefixed prompt strings need entries too, mapped to the same
    # correct answers, or the second pass KeyErrors on prompts _amap_and_
    # battery() never registered.
    amap.update({bm.BOS_TOKEN_2M + p: a for p, a in list(amap.items())})
    state = {"thin": [], "ckpt": [], "freed": [], "finite": []}

    class M:
        d = "m"

    def thin(repo, commit, device):
        state["thin"].append((repo, commit))
        if write_stray:
            (tmp_path / "results").mkdir(exist_ok=True)
            (tmp_path / "results" / "stray.json").write_text("{}")
        return M(), object(), {"repo": repo, "tensor_digest": "D", "commit": commit}

    def checkpoint(entry, cache_root, device):
        state["ckpt"].append(entry["revision"])
        return M(), {"repo": entry["repo"], "tensor_digest": "D", "commit": entry["commit"]}

    def finite(model, tok, prompt):
        state["finite"].append(prompt[-20:])
        return {"n_nonfinite": nonfinite, "max_abs": 12.5}

    loaders = {"thin": thin, "checkpoint": checkpoint, "tokenizer": lambda repo, c: object(),
               "runner": lambda tok, model: FakeRunner(amap, 0.5),
               "free": lambda rev, cache_root: state["freed"].append(rev),
               "check_tokenizer": lambda tok: None, "memory": lambda: 12345, "finite": finite,
               "render_ids": lambda tok, text: [48, 25]}
    return loaders, state


def test_preflight_prints_both_renders_and_writes_nothing(tmp_path, monkeypatch, capsys):
    _shrink_grid(monkeypatch)
    loaders, state = _preflight_loaders(tmp_path)
    pf.run(root=tmp_path, loaders=loaders, cache_root=tmp_path / "c", checkpoint_step=40000)
    out = capsys.readouterr().out
    man = _manifest()
    assert state["thin"] == [(bm.REPO_BASE, bm.entry_base_3b(man)["commit"])]
    assert state["ckpt"] == [bm.entry_3b(man, 40000)["revision"]] and state["freed"] == state["ckpt"]
    assert len(state["finite"]) == 2                                   # one finiteness probe per load
    assert out.count("[2m preflight] antonym") == 20 and out.count("[2m preflight] add3_mid") == 20
    assert out.count("[2m preflight] bos antonym") == 20 and out.count("[2m preflight] bos add3_mid") == 20
    assert out.count("[2m preflight] ckpt antonym") == 20 and out.count("[2m preflight] ckpt bos antonym") == 20
    assert "verify=" in out and "batch_size 16" in out and "dtype float16" in out
    assert "mps_allocated_bytes 12345" in out and "n_nonfinite 0" in out and "plain render ids [48, 25]" in out
    assert not (tmp_path / "results").exists()


def test_preflight_refuses_on_nonfinite_logits(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, state = _preflight_loaders(tmp_path, nonfinite=3)
    with pytest.raises(RuntimeError, match="non-finite"):
        pf.run(root=tmp_path, loaders=loaders, cache_root=tmp_path / "c", checkpoint_step=40000)
    assert state["ckpt"] == []                                          # refused at the first (thin) load


def test_preflight_refuses_if_it_wrote_under_results(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, _ = _preflight_loaders(tmp_path, write_stray=True)
    with pytest.raises(RuntimeError, match="preflight wrote under"):
        pf.run(root=tmp_path, loaders=loaders, cache_root=tmp_path / "c", checkpoint_step=40000)
