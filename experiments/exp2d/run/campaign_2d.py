"""Exp 2d campaign driver — COMMITTED AT BUILD, before the freeze and
before any rung runs. It decides what runs and in what order; it
never decides what a number means.

ORDER IS A DESIGN COMMITMENT (§10, frozen):
  pilot/410m → pilot/1b → [the frozen §7 procedure runs ONCE:
  compute_power_2d.py → power_2d.json; main refuses without it and runs
  regardless of what it says] → main/410m → main/1b → argmax/410m →
  argmax/1b.
The runner enforces the preconditions per rung, this driver per tier,
the analyzer on whatever exists — three layers, one rule. Gate 1 runs
INSIDE main as each reversal rung lands; a diff halts the runner, the
driver stops, and nothing later runs.

TIER-PER-PROCESS (exp3's allocator lesson): every (kind, size) tier is
one child process that loads its model once, runs its 34 rungs
sequentially with skip-if-exists, and exits. The watcher commits and
pushes per rung as records land.

PREFLIGHT GATES EVERY SIZE (exp3's standing rule): before any sampling
tier of a size runs, exp3's run/preflight_paths.py must pass for
(size, float32) on this stack.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

EXP2D = Path(__file__).resolve().parents[1]
if str(EXP2D.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2D.parent.parent))

from experiments.exp2d import analyze_2d as a  # noqa: E402
from experiments.exp2d.run.run_cell_2d import (  # noqa: E402
    SIZES_ASCENDING, gate1_halted, preconditions, tier_complete,
)


def tier_plan() -> list:
    return ([("pilot", s) for s in SIZES_ASCENDING]
            + [("main", s) for s in SIZES_ASCENDING]
            + [("argmax", s) for s in SIZES_ASCENDING])


def tier_pending(kind, size, out_root) -> list:
    if kind == "argmax":
        return [r for r in a.RUNGS
                if not a.argmax_record_path(out_root, size, r).exists()]
    return [r for r in a.RUNGS
            if not (a.tier_record_path(out_root, kind, size, r).exists()
                    and a.tier_draws_path(out_root, kind, size, r).exists())]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2d campaign driver")
    ap.add_argument("--out-root", default=str(EXP2D))
    ap.add_argument("--only-kind", choices=("pilot", "main", "argmax"))
    ap.add_argument("--limit", type=int, default=None,
                    help="run at most N tiers")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-preflight", action="store_true",
                    help="resume aid; the per-size artifacts must "
                         "already exist and pass")
    ar = ap.parse_args(argv)

    tiers = tier_plan()
    if ar.only_kind:
        tiers = [t for t in tiers if t[0] == ar.only_kind]
    todo = [t for t in tiers if not tier_complete(ar.out_root, *t)]
    if ar.limit is not None:
        todo = todo[: ar.limit]
    print(f"[2d] {len(tiers)} tiers selected, {len(tiers) - len(todo)} "
          f"complete, {len(todo)} to run, one process per tier",
          flush=True)
    if ar.dry_run:
        for kind, size in todo:
            pend = tier_pending(kind, size, ar.out_root)
            dtype = a.ARGMAX_DTYPE if kind == "argmax" else a.SAMPLING_DTYPE
            print(f"  would run {kind}/{size} [{dtype}] {len(pend)} rung(s)"
                  f" pending: {','.join(pend[:4])}"
                  f"{',...' if len(pend) > 4 else ''}", flush=True)
        return 0

    preflighted = set()
    t0, failed = time.time(), []
    for kind, size in todo:
        label = f"{kind}/{size}"
        halted, why = gate1_halted(ar.out_root)
        if halted:
            failed.append((label, why))
            print(f"  STOP: {why}", flush=True)
            break
        stop = False
        for check in preconditions(kind, ar.out_root):
            ok, why = check(ar.out_root)
            if not ok:
                failed.append((label, why))
                print(f"  STOP: {why}", flush=True)
                stop = True
                break
        if stop:
            break
        if kind != "argmax" and not ar.skip_preflight and \
                size not in preflighted:
            pf = subprocess.run(
                [sys.executable, "-m",
                 "experiments.exp3.run.preflight_paths",
                 "--size", size, "--dtype", "float32"],
                cwd=EXP2D.parent.parent)
            if pf.returncode != 0:
                failed.append((label, f"preflight {size}/float32 FAILED"))
                print(f"  STOP: preflight {size}/float32 failed — this "
                      f"tier's arithmetic is not verified", flush=True)
                break
            preflighted.add(size)
        t = time.time()
        r = subprocess.run(
            [sys.executable, "-m", "experiments.exp2d.run.run_cell_2d",
             "--tier", kind, size], cwd=EXP2D.parent.parent)
        if r.returncode != 0:
            failed.append((label, f"exit {r.returncode}"))
            print(f"  FAIL {label}: exit {r.returncode}", flush=True)
            break
        print(f"  tier done {label} {time.time()-t:.0f}s | elapsed "
              f"{(time.time()-t0)/60:.1f}m", flush=True)

    print(f"[2d] {'complete' if not failed else 'STOPPED'}: "
          f"{(time.time()-t0)/60:.1f}m", flush=True)
    for label, err in failed:
        print(f"  FAILED {label}: {err}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
