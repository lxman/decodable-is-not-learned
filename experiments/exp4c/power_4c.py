# experiments/exp4c/power_4c.py
"""Experiment 4c's power record (design `experiment-4c-design.md` §4;
plan Task 5): because the primary is a rank (q, null mean exactly 1/2)
against an exact family-block sign flip, THE NULL DISTRIBUTION OF THE
DECISION DOES NOT DEPEND ON THE DATA — the cell structure of §3.2
(which trajectory, which rung, which family, which type, how many flat
comparators) fixes it completely. Power is therefore computed here,
data-free, through the verdict's own primary code (`rank_4c.q_cell_4c`,
`rank_4c.block_flip_4c`), before the tag and before any model is
loaded — the declaration is part of the preregistration, not a
retrospective claim.

`cell_structure_4c()` reproduces the 26-cell structure from the pins
alone (`battery_4c.RUNG_SET_PIN_4C` / `CLEAR_INDEX_PIN_4C` /
`RUNG_TYPE_4C` / `FAMILY_OF`) — no series, no checkpoint, no alignment
value anywhere in this module. `simulate_cells_4c` draws one Gaussian
battery per simulated cell under a chosen alternative (`mu_arith`,
`mu_nonarith`) and correlation `rho` between the two runs' shared
tasks, and reads it through `q_cell_4c` exactly as the real analyzer
reads a real cell — the ONLY difference between a simulated draw and
a real one is where the numbers came from.

The two decision bars (P(p+ < .01), P(p+ < .05)) are hardcoded as
literals in `_simulate_arm_rho_4c` — NOT read from `rank_4c.ALPHA_4C`/
`MARGINAL_4C` — so that a test which monkeypatches those module
globals (`test_full_shape_4c.test_marginal_terminal_is_reachable_by_
the_tree`) cannot change what a re-derived power record computes out
from under a byte-reproduction check; the two constants happen to
share the same values as the program's bars, verified by
`test_power_4c.py`.

Pure numpy/scipy (`scipy.stats.norm.ppf` for delta) plus `rank_4c`
(itself pure numpy — no torch, no network, no model contact anywhere
downstream). `experiments.exp4._threads_4` is imported first, before
numpy, for bit-reproducibility across processes (Exp 4's Minor 7,
carried by every exp4c module).

Usage: `python -m experiments.exp4c.power_4c` (writes
`results/power_4c.json` ONCE, refusing a second write)."""
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

# The BLAS thread pool is sized when numpy is first imported, and a
# multi-threaded reduction is not bit-reproducible across processes —
# pinned before numpy and before any `experiments.*` import that pulls
# numpy in transitively (Exp 4's Minor 7; `rank_4c.py`'s own rule).
from experiments.exp4 import _threads_4  # noqa: E402,F401

import numpy as np  # noqa: E402
from scipy.stats import norm  # noqa: E402

from experiments.exp4c import battery_4c as bc  # noqa: E402
from experiments.exp4c import rank_4c as rk  # noqa: E402

# --------------------------------------------------------------- constants

N_SIM_4C = 4000
SEED_4C = 0
RHOS_4C = (0.0, 0.5)          # ascending; the LAST value is the deciding rho (design §4/§3.6)
POWER_BAR_4C = 0.75

# (mu_arith, mu_nonarith) per arm — the design-stage table's own
# alternatives (§4) plus the discovery set's own shape (§2).
ARMS_4C = {
    "null": (0.5, 0.5),
    "uniform_60": (0.60, 0.60),
    "uniform_65": (0.65, 0.65),
    "uniform_70": (0.70, 0.70),
    "discovery_shape": (0.51, 0.76),
}

# The min-detectable-uniform-lead grid (design §4's own table's rows
# plus two extra points bracketing it): .60/.65/.70 are already
# computed as part of ARMS_4C above and are REUSED, never re-simulated
# — only .55/.75/.80 spend fresh draws off the same rng stream.
_MIN_DETECTABLE_GRID_4C = (0.55, 0.60, 0.65, 0.70, 0.75, 0.80)
_MIN_DETECTABLE_RHO_4C = 0.5

# Hardcoded, not `rk.ALPHA_4C`/`rk.MARGINAL_4C` — see module docstring.
_P01_BAR_4C = 0.01
_P05_BAR_4C = 0.05

BLIND_REGION_4C = "any type-bound effect, and any uniform lead under the min-detectable value"

ASSUMPTIONS_4C = (
    "B-3: independent comparator pools per simulated cell (the flat pool is n_flat i.i.d. "
    "N(0,1) draws per cell, the first n_flat_arith of them the arithmetic comparators); the "
    "placebo arm (design §3.6), not this power record, measures the real cross-run dependence "
    "among the flat tasks."
)


# ------------------------------------------------------------ cell structure

def cell_structure_4c() -> list:
    """The 26-cell structure (design §3.2/§4), reproduced from the pins
    ALONE — no series, no real alignment value. One entry per
    (trajectory, rising rung): `traj`, `rung`, `family`, `type`,
    `n_flat` (the run's whole flat-pool size), `n_flat_arith` (the
    arithmetic-only subset). `RUNG_SET_PIN_4C[traj]["R"]` and
    `CLEAR_INDEX_PIN_4C[traj]`'s keys are asserted equal (the same
    rising-rung set, two pins) before either is trusted."""
    out = []
    for traj in bc.TRAJECTORIES_4C:
        pin = bc.RUNG_SET_PIN_4C[traj]
        R = tuple(pin["R"])
        ci_keys = tuple(sorted(bc.CLEAR_INDEX_PIN_4C[traj]))
        if tuple(sorted(R)) != ci_keys:
            raise ValueError(f"cell_structure_4c: {traj}: RUNG_SET_PIN_4C['R'] "
                             f"{sorted(R)} != CLEAR_INDEX_PIN_4C keys {list(ci_keys)}")
        flat = tuple(pin["flat"])
        flat_arith = tuple(r for r in flat if bc.RUNG_TYPE_4C[r] == "arithmetic")
        for r in sorted(R):
            out.append({
                "traj": traj, "rung": r, "family": bc.FAMILY_OF[r], "type": bc.RUNG_TYPE_4C[r],
                "n_flat": len(flat), "n_flat_arith": len(flat_arith),
            })
    return out


def structure_sha256_4c(structure) -> str:
    return hashlib.sha256(json.dumps(structure, sort_keys=True).encode()).hexdigest()


# ------------------------------------------------------------------ effect

def delta_of_mu_4c(mu: float) -> float:
    """The Gaussian mean shift placing P(a random flat draw < a random
    rising draw) = `mu`, for two unit-variance normals: `sqrt(2) *
    Phi^-1(mu)`. `delta_of_mu_4c(0.5) == 0.0` exactly (`norm.ppf(0.5)`
    is exactly 0.0)."""
    return float(np.sqrt(2.0) * norm.ppf(mu))


# ---------------------------------------------------------------- simulation

def simulate_cells_4c(structure, mu_arith, mu_nonarith, *, rho, rng) -> list:
    """One simulated battery: per DISTINCT rung name (shared across
    both trajectories when a rung's R-membership recurs on both, e.g.
    `antonym`) a latent `z_task ~ N(0,1)`; per cell `z = sqrt(rho) *
    z_task[rung] + sqrt(1-rho) * eps` (`eps` fresh per cell); `g_r = z +
    delta_of_mu_4c(mu_type)`; the flat pool `g_f ~ N(0,1)` i.i.d. of
    size `n_flat`, the first `n_flat_arith` of them the arithmetic
    comparators (B-3). Each output cell carries exactly the fields
    `rank_4c.block_flip_4c`/`U_4c` read: `family`, `rung`, `type`, `q`,
    `q_arith` (`None` off a non-arithmetic cell or an empty arithmetic
    pool)."""
    rungs = sorted({c["rung"] for c in structure})
    z_task = {r: float(rng.standard_normal()) for r in rungs}
    sqrt_rho = float(np.sqrt(rho))
    sqrt_1mrho = float(np.sqrt(1.0 - rho))
    out = []
    for c in structure:
        eps = float(rng.standard_normal())
        z = sqrt_rho * z_task[c["rung"]] + sqrt_1mrho * eps
        mu = mu_arith if c["type"] == "arithmetic" else mu_nonarith
        g_r = z + delta_of_mu_4c(mu)
        g_flat = rng.standard_normal(c["n_flat"])
        q, _ties = rk.q_cell_4c(g_r, g_flat)
        q_arith = None
        if c["type"] == "arithmetic" and c["n_flat_arith"] > 0:
            q_arith, _ = rk.q_cell_4c(g_r, g_flat[:c["n_flat_arith"]])
        out.append({"traj": c["traj"], "rung": c["rung"], "family": c["family"],
                    "type": c["type"], "q": q, "q_arith": q_arith})
    return out


def _simulate_arm_rho_4c(structure, mu_arith, mu_nonarith, rho, n_sim, rng) -> dict:
    """`n_sim` draws at one (arm, rho): per draw, `fl` = the family
    block flip over every cell's `q`, `fa` = the (default block, i.e.
    family) flip over the arithmetic-only cells' `q_arith` — design
    §4's own reading of §3.5's arithmetic stratum. Returns the rate
    each bar fires, `mean_U`/`sd_U` of the pooled mean."""
    n01 = n05 = narith05 = 0
    u_sum = 0.0
    u2_sum = 0.0
    for _ in range(n_sim):
        cells = simulate_cells_4c(structure, mu_arith, mu_nonarith, rho=rho, rng=rng)
        fl = rk.block_flip_4c(cells, key="q", block="family")
        arith_cells = [c for c in cells if c["q_arith"] is not None]
        fa = rk.block_flip_4c(arith_cells, key="q_arith")
        U = float(np.mean([c["q"] for c in cells]))
        n01 += int(fl["p_plus"] < _P01_BAR_4C)
        n05 += int(fl["p_plus"] < _P05_BAR_4C)
        narith05 += int(fa["p_plus"] < _P05_BAR_4C)
        u_sum += U
        u2_sum += U * U
    mean_U = u_sum / n_sim
    var_U = max(u2_sum / n_sim - mean_U * mean_U, 0.0)
    return {"rho": float(rho), "P_01": n01 / n_sim, "P_05": n05 / n_sim,
            "mean_U": float(mean_U), "sd_U": float(np.sqrt(var_U)), "P_arith_05": narith05 / n_sim}


def _interpolate_min_detectable_4c(grid_points, bar):
    """The smallest mu at which the linearly-interpolated P_01 curve
    crosses `bar`, over `grid_points` sorted ascending by mu. `None`
    when no grid point clears the bar."""
    pts = sorted(grid_points, key=lambda t: t[0])
    for i, (mu, p) in enumerate(pts):
        if p >= bar:
            if i == 0:
                return float(mu)
            mu0, p0 = pts[i - 1]
            mu1, p1 = pts[i]
            if p1 == p0:
                return float(mu1)
            frac = (bar - p0) / (p1 - p0)
            return float(mu0 + frac * (mu1 - mu0))
    return None


# -------------------------------------------------------------------- compute

def compute(structure, *, n_sim=N_SIM_4C, seed=SEED_4C, rhos=RHOS_4C, arms=ARMS_4C) -> dict:
    """One `np.random.default_rng(seed)` stream, consumed in a FIXED
    order: arms in `arms`' own (insertion) order, rho ascending within
    each arm, `n_sim` draws per (arm, rho); then the min-detectable-
    uniform-lead grid's un-reused points (design §4), ascending mu, at
    `rho = 0.5`. Deterministic in (`structure`, `n_sim`, `seed`,
    `rhos`, `arms`) alone — `test_power_4c.py`'s byte-reproducibility
    test calls this twice and compares the two dicts."""
    rng = np.random.default_rng(seed)
    arms_out = {}
    for arm_name, (mu_arith, mu_nonarith) in arms.items():
        by_rho = [_simulate_arm_rho_4c(structure, mu_arith, mu_nonarith, rho, n_sim, rng)
                  for rho in rhos]
        last = by_rho[-1]
        arms_out[arm_name] = {
            "mu_arith": float(mu_arith), "mu_nonarith": float(mu_nonarith), "by_rho": by_rho,
            "P_01": last["P_01"], "P_05": last["P_05"], "mean_U": last["mean_U"],
            "sd_U": last["sd_U"], "P_arith_05": last["P_arith_05"],
        }

    null_by_rho = arms_out["null"]["by_rho"] if "null" in arms_out else []
    realized_alpha_01 = [r["P_01"] for r in null_by_rho]
    realized_alpha_05 = [r["P_05"] for r in null_by_rho]

    # min-detectable uniform lead: reuse the uniform_XX arms already
    # computed above (matched on mu_arith == mu_nonarith), spend fresh
    # draws off the SAME rng only for the grid points not already an
    # arm — ascending mu order, so the stream is a deterministic
    # function of (structure, n_sim, seed, rhos, arms) alone.
    uniform_by_mu = {float(ma): arms_out[name]["P_01"]
                     for name, (ma, mn) in arms.items() if ma == mn}
    grid_points = []
    for mu in _MIN_DETECTABLE_GRID_4C:
        if float(mu) in uniform_by_mu:
            p01 = uniform_by_mu[float(mu)]
        else:
            rec = _simulate_arm_rho_4c(structure, mu, mu, _MIN_DETECTABLE_RHO_4C, n_sim, rng)
            p01 = rec["P_01"]
        grid_points.append((float(mu), float(p01)))
    min_detectable = _interpolate_min_detectable_4c(grid_points, POWER_BAR_4C)

    disc = arms_out.get("discovery_shape")
    p01_discovery = disc["P_01"] if disc is not None else None
    declaration = ("POWERED" if (p01_discovery is not None and p01_discovery >= POWER_BAR_4C)
                  else "DECLARED UNDERPOWERED IN ADVANCE")

    n_families = len({c["family"] for c in structure})
    return {
        "n_sim": int(n_sim), "seed": int(seed), "rhos": [float(r) for r in rhos],
        "arms": arms_out,
        "realized_alpha_01": realized_alpha_01, "realized_alpha_05": realized_alpha_05,
        "min_detectable_uniform_lead": min_detectable,
        "min_detectable_grid": [{"mu": mu, "P_01": p} for mu, p in grid_points],
        "declaration": declaration,
        "blind_region": BLIND_REGION_4C,
        "assumptions": ASSUMPTIONS_4C,
        "structure": structure,
        "cells_sha256": structure_sha256_4c(structure),
        "n_cells": len(structure), "n_families": int(n_families),
        "prereg_tag": bc.PREREG_TAG_4C,
    }


def main(root=EXP4C, *, n_sim=N_SIM_4C, seed=SEED_4C) -> dict:
    """Writes `<root>/results/power_4c.json` ONCE — refuses if it
    already exists (design §3.9: the power record precedes the tag,
    committed before any model contact)."""
    root = Path(root)
    out_path = root / "results" / "power_4c.json"
    if out_path.is_file():
        raise RuntimeError(f"power_4c.main: {out_path} already exists — the power record is "
                           f"written ONCE")
    structure = cell_structure_4c()
    rec = compute(structure, n_sim=n_sim, seed=seed)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1, sort_keys=True, allow_nan=False))
    return rec


if __name__ == "__main__":
    rec = main()
    print(f"declaration: {rec['declaration']}")
    disc = rec["arms"]["discovery_shape"]
    print(f"  discovery_shape: P_01(rho=.5)={disc['P_01']:.4f} P_05(rho=.5)={disc['P_05']:.4f} "
         f"by_rho={[(r['rho'], round(r['P_01'], 4), round(r['P_05'], 4)) for r in disc['by_rho']]}")
    for name in ("null", "uniform_60", "uniform_65", "uniform_70"):
        arm = rec["arms"][name]
        print(f"  {name}: P_01(rho=.5)={arm['P_01']:.4f} P_05(rho=.5)={arm['P_05']:.4f} "
             f"by_rho={[(r['rho'], round(r['P_01'], 4), round(r['P_05'], 4)) for r in arm['by_rho']]}")
    print(f"realized_alpha_01={rec['realized_alpha_01']} realized_alpha_05={rec['realized_alpha_05']}")
    print(f"min_detectable_uniform_lead={rec['min_detectable_uniform_lead']}")
    print(f"grid={rec['min_detectable_grid']}")
    print(f"n_cells={rec['n_cells']} n_families={rec['n_families']} cells_sha256={rec['cells_sha256']}")
