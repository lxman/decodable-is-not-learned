"""S3 — forecastability from below.

Design doc §3 (S3) and §4 (decision rule):

  Grokking is sudden on the argmax curve, so naive extrapolation of the surface
  metric fails even for the resolution exemplar. Forecastability is therefore defined
  on a SMOOTH PRECURSOR (the S1 probe trajectory, or log S2 rate), fit on
  pre-transition points only and extrapolated to predict the transition location.

  present iff the 90% forecast interval contains the true transition AND predicted
          location is within 25% of true AND the forecast beats a no-transition
          baseline.
  absent  iff precursor slope CI includes zero (nothing to extrapolate), or the
          interval misses the transition.

  Axis wrinkle: measured along whichever axis the transition lives on -- training
  steps for grokking, the GRAPH-STRUCTURE control parameter for Lubana. Recorded in
  ForecastResult.axis.

Operational choices (recorded in PROGRESS.md, frozen before result-grade data):
  - "Extrapolate to predict the transition location" is operationalized as: fit the
    precursor (y) vs axis (x) on pre-transition points, and solve for the x at which
    the fitted precursor reaches a preregistered `target_level` y*. y* is a property
    of the task (e.g. probe accuracy = a fixed fraction between chance and ceiling),
    passed in and frozen with the task config -- never fit to the observed transition.
  - Uncertainty is by bootstrap over the pre-transition points (seeded, deterministic
    given seed): interval90 = (5th, 95th) percentile of predicted x; slope_ci
    likewise. This avoids fragile analytic inversion of a ratio near slope 0.
  - "Beats a no-transition baseline" = the bootstrap slope CI excludes 0. A flat
    precursor (slope CI spans 0) cannot forecast a transition, so it reads absent.
"""

from __future__ import annotations

import numpy as np

from .schema import ForecastResult

_LO_PCT, _HI_PCT = 5.0, 95.0  # 90% interval


def _fit_predict_x(x: np.ndarray, y: np.ndarray, target_level: float):
    """OLS fit y ~ x; return (slope, predicted_x) where fitted line hits target_level.

    predicted_x is NaN when the slope is ~0 (no finite crossing).
    """
    slope, intercept = np.polyfit(x, y, 1)
    if abs(slope) < 1e-12:
        return slope, float("nan")
    return slope, (target_level - intercept) / slope


def forecast_from_below(
    precursor_x,
    precursor_y,
    true_transition: float,
    *,
    target_level: float,
    axis: str,
    n_boot: int = 2000,
    rel_tol: float = 0.25,
    seed: int,
) -> ForecastResult:
    """Fit the precursor on pre-transition points and forecast the transition location.

    Parameters
    ----------
    precursor_x, precursor_y : array
        Pre-transition points ONLY (the caller supplies points below the transition).
        x is the axis (training steps or graph parameter); y is the smooth precursor
        (probe accuracy or log S2 rate).
    true_transition : float
        Known transition location on the same axis (from the independent ground-truth
        check), used only to score the forecast -- never to fit it.
    target_level : float
        Preregistered precursor level y* whose crossing defines the predicted
        transition. Frozen with the task config.
    axis : str
        "training_steps" or "graph_param" (validated by ForecastResult/RunRecord).
    rel_tol : float
        Design tolerance on |pred - true| / true (0.25).

    Returns a ForecastResult.
    """
    x = np.asarray(precursor_x, dtype=float)
    y = np.asarray(precursor_y, dtype=float)
    if x.size < 3 or x.size != y.size:
        raise ValueError("need >= 3 matched pre-transition (x, y) points")

    slope, predicted = _fit_predict_x(x, y, target_level)

    rng = np.random.default_rng(seed)
    boot_slopes = np.empty(n_boot)
    boot_preds = np.empty(n_boot)
    idx = np.arange(x.size)
    for b in range(n_boot):
        take = rng.choice(idx, size=x.size, replace=True)
        bs, bp = _fit_predict_x(x[take], y[take], target_level)
        boot_slopes[b] = bs
        boot_preds[b] = bp

    slope_ci = (
        float(np.nanpercentile(boot_slopes, _LO_PCT)),
        float(np.nanpercentile(boot_slopes, _HI_PCT)),
    )
    finite = boot_preds[np.isfinite(boot_preds)]
    if finite.size >= max(2, int(0.5 * n_boot)):
        interval90 = (float(np.percentile(finite, _LO_PCT)),
                      float(np.percentile(finite, _HI_PCT)))
    else:
        # Too few finite crossings to forecast: undefined interval, reads absent.
        interval90 = (float("nan"), float("nan"))

    beats_baseline = bool(slope_ci[0] > 0 or slope_ci[1] < 0)  # CI excludes 0

    if np.isfinite(predicted):
        rel_error = abs(predicted - true_transition) / abs(true_transition)
    else:
        rel_error = float("inf")

    lo, hi = interval90
    contains = bool(np.isfinite(lo) and np.isfinite(hi) and lo <= true_transition <= hi)
    within_tol = bool(rel_error <= rel_tol)

    present = bool(contains and within_tol and beats_baseline)

    return ForecastResult(
        present=present,
        predicted_transition=float(predicted),
        true_transition=float(true_transition),
        interval90=interval90,
        rel_error=float(rel_error),
        slope_ci=slope_ci,
        beats_no_transition_baseline=beats_baseline,
        axis=axis,
    )
