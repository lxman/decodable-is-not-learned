"""Experiment 2 frozen analysis (design doc §4). Committed alongside the design doc
and NOT edited after data collection begins (mirror of Exp 1's discipline; tagged
when the doc's status flips to Preregistered).

Inputs (produced by the run stages, committed as they land):
  results/probe_scores.json   {capability: {"probe_margin": float, ...}}   (Stage 1)
  results/eval_scores.json    {capability: {"2.8b": m, "6.9b": m, "12b": m}} (Stage 2)
  battery/items/scored_battery.json  ["add2", ...]  (fixed at M1 inclusion)

Verdict logic (frozen):
  PASS          one-tailed permutation p < 0.05 AND point Spearman rho >= 0.5
  FAIL          bootstrap 95% CI on rho includes 0  (the falsifier)
  INDETERMINATE otherwise (reported with the CI; no post-hoc slicing)
  INSUFFICIENT_DATA  fewer than 10 scored capabilities with both scores

Both PASS and FAIL conditions can in principle hold on small n (a CI can cross 0
while the permutation p sneaks under 0.05); precedence is frozen here as
INSUFFICIENT-first, then FAIL, then PASS, then INDETERMINATE — the conservative
order (a CI including 0 can never be published as a pass).

Descriptive secondary (design doc §4, preregistered, NEVER scored): rho recomputed
over capabilities whose scale-ascent score exceeds ASCENT_FLOOR (0.05 ≈ 2.3σ of the
500-item noise floor). Diagnoses whether a null primary reflects outcome-side
flatness at Pythia scale (noise-rank ties from capabilities still flat at 12B)
rather than absence of ordering information. Reported alongside the verdict; has no
effect on it.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

EXP_DIR = Path(__file__).resolve().parent

MIN_N = 10
ALPHA_PERM = 0.05
RHO_BAR = 0.5
N_PERM = 100_000
N_BOOT = 10_000
SEED = 20260706
ASCENT_FLOOR = 0.05  # descriptive restricted-rho subset bar; never affects verdict
MIN_N_RESTRICTED = 3  # below this the restricted rho is meaningless; report NaN

EVAL_MODELS = ("2.8b", "6.9b", "12b")


def spearman(x, y) -> float:
    """Spearman rho via rank-transformed Pearson (average ranks for ties)."""
    from scipy.stats import rankdata

    rx, ry = rankdata(x), rankdata(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    denom = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / denom) if denom > 0 else 0.0


def permutation_p(x, y, n_perm=N_PERM, seed=SEED) -> float:
    """One-tailed (H1: rho > 0) Monte-Carlo permutation test, add-one estimator."""
    rng = np.random.default_rng(seed)
    obs = spearman(x, y)
    hits = sum(spearman(x, rng.permutation(y)) >= obs for _ in range(n_perm))
    return (hits + 1) / (n_perm + 1)


def bootstrap_ci(x, y, n_boot=N_BOOT, seed=SEED, level=0.95) -> tuple[float, float]:
    """Case-resampling bootstrap CI on rho."""
    rng = np.random.default_rng(seed)
    x, y = np.asarray(x), np.asarray(y)
    stats = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(x), size=len(x))
        stats.append(spearman(x[idx], y[idx]))
    lo, hi = np.quantile(stats, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(lo), float(hi)


@dataclass
class Report:
    verdict: str
    n: int
    rho: float = float("nan")
    perm_p: float = float("nan")
    ci95: tuple[float, float] = (float("nan"), float("nan"))
    capabilities: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    # descriptive restricted-rho secondary (§4): subset with scale-ascent > ASCENT_FLOOR
    restricted_n: int = 0
    restricted_rho: float = float("nan")


def analyze(probe_scores: dict, eval_scores: dict, scored_battery: list[str]) -> Report:
    caps = [c for c in scored_battery
            if c in probe_scores and c in eval_scores
            and all(m in eval_scores[c] for m in EVAL_MODELS)]
    dropped = [c for c in scored_battery if c not in caps]
    notes = [f"dropped (missing scores): {dropped}"] if dropped else []

    if len(caps) < MIN_N:
        return Report("INSUFFICIENT_DATA", len(caps), capabilities=caps,
                      notes=notes + [f"need >= {MIN_N} scored capabilities"])

    x = [float(probe_scores[c]["probe_margin"]) for c in caps]
    y = [float(np.mean([eval_scores[c][m] for m in EVAL_MODELS])) for c in caps]

    rho = spearman(x, y)
    p = permutation_p(x, y)
    ci = bootstrap_ci(x, y)

    if ci[0] <= 0.0 <= ci[1] or ci[1] < 0.0:
        verdict = "FAIL"
    elif p < ALPHA_PERM and rho >= RHO_BAR:
        verdict = "PASS"
    else:
        verdict = "INDETERMINATE"

    # Descriptive restricted-rho (never scored, never touches the verdict above).
    sub = [i for i in range(len(caps)) if y[i] > ASCENT_FLOOR]
    r_n, r_rho = len(sub), float("nan")
    if r_n >= MIN_N_RESTRICTED:
        r_rho = spearman([x[i] for i in sub], [y[i] for i in sub])
    notes = notes + [f"restricted (ascent > {ASCENT_FLOOR}): n={r_n}"]

    return Report(verdict, len(caps), rho, p, ci, caps, notes,
                  restricted_n=r_n, restricted_rho=r_rho)


def main():
    probe = json.loads((EXP_DIR / "results" / "probe_scores.json").read_text())
    evals = json.loads((EXP_DIR / "results" / "eval_scores.json").read_text())
    battery = json.loads((EXP_DIR / "battery" / "items" / "scored_battery.json").read_text())
    r = analyze(probe, evals, battery)
    print(f"verdict={r.verdict} n={r.n} rho={r.rho:.3f} perm_p={r.perm_p:.4g} "
          f"ci95=({r.ci95[0]:.3f},{r.ci95[1]:.3f})")
    print(f"descriptive restricted rho (ascent > {ASCENT_FLOOR}): "
          f"n={r.restricted_n} rho={r.restricted_rho:.3f}")
    for note in r.notes:
        print(f"  note: {note}")
    return r


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
