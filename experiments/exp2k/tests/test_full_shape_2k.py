# experiments/exp2k/tests/test_full_shape_2k.py
import pytest

from experiments.exp2k import analyze_2k as an
from experiments.exp2k import battery_2k as bk
from experiments.exp2k.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kw, want, ann in fs.world_specs():
        root = tmp_path_factory.mktemp(name.split()[0])
        seal = fs.write_world_2k(root, **kw)
        out[name] = (fs.run_world(root, seal), want, ann)
    return out


def test_every_terminal_and_annotation_reached(worlds):
    got = {}
    for name, (v, want, ann) in worlds.items():
        assert v["verdict"] == want, f"{name}: {v['verdict']} ({v['reason']})"
        if ann is not None:
            assert v["annotation"] == ann, f"{name}: {v['annotation']} ({v['reason']})"
        got.setdefault(v["verdict"], name)
    assert set(got) == set(an.WORLDS_2K)


def test_w1_density_shape(worlds):
    v, _, _ = worlds["W1 DENSITY"]
    p = v["primary"]
    assert p["fires"] is True and p["stratified"]["T"] >= 0.10
    assert v["referents"]["comparison"]["gate"] == "PASS"
    for s in bk.SIZES_2K:
        for r in bk.R_CAP_DESIGN:
            assert v["referents"]["gate1_2k"][s][r]["n_diffs"] == 0
            assert v["referents"]["gate1_2k"][s][r]["draws_compared"] == 32000
    sec = v["secondaries"]
    s1, s2 = sec["S1 block replication 1b"], sec["S2 nested ladder 1b"]
    assert s1["per_seed"]["0"]["stratified"]["T"] == v["referents"]["comparison"]["A64"]
    assert s2[64]["stratified"]["T"] == v["referents"]["comparison"]["A64"]
    assert s2[256]["stratified"]["T"] == p["stratified"]["T"]
    assert s1["sd"] is not None and len(s1["T"]) == 4
    s3 = sec["S3 matched density 1b"]
    assert set(s3["per_rung"]) == set(bk.R_CAP_DESIGN) and s3["T_A256"] == p["stratified"]["T"]
    assert "k_equivalent" in s3["placement"]
    assert set(sec["S4 partials 1b"]) == {"cross_beyond_within_256", "within_beyond_cross_256"}
    assert sec["S5 within lineage 1b"]["rungs_2.8b"] and sec["S5 within lineage 1b"]["rungs_6.9b"]
    assert sec["S6 410m replicate"]["primary_form"]["stratified"]["T"] is not None
    assert sec["S7 texture 1b"]["six_rung_mean_D"] is not None
    assert v["licensed_sentence"] == an.LICENSED_2K["DENSITY"]
    assert v["known_inputs_caveat"] in v["licensed_sentence"]
    assert sec["failures"] == []


def test_w2_null_and_w4_underpowered_licences(worlds):
    v, _, _ = worlds["W2 NOT-DENSITY null"]
    assert v["licensed_sentence"] == an.LICENSED_2K["NOT-DENSITY"]
    v, _, _ = worlds["W4 NOT-DENSITY underpowered"]
    assert v["declared_status"] == "DECLARED UNDERPOWERED IN ADVANCE"
    assert v["licensed_sentence"] == an.LICENSED_2K["NOT-DENSITY_UNDERPOWERED"]


def test_w3_structured_lands_under_the_bar_with_p_below_alpha(worlds):
    v, _, _ = worlds["W3 NOT-DENSITY structured"]
    p = v["primary"]["stratified"]
    assert p["p"] < 0.01 and 0.0 < p["T"] < 0.10, p


def test_refusal_reasons(worlds):
    f = lambda n: worlds[n][0]["referents"]["failures"]
    assert any("record or draws file missing" in x for x in f("W5 INSUFFICIENT missing tier record"))
    assert any("rows read" in x for x in f("W6 INSUFFICIENT truncated draws"))
    assert any("HALTED" in x for x in f("W7 INSUFFICIENT halted"))
    assert any("gate 1" in x and "differ" in x for x in f("W8 INSUFFICIENT gate-1 diff"))
    assert any("2k seal: counts" in x for x in f("W9 INSUFFICIENT seal counts"))
    assert any(x.startswith("comparison gate 2k A") for x in f("W10 INSUFFICIENT wrong pin"))
    assert any("power" in x for x in f("W11 INSUFFICIENT missing power"))
    assert any("model_sha" in x for x in f("W12 INSUFFICIENT model sha"))
    assert any("predictor_sha256" in x for x in f("W13 INSUFFICIENT power sha"))
    for n in ("W5 INSUFFICIENT missing tier record", "W8 INSUFFICIENT gate-1 diff"):
        v = worlds[n][0]
        assert v["primary"] is None and v["secondaries"] is None
