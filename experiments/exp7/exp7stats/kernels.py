"""Exact statistic kernels with NumPy RNG; no floating statistical comparisons.

New statistical RNG proposal: PCG64DXSM + NumPy hypergeometric/permuted,
version pinned. Sampling distribution is the same fixed-margin law as the
integer reference; byte streams intentionally differ and require ratification.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from math import lcm
import numpy as np
from exp7core.inference import groups, mean, eligibility
from .common import require, seed, ALPHA, KERNEL_VERSION

CHUNK = 64
NUMPY_PIN = "2.4.6"


def require_runtime():
    require(np.__version__ == NUMPY_PIN, f"statistical RNG requires numpy {NUMPY_PIN}, got {np.__version__}")
    return {"numpy": np.__version__, "rng": "PCG64DXSM", "kernel": KERNEL_VERSION, "chunk": CHUNK}


def rng(namespace, *parts):
    return np.random.Generator(np.random.PCG64DXSM(seed("statistics-kernel-v2", namespace, *parts)))


def rank_codes(x):
    require(len(x) > 0 and all(type(v) in (int, F) for v in x), "exact predictor values")
    levels = {v: i for i, v in enumerate(sorted(set(x)))}
    return np.asarray([levels[v] for v in x], dtype=np.int64)


class ExactLinear:
    """Integer-limb dot products. No float rounding at randomization ties.

    15-bit coefficients × bounded integer values accumulate in signed int64;
    base carries reconstruct the exact sign of arbitrarily large integers.
    """
    def __init__(self, weights):
        weights = tuple(F(w) for w in weights)
        require(weights and all(w >= 0 for w in weights), "nonnegative exact weights")
        common = lcm(*(w.denominator for w in weights))
        ints = [w.numerator * (common // w.denominator) for w in weights]
        self.base = 1 << 15
        limbs = max(1, (max(ints).bit_length() + 14) // 15)
        self.matrix = np.asarray([[(v >> (15*j)) & (self.base-1) for j in range(limbs)]
                                  for v in ints], dtype=np.int64)
        self.width = len(weights)

    def sign(self, values):
        values = np.asarray(values)
        require(values.ndim == 2 and values.shape[1] == self.width
                and values.dtype.kind in "iu", "exact linear integer matrix")
        values = values.astype(np.int64, copy=False)
        maximum = int(np.max(np.abs(values), initial=0))
        require(maximum * self.width * self.base < (1 << 62), "limb accumulator overflow")
        dots = values @ self.matrix
        carry = np.zeros(len(values), dtype=np.int64)
        nonzero = np.zeros(len(values), dtype=bool)
        for j in range(dots.shape[1]):
            z = dots[:, j] + carry
            nonzero |= z % self.base != 0
            carry = z // self.base
        return np.where(carry < 0, -1, np.where((carry > 0) | nonzero, 1, 0))


@dataclass
class SomersPlan:
    x: tuple
    y: tuple
    strata: tuple

    def __post_init__(self):
        require(len(self.x) == len(self.y) == len(self.strata) and len(self.x) > 0,
                "Somers plan lengths")
        require(all(type(v) is int and 0 <= v <= 26 for v in self.y), "bounded count outcome")
        self.codes = rank_codes(self.x)
        self.blocks, self.denominator = [], 0
        for ix in groups(self.strata):
            ix = np.asarray(ix, dtype=np.int64)
            yy = np.asarray([self.y[i] for i in ix], dtype=np.int64)
            _, ycode = np.unique(yy, return_inverse=True)
            counts = np.bincount(ycode)
            den = (len(ix) * (len(ix)-1) - int(np.sum(counts*(counts-1)))) // 2
            self.denominator += den
            self.blocks.append((ix, ycode, den))

    def numerators(self, codes):
        codes = np.asarray(codes, dtype=np.int64)
        require(codes.ndim == 2 and codes.shape[1] == len(self.x), "rank matrix shape")
        require(np.all(codes >= 0) and np.all(codes < len(self.x)), "rank code bounds")
        total = np.zeros(len(codes), dtype=np.int64)
        for ix, y, den in self.blocks:
            if den == 0:
                continue
            # Remap fixed local rank levels; permitted matrices only permute
            # the original ranks inside each block, preserving these levels.
            levels = np.unique(self.codes[ix])
            x = np.searchsorted(levels, codes[:, ix])
            require(np.all(x < len(levels)) and np.array_equal(levels[x], codes[:, ix]),
                    "rank escaped its stratum")
            ny, nx = int(y.max()) + 1, len(levels)
            idx = (np.arange(len(codes))[:, None] * nx + x) * ny + y[None, :]
            hist = np.bincount(idx.ravel(), minlength=len(codes)*nx*ny).reshape(len(codes), nx, ny)
            prev = np.cumsum(hist, axis=1) - hist
            smaller_y = np.cumsum(prev, axis=2) - prev
            signed = 2*smaller_y + prev - np.sum(prev, axis=2, keepdims=True)
            total += np.sum(hist*signed, axis=(1, 2))
        return total

    def observed(self):
        numerator = int(self.numerators(self.codes[None, :])[0])
        return {"numerator": numerator, "denominator": self.denominator,
                "D": F(numerator, self.denominator) if self.denominator else None,
                "uninformative_blocks": sum(den == 0 for _, _, den in self.blocks),
                "blocks": [{"n": len(ix), "denominator": den,
                            "predictor_constant": len(set(self.codes[ix])) == 1}
                           for ix, _, den in self.blocks]}


def somers(x, y, strata):
    return SomersPlan(tuple(x), tuple(y), tuple(strata)).observed()


def batch_somers(x, outcomes, strata):
    """Many generated outcomes on fixed predictor/strata; exact integer counts."""
    outcomes = np.asarray(outcomes)
    require(outcomes.ndim == 2 and outcomes.shape[1] == len(x)
            and outcomes.dtype.kind in "iu" and np.all(outcomes >= 0)
            and np.all(outcomes <= 26), "batch outcome matrix")
    codes = rank_codes(x)
    numerator = np.zeros(len(outcomes), dtype=np.int64)
    denominator = np.zeros(len(outcomes), dtype=np.int64)
    for group in groups(strata):
        ix = np.asarray(group, dtype=np.int64)
        _, xx = np.unique(codes[ix], return_inverse=True)
        yy = outcomes[:, ix]
        nx, ny = int(xx.max()) + 1, 27
        index = (np.arange(len(outcomes))[:, None]*nx + xx[None, :])*ny + yy
        hist = np.bincount(index.ravel(), minlength=len(outcomes)*nx*ny).reshape(len(outcomes), nx, ny)
        yc = np.sum(hist, axis=1)
        denominator += (len(ix)*(len(ix)-1) - np.sum(yc*(yc-1), axis=1)) // 2
        prev = np.cumsum(hist, axis=1) - hist
        smaller = np.cumsum(prev, axis=2) - prev
        numerator += np.sum(hist*(2*smaller + prev - np.sum(prev, axis=2, keepdims=True)), axis=(1, 2))
    return numerator, denominator


def decision(ge, consumed, B):
    lo, hi = F(ge+1, B+1), F(ge+B-consumed+1, B+1)
    return {"p": lo if consumed == B else None, "p_low": lo, "p_high": hi,
            "reject": hi < ALPHA, "nonreject": lo >= ALPHA,
            "n_ge": int(ge), "consumed": int(consumed), "B": B}


def _mc(compare, B, *, full, chunk=CHUNK):
    require(type(B) is int and B > 0 and type(chunk) is int and chunk > 0, "MC shape")
    ge = consumed = 0
    while consumed < B:
        take = min(chunk, B-consumed)
        signs = compare(take)
        require(len(signs) == take, "MC comparison count")
        ge += int(np.count_nonzero(signs >= 0))
        consumed += take
        d = decision(ge, consumed, B)
        if not full and (d["nonreject"] or d["reject"]):
            break
    return decision(ge, consumed, B)


def forecast(cells, subset, *, B, namespace, full=True, field="x", chunk=CHUNK):
    by = {c.family: c for c in cells}
    require(subset and len(set(subset)) == len(subset) and set(subset) <= set(by), "forecast subset")
    plans = [SomersPlan(tuple(getattr(s, field) for s in by[f].scores), by[f].y, by[f].strata)
             for f in subset]
    observed = [p.observed() for p in plans]
    require(all(r["D"] is not None for r in observed), "undefined forecast subset")
    nums = np.asarray([r["numerator"] for r in observed], dtype=np.int64)
    exact = ExactLinear([F(1, p.denominator) for p in plans])
    streams = [[rng(namespace, "forecast", field, f, j) for j in range(len(p.blocks))]
               for f, p in zip(subset, plans)]
    def compare(batch):
        columns = []
        for p, rr in zip(plans, streams):
            codes = np.broadcast_to(p.codes, (batch, len(p.codes))).copy()
            for (ix, _, _), gen in zip(p.blocks, rr):
                codes[:, ix] = gen.permuted(codes[:, ix], axis=1)
            columns.append(p.numerators(codes))
        return exact.sign(np.stack(columns, axis=1) - nums[None, :])
    out = _mc(compare, B, full=full, chunk=chunk)
    T = mean([r["D"] for r in observed])
    return {**out, "T": T, "fires": T >= F(1, 10) and out["reject"],
            "per_family": dict(zip(subset, observed)), "kernel": KERNEL_VERSION}


def selectivity(cells, subset, *, B, namespace, full=True, chunk=CHUNK):
    by = {c.family: c for c in cells}
    require(subset and len(set(subset)) == len(subset) and set(subset) <= set(by), "selectivity subset")
    tables, weights = [], []
    for f in subset:
        c = by[f]
        for s in c.scores:
            for t in (s.canonical, s.sham):
                if t.supported:
                    tables.append(t)
                    weights.append((F(1, t.m0) + F(1, t.m1)) / (2*len(c.scores)*len(subset)))
    observed = mean([mean(by[f].x) for f in subset])
    if not tables:
        return {**decision(B, B, B), "mean_x": observed, "fires": False,
                "analytic_all_unsupported": True, "kernel": KERNEL_VERSION}
    levels = sorted(set(weights))
    group = {v: j for j, v in enumerate(levels)}
    gids = np.asarray([group[v] for v in weights], dtype=np.int64)
    exact = ExactLinear(levels)
    good = np.asarray([t.n00+t.n10 for t in tables], dtype=np.int64)
    bad = np.asarray([t.m0+t.m1 for t in tables], dtype=np.int64) - good
    draws = np.asarray([t.m0 for t in tables], dtype=np.int64)
    a = np.asarray([t.n00 for t in tables], dtype=np.int64)
    gen = rng(namespace, "selectivity")
    def compare(batch):
        sampled = gen.hypergeometric(good, bad, draws, size=(batch, len(tables)))
        diff = sampled - a
        idx = np.arange(batch)[:, None]*len(levels) + gids[None, :]
        # Every weight is an integer delta <=64, and each group sum <=
        # 4,000*64. These integer-valued float additions are exact below 2**53.
        require(len(tables)*int(np.max(draws)) < (1 << 52), "exact bincount bound")
        grouped = np.bincount(idx.ravel(), weights=diff.ravel(), minlength=batch*len(levels))
        return exact.sign(grouped.astype(np.int64).reshape(batch, len(levels)))
    out = _mc(compare, B, full=full, chunk=chunk)
    return {**out, "mean_x": observed, "fires": observed >= F(1, 20) and out["reject"],
            "kernel": KERNEL_VERSION}


def primary(cells, *, B, namespace, full=True):
    subset, report = eligibility(cells)
    out = {"eligible": subset, "families": report,
           "all_family_mean_x": mean([mean(c.x) for c in cells])}
    if len(subset) < 3:
        return {**out, "state": "UNDETERMINED", "selectivity": None, "forecast": None}
    sel = selectivity(cells, subset, B=B, namespace=namespace, full=full)
    fore = forecast(cells, subset, B=B, namespace=namespace, full=full)
    state = {(True, True): "INPUT-SENSITIVE-FORECAST", (True, False): "SELECTIVE-ONLY",
             (False, True): "ORDER-ONLY", (False, False): "NO-JOINT-SUPPORT"}[sel["fires"], fore["fires"]]
    return {**out, "state": state, "selectivity": sel, "forecast": fore}
