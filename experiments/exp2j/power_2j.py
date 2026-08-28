# experiments/exp2j/power_2j.py
"""ONE power record for the primary (design §7, dial f): 2i's
machinery on the REAL x_B, the REAL composite strata (base × the four
functionals' buckets, exactly as the analyzer builds them), n_pos
bounded below by 2i's committed stage1_final endpoint counts, y
simulated from a latent mixing rank(x_B) at calibrated strength, every
cell through `analyze_2i.fires_2i`. Written once, before the tag;
refuses if the file exists. Computed from known inputs — a statement
about the instrument's resolution, not foresight."""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXP2J = Path(__file__).resolve().parent
if str(EXP2J.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2J.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i import power_2i as pw  # noqa: E402
from experiments.exp2j import functionals_2j as fn  # noqa: E402

NOTE_2J = ("Computed at the build from known inputs (x_B, the item files, 2i's endpoint "
           "counts): a claim about the primary's RESOLUTION on its composite strata, not "
           "about what will be found. Bar: P(fires | D = .15) >= .75 -> POWERED, else "
           "DECLARED UNDERPOWERED IN ADVANCE, which governs how ABSORBED reads (design §6).")


def main(out_path=None, *, root_2i=bi.EXP2I, root_2j=EXP2J) -> dict:
    bg.check_frozen_imports_2g()
    bi.check_frozen_2i()
    out_path = Path(out_path) if out_path is not None else Path(root_2j) / "results" / "power_2j.json"
    if out_path.exists():
        raise RuntimeError(f"{out_path} exists — the power record is written ONCE")
    rung_set = an2i._load_rung_set(root_2i)
    r_cap = tuple(rung_set["R_CAP"])
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
    x_b = bi.sampler_counts_olmo(r_cap, root=root_2i, battery=battery, verify_fn=verify_fn)
    tables = {r: fn.functional_table(battery[r], fn.draw_rows_2i(root_2i, r)) for r in r_cap}
    comp, report = fn.composite_strata(strata, tables, r_cap)
    rec = {"primary": pw._one_test_power(comp, x_b, n_pos, r_cap, n_steps=n_steps),
           "composite_report": report,
           "n_composite_strata": {r: len(set(comp[r]["strata"])) for r in r_cap},
           "base_strata_reference_2i_B": {"null_sd_T": 0.0111, "min_detectable_T": 0.02569},
           "shape_note": pw.SHAPE_NOTE_2I, "note": NOTE_2J}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1))
    print("primary:", rec["primary"]["declared_status"], "-", rec["primary"]["declaration"])
    return rec


if __name__ == "__main__":
    main()
