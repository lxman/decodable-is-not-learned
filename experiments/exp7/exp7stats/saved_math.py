"""Re-derive saved arithmetic from bounded retained counts; never draw randomness.

MC exceedance counts are authenticated inputs, not reconstructed RNG history.
We derive their finite bounds and deterministic impossibility constraints.
"""
from functools import lru_cache
from fractions import Fraction as F
from math import sqrt
import zlib
import numpy as np
from exp7core.inference import mean, groups
from .common import require, digest, dumps, FAMILIES, PREDICTORS
from .data import predictor_support
from .kernels import batch_somers, decision

VERSION = 2
BOUND_KEYS = ("p", "p_low", "p_high", "n_ge", "consumed", "B")


def equal(got, expected, label):
    require(digest(got) == digest(expected), label)


def pack(values):
    a = np.asarray(values)
    require(a.dtype.kind in "iu" and np.all(a >= 0) and np.all(a <= 255), "packed byte domain")
    return zlib.compress(a.astype(np.uint8).tobytes(), 9).hex()


def unpack(text, size):
    require(type(text) is str and len(text) <= 2*(size+1024), "packed count extent")
    try:
        data = bytes.fromhex(text)
        obj = zlib.decompressobj()
        raw = obj.decompress(data, size+1)
        require(len(raw) == size and obj.eof and not obj.unused_data and not obj.unconsumed_tail,
                "packed count coverage/trailing data")
    except (ValueError, zlib.error) as exc:
        require(False, f"malformed packed arithmetic counts: {exc}")
    return np.frombuffer(raw, dtype=np.uint8)


def scatter(values):
    defined = [v for v in values if v is not None]
    require(all(type(v) in (int, F) and -1 <= v <= 1 for v in defined), "D domain")
    avg = mean(defined) if defined else None
    variance = mean([(v-avg)**2 for v in defined]) if defined else None
    return {"defined": len(defined), "undefined": len(values)-len(defined), "mean_defined": avg,
            "population_variance": variance, "population_sd": sqrt(float(variance)) if variance is not None else None}


def predictor_geometry(predictors):
    """Caller supplies independently verified/re-scored sealed Predictors, never record support."""
    return {"schema": "exp7.predictor-geometry.v1", "predictors": {
        p: {f: {"x": tuple(s.x for s in predictors[p].family(f)),
                "strata": tuple(dumps(s).decode().strip() for s in dict(predictors[p].strata)[f])}
            for f in FAMILIES} for p in PREDICTORS},
        "support": {p: predictor_support(predictors[p]) for p in PREDICTORS}}


def validate_geometry(geometry, *, production):
    require(type(geometry) is dict and set(geometry) == {"schema", "predictors", "support"}
            and geometry["schema"] == "exp7.predictor-geometry.v1", "independent predictor geometry required")
    require(set(geometry["predictors"]) == set(PREDICTORS) and set(geometry["support"]) == set(PREDICTORS), "geometry predictors")
    for p in PREDICTORS:
        require(set(geometry["predictors"][p]) == set(FAMILIES), "geometry families")
        for f, row in geometry["predictors"][p].items():
            require(set(row) == {"x", "strata"}, "geometry row")
            n = len(row["x"])
            require((n == 500 if production else 20 <= n <= 500) and len(row["strata"]) == n, "geometry coverage")
            require(all(type(v) in (int, F) and -1 <= v <= 1 for v in row["x"]), "geometry x domain")
            require(all(type(s) is str and s for s in row["strata"]), "geometry strata IDs")
    return geometry


@lru_cache(maxsize=128)
def family_counts(x, strata, packed, nrep, n_positive, max_count, rho_one):
    n = len(x)
    yy = unpack(packed, nrep*n).reshape(nrep, n).astype(np.int64)
    expected = [0]*(n-n_positive) + [max_count-j*max_count//n_positive for j in range(n_positive)]
    require(0 < n_positive <= n and 1 <= max_count <= 26 and
            np.array_equal(np.sort(yy, axis=1), np.broadcast_to(sorted(expected), yy.shape)), "saved outcome count shape")
    if rho_one:
        order = sorted(range(n), key=lambda i: x[i])
        for i, j in zip(order, order[1:]):
            if x[i] < x[j]:
                # Across distinct x groups every y in lower group <= every y in higher.
                left = [k for k in order if x[k] == x[i]]
                right = [k for k in order if x[k] == x[j]]
                require(np.all(yy[:, left].max(axis=1) <= yy[:, right].min(axis=1)), "rho1 outcome violates rank signal")
    num, den = batch_somers(x, yy, strata)
    # Fixed-margin rearrangement extrema under within-block predictor permutation.
    hi, lo = yy.copy(), yy.copy()
    for ix in groups(strata):
        order = sorted(ix, key=lambda i: x[i])
        sorted_y = np.sort(yy[:, ix], axis=1)
        hi[:, order], lo[:, order] = sorted_y, sorted_y[:, ::-1]
    high, _ = batch_somers(x, hi, strata)
    low, _ = batch_somers(x, lo, strata)
    uninformative = np.zeros(nrep, dtype=np.int64)
    for ix in groups(strata):
        uninformative += np.max(yy[:, ix], axis=1) == np.min(yy[:, ix], axis=1)
    return tuple(tuple(int(v) for v in a) for a in (num, den, low, high, uninformative))


def outcome_summary(families, subset, outcomes, nrep, n_positive, max_count, *, rho_one=False):
    require(type(outcomes) is dict and set(outcomes) == set(subset), "saved outcome families")
    counts = {f: family_counts(tuple(families[f]["x"]), tuple(families[f]["strata"]), outcomes[f],
                               nrep, n_positive, max_count, rho_one) for f in subset}
    ds, bounds, eligibility = [], [], []
    for b in range(nrep):
        keep = tuple(f for f in subset if n_positive >= 20 and counts[f][1][b] > 0)
        defined = keep == tuple(subset)
        ds.append(mean([F(counts[f][0][b], counts[f][1][b]) for f in subset]) if defined else None)
        bounds.append({"low": mean([F(counts[f][2][b], counts[f][1][b]) for f in subset]) if defined else None,
                       "high": mean([F(counts[f][3][b], counts[f][1][b]) for f in subset]) if defined else None})
        eligibility.append({"eligible": keep, "uninformative": {f: counts[f][4][b] for f in subset}})
    summary = {"outcomes": outcomes, "Ds": ds, "mean_D": None if any(d is None for d in ds) else mean(ds),
               "scatter": scatter(ds), "uninformative_datasets": sum(d is None for d in ds)}
    return summary, eligibility, bounds


def checked_bound(bound, B, *, all_ge=False):
    require(type(bound) is dict and set(bound) == set(BOUND_KEYS), "saved MC fields")
    ge, used = bound["n_ge"], bound["consumed"]
    require(type(ge) is int and type(used) is int and 0 <= ge <= used <= B and used > 0
            and type(bound["B"]) is int and bound["B"] == B, "saved MC count domain")
    d = decision(ge, used, B)
    equal(bound, {k: d[k] for k in BOUND_KEYS}, "saved finite-p arithmetic")
    require(d["reject"] or d["nonreject"], "unfinished MC decision")
    require(not all_ge or ge == used, "MC exceedance count impossible under fixed geometry")
    return d
