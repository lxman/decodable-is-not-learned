"""Exp 1b campaign driver: plan, remaining, dispatch. Skip-if-exists, resumable.

Sixty cells — three systems x two sizes x five seeds, each trained and each
with an untrained twin. The durable unit is the record on disk, so an
interrupted campaign is restarted by re-running: `remaining()` is derived from
what exists, never from a checkpoint file that can disagree with reality.

Order, and why:
  1. trained 1M, then trained 10M — the cheap tier first, so a broken recipe
     surfaces in minutes rather than after a day of training.
  2. within a size, `grokking` first (~31 min for five seeds) before the two
     lubana rows (~24 h each).
  3. untrained cells last. They are probe-only, cost minutes, and depend on
     nothing, so they must not sit in front of the tier that takes days.

The lubana recipe constants are IMPORTED from run_untrained rather than
restated. A trained cell and its untrained twin have to be the same
architecture on the same data; if this module declared its own `scale` or
`model_size` the two could drift apart silently, and the floor-corrected S1
(design §4) would then compare a trained cell against a floor measured on a
different model. Sharing the objects makes that drift impossible.

Invocation is from the REPO ROOT, not from experiments/exp1b:

    ~/emergence-lab/.venv/bin/python -m experiments.exp1b.run.campaign_1b --list

exp1b's modules import absolutely from the repo root (`experiments.exp1b.*`),
unlike exp2c's, whose campaign script cds into its own experiment directory.
`campaign_1b.sh` handles this.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

EXP1B_DIR = Path(__file__).resolve().parents[1]
EXP1_DIR = EXP1B_DIR.parent / "exp1"

# Same guarded insertion as run_untrained.py — exp1's runners import their own
# package absolutely. Repeated here rather than relied upon as an import-order
# side effect of loading run_untrained. See run_untrained.py's docstring.
if str(EXP1_DIR) not in sys.path:
    sys.path.insert(0, str(EXP1_DIR))

from experiments.exp1.run.run_grokking import run_grokking  # noqa: E402
from experiments.exp1.run.run_lubana import run_lubana  # noqa: E402
from experiments.exp1b.run.run_untrained import (  # noqa: E402
    LUBANA_MODEL_SIZE,
    LUBANA_SCALE,
    record_path,
    run_untrained,
)

OUT_ROOT = EXP1B_DIR

KINDS = ("trained", "untrained")
SYSTEMS = ("grokking", "lubana_above", "lubana_below")   # grokking first
SIZES = ("1M", "10M")                                    # cheap tier first
SEEDS = (100, 101, 102, 103, 104)                        # disjoint from exp1's


def campaign_plan() -> list[tuple[str, str, str, int]]:
    """Every cell, in run order. `(kind, system, size, seed)`."""
    return [(kind, system, size, seed)
            for kind in KINDS
            for size in SIZES
            for system in SYSTEMS
            for seed in SEEDS]


def record_path_for(kind: str, system: str, size: str, seed: int) -> Path:
    """Where this cell's durable record lands.

    Reads the module-level OUT_ROOT at call time so a test can redirect the
    whole campaign with monkeypatch.
    """
    if kind == "untrained":
        return record_path(OUT_ROOT, system, size, seed)
    # The path exp1's own runners write to when handed out_dir=OUT_ROOT.
    return Path(OUT_ROOT) / "results" / system / size / f"seed{seed}.json"


def remaining() -> list[tuple[str, str, str, int]]:
    """Planned cells with no record on disk. Derived, never cached."""
    return [cell for cell in campaign_plan()
            if not record_path_for(*cell).exists()]


def describe_cell(kind: str, system: str, size: str, seed: int) -> str:
    """Human-readable label, and the completeness check for dispatch: every
    planned cell must map to a known route."""
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind!r}")
    if system not in SYSTEMS:
        raise ValueError(f"unknown system {system!r}")
    return f"{kind}/{system}/{size}/seed{seed}"


def run_cell(kind: str, system: str, size: str, seed: int):
    """Dispatch one cell to the runner that owns it. Exp 1's runners are used
    unmodified; only `out_dir` is redirected into 1b's tree."""
    describe_cell(kind, system, size, seed)          # refuse unknown routes
    if kind == "untrained":
        return run_untrained(system, size, seed, OUT_ROOT)
    if system == "grokking":
        return run_grokking(seed, size, out_dir=Path(OUT_ROOT))
    setting = "below" if system == "lubana_below" else "above"
    return run_lubana(setting, seed, LUBANA_SCALE, LUBANA_MODEL_SIZE[size],
                      out_dir=Path(OUT_ROOT))


def _stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Exp 1b campaign: skip-if-exists, resumable.")
    ap.add_argument("--only", choices=KINDS, help="restrict to one kind")
    ap.add_argument("--system", choices=SYSTEMS, help="restrict to one system")
    ap.add_argument("--size", choices=SIZES, help="restrict to one size")
    ap.add_argument("--seed", type=int, help="restrict to one seed")
    ap.add_argument("--list", action="store_true",
                    help="print the remaining cells and exit, running nothing")
    args = ap.parse_args(argv)

    cells = remaining()
    if args.only:
        cells = [c for c in cells if c[0] == args.only]
    if args.system:
        cells = [c for c in cells if c[1] == args.system]
    if args.size:
        cells = [c for c in cells if c[2] == args.size]
    if args.seed is not None:
        cells = [c for c in cells if c[3] == args.seed]

    done = len(campaign_plan()) - len(remaining())
    print(f"[1b] {_stamp()} {done}/{len(campaign_plan())} cells already on "
          f"disk; {len(cells)} selected to run")
    if args.list:
        for cell in cells:
            print(f"  {describe_cell(*cell)}")
        return 0

    for i, cell in enumerate(cells, 1):
        label = describe_cell(*cell)
        print(f"[1b] {_stamp()} START {label} ({i}/{len(cells)})", flush=True)
        t0 = time.time()
        try:
            run_cell(*cell)
        except Exception as exc:                       # noqa: BLE001
            print(f"[1b] {_stamp()} ABORT {label} after "
                  f"{time.time() - t0:.0f}s: {exc!r}", flush=True)
            return 1
        print(f"[1b] {_stamp()} DONE  {label} in {time.time() - t0:.0f}s",
              flush=True)

    print(f"[1b] {_stamp()} all selected cells complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
