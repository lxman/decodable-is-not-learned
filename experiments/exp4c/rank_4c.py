# experiments/exp4c/rank_4c.py
"""Experiment 4c's preregistered statistic (design `experiment-4c-
design.md` §3.3-§3.6, §5 S1/S3/S5/S7; plan Task 2): a rising task's
pre-clear alignment growth ranked among every never-performing (flat)
task's growth at the SAME checkpoint — no ratio, no eligibility
screen, null mean exactly 1/2, null data-free (`q_cell_4c`); cells
built from a run's own rung sets (`cells_4c`); the pooled mean
(`U_4c`); the exact family- and rung-block sign-flip primary
(`block_flip_4c`); the family-clustered bootstrap CI
(`cluster_bootstrap_ci_4c`); the rung-coupled placebo null and its own
alpha_placebo (`placebo_4c`); the arithmetic/non-arithmetic type
modifier (`type_modifier_4c`); the calibration read against the
placebo (`calibration_read_4c`); the four-world tree (`verdict_tree_
4c`); the named secondaries S3 (`window_mean_cells_4c`), S5 (`within_
riser_4c`), S7 (`never_performing_type_check_4c`); the site-0-excluded
alignment series (`alignment_series_4c`); and the design session's
known-answer reproduction plus its site-0 invariance check
(`discovery_set_4c`).

Pure numpy: no torch, no network, no model contact anywhere in this
module, and nothing here writes under `results/` — `discovery_set_4c`
READS Exp 4's committed tree (a closed experiment's git-tracked bytes)
but produces no artifact.

Everything under `experiments/exp2*`, `experiments/exp3*`,
`experiments/exp4/` and `experiments/exp4b/` is FROZEN: read, never
edited.

`block_flip_4c`'s `p_plus` and `p_minus` are the two one-sided tails of
the exact sign-flip distribution at the OBSERVED sum (Exp 4's
`primary_4` convention, `experiments/exp4/analyze_4.py`): `p_plus =
P(tot >= obs)`, `p_minus = P(tot <= obs)`; `p_minus < .05` is
`verdict_tree_4c`'s REVERSED sub-cell — the rising tasks' pre-clear
growth sitting BELOW the flat pool's (design §3.4)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# The BLAS thread pool is sized when numpy is first imported, and a
# multi-threaded reduction is not bit-reproducible across processes
# (`analyze_4.py`'s, `placebo_4b.py`'s own rule) — pinned before numpy
# and before any `experiments.*` import that pulls numpy in
# transitively.
from experiments.exp4 import _threads_4  # noqa: E402,F401

import numpy as np  # noqa: E402

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import analyze_4 as a4  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402
from experiments.exp4c import battery_4c as bc  # noqa: E402

# --------------------------------------------------------------- constants

ALPHA_4C = 0.01
MARGINAL_4C = 0.05
MIN_CLEAR_INDEX_4C = 2
N_BOOT_4C = 10_000
B_PLACEBO_4C = 10_000
MAX_ENUMERATE_4C = 20
SEED_4C = 0
CAL_MULTIPLE_4C = 2.0
EXCLUDED_SITES_4C = (0,)

WORLDS_4C = ("INSUFFICIENT_DATA", "REPLICATES", "MARGINAL", "NOT-REPLICATED")
MODIFIERS_4C = ("TYPE-GENERAL", "TYPE-BOUND", "NEITHER")

# The design session's `ARITH` literal (`experiments/exp4c/
# design_session/03_rank_clustered_and_types.py`), copied verbatim.
# `discovery_set_4c` asserts this equals `RUNG_TYPE_4C`'s own
# arithmetic set rather than trusting the two never drift apart.
_DESIGN_SESSION_ARITH_4C = frozenset({
    "add3_mid", "sub3_mid", "add4_mid", "sub4_mid", "add_base8", "sub_base8",
    "arith_next", "quad_next", "count_div13", "count_div7", "median5", "median7",
    "oct2dec", "base7", "base12_digitsum", "base13", "mod13", "mod13_comp", "mod17",
    "mod19", "isqrt_gap", "collatz_step2", "roman_sum7", "clock24", "clock24_d999",
})


# ------------------------------------------------------------------- core

def q_cell_4c(g_r, g_flat) -> tuple:
    """The mid-rank quantile of `g_r` among the comparator pool
    `g_flat` — ties split at one-half, so a task tied with every
    comparator reads exactly 0.5 and the null mean is 1/2 with no
    correction. Raises on an empty pool (nothing to rank against)."""
    pool = np.asarray(list(g_flat), dtype=np.float64)
    if pool.size == 0:
        raise ValueError("q_cell_4c: empty comparator pool")
    below = int(np.sum(pool < g_r))
    ties = int(np.sum(pool == g_r))
    return float((below + 0.5 * ties) / pool.size), ties


def growth_4c(a_series) -> list:
    """`a[i] - a[0]` — alignment growth since the series' own first
    grid point (t_1), never the untrained twin."""
    a = [float(v) for v in a_series]
    return [v - a[0] for v in a]


def cells_4c(series_by_traj, rung_sets_by_traj, *, type_of=None, family_of=None,
             min_clear_index=MIN_CLEAR_INDEX_4C) -> list:
    """One cell per (trajectory, rising task) whose clear index is at
    least `min_clear_index` (index 0/1 has no non-trivial pre-clear
    window): `q` = the rising task's growth at t_minus_index = c-1
    ranked among the run's flat pool at the SAME index; `q_arith` is
    the same reading against the flat pool restricted to arithmetic
    tasks, computed only for an arithmetic rising task with a
    non-empty arithmetic-flat pool (`None` otherwise — never a
    non-arithmetic cell's business). A rung with no `t_clear` (never
    actually cleared, despite being listed rising) is skipped; there
    is no window to read."""
    type_of = type_of or bc.RUNG_TYPE_4C
    family_of = family_of or bc.FAMILY_OF
    out = []
    for traj in sorted(series_by_traj):
        s, rs = series_by_traj[traj], rung_sets_by_traj[traj]
        steps = list(s["steps"])
        g = {r: growth_4c(s["a"][r]) for r in s["a"]}
        flat = sorted(rs["flat"])
        flat_ar = [f for f in flat if type_of[f] == "arithmetic"]
        for r in sorted(rs["R"]):
            tclear = rs["t_clear"].get(r)
            if tclear is None:
                continue
            c = steps.index(tclear)
            if c < min_clear_index:
                continue
            i = c - 1
            q, ties = q_cell_4c(g[r][i], [g[f][i] for f in flat])
            cell = {"traj": traj, "rung": r, "family": family_of[r], "type": type_of[r], "c": c,
                    "t_minus_index": i, "t_minus_step": steps[i], "q": q, "n_flat": len(flat),
                    "n_ties": ties, "q_arith": None, "n_flat_arith": len(flat_ar),
                    "n_ties_arith": None}
            if type_of[r] == "arithmetic" and flat_ar:
                qa, ta = q_cell_4c(g[r][i], [g[f][i] for f in flat_ar])
                cell["q_arith"], cell["n_ties_arith"] = qa, ta
            out.append(cell)
    return out


def U_4c(cells, key="q") -> float:
    """The pooled mean of `key` over cells that carry it (`q_arith` is
    `None` on non-arithmetic cells — `U_4c(cells, "q_arith")` reads the
    arithmetic stratum only, by construction)."""
    vals = [c[key] for c in cells if c.get(key) is not None]
    if not vals:
        raise ValueError(f"U_4c: no cells carry {key!r}")
    return float(np.mean(vals))


def block_flip_4c(cells, *, key="q", block="family") -> dict:
    """Exact enumeration of every sign flip of `(q - 1/2)` over the
    named block (family or rung) — never sampled; `block_flip_4c`
    refuses above `MAX_ENUMERATE_4C` blocks rather than degrade
    silently to a Monte Carlo estimate. `p_plus`/`p_minus` are the two
    one-sided tails at the observed sum (module docstring)."""
    cells = [c for c in cells if c.get(key) is not None]
    blocks = sorted({c[block] for c in cells})
    n = len(blocks)
    if n == 0:
        raise ValueError("block_flip_4c: no cells")
    if n > MAX_ENUMERATE_4C:
        raise ValueError(f"block_flip_4c: {n} blocks > MAX_ENUMERATE_4C — 4c enumerates "
                         f"exactly, never samples")
    idx = {b: i for i, b in enumerate(blocks)}
    sums = np.zeros(n)
    for c in cells:
        sums[idx[c[block]]] += c[key] - 0.5
    m = 1 << n
    bits = (np.arange(m)[:, None] >> np.arange(n)[None, :]) & 1
    signs = (1 - 2 * bits).astype(np.int8)
    tot = signs @ sums
    obs = float(sums.sum())
    return {"n_blocks": n, "blocks": blocks, "n_flips": int(m), "method": "exact", "observed": obs,
            "block_sums": {b: float(sums[idx[b]]) for b in blocks},
            "p_plus": float(np.mean(tot >= obs - 1e-12)),
            "p_minus": float(np.mean(tot <= obs + 1e-12)),
            "resolution": 1.0 / m}


def cluster_bootstrap_ci_4c(cells, *, key="q", block="family", n_boot=N_BOOT_4C,
                             seed=SEED_4C) -> dict:
    """The family-clustered bootstrap CI95 of the pooled mean: each
    draw resamples BLOCKS with replacement (never individual cells),
    so a family with several cells moves as one unit. Deterministic in
    `seed`."""
    cells = [c for c in cells if c.get(key) is not None]
    blocks = sorted({c[block] for c in cells})
    vals = {b: np.array([c[key] for c in cells if c[block] == b]) for b in blocks}
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        pick = rng.integers(0, len(blocks), size=len(blocks))
        boots[i] = np.concatenate([vals[blocks[j]] for j in pick]).mean()
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"lo": float(lo), "hi": float(hi), "n_boot": int(n_boot), "n_blocks": len(blocks),
            "seed": int(seed)}


# ---------------------------------------------------------------- placebo

def placebo_4c(series_by_traj, rung_sets_by_traj, cells, *, B=B_PLACEBO_4C,
               seed=SEED_4C) -> dict:
    """The rung-coupled placebo null (design §3.4): each draw replaces
    every real rising task with a task drawn (with replacement) from
    the flat pool COMMON to every run, reads that placebo task at the
    SAME (traj, t_minus_index) the real cell used, and scores it
    against its own flat pool with itself removed — a placebo rung is
    a flat rung, so its own trend must exclude it. `alpha_placebo_01`/
    `_05` are `block_flip_4c`'s own false-positive rate on this null,
    measured in the run rather than assumed (4b's process note 3,
    applied in advance): `no_alpha_claim` marks that this placebo run
    is not itself a preregistered significance test. Also carries the
    non-arithmetic stratum's own placebo reading (design §3.5: "the
    non-arithmetic stratum's rung-level flip and its placebo p are
    printed as descriptives") — `U_b_nonarith` restricts each battery's
    mean to the placebo cells whose REAL cell is non-arithmetic (an
    all-NaN array when there are none); `U_nonarith`/`p_placebo_
    nonarith`/`n_nonarith_cells` are `None`/`None`/`0` in that case."""
    pool = sorted(set.intersection(*[set(rung_sets_by_traj[t]["flat"]) for t in series_by_traj]))
    if not pool:
        raise ValueError("placebo_4c: the flat pools share no task")
    g = {t: {r: growth_4c(series_by_traj[t]["a"][r]) for r in series_by_traj[t]["a"]}
         for t in series_by_traj}
    tasks = sorted({c["rung"] for c in cells})
    nonarith_idx = [j for j, c in enumerate(cells) if c["type"] != "arithmetic"]
    rng = np.random.default_rng(seed)
    U_b = np.empty(B)
    U_b_nonarith = np.full(B, np.nan)
    fires01 = np.zeros(B, bool)
    fires05 = np.zeros(B, bool)
    for b in range(B):
        draw = {r: pool[rng.integers(len(pool))] for r in tasks}
        pc = []
        for c in cells:
            f = draw[c["rung"]]
            i = c["t_minus_index"]
            flat = [h for h in rung_sets_by_traj[c["traj"]]["flat"] if h != f]
            q, _ = q_cell_4c(g[c["traj"]][f][i], [g[c["traj"]][h][i] for h in flat])
            pc.append({"family": c["family"], "rung": c["rung"], "type": c["type"], "q": q})
        U_b[b] = np.mean([p["q"] for p in pc])
        if nonarith_idx:
            U_b_nonarith[b] = np.mean([pc[j]["q"] for j in nonarith_idx])
        fl = block_flip_4c(pc)
        fires01[b] = fl["p_plus"] < ALPHA_4C
        fires05[b] = fl["p_plus"] < MARGINAL_4C
    U = U_4c(cells)
    na_real = [c for c in cells if c["type"] != "arithmetic"]
    U_nonarith = U_4c(na_real) if na_real else None
    p_placebo_nonarith = (float(np.mean(U_b_nonarith >= U_nonarith - 1e-12))
                          if na_real else None)
    return {"B": int(B), "seed": int(seed), "pool_common": pool, "n_pool": len(pool), "U_b": U_b,
            "null_mean": float(U_b.mean()), "null_sd": float(U_b.std(ddof=1)),
            "p_placebo": float(np.mean(U_b >= U - 1e-12)), "alpha_placebo_01": float(fires01.mean()),
            "alpha_placebo_05": float(fires05.mean()), "no_alpha_claim": True,
            "U_b_nonarith": U_b_nonarith, "U_nonarith": U_nonarith,
            "p_placebo_nonarith": p_placebo_nonarith, "n_nonarith_cells": len(na_real)}


# ------------------------------------------------------ modifier, tree

def type_modifier_4c(cells) -> dict:
    """Does the pooled signal generalise past arithmetic, or live only
    in the option/string tasks? `nonarith["p_family"]` is deliberately
    `None`: with as few as 3 non-arithmetic families the exact
    family-block null cannot resolve below the .05 bar (4b's process
    note 3), so no p is printed there — `p_rung_descriptive` is
    reported instead, labelled as carrying no alpha claim."""
    ar = [c for c in cells if c["type"] == "arithmetic" and c["q_arith"] is not None]
    na = [c for c in cells if c["type"] != "arithmetic"]
    out = {"arith": None, "nonarith": None, "modifier": None}
    if ar:
        fl = block_flip_4c(ar, key="q_arith")
        out["arith"] = {"U": U_4c(ar, "q_arith"), "n_cells": len(ar), "n_families": fl["n_blocks"],
                        "p_plus": fl["p_plus"], "p_minus": fl["p_minus"], "flip": fl}
    if na:
        fams = sorted({c["family"] for c in na})
        rf = block_flip_4c(na, block="rung")
        out["nonarith"] = {"U": U_4c(na), "n_cells": len(na), "n_families": len(fams),
                           "p_family": None,
                           "p_family_reason": f"{len(fams)} families give {1 << len(fams)} flips "
                                              f"— the null cannot resolve the .05 bar (4b process "
                                              f"note 3); no p printed",
                           "p_rung_descriptive": rf["p_plus"], "n_rungs": rf["n_blocks"],
                           "no_alpha_claim": True}
    if out["arith"] and out["arith"]["p_plus"] < MARGINAL_4C:
        out["modifier"] = "TYPE-GENERAL"
    elif out["nonarith"] and out["nonarith"]["U"] > 0.5:
        out["modifier"] = "TYPE-BOUND"
    else:
        out["modifier"] = "NEITHER"
    return out


def calibration_read_4c(placebo, world) -> dict:
    """`bounded` is True when alpha_placebo at the deciding bar EXCEEDS
    `CAL_MULTIPLE_4C` times that bar — the rule's measured false-
    positive rate is close enough to the bar that the licence sentence
    must say so (design §3.6)."""
    bar = ALPHA_4C if world == "REPLICATES" else MARGINAL_4C
    alpha = placebo["alpha_placebo_01"] if world == "REPLICATES" else placebo["alpha_placebo_05"]
    return {"deciding_bar": bar, "alpha_at_bar": float(alpha), "multiple": CAL_MULTIPLE_4C,
            "bounded": bool(alpha > CAL_MULTIPLE_4C * bar),
            "alpha_placebo_01": placebo["alpha_placebo_01"],
            "alpha_placebo_05": placebo["alpha_placebo_05"]}


def verdict_tree_4c(failures, primary) -> dict:
    """INSUFFICIENT_DATA on any named failure; else REPLICATES /
    MARGINAL / NOT-REPLICATED by `primary["p_plus"]` against `ALPHA_4C`
    / `MARGINAL_4C`, with a REVERSED sub-cell inside NOT-REPLICATED
    when `primary["p_minus"] < MARGINAL_4C` — the rising tasks' growth
    sitting below the flat pool's rather than above it (design §3.4)."""
    if failures:
        return {"verdict": "INSUFFICIENT_DATA", "reason": "; ".join(failures[:5]), "reversed": None}
    p, pm = primary["p_plus"], primary["p_minus"]
    if p < ALPHA_4C:
        return {"verdict": "REPLICATES", "reason": f"p+ {p:.4g} < {ALPHA_4C}", "reversed": False}
    if p < MARGINAL_4C:
        return {"verdict": "MARGINAL", "reason": f"{ALPHA_4C} <= p+ {p:.4g} < {MARGINAL_4C}",
                "reversed": False}
    return {"verdict": "NOT-REPLICATED",
            "reason": f"p+ {p:.4g} >= {MARGINAL_4C}" +
                      (f"; REVERSED: p- {pm:.4g} < {MARGINAL_4C}" if pm < MARGINAL_4C else ""),
            "reversed": bool(pm < MARGINAL_4C)}


# -------------------------------------------------------------------- S3

def window_mean_cells_4c(series_by_traj, rung_sets_by_traj, *, type_of=None, family_of=None,
                          min_clear_index=MIN_CLEAR_INDEX_4C) -> list:
    """S3: as `cells_4c`, but `q` (and `q_arith`) is the MEAN over
    every index i in 1..c-1 of the mid-rank quantile at i, rather than
    the single reading at t_minus_index = c-1 alone — does the primary
    depend on which pre-clear step happened to be read, or does the
    ranking hold across the whole pre-clear window? Each cell carries
    `n_window = c - 1`, the number of indices averaged (always >= 1,
    since `min_clear_index` >= 2)."""
    type_of = type_of or bc.RUNG_TYPE_4C
    family_of = family_of or bc.FAMILY_OF
    out = []
    for traj in sorted(series_by_traj):
        s, rs = series_by_traj[traj], rung_sets_by_traj[traj]
        steps = list(s["steps"])
        g = {r: growth_4c(s["a"][r]) for r in s["a"]}
        flat = sorted(rs["flat"])
        flat_ar = [f for f in flat if type_of[f] == "arithmetic"]
        for r in sorted(rs["R"]):
            tclear = rs["t_clear"].get(r)
            if tclear is None:
                continue
            c = steps.index(tclear)
            if c < min_clear_index:
                continue
            idxs = list(range(1, c))
            qs = [q_cell_4c(g[r][i], [g[f][i] for f in flat])[0] for i in idxs]
            cell = {"traj": traj, "rung": r, "family": family_of[r], "type": type_of[r], "c": c,
                    "n_window": len(idxs), "q": float(np.mean(qs)), "n_flat": len(flat),
                    "q_arith": None, "n_flat_arith": len(flat_ar)}
            if type_of[r] == "arithmetic" and flat_ar:
                qas = [q_cell_4c(g[r][i], [g[f][i] for f in flat_ar])[0] for i in idxs]
                cell["q_arith"] = float(np.mean(qas))
            out.append(cell)
    return out


# -------------------------------------------------------------------- S5

def within_riser_4c(series_by_traj, rung_sets_by_traj, *,
                     min_clear_index=MIN_CLEAR_INDEX_4C) -> dict:
    """S5: read at its own t_minus_index, is a rising task's growth
    high relative to the run's OTHER rising tasks that "have NOT yet
    cleared at t⁻" (design §5) — a task with clear index c2 has not
    yet cleared at index c-1 iff c2 >= c (design's binding rule; a
    co-clearing task, c2 == c, counts as a comparator too) — the
    within-run comparator pool the primary's flat-only construction
    never uses? A rung with zero such comparators (the last riser to
    clear with no co-clearer, or the only riser in R) contributes no
    `q_within` (`None`) and is excluded from `U_within`, but stays in
    `cells` for accounting."""
    cells = []
    for traj in sorted(series_by_traj):
        s, rs = series_by_traj[traj], rung_sets_by_traj[traj]
        steps = list(s["steps"])
        g = {r: growth_4c(s["a"][r]) for r in s["a"]}
        rung_c = {}
        for r in rs["R"]:
            tclear = rs["t_clear"].get(r)
            if tclear is None:
                continue
            rung_c[r] = steps.index(tclear)
        for r in sorted(rung_c):
            c = rung_c[r]
            if c < min_clear_index:
                continue
            i = c - 1
            comparators = sorted(r2 for r2, c2 in rung_c.items() if r2 != r and c2 >= c)
            if comparators:
                q, _ = q_cell_4c(g[r][i], [g[r2][i] for r2 in comparators])
            else:
                q = None
            cells.append({"traj": traj, "rung": r, "q_within": q, "n_comparators": len(comparators)})
    withc = [c["q_within"] for c in cells if c["q_within"] is not None]
    return {"cells": cells, "U_within": float(np.mean(withc)) if withc else None,
            "n_with_comparators": len(withc)}


# -------------------------------------------------------------------- S7

def never_performing_type_check_4c(series_by_traj, rung_sets_by_traj, *, type_of=None) -> dict:
    """S7: is "non-arithmetic, never performing" itself the split, a
    property of rung shape rather than of what fires? Each non-
    arithmetic FLAT task's growth, ranked among the run's arithmetic
    FLAT tasks (never-performing on both sides), at every grid index
    i >= 1, averaged over the grid. A run with no arithmetic flat
    pool contributes nothing (there is no comparator pool to rank
    against)."""
    type_of = type_of or bc.RUNG_TYPE_4C
    per_task_run = []
    for traj in sorted(series_by_traj):
        s, rs = series_by_traj[traj], rung_sets_by_traj[traj]
        steps = list(s["steps"])
        g = {r: growth_4c(s["a"][r]) for r in s["a"]}
        flat = rs["flat"]
        arith_flat = [f for f in flat if type_of[f] == "arithmetic"]
        nonarith_flat = [f for f in flat if type_of[f] != "arithmetic"]
        if not arith_flat:
            continue
        for f in sorted(nonarith_flat):
            qs = [q_cell_4c(g[f][i], [g[h][i] for h in arith_flat])[0] for i in range(1, len(steps))]
            per_task_run.append({"traj": traj, "rung": f, "mean_q": float(np.mean(qs)),
                                 "n_arith_flat": len(arith_flat), "n_grid": len(qs)})
    vals = [t["mean_q"] for t in per_task_run]
    return {"per_task_run": per_task_run, "mean": float(np.mean(vals)) if vals else None,
            "n_task_runs": len(per_task_run)}


# --------------------------------------------------------- alignment series

def alignment_series_4c(tables_by_step, ref_tables, *, steps, excluded_sites=EXCLUDED_SITES_4C) -> dict:
    """`analyze_4.alignment_series_4`'s construction with hidden state
    0 excluded before the mean over sites (the degenerate constant-
    token site Exp 4's own gate 0 excludes, campaign stop #1) — the
    site-0-excluded analogue of the design session's known series,
    used only to check the primary's invariance to that exclusion.
    Every overlap is RE-DERIVED from the committed set tables via
    `collect_4.overlap_table_4` and cross-checked against a stored
    `overlaps[ref][rung]` array when present, raising and naming the
    step/rung/ref/site on disagreement (`analyze_4._alignment_parts_4`'s
    rule) — never trusting the stored array alone. Raises if
    `excluded_sites` would drop the whole site family."""
    a = {r: [] for r in bc.RUNGS}
    a_by_ref: dict = {}
    per_item: dict = {}
    n_sites_kept = None
    for step in steps:
        unit = tables_by_step[step]
        rec = unit["record"]
        pairing_by_ref = rec["pairing"]
        sites = rec["sites"]
        keep = [i for i, s in enumerate(sites) if int(s) not in excluded_sites]
        if not keep:
            raise ValueError(f"alignment_series_4c: step {step}: excluded_sites "
                             f"{list(excluded_sites)!r} excludes the whole site family {sites!r}")
        n_sites_kept = len(keep)
        stored = unit.get("overlaps") or {}
        pooled_by_rung = {}
        for rung in bc.RUNGS:
            sm = unit["sets"][rung]
            per_ref_fracs = []
            for ref, pairing in pairing_by_ref.items():
                sq = ref_tables[ref][rung]
                ov = collect_4.overlap_table_4(sm, sq, pairing)
                stored_ov = (stored.get(ref) or {}).get(rung)
                if stored_ov is not None and not np.array_equal(stored_ov, ov):
                    diff_sites = np.flatnonzero(~np.all(stored_ov == ov, axis=1))
                    site0 = int(diff_sites[0]) if len(diff_sites) else -1
                    raise ValueError(f"alignment_series_4c: step {step}: {rung}/{ref}/site{site0}: "
                                     f"stored overlap disagrees with the re-derived value")
                frac = ov[keep].astype(np.float64) / metric_4.K_4
                per_ref_fracs.append(frac)
                block = a_by_ref.setdefault(ref, {r: [] for r in bc.RUNGS})
                block[rung].append(float(frac.mean()))
            pooled = np.stack(per_ref_fracs, axis=0).mean(axis=(0, 1))
            a[rung].append(float(pooled.mean()))
            pooled_by_rung[rung] = pooled
        per_item[step] = pooled_by_rung
    return {"steps": list(steps), "a": a, "a_by_ref": a_by_ref, "per_item": per_item,
            "n_sites_kept": n_sites_kept, "excluded_sites": list(excluded_sites)}


# --------------------------------------------------------------- discovery

def discovery_set_4c(root4=None) -> dict:
    """The design session's known-answer reproduction (`design_session/
    02_rank_pooled.py` + `03_rank_clustered_and_types.py`, on Exp 4's
    four committed trajectories, site 0 INCLUDED — `analyze_4.
    alignment_series_4`'s own construction, unchanged) plus the site-0-
    EXCLUDED invariance check (`alignment_series_4c` on the same
    committed bytes): does excluding the degenerate constant-token site
    move a single cell's `q`? Zero model contact — every input is a
    committed, git-tracked byte on a CLOSED experiment's tree."""
    root4 = root4 if root4 is not None else battery_4.EXP4
    design_arith = {r for r, t in a4.RUNG_TYPE_4.items() if t == "arithmetic"}
    if design_arith != set(_DESIGN_SESSION_ARITH_4C):
        raise ValueError("discovery_set_4c: RUNG_TYPE_4's arithmetic set has drifted from the "
                         "design session's ARITH literal")

    floors = bg.load_floors()
    battery = bt.load_battery()
    S_incl, S_excl, RS = {}, {}, {}
    for traj in battery_4.TRAJECTORIES_4:
        oc = battery_4.load_outcome_4(traj, battery=battery)
        rs = battery_4.rung_sets_4(oc, floors)
        RS[traj] = rs
        sweep = a4.load_sweep_tables_4(root4, traj)
        raw = collect_4.load_ref_tables_4(root4, battery_4.REFS_FOR_4[traj])
        ref_tables = {r: t["sets"] for r, t in raw.items()}
        s_incl = a4.alignment_series_4(root4, traj, ref_tables, sweep)
        s_excl = alignment_series_4c(sweep, ref_tables, steps=list(battery_4.GRID_4[traj]))
        S_incl[traj] = {"steps": s_incl["steps"], "a": s_incl["a"]}
        S_excl[traj] = {"steps": s_excl["steps"], "a": s_excl["a"]}

    cells_incl = cells_4c(S_incl, RS)
    cells_excl = cells_4c(S_excl, RS)

    U = U_4c(cells_incl)
    flip_family = block_flip_4c(cells_incl, block="family")
    flip_rung = block_flip_4c(cells_incl, block="rung")
    per_run = {}
    for traj in battery_4.TRAJECTORIES_4:
        sub = [c for c in cells_incl if c["traj"] == traj]
        per_run[traj] = U_4c(sub) if sub else None
    modifier = type_modifier_4c(cells_incl)

    by_key_incl = {(c["traj"], c["rung"]): c["q"] for c in cells_incl}
    by_key_excl = {(c["traj"], c["rung"]): c["q"] for c in cells_excl}
    common = sorted(set(by_key_incl) & set(by_key_excl))
    diffs = [abs(by_key_incl[k] - by_key_excl[k]) for k in common]
    n_ident = sum(1 for d in diffs if d <= 1e-12)

    return {
        "U": U, "n_cells": len(cells_incl),
        "p_family": flip_family["p_plus"], "p_rung": flip_rung["p_plus"],
        "per_run": per_run,
        "U_arith": modifier["arith"]["U"] if modifier["arith"] else None,
        "n_arith": modifier["arith"]["n_cells"] if modifier["arith"] else 0,
        "p_arith_family": modifier["arith"]["p_plus"] if modifier["arith"] else None,
        "U_nonarith": modifier["nonarith"]["U"] if modifier["nonarith"] else None,
        "n_nonarith": modifier["nonarith"]["n_cells"] if modifier["nonarith"] else 0,
        "family_sums": dict(flip_family["block_sums"]),
        # Task 4: S6 pools the discovery set's own cells with the
        # confirmation set's, so the per-cell table travels with the
        # record. Additive — `DISCOVERY_PIN_4C` and
        # `check_discovery_pins_4c` are untouched and compare the same
        # scalar fields they always did.
        "cells": cells_incl,
        "site0_excluded": {"n_cells_q_identical": n_ident,
                           "max_abs_q_diff": float(max(diffs)) if diffs else 0.0,
                           "n_common_cells": len(common)},
    }


# `discovery_set_4c()`, run once on the committed Exp 4 tree
# (`experiments/exp4c/PROGRESS.md`'s Task 2 entry has the printed
# output verbatim). `check_discovery_pins_4c` compares every entry
# exactly (`==`, no tolerance) — the pins are what a prior run actually
# printed, not a re-derived approximation.
DISCOVERY_PIN_4C = {
    "U": 0.6223702443940539,
    "n_cells": 42,
    "p_family": 0.0390625,
    "p_rung": 0.00922393798828125,
    "per_run": {
        "pythia_2.8b": 0.4867724867724868,
        "olmo2_7b": 0.6298076923076923,
        "smollm3_3b": 0.6938775510204083,
        "comma_7b": 0.6458333333333334,
    },
    "U_arith": 0.5102564102564103,
    "n_arith": 26,
    "p_arith_family": 0.453125,
    "U_nonarith": 0.7595486111111112,
    "n_nonarith": 16,
    "family_sums": {
        "antonym": 1.4027777777777777,
        "base_arith": -0.3773148148148148,
        "base_repr": -0.25,
        "clock": 0.5,
        "mid_digit": -0.2685185185185185,
        "odd_one_out": 1.4285714285714284,
        "order_stat": 0.1875,
        "reversal": 1.3214285714285716,
        "seq_extrap": 1.19510582010582,
    },
    "site0_excluded": {"n_cells_q_identical": 42, "max_abs_q_diff": 0.0},
}


def check_discovery_pins_4c(rec) -> list:
    """`[]` when every pinned field of `DISCOVERY_PIN_4C` matches `rec`
    exactly (floats by `==`, since both sides are the same deterministic
    computation on the same committed bytes)."""
    bad = []
    for key, want in DISCOVERY_PIN_4C.items():
        got = rec.get(key)
        if isinstance(want, dict):
            for sub_key, sub_want in want.items():
                sub_got = (got or {}).get(sub_key)
                if sub_got != sub_want:
                    bad.append(f"{key}.{sub_key}: {sub_got!r} != {sub_want!r}")
        else:
            if got != want:
                bad.append(f"{key}: {got!r} != {want!r}")
    return bad
