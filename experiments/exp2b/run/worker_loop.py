"""Distributed-worker driver: run assigned (stage, size) combos in REVERSE
capability order (the Mac campaign works front-to-back; workers eat the queue
from the back), waiting for each combo's activation files to arrive via the
Mac-side sync loop.

Usage:  python -m run.worker_loop <processes> <stage:size> [...] [--shard=i/n]

--shard=i/n takes every n-th capability starting at i (after reversal) — the
mechanism behind Windows fleets of sharded single-process instances.
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
    args = [a for a in sys.argv[1:] if not a.startswith("--shard=")]
    shard = next((a.split("=")[1] for a in sys.argv[1:]
                  if a.startswith("--shard=")), None)
    processes = int(args[0])
    for combo in args[1:]:
        stage, size = combo.split(":")
        caps = list(reversed(default_caps(stage)))
        if shard:
            i, n = (int(x) for x in shard.split("/"))
            caps = caps[i::n]
        if not caps:
            continue
        mode = "untrained" if stage == "known_absent" else "trained"
        wait_for_activations(size, mode, caps)
        print(f"[worker] BEGIN {stage}/{size} ({len(caps)} caps, reversed)",
              flush=True)
        run_stage(stage, size, caps, processes=processes)
        print(f"[worker] DONE {stage}/{size}", flush=True)
    print("[worker] ALL ASSIGNMENTS DONE", flush=True)


if __name__ == "__main__":
    main()
