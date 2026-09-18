# experiments/exp4c/make_referents_4c.py
"""Every committed file `analyze_4c` reads BEFORE the campaign, sha256
relative to the repo root (2n's/exp4's own `make_referents_*` shape;
Task 5 brief's referent-manifest list, applied verbatim): the 2h and
2l upstream checkpoint manifests; every committed 2h/2l sweep file
(step0 + 22/16 trained steps x (`_checkpoint.json` + 34 rung records)
+ each's own `gate1.json`); Exp 4's 92 sweep units' `_load.json` + 34
`sets/*.npz` + `align.json` (the discovery gate's own re-derivation of
U on the four known runs), its 5 reference keys' committed files
(`_load.json` + 34 `sets/*.npz` + `global.npz` + `align.json` each —
`battery_4c.exp4_reference_paths_4c`), Exp 4's `eligibility_4.json`
and `power_4.json` (read by the discovery gate's own dependency
chain and by S4's continuity arm, which reuses `analyze_4`'s frozen
per-item alignment code); 2c's item files (`battery_2d.items_path`, all
34 rungs); 2d's committed verdict (`battery_2g.load_floors`'s own
default read, 2c's floors); the design session's `series_known4.json`;
`power_4c.py` itself.

Exp 4c's OWN campaign artifacts (the sweep units, the two gate-1
records) are NOT in this manifest — they are produced by the campaign
and checked directly by `analyze_4c.run()`'s own gates, never
re-derived through a referent-manifest sha (design §3.9: no
intermediate seal, the power record precedes the tag)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP4C = Path(__file__).resolve().parent
EXPERIMENTS = EXP4C.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4c import battery_4c as bc  # noqa: E402

N_FILES_4C = 8160


def _upstream_sweep_files(root, steps, gate1_path) -> list:
    """`root/step<step>/(_checkpoint.json + 34 rung .json)` over
    `steps` (2h's/2l's own committed sweep layout, matching
    `battery_4c.load_outcome_4c`'s reads exactly), plus the one
    `gate1.json` (2h's/2l's own closed-campaign gate 1, not exp4c's)."""
    files = []
    for step in steps:
        d = root / f"step{int(step)}"
        files.append(d / "_checkpoint.json")
        for r in bt.RUNGS:
            files.append(d / f"{r}.json")
    files.append(gate1_path)
    return files


def _exp4_sweep_unit_files(traj) -> list:
    """`_load.json` + 34 `sets/<rung>.npz` + `align.json` for every
    committed grid step of Exp 4's own trajectory — the discovery
    gate's own alignment inputs (`rank_4c.discovery_set_4c` ->
    `analyze_4.load_sweep_tables_4`), NOT `attested/`/`activations/`
    (both gitignored and unread by the discovery gate)."""
    files = []
    for step in battery_4.GRID_4[traj]:
        d = battery_4.unit_dir(battery_4.EXP4, traj, step)
        files.append(d / "_load.json")
        for r in bt.RUNGS:
            files.append(d / "sets" / f"{r}.npz")
        files.append(d / "align.json")
    return files


def _exp4_argmax_outcome_files(traj) -> list:
    """`_checkpoint.json` + 34 rung `.json` records for every committed
    grid step of Exp 4's own trajectory, read from `battery_4.
    SWEEP_ROOT_4[traj]` — NOT under `experiments/exp4/`, but each
    trajectory's UPSTREAM experiment's own committed sweep tree
    (2g's `results/sweep/2.8b/`, 2i's/2m's/2n's own): `battery_4.
    load_outcome_4`'s own reads, the discovery gate's second input
    (rung sets / clear indices, beside the alignment series
    `_exp4_sweep_unit_files` covers)."""
    files = []
    root = battery_4.SWEEP_ROOT_4[traj]
    for step in battery_4.GRID_4[traj]:
        d = root / f"step{int(step)}"
        files.append(d / "_checkpoint.json")
        for r in bt.RUNGS:
            files.append(d / f"{r}.json")
    return files


def referent_files_4c() -> list:
    files = []

    # (1) the 2h and 2l upstream checkpoint manifests
    files.append(bh.CHECKPOINTS_PATH_69)
    files.append(bl.CHECKPOINTS_PATH)

    # (2) every committed 2h/2l sweep file: step0 + trained grid
    files += _upstream_sweep_files(
        bh.sweep_dir_2h(bh.EXP2H), (bc.INIT_STEP_4C,) + tuple(bc.GRID_4C["pythia_6.9b"]),
        bh.gate1_path_2h(bh.EXP2H))
    files += _upstream_sweep_files(
        bl.sweep_dir(bl.EXP2L), (bc.INIT_STEP_4C,) + tuple(bc.GRID_4C["olmo2_13b"]),
        bl.gate1_path(bl.EXP2L))

    # (3) Exp 4's 92 sweep units — the discovery gate's own alignment
    # inputs, plus the upstream argmax-outcome records `battery_4.
    # load_outcome_4` reads (2g's/2i's/2m's/2n's own committed sweep
    # trees) to build the rung sets and clear indices `cells_4c` needs
    for traj in battery_4.TRAJECTORIES_4:
        files += _exp4_sweep_unit_files(traj)
        files += _exp4_argmax_outcome_files(traj)

    # (4) Exp 4's 5 reference keys (the union of REFS_FOR_4C plus the
    # 6.9b gate-1 reference)
    files += bc.exp4_reference_paths_4c(battery_4.EXP4)

    # (5) Exp 4's eligibility + power records
    files.append(battery_4.eligibility_path(battery_4.EXP4))
    files.append(battery_4.power_path(battery_4.EXP4))

    # (6) 2c's item files, all 34 rungs
    for r in bt.RUNGS:
        files.append(bt.items_path(r))

    # (7) 2d's committed verdict — `battery_2g.load_floors`'s own
    # default read (2c's floors)
    files.append(bg.EXP2D / "results" / "verdict.json")

    # (8) the design session's known-answer table + power_4c.py itself
    files.append(EXP4C / "design_session" / "series_known4.json")
    files.append(EXP4C / "power_4c.py")

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
    rec = {"note": "sha256 of every committed file analyze_4c reads before the campaign, "
                   "relative to the repo root; this file's own sha256 is pinned as "
                   "analyze_4c.REFERENTS_4C_SHA256",
           "base": "REPO", "files": {}}
    for p in referent_files_4c():
        if not p.is_file():
            raise FileNotFoundError(p)
        rec["files"][_rel(p)] = bg.sha256_file(p)
    rec["n_files"] = len(rec["files"])
    want = N_FILES_4C if n_files is None else n_files
    if want is not None and rec["n_files"] != want:
        raise ValueError(f"{rec['n_files']} files, expected {want}")
    Path(path).write_text(json.dumps(rec, indent=1, sort_keys=True))
    return rec


def check_referents_4c(path, *, sha_pin) -> list:
    """Raises ONLY on the sha-pin mismatch of the manifest file itself;
    every per-file drift is collected and RETURNED as a list (never
    raised) — the caller (`analyze_4c.run()`) is responsible for
    consuming the returned list (exp4's Task 5 finding 2, carried
    forward)."""
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    bad = []
    if N_FILES_4C is None or rec.get("n_files") != N_FILES_4C or rec["n_files"] != len(rec["files"]):
        bad.append(f"manifest carries {rec.get('n_files')} files, the frozen layout has "
                   f"{N_FILES_4C}")
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
        elif bg.sha256_file(p) != want:
            bad.append(f"manifest: {rel} changed since the manifest was built")
    return bad


if __name__ == "__main__":
    out = EXP4C / "referents_4c.json"
    r = build(out, n_files=None)
    print(f"{r['n_files']} files -> {out}")
    print("sha256", bg.sha256_file(out))
