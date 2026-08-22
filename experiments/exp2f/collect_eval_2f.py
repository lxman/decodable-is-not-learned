"""Exp 2f's ONLY model contact (design §9), run AFTER the tag on
Michael's word: residual-stream activations for the 500 eval items of
sub3_mid and arith_next at 410m and 1b, on the trained model and on
its untrained twin (2b's `load_pythia(untrained=True, seed=0)`), at
2c's two positions, fp16 — 2b/2c's collector verbatim in method (the
three renderers are byte-identical; `screen._render_prompt` and
`screen._position_indices` are used for both rungs).

Gate 1 (continuity), per (size, mode): the first CONTINUITY_N probe
items of each rung are re-collected and compared to the COMMITTED
rows of the 2b/2c activation file — the eval activations must come
from the same network (the twin's seeded init on this stack) and the
same stack as the probe-item activations the probe is trained on. The
record carries the max absolute and relative deviations; the analyzer
re-derives pass/fail from them against the pinned tolerance.

Usage: python -m experiments.exp2f.collect_eval_2f <size> <trained|untrained>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2F = Path(__file__).resolve().parent
EXPERIMENTS = EXP2F.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2f import analyze_2f as a  # noqa: E402
from experiments.exp2f import labels_2f as lb  # noqa: E402
from experiments.exp2f import make_referents_2f as mk  # noqa: E402
from experiments.exp2c.run import screen  # noqa: E402


def stack_info() -> dict:
    import torch
    import transformers
    return {"torch": torch.__version__, "transformers": transformers.__version__}


def collect_items(model, tok, cap, items, *, batch_size=32, device="mps"):
    """2b/2c's collector: X [n, n_layers, 2, d] fp16 for `items`."""
    import torch
    shots = [tuple(s) for s in cap["shots"]]
    prompts = [screen._render_prompt(it["question"], shots) for it in items]
    old_side = tok.padding_side
    tok.padding_side = "right"
    chunks = []
    try:
        for i in range(0, len(prompts), batch_size):
            chunk = prompts[i:i + batch_size]
            enc = tok(chunk, return_tensors="pt", padding=True,
                      add_special_tokens=False).to(device)
            with torch.no_grad():
                out = model(**enc, output_hidden_states=True)
            hs = torch.stack(out.hidden_states, dim=0)
            for b, prompt in enumerate(chunk):
                q_idx, p_idx = screen._position_indices(tok, prompt)
                sel = hs[:, b, [q_idx, p_idx], :]
                chunks.append(sel.to(torch.float16).cpu().numpy())
    finally:
        tok.padding_side = old_side
    return np.stack(chunks)


def compare_rows(new: np.ndarray, committed: np.ndarray) -> dict:
    """Max absolute and relative deviation between re-collected rows
    and the committed rows (fp16 → float32 for the arithmetic)."""
    new = np.asarray(new, dtype=np.float32)
    com = np.asarray(committed, dtype=np.float32)
    if new.shape != com.shape:
        raise ValueError(f"compare_rows: shapes {new.shape} vs {com.shape}")
    diff = np.abs(new - com)
    scale = np.maximum(np.abs(com), 1e-3)
    return {"n_compared": int(new.shape[0]),
            "max_abs_diff": float(diff.max()),
            "max_rel_diff": float((diff / scale).max()),
            "identical": bool(np.array_equal(new, com))}


def run_one(size: str, mode: str, *, root=a.EXP2F, device="mps") -> dict:
    from models import load_pythia
    untrained = mode == "untrained"
    tok, model = load_pythia(size, untrained=untrained, seed=a.UNTRAINED_SEED,
                             device=device)
    stack = stack_info()
    battery = {r: bt.load_item_file(r) for r in lb.RUNGS}
    per_rung = {}
    for rung in lb.RUNGS:
        cap = battery[rung]
        # gate 1 first: the committed probe rows must be reproduced
        com_path = mk.probe_npz_path(size, mode, rung)
        z = np.load(com_path, allow_pickle=False)
        com = z["X"][:a.CONTINUITY_N]
        new = collect_items(model, tok, cap, cap["probe_items"][:a.CONTINUITY_N],
                            device=device)
        per_rung[rung] = {"items": list(range(a.CONTINUITY_N)),
                          **compare_rows(new, com)}
        # then the eval items
        X = collect_items(model, tok, cap, cap["eval_items"], device=device)
        meta = a.eval_meta(size=size, mode=mode, rung=rung,
                           n_layers=int(X.shape[1]), stack=stack)
        p = a.eval_npz_path(root, size, mode, rung)
        p.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(p, X=X.astype(np.float16),
                            y=np.array([str(it["answer"]) for it in
                                        cap["eval_items"]]),
                            meta=json.dumps(meta))
        print(f"[2f] {size}/{mode}/{rung}: eval {X.shape}, continuity "
              f"{per_rung[rung]}", flush=True)
    rec = a.continuity_record(size=size, mode=mode, per_rung=per_rung,
                              stack=stack)
    cp = a.continuity_path(root, size, mode)
    cp.parent.mkdir(parents=True, exist_ok=True)
    cp.write_text(json.dumps(rec, indent=1))
    print(f"[2f] {size}/{mode}: continuity pass={rec['pass']}", flush=True)
    return rec


if __name__ == "__main__":
    size, mode = sys.argv[1], sys.argv[2]
    assert size in lb.SIZES and mode in mk.MODES
    run_one(size, mode)
