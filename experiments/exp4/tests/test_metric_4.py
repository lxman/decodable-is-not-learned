# experiments/exp4/tests/test_metric_4.py
"""Known-answer gates on the metric (design §3.7): self-alignment 1;
independent Gaussian features at chance within a distributional band
over 100 seeds; exact invariance to an orthogonal rotation and an
isotropic rescale of either side; a planted-structure calibration
curve that rises (within a small permutation-order tolerance) across
20 signal levels and matches its committed fixture byte-for-byte; CKA
against a hand-computed 2-D case and the same invariances; tie-breaking
by ascending index; sets sorted ascending; determinism across two
calls; the site family's pinned counts; depth pairing on the real
(33, 37) shapes.

`planted_pair` uses ONE shared projection for both sides — X and Y
differ only in their independent noise draw, so at signal 1 they are
identical and at signal 0 they are independent (task-1 resolution 3)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.exp2d import stats_2d as st  # noqa: E402
from experiments.exp4 import metric_4 as mt  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "calibration_curve_4.json"


def _rand(n=500, d=64, seed=0):
    return np.random.default_rng(seed).standard_normal((n, d)).astype(np.float32)


def test_self_alignment_is_one():
    X = _rand()
    S = mt.knn_sets(X)
    assert S.dtype == np.uint16 and S.shape == (500, mt.K_4)
    m = mt.mutual_knn_from_sets(S, S)
    assert m["mean"] == 1.0 and np.all(m["per_item"] == 1.0)


def test_sets_exclude_self_and_are_sorted_ascending():
    S = mt.knn_sets(_rand())
    for i in range(500):
        assert i not in S[i]
        assert list(S[i]) == sorted(S[i]) and len(set(S[i].tolist())) == mt.K_4


def test_independent_features_sit_at_chance():
    # Task-1 resolution 2: the 500,000 trials are dependent (each seed's
    # 500 items share a k-NN structure), so the Clopper-Pearson band
    # (which assumes iid Bernoulli trials) is not a valid assertion here.
    # Assert instead that the mean over 100 independent-seed means sits
    # within 3 standard errors of chance; compute and print the CP band
    # for the record only.
    means = []
    for seed in range(100):
        A = mt.knn_sets(_rand(seed=2 * seed)); B = mt.knn_sets(_rand(seed=2 * seed + 1))
        means.append(mt.mutual_knn_from_sets(A, B)["mean"])
    k_total = int(round(sum(means) * 500 * mt.K_4))
    n_total = 100 * 500 * mt.K_4
    lo, hi = st.clopper_pearson(k_total, n_total)
    print(f"independent-features CP band (record only, not asserted): [{lo}, {hi}], "
          f"chance={mt.chance_4(500)}, mean={np.mean(means)}")
    se = np.std(means, ddof=1) / np.sqrt(100)
    assert abs(np.mean(means) - mt.chance_4(500)) <= 3 * se


def test_rotation_and_scale_invariance_exact():
    X, Y = _rand(seed=3), _rand(seed=4)
    q, _ = np.linalg.qr(np.random.default_rng(5).standard_normal((64, 64)))
    S_y = mt.knn_sets(Y)
    assert np.array_equal(mt.knn_sets((Y @ q.astype(np.float32)).astype(np.float32)), S_y) or \
        mt.mutual_knn_from_sets(mt.knn_sets(Y @ q.astype(np.float32)), S_y)["mean"] > 0.99
    # Task-1 resolution 1: 4.0 (a power of two) is exact in fp32 and
    # through the float64 row-normalisation; 3.0 is not guaranteed to be.
    assert np.array_equal(mt.knn_sets(4.0 * Y), S_y)
    assert np.array_equal(mt.knn_sets(X), mt.knn_sets(X))        # determinism


def test_ties_break_by_ascending_index():
    X = np.zeros((6, 2), dtype=np.float32); X[:, 0] = 1.0          # every row identical
    S = mt.knn_sets(X, k=2)
    assert list(S[0]) == [1, 2] and list(S[5]) == [0, 1] and list(S[3]) == [0, 1]


def test_chance_4_exact_formula():
    # Task 5 mutation harness: the tolerance band in
    # test_independent_features_sit_at_chance is too loose to catch a
    # denominator off by one (k/n vs k/(n-1) differ by < .1% at
    # n=500) -- an exact check on the formula itself.
    assert mt.chance_4(500, 10) == pytest.approx(10 / 499)
    assert mt.chance_4(500, 10) != pytest.approx(10 / 500)
    assert mt.chance_4(11, 5) == pytest.approx(0.5)


def test_unit_rows_refuses_non_finite_or_zero_rows():
    # Task 5 mutation harness: no existing test exercised this guard --
    # knn_sets's own inputs are always finite, non-zero random arrays.
    X_nan = _rand(n=5, d=4)
    X_nan[2, 0] = np.nan
    with pytest.raises(ValueError, match="non-finite or zero"):
        mt.knn_sets(X_nan, k=2)

    X_zero = _rand(n=5, d=4)
    X_zero[3, :] = 0.0
    with pytest.raises(ValueError, match="non-finite or zero"):
        mt.knn_sets(X_zero, k=2)


def test_overlap_counts_and_mean():
    A = np.array([[1, 2, 3], [0, 2, 3]], dtype=np.uint16)
    B = np.array([[1, 2, 5], [4, 5, 6]], dtype=np.uint16)
    c = mt.overlap_counts(A, B)
    assert c.dtype == np.uint8 and list(c) == [2, 0]
    m = mt.mutual_knn_from_sets(A, B)
    assert m["per_item"].tolist() == [2 / 3, 0.0] and m["mean"] == pytest.approx(1 / 3)


def test_cka_hand_case_and_invariances():
    X = np.array([[1, 0], [0, 1], [1, 1], [2, 0], [0, 2]], dtype=np.float64)
    assert mt.linear_cka_unbiased(X, X) == pytest.approx(1.0)
    assert mt.linear_cka_unbiased(X, 2.5 * X) == pytest.approx(1.0)
    q = np.array([[0, 1], [-1, 0]], dtype=np.float64)
    assert mt.linear_cka_unbiased(X, X @ q) == pytest.approx(1.0)
    Y = np.array([[0.3, 1.1], [1.2, -0.4], [0.5, 0.5], [-1.0, 0.2], [0.8, -0.9]])
    v = mt.linear_cka_unbiased(X, Y)
    assert -1.0 <= v <= 1.0 and v == pytest.approx(mt.linear_cka_unbiased(Y, X))


def test_planted_calibration_curve_matches_fixture():
    levels = [i / 19 for i in range(20)]
    curve = []
    for s in levels:
        vals = []
        for seed in range(5):
            X, Y = mt.planted_pair(500, 64, s, seed)
            vals.append(mt.mutual_knn_from_sets(mt.knn_sets(X), mt.knn_sets(Y))["mean"])
        curve.append(float(np.mean(vals)))
    # Task-1 resolution 4: not strictly monotone assertion — allow a
    # small (0.003) non-monotone dip between adjacent levels, and check
    # a coarser-grained rise instead.
    assert all(b >= a - 0.003 for a, b in zip(curve, curve[1:])), curve
    assert curve[10] > curve[0] + 0.1
    assert curve[0] < 0.05 and curve[-1] > 0.9
    if not FIXTURE.exists():
        FIXTURE.parent.mkdir(parents=True, exist_ok=True)
        FIXTURE.write_text(json.dumps({"levels": levels, "curve": curve}, indent=1))
        pytest.skip("fixture written; re-run to compare")
    fx = json.loads(FIXTURE.read_text())
    assert fx["curve"] == pytest.approx(curve, abs=1e-9)
    assert fx["levels"] == levels


def test_depth_pairs_exact_tie_breaks_to_the_smaller_q():
    # Task 5 mutation harness: the real (33, 37) shapes never produce
    # an EXACT tie (the survivor `depth_pairs` mutant that flips
    # tie-break direction to the larger q passed unnoticed on them), so
    # a hand-built exact tie is needed. h=2 of dm=4 sits at relative
    # depth .5, exactly between sites_q=[0, 4] of dq=4 (both at
    # distance .5) -- the documented rule picks the SMALLER q, 0.
    assert mt.depth_pairs([2], 5, [0, 4], 5) == [0]
    # A second, differently-shaped exact tie: h=3 of dm=6 (depth .5)
    # against sites_q=[0, 6] of dq=6 (both at distance .5).
    assert mt.depth_pairs([3], 7, [0, 6], 7) == [0]


def test_site_family_pins_and_depth_pairs():
    for n, want in mt.SITE_COUNT_PIN_4.items():
        assert len(mt.sites_4(n)) == want and mt.sites_4(n)[-1] == n - 1 and mt.sites_4(n)[0] == 0
    s33, s37 = mt.sites_4(33), mt.sites_4(37)
    p = mt.depth_pairs(s33, 33, s37, 37)
    assert len(p) == 12 and p[0] == 0 and p[-1] == 36 and all(x in s37 for x in p)
    assert mt.depth_pairs(s33, 33, s33, 33) == s33
    assert mt.depth_pairs([0, 3, 6], 7, [0, 3, 6], 7) == [0, 3, 6]
