"""Exp 5's power record (design §4, dial k; B-5), written ONCE at the
targets stage from the SEALED finals, through the verdict's own code
(`stats_5.cell_5` / `primary_5` / `tree_5`).

The simulated live set = the (pair, rung) cells whose SMALL final clears
2d's bar (the real finals); the large side's true count under H0 equals
f (Prediction 3), under H1 f + OFFSET_ITEMS_5 on the selected cells;
each read = clip(round(true + N(0, σ))) with σ = SIGMA_READ_ITEMS_5 ×
factor; each placebo side carries an extra drift N(0, DRIFT_SD_ITEMS_5)
shared by its two reads; f itself is fixed (a committed read). Cells
live only through the large side are NOT simulated (disclosed: the
realized live set is printed beside this one by the analyzer). Arms:
null / spread (each live cell offset w.p. Q_5) / concentrated (every
live cell on an option-type rung offset), at noise factors 1 and ½;
the deciding arm = spread × 1 (B-5). The D grid for the minimum
detectable T runs on spread × 1."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP5 = Path(__file__).resolve().parent
if str(EXP5.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP5.parent.parent))

from experiments.exp5 import _threads_5  # noqa: E402,F401
import numpy as np  # noqa: E402

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import stats_5 as ss  # noqa: E402

SIGMA_READ_ITEMS_5 = 17.0 * float(np.sqrt(np.pi / 2)) / float(np.sqrt(2))   # 15.07
DRIFT_SD_ITEMS_5 = 4.0
NOISE_FACTORS_5 = (1.0, 0.5)
OFFSET_ITEMS_5 = 25
Q_5 = 0.5
N_SIM_5 = 1000
SEED_5 = 0
POWER_BAR_5 = 0.75
D_GRID_5 = (0.01, 0.02, 0.03, 0.04, 0.05, 0.06)
DECIDING_ARM_5 = {"arm": "spread", "noise_factor": 1.0, "D": 0.05, "q": 0.5}
ASSUMPTIONS_5 = (
    "the simulated live set is the cells whose small final clears the bar; cells live only through "
    "the large side are not simulated",
    "per-read noise is Gaussian on the count, sd 17.0·sqrt(pi/2)/sqrt(2) items at factor 1 (the committed "
    "pooled late |Δ| at 10k spacing read as a difference of two reads), halved at factor 1/2",
    "each placebo side carries one drift term N(0, 4 items) shared by its two reads",
    "f is fixed; every window is full (no edge cells)",
    "the offset is one-directional (+25 items) on the selected cells",
)


def live_structure_5(finals_counts: dict, floors: dict) -> list:
    out = []
    for small, large in b5.PAIRS_5:
        for rung in b5.RUNGS:
            f = int(finals_counts[small][rung])
            if b5.clears_5(f, floors[rung]):
                out.append({"small": small, "large": large, "rung": rung, "f": f,
                            "family": b5.FAMILY_OF[rung], "type": b5.RUNG_TYPE_5[rung]})
    return out


def _read(true, sigma, rng):
    return int(min(b5.N_ITEMS, max(0, round(true + rng.normal(0.0, sigma)))))


def simulate_battery_5(structure, floors, *, offset_cells, sigma, drift, rng,
                       offset_items=OFFSET_ITEMS_5) -> list:
    cells = []
    for i, s in enumerate(structure):
        true = s["f"] + (offset_items if i in offset_cells else 0)
        lo, hi = _read(true, sigma, rng), _read(true, sigma, rng)
        d_m, d_p = rng.normal(0.0, drift), rng.normal(0.0, drift)
        bm = [_read(true + d_m, sigma, rng), _read(true + d_m, sigma, rng)]
        bp = [_read(true + d_p, sigma, rng), _read(true + d_p, sigma, rng)]
        reads = {"lo": lo, "hi": hi, "a": (lo + hi) / 2, "b_minus": sum(bm) / 2, "b_plus": sum(bp) / 2,
                 "raw": {"lo": lo, "hi": hi, "b_minus": bm, "b_plus": bp}}
        c = ss.cell_5(f=s["f"], reads=reads, floor=floors[s["rung"]])
        c.update({k: s[k] for k in ("small", "large", "rung", "family", "type")})
        c.update({"bracket": [0, 0], "b_minus_steps": [], "b_plus_steps": [],
                  "residual_lo": 0.0, "residual_hi": 0.0})
        cells.append(c)
    return cells


def _arm(structure, floors, *, select, sigma, n_sim, rng, offset_items=OFFSET_ITEMS_5) -> dict:
    fires, Ts, ps = 0, [], []
    for _ in range(n_sim):
        offset_cells = select(rng)
        cells = simulate_battery_5(structure, floors, offset_cells=offset_cells, sigma=sigma,
                                   drift=DRIFT_SD_ITEMS_5, rng=rng, offset_items=offset_items)
        prim = ss.primary_5(cells, n_sample=b5.N_PERM_SAMPLED_5, seed=b5.PERM_SEED_5)
        mod = ss.modifier_5(cells)
        tree = ss.tree_5(failures=[], primary=prim, modifier=mod)
        fires += tree["verdict"] == "NOT-MATCHED"
        Ts.append(prim["T"] if prim["T"] is not None else 0.0)
        ps.append(prim["rung_block"]["p"])
    return {"P_fire": fires / n_sim, "mean_T": float(np.mean(Ts)), "sd_T": float(np.std(Ts)),
            "mean_p": float(np.mean(ps)), "n_sim": int(n_sim)}


def compute(finals_counts: dict, floors: dict, *, n_sim=N_SIM_5, seed=SEED_5) -> dict:
    """One rng, consumed in a FIXED order: arms (null, spread, concentrated)
    × noise factors ascending-by-name (1.0 then 0.5), then the D grid."""
    structure = live_structure_5(finals_counts, floors)
    n = len(structure)
    option_idx = {i for i, s in enumerate(structure) if s["type"] == "option"}
    rng = np.random.default_rng(seed)
    selects = {"null": lambda r: set(),
               "spread": lambda r: {i for i in range(n) if r.random() < Q_5},
               "concentrated": lambda r: set(option_idx)}
    arms = {}
    for name in ("null", "spread", "concentrated"):
        arms[name] = {}
        for factor in NOISE_FACTORS_5:
            arms[name][str(factor)] = _arm(structure, floors, select=selects[name],
                                           sigma=SIGMA_READ_ITEMS_5 * factor, n_sim=n_sim, rng=rng)
    grid = []
    for D in D_GRID_5:
        off = int(round(D * b5.N_ITEMS))
        r = _arm(structure, floors, select=selects["spread"], sigma=SIGMA_READ_ITEMS_5,
                 n_sim=n_sim, rng=rng, offset_items=off)
        grid.append({"D": D, "offset_items": off, "P_fire": r["P_fire"], "mean_T": r["mean_T"]})
    min_T = None
    for g in grid:
        if g["P_fire"] >= POWER_BAR_5:
            min_T = g["mean_T"]
            break
    deciding = arms["spread"]["1.0"]["P_fire"]
    return {"n_sim": int(n_sim), "seed": int(seed), "sigma_read_items": SIGMA_READ_ITEMS_5,
            "noise_factors": list(NOISE_FACTORS_5), "drift_sd_items": DRIFT_SD_ITEMS_5,
            "offset_items": OFFSET_ITEMS_5, "q": Q_5, "arms": arms,
            "realized_alpha": {k: v["P_fire"] for k, v in arms["null"].items()},
            "null_T": {k: {"mean": v["mean_T"], "sd": v["sd_T"]} for k, v in arms["null"].items()},
            "d_grid": grid, "min_detectable_T": min_T, "deciding_arm": dict(DECIDING_ARM_5),
            "P_deciding": deciding,
            "declaration": "POWERED" if deciding >= POWER_BAR_5 else "DECLARED UNDERPOWERED IN ADVANCE",
            "power_bar": POWER_BAR_5, "n_live_simulated": n,
            "live_rungs_simulated": sorted({s["rung"] for s in structure}),
            "structure": structure, "assumptions": list(ASSUMPTIONS_5),
            "structure_sha256": hashlib.sha256(json.dumps(structure, sort_keys=True).encode()).hexdigest(),
            "prereg_tag": b5.PREREG_TAG_5}


def load_finals_counts_5(root) -> dict:
    out = {}
    for size in b5.SIZES_5:
        if not b5.unit_complete_5(root, size, b5.FINAL_STEP_5):
            raise RuntimeError(f"power_5: the {size} final is not complete under {root}")
        out[size] = {r: int(json.loads(b5.rung_record_path_5(root, size, b5.FINAL_STEP_5, r).read_text())["correct"])
                     for r in b5.RUNGS}
    return out


def finals_sha256_5(root) -> str:
    h = hashlib.sha256()
    for size in b5.SIZES_5:
        h.update(bg.sha256_file(b5.unit_record_path_5(root, size, b5.FINAL_STEP_5)).encode())
    return h.hexdigest()


def main(root=EXP5, *, n_sim=None, seed=SEED_5) -> dict:
    root = Path(root)
    out = b5.power_path_5(root)
    if out.is_file():
        raise RuntimeError(f"power_5.main: {out} exists — the power record is written ONCE")
    n_sim = N_SIM_5 if n_sim is None else n_sim
    rec = compute(load_finals_counts_5(root), b5.load_floors_5(), n_sim=n_sim, seed=seed)
    rec["finals_sha256"] = finals_sha256_5(root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1, sort_keys=True, allow_nan=False))
    return rec


if __name__ == "__main__":
    rec = main()
    print(f"declaration: {rec['declaration']} (P_deciding {rec['P_deciding']:.3f} at "
          f"{rec['deciding_arm']}); n_live_simulated {rec['n_live_simulated']} over "
          f"{len(rec['live_rungs_simulated'])} rungs; realized α {rec['realized_alpha']}; "
          f"null T {rec['null_T']}; min detectable T {rec['min_detectable_T']}")
    for arm, by in rec["arms"].items():
        print(f"  {arm}: " + ", ".join(f"×{k}: P {v['P_fire']:.3f} T {v['mean_T']:+.4f}±{v['sd_T']:.4f}"
                                        for k, v in by.items()))
