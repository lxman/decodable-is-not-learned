# experiments/exp2n/tests/test_stages_2n.py
"""The 2n stage runners' control flow with FAKE loaders — no torch, no
network, no frozen tree touched. Mirrors 2m's test_stages_2m with 2n's
deltas: THREE thin loads at the endpoint stage (stage1_final,
stage2_final, main) from ONE repo; the rung set from stage1_final
only; the dtype override on every record; gate 1 = the endpoint through
the candidate loader vs the committed stage1_final records; the seeded
TWIN after gate 1 (its own record shapes, never freed — nothing was
downloaded); the preflight's two renders (now BOTH pinned — a
`BosRunner`-wrapped pass and a plain-runner pass, not a string prefix)
plus the eos facts and peak memory; the render/eos_stop_id pins every
record carries (dials n, o)."""
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
from experiments.exp2n import analyze_2n as an
from experiments.exp2n import battery_2n as bn
from experiments.exp2n.run import endpoint_2n as ep
from experiments.exp2n.run import preflight_2n as pf
from experiments.exp2n.run import sweep_2n as sw

SHORT_GRID = (10000, 20000, bn.ENDPOINT_STEP_2N)
SHORT_SUBSET = (20000, bn.ENDPOINT_STEP_2N)


@pytest.fixture(autouse=True)
def _blobs_that_exist(monkeypatch):
    subset = tuple(r for r in bn.INSTRUMENT_BLOBS_2N if (bn.REPO / r).is_file())
    monkeypatch.setattr(bn, "INSTRUMENT_BLOBS_2N", subset)


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
    asserted in test_battery_2n); the grid shrunk to SHORT_GRID."""
    return json.loads(bn.CHECKPOINTS_PATH.read_text())


def _shrink_grid(monkeypatch):
    monkeypatch.setattr(bn, "GRID_COMMA", SHORT_GRID)
    monkeypatch.setattr(bn, "EVERY40K_SUBSET_2N", SHORT_SUBSET)
    monkeypatch.setattr(bn, "load_manifest_comma", lambda path, sha_pin: _manifest())


def _fake_seals():
    return dict(tag_exists=lambda t: True,
                blob_sha=lambda tag, rel: bg.sha256_file(bn.REPO / rel) if (bn.REPO / rel).is_file() else None,
                blobs_bound=lambda tag, paths, repo_root=None: [])


def _which_of(repo, commit):
    man = _manifest()
    for which in bn.ENDPOINT_WHICH_2N:
        e = bn.entry_which_comma(man, which)
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
                                                              "mismatched_keys": 0},
                                             "config_eos_token_id": 2, "config_bos_token_id": 1,
                                             "generation_eos_token_id": 3}

    battery, amap = _amap_and_battery()

    def runner(tok, model):
        which = _which_of(*model.d)
        if raise_at_which == which:
            raise RuntimeError("boom")
        return FakeRunner(amap, frac_by_which.get(which, 0.5))

    return {"thin": thin, "runner": runner}, state


# ------------------------------------------------------- predictor seals

def test_require_predictor_seals_2n_rederives_predictor_sha_and_refuses_drift():
    got = ep.require_predictor_seals_2n(root_2i=bi.EXP2I, root_2k=bk.EXP2K,
                                        **{k: v for k, v in _fake_seals().items() if k != "blob_sha"})
    assert got["predictor_sha"] == bn.PREDICTOR_SHA_2N
    assert got["seal_2k"]["sha256"] == bn.SEAL_2K_SHA256 and got["seal_2i"]["sha256"] == bn.SEAL_2I_SHA256
    with pytest.raises(RuntimeError, match="does not bind"):
        ep.require_predictor_seals_2n(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: True,
                                      blobs_bound=lambda tag, paths, repo_root=None: ["x"] if tag == bk.SEAL_TAG_2K else [])
    with pytest.raises(RuntimeError, match="does not exist"):
        ep.require_predictor_seals_2n(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: t != bi.PREDICTOR_SEAL_TAG,
                                      blobs_bound=lambda tag, paths, repo_root=None: [])


@pytest.mark.parametrize("attr", ["SEAL_2I_SHA256", "SEAL_2K_SHA256"])
def test_require_predictor_seals_2n_refuses_a_seal_off_its_literal(monkeypatch, attr):
    monkeypatch.setattr(bn, attr, "0" * 64)
    with pytest.raises(RuntimeError, match="literal"):
        ep.require_predictor_seals_2n(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: True,
                                      blobs_bound=lambda tag, paths, repo_root=None: [])


def test_require_predictor_seals_2n_refuses_a_stale_composite(monkeypatch):
    monkeypatch.setattr(bn, "PREDICTOR_SHA_2N", "0" * 64)
    with pytest.raises(RuntimeError, match="does not re-derive"):
        ep.require_predictor_seals_2n(root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=lambda t: True,
                                      blobs_bound=lambda tag, paths, repo_root=None: [])


@pytest.mark.slow
def test_predictor_seals_bind_for_real():
    got = ep.require_predictor_seals_2n(root_2i=bi.EXP2I, root_2k=bk.EXP2K)
    assert got["predictor_sha"] == bn.PREDICTOR_SHA_2N


def test_endpoint_seal_path_sets_agree_three_ways(tmp_path):
    for p in an._endpoint_seal_paths_2n(tmp_path):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x")
    a = {str(p.relative_to(tmp_path)) for p in an._endpoint_seal_paths_2n(tmp_path)}
    b = set(bn.endpoint_files(tmp_path))
    c = set(sw.endpoint_seal_blob_paths(tmp_path))
    assert a == b == c
    assert len(a) == 2 + len(bn.ENDPOINT_WHICH_2N) * len(bt.RUNGS) == 104


# --------------------------------------------------------------- endpoint

def test_endpoint_refuses_without_tag_or_frozen_pin(tmp_path, monkeypatch):
    with pytest.raises(RuntimeError, match="does not exist"):
        ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=_endpoint_loaders()[0],
               tag_exists=lambda t: False, blob_sha=lambda t, r: None,
               blobs_bound=lambda tag, paths, repo_root=None: [])
    monkeypatch.setattr(bn, "FROZEN_SHA256_2N", {})
    with pytest.raises(RuntimeError, match="not pinned"):
        ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=_endpoint_loaders()[0], **_fake_seals())


def test_endpoint_writes_three_whichs_and_the_rung_set_from_stage1_final(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, state = _endpoint_loaders(frac_by_which={"stage1_final": 0.9, "stage2_final": 0.0, "main": 0.0})
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    man = _manifest()
    assert state["loads"] == [(bn.entry_which_comma(man, w)["repo"], bn.entry_which_comma(man, w)["commit"])
                              for w in bn.ENDPOINT_WHICH_2N]
    assert all(l[0] == bn.REPO_COMMA for l in state["loads"])
    for which in bn.ENDPOINT_WHICH_2N:
        for r in bt.RUNGS:
            rec = json.loads(bn.endpoint_record_path(tmp_path, which, r).read_text())
            assert rec["which"] == which and rec["size"] == bn.SIZE_OUT and rec["family"] == bn.FAMILY
            assert rec["seal_tag"] == bn.PREDICTOR_TAGS_2N and rec["predictor_sha"] == bn.PREDICTOR_SHA_2N
            assert rec["n"] == bt.N_ITEMS and len(rec["bits"]) == bt.N_ITEMS and "step" not in rec
            assert rec["dtype"] == bn.DTYPE_2N
            assert rec["revision"] == bn.entry_which_comma(man, which)["revision"]
    rs = json.loads(bn.rung_set_path(tmp_path).read_text())
    assert set(rs) >= {"R_COMMA", "R_PRIMARY", "R_ELEVEN_EXTRA", "R_EXTRA", "per_rung", "primary_is_the_nine",
                       "endpoint_file_sha256"}
    stage1 = {r: json.loads(bn.endpoint_record_path(tmp_path, "stage1_final", r).read_text())["correct"] for r in bt.RUNGS}
    assert rs["R_COMMA"] == bn.rung_set_from_counts_2n(stage1, bg.load_floors())["R_COMMA"]
    assert rs["R_PRIMARY"] and set(rs["R_PRIMARY"]) <= set(bn.R_CAP_2K)
    assert len(rs["endpoint_file_sha256"]) == 102
    for which in ("stage2_final", "main"):                     # the descriptive loads never drive the rung set
        assert all(json.loads(bn.endpoint_record_path(tmp_path, which, r).read_text())["correct"] == 0 for r in bt.RUNGS)


def test_endpoint_records_carry_the_dtype_constant(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    monkeypatch.setattr(bn, "DTYPE_2N", "float32")
    loaders, _ = _endpoint_loaders()
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    rec = json.loads(bn.endpoint_record_path(tmp_path, "main", "antonym").read_text())
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
    loaders, _ = _endpoint_loaders(raise_at_which="main")
    with pytest.raises(RuntimeError, match="boom"):
        ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    assert not bn.rung_set_path(tmp_path).exists()
    assert all(bn.endpoint_record_path(tmp_path, "stage1_final", r).exists() for r in bt.RUNGS)
    assert all(bn.endpoint_record_path(tmp_path, "stage2_final", r).exists() for r in bt.RUNGS)


# ------------------------------------------------------------------ sweep

def _setup_endpoint(tmp_path, *, gate_frac=0.5, digest="Dend", commit=None):
    battery, amap = _amap_and_battery()
    verify_fn = a2d.load_verify()
    man = _manifest()
    e = bn.entry_comma(man, bn.ENDPOINT_STEP_2N)
    commit = commit if commit is not None else e["commit"]
    counts = {}
    for which in bn.ENDPOINT_WHICH_2N:
        ew = bn.entry_which_comma(man, which)
        for rung in bt.RUNGS:
            cap = battery[rung]
            ev = evaluate_items(FakeRunner(amap, gate_frac if which == "stage1_final" else 0.0), cap, verify_fn)
            ckpt = {"revision": ew["revision"], "commit": commit if which == "stage1_final" else ew["commit"],
                    "kind": ew["kind"], "files": list(ew["files"]), "weight_sha256": digest,
                    "config_source": "cs", "tokenizer_source": "ts"}
            rec = bn.endpoint_item_record_2n(rung=rung, cap=cap, ev=ev, ckpt=ckpt, which=which,
                                             seal={"tag": bn.PREDICTOR_TAGS_2N, "sha256": bn.PREDICTOR_SHA_2N}, t_s=0.0)
            p = bn.endpoint_record_path(tmp_path, which, rung)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(rec, indent=1))
            if which == "stage1_final":
                counts[rung] = rec["correct"]
    rs = bn.rung_set_from_counts_2n(counts, bg.load_floors())
    bn.rung_set_path(tmp_path).write_text(json.dumps({**rs, "endpoint_file_sha256": {}}))
    bn.power_path(tmp_path).write_text(json.dumps({"A": {"declared_status": "x"}, "B": {"declared_status": "x"}}))
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
                                  "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0},
                                  "config_eos_token_id": 2, "config_bos_token_id": 1, "generation_eos_token_id": 3}

    def twin(config_commit, device):
        state["twin"].append(config_commit)
        return M(bn.TWIN), {"repo": bn.REPO_COMMA, "revision": bn.TWIN, "seed": bn.TWIN_SEED,
                            "config_source": f"{bn.REPO_COMMA}@{config_commit}", "tensor_digest": "Dtwin",
                            "config_eos_token_id": 2, "config_bos_token_id": 1, "generation_eos_token_id": 3}

    def tokenizer(repo, commit):
        state["tok"].append((repo, commit))
        return object()

    def runner(tok, model):
        state["calls"].append(model.d)
        if raise_at_revision == model.d:
            raise RuntimeError("boom")
        frac = gate_frac if model.d == entry["revision"] else frac_by_revision.get(model.d, 0.3)
        return FakeRunner(amap, 0.0 if model.d == bn.TWIN else frac)

    def free(revision, cache_root):
        state["freed"].append(revision)

    return {"checkpoint": checkpoint, "twin": twin, "tokenizer": tokenizer, "runner": runner, "free": free}, state


def test_sweep_refuses_without_endpoint_seal_then_runs_gate1_twin_and_grid(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    man = _manifest()
    e = bn.entry_comma(man, bn.ENDPOINT_STEP_2N)
    loaders, state = _sweep_loaders(entry=e)
    with pytest.raises(RuntimeError, match="endpoint stage"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    _setup_endpoint(tmp_path)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    # order: gate 1 (endpoint), the twin, then the grid ascending minus the endpoint
    assert state["calls"] == [e["revision"], bn.TWIN, bn.entry_comma(man, 10000)["revision"], bn.entry_comma(man, 20000)["revision"]]
    assert state["freed"] == [e["revision"], bn.entry_comma(man, 10000)["revision"], bn.entry_comma(man, 20000)["revision"]]
    assert state["twin"] == [e["commit"]] and (bn.REPO_COMMA, e["commit"]) in state["tok"]
    g = json.loads(bn.gate1_path(tmp_path).read_text())
    assert set(bn.GATE1_FIELDS_2N) <= set(g) and g["prereg_tag"] == bn.PREREG_TAG_2N
    assert all(v == 0 for v in g["bit_diffs"].values()) and all(v == bt.N_ITEMS for v in g["continuations_compared"].values())
    assert bn.gate1_failures_comma(g, {r: json.loads(bn.endpoint_record_path(tmp_path, "stage1_final", r).read_text()) for r in bt.RUNGS}) == []
    esha = bn.endpoint_sha256(tmp_path)
    for step in SHORT_GRID:
        assert sw.records_complete_comma(tmp_path, step)
        rec = json.loads(bn.record_path(tmp_path, step, "antonym").read_text())
        assert rec["step"] == step and rec["seal_tag"] == bn.ENDPOINT_SEAL_TAG_2N and rec["dtype"] == bn.DTYPE_2N
        assert rec["predictor_sha"] == bn.PREDICTOR_SHA_2N and rec["endpoint_sha256"] == esha
        cr = json.loads(bn.checkpoint_record_path(tmp_path, step).read_text())
        assert cr["size"] == bn.SIZE_OUT and cr["step"] == step and cr["repo"] == bn.REPO_COMMA
        assert cr["sha256"] == bn.entry_comma(man, step)["lfs_sha256"] and cr["loading_info"]["missing_keys"] == 0
    assert sw.records_complete_comma(tmp_path, bn.TWIN)
    rt = json.loads(bn.record_path(tmp_path, bn.TWIN, "antonym").read_text())
    assert rt["step"] == bn.TWIN and rt["commit"] is None and rt["kind"] == "from_config" and rt["correct"] == 0
    assert rt["config_source"] == f"{bn.REPO_COMMA}@{e['commit']}" and rt["endpoint_sha256"] == esha
    ct = json.loads(bn.checkpoint_record_path(tmp_path, bn.TWIN).read_text())
    assert ct == bn.twin_checkpoint_record_2n(info={"repo": bn.REPO_COMMA, "revision": bn.TWIN, "seed": bn.TWIN_SEED,
                                                    "config_source": f"{bn.REPO_COMMA}@{e['commit']}", "tensor_digest": "Dtwin",
                                                    "config_eos_token_id": 2, "config_bos_token_id": 1,
                                                    "generation_eos_token_id": 3})
    assert not bn.halt_marker_path(tmp_path).exists()


def test_run_twin_reads_the_config_commit_and_records_itself_only_after_every_rung(tmp_path, monkeypatch):
    """Mutation closure (Task 5, #47 and #51). Two properties of
    `run_twin` no other case observes: (a) the twin's tokenizer is read
    at the ENDPOINT's config commit — the stage-1 config the from_config
    referent was built from — not at the main revision; (b) its bespoke
    checkpoint record is written AFTER the rung loop, so an interruption
    mid-twin leaves no checkpoint record standing for rungs that were
    never evaluated (2i's R-3 resume rule: `records_complete_comma`
    reads that record as 'this step is done')."""
    man = _manifest()
    e = bn.entry_comma(man, bn.ENDPOINT_STEP_2N)
    entry_twin = bn.entry_comma(man, bn.TWIN)
    loaders, state = _sweep_loaders(entry=e)
    battery = bg.load_battery()
    verify = a2d.load_verify()
    real_eval, calls = sw.evaluate_items, {"n": 0}

    def _boom(runner, cap, verify_fn):
        calls["n"] += 1
        if calls["n"] == 3:
            raise RuntimeError("interrupted mid-twin")
        return real_eval(runner, cap, verify_fn)

    monkeypatch.setattr(sw, "evaluate_items", _boom)
    with pytest.raises(RuntimeError, match="interrupted mid-twin"):
        sw.run_twin(out_root=tmp_path, manifest=man, device="cpu", battery=battery, verify_fn=verify,
                    endpoint_sha="E" * 64, loaders=loaders)
    assert calls["n"] == 3 and state["twin"] == [entry_twin["config_commit"]]
    assert state["tok"] == [(bn.REPO_COMMA, entry_twin["config_commit"])]
    assert entry_twin["config_commit"] == e["commit"] != bn.REV_MAIN_2N
    assert bn.record_path(tmp_path, bn.TWIN, bt.RUNGS[0]).exists()          # two rungs did land
    assert not bn.checkpoint_record_path(tmp_path, bn.TWIN).exists()
    assert not sw.records_complete_comma(tmp_path, bn.TWIN)


def test_sweep_gate1_diff_halts_with_marker_and_refuses_resume(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path, gate_frac=0.5)
    e = bn.entry_comma(_manifest(), bn.ENDPOINT_STEP_2N)
    loaders, state = _sweep_loaders(entry=e, gate_frac=0.4)       # 2l's finding: 0.4 differs from 0.5 under FakeRunner's 0.499 ceiling
    with pytest.raises(RuntimeError, match="gate 1 comma_7b FAILED"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert bn.halt_marker_path(tmp_path).exists()
    assert sum(json.loads(bn.gate1_path(tmp_path).read_text())["bit_diffs"].values()) > 0
    assert state["calls"] == [e["revision"]] and state["freed"] == [e["revision"]] and state["twin"] == []
    assert sw.records_complete_comma(tmp_path, bn.ENDPOINT_STEP_2N)
    with pytest.raises(RuntimeError, match="halted"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert state["calls"] == [e["revision"]]


@pytest.mark.parametrize("kw,needle", [(dict(digest_gate_diff=True), "tensor digest"),
                                       (dict(commit_gate_diff=True), "commit")])
def test_sweep_gate1_digest_or_commit_mismatch_halts(tmp_path, monkeypatch, kw, needle):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bn.entry_comma(_manifest(), bn.ENDPOINT_STEP_2N)
    loaders, _ = _sweep_loaders(entry=e, **kw)
    with pytest.raises(RuntimeError, match="gate 1 comma_7b FAILED"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert any(needle in x for x in bn.halt_marker_path(tmp_path).read_text().splitlines())


def test_sweep_resume_skips_complete_steps_and_reenters_incomplete_ones(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    man = _manifest()
    e = bn.entry_comma(man, bn.ENDPOINT_STEP_2N)
    loaders, state = _sweep_loaders(entry=e, raise_at_revision=bn.entry_comma(man, 20000)["revision"])
    with pytest.raises(RuntimeError, match="boom"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    assert state["freed"][-1] == bn.entry_comma(man, 20000)["revision"]
    assert not sw.records_complete_comma(tmp_path, 20000)
    bn.checkpoint_record_path(tmp_path, 10000).unlink()
    assert not sw.records_complete_comma(tmp_path, 10000)
    bn.checkpoint_record_path(tmp_path, bn.TWIN).unlink()      # the twin re-enters too (2i R-3)
    assert not sw.records_complete_comma(tmp_path, bn.TWIN)
    loaders2, state2 = _sweep_loaders(entry=e)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders2, **_fake_seals())
    assert state2["calls"] == [bn.TWIN, bn.entry_comma(man, 10000)["revision"], bn.entry_comma(man, 20000)["revision"]]
    assert all(sw.records_complete_comma(tmp_path, s) for s in (bn.TWIN, 10000, 20000))


def test_sweep_resume_reruns_gate1_failures_check_on_stale_disk_record(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bn.entry_comma(_manifest(), bn.ENDPOINT_STEP_2N)
    loaders, _ = _sweep_loaders(entry=e)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **_fake_seals())
    g = json.loads(bn.gate1_path(tmp_path).read_text())
    g["prereg_tag"] = "exp2m-preregistered"
    bn.gate1_path(tmp_path).write_text(json.dumps(g))
    loaders2, state2 = _sweep_loaders(entry=e)
    with pytest.raises(RuntimeError, match="record on disk fails re-derivation"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders2, **_fake_seals())
    assert state2["calls"] == []


def test_sweep_dry_run_loads_nothing(tmp_path, monkeypatch, capsys):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bn.entry_comma(_manifest(), bn.ENDPOINT_STEP_2N)
    loaders, state = _sweep_loaders(entry=e)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, dry_run=True, **_fake_seals())
    out = capsys.readouterr().out
    assert state["calls"] == [] and "gate1, " in out and "'twin'" in out


def test_sweep_refuses_endpoint_seal_drift(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    _setup_endpoint(tmp_path)
    e = bn.entry_comma(_manifest(), bn.ENDPOINT_STEP_2N)
    loaders, _ = _sweep_loaders(entry=e)
    seals = _fake_seals()
    seals["blobs_bound"] = lambda tag, paths, repo_root=None: (["x"] if tag == bn.ENDPOINT_SEAL_TAG_2N else [])
    with pytest.raises(RuntimeError, match="exp2n-endpoint-sealed.*does not bind"):
        sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=loaders, **seals)
    paths = sw.endpoint_seal_blob_paths(tmp_path)
    assert len(paths) == 104 and "results/endpoint/rung_set_2n.json" in paths and "results/endpoint/power_2n.json" in paths


# -------------------------------------------------------------- preflight

def _preflight_loaders(tmp_path, *, nonfinite=0, write_stray=False):
    battery, amap = _amap_and_battery()
    # FakeRunner's frac=0.5 always looks up self.answers[p] for the first
    # 20 items regardless of render (i/1000 < 0.5 for i in 0..19), and
    # preflight's own runner is shared across the plain and BOS-prefixed
    # passes (one loader["runner"]/loader["plain_runner"] call per model
    # load) — so the BOS-prefixed prompt strings need entries too, mapped
    # to the same correct answers, or the pinned pass KeyErrors on
    # prompts _amap_and_battery() never registered.
    amap.update({bn.BOS_TOKEN_2N + p: a for p, a in list(amap.items())})
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
               "runner": lambda tok, model: bn.BosRunner(FakeRunner(amap, 0.5)),
               "plain_runner": lambda tok, model: FakeRunner(amap, 0.5),
               "free": lambda rev, cache_root: state["freed"].append(rev),
               "check_tokenizer": lambda tok: None,
               "eos_facts": lambda model: {"config_eos_token_id": 2, "config_bos_token_id": 1,
                                           "generation_eos_token_id": 3},
               "memory": lambda: {"current": 12345, "peak": 23456}, "finite": finite,
               "render_ids": lambda tok, text: [2, 52, 29] if text.startswith(bn.BOS_TOKEN_2N) else [52, 29]}
    return loaders, state


def test_preflight_prints_both_renders_and_writes_nothing(tmp_path, monkeypatch, capsys):
    _shrink_grid(monkeypatch)
    loaders, state = _preflight_loaders(tmp_path)
    pf.run(root=tmp_path, loaders=loaders, cache_root=tmp_path / "c", checkpoint_step=10000)
    out = capsys.readouterr().out
    man = _manifest()
    assert state["thin"] == [(bn.REPO_COMMA, bn.entry_main_comma(man)["commit"])]
    assert state["ckpt"] == [bn.entry_comma(man, 10000)["revision"]] and state["freed"] == state["ckpt"]
    assert len(state["finite"]) == 2                                   # one finiteness probe per load
    assert out.count("[2n preflight] antonym") == 20 and out.count("[2n preflight] add3_mid") == 20
    assert out.count("[2n preflight] plain antonym") == 20 and out.count("[2n preflight] plain add3_mid") == 20
    assert out.count("[2n preflight] ckpt antonym") == 20 and out.count("[2n preflight] ckpt plain antonym") == 20
    assert "verify=" in out and "batch_size 16" in out and "dtype float16" in out
    assert "mps_allocated_bytes 12345" in out and "n_nonfinite 0" in out and "plain render ids [52, 29]" in out
    assert not (tmp_path / "results").exists()


def test_preflight_refuses_on_nonfinite_logits(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, state = _preflight_loaders(tmp_path, nonfinite=3)
    with pytest.raises(RuntimeError, match="non-finite"):
        pf.run(root=tmp_path, loaders=loaders, cache_root=tmp_path / "c", checkpoint_step=10000)
    assert state["ckpt"] == []                                          # refused at the first (thin) load


def test_preflight_refuses_if_it_wrote_under_results(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, _ = _preflight_loaders(tmp_path, write_stray=True)
    with pytest.raises(RuntimeError, match="preflight wrote under"):
        pf.run(root=tmp_path, loaders=loaders, cache_root=tmp_path / "c", checkpoint_step=10000)


# ----------------------------------------------------- render / eos-stop-id

def test_records_carry_render_and_eos_stop_id(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, _ = _endpoint_loaders()
    ep.run(root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, loaders=loaders, **_fake_seals())
    for which in bn.ENDPOINT_WHICH_2N:
        rec = json.loads(bn.endpoint_record_path(tmp_path, which, "antonym").read_text())
        assert rec["render"] == bn.RENDER_2N == "bos" and rec["eos_stop_id"] == bn.EOS_STOP_ID_2N == 3
    e = bn.entry_comma(_manifest(), bn.ENDPOINT_STEP_2N)
    sl, _ = _sweep_loaders(entry=e)
    _setup_endpoint(tmp_path)
    sw.run(out_root=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=tmp_path / "c", loaders=sl, **_fake_seals())
    for step in SHORT_GRID + (bn.TWIN,):
        rec = json.loads(bn.record_path(tmp_path, step, "antonym").read_text())
        assert rec["render"] == "bos" and rec["eos_stop_id"] == 3
    cr = json.loads(bn.checkpoint_record_path(tmp_path, 20000).read_text())
    assert cr["config_eos_token_id"] == 2 and cr["generation_eos_token_id"] == 3
    ct = json.loads(bn.checkpoint_record_path(tmp_path, bn.TWIN).read_text())
    assert ct["generation_eos_token_id"] == 3


def test_real_loaders_wrap_the_harness_in_bos_runner(monkeypatch):
    """The production runner factories (never executed against a model in
    tests) must return a BosRunner around HFRunner — the render is a
    property of the factory, not of the caller."""
    import sys
    import types
    fake_harness = types.SimpleNamespace(HFRunner=lambda tok, model, batch_size: types.SimpleNamespace(batch_size=batch_size, generate=lambda p, k: p))
    monkeypatch.setitem(sys.modules, "harness", fake_harness)
    for mod in (ep, sw):
        r = mod.real_loaders(16)["runner"](object(), object())
        assert isinstance(r, bn.BosRunner) and r.batch_size == 16
        assert r.generate(["x"], 3) == [bn.BOS_TOKEN_2N + "x"]
    r = pf.real_loaders(16)["runner"](object(), object())
    assert isinstance(r, bn.BosRunner)
    plain = pf.real_loaders(16)["plain_runner"](object(), object())
    assert not isinstance(plain, bn.BosRunner) and plain.generate(["x"], 3) == ["x"]


def test_preflight_prints_eos_facts_and_peak_memory(tmp_path, monkeypatch, capsys):
    _shrink_grid(monkeypatch)
    loaders, _ = _preflight_loaders(tmp_path)
    pf.run(root=tmp_path, loaders=loaders, cache_root=tmp_path / "c", checkpoint_step=10000)
    out = capsys.readouterr().out
    assert out.count("config eos 2 | generation eos 3") == 2          # once per load
    assert "bos render ids [2, 52, 29]" in out and "plain render ids [52, 29]" in out
    assert "peak_mps_bytes" in out
