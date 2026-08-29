# experiments/exp2k/run/campaign_2k.py
"""Exp 2k campaign driver (design §10 dial g, §11): 1b then 410m, ONE
child process per size (one model load each), exp3's per-size preflight
(`experiments.exp3.run.preflight_paths --size <size> --dtype float32`)
before a size's tier unless --skip-preflight, stop on the first
non-zero exit or halt marker. It decides what runs; never what a number
means. Run detached (nohup + disown) with the watcher beside it.

Usage: python -m experiments.exp2k.run.campaign_2k [--only-size 1b] [--dry-run]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

EXP2K = Path(__file__).resolve().parents[1]
REPO = EXP2K.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2k.run.tier_2k import tier_complete  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2k campaign driver")
    ap.add_argument("--out-root", default=str(EXP2K))
    ap.add_argument("--only-size", choices=bk.SIZES_2K)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-preflight", action="store_true")
    ar = ap.parse_args(argv)
    sizes = [s for s in bk.SIZES_2K if not ar.only_size or s == ar.only_size]
    todo = [s for s in sizes if not tier_complete(ar.out_root, s)]
    print(f"[2k] sizes {sizes}, {len(todo)} to run: {todo}", flush=True)
    if ar.dry_run:
        for s in todo:
            subprocess.run([sys.executable, "-m", "experiments.exp2k.run.tier_2k", "--size", s,
                            "--out-root", ar.out_root, "--dry-run"], cwd=REPO)
        return 0
    t0, failed = time.time(), []
    for s in todo:
        if bk.halt_markers(ar.out_root):
            failed.append((s, "halt marker present"))
            print("  STOP: halt marker present", flush=True)
            break
        if not ar.skip_preflight:
            pf = subprocess.run([sys.executable, "-m", "experiments.exp3.run.preflight_paths",
                                 "--size", s, "--dtype", "float32"], cwd=REPO)
            if pf.returncode != 0:
                failed.append((s, f"preflight {s}/float32 FAILED"))
                print(f"  STOP: preflight {s}/float32 failed", flush=True)
                break
        t = time.time()
        r = subprocess.run([sys.executable, "-m", "experiments.exp2k.run.tier_2k", "--size", s,
                            "--out-root", ar.out_root], cwd=REPO)
        if r.returncode != 0:
            failed.append((s, f"exit {r.returncode}"))
            print(f"  FAIL {s}: exit {r.returncode}", flush=True)
            break
        print(f"  tier done {s} {(time.time() - t) / 60:.1f} min | elapsed "
              f"{(time.time() - t0) / 60:.1f} min", flush=True)
    print(f"[2k] {'complete' if not failed else 'STOPPED'}: {(time.time() - t0) / 60:.1f} min",
          flush=True)
    for s, why in failed:
        print(f"  FAILED {s}: {why}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
