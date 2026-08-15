"""Exp 3a campaign driver.

WRITTEN AFTER THE FREEZE. It decides what runs and in what order; it never
decides what a number means. The verdict is fixed by the frozen
`analyze_3a.py` and locked by that module's 24 fixtures. Not part of the
frozen artifact.

ORDER IS A DESIGN COMMITMENT (§8): all 12 untrained twins before any trained
cell, then trained 2.8b → 6.9b → 12b. Under the frozen verdict tree the
untrained cells are a contamination gate, and 1b's sequencing lesson is that
a control run after the thing it controls is not a control.

SEQUENTIAL BY DESIGN, unlike the 1c driver's 8 workers. Pythia-12b in fp16 is
~24 GB of weights; two of those in parallel on a 48 GB machine would swap or
fail, and a half-finished cell that OOMs costs a model load to redo. One cell
at a time, skip-if-exists, so a kill and restart loses at most the cell in
flight.

Each cell reloads its model, because the frozen runner owns model
construction. That is 24 loads rather than 6, and it is the right trade: the
data is produced by the runner that was frozen, not by a faster copy of it
inside the driver.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

EXP3A = Path(__file__).resolve().parents[1]
if str(EXP3A.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3A.parent.parent))

from experiments.exp3a.run.run_cell import (  # noqa: E402
    MODES, RUNGS, SIZES, record_path, run_cell,
)


def plan() -> list[tuple[str, str, str]]:
    """(rung, size, mode) in the order §8 fixes: every untrained cell first."""
    out = []
    for mode in ("untrained", "trained"):          # MODES order is not relied on
        for size in SIZES:                          # 2.8b -> 6.9b -> 12b
            for rung in RUNGS:
                out.append((rung, size, mode))
    return out


def pending(cells, out_root):
    return [c for c in cells
            if not record_path(out_root, c[0], c[1], c[2]).exists()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 3a campaign driver")
    ap.add_argument("--out-root", default=str(EXP3A))
    ap.add_argument("--only-mode", choices=MODES, default=None)
    ap.add_argument("--only-size", choices=SIZES, default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    cells = plan()
    if a.only_mode:
        cells = [c for c in cells if c[2] == a.only_mode]
    if a.only_size:
        cells = [c for c in cells if c[1] == a.only_size]
    todo = pending(cells, a.out_root)
    n_done = len(cells) - len(todo)
    if a.limit is not None:
        todo = todo[: a.limit]

    print(f"[3a] {len(cells)} cells selected, {n_done} already done, "
          f"{len(todo)} to run, sequential", flush=True)
    if a.dry_run:
        for c in todo:
            print("  would run", "/".join(c), flush=True)
        return 0

    t0, done, failed = time.time(), 0, []
    for rung, size, mode in todo:
        label = f"{rung}/{size}/{mode}"
        try:
            t = time.time()
            r = run_cell(rung, size, mode, out_root=a.out_root)
            done += 1
            el = time.time() - t0
            print(f"  done {done}/{len(todo)} {label} "
                  f"full_string={r['full_string_acc']:.4f} "
                  f"(2c committed {r['committed_2c_acc']}) "
                  f"{time.time()-t:.0f}s | elapsed {el/60:.1f}m "
                  f"eta {(len(todo)-done)*(el/done)/60:.1f}m", flush=True)
        except Exception as exc:                          # noqa: BLE001
            failed.append((label, repr(exc)))
            print(f"  FAIL {label}: {exc!r}", flush=True)

    print(f"[3a] complete: {done} ok, {len(failed)} failed, "
          f"{(time.time()-t0)/60:.1f}m", flush=True)
    for label, err in failed:
        print(f"  FAILED {label}: {err}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
