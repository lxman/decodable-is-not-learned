"""Fixtures for the inference machinery (design §5.3–§5.5; doc Open
items 2–3): the exact hypergeometric primary, m_min / THIN_MAX, the
count-weighted label-permutation null, the designation-
exchangeability null, and m_s,min — each exact DP proved against
brute-force enumeration on a small synthetic instance."""
import itertools
import math
from fractions import Fraction

import pytest

from experiments.exp3e import stats_3e as st


# ------------------------------------------------------ hypergeometric

def test_constants_are_the_design_literals():
    assert st.ALPHA_3E == 0.05
    assert st.THIN_MAX == 10
    assert (st.N_SUBSET, st.K_NON_REACHABLE) == (45, 13)


def test_hypergeom_pmf_sums_to_one_and_matches_closed_form():
    pmf = st.hypergeom_pmf(45, 13, 8)
    assert sum(pmf) == 1
    assert pmf[0] == Fraction(math.comb(32, 8), math.comb(45, 8))
    assert pmf[3] == Fraction(math.comb(13, 3) * math.comb(32, 5),
                              math.comb(45, 8))


def test_doc_table_values():
    # §5.3's printed table
    assert round(st.hypergeom_tails(45, 13, 8, 0)[0], 4) == 0.0488
    assert round(st.hypergeom_tails(45, 13, 10, 1)[0], 4) == 0.1345
    assert round(st.hypergeom_tails(45, 13, 15, 2)[0], 4) == 0.0980
    assert round(st.hypergeom_tails(45, 13, 20, 1)[0], 4) == 0.0015


def test_tails_include_the_observed_point_and_overlap():
    low, high = st.hypergeom_tails(45, 13, 8, 2)
    assert low + high > 1.0          # both tails include X = 2
    assert st.hypergeom_tails(45, 13, 8, 0)[1] == 1.0
    assert st.hypergeom_tails(45, 13, 8, 8)[0] == 1.0


def test_tails_refuse_impossible_observations():
    with pytest.raises(ValueError):
        st.hypergeom_tails(45, 13, 8, 9)
    with pytest.raises(ValueError):
        st.hypergeom_tails(45, 13, 14, 14)   # X > K


def test_m_min_is_eight_and_anti_m_min_is_three():
    assert st.m_min_of(45, 13, 0.05) == 8
    assert st.m_min_anti_of(45, 13, 0.05) == 3


def test_m_min_on_a_small_instance():
    # N = 8, K = 3: P(X = 0 | n) = C(5, n)/C(8, n): n=1 .625, n=2 .357,
    # n=3 .179, n=4 .0714, n=5 .0179 → m_min = 5 at α = .05
    assert st.m_min_of(8, 3, 0.05) == 5
    assert st.m_min_of(8, 3, 0.10) == 4


def test_primary_test_fields_and_thin():
    t = st.primary_test(n_fired=24, x_non_reachable=1)
    assert t["n_fired"] == 24 and t["x_non_reachable"] == 1
    assert t["p_low"] < 1e-3 and t["p_high"] > 0.99
    assert t["thin"] is False
    assert t["expected_x_under_null"] == pytest.approx(24 * 13 / 45)
    assert st.primary_test(n_fired=10, x_non_reachable=0)["thin"] is True
    assert st.primary_test(n_fired=11, x_non_reachable=0)["thin"] is False


def test_primary_test_with_no_fires_has_no_p():
    t = st.primary_test(n_fired=0, x_non_reachable=0)
    assert t["p_low"] is None and t["p_high"] is None and t["thin"]


def test_best_case_and_calibration_tables():
    bc = st.best_case_table(45, 13, 12)
    assert [r["n"] for r in bc] == list(range(1, 13))
    assert round(bc[7]["p_low_at_x0"], 4) == 0.0488
    cal = st.calibration_table(45, 13, (8, 24, 28), 0.05)
    for row in cal:
        assert row["size_low"] <= 0.05 and row["size_high"] <= 0.05
        assert row["size_union"] == pytest.approx(
            row["size_low"] + row["size_high"])


# ---------------------------------------------- count-weighted DP null

def _brute_count_weighted(counts, K):
    n = len(counts)
    dist = {}
    for sub in itertools.combinations(range(n), K):
        s = sum(counts[i] for i in sub)
        dist[s] = dist.get(s, 0) + 1
    return dist


def test_count_weighted_null_matches_brute_force():
    counts = [5, 3, 0, 1, 0, 2, 0, 1]
    got = st.count_weighted_null(counts, 3)
    want = _brute_count_weighted(counts, 3)
    assert got == want
    assert sum(got.values()) == math.comb(8, 3)


def test_count_weighted_test_tails_match_brute_force():
    counts = [5, 3, 0, 1, 0, 2, 0, 1]
    non = [2, 4, 6]                      # T_obs = 0
    t = st.count_weighted_test(counts, non)
    dist = _brute_count_weighted(counts, 3)
    tot = math.comb(8, 3)
    want_low = Fraction(sum(v for s, v in dist.items() if s <= 0), tot)
    assert t["T_obs"] == 0
    assert t["p_low"] == pytest.approx(float(want_low))
    assert t["p_high"] == pytest.approx(1.0)
    non2 = [0, 1, 5]                     # T_obs = 10, the maximum
    t2 = st.count_weighted_test(counts, non2)
    assert t2["p_high"] == pytest.approx(1 / tot)
    assert t2["p_low"] == pytest.approx(1.0)


def test_count_weighted_test_refuses_wrong_label_count():
    with pytest.raises(ValueError, match="labels"):
        st.count_weighted_test([1, 0, 0], [0, 1, 5])


def test_count_weighted_all_zero_counts_degenerate():
    t = st.count_weighted_test([0, 0, 0, 0], [0, 1])
    assert t["T_obs"] == 0 and t["p_low"] == 1.0 and t["p_high"] == 1.0


# ------------------------------------------ designation-exchangeability

def _brute_designation(vectors):
    dist = {}
    for pick in itertools.product(*vectors):
        s = sum(pick)
        dist[s] = dist.get(s, 0) + 1
    return dist


def test_designation_null_matches_brute_force():
    vectors = [(3, 1), (0, 2, 0), (1, 0, 0, 4), (2, 2)]
    got = st.designation_null(vectors)
    assert got == _brute_designation(vectors)
    assert sum(got.values()) == 2 * 3 * 4 * 2


def test_designation_test_upper_tail_matches_brute_force():
    vectors = [(3, 1), (0, 2, 0), (1, 0, 0, 4), (2, 2)]
    t = st.designation_test(vectors)
    t_obs = 3 + 0 + 1 + 2
    dist = _brute_designation(vectors)
    tot = sum(dist.values())
    want = Fraction(sum(v for s, v in dist.items() if s >= t_obs), tot)
    assert t["T_obs"] == t_obs
    assert t["p"] == pytest.approx(float(want))
    assert t["events"] == sum(sum(v) for v in vectors)
    assert t["n_items"] == 4


def test_designation_test_all_on_reverse_is_the_product_of_thetas():
    vectors = [(1, 0), (1, 0, 0), (1, 0, 0, 0)]
    t = st.designation_test(vectors)
    assert t["p"] == pytest.approx(1 / 24)


def test_designation_test_with_no_events():
    t = st.designation_test([(0, 0), (0, 0, 0)])
    assert t["events"] == 0 and t["T_obs"] == 0 and t["p"] == 1.0


def test_designation_test_refuses_degenerate_vectors():
    with pytest.raises(ValueError, match="competitor"):
        st.designation_test([(1,)])


# ------------------------------------------------------------- m_s,min

def _brute_m_s_min(m_sizes, alpha, e_max):
    slots = [(i, k) for i, m in enumerate(m_sizes) for k in range(1 + m)]
    for e in range(1, e_max + 1):
        best = 1.0
        for combo in itertools.combinations_with_replacement(slots, e):
            vectors = [[0] * (1 + m) for m in m_sizes]
            for (i, k) in combo:
                vectors[i][k] += 1
            p = st.designation_test([tuple(v) for v in vectors])["p"]
            best = min(best, p)
        if best <= alpha:
            return e
    return None


def test_m_s_min_matches_brute_force_on_a_small_instance():
    m_sizes = [1, 2, 3]
    assert st.m_s_min_of(m_sizes, 0.05) == _brute_m_s_min(m_sizes, 0.05, 4)
    assert st.m_s_min_of(m_sizes, 0.05) == 3
    assert st.m_s_min_of([1, 1], 0.05) is None      # (1/2)^2 = .25 > α


def test_m_s_min_on_the_design_structure_is_three():
    m_sizes = [1] * 10 + [2] * 6 + [3] * 5
    assert st.m_s_min_of(m_sizes, 0.05) == 3
    assert st.best_case_specificity_table(m_sizes, 4) == [
        {"events": 1, "best_p": pytest.approx(1 / 4)},
        {"events": 2, "best_p": pytest.approx(1 / 16)},
        {"events": 3, "best_p": pytest.approx(1 / 64)},
        {"events": 4, "best_p": pytest.approx(1 / 256)},
    ]


def test_specificity_annotation_tree():
    assert st.specificity_annotation(p=0.01, events=5, m_s_min=3) == \
        "DIRECTED"
    assert st.specificity_annotation(p=0.4, events=5, m_s_min=3) == \
        "MISFIRE-RATE"
    assert st.specificity_annotation(p=1.0, events=2, m_s_min=3) == \
        "SPARSE"
    assert st.specificity_annotation(p=None, events=0, m_s_min=3) == \
        "SPARSE"
    # the bar is inclusive: events == m_s,min is enough to have had a
    # best case that rejects, so it is MISFIRE-RATE, not SPARSE
    assert st.specificity_annotation(p=0.4, events=3, m_s_min=3) == \
        "MISFIRE-RATE"
    assert st.specificity_annotation(p=1.0, events=2, m_s_min=3) == \
        "SPARSE"
