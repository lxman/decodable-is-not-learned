# experiments/exp4/tests/test_analyze_4.py
"""Pure-function tests for `analyze_4.py` (Task 4 brief Step 1) plus
the eligibility bootstrap, `per_item_alignment_4`'s cross-check, and
the S2 known-answer gate. No torch, no network, no model contact."""
from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp4 import analyze_4 as an
from experiments.exp4 import battery_4
from experiments.exp4 import collect_4
from experiments.exp4 import metric_4


# ----------------------------------------------------------- brief Step 1

def test_excess_is_zero_at_t1_and_trend_subtracts():
    steps = [1, 2, 3, 4]
    a = {"r": [0.10, 0.20, 0.30, 0.40], "f1": [0.10, 0.15, 0.20, 0.25], "f2": [0.10, 0.15, 0.20, 0.25]}
    tr = an.trend_4(a, ["f1", "f2"], steps)
    assert tr == pytest.approx([0.10, 0.15, 0.20, 0.25])
    x = an.excess_4(a, tr, steps)
    assert x["r"] == pytest.approx([0.0, 0.05, 0.10, 0.15]) and x["r"][0] == 0.0


def test_phi_reads_the_last_point_before_the_clear():
    x = [0.0, 0.05, 0.10, 0.15]
    assert an.phi_4(x, 3) == pytest.approx(0.10 / 0.15)      # t_clear at index 3 -> t- index 2
    assert an.phi_4(x, 2) == pytest.approx(0.05 / 0.15)
    assert an.phi_4(x, 1) is None and an.phi_4(x, 0) is None   # no window
    assert an.phi_4([0.0, 0.0, 0.0, 0.0], 3) is None            # no endpoint excess


def test_primary_exact_flips_and_bars():
    cells = [{"traj": "a", "rung": f"r{i}", "phi": 0.6} for i in range(6)] + \
            [{"traj": "b", "rung": f"r{i}", "phi": 0.5} for i in range(6)]
    p = an.primary_4(cells, n_boot=200, seed=0)
    assert p["flip_method"] == "exact" and p["n_flips"] == 2 ** 6 and p["n_rungs"] == 6 and p["n_cells"] == 12
    assert p["T"] == pytest.approx(0.55) and p["p_plus"] == pytest.approx(1 / 64) and p["p_minus"] == 1.0
    # every bootstrap resample of this degenerate case reduces to the
    # identical multiset {0.6, 0.5} x 6, so ci95 collapses to a point
    # at T -- float64 arithmetic lands it at 0.5499999999999999, not
    # the literal 0.55, so the containment check carries a ULP-scale
    # tolerance (primary_4's own arithmetic, unmodified: T itself is
    # asserted above only via pytest.approx for the same reason)
    assert p["ci95"][0] <= 0.55 + 1e-9 and 0.55 - 1e-9 <= p["ci95"][1]
    v = an.verdict_tree_4([], 12, 6, dict(p, p_plus=0.005))
    assert v["verdict"] == "LEADS"


def test_tree_cells():
    base = {"T": 0.3, "p_plus": 0.004, "p_minus": 1.0, "ci95": [0.1, 0.5]}
    assert an.verdict_tree_4([], 5, 4, base)["verdict"] == "LEADS"
    assert an.verdict_tree_4([], 5, 4, dict(base, T=0.15, ci95=[0.05, 0.24]))["verdict"] == "PARTIAL"
    assert an.verdict_tree_4([], 5, 4, dict(base, T=0.02, p_plus=0.4, ci95=[-0.05, 0.10]))["verdict"] == "FOLLOWS"
    assert an.verdict_tree_4([], 5, 4, dict(base, T=0.15, p_plus=0.2, ci95=[-0.1, 0.4]))["verdict"] == "UNDETERMINED"
    assert an.verdict_tree_4([], 2, 2, base)["verdict"] == "NO-CONVERGENCE"
    assert an.verdict_tree_4([], 5, 2, base)["verdict"] == "NO-CONVERGENCE"
    assert an.verdict_tree_4(["4 something"], 5, 4, base)["verdict"] == "INSUFFICIENT_DATA"


def test_sign_flip_sampled_above_the_enumeration_cap():
    cells = [{"traj": "a", "rung": f"r{i}", "phi": 0.3 + 0.01 * i} for i in range(25)]
    p = an.primary_4(cells, n_boot=100, seed=0)
    assert p["flip_method"] == "sampled" and p["n_flips"] == an.N_FLIP_SAMPLE_4


# ------------------------------------------------------------- RUNG_TYPE_4

def test_rung_type_4_covers_the_34_rungs_exactly():
    assert set(an.RUNG_TYPE_4) == set(bt.RUNGS)
    counts = {}
    for typ in an.RUNG_TYPE_4.values():
        counts[typ] = counts.get(typ, 0) + 1
    assert counts == {"arithmetic": 25, "option": 4, "string": 5}


# ------------------------------------------------------- per_item_alignment_4

def _two_site_pair():
    """A tiny hand-built (sets_m, sets_q, pairing) triple: 2 sites, 3
    items, k=2 out of n=4 (padded to n=4 so overlap counts are
    non-trivial)."""
    sets_m = np.array([
        [[0, 1], [1, 2], [2, 3]],   # site 0: item i's neighbours
        [[3, 0], [0, 1], [1, 2]],   # site 1
    ], dtype=np.uint16)
    sets_q = np.array([
        [[0, 1], [1, 3], [2, 3]],   # site 0 (matches m's site 0 partially)
        [[3, 1], [0, 2], [1, 2]],   # site 1
    ], dtype=np.uint16)
    pairing = [0, 1]
    return sets_m, sets_q, pairing


def test_per_item_alignment_4_equals_metric_4_on_a_two_site_pair():
    sets_m, sets_q, pairing = _two_site_pair()
    tables_m = {"sets": {r: sets_m for r in battery_4.RUNGS}, "overlaps": {}}
    ref_tables = {"refX": {r: sets_q for r in battery_4.RUNGS}}
    pairing_by_ref = {"refX": pairing}
    out = an.per_item_alignment_4(tables_m, ref_tables, pairing_by_ref)
    expect_site0 = metric_4.overlap_counts(sets_m[0], sets_q[0]).astype(np.float64) / metric_4.K_4
    expect_site1 = metric_4.overlap_counts(sets_m[1], sets_q[1]).astype(np.float64) / metric_4.K_4
    expect = np.mean(np.stack([expect_site0, expect_site1]), axis=0)
    for r in battery_4.RUNGS:
        assert out[r] == pytest.approx(expect)


def test_per_item_alignment_4_refuses_a_disagreeing_stored_overlap():
    sets_m, sets_q, pairing = _two_site_pair()
    real_overlap = metric_4.overlap_counts(sets_m[0], sets_q[0])
    tampered = real_overlap.copy()
    tampered[0] = (tampered[0] + 1) % (metric_4.K_4 + 1)
    stale = np.stack([tampered, metric_4.overlap_counts(sets_m[1], sets_q[1])])
    tables_m = {"sets": {r: sets_m for r in battery_4.RUNGS},
               "overlaps": {"refX": {r: stale for r in battery_4.RUNGS}}}
    ref_tables = {"refX": {r: sets_q for r in battery_4.RUNGS}}
    pairing_by_ref = {"refX": pairing}
    with pytest.raises(ValueError, match="stored overlap disagrees"):
        an.per_item_alignment_4(tables_m, ref_tables, pairing_by_ref)


# ------------------------------------------------------------- eligibility

def _synthetic_reference_tree_leads(tmp_path):
    """A tiny synthetic reference-stage-only tree (Task 4's own world
    generator, mode='leads', restricted to stage 1) so
    `eligibility_table_4` can be exercised without a full sweep."""
    from experiments.exp4.tests import full_shape as fs
    fs.build_world(tmp_path, "leads", seed=1, stage="reference_only")
    return tmp_path


@pytest.mark.slow
def test_eligibility_table_4_on_a_synthetic_reference_tree(tmp_path):
    root = _synthetic_reference_tree_leads(tmp_path)
    table = an.eligibility_table_4(root, n_boot=200, seed=0)
    for traj in battery_4.TRAJECTORIES_4:
        block = table[traj]
        from experiments.exp2g import battery_2g as bg
        outcome = battery_4.load_outcome_4(traj)
        rs = battery_4.rung_sets_4(outcome, bg.load_floors())
        assert set(block["R"]) == set(rs["R"])
        assert set(block["flat"]) == set(rs["flat"])
        for rung, e in block["R"].items():
            if e["eligible"]:
                assert e["x_end"] >= an.SE_MULTIPLE_4 * e["se"] - 1e-9
                assert e["t_clear_index"] is None or e["t_clear_index"] >= an.MIN_CLEAR_INDEX_4
            else:
                assert e["reason"] in ("endpoint excess below 2 SE",
                                      "no pre-clear window (t_clear at grid index < 2)")


# -------------------------------------------------------- S2 known-answer

def test_s2_known_answer_gates_4_reproduces_2d_and_2e():
    out = an.s2_known_answer_gates_4()
    assert abs(out["auc_2d"] - 0.5454545454545454) < 1e-12
    assert abs(out["auc_2e"] - 0.6126482213438735) < 1e-12
    assert out["no_alpha_claim"] is True


# ----------------------------------------------------- real bug found by I-5(c)

@pytest.mark.slow
def test_s3_scale_4_does_not_crash_on_ref_pythia_12b(tmp_path):
    # A real, pre-existing bug -- not introduced by this fix round,
    # only surfaced by it (the LEADS world's new strict "every
    # secondary is a real value, never {'failed': ...}" check):
    # ref_pythia_12b (the "12b" ladder point) is written with refs=(),
    # so its own record's "pairing" field is empty -- handing that
    # straight to per_item_alignment_4 crashed on `np.stack([])`
    # ("need at least one array to stack") for EVERY rung, on any
    # tree, not only synthetic worlds. s3_scale_4 now re-derives the
    # pairing itself (via `collect_4._pairing_positions`, S8's own
    # pattern) whenever a unit's own stored pairing is empty.
    root = _synthetic_reference_tree_leads(tmp_path)
    out = an.s3_scale_4(root)
    assert out["source"] == "re-derived"
    for r in bt.RUNGS:
        assert "12b" in out["per_rung"][r]["a_by_size"]
        assert isinstance(out["per_rung"][r]["a_by_size"]["12b"], float)


# ------------------------------------------------------------------- I-7

@pytest.mark.slow
def test_read_sets_and_overlaps_requires_overlap_array_for_every_ref(tmp_path):
    # I-7(a): a unit whose record lists refs must carry one
    # overlap_<ref> array per (ref, rung) -- a silently-missing one
    # used to just skip that ref, undetected.
    import hashlib
    root = _synthetic_reference_tree_leads(tmp_path)
    traj = "pythia_2.8b"
    d = battery_4.reference_dir(root, f"endpoint_{traj}")
    rung = battery_4.RUNGS[0]
    p = d / "sets" / f"{rung}.npz"
    with np.load(p) as z:
        arrays = dict(z)
    ref_names = [k for k in arrays if k.startswith("overlap_")]
    assert ref_names, "fixture sanity: expected at least one overlap_<ref> array"
    del arrays[ref_names[0]]
    np.savez_compressed(p, **arrays)
    rec_path = d / "_load.json"
    rec = json.loads(rec_path.read_text())
    rec["sets_sha256"][rung] = hashlib.sha256(p.read_bytes()).hexdigest()
    rec_path.write_text(json.dumps(rec, indent=1))
    with pytest.raises(ValueError, match="overlap_"):
        an._load_one_unit_4(root, f"endpoint_{traj}")


@pytest.mark.slow
def test_load_one_unit_4_requires_full_34_rung_sha_map(tmp_path):
    # I-7(b): `set(rec["sets_sha256"]) == set(RUNGS)` -- a 33-entry
    # sha map (metadata short of a full rung, independent of whether
    # every npz FILE happens to still be present) must refuse.
    root = _synthetic_reference_tree_leads(tmp_path)
    traj = "pythia_2.8b"
    d = battery_4.reference_dir(root, f"endpoint_{traj}")
    rec_path = d / "_load.json"
    rec = json.loads(rec_path.read_text())
    first_rung = next(iter(rec["sets_sha256"]))
    del rec["sets_sha256"][first_rung]
    rec_path.write_text(json.dumps(rec, indent=1))
    with pytest.raises(ValueError, match="sets_sha256"):
        an._load_one_unit_4(root, f"endpoint_{traj}")


# ------------------------------------------------------------- C-1: gate 0

@pytest.mark.slow
def test_gate0_4_passes_on_a_synthetic_leads_reference_tree(tmp_path):
    root = _synthetic_reference_tree_leads(tmp_path)
    stage_keys = list(battery_4.STAGE1_KEYS_4) + list(battery_4.STAGE1_FIRST_UNITS_4)
    stage_tables = an.load_stage_tables_4(root, keys=stage_keys)
    for traj in battery_4.TRAJECTORIES_4:
        refs = battery_4.REFS_FOR_4[traj]
        ref_tables = {ref: rt["sets"] for ref, rt in
                     collect_4.load_ref_tables_4(root, refs).items()}
        g0 = an.gate0_4(root, traj, ref_tables, stage_tables)
        assert g0["pass"] is True, (traj, g0)
        assert g0["fraction_below"] >= an.GATE0_MIN_FRACTION_4
        n_sites = len(metric_4.sites_4(battery_4.N_HIDDEN_PIN_4[traj]))
        n_refs = len(battery_4.REFS_FOR_4[traj])
        # Task 5 finding 1: cells are per (rung, site, REFERENCE), not
        # averaged over references first -- n_cells scales by n_refs.
        assert g0["n_cells"] == len(battery_4.RUNGS) * n_sites * n_refs
        assert set(g0["per_reference"]) == set(refs)
        for ref in refs:
            assert g0["per_reference"][ref]["n_cells"] == len(battery_4.RUNGS) * n_sites
            assert 0.0 <= g0["per_reference"][ref]["fraction_below"] <= 1.0
        total_below = sum(round(g0["per_reference"][r]["fraction_below"]
                                * g0["per_reference"][r]["n_cells"]) for r in refs)
        assert total_below == pytest.approx(g0["fraction_below"] * g0["n_cells"], abs=1e-6)


def test_gate0_4_fails_when_twin_equals_endpoint():
    # A hand-built pair of tables where the twin's sets are IDENTICAL
    # to the endpoint's -- fraction_below must be exactly 0 (never
    # strictly below), well under GATE0_MIN_FRACTION_4.
    traj = "pythia_2.8b"
    sets_m, sets_q, pairing = _two_site_pair()
    unit = {"sets": {r: sets_m for r in battery_4.RUNGS}, "record": {"pairing": {"refX": pairing}}}
    stage_tables = {battery_4.INIT_KEY_4[traj]: unit, f"endpoint_{traj}": unit}
    ref_tables = {"refX": {r: sets_q for r in battery_4.RUNGS}}
    g0 = an.gate0_4(None, traj, ref_tables, stage_tables)
    assert g0["pass"] is False
    assert g0["fraction_below"] == pytest.approx(0.0)
    assert g0["per_reference"]["refX"]["fraction_below"] == pytest.approx(0.0)


def test_gate0_4_passes_when_twin_strictly_below_everywhere():
    traj = "pythia_2.8b"
    sets_m, sets_q, pairing = _two_site_pair()
    # the twin's overlap with the reference must be LOWER everywhere
    # than the endpoint's -- an empty (all-zero-overlap) twin against
    # a reference that fully agrees with the endpoint.
    twin_sets = np.array([[[10, 11], [11, 12], [12, 13]], [[13, 10], [10, 11], [11, 12]]],
                         dtype=np.uint16)   # disjoint from sets_q's 0..3 range -> 0 overlap
    twin = {"sets": {r: twin_sets for r in battery_4.RUNGS}, "record": {"pairing": {"refX": pairing}}}
    endpoint = {"sets": {r: sets_q for r in battery_4.RUNGS}, "record": {"pairing": {"refX": pairing}}}
    stage_tables = {battery_4.INIT_KEY_4[traj]: twin, f"endpoint_{traj}": endpoint}
    ref_tables = {"refX": {r: sets_q for r in battery_4.RUNGS}}
    g0 = an.gate0_4(None, traj, ref_tables, stage_tables)
    assert g0["pass"] is True
    assert g0["fraction_below"] == pytest.approx(1.0)
    assert g0["per_reference"]["refX"]["fraction_below"] == pytest.approx(1.0)


# ------------------------------------------------------------------- I-1

def test_gate1_failures_4_call_is_collected_not_raised_on_a_list_shape():
    bad = [1, 2, 3]
    val, f = an.collect_total_4(lambda: battery_4.gate1_failures_4(bad, traj="pythia_2.8b"),
                                "4 gate 1 pythia_2.8b failures check")
    assert val is None
    assert f and "4 gate 1 pythia_2.8b failures check" in f[0]


def test_check_power_matches_eligibility_4_call_is_collected_not_raised_on_a_scalar():
    # Review round 2 fix: this call was missing the now-required
    # `expected_n_sim` keyword-only argument (added in review round 1,
    # IMPORTANT 3), so the test was passing for the WRONG reason -- a
    # `TypeError: missing 1 required keyword-only argument`, not the
    # intended "power record is a scalar, not a dict" exception.
    # Verified directly before this fix: `f[0]` read "...TypeError:
    # _check_power_matches_eligibility_4() missing 1 required
    # keyword-only argument: 'expected_n_sim'".
    val, f = an.collect_total_4(
        lambda: an._check_power_matches_eligibility_4(42, {}, "deadbeef" * 8, expected_n_sim=10),
        "4 power vs eligibility check")
    assert val is None
    assert f and "4 power vs eligibility check" in f[0]
    assert "expected_n_sim" not in f[0]


def test_check_imports_4_and_check_referents_pass_on_the_committed_tree():
    # Review round 2, NEW A: both frozen-code pins must be self-
    # consistent against the committed tree -- a future edit to any
    # pinned file (power_4.py, make_referents_4.py, preflight_4.py,
    # verify_referents_4.py, or anything in FROZEN_SHA256_4) without a
    # matching re-pin now fails the fast suite immediately, rather than
    # drifting silently until a real-tree `analyze_4.run()` execution
    # surfaces it. `check_imports_4()`'s drift check runs over every
    # `IMPORTED_SHA256_4` entry unconditionally (independent of what
    # this process has actually imported); its "unpinned module" check
    # only examines modules already in `sys.modules`, which a plain
    # analyze_4-only test context won't have pulled in.
    from experiments.exp4 import make_referents_4 as mkr
    an.check_imports_4()   # raises on any drift or unpinned module
    bad = mkr.check_referents(an.REFERENTS_PATH_4, sha_pin=an.REFERENTS_4_SHA256)
    assert bad == []


def test_verdict_4_does_not_crash_on_a_malformed_eligibility_shape():
    # I-1: the earlier comparison already recorded a failure (as it
    # would in run()); a malformed (list, not dict) eligibility object
    # reaching verdict_4's packaging step must not THROW that verdict
    # away -- the tree's INSUFFICIENT_DATA (decided upstream) stands,
    # and the summary step's own failure is merely appended.
    tree = {"verdict": "INSUFFICIENT_DATA", "reason": "4 eligibility record disagrees: [...]"}
    v = an.verdict_4(failures=["4 eligibility record disagrees: [...]"], tree=tree, primary=None,
                     cells=[], eligibility=[1, 2, 3], rung_sets_by_traj=None, gate1_records={},
                     secondaries=None, sensitivities=None, pins_active={}, n_boot=10)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["eligibility_summary"] is None
    assert any("eligibility summary" in f for f in v["referents"]["failures"])


# ------------------------------------------------------------------- I-2

def test_s2_per_trajectory_4_uses_two_point_excess_not_raw_alignment():
    # Built so the OLD (buggy, pre-fix) predictor -- a_r(t2) -
    # trend(t2) alone, ignoring a_r(t1) -- would score every R rung's
    # RAW t2 value already above the flat pool's (AUC 1.0), while the
    # correct two-point excess x_r(t2) = (a_r(t2)-a_r(t1)) -
    # (trend(t2)-trend(t1)) exposes that r1's OWN rise (0.05) trails
    # the flat pool's rise (0.20) -- a real result the raw predictor
    # was blind to (excess AUC 0.5, not 1.0).
    r1, r2, f1, f2 = bt.RUNGS[0], bt.RUNGS[1], bt.RUNGS[2], bt.RUNGS[3]
    # s2_per_trajectory_4 indexes series["a"][r] for every r in
    # bt.RUNGS (all 34 real rungs), so every rung needs an entry --
    # give the untouched 30 the same flat baseline as f1/f2.
    a = {r: [0.10, 0.30] for r in bt.RUNGS}
    a[r1] = [0.90, 0.95]
    a[r2] = [0.05, 0.40]
    rung_sets_by_traj = {"t": {"R": [r1, r2], "flat": [f1, f2]}}
    series_by_traj = {"t": {"steps": [0, 1], "a": a}}
    out = an.s2_per_trajectory_4(series_by_traj, rung_sets_by_traj)
    assert out["t"]["source"] == "re-derived" and out["t"]["no_alpha_claim"] is True
    # the raw (pre-fix) predictor: every R rung already above the flat
    # pool's t2 value (trend_t2 = 0.30) -- a raw-AUC of 1.0
    trend_t2 = 0.30
    raw_x = {"r1": 0.95 - trend_t2, "r2": 0.40 - trend_t2, "f1": 0.0, "f2": 0.0}
    assert raw_x["r1"] > 0 and raw_x["r2"] > 0
    assert out["t"]["auc"] == pytest.approx(0.5)
    assert out["t"]["auc"] != pytest.approx(1.0)


# ------------------------------------------------------------------- I-3

def test_s4_size_axis_4_is_the_six_point_outcome_axis(monkeypatch):
    # I-3: sizes must be {70m,410m,1b,2.8b,6.9b,12b} -- 160m/1.4b
    # excluded -- so a rung whose first clear is at 410m (axis index
    # 1) is excluded by MIN_CLEAR_INDEX_4, and a rung whose first
    # clear is at 2.8b (axis index 3) reads t_minus = "1b" (index 2).
    v2d = json.loads((an.a2d.EXP2D / "results" / "verdict.json").read_bytes())
    rising_2d = [r for r in bt.RUNGS if v2d["per_rung"][r]["rising"]]
    assert len(rising_2d) >= 2, "need at least two rising rungs from the committed 2d verdict"
    r_early, r_mid = rising_2d[0], rising_2d[1]

    def fake_argmax(root_2d, size, rung):
        if rung == r_early and size == "410m":
            return 500
        if rung == r_mid and size in ("410m", "1b"):
            return 0
        return 0

    def fake_m4(size, rung):
        if rung == r_mid and size == "2.8b":
            return 500
        return 0

    monkeypatch.setattr(an, "_argmax_correct_4", fake_argmax)
    monkeypatch.setattr(an, "_m4_count_4", fake_m4)

    flat_a_by_size = {s: 0.5 for s in battery_4.LADDER_SIZES_4}
    rising_a_by_size = dict(flat_a_by_size, **{"2.8b": 0.7, "6.9b": 0.8, "12b": 0.9})
    per_rung = {}
    for r in bt.RUNGS:
        per_rung[r] = {"a_by_size": dict(rising_a_by_size if r == r_mid else flat_a_by_size)}
    s3_result = {"per_rung": per_rung}

    out = an.s4_size_axis_4(s3_result)
    assert out["sizes"] == list(an.AXIS_SIZES_4)
    assert "160m" not in out["sizes"] and "1.4b" not in out["sizes"]
    assert out["source"] == "re-derived"

    pr = out["per_rung"]
    assert pr[r_early]["first_clear_size"] == "410m"
    assert pr[r_early]["t_clear_index"] == 1
    assert pr[r_early]["phi"] is None      # excluded: index 1 < MIN_CLEAR_INDEX_4 (2)

    assert pr[r_mid]["first_clear_size"] == "2.8b"
    assert pr[r_mid]["t_clear_index"] == 3
    assert list(an.AXIS_SIZES_4)[pr[r_mid]["t_clear_index"] - 1] == "1b"
    assert pr[r_mid]["phi"] is not None
