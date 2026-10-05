"""Synthetic probability/rank generators and binomial defect-test primitives.

No production calibration/power orchestrator is implemented here. All callers
must supply replicate counts; miniature tests never execute the proposed grid.
"""
from fractions import Fraction as F
from math import comb, sqrt
from .contract import integer, require
from .inference import mean, somers
from .scoring import Score, Table


def prompt_probabilities(s0, s1, prior, delta):
    """Symmetric conditional alternative p0=prior+delta/2, p1=prior-delta/2."""
    values = tuple(F(v) for v in (s0, s1, prior, delta))
    s0, s1, prior, delta = values
    require(0 <= s0 <= 1 and 0 <= s1 <= 1 and 0 <= prior <= 1, "invalid nuisance")
    p0, p1 = prior + delta / 2, prior - delta / 2
    if not (0 <= p0 <= 1 and 0 <= p1 <= 1):
        return {"status": "UNSUPPORTED", "reason": "conditional probabilities outside [0,1]"}
    rows = ((s0 * p0, s0 * (1 - p0), 1 - s0),
            (s1 * p1, s1 * (1 - p1), 1 - s1))
    require(all(sum(r) == 1 and min(r) >= 0 for r in rows), "probability simplex")
    return {"status": "SUPPORTED", "rows": rows, "delta": delta,
            "availability": (s0, s1)}


def expected_x(s0, s1, delta, k):
    integer(k, 1, 1000000, "k")
    require(0 <= s0 <= 1 and 0 <= s1 <= 1 and -1 <= delta <= 1, "expectation domain")
    return (1 - (1 - F(s0)) ** k) * (1 - (1 - F(s1)) ** k) * F(delta)


def draw_row(probabilities, k, rng):
    require(len(probabilities) == 3 and sum(probabilities) == 1
            and min(probabilities) >= 0, "three-category simplex")
    integer(k, 1, 1000000, "k")
    counts = [0, 0, 0]
    a, b, _ = probabilities
    for _ in range(k):
        u = rng.random()
        counts[0 if u < a else 1 if u < a + b else 2] += 1
    return tuple(counts)


def simulate_table(spec, k, rng):
    require(spec["status"] == "SUPPORTED", "cannot simulate unsupported table")
    a, b = (draw_row(row, k, rng) for row in spec["rows"])
    return Table(a[0], a[1], b[0], b[1], k)


def rankz(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    require(len(order) > 0, "empty ranks")
    ranks, j = [0.0] * len(values), 0
    while j < len(order):
        h = j + 1
        while h < len(order) and values[order[h]] == values[order[j]]:
            h += 1
        for i in order[j:h]:
            ranks[i] = (j + h - 1) / 2
        j = h
    avg = sum(ranks) / len(ranks)
    sd = sqrt(sum((r - avg) ** 2 for r in ranks) / len(ranks))
    return tuple((r - avg) / sd if sd else 0.0 for r in ranks)


def rank_outcome(x, *, n_positive, max_count, rho, rng):
    """Predecessor's family-level rank/noise shape, preserving all predictor ties.

    Tie breaking at rho=1 is randomized, never stable-index ordered. Correlation
    is family-level; statistics/permutations remain within declared strata.
    """
    integer(n_positive, 0, len(x), "positive count")
    integer(max_count, 1, 26, "max nonzero count")
    require(0 <= rho <= 1, "rho")
    z = rankz(x)
    w = [rho * r + sqrt(1 - rho * rho) * rng.gauss(0, 1) for r in z]
    tie = [rng.random() for _ in z]
    order = sorted(range(len(z)), key=lambda i: (-w[i], tie[i]))[:n_positive]
    y = [0] * len(z)
    for j, i in enumerate(order):
        y[i] = max_count - j * max_count // n_positive
    return tuple(y)


def attainable_target(x, strata, *, target, n_positive, max_count, rng_factory,
                      n_cal, iterations, tolerance=0.005):
    """Common-noise bisection of this shape, refusing overshoot/unattainability.

    Production specification additionally requires independent validation draws;
    this helper never asserts power or uses actual selectivity significance.
    """
    integer(n_cal, 1, 1000000, "n_cal")
    integer(iterations, 1, 100, "iterations")
    require(callable(rng_factory), "explicit RNG factory")
    def evaluate(rho):
        vals = []
        for b in range(n_cal):
            y = rank_outcome(x, n_positive=n_positive, max_count=max_count,
                             rho=rho, rng=rng_factory(b))
            d = somers(x, y, strata)["D"]
            if d is None:
                return None
            vals.append(d)
        return float(mean(vals))
    low, high = evaluate(0), evaluate(1)
    if low is None or high is None or high < target - tolerance or low > target + tolerance:
        return {"status": "UNSUPPORTED", "rho": None, "mean_D": None,
                "null_mean_D": low, "shape_ceiling_mean_D": high}
    lo, hi = 0.0, 1.0
    for _ in range(iterations):
        mid = (lo + hi) / 2
        d = evaluate(mid)
        if d is None:
            return {"status": "UNSUPPORTED", "rho": None, "mean_D": None,
                    "reason": "uninformative simulated outcome"}
        if d < target:
            lo = mid
        else:
            hi = mid
    rho = (lo + hi) / 2
    got = evaluate(rho)
    if got is None:
        return {"status": "UNSUPPORTED", "rho": None, "mean_D": None,
                "reason": "uninformative simulated outcome at final evaluation"}
    return {"status": "SUPPORTED" if abs(got - target) <= tolerance else "UNSUPPORTED",
            "rho": rho, "mean_D": got, "null_mean_D": low,
            "shape_ceiling_mean_D": high, "target": target, "tolerance": tolerance}


def binomial_excess(k, n, null_rate):
    """One-sided exact binomial P(X>=k), using integer/rational arithmetic."""
    integer(n, 1, 1000000, "binomial n")
    integer(k, 0, n, "binomial k")
    p = F(null_rate)
    require(0 <= p <= 1, "binomial rate")
    return sum((F(comb(n, j)) * p ** j * (1 - p) ** (n - j)
                for j in range(k, n + 1)), F(0))


def binomial_interval(k, n, *, alpha=0.05):
    """Clopper-Pearson by bisection, floating log-PMF sums to avoid underflow."""
    from math import exp, lgamma, log, log1p
    integer(n, 1, 1000000, "binomial n")
    integer(k, 0, n, "binomial k")
    require(0 < alpha < 1, "interval alpha")
    def cdf(j, p):
        if j < 0:
            return 0.0
        if j >= n:
            return 1.0
        if p == 0:
            return 1.0
        if p == 1:
            return 0.0
        terms = [lgamma(n + 1) - lgamma(t + 1) - lgamma(n - t + 1)
                 + t * log(p) + (n - t) * log1p(-p) for t in range(j + 1)]
        m = max(terms)
        return min(1.0, exp(m) * sum(exp(v - m) for v in terms))
    def solve(j, target):
        lo, hi = 0.0, 1.0
        for _ in range(64):
            mid = (lo + hi) / 2
            if cdf(j, mid) > target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    return (0.0 if k == 0 else solve(k - 1, 1 - alpha / 2),
            1.0 if k == n else solve(k, alpha / 2))
