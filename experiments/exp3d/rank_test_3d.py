"""The preregistered statistic (design §5.3) and its exact null —
Experiment 3d's inference machinery, model-free and data-free: every
function here is a pure map from (frozen ranks, fired sets) to
numbers.

THE STATISTIC. T = Σ over fired items of their within-stratum midrank
(ascending cost, rank 1 = cheapest). Small T = fired items cheap =
the predicted direction. One-sided p = P(T ≤ T_obs) under the null
that FIXES each stratum's fired count and permutes which items within
the stratum are fired — exchangeability within stratum, independence
across strata. The upper tail P(T ≥ T_obs) is the ANTI-STRUCTURED
direction (§6), from the same null.

THE NULL, EXACTLY. Doubling every midrank makes it an integer (a
midrank is the mean of a run of consecutive integer ranks, so twice
it is an integer sum). For one stratum, the distribution of the sum
of m doubled midranks drawn without replacement is computed by the
convex-combination DP
    Q_j(m, s) = (1 − m/j)·Q_{j−1}(m, s) + (m/j)·Q_{j−1}(m−1, s−v_j)
over items j = 1..n — every coefficient in [0, 1], so float64 error
stays ~n·eps and no count ever overflows. T's null is the
convolution of the per-stratum distributions at the observed
composition. This IS exact enumeration in the design's sense (§5.3):
no sampling, no approximation beyond float64 rounding; the fixture
suite proves it against brute-force enumeration on small strata.

The DP is computed to fired-count cap DP_M_CAP per stratum. §5.3's
Monte Carlo clause (1,000,000 permutations at the committed seed) is
the fallback for compositions beyond the cap — with expected |F|
8–12 against a cap of 64 it should never run on real data, but it is
frozen, seeded, and fixture-tested all the same.
"""

from __future__ import annotations

import math

import numpy as np

# ---------------------------------------------------- frozen constants

ALPHA_3D = 0.05          # §5.3: one-sided, the primary's level
DP_M_CAP = 64            # exact-DP per-stratum fired-count cap
MC_PERM_COUNT = 1_000_000  # §5.3's Monte Carlo clause, frozen count
MC_PERM_SEED = 20260818    # frozen at build (doc Open item 3)
THIN_MAX = 4             # §6: any verdict reached on |F| ≤ 4 is THIN


# ------------------------------------------------------- doubled ranks

def doubled_midranks(midranks, idx) -> list:
    """The stratum's midranks × 2 as exact ints, in item order."""
    out = []
    for i in idx:
        d = midranks[i] * 2.0
        r = int(round(d))
        if abs(d - r) > 1e-9:
            raise ValueError(
                f"doubled midrank {d} for item {i} is not an integer — "
                f"midranks must be half-integers by construction")
        out.append(r)
    return out


# ---------------------------------------------------------- the DP

def subset_sum_dist(doubled, m_cap) -> np.ndarray:
    """Q[m, s] = P(sum of a uniform size-m subset's doubled midranks
    = s), for m = 0..min(m_cap, n). Support starts at 0; the array's
    second axis spans 0..max attainable sum for m_cap items."""
    n = len(doubled)
    if n == 0:
        raise ValueError("no items in stratum")
    m_top = min(m_cap, n)
    vmax = sorted(doubled)[::-1][:m_top]
    smax = sum(vmax)
    q = np.zeros((m_top + 1, smax + 1), dtype=np.float64)
    q[0, 0] = 1.0
    for j, v in enumerate(doubled, start=1):
        m_hi = min(j, m_top)
        for m in range(m_hi, 0, -1):
            keep = 1.0 - m / j
            take = m / j
            shifted = np.zeros_like(q[m])
            if v <= smax:
                shifted[v:] = q[m - 1][: smax + 1 - v]
            q[m] = keep * q[m] + take * shifted
    return q


def convolve_composition(per_stratum_q, composition) -> np.ndarray:
    """The null pmf of the DOUBLED statistic at a composition
    {stratum: fired count}: convolution of each stratum's row."""
    pmf = np.array([1.0])
    for key in sorted(per_stratum_q):
        m = composition.get(key, 0)
        q = per_stratum_q[key]
        if m == 0:
            continue
        if m >= q.shape[0]:
            raise ValueError(
                f"stratum {key} fired count {m} exceeds the exact-DP "
                f"cap {q.shape[0] - 1} — the Monte Carlo clause governs")
        row = q[m]
        nz = np.nonzero(row > 0.0)[0]
        if len(nz) == 0:
            raise ValueError(f"stratum {key} DP row {m} carries no mass")
        pmf = np.convolve(pmf, row[: nz[-1] + 1])
    return pmf


def tail_p(pmf, t_doubled) -> tuple:
    """(P(T ≤ t), P(T ≥ t)) for the doubled statistic under `pmf`
    (index = doubled sum). Both tails include the observed point."""
    t = int(t_doubled)
    if t < 0:
        raise ValueError(f"negative doubled statistic {t}")
    upper_from = min(t, len(pmf))
    low = float(pmf[: t + 1].sum()) if t < len(pmf) else 1.0
    high = float(pmf[upper_from:].sum())
    return min(low, 1.0), min(high, 1.0)


# ------------------------------------------------------- the test

def fired_composition(strata, fired_set) -> dict:
    comp = {}
    placed = set()
    for length, idx in sorted(strata.items()):
        s = set(idx)
        f = [i for i in fired_set if i in s]
        comp[str(length)] = len(f)
        placed.update(f)
    missing = set(fired_set) - placed
    if missing:
        raise ValueError(f"fired items {sorted(missing)} are in no "
                         f"stratum")
    return comp


def statistic_T(midranks, fired_set) -> float:
    return float(sum(midranks[i] for i in fired_set))


def stratified_rank_test(values, strata, fired_set, *,
                         alpha=ALPHA_3D, m_cap=DP_M_CAP,
                         mc_count=MC_PERM_COUNT,
                         mc_seed=MC_PERM_SEED) -> dict:
    """The §5.3 primary, end to end: midranks from the frozen values,
    T, exact null at the observed composition (or the frozen MC
    fallback past the DP cap), both one-sided tails."""
    from experiments.exp3d.functional_3d import stratified_midranks

    fired = sorted(set(fired_set))
    mids = stratified_midranks(values, strata)
    comp = fired_composition(strata, fired)
    t_obs = statistic_T(mids, fired)
    t2 = int(round(t_obs * 2.0))
    if abs(t_obs * 2.0 - t2) > 1e-6:
        raise ValueError(f"doubled T {t_obs * 2.0} is not an integer")

    over_cap = [k for k, m in comp.items()
                if m > min(m_cap, len(strata[int(k)]))]
    if not fired:
        return {"T": 0.0, "n_fired": 0, "composition": comp,
                "p_low": None, "p_high": None, "path": "empty",
                "alpha": alpha,
                "note": "no fired items — no rank evidence exists; the "
                        "verdict tree reads |F| < m_min (§6)"}
    if not over_cap:
        per_q = {k: subset_sum_dist(
            doubled_midranks(mids, strata[int(k)]), m_cap)
            for k in comp}
        pmf = convolve_composition(per_q, comp)
        p_low, p_high = tail_p(pmf, t2)
        path = "exact_dp"
    else:
        p_low, p_high = mc_tail_p(values, strata, comp, t2,
                                  mc_count=mc_count, mc_seed=mc_seed)
        path = "mc_1e6"
    return {"T": t_obs, "n_fired": len(fired), "composition": comp,
            "p_low": p_low, "p_high": p_high, "path": path,
            "alpha": alpha, "thin": len(fired) <= THIN_MAX}


def mc_tail_p(values, strata, composition, t2_obs, *,
              mc_count=MC_PERM_COUNT, mc_seed=MC_PERM_SEED) -> tuple:
    """§5.3's Monte Carlo clause: permute within strata at the fixed
    composition, MC_PERM_COUNT times at the frozen seed; add-one
    smoothing on both tails (the permutation-test convention that
    never reports p = 0)."""
    from experiments.exp3d.functional_3d import stratified_midranks

    rng = np.random.default_rng(mc_seed)
    mids = stratified_midranks(values, strata)
    t2 = np.zeros(mc_count, dtype=np.int64)
    chunk = 20_000
    for k in sorted(composition):
        m = composition[k]
        if m == 0:
            continue
        pool = np.array(doubled_midranks(mids, strata[int(k)]),
                        dtype=np.int64)
        if m > len(pool):
            raise ValueError(f"stratum {k} fired count {m} exceeds its "
                             f"{len(pool)} items")
        done = 0
        while done < mc_count:
            c = min(chunk, mc_count - done)
            keys_u = rng.random((c, len(pool)))
            take = np.argpartition(keys_u, m - 1, axis=1)[:, :m]
            t2[done:done + c] += pool[take].sum(axis=1)
            done += c
    low = (int((t2 <= t2_obs).sum()) + 1) / (mc_count + 1)
    high = (int((t2 >= t2_obs).sum()) + 1) / (mc_count + 1)
    return float(low), float(high)


# ---------------------------------------------------------- m_min

def m_min_of(values, strata, *, alpha=ALPHA_3D, m_cap=DP_M_CAP,
             direction="low") -> int:
    """§6: the smallest fired-set size whose BEST-CASE arrangement
    rejects at α — best case over compositions of m across strata AND
    placements within stratum (cheapest midranks for the predicted
    direction; most expensive for the anti direction, disclosed
    separately). Computed exactly from the frozen ranks."""
    from experiments.exp3d.functional_3d import stratified_midranks

    mids = stratified_midranks(values, strata)
    keys = sorted(str(L) for L in strata)
    per_q = {k: subset_sum_dist(doubled_midranks(mids, strata[int(k)]),
                                m_cap) for k in keys}
    sorted_ranks = {k: sorted(doubled_midranks(mids, strata[int(k)]),
                              reverse=(direction == "high"))
                    for k in keys}
    cap = min(m_cap, max(len(idx) for idx in strata.values()))
    for m in range(1, cap + 1):
        best = None
        for comp in _compositions(m, keys, strata):
            t2 = sum(sum(sorted_ranks[k][: comp[k]]) for k in keys)
            pmf = convolve_composition(per_q, comp)
            lo, hi = tail_p(pmf, t2)
            p = lo if direction == "low" else hi
            best = p if best is None else min(best, p)
        if best is not None and best <= alpha:
            return m
    raise ValueError(
        f"no fired-set size up to {cap} rejects at α = {alpha} even in "
        f"the best case — the functional's tie structure is degenerate "
        f"and the design cannot adjudicate (surface this, never guess)")


def _compositions(m, keys, strata):
    """Every way to place m fired items across the strata without
    exceeding a stratum's size."""
    sizes = {k: len(strata[int(k)]) for k in keys}

    def rec(j, left):
        if j == len(keys) - 1:
            if left <= sizes[keys[j]]:
                yield {keys[j]: left}
            return
        for take in range(0, min(left, sizes[keys[j]]) + 1):
            for rest in rec(j + 1, left - take):
                yield {keys[j]: take, **rest}

    for comp in rec(0, m):
        yield {k: comp.get(k, 0) for k in keys}


# ----------------------------------------------- decile bucket p-value

def bucket_tail_p(strata, bucket, fired_set) -> dict:
    """§5.4: |F ∩ B| with its exact tail p under the SAME null (fixed
    per-stratum fired counts, uniform within stratum): per stratum the
    overlap is hypergeometric; the total's distribution is their
    convolution; p = P(overlap ≥ observed)."""
    bucket = set(bucket)
    fired = set(fired_set)
    pmf = np.array([1.0])
    obs = 0
    for length, idx in sorted(strata.items()):
        s = set(idx)
        b = len(bucket & s)
        m = len(fired & s)
        obs += len(bucket & fired & s)
        n = len(idx)
        if m == 0 or b == 0:
            continue
        ks = np.arange(0, min(b, m) + 1)
        probs = np.array([_hyp_pmf(n, b, m, int(k)) for k in ks])
        pmf = np.convolve(pmf, probs)
    p = float(pmf[obs:].sum()) if obs < len(pmf) else 0.0
    return {"observed_overlap": obs, "p_upper": min(p, 1.0),
            "bucket_size": len(bucket)}


def _hyp_pmf(n, b, m, k) -> float:
    """P(overlap = k) drawing m items from n of which b are bucketed."""
    if k > b or m - k > n - b:
        return 0.0
    return math.exp(
        _lchoose(b, k) + _lchoose(n - b, m - k) - _lchoose(n, m))


def _lchoose(n, k) -> float:
    if k < 0 or k > n:
        return float("-inf")
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
