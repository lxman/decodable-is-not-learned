# experiments/exp2h/make_referents_2h.py
"""Every committed file `analyze_2h` reads from OTHER trees, sha256'd,
relative to the repo root: the 34 rung item files (each already
sha-checked again at load by `battery_2d.load_item_file`'s own
ITEMS_SHA_PIN — 2g's own `referents_2g.json` carries the identical
redundancy for the same 34 files), 2c's 34 committed m4 6.9b records,
2d's committed verdict.json (the floors, read unconditionally by
`analyze_2h.run()` via `battery_2g.load_floors()`, sha-pinned there as
`FLOORS_VERDICT_2D_SHA256` — 2g's own `referents_2g.json` carries the
identical file), 2d's 16 committed main-tier draws files at 1b/410m
for R_69's eight rungs (exactly what `battery_2h.sampler_counts` opens
for those two sizes — it reads ONLY the `.draws.jsonl.gz` file per
(size, rung), never the sibling `.json` tier record), and five files
that double-pin a subset of what
`battery_2h.FROZEN_2G_SHA256`/`check_frozen_2h` already hard-pin (2g's
sealed predictor.json, checkpoints_2g.json, referents_2g.json) plus
2h's own checkpoints_2h.json and hub_inventory_69.json — the same
double-pinning pattern 2g's own `referents_2g.json` uses for ITS
tree's checkpoints_2g.json/hub_inventory.json (also separately pinned
via `CHECKPOINTS_SHA256`)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2H = Path(__file__).resolve().parent
if str(EXP2H.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2H.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402

REPO = bg.REPO
N_FILES_2H = 34 + 34 + 1 + 16 + 3 + 2


def referent_files_2h() -> list:
    files = [bt.items_path(r) for r in bt.RUNGS]                          # 34
    for r in bt.RUNGS:
        files.append(bh.m4_path_69(r))                                   # 34
    files.append(bg.EXP2D / "results" / "verdict.json")                  # 1
    for size in bt.PROBE_SIZES:
        for r in bh.R_69:
            files.append(a2d.tier_draws_path(bh.EXP2D, "main", size, r))  # 16
    files += [bg.EXP2G / "results" / "predictor" / "predictor.json",
              bg.EXP2G / "checkpoints_2g.json", bg.EXP2G / "referents_2g.json"]  # 3
    files += [bh.CHECKPOINTS_PATH_69, bh.HUB_INVENTORY_PATH_69]           # 2
    return files


def build(path) -> dict:
    rec = {"note": "sha256 of every committed file analyze_2h reads from other "
                   "trees, relative to the repo root; this file's own sha256 is "
                   "pinned as analyze_2h.REFERENTS_2H_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files_2h():
        rel = str(Path(p).resolve().relative_to(REPO.resolve()))
        rec["files"][rel] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    if rec["n_files"] != N_FILES_2H:
        raise ValueError(f"{rec['n_files']} files, expected {N_FILES_2H}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def check_referents(path, *, sha_pin) -> list:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    bad = []
    if rec.get("n_files") != N_FILES_2H or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has "
                   f"{N_FILES_2H}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP2H / "referents_2h.json"
    r = build(out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
