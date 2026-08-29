# experiments/exp2k/power_2k.py
"""ONE power record for the primary (design §7): 2i's machinery on the
REAL sealed x_A^(256) (re-derived from the raw draws, cross-checked
against the seal), 2g's base strata, n_pos bounded below by 2i's
committed stage1_final endpoint counts, y from a latent mixing
rank(x) at calibrated strength, every cell through `fires_2i`.
Written once, after the seal and before the seal tag; refuses if the
file exists or the seal is absent. Carries the seal's sha (2j F-2's
lineage: a power record is a claim about ONE predictor) and 2i's
committed k = 64 reference numbers, read from 2i's power file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXP2K = Path(__file__).resolve().parent
if str(EXP2K.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2K.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i import power_2i as pw  # noqa: E402
from experiments.exp2k import analyze_2k as an  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402

NOTE_2K = ("Computed at the sealed stage from the REAL x_A^(256) and known inputs: a claim about "
           "the primary's RESOLUTION on 2g's strata, not about what will be found. Bar: "
           "P(fires | D = .15) >= .75 -> POWERED, else DECLARED UNDERPOWERED IN ADVANCE, which "
           "governs how NOT-DENSITY reads (design §6); P(fires | D = .10) is the coin-flip "
           "statement — the T >= .10 bar decides, not p.")


def main(out_path=None, *, root_2i=bi.EXP2I, root_2k=EXP2K, tag_exists=None, blob_sha=None,
         frozen_check=None) -> dict:
    # `frozen_check`: test-only injection (see seal_2k); the campaign never passes it
    bk.require_prereg_2k(tag_exists=tag_exists, blob_sha=blob_sha)
    bg.check_frozen_imports_2g()
    bi.check_frozen_2i()
    (frozen_check or bk.check_frozen_2k)()
    out_path = Path(out_path) if out_path is not None else bk.power_path(root_2k)
    if out_path.exists():
        raise RuntimeError(f"{out_path} exists — the power record is written ONCE")
    seal_p = bk.seal_path(root_2k)
    if not seal_p.is_file():
        raise RuntimeError(f"refusing: {seal_p} missing — run seal_2k first")
    seal = json.loads(seal_p.read_text())
    rung_set = an2i._load_rung_set(root_2i)
    r_cap = tuple(sorted(rung_set["R_CAP"]))
    predictor_rec = an2i._load_predictor_seal_content(root_2i)
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])
    manifest = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    n_steps = bi.n_trained_7b()
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    stage1 = an2i.load_endpoint_which(root_2i, "stage1_final", battery, verify_fn,
                                      entry=bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B),
                                      predictor_sha=predictor_rec["sha256"])
    n_pos = {r: int(stage1[r]["correct"]) for r in r_cap}
    failures, cells = an.load_tier_2k(root_2k, "1b", battery=battery, verify_fn=verify_fn, rungs=r_cap)
    if failures:
        raise RuntimeError(f"refusing: the 1b tier does not re-derive cleanly: {failures[:5]}")
    x256 = {r: cells[r]["counts"][bk.K_TOTAL] for r in r_cap}
    if any(x256[r] != seal["counts"]["1b"][r] for r in r_cap):
        raise RuntimeError("refusing: the seal's 1b counts differ from the re-derivation")
    ref = json.loads(bi.power_path(bi.EXP2I).read_text())["A"]   # the REAL committed 2i record, never a world's
    rec = {"primary": pw._one_test_power(strata, x256, n_pos, r_cap, n_steps=n_steps),
           "predictor_sha256": seal["sha256"],
           "reference_2i_A_k64": {"null_sd_T": ref["null"]["null_sd_T"],
                                  "p_fires_at_D_0.10": ref["targets"]["0.1"]["p_fires"],
                                  "p_fires_at_D_0.15": ref["targets"]["0.15"]["p_fires"]},
           "shape_note": pw.SHAPE_NOTE_2I, "note": NOTE_2K}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1))
    print("primary:", rec["primary"]["declared_status"], "-", rec["primary"]["declaration"])
    return rec


if __name__ == "__main__":
    main()
