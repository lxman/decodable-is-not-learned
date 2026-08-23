# experiments/exp2g/collect_eval_2g.py
"""Exp 2g stage 1 — the predictor-side model contact (design §9),
run AFTER `exp2g-preregistered` on Michael's word: residual-stream
activations for the 500 eval items of the 11 predictor rungs at 410m
and 1b, trained and twin, 2f's collector verbatim in method.

Continuity (2f's gate 1), per (size, mode): the first CONTINUITY_N
probe items of each rung re-collected and compared to the COMMITTED
rows of the 2b/2c activation file. Gate P (design §5): the two 2f
rungs' eval activations re-collected and compared to 2f's COMMITTED
eval files within the same tolerance. The analyzer and the predictor
builder re-derive pass/fail from the recorded diffs.

Usage: python -m experiments.exp2g.collect_eval_2g <size> <trained|untrained>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2G = Path(__file__).resolve().parent
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2f import analyze_2f as a2f  # noqa: E402
from experiments.exp2f import collect_eval_2f as c2f  # noqa: E402

CONTINUITY_N = 8
RTOL, ATOL = 1e-2, 1e-2
GATE_P_RUNGS = ("sub3_mid", "arith_next")
collect_items = c2f.collect_items
compare_rows = c2f.compare_rows
stack_info = c2f.stack_info


def eval_meta(*, size, mode, rung, n_layers, stack) -> dict:
    from models import PYTHIA_SHAS
    return {"size": size, "mode": mode, "capability": rung,
            "which_items": "eval_items", "n_items": bg.N_ITEMS,
            "n_layers": int(n_layers), "model_sha": PYTHIA_SHAS[size],
            "untrained_seed": bg.UNTRAINED_SEED if mode == "untrained" else None,
            "items_sha256": bg.ITEMS_SHA_PIN_OF(rung),
            "positions": ["question_end", "prompt_end"], "dtype": "float16",
            "n_shots": bg.N_SHOTS, "collector": "exp2g", "stack": stack}


def continuity_record(*, size, mode, per_rung, gate_p, stack) -> dict:
    from models import PYTHIA_SHAS
    rec = {"size": size, "mode": mode, "model_sha": PYTHIA_SHAS[size],
           "untrained_seed": bg.UNTRAINED_SEED if mode == "untrained" else None,
           "n_items_per_rung": CONTINUITY_N,
           "tolerance": {"rtol": RTOL, "atol": ATOL},
           "rungs": {r: dict(per_rung[r]) for r in per_rung},
           "gate_p": {r: dict(gate_p[r]) for r in gate_p}, "stack": stack}
    rec["pass"] = continuity_failures(rec, size=size, mode=mode) == []
    return rec


def _within(d) -> bool:
    return (d.get("max_rel_diff", 1e9) <= RTOL and d.get("max_abs_diff", 1e9) <= ATOL)


def continuity_failures(rec: dict, *, size, mode) -> list:
    """Re-derived from the diffs; the runner's `pass` is ignored."""
    from models import PYTHIA_SHAS
    bad = []
    if rec.get("size") != size or rec.get("mode") != mode:
        bad.append(f"continuity {size}/{mode}: record is for "
                   f"{rec.get('size')}/{rec.get('mode')}")
    if rec.get("model_sha") != PYTHIA_SHAS.get(size):
        bad.append(f"continuity {size}/{mode}: model_sha not 2b's pin")
    want_seed = bg.UNTRAINED_SEED if mode == "untrained" else None
    if rec.get("untrained_seed") != want_seed:
        bad.append(f"continuity {size}/{mode}: untrained_seed "
                   f"{rec.get('untrained_seed')!r} != {want_seed!r}")
    for r in bg.PREDICTOR_RUNGS:
        d = rec.get("rungs", {}).get(r)
        if not d:
            bad.append(f"continuity {size}/{mode}: no record for {r}")
            continue
        if d.get("n_compared") != CONTINUITY_N:
            bad.append(f"continuity {size}/{mode}/{r}: {d.get('n_compared')} "
                       f"items compared, pinned {CONTINUITY_N}")
        if not _within(d):
            bad.append(f"continuity {size}/{mode}/{r}: re-collected probe items "
                       f"deviate (rel {d.get('max_rel_diff')}, abs "
                       f"{d.get('max_abs_diff')}) beyond the tolerance")
    for r in GATE_P_RUNGS:
        d = rec.get("gate_p", {}).get(r)
        if not d:
            bad.append(f"gate P {size}/{mode}: no comparison for {r}")
            continue
        if d.get("n_compared") != bg.N_ITEMS or not _within(d):
            bad.append(f"gate P {size}/{mode}/{r}: 2f's committed eval activations "
                       f"not reproduced (n {d.get('n_compared')}, rel "
                       f"{d.get('max_rel_diff')}, abs {d.get('max_abs_diff')})")
    return bad


def run_one(size: str, mode: str, *, root=EXP2G, device="mps") -> dict:
    from models import load_pythia
    tok, model = load_pythia(size, untrained=(mode == "untrained"),
                             seed=bg.UNTRAINED_SEED, device=device)
    stack = stack_info()
    battery = bg.load_battery(bg.PREDICTOR_RUNGS)
    per_rung, gate_p = {}, {}
    for rung in bg.PREDICTOR_RUNGS:
        cap = battery[rung]
        z = np.load(bg.probe_npz_path(size, mode, rung), allow_pickle=False)
        com = z["X"][:CONTINUITY_N]
        new = collect_items(model, tok, cap, cap["probe_items"][:CONTINUITY_N],
                            device=device)
        per_rung[rung] = {"items": list(range(CONTINUITY_N)), **compare_rows(new, com)}
        X = collect_items(model, tok, cap, cap["eval_items"], device=device)
        if rung in GATE_P_RUNGS:
            z2 = np.load(a2f.eval_npz_path(a2f.EXP2F, size, mode, rung),
                         allow_pickle=False)
            gate_p[rung] = compare_rows(X, z2["X"])
        meta = eval_meta(size=size, mode=mode, rung=rung, n_layers=int(X.shape[1]),
                         stack=stack)
        p = bg.eval_npz_path(root, size, mode, rung)
        p.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(p, X=X.astype(np.float16),
                            y=np.array([str(it["answer"]) for it in cap["eval_items"]]),
                            meta=json.dumps(meta))
        print(f"[2g] {size}/{mode}/{rung}: eval {X.shape}, continuity "
              f"{per_rung[rung]}", flush=True)
    rec = continuity_record(size=size, mode=mode, per_rung=per_rung, gate_p=gate_p,
                            stack=stack)
    cp = bg.continuity_path(root, size, mode)
    cp.parent.mkdir(parents=True, exist_ok=True)
    cp.write_text(json.dumps(rec, indent=1))
    print(f"[2g] {size}/{mode}: continuity pass={rec['pass']}", flush=True)
    return rec


if __name__ == "__main__":
    size, mode = sys.argv[1], sys.argv[2]
    assert size in bg.PROBE_SIZES and mode in bg.MODES
    run_one(size, mode)
