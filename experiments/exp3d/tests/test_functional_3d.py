"""Unit fixtures for the frozen functional (doc Open items 1, 7):
worked examples for all four candidates, the canonical-order
bit-identity guarantee, midranks, tie structure, the decile bucket's
frozen boundary rule, and the §5.1 selection formula with its full
tie-break chain."""
import math

import pytest

from experiments.exp3c import analyze_3c as c
from experiments.exp3d import functional_3d as fl


# ------------------------------------------------------ the candidates

def test_c1_worked_examples():
    assert fl.c1_unigram_bits("aaaa") == 0.0
    assert fl.c1_unigram_bits("ecde") == 6.0
    assert fl.c1_unigram_bits("abcd") == 8.0
    assert abs(fl.c1_unigram_bits("rxxxxd")
               - 6 * (-(4 / 6) * math.log2(4 / 6)
                      - 2 * (1 / 6) * math.log2(1 / 6))) < 1e-12


def test_c1_canonical_order_bit_identity():
    """Two strings in the same character-count partition MUST get
    bit-identical values: 'aabadc' and 'dcbaaa' are both {3,1,1,1} but
    build their count dicts in different insertion orders — under
    unsorted summation they differ by 1 ulp (the build-ledger defect,
    closed by sorting)."""
    assert fl.c1_unigram_bits("aabadc") == fl.c1_unigram_bits("dcbaaa")
    assert fl.c1_unigram_bits("beaacd") == fl.c1_unigram_bits("ecbaad")


def test_c2_c3_worked_examples():
    assert fl.c2_distinct_ratio("aaaa") == 0.25
    assert fl.c2_distinct_ratio("ecde") == 0.75
    assert fl.c2_distinct_ratio("dmkd") == 0.75
    assert fl.c3_neg_longest_run("rxxxxd") == -4.0
    assert fl.c3_neg_longest_run("ecde") == -1.0
    assert fl.c3_neg_longest_run("aabbb") == -3.0


def test_c4_lz78_worked_examples():
    assert fl.c4_lz78_phrases("rxxxxd") == 4.0    # r|x|xx|xd
    assert fl.c4_lz78_phrases("ecde") == 4.0      # e|c|d|e (trailing)
    assert fl.c4_lz78_phrases("aaaaaa") == 3.0    # a|aa|aaa
    assert fl.c4_lz78_phrases("a") == 1.0
    assert fl.c4_lz78_phrases("abcd") == 4.0


def test_candidates_total_on_nonempty_and_refuse_empty():
    for _name, fn in fl.CANDIDATES:
        with pytest.raises(ValueError):
            fn("")
        with pytest.raises(ValueError):
            fn(None)
        assert isinstance(fn("zzz"), float)


def test_doc_order_frozen():
    assert [n for n, _f in fl.CANDIDATES] == [
        "C1_unigram_bits", "C2_distinct_ratio", "C3_neg_longest_run",
        "C4_lz78_phrases"]


# ------------------------------------------------------------- strata

def test_strata_law_identical_to_3c():
    answers = ["abcd", "efghi", "jklmno", "pqrs", "aaab"]
    assert fl.strata_of(answers) == c.strata_of(answers)


# ------------------------------------------------------ ranks and ties

def test_midranks_hand_worked():
    # values 1,2,2,5 in one stratum → ranks 1, 2.5, 2.5, 4
    values = [1.0, 2.0, 2.0, 5.0]
    strata = {4: [0, 1, 2, 3]}
    mids = fl.stratified_midranks(values, strata)
    assert mids == {0: 1.0, 1: 2.5, 2: 2.5, 3: 4.0}


def test_midranks_are_within_stratum():
    values = [9.0, 1.0, 1.0, 9.0]
    strata = {4: [0, 1], 5: [2, 3]}
    mids = fl.stratified_midranks(values, strata)
    assert mids == {0: 2.0, 1: 1.0, 2: 1.0, 3: 2.0}


def test_tie_structure_counts_and_midranks():
    values = [1.0, 1.0, 3.0]
    ts = fl.tie_structure(values, {4: [0, 1, 2]})
    assert ts["4"]["n_items"] == 3
    assert ts["4"]["n_distinct_values"] == 2
    assert ts["4"]["groups"][0] == {"value": 1.0, "count": 2,
                                    "midrank": 1.5}


def test_decile_bucket_frozen_boundary():
    # 12 items in one stratum → ceil(12/10) = 2; boundary tie between
    # items 3 and 5 (equal values) breaks by item index
    values = [5.0] * 12
    values[7] = 1.0
    values[3] = 2.0
    values[5] = 2.0
    b = fl.decile_bucket(values, {4: list(range(12))})
    assert b == [3, 7]     # 7 cheapest, then 3 beats 5 by index


def test_decile_bucket_per_stratum_ceil():
    strata = {4: list(range(11)), 5: list(range(11, 20))}
    values = [float(i) for i in range(20)]
    b = fl.decile_bucket(values, strata)
    assert b == [0, 1, 11]     # ceil(11/10)=2, ceil(9/10)=1


# ----------------------------------------------------- the §5.1 formula

def test_stratum_auc_hand_worked():
    values = [1.0, 2.0, 2.0, 4.0]
    # fired {0}: wins over 1,2,3 → 3/3 = 1.0
    assert fl.stratum_auc(values, [0], [1, 2, 3]) == 1.0
    # fired {1}: beats 3, ties 2, loses 0 → (1 + .5)/3
    assert fl.stratum_auc(values, [1], [0, 2, 3]) == pytest.approx(1.5 / 3)


def test_stratified_auc_weighting():
    values = [1.0, 2.0, 3.0, 1.0, 2.0]
    strata = {4: [0, 1, 2], 5: [3, 4]}
    out = fl.stratified_auc(values, strata, [0, 3])
    # stratum 4: fired {0} vs {1,2}: auc 1, weight 2
    # stratum 5: fired {3} vs {4}: auc 1, weight 1
    assert out["stratified_auc"] == 1.0
    assert out["per_stratum"]["4"]["weight"] == 2
    # a stratum with no fires carries no weight and says so
    out2 = fl.stratified_auc(values, strata, [0])
    assert out2["per_stratum"]["5"]["n_fired"] == 0


def test_stratified_auc_refusals():
    values = [1.0, 2.0]
    with pytest.raises(ValueError):
        fl.stratified_auc(values, {4: [0, 1]}, [0, 1])   # all fired
    with pytest.raises(ValueError):
        fl.stratified_auc(values, {4: [0, 1]}, [7])      # out of range
    with pytest.raises(ValueError):
        fl.stratified_auc(values, {4: [0, 1]}, [])       # no fires


def test_select_winner_mean_then_1b_then_doc_order():
    # C1 and C2 rank these fired sets identically (their orderings
    # agree on this battery), so the mean AUCs tie exactly and the 1b
    # AUCs tie exactly — doc order must pick C1.
    answers = ["aaab", "abcd", "efgh", "ijkl",
               "aaabc", "mnopq", "rstuv", "wxyza"]
    sel = fl.select_winner(answers, [0, 4], [0])
    t = sel["table"]
    assert t[0]["mean_auc"] == t[1]["mean_auc"]
    assert t[0]["auc_1b"] == t[1]["auc_1b"]
    assert sel["winner"] == "C1_unigram_bits"


def test_select_winner_prefers_higher_mean():
    # fired items are the longest-RUN items but entropy-expensive:
    # C3 must win on mean AUC
    answers = ["aabb", "abab", "abcd", "efgh",
               "aabbb", "ababa", "abcde", "fghij"]
    # 'aabb' run 2; 'abab' run 1 — same C1 (both {2,2}); C3 separates
    sel = fl.select_winner(answers, [0, 4], [0])
    assert sel["winner"] == "C3_neg_longest_run"
