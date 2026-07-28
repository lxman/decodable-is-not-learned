import numpy as np

from experiments.exp2c.battery import generators_rungs as g
from experiments.exp2c.battery.base import SPECS, validate_spec

EXPECTED = ["add4_mid", "sub4_mid", "base5", "base12", "sub_base8",
            "mod17", "mod19", "mod13_comp", "caesar_len8", "count_div13",
            "clock24_d999", "rev_string7"]


def test_all_registered_and_valid():
    for name in EXPECTED:
        assert name in SPECS, name
        assert validate_spec(SPECS[name]) == []


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
