"""Exp 2g power (design §7): the alternative modelled in the tie
structure's own terms — per rung, most items have y = 0; the
positive-outcome count is bounded below by the committed
final-checkpoint count; within each REAL stratum, x and a latent w are
bivariate normal with ρ calibrated so the realized within-stratum
Somers' D is the target; y = 0 for the lowest-w items, else a count
in 1 … n_trained by w's rank among the positives. Every simulated
battery goes through the verdict's own code (the tree on the
permutation test's output). Bar: P(FORECAST) ≥ .75 at D_true = .15,
else DECLARED UNDERPOWERED IN ADVANCE.

Usage: python -m experiments.exp2g.power_2g  (writes power_2g.json ONCE)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2G = Path(__file__).resolve().parent
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2g import analyze_2g as an  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402

N_SIM = 1000
N_PERM_POWER = 500
D_TARGETS = (0.10, 0.15, 0.20)
BAR = 0.75
DECLARE_AT = 0.15
POWER_PATH = EXP2G / "power_2g.json"


def _ranks_to_counts(order_pos, n_steps):
    """Higher latent → emittable earlier → more checkpoints verified:
    rank 0 (the highest w among the positives) gets n_steps, the last
    positive gets at least 1; non-increasing in rank."""
    n = len(order_pos)
    return {int(i): n_steps - int(rank * n_steps / n) for rank, i in enumerate(order_pos)}


def simulate_cells(rng, rho, table, n_pos, rungs, *, n_steps=None) -> tuple:
    n_steps = n_steps or bg.n_trained("2.8b")
    cells, twin = [], []
    for r in rungs:
        strata = list(table[r]["strata"])
        n = len(strata)
        z = rng.normal(size=n)
        x = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
        w = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
        order = np.argsort(-w)
        counts = _ranks_to_counts(order[:n_pos[r]], n_steps)
        y = np.array([counts.get(i, 0) for i in range(n)], dtype=float)
        cells.append({"rung": r, "x": x, "y": y, "strata": strata})
        twin.append({"rung": r, "x": rng.normal(size=n), "y": y, "strata": strata})
    return cells, twin


def realized_d(cells) -> float:
    return float(np.mean([st.somers_d_within(c["x"], c["y"], c["strata"])["d"]
                          for c in cells]))


def calibrate_rho(target_d, table, n_pos, rungs, *, seed=0, n_cal=20) -> float:
    lo, hi = 0.0, 0.999
    for _ in range(25):
        mid = (lo + hi) / 2
        rng = np.random.default_rng(seed)
        d = float(np.mean([realized_d(simulate_cells(rng, mid, table, n_pos, rungs)[0])
                           for _ in range(n_cal)]))
        if d < target_d:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _one(rng, rho, table, n_pos, rungs, n_perm):
    cells, twin = simulate_cells(rng, rho, table, n_pos, rungs)
    s = int(rng.integers(0, 2 ** 31))
    strat = st.perm_test(cells, n_perm=n_perm, seed=s)
    raw_cells = [{**c, "strata": ["0"] * len(c["strata"])} for c in cells]
    raw = st.perm_test(raw_cells, n_perm=n_perm, seed=s)
    tw = st.perm_test(twin, n_perm=n_perm, seed=s)
    prim = {"stratified": strat, "raw": raw, "twin": tw}
    return an.verdict_tree_2g([], prim)["verdict"], strat


def power_at(rho, table, n_pos, rungs, *, n_sim=N_SIM, n_perm=N_PERM_POWER, seed=0) -> dict:
    rng = np.random.default_rng(seed)
    verdicts, Ts, ps = [], [], []
    for _ in range(n_sim):
        v, strat = _one(rng, rho, table, n_pos, rungs, n_perm)
        verdicts.append(v)
        Ts.append(strat["T"])
        ps.append(strat["p"])
    return {"rho": float(rho), "n_sim": n_sim, "n_perm": n_perm,
            "p_forecast": float(np.mean([v == "FORECAST" for v in verdicts])),
            "p_detect": float(np.mean([p < st.ALPHA for p in ps])),
            "mean_T": float(np.mean(Ts)), "sd_T": float(np.std(Ts, ddof=1)) if n_sim > 1 else 0.0,
            "Ts": [float(t) for t in Ts],
            "verdicts": {v: verdicts.count(v) for v in set(verdicts)}}


def null_reference(table, n_pos, rungs, *, n_sim=N_SIM, n_perm=N_PERM_POWER, seed=1) -> dict:
    r = power_at(0.0, table, n_pos, rungs, n_sim=n_sim, n_perm=n_perm, seed=seed)
    return {**r, "false_forecast_rate": r["p_forecast"], "null_sd_T": r["sd_T"]}


def rung_precision(rho, table, n_pos, rungs, *, seed=0, n_boot=200) -> dict:
    """One calibrated simulation at `rho` (DECLARE_AT's calibrated D):
    each rung's n_pairs (the informative-pair count feeding the
    permutation statistic) and a bootstrap standard error on
    within-stratum D, via st.bootstrap_d's 97.5/2.5 percentile CI,
    normal-approximated: SE ≈ (hi − lo) / (2 × 1.959964)."""
    rng = np.random.default_rng(seed)
    cells, _ = simulate_cells(rng, rho, table, n_pos, rungs)
    out = {}
    for c in cells:
        d = st.somers_d_within(c["x"], c["y"], c["strata"])
        boot = st.bootstrap_d(c["x"], c["y"], c["strata"], n_boot=n_boot)
        se = ((boot["hi"] - boot["lo"]) / (2 * 1.959963985)
              if np.isfinite(boot["hi"]) and np.isfinite(boot["lo"]) else None)
        out[c["rung"]] = {"n_pairs": d["n_pairs"], "d_point": d["d"],
                          "bootstrap_ci": [boot["lo"], boot["hi"]],
                          "bootstrap_se": se, "n_boot": boot["n_boot"]}
    return out


def main(out_path=POWER_PATH) -> dict:
    if Path(out_path).exists():
        raise RuntimeError(f"{out_path} exists — the power record is written ONCE")
    # build_table (strata_2g.py) unconditionally iterates
    # bg.PREDICTOR_RUNGS, so the battery it's fed must cover that full
    # 11-rung set (R_28 alone is a 7-rung subset and raises KeyError);
    # everything downstream still indexes by bg.R_28 only.
    table = sg.build_table(bg.load_battery(bg.PREDICTOR_RUNGS))
    n_pos = {r: bg.FINAL_COUNT_PIN["2.8b"][r] for r in bg.R_28}
    rec = {"rungs": list(bg.R_28), "n_pos_lower_bound": n_pos,
           "n_trained_steps": bg.n_trained("2.8b"), "bar": BAR, "declare_at": DECLARE_AT,
           "t_bar": st.T_BAR, "alpha": st.ALPHA, "alpha_twin": st.ALPHA_TWIN,
           "n_sim": N_SIM, "n_perm": N_PERM_POWER, "targets": {}}
    declare_rho = None
    for d in D_TARGETS:
        rho = calibrate_rho(d, table, n_pos, bg.R_28)
        if d == DECLARE_AT:
            declare_rho = rho
        rec["targets"][str(d)] = power_at(rho, table, n_pos, bg.R_28)
        print(f"[2g power] D_true {d}: rho {rho:.3f} P(FORECAST) "
              f"{rec['targets'][str(d)]['p_forecast']:.3f}", flush=True)
    rec["null"] = null_reference(table, n_pos, bg.R_28)
    rec["min_detectable_T"] = float(np.quantile(rec["null"]["Ts"], 0.99))
    rec["per_rung_precision"] = rung_precision(declare_rho, table, n_pos, bg.R_28)
    p = rec["targets"][str(DECLARE_AT)]["p_forecast"]
    rec["declared_status"] = ("POWERED" if p >= BAR
                              else "DECLARED UNDERPOWERED IN ADVANCE")
    rec["declaration"] = (f"P(FORECAST | D_true = {DECLARE_AT}) = {p:.3f} against the "
                          f"bar {BAR}; null false-FORECAST rate "
                          f"{rec['null']['false_forecast_rate']:.3f}; null SD of T "
                          f"{rec['null']['null_sd_T']:.4f}")
    Path(out_path).write_text(json.dumps(rec, indent=1))
    print(rec["declared_status"], "—", rec["declaration"])
    return rec


if __name__ == "__main__":
    main()
