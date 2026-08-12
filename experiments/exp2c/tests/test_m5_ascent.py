# experiments/exp2c/tests/test_m5_ascent.py
"""Tests for the scale-ascent score — the OUTCOME side (design §3).

Ruled 2026-08-11 (Michael): mirror the probe side exactly.

  probe:  margin = (starved-val acc - null mean)/(1 - null mean),
                   zero below the significance bar;
          score  = seed-mean, then mean over the two probe sizes.

  eval:   margin = (trained acc - untrained floor)/(1 - untrained floor),
                   zero below the significance bar;
          score  = mean over the three eval sizes.

The probe side's bar is a hypothesis test at alpha .01, not an
interval-overlap rule, so the eval side uses one — Fisher exact,
one-sided, trained against its own empirical floor, per (rung, size)
cell. Exact, no approximation, no fitted quantity, consistent with the
harness's existing Clopper-Pearson choice.

EVERY test here runs on synthetic cells. This module was written and
frozen while M4 was still running and its numbers were unlooked-at;
tests that read real results would defeat that.
"""

import json

import pytest

from experiments.exp2c.run import m5_ascent as m5


def cell(correct, n=500):
    return {"correct": correct, "n": n, "acc": correct / n}


# ------------------------------------------------------- the margin rule

def test_margin_is_zero_when_trained_matches_the_floor():
    assert m5.ascent_margin(cell(50), cell(50))["margin"] == 0.0


def test_margin_is_zero_when_trained_is_below_the_floor():
    """Never negative — mirrors 'zero below the significance bar'."""
    assert m5.ascent_margin(cell(20), cell(60))["margin"] == 0.0


def test_margin_is_zero_when_the_lift_is_not_significant():
    """A handful of extra hits out of 500 is not ascent."""
    out = m5.ascent_margin(cell(55), cell(50))
    assert out["margin"] == 0.0
    assert out["significant"] is False


def test_margin_normalizes_against_the_empirical_floor():
    """(acc - floor)/(1 - floor), the probe side's formula with the
    untrained floor standing in for the permutation null mean."""
    out = m5.ascent_margin(cell(300), cell(50))       # .60 vs .10
    assert out["significant"] is True
    assert out["margin"] == pytest.approx((0.6 - 0.1) / (1 - 0.1))


def test_a_perfect_trained_score_over_a_zero_floor_is_margin_one():
    out = m5.ascent_margin(cell(500), cell(0))
    assert out["margin"] == pytest.approx(1.0)


def test_margin_carries_cp_bounds_on_both_arms():
    """Design §4: every zero ships a CP bound."""
    out = m5.ascent_margin(cell(0), cell(0))
    assert out["margin"] == 0.0
    assert out["trained_cp95"][0] == 0.0 and out["trained_cp95"][1] > 0
    assert out["untrained_cp95"][1] > 0


def test_the_bar_is_the_probe_sides_alpha():
    assert m5.ALPHA == 0.01


# ------------------------------------------------------ the rung score

def test_rung_score_is_the_mean_over_the_three_eval_sizes():
    cells = {"2.8b": (cell(300), cell(50)),
             "6.9b": (cell(400), cell(50)),
             "12b": (cell(500), cell(50))}
    out = m5.rung_ascent_score(cells)
    expected = sum(m5.ascent_margin(t, u)["margin"]
                   for t, u in cells.values()) / 3
    assert out["ascent_score"] == pytest.approx(expected)
    assert set(out["per_size"]) == {"2.8b", "6.9b", "12b"}


def test_a_rung_flat_at_every_size_scores_exactly_zero():
    """Flat rungs enter as zero-score ties (design §3) — not as a small
    positive number that would manufacture a spurious rank."""
    cells = {s: (cell(50), cell(50)) for s in ("2.8b", "6.9b", "12b")}
    assert m5.rung_ascent_score(cells)["ascent_score"] == 0.0


def test_rung_score_requires_all_three_sizes():
    """A partial rung would be an average over a different denominator
    than its neighbours — silent, and it would bias the ranking."""
    with pytest.raises(ValueError, match="missing"):
        m5.rung_ascent_score({"2.8b": (cell(300), cell(50))})


def test_no_extrapolated_or_fitted_quantity_is_produced():
    """Design §3: 'no fitted crossings or extrapolated quantities'. The
    score is a mean of three measured margins and nothing else."""
    cells = {"2.8b": (cell(100), cell(50)), "6.9b": (cell(300), cell(50)),
             "12b": (cell(450), cell(50))}
    out = m5.rung_ascent_score(cells)
    assert set(out) == {"ascent_score", "per_size"}


# --------------------------------------------------------- completeness

def test_assemble_refuses_on_an_incomplete_campaign(tmp_path):
    """Scoring a half-finished M4 would rank rungs against different
    amounts of evidence."""
    with pytest.raises(RuntimeError, match="incomplete"):
        m5.assemble(results_dir=tmp_path, write=False)


def test_assemble_reports_which_cells_are_missing(tmp_path):
    try:
        m5.assemble(results_dir=tmp_path, write=False)
    except RuntimeError as e:
        assert "204" in str(e)


# ------------------------------------------------------------ the join

def test_join_merges_probe_and_ascent_into_analyze_inputs():
    probe = {"rungs": [{"name": "a", "family": "f", "scored": True,
                        "probe_score": 0.5},
                       {"name": "b", "family": "f", "scored": True,
                        "probe_score": 0.1}],
             "untrained_fires": {"a": ["not_fire"], "b": ["not_fire"]},
             "shuffled_fires": []}
    ascent = {"rungs": {"a": {"ascent_score": 0.8},
                        "b": {"ascent_score": 0.2}}}
    inp = m5.join(probe, ascent)
    assert [r["ascent_score"] for r in inp.rungs] == [0.8, 0.2]
    assert [r["probe_score"] for r in inp.rungs] == [0.5, 0.1]
    assert inp.untrained_fires == probe["untrained_fires"]


def test_join_refuses_when_a_scored_rung_has_no_ascent_score():
    probe = {"rungs": [{"name": "a", "family": "f", "scored": True,
                        "probe_score": 0.5}],
             "untrained_fires": {}, "shuffled_fires": []}
    with pytest.raises(ValueError, match="ascent"):
        m5.join(probe, {"rungs": {}})


def test_join_preserves_the_family_block_order():
    probe = {"rungs": [{"name": n, "family": f, "scored": True,
                        "probe_score": 0.0}
                       for n, f in [("a", "f1"), ("b", "f1"), ("c", "f2")]],
             "untrained_fires": {}, "shuffled_fires": []}
    ascent = {"rungs": {n: {"ascent_score": 0.0} for n in "abc"}}
    inp = m5.join(probe, ascent)
    assert [r["name"] for r in inp.rungs] == ["a", "b", "c"]
