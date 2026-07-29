# experiments/exp2c/tests/test_power_table.py
import numpy as np

from experiments.exp2c.run import power_table as pt


def test_null_alpha_calibration():
    # under the family null the calibrated cutoff must yield ~1% rejections
    r = pt.simulate(families=[3, 3, 2, 2, 1, 1], rho_family=0.5,
                    rho_true=0.0, n_sims=400, seed=0)
    assert 0.0 <= r["alpha_at_cutoff"] <= 0.03


def test_power_monotone_in_effect():
    lo = pt.simulate([3, 3, 2, 2, 1, 1], 0.5, 0.4, n_sims=300, seed=1)
    hi = pt.simulate([3, 3, 2, 2, 1, 1], 0.5, 0.8, n_sims=300, seed=1)
    assert hi["power"] > lo["power"]


def test_naive_perm_p_equivalence():
    # Ruling 2026-07-29 (PROGRESS.md): the vectorized _naive_perm_p must
    # reproduce the plan-text loop implementation's p-values EXACTLY --
    # same rng.permutation call sequence, exact equality, no tolerance.
    for shape in ([3, 3, 2, 2, 1, 1], [3, 2, 1]):
        for seed in (0, 1, 2):
            x, y = pt._battery(np.random.default_rng(seed), shape,
                               rho_family=0.5, shared=0.3)
            p_loop = pt._naive_perm_p_loop(
                x, y, np.random.default_rng(seed + 100), n_perm=200)
            p_vec = pt._naive_perm_p(
                x, y, np.random.default_rng(seed + 100), n_perm=200)
            assert p_loop == p_vec, (shape, seed, p_loop, p_vec)
