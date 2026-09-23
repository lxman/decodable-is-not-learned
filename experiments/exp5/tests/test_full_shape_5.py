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
    # a COMPLETE, contract-clean unit nobody asked for (freeze F-4 made the empty-_unit.json
    # orphan above a torn-unit refusal too, so this is the case only the units_unnamed check
    # can refuse): written by the production run_unit_5 at an available step no replay names
    from experiments.exp2d import analyze_2d as a2d
    from experiments.exp5 import collect_5 as c5
    from experiments.exp5.tests import fakes_5 as fk
    ld, _ = fk.make_loaders(w["battery"], loss_fn=fs.loss_w, count_fn=fs.count_fn_for("MATCHED"))
    orphan_step = 29000
    assert not b5.unit_dir_5(tmp_path, "6.9b", orphan_step).exists()
    c5.run_unit_5("6.9b", orphan_step, root=tmp_path, manifest=w["manifest"], cache_root=tmp_path,
                  device="cuda", battery=w["battery"], verify_fn=a2d.load_verify(), sl=w["sl"],
                  host=json.loads(b5.host_record_path_5(tmp_path).read_text()), loaders=ld,
                  git_sha="g1", why="orphan")
    tbl = b5.loss_table_path_5(tmp_path); traw0 = tbl.read_bytes(); c5.rebuild_loss_table_5(tmp_path)
    assert b5.unit_complete_5(tmp_path, "6.9b", orphan_step)
    v = _run(tmp_path, w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and \
        any(f.startswith(f"gate 4 6.9b: step{orphan_step} on disk but never requested") for f in v["failures"])
    shutil.rmtree(b5.unit_dir_5(tmp_path, "6.9b", orphan_step)); tbl.write_bytes(traw0)
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
    assert v["verdict"] == "INSUFFICIENT_DATA" and \
        any("attested" in f and "measured" in f for f in v["failures"])
    lp4.write_bytes(raw); up.write_bytes(uraw); tbl.write_bytes(traw)
    # ratification slip 9: a CONSISTENT non-finite loss on a unit the search READS (a bisected
    # step, then a spine step) refuses — gate 3 as ratified: finite on every spine and bisection
    # unit; a window-only member is the ABSENT case, covered by
    # test_a_non_finite_window_member_is_absent_and_the_verdict_stands
    for bstep, kind in ((plan["bisected"][0], "bisect"), (fs.SPINE_W[1], "spine")):
        lp5 = b5.loss_record_path_5(tmp_path, "6.9b", bstep); raw5 = lp5.read_bytes(); rec = json.loads(raw5)
        rec["loss"] = float("nan"); rec["finite"] = False; rec["n_nonfinite"] = 3
        for x in rec["per_set"].values():
            x["loss"] = float("nan")
        lp5.write_text(json.dumps(rec))
        up5 = b5.unit_record_path_5(tmp_path, "6.9b", bstep); uraw5 = up5.read_bytes(); u = json.loads(uraw5)
        u["files"]["_loss.json"] = bg.sha256_file(lp5); up5.write_text(json.dumps(u))
        c5.rebuild_loss_table_5(tmp_path)
        v = _run(tmp_path, w)
        assert v["verdict"] == "INSUFFICIENT_DATA" and \
            any(f.startswith("gate 3 6.9b") and f"step{bstep}" in f and kind in f for f in v["failures"]), \
            (bstep, kind, v["failures"][:4])
        lp5.write_bytes(raw5); up5.write_bytes(uraw5); tbl.write_bytes(traw)
    # clean again
    assert _run(tmp_path, w)["verdict"] == "MATCHED"


def test_a_non_finite_window_member_is_absent_and_the_verdict_stands(tmp_path, monkeypatch):
    """Ratification slip 9 end to end through the PRODUCTION runner: a
    window-only member whose forward overflows is written, marked and
    treated as ABSENT — its side shorter (the edge rule), its counts never
    read, the member printed in S10 and under gate 4 — and the verdict is
    the clean world's. The MATCHED-POWERED licence sentence (slip 11)
    quotes the realized pair count and the largest realized ratio."""
    clean_root = tmp_path / "clean"
    w0 = fs.write_world_5(clean_root, "MATCHED", monkeypatch=monkeypatch)
    log = json.loads(b5.search_log_path_5(clean_root, "6.9b").read_text())
    last = [s for s in fs.SIZES_W[:-1] if log["pairs"].get(s, {}).get("status") == "done"][-1]
    plan = log["pairs"][last]["plan"]
    read = set(plan["bisected"]) | set(fs.SPINE_W)
    wstep = next(s for s in plan["b_plus"] + plan["b_minus"] if s not in read)
    side = "b_plus" if wstep in plan["b_plus"] else "b_minus"
    v0 = _run(clean_root, w0)
    assert v0["verdict"] == "MATCHED" and v0["failures"] == []
    root = tmp_path / "nonfinite"
    w = fs.write_world_5(root, "MATCHED", monkeypatch=monkeypatch, nonfinite_at=[("6.9b", wstep)])
    assert not b5.halt_marker_path_5(root, "6.9b").exists()
    log1 = json.loads(b5.search_log_path_5(root, "6.9b").read_text())
    p1 = log1["pairs"][last]["plan"]
    assert p1["absent"] == [wstep] and p1[side] == [s for s in plan[side] if s != wstep]
    assert p1["bracket"] == plan["bracket"] and p1["bisected"] == plan["bisected"]
    assert log1["nonfinite"] == [{"step": wstep, "why": "window", "pair": last, "n_nonfinite": 3}]
    assert json.loads(b5.unit_record_path_5(root, "6.9b", wstep).read_text())["finite"] is False
    v = _run(root, w)
    assert v["failures"] == [], v["failures"][:3]
    assert v["verdict"] == "MATCHED" and v["primary"]["n_rungs"] == v0["primary"]["n_rungs"]
    assert v["secondaries"]["S10"]["nonfinite_units"] == {"6.9b": {str(wstep): {"why": "window", "n_nonfinite": 3}}}
    assert v["gate4"]["window_members_absent"] == [f"{last}→6.9b: step{wstep}"]
    assert v["gate4"]["units_unnamed"] == [] and v["gate4"]["pairs_kept"] == v0["gate4"]["pairs_kept"]
    cells = [c for c in v["cells"] if c["small"] == last and c["large"] == "6.9b"]
    assert cells and all(c[f"{side}_steps"] == p1[side] for c in cells)
    assert wstep not in {s for c in cells for s in c["b_minus_steps"] + c["b_plus_steps"]}
    # slip 11: the licence block carries the realized pair count and the largest realized ratio
    # (the fake n_params is 1000 at every size, so every ratio is 1.0); the synthetic power record
    # declares UNDERPOWERED (N_SIM 30), so the POWERED sentence is checked on the same realized
    # pairs through licence_block_5 itself
    lic = v["licence"]
    assert lic["key"] == "MATCHED-UNDERPOWERED" and "not distinguishable" in lic["sentence"]
    assert lic["pairs_realized"] == v["gate4"]["pairs_kept"] and lic["largest_ratio_realized"] == 1.0
    powered = an.licence_block_5("MATCHED", None, {"declaration": "POWERED"},
                                 pairs=[{"small": "x", "large": "y", "ratio": 1.0}] * lic["pairs_realized"])
    assert f"across {v['gate4']['pairs_kept']} size pairs to 1×" in powered["sentence"]
    assert "read to date" not in powered["sentence"]


def test_write_produces_verdict_files(tmp_path, monkeypatch):
    w = fs.write_world_5(tmp_path, "LARGE-AHEAD", monkeypatch=monkeypatch)
    v = _run(tmp_path, w, write=True)
    assert (tmp_path / "results" / "verdict.json").is_file()
    txt = (tmp_path / "results" / "VERDICT.txt").read_text()
    assert txt.startswith("EXPERIMENT 5 VERDICT: NOT-MATCHED") and "LARGE-AHEAD" in txt
    assert "Performability ledger" in txt and "L-AHEAD" in txt
