# experiments/exp2m/make_referents_2m.py
"""Every committed file analyze_2m reads BEFORE the campaign, sha256'd
relative to the repo root: 2l's whole pre-campaign referent list
(`make_referents_2l.referent_files()` — 2k's, 2j's, 2i's lists, the 2i
predictor stage and sweep, 2k's tier files, seal and power record) +
2l's OWN campaign artifacts (its endpoint records, rung set, power
record, sweep tree, gate1.json and verdict.json — S8 reads the 13B
outcome through 2l's frozen loaders) + 2l's four instrument blobs +
2m's own `checkpoints_2m.json`, `hub_inventory_smollm3.json` and
`power_2m.py`. 2m's campaign artifacts (102 endpoint records, the rung
set, the power record, the sweep, gate 1) are NOT in this manifest —
they are bound by `exp2m-endpoint-sealed` and cross-checked at analysis
time — so the preregistration tag is never re-cut after the campaign."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2M = Path(__file__).resolve().parent
if str(EXP2M.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2M.parent.parent))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402
from experiments.exp2l import make_referents_2l as mk2l  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402

REPO = bg.REPO
N_FILES_2M = 3369   # Task 5: the pre-campaign manifest, byte-idempotent


def _2l_campaign_files() -> list:
    files = [bl.rung_set_path(bl.EXP2L), bl.power_path(bl.EXP2L), bl.gate1_path(bl.EXP2L),
             bl.EXP2L / "results" / "verdict.json"]
    for which in bl.ENDPOINT_WHICH:
        for r in bt.RUNGS:
            files.append(bl.endpoint_record_path(bl.EXP2L, which, r))
    for step in bl.GRID_13B + (bl.STEP0,):
        files.append(bl.checkpoint_record_path(bl.EXP2L, step))
        for r in bt.RUNGS:
            files.append(bl.record_path(bl.EXP2L, step, r))
    return files


def referent_files() -> list:
    files = list(mk2l.referent_files())
    files += _2l_campaign_files()
    files += [REPO / rel for rel in bl.INSTRUMENT_BLOBS_2L]
    files += [bm.CHECKPOINTS_PATH, bm.HUB_INVENTORY_PATH, EXP2M / "power_2m.py"]
    seen, out = set(), []
    for p in files:
        rp = Path(p).resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(rp)
    return out


def _rel(p) -> str:
    return str(Path(p).resolve().relative_to(REPO.resolve()))


def build(path, *, n_files=None) -> dict:
    rec = {"note": "sha256 of every committed file analyze_2m reads before the campaign, relative "
                   "to the repo root; this file's own sha256 is pinned as "
                   "analyze_2m.REFERENTS_2M_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files():
        if not p.is_file():
            raise FileNotFoundError(p)
        rec["files"][_rel(p)] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    want = N_FILES_2M if n_files is None else n_files
    if want is not None and rec["n_files"] != want:
        raise ValueError(f"{rec['n_files']} files, expected {want}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def check_referents(path, *, sha_pin) -> list:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    bad = []
    if N_FILES_2M is None or rec.get("n_files") != N_FILES_2M or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has {N_FILES_2M}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP2M / "referents_2m.json"
    r = build(out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
