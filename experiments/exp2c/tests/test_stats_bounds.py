import math

from experiments.exp2c import stats_bounds as sb


def test_max_quantile_analytic():
    # P(max2500 <= z) = 0.5 at the median: Phi(z)^2500 = 0.5
    z = sb.max_quantile(2500, 0.5)
    from scipy.stats import norm
    assert math.isclose(norm.cdf(z) ** 2500, 0.5, rel_tol=1e-6)


def test_known_values():
    # E-max ~ 3.5 for n=2500; median ~ 3.46; central-99% band and abort bound
    assert 2.8 < sb.max_quantile(2500, 0.005) < 2.95
    assert 4.5 < sb.max_quantile(2500, 0.995) < 4.75
    assert 5.2 < sb.GATE2_ABORT < 5.5


def test_classify_fire_bands():
    nm, sd = 0.10, 0.02
    lo, hi = sb.GATE2_TOLERATED
    assert sb.classify_fire(nm + (lo + 0.1) * sd, nm, sd, True) == "tolerated"
    assert sb.classify_fire(nm + (hi + 0.2) * sd, nm, sd, True) == "elevated"
    assert sb.classify_fire(nm + (sb.GATE2_ABORT + 0.2) * sd, nm, sd, True) == "structural_abort"
    assert sb.classify_fire(nm + 3.5 * sd, nm, sd, False) == "not_fire"


def test_2b_observed_fires_classify():
    # the two 2b shuffled fires sat at 3.6 and 4.7 null SD (ledger 07-25):
    # 3.6 -> tolerated; 4.7 -> elevated (counts, never aborts)
    nm, sd = 0.25, 0.01
    assert sb.classify_fire(nm + 3.6 * sd, nm, sd, True) == "tolerated"
    assert sb.classify_fire(nm + 4.7 * sd, nm, sd, True) == "elevated"
