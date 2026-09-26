# experiments/exp5b/tests/test_verify_referents_5b.py  (fast: individual
# check functions exercised directly, without a full cold-battery run)
from __future__ import annotations

import hashlib
import json

import pytest

from experiments.exp5b import verify_referents_5b as vr


def test_c4_skips_when_referents_sha_not_pinned(monkeypatch):
    monkeypatch.setattr(vr.an, "REFERENTS_5B_SHA256", None)
    assert vr._c4({}).startswith("SKIP")


def test_c4_catches_a_referent_drift(tmp_path, monkeypatch):
    p = tmp_path / "referents_5b.json"
    p.write_text(json.dumps({"n_files": 1, "files": {}}))
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    monkeypatch.setattr(vr, "EXP5B", tmp_path)
    monkeypatch.setattr(vr.an, "REFERENTS_5B_SHA256", sha)
    with pytest.raises(AssertionError, match="referent failure"):
        vr._c4({})


def test_c9_skips_when_no_power_record_is_on_disk(tmp_path, monkeypatch):
    monkeypatch.setattr(vr.b5b, "EXP5B", tmp_path)
    assert vr._c9({}).startswith("SKIP")


def test_c9_catches_a_power_record_that_does_not_reproduce(tmp_path, monkeypatch):
    monkeypatch.setattr(vr.b5b, "EXP5B", tmp_path)
    monkeypatch.setattr(vr.pw5b, "load_cells5_live_5b", lambda root: [{"fake": True}])
    monkeypatch.setattr(vr.b5, "load_floors_5", lambda: {"fake": True})
    monkeypatch.setattr(vr.pw5b, "compute_5b",
                        lambda cells, floors, *, n_sim, seed: {"n_sim": n_sim, "seed": seed,
                                                                 "declaration": "POWERED",
                                                                 "prereg_tag": vr.b5b.PREREG_TAG_5B,
                                                                 "exp5_closed_tag": vr.b5b.EXP5_CLOSED_TAG_5B})
    monkeypatch.setattr(vr.pw5b, "N_SIM_5B", 50)
    monkeypatch.setattr(vr.pw5b, "SEED_5B", 0)
    results = tmp_path / "results"
    results.mkdir()
    rec = {"n_sim": 50, "seed": 0, "declaration": "DECLARED UNDERPOWERED IN ADVANCE",
          "prereg_tag": vr.b5b.PREREG_TAG_5B, "exp5_closed_tag": vr.b5b.EXP5_CLOSED_TAG_5B,
          "exp5_verdict_sha256": None}
    (results / "power_5b.json").write_text(json.dumps(rec))
    with pytest.raises(AssertionError, match="byte for byte"):
        vr._c9({})


def test_c9_passes_when_the_power_record_reproduces(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(vr.b5b, "EXP5B", tmp_path)
    monkeypatch.setattr(vr.pw5b, "load_cells5_live_5b", lambda root: [{"fake": True}])
    monkeypatch.setattr(vr.b5, "load_floors_5", lambda: {"fake": True})
    monkeypatch.setattr(vr.pw5b, "compute_5b",
                        lambda cells, floors, *, n_sim, seed: {"n_sim": n_sim, "seed": seed,
                                                                 "declaration": "POWERED",
                                                                 "prereg_tag": vr.b5b.PREREG_TAG_5B,
                                                                 "exp5_closed_tag": vr.b5b.EXP5_CLOSED_TAG_5B})
    monkeypatch.setattr(vr.pw5b, "N_SIM_5B", 50)
    monkeypatch.setattr(vr.pw5b, "SEED_5B", 0)
    results = tmp_path / "results"
    results.mkdir()
    rec = {"n_sim": 50, "seed": 0, "declaration": "POWERED", "prereg_tag": vr.b5b.PREREG_TAG_5B,
          "exp5_closed_tag": vr.b5b.EXP5_CLOSED_TAG_5B, "exp5_verdict_sha256": None}
    (results / "power_5b.json").write_text(json.dumps(rec))
    assert vr._c9({}) is None
    assert "declaration: POWERED" in capsys.readouterr().out


def test_c10_skips_when_no_5b_unit_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(vr.b5b, "EXP5B", tmp_path)
    assert vr._c10({}).startswith("SKIP")


def test_c11_catches_a_file_count_mismatch(monkeypatch):
    monkeypatch.setattr(vr.mkr, "N_FILES_5B", vr.mkr.N_FILES_5B + 1)
    with pytest.raises(AssertionError, match="N_FILES_5B"):
        vr._c11({})


def test_c12_skips_when_no_5b_unit_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(vr.b5b, "EXP5B", tmp_path)
    assert vr._c12({}).startswith("SKIP")


def test_main_reports_ok_skip_and_tallies(monkeypatch):
    """`main()`'s own control flow on a stand-in check table (freeze C-4: the
    earlier form ran the whole real battery in every fast pass and asserted
    `rc in (0, 1)`, which nothing could fail): an ok and a SKIP tally 1/2 at
    rc 0; a raising check prints FAIL and returns 1 without running on."""
    import io
    from contextlib import redirect_stdout
    ran = []
    monkeypatch.setattr(vr, "CHECKS", [(1, "stand-in ok", lambda ctx: ran.append(1)),
                                       (2, "stand-in skip", lambda ctx: "SKIP not yet")])
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vr.main()
    out = buf.getvalue()
    assert rc == 0 and ran == [1]
    assert "[ 1] ok    stand-in ok" in out and "[ 2] skip  stand-in skip not yet" in out
    assert "referent battery: 1/2" in out

    def _boom(ctx):
        raise AssertionError("forced")
    monkeypatch.setattr(vr, "CHECKS", [(1, "stand-in fail", _boom), (2, "never reached", lambda ctx: ran.append(2))])
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vr.main()
    assert rc == 1 and ran == [1] and "FAIL  stand-in fail: AssertionError: forced" in buf.getvalue()
