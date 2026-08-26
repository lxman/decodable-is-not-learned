# experiments/exp2i/make_referents_2i.py
"""Every committed file `analyze_2i` reads from OTHER trees, sha256'd,
relative to the repo root — PLUS the stage artifacts this experiment
itself produces, listed with `sha256: null` at build time (they do not
exist yet) and REQUIRED to exist by analysis time: a `null` entry whose
path is still missing when `check_referents` runs is a refusal naming
the path; a `null` entry whose path now exists is accepted on presence
alone (there is no fixed hash to pin for a file this manifest predates).

Committed inputs (design §4, brief ruling 10): the 34 item files (each
already sha-checked again at load by `battery_2d.load_item_file`'s own
ITEMS_SHA_PIN); 2d's 68 committed main-tier draws files at 1b/410m for
all 34 rungs — exactly what `battery_2i.sampler_counts_pythia` and
`check_pythia_predictor_files` open; 2g's committed sealed predictor
(the strata source, `analyze_2i.pr.load_predictor`); 2i's own
`checkpoints_2i.json`/`hub_inventory_olmo.json`; every `FROZEN_SHA256`
module (16); 2g's committed 2.8b sweep tree and 2h's committed 6.9b
sweep tree (the reverse-direction descriptive's inputs, design §3.6,
~1,500 record files) — NOT 2g's 12b tree, which `_reverse_direction`
never reads."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2I = Path(__file__).resolve().parent
if str(EXP2I.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2I.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402

REPO = bg.REPO

# discovered once by running build() against the real committed trees,
# then pinned literally (2g's/2h's own referent-manifest convention) —
# the 34+68+1+1+1+20 fixed-count files plus the two sweep trees' walked
# counts (771 for 2g's 2.8b, 806 for 2h's 6.9b, as committed
# 2026-08-25/26) plus 139 not-yet-existing stage-artifact placeholders.
# The 20 (was 16 before the whole-branch review fix wave's I-2) is
# `len(bi.FROZEN_SHA256)`, read dynamically below via
# `referent_files_committed()` — never hardcoded as a path list here.
N_FILES_2I = 34 + 68 + 1 + 1 + 1 + 20 + 771 + 806 + 139


def referent_files_committed() -> list:
    files = [bt.items_path(r) for r in bt.RUNGS]                              # 34
    for size in bt.PROBE_SIZES:
        for r in bt.RUNGS:
            files.append(a2d.tier_draws_path(a2d.EXP2D, "main", size, r))     # 68
    files.append(bg.EXP2G / "results" / "predictor" / "predictor.json")       # 1
    files.append(bi.CHECKPOINTS_PATH)                                         # 1
    files.append(bi.HUB_INVENTORY_PATH)                                       # 1
    files += list(bi.FROZEN_SHA256)                                           # 16
    files += sorted((bg.EXP2G / "results" / "sweep" / "2.8b").rglob("*.json"))
    files += sorted((bh.EXP2H / "results" / "sweep" / bh.SIZE).rglob("*.json"))
    return files


def stage_artifact_files() -> list:
    """The 139 files `analyze_i.run` reads that Task 3's own build does
    not produce: 34 predictor draws + 34 predictor records + 1
    predictor seal, 68 endpoint records + 1 rung set + 1 power record."""
    files = []
    for r in bt.RUNGS:
        files.append(bi.predictor_draws_path(bi.EXP2I, r))
        files.append(bi.predictor_record_path(bi.EXP2I, r))
    files.append(bi.predictor_seal_path(bi.EXP2I))
    for which in ("stage1_final", "main"):
        for r in bt.RUNGS:
            files.append(bi.endpoint_record_path(bi.EXP2I, which, r))
    files.append(bi.rung_set_path(bi.EXP2I))
    files.append(bi.power_path(bi.EXP2I))
    return files


def _rel(p) -> str:
    return str(Path(p).resolve().relative_to(REPO.resolve()))


def build(path) -> dict:
    rec = {"note": "sha256 of every committed file analyze_2i reads from other "
                   "trees, relative to the repo root, plus the 139 stage "
                   "artifacts this experiment itself produces (sha256: null "
                   "until they exist — required at analysis time); this file's "
                   "own sha256 is pinned as analyze_2i.REFERENTS_2I_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files_committed():
        rec["files"][_rel(p)] = bg.sha256_file(p)
    for p in stage_artifact_files():
        rec["files"][_rel(p)] = bg.sha256_file(p) if Path(p).is_file() else None
    rec["n_files"] = len(rec["files"])
    if rec["n_files"] != N_FILES_2I:
        raise ValueError(f"{rec['n_files']} files, expected {N_FILES_2I}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def check_referents(path, *, sha_pin) -> list:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    bad = []
    if rec.get("n_files") != N_FILES_2I or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen "
                   f"layout has {N_FILES_2I}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if want is None:
            if not p.is_file():
                bad.append(f"manifest: {rel} is a required stage artifact, "
                           f"still missing")
            continue
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP2I / "referents_2i.json"
    r = build(out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
