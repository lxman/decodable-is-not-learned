# experiments/exp2k/make_referents_2k.py
"""Every committed file analyze_2k reads BEFORE the campaign, sha256'd
relative to the repo root: 2j's whole referent list (which carries
2i's, the 2i sweep, the three verdict records, 2i's instrument), 2j's
verdict record and instrument modules (`analyze_2j.py`,
`functionals_2j.py`), 2k's own `power_2k.py` and `run/seal_2k.py`, the
five committed stream maps, and 2d's 36 main-tier record+draws files
(both sizes x nine R_CAP rungs) — every input that exists before a
model is ever sampled. `build()`'s default is `with_campaign=False`:
this is the manifest `analyze_2k.REFERENTS_2K_SHA256` pins. The
campaign artifacts (2k's own 18 tier records, 18 draws files, the seal
`predictor_2k.json` and the power record `power_2k.json`) are NOT in
that manifest — they are bound by the seal tag
(`exp2k-predictor-sealed`, via `analyze_2i.require_seal_2i` on
`_seal_paths_2k`) and cross-checked at analysis time by
`seal_failures_2k` and `load_power_2k`, so the preregistration tag is
never re-cut after the campaign runs. `--with-campaign` on the CLI
builds the wider, post-campaign manifest for a descriptive listing
only — nothing in the pipeline consumes it."""
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
N_FILES_2K = 2649   # pre-campaign manifest (with_campaign=False), Task 5


def referent_files(*, with_campaign=False) -> list:
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


def build(path, *, with_campaign=False, n_files=None) -> dict:
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
