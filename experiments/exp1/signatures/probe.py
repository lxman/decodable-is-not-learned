"""S1 — probeability below threshold.

Design doc §3 (S1) and §4 (decision rule), verbatim intent:

  Train a linear probe (logistic regression) on FROZEN residual-stream activations
  to predict the task-relevant target. Layer and token position selected on a
  validation split; chance baseline explicit; multiple-comparison correction across
  layers.

  present  iff probe accuracy beats a label-permutation null at p < 0.01
           (Bonferroni across layers) at a checkpoint with argmax test acc < 5%.
  absent   iff it fails that bar at every below-threshold checkpoint and layer.

  Predictions: grokking -> present; Lubana-below -> absent; Lubana-above -> present.

Operational choices (recorded in PROGRESS.md, frozen before result-grade data):
  - Multiple-comparison correction is Bonferroni across every (layer, token)
    CANDIDATE, not layers alone — token position is also selected, so it is part of
    the comparison family. This is stricter than layer-only correction (the design's
    brand rewards a strict-but-passed test).
  - The label-permutation null shares one fixed train/val split with the observed
    fit, so observed and null differ only in the labels, never in the split.
  - `below_threshold` (whether argmax test acc < 5% at this checkpoint) is supplied
    by the caller, which owns the task's argmax accuracy; `present` requires it.
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression

from .schema import ProbeResult
from .stats import bonferroni, clopper_pearson, permutation_null


def _split_indices(n: int, val_frac: float, seed: int):
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_val = max(1, int(round(n * val_frac)))
    return perm[n_val:], perm[:n_val]  # train_idx, val_idx


def _make_val_scorer(X: np.ndarray, train_idx, val_idx, C: float, max_iter: int):
    """Return fit_fn(X, y) -> validation accuracy on the fixed split.

    Closes over the fixed split so the label-permutation null (which permutes y) and
    the observed fit use identical train/val partitions.
    """
    def fit_fn(_X, y):
        y = np.asarray(y)
        # sklearn >=1.7 handles multinomial automatically; the multi_class arg was removed.
        clf = LogisticRegression(C=C, max_iter=max_iter)
        clf.fit(X[train_idx], y[train_idx])
        return float((clf.predict(X[val_idx]) == y[val_idx]).mean())
    return fit_fn


def probe_below_threshold(
    activations: dict[tuple[int, int], np.ndarray],
    labels,
    *,
    chance: float,
    checkpoint_id: str,
    below_threshold: bool = True,
    alpha: float = 0.01,
    n_perm: int = 1000,
    val_frac: float = 0.25,
    C: float = 1.0,
    max_iter: int = 1000,
    seed: int,
) -> ProbeResult:
    """Fit linear probes over all (layer, token) candidates and test significance.

    Parameters
    ----------
    activations : {(layer, token): np.ndarray[N, d]}
        As produced by ResidualActivationCollector.collect.
    labels : array[N]
        Task-relevant target (e.g. the answer class for modular arithmetic).
    chance : float
        Explicit chance baseline (1/113 for mod-113), recorded for the report.
    checkpoint_id : str
        Identifier of the checkpoint these activations came from.
    below_threshold : bool
        Whether this checkpoint has argmax test accuracy < 5% (caller-supplied).
        `present` requires it, per the design rule.
    alpha : float
        Significance bar (design: 0.01).

    Returns a ProbeResult; `present` is True iff the best candidate's Bonferroni-
    corrected permutation p < alpha AND below_threshold.
    """
    if not activations:
        raise ValueError("activations map is empty")
    labels = np.asarray(labels)
    n = len(labels)
    keys = sorted(activations.keys())
    train_idx, val_idx = _split_indices(n, val_frac, seed)
    n_val = len(val_idx)

    accs: list[float] = []
    raw_ps: list[float] = []
    null_means: list[float] = []
    for i, key in enumerate(keys):
        X = activations[key]
        if X.shape[0] != n:
            raise ValueError(f"activations{key} has {X.shape[0]} rows, labels has {n}")
        fit_fn = _make_val_scorer(X, train_idx, val_idx, C, max_iter)
        p, null_mean, _ = permutation_null(fit_fn, X, labels, n_perm=n_perm, seed=seed + i)
        accs.append(fit_fn(X, labels))  # observed val accuracy (true labels)
        raw_ps.append(p)
        null_means.append(null_mean)

    corrected = bonferroni(raw_ps)
    # Best candidate: smallest corrected p, tie-broken by highest accuracy.
    best = min(range(len(keys)), key=lambda i: (corrected[i], -accs[i]))
    best_layer, best_token = keys[best]
    acc = accs[best]
    correct = int(round(acc * n_val))
    ci95 = clopper_pearson(correct, n_val)

    present = bool(corrected[best] < alpha and below_threshold)
    return ProbeResult(
        present=present,
        accuracy=acc,
        chance=chance,
        null_p=corrected[best],
        null_mean=null_means[best],
        ci95=ci95,
        best_layer=best_layer,
        best_token=best_token,
        n_layers_tested=len(keys),
        checkpoint_id=checkpoint_id,
        below_threshold=below_threshold,
    )
