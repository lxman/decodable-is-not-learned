# experiments/exp4c/run/preflight_4c.py
"""Exp 4c preflight (Task 3 brief step 5) — the one sanctioned
model-contact check before the campaign: one interior checkpoint of
each trajectory, loaded end to end, collected on two rungs, and freed.
Prints only; asserts afterwards that nothing under `root/results`
changed. Applies `check_frozen_4c()` but NOT `require_prereg_4c` (the
preflight runs before the tag exists).

For `("olmo2_13b", 1000)` then `("pythia_6.9b", 1000)`: `loaders
["step"]`; the checkpoint's own digest against `committed_step_digest
_4c`; `sites_4(n_hidden)`'s length against `SITE_COUNT_PIN_4C`; two
rungs (`antonym`, `add3_mid`) through `collect_4.collect_rung_4` at
`BATCH_4C[traj]` (`key=None` — 4c's batch pin is checked by
`process_model_4c`, not by this rehearsal); per-rung seconds, fp16
finiteness, and peak MPS memory (`torch.mps.driver_allocated_memory()`
when the runtime offers it — guarded by `hasattr`, never a hard
requirement); release, then free.

Usage: python -m experiments.exp4c.run.preflight_4c [--device mps]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

EXP4C = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP4C.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp4 import _threads_4  # noqa: E402,F401 — BEFORE numpy: pins the BLAS threads

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402
from experiments.exp4c import battery_4c  # noqa: E402
from experiments.exp4c import collect_4c  # noqa: E402

PREFLIGHT_RUNGS_4C = ("antonym", "add3_mid")
PREFLIGHT_UNITS_4C = (("olmo2_13b", 1000), ("pythia_6.9b", 1000))


def _results_snapshot(root) -> set:
    d = Path(root) / "results"
    if not d.exists():
        return set()
    return {(str(p.relative_to(d)), p.stat().st_size) for p in d.rglob("*") if p.is_file()}


def _peak_mps_memory():
    try:
        import torch
    except ImportError:
        return -1
    if hasattr(torch, "mps") and hasattr(torch.mps, "driver_allocated_memory"):
        try:
            return int(torch.mps.driver_allocated_memory())
        except Exception:  # noqa: BLE001 — no MPS device, or a fake run
            return -1
    return -1


def run(*, root=EXP4C, device: str = "mps", loaders=None, cache_root=None,
       units=PREFLIGHT_UNITS_4C, rungs=PREFLIGHT_RUNGS_4C) -> None:
    import numpy as np

    battery_4c.check_frozen_4c()
    before = _results_snapshot(root)
    cache_root = cache_root if cache_root is not None else battery_4c.CKPT_CACHE_4C
    if loaders is None:
        loaders = collect_4c.real_loaders_4c()
    battery = bt.load_battery()
    print(f"[4c preflight] threads pinned: {_threads_4.thread_pin_record_4()}", flush=True)

    for traj, step in units:
        model, tok, info = loaders["step"](traj, step, cache_root=cache_root, device=device)
        try:
            n_hidden = info["n_hidden"]
            sites = metric_4.sites_4(n_hidden)
            want_n_sites = battery_4c.SITE_COUNT_PIN_4C.get(n_hidden)
            print(f"[4c preflight] {traj} step{step}: sites_4 length {len(sites)} == "
                  f"SITE_COUNT_PIN_4C[{n_hidden}] {want_n_sites} -> "
                  f"{len(sites) == want_n_sites}", flush=True)
            want_digest = battery_4c.committed_step_digest_4c(traj, step)
            print(f"[4c preflight] {traj} step{step}: digest {info['tensor_digest']} == "
                  f"committed {want_digest} -> {info['tensor_digest'] == want_digest}",
                  flush=True)
            for rung in rungs:
                t0 = time.time()
                out = collect_4.collect_rung_4(model, tok, battery_4c.FAMILY_OF_TRAJ_4C[traj],
                                               battery[rung], sites=sites,
                                               batch_size=battery_4c.BATCH_4C[traj], device=device,
                                               key=None)
                dt = time.time() - t0
                finite = bool(np.isfinite(out["X"].astype(np.float32)).all())
                print(f"[4c preflight] {traj} step{step} {rung}: {dt:.1f}s finite={finite} "
                      f"shape={out['X'].shape} peak_mps_bytes={_peak_mps_memory()}", flush=True)
        finally:
            loaders["release"](model)
            loaders["free_step"](traj, step, cache_root=cache_root)
        print(f"[4c preflight] {traj} step{step}: released and freed", flush=True)

    after = _results_snapshot(root)
    if after != before:
        raise RuntimeError(f"preflight wrote under {Path(root) / 'results'}: "
                           f"{sorted(after - before)}")
    print("[4c preflight] complete: nothing written under results/", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 4c preflight")
    ap.add_argument("--device", default="mps")
    ar = ap.parse_args(argv)
    run(device=ar.device)
    return 0


if __name__ == "__main__":
    sys.exit(main())
