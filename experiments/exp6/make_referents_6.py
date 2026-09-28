# experiments/exp6/make_referents_6.py
"""The pre-campaign referent manifest: every committed file OUTSIDE
exp6 that the analyzer reads — the anchors' committed predictor streams
(2k, 2i), the control's (exp3), the four families' Mac records of the
anchors on every grid point, the five verdict records S9 and S10 read,
the four checkpoint manifests — with its sha256. The manifest's own sha
is a literal in the analyzer; campaign artifacts are bound by the seal
tags instead.

    python -m experiments.exp6.make_referents_6        (writes referents_6.json)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP6 = Path(__file__).resolve().parent
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp6 import battery_6 as b6  # noqa: E402
from experiments.exp6 import referents_6 as rf  # noqa: E402

PATH = EXP6 / "referents_6.json"


def _rel(p) -> str:
    return str(Path(p).relative_to(b6.REPO))


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build() -> dict:
    files = {}
    for p in rf.referent_files():
        files[_rel(p)] = _sha(p)
    return {"n_files": len(files), "files": dict(sorted(files.items()))}


def dumps(rec: dict) -> str:
    return json.dumps(rec, indent=1, sort_keys=True) + "\n"


def check_referents(path=PATH, *, sha_pin) -> list:
    """Failures, never an exception for a changed file: the manifest is
    the pinned one, names exactly the files the analyzer reads, and
    every file on disk is the file it names."""
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != sha_pin:
        return [f"6 referent manifest: {path} hashes to {got[:12]}, pinned "
                f"{str(sha_pin)[:12]}"]
    rec = json.loads(raw)
    bad = []
    want = sorted(_rel(p) for p in rf.referent_files())
    if sorted(rec["files"]) != want:
        bad.append("6 referent manifest: its file list is not the list the "
                   "analyzer reads")
    for rel, sha in rec["files"].items():
        p = b6.REPO / rel
        if not p.is_file():
            bad.append(f"6 referent manifest: {rel} missing")
        elif _sha(p) != sha:
            bad.append(f"6 referent manifest: {rel} changed")
    return bad


if __name__ == "__main__":
    text = dumps(build())
    PATH.write_text(text)
    print(json.loads(text)["n_files"], "files; sha256",
          hashlib.sha256(text.encode()).hexdigest())
