import pytest

from experiments.exp5b import analyze_5b as an
from experiments.exp5b import battery_5b as b5b
from experiments.exp5b import power_5b as pw5b


def test_collect_total_5b_prefix_named_types_and_crash_on_logic_defect():
    v, f = an.collect_total_5b(lambda: (_ for _ in ()).throw(OSError("x")), "5b x")
    assert v is None and f == ["5b x: OSError: x"]
    assert an.collect_total_5b(lambda: 3, "5b y") == (3, [])
    with pytest.raises(ZeroDivisionError):
        an.collect_total_5b(lambda: 1 / 0, "5b z")
    with pytest.raises(ValueError, match="prefix"):
        an.collect_total_5b(lambda: 3, "5 no")


def test_licence_block_names_every_cell():
    s1 = {"outside_2p8b": {"T": 0.004, "p": 0.3, "n_cells": 40}}
    for verdict, cell in (("SURVIVES", "CALIBRATED"), ("SURVIVES", "INFLATED"), ("SURVIVES", "OFF-GRID"),
                          ("NOT-SURVIVED", "INSIDE"), ("NOT-SURVIVED", "SIGN-ONLY"),
                          ("NOT-SURVIVED", "SIZE-ONLY"), ("UNDETERMINED", None), ("INSUFFICIENT_DATA", None)):
        tree = {"verdict": verdict, "cell": cell, "reason": "r"}
        lb = an.licence_block_5b(tree, primary={"T": 0.03, "rung_block": {"p": 0.002}},
                                 calibration={"alpha_realized": 0.012, "sigma_hat": 14.2, "null_mean_T": -0.001,
                                              "T_star": 0.031, "cell": cell, "in_grid": cell != "OFF-GRID"},
                                 s1=s1, sigma_hat={"pooled": 14.2, "per_side": {"1b": 12.0}})
        assert lb["key"] == (f"{verdict}-{cell}" if cell else verdict)
        assert lb["sentence"] and lb["caveat"]
        if cell == "OFF-GRID":
            # finding (Task 5): the brief's licence body (== design §6's verbatim sentence,
            # `experiment-5b-design.md` line 116, "the licence is NOT claimed") capitalizes
            # NOT for emphasis, matching its "DEMOTED" sibling; the brief's own assertion here
            # checked the lowercase spelling, which is never a substring of the capitalized
            # source phrase — corrected to the phrase design §6 actually specifies, unruled
            # (flagged in PROGRESS.md / the task report; not weakened otherwise)
            assert "NOT claimed" in lb["sentence"]
        if verdict == "SURVIVES":
            assert "15 items" in lb["sentence"] and "2 items" in lb["sentence"]     # .03×500, .004×500


def test_power_failures_5b_catches_a_non_reproducing_record(monkeypatch):
    def fake_compute(cells, floors, *, n_sim, seed):
        return {"n_sim": n_sim, "seed": seed, "declaration": "POWERED", "prereg_tag": b5b.PREREG_TAG_5B,
               "exp5_closed_tag": b5b.EXP5_CLOSED_TAG_5B, "sigma_hat_axis": [1] * 6, "alpha_5b_axis": [1] * 6,
               "null_mean_5b_axis": [1] * 6, "alpha_exp5_axis": [1] * 6, "alpha_naive_axis": [1] * 6,
               "null_mean_exp5_axis": [1] * 6, "null_mean_naive_axis": [1] * 6}
    monkeypatch.setattr(an.pw5b, "compute_5b", fake_compute)
    monkeypatch.setattr(an.pw5b, "N_SIM_5B", 5)
    monkeypatch.setattr(an.pw5b, "SEED_5B", 0)
    struct_sha = pw5b.structure_sha256_5b(pw5b.structure_5b([]))
    rec = {"prereg_tag": b5b.PREREG_TAG_5B, "exp5_closed_tag": b5b.EXP5_CLOSED_TAG_5B, "n_sim": 5, "seed": 0,
          "declaration": "DECLARED UNDERPOWERED IN ADVANCE", "sigma_hat_axis": [1] * 6, "alpha_5b_axis": [1] * 6,
          "null_mean_5b_axis": [1] * 6, "alpha_exp5_axis": [1] * 6, "alpha_naive_axis": [1] * 6,
          "null_mean_exp5_axis": [1] * 6, "null_mean_naive_axis": [1] * 6, "structure_sha256": struct_sha}
    bad = an.power_failures_5b(rec, cells5_live=[], floors={}, closed=None, power_gate="full")
    assert any("byte-for-byte" in b for b in bad)


def test_projection_failures_5b_checks_both_ancestries():
    sides = {"1b": {"git_shas": {143000: "u1", 30000: "u2"}, "whys": {143000: "final", 30000: "member"}}}
    ok = an.projection_failures_5b(sides, projection_commit="p", prereg_commit="t",
                                   is_ancestor=lambda a, b: True, edits=[])
    assert ok == []
    assert an.projection_failures_5b(sides, projection_commit=None, prereg_commit="t",
                                     is_ancestor=lambda a, b: True, edits=[])
    assert an.projection_failures_5b(sides, projection_commit="p", prereg_commit="t",
                                     is_ancestor=lambda a, b: not (a == "t" and b == "p"), edits=[])
    assert an.projection_failures_5b(sides, projection_commit="p", prereg_commit="t",
                                     is_ancestor=lambda a, b: not (a == "p" and b == "u2"), edits=[])
    assert an.projection_failures_5b(sides, projection_commit="p", prereg_commit="t",
                                     is_ancestor=lambda a, b: True, edits=["edited"])
