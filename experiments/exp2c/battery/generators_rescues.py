"""Rescues (design §2, cap 6; open item 3). Each names the taxonomy
mechanism it tests; a screen failure is constructive confirmation."""

import math

import numpy as np

from .base import CapabilitySpec, register


def _collatz_step(n: int) -> int:
    return n // 2 if n % 2 == 0 else 3 * n + 1


# Roman numeral helpers, values 1-99: notation matches 2b's to_roman/
# from_roman (experiments/exp2b/battery/generators.py) exactly, but
# deliberately NOT imported from there — 2b battery modules register
# their own specs at import time, and 2c's registry must stay clean of
# 2b side effects. Ruling 2026-07-28: gen returns the numeral-string
# surface (as caesar_len8 returns the transformed surface); int-valued
# gen would have templated as arabic digits in item generation, making
# the suffix-carrier mechanism test vacuous.
_RVAL = [(90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
         (5, "V"), (4, "IV"), (1, "I")]


def _to_roman(n: int) -> str:
    out = []
    for v, s in _RVAL:
        while n >= v:
            out.append(s)
            n -= v
    return "".join(out)


def _from_roman(s: str) -> int:
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    total = 0
    for a, b in zip(s, s[1:] + " "):
        v = vals[a]
        total += -v if b in vals and vals[b] > v else v
    return total


register(CapabilitySpec(
    name="roman_sum7", family="rescue_roman", dial_name="label_carrier",
    dial_value="sum_mod7",
    description="roman numeral addition (values 1-99), sum mod 7",
    answer_type="number",
    probe_label_space="(value(A)+value(B)) mod 7 (0-6)",
    basis_kind="ordered numeral-string pair; single shared holdout over "
               "the union of numeral values (shared-component variant)",
    composability="label requires converting BOTH numerals and adding; "
                  "printed on neither surface",
    dumbest_baseline="2b showed suffix sub-alphabet carries value-mod-10 "
                     "(margins .64-.82); sum-mod-7 is a function of both "
                     "values jointly, not of either suffix; random net "
                     "must fail unless a second carrier exists (that is "
                     "the test)",
    oracle=lambda a, b: (_from_roman(a) + _from_roman(b)) % 7,
    gen=lambda rng: (_to_roman(int(rng.integers(1, 100))),
                     _to_roman(int(rng.integers(1, 100)))),
    seed=20260813, rescue_of="roman",
    mechanism_tested="suffix sub-alphabet carries value-mod-10",
))

register(CapabilitySpec(
    name="collatz_step2", family="rescue_collatz",
    dial_name="label_carrier", dial_value="step2_mod7",
    description="two Collatz steps, second-step result mod 7",
    answer_type="number",
    probe_label_space="second Collatz step mod 7 (0-6)",
    basis_kind="N token (~9990 values)",
    composability="two branch-on-parity steps composed; mod 7 avoids the "
                  "digit alphabet entirely",
    dumbest_baseline="2b: first-step ones digit was N-mod-20-legible from "
                     "final digit tokens (.74-.81); step-2 mod 7 is not a "
                     "function of N mod 20 (depends on N through both "
                     "branches); random net must fail unless deeper "
                     "surface structure exists (the test)",
    oracle=lambda n: _collatz_step(_collatz_step(n)) % 7,
    gen=lambda rng: int(rng.integers(10, 10000)),
    seed=20260814, rescue_of="collatz2",
    mechanism_tested="first step is N-mod-20-legible from digit tokens",
))

register(CapabilitySpec(
    name="isqrt_gap", family="rescue_isqrt", dial_name="label_carrier",
    dial_value="gap_mod7",
    description="integer square root of N (100-9999), remainder mod 7",
    answer_type="number",
    probe_label_space="(N - isqrt(N)^2) mod 7 (0-6)",
    basis_kind="N token (~9900 values)",
    composability="remainder requires the root; oscillates within every "
                  "magnitude band (period ~2*root+1), mod 7 coprime to 10",
    dumbest_baseline="2b: root's ones digit constant on wide contiguous "
                     "bands (.36-.44 untrained); the gap mod 7 changes "
                     "within every band, so magnitude binning scores "
                     "chance; random net must fail unless the remainder "
                     "itself is surface-legible (the test)",
    oracle=lambda n: (n - math.isqrt(n) ** 2) % 7,
    gen=lambda rng: int(rng.integers(100, 10000)),
    seed=20260815, rescue_of="isqrt",
    mechanism_tested="root ones-digit constant on magnitude bands",
))
