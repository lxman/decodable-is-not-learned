"""Exact power tables from the frozen analysis (design §7, Open item 6).

Mass side: the critical count K*(n) is the smallest K the frozen
`sign_test_significance` calls significant — compute_power INVERTS the
frozen function rather than re-deriving the tail, so a drift between
the power tables and the adjudication convention cannot exist. Power
at effect θ is P(Binom(n, θ) ≥ K*). The adjudicated table sits at
n_tests = 4 (α = .01 Bonferroni, one-sided); the post-tie-n grid is
the recompute path §7 orders at the realized per-cell n_eff, and the
analysis reruns the same function at those n.

Sampling side: detection probability 1 − (1−p)^k against true per-draw
rate p at the pooled k's, and the .95-detectable rate — asserted equal
to `cp_upper(0, k)`, the same closed form read from the other side.

The doc's §7 quotes are cross-checked here and recorded with their
exact values in the committed artifact (`power.json`); any discrepancy
is ledgered, not silently absorbed. The freeze checklist re-runs this
script cold and compares byte-identically.
"""

from __future__ import annotations

import json
from pathlib import Path

from scipy.stats import binom

from experiments.exp3.analyze_3 import (
    ALPHA, K_TOTAL, N_ADJ_TESTS, cp_upper, sign_test_significance,
)

EXP3 = Path(__file__).resolve().parent
OUT = EXP3 / "power.json"

THETA_GRID = [round(0.50 + i * 0.01, 2) for i in range(21)]   # .50–.70
POST_TIE_N = (500, 490, 480, 460, 450, 440, 420, 400, 350, 300, 250,
              200, 150, 100)
K_REV_POOLED = 500 * K_TOTAL["rev_string7"]    # 128,000 (§3)
K_CTRL_POOLED = 500 * K_TOTAL["ctrl_copy"]     # 16,000
RATES = (1e-4, 2.3e-5, 1e-5, 1e-6)


def critical_count(n: int, *, n_tests=N_ADJ_TESTS, alpha=ALPHA) -> int:
    """Smallest K with a significant sign test at (n, n_tests, alpha),
    by direct search through the frozen significance function (the
    tail is monotone in K)."""
    for K in range(n + 1):
        _p, sig = sign_test_significance(K, n, n_tests=n_tests,
                                         alpha=alpha)
        if sig:
            return K
    raise ValueError(f"no critical count exists at n={n} — the test "
                     f"cannot fire at all there")


def sign_test_power(theta: float, n: int, *, n_tests=N_ADJ_TESTS,
                    alpha=ALPHA) -> float:
    return float(binom.sf(critical_count(n, n_tests=n_tests,
                                         alpha=alpha) - 1, n, theta))


def blind_edge(n: int, target: float, *, n_tests=N_ADJ_TESTS,
               alpha=ALPHA, step: float = 0.0005) -> float:
    """Smallest θ on a fine grid whose power reaches `target` — below
    it the design is blind at that confidence."""
    theta = 0.5
    while theta <= 1.0:
        if sign_test_power(theta, n, n_tests=n_tests, alpha=alpha) \
                >= target:
            return round(theta, 4)
        theta += step
    raise ValueError(f"power never reaches {target} at n={n}")


def detection(p: float, k: int) -> float:
    return float(1.0 - (1.0 - p) ** k)


def build() -> dict:
    k500 = critical_count(500)
    mass = {
        "alpha": ALPHA, "n_tests": N_ADJ_TESTS, "one_sided": True,
        "n": 500,
        "critical_count": k500,
        "power_by_theta": {f"{t:.2f}": sign_test_power(t, 500)
                           for t in THETA_GRID},
        "blind_theta_power50": blind_edge(500, 0.50),
        "blind_theta_power80": blind_edge(500, 0.80),
        "control_n_tests_1": {
            "critical_count": critical_count(500, n_tests=1),
        },
        "post_tie_n": {
            str(n): {
                "critical_count": critical_count(n),
                "power_at_0.55": sign_test_power(0.55, n),
                "power_at_0.60": sign_test_power(0.60, n),
            } for n in POST_TIE_N},
    }
    det = {str(k): {f"{p:.1e}": detection(p, k) for p in RATES}
           for k in (K_REV_POOLED, K_CTRL_POOLED)}
    rate95 = {}
    for k in (K_REV_POOLED, K_CTRL_POOLED):
        closed = 1.0 - 0.05 ** (1.0 / k)
        via_cp = cp_upper(0, k)
        if abs(closed - via_cp) > 1e-12:
            raise AssertionError(
                f"detectable-rate closed form {closed} disagrees with "
                f"cp_upper(0, {k}) = {via_cp} — the two sides of the "
                f"same bound must be the same number")
        rate95[str(k)] = closed
    sampling = {
        "k_pooled": {"reversal": K_REV_POOLED, "control": K_CTRL_POOLED},
        "detection_by_rate": det,
        "rate_detectable_at_95": rate95,
    }

    # §7's quotes, cross-checked with the exact values beside them
    quotes = {
        "critical_count_approx_282": {
            "quoted": 282, "computed": k500, "agrees": k500 == 282},
        "power_.95_at_theta_.60": {
            "quoted": 0.95, "computed": sign_test_power(0.60, 500),
            "agrees": abs(sign_test_power(0.60, 500) - 0.95) < 0.02},
        "power_.26_at_theta_.55": {
            "quoted": 0.26, "computed": sign_test_power(0.55, 500),
            "agrees": abs(sign_test_power(0.55, 500) - 0.26) < 0.02},
        "blind_theta_approx_.57": {
            "quoted": 0.57, "computed": blind_edge(500, 0.50),
            "agrees": abs(blind_edge(500, 0.50) - 0.57) < 0.01},
        "detection_.95_at_2.3e-5": {
            "quoted": 0.95, "computed": detection(2.3e-5, K_REV_POOLED),
            "agrees": abs(detection(2.3e-5, K_REV_POOLED) - 0.95) < 0.01},
        "detection_.72_at_1e-5": {
            "quoted": 0.72, "computed": detection(1e-5, K_REV_POOLED),
            "agrees": abs(detection(1e-5, K_REV_POOLED) - 0.72) < 0.01},
        "detection_.12_at_1e-6": {
            "quoted": 0.12, "computed": detection(1e-6, K_REV_POOLED),
            "agrees": abs(detection(1e-6, K_REV_POOLED) - 0.12) < 0.01},
    }
    return {"mass": mass, "sampling": sampling,
            "doc_quotes_check": quotes}


if __name__ == "__main__":
    tables = build()
    OUT.write_text(json.dumps(tables, indent=1, sort_keys=True) + "\n")
    q = tables["doc_quotes_check"]
    print(f"critical count (n=500, alpha {ALPHA}/{N_ADJ_TESTS} one-sided):"
          f" {tables['mass']['critical_count']}")
    print(f"power at .60: {tables['mass']['power_by_theta']['0.60']:.4f}"
          f" | at .55: {tables['mass']['power_by_theta']['0.55']:.4f}"
          f" | blind edge (power .5): "
          f"{tables['mass']['blind_theta_power50']}")
    print(f"detectable rate at .95, k=128000: "
          f"{tables['sampling']['rate_detectable_at_95']['128000']:.3e}")
    bad = [k for k, v in q.items() if not v["agrees"]]
    print("doc quotes: ALL AGREE" if not bad else
          f"doc quotes DISAGREE (ledger): {bad}")
    print(f"written: {OUT}")
