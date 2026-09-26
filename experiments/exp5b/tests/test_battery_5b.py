import json
import hashlib

import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5b import battery_5b as b5b


def test_constants_are_the_design_dials():
    assert b5b.WINDOW_STEPS_5B == (142000, 141000, 140000)
    assert b5b.unit_steps_5b() == (143000, 142000, 141000, 140000)
    assert b5b.reread_steps_5b() == (143000, 142000)
    assert b5b.SIZE_ORDER_5B == ("6.9b", "2.8b", "1.4b", "1b", "410m", "160m")
    assert set(b5b.SIZE_ORDER_5B) == set(b5b.small_sides_5b()) == set(b5.SMALL_SIDES_5)
    assert b5b.PLACEBO_SIGN_5B == 1 and abs(b5b.SQRT2_5B ** 2 - 2.0) < 1e-12
    assert b5b.SIGMA_GRID_5B == (5, 10, 15, 20, 30, 45) and b5b.SIGMA_BELIEF_5B == 15
    assert b5b.ALPHA_CAL_5B == 0.05 and b5b.LOSS_TOL_5B == 1e-4
    assert b5b.T_BAR_5B == b5.T_BAR_5 == 0.01 and b5b.ALPHA_5B == b5.ALPHA_5 == 0.01
    assert b5b.MIN_LIVE_CELLS_5B == 20 and b5b.MIN_NONZERO_BLOCKS_5B == 7
    assert b5b.SPIKE_PAIR_5B == ("2.8b", "12b")
    assert b5b.WORLDS_5B == ("INSUFFICIENT_DATA", "UNDETERMINED", "SURVIVES", "NOT-SURVIVED")
    assert b5b.SURVIVES_CELLS_5B == ("CALIBRATED", "INFLATED", "OFF-GRID")
    assert b5b.NOT_SURVIVED_CELLS_5B == ("INSIDE", "SIGN-ONLY", "SIZE-ONLY")
    assert b5b.WHYS_5B == ("final", "member")
    assert b5b.EXP5_CLOSED_TAG_5B == "exp5-closed" and b5b.PREREG_TAG_5B == "exp5b-preregistered"
    assert len(b5b.expected_units_5b()) == 6 * 4


def test_exp5_verdict_pin_matches_the_committed_file():
    """The literal pin (design §3.6 gate 2) is checked against the committed
    verdict.json at the build; a drift in either is caught here."""
    p = b5b.REPO / b5b.EXP5_VERDICT_REL_5B
    assert hashlib.sha256(p.read_bytes()).hexdigest() == b5b.EXP5_VERDICT_SHA256_5B
    v = json.loads(p.read_text())
    assert b5b.exp5_verdict_pin_failures_5b(v) == []
    live = [c for c in v["cells"] if c["live"] and c["defined_P"]]
    assert len(live) == b5b.EXP5_VERDICT_PIN_5B["n_cells"] == 63


def test_exp5_verdict_pin_failures_name_each_field():
    v = json.loads((b5b.REPO / b5b.EXP5_VERDICT_REL_5B).read_text())
    bad = dict(v); bad["verdict"] = "MATCHED"
    assert any("verdict" in f for f in b5b.exp5_verdict_pin_failures_5b(bad))
    bad = json.loads(json.dumps(v)); bad["primary"]["T"] = v["primary"]["T"] + 1e-12
    assert any("T" in f for f in b5b.exp5_verdict_pin_failures_5b(bad))
    bad = json.loads(json.dumps(v)); bad["primary"]["rung_block"]["p"] = 0.001
    assert any("rung-block p" in f for f in b5b.exp5_verdict_pin_failures_5b(bad))
    bad = json.loads(json.dumps(v)); bad["tree"]["modifier"] = "LARGE-AHEAD"
    assert any("modifier" in f for f in b5b.exp5_verdict_pin_failures_5b(bad))
    bad = json.loads(json.dumps(v)); bad["gate4"]["pairs_kept"] = 20
    assert any("pairs_kept" in f for f in b5b.exp5_verdict_pin_failures_5b(bad))


def test_exp5_verdict_equality_drops_meta_and_pins_active_only():
    v = json.loads((b5b.REPO / b5b.EXP5_VERDICT_REL_5B).read_text())
    other = json.loads(json.dumps(v))
    other["meta"] = {"git_sha": "x"}; other["pins_active"] = {"import_surface": False}
    assert b5b.exp5_verdict_equal_failures_5b(other, v) == []
    other["cells"][0]["R"] = other["cells"][0]["R"] + 1.0
    f = b5b.exp5_verdict_equal_failures_5b(other, v)
    assert f and "cells" in f[0]


def test_unit5b_record_contract(tmp_path):
    host = {"sha256": "h" * 64}
    good = {"size": "1b", "step": 142000, "why": "member", "reread": True,
            "reread_record": {"digest_equal": True, "digest_here": "d" * 64, "digest_committed": "d" * 64,
                              "loss_here": 2.0, "loss_committed": 2.0, "loss_delta": 0.0, "per_doc_diffs": 0,
                              "count_abs_diff_sum": 0, "count_abs_diff_max": 0,
                              "continuation_diffs_sum": 0, "byte_identical": True,
                              "tolerance_failures": [], "loss_within_tol": True},
            "prereg_tag": b5b.PREREG_TAG_5B, "exp5_closed_tag": b5b.EXP5_CLOSED_TAG_5B,
            "host_sha256": "h" * 64, "git_sha": "g" * 40, "written_utc": "2026-09-26T00:00:00+00:00"}
    assert b5b.unit5b_record_failures_5b(good, size="1b", step=142000, host=host) == []
    assert b5b.unit5b_record_failures_5b({**good, "prereg_tag": "exp5-preregistered"}, size="1b", step=142000, host=host)
    assert b5b.unit5b_record_failures_5b({**good, "reread": False}, size="1b", step=142000, host=host)
    assert b5b.unit5b_record_failures_5b({**good, "reread_record": None}, size="1b", step=142000, host=host)
    assert b5b.unit5b_record_failures_5b({**good, "why": "spine"}, size="1b", step=142000, host=host)
    assert b5b.unit5b_record_failures_5b({**good, "host_sha256": "z" * 64}, size="1b", step=142000, host=host)
    assert b5b.unit5b_record_failures_5b({**good, "git_sha": ""}, size="1b", step=142000, host=host)
    nm = {**good, "step": 141000, "reread": False, "reread_record": None}
    assert b5b.unit5b_record_failures_5b(nm, size="1b", step=141000, host=host) == []
    assert b5b.unit5b_record_failures_5b({**nm, "reread": True}, size="1b", step=141000, host=host)
    # freeze C-4: `why` must match the step ("final" iff the final)
    bad = b5b.unit5b_record_failures_5b({**good, "why": "final"}, size="1b", step=142000, host=host)
    assert any("does not match step 142000" in b for b in bad)
    fin = {**good, "step": 143000, "why": "member"}
    assert any("does not match step 143000" in b
               for b in b5b.unit5b_record_failures_5b(fin, size="1b", step=143000, host=host))
    assert not any("does not match" in b for b in b5b.unit5b_record_failures_5b(
        {**fin, "why": "final"}, size="1b", step=143000, host=host))


def test_unit_complete_5b_requires_both_records(tmp_path):
    d = b5b.unit_dir_5b(tmp_path, "1b", 142000)
    d.mkdir(parents=True)
    files = {}
    for name in b5.unit_files_5():
        (d / name).write_text("{}")
        files[name] = bg.sha256_file(d / name)
    (d / "_unit.json").write_text(json.dumps({"files": files}))
    assert b5.unit_complete_5(tmp_path, "1b", 142000)
    assert not b5b.unit_complete_5b(tmp_path, "1b", 142000)
    b5b.unit5b_record_path_5b(tmp_path, "1b", 142000).write_text("{}")
    assert b5b.unit_complete_5b(tmp_path, "1b", 142000)


def test_require_prereg_5b_binds_the_5b_blobs(monkeypatch):
    seen = []
    def blob_sha(tag, rel):
        seen.append((tag, rel)); return bg.sha256_file(b5b.REPO / rel)
    present = tuple(rel for rel in b5b.INSTRUMENT_BLOBS_5B if (b5b.REPO / rel).is_file())
    out = b5b.require_prereg_5b(tag_exists=lambda t: t == b5b.PREREG_TAG_5B, blob_sha=blob_sha, blobs=present)
    assert out["tag"] == b5b.PREREG_TAG_5B and set(out["instrument_blobs"]) == set(present)
    assert all(t == b5b.PREREG_TAG_5B for t, _ in seen)
    with pytest.raises(RuntimeError, match="does not exist"):
        b5b.require_prereg_5b(tag_exists=lambda t: False, blob_sha=blob_sha, blobs=present)
    with pytest.raises(RuntimeError, match="does not bind"):
        b5b.require_prereg_5b(tag_exists=lambda t: True, blob_sha=lambda t, r: "0" * 64, blobs=present)


def test_require_exp5_closed_binds_exp5_blobs_and_the_verdict():
    out = b5b.require_exp5_closed_5b(tag_exists=lambda t: t == "exp5-closed",
                                     blob_sha=lambda t, r: bg.sha256_file(b5b.REPO / r))
    assert out["tag"] == "exp5-closed" and set(out["blobs"]) == set(b5.INSTRUMENT_BLOBS_5)
    assert out["verdict_sha256"] == b5b.EXP5_VERDICT_SHA256_5B
    with pytest.raises(RuntimeError, match="exp5-closed"):
        b5b.require_exp5_closed_5b(tag_exists=lambda t: False, blob_sha=lambda t, r: bg.sha256_file(b5b.REPO / r))
    with pytest.raises(RuntimeError, match="does not bind"):
        b5b.require_exp5_closed_5b(tag_exists=lambda t: True, blob_sha=lambda t, r: "0" * 64)
    with pytest.raises(RuntimeError, match="verdict.json"):
        b5b.require_exp5_closed_5b(tag_exists=lambda t: True,
                                   blob_sha=lambda t, r: bg.sha256_file(b5b.REPO / r), verdict_sha="1" * 64)
    # verdict_sha=False skips the sha (the synthetic worlds' Experiment 5 tree)
    out = b5b.require_exp5_closed_5b(tag_exists=lambda t: True,
                                     blob_sha=lambda t, r: bg.sha256_file(b5b.REPO / r), verdict_sha=False)
    assert out["verdict_sha256"] is None


@pytest.mark.slow
def test_require_exp5_closed_against_real_git():
    out = b5b.require_exp5_closed_5b()
    assert set(out["blobs"]) == set(b5.INSTRUMENT_BLOBS_5)


def test_exp5_unit_record_reads_the_committed_units():
    ck = b5b.exp5_unit_record_5b(b5b.EXP5, "2.8b", 142000, "_checkpoint.json")
    assert ck["digest"] and ck["step"] == 142000
    rg = b5b.exp5_unit_record_5b(b5b.EXP5, "2.8b", 142000, "sub3_mid.json")
    assert rg["correct"] == 189 and len(rg["bits"]) == 500
    with pytest.raises(FileNotFoundError):
        b5b.exp5_unit_record_5b(b5b.EXP5, "12b", 142000, "_checkpoint.json")


def test_pins_are_unpinned_until_task_6():
    assert b5b.FROZEN_SHA256_5B is None or isinstance(b5b.FROZEN_SHA256_5B, dict)
    assert b5b.IMPORTED_SHA256_5B is None or isinstance(b5b.IMPORTED_SHA256_5B, dict)
    if b5b.FROZEN_SHA256_5B is None:
        with pytest.raises(RuntimeError, match="not pinned"):
            b5b.check_frozen_5b()
