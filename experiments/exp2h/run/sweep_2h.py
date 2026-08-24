# experiments/exp2h/run/sweep_2h.py
"""Exp 2h stage 2 — the 6.9b checkpoint sweep (design §7-§9). A thin
delta on `experiments/exp2g/run/sweep_2g.py`: there is no stage-1
predictor seal to check here (design §7 — both predictors, 2d's
committed sampler counts and 2g's already-sealed predictor.json, were
fixed before this experiment's design was written), so the runner
refuses without the freeze tag `exp2h-preregistered`
(`analyze_2h.require_prereg_2h`) in place of 2g's two-stage predictor
seal. `analyze_2h.gate1_failures_69`/`load_sweep_69` are the
production re-derivation this runner's own records must satisfy —
this module writes exactly the shapes those functions expect.

Order, load-bearing, otherwise identical to 2g: (1) the prereg
refusal; (2) gate 1 on the final point, over all 34 rungs — 2c's own
loader path (a, `models.load_pythia("6.9b")`) vs 2h's checkpoint
loader on main's candidate files (b, `battery_2h.load_checkpoint_69`),
tensor digest + continuation identity; any diff writes the gate
record, a HALTED marker, and raises — the tree it leaves is
INSUFFICIENT_DATA for the analyzer by construction; (3) the grid in
ascending step order, one checkpoint at a time, streamed (download ->
eval -> delete), every (step, rung) record durable and skip-if-exists.

`evaluate_items` and `item_record` are reused directly from
`sweep_2g` by import: neither is bound to any exp2g-only per-size
global (both take `size`/`cap`/`seal` as plain arguments; the "seal"
argument accepted here is 2g's already-sealed predictor
(`{"tag": bg.SEAL_TAG, "sha256": battery_2h.PREDICTOR_2G_SHA}`), which
is what `analyze_2g.step_record_failures` — reused UNCHANGED inside
`analyze_2h.load_sweep_69` — checks each record against). Everything
bound to a 2g-only per-size global (`bg.sweep_rungs`, `bg.GRID`,
`bg.FINAL_STEP`, `bg.record_path`, ...) is redefined locally against
`battery_2h`'s own 6.9b paths/pins/34-rung set instead.

Usage: python -m experiments.exp2h.run.sweep_2h [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

EXP2H = Path(__file__).resolve().parents[1]
if str(EXP2H.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2H.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g.run.sweep_2g import evaluate_items, item_record  # noqa: E402
from experiments.exp2h import analyze_2h as ah  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402


def _stack() -> dict:
    try:
        import torch
        import transformers
        return {"torch": torch.__version__, "transformers": transformers.__version__}
    except ImportError:                     # fakes in tests
        return {"torch": "n/a", "transformers": "n/a"}


def _git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=bg.REPO,
                          capture_output=True, text=True).stdout.strip()


def _assert_provenance() -> None:
    import harness
    import models
    want = {"harness": bg.EXP2C, "models": bg.EXP2B}
    for name, root in want.items():
        got = Path(sys.modules[name].__file__).resolve()
        if root.resolve() not in got.parents:
            raise ImportError(f"{name} resolved to {got}, not under {root}")


def real_loaders() -> dict:
    from harness import HFRunner
    from models import load_pythia, load_tokenizer
    from experiments.exp2g import checkpoints_2g as ck

    def pythia(device):
        return load_pythia(bh.SIZE, device=device)

    def checkpoint(step, entry, cache_root, device):
        return bh.load_checkpoint_69(step, entry, cache_root=cache_root, device=device)

    return {"pythia": pythia, "checkpoint": checkpoint,
            "tokenizer": lambda: load_tokenizer(bh.SIZE),
            "runner": lambda tok, model: HFRunner(tok, model), "digest": ck.tensor_digest,
            "free": lambda step, cache_root: bh.free_69(step, cache_root)}


def _release(model) -> None:
    if model is None:      # a download failure can leave the caller's slot empty
        return
    try:
        import torch
        del model
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:      # noqa: BLE001 — fakes
        pass


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


# --------------------------------------------------------------- steps

def records_complete_69(out_root, step) -> bool:
    return all(bh.record_path_2h(out_root, step, r).exists() for r in bt.RUNGS)


def run_rungs_69(runner, step, ckpt, *, out_root, battery, verify_fn, seal) -> dict:
    out = {}
    for rung in bt.RUNGS:
        p = bh.record_path_2h(out_root, step, rung)
        if p.exists():
            out[rung] = json.loads(p.read_text())
            continue
        t = time.time()
        ev = evaluate_items(runner, battery[rung], verify_fn)
        rec = item_record(size=bh.SIZE, step=step, rung=rung, cap=battery[rung], ev=ev,
                          ckpt=ckpt, seal=seal, t_s=time.time() - t)
        _write(p, rec)
        out[rung] = rec
        print(f"[2h sweep] {bh.SIZE}/step{step}/{rung}: {ev['correct']}/{len(ev['bits'])}",
              flush=True)
    return out


# -------------------------------------------------------------- gate 1

def gate1_69(*, out_root, manifest, cache_root, device, battery, verify_fn, prereg,
            loaders) -> dict:
    from models import PYTHIA_SHAS
    t0 = time.time()
    rungs = tuple(bt.RUNGS)
    entry = bh.entry_69(manifest, bh.FINAL_STEP_69)
    # (a) 2c's own path: models.load_pythia("6.9b")
    tok, model = loaders["pythia"](device)
    try:
        digest_a = loaders["digest"](model)
        runner = loaders["runner"](tok, model)
        evs = {r: evaluate_items(runner, battery[r], verify_fn) for r in rungs}
    finally:
        _release(model)
        # _release only deletes ITS OWN local `model` name; the caller's
        # `model`/`runner` locals still hold references, so the object
        # would stay resident until they're reassigned.
        runner = None
        model = None
    counts = {r: evs[r]["correct"] for r in rungs}
    diffs = {r: [counts[r], bh.FINAL_COUNT_PIN_69[r]] for r in rungs
             if counts[r] != bh.FINAL_COUNT_PIN_69[r]}
    # (b) 2h's loader path on main's candidate files
    model_b = None
    try:
        model_b, info_b = loaders["checkpoint"](bh.FINAL_STEP_69, entry, cache_root, device)
        digest_b = loaders["digest"](model_b)
        runner_b = loaders["runner"](loaders["tokenizer"](), model_b)
        cont_diffs = {}
        for r in rungs:
            ev_b = evaluate_items(runner_b, battery[r], verify_fn)
            cont_diffs[r] = int(sum(1 for x, y in zip(ev_b["continuations"],
                                                       evs[r]["continuations"]) if x != y))
    finally:
        _release(model_b)
        loaders["free"](bh.FINAL_STEP_69, cache_root)
    rec = {"size": bh.SIZE, "rungs": list(rungs), "model_sha": PYTHIA_SHAS[bh.SIZE],
           "main_entry": entry, "pin_counts": dict(bh.FINAL_COUNT_PIN_69),
           "counts_2c_path": counts, "diffs_vs_pin": diffs,
           "digest_2c_path": digest_a, "digest_2h_path": digest_b,
           "digests_equal": digest_a == digest_b,
           "continuation_diffs_2h_path": cont_diffs, "loader_info_2h_path": info_b,
           "hub_step143000": manifest["hub_step143000"],
           "prereg_tag": prereg["tag"], "stack": _stack(), "git_sha": _git_sha(),
           "timing": {"seconds": round(time.time() - t0, 1)}}
    failures = ah.gate1_failures_69(rec)
    rec["pass"] = not failures
    rec["failures"] = failures
    if failures:
        _write(bh.gate1_path_2h(out_root), rec)
        bh.halt_marker_path_2h(out_root).parent.mkdir(parents=True, exist_ok=True)
        bh.halt_marker_path_2h(out_root).write_text("\n".join(failures) + "\n")
        raise RuntimeError(f"gate 1 {bh.SIZE} FAILED — halted: {failures[:3]}")
    # the final grid point's records come from run (a), 2c's own path
    ckpt = {"revision": "main", "commit": PYTHIA_SHAS[bh.SIZE], "kind": "2c-loader",
            "files": list(entry["files"]), "sha256": dict(entry["lfs_sha256"]),
            "config_source": f"{bh.REPO_69}@{PYTHIA_SHAS[bh.SIZE]}",
            "tokenizer_source": f"{bh.REPO_69}@{PYTHIA_SHAS[bh.SIZE]}"}
    seal = {"tag": bg.SEAL_TAG, "sha256": bh.PREDICTOR_2G_SHA}
    for r in rungs:
        _write(bh.record_path_2h(out_root, bh.FINAL_STEP_69, r),
               item_record(size=bh.SIZE, step=bh.FINAL_STEP_69, rung=r, cap=battery[r],
                           ev=evs[r], ckpt=ckpt, seal=seal, t_s=0.0))
    _write(bh.checkpoint_record_path_2h(out_root, bh.FINAL_STEP_69),
           {"size": bh.SIZE, "step": bh.FINAL_STEP_69, "revision": "main", "digest": digest_a,
            "digest_2h_path": digest_b, "sha256": dict(entry["lfs_sha256"]),
            "loading_info": info_b.get("loading_info"), "via": "gate 1"})
    # records first, the gate record last: gate1.json on disk implies the final step's records exist
    _write(bh.gate1_path_2h(out_root), rec)
    print(f"[2h sweep] gate 1 {bh.SIZE}: PASS (34 rungs, counts exact, digests "
          f"equal, 0 continuation diffs)", flush=True)
    return rec


# --------------------------------------------------------------- steps

def run_step_69(step, *, out_root, manifest, cache_root, device, battery, verify_fn,
                seal, loaders) -> None:
    if records_complete_69(out_root, step):
        return
    entry = bh.entry_69(manifest, step)
    t0 = time.time()
    model = None
    try:
        model, info = loaders["checkpoint"](step, entry, cache_root, device)
        digest = loaders["digest"](model)
        _write(bh.checkpoint_record_path_2h(out_root, step),
               {**info, "size": bh.SIZE, "step": int(step), "digest": digest,
                "download_seconds": round(time.time() - t0, 1)})
        runner = loaders["runner"](loaders["tokenizer"](), model)
        ckpt = {**info, "revision": entry["revision"], "commit": entry["commit"],
                "kind": entry["kind"], "files": list(entry["files"])}
        run_rungs_69(runner, step, ckpt, out_root=out_root, battery=battery,
                    verify_fn=verify_fn, seal=seal)
    finally:
        _release(model)
        loaders["free"](step, cache_root)
    print(f"[2h sweep] {bh.SIZE}/step{step} done in {time.time() - t0:.0f} s", flush=True)


def run_69(*, out_root=EXP2H, cache_root=bh.CKPT_CACHE_69, device="mps", dry_run=False,
          tag_exists=None, loaders=None) -> None:
    prereg = ah.require_prereg_2h(tag_exists=tag_exists)
    bh.check_frozen_2h()
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    manifest = bh.load_manifest_69(bh.CHECKPOINTS_PATH_69, sha_pin=ah.CHECKPOINTS_2H_SHA256)
    if bh.halt_marker_path_2h(out_root).exists():
        raise RuntimeError(f"{bh.SIZE}: the sweep is halted "
                           f"({bh.halt_marker_path_2h(out_root)}); the analyzer reads "
                           f"this tree as INSUFFICIENT_DATA")
    pending = [s for s in bh.GRID_69 if not records_complete_69(out_root, s)]
    if dry_run:
        print(f"[2h sweep] {bh.SIZE}: prereg tag {prereg['tag']!r}; gate 1 "
              f"{'done' if bh.gate1_path_2h(out_root).is_file() else 'pending'}; "
              f"would run {len(pending)} step(s): {pending}", flush=True)
        return
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    g1 = bh.gate1_path_2h(out_root)
    seal = {"tag": bg.SEAL_TAG, "sha256": bh.PREDICTOR_2G_SHA}
    if not g1.is_file():
        gate1_69(out_root=out_root, manifest=manifest, cache_root=cache_root, device=device,
                 battery=battery, verify_fn=verify_fn, prereg=prereg, loaders=loaders)
    else:
        bad = ah.gate1_failures_69(json.loads(g1.read_text()))
        if bad:
            raise RuntimeError(f"gate 1 {bh.SIZE} record on disk fails re-derivation: {bad[:3]}")
        if not records_complete_69(out_root, bh.FINAL_STEP_69):
            raise RuntimeError(f"gate 1 {bh.SIZE}: record present but the final step's "
                               f"records are incomplete — delete {g1} to re-run the gate")
    for step in bh.GRID_69:
        if step == bh.FINAL_STEP_69:
            continue
        run_step_69(step, out_root=out_root, manifest=manifest, cache_root=cache_root,
                    device=device, battery=battery, verify_fn=verify_fn, seal=seal,
                    loaders=loaders)
    print(f"[2h sweep] {bh.SIZE}: complete", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2h checkpoint sweep (6.9b)")
    ap.add_argument("--out-root", default=str(EXP2H))
    ap.add_argument("--cache-root", default=str(bh.CKPT_CACHE_69))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run_69(out_root=Path(ar.out_root), cache_root=Path(ar.cache_root), device=ar.device,
          dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
