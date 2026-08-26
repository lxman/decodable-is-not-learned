# experiments/exp2i/power_2i.py
"""Exp 2i power (design §4, ruling 9): 2h's simulation shape run
TWICE, once per test — Test A with the REAL committed x_A
(`battery_2i.sampler_counts_pythia("1b", R_CAP)`) in 2g's plain strata,
Test B with the sealed x_B in the composite strata (x_A's zero cut,
`analyze_2i._composite_strata`). The positive-outcome count per rung
(`n_pos`) is bounded below by the `stage1_final` endpoint count — the
only real 7B quantity known at this stage (the sweep has not run). x is
the REAL predictor in both cases (never simulated); within each rung, y
is generated from a latent w = rho * rank(x) + sqrt(1-rho^2) * noise,
mixing x's own rank at a calibrated strength (rho=0 independent, rho->1
tracks x almost exactly); y = 0 for the lowest-w items, else a count in
1..n_trained by w's rank among the positives. Every simulated cell goes
through `analyze_2i.fires_2i` — the SAME firing rule the analyzer uses
on real data (ruling 9: one implementation, not two that could drift).

Bar: P(fires | D_true = .15) >= .75 per test, else DECLARED
UNDERPOWERED IN ADVANCE for that test. THIN is printed when
len(R_CAP) < 3 (design §4); the calibration note (each test at alpha
.01, the union of the four worlds not alpha-calibrated) rides on the
record.

Runs at stage 2 (after the endpoint), by the supervisor, detached, once
R_CAP and the endpoint are known; its sha is bound by ENDPOINT_SEAL_TAG,
not a code literal (ruling 1 — the analyzer requires the tag to carry
power_2i.json, rung_set_2i.json and every endpoint record byte-
identical).

Usage: python -m experiments.exp2i.power_2i  (writes power_2i.json ONCE)
Not run in this task — the supervisor runs it detached after stage 2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

EXP2I = Path(__file__).resolve().parent
if str(EXP2I.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2I.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402

N_SIM = 1000
N_PERM_POWER = 500
D_TARGETS = (0.10, 0.15, 0.20)
BAR = 0.75
DECLARE_AT = 0.15

# FREEZE attack item 8 (3d's sixth lesson, stated in advance rather
# than discovered at close-out). The number this record declares is a
# claim about the alternative's SHAPE, not only its size: y is
# generated from a latent that mixes rank(x) with noise at ITEM grain
# inside each rung's own strata, so P(fires) is calibrated against an
# item-level rank-concordance alternative. If the true effect is
# CLASS-level — a shift shared by every item in some stratum or
# equivalence class, which is exactly the shape 3d's own power table
# got wrong by a factor of ~6 — this table does not transfer, in
# either direction. It rides on the record so a reader of the
# declaration meets the caveat with it, not in a design doc elsewhere.
SHAPE_NOTE_2I = (
    "This power table is calibrated against an ITEM-LEVEL alternative: within "
    "each rung, y is generated from a latent mixing rank(x) with noise inside "
    "the rung's own strata. It is a claim about the alternative's shape, not "
    "only its size. A CLASS-level effect — a shift shared by every item in an "
    "equivalence class, the shape exp 3d's frozen power model mis-specified by "
    "roughly a factor of six — is not modelled here, and neither POWERED nor "
    "DECLARED UNDERPOWERED IN ADVANCE transfers to it. No class-level "
    "sensitivity is simulated (2h did not either); adding one would be a new "
    "statistic, not a pin, and was left to ratification.")


def _ranks_to_counts(order_pos, n_steps):
    """Higher latent -> emittable earlier -> more grid points verified:
    rank 0 (the highest w among the positives) gets n_steps, the last
    positive gets at least 1; non-increasing in rank. Same formula as
    `power_2h._ranks_to_counts`, re-declared locally (a trivial pure
    function, not worth a cross-module private-name dependency)."""
    n = len(order_pos)
    return {int(i): n_steps - int(rank * n_steps / n) for rank, i in enumerate(order_pos)}


def _rankz(x) -> np.ndarray:
    """Average-tie ranks, standardized to (roughly) unit variance, so
    `rho` has a comparable meaning across rungs whose real predictor
    counts sit on very different scales/zero-inflation."""
    r = rankdata(x, method="average")
    r = r - r.mean()
    sd = r.std(ddof=0)
    return r / sd if sd > 0 else np.zeros_like(r)


def simulate_cells_2i(rng, rho, strata, x_real, n_pos, rungs, *, n_steps) -> list:
    cells = []
    for r in rungs:
        s = list(strata[r]["strata"])
        n = len(s)
        x = np.asarray(x_real[r], dtype=np.float64)
        xz = _rankz(x)
        w = rho * xz + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
        order = np.argsort(-w)
        counts = _ranks_to_counts(order[:n_pos[r]], n_steps)
        y = np.array([counts.get(i, 0) for i in range(n)], dtype=float)
        cells.append({"rung": r, "x": x, "y": y, "strata": s})
    return cells


def realized_d(cells) -> float:
    return float(np.mean([st.somers_d_within(c["x"], c["y"], c["strata"])["d"]
                          for c in cells]))


def calibrate_rho(target_d, strata, x_real, n_pos, rungs, *, n_steps, seed=0,
                  n_cal=20) -> float:
    lo, hi = 0.0, 0.999
    for _ in range(25):
        mid = (lo + hi) / 2
        rng = np.random.default_rng(seed)
        d = float(np.mean([realized_d(simulate_cells_2i(rng, mid, strata, x_real, n_pos,
                                                         rungs, n_steps=n_steps))
                           for _ in range(n_cal)]))
        if d < target_d:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _one(rng, rho, strata, x_real, n_pos, rungs, n_perm, n_steps):
    cells = simulate_cells_2i(rng, rho, strata, x_real, n_pos, rungs, n_steps=n_steps)
    s = int(rng.integers(0, 2 ** 31))
    strat = st.perm_test(cells, n_perm=n_perm, seed=s)
    fires = an.fires_2i({"stratified": strat})
    return fires, strat


def power_at(rho, strata, x_real, n_pos, rungs, *, n_steps, n_sim=N_SIM,
            n_perm=N_PERM_POWER, seed=0) -> dict:
    rng = np.random.default_rng(seed)
    fires_l, Ts, ps = [], [], []
    for _ in range(n_sim):
        fires, strat = _one(rng, rho, strata, x_real, n_pos, rungs, n_perm, n_steps)
        fires_l.append(fires)
        Ts.append(strat["T"])
        ps.append(strat["p"])
    return {"rho": float(rho), "n_sim": n_sim, "n_perm": n_perm,
            "p_fires": float(np.mean(fires_l)),
            "p_detect": float(np.mean([p < an.ALPHA for p in ps])),
            "mean_T": float(np.mean(Ts)),
            "sd_T": float(np.std(Ts, ddof=1)) if n_sim > 1 else 0.0,
            "Ts": [float(t) for t in Ts]}


def null_reference(strata, x_real, n_pos, rungs, *, n_steps, n_sim=N_SIM,
                   n_perm=N_PERM_POWER, seed=1) -> dict:
    r = power_at(0.0, strata, x_real, n_pos, rungs, n_steps=n_steps, n_sim=n_sim,
                n_perm=n_perm, seed=seed)
    return {**r, "false_fire_rate": r["p_fires"], "null_sd_T": r["sd_T"]}


def _one_test_power(strata, x_real, n_pos, rungs, *, n_steps) -> dict:
    # N_SIM/N_PERM_POWER are read here BY NAME at call time (not baked
    # into power_at's/null_reference's own default-argument values,
    # which are frozen at module-import time) and threaded explicitly
    # into every call below — the only way a test's monkeypatch of the
    # module attributes actually shrinks the run.
    n_sim, n_perm = N_SIM, N_PERM_POWER
    # I-3: the SAME degeneracy rule the analyzer applies to the real
    # predictor/strata before running its own primary test (`an.
    # _degenerate_rungs`, not a copy) — a rung whose predictor has
    # fewer than two distinct values inside every stratum contributes
    # nothing to Somers' D, so simulating power over it would credit
    # the record with detecting a signal on a rung the real test can
    # never read. `dropped_degenerate` is printed; `thin` is judged on
    # the SURVIVING set (`keep`), not the rungs the caller passed in.
    dropped = an._degenerate_rungs(x_real, strata, rungs)
    keep = tuple(r for r in rungs if r not in dropped)
    rec = {"rungs": list(rungs), "dropped_degenerate": list(dropped),
          "rungs_simulated": list(keep), "n_pos_lower_bound": dict(n_pos),
          "n_trained_steps": n_steps, "bar": BAR, "declare_at": DECLARE_AT,
          "t_bar": an.T_BAR, "alpha": an.ALPHA, "n_sim": n_sim, "n_perm": n_perm,
          "thin": len(keep) < 3, "targets": {}}
    if not keep:
        # every rung lost to degeneracy (or none were eligible to begin
        # with) — there is nothing left to simulate power over; declare
        # THIN rather than crash inside `simulate_cells_2i`/`perm_test`
        # on an empty cell list (ruling 18's power-side analogue).
        rec["declared_status"] = "THIN"
        rec["declaration"] = (f"every rung lost to predictor degeneracy "
                              f"({dropped} of {list(rungs)}) — power cannot be "
                              f"simulated over zero rungs")
        return rec
    declare_p = None
    for d in D_TARGETS:
        rho = calibrate_rho(d, strata, x_real, n_pos, keep, n_steps=n_steps)
        p = power_at(rho, strata, x_real, n_pos, keep, n_steps=n_steps, n_sim=n_sim,
                     n_perm=n_perm)
        rec["targets"][str(d)] = {**p, "calibrated_rho": rho}
        if d == DECLARE_AT:
            declare_p = p["p_fires"]
        print(f"[2i power] D_true {d}: rho {rho:.3f} P(fires) {p['p_fires']:.3f}",
             flush=True)
    rec["null"] = null_reference(strata, x_real, n_pos, keep, n_steps=n_steps,
                                 n_sim=n_sim, n_perm=n_perm)
    rec["min_detectable_T"] = float(np.quantile(rec["null"]["Ts"], 0.99))
    if declare_p is None:
        # DECLARE_AT is not among the (possibly overridden, e.g. by a test)
        # D_TARGETS — power the declaration off a fresh calibration at
        # DECLARE_AT rather than silently skipping the declaration.
        rho = calibrate_rho(DECLARE_AT, strata, x_real, n_pos, keep, n_steps=n_steps)
        declare_p = power_at(rho, strata, x_real, n_pos, keep, n_steps=n_steps,
                             n_sim=n_sim, n_perm=n_perm)["p_fires"]
    rec["declared_status"] = ("POWERED" if declare_p >= BAR
                              else "DECLARED UNDERPOWERED IN ADVANCE")
    rec["declaration"] = (f"P(fires | D_true = {DECLARE_AT}) = {declare_p:.3f} against "
                          f"the bar {BAR}; null false-fire rate "
                          f"{rec['null']['false_fire_rate']:.3f}; null SD of T "
                          f"{rec['null']['null_sd_T']:.4f}")
    return rec


def main(out_path=None, *, root=EXP2I, tag_exists=None, blob_sha=None) -> dict:
    # review minor: the prereg tag + frozen-instrument checks every
    # other stage runner applies BEFORE any write — power_2i.main was
    # the one writer that skipped straight to the write-once guard.
    an.require_prereg_2i(tag_exists=tag_exists, blob_sha=blob_sha)
    bi.check_frozen_2i()

    out_path = Path(out_path) if out_path is not None else bi.power_path(root)
    if out_path.exists():
        raise RuntimeError(f"{out_path} exists — the power record is written ONCE")

    # refuses without rung_set_2i.json and predictor_2i.json (ruling 9) —
    # both loaders raise FileNotFoundError/ValueError naming the path.
    rung_set = an._load_rung_set(root)
    r_cap = tuple(rung_set["R_CAP"])
    predictor_rec = an._load_predictor_seal_content(root)

    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])

    manifest = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    n_steps = bi.n_trained_7b()
    stage1_entry = bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B)

    battery = bg.load_battery()
    from experiments.exp2d import analyze_2d as a2d
    verify_fn = a2d.load_verify()
    stage1 = an.load_endpoint_which(root, "stage1_final", battery, verify_fn,
                                    entry=stage1_entry, predictor_sha=predictor_rec["sha256"])
    n_pos = {r: int(stage1[r]["correct"]) for r in r_cap}

    x_a = bi.sampler_counts_pythia("1b", r_cap)
    x_b = bi.sampler_counts_olmo(r_cap, root=root, battery=battery, verify_fn=verify_fn)
    strata_b = an._composite_strata(strata, x_a, r_cap)

    rec = {"A": _one_test_power(strata, x_a, n_pos, r_cap, n_steps=n_steps),
          "B": _one_test_power(strata_b, x_b, n_pos, r_cap, n_steps=n_steps),
          "calibration_note": an.CALIBRATION_SENTENCE_2I,
          "shape_note": SHAPE_NOTE_2I}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1))
    print("A:", rec["A"]["declared_status"], "-", rec["A"]["declaration"])
    print("B:", rec["B"]["declared_status"], "-", rec["B"]["declaration"])
    return rec


if __name__ == "__main__":
    main()
