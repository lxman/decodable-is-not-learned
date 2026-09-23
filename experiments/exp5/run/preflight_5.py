# experiments/exp5/run/preflight_5.py
"""Exp 5 preflight (design §7 stage 0): the one sanctioned model-contact
check before the campaign — on the box, after the tag, on Michael's
word. `check_frozen_5()` applies (NOT `require_prereg_5` — 4c's rule:
the tag is checked by the stage runners, not the preflight). Prints
only; asserts afterwards that nothing under `root/results` changed
(4c's `_results_snapshot`).

12b `step1000` (the spine's first point) and `step256` — the earliest
checkpoint any window can reach: the spine starts at `step1000`, so
t_lo >= 1000 and B- = {256, 512} at worst (freeze ruling B-3(c); the
design's `step1` is loadable by no window) — loaded through `load_checkpoint_5`: digest,
n_params, `slice_loss_5` finiteness (`finite`, `n_nonfinite`, `loss`)
and the per-unit peak (`torch.cuda.max_memory_allocated()`, guarded —
4c note 1) printed AFTER the loss so the batch is resident, then one
rung (`antonym`) generated and timed; released and freed.

Then the 1b FINAL run TWICE as a full unit (`run_unit_5`) into two
scratch roots and compared byte-for-byte: `_loss.json` (`loss` repr,
`per_doc_loss`), every rung's `bits`/`continuations`, `_checkpoint.
json`'s digest — IDENTICAL or the diff counts.

Usage: python -m experiments.exp5.run.preflight_5 --device cuda"""
from __future__ import annotations

import argparse
import json
import sys
import time
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

PREFLIGHT_SIZE_5 = "12b"
PREFLIGHT_STEPS_5 = (1000, 256)   # ruling B-3(c): step256, not step1
PREFLIGHT_RUNG_5 = "antonym"
FINAL_SIZE_5 = "1b"


def _results_snapshot(root) -> set:
    d = Path(root) / "results"
    if not d.exists():
        return set()
    return {(str(p.relative_to(d)), p.stat().st_size) for p in d.rglob("*") if p.is_file()}


def _peak_cuda_memory() -> int:
    try:
        import torch
    except ImportError:
        return -1
    try:
        if torch.cuda.is_available():
            return int(torch.cuda.max_memory_allocated())
    except Exception:  # noqa: BLE001 — no CUDA device, or a fake run
        pass
    return -1


def _compare_units(d1: Path, d2: Path) -> dict:
    """`{}` iff IDENTICAL; else `{artifact: reason}` for each divergence."""
    diffs = {}
    loss1 = json.loads((d1 / "_loss.json").read_text())
    loss2 = json.loads((d2 / "_loss.json").read_text())
    if repr(loss1["loss"]) != repr(loss2["loss"]) or loss1["per_doc_loss"] != loss2["per_doc_loss"]:
        diffs["_loss.json"] = "loss or per_doc_loss differ"
    for rung in b5.RUNGS:
        r1 = json.loads((d1 / f"{rung}.json").read_text())
        r2 = json.loads((d2 / f"{rung}.json").read_text())
        if r1["bits"] != r2["bits"] or r1["continuations"] != r2["continuations"]:
            diffs[rung] = "bits or continuations differ"
    ck1 = json.loads((d1 / "_checkpoint.json").read_text())
    ck2 = json.loads((d2 / "_checkpoint.json").read_text())
    if ck1["digest"] != ck2["digest"]:
        diffs["_checkpoint.json"] = f"digest {ck1['digest']} != {ck2['digest']}"
    return diffs


def run(*, root=EXP5, device: str = "cuda", cache_root=None, loaders=None, manifest=None, sl=None,
       host=None, battery=None, verify_fn=None, transports=None, probe_size=PREFLIGHT_SIZE_5,
       probe_steps=PREFLIGHT_STEPS_5, rung=PREFLIGHT_RUNG_5, final_size=FINAL_SIZE_5) -> None:
    b5.check_frozen_5()
    root = Path(root)
    before = _results_snapshot(root)
    cache_root = cache_root if cache_root is not None else c5.CKPT_CACHE_5
    print(f"[5 preflight] threads pinned: {_threads_5.thread_pin_record_5()}", flush=True)
    if loaders is None:
        loaders = c5.real_loaders_5()
    manifest = manifest if manifest is not None else b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    sl = sl if sl is not None else sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
    battery = battery if battery is not None else bt.load_battery()
    verify_fn = verify_fn if verify_fn is not None else a2d.load_verify()

    if host is None:
        transports = transports if transports is not None else c5.measure_transports_5(cache_root=cache_root)
        print(f"[5 preflight] transports: {transports}", flush=True)
        host = c5.host_record_5(device, transports)
    else:
        print(f"[5 preflight] transports (from the given host record): {host.get('transports')}",
              flush=True)

    for step in probe_steps:
        entry = b5.entry_5(manifest, probe_size, step)
        model, info = loaders["checkpoint"](probe_size, step, entry, cache_root=cache_root,
                                            device=device)
        try:
            digest = loaders["digest"](model)
            n_params = loaders["n_params"](model)
            loss = loaders["loss"](model, sl, batch_size=b5.LOSS_BATCH_5, device=device)
            peak = _peak_cuda_memory()
            print(f"[5 preflight] {probe_size} step{step}: digest {digest} n_params {n_params} "
                  f"loss.finite {loss['finite']} loss.n_nonfinite {loss['n_nonfinite']} "
                  f"loss {loss['loss']:.5f} peak_cuda_bytes {peak}", flush=True)
            runner = loaders["runner"](loaders["tokenizer"](probe_size), model)
            from experiments.exp2g.run.sweep_2g import evaluate_items
            t0 = time.time()
            ev = evaluate_items(runner, battery[rung], verify_fn)
            print(f"[5 preflight] {probe_size} step{step} {rung}: {time.time() - t0:.1f}s "
                  f"correct {ev['correct']}/{len(ev['bits'])}", flush=True)
        finally:
            loaders["release"](model)
            model = None
            loaders["free"](probe_size, step, cache_root)
        print(f"[5 preflight] {probe_size} step{step}: released and freed", flush=True)

    scratch = Path(cache_root) / "_preflight_units"
    run_dirs = {}
    for tag in ("run1", "run2"):
        run_root = scratch / tag
        c5.run_unit_5(final_size, b5.FINAL_STEP_5, root=run_root, manifest=manifest,
                      cache_root=cache_root, device=device, battery=battery, verify_fn=verify_fn,
                      sl=sl, host=host, loaders=loaders, git_sha="preflight", why="preflight")
        run_dirs[tag] = b5.unit_dir_5(run_root, final_size, b5.FINAL_STEP_5)
    diffs = _compare_units(run_dirs["run1"], run_dirs["run2"])
    if diffs:
        print(f"[5 preflight] {final_size} final loaded TWICE: DIFFERS: {diffs}", flush=True)
    else:
        print(f"[5 preflight] {final_size} final loaded TWICE: IDENTICAL", flush=True)

    after = _results_snapshot(root)
    if after != before:
        raise RuntimeError(f"preflight wrote under {root / 'results'}: {sorted(after - before)}")
    print("[5 preflight] complete: nothing written under results/", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 5 preflight (stage 0)")
    ap.add_argument("--device", default="cuda")
    ar = ap.parse_args(argv)
    run(device=ar.device)
    return 0


if __name__ == "__main__":
    sys.exit(main())
