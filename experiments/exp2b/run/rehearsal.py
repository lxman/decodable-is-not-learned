"""PRE-FREEZE GATE REHEARSAL (design §7, ledgered): probe_starved against Exp
2's collected activations, where the ground truth is already known from the
instrument diagnostics. NOT Exp 2b data — a mechanics + calibration run.

Cases (410m, seed 0): mod7 untrained (known pure lookup — group-split
diagnostic collapsed it to chance) and mod7 trained (known ALSO lookup at this
scale — collapsed to 0.009 on held-out operands). A working starved instrument
must read BOTH as silent (present=False). Timing per unit is the fit-cost
calibration for the M2/M3 campaign estimate (first run of the workload shape
is the calibration run — the ledgered lesson).

Bases are parsed from Exp 2's committed mod7 items (first operand), matching
the probe labels stored in the npz (first operand mod 7 — a pure function of
the basis, the worst case for lookup and therefore the sharpest rehearsal).

Usage: python -m run.rehearsal   (writes results/rehearsal/*.json)
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import numpy as np

from probe_starved import probe_starved
from splits import SplitParams

EXP_DIR = Path(__file__).resolve().parent.parent
EXP2_DIR = EXP_DIR.parent / "exp2"
LAYER_STRIDE = 3   # the same frozen candidate family as the design specifies


def thin(act):
    n_layers = 1 + max(l for l, _ in act)
    keep = set(range(0, n_layers, LAYER_STRIDE)) | {n_layers - 1}
    return {(l, s): X for (l, s), X in act.items() if l in keep}


def load_exp2_activations(size, mode, cap):
    sys.path.insert(0, str(EXP2_DIR))          # rehearsal-only, subprocess-scoped
    from activations import activations_path, load_activation_map
    return load_activation_map(activations_path(size, mode, cap))


def main() -> None:
    items = json.loads(
        (EXP2_DIR / "battery" / "items" / "mod7.json").read_text())["probe_items"]
    bases = [(re.findall(r"\d+", it["question"])[0],) for it in items]

    out_dir = EXP_DIR / "results" / "rehearsal"
    out_dir.mkdir(parents=True, exist_ok=True)
    params = SplitParams(n_holdout=18)

    for mode, expect in (("untrained", "silent (pure lookup world)"),
                         ("trained", "silent (lookup at this scale)")):
        act, y, meta = load_exp2_activations("410m", mode, "mod7")
        act = thin(act)
        assert len(bases) == len(y)
        t0 = time.perf_counter()
        r = probe_starved(act, y, bases, split_params=params,
                          checkpoint_id=f"REHEARSAL exp2 410m {mode} mod7",
                          seed=0)
        dt = time.perf_counter() - t0
        r["wall_seconds"] = round(dt, 1)
        r["expectation"] = expect
        (out_dir / f"410m_{mode}_mod7_seed0.json").write_text(
            json.dumps(r, indent=1))
        print(f"[rehearsal] 410m/{mode}/mod7: present={r['present']} "
              f"acc={r['accuracy']:.4f} null_mean={r['null_mean']:.4f} "
              f"margin={r['margin']:.4f} n_val={r['split']['n_val']} "
              f"wall={dt:.0f}s  (expect {expect})", flush=True)

    print("[rehearsal] done", flush=True)


if __name__ == "__main__":
    main()
