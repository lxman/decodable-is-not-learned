# experiments/exp2i/run/endpoint_2i.py
"""Exp 2i stage 2 — the endpoint stage: OLMo-2 7B's stage-1 endpoint
(`stage1_final`) AND `main` through the thin loader, on all 34 rungs,
per-item bits and continuations stored (design §3.3, §7). The
`stage1_final` record fixes R (§4) by rule; `main` is descriptive only
— never in the rung-set rule or any outcome. Does NOT run power
(Task 3's module; the supervisor runs it once after this stage, then
seals `exp2i-endpoint-sealed`).

Order, load-bearing: (1) the prereg refusal (as `sample_2i`); (2)
`check_frozen_2i()`; (3) refuses unless `PREDICTOR_SEAL_TAG` exists
and blob-binds `predictor_2i.json` + every file it lists — both the
draws AND the record for all 34 rungs — to the tag
(`battery_2i.blobs_bound`, the 2h F-3 primitive). Per `which`
revision, the loader is built only if at least one rung's record is
still missing; a fully-written `which` is read back from disk instead
(review finding 2). `evaluate_items` is
reused directly from `exp2g.run.sweep_2g` (a pure function of its
(runner, cap, verify_fn) arguments, not bound to any exp2g-only
global); `item_record_2i` is written locally — 2g's `item_record`
hard-codes `dtype: "float16"` and Pythia seal fields this stage does
not have at write time in the same shape.

Usage: python -m experiments.exp2i.run.endpoint_2i [--dry-run]
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
from experiments.exp2i.run._common_2i import (  # noqa: E402
    assert_provenance as _assert_provenance,
    git_sha as _git_sha,
    release as _release,
    stack as _stack,
)

try:
    from experiments.exp2i.analyze_2i import require_prereg_2i  # noqa: E402
except ImportError:
    from experiments.exp2i.run._prereg_stub_2i import require_prereg_2i  # noqa: E402

WHICH = ("stage1_final", "main")


# ------------------------------------------------------------- record

def item_record_2i(*, rung, family, size, cap, ev, ckpt, seal, t_s,
                   step=None, which=None) -> dict:
    """2g's `item_record` shape with `family` added and the identity
    field generalized: sweep records (Task 4) carry `step` (int or
    `"twin"`); endpoint records (this module) carry `which`
    (`"stage1_final"` | `"main"`) — a record carries exactly one."""
    if (step is None) == (which is None):
        raise ValueError("item_record_2i: exactly one of step/which is required")
    from harness import MAX_NEW_TOKENS
    rec = {"rung": rung, "family": family, "size": size,
          "revision": ckpt["revision"], "commit": ckpt["commit"],
          "kind": ckpt["kind"], "files": list(ckpt.get("files", [])),
          "weight_sha256": ckpt.get("weight_sha256"),
          "config_source": ckpt.get("config_source"),
          "tokenizer_source": ckpt.get("tokenizer_source"),
          "items_sha256": cap["items_sha256"], "n": len(ev["bits"]),
          "correct": ev["correct"], "bits": ev["bits"],
          "continuations": ev["continuations"],
          "max_new_tokens": int(MAX_NEW_TOKENS[cap["answer_type"]]),
          "n_shots": bt.N_SHOTS, "dtype": "float16", "answer_type": cap["answer_type"],
          "verify": "2c normalize + exact match under 3c's total wrapper",
          "stack": _stack(), "git_sha": _git_sha(), "predictor_sha": seal["sha256"],
          "seal_tag": seal["tag"], "seconds": round(t_s, 2)}
    if step is not None:
        rec["step"] = step if step == bi.TWIN else int(step)
    else:
        rec["which"] = which
    return rec


# ------------------------------------------------------------- helpers
#
# `_stack`/`_git_sha`/`_assert_provenance`/`_release` are imported from
# `_common_2i` (Task 2 review finding 1 — byte-identical across
# sample_2i.py/endpoint_2i.py/preflight_2i.py); local underscore names
# kept so this module's own calls resolve unchanged.

def real_loaders() -> dict:
    from harness import HFRunner

    def olmo7b(commit, device):
        return bi.load_thin(bi.REPO_7B, commit, device=device, dtype="float16")

    return {"olmo7b": olmo7b, "runner": lambda tok, model: HFRunner(tok, model)}


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


# ----------------------------------------------------- predictor-seal gate

def _seal_blob_paths(root, seal: dict) -> list:
    """`predictor_2i.json` itself + every file it lists — the seal's
    `"files"` dict already covers both the draws AND the record file
    for all 34 rungs (`seal_2i.seal_predictor` hashes everything under
    `results/predictor/`), so binding the whole set is binding the
    seal's own integrity claim, not a narrowed reading of it. Paths
    relative to `root`; the seal's own relpath is derived from
    `predictor_seal_path`, not a hardcoded literal, so the two can
    never drift apart (finding 3)."""
    seal_rel = str(bi.predictor_seal_path(root).relative_to(root))
    return [seal_rel, *sorted(seal.get("files", {}))]


def _require_predictor_seal(root, *, blobs_bound=None, repo_root=None) -> dict:
    seal_path = bi.predictor_seal_path(root)
    if not seal_path.is_file():
        raise RuntimeError(f"refusing: the predictor seal {seal_path} is missing "
                           f"— the endpoint stage runs only after "
                           f"{bi.PREDICTOR_SEAL_TAG!r} is cut")
    seal = json.loads(seal_path.read_text())
    blobs_bound = blobs_bound or bi.blobs_bound
    rr = Path(repo_root) if repo_root is not None else bi.REPO
    prefix = os.path.relpath(Path(root), rr)
    rel_paths = [os.path.normpath(os.path.join(prefix, p))
                for p in _seal_blob_paths(root, seal)]
    drift = blobs_bound(bi.PREDICTOR_SEAL_TAG, rel_paths, repo_root=rr)
    if drift:
        raise RuntimeError(f"refusing: {bi.PREDICTOR_SEAL_TAG!r} does not bind "
                           f"{drift} — the predictor has drifted since the seal")
    return seal


# --------------------------------------------------------------- run

def run(*, root=EXP2I, device="mps", loaders=None, dry_run=False,
        tag_exists=None, blob_sha=None, blobs_bound=None, repo_root=None) -> None:
    prereg = require_prereg_2i(tag_exists=tag_exists, blob_sha=blob_sha)
    bi.check_frozen_2i()
    seal = _require_predictor_seal(root, blobs_bound=blobs_bound, repo_root=repo_root)

    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    manifest = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    rungs = tuple(bt.RUNGS)
    pending = [(which, r) for which in WHICH for r in rungs
              if not bi.endpoint_record_path(root, which, r).exists()]
    if dry_run:
        print(f"[2i endpoint] prereg tag {prereg['tag']!r}; predictor seal bound; "
              f"would run {len(pending)} (which, rung) unit(s)", flush=True)
        return
    if not pending and bi.rung_set_path(root).exists():
        print(f"[2i endpoint] nothing to do: all {len(rungs)} rung(s) already run "
              f"for both revisions, rung set already written", flush=True)
        return

    battery = bt.load_battery()
    verify_fn = a2d.load_verify()
    floors = bg.load_floors()
    seal_ref = {"tag": bi.PREDICTOR_SEAL_TAG, "sha256": seal["sha256"]}
    entries = {"stage1_final": bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B),
              "main": bi.entry_main(manifest, bi.REPO_7B)}

    stage1_final = {}
    for which in WHICH:
        which_pending = [r for r in rungs
                        if not bi.endpoint_record_path(root, which, r).exists()]
        if not which_pending:
            # every rung record for this revision already exists — no
            # loader needed for it (review finding 2: only a `which`
            # with at least one missing record earns a model load).
            if which == "stage1_final":
                for rung in rungs:
                    stage1_final[rung] = json.loads(
                        bi.endpoint_record_path(root, which, rung).read_text())
            print(f"[2i endpoint] {which}: all {len(rungs)} rung(s) already "
                  f"present, skipping the loader", flush=True)
            continue
        entry = entries[which]
        commit = entry["commit"]
        model, tok, info = loaders["olmo7b"](commit, device)
        try:
            runner = loaders["runner"](tok, model)
            ckpt = {"revision": entry.get("revision", which), "commit": commit,
                    "kind": entry.get("kind", "thin-loader"),
                    "files": list(entry.get("files", [])),
                    "weight_sha256": info.get("tensor_digest"),
                    "config_source": f"{bi.REPO_7B}@{commit}",
                    "tokenizer_source": f"{bi.REPO_7B}@{commit}"}
            for rung in rungs:
                p = bi.endpoint_record_path(root, which, rung)
                if p.exists():
                    rec = json.loads(p.read_text())
                else:
                    t0 = time.time()
                    ev = evaluate_items(runner, battery[rung], verify_fn)
                    rec = item_record_2i(rung=rung, family=bi.FAMILY, size=bi.SIZE_OUT,
                                         which=which, cap=battery[rung], ev=ev,
                                         ckpt=ckpt, seal=seal_ref, t_s=time.time() - t0)
                    _write(p, rec)
                    print(f"[2i endpoint] {which}/{rung}: {rec['correct']}/{rec['n']}",
                          flush=True)
                if which == "stage1_final":
                    stage1_final[rung] = rec
        finally:
            _release(model)

    counts = {r: stage1_final[r]["correct"] for r in rungs}
    rung_set = bi.rung_set_from_counts(counts, floors)
    endpoint_shas = {}
    for which in WHICH:
        for rung in rungs:
            p = bi.endpoint_record_path(root, which, rung)
            endpoint_shas[str(p.relative_to(root))] = bg.sha256_file(p)
    out = {**rung_set, "endpoint_file_sha256": endpoint_shas}
    _write(bi.rung_set_path(root), out)
    print(f"[2i endpoint] R_OLMO={rung_set['R_OLMO']} R_CAP={rung_set['R_CAP']} "
          f"R_EXTRA={rung_set['R_EXTRA']}", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2i endpoint stage (OLMo-2 7B)")
    ap.add_argument("--root", default=str(EXP2I))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(root=Path(ar.root), device=ar.device, dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
