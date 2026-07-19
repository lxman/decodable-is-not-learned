"""Exp 2b capability specs — tranche 1: the non-wordlist candidates
(design table #1–#9, #11, #16, #17, #26, #30) plus the ctrl_copy positive
control. Tranche 2 (word/semantic families, #12–#15, #18–#25, #27–#29) lands
with its wordlists in the next commit; SPECS below grows in place.

Conventions carried from Exp 2: oracles parse question TEXT only; basis
extractors (new) do the same, so the recorded basis values are independently
recomputable from the committed items. Probe labels are strings.

Design revision 2026-07-18 (doc §2 revision note): #3/#4 target the middle
digit of the result — the mod-10 wrap is non-additive, so per-token additive
scores cannot express it; carry/borrow COUNT targets were additive-threshold
composable and are gone. #10 (time arithmetic) moved to reserve for the same
mechanism with no clean repair.
"""

from __future__ import annotations

import re

from splits import SplitParams

from .base import CapabilitySpec

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _ints(q):
    return [int(x) for x in re.findall(r"\d+", q)]


# ------------------------------------------------------------------ roman helpers

_RVAL = [(90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
         (5, "V"), (4, "IV"), (1, "I")]


def to_roman(n: int) -> str:
    out = []
    for v, s in _RVAL:
        while n >= v:
            out.append(s)
            n -= v
    return "".join(out)


def from_roman(s: str) -> int:
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    total = 0
    for a, b in zip(s, s[1:] + " "):
        v = vals[a]
        total += -v if b in vals and vals[b] > v else v
    return total


# ---------------------------------------------------------------- #1, #2: mod 7

def _gen_mod7_add(rng, split):
    a, b = int(rng.integers(10, 100)), int(rng.integers(10, 100))
    return f"What is ({a} + {b}) mod 7?", str((a + b) % 7), a % 7


def _gen_mod7_mul(rng, split):
    a, b = int(rng.integers(10, 100)), int(rng.integers(10, 100))
    return f"What is ({a} * {b}) mod 7?", str((a * b) % 7), a % 7


def _basis_first_operand(q):
    return (str(_ints(q)[0]),)


# ------------------------------------------- #3, #4: middle digit of sum/diff

def _gen_add3_mid(rng, split):
    a, b = int(rng.integers(100, 1000)), int(rng.integers(100, 1000))
    return f"What is {a} + {b}?", str(a + b), ((a + b) // 10) % 10


def _gen_sub3_mid(rng, split):
    a = int(rng.integers(100, 1000))
    b = int(rng.integers(100, a + 1))     # non-negative difference
    return f"What is {a} - {b}?", str(a - b), ((a - b) // 10) % 10


def _basis_tens_pair(q):
    a, b = _ints(q)[:2]
    return (f"{(a // 10) % 10}t{(b // 10) % 10}",)


# --------------------------------------------------------------------- #5: gcd

def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _gen_gcd(rng, split):
    # rejection-sample for gcd in 1..12 (uniform-ish over pairs, bounded gcd)
    while True:
        a, b = int(rng.integers(10, 100)), int(rng.integers(10, 100))
        g = _gcd(a, b)
        if g <= 12:
            return f"What is the greatest common divisor of {a} and {b}?", str(g), g


def _basis_operand_pair_components(q):
    a, b = _ints(q)[:2]
    return (str(a), str(b))


# ------------------------------------------------------------- #6: divisibility

def _gen_div7(rng, split):
    # balance the classes: half divisible, half not (range widened to 10..9999
    # so the unique-question space clears 2500 — feasibility, not difficulty)
    if rng.random() < 0.5:
        n = 7 * int(rng.integers(2, 1429))         # 14..9996
        ans = "yes"
    else:
        n = int(rng.integers(10, 10000))
        while n % 7 == 0:
            n = int(rng.integers(10, 10000))
        ans = "no"
    return f"Is {n} divisible by 7?", ans, ans


def _basis_first_int(q):
    return (str(_ints(q)[0]),)


# ------------------------------------------------------------ #7: binary→decimal

def _gen_bin2dec(rng, split):
    # 8-11 significant bits: unique-question space 3840 (6 bits gave only 32,
    # under the 2500-item uniqueness requirement — feasibility, not difficulty)
    n = int(rng.integers(8, 12))
    bits = "1" + "".join(str(int(rng.integers(0, 2))) for _ in range(n - 1))
    v = int(bits, 2)
    return f"What is binary {bits} in decimal?", str(v), v % 10


def _basis_bitstring(q):
    return (re.search(r"\b[01]{8,11}\b", q).group(0),)


# --------------------------------------------------------- #8: day-of-week offset

def _gen_weekday(rng, split):
    d = DAYS[int(rng.integers(7))]
    n = int(rng.integers(1, 500))
    ans = DAYS[(DAYS.index(d) + n) % 7]
    return f"What day of the week is {n} days after {d}?", ans, n % 7


def _basis_offset(q):
    return (str(_ints(q)[0]),)


# ------------------------------------------------------------- #9: roman value

def _gen_roman(rng, split):
    n = int(rng.integers(1, 100))
    m = int(rng.integers(1, 100))
    return (f"What is {to_roman(n)} + {to_roman(m)} in decimal?",
            str(n + m), n % 10)


def _basis_first_numeral(q):
    return (re.findall(r"\b[IVXLC]+\b", q)[0],)


# -------------------------------------------------- #11: sorting (middle of 3)

def _gen_sort3(rng, split):
    vals = []
    while len(vals) < 3:
        v = int(rng.integers(10, 100))
        if v not in vals:
            vals.append(v)
    mid = sorted(vals)[1]
    return (f"Sort {vals[0]}, {vals[1]}, {vals[2]} in increasing order. "
            f"What is the middle number?", str(mid), mid % 10)


def _basis_all_ints(q):
    return tuple(sorted(str(v) for v in _ints(q)[:3]))


# ------------------------------------------- #16: reversed random string (last letter)

_LET = "abcdefghijklmnopqrstuvwxyz"


def _gen_reverse(rng, split):
    n = int(rng.integers(4, 7))
    s = "".join(_LET[int(rng.integers(26))] for _ in range(n))
    return f"Spell the string '{s}' backwards.", s[::-1], s[-1]


def _basis_quoted_string(q):
    return (re.search(r"'([a-z]+)'", q).group(1),)


_TOKENIZER = None


def _final_chunk(s: str) -> str:
    """Final BPE chunk of the quoted string as tokenized inside a prompt context
    (leading quote included, matching how the model actually sees it). Design
    table #16: the basis is the CHUNK — random strings share final chunks, so a
    whole-string holdout starves nothing. Deterministic given the pinned
    tokenizer SHA (models.py); requires the canonical venv + HF cache."""
    global _TOKENIZER
    if _TOKENIZER is None:
        from models import load_tokenizer
        _TOKENIZER = load_tokenizer("410m")   # one tokenizer across the Pythia suite
    ids = _TOKENIZER(f"'{s}'", add_special_tokens=False)["input_ids"]
    toks = [_TOKENIZER.decode([t]) for t in ids]
    # final chunk of the string itself: last token before the closing quote
    return toks[-2] if toks[-1] == "'" else toks[-1].rstrip("'")


def _basis_final_chunk(q):
    return (_final_chunk(re.search(r"'([a-z]+)'", q).group(1)),)


# --------------------------------------------------- #17: balanced parentheses

def _gen_parens(rng, split):
    n = int(rng.integers(4, 11))
    if rng.random() < 0.5:  # generate balanced (depth <= 3) by construction
        s, depth, remaining = [], 0, n
        while remaining:
            can_open = depth < 3 and remaining > depth
            must_open = depth == 0
            if must_open or (can_open and rng.random() < 0.5):
                s.append("("); depth += 1
            else:
                s.append(")"); depth -= 1
            remaining -= 1
        if depth:  # odd-length tail: close what's open (only reachable if n odd)
            s.extend(")" * depth)
        s = "".join(s)
        ans = "yes"
    else:
        s = "".join("(" if rng.random() < 0.5 else ")" for _ in range(n))
        d, ok = 0, True
        for c in s:
            d += 1 if c == "(" else -1
            if d < 0 or d > 3:
                ok = False
        ans = "yes" if (ok and d == 0) else "no"
    return f"Is the parenthesis string {s} balanced?", ans, ans


def _basis_paren_string(q):
    return (re.search(r"[()]+", q).group(0),)


def _oracle_parens(q):
    s = re.search(r"[()]+", q).group(0)
    d = 0
    for c in s:
        d += 1 if c == "(" else -1
        if d < 0 or d > 3:
            return "no"
    return "yes" if d == 0 else "no"


# ------------------------------------------------------------ #26: month offset

def _gen_month(rng, split):
    m = MONTHS[int(rng.integers(12))]
    k = int(rng.integers(1, 4))
    ans = MONTHS[(MONTHS.index(m) + k) % 12]
    return f"What month is {k} months after {m}?", ans, ans


def _basis_month_offset(q):
    k = _ints(q)[0]
    month = next(m for m in MONTHS if m in q)
    return (f"{month}+{k}",)


# ------------------------------------------------- #30: letter alphabet-half

def _gen_letter_half(rng, split):
    c = _LET[int(rng.integers(26))]
    ans = "yes" if c <= "m" else "no"
    return f"Is the letter '{c}' in the first half of the alphabet?", ans, ans


def _basis_quoted_letter(q):
    return (re.search(r"'([a-z])'", q).group(1),)


# ------------------------------------------------------------ positive control

def _gen_ctrl_copy(rng, split):
    n = int(rng.integers(4, 7))
    s = "".join(_LET[int(rng.integers(26))] for _ in range(n))
    return f"Repeat the string '{s}' exactly.", s, s[0]


# --------------------------------------------------------------------- oracles
# (text-only recomputation; never the generator's variables)

def _oracle_mod7_add(q):
    a, b = _ints(q)[:2]
    return str((a + b) % 7)


def _oracle_mod7_mul(q):
    a, b = _ints(q)[:2]
    return str((a * b) % 7)


def _oracle_add3(q):
    a, b = _ints(q)[:2]
    return str(a + b)


def _oracle_sub3(q):
    a, b = _ints(q)[:2]
    return str(a - b)


def _oracle_gcd(q):
    a, b = _ints(q)[:2]
    return str(_gcd(a, b))


def _oracle_div7(q):
    return "yes" if _ints(q)[0] % 7 == 0 else "no"


def _oracle_bin2dec(q):
    return str(int(re.search(r"\b[01]{8,11}\b", q).group(0), 2))


def _oracle_weekday(q):
    n = _ints(q)[0]
    d = next(x for x in DAYS if x in q)
    return DAYS[(DAYS.index(d) + n) % 7]


def _oracle_roman(q):
    r1, r2 = re.findall(r"\b[IVXLC]+\b", q)[:2]
    return str(from_roman(r1) + from_roman(r2))


def _oracle_sort3(q):
    return str(sorted(_ints(q)[:3])[1])


def _oracle_reverse(q):
    return re.search(r"'([a-z]+)'", q).group(1)[::-1]


def _oracle_month(q):
    k = _ints(q)[0]
    m = next(x for x in MONTHS if x in q)
    return MONTHS[(MONTHS.index(m) + k) % 12]


def _oracle_letter_half(q):
    return "yes" if re.search(r"'([a-z])'", q).group(1) <= "m" else "no"


def _oracle_ctrl_copy(q):
    return re.search(r"'([a-z]+)'", q).group(1)


# ----------------------------------------------------------------------- SPECS

SPECS = [
    CapabilitySpec(
        name="mod7_add", description="(a+b) mod 7, 2-digit operands",
        answer_type="number", probe_label_space="a mod 7 (0-6)",
        basis_kind="first operand token (90 values)",
        composability="mod-7 of a 2-digit number wraps: not additive in digits",
        shots=[("What is (23 + 45) mod 7?", "5"), ("What is (81 + 17) mod 7?", "0")],
        gen=_gen_mod7_add, oracle=_oracle_mod7_add, basis_fn=_basis_first_operand,
        split_params=SplitParams(n_holdout=18)),
    CapabilitySpec(
        name="mod7_mul", description="(a*b) mod 7, 2-digit operands",
        answer_type="number", probe_label_space="a mod 7 (0-6)",
        basis_kind="first operand token (90 values)",
        composability="as mod7_add",
        shots=[("What is (23 * 45) mod 7?", "6"), ("What is (81 * 17) mod 7?", "5")],
        gen=_gen_mod7_mul, oracle=_oracle_mod7_mul, basis_fn=_basis_first_operand,
        split_params=SplitParams(n_holdout=18)),
    CapabilitySpec(
        name="add3_mid", description="3-digit addition",
        answer_type="number", probe_label_space="middle digit of the sum (0-9)",
        basis_kind="tens-digit pair (100 values)",
        composability="(a1+b1+carry) mod 10 wraps: not expressible by additive "
                      "per-token scores (design revision 2026-07-18)",
        shots=[("What is 234 + 567?", "801"), ("What is 912 + 145?", "1057")],
        gen=_gen_add3_mid, oracle=_oracle_add3, basis_fn=_basis_tens_pair,
        split_params=SplitParams(n_holdout=20)),
    CapabilitySpec(
        name="sub3_mid", description="3-digit subtraction (non-negative)",
        answer_type="number", probe_label_space="middle digit of the difference (0-9)",
        basis_kind="tens-digit pair (100 values)",
        composability="mod-10 wrap under borrow: as add3_mid",
        shots=[("What is 634 - 267?", "367"), ("What is 912 - 145?", "767")],
        gen=_gen_sub3_mid, oracle=_oracle_sub3, basis_fn=_basis_tens_pair,
        split_params=SplitParams(n_holdout=20)),
    CapabilitySpec(
        name="gcd", description="GCD of two 2-digit numbers (bounded 1-12)",
        answer_type="number", probe_label_space="gcd class (1-12)",
        basis_kind="both operand tokens (2 components, ~90 values each)",
        composability="gcd is jointly nonlocal in the operand pair",
        shots=[("What is the greatest common divisor of 24 and 36?", "12"),
               ("What is the greatest common divisor of 35 and 12?", "1")],
        gen=_gen_gcd, oracle=_oracle_gcd, basis_fn=_basis_operand_pair_components,
        split_params=SplitParams(holdout_frac=0.45, min_val_items=300,
                                 shared_components=True),
        n_probe=4000),
    CapabilitySpec(
        name="div7", description="divisibility by 7 (yes/no)",
        answer_type="word", probe_label_space="divisibility bit (yes/no)",
        basis_kind="dividend token (~870 values)",
        composability="n mod 7 == 0 wraps over the digit expansion: not additive",
        shots=[("Is 49 divisible by 7?", "yes"), ("Is 50 divisible by 7?", "no")],
        gen=_gen_div7, oracle=_oracle_div7, basis_fn=_basis_first_int),
    CapabilitySpec(
        name="bin2dec", description="binary to decimal, 8-11 bits",
        answer_type="number", probe_label_space="value mod 10 (0-9)",
        basis_kind="bit-string (3840 significant 8-11-bit strings)",
        composability="(sum 2^i b_i) mod 10 wraps hundreds of times over the "
                      "range: additive per-bit scores cannot express it",
        shots=[("What is binary 10110101 in decimal?", "181"),
               ("What is binary 11001010 in decimal?", "202")],
        gen=_gen_bin2dec, oracle=_oracle_bin2dec, basis_fn=_basis_bitstring),
    CapabilitySpec(
        name="weekday", description="day-of-week offset, N <= 499",
        answer_type="word", probe_label_space="N mod 7 (0-6)",
        basis_kind="offset token N (~499 values)",
        composability="N mod 7 wraps over the digit expansion: not additive",
        shots=[("What day of the week is 3 days after Monday?", "Thursday"),
               ("What day of the week is 10 days after Friday?", "Monday")],
        gen=_gen_weekday, oracle=_oracle_weekday, basis_fn=_basis_offset),
    CapabilitySpec(
        name="roman", description="roman numeral addition (values 1-99)",
        answer_type="number", probe_label_space="first numeral's value mod 10 (0-9)",
        basis_kind="first numeral string (99 values)",
        composability="subtractive notation is sequence-nonlocal (IV vs VI)",
        shots=[("What is XIV + VII in decimal?", "21"),
               ("What is XL + IX in decimal?", "49")],
        gen=_gen_roman, oracle=_oracle_roman, basis_fn=_basis_first_numeral,
        split_params=SplitParams(n_holdout=20)),
    CapabilitySpec(
        name="sort3_mid", description="middle of three 2-digit numbers",
        answer_type="number", probe_label_space="middle element's value mod 10 (0-9)",
        basis_kind="the unordered number triple's members (3 components)",
        composability="M0-REVIEW flag per design: pairwise comparison of 2-digit "
                      "numbers is near-lexicographic (first-digit shortcut); kept "
                      "pending the M0 review the design table mandates",
        shots=[("Sort 34, 12, 78 in increasing order. What is the middle number?", "34"),
               ("Sort 91, 55, 23 in increasing order. What is the middle number?", "55")],
        gen=_gen_sort3, oracle=_oracle_sort3, basis_fn=_basis_all_ints,
        split_params=SplitParams(holdout_frac=0.37, min_val_items=300,
                                 shared_components=True),
        n_probe=8000),
    CapabilitySpec(
        name="reverse_string", description="reverse a random 4-6 letter string",
        answer_type="word", probe_label_space="last letter of the input (26)",
        basis_kind="final BPE chunk of the input string (design table #16 — "
                   "the tokenizer-keyed basis; random strings SHARE final "
                   "chunks, so the chunk, not the string, is the lookup unit)",
        composability="last-letter-of-unseen-chunk requires linking a token to "
                      "its spelling — model knowledge, not lookup. NOTE the "
                      "class-coverage constraint does real work here: 1-letter "
                      "final chunks equal the target class and the split "
                      "machinery must keep every class on both sides",
        shots=[("Spell the string 'abcde' backwards.", "edcba"),
               ("Spell the string 'stone' backwards.", "enots")],
        gen=_gen_reverse, oracle=_oracle_reverse, basis_fn=_basis_final_chunk,
        split_params=SplitParams(holdout_frac=0.2, min_holdout_values=15,
                                 min_val_items=300)),
    CapabilitySpec(
        name="parens", description="balanced-parenthesis check (depth <= 3)",
        answer_type="word", probe_label_space="valid/invalid bit (yes/no)",
        basis_kind="the parenthesis string (unique per item)",
        composability="validity is a chain property (prefix depths); a bag of "
                      "positions is insufficient — additive scores over position "
                      "tokens cannot track the running minimum",
        shots=[("Is the parenthesis string (()) balanced?", "yes"),
               ("Is the parenthesis string ())( balanced?", "no")],
        gen=_gen_parens, oracle=_oracle_parens, basis_fn=_basis_paren_string,
        split_params=SplitParams(holdout_frac=0.2, min_val_items=300)),
    CapabilitySpec(
        name="month_offset", description="month + k months (k in 1-3)",
        answer_type="word", probe_label_space="the result month (12)",
        basis_kind="(month, offset) combo (36 values)",
        composability="12-class cyclic lookup basis starved directly; result "
                      "month for an unseen combo requires the cyclic ordering",
        shots=[("What month is 2 months after March?", "May"),
               ("What month is 1 month after December?", "January")],
        gen=_gen_month, oracle=_oracle_month, basis_fn=_basis_month_offset,
        split_params=SplitParams(n_holdout=14, min_holdout_values=14,
                                 min_val_items=300)),
    CapabilitySpec(
        name="letter_half", description="is the letter in the first alphabet half",
        answer_type="word", probe_label_space="the bit (yes/no)",
        basis_kind="the letter (26 values)",
        composability="single-letter basis starved directly; the boundary "
                      "position of an unseen letter requires alphabet ordering",
        shots=[("Is the letter 'c' in the first half of the alphabet?", "yes"),
               ("Is the letter 'r' in the first half of the alphabet?", "no")],
        gen=_gen_letter_half, oracle=_oracle_letter_half, basis_fn=_basis_quoted_letter,
        split_params=SplitParams(n_holdout=5, min_holdout_values=5, min_val_items=300)),
    CapabilitySpec(
        name="ctrl_copy", description="POSITIVE CONTROL: exact copy of a string",
        answer_type="word", probe_label_space="first letter (26)",
        basis_kind="(control - no starved split; gate, not scored)",
        composability="(control)",
        shots=[("Repeat the string 'abcd' exactly.", "abcd"),
               ("Repeat the string 'zyxw' exactly.", "zyxw")],
        gen=_gen_ctrl_copy, oracle=_oracle_ctrl_copy, basis_fn=_basis_quoted_string,
        scored=False, allow_dupes=True),
]
