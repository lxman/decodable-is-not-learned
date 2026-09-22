import json

import pytest

from experiments.exp5 import analyze_5 as an
from experiments.exp5 import battery_5 as b5
from experiments.exp5.tests import full_shape_5 as fs

pytestmark = pytest.mark.slow


def _run(root, w, **over):
    from experiments.exp2g import battery_2g as bg
    kw = dict(root=root, write=False, n_sample=200, n_boot=100, manifest=w["manifest"], sl=w["sl"],
              tag_exists=lambda t: True, blob_sha=lambda t, r: bg.sha256_file(b5.REPO / r),
              blobs_bound=lambda t, p, **k: [],
              projection_commit="p1", is_ancestor=lambda a, b: True, seal_tag_commit="s1",
              referents_sha=False, imports_pinned=False, frozen_check=lambda: None, power_gate="full")
    kw.update(over)
    return an.run(**kw)


@pytest.mark.parametrize("mode,world,modifier", [
    ("MATCHED", "MATCHED", None), ("LARGE-AHEAD", "NOT-MATCHED", "LARGE-AHEAD"),
    ("SMALL-AHEAD", "NOT-MATCHED", "SMALL-AHEAD"), ("MIXED", "NOT-MATCHED", "MIXED"),
    ("UNDETERMINED", "UNDETERMINED", None)])
def test_every_terminal_is_reachable(tmp_path, monkeypatch, mode, world, modifier):
    w = fs.write_world_5(tmp_path, mode, monkeypatch=monkeypatch)
    v = _run(tmp_path, w)
    assert v["failures"] == [], v["failures"][:3]
    assert v["verdict"] == world and v["tree"]["modifier"] == modifier
    assert v["gate4"]["pairs_kept"] + v["gate4"]["pairs_dropped"] == len(b5.PAIRS_5)
    assert v["gate4"]["units_unnamed"] == []
    assert set(v["secondaries"]) >= {"S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S10", "S11"}
    if mode == "MATCHED":
        assert v["primary"]["T"] < b5.T_BAR_5
        assert v["secondaries"]["S1"]["classes"]["CONCORDANT"] > 0
    if mode == "LARGE-AHEAD":
        assert v["secondaries"]["S1"]["classes"]["L-AHEAD"] > 0
    # review finding 2: S8 carries 2g's/2h's FULL committed grids with interpolated flags;
    # S10 carries re_crossings and the B-6 12b comparison
    s8 = v["secondaries"]["S8"]
    assert set(s8) == {"2.8b", "6.9b"}
    for size, n_grid in (("2.8b", 21), ("6.9b", 22)):
        assert s8[size]["n_grid"] == n_grid and s8[size]["points"]
        assert any(p["interpolated"] for p in s8[size]["points"])
        assert any(not p["interpolated"] for p in s8[size]["points"])
    s10 = v["secondaries"]["S10"]
    assert "re_crossings" in s10 and "b6_12b" in s10 and s10["b6_12b"] == []
    assert set(s10["re_crossings"]) == set(b5.LARGE_SIDES_5)


def test_refusal_routes_deliver_insufficient_data(tmp_path, monkeypatch):
    w = fs.write_world_5(tmp_path, "MATCHED", monkeypatch=monkeypatch)
    # a unit file removed
    p = b5.rung_record_path_5(tmp_path, "6.9b", 4000, "antonym")
    raw = p.read_bytes(); p.unlink()
    v = _run(tmp_path, w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("6.9b" in f for f in v["failures"])
    p.write_bytes(raw)
    # a halt marker
    h = b5.halt_marker_path_5(tmp_path, "2.8b"); h.write_text("x\n")
    assert _run(tmp_path, w)["verdict"] == "INSUFFICIENT_DATA"; h.unlink()
    # the search log's bisection sequence tampered (gate 4)
    lp = b5.search_log_path_5(tmp_path, "6.9b"); log = json.loads(lp.read_text()); raw = lp.read_bytes()
    pair = next(k for k, v in log["pairs"].items() if v["status"] == "done")
    log["pairs"][pair]["plan"]["bisected"] = log["pairs"][pair]["plan"]["bisected"][::-1]
    lp.write_text(json.dumps(log))
    v = _run(tmp_path, w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("gate 4" in f for f in v["failures"])
    lp.write_bytes(raw)
    # a unit nobody asked for (gate 4: nothing else loaded)
    extra = b5.unit_dir_5(tmp_path, "6.9b", 999); extra.mkdir()
    (extra / "_unit.json").write_text("{}")
    v = _run(tmp_path, w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("step999" in f for f in v["failures"])
    import shutil; shutil.rmtree(extra)
    # an orphan unit dir under the SMALLEST world size (gate 4 review finding 1: the
    # units_unnamed check must run for every size, not only LARGE_SIDES_5 — the smallest size
    # is never swept as large, so it was never checked at all before this fix)
    extra_small = b5.unit_dir_5(tmp_path, "1b", 998); extra_small.mkdir()
    (extra_small / "_unit.json").write_text("{}")
    v = _run(tmp_path, w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("step998" in f for f in v["failures"])
    shutil.rmtree(extra_small)
    # a stray pairs key injected into a search log, naming an existing (complete) unit — gate 4
    # review finding 1: "expected" must never be built from the log's own requested_all, and any
    # pairs key that is not a legitimate (smaller) partner of the size must be refused outright
    lp3 = b5.search_log_path_5(tmp_path, "6.9b"); log3 = json.loads(lp3.read_text())
    raw3 = lp3.read_bytes()
    log3["pairs"]["bogus"] = {"target": 2.0, "status": "done", "requests": [],
                              "plan": {"status": "done", "bracket": [1000, 2000], "b_minus": [],
                                       "b_plus": [], "bisected": []},
                              "requested_all": [{"step": 1000, "why": "spine", "action": "reused"}]}
    lp3.write_text(json.dumps(log3))
    v = _run(tmp_path, w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and \
        any("gate 4" in f and "bogus" in f for f in v["failures"])
    lp3.write_bytes(raw3)
    # the projection not an ancestor (gate 5)
    v = _run(tmp_path, w, is_ancestor=lambda a, b: False)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("projection" in f for f in v["failures"])
    # the power record not reproducible (gate 5)
    pp = b5.power_path_5(tmp_path); raw = pp.read_bytes(); rec = json.loads(raw); rec["n_sim"] += 1
    pp.write_text(json.dumps(rec))
    v = _run(tmp_path, w)
    assert any("power" in f for f in v["failures"]); pp.write_bytes(raw)
    # a unit from a different stack (gate 0)
    lp2 = b5.loss_record_path_5(tmp_path, "2.8b", 1000); raw = lp2.read_bytes(); rec = json.loads(raw)
    rec["stack"]["torch"] = "0.0"; lp2.write_text(json.dumps(rec))
    up = b5.unit_record_path_5(tmp_path, "2.8b", 1000); uraw = up.read_bytes(); u = json.loads(uraw)
    from experiments.exp2g import battery_2g as bg
    u["files"]["_loss.json"] = bg.sha256_file(lp2); up.write_text(json.dumps(u))
    v = _run(tmp_path, w)
    assert any("stack" in f for f in v["failures"]); lp2.write_bytes(raw); up.write_bytes(uraw)
    # freeze F-4: the SMALLEST size's S11 unit torn — its search log is never read, so
    # before the closure the unit vanished from S11 with the verdict MATCHED
    s11 = b5.unit_dir_5(tmp_path, fs.SIZES_W[0], b5.S11_STEP_5)
    raw = (s11 / "odd6.json").read_bytes(); (s11 / "odd6.json").unlink()
    from experiments.exp5 import collect_5 as c5
    tbl = b5.loss_table_path_5(tmp_path); traw = tbl.read_bytes(); c5.rebuild_loss_table_5(tmp_path)
    v = _run(tmp_path, w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and \
        any(f.startswith(f"gate 3 {fs.SIZES_W[0]}: step{b5.S11_STEP_5}") for f in v["failures"])
    (s11 / "odd6.json").write_bytes(raw); tbl.write_bytes(traw)
    # freeze F-4: a NaN loss on a window unit with `finite` left True (table rebuilt over it)
    log = json.loads(b5.search_log_path_5(tmp_path, "6.9b").read_text())
    plan = next(v["plan"] for v in log["pairs"].values() if v["status"] == "done")
    wstep = (plan["b_plus"] or plan["b_minus"])[0]
    lp4 = b5.loss_record_path_5(tmp_path, "6.9b", wstep); raw = lp4.read_bytes(); rec = json.loads(raw)
    rec["loss"] = float("nan")
    for x in rec["per_set"].values():
        x["loss"] = float("nan")
    lp4.write_text(json.dumps(rec))
    up = b5.unit_record_path_5(tmp_path, "6.9b", wstep); uraw = up.read_bytes(); u = json.loads(uraw)
    u["files"]["_loss.json"] = bg.sha256_file(lp4); up.write_text(json.dumps(u))
    c5.rebuild_loss_table_5(tmp_path)
    v = _run(tmp_path, w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("not a finite float" in f for f in v["failures"])
    lp4.write_bytes(raw); up.write_bytes(uraw); tbl.write_bytes(traw)
    # clean again
    assert _run(tmp_path, w)["verdict"] == "MATCHED"


def test_write_produces_verdict_files(tmp_path, monkeypatch):
    w = fs.write_world_5(tmp_path, "LARGE-AHEAD", monkeypatch=monkeypatch)
    v = _run(tmp_path, w, write=True)
    assert (tmp_path / "results" / "verdict.json").is_file()
    txt = (tmp_path / "results" / "VERDICT.txt").read_text()
    assert txt.startswith("EXPERIMENT 5 VERDICT: NOT-MATCHED") and "LARGE-AHEAD" in txt
    assert "Performability ledger" in txt and "L-AHEAD" in txt
