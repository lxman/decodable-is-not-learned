import itertools, numpy as np, pytest
from experiments.exp4c import rank_4c as rk


def _series(a_by_rung, steps):
    return {"steps": list(steps), "a": {r: list(v) for r, v in a_by_rung.items()}}


def test_q_is_the_mid_rank_quantile_with_ties_at_half():
    assert rk.q_cell_4c(0.5, [0.1, 0.2, 0.9, 1.0]) == (0.5, 0)
    assert rk.q_cell_4c(0.2, [0.1, 0.2, 0.9, 1.0]) == (0.375, 1)     # 1 below + ½·1 tie over 4
    assert rk.q_cell_4c(2.0, [0.1, 0.2]) == (1.0, 0) and rk.q_cell_4c(-1.0, [0.1, 0.2]) == (0.0, 0)
    with pytest.raises(ValueError):
        rk.q_cell_4c(0.0, [])


def test_growth_is_the_series_minus_its_own_first_point():
    assert rk.growth_4c([0.2, 0.3, 0.5]) == [0.0, pytest.approx(0.1), pytest.approx(0.3)]


def _two_runs():
    steps = [1, 2, 3, 4, 5]
    # run A: rising add3_mid clears at index 3 (t⁻ = 2); flat pool mod13/mod17/caesar; transient dropped
    a = {"add3_mid": [0.0, 0.1, 0.5, 0.6, 0.7], "mod13": [0.0, 0.1, 0.2, 0.3, 0.4], "mod17": [0.0, 0.0, 0.1, 0.2, 0.3],
         "caesar": [0.0, 0.2, 0.3, 0.3, 0.3], "antonym": [0.0, 0.1, 0.05, 0.6, 0.8]}
    rsA = {"R": ["add3_mid", "antonym"], "flat": ["caesar", "mod13", "mod17"], "transient": [], "t_clear": {"add3_mid": 4, "antonym": 5}}
    rsB = {"R": ["add3_mid"], "flat": ["mod13", "mod17"], "transient": ["caesar"], "t_clear": {"add3_mid": 3}}
    b = {"add3_mid": [0.0, 0.05, 0.1, 0.2, 0.2], "mod13": [0.0, 0.2, 0.4, 0.5, 0.5], "mod17": [0.0, 0.3, 0.4, 0.5, 0.5], "caesar": [0.0] * 5}
    return {"A": _series(a, steps), "B": _series(b, steps)}, {"A": rsA, "B": rsB}


def test_cells_read_growth_at_the_last_pre_clear_index_among_the_flat_pool():
    S, RS = _two_runs(); cells = rk.cells_4c(S, RS)
    by = {(c["traj"], c["rung"]): c for c in cells}
    a = by[("A", "add3_mid")]; assert a["c"] == 3 and a["t_minus_index"] == 2 and a["t_minus_step"] == 3
    assert a["q"] == 1.0 and a["n_flat"] == 3 and a["n_ties"] == 0                # g=.5 vs .2/.1/.3
    assert a["q_arith"] == 1.0 and a["n_flat_arith"] == 2                          # caesar is a string task
    an = by[("A", "antonym")]; assert an["c"] == 4 and an["q"] == 1.0 and an["q_arith"] is None   # g at index 3 = .6, flat g = .3/.2/.3 -> q = 1.0
    bb = by[("B", "add3_mid")]; assert bb["c"] == 2 and bb["q"] == 0.0             # g=.05 vs .2/.3
    assert {c["family"] for c in cells} == {"mid_digit", "antonym"}


def test_cells_q_arith_ranks_against_the_arithmetic_flat_pool_only():
    """The existing `add3_mid`/caesar fixture above doesn't discriminate
    the arithmetic ranking pool from the whole one (add3_mid's growth
    exceeds every flat member either way); this one does: the rising
    task's growth sits BELOW the non-arithmetic flat member (caesar)
    but ABOVE both arithmetic flat members, so q (whole pool) and
    q_arith (arithmetic-only pool) must differ."""
    steps = [1, 2, 3]
    a = {"add3_mid": [0.0, 0.5, 0.6], "caesar": [0.0, 0.9, 0.95], "mod13": [0.0, 0.1, 0.15],
        "mod17": [0.0, 0.2, 0.25]}
    rs = {"A": {"R": ["add3_mid"], "flat": ["caesar", "mod13", "mod17"], "transient": [],
                "t_clear": {"add3_mid": 3}}}
    S = {"A": _series(a, steps)}
    cells = rk.cells_4c(S, rs)
    c = cells[0]
    assert c["t_minus_index"] == 1 and c["n_flat"] == 3 and c["n_flat_arith"] == 2
    assert c["q"] == pytest.approx(2 / 3)          # below caesar(.9), above mod13(.1)/mod17(.2)
    assert c["q_arith"] == pytest.approx(1.0)       # ranked among mod13/mod17 ONLY: above both


def test_cells_drop_no_window_and_transient():
    S, RS = _two_runs(); RS["A"]["t_clear"]["add3_mid"] = 2   # index 1 < 2
    assert ("A", "add3_mid") not in {(c["traj"], c["rung"]) for c in rk.cells_4c(S, RS)}


def test_block_flip_is_exact_with_two_one_sided_tails():
    cells = [{"family": "f1", "rung": "r1", "q": 0.9}, {"family": "f1", "rung": "r2", "q": 0.8}, {"family": "f2", "rung": "r3", "q": 0.7}]
    out = rk.block_flip_4c(cells)
    assert out["n_blocks"] == 2 and out["n_flips"] == 4 and out["method"] == "exact"
    # obs = .9 is the enumeration's own maximum (both block sums positive): p_plus is the whole
    # upper tail (1 of 4), p_minus the empirical CDF at obs — the whole distribution sits at or
    # below its own maximum, so p_minus == 1.0 (Exp 4's `primary_4` convention, analyze_4.py:648).
    assert out["p_plus"] == 0.25 and out["p_minus"] == 1.0 and out["observed"] == pytest.approx(0.9)
    # The mirror fixture (q's reflected around .5): obs is now the minimum, so the tails swap.
    mirrored = [{"family": "f1", "rung": "r1", "q": 0.1}, {"family": "f1", "rung": "r2", "q": 0.2}, {"family": "f2", "rung": "r3", "q": 0.3}]
    m = rk.block_flip_4c(mirrored)
    assert m["p_plus"] == 1.0 and m["p_minus"] == 0.25 and m["observed"] == pytest.approx(-0.9)
    null = [{"family": f, "rung": f, "q": 0.5} for f in "abc"]
    nl = rk.block_flip_4c(null)
    assert nl["p_plus"] == 1.0 and nl["p_minus"] == 1.0
    with pytest.raises(ValueError):
        rk.block_flip_4c([{"family": str(i), "rung": str(i), "q": .6} for i in range(21)])


def test_bootstrap_is_family_clustered_and_seeded():
    cells = [{"family": "f1", "rung": "r1", "q": 0.9}, {"family": "f2", "rung": "r2", "q": 0.1}]
    a = rk.cluster_bootstrap_ci_4c(cells, n_boot=200, seed=1); b = rk.cluster_bootstrap_ci_4c(cells, n_boot=200, seed=1)
    assert a == b and a["lo"] in (0.1, 0.5, 0.9) and a["hi"] in (0.1, 0.5, 0.9)


def test_bootstrap_resamples_whole_blocks_not_individual_cells():
    """The PREVIOUS test's fixture (1 cell per family) cannot tell block
    resampling from cell resampling apart — with 1 cell per block the
    two coincide. Here family A holds 100 zeros and family B a single
    1.0: resampling BLOCKS (2 of them, with replacement) draws the
    all-B combination (mean 1.0) on 1/4 of draws, so with n_boot=4000
    the 97.5th percentile must be exactly 1.0; resampling the 101
    underlying CELLS directly would essentially never draw all ones."""
    cells = ([{"family": "A", "rung": f"a{i}", "q": 0.0} for i in range(100)]
            + [{"family": "B", "rung": "b0", "q": 1.0}])
    out = rk.cluster_bootstrap_ci_4c(cells, n_boot=4000, seed=0)
    assert out["n_blocks"] == 2
    assert out["hi"] == 1.0
    assert out["lo"] == 0.0


def test_tree_and_modifier_cells():
    assert rk.verdict_tree_4c(["x"], None)["verdict"] == "INSUFFICIENT_DATA"
    assert rk.verdict_tree_4c([], {"p_plus": 0.009, "p_minus": 0.99})["verdict"] == "REPLICATES"
    assert rk.verdict_tree_4c([], {"p_plus": 0.02, "p_minus": 0.98})["verdict"] == "MARGINAL"
    v = rk.verdict_tree_4c([], {"p_plus": 0.5, "p_minus": 0.5}); assert v["verdict"] == "NOT-REPLICATED" and v["reversed"] is False
    v = rk.verdict_tree_4c([], {"p_plus": 0.99, "p_minus": 0.03}); assert v["verdict"] == "NOT-REPLICATED" and v["reversed"] is True
    assert rk.calibration_read_4c({"alpha_placebo_01": 0.03, "alpha_placebo_05": 0.06}, "REPLICATES")["bounded"] is True
    assert rk.calibration_read_4c({"alpha_placebo_01": 0.019, "alpha_placebo_05": 0.2}, "REPLICATES")["bounded"] is False
    assert rk.calibration_read_4c({"alpha_placebo_01": 0.5, "alpha_placebo_05": 0.11}, "MARGINAL")["bounded"] is True


def test_modifier_type_general_decided_at_the_marginal_bar_not_alpha():
    """Seven arithmetic families (the same zero-deviation construction
    as the placebo alpha test): U_arith's family-block p+ lands at
    2/128 = .015625 — inside [ALPHA_4C, MARGINAL_4C) = [.01, .05).
    TYPE-GENERAL fires because the modifier reads MARGINAL_4C, not
    ALPHA_4C."""
    cells = ([{"family": f"f{k}", "type": "arithmetic", "q_arith": 1.0} for k in range(1, 7)]
            + [{"family": "f7", "type": "arithmetic", "q_arith": 0.5}])
    out = rk.type_modifier_4c(cells)
    assert out["arith"]["p_plus"] == pytest.approx(2 / 128)
    assert out["modifier"] == "TYPE-GENERAL"


def test_modifier_refuses_a_family_p_for_the_nonarith_stratum():
    S, RS = _two_runs(); out = rk.type_modifier_4c(rk.cells_4c(S, RS))
    assert out["nonarith"]["p_family"] is None and "cannot resolve" in out["nonarith"]["p_family_reason"]
    assert out["arith"]["n_cells"] == 2 and out["modifier"] in rk.MODIFIERS_4C


def test_placebo_pool_is_the_common_flat_set_and_removes_the_drawn_task():
    S, RS = _two_runs(); cells = rk.cells_4c(S, RS)
    out = rk.placebo_4c(S, RS, cells, B=50, seed=0)
    assert out["pool_common"] == ["mod13", "mod17"] and out["U_b"].shape == (50,)
    assert 0.0 <= out["p_placebo"] <= 1.0 and 0.0 <= out["alpha_placebo_01"] <= out["alpha_placebo_05"] <= 1.0


def test_placebo_draw_excludes_itself_from_its_own_comparator_pool():
    """A numeric, draw-independent discriminator: two trajectories'
    flat sets intersect at exactly one task ("h1"), so the placebo
    draw is DETERMINISTIC (`rng.integers(1)` is always 0) regardless of
    seed. Traj A's own flat pool has two more members (h2/h3) the
    drawn task must be scored against with itself excluded."""
    steps = [1, 2]
    a = {"h1": [0.0, 0.9], "h2": [0.0, 0.1], "h3": [0.0, 0.2]}
    b = {"h1": [0.0, 0.9], "hX": [0.0, 0.5]}
    S = {"A": _series(a, steps), "B": _series(b, steps)}
    RS = {"A": {"flat": ["h1", "h2", "h3"]}, "B": {"flat": ["h1", "hX"]}}
    cells = [{"traj": "A", "rung": "r", "family": "F", "type": "arithmetic", "t_minus_index": 1,
             "q": 0.5}]                                    # "q": placebo_4c's own U_4c(cells) needs it
    out = rk.placebo_4c(S, RS, cells, B=2, seed=0)          # B=2, not 1: std(ddof=1) needs >=2 points
    assert out["pool_common"] == ["h1"]                 # deterministic draw: always "h1"
    # self (h1=.9) excluded: ranked among h2=.1/h3=.2 only -> both below -> q=1.0
    assert out["null_mean"] == pytest.approx(1.0)


def test_placebo_alpha_01_uses_the_01_bar_not_the_05_bar():
    """Seven families, one deterministic placebo battery (pool_common
    size 1, so the draw never varies): six score q=1.0, one scores
    exactly q=0.5 (a zero-deviation family, so BOTH its sign choices
    tie at the observed maximum) — the family-block enumeration over 7
    blocks (128 flips) then has EXACTLY 2 flips at or above the
    observed sum, p_plus = 2/128 = .015625, strictly between ALPHA_4C
    (.01) and MARGINAL_4C (.05): `alpha_placebo_01` must read 0.0 and
    `alpha_placebo_05` must read 1.0 — if they read the same value,
    fires01 used the wrong bar."""
    steps = list(range(8))
    h1 = [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5]
    m1 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    m2 = [0.0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1.0]
    S = {"A": _series({"h1": h1, "m1": m1, "m2": m2}, steps),
        "B": _series({"h1": [0.0] * 8, "hY": [0.0] * 8}, steps)}
    RS = {"A": {"flat": ["h1", "m1", "m2"]}, "B": {"flat": ["h1", "hY"]}}
    cells = [{"traj": "A", "rung": f"r{k}", "family": f"f{k}", "type": "arithmetic",
             "t_minus_index": k, "q": 0.5} for k in range(1, 8)]   # "q": U_4c(cells) needs it
    out = rk.placebo_4c(S, RS, cells, B=2, seed=0)
    assert out["pool_common"] == ["h1"]                 # deterministic draw
    assert out["alpha_placebo_01"] == 0.0
    assert out["alpha_placebo_05"] == 1.0


def test_placebo_carries_the_non_arithmetic_stratum_reading():
    # design §3.5: "the non-arithmetic stratum's rung-level flip and its placebo p are printed
    # as descriptives" — of the fixture's three cells, only ("A", "antonym") is non-arithmetic.
    S, RS = _two_runs(); cells = rk.cells_4c(S, RS)
    out = rk.placebo_4c(S, RS, cells, B=50, seed=0)
    assert out["n_nonarith_cells"] == 1
    assert out["U_b_nonarith"].shape == (50,) and not np.any(np.isnan(out["U_b_nonarith"]))
    assert out["U_nonarith"] is not None
    assert 0.0 <= out["p_placebo_nonarith"] <= 1.0


def test_placebo_nonarith_reading_is_none_without_a_nonarithmetic_rising_task():
    S, RS = _two_runs()
    RS = {"A": dict(RS["A"], R=["add3_mid"]), "B": RS["B"]}   # drop antonym, the only non-arithmetic riser
    cells = rk.cells_4c(S, RS)
    assert {c["type"] for c in cells} == {"arithmetic"}
    out = rk.placebo_4c(S, RS, cells, B=20, seed=0)
    assert out["n_nonarith_cells"] == 0
    assert out["U_nonarith"] is None and out["p_placebo_nonarith"] is None
    assert out["U_b_nonarith"].shape == (20,) and np.all(np.isnan(out["U_b_nonarith"]))


def test_window_mean_cells_averages_over_the_full_preclear_window():
    S, RS = _two_runs(); cells = rk.window_mean_cells_4c(S, RS)
    by = {(c["traj"], c["rung"]): c for c in cells}
    a = by[("A", "add3_mid")]
    assert a["n_window"] == 2 and a["q"] == pytest.approx(0.75) and a["q_arith"] == pytest.approx(0.875)
    an = by[("A", "antonym")]
    assert an["n_window"] == 3 and an["q"] == pytest.approx(0.5) and an["q_arith"] is None
    bb = by[("B", "add3_mid")]
    assert bb["n_window"] == 1 and bb["q"] == pytest.approx(0.0) and bb["q_arith"] == pytest.approx(0.0)


def test_within_riser_ranks_against_other_not_yet_cleared_risers():
    S, RS = _two_runs(); out = rk.within_riser_4c(S, RS)
    by = {(c["traj"], c["rung"]): c for c in out["cells"]}
    assert by[("A", "add3_mid")]["n_comparators"] == 1 and by[("A", "add3_mid")]["q_within"] == pytest.approx(1.0)
    assert by[("A", "antonym")]["n_comparators"] == 0 and by[("A", "antonym")]["q_within"] is None
    assert by[("B", "add3_mid")]["n_comparators"] == 0 and by[("B", "add3_mid")]["q_within"] is None
    assert out["n_with_comparators"] == 1 and out["U_within"] == pytest.approx(1.0)


def test_within_riser_counts_a_co_clearing_task_as_a_comparator():
    # design §5: comparators are the run's rising tasks that "have NOT yet cleared at t⁻" — a
    # task with clear index c2 has not cleared at index c-1 iff c2 >= c (the design's binding
    # rule, over the plan's stricter c2 > c). r1 and r2 co-clear at c=3: each must count the
    # OTHER as a comparator despite c2 == c. r3 cleared EARLIER (c=2 < 3): excluded as r1/r2's
    # comparator, but r1 and r2 (not yet cleared at r3's own t⁻) count as r3's comparators.
    steps = [0, 1, 2, 3, 4]
    a = {"r1": [0.0, 0.1, 0.2, 0.9, 1.0], "r2": [0.0, 0.1, 0.3, 0.8, 0.9], "r3": [0.0, 0.1, 0.05, 0.2, 0.3]}
    S = {"A": _series(a, steps)}
    RS = {"A": {"R": ["r1", "r2", "r3"], "flat": [], "transient": [], "t_clear": {"r1": 3, "r2": 3, "r3": 2}}}
    out = rk.within_riser_4c(S, RS)
    by = {c["rung"]: c for c in out["cells"]}
    assert by["r1"]["n_comparators"] == 1 and by["r1"]["q_within"] == pytest.approx(0.0)
    assert by["r2"]["n_comparators"] == 1 and by["r2"]["q_within"] == pytest.approx(1.0)
    assert by["r3"]["n_comparators"] == 2 and by["r3"]["q_within"] == pytest.approx(0.5)


def test_never_performing_type_check_ranks_nonarith_flat_among_arith_flat():
    S, RS = _two_runs(); out = rk.never_performing_type_check_4c(S, RS)
    assert out["n_task_runs"] == 1                        # only run A has a non-arithmetic flat task (caesar)
    row = out["per_task_run"][0]
    assert row["traj"] == "A" and row["rung"] == "caesar" and row["n_arith_flat"] == 2 and row["n_grid"] == 4
    assert row["mean_q"] == pytest.approx(0.75) and out["mean"] == pytest.approx(0.75)


def _tiny_alignment_fixture(k=4, n_items=3):
    rng = np.random.default_rng(0)
    sets_m = {r: rng.integers(0, 5, size=(2, n_items, k)).astype(np.uint16) for r in rk.bc.RUNGS}
    sets_q = {r: rng.integers(0, 5, size=(2, n_items, k)).astype(np.uint16) for r in rk.bc.RUNGS}
    ref_tables = {"ref_x": sets_q}
    unit = {"record": {"pairing": {"ref_x": [0, 1]}, "sites": [0, 1]}, "sets": sets_m, "overlaps": {}}
    return {1: unit}, ref_tables


def test_alignment_series_4c_excludes_site0_by_default():
    """The PREVIOUS test passes `excluded_sites=(0,)` explicitly, which
    exercises the module's DEFAULT-independent behaviour but not the
    default itself — a source-level mutation of `EXCLUDED_SITES_4C`
    would go unnoticed there. This one relies on the default."""
    tables_by_step, ref_tables = _tiny_alignment_fixture()
    out = rk.alignment_series_4c(tables_by_step, ref_tables, steps=[1])
    assert out["n_sites_kept"] == 1 and out["excluded_sites"] == [0]


def test_alignment_series_4c_excludes_site0_and_matches_the_single_reference():
    tables_by_step, ref_tables = _tiny_alignment_fixture()
    out = rk.alignment_series_4c(tables_by_step, ref_tables, steps=[1], excluded_sites=(0,))
    assert out["n_sites_kept"] == 1 and out["excluded_sites"] == [0] and out["steps"] == [1]
    for rung in rk.bc.RUNGS:
        assert len(out["a"][rung]) == 1 and 0.0 <= out["a"][rung][0] <= 1.0
        # a single reference: the pooled series equals that reference's own series exactly.
        assert out["a_by_ref"]["ref_x"][rung][0] == pytest.approx(out["a"][rung][0])


def test_alignment_series_4c_refuses_an_empty_kept_site_set():
    tables_by_step, ref_tables = _tiny_alignment_fixture()
    with pytest.raises(ValueError, match="excludes the whole site family"):
        rk.alignment_series_4c(tables_by_step, ref_tables, steps=[1], excluded_sites=(0, 1))


def test_alignment_series_4c_raises_naming_rung_ref_on_stored_overlap_disagreement():
    tables_by_step, ref_tables = _tiny_alignment_fixture()
    bad_rung = rk.bc.RUNGS[0]
    tables_by_step[1]["overlaps"] = {"ref_x": {bad_rung: np.zeros((2, 3), dtype=np.uint8)}}
    with pytest.raises(ValueError, match=f"{bad_rung}/ref_x/site"):
        rk.alignment_series_4c(tables_by_step, ref_tables, steps=[1])


@pytest.mark.slow
def test_discovery_set_reproduces_the_design_session_and_is_site0_invariant():
    rec = rk.discovery_set_4c()
    assert rk.check_discovery_pins_4c(rec) == []
    assert round(rec["U"], 4) == 0.6224 and rec["n_cells"] == 42 and round(rec["p_family"], 4) == 0.0391
    assert round(rec["U_arith"], 4) == 0.5103 and round(rec["U_nonarith"], 4) == 0.7595
    assert rec["site0_excluded"]["n_cells_q_identical"] == 42 and rec["site0_excluded"]["max_abs_q_diff"] == 0.0
    _assert_design_doc_literals_4c(rec)


def _assert_design_doc_literals_4c(rec, *, counts=True):
    """FREEZE F-6: design §2(3)/§2(4)/§3.7(1) print EVERY discovery
    number to four decimals, and only five of them were asserted
    against the doc — `DISCOVERY_PIN_4C`'s own full-precision entries
    are checked against themselves by `check_discovery_pins_4c`, so a
    pin mistyped relative to the doc it was copied from would have
    shown nowhere. The rest of §3.7(1)'s list, asserted here."""
    assert round(rec["p_rung"], 4) == 0.0092
    if counts:
        # `DISCOVERY_PIN_4C` does not carry the two stratum counts; the
        # slow test, which has the real record, asserts them.
        assert rec["n_arith"] == 26 and rec["n_nonarith"] == 16
    assert {k: round(v, 3) for k, v in rec["per_run"].items()} == {
        "pythia_2.8b": 0.487, "olmo2_7b": 0.630, "smollm3_3b": 0.694, "comma_7b": 0.646}


def test_the_discovery_pins_themselves_carry_the_design_docs_literals():
    """FREEZE F-6, without touching Exp 4's tree: the SAME assertions
    against `DISCOVERY_PIN_4C` directly, so the doc-vs-pin comparison
    runs in the FAST suite and not only in the slow one."""
    pin = dict(rk.DISCOVERY_PIN_4C)
    assert round(pin["U"], 4) == 0.6224 and pin["n_cells"] == 42
    assert round(pin["p_family"], 4) == 0.0391
    assert round(pin["U_arith"], 4) == 0.5103 and round(pin["U_nonarith"], 4) == 0.7595
    _assert_design_doc_literals_4c(pin, counts=False)
    assert len(pin["family_sums"]) == 9


# ---------------- FREEZE: the licence sentences' DIRECTION (4b F-3's
# class) — REPLICATES and MARGINAL both assert the rising tasks grew
# MORE, and REVERSED asserts they grew LESS. Both are implied by the
# exact flip's own symmetry rather than checked anywhere, so the
# implication is pinned here.

def test_a_significant_p_plus_implies_U_above_one_half_and_p_minus_below_implies_under():
    """`tot(-s) = -tot(s)` and the enumeration contains `-s` for every
    `s`, so the flip distribution is exactly symmetric about 0 and
    `p_plus = P(tot >= obs)` is at least 1/2 whenever `obs <= 0`.
    Hence `p_plus < MARGINAL_4C` forces `obs > 0`, i.e. U > 1/2 — the
    direction the REPLICATES and MARGINAL licence bodies assert — and
    `p_minus < MARGINAL_4C` forces U < 1/2, the direction REVERSED
    asserts. Checked over random batteries on the real family
    structure, both tails, including the obs == 0 boundary."""
    rng = np.random.default_rng(4)
    fams = [f"f{i}" for i in range(9)]
    seen_pos = seen_neg = 0
    for _ in range(400):
        cells = [{"family": fams[i % 9], "rung": f"r{i}",
                  "q": float(0.5 + rng.normal(scale=0.35))} for i in range(26)]
        fl = rk.block_flip_4c(cells)
        U = rk.U_4c(cells)
        if fl["p_plus"] < rk.MARGINAL_4C:
            assert U > 0.5 and fl["observed"] > 0
            seen_pos += 1
        if fl["p_minus"] < rk.MARGINAL_4C:
            assert U < 0.5 and fl["observed"] < 0
            seen_neg += 1
        assert fl["p_plus"] >= 1.0 / fl["n_flips"] and fl["p_minus"] >= 1.0 / fl["n_flips"]
    assert seen_pos and seen_neg, (seen_pos, seen_neg)
    flat = [{"family": fams[i % 9], "rung": f"r{i}", "q": 0.5} for i in range(26)]
    fl0 = rk.block_flip_4c(flat)
    assert fl0["observed"] == 0.0 and fl0["p_plus"] >= 0.5 and fl0["p_minus"] >= 0.5


# ------------- FINAL REVIEW minor: `p_family_reason` checks its own claim

def test_p_family_reason_says_the_null_cannot_resolve_at_three_families():
    """Design §3.5's expected case: 3 non-arithmetic families give
    2**3 = 8 flips, finest attainable p 1/8 = .125, above the .05 bar
    — the sentence's original, unconditional claim."""
    s = rk._p_family_reason_4c(3)
    assert "3 families give 8 flips" in s
    assert "cannot resolve" in s and "0.125" in s and "no p printed" in s


def test_p_family_reason_calls_the_refusal_categorical_when_the_null_could_resolve():
    """At 5 families the null gives 32 flips, finest p .03125 — BELOW
    the .05 bar — so the old sentence asserted something false while
    the refusal itself stayed right. The reason now names design §3.5
    instead."""
    s = rk._p_family_reason_4c(5)
    assert "5 families give 32 flips" in s
    assert "cannot resolve" not in s
    assert "categorical by design" in s and "0.03125" in s


def test_p_family_reason_switches_exactly_at_the_marginal_bar():
    fine = [1.0 / (1 << n) for n in range(1, 8)]
    for n, p in enumerate(fine, start=1):
        s = rk._p_family_reason_4c(n)
        assert ("cannot resolve" in s) is (p > rk.MARGINAL_4C), (n, p, s)


def test_the_modifier_still_refuses_the_family_p_in_both_branches():
    """The refusal is unconditional — only the reason moves."""
    for n_fams, needle in ((3, "cannot resolve"), (5, "categorical by design")):
        cells = [{"family": f"f{k}", "type": "option", "q": 0.9, "q_arith": None,
                  "rung": f"r{k}"} for k in range(n_fams)]
        out = rk.type_modifier_4c(cells)
        assert out["nonarith"]["p_family"] is None
        assert out["nonarith"]["n_families"] == n_fams
        assert needle in out["nonarith"]["p_family_reason"]
