# experiments/exp2j/tests/test_full_shape_2j.py
import pytest

from experiments.exp2j import analyze_2j as an
from experiments.exp2j import functionals_2j as fn
from experiments.exp2j.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kw, want in fs.world_specs():
        root = tmp_path_factory.mktemp(name.split()[0])
        seal = fs.write_world_2j(root, **kw)
        out[name] = (fs.run_world(root, seal), want)
    return out


def test_every_terminal_reached(worlds):
    got = {}
    for name, (v, want) in worlds.items():
        assert v["verdict"] == want, f"{name}: {v['verdict']} ({v['reason']})"
        got.setdefault(v["verdict"], name)
    assert set(got) == set(an.WORLDS_2J)


def test_w1_residual_shape(worlds):
    v, _ = worlds["W1 RESIDUAL"]
    p = v["primary"]
    assert p["fires"] is True and p["stratified"]["T"] >= 0.10
    assert set(p["composite_report"]) == set(v["referents"]["rung_set"]["R_CAP"])
    for r, rep in p["composite_report"].items():
        assert set(rep) == set(fn.FUNCTIONALS)
    assert v["referents"]["comparison"]["gate"] == "PASS"
    assert v["primary"]["block_gate_T64"] == v["referents"]["comparison"]["2i"]["within_alone"]
    s = v["secondaries"]
    d = s["decomposition x_B to olmo7b"]
    assert d["within_alone"]["stratified"]["T"] == v["referents"]["comparison"]["2i"]["within_alone"]
    assert d["beyond_all"]["stratified"]["T"] == p["stratified"]["T"]
    assert v["a1"]["reading"] in an.A1_READINGS
    for lab in ("olmo7b", "2.8b", "6.9b"):
        assert v["a1"]["outcomes"][lab]["ladder"]["64"]["B"]["n_blocks"] == 1
    assert v["licensed_sentence"] == an.LICENSED_2J["RESIDUAL"]
    assert v["known_inputs_caveat"] in v["licensed_sentence"]


def test_w2_absorbed_by_habit_names_pi(worlds):
    v, _ = worlds["W2 ABSORBED habit"]
    d = v["secondaries"]["decomposition x_B to olmo7b"]
    assert d["within_alone"]["fires"] is True          # the forecast exists
    assert v["primary"]["fires"] is False               # and π absorbs it
    assert d["beyond_single"]["pi"]["fires"] is False
    assert d["alone"]["pi"]["fires"] is True
    assert d["fraction_absorbed"] > 0.5
    assert v["licensed_sentence"] == an.LICENSED_2J["ABSORBED"]


def test_w4_underpowered_changes_the_licence(worlds):
    v, _ = worlds["W4 ABSORBED underpowered"]
    assert v["declared_status"] == "DECLARED UNDERPOWERED IN ADVANCE"
    assert v["licensed_sentence"] == an.LICENSED_2J["ABSORBED_UNDERPOWERED"]


def test_refusal_reasons(worlds):
    f = lambda n: worlds[n][0]["referents"]["failures"]
    assert any("x_B" in x or "draws" in x for x in f("W5 INSUFFICIENT missing x_B draws"))
    assert any("power" in x for x in f("W6 INSUFFICIENT missing power"))
    assert any("comparison" in x for x in f("W7 INSUFFICIENT missing 2i verdict"))
    assert any(x.startswith("comparison gate 2i") for x in f("W8 INSUFFICIENT comparison pin mismatch"))
    assert any("HALTED" in x for x in f("W9 INSUFFICIENT halted"))
    for n in ("W5 INSUFFICIENT missing x_B draws", "W8 INSUFFICIENT comparison pin mismatch"):
        v = worlds[n][0]
        assert v["primary"] is None and v["secondaries"] is None and v["a1"] is None
