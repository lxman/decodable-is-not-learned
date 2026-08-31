# experiments/exp2l/run/endpoint_2l.py
"""Exp 2l stage 1 — the endpoint stage: OLMo-2 13B's stage-1 endpoint
(`stage1_final`) AND `main` through the thin loader, on all 34 rungs,
per-item bits and continuations stored (design §3.3, §7). The
`stage1_final` record fixes R by rule (`battery_2l.rung_set_from_
counts_2l`); `main` is descriptive only. Does NOT run power (the
supervisor runs `power_2l` once after this stage, then cuts
`exp2l-endpoint-sealed`).

Order, load-bearing: (1) `require_prereg_2l`; (2) `check_frozen_2l`;
(3) `require_predictor_seals_2l` — BOTH predictor seals must bind their
tags with real git by default (2k's `exp2k-predictor-sealed` over
`analyze_2k._seal_paths_2k`, 2i's `exp2i-predictor-sealed` over
`analyze_2i._predictor_seal_paths`), and each seal's `sha256` must equal
its literal in `battery_2l`, so `PREDICTOR_SHA_2L` is re-derived, never
trusted; (4) the stage. `evaluate_items` (2g) and `item_record_2i` (2i)
are reused; every record stamps `seal_tag = PREDICTOR_TAGS_2L`,
`predictor_sha = PREDICTOR_SHA_2L`, `size = olmo13b`.

Usage: python -m experiments.exp2l.run.endpoint_2l [--dry-run]
"""

from __future__ import annotations

import argparse
import json
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
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i.run._common_2i import (  # noqa: E402
    assert_provenance as _assert_provenance,
    ckpt_of,
    release as _release,
)
from experiments.exp2i.run.endpoint_2i import item_record_2i  # noqa: E402
from experiments.exp2k import analyze_2k as an2k  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402


def real_loaders(batch_size: int = bl.BATCH_SIZE_2L) -> dict:
    from harness import HFRunner

    def olmo13b(commit, device):
        return bl.load_thin_13b(commit, device=device, dtype="float16")

    return {"olmo13b": olmo13b, "runner": lambda tok, model: HFRunner(tok, model, batch_size)}


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


# -------------------------------------------------------- predictor seals

def require_predictor_seals_2l(*, tag_exists=None, blobs_bound=None, root_2i=bi.EXP2I,
                               root_2k=bk.EXP2K) -> dict:
    """Both predictor seals bound to their tags (2i's `require_seal_2i`
    over each experiment's own path rule, real git by default), each
    seal's `sha256` equal to its literal, the composite re-derived."""
    seal_2k_p, seal_2i_p = bk.seal_path(root_2k), bi.predictor_seal_path(root_2i)
    for p in (seal_2k_p, seal_2i_p):
        if not p.is_file():
            raise RuntimeError(f"refusing: the predictor seal {p} is missing")
    seal_2k = json.loads(seal_2k_p.read_text())
    seal_2i = an2i._load_predictor_seal_content(root_2i)
    for tag, paths in ((bk.SEAL_TAG_2K, an2k._seal_paths_2k(root_2k, seal_2k)),
                       (bi.PREDICTOR_SEAL_TAG, an2i._predictor_seal_paths(root_2i, seal_2i))):
        r = an2i.require_seal_2i(tag, paths, tag_exists=tag_exists, blobs_bound=blobs_bound)
        if r["failures"]:
            raise RuntimeError(f"refusing: predictor seal: {r['failures'][0]}")
    if seal_2k.get("sha256") != bl.SEAL_2K_SHA256:
        raise RuntimeError(f"refusing: 2k's seal sha {seal_2k.get('sha256')!r} is not the "
                           f"literal {bl.SEAL_2K_SHA256!r}")
    if seal_2i.get("sha256") != bl.SEAL_2I_SHA256:
        raise RuntimeError(f"refusing: 2i's seal sha {seal_2i.get('sha256')!r} is not the "
                           f"literal {bl.SEAL_2I_SHA256!r}")
    psha = bl.predictor_sha_2l(seal_2k["sha256"], seal_2i["sha256"])
    if psha != bl.PREDICTOR_SHA_2L:
        raise RuntimeError("refusing: PREDICTOR_SHA_2L does not re-derive from the two seals")
    return {"seal_2k": seal_2k, "seal_2i": seal_2i, "predictor_sha": psha}


# --------------------------------------------------------------- run

def run(*, root=EXP2L, root_2i=bi.EXP2I, root_2k=bk.EXP2K, device="mps", loaders=None,
        dry_run=False, tag_exists=None, blob_sha=None, blobs_bound=None) -> None:
    prereg = bl.require_prereg_2l(tag_exists=tag_exists, blob_sha=blob_sha)
    bl.check_frozen_2l()
    seals = require_predictor_seals_2l(tag_exists=tag_exists, blobs_bound=blobs_bound,
                                       root_2i=root_2i, root_2k=root_2k)
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    manifest = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    rungs = tuple(bt.RUNGS)
    pending = [(w, r) for w in bl.ENDPOINT_WHICH for r in rungs
               if not bl.endpoint_record_path(root, w, r).exists()]
    if dry_run:
        print(f"[2l endpoint] prereg tag {prereg['tag']!r}; both predictor seals bound "
              f"(predictor_sha {seals['predictor_sha'][:12]}); would run {len(pending)} "
              f"(which, rung) unit(s)", flush=True)
        return
    if not pending and bl.rung_set_path(root).exists():
        print(f"[2l endpoint] nothing to do: all {len(rungs)} rung(s) already run for both "
              f"revisions, rung set already written", flush=True)
        return

    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    floors = bg.load_floors()
    seal_ref = {"tag": bl.PREDICTOR_TAGS_2L, "sha256": seals["predictor_sha"]}
    entries = {"stage1_final": bl.entry_13b(manifest, bl.ENDPOINT_STEP_13B),
               "main": bl.entry_main_13b(manifest)}
    stage1_final = {}
    for which in bl.ENDPOINT_WHICH:
        which_pending = [r for r in rungs if not bl.endpoint_record_path(root, which, r).exists()]
        if not which_pending:
            if which == "stage1_final":
                for rung in rungs:
                    stage1_final[rung] = json.loads(
                        bl.endpoint_record_path(root, which, rung).read_text())
            print(f"[2l endpoint] {which}: all {len(rungs)} rung(s) already present, skipping "
                  f"the loader", flush=True)
            continue
        entry = entries[which]
        model = None
        try:
            model, tok, info = loaders["olmo13b"](entry["commit"], device)
            runner = loaders["runner"](tok, model)
            ckpt = ckpt_of(entry, info, repo=bl.REPO_13B, revision_fallback=which)
            for rung in rungs:
                p = bl.endpoint_record_path(root, which, rung)
                if p.exists():
                    rec = json.loads(p.read_text())
                else:
                    t0 = time.time()
                    ev = evaluate_items(runner, battery[rung], verify_fn)
                    rec = item_record_2i(rung=rung, family=bl.FAMILY, size=bl.SIZE_OUT,
                                         which=which, cap=battery[rung], ev=ev, ckpt=ckpt,
                                         seal=seal_ref, t_s=time.time() - t0)
                    _write(p, rec)
                    print(f"[2l endpoint] {which}/{rung}: {rec['correct']}/{rec['n']}", flush=True)
                if which == "stage1_final":
                    stage1_final[rung] = rec
        finally:
            _release(model)

    counts = {r: stage1_final[r]["correct"] for r in rungs}
    rung_set = bl.rung_set_from_counts_2l(counts, floors)
    endpoint_shas = {}
    for which in bl.ENDPOINT_WHICH:
        for rung in rungs:
            p = bl.endpoint_record_path(root, which, rung)
            endpoint_shas[str(p.relative_to(root))] = bg.sha256_file(p)
    _write(bl.rung_set_path(root), {**rung_set, "endpoint_file_sha256": endpoint_shas})
    print(f"[2l endpoint] R_13B={rung_set['R_13B']} R_PRIMARY={rung_set['R_PRIMARY']} "
          f"R_ELEVEN_EXTRA={rung_set['R_ELEVEN_EXTRA']} R_EXTRA={rung_set['R_EXTRA']} "
          f"primary_is_the_nine={rung_set['primary_is_the_nine']}", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2l endpoint stage (OLMo-2 13B)")
    ap.add_argument("--root", default=str(EXP2L))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(root=Path(ar.root), device=ar.device, dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
