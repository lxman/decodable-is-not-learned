# experiments/exp2g/probe_2g.py
"""Exp 2g probe (design §3): 2f's machinery — 2b's standardized
logistic regression (C = 1.0, max_iter 100) at 2c's site family — with
the site chosen by seeded cross-validation on the PROBE items only
(ruling: eval items and the outcome never enter the choice), then
refit on all probe items; the per-item score is the probe's
log-probability of the item's true label (ruling a). 2f's rule (best
site by eval accuracy) is computed beside it as a sensitivity."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

EXP2G = Path(__file__).resolve().parent
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2f import probe_2f as pb  # noqa: E402

CV_SEED = 0
CV_HOLDOUT = 0.2
fit_probe = pb.fit_probe
site_family = pb.site_family
thin = pb.thin


def site_key(site) -> str:
    return str(tuple(int(v) for v in site))


def _lowest_first(sites):
    return sorted(sites, key=lambda s: (int(s[0]), int(s[1])))


def cv_site(act_train, y_train, *, seed: int = CV_SEED,
            holdout: float = CV_HOLDOUT) -> tuple:
    """The site with the highest held-out accuracy on a seeded split of
    the probe items; ties → the lowest (layer, slot)."""
    sites = _lowest_first(act_train)
    cv = pb.cv_probe_sites(act_train, y_train, sites, seed=seed,
                           holdout_frac=holdout)
    split = cv.pop("split")
    per_site = {site_key(s): float(cv[s]["acc"]) for s in sites}
    best = max(per_site.values())
    site = next(s for s in sites if per_site[site_key(s)] == best)
    return tuple(int(v) for v in site), per_site, split


def item_log_probs(clf, X, y) -> np.ndarray:
    classes = [str(c) for c in clf.classes_]
    y = [str(v) for v in y]
    missing = sorted(set(y) - set(classes))
    if missing:
        raise ValueError(f"labels {missing} have no probe class — the probe "
                         f"items never carried them")
    col = {c: i for i, c in enumerate(classes)}
    lp = clf.predict_log_proba(np.asarray(X, dtype=np.float32))
    return lp[np.arange(len(y)), [col[v] for v in y]]


def score_at_site(act_train, y_train, act_eval, y_eval, site) -> dict:
    site = tuple(int(v) for v in site)
    clf = pb.fit_probe(act_train[site], y_train)
    X = np.asarray(act_eval[site], dtype=np.float32)
    scores = item_log_probs(clf, X, y_eval)
    pred = [str(v) for v in clf.predict(X)]
    correct = int(sum(p == str(t) for p, t in zip(pred, y_eval)))
    return {"site": [site[0], site[1]], "scores": [float(v) for v in scores],
            "pred": pred, "eval_correct": correct,
            "eval_acc": correct / len(y_eval), "n": int(len(y_eval))}


def eval_best_site(act_train, y_train, act_eval, y_eval) -> tuple:
    """2f's rule: the site with the highest EVAL accuracy (ties → lowest)."""
    sites = _lowest_first(set(act_train) & set(act_eval))
    res = pb.eval_probe_sites(act_train, y_train, act_eval, y_eval, sites)
    per_site = {site_key(s): float(res[s]["acc"]) for s in sites}
    best = max(per_site.values())
    site = next(s for s in sites if per_site[site_key(s)] == best)
    return tuple(int(v) for v in site), per_site


def score_cell(act_train, y_train, act_eval, y_eval, *, seed: int = CV_SEED,
               holdout: float = CV_HOLDOUT, with_eval_rule: bool = True) -> dict:
    sites = sorted(set(act_train) & set(act_eval))
    if not sites:
        raise ValueError("score_cell: no common sites")
    y_train = [str(v) for v in y_train]
    y_eval = [str(v) for v in y_eval]
    site, per_site, split = cv_site({s: act_train[s] for s in sites}, y_train,
                                    seed=seed, holdout=holdout)
    out = score_at_site(act_train, y_train, act_eval, y_eval, site)
    out["cv"] = {"per_site": per_site, "split": split,
                 "best_acc": per_site[site_key(site)]}
    out["n_sites"] = len(sites)
    if with_eval_rule:
        es, eps = eval_best_site(act_train, y_train, act_eval, y_eval)
        r = score_at_site(act_train, y_train, act_eval, y_eval, es)
        out["eval_rule"] = {"site": r["site"], "scores": r["scores"],
                            "eval_acc": r["eval_acc"], "per_site": eps}
    return out
