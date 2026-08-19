"""Exact §7 tables from the frozen analysis (doc Open item 2) —
committed as `power_3d.json` and re-run byte-identically at the
freeze.

WHAT IS COMPUTED. m_min (§6's UNINFORMATIVE bar, predicted direction;
the anti direction disclosed beside it); the exact-null inputs (the
per-stratum doubled-midrank multisets the frozen DP consumes, plus
the best-case rejection table m = 1..12); world probabilities and
power under three truths per cell — FLAT (every item at the committed
pooled rate), OBSERVED-CONCENTRATION (per-item rates ∝ committed
pooled per-item counts with add-λ smoothing, scaled to the committed
cell rate), and HALF-CONCENTRATION (counts at half strength, same λ,
same scaling); P(UNINFORMATIVE) and P(|F| ≤ 4) under the committed
flat rate (§6's named build-table entries); and the λ sensitivity
grid.

THE λ RULE, FROZEN BEFORE THE NUMBERS (build ledger, PROGRESS.md).
λ = μ̂² / (V̂ − μ̂) computed from the 1b committed per-item fire
counts — the Gamma-shape moment estimator for a Gamma-Poisson rate
mixture, i.e. the committed record's OWN measurement of its
overdispersion. Rationale: the alternative §7 names is "the committed
heterogeneity is real and persists"; a conventional add-half
(Jeffreys) λ = 0.5 CONTRADICTS the committed record it is supposed to
encode — it flattens the alternative to near-null (the sensitivity
grid shows the collapse) because the smoothing mass then dwarfs the
10 committed counts. One λ for the design, from the adjudicating
cell's counts, applied to both cells (410m's three singleton fires
carry no overdispersion signal of their own: V̂ < μ̂ there, the
estimator is undefined, and 410m is non-gating throughout). The
half-effect alternative halves the counts, not λ.

HONESTY CLAUSE (§7, verbatim obligation): 13 fires calibrate any
alternative loosely. If power at the observed-concentration
alternative lands under the program's .75 bar, the experiment is
DECLARED UNDERPOWERED IN ADVANCE and runs anyway with that concession
printed (1c precedent) — the tranche also buys rate resolution
regardless of the rank verdict.

Everything here is detection-and-rank arithmetic on frozen inputs:
no model, no draws, no new quantities for any real cell.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP3D = Path(__file__).resolve().parent
if str(EXP3D.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3D.parent.parent))

from experiments.exp3d import functional_3d as fl  # noqa: E402
from experiments.exp3d import rank_test_3d as rt  # noqa: E402
from experiments.exp3d.analyze_3d import (  # noqa: E402
    COMMITTED_BASE_DRAWS, COMMITTED_FIRE_COUNTS, K_NEW_3D, N_ITEMS,
    POWER_PATH, SIZES_3D, check_frozen_imports_3d, committed_fired_sets,
    load_item_file,
)

POWER_SIM_SEED = 20260819     # frozen at build (doc Open item 3 family)
POWER_SIM_M = 200_000         # simulated tranches per (cell, truth)
POWER_BAR = 0.75              # the program's bar (1c precedent)
LAMBDA_SENSITIVITY = (0.01, 0.1, 0.5, 1.0)
BEST_CASE_TABLE_M = 12


def lambda_hat() -> dict:
    """The frozen λ rule: Gamma-shape moment estimator on the 1b
    committed per-item counts. μ̂ = mean count, V̂ = population
    variance; λ = μ̂²/(V̂ − μ̂), defined only when V̂ > μ̂
    (overdispersion present — asserted, not assumed)."""
    counts = np.zeros(N_ITEMS)
    for i, k in COMMITTED_FIRE_COUNTS["1b"].items():
        counts[i] = k
    mu = counts.mean()
    var = counts.var()
    if var <= mu:
        raise ValueError(
            f"1b committed counts show no overdispersion (V̂ = {var} ≤ "
            f"μ̂ = {mu}) — the frozen λ rule is undefined and the "
            f"build must stop and re-derive, not guess")
    lam = mu * mu / (var - mu)
    return {"mu_hat": float(mu), "var_hat": float(var),
            "lambda": float(lam),
            "rule": "lambda = mu^2/(V - mu), Gamma-shape moment "
                    "estimator on the 1b committed per-item counts; "
                    "frozen before any power number was computed "
                    "(PROGRESS.md, build ledger)"}


def alternative_rates(size: str, lam: float, effect: float) -> np.ndarray:
    """Per-item per-draw rates: r_i ∝ (effect × c_i + λ), normalized so
    the MEAN per-item rate equals the committed pooled cell rate —
    'scaled to the committed cell rate' (§7). effect = 1 is the
    observed-concentration truth, 0.5 the half-effect, 0 the flat
    truth (any λ > 0 then gives exactly flat)."""
    c_counts = np.zeros(N_ITEMS)
    for i, k in COMMITTED_FIRE_COUNTS[size].items():
        c_counts[i] = k
    w = effect * c_counts + lam
    cell_rate = sum(COMMITTED_FIRE_COUNTS[size].values()) \
        / COMMITTED_BASE_DRAWS[size]
    r = cell_rate * N_ITEMS * w / w.sum()
    return r


def simulate_worlds(values, strata, m_min, size, rates, *,
                    m_sims=POWER_SIM_M, seed=POWER_SIM_SEED) -> dict:
    """Simulate the tranche under per-item per-draw `rates`, classify
    every simulated fired set through the SAME machinery the verdict
    runs (exact-DP p at the observed composition, §6's mechanical
    order), and tally world probabilities."""
    k = K_NEW_3D[size]
    q = 1.0 - (1.0 - rates) ** k
    rng = np.random.default_rng(seed)
    mids = fl.stratified_midranks(values, strata)
    keys = sorted(str(L) for L in strata)
    per_q = {kk: rt.subset_sum_dist(
        rt.doubled_midranks(mids, strata[int(kk)]), rt.DP_M_CAP)
        for kk in keys}
    stratum_of_item = {}
    for L, idx in strata.items():
        for i in idx:
            stratum_of_item[i] = str(L)
    d2 = np.array([int(round(mids[i] * 2)) for i in range(len(rates))])
    strat_idx = {kk: np.array(strata[int(kk)]) for kk in keys}

    pmf_cache: dict[tuple, np.ndarray] = {}
    tallies = {"STRUCTURED": 0, "ANTI-STRUCTURED": 0,
               "UNSTRUCTURED": 0, "UNINFORMATIVE": 0}
    thin = 0
    f_sizes = np.zeros(m_sims, dtype=np.int64)
    fire_draws = np.zeros(m_sims, dtype=np.float64)
    chunk = 5_000
    done = 0
    while done < m_sims:
        n = min(chunk, m_sims - done)
        u = rng.random((n, len(rates)))
        fired = u < q[None, :]
        f_sizes[done:done + n] = fired.sum(axis=1)
        for row in range(n):
            f = np.nonzero(fired[row])[0]
            if len(f) == 0:
                tallies["UNINFORMATIVE"] += 1
                thin += 1
                continue
            comp = tuple(int(np.isin(strat_idx[kk], f).sum())
                         for kk in keys)
            if comp not in pmf_cache:
                pmf_cache[comp] = rt.convolve_composition(
                    per_q, dict(zip(keys, comp)))
            t2 = int(d2[f].sum())
            p_low, p_high = rt.tail_p(pmf_cache[comp], t2)
            if len(f) <= rt.THIN_MAX:
                thin += 1
            if p_low <= rt.ALPHA_3D:
                tallies["STRUCTURED"] += 1
            elif p_high <= rt.ALPHA_3D:
                tallies["ANTI-STRUCTURED"] += 1
            elif len(f) >= m_min:
                tallies["UNSTRUCTURED"] += 1
            else:
                tallies["UNINFORMATIVE"] += 1
        done += n
    exp_draws = float((rates * k).sum())
    return {
        "worlds": {w: n / m_sims for w, n in tallies.items()},
        "p_thin_qualifier": thin / m_sims,
        "expected_new_fire_draws": exp_draws,
        "expected_F": float(f_sizes.mean()),
        "p_F_le_4": float((f_sizes <= 4).mean()),
        "p_F_lt_m_min": float((f_sizes < m_min).mean()),
        "n_sims": m_sims,
        "n_distinct_compositions": len(pmf_cache),
    }


def best_case_table(values, strata, m_top=BEST_CASE_TABLE_M) -> list:
    """For m = 1..m_top: the best-case (cheapest-placement, best
    composition) one-sided p — the exact-null table m_min is read
    from, committed for the record."""
    mids = fl.stratified_midranks(values, strata)
    keys = sorted(str(L) for L in strata)
    per_q = {kk: rt.subset_sum_dist(
        rt.doubled_midranks(mids, strata[int(kk)]), rt.DP_M_CAP)
        for kk in keys}
    cheap = {kk: sorted(rt.doubled_midranks(mids, strata[int(kk)]))
             for kk in keys}
    out = []
    for m in range(1, m_top + 1):
        best = None
        best_comp = None
        for comp in rt._compositions(m, keys, strata):
            t2 = sum(sum(cheap[kk][: comp[kk]]) for kk in keys)
            pmf = rt.convolve_composition(per_q, comp)
            p = rt.tail_p(pmf, t2)[0]
            if best is None or p < best:
                best, best_comp = p, comp
        out.append({"m": m, "best_case_p": best,
                    "best_composition": best_comp,
                    "rejects_at_alpha": bool(best <= rt.ALPHA_3D)})
    return out


def build() -> dict:
    check_frozen_imports_3d()
    items = load_item_file("reverse_string")
    answers = items["answers"]
    sel = fl.select_winner(answers, *[committed_fired_sets()[s]
                                      for s in ("1b", "410m")])
    name, fn = fl.CANDIDATES[sel["winner_index"]]
    values = fl.candidate_values(fn, answers)
    strata = fl.strata_of(answers)
    mids = fl.stratified_midranks(values, strata)

    m_min = rt.m_min_of(values, strata)
    m_min_anti = rt.m_min_of(values, strata, direction="high")
    lam = lambda_hat()

    null_inputs = {
        str(L): {"n_items": len(idx),
                 "doubled_midranks_multiset": sorted(
                     rt.doubled_midranks(mids, idx))}
        for L, idx in sorted(strata.items())}

    cells = {}
    for size in SIZES_3D:
        flat = simulate_worlds(values, strata, m_min, size,
                               alternative_rates(size, 1.0, 0.0))
        obs = simulate_worlds(values, strata, m_min, size,
                              alternative_rates(size, lam["lambda"], 1.0))
        half = simulate_worlds(values, strata, m_min, size,
                               alternative_rates(size, lam["lambda"],
                                                 0.5))
        cells[size] = {"FLAT_committed_rate": flat,
                       "OBSERVED_CONCENTRATION": obs,
                       "HALF_CONCENTRATION": half}

    sensitivity = {}
    for lam_s in LAMBDA_SENSITIVITY:
        r = simulate_worlds(values, strata, m_min, "1b",
                            alternative_rates("1b", lam_s, 1.0))
        sensitivity[f"{lam_s:g}"] = {
            "power_STRUCTURED": r["worlds"]["STRUCTURED"],
            "expected_F": r["expected_F"]}

    power_obs_1b = cells["1b"]["OBSERVED_CONCENTRATION"]["worlds"][
        "STRUCTURED"]

    # ---- doc quotes, cross-checked (3c's convention: discrepancies
    # ledgered, never silently absorbed)
    t4 = fl.tie_structure(values, strata)["4"]
    cheapest_len4 = t4["groups"][0]["count"]
    quotes = {
        "expected_F_8_to_12_at_1b": {
            "quoted": "8-12 (§6)",
            "computed": cells["1b"]["OBSERVED_CONCENTRATION"][
                "expected_F"],
            "agrees": 8.0 <= cells["1b"]["OBSERVED_CONCENTRATION"][
                "expected_F"] <= 12.0},
        "expected_new_fires_15_18_at_1b": {
            "quoted": "15-18 (§3)",
            "computed": cells["1b"]["FLAT_committed_rate"][
                "expected_new_fire_draws"],
            "agrees": 14.0 <= cells["1b"]["FLAT_committed_rate"][
                "expected_new_fire_draws"] <= 18.5},
        "expected_new_fires_2_3_at_410m": {
            "quoted": "2-3 (§3)",
            "computed": cells["410m"]["FLAT_committed_rate"][
                "expected_new_fire_draws"],
            "agrees": 1.8 <= cells["410m"]["FLAT_committed_rate"][
                "expected_new_fire_draws"] <= 3.2},
        "single_rank1_fire_p_1_of_194": {
            "quoted": "1/194 = 0.00515 (§6's illustrative arithmetic)",
            "computed": cheapest_len4 / 194.0,
            "agrees": cheapest_len4 == 1,
            "note": f"the realized winner has NO unique rank-1 item in "
                    f"the len-4 stratum: its cheapest tied class holds "
                    f"{cheapest_len4} items, so a single len-4 fire's "
                    f"best p is {cheapest_len4}/194 = "
                    f"{cheapest_len4 / 194.0:.4f}. The §6 mechanism "
                    f"(m_min from frozen ranks) is unaffected; the "
                    f"doc's tie-free example number is a ledgered slip "
                    f"if this disagrees."},
        "bucket_52_items": {
            "quoted": 52,
            "computed": len(fl.decile_bucket(values, strata)),
            "agrees": len(fl.decile_bucket(values, strata)) == 52},
    }

    return {
        "winner": sel["winner"],
        "alpha": rt.ALPHA_3D,
        "mc_permutation": {"count": rt.MC_PERM_COUNT,
                           "seed": rt.MC_PERM_SEED,
                           "dp_cap": rt.DP_M_CAP,
                           "note": "exact DP adjudicates every "
                                   "composition within the cap; the "
                                   "seeded MC clause is the frozen "
                                   "fallback past it"},
        "power_sim": {"seed": POWER_SIM_SEED, "n_sims": POWER_SIM_M},
        "m_min": m_min,
        "m_min_anti_direction_disclosed": m_min_anti,
        "best_case_table": best_case_table(values, strata),
        "null_inputs": null_inputs,
        "lambda": lam,
        "cells": cells,
        "lambda_sensitivity_1b_observed": sensitivity,
        "power_bar": POWER_BAR,
        "power_at_observed_concentration_1b": power_obs_1b,
        "declared_underpowered_in_advance": bool(power_obs_1b
                                                 < POWER_BAR),
        "doc_quotes_check": quotes,
        "luck_floors": {str(L): 26.0 ** (-L) for L in (4, 5, 6)},
    }


if __name__ == "__main__":
    tables = build()
    POWER_PATH.write_text(json.dumps(tables, indent=1, sort_keys=True)
                          + "\n")
    print(f"winner: {tables['winner']}")
    print(f"m_min = {tables['m_min']} (anti direction "
          f"{tables['m_min_anti_direction_disclosed']})")
    print(f"lambda = {tables['lambda']['lambda']:.6f}")
    for size in SIZES_3D:
        cc = tables["cells"][size]
        print(f"{size}: power(OBS) = "
              f"{cc['OBSERVED_CONCENTRATION']['worlds']['STRUCTURED']:.4f}"
              f" | power(HALF) = "
              f"{cc['HALF_CONCENTRATION']['worlds']['STRUCTURED']:.4f}"
              f" | flat P(reject) = "
              f"{cc['FLAT_committed_rate']['worlds']['STRUCTURED']:.4f}"
              f" | E|F| OBS = "
              f"{cc['OBSERVED_CONCENTRATION']['expected_F']:.1f}"
              f" | P(UNINF) flat = "
              f"{cc['FLAT_committed_rate']['worlds']['UNINFORMATIVE']:.4f}"
              f" | P(|F|<=4) flat = "
              f"{cc['FLAT_committed_rate']['p_F_le_4']:.4f}")
    print(f"declared underpowered in advance: "
          f"{tables['declared_underpowered_in_advance']} "
          f"(bar {POWER_BAR})")
    print("lambda sensitivity (1b, observed): "
          + ", ".join(f"λ={k}: {v['power_STRUCTURED']:.3f}"
                      for k, v in sorted(
                          tables["lambda_sensitivity_1b_observed"]
                          .items(), key=lambda kv: float(kv[0]))))
    bad = [k for k, v in tables["doc_quotes_check"].items()
           if not v["agrees"]]
    print("doc quotes: " + ("ALL AGREE" if not bad
                            else f"DISAGREE (ledger): {bad}"))
    print(f"written: {POWER_PATH}")
