"""S2 — elicitability by exhaustive sampling.

Design doc §3 (S2) and §4 (decision rule):

  At pre-threshold checkpoints, draw N samples per query at temperature; estimate the
  pass rate (pass@k). Sampling budget up to 1e5 samples per query.

  present iff Clopper-Pearson 95% LOWER bound on the pass rate exceeds the empirical
          guessing floor (from an untrained control), while argmax fails.
  absent  iff Clopper-Pearson 95% UPPER bound <= guessing floor. The upper bound is
          reported as a number -- NEVER "zero."

  Predictions: grokking -> present; Lubana-below -> absent (bounded, not zeroed);
  Lubana-above -> present.

Operational choices (recorded in PROGRESS.md, frozen before result-grade data):
  - The pass rate is measured at SAMPLE granularity, pooled across queries:
    rate = (verified samples) / (total samples drawn), n = n_per_query * n_queries.
    This is the quantity the ~3e-5 budget floor (design §4) refers to, and the one
    on which the Clopper-Pearson bound is exact.
  - The guessing floor is passed in (design: estimated from an untrained control
    model); this function does not itself define it. The driver builds it empirically
    from a random-init control under identical sampling.
  - "while argmax fails" (§3) is operationalized as argmax UNRELIABLE: the argmax pass
    rate over the queries is below `argmax_reliable_level` (the frozen 5% below-
    threshold level), NOT "argmax solved zero queries" (which is sample-size-dependent
    and too strict when the model is a hair above chance).
  - `absent` and `present` are mutually exclusive by construction; a middle zone
    (lower <= floor < upper) is neither, and is reported as such (an indeterminate
    campaign that needs more budget) rather than silently coerced.
"""

from __future__ import annotations

import numpy as np

from .schema import SamplingResult
from .stats import clopper_pearson


def elicit_by_sampling(
    sample_fn,
    queries,
    verifier,
    *,
    guessing_floor: float,
    n_per_query: int = 100_000,
    alpha: float = 0.05,
    argmax_fn=None,
    argmax_reliable_level: float = 0.05,
    checkpoint_id: str,
    seed: int,
) -> SamplingResult:
    """Estimate a pass rate by sampling and decide present/absent by CP bounds.

    Parameters
    ----------
    sample_fn : callable(query, n, rng) -> iterable
        Draws n samples for a query. May return a list or a generator; samples are
        consumed one at a time so a generator keeps memory flat at 1e5 budget.
    queries : sequence
        The queries to sample over (e.g. held-out (a, b) pairs).
    verifier : callable(query, sample) -> bool
        True iff the sample is a correct answer for the query.
    guessing_floor : float
        Empirical guessing rate from an untrained control (design §3).
    n_per_query : int
        Samples per query; the campaign budget is n_per_query * len(queries).
    argmax_fn : callable(query) -> sample, optional
        Greedy/argmax decode. If given, `argmax_fails` = (argmax pass rate over the
        queries < argmax_reliable_level). Absent it, argmax_fails defaults True (the
        caller is responsible for sampling at a below-threshold checkpoint).
    argmax_reliable_level : float
        The rate below which argmax counts as "failing" (the frozen 5% level).
    checkpoint_id : str
        Identifier of the checkpoint being sampled.

    Returns a SamplingResult. cp_upper is always populated (never a claimed zero).
    """
    queries = list(queries)
    if not queries:
        raise ValueError("queries is empty")
    rng = np.random.default_rng(seed)

    passes = 0
    n = 0
    for q in queries:
        for sample in sample_fn(q, n_per_query, rng):
            n += 1
            if verifier(q, sample):
                passes += 1

    rate_point = passes / n if n else 0.0
    cp_lower, cp_upper = clopper_pearson(passes, n, alpha=alpha)

    if argmax_fn is not None:
        argmax_rate = sum(bool(verifier(q, argmax_fn(q))) for q in queries) / len(queries)
        argmax_fails = argmax_rate < argmax_reliable_level
    else:
        argmax_fails = True  # unknown; do not let a missing argmax fabricate "present"

    present = bool(cp_lower > guessing_floor and argmax_fails)
    absent = bool(cp_upper <= guessing_floor)

    return SamplingResult(
        present=present,
        absent=absent,
        passes=passes,
        n=n,
        rate_point=rate_point,
        cp_lower=cp_lower,
        cp_upper=cp_upper,
        guessing_floor=guessing_floor,
        argmax_fails=argmax_fails,
        checkpoint_id=checkpoint_id,
    )
