# experiments/exp4/run/sweep_4.py
"""Exp 4 stage 2 — the per-trajectory checkpoint sweep (design §3.4,
§3.7 gate 1, §3.10; Task 3 brief + resolution 5). Refusal order:
`require_prereg_4` -> `check_frozen_4` -> `require_reference_seal_4`
(2i's `require_seal_2i` over `reference_seal_paths_4` — any failure
refuses) -> eligibility + power records present -> a HALTED marker for
THIS trajectory refuses.

Gate 1 FIRST: `loaders["step"](traj, endpoint)`; `info["tensor_digest"]`
must equal `committed_step_digest_4` AND the sealed
`reference/endpoint_<traj>/_load.json`'s `tensor_digest` — a mismatch
here halts before any processing. `process_model_4` into
`unit_dir(root, traj, endpoint)`, `keep_activations=False` (the
activation shas are computed before deletion — resolution 6, inside
`write_load_4`); then `gate1_rederive_4` (byte comparison against the
reference-stage endpoint) -> `gate1_record_4` written -> any
inequality (`gate1_failures_4`) halts with `f"gate 1 {traj}:
{failures}"` and exits 2.

Then every grid step ascending EXCEPT the endpoint and the first step
(already complete from the reference stage's stage-1-first-units pass
— asserted complete, else refuses): per-step digest pin, `process_model
_4`, activations deleted after the write's own re-read, the checkpoint
freed. Resume = skip-if-complete (`unit_complete_4`); an incomplete
unit dir is re-entered and its files overwritten (`write_load_4`
always rewrites every one of the 34 rungs' files for the unit it is
given).

Usage: python -m experiments.exp4.run.sweep_4 --traj KEY [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

EXP4 = Path(__file__).resolve().parents[1]
REPO = EXP4.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i.run._common_2i import git_sha as _git_sha, stack as _stack  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402


def require_reference_seal_4(root, *, tag_exists=None, blobs_bound=None, repo_root=None) -> None:
    """2i's `require_seal_2i` over `battery_4.reference_seal_paths_4`
    (paths relative to `root`, rejoined here since `require_seal_2i`
    itself relpaths against `repo_root`); any failure refuses."""
    root = Path(root)
    rr = Path(repo_root) if repo_root is not None else battery_4.REPO
    paths = [root / p for p in battery_4.reference_seal_paths_4(root)]
    r = an2i.require_seal_2i(battery_4.REFERENCE_SEAL_TAG_4, paths, tag_exists=tag_exists,
                             blobs_bound=blobs_bound, repo_root=rr)
    if r["failures"]:
        raise RuntimeError(f"refusing: reference seal: {r['failures'][0]}")


def _halt(root, traj, message: str) -> None:
    p = battery_4.halt_marker_path(root, traj)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(message + "\n")
    print(f"[4 sweep] HALTED: {message}", flush=True)


def run_gate1(*, traj, root, cache_root, device, battery, refs, ref_tables, loaders) -> dict:
    endpoint_step = battery_4.ENDPOINT_STEP_4[traj]
    model, tok, info = loaders["step"](traj, endpoint_step, cache_root=cache_root, device=device)
    want = battery_4.committed_step_digest_4(traj, endpoint_step)
    ref_rec = json.loads(battery_4.load_record_path(root, f"endpoint_{traj}").read_text())
    got = info["tensor_digest"]
    if got != want or got != ref_rec.get("tensor_digest"):
        loaders["release"](model)
        loaders["free_step"](traj, endpoint_step, cache_root=cache_root)
        _halt(root, traj, f"gate 1 {traj}: digest {got} != committed {want} / "
                          f"sealed {ref_rec.get('tensor_digest')}")
        raise SystemExit(2)

    t0 = time.time()
    ref_activation_paths = collect_4.ref_activation_paths_4(root, refs)
    try:
        collect_4.process_model_4(
            model, tok, key_or_unit=(traj, endpoint_step), family=collect_4.family_of_traj_4(traj),
            info=info, root=root, battery=battery, ref_tables=ref_tables,
            ref_activation_paths=ref_activation_paths, batch_size=battery_4.BATCH_4[traj],
            device=device, keep_activations=False, sites=metric_4.sites_4(info["n_hidden"]),
            refs=refs, committed_digest=want, stack=_stack(), git_sha=_git_sha())
    finally:
        loaders["release"](model)
        loaders["free_step"](traj, endpoint_step, cache_root=cache_root)

    g1 = battery_4.gate1_rederive_4(root, traj)
    sweep_rec = json.loads((battery_4.unit_dir(root, traj, endpoint_step) / "_load.json").read_text())
    rec = battery_4.gate1_record_4(traj=traj, sweep_rec=sweep_rec, reference_rec=ref_rec,
                                   sets_equal=g1["sets_equal"],
                                   activation_sha_equal=g1["activation_sha_equal"],
                                   digest_equal=g1["digest_equal"], seconds=time.time() - t0)
    battery_4.gate1_path(root, traj).parent.mkdir(parents=True, exist_ok=True)
    battery_4.gate1_path(root, traj).write_text(json.dumps(rec, indent=1))
    bad = battery_4.gate1_failures_4(rec, traj=traj)
    if bad:
        _halt(root, traj, f"gate 1 {traj}: {bad}")
        raise SystemExit(2)
    print(f"[4 sweep] gate 1 {traj}: PASS (34 rungs, digest+commit equal, 0 diffs)", flush=True)
    return rec


def run(*, traj, root=EXP4, cache_root=None, device: str = "mps", dry_run: bool = False,
       loaders=None, tag_exists=None, blob_sha=None, blobs_bound=None) -> None:
    prereg = battery_4.require_prereg_4(tag_exists=tag_exists, blob_sha=blob_sha)
    battery_4.check_frozen_4()
    require_reference_seal_4(root, tag_exists=tag_exists, blobs_bound=blobs_bound)
    if not battery_4.eligibility_path(root).is_file():
        raise RuntimeError(f"refusing: {battery_4.eligibility_path(root)} is not present")
    if not battery_4.power_path(root).is_file():
        raise RuntimeError(f"refusing: {battery_4.power_path(root)} is not present")
    if battery_4.halt_marker_path(root, traj).exists():
        raise RuntimeError(f"refusing: {traj} sweep is halted "
                           f"({battery_4.halt_marker_path(root, traj)})")

    cache_root = cache_root if cache_root is not None else battery_4.CKPT_CACHE_4
    endpoint_step = battery_4.ENDPOINT_STEP_4[traj]
    first_step = battery_4.FIRST_STEP_4[traj]
    rest = [s for s in battery_4.GRID_4[traj] if s not in (endpoint_step, first_step)]
    gate_done = battery_4.gate1_path(root, traj).is_file()
    pending = [s for s in rest if not battery_4.unit_complete_4(root, (traj, s))]

    if dry_run:
        print(f"[4 sweep] prereg tag {prereg['tag']!r}; gate 1 {traj} "
              f"{'done' if gate_done else 'pending'}; would run "
              f"{len(pending) + (0 if gate_done else 1)} step(s)", flush=True)
        return

    if not battery_4.unit_complete_4(root, (traj, first_step)):
        raise RuntimeError(f"refusing: {traj} step{first_step} (the reference stage's first "
                           f"grid point) is not complete — run the reference stage first")

    if loaders is None:
        loaders = collect_4.real_loaders_4()
    battery = bt.load_battery()
    refs = battery_4.REFS_FOR_4[traj]
    ref_tables = collect_4.load_ref_tables_4(root, refs)
    ref_activation_paths = collect_4.ref_activation_paths_4(root, refs)

    if not gate_done:
        run_gate1(traj=traj, root=root, cache_root=cache_root, device=device, battery=battery,
                 refs=refs, ref_tables=ref_tables, loaders=loaders)
    else:
        g1 = json.loads(battery_4.gate1_path(root, traj).read_text())
        bad = battery_4.gate1_failures_4(g1, traj=traj)
        if bad:
            raise RuntimeError(f"gate 1 {traj} record on disk fails re-derivation: {bad}")
        if not battery_4.unit_complete_4(root, (traj, endpoint_step)):
            raise RuntimeError(f"gate 1 {traj}: record present but step{endpoint_step}'s "
                               f"unit is incomplete — delete {battery_4.gate1_path(root, traj)} "
                               f"to re-run the gate")

    for step in rest:
        if battery_4.unit_complete_4(root, (traj, step)):
            continue
        model, tok, info = loaders["step"](traj, step, cache_root=cache_root, device=device)
        want = battery_4.committed_step_digest_4(traj, step)
        if info["tensor_digest"] != want:
            loaders["release"](model)
            loaders["free_step"](traj, step, cache_root=cache_root)
            _halt(root, traj, f"step{step} {traj}: digest {info['tensor_digest']} != "
                              f"committed {want}")
            raise SystemExit(2)
        t0 = time.time()
        try:
            collect_4.process_model_4(
                model, tok, key_or_unit=(traj, step), family=collect_4.family_of_traj_4(traj),
                info=info, root=root, battery=battery, ref_tables=ref_tables,
                ref_activation_paths=ref_activation_paths, batch_size=battery_4.BATCH_4[traj],
                device=device, keep_activations=False, sites=metric_4.sites_4(info["n_hidden"]),
                refs=refs, committed_digest=want, stack=_stack(), git_sha=_git_sha())
        finally:
            loaders["release"](model)
            loaders["free_step"](traj, step, cache_root=cache_root)
        print(f"[4 sweep] {traj} step{step}: done in {time.time() - t0:.0f}s", flush=True)

    print(f"[4 sweep] {traj}: complete", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 4 checkpoint sweep")
    ap.add_argument("--traj", required=True, choices=battery_4.TRAJECTORIES_4)
    ap.add_argument("--root", default=str(EXP4))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(traj=ar.traj, root=Path(ar.root), device=ar.device, dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
