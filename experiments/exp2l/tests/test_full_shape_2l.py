# experiments/exp2l/tests/test_full_shape_2l.py
"""Every 2l terminal end to end on synthetic 13B trees (REAL predictors
through their real seal tags) via the production loaders."""
import json

import pytest

from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2k import battery_2k as bk
from experiments.exp2l import analyze_2l as an
from experiments.exp2l import battery_2l as bl
from experiments.exp2l.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kw, want in fs.world_specs():
        root = tmp_path_factory.mktemp(name.split()[0])
        seal = fs.write_world_2l(root, **kw)
        out[name] = (fs.run_world(root, seal), want)
    return out


def test_every_terminal_reached(worlds):
    got = {}
    for name, (v, want) in worlds.items():
        if want is not None:                      # W19 asserts a disclosure, not a terminal
            assert v["verdict"] == want, f"{name}: {v['verdict']} ({v['reason']})"
        got.setdefault(v["verdict"], name)
    assert set(got) == set(an.WORLDS)     # every verdict comes from WORLDS, so this is equality


def test_w1_shared_shape(worlds):
    v, _ = worlds["W1 SHARED"]
    A, B = v["tests"]["A"], v["tests"]["B"]
    assert A["fires"] is True and B["fires"] is False
    assert A["stratified"]["T"] >= 0.10 and A["stratified"]["p"] < 0.01
    assert A["eligible"] == list(fs.RUNGS_PRIMARY)
    sec = v["secondaries"]
    assert sec["S1 ladder 1b"][256]["stratified"]["T"] == A["stratified"]["T"]
    assert len(sec["S1 blocks 1b"]["T"]) == 4 and sec["S1 blocks 1b"]["sd"] is not None
    assert sec["S2 410m at 256"]["primary_form"]["stratified"]["T"] is not None
    assert sec["S3 within alone"]["stratified"]["T"] is not None
    assert sec["S3 cross beyond within"]["stratified"]["T"] is not None
    assert set(sec["S4 matched density"]["per_rung"]) == set(fs.RUNGS_PRIMARY)
    assert sec["S4 matched density"]["T_A256"] == A["stratified"]["T"]
    assert sec["S5 answer prior"]["non_gating"] is True
    assert set(sec["S6 step0 and main"]["step0_counts"]) == set(bl.bt.RUNGS)
    assert all(c == 0 for c in sec["S6 step0 and main"]["step0_counts"].values())
    s7 = sec["S7 textures"]
    assert s7["collapses"] and any(c["correct"] == 0 for c in s7["collapses"])   # the 25 all-zero rungs emit ' zzz' ×500
    assert s7["first_correct_A"]["stratified"]["T"] is not None
    assert sec["extra rungs"] == {"eleven_extra": {}, "extra": {}}
    assert sec["sensitivities"]["primary_is_the_nine"] is True
    assert sec["failures"] == []
    ref = v["referents"]
    assert ref["predictor_seal_2k"]["failures"] == [] and ref["predictor_seal_2i"]["failures"] == []
    for s in bk.SIZES_2K:
        for r in fs.RUNGS_PRIMARY:
            assert ref["gate1_2k"][s][r]["n_diffs"] == 0
    assert ref["endpoint_sha256"] and ref["gate1"]["prereg_tag"] == bl.PREREG_TAG_2L
    assert v["licensed_sentence"] == an.LICENSED_2L["SHARED"]
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2L
    assert v["calibration_note"] == an2i.CALIBRATION_SENTENCE_2I


def test_w2_lineage_and_w3_both(worlds):
    v, _ = worlds["W2 LINEAGE"]
    assert v["tests"]["B"]["fires"] is True and v["tests"]["A"]["fires"] is False
    v, _ = worlds["W3 BOTH"]
    assert v["tests"]["A"]["fires"] and v["tests"]["B"]["fires"]


def test_w5_inverted_names_inversion(worlds):
    v, _ = worlds["W5 NEITHER inverted"]
    assert "inverted" in v["reason"]


def test_w6_underpowered_disclosure_rides_on_the_licence(worlds):
    v, _ = worlds["W6 SHARED underpowered B disclosed"]
    assert v["verdict"] == "SHARED"
    assert an.DISCLOSURE_UNDERPOWERED_2L["B"] in v["licensed_sentence"]
    assert an.DISCLOSURE_UNDERPOWERED_2L["A"] not in v["licensed_sentence"]


def test_w18_extra_rungs_carry_an_undefined_d(worlds):
    """FREEZE item 16: the printed extra rungs have a CONSTANT outcome, so
    Somers' D is undefined (NaN) — the verdict must still be built."""
    import math
    v, _ = worlds["W18 SHARED extra rungs with an undefined D"]
    ex = v["secondaries"]["extra rungs"]
    assert set(ex["eleven_extra"]) == {"count_div13"} and set(ex["extra"]) == {"caesar"}
    assert math.isnan(ex["eleven_extra"]["count_div13"]["stratified_d_A64"])
    assert math.isnan(ex["extra"]["caesar"]["raw_d_B"])
    assert v["secondaries"]["failures"] == []


def test_w18_verdict_json_is_strict_with_a_nan_secondary(tmp_path):
    """The same world through the WRITE path: `json.dumps(...,
    allow_nan=False)` must survive the NaN via `_json_safe`."""
    seal = fs.write_world_2l(tmp_path, mode="a_only", all_fire=("count_div13", "caesar"))
    out = tmp_path / "verdict.json"
    an.run(root_2l=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, n_perm=30, n_boot=10,
           referents_sha=False, write=True, out_path=out, **seal)
    rec = json.loads(out.read_text())
    assert rec["secondaries"]["extra rungs"]["extra"]["caesar"]["raw_d_A64"] is None
    assert "NaN" not in out.read_text()


def test_w19_thin_eligible_set_is_disclosed(worlds):
    """FREEZE F-4: |R_PRIMARY| = 4, so DISCLOSURE_THIN_2L does not fire —
    but `cells_for`'s n_pos floor leaves each test one eligible rung."""
    v, _ = worlds["W19 thin eligible set (F-4)"]
    assert v["verdict"] != "INSUFFICIENT_DATA", v["reason"]
    assert v["secondaries"]["sensitivities"]["R_PRIMARY"] == \
        ["add3_mid", "add_base8", "sub3_mid", "sub4_mid"]
    A = v["tests"]["A"]
    assert A["eligible"] == ["add_base8"] and sorted(A["thin"]) == ["add3_mid", "sub3_mid", "sub4_mid"]
    assert an.DISCLOSURE_THIN_2L not in v["reason"]
    for t in ("A", "B"):
        hit = [d for d in v["reason"].split("; ")
               if d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2L + t)]
        assert hit, v["reason"]
        assert hit[0] in v["licensed_sentence"]


def test_refusal_reasons(worlds):
    f = lambda n: worlds[n][0]["referents"]["failures"]
    assert any("2l endpoint stage1_final" in x for x in f("W7 INSUFFICIENT missing endpoint record"))
    assert any("2l endpoint seal binding" in x for x in f("W8 INSUFFICIENT drifted endpoint seal"))
    assert any("halted" in x for x in f("W9 INSUFFICIENT halted"))
    assert any("re-derivation (byte identity)" in x or "re-derive" in x for x in f("W10 INSUFFICIENT gate-1 diff (real bytes, attestation blind, no marker)"))
    assert any("attested bit_diffs" in x for x in f("W11 INSUFFICIENT gate-1 attested mismatch"))
    assert any("2l sweep olmo13b" in x for x in f("W12 INSUFFICIENT missing sweep record"))
    assert any("checkpoint record missing" in x for x in f("W13 INSUFFICIENT missing step-0 checkpoint record"))
    assert any("2l power record" in x for x in f("W14 INSUFFICIENT missing power"))
    assert any("predictor_sha256" in x for x in f("W15 INSUFFICIENT power sha"))
    assert any("2l power claims" in x for x in f("W16 INSUFFICIENT power claims"))
    assert any("endpoint_sha256" in x for x in f("W17 INSUFFICIENT endpoint file edited after the sweep stamped its sha"))
    for n in ("W7 INSUFFICIENT missing endpoint record", "W10 INSUFFICIENT gate-1 diff (real bytes, attestation blind, no marker)"):
        v = worlds[n][0]
        assert v["tests"] is None and v["secondaries"] is None
