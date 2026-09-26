# experiments/exp5b/run/units_5b.py
"""Exp 5b's stage runner (design §7 stage 2): one small side's four units
in order (the final, 142000, 141000, 140000), each through Experiment 5's
writer into 5b's tree with 5b's attestation last. Refusal order: 5b
prereg tag → exp5-closed binding → frozen → imports → the power record
present → the projection an ancestor of HEAD → HALTED → (dry run stops
here) → the host record (written once). The size halts at load on a
re-read whose tensor digest is not Experiment 5's.

Usage: python -m experiments.exp5b.run.units_5b --size 6.9b --device cuda [--dry-run]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXP5B = Path(__file__).resolve().parents[1]
REPO = EXP5B.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import collect_5 as c5  # noqa: E402
from experiments.exp5 import slice_5 as sl5  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402
from experiments.exp5b import collect_5b as c5b  # noqa: E402


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def run(*, size, root=EXP5B, exp5_root=None, cache_root=None, device="cuda", dry_run=False, loaders=None,
        manifest=None, sl=None, host_meta=None, git_sha=None, tag_exists=None, blob_sha=None,
        verdict_sha=None, projection_commit=None, is_ancestor=None, power_present=None,
        halt_on_digest=True) -> None:
    prereg = b5b.require_prereg_5b(tag_exists=tag_exists, blob_sha=blob_sha)
    exp5_root = b5b.EXP5 if exp5_root is None else Path(exp5_root)
    b5b.require_exp5_closed_5b(tag_exists=tag_exists, blob_sha=blob_sha, verdict_sha=verdict_sha,
                               exp5_root=exp5_root)
    b5b.check_frozen_5b()
    b5b.check_imports_5b()
    root = Path(root)
    cache_root = cache_root if cache_root is not None else c5.CKPT_CACHE_5
    git_sha = git_sha or b5b.git_sha_5b()
    present = b5b.power_path_5b(root).is_file() if power_present is None else power_present
    if not present:
        raise RuntimeError("refusing: results/power_5b.json is not present — power ONCE precedes the tag")
    pc = b5b.projection_commit_5b() if projection_commit is None and is_ancestor is None else projection_commit
    anc = is_ancestor or b5b.is_ancestor_5b
    if not pc or not anc(pc, git_sha):
        raise RuntimeError("refusing: the projection is not committed in this HEAD's history "
                           "(design §7: the projection is sealed before any unit)")
    if b5b.halt_marker_path_5b(root, size).exists():
        raise RuntimeError(f"refusing: {size} is halted ({b5b.halt_marker_path_5b(root, size)})")
    if size not in b5b.small_sides_5b():
        raise RuntimeError(f"refusing: {size} is not a small side")
    manifest = manifest if manifest is not None else b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    steps = b5b.unit_steps_5b()
    pending = [st for st in steps if not b5b.unit_complete_5b(root, size, st)]
    if dry_run:
        host_state = "present" if b5b.host_record_path_5b(root).is_file() else "pending"
        print(f"[5b units] {size}: prereg {prereg['tag']!r}; host record {host_state}; steps {steps}; "
              f"would run {len(pending)} unit(s): {pending}", flush=True)
        return
    sl = sl if sl is not None else sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
    if loaders is None:
        loaders = c5.real_loaders_5()
    hp = b5b.host_record_path_5b(root)
    if host_meta is None:
        live = c5.host_record_5(device, c5.measure_transports_5(cache_root=cache_root))
    else:
        live = c5.host_record_5(device, host_meta["transports"], stack=host_meta["stack"],
                                gpu=host_meta["gpu"], python=host_meta["python"])
    if hp.is_file():
        host = json.loads(hp.read_text())
        if host["stack"] != live["stack"] or host["device"] != live["device"]:
            raise RuntimeError(f"refusing: the host record on disk ({host['stack']}, {host['device']}) "
                               f"is not this process's ({live['stack']}, {live['device']})")
    else:
        bad = b5.host_record_failures_5(live)
        if bad:
            raise RuntimeError(f"refusing: host record: {bad}")
        _write(hp, live)
        host = live
    battery = bt.load_battery()
    verify_fn = a2d.load_verify()
    pf = c5.Prefetcher(loaders, cache_root=cache_root)
    kw = dict(root=root, exp5_root=exp5_root, manifest=manifest, cache_root=cache_root, device=device,
              battery=battery, verify_fn=verify_fn, sl=sl, host=host, loaders=loaders, git_sha=git_sha,
              prefetcher=pf, halt_on_digest=halt_on_digest)
    for i, step in enumerate(steps):
        nxt = steps[i + 1] if i + 1 < len(steps) else None
        if nxt is not None and not b5b.unit_complete_5b(root, size, nxt):
            pf.start(size, b5.entry_5(manifest, size, nxt))
        c5b.run_unit_5b(size, step, why=("final" if step == b5.FINAL_STEP_5 else "member"), **kw)
    pf.wait()
    c5b.gate1_record_5b(root, host=host, git_sha=git_sha)
    print(f"[5b units] {size}: complete ({len(steps)} units)", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 5b: one small side's four units")
    ap.add_argument("--size", required=True)
    ap.add_argument("--root", default=str(EXP5B))
    ap.add_argument("--cache-root", default=str(c5.CKPT_CACHE_5))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(size=ar.size, root=Path(ar.root), cache_root=Path(ar.cache_root), device=ar.device, dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
