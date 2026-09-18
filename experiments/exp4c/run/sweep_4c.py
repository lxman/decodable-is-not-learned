# experiments/exp4c/run/sweep_4c.py
"""Exp 4c's one stage runner (design `experiment-4c-design.md`
§3.7-§3.10; Task 3 brief step 4): unlike exp4, there is no separate
reference stage — the ONLY reference this build ever writes is the
OLMo-2 13B thin endpoint (`battery_4c.THIN_ENDPOINT_KEY_4C`, since
Exp 4 never built a 13B reference — B-1), written under THIS run's
own `root` on demand. The Pythia 6.9b gate rereads Exp 4's own
committed `ladder_pythia_6.9b` table under `root4` instead.

Refusal order: `battery_4c.require_prereg_4c` -> `battery_4c.
check_frozen_4c` -> `an2i.require_seal_2i` over Exp 4's own reference
seal tag (`battery_4.REFERENCE_SEAL_TAG_4`, the five keys exp4c reuses
from Exp 4's tree — `battery_4c.exp4_reference_paths_4c(root4)`; any
failure refuses) -> `results/power_4c.json` present (else "run
power_4c.main first — the record precedes the tag": the power record
precedes the tag, same as every other campaign in this program) -> a
HALTED marker for THIS trajectory refuses.

Then, for `olmo2_13b` only and only if its thin endpoint is not
already complete: the thin endpoint (`run_thin_endpoint`). Gate 1
(`run_gate1`) if not already passed: the sweep's own endpoint step,
digest-pinned twice (against the committed outcome AND the gate-1
reference's own measured digest) before any processing, `process_model
_4c` into `sweep/<traj>/step<endpoint>`, then a byte rederivation
(`gate1_rederive_4c`) against the reference named by `battery_4c.
GATE1_REFERENCE_4C[traj]` -- any inequality (`gate1_failures_4c`) halts
WITH the gate1.json record on disk (it is written before the check)
and exits 2. Then every remaining unit — `battery_4c.INIT_STEP_4C`
(step 0, the real init checkpoint on both runs) FIRST, then the rest
of `battery_4c.GRID_4C[traj]` ascending, excluding the endpoint (gate
1's own unit) — each: skip if complete (resume); the step's own
digest pin; `process_model_4c`; the checkpoint freed either way.

Usage: python -m experiments.exp4c.run.sweep_4c --traj KEY [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

EXP4C = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP4C.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp4 import _threads_4  # noqa: E402,F401 — BEFORE numpy: pins the BLAS threads

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i.run._common_2i import git_sha as _git_sha, stack as _stack  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402
from experiments.exp4c import battery_4c  # noqa: E402
from experiments.exp4c import collect_4c  # noqa: E402

EXP4 = battery_4.EXP4


def _halt(root, traj, message: str) -> None:
    p = battery_4.halt_marker_path(root, traj)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(message + "\n")
    print(f"[4c sweep] HALTED: {message}", flush=True)


def _process(*, model, tok, info, key_or_unit, traj, root, battery, ref_tables, refs,
            committed_digest, loaders, free, device):
    box = [model]
    del model                          # ratification open item 1: the box is the only holder,
    release = collect_4.release_once_4(loaders, box[0])   # and process_model_4c empties it
    try:
        return collect_4c.process_model_4c(
            box, tok, key_or_unit=key_or_unit, family=battery_4c.FAMILY_OF_TRAJ_4C[traj],
            info=info, root=root, battery=battery, ref_tables=ref_tables,
            batch_size=battery_4c.BATCH_4C[key_or_unit if isinstance(key_or_unit, str) else traj],
            device=device, sites=metric_4.sites_4(info["n_hidden"]), refs=refs,
            committed_digest=committed_digest, stack=_stack(), git_sha=_git_sha(),
            release_model=release)
    finally:
        release()
        free()


def run_thin_endpoint(*, root, root4, device, battery, ref_tables, loaders):
    """The 13B thin endpoint — written once, under `root`, the first
    time this run needs it (B-1: Exp 4 holds no committed 13B
    reference)."""
    key, traj = battery_4c.THIN_ENDPOINT_KEY_4C, "olmo2_13b"
    model, tok, info = loaders["thin"](key, device=device)
    want = battery_4c.committed_step_digest_4c(traj, battery_4c.ENDPOINT_STEP_4C[traj])
    if info["tensor_digest"] != want:
        loaders["release"](model)
        _halt(root, traj, f"thin endpoint {key}: digest {info['tensor_digest']} != committed {want}")
        raise SystemExit(2)
    return _process(model=model, tok=tok, info=info, key_or_unit=key, traj=traj, root=root,
                    battery=battery, ref_tables=ref_tables, refs=battery_4c.REFS_FOR_4C[traj],
                    committed_digest=want, loaders=loaders, free=lambda: None, device=device)


def run_gate1(*, traj, root, root4, cache_root, device, battery, refs, ref_tables, loaders):
    endpoint = battery_4c.ENDPOINT_STEP_4C[traj]
    ref_dir = battery_4c.gate1_reference_dir_4c(root, root4, traj)
    where, ref_key = battery_4c.GATE1_REFERENCE_4C[traj]
    if not battery_4.unit_complete_4(root4 if where == "exp4" else root, ref_key):
        raise RuntimeError(f"gate 1 {traj}: the reference unit {ref_dir} is not complete")
    ref_rec = json.loads((ref_dir / "_load.json").read_text())

    model, tok, info = loaders["step"](traj, endpoint, cache_root=cache_root, device=device)
    want = battery_4c.committed_step_digest_4c(traj, endpoint)
    got = info["tensor_digest"]
    if got != want or got != ref_rec.get("tensor_digest"):
        loaders["release"](model)
        loaders["free_step"](traj, endpoint, cache_root=cache_root)
        _halt(root, traj, f"gate 1 {traj}: digest {got} != committed {want} / reference "
                          f"{ref_rec.get('tensor_digest')}")
        raise SystemExit(2)

    t0 = time.time()
    _process(model=model, tok=tok, info=info, key_or_unit=(traj, endpoint), traj=traj, root=root,
             battery=battery, ref_tables=ref_tables, refs=refs, committed_digest=want,
             loaders=loaders, free=lambda: loaders["free_step"](traj, endpoint, cache_root=cache_root),
             device=device)

    der = battery_4c.gate1_rederive_4c(root, root4, traj)
    sweep_rec = json.loads((battery_4.unit_dir(root, traj, endpoint) / "_load.json").read_text())
    rec = battery_4c.gate1_record_4c(traj=traj, sweep_rec=sweep_rec, reference_rec=ref_rec,
                                     rederived=der, seconds=time.time() - t0)
    p = battery_4.gate1_path(root, traj)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1))
    bad = battery_4c.gate1_failures_4c(rec, traj=traj)
    if bad:
        _halt(root, traj, f"gate 1 {traj}: {bad[:3]}")
        raise SystemExit(2)
    print(f"[4c sweep] gate 1 {traj}: PASS (34 rungs, digest equal, 0 byte diffs vs "
          f"{rec['reference_root']}/{rec['reference_key']})", flush=True)
    return rec


def run(*, traj, root=EXP4C, root4=EXP4, cache_root=None, device: str = "mps",
       dry_run: bool = False, loaders=None, tag_exists=None, blob_sha=None,
       blobs_bound=None) -> None:
    prereg = battery_4c.require_prereg_4c(tag_exists=tag_exists, blob_sha=blob_sha)
    battery_4c.check_frozen_4c()
    seal = an2i.require_seal_2i(battery_4.REFERENCE_SEAL_TAG_4,
                                battery_4c.exp4_reference_paths_4c(root4),
                                tag_exists=tag_exists, blobs_bound=blobs_bound, repo_root=REPO)
    if seal["failures"]:
        raise RuntimeError(f"refusing: exp4 reference seal: {seal['failures'][0]}")
    power_p = Path(root) / "results" / "power_4c.json"
    if not power_p.is_file():
        raise RuntimeError(f"refusing: {power_p} is not present — run power_4c.main first — "
                           f"the record precedes the tag")
    if battery_4.halt_marker_path(root, traj).exists():
        raise RuntimeError(f"refusing: {traj} sweep is halted "
                           f"({battery_4.halt_marker_path(root, traj)})")

    cache_root = cache_root if cache_root is not None else battery_4c.CKPT_CACHE_4C
    endpoint = battery_4c.ENDPOINT_STEP_4C[traj]
    units = [battery_4c.INIT_STEP_4C] + [s for s in battery_4c.GRID_4C[traj] if s != endpoint]
    pending = [s for s in units if not battery_4.unit_complete_4(root, (traj, s))]
    gate_done = battery_4.gate1_path(root, traj).is_file()
    thin_needed = (traj == "olmo2_13b"
                  and not battery_4.unit_complete_4(root, battery_4c.THIN_ENDPOINT_KEY_4C))

    if dry_run:
        print(f"[4c sweep] prereg tag {prereg['tag']!r}; thin endpoint "
              f"{'pending' if thin_needed else 'done/n-a'}; gate 1 {traj} "
              f"{'done' if gate_done else 'pending'}; would run {len(pending)} unit(s)",
              flush=True)
        return

    if loaders is None:
        loaders = collect_4c.real_loaders_4c()
    battery = bt.load_battery()
    refs = battery_4c.REFS_FOR_4C[traj]
    ref_tables = collect_4.load_ref_tables_4(root4, refs)

    if thin_needed:
        run_thin_endpoint(root=root, root4=root4, device=device, battery=battery,
                          ref_tables=ref_tables, loaders=loaders)

    if not gate_done:
        run_gate1(traj=traj, root=root, root4=root4, cache_root=cache_root, device=device,
                 battery=battery, refs=refs, ref_tables=ref_tables, loaders=loaders)
    else:
        g1 = json.loads(battery_4.gate1_path(root, traj).read_text())
        bad = battery_4c.gate1_failures_4c(g1, traj=traj)
        if bad:
            raise RuntimeError(f"gate 1 {traj} record on disk fails re-derivation: {bad}")
        if not battery_4.unit_complete_4(root, (traj, endpoint)):
            raise RuntimeError(f"gate 1 {traj}: record present but step{endpoint}'s unit is "
                               f"incomplete — delete {battery_4.gate1_path(root, traj)} to "
                               f"re-run the gate")

    for step in units:
        if battery_4.unit_complete_4(root, (traj, step)):
            continue
        model, tok, info = loaders["step"](traj, step, cache_root=cache_root, device=device)
        want = battery_4c.committed_step_digest_4c(traj, step)
        if info["tensor_digest"] != want:
            loaders["release"](model)
            loaders["free_step"](traj, step, cache_root=cache_root)
            _halt(root, traj, f"step{step} {traj}: digest {info['tensor_digest']} != "
                              f"committed {want}")
            raise SystemExit(2)
        t0 = time.time()
        _process(model=model, tok=tok, info=info, key_or_unit=(traj, step), traj=traj, root=root,
                 battery=battery, ref_tables=ref_tables, refs=refs, committed_digest=want,
                 loaders=loaders, free=lambda s=step: loaders["free_step"](traj, s, cache_root=cache_root),
                 device=device)
        print(f"[4c sweep] {traj} step{step}: done in {time.time() - t0:.0f}s", flush=True)

    print(f"[4c sweep] {traj}: complete", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 4c checkpoint sweep")
    ap.add_argument("--traj", required=True, choices=battery_4c.TRAJECTORIES_4C)
    ap.add_argument("--root", default=str(EXP4C))
    ap.add_argument("--root4", default=str(EXP4))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(traj=ar.traj, root=Path(ar.root), root4=Path(ar.root4), device=ar.device,
       dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
