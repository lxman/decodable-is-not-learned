"""The Exp 2b Stage-1 instrument: basis-starved linear probes (design §3).

A NEW function, per the never-edit rule on Exp 1's frozen signature library:
the frozen `probe_below_threshold` draws its own random split and cannot take
a caller-supplied group split. This module mirrors its estimator pipeline
verbatim (StandardScaler + LogisticRegression, C=1.0, max_iter=100 — the
ledgered Exp 2 compute revision carries over) and reuses the frozen stats
primitives UNCHANGED via the exp1-alias loader: `permutation_null` (which
already returns the null SD needed for the gate floor-signature check),
`bonferroni`, and `clopper_pearson`.

The split is the capability's starving split (splits.py), deterministic per
seed. The permutation null permutes labels over ALL items under the FIXED
split — under H0 (no X↔y association) labels are exchangeable, so the test is
exact regardless of the split's structure; a lookup strategy is starved in the
observed fit and in every permuted fit alike.

present  iff Bonferroni-corrected permutation p < alpha (0.01) on the starved
         validation set. Margin = (acc − null_mean)/(1 − null_mean), zeroed
         below the bar (design §3, carried from Exp 2).
"""

from __future__ import annotations

import importlib.util
import sys
import warnings
from pathlib import Path

import numpy as np

from splits import SplitParams, starving_split

_SIG_DIR = Path(__file__).resolve().parent.parent / "exp1" / "signatures"
_ALIAS = "exp1_signatures"

if _ALIAS not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        _ALIAS, _SIG_DIR / "__init__.py",
        submodule_search_locations=[str(_SIG_DIR)])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules[_ALIAS] = pkg
    spec.loader.exec_module(pkg)

_stats = importlib.import_module(f"{_ALIAS}.stats")
permutation_null = _stats.permutation_null
bonferroni = _stats.bonferroni
clopper_pearson = _stats.clopper_pearson

C = 1.0
MAX_ITER = 100     # ledgered Exp 2 revision (291ec9c): true fits converge by 92
ALPHA = 0.01
N_PERM = 2500      # add-one floor x Bonferroni family < alpha (family <= 18)


def _make_starved_scorer(X, train_idx, val_idx):
    """fit_fn(X, y) -> starved-validation accuracy on the FIXED split (observed
    and null fits share it; only labels differ). Mirrors the frozen module's
    scaler-inside-the-split discipline."""
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    def fit_fn(_X, y):
        y = np.asarray(y)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            clf = make_pipeline(StandardScaler(),
                                LogisticRegression(C=C, max_iter=MAX_ITER))
            clf.fit(X[train_idx], y[train_idx])
        return float((clf.predict(X[val_idx]) == y[val_idx]).mean())
    return fit_fn


def probe_starved(
    activations: dict[tuple[int, int], np.ndarray],
    labels,
    bases: list[tuple],
    *,
    split_params: SplitParams,
    checkpoint_id: str,
    alpha: float = ALPHA,
    n_perm: int = N_PERM,
    seed: int,
) -> dict:
    """Fit starved probes over all (layer, token) candidates; test significance.

    Returns a plain dict (this module owns its schema; nothing frozen is
    edited): present, accuracy, chance (majority class of the starved val set),
    null_p (corrected), null_mean, null_std, margin, best_layer/best_token,
    n_candidates, split (n_train/n_val/n_dropped/held_per_component), ci95.
    """
    if not activations:
        raise ValueError("activations map is empty")
    labels = np.asarray(labels)
    train_idx, val_idx, split_info = starving_split(
        bases, labels, seed, split_params)
    n_val = len(val_idx)
    keys = sorted(activations.keys())

    accs, raw_ps, null_means, null_stds = [], [], [], []
    for i, key in enumerate(keys):
        X = activations[key]
        if X.shape[0] != len(labels):
            raise ValueError(f"activations{key}: {X.shape[0]} rows vs "
                             f"{len(labels)} labels")
        fit_fn = _make_starved_scorer(X, train_idx, val_idx)
        p, null_mean, null_std = permutation_null(
            fit_fn, X, labels, n_perm=n_perm, seed=seed + i)
        accs.append(fit_fn(X, labels))
        raw_ps.append(p)
        null_means.append(null_mean)
        null_stds.append(null_std)

    corrected = bonferroni(raw_ps)
    best = min(range(len(keys)), key=lambda i: (corrected[i], -accs[i]))
    best_layer, best_token = keys[best]
    acc = accs[best]
    ci95 = clopper_pearson(int(round(acc * n_val)), n_val)

    counts = {}
    for lbl in labels[val_idx]:
        counts[lbl] = counts.get(lbl, 0) + 1
    chance = max(counts.values()) / n_val

    present = bool(corrected[best] < alpha)
    margin = 0.0
    if present:
        margin = (acc - null_means[best]) / max(1e-9, 1.0 - null_means[best])

    return {
        "present": present, "accuracy": acc, "chance": chance,
        "null_p": corrected[best], "null_mean": null_means[best],
        "null_std": null_stds[best], "margin": margin,
        "best_layer": int(best_layer), "best_token": int(best_token),
        "n_candidates": len(keys), "ci95": list(ci95),
        "split": split_info, "checkpoint_id": checkpoint_id, "seed": seed,
    }
