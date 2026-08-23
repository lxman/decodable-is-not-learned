# experiments/exp2g/tests/full_shape.py
"""Synthetic full-shape 2g trees: a sealed predictor file with
controlled association, a complete (or deliberately incomplete)
sweep tree whose final-step counts equal m4's pins (so gate 1 passes
on the world exactly as it must on the real tree), every record in
the production layout, read by analyze_2g.run through the same
loaders the real run uses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2G = Path(__file__).resolve().parents[1]
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2g import analyze_2g as an  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import labels_2g as lb  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402

_BATTERY = None
_MANIFEST = None


def battery():
    global _BATTERY
    if _BATTERY is None:
        _BATTERY = bg.load_battery()
    return _BATTERY


def manifest():
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = ck.load_manifest(bg.CHECKPOINTS_PATH, sha_pin=None)
    return _MANIFEST


def _cell(scores):
    s = [float(v) for v in scores]
    return {"site": [3, 1], "scores": s, "pred": ["1"] * len(s), "eval_correct": 0,
            "eval_acc": 0.3, "n": len(s), "n_sites": 14,
            "cv": {"per_site": {"(3, 1)": 0.3}, "best_acc": 0.3,
                   "split": {"seed": 0, "holdout_frac": 0.2}},
            "eval_rule": {"site": [3, 1], "scores": s, "eval_acc": 0.3,
                          "per_site": {"(3, 1)": 0.3}}}


def _latents(rng, strata_ids, *, difficulty_only):
    n = len(strata_ids)
    if difficulty_only:
        levels = sorted(set(strata_ids))
        eff = {s: 3.0 * k / max(1, len(levels) - 1) for k, s in enumerate(levels)}
        return np.array([eff[s] for s in strata_ids]) + 0.05 * rng.normal(size=n)
    return rng.normal(size=n)


def write_world(root, *, assoc=0.8, twin_assoc=0.0, difficulty_only=False, invert=False,
                sizes=("2.8b",), missing_step=None, halt=False, seal_ok=True, seed=0) -> dict:
    root = Path(root)
    rng = np.random.default_rng(seed)
    bat = battery()
    table = sg.build_table({r: bat[r] for r in bg.PREDICTOR_RUNGS})
    man = manifest()
    sign = -1.0 if invert else 1.0
    noise = 0.3 if difficulty_only else np.sqrt(max(1e-9, 1 - assoc ** 2))
    z, w = {}, {}
    cells = {}
    for r in bg.PREDICTOR_RUNGS:
        zr = _latents(rng, table[r]["strata"], difficulty_only=difficulty_only)
        z[r] = zr
        w[r] = zr + noise * rng.normal(size=len(zr))
        cells[r] = {}
        for s in bg.PROBE_SIZES:
            a = assoc if difficulty_only is False else 1.0
            x_tr = sign * a * zr + noise * rng.normal(size=len(zr))
            x_tw = twin_assoc * zr + np.sqrt(max(1e-9, 1 - twin_assoc ** 2)) * rng.normal(size=len(zr))
            cells[r][s] = {"trained": _cell(-np.abs(x_tr.min()) + x_tr - 1.0),
                           "untrained": _cell(-np.abs(x_tw.min()) + x_tw - 1.0)}
    rec = {"rungs": list(bg.PREDICTOR_RUNGS), "sizes": list(bg.PROBE_SIZES),
           "modes": list(bg.MODES), "primary_size": bg.PRIMARY_SIZE, "cells": cells,
           "strata": sg.to_json(table),
           "label_kinds": {r: lb.KIND_OF[r] for r in bg.PREDICTOR_RUNGS},
           "gates": {"synthetic": True}, "inputs": {}, "stack": {"torch": "synthetic"},
           "git_sha": "synthetic"}
    p = bg.predictor_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1, sort_keys=True))
    sha = bg.sha256_file(p)
    bg.predictor_sha_path(root).write_text(f"{sha}  predictor.json\n")
    bg.strata_path(root).write_text(json.dumps(sg.to_json(table)))
    seal = {"tag": bg.SEAL_TAG, "sha256": sha}
    for size in sizes:
        steps = bg.trained_steps(size)
        rungs = bg.sweep_rungs(size)
        first = {}
        for r in rungs:
            n_pos = bg.FINAL_COUNT_PIN[size][r]
            if r in bg.PREDICTOR_RUNGS:
                order = np.argsort(-w[r])          # highest latent first
            else:
                order = np.arange(bg.N_ITEMS)
            first[r] = {}
            for rank, i in enumerate(order[:n_pos]):
                k = int(rank * len(steps) / max(1, n_pos))   # earlier for higher w
                first[r][int(i)] = steps[k]
        for step in bg.GRID[size]:
            if step == missing_step:
                continue
            entry = ck.entry_for(man, size, step)
            if step != bg.FINAL_STEP:
                _w(bg.checkpoint_record_path(root, size, step),
                   {"size": size, "step": step, "digest": f"d{step}",
                    "sha256": dict(entry["lfs_sha256"]),
                    "loading_info": {"missing_keys": 0, "unexpected_keys": 0,
                                     "mismatched_keys": 0}})
            for r in rungs:
                cap = bat[r]
                bits = [int(step != 0 and i in first[r] and step >= first[r][i])
                        for i in range(bg.N_ITEMS)]
                if step == bg.FINAL_STEP:
                    assert sum(bits) == bg.FINAL_COUNT_PIN[size][r]
                conts = [f" {it['answer']}" if b else " zzz"
                         for b, it in zip(bits, cap["eval_items"])]
                _w(bg.record_path(root, size, step, r),
                   {"rung": r, "size": size, "step": step, "revision": entry["revision"],
                    "commit": (an.pythia_sha(size) if step == bg.FINAL_STEP else entry["commit"]),
                    "kind": entry["kind"], "files": entry["files"],
                    "items_sha256": cap["items_sha256"], "n": bg.N_ITEMS,
                    "correct": sum(bits), "bits": bits, "continuations": conts,
                    "answer_type": cap["answer_type"], "predictor_sha": sha,
                    "seal_tag": bg.SEAL_TAG})
        g = {"size": size, "rungs": list(rungs), "model_sha": an.pythia_sha(size),
             "counts_2c_path": dict(bg.FINAL_COUNT_PIN[size]), "diffs_vs_pin": {},
             "digest_2c_path": "D" * 64, "digest_2g_path": ("E" if halt else "D") * 64,
             "continuation_diffs_2g_path": {r: 0 for r in rungs}, "seal": seal,
             "hub_step143000": man[size]["hub_step143000"]}
        g["failures"] = an.gate1_failures(g, size)
        g["pass"] = not g["failures"]
        _w(bg.gate1_path(root, size), g)
        if halt:
            bg.halt_marker_path(root, size).write_text("synthetic halt\n")
    blob = sha if seal_ok else "0" * 64
    return {"tag_exists": lambda t: t == bg.SEAL_TAG, "blob_sha": lambda t, rel: blob}


def _w(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))


def run_world(root, seal, *, n_perm=300, n_boot=50) -> dict:
    return an.run(root=root, n_perm=n_perm, n_boot=n_boot, referents_sha=None,
                  with_2d_secondaries=False, **seal)


def world_specs() -> list:
    return [
        ("W1 FORECAST", dict(assoc=0.8), "FORECAST"),
        ("W2 SURFACE twin forecasts too", dict(assoc=0.8, twin_assoc=0.8), "SURFACE"),
        ("W3 DIFFICULTY-ONLY", dict(difficulty_only=True), "DIFFICULTY-ONLY"),
        ("W4 NO-FORECAST independent", dict(assoc=0.0), "NO-FORECAST"),
        ("W5 inverted -> NO-FORECAST", dict(assoc=0.8, invert=True), "NO-FORECAST"),
        ("W6 INSUFFICIENT missing step", dict(assoc=0.8, missing_step=40000), "INSUFFICIENT_DATA"),
        ("W7 INSUFFICIENT halted", dict(assoc=0.8, halt=True), "INSUFFICIENT_DATA"),
        ("W8 INSUFFICIENT seal mismatch", dict(assoc=0.8, seal_ok=False), "INSUFFICIENT_DATA"),
        ("W9 FORECAST with 12b replication", dict(assoc=0.8, sizes=("2.8b", "12b")), "FORECAST"),
    ]
