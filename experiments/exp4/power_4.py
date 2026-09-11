# experiments/exp4/power_4.py
"""Experiment 4's power record (design §4; Task 5 brief + resolutions),
written ONCE at the reference stage, before the projection, through the
verdict's own code: for each arm phi* in {0.0, 0.25, 0.5}, N_SIM
simulated alignment tables are built from the REAL measured endpoint
excess/SE/trend of every eligible cell -- per eligible (traj, rung)
cell the excess rises as E_r * F(i), F(i) = logistic((i - m) / 0.75),
m solved by bisection so that F(c_r - 1) / F(G - 1) = phi* (phi* = 0:
m = c_r + 3, the bisection's own asymptote); per-rung-per-step Gaussian
noise at the rung's own measured SE (se_r on rising rungs, se_at_end on
flat rungs); the flat pool's trend interpolated log-linearly in step
between the trajectory's measured t_1/t_end trend values. Each
simulated table is fed through `analyze_4.trend_4` -> `excess_4` ->
the SAME eligibility rule (rule (ii) only -- t_clear_index is fixed;
a candidate cell's endpoint excess can still fail to clear
`SE_MULTIPLE_4 * se` in a given draw, dropping it from that draw's
cells, printed as `mean_eligible_cells`) -> `cells_4` -> `primary_4`
(n_boot=200) -> `verdict_tree_4` -- the exact same functions the real
analyzer calls, never a re-implementation.

No torch, no model contact: `main(root)` reads the committed
`eligibility_4.json` (written by the reference stage) and the real
outcome/rung-set tables (`battery_4.load_outcome_4` /
`battery_4.rung_sets_4`, themselves reading only committed exp2g/2i/
2m/2n bytes), then calls `compute()`.

Usage: python -m experiments.exp4.power_4   (writes power_4.json ONCE)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.special import expit
from scipy.stats import norm

EXP4 = Path(__file__).resolve().parent
EXPERIMENTS = EXP4.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402

TREND_SHAPE_NOTE_4 = (
    "the flat pool's trend as measured at the endpoint and interpolated log-linearly in tokens "
    "between t_1 and t_end (the simulation's trend shape is disclosed as an assumption; the "
    "analyzer's reading does not depend on it)."
)

ELIGIBILITY_BAR_NULL_CROSSING_NOTE_4 = (
    "the item bootstrap does not resample neighbour sets, so null cells cross the one-sided 2-SE "
    "bar above the nominal 2.3% (2-12% in the worlds) -- a disclosure carried from Task 4's "
    "review, not re-derived here."
)

MIN_DETECTABLE_T_NOTE_4 = (
    "min_detectable_T is the normal-approximation T at which the one-sided sign-flip test's p "
    "reaches ALPHA_4 (.01) with probability .75, given null_sd_T as the statistic's SD: "
    "null_sd_T * (z_{1-ALPHA_4} + z_{.75})."
)

N_BOOT_POWER_4 = 200
LOGISTIC_WIDTH_4 = 0.75


def _logistic(x):
    return expit(x)   # numerically stable sigmoid (no overflow on large |x|)


def _solve_m(c_r: int, G: int, phi_target: float, *, width=LOGISTIC_WIDTH_4) -> float:
    """`m` such that `F(c_r - 1) / F(G - 1) == phi_target`, `F(i) =
    logistic((i - m) / width)`. `phi_target == 0.0` is the bisection's
    own asymptote (the ratio -> a positive floor > 0 as m -> +inf, never
    exactly 0), so it is the literal `m = c_r + 3` the design fixes
    directly rather than bisected."""
    if phi_target == 0.0:
        return float(c_r) + 3.0

    def ratio(m):
        num, den = _logistic((c_r - 1 - m) / width), _logistic((G - 1 - m) / width)
        return 0.0 if den == 0.0 else num / den

    lo, hi = -1e4, 1e4
    g_lo, g_hi = ratio(lo) - phi_target, ratio(hi) - phi_target
    if g_lo == 0.0:
        return lo
    if g_hi == 0.0:
        return hi
    if (g_lo > 0) == (g_hi > 0):
        # No sign change in the bracket (an extreme phi_target against
        # a narrow grid) -- fall back to whichever bound is closer.
        return lo if abs(g_lo) < abs(g_hi) else hi
    for _ in range(200):
        mid = (lo + hi) / 2.0
        g_mid = ratio(mid) - phi_target
        if g_mid == 0.0:
            return mid
        if (g_lo > 0) == (g_mid > 0):
            lo, g_lo = mid, g_mid
        else:
            hi, g_hi = mid, g_mid
    return (lo + hi) / 2.0


def _candidates(elig: dict) -> list:
    out = []
    for traj, block in elig.items():
        for rung, e in (block.get("R") or {}).items():
            if e.get("eligible"):
                out.append((traj, rung))
    return sorted(out)


def compute(elig: dict, rung_sets: dict, grids: dict, *, n_sim: int = 1000, seed: int = 0,
           phis: tuple = (0.0, 0.25, 0.5)) -> dict:
    candidates = _candidates(elig)
    if not candidates:
        raise ValueError("power_4.compute: no eligible cells in the eligibility table")
    rungs = sorted({r for _, r in candidates})
    n_rungs = len(rungs)
    trajs = sorted({t for t, _ in candidates})

    cell_info = {}
    for traj, rung in candidates:
        e = elig[traj]["R"][rung]
        steps = list(grids[traj])
        G = len(steps)
        c_r = int(e["t_clear_index"])
        cell_info[(traj, rung)] = dict(G=G, c_r=c_r, E_r=float(e["x_end"]), se_r=float(e["se"]),
                                       t_clear=e["t_clear"])

    traj_info = {}
    for traj in trajs:
        flat = list(rung_sets[traj]["flat"])
        flat_se = {r: float(elig[traj]["flat"][r]["se_at_end"]) for r in flat}
        steps = list(grids[traj])
        traj_info[traj] = dict(flat=flat, flat_se=flat_se, steps=steps,
                               trend_t1=float(elig[traj]["trend_t1"]),
                               trend_end=float(elig[traj]["trend_end"]))

    trend_arr = {}
    for traj, ti in traj_info.items():
        steps_arr = np.asarray(ti["steps"], dtype=np.float64)
        s0, s1 = steps_arr[0], steps_arr[-1]
        if s1 == s0:
            frac = np.zeros_like(steps_arr)
        else:
            frac = (np.log(steps_arr) - np.log(s0)) / (np.log(s1) - np.log(s0))
        trend_arr[traj] = ti["trend_t1"] + (ti["trend_end"] - ti["trend_t1"]) * frac

    m_by_phi = {phi: {key: _solve_m(info["c_r"], info["G"], phi) for key, info in cell_info.items()}
               for phi in phis}

    rng = np.random.default_rng(seed)

    arms = {}
    for phi in phis:
        world_counts = {w: 0 for w in an.WORLDS_4}
        Ts, elig_counts = [], []
        for draw in range(n_sim):
            series_by_traj = {}
            for traj, ti in traj_info.items():
                steps = ti["steps"]
                G = len(steps)
                a = {}
                for r in ti["flat"]:
                    noise = rng.normal(0.0, ti["flat_se"][r], size=G)
                    a[r] = (trend_arr[traj] + noise).tolist()
                series_by_traj[traj] = {"steps": steps, "a": a}
            for (traj, rung), info in cell_info.items():
                G = info["G"]
                m = m_by_phi[phi][(traj, rung)]
                idx = np.arange(G, dtype=np.float64)
                F = _logistic((idx - m) / LOGISTIC_WIDTH_4)
                noise = rng.normal(0.0, info["se_r"], size=G)
                series = trend_arr[traj] + info["E_r"] * F + noise
                series_by_traj[traj]["a"][rung] = series.tolist()

            eligibility_sim = {}
            for traj in trajs:
                rs = rung_sets[traj]
                trend = an.trend_4(series_by_traj[traj]["a"], rs["flat"], series_by_traj[traj]["steps"])
                excess = an.excess_4(series_by_traj[traj]["a"], trend, series_by_traj[traj]["steps"])
                Rdict = {}
                for (t2, rung), info in cell_info.items():
                    if t2 != traj:
                        continue
                    x_end_sim = excess[rung][-1]
                    ok = x_end_sim >= an.SE_MULTIPLE_4 * info["se_r"]
                    Rdict[rung] = {"eligible": bool(ok), "t_clear": info["t_clear"],
                                  "t_clear_index": info["c_r"]}
                eligibility_sim[traj] = {"R": Rdict}

            rs_subset = {traj: rung_sets[traj] for traj in trajs}
            cells = an.cells_4(series_by_traj, rs_subset, eligibility_sim)
            n_cells = len(cells)
            elig_counts.append(n_cells)
            if n_cells == 0:
                tree = an.verdict_tree_4([], 0, 0, {})
                T = None
            else:
                n_rungs_draw = len({c["rung"] for c in cells})
                boot_seed = seed * 7919 + int(round(phi * 1000)) * 1_000_003 + draw
                primary = an.primary_4(cells, n_boot=N_BOOT_POWER_4, seed=boot_seed)
                tree = an.verdict_tree_4([], n_cells, n_rungs_draw, primary)
                T = primary["T"]
            world = tree["verdict"]
            world_counts[world] = world_counts.get(world, 0) + 1
            if T is not None:
                Ts.append(T)

        if world_counts.get("INSUFFICIENT_DATA", 0):
            raise RuntimeError("power_4.compute: a simulated draw reached INSUFFICIENT_DATA "
                               "(should be unreachable — failures is always [])")

        mean_T = float(np.mean(Ts)) if Ts else None
        sd_T = float(np.std(Ts, ddof=1)) if len(Ts) > 1 else (0.0 if len(Ts) == 1 else None)
        arms[str(phi)] = {
            "P_LEADS": world_counts.get("LEADS", 0) / n_sim,
            "P_PARTIAL": world_counts.get("PARTIAL", 0) / n_sim,
            "P_FOLLOWS": world_counts.get("FOLLOWS", 0) / n_sim,
            "P_UNDETERMINED": world_counts.get("UNDETERMINED", 0) / n_sim,
            "P_NO_CONVERGENCE": world_counts.get("NO-CONVERGENCE", 0) / n_sim,
            "mean_T": mean_T, "sd_T": sd_T,
            "mean_eligible_cells": float(np.mean(elig_counts)) if elig_counts else 0.0,
        }

    null_key = str(0.0)
    null_sd_T = arms[null_key]["sd_T"] if null_key in arms else None
    if null_sd_T is not None:
        z = norm.ppf(1.0 - an.ALPHA_4) + norm.ppf(0.75)
        min_detectable_T = float(null_sd_T * z)
    else:
        min_detectable_T = None

    decl_key = str(0.5)
    if decl_key in arms and arms[decl_key]["P_LEADS"] is not None:
        declaration = "POWERED" if arms[decl_key]["P_LEADS"] >= 0.75 else "UNDERPOWERED IN ADVANCE"
    else:
        declaration = "UNDERPOWERED IN ADVANCE"

    return {
        "n_sim": n_sim, "seed": seed, "phis": list(phis), "arms": arms,
        "null_sd_T": null_sd_T, "min_detectable_T": min_detectable_T,
        "min_detectable_T_note": MIN_DETECTABLE_T_NOTE_4,
        "declaration": declaration,
        "cells": [[t, r] for t, r in candidates], "rungs": rungs,
        "flip_resolution": 1.0 / (2 ** n_rungs) if n_rungs else None,
        "assumptions": TREND_SHAPE_NOTE_4,
        "eligibility_bar_null_crossing_note": ELIGIBILITY_BAR_NULL_CROSSING_NOTE_4,
        "eligibility_sha256": None, "prereg_tag": None,
    }


def main(root=battery_4.EXP4, *, n_sim: int = 1000, seed: int = 0,
        phis: tuple = (0.0, 0.25, 0.5)) -> dict:
    root = Path(root)
    out_path = battery_4.power_path(root)
    if out_path.exists():
        raise RuntimeError(f"{out_path} exists — the power record is written ONCE")
    elig_path = battery_4.eligibility_path(root)
    if not elig_path.is_file():
        raise RuntimeError(f"{elig_path} is not present — run the reference stage first")
    elig_sha = bg.sha256_file(elig_path)
    elig = json.loads(elig_path.read_text())

    floors = bg.load_floors()
    battery = bt.load_battery()
    rung_sets = {}
    for traj in battery_4.TRAJECTORIES_4:
        outcome = battery_4.load_outcome_4(traj, battery=battery)
        rung_sets[traj] = battery_4.rung_sets_4(outcome, floors)
    grids = {traj: list(battery_4.GRID_4[traj]) for traj in battery_4.TRAJECTORIES_4}

    rec = compute(elig, rung_sets, grids, n_sim=n_sim, seed=seed, phis=phis)
    rec["eligibility_sha256"] = elig_sha
    rec["prereg_tag"] = battery_4.PREREG_TAG_4

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1))
    print(f"declaration: {rec['declaration']}")
    for phi, arm in rec["arms"].items():
        print(f"  phi={phi}: P_LEADS={arm['P_LEADS']:.3f} mean_T={arm['mean_T']} "
             f"mean_eligible_cells={arm['mean_eligible_cells']:.2f}")
    print(f"null_sd_T={rec['null_sd_T']} min_detectable_T={rec['min_detectable_T']}")
    return rec


if __name__ == "__main__":
    main()
