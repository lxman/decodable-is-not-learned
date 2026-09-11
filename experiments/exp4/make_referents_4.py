# experiments/exp4/make_referents_4.py
"""Every committed file `analyze_4` reads BEFORE the campaign, sha256'd
relative to the repo root (2n's `make_referents_2n.py` shape; Task 5
brief's "Referent manifest" list, applied verbatim): the four upstream
checkpoint manifests (2g/2i/2m/2n); every committed sweep file of the
four trajectories (`_checkpoint.json` + the 34 item records per grid
step, 2g's real `step0`, the other three's seeded `twin/`, each
trajectory's own closed `gate1.json`); 2i/2m/2n's `stage1_final`
endpoint records + their `rung_set_*.json`; 2d's and 2e's committed
`results/verdict.json`; 2d's argmax records (410m/1b, the rungs 2d
itself calls rising); 2c's m4 files for the three eval sizes exp4's S4
reads (2.8b/6.9b/12b); 2g's `results/predictor/{predictor.json,
strata.json}`; 2c's item files (`battery_2d.items_path`, all 34
rungs); `hub_inventory_pythia_4.json`; the planted-calibration fixture;
`power_4.py`.

exp4's OWN campaign artifacts (the reference-stage keys, the sweep, the
eligibility/power records) are NOT in this manifest -- they are bound
by `exp4-reference-sealed` (design §3.10) and cross-checked at analysis
time, so the preregistration tag is never re-cut after the campaign."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP4 = Path(__file__).resolve().parent
EXPERIMENTS = EXP4.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402
from experiments.exp2n import battery_2n as bn  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402

N_FILES_4 = 3615


def _sweep_files_4(traj: str) -> list:
    root = battery_4.SWEEP_ROOT_4[traj]
    files = []
    for step in battery_4.GRID_4[traj]:
        files.append(root / f"step{int(step)}" / "_checkpoint.json")
        for r in bt.RUNGS:
            files.append(root / f"step{int(step)}" / f"{r}.json")
    files.append(root / "gate1.json")
    if traj == "pythia_2.8b":
        files.append(root / "step0" / "_checkpoint.json")
        for r in bt.RUNGS:
            files.append(root / "step0" / f"{r}.json")
    else:
        files.append(root / "twin" / "_checkpoint.json")
        for r in bt.RUNGS:
            files.append(root / "twin" / f"{r}.json")
    return files


def referent_files() -> list:
    files = []

    # (1) the four upstream checkpoint manifests
    files += [bg.CHECKPOINTS_PATH, bi.CHECKPOINTS_PATH, bm.CHECKPOINTS_PATH, bn.CHECKPOINTS_PATH]

    # (2) every committed sweep file of the four trajectories
    for traj in battery_4.TRAJECTORIES_4:
        files += _sweep_files_4(traj)

    # (3) 2i/2m/2n's stage1_final endpoint records + their rung sets
    for r in bt.RUNGS:
        files.append(bi.endpoint_record_path(bi.EXP2I, "stage1_final", r))
    files.append(bi.rung_set_path(bi.EXP2I))
    for r in bt.RUNGS:
        files.append(bm.endpoint_record_path(bm.EXP2M, "stage1_final", r))
    files.append(bm.rung_set_path(bm.EXP2M))
    for r in bt.RUNGS:
        files.append(bn.endpoint_record_path(bn.EXP2N, "stage1_final", r))
    files.append(bn.rung_set_path(bn.EXP2N))

    # (4) 2d's and 2e's committed verdict records
    files.append(a2d.EXP2D / "results" / "verdict.json")
    files.append(EXPERIMENTS / "exp2e" / "results" / "verdict.json")

    # (5) 2d's argmax records (410m/1b) over the rungs 2d's own verdict calls rising
    v2d = json.loads((a2d.EXP2D / "results" / "verdict.json").read_bytes())
    rising_2d = [r for r in bt.RUNGS if v2d["per_rung"][r]["rising"]]
    for size in ("410m", "1b"):
        for r in rising_2d:
            files.append(a2d.argmax_record_path(a2d.EXP2D, size, r))

    # (6) 2c's m4 files for the three eval sizes S4 reads: 2.8b (all 34
    # rungs), 12b (the predictor rungs only), 6.9b (2h's pinned set)
    for r in bt.RUNGS:
        files.append(bg.m4_path("2.8b", r))
    for r in bg.PREDICTOR_RUNGS:
        files.append(bg.m4_path("12b", r))
    for r in bh.FINAL_COUNT_PIN_69:
        files.append(bh.m4_path_69(r))

    # (7) 2g's predictor + strata
    files.append(bg.predictor_path(bg.EXP2G))
    files.append(bg.strata_path(bg.EXP2G))

    # (8) 2c's item files (all 34 rungs), via battery_2d.items_path
    for r in bt.RUNGS:
        files.append(bt.items_path(r))

    # (9) exp4's own pre-campaign committed files
    files.append(battery_4.HUB_INVENTORY_PYTHIA_PATH)
    files.append(EXP4 / "tests" / "fixtures" / "calibration_curve_4.json")
    files.append(EXP4 / "power_4.py")

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
    rec = {"note": "sha256 of every committed file analyze_4 reads before the campaign, relative "
                   "to the repo root; this file's own sha256 is pinned as "
                   "analyze_4.REFERENTS_4_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files():
        if not p.is_file():
            raise FileNotFoundError(p)
        rec["files"][_rel(p)] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    want = N_FILES_4 if n_files is None else n_files
    if want is not None and rec["n_files"] != want:
        raise ValueError(f"{rec['n_files']} files, expected {want}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def check_referents(path, *, sha_pin) -> list:
    """2n's contract: raises ONLY on the sha-pin mismatch of the
    manifest file itself; every per-file drift is collected and
    RETURNED as a list (never raised) -- the caller (`analyze_4.run()`)
    is responsible for consuming the returned list (Task 5 finding 2)."""
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    bad = []
    if N_FILES_4 is None or rec.get("n_files") != N_FILES_4 or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has {N_FILES_4}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP4 / "referents_4.json"
    r = build(out)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
