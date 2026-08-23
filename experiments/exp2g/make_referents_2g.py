# experiments/exp2g/make_referents_2g.py
"""Every committed file analyze_2g reads from OTHER trees, sha256'd,
relative to the repo root: the 11 predictor-rung item files, the 44
probe-item activation files, 2f's 8 eval files + 4 continuity records
+ verdict, 2c's m4 records (34 at 2.8b, 11 at 12b), 2d's verdict and
its 1b argmax (7) and main records+draws (14), 2g's own checkpoint
manifest and Hub inventory, the two activation digest lists."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2G = Path(__file__).resolve().parent
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2f import analyze_2f as a2f  # noqa: E402

REPO = bg.REPO
N_FILES = 11 + 44 + 13 + 45 + 1 + 7 + 14 + 2 + 2


def referent_files() -> list:
    files = [bt.items_path(r) for r in bg.PREDICTOR_RUNGS]
    for size in bg.PROBE_SIZES:
        for mode in bg.MODES:
            for r in bg.PREDICTOR_RUNGS:
                files.append(bg.probe_npz_path(size, mode, r))
    for size in bg.PROBE_SIZES:
        for mode in bg.MODES:
            for r in ("sub3_mid", "arith_next"):
                files.append(a2f.eval_npz_path(a2f.EXP2F, size, mode, r))
            files.append(a2f.continuity_path(a2f.EXP2F, size, mode))
    files.append(a2f.EXP2F / "results" / "verdict.json")
    for size in bg.SWEEP_SIZES:
        for r in bg.sweep_rungs(size):
            files.append(bg.m4_path(size, r))
    files.append(bg.EXP2D / "results" / "verdict.json")
    for r in bg.R_28:
        files.append(a2d.argmax_record_path(bg.EXP2D, "1b", r))
    for r in bg.R_28:
        files.append(a2d.tier_record_path(bg.EXP2D, "main", "1b", r))
        files.append(a2d.tier_draws_path(bg.EXP2D, "main", "1b", r))
    files += [bg.CHECKPOINTS_PATH, bg.HUB_INVENTORY_PATH]
    files += [bg.EXP2B / "results" / "activations_sha256.txt",
              bg.EXP2C / "results" / "activations_sha256.txt"]
    return files


def build(path) -> dict:
    rec = {"note": "sha256 of every committed file analyze_2g reads from other trees, "
                   "relative to the repo root; this file's own sha256 is pinned as "
                   "analyze_2g.REFERENTS_FILE_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files():
        rel = str(Path(p).resolve().relative_to(REPO.resolve()))
        rec["files"][rel] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    if rec["n_files"] != N_FILES:
        raise ValueError(f"{rec['n_files']} files, expected {N_FILES}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def check_referents(path, *, sha_pin) -> list:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    bad = []
    if rec.get("n_files") != N_FILES or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has {N_FILES}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP2G / "referents_2g.json"
    r = build(out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
