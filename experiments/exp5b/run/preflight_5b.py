# experiments/exp5b/run/preflight_5b.py
"""Exp 5b preflight (design §7 stage 1; plan B-1): scratch only — the
`twice_size` final loaded and scored TWICE into two scratch roots and
compared byte-for-byte (Experiment 5's `_compare_units`), the
`timed_size` final run whole and timed with its loss-forward peak (the
largest unit of this campaign — Experiment 5 note 4, 4c note 1). Nothing
under `root/results` may change. `check_frozen_5b` applies, not the tag
(4c's rule). Usage: python -m experiments.exp5b.run.preflight_5b --device cuda"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

EXP5B = Path(__file__).resolve().parents[1]
REPO = EXP5B.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import collect_5 as c5  # noqa: E402
from experiments.exp5 import slice_5 as sl5  # noqa: E402
from experiments.exp5.run import preflight_5 as pf5  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402


def run(*, root=EXP5B, device="cuda", cache_root=None, loaders=None, manifest=None, sl=None, host=None,
        battery=None, verify_fn=None, transports=None, twice_size="1b", timed_size="6.9b") -> dict:
    b5b.check_frozen_5b()
    root = Path(root)
    before = pf5._results_snapshot(root)
    cache_root = cache_root if cache_root is not None else c5.CKPT_CACHE_5
    if loaders is None:
        loaders = c5.real_loaders_5()
    manifest = manifest if manifest is not None else b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    sl = sl if sl is not None else sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
    battery = battery if battery is not None else bt.load_battery()
    verify_fn = verify_fn if verify_fn is not None else a2d.load_verify()
    if host is None:
        transports = transports if transports is not None else c5.measure_transports_5(cache_root=cache_root)
        print(f"[5b preflight] transports: {transports}", flush=True)
        host = c5.host_record_5(device, transports)
    scratch = Path(cache_root) / "_preflight_units_5b"
    kw = dict(manifest=manifest, cache_root=cache_root, device=device, battery=battery, verify_fn=verify_fn,
              sl=sl, host=host, loaders=loaders, git_sha="preflight", why="preflight")
    dirs = {}
    for tag in ("run1", "run2"):
        c5.run_unit_5(twice_size, b5.FINAL_STEP_5, root=scratch / tag, **kw)
        dirs[tag] = b5.unit_dir_5(scratch / tag, twice_size, b5.FINAL_STEP_5)
    diffs = pf5._compare_units(dirs["run1"], dirs["run2"])
    print(f"[5b preflight] {twice_size} final loaded TWICE: {'IDENTICAL' if not diffs else f'DIFFERS: {diffs}'}",
          flush=True)
    t0 = time.time()
    c5.run_unit_5(timed_size, b5.FINAL_STEP_5, root=scratch / "timed", **kw)
    seconds = time.time() - t0
    peak = pf5._peak_cuda_memory()
    print(f"[5b preflight] {timed_size} final whole unit: {seconds:.0f} s, peak_cuda_bytes {peak}", flush=True)
    after = pf5._results_snapshot(root)
    if after != before:
        raise RuntimeError(f"preflight wrote under {root / 'results'}: {sorted(after - before)}")
    print("[5b preflight] complete: nothing written under results/", flush=True)
    return {"twice_identical": not diffs, "twice_diffs": diffs,
            "timed": {"size": timed_size, "seconds": seconds, "peak_cuda_bytes": peak}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 5b preflight")
    ap.add_argument("--device", default="cuda")
    ar = ap.parse_args(argv)
    run(device=ar.device)
    return 0


if __name__ == "__main__":
    sys.exit(main())
