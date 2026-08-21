"""The preregistered statistics (design §5.3–§5.5) — Experiment 3e's
inference machinery, model-free and data-free: every function here is
a pure map from (frozen partition, fired sets, counts) to numbers,
exact by integer combinatorics, no Monte Carlo anywhere.

THE PRIMARY (§5.3). X = |F ∩ non-reachable| given n = |F|, under the
null that the reachability label is exchangeable across the 45 items
with respect to firing: X ~ Hypergeometric(N = 45, K = 13, n).
p_low = P(X ≤ x) is the SHORTCUT direction (non-reachable under-
fires), p_high = P(X ≥ x) the ANTI direction; α = .05 one-sided each
way; both tails include the observed point. m_min = the smallest n
whose best-case arrangement (X = 0) rejects; THIN on n ≤ THIN_MAX.

THE COUNT-WEIGHTED SECONDARY (§5.4). T_c = total new fires on the
non-reachable items; null = a uniformly random choice of which K of
the N items carry the "non-reachable" label, CONDITIONAL on every
item's own count — an integer subset-count DP over items (exact), so
a hot item produces a correspondingly heavy null.

THE DESIGNATION-EXCHANGEABILITY NULL (§5.5). For every arm item a
count vector (r_i, c_i1, …, c_i|M_i|); under "the reverse is nothing
special among its matched one-edit outputs" which entry is designated
the reverse is uniform over the 1 + |M_i| slots, independently across
items, conditional on the vector. T_s = Σ_i r_i; p = P(T_s ≥ T_obs)
by an exact integer convolution over items. m_s,min = the smallest
matched-event total whose best case rejects: the best case is one
event per item on the reverse of the smallest-θ items (proof in
m_s_min_of's docstring), so best_p(E) = Π of the E smallest θ_i.
"""

from __future__ import annotations

import math
from fractions import Fraction

# ---------------------------------------------------- frozen constants

ALPHA_3E = 0.05          # §5.3: one-sided, each direction
THIN_MAX = 10            # §6: any verdict reached on n ≤ 10 is THIN
N_SUBSET = 45            # §3: the committed len-4 repeat class
K_NON_REACHABLE = 13     # §5.1: the non-reachable count
SPECIFICITY_ANNOTATIONS = ("DIRECTED", "MISFIRE-RATE", "SPARSE")


# ------------------------------------------------------ hypergeometric

def hypergeom_pmf(N: int, K: int, n: int) -> list:
    """P(X = x) for x = 0..n as exact Fractions; X = number of the n
    drawn items (without replacement) that carry the K-label."""
    if not (0 <= K <= N and 0 <= n <= N):
        raise ValueError(f"hypergeometric parameters N={N}, K={K}, n={n} "
                         f"out of range")
    tot = math.comb(N, n)
    return [Fraction(math.comb(K, x) * math.comb(N - K, n - x), tot)
            for x in range(n + 1)]


def hypergeom_tails(N: int, K: int, n: int, x: int) -> tuple:
    """(P(X ≤ x), P(X ≥ x)), both including the observed point."""
    if not (0 <= x <= n and x <= K and n - x <= N - K):
        raise ValueError(f"X = {x} is impossible for N={N}, K={K}, n={n}")
    pmf = hypergeom_pmf(N, K, n)
    return (float(sum(pmf[: x + 1])), float(sum(pmf[x:])))


def m_min_of(N: int, K: int, alpha: float) -> int:
    """Smallest n at which X = 0 rejects in the SHORTCUT direction:
    C(N−K, n)/C(N, n) ≤ α. None if no n ≤ N−K does."""
    for n in range(1, N - K + 1):
        if Fraction(math.comb(N - K, n), math.comb(N, n)) <= Fraction(alpha):
            return n
    return None


def m_min_anti_of(N: int, K: int, alpha: float) -> int:
    """Smallest n at which X = n (every fired item non-reachable)
    rejects in the ANTI direction: C(K, n)/C(N, n) ≤ α. Disclosed,
    never gating (§5.3's m_min is the SHORTCUT-direction one)."""
    for n in range(1, K + 1):
        if Fraction(math.comb(K, n), math.comb(N, n)) <= Fraction(alpha):
            return n
    return None


def primary_test(n_fired: int, x_non_reachable: int, *, N=N_SUBSET,
                 K=K_NON_REACHABLE, alpha=ALPHA_3E,
                 thin_max=THIN_MAX) -> dict:
    """§5.3 on an observed fired set: both tails, the THIN flag, and
    the null expectation. No fires → no p (the UNINFORMATIVE branch
    owns that case)."""
    if n_fired == 0:
        return {"n_fired": 0, "x_non_reachable": 0, "p_low": None,
                "p_high": None, "alpha": alpha, "thin": True,
                "expected_x_under_null": 0.0,
                "null": f"Hypergeometric(N={N}, K={K}, n=0)"}
    low, high = hypergeom_tails(N, K, n_fired, x_non_reachable)
    return {"n_fired": int(n_fired), "x_non_reachable": int(x_non_reachable),
            "p_low": low, "p_high": high, "alpha": alpha,
            "thin": bool(n_fired <= thin_max),
            "expected_x_under_null": n_fired * K / N,
            "null": f"Hypergeometric(N={N}, K={K}, n={n_fired})"}


def best_case_table(N: int, K: int, n_max: int) -> list:
    """For n = 1..n_max: p_low at X = 0 (SHORTCUT's best case) and
    p_high at X = min(n, K) (ANTI's best case)."""
    out = []
    for n in range(1, n_max + 1):
        x_hi = min(n, K)
        out.append({"n": n,
                    "p_low_at_x0": hypergeom_tails(N, K, n, 0)[0],
                    "p_high_at_all_non_reachable":
                        hypergeom_tails(N, K, n, x_hi)[1]
                        if n - x_hi <= N - K else None})
    return out


def calibration_table(N: int, K: int, ns, alpha: float) -> list:
    """Realized null sizes at each n: P(p_low ≤ α), P(p_high ≤ α),
    and their union (the two worlds are disjoint events, so the union
    is the sum) — 3d §7's corrected calibration sentence, printed."""
    out = []
    for n in ns:
        pmf = hypergeom_pmf(N, K, n)
        size_low = Fraction(0)
        size_high = Fraction(0)
        for x in range(n + 1):
            if pmf[x] == 0:
                continue
            if sum(pmf[: x + 1]) <= Fraction(alpha):
                size_low += pmf[x]
            if sum(pmf[x:]) <= Fraction(alpha):
                size_high += pmf[x]
        out.append({"n": n, "size_low": float(size_low),
                    "size_high": float(size_high),
                    "size_union": float(size_low + size_high)})
    return out


# ---------------------------------------------- count-weighted DP null

def count_weighted_null(counts, K: int) -> dict:
    """{sum: number of K-subsets of the items with that count sum} —
    exact integer subset-count DP over items."""
    counts = [int(c) for c in counts]
    if any(c < 0 for c in counts):
        raise ValueError("negative fire count")
    if not (0 <= K <= len(counts)):
        raise ValueError(f"K = {K} against {len(counts)} items")
    # dp[m] = {sum: ways} over the items processed so far
    dp = [dict() for _ in range(K + 1)]
    dp[0][0] = 1
    for c in counts:
        for m in range(min(K, len(counts)), 0, -1):
            src = dp[m - 1]
            if not src:
                continue
            dst = dp[m]
            for s, w in src.items():
                dst[s + c] = dst.get(s + c, 0) + w
    return dict(sorted(dp[K].items()))


def count_weighted_test(counts, non_reachable_items) -> dict:
    """§5.4's count-weighted contrast: T_c = Σ counts over the
    non-reachable items; p_low = P(T_c ≤ obs), p_high = P(T_c ≥ obs)
    under the label permutation conditional on every item's count."""
    counts = [int(c) for c in counts]
    labels = sorted(set(int(i) for i in non_reachable_items))
    if len(labels) != len(non_reachable_items) or \
            any(i < 0 or i >= len(counts) for i in labels):
        raise ValueError(f"non-reachable labels {non_reachable_items} "
                         f"are not distinct item indices into "
                         f"{len(counts)} items")
    K = len(labels)
    t_obs = sum(counts[i] for i in labels)
    dist = count_weighted_null(counts, K)
    tot = sum(dist.values())
    low = Fraction(sum(w for s, w in dist.items() if s <= t_obs), tot)
    high = Fraction(sum(w for s, w in dist.items() if s >= t_obs), tot)
    return {"T_obs": int(t_obs), "p_low": float(low), "p_high": float(high),
            "K": K, "n_items": len(counts),
            "total_fires": int(sum(counts)),
            "null": "uniform choice of which K items carry the "
                    "non-reachable label, conditional on every item's "
                    "own count (exact subset-count DP)"}


# ------------------------------------------ designation-exchangeability

def designation_null(vectors) -> dict:
    """{sum: number of designation tuples with that sum}: one slot per
    item chosen among its 1 + |M_i| count values — exact integer
    convolution."""
    dist = {0: 1}
    for v in vectors:
        nxt: dict[int, int] = {}
        for s, w in dist.items():
            for c in v:
                nxt[s + int(c)] = nxt.get(s + int(c), 0) + w
        dist = nxt
    return dict(sorted(dist.items()))


def designation_test(vectors) -> dict:
    """§5.5: T_s = Σ_i r_i (the FIRST entry of every vector is the
    reverse's count); one-sided p = P(T_s ≥ T_obs) under designation
    exchangeability. Every vector must carry at least one competitor
    slot (an item with |M| = 0 sits out the arm by construction)."""
    vecs = []
    for v in vectors:
        v = tuple(int(c) for c in v)
        if len(v) < 2:
            raise ValueError(f"count vector {v} carries no competitor "
                             f"slot — an item with |M| = 0 sits out "
                             f"the arm (§5.1)")
        if any(c < 0 for c in v):
            raise ValueError("negative emission count")
        vecs.append(v)
    t_obs = sum(v[0] for v in vecs)
    events = sum(sum(v) for v in vecs)
    if not vecs or events == 0:
        return {"T_obs": int(t_obs), "p": 1.0, "events": int(events),
                "n_items": len(vecs),
                "null": "designation exchangeability (exact)"}
    dist = designation_null(vecs)
    tot = sum(dist.values())
    p = Fraction(sum(w for s, w in dist.items() if s >= t_obs), tot)
    return {"T_obs": int(t_obs), "p": float(p), "events": int(events),
            "n_items": len(vecs),
            "reverse_share": (t_obs / events) if events else None,
            "null": "for each item one of its 1+|M| count values is "
                    "designated 'the reverse' uniformly at random "
                    "(exact convolution)"}


def best_case_specificity_table(m_sizes, e_max: int) -> list:
    """best_p(E) = Π of the E smallest θ_i, θ_i = 1/(1 + |M_i|).

    Why this is the best case (§5.5 m_s,min): for any configuration,
    {every item designates its reverse value} ⊆ {T_s ≥ T_obs}, so
    p ≥ Π θ_i over the items whose vector is non-constant. Moving all
    of an item's events onto its reverse gives a configuration whose
    p is EXACTLY Π θ_i over the items carrying events, which is ≤ the
    original bound; and with E events that product is smallest when
    the events sit one each on the E smallest-θ items. The fixture
    suite proves this against exhaustive enumeration on a small
    instance."""
    thetas = sorted(Fraction(1, 1 + int(m)) for m in m_sizes)
    out = []
    for e in range(1, e_max + 1):
        if e > len(thetas):
            break
        p = Fraction(1)
        for th in thetas[:e]:
            p *= th
        out.append({"events": e, "best_p": float(p)})
    return out


def m_s_min_of(m_sizes, alpha: float):
    """Smallest matched-event total whose best case rejects at α;
    None if even one event per arm item cannot."""
    for row in best_case_specificity_table(m_sizes, len(m_sizes)):
        if Fraction(row["best_p"]) <= Fraction(alpha) or \
                row["best_p"] <= alpha:
            return row["events"]
    return None


def specificity_annotation(*, p, events: int, m_s_min: int,
                           alpha=ALPHA_3E) -> str:
    """§5.5's annotation tree, mechanical: DIRECTED on rejection,
    SPARSE below m_s,min, MISFIRE-RATE otherwise."""
    if p is not None and p <= alpha:
        return "DIRECTED"
    if m_s_min is None or events < m_s_min:
        return "SPARSE"
    return "MISFIRE-RATE"
