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

from experiments.exp2g import battery_2g as bg
from experiments.exp2g import stats_2g as st
from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2j import analyze_2j as an2j
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
    monkeypatch.setattr(an, "IMPORTED_SHA256_2K", {bk.EXP2K / "__init__.py": "0" * 64})
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
