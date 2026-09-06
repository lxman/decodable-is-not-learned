# experiments/exp2n/make_referents_2n.py
"""Every committed file analyze_2n reads BEFORE the campaign, sha256'd
relative to the repo root: 2m's whole pre-campaign referent list
(`make_referents_2m.referent_files()` — 2l's, 2k's, 2j's, 2i's lists,
the 2i predictor stage and sweep, 2k's tier files, seal and power
record, 2l's OWN campaign artifacts) + 2m's OWN campaign artifacts (its
endpoint records, rung set, power record, sweep tree, gate1.json and
verdict.json — S8 reads the SmolLM3-3B outcome through 2m's frozen
loaders) + 2m's four instrument blobs + 2n's own `checkpoints_2n.json`,
`hub_inventory_comma.json` and `power_2n.py`. 2n's campaign artifacts
(102 endpoint records, the rung set, the power record, the sweep, gate
1) are NOT in this manifest — they are bound by `exp2n-endpoint-sealed`
and cross-checked at analysis time — so the preregistration tag is
never re-cut after the campaign."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2N = Path(__file__).resolve().parent
if str(EXP2N.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2N.parent.parent))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402
from experiments.exp2m import make_referents_2m as mk2m  # noqa: E402
from experiments.exp2n import battery_2n as bn  # noqa: E402

REPO = bg.REPO
N_FILES_2N = None   # Task 5: the pre-campaign manifest, byte-idempotent


def _2m_campaign_files() -> list:
    files = [bm.rung_set_path(bm.EXP2M), bm.power_path(bm.EXP2M), bm.gate1_path(bm.EXP2M),
             bm.EXP2M / "results" / "verdict.json"]
    for which in bm.ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            files.append(bm.endpoint_record_path(bm.EXP2M, which, r))
    for step in bm.GRID_3B + (bm.TWIN,):
        files.append(bm.checkpoint_record_path(bm.EXP2M, step))
        for r in bt.RUNGS:
            files.append(bm.record_path(bm.EXP2M, step, r))
    return files


def referent_files() -> list:
    files = list(mk2m.referent_files())
    files += _2m_campaign_files()
    files += [REPO / rel for rel in bm.INSTRUMENT_BLOBS_2M]
    files += [bn.CHECKPOINTS_PATH, bn.HUB_INVENTORY_PATH, EXP2N / "power_2n.py"]
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
    rec = {"note": "sha256 of every committed file analyze_2n reads before the campaign, relative "
                   "to the repo root; this file's own sha256 is pinned as "
                   "analyze_2n.REFERENTS_2N_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files():
        if not p.is_file():
            raise FileNotFoundError(p)
        rec["files"][_rel(p)] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    want = N_FILES_2N if n_files is None else n_files
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
    if N_FILES_2N is None or rec.get("n_files") != N_FILES_2N or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has {N_FILES_2N}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP2N / "referents_2n.json"
    r = build(out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
