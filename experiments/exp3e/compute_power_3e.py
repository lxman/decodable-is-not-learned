"""Power, honestly (design §7; doc Open item 4) — CLASS-LEVEL BY
DESIGN (the sixth lesson applied in advance): the alternative is
expressed as per-class per-draw rates over the realized 32/13 split,
never as per-item concentration on the committed fired items.

THE PRIMARY'S POWER IS EXACT. Under independent items with per-class
fire probabilities q_reach / q_non over the tranche, n_reach ~
Binomial(32, q_reach) and n_non ~ Binomial(13, q_non) independently;
every (n_reach, n_non) pair is enumerated and classified through the
SAME hypergeometric tails and mechanical tree the verdict runs — no
Monte Carlo, no approximation beyond float64.

Per-item fire probability under a per-draw rate r over D draws:
homogeneous P = 1 − exp(−rD) (Poisson thinning of the draws); gamma-
dispersed, rate ~ Gamma(shape k, mean r): P = 1 − (1 + rD/k)^(−k)
(the negative-binomial zero probability). The shape is fitted to the
committed reachable per-item counts at 1b by the program's frozen
moment rule (3d's λ rule, by precedent): k = μ̂²/(V̂ − μ̂), population
variance — the committed record's own overdispersion measurement,
frozen BEFORE any power number ran (PROGRESS.md).

THE SPECIFICITY ARM'S POWER IS A SCENARIO (§7): no committed draw was
ever scored against a competitor, so competitor rates are unknown.
Reverse emissions follow the reachable-class rate; competitors share
(1 − π)/π of it equally under a reverse-share π ∈ {.6, .75, .9}, and
the null puts every matched string at the same rate. Monte Carlo at
the committed seed, each simulated arm judged by the exact
designation-exchangeability DP the verdict runs.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

EXP3E = Path(__file__).resolve().parent
if str(EXP3E.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3E.parent.parent))

from experiments.exp3d import analyze_3d as d  # noqa: E402
from experiments.exp3e import partition_3e as pt  # noqa: E402
from experiments.exp3e import stats_3e as st  # noqa: E402
from experiments.exp3e.analyze_3e import (  # noqa: E402
    COMMITTED_FIRE_COUNTS_SUBSET, K_COMMITTED, K_NEW_3E, N_ALL_DISTINCT_LEN4,
    PARTITION_FILE_SHA256, PARTITION_PATH, POWER_PATH, RUNG, SIZES_3E,
    SUBSET_ITEMS_PIN, load_partition_3e, power_pin_entries,
)

POWER_SEED = 20260821          # frozen at build (doc Open item 4)
SPEC_SIMS = 20_000             # specificity scenarios, per scenario
POWER_BAR = 0.75               # the program's bar since Exp 1
RATIO_GRID = tuple(round(x, 3) for x in np.linspace(1.0, 0.0, 101))
CALIBRATION_NS = (8, 10, 12, 15, 20, 24, 28, 32)

# §3: the committed all-distinct len-4 rates (the H_shortcut
# non-reachable rate) — 3 / 381,440 at 1b, 2 / 267,008 at 410m.
# Transcribed from 3d's sha-pinned verdict record (strata table) and
# re-derived at run() time by analyze_3e from raw bytes.
ALL_DISTINCT_COMMITTED = {"1b": {"count": 3, "n_draws": 381_440},
                          "410m": {"count": 2, "n_draws": 267_008}}


# --------------------------------------------------- fire probabilities

def p_fire_homogeneous(rate: float, draws: int) -> float:
    return 1.0 - math.exp(-rate * draws)


def p_fire_gamma(rate: float, draws: int, shape: float) -> float:
    return 1.0 - (1.0 + rate * draws / shape) ** (-shape)


def dispersion_hat(counts) -> dict:
    """The frozen moment rule on the committed reachable per-item
    counts: k = μ̂²/(V̂ − μ̂), population variance (3d's λ rule by
    precedent)."""
    x = np.asarray(counts, dtype=np.float64)
    mu = float(x.mean())
    var = float(x.var())
    if var <= mu:
        raise ValueError(
            f"committed counts show no overdispersion (V̂ = {var} ≤ μ̂ = "
            f"{mu}) — the frozen shape rule is undefined and the build "
            f"must stop and re-derive, not guess")
    return {"mu_hat": mu, "var_hat": var, "shape": mu * mu / (var - mu),
            "n_items": int(len(x)), "counts": [int(v) for v in x],
            "rule": "shape = mu^2/(V - mu), Gamma-shape moment "
                    "estimator on the committed reachable per-item "
                    "counts at 1b, population variance; frozen before "
                    "any power number was computed (PROGRESS.md)"}


# ------------------------------------------------- exact world probs

def _binom_pmf(n: int, q: float) -> np.ndarray:
    ks = np.arange(n + 1)
    return np.array([math.comb(n, k) * q ** k * (1 - q) ** (n - k)
                     for k in ks])


def world_probs(q_reach: float, q_non: float, *, n_reach: int, n_non: int,
                m_min: int, alpha=st.ALPHA_3E, thin_max=st.THIN_MAX) -> dict:
    """Exact world probabilities under independent per-item fire
    probabilities by class, through the verdict's own tails and tree."""
    N_ = n_reach + n_non
    pr = _binom_pmf(n_reach, q_reach)
    pn = _binom_pmf(n_non, q_non)
    tallies = {w: 0.0 for w in ("SHORTCUT", "ANTI-SHORTCUT",
                                "NO-SHORTCUT", "UNINFORMATIVE")}
    p_thin = 0.0
    e_n = e_x = 0.0
    p_n_le_10 = 0.0
    for a, pa in enumerate(pr):
        for b, pb in enumerate(pn):
            w = pa * pb
            if w == 0.0:
                continue
            n = a + b
            e_n += w * n
            e_x += w * b
            if n <= thin_max:
                p_thin += w
            if n <= 10:
                p_n_le_10 += w
            if n == 0:
                tallies["UNINFORMATIVE"] += w
                continue
            low, high = st.hypergeom_tails(N_, n_non, n, b)
            if low <= alpha:
                tallies["SHORTCUT"] += w
            elif high <= alpha:
                tallies["ANTI-SHORTCUT"] += w
            elif n >= m_min:
                tallies["NO-SHORTCUT"] += w
            else:
                tallies["UNINFORMATIVE"] += w
    return {"worlds": tallies, "p_thin": p_thin, "expected_n": e_n,
            "expected_x": e_x, "p_n_le_10": p_n_le_10,
            "q_reach": q_reach, "q_non": q_non}


def min_detectable_ratio(rate_reach: float, draws: int, *, n_reach, n_non,
                         m_min, shape, grid=RATIO_GRID) -> dict:
    """Largest non-reachable/reachable rate ratio ρ at which
    P(SHORTCUT) ≥ .75, reachable rate fixed at the committed value."""
    def q(rate):
        return (p_fire_gamma(rate, draws, shape) if shape
                else p_fire_homogeneous(rate, draws))
    rows = []
    best = None
    for rho in grid:
        w = world_probs(q(rate_reach), q(rho * rate_reach), n_reach=n_reach,
                        n_non=n_non, m_min=m_min)
        rows.append({"ratio": float(rho),
                     "p_shortcut": w["worlds"]["SHORTCUT"],
                     "expected_n": w["expected_n"]})
        if w["worlds"]["SHORTCUT"] >= POWER_BAR and \
                (best is None or rho > best):
            best = float(rho)
    return {"grid": rows, "max_ratio_at_power_75": best,
            "dispersion": "gamma" if shape else "homogeneous"}


# ------------------------------------------------ specificity scenarios

def simulate_specificity(m_sizes, *, reverse_rate, draws, reverse_share,
                         m_s_min, n_sims, seed, shape=None) -> dict:
    """Monte Carlo over the arm: per item, reverse count ~ Poisson(λ_r D)
    with λ_r the reachable-class rate (gamma-dispersed when `shape`),
    each of the |M| competitors ~ Poisson(λ_r D (1−π)/(π|M|)); under
    the null (reverse_share None) every matched string shares λ_r.
    Each simulated arm is judged by the exact designation DP."""
    rng = np.random.default_rng(seed)
    rejects = sparse = 0
    events_total = 0
    for _ in range(n_sims):
        vectors = []
        for m in m_sizes:
            lam = reverse_rate
            if shape:
                lam = rng.gamma(shape, reverse_rate / shape)
            if reverse_share is None:
                rates = [lam] * (1 + m)
            else:
                comp = lam * (1 - reverse_share) / (reverse_share * m)
                rates = [lam] + [comp] * m
            vectors.append(tuple(int(rng.poisson(r * draws)) for r in rates))
        t = st.designation_test(vectors)
        events_total += t["events"]
        ann = st.specificity_annotation(p=t["p"], events=t["events"],
                                        m_s_min=m_s_min)
        if ann == "DIRECTED":
            rejects += 1
        elif ann == "SPARSE":
            sparse += 1
    return {"p_reject": rejects / n_sims, "p_sparse": sparse / n_sims,
            "expected_events": events_total / n_sims,
            "reverse_share": reverse_share, "n_sims": n_sims,
            "dispersion": "gamma" if shape else "homogeneous"}


# -------------------------------------------------------------- driver

def compute(partition, *, spec_sims=SPEC_SIMS) -> dict:
    pins = power_pin_entries(partition)
    m_min = pins["m_min"]
    n_reach = len(partition["reachable"])
    n_non = len(partition["non_reachable"])
    reach_set = set(partition["reachable"])
    # committed rates by class (§3), from the address pin and the
    # committed draw totals
    rates = {}
    for size in SIZES_3E:
        cnt = COMMITTED_FIRE_COUNTS_SUBSET[size]
        reach_f = sum(v for i, v in cnt.items() if i in reach_set)
        non_f = sum(v for i, v in cnt.items() if i not in reach_set)
        k = K_COMMITTED[size]
        r_reach = reach_f / (n_reach * k)
        r_non_ad = (ALL_DISTINCT_COMMITTED[size]["count"]
                    / ALL_DISTINCT_COMMITTED[size]["n_draws"])
        r_class = (reach_f + non_f) / ((n_reach + n_non) * k)
        rates[size] = {
            "reachable_committed": r_reach,
            "reachable_fires": reach_f,
            "non_reachable_committed_fires": non_f,
            "non_reachable_committed_cp95_upper":
                d.a3.cp_upper(non_f, n_non * k) if non_f == 0 else None,
            "all_distinct_committed": r_non_ad,
            "repeat_class_committed": r_class,
            "H_shortcut": {"reach": r_reach, "non": r_non_ad},
            "H_half": {"reach": r_reach,
                       "non": math.sqrt(r_reach * r_non_ad)},
            "H0": {"reach": r_class, "non": r_class},
        }
    # dispersion from the 1b reachable per-item counts
    counts_1b = [COMMITTED_FIRE_COUNTS_SUBSET["1b"].get(i, 0)
                 for i in partition["reachable"]]
    disp = dispersion_hat(counts_1b)
    shape = disp["shape"]

    scenarios = {}
    for size in SIZES_3E:
        draws = K_NEW_3E[size]
        scenarios[size] = {}
        for hyp in ("H_shortcut", "H_half", "H0"):
            rr = rates[size][hyp]
            for variant, sh in (("gamma", shape), ("homogeneous", None)):
                qf = (lambda r: p_fire_gamma(r, draws, sh)) if sh else \
                    (lambda r: p_fire_homogeneous(r, draws))
                w = world_probs(qf(rr["reach"]), qf(rr["non"]),
                                n_reach=n_reach, n_non=n_non, m_min=m_min)
                scenarios[size][f"{hyp}/{variant}"] = {
                    **w, "rates": rr, "draws_per_item": draws}
    mdr = {size: {v: min_detectable_ratio(
        rates[size]["reachable_committed"], K_NEW_3E[size],
        n_reach=n_reach, n_non=n_non, m_min=m_min, shape=sh)
        for v, sh in (("gamma", shape), ("homogeneous", None))}
        for size in SIZES_3E}
    calib = {
        "conditional_on_n": st.calibration_table(n_reach + n_non, n_non,
                                                 CALIBRATION_NS, st.ALPHA_3E),
        "unconditional_H0": {
            size: {v: {"size_low": scenarios[size][f"H0/{v}"]["worlds"]
                       ["SHORTCUT"],
                       "size_high": scenarios[size][f"H0/{v}"]["worlds"]
                       ["ANTI-SHORTCUT"],
                       "size_union": scenarios[size][f"H0/{v}"]["worlds"]
                       ["SHORTCUT"] + scenarios[size][f"H0/{v}"]["worlds"]
                       ["ANTI-SHORTCUT"]}
                   for v in ("gamma", "homogeneous")}
            for size in SIZES_3E},
        "note": "each direction calibrates at ≤ α; the union of the two "
                "directional worlds is ≤ 2α, not α (3d §7's corrected "
                "sentence, applied in advance)",
    }
    # specificity scenarios at 1b (the adjudicating cell's draws)
    m_sizes = pins["arm_m_sizes"]
    spec = {}
    seed = POWER_SEED
    for variant, sh in (("gamma", shape), ("homogeneous", None)):
        for share in (None, 0.6, 0.75, 0.9):
            seed += 1
            key = f"{'null' if share is None else f'share_{share}'}/{variant}"
            spec[key] = simulate_specificity(
                m_sizes, reverse_rate=rates["1b"]["reachable_committed"],
                draws=K_NEW_3E["1b"], reverse_share=share,
                m_s_min=pins["m_s_min"], n_sims=spec_sims, seed=seed,
                shape=sh)
    named = {size: scenarios[size]["H_shortcut/gamma"]["worlds"]["SHORTCUT"]
             for size in SIZES_3E}
    half = {size: scenarios[size]["H_half/gamma"]["worlds"]["SHORTCUT"]
            for size in SIZES_3E}
    concessions = []
    if named["1b"] < POWER_BAR:
        concessions.append(
            f"UNDERPOWERED at the named alternative H_shortcut under gamma "
            f"dispersion: P(SHORTCUT) = {named['1b']:.4f} < {POWER_BAR}")
    if half["1b"] < POWER_BAR:
        concessions.append(
            f"UNDERPOWERED at H_half under gamma dispersion: P(SHORTCUT) = "
            f"{half['1b']:.4f} < {POWER_BAR} — a partial shortcut is not "
            f"reliably detectable at this budget; the minimum detectable "
            f"non-reachable/reachable rate ratio at .75 power is "
            f"{mdr['1b']['gamma']['max_ratio_at_power_75']} (gamma) / "
            f"{mdr['1b']['homogeneous']['max_ratio_at_power_75']} "
            f"(homogeneous)")
    concessions.append(
        f"410m replication: P(n ≤ 10) = "
        f"{scenarios['410m']['H0/gamma']['p_n_le_10']:.3f} under H0/gamma — "
        f"the annotation will almost surely carry THIN (§7, disclosed in "
        f"advance)")
    return {
        **pins,
        "power_bar": POWER_BAR,
        "power_seed": POWER_SEED,
        "best_case_table": st.best_case_table(n_reach + n_non, n_non, 32),
        "best_case_specificity_table":
            st.best_case_specificity_table(m_sizes, 8),
        "committed_rates": rates,
        "dispersion": disp,
        "scenarios": scenarios,
        "min_detectable_ratio": mdr,
        "calibration": calib,
        "specificity_scenarios": spec,
        "specificity_note": "competitor rates are UNKNOWN — no committed "
                            "draw has ever been scored against a "
                            "competitor — so the arm's event total is a "
                            "scenario, printed as one (§7)",
        "power_at_named_alternative": {
            "rule": "P(SHORTCUT) under H_shortcut with gamma dispersion "
                    "(the pessimistic variant) at the adjudicating cell; "
                    "H_half reported beside it",
            "1b": named["1b"], "410m_non_gating": named["410m"],
            "1b_H_half": half["1b"], "410m_H_half_non_gating": half["410m"]},
        "declared_underpowered": bool(named["1b"] < POWER_BAR),
        "underpowered_at_H_half": bool(half["1b"] < POWER_BAR),
        "concessions_printed_in_advance": concessions,
    }


def main() -> int:
    items = d.load_item_file(RUNG)
    partition = load_partition_3e(items["answers"], PARTITION_PATH,
                                  subset_pin=SUBSET_ITEMS_PIN,
                                  file_sha_pin=PARTITION_FILE_SHA256)
    if len(pt.repeat_class_len4(items["answers"])) + N_ALL_DISTINCT_LEN4 != \
            d.STRATA_PIN[4]:
        raise ValueError("len-4 stratum does not split 45 + 149")
    rec = compute(partition)
    POWER_PATH.write_text(json.dumps(rec, indent=1))
    p1 = rec["power_at_named_alternative"]["1b"]
    for line in rec["concessions_printed_in_advance"]:
        print(f"[3e power] CONCESSION: {line}", flush=True)
    print(f"[3e power] m_min {rec['m_min']}, m_s,min {rec['m_s_min']}; "
          f"P(SHORTCUT | H_shortcut, gamma, 1b) = {p1:.4f} "
          f"({'UNDERPOWERED — declared in advance' if rec['declared_underpowered'] else 'above the .75 bar'}); "
          f"shape {rec['dispersion']['shape']:.4f}; 410m P(n ≤ 10 | H0, "
          f"gamma) = "
          f"{rec['scenarios']['410m']['H0/gamma']['p_n_le_10']:.3f}; "
          f"record {POWER_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
