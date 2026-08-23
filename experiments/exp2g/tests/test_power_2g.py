import numpy as np

from experiments.exp2g import battery_2g as bg
from experiments.exp2g import power_2g as pw
from experiments.exp2g import strata_2g as sg


def _setup():
    # build_table (strata_2g.py) unconditionally iterates
    # bg.PREDICTOR_RUNGS, so the battery it's fed must cover that full
    # 11-rung set (R_28 alone is a 7-rung subset and raises KeyError);
    # everything downstream still indexes by bg.R_28 only.
    table = sg.build_table(bg.load_battery(bg.PREDICTOR_RUNGS))
    n_pos = {r: bg.FINAL_COUNT_PIN["2.8b"][r] for r in bg.R_28}
    return table, n_pos


def test_simulated_cells_respect_n_pos_and_strata():
    table, n_pos = _setup()
    rng = np.random.default_rng(0)
    cells, twin = pw.simulate_cells(rng, 0.5, table, n_pos, bg.R_28)
    by = {c["rung"]: c for c in cells}
    for r in bg.R_28:
        assert int((np.asarray(by[r]["y"]) > 0).sum()) == n_pos[r]
        assert by[r]["strata"] == table[r]["strata"]
        assert max(by[r]["y"]) <= bg.n_trained("2.8b")
    assert abs(pw.realized_d(twin)) < 0.1


def test_calibration_is_monotone():
    table, n_pos = _setup()
    lo = pw.calibrate_rho(0.10, table, n_pos, bg.R_28, seed=0, n_cal=5)
    hi = pw.calibrate_rho(0.20, table, n_pos, bg.R_28, seed=0, n_cal=5)
    assert 0 < lo < hi < 1


def test_power_at_runs_through_the_tree():
    table, n_pos = _setup()
    # n_perm must clear the permutation p-value floor 1/(n_perm+1) < ALPHA
    # (.01) for FORECAST to be reachable at all; 50 floors at ~.0196 and
    # can never satisfy p < ALPHA regardless of rho, so 200 (floor ~.005).
    r = pw.power_at(0.9, table, n_pos, bg.R_28, n_sim=3, n_perm=200, seed=0)
    assert set(r) >= {"p_forecast", "p_detect", "mean_T", "n_sim", "rho"}
    assert r["p_forecast"] == 1.0
