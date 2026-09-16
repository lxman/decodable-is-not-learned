# experiments/exp4b/battery_4b.py
"""Experiment 4b's foundation: constants, the pin to Experiment 4's
closed tree, paths, the preregistration binding, and the loaders that
read Exp 4's committed records (design successor to `experiment-4-
design.md`, ANALYSIS-ONLY — Exp 4's own bytes, never a fresh model
load).

Everything under `experiments/exp2*`, `experiments/exp3*`, and
`experiments/exp4/` is FROZEN here too: read, never edited.
`battery_4.check_frozen_4()` covers the exp2*/exp3* transitive
imports; `EXP4_CLOSED_SHA256_4B`/`check_exp4_closed_4b` adds the seven
files of `experiments/exp4/` itself, pinned to their content at tag
`exp4-closed` (2g's `predictor_2g.git_tag_exists`/`git_blob_sha256`
pattern, applied to a whole module instead of one seal target)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXP4B = Path(__file__).resolve().parent
EXPERIMENTS = EXP4B.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402

EXP4 = battery_4.EXP4
RESULTS_4B = EXP4B / "results"

PREREG_TAG_4B = "exp4b-preregistered"
CLOSED_TAG_4B = "exp4b-closed"
EXP4_CLOSED_TAG = "exp4-closed"

INSTRUMENT_BLOBS_4B = (
    "experiments/exp4b/analyze_4b.py",
    "experiments/exp4b/battery_4b.py",
    "experiments/exp4b/placebo_4b.py",
    "experiments/exp4b/power_ext_4b.py",
    "experiments/exp4b/levels_4b.py",
)

# The seven files of `experiments/exp4/` pinned to their content at
# tag `exp4-closed`, repo-relative keys. Recomputed with:
#   for f in __init__.py analyze_4.py battery_4.py metric_4.py \
#            collect_4.py power_4.py make_referents_4.py; do
#     /opt/homebrew/bin/git show exp4-closed:experiments/exp4/$f | shasum -a 256
#   done
EXP4_CLOSED_SHA256_4B = {
    "experiments/exp4/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp4/analyze_4.py":
        "0cbf7dc9ae505e1cde567249ee8d9a3368cf5aa7001152145eb326c91a51d8fd",
    "experiments/exp4/battery_4.py":
        "7c6ea88817b9dc421068f9637c164754c08ded4d6af8a7e581454be9187ae4c8",
    "experiments/exp4/metric_4.py":
        "814125a47eb922d1c3355a401efb20cab8c0520be91f5e11c16cd3545723b86b",
    "experiments/exp4/collect_4.py":
        "fb45b86b96943a1a633ed3b5ec22e535c1a7b3307d56bd4b3fcb237e3013e617",
    "experiments/exp4/power_4.py":
        "99949ed9f573959110779e6b3826c12606f8f7c0ccafefe6bcf8cddd4463515d",
    "experiments/exp4/make_referents_4.py":
        "e8b9cff34a34c830e2e07302eae6bcd811fe22fe978f77c0ea32ff07d4491b7e",
}

# ---------------------------------------------------------------- constants

B_4B = 10_000
SEED_4B = 0
B_ALPHA_4B = B_4B
ALPHA_4B = 0.01
MARGINAL_4B = 0.05
MIN_PLACEBO_TOTAL_4B = 8
MIN_PLACEBO_PER_TRAJ_4B = 3
EXT_MULTIPLES_4B = (4.0, 6.0, 8.0, 12.0)
N_SIM_EXT_4B = 1000
EXT_SEED_4B = 4242
N_BOOT_LEVELS_4B = 2000
WORLDS_4B = ("INSUFFICIENT_DATA", "CALIBRATED", "MARGINAL", "NOT-DISTINGUISHABLE")
TYPES_4B = ("arithmetic", "option", "string")

# -------------------------------------------------------------------- paths


def verdict_path_4b(root) -> Path:
    return Path(root) / "results" / "verdict.json"


def verdict_txt_path_4b(root) -> Path:
    return Path(root) / "results" / "VERDICT.txt"


def placebo_record_path_4b(root) -> Path:
    return Path(root) / "results" / "placebo.json"


def power_ext_path_4b(root) -> Path:
    return Path(root) / "results" / "power_ext.json"


# ----------------------------------------------------------------- binding


def check_exp4_closed_4b() -> None:
    battery_4.check_frozen_4()
    bad = []
    for rel, want in EXP4_CLOSED_SHA256_4B.items():
        p = REPO / rel
        got = bg.sha256_file(p) if p.is_file() else None
        if got != want:
            bad.append(f"{rel}: {got} != {want}")
    if bad:
        raise RuntimeError("4b: exp4 module drifted from its exp4-closed pin: " + "; ".join(bad))


def require_prereg_4b(*, tag_exists=None, blob_sha=None) -> dict:
    """`battery_4.require_prereg_4`'s body (2n's `require_prereg_2n`
    pattern, itself 2k's blob binding), on exp4b's own tag and
    instrument blobs."""
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_4B):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_4B} does not exist")
    bound = {}
    for rel in INSTRUMENT_BLOBS_4B:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_4B, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_4B} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_4B, "instrument_blobs": bound}


# ------------------------------------------------------- exp4 record loaders


def load_exp4_verdict_4b(root4) -> dict:
    """Exp 4's committed `verdict.json`. Refuses (`ValueError`) if the
    verdict carries no primary reading to build a placebo null
    against — `INSUFFICIENT_DATA`/`NO-CONVERGENCE`, or a missing
    `primary.T`."""
    p = battery_4.verdict_path(root4)
    v = json.loads(Path(p).read_text())
    if v.get("verdict") in ("INSUFFICIENT_DATA", "NO-CONVERGENCE") or \
            v.get("primary", {}).get("T") is None:
        raise ValueError("4b: exp4 verdict carries no primary")
    return v


def load_exp4_eligibility_4b(root4) -> dict:
    p = battery_4.eligibility_path(root4)
    return json.loads(Path(p).read_text())


def load_exp4_power_4b(root4):
    """The committed `power_4.json` record and the sha256 of its file
    bytes (the second element every downstream gate re-derives its own
    input pin from)."""
    p = battery_4.power_path(root4)
    rec = json.loads(Path(p).read_text())
    return rec, bg.sha256_file(p)


def cells_from_verdict_4b(v: dict) -> list:
    """The committed cells of an exp4 verdict, each reduced to `traj,
    rung, phi, t_clear, t_clear_index` — `t_clear_index` is `t_clear`'s
    position on `battery_4.GRID_4[traj]`, re-derived by grid lookup
    (never retyped). Raises `ValueError` if a cell's `t_clear` is not
    on that trajectory's grid."""
    out = []
    for c in v.get("cells", []):
        traj = c["traj"]
        t_clear = c["t_clear"]
        grid = list(battery_4.GRID_4[traj])
        try:
            idx = grid.index(t_clear)
        except ValueError:
            raise ValueError(f"4b: t_clear {t_clear} not on GRID_4[{traj}]")
        out.append({"traj": traj, "rung": c["rung"], "phi": c["phi"],
                    "t_clear": t_clear, "t_clear_index": idx})
    return out


def real_design_4b(cells: list) -> dict:
    """`{traj: {"n": n_M, "clear_indices": sorted C_M, "rungs":
    sorted rung names}}` over every trajectory in
    `battery_4.TRAJECTORIES_4` — a trajectory with no committed cell
    reads `n=0, clear_indices=[], rungs=[]`."""
    out = {traj: {"n": 0, "clear_indices": [], "rungs": []}
           for traj in battery_4.TRAJECTORIES_4}
    for c in cells:
        traj = c["traj"]
        out[traj]["n"] += 1
        out[traj]["clear_indices"].append(c["t_clear_index"])
        out[traj]["rungs"].append(c["rung"])
    for traj in out:
        out[traj]["clear_indices"] = sorted(out[traj]["clear_indices"])
        out[traj]["rungs"] = sorted(out[traj]["rungs"])
    return out


def T_4_from_verdict_4b(v: dict) -> float:
    return float(v["primary"]["T"])
