# experiments/exp4b/levels_4b.py
"""Experiment 4b's S6 (design `experiment-4b-design.md` §5, plan Task
4): the level descriptives with hidden-state 0 excluded from the site
family, each with an item-bootstrap CI95.

Exp 4's frozen level descriptives — S3 (`analyze_4.s3_scale_4`, the
Pythia size ladder), S8 (`analyze_4.s8_referents_4`, twins/ceiling/
within-family) and S5(a) (`analyze_4.s5_site_sensitivities_4`'s
`max_over_pairs`) — average alignment over the pinned site family
INCLUDING hidden-state 0. Hidden state 0 is the embedding of a constant
prompt-end token, so its k-NN sets are IDENTICAL in every model:
alignment exactly 1.0, always, by construction. On the site families
this program's models carry (`GATE0_MIN_FRACTION_4`'s own site counts
run 3-13), that one degenerate site is a 1/n_sites share of the mean —
non-trivial, and it dominates every rung's level toward 1.0 by exactly
that share regardless of what the OTHER sites read. `analyze_4`'s own
gate 0 already treats this site as unusable evidence
(`GATE0_EXCLUDED_SITES_4 = (0,)`); this module recomputes S3/S8/S5(a)
with the same exclusion, so the size axis, the twins, the references'
mutual ceiling, the within-family series and the Huh max-over-pairs
reading are read on the sites gate 0 itself trusts.

Every read here goes through `analyze_4`'s own frozen loaders
(`_load_one_unit_4` via `load_stage_tables_4`/`load_sweep_tables_4`'s
underlying call, `_load_global`) and `collect_4`'s frozen set-table
machinery (`overlap_table_4`, `_max_over_pairs`, `load_ref_tables_4`,
`_pairing_positions`, `non_pythia_refs_4`) — none of it is
reimplemented; this module supplies only the site-family FILTER
(`kept_positions_4b`, the `_gate0_kept_positions_4` array-position rule
generalised to a raw site list) and the levels/CI machinery built on
top of it.

The exclusion rule has two shapes, both drawn from ambiguity
resolution (1):

* Everywhere a FIXED depth-matched pairing is used (`per_item_level_4b`
  and everything built on it — `ladder_4b`, `twins_4b`, `ceiling_4b`,
  `within_family_4b`) the filter applies to the MODEL ("M") side's site
  axis only, post-hoc, on the already-computed overlap table — exactly
  `_gate0_kept_positions_4`'s convention. The reference side is never
  independently sliced: the pairing already routes each kept M
  position to whatever reference site sits at the matching relative
  depth (for site 0, that is almost always the reference's own site 0,
  the same degenerate embedding layer, so excluding M's position 0
  already removes the (0, 0)-shaped comparison in practice).
* `max_over_pairs_4b`/`max_pair_alignment_4b` scan the FULL cross
  product of M's sites against a reference's sites (no fixed pairing
  to route through), so the exclusion is applied independently to
  BOTH sides before the cross product is scanned.

Zero model contact; no torch. Every failure raised directly by this
module is prefixed "4b: "."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Design §3.2 / build constraint: the BLAS thread pool is sized when
# numpy is first imported — pinned before numpy (and before every
# `experiments.*` import that pulls numpy in transitively), exactly as
# `analyze_4.py`/`placebo_4b.py` do.
from experiments.exp4 import _threads_4  # noqa: E402,F401

import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402

# -------------------------------------------------------- the filter itself


def kept_positions_4b(sites: list, excluded=an.GATE0_EXCLUDED_SITES_4) -> list:
    """Array POSITIONS of `sites` (a model's own hidden-state LAYER
    index list, e.g. a unit's `record["sites"]`) whose layer is not in
    `excluded` — `analyze_4._gate0_kept_positions_4`'s rule ("position
    i of a row is layer `sites[i]`; the two coincide only for i = 0"),
    generalised to take a raw site list directly rather than a pair of
    twin/endpoint tables. `excluded=()` keeps every position."""
    bad = set(int(e) for e in excluded)
    return [i for i, s in enumerate(int(x) for x in sites) if s not in bad]


# ------------------------------------------------------------ per-item level


def per_item_level_4b(tables_m: dict, ref_tables: dict, pairing_by_ref: dict, *,
                      excluded=(0,)) -> dict:
    """`analyze_4._alignment_parts_4`'s pooled construction (mean over
    references and M's sites of overlap/k, via `collect_4.
    overlap_table_4` under the FIXED depth-matched `pairing_by_ref`),
    with M's site axis filtered to `kept_positions_4b` before the mean
    is taken. Returns `{rung: float64[n_items]}` for every rung present
    in `tables_m["sets"]`, plus `"_by_ref": {ref: {rung:
    float64[n_items]}}` (the same quantity for one reference alone —
    `_alignment_parts_4`'s `per_reference` half, S11's clause).

    Iterates over `sorted(tables_m["sets"])` rather than
    `battery_4.RUNGS` — a unit loaded via `analyze_4._load_one_unit_4`
    carries exactly `battery_4.RUNGS` (`_load_one_unit_4` enforces
    34-rung coverage before this function ever sees it), so production
    callers get the real battery; a fast test can build a table with
    just the rung(s) it needs.

    Unlike `_alignment_parts_4`, this does NOT cross-check a stored
    `overlap_<ref>` array — every real caller here reads the same
    committed bytes `analyze_4.per_item_alignment_4` already checked
    when Exp 4's own verdict was built; re-checking here would cost a
    second full overlap pass (`_alignment_parts_4`'s own docstring:
    "by far the most expensive thing the analyzer does") for no new
    information."""
    sites_m = [int(s) for s in (tables_m.get("record", {}).get("sites") or [])]
    if not sites_m:
        raise ValueError("4b: per_item_level_4b: tables_m carries no record[\"sites\"]")
    keep = kept_positions_4b(sites_m, excluded)
    if not keep:
        raise ValueError(f"4b: per_item_level_4b: excluded {list(excluded)!r} drops "
                         f"every site of {sites_m!r} — there would be nothing to average")
    sets_m = tables_m["sets"]
    rungs = sorted(sets_m.keys())
    pooled, by_ref = {}, {ref: {} for ref in pairing_by_ref}
    for rung in rungs:
        sm = np.asarray(sets_m[rung])
        per_ref = []
        for ref, pairing in pairing_by_ref.items():
            sq = ref_tables[ref][rung]
            ov = collect_4.overlap_table_4(sm, sq, pairing)          # [n_sites, n_items]
            frac = ov.astype(np.float64) / metric_4.K_4
            frac_kept = frac[keep]                                    # [n_keep, n_items]
            per_ref.append(frac_kept)
            by_ref[ref][rung] = frac_kept.mean(axis=0)                # [n_items]
        pooled[rung] = np.stack(per_ref, axis=0).mean(axis=(0, 1))    # [n_items]
    pooled["_by_ref"] = by_ref
    return pooled


def level_ci_4b(vec, *, n_boot=battery_4b.N_BOOT_LEVELS_4B, seed=0) -> dict:
    """Item-level percentile bootstrap of `vec`'s mean:
    `{"mean", "ci95": [lo, hi], "n_boot", "seed"}`. `n_boot` resamples
    of `vec`'s own item axis with replacement, the 2.5th/97.5th
    percentiles of the resample means."""
    vec = np.asarray(vec, dtype=np.float64)
    n = vec.shape[0]
    if n < 2:
        raise ValueError(f"4b: level_ci_4b: need at least 2 items, got {n}")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(int(n_boot), n))
    boots = vec[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"mean": float(vec.mean()), "ci95": [float(lo), float(hi)],
           "n_boot": int(n_boot), "seed": int(seed)}


# ----------------------------------------------------------- (a) the ladder


def _ladder_unit_pairing_4b(unit, ref_tables_raw, non_pythia):
    """A ladder/12b unit's `record["pairing"]` when non-empty (the
    real, committed pairing); re-derived via `collect_4.
    _pairing_positions` when empty (`ref_pythia_12b`, size "12b" on
    this axis, is written with `refs=()` — its own record carries no
    pairing against the non-Pythia references — `analyze_4.
    s3_scale_4`'s own fallback, read verbatim)."""
    pairing_by_ref = unit["record"]["pairing"]
    if pairing_by_ref:
        return pairing_by_ref
    sites_u, n_hidden_u = unit["record"]["sites"], unit["record"]["n_hidden"]
    return {ref: collect_4._pairing_positions(sites_u, n_hidden_u,
                                              ref_tables_raw[ref]["sites"],
                                              ref_tables_raw[ref]["n_hidden"])
           for ref in non_pythia}


def _ladder_global_4b(root4, units, ref_tables_raw, non_pythia, sizes, logp, excluded):
    """The global-bank half of `ladder_4b` (`analyze_4.s3_scale_4`'s
    own `global_reading`, re-derived with the site filter): degrades
    to `{"available": False, "note": ...}` — never a crash — when
    `global.npz` was not committed for one or more ladder keys
    (ambiguity resolution 2), exactly as `s3_scale_4` itself degrades."""
    try:
        refs_global = {ref: an._load_global(root4, ref) for ref in non_pythia}
        means, cis = {}, {}
        for size in sizes:
            unit = units[size]
            key = "ref_pythia_12b" if size == "12b" else f"ladder_pythia_{size}"
            g = an._load_global(root4, key)
            keep = kept_positions_4b(unit["record"]["sites"], excluded)
            pairing_by_ref = _ladder_unit_pairing_4b(unit, ref_tables_raw, non_pythia)
            per_ref_vecs = []
            for ref in non_pythia:
                ov = collect_4.overlap_table_4(g, refs_global[ref], pairing_by_ref[ref])
                frac = ov.astype(np.float64) / metric_4.K_4
                per_ref_vecs.append(frac[keep])                       # [n_keep, total]
            vec = np.mean(per_ref_vecs, axis=(0, 1))                  # [total]
            means[size] = float(vec.mean())
            cis[size] = level_ci_4b(vec)
        vals = np.array([means[s] for s in sizes])
        rho = float(spearmanr(vals, logp).statistic) if len(set(vals.tolist())) > 1 else None
        return {"a_by_size": means, "ci_by_size": cis, "rho_log_params": rho, "available": True}
    except (FileNotFoundError, OSError, zipfile.BadZipFile, ValueError):
        return {"available": False,
               "note": "global.npz not committed for one or more ladder keys"}


def ladder_4b(root4, *, excluded=(0,)) -> dict:
    """S6(a): the Pythia size ladder (`analyze_4.s3_scale_4`'s per-rung
    structure, re-derived with the site filter) — per rung, per size in
    `battery_4.LADDER_SIZES_4` (70m..12b, "12b" read off `ref_pythia_
    12b`): `a_by_size`, `ci_by_size` (`level_ci_4b` per size), Spearman
    of the per-size means with log parameters (`None` when the series
    is constant), the largest single-step share of the total rise; plus
    the global bank (`_ladder_global_4b`). `known_in_advance: True` on
    the whole block — design §2 discloses this reading's headline
    (34/34 rungs rising, median Spearman .89, mean level .198 at 70m ->
    .317 at 12b) as known to the designer before the freeze; §5 grades
    S6(a) on nothing."""
    non_pythia = collect_4.non_pythia_refs_4()
    ref_tables_raw = collect_4.load_ref_tables_4(root4, non_pythia)
    ref_tables = {ref: rt["sets"] for ref, rt in ref_tables_raw.items()}
    sizes = battery_4.LADDER_SIZES_4
    levels_by_size, units = {}, {}
    for size in sizes:
        key = "ref_pythia_12b" if size == "12b" else f"ladder_pythia_{size}"
        unit = an._load_one_unit_4(root4, key)
        units[size] = unit
        pairing_by_ref = _ladder_unit_pairing_4b(unit, ref_tables_raw, non_pythia)
        levels_by_size[size] = per_item_level_4b(unit, ref_tables, pairing_by_ref,
                                                 excluded=excluded)
    rungs = sorted(k for k in levels_by_size[sizes[0]] if k != "_by_ref")
    logp = np.array([np.log(battery_4.PYTHIA_PARAMS_4[s]) for s in sizes])
    per_rung = {}
    for r in rungs:
        vecs = {s: levels_by_size[s][r] for s in sizes}
        means = np.array([vecs[s].mean() for s in sizes])
        cis = {s: level_ci_4b(vecs[s]) for s in sizes}
        rho = float(spearmanr(means, logp).statistic) if len(set(means.tolist())) > 1 else None
        rise = float(means[-1] - means[0])
        share = float(np.max(np.diff(means)) / rise) if rise > 0 else None
        per_rung[r] = {"a_by_size": {s: float(means[i]) for i, s in enumerate(sizes)},
                       "ci_by_size": cis, "rho_log_params": rho, "max_single_step_share": share}
    global_reading = _ladder_global_4b(root4, units, ref_tables_raw, non_pythia, sizes,
                                       logp, excluded)
    return {"per_rung": per_rung, "sizes": list(sizes), "global": global_reading,
           "known_in_advance": True, "excluded": [int(e) for e in excluded],
           "source": "re-derived"}


# ------------------------------------------------------------- (b) twins


def twins_4b(root4, *, excluded=(0,)) -> dict:
    """S6(b): the untrained twins per trajectory per rung
    (`analyze_4.s8_referents_4`'s `twins` block, re-derived with the
    site filter), each with an item-bootstrap CI95."""
    out = {}
    for traj in battery_4.TRAJECTORIES_4:
        key = battery_4.INIT_KEY_4[traj]
        unit = an._load_one_unit_4(root4, key)
        refs = battery_4.REFS_FOR_4[traj]
        ref_tables_raw = collect_4.load_ref_tables_4(root4, refs)
        ref_tables = {ref: rt["sets"] for ref, rt in ref_tables_raw.items()}
        levels = per_item_level_4b(unit, ref_tables, unit["record"]["pairing"],
                                   excluded=excluded)
        rungs = sorted(k for k in levels if k != "_by_ref")
        out[traj] = {r: level_ci_4b(levels[r]) for r in rungs}
    return out


# ----------------------------------------------------------- (c) ceiling


def ceiling_4b(root4, *, excluded=(0,)) -> dict:
    """S6(c): the references' mutual alignment per pair per rung
    (`analyze_4.s8_referents_4`'s `ceiling` block read ATTESTED from
    `align.json`; this recomputes it from the committed set tables so
    the site filter has array positions to act on). A reference-stage
    key loads cleanly through `analyze_4._load_one_unit_4` — the SAME
    unit shape `twins_4b`/`ladder_4b` already load (`s3_scale_4`'s own
    "12b" ladder point IS `ref_pythia_12b` loaded this way) — so this
    is `twins_4b`'s structure with the reference itself standing in for
    the trained unit: `per_item_level_4b` is called once per reference
    `a` (playing the "M" role, filtered by ITS OWN kept positions — the
    general M-only rule this module uses everywhere except
    `max_over_pairs_4b`) against every OTHER reference as `ref_tables`,
    and the per-pair per-rung CIs are read straight off its `"_by_ref"`
    output — no second implementation of the overlap -> filter -> mean
    arithmetic. The depth-matched pairing from `a`'s sites to each
    other reference's is re-derived via `collect_4._pairing_positions`
    (reference units carry no pairing of their own — they are written
    with `refs=()`). Returns `{"pairs": {a: {b: {rung: {"mean",
    "ci95", ...}}}}}` for every ordered pair `a != b` in
    `battery_4.REFERENCES_4`."""
    units = {ref: an._load_one_unit_4(root4, ref) for ref in battery_4.REFERENCES_4}
    pairs = {}
    for a in battery_4.REFERENCES_4:
        others = [b for b in battery_4.REFERENCES_4 if b != a]
        sites_a = [int(s) for s in units[a]["record"]["sites"]]
        n_hidden_a = units[a]["record"]["n_hidden"]
        ref_tables = {b: units[b]["sets"] for b in others}
        pairing_by_ref = {
            b: collect_4._pairing_positions(sites_a, n_hidden_a,
                                            [int(s) for s in units[b]["record"]["sites"]],
                                            units[b]["record"]["n_hidden"])
            for b in others
        }
        levels = per_item_level_4b(units[a], ref_tables, pairing_by_ref, excluded=excluded)
        pairs[a] = {b: {r: level_ci_4b(vec) for r, vec in levels["_by_ref"][b].items()}
                   for b in others}
    return {"pairs": pairs, "source": "re-derived"}


# ------------------------------------------------------ (d) within-family


def within_family_4b(root4, *, excluded=(0,)) -> dict:
    """S6(d): Pythia 2.8b's trajectory against `ref_pythia_12b`
    (`analyze_4.s8_referents_4`'s `within_family` block, re-derived
    with the site filter) — point values at every grid step, an
    item-bootstrap CI95 only at the first and last step (design §5's
    "CI at t_1 and t_end only": a CI at every one of `GRID_4
    ["pythia_2.8b"]`'s ~21 points would cost 21 bootstraps per rung for
    a series this module's callers only ever read at its endpoints).

    Ambiguity resolution 3: `ref_pythia_12b` shares Pythia's family
    with `pythia_2.8b`, so `REFS_FOR_4["pythia_2.8b"]` (cross-family
    only) EXCLUDES it — a sweep unit's own `record["pairing"]` will
    not carry a `"ref_pythia_12b"` entry, and the depth pairing is
    re-derived via `collect_4._pairing_positions` instead (the branch
    a real committed tree always takes; the direct `.get(ref)` read is
    kept as a no-op fast path in case a future unit ever does carry
    it)."""
    traj, ref = "pythia_2.8b", "ref_pythia_12b"
    ref_table = collect_4.load_ref_tables_4(root4, (ref,))[ref]
    ref_sets = ref_table["sets"]
    ref_sites = [int(s) for s in ref_table["sites"]]
    ref_n_hidden = ref_table["n_hidden"]
    steps = list(battery_4.GRID_4[traj])
    rungs = sorted(battery_4.RUNGS)
    per_rung_series = {r: [] for r in rungs}
    edge_vecs = {r: {} for r in rungs}
    last = len(steps) - 1
    for i, s in enumerate(steps):
        unit = an._load_one_unit_4(root4, (traj, s))
        sites_m = [int(x) for x in unit["record"]["sites"]]
        n_hidden_m = unit["record"]["n_hidden"]
        keep = kept_positions_4b(sites_m, excluded)
        pairing = (unit["record"].get("pairing") or {}).get(ref)
        if pairing is None:
            pairing = collect_4._pairing_positions(sites_m, n_hidden_m, ref_sites, ref_n_hidden)
        is_edge = i == 0 or i == last
        for r in rungs:
            ov = collect_4.overlap_table_4(unit["sets"][r], ref_sets[r], pairing)
            frac = ov.astype(np.float64) / metric_4.K_4
            vec = frac[keep].mean(axis=0)
            per_rung_series[r].append(float(vec.mean()))
            if is_edge:
                edge_vecs[r][i] = vec
    per_rung = {}
    for r in rungs:
        per_rung[r] = {"steps": steps, "a": per_rung_series[r],
                       "ci_t1": level_ci_4b(edge_vecs[r][0]),
                       "ci_end": level_ci_4b(edge_vecs[r][last])}
    return {"traj": traj, "ref": ref, "per_rung": per_rung, "source": "re-derived"}


# --------------------------------------------------------- (e) max-over-pairs

MAX_PAIRS_EXCLUDED_NOTE_4B = (
    "the excluded layer is dropped from BOTH sides of the site cross product "
    "before it is scanned (ambiguity resolution 1) -- unlike the fixed "
    "depth-matched pairing this module uses everywhere else, there is no "
    "pairing argument here to route the exclusion through one side only")


def max_pair_alignment_4b(sets_m, sites_m, sets_q, sites_q, *, excluded=(0,)):
    """The Huh max-over-pairs reading (`collect_4._max_over_pairs`) with
    the excluded layer dropped from BOTH `sites_m` and `sites_q` before
    the full cross product is scanned. Returns `(best_mean, [layer_m,
    layer_q])`, `_max_over_pairs`'s own shape — the winning pair's
    hidden-state LAYER indices, not array positions."""
    keep_m = kept_positions_4b(sites_m, excluded)
    keep_q = kept_positions_4b(sites_q, excluded)
    if not keep_m or not keep_q:
        raise ValueError(f"4b: max_pair_alignment_4b: excluded {list(excluded)!r} drops "
                         f"every site on one side (m={sites_m!r}, q={sites_q!r})")
    sm = np.asarray(sets_m)[keep_m]
    sq = np.asarray(sets_q)[keep_q]
    sm_labels = [int(sites_m[i]) for i in keep_m]
    sq_labels = [int(sites_q[i]) for i in keep_q]
    return collect_4._max_over_pairs(sm, sm_labels, sq, sq_labels, metric_4.K_4)


def max_over_pairs_4b(root4, cells, *, excluded=(0,)) -> dict:
    """S6(e): the max-over-pairs alignment with the degenerate site
    excluded from both sides, per real cell — the S5(a) reading Exp 4
    could not produce (its own `series_max_pairs` reads an ATTESTED
    `knn_max_over_pairs_prompt_end` from `align.json`, computed over
    the FULL site family; there is no attested reading with site 0
    already dropped, so this recomputes it from the committed set
    tables via `max_pair_alignment_4b`).

    For each cell's trajectory: the flat-rung pool's max-over-pairs
    series (mean over that trajectory's cross-family references,
    `battery_4.REFS_FOR_4[traj]`) at every grid step builds the trend
    (`analyze_4.trend_4`, called unmodified); each cell's own rung gets
    the same series, reduced to excess (`analyze_4.excess_4`) and phi
    (`analyze_4.phi_4`) at its own `t_clear_index`. `cells`: an
    iterable of `{"traj", "rung", "t_clear_index"}` (`battery_4b.
    cells_from_verdict_4b`'s shape, or hand-built the same way when no
    committed verdict exists — a `full_shape` world never has one).

    Returns `{"cells": [{"traj", "rung", "phi", "x_end", "series"}],
    "pooled_phi": mean phi over cells with a non-None phi (`None` if
    every cell is `None`), "n_cells", "n_phi", "excluded_pair_note"}`."""
    floors = bg.load_floors()
    battery = bt.load_battery()
    by_traj: dict = {}
    for c in cells:
        by_traj.setdefault(c["traj"], []).append(c)
    per_cell = []
    for traj, traj_cells in by_traj.items():
        outcome = battery_4.load_outcome_4(traj, battery=battery)
        rs = battery_4.rung_sets_4(outcome, floors)
        flat = rs["flat"]
        if not flat:
            raise ValueError(f"4b: max_over_pairs_4b: {traj} has no flat rungs")
        steps = list(battery_4.GRID_4[traj])
        refs = battery_4.REFS_FOR_4[traj]
        ref_tables_raw = collect_4.load_ref_tables_4(root4, refs)
        needed = sorted(set(flat) | {c["rung"] for c in traj_cells})
        series = {r: [] for r in needed}
        for s in steps:
            unit = an._load_one_unit_4(root4, (traj, s))
            sites_m = [int(x) for x in unit["record"]["sites"]]
            for r in needed:
                sm = unit["sets"][r]
                per_ref = []
                for ref in refs:
                    rt = ref_tables_raw[ref]
                    sites_q = [int(x) for x in rt["sites"]]
                    best, _ = max_pair_alignment_4b(sm, sites_m, rt["sets"][r], sites_q,
                                                    excluded=excluded)
                    per_ref.append(best)
                series[r].append(float(np.mean(per_ref)))
        trend = an.trend_4(series, flat, steps)
        for c in traj_cells:
            r = c["rung"]
            x = an.excess_4({r: series[r]}, trend, steps)[r]
            phi = an.phi_4(x, c["t_clear_index"])
            per_cell.append({"traj": traj, "rung": r, "phi": phi, "x_end": x[-1], "series": x})
    phis = [c["phi"] for c in per_cell if c["phi"] is not None]
    pooled_phi = float(np.mean(phis)) if phis else None
    return {"cells": per_cell, "pooled_phi": pooled_phi, "n_cells": len(per_cell),
           "n_phi": len(phis), "excluded_pair_note": MAX_PAIRS_EXCLUDED_NOTE_4B,
           "source": "re-derived"}
