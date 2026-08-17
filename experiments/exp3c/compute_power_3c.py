"""Exact §7 tables from the frozen analysis (design §7, doc Open item
5) — committed as `power_3c.json` and re-run byte-identically at the
freeze.

There is no significance test anywhere in 3c (no mass arm, no trend
test — §7's own power numbers forbid one), so the whole table is
detection arithmetic: P(at least one fire in n draws | true per-draw
rate p) = 1 − (1−p)^n, the CP zero bounds read from the other side
(asserted equal to `cp_upper(0, n)` — the same closed form, exp3's
cross-check), the per-stratum grids under geometric length scaling
from the observed length-4 anchor, and the 26^-L luck floors.

The doc's §7/§8 quotes are cross-checked here and recorded with their
exact values; any discrepancy is ledgered, not silently absorbed
(exp3's convention). Three quotes are EXPECTED to disagree — the
build session's recon found them (PROGRESS.md readings 1–2, extended
by the LONE-DRAW probability below):

- "26^-4 ≈ 1.5e-6": 26^-4 = 2.19e-6.
- "a factor of ~13 on the point estimate": the observed length-4
  stratum rate over the true luck floor is ~9.2×.
- "LONE-DRAW at ~1-in-3 even if the true rate is 1e-6": P(zero new
  fires at the fired cell | p = 1e-6, n = 384,000) = e^(−0.384) =
  .68 — TWO in three. The quoted 1-in-3 is the detection
  probability (.32) mis-assigned to its own complement. LONE-DRAW
  reaches ~1-in-3 only if the true rate is ≈ 2.9e-6.

The strata item counts are read from exp3's committed sampling
records (the referent tree), never assumed.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments.exp3 import analyze_3 as a3
from experiments.exp3c.analyze_3c import (
    FIRED_CELL, K_NEW, K_POOLED, REVERSAL_RUNGS, SCORED_CELLS,
    check_frozen_imports, luck_floor, strata_of,
)

EXP3C = Path(__file__).resolve().parent
OUT = EXP3C / "power_3c.json"

N_ITEMS = 500
N_NEW_CELL = N_ITEMS * K_NEW          # 384,000 new draws per cell
N_POOLED_CELL = N_ITEMS * K_POOLED    # 512,000 pooled draws per cell
N_EXP3_CELL = N_POOLED_CELL - N_NEW_CELL   # 128,000 committed

# §7's rate grid: the observed exp3 point rate, then the tail
RATES = (1.0 / N_EXP3_CELL, 2e-6, 1e-6)

# the observed length-4 stratum rate at the fired cell: exp3's one
# fire over the stratum's committed draws (194 items × 256)
LEN4_ITEMS = 194


def detection(p: float, n: int) -> float:
    return float(1.0 - (1.0 - p) ** n)


def committed_strata() -> dict:
    """Answer-length strata counts from exp3's committed sampling
    records (410m_trained tree side; the shape check pins all four
    cells to identical answers, so one record per rung suffices)."""
    out = {}
    for rung in REVERSAL_RUNGS:
        p = (a3.EXP3 / "results" / "sampling" / "410m_trained"
             / f"{rung}.json")
        rec = json.loads(p.read_text())
        by_len = strata_of([str(x) for x in rec["answers"]])
        out[rung] = {L: len(idx) for L, idx in sorted(by_len.items())}
        if sum(out[rung].values()) != rec["n_items"]:
            raise ValueError(
                f"strata of {rung} cover {sum(out[rung].values())} items "
                f"against n_items {rec['n_items']}")
    return out


def build() -> dict:
    check_frozen_imports()
    strata_counts = committed_strata()
    if strata_counts != {"rev_string7": {7: 500},
                         "reverse_string": {4: 194, 5: 155, 6: 151}}:
        raise ValueError(
            f"committed strata {strata_counts} are not the design's "
            f"(§1: lengths 4-6 at 194/155/151 and 7 at 500)")

    anchor_len4 = 1.0 / (LEN4_ITEMS * a3.K_TOTAL["rev_string7"])  # 1/49,664

    # CP zero bounds, closed form asserted equal to cp_upper (exp3's
    # two-sides-of-one-bound check)
    bounds = {}
    for name, n in (("new_cell", N_NEW_CELL),
                    ("pooled_cell", N_POOLED_CELL),
                    ("exp3_cell", N_EXP3_CELL)):
        closed = 1.0 - 0.05 ** (1.0 / n)
        via_cp = a3.cp_upper(0, n)
        if abs(closed - via_cp) > 1e-12:
            raise AssertionError(
                f"detectable-rate closed form {closed} disagrees with "
                f"cp_upper(0, {n}) = {via_cp} — the two sides of the "
                f"same bound must be the same number")
        bounds[name] = closed
    resolution_gain = bounds["exp3_cell"] / bounds["pooled_cell"]

    sampling = {
        "n_new_per_cell": N_NEW_CELL,
        "n_pooled_per_cell": N_POOLED_CELL,
        "n_exp3_per_cell": N_EXP3_CELL,
        "detection_new_by_rate": {f"{p:.6e}": detection(p, N_NEW_CELL)
                                  for p in RATES},
        "p_lone_draw_at_fired_cell_by_rate": {
            f"{p:.6e}": 1.0 - detection(p, N_NEW_CELL) for p in RATES},
        "rate_where_lone_draw_is_one_in_three":
            -math.log(1.0 / 3.0) / N_NEW_CELL,
        "zero_bounds_cp95": bounds,
        "pooled_resolution_gain_over_exp3": resolution_gain,
        "lone_draw_pooled_point_rate": 1.0 / N_POOLED_CELL,
    }

    # per-stratum detection under geometric scaling from the length-4
    # anchor (§1's mechanism, tested only at the resolution the budget
    # buys; §7: why no trend test)
    strata = {}
    for rung, counts in strata_counts.items():
        cell = {}
        for L, n_items in counts.items():
            p_geo = anchor_len4 / (26.0 ** (L - 4))
            n_new = n_items * K_NEW
            n_pool = n_items * K_POOLED
            cell[str(L)] = {
                "n_items": n_items,
                "n_new": n_new, "n_pooled": n_pool,
                "geometric_rate_from_len4_anchor": p_geo,
                "detection_new_at_geometric_rate": detection(p_geo, n_new),
                "detection_pooled_at_geometric_rate":
                    detection(p_geo, n_pool),
                "luck_floor": luck_floor(L),
            }
        strata[rung] = cell
    len4 = strata["reverse_string"]["4"]

    quotes = {
        "detection_.95_at_point_rate_7.8e-6": {
            "quoted": 0.95,
            "computed": detection(RATES[0], N_NEW_CELL),
            "agrees": abs(detection(RATES[0], N_NEW_CELL) - 0.95) < 0.02},
        "detection_.53_at_2e-6": {
            "quoted": 0.53, "computed": detection(2e-6, N_NEW_CELL),
            "agrees": abs(detection(2e-6, N_NEW_CELL) - 0.53) < 0.02},
        "detection_.32_at_1e-6": {
            "quoted": 0.32, "computed": detection(1e-6, N_NEW_CELL),
            "agrees": abs(detection(1e-6, N_NEW_CELL) - 0.32) < 0.02},
        "len4_stratum_n_new_148992": {
            "quoted": 148992, "computed": len4["n_new"],
            "agrees": len4["n_new"] == 148992},
        "len4_stratum_observed_rate_2.01e-5": {
            "quoted": 2.01e-5, "computed": anchor_len4,
            "agrees": abs(anchor_len4 - 2.01e-5) < 1e-7},
        "detection_.95_at_len4_observed": {
            "quoted": 0.95,
            "computed": detection(anchor_len4, len4["n_new"]),
            "agrees": abs(detection(anchor_len4, len4["n_new"]) - 0.95)
            < 0.02},
        "pooled_zero_bound_5.85e-6": {
            "quoted": 5.85e-6, "computed": bounds["pooled_cell"],
            "agrees": abs(bounds["pooled_cell"] - 5.85e-6) < 1e-8},
        "exp3_zero_bound_2.34e-5": {
            "quoted": 2.34e-5, "computed": bounds["exp3_cell"],
            "agrees": abs(bounds["exp3_cell"] - 2.34e-5) < 1e-7},
        "resolution_gain_4x": {
            "quoted": 4.0, "computed": resolution_gain,
            "agrees": abs(resolution_gain - 4.0) < 0.01},
        "lone_draw_pooled_point_1.95e-6": {
            "quoted": 1.95e-6, "computed": 1.0 / N_POOLED_CELL,
            "agrees": abs(1.0 / N_POOLED_CELL - 1.95e-6) < 1e-8},
        "len5_geometric_rate_7.7e-7": {
            "quoted": 7.7e-7,
            "computed": strata["reverse_string"]["5"]
            ["geometric_rate_from_len4_anchor"],
            "agrees": abs(strata["reverse_string"]["5"]
                          ["geometric_rate_from_len4_anchor"] - 7.7e-7)
            < 5e-8},
        "len5_stratum_detection_.11": {
            "quoted": 0.11,
            "computed": strata["reverse_string"]["5"]
            ["detection_pooled_at_geometric_rate"],
            "agrees": abs(strata["reverse_string"]["5"]
                          ["detection_pooled_at_geometric_rate"] - 0.11)
            < 0.02},
        # ---- the three EXPECTED disagreements (module docstring;
        # PROGRESS.md reading 2 + the LONE-DRAW complement slip) ----
        "luck_floor_26^-4_quoted_1.5e-6": {
            "quoted": 1.5e-6, "computed": luck_floor(4),
            "agrees": abs(luck_floor(4) - 1.5e-6) < 1e-7,
            "note": "26^-4 = 2.19e-6; the doc's ≈1.5e-6 is an "
                    "arithmetic slip (PROGRESS.md reading 2)"},
        "luck_gap_factor_quoted_13x": {
            "quoted": 13.0, "computed": anchor_len4 / luck_floor(4),
            "agrees": abs(anchor_len4 / luck_floor(4) - 13.0) < 1.0,
            "note": "the observed len-4 rate over the true luck floor "
                    "is ~9.2x; ~13x followed from the 1.5e-6 slip"},
        "lone_draw_one_in_three_at_1e-6": {
            "quoted": 1.0 / 3.0,
            "computed": 1.0 - detection(1e-6, N_NEW_CELL),
            "agrees": abs((1.0 - detection(1e-6, N_NEW_CELL))
                          - 1.0 / 3.0) < 0.02,
            "note": "P(zero new fires | 1e-6) = .68 — two in three; "
                    "the quoted 1-in-3 is the detection probability "
                    ".32 mis-assigned to its complement. LONE-DRAW is "
                    "1-in-3 only at a true rate ≈ 2.9e-6"},
    }
    return {"sampling": sampling, "strata": strata,
            "luck_floors": {str(L): luck_floor(L) for L in (4, 5, 6, 7)},
            "doc_quotes_check": quotes}


if __name__ == "__main__":
    tables = build()
    OUT.write_text(json.dumps(tables, indent=1, sort_keys=True) + "\n")
    s = tables["sampling"]
    print(f"detection at exp3 point rate (n={s['n_new_per_cell']}): "
          f"{s['detection_new_by_rate'][f'{RATES[0]:.6e}']:.4f}")
    print(f"pooled zero bound: {s['zero_bounds_cp95']['pooled_cell']:.3e}"
          f" ({s['pooled_resolution_gain_over_exp3']:.2f}x exp3's "
          f"{s['zero_bounds_cp95']['exp3_cell']:.3e})")
    print(f"luck floors: " + ", ".join(
        f"26^-{L}={v:.2e}" for L, v in tables["luck_floors"].items()))
    q = tables["doc_quotes_check"]
    bad = [k for k, v in q.items() if not v["agrees"]]
    expected_bad = {"luck_floor_26^-4_quoted_1.5e-6",
                    "luck_gap_factor_quoted_13x",
                    "lone_draw_one_in_three_at_1e-6"}
    print("doc quotes: "
          + ("ALL AGREE" if not bad else f"DISAGREE (ledgered): {bad}"))
    if set(bad) != expected_bad:
        print(f"UNEXPECTED quote-check state — expected exactly "
              f"{sorted(expected_bad)} to disagree; ledger before "
              f"proceeding")
    print(f"written: {OUT}")
