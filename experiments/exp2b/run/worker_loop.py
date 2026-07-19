"""Distributed-worker driver: run assigned (stage, size) combos in REVERSE
capability order (the Mac campaign works front-to-back; workers eat the queue
from the back), waiting for each combo's activation files to arrive via the
Mac-side sync loop.

Usage:  python -m run.worker_loop <processes> <stage:size> [stage:size ...]
"""

from __future__ import annotations

import sys
import time

from activations import activations_path
from run.battery_sets import scored_battery  # noqa: F401
from run.run_probes_2b import default_caps, run_stage


def wait_for_activations(size: str, mode: str, caps: list[str]) -> None:
    missing = [c for c in caps if not activations_path(size, mode, c).exists()]
    while missing:
        print(f"[worker] waiting for {len(missing)} {size}/{mode} activation "
              f"file(s) (e.g. {missing[0]})...", flush=True)
        time.sleep(120)
        missing = [c for c in caps if not activations_path(size, mode, c).exists()]


def main() -> None:
    processes = int(sys.argv[1])
    for combo in sys.argv[2:]:
        stage, size = combo.split(":")
        caps = list(reversed(default_caps(stage)))
        mode = "untrained" if stage == "known_absent" else "trained"
        wait_for_activations(size, mode, caps)
        print(f"[worker] BEGIN {stage}/{size} ({len(caps)} caps, reversed)",
              flush=True)
        run_stage(stage, size, caps, processes=processes)
        print(f"[worker] DONE {stage}/{size}", flush=True)
    print("[worker] ALL ASSIGNMENTS DONE", flush=True)


if __name__ == "__main__":
    main()
