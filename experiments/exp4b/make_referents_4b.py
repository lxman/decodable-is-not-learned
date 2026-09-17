# experiments/exp4b/make_referents_4b.py
"""Every committed file `analyze_4b` reads, sha256'd relative to the
repo root (design `experiment-4b-design.md` §3.6 "Referents"; 2n's
`make_referents_2n.py` shape, `experiments/exp4/make_referents_4.py`'s
own copy one experiment over): Exp 4's own pre-campaign referent set
(re-read and re-verified through `make_referents_4.check_referents`
against its pin, then every one of its listed files folded in here
too) UNION Exp 4's reference-stage seal paths (`battery_4.
reference_seal_paths_4`) UNION every file of every sweep unit
(`_load.json`, `align.json`, 34 `sets/<rung>.npz`, for every grid step
of all four trajectories -- the interior of the sweep
`reference_seal_paths_4` does not reach, since that function only
covers the four `STAGE1_FIRST_UNITS_4`) UNION the four trajectories'
`gate1.json` UNION `{results/verdict.json, results/VERDICT.txt,
results/reference/eligibility_4.json, results/reference/power_4.json,
referents_4.json}` -- all under `experiments/exp4/`, ALWAYS the real,
closed tree (`battery_4.EXP4`): this manifest is a pre-tag, one-time
hash walk of Exp 4's own committed campaign, not a function of
whatever `root4` a later analyzer call is given.

exp4b's OWN files (this module, `analyze_4b.py`, `battery_4b.py`,
`placebo_4b.py`, `power_ext_4b.py`, `levels_4b.py`) are NOT in this
manifest -- they are bound by `exp4b-preregistered`
(`battery_4b.require_prereg_4b`), the same split Exp 4 itself drew
between its own `INSTRUMENT_BLOBS_4` (tag-bound) and its upstream
referents (manifest-bound)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP4B = Path(__file__).resolve().parent
EXPERIMENTS = EXP4B.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import make_referents_4 as mkr4  # noqa: E402

# Measured empirically by running `build()` against the real, closed
# exp4 tree once (see PROGRESS.md's Task 5 entry for the count and the
# real-tree timing) -- exp4's own `N_FILES_4` pattern. Union size after
# dedup: 3,615 (exp4's own referents) + 849 (reference-seal paths) +
# 3,312 (interior sweep-unit files, 92 grid steps x 36) + 4 (gate1.json)
# + 5 (exp4 top-level files) - 146 overlap (the four STAGE1_FIRST_UNITS_4
# already counted by the interior sweep walk, 4 x 36 = 144; eligibility_
# 4.json/power_4.json already counted by reference_seal_paths_4, which
# appends both) = 7,639.
N_FILES_4B = 7639


def _sweep_unit_files_4b() -> list:
    """`_load.json` + `align.json` + 34 `sets/<rung>.npz`, for EVERY
    grid step of all four trajectories -- the interior of the sweep
    that `battery_4.reference_seal_paths_4` does not reach (it covers
    only the four `STAGE1_FIRST_UNITS_4`, i.e. each trajectory's FIRST
    step)."""
    files = []
    for traj in battery_4.TRAJECTORIES_4:
        for step in battery_4.GRID_4[traj]:
            d = battery_4.unit_dir(battery_4.EXP4, traj, step)
            files.append(d / "_load.json")
            files.append(d / "align.json")
            for r in battery_4.RUNGS:
                files.append(d / "sets" / f"{r}.npz")
    return files


def _exp4_referents_files_4b() -> list:
    """Every path Exp 4's own committed `referents_4.json` lists,
    re-read and re-verified against `an.REFERENTS_4_SHA256` first
    (`make_referents_4.check_referents` raises on a sha-pin mismatch
    of the manifest file itself, and returns per-file drift as a list
    this function raises on too -- exp4b's own manifest must not be
    built on top of a referent set that has already drifted)."""
    path = an.REFERENTS_PATH_4
    if an.REFERENTS_4_SHA256 is not None:
        bad = mkr4.check_referents(path, sha_pin=an.REFERENTS_4_SHA256)
        if bad:
            raise ValueError(f"4b: exp4's own referents_4.json has drifted: {bad[:5]}")
    rec = json.loads(path.read_bytes())
    return [REPO / rel for rel in rec["files"]]


def referent_files_4b() -> list:
    root = battery_4.EXP4
    files = []
    files += _exp4_referents_files_4b()
    files += [root / p for p in battery_4.reference_seal_paths_4(root)]
    files += _sweep_unit_files_4b()
    for traj in battery_4.TRAJECTORIES_4:
        files.append(battery_4.gate1_path(root, traj))
    files.append(battery_4.verdict_path(root))
    files.append(battery_4.verdict_txt_path(root))
    files.append(battery_4.eligibility_path(root))
    files.append(battery_4.power_path(root))
    files.append(an.REFERENTS_PATH_4)

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
    rec = {"note": "sha256 of every committed file analyze_4b reads, relative to the repo root, "
                   "always the real closed exp4 tree; this file's own sha256 is pinned as "
                   "analyze_4b.REFERENTS_4B_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files_4b():
        if not p.is_file():
            raise FileNotFoundError(p)
        rec["files"][_rel(p)] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    want = N_FILES_4B if n_files is None else n_files
    if want is not None and rec["n_files"] != want:
        raise ValueError(f"{rec['n_files']} files, expected {want}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def check_referents_4b(path, *, sha_pin) -> list:
    """`make_referents_4.check_referents`'s own contract, one experiment
    over: raises ONLY on the sha-pin mismatch of the manifest file
    itself; every per-file drift is collected and RETURNED as a list
    (never raised) -- the caller (`analyze_4b.run()`) is responsible
    for consuming the returned list."""
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    bad = []
    if N_FILES_4B is None or rec.get("n_files") != N_FILES_4B or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has {N_FILES_4B}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP4B / "referents_4b.json"
    r = build(out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
