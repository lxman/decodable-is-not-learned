"""Every §6 terminal, end to end on synthetic 2f worlds through the
frozen loaders and the production pin path."""
import pytest

from experiments.exp2f import analyze_2f as a
from experiments.exp2f import labels_2f as lb
from experiments.exp2f.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kwargs, want in fs.world_specs():
        tmp = tmp_path_factory.mktemp(name.split()[0])
        out[name] = (fs.build_world(tmp, **kwargs), want)
    return out


def test_every_terminal_reached(worlds):
    got = {}
    for name, (v, want) in worlds.items():
        assert v["verdict"] == want, f"{name}: got {v['verdict']!r}, want " \
                                     f"{want!r}\nreason: {v.get('reason')}"
        got.setdefault(v["verdict"], name)
    assert set(got) == set(a.WORLDS)


def test_w1_ladder_shape(worlds):
    v, _ = worlds["W1 LADDER probe+sampler+argmax on arith_next"]
    c = v["cells"]["arith_next/1b"]
    assert c["D"] == [True, True, True] and c["monotone"] and not c["void"]
    assert c["probe"]["trained"]["best_site"] == [3, 1]
    assert c["sampling"]["main"]["D"] and c["sampling"]["main"]["n"] == 32_000
    assert c["sampling"]["main"]["exact"] == 300
    assert c["sampling"]["main"]["match"] == 6300
    assert c["argmax"]["D"] and c["argmax"]["exact"] == 20 and c["argmax"]["n"] == 500
    s = v["cells"]["sub3_mid/410m"]
    assert s["D"] == [False, False, False] and s["monotone"]
    assert v["n_void"] == 0 and v["n_violations"] == 0 and v["n_detections"] > 0
    assert v["known_inputs_caveat"] == a.KNOWN_INPUTS_CAVEAT_2F
    ref = v["referents"]
    assert ref["failures"] == [] and ref["manifest"]["n_files"] == 34
    assert ref["exact_match_gate"].startswith("PASS") and \
        ref["m3_gate"].startswith("PASS") and ref["continuity_gate"].startswith("PASS")
    assert ref["probe_label_gates"]["sub3_mid/mid_digit"].startswith("PASS")
    sec = v["secondaries"]
    assert sec["arith_next_mod7"]["cells"]["arith_next/1b"]["D"][1] is not None
    assert "pilot" in c["sampling"] and c["sampling"]["pilot"]["n"] == 4_000
    assert sec["alpha_05"]["cells"]["arith_next/1b"]["D"][0] is True
    assert "cv_probe" in c["probe"] and c["probe"]["cv_probe"]["split"]["n_val"] > 0
    assert v["floors"]["arith_next/last_digit"]["floor"] >= 0.1
    assert v["licensed_sentence"] and "ladder" in v["licensed_sentence"].lower()


def test_w2_inverted_names_the_cells(worlds):
    v, _ = worlds["W2 INVERTED sampler without probe"]
    assert set(v["violations"]) >= {"arith_next/410m", "arith_next/1b"}
    assert v["cells"]["arith_next/1b"]["D"] == [False, True, True]
    assert "reversal" in v["licensed_sentence"]


def test_w6_argmax_without_sampler_is_inverted(worlds):
    v, _ = worlds["W6 INVERTED argmax without sampler"]
    c = v["cells"]["arith_next/1b"]
    assert c["D"] == [True, False, True] and not c["monotone"]


def test_w7_probe_only_is_ladder(worlds):
    v, _ = worlds["W7 LADDER probe only"]
    assert v["cells"]["arith_next/1b"]["D"] == [True, False, False]
    assert v["n_detections"] == 2


def test_refusal_worlds(worlds):
    v4, _ = worlds["W4 INSUFFICIENT_DATA manifest byte changed"]
    assert any("manifest" in f for f in v4["referents"]["failures"])
    v5, _ = worlds["W5 INSUFFICIENT_DATA both arith_next cells void"]
    assert v5["n_void"] == 2 and "void" in v5["reason"]
    v8, _ = worlds["W8 INSUFFICIENT_DATA continuity gate"]
    assert any("continuity" in f for f in v8["referents"]["failures"])
    v9, _ = worlds["W9 INSUFFICIENT_DATA exact-match pin"]
    assert any("exact-match" in f for f in v9["referents"]["failures"])
    for v in (v4, v5, v8, v9):
        assert v["verdict"] == "INSUFFICIENT_DATA" and v["cells"] is None or \
            v["verdict"] == "INSUFFICIENT_DATA"
