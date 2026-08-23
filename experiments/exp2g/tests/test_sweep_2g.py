# experiments/exp2g/tests/test_sweep_2g.py
"""The runner's control flow with FAKE loaders: seal refusal, gate 1
first, halt on diff, records and skip-if-exists, dry run."""
import json

import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp2g import checkpoints_2g as ck
from experiments.exp2g.run import sweep_2g as sw
from experiments.exp2g.tests.test_predictor_2g import _fake_predictor


class FakeRunner:
    def __init__(self, answers_by_prompt, frac, raise_at_call=None):
        self.answers, self.frac = answers_by_prompt, frac
        self.raise_at_call, self.calls = raise_at_call, 0

    def generate(self, prompts, max_new_tokens):
        if self.raise_at_call is not None and self.calls == self.raise_at_call:
            raise RuntimeError("boom")
        self.calls += 1
        out = []
        for i, p in enumerate(prompts):
            out.append(f" {self.answers[p]}" if (i % 1000) / 1000 < self.frac else " zzz")
        return out


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

    def pythia(size, device):
        return object(), M(digest_main)

    def checkpoint(size, step, entry, cache_root, device):
        return M(digest_ckpt if step == bg.FINAL_STEP else f"d{step}"), \
            {"step": step, "sha256": dict(entry["lfs_sha256"]), "commit": entry["commit"],
             "kind": entry["kind"], "files": entry["files"],
             "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}}

    state = {"calls": [], "freed": []}

    def runner(tok, model):
        state["calls"].append(model.d)
        if model.d in (digest_main, digest_ckpt):
            # the final point: reproduce m4's counts exactly unless asked not to
            return _CountedRunner(amap, battery, counts_ok)
        step = int(model.d[1:])
        raise_at_call = raise_at[1] if raise_at is not None and raise_at[0] == step else None
        return FakeRunner(amap, frac_by_step.get(step, 0.1), raise_at_call=raise_at_call)

    def free(size, step, cache_root):
        state["freed"].append((size, step))

    return {"pythia": pythia, "checkpoint": checkpoint, "tokenizer": lambda s: object(),
            "runner": runner, "digest": lambda m: m.d, "free": free}, state


class _CountedRunner:
    """Emits exactly FINAL_COUNT_PIN correct answers per rung (the first k
    items), so gate 1's count comparison passes on the fake."""
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
            want = bg.FINAL_COUNT_PIN["2.8b"].get(r, bg.FINAL_COUNT_PIN["12b"].get(r))
            if not self.ok:
                want += 1
            out.append(f" {self.amap[p]}" if i < want else " zzz")
        return out


def _seal(tmp_path):
    _fake_predictor(tmp_path)
    from experiments.exp2g import predictor_2g as pr
    sha = pr.predictor_sha(tmp_path)
    return dict(tag_exists=lambda t: True, blob_sha=lambda t, rel: sha)


def test_refuses_without_seal(tmp_path):
    _fake_predictor(tmp_path)
    loaders, _ = _loaders(tmp_path)
    with pytest.raises(RuntimeError, match="seal"):
        sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                    loaders=loaders, tag_exists=lambda t: False, blob_sha=lambda t, r: "x")


def test_gate1_runs_first_and_halts_on_digest_diff(tmp_path):
    loaders, state = _loaders(tmp_path, digest_ckpt="E")
    with pytest.raises(RuntimeError, match="gate 1"):
        sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                    loaders=loaders, **_seal(tmp_path))
    assert bg.halt_marker_path(tmp_path, "2.8b").exists()
    rec = json.loads(bg.gate1_path(tmp_path, "2.8b").read_text())
    assert rec["pass"] is False and rec["digest_2c_path"] != rec["digest_2g_path"]
    assert not bg.record_path(tmp_path, "2.8b", 143000, "antonym").exists()
    assert not bg.record_path(tmp_path, "2.8b", 1000, "antonym").exists()
    # a halted tree refuses to resume
    with pytest.raises(RuntimeError, match="halted"):
        sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                    loaders=loaders, **_seal(tmp_path))


def test_gate1_halts_on_count_diff(tmp_path):
    loaders, _ = _loaders(tmp_path, counts_ok=False)
    with pytest.raises(RuntimeError, match="gate 1"):
        sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                    loaders=loaders, **_seal(tmp_path))
    rec = json.loads(bg.gate1_path(tmp_path, "2.8b").read_text())
    assert rec["diffs_vs_pin"]


def test_full_fake_sweep_writes_every_record_and_resumes(tmp_path, monkeypatch):
    monkeypatch.setattr(bg, "GRID", {"2.8b": (0, 1000, 143000), "12b": bg.GRID["12b"]})
    monkeypatch.setattr(ck, "load_manifest",
                        lambda path, sha_pin: json.loads(bg.CHECKPOINTS_PATH.read_text()))
    loaders, state = _loaders(tmp_path, frac_by_step={1000: 0.2})
    sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                loaders=loaders, **_seal(tmp_path))
    for step in (0, 1000, 143000):
        for r in bg.sweep_rungs("2.8b"):
            rec = json.loads(bg.record_path(tmp_path, "2.8b", step, r).read_text())
            assert rec["n"] == 500 and len(rec["bits"]) == 500 and rec["correct"] == sum(rec["bits"])
            assert rec["predictor_sha"] == _seal(tmp_path)["blob_sha"]("t", "r")
    g = json.loads(bg.gate1_path(tmp_path, "2.8b").read_text())
    assert g["pass"] is True and g["diffs_vs_pin"] == {}
    assert json.loads(bg.record_path(tmp_path, "2.8b", 143000, "antonym").read_text())["correct"] == 272
    assert json.loads(bg.checkpoint_record_path(tmp_path, "2.8b", 1000).read_text())["digest"] == "d1000"
    n_calls = len(state["calls"])
    sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                loaders=loaders, **_seal(tmp_path))
    assert len(state["calls"]) == n_calls          # nothing re-run


def test_dry_run_touches_nothing(tmp_path, capsys):
    loaders, state = _loaders(tmp_path)
    sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                loaders=loaders, dry_run=True, **_seal(tmp_path))
    assert state["calls"] == [] and "would run" in capsys.readouterr().out


def test_mid_step_exception_frees_the_checkpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(bg, "GRID", {"2.8b": (0, 1000, 143000), "12b": bg.GRID["12b"]})
    monkeypatch.setattr(ck, "load_manifest",
                        lambda path, sha_pin: json.loads(bg.CHECKPOINTS_PATH.read_text()))
    loaders, state = _loaders(tmp_path, raise_at=(1000, 5))
    with pytest.raises(RuntimeError, match="boom"):
        sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                    loaders=loaders, **_seal(tmp_path))
    assert ("2.8b", 1000) in state["freed"]
    g = json.loads(bg.gate1_path(tmp_path, "2.8b").read_text())
    assert g["pass"] is True
    for r in bg.sweep_rungs("2.8b"):
        assert bg.record_path(tmp_path, "2.8b", 143000, r).exists()
    n_step1000 = sum(1 for r in bg.sweep_rungs("2.8b")
                     if bg.record_path(tmp_path, "2.8b", 1000, r).exists())
    assert n_step1000 < 34


def test_gate1_record_without_final_records_refuses(tmp_path, monkeypatch):
    monkeypatch.setattr(bg, "GRID", {"2.8b": (0, 1000, 143000), "12b": bg.GRID["12b"]})
    monkeypatch.setattr(ck, "load_manifest",
                        lambda path, sha_pin: json.loads(bg.CHECKPOINTS_PATH.read_text()))
    loaders, _ = _loaders(tmp_path)
    sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                loaders=loaders, **_seal(tmp_path))
    bg.record_path(tmp_path, "2.8b", 143000, "antonym").unlink()
    with pytest.raises(RuntimeError, match="incomplete"):
        sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                    loaders=loaders, **_seal(tmp_path))


def test_existing_gate1_record_fails_rederivation(tmp_path, monkeypatch):
    monkeypatch.setattr(bg, "GRID", {"2.8b": (0, 1000, 143000), "12b": bg.GRID["12b"]})
    monkeypatch.setattr(ck, "load_manifest",
                        lambda path, sha_pin: json.loads(bg.CHECKPOINTS_PATH.read_text()))
    loaders, _ = _loaders(tmp_path)
    sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                loaders=loaders, **_seal(tmp_path))
    g = bg.gate1_path(tmp_path, "2.8b")
    rec = json.loads(g.read_text())
    rec["counts_2c_path"]["antonym"] += 1        # corrupt the on-disk record
    g.write_text(json.dumps(rec))
    with pytest.raises(RuntimeError, match="re-derivation"):
        sw.run_size("2.8b", out_root=tmp_path, cache_root=tmp_path / "c", device="cpu",
                    loaders=loaders, **_seal(tmp_path))
