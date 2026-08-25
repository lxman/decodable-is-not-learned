# experiments/exp2h/tests/test_sweep_2h.py
"""The 6.9b runner's control flow with FAKE loaders: prereg-tag
refusal, gate 1 first, halt on diff, records and skip-if-exists,
resume refusal, dry run, mid-step exception frees the checkpoint.
Mirrors `experiments/exp2g/tests/test_sweep_2g.py` with battery_2h's
paths/pins and the two-stage predictor seal replaced by the single
freeze-tag refusal."""
import json

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g.tests.test_sweep_2g import FakeRunner
from experiments.exp2h import battery_2h as bh
from experiments.exp2h.run import sweep_2h as sw


def _loaders(tmp_path, *, digest_main="D", digest_ckpt="D", frac_by_step=None, counts_ok=True,
             raise_at=None):
    from harness import render_prompt
    battery = bg.load_battery()
    amap = {}
    for cap in battery.values():
        shots = [tuple(s) for s in cap["shots"]][:bg.N_SHOTS]
        for it in cap["eval_items"]:
            amap[render_prompt(it["question"], shots)] = it["answer"]
    frac_by_step = frac_by_step or {}

    class M:
        def __init__(self, d): self.d = d

    def pythia(device):
        return object(), M(digest_main)

    def checkpoint(step, entry, cache_root, device):
        return M(digest_ckpt if step == bh.FINAL_STEP_69 else f"d{step}"), \
            {"step": step, "sha256": dict(entry["lfs_sha256"]), "commit": entry["commit"],
             "kind": entry["kind"], "files": entry["files"],
             "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}}

    state = {"calls": [], "freed": []}

    def runner(tok, model):
        state["calls"].append(model.d)
        if model.d in (digest_main, digest_ckpt):
            # the final point: reproduce m4's 6.9b counts exactly unless asked not to
            return _CountedRunner(amap, battery, counts_ok)
        step = int(model.d[1:])
        raise_at_call = raise_at[1] if raise_at is not None and raise_at[0] == step else None
        return FakeRunner(amap, frac_by_step.get(step, 0.1), raise_at_call=raise_at_call)

    def free(step, cache_root):
        state["freed"].append(step)

    return {"pythia": pythia, "checkpoint": checkpoint, "tokenizer": lambda: object(),
            "runner": runner, "digest": lambda m: m.d, "free": free}, state


class _CountedRunner:
    """Emits exactly FINAL_COUNT_PIN_69 correct answers per rung (the
    first k items), so gate 1's count comparison passes on the fake."""
    def __init__(self, amap, battery, ok):
        self.amap, self.ok = amap, ok
        self.by_prompt_rung = {}
        from harness import render_prompt
        for r, cap in battery.items():
            shots = [tuple(s) for s in cap["shots"]][:bg.N_SHOTS]
            for i, it in enumerate(cap["eval_items"]):
                self.by_prompt_rung[render_prompt(it["question"], shots)] = (r, i)

    def generate(self, prompts, k):
        out = []
        for p in prompts:
            r, i = self.by_prompt_rung[p]
            want = bh.FINAL_COUNT_PIN_69[r]
            if not self.ok:
                want += 1
            out.append(f" {self.amap[p]}" if i < want else " zzz")
        return out


def _prereg():
    return dict(tag_exists=lambda t: True,
                blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel))


def _shrink_grid(monkeypatch):
    """A short 3-step grid (a subset of the real committed manifest's
    entries, so `entry_69` still resolves), with `load_manifest_69`
    replaced to skip the grid-equality check against the real,
    23-step committed file (mirrors 2g's identical technique for its
    own GRID/load_manifest pair)."""
    monkeypatch.setattr(bh, "GRID_69", (0, 1000, 143000))
    monkeypatch.setattr(bh, "load_manifest_69",
                        lambda path, sha_pin: json.loads(bh.CHECKPOINTS_PATH_69.read_text()))


def test_refuses_without_prereg_tag(tmp_path):
    loaders, _ = _loaders(tmp_path)
    with pytest.raises(RuntimeError, match="preregistration tag"):
        sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                  loaders=loaders, tag_exists=lambda t: False)


def test_gate1_runs_first_and_halts_on_digest_diff(tmp_path):
    loaders, state = _loaders(tmp_path, digest_ckpt="E")
    with pytest.raises(RuntimeError, match="gate 1"):
        sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                  loaders=loaders, **_prereg())
    assert bh.halt_marker_path_2h(tmp_path).exists()
    rec = json.loads(bh.gate1_path_2h(tmp_path).read_text())
    assert rec["pass"] is False and rec["digest_2c_path"] != rec["digest_2h_path"]
    assert not bh.record_path_2h(tmp_path, bh.FINAL_STEP_69, "antonym").exists()
    assert not bh.record_path_2h(tmp_path, 1000, "antonym").exists()
    # a halted tree refuses to resume
    with pytest.raises(RuntimeError, match="halted"):
        sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                  loaders=loaders, **_prereg())


def test_gate1_halts_on_count_diff(tmp_path):
    loaders, _ = _loaders(tmp_path, counts_ok=False)
    with pytest.raises(RuntimeError, match="gate 1"):
        sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                  loaders=loaders, **_prereg())
    rec = json.loads(bh.gate1_path_2h(tmp_path).read_text())
    assert rec["diffs_vs_pin"]


def test_full_fake_sweep_writes_every_record_and_resumes(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, state = _loaders(tmp_path, frac_by_step={1000: 0.2})
    sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())
    for step in (0, 1000, 143000):
        for r in bt.RUNGS:
            rec = json.loads(bh.record_path_2h(tmp_path, step, r).read_text())
            assert rec["n"] == bt.N_ITEMS and len(rec["bits"]) == bt.N_ITEMS
            assert rec["correct"] == sum(rec["bits"])
            assert rec["predictor_sha"] == bh.PREDICTOR_2G_SHA
            assert rec["seal_tag"] == bg.SEAL_TAG
    g = json.loads(bh.gate1_path_2h(tmp_path).read_text())
    assert g["pass"] is True and g["diffs_vs_pin"] == {}
    assert g["prereg_tag"] == bh.PREREG_TAG_2H
    # freeze F-2: the runner attests the comparison's COVERAGE, and the
    # analyzer's gate requires the full battery on every rung — the two
    # sides of the contract exercised against the shared shape, not
    # against each other's mocks.
    assert g["continuations_compared_2h_path"] == {r: bt.N_ITEMS for r in bt.RUNGS}
    assert an_gate_clean(g)
    got_antonym = json.loads(bh.record_path_2h(tmp_path, bh.FINAL_STEP_69,
                                               "antonym").read_text())["correct"]
    assert got_antonym == bh.FINAL_COUNT_PIN_69["antonym"]
    assert json.loads(bh.checkpoint_record_path_2h(tmp_path, 1000).read_text())["digest"] == "d1000"
    n_calls = len(state["calls"])
    sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())
    assert len(state["calls"]) == n_calls          # nothing re-run


def test_dry_run_touches_nothing(tmp_path, capsys):
    loaders, state = _loaders(tmp_path)
    sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              dry_run=True, **_prereg())
    assert state["calls"] == [] and "would run" in capsys.readouterr().out


def test_mid_step_exception_frees_the_checkpoint(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, state = _loaders(tmp_path, raise_at=(1000, 5))
    with pytest.raises(RuntimeError, match="boom"):
        sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
                  **_prereg())
    assert 1000 in state["freed"]
    g = json.loads(bh.gate1_path_2h(tmp_path).read_text())
    assert g["pass"] is True
    for r in bt.RUNGS:
        assert bh.record_path_2h(tmp_path, bh.FINAL_STEP_69, r).exists()
    n_step1000 = sum(1 for r in bt.RUNGS if bh.record_path_2h(tmp_path, 1000, r).exists())
    assert n_step1000 < len(bt.RUNGS)


def test_gate1_record_without_final_records_refuses(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, _ = _loaders(tmp_path)
    sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())
    bh.record_path_2h(tmp_path, bh.FINAL_STEP_69, "antonym").unlink()
    with pytest.raises(RuntimeError, match="incomplete"):
        sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
                  **_prereg())


def test_existing_gate1_record_fails_rederivation(tmp_path, monkeypatch):
    _shrink_grid(monkeypatch)
    loaders, _ = _loaders(tmp_path)
    sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
              **_prereg())
    g = bh.gate1_path_2h(tmp_path)
    rec = json.loads(g.read_text())
    rec["counts_2c_path"]["antonym"] += 1        # corrupt the on-disk record
    g.write_text(json.dumps(rec))
    with pytest.raises(RuntimeError, match="re-derivation"):
        sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu", loaders=loaders,
                  **_prereg())


def an_gate_clean(rec) -> bool:
    """The analyzer's own re-derivation over the runner's committed
    record (freeze F-2): the record the runner writes must satisfy
    `analyze_2h.gate1_failures_69` with nothing left over."""
    from experiments.exp2h import analyze_2h as ah
    return ah.gate1_failures_69(rec) == []


def test_prereg_refusal_precedes_any_loader_construction(tmp_path, monkeypatch):
    """Attack-list item 6 (the ordering): with `loaders=None` — the REAL
    path — nothing model-touching may be reachable before the freeze-tag
    refusal. `_assert_provenance`/`real_loaders` are the first two calls
    that could import or build anything; neither is reached."""
    called = []
    monkeypatch.setattr(sw, "_assert_provenance", lambda: called.append("provenance"))
    monkeypatch.setattr(sw, "real_loaders", lambda: called.append("loaders") or {})
    with pytest.raises(RuntimeError, match="preregistration tag"):
        sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                  loaders=None, tag_exists=lambda t: False)
    assert called == []
    # and with the tag present but the instrument drifted from it (F-3)
    with pytest.raises(RuntimeError, match="drifted"):
        sw.run_69(out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                  loaders=None, tag_exists=lambda t: True,
                  blob_sha=lambda tag, rel: "0" * 64)
    assert called == []
