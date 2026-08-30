# experiments/exp2l/make_referents_2l.py
"""Every committed file analyze_2l reads BEFORE the campaign, sha256'd
relative to the repo root: 2k's whole post-campaign referent list
(`make_referents_2k.referent_files(with_campaign=True)` — 2j's, 2i's,
the 2i predictor stage and sweep, 2k's 36 tier files, seal and power
record) + 2k's verdict record and its three instrument blobs + 2i's
`run/endpoint_2i.py` + 2l's own `checkpoints_2l.json`,
`hub_inventory_olmo13b.json` and `power_2l.py`. The campaign artifacts
(68 endpoint records, the rung set, the power record, the sweep, gate
1) are NOT in this manifest — they are bound by `exp2l-endpoint-sealed`
and cross-checked at analysis time (record failures, the composite
`endpoint_sha256`, gate 1 re-derived) — so the preregistration tag is
never re-cut after the campaign."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2L = Path(__file__).resolve().parent
if str(EXP2L.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2L.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2k import make_referents_2k as mk2k  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402

REPO = bg.REPO
N_FILES_2L = None   # Task 5


def referent_files() -> list:
    files = list(mk2k.referent_files(with_campaign=True))
    files += [bk.EXP2K / "results" / "verdict.json"]
    files += [REPO / rel for rel in bk.INSTRUMENT_BLOBS_2K]
    files += [REPO / "experiments/exp2i/run/endpoint_2i.py",
              bl.CHECKPOINTS_PATH, bl.HUB_INVENTORY_PATH, EXP2L / "power_2l.py"]
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
    rec = {"note": "sha256 of every committed file analyze_2l reads before the campaign, relative "
                   "to the repo root; this file's own sha256 is pinned as "
                   "analyze_2l.REFERENTS_2L_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files():
        if not p.is_file():
            raise FileNotFoundError(p)
        rec["files"][_rel(p)] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    want = N_FILES_2L if n_files is None else n_files
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
    if N_FILES_2L is None or rec.get("n_files") != N_FILES_2L or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has {N_FILES_2L}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP2L / "referents_2l.json"
    r = build(out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
