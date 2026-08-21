"""Power, honestly (design §7) — the FROZEN PROCEDURE, pilot-driven,
run ONCE after the pilot and before main; its output (`power_2d.json`)
is the declaration main waits for and runs regardless of (ruling c).

Built in session 2 over the REALIZED outcome vector (known: 13 rising
/ 21 flat in 16 families under the frozen §5.2 rule) and fixed at the
freeze; the pilot supplies the one input that does not exist yet —
the predictor's REALIZED zero set.

THE MODEL (class-level; the sixth lesson applied in advance):

  latent L_g ~ N(μ, 1), score S_g = max(0, L_g − τ)      (a Tobit)
  non-rising rungs: μ = 0;  rising rungs: μ = d.

  τ  is set from the pilot: the fraction of NON-RISING rungs whose
     pilot predictor score is zero, z0/n0, as the censoring
     probability, continuity-corrected so τ is finite even when every
     non-rising rung is at zero: τ = Φ⁻¹((z0 + ½)/(n0 + 1)).
  d  is the FIXED EFFECT: solved (bisection, deterministic quadrature)
     so that the POPULATION AUC between a rising and a non-rising
     score — P(S1 > S0) + ½ P(S1 = S0), ties at zero counted half —
     equals AUC_true ∈ {.75, .85}; .5 is also run as the α check.

  TIES HONOURED (§7): a non-rising rung the pilot places in the zero
  set is HELD AT ZERO in every simulation (not redrawn); the remaining
  non-rising rungs draw from the POSITIVE part of their censored
  normal. A rising rung the pilot places at RAW zero (0 verified draws
  at BOTH sizes in its 8,000 pilot draws) is NOT held at zero: it is
  drawn from the alternative TRUNCATED at the pilot's CP bound, mapped
  into score units — cap_g = mean over sizes of the corrected margin
  at rate CP95_upper(0 / 4,000) = 7.49e-4 against the rung's floor.
  Every floor on this battery is ≥ .002 > 7.49e-4, so every cap_g is
  0 and the truncation IS the zero: the pilot's raw zero set is,
  under the floor rule, main's zero set — the "upper bound" of §7 is
  tight. The procedure computes the cap from the rule rather than
  assuming it, and prints it, so the freeze can see the arithmetic.

  Families are blocks: every simulated battery is judged by the SAME
  code the verdict runs — `stats_2d.primary_test` (2c's sampled
  block-permutation group at seed 0, the family-cluster bootstrap with
  drops counted) and `stats_2d.verdict_tree` with gate 1 clean.
  Power = P(PASS). DECLARED UNDERPOWERED IN ADVANCE iff power at
  AUC_true = .85 < .75 (1c/3e precedent). MAIN RUNS REGARDLESS.

The BUILD-TIME ENVELOPE (`--envelope`, no pilot needed) sweeps
hypothetical pilot zero sets over the realized outcome — how many of
the 13 rising rungs the pilot might place at raw zero, against what
fraction of the 21 flat rungs at zero — and prints power at .85 for
each, so the freeze knows the procedure's shape before the pilot
exists. The envelope is information, not a declaration.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.stats import norm

EXP2D = Path(__file__).resolve().parent
if str(EXP2D.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2D.parent.parent))

from experiments.exp2d import analyze_2d as a  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402

POWER_SEED = 20260821        # frozen at build
N_SIMS = 2000                # per AUC_true
AUC_TARGETS = (0.5, 0.75, 0.85)
DECLARATION_TARGET = 0.85    # §7: the declared-underpowered rule reads here
POWER_BAR = 0.75             # the program's bar since Exp 1
PILOT_CP_UPPER = st.clopper_pearson(0, a.PILOT_DRAWS_PER_RUNG)[1]  # 7.49e-4


# ------------------------------------------------------------ the model

def tau_from_zero_fraction(z0: int, n0: int) -> float:
    if n0 <= 0:
        raise ValueError("no non-rising rungs")
    return float(norm.ppf((z0 + 0.5) / (n0 + 1)))


def population_auc(d: float, tau: float) -> float:
    """P(S1 > S0) + ½ P(S1 = S0) for S = max(0, L − τ), L0 ~ N(0,1),
    L1 ~ N(d,1), independent. Deterministic quadrature."""
    p0z = norm.cdf(tau)            # P(S0 = 0)
    p1z = norm.cdf(tau - d)        # P(S1 = 0)
    both_zero = p0z * p1z
    one_pos = (1.0 - p1z) * p0z    # S1 > 0 = S0
    both_pos, _ = quad(lambda u: norm.pdf(u) * (1.0 - norm.cdf(u - d)),
                       tau, np.inf)
    return float(one_pos + both_pos + 0.5 * both_zero)


def solve_effect(auc_true: float, tau: float, *, lo=0.0, hi=12.0,
                 tol=1e-10) -> float:
    """The d with population_auc(d, τ) = auc_true, by bisection."""
    if auc_true <= 0.5:
        return 0.0
    f_lo = population_auc(lo, tau) - auc_true
    f_hi = population_auc(hi, tau) - auc_true
    if f_lo > 0 or f_hi < 0:
        raise ValueError(f"AUC {auc_true} not bracketed on [{lo}, {hi}] at "
                         f"tau {tau}")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if population_auc(mid, tau) - auc_true > 0:
            hi = mid
        else:
            lo = mid
        if hi - lo < tol:
            break
    return float(0.5 * (lo + hi))


def score_cap(floor: float, *, rate=PILOT_CP_UPPER) -> float:
    """The corrected margin a rate at the pilot CP bound would earn
    against `floor` — the truncation point for a pilot-raw-zero rising
    rung, in score units (0 whenever floor ≥ rate)."""
    return float(max(0.0, (rate - floor) / (1.0 - floor)))


def simulate_scores(rng, *, rising, held_zero, caps, tau, d) -> np.ndarray:
    """One simulated predictor vector over the 34 rungs.
    rising: bool per rung; held_zero: bool per rung (non-rising pilot
    zeros, forced 0); caps: per rung, None for 'no truncation', else
    the score cap for pilot-raw-zero rising rungs."""
    n = len(rising)
    s = np.zeros(n)
    for i in range(n):
        if rising[i]:
            cap = caps[i]
            if cap is None:
                L = rng.normal(d, 1.0)
            else:
                # truncated at τ + cap: draw L | L ≤ τ + cap by inverse cdf
                u = rng.uniform(0.0, norm.cdf(tau + cap - d))
                L = d + norm.ppf(max(u, 1e-300))
            s[i] = max(0.0, L - tau)
        else:
            if held_zero[i]:
                s[i] = 0.0
            else:
                # positive part: L | L > τ
                u = rng.uniform(norm.cdf(tau), 1.0)
                L = norm.ppf(min(u, 1 - 1e-16))
                s[i] = max(0.0, L - tau)
    return s


# ------------------------------------------------------------ the run

def power_at(auc_true, *, rising, held_zero, caps, tau, families,
             family_labels, n_sims=N_SIMS, seed=POWER_SEED,
             group=None, counts=None) -> dict:
    d = solve_effect(auc_true, tau)
    rng = np.random.default_rng(seed)
    y = np.asarray(rising, dtype=int)
    group = group or st.block_perm_group(families)
    counts = st.bootstrap_counts_matrix(len(set(family_labels))) \
        if counts is None else counts
    verdicts = {w: 0 for w in st.WORLDS}
    aucs = []
    for _ in range(n_sims):
        x = simulate_scores(rng, rising=rising, held_zero=held_zero,
                            caps=caps, tau=tau, d=d)
        t = st.primary_test(x, y, families, family_labels, group=group,
                            counts=counts)
        v = st.verdict_tree(gate1_diff_cells=[], auc_obs=t["auc"],
                            block_p=t["block"]["p"], ci=t["bootstrap"]["ci"])
        verdicts[v["verdict"]] += 1
        aucs.append(t["auc"])
    return {"auc_true": auc_true, "effect_d": d,
            "population_auc_check": population_auc(d, tau),
            "p_pass": verdicts["PASS"] / n_sims,
            "verdict_shares": {w: c / n_sims for w, c in verdicts.items()},
            "mean_realized_auc": float(np.mean(aucs)),
            "n_sims": n_sims}


def pilot_zero_set(pilot_predictor, outcome) -> dict:
    """From the pilot's corrected predictor (analyze_2d.
    predictor_from_tier on the pilot tier) and the realized outcome:
    the non-rising zero set, the rising raw-zero set, and the caps."""
    held_zero, caps, rising = [], [], []
    z0 = n0 = 0
    rising_raw_zero = []
    for r in a.RUNGS:
        is_r = bool(outcome["rungs"][r]["rising"])
        rising.append(is_r)
        p = pilot_predictor[r]
        if is_r:
            held_zero.append(False)
            raw0 = all(p["raw_zero"][s] for s in a.PROBE_SIZES)
            if raw0:
                rising_raw_zero.append(r)
                caps.append(float(np.mean([score_cap(outcome["rungs"][r]["floor"])
                                           for _ in a.PROBE_SIZES])))
            else:
                caps.append(None)
        else:
            n0 += 1
            z = p["score"] == 0.0
            z0 += int(z)
            held_zero.append(bool(z))
            caps.append(None)
    return {"rising": rising, "held_zero": held_zero, "caps": caps,
            "z0": z0, "n0": n0,
            "non_rising_zero_set": [r for r, h, ri in
                                    zip(a.RUNGS, held_zero, rising)
                                    if h and not ri],
            "rising_raw_zero_set": rising_raw_zero,
            "rising_raw_zero_caps": {r: c for r, c, ri in
                                     zip(a.RUNGS, caps, rising)
                                     if ri and c is not None},
            "pilot_cp_upper_rate": PILOT_CP_UPPER}


def run_procedure(pilot_predictor, outcome, *, n_sims=N_SIMS,
                  seed=POWER_SEED, targets=AUC_TARGETS) -> dict:
    zs = pilot_zero_set(pilot_predictor, outcome)
    tau = tau_from_zero_fraction(zs["z0"], zs["n0"])
    # the declaration target is always computed, whatever else is asked
    targets = tuple(dict.fromkeys(tuple(targets) + (DECLARATION_TARGET,)))
    fams = [a.FAMILY_OF[r] for r in a.RUNGS]
    group = st.block_perm_group(a.FAMILY_SIZES)
    counts = st.bootstrap_counts_matrix(bt.N_FAMILIES)
    power = {}
    for t in targets:
        power[str(t)] = power_at(t, rising=zs["rising"],
                                 held_zero=zs["held_zero"], caps=zs["caps"],
                                 tau=tau, families=a.FAMILY_SIZES,
                                 family_labels=fams, n_sims=n_sims,
                                 seed=seed, group=group, counts=counts)
    p85 = power[str(DECLARATION_TARGET)]["p_pass"]
    declared = p85 < POWER_BAR
    return {
        "procedure": "design §7, frozen at build: Tobit latent model, "
                     "τ from the pilot's non-rising zero fraction, fixed "
                     "effect d solved for the population AUC, non-rising "
                     "pilot zeros held at zero, rising pilot raw-zeros "
                     "truncated at the pilot CP bound in score units, "
                     "families as blocks, P(PASS) through the verdict's "
                     "own block test + cluster bootstrap + tree",
        "seed": seed, "n_sims": n_sims,
        "outcome": {"n_rising": int(sum(zs["rising"])),
                    "n_flat": int(len(zs["rising"]) - sum(zs["rising"]))},
        "pilot_zero_set": {k: zs[k] for k in
                           ("z0", "n0", "non_rising_zero_set",
                            "rising_raw_zero_set", "rising_raw_zero_caps",
                            "pilot_cp_upper_rate")},
        "tau": tau,
        "power": {k: {kk: vv for kk, vv in v.items()} for k, v in power.items()},
        "power_bar": POWER_BAR,
        "declaration_target": DECLARATION_TARGET,
        "declared_underpowered": bool(declared),
        "declared_status": ("DECLARED UNDERPOWERED IN ADVANCE"
                            if declared else "POWERED"),
        "run_anyway": "main runs regardless (ruling c, Michael "
                      "2026-08-21): a FAIL under DECLARED UNDERPOWERED "
                      "reads 'not detected at this resolution'",
    }


# ------------------------------------------------------------ envelope

def envelope(outcome, *, n_sims=300, seed=POWER_SEED,
             auc_true=DECLARATION_TARGET) -> dict:
    """Build-time information: power at `auc_true` over hypothetical
    pilot zero sets — k rising rungs at raw zero (the k with the
    SMALLEST corrected ascent, a worst-case-ordered choice) × a
    non-rising zero fraction grid."""
    rising_all = [bool(outcome["rungs"][r]["rising"]) for r in a.RUNGS]
    n1 = sum(rising_all)
    n0 = len(rising_all) - n1
    by_ascent = sorted([r for r in a.RUNGS if outcome["rungs"][r]["rising"]],
                       key=lambda r: outcome["rungs"][r]["corrected_ascent"])
    flat = [r for r in a.RUNGS if not outcome["rungs"][r]["rising"]]
    fams = [a.FAMILY_OF[r] for r in a.RUNGS]
    group = st.block_perm_group(a.FAMILY_SIZES)
    counts = st.bootstrap_counts_matrix(bt.N_FAMILIES)
    rows = []
    for frac in (0.5, 0.75, 1.0):
        z0 = int(round(frac * n0))
        zero_flat = set(flat[:z0])
        tau = tau_from_zero_fraction(z0, n0)
        for k in (0, 2, 4, 6, 8, 10, n1):
            raw0 = set(by_ascent[:k])
            held = [(r in zero_flat) for r in a.RUNGS]
            caps = [score_cap(outcome["rungs"][r]["floor"])
                    if r in raw0 else None for r in a.RUNGS]
            res = power_at(auc_true, rising=rising_all, held_zero=held,
                           caps=caps, tau=tau, families=a.FAMILY_SIZES,
                           family_labels=fams, n_sims=n_sims, seed=seed,
                           group=group, counts=counts)
            rows.append({"non_rising_zero_fraction": frac, "z0": z0,
                         "rising_raw_zero": k, "tau": tau,
                         "p_pass": res["p_pass"],
                         "mean_realized_auc": res["mean_realized_auc"]})
            print(f"  flat-zero {frac:.2f} (z0={z0:2d})  rising-raw-zero "
                  f"{k:2d}  τ {tau:+.3f}  P(PASS|AUC {auc_true}) = "
                  f"{res['p_pass']:.3f}  E[AUC] {res['mean_realized_auc']:.3f}",
                  flush=True)
    return {"auc_true": auc_true, "n_sims": n_sims, "rows": rows,
            "note": "build-time information over hypothetical pilot zero "
                    "sets; NOT a declaration"}


# ------------------------------------------------------------ main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", default=str(EXP2D))
    ap.add_argument("--envelope", action="store_true",
                    help="build-time sweep over hypothetical pilot zero "
                         "sets (no pilot needed; writes power_envelope_2d.json)")
    ap.add_argument("--n-sims", type=int, default=None)
    ar = ap.parse_args(argv)

    a.check_frozen_imports_2d()
    battery = bt.load_battery()
    floors = bt.floor_table(battery)
    outcome = a.load_outcome(floors, referents=a.load_referents())

    if ar.envelope:
        env = envelope(outcome, n_sims=ar.n_sims or 300)
        out = Path(ar.out_root) / "power_envelope_2d.json"
        out.write_text(json.dumps(env, indent=1))
        print(f"[2d power] envelope -> {out}")
        return 0

    out = Path(ar.out_root) / "power_2d.json"
    if out.exists():
        print(f"[2d power] {out} exists — the procedure runs ONCE; refusing "
              f"to overwrite")
        return 1
    verify_fn = a.load_verify()
    pilot_cells = a.load_sampling_tier(ar.out_root, "pilot", battery,
                                       verify_fn)
    pilot_pred = a.predictor_from_tier(pilot_cells, floors,
                                       n_draws_per_rung=a.PILOT_DRAWS_PER_RUNG)
    rec = run_procedure(pilot_pred, outcome, n_sims=ar.n_sims or N_SIMS)
    rec["pilot_predictor"] = {r: {"score": pilot_pred[r]["score"],
                                  "raw_zero": pilot_pred[r]["raw_zero"],
                                  "verified": {s: pilot_cells[(r, s)]["verified"]
                                               for s in a.PROBE_SIZES}}
                              for r in a.RUNGS}
    out.write_text(json.dumps(rec, indent=1))
    print(f"[2d power] τ {rec['tau']:+.3f}; non-rising zero set "
          f"{rec['pilot_zero_set']['z0']}/{rec['pilot_zero_set']['n0']}; "
          f"rising raw-zero {rec['pilot_zero_set']['rising_raw_zero_set']}")
    for k, v in rec["power"].items():
        print(f"  AUC_true {k}: P(PASS) = {v['p_pass']:.4f}  (d = "
              f"{v['effect_d']:.3f}, E[AUC] {v['mean_realized_auc']:.3f})")
    print(f"[2d power] {rec['declared_status']} — {rec['run_anyway']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
