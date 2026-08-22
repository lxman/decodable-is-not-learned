"""analyze_2e: the pins, the manifest, the tally pin, the 2d
comparison gate (on the REAL tree — a known answer, not the verdict)
and the referent phase's refusal-to-failure routing."""
import hashlib
import json

import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import stats_2d as st
from experiments.exp2e import analyze_2e as a
from experiments.exp2e import functionals_2e as fn
from experiments.exp2e import make_referents_2e as mk
from experiments.exp2e.tests import full_shape as fs


# ------------------------------------------------------------------ pins

def test_frozen_import_pins_hold_on_disk():
    a.check_frozen_imports_2e()
    assert {p.name for p in a.FROZEN_IMPORT_SHA256_2E} >= {
        "analyze_2d.py", "stats_2d.py", "battery_2d.py", "rederive_2d.py",
        "referents_2d.json", "stream_map_2d.json", "power_2d.json"}


def test_frozen_import_pin_fires(monkeypatch):
    pins = dict(a.FROZEN_IMPORT_SHA256_2E)
    k = next(iter(pins))
    pins[k] = "0" * 64
    monkeypatch.setattr(a, "FROZEN_IMPORT_SHA256_2E", pins)
    with pytest.raises(ValueError, match="frozen file"):
        a.check_frozen_imports_2e()


def test_tally_pin_is_the_doc_table():
    assert len(a.MAIN_TALLY_PIN) == 68
    assert a.MAIN_TALLY_PIN[("arith_next", "410m")] == 831
    assert a.MAIN_TALLY_PIN[("arith_next", "1b")] == 531
    assert a.MAIN_TALLY_PIN[("reverse_string", "1b")] == 1
    assert a.MAIN_TALLY_PIN[("rev_string7", "410m")] == 0
    assert a.MAIN_TALLY_PIN[("antonym", "410m")] == 5015
    assert all(isinstance(v, int) for v in a.MAIN_TALLY_PIN.values())
    assert {r for r, _ in a.MAIN_TALLY_PIN} == set(a2d.RUNGS)


def test_verdict_2d_pin_literals():
    assert a.VERDICT_2D_PIN["auc"] == 0.5454545454545454
    assert a.VERDICT_2D_PIN["block_p"] == 0.6674933250667493
    assert a.VERDICT_2D_PIN["ci"] == [0.5, 0.6666666666666666]
    assert a.VERDICT_2D_PIN["bootstrap_n_dropped"] == 2
    assert a.VERDICT_2D_PIN["verdict"] == "FAIL"
    v = json.loads((a2d.EXP2D / "results" / "verdict.json").read_text())
    assert a.verdict_2d_pin_from_record(v) == a.VERDICT_2D_PIN
    assert a.PROBE_2C_AUC_PIN == v["secondaries"]["probe_predictor_auc"]["auc"]


# -------------------------------------------------------------- manifest

@pytest.fixture(scope="module")
def world(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("w")
    _, floors = fs.battery()
    pins = fs.build_world(tmp, main_verified=fs.counts_for(
        {r: floors[r]["floor"] + 0.2 for r in fs.rising_rungs()}), run=False)
    return tmp, pins


def test_manifest_build_is_idempotent_and_complete(world, tmp_path):
    root, pins = world
    p1 = tmp_path / "m1.json"
    p2 = tmp_path / "m2.json"
    r1 = mk.build(root, p1)
    r2 = mk.build(root, p2)
    assert p1.read_bytes() == p2.read_bytes()
    assert r1["n_files"] == 273 and len(r1["files"]) == 273
    assert "results/verdict.json" in r1["files"]
    assert sum(k.startswith("results/main/") for k in r1["files"]) == 136
    assert sum(k.startswith("results/pilot/") for k in r1["files"]) == 136
    assert all(not k.startswith("/") for k in r1["files"])


def test_manifest_check_reports_changed_and_missing(world, tmp_path):
    root, pins = world
    rec = a.load_manifest(pins["manifest_path"], file_sha_pin=pins["manifest_sha_pin"])
    assert a.check_manifest(root, rec) == []
    with pytest.raises(ValueError, match="sha256"):
        a.load_manifest(pins["manifest_path"], file_sha_pin="0" * 64)
    rec2 = json.loads(json.dumps(rec))
    k = "results/pilot/1b_trained/base7.json"
    rec2["files"][k] = "1" * 64
    # one entry renamed (count unchanged): the named file is missing
    rec2["files"]["results/pilot/1b_trained/nope.json"] = \
        rec2["files"].pop("results/pilot/1b_trained/base13.json")
    bad = a.check_manifest(root, rec2)
    assert len(bad) == 2 and any("missing" in b for b in bad) \
        and any(k in b for b in bad)
    with pytest.raises(ValueError, match="n_files"):
        rec3 = dict(rec); rec3["n_files"] = 5
        a.check_manifest(root, rec3)


def test_real_manifest_pinned_by_literal():
    rec = a.load_manifest()
    assert rec["n_files"] == 273
    got = hashlib.sha256(a.REFERENTS_PATH.read_bytes()).hexdigest()
    assert got == a.REFERENTS_FILE_SHA256
    assert a.check_manifest(a2d.EXP2D, rec) == []


# ------------------------------------------------------------ tally pin

def test_tally_pin_check(world):
    root, pins = world
    battery, floors = fs.battery()
    cells = a2d.load_sampling_tier(root, "main", battery, a2d.load_verify())
    assert a.check_tally_pin(cells, pins["tally_pin"]) == []
    bad = dict(pins["tally_pin"]); bad[("mod17", "1b")] += 5
    f = a.check_tally_pin(cells, bad)
    assert len(f) == 1 and "mod17/1b" in f[0] and "tally pin" in f[0]


# ---------------------------------------------- 2d comparison (real tree)

def test_comparison_gate_reproduces_2d_primary_on_the_real_tree():
    """The known-answer gate for the inherited statistic: 2d's
    thresholded predictor re-derived from the committed main tier
    through 2d's own code == 2d's verdict.json primary, exactly."""
    battery, floors = fs.battery()
    cells = a2d.load_sampling_tier(a2d.EXP2D, "main", battery, a2d.load_verify())
    out = fs.outcome()
    cmp = a.comparison_2d(cells, floors, out)
    v = json.loads((a2d.EXP2D / "results" / "verdict.json").read_text())
    assert cmp["auc"] == v["primary"]["auc"] == 0.5454545454545454
    assert cmp["block_p"] == v["primary"]["block_p"]
    assert cmp["ci"] == v["primary"]["ci"]
    assert cmp["bootstrap_n_dropped"] == v["primary"]["bootstrap_n_dropped"]
    assert a.check_comparison_2d(cmp, a2d.EXP2D, a.VERDICT_2D_PIN) == []
    assert a.check_tally_pin(cells, a.MAIN_TALLY_PIN) == []


def test_comparison_gate_fires_on_literal_mismatch(world):
    root, pins = world
    battery, floors = fs.battery()
    cells = a2d.load_sampling_tier(root, "main", battery, a2d.load_verify())
    cmp = a.comparison_2d(cells, floors, fs.outcome())
    assert a.check_comparison_2d(cmp, root, pins["verdict_2d_pin"]) == []
    pin = dict(pins["verdict_2d_pin"]); pin["auc"] = 0.123
    f = a.check_comparison_2d(cmp, root, pin)
    assert len(f) == 1 and "2d comparison" in f[0] and "literal" in f[0]


# ------------------------------------------- refusals become failures

def test_outcome_gate_failure_is_collected(monkeypatch, tmp_path):
    real = a2d._m4_path("12b", "trained", "sub4_mid")
    alt = tmp_path / "sub4_mid.json"
    rec = json.loads(real.read_text()); rec["correct"] += 3
    alt.write_text(json.dumps(rec))
    orig = a2d._m4_path
    monkeypatch.setattr(a2d, "_m4_path", lambda s, m, r: alt if (s, m, r) == (
        "12b", "trained", "sub4_mid") else orig(s, m, r))
    _, floors = fs.battery()
    got, failures = a.collect(lambda: a2d.load_outcome(floors), "outcome")
    assert got is None and len(failures) == 1 and \
        "known-answer gate" in failures[0] and failures[0].startswith("outcome:")


def test_collect_passes_non_refusal_errors_through():
    with pytest.raises(TypeError):
        a.collect(lambda: 1 + "x", "x")
    got, f = a.collect(lambda: 7, "x")
    assert got == 7 and f == []


# ------------------------------------------ verdict_2e on synthetic cells
#
# Disk-free: synthetic tally dicts in 2d's loader shape, the REAL
# outcome / floors / probe, the 2d comparison column computed from the
# same synthetic cells. What the worlds prove end to end, these prove
# fast enough for the mutation battery.

def _cells(rate_by_rung, n, floors):
    out = {}
    for r in a2d.RUNGS:
        for s in a2d.PROBE_SIZES:
            v = int(round(rate_by_rung.get(r, 0.0) * n))
            out[(r, s)] = {"verified": v, "n_draws": n, "rate": v / n}
    return out


@pytest.fixture(scope="module")
def synth():
    _, floors = fs.battery()
    out = fs.outcome()
    ris, fla = fs.rising_rungs(), fs.flat_rungs()
    rate = {**{r: floors[r]["floor"] * 1.05 for r in ris},
            **{r: floors[r]["floor"] * 0.95 for r in fla}}
    main = _cells(rate, 32_000, floors)
    pilot = _cells(rate, 4_000, floors)
    cmp = a.comparison_2d(main, floors, out)
    ref = {"failures": [], "manifest": {"n_files": 273}}
    v = a.verdict_2e(outcome=out, main_cells=main, pilot_cells=pilot,
                     floors=floors, probe=a2d.load_probe_predictor(),
                     cmp2d=cmp, referents=ref)
    return v, main, pilot, floors, out


def test_synth_primary_is_f1_and_f2_differs(synth):
    v, main, pilot, floors, out = synth
    assert v["verdict"] == "PASS" and v["primary"]["functional"] == "F1"
    f = v["secondaries"]["functionals"]
    assert v["primary"]["auc"] == f["F1"]["auc"] == 1.0
    assert f["F2"]["auc"] < .75
    import numpy as np
    y = np.array([int(v["per_rung"][r]["rising"]) for r in a2d.RUNGS])
    assert v["primary"]["auc"] == st.auc(
        np.array([v["per_rung"][r]["F1"] for r in a2d.RUNGS]), y)
    assert f["F2"]["auc"] == st.auc(
        np.array([v["per_rung"][r]["F2"] for r in a2d.RUNGS]), y)
    assert f["B0"]["auc"] == st.auc(
        np.array([v["per_rung"][r]["B0"] for r in a2d.RUNGS]), y)
    assert f["F3"]["auc"] == st.auc(
        np.array([v["per_rung"][r]["F3"] for r in a2d.RUNGS]), y)


def test_synth_record_carries_disclosure_and_b0_sentence(synth):
    v, *_ = synth
    assert v["known_inputs_caveat"] == a.KNOWN_INPUTS_CAVEAT_2E
    s = v["licensed_sentence_if_pass"]
    b0 = v["secondaries"]["functionals"]["B0"]["auc"]
    assert f"{b0:.4f}" in s and "floor alone" in s \
        and a.KNOWN_INPUTS_CAVEAT_2E in s and "threshold" in s
    assert v["model_contact"] == "none"


def test_synth_pilot_uses_its_own_eps_and_is_non_gating(synth):
    v, main, pilot, floors, out = synth
    pil = v["secondaries"]["pilot_replication"]
    assert pil["eps"] == 1 / 8_000 and pil["n_draws_per_cell"] == 4_000
    assert v["primary"]["eps"] == 1 / 64_000
    assert v["per_rung"]["antonym"]["F1_pilot"] != v["per_rung"]["antonym"]["F1"]
    # same rates, but 4,000-draw rounding and ε = 1/8,000 reorder the
    # small-floor rungs: high, not 1.0
    assert isinstance(pil["rank_corr_pilot_vs_main_f1"], float)
    assert pil["rank_corr_pilot_vs_main_f1"] > .7


def test_synth_secondaries_shape(synth):
    v, main, pilot, floors, out = synth
    sec = v["secondaries"]
    d = sec["f1_minus_b0"]
    assert d["diff_obs"] == pytest.approx(1.0 - sec["functionals"]["B0"]["auc"])
    assert d["n_valid"] + d["n_dropped"] == 10_000
    assert [e["eps"] for e in sec["sensitivity"]["eps"]] == list(fn.EPS_SENSITIVITY)
    assert sec["sensitivity"]["eps"][0]["auc"] == v["primary"]["auc"]
    assert sec["sensitivity"]["drop_first_digit_run_rungs"]["n_rungs"] == 32
    assert sec["sensitivity"]["majority_floor_only"]["rungs_affected"] == \
        sorted(a2d.bt.OPTION_LISTING_PIN)
    assert sec["sensitivity_12b_only_label"]["n_rising"] == 9
    assert sec["replication_1b_only"]["auc"] == 1.0
    assert sec["probe_predictor_2c"]["auc_matches_2d_record"]
    assert sec["comparison_2d_thresholded"]["n_rising"] == 11
    for k in ("F1", "F2", "F3", "B0"):
        o = sec["ordering_vs_corrected_ascent"][k]
        assert o["rho"] is not None and o["block_p"] is not None
    assert set(v["per_rung"]) == set(a2d.RUNGS)
    row = v["per_rung"]["mod17"]
    assert row["rate_1b"] == main[("mod17", "1b")]["rate"]
    assert row["score_2d"] == 0.0 and not row["rising"]


def test_synth_majority_only_sensitivity_moves_option_rungs(synth):
    v, main, pilot, floors, out = synth
    # under the majority-only floor the six option-listing rungs score
    # higher (their floors drop), so the sensitivity AUC can differ
    t = fn.f1_table(main, floors, floor_key="majority_floor")
    for r in a2d.bt.OPTION_LISTING_PIN:
        assert t[r]["score"] > v["per_rung"][r]["F1"]
    for r in ("mod17", "base7"):
        assert t[r]["score"] == v["per_rung"][r]["F1"]


def test_insufficient_record_shape():
    _, floors = fs.battery()
    v = a.insufficient_data_record_2e(["manifest: x missing"],
                                      referents={"failures": ["manifest: x missing"]},
                                      outcome=None)
    assert v["verdict"] == "INSUFFICIENT_DATA" and v["primary"] is None
    assert v["known_inputs_caveat"] == a.KNOWN_INPUTS_CAVEAT_2E
    assert v["outcome_summary"] is None and "x missing" in v["reason"]
