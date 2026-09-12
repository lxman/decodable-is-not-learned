# experiments/exp4/run/reference_4.py
"""Exp 4 stage 1 — the reference stage (design §3.3, §3.7 gate 0,
§3.10; Task 3 brief + resolutions 1, 4, 7). Refusal order:
`require_prereg_4` -> `check_frozen_4` -> any `HALTED` marker anywhere
under `results/` refuses. Then, skip-if-complete (`unit_complete_4`),
in order:

1. The four references (`REFERENCES_4`), `refs=()` — no reference is
   aligned against anything on this first pass; `cross_reference_4`
   fills in the true 3-way ceiling afterward, from stored bytes, no
   model contact (resolution 7). `keep_activations=True`.
2. The four endpoints (`endpoint_<traj>`): `committed_step_digest_4`
   pinned against `info["tensor_digest"]`; a mismatch writes
   `collect_4.reference_halt_marker_path(root)` and exits 2 (SystemExit
   — never a bare crash, so a test can assert the halt without killing
   the runner). `refs = REFS_FOR_4[traj]`, `keep_activations=True`.
3. The four first grid points (`STAGE1_FIRST_UNITS_4`, via
   `loaders["step"]`, written under `unit_dir`): same digest pin,
   `keep_activations=False` (activations deleted after the write's own
   re-read), the checkpoint freed after.
4. The four inits (`INIT_KEY_4`): `committed_init_digest_4` pinned;
   `keep_activations=True`.
5. The seven ladder sizes (`LADDER_SIZES_4` minus `"12b"`, which is
   `ref_pythia_12b`): no digest pin; `refs` = the three non-Pythia
   references (`collect_4.non_pythia_refs_4()`); `keep_activations=
   True`. The 12b load (`ref_pythia_12b`, stage 1) prints the mlx
   reminder (dial j) — operational, not enforced.

After the last key: `eligibility_fn(root)` (resolution 1 — `main()`
resolves this lazily to `analyze_4.eligibility_table_4`, or leaves it
`None` and prints a deferral line, AFTER doing the loads, when Task 4
is not yet built) is called and its return written to
`battery_4.eligibility_path(root)`.

Usage: python -m experiments.exp4.run.reference_4 [--dry-run] [--only KEY]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXP4 = Path(__file__).resolve().parents[1]
REPO = EXP4.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp4 import _threads_4  # noqa: E402,F401 — BEFORE numpy: pins the BLAS threads

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2i.run._common_2i import git_sha as _git_sha, stack as _stack  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402


def _any_halted(root) -> bool:
    d = Path(root) / "results"
    if not d.exists():
        return False
    return any(d.rglob("HALTED"))


def _halt_reference(root, message: str) -> None:
    p = collect_4.reference_halt_marker_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(message + "\n")
    print(f"[4 reference] HALTED: {message}", flush=True)


def _keyed(key: str, only) -> bool:
    return only is None or only == key


def _process(*, model, tok, root, key_or_unit, family, info, battery, ref_tables, refs, batch_size,
            device, keep_activations, committed_digest, loaders, release_model=None):
    # The references' own activation files are on disk (keep_activations
    # =True for every one of the four) by the time any endpoint/first-
    # unit/init/ladder load runs, so CKA (design §3.2) is wired here
    # rather than left permanently None (fix round 1, finding 1).
    ref_activation_paths = collect_4.ref_activation_paths_4(root, refs)
    return collect_4.process_model_4(
        model, tok, key_or_unit=key_or_unit, family=family, info=info, root=root, battery=battery,
        ref_tables=ref_tables, ref_activation_paths=ref_activation_paths, batch_size=batch_size,
        device=device, keep_activations=keep_activations, sites=metric_4.sites_4(info["n_hidden"]),
        refs=refs, committed_digest=committed_digest, stack=_stack(), git_sha=_git_sha(),
        release_model=release_model)


def run(*, root=EXP4, device: str = "mps", loaders=None, dry_run: bool = False, only=None,
       eligibility_fn=None, tag_exists=None, blob_sha=None, cache_root=None) -> None:
    prereg = battery_4.require_prereg_4(tag_exists=tag_exists, blob_sha=blob_sha)
    battery_4.check_frozen_4()
    if _any_halted(root):
        raise RuntimeError(f"refusing: a HALTED marker exists under {Path(root) / 'results'}")

    if loaders is None:
        loaders = collect_4.real_loaders_4()
    cache_root = cache_root if cache_root is not None else battery_4.CKPT_CACHE_4
    battery = bt.load_battery()

    pending = []
    for ref in battery_4.REFERENCES_4:
        if _keyed(ref, only) and not battery_4.unit_complete_4(root, ref):
            pending.append(ref)
    for traj in battery_4.TRAJECTORIES_4:
        key = f"endpoint_{traj}"
        if _keyed(key, only) and not battery_4.unit_complete_4(root, key):
            pending.append(key)
    for traj, step in battery_4.STAGE1_FIRST_UNITS_4:
        if _keyed(traj, only) and not battery_4.unit_complete_4(root, (traj, step)):
            pending.append((traj, step))
    for traj in battery_4.TRAJECTORIES_4:
        key = battery_4.INIT_KEY_4[traj]
        if _keyed(key, only) and not battery_4.unit_complete_4(root, key):
            pending.append(key)
    for size in battery_4.LADDER_SIZES_4:
        if size == "12b":
            continue
        key = f"ladder_pythia_{size}"
        if _keyed(key, only) and not battery_4.unit_complete_4(root, key):
            pending.append(key)

    if dry_run:
        print(f"[4 reference] prereg tag {prereg['tag']!r}; would run {len(pending)} "
              f"unit(s): {pending}", flush=True)
        return

    # -------------------------------------------------------- (1) references
    for ref in battery_4.REFERENCES_4:
        if not _keyed(ref, only):
            continue
        if battery_4.unit_complete_4(root, ref):
            continue
        if ref == "ref_pythia_12b":
            print("[4 reference] ref_pythia_12b: the mlx text-server LaunchAgent must be "
                  "down before this load (dial j) — operational, not enforced", flush=True)
        model, tok, info = loaders["key"](ref, cache_root=cache_root, device=device)
        release = collect_4.release_once_4(loaders, model)
        try:
            _process(model=model, tok=tok, root=root, key_or_unit=ref, family=battery_4.FAMILY_OF_KEY_4[ref], info=info,
                    battery=battery, ref_tables={}, refs=(), batch_size=battery_4.BATCH_4[ref],
                    device=device, keep_activations=True, committed_digest=None, loaders=loaders,
                    release_model=release)
        finally:
            release()
        print(f"[4 reference] {ref}: done", flush=True)

    if all(battery_4.unit_complete_4(root, r) for r in battery_4.REFERENCES_4) and only is None:
        collect_4.cross_reference_4(root)
        print("[4 reference] cross_reference_4: the four references' align.json filled "
              "against each other (no model contact)", flush=True)

    # --------------------------------------------------------- (2) endpoints
    for traj in battery_4.TRAJECTORIES_4:
        key = f"endpoint_{traj}"
        if not _keyed(key, only):
            continue
        if battery_4.unit_complete_4(root, key):
            continue
        model, tok, info = loaders["key"](key, cache_root=cache_root, device=device)
        want = battery_4.committed_step_digest_4(traj, battery_4.ENDPOINT_STEP_4[traj])
        if info["tensor_digest"] != want:
            loaders["release"](model)
            _halt_reference(root, f"endpoint_{traj}: digest {info['tensor_digest']} != "
                                  f"committed {want}")
            raise SystemExit(2)
        release = collect_4.release_once_4(loaders, model)
        try:
            refs = battery_4.REFS_FOR_4[traj]
            ref_tables = collect_4.load_ref_tables_4(root, refs)
            _process(model=model, tok=tok, root=root, key_or_unit=key, family=battery_4.FAMILY_OF_KEY_4[key], info=info,
                    battery=battery, ref_tables=ref_tables, refs=refs,
                    batch_size=battery_4.BATCH_4[key], device=device, keep_activations=True,
                    committed_digest=want, loaders=loaders, release_model=release)
        finally:
            release()
        print(f"[4 reference] {key}: done", flush=True)

    # ------------------------------------------------------- (3) first units
    for traj, step in battery_4.STAGE1_FIRST_UNITS_4:
        if not _keyed(traj, only):
            continue
        if battery_4.unit_complete_4(root, (traj, step)):
            continue
        model, tok, info = loaders["step"](traj, step, cache_root=cache_root, device=device)
        want = battery_4.committed_step_digest_4(traj, step)
        if info["tensor_digest"] != want:
            loaders["release"](model)
            loaders["free_step"](traj, step, cache_root=cache_root)
            _halt_reference(root, f"{traj} step{step}: digest {info['tensor_digest']} != "
                                  f"committed {want}")
            raise SystemExit(2)
        release = collect_4.release_once_4(loaders, model)
        try:
            refs = battery_4.REFS_FOR_4[traj]
            ref_tables = collect_4.load_ref_tables_4(root, refs)
            _process(model=model, tok=tok, root=root, key_or_unit=(traj, step), family=collect_4.family_of_traj_4(traj),
                    info=info, battery=battery, ref_tables=ref_tables, refs=refs,
                    batch_size=battery_4.BATCH_4[traj], device=device, keep_activations=False,
                    committed_digest=want, loaders=loaders, release_model=release)
        finally:
            release()
            loaders["free_step"](traj, step, cache_root=cache_root)
        print(f"[4 reference] {traj} step{step} (first unit): done", flush=True)

    # -------------------------------------------------------------- (4) inits
    for traj in battery_4.TRAJECTORIES_4:
        key = battery_4.INIT_KEY_4[traj]
        if not _keyed(key, only):
            continue
        if battery_4.unit_complete_4(root, key):
            continue
        model, tok, info = loaders["key"](key, cache_root=cache_root, device=device)
        want = battery_4.committed_init_digest_4(traj)
        if info["tensor_digest"] != want:
            loaders["release"](model)
            _halt_reference(root, f"{key}: digest {info['tensor_digest']} != committed {want}")
            raise SystemExit(2)
        release = collect_4.release_once_4(loaders, model)
        try:
            refs = battery_4.REFS_FOR_4[traj]
            ref_tables = collect_4.load_ref_tables_4(root, refs)
            _process(model=model, tok=tok, root=root, key_or_unit=key, family=battery_4.FAMILY_OF_KEY_4[key], info=info,
                    battery=battery, ref_tables=ref_tables, refs=refs,
                    batch_size=battery_4.BATCH_4[key], device=device, keep_activations=True,
                    committed_digest=want, loaders=loaders, release_model=release)
        finally:
            release()
        print(f"[4 reference] {key}: done", flush=True)

    # ------------------------------------------------------------- (5) ladder
    non_pythia = collect_4.non_pythia_refs_4()
    ref_tables_ladder = None
    for size in battery_4.LADDER_SIZES_4:
        if size == "12b":
            continue
        key = f"ladder_pythia_{size}"
        if not _keyed(key, only):
            continue
        if battery_4.unit_complete_4(root, key):
            continue
        model, tok, info = loaders["key"](key, cache_root=cache_root, device=device)
        release = collect_4.release_once_4(loaders, model)
        try:
            if ref_tables_ladder is None:
                ref_tables_ladder = collect_4.load_ref_tables_4(root, non_pythia)
            _process(model=model, tok=tok, root=root, key_or_unit=key, family=battery_4.FAMILY_OF_KEY_4[key], info=info,
                    battery=battery, ref_tables=ref_tables_ladder, refs=non_pythia,
                    batch_size=battery_4.BATCH_4[key], device=device, keep_activations=True,
                    committed_digest=None, loaders=loaders, release_model=release)
        finally:
            release()
        print(f"[4 reference] {key}: done", flush=True)

    print("[4 reference] all 19 keys + 4 first units complete", flush=True)

    if eligibility_fn is not None and only is None:
        table = eligibility_fn(root)
        battery_4.eligibility_path(root).parent.mkdir(parents=True, exist_ok=True)
        battery_4.eligibility_path(root).write_text(json.dumps(table, indent=1))
        print(f"[4 reference] eligibility written to {battery_4.eligibility_path(root)}", flush=True)


def _resolve_eligibility_fn():
    try:
        from experiments.exp4 import analyze_4
        return analyze_4.eligibility_table_4
    except ImportError:
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 4 reference stage")
    ap.add_argument("--root", default=str(EXP4))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--only-eligibility", action="store_true",
                    help="write eligibility_4.json from analyze_4 without re-running the loads "
                         "(the deferred write, once Task 4 lands)")
    ar = ap.parse_args(argv)
    root = Path(ar.root)

    eligibility_fn = _resolve_eligibility_fn()

    if ar.only_eligibility:
        if eligibility_fn is None:
            print("[4 reference] eligibility deferred: analyze_4 not built", flush=True)
            return 0
        table = eligibility_fn(root)
        battery_4.eligibility_path(root).parent.mkdir(parents=True, exist_ok=True)
        battery_4.eligibility_path(root).write_text(json.dumps(table, indent=1))
        print(f"[4 reference] eligibility written to {battery_4.eligibility_path(root)}", flush=True)
        return 0

    run(root=root, device=ar.device, dry_run=ar.dry_run, only=ar.only, eligibility_fn=eligibility_fn)

    if eligibility_fn is None:
        print("[4 reference] eligibility deferred: analyze_4 not built", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
