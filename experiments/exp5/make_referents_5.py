# experiments/exp5/make_referents_5.py
"""Every committed file `analyze_5.run()` reads BEFORE the campaign,
sha256 relative to the repo root (Task 6 brief's referent-manifest
list, applied verbatim over battery_5's own accessors, exp4c's
`make_referents_4c.py` shape):

  1. the 34 item files (`battery_2d.items_path`)
  2. 2d's committed verdict — `battery_5.load_floors_5`'s own read
     (2c's floors, 34 rungs)
  3. 2c's m4 final counts at 2.8b/6.9b/12b (34 x 3, `battery_2g.
     m4_path`/`battery_2h.m4_path_69`)
  4. 2d's argmax final counts at 410m/1b (34 x 2, under `experiments/
     exp2d/results/argmax/`)
  5. 2g's FULL committed 2.8b trained grid (`battery_2g.trained_
     steps("2.8b")`, 21 steps x (34 rungs + `_checkpoint.json`) — S8
     reads the whole grid now, which already covers gate 1(c)'s
     7-step interior subset)
  6. 2g's 12b sweep records at the six B-6 descriptive steps
     (`battery_5.GATE1_DESCRIPTIVE_12B_5`, 6 x 12)
  7. 2h's FULL committed 6.9b trained grid (`battery_2h.trained_
     steps_69()`, 22 x 35 — covers gate 1(c)'s 8-step interior subset)
  8. `checkpoints_5.json`, `hub_inventory_5.json`, `slice_5.npz`,
     `power_5.py`

Exp 5's OWN campaign artifacts (units, gate 1(a)/(b)/(c) records, the
search logs, the host record, the power record, the projection) are
NOT in this manifest — `analyze_5.run()` checks them directly against
their own contracts, never through a referent-manifest sha (they do
not exist before the campaign runs)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP5 = Path(__file__).resolve().parent
EXPERIMENTS = EXP5.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402

N_FILES_5 = 1786


def _argmax_files(size: str) -> list:
    root = EXPERIMENTS / "exp2d" / "results" / "argmax" / f"{size}_trained"
    return [root / f"{r}.json" for r in bt.RUNGS]


def _m4_files(size: str) -> list:
    return [bg.m4_path(size, r) for r in bt.RUNGS]


def _sweep_grid_files(root, size: str, steps, rungs) -> list:
    """`_checkpoint.json` + one rung record per `rungs` for every step,
    2g's own committed layout (`battery_5.interior_record_path_5`'s
    own accessor — the same tree gate 1(c) reads, unrestricted to its
    interior-steps subset). `rungs` is `battery_2g.sweep_rungs(size)`
    — ADJUDICATING (2.8b) committed all 34; REPLICATING (12b)
    committed only the 11 `PREDICTOR_RUNGS` (verified against the
    real tree: `experiments/exp2g/results/sweep/12b/step*/` holds 12
    files per step — 11 rungs + `_checkpoint.json` — never 34; see
    PROGRESS.md, Task 6 finding)."""
    files = []
    for step in steps:
        files.append(bg.checkpoint_record_path(root, size, step))
        for r in rungs:
            files.append(bg.record_path(root, size, step, r))
    return files


def _sweep_grid_files_69(steps) -> list:
    files = []
    for step in steps:
        files.append(bh.checkpoint_record_path_2h(bh.EXP2H, step))
        for r in bt.RUNGS:
            files.append(bh.record_path_2h(bh.EXP2H, step, r))
    return files


def referent_files_5() -> list:
    files = []

    # (1) 2c's 34 item files
    for r in bt.RUNGS:
        files.append(bt.items_path(r))

    # (2) 2d's committed verdict (floors)
    files.append(bg.EXP2D / "results" / "verdict.json")

    # (3) 2c's m4 final counts at 2.8b/6.9b/12b
    files += _m4_files("2.8b")
    files += _m4_files("6.9b")
    files += _m4_files("12b")

    # (4) 2d's argmax final counts at 410m/1b
    files += _argmax_files("410m")
    files += _argmax_files("1b")

    # (5) 2g's full committed 2.8b trained grid (all 34 rungs — ADJUDICATING)
    files += _sweep_grid_files(bg.EXP2G, "2.8b", bg.trained_steps("2.8b"),
                               bg.sweep_rungs("2.8b"))

    # (6) 2g's 12b sweep records at the six B-6 descriptive steps (11
    # PREDICTOR_RUNGS only — REPLICATING; see the Task 6 finding above)
    files += _sweep_grid_files(bg.EXP2G, "12b", b5.GATE1_DESCRIPTIVE_12B_5,
                               bg.sweep_rungs("12b"))

    # (7) 2h's full committed 6.9b trained grid
    files += _sweep_grid_files_69(bh.trained_steps_69())

    # (8) exp5's own committed inputs
    files.append(b5.CHECKPOINTS_PATH_5)
    files.append(b5.HUB_INVENTORY_PATH_5)
    files.append(b5.SLICE_PATH_5)
    files.append(EXP5 / "power_5.py")

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
    rec = {"note": "sha256 of every committed file analyze_5.run() reads before the campaign, "
                   "relative to the repo root; this file's own sha256 is pinned as "
                   "analyze_5.REFERENTS_5_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files_5():
        if not p.is_file():
            raise FileNotFoundError(p)
        rec["files"][_rel(p)] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    want = N_FILES_5 if n_files is None else n_files
    if want is not None and rec["n_files"] != want:
        raise ValueError(f"{rec['n_files']} files, expected {want}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def check_referents_5(path, *, sha_pin) -> list:
    """Raises ONLY on the sha-pin mismatch of the manifest file itself;
    every per-file drift is collected and RETURNED as a list (never
    raised) — the caller (`analyze_5.run()`) is responsible for
    consuming the returned list."""
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    bad = []
    if N_FILES_5 is None or rec.get("n_files") != N_FILES_5 or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has "
                   f"{N_FILES_5}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP5 / "referents_5.json"
    r = build(out, n_files=None)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
