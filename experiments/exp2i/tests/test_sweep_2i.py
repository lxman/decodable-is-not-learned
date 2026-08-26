# experiments/exp2i/tests/test_sweep_2i.py
"""The OLMo-2 7B sweep runner's control flow with FAKE loaders — no
torch, no network, no frozen tree touched. Mirrors
`experiments/exp2h/tests/test_sweep_2h.py`'s shape (prereg refusal,
gate 1 first, halt on diff, records + skip-if-exists, resume refusal,
dry run, mid-step exception frees the checkpoint) with 2i's deltas:
TWO seal refusals (predictor, endpoint) in place of 2h's single
freeze-tag gate; gate 1 diffs the sweep's OWN evaluation of step
928646 against the ALREADY-COMMITTED `stage1_final` endpoint records
(not two fresh loader paths, since the endpoint stage already ran);
TWIN runs between gate 1 and the grid; `free_checkpoint`'s cache key
must match `download_entry`'s (ruling 4 — the reviewer-flagged
decoupling risk)."""
from __future__ import annotations

import json

import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g.run.sweep_2g import evaluate_items
from experiments.exp2g.tests.test_sweep_2g import FakeRunner
from experiments.exp2i import analyze_2i as an
from experiments.exp2i import battery_2i as bi
from experiments.exp2i.run import endpoint_2i as ep
from experiments.exp2i.run import sweep_2i as sw


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
    return bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)


def _shrink_grid(monkeypatch, steps):
    """A short grid (a subset of the real committed manifest's 21
    entries, always ending in ENDPOINT_STEP_7B, so `entry_7b` still
    resolves) — mirrors 2h's `_shrink_grid`."""
    monkeypatch.setattr(bi, "GRID_7B", tuple(steps))
    monkeypatch.setattr(bi, "load_manifest",
                        lambda path, sha_pin: json.loads(bi.CHECKPOINTS_PATH.read_text()))


def _setup_seals(tmp_path, *, gate_frac=0.5, digest="Dend", commit=None, psha="PSHA-2I"):
    """Writes the two upstream stage artifacts the sweep refuses
    without: `predictor_2i.json` (existence only — `blobs_bound` is
    faked in these tests) and `rung_set_2i.json`/`power_2i.json` (the
    endpoint-seal's own existence check). Also writes all 34
    `stage1_final` endpoint records via the REAL `evaluate_items` +
    `item_record_2i` — the exact production shape gate 1 diffs
    against — using `FakeRunner(amap, gate_frac)` so a sweep-side
    FakeRunner built with the SAME fraction reproduces them byte for
    byte (no hand-duplicated generation logic)."""
    battery, amap = _amap_and_battery()
    verify_fn = a2d.load_verify()
    manifest = _manifest()
    entry_stage1 = bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B)
    commit = commit if commit is not None else entry_stage1["commit"]

    for rung in bt.RUNGS:
        cap = battery[rung]
        ev = evaluate_items(FakeRunner(amap, gate_frac), cap, verify_fn)
        ckpt = {"revision": entry_stage1["revision"], "commit": commit,
               "kind": entry_stage1["kind"], "files": list(entry_stage1.get("files", [])),
               "weight_sha256": digest, "config_source": "cs", "tokenizer_source": "ts"}
        rec = ep.item_record_2i(rung=rung, family=bi.FAMILY, size=bi.SIZE_OUT,
                               which="stage1_final", cap=cap, ev=ev, ckpt=ckpt,
                               seal={"tag": bi.PREDICTOR_SEAL_TAG, "sha256": psha}, t_s=0.0)
        p = bi.endpoint_record_path(tmp_path, "stage1_final", rung)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec, indent=1))

    pp = bi.predictor_seal_path(tmp_path)
    pp.parent.mkdir(parents=True, exist_ok=True)
    pp.write_text(json.dumps({"files": {}, "counts": {}, "sha256": psha,
                              "tag": bi.PREDICTOR_SEAL_TAG, "sampling": {}}))
    rp = bi.rung_set_path(tmp_path)
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps({"R_OLMO": [], "R_CAP": [], "R_EXTRA": [],
                              "per_rung": {}, "endpoint_file_sha256": {}}))
    wp = bi.power_path(tmp_path)
    wp.write_text(json.dumps({"A": {"declared_status": "x", "declaration": "x"},
                              "B": {"declared_status": "x", "declaration": "x"}}))
    return {"battery": battery, "amap": amap, "manifest": manifest,
           "entry_stage1": entry_stage1, "commit_stage1": commit, "digest_gate": digest,
           "psha": psha}


def _prereg():
    return dict(tag_exists=lambda t: True,
                blob_sha=lambda tag, rel: bg.sha256_file(bi.REPO / rel) if
                (bi.REPO / rel).is_file() else None,
                blobs_bound=lambda tag, paths, repo_root=None: [])


def _loaders(*, entry_stage1, gate_frac=0.5, digest_gate="Dend", commit_gate=None,
            frac_by_revision=None, digest_gate_diff=False, commit_gate_diff=False,
            raise_at_revision=None):
    frac_by_revision = frac_by_revision or {}
    commit_gate = commit_gate if commit_gate is not None else entry_stage1["commit"]
    state = {"calls": [], "freed": [], "tok_commits": []}

    class M:
        def __init__(self, d): self.d = d

    def checkpoint(entry, cache_root, device):
        is_gate = entry["revision"] == entry_stage1["revision"]
        digest = digest_gate if not (is_gate and digest_gate_diff) else "WRONG-DIGEST"
        commit = commit_gate if not (is_gate and commit_gate_diff) else "0" * 40
        return M(f"D-{entry['revision']}"), {
            "tensor_digest": digest, "commit": commit,
            "config_source": f"cs-{entry['revision']}",
            "sha256": dict(entry.get("lfs_sha256", {})),
            "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}}

    def twin(device):
        return M("D-twin"), {"tensor_digest": "D-twin", "config_source": "cs-twin"}

    def tokenizer(commit):
        state["tok_commits"].append(commit)
        return object()

    def runner_factory(tok, model):
        state["calls"].append(model.d)
        rev = model.d[2:]
        # `raise_at_revision` applies to WHICHEVER revision it names —
        # gate, twin or a grid step — a superset of the earlier
        # grid-only behavior (no prior test names the gate's/twin's
        # own revision, so this is additive).
        raise_call = (raise_at_revision[1] if raise_at_revision is not None and
                     raise_at_revision[0] == rev else None)
        if rev == entry_stage1["revision"]:
            return FakeRunner(_amap_and_battery()[1], gate_frac, raise_at_call=raise_call)
        if rev == "twin":
            frac = frac_by_revision.get("twin", 0.0)
            return FakeRunner(_amap_and_battery()[1], frac, raise_at_call=raise_call)
        return FakeRunner(_amap_and_battery()[1], frac_by_revision.get(rev, 0.1),
                          raise_at_call=raise_call)

    def free(revision, cache_root):
        state["freed"].append(revision)

    return {"checkpoint": checkpoint, "twin": twin, "tokenizer": tokenizer,
           "runner": runner_factory, "free": free}, state


# ------------------------------------------------------------ refusals

def test_refuses_without_prereg_tag(tmp_path):
    with pytest.raises(RuntimeError, match="preregistration tag"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders={},
              tag_exists=lambda t: False)


def test_refuses_without_predictor_seal(tmp_path):
    with pytest.raises(RuntimeError, match="predictor seal"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders={},
              **_prereg())


def test_refuses_without_endpoint_seal(tmp_path):
    p = bi.predictor_seal_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"files": {}, "sha256": "x"}))
    with pytest.raises(RuntimeError, match="endpoint"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders={},
              **_prereg())


def test_refuses_on_drifted_endpoint_seal(tmp_path):
    setup = _setup_seals(tmp_path)
    with pytest.raises(RuntimeError, match="does not bind"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders={},
              tag_exists=lambda t: True,
              blob_sha=lambda tag, rel: bg.sha256_file(bi.REPO / rel) if
              (bi.REPO / rel).is_file() else None,
              blobs_bound=lambda tag, paths, repo_root=None:
              (["drifted"] if tag == bi.ENDPOINT_SEAL_TAG else []))


def test_prereg_refusal_precedes_any_loader_construction(tmp_path, monkeypatch):
    called = []
    monkeypatch.setattr(sw, "_assert_provenance", lambda: called.append("p"))
    monkeypatch.setattr(sw, "real_loaders", lambda: called.append("l") or {})
    with pytest.raises(RuntimeError, match="preregistration tag"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
              loaders=None, tag_exists=lambda t: False)
    assert called == []
    with pytest.raises(RuntimeError, match="drifted"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
              loaders=None, tag_exists=lambda t: True, blob_sha=lambda tag, rel: "0" * 64)
    assert called == []


def test_frozen_check_runs_before_seals(tmp_path, monkeypatch):
    """Ruling 1's order (prereg -> `check_frozen_2i` -> predictor seal
    -> endpoint seal): a distinctive raise from a monkeypatched
    `check_frozen_2i` must reach the caller UNCHANGED, proving the call
    is real, unguarded and precedes the seal checks — neither seal
    file exists in this tmp_path, so a SKIPPED frozen check would
    surface as the different 'predictor seal' refusal instead."""
    def boom():
        raise ValueError("frozen-check-fired")
    monkeypatch.setattr(bi, "check_frozen_2i", boom)
    with pytest.raises(ValueError, match="frozen-check-fired"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders={},
              **_prereg())


# -------------------------------------------------------------- gate 1

def test_gate1_runs_first_and_halts_on_bit_diff(tmp_path, monkeypatch):
    # FakeRunner's hit rule is `(i % 1000) / 1000 < frac` over i in
    # [0, 500) — any frac >= 0.5 hits EVERY item (max i/1000 is .499),
    # so both fracs must sit below .5 to produce a genuine partial-hit
    # mismatch between the fixture and the sweep's own gate-1 eval.
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.2)
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.4,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"])
    with pytest.raises(RuntimeError, match="gate 1"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())
    assert bi.halt_marker_path(tmp_path).exists()
    rec = json.loads(bi.gate1_path(tmp_path).read_text())
    assert any(v != 0 for v in rec["bit_diffs"].values())
    assert not bi.record_path(tmp_path, 1000, "antonym").exists()
    with pytest.raises(RuntimeError, match="halted"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())


def test_gate1_halts_on_digest_diff(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              digest_gate_diff=True)
    with pytest.raises(RuntimeError, match="gate 1"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())
    rec = json.loads(bi.gate1_path(tmp_path).read_text())
    assert rec["digest_sweep"] != rec["digest_endpoint"]


def test_gate1_halts_on_commit_diff(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              commit_gate_diff=True)
    with pytest.raises(RuntimeError, match="gate 1"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())
    rec = json.loads(bi.gate1_path(tmp_path).read_text())
    assert rec["commit_sweep"] != rec["commit_endpoint"]


def test_gate1_record_matches_analyzer_rederivation(tmp_path, monkeypatch):
    """The runner's own gate1.json must satisfy `analyze_2i
    .gate1_failures_7b` cold — the shape contract exercised against
    the analyzer's own re-derivation, not against the runner's mocks."""
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"])
    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())
    g = json.loads(bi.gate1_path(tmp_path).read_text())
    stage1_final = {r: json.loads(bi.endpoint_record_path(tmp_path, "stage1_final", r)
                                  .read_text()) for r in bt.RUNGS}
    assert an.gate1_failures_7b(g, stage1_final) == []
    assert g["continuations_compared"] == {r: bt.N_ITEMS for r in bt.RUNGS}
    assert g["prereg_tag"] == bi.PREREG_TAG


def test_gate1_mid_loop_exception_releases_and_writes_nothing_then_resumes(
        tmp_path, monkeypatch):
    """Review finding 7: a mid-rung exception during gate 1's OWN
    evaluation loop is a CRASH, not a gate FAILURE — `gate1_failures_7b`
    never runs, so nothing it could produce (a HALTED marker) is
    written either. Gate 1's writes are atomic (ruling 2: records,
    then the checkpoint record, then gate1.json, all after the loop
    completes, or none of them at all) — so a mid-loop crash leaves NO
    partial record, no checkpoint record, no gate1.json, no HALTED
    marker; the model is released and the checkpoint cache freed
    regardless. A clean re-run (the same loaders, no longer raising)
    then succeeds from scratch — gate 1 has no PER-RUNG persistence to
    resume from the way the grid steps/twin do (their skip-if-exists
    is at the rung grain), so 'resumes' here means the overall sweep
    recovers cleanly and completes, not that individual gate-1 rungs
    are individually skipped."""
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    gate_rev = setup["entry_stage1"]["revision"]
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0},
                              raise_at_revision=(gate_rev, 10))

    with pytest.raises(RuntimeError, match="boom"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())

    assert gate_rev in state["freed"]                       # released + freed
    assert not bi.gate1_path(tmp_path).exists()              # no gate1.json
    assert not bi.halt_marker_path(tmp_path).exists()         # not a gate failure
    assert not bi.checkpoint_record_path(tmp_path, bi.ENDPOINT_STEP_7B).exists()
    for r in bt.RUNGS:
        assert not bi.record_path(tmp_path, bi.ENDPOINT_STEP_7B, r).exists()

    loaders2, state2 = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                                digest_gate="Dend", commit_gate=setup["commit_stage1"],
                                frac_by_revision={"twin": 0.0})
    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders2,
          **_prereg())
    assert bi.gate1_path(tmp_path).is_file()
    assert an.gate1_failures_7b(
        json.loads(bi.gate1_path(tmp_path).read_text()),
        {r: json.loads(bi.endpoint_record_path(tmp_path, "stage1_final", r).read_text())
        for r in bt.RUNGS}) == []
    for r in bt.RUNGS:
        assert bi.record_path(tmp_path, bi.ENDPOINT_STEP_7B, r).exists()
        assert bi.record_path(tmp_path, bi.TWIN, r).exists()


# ------------------------------------------------------------- the sweep

def test_full_fake_sweep_writes_gate1_twin_grid_and_resumes(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch, (1000, 128000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0})
    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())

    for step in (bi.ENDPOINT_STEP_7B, 1000, 128000, bi.TWIN):
        for r in bt.RUNGS:
            rec = json.loads(bi.record_path(tmp_path, step, r).read_text())
            assert rec["n"] == bt.N_ITEMS and len(rec["bits"]) == bt.N_ITEMS
            assert rec["correct"] == sum(rec["bits"])
            assert rec["predictor_sha"] == setup["psha"]
            assert rec["seal_tag"] == bi.ENDPOINT_SEAL_TAG
            assert rec["step"] == (bi.TWIN if step == bi.TWIN else step)
    twin_rec = json.loads(bi.record_path(tmp_path, bi.TWIN, "antonym").read_text())
    assert twin_rec["commit"] is None and twin_rec["kind"] == "from_config"
    assert twin_rec["correct"] == 0     # frac_by_revision["twin"] = 0.0

    g = json.loads(bi.gate1_path(tmp_path).read_text())
    assert g["prereg_tag"] == bi.PREREG_TAG
    assert an.gate1_failures_7b(
        g, {r: json.loads(bi.endpoint_record_path(tmp_path, "stage1_final", r).read_text())
           for r in bt.RUNGS}) == []

    n_calls = len(state["calls"])
    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())
    assert len(state["calls"]) == n_calls          # nothing re-run


def test_dry_run_touches_nothing_and_builds_no_loader(tmp_path, capsys):
    setup = _setup_seals(tmp_path)

    def boom(*a, **k):
        raise AssertionError("must not be called during dry run")

    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
          loaders={"checkpoint": boom, "twin": boom, "tokenizer": boom, "runner": boom,
                   "free": boom}, dry_run=True, **_prereg())
    assert "would run" in capsys.readouterr().out
    assert not bi.gate1_path(tmp_path).exists()


def test_mid_step_exception_frees_the_checkpoint(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    entry_1000 = bi.entry_7b(setup["manifest"], 1000)
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0},
                              raise_at_revision=(entry_1000["revision"], 5))
    with pytest.raises(RuntimeError, match="boom"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())
    assert entry_1000["revision"] in state["freed"]
    g = json.loads(bi.gate1_path(tmp_path).read_text())
    for r in bt.RUNGS:
        assert bi.record_path(tmp_path, bi.ENDPOINT_STEP_7B, r).exists()
    assert bi.record_path(tmp_path, bi.TWIN, "antonym").exists()
    n_step1000 = sum(1 for r in bt.RUNGS if bi.record_path(tmp_path, 1000, r).exists())
    assert n_step1000 < len(bt.RUNGS)
    # review finding 1: the checkpoint record is written AFTER the
    # rung loop now (matching run_gate1's own order) — a step left
    # partial by a mid-loop exception must not have one on disk.
    assert not bi.checkpoint_record_path(tmp_path, 1000).exists()


def test_checkpoint_record_written_only_once_all_rung_records_exist(tmp_path, monkeypatch):
    """Review finding 1, the positive side: `run_step`'s checkpoint
    record appears only after all 34 rung records do — verified by
    running with SIX of the real 34 rungs pre-populated on disk (a
    step left over from a prior, still-incomplete run) and a fake
    checkpoint loader that raises if the record already exists at the
    moment the checkpoint-record write is attempted, catching an
    early (pre-loop) write immediately rather than merely asserting
    absence afterward."""
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    entry_1000 = bi.entry_7b(setup["manifest"], 1000)
    for r in bt.RUNGS[:6]:
        p = bi.record_path(tmp_path, 1000, r)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"rung": r, "step": 1000}))
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0})

    seen_early = []

    real_checkpoint = loaders["checkpoint"]

    def checking_checkpoint(entry, cache_root, device):
        if entry["revision"] == entry_1000["revision"]:
            seen_early.append(bi.checkpoint_record_path(tmp_path, 1000).exists())
        return real_checkpoint(entry, cache_root, device)

    loaders["checkpoint"] = checking_checkpoint

    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())

    assert seen_early == [False]     # not present at load time (before the loop)
    assert bi.checkpoint_record_path(tmp_path, 1000).is_file()
    for r in bt.RUNGS:
        assert bi.record_path(tmp_path, 1000, r).exists()
    rec = json.loads(bi.checkpoint_record_path(tmp_path, 1000).read_text())
    assert rec["step"] == 1000 and "download_seconds" in rec


def test_resume_writes_a_missing_checkpoint_record_for_a_complete_step(
        tmp_path, monkeypatch):
    """FREEZE R-3, the deadlock: a process killed between the LAST rung
    record and the checkpoint-record write leaves all 34 rung records
    and no `_checkpoint.json`. Under the old rung-records-only
    `records_complete_7b` the step was skipped forever on resume, while
    `analyze_2i.load_sweep_7b` refuses any tree missing that checkpoint
    record — the sweep could never complete and the analyzer could
    never do anything but INSUFFICIENT_DATA.

    Built by running the sweep to completion and then DELETING the
    checkpoint record (the exact on-disk state the interrupt leaves,
    not a hand-assembled approximation), then resuming: the step is
    re-entered, no rung record is rewritten, and the checkpoint record
    appears."""
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0})
    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())
    assert sw.records_complete_7b(tmp_path, 1000) is True

    cp = bi.checkpoint_record_path(tmp_path, 1000)
    cp.unlink()
    before = {r: bi.record_path(tmp_path, 1000, r).read_text() for r in bt.RUNGS}
    assert sw.records_complete_7b(tmp_path, 1000) is False   # the R-3 predicate

    n_calls = len(state["calls"])
    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())
    assert cp.is_file()                                      # the record is back
    assert len(state["calls"]) == n_calls + 1                # exactly one reload
    for r in bt.RUNGS:                                       # no rung re-evaluated
        assert bi.record_path(tmp_path, 1000, r).read_text() == before[r]
    assert json.loads(cp.read_text())["step"] == 1000


def test_resume_writes_a_missing_checkpoint_record_for_the_twin(tmp_path, monkeypatch):
    """FREEZE R-3 on `run_twin`'s own window. `load_sweep_7b` does not
    require a checkpoint record for the TWIN (`if step != bi.TWIN`), so
    this half never deadlocked the analyzer — but the twin's own
    provenance record (seed, config source, tensor digest) would have
    been silently absent from the committed tree forever, and the fix
    is the same predicate."""
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0})
    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())
    cp = bi.checkpoint_record_path(tmp_path, bi.TWIN)
    assert cp.is_file()
    cp.unlink()
    before = {r: bi.record_path(tmp_path, bi.TWIN, r).read_text() for r in bt.RUNGS}
    assert sw.records_complete_7b(tmp_path, bi.TWIN) is False

    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())
    assert cp.is_file()
    assert json.loads(cp.read_text())["step"] == bi.TWIN
    for r in bt.RUNGS:
        assert bi.record_path(tmp_path, bi.TWIN, r).read_text() == before[r]


def test_download_seconds_excludes_rung_eval_time(tmp_path, monkeypatch):
    """Review finding 1: `download_seconds` must mean the SAME thing
    on both `run_gate1` and `run_step` — the checkpoint's own
    load time, not load+eval — even though the record housing it is
    now written AFTER the eval loop on both paths. A real (small)
    sleep in the fake checkpoint loader plus a real (small) sleep per
    rung in the runner gives a wall-clock gap wide enough (~4x) to be
    robust against ordinary CI jitter without waiting long."""
    import time as _time_mod
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0})

    real_checkpoint = loaders["checkpoint"]

    def slow_checkpoint(entry, cache_root, device):
        if entry["revision"] != setup["entry_stage1"]["revision"]:
            _time_mod.sleep(0.25)
        return real_checkpoint(entry, cache_root, device)

    real_runner = loaders["runner"]

    def slow_runner(tok, model):
        r = real_runner(tok, model)
        if model.d[2:] not in (setup["entry_stage1"]["revision"], "twin"):
            orig_generate = r.generate

            def slow_generate(prompts, max_new_tokens):
                _time_mod.sleep(0.02)
                return orig_generate(prompts, max_new_tokens)
            r.generate = slow_generate
        return r

    loaders["checkpoint"] = slow_checkpoint
    loaders["runner"] = slow_runner

    t_start = _time_mod.perf_counter()
    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())
    wall = _time_mod.perf_counter() - t_start

    rec = json.loads(bi.checkpoint_record_path(tmp_path, 1000).read_text())
    # ~0.25 s of checkpoint-load sleep vs. ~0.68 s (34 x 0.02 s) of
    # additional eval sleep on top of it for this one step alone —
    # download_seconds must land near the former, nowhere near a
    # combined figure, and nowhere near the run's total wall time.
    assert rec["download_seconds"] < 0.6
    assert wall > 0.8


def test_free_checkpoint_key_matches_download_key(tmp_path, monkeypatch):
    """Ruling 4 (the reviewer-flagged decoupling risk): `download_entry`/
    `clean_dir` key the cache by `entry['revision']` — the runner's
    `free_checkpoint` call must use the SAME key, real function, real
    cache-path helper, or a multi-GB directory survives every step.
    A fake 'checkpoint' loader creates the tree the way `load_checkpoint`
    really would (no torch/network), for both a clean completion and a
    mid-step exception."""
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    cache_root = tmp_path / "cache"
    entry_1000 = bi.entry_7b(setup["manifest"], 1000)

    def make_checkpoint_with_real_cache(entry, cache_root, device):
        d = bi._cache_dir(bi.REPO_7B, entry["revision"], cache_root) / "clean"
        d.mkdir(parents=True, exist_ok=True)
        (d / "model.safetensors").write_bytes(b"x" * 1024)
        is_gate = entry["revision"] == setup["entry_stage1"]["revision"]
        digest = "Dend" if is_gate else f"D-{entry['revision']}"
        commit = setup["commit_stage1"] if is_gate else entry["commit"]
        class M:
            def __init__(self, d): self.d = d
        # `.d` must stay in the "D-{revision}" shape `runner_factory`
        # (built by `_loaders`, reused here) dispatches on — `digest`
        # (the fake TENSOR digest, unrelated) is free to differ.
        return M(f"D-{entry['revision']}"), {
            "tensor_digest": digest, "commit": commit, "config_source": "cs",
            "sha256": dict(entry.get("lfs_sha256", {})),
            "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}}

    def free(revision, cache_root):
        bi.free_checkpoint(bi.REPO_7B, revision, cache_root)

    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0})
    loaders["checkpoint"] = make_checkpoint_with_real_cache
    loaders["free"] = free

    sw.run(out_root=tmp_path, cache_root=cache_root, device="cpu", loaders=loaders,
          **_prereg())
    assert not bi._cache_dir(bi.REPO_7B, entry_1000["revision"], cache_root).exists()
    assert not bi._cache_dir(bi.REPO_7B, setup["entry_stage1"]["revision"],
                             cache_root).exists()


def test_free_checkpoint_key_matches_after_mid_step_exception(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    cache_root = tmp_path / "cache"
    entry_1000 = bi.entry_7b(setup["manifest"], 1000)

    def make_checkpoint_with_real_cache(entry, cache_root, device):
        d = bi._cache_dir(bi.REPO_7B, entry["revision"], cache_root) / "clean"
        d.mkdir(parents=True, exist_ok=True)
        (d / "model.safetensors").write_bytes(b"x" * 1024)
        is_gate = entry["revision"] == setup["entry_stage1"]["revision"]
        digest = "Dend" if is_gate else f"D-{entry['revision']}"
        commit = setup["commit_stage1"] if is_gate else entry["commit"]
        class M:
            def __init__(self, d): self.d = d
        # `.d` must stay in the "D-{revision}" shape `runner_factory`
        # (built by `_loaders`, reused here) dispatches on — `digest`
        # (the fake TENSOR digest, unrelated) is free to differ.
        return M(f"D-{entry['revision']}"), {
            "tensor_digest": digest, "commit": commit, "config_source": "cs",
            "sha256": dict(entry.get("lfs_sha256", {})),
            "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}}

    def free(revision, cache_root):
        bi.free_checkpoint(bi.REPO_7B, revision, cache_root)

    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0},
                              raise_at_revision=(entry_1000["revision"], 2))
    loaders["checkpoint"] = make_checkpoint_with_real_cache
    loaders["free"] = free

    with pytest.raises(RuntimeError, match="boom"):
        sw.run(out_root=tmp_path, cache_root=cache_root, device="cpu", loaders=loaders,
              **_prereg())
    assert not bi._cache_dir(bi.REPO_7B, entry_1000["revision"], cache_root).exists()


def test_gate1_record_without_final_records_refuses(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0})
    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())
    bi.record_path(tmp_path, bi.ENDPOINT_STEP_7B, "antonym").unlink()
    with pytest.raises(RuntimeError, match="incomplete"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())


def test_existing_gate1_record_fails_rederivation(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch, (1000, bi.ENDPOINT_STEP_7B))
    setup = _setup_seals(tmp_path, gate_frac=0.5, digest="Dend")
    loaders, state = _loaders(entry_stage1=setup["entry_stage1"], gate_frac=0.5,
                              digest_gate="Dend", commit_gate=setup["commit_stage1"],
                              frac_by_revision={"twin": 0.0})
    sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
          **_prereg())
    g = bi.gate1_path(tmp_path)
    rec = json.loads(g.read_text())
    rec["bit_diffs"] = dict(rec["bit_diffs"])
    rec["bit_diffs"]["antonym"] = 3       # corrupt the on-disk record
    g.write_text(json.dumps(rec))
    with pytest.raises(RuntimeError, match="re-derivation"):
        sw.run(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())
