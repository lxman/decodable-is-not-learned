"""New rungs for survivor-derived families (design §2). Every spec's
basis and dumbest-baseline text is written against the tokenizer, not
task intuition; digit-local labels are banned (bin2dec lesson: no label
sharing a modulus with the surface digit alphabet).

Two flags surfaced during implementation (task-4 report has the full
writeup):

- base5: N mod 5 IS a banned digit-local label (gcd(5,10)=5, so it
  reduces to N's last base-10 digit mod 5 — the bin2dec species at a
  different modulus). Registered anyway, self-flagged in its basis_kind
  text, per the 2b alpha_offset precedent (register a candidate known
  to be structurally doomed so the tier-1 screen adjudicates and
  records the rejection formally, rather than a silent pre-filter that
  leaves no record). Not silently redesigned to a different modulus.
- caesar_len8: the committed word pool (experiments/exp2b/battery/
  wordlists.py WORDS) has only 9 words of length 7-8 across 7 distinct
  first letters (max class size 2) — nowhere near the class coverage
  2b's caesar needed (n_holdout=39, min_holdout_values=26). Registered
  with the real 9-word pool and flagged; expected to fail tier-1
  feasibility screening as constructed.
"""

import ast
from pathlib import Path

import numpy as np

from .base import CapabilitySpec, register

_ALPHA = "abcdefghijklmnopqrstuvwxyz"


def _shift(s, k):
    return "".join(_ALPHA[(_ALPHA.index(c) + k) % 26] for c in s)


# --------------------------------------------------------- caesar_len8 pool
# Read (not imported) from the frozen experiments/exp2b/battery/wordlists.py
# per the task-4 brief's binding constraint. Filtered to 7-8 letter entries
# at module load; see the module docstring for the resulting feasibility
# concern (only 9 words survive the filter).
_WORDLISTS_PATH = (Path(__file__).resolve().parents[2] / "exp2b" / "battery"
                   / "wordlists.py")
_WORDLISTS_SRC = _WORDLISTS_PATH.read_text()
_ALL_WORDS = next(
    ast.literal_eval(node.value)
    for node in ast.parse(_WORDLISTS_SRC).body
    if isinstance(node, ast.Assign)
    and len(node.targets) == 1
    and getattr(node.targets[0], "id", None) == "WORDS"
)
# feather, journal, machine, mistake, special, veteran, weather, witness,
# keyboard — 9 words, 7 distinct first letters, max class size 2.
CAESAR_LEN8_WORDS = sorted(w for w in _ALL_WORDS if len(w) in (7, 8))


def _gen_caesar_len8(rng):
    w = CAESAR_LEN8_WORDS[int(rng.integers(len(CAESAR_LEN8_WORDS)))]
    k = int(rng.integers(1, 6))
    return (_shift(w, k), k)


def _oracle_caesar_len8(enc, k):
    return _shift(enc, 26 - k)[0]


# --------------------------------------------------------------- other gens

def _gen_sub4_mid(rng):
    a = int(rng.integers(1001, 10000))
    b = int(rng.integers(1000, a))
    return (a, b)


def _gen_sub_base8(rng):
    # both operands two-digit octal numerals (decimal 8-63); a > b
    a = int(rng.integers(9, 64))
    b = int(rng.integers(8, a))
    return (a, b)


def _gen_mod13_comp(rng):
    a = int(rng.integers(100, 1000))
    b = int(rng.integers(100, 1000))
    c = int(rng.integers(2, 10))
    return (a, b, c)


def _gen_count_div13(rng):
    a = int(rng.integers(10, 900))
    b = a + int(rng.integers(30, 121))
    return (a, b)


def _gen_clock24_d999(rng):
    h = int(rng.integers(0, 24))
    d = int(rng.integers(500, 1000))
    return (h, d)


def _gen_rev_string7(rng):
    s = "".join(_ALPHA[int(rng.integers(26))] for _ in range(7))
    return (s,)


register(CapabilitySpec(
    name="add4_mid", family="mid_digit", dial_name="digits", dial_value=4,
    description="4-digit addition, hundreds digit of the sum",
    answer_type="number",
    probe_label_space="hundreds digit of a+b (0-9)",
    basis_kind="hundreds-digit pair of the operands (100 values)",
    composability="the hundreds digit of the sum depends on the carry out "
                  "of the tens column: two-deep carry chain, not additive "
                  "in per-operand scores",
    dumbest_baseline="lookup on the hundreds-digit pair scores chance on "
                     "starved val (pairs held out); random net cannot "
                     "express the carry composition (2b: add3_mid untrained "
                     "0.000 every cell)",
    oracle=lambda a, b: (a + b) // 100 % 10,
    gen=lambda rng: (int(rng.integers(1000, 10000)),
                     int(rng.integers(1000, 10000))),
    seed=20260801,
))

register(CapabilitySpec(
    name="sub4_mid", family="mid_digit", dial_name="digits", dial_value=4,
    description="4-digit subtraction, hundreds digit of the difference (a>b)",
    answer_type="number",
    probe_label_space="hundreds digit of a-b (0-9)",
    basis_kind="hundreds-digit pair of the operands (100 values)",
    composability="the hundreds digit of the difference depends on the "
                  "borrow out of the tens column: the subtractive mirror "
                  "of add4_mid's carry chain, not additive in per-operand "
                  "scores",
    dumbest_baseline="lookup on the hundreds-digit pair scores chance on "
                     "starved val (pairs held out); random net cannot "
                     "express the borrow composition, the same mechanism "
                     "class as 2b's sub3_mid (closed-record survivor)",
    oracle=lambda a, b: (a - b) // 100 % 10,
    gen=_gen_sub4_mid,
    seed=20260802,
))

register(CapabilitySpec(
    name="base5", family="base_repr", dial_name="base", dial_value=5,
    description="write N in base 5, last digit of the representation "
                "(N in [200,9999])",
    answer_type="number",
    probe_label_space="N mod 5, last base-5 digit (0-4)",
    basis_kind="FLAGGED (task-4): digit-local, not a real composition "
              "basis. N mod 5 depends only on N's last base-10 digit "
              "because gcd(5,10)=5 (10 = 0 mod 5) — exactly the "
              "value-mod-10 species design §2 bans, one divisor down "
              "from bin2dec's mod-10. Registered per the 2b alpha_offset "
              "precedent (self-flagged expected-eject) rather than "
              "silently redesigned or silently dropped",
    composability="none: a single trailing-digit readout suffices; no "
                  "carry or multi-digit composition is required, the "
                  "opposite of base7's chain-nonlocal repeated-division "
                  "basis",
    dumbest_baseline="last-decimal-digit lookup (10 classes, every class "
                     "seen in training by construction) solves this "
                     "exactly on starved val; an untrained random-"
                     "projection net is expected to decode it "
                     "structurally, the same failure mode that closed "
                     "Exp 2's mod7-family lookup class and drove 13 of "
                     "2b's 25 candidates to attrition — flagged for "
                     "tier-1 rejection, not silently pre-filtered",
    oracle=lambda n: n % 5,
    gen=lambda rng: (int(rng.integers(200, 10000)),),
    seed=20260803,
))

register(CapabilitySpec(
    name="base12", family="base_repr", dial_name="base", dial_value=12,
    description="write N in base 12, last digit of the representation "
                "(N in [200,9999]; probe label 0-11, values 10/11 are "
                "letters in the surface answer only)",
    answer_type="number",
    probe_label_space="N mod 12, last base-12 digit as an integer (0-11)",
    basis_kind="N token (~9800 values in [200,9999])",
    composability="10^k mod 12 runs 1, 10, 4, 4, 4, ... for k=0,1,2,3,...; "
                  "unlike base5 (10 = 0 mod 5, single-digit-readable), 12 "
                  "never divides a power of 10 (12=4*3 and 3 never divides "
                  "10^k), so N mod 12 requires composing every digit's "
                  "contribution — base7's chain-nonlocal pattern at a "
                  "different base, not base5's leak",
    dumbest_baseline="a last-digit (or last-two-digit) lookup fails "
                     "structurally, unlike base5: N mod 12 is not a "
                     "function of any fixed-width digit suffix alone, so "
                     "starved val cannot be solved from a single surface "
                     "token; matches base7's accepted 2b precedent",
    oracle=lambda n: n % 12,
    gen=lambda rng: (int(rng.integers(200, 10000)),),
    seed=20260804,
))

register(CapabilitySpec(
    name="sub_base8", family="base_arith", dial_name="op", dial_value="sub",
    description="octal subtraction, ones digit of the difference, "
                "two-digit octal operands (a>b)",
    answer_type="number",
    probe_label_space="ones digit of octal a-b (0-7)",
    basis_kind="ones-digit pair in base 8 (64 values), the subtractive "
              "mirror of add_base8's basis",
    composability="(a0-b0) mod 8 with a borrow from the eights place when "
                  "a0<b0: the borrow mirror of add_base8's carry wrap, not "
                  "additive in (a0,b0) scores",
    dumbest_baseline="ones-digit-pair lookup scores chance on starved val "
                     "(pairs held out); the borrow composition is the "
                     "accepted add_base8 mechanism run in reverse (2b "
                     "closed-record survivor family)",
    oracle=lambda a, b: (a - b) % 8,
    gen=_gen_sub_base8,
    seed=20260805,
))

register(CapabilitySpec(
    name="mod17", family="modulus", dial_name="modulus", dial_value=17,
    description="(a+b) mod 17, 3-digit operands",
    answer_type="number",
    probe_label_space="a mod 17 (0-16)",
    basis_kind="first operand token (900 values)",
    composability="mod-17 of a 3-digit number requires composing all "
                  "three digits; 17 is coprime to 10 (no digit shortcut)",
    dumbest_baseline="operand-token lookup starved by construction; "
                     "random net: mod-13 analog read 0.000 untrained in "
                     "2b, mod-17 strictly harder for digit statistics",
    oracle=lambda a, b: a % 17,
    gen=lambda rng: (int(rng.integers(100, 1000)),
                     int(rng.integers(100, 1000))),
    seed=20260806,
))

register(CapabilitySpec(
    name="mod19", family="modulus", dial_name="modulus", dial_value=19,
    description="(a+b) mod 19, 3-digit operands",
    answer_type="number",
    probe_label_space="a mod 19 (0-18)",
    basis_kind="first operand token (900 values)",
    composability="mod-19 of a 3-digit number requires composing all "
                  "three digits; 19 is coprime to 10 (no digit shortcut), "
                  "same structure as mod17 at a larger residue count",
    dumbest_baseline="operand-token lookup starved by construction; "
                     "random net: the mod13/mod17 family reads at floor "
                     "untrained in 2b/2c screening, mod19 strictly harder "
                     "for digit statistics (more residue classes to leak "
                     "through the same random projections)",
    oracle=lambda a, b: a % 19,
    gen=lambda rng: (int(rng.integers(100, 1000)),
                     int(rng.integers(100, 1000))),
    seed=20260807,
))

register(CapabilitySpec(
    name="mod13_comp", family="modulus", dial_name="depth", dial_value=2,
    description="((a+b)*c) mod 13, 3-digit a,b and single-digit c "
                "(2-9); probe label is the first-stage intermediate",
    answer_type="number",
    probe_label_space="(a+b) mod 13 (0-12), computed before the *c step",
    basis_kind="first operand token (900 values); the multiplier c is "
              "drawn independently and does not enter the label",
    composability="the probed value is an intermediate computed before "
                  "the final *c mod 13 step: composition depth 2, testing "
                  "whether the model represents (a+b) mod 13 en route to "
                  "the full expression rather than only the surface-"
                  "adjacent final digit",
    dumbest_baseline="operand-token lookup starved by construction, as "
                     "mod13; a shortcut keyed on the FINAL answer's "
                     "surface tokens cannot recover the intermediate "
                     "without redoing the addition — depth-2 composition "
                     "is the point of the rung, not incidental",
    oracle=lambda a, b, c: (a + b) % 13,
    gen=_gen_mod13_comp,
    seed=20260808,
))

register(CapabilitySpec(
    name="caesar_len8", family="rotation", dial_name="word_len",
    dial_value="7-8",
    description="decode a Caesar shift (k stated, 1-5) of a 7-8 letter "
                "word",
    answer_type="word",
    probe_label_space="first letter of the decoded word",
    basis_kind="FLAGGED (task-4): (first cipher letter, shift) combo, but "
              "drawn from only 9 words at this length in the committed "
              "pool (experiments/exp2b/battery/wordlists.py WORDS, read "
              "not imported) across 7 distinct first letters, max class "
              "size 2 — far short of caesar's own ~130-value basis "
              "(n_holdout=39, min_holdout_values=26 in the 2b split). No "
              "held-out split with adequate class coverage is achievable "
              "from this pool as constructed",
    composability="the class for an unseen (letter, k) combo requires the "
                  "alphabet rotation, not a memorized combo table — same "
                  "mechanism as caesar, undermined here by pool size, not "
                  "by the mechanism itself",
    dumbest_baseline="with only 9 words, a small memorized combo table is "
                     "plausibly complete rather than starved; expected to "
                     "fail tier-1 feasibility screening as constructed "
                     "(flagged, not silently dropped — see task-4 report)",
    oracle=_oracle_caesar_len8,
    gen=_gen_caesar_len8,
    seed=20260809,
))

register(CapabilitySpec(
    name="count_div13", family="counting", dial_name="divisor",
    dial_value=13,
    description="count of multiples of 13 in [a,b] (inclusive)",
    answer_type="number",
    probe_label_space="the count (~1-10)",
    basis_kind="both endpoint tokens (shared value space)",
    composability="floor(b/13) - floor((a-1)/13): two floors and a "
                  "difference — nonlocal in both endpoints jointly, the "
                  "count_div7 pattern at a larger divisor",
    dumbest_baseline="endpoint lookup starved by shared-component "
                     "splitting (as count_div7); the floor-difference "
                     "composition is not additive in either endpoint "
                     "alone, matching count_div7's accepted 2b precedent",
    oracle=lambda a, b: b // 13 - (a - 1) // 13,
    gen=_gen_count_div13,
    seed=20260810,
))

register(CapabilitySpec(
    name="clock24_d999", family="clock", dial_name="D_max", dial_value=999,
    description="24-hour clock, +D hours (D in [500,999])",
    answer_type="word",
    probe_label_space="(H+D) mod 24 (0-23)",
    basis_kind="offset token D (500 values in [500,999]); wider dial than "
              "clock24's D in [25,499]",
    composability="D mod 24 wraps over the digit expansion (24=8*3, and 3 "
                  "never divides a power of 10 — no digit-position "
                  "shortcut, the same non-reduction argument as base12); "
                  "not additive",
    dumbest_baseline="offset-token lookup starved by construction; "
                     "matches clock24's accepted 2b precedent — this rung "
                     "tests whether the mod-24 composition holds at a "
                     "wider, entirely disjoint offset range",
    oracle=lambda h, d: (h + d) % 24,
    gen=_gen_clock24_d999,
    seed=20260811,
))

register(CapabilitySpec(
    name="rev_string7", family="reversal", dial_name="len", dial_value=7,
    description="reverse a random 7-letter string",
    answer_type="word",
    probe_label_space="last letter of the 7-letter input (26)",
    basis_kind="final BPE chunk of the input string (as reverse_string; "
              "random strings share final chunks, so the chunk, not the "
              "string, is the lookup unit)",
    composability="last-letter-of-unseen-chunk requires linking a token "
                  "to its spelling — model knowledge, not lookup. Fixed "
                  "length 7 removes reverse_string's variable-length "
                  "class-coverage complication (every item is the same "
                  "length; only the letters vary)",
    dumbest_baseline="final-chunk lookup on held-out chunks scores chance "
                     "on starved val; matches reverse_string's accepted "
                     "2b precedent (closed-record survivor)",
    oracle=lambda s: s[-1],
    gen=_gen_rev_string7,
    seed=20260812,
))
