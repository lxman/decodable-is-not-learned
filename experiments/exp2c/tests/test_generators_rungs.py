import numpy as np

from experiments.exp2c.battery import generators_rungs as g
from experiments.exp2c.battery.base import SPECS, validate_spec
from experiments.exp2c.battery.wordlists_2c import WORDS_7_8

EXPECTED = ["add4_mid", "sub4_mid", "base12", "base12_digitsum", "sub_base8",
            "mod17", "mod19", "mod13_comp", "caesar_len8", "count_div13",
            "clock24_d999", "rev_string7"]


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
