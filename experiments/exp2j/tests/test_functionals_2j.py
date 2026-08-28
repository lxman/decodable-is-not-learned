# experiments/exp2j/tests/test_functionals_2j.py
"""functionals_2j: the four functionals on hand-built caps and on the
REAL item files (design §2's table pinned by literal), the bucket
rule's three branches, composite strata, verified bits vs 2i's own
counts, the thinner and the matched-k rule."""
from __future__ import annotations

import numpy as np
import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2g import battery_2g as bg
from experiments.exp2i import battery_2i as bi
from experiments.exp2j import functionals_2j as fn


def _cap(items, answer_type="number"):
    return {"answer_type": answer_type,
            "eval_items": [{"question": q, "answer": a} for q, a in items]}


def _rows(draws_by_item):
    return [{"item": i, "draws": {"0": list(d)}} for i, d in enumerate(draws_by_item)]


# ------------------------------------------------------------- functionals

def test_answer_length_repeat_overlap_on_hand_items():
    cap = _cap([("What is 12 + 21?", "33"), ("What is 40 + 5?", "45"),
                ("What is 7 + 7?", "14")])
    assert fn.answer_length(cap) == [2, 2, 2]
    assert fn.repeated_char(cap) == [1, 0, 0]
    # '33': both chars in the question? '3' absent from "What is 12 + 21?" -> 0.0
    # '45': '4' and '5' both present -> 1.0 ; '14': '1' absent, '4' absent -> 0.0
    assert fn.input_overlap(cap) == [0.0, 1.0, 0.0]


def test_input_overlap_lowercases_the_question():
    cap = _cap([("Which of these means the opposite of 'Hot': COLD, big?", "cold")],
               answer_type="word")
    assert fn.input_overlap(cap) == [1.0]


def test_answer_length_uses_normalized_not_raw():
    """The '33'/'45'/'14' hand cases above don't distinguish normalized
    from raw (already lowercase digit strings) — this one does: trailing
    punctuation and case are stripped by normalize_answer before length
    is taken (a Step 4 mutant: answer_length on the raw answer)."""
    cap = _cap([("What is the opposite of hot?", "Cold."),
                (" q1", "  DOG  ")], answer_type="word")
    assert fn.answer_length(cap) == [4, 3]     # 'cold', 'dog' — not 5, 7


def test_wrong_target_propensity_excludes_same_answer_items():
    # items 0 and 1 share the answer '3'; item 2's answer is '5'
    cap = _cap([("q0", "3"), ("q1", "3"), ("q2", "5")])
    fn_n = fn.N_ITEMS
    rows = _rows([[" 3"] * 2 + [" 5"] * 2,      # item 0: two 3s, two 5s
                  [" 3"] * 4,                    # item 1: four 3s
                  [" 5"] * 3 + [" 3"]])          # item 2: three 5s, one 3
    # monkeypatch the sizes for a 3-item, 4-draw toy
    fn.N_ITEMS, fn.DRAWS_PER_ITEM = 3, 4
    try:
        pi = fn.wrong_target_propensity(rows, cap)
        # π_0 = draws on items with answer != '3' (item 2 only) emitting '3' = 1/4
        # π_1 = same = 1/4 ; π_2 = draws on items 0,1 emitting '5' = 2/8
        assert pi == pytest.approx([0.25, 0.25, 0.25])
        loo = fn.wrong_target_propensity(rows, cap, loo=True)
        # LOO for item 0: draws on items 1,2 emitting '3' = 5/8
        assert loo[0] == pytest.approx(5 / 8)
    finally:
        fn.N_ITEMS, fn.DRAWS_PER_ITEM = fn_n, bi.DRAWS_PER_ITEM


def test_normalized_draw_mirrors_verify_3c_on_index_error():
    # normalize_answer on an empty word answer raises IndexError only through
    # s.split()[0] on '' ... which returns '' (guarded) — so the None branch is
    # reached by monkeypatching, proving the mirror exists rather than a hope.
    import experiments.exp2j.functionals_2j as m
    orig = m.harness.normalize_answer
    m.harness.normalize_answer = lambda t, at: (_ for _ in ()).throw(IndexError("x"))
    try:
        assert fn.normalized_draw("anything", "word") is None
    finally:
        m.harness.normalize_answer = orig


# ------------------------------------------------------------ bucket rule

def test_bucket_median_tie_fallback_and_drop():
    b, rule = fn.bucket([0, 1, 2, 3, 4, 5])
    assert rule == "median" and b == [0, 0, 0, 1, 1, 1]
    b, rule = fn.bucket([2] * 196 + [3] * 304)          # med = 3: '>' constant
    assert rule == "tie_fallback" and sum(b) == 304
    b, rule = fn.bucket([0] * 400 + [1] * 100)          # med = 0: '>' works
    assert rule == "median" and sum(b) == 100
    b, rule = fn.bucket([1] * 274 + [0] * 226)          # R on antonym: med = 1
    assert rule == "tie_fallback" and sum(b) == 274
    b, rule = fn.bucket([7] * 500)
    assert b is None and rule == "dropped_constant"


def test_bucket_terciles():
    b, rule = fn.bucket_terciles(list(range(9)))
    assert rule == "terciles" and b == [0, 0, 0, 1, 1, 1, 2, 2, 2]
    b, rule = fn.bucket_terciles([5] * 9)
    assert b is None


def test_composite_strata_joins_surviving_functionals_in_order():
    base = {"r": {"strata": ["a", "a", "b", "b"]}}
    tables = {"r": {"pi": [0, 0, 1, 1], "L": [3, 3, 3, 3], "R": [1, 0, 1, 0],
                    "O": [0.0, 0.5, 0.5, 1.0]}}
    strata, report = fn.composite_strata(base, tables, ("r",))
    # R = [1, 0, 1, 0] is a permutation of pi = [0, 0, 1, 1] (same
    # multiset {0, 0, 1, 1}); bucket() is a pure function of the value
    # multiset (median, then a >/>= threshold), so it cannot classify
    # R differently from pi here — confirmed directly against
    # test_bucket_median_tie_fallback_and_drop's own worked cases.
    # Brief's draft had "tie_fallback" for R; corrected to "median".
    assert report["r"] == {"pi": "median", "L": "dropped_constant", "R": "median",
                           "O": "median"}
    assert strata["r"]["strata"] == ["a|0|1|0", "a|0|0|0", "b|1|1|0", "b|1|0|1"]


# --------------------------------------------------- bits, counts, thinner

def test_verified_bits_and_counts():
    cap = _cap([("q0", "3"), ("q1", "5")])
    rows = _rows([[" 3", " x", " 3", " 3"], [" 5", " 5", " x", " x"]])
    verify = a2d.load_verify()
    fn.N_ITEMS, fn.DRAWS_PER_ITEM = 2, 4
    try:
        bits = fn.verified_bits(rows, cap, verify)
        assert bits == [[1, 0, 1, 1], [1, 1, 0, 0]]
        assert fn.counts_from_bits(bits) == [3, 2]
        assert fn.thinned_counts(bits, 2, 0) == [1, 2]
        assert fn.thinned_counts(bits, 2, 1) == [2, 0]
    finally:
        fn.N_ITEMS, fn.DRAWS_PER_ITEM = bi.N_ITEMS, bi.DRAWS_PER_ITEM


def test_matched_k_rule_and_bounds():
    assert fn.matched_k(0.00031, 0.00300) == {"denser": "B", "k": 7, "n_blocks": 9}
    assert fn.matched_k(0.1365, 0.4048)["k"] == 22
    assert fn.matched_k(0.00047, 0.00019) == {"denser": "A", "k": 26, "n_blocks": 2}
    assert fn.matched_k(0.1, 0.1) == {"denser": None, "k": 64, "n_blocks": 1}
    assert fn.matched_k(0.0, 0.5)["k"] == 1                    # clipped low
    assert fn.matched_k(0.0998, 0.1121)["k"] == 57
    assert fn.matched_k(0.5, 0.0) == {"denser": "A", "k": 1, "n_blocks": 64}


def test_zero_fraction_k():
    bits_dense = [[1] * 64, [0] * 63 + [1], [0] * 64, [0] * 64]
    counts_sparse = [1, 0, 0, 0]              # 1/4 positive
    assert fn.zero_fraction_k(bits_dense, counts_sparse) == 1


# ------------------------------------------------- the real item files (§2)

REAL = {  # rung: (distinct answers, repeat-char answers, answer verbatim in question)
    "antonym": (111, 274, 500), "antonym6": (127, 264, 500), "odd6": (80, 166, 500),
    "add_base8": (100, 165, 0), "sub_base8": (52, 44, 74), "arith_next": (136, 111, 0),
    "add3_mid": (418, 222, 0), "sub3_mid": (325, 113, 24), "sub4_mid": (470, 216, 1)}


@pytest.mark.parametrize("rung", sorted(REAL))
def test_design_table_reproduces_on_the_real_item_files(rung):
    cap = bg.load_battery((rung,))[rung]
    ans = [str(it["answer"]) for it in cap["eval_items"]]
    distinct, rep, verb = REAL[rung]
    assert len(set(ans)) == distinct
    assert sum(fn.repeated_char(cap)) == rep
    assert sum(1 for it in cap["eval_items"] if str(it["answer"]) in it["question"]) == verb
    if rung in ("antonym", "antonym6", "odd6"):
        assert fn.bucket(fn.input_overlap(cap))[1] == "dropped_constant"


@pytest.mark.parametrize("rung", ["sub_base8", "antonym"])
def test_bits_reproduce_2i_counts_and_pi_matches_swapped_verify(rung):
    """verified_bits summed == battery_2i.sampler_counts_olmo (the
    production count) on the real committed x_B draws; and the π
    predicate equals verify_fn with the target swapped on a sample."""
    bat = bg.load_battery((rung,))
    verify = a2d.load_verify()
    rows = fn.draw_rows_2i(bi.EXP2I, rung)
    bits = fn.verified_bits(rows, bat[rung], verify)
    prod = bi.sampler_counts_olmo((rung,), root=bi.EXP2I, battery=bat, verify_fn=verify)
    assert fn.counts_from_bits(bits) == prod[rung]
    cap = bat[rung]
    ans = fn.normalized_answers(cap)
    rng = np.random.default_rng(0)
    for _ in range(200):
        i, j, d = rng.integers(500), rng.integers(500), rng.integers(64)
        draw = rows[j]["draws"]["0"][d]
        assert (fn.normalized_draw(draw, cap["answer_type"]) == ans[i]) == \
            bool(verify(draw, cap["eval_items"][i]["answer"], cap["answer_type"]))
