# experiments/exp4b/tests/test_levels_4b.py
"""Tests for `levels_4b.py` (Task 4, design `experiment-4b-design.md`
§5 S6): the level descriptives with hidden-state 0 excluded from the
site family, each with an item-bootstrap CI95.

Step 1(a)-(c)/(e) are FAST — pure computation on `fakes_4b.
planted_tables`'s synthetic set tables, no committed bytes, no model
contact. Step 1(d) is SLOW: it needs `ladder_4b` to run against a real
committed-shaped tree, built via `experiments/exp4/tests/full_shape.
build_world(..., stage="full")` — a `stage="full"` build sweeps a real
92-point grid (~11-13 minutes per `experiments/exp4/PROGRESS.md` and
this build's Task 3 report) — so ONE module-scoped world is shared by
every slow test in this file (`test_power_ext_4b.py`'s own pattern):
`ladder_4b` (the brief's own (d)), plus `twins_4b`/`ceiling_4b`/
`within_family_4b` for completeness against the brief's full
Interfaces block, none of which the brief's Step 1 list names
explicitly. `max_over_pairs_4b` is exercised FAST instead (see its own
test's module-level comment below) — its full cross product is
expensive enough at real site/grid counts that a world does not make
it cheap; the wiring is verified with small monkeypatched set tables."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4.tests import full_shape as fs  # noqa: E402
from experiments.exp4b import levels_4b  # noqa: E402
from experiments.exp4b.tests import fakes_4b  # noqa: E402

# --------------------------------------------------------- kept_positions_4b


def test_kept_positions_4b_drops_position_whose_label_is_excluded():
    assert levels_4b.kept_positions_4b([0, 3, 7, 12]) == [1, 2, 3]


def test_kept_positions_4b_keeps_everything_when_excluded_is_empty():
    assert levels_4b.kept_positions_4b([0, 3, 7, 12], excluded=()) == [0, 1, 2, 3]


def test_kept_positions_4b_default_is_gate0_excluded_sites_4():
    # position 0 is excluded whenever its LABEL is 0, regardless of
    # where in the list it sits.
    assert levels_4b.kept_positions_4b([5, 0, 9]) == [0, 2]
    assert levels_4b.kept_positions_4b([5, 0, 9]) == \
        levels_4b.kept_positions_4b([5, 0, 9], excluded=an.GATE0_EXCLUDED_SITES_4)


# --------------------------------------------------------- per_item_level_4b


def _one_rung_tables(n_sites, v, *, n_items=64, seed=0, rung="rung0", ref="refA"):
    sets_m, sets_q, sites_m, sites_q = fakes_4b.planted_tables(
        n_sites, n_items=n_items, v=v, seed=seed)
    tables_m = {"sets": {rung: sets_m}, "record": {"sites": sites_m}}
    ref_tables = {ref: {rung: sets_q}}
    pairing_by_ref = {ref: list(range(n_sites))}
    return tables_m, ref_tables, pairing_by_ref, rung, ref


def test_per_item_level_4b_with_site0_excluded_equals_the_planted_value():
    n_sites, v = 5, 0.4
    tables_m, ref_tables, pairing_by_ref, rung, ref = _one_rung_tables(n_sites, v)
    out = levels_4b.per_item_level_4b(tables_m, ref_tables, pairing_by_ref, excluded=(0,))
    np.testing.assert_allclose(out[rung], v)
    np.testing.assert_allclose(out["_by_ref"][ref][rung], v)


def test_per_item_level_4b_with_site0_included_equals_the_1_over_n_share():
    n_sites, v = 5, 0.4
    tables_m, ref_tables, pairing_by_ref, rung, ref = _one_rung_tables(n_sites, v)
    out = levels_4b.per_item_level_4b(tables_m, ref_tables, pairing_by_ref, excluded=())
    expected = (1.0 + (n_sites - 1) * v) / n_sites
    np.testing.assert_allclose(out[rung], expected)


def test_per_item_level_4b_refuses_when_excluded_drops_every_site():
    n_sites, v = 3, 0.5
    tables_m, ref_tables, pairing_by_ref, rung, ref = _one_rung_tables(n_sites, v)
    with pytest.raises(ValueError, match="4b:"):
        levels_4b.per_item_level_4b(tables_m, ref_tables, pairing_by_ref, excluded=(0, 1, 2))


# -------------------------------------------------------------- level_ci_4b


def test_level_ci_4b_is_deterministic():
    rng = np.random.default_rng(1)
    vec = rng.normal(0.5, 0.05, size=200)
    out1 = levels_4b.level_ci_4b(vec, n_boot=500, seed=0)
    out2 = levels_4b.level_ci_4b(vec, n_boot=500, seed=0)
    assert out1 == out2


def test_level_ci_4b_ci_contains_the_mean():
    rng = np.random.default_rng(2)
    vec = rng.normal(0.3, 0.08, size=300)
    out = levels_4b.level_ci_4b(vec, n_boot=1000, seed=7)
    assert out["ci95"][0] <= out["mean"] <= out["ci95"][1]
    assert out["mean"] == pytest.approx(float(vec.mean()))


def test_level_ci_4b_different_seed_gives_different_ci():
    rng = np.random.default_rng(3)
    vec = rng.normal(0.5, 0.1, size=100)
    out_a = levels_4b.level_ci_4b(vec, n_boot=200, seed=0)
    out_b = levels_4b.level_ci_4b(vec, n_boot=200, seed=1)
    assert out_a["mean"] == out_b["mean"]
    assert out_a["ci95"] != out_b["ci95"]


def test_level_ci_4b_uses_exactly_the_2_5_97_5_percentiles(monkeypatch):
    """Mutation harness finding (Task 6): widening the percentile pair
    to [5.0, 95.0] narrows the CI but does not put it OUTSIDE the mean
    (`test_level_ci_4b_ci_contains_the_mean` still holds either way) and
    does not change determinism/seed-sensitivity -- none of the
    existing tests pin the LITERAL percentile values. Spies on
    `np.percentile` (imported into `levels_4b` as `np`, called
    unqualified inside the module) and asserts the exact `[2.5, 97.5]`
    pair was requested."""
    calls = []
    real_percentile = levels_4b.np.percentile

    def spy(a, q, *a2, **kw):
        calls.append(list(q) if hasattr(q, "__iter__") else q)
        return real_percentile(a, q, *a2, **kw)

    monkeypatch.setattr(levels_4b.np, "percentile", spy)
    rng = np.random.default_rng(5)
    levels_4b.level_ci_4b(rng.normal(0.4, 0.05, size=50), n_boot=100, seed=0)
    assert [2.5, 97.5] in calls, calls


# ------------------------------------------------------- max_pair_alignment_4b


def test_max_pair_alignment_4b_unfiltered_best_pair_is_the_degenerate_00():
    n_sites, v = 4, 0.3
    sets_m, sets_q, sites_m, sites_q = fakes_4b.planted_tables(n_sites, n_items=48, v=v, seed=2)
    best, pair = levels_4b.max_pair_alignment_4b(sets_m, sites_m, sets_q, sites_q, excluded=())
    assert best == pytest.approx(1.0)
    assert pair == [0, 0]


def test_max_pair_alignment_4b_excludes_site0_returns_v():
    n_sites, v = 4, 0.3
    sets_m, sets_q, sites_m, sites_q = fakes_4b.planted_tables(n_sites, n_items=48, v=v, seed=2)
    best, pair = levels_4b.max_pair_alignment_4b(sets_m, sites_m, sets_q, sites_q, excluded=(0,))
    assert best == pytest.approx(v)
    assert 0 not in pair


def test_max_pair_alignment_4b_off_diagonal_pairs_score_zero():
    n_sites, v = 3, 0.6
    sets_m, sets_q, sites_m, sites_q = fakes_4b.planted_tables(n_sites, n_items=32, v=v, seed=5)
    # site 1 on m against site 2 on q: different sites, structurally 0
    # shared ids by construction.
    from experiments.exp4 import metric_4
    frac = metric_4.overlap_counts(sets_m[1], sets_q[2]).astype(np.float64) / metric_4.K_4
    assert np.all(frac == 0.0)


# ----------------------------------------------------------------- ceiling_4b


def test_ceiling_4b_pinned_values_on_planted_tables(monkeypatch):
    # Review fix: `ceiling_4b` was refactored to call `per_item_level_4b`
    # once per reference (reading the per-pair vectors off its
    # "_by_ref" output, `twins_4b`'s own structure) instead of
    # duplicating the overlap -> filter -> mean arithmetic. This pins
    # its output on `planted_tables`, both `excluded` and `included`,
    # so a future drift between the two call sites `per_item_level_4b`
    # now serves is caught here rather than only at the (bit-identical
    # by construction, but unchecked at this grain) world level.
    n_sites, v, n_items = 4, 0.3, 40   # round(v*10)=3 exactly -- avoids the round-half-to-even edge
    sets_m, sets_q, sites, _ = fakes_4b.planted_tables(n_sites, n_items=n_items, v=v, seed=3)
    rungs = ["rungA", "rungB"]
    refs = ("ref_pythia_12b", "ref_olmo2_7b")
    arr_by_ref = {refs[0]: sets_m, refs[1]: sets_q}

    def fake_load_one_unit(root, key):
        return {"record": {"sites": list(sites), "n_hidden": n_sites},
               "sets": {r: arr_by_ref[key] for r in rungs}}

    monkeypatch.setattr(levels_4b.an, "_load_one_unit_4", fake_load_one_unit)
    monkeypatch.setattr(levels_4b.battery_4, "REFERENCES_4", refs)

    out_excluded = levels_4b.ceiling_4b("unused-root", excluded=(0,))
    out_included = levels_4b.ceiling_4b("unused-root", excluded=())

    expected_included = (1.0 + (n_sites - 1) * v) / n_sites
    for a, b in ((refs[0], refs[1]), (refs[1], refs[0])):
        assert set(out_excluded["pairs"][a]) == {b}
        assert set(out_excluded["pairs"][a][b]) == set(rungs)
        for r in rungs:
            assert out_excluded["pairs"][a][b][r]["mean"] == pytest.approx(v)
            assert out_included["pairs"][a][b][r]["mean"] == pytest.approx(expected_included)


# ------------------------------------------------------------- slow: world

WORLD_SEED_4B = 401


@pytest.fixture(scope="module")
def _leads_world(tmp_path_factory):
    """ONE full-grid LEADS-mode world (`test_power_ext_4b.py`'s own
    module-scoped pattern), shared read-only by every slow test in
    this file."""
    root = tmp_path_factory.mktemp("levels_leads_world")
    fs.build_world(root, "leads", seed=WORLD_SEED_4B, stage="full")
    return root


@pytest.mark.slow
def test_ladder_4b_on_full_shape_world_reports_eight_sizes(_leads_world):
    out = levels_4b.ladder_4b(_leads_world)
    assert out["sizes"] == list(battery_4.LADDER_SIZES_4)
    assert len(out["sizes"]) == 8
    assert out["known_in_advance"] is True
    assert set(out["per_rung"]) == set(battery_4.RUNGS)
    for r in battery_4.RUNGS:
        entry = out["per_rung"][r]
        assert set(entry["a_by_size"]) == set(battery_4.LADDER_SIZES_4)
        assert set(entry["ci_by_size"]) == set(battery_4.LADDER_SIZES_4)
        for size in battery_4.LADDER_SIZES_4:
            ci = entry["ci_by_size"][size]
            assert ci["ci95"][0] <= entry["a_by_size"][size] <= ci["ci95"][1]
        rho = entry["rho_log_params"]
        if rho is not None:
            assert -1.0 <= rho <= 1.0
    # the synthetic world's `_write_synthetic_unit` never writes
    # global.npz (full_shape.py's own module docstring) — the global
    # bank degrades to unavailable, disclosed rather than crashing.
    assert out["global"]["available"] is False
    assert "note" in out["global"]


@pytest.mark.slow
def test_twins_4b_on_full_shape_world_covers_every_trajectory_and_rung(_leads_world):
    out = levels_4b.twins_4b(_leads_world)
    assert set(out) == set(battery_4.TRAJECTORIES_4)
    for traj in battery_4.TRAJECTORIES_4:
        assert set(out[traj]) == set(battery_4.RUNGS)
        for r in battery_4.RUNGS:
            ci = out[traj][r]
            assert 0.0 <= ci["mean"] <= 1.0
            assert ci["ci95"][0] <= ci["mean"] <= ci["ci95"][1]


@pytest.mark.slow
def test_ceiling_4b_on_full_shape_world_covers_every_reference_pair(_leads_world):
    out = levels_4b.ceiling_4b(_leads_world)
    refs = battery_4.REFERENCES_4
    assert set(out["pairs"]) == set(refs)
    for a in refs:
        others = set(refs) - {a}
        assert set(out["pairs"][a]) == others
        for b in others:
            per_rung = out["pairs"][a][b]
            assert set(per_rung) == set(battery_4.RUNGS)
            for r in battery_4.RUNGS:
                ci = per_rung[r]
                assert ci["ci95"][0] <= ci["mean"] <= ci["ci95"][1]


@pytest.mark.slow
def test_within_family_4b_on_full_shape_world_has_ci_only_at_the_edges(_leads_world):
    out = levels_4b.within_family_4b(_leads_world)
    assert out["traj"] == "pythia_2.8b"
    assert out["ref"] == "ref_pythia_12b"
    steps = list(battery_4.GRID_4["pythia_2.8b"])
    assert set(out["per_rung"]) == set(battery_4.RUNGS)
    for r in battery_4.RUNGS:
        entry = out["per_rung"][r]
        assert entry["steps"] == steps
        assert len(entry["a"]) == len(steps)
        assert entry["ci_t1"]["ci95"][0] <= entry["ci_t1"]["mean"] <= entry["ci_t1"]["ci95"][1]
        assert entry["ci_end"]["ci95"][0] <= entry["ci_end"]["mean"] <= entry["ci_end"]["ci95"][1]
        # the point series' own endpoints agree with the CI blocks'
        # means (same underlying vector, re-derived once for the
        # series and once — deliberately — for the CI).
        assert entry["a"][0] == pytest.approx(entry["ci_t1"]["mean"], abs=1e-9)
        assert entry["a"][-1] == pytest.approx(entry["ci_end"]["mean"], abs=1e-9)


# `max_over_pairs_4b`'s full cross product is expensive at real
# site/grid counts (`collect_4._max_over_pairs` scans EVERY (site_m,
# site_q) pair, each a python-level `overlap_counts` loop over every
# item — exactly why `full_shape.py` itself restricts
# `compute_max_pairs=True` to one trajectory even for the ATTESTED
# reading it stores). Rather than pay a real 21-26-step, ~27-flat-rung,
# 3-ref, up-to-13x13-site cross product (tens of millions of python-
# level set intersections — no `_leads_world` build makes that cheap),
# this test keeps the REAL committed outcome/grid/rung-set machinery
# (`battery_4.load_outcome_4`/`rung_sets_4`/`GRID_4`/`REFS_FOR_4` — all
# fast JSON reads) and fakes only the per-unit SET TABLES, at a small
# `n_sites`/`n_items`, via `monkeypatch` on `an._load_one_unit_4` and
# `collect_4.load_ref_tables_4` as `levels_4b` itself imports them —
# exercising the SAME wiring (needed-rung union, per-ref averaging,
# `trend_4`/`excess_4`/`phi_4`, per-cell reduction, `pooled_phi`) a
# real tree would, at a cost of milliseconds instead of minutes.

_FAKE_N_SITES, _FAKE_N_ITEMS, _FAKE_K = 4, 30, 10


def test_max_over_pairs_4b_wiring_with_small_fake_set_tables(monkeypatch):
    traj = "pythia_2.8b"
    floors = bg.load_floors()
    battery = bt.load_battery()
    outcome = battery_4.load_outcome_4(traj, battery=battery)
    rs = battery_4.rung_sets_4(outcome, floors)
    assert rs["R"], "pythia_2.8b must have at least one rising rung to pick a cell from"
    cell_rung = rs["R"][0]
    steps = list(battery_4.GRID_4[traj])
    t_clear_index = min(4, len(steps) - 2)
    assert t_clear_index >= an.MIN_CLEAR_INDEX_4
    cells = [{"traj": traj, "rung": cell_rung, "t_clear_index": t_clear_index}]

    ref_arr, _, ref_sites, _ = fakes_4b.planted_tables(
        _FAKE_N_SITES, n_items=_FAKE_N_ITEMS, v=0.5, seed=0)

    class _MissingReturnsConstant(dict):
        def __init__(self, const):
            super().__init__()
            self._const = const

        def __missing__(self, key):
            return self._const

    def fake_load_one_unit(root, key):
        _traj, s = key
        i = steps.index(s)
        flat_arr = fakes_4b.match_sets(ref_arr, 0.2, k=_FAKE_K, seed=1000 + i)
        cell_v = min(0.05 + 0.03 * i, 0.9)
        cell_arr = fakes_4b.match_sets(ref_arr, cell_v, k=_FAKE_K, seed=2000 + i)
        sets = _MissingReturnsConstant(flat_arr)
        sets[cell_rung] = cell_arr
        return {"record": {"sites": list(range(_FAKE_N_SITES))}, "sets": sets}

    def fake_load_ref_tables(root, refs):
        sets = _MissingReturnsConstant(ref_arr)
        return {ref: {"sets": sets, "sites": list(ref_sites), "n_hidden": _FAKE_N_SITES}
               for ref in refs}

    monkeypatch.setattr(levels_4b.an, "_load_one_unit_4", fake_load_one_unit)
    monkeypatch.setattr(levels_4b.collect_4, "load_ref_tables_4", fake_load_ref_tables)

    out = levels_4b.max_over_pairs_4b("unused-root", cells)
    assert out["n_cells"] == 1
    assert out["excluded_pair_note"]
    entry = out["cells"][0]
    assert entry["traj"] == traj
    assert entry["rung"] == cell_rung
    assert len(entry["series"]) == len(steps)
    assert entry["series"][0] == pytest.approx(0.0, abs=1e-12)     # excess_4 zeros t_1
    # the cell rung's own alignment rises with step index while the
    # flat pool is held flat -- the excess (and hence phi) must be a
    # real, non-None reading, not the "constant series" degenerate
    # `phi_4` returns None for.
    assert entry["phi"] is not None
    assert isinstance(entry["phi"], float)
    assert out["pooled_phi"] == pytest.approx(entry["phi"])
    assert out["n_phi"] == 1
