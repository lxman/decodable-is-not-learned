import numpy as np
import pytest

from experiments.exp2g import stats_2g as sg


def test_somers_d_hand_cases():
    # all informative pairs concordant
    r = sg.somers_d_within([1, 2, 3, 4], [0, 0, 1, 1], ["a"] * 4)
    assert r["d"] == 1.0 and r["n_pairs"] == 4 and r["n_pos"] == 2
    # all discordant
    assert sg.somers_d_within([4, 3, 2, 1], [0, 0, 1, 1], ["a"] * 4)["d"] == -1.0
    # cross-stratum pairs are not counted
    r = sg.somers_d_within([1, 2, 3, 4], [0, 1, 0, 1], ["a", "b", "a", "b"])
    assert r["n_pairs"] == 0 and np.isnan(r["d"])
    # x ties contribute 0
    r = sg.somers_d_within([1, 1, 2, 2], [0, 1, 0, 1], ["a"] * 4)
    assert r["n_pairs"] == 4 and r["d"] == 0.0
    # y ties are not informative
    r = sg.somers_d_within([1, 2, 3], [1, 1, 1], ["a"] * 3)
    assert r["n_pairs"] == 0


def test_permute_within_keeps_strata():
    rng = np.random.default_rng(0)
    x = np.arange(10.0)
    strata = ["a"] * 5 + ["b"] * 5
    xp = sg.permute_within(x, strata, rng)
    assert sorted(xp[:5]) == list(range(5)) and sorted(xp[5:]) == list(range(5, 10))


def _cell(rng, n, rho, n_pos, strata_k=2, rung="r"):
    z = rng.normal(size=n)
    x = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
    w = rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=n)
    order = np.argsort(w)
    y = np.zeros(n, int)
    y[order[-n_pos:]] = 1 + np.arange(n_pos) * 21 // n_pos
    strata = [str(i % strata_k) for i in range(n)]
    return {"rung": rung, "x": x, "y": y, "strata": strata}


def test_perm_test_null_is_calibrated_and_signal_detected():
    rng = np.random.default_rng(1)
    null_cells = [_cell(rng, 300, 0.0, 60, rung=f"r{i}") for i in range(3)]
    r0 = sg.perm_test(null_cells, n_perm=400, seed=0)
    assert abs(r0["T"]) < 0.12 and r0["p"] > 0.05
    assert set(r0["per_rung"]) == {"r0", "r1", "r2"}
    sig_cells = [_cell(rng, 300, 0.7, 60, rung=f"r{i}") for i in range(3)]
    r1 = sg.perm_test(sig_cells, n_perm=400, seed=0)
    assert r1["T"] > 0.3 and r1["p"] < 0.01
    assert r1["n_perm"] == 400 and r1["null_sd"] > 0


def test_perm_test_is_deterministic():
    rng = np.random.default_rng(2)
    cells = [_cell(rng, 100, 0.3, 30)]
    a = sg.perm_test(cells, n_perm=200, seed=5)
    b = sg.perm_test(cells, n_perm=200, seed=5)
    assert a == b


def test_perm_test_refuses_a_cell_without_pairs():
    with pytest.raises(ValueError):
        sg.perm_test([{"rung": "r", "x": [1, 2], "y": [0, 0], "strata": ["a", "a"]}],
                     n_perm=10, seed=0)


def test_bootstrap_and_pooled():
    rng = np.random.default_rng(3)
    c = _cell(rng, 200, 0.8, 50)
    ci = sg.bootstrap_d(c["x"], c["y"], c["strata"], n_boot=100, seed=0)
    assert ci["lo"] <= ci["point"] <= ci["hi"] and ci["lo"] > 0
    p = sg.pooled_d([c, _cell(rng, 50, 0.0, 10)])
    assert -1 <= p <= 1
