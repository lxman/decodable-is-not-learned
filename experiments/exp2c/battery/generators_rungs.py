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
from .wordlists_2c import CATEGORIES_2C, WORDS_7_8

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

# ----------------------------------------------------------------- str_align
# F4 reserve, PROMOTED 2026-08-02 under §7's pre-ruled fallback: pos_letter
# ejected as a full family at tier-1 (structural_abort x8), so str_align
# enters with its reserve seeds, restoring the 35-rung B2 shape. Spec at
# build rigor from proposal §3 F4; screened at the front of its own wave
# (MEDIUM-HIGH). The alphabet arithmetic, shown so a skeptic can check it:
# over a 26-letter alphabet two random strings match per position with
# p=1/26, so P(zero matches over L=8) = (25/26)^8 ~= 0.73 -- the label is
# ~always 0, degenerate (LCP is worse: P(LCP=0) = 25/26). The 4-letter
# alphabet {a,b,c,d} gives p=1/4 and a real spread: Binomial(8, 1/4) =
# {0:.10, 1:.27, 2:.31, 3:.21, 4:.09, 5:.02, >=6:.004}, modal 2,
# effective ~5 classes (Binomial(12, 1/4) adds classes: {0:.03, 1:.13,
# 2:.23, 3:.26, 4:.19, 5:.10, 6:.04, 7:.01}). The same alphabet choice
# WORSENS the named shared-chunk carrier (frequent coincidental shared
# 2-grams the tokenizer can emit as shared chunks) -- the two pressures
# trade off, which is why this family was rated drop-first and reserve.

# Label-tail ruling 2026-08-02 (Michael, "follow your recommendation" on
# the ledgered table): the frozen starving_split demands full label-class
# coverage and the Binomial tails cannot supply it (hamming8 infeasible
# at its assigned seed on a match-count-7 singleton, hamming12 outright).
# Remedy ruled: rejection-sample the tail at generation -- cap 5 for L=8
# (labels 0-5 exact, min class ~92 per 4000; rejects P(>=6) ~= 0.0042 of
# pairs) and cap 7 for L=12 (labels 0-7 exact, min class ~46 per 4000;
# rejects P(>=8) ~= 0.0028), keeping the richer label space on the
# 12-length rung so the length dial retains its wider-count-range story.
# The oracle stays exact on every printed pair; only the generator's
# acceptance set changed.

_HAM_ALPHA = "abcd"


def _gen_hamming(rng, L, cap):
    while True:
        s1 = "".join(_HAM_ALPHA[int(rng.integers(4))] for _ in range(L))
        s2 = "".join(_HAM_ALPHA[int(rng.integers(4))] for _ in range(L))
        if sum(a == b for a, b in zip(s1, s2)) <= cap:
            return (s1, s2)


def _oracle_hamming(s1, s2):
    return sum(a == b for a, b in zip(s1, s2))


register(CapabilitySpec(
    name="hamming8", family="str_align", dial_name="length", dial_value=8,
    description="two random 8-letter strings over the alphabet {a,b,c,d}; "
                "count the positions where they have the same letter "
                "(labels 0-5; pairs with count >= 6 rejection-sampled out "
                "at generation, label-tail ruling 2026-08-02)",
    answer_type="number",
    probe_label_space="Hamming match count, 0-5 exact by construction "
                      "(6-class; the Binomial(8,1/4) tail >= 6, jointly "
                      "~0.4% of pairs, is rejection-sampled out per the "
                      "2026-08-02 ruling -- the proposal's 9-class "
                      "'nominal' space was infeasible under the frozen "
                      "split's full-class-coverage requirement)",
    basis_kind="both printed strings (shared_components over their "
              "union, holdout 0.45 -- the count_div13/roman_sum7 "
              "shared-2-component shape); strings are fresh-random over "
              "4^8, so held-out val items carry string values the probe "
              "never trained on",
    composability="a position-wise alignment reduction: compare the two "
                  "strings slot by slot and count agreements -- a 2-D "
                  "interaction over the pair, non-additive in either "
                  "string alone. No data-dependent index anywhere: the "
                  "pos_letter ejection (2026-08-02, structural_abort x8) "
                  "killed the variable-index gather whose read position "
                  "was surface-computable; here every comparison position "
                  "is fixed and the label is a whole-sequence reduction",
    dumbest_baseline="the named carriers (proposal §3 F4): length-count "
                     "legibility (the match count correlates with how "
                     "many BPE chunks the two quoted strings share) and "
                     "the shared-chunk carrier (a 4-letter alphabet makes "
                     "coincidental shared 2-grams frequent, and the "
                     "tokenizer can emit them as shared chunks a random "
                     "projection can detect). The screen adjudicates "
                     "whether untrained nets count aligned chunk "
                     "coincidences well enough to beat the null; the "
                     "family was rated drop-first on exactly this "
                     "tension and is screened FIRST in its wave",
    oracle=_oracle_hamming,
    gen=lambda rng: _gen_hamming(rng, 8, 5),
    seed=20260826,
))

register(CapabilitySpec(
    name="hamming12", family="str_align", dial_name="length", dial_value=12,
    description="two random 12-letter strings over the alphabet {a,b,c,d}; "
                "count the positions where they have the same letter "
                "(labels 0-7; pairs with count >= 8 rejection-sampled out "
                "at generation, label-tail ruling 2026-08-02)",
    answer_type="number",
    probe_label_space="Hamming match count, 0-7 exact by construction "
                      "(8-class; the Binomial(12,1/4) tail >= 8, jointly "
                      "~0.3% of pairs, is rejection-sampled out per the "
                      "2026-08-02 ruling -- richer than hamming8's 0-5 so "
                      "the length dial keeps its wider-count-range story)",
    basis_kind="both printed strings (shared_components over their "
              "union, holdout 0.45 -- the count_div13/roman_sum7 "
              "shared-2-component shape); strings are fresh-random over "
              "4^12, so held-out val items carry string values the probe "
              "never trained on",
    composability="the same position-wise alignment reduction as "
                  "hamming8 with the dial moved to length 12: more "
                  "comparison slots, a wider count range (Binomial(12,"
                  "1/4) populates classes 0-7 robustly vs hamming8's "
                  "0-5), and a longer reduction chain. No data-dependent "
                  "index (see hamming8 and the pos_letter ejection "
                  "record)",
    dumbest_baseline="hamming8's carriers at greater length: more "
                     "positions means more coincidental shared chunks "
                     "for a random projection to count, but also a "
                     "longer reduction to compose. Within-family "
                     "secondary expectation: if the family survives, "
                     "the 12-length margin sits below the 8-length one; "
                     "if shared-chunk counting is expressible untrained, "
                     "BOTH lengths fire and the family ejects -- the "
                     "screen adjudicates",
    oracle=_oracle_hamming,
    gen=lambda rng: _gen_hamming(rng, 12, 7),
    seed=20260827,
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


# ------------------------------------------------- wave 2 (blessed 2026-08-02)
# Built under the approved consolidated feasibility blessing (PROGRESS
# 2026-08-02): order_stat rungs on the first-printed-number basis (the
# mod17-lesson single-component reduction -- the proposal's all-components
# shared basis collapses the AND-split at k>=5: train 158-223 of 8000 at
# k=5, infeasible outright at k=7); arith_next at the sub_base8 figures
# (0.35/1000, its 1,710-run space < the 2,500 default); quad_next and
# odd6 as proposed (odd6 keeps the 2b odd_one_out family figures
# 0.45/8000, flagged costs accepted: train ~342, one sweep seed at 40
# redraws).

def _gen_median(rng, n):
    vals = rng.choice(np.arange(100, 1000), size=n, replace=False)
    return tuple(int(v) for v in vals)


def _oracle_median(*vals):
    med = sorted(vals)[len(vals) // 2]
    return vals.index(med) + 1          # printed slot, 1-indexed


def _surface_median(*vals):
    return sorted(vals)[len(vals) // 2]


register(CapabilitySpec(
    name="median5", family="order_stat", dial_name="set_size", dial_value=5,
    description="which of 5 distinct 3-digit integers (printed in random "
                "order) is the median; answer = the median value, probe "
                "label = its printed position",
    answer_type="number",
    probe_label_space="printed position of the median (1-5), "
                      "shuffle-uniform over the slots",
    basis_kind="first printed number (900 values) -- consolidated "
              "blessing 2026-08-02: the mod17-lesson single-component "
              "reduction; the proposal's all-components shared basis "
              "collapses the AND-split at k=5 (train side 158-223 of "
              "8000 at feasible holdouts; sweep ledgered 2026-08-02)",
    composability="the k-th order statistic is a rank interaction: "
                  "non-additive in any single element, requiring the "
                  "full pairwise comparison across the set. The median's "
                  "position is translation-invariant (add any constant "
                  "to all five numbers and the slot is unchanged), so "
                  "the label is not a function of absolute magnitude; "
                  "all elements share the 3-digit token width, blunting "
                  "digit-count banding",
    dumbest_baseline="first-number lookup starved by construction; a "
                     "set-to-position lookup cannot generalize (every "
                     "printed set is fresh over C(900,5) draws). Fires "
                     "if a random net partially ranks by crude "
                     "per-position magnitude proxies (leading digits) "
                     "well enough to guess the median slot above "
                     "chance -- median, not min/max, precisely because "
                     "extremes correlate with gross magnitude while the "
                     "median needs the full ranking; the untrained "
                     "screen adjudicates",
    oracle=_oracle_median,
    surface_answer=_surface_median,
    gen=lambda rng: _gen_median(rng, 5),
    seed=20260820,
))

register(CapabilitySpec(
    name="median7", family="order_stat", dial_name="set_size", dial_value=7,
    description="which of 7 distinct 3-digit integers (printed in random "
                "order) is the median; answer = the median value, probe "
                "label = its printed position",
    answer_type="number",
    probe_label_space="printed position of the median (1-7), "
                      "shuffle-uniform over the slots",
    basis_kind="first printed number (900 values) -- same blessed "
              "reduction as median5, applied uniformly so both family "
              "rungs starve identically (the 7-component shared basis "
              "is infeasible at every swept holdout)",
    composability="median5's rank interaction at 7 elements: a 7-way "
                  "ranking with 21 pairwise comparisons vs median5's "
                  "10 -- the set-size dial raises the comparison count; "
                  "translation-invariance and equal token width as "
                  "median5",
    dumbest_baseline="as median5; the 7-way rank is strictly harder to "
                     "leak through random projections than the 5-way "
                     "(within-family secondary expects the 7-slot "
                     "margin below the 5-slot one if the family "
                     "survives); the untrained screen adjudicates",
    oracle=_oracle_median,
    surface_answer=_surface_median,
    gen=lambda rng: _gen_median(rng, 7),
    seed=20260821,
))


def _gen_arith_next(rng):
    a = int(rng.integers(10, 100))
    d = int(rng.integers(2, 21))
    return (a, a + d, a + 2 * d, a + 3 * d)


def _gen_quad_next(rng):
    a = int(rng.integers(10, 100))
    d = int(rng.integers(2, 21))
    q = int(rng.integers(1, 10))
    return (a, a + d + q, a + 2 * d + 4 * q, a + 3 * d + 9 * q)


register(CapabilitySpec(
    name="arith_next", family="seq_extrap", dial_name="degree",
    dial_value=1,
    description="arithmetic run a, a+d, a+2d, a+3d (a in [10,99], d in "
                "[2,20]); answer = the next term (not printed); probe "
                "label = next term mod 7",
    answer_type="number",
    probe_label_space="(a+4d) mod 7 (7-class)",
    basis_kind="first printed term a (90 values) -- growth ruling: "
              "holding out a starves the a-to-label lookup and avoids "
              "the joint-AND trap of a multi-component basis (the mod17 "
              "lesson). Reduced pool blessed 2026-08-02: the (a,d) "
              "space is 1,710 runs < the 2,500 default, so n_probe "
              "1000 at holdout 0.35 (the sub_base8 figures; 1,500 of "
              "1,710 runs used)",
    composability="rule inference (first differences constant), one "
                  "application, then a modular reduction off the digit "
                  "alphabet; non-local in the shown terms",
    dumbest_baseline="named at full strength (proposal §3 F2): a+4d = "
                     "2*t3 - t2 identically, so the label is (2*t3 - "
                     "t2) mod 7 with no inference required. The defense "
                     "is not that the label is off the surface -- it "
                     "isn't -- but that evaluating the functional "
                     "requires the mod-7 residue of multi-digit printed "
                     "tokens (the full-digit composition base7 cleared "
                     "at untrained 0.000), composed across two tokens; "
                     "the screen adjudicates",
    oracle=lambda t0, t1, t2, t3: (2 * t3 - t2) % 7,
    surface_answer=lambda t0, t1, t2, t3: 2 * t3 - t2,
    gen=_gen_arith_next,
    seed=20260822,
))

register(CapabilitySpec(
    name="quad_next", family="seq_extrap", dial_name="degree",
    dial_value=2,
    description="quadratic run t_k = a + d*k + q*k^2, k=0..3 (a in "
                "[10,99], d in [2,20], q in [1,9]); answer = the next "
                "term t_4 (not printed); probe label = t_4 mod 7",
    answer_type="number",
    probe_label_space="t_4 = (a + 4d + 16q) mod 7 (7-class; uniform to "
                      "within +/-1 over the 15,390-triple box -- counts "
                      "2198/2199 per class by enumeration; 15,390 = "
                      "7*2198 + 4, so EXACT uniformity is impossible. "
                      "Corrected 2026-08-02: the proposal's 'exactly "
                      "uniform, verified by enumeration' misread its own "
                      "enumeration output)",
    basis_kind="first printed term a (90 values) -- same ruled "
              "reduction as arith_next; the (a,d,q) map is injective "
              "onto printed runs (15,390 distinct), so the default "
              "2,500-item target fits with room",
    composability="one inference level deeper than arith_next: three "
                  "first differences (d+q, d+3q, d+5q), two second "
                  "differences (both 2q, constant -- q >= 1 keeps 2q >= "
                  "2, never degenerating into the arithmetic rung), "
                  "recover the step, apply once, reduce mod 7",
    dumbest_baseline="named at full strength (proposal §3 F2, "
                     "finalization catch): third differences of a "
                     "quadratic vanish, so t_4 = 3*t3 - 3*t2 + t1 "
                     "EXACTLY -- the label is a fixed linear functional "
                     "of three printed terms mod 7, no inference "
                     "required. Defense: the mod-7 residues of "
                     "multi-digit tokens composed across THREE tokens "
                     "(base7's cleared mechanism at three-fold "
                     "composition). Disclosed surface bit: t_4's parity "
                     "equals t_0's (4d+16q even), and gcd(2,7)=1 means "
                     "parity determines nothing about the 7-class "
                     "label; the screen adjudicates",
    oracle=lambda t0, t1, t2, t3: (3 * t3 - 3 * t2 + t1) % 7,
    surface_answer=lambda t0, t1, t2, t3: 3 * t3 - 3 * t2 + t1,
    gen=_gen_quad_next,
    seed=20260823,
))


_CAT_OF = {w: c for c, ms in CATEGORIES_2C.items() for w in ms}


def _gen_odd6(rng):
    cats = list(CATEGORIES_2C)
    i1, i2 = (int(x) for x in rng.choice(len(cats), size=2, replace=False))
    five = [str(w) for w in rng.choice(CATEGORIES_2C[cats[i1]], size=5,
                                       replace=False)]
    odd = str(CATEGORIES_2C[cats[i2]][int(rng.integers(8))])
    pos = int(rng.integers(6))
    return tuple(five[:pos] + [odd] + five[pos:])


def _oracle_odd6(*words):
    cats = [_CAT_OF[w] for w in words]
    return next(i + 1 for i, c in enumerate(cats) if cats.count(c) == 1)


def _surface_odd6(*words):
    return words[_oracle_odd6(*words) - 1]


register(CapabilitySpec(
    name="odd6", family="odd_one_out", dial_name="n_words", dial_value=6,
    description="which of 6 words is not like the others (5 from one "
                "CATEGORIES_2C category + 1 from another); answer = the "
                "odd word, probe label = its printed position",
    answer_type="word",
    probe_label_space="printed position of the odd word (1-6), "
                      "shuffle-assigned",
    basis_kind="the odd word alone (1-comp, 80 values; holdout 0.30 -> "
              "24 held values, val ~30% of items) -- RE-BLESSED "
              "2026-08-02 on Michael's ruling, superseding the "
              "originally blessed all-six-words shared basis (0.45/"
              "8000): the wave-2 review showed that plan cleared its "
              "floors only when the holdout swallowed one complete "
              "8-word category, making starved val 88-100% a single "
              "category with correlated seeds. With the odd word held "
              "out, val items' odd words are unseen while the split "
              "stays non-degenerate; the word-set-to-position lookup "
              "left unstarved cannot generalize (position is "
              "shuffle-random)",
    composability="category-membership comparison across all six words "
                  "-- an interaction, not an additive score (the reused "
                  "odd_one_out mechanism at 6 words: 15 pairwise "
                  "comparisons vs 6 at the reused rung's 4 words)",
    dumbest_baseline="position under a randomized presentation is not a "
                     "function of any surface token (2b odd_one_out: "
                     "untrained margin 0.000 every cell). Fires if a "
                     "CATEGORIES_2C category is morphologically "
                     "clustered or length-skewed (leak class 5/6) -- the "
                     "§2(c) vocab hygiene criteria are programmatic in "
                     "test_wordlists_2c.py (no >=3-letter fragment "
                     "shared by >=3 members, mean-length band 4.0-6.0, "
                     ">=5 first letters per category) and the list is "
                     "hand-approved (ruling 3 closed 2026-08-02); the "
                     "screen adjudicates the residue",
    oracle=_oracle_odd6,
    surface_answer=_surface_odd6,
    gen=_gen_odd6,
    seed=20260819,
))


# ------------------------------------------------------------------ wave 3
# base13 (proposal §2a, seed 20260817) and antonym6 (§2b, 20260818): the
# LOW-risk rungs, built last per §6 now that every risky slot has
# resolved (pos_letter ejected -> str_align promoted + passed; wave 2
# screened). Both take pure-default split plans per the approved
# blessing table.

_B13_DIGITS = "0123456789ABC"


def _to_base13(n):
    out = ""
    while n:
        out, n = _B13_DIGITS[n % 13] + out, n // 13
    return out or "0"


register(CapabilitySpec(
    name="base13", family="base_repr", dial_name="base", dial_value=13,
    description="write N in base 13, last digit of the representation "
                "(N in [200,9999]; probe label 0-12, values 10/11/12 are "
                "letters A/B/C in the surface answer only)",
    answer_type="number",
    probe_label_space="N mod 13, last base-13 digit as an integer (0-12)",
    basis_kind="N token (~9800 values in [200,9999])",
    composability="13 is prime -- no CRT decomposition exists, the exact "
                  "defect that killed base12 (12 = 3x4) is structurally "
                  "impossible. gcd(13,10)=1 and 10^k mod 13 cycles "
                  "1,10,9,12,3,4 with period 6, never 0, so no fixed "
                  "decimal suffix determines the label; N mod 13 "
                  "requires composing every digit's contribution "
                  "(base7's chain-nonlocal pattern at a larger residue "
                  "count)",
    dumbest_baseline="not value-mod-10 (23 -> 10 and 33 -> 7 share last "
                     "digit 3, differ mod 13); not magnitude-banding "
                     "(period-13 oscillation across the range). The one "
                     "named surface carrier: 10^3 = -1 (mod 13), so "
                     "N mod 13 = ((N mod 1000) - (N div 1000)) mod 13 "
                     "for our <=4-digit N -- the SAME 3-digit-block "
                     "alternating rule as base7 (10^3 = -1 mod 7), and "
                     "base7 survived at untrained 0.000; a 13-class "
                     "label is strictly harder to leak through the same "
                     "projections than base7's 7-class one. The screen "
                     "adjudicates",
    oracle=lambda n: n % 13,
    surface_answer=_to_base13,
    gen=lambda rng: (int(rng.integers(200, 10000)),),
    seed=20260817,
))


from .wordlists_2c import ANTONYMS_2C, ANTONYMS_2C_ADJ, ANTONYMS_2C_NOUN

_ANT6 = dict(ANTONYMS_2C)
_ADJ6_WORDS = [w for p in ANTONYMS_2C_ADJ for w in p]
_NOUN6_WORDS = [w for p in ANTONYMS_2C_NOUN for w in p]
_ADJ6_CUES = {p[0] for p in ANTONYMS_2C_ADJ}


def _gen_antonym6(rng):
    cue, ans = ANTONYMS_2C[int(rng.integers(len(ANTONYMS_2C)))]
    pool = _ADJ6_WORDS if cue in _ADJ6_CUES else _NOUN6_WORDS
    distractors = []
    while len(distractors) < 5:
        w = pool[int(rng.integers(len(pool)))]
        if w not in (cue, ans) and w not in distractors:
            distractors.append(w)
    pos = int(rng.integers(6))
    opts = distractors[:pos] + [ans] + distractors[pos:]
    return (cue, *opts)


def _oracle_antonym6(cue, *opts):
    return opts.index(_ANT6[cue]) + 1


def _surface_antonym6(cue, *opts):
    return _ANT6[cue]


register(CapabilitySpec(
    name="antonym6", family="antonym", dial_name="n_choices", dial_value=6,
    description="which of 6 words means the opposite of the cue (1 "
                "antonym + 5 distractors from the cue's own POS sublist "
                "of ANTONYMS_2C); answer = the antonym word, probe label "
                "= its printed position",
    answer_type="word",
    probe_label_space="printed position of the antonym (1-6), "
                      "shuffle-assigned",
    basis_kind="the cue word (130 values, ANTONYMS_2C cues; holdout 0.2 "
              "leaves 26 held cues and ~400 val items -- swept feasible "
              "2026-08-02, no override needed since the approved list "
              "landed at 130 pairs, well above its ~90 floor)",
    composability="the class for a held-out cue requires the antonym "
                  "relation, not a memorized cue-to-position table "
                  "(position is shuffle-random, so no such table "
                  "exists); the k=6 dial (ruled) raises the distractor "
                  "count over the reused rung's 4",
    dumbest_baseline="position under a randomized presentation is not a "
                     "function of any surface token -- the exact "
                     "survivor mechanism (2b antonym: untrained margin "
                     "0.000 in every cell). The only leak path is the "
                     "answer being surface-distinguishable from its "
                     "distractors; ANTONYMS_2C's construction rules "
                     "close the named routes at the pair level (no "
                     "containment, no shared prefix/suffix >= 3, edit "
                     "distance >= 3, length gap <= 4, token-unique "
                     "pool) and distractors draw from the cue's own POS "
                     "sublist, all tested in test_wordlists_2c.py and "
                     "hand-approved (ruling 3, 2026-08-02); the screen "
                     "adjudicates the residue",
    oracle=_oracle_antonym6,
    surface_answer=_surface_antonym6,
    gen=_gen_antonym6,
    seed=20260818,
))
