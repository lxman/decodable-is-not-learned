# experiments/exp2k/run/seal_2k.py
"""Exp 2k predictor seal (design §3.6): one committed file,
`results/predictor_2k.json`, closing the tier before the power record
and the analyzer. Refuses if it exists (the seal runs once), if any of
the 2 × 9 record+draws pairs is missing, if a halt marker exists, on
any record-provenance failure (`battery_2k.tier_record_failures_2k`
with 2i's committed sha per cell), or on any gate-1 diff re-derived
from 2d's committed file. Every count — at 64, 128, 192, 256 — is
recomputed from the raw draws; nothing is copied from a record. The
TAG `exp2k-predictor-sealed` is cut by the supervisor AFTER the power
record (it binds the tier files, this seal and the power record)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXP2K = Path(__file__).resolve().parents[1]
REPO = EXP2K.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2k import analyze_2k as an  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402


def seal_predictor(root=EXP2K, *, tag_exists=None, blob_sha=None, frozen_check=None) -> dict:
    """`frozen_check` is a TEST-ONLY injection point (the worlds pass a
    no-op until Task 5 pins FROZEN_SHA256_2K, then drop it); the campaign
    never passes it."""
    root = Path(root)
    out_path = bk.seal_path(root)
    if out_path.exists():
        raise RuntimeError(f"refusing: {out_path} already exists — the tier is sealed")
    bk.require_prereg_2k(tag_exists=tag_exists, blob_sha=blob_sha)
    bg.check_frozen_imports_2g()
    bi.check_frozen_2i()
    (frozen_check or bk.check_frozen_2k)()
    bi.check_pythia_predictor_files()
    if bk.halt_markers(root):
        raise RuntimeError(f"refusing: halt marker(s) present {[p.name for p in bk.halt_markers(root)]}")
    missing = [f"{s}/{r}" for s in bk.SIZES_2K for r in bk.R_CAP_DESIGN
               if not (bk.tier_record_path(root, s, r).is_file()
                       and bk.tier_draws_path(root, s, r).is_file())]
    if missing:
        raise RuntimeError(f"refusing: {len(missing)} cell(s) missing a record+draws pair: {missing}")
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    cells, counts, by_k, gate1 = {}, {}, {}, {}
    for size in bk.SIZES_2K:
        failures, c = an.load_tier_2k(root, size, battery=battery, verify_fn=verify_fn,
                                      rungs=bk.R_CAP_DESIGN)
        if failures:
            raise RuntimeError(f"refusing to seal: {len(failures)} failure(s) at {size}: "
                               f"{failures[:5]}")
        cells[size] = c
        counts[size] = {r: c[r]["counts"][bk.K_TOTAL] for r in bk.R_CAP_DESIGN}
        by_k[size] = {str(k): {r: c[r]["counts"][k] for r in bk.R_CAP_DESIGN} for k in bk.LADDER_K}
        gate1[size] = {r: c[r]["gate1_rederived"] for r in bk.R_CAP_DESIGN}
    tier_dir = root / "results" / bk.TIER
    files = {str(p.relative_to(root)): bg.sha256_file(p)
             for p in sorted(tier_dir.rglob("*")) if p.is_file()}
    rec = {"files": files, "counts": counts, "counts_by_k": by_k, "gate1": gate1,
           "sha256": an.seal_sha_of(files), "tag": bk.SEAL_TAG_2K,
           "sampling": {"sizes": list(bk.SIZES_2K), "seeds": list(bk.SEEDS_2K),
                        "draws_per_seed": bk.DRAWS_PER_SEED, "k_total": bk.K_TOTAL,
                        "temperature": 1.0, "truncation": "none", "dtype": a2d.SAMPLING_DTYPE,
                        "stream_namespace": a2d.STREAM_NAMESPACE,
                        "model_sha": {s: bk.pythia_sha(s) for s in bk.SIZES_2K}}}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"[2k seal] sealed: {len(files)} files, sha256 {rec['sha256']}; gate 1 re-derived "
          f"0 diffs on {2 * 9} cells", flush=True)
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2k predictor seal")
    ap.add_argument("--root", default=str(EXP2K))
    ar = ap.parse_args(argv)
    seal_predictor(root=Path(ar.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
