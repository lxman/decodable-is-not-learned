import numpy as np

from experiments.exp2c.battery import generators_rungs as g
from experiments.exp2c.battery.base import SPECS, validate_spec
from experiments.exp2c.battery.wordlists_2c import WORDS_7_8

EXPECTED = ["add4_mid", "sub4_mid", "base12", "sub_base8",
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
    assert len(g.CAESAR_LEN8_WORDS) >= 550


def test_wordlists_2c_sanity():
    assert len(WORDS_7_8) >= 550
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
