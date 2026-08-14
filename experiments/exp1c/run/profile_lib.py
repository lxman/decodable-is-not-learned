"""Runner logic for Experiment 1c, with no torch dependency.

Everything here has a decision in it, so it is testable without a checkpoint or
a GPU. The torch-dependent orchestration — building the language, loading the
checkpoint, collecting activations — lives in run_profile.py and calls these.

Nothing under experiments/exp1/ or experiments/exp1b/ is modified. The
checkpoint tree this reads was written by exp1's own run_lubana.py during the
1b campaign; 1c only reads it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from experiments.exp1.signatures.stats import permutation_null
from experiments.exp1c.records import LAYERS, TOKENS, SiteResult

EXP1B_DIR = Path(__file__).resolve().parents[2] / "exp1b"

# run_lubana.py:217 writes the sweep to checkpoints/lubana_s3graph_{mult}{suffix}
# and the scored rows to checkpoints/{system}{suffix}, where suffix is
# "_m{model_size}" for the 1M tier and empty for the base (10M) model
# (configs/lubana.py, ckpt_suffix).
_SUFFIX = {"1M": "_m1M", "10M": ""}


def stratified_subsample(entities, entity_class, per_class: int, *,
                         seed: int) -> np.ndarray:
    """`per_class` entities from each class, deterministic given the seed.

    Design §4: this is what holds n and class balance constant along the swept
    axis, so power cannot fall as the predicted effect rises. The count is
    asserted, never silently reduced — the margin at 40/class is ZERO at
    0.85 p_c (design open item 3), so a quiet fallback to 39 would reintroduce
    exactly the confound the subsample exists to remove.

    Determinism matters twice over: a cell and its twin must be scored on the
    identical rows, or the paired difference is not a floor comparison.
    """
    entities = np.asarray(entities)
    entity_class = np.asarray(entity_class)
    if entities.shape != entity_class.shape:
        raise ValueError(
            f"entities {entities.shape} and entity_class {entity_class.shape} "
            f"must describe the same pool")

    rng = np.random.default_rng(seed)
    picked = []
    for c in np.unique(entity_class):
        members = entities[entity_class == c]
        if members.size < per_class:
            raise ValueError(
                f"class {int(c)} has only {members.size} entities, below the "
                f"{per_class}/class quota — the stratified subsample cannot be "
                f"built and must not be silently shrunk")
        picked.append(rng.choice(members, size=per_class, replace=False))
    return np.sort(np.concatenate(picked))


def checkpoint_path(system: str, size: str, seed: int, *, step: int,
                    density: float | None = None,
                    root: str | Path = EXP1B_DIR) -> Path:
    """Locate one checkpoint in the tree the 1b campaign wrote."""
    if size not in _SUFFIX:
        raise ValueError(f"size must be one of {tuple(_SUFFIX)}, got {size!r}")
    if system == "sweep":
        if density is None:
            raise ValueError(
                "the sweep is indexed by density — a sweep checkpoint path "
                "without one would read an arbitrary graph")
        stem = f"lubana_s3graph_{density:g}"
    else:
        stem = system
    return (Path(root) / "checkpoints" / f"{stem}{_SUFFIX[size]}"
            / f"seed{seed}" / f"step_{step:07d}.pt")


def split_indices(n: int, val_frac: float, seed: int):
    """One split, shared by every site and by the twin.

    Mirrors exp1's signatures/probe.py:_split_indices exactly. It is restated
    here rather than imported so that a change to exp1's private helper cannot
    silently move 1c's split — exp1 is read-only and frozen under its tag, and
    a shared private function is a coupling this experiment does not want.
    """
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_val = max(1, int(round(n * val_frac)))
    return perm[n_val:], perm[:n_val]


def _val_scorer(X, train_idx, val_idx):
    def fit_fn(_X, y):
        y = np.asarray(y)
        clf = make_pipeline(StandardScaler(),
                            LogisticRegression(C=1.0, max_iter=1000))
        clf.fit(X[train_idx], y[train_idx])
        return float((clf.predict(X[val_idx]) == y[val_idx]).mean())
    return fit_fn


def probe_sites(activations, labels, *, seed: int, n_perm: int | None = None,
                val_frac: float = 0.25, return_n_val: bool = False):
    """Fit a linear probe at all 8 sites and keep every one of them.

    No argmax. The argmax collapse is what 1c exists to stop doing: it is
    biased upward, it discards which channel carried the signal, and it turns a
    profile into one bit.

    `n_perm=None` is the natural-n diagnostic arm — margins only, no null,
    which is the entire reason that arm costs 640 fits rather than 9.6 M.
    """
    labels = np.asarray(labels)
    n = len(labels)
    train_idx, val_idx = split_indices(n, val_frac, seed)

    out = []
    for i, key in enumerate(sorted(activations)):
        layer, token = key
        if layer not in LAYERS or token not in TOKENS:
            raise ValueError(f"site {key} is outside the frozen 8-site grid")
        X = np.asarray(activations[key])
        if X.shape[0] != n:
            raise ValueError(
                f"site {key} has {X.shape[0]} rows, labels has {n}")
        fit_fn = _val_scorer(X, train_idx, val_idx)
        acc = fit_fn(X, labels)
        if n_perm is None:
            p_raw, null_mean = None, None
        else:
            # The null shares this one fixed split, so observed and null differ
            # only in the labels, never in the partition.
            p_raw, null_mean, _ = permutation_null(
                fit_fn, X, labels, n_perm=n_perm, seed=seed + i)
        out.append(SiteResult(layer=layer, token=token, accuracy=acc,
                              null_p_raw=p_raw, null_mean=null_mean))
    return (out, len(val_idx)) if return_n_val else out
