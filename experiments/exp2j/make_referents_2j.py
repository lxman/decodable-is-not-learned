# experiments/exp2j/make_referents_2j.py
"""Every committed file analyze_2j reads, sha256'd relative to the repo
root: 2i's whole referent list (items, 2d draws, 2g predictor, 2i
manifest + inventory, 2i's 22 frozen modules, 2g's 2.8b tree, 2h's
6.9b tree) PLUS 2i's stage artifacts now committed (34 draws + 34
records + seal, 68 endpoint records, rung set, power) and its 771-file
sweep tree, the three verdict records (2i, 2g, 2h), 2i's own two
instrument modules, and 2j's power record. No null entries: every
file exists at build time."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2J = Path(__file__).resolve().parent
if str(EXP2J.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2J.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i import make_referents_2i as mk2i  # noqa: E402

REPO = bg.REPO
N_FILES_2J = None   # discovered once by build() on the real tree, then pinned literally (Task 4)


def referent_files() -> list:
    files = list(mk2i.referent_files_committed())          # 1704
    files += mk2i.stage_artifact_files()                    # 139, all present now
    files += sorted((bi.EXP2I / "results" / "sweep").rglob("*.json"))
    files += [bi.EXP2I / "results" / "verdict.json", bg.EXP2G / "results" / "verdict.json",
              bh.EXP2H / "results" / "verdict.json",
              bi.EXP2I / "analyze_2i.py", bi.EXP2I / "battery_2i.py",
              EXP2J / "results" / "power_2j.json", EXP2J / "power_2j.py"]
    seen, out = set(), []
    for p in files:
        rp = Path(p).resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(rp)
    return out


def _rel(p) -> str:
    return str(Path(p).resolve().relative_to(REPO.resolve()))


def build(path) -> dict:
    rec = {"note": "sha256 of every committed file analyze_2j reads, relative to the repo "
                   "root; this file's own sha256 is pinned as analyze_2j.REFERENTS_2J_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files():
        if not p.is_file():
            raise FileNotFoundError(p)
        rec["files"][_rel(p)] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    if N_FILES_2J is not None and rec["n_files"] != N_FILES_2J:
        raise ValueError(f"{rec['n_files']} files, expected {N_FILES_2J}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def check_referents(path, *, sha_pin) -> list:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    bad = []
    if N_FILES_2J is None or rec.get("n_files") != N_FILES_2J or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has {N_FILES_2J}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP2J / "referents_2j.json"
    r = build(out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
