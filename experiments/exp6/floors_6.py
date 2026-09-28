# experiments/exp6/floors_6.py
"""Exp 6 floors: 2d's rule, max(majority share, 1/n_options), with the
option count DECLARED per rung and checked against every item, never
detected (2d's detector reads "options after the last colon", which the
sort rungs' own question text would trip). The bar is 2d's
`binomial_bar` verbatim.

Beside the rule's floor, a HEURISTIC floor per rung (plan delta B-22):
the best of a fixed list of guessers that read an item's surface and
solve nothing. It decides nothing in the primary. It is printed beside
every count, and a named sensitivity reads the tests over the rungs a
family cleared beyond it."""
from __future__ import annotations

from collections import Counter

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import verify_6 as v6
from experiments.exp6.battery.spec import OPTIONS_PREFIX


# rung -> [majority count of 500, declared option count], pinned from the
# committed item files; floor = max(majority count / 500, 1 / n_options)
FLOOR_PIN_6 = {
    "modarith_add1": [4, None],
    "modarith_sub1": [4, None],
    "modarith_mul1": [15, None],
    "unscramble_short": [1, None],
    "unscramble_long": [1, None],
    "ipa_word": [2, None],
    "sort3": [1, None],
    "sort5": [1, None],
    "deduction3": [14, 3],
    "deduction5": [17, 5],
    "ascii_bubble": [1, None],
    "ascii_basic": [1, None],
    "shapes": [50, 10],
    "temporal": [15, 4],
    "lcs": [50, None],
    "unit_interp1": [13, 5],
    "unit_interp2": [17, 5],
}


def majority_floor_6(cap: dict) -> dict:
    at = cap["answer_type"]
    answers = [v6.normalize_answer_side(str(it["answer"]), at)
               for it in cap["eval_items"]]
    counts = Counter(answers)
    top, n_top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    return {"majority_floor": n_top / len(answers), "majority_answer": top,
            "majority_count": int(n_top), "n_items": len(answers),
            "n_distinct_answers": len(counts)}


def options_of(item: dict, answer_type: str) -> list:
    q = item["question"]
    if OPTIONS_PREFIX not in q:
        return []
    tail = q.rsplit(OPTIONS_PREFIX, 1)[1]
    return [v6.normalize_6(o, answer_type) for o in tail.split(", ")]


def rung_floor_6(cap: dict) -> dict:
    rung = cap["name"]
    if rung not in b6.RUNGS_6:
        raise ValueError(f"{rung!r} is not an Exp 6 rung; the anchors' floors "
                         f"are 2d's (battery_2d.rung_floor)")
    at = cap["answer_type"]
    maj = majority_floor_6(cap)
    n_opt = b6.N_OPTIONS_OF.get(rung)
    for i, it in enumerate(cap["eval_items"]):
        opts = options_of(it, at)
        if n_opt is None:
            if opts:
                raise ValueError(f"{rung} item {i}: options listed on a rung "
                                 f"declared free-form")
            continue
        want = v6.normalize_answer_side(str(it["answer"]), at)
        if len(opts) != n_opt or len(set(opts)) != n_opt or opts.count(want) != 1:
            raise ValueError(f"{rung} item {i}: options {opts} against "
                             f"n_options {n_opt} and answer {want!r}")
    floor = maj["majority_floor"] if n_opt is None else max(
        maj["majority_floor"], 1.0 / n_opt)
    return {**maj, "n_options": n_opt, "floor": float(floor),
            "floor_rule": ("majority" if n_opt is None
                           else "max(majority, 1/n_options)")}


def floor_table_6(battery: dict) -> dict:
    """Floors for every rung of `battery`: Exp 6's rule on its own
    rungs, 2d's committed rule on the anchors and the control."""
    out = {}
    for rung, cap in battery.items():
        if rung in b6.RUNGS_6:
            out[rung] = rung_floor_6(cap)
        elif rung in b6.ANCHORS_6:
            from experiments.exp2d import battery_2d as bt
            out[rung] = bt.rung_floor(cap)
        else:                       # the control: never scored against a floor
            out[rung] = {**majority_floor_6(cap), "n_options": None,
                         "floor": majority_floor_6(cap)["majority_floor"],
                         "floor_rule": "majority (control, not scored)"}
    return out


# ------------------------------------------------------ heuristic floors
# rung -> {guesser: its count of 500}, pinned from the committed item
# files; {} where no guesser applies. The heuristic floor is the largest.
HEURISTIC_PIN_6 = {
    "modarith_add1": {},
    "modarith_sub1": {},
    "modarith_mul1": {},
    "unscramble_short": {},
    "unscramble_long": {},
    "ipa_word": {},
    "sort3": {},
    "sort5": {},
    "deduction3": {
        "the only option absent from the text":
            0,
        "the option at one list position":
            170,
    },
    "deduction5": {
        "the only option absent from the text":
            0,
        "the option at one list position":
            100,
    },
    "ascii_bubble": {},
    "ascii_basic": {},
    "shapes": {
        "the only option absent from the text":
            0,
        "the option at one list position":
            46,
    },
    "temporal": {
        "the only option absent from the text":
            500,
        "the option at one list position":
            118,
    },
    "lcs": {
        "the commonest answer at the count of distinct letters the two strings share":
            221,
        "the commonest answer at the count of letters the two strings share":
            237,
        "the commonest answer at the longer string's length":
            92,
        "the commonest answer at the shorter string's length":
            115,
        "the commonest answer at the two strings' total length":
            114,
    },
    "unit_interp1": {
        "of the options that combine every number of the text once, the nearest to its largest number":
            179,
        "of the options that divide or are a multiple of the text's largest number, the nearest to it":
            100,
        "of the options the text does not print, the one sharing most with its numbers":
            139,
        "the first option a number of the text divides":
            116,
        "the first option that is the product of two numbers of the text":
            92,
        "the largest option the text does not print":
            126,
        "the only option absent from the text":
            0,
        "the option at one list position":
            100,
        "the option of one rank by size":
            121,
        "the smallest option the text does not print":
            67,
        "the smallest option the text does not print that divides none of its numbers":
            85,
        "the text's last number where the blank carries its unit word, else the first option that is the product of two numbers of the text":
            92,
    },
    "unit_interp2": {
        "of the options that combine every number of the text once, the nearest to its largest number":
            148,
        "of the options that divide or are a multiple of the text's largest number, the nearest to it":
            140,
        "of the options the text does not print, the one sharing most with its numbers":
            146,
        "the first option a number of the text divides":
            105,
        "the first option that is the product of two numbers of the text":
            166,
        "the largest option the text does not print":
            114,
        "the only option absent from the text":
            0,
        "the option at one list position":
            100,
        "the option of one rank by size":
            130,
        "the smallest option the text does not print":
            145,
        "the smallest option the text does not print that divides none of its numbers":
            82,
        "the text's last number where the blank carries its unit word, else the first option that is the product of two numbers of the text":
            250,
    },
}
LIST_POSITION = "the option at one list position"
SIZE_RANK = "the option of one rank by size"
ABSENT = "the only option absent from the text"
DIVISIBLE = "the first option a number of the text divides"
SHARES = "of the options the text does not print, the one sharing most with its numbers"
NONDIVISOR = ("the smallest option the text does not print that divides none of "
              "its numbers")
PRODUCT = "the first option that is the product of two numbers of the text"
UNPRINTED_MIN = "the smallest option the text does not print"
UNPRINTED_MAX = "the largest option the text does not print"
EACH_ONCE = ("of the options that combine every number of the text once, the nearest "
             "to its largest number")
RELATED = ("of the options that divide or are a multiple of the text's largest "
           "number, the nearest to it")
SAME_UNIT = ("the text's last number where the blank carries its unit word, else the "
             "first option that is the product of two numbers of the text")
LENGTH_MIN = "the commonest answer at the shorter string's length"
LENGTH_MAX = "the commonest answer at the longer string's length"
LENGTH_SUM = "the commonest answer at the two strings' total length"
LETTERS_SHARED = "the commonest answer at the count of letters the two strings share"
LETTERS_DISTINCT = ("the commonest answer at the count of distinct letters the two "
                    "strings share")
GUESSERS_6 = (LIST_POSITION, SIZE_RANK, ABSENT, DIVISIBLE, SHARES, NONDIVISOR, PRODUCT,
              UNPRINTED_MIN, UNPRINTED_MAX, EACH_ONCE, RELATED, SAME_UNIT, LENGTH_MIN,
              LENGTH_MAX, LENGTH_SUM, LETTERS_SHARED, LETTERS_DISTINCT)
# the words a unit sentence scales its rate by (the generator's tables and
# the task files' one misspelling), as a reader of the text meets them
FACTOR_WORDS_6 = (("twice", 2), ("three times", 3), ("four times", 4), ("half", 2),
                  ("one third", 3), ("one fourth", 4), ("one forth", 4))
HALF_BLOCK = 10          # cross-fit halves: slots 0-9, 20-29, ... against the rest


def _cross_fit(keys, answers) -> int:
    """A guesser that LEARNS a table (key -> commonest answer) is fitted
    on one half of the rung and scored on the other, both ways: what it
    scores on items it has not seen. The halves alternate in blocks of
    ten slots, so every designed cycle is in both."""
    hits = 0
    for half in (0, 1):
        fit, seen = {}, Counter()
        for i, (k, a) in enumerate(zip(keys, answers)):
            if (i // HALF_BLOCK) % 2 != half:
                fit.setdefault(k, Counter())[a] += 1
                seen[a] += 1
        fallback = sorted(seen.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        for i, (k, a) in enumerate(zip(keys, answers)):
            if (i // HALF_BLOCK) % 2 == half:
                c = fit.get(k)
                guess = (sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
                         if c else fallback)
                hits += guess == a
    return int(hits)


def _numbers(text: str) -> list:
    import re
    return [int(x) for x in re.findall(r"\d+", text)]


def _smooth(x: int) -> bool:
    for q in (2, 3, 5):
        while x % q == 0:
            x //= q
    return x == 1


def _number_guessers(o: list, text: list, factor: int = 1) -> dict:
    """What each fixed rule picks among the integer options `o` of one
    item whose text prints the numbers `text` and scales by `factor` (1:
    no scaling word). A rule with nothing to pick takes the first
    option, except where it says what it takes instead.

    EACH_ONCE does the sentence's arithmetic and never reads its units:
    the largest printed number times or over every other printed number
    and the factor, each used once. It is in the list because it is what
    a model that composes numbers, and interprets nothing, would do."""
    import itertools
    import math
    from fractions import Fraction
    big = [t for t in text if t > 1]
    free = [x for x in o if x not in text]
    none = [x for x in free if not any(t % x == 0 for t in big)]
    mult = [x for x in o if any(x % t == 0 for t in big)]
    prod = [x for x in o if any(x == a * b for i, a in enumerate(text)
                                for b in text[i + 1:])]
    share = max(free or o, key=lambda x: (sum(math.gcd(x, t) for t in text),
                                          -o.index(x)))
    top = max(text) if text else 1

    def nearest(seq):
        return min(seq, key=lambda x: (abs(math.log(x / top)), o.index(x)))
    rest = list(text)
    if text:
        rest.remove(top)
    fs = [x for x in rest if x > 1] + ([factor] if factor > 1 else [])
    once = set()
    for es in itertools.product((-1, 1), repeat=len(fs)):
        v = Fraction(top)
        for f, e in zip(fs, es):
            v *= Fraction(f) ** e
        if v.denominator == 1:
            once.add(int(v))
    uses = [x for x in free if x in once]
    kin = [x for x in free if _smooth(x) and (x % top == 0 or top % x == 0)]
    return {DIVISIBLE: mult[0] if mult else o[0], SHARES: share,
            NONDIVISOR: min(none) if none else o[0],
            PRODUCT: prod[0] if prod else o[0],
            UNPRINTED_MIN: min(free) if free else o[0],
            UNPRINTED_MAX: max(free) if free else o[0],
            EACH_ONCE: nearest(uses) if uses else (min(free) if free else o[0]),
            RELATED: nearest(kin or free or o)}


def _same_unit(o: list, body: str) -> int:
    """A rule that reads two unit words and no more: the word after the
    blank against the word after the last number the text prints. The
    same word: that number, where it is an option (the quantity asked is
    the quantity stated). Otherwise the first option that is the product
    of two printed numbers. It never works out which unit a rate is per
    and never reads a scaling."""
    import re
    blank = re.search(r"\(\) (\w+)", body)
    nums = re.findall(r"(\d+) (\w+)", body)

    def stem(w):
        return w[:-1] if w.endswith("s") else w
    if blank and nums and stem(blank.group(1)) == stem(nums[-1][1]) and \
            int(nums[-1][0]) in o:
        return int(nums[-1][0])
    return _number_guessers(o, _numbers(body))[PRODUCT]


def heuristic_floor_6(cap: dict) -> dict:
    """What a guesser that reads an item's SURFACE and solves nothing
    can score on the rung: the best of a fixed list. A guesser that
    learns a table is cross-fitted; one that applies a fixed rule is
    scored as it stands. The list is fixed here, before any model read
    an item; a rule outside it may score more."""
    rung, at, items = cap["name"], cap["answer_type"], cap["eval_items"]
    n = len(items)
    found = {}
    if b6.N_OPTIONS_OF.get(rung):
        opts = [options_of(it, at) for it in items]
        want = [v6.normalize_answer_side(str(it["answer"]), at) for it in items]
        body = [it["question"].rsplit(OPTIONS_PREFIX, 1)[0] for it in items]
        found[LIST_POSITION] = _cross_fit([0] * n, [o.index(w)
                                                    for o, w in zip(opts, want)])
        found[ABSENT] = sum([x for x in o if x not in b.lower()] == [w]
                            for o, w, b in zip(opts, want, body))
        if at == "number":
            ints = [[int(x) for x in o] for o in opts]
            found[SIZE_RANK] = _cross_fit(
                [0] * n, [sorted(o).index(int(w)) for o, w in zip(ints, want)])
            hits = Counter()
            for o, w, b in zip(ints, want, body):
                k = next((k for word, k in FACTOR_WORDS_6 if word in b), 1)
                for name, x in _number_guessers(o, _numbers(b), k).items():
                    hits[name] += x == int(w)
            found.update({name: hits[name] for name in (
                DIVISIBLE, SHARES, NONDIVISOR, PRODUCT, UNPRINTED_MIN, UNPRINTED_MAX,
                EACH_ONCE, RELATED)})
            found[SAME_UNIT] = sum(_same_unit(o, b) == int(w)
                                   for o, w, b in zip(ints, want, body))
    if rung == "lcs":
        sa = [it["meta"]["a"] for it in items]
        sb = [it["meta"]["b"] for it in items]
        ans = [it["answer"] for it in items]
        found[LENGTH_MIN] = _cross_fit([min(len(x), len(y)) for x, y in zip(sa, sb)], ans)
        found[LENGTH_MAX] = _cross_fit([max(len(x), len(y)) for x, y in zip(sa, sb)], ans)
        found[LENGTH_SUM] = _cross_fit([len(x) + len(y) for x, y in zip(sa, sb)], ans)
        found[LETTERS_SHARED] = _cross_fit(
            [sum((Counter(x) & Counter(y)).values()) for x, y in zip(sa, sb)], ans)
        found[LETTERS_DISTINCT] = _cross_fit(
            [len(set(x) & set(y)) for x, y in zip(sa, sb)], ans)
    if not found:
        return {"heuristics": {}, "heuristic": None, "heuristic_count": None,
                "heuristic_floor": None, "n_items": n}
    name, count = sorted(found.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    return {"heuristics": {k: int(v) for k, v in sorted(found.items())},
            "heuristic": name, "heuristic_count": int(count),
            "heuristic_floor": count / n, "n_items": n}


def heuristic_table_6(battery: dict) -> dict:
    return {r: heuristic_floor_6(battery[r]) for r in b6.RUNGS_6 if r in battery}


def check_heuristic_pins_6(table: dict) -> dict:
    out = {}
    for rung in b6.RUNGS_6:
        got = table[rung]["heuristics"]
        if got != HEURISTIC_PIN_6[rung]:
            raise ValueError(f"{rung}: heuristic floor {got} against the pin "
                             f"{HEURISTIC_PIN_6[rung]}")
        out[rung] = "PASS"
    return out


def clears(k: int, n: int, floor: float) -> dict:
    from experiments.exp2d import stats_2d as st
    return st.binomial_bar(int(k), int(n), float(floor))


def check_floor_pins_6(table: dict) -> dict:
    out = {}
    for rung in b6.RUNGS_6:
        t = table[rung]
        maj, n_opt = FLOOR_PIN_6[rung]
        want = max(maj / b6.N_ITEMS, 1.0 / n_opt) if n_opt else maj / b6.N_ITEMS
        if [t["majority_count"], t["n_options"]] != [maj, n_opt] or \
                abs(t["floor"] - want) > 1e-12:
            raise ValueError(f"{rung}: floor {t['floor']} (majority "
                             f"{t['majority_count']}, options {t['n_options']}) "
                             f"against the pin {FLOOR_PIN_6[rung]}")
        if not 0.0 < t["floor"] < 1.0:
            raise ValueError(f"{rung}: floor {t['floor']} outside (0, 1)")
        out[rung] = "PASS"
    return out
