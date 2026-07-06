"""The 16 scored capability candidates + 2 positive controls (design doc §2).

Every oracle parses the question TEXT — never the generator's internals — so the
oracle-agreement check in base.generate_items is a genuine known-answer gate.
Word-pool tasks split their pools deterministically (eval = every 5th word of the
sorted pool) so probe and eval items share no words (design §3 split hygiene).
"""

from __future__ import annotations

import re
from collections import Counter

from .base import CapabilitySpec
from .wordlists import CATEGORIES, DAYS, NAMES, WORDS

# ---------------------------------------------------------------------------- pools

# enforce the 4-6 letter operationalization in code, not by trusting the list
_WORDS = sorted({w for w in WORDS if 4 <= len(w) <= 6})
EVAL_WORDS = _WORDS[::5]
PROBE_WORDS = [w for i, w in enumerate(_WORDS) if i % 5]

# words whose letter-multiset is unique in the whole list (unscramble answers
# are well-defined against the committed pool)
_MS = Counter("".join(sorted(w)) for w in _WORDS)
_WORDSET = set(_WORDS)
UNIQ = [w for w in _WORDS if _MS["".join(sorted(w))] == 1]
UNIQ_EVAL = UNIQ[::5]
UNIQ_PROBE = [w for i, w in enumerate(UNIQ) if i % 5]

_CAT_MEMBERS = {w for ws in CATEGORIES.values() for w in ws}
_DISTRACTORS = [w for w in _WORDS if w not in _CAT_MEMBERS]


def _pool(split, ev, pr):
    return ev if split == "eval" else pr


def _by_letter(pool, min_n):
    d = {}
    for w in pool:
        d.setdefault(w[0], []).append(w)
    return {k: v for k, v in d.items() if len(v) >= min_n}


def _stratified_pools(ev, pr, min_ev=3, min_pr=12):
    """Letter-stratified word sampling for tasks whose probe label is a first
    letter: rare first letters would leave the probe's rarest class data-starved
    (<30 examples), so we sample the letter uniformly over letters with enough
    support in BOTH splits, then the word. Preregistered in the design doc."""
    e, p = _by_letter(ev, min_ev), _by_letter(pr, min_pr)
    letters = sorted(set(e) & set(p))
    return letters, e, p


def _draw_stratified(rng, split, letters, e, p):
    letter = letters[int(rng.integers(len(letters)))]
    pool = (e if split == "eval" else p)[letter]
    return pool[int(rng.integers(len(pool)))]


_UNSCRAMBLE = None
_CIPHERP = None


def _lazy_pools():
    global _UNSCRAMBLE, _CIPHERP
    if _UNSCRAMBLE is None:
        _UNSCRAMBLE = _stratified_pools(UNIQ_EVAL, UNIQ_PROBE)
        _CIPHERP = _stratified_pools(EVAL_WORDS, PROBE_WORDS)
    return _UNSCRAMBLE, _CIPHERP


def _ints(q):
    return [int(x) for x in re.findall(r"\d+", q)]


# ------------------------------------------------------------------- roman helpers

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


# ------------------------------------------------------------------ 16 candidates

def _gen_add2(rng, split):
    a, b = int(rng.integers(10, 100)), int(rng.integers(10, 100))
    return f"What is {a} + {b}?", str(a + b), int(a % 10 + b % 10 >= 10)


def _gen_add3(rng, split):
    a, b = int(rng.integers(100, 1000)), int(rng.integers(100, 1000))
    carries, c = 0, 0
    x, y = a, b
    for _ in range(3):
        c = int(x % 10 + y % 10 + c >= 10)
        carries += c
        x, y = x // 10, y // 10
    return f"What is {a} + {b}?", str(a + b), carries


def _gen_mult2(rng, split):
    a, b = int(rng.integers(10, 100)), int(rng.integers(10, 100))
    return f"What is {a} * {b}?", str(a * b), (a * b) % 10


def _gen_mod7(rng, split):
    a, b = int(rng.integers(10, 100)), int(rng.integers(10, 100))
    return f"What is ({a} + {b}) mod 7?", str((a + b) % 7), a % 7


def _gen_parity(rng, split):
    n = int(rng.integers(8, 13))
    bits = "".join(str(int(b)) for b in rng.integers(0, 2, size=n))
    parity = bits.count("1") % 2
    half = bits[: n // 2].count("1") % 2
    return (f"Is the number of ones in the binary string {bits} even or odd?",
            "odd" if parity else "even", half)


def _gen_unscramble(rng, split):
    (letters, e, p), _ = _lazy_pools()
    w = _draw_stratified(rng, split, letters, e, p)
    for _ in range(20):
        perm = rng.permutation(len(w))
        s = "".join(w[i] for i in perm)
        if s != w and s not in _WORDSET:
            break
    else:
        s = w[::-1] if w[::-1] != w and w[::-1] not in _WORDSET else None
        if s is None:
            raise RuntimeError(f"cannot scramble {w}")
    return (f"Unscramble the letters '{s}' to form a common English word.", w, w[0])


_OBJECTS = ["ball", "coin", "book", "key", "map", "pen"]


def _gen_entity(rng, split):
    n1, n2, n3 = (NAMES[i] for i in rng.choice(len(NAMES), size=3, replace=False))
    obj = _OBJECTS[int(rng.integers(len(_OBJECTS)))]
    q = (f"{n1.capitalize()} has the {obj}. {n1.capitalize()} gives the {obj} to "
         f"{n2.capitalize()}. {n2.capitalize()} gives the {obj} to {n3.capitalize()}. "
         f"Who has the {obj} now?")
    return q, n3, n2


_RELS = ["taller", "older", "faster", "heavier", "stronger"]


def _gen_deduce(rng, split):
    a, b, c = (NAMES[i] for i in rng.choice(len(NAMES), size=3, replace=False))
    rel = _RELS[int(rng.integers(len(_RELS)))]
    x, y = (a, c) if rng.integers(2) else (c, a)
    q = (f"{a.capitalize()} is {rel} than {b.capitalize()}. {b.capitalize()} is {rel} "
         f"than {c.capitalize()}. Who is {rel}: {x.capitalize()} or {y.capitalize()}?")
    return q, a, b


def _gen_acronym(rng, split):
    pool = _pool(split, EVAL_WORDS, PROBE_WORDS)
    _, (letters, e, p) = _lazy_pools()
    w2 = _draw_stratified(rng, split, letters, e, p)  # probe label = 2nd word's letter
    others = [pool[i] for i in rng.choice(len(pool), size=2, replace=False)]
    if w2 in others:
        return _gen_acronym(rng, split)
    ws = [others[0], w2, others[1]]
    q = (f"Take the first letter of each word in '{' '.join(ws)}' and join them. "
         f"What is the result?")
    return q, "".join(w[0] for w in ws), ws[1][0]


def _gen_reverse(rng, split):
    n = int(rng.integers(4, 7))
    s = "".join("abcdefghijklmnopqrstuvwxyz"[i] for i in rng.integers(0, 26, size=n))
    return f"Spell the string '{s}' backwards.", s[::-1], s[0]


def _gen_roman(rng, split):
    a, b = int(rng.integers(1, 100)), int(rng.integers(1, 100))
    q = (f"What is the sum of the Roman numerals {to_roman(a)} and {to_roman(b)}, "
         f"written as a decimal number?")
    return q, str(a + b), a % 10


def _gen_alpha(rng, split):
    pool = _pool(split, EVAL_WORDS, PROBE_WORDS)
    ws = [pool[i] for i in rng.choice(len(pool), size=4, replace=False)]
    q = f"Which of these words comes first in alphabetical order: {', '.join(ws)}?"
    ans = min(ws)
    return q, ans, ws.index(ans) + 1  # probe label: list position, balanced 1-4


_UNIT_MAP = {("meters", "kilometers"): 3, ("centimeters", "meters"): 2,
             ("millimeters", "centimeters"): 1, ("grams", "kilograms"): 3,
             ("milligrams", "grams"): 3, ("milliliters", "liters"): 3}
_UNIT_KEYS = list(_UNIT_MAP)


def _gen_units(rng, split):
    u1, u2 = _UNIT_KEYS[int(rng.integers(len(_UNIT_KEYS)))]
    n = int(rng.integers(2, 1000))
    e = _UNIT_MAP[(u1, u2)]
    return f"How many {u1} are in {n} {u2}?", str(n * 10 ** e), e


def _gen_weekday(rng, split):
    d = int(rng.integers(7))
    n = int(rng.integers(1, 500))
    q = f"Today is {DAYS[d].capitalize()}. What day of the week will it be {n} days from now?"
    return q, DAYS[(d + n) % 7], n % 7


def _gen_count(rng, split):
    cat = list(CATEGORIES)[int(rng.integers(len(CATEGORIES)))]
    k = int(rng.integers(1, 6))
    members = [CATEGORIES[cat][i] for i in rng.choice(len(CATEGORIES[cat]), size=k, replace=False)]
    dis = [_DISTRACTORS[i] for i in rng.choice(len(_DISTRACTORS), size=6 - k, replace=False)]
    ws = members + dis
    rng.shuffle(ws)
    q = f"How many {cat} are in this list: {', '.join(ws)}?"
    return q, str(k), sum(w in CATEGORIES[cat] for w in ws[:3])


def _shift(s, k):
    return "".join(chr((ord(c) - 97 + k) % 26 + 97) for c in s)


def _gen_cipher(rng, split):
    _, (letters, e, p) = _lazy_pools()
    w = _draw_stratified(rng, split, letters, e, p)
    k = int(rng.integers(1, 6))
    q = (f"Each letter of '{_shift(w, k)}' was shifted forward by {k} alphabet "
         f"positions. What was the original word?")
    return q, w, w[0]


# --------------------------------------------------------------- positive controls

def _gen_copy(rng, split):
    _, (letters, e, p) = _lazy_pools()
    w = _draw_stratified(rng, split, letters, e, p)
    return f"Repeat this word exactly: '{w}'.", w, w[0]


def _gen_next_letter(rng, split):
    c = "abcdefghijklmnopqrstuvwxy"[int(rng.integers(25))]
    return f"What is the next letter of the alphabet after '{c}'?", chr(ord(c) + 1), c


# ------------------------------------------------------------------------- oracles

def _ora_add(q):
    a, b = _ints(q)[:2]
    return str(a + b)


def _ora_mult(q):
    a, b = _ints(q)[:2]
    return str(a * b)


def _ora_mod7(q):
    a, b, m = _ints(q)[:3]
    return str((a + b) % m)


def _ora_parity(q):
    bits = re.search(r"[01]{8,}", q).group(0)
    return "odd" if bits.count("1") % 2 else "even"


def _ora_unscramble(q):
    s = re.search(r"'([a-z]+)'", q).group(1)
    key = "".join(sorted(s))
    matches = [w for w in _WORDS if "".join(sorted(w)) == key]
    assert len(matches) == 1, f"ambiguous scramble {s!r}: {matches}"
    return matches[0]


def _ora_entity(q):
    transfers = re.findall(r"(\w+) gives the \w+ to (\w+)\.", q)
    holder = re.search(r"^(\w+) has the", q).group(1)
    for src, dst in transfers:
        assert src == holder, f"broken chain in {q!r}"
        holder = dst
    return holder.lower()


def _ora_deduce(q):
    (a, _r1, b1), (b2, _r2, c) = re.findall(r"(\w+) is (\w+) than (\w+)\.", q)
    assert b1 == b2
    return a.lower()


def _ora_acronym(q):
    ws = re.search(r"'([a-z ]+)'", q).group(1).split()
    return "".join(w[0] for w in ws)


def _ora_reverse(q):
    return re.search(r"'([a-z]+)'", q).group(1)[::-1]


def _ora_roman(q):
    r1, r2 = re.search(r"Roman numerals ([IVXLC]+) and ([IVXLC]+)", q).groups()
    return str(from_roman(r1) + from_roman(r2))


def _ora_alpha(q):
    ws = q.split(":")[1].strip(" ?").split(", ")
    return min(ws)


def _ora_units(q):
    m = re.search(r"How many (\w+) are in (\d+) (\w+)\?", q)
    u1, n, u2 = m.group(1), int(m.group(2)), m.group(3)
    return str(n * 10 ** _UNIT_MAP[(u1, u2)])


def _ora_weekday(q):
    d = re.search(r"Today is (\w+)\.", q).group(1).lower()
    n = int(re.search(r"be (\d+) days", q).group(1))
    return DAYS[(DAYS.index(d) + n) % 7]


def _ora_count(q):
    cat = re.search(r"How many (\w+) are", q).group(1)
    ws = q.split(":")[1].strip(" ?").split(", ")
    return str(sum(w in CATEGORIES[cat] for w in ws))


def _ora_cipher(q):
    s = re.search(r"'([a-z]+)'", q).group(1)
    k = int(re.search(r"by (\d+) alphabet", q).group(1))
    return _shift(s, -k)


def _ora_copy(q):
    return re.search(r"'([a-z]+)'", q).group(1)


def _ora_next_letter(q):
    return chr(ord(re.search(r"after '([a-z])'", q).group(1)) + 1)


# ---------------------------------------------------------------------- the specs

SPECS = [
    CapabilitySpec("add2", "2-digit addition (carry mixed)", "number",
                   "carry bit of the ones column (0/1)",
                   [("What is 21 + 34?", "55"), ("What is 58 + 27?", "85")],
                   _gen_add2, _ora_add),
    CapabilitySpec("add3", "3-digit addition", "number",
                   "number of carry operations (0-3)",
                   [("What is 214 + 351?", "565"), ("What is 687 + 456?", "1143")],
                   _gen_add3, _ora_add),
    CapabilitySpec("mult2", "2-digit multiplication", "number",
                   "ones digit of the product (0-9)",
                   [("What is 12 * 13?", "156"), ("What is 45 * 22?", "990")],
                   _gen_mult2, _ora_mult),
    CapabilitySpec("mod7", "modular addition mod 7", "number",
                   "first operand mod 7 (0-6)",
                   [("What is (12 + 15) mod 7?", "6"), ("What is (30 + 41) mod 7?", "1")],
                   _gen_mod7, _ora_mod7),
    CapabilitySpec("parity", "parity of 8-12 bit strings", "choice",
                   "parity of the first half of the string (0/1)",
                   [("Is the number of ones in the binary string 10110100 even or odd?", "even"),
                    ("Is the number of ones in the binary string 111000101 even or odd?", "odd")],
                   _gen_parity, _ora_parity),
    CapabilitySpec("unscramble", "word unscrambling (4-6 letters)", "word",
                   "first letter of the solution word (a-z)",
                   [("Unscramble the letters 'lpaep' to form a common English word.", "apple"),
                    ("Unscramble the letters 'rgeen' to form a common English word.", "green")],
                   _gen_unscramble, _ora_unscramble),
    CapabilitySpec("entity_track", "entity tracking (3 entities, 2 transfers)", "word",
                   "holder after the FIRST transfer (name)",
                   [("Emma has the coin. Emma gives the coin to Jack. Jack gives the coin "
                     "to Noah. Who has the coin now?", "noah"),
                    ("Liam has the map. Liam gives the map to Tina. Tina gives the map "
                     "to Karen. Who has the map now?", "karen")],
                   _gen_entity, _ora_entity),
    CapabilitySpec("deduce2", "2-hop transitive deduction", "word",
                   "the middle term of the chain (name)",
                   [("Sam is older than Mary. Mary is older than Peter. Who is older: "
                     "Sam or Peter?", "sam"),
                    ("Grace is faster than Henry. Henry is faster than Bob. Who is faster: "
                     "Bob or Grace?", "grace")],
                   _gen_deduce, _ora_deduce),
    CapabilitySpec("acronym", "first-letter acronym construction", "letters",
                   "first letter of the SECOND word (a-z)",
                   [("Take the first letter of each word in 'garden output wolf' and join "
                     "them. What is the result?", "gow"),
                    ("Take the first letter of each word in 'mint able print' and join "
                     "them. What is the result?", "map")],
                   _gen_acronym, _ora_acronym),
    CapabilitySpec("reverse_string", "spelling a 4-6 letter string backwards", "word",
                   "first letter of the input string (a-z)",
                   [("Spell the string 'kmbt' backwards.", "tbmk"),
                    ("Spell the string 'quraf' backwards.", "faruq")],
                   _gen_reverse, _ora_reverse),
    CapabilitySpec("roman", "Roman-numeral addition (values 1-99)", "number",
                   "ones digit of the first numeral's value (0-9)",
                   [("What is the sum of the Roman numerals IV and XII, written as a "
                     "decimal number?", "16"),
                    ("What is the sum of the Roman numerals XXVII and LI, written as a "
                     "decimal number?", "78")],
                   _gen_roman, _ora_roman),
    CapabilitySpec("alpha_order", "alphabetically-first of 4 words", "word",
                   "list position of the answer (1-4)",
                   [("Which of these words comes first in alphabetical order: mango, "
                     "chair, tiger, bread?", "bread"),
                    ("Which of these words comes first in alphabetical order: wolf, "
                     "stone, pearl, zebra?", "pearl")],
                   _gen_alpha, _ora_alpha),
    CapabilitySpec("units", "1-step metric conversion", "number",
                   "power of ten of the conversion factor (1-3)",
                   [("How many meters are in 4 kilometers?", "4000"),
                    ("How many centimeters are in 12 meters?", "1200")],
                   _gen_units, _ora_units),
    CapabilitySpec("weekday", "day-of-week offset arithmetic", "word",
                   "offset mod 7 (0-6)",
                   [("Today is Monday. What day of the week will it be 4 days from now?",
                     "friday"),
                    ("Today is Saturday. What day of the week will it be 10 days from now?",
                     "tuesday")],
                   _gen_weekday, _ora_weekday),
    CapabilitySpec("count_category", "counting category members in a 6-word list", "number",
                   "category count among the first 3 words (0-3)",
                   [("How many animals are in this list: dog, chair, lion, ruby, frog, "
                     "desk?", "3"),
                    ("How many colors are in this list: red, wolf, spoon, gold, lamp, "
                     "cave?", "2")],
                   _gen_count, _ora_count),
    CapabilitySpec("cipher", "Caesar-shift decoding (shift 1-5, stated)", "word",
                   "first letter of the decoded word (a-z)",
                   [("Each letter of 'bqqmf' was shifted forward by 1 alphabet positions. "
                     "What was the original word?", "apple"),
                    ("Each letter of 'jqtug' was shifted forward by 2 alphabet positions. "
                     "What was the original word?", "horse")],
                   _gen_cipher, _ora_cipher),
    # ---- positive controls (gates; excluded from the scored correlation) ----
    CapabilitySpec("ctrl_copy", "POSITIVE CONTROL: exact word copy", "word",
                   "first letter of the word (a-z)",
                   [("Repeat this word exactly: 'stone'.", "stone"),
                    ("Repeat this word exactly: 'river'.", "river")],
                   _gen_copy, _ora_copy, scored=False, allow_dupes=True),
    CapabilitySpec("ctrl_next_letter", "POSITIVE CONTROL: next alphabet letter", "word",
                   "the input letter (a-y)",
                   [("What is the next letter of the alphabet after 'c'?", "d"),
                    ("What is the next letter of the alphabet after 'm'?", "n")],
                   _gen_next_letter, _ora_next_letter, scored=False, allow_dupes=True),
]

SPEC_BY_NAME = {s.name: s for s in SPECS}
