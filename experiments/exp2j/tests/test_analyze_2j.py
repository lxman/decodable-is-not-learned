# experiments/exp2j/tests/test_analyze_2j.py
"""analyze_2j: the tree on literal inputs, the pin extractors and the
three-way comparison gate, t_only vs _run_test on a toy, the
decomposition's shape, require_prereg_2j, FROZEN_SHA256_2J vs disk,
prefix-disjoint failure labels, run() on an empty 2i root."""
from __future__ import annotations

import ast
import json
import re

import numpy as np
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp2g import stats_2g as st
from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2j import analyze_2j as an
from experiments.exp2j import functionals_2j as fn


def _prim(T, p, fires):
    return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}, "fires": fires,
            "named_inside": None}


def _power(status):
    return {"declared_status": status, "declaration": "x", "rungs": list(bi.STRATA_RUNGS),
            "n_trained_steps": 21}


def test_tree_worlds_and_declaration():
    assert an.verdict_tree_2j(["x"], None, None)["verdict"] == "INSUFFICIENT_DATA"
    v = an.verdict_tree_2j([], _prim(0.15, 0.001, True), _power("POWERED"))
    assert v["verdict"] == "RESIDUAL"
    v = an.verdict_tree_2j([], _prim(0.05, 0.001, False), _power("POWERED"))
    assert v["verdict"] == "ABSORBED" and v["declared_status"] == "POWERED"
    v = an.verdict_tree_2j([], _prim(0.05, 0.3, False),
                           _power("DECLARED UNDERPOWERED IN ADVANCE"))
    assert v["verdict"] == "ABSORBED"
    assert "not detected at this resolution" in an.LICENSED_2J["ABSORBED_UNDERPOWERED"]
    assert set(an.WORLDS_2J) == {"INSUFFICIENT_DATA", "RESIDUAL", "ABSORBED"}


def test_licensed_sentences_carry_the_disclosure():
    for k, s in an.LICENSED_2J.items():
        assert an.KNOWN_INPUTS_CAVEAT_2J in s, k


def test_pins_extract_from_the_committed_records():
    v2i = json.loads((bi.EXP2I / "results" / "verdict.json").read_text())
    assert an.pin_from_record_2i(v2i) == an.VERDICT_2I_PIN
    v2g = json.loads((bg.EXP2G / "results" / "verdict.json").read_text())
    assert an.pin_from_record_2g(v2g) == an.VERDICT_2G_PIN
    from experiments.exp2h import battery_2h as bh
    v2h = json.loads((bh.EXP2H / "results" / "verdict.json").read_text())
    assert an.pin_from_record_2h(v2h) == an.VERDICT_2H_PIN


def test_check_pin_three_way_exact():
    lit = {"B": 0.5, "A": 0.25}
    assert an.check_pin(dict(lit), dict(lit), lit, "2i comparison") == []
    bad = an.check_pin({"B": 0.5, "A": 0.25000001}, dict(lit), lit, "2i comparison")
    assert bad and bad[0].startswith("2i comparison") and "A" in bad[0]
    bad = an.check_pin(dict(lit), {"B": 0.5, "A": 0.3}, lit, "2i comparison")
    assert any("verdict.json" in b for b in bad)


def _toy_cells(seed=0):
    rng = np.random.default_rng(seed)
    n = 60
    x = {"r1": [int(v) for v in rng.integers(0, 10, n)],
         "r2": [int(v) for v in rng.integers(0, 10, n)]}
    out = {r: {"y": [int(v) for v in rng.integers(0, 21, n)], "n_pos": n} for r in x}
    strata = {r: {"strata": [str(i % 3) for i in range(n)]} for r in x}
    return x, out, strata


def test_t_only_equals_run_test_T_exactly():
    x, out, strata = _toy_cells()
    full = an2i._run_test(x, "olmo1b", out, strata, ("r1", "r2"), n_perm=20, n_boot=5)
    t = an.t_only(x, "olmo1b", out, strata, ("r1", "r2"))
    assert t["T"] == full["stratified"]["T"]
    assert t["per_rung"] == {r: full["per_rung"][r]["d"] for r in ("r1", "r2")}


def test_t_only_undefined_on_degenerate_predictor():
    x, out, strata = _toy_cells()
    x = {r: [3] * 60 for r in x}
    t = an.t_only(x, "olmo1b", out, strata, ("r1", "r2"))
    assert t["T"] is None and sorted(t["dropped_degenerate"]) == ["r1", "r2"]


def test_decomposition_shape_on_a_toy():
    x, out, strata = _toy_cells()
    tables = {r: {"pi": list(np.random.default_rng(1).random(60)), "L": [2] * 30 + [3] * 30,
                  "R": [0, 1] * 30, "O": [1.0] * 60} for r in x}
    d = an.decomposition(x, "olmo1b", out, strata, tables, ("r1", "r2"), n_perm=20, n_boot=5)
    assert set(d) == {"within_alone", "beyond_all", "fraction_absorbed", "beyond_single",
                      "alone", "composite_report"}
    assert set(d["beyond_single"]) == set(fn.FUNCTIONALS)
    assert d["composite_report"]["r1"]["O"] == "dropped_constant"
    assert "O" not in d["alone"] or d["alone"]["O"] is None


def test_require_prereg_2j_refuses_missing_tag_and_drift():
    def blob_ok(tag, rel):
        p = bg.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None
    got = an.require_prereg_2j(tag_exists=lambda t: t == an.PREREG_TAG_2J, blob_sha=blob_ok)
    assert set(got["instrument_blobs"]) == set(an.INSTRUMENT_BLOBS_2J)
    with pytest.raises(RuntimeError, match="preregistration tag"):
        an.require_prereg_2j(tag_exists=lambda t: False, blob_sha=blob_ok)
    with pytest.raises(RuntimeError, match="does not bind"):
        an.require_prereg_2j(tag_exists=lambda t: True, blob_sha=lambda t, r: "0" * 64)


def test_frozen_pins_match_disk():
    an.check_frozen_2j()
    # Ruling (controller, task-2 brief addendum): +3, not +4 — power_2j.py
    # does not exist until Task 3, so `_pin_frozen_now()` only picks up
    # analyze_2i.py, battery_2i.py and make_referents_2j.py over 2i's own
    # FROZEN_SHA256. Task 4 tightens this to the literal dict + 4.
    assert len(an.FROZEN_SHA256_2J) >= len(bi.FROZEN_SHA256) + 3


def test_collect_total_labels_are_prefix_disjoint():
    src = (an.EXP2J / "analyze_2j.py").read_text()
    labels = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call):
            f = node.func
            name = f.id if isinstance(f, ast.Name) else getattr(f, "attr", None)
            if name == "collect_total" and len(node.args) >= 2 and \
                    isinstance(node.args[1], ast.Constant):
                labels.append(node.args[1].value)
    assert len(labels) >= 20
    for a in labels:
        for b in labels:
            assert a == b or not b.startswith(a), (a, b)


def test_run_on_an_empty_2i_root_is_insufficient_data(tmp_path):
    v = an.run(root_2i=tmp_path, root_2j=tmp_path, referents_sha=False, n_perm=10, n_boot=3,
               tag_exists=lambda t: True,
               blob_sha=lambda t, r: bg.sha256_file(bg.REPO / r) if (bg.REPO / r).is_file() else None,
               blobs_bound=lambda tag, paths, repo_root=None: [])
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["primary"] is None and v["secondaries"] is None
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2J


def test_run_refuses_when_the_manifest_is_not_pinned(tmp_path, monkeypatch):
    monkeypatch.setattr(an, "REFERENTS_2J_SHA256", None)
    v = an.run(root_2i=tmp_path, root_2j=tmp_path, n_perm=10, n_boot=3,
               tag_exists=lambda t: True, blob_sha=lambda t, r: None,
               blobs_bound=lambda tag, paths, repo_root=None: [])
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("not pinned" in f for f in v["referents"]["failures"])
