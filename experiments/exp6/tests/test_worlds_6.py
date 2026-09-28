# experiments/exp6/tests/test_worlds_6.py
"""Full-shape worlds through `analyze_6.run`: every terminal of the
tree, every refusal route, and the trees the REAL runners leave when
they stop. The worlds are written by the runners themselves against
fake loaders (`_world_6`); a refusal world is a clone of the base world
with ONE thing wrong. Slow: the base world takes half a minute to build
and a full analysis a minute."""
import gzip
from collections import Counter
import json
import shutil

import pytest

from experiments.exp6 import analyze_6 as an
from experiments.exp6 import battery_6 as b6
from experiments.exp6 import families_6 as fm
from experiments.exp6 import pins_6 as p6
from experiments.exp6 import power_6 as pw6
from experiments.exp6 import records_6 as r6
from experiments.exp6.run import _common_6 as cm
from experiments.exp6.tests import _world_6 as W

pytestmark = pytest.mark.slow
N_PERM, N_BOOT = 120, 10          # 1/121 < .01: a firing test can fire


def analyze(root, **over):
    kw = dict(W.ANALYZE, n_perm=N_PERM, n_boot=N_BOOT)
    kw.update(over)
    return an.run(root, **kw)


@pytest.fixture(scope="session")
def battery():
    return b6.load_battery_6()


@pytest.fixture(scope="session")
def base(tmp_path_factory, battery):
    root = tmp_path_factory.mktemp("base")
    W.build_world(root, W.spec(rho=W.general(0.6)), battery=battery)
    return root


@pytest.fixture
def world(base, tmp_path):
    return W.clone(base, tmp_path / "w")


def edit(path, fn):
    rec = json.loads(path.read_text())
    out = fn(rec)
    path.write_text(json.dumps(rec if out is None else out, indent=1))


def refused(v, *needles):
    assert v["verdict"] == "INSUFFICIENT_DATA", v["verdict"]
    assert v["tests"] is None and v["secondaries"] is None and v["statuses"] is None
    text = " || ".join(v["referents"]["failures"])
    for n in needles:
        assert n in text, (n, text[:1500])
    assert v["licensed_sentence"] == an.LICENSED_6["INSUFFICIENT_DATA"]
    return text


# ------------------------------------------------------------ the terminals
def test_general(base):
    v = analyze(base)
    assert v["verdict"] == "GENERAL", v["reason"]
    assert v["referents"]["failures"] == []
    assert v["statuses"]["A"]["status"] == v["statuses"]["B"]["status"] == "H"
    assert set(v["tests"]) == {pw6.test_name(t, f) for t, f in pw6.TESTS_6}
    for name, t in v["tests"].items():
        assert t["fires"] and set(t["eligible"]) == set(W.DEFAULT_R), name
        assert t["eligible"] == [r for r in b6.RUNGS_6 if r in W.DEFAULT_R]
        assert t["stratified"]["T"] >= 0.10 and t["stratified"]["p"] < 0.01
    assert v["modifiers"] == [an.HEADLINE_UNQUALIFIED_6]
    assert v["licensed_sentence"].startswith(an.LICENSED_6["GENERAL"])
    sec = v["secondaries"]
    assert sec["failures"] == []
    assert set(sec) >= {"S1 ladder", "S2 410m at 256", "S3 the two predictors",
                        "S4 by type and class", "S5 answer prior", "S6 referents",
                        "S7 textures", "S8 outcome order", "S9 two batteries",
                        "S10 anchors", "S11 structure-conditioned", "S12 ipa relaxed",
                        "S13 beyond the heuristic floor", "sensitivities"}
    s6_ = sec["S6 referents"]
    assert set(s6_["pilot"]) == set(s6_["predictor_twin"]) == set(b6.RUNGS_6)
    for r in b6.RUNGS_6:
        assert s6_["predictor_twin"][r]["verified"] == 0
        assert s6_["pilot"][r]["n_draws"] == 500 * 8
        assert 0 < s6_["pilot"][r]["live_items"] <= s6_["pilot"][r]["live_items_main"]
    # S13: a string match solves `temporal`; every other rung of R_f stands
    s13 = sec["S13 beyond the heuristic floor"]
    for f in fm.FAMILIES_6:
        assert s13["rungs"][f]["not_beyond"] == ["temporal"]
        assert s13["rungs"][f]["R_heuristic"] == [
            r for r in b6.RUNGS_6 if r in W.DEFAULT_R and r != "temporal"]
    assert s13["world"] == "GENERAL" and all(t["fires"] for t in s13["tests"].values())
    assert all("temporal" not in t["eligible"] for t in s13["tests"].values())
    # S11: every test re-read in the strata the structure level is crossed into
    s11 = sec["S11 structure-conditioned"]
    assert set(s11["tests"]) == set(v["tests"]) and s11["world"] == "GENERAL"
    # S12: this world's models write eng_to_ipa's convention and never
    # clear `ipa_word`, so the relaxed reading changes nothing
    s12 = sec["S12 ipa relaxed"]
    for f in fm.FAMILIES_6:
        row = s12["families"][f]
        assert row["endpoint_count"] == {"strict": 0, "relaxed": 0}
        assert not row["strict_in_R"] and "ipa_word" not in row["rungs"]
    assert s12["world"] == "GENERAL"
    # S10: the anchors went through the new pipeline on the Mac's own
    # bytes, so they reproduce the committed per-rung D exactly
    for name, row in sec["S10 anchors"].items():
        for r in b6.ANCHORS_6:
            assert row["rungs"][r]["within"] is True, (name, r, row["rungs"][r])
    assert v["referents"]["pins_active"] == {
        "frozen_modules": False, "import_surface": False, "referent_manifest": False,
        "prereg_tag": False, "seal_tags": False}
    json.dumps(an.an2i._json_safe(v), default=an.an2i._jsonable, allow_nan=False)


@pytest.mark.parametrize("rho,world_name,statuses", [
    ({(("A"), f): .6 for f in fm.FAMILIES_6}, "PYTHIA-ONLY", ("H", "F")),
    ({(("B"), f): .6 for f in fm.FAMILIES_6}, "OLMO-ONLY", ("F", "H")),
    ({("A", "olmo7b"): .6, ("A", "olmo13b"): .6, ("B", "smollm3_3b"): .6,
      ("B", "comma_7b"): .6}, "SPLIT", ("S", "S")),
    ({}, "BATTERY-BOUND", ("F", "F")),
])
def test_the_other_worlds(tmp_path, battery, rho, world_name, statuses):
    W.build_world(tmp_path, W.spec(rho=rho, seed=3), battery=battery)
    v = analyze(tmp_path)
    assert v["verdict"] == world_name, v["reason"]
    assert (v["statuses"]["A"]["status"], v["statuses"]["B"]["status"]) == statuses
    for (t, f), r in rho.items():
        assert v["tests"][pw6.test_name(t, f)]["fires"]
    for t, f in pw6.TESTS_6:
        if (t, f) not in rho:
            assert not v["tests"][pw6.test_name(t, f)]["fires"]
    if world_name == "BATTERY-BOUND":
        assert v["modifiers"] == [an.BATTERY_BOUND_POWERED_6]
        assert "withdrawn" in v["licensed_sentence"]


def test_battery_bound_under_an_underpowered_record(tmp_path, battery):
    W.build_world(tmp_path, W.spec(seed=4), battery=battery, p15=0.5)
    v = analyze(tmp_path)
    assert v["verdict"] == "BATTERY-BOUND"
    assert v["modifiers"] == [an.BATTERY_BOUND_UNDERPOWERED_6]
    assert "withdrawn" not in v["licensed_sentence"]
    assert len(v["disclosures"]) == 8
    assert v["referents"]["power"]["tests"]["A:olmo7b"]["declared_status"] == \
        "DECLARED UNDERPOWERED IN ADVANCE"


def test_undetermined_when_the_families_clear_two_rungs(tmp_path, battery):
    R = {f: ("lcs", "sort3") for f in fm.FAMILIES_6}
    W.build_world(tmp_path, W.spec(rho=W.general(.6), R=R, seed=5), battery=battery)
    v = analyze(tmp_path)
    assert v["verdict"] == "UNDETERMINED", v["reason"]
    assert (v["statuses"]["A"]["status"], v["statuses"]["B"]["status"]) == ("U", "U")
    assert any("outcome side" in m for m in v["modifiers"])
    assert v["referents"]["rung_sets"]["families"]["olmo7b"]["R"] == ["sort3", "lcs"]


def test_the_verdict_is_written_as_strict_json(world):
    v = analyze(world, write=True)
    raw = r6.verdict_path(world).read_text()
    assert json.loads(raw, parse_constant=lambda c: pytest.fail(c))["verdict"] == \
        v["verdict"] == "GENERAL"


# ------------------------------------------------------- refusals: predictors
def test_a_missing_predictor_unit(world):
    r6.tier_record_path(world, "pythia_1b", "main", "lcs").unlink()
    refused(analyze(world), "pythia_1b/main/lcs: unit missing")


def test_a_truncated_draws_file(world):
    p = r6.tier_draws_path(world, "olmo2_1b", "main", "sort5")
    raw = p.read_bytes()
    p.write_bytes(raw[:len(raw) // 2])
    refused(analyze(world), "6 predictor units")


def test_a_draw_changed_after_the_seal(world):
    p = r6.tier_draws_path(world, "pythia_1b", "main", "sort3")
    rows = r6.read_draws(p, seeds=(0, 1, 2, 3), dps=64)
    rows[11]["draws"]["2"][5] = " " + b6.load_item_file_6("sort3")["eval_items"][11]["answer"]
    rows[11]["draws"]["2"][6] = " qqq"
    rows[11]["draws"]["2"][5] += ""
    r6.write_draws(p, rows)
    refused(analyze(world), "draws_sha256 is not the draws file's",
            "does not describe the files on disk")


@pytest.mark.parametrize("field,value", [("seeds", [0, 1, 2, 4]), ("commit", "main"),
                                         ("items_sha256", "0" * 64),
                                         ("model_sha", "0" * 64)])
def test_a_predictor_record_rewritten(world, field, value):
    """2i F-1: provenance attested, never measured. Here it is measured."""
    edit(r6.tier_record_path(world, "pythia_1b", "main", "temporal"),
         lambda r: r.__setitem__(field, value))
    refused(analyze(world), f"pythia_1b/main/temporal: {field}"
            if field != "model_sha" else "model_sha")


def test_an_anchor_that_is_not_the_committed_stream(world):
    p = r6.tier_draws_path(world, "olmo2_1b", "main", "add_base8")
    rows = r6.read_draws(p, seeds=(0,), dps=64)
    rows[3]["draws"]["0"][9] += "!"
    r6.write_draws(p, rows)
    refused(analyze(world), "gate 1-P olmo2_1b/main/add_base8: 1 diffs over 32000 of 32000")


def test_the_predictor_seal(world):
    seal = r6.seal_path(world)
    edit(seal, lambda r: r["counts"]["pythia_1b"]["lcs"].__setitem__(0, 999))
    refused(analyze(world), "its counts do not re-derive from the draws")
    seal.unlink()
    refused(analyze(world), "6 predictor seal")


def test_the_predictor_seal_names_the_pinned_models_and_gate_1p_is_rederived(world):
    edit(r6.seal_path(world),
         lambda r: r["models"]["pythia_1b"].__setitem__("commit", "main"))

    def change(r):
        r["units"][sorted(r["units"])[0]]["draws_compared"] -= 1
    edit(r6.gate1p_path(world), change)
    refused(analyze(world), "6 predictor seal: its models are not the pins",
            "6 gate 1-P: the record does not re-derive from the draws")


@pytest.mark.parametrize("suffix", ["", ".jsonl.gz"])
def test_either_halt_artifact_of_the_predictor_stage_refuses(world, suffix):
    p = r6.tier_halt_path(world, "pythia_410m", "main", "sub_base8")
    p.with_name(p.name + suffix).write_bytes(b"{}")
    refused(analyze(world), "6 halt marker", "a runner halted")


# --------------------------------------------------------- refusals: endpoint
def test_a_missing_endpoint_record(world):
    r6.endpoint_record_path(world, "olmo13b", "init", "shapes").unlink()
    refused(analyze(world), "6 endpoint olmo13b/init/shapes: record missing")


def test_an_endpoint_bit_flipped(world):
    def flip(r):
        i = r["bits"].index(0)
        r["bits"][i] = 1
        r["correct"] += 1
    edit(r6.endpoint_record_path(world, "comma_7b", "stage1_final", "lcs"), flip)
    refused(analyze(world), "comma_7b/stage1_final/lcs: the bits do not re-derive")


def test_the_gate_1b_record_and_the_rung_sets_are_rederived(world):
    edit(r6.gate1b_path(world), lambda r: r["families"]["olmo7b"]["stage1_final"]["box"]
         .__setitem__("add_base8", 0))
    refused(analyze(world), "6 gate 1(b): the record's families does not re-derive")


def test_a_rung_added_to_a_rung_set(world):
    def add(r):
        r["families"]["olmo7b"]["R"].append("ipa_word")
    edit(r6.rung_sets_path(world), add)
    refused(analyze(world), "6 rung sets: the record does not re-derive")


def test_rung_sets_of_another_predictor_seal(world):
    edit(r6.rung_sets_path(world),
         lambda r: r.__setitem__("predictor_sha256", "0" * 64))
    refused(analyze(world), "6 rung sets: predictor_sha256 is not the predictor seal's")


def test_an_incomplete_endpoint_stage_is_not_swept(world):
    """A record of the endpoint stage is gone and the rung sets no longer
    name it, so the stage's composite sha computes. The family is not
    swept against half an endpoint stage all the same."""
    p = r6.endpoint_record_path(world, "olmo13b", "init", "shapes")
    rel = str(p.relative_to(world))
    p.unlink()

    def drop(r):
        r["sealed_files"].remove(rel)
        del r["sealed_sha256"][rel]
    edit(r6.rung_sets_path(world), drop)
    text = refused(analyze(world), "6 endpoint olmo13b/init/shapes: record missing",
                   "6 gate 1(b) olmo13b: the endpoint stage is incomplete",
                   "6 sweep olmo13b: ValueError: the sealed stages are incomplete")
    assert "6 sweep olmo7b: " not in text                  # the whole families are read


def test_an_endpoint_anchor_out_of_tolerance(world):
    """The records are coherent and the anchor is 16 items off the
    Mac's: gate 1(b) re-derived, not read."""
    p = r6.endpoint_record_path(world, "olmo7b", "stage1_final", "add_base8")
    rec = json.loads(p.read_text())
    n = 0
    for i, b in enumerate(rec["bits"]):
        if b and n < 16:
            rec["bits"][i], rec["continuations"][i] = 0, " qqq"
            n += 1
    rec["correct"] -= 16
    p.write_text(json.dumps(rec))
    refused(analyze(world), "6 gate 1(b) olmo7b/stage1_final/add_base8: |Δ| 16 > 15")


def test_a_host_record(world):
    h = next(cm.hosts_dir(world).glob("*.json"))
    edit(h, lambda r: r["stack"].__setitem__("torch", "2.11.0"))
    text = refused(analyze(world), "6 host")
    assert "torch" in text or "sha256 is not the key" in text
    for p in cm.hosts_dir(world).glob("*.json"):
        p.unlink()
    refused(analyze(world), "has no host record")


def test_the_endpoint_halt_marker(world):
    r6.endpoint_halt_path(world).write_text("gate 1(b) fired\n")
    refused(analyze(world), "6 halt marker: results/endpoint/HALTED")


# ------------------------------------------------------------ refusals: power
def test_the_power_record(world):
    p = r6.power_path(world)
    edit(p, lambda r: r["tests"]["A:olmo7b"].__setitem__("declared_status",
                                                         "DECLARED UNDERPOWERED IN ADVANCE"))
    refused(analyze(world), "6 power A:olmo7b: declared")
    p.unlink()
    refused(analyze(world), "6 power record")


def test_a_power_record_of_another_predictor_seal(world):
    edit(r6.power_path(world), lambda r: r.__setitem__("predictor_sha256", "0" * 64))
    refused(analyze(world), "6 power: predictor_sha256 is not the predictor seal's")


def test_a_power_record_of_other_rung_sets(world):
    edit(r6.power_path(world), lambda r: r.__setitem__("rung_sets_sha256", "0" * 64))
    refused(analyze(world), "6 power: rung_sets_sha256 is not the rung sets'")


# ------------------------------------------------------------ refusals: sweep
def test_an_unfinished_sweep_delivers_no_verdict(world):
    """5b F-1: the window is complete or there is no verdict."""
    step = fm.grid("olmo13b")[4]
    shutil.rmtree(r6.step_dir(world, "olmo13b", step))
    refused(analyze(world), f"6 sweep olmo13b/step{step}: not complete",
            "an unfinished campaign delivers no verdict")


def test_a_step_without_its_completeness_record(world):
    step = fm.grid("comma_7b")[2]
    r6.checkpoint_path(world, "comma_7b", step).unlink()
    refused(analyze(world), f"6 sweep comma_7b/step{step}: not complete")


def test_a_continuation_changed(world):
    step = fm.grid("smollm3_3b")[7]

    def change(r):
        i = r["bits"].index(1)
        r["continuations"][i] = " qqq"
    edit(r6.sweep_record_path(world, "smollm3_3b", step, "sort3"), change)
    refused(analyze(world), f"smollm3_3b/step{step}/sort3: the bits do not re-derive")


def test_a_sweep_record_of_another_endpoint_seal(world):
    step = fm.grid("olmo7b")[3]
    edit(r6.sweep_record_path(world, "olmo7b", step, "lcs"),
         lambda r: r.__setitem__("endpoint_sha256", "0" * 64))
    refused(analyze(world), "endpoint_sha256 is not the sealed endpoint's")


def _sweep_host(world, family):
    rec = json.loads(r6.checkpoint_path(world, family, fm.grid(family)[0]).read_text())
    return rec["host_sha256"]


def test_gate_1_is_rederived_from_the_hosts_own_reads(world):
    h = _sweep_host(world, "olmo7b")
    # the thin read says one thing, the candidate read another
    def change(r):
        i = r["bits"].index(1)
        r["bits"][i], r["continuations"][i] = 0, " qqq"
        r["correct"] -= 1
    edit(r6.gate_record_path(world, "olmo7b", h, r6.SWEEP_THIN, "sort3"), change)
    refused(analyze(world), "6 gate 1(a) olmo7b/sort3: 1 bit and 1 continuation diffs")


def test_a_gate_1_record_is_measured_and_tied_to_the_sealed_endpoint(world):
    """The record passes and names this host; what it says of the two
    reads and which endpoint stage it was run against are held to the
    bytes all the same."""
    h = _sweep_host(world, "olmo13b")

    def change(r):
        r["digest_thin"] = "digest:another"
        r["endpoint_sha256"] = "0" * 64
    edit(r6.gate1_path(world, "olmo13b", h), change)
    refused(analyze(world),
            f"6 gate 1 olmo13b/{h[:12]}: the record's digest_thin does not re-derive "
            f"from the bytes",
            f"6 gate 1 olmo13b/{h[:12]}: endpoint_sha256")


def test_a_step_short_of_a_record_and_a_sweep_host_without_one(world):
    step = fm.grid("comma_7b")[6]
    r6.sweep_record_path(world, "comma_7b", step, "shapes").unlink()
    h = _sweep_host(world, "olmo7b")
    (cm.hosts_dir(world) / f"{h[:12]}.json").unlink()
    refused(analyze(world), f"6 sweep comma_7b/step{step}/shapes: record missing",
            f"6 sweep olmo7b/step{fm.grid('olmo7b')[0]}: host {h[:12]} has no host "
            f"record",
            f"6 gate 1 olmo7b: host {h[:12]} has no host record")


def test_a_gate_record_that_did_not_pass_or_is_missing(world):
    h = _sweep_host(world, "comma_7b")
    g = r6.gate1_path(world, "comma_7b", h)
    edit(g, lambda r: r.__setitem__("pass", False))
    refused(analyze(world), "the gate did not pass")
    g.unlink()
    refused(analyze(world), f"6 gate 1 comma_7b/{h[:12]}: gate record missing")


def test_a_failed_gate_left_by_a_host_that_swept_nothing(world):
    other = W.host("box-that-failed")
    r6.write_json(cm.hosts_dir(world) / f"{other['sha256'][:12]}.json", other)
    r6.write_json(r6.gate1_path(world, "olmo7b", other["sha256"]),
                  {"pass": False, "host_sha256": other["sha256"], "failures": ["x"]})
    refused(analyze(world), "the gate did not pass")


def test_the_endpoint_step_is_its_hosts_candidate_read(world):
    end = fm.endpoint_step("olmo13b")

    def change(r):
        i = r["bits"].index(0)
        r["bits"][i] = 1
        r["continuations"][i] = " " + b6.load_item_file_6("sort3")["eval_items"][i]["answer"]
        r["correct"] += 1
    edit(r6.sweep_record_path(world, "olmo13b", end, "sort3"), change)
    refused(analyze(world), f"6 sweep olmo13b/step{end}/sort3: not its host's candidate read")


def test_an_anchor_out_of_tolerance_at_a_grid_step(world):
    step = fm.grid("olmo7b")[10]
    p = r6.sweep_record_path(world, "olmo7b", step, "sub_base8")
    rec = json.loads(p.read_text())
    rec["continuations"] = [" qqq"] * 500
    rec["bits"], rec["correct"] = [0] * 500, 0
    p.write_text(json.dumps(rec))
    refused(analyze(world), f"6 gate 1(c) olmo7b/step{step}/sub_base8")


def test_the_sweep_halt_artifacts(world):
    r6.halted_step_dir(world, "olmo7b", 1000).mkdir(parents=True)
    refused(analyze(world), "6 halt marker: results/sweep/olmo7b/failed_steps")


# ------------------------------------------------------- refusals: the pins
def test_the_tags(world):
    refused(analyze(world, tag_exists=lambda t: False), "6 prereg tag",
            "6 predictor seal binding", "6 endpoint seal binding")
    refused(analyze(world, blobs_bound=lambda tag, rel, repo_root=None: list(rel)[:1]),
            "6 predictor seal binding", "6 endpoint seal binding")
    refused(analyze(world, blob_sha=lambda tag, rel: "0" * 64), "6 prereg tag")


def test_the_pins_that_are_not_filled_refuse(world, monkeypatch):
    # the production check, on an empty table, whatever the build has filled
    monkeypatch.setattr(p6, "FROZEN_SHA256_6", None)
    text = refused(analyze(world, imports_pinned=None, referents_sha=None,
                           frozen_check=None))
    assert "6 import surface: not pinned" in text
    assert "6 referent manifest: not pinned" in text
    assert "6 frozen modules" in text


def test_a_changed_item_file(world, tmp_path, monkeypatch):
    items = tmp_path / "items"
    shutil.copytree(b6.ITEMS_DIR, items)
    p = items / "lcs.json"
    p.write_text(p.read_text().replace('"answer": "3"', '"answer": "4"', 1))
    monkeypatch.setattr(b6, "ITEMS_DIR", items)
    refused(analyze(world), "6 battery items")


# ----------------------------------- refusals: a check that itself fails
@pytest.mark.parametrize("name,label", [("test_inputs", "6 test inputs"),
                                        ("_run_test", "6 primary")])
def test_a_step_of_the_analysis_that_raises_is_a_refusal(base, monkeypatch, name, label):
    """Totality inside the analysis: the tree is whole and a step of the
    analysis raises. A refusal with the reason, never a crash."""
    def boom(*a, **k):
        raise RuntimeError("the step itself failed")
    monkeypatch.setattr(an, name, boom)
    refused(analyze(base), f"{label}: RuntimeError: the step itself failed")


@pytest.mark.parametrize("n,label", [(2, "6 import surface (exit)"),
                                     (3, "6 import surface (post-secondaries)")])
def test_the_import_surface_is_checked_again_after_the_analysis(base, monkeypatch, n,
                                                                label):
    """A module that arrives DURING the analysis: the check at the door
    passes and a later one does not. The verdict that was computed is
    not delivered (2j F-1: checked at entry and at exit)."""
    calls = {"n": 0}

    def check():
        calls["n"] += 1
        if calls["n"] == n:
            raise RuntimeError("unpinned module on the import surface: x.py")
    monkeypatch.setattr(p6, "check_imports_6", check)
    v = analyze(base, imports_pinned=True)
    refused(v, f"{label}: RuntimeError: unpinned module on the import surface: x.py")
    assert calls["n"] == n and v["referents"]["pins_active"]["import_surface"] is True


# --------------------------------------- the trees the real runners leave
def test_a_predictor_gate_that_fires_leaves_a_tree_that_refuses(tmp_path, battery):
    design = W.Design(W.spec(), battery)
    unit = ("pythia_1b", "main", "sub_base8")
    with pytest.raises(RuntimeError, match="GATE 1-P FIRED"):
        W.build_predictors(tmp_path, design, break_gate=unit)
    halted = r6.tier_halt_path(tmp_path, *unit)
    assert halted.is_file() and halted.with_name(halted.name + ".jsonl.gz").is_file()
    assert not r6.tier_record_path(tmp_path, *unit).exists()
    refused(analyze(tmp_path), "6 halt marker")
    with pytest.raises(RuntimeError, match="halt marker"):      # and nothing resumes
        W.build_predictors(tmp_path, design)


def test_a_sweep_the_box_abandoned(base, tmp_path, battery):
    root = W.clone(base, tmp_path / "w")
    shutil.rmtree(r6.sweep_dir(root, "olmo13b"))
    design = W.Design(W.spec(rho=W.general(0.6)), battery)
    with pytest.raises(KeyboardInterrupt):
        W.build_sweep(root, design, "olmo13b", stop_after=5)
    done = [s for s in fm.grid("olmo13b")
            if r6.checkpoint_path(root, "olmo13b", s).exists()]
    assert 1 <= len(done) < len(fm.grid("olmo13b"))
    refused(analyze(root), "an unfinished campaign delivers no verdict")
    # a second host takes the family over: its own gate, nothing overwritten
    before = {p: p.read_bytes() for p in r6.sweep_dir(root, "olmo13b").rglob("*.json")}
    W.build_sweep(root, design, "olmo13b", host_rec=W.host("box-two"))
    for p, raw in before.items():
        assert p.read_bytes() == raw
    assert len(list(r6.sweep_dir(root, "olmo13b").glob("gate1_*.json"))) == 2
    v = analyze(root)
    assert v["verdict"] == "GENERAL", v["reason"]
    assert len(v["referents"]["sweep_hosts"]["olmo13b"]) == 2


def test_a_sweep_gate_that_fires_leaves_a_tree_that_refuses(base, tmp_path, battery):
    root = W.clone(base, tmp_path / "w")
    shutil.rmtree(r6.sweep_dir(root, "comma_7b"))
    design = W.Design(W.spec(rho=W.general(0.6)), battery)
    bad_step = fm.grid("comma_7b")[3]

    def perturb(family, key, rung, conts):
        return [" qqq"] * 500 if (key == bad_step and rung == "add_base8") else conts
    with pytest.raises(RuntimeError, match=r"GATE 1\(c\) FIRED"):
        W.build_sweep(root, design, "comma_7b", perturb=perturb)
    assert r6.sweep_halt_path(root, "comma_7b").is_file()
    assert (r6.halted_step_dir(root, "comma_7b", bad_step) / "add_base8.json").is_file()
    assert not r6.step_dir(root, "comma_7b", bad_step).exists()
    refused(analyze(root), "6 halt marker")
    with pytest.raises(RuntimeError, match="halt marker"):
        W.build_sweep(root, design, "comma_7b")


def test_two_loaders_that_disagree_halt_the_sweep(base, tmp_path, battery):
    root = W.clone(base, tmp_path / "w")
    shutil.rmtree(r6.sweep_dir(root, "olmo7b"))
    design = W.Design(W.spec(rho=W.general(0.6)), battery)
    with pytest.raises(RuntimeError, match="GATE 1 FIRED"):
        W.build_sweep(root, design, "olmo7b",
                      digest=lambda f, k, how: f"digest:{f}:{k}:{how}")
    assert not r6.step_dir(root, "olmo7b", fm.endpoint_step("olmo7b")).exists()
    refused(analyze(root), "6 halt marker", "the gate did not pass")


def test_an_endpoint_stage_whose_anchors_are_off(tmp_path, battery):
    design = W.Design(W.spec(), battery)
    W.build_predictors(tmp_path, design)
    W.seal_predictors(tmp_path)

    def perturb(family, key, rung, conts):
        return [" qqq"] * 500 if (family == "olmo7b" and rung == "sub_base8"
                                  and key != fm.INIT) else conts
    with pytest.raises(RuntimeError, match=r"GATE 1\(b\) FIRED"):
        W.build_endpoints(tmp_path, design, perturb=perturb)
    assert r6.endpoint_halt_path(tmp_path).is_file()
    with pytest.raises(RuntimeError, match="halt marker"):
        W.seal_endpoints(tmp_path)
    refused(analyze(tmp_path), "6 halt marker")


def test_the_stages_refuse_out_of_order(tmp_path, battery):
    design = W.Design(W.spec(), battery)
    with pytest.raises((FileNotFoundError, RuntimeError)):
        W.build_endpoints(tmp_path, design)               # no predictor seal
    W.build_predictors(tmp_path, design)
    with pytest.raises((FileNotFoundError, RuntimeError)):
        W.build_endpoints(tmp_path, design)               # sampled, not sealed
    W.seal_predictors(tmp_path)
    with pytest.raises(RuntimeError, match="sealed"):
        W.build_predictors(tmp_path, design)              # nothing is sampled after it
    with pytest.raises(RuntimeError, match="not sealed"):
        W.build_sweep(tmp_path, design, "olmo7b")         # no endpoint seal
    refused(analyze(tmp_path), "6 endpoint")


def test_what_each_secondary_reads(base, monkeypatch):
    """Which predictor, which outcome, which strata and which rungs each
    reading hands to the test — recorded at the one door they all pass."""
    calls = []
    real = an._run_test

    def spy(x, label, out, strata, rungs, **kw):
        calls.append({"label": label, "rungs": tuple(rungs),
                      "structure": all("structure" in strata[r] for r in rungs),
                      "x": {r: list(x[r]) for r in rungs}})
        return real(x, label, out, strata, rungs, **kw)
    monkeypatch.setattr(an, "_run_test", spy)
    v = analyze(base)
    assert v["verdict"] == "GENERAL"
    ctx, bad = an.load_sealed_stages(base, tag_exists=W.tag_exists,
                                     blobs_bound=W.blobs_bound)
    assert not bad
    R = tuple(r for r in b6.RUNGS_6 if r in W.DEFAULT_R)
    Rh = tuple(r for r in R if r != "temporal")
    primary = calls[:8]                                   # the eight tests come first
    assert [c["label"] for c in primary] == ["1b:k256"] * 4 + ["olmo1b"] * 4
    for c in primary:
        t = "A" if c["label"] == "1b:k256" else "B"
        assert c["rungs"] == R and not c["structure"]
        assert c["x"] == {r: ctx["pred"][t]["x"][r] for r in R}
    assert primary[0]["x"] != primary[4]["x"]             # two predictors, not one
    crossed = [c for c in calls if c["structure"]]
    assert len(crossed) == 8 and {c["rungs"] for c in crossed} == {R}     # S11
    beyond = [c for c in calls[8:] if c["rungs"] == Rh and not c["structure"]]
    assert len(beyond) >= 8                                               # S13
    assert Counter(c["label"] for c in beyond)["olmo1b"] >= 4
    # the power record and the analyzer read the endpoint's counts, not the init's
    inputs = an.test_inputs(ctx)
    for (t, f), inp in inputs.items():
        recs = ctx["endpoint"][f]["stage1_final"]["records"]
        assert inp["n_pos"] == {r: recs[r]["correct"] for r in R}
        assert all(inp["n_pos"][r] == 300 for r in R)


@pytest.mark.parametrize("stage", ["predictor", "endpoint", "sweep"])
def test_an_exit_gate_that_fires_leaves_a_tree_that_refuses(base, tmp_path, battery,
                                                            stage):
    """The entry gate passes and the exit gate does not: a module arrived
    during the run. The records are on disk, the stage's marker beside
    them, and the analyzer refuses."""
    design = W.Design(W.spec(rho=W.general(0.6)), battery)
    n = {"calls": 0}

    def second_time():
        n["calls"] += 1
        if n["calls"] > 1:
            raise RuntimeError("unpinned module on the import surface: x.py")
    inject = dict(W.INJECT, frozen_check=second_time)
    if stage == "predictor":
        root = tmp_path
        with pytest.raises(RuntimeError, match="EXIT GATE FIRED"):
            W.pr.run("olmo2_1b", root=root, device="cpu",
                     loader=W.fake_predictor_loader, sampler=W.fake_sampler(design),
                     **inject)
        marker = r6.predictor_halt_path(root)
        assert r6.tier_record_path(root, "olmo2_1b", "main", "lcs").is_file()
    elif stage == "endpoint":
        root = tmp_path
        W.build_predictors(root, design)
        W.seal_predictors(root)
        h = W.host("box-endpoint")
        r6.write_json(cm.hosts_dir(root) / f"{h['sha256'][:12]}.json", h)
        with pytest.raises(RuntimeError, match="EXIT GATE FIRED"):
            W.ep.run(root=root, device="cuda", loaders=W.fake_loaders(design), host=h,
                     **dict(W.INJECT_SEAL, frozen_check=second_time))
        marker = r6.endpoint_halt_path(root)
        assert r6.gate1b_path(root).is_file()
    else:
        root = W.clone(base, tmp_path / "w")
        shutil.rmtree(r6.sweep_dir(root, "comma_7b"))
        h = W.host("box-sweep")
        with pytest.raises(RuntimeError, match="EXIT GATE FIRED"):
            W.sw.run("comma_7b", root=root, device="cuda",
                     loaders=W.fake_loaders(design), host=h,
                     cache_root=root / "ckpt",
                     **dict(W.INJECT_SEAL, frozen_check=second_time))
        marker = r6.sweep_halt_path(root, "comma_7b")
        assert all(r6.checkpoint_path(root, "comma_7b", s).is_file()
                   for s in fm.grid("comma_7b"))          # every unit landed
    assert marker.is_file() and "exit gate" in marker.read_text()
    refused(analyze(root), "6 halt marker")
    with pytest.raises(RuntimeError, match="halt marker"):
        cm.refuse_if_halted(root)


def test_a_seal_whose_exit_gate_fires_writes_no_seal(tmp_path, battery):
    design = W.Design(W.spec(rho=W.general(0.6)), battery)
    W.build_predictors(tmp_path, design)
    n = {"calls": 0}

    def second_time():
        n["calls"] += 1
        if n["calls"] > 1:
            raise RuntimeError("frozen module drifted")
    with pytest.raises(RuntimeError, match="EXIT GATE FIRED"):
        W.sp.seal(tmp_path, **dict(W.INJECT, frozen_check=second_time))
    assert not r6.seal_path(tmp_path).exists() and not r6.gate1p_path(tmp_path).exists()
    assert r6.predictor_halt_path(tmp_path).is_file()
    # the endpoint seal, on a stage that is whole
    r6.predictor_halt_path(tmp_path).unlink()
    W.seal_predictors(tmp_path)
    W.build_endpoints(tmp_path, design)
    n["calls"] = 0
    with pytest.raises(RuntimeError, match="EXIT GATE FIRED"):
        W.se.seal(tmp_path, **dict(W.INJECT_SEAL, frozen_check=second_time))
    assert not r6.rung_sets_path(tmp_path).exists()
    assert r6.endpoint_halt_path(tmp_path).is_file()
    r6.endpoint_halt_path(tmp_path).unlink()
    assert W.seal_endpoints(tmp_path)["tag"] == r6.ENDPOINT_SEAL_TAG_6


def test_a_family_that_writes_another_convention(tmp_path, battery):
    """Every model of this world transcribes 300 words correctly and
    writes them with no stress mark and the affricates as digraphs. The
    strict criterion credits the answers that carry neither; the relaxed
    reading credits all 300, on both sides of every test."""
    R = {f: W.DEFAULT_R + ("ipa_word",) for f in fm.FAMILIES_6}
    W.build_world(tmp_path, W.spec(rho=W.general(), R=R, ipa_other=True),
                  battery=battery)
    v = analyze(tmp_path)
    assert v["verdict"] == "GENERAL", v["reason"]
    s12 = v["secondaries"]["S12 ipa relaxed"]
    assert v["secondaries"]["failures"] == []
    plain = sum(1 for it in battery["ipa_word"]["eval_items"]
                if W.other_convention(str(it["answer"])) == str(it["answer"]))
    relaxed = Counter(an.relaxed_ipa(it["answer"])
                      for it in battery["ipa_word"]["eval_items"])
    floor = max(relaxed.values()) / 500
    assert s12["n_answers_changed"] >= 500 - plain
    for f in fm.FAMILIES_6:
        row = s12["families"][f]
        assert row["endpoint_count"]["relaxed"] == 300
        assert 0 < row["endpoint_count"]["strict"] < 300
        assert row["relaxed_clears"] and "ipa_word" in row["rungs"]
        assert row["ever"]["relaxed"] == 300 > row["ever"]["strict"]
        assert row["relaxed_floor"] == floor
        for t in ("A", "B"):
            p = row["predictors"][t]
            assert p["test"]["fires"] and "ipa_word" in p["test"]["eligible"]
            assert p["live_items"]["relaxed"] > p["live_items"]["strict"]
            assert p["d_ipa_word"]["relaxed"] > 0.2
            # the test read the RELAXED counts on both sides
            assert p["test"]["per_rung"]["ipa_word"]["d"] == pytest.approx(
                p["d_ipa_word"]["relaxed"])
            assert p["d_ipa_word"]["strict"] != pytest.approx(
                p["d_ipa_word"]["relaxed"])
    assert s12["world"] == "GENERAL"
