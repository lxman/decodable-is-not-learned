# experiments/exp2l/run/sweep_2l.py
"""Exp 2l stage 2 — the OLMo-2 13B stage-1 sweep (design §3.4–§3.5,
§7). Gate 1 first (the endpoint step 596057 re-derived through the
sweep's OWN candidate-file loader `battery_2l.load_checkpoint_13b` and
diffed against the ALREADY-COMMITTED `stage1_final` endpoint records),
then the REAL step 0 (`stage1-step0-tokens0B`, a checkpoint with
weights: loaded, recorded, never in an outcome), then the 15 remaining
grid steps ascending.

Refusal order: `require_prereg_2l` → `check_frozen_2l` → both predictor
seals (`endpoint_2l.require_predictor_seals_2l`) → the endpoint seal
(`require_endpoint_seal_2l`: `exp2l-endpoint-sealed` binds the 68
endpoint records + `rung_set_2l.json` + `power_2l.json`) → a HALTED-tree
resume refusal → the sweep. `endpoint_sha256(out_root)` is computed
ONCE after the endpoint seal binds and stamped into every sweep record.

2i ruling 4: `download_entry_13b`/`clean_dir_13b` key the cache by
`entry["revision"]`; `free_checkpoint_13b` is called with that SAME
key, or a 55 GB directory survives every step.

Usage: python -m experiments.exp2l.run.sweep_2l [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

EXP2L = Path(__file__).resolve().parents[1]
REPO = EXP2L.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g.run.sweep_2g import evaluate_items  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i.run._common_2i import (  # noqa: E402
    assert_provenance as _assert_provenance,
    ckpt_of,
    git_sha as _git_sha,
    release as _release,
    stack as _stack,
)
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402
from experiments.exp2l.run.endpoint_2l import require_predictor_seals_2l  # noqa: E402


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def real_loaders(batch_size: int = bl.BATCH_SIZE_2L) -> dict:
    from harness import HFRunner

    def checkpoint(entry, cache_root, device):
        return bl.load_checkpoint_13b(entry, cache_root=cache_root, device=device, dtype="float16")

    def tokenizer(commit):
        return bl.load_tokenizer_13b(commit)

    def free(revision, cache_root):
        bl.free_checkpoint_13b(revision, cache_root)

    return {"checkpoint": checkpoint, "tokenizer": tokenizer,
            "runner": lambda tok, model: HFRunner(tok, model, batch_size), "free": free}


# ------------------------------------------------------- endpoint seal

def endpoint_seal_blob_paths(root) -> list:
    paths = [bl.rung_set_path(root), bl.power_path(root)]
    for which in bl.ENDPOINT_WHICH:
        for r in bt.RUNGS:
            paths.append(bl.endpoint_record_path(root, which, r))
    return [str(p.relative_to(root)) for p in paths]


def require_endpoint_seal_2l(root, *, blobs_bound=None, repo_root=None) -> None:
    if not bl.rung_set_path(root).is_file() or not bl.power_path(root).is_file():
        raise RuntimeError(f"refusing: the endpoint stage ({bl.rung_set_path(root)}, "
                           f"{bl.power_path(root)}) is not complete — the sweep runs only after "
                           f"{bl.ENDPOINT_SEAL_TAG_2L!r} is cut")
    blobs_bound = blobs_bound or bi.blobs_bound
    rr = Path(repo_root) if repo_root is not None else bl.REPO
    prefix = os.path.relpath(Path(root), rr)
    rel = [os.path.normpath(os.path.join(prefix, p)) for p in endpoint_seal_blob_paths(root)]
    drift = blobs_bound(bl.ENDPOINT_SEAL_TAG_2L, rel, repo_root=rr)
    if drift:
        raise RuntimeError(f"refusing: {bl.ENDPOINT_SEAL_TAG_2L!r} does not bind {drift} — the "
                           f"endpoint has drifted since the seal")


def _load_stage1_final(root) -> dict:
    return {r: json.loads(bl.endpoint_record_path(root, "stage1_final", r).read_text())
            for r in bt.RUNGS}


def records_complete_13b(out_root, step) -> bool:
    """34 rung records AND the checkpoint record (2i R-3: the resume
    window between the last rung write and the checkpoint-record write
    must re-enter the step, not skip it forever)."""
    if not all(bl.record_path(out_root, step, r).exists() for r in bt.RUNGS):
        return False
    return bl.checkpoint_record_path(out_root, step).exists()


# -------------------------------------------------------------- gate 1

def run_gate1(*, out_root, manifest, cache_root, device, battery, verify_fn, endpoint_sha,
              prereg, loaders) -> dict:
    t0 = time.time()
    rungs = tuple(bt.RUNGS)
    entry = bl.entry_13b(manifest, bl.ENDPOINT_STEP_13B)
    stage1_final = _load_stage1_final(out_root)
    model = None
    try:
        model, info = loaders["checkpoint"](entry, cache_root, device)
        tok = loaders["tokenizer"](entry["commit"])
        runner = loaders["runner"](tok, model)
        ckpt = ckpt_of(entry, info, repo=bl.REPO_13B)
        download_seconds = time.time() - t0
        recs, bit_diffs, cont_diffs, cont_n = {}, {}, {}, {}
        for r in rungs:
            ev = evaluate_items(runner, battery[r], verify_fn)
            rec = bl.item_record_2l(rung=r, cap=battery[r], ev=ev, ckpt=ckpt,
                                    step=bl.ENDPOINT_STEP_13B, endpoint_sha=endpoint_sha, t_s=0.0)
            recs[r] = rec
            ref = stage1_final[r]
            bit_diffs[r] = int(sum(1 for a, b in zip(rec["bits"], ref["bits"]) if a != b))
            pairs = list(zip(rec["continuations"], ref["continuations"]))
            cont_n[r] = len(pairs)
            cont_diffs[r] = int(sum(1 for a, b in pairs if a != b))
    finally:
        _release(model)
        loaders["free"](entry["revision"], cache_root)

    gate_rec = {"rungs": list(rungs), "bit_diffs": bit_diffs, "continuation_diffs": cont_diffs,
                "continuations_compared": cont_n, "digest_sweep": ckpt["weight_sha256"],
                "digest_endpoint": stage1_final[rungs[0]].get("weight_sha256"),
                "commit_sweep": ckpt["commit"], "commit_endpoint": stage1_final[rungs[0]].get("commit"),
                "prereg_tag": prereg["tag"], "stack": _stack(), "git_sha": _git_sha(),
                "timing": {"seconds": round(time.time() - t0, 1)}}
    for r in rungs:
        _write(bl.record_path(out_root, bl.ENDPOINT_STEP_13B, r), recs[r])
    _write(bl.checkpoint_record_path(out_root, bl.ENDPOINT_STEP_13B),
           bl.checkpoint_record_2l(step=bl.ENDPOINT_STEP_13B, ckpt=ckpt, info=info,
                                   seconds=download_seconds))
    _write(bl.gate1_path(out_root), gate_rec)
    bad = bl.gate1_failures_13b(gate_rec, stage1_final)
    if bad:
        bl.halt_marker_path(out_root).parent.mkdir(parents=True, exist_ok=True)
        bl.halt_marker_path(out_root).write_text("\n".join(bad) + "\n")
        raise RuntimeError(f"gate 1 olmo13b FAILED — halted: {bad[:3]}")
    print("[2l sweep] gate 1 olmo13b: PASS (34 rungs, digest+commit equal, 0 diffs)", flush=True)
    return gate_rec


# ---------------------------------------------------------- grid steps

def run_step(step, *, out_root, manifest, cache_root, device, battery, verify_fn, endpoint_sha,
             loaders) -> None:
    if records_complete_13b(out_root, step):
        return
    entry = bl.entry_13b(manifest, step)
    t0 = time.time()
    model = None
    try:
        model, info = loaders["checkpoint"](entry, cache_root, device)
        tok = loaders["tokenizer"](entry["commit"])
        runner = loaders["runner"](tok, model)
        ckpt = ckpt_of(entry, info, repo=bl.REPO_13B)
        download_seconds = time.time() - t0
        for rung in bt.RUNGS:
            p = bl.record_path(out_root, step, rung)
            if p.exists():
                continue
            ev = evaluate_items(runner, battery[rung], verify_fn)
            rec = bl.item_record_2l(rung=rung, cap=battery[rung], ev=ev, ckpt=ckpt, step=step,
                                    endpoint_sha=endpoint_sha, t_s=0.0)
            _write(p, rec)
            print(f"[2l sweep] step{step}/{rung}: {rec['correct']}/{rec['n']}", flush=True)
        _write(bl.checkpoint_record_path(out_root, step),
               bl.checkpoint_record_2l(step=step, ckpt=ckpt, info=info, seconds=download_seconds))
    finally:
        _release(model)
        loaders["free"](entry["revision"], cache_root)
    print(f"[2l sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)


# ----------------------------------------------------------------- run

def run(*, out_root=EXP2L, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=bl.CKPT_CACHE_2L,
        device="mps", dry_run=False, tag_exists=None, blob_sha=None, blobs_bound=None,
        loaders=None) -> None:
    prereg = bl.require_prereg_2l(tag_exists=tag_exists, blob_sha=blob_sha)
    bl.check_frozen_2l()
    require_predictor_seals_2l(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2l(out_root, blobs_bound=blobs_bound)
    manifest = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    if bl.halt_marker_path(out_root).exists():
        raise RuntimeError(f"olmo13b: the sweep is halted ({bl.halt_marker_path(out_root)}); "
                           f"the analyzer reads this tree as INSUFFICIENT_DATA")
    rest = (bl.STEP0,) + tuple(s for s in bl.GRID_13B if s != bl.ENDPOINT_STEP_13B)
    pending = [s for s in rest if not records_complete_13b(out_root, s)]
    gate_done = bl.gate1_path(out_root).is_file()
    if dry_run:
        print(f"[2l sweep] prereg tag {prereg['tag']!r}; gate 1 "
              f"{'done' if gate_done else 'pending'}; would run "
              f"{len(pending) + (0 if gate_done else 1)} step(s): "
              f"{('gate1, ' if not gate_done else '') + str(pending)}", flush=True)
        return
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    endpoint_sha = bl.endpoint_sha256(out_root)

    g1 = bl.gate1_path(out_root)
    if not g1.is_file():
        run_gate1(out_root=out_root, manifest=manifest, cache_root=cache_root, device=device,
                  battery=battery, verify_fn=verify_fn, endpoint_sha=endpoint_sha, prereg=prereg,
                  loaders=loaders)
    else:
        bad = bl.gate1_failures_13b(json.loads(g1.read_text()), _load_stage1_final(out_root))
        if bad:
            raise RuntimeError(f"gate 1 olmo13b record on disk fails re-derivation: {bad[:3]}")
        if not records_complete_13b(out_root, bl.ENDPOINT_STEP_13B):
            raise RuntimeError(f"gate 1 olmo13b: record present but step{bl.ENDPOINT_STEP_13B}'s "
                               f"records are incomplete — delete {g1} to re-run the gate")
    for step in rest:
        run_step(step, out_root=out_root, manifest=manifest, cache_root=cache_root, device=device,
                 battery=battery, verify_fn=verify_fn, endpoint_sha=endpoint_sha, loaders=loaders)
    print("[2l sweep] olmo13b: complete", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2l checkpoint sweep (OLMo-2 13B)")
    ap.add_argument("--out-root", default=str(EXP2L))
    ap.add_argument("--cache-root", default=str(bl.CKPT_CACHE_2L))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(out_root=Path(ar.out_root), cache_root=Path(ar.cache_root), device=ar.device,
        dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
