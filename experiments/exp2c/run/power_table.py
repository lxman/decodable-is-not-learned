# experiments/exp2c/run/power_table.py
"""MC calibration + power under the family-correlation model (design
§5, open item 1). Latent model per simulated battery: family effect
u_f ~ N(0,1); rung latents x = sqrt(rho_family)*u_f + sqrt(1-rho)*e for
BOTH the margin variable and (independently under H0) the ascent
variable; under H1 the two latents share a common component scaled to
target Spearman rho_true. Observed values are the latents' ranks —
Gaussian copula, so Spearman's rho is what the shared scale controls.
The naive test is the ordinary 1e5-draw permutation p on rungs; the
calibrated cutoff is the largest naive-p threshold whose rejection rate
under the family H0 is <= .01."""

import json
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr


def _battery(rng, families, rho_family, shared):
    xs, ys = [], []
    for size in families:
        uf_x, uf_y = rng.normal(size=2)
        for _ in range(size):
            c = rng.normal() * shared
            ex = np.sqrt(rho_family) * uf_x + \
                np.sqrt(1 - rho_family) * rng.normal()
            ey = np.sqrt(rho_family) * uf_y + \
                np.sqrt(1 - rho_family) * rng.normal()
            xs.append(ex + c)
            ys.append(ey + c)
    return np.array(xs), np.array(ys)


def _naive_perm_p_loop(x, y, rng, n_perm=2000):
    """Reference implementation, verbatim from the plan text (task-9 brief
    Step 3). Kept as the ground truth the vectorized `_naive_perm_p` is
    guarded against (exact p-value equality, test_naive_perm_p_equivalence);
    plan-deviation ruling ledgered in PROGRESS.md 2026-07-29."""
    obs = spearmanr(x, y).statistic
    perms = np.array([spearmanr(x, rng.permutation(y)).statistic
                      for _ in range(n_perm)])
    return (1 + np.sum(perms >= obs)) / (n_perm + 1)


def _naive_perm_p(x, y, rng, n_perm=2000):
    """Vectorized equivalent of `_naive_perm_p_loop` (ruling 2026-07-29).
    Rank-transforms once with rankdata's average-rank semantics (spearmanr's
    own ranking); draws the permutations with the SAME `rng.permutation`
    call sequence as the loop (`rng.permutation(n)` consumes the identical
    RNG stream as `rng.permutation(y)`, and rankdata is permutation-
    equivariant, so ranking-then-permuting equals permuting-then-ranking);
    vectorizes only the Pearson-on-ranks arithmetic. The observed statistic
    goes through the same vectorized arithmetic as the permuted ones, so
    the `perms >= obs` lattice ties resolve exactly as in the loop version
    (rank products are dyadic rationals summed exactly in float64). The
    p-value formula is unchanged."""
    n = len(y)
    rx = rankdata(x)
    ry = rankdata(y)
    idx = np.stack([rng.permutation(n) for _ in range(n_perm)])

    rxc = rx - rx.mean()
    ryc = ry - ry.mean()
    dx = np.sqrt(rxc @ rxc / (n - 1))
    dy = np.sqrt(ryc @ ryc / (n - 1))  # permutation-invariant

    # mirror np.corrcoef's sequential divisions ((cov/dx)/dy) and clip
    obs = np.clip((rxc @ ryc / (n - 1)) / dx / dy, -1.0, 1.0)
    covs = (ryc[idx] @ rxc) / (n - 1)
    perms = np.clip(covs / dx / dy, -1.0, 1.0)
    return (1 + np.sum(perms >= obs)) / (n_perm + 1)


def _shared_for_target_rho(rho_true):
    # calibrate the shared-component scale so pop Spearman ~= rho_true
    return np.sqrt(rho_true / max(1e-9, (1 - rho_true))) if rho_true < 1 else 10.0


def simulate(families, rho_family, rho_true, n_sims=1000, seed=0,
             n_perm=1000):
    rng = np.random.default_rng(seed)
    null_ps, alt_ps = [], []
    for _ in range(n_sims):
        x0, y0 = _battery(rng, families, rho_family, shared=0.0)
        null_ps.append(_naive_perm_p(x0, y0, rng, n_perm))
        x1, y1 = _battery(rng, families, rho_family,
                          shared=_shared_for_target_rho(rho_true))
        alt_ps.append(_naive_perm_p(x1, y1, rng, n_perm))
    null_ps, alt_ps = np.sort(null_ps), np.array(alt_ps)
    k = max(0, int(np.floor(0.01 * len(null_ps))) - 1)
    cutoff = float(null_ps[k]) if len(null_ps) else 0.01
    return {"calibrated_cutoff": cutoff,
            "alpha_at_cutoff": float(np.mean(np.array(null_ps) <= cutoff)),
            "power": float(np.mean(alt_ps <= cutoff)),
            "naive_p_dist": [float(null_ps[i])
                             for i in (0, len(null_ps) // 2, -1)]}


# ------------------------------------------------------------------- CLI

HERE = Path(__file__).resolve().parent.parent   # experiments/exp2c
RESULTS = HERE / "results"
ITEMS_DIR = HERE / "battery" / "items"

RHO_TRUE_VALUES = (0.0, 0.5, 0.6, 0.7, 0.8)
FRAGILITY_DELTA = 0.2
N_SIMS = 5000
N_PERM = 5000


def _family_sizes(items_dir: Path = ITEMS_DIR) -> list[int]:
    """Actual family sizes from the built battery's item specs. Skips
    ejections.json, which is a bare JSON list (the zero-ejections record),
    not a spec dict with a `family` field."""
    counts: dict[str, int] = {}
    for f in sorted(items_dir.glob("*.json")):
        if f.stem == "ejections":
            continue
        spec = json.loads(f.read_text())
        family = spec["family"]
        counts[family] = counts.get(family, 0) + 1
    return list(counts.values())


def _read_rho_family(results_dir: Path = RESULTS) -> float:
    d = json.loads((results_dir / "family_corr.json").read_text())
    return float(d["rho_family"])


def _run_power_table(families, rho_family_est, *, n_sims=N_SIMS,
                     n_perm=N_PERM, rho_true_values=RHO_TRUE_VALUES,
                     fragility_delta=FRAGILITY_DELTA, seed=0):
    """Runs `simulate` across rho_true_values at the estimated rho_family,
    plus the +/- fragility_delta sweep on rho_family (at rho_true=0.0, the
    calibration point) to check how much the calibrated cutoff moves.
    Returns the assembled results dict and whether the sweep is FRAGILE
    (cutoff drifts by >2x across the sweep)."""
    rho_family_sweep = [rho_family_est - fragility_delta, rho_family_est,
                        rho_family_est + fragility_delta]
    rho_family_sweep = [r for r in rho_family_sweep if 0.0 <= r <= 1.0]

    main_runs = {}
    for rho_true in rho_true_values:
        main_runs[rho_true] = simulate(families, rho_family_est, rho_true,
                                       n_sims=n_sims, seed=seed, n_perm=n_perm)

    fragility_runs = {}
    for rho_f in rho_family_sweep:
        fragility_runs[rho_f] = simulate(families, rho_f, 0.0,
                                         n_sims=n_sims, seed=seed,
                                         n_perm=n_perm)

    cutoffs = [r["calibrated_cutoff"] for r in fragility_runs.values()]
    if min(cutoffs) > 0:
        drift_ratio = max(cutoffs) / min(cutoffs)
    elif max(cutoffs) == 0:
        drift_ratio = 1.0            # all-zero sweep: no drift to report
    else:
        drift_ratio = float("inf")   # some zero, some not: unbounded drift
    fragile = drift_ratio > 2.0

    return {
        "families": families,
        "rho_family_estimate": rho_family_est,
        "n_sims": n_sims,
        "n_perm": n_perm,
        "rho_true_values": list(rho_true_values),
        "runs": {str(k): v for k, v in main_runs.items()},
        "fragility_sweep": {str(k): v for k, v in fragility_runs.items()},
        "fragility_drift_ratio": drift_ratio,
        "fragile": fragile,
    }, fragile


def _write_markdown(out: dict, path: Path) -> None:
    lines = [
        "# Experiment 2c: MC calibration + power table",
        "",
        f"Family sizes: {out['families']}",
        f"rho_family estimate: {out['rho_family_estimate']}",
        f"n_sims={out['n_sims']}, n_perm={out['n_perm']}",
        "",
        "## Power at rho_family estimate",
        "",
        "| rho_true | calibrated_cutoff | alpha_at_cutoff | power |",
        "|---|---|---|---|",
    ]
    for rho_true in out["rho_true_values"]:
        r = out["runs"][str(rho_true)]
        lines.append(f"| {rho_true} | {r['calibrated_cutoff']:.5f} | "
                     f"{r['alpha_at_cutoff']:.4f} | {r['power']:.4f} |")
    lines += [
        "",
        "## Fragility sweep (rho_family, rho_true=0.0)",
        "",
        "| rho_family | calibrated_cutoff |",
        "|---|---|",
    ]
    for rho_f, r in out["fragility_sweep"].items():
        lines.append(f"| {rho_f} | {r['calibrated_cutoff']:.5f} |")
    lines += [
        "",
        f"Drift ratio across sweep: {out['fragility_drift_ratio']:.3f}",
        f"FRAGILE: {out['fragile']}",
        "",
    ]
    path.write_text("\n".join(lines))


def main(argv=None) -> None:
    import argparse

    p = argparse.ArgumentParser(
        description="MC calibration + power table under the family model")
    p.add_argument("--items-dir", type=Path, default=ITEMS_DIR)
    p.add_argument("--results-dir", type=Path, default=RESULTS)
    p.add_argument("--n-sims", type=int, default=N_SIMS)
    p.add_argument("--n-perm", type=int, default=N_PERM)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out-json", type=Path, default=None)
    p.add_argument("--out-md", type=Path, default=None)
    args = p.parse_args(argv)

    families = _family_sizes(args.items_dir)
    rho_family_est = _read_rho_family(args.results_dir)

    out, fragile = _run_power_table(families, rho_family_est,
                                    n_sims=args.n_sims, n_perm=args.n_perm,
                                    seed=args.seed)

    out_json = args.out_json or (args.results_dir / "power_table.json")
    out_md = args.out_md or (args.results_dir / "power_table.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(out, indent=1))
    _write_markdown(out, out_md)

    if fragile:
        print(f"FRAGILE: calibrated cutoff drift ratio "
              f"{out['fragility_drift_ratio']:.3f} across rho_family sweep "
              f"{list(out['fragility_sweep'].keys())}", flush=True)
    print(f"[power_table] wrote {out_json} and {out_md} "
          f"(families={families}, rho_family={rho_family_est})", flush=True)


if __name__ == "__main__":
    main()
