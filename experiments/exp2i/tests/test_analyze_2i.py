# experiments/exp2i/tests/test_analyze_2i.py
"""analyze_2i: the two-test tree on literal inputs, require_prereg_2i/
require_seal_2i, gate1_failures_7b, step/endpoint record refusals
through load_sweep_7b/load_endpoint_which, outcomes_7b/rung_level_7b,
_run_test/fires_2i/named_inside_2i/_degenerate_rungs, composite strata,
the referent loaders, run() on the real (artifact-free) tree."""
from __future__ import annotations

import json
import re

import numpy as np
import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2h import battery_2h as bh
from experiments.exp2i import analyze_2i as an
from experiments.exp2i import battery_2i as bi


# ------------------------------------------------------------- the tree

def _prim(T, p, n_perm=10000, n_ge=0):
    return {"stratified": {"T": T, "p": p, "n_perm": n_perm, "n_ge": n_ge}}


def test_fires_and_named_inside():
    assert an.fires_2i(_prim(0.20, 0.001)) is True
    assert an.fires_2i(_prim(0.02, 0.5)) is False
    assert an.fires_2i(_prim(0.10, 0.0099)) is True
    assert an.fires_2i(_prim(0.10, 0.01)) is False

    assert an.named_inside_2i(_prim(0.20, 0.001)) is None
    n = an.named_inside_2i(_prim(0.05, 0.001))
    assert "below the effect bar" in n
    n = an.named_inside_2i(_prim(-0.3, 0.999))
    assert "inverted" in n


def _A(fires, named=None, T=0.2, p=0.001):
    d = _prim(T if fires else 0.02, p if fires else 0.5)
    d["fires"] = fires
    d["named_inside"] = named
    return d


def test_verdict_tree_worlds():
    assert an.verdict_tree_2i(["x"], None, None)["verdict"] == "INSUFFICIENT_DATA"
    assert an.verdict_tree_2i([], _A(True), _A(False))["verdict"] == "SHARED"
    assert an.verdict_tree_2i([], _A(False), _A(True))["verdict"] == "LINEAGE"
    assert an.verdict_tree_2i([], _A(True), _A(True))["verdict"] == "BOTH"
    assert an.verdict_tree_2i([], _A(False), _A(False))["verdict"] == "NEITHER"
    assert set(an.WORLDS) == {"INSUFFICIENT_DATA", "SHARED", "LINEAGE", "BOTH", "NEITHER"}


def test_verdict_tree_reason_carries_named_inside():
    B = _A(False, named="inverted (T = -0.30; one-sided p for T_perm <= T_obs ~ 1.0)")
    v = an.verdict_tree_2i([], _A(True), B)
    assert "inverted" in v["reason"]


# --------------------------------------------------------- require_prereg_2i

def _blob_ok(tag, rel):
    """Stands in for `predictor_2g.git_blob_sha256`: None for a path the
    tag (and the working tree) never carried, otherwise the working
    copy's own hash — same shape as the stub's own `_prereg()` helper."""
    p = bi.REPO / rel
    return bg.sha256_file(p) if p.is_file() else None


def test_require_prereg_2i_passes_with_matching_blobs():
    # Task 4 landed `run/sweep_2i.py`, the fifth and final file in
    # `INSTRUMENT_BLOBS_2I` — all five now on disk, so the pass path is
    # reachable on the real, unshrunk set.
    got = an.require_prereg_2i(tag_exists=lambda t: t == bi.PREREG_TAG, blob_sha=_blob_ok)
    assert got["tag"] == bi.PREREG_TAG
    assert set(got["instrument_blobs"]) == set(an.INSTRUMENT_BLOBS_2I)
    assert len(got["instrument_blobs"]) == 5


def test_require_prereg_2i_refuses_missing_tag():
    with pytest.raises(RuntimeError, match="preregistration tag"):
        an.require_prereg_2i(tag_exists=lambda t: False, blob_sha=_blob_ok)


def test_require_prereg_2i_refuses_missing_instrument_file(monkeypatch):
    """All five real instrument files are on disk since Task 4 landed
    `run/sweep_2i.py` — this exercises the 'not on disk' refusal branch
    directly (`got is None` in `require_prereg_2i`'s loop) against a
    file that genuinely is not on disk, rather than letting that branch
    go untested now that the real five-file set is complete."""
    subset = an.INSTRUMENT_BLOBS_2I + ("experiments/exp2i/run/does_not_exist.py",)
    monkeypatch.setattr(an, "INSTRUMENT_BLOBS_2I", subset)
    with pytest.raises(RuntimeError, match="not on disk"):
        an.require_prereg_2i(tag_exists=lambda t: True, blob_sha=_blob_ok)


def test_require_prereg_2i_refuses_drifted_blob():
    def drifted(tag, rel):
        return "0" * 64 if rel.endswith("analyze_2i.py") else _blob_ok(tag, rel)
    with pytest.raises(RuntimeError, match="drifted"):
        an.require_prereg_2i(tag_exists=lambda t: True, blob_sha=drifted)


# --------------------------------------------------------- require_seal_2i

def test_require_seal_2i_missing_tag():
    got = an.require_seal_2i("no-such-tag", ["a", "b"], tag_exists=lambda t: False)
    assert got["failures"] and "does not exist" in got["failures"][0]


def test_require_seal_2i_bound_ok():
    got = an.require_seal_2i("t", ["a"], tag_exists=lambda t: True,
                             blobs_bound=lambda tag, paths, repo_root=None: [])
    assert got["failures"] == []


def test_require_seal_2i_drifted():
    got = an.require_seal_2i("t", ["a", "b"], tag_exists=lambda t: True,
                             blobs_bound=lambda tag, paths, repo_root=None: ["a"])
    assert got["failures"] and "does not bind" in got["failures"][0]


def test_require_seal_2i_never_raises_on_exceptions():
    def boom_exists(t):
        raise RuntimeError("network down")
    got = an.require_seal_2i("t", ["a"], tag_exists=boom_exists)
    assert got["failures"] and "RuntimeError" in got["failures"][0]

    def boom_bound(tag, paths, repo_root=None):
        raise ValueError("git broke")
    got2 = an.require_seal_2i("t", ["a"], tag_exists=lambda t: True, blobs_bound=boom_bound)
    assert got2["failures"] and "ValueError" in got2["failures"][0]


def test_seal_path_helpers_counts(tmp_path):
    pred_paths = an._predictor_seal_paths(tmp_path)
    assert len(pred_paths) == 1 + 2 * len(bt.RUNGS)
    ep_paths = an._endpoint_seal_paths(tmp_path)
    assert len(ep_paths) == 2 + 2 * len(bt.RUNGS)


# ------------------------------------------------------------- gate 1

def _gate_rec(**over):
    rec = {"rungs": list(bt.RUNGS), "bit_diffs": {r: 0 for r in bt.RUNGS},
           "continuation_diffs": {r: 0 for r in bt.RUNGS},
           "continuations_compared": {r: bt.N_ITEMS for r in bt.RUNGS},
           "digest_sweep": "d" * 64, "digest_endpoint": "d" * 64,
           "commit_sweep": "c" * 40, "commit_endpoint": "c" * 40,
           "prereg_tag": bi.PREREG_TAG}
    rec.update(over)
    return rec


def _endpoint_stub_records():
    return {r: {"rung": r} for r in bt.RUNGS}


def test_gate1_failures_7b_clean():
    assert an.gate1_failures_7b(_gate_rec(), _endpoint_stub_records()) == []


def test_gate1_failures_7b_bit_diff():
    bad = _gate_rec(); bad["bit_diffs"] = dict(bad["bit_diffs"]); bad["bit_diffs"]["antonym"] = 3
    fails = an.gate1_failures_7b(bad, _endpoint_stub_records())
    assert any("antonym" in f and "bit diff" in f for f in fails)


def test_gate1_failures_7b_continuation_diff():
    bad = _gate_rec()
    bad["continuation_diffs"] = dict(bad["continuation_diffs"])
    bad["continuation_diffs"]["antonym"] = 2
    fails = an.gate1_failures_7b(bad, _endpoint_stub_records())
    assert any("antonym" in f and "continuation diffs" in f for f in fails)


def test_gate1_failures_7b_digest_mismatch():
    bad = _gate_rec(digest_endpoint="e" * 64)
    assert any("digest" in f for f in an.gate1_failures_7b(bad, _endpoint_stub_records()))


def test_gate1_failures_7b_commit_mismatch():
    bad = _gate_rec(commit_endpoint="f" * 40)
    assert any("commit" in f for f in an.gate1_failures_7b(bad, _endpoint_stub_records()))


def test_gate1_failures_7b_truncated_coverage():
    bad = _gate_rec()
    bad["continuations_compared"] = dict(bad["continuations_compared"])
    bad["continuations_compared"]["antonym"] = 0
    fails = an.gate1_failures_7b(bad, _endpoint_stub_records())
    assert any("pairs compared" in f for f in fails)


def test_gate1_failures_7b_missing_coverage_field_refuses_every_rung():
    bad = _gate_rec()
    bad.pop("continuations_compared")
    fails = an.gate1_failures_7b(bad, _endpoint_stub_records())
    assert len(fails) == len(bt.RUNGS)
    assert all("pairs compared" in f for f in fails)


def test_gate1_failures_7b_wrong_tag():
    bad = _gate_rec(prereg_tag="not-the-tag")
    assert any("prereg_tag" in f for f in an.gate1_failures_7b(bad, _endpoint_stub_records()))


def test_gate1_failures_7b_no_endpoint_record_for_rung():
    fails = an.gate1_failures_7b(_gate_rec(), {r: {} for r in bt.RUNGS if r != "antonym"})
    assert any("antonym" in f and "no stage1_final" in f for f in fails)


def test_gate1_fields_constant():
    assert set(an.GATE1_FIELDS) == set(_gate_rec())


# --------------------------------------------------- step/endpoint records

def _entry(commit="c" * 40):
    return {"revision": "step1000", "commit": commit, "kind": "bin-shards",
           "files": ["a"], "lfs_sha256": {"a": "f" * 64}}


def _cap_and_verify():
    from experiments.exp2d import analyze_2d as a2d
    cap = bg.load_battery(["antonym"])["antonym"]
    return cap, a2d.load_verify()


def test_step_record_failures_2i_clean_and_mutations():
    cap, verify = _cap_and_verify()
    entry = _entry()
    conts = [f" {it['answer']}" if i % 3 == 0 else " zzz"
            for i, it in enumerate(cap["eval_items"])]
    bits = [int(verify(c, it["answer"], cap["answer_type"]))
           for c, it in zip(conts, cap["eval_items"])]
    rec = {"rung": "antonym", "size": bi.SIZE_OUT, "family": bi.FAMILY, "step": 1000,
          "commit": entry["commit"], "items_sha256": cap["items_sha256"], "n": bt.N_ITEMS,
          "correct": sum(bits), "bits": bits, "continuations": conts,
          "predictor_sha": "P" * 64, "seal_tag": bi.ENDPOINT_SEAL_TAG,
          "answer_type": cap["answer_type"]}
    assert an.step_record_failures_2i(rec, step=1000, rung="antonym", cap=cap, entry=entry,
                                      verify_fn=verify, predictor_sha="P" * 64) == []

    bad = dict(rec); bad["predictor_sha"] = "Q" * 64
    assert an.step_record_failures_2i(bad, step=1000, rung="antonym", cap=cap, entry=entry,
                                      verify_fn=verify, predictor_sha="P" * 64)

    bad = dict(rec); bad["seal_tag"] = "wrong-tag"
    assert an.step_record_failures_2i(bad, step=1000, rung="antonym", cap=cap, entry=entry,
                                      verify_fn=verify, predictor_sha="P" * 64)

    bad = dict(rec); bad["commit"] = "z" * 40
    assert an.step_record_failures_2i(bad, step=1000, rung="antonym", cap=cap, entry=entry,
                                      verify_fn=verify, predictor_sha="P" * 64)

    bad = dict(rec); bad["bits"] = list(bad["bits"]); bad["bits"][0] = 1 - bad["bits"][0]
    bad["correct"] = sum(bad["bits"])
    fails = an.step_record_failures_2i(bad, step=1000, rung="antonym", cap=cap, entry=entry,
                                       verify_fn=verify, predictor_sha="P" * 64)
    assert any("re-verification" in f for f in fails)


def test_step_record_failures_2i_twin_shape():
    cap, verify = _cap_and_verify()
    twin_entry = {"revision": "twin", "commit": None, "kind": "from_config", "files": []}
    conts = [" zzz" for _ in cap["eval_items"]]
    bits = [0] * bt.N_ITEMS
    rec = {"rung": "antonym", "size": bi.SIZE_OUT, "family": bi.FAMILY, "step": bi.TWIN,
          "commit": None, "kind": "from_config", "items_sha256": cap["items_sha256"],
          "n": bt.N_ITEMS, "correct": 0, "bits": bits, "continuations": conts,
          "predictor_sha": "P" * 64, "seal_tag": bi.ENDPOINT_SEAL_TAG,
          "answer_type": cap["answer_type"]}
    assert an.step_record_failures_2i(rec, step=bi.TWIN, rung="antonym", cap=cap,
                                      entry=twin_entry, verify_fn=verify,
                                      predictor_sha="P" * 64) == []
    bad = dict(rec); bad["commit"] = "nonNone"
    assert an.step_record_failures_2i(bad, step=bi.TWIN, rung="antonym", cap=cap,
                                      entry=twin_entry, verify_fn=verify,
                                      predictor_sha="P" * 64)


def test_endpoint_record_failures_2i_clean_and_mutations():
    cap, verify = _cap_and_verify()
    entry = _entry()
    conts = [f" {it['answer']}" if i % 3 == 0 else " zzz"
            for i, it in enumerate(cap["eval_items"])]
    bits = [int(verify(c, it["answer"], cap["answer_type"]))
           for c, it in zip(conts, cap["eval_items"])]
    rec = {"rung": "antonym", "size": bi.SIZE_OUT, "family": bi.FAMILY, "which": "stage1_final",
          "commit": entry["commit"], "items_sha256": cap["items_sha256"], "n": bt.N_ITEMS,
          "correct": sum(bits), "bits": bits, "continuations": conts,
          "predictor_sha": "P" * 64, "seal_tag": bi.PREDICTOR_SEAL_TAG,
          "answer_type": cap["answer_type"]}
    assert an.endpoint_record_failures_2i(rec, which="stage1_final", rung="antonym", cap=cap,
                                          entry=entry, verify_fn=verify,
                                          predictor_sha="P" * 64) == []
    bad = dict(rec); bad["seal_tag"] = bi.ENDPOINT_SEAL_TAG   # the wrong tag for THIS record
    assert an.endpoint_record_failures_2i(bad, which="stage1_final", rung="antonym", cap=cap,
                                          entry=entry, verify_fn=verify, predictor_sha="P" * 64)
    bad = dict(rec); bad["which"] = "main"
    assert an.endpoint_record_failures_2i(bad, which="stage1_final", rung="antonym", cap=cap,
                                          entry=entry, verify_fn=verify, predictor_sha="P" * 64)


# ------------------------------------------------------------ outcomes

def test_outcomes_7b_and_rung_level_7b():
    steps = bi.trained_steps_7b()
    sweep = {bi.TWIN: {"r": {"bits": [1] * bt.N_ITEMS, "correct": bt.N_ITEMS}}}
    for s in steps:
        bits = [1 if (s >= 32000 and i < 300) or (s == 1000 and i == 0) else 0
               for i in range(bt.N_ITEMS)]
        sweep[s] = {"r": {"bits": bits, "correct": sum(bits)}}
    out = an.outcomes_7b(sweep, rungs=("r",))
    o = out["r"]
    n_ge = sum(1 for s in steps if s >= 32000)
    assert o["y"][5] == n_ge and o["y"][0] == n_ge + 1 and o["y"][400] == 0
    assert o["first"][0] == 1000 and o["first"][400] is None
    assert o["n_pos"] == 300
    assert o["counts_by_step"][steps[0]] == 1   # only item 0 fires at step 1000

    rl = an.rung_level_7b(out, {"r": 0.25}, rungs=("r",))
    assert rl["r"]["s_star"] == 32000
    assert rl["r"]["final_clears"] is True


def test_outcomes_7b_never_includes_twin():
    steps = bi.trained_steps_7b()
    sweep = {bi.TWIN: {"r": {"bits": [1] * bt.N_ITEMS, "correct": bt.N_ITEMS}}}
    for s in steps:
        sweep[s] = {"r": {"bits": [0] * bt.N_ITEMS, "correct": 0}}
    out = an.outcomes_7b(sweep, rungs=("r",))
    assert out["r"]["y"] == [0] * bt.N_ITEMS
    assert out["r"]["n_pos"] == 0


# ------------------------------------------------------- primary/_run_test

def _synthetic_cells(rng, n=300, rho=0.7, n_pos=80):
    z = rng.normal(size=n)
    x = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
    w = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
    y = np.zeros(n, int)
    y[np.argsort(w)[-n_pos:]] = 1 + np.arange(n_pos) * 21 // n_pos
    return [int(round(v)) for v in x], y


def test_primary_2i_is_the_shared_2h_function_no_twin():
    from experiments.exp2h import analyze_2h as an2h
    assert an.primary_2i is an2h.primary_2h


def test_run_test_fires_on_a_strong_synthetic_signal():
    rng = np.random.default_rng(0)
    counts, out, strata = {}, {}, {}
    for r in ("a", "b"):
        x, y = _synthetic_cells(rng)
        counts[r] = x
        out[r] = {"y": list(y), "n_pos": int((y > 0).sum()), "first": [None] * len(y)}
        strata[r] = {"strata": [str(i % 3) for i in range(len(y))]}
    res = an._run_test(counts, "1b", out, strata, ("a", "b"), n_perm=300, n_boot=50)
    assert res["fires"] is True
    assert res["dropped_degenerate"] == []
    assert res["named_inside"] is None
    assert "twin" not in res


def test_degenerate_rungs_dropped_before_primary():
    rng = np.random.default_rng(0)
    counts, out, strata = {}, {}, {}
    for r in ("a",):
        x, y = _synthetic_cells(rng)
        counts[r] = x
        out[r] = {"y": list(y), "n_pos": int((y > 0).sum()), "first": [None] * len(y)}
        strata[r] = {"strata": [str(i % 3) for i in range(len(y))]}
    # a second rung whose predictor is CONSTANT inside every stratum
    n = 300
    counts["b"] = [7] * n
    y = np.zeros(n, int); y[:80] = 1
    out["b"] = {"y": list(y), "n_pos": 80, "first": [None] * n}
    strata["b"] = {"strata": [str(i % 3) for i in range(n)]}

    dropped = an._degenerate_rungs(counts, strata, ("a", "b"))
    assert dropped == ["b"]

    res = an._run_test(counts, "1b", out, strata, ("a", "b"), n_perm=300, n_boot=50)
    assert res["dropped_degenerate"] == ["b"]
    assert res["eligible"] == ["a"]


def test_degenerate_rungs_not_degenerate_if_any_stratum_has_two_values():
    counts = {"a": [1, 1, 2, 2, 1, 1]}
    strata = {"a": {"strata": ["0", "0", "0", "0", "1", "1"]}}
    assert an._degenerate_rungs(counts, strata, ("a",)) == []
    counts2 = {"a": [1, 1, 1, 1, 1, 1]}
    assert an._degenerate_rungs(counts2, strata, ("a",)) == ["a"]


# --------------------------------------------------------- composite strata

def test_composite_strata_zero_cut():
    strata = {"r": {"strata": ["x", "x", "y", "y"]}}
    cond = {"r": [0, 3, 0, 5]}
    got = an._composite_strata(strata, cond, ("r",))
    assert got["r"]["strata"] == ["x|0", "x|1", "y|0", "y|1"]


def test_composite_strata_median():
    strata = {"r": {"strata": ["x", "x", "y", "y"]}}
    cond = {"r": [1, 2, 3, 4]}
    got = an._composite_strata_median(strata, cond, ("r",))
    want_buckets = an._median_bucket([1, 2, 3, 4])
    want = [f"{s}|{b}" for s, b in zip(["x", "x", "y", "y"], want_buckets)]
    assert got["r"]["strata"] == want
    assert all("|" in s for s in got["r"]["strata"])
    assert [s.split("|")[0] for s in got["r"]["strata"]] == ["x", "x", "y", "y"]


# ------------------------------------------------------ referent loaders

def test_load_predictor_seal_content_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        an._load_predictor_seal_content(tmp_path)


def test_load_predictor_seal_content_wrong_tag(tmp_path):
    p = bi.predictor_seal_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"sha256": "s", "tag": "wrong", "files": {}, "counts": {}}))
    with pytest.raises(ValueError, match="tag"):
        an._load_predictor_seal_content(tmp_path)


def test_load_rung_set_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        an._load_rung_set(tmp_path)


def test_load_rung_set_partition_check(tmp_path):
    p = bi.rung_set_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"R_OLMO": ["a", "b"], "R_CAP": ["a"], "R_EXTRA": [],
                             "per_rung": {}, "endpoint_file_sha256": {}}))
    with pytest.raises(ValueError, match="partition"):
        an._load_rung_set(tmp_path)


def test_check_rung_set_vs_endpoint_clean_and_mismatch():
    rung_set = {"per_rung": {"antonym": {"k": 12}, "clock24": {"k": 0}}}
    stage1 = {"antonym": {"correct": 12}, "clock24": {"correct": 0}}
    assert an._check_rung_set_vs_endpoint(rung_set, stage1) == []

    bad_stage1 = {"antonym": {"correct": 13}, "clock24": {"correct": 0}}
    fails = an._check_rung_set_vs_endpoint(rung_set, bad_stage1)
    assert len(fails) == 1 and "antonym" in fails[0]


def test_load_power_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        an._load_power(tmp_path)


def test_load_power_missing_declaration(tmp_path):
    p = bi.power_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"A": {"declared_status": "POWERED"}, "B": {}}))
    with pytest.raises(ValueError):
        an._load_power(tmp_path)


# --------------------------------------------------------------- run()

def test_run_on_the_real_tree_is_insufficient_data_no_crash():
    v = an.run()
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["tests"] is None and v["secondaries"] is None
    assert v["referents"]["failures"]
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2I
    assert v["licensed_sentence"] == an.LICENSED["INSUFFICIENT_DATA"]


def test_run_refuses_a_drifted_instrument_as_insufficient_data():
    v = an.run(tag_exists=lambda t: True, blob_sha=lambda tag, rel: "0" * 64)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("prereg tag" in f for f in v["referents"]["failures"])


def test_run_refuses_a_wrong_manifest_sha():
    v = an.run(manifest_sha="0" * 64)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any(f.startswith("checkpoint manifest") for f in v["referents"]["failures"])


# ------------------------------------------------------ fixture-pinned strings

def test_known_inputs_caveat_mentions_the_2i_boundary():
    assert "2h" in an.KNOWN_INPUTS_CAVEAT_2I
    assert "OLMo" in an.KNOWN_INPUTS_CAVEAT_2I
    assert "Hub" in an.KNOWN_INPUTS_CAVEAT_2I


def _design_doc_licenses() -> dict:
    """§6's four `- **WORLD:** ...` bullets, extracted from the design
    doc itself and normalized (wrapped lines joined with single spaces,
    a trailing period stripped) — the doc is the authority; this
    re-derives what a byte-for-byte-correct `LICENSED` must equal,
    rather than eyeballing the two side by side."""
    text = (bi.REPO / "experiment-2i-design.md").read_text(encoding="utf-8")
    section = re.search(r"## 6\. Licences.*?(?=\n## 7\.)", text, re.DOTALL).group(0)
    out = {}
    for m in re.finditer(r"- \*\*(\w+):\*\*\s*(.*?)(?=\n- |\Z)", section, re.DOTALL):
        label, body = m.group(1), m.group(2)
        norm = re.sub(r"\s+", " ", body).strip()
        if norm.endswith("."):
            norm = norm[:-1]
        out[label] = norm
    return out


def test_licensed_sentences_are_verbatim_design_text():
    doc = _design_doc_licenses()
    assert set(doc) == {"SHARED", "LINEAGE", "BOTH", "NEITHER"}
    for world in ("SHARED", "LINEAGE", "BOTH", "NEITHER"):
        assert an.LICENSED[world] == doc[world], world
    assert set(an.LICENSED) == set(an.WORLDS)


def test_calibration_sentence_states_non_calibration_of_the_union():
    assert "alpha .01" in an.CALIBRATION_SENTENCE_2I.replace("α", "alpha")
    assert "not" in an.CALIBRATION_SENTENCE_2I and "calibrated" in an.CALIBRATION_SENTENCE_2I
