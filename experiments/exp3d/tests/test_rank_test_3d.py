"""Unit fixtures for the exact null and the preregistered statistic
(doc Open items 2, 3, 7): DP vs brute-force enumeration, tail
conventions, the MC fallback's agreement with the exact path, m_min
in both directions, composition enumeration, and the decile bucket's
hypergeometric tail."""
import itertools
import math

import numpy as np
import pytest

from experiments.exp3d import functional_3d as fl
from experiments.exp3d import rank_test_3d as rt

ANSWERS = ["aaab", "aabc", "abcd", "abce", "abcf", "aabb", "abcg",
           "aaabc", "aabcd", "abcde", "abcdf", "abcdg", "aabce"]
STRATA = fl.strata_of(ANSWERS)
VALUES = fl.candidate_values(fl.c1_unigram_bits, ANSWERS)
MIDS = fl.stratified_midranks(VALUES, STRATA)


def brute_pmf(composition):
    pools = {k: rt.doubled_midranks(MIDS, STRATA[int(k)])
             for k in composition}
    counts = {}
    total = 0
    per = []
    for k in sorted(composition):
        per.append(list(itertools.combinations(pools[k],
                                               composition[k])))
    for combo in itertools.product(*per):
        s = sum(sum(c_) for c_ in combo)
        counts[s] = counts.get(s, 0) + 1
        total += 1
    return {s: n / total for s, n in counts.items()}


@pytest.mark.parametrize("comp", [{"4": 1, "5": 0}, {"4": 2, "5": 1},
                                  {"4": 3, "5": 2}, {"4": 0, "5": 3}])
def test_dp_equals_enumeration(comp):
    per_q = {k: rt.subset_sum_dist(
        rt.doubled_midranks(MIDS, STRATA[int(k)]), 8)
        for k in ("4", "5")}
    pmf = rt.convolve_composition(per_q, comp)
    brute = brute_pmf({k: v for k, v in comp.items() if v})
    for s, p in brute.items():
        assert pmf[s] == pytest.approx(p, abs=1e-12)
    assert pmf.sum() == pytest.approx(1.0, abs=1e-12)


def test_tail_p_includes_observed_point_both_sides():
    pmf = np.array([0.0, 0.2, 0.3, 0.5])
    lo, hi = rt.tail_p(pmf, 2)
    assert lo == pytest.approx(0.5)
    assert hi == pytest.approx(0.8)
    # beyond support: lower tail saturates, upper tail is 0
    lo, hi = rt.tail_p(pmf, 9)
    assert lo == 1.0 and hi == 0.0


def test_doubled_midranks_integrality():
    assert rt.doubled_midranks({0: 1.5, 1: 2.0}, [0, 1]) == [3, 4]
    with pytest.raises(ValueError):
        rt.doubled_midranks({0: 1.3}, [0])


def test_statistic_T_and_composition():
    fired = [0, 7]
    t = rt.statistic_T(MIDS, fired)
    assert t == MIDS[0] + MIDS[7]
    comp = rt.fired_composition(STRATA, fired)
    assert comp == {"4": 1, "5": 1}
    with pytest.raises(ValueError):
        rt.fired_composition(STRATA, [99])


def test_full_test_exact_path():
    res = rt.stratified_rank_test(VALUES, STRATA, [0, 7])
    assert res["path"] == "exact_dp"
    assert res["thin"] is True
    # cheapest item in each stratum: p_low = P(T4<=r0)P(T5<=r7)
    # 'aaab' is uniquely cheapest of 7; 'aaabc' uniquely cheapest of 6
    assert res["p_low"] == pytest.approx((1 / 7) * (1 / 6))
    assert res["p_high"] == 1.0


def test_empty_fired_set():
    res = rt.stratified_rank_test(VALUES, STRATA, [])
    assert res["p_low"] is None and res["path"] == "empty"


def test_mc_agrees_with_exact():
    per_q = {k: rt.subset_sum_dist(
        rt.doubled_midranks(MIDS, STRATA[int(k)]), 8)
        for k in ("4", "5")}
    comp = {"4": 2, "5": 1}
    pmf = rt.convolve_composition(per_q, comp)
    t2 = 18
    lo_e, hi_e = rt.tail_p(pmf, t2)
    lo_m, hi_m = rt.mc_tail_p(VALUES, STRATA, comp, t2,
                              mc_count=100_000, mc_seed=11)
    assert lo_m == pytest.approx(lo_e, abs=6e-3)
    assert hi_m == pytest.approx(hi_e, abs=6e-3)


def test_mc_is_seeded_and_reproducible():
    a = rt.mc_tail_p(VALUES, STRATA, {"4": 2}, 10, mc_count=10_000,
                     mc_seed=rt.MC_PERM_SEED)
    b = rt.mc_tail_p(VALUES, STRATA, {"4": 2}, 10, mc_count=10_000,
                     mc_seed=rt.MC_PERM_SEED)
    assert a == b


def test_frozen_constants():
    assert rt.ALPHA_3D == 0.05
    assert rt.MC_PERM_COUNT == 1_000_000
    assert rt.MC_PERM_SEED == 20260818
    assert rt.THIN_MAX == 4
    assert rt.DP_M_CAP == 64


def test_m_min_hand_verified():
    # single fire best: 1/7 (len-4 'aaab' unique cheapest? 'aaab' is
    # {3,1}, 'aabb' {2,2}, 'aabc' {2,1,1} — all distinct values, so
    # cheapest IS unique: p = 1/7 > .05; len-5: 1/6 > .05.
    # m = 2 best: both cheapest singles: (1/7)(1/6) = .0238 <= .05.
    assert rt.m_min_of(VALUES, STRATA) == 2
    # anti direction: most-expensive placements. len-5's top class has
    # 3 tied items ('abcde','abcdf','abcdg'): m=3 all three →
    # P(T5 >= max) = C(3,3)/C(6,3) = 1/20 = .05 <= alpha — the
    # boundary case rejects exactly AT alpha, and no m <= 2
    # arrangement reaches .05 anywhere (best m=2 is C(3,2)/C(6,2) =
    # .2 within len-5, (4/7)(3/6) = .286 cross-strata, C(4,2)/C(7,2)
    # = .286 within len-4)
    assert rt.m_min_of(VALUES, STRATA, direction="high") == 3


def test_m_min_degenerate_raises():
    # all values tied: no arrangement ever rejects — must surface,
    # never guess (a degenerate functional is a freeze-visible
    # pathology, not a silent m_min)
    flat = [1.0] * 13
    with pytest.raises(ValueError):
        rt.m_min_of(flat, STRATA)


def test_compositions_complete_and_bounded():
    strata = {4: [0, 1], 5: [2, 3, 4]}
    comps = list(rt._compositions(3, ["4", "5"], strata))
    assert {tuple(sorted(c.items())) for c in comps} == {
        (("4", 0), ("5", 3)), (("4", 1), ("5", 2)),
        (("4", 2), ("5", 1))}


def test_bucket_tail_p_matches_hypergeometric():
    # one stratum of 7, explicit 2-item bucket, both fired items in it:
    # p = C(2,2)/C(7,2) = 1/21
    res = rt.bucket_tail_p({4: STRATA[4]}, [0, 5], [0, 5])
    assert res["observed_overlap"] == 2
    want = (math.comb(2, 2) * math.comb(5, 0)) / math.comb(7, 2)
    assert res["p_upper"] == pytest.approx(want)


def test_bucket_tail_p_convolves_strata():
    # the frozen decile bucket here is 1 item per stratum
    # (ceil(7/10) = ceil(6/10) = 1): the two strata's cheapest
    bucket = fl.decile_bucket(VALUES, STRATA)
    assert bucket == [0, 7]
    res = rt.bucket_tail_p(STRATA, bucket, [0, 7])
    # both fired items are their strata's sole bucket members:
    # p = (1/7)(1/6) exact
    assert res["observed_overlap"] == 2
    assert res["p_upper"] == pytest.approx((1 / 7) * (1 / 6))


def test_flat_calibration_exact_small():
    """Under the null itself (uniform fired sets at fixed composition),
    P(p_low <= alpha) <= alpha, exactly, by enumeration — the
    discreteness-conservative property the power table's FLAT row
    shows at scale."""
    comp = {"4": 2, "5": 1}
    per_q = {k: rt.subset_sum_dist(
        rt.doubled_midranks(MIDS, STRATA[int(k)]), 8)
        for k in ("4", "5")}
    pmf = rt.convolve_composition(per_q, comp)
    hit = tot = 0
    for f4 in itertools.combinations(STRATA[4], 2):
        for f5 in itertools.combinations(STRATA[5], 1):
            t2 = sum(int(round(MIDS[i] * 2)) for i in f4 + f5)
            p_low, _ = rt.tail_p(pmf, t2)
            hit += p_low <= 0.05
            tot += 1
    assert hit / tot <= 0.05
