# experiments/exp2m/run/sweep_2m.py
"""Exp 2m stage 2 — the SmolLM3-3B stage-1 sweep (design §3.5–§3.6,
§7). Gate 1 first (the endpoint step 3440000 re-derived through the
sweep's OWN candidate-file loader `battery_2m.load_checkpoint_3b` and
diffed against the ALREADY-COMMITTED `stage1_final` endpoint records),
then the seeded from_config TWIN (the init referent: recorded, never in
an outcome, nothing downloaded so nothing freed), then the 25 remaining
grid steps ascending.

Refusal order: `require_prereg_2m` → `check_frozen_2m` → both predictor
seals (`endpoint_2m.require_predictor_seals_2m`) → the endpoint seal
(`require_endpoint_seal_2m`: `exp2m-endpoint-sealed` binds the 102
endpoint records + `rung_set_2m.json` + `power_2m.json`) → a HALTED-tree
resume refusal → the sweep. `endpoint_sha256(out_root)` is computed
ONCE after the endpoint seal binds and stamped into every sweep record.

2i ruling 4: `download_entry_3b`/`clean_dir_3b` key the cache by
`entry["revision"]`; `free_checkpoint_3b` is called with that SAME key.

Usage: python -m experiments.exp2m.run.sweep_2m [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

EXP2M = Path(__file__).resolve().parents[1]
REPO = EXP2M.parent.parent
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
from experiments.exp2m import battery_2m as bm  # noqa: E402
from experiments.exp2m.run.endpoint_2m import require_predictor_seals_2m  # noqa: E402


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def real_loaders(batch_size: int = bm.BATCH_SIZE_2M) -> dict:
    from harness import HFRunner

    def checkpoint(entry, cache_root, device):
        return bm.load_checkpoint_3b(entry, cache_root=cache_root, device=device, dtype=bm.DTYPE_2M)

    def twin(config_commit, device):
        return bm.load_twin_3b(config_commit=config_commit, device=device, dtype=bm.DTYPE_2M,
                               seed=bm.TWIN_SEED)

    def tokenizer(repo, commit):
        return bm.load_tokenizer_3b(repo, commit)

    def free(revision, cache_root):
        bm.free_checkpoint_3b(revision, cache_root)

    return {"checkpoint": checkpoint, "twin": twin, "tokenizer": tokenizer,
            "runner": lambda tok, model: HFRunner(tok, model, batch_size), "free": free}


# ------------------------------------------------------- endpoint seal

def endpoint_seal_blob_paths(root) -> list:
    paths = [bm.rung_set_path(root), bm.power_path(root)]
    for which in bm.ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            paths.append(bm.endpoint_record_path(root, which, r))
    return [str(p.relative_to(root)) for p in paths]


def require_endpoint_seal_2m(root, *, blobs_bound=None, repo_root=None) -> None:
    if not bm.rung_set_path(root).is_file() or not bm.power_path(root).is_file():
        raise RuntimeError(f"refusing: the endpoint stage ({bm.rung_set_path(root)}, "
                           f"{bm.power_path(root)}) is not complete — the sweep runs only after "
                           f"{bm.ENDPOINT_SEAL_TAG_2M!r} is cut")
    blobs_bound = blobs_bound or bi.blobs_bound
    rr = Path(repo_root) if repo_root is not None else bm.REPO
    prefix = os.path.relpath(Path(root), rr)
    rel = [os.path.normpath(os.path.join(prefix, p)) for p in endpoint_seal_blob_paths(root)]
    drift = blobs_bound(bm.ENDPOINT_SEAL_TAG_2M, rel, repo_root=rr)
    if drift:
        raise RuntimeError(f"refusing: {bm.ENDPOINT_SEAL_TAG_2M!r} does not bind {drift} — the "
                           f"endpoint has drifted since the seal")


def _load_stage1_final(root) -> dict:
    return {r: json.loads(bm.endpoint_record_path(root, "stage1_final", r).read_text())
            for r in bt.RUNGS}


def records_complete_3b(out_root, step) -> bool:
    """34 rung records AND the checkpoint record (2i R-3); the twin's
    key is its own directory."""
    if not all(bm.record_path(out_root, step, r).exists() for r in bt.RUNGS):
        return False
    return bm.checkpoint_record_path(out_root, step).exists()


# -------------------------------------------------------------- gate 1

def run_gate1(*, out_root, manifest, cache_root, device, battery, verify_fn, endpoint_sha,
              prereg, loaders) -> dict:
    t0 = time.time()
    rungs = tuple(bt.RUNGS)
    entry = bm.entry_3b(manifest, bm.ENDPOINT_STEP_2M)
    stage1_final = _load_stage1_final(out_root)
    model = None
    try:
        model, info = loaders["checkpoint"](entry, cache_root, device)
        tok = loaders["tokenizer"](entry["repo"], entry["commit"])
        runner = loaders["runner"](tok, model)
        ckpt = ckpt_of(entry, info, repo=entry["repo"])
        download_seconds = time.time() - t0
        recs, bit_diffs, cont_diffs, cont_n = {}, {}, {}, {}
        for r in rungs:
            ev = evaluate_items(runner, battery[r], verify_fn)
            rec = bm.item_record_2m(rung=r, cap=battery[r], ev=ev, ckpt=ckpt,
                                    step=bm.ENDPOINT_STEP_2M, endpoint_sha=endpoint_sha, t_s=0.0)
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
        _write(bm.record_path(out_root, bm.ENDPOINT_STEP_2M, r), recs[r])
    _write(bm.checkpoint_record_path(out_root, bm.ENDPOINT_STEP_2M),
           bm.checkpoint_record_2m(step=bm.ENDPOINT_STEP_2M, ckpt=ckpt, info=info, seconds=download_seconds))
    _write(bm.gate1_path(out_root), gate_rec)
    bad = bm.gate1_failures_3b(gate_rec, stage1_final)
    if bad:
        bm.halt_marker_path(out_root).parent.mkdir(parents=True, exist_ok=True)
        bm.halt_marker_path(out_root).write_text("\n".join(bad) + "\n")
        raise RuntimeError(f"gate 1 smollm3_3b FAILED — halted: {bad[:3]}")
    print("[2m sweep] gate 1 smollm3_3b: PASS (34 rungs, digest+commit equal, 0 diffs)", flush=True)
    return gate_rec


# ---------------------------------------------------------------- twin

def run_twin(*, out_root, manifest, device, battery, verify_fn, endpoint_sha, loaders) -> None:
    """2i's `run_twin` shape: the seeded from_config referent, its 34
    records then its bespoke checkpoint record (written AFTER the loop,
    so an interrupted twin never leaves a checkpoint record for rungs
    that were never evaluated). Nothing is downloaded, nothing freed."""
    if records_complete_3b(out_root, bm.TWIN):
        return
    entry = bm.entry_3b(manifest, bm.TWIN)
    t0 = time.time()
    model = None
    try:
        model, info = loaders["twin"](entry["config_commit"], device)
        tok = loaders["tokenizer"](entry["repo"], entry["config_commit"])
        runner = loaders["runner"](tok, model)
        ckpt = {"revision": bm.TWIN, "commit": None, "kind": "from_config", "files": [],
                "weight_sha256": info["tensor_digest"], "config_source": info["config_source"],
                "tokenizer_source": f"{entry['repo']}@{entry['config_commit']}"}
        for rung in bt.RUNGS:
            p = bm.record_path(out_root, bm.TWIN, rung)
            if p.exists():
                continue
            ev = evaluate_items(runner, battery[rung], verify_fn)
            rec = bm.item_record_2m(rung=rung, cap=battery[rung], ev=ev, ckpt=ckpt, step=bm.TWIN,
                                    endpoint_sha=endpoint_sha, t_s=0.0)
            _write(p, rec)
            print(f"[2m sweep] twin/{rung}: {rec['correct']}/{rec['n']}", flush=True)
        _write(bm.checkpoint_record_path(out_root, bm.TWIN), bm.twin_checkpoint_record_2m(info=info))
    finally:
        _release(model)
    print(f"[2m sweep] twin done in {time.time() - t0:.0f} s", flush=True)


# ---------------------------------------------------------- grid steps

def run_step(step, *, out_root, manifest, cache_root, device, battery, verify_fn, endpoint_sha,
             loaders) -> None:
    if records_complete_3b(out_root, step):
        return
    entry = bm.entry_3b(manifest, step)
    t0 = time.time()
    model = None
    try:
        model, info = loaders["checkpoint"](entry, cache_root, device)
        tok = loaders["tokenizer"](entry["repo"], entry["commit"])
        runner = loaders["runner"](tok, model)
        ckpt = ckpt_of(entry, info, repo=entry["repo"])
        download_seconds = time.time() - t0
        for rung in bt.RUNGS:
            p = bm.record_path(out_root, step, rung)
            if p.exists():
                continue
            ev = evaluate_items(runner, battery[rung], verify_fn)
            rec = bm.item_record_2m(rung=rung, cap=battery[rung], ev=ev, ckpt=ckpt, step=step,
                                    endpoint_sha=endpoint_sha, t_s=0.0)
            _write(p, rec)
            print(f"[2m sweep] step{step}/{rung}: {rec['correct']}/{rec['n']}", flush=True)
        _write(bm.checkpoint_record_path(out_root, step),
               bm.checkpoint_record_2m(step=step, ckpt=ckpt, info=info, seconds=download_seconds))
    finally:
        _release(model)
        loaders["free"](entry["revision"], cache_root)
    print(f"[2m sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)


# ----------------------------------------------------------------- run

def run(*, out_root=EXP2M, root_2i=bi.EXP2I, root_2k=bk.EXP2K, cache_root=bm.CKPT_CACHE_2M,
        device="mps", dry_run=False, tag_exists=None, blob_sha=None, blobs_bound=None,
        loaders=None) -> None:
    prereg = bm.require_prereg_2m(tag_exists=tag_exists, blob_sha=blob_sha)
    bm.check_frozen_2m()
    require_predictor_seals_2m(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2m(out_root, blobs_bound=blobs_bound)
    manifest = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
    if bm.halt_marker_path(out_root).exists():
        raise RuntimeError(f"smollm3_3b: the sweep is halted ({bm.halt_marker_path(out_root)}); "
                           f"the analyzer reads this tree as INSUFFICIENT_DATA")
    rest = (bm.TWIN,) + tuple(s for s in bm.GRID_3B if s != bm.ENDPOINT_STEP_2M)
    pending = [s for s in rest if not records_complete_3b(out_root, s)]
    gate_done = bm.gate1_path(out_root).is_file()
    if dry_run:
        print(f"[2m sweep] prereg tag {prereg['tag']!r}; dtype {bm.DTYPE_2M}; gate 1 "
              f"{'done' if gate_done else 'pending'}; would run "
              f"{len(pending) + (0 if gate_done else 1)} step(s): "
              f"{('gate1, ' if not gate_done else '') + str(pending)}", flush=True)
        return
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    endpoint_sha = bm.endpoint_sha256(out_root)

    g1 = bm.gate1_path(out_root)
    if not g1.is_file():
        run_gate1(out_root=out_root, manifest=manifest, cache_root=cache_root, device=device,
                  battery=battery, verify_fn=verify_fn, endpoint_sha=endpoint_sha, prereg=prereg,
                  loaders=loaders)
    else:
        bad = bm.gate1_failures_3b(json.loads(g1.read_text()), _load_stage1_final(out_root))
        if bad:
            raise RuntimeError(f"gate 1 smollm3_3b record on disk fails re-derivation: {bad[:3]}")
        if not records_complete_3b(out_root, bm.ENDPOINT_STEP_2M):
            raise RuntimeError(f"gate 1 smollm3_3b: record present but step{bm.ENDPOINT_STEP_2M}'s "
                               f"records are incomplete — delete {g1} to re-run the gate")
    for step in rest:
        if step == bm.TWIN:
            run_twin(out_root=out_root, manifest=manifest, device=device, battery=battery,
                     verify_fn=verify_fn, endpoint_sha=endpoint_sha, loaders=loaders)
        else:
            run_step(step, out_root=out_root, manifest=manifest, cache_root=cache_root, device=device,
                     battery=battery, verify_fn=verify_fn, endpoint_sha=endpoint_sha, loaders=loaders)
    print("[2m sweep] smollm3_3b: complete", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2m checkpoint sweep (SmolLM3-3B stage 1)")
    ap.add_argument("--out-root", default=str(EXP2M))
    ap.add_argument("--cache-root", default=str(bm.CKPT_CACHE_2M))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(out_root=Path(ar.out_root), cache_root=Path(ar.cache_root), device=ar.device,
        dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
