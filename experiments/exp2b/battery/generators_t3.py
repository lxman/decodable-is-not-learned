"""Exp 2b capability specs — tranche 3: AMENDMENT #1 candidates (#31–#42),
designed after M1 inclusion left 13 < 20 survivors (design §2 amendment note,
approved by Michael 2026-07-19). Hard, large-answer-space tasks built from the
two measured failure mechanisms: no small answer spaces (the format artifact),
difficulty above 1b's measured range (the ability misjudgments).

Same discipline as tranches 1–2: text-only oracles and basis extractors,
non-additive composability arguments, positional seeds (appended AFTER
tranche 2 — existing item streams unchanged)."""

from __future__ import annotations

import re

from splits import SplitParams

from .base import CapabilitySpec

_LET = "abcdefghijklmnopqrstuvwxyz"


def _ints(q):
    return [int(x) for x in re.findall(r"\d+", q)]


# --------------------------------------------------------------- generators

def _gen_mod13(rng, split):
    a, b = int(rng.integers(100, 1000)), int(rng.integers(100, 1000))
    return f"What is ({a} + {b}) mod 13?", str((a + b) % 13), a % 13


def _gen_sq_mod7(rng, split):
    a, b = int(rng.integers(10, 100)), int(rng.integers(10, 100))
    return f"What is ({a}^2 + {b}) mod 7?", str((a * a + b) % 7), (a * a) % 7


def _gen_digitprod7(rng, split):
    ds = [int(rng.integers(1, 10)) for _ in range(4)]
    n = int("".join(map(str, ds)))
    p = ds[0] * ds[1] * ds[2] * ds[3]
    return (f"What is the product of the digits of {n}, mod 7?",
            str(p % 7), p % 7)


def _gen_numletter(rng, split):
    n = int(rng.integers(10, 1000))
    c = _LET[int(rng.integers(26))]
    p = _LET.index(c) + 1
    return (f"Multiply {n} by the alphabet position of '{c}'. What is the "
            f"result mod 26?", str((n * p) % 26), (n * p) % 26)


def _collatz(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1


def _gen_collatz2(rng, split):
    n = int(rng.integers(10, 10000))
    s1 = _collatz(n)
    return (f"Apply the Collatz rule (if even, halve; if odd, triple and add "
            f"1) twice to {n}. What is the result?", str(_collatz(s1)), s1 % 10)


def _to_base(n, b):
    out = []
    while n:
        out.append(str(n % b))
        n //= b
    return "".join(reversed(out)) or "0"


def _gen_base7(rng, split):
    n = int(rng.integers(10, 10000))
    return f"Write {n} in base 7.", _to_base(n, 7), n % 7


def _gen_oct2dec(rng, split):
    nd = int(rng.integers(3, 5))
    ds = [str(int(rng.integers(1, 8)))] + [str(int(rng.integers(0, 8)))
                                           for _ in range(nd - 1)]
    s = "".join(ds)
    v = int(s, 8)
    return f"What is octal {s} in decimal?", str(v), v % 10


def _gen_addbase8(rng, split):
    a = int(rng.integers(1, 8)) * 8 + int(rng.integers(0, 8))
    b = int(rng.integers(1, 8)) * 8 + int(rng.integers(0, 8))
    ao, bo = _to_base(a, 8), _to_base(b, 8)
    return (f"What is {ao} + {bo} in base 8 (both numbers are octal)?",
            _to_base(a + b, 8), (a % 8 + b % 8) % 8)


def _gen_mul3x1(rng, split):
    a, d = int(rng.integers(100, 1000)), int(rng.integers(2, 10))
    return f"What is {a} * {d}?", str(a * d), (a * d // 10) % 10


def _gen_isqrt(rng, split):
    n = int(rng.integers(100, 10000))
    r = int(n ** 0.5)
    while r * r > n:
        r -= 1
    while (r + 1) * (r + 1) <= n:
        r += 1
    return (f"What is the integer square root (rounded down) of {n}?",
            str(r), r % 10)


def _gen_between(rng, split):
    a = int(rng.integers(10, 900))
    b = a + int(rng.integers(30, 121))
    cnt = b // 7 - (a - 1) // 7
    return (f"How many integers between {a} and {b} (inclusive) are divisible "
            f"by 7?", str(cnt), cnt)


def _gen_clock24(rng, split):
    h = int(rng.integers(0, 24))
    d = int(rng.integers(25, 500))
    return (f"It is {h}:00 on a 24-hour clock. What time will it be in {d} "
            f"hours? Answer as H:00.", f"{(h + d) % 24}:00", (h + d) % 24)


# ------------------------------------------------------------------- oracles

def _oracle_mod13(q):
    a, b = _ints(q)[:2]
    return str((a + b) % 13)


def _oracle_sq_mod7(q):
    m = re.search(r"\((\d+)\^2 \+ (\d+)\) mod 7", q)
    a, b = int(m.group(1)), int(m.group(2))
    return str((a * a + b) % 7)


def _oracle_digitprod7(q):
    n = re.search(r"digits of (\d+)", q).group(1)
    p = 1
    for c in n:
        p *= int(c)
    return str(p % 7)


def _oracle_numletter(q):
    n = int(re.search(r"Multiply (\d+)", q).group(1))
    c = re.search(r"'([a-z])'", q).group(1)
    return str((n * (_LET.index(c) + 1)) % 26)


def _oracle_collatz2(q):
    n = int(re.search(r"twice to (\d+)", q).group(1))
    return str(_collatz(_collatz(n)))


def _oracle_base7(q):
    return _to_base(int(re.search(r"Write (\d+)", q).group(1)), 7)


def _oracle_oct2dec(q):
    return str(int(re.search(r"octal (\d+)", q).group(1), 8))


def _oracle_addbase8(q):
    m = re.search(r"What is (\d+) \+ (\d+) in base 8", q)
    return _to_base(int(m.group(1), 8) + int(m.group(2), 8), 8)


def _oracle_mul3x1(q):
    a, d = _ints(q)[:2]
    return str(a * d)


def _oracle_isqrt(q):
    n = int(re.search(r"of (\d+)\?", q).group(1))
    r = int(n ** 0.5)
    while r * r > n:
        r -= 1
    while (r + 1) * (r + 1) <= n:
        r += 1
    return str(r)


def _oracle_between(q):
    a, b, _ = _ints(q)[:3]
    return str(b // 7 - (a - 1) // 7)


def _oracle_clock24(q):
    h = int(re.search(r"It is (\d+):00", q).group(1))
    d = int(re.search(r"in (\d+) hours", q).group(1))
    return f"{(h + d) % 24}:00"


# --------------------------------------------------------------------- bases

def _basis_first_int(q):
    return (str(_ints(q)[0]),)


def _basis_clock_offset(q):
    return (re.search(r"in (\d+) hours", q).group(1),)


def _basis_octpair_ones(q):
    m = re.search(r"What is (\d+) \+ (\d+) in base 8", q)
    return (f"{m.group(1)[-1]}o{m.group(2)[-1]}",)


def _basis_pair_shared(q):
    a, b = _ints(q)[:2]
    return (str(a), str(b))


def _basis_collatz(q):
    return (re.search(r"twice to (\d+)", q).group(1),)


def _basis_write(q):
    return (re.search(r"Write (\d+)", q).group(1),)


def _basis_octal(q):
    return (re.search(r"octal (\d+)", q).group(1),)


def _basis_isqrt(q):
    return (re.search(r"of (\d+)\?", q).group(1),)


def _basis_mulfirst(q):
    return (str(_ints(q)[0]),)


def _basis_sq(q):
    return (re.search(r"\((\d+)\^2", q).group(1),)


def _basis_numletter(q):
    return (re.search(r"Multiply (\d+)", q).group(1),)


# ----------------------------------------------------------------- T3 SPECS

SPECS_T3 = [
    CapabilitySpec(
        name="mod13", description="(a+b) mod 13, 3-digit operands",
        answer_type="number", probe_label_space="a mod 13 (0-12)",
        basis_kind="first operand token (900 values)",
        composability="mod-13 of a 3-digit number wraps repeatedly: not "
                      "additive in digits",
        shots=[("What is (234 + 567) mod 13?", "8"),
               ("What is (912 + 145) mod 13?", "4")],
        gen=_gen_mod13, oracle=_oracle_mod13, basis_fn=_basis_first_int),
    CapabilitySpec(
        name="sq_mod7", description="(a^2 + b) mod 7, 2-digit operands",
        answer_type="number",
        probe_label_space="a^2 mod 7 (quadratic residues: 0, 1, 2, 4)",
        basis_kind="the squared operand token (90 values)",
        composability="a^2 mod 7 is a nonlinear function of a with the mod "
                      "wrap; not expressible by additive digit scores",
        shots=[("What is (23^2 + 45) mod 7?", "0"),
               ("What is (81^2 + 17) mod 7?", "5")],
        gen=_gen_sq_mod7, oracle=_oracle_sq_mod7, basis_fn=_basis_sq,
        split_params=SplitParams(n_holdout=18)),
    CapabilitySpec(
        name="digitprod7", description="product of 4 digits (1-9), mod 7",
        answer_type="number", probe_label_space="the product mod 7 (0-6)",
        basis_kind="the number token (9^4 = 6561 values)",
        composability="a PRODUCT of digits under a mod wrap is "
                      "multiplicative-interactive, not additive",
        shots=[("What is the product of the digits of 2345, mod 7?", "1"),
               ("What is the product of the digits of 9172, mod 7?", "0")],
        gen=_gen_digitprod7, oracle=_oracle_digitprod7, basis_fn=_basis_first_int),
    CapabilitySpec(
        name="numletter", description="(N x alphabet position) mod 26",
        answer_type="number", probe_label_space="the result (0-25)",
        basis_kind="N token (990 values); letters all seen",
        composability="a product mod 26 for an UNSEEN N cannot be composed "
                      "from per-letter knowledge plus additive N scores",
        shots=[("Multiply 12 by the alphabet position of 'c'. What is the "
                "result mod 26?", "10"),
               ("Multiply 45 by the alphabet position of 'e'. What is the "
                "result mod 26?", "17")],
        gen=_gen_numletter, oracle=_oracle_numletter, basis_fn=_basis_numletter),
    CapabilitySpec(
        name="collatz2", description="two Collatz steps",
        answer_type="number",
        probe_label_space="ones digit of the FIRST-step result (0-9)",
        basis_kind="N token (~9990 values)",
        composability="branch-on-parity then arithmetic: piecewise, not "
                      "additive; the intermediate requires executing step 1",
        shots=[("Apply the Collatz rule (if even, halve; if odd, triple and "
                "add 1) twice to 10. What is the result?", "16"),
               ("Apply the Collatz rule (if even, halve; if odd, triple and "
                "add 1) twice to 15. What is the result?", "23")],
        gen=_gen_collatz2, oracle=_oracle_collatz2, basis_fn=_basis_collatz),
    CapabilitySpec(
        name="base7", description="write N in base 7",
        answer_type="number", probe_label_space="N mod 7 (0-6, the last digit)",
        basis_kind="N token (~9990 values)",
        composability="base conversion is repeated division with remainders: "
                      "chain-nonlocal, wraps at every digit",
        shots=[("Write 10 in base 7.", "13"), ("Write 100 in base 7.", "202")],
        gen=_gen_base7, oracle=_oracle_base7, basis_fn=_basis_write),
    CapabilitySpec(
        name="oct2dec", description="octal to decimal, 3-4 octal digits",
        answer_type="number", probe_label_space="value mod 10 (0-9)",
        basis_kind="octal string (4032 values). SIBLING NOTE: value-mod-10 "
                   "species shared with bin2dec (option-3 treatment)",
        composability="(sum 8^i d_i) mod 10 wraps repeatedly: not additive",
        shots=[("What is octal 234 in decimal?", "156"),
               ("What is octal 1750 in decimal?", "1000")],
        gen=_gen_oct2dec, oracle=_oracle_oct2dec, basis_fn=_basis_octal),
    CapabilitySpec(
        name="add_base8", description="octal addition, 2-digit operands",
        answer_type="number",
        probe_label_space="ones digit of the octal sum (0-7)",
        basis_kind="ones-digit pair in base 8 (64 values)",
        composability="(a0+b0) mod 8: the wrap is non-additive (the base-10 "
                      "add2 lesson applied at base 8, where 1b has no format "
                      "prior)",
        shots=[("What is 23 + 45 in base 8 (both numbers are octal)?", "70"),
               ("What is 34 + 25 in base 8 (both numbers are octal)?", "61")],
        gen=_gen_addbase8, oracle=_oracle_addbase8, basis_fn=_basis_octpair_ones,
        split_params=SplitParams(n_holdout=13, min_holdout_values=13)),
    CapabilitySpec(
        name="mul3x1", description="3-digit x 1-digit multiplication",
        answer_type="number", probe_label_space="tens digit of the product (0-9)",
        basis_kind="the 3-digit operand token (900 values)",
        composability="the product's tens digit rides the carry chain with a "
                      "mod-10 wrap: not additive in (a, d) scores",
        shots=[("What is 234 * 3?", "702"), ("What is 917 * 4?", "3668")],
        gen=_gen_mul3x1, oracle=_oracle_mul3x1, basis_fn=_basis_mulfirst),
    CapabilitySpec(
        name="isqrt", description="integer square root of N (100-9999)",
        answer_type="number", probe_label_space="ones digit of the root (0-9)",
        basis_kind="N token (~9900 values)",
        composability="isqrt is a global nonlinear function of N; its ones "
                      "digit wraps: not additive in digits",
        shots=[("What is the integer square root (rounded down) of 200?", "14"),
               ("What is the integer square root (rounded down) of 5000?", "70")],
        gen=_gen_isqrt, oracle=_oracle_isqrt, basis_fn=_basis_isqrt),
    CapabilitySpec(
        name="count_div7", description="count of multiples of 7 in [a, b]",
        answer_type="number", probe_label_space="the count (~4-18)",
        basis_kind="both endpoint tokens (shared value space)",
        composability="floor(b/7) - floor((a-1)/7): two floors and a "
                      "difference — nonlocal in both endpoints jointly",
        shots=[("How many integers between 10 and 50 (inclusive) are "
                "divisible by 7?", "6"),
               ("How many integers between 100 and 200 (inclusive) are "
                "divisible by 7?", "14")],
        gen=_gen_between, oracle=_oracle_between, basis_fn=_basis_pair_shared,
        split_params=SplitParams(holdout_frac=0.45, min_val_items=300,
                                 shared_components=True),
        n_probe=4000),
    CapabilitySpec(
        name="clock24", description="24-hour clock, +D hours (D 25-499)",
        answer_type="word", probe_label_space="(H+D) mod 24 (0-23)",
        basis_kind="offset token D (475 values). SIBLING NOTE: mod-of-offset "
                   "species shared with weekday (option-3 treatment)",
        composability="D mod 24 wraps over the digit expansion: not additive",
        shots=[("It is 14:00 on a 24-hour clock. What time will it be in 75 "
                "hours? Answer as H:00.", "17:00"),
               ("It is 8:00 on a 24-hour clock. What time will it be in 30 "
                "hours? Answer as H:00.", "14:00")],
        gen=_gen_clock24, oracle=_oracle_clock24, basis_fn=_basis_clock_offset),
]
