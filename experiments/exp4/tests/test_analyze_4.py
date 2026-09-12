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


# --------------------------------------------- freeze closures (F-2, F-5)

def test_expected_pairing_4_matches_the_producers_own_re_derivation():
    """FREEZE F-2: the analyzer's re-derivation must be the producer's
    own function on the pinned site families, for every real
    (trajectory-or-key, reference) shape — otherwise the new refusal
    would fire on honest records."""
    for key in list(battery_4.STAGE1_KEYS_4) + [u for u in battery_4.STAGE1_FIRST_UNITS_4]:
        exp = an._expected_fields_4(key)
        got = an.expected_pairing_4(exp["n_hidden"], exp["refs"])
        assert sorted(got) == sorted(exp["refs"])
        sites_m = metric_4.sites_4(exp["n_hidden"])
        for ref in exp["refs"]:
            n_q = battery_4.N_HIDDEN_PIN_4[ref]
            want = collect_4._pairing_positions(sites_m, exp["n_hidden"], metric_4.sites_4(n_q), n_q)
            assert got[ref] == [int(j) for j in want]
            assert len(got[ref]) == len(sites_m)
            assert all(0 <= j < len(metric_4.sites_4(n_q)) for j in got[ref])


def test_expected_pairing_4_on_the_real_33_to_37_shape_is_not_the_identity():
    """The 12-site to 13-site pairing (Pythia/OLMo/Comma against
    SmolLM3 or Pythia-12b) is the only non-identity one on the real
    shapes; it is what a dropped or rotated pairing would corrupt."""
    p = an.expected_pairing_4(33, ("ref_smollm3_3b",))["ref_smollm3_3b"]
    assert p == [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12]
    assert an.expected_pairing_4(33, ("ref_olmo2_7b",))["ref_olmo2_7b"] == list(range(12))


def _write_sets_tree(root, key, arrays):
    d = battery_4.reference_dir(root, key) / "sets"
    d.mkdir(parents=True, exist_ok=True)
    for rung in battery_4.RUNGS:
        np.savez_compressed(d / f"{rung}.npz", sets=arrays[rung])


def test_ladder_known_answer_4_equal_absent_and_unequal(tmp_path):
    """FREEZE F-5: design §7's known-answer check (the ladder's 2.8b
    `main` against the step143000 endpoint) was never built. It is
    DESCRIPTIVE, not gating."""
    rng = np.random.default_rng(0)
    a = {r: rng.integers(0, 500, size=(2, 4, 10), dtype=np.uint16) for r in battery_4.RUNGS}
    assert an.ladder_known_answer_4(tmp_path)["available"] is False
    _write_sets_tree(tmp_path, "ladder_pythia_2.8b", a)
    assert an.ladder_known_answer_4(tmp_path)["available"] is False    # one side only
    _write_sets_tree(tmp_path, "endpoint_pythia_2.8b", a)
    eq = an.ladder_known_answer_4(tmp_path)
    assert eq["available"] and eq["equal"] and eq["gating"] is False
    assert eq["n_equal"] == eq["n_rungs"] == len(battery_4.RUNGS)
    b = dict(a)
    b[battery_4.RUNGS[0]] = (a[battery_4.RUNGS[0]].astype(np.int64) + 1).astype(np.uint16)
    _write_sets_tree(tmp_path, "endpoint_pythia_2.8b", b)
    ne = an.ladder_known_answer_4(tmp_path)
    assert ne["available"] and ne["equal"] is False and ne["gating"] is False
    assert ne["n_equal"] == len(battery_4.RUNGS) - 1
    assert ne["per_rung"][battery_4.RUNGS[0]] is False


# ============================================================ freeze F-7
# The freeze's full mutation re-sweep (`mutation_freeze_full.log`) found
# sixteen static mutants surviving the fast suite and twenty-four
# totality mutants surviving the totality suite, against a build ledger
# claiming 106/108 killed. The structural reason: NO fast-suite test
# calls `analyze_4.run()`, so the fast pass the build credits with
# killing the `collect_total_4` wrapper mutants could not have observed
# them; and the sixteen static survivors are preregistered dials and
# verdict-path rules whose only covering tests live in the 100-minute
# world suite, which no mutation pass has ever run. The tests below
# observe each survivor directly, in the fast suite.

def test_preregistered_bars_and_dials_are_at_their_design_values():
    """Every dial §3.6/§4 fixes, pinned as a literal. A post-tag edit to
    any of them — or a mutation of one — fails here immediately, which
    is what the mutation re-sweep found nothing else doing."""
    assert an.T_BAR_4 == 0.25              # §3.6: LEADS needs T >= .25
    assert an.ALPHA_4 == 0.01              # §3.6: the program's alpha
    assert an.MIN_CELLS_4 == 3             # §3.9: NO-CONVERGENCE below 3 cells
    assert an.MIN_RUNGS_4 == 3             # §3.9: ... or below 3 rungs
    assert an.SE_MULTIPLE_4 == 2.0         # §4 rule (ii): x_end >= 2 x SE
    assert an.MIN_CLEAR_INDEX_4 == 2       # §3.5: t_clear >= t_3
    assert an.GATE0_MIN_FRACTION_4 == 0.90  # §3.7 gate 0
    assert an.N_BOOT_4 == 10_000           # §3.6 CI95
    assert an.N_FLIP_SAMPLE_4 == 10_000    # §3.6, above the enumeration cap
    assert an.MAX_ENUMERATE_4 == 20        # §3.6: exact below this
    assert an.N_BOOT_ELIG_4 == 2000        # §4's item bootstrap
    assert an.POWER_BAR_4 == 0.75          # §4: P(LEADS | phi=.5) >= .75
    assert an.POWER_PHIS_4 == (0.0, 0.25, 0.5)
    assert metric_4.K_4 == 10 and battery_4.DTYPE_4 == "float16"
    assert battery_4.PRIMARY_POSITION_4 == 1     # §3.1: the prompt end
    assert an.WORLDS_4 == ("INSUFFICIENT_DATA", "NO-CONVERGENCE", "LEADS",
                           "PARTIAL", "FOLLOWS", "UNDETERMINED")


def test_verdict_tree_4_decides_at_the_exact_bars():
    """The tie cases §3.9's wording fixes, each one bar-width from its
    neighbour — a lowered T_BAR_4 or a raised ALPHA_4 flips one."""
    b = {"T": 0.3, "p_plus": 0.004, "p_minus": 1.0, "ci95": [0.1, 0.5]}
    # T exactly at the bar with p under alpha: LEADS.
    assert an.verdict_tree_4([], 5, 4, dict(b, T=0.25))["verdict"] == "LEADS"
    # T just under the bar: PARTIAL, not LEADS (kills T_BAR_4 -> .2).
    assert an.verdict_tree_4([], 5, 4, dict(b, T=0.22))["verdict"] == "PARTIAL"
    assert an.verdict_tree_4([], 5, 4, dict(b, T=0.21))["verdict"] == "PARTIAL"
    # p exactly at alpha is NOT significant (strict <) ...
    assert an.verdict_tree_4([], 5, 4, dict(b, p_plus=0.01))["verdict"] == "UNDETERMINED"
    # ... and p between .01 and .05 must not fire either (kills ALPHA_4 -> .05).
    assert an.verdict_tree_4([], 5, 4, dict(b, p_plus=0.02))["verdict"] == "UNDETERMINED"
    assert an.verdict_tree_4([], 5, 4, dict(b, T=0.15, p_plus=0.02,
                                            ci95=[0.05, 0.24]))["verdict"] == "FOLLOWS"
    # CI95 upper exactly at the bar is NOT excluded (strict <).
    assert an.verdict_tree_4([], 5, 4, dict(b, T=0.02, p_plus=0.4,
                                            ci95=[-0.05, 0.25]))["verdict"] == "UNDETERMINED"
    # the cell/rung floors (kills MIN_CELLS_4 -> 1)
    assert an.verdict_tree_4([], 2, 4, b)["verdict"] == "NO-CONVERGENCE"
    assert an.verdict_tree_4([], 3, 3, b)["verdict"] == "LEADS"


def _series_for_cells(steps, a_by_rung):
    return {"steps": list(steps), "a": {r: list(v) for r, v in a_by_rung.items()}}


def test_cells_4_uses_the_flat_pool_as_the_trend_not_r():
    """§3.5: the excess nets out the FLAT rungs' growth. A trend taken
    over R instead would subtract the rising rungs' own growth and
    collapse phi — built so the two readings differ by construction."""
    steps = [10, 20, 30, 40]
    a = {"rise": [0.02, 0.04, 0.05, 0.06],     # rises early
         "other": [0.02, 0.04, 0.05, 0.06],    # a second R rung, same shape
         "flat1": [0.02, 0.02, 0.02, 0.02],    # the flat pool: no growth at all
         "flat2": [0.02, 0.02, 0.02, 0.02]}
    rs = {"R": ["rise", "other"], "flat": ["flat1", "flat2"], "transient": [],
          "t_clear": {"rise": 30, "other": 30}, "clears_and_stays": {}, "endpoint_step": 40}
    elig = {"t": {"R": {"rise": {"eligible": True, "t_clear": 30, "t_clear_index": 2},
                        "other": {"eligible": True, "t_clear": 30, "t_clear_index": 2}}}}
    cells = an.cells_4({"t": _series_for_cells(steps, a)}, {"t": rs}, elig)
    assert len(cells) == 2
    # flat pool flat => excess == the rung's own growth => phi = .02/.04 = .5
    assert cells[0]["phi"] == pytest.approx(0.5)
    # a trend over R would be the mean of the two identical rising rungs,
    # leaving an excess of exactly 0 at every step and no cell at all.
    trend_over_R = an.trend_4(a, rs["R"], steps)
    assert an.excess_4(a, trend_over_R, steps)["rise"] == [0.0, 0.0, 0.0, 0.0]


def test_every_exp4_entry_point_pins_the_blas_threads_before_numpy():
    """Final review Minor 7. The BLAS thread pool is sized when the
    library is first loaded, so `_threads_4` has to be imported before
    numpy AND before every `experiments.*` import that pulls numpy in
    transitively. Structural, by AST on the source, because by the time
    a test runs, pytest's own conftest has long since imported numpy
    and the runtime order cannot be observed from inside."""
    import ast
    import os
    from experiments.exp4 import _threads_4

    assert _threads_4.threads_pinned_4() is True
    for v in _threads_4.THREAD_ENV_4:
        assert os.environ[v] == "1", v
    assert _threads_4.thread_pin_record_4()["threads_pinned"] is True

    for rel in ("analyze_4.py", "run/reference_4.py", "run/sweep_4.py", "run/preflight_4.py"):
        src = (an.EXP4 / rel).read_text()
        tree = ast.parse(src)
        threads_line, numpy_lines, other_exp_lines = None, [], []
        for node in ast.walk(tree):
            is_threads = (isinstance(node, ast.ImportFrom) and node.module == "experiments.exp4"
                          and any(a.name == "_threads_4" for a in node.names))
            if is_threads:
                threads_line = node.lineno
            elif isinstance(node, ast.Import) and any(a.name == "numpy" for a in node.names):
                numpy_lines.append(node.lineno)
            elif isinstance(node, ast.ImportFrom) and (node.module or "").startswith("experiments."):
                other_exp_lines.append(node.lineno)
        assert threads_line is not None, f"{rel} does not import _threads_4"
        for ln in numpy_lines:
            assert threads_line < ln, f"{rel}: numpy imported at line {ln}, before the pin"
        assert threads_line < min(other_exp_lines), rel


def test_family_matched_trend_4_uses_only_the_flat_siblings_of_the_rungs_own_family():
    """§5's named sensitivity: the trend taken over the flat rungs of
    the cell's OWN 2c family. Built so the two readings differ by
    construction — `antonym6` (family `antonym`) has one flat sibling,
    `antonym`, whose growth is twice the pooled flat pool's, so the
    family-matched excess is strictly smaller than the pooled one; and
    `add_base8` (family `base_arith`) has NO flat sibling here, so it
    is printed with its reason and left out of T."""
    steps = [10, 20, 30, 40]
    a = {"antonym6": [0.10, 0.30, 0.35, 0.50],    # the eligible cell, family `antonym`
         "antonym": [0.10, 0.20, 0.25, 0.30],     # its ONE flat sibling
         "add_base8": [0.10, 0.30, 0.35, 0.50],   # eligible, family `base_arith`, no sibling
         "mod13": [0.10, 0.10, 0.15, 0.20],       # pooled-only flat rungs
         "mod17": [0.10, 0.10, 0.15, 0.20]}
    rs = {"R": ["antonym6", "add_base8"], "flat": ["antonym", "mod13", "mod17"],
          "transient": [], "t_clear": {"antonym6": 30, "add_base8": 30},
          "clears_and_stays": {}, "endpoint_step": 40}
    elig = {"t": {"R": {"antonym6": {"eligible": True, "t_clear": 30, "t_clear_index": 2},
                        "add_base8": {"eligible": True, "t_clear": 30, "t_clear_index": 2}}}}
    out = an.family_matched_trend_4({"t": _series_for_cells(steps, a)}, {"t": rs}, elig)

    cell = out["per_cell"]["t/antonym6"]
    assert cell["family"] == "antonym" and cell["siblings"] == ["antonym"]
    # family-matched: the rung grows .20 by t- (index 1, the last step
    # before t_clear at index 2) and .40 by t_end; the sibling grows
    # .10 / .20 -> excess .10 / .20 -> phi .5
    assert cell["phi_family_matched"] == pytest.approx(0.5)
    # pooled: the flat pool's mean growth is (.10 + 0 + 0)/3 at t- and
    # (.20 + .10 + .10)/3 at t_end -> phi .625, a different reading
    assert cell["phi_pooled"] == pytest.approx(0.625)

    no_sib = out["per_cell"]["t/add_base8"]
    assert no_sib["n_siblings"] == 0 and no_sib["phi_family_matched"] is None
    assert "no flat sibling" in no_sib["reason"]
    assert no_sib["phi_pooled"] is not None

    # T is re-read over exactly the cells that HAVE a sibling
    assert out["n_cells"] == 1 and out["n_cells_without_a_sibling"] == 1
    assert out["T_family_matched"] == pytest.approx(0.5)
    assert out["no_alpha_claim"] is True and out["source"] == "re-derived"


def test_s11_per_reference_4_reads_each_reference_alone_and_names_the_leader():
    """S11's per-reference clause / §3.3's "per-reference values are
    printed in every world": one excess series per reference, a phi per
    (cell, reference), the leading reference per cell and the
    per-trajectory tally. Built so the three references disagree by
    construction — refA's excess arrives before the clear, refB's
    after, refC's not at all."""
    steps = [10, 20, 30, 40]
    flat = {"mod13": [0.10, 0.10, 0.10, 0.10], "mod17": [0.10, 0.10, 0.10, 0.10]}
    a_by_ref = {
        "refA": {"antonym6": [0.10, 0.18, 0.22, 0.30], **flat},   # early: phi ~ .4
        "refB": {"antonym6": [0.10, 0.11, 0.12, 0.30], **flat},   # late: phi ~ .1
        "refC": {"antonym6": [0.10, 0.10, 0.10, 0.10], **flat},   # nothing: x_end 0 -> None
    }
    pooled = {r: [float(np.mean([a_by_ref[ref][r][i] for ref in a_by_ref]))
                  for i in range(len(steps))] for r in ("antonym6", "mod13", "mod17")}
    series = {"t": {"steps": steps, "a": pooled, "per_item": {}, "a_by_ref": a_by_ref}}
    rs = {"R": ["antonym6"], "flat": ["mod13", "mod17"], "transient": [],
          "t_clear": {"antonym6": 30}, "clears_and_stays": {}, "endpoint_step": 40}
    elig = {"t": {"R": {"antonym6": {"eligible": True, "t_clear": 30, "t_clear_index": 2}}}}

    out = an.s11_per_reference_4(series, {"t": rs}, elig)
    block = out["per_traj"]["t"]
    assert block["available"] is True and block["references"] == ["refA", "refB", "refC"]
    cell = block["per_cell"]["antonym6"]
    # t- is index 1 (t_clear at index 2): refA's excess is .08 of .20,
    # refB's is .01 of .20
    assert cell["phi_by_ref"]["refA"] == pytest.approx(0.08 / 0.20)
    assert cell["phi_by_ref"]["refB"] == pytest.approx(0.01 / 0.20)
    assert cell["phi_by_ref"]["refC"] is None          # no endpoint excess at all
    assert cell["leading_reference"] == "refA"
    assert block["leads_tally"] == {"refA": 1, "refB": 0, "refC": 0}
    assert block["leads_most_often"] == "refA"
    assert out["no_alpha_claim"] is True

    # a tree with no per-reference series degrades, it does not raise
    bare = an.s11_per_reference_4({"t": {"steps": steps, "a": pooled, "per_item": {}}},
                                  {"t": rs}, elig)
    assert bare["per_traj"]["t"]["available"] is False


def test_alignment_parts_4_pooled_half_is_bit_identical_to_per_item_alignment_4():
    """The per-reference reading was factored INTO the pooled one so it
    costs no second overlap pass; the pooled half must be the same
    bits it was before the factor (it decides a_r(t), the excess, phi
    and T)."""
    rng = np.random.default_rng(0)
    n, k, n_sites = 40, metric_4.K_4, 3
    sets_m = {r: rng.integers(0, n, size=(n_sites, n, k), dtype=np.uint16)
              for r in battery_4.RUNGS}
    refs = {f"ref{i}": {r: rng.integers(0, n, size=(n_sites, n, k), dtype=np.uint16)
                        for r in battery_4.RUNGS} for i in range(3)}
    pairing = {ref: list(range(n_sites)) for ref in refs}
    tables = {"sets": sets_m, "overlaps": {}}
    pooled, per_ref = an._alignment_parts_4(tables, refs, pairing)
    direct = an.per_item_alignment_4(tables, refs, pairing)
    for r in battery_4.RUNGS:
        assert np.array_equal(pooled[r], direct[r])
        # and the pooled value IS the mean over the per-reference ones
        assert np.allclose(pooled[r], np.mean([per_ref[ref][r] for ref in refs], axis=0))


def test_lambda_hat_4_reads_the_flat_pools_scatter_over_its_bootstrap_se():
    """R-7(b): lambda_hat = the flat pool's between-step scatter (the
    SD over grid steps of each flat rung's own excess, pooled in
    quadrature) over the quadrature-pooled item-bootstrap SE the
    eligibility record carries. Built so the answer is arithmetic, not
    a fit: two flat rungs whose excesses are exact +-d square waves
    about zero, so each rung's own SD is known in closed form."""
    steps = [10, 20, 30, 40]
    # flat1/flat2 wobble in opposite directions, so the POOLED trend is
    # flat and each rung's excess is its own wobble exactly.
    a = {"rise": [0.10, 0.14, 0.18, 0.22],
         "flat1": [0.10, 0.12, 0.10, 0.12],
         "flat2": [0.10, 0.08, 0.10, 0.08]}
    rs = {"R": ["rise"], "flat": ["flat1", "flat2"], "transient": [],
          "t_clear": {"rise": 30}, "clears_and_stays": {}, "endpoint_step": 40}
    elig = {"t": {"R": {}, "flat": {"flat1": {"se_at_end": 0.01},
                                    "flat2": {"se_at_end": 0.01}}}}
    series = {"t": _series_for_cells(steps, a)}
    out = an.lambda_hat_4(series, {"t": rs}, elig)
    block = out["per_traj"]["t"]
    # flat1's excess is [0, .02, 0, .02]; flat2's is [0, -.02, 0, -.02]
    want_sd = float(np.std([0.0, 0.02, 0.0, 0.02], ddof=1))
    assert block["per_rung"]["flat1"]["scatter_sd"] == pytest.approx(want_sd)
    assert block["per_rung"]["flat2"]["scatter_sd"] == pytest.approx(want_sd)
    assert block["scatter_sd"] == pytest.approx(want_sd)      # quadrature over equal SDs
    assert block["bootstrap_se"] == pytest.approx(0.01)
    assert block["lambda_hat"] == pytest.approx(want_sd / 0.01)
    assert block["n_flat"] == 2 and block["n_flat_with_se"] == 2 and block["n_steps"] == 4
    assert out["no_alpha_claim"] is True and out["source"] == "re-derived"
    assert out["note"] == an.LAMBDA_HAT_NOTE_4


def test_lambda_hat_4_degrades_rather_than_raises_without_a_flat_pool():
    steps = [10, 20]
    rs = {"R": ["rise"], "flat": [], "transient": [], "t_clear": {}, "clears_and_stays": {},
          "endpoint_step": 20}
    out = an.lambda_hat_4({"t": _series_for_cells(steps, {"rise": [0.1, 0.2]})}, {"t": rs},
                          {"t": {"R": {}, "flat": {}}})
    assert out["per_traj"]["t"]["lambda_hat"] is None
    # a trajectory with no rung sets at all (a failed load) is the other
    # shape run() can hand it
    out2 = an.lambda_hat_4({"t": _series_for_cells(steps, {"rise": [0.1, 0.2]})}, {"t": None}, {})
    assert out2["per_traj"]["t"]["lambda_hat"] is None


def test_licence_condition_4_counts_qualifying_trajectories():
    """Minor 9 / design §6: LEADS on at least two of the four
    per-model readings, each at its own p < .05 and T >= .25."""
    def pt(T, p):
        return {"T": T, "p_plus": p, "n_cells": 3, "n_rungs": 3, "flip_method": "exact"}
    one = an.licence_condition_4({"per_traj": {"a": pt(0.4, 0.01), "b": pt(0.4, 0.20),
                                               "c": pt(0.1, 0.001), "d": pt(0.9, 0.049)}})
    assert one["trajectories"] == ["a", "d"] and one["n_qualifying"] == 2
    assert one["met"] is True and one["descriptive"] is True
    # exactly at the bars: T == .25 qualifies (>=), p == .05 does not (<)
    edge = an.licence_condition_4({"per_traj": {"a": pt(an.T_BAR_4, 0.049),
                                                "b": pt(0.9, an.LICENCE_TRAJ_ALPHA_4)}})
    assert edge["trajectories"] == ["a"] and edge["met"] is False
    assert an.licence_condition_4(None)["met"] is False
    assert an.licence_condition_4({})["n_trajectories_read"] == 0


def test_primary_4_bootstrap_resamples_whole_rungs_not_cells():
    """§3.6's CI95 is a RUNG-clustered bootstrap: a rung carrying four
    cells enters or leaves as a block. Built so cell-level resampling
    cannot reproduce the interval — one 4-cell rung at .9 against three
    1-cell rungs at .1, where rung clustering must put real mass on
    .9-heavy and .1-only draws."""
    cells = ([{"traj": "t", "rung": "hot", "phi": 0.9} for _ in range(4)]
             + [{"traj": "t", "rung": f"c{i}", "phi": 0.1} for i in range(3)])
    p = an.primary_4(cells, n_boot=2000, seed=0)
    assert p["n_cells"] == 7 and p["n_rungs"] == 4
    lo, hi = p["ci95"]
    # Drawing four "cold" rungs (p = (3/4)^4 = 31.6 %, far above 2.5 %)
    # puts the lower bound at exactly .1; three hot picks of four puts
    # the upper at (12*.9 + .1)/13 = .8385. Cell-level resampling of the
    # same 7 cells concentrates near the mean (.557) and reads
    # [.214, .786] — it can reach NEITHER of these bounds.
    assert lo == pytest.approx(0.1), p["ci95"]
    assert hi == pytest.approx(0.8384615384615386), p["ci95"]


def test_flip_signs_values_are_exactly_plus_minus_one():
    """§3.6's null flips a rung's sign — +-1, nothing else, and the
    enumeration is complete below the cap."""
    S, method = an._flip_signs(4, seed=0)
    assert method == "exact" and S.shape == (16, 4)
    assert set(np.unique(S).tolist()) == {-1, 1}
    assert S.sum() == 0                     # every sign pattern once
    assert len({tuple(r) for r in S.tolist()}) == 16
    S2, m2 = an._flip_signs(an.MAX_ENUMERATE_4 + 1, seed=0)
    assert m2 == "sampled" and set(np.unique(S2).tolist()) == {-1, 1}


def test_compare_eligibility_4_resolves_drift_far_below_a_tenth():
    """The committed eligibility record is compared to its own
    re-derivation at 1e-12 — a tolerance of 1e-1 would accept a table
    that disagrees about every excess."""
    a = {"t": {"R": {"r": {"x_end": 0.30000000000, "se": 0.01}}}}
    b = {"t": {"R": {"r": {"x_end": 0.30000000001, "se": 0.01}}}}
    assert an._compare_eligibility_4(a, b) != []
    c = {"t": {"R": {"r": {"x_end": 0.35, "se": 0.01}}}}
    assert an._compare_eligibility_4(a, c) != []
    assert an._compare_eligibility_4(a, a) == []


def test_eligibility_summary_4_counts_only_the_eligible_rungs():
    elig = {"t": {"R": {"a": {"eligible": True}, "b": {"eligible": False},
                        "c": {"eligible": True}},
                  "flat": {"f1": {}, "f2": {}}, "transient": ["x"]}}
    s = an._eligibility_summary_4(elig)["t"]
    assert s == {"n_R": 3, "n_eligible": 2, "n_flat": 2, "n_transient": 1}


def test_gate0_4_bar_is_inclusive_at_exactly_the_fraction():
    """§3.7: gate 0 passes at `fraction_below >= .90`. Built to land on
    exactly .90 — 153 of 170 cells below — so `>` and `>=` disagree."""
    traj = "pythia_2.8b"
    n_sites, n, k = 5, 10, 3
    rungs = list(battery_4.RUNGS)              # 34 rungs x 5 sites x 1 ref = 170 cells
    ref = np.tile(np.arange(k, dtype=np.uint16), (n_sites, n, 1))
    endpoint_sets = ref.copy()                 # full overlap everywhere
    low = np.tile(np.arange(k, dtype=np.uint16) + 50, (n_sites, n, 1))   # zero overlap
    pairing = list(range(n_sites))
    # 17 of the 170 (rung, site) cells must NOT be below: give three
    # rungs' first five sites, and two sites of a fourth rung, full
    # overlap in the twin too (3*5 + 2 = 17).
    twin = {}
    for i, r in enumerate(rungs):
        if i < 3:
            twin[r] = endpoint_sets.copy()
        elif i == 3:
            t = low.copy(); t[:2] = ref[:2]
            twin[r] = t
        else:
            twin[r] = low
    stage_tables = {
        battery_4.INIT_KEY_4[traj]: {"sets": twin, "record": {"pairing": {"refX": pairing}}},
        f"endpoint_{traj}": {"sets": {r: endpoint_sets for r in rungs},
                             "record": {"pairing": {"refX": pairing}}},
    }
    ref_tables = {"refX": {r: ref for r in rungs}}
    g0 = an.gate0_4(None, traj, ref_tables, stage_tables)
    assert g0["n_cells"] == 170
    assert g0["fraction_below"] == pytest.approx(0.90)
    assert g0["pass"] is True          # >= , not > : exactly at the bar passes


def test_s2_known_answer_gates_4_refuses_a_perturbed_auc(tmp_path, monkeypatch):
    """The 2d/2e AUC known-answer gate is exact to 1e-12. A tolerance of
    1e-1 would accept a reproduction that is wrong in the second
    decimal — built by perturbing a committed predictor score."""
    import shutil
    from experiments.exp2d import analyze_2d as a2d
    real_2d, real_2e = a2d.EXP2D, an.EXPERIMENTS / "exp2e"
    for src, name in ((real_2d, "exp2d"), (real_2e, "exp2e")):
        (tmp_path / name / "results").mkdir(parents=True)
        shutil.copy2(src / "results" / "verdict.json", tmp_path / name / "results" / "verdict.json")
    monkeypatch.setattr(a2d, "EXP2D", tmp_path / "exp2d")
    monkeypatch.setattr(an, "EXPERIMENTS", tmp_path)
    assert an.s2_known_answer_gates_4()["auc_2d"] == pytest.approx(0.5454545454545454, abs=1e-15)

    p = tmp_path / "exp2d" / "results" / "verdict.json"
    obj = json.loads(p.read_text())
    r0 = sorted(obj["per_rung"])[0]
    obj["per_rung"][r0]["predictor_score"] = 1e9      # reorders the AUC's ranking
    p.write_text(json.dumps(obj))
    with pytest.raises(ValueError, match="2d's AUC"):
        an.s2_known_answer_gates_4()

    shutil.copy2(real_2d / "results" / "verdict.json", p)
    q = tmp_path / "exp2e" / "results" / "verdict.json"
    obj = json.loads(q.read_text())
    r0 = sorted(obj["per_rung"])[0]
    obj["per_rung"][r0]["F1"] = 1e9
    q.write_text(json.dumps(obj))
    with pytest.raises(ValueError, match="2e's AUC"):
        an.s2_known_answer_gates_4()


def test_s1_order_4_reports_concordance_not_discordance():
    """S1's Somers' D is concordant MINUS discordant: a rung that agrees
    earlier and clears earlier is a POSITIVE contribution."""
    steps = [10, 20, 30, 40]
    a = {"early": [0.02, 0.06, 0.06, 0.06],    # half-rises at index 1
         "late": [0.02, 0.02, 0.02, 0.06],     # half-rises at index 3
         "flat1": [0.02, 0.02, 0.02, 0.02],
         "flat2": [0.02, 0.02, 0.02, 0.02]}
    rs = {"R": ["early", "late"], "flat": ["flat1", "flat2"], "transient": [],
          "t_clear": {"early": 20, "late": 40}, "clears_and_stays": {}, "endpoint_step": 40}
    out = an.s1_order_4({"t": _series_for_cells(steps, a)}, {"t": rs})
    assert out["pooled_d"] == pytest.approx(1.0), out
    per = out["per_traj"]["t"]
    assert per["n_concordant"] == 1 and per["n_discordant"] == 0 and per["d"] == 1.0


def test_every_collect_total_4_refusal_label_is_present():
    """FREEZE F-7's general closure. Every `collect_total_4(thunk,
    label)` site in `analyze_4.py` is a refusal the analyzer must
    COLLECT rather than raise (2d F-1 / 2h F-1's lesson); the mutation
    harness generates one mutant per site by stripping the wrapper, and
    NO fast test could observe any of them because no fast test calls
    `run()`. The refusal surface is pinned here by its own label set,
    read from the source by AST: stripping a wrapper removes its label
    and fails this test in milliseconds."""
    import ast
    src = (an.EXP4 / "analyze_4.py").read_text()
    labels = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "collect_total_4":
            assert len(node.args) >= 2, "every collect_total_4 call carries a label"
            labels.append(ast.get_source_segment(src, node.args[1]))
    assert sorted(labels) == sorted(COLLECT_TOTAL_LABELS_4), (
        f"the refusal surface changed: added {sorted(set(labels) - set(COLLECT_TOTAL_LABELS_4))}, "
        f"removed {sorted(set(COLLECT_TOTAL_LABELS_4) - set(labels))}")
    assert len(labels) == len(set(labels)) == 33
    for lab in labels:
        assert lab.startswith('"4 ') or lab.startswith('f"4 '), lab


COLLECT_TOTAL_LABELS_4 = [
    '"4 battery items"', '"4 cells"', '"4 checkpoint manifests"',
    '"4 eligibility re-derivation"', '"4 eligibility record"', '"4 eligibility summary"',
    '"4 floors 2d"', '"4 frozen modules"', '"4 halt marker read"',
    '"4 import surface (entry)"', '"4 import surface (exit)"',
    '"4 ladder known-answer (descriptive)"', '"4 lambda_hat"', '"4 licence condition"',
    '"4 power record"', '"4 power summary"',
    '"4 power vs eligibility check"', '"4 prereg tag"', '"4 primary"', '"4 reference seal"',
    '"4 referent manifest"', '"4 stage tables"',
    'f"4 alignment series {traj}"', 'f"4 gate 0 {traj} ref tables"', 'f"4 gate 0 {traj}"',
    'f"4 gate 1 {traj} failures check"', 'f"4 gate 1 {traj} re-derivation"',
    'f"4 gate 1 {traj} record"', 'f"4 outcome {traj}"', 'f"4 ref tables {traj}"',
    'f"4 rung sets {traj}"', 'f"4 sweep tables {traj}"', 'f"4 {name}"',
]


def test_run_requires_all_four_gate1_agreements():
    """I-6's fix, pinned. `gate1_rederive_4` computes four independent
    agreements — the committed prompt-end set bytes per rung, the two
    records' per-rung `activation_sha256`, their per-rung
    `attested_sha256` (design §3.7: identity on every (rung, site,
    position), which is what covers the question-end and pooled
    tables), and the two `tensor_digest`s — and `run()` must require ALL
    FOUR. Dropping one is a mutation only the 100-minute world route
    `gate1_sweep_endpoint_edited` can observe behaviourally, so the
    requirement is pinned structurally here: the condition that raises
    "re-derived bytes disagree" must name every one of them."""
    import ast
    src = (an.EXP4 / "analyze_4.py").read_text()
    needle = "re-derived bytes disagree"
    found = []
    for node in ast.walk(ast.parse(src)):
        # the INNERMOST branch: one statement, and it is the append
        # itself (ast.walk also reaches the enclosing `if not failures:`
        # and the `for` body's own `if`, whose source contains the
        # needle transitively).
        if not isinstance(node, ast.If) or len(node.body) != 1 \
                or not isinstance(node.body[0], ast.Expr):
            continue
        body_src = ast.get_source_segment(src, node.body[0]) or ""
        if needle in body_src and "failures.append" in body_src:
            found.append(ast.get_source_segment(src, node.test))
    assert len(found) == 1, f"expected exactly one gate-1 disagreement branch, got {len(found)}"
    cond = found[0]
    for key in ("sets_equal", "activation_sha_equal", "attested_sha_equal", "digest_equal"):
        assert key in cond, f"run()'s gate-1 condition does not require {key}: {cond}"
    assert cond.count("all(") == 3          # the three per-rung dicts, each fully quantified
