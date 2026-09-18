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


def test_cells_drop_no_window_and_transient():
    S, RS = _two_runs(); RS["A"]["t_clear"]["add3_mid"] = 2   # index 1 < 2
    assert ("A", "add3_mid") not in {(c["traj"], c["rung"]) for c in rk.cells_4c(S, RS)}


def test_block_flip_is_exact_and_symmetric():
    cells = [{"family": "f1", "rung": "r1", "q": 0.9}, {"family": "f1", "rung": "r2", "q": 0.8}, {"family": "f2", "rung": "r3", "q": 0.7}]
    out = rk.block_flip_4c(cells)
    assert out["n_blocks"] == 2 and out["n_flips"] == 4 and out["method"] == "exact"
    assert out["p_plus"] == 0.25 and out["p_minus"] == 0.25 and out["observed"] == pytest.approx(0.9)
    null = [{"family": f, "rung": f, "q": 0.5} for f in "abc"]
    assert rk.block_flip_4c(null)["p_plus"] == 1.0
    with pytest.raises(ValueError):
        rk.block_flip_4c([{"family": str(i), "rung": str(i), "q": .6} for i in range(21)])


def test_bootstrap_is_family_clustered_and_seeded():
    cells = [{"family": "f1", "rung": "r1", "q": 0.9}, {"family": "f2", "rung": "r2", "q": 0.1}]
    a = rk.cluster_bootstrap_ci_4c(cells, n_boot=200, seed=1); b = rk.cluster_bootstrap_ci_4c(cells, n_boot=200, seed=1)
    assert a == b and a["lo"] in (0.1, 0.5, 0.9) and a["hi"] in (0.1, 0.5, 0.9)


def test_tree_and_modifier_cells():
    assert rk.verdict_tree_4c(["x"], None)["verdict"] == "INSUFFICIENT_DATA"
    assert rk.verdict_tree_4c([], {"p_plus": 0.009, "p_minus": 0.99})["verdict"] == "REPLICATES"
    assert rk.verdict_tree_4c([], {"p_plus": 0.02, "p_minus": 0.98})["verdict"] == "MARGINAL"
    v = rk.verdict_tree_4c([], {"p_plus": 0.5, "p_minus": 0.5}); assert v["verdict"] == "NOT-REPLICATED" and v["reversed"] is False
    v = rk.verdict_tree_4c([], {"p_plus": 0.99, "p_minus": 0.03}); assert v["verdict"] == "NOT-REPLICATED" and v["reversed"] is True
    assert rk.calibration_read_4c({"alpha_placebo_01": 0.03, "alpha_placebo_05": 0.06}, "REPLICATES")["bounded"] is True
    assert rk.calibration_read_4c({"alpha_placebo_01": 0.019, "alpha_placebo_05": 0.2}, "REPLICATES")["bounded"] is False
    assert rk.calibration_read_4c({"alpha_placebo_01": 0.5, "alpha_placebo_05": 0.11}, "MARGINAL")["bounded"] is True


def test_modifier_refuses_a_family_p_for_the_nonarith_stratum():
    S, RS = _two_runs(); out = rk.type_modifier_4c(rk.cells_4c(S, RS))
    assert out["nonarith"]["p_family"] is None and "cannot resolve" in out["nonarith"]["p_family_reason"]
    assert out["arith"]["n_cells"] == 2 and out["modifier"] in rk.MODIFIERS_4C


def test_placebo_pool_is_the_common_flat_set_and_removes_the_drawn_task():
    S, RS = _two_runs(); cells = rk.cells_4c(S, RS)
    out = rk.placebo_4c(S, RS, cells, B=50, seed=0)
    assert out["pool_common"] == ["mod13", "mod17"] and out["U_b"].shape == (50,)
    assert 0.0 <= out["p_placebo"] <= 1.0 and 0.0 <= out["alpha_placebo_01"] <= out["alpha_placebo_05"] <= 1.0


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
