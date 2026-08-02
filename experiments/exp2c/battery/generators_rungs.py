"""New rungs for survivor-derived families (design §2). Every spec's
basis and dumbest-baseline text is written against the tokenizer, not
task intuition; digit-local labels are banned (bin2dec lesson: no label
sharing a modulus with the surface digit alphabet).

Two flags surfaced during implementation (task-4 report has the full
writeup) and were adjudicated by Michael on 2026-07-28:

- base5: N mod 5 IS a banned digit-local label (gcd(5,10)=5, so it
  reduces to N's last base-10 digit mod 5 — the bin2dec species at a
  different modulus). RULING: ejected at design time (not registered);
  the CapabilitySpec definition is kept below as the record of the
  catch and filed in EJECTED with the mechanism. base12 fills the
  base_repr slot per the design's "base-5 or base-12".
- caesar_len8: the committed word pool (experiments/exp2b/battery/
  wordlists.py WORDS) has only 9 words of length 7-8 across 7 distinct
  first letters (max class size 2) — nowhere near the class coverage
  2b's caesar needed (n_holdout=39, min_holdout_values=26). RULING:
  rewired to draw from the new 2c pool, wordlists_2c.WORDS_7_8 (this
  module is 2c's own, not frozen), which has real class coverage.
"""

import numpy as np

from .base import CapabilitySpec, register
from .wordlists_2c import WORDS_7_8

_ALPHA = "abcdefghijklmnopqrstuvwxyz"


def _shift(s, k):
    return "".join(_ALPHA[(_ALPHA.index(c) + k) % 26] for c in s)


# Review ruling 2026-07-29 (Fix A): specs whose question text demands the
# full task result carry a surface_answer callable computing that result;
# `oracle` keeps computing the probe label only. base12's surface uses
# hex-style letter digits for 10/11, per its own description ("values
# 10/11 are letters in the surface answer only").
_B12_DIGITS = "0123456789AB"


def _to_base12(n):
    out = ""
    while n:
        out, n = _B12_DIGITS[n % 12] + out, n // 12
    return out or "0"


# --------------------------------------------------------- caesar_len8 pool
# 2c's own wordlist (design §2 ruling 2026-07-28), not a slice of 2b's
# frozen wordlists.py: real class coverage (>=550 words, >=20 distinct
# first letters), see wordlists_2c.py.
CAESAR_LEN8_WORDS = sorted(WORDS_7_8)


# ------------------------------------------------------------------ EJECTED
# Design-time ejections: CapabilitySpec kept as the record of the catch,
# never registered into SPECS. dict[name] -> (spec, reason).
EJECTED: dict = {}


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
    surface_answer=lambda a, b: a + b,
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
    surface_answer=lambda a, b: a - b,
    gen=_gen_sub4_mid,
    seed=20260802,
))

# base5: EJECTED at design time (ruling 2026-07-28) — kept as the record
# of the catch, deliberately NOT passed to register(). See EJECTED below.
_base5_spec = CapabilitySpec(
    name="base5", family="base_repr", dial_name="base", dial_value=5,
    description="write N in base 5, last digit of the representation "
                "(N in [200,9999])",
    answer_type="number",
    probe_label_space="N mod 5, last base-5 digit (0-4)",
    basis_kind="EJECTED (design §2, ruling 2026-07-28): digit-local, not "
              "a real composition basis. N mod 5 depends only on N's "
              "last base-10 digit because gcd(5,10)=5 (10 = 0 mod 5) — "
              "exactly the value-mod-10 species design §2 bans, one "
              "divisor down from bin2dec's mod-10",
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
                     "2b's 25 candidates to attrition — ejected before "
                     "tier-1, not silently pre-filtered",
    oracle=lambda n: n % 5,
    gen=lambda rng: (int(rng.integers(200, 10000)),),
    seed=20260803,
)
EJECTED["base5"] = (
    _base5_spec,
    "design-time ban (design §2): N mod 5 = f(last decimal digit) since "
    "10 ≡ 0 (mod 5) — the value-mod-10/bin2dec class. Ejected on "
    "Michael's ruling 2026-07-28; base12 fills the base_repr slot per "
    "the design's 'base-5 or base-12'.",
)

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
    surface_answer=_to_base12,
    gen=lambda rng: (int(rng.integers(200, 10000)),),
    seed=20260804,
))

def _oracle_base12_digitsum(n):
    return sum(_B12_DIGITS.index(c) for c in _to_base12(n)) % 5


# base12_digitsum: replacement rung for base12's tier-1 ejection (task-12
# step 2, ruling 2026-07-30). base12's own preregistered dumbest_baseline
# argued a digit-suffix lookup fails structurally for N mod 12, but missed
# the CRT decomposition: N mod 12 factors into N mod 3 (the decimal digit
# sum) and N mod 4 (the last two decimal digits), both classic surface
# carriers -- exactly what caught base12 four-for-four with
# structural_abort. This rung moves the label off modular arithmetic
# entirely: not N mod 12, but the digit-SUM of the base-12 representation,
# mod 5. base12's registration above stays untouched as the ejection
# record.
register(CapabilitySpec(
    name="base12_digitsum", family="base_repr", dial_name="label_carrier",
    dial_value="digitsum_mod5",
    description="write N in base 12, digit-sum of the representation mod "
                "5 (N in [200,9999]; surface answer is the base-12 string, "
                "values 10/11 are letters in the surface answer only)",
    answer_type="number",
    probe_label_space="digit-sum of the base-12 representation, mod 5 "
                      "(0-4)",
    basis_kind="N token (~9800 values in [200,9999])",
    composability="the digit-sum depends on every digit of the base-12 "
                  "quotient chain (base12's own repeated-division chain, "
                  "not a single trailing readout); digit-sum_12(N) is "
                  "congruent to N mod 11, but only as a congruence -- the "
                  "sum itself is not a modular function of N, so no fixed "
                  "digit position determines it. 5 is coprime to each of "
                  "3, 4, and 11, so none of the surface-legible "
                  "congruences (mod 3 via the decimal digit sum, mod 4 "
                  "via the last two decimal digits, mod 11 via the "
                  "congruence above) determines the digit-sum-mod-5 "
                  "label -- no CRT shortcut from the decimal surface "
                  "exists",
    dumbest_baseline="2c tier-1 caught base12 with structural_abort x4 -- "
                     "its label N mod 12 CRT-decomposes into mod-3 (the "
                     "decimal digit-sum carrier) and mod-4 (the last-two-"
                     "digits carrier), a mechanism base12's own "
                     "preregistered dumbest_baseline reasoned away. Those "
                     "two carriers determine N mod 12 exactly but do not "
                     "determine the base-12 digit-sum mod 5; random net "
                     "must fail unless a second, independent carrier "
                     "exists (that is the test)",
    oracle=_oracle_base12_digitsum,
    surface_answer=_to_base12,
    gen=lambda rng: (int(rng.integers(200, 10000)),),
    seed=20260816,
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
    surface_answer=lambda a, b: format(a - b, "o"),
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
    surface_answer=lambda a, b: (a + b) % 17,
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
    surface_answer=lambda a, b: (a + b) % 19,
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
    surface_answer=lambda a, b, c: ((a + b) * c) % 13,
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
    basis_kind="(first cipher letter, shift) combo, drawn from "
              "wordlists_2c.WORDS_7_8 (1500+ words, 24 distinct first "
              "letters) per Michael's ruling 2026-07-28 — replaces the "
              "prior 9-word slice of 2b's frozen wordlists.py, which fell "
              "far short of caesar's own ~130-value basis (n_holdout=39, "
              "min_holdout_values=26 in the 2b split)",
    composability="the class for an unseen (letter, k) combo requires the "
                  "alphabet rotation, not a memorized combo table — same "
                  "mechanism as caesar, now with pool size adequate to "
                  "test it",
    dumbest_baseline="combo-table lookup on held-out (letter, k) pairs "
                     "scores chance on starved val once the pool is large "
                     "enough for a real split (wordlists_2c.WORDS_7_8, "
                     "ruling 2026-07-28) — the 9-word pool that made a "
                     "memorized table plausibly complete is retired",
    oracle=_oracle_caesar_len8,
    surface_answer=lambda enc, k: _shift(enc, 26 - k),
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

# ---------------------------------------------------------------- pos_letter
# F3 growth family (growth-proposal.md §3, ACCEPTED 2026-08-01; basis ruled
# string-as-basis, ruling 2). A data-dependent gather: compute an index from
# two printed integers, read the letter at that index of a printed random
# string. Interior positions only (2-7, 1-indexed): the first-letter carrier
# (leak class 6) and the final-BPE-chunk carrier (reverse_string's Exp-2
# mechanism) never see the label. Uniform random letters kill the English
# letter-frequency shortcut. Position-distribution arithmetic (enumerated
# over all 64 (i,j) pairs, pinned in test_pos_letter_position_distribution):
#   sum:  p in 2..7 at 10,10,11,12,11,10 of 64 -- near-uniform, max 0.1875
#   prod: p in 2..7 at 21, 5,14, 7,13, 4 of 64 -- 0.328 concentrated on p=2
#         (products cluster on 0 mod 6), the named F3b risk; screened FIRST
#         in the growth build wave per proposal §6.

def _gen_pos_letter(rng):
    s = "".join(_ALPHA[int(rng.integers(26))] for _ in range(8))
    i = int(rng.integers(1, 9))
    j = int(rng.integers(1, 9))
    return (s, i, j)


def _oracle_letter_sum(s, i, j):
    return s[((i + j) % 6) + 1]     # 0-indexed p-1 for p = ((i+j) mod 6) + 2


def _oracle_letter_prod(s, i, j):
    return s[((i * j) % 6) + 1]


register(CapabilitySpec(
    name="letter_sum", family="pos_letter", dial_name="index_op",
    dial_value="sum",
    description="read the letter at position p = ((i+j) mod 6) + 2 "
                "(1-indexed, interior 2-7 only) of a printed random "
                "8-letter string; i, j in [1,8] printed alongside",
    answer_type="word",
    probe_label_space="the letter at p (a-z, 26 nominal; split stratified "
                      "by label)",
    basis_kind="the printed string S itself, per-string holdout (string-"
              "as-basis ruling 2026-08-01, the N-token-basis shape): every "
              "S is fresh-random over 26^8, so held-out val items always "
              "carry strings the probe never trained on and a string-to-"
              "label lookup starves by construction",
    composability="a variable-index gather: the read position is computed "
                  "from two printed integers, then the letter is fetched "
                  "from that data-dependent slot of a different printed "
                  "token -- non-local in (i, j, S) jointly; random "
                  "projections are weak at variable-index gather, and that "
                  "weakness is what the rung tests. Position distribution "
                  "is near-uniform for the sum op (10-12 of 64 per slot, "
                  "max 0.1875), so no fixed slot dominates",
    dumbest_baseline="honest disclosure (ruling 2026-08-01): the position "
                     "arithmetic is inherently UNSTARVABLE -- i and j are "
                     "printed and p = ((i+j) mod 6) + 2 is low-complexity, "
                     "so no holdout removes position computability; what "
                     "the per-string holdout starves is the string, "
                     "leaving exactly the gather-from-a-fresh-string "
                     "capability under test. A fixed-slot reader gets the "
                     "right position at most 18.75% of draws and the right "
                     "letter only if slot-letter identity is decodable "
                     "from untrained activations at all -- reverse_string, "
                     "the fixed-position precedent, read 0.000 untrained "
                     "under starving. The tier-1/tier-2 untrained screen "
                     "is the arbiter of the variable-index gather",
    oracle=_oracle_letter_sum,
    gen=_gen_pos_letter,
    seed=20260824,
))

register(CapabilitySpec(
    name="letter_prod", family="pos_letter", dial_name="index_op",
    dial_value="prod",
    description="read the letter at position p = ((i*j) mod 6) + 2 "
                "(1-indexed, interior 2-7 only) of a printed random "
                "8-letter string; i, j in [1,8] printed alongside",
    answer_type="word",
    probe_label_space="the letter at p (a-z, 26 nominal; split stratified "
                      "by label)",
    basis_kind="the printed string S itself, per-string holdout (string-"
              "as-basis ruling 2026-08-01, the N-token-basis shape): every "
              "S is fresh-random over 26^8, so held-out val items always "
              "carry strings the probe never trained on and a string-to-"
              "label lookup starves by construction",
    composability="the same variable-index gather as letter_sum with the "
                  "index op moved to the product: i*j mod 6 changes the "
                  "index distribution, which is the family dial. Named at "
                  "full strength: products cluster on 0 mod 6, so p=2 "
                  "absorbs 21/64 = 0.328 of draws (vs 0.167 uniform) -- "
                  "the position-concentration risk the proposal flags for "
                  "F3b specifically, and why this rung screens FIRST in "
                  "the growth build wave (proposal §6)",
    dumbest_baseline="honest disclosure (ruling 2026-08-01): position "
                     "arithmetic UNSTARVABLE as letter_sum's (i, j "
                     "printed; low-complexity map); the per-string holdout "
                     "starves only the string. The sharpest fixed-slot "
                     "attack: always read slot 2 -- right position 32.8% "
                     "of draws, plus 1/26 coincidence elsewhere, is ~0.35 "
                     "accuracy against a ~0.04 chance floor IF slot-2 "
                     "letter identity is linearly decodable from untrained "
                     "activations; reverse_string's fixed-position 0.000 "
                     "precedent says it is not, and the untrained screen "
                     "adjudicates exactly this before the rung can enter "
                     "the battery",
    oracle=_oracle_letter_prod,
    gen=_gen_pos_letter,
    seed=20260825,
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
    surface_answer=lambda s: s[::-1],
    gen=_gen_rev_string7,
    seed=20260812,
))
