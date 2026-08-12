"""Fixture suite for the frozen Exp 1b analysis (design §5).

One synthetic case per preregistered provision. No test here reads a real
record — the analysis freezes before any 1b data exists, which is the only
thing that makes it a preregistration.
"""

import pytest

from experiments.exp1b import analyze_1b as a


def cells(system, present_by_size):
    """present_by_size: {"1M": n_present, "10M": n_present}, 5 seeds each."""
    out = []
    for size, k in present_by_size.items():
        for seed in range(5):
            out.append({"system": system, "size_bucket": size,
                        "seed": 100 + seed, "present": seed < k})
    return out


def matrix(grok=(5, 4), above=(5, 5), below=(0, 0), untrained_present=0):
    trained = (cells("grokking", dict(zip(a.SIZES, grok)))
               + cells("lubana_above", dict(zip(a.SIZES, above)))
               + cells("lubana_below", dict(zip(a.SIZES, below))))
    untrained = []
    for system in a.TRAINED_ROWS:
        for size in a.SIZES:
            for seed in range(5):
                untrained.append({"system": system, "size_bucket": size,
                                  "seed": 100 + seed, "present": False})
    for i in range(untrained_present):
        untrained[i]["present"] = True
    return trained, untrained


def test_passes_on_the_expected_matrix():
    out = a.verdict(*matrix())
    assert out["verdict"] == "PASS"
    assert out["failures"] == []


def test_pools_counts_across_sizes():
    out = a.verdict(*matrix(grok=(5, 4)))
    assert out["rows"]["grokking"]["present"] == 9
    assert out["rows"]["grokking"]["n"] == 10
    assert out["rows"]["grokking"]["per_size"] == {"1M": 5, "10M": 4}


def test_present_row_below_the_bar_fails():
    out = a.verdict(*matrix(grok=(4, 3)))          # 7/10 < 8
    assert out["verdict"] == "FAIL"
    assert any("grokking" in f for f in out["failures"])


def test_a_single_fire_on_the_absent_row_fails():
    out = a.verdict(*matrix(below=(1, 0)))
    assert out["verdict"] == "FAIL"
    assert any("lubana_below" in f for f in out["failures"])


def test_a_single_fire_on_the_untrained_row_fails():
    """The reservoir gate. One fire means the probe is reading the
    high-dimensional expansion, not the structure — the failure mode that
    terminated Experiment 2 at 120 of 120 fits."""
    out = a.verdict(*matrix(untrained_present=1))
    assert out["verdict"] == "FAIL"
    assert any("untrained" in f for f in out["failures"])


def test_pooling_tolerates_a_five_three_split_and_says_so():
    """Preregistered consequence of pooling: >=8/10 admits a split that a
    per-size >=4/5 bar would reject. Per-size counts stay visible."""
    out = a.verdict(*matrix(grok=(5, 3)))
    assert out["verdict"] == "PASS"
    assert out["rows"]["grokking"]["per_size"] == {"1M": 5, "10M": 3}


def test_zero_rows_carry_a_clopper_pearson_bound():
    out = a.verdict(*matrix())
    lo, hi = out["rows"]["lubana_below"]["cp95"]
    assert lo == 0.0
    assert 0.25 < hi < 0.35            # 0/10
    lo_u, hi_u = out["rows"]["untrained"]["cp95"]
    assert hi_u < 0.15                 # 0/30 is a much tighter bound


def test_untrained_row_pools_all_thirty_twins():
    out = a.verdict(*matrix())
    assert out["rows"]["untrained"]["n"] == 30


def test_missing_cells_are_refused_not_scored():
    trained, untrained = matrix()
    trained.pop()
    with pytest.raises(ValueError, match="incomplete"):
        a.verdict(trained, untrained)


def test_a_size_outside_the_matrix_is_refused():
    trained, untrained = matrix()
    trained.append({"system": "grokking", "size_bucket": "100M",
                    "seed": 100, "present": True})
    with pytest.raises(ValueError, match="100M"):
        a.verdict(trained, untrained)


def test_the_bar_constants_are_the_preregistered_ones():
    assert a.PRESENT_BAR == 8
    assert a.POOLED_N == 10
    assert a.SIZES == ("1M", "10M")
    assert a.SEEDS == (100, 101, 102, 103, 104)
