"""Synthetic full-shape 2f trees for the freeze rule: every §6
terminal executed end to end through the frozen loaders.

A world is one root holding BOTH layouts the analyzer reads: 2d's
(main/pilot records + draws, argmax records, for the four cells,
written by 2d's own world writers with rows built here so the LABEL
and EXACT matches are controlled separately) and 2f's own
(activations_probe/ and activations_eval/ npz files, continuity
records, probes_m3 records, items/). Activations are synthetic and
small (7 layers × 2 positions × 12 dims; family {0,3,6} × 2): the
label is one-hot-encoded at site (3, 1) with a chosen strength (0 =
silent), on the trained model and/or its twin. Probe-item bases and
committed probe_labels are the REAL item files' (so 2b's starving
split is the real split), eval-item answers are the real answers.
Every literal the real run pins is taken FROM THE WORLD by
`pins_from_world` through the same builders the production pins were
made with.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

EXP2F = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2F.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d.tests import full_shape as fs2d  # noqa: E402
from experiments.exp2f import analyze_2f as a  # noqa: E402
from experiments.exp2f import labels_2f as lb  # noqa: E402
from experiments.exp2f import make_referents_2f as mk  # noqa: E402
from experiments.exp2f import probe_2f as pb  # noqa: E402

RUNGS, SIZES = lb.RUNGS, lb.SIZES
FILLER = fs2d.FILLER
N_LAYERS, D, SITE = 7, 12, (3, 1)
FAKE_STACK = fs2d.FAKE_STACK

_BATTERY = None


def battery():
    global _BATTERY
    if _BATTERY is None:
        _BATTERY = {r: bt.load_item_file(r) for r in RUNGS}
    return _BATTERY


def model_sha(size):
    from models import PYTHIA_SHAS
    return PYTHIA_SHAS[size]


# ------------------------------------------------------------- emissions

def label_only_number(rung, answer: str) -> str:
    """A number with the PRIMARY label of `answer` and a different
    value: +100/−100 keeps sub3_mid's middle digit, +10 keeps
    arith_next's last digit."""
    n = int(answer)
    if rung == "sub3_mid":
        m = n + 100 if n + 100 <= 999 else n - 100
    else:
        m = n + 10
    assert m != n and lb.answer_label(lb.PRIMARY[rung], str(m)) == \
        lb.answer_label(lb.PRIMARY[rung], answer)
    return str(m)


def synthetic_rows(rung, cap, *, seed, dps, exact, label_only) -> list:
    """`exact` draws equal to the answer, `label_only` draws with the
    right label and wrong value, the rest FILLER; spread one per item
    then wrapping, exact first."""
    n = len(cap["eval_items"])
    per_e, per_l = [0] * n, [0] * n
    for k in range(exact):
        per_e[k % n] += 1
    for k in range(label_only):
        per_l[(k + 250) % n] += 1
    rows = []
    for i, it in enumerate(cap["eval_items"]):
        e = min(per_e[i], dps)
        l = min(per_l[i], dps - e)
        draws = [str(it["answer"])] * e + \
            [" " + label_only_number(rung, str(it["answer"])) + "\n\nQ:"] * l + \
            [FILLER] * (dps - e - l)
        rows.append({"item": i, "draws": {str(seed): draws}})
    return rows


def write_cells(root, spec, *, verify) -> dict:
    """spec[(rung, size)] = {"main": (exact, label_only), "pilot": (...),
    "argmax": (exact, label_only)}. Returns the exact counts written."""
    caps = battery()
    written = {}
    for (rung, size), s in spec.items():
        for tier in ("main", "pilot"):
            e, l = s.get(tier, (0, 0))
            t = a2d.TIERS[tier]
            rows = synthetic_rows(rung, caps[rung], seed=t["seed"],
                                  dps=t["draws_per_seed"], exact=e, label_only=l)
            fs2d.write_sampling_cell(root, tier, size, rung, rows, verify=verify)
            written[(rung, size, tier)] = e
        e, l = s.get("argmax", (0, 0))
        conts = []
        for i, it in enumerate(caps[rung]["eval_items"]):
            if i < e:
                conts.append(" " + str(it["answer"]) + "\n\nQ:")
            elif i < e + l:
                conts.append(" " + label_only_number(rung, str(it["answer"])) + "\n")
            else:
                conts.append(FILLER)
        _write_argmax(root, size, rung, conts, verify=verify)
        written[(rung, size, "argmax")] = e
    return written


def _write_argmax(root, size, rung, conts, *, verify):
    cap = battery()[rung]
    got = sum(verify(c, str(it["answer"]), "number")
              for c, it in zip(conts, cap["eval_items"]))
    rec = {"rung": rung, "size": size, "mode": a2d.MODE, "tier": "argmax",
           "n_items": len(conts), "answer_type": "number",
           "n_shots": bt.N_SHOTS, "dtype": a2d.ARGMAX_DTYPE,
           "untrained_seed": None, "model_sha": model_sha(size),
           "items_sha256": bt.ITEMS_SHA_PIN[rung],
           "max_new_tokens": bt.max_new_tokens(rung),
           "continuations": conts, "correct": int(got),
           "acc": got / len(conts), "redecode_diffs": None,
           "stack": FAKE_STACK}
    p = a2d.argmax_record_path(root, size, rung)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1))


# ----------------------------------------------------------- activations

def _encode(rng, labels, *, strength, n_layers=N_LAYERS, d=D, site=SITE):
    n = len(labels)
    X = rng.normal(size=(n, n_layers, 2, d)).astype(np.float32)
    if strength:
        for i, lab in enumerate(labels):
            X[i, site[0], site[1], int(lab)] += strength
    return X.astype(np.float16)


def write_probe_npz(root, size, mode, rung, *, strength, seed) -> Path:
    """Synthetic probe-item activations: y = the COMMITTED probe_label
    (2c's), the primary label encoded at SITE."""
    cap = battery()[rung]
    items = cap["probe_items"]
    y_committed = np.array([it["probe_label"] for it in items], dtype=object)
    y_primary = [lb.answer_label(lb.PRIMARY[rung], it["answer"]) for it in items]
    X = _encode(np.random.default_rng(seed), y_primary, strength=strength)
    meta = {"size": size, "mode": mode, "capability": rung,
            "sha": model_sha(size), "n_items": len(items),
            "n_layers": N_LAYERS}
    if mode == "untrained":
        meta["untrained_seed"] = 0
    p = mk.probe_npz_path(size, mode, rung, probe_root=root)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(p, X=X, y=y_committed.astype(str), meta=json.dumps(meta))
    return p


def write_eval_npz(root, size, mode, rung, *, strength, seed) -> Path:
    cap = battery()[rung]
    items = cap["eval_items"]
    y_primary = [lb.answer_label(lb.PRIMARY[rung], it["answer"]) for it in items]
    X = _encode(np.random.default_rng(seed), y_primary, strength=strength)
    meta = a.eval_meta(size=size, mode=mode, rung=rung, n_layers=N_LAYERS,
                       stack=FAKE_STACK)
    p = a.eval_npz_path(root, size, mode, rung)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(p, X=X, y=np.array([str(it["answer"]) for it in items]),
                        meta=json.dumps(meta))
    return p


def write_continuity(root, size, mode, *, max_abs=0.0, max_rel=0.0) -> Path:
    rec = a.continuity_record(size=size, mode=mode, per_rung={
        r: {"items": list(range(a.CONTINUITY_N)), "n_compared": a.CONTINUITY_N,
            "max_abs_diff": max_abs, "max_rel_diff": max_rel}
        for r in RUNGS}, stack=FAKE_STACK)
    p = a.continuity_path(root, size, mode)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1))
    return p


def write_m3_record(root, size, rung) -> Path:
    """The world's 'committed' m3 record: what 2b's starved probe reads
    on the world's own probe npz — the gate then compares the
    analyzer's re-derivation to it (the real records are 2c's)."""
    cap = battery()[rung]
    act, y, _ = a.load_npz_map(mk.probe_npz_path(size, "trained", rung,
                                                 probe_root=root))
    bases = [tuple(it["basis"]) for it in cap["probe_items"]]
    out = pb.starved_accuracies(act, y, bases, a.SPLIT_PARAMS[rung], seed=0)
    rec = {"stage": "m3", "size": size, "capability": rung, "seed": 0,
           "accuracy": out["accuracy"], "best_layer": out["best_site"][0],
           "best_token": out["best_site"][1], "split": out["split"],
           "n_candidates": len(out["per_site"]), "synthetic": True}
    p = mk.m3_record_path(size, rung, probe_root=root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1))
    return p


def write_items(root):
    for r in RUNGS:
        p = Path(root) / "items" / f"{r}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(bt.items_path(r).read_bytes())


# --------------------------------------------------------------- pins

def pins_from_world(root) -> dict:
    root = Path(root)
    manifest_path = root / "referents_2f.json"
    mk.build(manifest_path, base=root, d2_root=root, probe_root=root)
    sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    exact = {}
    for tier in ("main", "pilot"):
        for size in SIZES:
            for rung in RUNGS:
                r = json.loads(a2d.tier_record_path(root, tier, size, rung)
                               .read_text())
                seed = str(a2d.TIERS[tier]["seed"])
                exact[(rung, size, tier)] = int(r["per_seed_tallies"][seed]
                                                ["full_string"])
    for size in SIZES:
        for rung in RUNGS:
            exact[(rung, size, "argmax")] = int(json.loads(
                a2d.argmax_record_path(root, size, rung).read_text())["correct"])
    m3 = {}
    for size in SIZES:
        for rung in RUNGS:
            rec = json.loads(mk.m3_record_path(size, rung, probe_root=root)
                             .read_text())
            m3[(rung, size)] = a.m3_pin_from_record(rec)
    npz = {}
    for size in SIZES:
        for rung in RUNGS:
            for mode in mk.MODES:
                p = mk.probe_npz_path(size, mode, rung, probe_root=root)
                npz[(rung, size, mode)] = hashlib.sha256(p.read_bytes()).hexdigest()
    return {"manifest_path": manifest_path, "manifest_sha_pin": sha,
            "exact_pin": exact, "m3_pin": m3, "npz_pin": npz}


# --------------------------------------------------------------- worlds

def build_world(root, *, cells, probe_strength, twin_strength=None,
                continuity=None, mutate=None, run=True) -> dict:
    """cells: spec for write_cells; probe_strength[(rung, size)] for the
    trained model (0 = silent); twin_strength likewise (default 0);
    continuity[(size, mode)] = (max_abs, max_rel) (default clean)."""
    root = Path(root)
    verify = a2d.load_verify()
    twin_strength = twin_strength or {}
    continuity = continuity or {}
    write_items(root)
    write_cells(root, cells, verify=verify)
    k = 0
    for size in SIZES:
        for rung in RUNGS:
            for mode in mk.MODES:
                s = probe_strength.get((rung, size), 0.0) if mode == "trained" \
                    else twin_strength.get((rung, size), 0.0)
                write_probe_npz(root, size, mode, rung, strength=s, seed=100 + k)
                write_eval_npz(root, size, mode, rung, strength=s, seed=200 + k)
                k += 1
        for mode in mk.MODES:
            ma, mr = continuity.get((size, mode), (0.0, 0.0))
            write_continuity(root, size, mode, max_abs=ma, max_rel=mr)
    for size in SIZES:
        for rung in RUNGS:
            write_m3_record(root, size, rung)
    pins = pins_from_world(root)
    if mutate is not None:
        mutate(root, pins)
    if not run:
        return pins
    v = a.run(root, d2_root=root, probe_root=root,
              manifest_path=pins["manifest_path"],
              manifest_sha_pin=pins["manifest_sha_pin"],
              exact_pin=pins["exact_pin"], m3_pin=pins["m3_pin"],
              npz_pin=pins["npz_pin"])
    v["_pins"] = pins
    return v


def full_cells(*, arith=(300, 6000), arith_argmax=(20, 80), sub=(0, 0)):
    """A cells spec: arith_next with `arith` (exact, label_only) in main,
    an eighth in pilot, `arith_argmax` in argmax; sub3_mid `sub`."""
    spec = {}
    for size in SIZES:
        spec[("arith_next", size)] = {"main": arith,
                                      "pilot": (arith[0] // 8, arith[1] // 8),
                                      "argmax": arith_argmax}
        spec[("sub3_mid", size)] = {"main": sub, "pilot": (sub[0] // 8, sub[1] // 8),
                                    "argmax": (0, 0)}
    return spec


# ------------------------------------------------------------ mutators

def mutate_manifest(root, pins):
    p = a2d.tier_record_path(root, "pilot", "410m", "sub3_mid")
    p.write_text(p.read_text() + "\n")


def mutate_exact_pin(root, pins):
    pins["exact_pin"][("arith_next", "1b", "main")] += 1


def mutate_continuity_bad(root, pins):
    write_continuity(root, "1b", "untrained", max_abs=1.0, max_rel=0.5)
    pins.update(pins_from_world(root))


def world_specs() -> list:
    strong = {(r, s): 4.0 for r in RUNGS for s in SIZES}
    arith_only = {("arith_next", s): 4.0 for s in SIZES}
    silent = {}
    specs = []
    specs.append(("W1 LADDER probe+sampler+argmax on arith_next",
                  {"cells": full_cells(), "probe_strength": arith_only},
                  "LADDER"))
    specs.append(("W2 INVERTED sampler without probe",
                  {"cells": full_cells(), "probe_strength": silent},
                  "INVERTED"))
    specs.append(("W3 SILENT nothing anywhere",
                  {"cells": full_cells(arith=(0, 0), arith_argmax=(0, 0)),
                   "probe_strength": silent},
                  "SILENT"))
    specs.append(("W4 INSUFFICIENT_DATA manifest byte changed",
                  {"cells": full_cells(), "probe_strength": arith_only,
                   "mutate": mutate_manifest},
                  "INSUFFICIENT_DATA"))
    specs.append(("W5 INSUFFICIENT_DATA both arith_next cells void",
                  {"cells": full_cells(), "probe_strength": strong,
                   "twin_strength": arith_only},
                  "INSUFFICIENT_DATA"))
    specs.append(("W6 INVERTED argmax without sampler",
                  {"cells": full_cells(arith=(0, 0), arith_argmax=(20, 80)),
                   "probe_strength": arith_only},
                  "INVERTED"))
    specs.append(("W7 LADDER probe only",
                  {"cells": full_cells(arith=(0, 0), arith_argmax=(0, 0)),
                   "probe_strength": arith_only},
                  "LADDER"))
    specs.append(("W8 INSUFFICIENT_DATA continuity gate",
                  {"cells": full_cells(), "probe_strength": arith_only,
                   "mutate": mutate_continuity_bad},
                  "INSUFFICIENT_DATA"))
    specs.append(("W9 INSUFFICIENT_DATA exact-match pin",
                  {"cells": full_cells(), "probe_strength": arith_only,
                   "mutate": mutate_exact_pin},
                  "INSUFFICIENT_DATA"))
    return specs
