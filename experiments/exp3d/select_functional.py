"""Build obligation 1 (design §5.1, Open item 1): compute the four
candidate scores on the committed fired sets, take the winner by the
frozen formula, and commit the record — the winner's 500 per-item
values, their midranks, the tie structure, and the frozen decile
bucket — as `functional_selection_3d.json`.

Provenance, disclosed: the fired sets are the 13 committed fires
(§4's address pin, re-derivable from raw bytes); selection is
IN-SAMPLE on them, which is motivation, not evidence — confirmatory
inference sees only new draws (§5.1). No builder discretion remains
in the winner: the formula, the tie-breaks, and the inputs are all
frozen in functional_3d.select_winner and analyze_3d's pins.

Re-run at the freeze; the written file must be byte-identical
(compute_power_3c's convention). analyze_3d.load_selection recomputes
everything in this record from the item file at every analysis run
and refuses disagreement.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXP3D = Path(__file__).resolve().parent
if str(EXP3D.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3D.parent.parent))

from experiments.exp3d import functional_3d as fl  # noqa: E402
from experiments.exp3d.analyze_3d import (  # noqa: E402
    COMMITTED_FIRES_PIN, ITEMS_SHA_PIN, SELECTION_PATH,
    check_frozen_imports_3d, committed_fired_sets, load_item_file,
)


def build() -> dict:
    check_frozen_imports_3d()
    items = load_item_file("reverse_string")
    answers = items["answers"]
    fired = committed_fired_sets()
    sel = fl.select_winner(answers, fired["1b"], fired["410m"])
    name, fn = fl.CANDIDATES[sel["winner_index"]]
    values = fl.candidate_values(fn, answers)
    strata = fl.strata_of(answers)
    mids = fl.stratified_midranks(values, strata)
    return {
        "formula": ("mean over cells of the stratified AUC "
                    "Σ_s |F_s||U_s|·AUC_s / Σ_s |F_s||U_s| on the "
                    "committed fired sets; ties break by the 1b AUC, "
                    "then doc order C1 < C2 < C3 < C4 (§5.1, frozen "
                    "at design)"),
        "in_sample_note": ("selection is in-sample on the 13 committed "
                           "fires, DISCLOSED (§5.1): motivation, not "
                           "evidence; confirmatory inference sees only "
                           "new draws"),
        "items_sha256": ITEMS_SHA_PIN["reverse_string"],
        "committed_fired_sets": fired,
        "committed_fire_addresses": {
            s: list(COMMITTED_FIRES_PIN[s]) for s in ("410m", "1b")},
        "selection_table": sel["table"],
        "winner": sel["winner"],
        "winner_values": values,
        "winner_midranks_by_item": {str(i): mids[i]
                                    for i in sorted(mids)},
        "tie_structure": fl.tie_structure(values, strata),
        "decile_bucket": fl.decile_bucket(values, strata),
        "fired_item_answers": {
            s: {str(i): answers[i] for i in fired[s]}
            for s in ("410m", "1b")},
    }


if __name__ == "__main__":
    rec = build()
    SELECTION_PATH.write_text(json.dumps(rec, indent=1, sort_keys=True)
                              + "\n")
    print(f"winner: {rec['winner']}")
    for row in rec["selection_table"]:
        print(f"  {row['candidate']}: mean {row['mean_auc']:.4f} "
              f"(1b {row['auc_1b']:.4f}, 410m {row['auc_410m']:.4f})")
    ties = rec["tie_structure"]
    for L in sorted(ties):
        t = ties[L]
        print(f"  stratum {L}: {t['n_items']} items, "
              f"{t['n_distinct_values']} distinct values")
    print(f"bucket: {len(rec['decile_bucket'])} items")
    print(f"written: {SELECTION_PATH}")
