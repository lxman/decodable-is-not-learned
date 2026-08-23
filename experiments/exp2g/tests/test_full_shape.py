# experiments/exp2g/tests/test_full_shape.py
"""Every §6.3 terminal, end to end on synthetic 2g trees through the
production loaders and the seal path."""
import pytest

from experiments.exp2g import analyze_2g as an
from experiments.exp2g.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kw, want in fs.world_specs():
        root = tmp_path_factory.mktemp(name.split()[0])
        seal = fs.write_world(root, **kw)
        out[name] = (fs.run_world(root, seal), want)
    return out


def test_every_terminal_reached(worlds):
    got = {}
    for name, (v, want) in worlds.items():
        assert v["verdict"] == want, f"{name}: {v['verdict']} ({v['reason']})"
        got.setdefault(v["verdict"], name)
    assert set(got) == set(an.WORLDS)


def test_w1_shape(worlds):
    v, _ = worlds["W1 FORECAST"]
    p = v["primary"]
    assert p["eligible"] == list(an.bg.R_28) and p["thin"] == []
    assert p["stratified"]["T"] >= 0.10 and p["stratified"]["p"] < 0.01
    assert p["twin"]["p"] >= 0.05
    assert v["rung_level"]["antonym"]["final_clears"] is True
    assert v["secondaries"]["replication_410m"]["tree"]["verdict"] == "FORECAST"
    assert v["secondaries"]["replication_12b"]["failures"]       # no 12b tree in W1
    assert v["referents"]["gate1"]["pass"] is True
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2G


def test_w5_inverted_named(worlds):
    v, _ = worlds["W5 inverted -> NO-FORECAST"]
    assert "inverted" in v["reason"]


def test_w6_w7_w8_reasons(worlds):
    assert "step40000" in worlds["W6 INSUFFICIENT missing step"][0]["reason"]
    assert "halted" in worlds["W7 INSUFFICIENT halted"][0]["reason"]
    assert "seal" in worlds["W8 INSUFFICIENT seal mismatch"][0]["reason"]


def test_w9_replication(worlds):
    v, _ = worlds["W9 FORECAST with 12b replication"]
    rep = v["secondaries"]["replication_12b"]
    assert rep["failures"] == [] and rep["tree"]["verdict"] == "FORECAST"
    assert rep["primary"]["thin"] == ["sub4_mid"]
