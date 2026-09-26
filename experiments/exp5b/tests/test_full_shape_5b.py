import json

import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5b import battery_5b as b5b
from experiments.exp5b.tests import full_shape_5b as fs5b

pytestmark = pytest.mark.slow


@pytest.mark.parametrize("mode,world,cell", [
    ("SURVIVES", "SURVIVES", "CALIBRATED"), ("INSIDE", "NOT-SURVIVED", "INSIDE"),
    ("SIGN-ONLY", "NOT-SURVIVED", "SIGN-ONLY"), ("SIZE-ONLY", "NOT-SURVIVED", "SIZE-ONLY"),
    ("UNDETERMINED", "UNDETERMINED", None)])
def test_every_terminal_is_reachable(tmp_path, monkeypatch, mode, world, cell):
    w = fs5b.write_world_5b(tmp_path, mode, monkeypatch=monkeypatch)
    v = fs5b.run_5b(w)
    assert v["failures"] == [], v["failures"][:3]
    assert (v["verdict"], v["tree"]["cell"]) == (world, cell), (v["primary"], v["calibration"])
    assert v["gate2"]["exp5_verdict_equal"] and v["gate2"]["exp5_failures"] == []
    assert v["gate1"]["pass"] and all(u["byte_identical"] for u in v["gate1"]["per_unit"].values())
    assert set(v["secondaries"]) == {f"S{i}" for i in range(1, 13)}
    assert v["sides"]["excluded"] == [] and v["sides"]["members_absent"] == {}
    if world != "UNDETERMINED":
        assert v["primary"]["n_cells"] >= 20 and v["licence"]["key"].startswith(world)


def test_calibration_sub_cells_from_a_doctored_power_record(tmp_path, monkeypatch):
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    p = b5b.power_path_5b(w["root5b"])
    rec = json.loads(p.read_text())
    doctored = dict(rec, alpha_5b_axis=[0.2] * 6)
    p.write_text(json.dumps(doctored, indent=1, sort_keys=True))
    v = fs5b.run_5b(w, power_gate="skip")
    assert (v["verdict"], v["tree"]["cell"]) == ("SURVIVES", "INFLATED")
    doctored = dict(rec, sigma_hat_axis=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    p.write_text(json.dumps(doctored, indent=1, sort_keys=True))
    v = fs5b.run_5b(w, power_gate="skip")
    assert (v["verdict"], v["tree"]["cell"]) == ("SURVIVES", "OFF-GRID")
    # finding (Task 5): design §6's verbatim OFF-GRID sentence capitalizes "NOT" for
    # emphasis (matching its "DEMOTED" sibling) — corrected from the brief's lowercase
    # literal, same finding as test_analyze_5b.py's test_licence_block_names_every_cell
    assert "NOT claimed" in v["licence"]["sentence"]
    p.write_text(json.dumps(rec, indent=1, sort_keys=True))
    v = fs5b.run_5b(w)                       # the power gate recomputes: the doctored record is gone
    assert v["failures"] == []


def test_nonfinite_member_is_absent_never_read(tmp_path, monkeypatch):
    """Review Focus 2."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch, nonfinite_at=[("1b", 30000)])
    v = fs5b.run_5b(w)
    assert v["failures"] == []
    assert v["sides"]["members_absent"] == {"1b": {"30000": "non-finite loss"}} or \
        list(v["sides"]["members_absent"]) == ["1b"]
    for c in v["cells"]:
        if c["small"] == "1b":
            # finding (Task 5): n_terms == n_members * (# of non-None outer windows);
            # the brief's blanket "== 4" assumes both b_minus/b_plus are always present,
            # but a pair sitting at the spine's edge (e.g. 2.8b x 1b: bracket [1000,2000],
            # window []+[3000,4000] — see the world's build log) legitimately has an empty
            # b_minus, so its cells carry only n_members (here 2) terms, not 2*n_members
            n_sides = sum(1 for side in (c["b_minus"], c["b_plus"]) if side is not None)
            assert "30000" not in c["members"] and c["n_members"] == 2 \
                and c["n_terms"] == n_sides * c["n_members"]
    assert v["verdict"] == "SURVIVES"


def test_side_absent_or_memberless_is_excluded_not_refused(tmp_path, monkeypatch):
    """Review Focus 5."""
    import shutil
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    shutil.rmtree(b5b.units_root_5b(w["root5b"]) / "1b")
    v = fs5b.run_5b(w)
    assert v["failures"] == [] and v["sides"]["excluded"] == ["1b"] and v["sides"]["cells_dropped"] > 0
    assert v["verdict"] in ("SURVIVES", "UNDETERMINED", "NOT-SURVIVED")
    w = fs5b.write_world_5b(tmp_path / "b", "SURVIVES", monkeypatch=monkeypatch)
    for step in fs5b.WINDOW_W:
        shutil.rmtree(b5b.unit_dir_5b(w["root5b"], "1.4b", step))
    v = fs5b.run_5b(w)
    assert v["failures"] == [] and v["sides"]["excluded"] == ["1.4b"]
    # a side whose FINAL is torn but whose members exist is a refusal
    w = fs5b.write_world_5b(tmp_path / "c", "SURVIVES", monkeypatch=monkeypatch)
    shutil.rmtree(b5b.unit_dir_5b(w["root5b"], "2.8b", b5.FINAL_STEP_5))
    v = fs5b.run_5b(w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("2.8b" in f for f in v["failures"])


def test_refusal_routes_deliver_insufficient_data(tmp_path, monkeypatch):
    import shutil
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    r5b = w["root5b"]

    def refuses(needle, **over):
        v = fs5b.run_5b(w, **over)
        assert v["verdict"] == "INSUFFICIENT_DATA" and any(needle in f for f in v["failures"]), v["failures"][:3]
        assert v["primary"] is None and "S8" not in (v["secondaries"] or {})
        return v

    # a torn member unit (one rung file removed)
    p = b5.rung_record_path_5(r5b, "1b", 30000, "antonym"); raw = p.read_bytes(); p.unlink()
    refuses("1b"); p.write_bytes(raw)
    # a unit without its 5b attestation
    p = b5b.unit5b_record_path_5b(r5b, "1b", 30000); raw = p.read_bytes(); p.unlink()
    refuses("_unit_5b"); p.write_bytes(raw)
    # an extra unit on disk (nothing else loaded)
    # finding (Task 5): a blind copytree leaves every file still declaring step 30000
    # internally (_checkpoint.json/_unit.json/rung records/_unit_5b.json), which trips
    # Experiment 5's OWN gate-3 step/commit/revision/sha consistency check inside
    # an5.load_units_5 (called before this module's own "extra" check) with a
    # "gate 3 contract failure(s)" message instead of exercising the "never requested"
    # path the test names; every step-bearing field in this synthetic world embeds the
    # step number as a literal text substring (revision "step30000", commit "c30000",
    # the fake lfs sha "sha-1b-30000", the bare "step": 30000), so a plain text
    # substitution makes the copy internally self-consistent as a genuine, well-formed,
    # simply-unrequested step12000 unit
    extra = b5b.unit_dir_5b(r5b, "1b", 12000); shutil.copytree(b5b.unit_dir_5b(r5b, "1b", 30000), extra)
    for fp in extra.iterdir():
        if fp.name != "_unit.json":
            fp.write_text(fp.read_text().replace("30000", "12000"))
    # the substitution changes file bytes, so _unit.json's own recorded shas (still the
    # pre-substitution ones) must be refreshed or unit_complete_5 reads the unit as torn
    unit_p = extra / "_unit.json"
    unit_rec = json.loads(unit_p.read_text().replace("30000", "12000"))
    unit_rec["files"] = {name: bg.sha256_file(extra / name) for name in unit_rec["files"]}
    unit_p.write_text(json.dumps(unit_rec))
    refuses("never requested"); shutil.rmtree(extra)
    # a HALTED marker
    hp = b5b.halt_marker_path_5b(r5b, "1b"); hp.write_text("forced\n"); refuses("halt"); hp.unlink()
    # the power record missing / tampered
    pp = b5b.power_path_5b(r5b); raw = pp.read_bytes(); pp.unlink(); refuses("power"); pp.write_bytes(raw)
    rec = json.loads(raw); rec["n_sim"] = 31; pp.write_text(json.dumps(rec, indent=1, sort_keys=True))
    refuses("power"); pp.write_bytes(raw)
    # the projection not an ancestor / the tag not an ancestor of the projection
    refuses("projection", is_ancestor=lambda a, b: False)
    # the exp5-closed binding broken
    refuses("exp5-closed", tag_exists=lambda t: t != "exp5-closed")
    # the 5b prereg tag missing
    refuses("exp5b-preregistered", tag_exists=lambda t: t != b5b.PREREG_TAG_5B)


def test_exp5_tree_tamper_refuses(tmp_path, monkeypatch):
    """Review Focus 3, three variants."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    r5 = w["root5"]
    # (a) a committed Experiment 5 rung record edited → Experiment 5's own gate 3 refuses → surfaced as "5b exp5"
    p = b5.rung_record_path_5(r5, "2.8b", b5.FINAL_STEP_5, "antonym")
    raw = p.read_bytes(); rec = json.loads(raw); rec["correct"] += 1; p.write_text(json.dumps(rec))
    v = fs5b.run_5b(w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any(f.startswith("5b exp5") for f in v["failures"])
    p.write_bytes(raw)
    # (b) the committed verdict.json differs from the re-derivation
    vp = r5 / "results" / "verdict.json"; raw = vp.read_bytes(); vv = json.loads(raw)
    vv["primary"]["T"] = vv["primary"]["T"] + 1e-9; vp.write_text(json.dumps(vv))
    v = fs5b.run_5b(w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("differs from the committed" in f for f in v["failures"])
    vp.write_bytes(raw)
    # (c) an Experiment 5 instrument blob not bound at exp5-closed
    v = fs5b.run_5b(w, blob_sha=lambda t, r: ("0" * 64) if r == "experiments/exp5/stats_5.py" else
                    bg.sha256_file(b5b.REPO / r))
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("does not bind" in f for f in v["failures"])


def test_gate1_refuses_a_count_or_loss_drift_beyond_tolerance(tmp_path, monkeypatch):
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch, reread_delta={"antonym": 20})
    v = fs5b.run_5b(w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("gate 1" in f and "antonym" in f for f in v["failures"])
    w = fs5b.write_world_5b(tmp_path / "b", "SURVIVES", monkeypatch=monkeypatch, loss_delta_final=1e-3)
    v = fs5b.run_5b(w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("|Δℓ|" in f for f in v["failures"])
    w = fs5b.write_world_5b(tmp_path / "c", "SURVIVES", monkeypatch=monkeypatch, halt_on_digest=False,
                            digest_fn_b=lambda s, st: "b-" + s + str(st))
    v = fs5b.run_5b(w)
    assert v["verdict"] == "INSUFFICIENT_DATA" and any("digest" in f for f in v["failures"])


def test_primary_is_uncomputable_before_the_campaign(tmp_path, monkeypatch):
    """Design §2 / §11 (i): the Experiment 5 world exists, no 5b unit does →
    refusal at the host record / units, no statistic, no S8."""
    import shutil
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    shutil.rmtree(w["root5b"] / "results" / "units")
    b5b.host_record_path_5b(w["root5b"]).unlink()
    v = fs5b.run_5b(w)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any(f.startswith("5b host record") for f in v["failures"])
    assert v["primary"] is None and v["cells"] == [] and not v["secondaries"]


def test_verdict_txt_and_write(tmp_path, monkeypatch):
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    v = fs5b.run_5b(w, write=True)
    txt = (w["root5b"] / "results" / "VERDICT.txt").read_text()
    assert txt.startswith("EXPERIMENT 5b VERDICT: SURVIVES · CALIBRATED")
    assert "T_sym" in txt and "items per 500" in txt and "sigma_hat" in txt and "S8" in txt
    assert json.loads((w["root5b"] / "results" / "verdict.json").read_text())["verdict"] == "SURVIVES"
