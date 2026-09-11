# experiments/exp4/run/preflight_4.py
"""Exp 4 preflight (design §3.7 gate 1's ulp question, §3.10 dial k;
Task 3 resolution 8) — the ONE sanctioned model-contact check before
the campaign: (a) `ladder_pythia_2.8b` (already-cached weights, 2b's
loader path) collected TWICE, in two separate model calls, on
`antonym` and `add3_mid`, the SAME pinned batching — prints per-rung
seconds, peak MPS memory (`torch.mps.driver_allocated_memory()`), the
fp16 finiteness of the hidden states, and whether the two collections
are BYTE-IDENTICAL and whether their `set_tables_4` are identical (if
not, gate 1's identity requirement has to be relaxed to a k-NN-set
identity plus a disclosed tolerance BEFORE the tag — design §3.7 — a
call for Michael, not this script); (b) `load_step_4("comma_7b",
10000)` end to end (download, candidate-file load, tensor digest
compared against `committed_step_digest_4`), then freed. Applies
`check_frozen_4()` but NOT `require_prereg_4` (the preflight runs
before the tag exists). Prints only; asserts afterward that nothing
under `root/results` changed.

Usage: python -m experiments.exp4.run.preflight_4 [--checkpoint-step 10000]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXP4 = Path(__file__).resolve().parents[1]
REPO = EXP4.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402

PREFLIGHT_RUNGS = ("antonym", "add3_mid")
PREFLIGHT_KEY = "ladder_pythia_2.8b"


def _results_snapshot(root) -> set:
    d = Path(root) / "results"
    if not d.exists():
        return set()
    return {(str(p.relative_to(d)), p.stat().st_size) for p in d.rglob("*") if p.is_file()}


def _peak_mps_memory():
    try:
        import torch
        return int(torch.mps.driver_allocated_memory())
    except Exception:  # noqa: BLE001 — no MPS device, or a fake run
        return -1


def run(*, root=EXP4, device: str = "mps", loaders=None, rungs=PREFLIGHT_RUNGS,
       checkpoint_step: int = 10000) -> None:
    import numpy as np

    battery_4.check_frozen_4()
    before = _results_snapshot(root)
    if loaders is None:
        loaders = collect_4.real_loaders_4()
    battery = bt.load_battery()

    # (a) two forward collections of the same two rungs, same weights
    passes = []
    model, tok, info = loaders["key"](PREFLIGHT_KEY, device=device)
    try:
        sites = metric_4.sites_4(info["n_hidden"])
        batch_size = battery_4.BATCH_4[PREFLIGHT_KEY]
        for i in range(2):
            per_rung = {}
            for rung in rungs:
                import time
                t0 = time.time()
                cap = battery[rung]
                out = collect_4.collect_rung_4(model, tok, "pythia", cap, sites=sites,
                                               batch_size=batch_size, device=device,
                                               key=PREFLIGHT_KEY)
                dt = time.time() - t0
                per_rung[rung] = out
                finite = bool(np.isfinite(out["X"].astype(np.float32)).all())
                print(f"[4 preflight] pass {i} {rung}: {dt:.1f}s finite={finite} "
                      f"peak_mps_bytes={_peak_mps_memory()}", flush=True)
            passes.append(per_rung)
    finally:
        loaders["release"](model)

    for rung in rungs:
        x0, x1 = passes[0][rung]["X"], passes[1][rung]["X"]
        identical = bool(np.array_equal(x0, x1))
        s0 = collect_4.set_tables_4(x0)
        s1 = collect_4.set_tables_4(x1)
        sets_identical = bool(np.array_equal(s0, s1))
        print(f"[4 preflight] {rung}: X byte-identical across the two passes = {identical}; "
              f"set_tables_4 identical = {sets_identical}", flush=True)

    # (b) one grid checkpoint, end to end
    model, tok, info = loaders["step"]("comma_7b", checkpoint_step, device=device)
    want = battery_4.committed_step_digest_4("comma_7b", checkpoint_step)
    print(f"[4 preflight] comma_7b step{checkpoint_step}: digest {info['tensor_digest']} == "
          f"committed {want} -> {info['tensor_digest'] == want}", flush=True)
    loaders["release"](model)
    loaders["free_step"]("comma_7b", checkpoint_step)

    after = _results_snapshot(root)
    if after != before:
        raise RuntimeError(f"preflight wrote under {Path(root) / 'results'}: "
                           f"{sorted(after - before)}")
    print("[4 preflight] complete: nothing written under results/", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 4 preflight (dial k)")
    ap.add_argument("--root", default=str(EXP4))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--checkpoint-step", type=int, default=10000)
    ar = ap.parse_args(argv)
    run(root=Path(ar.root), device=ar.device, checkpoint_step=ar.checkpoint_step)
    return 0


if __name__ == "__main__":
    sys.exit(main())
