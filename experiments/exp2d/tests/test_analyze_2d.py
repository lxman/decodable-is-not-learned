"""analyze_2d loaders: every refusal that guards a verdict input,
exercised on synthetic trees built by the world builder's writers."""
import gzip
import json

import pytest

from experiments.exp2d import analyze_2d as a
from experiments.exp2d import battery_2d as bt
from experiments.exp2d.tests import full_shape as fs


@pytest.fixture(scope="module")
def env():
    battery, floors = fs.battery()
    return {"battery": battery, "floors": floors, "verify": a.load_verify(),
            "outcome": fs.outcome()}


def _one_cell(tmp_path, env, tier, size, rung, verified):
    spec = a.TIERS[tier]
    rows = fs.synthetic_rows(env["battery"][rung], seed=spec["seed"],
                             dps=spec["draws_per_seed"], verified=verified)
    fs.write_sampling_cell(tmp_path, tier, size, rung, rows,
                           verify=env["verify"])
    return rows


def _edit_record(path, **changes):
    rec = json.loads(path.read_text())
    rec.update(changes)
    path.write_text(json.dumps(rec))


# --------------------------------------------------------------- outcome

def test_outcome_known_answer_gate_and_rule(env):
    out = env["outcome"]
    assert out["n_rising"] == 11 and out["n_rising_12b"] == 9
    assert out["rungs"]["sub3_mid"]["rising"]
    assert not out["rungs"]["sub3_mid"]["rising_12b"]
    # ruling H: the option-listing rungs against 1/n_options
    assert out["rungs"]["median7"]["floor"] == pytest.approx(1 / 7)
    assert not out["rungs"]["median7"]["rising"]
    assert not out["rungs"]["odd_one_out"]["rising"]
    assert out["rungs"]["median5"]["rising"] and \
        out["rungs"]["median5"]["rising_12b"]
    assert out["rungs"]["odd6"]["rising"] and not out["rungs"]["odd6"]["rising_12b"]
    assert out["rungs"]["hamming12"]["corrected_ascent"] == 0.0
    assert out["rungs"]["hamming12"]["per_size"]["12b"]["trained_acc"] == .232
    assert out["rungs"]["count_div13"]["rising"]
    assert out["rungs"]["antonym"]["corrected_ascent"] == pytest.approx(
        ((.544 - .25) + (.572 - .25) + (.560 - .25)) / (1 - .25) / 3)
    assert out["rungs"]["add3_mid"]["corrected_ascent"] == pytest.approx(
        ((.086 - .006) + (.038 - .006) + (.052 - .006)) / (1 - .006) / 3)
    # 2c's frozen column rides alongside for comparability
    assert out["rungs"]["add3_mid"]["ascent_2c"] == pytest.approx(
        0.058666666666666666)
    # untrained twins printed, never used
    assert out["rungs"]["sub3_mid"]["per_size"]["2.8b"]["untrained_acc"] == 0.0


def test_outcome_gate_fires_on_altered_record(env, monkeypatch, tmp_path):
    """Point one m4 record at a copy with a changed count: 2c's rule
    no longer reproduces ascent_scores.json → hard error."""
    real = a._m4_path("12b", "trained", "sub4_mid")
    alt = tmp_path / "sub4_mid.json"
    rec = json.loads(real.read_text())
    rec["correct"] = rec["correct"] + 3
    alt.write_text(json.dumps(rec))
    orig = a._m4_path

    def fake(size, mode, rung):
        return alt if (size, mode, rung) == ("12b", "trained", "sub4_mid") \
            else orig(size, mode, rung)
    monkeypatch.setattr(a, "_m4_path", fake)
    with pytest.raises(ValueError, match="known-answer gate"):
        a.load_outcome(env["floors"])


def test_probe_predictor_order():
    p = a.load_probe_predictor()
    assert list(p) == list(a.RUNGS)
    assert sum(v > 0 for v in p.values()) == 12
    assert p["sub3_mid"] == 0.0 and p["arith_next"] == 0.0


# ------------------------------------------------------- sampling tiers

def test_read_rows_coverage_and_shape(tmp_path, env):
    rows = _one_cell(tmp_path, env, "pilot", "410m", "mod17", 5)
    g = a.tier_draws_path(tmp_path, "pilot", "410m", "mod17")
    got = a.read_rows(g, seed=1000, dps=8)
    assert len(got) == 500
    assert got[0]["draws"]["1000"][0] == \
        str(env["battery"]["mod17"]["eval_items"][0]["answer"])
    assert got[0]["draws"]["1000"][1] == fs.FILLER
    with pytest.raises(ValueError, match="not the tier's seed"):
        a.read_rows(g, seed=0, dps=8)
    with pytest.raises(ValueError, match="draws_per_seed"):
        a.read_rows(g, seed=1000, dps=64)
    # truncated file
    with gzip.open(g, "wt") as f:
        for row in rows[:499]:
            f.write(json.dumps(row) + "\n")
    with pytest.raises(ValueError, match="coverage incomplete"):
        a.read_rows(g, seed=1000, dps=8)


def test_tier_loader_recomputes_and_refuses_stale_tally(tmp_path, env):
    for size in a.PROBE_SIZES:
        for rung in a.RUNGS:
            _one_cell(tmp_path, env, "pilot", size, rung,
                      3 if rung == "antonym" else 0)
    cells = a.load_sampling_tier(tmp_path, "pilot", env["battery"],
                                 env["verify"])
    assert cells[("antonym", "1b")]["verified"] == 3
    assert cells[("antonym", "1b")]["n_draws"] == 4000
    assert cells[("mod17", "410m")]["verified"] == 0
    p = a.tier_record_path(tmp_path, "pilot", "1b", "antonym")
    _edit_record(p, per_seed_tallies={"1000": {"full_string": 4,
                                               "n_draws": 4000}})
    with pytest.raises(ValueError, match="stored tallies"):
        a.load_sampling_tier(tmp_path, "pilot", env["battery"], env["verify"])


def test_tier_loader_pins_provenance(tmp_path, env):
    for size in a.PROBE_SIZES:
        for rung in a.RUNGS:
            _one_cell(tmp_path, env, "pilot", size, rung, 0)
    p = a.tier_record_path(tmp_path, "pilot", "410m", "base7")
    for field, bad in (("max_new_tokens", 12), ("dtype", "float16"),
                       ("seeds", [0]), ("items_sha256", "00" * 32),
                       ("stream_namespace", "exp2d"), ("model_sha", "abc"),
                       ("answer_type", "word")):
        rec = json.loads(p.read_text())
        good = rec[field]
        _edit_record(p, **{field: bad})
        with pytest.raises(ValueError):
            a.load_sampling_tier(tmp_path, "pilot", env["battery"],
                                 env["verify"])
        _edit_record(p, **{field: good})
    # answers must be the sha-pinned file's
    rec = json.loads(p.read_text())
    rec["answers"][3] = "999999"
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="answers disagree"):
        a.load_sampling_tier(tmp_path, "pilot", env["battery"], env["verify"])


def test_tier_loader_refuses_incomplete(tmp_path, env):
    _one_cell(tmp_path, env, "main", "410m", "mod17", 0)
    with pytest.raises(FileNotFoundError, match="incomplete"):
        a.load_sampling_tier(tmp_path, "main", env["battery"], env["verify"])


def test_predictor_from_tier_rule(env):
    floors = env["floors"]
    cells = {}
    for r in a.RUNGS:
        for s in a.PROBE_SIZES:
            cells[(r, s)] = {"verified": 0, "n_draws": 32000}
    cells[("antonym", "1b")] = {"verified": 12000, "n_draws": 32000}   # .375 > .25
    cells[("antonym", "410m")] = {"verified": 7000, "n_draws": 32000}   # .219 < .25
    cells[("mod13", "1b")] = {"verified": 3010, "n_draws": 32000}      # .0941 vs .094
    pred = a.predictor_from_tier(cells, floors, n_draws_per_rung=32000)
    assert floors["antonym"]["floor"] == 0.25                           # ruling H
    m1b = (12000 / 32000 - 0.25) / (1 - 0.25)
    assert pred["antonym"]["per_size"]["1b"]["margin"] == pytest.approx(m1b)
    assert pred["antonym"]["per_size"]["410m"]["margin"] == 0.0
    assert pred["antonym"]["score"] == pytest.approx(m1b / 2)
    assert pred["antonym"]["raw_zero"] == {"410m": False, "1b": False}
    assert pred["mod13"]["score"] == 0.0          # above floor, not significant
    assert pred["mod17"]["raw_zero"] == {"410m": True, "1b": True}
    with pytest.raises(ValueError):
        a.predictor_from_tier(cells, floors, n_draws_per_rung=4000)


# ---------------------------------------------------------------- gate 1

def _gate1_tree(tmp_path, env, mutate=None):
    for rung in a.REVERSAL_RUNGS:
        for size in a.PROBE_SIZES:
            rows = [{"item": r["item"], "draws": {"0": list(r["draws"]["0"])}}
                    for r in fs.committed_rows(rung, size)]
            if mutate == (rung, size):
                rows[0]["draws"]["0"][0] += "?"
            fs.write_gate1(tmp_path, rung, size, rows, verify=env["verify"])


def test_gate1_loader_clean_and_drift(tmp_path, env):
    _gate1_tree(tmp_path, env)
    g = a.load_gate1(tmp_path)
    assert g["diff_cells"] == [] and g["total_draws_compared"] == 128_000
    assert g["cells"][("reverse_string", "1b")]["fires_reproduced"] == \
        [{"item": 436, "seed": 0, "draw": 6}]
    _gate1_tree(tmp_path, env, mutate=("rev_string7", "410m"))
    g = a.load_gate1(tmp_path)
    assert g["diff_cells"] == ["rev_string7/410m"]
    assert g["cells"][("rev_string7", "410m")]["n_diffs"] == 1


def test_gate1_loader_refusals(tmp_path, env):
    _gate1_tree(tmp_path, env)
    p = a.gate1_record_path(tmp_path, "1b", "reverse_string")
    good = p.read_text()
    for field, bad, msg in (
            ("draws_compared", 31_936, "coverage"),
            ("n_items", 499, "coverage"),
            ("seeds_rederived", [1], "seed"),
            ("committed_draws_sha256", "ab" * 32, "literal"),
            ("items_sha256", "cd" * 32, "pin"),
            ("fires_reproduced", [], "committed fires"),
            ("n_diffs", 2, "disagree")):
        _edit_record(p, **{field: bad})
        with pytest.raises(ValueError, match=msg):
            a.load_gate1(tmp_path)
        p.write_text(good)
    p.unlink()
    with pytest.raises(FileNotFoundError):
        a.load_gate1(tmp_path)


def test_gate1_vs_main_cross_check(tmp_path, env):
    """The analyzer recomputes the comparison from the MAIN draws it
    loaded; a record claiming 0 diffs over drifted main draws is
    caught."""
    _gate1_tree(tmp_path, env)
    gate1 = a.load_gate1(tmp_path)
    main_cells = {}
    for rung in a.REVERSAL_RUNGS:
        for size in a.PROBE_SIZES:
            rows = [{"item": r["item"], "draws": {"0": list(r["draws"]["0"])}}
                    for r in fs.committed_rows(rung, size)]
            main_cells[(rung, size)] = {"rows": rows}
    a.check_gate1_vs_main(gate1, main_cells)
    main_cells[("reverse_string", "410m")]["rows"][2]["draws"]["0"][1] += "~"
    with pytest.raises(ValueError, match="analyzer's own comparison"):
        a.check_gate1_vs_main(gate1, main_cells)


# ---------------------------------------------------------------- argmax

def test_argmax_loader(tmp_path, env):
    for size in a.PROBE_SIZES:
        for rung in a.RUNGS:
            fs.write_argmax(tmp_path, size, rung, 7 if rung == "caesar" else 0,
                            verify=env["verify"])
    am = a.load_argmax(tmp_path, env["battery"], env["verify"])
    assert am[("caesar", "1b")]["correct"] == 7
    p = a.argmax_record_path(tmp_path, "1b", "caesar")
    _edit_record(p, correct=8)
    with pytest.raises(ValueError, match="stored correct"):
        a.load_argmax(tmp_path, env["battery"], env["verify"])
    _edit_record(p, correct=7, dtype="float32")
    with pytest.raises(ValueError, match="provenance"):
        a.load_argmax(tmp_path, env["battery"], env["verify"])
    p.unlink()
    with pytest.raises(FileNotFoundError):
        a.load_argmax(tmp_path, env["battery"], env["verify"])
    assert a.load_argmax(tmp_path, env["battery"], env["verify"],
                         required=False) is None


# ------------------------------------------------------------ power rec

def test_power_record_required_for_run(tmp_path):
    with pytest.raises(FileNotFoundError):
        a.load_power_record(tmp_path / "power_2d.json")
    (tmp_path / "power_2d.json").write_text('{"declared_status": "X"}')
    with pytest.raises(ValueError):
        a.load_power_record(tmp_path / "power_2d.json")


# ----------------------------------------------------------- referents

def test_referents_manifest_pinned():
    ref = a.load_referents()
    assert ref["n_files"] == 250
    with pytest.raises(ValueError, match="sha256"):
        a.load_referents(file_sha_pin="00" * 32)


def test_stream_map_continuity():
    r = a.check_stream_map_2d()
    assert r["continuity_cells"] == 4
    with pytest.raises(ValueError):
        a.check_stream_map_2d(exp3_map_path=a.EXP2D / "stream_map_2d.json")


# ------------------------------------------------------ more refusals

def test_outcome_n_pin(env, monkeypatch, tmp_path):
    real = a._m4_path("2.8b", "untrained", "mod17")
    alt = tmp_path / "mod17.json"
    rec = json.loads(real.read_text())
    rec["n"] = 499
    alt.write_text(json.dumps(rec))
    orig = a._m4_path
    monkeypatch.setattr(a, "_m4_path", lambda s, m, r: alt if (s, m, r) == (
        "2.8b", "untrained", "mod17") else orig(s, m, r))
    with pytest.raises(ValueError, match="n 499"):
        a.load_outcome(env["floors"])


def test_frozen_import_check_fires(monkeypatch):
    bad = dict(a.FROZEN_IMPORT_SHA256_2D)
    bad[a.EXP2C / "harness.py"] = "00" * 32
    monkeypatch.setattr(a, "FROZEN_IMPORT_SHA256_2D", bad)
    with pytest.raises(ValueError, match="frozen file"):
        a.check_frozen_imports_2d()


def test_referent_entries_are_rehashed(tmp_path):
    rec = json.loads(a.REFERENTS_PATH.read_text())
    k = next(iter(rec["files"]))
    rec["files"][k] = "00" * 32
    p = tmp_path / "ref.json"
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="differ from the manifest"):
        a.load_referents(p, file_sha_pin=None)
    rec["files"]["experiments/nonexistent.json"] = "11" * 32
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="differ from the manifest"):
        a.load_referents(p, file_sha_pin=None)


def test_percolation_candidate_rule(env):
    outcome = env["outcome"]
    probe = {r: 0.0 for r in a.RUNGS}
    probe["antonym"] = 0.5
    cells = {(r, s): {"verified": 0} for r in a.RUNGS for s in a.PROBE_SIZES}
    cells[("sub3_mid", "1b")] = {"verified": 1}
    cells[("sub3_mid", "410m")] = {"verified": 0}
    cells[("arith_next", "410m")] = {"verified": 3}    # 410m irrelevant
    got = a.percolation_candidates(outcome, cells, probe)
    assert "arith_next" in got                # rising, 1b zero, probe zero
    assert "sub3_mid" not in got              # one 1b draw
    assert "antonym" not in got               # probe nonzero
    assert "hamming12" not in got             # not rising
    assert all(outcome["rungs"][r]["rising"] for r in got)


def test_twin_totals_check():
    assert a.check_twin_totals(0, 512_000, 64_000)["fires"] == 0
    for args in ((1, 512_000, 64_000), (0, 511_999, 64_000),
                 (0, 512_000, 64_001)):
        with pytest.raises(ValueError, match="twin record"):
            a.check_twin_totals(*args)


# ------------------------------------------- freeze F-1: the halt tree

def test_scan_gate1_halt_delivers_insufficient_data_from_runner_tree(tmp_path):
    """The tree the PRODUCTION RUNNER leaves after a gate-1 halt (gate-1
    record with diffs, .HALTED rows, no normal draws file, later tiers
    absent) must yield §6's first terminal from run(), not a
    FileNotFoundError from the complete-tree loaders."""
    v = fs.build_halt_world(tmp_path, halt_at=("rev_string7", "410m"))
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["halted_before_completion"] is True
    assert v["gate1"]["diff_cells"] == ["rev_string7/410m"]
    assert v["gate1"]["records_present"] == 1
    d = v["gate1"]["diffs_verbatim"]["rev_string7/410m"]
    assert len(d) == 1 and d[0]["item"] == 7 and d[0]["draw"] == 11
    assert v["gate1"]["cells"]["rev_string7/410m"]["halted_rows_reverified"]
    assert v["primary"] is None
    assert v["tiers"]["main/410m"]["rungs_complete"] == \
        a.RUNGS.index("rev_string7")
    assert v["tiers"]["main/1b"]["rungs_complete"] == 0
    assert v["tiers"]["pilot/1b"]["rungs_complete"] == 34
    assert v["outcome_summary"]["n_rising"] == 11
    assert v["power"]["declared_status"] == "POWERED"
    assert "ZERO free parameters" in v["known_outcome_caveat"]
    # the complete-tree loader still refuses the incomplete main tier
    with pytest.raises(FileNotFoundError, match="incomplete"):
        a.load_sampling_tier(tmp_path, "main", fs.battery()[0],
                             a.load_verify())


def test_scan_gate1_halt_reverifies_halted_rows(tmp_path):
    """The analyzer does not trust the halt record: the .HALTED rows are
    compared to exp3's bytes again and must reproduce the diff count."""
    fs.build_halt_world(tmp_path, halt_at=("reverse_string", "1b"), run=False)
    hp = a.halted_draws_path(tmp_path, "1b", "reverse_string")
    rows = [json.loads(l) for l in gzip.open(hp, "rt")]
    rows[3]["draws"]["0"][2] += "?"                 # a second diff the record lacks
    with gzip.open(hp, "wt") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="own comparison of the .HALTED"):
        a.run(tmp_path)
    hp.unlink()                                    # absent: record stands, noted
    v = a.run(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["gate1"]["cells"]["reverse_string/1b"][
        "halted_rows_reverified"] is False


def test_scan_gate1_halt_is_silent_on_a_clean_or_empty_tree(tmp_path, env):
    assert a.scan_gate1_halt(tmp_path) == {"halted_cells": [], "cells": {},
                                          "records_present": 0}
    _gate1_tree(tmp_path, env)
    s = a.scan_gate1_halt(tmp_path)
    assert s["halted_cells"] == [] and s["records_present"] == 4
    # a halt record still carries every pin: a bad one is a hard error
    _gate1_tree(tmp_path, env, mutate=("rev_string7", "410m"))
    p = a.gate1_record_path(tmp_path, "410m", "rev_string7")
    _edit_record(p, model_sha="ff" * 20)
    with pytest.raises(ValueError, match="pinned"):
        a.scan_gate1_halt(tmp_path)


# ------------------------------------------- freeze F-2: attestations

def test_gate1_model_sha_pinned(tmp_path, env):
    _gate1_tree(tmp_path, env)
    p = a.gate1_record_path(tmp_path, "1b", "reverse_string")
    _edit_record(p, model_sha="ff" * 20)
    with pytest.raises(ValueError, match="model_sha"):
        a.load_gate1(tmp_path)


def test_argmax_model_sha_and_answer_type_pinned(tmp_path, env):
    for size in a.PROBE_SIZES:
        for rung in a.RUNGS:
            fs.write_argmax(tmp_path, size, rung, 0, verify=env["verify"])
    p = a.argmax_record_path(tmp_path, "410m", "mod17")
    good = p.read_text()
    for field, bad in (("model_sha", "ff" * 20), ("answer_type", "word")):
        _edit_record(p, **{field: bad})
        with pytest.raises(ValueError, match="provenance"):
            a.load_argmax(tmp_path, env["battery"], env["verify"])
        p.write_text(good)


def test_power_record_must_match_the_pilot_tier(tmp_path, env):
    """power_2d.json attests the pilot predictor it declared from; the
    analyzer compares it to the pilot tier recomputed from bytes."""
    for size in a.PROBE_SIZES:
        for rung in a.RUNGS:
            _one_cell(tmp_path, env, "pilot", size, rung,
                      40 if rung == "antonym" else 0)
    pred = fs.pilot_predictor_of(tmp_path, verify=env["verify"])
    fs.write_power(tmp_path, "POWERED", pred)
    a.check_power_vs_pilot(a.load_power_record(tmp_path / "power_2d.json"), pred)
    rec = json.loads((tmp_path / "power_2d.json").read_text())
    rec["pilot_predictor"]["mod17"]["score"] = 0.01
    (tmp_path / "power_2d.json").write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="attested pilot predictor"):
        a.check_power_vs_pilot(a.load_power_record(tmp_path / "power_2d.json"),
                               pred)
    del rec["pilot_predictor"]
    (tmp_path / "power_2d.json").write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="pilot_predictor"):
        a.load_power_record(tmp_path / "power_2d.json")


def test_run_refuses_a_power_record_that_disagrees_with_the_pilot(tmp_path):
    """Through run() itself (mutation [73]): a full tree whose
    power_2d.json attests a pilot predictor the pilot draws on disk do
    not reproduce must be refused before any verdict."""
    _, floors = fs.battery()
    ris = fs.rising_rungs()
    fs.build_world(tmp_path, main_verified=fs.counts_for(
        {r: floors[r]["floor"] + 0.2 for r in ris}), run=False)
    p = tmp_path / "power_2d.json"
    rec = json.loads(p.read_text())
    rec["pilot_predictor"]["mod17"]["raw_zero"]["1b"] = \
        not rec["pilot_predictor"]["mod17"]["raw_zero"]["1b"]
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="attested pilot predictor"):
        a.run(tmp_path)
