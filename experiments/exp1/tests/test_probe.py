"""M2 planted-signal tests for S1 (the probe).

Design §3 predictions: grokking -> present, Lubana-below -> absent. Here the
"present" and "absent" inputs are built by construction: one layer linearly encodes
the labels (a resolution stand-in), another is pure noise (a percolation stand-in).
"""

import numpy as np
import pytest

from signatures.probe import probe_below_threshold


def _planted(n=300, d=8, n_classes=4, snr=3.0, seed=0):
    """Return (signal_acts, noise_acts, labels).

    signal_acts: class-dependent mean + noise -> linearly probeable.
    noise_acts : label-independent noise -> not probeable.
    """
    rng = np.random.default_rng(seed)
    labels = rng.integers(0, n_classes, size=n)
    centers = rng.standard_normal((n_classes, d)) * snr
    signal = centers[labels] + rng.standard_normal((n, d))
    noise = rng.standard_normal((n, d))
    return signal, noise, labels


def test_probe_present_on_planted_signal():
    signal, _, labels = _planted()
    res = probe_below_threshold(
        {(0, -1): signal}, labels,
        chance=0.25, checkpoint_id="ck", below_threshold=True,
        n_perm=200, seed=1,
    )
    assert res.present is True
    assert res.accuracy > 0.5           # well above chance 0.25
    assert res.null_p < 0.01
    assert res.ci95[0] <= res.accuracy <= res.ci95[1]
    assert res.signature == "S1"


def test_probe_absent_on_pure_noise():
    _, noise, labels = _planted()
    res = probe_below_threshold(
        {(0, -1): noise}, labels,
        chance=0.25, checkpoint_id="ck", below_threshold=True,
        n_perm=200, seed=1,
    )
    assert res.present is False
    assert res.null_p >= 0.01


def test_probe_selects_the_informative_layer():
    signal, noise, labels = _planted()
    res = probe_below_threshold(
        {(0, -1): noise, (1, -1): signal}, labels,
        chance=0.25, checkpoint_id="ck", below_threshold=True,
        n_perm=200, seed=2,
    )
    assert res.present is True
    assert (res.best_layer, res.best_token) == (1, -1)  # the signal-bearing layer
    assert res.n_layers_tested == 2


def test_probe_not_present_when_not_below_threshold():
    """Even a strong probe reads 'not present' if the checkpoint is above threshold.

    Design rule: S1 present is defined only at a below-threshold checkpoint.
    """
    signal, _, labels = _planted()
    res = probe_below_threshold(
        {(0, -1): signal}, labels,
        chance=0.25, checkpoint_id="ck", below_threshold=False,
        n_perm=200, seed=1,
    )
    assert res.present is False
    assert res.below_threshold is False


def test_probe_rejects_mismatched_rows():
    signal, _, labels = _planted()
    with pytest.raises(ValueError):
        probe_below_threshold(
            {(0, -1): signal[:-5]}, labels,
            chance=0.25, checkpoint_id="ck", seed=1, n_perm=10,
        )
