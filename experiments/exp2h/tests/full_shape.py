# experiments/exp2h/tests/full_shape.py
"""Synthetic full-shape 2h trees. x is NEVER synthesized: every world
uses `battery_2h.sampler_counts("1b", R_69)` — the real, committed 2d
draws — as the primary predictor, exactly as the real run will. Only
the 6.9b sweep (a tree nobody has queried yet) is synthetic, built so
each rung's outcome ranking is a controlled function of x: positively
(CONFIRMED), independently (NOT-CONFIRMED), or negatively (NOT-
CONFIRMED, 'inverted'). Final-step counts equal m4's committed 6.9b
pins on all 34 rungs (so gate 1 passes on the world exactly as it must
on the real tree); every record sits in the production layout, read by
`analyze_2h.run` through the same loaders the real run uses. No
predictor synthesis is needed for the probe competitor either — 2g's
own committed, sealed predictor.json is read unchanged."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2H = Path(__file__).resolve().parents[1]
if str(EXP2H.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2H.parent.parent))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2h import analyze_2h as an  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402

_BATTERY = None
_MANIFEST = None
_SAMPLER = None


def battery():
    global _BATTERY
    if _BATTERY is None:
        _BATTERY = bg.load_battery()
    return _BATTERY


def manifest():
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = bh.load_manifest_69(bh.CHECKPOINTS_PATH_69, sha_pin=None)
    return _MANIFEST


def sampler_1b():
    global _SAMPLER
    if _SAMPLER is None:
        _SAMPLER = bh.sampler_counts("1b", bh.R_69)
    return _SAMPLER


def _w(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))


def _latent(rng, x, mode):
    """A per-rung ranking latent built from the REAL sampler counts x:
    'rank' ranks descending in x plus tie-breaking noise (drives
    CONFIRMED), 'independent' ignores x entirely (drives NOT-CONFIRMED),
    'inverted' ranks ascending in x (drives NOT-CONFIRMED, 'inverted').
    Ties in x (heavy zero-inflation on most rungs) are broken by the
    same noise draw regardless of mode, so only the x-dependence itself
    changes across worlds."""
    n = len(x)
    tie = rng.normal(size=n) * 0.01
    xa = np.asarray(x, dtype=np.float64)
    if mode == "rank":
        return xa + tie
    if mode == "inverted":
        return -xa + tie
    if mode == "independent":
        return rng.normal(size=n)
    raise ValueError(mode)


def write_world(root, *, mode="rank", missing_step=None, halt=False, seed=0) -> dict:
    root = Path(root)
    rng = np.random.default_rng(seed)
    bat = battery()
    man = manifest()
    samp = sampler_1b()
    steps = bh.trained_steps_69()
    n_steps = len(steps)

    first = {}
    for r in bt.RUNGS:
        n_pos = bh.FINAL_COUNT_PIN_69[r]
        if r in bh.R_69:
            w = _latent(rng, samp[r], mode)
        else:
            w = rng.normal(size=bt.N_ITEMS)
        order = np.argsort(-w)
        first[r] = {}
        for rank, i in enumerate(order[:n_pos]):
            k = int(rank * n_steps / max(1, n_pos))
            first[r][int(i)] = steps[k]

    if not halt:
        for step in bh.GRID_69:
            if step == missing_step:
                continue
            entry = bh.entry_69(man, step)
            if step != bh.FINAL_STEP_69:
                _w(bh.checkpoint_record_path_2h(root, step),
                   {"size": bh.SIZE, "step": step, "digest": f"d{step}",
                    "sha256": dict(entry["lfs_sha256"]),
                    "loading_info": {"missing_keys": 0, "unexpected_keys": 0,
                                     "mismatched_keys": 0}})
            for r in bt.RUNGS:
                cap = bat[r]
                bits = [int(step != 0 and i in first[r] and step >= first[r][i])
                        for i in range(bt.N_ITEMS)]
                if step == bh.FINAL_STEP_69:
                    assert sum(bits) == bh.FINAL_COUNT_PIN_69[r]
                conts = [f" {it['answer']}" if b else " zzz"
                         for b, it in zip(bits, cap["eval_items"])]
                _w(bh.record_path_2h(root, step, r),
                   {"rung": r, "size": bh.SIZE, "step": step, "revision": entry["revision"],
                    "commit": (an.an2g.pythia_sha(bh.SIZE) if step == bh.FINAL_STEP_69
                              else entry["commit"]),
                    "kind": entry["kind"], "files": entry["files"],
                    "items_sha256": cap["items_sha256"], "n": bt.N_ITEMS,
                    "correct": sum(bits), "bits": bits, "continuations": conts,
                    "answer_type": cap["answer_type"], "predictor_sha": bh.PREDICTOR_2G_SHA,
                    "seal_tag": bg.SEAL_TAG})
    g = {"size": bh.SIZE, "rungs": list(bt.RUNGS), "model_sha": an.an2g.pythia_sha(bh.SIZE),
         "counts_2c_path": dict(bh.FINAL_COUNT_PIN_69), "diffs_vs_pin": {},
         "digest_2c_path": "D" * 64, "digest_2h_path": ("E" if halt else "D") * 64,
         "continuation_diffs_2h_path": {r: 0 for r in bt.RUNGS},
         "continuations_compared_2h_path": {r: bt.N_ITEMS for r in bt.RUNGS},
         "prereg_tag": bh.PREREG_TAG_2H, "hub_step143000": man["hub_step143000"]}
    g["failures"] = an.gate1_failures_69(g)
    g["pass"] = not g["failures"]
    _w(bh.gate1_path_2h(root), g)
    if halt:
        bh.halt_marker_path_2h(root).write_text("synthetic halt\n")
    return {"tag_exists": lambda t: t == bh.PREREG_TAG_2H,
            "blob_sha": lambda tag, rel: bg.sha256_file(bg.REPO / rel)}


def run_world(root, seal, *, manifest_sha=None, referents_sha=None, power_sha=None,
              n_perm=200, n_boot=50) -> dict:
    """`referents_sha`/`power_sha` default to None (the manifest and the
    power record are 2h's OWN committed artifacts, unaffected by a
    synthetic world's tree) — W7/W8/W9 pass them explicitly so both
    refusal routes AND the passing route are exercised end to end
    through `run()` on a full-shape tree (freeze, attack-list item 12)."""
    return an.run(root=root, n_perm=n_perm, n_boot=n_boot, referents_sha=referents_sha,
                  power_sha=power_sha,
                  manifest_sha=(manifest_sha if manifest_sha is not None
                               else an.CHECKPOINTS_2H_SHA256),
                  **seal)


def world_specs() -> list:
    return [
        ("W1 CONFIRMED", dict(mode="rank"), {}, "CONFIRMED"),
        ("W2 NOT-CONFIRMED independent", dict(mode="independent"), {}, "NOT-CONFIRMED"),
        ("W3 NOT-CONFIRMED inverted", dict(mode="inverted"), {}, "NOT-CONFIRMED"),
        ("W4 INSUFFICIENT missing step",
         dict(mode="rank", missing_step=40000), {}, "INSUFFICIENT_DATA"),
        ("W5 INSUFFICIENT halted", dict(mode="rank", halt=True), {}, "INSUFFICIENT_DATA"),
        ("W6 INSUFFICIENT wrong manifest sha", dict(mode="rank"),
         {"manifest_sha": "0" * 64}, "INSUFFICIENT_DATA"),
    ]
