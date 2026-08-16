"""Exp 3 campaign driver — COMMITTED AT BUILD, before the freeze and
before any cell runs (1c's practice; 3a ate a post-freeze correction
for writing its driver late). It decides what runs and in what order;
it never decides what a number means.

TIER-PER-PROCESS (design §2.3, the 3b allocator lesson): every (kind,
size, mode) tier is one child process that loads its model once, runs
its four rungs' cells sequentially with skip-if-exists, and exits —
no process ever holds more than one tier's MPS cache. Sizes ascend;
untrained twins run before the trained cells they control (1b's
sequencing lesson).

ORDER IS A DESIGN COMMITMENT (§10.3): gate-2 greedy re-decode first,
then the mass ladder, then all twin sampling, then trained sampling
410m before 1b.

PREFLIGHT GATES EVERY TIER (PROGRESS.md 2026-08-15): before any cell
of a (size, dtype) runs, run/preflight_paths.py must pass for that
pair on this stack — a tier whose arithmetic cannot be verified does
not run.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

EXP3 = Path(__file__).resolve().parents[1]
if str(EXP3.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3.parent.parent))

from experiments.exp3.analyze_3 import (  # noqa: E402
    EVAL_SIZES, PROBE_SIZES, RUNGS,
)
from experiments.exp3.run.run_cell import cell_policy, record_path  # noqa: E402


def tier_plan() -> list:
    """(kind, size, mode) tiers in the committed order."""
    tiers = []
    for mode in ("untrained", "trained"):
        for size in PROBE_SIZES:
            tiers.append(("redecode", size, mode))
    for size in PROBE_SIZES:
        tiers.append(("mass", size, "untrained"))
    for size in PROBE_SIZES + EVAL_SIZES:
        tiers.append(("mass", size, "trained"))
    for size in PROBE_SIZES:
        tiers.append(("sampling", size, "untrained"))
    for size in PROBE_SIZES:
        tiers.append(("sampling", size, "trained"))
    return tiers


def tier_pending(kind, size, mode, out_root) -> list:
    return [r for r in RUNGS
            if not record_path(out_root, kind, r, size, mode).exists()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 3 campaign driver")
    ap.add_argument("--out-root", default=str(EXP3))
    ap.add_argument("--only-kind", choices=("redecode", "mass", "sampling"))
    ap.add_argument("--limit", type=int, default=None,
                    help="run at most N tiers")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-preflight", action="store_true",
                    help="resume aid; the per-size artifacts must "
                         "already exist and pass")
    a = ap.parse_args(argv)

    tiers = tier_plan()
    if a.only_kind:
        tiers = [t for t in tiers if t[0] == a.only_kind]
    todo = [t for t in tiers if tier_pending(*t, a.out_root)]
    if a.limit is not None:
        todo = todo[: a.limit]
    print(f"[3] {len(tiers)} tiers selected, {len(tiers) - len(todo)} "
          f"complete, {len(todo)} to run, one process per tier", flush=True)
    if a.dry_run:
        for kind, size, mode in todo:
            dtype, depth = cell_policy(kind, size)
            pend = tier_pending(kind, size, mode, a.out_root)
            print(f"  would run {kind}/{size}/{mode} [{dtype}"
                  f"{f' d{depth}' if depth else ''}] "
                  f"cells: {','.join(pend)}", flush=True)
        return 0

    preflighted = set()
    t0, failed = time.time(), []
    for kind, size, mode in todo:
        dtype, _ = cell_policy(kind, size)
        label = f"{kind}/{size}/{mode}"
        if not a.skip_preflight and kind in ("mass", "sampling") \
                and (size, dtype) not in preflighted:
            pf_args = [sys.executable, "-m",
                       "experiments.exp3.run.preflight_paths",
                       "--size", size, "--dtype", dtype]
            if dtype == "float16":
                # the fp16 tier (12b mass, depth 1) uses ONLY batch-1
                # keep1 forwards; gate it on the paths it uses
                # (PROGRESS.md 2026-08-16, freeze finding #3)
                pf_args.append("--keep1-only")
            pf = subprocess.run(pf_args, cwd=EXP3.parent.parent)
            if pf.returncode != 0:
                failed.append((label, f"preflight {size}/{dtype} FAILED"))
                print(f"  STOP: preflight {size}/{dtype} failed — this "
                      f"tier's arithmetic is not verified", flush=True)
                break
            preflighted.add((size, dtype))
        t = time.time()
        r = subprocess.run(
            [sys.executable, "-m", "experiments.exp3.run.run_cell",
             "--tier", kind, size, mode], cwd=EXP3.parent.parent)
        if r.returncode != 0:
            failed.append((label, f"exit {r.returncode}"))
            print(f"  FAIL {label}: exit {r.returncode}", flush=True)
            break
        print(f"  tier done {label} {time.time()-t:.0f}s | elapsed "
              f"{(time.time()-t0)/60:.1f}m", flush=True)

    print(f"[3] {'complete' if not failed else 'STOPPED'}: "
          f"{(time.time()-t0)/60:.1f}m", flush=True)
    for label, err in failed:
        print(f"  FAILED {label}: {err}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
