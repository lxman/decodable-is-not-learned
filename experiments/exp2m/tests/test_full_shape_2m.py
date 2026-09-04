# experiments/exp2m/tests/test_full_shape_2m.py
"""Every 2m terminal end to end on synthetic SmolLM3 trees (REAL
predictors through their real seal tags) via the production loaders."""
import json
import math

import pytest

from experiments.exp2i import battery_2i as bi
from experiments.exp2k import battery_2k as bk
from experiments.exp2m import analyze_2m as an
from experiments.exp2m import battery_2m as bm
from experiments.exp2m.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kw, want in fs.world_specs():
        root = tmp_path_factory.mktemp(name.split()[0])
        seal = fs.write_world_2m(root, **kw)
        out[name] = (fs.run_world(root, seal), want)
    return out


def test_every_terminal_reached(worlds):
    got = {}
    for name, (v, want) in worlds.items():
        if want is not None:
            assert v["verdict"] == want, f"{name}: {v['verdict']} ({v['reason']})"
        got.setdefault(v["verdict"], name)
    assert set(got) == set(an.WORLDS_2M)


def test_w1_pythia_only_shape(worlds):
    v, _ = worlds["W1 PYTHIA-ONLY"]
    A, B = v["tests"]["A"], v["tests"]["B"]
    assert A["fires"] is True and B["fires"] is False
    assert A["stratified"]["T"] >= 0.10 and A["stratified"]["p"] < 0.01
    assert A["eligible"] == list(fs.RUNGS_PRIMARY)
    sec = v["secondaries"]
    assert sec["S1 ladder 1b"][256]["stratified"]["T"] == A["stratified"]["T"]
    assert len(sec["S1 blocks 1b"]["T"]) == 4 and sec["S1 blocks 1b"]["sd"] is not None
    assert sec["S2 410m at 256"]["primary_form"]["stratified"]["T"] is not None
    assert sec["S3 B beyond A"]["stratified"]["T"] is not None and sec["S3 A beyond B"]["stratified"]["T"] is not None
    pd = sec["S3 paired difference"]
    assert pd["diff_B_minus_A"] < 0 and pd["ci95"][1] < 0 and pd["rungs"] == list(fs.RUNGS_PRIMARY)
    assert set(sec["S4 matched density"]["per_rung"]) == set(fs.RUNGS_PRIMARY)
    assert sec["S4 matched density"]["T_A256"] == A["stratified"]["T"]
    assert sec["S5 answer prior"]["non_gating"] is True
    s6 = sec["S6 twin stage3 base"]
    assert set(s6["twin_counts"]) == set(bm.bt.RUNGS) and all(c == 0 for c in s6["twin_counts"].values())
    assert set(s6["stage3_final_vs_endpoint"]) == set(bm.bt.RUNGS) and set(s6["base_vs_endpoint"]) == set(bm.bt.RUNGS)
    s7 = sec["S7 textures"]
    assert s7["collapses"] and any(c["step"] == bm.TWIN for c in s7["collapses"])      # the twin's ' zzz' x500
    assert set(s7["ceiling_fraction"]) == set(bm.bt.RUNGS)
    assert s7["ceiling_fraction"]["antonym"]["n_ceiling"] >= 1                       # the first-ranked items fire at 40k
    assert s7["first_correct_A"]["stratified"]["T"] is not None
    s8 = sec["S8 outcome order"]
    assert set(s8) == {"pythia_2.8b", "pythia_6.9b", "olmo2_7b", "olmo2_13b"}
    assert s8["olmo2_13b"]["rungs"] == list(fs.RUNGS_PRIMARY) and all(x["descriptive"] for x in s8.values())
    assert sec["extra rungs"] == {"eleven_extra": {}, "extra": {}}
    sens = sec["sensitivities"]
    assert sens["primary_is_the_nine"] is True and sens["log_head_subset"]["steps"] == list(bm.LOG_HEAD_SUBSET_2M)
    assert sens["log_head_subset"]["A"]["fires"] is True                             # the subset still carries the order
    assert sens["B_conditioned_on_A_median"]["stratified"]["T"] is not None
    assert sec["failures"] == []
    ref = v["referents"]
    assert ref["predictor_seal_2k"]["failures"] == [] and ref["predictor_seal_2i"]["failures"] == []
    for s in bk.SIZES_2K:
        for r in fs.RUNGS_PRIMARY:
            assert ref["gate1_2k"][s][r]["n_diffs"] == 0
    assert ref["endpoint_sha256"] and ref["gate1"]["prereg_tag"] == bm.PREREG_TAG_2M
    assert ref["dtype"] == bm.DTYPE_2M and ref["batch_size"] == bm.BATCH_SIZE_2M
    assert v["licensed_sentence"] == an.LICENSED_2M["PYTHIA-ONLY"]
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2M and v["calibration_note"] == an.CALIBRATION_SENTENCE_2M


def test_w2_olmo_only_and_w3_shared(worlds):
    v, _ = worlds["W2 OLMO-ONLY"]
    assert v["tests"]["B"]["fires"] is True and v["tests"]["A"]["fires"] is False
    assert v["secondaries"]["S3 paired difference"]["diff_B_minus_A"] > 0
    v, _ = worlds["W3 SHARED"]
    assert v["tests"]["A"]["fires"] and v["tests"]["B"]["fires"]


def test_w5_inverted_names_inversion(worlds):
    assert "inverted" in worlds["W5 NEITHER inverted"][0]["reason"]


def test_w6_underpowered_disclosure_rides_on_the_licence(worlds):
    v, _ = worlds["W6 PYTHIA-ONLY underpowered B disclosed"]
    assert v["verdict"] == "PYTHIA-ONLY"
    assert an.DISCLOSURE_UNDERPOWERED_2M["B"] in v["licensed_sentence"]
    assert an.DISCLOSURE_UNDERPOWERED_2M["A"] not in v["licensed_sentence"]


def test_w23_underpowered_a_disclosure_rides_on_the_licence(worlds):
    v, _ = worlds["W23 OLMO-ONLY underpowered A disclosed"]
    assert v["verdict"] == "OLMO-ONLY"
    assert an.DISCLOSURE_UNDERPOWERED_2M["A"] in v["licensed_sentence"]
    assert an.DISCLOSURE_UNDERPOWERED_2M["B"] not in v["licensed_sentence"]


def test_w18_extra_rungs_carry_an_undefined_d(worlds):
    v, _ = worlds["W18 PYTHIA-ONLY extra rungs with an undefined D"]
    ex = v["secondaries"]["extra rungs"]
    assert set(ex["eleven_extra"]) == {"count_div13"} and set(ex["extra"]) == {"caesar"}
    assert math.isnan(ex["eleven_extra"]["count_div13"]["stratified_d_A64"])
    assert math.isnan(ex["extra"]["caesar"]["raw_d_B"])
    assert v["secondaries"]["failures"] == []


def test_w18_verdict_json_is_strict_with_a_nan_secondary(tmp_path):
    seal = fs.write_world_2m(tmp_path, mode="pythia_only", all_fire=("count_div13", "caesar"))
    out = tmp_path / "verdict.json"
    an.run(root_2m=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, n_perm=30, n_boot=10,
           referents_sha=False, write=True, out_path=out, s8_loader=fs.s8_cached, **seal)
    rec = json.loads(out.read_text())
    assert rec["secondaries"]["extra rungs"]["extra"]["caesar"]["raw_d_A64"] is None
    assert "NaN" not in out.read_text()


def test_w19_thin_eligible_set_is_disclosed(worlds):
    v, _ = worlds["W19 thin eligible set (2l F-4)"]
    assert v["verdict"] != "INSUFFICIENT_DATA", v["reason"]
    assert v["secondaries"]["sensitivities"]["R_PRIMARY"] == ["add3_mid", "add_base8", "sub3_mid", "sub4_mid"]
    A = v["tests"]["A"]
    assert A["eligible"] == ["add_base8"] and sorted(A["thin"]) == ["add3_mid", "sub3_mid", "sub4_mid"]
    assert an.DISCLOSURE_THIN_2M not in v["reason"]
    for t in ("A", "B"):
        hit = [d for d in v["reason"].split("; ") if d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2M + t)]
        assert hit, v["reason"]
        assert hit[0] in v["licensed_sentence"]


def test_s8_production_loader_once(tmp_path):
    """The production S8 path (no injection) on one world: the four
    committed outcomes through their own frozen readers (≈ 2–4 min)."""
    seal = fs.write_world_2m(tmp_path, mode="shared")
    v = an.run(root_2m=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, n_perm=30, n_boot=10,
               referents_sha=False, **seal)
    s8 = v["secondaries"]["S8 outcome order"]
    assert set(s8) == {"pythia_2.8b", "pythia_6.9b", "olmo2_7b", "olmo2_13b"}
    assert s8["pythia_2.8b"]["rungs"] == [r for r in fs.RUNGS_PRIMARY if r in bm.bg.R_28]
    assert "failed" not in s8["olmo2_13b"]


def test_refusal_reasons(worlds):
    f = lambda n: worlds[n][0]["referents"]["failures"]
    assert any("2m endpoint stage1_final" in x for x in f("W7 INSUFFICIENT missing endpoint record"))
    assert any("2m endpoint seal binding" in x for x in f("W8 INSUFFICIENT drifted endpoint seal"))
    assert any("halted" in x for x in f("W9 INSUFFICIENT halted"))
    assert any("re-derive" in x for x in f("W10 INSUFFICIENT gate-1 diff (real bytes, attestation blind, no marker)"))
    assert any("attested bit_diffs" in x for x in f("W11 INSUFFICIENT gate-1 attested mismatch"))
    assert any("2m sweep smollm3_3b" in x for x in f("W12 INSUFFICIENT missing sweep record"))
    assert any("checkpoint record missing" in x for x in f("W13 INSUFFICIENT missing twin checkpoint record"))
    assert any("2m power record" in x for x in f("W14 INSUFFICIENT missing power"))
    assert any("predictor_sha256" in x for x in f("W15 INSUFFICIENT power sha"))
    assert any("2m power claims" in x for x in f("W16 INSUFFICIENT power claims"))
    assert any("endpoint_sha256" in x for x in f("W17 INSUFFICIENT endpoint file edited after the sweep stamped its sha"))
    assert any("2m endpoint base" in x for x in f("W20 INSUFFICIENT missing base record"))
    assert any("2m sweep smollm3_3b" in x and "twin" in x for x in f("W21 INSUFFICIENT missing twin record"))
    assert any("dtype" in x for x in f("W22 INSUFFICIENT a record at another precision"))
    for n in ("W7 INSUFFICIENT missing endpoint record", "W22 INSUFFICIENT a record at another precision"):
        v = worlds[n][0]
        assert v["tests"] is None and v["secondaries"] is None
