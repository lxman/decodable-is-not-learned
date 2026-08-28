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


def _prim(T, p, fires, eligible=("r1", "r2", "r3")):
    return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}, "fires": fires,
            "named_inside": None, "eligible": list(eligible)}


def _undefined_prim():
    """The shape `an2i._undefined_result_2i` actually returns (Ruling
    18: `_run_test` short-circuits before `primary_2i` when every
    eligible rung is degenerate inside the composite strata)."""
    return {"stratified": {"T": None, "p": 1.0, "n_perm": 0, "n_ge": 0}, "fires": False,
            "named_inside": ("undefined: every eligible rung degenerate (predictor "
                             "constant inside every stratum)"),
            "eligible": []}


def _power(status):
    return {"declared_status": status, "declaration": "x", "rungs": list(bi.STRATA_RUNGS),
            "n_trained_steps": 21}


def test_tree_worlds_and_declaration():
    assert an.verdict_tree_2j(["x"], None, None)["verdict"] == "INSUFFICIENT_DATA"
    v = an.verdict_tree_2j([], _prim(0.15, 0.001, True), _power("POWERED"))
    assert v["verdict"] == "RESIDUAL"
    v = an.verdict_tree_2j([], _prim(0.05, 0.001, False), _power("POWERED"))
    assert v["verdict"] == "ABSORBED" and v["declared_status"] == "POWERED"
    assert v["disclosures"] == []
    v = an.verdict_tree_2j([], _prim(0.05, 0.3, False),
                           _power("DECLARED UNDERPOWERED IN ADVANCE"))
    assert v["verdict"] == "ABSORBED"
    assert "not detected at this resolution" in an.LICENSED_2J["ABSORBED_UNDERPOWERED"]
    assert set(an.WORLDS_2J) == {"INSUFFICIENT_DATA", "RESIDUAL", "ABSORBED"}


def test_licensed_sentences_carry_the_disclosure():
    assert "ABSORBED_UNDEFINED" in an.LICENSED_2J
    for k, s in an.LICENSED_2J.items():
        assert an.KNOWN_INPUTS_CAVEAT_2J in s, k


def test_undefined_primary_absorbed_with_disclosure_not_full_licence():
    """fix round 1 / Finding 1 (i): an undefined primary (2i's Ruling
    18 shape) must not read as a positive ABSORBED result."""
    v = an.verdict_tree_2j([], _undefined_prim(), _power("POWERED"))
    assert v["verdict"] == "ABSORBED"
    assert v["disclosures"] == [an.DISCLOSURE_UNDEFINED_2J]
    assert "undefined" in v["reason"]
    lic = an._licensed(v)
    assert lic.startswith(an.LICENSED_2J["ABSORBED_UNDEFINED"])
    assert an.DISCLOSURE_UNDEFINED_2J in lic


def test_realized_thin_primary_absorbed_with_disclosure_regardless_of_power():
    """fix round 1 / Finding 1 (ii): a REALIZED eligible set under
    three rungs is THIN even when the power record (fixed before the
    composite strata existed) declared POWERED."""
    prim = _prim(0.05, 0.3, False, eligible=("a", "b"))
    v = an.verdict_tree_2j([], prim, _power("POWERED"))
    assert v["verdict"] == "ABSORBED"
    assert v["disclosures"] == [an.DISCLOSURE_THIN_2J]
    lic = an._licensed(v)
    assert lic.startswith(an.LICENSED_2J["ABSORBED_THIN"])
    assert an.DISCLOSURE_THIN_2J in lic


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


# ---------------------------------------------------- fix round 1 / Finding 2

def _a1_toy(seed=7, n=60, pa=0.15, pb=0.65):
    """Two rungs, 60 items, 64 synthetic bits per item, B markedly
    denser than A on both rungs (so `matched("B")` thins every rung and
    `matched("A")` never does — the clean case the two n_blocks_used
    assertions below are checking) and a three-level base stratum."""
    rng = np.random.default_rng(seed)
    rungs = ("r1", "r2")
    strata = {r: {"strata": [str(i % 3) for i in range(n)]} for r in rungs}
    bits_a, bits_b = {}, {}
    for r in rungs:
        bits_a[r] = [[int(v) for v in (rng.random(64) < pa)] for _ in range(n)]
        bits_b[r] = [[int(v) for v in (rng.random(64) < pb)] for _ in range(n)]
    out = {r: {"y": [int(v) for v in rng.integers(0, 21, n)], "n_pos": n} for r in rungs}
    return bits_a, bits_b, out, strata, rungs


def test_a1_density_per_rung_block_readings_and_gap():
    bits_a, bits_b, out, strata, rungs = _a1_toy()
    d = an.a1_density(bits_a, bits_b, {"toy": (out, rungs, 0.1, 0.3)}, strata)
    o = d["outcomes"]["toy"]
    assert set(o) == {"per_rung", "anchors", "thinned_B_matched", "thinned_A_matched",
                      "thinned_B_zero_fraction", "gap_fraction_closed", "ladder"}
    for key in ("thinned_B_matched", "thinned_A_matched", "thinned_B_zero_fraction"):
        assert set(o[key]) == {"T", "per_rung"}
        for r in rungs:
            assert set(o[key]["per_rung"][r]) == {"mean", "min", "max", "n_blocks_used"}

    # B is the denser predictor on both rungs at these synthetic rates
    # (asserted, not assumed, so a future rng/parameter change fails
    # loud rather than silently testing the wrong branch).
    for r in rungs:
        assert o["per_rung"][r]["denser"] == "B"

    # the bug this finding fixed: each rung gets ITS OWN block count,
    # not a shared min() across rungs — on the thinned side that's
    # `64 // k` (which differs rung to rung), on the untouched side
    # it's always 1 (the single full-64 "block").
    for r in rungs:
        k = o["per_rung"][r]["k"]
        assert o["thinned_B_matched"]["per_rung"][r]["n_blocks_used"] == 64 // k
        assert o["thinned_A_matched"]["per_rung"][r]["n_blocks_used"] == 1
        assert o["thinned_B_zero_fraction"]["per_rung"][r]["n_blocks_used"] == 1

    # gap_fraction_closed is computed from thinned_B_matched["T"] alone
    # (hand-checkable arithmetic against literal, non-data-derived
    # anchors — the anchors say nothing about what T actually is).
    mb_T = o["thinned_B_matched"]["T"]
    assert mb_T is not None
    assert o["gap_fraction_closed"] == pytest.approx((0.3 - mb_T) / (0.3 - 0.1))


def test_ladder_k64_matches_t_only_bit_for_bit():
    """design §5.4's k=64 sanity: the ladder's own per-rung machinery,
    at the coarsest block width, must reduce exactly to `t_only`'s
    joint per-rung d — not merely a close numerical match."""
    bits_a, bits_b, out, strata, rungs = _a1_toy()
    d = an.a1_density(bits_a, bits_b, {"toy": (out, rungs, 0.1, 0.3)}, strata)
    ladder64 = d["outcomes"]["toy"]["ladder"]["64"]
    assert ladder64["A"]["n_blocks"] == 1 and ladder64["B"]["n_blocks"] == 1

    x_b = {r: fn.counts_from_bits(bits_b[r]) for r in rungs}
    want_b = an.t_only(x_b, bi.SIZE_PRED, out, strata, rungs)
    assert ladder64["B"]["T"] == want_b["T"]
    for r in rungs:
        assert ladder64["B"]["per_rung"][r]["mean"] == want_b["per_rung"][r]

    x_a = {r: fn.counts_from_bits(bits_a[r]) for r in rungs}
    want_a = an.t_only(x_a, "A", out, strata, rungs)
    assert ladder64["A"]["T"] == want_a["T"]
    for r in rungs:
        assert ladder64["A"]["per_rung"][r]["mean"] == want_a["per_rung"][r]
