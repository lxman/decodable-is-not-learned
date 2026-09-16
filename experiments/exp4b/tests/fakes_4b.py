# experiments/exp4b/tests/fakes_4b.py
"""Synthetic builders for `placebo_4b`'s tests: no committed bytes, no
model contact. `make_series` builds the `alignment_series_4` shape
(`{"steps", "a": {rung: [per step]}}`) `placebo_4b` consumes;
`iid_noise_world`/`random_walk_world` are the two calibration worlds
Step 1(d)/(e) run the placebo null against; `pia_from_means` builds
per-item alignment arrays (`float64[n_items]`) of the shape
`placebo_se_4b`'s bootstrap reads; `matching_pia` builds a `(series,
pia_t1, pia_end)` triple that satisfies `placebo_pool_4b`'s
series/pia consistency refusal EXACTLY (review finding 2) -- use this,
not a `series` and a separately-built `pia_from_means`, wherever a
test calls `placebo_pool_4b` (directly or through a function that
does)."""
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
    bootstrap SE is nonzero and rung-specific. The REALIZED mean of
    each array will differ from `rung_means[rung]` by the sample's own
    noise -- callers that need `placebo_pool_4b`'s series/pia identity
    to hold EXACTLY (every real caller) must use `matching_pia`
    instead, which reads the realized mean back rather than assuming
    it equals the target."""
    rng = np.random.default_rng(seed)
    return {r: (m + rng.normal(0.0, item_sigma, size=n_items)).astype(np.float64)
            for r, m in rung_means.items()}


def matching_pia(series: dict, flat: list, *, item_sigma=0.02, seed=0, n_items=500):
    """Builds per-item alignment arrays around `series["a"][f][0]`/
    `[-1]` for every f in `flat`, then returns a NEW series whose
    endpoints are REPLACED by those arrays' own realized means --
    reproducing `alignment_series_4`'s own construction (`a[r].append(
    float(pia[r].mean()))`) exactly, so `placebo_pool_4b`'s series/pia
    consistency check (placebo_4b's own refusal) is satisfied
    bit-for-bit rather than approximately. Intermediate steps are left
    unchanged (no pia exists for them; only t_1 and the endpoint are
    ever read against a pia array). Returns
    `(series_matched, pia_t1, pia_end)`."""
    rng_t1 = np.random.default_rng(seed * 2 + 1)
    rng_end = np.random.default_rng(seed * 2 + 2)
    a = {r: list(vals) for r, vals in series["a"].items()}
    pia_t1, pia_end = {}, {}
    for f in flat:
        arr_t1 = (series["a"][f][0] + rng_t1.normal(0.0, item_sigma, size=n_items)).astype(np.float64)
        arr_end = (series["a"][f][-1] + rng_end.normal(0.0, item_sigma, size=n_items)).astype(np.float64)
        pia_t1[f] = arr_t1
        pia_end[f] = arr_end
        a[f][0] = float(arr_t1.mean())
        a[f][-1] = float(arr_end.mean())
    return {"steps": list(series["steps"]), "a": a}, pia_t1, pia_end


def planted_tables(n_sites, *, n_items=500, v, k=10, seed=0):
    """Two synthetic set tables `(sets_m, sets_q)`, each `int64[n_sites,
    n_items, k]`, for `levels_4b`'s fast tests (Task 4 brief Step 1,
    resolution 5): site 0 is IDENTICAL on both sides — `sets_m[0] ==
    sets_q[0]` elementwise, so `metric_4.overlap_counts`/
    `mutual_knn_from_sets` reads exactly `1.0` there, the degenerate
    constant-token reading `GATE0_EXCLUDED_SITES_4` exists to drop —
    and every site `i >= 1` shares exactly `round(v*k)` of its `k`
    neighbour ids between the two models, so that site reads exactly
    `v`, bit for bit (no residual noise: the shared ids are the SAME
    array slice on both sides, and the non-shared ids are drawn from
    disjoint integer ranges so they can never accidentally coincide).

    Each site additionally owns a private, disjoint slice of the id
    universe (`3*10*k` ids wide, offset by `3*10*k*i`), so a CROSS-site
    pair — site i on one side against site j != i on the other — has
    structurally ZERO shared ids: exactly `0.0`, always below `v` for
    `v > 0`. This is what makes `levels_4b.max_pair_alignment_4b`'s
    "the best KEPT pair is v" exact rather than merely likely — the
    max over every kept cross-pair lands on a diagonal (same-index,
    non-zero) pair, never an off-diagonal one.

    Returns `(sets_m, sets_q, sites_m, sites_q)` with `sites_m ==
    sites_q == list(range(n_sites))` (both models use the same LAYER
    labels — a `depth_pairs`/`_pairing_positions` re-derivation over
    these labels reduces to the identity pairing)."""
    n_shared = int(round(v * k))
    if not 0 <= n_shared <= k:
        raise ValueError(f"planted_tables: v={v} at k={k} gives n_shared={n_shared} outside [0, {k}]")
    rng = np.random.default_rng(seed)
    block = 10 * k
    sets_m = np.zeros((n_sites, n_items, k), dtype=np.int64)
    sets_q = np.zeros((n_sites, n_items, k), dtype=np.int64)
    for i in range(n_sites):
        base = i * 3 * block          # each site's own disjoint id range
        for t in range(n_items):
            if i == 0:
                full = rng.choice(block, size=k, replace=False) + base
                sets_m[i, t] = full
                sets_q[i, t] = full
                continue
            shared = rng.choice(block, size=n_shared, replace=False) + base
            row_m, row_q = list(shared), list(shared)
            rest = k - n_shared
            if rest:
                extra_m = rng.choice(np.arange(block, 2 * block), size=rest, replace=False) + base
                extra_q = rng.choice(np.arange(2 * block, 3 * block), size=rest, replace=False) + base
                row_m += list(extra_m)
                row_q += list(extra_q)
            sets_m[i, t] = row_m
            sets_q[i, t] = row_q
    sites = list(range(n_sites))
    return sets_m, sets_q, sites, sites


def match_sets(sets_q, v, *, k=10, seed=0):
    """A new set table `sets_m` (same shape as `sets_q`) sharing
    EXACTLY `round(v*k)` ids per item, at EVERY site uniformly (no
    site-0 special case — `planted_tables` models that; this is for a
    test that wants a controllable alignment level against a FIXED
    reference table it does not otherwise get to construct, e.g.
    `test_levels_4b.py`'s `max_over_pairs_4b` wiring test, where the
    reference side is loaded once per trajectory and the model side
    varies per grid step). The shared ids are literal elements of
    `sets_q`'s own row (so the intersection count is exact); the
    non-shared ids are drawn from an ever-advancing, always-disjoint
    id block, so they can never accidentally coincide with `sets_q`'s
    own ids or with a previous item's non-shared ids."""
    sets_q = np.asarray(sets_q)
    n_sites, n_items, k_q = sets_q.shape
    if k_q != k:
        raise ValueError(f"match_sets: sets_q's k={k_q} != {k}")
    n_shared = int(round(v * k))
    if not 0 <= n_shared <= k:
        raise ValueError(f"match_sets: v={v} at k={k} gives n_shared={n_shared} outside [0, {k}]")
    rng = np.random.default_rng(seed)
    out = np.zeros_like(sets_q)
    fresh_base = int(sets_q.max()) + 1000
    for i in range(n_sites):
        for t in range(n_items):
            row_q = sets_q[i, t]
            shared_idx = rng.choice(k, size=n_shared, replace=False)
            row = list(row_q[shared_idx])
            rest = k - n_shared
            if rest:
                extra = rng.choice(np.arange(fresh_base, fresh_base + 10 * k), size=rest, replace=False)
                row += list(extra)
                fresh_base += 10 * k
            out[i, t] = row
    return out


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
