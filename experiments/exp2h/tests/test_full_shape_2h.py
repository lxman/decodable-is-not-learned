# experiments/exp2h/tests/test_full_shape_2h.py
"""Every 2h terminal, end to end on synthetic 6.9b sweeps (real x,
synthetic outcome) through the production loaders and the prereg-tag
path."""
import pytest

from experiments.exp2h import analyze_2h as an
from experiments.exp2h.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kw, run_kw, want in fs.world_specs():
        root = tmp_path_factory.mktemp(name.split()[0])
        seal = fs.write_world(root, **kw)
        out[name] = (fs.run_world(root, seal, **run_kw), want)
    return out


def test_every_terminal_reached(worlds):
    got = {}
    for name, (v, want) in worlds.items():
        assert v["verdict"] == want, f"{name}: {v['verdict']} ({v['reason']})"
        got.setdefault(v["verdict"], name)
    assert set(got) == set(an.WORLDS)


def test_w1_shape(worlds):
    v, _ = worlds["W1 CONFIRMED"]
    p = v["primary"]
    assert set(p["eligible"]) == set(bh_r69_eligible())
    assert p["thin"] == ["add3_mid"]           # under the eligibility floor (design §4)
    assert p["stratified"]["T"] >= 0.10 and p["stratified"]["p"] < 0.01
    assert "twin" not in p
    assert v["rung_level"]["antonym"]["final_clears"] is True
    assert v["secondaries"]["probe_competitor"]["tree"]["verdict"] in an.WORLDS
    assert v["secondaries"]["replication_410m"]["tree"]["verdict"] in an.WORLDS
    assert v["secondaries"]["probe_beyond_sampler"]["eligible"]
    assert v["secondaries"]["sampler_beyond_probe"]["eligible"]
    assert v["secondaries"]["first_correct_outcome"]["note"]
    assert v["secondaries"]["beyond_410m_1b"]["eligible"]
    assert set(v["secondaries"]["rung_level"]["table"]) == set(bh_r69())
    assert v["secondaries"]["flat_rungs"]
    assert v["secondaries"]["step0_counts"]
    assert v["referents"]["gate1"]["pass"] is True
    assert v["referents"]["power"] is None          # power_sha=None in worlds
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2H


def test_w3_inverted_named(worlds):
    v, _ = worlds["W3 NOT-CONFIRMED inverted"]
    assert "inverted" in v["reason"]


def test_w4_w5_w6_reasons(worlds):
    assert "step40000" in worlds["W4 INSUFFICIENT missing step"][0]["reason"]
    assert "halted" in worlds["W5 INSUFFICIENT halted"][0]["reason"]
    assert "checkpoint manifest" in worlds["W6 INSUFFICIENT wrong manifest sha"][0]["reason"]


def test_w7_w8_pinned_artifact_refusals(worlds):
    """Attack-list item 12: the referents-manifest and power-record
    refusal routes, end to end through run() on a full-shape tree."""
    v7 = worlds["W7 INSUFFICIENT wrong referents sha"][0]
    assert "referent manifest" in v7["reason"] and "referents_2h.json" in v7["reason"]
    v8 = worlds["W8 INSUFFICIENT wrong power sha"][0]
    assert "power record" in v8["reason"] and "power_2h.json" in v8["reason"]


def test_w9_real_pins_pass(worlds):
    """The other half of item 12: with 2h's REAL referents and power
    pins in force, the same tree reaches CONFIRMED and the power
    record's declaration rides on the verdict."""
    v = worlds["W9 CONFIRMED through the real referents + power pins"][0]
    assert v["referents"]["power"]["declared_status"] == "POWERED"
    assert v["referents"]["power"]["sha256"] == an.POWER_2H_SHA256
    assert v["primary"]["stratified"]["T"] >= 0.10


def bh_r69():
    from experiments.exp2h import battery_2h as bh
    return bh.R_69


def bh_r69_eligible():
    from experiments.exp2h import battery_2h as bh
    return tuple(r for r in bh.R_69 if r != "add3_mid")
