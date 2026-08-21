"""Exp 3e campaign driver — COMMITTED AT BUILD, before the freeze and
before any cell runs (the standing practice since 1c). It decides
what runs and in what order; it never decides what a number means.

ORDER IS A DESIGN COMMITMENT (§10, frozen): scorer known-answer gates
(already committed, no model) → gate-1 re-derivation, both sizes →
the tranche, 410m before 1b, 16-seed blocks ascending. Each later
kind REFUSES to start while any earlier kind's record is missing or
failed: the runner enforces it per cell, this driver enforces it per
tier, and the analyzer enforces it on whatever exists — three layers,
one rule.

TIER-PER-PROCESS (exp3's allocator lesson): every (kind, size) tier
is one child process that loads its model once, runs its cells
sequentially with skip-if-exists, and exits. The sampling tiers'
durable unit is the 16-seed block (§10.4, 46,080 draws): the watcher
commits and pushes per block as shards land.

PREFLIGHT GATES EVERY SIZE (exp3's standing rule): before any tier of
a size runs, exp3's run/preflight_paths.py must pass for
(size, float32) on this stack.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

EXP3E = Path(__file__).resolve().parents[1]
if str(EXP3E.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3E.parent.parent))

from experiments.exp3e import rederive_3e  # noqa: E402
from experiments.exp3e.analyze_3e import SEED_BLOCKS  # noqa: E402
from experiments.exp3e.run.run_cell_3e import (  # noqa: E402
    gate1_clean, sampling_draws_path, sampling_record_path,
    scorer_gates_clean,
)

SIZES_ASCENDING = ("410m", "1b")


def tier_plan() -> list:
    """(kind, size) tiers in the committed §10 order."""
    return [("gate1", s) for s in SIZES_ASCENDING] + \
        [("sampling", s) for s in SIZES_ASCENDING]


def tier_pending(kind, size, out_root) -> list:
    if kind == "gate1":
        return [] if rederive_3e.record_path(out_root, size).exists() \
            else ["reverse_string"]
    return [f"s{b[0]}-s{b[-1]}" for b in SEED_BLOCKS[size]
            if not (sampling_record_path(out_root, size, b).exists()
                    and sampling_draws_path(out_root, size,
                                            b).exists())]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 3e campaign driver")
    ap.add_argument("--out-root", default=str(EXP3E))
    ap.add_argument("--only-kind", choices=("gate1", "sampling"))
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
    print(f"[3e] {len(tiers)} tiers selected, {len(tiers) - len(todo)} "
          f"complete, {len(todo)} to run, one process per tier",
          flush=True)
    if a.dry_run:
        for kind, size in todo:
            pend = tier_pending(kind, size, a.out_root)
            print(f"  would run {kind}/{size} [float32] "
                  f"units: {','.join(pend)}", flush=True)
        return 0

    preflighted = set()
    t0, failed = time.time(), []
    for kind, size in todo:
        label = f"{kind}/{size}"
        checks = [scorer_gates_clean] + ([gate1_clean]
                                         if kind == "sampling" else [])
        stop = False
        for check in checks:
            ok, why = check(a.out_root)
            if not ok:
                failed.append((label, why))
                print(f"  STOP: {why}", flush=True)
                stop = True
                break
        if stop:
            break
        if not a.skip_preflight and size not in preflighted:
            pf = subprocess.run(
                [sys.executable, "-m",
                 "experiments.exp3.run.preflight_paths",
                 "--size", size, "--dtype", "float32"],
                cwd=EXP3E.parent.parent)
            if pf.returncode != 0:
                failed.append((label, f"preflight {size}/float32 "
                                      f"FAILED"))
                print(f"  STOP: preflight {size}/float32 failed — "
                      f"this tier's arithmetic is not verified",
                      flush=True)
                break
            preflighted.add(size)
        t = time.time()
        r = subprocess.run(
            [sys.executable, "-m", "experiments.exp3e.run.run_cell_3e",
             "--tier", kind, size], cwd=EXP3E.parent.parent)
        if r.returncode != 0:
            failed.append((label, f"exit {r.returncode}"))
            print(f"  FAIL {label}: exit {r.returncode}", flush=True)
            break
        print(f"  tier done {label} {time.time()-t:.0f}s | elapsed "
              f"{(time.time()-t0)/60:.1f}m", flush=True)

    print(f"[3e] {'complete' if not failed else 'STOPPED'}: "
          f"{(time.time()-t0)/60:.1f}m", flush=True)
    for label, err in failed:
        print(f"  FAILED {label}: {err}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
