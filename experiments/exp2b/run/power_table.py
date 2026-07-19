"""MC power table for the frozen verdict rule (design §5: computed and
committed WITH the freeze, replacing the design-time normal approximations).

Simulates the FULL verdict machinery per cell — the actual spearman /
permutation-p / bootstrap-CI functions from the frozen analyze.py, with the
actual precedence (FAIL veto included) — not a formula. Reduced MC depths for
tractability (N_PERM_SIM/N_BOOT_SIM below), which UNDERSTATE nothing
systematically: the permutation p at 1999 draws has floor .0005 << .01.

Bivariate normals with Pearson r = 2 sin(pi * rho_s / 6) give the target
Spearman rho_s exactly (Pearson 1907 relation for normals).

Usage: python -m run.power_table   (writes results/power_table.json + .md)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from analyze import ALPHA_PERM, RHO_BAR, bootstrap_ci, permutation_p, spearman

EXP_DIR = Path(__file__).resolve().parent.parent
NS = (20, 24, 27, 30)
TRUE_RHOS = (0.0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
N_SIMS = 400
N_PERM_SIM = 1999
N_BOOT_SIM = 1000
SEED = 20260718


def simulate_cell(n: int, rho_s: float, rng: np.random.Generator) -> dict:
    r = 2 * np.sin(np.pi * rho_s / 6)
    cov = [[1, r], [r, 1]]
    verdicts = {"PASS": 0, "FAIL": 0, "INDETERMINATE": 0}
    for s in range(N_SIMS):
        xy = rng.multivariate_normal([0, 0], cov, size=n)
        x, y = xy[:, 0], xy[:, 1]
        seed = int(rng.integers(2**31))
        rho = spearman(x, y)
        p = permutation_p(x, y, n_perm=N_PERM_SIM, seed=seed)
        ci = bootstrap_ci(x, y, n_boot=N_BOOT_SIM, seed=seed)
        if ci[0] <= 0.0 <= ci[1] or ci[1] < 0.0:
            verdicts["FAIL"] += 1
        elif p < ALPHA_PERM and rho >= RHO_BAR:
            verdicts["PASS"] += 1
        else:
            verdicts["INDETERMINATE"] += 1
    return {k: v / N_SIMS for k, v in verdicts.items()}


def main() -> None:
    rng = np.random.default_rng(SEED)
    table = {}
    for n in NS:
        for rho_s in TRUE_RHOS:
            cell = simulate_cell(n, rho_s, rng)
            table[f"n={n},rho={rho_s}"] = cell
            print(f"n={n} true_rho={rho_s}: PASS={cell['PASS']:.3f} "
                  f"FAIL={cell['FAIL']:.3f} IND={cell['INDETERMINATE']:.3f}",
                  flush=True)

    out = {"meta": {"n_sims": N_SIMS, "n_perm": N_PERM_SIM, "n_boot": N_BOOT_SIM,
                    "seed": SEED, "rule": f"PASS iff p<{ALPHA_PERM} and rho>={RHO_BAR}; "
                    "FAIL iff bootstrap CI covers 0 (veto first)"},
           "cells": table}
    (EXP_DIR / "results").mkdir(exist_ok=True)
    (EXP_DIR / "results" / "power_table.json").write_text(json.dumps(out, indent=1))

    lines = ["# Exp 2b MC power table (frozen verdict rule, simulated end-to-end)",
             "", f"{N_SIMS} sims/cell, perm={N_PERM_SIM}, boot={N_BOOT_SIM}, "
             f"seed={SEED}. Rows: true Spearman rho. Cells: P(PASS)/P(FAIL).", "",
             "| true rho | " + " | ".join(f"n={n}" for n in NS) + " |",
             "|---|" + "---|" * len(NS)]
    for rho_s in TRUE_RHOS:
        row = [f"| {rho_s} "]
        for n in NS:
            c = table[f"n={n},rho={rho_s}"]
            row.append(f"| {c['PASS']:.2f} / {c['FAIL']:.2f} ")
        lines.append("".join(row) + "|")
    (EXP_DIR / "results" / "power_table.md").write_text("\n".join(lines) + "\n")
    print("[power] written", flush=True)


if __name__ == "__main__":
    main()
