"""Build `referents_2e.json`: the sha256 of every committed 2d file
the 2e analyzer reads from the tree — the 136 main-tier and 136
pilot-tier record/draws pairs (272) and 2d's `results/verdict.json`
(the comparison referent). Entries are relative to the tree root so
the same builder pins a synthetic world. Run at BUILD on the real
tree; the file's own sha is then pinned as
`analyze_2e.REFERENTS_FILE_SHA256`. Byte-idempotent on unchanged
trees (sorted keys, fixed indent)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2E = Path(__file__).resolve().parent
if str(EXP2E.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2E.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402

TIERS = ("pilot", "main")
N_FILES = 2 * 2 * len(a2d.RUNGS) * len(a2d.PROBE_SIZES) + 1   # 273


def referent_files(root) -> list:
    root = Path(root)
    files = []
    for tier in TIERS:
        for size in a2d.PROBE_SIZES:
            for rung in a2d.RUNGS:
                files.append(a2d.tier_record_path(root, tier, size, rung))
                files.append(a2d.tier_draws_path(root, tier, size, rung))
    files.append(root / "results" / "verdict.json")
    return files


def build(root, path) -> dict:
    root = Path(root)
    rec = {"note": "sha256 of every 2d tree file analyze_2e reads, relative "
                   "to the 2d tree root; the file's own sha256 is pinned "
                   "as analyze_2e.REFERENTS_FILE_SHA256",
           "files": {}}
    for p in referent_files(root):
        rel = str(p.relative_to(root))
        rec["files"][rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    rec["n_files"] = len(rec["files"])
    if rec["n_files"] != N_FILES:
        raise ValueError(f"{rec['n_files']} files, expected {N_FILES}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


if __name__ == "__main__":
    out = EXP2E / "referents_2e.json"
    r = build(a2d.EXP2D, out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", hashlib.sha256(out.read_bytes()).hexdigest())
