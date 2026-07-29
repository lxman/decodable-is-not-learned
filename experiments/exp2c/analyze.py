# experiments/exp2c/analyze.py
"""Frozen analysis for Exp 2c (design §5). The verdict tree, in
precedence order: PIPELINE_ABORT (gate 2 structural) ->
INSUFFICIENT_DATA (dual floor after attrition) -> FAIL (family-cluster
bootstrap CI includes 0) -> PASS (calibrated p AND rho >= 0.5) ->
INDETERMINATE. Every rule that fires appends to the audit list."""

from dataclasses import dataclass, field

import numpy as np
from scipy.stats import spearmanr

RHO_BAR = 0.5
MIN_FAMILIES = 8
MIN_RUNGS = 20
N_PERM = 100_000
N_BOOT = 10_000


@dataclass
class AnalyzeInputs:
    rungs: list
    untrained_fires: dict
    shuffled_fires: list
    calibrated_cutoff: float


def verdict(inp: AnalyzeInputs, seed=0) -> dict:
    audit = []
    # gate 2: abort only on structural_abort classification
    if any(f["classification"] == "structural_abort"
           for f in inp.shuffled_fires):
        return {"verdict": "PIPELINE_ABORT",
                "audit": audit + ["shuffled:structural_abort"]}
    if inp.shuffled_fires:
        audit.append("shuffled:count_test")
    # gate 1 residual attrition: any rung with a structural fire drops
    scored = []
    for r in inp.rungs:
        fires = inp.untrained_fires.get(r["name"], [])
        if any(c in ("elevated", "structural_abort") for c in fires):
            audit.append(f"attrition:{r['name']}")
        elif r["scored"]:
            scored.append(r)
    fams = {r["family"] for r in scored}
    if len(fams) < MIN_FAMILIES or len(scored) < MIN_RUNGS:
        return {"verdict": "INSUFFICIENT_DATA", "audit": audit,
                "n_rungs": len(scored), "n_families": len(fams)}
    x = np.array([r["probe_score"] for r in scored])
    y = np.array([r["ascent_score"] for r in scored])
    for f in sorted(fams):
        ys = y[[i for i, r in enumerate(scored) if r["family"] == f]]
        if len(ys) > 1 and np.all(ys == ys[0]):
            audit.append(f"ties:{f}")
    rng = np.random.default_rng(seed)
    rho = float(spearmanr(x, y).statistic)
    perms = np.array([spearmanr(x, rng.permutation(y)).statistic
                      for _ in range(N_PERM)])
    naive_p = float((1 + np.sum(perms >= rho)) / (N_PERM + 1))
    # family-cluster bootstrap CI
    fam_list = sorted(fams)
    idx_of = {f: [i for i, r in enumerate(scored) if r["family"] == f]
              for f in fam_list}
    boots = []
    for _ in range(N_BOOT):
        pick = rng.choice(len(fam_list), size=len(fam_list), replace=True)
        ii = [i for k in pick for i in idx_of[fam_list[k]]]
        if len(set(x[ii])) > 1 and len(set(y[ii])) > 1:
            boots.append(spearmanr(x[ii], y[ii]).statistic)
    ci = (float(np.percentile(boots, 2.5)),
          float(np.percentile(boots, 97.5))) if boots else (None, None)
    base = {"rho": rho, "naive_p": naive_p, "ci": ci, "audit": audit,
            "n_rungs": len(scored), "n_families": len(fams)}
    if ci[0] is not None and ci[0] <= 0.0 <= ci[1]:
        return {**base, "verdict": "FAIL"}
    if naive_p < inp.calibrated_cutoff and rho >= RHO_BAR:
        return {**base, "verdict": "PASS"}
    return {**base, "verdict": "INDETERMINATE"}
