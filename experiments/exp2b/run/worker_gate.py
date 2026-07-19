"""Distributed-worker determinism gate (design §6): a box's results count
ONLY after it reproduces the Mac reference fixture bit-for-bit on the fields
that matter (accuracies are prediction counts; any BLAS/solver divergence
that flips a single prediction fails the gate — exclude the box, don't debug).

  python -m run.worker_gate --reference   (Mac: writes results/worker_gate_reference.json)
  python -m run.worker_gate               (worker: computes + compares; exit 0/1)

The fixture is a seeded synthetic structure world through the REAL
probe_starved path (reduced n_perm for speed; determinism, not power).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from probe_starved import probe_starved
from splits import SplitParams

EXP_DIR = Path(__file__).resolve().parent.parent
REF = EXP_DIR / "results" / "worker_gate_reference.json"
COMPARE_KEYS = ("present", "accuracy", "null_p", "null_mean", "null_std",
                "margin", "best_layer", "best_token", "chance", "ci95")


def fixture() -> dict:
    rng = np.random.default_rng(20260719)
    n, d, n_vals, n_cls = 1200, 48, 40, 5
    vals = [str(v) for v in range(n_vals)]
    bases = [(vals[int(rng.integers(n_vals))],) for _ in range(n)]
    table = {v: str(i % n_cls) for i, v in enumerate(vals)}
    y = np.array([table[b[0]] for b in bases], dtype=object)
    X = rng.normal(size=(n, 2, 2, d)).astype(np.float32)
    for i in range(n):
        X[i, 1, 1, int(y[i])] += 2.0      # moderate signal: solver must WORK
    act = {(l, s): X[:, l, s, :] for l in range(2) for s in range(2)}
    r = probe_starved(act, y, bases,
                      split_params=SplitParams(holdout_frac=0.2,
                                               min_holdout_values=5,
                                               min_val_items=100),
                      checkpoint_id="worker-gate-fixture", seed=0, n_perm=300)
    return {k: r[k] for k in COMPARE_KEYS}


def main() -> None:
    import platform
    import numpy
    import sklearn
    got = fixture()
    env = {"python": platform.python_version(), "numpy": numpy.__version__,
           "sklearn": sklearn.__version__, "machine": platform.machine(),
           "node": platform.node()}
    if "--reference" in sys.argv:
        REF.parent.mkdir(exist_ok=True)
        REF.write_text(json.dumps({"env": env, "fixture": got}, indent=1))
        print(f"[gate] reference written by {env}")
        return
    ref = json.loads(REF.read_text())
    ok = ref["fixture"] == got
    print(f"[gate] this box: {env}")
    print(f"[gate] reference: {ref['env']}")
    if ok:
        print("[gate] PASS — bit-identical fixture; this box's results count")
    else:
        for k in COMPARE_KEYS:
            if ref["fixture"][k] != got[k]:
                print(f"[gate] MISMATCH {k}: ref={ref['fixture'][k]} got={got[k]}")
        print("[gate] FAIL — exclude this box (design §6: exclude, don't debug)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
