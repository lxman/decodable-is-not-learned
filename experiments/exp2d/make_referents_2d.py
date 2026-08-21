"""Build `referents_2d.json`: the sha256 of every committed input file
the analyzer reads that is not already pinned by literal in
analyze_2d.py — 2c's 204 m4 eval records, the 34 item files (again,
so the manifest is self-contained), exp3's 4 reversal shard records
and 4 redecode records. Run at BUILD on the committed trees; the
file's own sha is then pinned as `REFERENTS_FILE_SHA256`. Re-running
on unchanged trees is byte-idempotent (sorted keys, fixed indent)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2D = Path(__file__).resolve().parent
if str(EXP2D.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2D.parent.parent))

from experiments.exp2d import analyze_2d as a  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402


def referent_files() -> list:
    files = []
    for rung in bt.RUNGS:
        files.append(bt.items_path(rung))
        for size in bt.EVAL_SIZES:
            for mode in ("trained", "untrained"):
                files.append(a._m4_path(size, mode, rung))
    for rung in a.REVERSAL_RUNGS:
        for size in bt.PROBE_SIZES:
            files.append(a.EXP3 / "results" / "sampling" / f"{size}_trained"
                         / f"{rung}.json")
            files.append(a.EXP3 / "results" / "sampling" / f"{size}_trained"
                         / f"{rung}.draws.jsonl.gz")
            files.append(a.EXP3 / "results" / "redecode" / f"{size}_trained"
                         / f"{rung}.json")
    return files


def build(path=a.REFERENTS_PATH) -> dict:
    rec = {"note": "sha256 of every committed input file analyze_2d reads "
                   "that is not a code literal there; the file's own "
                   "sha256 is pinned as analyze_2d.REFERENTS_FILE_SHA256",
           "files": {}}
    for p in referent_files():
        rel = str(p.resolve().relative_to(a.REPO))
        rec["files"][rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    rec["n_files"] = len(rec["files"])
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


if __name__ == "__main__":
    r = build()
    print(f"{r['n_files']} files -> {a.REFERENTS_PATH}")
    print("sha256", hashlib.sha256(a.REFERENTS_PATH.read_bytes()).hexdigest())
