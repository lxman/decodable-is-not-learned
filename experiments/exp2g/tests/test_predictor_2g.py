# experiments/exp2g/tests/test_predictor_2g.py
import hashlib
import json
import os

import numpy as np
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp2g import predictor_2g as pr
from experiments.exp2g import strata_2g as sg


def _fake_predictor(root, *, n=500):
    rng = np.random.default_rng(0)
    battery = bg.load_battery(bg.PREDICTOR_RUNGS)
    cells = {}
    for r in bg.PREDICTOR_RUNGS:
        cells[r] = {}
        for s in bg.PROBE_SIZES:
            cells[r][s] = {}
            for m in bg.MODES:
                sc = list(map(float, -rng.random(n)))
                cells[r][s][m] = {"site": [3, 1], "scores": sc, "eval_acc": 0.3,
                                  "eval_correct": 150, "n": n, "pred": ["1"] * n,
                                  "cv": {"per_site": {"(3, 1)": 0.3}, "best_acc": 0.3,
                                         "split": {"seed": 0, "holdout_frac": 0.2}},
                                  "n_sites": 14,
                                  "eval_rule": {"site": [3, 1], "scores": sc, "eval_acc": 0.3,
                                                "per_site": {"(3, 1)": 0.3}}}
    rec = {"rungs": list(bg.PREDICTOR_RUNGS), "sizes": list(bg.PROBE_SIZES),
           "modes": list(bg.MODES), "primary_size": bg.PRIMARY_SIZE,
           "cells": cells, "strata": sg.to_json(sg.build_table(battery)),
           "label_kinds": {r: "x" for r in bg.PREDICTOR_RUNGS},
           "gates": {}, "inputs": {}, "stack": {}, "git_sha": "deadbeef"}
    p = bg.predictor_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1, sort_keys=True))
    bg.predictor_sha_path(root).write_text(bg.sha256_file(p) + "  predictor.json\n")
    return rec


def test_load_predictor_shape_and_pins(tmp_path):
    _fake_predictor(tmp_path)
    pred = pr.load_predictor(bg.predictor_path(tmp_path), sha_pin=None)
    x = pr.cell_scores(pred, "antonym", "1b", "trained")
    assert x.shape == (500,) and np.all(x <= 0)
    assert pr.cell_scores(pred, "antonym", "1b", "trained", rule="eval").shape == (500,)
    with pytest.raises(ValueError):
        pr.load_predictor(bg.predictor_path(tmp_path), sha_pin="0" * 64)
    rec = json.loads(bg.predictor_path(tmp_path).read_text())
    rec["cells"]["antonym"]["1b"]["trained"]["scores"] = rec["cells"]["antonym"]["1b"]["trained"]["scores"][:10]
    bg.predictor_path(tmp_path).write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="scores"):
        pr.load_predictor(bg.predictor_path(tmp_path), sha_pin=None)


def test_require_seal(tmp_path):
    _fake_predictor(tmp_path)
    sha = pr.predictor_sha(tmp_path)
    ok = pr.require_seal(tmp_path, tag_exists=lambda t: t == bg.SEAL_TAG,
                         blob_sha=lambda t, rel: sha)
    assert ok["tag"] == bg.SEAL_TAG and ok["sha256"] == sha
    with pytest.raises(RuntimeError, match="tag"):
        pr.require_seal(tmp_path, tag_exists=lambda t: False, blob_sha=lambda t, rel: sha)
    with pytest.raises(RuntimeError, match="sha"):
        pr.require_seal(tmp_path, tag_exists=lambda t: True, blob_sha=lambda t, rel: "0" * 64)
    bg.predictor_sha_path(tmp_path).write_text("1" * 64 + "  predictor.json\n")
    with pytest.raises(RuntimeError, match="predictor_sha256.txt"):
        pr.require_seal(tmp_path, tag_exists=lambda t: True, blob_sha=lambda t, rel: sha)


def test_git_helpers_on_this_repo():
    assert pr.git_tag_exists("exp2f-closed") is True
    assert pr.git_tag_exists("no-such-tag-2g") is False
    s = pr.git_blob_sha256("exp2f-closed", "experiments/exp2f/labels_2f.py")
    assert s == bg.sha256_file(bg.EXP2F / "labels_2f.py")
    assert pr.git_blob_sha256("exp2f-closed", "experiments/exp2f/nope.py") is None


@pytest.mark.skipif(os.environ.get("EXP2G_SLOW") != "1", reason="set EXP2G_SLOW=1 (≈ 4 min of probe fits)")
def test_2f_gate_reproduces_committed_per_site_accuracies():
    g = pr.check_2f_gate()
    assert g == {"sub3_mid/410m": "PASS", "sub3_mid/1b": "PASS",
                 "arith_next/410m": "PASS", "arith_next/1b": "PASS"}
