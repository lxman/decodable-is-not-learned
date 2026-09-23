# experiments/exp5/tests/test_analyze_5.py  (fast: the pure pieces)
import json
import math

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp5 import analyze_5 as an
from experiments.exp5 import battery_5 as b5


def test_collect_total_5_prefix_named_types_and_crash_on_logic_defect():
    v, f = an.collect_total_5(lambda: (_ for _ in ()).throw(OSError("x")), "5 x")
    assert v is None and f == ["5 x: OSError: x"]
    v, f = an.collect_total_5(lambda: 3, "5 y")
    assert v == 3 and f == []
    with pytest.raises(ZeroDivisionError):          # a logic defect is never laundered
        an.collect_total_5(lambda: 1 / 0, "5 z")
    with pytest.raises(ValueError, match="prefix"):
        an.collect_total_5(lambda: 3, "no prefix")


def test_gate1a_failures():
    good = {"digests_equal": True, "continuation_diffs": {r: 0 for r in b5.RUNGS},
            "continuations_compared": {r: 500 for r in b5.RUNGS}, "loss_equal": True,
            "prereg_tag": b5.PREREG_TAG_5, "pass": True,
            # freeze F-2: the measured fields the flags are re-derived from
            "digest_2c_path": "d" * 64, "digest_candidate_path": "d" * 64,
            "loss_2c_path": 2.5, "loss_candidate_path": 2.5, "per_doc_diffs": 0}
    assert an.gate1a_failures_5(good) == []
    assert an.gate1a_failures_5({**good, "digests_equal": False})
    assert an.gate1a_failures_5({**good, "continuations_compared": {**good["continuations_compared"], "mod13": 499}})
    assert an.gate1a_failures_5({**good, "loss_equal": False})


def test_gate1a_flags_are_re_derived_not_attested():
    """Freeze F-2: digests_equal / loss_equal are the runner's attestations;
    the record carries what they were computed from and the analyzer
    re-derives them, and ties the candidate path to the 2.8b final unit."""
    good = {"digests_equal": True, "continuation_diffs": {r: 0 for r in b5.RUNGS},
            "continuations_compared": {r: 500 for r in b5.RUNGS}, "loss_equal": True,
            "prereg_tag": b5.PREREG_TAG_5, "pass": True,
            "digest_2c_path": "d" * 64, "digest_candidate_path": "d" * 64,
            "loss_2c_path": 2.5, "loss_candidate_path": 2.5, "per_doc_diffs": 0,
            "counts_2c_path": {r: 7 for r in b5.RUNGS}}
    assert an.gate1a_failures_5(good) == []
    assert an.gate1a_failures_5({**good, "digest_2c_path": "e" * 64})
    assert an.gate1a_failures_5({**good, "loss_2c_path": 2.5 + 1e-12})
    assert an.gate1a_failures_5({**good, "per_doc_diffs": 1})
    assert an.gate1a_failures_5({**good, "per_doc_diffs": None})
    unit = {"digest": "d" * 64, "loss": 2.5, "counts": {r: 7 for r in b5.RUNGS}}
    assert an.gate1a_unit_failures_5(good, unit) == []
    assert an.gate1a_unit_failures_5(good, {**unit, "loss": 2.5 + 1e-12})
    assert an.gate1a_unit_failures_5(good, {**unit, "digest": "f" * 64})
    assert an.gate1a_unit_failures_5(good, {**unit, "counts": {**unit["counts"], "antonym": 8}})


def test_licence_block_cells():
    for world, mod in (("MATCHED", None), ("NOT-MATCHED", "LARGE-AHEAD"), ("NOT-MATCHED", "SMALL-AHEAD"),
                       ("NOT-MATCHED", "MIXED"), ("NOT-MATCHED", "THIN"), ("UNDETERMINED", None),
                       ("INSUFFICIENT_DATA", None)):
        lic = an.licence_block_5(world, mod, {"declaration": "POWERED", "min_detectable_T": 0.01})
        assert lic["sentence"] and lic["caveat"].startswith("one family")
    under = an.licence_block_5("MATCHED", None, {"declaration": "DECLARED UNDERPOWERED IN ADVANCE",
                                                 "min_detectable_T": 0.02})
    assert "not distinguishable at this resolution" in under["sentence"]


def test_projection_failures():
    units = {"6.9b": {"git_shas": {1000: "u1", 2000: "u2"}, "whys": {1000: "spine", 2000: "bisect"}},
             "1b": {"git_shas": {143000: "f1"}, "whys": {143000: "final"}}}
    ok = an.projection_failures_5(units, projection_commit="p", is_ancestor=lambda a, b: True,
                                  seal_tag_commit="s")
    assert ok == []
    bad = an.projection_failures_5(units, projection_commit="p",
                                   is_ancestor=lambda a, b: not (a == "p" and b == "u2"),
                                   seal_tag_commit="s")
    assert any("6.9b/step2000" in f for f in bad)
    assert an.projection_failures_5(units, projection_commit=None, is_ancestor=lambda a, b: True,
                                    seal_tag_commit="s")
    # Task 6 mutation kill: the FINAL step is excluded from the ancestry
    # check (its unit is built in stage 1, before the projection is even
    # sealed) — an is_ancestor that fails specifically on the final's
    # own git_sha must still read clean.
    final_excluded = an.projection_failures_5(
        units, projection_commit="p", is_ancestor=lambda a, b: not (a == "p" and b == "f1"),
        seal_tag_commit="s")
    assert final_excluded == []


def test_power_failures_5_pins_n_sim_and_seed(monkeypatch):
    """Review finding 4: n_sim/seed provenance is MEASURED against
    power_5's own committed constants, not merely self-consistent —
    power_failures_5 is the whole of gate 5, so this is exercised
    directly rather than through run()."""
    from experiments.exp5 import power_5 as pw
    monkeypatch.setattr(pw, "finals_sha256_5", lambda root: "x" * 64)
    good = {"prereg_tag": b5.PREREG_TAG_5, "n_sim": pw.N_SIM_5, "seed": pw.SEED_5,
            "finals_sha256": "x" * 64, "declaration": "POWERED"}
    assert an.power_failures_5("root", good, None, None, power_gate="skip") == []
    bad_n = an.power_failures_5("root", {**good, "n_sim": pw.N_SIM_5 + 1}, None, None,
                                power_gate="skip")
    assert any("n_sim" in m for m in bad_n)
    bad_s = an.power_failures_5("root", {**good, "seed": pw.SEED_5 + 1}, None, None,
                                power_gate="skip")
    assert any("seed" in m for m in bad_s)


def test_power_failures_5_refuses_on_missing_inputs_when_gate_is_full(monkeypatch):
    """Task 6 fix (flagged Task 5 minor): power_gate == 'full' asks for
    the reproduction — finals_counts/floors missing must REFUSE, not
    silently no-op the check the caller asked for."""
    from experiments.exp5 import power_5 as pw
    monkeypatch.setattr(pw, "finals_sha256_5", lambda root: "x" * 64)
    good = {"prereg_tag": b5.PREREG_TAG_5, "n_sim": pw.N_SIM_5, "seed": pw.SEED_5,
            "finals_sha256": "x" * 64, "declaration": "POWERED"}
    bad_fc = an.power_failures_5("root", good, None, {}, power_gate="full")
    assert any("finals_counts or floors missing" in m for m in bad_fc)
    bad_fl = an.power_failures_5("root", good, {}, None, power_gate="full")
    assert any("finals_counts or floors missing" in m for m in bad_fl)
    # power_gate="skip" is unaffected — None inputs are the normal test-only shape
    assert an.power_failures_5("root", good, None, None, power_gate="skip") == []


def test_re_crossings_5_counts_intervals_beyond_the_first(monkeypatch):
    """Review finding 2 (S10): a non-monotone spine loss table on a
    synthetic (size, spine) crosses a target twice; the first crossing
    is the one plan_5 actually bisects, the second is a re-crossing."""
    monkeypatch.setattr(b5, "SIZES_5", ("small", "big"))
    monkeypatch.setattr(b5, "SPINE_5", (10, 20, 30, 40))
    manifest = {"big": {"available": [10, 20, 30, 40]}}
    units = {"big": {"losses": {10: 5.0, 20: 3.0, 30: 4.0, 40: 1.0}},
             "small": {"losses": {b5.FINAL_STEP_5: 3.5}}}
    out = an._re_crossings_5(units, manifest, "big")
    assert out["small"]["n_crossings"] == 2
    assert out["small"]["intervals"] == [[10, 20], [30, 40]]
    assert out["small"]["re_crossings"] == [[30, 40]]


def test_replay_pairs_5_uses_the_committed_loss_not_the_logged_target(monkeypatch):
    """Task 6 mutation kill: the replay's target is the RE-DERIVED
    small final loss (`small_units["losses"][FINAL_STEP_5]`), never the
    search log's own attested `target` field — a stray/tampered logged
    target must not steer which bracket the replay lands on. Decreasing
    losses at [10,20,30,40] = [5,3,2,1]: the real final loss 3.5 crosses
    at [10,20]; a tampered logged target of 1.5 would cross at [30,40]
    instead if the replay ever used it."""
    monkeypatch.setattr(b5, "SIZES_5", ("small", "big"))
    monkeypatch.setattr(b5, "SPINE_5", (10, 20, 30, 40))
    monkeypatch.setattr(b5, "N_WINDOW_SIDE_5", 2)
    manifest = {"big": {"available": [10, 20, 30, 40]}}
    units = {"big": {"losses": {10: 5.0, 20: 3.0, 30: 2.0, 40: 1.0},
                     "counts": {s: {r: 1 for r in bt.RUNGS} for s in (10, 20, 30, 40)}},
             "small": {"losses": {b5.FINAL_STEP_5: 3.5},
                      "counts": {b5.FINAL_STEP_5: {r: 1 for r in bt.RUNGS}}}}
    log = {"size": "big", "spine": [10, 20, 30, 40],
          "pairs": {"small": {"target": 1.5, "status": "done", "plan": {},
                              "requested_all": []}}}
    pairs_data, failures = an.replay_pairs_5(units, manifest, log)
    assert len(pairs_data) == 1
    assert pairs_data[0]["plan"]["bracket"] == [10, 20]


def test_b6_12b_5_compares_on_the_intersection_and_scales_the_sum_bound(monkeypatch):
    """B-6 ruling 2026-09-22: the unit's `counts` are the full 34 RUNGS
    (every real collected 12b unit reads all 34), the referent is 11
    PREDICTOR_RUNGS only (`mac_interior_counts_5`'s corrected shape) —
    `_b6_12b_5` must compare on the INTERSECTION (11), print
    `n_rungs_compared`, and scale `GATE1_TOL_SUM_5` to 11/34 rather
    than reporting 23 spurious 'missing on one side' failures for the
    rungs the referent never carries."""
    eleven = b5.GATE1_DESCRIPTIVE_12B_RUNGS_5
    monkeypatch.setattr(b5, "GATE1_DESCRIPTIVE_12B_5", (1000,))
    monkeypatch.setattr(b5, "mac_interior_counts_5",
                        lambda size, step: {r: 100 for r in eleven})
    counts_34 = {r: 100 for r in bt.RUNGS}
    units = {"12b": {"steps": [1000], "counts": {1000: counts_34}}}
    rows = an._b6_12b_5(units)
    assert len(rows) == 1
    row = rows[0]
    assert row["n_rungs_compared"] == 11
    assert row["failures"] == []
    assert row["sum_abs_diff"] == 0 and row["max_abs_diff"] == 0
    assert math.isclose(row["gate1_tol_sum_scaled"], b5.GATE1_TOL_SUM_5 * 11 / 34)

    # a per-rung Δ beyond GATE1_TOL_PER_RUNG_5, still over only 11 rungs
    counts_off = dict(counts_34)
    counts_off[eleven[0]] = 100 + b5.GATE1_TOL_PER_RUNG_5 + 1
    units_off = {"12b": {"steps": [1000], "counts": {1000: counts_off}}}
    row_off = an._b6_12b_5(units_off)[0]
    assert row_off["n_rungs_compared"] == 11
    assert any(eleven[0] in f for f in row_off["failures"])
    assert not any("count missing" in f for f in row_off["failures"])


def test_s8_grid_points_interpolates_and_flags_measured_points(tmp_path, monkeypatch):
    """Review finding 2 (S8): a grid point coinciding with a step this
    experiment actually loaded is MEASURED ('interpolated': False); a
    grid point in between is log-step interpolated ('interpolated':
    True) between the two bracketing loaded points."""
    rungs = ("antonym", "antonym6")
    monkeypatch.setattr(b5, "RUNGS", rungs)
    for step in (100, 200, 300):
        d = tmp_path / f"step{step}"
        d.mkdir()
        for r in rungs:
            (d / f"{r}.json").write_text(json.dumps({"correct": step}))
    monkeypatch.setattr(b5, "interior_record_path_5",
                        lambda size, step, rung: tmp_path / f"step{step}" / f"{rung}.json")
    steps_avail, losses_avail = [100, 300], [5.0, 1.0]   # 200 was never loaded by this experiment
    pts = an._s8_grid_points_5("fake", [100, 200, 300], steps_avail, losses_avail)
    by_step = {p["step"]: p for p in pts}
    assert by_step[100]["interpolated"] is False and by_step[100]["loss"] == 5.0
    assert by_step[300]["interpolated"] is False and by_step[300]["loss"] == 1.0
    assert by_step[200]["interpolated"] is True
    x0, x1, x = math.log(100), math.log(300), math.log(200)
    expected = 5.0 + (1.0 - 5.0) * (x - x0) / (x1 - x0)
    assert abs(by_step[200]["loss"] - expected) < 1e-9
    assert by_step[200]["counts"] == {"antonym": 200, "antonym6": 200}


def test_drop_kind_names_which_fact_dropped_the_pair():
    """Freeze F-6: 'no spine interval crosses' is two facts — never reaches the
    target (design §3.2's named cause) or already below it at the first spine
    point (the crossing lies in the unsearched log head)."""
    sl = {"1000": 3.0, "2000": 2.9, "143000": 2.5}
    assert an.drop_kind_5({"spine_losses": sl, "target": 2.4}) == "never_reaches"
    assert an.drop_kind_5({"spine_losses": sl, "target": 3.1}) == "crosses_before_spine"
    assert an.drop_kind_5({"spine_losses": {}, "target": 3.1}) == "unknown"


def _g1_tree(tmp_path, counts_by_size_step):
    for (size, step), counts in counts_by_size_step.items():
        for r in b5.RUNGS:
            p = b5.rung_record_path_5(tmp_path, size, step, r)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"correct": counts[r]}))


def test_gate1b_re_derivation_refuses_a_count_beyond_tolerance(tmp_path, monkeypatch):
    """Final review I-1: gate 1(b)'s analyzer-side re-derivation had no test
    and no mutant (the worlds carry no referent)."""
    ref = {s: {r: 100 + i for i, r in enumerate(b5.RUNGS)} for s in ("1b", "2.8b")}
    monkeypatch.setattr(b5, "GATE1_REFERENT_SOURCE_5", {"1b": "fake", "2.8b": "fake"})
    monkeypatch.setattr(b5, "mac_final_counts_5", lambda size: ref.get(size))
    _g1_tree(tmp_path, {(s, b5.FINAL_STEP_5): {r: ref.get(s, {}).get(r, 0) for r in b5.RUNGS}
                        for s in b5.SIZES_5})
    no_ref = sorted(s for s in b5.SIZES_5 if s not in ref)
    rec = {"pass": True, "no_referent": no_ref}
    assert an.gate1b_failures_5(tmp_path, rec) == []
    assert an.gate1b_rederived_5(tmp_path) == {s: {"max_abs_diff": 0, "sum_abs_diff": 0,
                                                    "n_rungs": 34} for s in ref}
    moved = dict(ref["2.8b"]); moved["antonym"] += 16
    _g1_tree(tmp_path, {("2.8b", b5.FINAL_STEP_5): moved})
    bad = an.gate1b_failures_5(tmp_path, rec)
    assert any("gate 1(b) 2.8b/antonym: |Δ| 16 > 15" in f for f in bad)
    assert an.gate1b_rederived_5(tmp_path)["2.8b"]["max_abs_diff"] == 16
    moved = {r: v + 4 for r, v in ref["2.8b"].items()}          # 4 x 34 = 136 > 120 summed
    _g1_tree(tmp_path, {("2.8b", b5.FINAL_STEP_5): moved})
    assert any("sum |Δ| 136 > 120" in f for f in an.gate1b_failures_5(tmp_path, rec))


def test_gate1c_re_derivation_refuses_a_count_and_a_wrong_steps_set(tmp_path, monkeypatch):
    steps = (1000, 6000)
    ref = {st: {r: 50 + i for i, r in enumerate(b5.RUNGS)} for st in steps}
    monkeypatch.setattr(b5, "GATE1_INTERIOR_5", {"2.8b": steps})
    monkeypatch.setattr(b5, "mac_interior_counts_5", lambda size, step: ref.get(int(step)))
    _g1_tree(tmp_path, {("2.8b", st): ref[st] for st in steps})
    rec = {"pass": True, "steps": {str(st): {} for st in steps}}
    assert an.gate1c_failures_5(tmp_path, "2.8b", rec) == []
    assert set(an.gate1c_rederived_5(tmp_path, "2.8b")) == {"1000", "6000"}
    assert any("steps" in f for f in an.gate1c_failures_5(tmp_path, "2.8b",
                                                            {"pass": True, "steps": {"1000": {}}}))
    moved = dict(ref[6000]); moved["odd6"] += 16
    _g1_tree(tmp_path, {("2.8b", 6000): moved})
    assert any("gate 1(c) 2.8b/step6000/odd6: |Δ| 16 > 15" in f
               for f in an.gate1c_failures_5(tmp_path, "2.8b", rec))


def test_verdict_txt_prints_the_analyzers_gate1_figures_not_the_runners():
    v = {"tree": {"verdict": "MATCHED"}, "licence": {}, "primary": {}, "secondaries": {},
         "gate1": {"a": {}, "b": {"pass": True, "no_referent": [],
                                  "per_size": {"2.8b": {"referent": {}, "max_abs_diff": 999,
                                                        "sum_abs_diff": 999}},
                                  "rederived_by_analyzer": {"2.8b": {"max_abs_diff": 3,
                                                                     "sum_abs_diff": 11}}},
                   "c": {"2.8b": {"steps": {"1000": {"referent": {}, "max_abs_diff": 999,
                                                     "sum_abs_diff": 999}},
                                  "rederived_by_analyzer": {"1000": {"max_abs_diff": 2,
                                                                     "sum_abs_diff": 7}}}}}}
    txt = an.write_verdict_txt_5(v)
    assert "2.8b: max|Δ|=3 sum|Δ|=11" in txt and "gate 1(c) 2.8b/step1000: max|Δ|=2 sum|Δ|=7" in txt
    assert "999" not in txt


def test_s10_reads_12b_finiteness_from_the_units():
    """Final review M-1: S10's 12b finiteness came from a file nothing writes."""
    u = {"steps": [256, 1000, 143000], "losses": {256: 3.0, 1000: 2.9, 143000: 2.0}, "counts": {},
         "loss_records": {256: {"finite": True, "n_nonfinite": 0}, 1000: {"finite": True, "n_nonfinite": 0},
                          143000: {"finite": True, "n_nonfinite": 0}}}
    s10 = an._s10_texture_5({"12b": u}, [], "/nonexistent", None)
    assert s10["12b_finiteness"] == {"256": {"finite": True, "n_nonfinite": 0},
                                     "1000": {"finite": True, "n_nonfinite": 0}}
    assert "preflight" not in s10


def test_dropped_detail_comes_from_the_analyzers_replay(monkeypatch):
    """Final review M-7: never from the log's plan."""
    from experiments.exp5.tests import fakes_5 as fk
    sizes = ("1b", "2.8b")
    monkeypatch.setattr(b5, "SIZES_5", sizes)
    avail = (1000, 2000, 4000, 143000)
    monkeypatch.setattr(b5, "SPINE_5", avail)
    man = fk.synthetic_manifest(sizes, avail)
    units = {"1b": {"losses": {143000: 1.0}}, "2.8b": {"losses": {1000: 3.0, 2000: 2.5, 4000: 2.2, 143000: 2.1}}}
    d = an._dropped_detail_5(units, man, "2.8b")
    assert len(d) == 1 and d[0]["small"] == "1b" and d[0]["kind"] == "never_reaches"
    assert d[0]["target"] == 1.0 and d[0]["spine_losses"]["143000"] == 2.1
