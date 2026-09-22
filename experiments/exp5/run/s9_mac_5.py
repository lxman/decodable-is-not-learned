# experiments/exp5/run/s9_mac_5.py
"""Exp 5 S9 (design §5: "cross-host drift, both ways", non-gating).
Post-campaign, on the Mac (`--device mps`): one window unit re-run in
the Mac's own stack and compared to the box's committed counts for the
same unit under gate 1's tolerance — the drift between the two stacks
measured at an interior checkpoint, not only at the finals. The two
units S9 names (design §5): the bracket's t_lo of the pairs (410m, 1b)
and (2.8b, 6.9b), read from the respective search logs (`--partner`);
an explicit `--step` overrides.

The unit lands FLAT under `results/s9/<size>/step<k>/` (its own 36 + 1
files, not a nested `results/units/...` tree) — `run_unit_5` writes to
a private scratch root first (its own `unit_dir_5` is hardcoded to
`results/units/...`), then the files are copied into place and the
scratch is discarded. The Mac's host record (`host_record_5("mps", ...)`
with both transports None/"classic" — the Mac never streams the box's
xet path) is write-once at `results/s9/host_mac_5.json`.

Usage: python -m experiments.exp5.run.s9_mac_5 --size 1b --partner 410m
       [--device mps]"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

EXP5 = Path(__file__).resolve().parents[1]
REPO = EXP5.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import collect_5 as c5  # noqa: E402
from experiments.exp5 import slice_5 as sl5  # noqa: E402

HOST_MAC_TRANSPORTS_5 = {"classic_mbps": None, "xet_mbps": None, "used": "classic"}


def s9_host_path_5(root) -> Path:
    return Path(root) / "results" / "s9" / "host_mac_5.json"


def mac_host_record_5(*, write_once_root=None, stack=None, gpu=None, python=None) -> dict:
    """Write-once, like the box's `host_5.json`: a second call with the
    same `write_once_root` returns the ON-DISK record, whatever the
    caller passes for stack/gpu/python this time."""
    p = s9_host_path_5(write_once_root) if write_once_root is not None else None
    if p is not None and p.is_file():
        return json.loads(p.read_text())
    host = c5.host_record_5("mps", HOST_MAC_TRANSPORTS_5, stack=stack, gpu=gpu, python=python)
    if p is not None:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(host, indent=1))
    return host


def _copy_unit(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in b5.unit_files_5() + ("_unit.json",):
        shutil.copy2(src / name, dst / name)


def run(*, size, step, root=EXP5, cache_root=None, device: str = "mps", loaders=None,
       manifest=None, sl=None, battery=None, verify_fn=None, host=None, box_counts=None) -> dict:
    """Runs ONE unit on the Mac, lands it at `s9_dir_5(root, size,
    step)`, and (when `box_counts` is given — the box's committed
    per-rung counts for this unit) prints and returns the tolerance
    comparison. Never raises on a tolerance miss — S9 is non-gating."""
    root = Path(root)
    cache_root = cache_root if cache_root is not None else c5.CKPT_CACHE_5
    manifest = manifest if manifest is not None else b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    sl = sl if sl is not None else sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
    battery = battery if battery is not None else bt.load_battery()
    verify_fn = verify_fn if verify_fn is not None else a2d.load_verify()
    if loaders is None:
        loaders = c5.real_loaders_5()
    host = host if host is not None else mac_host_record_5(write_once_root=root)

    scratch = Path(cache_root) / "_s9_scratch"
    rec = c5.run_unit_5(size, step, root=scratch, manifest=manifest, cache_root=cache_root,
                        device=device, battery=battery, verify_fn=verify_fn, sl=sl, host=host,
                        loaders=loaders, git_sha="s9", why="s9")
    src = b5.unit_dir_5(scratch, size, step)
    dst = b5.s9_dir_5(root, size, step)
    _copy_unit(src, dst)
    shutil.rmtree(b5.units_root_5(scratch), ignore_errors=True)

    counts = {r: json.loads((dst / f"{r}.json").read_text())["correct"] for r in b5.RUNGS}
    loss = json.loads((dst / "_loss.json").read_text())["loss"]
    out = {"size": size, "step": int(step), "device": device, "counts": counts, "loss": loss,
          "action": rec["action"]}
    if box_counts is not None:
        out["box_counts"] = box_counts
        out["failures"] = b5.tolerance_failures_5(counts, box_counts, label=f"S9 {size}/step{step}")
        out["sum_abs_diff"] = sum(abs(counts[r] - box_counts[r]) for r in b5.RUNGS)
        out["max_abs_diff"] = max(abs(counts[r] - box_counts[r]) for r in b5.RUNGS)
        print(f"[5 s9] {size}/step{step}: {'PASS' if not out['failures'] else 'TOLERANCE MISS'} "
              f"(sum |Δ| {out['sum_abs_diff']}, max |Δ| {out['max_abs_diff']}, non-gating)",
              flush=True)
    print(f"[5 s9] {size}/step{step}: loss {loss:.5f}", flush=True)
    return out


def _bracket_lo(root, size, partner) -> int:
    log = json.loads(b5.search_log_path_5(root, size).read_text())
    return int(log["pairs"][partner]["plan"]["bracket"][0])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 5 S9: one cross-host unit on the Mac")
    ap.add_argument("--size", required=True)
    ap.add_argument("--step", type=int)
    ap.add_argument("--partner", help="read the bracket's t_lo from --size's search log for this "
                    "small partner instead of an explicit --step")
    ap.add_argument("--root", default=str(EXP5))
    ap.add_argument("--cache-root", default=str(c5.CKPT_CACHE_5))
    ap.add_argument("--device", default="mps")
    ar = ap.parse_args(argv)
    step = ar.step if ar.step is not None else _bracket_lo(Path(ar.root), ar.size, ar.partner)
    run(size=ar.size, step=step, root=Path(ar.root), cache_root=Path(ar.cache_root), device=ar.device)
    return 0


if __name__ == "__main__":
    sys.exit(main())
