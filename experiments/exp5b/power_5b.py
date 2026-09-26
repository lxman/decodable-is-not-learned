# experiments/exp5b/power_5b.py
"""Exp 5b's power and calibration record (design §4, dials h/i), written
ONCE at the build — before the tag, from Experiment 5's committed live
cells and the σ_s grid; bound by `exp5b-preregistered` (plan B-8).

Experiment 5's noise model (`power_5.py`) with the one thing it held
fixed now varied: f is ONE draw at σ_s around its truth, entering both R
(Experiment 5's rule, via `stats_5.cell_5` with f_read) and M (5b's, via
`stats_5b.cell_5b`); the three members are draws at σ_s around f's truth
with one shared small-side drift N(0, DRIFT); the large side's reads and
placebo drifts as in Experiment 5. The cell set is fixed at the live
cells (liveness never re-evaluated). Arms per grid point: null / plugin
(the committed a − f as truth) / shrunk (half) / exp5_spread (25 items on
half the cells). One rng, consumed in a FIXED order."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP5B = Path(__file__).resolve().parent
if str(EXP5B.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP5B.parent.parent))

from experiments.exp5 import _threads_5  # noqa: E402,F401
import numpy as np  # noqa: E402

from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import power_5 as pw  # noqa: E402
from experiments.exp5 import stats_5 as ss  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402
from experiments.exp5b import stats_5b as st  # noqa: E402

SIGMA_L_5B = pw.SIGMA_READ_ITEMS_5
DRIFT_5B = pw.DRIFT_SD_ITEMS_5
N_SIM_5B = 1000
SEED_5B = 0
POWER_BAR_5B = 0.75
ARMS_5B = ("null", "plugin", "shrunk", "exp5_spread")
OFFSET_SCALE_5B = {"null": 0.0, "plugin": 1.0, "shrunk": 0.5}
D_GRID_5B = pw.D_GRID_5
FRACTION_GRID_5B = (0.25, 0.5, 0.75, 1.0)
N_MEMBERS_5B = 3
STRUCTURE_KEYS_5B = ("small", "large", "rung", "family", "type", "f", "a", "b_minus", "b_plus",
                     "R", "P", "signed", "c")
ASSUMPTIONS_5B = (
    "the cell set is Experiment 5's 63 live cells with a defined P, fixed; liveness is never re-evaluated",
    "per-read noise is Gaussian on the count, clipped to [0, 500]: sd SIGMA_L_5B = 15.07 items on the "
    "large side (Experiment 5's), sigma_s on the grid on the small side",
    "f is ONE draw at sigma_s around its truth, entering both R and M (box B's re-read of the same "
    "checkpoint is the same read up to the cross-box drift, set to zero here and measured by S11)",
    "the three window members are draws at sigma_s around f's truth with one shared small-side drift "
    "N(0, 4 items); each large-side placebo side carries one drift N(0, 4) shared by its two reads",
    "the plugin arm's truth is each cell's committed a - f (it includes Experiment 5's read noise and "
    "so overstates the effect); the shrunk arm halves it; exp5_spread is Experiment 5's deciding arm",
    "the simulated sigma_hat is the analyzer's own estimator on the simulated small-side reads",
)


def structure_5b(cells5_live: list) -> list:
    out = []
    for c in cells5_live:
        s = {k: c.get(k) for k in STRUCTURE_KEYS_5B}
        s["f"] = int(s["f"])
        s["offset"] = float(s["a"]) - s["f"]
        out.append(s)
    return out


def structure_sha256_5b(structure: list) -> str:
    return hashlib.sha256(json.dumps(structure, sort_keys=True).encode()).hexdigest()


def _cell5_from_reads(s: dict, reads: dict, floor: float) -> dict:
    c5 = ss.cell_5(f=reads["f_read"], reads=reads, floor=floor)
    c5.update({k: s[k] for k in ("small", "large", "rung", "family", "type")})
    c5.update({"bracket": [0, 0], "b_minus_steps": [], "b_plus_steps": [],
               "residual_lo": 0.0, "residual_hi": 0.0})
    return c5


def simulate_5b(structure, floors, *, sigma_s, offset_scale, rng, spread_cells=None,
                spread_items=pw.OFFSET_ITEMS_5) -> list:
    """`spread_cells` (a set of indices) switches to Experiment 5's alternative:
    `spread_items` on the selected cells, zero elsewhere (exp5_spread uses 25;
    the D grid uses D×500); otherwise the plugin truth scaled by `offset_scale`."""
    cells = []
    for i, s in enumerate(structure):
        f_true = s["f"]
        if spread_cells is not None:
            a_true = f_true + (spread_items if i in spread_cells else 0)
        else:
            a_true = f_true + offset_scale * s["offset"]
        f_read = pw._read(f_true, sigma_s, rng)
        lo, hi = pw._read(a_true, SIGMA_L_5B, rng), pw._read(a_true, SIGMA_L_5B, rng)
        d_m, d_p = rng.normal(0.0, DRIFT_5B), rng.normal(0.0, DRIFT_5B)
        bm = [pw._read(a_true + d_m, SIGMA_L_5B, rng), pw._read(a_true + d_m, SIGMA_L_5B, rng)]
        bp = [pw._read(a_true + d_p, SIGMA_L_5B, rng), pw._read(a_true + d_p, SIGMA_L_5B, rng)]
        d_s = rng.normal(0.0, DRIFT_5B)
        members = {step: pw._read(f_true + d_s, sigma_s, rng) for step in b5b.WINDOW_STEPS_5B}
        reads = {"f_read": f_read, "lo": lo, "hi": hi, "a": (lo + hi) / 2, "b_minus": sum(bm) / 2,
                 "b_plus": sum(bp) / 2, "raw": {"lo": lo, "hi": hi, "b_minus": bm, "b_plus": bp}}
        floor = floors[s["rung"]]
        c5 = _cell5_from_reads(s, reads, floor)                # Experiment 5's rule with f noised
        c5b = st.cell_5b(c5, {"f_B": f_read, "members": members}, floor)
        c5b["c_exp5_sim"] = c5["c"]
        cells.append(c5b)
    return cells


def _summ(vals):
    return float(np.mean(vals)), float(np.std(vals))


def arm_5b(structure, floors, *, sigma_s, offset_scale, n_sim, rng, spread=False,
           spread_items=pw.OFFSET_ITEMS_5) -> dict:
    n = len(structure)
    fires = {"5b": 0, "exp5": 0, "naive": 0}
    Ts = {"5b": [], "exp5": [], "naive": []}
    sig = []
    for _ in range(n_sim):
        sel = {i for i in range(n) if rng.random() < pw.Q_5} if spread else None
        cells = simulate_5b(structure, floors, sigma_s=sigma_s, offset_scale=offset_scale, rng=rng,
                            spread_cells=sel, spread_items=spread_items)
        p5b = st.primary_5b(cells, key="c_sym", n_sample=b5.N_PERM_SAMPLED_5, seed=b5.PERM_SEED_5)
        t5b = st.tree_5b(failures=[], primary=p5b, calibration={"cell": "CALIBRATED"})
        fires["5b"] += t5b["verdict"] == "SURVIVES"
        Ts["5b"].append(p5b["T"] if p5b["T"] is not None else 0.0)
        pe = st.primary_5b(cells, key="c_exp5_sim", n_sample=b5.N_PERM_SAMPLED_5, seed=b5.PERM_SEED_5)
        te = ss.tree_5(failures=[], primary={**pe, "n_cells": pe["n_cells"]},
                       modifier={"modifier": "MIXED"})
        fires["exp5"] += te["verdict"] == "NOT-MATCHED"
        Ts["exp5"].append(pe["T"] if pe["T"] is not None else 0.0)
        pn = st.primary_5b(cells, key="c_naive", n_sample=b5.N_PERM_SAMPLED_5, seed=b5.PERM_SEED_5)
        tn = st.tree_5b(failures=[], primary=pn, calibration={"cell": "CALIBRATED"})
        fires["naive"] += tn["verdict"] == "SURVIVES"
        Ts["naive"].append(pn["T"] if pn["T"] is not None else 0.0)
        sig.append(st.sigma_hat_5b(cells)["pooled"] or 0.0)
    m5, s5 = _summ(Ts["5b"]); me, se = _summ(Ts["exp5"]); mn, sn = _summ(Ts["naive"])
    return {"P_fire_5b": fires["5b"] / n_sim, "P_fire_exp5": fires["exp5"] / n_sim,
            "P_fire_naive": fires["naive"] / n_sim, "mean_T_5b": m5, "sd_T_5b": s5,
            "mean_T_exp5": me, "sd_T_exp5": se, "mean_T_naive": mn, "sd_T_naive": sn,
            "sigma_hat_sim_mean": float(np.mean(sig)), "n_sim": int(n_sim)}


def compute_5b(cells5_live: list, floors: dict, *, n_sim=N_SIM_5B, seed=SEED_5B) -> dict:
    """One rng, FIXED order: for σ_s ascending on the grid, the arms in
    ARMS_5B order; then the D grid (exp5's spread selection at σ_s =
    SIGMA_BELIEF_5B, offsets D×500 on the selected cells); then the
    fraction grid (the plugin offsets scaled, σ_s = SIGMA_BELIEF_5B)."""
    structure = structure_5b(cells5_live)
    rng = np.random.default_rng(seed)
    grid = []
    for sigma_s in b5b.SIGMA_GRID_5B:
        arms = {}
        for arm in ARMS_5B:
            if arm == "exp5_spread":
                arms[arm] = arm_5b(structure, floors, sigma_s=sigma_s, offset_scale=0.0, n_sim=n_sim,
                                   rng=rng, spread=True, spread_items=pw.OFFSET_ITEMS_5)
            else:
                arms[arm] = arm_5b(structure, floors, sigma_s=sigma_s, offset_scale=OFFSET_SCALE_5B[arm],
                                   n_sim=n_sim, rng=rng)
        grid.append({"sigma_s": sigma_s, "sigma_hat_sim_mean": arms["null"]["sigma_hat_sim_mean"],
                     "arms": arms})
    d_grid = []
    for D in D_GRID_5B:
        off = int(round(D * b5.N_ITEMS))
        r = arm_5b(structure, floors, sigma_s=b5b.SIGMA_BELIEF_5B, offset_scale=0.0, n_sim=n_sim, rng=rng,
                   spread=True, spread_items=off)
        d_grid.append({"D": D, "offset_items": off, "P_fire_5b": r["P_fire_5b"], "mean_T_5b": r["mean_T_5b"]})
    min_T = None
    for g in d_grid:
        if g["P_fire_5b"] >= POWER_BAR_5B:
            min_T = g["mean_T_5b"]
            break
    fraction_grid = []
    for frac in FRACTION_GRID_5B:
        r = arm_5b(structure, floors, sigma_s=b5b.SIGMA_BELIEF_5B, offset_scale=frac, n_sim=n_sim, rng=rng)
        fraction_grid.append({"fraction": frac, "P_fire_5b": r["P_fire_5b"], "mean_T_5b": r["mean_T_5b"]})
    i_belief = list(b5b.SIGMA_GRID_5B).index(b5b.SIGMA_BELIEF_5B)
    deciding = grid[i_belief]["arms"]["plugin"]["P_fire_5b"]
    nulls = [g["arms"]["null"] for g in grid]
    return {"n_sim": int(n_sim), "seed": int(seed), "sigma_l": SIGMA_L_5B, "drift": DRIFT_5B,
            "n_members": N_MEMBERS_5B, "grid": grid,
            "sigma_hat_axis": [g["sigma_hat_sim_mean"] for g in grid],
            "alpha_5b_axis": [a["P_fire_5b"] for a in nulls],
            "alpha_exp5_axis": [a["P_fire_exp5"] for a in nulls],
            "alpha_naive_axis": [a["P_fire_naive"] for a in nulls],
            "null_mean_5b_axis": [a["mean_T_5b"] for a in nulls],
            "null_mean_exp5_axis": [a["mean_T_exp5"] for a in nulls],
            "null_mean_naive_axis": [a["mean_T_naive"] for a in nulls],
            "null_sd_5b_axis": [a["sd_T_5b"] for a in nulls],
            "deciding": {"sigma_s": b5b.SIGMA_BELIEF_5B, "arm": "plugin", "P_fire_5b": deciding},
            "declaration": "POWERED" if deciding >= POWER_BAR_5B else "DECLARED UNDERPOWERED IN ADVANCE",
            "power_bar": POWER_BAR_5B, "d_grid": d_grid, "min_detectable_T_5b": min_T,
            "fraction_grid": fraction_grid, "n_live": len(structure),
            "live_rungs": sorted({s["rung"] for s in structure}),
            "structure_sha256": structure_sha256_5b(structure),
            "exp5_closed_tag": b5b.EXP5_CLOSED_TAG_5B, "prereg_tag": b5b.PREREG_TAG_5B,
            "assumptions": list(ASSUMPTIONS_5B)}


def load_cells5_live_5b(exp5_root, *, verdict_sha=None) -> list:
    """Experiment 5's committed verdict.json (sha-pinned unless
    `verdict_sha=False`) → its live cells with a defined P."""
    p = Path(exp5_root) / "results" / "verdict.json"
    raw = p.read_bytes()
    if verdict_sha is not False:
        want = b5b.EXP5_VERDICT_SHA256_5B if verdict_sha is None else verdict_sha
        got = hashlib.sha256(raw).hexdigest()
        if got != want:
            raise RuntimeError(f"{p} hashes to {got[:12]}, pinned {str(want)[:12]}")
    v = json.loads(raw)
    return [c for c in v["cells"] if c.get("live") and c.get("defined_P")]


def main(root=EXP5B, *, exp5_root=None, n_sim=None, seed=SEED_5B, tag_exists=None, blob_sha=None,
         verdict_sha=None) -> dict:
    """ONCE, pre-tag: the exp5-closed binding, the frozen modules and the
    import surface asserted first; refuses if the record exists."""
    exp5_root = b5b.EXP5 if exp5_root is None else Path(exp5_root)
    closed = b5b.require_exp5_closed_5b(tag_exists=tag_exists, blob_sha=blob_sha, verdict_sha=verdict_sha,
                                        exp5_root=exp5_root)
    b5b.check_frozen_5b()
    b5b.check_imports_5b()
    out = b5b.power_path_5b(Path(root))
    if out.is_file():
        raise RuntimeError(f"power_5b.main: {out} exists — the power record is written ONCE")
    n_sim = N_SIM_5B if n_sim is None else n_sim
    cells5 = load_cells5_live_5b(exp5_root, verdict_sha=verdict_sha)
    rec = compute_5b(cells5, b5.load_floors_5(), n_sim=n_sim, seed=seed)
    rec["exp5_verdict_sha256"] = closed["verdict_sha256"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1, sort_keys=True, allow_nan=False))
    return rec


if __name__ == "__main__":
    rec = main()
    print(f"declaration: {rec['declaration']} (P {rec['deciding']['P_fire_5b']:.3f} at the plugin arm, "
          f"sigma_s {rec['deciding']['sigma_s']}); n_live {rec['n_live']} over {len(rec['live_rungs'])} rungs")
    for g in rec["grid"]:
        a = g["arms"]
        print(f"  sigma_s {g['sigma_s']:>2} (sigma_hat_sim {g['sigma_hat_sim_mean']:.2f}): "
              f"alpha 5b {a['null']['P_fire_5b']:.3f} exp5 {a['null']['P_fire_exp5']:.3f} "
              f"naive {a['null']['P_fire_naive']:.3f} | null T 5b {a['null']['mean_T_5b']:+.4f} "
              f"exp5 {a['null']['mean_T_exp5']:+.4f} naive {a['null']['mean_T_naive']:+.4f} | "
              f"P(plugin) {a['plugin']['P_fire_5b']:.3f} P(shrunk) {a['shrunk']['P_fire_5b']:.3f} "
              f"P(exp5_spread) {a['exp5_spread']['P_fire_5b']:.3f}")
    print(f"  min detectable T_5b {rec['min_detectable_T_5b']}; fractions "
          + ", ".join(f"{f['fraction']}: {f['P_fire_5b']:.3f}" for f in rec["fraction_grid"]))
