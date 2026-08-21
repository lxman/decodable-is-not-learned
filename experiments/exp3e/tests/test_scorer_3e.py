"""Fixtures for the target-swapped scorer (design §5.5) and its two
known-answer gates over synthetic committed trees."""
import json

import pytest

from experiments.exp3 import analyze_3 as a3
from experiments.exp3c import analyze_3c as c
from experiments.exp3d import analyze_3d as d
from experiments.exp3e import analyze_3e as e
from experiments.exp3e import scorer_3e as sc
from experiments.exp3e import scorer_gates_3e as sg
from experiments.exp3e.tests import full_shape as fs


def test_scorer_is_3c_verify_with_the_target_as_parameter():
    score = sc.load_scorer()
    v = c.load_verify_3c()
    for draw, tgt in ((" ecde\n\nQ: next", "ecde"), (" Ecde.", "ecde"),
                      (" edec", "ecde"), (" ecdex", "ecde"), ("", "ecde")):
        assert score(draw, tgt, "word") == v(draw, tgt, "word")
    assert score(" edec\n", "edec", "word") is True
    assert score(" edec\n", "ecde", "word") is False


def test_scorer_is_total_on_the_3c_crasher_shape():
    score = sc.load_scorer()
    # punctuation-wrapped interior non-space whitespace: normalize's
    # split()[0] raises IndexError (3c stop #1's class); the wrapper
    # scores the DRAW False, never raises
    assert score(".\t.", "ecde", "word") is False
    assert score("'\x0b'", "ecde", "word") is False
    assert score('"\r"', "ecde", "word") is False
    with pytest.raises(IndexError):
        score(" ecde", ".\t.", "word")    # answer-side crash stays hard


def test_is_void_casefolds():
    assert sc.is_void("ecde", "Spell the string 'ECDE' backwards")
    assert not sc.is_void("ecde", "Spell the string 'edce' backwards")


def test_emissions_counts_addresses_and_void():
    rows = {7: {"0": [" ecde", " edec", " ~z"], "1": [" edec", " ecde", " ecde"]}}
    em = sc.emissions(rows, {7: ["ecde", "edec", "eecd"]}, "word",
                      sc.load_scorer(), prompts={7: "hint edec here"})
    assert em[7]["ecde"]["count"] == 3 and not em[7]["ecde"]["void"]
    assert [(a["seed"], a["draw"]) for a in em[7]["ecde"]["addresses"]] == \
        [(0, 0), (1, 1), (1, 2)]
    assert em[7]["edec"]["void"] is True
    assert em[7]["edec"]["raw_count"] == 2 and em[7]["edec"]["count"] == 0
    assert em[7]["eecd"]["count"] == 0 and em[7]["eecd"]["addresses"] == []


def _base(tmp):
    e3 = fs.write_exp3_tree(tmp / "exp3")
    c3 = fs.write_3c_tree(tmp / "exp3c")
    d3 = fs.write_3d_tree(tmp / "exp3d")
    pins = {
        "reverse_string": {
            size: {"exp3": e3[("reverse_string", size, "trained")],
                   "3c": c3[("reverse_string", size, "trained")],
                   "3d": {d.shard_name(b): d3[(size, b)]
                          for b in d.SEED_BLOCKS[size]}}
            for size in e.SIZES_3E},
        "ctrl_copy": {size: e3[(a3.POSITIVE_CONTROL, size, "trained")]
                      for size in e.SIZES_3E}}
    rows = e.load_committed_rows(
        roots={"exp3": tmp / "exp3", "3c": tmp / "exp3c",
               "3d": tmp / "exp3d"}, n_items=fs.N, draws_pins=pins)
    _l, answers = fs.rung_items("reverse_string")
    return e.committed_base_3e(
        rows, answers, "word", sc.load_scorer(),
        fires_pin=fs.SYN_COMMITTED_FIRES, subset=fs.SUBSET,
        ctrl_answers=fs.rung_items(a3.POSITIVE_CONTROL)[1])


def test_scorer_gate_record_passes_on_the_committed_referents(tmp_path):
    base = _base(tmp_path)
    rec = sg.scorer_gate_record(base, fires_pin=fs.syn_repeat_class_fires(),
                                ctrl_pin=fs.SYN_CTRL_RATE,
                                meta={"items_sha256": "x"})
    assert rec["passed"] is True
    assert rec["gate_a"]["passed"] and rec["gate_b"]["passed"]
    assert rec["gate_a"]["addresses"]["1b"] == \
        fs.syn_repeat_class_fires()["1b"]
    assert rec["gate_b"]["counts"]["410m"] == fs.SYN_CTRL_RATE["410m"]
    out = sg.write_record(rec, tmp_path / "exp3e")
    assert out == tmp_path / "exp3e" / "results" / "scorer_gates.json"
    loaded = e.load_scorer_gates_3e(tmp_path / "exp3e",
                                    fires_pin=fs.syn_repeat_class_fires(),
                                    ctrl_pin=fs.SYN_CTRL_RATE)
    assert loaded["passed"] is True


def test_scorer_gate_record_fails_closed_and_is_still_written(tmp_path):
    base = _base(tmp_path)
    bad_fires = {s: v[:-1] for s, v in fs.syn_repeat_class_fires().items()}
    rec = sg.scorer_gate_record(base, fires_pin=bad_fires,
                                ctrl_pin=fs.SYN_CTRL_RATE, meta={})
    assert rec["passed"] is False and rec["gate_a"]["passed"] is False
    assert rec["gate_b"]["passed"] is True
    sg.write_record(rec, tmp_path / "exp3e")
    written = json.loads(
        (tmp_path / "exp3e/results/scorer_gates.json").read_text())
    assert written["passed"] is False
    bad_ctrl = {s: {"count": v["count"] - 1, "n_draws": v["n_draws"]}
                for s, v in fs.SYN_CTRL_RATE.items()}
    rec2 = sg.scorer_gate_record(base, fires_pin=fs.syn_repeat_class_fires(),
                                 ctrl_pin=bad_ctrl, meta={})
    assert rec2["gate_b"]["passed"] is False and rec2["passed"] is False
