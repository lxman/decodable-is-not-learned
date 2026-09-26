# experiments/exp5b/make_referents_5b.py
"""Every committed file `analyze_5b.run()` reads BEFORE the campaign, sha256
relative to the repo root (Experiment 5's `make_referents_5` shape):
  1. Experiment 5's own referent list (`make_referents_5.referent_files_5()`: the 34 item files, 2d's
     verdict, 2c's/2d's finals, 2g's/2h's grids, the manifest, the inventory, the slice, power_5.py)
  2. every file under `experiments/exp5/results/` (`*.json` and `VERDICT.txt`) — Experiment 5's whole
     closed record, which `analyze_5.run()` reads inside gate 2
  3. Experiment 5's thirteen instrument blobs and `experiments/exp5/projection.md`
  4. `experiments/exp5/referents_5.json`
5b's OWN campaign artifacts (its units, host, gate1 and power records, its projection) are never here."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP5B = Path(__file__).resolve().parent
REPO = EXP5B.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import make_referents_5 as mkr5  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402

N_FILES_5B = 8399      # pinned at Task 6 step 5 (built: 8,399 files; brief's "≈ 8,400" estimate)


def referent_files_5b() -> list:
    files = list(mkr5.referent_files_5())
    res = b5b.EXP5 / "results"
    files += sorted(p for p in res.rglob("*.json") if p.is_file())
    files.append(res / "VERDICT.txt")
    files += [REPO / rel for rel in b5.INSTRUMENT_BLOBS_5]
    files.append(b5b.EXP5 / "projection.md")
    files.append(b5b.EXP5 / "referents_5.json")
    seen, out = set(), []
    for p in files:
        rp = Path(p).resolve()
        if rp not in seen and rp.is_file():
            seen.add(rp)
            out.append(rp)
    return out


def _rel(p) -> str:
    return str(Path(p).resolve().relative_to(REPO.resolve()))


def build(path, *, n_files=None) -> dict:
    rec = {"note": "sha256 of every committed file analyze_5b.run() reads before the campaign, relative "
                   "to the repo root; this file's own sha256 is pinned as analyze_5b.REFERENTS_5B_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files_5b():
        rec["files"][_rel(p)] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    want = N_FILES_5B if n_files is None else n_files
    if want is not None and rec["n_files"] != want:
        raise ValueError(f"{rec['n_files']} files, expected {want}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def check_referents_5b(path, *, sha_pin) -> list:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    bad = []
    if N_FILES_5B is None or rec.get("n_files") != N_FILES_5B or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has {N_FILES_5B}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP5B / "referents_5b.json"
    r = build(out, n_files=None)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
