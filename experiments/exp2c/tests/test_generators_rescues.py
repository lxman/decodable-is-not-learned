from experiments.exp2c.battery import generators_rescues  # noqa: F401
from experiments.exp2c.battery.base import SPECS, validate_spec
import math


def test_registered_with_mechanisms():
    for name in ("roman_sum7", "collatz_step2", "isqrt_gap"):
        s = SPECS[name]
        assert validate_spec(s) == []
        assert s.rescue_of and s.mechanism_tested


def test_roman_sum7_oracle():
    # LXVII(67) + LXXXVII(87) = 154 -> 154 % 7 = 0
    assert SPECS["roman_sum7"].oracle(67, 87) == 0


def test_collatz_step2_oracle():
    # N=10: 5, then 16 -> 16 % 7 = 2 ; N=15: 46, then 23 -> 23 % 7 = 2
    assert SPECS["collatz_step2"].oracle(10) == 2
    assert SPECS["collatz_step2"].oracle(15) == 2


def test_isqrt_gap_oracle():
    # N=9470: isqrt 97, 97^2=9409, gap 61 -> 61 % 7 = 5
    assert SPECS["isqrt_gap"].oracle(9470) == 5
    for n in (100, 101, 9999):
        r = math.isqrt(n)
        assert SPECS["isqrt_gap"].oracle(n) == (n - r * r) % 7
