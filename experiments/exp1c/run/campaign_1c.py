"""Exp 1c campaign driver.

WRITTEN AFTER THE FREEZE (ruling 14 of FREEZE_CHECKLIST.md). This file decides
what runs and in what order. It never decides what a number means: the verdict
is fixed by the frozen `analyze_1c.py` and locked by that module's fixtures.
It is not part of the frozen artifact and could be deleted and rewritten
without touching a single preregistered quantity.

ORDER IS A DESIGN COMMITMENT, not a convenience (§8):

  twins    all 100 twin profiles, BEFORE any trained cell is read. Under the
           frozen prediction the twins are the load-bearing measurement, and
           running them first is what made 1b's floor correction legitimate
           while it was still available.
  stage_a  20 trained known-answer cells. Gate. If the measure cannot
           reproduce what 1b already scored, the sweep is never probed.
  stage_b  80 trained sweep profiles across both arms.

LIVENESS. 1b's campaign log wrote only START/DONE, so a hang and a long cell
looked identical and liveness had to be read off checkpoint mtimes. 1c writes
no checkpoints, so that trick is unavailable — instead every cell logs its own
elapsed time on completion and the driver prints a running done/total. With
~100 cells over a few hours a stalled campaign shows a gap in a log that is
otherwise moving every few minutes.
"""

from __future__ import annotations

import os

# Pin BLAS before numpy/torch are imported anywhere below. Each worker gets one
# thread; oversubscription across processes is slower than either alone, and on
# this machine the 4 efficiency cores make a shared thread pool actively bad.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402

EXP1C_DIR = Path(__file__).resolve().parents[1]
EXP1B_DIR = EXP1C_DIR.parent / "exp1b"

DENSITIES = (0.25, 0.45, 0.65, 0.85)
SIZES = ("1M", "10M")
SEEDS = (100, 101, 102, 103, 104)
STAGE_A_SYSTEMS = ("lubana_above", "lubana_below")
STAGE_A_DENSITY = {"lubana_above": 10.0, "lubana_below": 0.50}
PHASES = ("twins", "stage_a", "stage_b")


@dataclass(frozen=True)
class Cell:
    system: str
    arm: str
    density: float
    size: str
    seed: int
    trained: bool
    step: int | None = None

    def label(self) -> str:
        return (f"{self.system}/{self.arm}/p{self.density:g}/{self.size}/"
                f"seed{self.seed}/{'trained' if self.trained else 'twin'}")


def _stage_a_step(exp1b_root, system: str, size: str, seed: int) -> int:
    """The checkpoint 1b actually scored, from its own record. No default:
    ruling 16 — a default would silently probe a different checkpoint than the
    one whose answer is known."""
    p = Path(exp1b_root) / "results" / system / size / f"seed{seed}.json"
    if not p.is_file():
        raise ValueError(
            f"no 1b record at {p} — Stage A cannot invent a checkpoint step "
            f"for {system}/{size}/seed{seed}")
    cid = json.loads(p.read_text())["s1"]["checkpoint_id"]
    return int(str(cid).split("_")[-1])


def _stage_a_cells(exp1b_root, trained: bool):
    return [Cell(system=sys_, arm="fixed", density=STAGE_A_DENSITY[sys_],
                 size=size, seed=seed, trained=trained,
                 step=_stage_a_step(exp1b_root, sys_, size, seed))
            for sys_ in STAGE_A_SYSTEMS for size in SIZES for seed in SEEDS]


def _sweep_cells(arm: str, trained: bool):
    return [Cell(system="sweep", arm=arm, density=d, size=size, seed=seed,
                 trained=trained)
            for d in DENSITIES for size in SIZES for seed in SEEDS]


def cells_for_phase(phase: str, *, exp1b_root=EXP1B_DIR) -> list[Cell]:
    if phase not in PHASES:
        raise ValueError(f"phase must be one of {PHASES}, got {phase!r}")
    if phase == "twins":
        return (_stage_a_cells(exp1b_root, trained=False)
                + _sweep_cells("fixed", trained=False)
                + _sweep_cells("natural", trained=False))
    if phase == "stage_a":
        return _stage_a_cells(exp1b_root, trained=True)
    return _sweep_cells("fixed", trained=True) + _sweep_cells("natural",
                                                              trained=True)


def pending(cells, out_root) -> list[Cell]:
    from experiments.exp1c.records import record_path

    return [c for c in cells
            if not record_path(out_root, c.system, c.arm, c.density, c.size,
                               c.seed, c.trained).exists()]


def _run_one(cell: Cell, out_root):
    from experiments.exp1c.run.run_profile import run_profile

    t0 = time.time()
    rec = run_profile(cell.system, cell.arm, cell.density, cell.size,
                      cell.seed, trained=cell.trained, out_root=out_root,
                      step=cell.step)
    return cell, time.time() - t0, rec.n_rows, rec.n_val


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 1c campaign driver")
    ap.add_argument("phase", choices=PHASES)
    ap.add_argument("--out-root", default=str(EXP1C_DIR))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=None,
                    help="run at most N cells then stop (smoke runs)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    cells = cells_for_phase(a.phase)
    todo = pending(cells, a.out_root)
    # Count what is genuinely on disk BEFORE --limit truncates the queue.
    # Conflating the two made a fresh tree report "99 already done".
    n_done = len(cells) - len(todo)
    if a.limit is not None:
        todo = todo[: a.limit]

    print(f"[1c/{a.phase}] {len(cells)} cells, {n_done} already done, "
          f"{len(todo)} to run, {a.workers} workers", flush=True)
    if a.dry_run:
        for c in todo:
            print("  would run", c.label(), flush=True)
        return 0

    t0, done, failed = time.time(), 0, []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(_run_one, c, a.out_root): c for c in todo}
        for fut in as_completed(futs):
            cell = futs[fut]
            try:
                _c, dt, n_rows, n_val = fut.result()
            except Exception as exc:                      # noqa: BLE001
                failed.append((cell, repr(exc)))
                print(f"  FAIL {cell.label()}: {exc!r}", flush=True)
                continue
            done += 1
            el = time.time() - t0
            rate = el / done
            print(f"  done {done}/{len(todo)} {cell.label()} "
                  f"n={n_rows} val={n_val} {dt:.1f}s "
                  f"| elapsed {el/60:.1f}m eta {(len(todo)-done)*rate/60:.1f}m",
                  flush=True)

    print(f"[1c/{a.phase}] complete: {done} ok, {len(failed)} failed, "
          f"{(time.time()-t0)/60:.1f}m", flush=True)
    for cell, err in failed:
        print(f"  FAILED {cell.label()}: {err}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
