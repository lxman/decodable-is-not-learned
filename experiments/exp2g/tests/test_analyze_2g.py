# experiments/exp2g/tests/test_analyze_2g.py
"""analyze_2g: the tree on literal inputs, gate-1 re-derivation, the
step-record refusals, outcomes, rung level, primary on synthetic cells."""
import json

import numpy as np
import pytest

from experiments.exp2g import analyze_2g as an
from experiments.exp2g import battery_2g as bg
from experiments.exp2g import labels_2g as lb
from experiments.exp2g import stats_2g as st


def _prim(T, p, p_raw, p_twin):
    return {"stratified": {"T": T, "p": p}, "raw": {"T": T, "p": p_raw},
            "twin": {"T": 0.0, "p": p_twin}}


def test_tree_is_complete_and_exclusive():
    v = an.verdict_tree_2g(["x"], None)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert an.verdict_tree_2g([], _prim(.20, .001, .001, .5))["verdict"] == "FORECAST"
    assert an.verdict_tree_2g([], _prim(.20, .001, .001, .01))["verdict"] == "SURFACE"
    assert an.verdict_tree_2g([], _prim(.05, .5, .001, .5))["verdict"] == "DIFFICULTY-ONLY"
    assert an.verdict_tree_2g([], _prim(.02, .5, .5, .5))["verdict"] == "NO-FORECAST"
    v = an.verdict_tree_2g([], _prim(.05, .001, .001, .5))     # detected below the bar
    assert v["verdict"] == "NO-FORECAST" and "below the effect bar" in v["reason"]
    v = an.verdict_tree_2g([], _prim(-.3, .999, .999, .5))
    assert v["verdict"] == "NO-FORECAST" and "inverted" in v["reason"]
    # exactly at the boundaries
    assert an.verdict_tree_2g([], _prim(.10, .0099, .5, .05))["verdict"] == "FORECAST"
    assert an.verdict_tree_2g([], _prim(.10, .01, .5, .05))["verdict"] == "NO-FORECAST"
    assert set(an.WORLDS) == {"INSUFFICIENT_DATA", "FORECAST", "SURFACE",
                              "DIFFICULTY-ONLY", "NO-FORECAST"}


def _gate_rec(size="2.8b", **over):
    rungs = bg.sweep_rungs(size)
    rec = {"size": size, "rungs": list(rungs),
           "counts_2c_path": dict(bg.FINAL_COUNT_PIN[size]),
           "digest_2c_path": "d" * 64, "digest_2g_path": "d" * 64,
           "continuation_diffs_2g_path": {r: 0 for r in rungs},
           "model_sha": an.pythia_sha(size), "seal": {"sha256": "s" * 64}}
    rec.update(over)
    return rec


def test_gate1_rederived_not_trusted():
    assert an.gate1_failures(_gate_rec(), "2.8b") == []
    bad = _gate_rec(); bad["counts_2c_path"]["antonym"] += 1
    assert any("antonym" in f for f in an.gate1_failures(bad, "2.8b"))
    bad = _gate_rec(digest_2g_path="e" * 64)
    assert any("digest" in f for f in an.gate1_failures(bad, "2.8b"))
    bad = _gate_rec(); bad["continuation_diffs_2g_path"]["sub3_mid"] = 3
    assert any("continuation" in f for f in an.gate1_failures(bad, "2.8b"))
    bad = _gate_rec(model_sha="0" * 40)
    assert an.gate1_failures(bad, "2.8b")
    bad = _gate_rec(); bad["counts_2c_path"].pop("odd6")
    assert an.gate1_failures(bad, "2.8b")
    bad = _gate_rec(); bad["pass"] = True; bad["digest_2g_path"] = "e" * 64
    assert an.gate1_failures(bad, "2.8b")
    assert an.gate1_failures(_gate_rec("12b"), "12b") == []


def _step_rec(cap, *, step=1000, rung="antonym", size="2.8b", entry=None, seal="s" * 64,
              verify=None):
    from experiments.exp2d import analyze_2d as a2d
    verify = verify or a2d.load_verify()
    conts = [f" {it['answer']}" if i % 3 == 0 else " zzz" for i, it in enumerate(cap["eval_items"])]
    bits = [int(verify(c, it["answer"], cap["answer_type"])) for c, it in zip(conts, cap["eval_items"])]
    entry = entry or {"revision": "step1000", "commit": "c" * 40, "kind": "bin",
                      "files": ["pytorch_model.bin"], "lfs_sha256": {"pytorch_model.bin": "f" * 64}}
    return {"rung": rung, "size": size, "step": step, "revision": entry["revision"],
            "commit": entry["commit"], "items_sha256": cap["items_sha256"], "n": 500,
            "correct": sum(bits), "bits": bits, "continuations": conts,
            "predictor_sha": seal, "seal_tag": bg.SEAL_TAG, "answer_type": cap["answer_type"]}


def test_step_record_refusals():
    cap = bg.load_battery(["antonym"])["antonym"]
    from experiments.exp2d import analyze_2d as a2d
    verify = a2d.load_verify()
    entry = {"revision": "step1000", "commit": "c" * 40, "kind": "bin", "files": ["pytorch_model.bin"],
             "lfs_sha256": {"pytorch_model.bin": "f" * 64}}
    ok = _step_rec(cap, entry=entry)
    kw = dict(size="2.8b", step=1000, rung="antonym", cap=cap, entry=entry, verify_fn=verify,
              seal_sha="s" * 64)
    assert an.step_record_failures(ok, **kw) == []
    r = dict(ok); r["correct"] += 1
    assert any("correct" in f for f in an.step_record_failures(r, **kw))
    r = dict(ok); r["bits"] = list(ok["bits"]); r["bits"][0] ^= 1; r["correct"] = sum(r["bits"])
    assert any("re-verif" in f for f in an.step_record_failures(r, **kw))
    r = dict(ok); r["commit"] = "e" * 40
    assert any("commit" in f for f in an.step_record_failures(r, **kw))
    r = dict(ok); r["predictor_sha"] = "t" * 64
    assert any("seal" in f for f in an.step_record_failures(r, **kw))
    r = dict(ok); r["items_sha256"] = "0" * 64
    assert an.step_record_failures(r, **kw)
    r = dict(ok); r["continuations"] = ok["continuations"][:499]
    assert an.step_record_failures(r, **kw)


def test_outcomes_and_rung_level():
    steps = bg.trained_steps("2.8b")
    sweep = {}
    for s in bg.GRID["2.8b"]:
        sweep[s] = {"r": {"bits": [1 if (s >= 30000 and i < 300) or (s == 1000 and i == 0) else 0
                                   for i in range(500)], "correct": 0}}
        sweep[s]["r"]["correct"] = sum(sweep[s]["r"]["bits"])
    out = an.outcomes(sweep, "2.8b", rungs=("r",))
    o = out["r"]
    n_ge = sum(1 for s in steps if s >= 30000)
    assert o["y"][5] == n_ge and o["y"][0] == n_ge + 1 and o["y"][400] == 0
    assert o["first"][0] == 1000 and o["first"][5] == 30000 and o["first"][400] is None
    assert o["stab"][0] == 30000 and o["last"][400] is None
    assert o["n_pos"] == 300 and o["counts_by_step"][0] == 0
    rl = an.rung_level(out, "2.8b", {"r": 0.25}, rungs=("r",))
    assert rl["r"]["s_star"] == 30000 and rl["r"]["final_clears"] is True
    assert rl["r"]["transient_clears"] == []


def _cells(rng, n=300, rho=0.7, n_pos=80):
    z = rng.normal(size=n)
    x = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
    w = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
    y = np.zeros(n, int); y[np.argsort(w)[-n_pos:]] = 1 + np.arange(n_pos) * 21 // n_pos
    return x, y


def test_primary_on_synthetic_predictor():
    rng = np.random.default_rng(0)
    pred = {"cells": {}}
    out, strata = {}, {}
    for r in ("a", "b"):
        x, y = _cells(rng)
        xt = rng.normal(size=len(x))
        pred["cells"][r] = {"1b": {"trained": {"scores": list(x), "eval_rule": {"scores": list(x)}},
                                   "untrained": {"scores": list(xt), "eval_rule": {"scores": list(xt)}}}}
        out[r] = {"y": list(y), "n_pos": int((y > 0).sum()), "first": [None] * len(y)}
        strata[r] = {"strata": [str(i % 3) for i in range(len(y))]}
    prim = an.primary(pred, out, strata, size_pred="1b", rungs=("a", "b"), n_perm=300, seed=0,
                      n_boot=50)
    assert prim["stratified"]["T"] > 0.3 and prim["stratified"]["p"] < 0.01
    assert prim["twin"]["p"] > 0.05 and prim["raw"]["p"] < 0.01
    assert prim["eligible"] == ["a", "b"] and prim["thin"] == []
    assert set(prim["per_rung"]) == {"a", "b"} and "ci" in prim["per_rung"]["a"]
    assert an.verdict_tree_2g([], prim)["verdict"] == "FORECAST"


def test_label_floors_for_rung_level():
    battery = bg.load_battery()
    lbf = lb.floor_table({r: battery[r] for r in bg.PREDICTOR_RUNGS})
    assert set(lbf) == set(bg.PREDICTOR_RUNGS) and all(0 < lbf[r]["floor"] <= 1 for r in bg.R_28)
    with pytest.raises(KeyError):
        lb.floor_table({"antonym": battery["antonym"]})


def test_primary_thin_and_no_eligible():
    rng = np.random.default_rng(1)
    pred = {"cells": {}}
    out, strata = {}, {}
    for r, n_pos in (("a", 80), ("b", 5)):
        x, y = _cells(rng, n_pos=n_pos)
        pred["cells"][r] = {"1b": {"trained": {"scores": list(x), "eval_rule": {"scores": list(x)}},
                                   "untrained": {"scores": list(x), "eval_rule": {"scores": list(x)}}}}
        out[r] = {"y": list(y), "n_pos": int((y > 0).sum()), "first": [None] * len(y)}
        strata[r] = {"strata": [str(i % 3) for i in range(len(y))]}
    prim = an.primary(pred, out, strata, size_pred="1b", rungs=("a", "b"), n_perm=50, seed=0,
                      n_boot=20)
    assert prim["eligible"] == ["a"] and prim["thin"] == ["b"]

    pred2 = {"cells": {}}
    out2, strata2 = {}, {}
    for r in ("c", "d"):
        x, y = _cells(rng, n_pos=5)
        pred2["cells"][r] = {"1b": {"trained": {"scores": list(x), "eval_rule": {"scores": list(x)}},
                                    "untrained": {"scores": list(x), "eval_rule": {"scores": list(x)}}}}
        out2[r] = {"y": list(y), "n_pos": int((y > 0).sum()), "first": [None] * len(y)}
        strata2[r] = {"strata": [str(i % 3) for i in range(len(y))]}
    with pytest.raises(ValueError, match="no eligible"):
        an.primary(pred2, out2, strata2, size_pred="1b", rungs=("c", "d"), n_perm=50, seed=0,
                  n_boot=20)


def test_outcomes_never_counts_step0():
    # step 0 fires on every item, no trained step fires on any item:
    # y must be 0 everywhere (trained_steps excludes step 0), even
    # though counts_by_step still records step 0's own hit count.
    sweep = {}
    for s in bg.GRID["2.8b"]:
        bits = [1] * bg.N_ITEMS if s == 0 else [0] * bg.N_ITEMS
        sweep[s] = {"r": {"bits": bits, "correct": sum(bits)}}
    out = an.outcomes(sweep, "2.8b", rungs=("r",))
    o = out["r"]
    assert o["y"] == [0] * bg.N_ITEMS
    assert o["first"] == [None] * bg.N_ITEMS and o["last"] == [None] * bg.N_ITEMS
    assert o["n_pos"] == 0
    assert o["counts_by_step"][0] == bg.N_ITEMS


def test_load_sweep_refuses_a_missing_record(tmp_path, monkeypatch):
    monkeypatch.setattr(bg, "sweep_rungs", lambda size: ("r",))
    manifest = {"2.8b": {"entries": {"1000": {"lfs_sha256": {}}}}}
    # a VALID checkpoint record for the step: under the real code the
    # per-rung "record missing" raise fires first and this is never
    # reached, but it must be a PASSING record so a mutant that inerts
    # the per-rung check doesn't fall through to the checkpoint-record
    # check's different message instead (that would still fail the
    # suite, but for the wrong reason — mutant #46's note).
    cp = bg.checkpoint_record_path(tmp_path, "2.8b", 1000)
    cp.parent.mkdir(parents=True, exist_ok=True)
    cp.write_text(json.dumps({"sha256": {}, "loading_info": {"missing_keys": 0,
                                                              "unexpected_keys": 0,
                                                              "mismatched_keys": 0}}))
    with pytest.raises(FileNotFoundError, match="sweep record missing"):
        an.load_sweep(tmp_path, "2.8b", {"r": {}}, lambda *a, **k: True,
                      manifest=manifest, seal_sha="s", steps=(1000,))


def test_rung_level_transient_clears():
    steps = bg.trained_steps("2.8b")
    sweep = {}
    for s in bg.GRID["2.8b"]:
        bits = ([1] * 300 + [0] * 200) if s == 30000 else [0] * 500
        sweep[s] = {"r": {"bits": bits, "correct": sum(bits)}}
    out = an.outcomes(sweep, "2.8b", rungs=("r",))
    rl = an.rung_level(out, "2.8b", {"r": 0.25}, rungs=("r",))
    assert rl["r"]["s_star"] == 30000
    assert rl["r"]["final_clears"] is False
    assert rl["r"]["transient_clears"] == [30000]
