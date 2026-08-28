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

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2g import battery_2g as bg
from experiments.exp2g import predictor_2g as pr
from experiments.exp2g import stats_2g as st
from experiments.exp2g import strata_2g as sg
from experiments.exp2h import battery_2h as bh
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


def test_licensed_plain_absorbed_powered_is_the_absorbed_sentence():
    """No fast test previously called `_licensed` on a plain
    (no-disclosure) POWERED ABSORBED tree — closes a Step 4 mutation
    gap (`_licensed`'s POWERED branch swapped to ABSORBED_UNDERPOWERED)."""
    v = an.verdict_tree_2j([], _prim(0.05, 0.001, False), _power("POWERED"))
    assert v["verdict"] == "ABSORBED" and v["disclosures"] == []
    assert an._licensed(v) == an.LICENSED_2J["ABSORBED"]


def test_pins_extract_from_the_committed_records():
    v2i = json.loads((bi.EXP2I / "results" / "verdict.json").read_text())
    assert an.pin_from_record_2i(v2i) == an.VERDICT_2I_PIN
    v2g = json.loads((bg.EXP2G / "results" / "verdict.json").read_text())
    assert an.pin_from_record_2g(v2g) == an.VERDICT_2G_PIN
    v2h = json.loads((bh.EXP2H / "results" / "verdict.json").read_text())
    assert an.pin_from_record_2h(v2h) == an.VERDICT_2H_PIN


def test_check_pin_three_way_exact():
    lit = {"B": 0.5, "A": 0.25}
    assert an.check_pin(dict(lit), dict(lit), lit, "2i comparison") == []
    bad = an.check_pin({"B": 0.5, "A": 0.25000001}, dict(lit), lit, "2i comparison")
    assert bad and bad[0].startswith("2i comparison") and "A" in bad[0]
    bad = an.check_pin(dict(lit), {"B": 0.5, "A": 0.3}, lit, "2i comparison")
    assert any("verdict.json" in b for b in bad)


def test_check_pin_isolates_on_disk_vs_literal_drift():
    """check_pin's SECOND check (on_disk vs the literal) isolated from
    its first (rederived vs on_disk): rederived is built to match
    on_disk exactly, so only the second check can flag on_disk's own
    drift from the literal pin — the existing test above does not
    isolate this (its mismatched case's FIRST loop already emits a
    message containing 'verdict.json', so removing the second check
    entirely survived it — a Step 4 mutation gap)."""
    lit = {"B": 0.5}
    on_disk = {"B": 0.6}          # drifted from the literal
    rederived = {"B": 0.6}        # matches on_disk exactly -> first loop clean
    bad = an.check_pin(rederived, on_disk, lit, "iso")
    assert any("verdict.json" in b and "literal pin" in b for b in bad)


def test_load_power_2j_refuses_a_strict_superset_of_rungs(tmp_path):
    """rung EQUALITY, not a subset relation — a power record whose
    rungs are a strict superset of r_cap must be refused (a Step 4
    mutation gap: r_cap.issubset(prim_rungs) is still True when
    prim_rungs carries extra entries beyond r_cap)."""
    (tmp_path / "results").mkdir()
    rec = {"primary": {"declared_status": "POWERED", "rungs": ["a", "b", "extra"],
                       "n_trained_steps": len(bi.trained_steps_7b())}}
    (tmp_path / "results" / "power_2j.json").write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="power rungs"):
        an._load_power_2j(tmp_path, ("a", "b"))


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


def test_t_only_uses_mean_not_median_over_three_rungs():
    """The two 2-rung toys above cannot separate mean from median (with
    exactly two values they coincide); three rungs with distinct d's
    can. Values transcribed from this exact seed/data (a mean-vs-median
    mutation on t_only's final `np.mean` call is a Step 4 mutant)."""
    rng = np.random.default_rng(3)
    n = 60
    x = {f"r{i}": [int(v) for v in rng.integers(0, 10, n)] for i in range(3)}
    out = {r: {"y": [int(v) for v in rng.integers(0, 21, n)], "n_pos": n} for r in x}
    strata = {r: {"strata": [str(i % 3) for i in range(n)]} for r in x}
    t = an.t_only(x, "olmo1b", out, strata, tuple(x))
    vals = list(t["per_rung"].values())
    assert len(vals) == 3
    assert t["T"] == pytest.approx(float(np.mean(vals)))
    assert t["T"] != pytest.approx(float(np.median(vals)))


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


def test_rederive_2i_b_uses_the_zero_cut_not_the_median_bucket():
    """rederive_2i's 'B' test must stratify on `an2i._composite_strata`
    (the zero cut on x_a), not `_composite_strata_median`
    (`cross_beyond_within`'s construction) — worlds/full_shape cannot
    see this mutation (they derive their own embedded comparison pins
    with the SAME code under test, so a mutated rederive_2i is
    self-consistent there). x_a is built so the two cuts disagree: 20
    zeros + 1..40 gives a 20/40 zero-cut split vs a ~30/30 median split."""
    rng = np.random.default_rng(11)
    n, r = 60, "r"
    x_a = {r: [0] * 20 + list(range(1, 41))}
    x_b = {r: [int(v) for v in rng.integers(0, 64, n)]}
    out = {r: {"y": [int(v) for v in rng.integers(0, 21, n)], "n_pos": n}}
    strata = {r: {"strata": [str(i % 3) for i in range(n)]}}
    py = {"2.8b": out, "6.9b": out}
    kw = dict(n_perm=15, n_boot=5)
    red = an.rederive_2i(x_a, x_b, out, strata, (r,), py, **kw)
    zero_cut = an2i._run_test(x_b, bi.SIZE_PRED, out, an2i._composite_strata(strata, x_a, (r,)),
                              (r,), **kw)
    median_cut = an2i._run_test(x_b, bi.SIZE_PRED, out,
                                an2i._composite_strata_median(strata, x_a, (r,)), (r,), **kw)
    assert zero_cut["stratified"]["T"] != median_cut["stratified"]["T"]   # the toy is not vacuous
    assert red["B"]["stratified"]["T"] == zero_cut["stratified"]["T"]


def test_rederive_2g2h_primary_uses_r_69_not_r_28():
    """rederive_2g2h's 'primary' test must run `bh.R_69`'s rungs against
    py['6.9b'], not `bg.R_28`'s against it — closes a Step 4 mutation
    gap (both module-level rung tuples monkeypatched to disjoint,
    single-rung sets so the swap is unmissable: with the mutant, 'primary'
    would be built over r28, which is absent from py['6.9b'] and raises)."""
    r28, r69 = "only_28", "only_69"
    strata = {r28: {"strata": ["0", "1", "0", "1"]}, r69: {"strata": ["0", "1", "0", "1"]}}
    x_a_full = {r28: [1, 2, 3, 4], r69: [10, 20, 30, 40]}
    py = {"2.8b": {r28: {"y": [0, 1, 0, 1], "n_pos": 2}},
         "6.9b": {r69: {"y": [1, 0, 1, 0], "n_pos": 2}}}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(bg, "R_28", (r28,))
        mp.setattr(bh, "R_69", (r69,))
        red = an.rederive_2g2h(x_a_full, py, strata, n_perm=15, n_boot=5)
    want = an2i._run_test(x_a_full, "1b", py["6.9b"], strata, (r69,), n_perm=15, n_boot=5)
    assert an._T_of(red["primary"]) == an._T_of(want)


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
    # Task 4: FROZEN_SHA256_2J is now a LITERAL dict over exactly
    # FROZEN_FILES_2J's 26 paths (2i's 22 + analyze_2i.py + battery_2i.py
    # + power_2j.py + make_referents_2j.py) — recomputed here directly
    # from disk, independent of the literal, so a stale literal fails
    # loud rather than merely counting entries.
    assert len(an.FROZEN_SHA256_2J) == 26
    assert set(an.FROZEN_SHA256_2J) == set(an.FROZEN_FILES_2J)
    for p, want in an.FROZEN_SHA256_2J.items():
        assert bg.sha256_file(p) == want, p


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


def _raiser(*a, **kw):
    raise RuntimeError("injected for a Step 4 totality mutation test")


def _run_empty(tmp_path, **kw):
    return an.run(root_2i=tmp_path, root_2j=tmp_path, referents_sha=False, n_perm=10, n_boot=3,
                  tag_exists=lambda t: True,
                  blob_sha=lambda t, r: bg.sha256_file(bg.REPO / r) if (bg.REPO / r).is_file() else None,
                  blobs_bound=lambda tag, paths, repo_root=None: [], **kw)


# The block below closes Step 4 mutation gaps at collect_total call
# sites whose thunks read REAL, root_2i-INDEPENDENT repo data (the
# battery, the floors, the verify criterion, the 2g strata predictor,
# the 2i checkpoint manifest, the frozen-import checks, the strata pin
# check, the manifest-entry lookups, the 2g/2h pythia outcomes) — these
# all SUCCEED even against the empty `tmp_path` root the test above
# uses, so stripping their collect_total wrapper is invisible there;
# each test below forces exactly ONE of them to raise and checks the
# run still reaches INSUFFICIENT_DATA (not an uncaught exception, which
# would fail the test with an ERROR rather than a clean assertion).

def test_run_catches_a_forced_battery_load_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(bg, "load_battery", _raiser)
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("battery items" in f for f in v["referents"]["failures"])


def test_run_catches_a_forced_floors_load_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(bg, "load_floors", _raiser)
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("floors 2d" in f for f in v["referents"]["failures"])


def test_run_catches_a_forced_verify_load_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(a2d, "load_verify", _raiser)
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("verify criterion 3c" in f for f in v["referents"]["failures"])


def test_run_catches_a_forced_strata_predictor_load_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(pr, "load_predictor", _raiser)
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("strata source 2g predictor" in f for f in v["referents"]["failures"])


def test_run_catches_a_forced_checkpoint_manifest_load_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(bi, "load_manifest", _raiser)
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2i checkpoint manifest" in f for f in v["referents"]["failures"])


def test_run_catches_a_forced_pythia_outcomes_load_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(an, "load_pythia_outcomes", _raiser)
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("pythia outcomes 2g 2h" in f for f in v["referents"]["failures"])


def test_run_catches_a_forced_frozen_imports_check_failure(tmp_path, monkeypatch):
    """The frozen-imports loop's ONE `collect_total(thunk, label)` call
    site cycles through four checks at runtime; forcing any one of them
    to raise is enough to prove the loop's wrapper is intact."""
    monkeypatch.setattr(bg, "check_frozen_imports_2g", _raiser)
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2g upstream frozen imports" in f for f in v["referents"]["failures"])


def test_run_catches_a_forced_strata_pins_check_failure(tmp_path, monkeypatch):
    """`sg.check_strata_pins` also runs INSIDE `pr.load_predictor`'s own
    validation (its first call, which must succeed so `pred2g`/`strata`
    build normally) — a bare raiser fails at the earlier "strata source
    2g predictor" label instead, so this only raises from the SECOND
    call onward (run()'s own downstream "strata pins 2g" site)."""
    orig = sg.check_strata_pins
    calls = {"n": 0}

    def flaky(*a, **kw):
        calls["n"] += 1
        if calls["n"] == 1:
            return orig(*a, **kw)
        raise RuntimeError("injected for a Step 4 totality mutation test")

    monkeypatch.setattr(sg, "check_strata_pins", flaky)
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("strata pins 2g" in f for f in v["referents"]["failures"])


def test_run_catches_a_forced_entry_7b_lookup_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(bi, "entry_7b", _raiser)
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2i 7B endpoint entry" in f for f in v["referents"]["failures"])


def test_run_catches_a_forced_entry_1b_endpoint_lookup_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(bi, "entry_1b_endpoint", _raiser)
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2i 1B endpoint entry" in f for f in v["referents"]["failures"])


def test_run_catches_a_forced_referent_manifest_check_failure(tmp_path, monkeypatch):
    """The manifest-check thunk (`mkr.check_referents`) is SKIPPED
    entirely when the caller passes `referents_sha=False`, as every
    other empty-root test above does — so it needs its own test that
    lets `referents_sha` default (to the now-pinned REFERENTS_2J_SHA256
    literal) instead."""
    from experiments.exp2j import make_referents_2j as mkr
    monkeypatch.setattr(mkr, "check_referents", _raiser)
    v = an.run(root_2i=tmp_path, root_2j=tmp_path, n_perm=10, n_boot=3,
              tag_exists=lambda t: True,
              blob_sha=lambda t, r: bg.sha256_file(bg.REPO / r) if (bg.REPO / r).is_file() else None,
              blobs_bound=lambda tag, paths, repo_root=None: [])
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2j referent manifest" in f for f in v["referents"]["failures"])


def test_run_catches_a_torn_gate1_record_on_read(tmp_path):
    """`collect_total(lambda: json.loads(g1p.read_text()), "2i gate 1
    record")` is only reached when `g1p.is_file()` — on the empty-root
    test above `gate1_path` has no file at all, so the branch that
    would raise (rather than the earlier 'record missing' failure) is
    never taken; writing a torn file at that exact path (no other
    monkeypatch needed) reaches it directly and cheaply."""
    p = bi.gate1_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{not valid json")
    v = _run_empty(tmp_path)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2i gate 1 record" in f for f in v["referents"]["failures"])


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
