"""Exp 2h power (design §4, plan Task 2): 2g's simulation shape with
one deliberate swap — x is the REAL committed 1b sampler count per
rung (`battery_2h.sampler_counts`), not simulated jointly with the
outcome through a shared latent. Most items have x = 0 (heavy
zero-inflation is the true tie structure any real run will face); the
positive-outcome count is bounded below by the committed
final-checkpoint count (`FINAL_COUNT_PIN_69`); within each rung, y is
generated from a latent w = rho * rank(x) + sqrt(1-rho^2) * noise —
mixing x's own rank at a calibrated strength — so rho=0 is
independent of the real x and rho->1 tracks it almost exactly; y = 0
for the lowest-w items, else a count in 1..n_trained by w's rank among
the positives. No twin arm (design §3.3 — 2h's tree has none). Every
simulated cell goes through the verdict's own tree
(`analyze_2h.verdict_tree_2h`) on the permutation test's output.
Bar: P(CONFIRMED) >= .75 at D_true = .15, else DECLARED UNDERPOWERED
IN ADVANCE.

Usage: python -m experiments.exp2h.power_2h  (writes power_2h.json ONCE)
Not run in this task — Task 3 runs it detached after the freeze.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

EXP2H = Path(__file__).resolve().parent
if str(EXP2H.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2H.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import analyze_2h as an  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402

N_SIM = 1000
N_PERM_POWER = 500
D_TARGETS = (0.10, 0.15, 0.20)
BAR = 0.75
DECLARE_AT = 0.15
POWER_PATH_2H = EXP2H / "power_2h.json"


def _ranks_to_counts(order_pos, n_steps):
    """Higher latent -> emittable earlier -> more checkpoints verified:
    rank 0 (the highest w among the positives) gets n_steps, the last
    positive gets at least 1; non-increasing in rank. Same formula as
    `power_2g._ranks_to_counts`, re-declared locally (a trivial pure
    function, not worth a cross-module private-name dependency)."""
    n = len(order_pos)
    return {int(i): n_steps - int(rank * n_steps / n) for rank, i in enumerate(order_pos)}


def _rankz(x) -> np.ndarray:
    """Average-tie ranks, standardized to (roughly) unit variance, so
    `rho` has a comparable meaning across rungs whose real sampler
    counts sit on very different scales/zero-inflation."""
    r = rankdata(x, method="average")
    r = r - r.mean()
    sd = r.std(ddof=0)
    return r / sd if sd > 0 else np.zeros_like(r)


def simulate_cells_69(rng, rho, table, x_real, n_pos, rungs, *, n_steps=None) -> list:
    n_steps = n_steps or bh.n_trained_69()
    cells = []
    for r in rungs:
        strata = list(table[r]["strata"])
        n = len(strata)
        x = np.asarray(x_real[r], dtype=np.float64)
        xz = _rankz(x)
        w = rho * xz + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
        order = np.argsort(-w)
        counts = _ranks_to_counts(order[:n_pos[r]], n_steps)
        y = np.array([counts.get(i, 0) for i in range(n)], dtype=float)
        cells.append({"rung": r, "x": x, "y": y, "strata": strata})
    return cells


def realized_d(cells) -> float:
    return float(np.mean([st.somers_d_within(c["x"], c["y"], c["strata"])["d"]
                          for c in cells]))


def calibrate_rho(target_d, table, x_real, n_pos, rungs, *, seed=0, n_cal=20) -> float:
    lo, hi = 0.0, 0.999
    for _ in range(25):
        mid = (lo + hi) / 2
        rng = np.random.default_rng(seed)
        d = float(np.mean([realized_d(simulate_cells_69(rng, mid, table, x_real, n_pos, rungs))
                           for _ in range(n_cal)]))
        if d < target_d:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _one(rng, rho, table, x_real, n_pos, rungs, n_perm):
    cells = simulate_cells_69(rng, rho, table, x_real, n_pos, rungs)
    s = int(rng.integers(0, 2 ** 31))
    strat = st.perm_test(cells, n_perm=n_perm, seed=s)
    verdict = an.verdict_tree_2h([], {"stratified": strat})["verdict"]
    return verdict, strat


def power_at(rho, table, x_real, n_pos, rungs, *, n_sim=N_SIM, n_perm=N_PERM_POWER,
            seed=0) -> dict:
    rng = np.random.default_rng(seed)
    verdicts, Ts, ps = [], [], []
    for _ in range(n_sim):
        v, strat = _one(rng, rho, table, x_real, n_pos, rungs, n_perm)
        verdicts.append(v)
        Ts.append(strat["T"])
        ps.append(strat["p"])
    return {"rho": float(rho), "n_sim": n_sim, "n_perm": n_perm,
            "p_confirmed": float(np.mean([v == "CONFIRMED" for v in verdicts])),
            "p_detect": float(np.mean([p < st.ALPHA for p in ps])),
            "mean_T": float(np.mean(Ts)),
            "sd_T": float(np.std(Ts, ddof=1)) if n_sim > 1 else 0.0,
            "Ts": [float(t) for t in Ts],
            "verdicts": {v: verdicts.count(v) for v in set(verdicts)}}


def null_reference(table, x_real, n_pos, rungs, *, n_sim=N_SIM, n_perm=N_PERM_POWER,
                   seed=1) -> dict:
    r = power_at(0.0, table, x_real, n_pos, rungs, n_sim=n_sim, n_perm=n_perm, seed=seed)
    return {**r, "false_confirmed_rate": r["p_confirmed"], "null_sd_T": r["sd_T"]}


def main(out_path=POWER_PATH_2H) -> dict:
    if Path(out_path).exists():
        raise RuntimeError(f"{out_path} exists — the power record is written ONCE")
    # sg.build_table (strata_2g.py) unconditionally iterates
    # bg.PREDICTOR_RUNGS, so the battery fed to it must cover that full
    # 11-rung set (R_69 alone is an 8-rung subset and raises KeyError);
    # everything downstream still indexes by bh.R_69 only.
    table = sg.build_table(bg.load_battery(bg.PREDICTOR_RUNGS))
    x_real = bh.sampler_counts("1b", bh.R_69)
    n_pos = {r: bh.FINAL_COUNT_PIN_69[r] for r in bh.R_69}
    rec = {"rungs": list(bh.R_69), "n_pos_lower_bound": n_pos,
           "n_trained_steps": bh.n_trained_69(), "bar": BAR, "declare_at": DECLARE_AT,
           "t_bar": st.T_BAR, "alpha": st.ALPHA, "n_sim": N_SIM, "n_perm": N_PERM_POWER,
           "targets": {}}
    declare_rho = None
    for d in D_TARGETS:
        rho = calibrate_rho(d, table, x_real, n_pos, bh.R_69)
        if d == DECLARE_AT:
            declare_rho = rho
        rec["targets"][str(d)] = power_at(rho, table, x_real, n_pos, bh.R_69)
        print(f"[2h power] D_true {d}: rho {rho:.3f} P(CONFIRMED) "
              f"{rec['targets'][str(d)]['p_confirmed']:.3f}", flush=True)
    rec["null"] = null_reference(table, x_real, n_pos, bh.R_69)
    rec["min_detectable_T"] = float(np.quantile(rec["null"]["Ts"], 0.99))
    p = rec["targets"][str(DECLARE_AT)]["p_confirmed"]
    rec["declared_status"] = ("POWERED" if p >= BAR
                              else "DECLARED UNDERPOWERED IN ADVANCE")
    rec["declaration"] = (f"P(CONFIRMED | D_true = {DECLARE_AT}) = {p:.3f} against the bar "
                          f"{BAR}; null false-CONFIRMED rate "
                          f"{rec['null']['false_confirmed_rate']:.3f}; null SD of T "
                          f"{rec['null']['null_sd_T']:.4f}")
    Path(out_path).write_text(json.dumps(rec, indent=1))
    print(rec["declared_status"], "—", rec["declaration"])
    return rec


if __name__ == "__main__":
    main()
