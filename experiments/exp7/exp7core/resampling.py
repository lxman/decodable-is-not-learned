"""Pair-bundle bootstrap primitives; no independent resampling of arms/models."""
from fractions import Fraction as F
import random
from .contract import integer, require, seed


def bundle_indices(family_sizes, *, B=1000, namespace):
    integer(B, 1, 10000000, "bootstrap replicates")
    require(type(family_sizes) is dict and family_sizes, "family sizes")
    for n in family_sizes.values():
        integer(n, 1, 1000000, "family size")
    for b in range(B):
        out = {}
        for f in sorted(family_sizes):
            rng = random.Random(seed("pair-bootstrap", namespace, b, f))
            n = family_sizes[f]
            out[f] = tuple(rng.randrange(n) for _ in range(n))
        yield out


def take_bundle(bundle, indices):
    """bundle is an aligned tuple of complete per-pair objects, never four arrays."""
    require(type(bundle) is tuple and len(bundle) > 0, "nonempty tuple bundle")
    require(type(indices) is tuple and len(indices) == len(bundle), "bootstrap coverage")
    require(all(type(i) is int and 0 <= i < len(bundle) for i in indices), "bootstrap index")
    return tuple(bundle[i] for i in indices)


def quantile(values, probability):
    require(values and F(0) <= probability <= F(1), "quantile arguments")
    xs = sorted(values)
    h = probability * (len(xs) - 1)
    lo = h.numerator // h.denominator
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (h - lo) * (xs[hi] - xs[lo])


def interval(values):
    """Undefined-D replicates are omitted AND counted, never replaced by zero."""
    valid = [v for v in values if v is not None]
    return {"B": len(values), "defined": len(valid), "undefined": len(values) - len(valid),
            "low": quantile(valid, F(1, 40)) if valid else None,
            "high": quantile(valid, F(39, 40)) if valid else None}


def paired_difference(left, right):
    require(len(left) == len(right), "paired bootstrap lengths")
    return interval([a - b if a is not None and b is not None else None
                     for a, b in zip(left, right)])
