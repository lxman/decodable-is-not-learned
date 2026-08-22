"""Exp 2f probe rung (design §5): the same label the generators are
scored on, read from residual-stream activations with 2b's probe
(StandardScaler + logistic regression, C = 1, max_iter = 100 — the
constants imported, never copied), trained on ALL of a rung's
committed probe items and evaluated on its 500 eval items, at 2c's
candidate-site family (every third layer + final, × 2 positions —
`screen.LAYER_STRIDE`). Detection at a site: the eval accuracy clears
the rung's floor c by 2d's one-sided exact binomial bar at α = .01,
Bonferroni-corrected across the family (2b's `bonferroni`); the best
site is 2c's tie rule (min corrected p, then max accuracy). The
untrained twin (same procedure, the twin's probe-item and eval-item
activations) is the void control (ruling c): a cell is VOID when the
twin detects at the trained model's best site; and the trained reading
must exceed the twin's there (1b's floor correction).

Pure functions on activation maps {(layer, slot): float32 [n, d]};
no I/O here.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np

EXP2F = Path(__file__).resolve().parent
EXPERIMENTS = EXP2F.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))

from experiments.exp2d import battery_2d as bt  # noqa: E402,F401  (sys.path order: exp2b/exp2c first)
from experiments.exp2d import stats_2d as st  # noqa: E402
from experiments.exp2b import probe_starved as ps  # noqa: E402
from experiments.exp2b.splits import starving_split  # noqa: E402
from experiments.exp2c.run.screen import LAYER_STRIDE  # noqa: E402

C = ps.C
MAX_ITER = ps.MAX_ITER
ALPHA = ps.ALPHA
bonferroni = ps.bonferroni


# ------------------------------------------------------------ the family

def site_family(n_layers: int) -> list:
    """(layer, slot) for every LAYER_STRIDE-th layer + the final layer,
    × 2 positions — 2c's `_thin_layers` as a list (18 at 410m, 14 at 1b)."""
    if n_layers <= 0:
        raise ValueError(f"site_family: n_layers {n_layers}")
    keep = sorted(set(range(0, n_layers, LAYER_STRIDE)) | {n_layers - 1})
    return [(l, s) for l in keep for s in (0, 1)]


def thin(act: dict) -> dict:
    n_layers = 1 + max(l for l, _ in act)
    keep = set(site_family(n_layers))
    return {k: X for k, X in act.items() if k in keep}


# -------------------------------------------------------------- the fit

def fit_probe(X_train, y_train):
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        clf = make_pipeline(StandardScaler(),
                            LogisticRegression(C=C, max_iter=MAX_ITER))
        clf.fit(np.asarray(X_train, dtype=np.float32), np.asarray(y_train))
    return clf


def _site_result(clf, X_eval, y_eval) -> dict:
    y_eval = np.asarray(y_eval)
    pred = clf.predict(np.asarray(X_eval, dtype=np.float32))
    correct = int((pred == y_eval).sum())
    return {"acc": correct / len(y_eval), "correct": correct,
            "n": int(len(y_eval))}


def eval_probe_sites(act_train, y_train, act_eval, y_eval, sites) -> dict:
    """Per site: the probe trained on every probe item, scored on the
    eval items."""
    y_train = np.asarray(y_train)
    y_eval = np.asarray(y_eval)
    out = {}
    for site in sites:
        if act_train[site].shape[0] != len(y_train) or \
                act_eval[site].shape[0] != len(y_eval):
            raise ValueError(f"site {site}: rows disagree with labels")
        clf = fit_probe(act_train[site], y_train)
        out[site] = _site_result(clf, act_eval[site], y_eval)
    return out


# ----------------------------------------------------------- detection

def _key(site) -> str:
    return str(tuple(int(x) for x in site))


def detect(per_site: dict, *, floor: float, alpha: float = ALPHA) -> dict:
    """2d's bar at every site, Bonferroni over the family, 2c's tie
    rule for the best site. Detected iff the best site's corrected p <
    α AND its rate exceeds the floor."""
    sites = sorted(per_site)
    raw = []
    for s in sites:
        r = per_site[s]
        raw.append(st.binomial_bar(r["correct"], r["n"], floor, alpha)["p"])
    corrected = list(bonferroni(raw))
    accs = [per_site[s]["acc"] for s in sites]
    best = min(range(len(sites)), key=lambda i: (corrected[i], -accs[i]))
    detected = bool(corrected[best] < alpha and accs[best] > floor)
    lo, hi = st.clopper_pearson(per_site[sites[best]]["correct"],
                                per_site[sites[best]]["n"])
    return {
        "detected": detected, "best_site": list(sites[best]),
        "best_acc": accs[best], "best_cp95": [lo, hi],
        "p_corrected_best": corrected[best], "floor": float(floor),
        "alpha": alpha, "n_sites": len(sites),
        "per_site": {_key(s): {**per_site[s], "p": raw[i],
                               "p_corrected": corrected[i]}
                     for i, s in enumerate(sites)},
    }


def probe_rung(act_tr_train, y_train, act_tr_eval, y_eval,
               act_tw_train, act_tw_eval, *, floor: float,
               alpha: float = ALPHA) -> dict:
    """The probe rung of one cell: trained model vs its untrained twin
    at the family, the void rule, D_probe ∈ {True, False, None(void)}."""
    sites = sorted(set(act_tr_train) & set(act_tr_eval))
    if not sites:
        raise ValueError("no common sites between train and eval maps")
    tr = detect(eval_probe_sites(act_tr_train, y_train, act_tr_eval, y_eval,
                                 sites), floor=floor, alpha=alpha)
    tw = detect(eval_probe_sites(act_tw_train, y_train, act_tw_eval, y_eval,
                                 sites), floor=floor, alpha=alpha)
    best = _key(tr["best_site"])
    tw_at_best = tw["per_site"][best]
    twin_detects_at_best = bool(tw_at_best["p_corrected"] < alpha
                                and tw_at_best["acc"] > floor)
    exceeds = bool(tr["best_acc"] > tw_at_best["acc"])
    void = bool(twin_detects_at_best)
    if void:
        d = None
    else:
        d = bool(tr["detected"] and exceeds)
    return {
        "trained": tr,
        "twin": {**tw, "acc_at_trained_best": tw_at_best["acc"],
                 "p_corrected_at_trained_best": tw_at_best["p_corrected"]},
        "twin_detects_at_best": twin_detects_at_best,
        "trained_exceeds_twin_at_best": exceeds,
        "void": void, "D_probe": d,
        "rule": "detected at the best site (Bonferroni over the family) AND "
                "not void (twin does not detect at that site) AND trained "
                "accuracy > twin accuracy there",
    }


# --------------------------------------------------- the CV secondary

def cv_probe_sites(act_train, y_train, sites, *, seed: int,
                   holdout_frac: float = 0.2) -> dict:
    """Ruling b's printed secondary: a seeded random split over the
    probe items (not the eval items), per-site held-out accuracy."""
    y_train = np.asarray(y_train)
    n = len(y_train)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_val = int(round(holdout_frac * n))
    val_idx, tr_idx = perm[:n_val], perm[n_val:]
    out = {}
    for site in sites:
        clf = fit_probe(act_train[site][tr_idx], y_train[tr_idx])
        out[site] = _site_result(clf, act_train[site][val_idx], y_train[val_idx])
    out["split"] = {"seed": seed, "holdout_frac": holdout_frac,
                    "n_train": int(len(tr_idx)), "n_val": int(n_val)}
    return out


# ---------------------------------------------- the m3 reproduction gate

def starved_accuracies(act, y, bases, split_params, *, seed: int) -> dict:
    """2c's starved-validation accuracies at the family under 2b's
    `starving_split` (the committed split parameters and seed), the
    best site by 2c's tie rule in the degenerate all-p-1 case (max
    accuracy). The known-answer gate: on the committed activation
    files this must reproduce the committed m3 record's accuracy,
    best site and split counts exactly."""
    y = np.asarray(y)
    act = thin(act)
    train_idx, val_idx, info = starving_split(bases, y, seed, split_params)
    per = {}
    for site in sorted(act):
        clf = fit_probe(act[site][train_idx], y[train_idx])
        per[site] = _site_result(clf, act[site][val_idx], y[val_idx])
    sites = sorted(per)
    best = max(sites, key=lambda s: per[s]["acc"])
    return {"per_site": {_key(s): per[s] for s in sites},
            "best_site": list(best), "accuracy": per[best]["acc"],
            "n_val": int(len(val_idx)), "split": info}
