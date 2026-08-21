"""Exp 2d statistics (design §5.1–§5.3, §6): pure functions, no I/O.

- the significance bar: one-sided exact binomial against the rung's
  majority-answer floor at α = .01, applied IDENTICALLY to the outcome
  (argmax accuracy over 500 items) and the predictor (sampled rate
  over 32,000 draws);
- the corrected margin max(0, x − c)/(1 − c), zero below the bar;
- the primary: AUC of the predictor score between rising and
  non-rising rungs, under 2c's EXACT FAMILY-BLOCK PERMUTATION GROUP
  (`experiments/exp2c/run/power_table`: enumerated below the 5e6
  guard, 100,000 seeded draws above it; blocks of same-size families
  exchanged position-for-position, x fixed to rung identity) with the
  AUC as the statistic in place of 2c's Spearman ρ — the generators,
  routing and p-value conventions are IMPORTED, never copied;
- the falsifier: 2c's family-cluster bootstrap (10,000 seeded
  resamples of families with replacement, percentile 95% CI), with
  undefined resamples DROPPED AND COUNTED (fix i), never imputed .5;
- the verdict tree (§6), mechanical, callable without a tree on disk
  so the power procedure can run the very same code.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, rankdata, spearmanr

EXP2D = Path(__file__).resolve().parent
if str(EXP2D.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2D.parent.parent))

from experiments.exp2c.run import power_table as pt2c  # noqa: E402

ALPHA = 0.01                 # §5.1/§5.2/§5.3: 2c's level, every bar
AUC_BAR = 0.75               # §6 PASS: AUC ≥ .75 (ruling d)
N_BOOT = 10_000              # §5.3: 2c's resample count
PERM_SAMPLE = 100_000        # §5.3: 2c's sampled-draw count above the guard
PERM_SEED = 0                # 2c's exact_block_p default seed
BOOT_SEED = 0                # 2c's verdict(seed=0)
CP_LEVEL = 0.95


# ------------------------------------------------------------ the bar

def clopper_pearson(k: int, n: int, level: float = CP_LEVEL) -> tuple:
    from scipy.stats import beta
    a = 1.0 - level
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi


def binomial_bar(k: int, n: int, floor: float, alpha: float = ALPHA) -> dict:
    """One-sided exact binomial: P(X ≥ k | n, p = floor). Significant
    iff p < alpha AND the observed rate exceeds the floor."""
    k, n = int(k), int(n)
    if n <= 0 or k < 0 or k > n:
        raise ValueError(f"binomial_bar: k={k}, n={n}")
    if not (0.0 < floor < 1.0):
        raise ValueError(f"binomial_bar: floor {floor} must lie in (0, 1)")
    p = float(binomtest(k, n, floor, alternative="greater").pvalue)
    rate = k / n
    return {"k": k, "n": n, "rate": rate, "p": p,
            "significant": bool(p < alpha and rate > floor)}


def corrected_margin(k: int, n: int, floor: float,
                     alpha: float = ALPHA) -> dict:
    """§5.1/§5.2: max(0, x − c)/(1 − c), zeroed unless x clears c by
    the binomial bar. Never negative. CP bound rides on every cell."""
    bar = binomial_bar(k, n, floor, alpha)
    m = (bar["rate"] - floor) / (1.0 - floor) if bar["significant"] else 0.0
    lo, hi = clopper_pearson(k, n)
    return {**bar, "floor": float(floor), "margin": float(max(0.0, m)),
            "cp95": [lo, hi]}


# ------------------------------------------------------------- the AUC

def auc(x, y) -> float:
    """Mann–Whitney AUC of x between y == 1 (rising) and y == 0, ties
    counted half (midranks): P(x1 > x0) + ½ P(x1 = x0). Undefined —
    ValueError — when either class is empty; callers that tolerate
    that (the bootstrap) test first."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=int)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError("auc: x and y must be equal-length 1-D")
    n1 = int(y.sum())
    n0 = int(len(y) - n1)
    if n1 == 0 or n0 == 0:
        raise ValueError(f"auc undefined: n_rising={n1}, n_flat={n0}")
    r = rankdata(x)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def auc_pairwise_matrix(x) -> np.ndarray:
    """S[i, j] = 1 if x_i > x_j, ½ if equal, 0 otherwise. The AUC of a
    multiset of rungs with counts c is (c·1[y=1])ᵀ S (c·1[y=0]) /
    (n1 n0) — the identity the bootstrap uses; `auc` and this agree
    exactly (fixture)."""
    x = np.asarray(x, dtype=float)
    gt = (x[:, None] > x[None, :]).astype(float)
    eq = (x[:, None] == x[None, :]).astype(float)
    return gt + 0.5 * eq


# --------------------------------------------- block permutation (2c's)

def block_perm_group(families, *, max_enumerate=pt2c.EXACT_PERM_GUARD,
                     n_sample=PERM_SAMPLE, seed=PERM_SEED) -> dict:
    """The permutation index matrix 2c's `exact_block_p` would use for
    this `families` vector — enumerated below the guard, else
    `sampled_block_perms` at `n_sample` draws from
    `np.random.default_rng(seed)` — together with the routing label.
    Generated ONCE and reused (the power procedure runs thousands of
    tests on the same group)."""
    families = [int(f) for f in families]
    _, _, group_items = pt2c._block_perm_offsets(families)
    total = pt2c._block_perm_total(group_items)
    if total <= max_enumerate:
        perms = pt2c.exact_block_perms(families)
        return {"perms": perms, "method": "enumerated",
                "group_size": int(total)}
    rng = np.random.default_rng(seed)
    perms = pt2c.sampled_block_perms(families, n_sample, rng)
    return {"perms": perms, "method": "sampled", "group_size": int(total)}


def _auc_over_perms(x, y, perms) -> tuple:
    """AUC for every block-permuted label vector y[perm], x fixed.
    Midranks of x are permutation-invariant, so AUC_perm =
    (rank_x · y[perm] − n1(n1+1)/2) / (n1 n0): one gather + one
    matvec."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=int)
    n1 = int(y.sum())
    n0 = int(len(y) - n1)
    if n1 == 0 or n0 == 0:
        raise ValueError("block test undefined without both classes")
    r = rankdata(x)
    obs = float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))
    yp = y[perms]                                  # (n_perms, n)
    stats = (yp @ r - n1 * (n1 + 1) / 2) / (n1 * n0)
    return obs, stats


def block_perm_auc_p(x, y, families, group=None, **kw) -> dict:
    """§5.3: one-sided family-block permutation p for the AUC, PASS
    direction AUC > .5. Conventions are 2c's, per routing:
    enumerated → p = #{AUC_perm ≥ AUC_obs} / n_perms (row 0 is the
    identity, so the minimum is 1/n_perms); sampled → add-one,
    p = (1 + #{≥}) / (M + 1). Raises on a layout mismatch like 2c."""
    n = int(sum(families))
    if len(x) != n or len(y) != n:
        raise ValueError(
            f"block_perm_auc_p: sum(families)={n} but len(x)={len(x)}, "
            f"len(y)={len(y)} — arrays must be the family-contiguous "
            f"layout (2c's convention)")
    group = group or block_perm_group(families, **kw)
    perms = group["perms"]
    obs, stats = _auc_over_perms(x, y, perms)
    count = int(np.sum(stats >= obs))
    if group["method"] == "enumerated":
        p = count / perms.shape[0]
        n_perms = int(perms.shape[0])
        res = 1.0 / n_perms
    else:
        p = (1 + count) / (perms.shape[0] + 1)
        n_perms = int(perms.shape[0])
        res = 1.0 / (n_perms + 1)
    return {"auc_obs": obs, "p": float(p), "count_ge": count,
            "n_perms": n_perms, "resolution": res,
            "method": group["method"], "group_size": group["group_size"]}


def spearman_block_p(x, y, families) -> dict:
    """2c's `exact_block_p` verbatim (the secondary's ordering test)."""
    return pt2c.exact_block_p(np.asarray(x, float), np.asarray(y, float),
                              [int(f) for f in families])


# ----------------------------------------------- family-cluster bootstrap

def bootstrap_counts_matrix(n_fam: int, n_boot: int = N_BOOT,
                            seed: int = BOOT_SEED) -> np.ndarray:
    """(n_boot, n_fam) integer counts: resample b draws
    `rng.choice(n_fam, size=n_fam, replace=True)` — 2c's loop, in 2c's
    draw order from `np.random.default_rng(seed)` — and counts how
    many times each family was picked."""
    rng = np.random.default_rng(seed)
    out = np.zeros((n_boot, n_fam), dtype=np.int64)
    for b in range(n_boot):
        pick = rng.choice(n_fam, size=n_fam, replace=True)
        np.add.at(out[b], pick, 1)
    return out


def family_membership(family_labels) -> tuple:
    """(sorted family list, (n_fam, n_rung) 0/1 membership matrix) —
    2c's `sorted(fams)` ordering for the bootstrap."""
    fams = sorted(set(family_labels))
    idx = {f: i for i, f in enumerate(fams)}
    M = np.zeros((len(fams), len(family_labels)), dtype=np.int64)
    for j, f in enumerate(family_labels):
        M[idx[f], j] = 1
    return fams, M


def cluster_bootstrap_auc(x, y, family_labels, *, counts=None,
                          n_boot=N_BOOT, seed=BOOT_SEED) -> dict:
    """§5.3 falsifier: percentile 95% CI of the AUC over family
    resamples. A resample whose rungs carry no rising or no non-rising
    rung leaves AUC undefined and is DROPPED AND COUNTED (fix i). The
    AUC of a resample is computed from rung multiplicities through the
    pairwise matrix — exactly the midrank AUC of the expanded multiset
    (fixture-proved)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=int)
    fams, M = family_membership(family_labels)
    C = bootstrap_counts_matrix(len(fams), n_boot, seed) \
        if counts is None else counts
    rc = C @ M                                   # (n_boot, n_rung) rung counts
    c1 = rc * (y == 1)[None, :]
    c0 = rc * (y == 0)[None, :]
    n1 = c1.sum(1)
    n0 = c0.sum(1)
    valid = (n1 > 0) & (n0 > 0)
    S = auc_pairwise_matrix(x)
    num = np.einsum("bi,ij,bj->b", c1[valid].astype(float), S,
                    c0[valid].astype(float))
    aucs = num / (n1[valid] * n0[valid])
    n_valid = int(valid.sum())
    n_dropped = int(len(valid) - n_valid)
    if n_valid == 0:
        return {"ci": [None, None], "n_valid": 0, "n_dropped": n_dropped,
                "n_boot": int(len(valid))}
    return {"ci": [float(np.percentile(aucs, 2.5)),
                   float(np.percentile(aucs, 97.5))],
            "n_valid": n_valid, "n_dropped": n_dropped,
            "n_boot": int(len(valid)), "boot_mean": float(aucs.mean())}


def cluster_bootstrap_spearman(x, y, family_labels, *, n_boot=N_BOOT,
                               seed=BOOT_SEED) -> dict:
    """2c's bootstrap for the ρ secondary, with the drops COUNTED (2c
    dropped silently when x or y was constant in a resample)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    fams = sorted(set(family_labels))
    idx_of = {f: [i for i, g in enumerate(family_labels) if g == f]
              for f in fams}
    rng = np.random.default_rng(seed)
    boots, dropped = [], 0
    for _ in range(n_boot):
        pick = rng.choice(len(fams), size=len(fams), replace=True)
        ii = [i for k in pick for i in idx_of[fams[k]]]
        if len(set(x[ii])) > 1 and len(set(y[ii])) > 1:
            boots.append(float(spearmanr(x[ii], y[ii]).statistic))
        else:
            dropped += 1
    if not boots:
        return {"ci": [None, None], "n_valid": 0, "n_dropped": dropped,
                "n_boot": n_boot}
    return {"ci": [float(np.percentile(boots, 2.5)),
                   float(np.percentile(boots, 97.5))],
            "n_valid": len(boots), "n_dropped": dropped, "n_boot": n_boot}


# ------------------------------------------------------------ the tree

WORLDS = ("INSUFFICIENT_DATA", "FAIL", "PASS", "INDETERMINATE")


def verdict_tree(*, gate1_diff_cells, auc_obs, block_p, ci,
                 alpha=ALPHA, auc_bar=AUC_BAR) -> dict:
    """§6, mechanical precedence: gate-1 diff → INSUFFICIENT_DATA;
    CI includes .5 → FAIL; block p < α AND AUC ≥ bar → PASS; else
    INDETERMINATE. No power branch (ruling c)."""
    if gate1_diff_cells:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": f"gate 1: the production-path seed-0 streams "
                          f"differ from exp3's committed bytes in "
                          f"{len(gate1_diff_cells)} cell(s): "
                          f"{sorted(gate1_diff_cells)}"}
    lo, hi = ci
    if lo is None or hi is None:
        raise ValueError("verdict_tree: the bootstrap CI is undefined "
                         "(no valid resample) — not a verdict")
    if lo <= 0.5 <= hi:
        return {"verdict": "FAIL",
                "reason": f"family-cluster bootstrap 95% CI on AUC "
                          f"[{lo:.4f}, {hi:.4f}] includes .5"}
    if block_p < alpha and auc_obs >= auc_bar:
        return {"verdict": "PASS",
                "reason": f"block p {block_p:.6g} < {alpha} and AUC "
                          f"{auc_obs:.4f} ≥ {auc_bar}"}
    return {"verdict": "INDETERMINATE",
            "reason": f"CI [{lo:.4f}, {hi:.4f}] excludes .5 but block p "
                      f"{block_p:.6g} / AUC {auc_obs:.4f} do not meet "
                      f"p < {alpha} and AUC ≥ {auc_bar}"}


def primary_test(x, y, families, family_labels, *, group=None,
                 counts=None) -> dict:
    """AUC + block p + cluster CI for one (predictor, label) pair in
    the family-contiguous layout. `group`/`counts` let a caller reuse
    the permutation matrix and bootstrap draws (power)."""
    a = auc(x, y)
    block = block_perm_auc_p(x, y, families, group=group)
    boot = cluster_bootstrap_auc(x, y, family_labels, counts=counts)
    return {"auc": a, "block": block, "bootstrap": boot,
            "n_rising": int(np.sum(np.asarray(y) == 1)),
            "n_flat": int(np.sum(np.asarray(y) == 0))}
