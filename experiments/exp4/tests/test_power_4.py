# experiments/exp4/tests/test_power_4.py
"""Tests for `power_4.py` (Task 5 brief + resolutions): `compute()` on
a hand-built (synthetic, no world) eligibility table gives a higher
P(LEADS) at phi*=.5 than at phi*=0, with P(LEADS|0) small (the exact
sign-flip resolution requires >= 7 rungs, since 1/2^n_rungs < ALPHA_4
only from n_rungs=7 on); `main()` writes the record ONCE and refuses a
second write; the eligibility_sha256/cells mismatch is refused by
`analyze_4._check_power_matches_eligibility_4`, on a tmp tree with a
stub eligibility file."""
from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp4 import analyze_4 as an
from experiments.exp4 import battery_4
from experiments.exp4 import power_4 as pw


def _synthetic_eligibility(n_rungs_per_traj=4, n_traj=2, *, G=6, c_r=3,
                           trend_t1=0.0, trend_end=0.05, x_end=0.3, se=0.02,
                           flat_se=0.01) -> tuple:
    """Two trajectories, each with `n_rungs_per_traj` distinct eligible
    R rungs (globally distinct names, so the union of rungs is
    n_traj * n_rungs_per_traj) and 3 flat rungs, over a small G-point
    grid. Returns `(elig, rung_sets, grids)`."""
    elig, rung_sets, grids = {}, {}, {}
    # Real grids never start at step 0 (Pythia's first grid point is
    # 1000; the other three trajectories start higher) -- log-linear
    # interpolation needs a strictly positive t_1.
    steps = list(range(10, 10 * (G + 1), 10))
    for ti in range(n_traj):
        traj = f"synthetic_t{ti}"
        flat = [f"f{ti}_{j}" for j in range(3)]
        R = [f"r{ti}_{j}" for j in range(n_rungs_per_traj)]
        elig[traj] = {
            "R": {r: {"x_end": x_end, "se": se, "eligible": True, "reason": "eligible",
                     "t_clear": steps[c_r], "t_clear_index": c_r} for r in R},
            "flat": {f: {"se_at_end": flat_se} for f in flat},
            "trend_t1": trend_t1, "trend_end": trend_end,
        }
        rung_sets[traj] = {"R": R, "flat": flat, "transient": [], "t_clear": {},
                           "endpoint_step": steps[-1]}
        grids[traj] = steps
    return elig, rung_sets, grids


def test_solve_m_hits_the_target_ratio():
    c_r, G = 4, 8
    for phi in (0.1, 0.25, 0.5, 0.75):
        m = pw._solve_m(c_r, G, phi)
        got = pw._logistic((c_r - 1 - m) / pw.LOGISTIC_WIDTH_4) / \
            pw._logistic((G - 1 - m) / pw.LOGISTIC_WIDTH_4)
        assert got == pytest.approx(phi, abs=1e-6)
    # phi* = 0 is the disclosed asymptote, not bisected.
    assert pw._solve_m(c_r, G, 0.0) == pytest.approx(c_r + 3.0)


def test_compute_leads_more_often_at_phi_half_than_phi_zero():
    elig, rung_sets, grids = _synthetic_eligibility()
    n_rungs = len({r for t in elig for r in elig[t]["R"]})
    assert n_rungs == 8   # 2 traj x 4 rungs, globally distinct names
    assert 1.0 / (2 ** n_rungs) < an.ALPHA_4   # the resolution requirement this fixture needs

    rec = pw.compute(elig, rung_sets, grids, n_sim=40, seed=0, phis=(0.0, 0.5))
    assert rec["arms"]["0.0"]["P_LEADS"] <= 0.1
    assert rec["arms"]["0.5"]["P_LEADS"] > rec["arms"]["0.0"]["P_LEADS"]
    assert rec["rungs"] == sorted({r for t in elig for r in elig[t]["R"]})
    assert rec["cells"] == sorted([t, r] for t in elig for r in elig[t]["R"])
    assert rec["flip_resolution"] == pytest.approx(1.0 / 256)
    assert rec["null_sd_T"] == rec["arms"]["0.0"]["sd_T"]
    assert rec["min_detectable_T"] is not None and rec["min_detectable_T"] > 0
    assert rec["assumptions"] == pw.TREND_SHAPE_NOTE_4
    assert rec["eligibility_bar_null_crossing_note"] == pw.ELIGIBILITY_BAR_NULL_CROSSING_NOTE_4
    for phi_key in ("0.0", "0.5"):
        arm = rec["arms"][phi_key]
        for field in ("P_LEADS", "P_PARTIAL", "P_FOLLOWS", "P_UNDETERMINED", "P_NO_CONVERGENCE"):
            assert 0.0 <= arm[field] <= 1.0
        assert 0.0 <= arm["mean_eligible_cells"] <= 8.0


def test_compute_declaration_powered_when_phi_half_clears_bar():
    elig, rung_sets, grids = _synthetic_eligibility()
    rec = pw.compute(elig, rung_sets, grids, n_sim=60, seed=1, phis=(0.0, 0.25, 0.5))
    assert rec["declaration"] in ("POWERED", "UNDERPOWERED IN ADVANCE")
    assert rec["declaration"] == ("POWERED" if rec["arms"]["0.5"]["P_LEADS"] >= 0.75
                                  else "UNDERPOWERED IN ADVANCE")


def test_compute_mean_eligible_cells_drops_when_signal_is_weak():
    # A cell whose x_end barely clears 2*se should sometimes drop out
    # of a draw by noise alone -- "cells can drop out by noise" (the
    # brief's own phrase) -- so mean_eligible_cells should read BELOW
    # the candidate count at least at phi* = 0 (little of the excess
    # has arrived pre-clear, and the endpoint value itself still
    # carries the SAME per-step noise).
    elig, rung_sets, grids = _synthetic_eligibility(x_end=0.045, se=0.02)   # 2*se = 0.04
    rec = pw.compute(elig, rung_sets, grids, n_sim=80, seed=2, phis=(0.0,))
    assert rec["arms"]["0.0"]["mean_eligible_cells"] < 8.0


def test_compute_raises_on_empty_eligibility():
    with pytest.raises(ValueError, match="no eligible cells"):
        pw.compute({"t": {"R": {}, "flat": {}}}, {"t": {"R": [], "flat": []}}, {"t": [0, 10]})


def test_main_writes_once_and_refuses_a_second_write(tmp_path):
    root = tmp_path / "root"
    elig, _, _ = _synthetic_eligibility(n_rungs_per_traj=7, n_traj=1)
    # `main()` reads real rung_sets/grids for the four REAL trajectories
    # (frozen exp2g/2i/2m/2n bytes, independent of `root`) but `compute
    # ()` only ever touches the trajectories present in `elig` --
    # reuse ONE real trajectory name/grid so the candidate rungs are a
    # subset of its real R (`cells_4` requires that: it only ever
    # reads rungs in `rs["R"]`).
    real_traj = "pythia_2.8b"
    real_R = list(battery_4.RUNG_SET_PIN_4[real_traj])
    real_flat = sorted(set(battery_4.RUNGS) - set(real_R))
    steps = list(battery_4.GRID_4[real_traj])
    fake = {real_traj: {
        "R": {r: {"x_end": 0.3, "se": 0.02, "eligible": True, "reason": "eligible",
                 "t_clear": steps[5], "t_clear_index": 5} for r in real_R},
        "flat": {f: {"se_at_end": 0.01} for f in real_flat},
        "trend_t1": 0.0, "trend_end": 0.05,
    }}
    elig_path = battery_4.eligibility_path(root)
    elig_path.parent.mkdir(parents=True, exist_ok=True)
    elig_path.write_text(json.dumps(fake, indent=1))

    rec = pw.main(root=root, n_sim=10, seed=0, phis=(0.0, 0.5))
    assert battery_4.power_path(root).is_file()
    on_disk = json.loads(battery_4.power_path(root).read_text())
    assert on_disk["eligibility_sha256"] == bg.sha256_file(elig_path)
    assert on_disk["prereg_tag"] == battery_4.PREREG_TAG_4
    assert rec["eligibility_sha256"] == on_disk["eligibility_sha256"]

    with pytest.raises(RuntimeError, match="written ONCE"):
        pw.main(root=root, n_sim=10, seed=0)


def test_main_refuses_when_eligibility_file_absent(tmp_path):
    root = tmp_path / "root"
    with pytest.raises(RuntimeError, match="reference stage"):
        pw.main(root=root, n_sim=10)


# -------------------------------------- analyzer cross-check (a stub tree)

def test_analyzer_refuses_power_record_with_wrong_eligibility_sha(tmp_path):
    elig = {"t": {"R": {"r1": {"eligible": True}, "r2": {"eligible": True},
                       "r3": {"eligible": True}}}}
    elig_path = tmp_path / "eligibility_4.json"
    elig_path.write_text(json.dumps(elig, indent=1))
    real_sha = bg.sha256_file(elig_path)

    power_ok = {"cells": [["t", "r1"], ["t", "r2"], ["t", "r3"]], "rungs": ["r1", "r2", "r3"],
               "eligibility_sha256": real_sha, "declaration": "POWERED", "n_sim": 10, "arms": {}}
    bad_ok = an._check_power_matches_eligibility_4(power_ok, elig, real_sha)
    assert bad_ok == []

    power_bad_sha = dict(power_ok, eligibility_sha256="deadbeef" * 8)
    bad_sha = an._check_power_matches_eligibility_4(power_bad_sha, elig, real_sha)
    assert any("eligibility_sha256" in b for b in bad_sha)

    power_bad_cells = dict(power_ok, cells=[["t", "r1"]])
    bad_cells = an._check_power_matches_eligibility_4(power_bad_cells, elig, real_sha)
    assert any("cells" in b for b in bad_cells)

    power_bad_rungs = dict(power_ok, rungs=["r1", "r2", "bogus_rung"])
    bad_rungs = an._check_power_matches_eligibility_4(power_bad_rungs, elig, real_sha)
    assert any("rungs" in b for b in bad_rungs)
