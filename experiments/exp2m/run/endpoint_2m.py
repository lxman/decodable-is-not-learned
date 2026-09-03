# experiments/exp2m/run/endpoint_2m.py
"""Exp 2m stage 1 — the endpoint stage: three thin loads on all 34
rungs (design §3.4, §7): SmolLM3-3B's stage-1 endpoint (`stage1_final`,
the OUTCOME's endpoint — fixes R by rule via `battery_2m.rung_set_from_
counts_2m`), the last pretraining checkpoint before context extension
(`stage3_final`, descriptive) and the released base from its own repo
(`base`, descriptive). Per-item bits and continuations stored; every
record's `dtype` is `DTYPE_2M`. Does NOT run power (the supervisor runs
`power_2m` once after this stage, then cuts `exp2m-endpoint-sealed`).

Order, load-bearing: (1) `require_prereg_2m`; (2) `check_frozen_2m`;
(3) `require_predictor_seals_2m` — BOTH predictor seals must bind their
tags with real git by default, and each seal's `sha256` must equal its
literal in `battery_2m`, so `PREDICTOR_SHA_2M` is re-derived, never
trusted; (4) the stage. `evaluate_items` (2g) and `ckpt_of` (2i) are
reused; every record stamps `seal_tag = PREDICTOR_TAGS_2M`,
`predictor_sha = PREDICTOR_SHA_2M`, `size = smollm3_3b`.

Usage: python -m experiments.exp2m.run.endpoint_2m [--dry-run]
"""

from __future__ import annotations

import argparse
import json
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
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i.run._common_2i import (  # noqa: E402
    assert_provenance as _assert_provenance,
    ckpt_of,
    release as _release,
)
from experiments.exp2k import analyze_2k as an2k  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402


def real_loaders(batch_size: int = bm.BATCH_SIZE_2M) -> dict:
    from harness import HFRunner

    def thin(repo, commit, device):
        return bm.load_thin_3b(repo, commit, device=device, dtype=bm.DTYPE_2M)

    return {"thin": thin, "runner": lambda tok, model: HFRunner(tok, model, batch_size)}


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


# -------------------------------------------------------- predictor seals

def require_predictor_seals_2m(*, tag_exists=None, blobs_bound=None, root_2i=bi.EXP2I,
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
    if seal_2k.get("sha256") != bm.SEAL_2K_SHA256:
        raise RuntimeError(f"refusing: 2k's seal sha {seal_2k.get('sha256')!r} is not the "
                           f"literal {bm.SEAL_2K_SHA256!r}")
    if seal_2i.get("sha256") != bm.SEAL_2I_SHA256:
        raise RuntimeError(f"refusing: 2i's seal sha {seal_2i.get('sha256')!r} is not the "
                           f"literal {bm.SEAL_2I_SHA256!r}")
    psha = bm.predictor_sha_2m(seal_2k["sha256"], seal_2i["sha256"])
    if psha != bm.PREDICTOR_SHA_2M:
        raise RuntimeError("refusing: PREDICTOR_SHA_2M does not re-derive from the two seals")
    return {"seal_2k": seal_2k, "seal_2i": seal_2i, "predictor_sha": psha}


# --------------------------------------------------------------- run

def run(*, root=EXP2M, root_2i=bi.EXP2I, root_2k=bk.EXP2K, device="mps", loaders=None,
        dry_run=False, tag_exists=None, blob_sha=None, blobs_bound=None) -> None:
    prereg = bm.require_prereg_2m(tag_exists=tag_exists, blob_sha=blob_sha)
    bm.check_frozen_2m()
    seals = require_predictor_seals_2m(tag_exists=tag_exists, blobs_bound=blobs_bound,
                                       root_2i=root_2i, root_2k=root_2k)
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    manifest = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
    rungs = tuple(bt.RUNGS)
    pending = [(w, r) for w in bm.ENDPOINT_WHICH_2M for r in rungs
               if not bm.endpoint_record_path(root, w, r).exists()]
    if dry_run:
        print(f"[2m endpoint] prereg tag {prereg['tag']!r}; both predictor seals bound "
              f"(predictor_sha {seals['predictor_sha'][:12]}); dtype {bm.DTYPE_2M}; would run "
              f"{len(pending)} (which, rung) unit(s)", flush=True)
        return
    if not pending and bm.rung_set_path(root).exists():
        print(f"[2m endpoint] nothing to do: all {len(rungs)} rung(s) already run for all three "
              f"revisions, rung set already written", flush=True)
        return

    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    floors = bg.load_floors()
    seal_ref = {"tag": bm.PREDICTOR_TAGS_2M, "sha256": seals["predictor_sha"]}
    stage1_final = {}
    for which in bm.ENDPOINT_WHICH_2M:
        which_pending = [r for r in rungs if not bm.endpoint_record_path(root, which, r).exists()]
        if not which_pending:
            if which == "stage1_final":
                for rung in rungs:
                    stage1_final[rung] = json.loads(bm.endpoint_record_path(root, which, rung).read_text())
            print(f"[2m endpoint] {which}: all {len(rungs)} rung(s) already present, skipping the "
                  f"loader", flush=True)
            continue
        entry = bm.entry_which_3b(manifest, which)
        model = None
        try:
            model, tok, info = loaders["thin"](entry["repo"], entry["commit"], device)
            runner = loaders["runner"](tok, model)
            ckpt = ckpt_of(entry, info, repo=entry["repo"], revision_fallback=which)
            for rung in rungs:
                p = bm.endpoint_record_path(root, which, rung)
                if p.exists():
                    rec = json.loads(p.read_text())
                else:
                    t0 = time.time()
                    ev = evaluate_items(runner, battery[rung], verify_fn)
                    rec = bm.endpoint_item_record_2m(rung=rung, cap=battery[rung], ev=ev, ckpt=ckpt,
                                                     which=which, seal=seal_ref, t_s=time.time() - t0)
                    _write(p, rec)
                    print(f"[2m endpoint] {which}/{rung}: {rec['correct']}/{rec['n']}", flush=True)
                if which == "stage1_final":
                    stage1_final[rung] = rec
        finally:
            _release(model)

    counts = {r: stage1_final[r]["correct"] for r in rungs}
    rung_set = bm.rung_set_from_counts_2m(counts, floors)
    endpoint_shas = {}
    for which in bm.ENDPOINT_WHICH_2M:
        for rung in rungs:
            p = bm.endpoint_record_path(root, which, rung)
            endpoint_shas[str(p.relative_to(root))] = bg.sha256_file(p)
    _write(bm.rung_set_path(root), {**rung_set, "endpoint_file_sha256": endpoint_shas})
    print(f"[2m endpoint] R_3B={rung_set['R_3B']} R_PRIMARY={rung_set['R_PRIMARY']} "
          f"R_ELEVEN_EXTRA={rung_set['R_ELEVEN_EXTRA']} R_EXTRA={rung_set['R_EXTRA']} "
          f"primary_is_the_nine={rung_set['primary_is_the_nine']}", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2m endpoint stage (SmolLM3-3B: stage1_final, stage3_final, base)")
    ap.add_argument("--root", default=str(EXP2M))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(root=Path(ar.root), device=ar.device, dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
