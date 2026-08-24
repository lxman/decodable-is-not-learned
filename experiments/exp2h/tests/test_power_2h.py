# experiments/exp2h/tests/test_power_2h.py
"""power_2h: the simulated cells respect n_pos and use the REAL
committed sampler counts as x (never simulated); calibration is
monotone; power_at runs through analyze_2h's own tree."""
import numpy as np

from experiments.exp2g import battery_2g as bg
from experiments.exp2g import strata_2g as sg
from experiments.exp2h import battery_2h as bh
from experiments.exp2h import power_2h as pw


def _setup():
    # sg.build_table unconditionally iterates bg.PREDICTOR_RUNGS, so the
    # battery it's fed must cover that full 11-rung set (R_69 alone is
    # an 8-rung subset and raises KeyError); everything downstream still
    # indexes by bh.R_69 only.
    table = sg.build_table(bg.load_battery(bg.PREDICTOR_RUNGS))
    x_real = bh.sampler_counts("1b", bh.R_69)
    n_pos = {r: bh.FINAL_COUNT_PIN_69[r] for r in bh.R_69}
    return table, x_real, n_pos


def test_simulated_cells_respect_n_pos_and_use_real_x():
    table, x_real, n_pos = _setup()
    rng = np.random.default_rng(0)
    cells = pw.simulate_cells_69(rng, 0.5, table, x_real, n_pos, bh.R_69)
    by = {c["rung"]: c for c in cells}
    assert bh.n_trained_69() == 22
    for r in bh.R_69:
        assert int((np.asarray(by[r]["y"]) > 0).sum()) == n_pos[r]
        assert by[r]["strata"] == table[r]["strata"]
        # x is the real committed count, untouched by the simulation
        assert list(by[r]["x"]) == list(x_real[r])
        assert max(by[r]["y"]) <= 22


def test_calibration_is_monotone():
    table, x_real, n_pos = _setup()
    lo = pw.calibrate_rho(0.10, table, x_real, n_pos, bh.R_69, seed=0, n_cal=5)
    hi = pw.calibrate_rho(0.20, table, x_real, n_pos, bh.R_69, seed=0, n_cal=5)
    assert 0 <= lo < hi < 1


def test_power_at_runs_through_the_tree():
    table, x_real, n_pos = _setup()
    # n_perm must clear the permutation p-value floor 1/(n_perm+1) < ALPHA
    # (.01) for CONFIRMED to be reachable at all; 200 floors at ~.005.
    r = pw.power_at(0.9, table, x_real, n_pos, bh.R_69, n_sim=5, n_perm=200, seed=0)
    assert set(r) >= {"p_confirmed", "p_detect", "mean_T", "n_sim", "rho"}
    assert r["p_confirmed"] > 0.5


def test_rank_to_count_direction():
    c = pw._ranks_to_counts([10, 20, 30, 40], 21)
    assert c[10] == 21
    assert c[40] >= 1
    assert c[10] >= c[20] >= c[30] >= c[40]


def test_rankz_handles_zero_variance():
    z = pw._rankz(np.zeros(5))
    assert np.allclose(z, 0.0)
