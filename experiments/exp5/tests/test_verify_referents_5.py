# experiments/exp5/tests/test_verify_referents_5.py  (fast: individual
# check functions exercised directly, without a full cold-battery run)
from __future__ import annotations

import json

import pytest

from experiments.exp5 import verify_referents_5 as vr


def test_c3_skips_when_referents_sha_not_pinned(monkeypatch):
    monkeypatch.setattr(vr.an, "REFERENTS_5_SHA256", None)
    assert vr._c3({}).startswith("SKIP")


def test_c3_catches_a_referent_drift(monkeypatch, tmp_path):
    p = tmp_path / "referents_5.json"
    p.write_text(json.dumps({"n_files": 1, "files": {}}))
    import hashlib
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    monkeypatch.setattr(vr, "EXP5", tmp_path)
    monkeypatch.setattr(vr.an, "REFERENTS_5_SHA256", sha)
    with pytest.raises(AssertionError, match="referent failure"):
        vr._c3({})


def test_c11_skips_when_no_power_record_is_on_disk(tmp_path, monkeypatch):
    monkeypatch.setattr(vr.b5, "EXP5", tmp_path)
    assert vr._c11({}).startswith("SKIP")


def test_c11_catches_a_power_record_that_does_not_reproduce(tmp_path, monkeypatch):
    monkeypatch.setattr(vr.b5, "EXP5", tmp_path)
    monkeypatch.setattr(vr.pw, "load_finals_counts_5", lambda root: {"fake": True})
    monkeypatch.setattr(vr.b5, "load_floors_5", lambda: {"fake": True})
    monkeypatch.setattr(vr.pw, "finals_sha256_5", lambda root: "x" * 64)
    monkeypatch.setattr(vr.pw, "compute",
                        lambda finals, floors, *, n_sim, seed: {"n_sim": n_sim, "seed": seed,
                                                                  "declaration": "POWERED"})
    results = tmp_path / "results"
    results.mkdir()
    rec = {"n_sim": 50, "seed": 0, "declaration": "DECLARED UNDERPOWERED IN ADVANCE",
           "finals_sha256": "x" * 64}
    (results / "power_5.json").write_text(json.dumps(rec))
    with pytest.raises(AssertionError, match="byte for byte"):
        vr._c11({})


def test_c11_passes_when_the_power_record_reproduces(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(vr.b5, "EXP5", tmp_path)
    monkeypatch.setattr(vr.pw, "load_finals_counts_5", lambda root: {"fake": True})
    monkeypatch.setattr(vr.b5, "load_floors_5", lambda: {"fake": True})
    monkeypatch.setattr(vr.pw, "finals_sha256_5", lambda root: "x" * 64)
    monkeypatch.setattr(vr.pw, "compute",
                        lambda finals, floors, *, n_sim, seed: {"n_sim": n_sim, "seed": seed,
                                                                  "declaration": "POWERED"})
    results = tmp_path / "results"
    results.mkdir()
    rec = {"n_sim": 50, "seed": 0, "declaration": "POWERED", "finals_sha256": "x" * 64}
    (results / "power_5.json").write_text(json.dumps(rec))
    assert vr._c11({}) is None
    assert "declaration: POWERED" in capsys.readouterr().out


def test_c13_skips_when_no_campaign_has_run(tmp_path, monkeypatch):
    monkeypatch.setattr(vr.b5, "EXP5", tmp_path)
    assert vr._c13({}).startswith("SKIP")


def test_c13_checks_gate1a_when_present_and_raises_on_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(vr.b5, "EXP5", tmp_path)
    results = tmp_path / "results"
    results.mkdir()
    (results / "gate1a.json").write_text(json.dumps({"digests_equal": False}))
    with pytest.raises(AssertionError, match="gate 1\\(a\\)"):
        vr._c13({})


def test_c13_passes_and_prints_when_records_are_clean(tmp_path, monkeypatch, capsys):
    from experiments.exp5 import battery_5 as b5
    monkeypatch.setattr(vr.b5, "EXP5", tmp_path)
    results = tmp_path / "results"
    results.mkdir()
    good_a = {"digests_equal": True, "continuation_diffs": {r: 0 for r in b5.RUNGS},
             "continuations_compared": {r: 500 for r in b5.RUNGS}, "loss_equal": True,
             "prereg_tag": b5.PREREG_TAG_5, "pass": True,
             "digest_2c_path": "d" * 64, "digest_candidate_path": "d" * 64,
             "loss_2c_path": 2.5, "loss_candidate_path": 2.5, "per_doc_diffs": 0}
    (results / "gate1a.json").write_text(json.dumps(good_a))
    assert vr._c13({}) is None
    assert "1(a) ok" in capsys.readouterr().out


def test_c12_catches_a_file_count_mismatch(monkeypatch):
    monkeypatch.setattr(vr.mkr, "N_FILES_5", vr.mkr.N_FILES_5 + 1)
    with pytest.raises(AssertionError, match="N_FILES_5"):
        vr._c12({})


def test_c7_skips_rather_than_downloads_when_the_tokenizer_is_not_cached(monkeypatch, tmp_path):
    """Review finding 1 (Task 6 fix round 1): `_c7` must SKIP — never
    raise, never silently download — when the tokenizer isn't cached.
    The val file is faked as already-cached (item 7's first half is
    not this finding's concern); `load_slice_tokenizer_5` is made to
    raise OSError exactly as it would with `local_files_only=True` and
    nothing cached."""
    fake_path = tmp_path / "val.jsonl.zst"
    fake_path.write_bytes(b"")
    monkeypatch.setattr("huggingface_hub.hf_hub_download", lambda *a, **k: str(fake_path))
    monkeypatch.setattr(vr.sl5, "verify_slice_file_5", lambda p: None)

    def _raise(*, local_files_only):
        assert local_files_only is True
        raise OSError("not cached and offline")

    monkeypatch.setattr(vr.sl5, "load_slice_tokenizer_5", _raise)
    result = vr._c7({})
    assert result.startswith("SKIP")
    assert "tokenizer" in result


def test_c5_catches_a_hub_rewrite(tmp_path, monkeypatch):
    """A closed-grid LFS sha differing between the fresh manifest and
    2g's/2h's own committed (closed) manifest must raise, naming the
    step — the check `verify_referents_5.py` exists to run."""
    from experiments.exp2g import battery_2g as bg
    real_manifest = vr.b5.load_manifest_5(sha_pin=vr.b5.CHECKPOINTS_SHA256_5)
    step = bg.trained_steps("2.8b")[0]
    tampered = json.loads(json.dumps(real_manifest))
    tampered["2.8b"]["entries"][str(step)]["lfs_sha256"] = {"tampered": "0" * 64}
    monkeypatch.setattr(vr.b5, "load_manifest_5", lambda **k: tampered)
    with pytest.raises(AssertionError):
        vr._c5({})
