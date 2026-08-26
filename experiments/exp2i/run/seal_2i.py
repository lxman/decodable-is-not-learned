# experiments/exp2i/run/seal_2i.py
"""Exp 2i predictor seal (design §3.2, ruling 8): one committed file,
`predictor_2i.json`, closing stage 1 before any 7B weight loads. Refuses
if the seal already exists (the seal runs once) or if any of the 34
rungs' draws+record pair is missing. The counts are recomputed through
`battery_2i.sampler_counts_olmo` — not copied from the per-rung
records — so the seal re-verifies every one of the ≈1.09M draws
against 2c's normalize + exact match under 3c's total wrapper. The
TAG (`exp2i-predictor-sealed`) is cut by the supervisor after this
runs — this module only writes and prints the sha the tag must bind.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

EXP2I = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2I.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp3 import sampler  # noqa: E402

# Copied verbatim from `experiments/exp3/stream_map.json`'s "formula"
# field (`sampler.dump_stream_map`'s own literal) — sampler.py is
# frozen and sha-pinned (`battery_2i.FROZEN_SHA256`), so a drift there
# is caught by `check_frozen_2i()` independently of this copy.
STREAM_FORMULA_2I = ("int.from_bytes(sha256('exp3|{rung}|{size}|{mode}|"
                     "s{seed}|i{item}').digest()[:8], 'big') & ((1<<63)-1)")


def seal_predictor(root=EXP2I) -> dict:
    out_path = bi.predictor_seal_path(root)
    if out_path.exists():
        raise RuntimeError(f"refusing: {out_path} already exists — the predictor "
                           f"is already sealed")
    bi.check_frozen_2i()
    missing = [r for r in bt.RUNGS
              if not (bi.predictor_draws_path(root, r).is_file()
                      and bi.predictor_record_path(root, r).is_file())]
    if missing:
        raise RuntimeError(f"refusing: {len(missing)} rung(s) missing a draws+record "
                           f"pair: {missing}")

    battery = bt.load_battery()
    verify_fn = a2d.load_verify()
    counts = bi.sampler_counts_olmo(bt.RUNGS, root=root, battery=battery,
                                    verify_fn=verify_fn)

    pred_dir = Path(root) / "results" / "predictor"
    files = {str(p.relative_to(root)): bg.sha256_file(p)
            for p in sorted(pred_dir.rglob("*")) if p.is_file()}
    lines = "\n".join(f"{rel} {sha}" for rel, sha in sorted(files.items()))
    sha = hashlib.sha256(lines.encode()).hexdigest()

    manifest = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    commit = bi.entry_1b_endpoint(manifest)["commit"]

    rec = {"files": files, "counts": {r: list(int(c) for c in v)
                                      for r, v in counts.items()},
          "sha256": sha, "tag": bi.PREDICTOR_SEAL_TAG,
          "sampling": {"size": bi.SIZE_PRED, "repo": bi.REPO_1B,
                       "revision": bi.REV_1B_ENDPOINT, "commit": commit,
                       "seed": bi.SAMPLING_SEED, "draws_per_item": bi.DRAWS_PER_ITEM,
                       "temperature": 1.0, "dtype": "float32",
                       "stream_namespace": sampler.STREAM_NAMESPACE,
                       "stream_formula": STREAM_FORMULA_2I}}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"[2i seal] predictor sealed: {len(files)} files, sha256 {sha}", flush=True)
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2i predictor seal")
    ap.add_argument("--root", default=str(EXP2I))
    ar = ap.parse_args(argv)
    seal_predictor(root=Path(ar.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
