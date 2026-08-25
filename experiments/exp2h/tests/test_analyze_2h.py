# experiments/exp2h/tests/test_analyze_2h.py
"""analyze_2h: the tree on literal inputs, gate-1 re-derivation, the
step-record refusals through load_sweep_69, outcomes_69/rung_level_69,
primary_2h on synthetic cells, load_power_2h."""
import json

import numpy as np
import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import analyze_2g as an2g
from experiments.exp2g import battery_2g as bg
from experiments.exp2h import analyze_2h as an
from experiments.exp2h import battery_2h as bh


def _prim(T, p):
    return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}}


def test_tree_is_complete_and_exclusive():
    v = an.verdict_tree_2h(["x"], None)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert an.verdict_tree_2h([], _prim(.20, .001))["verdict"] == "CONFIRMED"
    assert an.verdict_tree_2h([], _prim(.02, .5))["verdict"] == "NOT-CONFIRMED"
    v = an.verdict_tree_2h([], _prim(.05, .001))     # detected below the bar
    assert v["verdict"] == "NOT-CONFIRMED" and "below the effect bar" in v["reason"]
    v = an.verdict_tree_2h([], _prim(-.3, .999))
    assert v["verdict"] == "NOT-CONFIRMED" and "inverted" in v["reason"]
    # exactly at the boundaries
    assert an.verdict_tree_2h([], _prim(.10, .0099))["verdict"] == "CONFIRMED"
    assert an.verdict_tree_2h([], _prim(.10, .01))["verdict"] == "NOT-CONFIRMED"
    assert an.verdict_tree_2h([], _prim(.099, .001))["verdict"] == "NOT-CONFIRMED"
    assert set(an.WORLDS) == {"INSUFFICIENT_DATA", "CONFIRMED", "NOT-CONFIRMED"}


def _gate_rec(**over):
    rungs = list(bt.RUNGS)
    rec = {"size": "6.9b", "rungs": rungs,
           "counts_2c_path": dict(bh.FINAL_COUNT_PIN_69),
           "digest_2c_path": "d" * 64, "digest_2h_path": "d" * 64,
           "continuation_diffs_2h_path": {r: 0 for r in rungs},
           "model_sha": an2g.pythia_sha("6.9b"), "prereg_tag": bh.PREREG_TAG_2H}
    rec.update(over)
    return rec


def test_gate1_rederived_not_trusted():
    assert an.gate1_failures_69(_gate_rec()) == []
    bad = _gate_rec(); bad["counts_2c_path"] = dict(bad["counts_2c_path"])
    bad["counts_2c_path"]["antonym"] += 1
    assert any("antonym" in f for f in an.gate1_failures_69(bad))
    bad = _gate_rec(digest_2h_path="e" * 64)
    assert any("digest" in f for f in an.gate1_failures_69(bad))
    bad = _gate_rec(); bad["continuation_diffs_2h_path"] = dict(bad["continuation_diffs_2h_path"])
    bad["continuation_diffs_2h_path"]["sub3_mid"] = 3
    assert any("continuation" in f for f in an.gate1_failures_69(bad))
    bad = _gate_rec(model_sha="0" * 40)
    assert an.gate1_failures_69(bad)
    bad = _gate_rec(); bad["counts_2c_path"] = dict(bad["counts_2c_path"])
    bad["counts_2c_path"].pop("odd6")
    assert an.gate1_failures_69(bad)
    bad = _gate_rec(prereg_tag="not-the-tag")
    assert any("prereg_tag" in f for f in an.gate1_failures_69(bad))
    bad = _gate_rec(); bad["rungs"] = list(bt.RUNGS)[:-1]
    assert an.gate1_failures_69(bad)
    bad = _gate_rec(size="2.8b")
    assert an.gate1_failures_69(bad)


def _entry(commit="c" * 40):
    return {"revision": "step1000", "commit": commit, "kind": "bin",
            "files": ["pytorch_model.bin"], "lfs_sha256": {"pytorch_model.bin": "f" * 64}}


def test_load_sweep_69_reuses_step_record_failures(tmp_path, monkeypatch):
    from experiments.exp2d import analyze_2d as a2d
    cap = bg.load_battery(["antonym"])["antonym"]
    verify = a2d.load_verify()
    entry = _entry()
    conts = [f" {it['answer']}" if i % 3 == 0 else " zzz"
            for i, it in enumerate(cap["eval_items"])]
    bits = [int(verify(c, it["answer"], cap["answer_type"]))
           for c, it in zip(conts, cap["eval_items"])]
    rec = {"rung": "antonym", "size": "6.9b", "step": 1000, "revision": entry["revision"],
          "commit": entry["commit"], "items_sha256": cap["items_sha256"], "n": bt.N_ITEMS,
          "correct": sum(bits), "bits": bits, "continuations": conts,
          "predictor_sha": bh.PREDICTOR_2G_SHA, "seal_tag": bg.SEAL_TAG,
          "answer_type": cap["answer_type"]}
    p = bh.record_path_2h(tmp_path, 1000, "antonym")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec))
    cp = bh.checkpoint_record_path_2h(tmp_path, 1000)
    cp.write_text(json.dumps({"sha256": dict(entry["lfs_sha256"]),
                              "loading_info": {"missing_keys": 0, "unexpected_keys": 0,
                                               "mismatched_keys": 0}}))
    manifest = {"entries": {"1000": entry}}
    battery = {"antonym": cap}
    got = an.load_sweep_69(tmp_path, battery, verify, manifest=manifest,
                           seal_sha=bh.PREDICTOR_2G_SHA, steps=(1000,), rungs=("antonym",))
    assert got[1000]["antonym"]["correct"] == sum(bits)

    # a mutated record (wrong seal) is refused via an2g.step_record_failures
    bad_rec = dict(rec); bad_rec["predictor_sha"] = "t" * 64
    p.write_text(json.dumps(bad_rec))
    with pytest.raises(ValueError):
        an.load_sweep_69(tmp_path, battery, verify, manifest=manifest,
                         seal_sha=bh.PREDICTOR_2G_SHA, steps=(1000,), rungs=("antonym",))


def test_load_sweep_69_refuses_a_missing_record(tmp_path):
    manifest = {"entries": {"1000": _entry()}}
    with pytest.raises(FileNotFoundError, match="sweep record missing"):
        an.load_sweep_69(tmp_path, {"antonym": {}}, lambda *a, **k: True,
                         manifest=manifest, seal_sha="s", steps=(1000,), rungs=("antonym",))


def test_load_sweep_69_refuses_a_missing_checkpoint_record(tmp_path):
    from experiments.exp2d import analyze_2d as a2d
    cap = bg.load_battery(["antonym"])["antonym"]
    verify = a2d.load_verify()
    entry = _entry()
    conts = [" zzz"] * bt.N_ITEMS
    rec = {"rung": "antonym", "size": "6.9b", "step": 1000, "revision": entry["revision"],
          "commit": entry["commit"], "items_sha256": cap["items_sha256"], "n": bt.N_ITEMS,
          "correct": 0, "bits": [0] * bt.N_ITEMS, "continuations": conts,
          "predictor_sha": bh.PREDICTOR_2G_SHA, "seal_tag": bg.SEAL_TAG,
          "answer_type": cap["answer_type"]}
    p = bh.record_path_2h(tmp_path, 1000, "antonym")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec))
    manifest = {"entries": {"1000": entry}}
    with pytest.raises(FileNotFoundError, match="checkpoint record missing"):
        an.load_sweep_69(tmp_path, {"antonym": cap}, verify, manifest=manifest,
                         seal_sha=bh.PREDICTOR_2G_SHA, steps=(1000,), rungs=("antonym",))


def test_load_sweep_69_refuses_a_torn_json_record(tmp_path):
    # a syntactically invalid/truncated step record — e.g. a partial
    # write cut off mid-campaign — must not raise past load_sweep_69
    # uncollected: json.JSONDecodeError is a ValueError subclass, so
    # analyze_2h.run()'s call site (which wraps load_sweep_69 in
    # `collect()`) turns it into a referent failure and the analyzer
    # delivers INSUFFICIENT_DATA with the reason, not a crash.
    manifest = {"entries": {"1000": _entry()}}
    p = bh.record_path_2h(tmp_path, 1000, "antonym")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('{"rung": "antonym", "size": "6.9b", "step": 1000, "corr')  # torn mid-write

    with pytest.raises(json.JSONDecodeError):
        an.load_sweep_69(tmp_path, {"antonym": {}}, lambda *a, **k: True,
                         manifest=manifest, seal_sha="s", steps=(1000,), rungs=("antonym",))

    val, failures = an.collect(
        lambda: an.load_sweep_69(tmp_path, {"antonym": {}}, lambda *a, **k: True,
                                 manifest=manifest, seal_sha="s", steps=(1000,),
                                 rungs=("antonym",)),
        "sweep 6.9b")
    assert val is None
    assert len(failures) == 1
    assert "sweep 6.9b" in failures[0] and "JSONDecodeError" in failures[0]

    tree = an.verdict_tree_2h(failures, None)
    assert tree["verdict"] == "INSUFFICIENT_DATA"
    assert "JSONDecodeError" in tree["reason"]


def test_outcomes_69_and_rung_level_69():
    steps = bh.trained_steps_69()
    sweep = {}
    for s in bh.GRID_69:
        bits = [1 if (s >= 30000 and i < 300) or (s == 1000 and i == 0) else 0
               for i in range(bt.N_ITEMS)]
        sweep[s] = {"r": {"bits": bits, "correct": sum(bits)}}
    out = an.outcomes_69(sweep, rungs=("r",))
    o = out["r"]
    n_ge = sum(1 for s in steps if s >= 30000)
    assert o["y"][5] == n_ge and o["y"][0] == n_ge + 1 and o["y"][400] == 0
    assert o["first"][0] == 1000 and o["first"][5] == 30000 and o["first"][400] is None
    assert o["stab"][0] == 30000 and o["last"][400] is None
    assert o["n_pos"] == 300 and o["counts_by_step"][0] == 0
    rl = an.rung_level_69(out, {"r": 0.25}, rungs=("r",))
    assert rl["r"]["s_star"] == 30000 and rl["r"]["final_clears"] is True
    assert rl["r"]["transient_clears"] == []


def test_rung_level_69_transient_clears():
    sweep = {}
    for s in bh.GRID_69:
        bits = ([1] * 300 + [0] * (bt.N_ITEMS - 300)) if s == 30000 else [0] * bt.N_ITEMS
        sweep[s] = {"r": {"bits": bits, "correct": sum(bits)}}
    out = an.outcomes_69(sweep, rungs=("r",))
    rl = an.rung_level_69(out, {"r": 0.25}, rungs=("r",))
    assert rl["r"]["s_star"] == 30000
    assert rl["r"]["final_clears"] is False
    assert rl["r"]["transient_clears"] == [30000]


def _cells(rng, n=300, rho=0.7, n_pos=80):
    z = rng.normal(size=n)
    x = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
    w = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
    y = np.zeros(n, int); y[np.argsort(w)[-n_pos:]] = 1 + np.arange(n_pos) * 21 // n_pos
    return x, y


def test_primary_2h_on_synthetic_predictor_has_no_twin():
    rng = np.random.default_rng(0)
    pred = {"cells": {}}
    out, strata = {}, {}
    for r in ("a", "b"):
        x, y = _cells(rng)
        pred["cells"][r] = {"1b": {"trained": {"scores": list(x), "eval_rule": {"scores": list(x)}}}}
        out[r] = {"y": list(y), "n_pos": int((y > 0).sum()), "first": [None] * len(y)}
        strata[r] = {"strata": [str(i % 3) for i in range(len(y))]}
    prim = an.primary_2h(pred, out, strata, size_pred="1b", rungs=("a", "b"), n_perm=300,
                         seed=0, n_boot=50)
    assert "twin" not in prim
    assert prim["stratified"]["T"] > 0.3 and prim["stratified"]["p"] < 0.01
    assert prim["raw"]["p"] < 0.01
    assert prim["eligible"] == ["a", "b"] and prim["thin"] == []
    assert set(prim["per_rung"]) == {"a", "b"} and "ci" in prim["per_rung"]["a"]
    assert an.verdict_tree_2h([], prim)["verdict"] == "CONFIRMED"


def test_primary_2h_thin_and_no_eligible():
    rng = np.random.default_rng(1)
    pred = {"cells": {}}
    out, strata = {}, {}
    for r, n_pos in (("a", 80), ("b", 5)):
        x, y = _cells(rng, n_pos=n_pos)
        pred["cells"][r] = {"1b": {"trained": {"scores": list(x), "eval_rule": {"scores": list(x)}}}}
        out[r] = {"y": list(y), "n_pos": int((y > 0).sum()), "first": [None] * len(y)}
        strata[r] = {"strata": [str(i % 3) for i in range(len(y))]}
    prim = an.primary_2h(pred, out, strata, size_pred="1b", rungs=("a", "b"), n_perm=50,
                         seed=0, n_boot=20)
    assert prim["eligible"] == ["a"] and prim["thin"] == ["b"]

    pred2 = {"cells": {}}
    out2, strata2 = {}, {}
    for r in ("c", "d"):
        x, y = _cells(rng, n_pos=5)
        pred2["cells"][r] = {"1b": {"trained": {"scores": list(x), "eval_rule": {"scores": list(x)}}}}
        out2[r] = {"y": list(y), "n_pos": int((y > 0).sum()), "first": [None] * len(y)}
        strata2[r] = {"strata": [str(i % 3) for i in range(len(y))]}
    with pytest.raises(ValueError, match="no eligible"):
        an.primary_2h(pred2, out2, strata2, size_pred="1b", rungs=("c", "d"), n_perm=50,
                     seed=0, n_boot=20)


def test_outcomes_69_never_counts_step0():
    sweep = {}
    for s in bh.GRID_69:
        bits = [1] * bt.N_ITEMS if s == 0 else [0] * bt.N_ITEMS
        sweep[s] = {"r": {"bits": bits, "correct": sum(bits)}}
    out = an.outcomes_69(sweep, rungs=("r",))
    o = out["r"]
    assert o["y"] == [0] * bt.N_ITEMS
    assert o["first"] == [None] * bt.N_ITEMS and o["last"] == [None] * bt.N_ITEMS
    assert o["n_pos"] == 0
    assert o["counts_by_step"][0] == bt.N_ITEMS


def test_load_power_2h_missing_declared_status(tmp_path):
    p = tmp_path / "power_2h.json"
    p.write_text(json.dumps({"declaration": "x"}))
    import hashlib
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="declared_status"):
        an.load_power_2h(path=p, sha_pin=sha)


def test_load_power_2h_wrong_sha(tmp_path):
    p = tmp_path / "power_2h.json"
    p.write_text(json.dumps({"declared_status": "POWERED", "declaration": "x", "n_sim": 10}))
    with pytest.raises(ValueError, match="pinned"):
        an.load_power_2h(path=p, sha_pin="0" * 64)


def test_require_prereg_2h():
    assert an.require_prereg_2h(tag_exists=lambda t: t == bh.PREREG_TAG_2H) == \
        {"tag": bh.PREREG_TAG_2H}
    with pytest.raises(RuntimeError, match="refusing"):
        an.require_prereg_2h(tag_exists=lambda t: False)


def test_run_catches_sweep_load_failure_as_insufficient_data_not_a_crash():
    # Task 3 (build): against the real, unmodified repo tree — no 6.9b
    # sweep has run yet — `manifest`/`battery`/`verify_fn`/`pred` all
    # load cleanly from committed files, so `_sweep_ready` is True and
    # `run()` reaches the `collect(lambda: load_sweep_69(...), ...)`
    # call site; `load_sweep_69` then raises FileNotFoundError on the
    # first (step, rung) it reads, since no sweep record exists on
    # disk. This is the exact call site the mutation harness's "strip
    # the collect() wrapping at run()'s load_sweep_69 call site" mutant
    # targets (Task 2 re-review finding): the existing torn-JSON test
    # exercises `load_sweep_69` and a bare `collect()` call in
    # isolation, never `run()` itself, so it does not catch a stripped
    # wrapping AT THIS call site. Without collect() here, the
    # FileNotFoundError would propagate uncaught out of run() instead
    # of becoming a referent failure — this test fails with an
    # unhandled exception under that mutant and passes clean otherwise.
    v = an.run()
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any(f.startswith(f"sweep {bh.SIZE}: FileNotFoundError")
              for f in v["referents"]["failures"])
