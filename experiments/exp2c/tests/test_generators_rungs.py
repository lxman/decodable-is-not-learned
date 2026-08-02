import numpy as np

from experiments.exp2c.battery import generators_rungs as g
from experiments.exp2c.battery.base import SPECS, validate_spec
from experiments.exp2c.battery.wordlists_2c import WORDS_7_8

EXPECTED = ["add4_mid", "sub4_mid", "base12", "base12_digitsum", "sub_base8",
            "mod17", "mod19", "mod13_comp", "caesar_len8", "count_div13",
            "clock24_d999", "rev_string7", "letter_sum", "letter_prod",
            "hamming8", "hamming12", "median5", "median7", "arith_next",
            "quad_next", "odd6"]


def test_all_registered_and_valid():
    for name in EXPECTED:
        assert name in SPECS, name
        assert validate_spec(SPECS[name]) == []


def test_base5_ejected_not_registered():
    # Ruling 2026-07-28: base5 is a banned digit-local label (N mod 5 = f
    # of the last decimal digit, since 10 = 0 mod 5) -- ejected at design
    # time, kept only as the record of the catch.
    assert "base5" in g.EJECTED
    assert "base5" not in SPECS
    spec, reason = g.EJECTED["base5"]
    assert spec.name == "base5"
    assert "last decimal digit" in reason
    assert "mod 5" in reason.lower() or "mod5" in reason.lower()


def test_caesar_len8_pool_is_wordlists_2c():
    # Ruling 2026-07-28: caesar_len8 draws from the new 2c 7-8 letter
    # wordlist, not a 9-word slice of 2b's frozen WORDS.
    assert g.CAESAR_LEN8_WORDS == sorted(WORDS_7_8)
    assert len(g.CAESAR_LEN8_WORDS) >= 1400


def test_wordlists_2c_sanity():
    # Floor set at 1400 (re-review finding): headroom below the shipped
    # 1522 for legitimate future scrubs, far above the starved-pool
    # failure regime the 550 floor would have tolerated.
    assert len(WORDS_7_8) >= 1400
    assert len(set(WORDS_7_8)) == len(WORDS_7_8)
    assert all(w.isalpha() and w.islower() for w in WORDS_7_8)
    assert all(len(w) in (7, 8) for w in WORDS_7_8)
    assert len({w[0] for w in WORDS_7_8}) >= 20


def test_add4_mid_oracle():
    # 1234 + 8765 = 9999 -> hundreds digit 9; 4999 + 5001 = 10000 -> 0
    assert SPECS["add4_mid"].oracle(1234, 8765) == 9
    assert SPECS["add4_mid"].oracle(4999, 5001) == 0


def test_mod17_oracle_label_is_first_operand():
    assert SPECS["mod17"].oracle(659, 800) == 659 % 17


def test_gen_deterministic():
    s = SPECS["mod17"]
    a = s.gen(np.random.default_rng(s.seed))
    b = s.gen(np.random.default_rng(s.seed))
    assert a == b


def test_base12_digitsum_oracle():
    # 7369 -> base12 "4321" -> digit sum 4+3+2+1=10 -> mod 5 = 0
    # 200   -> base12 "148"  -> digit sum 1+4+8=13   -> mod 5 = 3
    # 9999  -> base12 "5953" -> digit sum 5+9+5+3=22 -> mod 5 = 2
    # A/B letter-digit path (review fix 2026-07-30: the letters carry
    # their VALUES, A=10 and B=11, into the sum):
    # 130   -> base12 "AA"   -> digit sum 10+10=20   -> mod 5 = 0
    # 143   -> base12 "BB"   -> digit sum 11+11=22   -> mod 5 = 2
    # (hand-verified independently against a fresh _to_base12 reimplementation
    # before use; see task-12r-report.md)
    assert SPECS["base12_digitsum"].oracle(7369) == 0
    assert SPECS["base12_digitsum"].oracle(200) == 3
    assert SPECS["base12_digitsum"].oracle(9999) == 2
    assert SPECS["base12_digitsum"].oracle(130) == 0
    assert SPECS["base12_digitsum"].oracle(143) == 2
    # general-form check: independent divmod-loop digit-sum, mirroring
    # test_isqrt_gap_oracle's style (no reuse of the module's _to_base12).
    # 130 ("AA"), 143 ("BB"), and 1548 ("A90") keep the letter-digit path
    # covered here too.
    for n in (130, 143, 201, 500, 1548, 1728, 4096, 8888, 9998):
        total, m = 0, n
        while m:
            m, r = divmod(m, 12)
            total += r
        assert SPECS["base12_digitsum"].oracle(n) == total % 5


def test_base12_digitsum_surface_answer_matches_base12():
    # surface_answer is the same base-12 string renderer base12 uses.
    assert SPECS["base12_digitsum"].surface_answer(7369) == "4321"
    assert SPECS["base12_digitsum"].surface_answer is SPECS["base12"].surface_answer


def test_base12_digitsum_rescue_route_left_unset():
    # Ruling (task-12r): every existing rescue_of/mechanism_tested holder
    # (roman_sum7, collatz_step2, isqrt_gap) carries a family named
    # "rescue_<x>"; base12_digitsum's family is pinned to "base_repr"
    # (matching base12's own family, not a rescue_ family), which
    # contradicts that naming convention even though validate_spec's
    # mechanical check would accept rescue_of="base12" on its own. Route
    # taken: leave rescue_of/mechanism_tested unset and carry the
    # fire->silence contrast in dumbest_baseline only.
    s = SPECS["base12_digitsum"]
    assert s.rescue_of is None and s.mechanism_tested is None
    assert s.family == "base_repr"
    assert "base12" in s.dumbest_baseline
    assert "CRT" in s.dumbest_baseline


# ---------------------------------------------------------------- pos_letter
# F3 growth rungs (growth-proposal.md §3, accepted 2026-08-01): 8-letter
# uniform random string S, i,j in [1,8], read position p = ((i op j) mod 6)
# + 2 (1-indexed, interior 2-7 only), probe label = the letter at p. The
# question asks for the letter directly, so surface_answer is None and
# answer == probe_label (the rescue-style shape, not Fix A's).

def test_pos_letter_registered_and_valid():
    for name in ("letter_sum", "letter_prod"):
        assert name in SPECS, name
        assert validate_spec(SPECS[name]) == []
        s = SPECS[name]
        assert s.family == "pos_letter"
        assert s.dial_name == "index_op"
        assert s.answer_type == "word"
        assert s.surface_answer is None
        assert s.rescue_of is None and s.mechanism_tested is None
    assert SPECS["letter_sum"].dial_value == "sum"
    assert SPECS["letter_prod"].dial_value == "prod"
    # seeds per the accepted proposal (contiguous growth block)
    assert SPECS["letter_sum"].seed == 20260824
    assert SPECS["letter_prod"].seed == 20260825


def test_letter_sum_oracle():
    # p = ((i+j) mod 6) + 2, 1-indexed. Hand-worked on 'qwertyui'
    # (all-distinct letters, no position/letter aliasing):
    # i=3,j=5: (8 mod 6)+2 = 4  -> 'r'
    # i=8,j=8: (16 mod 6)+2 = 6 -> 'y'
    # i=2,j=4: (6 mod 6)+2 = 2  -> 'w'  (p floor: never position 1)
    # i=2,j=3: (5 mod 6)+2 = 7  -> 'u'  (p ceiling: never position 8)
    o = SPECS["letter_sum"].oracle
    assert o("qwertyui", 3, 5) == "r"
    assert o("qwertyui", 8, 8) == "y"
    assert o("qwertyui", 2, 4) == "w"
    assert o("qwertyui", 2, 3) == "u"


def test_letter_prod_oracle():
    # p = ((i*j) mod 6) + 2, same string:
    # i=3,j=5: (15 mod 6)+2 = 5 -> 't'
    # i=2,j=3: (6 mod 6)+2 = 2  -> 'w'
    # i=1,j=1: (1 mod 6)+2 = 3  -> 'e'
    # i=7,j=8: (56 mod 6)+2 = 4 -> 'r'
    o = SPECS["letter_prod"].oracle
    assert o("qwertyui", 3, 5) == "t"
    assert o("qwertyui", 2, 3) == "w"
    assert o("qwertyui", 1, 1) == "e"
    assert o("qwertyui", 7, 8) == "r"


def test_pos_letter_gen_shape_and_interior_positions():
    for name, op in (("letter_sum", lambda i, j: i + j),
                     ("letter_prod", lambda i, j: i * j)):
        s = SPECS[name]
        rng = np.random.default_rng(s.seed)
        seen_p = set()
        for _ in range(500):
            S, i, j = s.gen(rng)
            assert len(S) == 8 and S.isalpha() and S.islower()
            assert 1 <= i <= 8 and 1 <= j <= 8
            p = (op(i, j) % 6) + 2
            seen_p.add(p)
            assert s.oracle(S, i, j) == S[p - 1]
        # interior only (2-7): first/last letter never read (leak class 6
        # and the final-BPE-chunk carrier are dodged by construction)
        assert seen_p == set(range(2, 8))


def test_pos_letter_position_distribution():
    # The proposal's position-uniformity check, pinned by enumeration over
    # all 64 (i,j) pairs via the public oracle on 'abcdefgh' (letter at p
    # identifies p): sum is near-uniform (10-12 of 64 per slot); prod
    # concentrates 21/64 on p=2 (products cluster on 0 mod 6) -- the named
    # F3b risk the tier-1 screen adjudicates, stated at full strength in
    # the spec text.
    from collections import Counter
    S = "abcdefgh"
    for name, expected in (
            ("letter_sum", {2: 10, 3: 10, 4: 11, 5: 12, 6: 11, 7: 10}),
            ("letter_prod", {2: 21, 3: 5, 4: 14, 5: 7, 6: 13, 7: 4})):
        o = SPECS[name].oracle
        c = Counter(S.index(o(S, i, j)) + 1
                    for i in range(1, 9) for j in range(1, 9))
        assert dict(c) == expected, name


def test_pos_letter_gen_deterministic():
    for name in ("letter_sum", "letter_prod"):
        s = SPECS[name]
        a = s.gen(np.random.default_rng(s.seed))
        b = s.gen(np.random.default_rng(s.seed))
        assert a == b


# ----------------------------------------------------------------- str_align
# F4 reserve, PROMOTED 2026-08-02 under §7's pre-ruled fallback after
# pos_letter's full-family tier-1 ejection. Two equal-length random
# strings over the 4-letter alphabet {a,b,c,d}; probe label = Hamming
# match count (0..L). The question asks for the count directly:
# surface_answer None, answer == probe_label.

def test_str_align_registered_and_valid():
    for name, L in (("hamming8", 8), ("hamming12", 12)):
        assert name in SPECS, name
        assert validate_spec(SPECS[name]) == []
        s = SPECS[name]
        assert s.family == "str_align"
        assert s.dial_name == "length"
        assert s.dial_value == L
        assert s.answer_type == "number"
        assert s.surface_answer is None
        assert s.rescue_of is None and s.mechanism_tested is None
    # reserve seeds, assigned only on promotion (proposal §0/§3)
    assert SPECS["hamming8"].seed == 20260826
    assert SPECS["hamming12"].seed == 20260827
    # label-tail ruling 2026-08-02 (Michael: "follow your recommendation"):
    # capped label spaces stated in the spec text itself
    assert "0-5" in SPECS["hamming8"].probe_label_space
    assert "0-7" in SPECS["hamming12"].probe_label_space


def test_hamming_oracle():
    # hand-worked vectors:
    # identical strings -> L; disjoint letters -> 0;
    # 'abcaabca' vs 'abcbabcb': matches at 1,2,3,5,6,7 (1-indexed) -> 6
    o8 = SPECS["hamming8"].oracle
    assert o8("abcdabcd", "abcdabcd") == 8
    assert o8("aaaaaaaa", "bbbbbbbb") == 0
    assert o8("abcaabca", "abcbabcb") == 6
    # 12-length: 'abcdabcdabcd' vs 'abcdabcddcba' -> first 9 match
    # (positions 1-8 all match, position 9 a=a b=d? no: 9th char of s1 is
    # 'a', of s2 'd' -> mismatch; hand count below = 8 + 1 (position 12?
    # s1[11]='d', s2[11]='a' -> no). Exact: zip pairs
    # (a,a)(b,b)(c,c)(d,d)(a,a)(b,b)(c,c)(d,d)(a,d)(b,c)(c,b)(d,a) -> 8
    o12 = SPECS["hamming12"].oracle
    assert o12("abcdabcdabcd", "abcdabcddcba") == 8
    assert o12("abcdabcdabcd", "abcdabcdabcd") == 12


def test_hamming_gen_shape_and_label_range():
    # label-tail ruling 2026-08-02: gen rejection-samples pairs whose
    # match count exceeds the cap (5 for L=8, 7 for L=12), so the label
    # space is exact-by-construction, not nominal. 1000 draws must both
    # respect the cap and REACH it (min tail class ~2.3%/~1.2%).
    for name, L, cap in (("hamming8", 8, 5), ("hamming12", 12, 7)):
        s = SPECS[name]
        rng = np.random.default_rng(s.seed)
        seen = set()
        for _ in range(1000):
            s1, s2 = s.gen(rng)
            assert len(s1) == L and len(s2) == L
            assert set(s1) <= set("abcd") and set(s2) <= set("abcd")
            lab = s.oracle(s1, s2)
            assert lab == sum(a == b for a, b in zip(s1, s2))
            assert 0 <= lab <= cap
            seen.add(lab)
        assert seen == set(range(cap + 1)), (name, seen)


def test_hamming_gen_deterministic():
    for name in ("hamming8", "hamming12"):
        s = SPECS[name]
        a = s.gen(np.random.default_rng(s.seed))
        b = s.gen(np.random.default_rng(s.seed))
        assert a == b


# ------------------------------------------------- wave 2 (blessing 2026-08-02)
# order_stat (median5/median7): position label under randomized
# presentation, first-printed-number basis per the approved consolidated
# blessing (the mod17-lesson reduction; the proposal's shared-components
# basis collapsed the AND-split at k>=5, PROGRESS 2026-08-02).
# seq_extrap (arith_next/quad_next): next-term label mod 7, basis = first
# printed term (growth ruling). odd6: the odd_one_out sibling at 6 words
# over CATEGORIES_2C, 6-comp shared basis (2b family precedent figures).

def test_wave2_registered_and_valid():
    expect = {
        "median5": ("order_stat", "set_size", 5, 20260820),
        "median7": ("order_stat", "set_size", 7, 20260821),
        "arith_next": ("seq_extrap", "degree", 1, 20260822),
        "quad_next": ("seq_extrap", "degree", 2, 20260823),
        "odd6": ("odd_one_out", "n_words", 6, 20260819),
    }
    for name, (fam, dial, dv, seed) in expect.items():
        assert name in SPECS, name
        assert validate_spec(SPECS[name]) == []
        s = SPECS[name]
        assert s.family == fam and s.dial_name == dial
        assert s.dial_value == dv and s.seed == seed
        assert s.rescue_of is None and s.mechanism_tested is None
        # all five ask for a task result distinct from the probe label:
        # median value / next term / odd word, never the position or mod
        assert s.surface_answer is not None, name


def test_median_oracle_and_surface():
    # median5 printed (512, 130, 987, 344, 700): sorted 130,344,512,700,
    # 987 -> median 512 sits at printed slot 1; surface answer = 512.
    s5 = SPECS["median5"]
    assert s5.oracle(512, 130, 987, 344, 700) == 1
    assert s5.surface_answer(512, 130, 987, 344, 700) == 512
    # printed (200, 900, 500, 300, 400): median 400 at slot 5
    assert s5.oracle(200, 900, 500, 300, 400) == 5
    assert s5.surface_answer(200, 900, 500, 300, 400) == 400
    # median7 printed (300,100,200,700,500,600,400): median 400, slot 7
    s7 = SPECS["median7"]
    assert s7.oracle(300, 100, 200, 700, 500, 600, 400) == 7
    assert s7.surface_answer(300, 100, 200, 700, 500, 600, 400) == 400


def test_median_gen_shape():
    for name, n in (("median5", 5), ("median7", 7)):
        s = SPECS[name]
        rng = np.random.default_rng(s.seed)
        seen_pos = set()
        for _ in range(400):
            vals = s.gen(rng)
            assert len(vals) == n == len(set(vals))
            assert all(100 <= v <= 999 for v in vals)
            pos = s.oracle(*vals)
            seen_pos.add(pos)
            assert vals[pos - 1] == sorted(vals)[n // 2]
            assert s.surface_answer(*vals) == sorted(vals)[n // 2]
        # the median's slot is shuffle-uniform: all n positions reached
        assert seen_pos == set(range(1, n + 1))


def test_arith_next_oracle():
    # terms 11,13,15,17 (a=11,d=2): next 19, label 19 mod 7 = 5.
    # The 2t3 - t2 identity IS the oracle (2*17-15 = 19).
    s = SPECS["arith_next"]
    assert s.surface_answer(11, 13, 15, 17) == 19
    assert s.oracle(11, 13, 15, 17) == 5
    # 10,30,50,70 -> 90, label 90 mod 7 = 6
    assert s.surface_answer(10, 30, 50, 70) == 90
    assert s.oracle(10, 30, 50, 70) == 6


def test_quad_next_oracle():
    # a=10,d=2,q=1: terms 10,13,18,25 -> t4 = 34 (identity: 3*25-3*18+13);
    # label 34 mod 7 = 6. Proposal's max case a=99,d=20,q=9: terms
    # 99,128,175,240 -> t4 = 323, label 323 mod 7 = 1.
    s = SPECS["quad_next"]
    assert s.surface_answer(10, 13, 18, 25) == 34
    assert s.oracle(10, 13, 18, 25) == 6
    assert s.surface_answer(99, 128, 175, 240) == 323
    assert s.oracle(99, 128, 175, 240) == 1


def test_seq_extrap_gen_shape():
    # arith_next: strictly increasing 4-term run, a in [10,99], d in
    # [2,20]; quad_next: t_k = a + d*k + q*k^2, q in [1,9] (second
    # difference 2q >= 2, never degenerate to arith).
    s = SPECS["arith_next"]
    rng = np.random.default_rng(s.seed)
    for _ in range(400):
        t = s.gen(rng)
        d = t[1] - t[0]
        assert t == (t[0], t[0] + d, t[0] + 2 * d, t[0] + 3 * d)
        assert 10 <= t[0] <= 99 and 2 <= d <= 20
    s = SPECS["quad_next"]
    rng = np.random.default_rng(s.seed)
    for _ in range(400):
        t = s.gen(rng)
        d2a = t[2] - 2 * t[1] + t[0]
        d2b = t[3] - 2 * t[2] + t[1]
        assert d2a == d2b and d2a % 2 == 0 and d2a >= 2  # 2q constant
        q = d2a // 2
        d = (t[1] - t[0]) - q
        assert 10 <= t[0] <= 99 and 2 <= d <= 20 and 1 <= q <= 9
        assert t[0] < t[1] < t[2] < t[3]


def test_odd6_oracle_and_surface():
    # five insects + one gemstone: odd word 'opal' at printed slot 3.
    words = ("ant", "bee", "opal", "wasp", "moth", "beetle")
    s = SPECS["odd6"]
    assert s.oracle(*words) == 3
    assert s.surface_answer(*words) == "opal"
    # odd word at the last slot: five fabrics + a sport
    words = ("cotton", "silk", "wool", "denim", "satin", "judo")
    assert s.oracle(*words) == 6
    assert s.surface_answer(*words) == "judo"


def test_odd6_gen_shape():
    from experiments.exp2c.battery.wordlists_2c import CATEGORIES_2C
    cat_of = {w: c for c, ms in CATEGORIES_2C.items() for w in ms}
    s = SPECS["odd6"]
    rng = np.random.default_rng(s.seed)
    seen_pos = set()
    for _ in range(400):
        words = s.gen(rng)
        assert len(words) == 6 == len(set(words))
        cats = [cat_of[w] for w in words]
        # exactly 5 from one category + 1 from another
        odd = [w for w, c in zip(words, cats) if cats.count(c) == 1]
        assert len(odd) == 1
        pos = s.oracle(*words)
        seen_pos.add(pos)
        assert words[pos - 1] == odd[0] == s.surface_answer(*words)
    assert seen_pos == set(range(1, 7))


def test_wave2_gen_deterministic():
    for name in ("median5", "median7", "arith_next", "quad_next", "odd6"):
        s = SPECS[name]
        a = s.gen(np.random.default_rng(s.seed))
        b = s.gen(np.random.default_rng(s.seed))
        assert a == b
