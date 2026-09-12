# experiments/exp4/run/preflight_4.py
"""Exp 4 preflight (design §3.7 gate 1's ulp question, §3.10 dial k;
Task 3 resolution 8; final-review IMPORTANT 1) — the ONE sanctioned
model-contact check before the campaign. Prints only; asserts
afterwards that nothing under `root/results` changed. Applies
`check_frozen_4()` but NOT `require_prereg_4` (the preflight runs
before the tag exists).

(a) **Two LOADS of the same weights.** `ladder_pythia_2.8b` (cached
    weights, 2b's loader path) is loaded, collected on `antonym` and
    `add3_mid` under the pinned batching, RELEASED, and then loaded
    AGAIN and collected again — and the two collections are compared.
    The earlier build loaded once and collected twice from the same
    model object, which measures forward-pass determinism and cannot
    answer §3.7's question, which is about two LOADS of the same
    weights (a fresh `from_pretrained`, a fresh device placement, a
    fresh kernel-selection pass). Prints per-rung seconds, peak MPS
    memory (`torch.mps.driver_allocated_memory()`), the fp16
    finiteness of the hidden states, both loads' `tensor_digest`, and
    whether the two `X` arrays and their `set_tables_4` are
    BYTE-IDENTICAL ACROSS THE LOADS. If they are not, gate 1's
    identity requirement has to be relaxed to a k-NN-set identity plus
    a disclosed tolerance BEFORE the tag (design §3.7, and the freeze's
    R-2 on what becomes of `activation_sha_equal` and the pooled
    tables) — a call for Michael, not this script.

(b) **One cross-loader-path comparison**, on `antonym` only: the same
    Pythia-2.8b weights reached two ways — `ladder_pythia_2.8b` through
    2b's `from_pretrained` at the pinned `main` revision (side (a)'s
    first pass, reused) versus `load_step_4("pythia_2.8b", 143000)`
    through 2g's candidate-file loader with 2g's pinned config. This is
    design §7's ladder check (the freeze's F-5 / R-1: the analyzer
    records it from committed set tables as a DESCRIPTIVE field, and
    the program has never measured whether the two loader paths agree)
    rehearsed on one rung before the tag, so the projection has a
    measurement rather than an assumption. Prints both sides' tensor
    digests, the step side's digest against `committed_step_digest_4`,
    and whether the collected `X` and the set tables are identical. The
    step-143000 checkpoint is freed afterwards.

(c) **One interior checkpoint of the most expensive family** —
    `load_step_4("comma_7b", 10000)` end to end (download,
    candidate-file load, tensor digest against
    `committed_step_digest_4`), then freed: 2i stop #1's lesson, the
    loader rehearsed before the tag binds.

Usage: python -m experiments.exp4.run.preflight_4 [--checkpoint-step 10000]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

EXP4 = Path(__file__).resolve().parents[1]
REPO = EXP4.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp4 import _threads_4  # noqa: E402,F401 — BEFORE numpy: pins the BLAS threads
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402

PREFLIGHT_RUNGS = ("antonym", "add3_mid")
PREFLIGHT_KEY = "ladder_pythia_2.8b"
CROSS_TRAJ_4 = "pythia_2.8b"
CROSS_RUNG_4 = "antonym"


def _results_snapshot(root) -> set:
    d = Path(root) / "results"
    if not d.exists():
        return set()
    return {(str(p.relative_to(d)), p.stat().st_size) for p in d.rglob("*") if p.is_file()}


def _peak_mps_memory():
    try:
        import torch
        return int(torch.mps.driver_allocated_memory())
    except Exception:  # noqa: BLE001 — no MPS device, or a fake run
        return -1


def _collect(model, tok, battery, rung, *, sites, batch_size, device, key, label):
    import numpy as np
    t0 = time.time()
    out = collect_4.collect_rung_4(model, tok, "pythia", battery[rung], sites=sites,
                                   batch_size=batch_size, device=device, key=key)
    dt = time.time() - t0
    finite = bool(np.isfinite(out["X"].astype(np.float32)).all())
    print(f"[4 preflight] {label} {rung}: {dt:.1f}s finite={finite} shape={out['X'].shape} "
          f"peak_mps_bytes={_peak_mps_memory()}", flush=True)
    return out


def run(*, root=EXP4, device: str = "mps", loaders=None, rungs=PREFLIGHT_RUNGS,
       checkpoint_step: int = 10000, ladder_step=None) -> None:
    import numpy as np

    battery_4.check_frozen_4()
    before = _results_snapshot(root)
    if loaders is None:
        loaders = collect_4.real_loaders_4()
    battery = bt.load_battery()
    if ladder_step is None:
        ladder_step = battery_4.ENDPOINT_STEP_4[CROSS_TRAJ_4]
    print(f"[4 preflight] threads pinned: {_threads_4.thread_pin_record_4()}", flush=True)

    # ------------------------------------------ (a) TWO LOADS, same weights
    passes, digests = [], []
    batch_size = battery_4.BATCH_4[PREFLIGHT_KEY]
    for i in range(2):
        model, tok, info = loaders["key"](PREFLIGHT_KEY, device=device)
        try:
            sites = metric_4.sites_4(info["n_hidden"])
            per_rung = {}
            for rung in rungs:
                per_rung[rung] = _collect(model, tok, battery, rung, sites=sites,
                                          batch_size=batch_size, device=device,
                                          key=PREFLIGHT_KEY, label=f"load {i}")
            passes.append(per_rung)
            digests.append(info.get("tensor_digest"))
        finally:
            loaders["release"](model)
        print(f"[4 preflight] load {i} released ({PREFLIGHT_KEY}, digest {digests[-1]})",
              flush=True)

    print(f"[4 preflight] the two loads' tensor digests equal = "
          f"{digests[0] == digests[1]} ({digests[0]} / {digests[1]})", flush=True)
    for rung in rungs:
        x0, x1 = passes[0][rung]["X"], passes[1][rung]["X"]
        identical = bool(np.array_equal(x0, x1))
        s0 = collect_4.set_tables_4(x0)
        s1 = collect_4.set_tables_4(x1)
        sets_identical = bool(np.array_equal(s0, s1))
        print(f"[4 preflight] {rung}: X byte-identical across the two LOADS = {identical}; "
              f"set_tables_4 identical across the two LOADS = {sets_identical}", flush=True)

    # ------------------------------------- (b) the two loader paths, one rung
    cross_rung = CROSS_RUNG_4 if CROSS_RUNG_4 in rungs else rungs[0]
    model, tok, info_step = loaders["step"](CROSS_TRAJ_4, ladder_step, device=device)
    try:
        sites_step = metric_4.sites_4(info_step["n_hidden"])
        step_out = _collect(model, tok, battery, cross_rung, sites=sites_step,
                            batch_size=battery_4.BATCH_4[CROSS_TRAJ_4], device=device,
                            key=CROSS_TRAJ_4, label=f"step{ladder_step}")
    finally:
        loaders["release"](model)
        loaders["free_step"](CROSS_TRAJ_4, ladder_step)

    want_step = battery_4.committed_step_digest_4(CROSS_TRAJ_4, ladder_step)
    print(f"[4 preflight] {CROSS_TRAJ_4} step{ladder_step}: digest "
          f"{info_step.get('tensor_digest')} == committed {want_step} -> "
          f"{info_step.get('tensor_digest') == want_step}", flush=True)
    print(f"[4 preflight] loader paths: {PREFLIGHT_KEY} digest {digests[0]} vs "
          f"{CROSS_TRAJ_4} step{ladder_step} digest {info_step.get('tensor_digest')} -> "
          f"equal = {digests[0] == info_step.get('tensor_digest')}", flush=True)
    x_ladder, x_step = passes[0][cross_rung]["X"], step_out["X"]
    same_shape = x_ladder.shape == x_step.shape
    x_equal = bool(same_shape and np.array_equal(x_ladder, x_step))
    sets_equal = bool(same_shape and np.array_equal(collect_4.set_tables_4(x_ladder),
                                                    collect_4.set_tables_4(x_step)))
    print(f"[4 preflight] design §7 ladder check, {cross_rung} only: X identical across the "
          f"two LOADER PATHS = {x_equal}; set_tables_4 identical = {sets_equal} "
          f"(shapes {x_ladder.shape} / {x_step.shape})", flush=True)

    # ------------------------------ (c) one interior checkpoint, end to end
    model, tok, info = loaders["step"]("comma_7b", checkpoint_step, device=device)
    want = battery_4.committed_step_digest_4("comma_7b", checkpoint_step)
    print(f"[4 preflight] comma_7b step{checkpoint_step}: digest {info['tensor_digest']} == "
          f"committed {want} -> {info['tensor_digest'] == want}", flush=True)
    loaders["release"](model)
    loaders["free_step"]("comma_7b", checkpoint_step)

    after = _results_snapshot(root)
    if after != before:
        raise RuntimeError(f"preflight wrote under {Path(root) / 'results'}: "
                           f"{sorted(after - before)}")
    print("[4 preflight] complete: nothing written under results/", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 4 preflight (dial k)")
    ap.add_argument("--root", default=str(EXP4))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--checkpoint-step", type=int, default=10000)
    ap.add_argument("--ladder-step", type=int, default=None,
                    help="the Pythia-2.8b grid step for the cross-loader-path check "
                         "(default: the trajectory's endpoint, 143000)")
    ar = ap.parse_args(argv)
    run(root=Path(ar.root), device=ar.device, checkpoint_step=ar.checkpoint_step,
        ladder_step=ar.ladder_step)
    return 0


if __name__ == "__main__":
    sys.exit(main())
