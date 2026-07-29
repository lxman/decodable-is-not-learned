import numpy as np

from experiments.exp2c.run import screen


def test_reject_on_planted_leak():
    # labels linearly decodable from "activations" -> must reject
    rng = np.random.default_rng(0)
    X = rng.normal(size=(400, 32)).astype(np.float32)
    y = (X[:, 0] > 0).astype(int)          # surface-legible label
    rec = screen.screen_arrays(X, y, n_perm=200, seed=0)
    assert rec["classification"] in ("elevated", "structural_abort") or \
        rec["at_floor"] and rec["margin"] > 0.2


def test_pass_on_null():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(400, 32)).astype(np.float32)
    y = rng.integers(0, 7, size=400)
    rec = screen.screen_arrays(X, y, n_perm=200, seed=0)
    assert rec["classification"] in ("not_fire", "tolerated")
