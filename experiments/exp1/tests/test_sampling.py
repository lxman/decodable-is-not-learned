"""M2 planted-signal tests for S2 (exhaustive sampling).

Bernoulli oracles with a KNOWN true rate stand in for a model: a nonzero rate above
the guessing floor must read 'present'; a genuinely zero rate must read 'absent' with
a finite, positive Clopper-Pearson upper bound -- never a claimed zero (design §4).
"""

import pytest

from signatures.sampling import elicit_by_sampling


def _bernoulli_sampler(true_rate):
    """sample_fn(query, n, rng) -> n draws; a draw 'passes' iff it equals 'ok'."""
    def sample_fn(_query, n, rng):
        return ["ok" if rng.random() < true_rate else "no" for _ in range(n)]
    return sample_fn


def _verifier(_query, sample):
    return sample == "ok"


def test_present_when_rate_above_floor_and_argmax_fails():
    res = elicit_by_sampling(
        _bernoulli_sampler(0.05), queries=["q"], verifier=_verifier,
        guessing_floor=1e-3, n_per_query=5000,
        argmax_fn=lambda q: "no",  # greedy is wrong
        checkpoint_id="ck", seed=0,
    )
    assert res.present is True
    assert res.absent is False
    assert res.cp_lower > 1e-3
    assert res.argmax_fails is True


def test_absent_on_zero_rate_reports_finite_upper_bound():
    res = elicit_by_sampling(
        _bernoulli_sampler(0.0), queries=["q"], verifier=_verifier,
        guessing_floor=1e-3, n_per_query=10_000,
        argmax_fn=lambda q: "no",
        checkpoint_id="ck", seed=0,
    )
    assert res.absent is True
    assert res.present is False
    assert res.passes == 0
    assert res.cp_upper > 0.0            # never a claimed zero
    assert res.cp_upper <= 1e-3          # bounded below the floor -> 'absent'
    assert res.rate_point == 0.0


def test_present_requires_argmax_failure():
    """A nonzero rate is not 'present' if greedy already solves it (capability exists)."""
    res = elicit_by_sampling(
        _bernoulli_sampler(0.05), queries=["q"], verifier=_verifier,
        guessing_floor=1e-3, n_per_query=5000,
        argmax_fn=lambda q: "ok",  # greedy is correct (rate 1.0 >= 5%)
        checkpoint_id="ck", seed=0,
    )
    assert res.argmax_fails is False
    assert res.present is False


def test_argmax_fails_is_rate_based_not_zero_based():
    """A few queries solved by argmax below the reliability level still counts as
    'argmax fails' — the fix for the grokking below-threshold case (~2% argmax)."""
    # 100 queries; argmax solves exactly 2 (2% < 5% level) -> argmax_fails True.
    solved = set(range(2))
    res = elicit_by_sampling(
        _bernoulli_sampler(0.05), queries=list(range(100)), verifier=_verifier,
        guessing_floor=1e-3, n_per_query=500,
        argmax_fn=lambda q: "ok" if q in solved else "no",
        argmax_reliable_level=0.05, checkpoint_id="ck", seed=0,
    )
    assert res.argmax_fails is True     # 2% < 5%, so argmax is unreliable
    assert res.present is True          # and sampling clears the floor
    # Raise the count above the level and it flips.
    solved2 = set(range(10))            # 10% >= 5%
    res2 = elicit_by_sampling(
        _bernoulli_sampler(0.05), queries=list(range(100)), verifier=_verifier,
        guessing_floor=1e-3, n_per_query=500,
        argmax_fn=lambda q: "ok" if q in solved2 else "no",
        argmax_reliable_level=0.05, checkpoint_id="ck", seed=0,
    )
    assert res2.argmax_fails is False
    assert res2.present is False


def test_budget_scales_with_query_count():
    res = elicit_by_sampling(
        _bernoulli_sampler(0.0), queries=["a", "b", "c"], verifier=_verifier,
        guessing_floor=1e-3, n_per_query=1000,
        argmax_fn=lambda q: "no", checkpoint_id="ck", seed=0,
    )
    assert res.n == 3000  # n_per_query * n_queries


def test_indeterminate_zone_is_neither_present_nor_absent():
    """Low budget can leave lower <= floor < upper: reported as neither, not coerced."""
    res = elicit_by_sampling(
        _bernoulli_sampler(0.01), queries=["q"], verifier=_verifier,
        guessing_floor=0.01, n_per_query=50,   # tiny budget, wide CI straddling floor
        argmax_fn=lambda q: "no", checkpoint_id="ck", seed=0,
    )
    assert not (res.present and res.absent)
    if res.cp_lower <= res.guessing_floor < res.cp_upper:
        assert res.present is False and res.absent is False


def test_rejects_empty_queries():
    with pytest.raises(ValueError):
        elicit_by_sampling(
            _bernoulli_sampler(0.0), queries=[], verifier=_verifier,
            guessing_floor=1e-3, checkpoint_id="ck", seed=0,
        )
