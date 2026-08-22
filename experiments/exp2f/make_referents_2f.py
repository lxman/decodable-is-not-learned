"""Build a referent manifest for Exp 2f: sha256 of every committed
file the analyzer reads from other trees — 2d's main/pilot records and
draws and argmax records for the four cells (20), the 2b/2c probe-item
activation files for both rungs × sizes × {trained, untrained} (8),
the committed m3 probe records (4) and the two item files (2): 34
entries, relative to `base`. On the real trees base = the repository
root; a synthetic world passes its own root. The manifest's own sha
is pinned as `analyze_2f.REFERENTS_FILE_SHA256`. Byte-idempotent."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2F = Path(__file__).resolve().parent
EXPERIMENTS = EXP2F.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402

RUNGS = ("sub3_mid", "arith_next")
SIZES = bt.PROBE_SIZES
MODES = ("trained", "untrained")
N_FILES = 20 + 8 + 4 + 2


def probe_npz_path(size, mode, rung, *, probe_root=None) -> Path:
    """The committed probe-item activation file: 2b's tree for the
    survivor sub3_mid, 2c's for arith_next; a world's own tree when
    `probe_root` is given."""
    if probe_root is not None:
        return (Path(probe_root) / "results" / "activations_probe"
                / f"{size}_{mode}" / f"{rung}.npz")
    exp = bt.EXP2B if rung in bt.REUSED else bt.EXP2C
    return exp / "results" / "activations" / f"{size}_{mode}" / f"{rung}.npz"


def m3_record_path(size, rung, *, probe_root=None) -> Path:
    if probe_root is not None:
        return (Path(probe_root) / "results" / "probes_m3"
                / f"{size}_{rung}_seed0.json")
    exp = bt.EXP2B if rung in bt.REUSED else bt.EXP2C
    return exp / "results" / "probes" / "m3" / f"{size}_{rung}_seed0.json"


def referent_files(*, d2_root=None, probe_root=None) -> list:
    d2 = Path(d2_root or a2d.EXP2D)
    files = []
    for tier in ("pilot", "main"):
        for size in SIZES:
            for rung in RUNGS:
                files.append(a2d.tier_record_path(d2, tier, size, rung))
                files.append(a2d.tier_draws_path(d2, tier, size, rung))
    for size in SIZES:
        for rung in RUNGS:
            files.append(a2d.argmax_record_path(d2, size, rung))
    for size in SIZES:
        for rung in RUNGS:
            for mode in MODES:
                files.append(probe_npz_path(size, mode, rung,
                                            probe_root=probe_root))
    for size in SIZES:
        for rung in RUNGS:
            files.append(m3_record_path(size, rung, probe_root=probe_root))
    for rung in RUNGS:
        files.append(bt.items_path(rung) if probe_root is None
                     else Path(probe_root) / "items" / f"{rung}.json")
    return files


def build(path, *, base=REPO, d2_root=None, probe_root=None) -> dict:
    base = Path(base)
    rec = {"note": "sha256 of every committed file analyze_2f reads from "
                   "other trees, relative to `base`; the file's own sha256 "
                   "is pinned as analyze_2f.REFERENTS_FILE_SHA256",
           "base": "REPO" if base == REPO else str(base), "files": {}}
    for p in referent_files(d2_root=d2_root, probe_root=probe_root):
        rel = str(Path(p).resolve().relative_to(base.resolve()))
        rec["files"][rel] = hashlib.sha256(Path(p).read_bytes()).hexdigest()
    rec["n_files"] = len(rec["files"])
    if rec["n_files"] != N_FILES:
        raise ValueError(f"{rec['n_files']} files, expected {N_FILES}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


if __name__ == "__main__":
    out = EXP2F / "referents_2f.json"
    r = build(out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", hashlib.sha256(out.read_bytes()).hexdigest())
