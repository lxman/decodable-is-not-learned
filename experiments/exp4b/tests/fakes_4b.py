# experiments/exp4b/tests/fakes_4b.py
"""Synthetic builders for `placebo_4b`'s tests: no committed bytes, no
model contact. `make_series` builds the `alignment_series_4` shape
(`{"steps", "a": {rung: [per step]}}`) `placebo_4b` consumes;
`iid_noise_world`/`random_walk_world` are the two calibration worlds
Step 1(d)/(e) run the placebo null against; `pia_from_means` builds
per-item alignment arrays (`float64[n_items]`) of the shape
`placebo_se_4b`'s bootstrap reads."""
from __future__ import annotations

import numpy as np


def make_series(steps, values: dict) -> dict:
    """`values`: `{rung: [per-step float]}`. Returns
    `{"steps": [...], "a": {rung: [...]}}`."""
    return {"steps": list(steps), "a": {r: list(v) for r, v in values.items()}}


def iid_noise_world(*, n_flat=30, n_steps=20, sigma=0.05, seed=0):
    """Flat rungs wobble as iid N(0, sigma) around a shared trend — no
    drift, no systematic rise. Returns `(series, flat_rungs)`."""
    rng = np.random.default_rng(seed)
    steps = list(range(n_steps))
    trend = rng.normal(0.5, 0.1, size=n_steps)
    flat = [f"flat_{i}" for i in range(n_flat)]
    a = {f: (trend + rng.normal(0.0, sigma, size=n_steps)).tolist() for f in flat}
    return make_series(steps, a), flat


def random_walk_world(*, n_flat=30, n_steps=20, step_sigma=0.05, seed=0):
    """Flat rungs are cumulative sums of iid increments (a drifting,
    accumulating world) around a common start. Returns
    `(series, flat_rungs)`."""
    rng = np.random.default_rng(seed)
    steps = list(range(n_steps))
    flat = [f"flat_{i}" for i in range(n_flat)]
    a = {}
    for f in flat:
        increments = rng.normal(0.0, step_sigma, size=n_steps)
        increments[0] = 0.0
        a[f] = (0.5 + np.cumsum(increments)).tolist()
    return make_series(steps, a), flat


def pia_from_means(rung_means: dict, *, n_items=500, item_sigma=0.02, seed=0) -> dict:
    """`{rung: float64[n_items]}` whose item mean is (in expectation)
    `rung_means[rung]`, with iid item-level noise so the leave-one-out
    bootstrap SE is nonzero and rung-specific."""
    rng = np.random.default_rng(seed)
    return {r: (m + rng.normal(0.0, item_sigma, size=n_items)).astype(np.float64)
            for r, m in rung_means.items()}


def autocorr_world(*, n_flat=30, n_steps=20, rho=0.0, sigma=0.05, seed=0):
    """Flat rungs whose LOO-excess INCREMENTS carry lag-1
    autocorrelation `rho` (0.0 -> iid increments; 0.5 -> AR(1)) —
    Step 1(k)'s two worlds for `s5_autocorr_4b`. Each rung's increment
    stream `e[1:]` follows `e[t] = rho*e[t-1] + sqrt(1-rho^2)*N(0,
    sigma)`; `a_r(t) = 0.5 + cumsum(e)` with `e[0] = 0` (no increment
    before t_1). Returns `(series, flat_rungs)`."""
    steps = list(range(n_steps))
    flat = [f"flat_{i}" for i in range(n_flat)]
    a = {}
    for i, f in enumerate(flat):
        rng = np.random.default_rng(seed * 10_000 + i)
        e = np.zeros(n_steps)
        for t in range(1, n_steps):
            e[t] = rho * e[t - 1] + np.sqrt(1.0 - rho ** 2) * rng.normal(0.0, sigma)
        a[f] = (0.5 + np.cumsum(e)).tolist()
    return make_series(steps, a), flat


def rising_rung_series(steps, flat_a: dict, *, rung: str, extra_drift, base_sigma, seed):
    """One rising rung's series added to an existing flat-rung `a`
    dict: shares the flat rungs' trend + `base_sigma` wobble, PLUS
    `extra_drift[i]` at grid index i (0 for a rung meant to look like
    a flat rung driven through the primary's machinery, e.g. S4's
    matched-scale check). Returns the augmented `a` dict (copy)."""
    rng = np.random.default_rng(seed)
    n = len(steps)
    trend = np.mean([flat_a[f] for f in flat_a], axis=0)
    noise = rng.normal(0.0, base_sigma, size=n)
    out = dict(flat_a)
    out[rung] = (trend + noise + np.asarray(extra_drift, dtype=np.float64)).tolist()
    return out
