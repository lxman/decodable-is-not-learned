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
            "prereg_tag": b5.PREREG_TAG_5, "pass": True}
    assert an.gate1a_failures_5(good) == []
    assert an.gate1a_failures_5({**good, "digests_equal": False})
    assert an.gate1a_failures_5({**good, "continuations_compared": {**good["continuations_compared"], "mod13": 499}})
    assert an.gate1a_failures_5({**good, "loss_equal": False})


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
