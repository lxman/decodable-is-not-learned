# experiments/exp2k/make_referents_2k.py
"""Every committed file analyze_2k reads, sha256'd relative to the repo
root: 2j's whole referent list (which carries 2i's, the 2i sweep, the
three verdict records, 2i's instrument) PLUS 2j's verdict record and
instrument modules, 2d's main-tier records for both sizes, the five
stream maps, and 2k's own seal and power record (the campaign
artifacts: absent at the build, so `build()` accepts `allow_missing`
for the pre-campaign manifest and the Task-5 pin is re-cut at the seal
stage — see Task 5 and the process tail)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2K = Path(__file__).resolve().parent
if str(EXP2K.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2K.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2j import make_referents_2j as mk2j  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402

REPO = bg.REPO
N_FILES_2K = None   # Task 5 / seal stage: pinned literally


def referent_files(*, with_campaign=True) -> list:
    files = list(mk2j.referent_files())
    files += [REPO / "experiments/exp2j/results/verdict.json",
              REPO / "experiments/exp2j/analyze_2j.py", REPO / "experiments/exp2j/functionals_2j.py",
              EXP2K / "power_2k.py", EXP2K / "run" / "seal_2k.py"]
    files += list(bk.STREAM_MAPS)
    for size in bk.SIZES_2K:
        for r in bk.R_CAP_DESIGN:
            files += [a2d.tier_record_path(a2d.EXP2D, "main", size, r),
                      a2d.tier_draws_path(a2d.EXP2D, "main", size, r)]
    if with_campaign:
        files += [bk.seal_path(EXP2K), bk.power_path(EXP2K)]
        for size in bk.SIZES_2K:
            for r in bk.R_CAP_DESIGN:
                files += [bk.tier_record_path(EXP2K, size, r), bk.tier_draws_path(EXP2K, size, r)]
    seen, out = set(), []
    for p in files:
        rp = Path(p).resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(rp)
    return out


def _rel(p) -> str:
    return str(Path(p).resolve().relative_to(REPO.resolve()))


def build(path, *, with_campaign=True, n_files=None) -> dict:
    rec = {"note": "sha256 of every committed file analyze_2k reads, relative to the repo root; "
                   "this file's own sha256 is pinned as analyze_2k.REFERENTS_2K_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files(with_campaign=with_campaign):
        if not p.is_file():
            raise FileNotFoundError(p)
        rec["files"][_rel(p)] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    want = N_FILES_2K if n_files is None else n_files
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
    if N_FILES_2K is None or rec.get("n_files") != N_FILES_2K or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has {N_FILES_2K}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP2K / "referents_2k.json"
    r = build(out, with_campaign="--with-campaign" in sys.argv)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
