# experiments/exp2n/tests/test_full_shape_2n.py
"""Every 2n terminal end to end on synthetic Comma trees (REAL
predictors through their real seal tags) via the production loaders."""
import json
import math

import pytest

from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2k import battery_2k as bk
from experiments.exp2n import analyze_2n as an
from experiments.exp2n import battery_2n as bn
from experiments.exp2n.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kw, want in fs.world_specs():
        root = tmp_path_factory.mktemp(name.split()[0])
        seal = fs.write_world_2n(root, **kw)
        # The world ROOT is kept in the tuple: the dial-b equality guard
        # in `test_w1_pythia_only_shape` re-derives Test B from the same
        # synthetic tree the verdict was computed on.
        out[name] = (fs.run_world(root, seal), want, root)
    return out


def test_every_terminal_reached(worlds):
    got = {}
    for name, (v, want, _root) in worlds.items():
        if want is not None:
            assert v["verdict"] == want, f"{name}: {v['verdict']} ({v['reason']})"
        got.setdefault(v["verdict"], name)
    assert set(got) == set(an.WORLDS_2N)


def test_w1_pythia_only_shape(worlds):
    v, _, root = worlds["W1 PYTHIA-ONLY"]
    A, B = v["tests"]["A"], v["tests"]["B"]
    assert A["fires"] is True and B["fires"] is False
    assert A["stratified"]["T"] >= 0.10 and A["stratified"]["p"] < 0.01
    assert A["eligible"] == list(fs.RUNGS_PRIMARY)
    sec = v["secondaries"]
    assert sec["S1 ladder 1b"][256]["stratified"]["T"] == A["stratified"]["T"]
    assert len(sec["S1 blocks 1b"]["T"]) == 4 and sec["S1 blocks 1b"]["sd"] is not None
    assert sec["S2 410m at 256"]["primary_form"]["stratified"]["T"] is not None
    assert sec["S3 B beyond A"]["stratified"]["T"] is not None and sec["S3 A beyond B"]["stratified"]["T"] is not None
    # Mutation closure (2m's Task 5, #88) and dial b restated as a test: the
    # PRIMARY Test B is UNCONDITIONED, read on 2g's base strata — it is
    # NOT S3's conditioned form (x_B beyond x_A's median bucket), which
    # is what 2l's construction made primary.
    assert B["stratified"]["T"] != sec["S3 B beyond A"]["stratified"]["T"]
    pd = sec["S3 paired difference"]
    assert pd["diff_B_minus_A"] < 0 and pd["ci95"][1] < 0 and pd["rungs"] == list(fs.RUNGS_PRIMARY)
    assert set(sec["S4 matched density"]["per_rung"]) == set(fs.RUNGS_PRIMARY)
    assert sec["S4 matched density"]["T_A256"] == A["stratified"]["T"]
    assert sec["S5 answer prior"]["non_gating"] is True
    # Freeze F-3: the descriptives say in words that their `fires` key is
    # not a firing rule.
    assert sec["S5 answer prior"]["no_alpha_claim"] is True
    assert sec["S5 answer prior"]["note"] == an.NO_ALPHA_NOTE_2N.format(name="S5")
    s6 = sec["S6 twin stage2 main"]
    assert set(s6["twin_counts"]) == set(bn.bt.RUNGS) and all(c == 0 for c in s6["twin_counts"].values())
    assert set(s6["stage2_final_vs_endpoint"]) == set(bn.bt.RUNGS) and set(s6["main_vs_endpoint"]) == set(bn.bt.RUNGS)
    s7 = sec["S7 textures"]
    assert s7["collapses"] and any(c["step"] == bn.TWIN for c in s7["collapses"])      # the twin's ' zzz' x500
    assert set(s7["ceiling_fraction"]) == set(bn.bt.RUNGS)
    assert s7["ceiling_fraction"]["antonym"]["n_ceiling"] >= 1                       # the first-ranked items fire at 40k
    assert s7["first_correct_A"]["stratified"]["T"] is not None
    s8 = sec["S8 outcome order"]
    assert set(s8) == {"pythia_2.8b", "pythia_6.9b", "olmo2_7b", "olmo2_13b", "smollm3_3b"}
    assert s8["olmo2_13b"]["rungs"] == list(fs.RUNGS_PRIMARY) and all(x["descriptive"] for x in s8.values())
    assert all(x["no_alpha_claim"] and x["note"] == an.NO_ALPHA_NOTE_2N.format(name="S8")
               for x in s8.values())
    assert sec["extra rungs"] == {"eleven_extra": {}, "extra": {}}
    sens = sec["sensitivities"]
    assert sens["primary_is_the_nine"] is True and sens["every40k_subset"]["steps"] == list(bn.EVERY40K_SUBSET_2N)
    assert sens["every40k_subset"]["A"]["fires"] is True                             # the subset still carries the order
    # Mutation closure (2m's Task 5, #99): the sensitivity is computed over
    # the 12-point EVERY40K_SUBSET_2N, not over the full 24-point grid —
    # a different outcome, so a different T from the primary's.
    assert sens["every40k_subset"]["A"]["stratified"]["T"] != A["stratified"]["T"]
    assert sens["every40k_subset"]["B"]["stratified"]["T"] is not None
    assert sens["every40k_subset"]["B"]["stratified"]["T"] != B["stratified"]["T"]
    assert sens["B_conditioned_on_A_median"]["stratified"]["T"] is not None
    assert sec["failures"] == []
    ref = v["referents"]
    assert ref["predictor_seal_2k"]["failures"] == [] and ref["predictor_seal_2i"]["failures"] == []
    for s in bk.SIZES_2K:
        for r in fs.RUNGS_PRIMARY:
            assert ref["gate1_2k"][s][r]["n_diffs"] == 0
    assert ref["endpoint_sha256"] and ref["gate1"]["prereg_tag"] == bn.PREREG_TAG_2N
    assert ref["dtype"] == bn.DTYPE_2N and ref["batch_size"] == bn.BATCH_SIZE_2N
    # Test-side correction (root cause: 2m never carried an annotation, so
    # its licensed_sentence == LICENSED_2M[verdict] exactly; 2n's
    # `_licensed_2n` always appends the C_MODIFIERS_2N text after the base
    # licence — an exact match can never hold here, only a prefix, same
    # style as the referent battery's item 8 "licence prefix" checks).
    assert v["licensed_sentence"].startswith(an.LICENSED_2N["PYTHIA-ONLY"])
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2N and v["calibration_note"] == an.CALIBRATION_SENTENCE_2N
    # Dial b in its EXACT form (mutation closure, 2m's Task 5 fix round 1, #88):
    # Test B re-derived from this world's own tree on the BARE base strata
    # must be the verdict's B, statistic for statistic. `_run_test` is
    # deterministic at a fixed seed and the inputs here are the same objects
    # `run()` used, so this is an equality, not a tolerance. The `!=` line
    # above rules out S3's conditioned form; this rules IN the base one.
    sweep = an.load_sweep_comma(root, fs.battery(), fs.verify_fn(), manifest=fs.manifest(),
                                endpoint_sha=bn.endpoint_sha256(root))
    out = an.outcomes_comma(sweep, rungs=tuple(bn.bt.RUNGS))
    B_base = an2i._run_test(fs.x_b_real(), bi.SIZE_PRED, out, fs.strata(), fs.RUNGS_PRIMARY,
                            n_perm=200, n_boot=20)
    assert B_base["stratified"]["T"] == B["stratified"]["T"]


def test_w2_olmo_only_and_w3_shared(worlds):
    v, _, _root = worlds["W2 OLMO-ONLY"]
    assert v["tests"]["B"]["fires"] is True and v["tests"]["A"]["fires"] is False
    assert v["secondaries"]["S3 paired difference"]["diff_B_minus_A"] > 0
    v, _, _root = worlds["W3 SHARED"]
    assert v["tests"]["A"]["fires"] and v["tests"]["B"]["fires"]


def test_w5_inverted_names_inversion(worlds):
    assert "inverted" in worlds["W5 NEITHER inverted"][0]["reason"]


def test_w6_underpowered_disclosure_rides_on_the_licence(worlds):
    v, _, _root = worlds["W6 PYTHIA-ONLY underpowered B disclosed"]
    assert v["verdict"] == "PYTHIA-ONLY"
    assert an.DISCLOSURE_UNDERPOWERED_2N["B"] in v["licensed_sentence"]
    assert an.DISCLOSURE_UNDERPOWERED_2N["A"] not in v["licensed_sentence"]


def test_w23_underpowered_a_disclosure_rides_on_the_licence(worlds):
    v, _, _root = worlds["W23 OLMO-ONLY underpowered A disclosed"]
    assert v["verdict"] == "OLMO-ONLY"
    assert an.DISCLOSURE_UNDERPOWERED_2N["A"] in v["licensed_sentence"]
    assert an.DISCLOSURE_UNDERPOWERED_2N["B"] not in v["licensed_sentence"]


def test_w18_extra_rungs_carry_an_undefined_d(worlds):
    v, _, _root = worlds["W18 PYTHIA-ONLY extra rungs with an undefined D"]
    ex = v["secondaries"]["extra rungs"]
    assert set(ex["eleven_extra"]) == {"count_div13"} and set(ex["extra"]) == {"caesar"}
    assert math.isnan(ex["eleven_extra"]["count_div13"]["stratified_d_A64"])
    assert math.isnan(ex["extra"]["caesar"]["raw_d_B"])
    assert v["secondaries"]["failures"] == []


def test_w18_verdict_json_is_strict_with_a_nan_secondary(tmp_path):
    seal = fs.write_world_2n(tmp_path, mode="pythia_only", all_fire=("count_div13", "caesar"))
    out = tmp_path / "verdict.json"
    # Ruling 5: FROZEN_SHA256_2N/IMPORTED_SHA256_2N still empty/None
    # pending Task 5 — the same stand-ins as `run_world`.
    frozen_check = None if bn.FROZEN_SHA256_2N else (lambda: None)
    imports_pinned = True if an.IMPORTED_SHA256_2N is not None else False
    an.run(root_2n=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, n_perm=30, n_boot=10,
           referents_sha=False, write=True, out_path=out, s8_loader=fs.s8_cached,
           frozen_check=frozen_check, imports_pinned=imports_pinned, **seal)
    rec = json.loads(out.read_text())
    assert rec["secondaries"]["extra rungs"]["extra"]["caesar"]["raw_d_A64"] is None
    assert "NaN" not in out.read_text()


def test_w19_thin_eligible_set_is_disclosed(worlds):
    v, _, _root = worlds["W19 thin eligible set (2l F-4)"]
    assert v["verdict"] != "INSUFFICIENT_DATA", v["reason"]
    assert v["secondaries"]["sensitivities"]["R_PRIMARY"] == ["add3_mid", "add_base8", "sub3_mid", "sub4_mid"]
    A = v["tests"]["A"]
    assert A["eligible"] == ["add_base8"] and sorted(A["thin"]) == ["add3_mid", "sub3_mid", "sub4_mid"]
    assert an.DISCLOSURE_THIN_2N not in v["reason"]
    for t in ("A", "B"):
        hit = [d for d in v["reason"].split("; ") if d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2N + t)]
        assert hit, v["reason"]
        assert hit[0] in v["licensed_sentence"]


def test_w24_partial_eligible_set_is_disclosed(worlds):
    """Freeze F-1: R_PRIMARY carries nine rungs, both tests read eight
    (`add3_mid` has 12 positives — it clears 2d's endpoint bar at k = 9
    and misses the n_pos >= 20 eligibility), the power record still
    declares POWERED over all nine, and 2l F-4's guard is silent because
    eight >= three. The disclosure names the rung and rides on the
    licence."""
    v, _, _root = worlds["W24 PYTHIA-ONLY partial eligible set disclosed (freeze F-1)"]
    assert v["verdict"] == "PYTHIA-ONLY", v["reason"]
    A, B = v["tests"]["A"], v["tests"]["B"]
    assert A["thin"] == ["add3_mid"] and "add3_mid" not in A["eligible"] and len(A["eligible"]) == 8
    assert B["thin"] == ["add3_mid"] and len(B["eligible"]) == 8
    assert v["referents"]["power"]["A"]["rungs_simulated"] == list(fs.RUNGS_PRIMARY)
    assert v["referents"]["power"]["A"]["declared_status"] == "POWERED"
    assert an.DISCLOSURE_THIN_2N not in v["reason"]
    assert not any(d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2N) for d in v["reason"].split("; "))
    for t in ("A", "B"):
        hit = [d for d in v["reason"].split("; ")
               if d.startswith(an.DISCLOSURE_PARTIAL_ELIGIBLE_PREFIX_2N + t)]
        assert hit, v["reason"]
        assert "add3_mid" in hit[0] and hit[0] in v["licensed_sentence"]


def test_w25_a_which_assembled_from_two_loads_refuses(worlds):
    """Freeze F-2: `stage2_final`'s 34 records carry two different tensor
    digests, written before the rung set's sha table and the 104-file
    composite were computed, so both agree with the mixed tree. Gate 1
    never reads stage2_final and no sha check fires — the which-coherence
    measurement is the only thing that can refuse."""
    v, _, _root = worlds["W25 INSUFFICIENT a which assembled from two loads (freeze F-2)"]
    assert v["verdict"] == "INSUFFICIENT_DATA"
    hits = [x for x in v["referents"]["failures"] if "did not come from one load" in x]
    assert hits and "stage2_final" in hits[0], v["referents"]["failures"]
    assert not any("endpoint_file_sha256" in x for x in v["referents"]["failures"])
    assert not any("endpoint_sha256" in x for x in v["referents"]["failures"])


def test_s8_production_loader_once(tmp_path):
    """The production S8 path (no injection) on one world: the five
    committed outcomes through their own frozen readers (≈ 3–5 min)."""
    seal = fs.write_world_2n(tmp_path, mode="shared")
    frozen_check = None if bn.FROZEN_SHA256_2N else (lambda: None)
    imports_pinned = True if an.IMPORTED_SHA256_2N is not None else False
    v = an.run(root_2n=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, n_perm=30, n_boot=10,
               referents_sha=False, frozen_check=frozen_check, imports_pinned=imports_pinned, **seal)
    s8 = v["secondaries"]["S8 outcome order"]
    assert set(s8) == {"pythia_2.8b", "pythia_6.9b", "olmo2_7b", "olmo2_13b", "smollm3_3b"}
    assert s8["pythia_2.8b"]["rungs"] == [r for r in fs.RUNGS_PRIMARY if r in bn.bg.R_28]
    assert "failed" not in s8["olmo2_13b"]


def test_refusal_reasons(worlds):
    f = lambda n: worlds[n][0]["referents"]["failures"]
    assert any("2n endpoint stage1_final" in x for x in f("W7 INSUFFICIENT missing endpoint record"))
    assert any("2n endpoint seal binding" in x for x in f("W8 INSUFFICIENT drifted endpoint seal"))
    assert any("halted" in x for x in f("W9 INSUFFICIENT halted"))
    assert any("re-derive" in x for x in f("W10 INSUFFICIENT gate-1 diff (real bytes, attestation blind, no marker)"))
    assert any("attested bit_diffs" in x for x in f("W11 INSUFFICIENT gate-1 attested mismatch"))
    assert any("2n sweep comma_7b" in x for x in f("W12 INSUFFICIENT missing sweep record"))
    assert any("checkpoint record missing" in x for x in f("W13 INSUFFICIENT missing twin checkpoint record"))
    assert any("2n power record" in x for x in f("W14 INSUFFICIENT missing power"))
    assert any("predictor_sha256" in x for x in f("W15 INSUFFICIENT power sha"))
    assert any("2n power claims" in x for x in f("W16 INSUFFICIENT power claims"))
    assert any("endpoint_sha256" in x for x in f("W17 INSUFFICIENT endpoint file edited after the sweep stamped its sha"))
    assert any("2n endpoint main" in x for x in f("W20 INSUFFICIENT missing main record"))
    assert any("2n sweep comma_7b" in x and "twin" in x for x in f("W21 INSUFFICIENT missing twin record"))
    assert any("dtype" in x for x in f("W22 INSUFFICIENT a record at another precision"))
    for n in ("W7 INSUFFICIENT missing endpoint record", "W22 INSUFFICIENT a record at another precision"):
        v = worlds[n][0]
        assert v["tests"] is None and v["secondaries"] is None


def test_annotation_c_cells_across_the_worlds(worlds):
    v1, _, _ = worlds["W1 PYTHIA-ONLY"]
    v2, _, _ = worlds["W2 OLMO-ONLY"]
    v4, _, _ = worlds["W4 NEITHER independent"]
    assert v1["annotation"]["C"]["reading"] == "A-LEADS" and v1["annotation"]["C"]["delta"] < 0
    assert v2["annotation"]["C"]["reading"] == "B-LEADS" and v2["annotation"]["C"]["delta"] > 0
    assert v4["annotation"]["C"]["reading"] in ("NO-LEAD", "A-LEADS", "B-LEADS")
    for v in (v1, v2, v4):
        c = v["annotation"]["C"]
        # Test-side correction: `c["increment_3b"]` is the RAW value read
        # from 2m's committed verdict.json (unrounded); an.INCREMENT_3B_2N
        # is the literal rounded to 4 dp (same rounding `run()` itself
        # applies when checking it, and the same style the last assertion
        # in this loop already uses two lines down).
        assert round(c["increment_3b"], 4) == an.INCREMENT_3B_2N and isinstance(c["covers_3b_increment"], bool)
        assert set(c["k_by_rung"]) == set(c["rungs"]) and all(1 <= k <= 64 for k in c["k_by_rung"].values())
        assert f"C: {c['reading']}" in v["reason"] and v["secondaries"]["C corpus annotation"] == c
        assert an.C_MODIFIERS_2N[an._c_modifier_key_2n(c)] in v["licensed_sentence"]
        assert v["referents"]["render"] == "bos" and v["referents"]["eos_stop_id"] == 3
        assert round(v["referents"]["increment_3b"], 4) == 0.0659


def test_s8_five_rows_s8c_and_s9(worlds):
    v, _, _ = worlds["W1 PYTHIA-ONLY"]
    s8 = v["secondaries"]["S8 outcome order"]
    assert set(s8) == {"pythia_2.8b", "pythia_6.9b", "olmo2_7b", "olmo2_13b", "smollm3_3b"}
    assert s8["smollm3_3b"]["rungs"] == list(fs.RUNGS_PRIMARY)
    s8c = v["secondaries"]["S8c corpus contrast"]
    assert s8c["pile_rows"] == ["pythia_2.8b", "pythia_6.9b"] and len(s8c["dclm_rows"]) == 3 and s8c["ci95"] is not None
    s9 = v["secondaries"]["S9 sign ledger"]
    assert set(s9["rows"]) == {"antonym", "antonym6", "odd6"}
    assert round(s9["rows"]["antonym"]["olmo2_13b_2l"]["B"], 3) == 0.256
    sens = v["secondaries"]["sensitivities"]
    assert sens["every40k_subset"]["control"] is True and sens["every40k_subset"]["steps"] == list(bn.EVERY40K_SUBSET_2N)
    assert sens["every40k_subset"]["A"]["stratified"]["T"] != v["tests"]["A"]["stratified"]["T"]


def test_w26_w27_render_and_stop_id_refusals(worlds):
    assert worlds["W26 INSUFFICIENT a record at another render"][0]["verdict"] == "INSUFFICIENT_DATA"
    assert any("render" in x for x in worlds["W26 INSUFFICIENT a record at another render"][0]["referents"]["failures"])
    assert worlds["W27 INSUFFICIENT a checkpoint record without the stop-id override"][0]["verdict"] == "INSUFFICIENT_DATA"
    assert any("generation_eos_token_id" in x for x in worlds["W27 INSUFFICIENT a checkpoint record without the stop-id override"][0]["referents"]["failures"])
