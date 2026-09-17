# experiments/exp4b/placebo_4b.py
"""Experiment 4b's placebo null (design `experiment-4b-design.md`
§3.2-§3.4, §5 S2-S5/S8; plan Task 2): is Exp 4's committed primary T
distinguishable from the T that the FLAT rungs produce when put
through Exp 4's OWN measurement (leave-one-out excess over the flat
pool, the same one-sided 2-SE eligibility bar with a leave-one-out
item-bootstrap SE, the real cells' clear-index multisets permuted onto
placebo rungs drawn with replacement)?

Every measurement primitive is Exp 4's own, imported and never
reimplemented: `analyze_4.trend_4/excess_4/phi_4/primary_4/
verdict_tree_4`. This module supplies only what changes for a
placebo rung — the leave-one-out trend/excess/eligibility-SE the real
rungs never needed (a real rung's trend is the FULL flat pool; a
placebo rung IS a flat rung, so it must be left out of its own
trend) — and the battery machinery (drawing placebo rungs against the
real cells' clear-index multisets, calibrating T against that null,
α_placebo, the per-type/per-trajectory breakdowns, and S3/S4/S5/S8).

Zero model contact; no torch import. Every function here is pure
computation over in-memory series/arrays (`{"steps", "a": {rung:
[...]}}` per-trajectory series, `{rung: float64[500]}` per-item
alignment arrays) — the real-tree loaders that build those inputs
from `experiments/exp4/results/` are `analyze_4b.py`'s job (Task 5).

Failure messages here are prefixed "4b: "."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Design §3.2 / build constraint: the BLAS thread pool is sized when
# numpy is first imported, and a multi-threaded reduction is not
# bit-reproducible across processes — `_threads_4` pins it before
# numpy (and before every `experiments.*` import that pulls numpy in
# transitively), exactly as `analyze_4.py` does.
from experiments.exp4 import _threads_4  # noqa: E402,F401

import numpy as np  # noqa: E402

from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import power_4 as pw  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402

# ------------------------------------------------------ leave-one-out trend


def loo_trend_4b(a: dict, flat: list, steps: list, f: str) -> list:
    """`trend_loo(t) = mean over r in flat \\ {f} of a_r(t)` — design
    §3.2's leave-one-out trend a placebo rung f is scored against (the
    pool of every OTHER flat rung).

    Final review Important 4: f is left out NOT because a self-included
    trend would make f's excess "identically zero" (it would not: a
    flat rung's self-included, full-pool excess is exactly
    `(n-1)/n` times its leave-one-out excess, n = `len(flat)`, both
    nonzero together or zero together) but because the self-included
    and leave-one-out constructions differ only by that same constant
    scale factor at every step -- `phi` (a ratio of two excess values)
    and the one-sided `x_end >= 2*SE` eligibility bar (both sides
    scaled identically) are PROVABLY INVARIANT to which of the two a
    placebo rung is read against (verified numerically in
    `test_placebo_pool_4b_loo_vs_full_pool_invariance_of_phi_and_
    eligibility`). Leave-one-out is used anyway (design §10 dial (c))
    because it is the exact analogue of a rising rung's own
    construction (never a member of the pool that scores it) --
    S4 (`s4_scatter_ratio_4b`) is the one statistic this scale factor
    actually touches, and it corrects for it explicitly. Raises
    `ValueError` when the leave-one-out pool is empty (`flat == [f]`
    or `f` not among a singleton `flat`) -- checked here, with a
    "4b: "-prefixed message, because `analyze_4.trend_4`'s own empty
    check carries no prefix and names no rung. The computation itself
    is `trend_4`'s own (called, never reimplemented)."""
    pool = [r for r in flat if r != f]
    if not pool:
        raise ValueError(f"4b: leave-one-out pool empty for {f}")
    return an.trend_4(a, pool, steps)


def loo_excess_4b(a: dict, flat: list, steps: list, f: str) -> list:
    """`x_f(t) = (a_f(t) - a_f(t_1)) - (trend_loo(t) - trend_loo(t_1))`
    under `loo_trend_4b` — `analyze_4.excess_4`'s own formula, applied
    to `f` against its own leave-one-out trend rather than the full
    flat pool. `x_f[0] == 0.0` by construction (both terms vanish at
    t_1)."""
    trend = loo_trend_4b(a, flat, steps, f)
    return an.excess_4({f: a[f]}, trend, steps)[f]


def placebo_phi_4b(x: list, c: int):
    """= `analyze_4.phi_4(x, c)` — a placebo rung's pre-clear fraction
    at an ASSIGNED clear index c is read by the identical rule a real
    rung's own t_clear reads by."""
    return an.phi_4(x, c)


# --------------------------------------------------- leave-one-out eligibility


def placebo_se_4b(pia_t1: dict, pia_end: dict, flat: list, f: str, *,
                   n_boot: int = an.N_BOOT_ELIG_4, seed: int = 0) -> float:
    """The item-bootstrap SD of `x_f(t_end)` under the leave-one-out
    trend — `analyze_4.eligibility_table_4`'s own `boot` shape, with
    the trend pool restricted to `flat \\ {f}`. Deterministic in
    `seed`; raises `ValueError` when the leave-one-out pool is empty."""
    pool = [r for r in flat if r != f]
    if not pool:
        raise ValueError(f"4b: leave-one-out pool empty for {f}")
    n = battery_4.N_ITEMS
    rng = np.random.default_rng(seed)

    def boot(r):
        idx = rng.integers(0, n, size=(n_boot, n))
        return pia_t1[r][idx].mean(axis=1), pia_end[r][idx].mean(axis=1)

    pool_t1, pool_e = [], []
    for r in pool:
        a1, ae = boot(r)
        pool_t1.append(a1)
        pool_e.append(ae)
    trend_t1 = np.mean(pool_t1, axis=0)
    trend_e = np.mean(pool_e, axis=0)
    f_t1, f_e = boot(f)
    x_end_b = (f_e - f_t1) - (trend_e - trend_t1)
    return float(np.std(x_end_b, ddof=1))


def placebo_pool_4b(series: dict, pia_t1: dict, pia_end: dict, flat: list, *,
                     n_boot: int, seed: int) -> dict:
    """`{f: {"x_end", "se", "eligible", "excess": [...]}}` for every f
    in `flat` — the leave-one-out excess series, its endpoint value,
    the leave-one-out item-bootstrap SE (the SAME `seed` re-seeds a
    fresh generator per f, so the pool is order-independent), and the
    one-sided `SE_MULTIPLE_4`-SE eligibility bar. `P_M = [f for f in
    flat if pool[f]["eligible"]]` is read off this by the caller.

    Refuses, per f, unless `series["a"][f][0]`/`[-1]` are EXACTLY the
    means of `pia_t1[f]`/`pia_end[f]` -- `alignment_series_4` sets
    `a[r].append(float(pia[r].mean()))`, so a real (t_1, endpoint)
    series/pia pair satisfies this identically; a mismatch means the
    excess (from `series`) and the SE (from `pia_t1`/`pia_end`) were
    built from different checkpoints, which would silently change P_M
    and the whole null with no other gate catching it."""
    steps = series["steps"]
    a = series["a"]
    out = {}
    for f in flat:
        want_t1 = float(pia_t1[f].mean())
        want_end = float(pia_end[f].mean())
        if a[f][0] != want_t1 or a[f][-1] != want_end:
            raise ValueError(
                f"4b: series/pia mismatch for {f} -- series[\"a\"][{f!r}] is "
                f"[{a[f][0]!r}, ..., {a[f][-1]!r}] but pia_t1[{f!r}].mean() = "
                f"{want_t1!r} and pia_end[{f!r}].mean() = {want_end!r}; these must "
                f"be the SAME checkpoint's tables (alignment_series_4's own identity)")
        excess = loo_excess_4b(a, flat, steps, f)
        x_end = excess[-1]
        se = placebo_se_4b(pia_t1, pia_end, flat, f, n_boot=n_boot, seed=seed)
        eligible = x_end >= an.SE_MULTIPLE_4 * se
        out[f] = {"x_end": x_end, "se": se, "eligible": bool(eligible), "excess": excess}
    return out


# --------------------------------------------------------------- the batteries


def draw_batteries_4b(pools: dict, design: dict, *, B: int, seed: int, rng=None) -> dict:
    """`B` placebo batteries: for each trajectory M (in `sorted(design)`
    order) with real cell count n_M and real clear-index multiset C_M,
    draw n_M placebo rungs from `P_M` WITH replacement and assign a
    uniformly random permutation of C_M to them; `T_b` is the plain
    mean of phi over the battery's cells (every trajectory's cells
    pooled). One `np.random.default_rng(seed)` consumed across every
    battery and trajectory in that fixed order (`rng`, when given,
    is used in place of constructing a fresh one — the caller's own
    generator, still consumed in the same order).

    Raises `ValueError` naming the trajectory when it has real cells
    (`design[t]["n"] > 0`) but no eligible placebo rung at all."""
    if rng is None:
        rng = np.random.default_rng(seed)
    trajs = sorted(design)
    P = {t: sorted(f for f, d in pools[t].items() if d["eligible"]) for t in trajs}
    feas = {}
    for t in trajs:
        if design[t]["n"] > 0 and not P[t]:
            raise ValueError(f"4b: no eligible placebo rung on {t}")
        feas[t] = {"n_real": design[t]["n"], "n_eligible_placebo": len(P[t]),
                   "deficit": design[t]["n"] > 0 and len(P[t]) < battery_4b.MIN_PLACEBO_PER_TRAJ_4B}
    T = np.empty(B)
    per_traj = {t: np.empty(B) for t in trajs}
    cells_all = []
    n_distinct = np.empty(B, dtype=int)
    for b in range(B):
        cells = []
        for t in trajs:
            n = design[t]["n"]
            if n == 0:
                per_traj[t][b] = np.nan
                continue
            picks = rng.integers(0, len(P[t]), size=n)
            order = rng.permutation(n)
            cs = [design[t]["clear_indices"][i] for i in order]
            phis = []
            for k, c in zip(picks, cs):
                f = P[t][k]
                phi = an.phi_4(pools[t][f]["excess"], c)
                if phi is None:
                    raise ValueError(f"4b: placebo phi undefined for {t}/{f} at c={c}")
                cells.append({"traj": t, "rung": f, "phi": phi, "c": int(c)})
                phis.append(phi)
            per_traj[t][b] = float(np.mean(phis))
        # A guard, not a behaviour change: every REAL design has at
        # least one trajectory with n > 0, so `cells` is never empty in
        # the main pipeline. A type-restricted design (per_type_4b) can
        # zero every trajectory, though -- `np.mean([])` would still
        # return nan there, but noisily (RuntimeWarning); this reaches
        # the same nan without it.
        T[b] = float(np.mean([c["phi"] for c in cells])) if cells else float("nan")
        n_distinct[b] = len({c["rung"] for c in cells})
        cells_all.append(cells)
    return {"T": T, "per_traj_mean": per_traj, "cells": cells_all,
            "n_distinct_rungs": n_distinct, "feasibility": feas, "P": P}


# ------------------------------------------------------------- calibration


def p_cal_4b(T_b, T4: float) -> dict:
    """`p_cal = (1 + #{b: T_b >= T4 - eps}) / (B + 1)` — design §3.3's
    ONE-SIDED calibration reading of the observed T4 (the lens
    account's direction), add-one smoothed against the B draws.
    `p_low = (1 + #{b: T_b <= T4 + eps}) / (B + 1)` is printed beside
    it as its two-sided COMPLEMENT only (design §3.3: "nothing more"),
    not a second calibration."""
    T_b = np.asarray(T_b, dtype=np.float64)
    B = int(len(T_b))
    eps = 1e-15
    p_cal = (1 + int(np.sum(T_b >= T4 - eps))) / (B + 1)
    p_low = (1 + int(np.sum(T_b <= T4 + eps))) / (B + 1)
    return {"p_cal": float(p_cal), "p_low": float(p_low), "B": B,
            "p_cal_mc_se": _mc_se_4b(p_cal, B)}


def _mc_se_4b(p: float, B: int):
    """FREEZE F-2: p_cal is a Monte Carlo estimate over B battery
    draws, and design §3.7's tree reads it against two HARD bars (.01,
    .05) with no tolerance at either. Its own resolution is the
    binomial SE sqrt(p(1-p)/B) -- .00099 at p = .01, .00218 at p = .05,
    B = 10,000 (measured at the freeze on a synthetic pool at this
    design's own sizes: the seed-to-seed SD of p_cal over twelve seeds
    matched the binomial law to the third decimal). The seed is fixed
    pre-tag in `battery_4b.SEED_4B` and tag-bound, so this is a
    RESOLUTION disclosure, not a manipulation channel -- but a p_cal
    within about one of these SEs of a bar is decided by the draw, and
    the record says so rather than leaving a reader to compute it
    (2l/2n's lesson: a bar needs a tolerance)."""
    if not B:
        return None
    return float(np.sqrt(max(p * (1.0 - p), 0.0) / B))


def bar_margins_4b(p_cal: float, B: int, bars=None) -> dict:
    """F-2's reading: each tree bar's distance from `p_cal` in units of
    p_cal's own Monte Carlo SE. `within_mc_se` names every bar the
    estimate sits closer to than 2 SE -- the cells where the world
    turns on the draw rather than on the data."""
    if bars is None:
        bars = (battery_4b.ALPHA_4B, battery_4b.MARGINAL_4B)
    se = _mc_se_4b(p_cal, B)
    out, close = {}, []
    for bar in bars:
        if se:
            out[str(bar)] = {"margin": float(p_cal - bar), "margin_in_mc_se": float((p_cal - bar) / se)}
            if abs(p_cal - bar) <= 2.0 * se:
                close.append(str(bar))
        else:
            out[str(bar)] = {"margin": float(p_cal - bar), "margin_in_mc_se": None}
    return {"p_cal_mc_se": se, "per_bar": out, "within_2_mc_se": close,
            "note": ("p_cal is a Monte Carlo estimate over B draws; a bar it sits within ~1 SE "
                     "of is decided by the seeded draw, not by the data. The seed is fixed "
                     "pre-tag and tag-bound; this is a resolution disclosure.")}


def t_star_4b(T_b, T4: float) -> dict:
    """The calibrated lead `T* = T4 - mean(T_b)`, its placebo interval
    `[T4 - Q.975(T_b), T4 - Q.025(T_b)]`, the null's mean/SD, and its
    upper quantiles `q95`/`q99` (the T that would have cleared each
    percentile)."""
    T_b = np.asarray(T_b, dtype=np.float64)
    null_mean = float(np.mean(T_b))
    null_sd = float(np.std(T_b, ddof=1))
    lo, hi = np.percentile(T_b, [2.5, 97.5])
    q95 = float(np.percentile(T_b, 95))
    q99 = float(np.percentile(T_b, 99))
    return {"T_star": float(T4 - null_mean), "interval": [float(T4 - hi), float(T4 - lo)],
            "null_mean": null_mean, "null_sd": null_sd, "q95": q95, "q99": q99}


def alpha_placebo_4b(batteries: dict, *, seed: int, b_alpha=None, real_regime: dict = None) -> dict:
    """Exp 4's own LEADS rule run on every placebo battery's cells,
    through `analyze_4.primary_4`/`verdict_tree_4` unchanged —
    `alpha_placebo` is the false-positive rate of Exp 4's rule on the
    real flat-rung scatter. `b_alpha` (default `None` -> every
    battery) caps how many of `batteries["cells"]` are scored.

    Ruled addition r3 (final review): `flip_method_counts` tallies how
    many of the scored batteries' own `primary_4(...)["flip_method"]`
    came back `"exact"` (the rung-level sign-flip null enumerated,
    `n_rungs <= MAX_ENUMERATE_4`) versus `"sampled"` (Monte Carlo
    flips) — the regime a given placebo battery's rung count happened
    to land in, disclosed rather than assumed uniform. `real_regime`
    (default `None`) is passed through VERBATIM, never recomputed —
    the caller reads it straight off the committed `v4["primary"]`
    (`flip_method`/`n_rungs`), so the record can be read beside the
    tally without this function ever touching `v4` itself."""
    cells_all = batteries["cells"]
    B = len(cells_all)
    n_batteries = B if b_alpha is None else min(int(b_alpha), B)
    world_counts = {w: 0 for w in an.WORLDS_4}
    flip_method_counts = {"exact": 0, "sampled": 0}
    n_leads = 0
    for b in range(n_batteries):
        cells = cells_all[b]
        primary = an.primary_4(cells, n_boot=pw.N_BOOT_POWER_4, seed=seed * 7919 + b)
        n_rungs = len({c["rung"] for c in cells})
        v = an.verdict_tree_4([], len(cells), n_rungs, primary)
        world = v["verdict"]
        world_counts[world] = world_counts.get(world, 0) + 1
        method = primary.get("flip_method")
        flip_method_counts[method] = flip_method_counts.get(method, 0) + 1
        if world == "LEADS":
            n_leads += 1
    alpha_placebo = (n_leads / n_batteries) if n_batteries else 0.0
    return {"alpha_placebo": float(alpha_placebo), "n_batteries": int(n_batteries),
            "world_counts": world_counts, "n_leads": int(n_leads),
            "flip_method_counts": flip_method_counts, "real_regime": real_regime}


def per_traj_4b(batteries: dict, design: dict, v4_per_traj: dict) -> dict:
    """Per trajectory: the observed T read from Exp 4's OWN
    `primary.per_traj` record (`v4_per_traj[traj]["T"]`), calibrated
    against that trajectory's own placebo null
    (`batteries["per_traj_mean"][traj]`, NaN-free wherever the design
    carries real cells)."""
    out = {}
    for t, rec in v4_per_traj.items():
        T_obs = float(rec["T"])
        T_b = np.asarray(batteries["per_traj_mean"][t], dtype=np.float64)
        if np.any(np.isnan(T_b)):
            raise ValueError(f"4b: per_traj_mean for {t} carries NaN — "
                             f"design[{t!r}]['n'] must be > 0 to calibrate against it")
        pc = p_cal_4b(T_b, T_obs)
        ts = t_star_4b(T_b, T_obs)
        out[t] = {"T_obs": T_obs, "p_cal": pc["p_cal"], "T_star": ts["T_star"],
                  "interval": ts["interval"], "null_mean": ts["null_mean"],
                  "null_sd": ts["null_sd"], "n_cells": design[t]["n"]}
    return out


def per_type_4b(pools: dict, cells: list, *, B: int, seed: int) -> dict:
    """Build finding B-2: per rung-type tau, a type-restricted placebo
    battery — the real cells of type tau (their count and clear
    multiset, per trajectory) matched against `P_M` restricted to
    `RUNG_TYPE_4[f] == tau`. A trajectory with real cells of type tau
    but no eligible SAME-TYPE placebo rung contributes no cells to
    that trajectory (its deficit is printed under `feasibility`,
    `draw_batteries_4b`'s totality raise never triggers for it). A
    type with no real cells at all reads `None`.

    Refuses (p_cal/T_star/interval/null_mean/null_sd all `None`, with
    a `reason` string) rather than compute a calibration when the type
    battery's null does not cover every trajectory that contributes to
    `T_obs` (T_obs would average in a trajectory the null says nothing
    about) or is empty outright (every trajectory zeroed). Both are
    detected BEFORE `p_cal_4b`/`t_star_4b` are called, so neither the
    NaN propagation nor its RuntimeWarning ever happens."""
    offset = {"arithmetic": 1, "option": 2, "string": 3}
    out = {}
    for typ in battery_4b.TYPES_4B:
        type_cells = [c for c in cells if an.RUNG_TYPE_4.get(c["rung"]) == typ]
        if not type_cells:
            out[typ] = None
            continue
        design_full = battery_4b.real_design_4b(type_cells)
        pools_typ, design_typ, feasibility = {}, {}, {}
        for t, d in design_full.items():
            pool_t = {f: v for f, v in pools.get(t, {}).items()
                     if an.RUNG_TYPE_4.get(f) == typ}
            n_eligible = sum(1 for v in pool_t.values() if v["eligible"])
            if d["n"] > 0 and n_eligible == 0:
                design_typ[t] = {"n": 0, "clear_indices": [], "rungs": []}
            else:
                design_typ[t] = d
            feasibility[t] = {"n_real": d["n"], "n_eligible_placebo": n_eligible,
                              "deficit": d["n"] > 0 and n_eligible < battery_4b.MIN_PLACEBO_PER_TRAJ_4B}
            pools_typ[t] = pool_t
        batteries_typ = draw_batteries_4b(pools_typ, design_typ, B=B, seed=seed + offset[typ])
        T_obs = float(np.mean([c["phi"] for c in type_cells]))
        n_cells_obs = len(type_cells)

        obs_trajs = {c["traj"] for c in type_cells}
        covered_trajs = {t for t, d in design_typ.items() if d["n"] > 0}
        uncovered = sorted(obs_trajs - covered_trajs)
        null_empty = bool(np.all(np.isnan(batteries_typ["T"])))

        if uncovered or null_empty:
            reason = (f"4b: {typ} type battery's null does not cover every "
                      f"trajectory contributing to T_obs (uncovered: {uncovered})"
                      if uncovered else
                      f"4b: {typ} type battery's null is empty (no eligible "
                      f"same-type placebo rung on any contributing trajectory)")
            out[typ] = {"T_obs": T_obs, "p_cal": None, "T_star": None, "interval": None,
                        "null_mean": None, "null_sd": None, "n_cells": n_cells_obs,
                        "feasibility": feasibility, "reason": reason}
            continue

        pc = p_cal_4b(batteries_typ["T"], T_obs)
        ts = t_star_4b(batteries_typ["T"], T_obs)
        out[typ] = {"T_obs": T_obs, "p_cal": pc["p_cal"], "T_star": ts["T_star"],
                    "interval": ts["interval"], "null_mean": ts["null_mean"],
                    "null_sd": ts["null_sd"], "n_cells": n_cells_obs,
                    "feasibility": feasibility, "reason": None}
    return out


# ------------------------------------------------------------------- S3/S4/S5/S8


def _bin_label(frac: float) -> str:
    if frac < 0.2:
        return "[0,.2)"
    if frac < 0.4:
        return "[.2,.4)"
    if frac < 0.6:
        return "[.4,.6)"
    if frac < 0.8:
        return "[.6,.8)"
    return "[.8,1]"


def s3_shape_4b(batteries: dict, design: dict, cells: list) -> dict:
    """S3 — the null's shape (design §5): mean/SD of placebo phi per
    trajectory and per clear index c present in C_M (pooled over every
    battery draw at that (traj, c)); the pooled null-mean-of-phi as a
    function of c/(G-1) in five bins; and, per REAL cell, the
    calibrated excess `e = phi_obs - mean placebo phi at the same
    (traj, c)` and the cell's placebo quantile (share of placebo phi
    at or below phi_obs).

    Takes `cells` (Exp 4's real cells, `traj/rung/phi/t_clear_index`)
    in addition to the two-argument shape the plan's interface line
    names, because the per-real-cell residual the design doc requires
    (`experiment-4b-design.md` S3) reads phi_obs off the real cell,
    which `design` (`battery_4b.real_design_4b`'s reduced clear-index
    multiset) does not carry — see the Task 2 report."""
    buckets: dict = {}
    for battery_cells in batteries["cells"]:
        for cell in battery_cells:
            buckets.setdefault((cell["traj"], cell["c"]), []).append(cell["phi"])

    per_traj_c: dict = {}
    for (t, c), vals in buckets.items():
        arr = np.asarray(vals, dtype=np.float64)
        per_traj_c.setdefault(t, {})[c] = {
            "mean": float(arr.mean()),
            "sd": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
            "n": int(len(arr)),
        }

    pooled_bins = {label: [] for label in
                   ("[0,.2)", "[.2,.4)", "[.4,.6)", "[.6,.8)", "[.8,1]")}
    for (t, c), vals in buckets.items():
        grid = battery_4.GRID_4.get(t)
        g = len(grid) if grid else max(design[t]["clear_indices"], default=1) + 1
        frac = (c / (g - 1)) if g > 1 else 0.0
        pooled_bins[_bin_label(frac)].extend(vals)
    pooled_bins_summary = {
        label: ({"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1)) if len(v) > 1 else 0.0,
                "n": len(v)} if v else {"mean": None, "sd": None, "n": 0})
        for label, v in pooled_bins.items()
    }

    per_cell = []
    for rc in cells:
        t, c, phi_obs = rc["traj"], rc["t_clear_index"], rc["phi"]
        stat = per_traj_c.get(t, {}).get(c)
        if stat is None:
            per_cell.append({"traj": t, "rung": rc["rung"], "c": c, "phi_obs": phi_obs,
                             "e": None, "quantile": None, "n_null": 0})
            continue
        null_vals = np.asarray(buckets[(t, c)], dtype=np.float64)
        per_cell.append({
            "traj": t, "rung": rc["rung"], "c": c, "phi_obs": phi_obs,
            "e": float(phi_obs - stat["mean"]),
            "quantile": float(np.mean(null_vals <= phi_obs)),
            "n_null": stat["n"],
        })

    return {"per_traj_c": per_traj_c, "pooled_bins": pooled_bins_summary, "per_cell": per_cell}


# FREEZE NB-1 minor: VERDICT.txt's S4 line and the record's pooled
# block state WHAT is compared, so a reader is never left to infer it
# from the field names.
S4_COMPARED_NOTE_4B = (
    "RMS of the RISING cells' full-flat-pool excess increments over each cell's pre-clear "
    "window (grid indices strictly before its clear) / RMS of the FLAT rungs' leave-one-out "
    "excess increments over the whole grid; both sides target-outside-pool and raw (no "
    "rescale), differing only in pool size (n vs n-1), whose matched-scale expectation is "
    "sqrt(1 - 1/n^2) -- see pool_size_expected_ratio")

# design §5's own reading bins for the pooled null-mean-of-phi against
# c/(G-1), in order. `s3_shape_4b` builds exactly these keys; a fast
# test pins the two against each other.
POOLED_BIN_ORDER_4B = ("[0,.2)", "[.2,.4)", "[.4,.6)", "[.6,.8)", "[.8,1]")

# FREEZE NB-2: design §5 S1's "WITH the per-index table S3 rising"
# made EXACT -- the design doc names the conjunct without a rule, and
# S1's reading label is printed in VERDICT.txt, so the rule is fixed
# here rather than left to the reader. RISING means: at least two of
# `POOLED_BIN_ORDER_4B`'s bins carry draws (n > 0 and a non-None
# mean), and the LAST such bin's pooled mean of placebo phi exceeds
# the FIRST such bin's by more than `S1_SHAPE_TOL_4B` (.05, design
# §5's own tolerance for the same-shape comparison -- §5 names no
# second one). Monotonicity across every non-empty bin is printed
# beside it as `bins_nondecreasing`, descriptive, never the rule: five
# bins estimated from at most |P_M| rungs are too coarse for a
# monotonicity test (design §4 (iii)).
S1_SHAPE_TOL_4B = 0.05


def s3_pooled_rising_4b(s3: dict) -> dict:
    """The `S1_SHAPE_TOL_4B` rule above, applied to `s3_shape_4b`'s
    `pooled_bins`. Returns `{"rising": bool | None, "first_bin",
    "last_bin", "delta", "n_bins_with_draws", "bins_nondecreasing",
    "tol", "rule"}`; `rising` is `None` (undecidable, never a silent
    False) when fewer than two bins carry draws."""
    bins = (s3 or {}).get("pooled_bins") or {}
    live = [(label, bins[label]) for label in POOLED_BIN_ORDER_4B
            if (bins.get(label) or {}).get("n") and bins[label].get("mean") is not None]
    out = {"n_bins_with_draws": len(live), "tol": S1_SHAPE_TOL_4B,
           "rule": ("rising = the last bin with draws exceeds the first by more than "
                    f"{S1_SHAPE_TOL_4B} (design §5 S1's conjunct, made exact at the freeze)")}
    if len(live) < 2:
        out.update({"rising": None, "first_bin": live[0][0] if live else None,
                    "last_bin": live[-1][0] if live else None, "delta": None,
                    "bins_nondecreasing": None})
        return out
    means = [rec["mean"] for _, rec in live]
    delta = float(means[-1] - means[0])
    out.update({"rising": bool(delta > S1_SHAPE_TOL_4B), "first_bin": live[0][0],
                "last_bin": live[-1][0], "delta": delta,
                "bins_nondecreasing": bool(all(b >= a for a, b in zip(means, means[1:])))})
    return out


def _full_pool_excess_4b(series: dict, flat: list) -> dict:
    """`analyze_4.trend_4`/`excess_4` over the FULL flat pool — the
    same construction a real cell's own phi uses (never leave-one-out:
    a real rising rung is not itself a member of the flat pool)."""
    steps = series["steps"]
    trend = an.trend_4(series["a"], flat, steps)
    return an.excess_4(series["a"], trend, steps)


def s4_scatter_ratio_4b(series_by_traj: dict, rung_sets: dict, cells: list) -> dict:
    """S4 (design §5, §4(i)): per trajectory, the RMS pre-clear-window
    increment of the real (rising) cells' excess (`np.diff(excess[
    rung][:c])`, full-flat-pool excess, grid indices strictly before
    the clear) against the RMS increment of the flat rungs' own
    leave-one-out excess over the whole grid — the two scatters S4
    exists to compare (design §4(i): a rising rung whose representation
    wobbles more between checkpoints than a flat rung's, for reasons
    unrelated to the lead, makes the placebo null too narrow).

    FREEZE NB-1 (the fix wave's own re-review; the final review's
    Important 3 mis-identified the comparator and its fix is REVERSED
    here). BOTH sides are target-OUTSIDE-pool: a rising rung is never
    a member of the flat pool that scores it, and a placebo rung is
    left out of its own leave-one-out pool. The two constructions
    therefore differ ONLY in pool SIZE -- n-1 rungs behind the flat
    side's trend, n behind the rising side's -- which at matched wobble
    scale sigma makes the RAW ratio's expectation
    sqrt((sigma^2 + sigma^2/n) / (sigma^2 (1 + 1/(n-1)))) =
    sqrt(1 - 1/n^2), i.e. 1 to within 1/(2n^2): 0.07% at n = 27, 0.26%
    at n = 14. The fix wave divided the flat side by n/(n-1) on the
    reading that it was self-included; it is not, so the division
    INVERTED the bias -- inflating the ratio by 3.8-7.4% at this
    battery's flat-pool sizes (27/16/14/16), in the direction design
    §4(i) reads as "the rising rungs wobble more, so the placebo null
    is too narrow and p_cal is anti-conservative". The division is
    dropped: `rms_flat` is the RAW leave-one-out RMS, and it is what
    `ratio` compares against. `rms_flat_loo` (the same quantity under
    its build-time name) and `loo_scale_factor` (n/(n-1)) stay as
    DISCLOSURE fields only -- nothing divides by them.

    Disclosed, not corrected for: (i) the residual pool-size mismatch,
    expectation sqrt(1 - 1/n^2) at matched scale, printed per
    trajectory as `pool_size_expected_ratio`; (ii) the rising side is
    read ONLY over each cell's pre-clear window (so no lead enters the
    comparison) while the flat side pools leave-one-out increments over
    the WHOLE grid -- the two scatters are windows of different length."""
    per_traj = {}
    pooled_rising, pooled_flat = [], []
    for t in sorted(series_by_traj):
        series = series_by_traj[t]
        a, steps, flat = series["a"], series["steps"], rung_sets[t]["flat"]
        excess = _full_pool_excess_4b(series, flat)
        n_flat = len(flat)
        loo_scale_factor = (n_flat / (n_flat - 1)) if n_flat > 1 else None

        rising_incs = []
        for rc in cells:
            if rc["traj"] != t:
                continue
            window = excess[rc["rung"]][:rc["t_clear_index"]]
            if len(window) > 1:
                rising_incs.extend(np.diff(window).tolist())

        flat_incs = []
        for f in flat:
            loo = loo_excess_4b(a, flat, steps, f)
            flat_incs.extend(np.diff(loo).tolist())

        rms_rising = float(np.sqrt(np.mean(np.square(rising_incs)))) if rising_incs else None
        rms_flat = float(np.sqrt(np.mean(np.square(flat_incs)))) if flat_incs else None
        # NB-1: the same quantity, kept under its build-time name as a
        # disclosure field -- `rms_flat` is no longer a rescale of it.
        rms_flat_loo = rms_flat
        ratio = (rms_rising / rms_flat) if (rms_rising is not None and rms_flat) else None
        expected = (float(np.sqrt(1.0 - 1.0 / (n_flat ** 2))) if n_flat > 1 else None)
        per_traj[t] = {"rms_rising": rms_rising, "rms_flat": rms_flat,
                       "rms_flat_loo": rms_flat_loo, "loo_scale_factor": loo_scale_factor,
                       "pool_size_expected_ratio": expected,
                       "ratio": ratio,
                       "n_rising_increments": len(rising_incs), "n_flat_increments": len(flat_incs)}
        pooled_rising.extend(rising_incs)
        pooled_flat.extend(flat_incs)

    rms_rising_p = float(np.sqrt(np.mean(np.square(pooled_rising)))) if pooled_rising else None
    rms_flat_p = float(np.sqrt(np.mean(np.square(pooled_flat)))) if pooled_flat else None
    ratio_p = (rms_rising_p / rms_flat_p) if (rms_rising_p is not None and rms_flat_p) else None
    return {"per_traj": per_traj,
            "pooled": {"rms_rising": rms_rising_p, "rms_flat": rms_flat_p, "ratio": ratio_p},
            "compared": S4_COMPARED_NOTE_4B}


def _lag1_autocorr_4b(x: np.ndarray):
    x = np.asarray(x, dtype=np.float64)
    if len(x) < 3:
        return None
    x0, x1 = x[:-1], x[1:]
    if np.std(x0) == 0.0 or np.std(x1) == 0.0:
        return None
    return float(np.corrcoef(x0, x1)[0, 1])


def s5_autocorr_4b(series_by_traj: dict, rung_sets: dict) -> dict:
    """S5 (design §5): lag-1 autocorrelation of the flat rungs'
    leave-one-out excess increments, per rung and pooled per
    trajectory two ways — the simple (Fisher-free) mean of the
    per-rung correlations, and the correlation computed once over
    every rung's (increment, next-increment) pairs concatenated."""
    out = {}
    for t in sorted(series_by_traj):
        series = series_by_traj[t]
        a, steps, flat = series["a"], series["steps"], rung_sets[t]["flat"]
        per_rung, all_x0, all_x1 = {}, [], []
        for f in flat:
            inc = np.diff(loo_excess_4b(a, flat, steps, f))
            per_rung[f] = _lag1_autocorr_4b(inc)
            if len(inc) >= 2:
                all_x0.extend(inc[:-1].tolist())
                all_x1.extend(inc[1:].tolist())
        valid = [r for r in per_rung.values() if r is not None]
        mean_rho = float(np.mean(valid)) if valid else None
        if len(all_x0) >= 2 and np.std(all_x0) > 0 and np.std(all_x1) > 0:
            pooled_rho = float(np.corrcoef(all_x0, all_x1)[0, 1])
        else:
            pooled_rho = None
        out[t] = {"per_rung": per_rung, "mean_of_rungs": mean_rho, "pooled": pooled_rho,
                  "n_rungs": len(flat)}
    return out


def s8_curves_4b(series_by_traj: dict, rung_sets: dict, cells: list, pools: dict,
                 batteries: dict) -> dict:
    """S8 (design §5): per real cell, the placebo quantile of
    `x_r(t_i)/x_r(t_end)` at every grid index i strictly before the
    clear — a curve, not one number — against the placebo cells the
    batteries actually assigned that SAME (trajectory, c), evaluated
    at the SAME i (share at or below)."""
    drawn: dict = {}
    for battery_cells in batteries["cells"]:
        for bc in battery_cells:
            drawn.setdefault((bc["traj"], bc["c"]), []).append(bc["rung"])

    out = []
    for rc in cells:
        t, rung, c = rc["traj"], rc["rung"], rc["t_clear_index"]
        series = series_by_traj[t]
        flat = rung_sets[t]["flat"]
        excess = _full_pool_excess_4b(series, flat)
        x_r = excess[rung]
        x_end = x_r[-1]
        rungs_drawn = drawn.get((t, c), [])
        curve = []
        for i in range(c):
            val_obs = (x_r[i] / x_end) if x_end else None
            null_vals = []
            for f in rungs_drawn:
                fx = pools[t][f]["excess"]
                f_end = fx[-1]
                if f_end:
                    null_vals.append(fx[i] / f_end)
            if val_obs is None or not null_vals:
                quantile = None
            else:
                quantile = float(np.mean(np.asarray(null_vals) <= val_obs))
            curve.append({"i": i, "value": val_obs, "quantile": quantile, "n_null": len(null_vals)})
        out.append({"traj": t, "rung": rung, "c": c, "curve": curve})
    return out
