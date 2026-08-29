# experiments/exp2k/tests/test_analyze_2k.py
"""analyze_2k: the tree on literal inputs, the licences, the pin
extractors on the committed 2i/2j records, ladder/blocks/placement on
toys, load_power_2k refusals, require_prereg_2k, prefix-disjoint
labels (own, vs 2i, vs 2j), the import surface, run() on an empty root
and on a halted root."""
from __future__ import annotations

import ast
import json
import re
import sys
import types
from pathlib import Path

import numpy as np
import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g import predictor_2g as pr
from experiments.exp2g import stats_2g as st
from experiments.exp2g import strata_2g as sg
from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2j import analyze_2j as an2j
from experiments.exp2j import functionals_2j as fn
from experiments.exp2k import analyze_2k as an
from experiments.exp2k import battery_2k as bk


def _prim(T, p, fires, eligible=("r1", "r2", "r3")):
    return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}, "fires": fires,
            "named_inside": None, "eligible": list(eligible), "per_rung": {}}


def _undefined_prim():
    return {"stratified": {"T": None, "p": 1.0, "n_perm": 0, "n_ge": 0}, "fires": False,
            "named_inside": "undefined: every eligible rung degenerate (predictor "
                            "constant inside every stratum)", "eligible": [], "per_rung": {}}


def _power(status="POWERED"):
    return {"declared_status": status, "declaration": "x", "rungs": list(bk.R_CAP_DESIGN),
            "n_trained_steps": 21}


def test_tree_worlds_and_annotations():
    assert an.verdict_tree_2k(["x"], None, None)["verdict"] == "INSUFFICIENT_DATA"
    v = an.verdict_tree_2k([], _prim(0.15, 0.001, True), _power())
    assert v["verdict"] == "DENSITY" and v["annotation"] is None
    v = an.verdict_tree_2k([], _prim(0.05, 0.001, False), _power())
    assert v["verdict"] == "NOT-DENSITY" and v["annotation"] == "structured"
    v = an.verdict_tree_2k([], _prim(0.15, 0.3, False), _power())
    assert v["verdict"] == "NOT-DENSITY" and v["annotation"] == "null"
    v = an.verdict_tree_2k([], _prim(0.0999, 0.001, False), _power())
    assert v["annotation"] == "structured"
    assert set(an.WORLDS_2K) == {"INSUFFICIENT_DATA", "DENSITY", "NOT-DENSITY"}


def test_tree_annotation_boundary_is_alpha_not_a_looser_literal():
    # ALPHA is 0.01: p = 0.03 sits BETWEEN 0.01 and a loosened 0.05 bar,
    # so this is the one p value that tells the two apart.
    assert st.ALPHA == 0.01
    v = an.verdict_tree_2k([], _prim(0.05, 0.03, False), _power())
    assert v["annotation"] == "null"


def test_tree_disclosures_thin_and_undefined():
    v = an.verdict_tree_2k([], _undefined_prim(), _power())
    assert v["verdict"] == "NOT-DENSITY" and v["annotation"] == "null"
    assert v["disclosures"] == [an.DISCLOSURE_UNDEFINED_2K]
    assert an.DISCLOSURE_UNDEFINED_2K in an._licensed(v)
    v = an.verdict_tree_2k([], _prim(0.05, 0.3, False, eligible=("a", "b")), _power())
    assert v["disclosures"] == [an.DISCLOSURE_THIN_2K]
    v = an.verdict_tree_2k([], _prim(0.15, 0.001, True, eligible=("a", "b")), _power())
    assert v["verdict"] == "DENSITY" and v["disclosures"] == [an.DISCLOSURE_THIN_2K]


def test_licensed_sentences_carry_the_caveat_and_the_status():
    for k, s in an.LICENSED_2K.items():
        assert an.KNOWN_INPUTS_CAVEAT_2K in s, k
    assert an.KNOWN_INPUTS_CAVEAT_2K.startswith("The outcome. 2i's 7B stage-1 sweep")
    v = an.verdict_tree_2k([], _prim(0.05, 0.3, False), _power("DECLARED UNDERPOWERED IN ADVANCE"))
    assert "not detected at this resolution" in an._licensed(v)
    v = an.verdict_tree_2k([], _prim(0.15, 0.001, True), _power())
    assert "bar cleared" in an._licensed(v) and "not a forecast" in an._licensed(v)
    # NOT-DENSITY under a plain POWERED status licenses the (non-underpowered)
    # NOT-DENSITY sentence, not the DECLARED-UNDERPOWERED one.
    v = an.verdict_tree_2k([], _prim(0.05, 0.3, False), _power("POWERED"))
    assert an._licensed(v) == an.LICENSED_2K["NOT-DENSITY"]
    assert "not detected at this resolution" not in an._licensed(v)


def test_pins_extract_from_the_committed_2i_record():
    v2i = json.loads((bi.EXP2I / "results" / "verdict.json").read_text())
    got = an.pin_a_from_record_2i(v2i)
    assert got["A"] == an.VERDICT_2I_PIN_A == 0.09491251078607414
    assert set(got["per_rung"]) == set(bk.R_CAP_DESIGN)
    assert got["per_rung"]["sub_base8"] > got["per_rung"]["sub4_mid"]
    a410 = an.pin_a410_from_record_2i(v2i)
    assert a410 == an.VERDICT_2I_PIN_A410 and 0.10 < a410 < 0.13
    v2g = json.loads((bg.EXP2G / "results" / "verdict.json").read_text())
    assert an2j.pin_from_record_2g(v2g)["sampler_competitor"] == an.VERDICT_2G_PIN_28


def test_ladder_b_from_the_committed_2j_record():
    lad = an.ladder_b_from_record_2j(json.loads(
        (bg.REPO / "experiments/exp2j/results/verdict.json").read_text()))
    assert set(lad) == {1, 2, 4, 8, 16, 32, 64}
    assert abs(lad[64] - 0.2204) < 1e-3 and abs(lad[4] - 0.1104) < 1e-3


def test_placement_on_ladder_interpolates_in_log_k():
    lad = {1: 0.05, 2: 0.08, 4: 0.11, 8: 0.145, 16: 0.176, 32: 0.2025, 64: 0.2204}
    p = an.placement_on_ladder(lad, 0.145)
    assert p["k_equivalent"] == pytest.approx(8.0) and p["bracket"] == [8, 8]
    p = an.placement_on_ladder(lad, 0.16)                 # between 8 and 16
    assert 8 < p["k_equivalent"] < 16 and p["bracket"] == [8, 16]
    frac = (0.16 - 0.145) / (0.176 - 0.145)
    want_log2 = 2 ** (np.log2(8) + frac * (np.log2(16) - np.log2(8)))
    want_linear = 8 + frac * (16 - 8)
    assert p["k_equivalent"] == pytest.approx(want_log2)
    assert p["k_equivalent"] != pytest.approx(want_linear)   # log2, not linear, interpolation
    assert an.placement_on_ladder(lad, 0.30)["bracket"] == [64, None]
    assert an.placement_on_ladder(lad, 0.01)["bracket"] == [None, 1]


def _toy(seed=0, n=80, k_signal=256):
    """Toy cells: bits 500-free — n items, strata two levels, y a noisy
    function of the 256-count; returns (bits, out, strata)."""
    rng = np.random.default_rng(seed)
    q = rng.beta(0.5, 2.0, size=n)
    bits = [[int(rng.random() < q[i]) for _ in range(256)] for i in range(n)]
    y = [int(min(21, round(21 * q[i] + rng.normal(0, 2)))) for i in range(n)]
    y = [max(0, v) for v in y]
    out = {"r1": {"y": y, "n_pos": sum(1 for v in y if v > 0)}}
    strata = {"r1": {"strata": [str(i % 2) for i in range(n)]}}
    return {"r1": bits}, out, strata


def test_ladder_2k_k64_equals_block0_and_k256_equals_full():
    bits, out, strata = _toy()
    kw = dict(n_perm=50, n_boot=5)
    lad = an.ladder_2k(bits, out, strata, ("r1",), "1b", **kw)
    assert set(lad) == set(bk.LADDER_K)
    s1 = an.s1_blocks(bits, out, strata, ("r1",), "1b", **kw)
    assert lad[64]["stratified"]["T"] == s1["per_seed"]["0"]["stratified"]["T"]
    full = an2i._run_test({"r1": bk.counts_at_k(bits["r1"], 256)}, "1b", out, strata, ("r1",), **kw)
    assert lad[256]["stratified"]["T"] == full["stratified"]["T"]
    assert set(s1["per_seed"]) == {"0", "1", "2", "3"}
    assert len(s1["T"]) == 4 and s1["sd"] == pytest.approx(float(np.std(s1["T"], ddof=1)))
    assert s1["min"] <= s1["mean"] <= s1["max"]


def test_s3_matched_thins_b_to_matched_k_and_caps():
    rng = np.random.default_rng(1)
    n = 60
    bits_b = {"r1": [[int(rng.random() < 0.3) for _ in range(64)] for _ in range(n)]}
    x_a64 = {"r1": [int(rng.random() < 0.02) for _ in range(n)]}
    bits_a = {"r1": [[int(rng.random() < 0.02) for _ in range(256)] for _ in range(n)]}
    x_a256 = {"r1": bk.counts_at_k(bits_a["r1"], 256)}
    y = [int(rng.integers(0, 22)) for _ in range(n)]
    out = {"r1": {"y": y, "n_pos": sum(1 for v in y if v > 0)}}
    strata = {"r1": {"strata": ["0"] * n}}
    res = an.s3_matched(bits_b, x_a64, x_a256, out, strata, ("r1",), ladder_b={64: 0.2, 1: 0.01})
    k = res["per_rung"]["r1"]["k"]
    assert 1 <= k <= 64 and res["per_rung"]["r1"]["n_blocks"] == 64 // k
    assert "thinned_B" in res and "placement" in res and "T_A256" in res
    # n_blocks_used counts blocks _block_reading actually averaged over —
    # if n_blocks were hardcoded to 1 (rather than the matched m["n_blocks"]),
    # this could never exceed 1.
    assert res["per_rung"]["r1"]["n_blocks_used"] == res["per_rung"]["r1"]["n_blocks"] > 1
    # a rung where A at 256 is at least as dense as B at 64 is capped
    dense_a = {"r1": [64] * n}
    res2 = an.s3_matched(bits_b, {"r1": [16] * n}, dense_a, out, strata, ("r1",), ladder_b={64: 0.2})
    assert res2["per_rung"]["r1"]["capped"] is True and res2["per_rung"]["r1"]["k"] == 64


def test_load_power_2k_refusals(tmp_path):
    p = bk.power_path(tmp_path)
    p.parent.mkdir(parents=True)
    good = {"primary": _power(), "predictor_sha256": "S" * 64, "shape_note": "x", "note": "x"}
    p.write_text(json.dumps(good))
    assert an.load_power_2k(tmp_path, bk.R_CAP_DESIGN, "S" * 64)["primary"]["declared_status"] == "POWERED"
    with pytest.raises(ValueError, match="predictor_sha256"):
        an.load_power_2k(tmp_path, bk.R_CAP_DESIGN, "T" * 64)
    bad = dict(good, primary=dict(_power(), rungs=list(bk.R_CAP_DESIGN) + ["extra"]))
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="rungs"):
        an.load_power_2k(tmp_path, bk.R_CAP_DESIGN, "S" * 64)
    bad = dict(good, primary=dict(_power("MAYBE")))
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="declared_status"):
        an.load_power_2k(tmp_path, bk.R_CAP_DESIGN, "S" * 64)
    p.write_text("[]")
    with pytest.raises(ValueError):
        an.load_power_2k(tmp_path, bk.R_CAP_DESIGN, "S" * 64)


def _raise_2i(*a, **kw):
    raise ValueError("injected for a Task 5 load_2i_tree collect_total test")


_2I_TAG_OK = dict(tag_exists=lambda t: True, blobs_bound=lambda tag, paths, repo_root=None: [])


@pytest.mark.parametrize("mod,attr,label", [
    (bg, "load_battery", "2k battery items"),
    (bg, "load_floors", "2k floors 2d"),
    (a2d, "load_verify", "2k verify criterion 3c"),
    (pr, "load_predictor", "2k strata source 2g predictor"),
    (bi, "load_manifest", "2k/2i checkpoint manifest"),
    (an2i, "_load_predictor_seal_content", "2k/2i predictor seal content"),
    (an2i, "_load_rung_set", "2k/2i rung set file"),
    (an2i, "load_predictor_records_2i", "2k/2i predictor olmo1b records"),
    (an2i, "load_endpoint_which", "2k/2i endpoint stage1_final"),
    (an2i, "load_sweep_7b", "2k/2i sweep olmo7b"),
    (an2i, "gate1_rederive_7b", "2k/2i gate 1 byte identity re-derived"),
    (bi, "sampler_counts_olmo", "2k x_B counts olmo1b"),
    (fn, "draw_rows_2i", "2k bits x_B"),
    (an2j, "load_pythia_outcomes", "2k pythia outcomes 2g 2h"),
    (bi, "entry_7b", "2k/2i 7B endpoint entry"),
    (bi, "entry_1b_endpoint", "2k/2i 1B endpoint entry"),
    (an2i, "_check_predictor_seal_sampling", "2k/2i predictor seal sampling block"),
    (an2i, "_check_rung_set_vs_endpoint", "2k/2i rung set vs endpoint"),
    (an2i, "_check_predictor_counts_2i", "2k x_B counts vs the sealed attestation"),
    (an2i, "_check_rung_set_derivation", "2k/2i rung set re-derivation"),
], ids=lambda v: v if isinstance(v, str) and " " not in v else "-")
def test_load_2i_tree_collect_total_sites_land_gracefully(monkeypatch, mod, attr, label):
    # each of load_2i_tree's collect_total sites, forced to raise ONE at a
    # time on the REAL committed 2i tree (~3s, no world needed): confirms
    # the site is actually collect_total-wrapped (a bare re-implementation
    # would let the injected exception escape uncaught) and that the
    # exact label this task's brief names is what lands in `failures`.
    monkeypatch.setattr(mod, attr, _raise_2i)
    failures, ctx = an.load_2i_tree(bi.EXP2I, **_2I_TAG_OK)
    assert any(label in f for f in failures), (label, failures)


def test_load_2i_tree_frozen_imports_loop_forced_exception(monkeypatch):
    # the "for thunk, label in (...)" loop (line 287) is ONE collect_total
    # call site executed four times; breaking any one thunk proves the
    # site is wrapped.
    monkeypatch.setattr(bg, "check_frozen_imports_2g", _raise_2i)
    failures, ctx = an.load_2i_tree(bi.EXP2I, **_2I_TAG_OK)
    assert any("2k upstream 2g frozen imports" in f for f in failures), failures


def test_load_2i_tree_strata_pins_direct_call_forced_exception(monkeypatch):
    # sg.check_strata_pins is ALSO called internally by pr.load_predictor
    # (predictor_2g.py, on the raw table) before load_2i_tree's OWN direct
    # call on the converted strata object — a blanket monkeypatch breaks
    # the upstream call first and never reaches the target site, so this
    # lets the first (upstream) call through and breaks only the second.
    orig = sg.check_strata_pins
    calls = {"n": 0}

    def wrapped(*a, **kw):
        calls["n"] += 1
        if calls["n"] >= 2:
            raise ValueError("injected for a Task 5 load_2i_tree collect_total test")
        return orig(*a, **kw)

    monkeypatch.setattr(sg, "check_strata_pins", wrapped)
    failures, ctx = an.load_2i_tree(bi.EXP2I, **_2I_TAG_OK)
    assert any("2k strata pins 2g" in f for f in failures), failures


def test_load_2i_tree_gate1_record_torn(monkeypatch, tmp_path):
    bad = tmp_path / "gate1.json"
    bad.write_text('{"broken"')
    monkeypatch.setattr(bi, "gate1_path", lambda root: bad)
    failures, ctx = an.load_2i_tree(bi.EXP2I, **_2I_TAG_OK)
    assert any("2k/2i gate 1 record" in f for f in failures), failures


def test_load_2i_tree_outcomes_7b_forced_exception(monkeypatch):
    # guarded by `if not failures:` — must run with nothing ELSE broken,
    # so it is its own test rather than a parametrize case.
    monkeypatch.setattr(an2i, "outcomes_7b", _raise_2i)
    failures, ctx = an.load_2i_tree(bi.EXP2I, **_2I_TAG_OK)
    assert any("2k outcome olmo7b" in f for f in failures), failures


def test_load_2i_tree_clean_on_the_real_committed_tree():
    # the control: nothing broken, the real tree loads with zero failures
    # (every one of the above tests is a controlled deviation from this).
    failures, ctx = an.load_2i_tree(bi.EXP2I, **_2I_TAG_OK)
    assert failures == []
    assert ctx["r_cap"] == bk.R_CAP_DESIGN


_RUN_EMPTY_ROOT_OK = dict(referents_sha=False, imports_pinned=False, tag_exists=lambda t: True,
                          blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel),
                          blobs_bound=lambda tag, paths, repo_root=None: [])


def test_run_frozen_modules_forced_exception(monkeypatch, tmp_path):
    monkeypatch.setattr(bk, "check_frozen_2k", _raise_2i)
    v = an.run(root_2i=tmp_path, root_2k=tmp_path, **_RUN_EMPTY_ROOT_OK)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2k frozen modules" in f for f in v["referents"]["failures"])


def test_run_prereg_forced_exception(monkeypatch, tmp_path):
    monkeypatch.setattr(bk, "require_prereg_2k", _raise_2i)
    v = an.run(root_2i=tmp_path, root_2k=tmp_path, **_RUN_EMPTY_ROOT_OK)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2k prereg tag" in f for f in v["referents"]["failures"])


def test_run_referent_manifest_forced_exception(monkeypatch, tmp_path):
    from experiments.exp2k import make_referents_2k as mkr
    monkeypatch.setattr(mkr, "check_referents", _raise_2i)
    kw = {**_RUN_EMPTY_ROOT_OK, "referents_sha": an.REFERENTS_2K_SHA256}
    v = an.run(root_2i=tmp_path, root_2k=tmp_path, **kw)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2k referent manifest" in f for f in v["referents"]["failures"])


def _tier_fixture(tmp_path, rung="antonym", size="1b"):
    """One real cell's worth of tier data on a fresh root: the record
    round-trips through tier_record_2k/tier_record_failures_2k (2j F-1's
    rule — a fixture must carry the real shape), draws = the real
    committed seed-0 row plus placeholder seeds 1-3, so load_tier_2k's
    gate-1 re-derivation and per_seed_tallies check both pass cleanly."""
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    cap = battery[rung]
    committed = bk.committed_by_item(bk.committed_rows(size, rung))
    rows = [{"item": i, "draws": {"0": list(committed[i]), "1": [" x"] * bk.DRAWS_PER_SEED,
                                  "2": [" x"] * bk.DRAWS_PER_SEED, "3": [" x"] * bk.DRAWS_PER_SEED}}
            for i in range(bk.N_ITEMS)]
    crec_p = bk.committed_record_path(size, rung)
    cgz_p = bk.committed_draws_path(size, rung)
    rec = bk.tier_record_2k(rung=rung, size=size, cap=cap, rows=rows, verify_fn=verify_fn,
                            model_sha=bk.pythia_sha(size),
                            stack={"torch": "n/a", "transformers": "n/a"}, git_sha="", seconds=0.0,
                            committed_gz_sha=bg.sha256_file(cgz_p),
                            committed_record_sha=bg.sha256_file(crec_p),
                            gate1_items_compared=bk.N_ITEMS,
                            gate1_draws_compared=bk.N_ITEMS * bk.DRAWS_PER_SEED)
    from experiments.exp2i.run.sample_2i import write_draws
    bk.tier_draws_path(tmp_path, size, rung).parent.mkdir(parents=True, exist_ok=True)
    write_draws(bk.tier_draws_path(tmp_path, size, rung), rows)
    bk.tier_record_path(tmp_path, size, rung).write_text(json.dumps(rec))
    return battery, verify_fn


def test_load_tier_2k_clean_on_one_real_cell(tmp_path):
    battery, verify_fn = _tier_fixture(tmp_path)
    failures, cells = an.load_tier_2k(tmp_path, "1b", battery=battery, verify_fn=verify_fn,
                                      rungs=("antonym",))
    assert failures == []
    assert set(cells) == {"antonym"}
    assert cells["antonym"]["gate1_rederived"]["n_diffs"] == 0


def test_load_tier_2k_record_read_torn(tmp_path):
    battery, verify_fn = _tier_fixture(tmp_path)
    bk.tier_record_path(tmp_path, "1b", "antonym").write_text('{"broken"')
    failures, cells = an.load_tier_2k(tmp_path, "1b", battery=battery, verify_fn=verify_fn,
                                      rungs=("antonym",))
    assert any("record read" in f for f in failures), failures


def test_load_tier_2k_rows_read_torn(tmp_path):
    battery, verify_fn = _tier_fixture(tmp_path)
    p = bk.tier_draws_path(tmp_path, "1b", "antonym")
    p.write_bytes(p.read_bytes()[:-50])
    failures, cells = an.load_tier_2k(tmp_path, "1b", battery=battery, verify_fn=verify_fn,
                                      rungs=("antonym",))
    assert any("rows read" in f for f in failures), failures


def test_load_tier_2k_gate1_catches_a_real_seed0_diff(tmp_path):
    from experiments.exp2i.run.sample_2i import write_draws
    battery, verify_fn = _tier_fixture(tmp_path)
    p = bk.tier_draws_path(tmp_path, "1b", "antonym")
    rows = bk.read_rows_2k(p)
    rows[0]["draws"]["0"][0] = rows[0]["draws"]["0"][0] + "!"
    write_draws(p, rows)
    failures, cells = an.load_tier_2k(tmp_path, "1b", battery=battery, verify_fn=verify_fn,
                                      rungs=("antonym",))
    assert any("gate 1" in f and "differ" in f for f in failures), failures


def test_load_tier_2k_catches_a_wrong_committed_sha_in_the_record(tmp_path):
    battery, verify_fn = _tier_fixture(tmp_path)
    p = bk.tier_record_path(tmp_path, "1b", "antonym")
    rec = json.loads(p.read_text())
    rec["gate1"]["committed_draws_sha256"] = "0" * 64
    p.write_text(json.dumps(rec))
    failures, cells = an.load_tier_2k(tmp_path, "1b", battery=battery, verify_fn=verify_fn,
                                      rungs=("antonym",))
    assert any("committed_draws_sha256" in f for f in failures), failures


def test_load_tier_2k_gate1_forced_exception(monkeypatch, tmp_path):
    battery, verify_fn = _tier_fixture(tmp_path)
    monkeypatch.setattr(bk, "diff_seed0", _raise_2i)
    failures, cells = an.load_tier_2k(tmp_path, "1b", battery=battery, verify_fn=verify_fn,
                                      rungs=("antonym",))
    assert any("gate 1 re-derived" in f for f in failures), failures


def test_load_tier_2k_bits_forced_exception(monkeypatch, tmp_path):
    battery, verify_fn = _tier_fixture(tmp_path)
    monkeypatch.setattr(bk, "bits_2k", _raise_2i)
    failures, cells = an.load_tier_2k(tmp_path, "1b", battery=battery, verify_fn=verify_fn,
                                      rungs=("antonym",))
    assert any("bits and tallies" in f for f in failures), failures


def test_load_tier_2k_gate1_catches_a_wrong_draws_compared_attestation(tmp_path):
    # fix round 1 / Finding 1 (mutant #26): the record's OWN attested
    # gate1.draws_compared is wrong while the rows/draws file is
    # untouched, so _gate()'s own re-derivation (against a freshly
    # computed n_cmp) is what has to catch it. tier_record_failures_2k
    # ALSO flags a wrong draws_compared (against the fixed N_ITEMS *
    # DRAWS_PER_SEED constant, which is the same target here) — the
    # needle below is _gate()'s own distinct message text ("gate 1
    # attested ... re-derived ..."), so this only passes if _gate()'s
    # line is intact, not merely because SOME failure was reported.
    battery, verify_fn = _tier_fixture(tmp_path)
    p = bk.tier_record_path(tmp_path, "1b", "antonym")
    rec = json.loads(p.read_text())
    rec["gate1"]["draws_compared"] = 31999
    p.write_text(json.dumps(rec))
    failures, cells = an.load_tier_2k(tmp_path, "1b", battery=battery, verify_fn=verify_fn,
                                      rungs=("antonym",))
    assert any("gate 1 attested" in f for f in failures), failures


def test_load_tier_2k_bits_catches_a_wrong_per_seed_tallies(tmp_path):
    # fix round 1 / Finding 1 (mutant #27): corrupts only the VALUE
    # tallied (full_string), not n_draws — tier_record_failures_2k only
    # checks n_draws (a fixed constant), so it does NOT independently
    # catch this; only _bits()'s own re-derivation against the draws
    # file, freshly re-verified, can.
    battery, verify_fn = _tier_fixture(tmp_path)
    p = bk.tier_record_path(tmp_path, "1b", "antonym")
    rec = json.loads(p.read_text())
    rec["per_seed_tallies"]["0"]["full_string"] += 1
    p.write_text(json.dumps(rec))
    failures, cells = an.load_tier_2k(tmp_path, "1b", battery=battery, verify_fn=verify_fn,
                                      rungs=("antonym",))
    assert any("disagree with the re-derivation" in f for f in failures), failures


def _all_failure_labels_2k():
    src = (bk.EXP2K / "analyze_2k.py").read_text()
    tree = ast.parse(src)
    labels = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "collect_total" \
                and len(node.args) == 2 and isinstance(node.args[1], ast.Constant):
            labels.append(node.args[1].value)
    # the f-string labels inside loops carry "{size}"/"{rung}" — collect their literal prefixes
    for m in re.finditer(r'collect_total\([^,]+,\s*f"([^"{]+)', src):
        labels.append(m.group(1))
    assert labels
    return labels


def test_collect_total_labels_are_prefix_disjoint_and_disjoint_from_2i_2j():
    labels = _all_failure_labels_2k()
    # fix round 1 / Finding 2: the load_tier_2k wrap's label ("2k tier
    # {size} load") is only harvestable by the f-string regex if its
    # thunk is a bare name with no commas (bound via `def _tier(size=
    # size): ...` rather than an inline lambda calling load_tier_2k with
    # several keyword arguments) — assert it is actually collected, not
    # silently skipped.
    assert any(label.startswith("2k tier ") for label in labels), labels
    for a in labels:
        for b in labels:
            if a != b:
                assert not b.startswith(a), (a, b)
    src_2i = (bi.EXP2I / "analyze_2i.py").read_text()
    src_2j = (bg.REPO / "experiments/exp2j/analyze_2j.py").read_text()
    for a in labels:
        assert f'"{a}"' not in src_2i and f'"{a}"' not in src_2j, a


def test_run_on_an_empty_root_is_insufficient_data(tmp_path):
    v = an.run(root_2i=tmp_path, root_2k=tmp_path, referents_sha=False, imports_pinned=False,
               tag_exists=lambda t: True,
               blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel),
               blobs_bound=lambda tag, paths, repo_root=None: [])
    assert v["verdict"] == "INSUFFICIENT_DATA" and v["primary"] is None and v["secondaries"] is None
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2K
    assert any("2k tier" in f for f in v["referents"]["failures"])


def test_run_on_a_halted_root_names_the_marker_first(tmp_path):
    m = bk.halt_marker_path(tmp_path, "1b", "antonym")
    m.parent.mkdir(parents=True)
    m.write_text("{}")
    v = an.run(root_2i=tmp_path, root_2k=tmp_path, referents_sha=False, imports_pinned=False,
               tag_exists=lambda t: True,
               blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel),
               blobs_bound=lambda tag, paths, repo_root=None: [])
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("HALTED" in f for f in v["referents"]["failures"])


def test_run_refuses_when_the_manifest_or_imports_are_not_pinned(tmp_path, monkeypatch):
    monkeypatch.setattr(an, "REFERENTS_2K_SHA256", None)
    v = an.run(root_2i=tmp_path, root_2k=tmp_path, imports_pinned=False, tag_exists=lambda t: True,
               blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel),
               blobs_bound=lambda tag, paths, repo_root=None: [])
    assert any("not pinned" in f for f in v["referents"]["failures"])
    monkeypatch.setattr(an, "IMPORTED_SHA256_2K", None)
    v = an.run(root_2i=tmp_path, root_2k=tmp_path, referents_sha=False, tag_exists=lambda t: True,
               blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel),
               blobs_bound=lambda tag, paths, repo_root=None: [])
    assert any("import surface" in f and "not pinned" in f for f in v["referents"]["failures"])


def test_check_imports_2k_refuses_an_unpinned_loaded_module(monkeypatch, tmp_path):
    monkeypatch.setattr(an, "IMPORTED_SHA256_2K", {})
    fake = types.ModuleType("experiments.exp2k.tests_fake_mod")
    fake_path = bk.EXP2K / "zz_fake_mod.py"
    fake.__file__ = str(fake_path)
    monkeypatch.setitem(sys.modules, "experiments.exp2k.zz_fake_mod", fake)
    with pytest.raises(RuntimeError, match="unpinned module"):
        an.check_imports_2k()


def test_check_imports_2k_refuses_a_drifted_pin(monkeypatch):
    # Corrupt ONE real entry's hash rather than replacing the whole dict:
    # under whole-directory collection, run/__init__.py and
    # run/rehearse_2k.py are already in sys.modules (test_tier_2k.py
    # imports rehearse_2k at module scope) by the time this test runs,
    # so wiping IMPORTED_SHA256_2K wholesale would report THEM unpinned
    # before ever reaching the drift this test is actually about — a
    # session-order fragility, not a defect in check_imports_2k itself.
    corrupted = dict(an.IMPORTED_SHA256_2K)
    corrupted[bk.EXP2K / "__init__.py"] = "0" * 64
    monkeypatch.setattr(an, "IMPORTED_SHA256_2K", corrupted)
    with pytest.raises(RuntimeError, match="drifted"):
        an.check_imports_2k()


def test_check_imports_2k_refuses_when_frozen_sha_does_not_cover_frozen_files(monkeypatch):
    # fix round 1 / Finding 1: once FROZEN_SHA256_2K is non-empty its
    # keys must equal FROZEN_FILES_2K's paths exactly, or a path could
    # be "covered" here and hash-verified by no gate anywhere. Drop the
    # first documented path from the pinned dict (fake hash values —
    # the coverage check fires before any hash is ever read).
    partial = {p: "x" * 64 for p in bk.FROZEN_FILES_2K[1:]}
    monkeypatch.setattr(bk, "FROZEN_SHA256_2K", partial)
    monkeypatch.setattr(an, "IMPORTED_SHA256_2K", {})
    with pytest.raises(RuntimeError, match="does not cover"):
        an.check_imports_2k()


def test_check_imports_2k_empty_frozen_sha_does_not_trigger_the_coverage_check(monkeypatch):
    # the pre-Task-5 state (FROZEN_SHA256_2K == {}): the coverage
    # equality check is inert by construction (`if FROZEN_SHA256_2K`),
    # so whatever else check_imports_2k() does, it must not raise
    # "does not cover".
    monkeypatch.setattr(bk, "FROZEN_SHA256_2K", {})
    monkeypatch.setattr(an, "IMPORTED_SHA256_2K", {})
    try:
        an.check_imports_2k()
    except RuntimeError as e:
        assert "does not cover" not in str(e)


def test_check_imports_2k_excludes_test_helpers(monkeypatch):
    monkeypatch.setattr(an, "IMPORTED_SHA256_2K", {})
    mod = types.ModuleType("experiments.exp2k.tests.helper_x")
    mod.__file__ = str(bk.EXP2K / "tests" / "helper_x.py")
    monkeypatch.setitem(sys.modules, "experiments.exp2k.tests.helper_x", mod)
    # only the fake test helper is unpinned-but-excluded; other loaded 2k
    # modules are covered by INSTRUMENT_BLOBS_2K / FROZEN — unless the
    # scan finds a real gap, in which case this test reports it
    try:
        an.check_imports_2k()
    except RuntimeError as e:
        assert "helper_x" not in str(e)


def test_seal_paths_2k_union_of_rule_and_seal_files(tmp_path):
    seal = {"files": {"results/k256/1b_trained/stray.txt": "x"}}
    paths = an._seal_paths_2k(tmp_path, seal)
    assert bk.seal_path(tmp_path) in paths and bk.power_path(tmp_path) in paths
    assert bk.tier_draws_path(tmp_path, "410m", "odd6") in paths
    assert tmp_path / "results/k256/1b_trained/stray.txt" in paths
    assert len(paths) == 2 + 2 * 9 * 2 + 1


# ------------------------------------------- mutation_check.py's own guard
# (fix round 1 / Finding 3: two concurrent mutation_check.py runs raced on
# one .mutation_backup and corrupted analyze_2k.py earlier in this task.)

def test_mutation_check_refuses_a_concurrent_run(tmp_path):
    from experiments.exp2k.tests import mutation_check as mc
    target = tmp_path / "x.py"
    target.write_text("VALUE = 1\n")
    backup = target.with_suffix(target.suffix + ".mutation_backup")
    backup.write_bytes(b"stale backup from a concurrent or crashed run")
    with pytest.raises(RuntimeError, match="already exists"):
        mc._acquire_backup(target)
    assert target.read_text() == "VALUE = 1\n"   # refused before mutating anything


def test_mutation_check_refuses_at_start_if_any_backup_exists(monkeypatch, tmp_path):
    from experiments.exp2k.tests import mutation_check as mc
    fake_root = tmp_path / "experiments" / "exp2k"
    fake_root.mkdir(parents=True)
    (fake_root / "battery_2k.py.mutation_backup").write_bytes(b"x")
    monkeypatch.setattr(mc, "ROOT", tmp_path)
    with pytest.raises(RuntimeError, match="mutation_backup"):
        mc._refuse_if_any_backup_exists()
