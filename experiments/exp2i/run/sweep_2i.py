# experiments/exp2i/run/sweep_2i.py
"""Exp 2i stage 3 — the OLMo-2 7B checkpoint sweep (design §3.4-§3.6,
§7). Gate 1 first (the endpoint step 928646, re-derived through the
sweep's OWN checkpoint loader — `battery_2i.load_checkpoint`'s
candidate-file path — and diffed against the ALREADY-COMMITTED
`stage1_final` endpoint records Task 2's `endpoint_2i.py` wrote; no
second fresh loader path is needed here, unlike 2h's gate 1, because
the endpoint stage already produced the comparison side), then the
from_config `TWIN` (seed 0, a step-0 referent, never a predictor),
then the 20 remaining grid steps ascending.

Refusal order (ruling 1): `require_prereg_2i` (the tag must carry all
FIVE instrument blobs, including this file) -> `check_frozen_2i()` ->
the predictor seal (`endpoint_2i._require_predictor_seal`, reused
directly — the same check the endpoint stage already applies) -> the
endpoint seal (`_require_endpoint_seal` below, mirroring its path
construction over `rung_set_2i.json` + `power_2i.json` + the 68
endpoint records) -> a HALTED-tree resume refusal -> the sweep itself.
A refusal never leaves a partial record.

`evaluate_items`/`item_record_2i` are reused directly (the former from
`exp2g.run.sweep_2g`, pure in its (runner, cap, verify_fn) arguments;
the latter from `endpoint_2i.py`, already generalized to accept
`step=` in place of `which=`). `gate1_failures_7b` (`analyze_2i.py`)
is the production re-derivation this runner's own `gate1.json` must
satisfy byte for byte — the same record shape `load_sweep_7b` expects
back.

Ruling 4 (the reviewer-flagged decoupling risk): `battery_2i
.download_entry`/`clean_dir` key the raw + clean cache by
`entry['revision']` (the branch-name string, NOT a step int) —
`free_checkpoint` here is always called with that SAME key, or a
multi-GB directory survives every step.

Usage: python -m experiments.exp2i.run.sweep_2i [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

EXP2I = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2I.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g.run.sweep_2g import evaluate_items  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i.analyze_2i import (  # noqa: E402
    gate1_failures_7b,
    require_prereg_2i,
)
from experiments.exp2i.run._common_2i import (  # noqa: E402
    assert_provenance as _assert_provenance,
    checkpoint_record,
    ckpt_of,
    git_sha as _git_sha,
    release as _release,
    stack as _stack,
)
from experiments.exp2i.run.endpoint_2i import (  # noqa: E402
    _require_predictor_seal,
    item_record_2i,
)


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def real_loaders() -> dict:
    from harness import HFRunner

    def checkpoint(entry, cache_root, device):
        return bi.load_checkpoint(bi.REPO_7B, entry, cache_root=cache_root,
                                  device=device, dtype="float16")

    def twin(device):
        return bi.load_twin_7b(device=device, dtype="float16", seed=bi.TWIN_SEED)

    def tokenizer(commit):
        return bi.load_tokenizer(bi.REPO_7B, commit)

    def free(revision, cache_root):
        bi.free_checkpoint(bi.REPO_7B, revision, cache_root)

    return {"checkpoint": checkpoint, "twin": twin, "tokenizer": tokenizer,
           "runner": lambda tok, model: HFRunner(tok, model), "free": free}


# ---------------------------------------------------------- endpoint seal
#
# There is no aggregate seal-content file for the endpoint stage (unlike
# the predictor's `predictor_2i.json`) — `ENDPOINT_SEAL_TAG` binds
# `rung_set_2i.json` + `power_2i.json` + all 68 (which, rung) endpoint
# records directly (`analyze_2i._endpoint_seal_paths`'s own set,
# mirrored here so a drift in either copy is a refusal, never a silent
# narrowing).

def _endpoint_seal_blob_paths(root) -> list:
    paths = [bi.rung_set_path(root), bi.power_path(root)]
    for which in ("stage1_final", "main"):
        for r in bt.RUNGS:
            paths.append(bi.endpoint_record_path(root, which, r))
    return [str(p.relative_to(root)) for p in paths]


def _require_endpoint_seal(root, *, blobs_bound=None, repo_root=None) -> None:
    if not bi.rung_set_path(root).is_file() or not bi.power_path(root).is_file():
        raise RuntimeError(f"refusing: the endpoint stage ({bi.rung_set_path(root)}, "
                           f"{bi.power_path(root)}) is not complete — the sweep runs "
                           f"only after {bi.ENDPOINT_SEAL_TAG!r} is cut")
    blobs_bound = blobs_bound or bi.blobs_bound
    rr = Path(repo_root) if repo_root is not None else bi.REPO
    prefix = os.path.relpath(Path(root), rr)
    rel_paths = [os.path.normpath(os.path.join(prefix, p))
                for p in _endpoint_seal_blob_paths(root)]
    drift = blobs_bound(bi.ENDPOINT_SEAL_TAG, rel_paths, repo_root=rr)
    if drift:
        raise RuntimeError(f"refusing: {bi.ENDPOINT_SEAL_TAG!r} does not bind "
                           f"{drift} — the endpoint has drifted since the seal")


def _load_predictor_sha(root) -> str:
    p = bi.predictor_seal_path(root)
    return json.loads(p.read_text())["sha256"]


def _load_stage1_final(root) -> dict:
    return {r: json.loads(bi.endpoint_record_path(root, "stage1_final", r).read_text())
           for r in bt.RUNGS}


# --------------------------------------------------------------- steps

def records_complete_7b(out_root, step) -> bool:
    """A step is complete only when its 34 rung records AND its
    `_checkpoint.json` are on disk.

    FREEZE R-3 (the resume window): the rung records are written one at
    a time inside the loop and the checkpoint record only after the
    loop, so a process killed between the LAST rung write and the
    checkpoint-record write left a tree that satisfied the old
    rung-records-only predicate — `run_step`/`run_twin` skipped the
    step forever on every resume, while `analyze_2i.load_sweep_7b`
    requires that checkpoint record and refused the tree forever. Both
    sides were individually correct; together they deadlocked. Requiring
    the record here closes it: the resume re-enters the step, skips
    every rung record already present (the rung-grain skip inside the
    loop is untouched), and writes the checkpoint record — the cost is
    one checkpoint load, not 34 re-evaluations."""
    if not all(bi.record_path(out_root, step, r).exists() for r in bt.RUNGS):
        return False
    return bi.checkpoint_record_path(out_root, step).exists()


# -------------------------------------------------------------- gate 1

def run_gate1(*, out_root, manifest, cache_root, device, battery, verify_fn, seal,
             prereg, loaders) -> dict:
    t0 = time.time()
    rungs = tuple(bt.RUNGS)
    entry = bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B)
    stage1_final = _load_stage1_final(out_root)
    model = None
    try:
        model, info = loaders["checkpoint"](entry, cache_root, device)
        tok = loaders["tokenizer"](entry["commit"])
        runner = loaders["runner"](tok, model)
        ckpt = ckpt_of(entry, info, repo=bi.REPO_7B)
        # download_seconds means the SAME thing on every path in this
        # module (review finding 1): time to load the checkpoint,
        # captured here, BEFORE the 34-rung eval loop — not the
        # combined download+eval time the write-after-loop ordering
        # below would otherwise measure.
        download_seconds = time.time() - t0
        recs, bit_diffs, cont_diffs, cont_n = {}, {}, {}, {}
        for r in rungs:
            ev = evaluate_items(runner, battery[r], verify_fn)
            rec = item_record_2i(rung=r, family=bi.FAMILY, size=bi.SIZE_OUT,
                                 step=bi.ENDPOINT_STEP_7B, cap=battery[r], ev=ev,
                                 ckpt=ckpt, seal=seal, t_s=0.0)
            recs[r] = rec
            ref = stage1_final[r]
            bit_diffs[r] = int(sum(1 for a, b in zip(rec["bits"], ref["bits"]) if a != b))
            pairs = list(zip(rec["continuations"], ref["continuations"]))
            cont_n[r] = len(pairs)
            cont_diffs[r] = int(sum(1 for a, b in pairs if a != b))
    finally:
        _release(model)
        loaders["free"](entry["revision"], cache_root)

    digest_endpoint = stage1_final[rungs[0]].get("weight_sha256")
    commit_endpoint = stage1_final[rungs[0]].get("commit")
    gate_rec = {"rungs": list(rungs), "bit_diffs": bit_diffs,
               "continuation_diffs": cont_diffs, "continuations_compared": cont_n,
               "digest_sweep": ckpt["weight_sha256"], "digest_endpoint": digest_endpoint,
               "commit_sweep": ckpt["commit"], "commit_endpoint": commit_endpoint,
               "prereg_tag": prereg["tag"], "stack": _stack(), "git_sha": _git_sha(),
               "timing": {"seconds": round(time.time() - t0, 1)}}

    for r in rungs:
        _write(bi.record_path(out_root, bi.ENDPOINT_STEP_7B, r), recs[r])
    _write(bi.checkpoint_record_path(out_root, bi.ENDPOINT_STEP_7B),
          checkpoint_record(step_or_which=bi.ENDPOINT_STEP_7B, ckpt=ckpt, info=info,
                            seconds=download_seconds))
    _write(bi.gate1_path(out_root), gate_rec)

    bad = gate1_failures_7b(gate_rec, stage1_final)
    if bad:
        bi.halt_marker_path(out_root).parent.mkdir(parents=True, exist_ok=True)
        bi.halt_marker_path(out_root).write_text("\n".join(bad) + "\n")
        raise RuntimeError(f"gate 1 olmo7b FAILED — halted: {bad[:3]}")
    print("[2i sweep] gate 1 olmo7b: PASS (34 rungs, digest+commit equal, 0 diffs)",
         flush=True)
    return gate_rec


# ---------------------------------------------------------------- twin

def run_twin(*, out_root, device, manifest, battery, verify_fn, seal, loaders) -> None:
    if records_complete_7b(out_root, bi.TWIN):
        return
    entry = bi.entry_7b(manifest, bi.TWIN)
    t0 = time.time()
    model = None
    try:
        model, info = loaders["twin"](device)
        tok = loaders["tokenizer"](entry["config_commit"])
        runner = loaders["runner"](tok, model)
        ckpt = {"revision": "twin", "commit": None, "kind": "from_config", "files": [],
               "weight_sha256": info["tensor_digest"], "config_source": info["config_source"],
               "tokenizer_source": f"{bi.REPO_7B}@{entry['config_commit']}"}
        # the checkpoint record is written AFTER the rung loop (review
        # minor) — matching run_gate1's/run_step's own records -> then
        # -> checkpoint-record order, so a run interrupted mid-loop
        # never leaves a checkpoint record for rungs that were never
        # actually evaluated.
        for rung in bt.RUNGS:
            p = bi.record_path(out_root, bi.TWIN, rung)
            if p.exists():
                continue
            ev = evaluate_items(runner, battery[rung], verify_fn)
            rec = item_record_2i(rung=rung, family=bi.FAMILY, size=bi.SIZE_OUT,
                                 step=bi.TWIN, cap=battery[rung], ev=ev, ckpt=ckpt,
                                 seal=seal, t_s=0.0)
            _write(p, rec)
            print(f"[2i sweep] twin/{rung}: {rec['correct']}/{rec['n']}", flush=True)
        _write(bi.checkpoint_record_path(out_root, bi.TWIN),
              {"family": bi.FAMILY, "size": bi.SIZE_OUT, "step": bi.TWIN, "revision": "twin",
               "commit": None, "kind": "from_config", "seed": bi.TWIN_SEED,
               "digest": info["tensor_digest"], "config_source": info["config_source"]})
    finally:
        _release(model)
    print(f"[2i sweep] twin done in {time.time() - t0:.0f} s", flush=True)


# ---------------------------------------------------------- grid steps

def run_step(step, *, out_root, manifest, cache_root, device, battery, verify_fn, seal,
            loaders) -> None:
    if records_complete_7b(out_root, step):
        return
    entry = bi.entry_7b(manifest, step)
    t0 = time.time()
    model = None
    try:
        model, info = loaders["checkpoint"](entry, cache_root, device)
        tok = loaders["tokenizer"](entry["commit"])
        runner = loaders["runner"](tok, model)
        ckpt = ckpt_of(entry, info, repo=bi.REPO_7B)
        # download_seconds captured here (before the loop) so it means
        # the SAME thing as run_gate1's — review finding 1; the RECORD
        # itself is written after the loop (below), matching
        # run_gate1's own records -> checkpoint record order.
        download_seconds = time.time() - t0
        for rung in bt.RUNGS:
            p = bi.record_path(out_root, step, rung)
            if p.exists():
                continue
            ev = evaluate_items(runner, battery[rung], verify_fn)
            rec = item_record_2i(rung=rung, family=bi.FAMILY, size=bi.SIZE_OUT, step=step,
                                 cap=battery[rung], ev=ev, ckpt=ckpt, seal=seal, t_s=0.0)
            _write(p, rec)
            print(f"[2i sweep] step{step}/{rung}: {rec['correct']}/{rec['n']}", flush=True)
        _write(bi.checkpoint_record_path(out_root, step),
              checkpoint_record(step_or_which=int(step), ckpt=ckpt, info=info,
                                seconds=download_seconds))
    finally:
        _release(model)
        loaders["free"](entry["revision"], cache_root)
    print(f"[2i sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)


# ----------------------------------------------------------------- run

def run(*, out_root=EXP2I, cache_root=bi.CKPT_CACHE, device="mps", dry_run=False,
       tag_exists=None, blob_sha=None, blobs_bound=None, repo_root=None,
       loaders=None) -> None:
    prereg = require_prereg_2i(tag_exists=tag_exists, blob_sha=blob_sha)
    bi.check_frozen_2i()
    _require_predictor_seal(out_root, blobs_bound=blobs_bound, repo_root=repo_root)
    _require_endpoint_seal(out_root, blobs_bound=blobs_bound, repo_root=repo_root)

    manifest = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    if bi.halt_marker_path(out_root).exists():
        raise RuntimeError(f"olmo7b: the sweep is halted "
                           f"({bi.halt_marker_path(out_root)}); the analyzer reads this "
                           f"tree as INSUFFICIENT_DATA")

    rest_steps = (bi.TWIN,) + tuple(s for s in bi.GRID_7B if s != bi.ENDPOINT_STEP_7B)
    pending = [s for s in rest_steps if not records_complete_7b(out_root, s)]
    gate_done = bi.gate1_path(out_root).is_file()
    if dry_run:
        print(f"[2i sweep] prereg tag {prereg['tag']!r}; gate 1 "
              f"{'done' if gate_done else 'pending'}; would run "
              f"{len(pending) + (0 if gate_done else 1)} step(s): "
              f"{('gate1, ' if not gate_done else '') + str(pending)}", flush=True)
        return

    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()

    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    predictor_sha = _load_predictor_sha(out_root)
    seal = {"tag": bi.ENDPOINT_SEAL_TAG, "sha256": predictor_sha}

    g1 = bi.gate1_path(out_root)
    if not g1.is_file():
        run_gate1(out_root=out_root, manifest=manifest, cache_root=cache_root, device=device,
                 battery=battery, verify_fn=verify_fn, seal=seal, prereg=prereg,
                 loaders=loaders)
    else:
        stage1_final = _load_stage1_final(out_root)
        bad = gate1_failures_7b(json.loads(g1.read_text()), stage1_final)
        if bad:
            raise RuntimeError(f"gate 1 olmo7b record on disk fails re-derivation: {bad[:3]}")
        if not records_complete_7b(out_root, bi.ENDPOINT_STEP_7B):
            raise RuntimeError(f"gate 1 olmo7b: record present but step"
                               f"{bi.ENDPOINT_STEP_7B}'s records are incomplete — delete "
                               f"{g1} to re-run the gate")

    run_twin(out_root=out_root, device=device, manifest=manifest, battery=battery,
            verify_fn=verify_fn, seal=seal, loaders=loaders)

    for step in bi.GRID_7B:
        if step == bi.ENDPOINT_STEP_7B:
            continue
        run_step(step, out_root=out_root, manifest=manifest, cache_root=cache_root,
                device=device, battery=battery, verify_fn=verify_fn, seal=seal,
                loaders=loaders)
    print("[2i sweep] olmo7b: complete", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2i checkpoint sweep (OLMo-2 7B)")
    ap.add_argument("--out-root", default=str(EXP2I))
    ap.add_argument("--cache-root", default=str(bi.CKPT_CACHE))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(out_root=Path(ar.out_root), cache_root=Path(ar.cache_root), device=ar.device,
       dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
