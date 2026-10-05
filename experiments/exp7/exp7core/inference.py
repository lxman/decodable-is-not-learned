"""Exact-rational reference inference; efficient O(n log n) Somers counts.

Randomizations are deliberately scalar reference code. Production batch
acceleration must be independently differential-tested against these functions.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import comb
import random
from .contract import integer, require, seed
from .scoring import Table, Score


def mean(values):
    require(len(values) > 0, "empty mean")
    return sum(values, F(0)) / len(values)


def groups(strata):
    out = defaultdict(list)
    for i, s in enumerate(strata):
        out[s].append(i)
    return [out[s] for s in sorted(out, key=repr)]


def somers(x, y, strata):
    require(len(x) == len(y) == len(strata) and len(x) > 0, "Somers lengths")
    require(all(type(v) in (int, F) for v in x), "predictor must be exact finite rational")
    require(all(type(v) is int for v in y), "outcome must be integer")
    numerator = denominator = 0
    blocks = []
    for ix in groups(strata):
        levels = sorted({y[i] for i in ix})
        ranks = {v: j + 1 for j, v in enumerate(levels)}
        tree = [0] * (len(levels) + 1)
        def prefix(j):
            n = 0
            while j:
                n += tree[j]
                j -= j & -j
            return n
        def add(j):
            while j < len(tree):
                tree[j] += 1
                j += j & -j
        ordered = sorted(ix, key=lambda i: x[i])
        bnum, seen, j = 0, 0, 0
        while j < len(ordered):
            h = j + 1
            while h < len(ordered) and x[ordered[h]] == x[ordered[j]]:
                h += 1
            for i in ordered[j:h]:
                r = ranks[y[i]]
                bnum += prefix(r - 1) - (seen - prefix(r))
            for i in ordered[j:h]:
                add(ranks[y[i]])
            seen += h - j
            j = h
        den = comb(len(ix), 2) - sum(comb(n, 2) for n in Counter(y[i] for i in ix).values())
        numerator += bnum
        denominator += den
        blocks.append({"n": len(ix), "numerator": bnum, "denominator": den,
                       "predictor_constant": len({x[i] for i in ix}) == 1})
    return {"numerator": numerator, "denominator": denominator,
            "D": F(numerator, denominator) if denominator else None,
            "blocks": tuple(blocks),
            "uninformative_blocks": sum(b["denominator"] == 0 for b in blocks)}


@dataclass(frozen=True)
class Cell:
    family: str
    ids: tuple
    scores: tuple
    y: tuple
    strata: tuple

    def __post_init__(self):
        n = len(self.ids)
        require(n > 0 and len(set(self.ids)) == n, "pair IDs")
        require(len(self.scores) == len(self.y) == len(self.strata) == n, "cell coverage")
        require(all(isinstance(s, Score) for s in self.scores), "score type")
        require(all(type(v) is int and 0 <= v <= 26 for v in self.y), "outcome range")

    @property
    def x(self):
        return tuple(s.x for s in self.scores)


def eligibility(cells):
    require(len(cells) > 0 and len({c.family for c in cells}) == len(cells), "family coverage")
    keep, report = [], {}
    for c in cells:
        reading = somers(c.x, c.y, c.strata)
        positives = sum(v > 0 for v in c.y)
        reasons = []
        if positives < 20:
            reasons.append("fewer than 20 distinct joint-positive pairs")
        if reading["denominator"] == 0:
            reasons.append("no outcome-informative within-stratum comparison")
        if not reasons:
            keep.append(c.family)
        report[c.family] = {**reading, "n_positive": positives,
                            "constant_x": len(set(c.x)) == 1,
                            "mean_x": mean(c.x), "excluded_reasons": tuple(reasons)}
    return tuple(keep), report


def selected(cells, subset):
    require(len(subset) > 0 and len(set(subset)) == len(subset), "subset")
    by = {c.family: c for c in cells}
    require(set(subset) <= set(by), "missing subset family")
    return tuple(by[f] for f in subset)


def aggregate_D(cells, subset, *, field="x"):
    ds = []
    for c in selected(cells, subset):
        x = tuple(getattr(s, field) for s in c.scores)
        d = somers(x, c.y, c.strata)["D"]
        if d is None:
            return None
        ds.append(d)
    return mean(ds)


@lru_cache(maxsize=40000)
def hypergeom_weights(m0, m1, K):
    integer(m0, 0, 1000000, "m0")
    integer(m1, 0, 1000000, "m1")
    integer(K, 0, m0 + m1, "column margin")
    lo, hi = max(0, K - m1), min(m0, K)
    ws = tuple(comb(K, a) * comb(m0 + m1 - K, m0 - a) for a in range(lo, hi + 1))
    require(sum(ws) == comb(m0 + m1, m0), "hypergeometric normalization")
    return lo, ws


def randomized_table(table, rng):
    m0, m1, K = table.m0, table.m1, table.n00 + table.n10
    if not table.supported:
        return table  # x is identically zero for every such table.
    lo, ws = hypergeom_weights(m0, m1, K)
    ticket = rng.randrange(sum(ws))
    for j, w in enumerate(ws):
        ticket -= w
        if ticket < 0:
            a = lo + j
            return Table(a, m0 - a, K - a, m1 - K + a, table.k)
    raise AssertionError("unreachable hypergeometric inverse CDF")


def selectivity_test(cells, subset, *, B=10000, namespace):
    integer(B, 1, 10000000, "randomization count")
    cs = selected(cells, subset)
    observed = mean([mean(c.x) for c in cs])
    rng = random.Random(seed("selectivity", namespace, tuple(subset)))
    ge = 0
    for _ in range(B):
        null = mean([mean([(randomized_table(s.canonical, rng).x +
                            randomized_table(s.sham, rng).x) / 2
                           for s in c.scores]) for c in cs])
        ge += null >= observed
    return {"mean_x": observed, "p": F(1 + ge, 1 + B), "n_ge": ge, "B": B}


def permutation_test(cells, subset, *, B=10000, namespace, field="x"):
    integer(B, 1, 10000000, "permutation count")
    cs = selected(cells, subset)
    observed = aggregate_D(cs, subset, field=field)
    require(observed is not None, "undefined forecast")
    rng = random.Random(seed("forecast", namespace, tuple(subset), field))
    plans = [(c, groups(c.strata), tuple(getattr(s, field) for s in c.scores)) for c in cs]
    ge = 0
    for _ in range(B):
        ds = []
        for c, blocks, original in plans:
            x = list(original)
            for ix in blocks:
                values = [original[i] for i in ix]
                rng.shuffle(values)
                for i, v in zip(ix, values):
                    x[i] = v
            ds.append(somers(x, c.y, c.strata)["D"])
        ge += mean(ds) >= observed
    return {"T": observed, "p": F(1 + ge, 1 + B), "n_ge": ge, "B": B}


def selectivity_fires(result):
    return result["mean_x"] >= F(1, 20) and result["p"] < F(1, 200)


def forecast_fires(result):
    return result["T"] >= F(1, 10) and result["p"] < F(1, 200)


def primary(cells, *, namespace, B=10000):
    subset, families = eligibility(cells)
    out = {"eligible": subset, "families": families,
           "all_family_mean_x": mean([mean(c.x) for c in cells]),
           "selective": False, "forecast": False}
    if len(subset) < 3:
        return {**out, "state": "UNDETERMINED", "selectivity": None, "order": None}
    sel = selectivity_test(cells, subset, B=B, namespace=namespace)
    fore = permutation_test(cells, subset, B=B, namespace=namespace)
    a, b = selectivity_fires(sel), forecast_fires(fore)
    state = {(True, True): "INPUT-SENSITIVE-FORECAST", (True, False): "SELECTIVE-ONLY",
             (False, True): "ORDER-ONLY", (False, False): "NO-JOINT-SUPPORT"}[a, b]
    return {**out, "state": state, "selectivity": sel, "order": fore,
            "selective": a, "forecast": b}
