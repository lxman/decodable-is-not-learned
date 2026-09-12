# experiments/exp4/power_4.py
"""Experiment 4's power record (design §4; Task 5 brief + resolutions;
final review IMPORTANT 2 / ratification item R-7 adds the fourth arm),
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

A FOURTH arm, `"zero_excess"` (R-7), injects E_r = 0 for EVERY rung of
R_M -- the whole candidate pool, not only the eligible cells -- through
the same path, because phi's null mean is ~.5, not 0, for cells
SELECTED at the 2-SE bar; its P_LEADS is the record's
`realized_alpha_leads`, and `zero_excess_scatter` re-runs it at noise
multiples 1/1.5/2/3 so the analyzer's measured `lambda_hat` can be
placed against it. See ZERO_EXCESS_NOTE_4.

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

# Review round 1, IMPORTANT 2: for a cell whose t_clear sits at or near
# the grid's last index (c_r close to G-1), phi*=0's FIXED m=c_r+3
# construction (never bisected -- the disclosed asymptote formula) can
# leave F_end small regardless of the true achievable floor, giving a
# simulated endpoint excess well below the cell's real E_r (e.g. ~1.8%
# of E_r when c_r == G-1: G-1-m = G-1-(c_r+3) = -4 exactly whenever
# c_r == G-1, for ANY G). An alternative arm's BISECTED construction
# searches for the m that best hits its own (higher) target ratio, and
# in doing so typically keeps F_end larger for the same cell -- so the
# null arm's simulated excess is more likely to miss the eligibility
# bar (SE_MULTIPLE_4 * se) than an alternative arm's, and the null
# arm's eligible-cell set can read SMALLER for exactly the cells this
# affects. null_sd_T/min_detectable_T/the realized alpha are all
# computed on the null arm's own (possibly smaller) eligible set. See
# the per-cell `construction` block and `construction_miss`
# (|realized_ratio - phi*| > .02, computed once per (phi, cell) below,
# never silently) for exactly which cells and arms this affects.
CONSTRUCTION_NOTE_4 = (
    "for a cell whose t_clear sits at or near the grid's last index, phi*=0's fixed m=c_r+3 "
    "construction can leave F_end small regardless of the true achievable floor (e.g. ~1.8% of "
    "E_r when c_r == G-1), more likely to miss the eligibility bar than an alternative arm's "
    "bisected construction -- the null arm's eligible-cell set can therefore read SMALLER than an "
    "alternative arm's for the affected cells, and null_sd_T/min_detectable_T/the realized alpha "
    "are computed on the null arm's own (possibly smaller) eligible set; see the per-cell "
    "`construction` block and `construction_miss` (|realized_ratio - phi*| > .02) for exactly "
    "which cells and arms this affects."
)

NOISE_SCALE_NOTE_4 = (
    "noise is drawn independently at EVERY grid point (not only t_1/t_end), so a two-point "
    "difference like the endpoint excess itself combines two independent N(0, se) draws at "
    "sqrt(2) times the nominal se -- part of why null cells cross the eligibility bar above its "
    "nominal rate (see eligibility_bar_null_crossing_note)."
)

RNG_ORDER_NOTE_4 = (
    "a single numpy Generator stream (seeded once from `seed`) is consumed sequentially across "
    "every arm in `phis` order, each arm's n_sim draws run to completion before the next arm "
    "begins -- the arms are successive draws from one stream, not independently-seeded replicates "
    "of each other; the zero-excess arms follow the phi arms on the same stream, in ascending "
    "scatter-multiple order, so adding them leaves every phi arm's draws byte-identical."
)

# Final review, IMPORTANT 2 -> ratification item R-7. The arm the LEADS
# licence is read against, and the reason it exists: phi's null mean is
# ~.5, not 0, for cells SELECTED at the eligibility bar. x_r(t_1) and
# trend(t_1) enter BOTH the numerator x_r(t-) and the denominator
# x_r(t_end), so Cov(x_pre, x_end) = Var(noise at t_1) and the
# correlation is exactly .5 under pure noise -- conditioning on a large
# positive x_end drags x(t-) up with it (the reviewer measured a
# selected-cell mean phi of .4957 under pure noise). The phi = 0 arm
# CANNOT see this: it injects each cell's real E_r, so the eligibility
# bar is not binding there and the selection that inflates phi never
# happens. The zero-excess arm injects E_r = 0 for EVERY rung of R_M --
# the whole candidate pool, not only the cells the eligibility stage
# selected -- at the measured SEs, with the flat pool as trend and the
# eligibility rule re-applied per draw, through the verdict's own tree.
ZERO_EXCESS_NOTE_4 = (
    "the `zero_excess` arm (final review IMPORTANT 2 / ratification item R-7) injects E_r = 0 for "
    "EVERY rung of R_M -- the whole candidate pool, not only the cells the eligibility stage "
    "selected -- at the measured SEs (rising rungs' `se`, flat rungs' `se_at_end`), with the flat "
    "pool as trend and the eligibility rule re-applied per draw, through cells_4 -> primary_4 -> "
    "verdict_tree_4. It exists because phi's null mean is ~.5, not 0, for cells SELECTED at the "
    "2-SE bar (the shared a_r(t_1) - trend(t_1) baseline sits in both the numerator x_r(t-) and "
    "the denominator x_r(t_end), so conditioning on a large positive x_end drags x(t-) up with "
    "it); the phi = 0 arm injects each cell's real E_r, so the selection is not binding there. "
    "`realized_alpha_leads` is this arm's own P_LEADS. `zero_excess_scatter` re-runs the arm with "
    "the per-step noise multiplied by each of the `zero_excess_multiples` while the eligibility "
    "bar stays at the measured (unmultiplied) SE, so the analyzer's realized lambda_hat -- the "
    "flat pool's between-step scatter over its own item-bootstrap SE, reported per trajectory "
    "under the verdict's `calibration` -- can be placed against the grid. The multiple 1.0 run IS "
    "the `zero_excess` arm, not a second draw of it."
)

ASSUMPTIONS_4 = " ".join(
    [TREND_SHAPE_NOTE_4, CONSTRUCTION_NOTE_4, NOISE_SCALE_NOTE_4, RNG_ORDER_NOTE_4,
     ZERO_EXCESS_NOTE_4])

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
N_SIM_4 = 1000   # the campaign constant (review round 1, IMPORTANT 3); tests inject a smaller n_sim
CONSTRUCTION_MISS_TOL_4 = 0.02


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


def _pool(elig: dict) -> list:
    """EVERY (traj, rung) of R_M in the eligibility table -- the whole
    candidate pool the zero-excess arm simulates, eligible or not (R-7:
    the selection at the 2-SE bar is the thing that arm exists to
    price, so it must not be conditioned on)."""
    out = []
    for traj, block in elig.items():
        for rung in (block.get("R") or {}):
            out.append((traj, rung))
    return sorted(out)


def _multiple_key(m) -> str:
    return str(float(m))


def _degenerate_arm() -> dict:
    """An arm with nothing to simulate: every draw is NO-CONVERGENCE
    with certainty, and there is no T distribution to summarize, so
    mean_T/sd_T are None -- legitimate, not missing data (analyze_4's
    `_check_power_matches_eligibility_4` accepts None exactly when
    `mean_eligible_cells == 0.0`)."""
    return {"P_LEADS": 0.0, "P_PARTIAL": 0.0, "P_FOLLOWS": 0.0, "P_UNDETERMINED": 0.0,
            "P_NO_CONVERGENCE": 1.0, "mean_T": None, "sd_T": None,
            "mean_eligible_cells": 0.0, "construction_miss_count": 0}


def _arm_from_counts(world_counts, Ts, elig_counts, n_sim, *, construction_miss_count=0) -> dict:
    mean_T = float(np.mean(Ts)) if Ts else None
    sd_T = float(np.std(Ts, ddof=1)) if len(Ts) > 1 else (0.0 if len(Ts) == 1 else None)
    return {
        "P_LEADS": world_counts.get("LEADS", 0) / n_sim,
        "P_PARTIAL": world_counts.get("PARTIAL", 0) / n_sim,
        "P_FOLLOWS": world_counts.get("FOLLOWS", 0) / n_sim,
        "P_UNDETERMINED": world_counts.get("UNDETERMINED", 0) / n_sim,
        "P_NO_CONVERGENCE": world_counts.get("NO-CONVERGENCE", 0) / n_sim,
        "mean_T": mean_T, "sd_T": sd_T,
        "mean_eligible_cells": float(np.mean(elig_counts)) if elig_counts else 0.0,
        "construction_miss_count": construction_miss_count,
    }


def _simulate_zero_excess(*, pool_info, traj_info, trend_arr, rung_sets, rng, n_sim, scale,
                          seed, scale_index) -> dict:
    """R-7's arm at one scatter multiple: E_r = 0 for every rung of the
    pool, per-step Gaussian noise at `scale` x the measured SE, the flat
    pool as trend, and the ELIGIBILITY BAR LEFT AT THE MEASURED SE (the
    multiple models between-checkpoint scatter that the item bootstrap
    does not see; multiplying the bar too would defeat the reading).
    Runs through `analyze_4.trend_4` -> `excess_4` -> the eligibility
    rule -> `cells_4` -> `primary_4` -> `verdict_tree_4`, the same
    functions the real analyzer calls."""
    pool_trajs = sorted(traj_info)
    world_counts = {w: 0 for w in an.WORLDS_4}
    Ts, elig_counts = [], []
    for draw in range(n_sim):
        series_by_traj = {}
        for traj in pool_trajs:
            ti = traj_info[traj]
            steps = ti["steps"]
            G = len(steps)
            a = {}
            for r in ti["flat"]:
                noise = rng.normal(0.0, ti["flat_se"][r] * scale, size=G)
                a[r] = (trend_arr[traj] + noise).tolist()
            series_by_traj[traj] = {"steps": steps, "a": a}
        for (traj, rung), info in pool_info.items():
            noise = rng.normal(0.0, info["se_r"] * scale, size=info["G"])
            series_by_traj[traj]["a"][rung] = (trend_arr[traj] + noise).tolist()

        eligibility_sim = {}
        for traj in pool_trajs:
            rs = rung_sets[traj]
            trend = an.trend_4(series_by_traj[traj]["a"], rs["flat"], series_by_traj[traj]["steps"])
            excess = an.excess_4(series_by_traj[traj]["a"], trend, series_by_traj[traj]["steps"])
            Rdict = {}
            for (t2, rung), info in pool_info.items():
                if t2 != traj:
                    continue
                ok = excess[rung][-1] >= an.SE_MULTIPLE_4 * info["se_r"]
                Rdict[rung] = {"eligible": bool(ok), "t_clear": info["t_clear"],
                              "t_clear_index": info["c_r"]}
            eligibility_sim[traj] = {"R": Rdict}

        rs_subset = {traj: rung_sets[traj] for traj in pool_trajs}
        cells = an.cells_4(series_by_traj, rs_subset, eligibility_sim)
        n_cells = len(cells)
        elig_counts.append(n_cells)
        if n_cells == 0:
            tree = an.verdict_tree_4([], 0, 0, {})
            T = None
        else:
            n_rungs_draw = len({c["rung"] for c in cells})
            boot_seed = seed * 7919 + (911_000 + scale_index) * 1_000_003 + draw
            primary = an.primary_4(cells, n_boot=N_BOOT_POWER_4, seed=boot_seed)
            tree = an.verdict_tree_4([], n_cells, n_rungs_draw, primary)
            T = primary["T"]
        world_counts[tree["verdict"]] = world_counts.get(tree["verdict"], 0) + 1
        if T is not None:
            Ts.append(T)

    if world_counts.get("INSUFFICIENT_DATA", 0):
        raise RuntimeError("power_4._simulate_zero_excess: a simulated draw reached "
                           "INSUFFICIENT_DATA (should be unreachable — failures is always [])")
    arm = _arm_from_counts(world_counts, Ts, elig_counts, n_sim)
    arm["scatter_multiple"] = float(scale)
    return arm


def compute(elig: dict, rung_sets: dict, grids: dict, *, n_sim: int = N_SIM_4, seed: int = 0,
           phis: tuple = (0.0, 0.25, 0.5)) -> dict:
    candidates = _candidates(elig)
    pool = _pool(elig)
    if not pool:
        # Review round 2, NEW B(i) (the controller's ruling): zero
        # eligible cells is not an error to raise on -- it is a real,
        # disclosable outcome (the eligibility stage itself produced
        # nothing to simulate over). Every arm reads NO-CONVERGENCE with
        # certainty; there is no T distribution to summarize, so mean_T/
        # sd_T/null_sd_T/min_detectable_T are None -- legitimate, not
        # missing data (see `_check_power_matches_eligibility_4`'s
        # matching `mean_eligible_cells == 0.0` carve-out in analyze_4.py).
        # R-7: with an EMPTY POOL the zero-excess arm has nothing to
        # simulate either (it reads R_M, not the eligible set), so it
        # takes the same degenerate shape.
        arms = {str(phi): _degenerate_arm() for phi in phis}
        arms[an.ZERO_EXCESS_ARM_4] = dict(_degenerate_arm(), scatter_multiple=1.0,
                                          realized_alpha_leads=0.0)
        return {
            "n_sim": n_sim, "seed": seed, "phis": list(phis), "arms": arms,
            "null_sd_T": None, "min_detectable_T": None,
            "min_detectable_T_note": MIN_DETECTABLE_T_NOTE_4,
            "declaration": "UNDERPOWERED IN ADVANCE",
            "cells": [], "rungs": [],
            "flip_resolution": None,
            "assumptions": ASSUMPTIONS_4,
            "eligibility_bar_null_crossing_note": ELIGIBILITY_BAR_NULL_CROSSING_NOTE_4,
            "construction": {},
            "zero_excess_multiples": [float(m) for m in an.ZERO_EXCESS_MULTIPLES_4],
            "zero_excess_scatter": {_multiple_key(m): 0.0 for m in an.ZERO_EXCESS_MULTIPLES_4},
            "zero_excess_note": ZERO_EXCESS_NOTE_4,
            "zero_excess_pool_cells": [],
            "eligibility_sha256": None, "prereg_tag": None,
        }
    rungs = sorted({r for _, r in candidates})
    n_rungs = len(rungs)
    trajs = sorted({t for t, _ in candidates})
    pool_trajs = sorted({t for t, _ in pool})

    cell_info = {}
    for traj, rung in candidates:
        e = elig[traj]["R"][rung]
        steps = list(grids[traj])
        G = len(steps)
        c_r = int(e["t_clear_index"])
        cell_info[(traj, rung)] = dict(G=G, c_r=c_r, E_r=float(e["x_end"]), se_r=float(e["se"]),
                                       t_clear=e["t_clear"])

    # R-7: the zero-excess arm's own pool -- every rung of R_M, with its
    # measured SE and its fixed t_clear index. A rung with no pre-clear
    # window (t_clear_index None or < MIN_CLEAR_INDEX_4) stays in the
    # pool and is dropped by `phi_4` inside `cells_4`, exactly as the
    # real analyzer drops it.
    pool_info = {}
    for traj, rung in pool:
        e = elig[traj]["R"][rung]
        tci = e.get("t_clear_index")
        pool_info[(traj, rung)] = dict(G=len(list(grids[traj])),
                                       c_r=None if tci is None else int(tci),
                                       se_r=float(e["se"]), t_clear=e.get("t_clear"))

    traj_info = {}
    for traj in pool_trajs:
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
        # Review round 1 minor: real grids never start at step 0
        # (log-linear interpolation needs a strictly positive t_1) --
        # refuse rather than silently produce log(0) = -inf / nan.
        if s0 <= 0:
            raise ValueError(f"power_4.compute: {traj}'s grid starts at step {s0!r} <= 0 -- "
                             f"log-linear trend interpolation needs a strictly positive t_1")
        if s1 == s0:
            frac = np.zeros_like(steps_arr)
        else:
            frac = (np.log(steps_arr) - np.log(s0)) / (np.log(s1) - np.log(s0))
        trend_arr[traj] = ti["trend_t1"] + (ti["trend_end"] - ti["trend_t1"]) * frac

    m_by_phi = {phi: {key: _solve_m(info["c_r"], info["G"], phi) for key, info in cell_info.items()}
               for phi in phis}

    # Review round 1, IMPORTANT 2: record the REALIZED construction
    # (m, F_end, realized_ratio) per (phi, cell) -- a deterministic
    # property of (c_r, G, phi*) alone, computed once here, never
    # inferred from the noisy simulated draws.
    construction = {}
    for phi in phis:
        per_cell, miss_list = {}, []
        for (traj, rung), info in cell_info.items():
            m = m_by_phi[phi][(traj, rung)]
            G, c_r = info["G"], info["c_r"]
            F_end = float(_logistic((G - 1 - m) / LOGISTIC_WIDTH_4))
            F_pre = float(_logistic((c_r - 1 - m) / LOGISTIC_WIDTH_4))
            realized = (F_pre / F_end) if F_end > 0.0 else 0.0
            miss = abs(realized - phi) > CONSTRUCTION_MISS_TOL_4
            key = f"{traj}/{rung}"
            per_cell[key] = {"m": float(m), "F_end": F_end, "realized_ratio": float(realized),
                             "construction_miss": bool(miss)}
            if miss:
                miss_list.append(key)
        construction[str(phi)] = {"cells": per_cell, "construction_miss": miss_list,
                                  "construction_miss_count": len(miss_list)}

    rng = np.random.default_rng(seed)

    arms = {}
    for phi in phis:
        world_counts = {w: 0 for w in an.WORLDS_4}
        Ts, elig_counts = [], []
        for draw in range(n_sim):
            series_by_traj = {}
            for traj in trajs:
                ti = traj_info[traj]
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

        arms[str(phi)] = _arm_from_counts(
            world_counts, Ts, elig_counts, n_sim,
            construction_miss_count=construction[str(phi)]["construction_miss_count"])

    # R-7: the zero-excess arms, after every phi arm, on the same stream
    # and in ascending multiple order (so the phi arms' draws are
    # byte-identical to what they were before this arm existed). The
    # multiple-1.0 run IS the `zero_excess` arm; the grid is the same
    # simulation with the per-step noise scaled, so the realized
    # lambda_hat the analyzer measures can be placed against it.
    zero_by_multiple = {}
    for i, mult in enumerate(an.ZERO_EXCESS_MULTIPLES_4):
        zero_by_multiple[float(mult)] = _simulate_zero_excess(
            pool_info=pool_info, traj_info=traj_info, trend_arr=trend_arr, rung_sets=rung_sets,
            rng=rng, n_sim=n_sim, scale=float(mult), seed=seed, scale_index=i)
    zero_arm = dict(zero_by_multiple[1.0])
    zero_arm["realized_alpha_leads"] = zero_arm["P_LEADS"]
    arms[an.ZERO_EXCESS_ARM_4] = zero_arm
    zero_excess_scatter = {_multiple_key(m): zero_by_multiple[float(m)]["P_LEADS"]
                          for m in an.ZERO_EXCESS_MULTIPLES_4}

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
        "assumptions": ASSUMPTIONS_4,
        "eligibility_bar_null_crossing_note": ELIGIBILITY_BAR_NULL_CROSSING_NOTE_4,
        "construction": construction,
        "zero_excess_multiples": [float(m) for m in an.ZERO_EXCESS_MULTIPLES_4],
        "zero_excess_scatter": zero_excess_scatter,
        "zero_excess_note": ZERO_EXCESS_NOTE_4,
        "zero_excess_pool_cells": [[t, r] for t, r in pool],
        "eligibility_sha256": None, "prereg_tag": None,
    }


def main(root=battery_4.EXP4, *, n_sim: int = N_SIM_4, seed: int = 0,
        phis: tuple = an.POWER_PHIS_4) -> dict:
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
        print(f"  arm={phi}: P_LEADS={arm['P_LEADS']:.3f} mean_T={arm['mean_T']} "
             f"mean_eligible_cells={arm['mean_eligible_cells']:.2f}")
    zero = rec["arms"].get(an.ZERO_EXCESS_ARM_4) or {}
    print(f"realized_alpha_leads (zero excess)={zero.get('realized_alpha_leads')}; "
         f"zero_excess_scatter={rec.get('zero_excess_scatter')}")
    print(f"null_sd_T={rec['null_sd_T']} min_detectable_T={rec['min_detectable_T']}")
    return rec


if __name__ == "__main__":
    main()
