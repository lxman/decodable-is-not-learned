"""Statistical primitives for the three-signature instrument.

Pure functions, no task/model imports. These are the load-bearing statistics the
preregistered decision rules (design doc §3–§4) are written in terms of:

- clopper_pearson : exact binomial CI. S2 "absent" is ALWAYS reported as the upper
  bound here, never as a claimed zero.
- permutation_null : label-permutation significance for the S1 probe.
- cohens_d        : magnitude-of-separation for the overall PASS bar (d >= 2).
- bonferroni      : multiple-comparison correction across probe layers.

Exp 2/3/4 import this module unchanged.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import beta


def clopper_pearson(passes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact (Clopper-Pearson) binomial confidence interval for a pass rate.

    Returns (lower, upper) at confidence 1 - alpha. The interval is exact via the
    Beta-distribution inversion, so it is valid at the tails where the normal
    approximation fails — including passes == 0, where the upper bound is a finite
    positive number. That upper bound is the "never a claimed zero" guarantee: a
    campaign that saw nothing still yields a numeric ceiling on the true rate.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not (0 <= passes <= n):
        raise ValueError("passes must be in [0, n]")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0, 1)")

    lower = 0.0 if passes == 0 else float(beta.ppf(alpha / 2, passes, n - passes + 1))
    upper = 1.0 if passes == n else float(beta.ppf(1 - alpha / 2, passes + 1, n - passes))
    return lower, upper


def permutation_null(
    fit_fn,
    X: np.ndarray,
    y: np.ndarray,
    *,
    n_perm: int = 1000,
    seed: int,
) -> tuple[float, float, float]:
    """Label-permutation significance test.

    fit_fn(X, y) -> float scores a fit (e.g. probe accuracy). We score once on the
    true labels, then n_perm times on shuffled labels to build the null. Returns
    (p, null_mean, null_std) where

        p = (1 + #{null >= observed}) / (n_perm + 1)

    the standard add-one estimator (p is never exactly 0, matching the essay's
    "never a claimed zero" discipline for the probe as well). null_mean should sit
    near chance for a signal-free readout.
    """
    if n_perm < 1:
        raise ValueError("n_perm must be >= 1")
    rng = np.random.default_rng(seed)
    y = np.asarray(y)

    observed = float(fit_fn(X, y))
    null = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        null[i] = float(fit_fn(X, rng.permutation(y)))

    p = (1.0 + np.count_nonzero(null >= observed)) / (n_perm + 1.0)
    return float(p), float(null.mean()), float(null.std(ddof=1)) if n_perm > 1 else 0.0


def cohens_d(a, b) -> float:
    """Pooled-SD standardized mean difference, d = (mean(a) - mean(b)) / s_pooled.

    Used for the overall PASS bar on the continuous signatures S1/S2: the grokking
    row and the Lubana-below row must separate at d >= 2 (design §4). Sign follows
    (a - b), so pass the resolution row as `a` to get a positive d in the predicted
    direction.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = a.size, b.size
    if na < 2 or nb < 2:
        raise ValueError("each group needs >= 2 observations for pooled SD")
    va, vb = a.var(ddof=1), b.var(ddof=1)
    pooled = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    if pooled == 0:
        # Identical spreads and identical means -> 0; separated means -> undefined.
        return 0.0 if a.mean() == b.mean() else float("inf")
    return float((a.mean() - b.mean()) / pooled)


def bonferroni(pvals) -> list[float]:
    """Bonferroni-correct a list of p-values across m comparisons (m = len(pvals)).

    Each corrected value is min(1, p * m). Applied across probe layers for S1.
    """
    pvals = list(pvals)
    m = len(pvals)
    if m == 0:
        return []
    return [min(1.0, float(p) * m) for p in pvals]
