"""Exp 3c campaign driver — COMMITTED AT BUILD, before the freeze and
before any cell runs (1c's practice, exp3's precedent). It decides
what runs and in what order; it never decides what a number means.

ORDER IS A DESIGN COMMITMENT (§10.3): gate-1 re-derivation FIRST — all
five cells, both sizes — then the new draws, 410m before 1b. A
sampling tier REFUSES to start while any gate-1 record is missing or
carries diffs: if the generation law drifted since exp3, 1.5M new
draws would be uninterpretable, so the campaign stops before sampling
them (the analyzer enforces the same rule on whatever exists).

TIER-PER-PROCESS (exp3's allocator lesson): every (kind, size) tier is
one child process that loads its model once, runs its cells
sequentially with skip-if-exists, and exits — no process ever holds
more than one tier's MPS cache.

PREFLIGHT GATES EVERY SIZE (exp3's standing rule): before any tier of
a size runs, exp3's run/preflight_paths.py must pass for
(size, float32) on this stack — a tier whose arithmetic cannot be
verified does not run.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

EXP3C = Path(__file__).resolve().parents[1]
if str(EXP3C.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3C.parent.parent))

from experiments.exp3c.run.run_cell_3c import (  # noqa: E402
    TIER_RUNGS, draws_path, record_path,
)

SIZES_ASCENDING = ("410m", "1b")


def tier_plan() -> list:
    """(kind, size) tiers in the committed order: gate1 everywhere
    before sampling anywhere; sizes ascend within a kind."""
    return [("gate1", s) for s in SIZES_ASCENDING] + \
        [("sampling", s) for s in SIZES_ASCENDING]


def cell_complete(kind, rung, size, out_root) -> bool:
    if not record_path(out_root, kind, rung, size).exists():
        return False
    if kind == "sampling" and not draws_path(out_root, rung,
                                             size).exists():
        return False
    return True


def tier_pending(kind, size, out_root) -> list:
    return [r for r in TIER_RUNGS[kind][size]
            if not cell_complete(kind, r, size, out_root)]


def gate1_clean(out_root) -> tuple[bool, str]:
    """True iff every gate-1 record exists and carries zero diffs —
    the sampling tiers' precondition."""
    for size in SIZES_ASCENDING:
        for rung in TIER_RUNGS["gate1"][size]:
            p = record_path(out_root, "gate1", rung, size)
            if not p.exists():
                return False, f"gate-1 record missing: {rung}/{size}"
            rec = json.loads(p.read_text())
            if rec.get("n_diffs") != 0:
                return False, (f"gate-1 diffs at {rung}/{size}: "
                               f"{rec.get('n_diffs')} differing draws — "
                               f"the generation law drifted; no new "
                               f"draw is interpretable")
    return True, "all 5 gate-1 records exist with 0 diffs"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 3c campaign driver")
    ap.add_argument("--out-root", default=str(EXP3C))
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
    print(f"[3c] {len(tiers)} tiers selected, {len(tiers) - len(todo)} "
          f"complete, {len(todo)} to run, one process per tier",
          flush=True)
    if a.dry_run:
        for kind, size in todo:
            pend = tier_pending(kind, size, a.out_root)
            print(f"  would run {kind}/{size} [float32] "
                  f"cells: {','.join(pend)}", flush=True)
        return 0

    preflighted = set()
    t0, failed = time.time(), []
    for kind, size in todo:
        label = f"{kind}/{size}"
        if kind == "sampling":
            ok, why = gate1_clean(a.out_root)
            if not ok:
                failed.append((label, why))
                print(f"  STOP: {why}", flush=True)
                break
        if not a.skip_preflight and size not in preflighted:
            pf = subprocess.run(
                [sys.executable, "-m",
                 "experiments.exp3.run.preflight_paths",
                 "--size", size, "--dtype", "float32"],
                cwd=EXP3C.parent.parent)
            if pf.returncode != 0:
                failed.append((label, f"preflight {size}/float32 FAILED"))
                print(f"  STOP: preflight {size}/float32 failed — this "
                      f"tier's arithmetic is not verified", flush=True)
                break
            preflighted.add(size)
        t = time.time()
        r = subprocess.run(
            [sys.executable, "-m", "experiments.exp3c.run.run_cell_3c",
             "--tier", kind, size], cwd=EXP3C.parent.parent)
        if r.returncode != 0:
            failed.append((label, f"exit {r.returncode}"))
            print(f"  FAIL {label}: exit {r.returncode}", flush=True)
            break
        print(f"  tier done {label} {time.time()-t:.0f}s | elapsed "
              f"{(time.time()-t0)/60:.1f}m", flush=True)

    print(f"[3c] {'complete' if not failed else 'STOPPED'}: "
          f"{(time.time()-t0)/60:.1f}m", flush=True)
    for label, err in failed:
        print(f"  FAILED {label}: {err}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
