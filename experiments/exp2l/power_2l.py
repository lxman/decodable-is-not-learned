# experiments/exp2l/power_2l.py
"""ONE power record (design §4, dial h), written at the endpoint stage
after the rung set and before the projection: 2i's machinery
(`power_2i._one_test_power`) run TWICE on the REAL predictors — Test A
with x_A^(256) (re-derived from 2k's tier through `analyze_2k.
load_tier_2k`, cross-checked against the seal) on 2g's base strata;
Test B with x_B (2i's sealed counts) in strata = base | median bucket
of x_A^(256) — n_pos bounded below by the 13B stage-1 endpoint count,
y from a latent mixing rank(x) at calibrated strength, every cell
through `analyze_2i.fires_2i`, n_trained_steps = 16. Bar: P(fires |
D = .15) ≥ .75 per test, else DECLARED UNDERPOWERED IN ADVANCE.

NEW (2k's process note, applied — dial h): `block_sd_A` prints Test
A's predictor block SD — T_A computed by `analyze_2j.t_only` on each of
x_A's four 64-draw blocks (2k's seeds 0–3) against outcomes drawn from
the endpoint-bounded latent at the D = .15 calibration (and at the
null), the SD across the four blocks averaged over simulations — beside
the null SD, so the record says in advance how far a k = 64 reading of
the same predictor would scatter, and the projection places its
verdict call inside or outside that scatter.

Refuses if the record exists, if the rung set is absent, or if either
predictor does not re-derive. Its sha is bound by `exp2l-endpoint-
sealed`; the analyzer re-derives its claims (`check_power_claims_2l`).

Usage: python -m experiments.exp2l.power_2l   (writes power_2l.json ONCE)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2L = Path(__file__).resolve().parent
if str(EXP2L.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2L.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i import power_2i as pw  # noqa: E402
from experiments.exp2j import analyze_2j as an2j  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2l import analyze_2l as an  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402
from experiments.exp2l.run.endpoint_2l import require_predictor_seals_2l  # noqa: E402

N_SIM_BLOCKS = 200
NOTE_2L = ("Computed at the endpoint stage from the REAL sealed predictors and the 13B stage-1 "
           "endpoint counts: a claim about each test's RESOLUTION on 2g's strata (A) and the "
           "median-composite strata (B), not about what will be found. Bar: P(fires | D = .15) "
           ">= .75 -> POWERED, else DECLARED UNDERPOWERED IN ADVANCE; P(fires | D = .10) is the "
           "coin-flip statement — the T >= .10 bar decides, not p. block_sd_A: how far a k = 64 "
           "reading of the same cross-family predictor would scatter across 2k's four 64-draw "
           "blocks under the same latent (dial h; 2k measured .0066 on 7B's known outcome).")


def block_sd_A(strata, bits_1b, x_a256, n_pos, rungs, *, n_steps, n_sim=N_SIM_BLOCKS, seed=2) -> dict:
    """For each simulated outcome (the latent at rho calibrated to
    D = .15 on x_A^(256), and at rho = 0), T on each of the four 64-draw
    blocks via `t_only`; the SD across blocks, averaged over sims."""
    dropped = an2i._degenerate_rungs(x_a256, strata, rungs)
    keep = tuple(r for r in rungs if r not in dropped)
    if not keep:
        return {"n_sim": 0, "mean_block_sd_at_declare": None, "mean_block_sd_null": None,
                "per_block_mean_T_at_declare": [None] * len(bk.SEEDS_2K), "blocks": len(bk.SEEDS_2K),
                "note": "every rung degenerate; nothing simulated"}
    rho = pw.calibrate_rho(pw.DECLARE_AT, strata, x_a256, n_pos, keep, n_steps=n_steps)
    blocks = {b: {r: bk.block_counts(bits_1b[r], b) for r in keep} for b in range(len(bk.SEEDS_2K))}
    res = {}
    for label, rho_ in (("at_declare", rho), ("null", 0.0)):
        rng = np.random.default_rng(seed)
        sds, per_block = [], {b: [] for b in blocks}
        for _ in range(n_sim):
            cells = pw.simulate_cells_2i(rng, rho_, strata, x_a256, n_pos, keep, n_steps=n_steps)
            out = {c["rung"]: {"y": [float(v) for v in c["y"]], "n_pos": int((np.asarray(c["y"]) > 0).sum())}
                   for c in cells}
            ts = []
            for b in blocks:
                t = an2j.t_only(blocks[b], f"1b:s{b}", out, strata, keep)["T"]
                if t is not None:
                    ts.append(t)
                    per_block[b].append(t)
            if len(ts) > 1:
                sds.append(float(np.std(ts, ddof=1)))
        res[label] = {"mean_sd": float(np.mean(sds)) if sds else None,
                      "per_block_mean_T": [float(np.mean(per_block[b])) if per_block[b] else None
                                           for b in blocks]}
    return {"n_sim": n_sim, "calibrated_rho": float(rho), "rungs": list(keep),
            "mean_block_sd_at_declare": res["at_declare"]["mean_sd"],
            "mean_block_sd_null": res["null"]["mean_sd"],
            "per_block_mean_T_at_declare": res["at_declare"]["per_block_mean_T"],
            "per_block_mean_T_null": res["null"]["per_block_mean_T"], "blocks": len(bk.SEEDS_2K)}


def main(out_path=None, *, root_2l=EXP2L, root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=None,
         blob_sha=None, blobs_bound=None, frozen_check=None) -> dict:
    bl.require_prereg_2l(tag_exists=tag_exists, blob_sha=blob_sha)
    bg.check_frozen_imports_2g()
    bi.check_frozen_2i()
    (frozen_check or bl.check_frozen_2l)()
    out_path = Path(out_path) if out_path is not None else bl.power_path(root_2l)
    if out_path.exists():
        raise RuntimeError(f"{out_path} exists — the power record is written ONCE")
    seals = require_predictor_seals_2l(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                                       root_2k=root_2k)
    rung_set = an._load_rung_set_2l(root_2l)
    r_primary = tuple(rung_set["R_PRIMARY"])
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])
    manifest = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    stage1 = an.load_endpoint_which_2l(root_2l, "stage1_final", battery, verify_fn,
                                       entry=bl.entry_13b(manifest, bl.ENDPOINT_STEP_13B))
    n_pos = {r: int(stage1[r]["correct"]) for r in r_primary}
    fp, pctx = an.load_predictors_2l(root_2i, root_2k, battery=battery, verify_fn=verify_fn,
                                     tag_exists=tag_exists, blobs_bound=blobs_bound)
    if fp:
        raise RuntimeError(f"refusing: the predictors do not re-derive cleanly: {fp[:5]}")
    cells = pctx["cells_2k"]["1b"]
    x256 = {r: cells[r]["counts"][bk.K_TOTAL] for r in r_primary}
    bits = {r: cells[r]["bits"] for r in r_primary}
    x_b = {r: pctx["x_b"][r] for r in r_primary}
    n_steps = bl.n_trained_13b()
    strata_b = an2i._composite_strata_median(strata, x256, r_primary)
    rec = {"A": pw._one_test_power(strata, x256, n_pos, r_primary, n_steps=n_steps),
           "B": pw._one_test_power(strata_b, x_b, n_pos, r_primary, n_steps=n_steps),
           "block_sd_A": block_sd_A(strata, bits, x256, n_pos, r_primary, n_steps=n_steps,
                                    n_sim=N_SIM_BLOCKS),
           "predictor_sha256": seals["predictor_sha"], "r_primary": list(r_primary),
           "primary_is_the_nine": bool(rung_set["primary_is_the_nine"]),
           "calibration_note": an2i.CALIBRATION_SENTENCE_2I, "shape_note": pw.SHAPE_NOTE_2I,
           "note": NOTE_2L}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1))
    print("A:", rec["A"]["declared_status"], "-", rec["A"]["declaration"])
    print("B:", rec["B"]["declared_status"], "-", rec["B"]["declaration"])
    print("block SD (A, at D=.15):", rec["block_sd_A"]["mean_block_sd_at_declare"],
          "| null:", rec["block_sd_A"]["mean_block_sd_null"])
    return rec


if __name__ == "__main__":
    main()
