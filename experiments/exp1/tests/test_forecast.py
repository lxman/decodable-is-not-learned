"""M2 planted-signal tests for S3 (forecastability from below).

A rising precursor with a known crossing must be forecastable (present); a flat
precursor has nothing to extrapolate (slope CI spans 0 -> absent), matching the
design's grokking -> present, Lubana-below -> absent predictions.
"""

import numpy as np
import pytest

from signatures.forecast import forecast_from_below


def test_present_on_rising_precursor_with_known_crossing():
    # y = 0.05 * x, so y* = 0.35 is reached at x = 7. Feed pre-transition points x<7.
    x = np.arange(0, 7, dtype=float)
    rng = np.random.default_rng(0)
    y = 0.05 * x + 0.002 * rng.standard_normal(x.size)
    res = forecast_from_below(
        x, y, true_transition=7.0,
        target_level=0.35, axis="training_steps", seed=1,
    )
    assert res.present is True
    assert abs(res.predicted_transition - 7.0) / 7.0 <= 0.25
    assert res.interval90[0] <= 7.0 <= res.interval90[1]
    assert res.beats_no_transition_baseline is True
    assert res.signature == "S3"


def test_absent_on_flat_precursor():
    x = np.arange(0, 8, dtype=float)
    rng = np.random.default_rng(1)
    y = 0.10 + 0.002 * rng.standard_normal(x.size)  # no trend
    res = forecast_from_below(
        x, y, true_transition=20.0,
        target_level=0.35, axis="training_steps", seed=2,
    )
    assert res.present is False
    assert res.beats_no_transition_baseline is False   # slope CI spans 0
    assert res.slope_ci[0] <= 0.0 <= res.slope_ci[1]


def test_absent_when_interval_misses_transition():
    """A clean trend that extrapolates to the WRONG place must read absent."""
    x = np.arange(0, 7, dtype=float)
    y = 0.05 * x  # crosses 0.35 at x=7
    res = forecast_from_below(
        x, y, true_transition=50.0,   # true transition far from the x=7 forecast
        target_level=0.35, axis="training_steps", seed=3,
    )
    assert res.present is False
    assert res.rel_error > 0.25


def test_graph_axis_is_recorded_for_lubana():
    x = np.arange(0, 7, dtype=float)
    y = 0.05 * x
    res = forecast_from_below(
        x, y, true_transition=7.0,
        target_level=0.35, axis="graph_param", seed=4,
    )
    assert res.axis == "graph_param"


def test_log_transform_forecasts_exponential_precursor():
    """An exponentially-rising precursor is forecast accurately in log space but the
    linear fit overshoots (biases late) — the grokking S3 fix."""
    x = np.arange(0, 10, dtype=float)
    rng = np.random.default_rng(0)
    y = 0.02 * np.exp(0.35 * x) * (1 + 0.05 * rng.standard_normal(x.size))  # noisy exp rise
    true = 9.2                           # analytic 0.5-crossing ~ 9.20
    log_res = forecast_from_below(
        x, y, true_transition=true, target_level=0.5,
        axis="training_steps", transform="log", seed=1,
    )
    lin_res = forecast_from_below(
        x, y, true_transition=true, target_level=0.5,
        axis="training_steps", transform="linear", seed=1,
    )
    assert log_res.present is True
    assert log_res.rel_error < 0.25
    # The linear fit on the same convex data lands worse than log (biased late).
    assert lin_res.rel_error > log_res.rel_error


def test_requires_enough_points():
    with pytest.raises(ValueError):
        forecast_from_below(
            [0.0, 1.0], [0.0, 0.05], true_transition=7.0,
            target_level=0.35, axis="training_steps", seed=5,
        )
