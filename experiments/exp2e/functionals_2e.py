"""Exp 2e functionals (design §5.1, §5.5, §6): pure functions, no I/O.

The predictor family is enumerated here and nowhere else — one
primary (F1) and three printed alternatives (F2, F3, B0) — on the
tally table 2d's frozen tier loader returns ({(rung, size):
{"verified", "n_draws", ...}}) and 2d's floor table. Every bar, the
AUC, the block-permutation group and the cluster bootstrap are 2d's
(`experiments/exp2d/stats_2d.py`), imported, never copied; the one
new statistical object is the PAIRED cluster bootstrap for
AUC(F1) − AUC(B0), whose single-arm marginals reproduce 2d's CI
exactly (fixture-proved).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

EXP2E = Path(__file__).resolve().parent
if str(EXP2E.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2E.parent.parent))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402

ALPHA = st.ALPHA          # ruling d: 2d's bars, the same objects
AUC_BAR = st.AUC_BAR
WORLDS = st.WORLDS

MAIN_DRAWS = 32_000       # 2d's main tier, per (rung, size)
PILOT_DRAWS = 4_000       # 2d's pilot tier


def eps_for(n_draws: int) -> float:
    """§5.1 / ruling c: the continuity constant is HALF A DRAW at the
    tier's own resolution, 1 / (2 n)."""
    n = int(n_draws)
    if n <= 0:
        raise ValueError(f"eps_for: n_draws {n_draws}")
    return 1.0 / (2 * n)


EPS_MAIN = eps_for(MAIN_DRAWS)      # 1 / 64,000
EPS_PILOT = eps_for(PILOT_DRAWS)    # 1 / 8,000
EPS_SENSITIVITY = (1 / 64_000, 1 / 32_000, 1 / 3_200)   # §5.5 (first = primary)


def _rate(cells, rung, size, n_draws) -> float:
    cell = cells[(rung, size)]
    if cell["n_draws"] != n_draws:
        raise ValueError(f"{rung}/{size}: n_draws {cell['n_draws']} against "
                         f"the tier's {n_draws}")
    return cell["verified"] / cell["n_draws"]


def _n_draws_of(cells, rungs, sizes) -> int:
    ns = {cells[(r, s)]["n_draws"] for r in rungs for s in sizes}
    if len(ns) != 1:
        raise ValueError(f"tier carries mixed n_draws {sorted(ns)}")
    return ns.pop()


# ------------------------------------------------------------------ F1

def log_excess(rate: float, floor: float, eps: float) -> float:
    """log((rate + ε) / floor): 0 at the floor (up to log(1 + ε/c)),
    positive above, negative below; log(ε / c) at zero draws."""
    if not (0.0 < floor < 1.0):
        raise ValueError(f"log_excess: floor {floor}")
    if eps <= 0:
        raise ValueError(f"log_excess: eps {eps}")
    return math.log((rate + eps) / floor)


def f1_table(cells, floors, *, rungs=bt.RUNGS, sizes=bt.PROBE_SIZES,
             eps=None, floor_key="floor") -> dict:
    """F1 (PRIMARY): mean over sizes of log((r_gs + ε) / c_g). ε
    defaults to half a draw at the tier's n_draws; `floor_key`
    'majority_floor' is the §5.5 ruling-k-undone sensitivity."""
    n = _n_draws_of(cells, rungs, sizes)
    e = eps_for(n) if eps is None else float(eps)
    out = {}
    for r in rungs:
        c = floors[r][floor_key]
        per = {s: log_excess(_rate(cells, r, s, n), c, e) for s in sizes}
        out[r] = {"per_size": per,
                  "score": float(sum(per.values()) / len(sizes)),
                  "floor": float(c), "eps": e}
    return out


# ------------------------------------------------------------------ F2

def f2_table(cells, *, rungs=bt.RUNGS, sizes=bt.PROBE_SIZES, eps=None) -> dict:
    """F2: mean over sizes of log(r_gs + ε). No floor."""
    n = _n_draws_of(cells, rungs, sizes)
    e = eps_for(n) if eps is None else float(eps)
    out = {}
    for r in rungs:
        per = {s: math.log(_rate(cells, r, s, n) + e) for s in sizes}
        out[r] = {"per_size": per,
                  "score": float(sum(per.values()) / len(sizes)), "eps": e}
    return out


# ------------------------------------------------------------------ B0

def b0_table(floors, *, rungs=bt.RUNGS, floor_key="floor") -> dict:
    """B0: −log c_g — the floor alone (§8's dumbest baseline)."""
    out = {}
    for r in rungs:
        c = floors[r][floor_key]
        if not (0.0 < c < 1.0):
            raise ValueError(f"b0: floor {c} for {r}")
        out[r] = {"score": float(-math.log(c)), "floor": float(c)}
    return out


# ------------------------------------------------------------------ F3

def f3_table(cells, floors, *, rungs=bt.RUNGS, sizes=bt.PROBE_SIZES,
             floor_key="floor") -> dict:
    """F3: the rank residual. R_g = midrank of the mean rate over
    sizes, Z_g = midrank of the floor; F3_g = R_g − (â + b̂ Z_g) with
    (â, b̂) the least-squares fit over the rungs given — the Spearman
    partial's residual, floor-adjusted without a functional form."""
    n = _n_draws_of(cells, rungs, sizes)
    mean_rate = np.array([sum(_rate(cells, r, s, n) for s in sizes) / len(sizes)
                          for r in rungs], dtype=float)
    floor = np.array([floors[r][floor_key] for r in rungs], dtype=float)
    R = rankdata(mean_rate)
    Z = rankdata(floor)
    A = np.column_stack([np.ones(len(rungs)), Z])
    coef, *_ = np.linalg.lstsq(A, R, rcond=None)
    resid = R - A @ coef
    out = {}
    for i, r in enumerate(rungs):
        out[r] = {"score": float(resid[i]), "mean_rate": float(mean_rate[i]),
                  "rank_rate": float(R[i]), "rank_floor": float(Z[i])}
    out_fit = {"intercept": float(coef[0]), "slope": float(coef[1])}
    for r in rungs:
        out[r]["fit"] = out_fit
    return out


# ------------------------------------------------------- paired bootstrap

def cluster_bootstrap_auc_paired(x1, x2, y, family_labels, *, counts=None,
                                 n_boot=st.N_BOOT, seed=st.BOOT_SEED) -> dict:
    """§5.4: AUC(x1) − AUC(x2) over the SAME family resamples (2d's
    counts matrix, 2c's draw order), undefined resamples dropped and
    counted as in 2d. The single-arm CIs are 2d's
    `cluster_bootstrap_auc` exactly (same counts, same arithmetic)."""
    x1 = np.asarray(x1, dtype=float)
    x2 = np.asarray(x2, dtype=float)
    y = np.asarray(y, dtype=int)
    fams, M = st.family_membership(family_labels)
    C = st.bootstrap_counts_matrix(len(fams), n_boot, seed) \
        if counts is None else counts
    rc = C @ M
    c1 = rc * (y == 1)[None, :]
    c0 = rc * (y == 0)[None, :]
    n1 = c1.sum(1)
    n0 = c0.sum(1)
    valid = (n1 > 0) & (n0 > 0)
    c1v = c1[valid].astype(float)
    c0v = c0[valid].astype(float)
    den = n1[valid] * n0[valid]
    a1 = np.einsum("bi,ij,bj->b", c1v, st.auc_pairwise_matrix(x1), c0v) / den
    a2 = np.einsum("bi,ij,bj->b", c1v, st.auc_pairwise_matrix(x2), c0v) / den
    n_valid = int(valid.sum())
    n_dropped = int(len(valid) - n_valid)
    obs = float(st.auc(x1, y) - st.auc(x2, y))
    if n_valid == 0:
        return {"ci_1": [None, None], "ci_2": [None, None],
                "ci_diff": [None, None], "diff_obs": obs,
                "n_valid": 0, "n_dropped": n_dropped, "n_boot": int(len(valid))}
    d = a1 - a2
    pct = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    return {"ci_1": pct(a1), "ci_2": pct(a2), "ci_diff": pct(d),
            "diff_obs": obs, "diff_boot_mean": float(d.mean()),
            "n_valid": n_valid, "n_dropped": n_dropped,
            "n_boot": int(len(valid))}


# ------------------------------------------------------------------ tree

def verdict_tree_2e(*, referent_failures, auc_obs, block_p, ci,
                    alpha=ALPHA, auc_bar=AUC_BAR) -> dict:
    """§6, mechanical precedence: any pinned referent failing →
    INSUFFICIENT_DATA; then 2d's tree verbatim (CI includes .5 →
    FAIL; block p < α AND AUC ≥ bar → PASS; else INDETERMINATE)."""
    if referent_failures:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": f"{len(referent_failures)} pinned referent(s) "
                          f"failed: {list(referent_failures)[:5]}"}
    return st.verdict_tree(gate1_diff_cells=[], auc_obs=auc_obs,
                           block_p=block_p, ci=ci, alpha=alpha,
                           auc_bar=auc_bar)


# ------------------------------------------------------- reduced layout

def drop_rungs_layout(dropped) -> tuple:
    """§5.5: the battery with `dropped` removed → (rungs kept, family
    sizes in 2d's family order, family labels) — 2d's
    `_restricted_layout` convention."""
    dropped = set(dropped)
    unknown = dropped - set(bt.RUNGS)
    if unknown:
        raise ValueError(f"drop_rungs_layout: not rungs: {sorted(unknown)}")
    kept = [r for r in bt.RUNGS if r not in dropped]
    fams = [bt.FAMILY_OF[r] for r in kept]
    order = list(dict.fromkeys(fams))
    sizes = [sum(1 for f in fams if f == fam) for fam in order]
    return kept, sizes, fams
