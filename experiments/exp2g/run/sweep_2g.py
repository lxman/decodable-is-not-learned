# experiments/exp2g/run/sweep_2g.py
"""Exp 2g stage 2 — the checkpoint sweep (design §4, §5 G-1, §9).

Order, load-bearing: (1) the seal (require_seal) — no checkpoint loads
without `exp2g-predictor-sealed`; (2) gate 1 on the final point —
2c's own loader must reproduce m4's counts exactly, and 2g's
checkpoint loader on main's candidate files must give the same tensor
digest and byte-identical continuations; any diff writes the gate
record, a HALTED marker, and raises — the tree it leaves is
INSUFFICIENT_DATA for the analyzer by construction; (3) the grid in
ascending step order, one checkpoint at a time, streamed (download →
eval → delete), every (step, rung) record durable and skip-if-exists.

Usage: python -m experiments.exp2g.run.sweep_2g --size 2.8b [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

EXP2G = Path(__file__).resolve().parents[1]
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2g import analyze_2g as an  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2d import analyze_2d as a2d  # noqa: E402


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

    def pythia(size, device):
        return load_pythia(size, device=device)

    def checkpoint(size, step, entry, cache_root, device):
        return ck.load_checkpoint(size, step, entry, cache_root=cache_root, device=device)

    return {"pythia": pythia, "checkpoint": checkpoint, "tokenizer": load_tokenizer,
            "runner": lambda tok, model: HFRunner(tok, model), "digest": ck.tensor_digest,
            "free": ck.free_checkpoint}


def _release(model) -> None:
    try:
        import torch
        del model
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:      # noqa: BLE001 — fakes
        pass


# --------------------------------------------------------------- eval

def evaluate_items(runner, cap: dict, verify_fn) -> dict:
    from harness import MAX_NEW_TOKENS, render_prompt
    shots = [tuple(s) for s in cap["shots"]][:bg.N_SHOTS]
    prompts = [render_prompt(it["question"], shots) for it in cap["eval_items"]]
    preds = runner.generate(prompts, MAX_NEW_TOKENS[cap["answer_type"]])
    if len(preds) != len(cap["eval_items"]):
        raise RuntimeError("generate returned the wrong number of continuations")
    bits = [int(bool(verify_fn(p, it["answer"], cap["answer_type"])))
            for p, it in zip(preds, cap["eval_items"])]
    return {"correct": int(sum(bits)), "bits": bits, "continuations": list(preds)}


def item_record(*, size, step, rung, cap, ev, ckpt, seal, t_s) -> dict:
    from harness import MAX_NEW_TOKENS
    return {"rung": rung, "size": size, "step": int(step), "revision": ckpt["revision"],
            "commit": ckpt["commit"], "kind": ckpt["kind"], "files": list(ckpt["files"]),
            "weight_sha256": dict(ckpt.get("sha256", {})),
            "config_source": ckpt.get("config_source"),
            "tokenizer_source": ckpt.get("tokenizer_source"),
            "items_sha256": cap["items_sha256"], "n": len(ev["bits"]),
            "correct": ev["correct"], "bits": ev["bits"],
            "continuations": ev["continuations"],
            "max_new_tokens": int(MAX_NEW_TOKENS[cap["answer_type"]]),
            "n_shots": bg.N_SHOTS, "dtype": "float16", "answer_type": cap["answer_type"],
            "verify": "2c normalize + exact match under 3c's total wrapper",
            "stack": _stack(), "git_sha": _git_sha(), "predictor_sha": seal["sha256"],
            "seal_tag": seal["tag"], "seconds": round(t_s, 2)}


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def records_complete(out_root, size, step) -> bool:
    return all(bg.record_path(out_root, size, step, r).exists()
               for r in bg.sweep_rungs(size))


def run_rungs(runner, size, step, ckpt, *, out_root, battery, verify_fn, seal) -> dict:
    out = {}
    for rung in bg.sweep_rungs(size):
        p = bg.record_path(out_root, size, step, rung)
        if p.exists():
            out[rung] = json.loads(p.read_text())
            continue
        t = time.time()
        ev = evaluate_items(runner, battery[rung], verify_fn)
        rec = item_record(size=size, step=step, rung=rung, cap=battery[rung], ev=ev,
                          ckpt=ckpt, seal=seal, t_s=time.time() - t)
        _write(p, rec)
        out[rung] = rec
        print(f"[2g sweep] {size}/step{step}/{rung}: {ev['correct']}/{len(ev['bits'])}",
              flush=True)
    return out


# -------------------------------------------------------------- gate 1

def gate1(size, *, out_root, manifest, cache_root, device, battery, verify_fn, seal,
          loaders) -> dict:
    from models import PYTHIA_SHAS
    t0 = time.time()
    rungs = bg.sweep_rungs(size)
    entry = ck.entry_for(manifest, size, bg.FINAL_STEP)
    # (a) 2c's own path
    tok, model = loaders["pythia"](size, device)
    try:
        digest_a = loaders["digest"](model)
        runner = loaders["runner"](tok, model)
        evs = {r: evaluate_items(runner, battery[r], verify_fn) for r in rungs}
    finally:
        _release(model)
    counts = {r: evs[r]["correct"] for r in rungs}
    diffs = {r: [counts[r], bg.FINAL_COUNT_PIN[size][r]] for r in rungs
             if counts[r] != bg.FINAL_COUNT_PIN[size][r]}
    # (b) 2g's loader path on main's candidate files
    model_b, info_b = loaders["checkpoint"](size, bg.FINAL_STEP, entry, cache_root, device)
    try:
        digest_b = loaders["digest"](model_b)
        runner_b = loaders["runner"](loaders["tokenizer"](size), model_b)
        cont_diffs = {}
        for r in rungs:
            ev_b = evaluate_items(runner_b, battery[r], verify_fn)
            cont_diffs[r] = int(sum(1 for x, y in zip(ev_b["continuations"],
                                                      evs[r]["continuations"]) if x != y))
    finally:
        _release(model_b)
        loaders["free"](size, bg.FINAL_STEP, cache_root)
    rec = {"size": size, "rungs": list(rungs), "model_sha": PYTHIA_SHAS[size],
           "main_entry": entry, "pin_counts": dict(bg.FINAL_COUNT_PIN[size]),
           "counts_2c_path": counts, "diffs_vs_pin": diffs,
           "digest_2c_path": digest_a, "digest_2g_path": digest_b,
           "digests_equal": digest_a == digest_b,
           "continuation_diffs_2g_path": cont_diffs, "loader_info_2g_path": info_b,
           "hub_step143000": manifest[size]["hub_step143000"],
           "seal": seal, "stack": _stack(), "git_sha": _git_sha(),
           "timing": {"seconds": round(time.time() - t0, 1)}}
    failures = an.gate1_failures(rec, size)
    rec["pass"] = not failures
    rec["failures"] = failures
    if failures:
        _write(bg.gate1_path(out_root, size), rec)
        bg.halt_marker_path(out_root, size).parent.mkdir(parents=True, exist_ok=True)
        bg.halt_marker_path(out_root, size).write_text("\n".join(failures) + "\n")
        raise RuntimeError(f"gate 1 {size} FAILED — halted: {failures[:3]}")
    # the final grid point's records come from run (a), 2c's own path
    ckpt = {"revision": "main", "commit": PYTHIA_SHAS[size], "kind": "2c-loader",
            "files": list(entry["files"]), "sha256": dict(entry["lfs_sha256"]),
            "config_source": f"{bg.REPO_OF[size]}@{PYTHIA_SHAS[size]}",
            "tokenizer_source": f"{bg.REPO_OF[size]}@{PYTHIA_SHAS[size]}"}
    for r in rungs:
        _write(bg.record_path(out_root, size, bg.FINAL_STEP, r),
               item_record(size=size, step=bg.FINAL_STEP, rung=r, cap=battery[r],
                           ev=evs[r], ckpt=ckpt, seal=seal, t_s=0.0))
    _write(bg.checkpoint_record_path(out_root, size, bg.FINAL_STEP),
           {"size": size, "step": bg.FINAL_STEP, "revision": "main", "digest": digest_a,
            "digest_2g_path": digest_b, "sha256": dict(entry["lfs_sha256"]),
            "loading_info": info_b.get("loading_info"), "via": "gate 1"})
    # records first, the gate record last: gate1.json on disk implies the final step's records exist
    _write(bg.gate1_path(out_root, size), rec)
    print(f"[2g sweep] gate 1 {size}: PASS ({len(rungs)} rungs, counts exact, digests "
          f"equal, 0 continuation diffs)", flush=True)
    return rec


# --------------------------------------------------------------- steps

def run_step(size, step, *, out_root, manifest, cache_root, device, battery, verify_fn,
             seal, loaders) -> None:
    if records_complete(out_root, size, step):
        return
    entry = ck.entry_for(manifest, size, step)
    t0 = time.time()
    model, info = loaders["checkpoint"](size, step, entry, cache_root, device)
    try:
        digest = loaders["digest"](model)
        _write(bg.checkpoint_record_path(out_root, size, step),
               {**info, "size": size, "step": int(step), "digest": digest,
                "download_seconds": round(time.time() - t0, 1)})
        runner = loaders["runner"](loaders["tokenizer"](size), model)
        ckpt = {**info, "revision": entry["revision"], "commit": entry["commit"],
                "kind": entry["kind"], "files": list(entry["files"])}
        run_rungs(runner, size, step, ckpt, out_root=out_root, battery=battery,
                  verify_fn=verify_fn, seal=seal)
    finally:
        _release(model)
        loaders["free"](size, step, cache_root)
    print(f"[2g sweep] {size}/step{step} done in {time.time() - t0:.0f} s", flush=True)


def run_size(size, *, out_root=EXP2G, cache_root=ck.CKPT_CACHE, device="mps",
             dry_run=False, tag_exists=None, blob_sha=None, loaders=None) -> None:
    seal = pr.require_seal(out_root, tag_exists=tag_exists, blob_sha=blob_sha)
    bg.check_frozen_imports_2g()
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    manifest = ck.load_manifest(bg.CHECKPOINTS_PATH, sha_pin=an.CHECKPOINTS_SHA256)
    if bg.halt_marker_path(out_root, size).exists():
        raise RuntimeError(f"{size}: the sweep is halted "
                           f"({bg.halt_marker_path(out_root, size)}); the analyzer reads "
                           f"this tree as INSUFFICIENT_DATA")
    pending = [s for s in bg.GRID[size] if not records_complete(out_root, size, s)]
    if dry_run:
        print(f"[2g sweep] {size}: seal {seal['sha256'][:12]}; gate 1 "
              f"{'done' if bg.gate1_path(out_root, size).is_file() else 'pending'}; "
              f"would run {len(pending)} step(s): {pending}", flush=True)
        return
    battery = bg.load_battery(bg.sweep_rungs(size))
    verify_fn = a2d.load_verify()
    g1 = bg.gate1_path(out_root, size)
    if not g1.is_file():
        gate1(size, out_root=out_root, manifest=manifest, cache_root=cache_root,
              device=device, battery=battery, verify_fn=verify_fn, seal=seal,
              loaders=loaders)
    else:
        bad = an.gate1_failures(json.loads(g1.read_text()), size)
        if bad:
            raise RuntimeError(f"gate 1 {size} record on disk fails re-derivation: {bad[:3]}")
        if not records_complete(out_root, size, bg.FINAL_STEP):
            raise RuntimeError(f"gate 1 {size}: record present but the final step's records "
                               f"are incomplete — delete {g1} to re-run the gate")
    for step in bg.GRID[size]:
        if step == bg.FINAL_STEP:
            continue
        run_step(size, step, out_root=out_root, manifest=manifest, cache_root=cache_root,
                 device=device, battery=battery, verify_fn=verify_fn, seal=seal,
                 loaders=loaders)
    print(f"[2g sweep] {size}: complete", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2g checkpoint sweep")
    ap.add_argument("--size", required=True, choices=bg.SWEEP_SIZES)
    ap.add_argument("--out-root", default=str(EXP2G))
    ap.add_argument("--cache-root", default=str(ck.CKPT_CACHE))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run_size(ar.size, out_root=Path(ar.out_root), cache_root=Path(ar.cache_root),
             device=ar.device, dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
