# experiments/exp2n/power_2n.py
"""ONE power record (design §4, dial h), written at the endpoint stage
after the rung set and before the projection: 2i's machinery
(`power_2i._one_test_power`) run TWICE on the REAL predictors — Test A
with x_A^(256) and Test B with x_B, BOTH on 2g's base strata (dial b:
unconditioned) — n_pos bounded below by the Comma v0.1-1T stage-1
endpoint count, y from a latent mixing rank(x) at calibrated strength, every
cell through `analyze_2i.fires_2i`, n_trained_steps = 24. Bar: P(fires
| D = .15) ≥ .75 per test, else DECLARED UNDERPOWERED IN ADVANCE.
`block_sd_A` as 2l (dial h): T_A by `analyze_2j.t_only` on each of
x_A's four 64-draw blocks against outcomes drawn from the endpoint-
bounded latent at D = .15 (and at the null), the SD across the four
blocks averaged over simulations. `delta_sd` (dial h, the annotation C
line): the null and at-declare SD of Delta = T(x_B thinned) − T(x_A^256)
across simulated outcomes, plus the paired-bootstrap SD of Delta on one
null draw, from which `min_detectable_delta` follows by the stated
normal approximation — the annotation's own resolution claim, printed
once and never re-run. Refuses if the record exists, if the rung set is
absent, or if either predictor does not re-derive.

Usage: python -m experiments.exp2n.power_2n   (writes power_2n.json ONCE)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2N = Path(__file__).resolve().parent
if str(EXP2N.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2N.parent.parent))

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
from experiments.exp2n import analyze_2n as an  # noqa: E402
from experiments.exp2n import battery_2n as bn  # noqa: E402
from experiments.exp2n.run.endpoint_2n import require_predictor_seals_2n  # noqa: E402

N_SIM_BLOCKS = 200
N_SIM_DELTA = 200
N_BOOT_DELTA = 200
DELTA_FORMULA_2N = ("min_detectable_delta = 2.63 * delta_boot_sd_null (normal approximation: CI95 excludes zero "
                    "with power .75)")
NOTE_2N = ("Computed at the endpoint stage from the REAL sealed predictors and the Comma v0.1-1T "
           "stage-1 endpoint counts: a claim about each test's RESOLUTION on 2g's base strata (both tests "
           "unconditioned, dial b), not about what will be found. Bar: P(fires | D = .15) >= .75 -> "
           "POWERED, else DECLARED UNDERPOWERED IN ADVANCE; P(fires | D = .10) is the coin-flip "
           "statement — the T >= .10 bar decides, not p. block_sd_A: how far a k = 64 reading of "
           "the same cross-family predictor would scatter across 2k's four 64-draw blocks under the "
           "same latent (dial h; 2l measured .0070 at 13B). delta_sd: the null and at-declare SD of "
           "Delta = T(x_B thinned) - T(x_A^256) across simulated outcomes, and the paired-bootstrap SD "
           "of Delta on one null draw, from which min_detectable_delta follows by the stated normal "
           "approximation — the annotation C's own resolution claim, printed once and never re-run.")


def block_sd_A(strata, bits_1b, x_a256, n_pos, rungs, *, n_steps, n_sim=N_SIM_BLOCKS, seed=2) -> dict:
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
                      "per_block_mean_T": [float(np.mean(per_block[b])) if per_block[b] else None for b in blocks]}
    return {"n_sim": n_sim, "calibrated_rho": float(rho), "rungs": list(keep),
            "mean_block_sd_at_declare": res["at_declare"]["mean_sd"],
            "mean_block_sd_null": res["null"]["mean_sd"],
            "per_block_mean_T_at_declare": res["at_declare"]["per_block_mean_T"],
            "per_block_mean_T_null": res["null"]["per_block_mean_T"], "blocks": len(bk.SEEDS_2K)}


def delta_sd_2n(strata, bits_b, x_a64, x_a256, x_b, n_pos, rungs, *, n_steps, n_sim=N_SIM_DELTA,
                n_boot=N_BOOT_DELTA, seed=3) -> dict:
    """Design §4 (dial h, the Δ line): Δ = t_only(x_B thinned) − t_only(x_A256)
    on simulated outcomes — its SD across `n_sim` outcomes at the null
    (rho = 0) and under each test's own calibrated latent at D = .15 —
    and the paired bootstrap SD of Δ on the FIRST null outcome, from
    which `min_detectable_delta` follows by the stated normal
    approximation. Over the rungs non-degenerate for BOTH predictors."""
    dropped = set(an2i._degenerate_rungs(x_a256, strata, rungs)) | set(an2i._degenerate_rungs(x_b, strata, rungs))
    keep = tuple(r for r in rungs if r not in dropped)
    if not keep:
        return {"n_sim": 0, "delta_null_sd": None, "delta_sd_at_declare_A": None, "delta_sd_at_declare_B": None,
                "delta_boot_sd_null": None, "min_detectable_delta": None, "formula": DELTA_FORMULA_2N,
                "k_by_rung": {}, "rungs": [], "note": "every rung degenerate for one predictor; nothing simulated"}
    x_thin, k_by_rung = an.thinned_x_b_2n(bits_b, x_a64, keep)
    rho_a = pw.calibrate_rho(pw.DECLARE_AT, strata, x_a256, n_pos, keep, n_steps=n_steps)
    rho_b = pw.calibrate_rho(pw.DECLARE_AT, strata, x_b, n_pos, keep, n_steps=n_steps)

    def _out(cells):
        return {c["rung"]: {"y": [float(v) for v in c["y"]], "n_pos": int((np.asarray(c["y"]) > 0).sum())} for c in cells}

    def _delta(out):
        tb = an2j.t_only(x_thin, "olmo1b:thinned", out, strata, keep)["T"]
        ta = an2j.t_only(x_a256, "1b:k256", out, strata, keep)["T"]
        return None if tb is None or ta is None else tb - ta

    res, first_null = {}, None
    for label, rho_, x_lat in (("null", 0.0, x_a256), ("at_declare_A", rho_a, x_a256), ("at_declare_B", rho_b, x_b)):
        rng = np.random.default_rng(seed)
        ds = []
        for i in range(n_sim):
            out = _out(pw.simulate_cells_2i(rng, rho_, strata, x_lat, n_pos, keep, n_steps=n_steps))
            if label == "null" and i == 0:
                first_null = out
            d = _delta(out)
            if d is not None and np.isfinite(d):
                ds.append(d)
        res[label] = float(np.std(ds, ddof=1)) if len(ds) > 1 else None
    boot = an.paired_contrast_2n({"B_thinned": x_thin}, {"A256": x_a256}, first_null, strata, keep,
                                 n_boot=n_boot, seed=seed) if first_null else {"ci95": None}
    bsd = None
    if boot.get("ci95") is not None:
        bsd = (boot["ci95"][1] - boot["ci95"][0]) / (2 * 1.96)
    return {"n_sim": n_sim, "delta_null_sd": res["null"], "delta_sd_at_declare_A": res["at_declare_A"],
            "delta_sd_at_declare_B": res["at_declare_B"], "delta_boot_sd_null": bsd,
            "min_detectable_delta": (None if bsd is None else 2.63 * bsd), "formula": DELTA_FORMULA_2N,
            "calibrated_rho_A": float(rho_a), "calibrated_rho_B": float(rho_b),
            "k_by_rung": {r: int(k) for r, k in k_by_rung.items()}, "rungs": list(keep), "n_boot": boot.get("n_boot")}


def main(out_path=None, *, root_2n=EXP2N, root_2i=bi.EXP2I, root_2k=bk.EXP2K, tag_exists=None,
         blob_sha=None, blobs_bound=None, frozen_check=None) -> dict:
    bn.require_prereg_2n(tag_exists=tag_exists, blob_sha=blob_sha)
    bg.check_frozen_imports_2g()
    bi.check_frozen_2i()
    (frozen_check or bn.check_frozen_2n)()
    out_path = Path(out_path) if out_path is not None else bn.power_path(root_2n)
    if out_path.exists():
        raise RuntimeError(f"{out_path} exists — the power record is written ONCE")
    seals = require_predictor_seals_2n(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                                       root_2k=root_2k)
    rung_set = an._load_rung_set_2n(root_2n)
    r_primary = tuple(rung_set["R_PRIMARY"])
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])
    manifest = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    stage1 = an.load_endpoint_which_2n(root_2n, "stage1_final", battery, verify_fn,
                                       entry=bn.entry_which_comma(manifest, "stage1_final"))
    n_pos = {r: int(stage1[r]["correct"]) for r in r_primary}
    fp, pctx = an.load_predictors_2n(root_2i, root_2k, battery=battery, verify_fn=verify_fn,
                                     tag_exists=tag_exists, blobs_bound=blobs_bound)
    if fp:
        raise RuntimeError(f"refusing: the predictors do not re-derive cleanly: {fp[:5]}")
    cells = pctx["cells_2k"]["1b"]
    x256 = {r: cells[r]["counts"][bk.K_TOTAL] for r in r_primary}
    bits = {r: cells[r]["bits"] for r in r_primary}
    x_b = {r: pctx["x_b"][r] for r in r_primary}
    bits_b = {r: pctx["bits_b"][r] for r in r_primary}
    x_a64 = {r: cells[r]["counts"][64] for r in r_primary}
    n_steps = bn.n_trained_comma()
    rec = {"A": pw._one_test_power(strata, x256, n_pos, r_primary, n_steps=n_steps),
           "B": pw._one_test_power(strata, x_b, n_pos, r_primary, n_steps=n_steps),
           "block_sd_A": block_sd_A(strata, bits, x256, n_pos, r_primary, n_steps=n_steps, n_sim=N_SIM_BLOCKS),
           "delta_sd": delta_sd_2n(strata, bits_b, x_a64, x256, x_b, n_pos, r_primary, n_steps=n_steps),
           "predictor_sha256": seals["predictor_sha"], "r_primary": list(r_primary),
           "primary_is_the_nine": bool(rung_set["primary_is_the_nine"]),
           "calibration_note": an.CALIBRATION_SENTENCE_2N, "shape_note": pw.SHAPE_NOTE_2I, "note": NOTE_2N}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1))
    print("A:", rec["A"]["declared_status"], "-", rec["A"]["declaration"])
    print("B:", rec["B"]["declared_status"], "-", rec["B"]["declaration"])
    print("block SD (A, at D=.15):", rec["block_sd_A"]["mean_block_sd_at_declare"],
          "| null:", rec["block_sd_A"]["mean_block_sd_null"])
    print("delta SD (null):", rec["delta_sd"]["delta_null_sd"],
          "| boot SD (null):", rec["delta_sd"]["delta_boot_sd_null"],
          "| min detectable delta:", rec["delta_sd"]["min_detectable_delta"])
    return rec


if __name__ == "__main__":
    main()
