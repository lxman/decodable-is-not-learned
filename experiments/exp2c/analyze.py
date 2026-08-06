# experiments/exp2c/analyze.py
"""Frozen analysis for Exp 2c (design §5). The verdict tree, in
precedence order: PIPELINE_ABORT (gate 2 structural) ->
INSUFFICIENT_DATA (dual floor after attrition) -> FAIL (family-cluster
bootstrap CI includes 0) -> PASS (block-permutation p < .01 AND
rho >= 0.5) -> INDETERMINATE. Every rule that fires appends to the
audit list.

Amendment (ruling 2026-08-01, implemented pre-freeze 2026-08-06): the
PASS branch adjudicates with the design §5 exact family-block
permutation test (`run.power_table.exact_block_p` — enumerated below
the 5e6 guard, sampled at 100,000 seeded draws above it) at fixed
alpha .01, replacing the calibrated-naive permutation test and its
rho_family-dependent `calibrated_cutoff` input. Rung arrays are
grouped into contiguous per-family blocks (family order = first
appearance in the scored list) before the call, per the ledgered
interface contract — the block test's layout convention, not an
assumption about input order."""

from dataclasses import dataclass

import numpy as np
from scipy.stats import spearmanr

try:  # experiments.exp2c.analyze (pytest / absolute import)
    from .run.power_table import exact_block_p
except ImportError:  # pragma: no cover - direct import from exp2c/
    from run.power_table import exact_block_p

RHO_BAR = 0.5
ALPHA_EXACT = 0.01
MIN_FAMILIES = 8
MIN_RUNGS = 20
N_BOOT = 10_000


@dataclass
class AnalyzeInputs:
    rungs: list
    untrained_fires: dict
    shuffled_fires: list


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
        else:
            audit.append(f"unscored:{r['name']}")
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
    rho = float(spearmanr(x, y).statistic)
    # block-permutation test on family-contiguous arrays (the ledgered
    # layout contract: block i of the sizes vector IS family i's rungs)
    fam_order = []
    for r in scored:
        if r["family"] not in fam_order:
            fam_order.append(r["family"])
    grouped = [r for f in fam_order for r in scored if r["family"] == f]
    fam_sizes = [sum(1 for r in scored if r["family"] == f)
                 for f in fam_order]
    xg = np.array([r["probe_score"] for r in grouped])
    yg = np.array([r["ascent_score"] for r in grouped])
    block = exact_block_p(xg, yg, fam_sizes)
    # family-cluster bootstrap CI
    rng = np.random.default_rng(seed)
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
    base = {"rho": rho, "block_p": float(block["p"]),
            "n_perms": int(block["n_perms"]),
            "resolution": float(block["resolution"]),
            "method": block["method"], "ci": ci, "audit": audit,
            "n_rungs": len(scored), "n_families": len(fams)}
    if ci[0] is not None and ci[0] <= 0.0 <= ci[1]:
        return {**base, "verdict": "FAIL"}
    if block["p"] < ALPHA_EXACT and rho >= RHO_BAR:
        return {**base, "verdict": "PASS"}
    return {**base, "verdict": "INDETERMINATE"}
