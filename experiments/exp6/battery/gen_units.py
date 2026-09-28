# experiments/exp6/battery/gen_units.py
"""Unit interpretation, levels 1 and 2 (BIG-bench unit_interpretation
lv1 / lv2; Wei class E.3). The subjects, units and sentence frames are
the README's and the task files'. Every number in an item and its answer
is a positive integer.

The numbers and the wrong options follow the README's generation rule
(its steps 3 and 5). Numbers are drawn from pools of integers without a
prime factor above 5 ("excluding numbers with large prime factors"); the
quantity a sentence shows is a multiple of the least common multiple of
its rate's two numbers and of its scaling factor, so that every
combination of the item's numbers is an integer ("applying the least
common multiples"). A wrong option is a COMBINATION of the item's own
numbers — the shown quantity times or over the rate's numbers and the
factor, the answers of the wrong readings — three times in four, and a
POOL number once in four ("most incorrect answers are the wrong
combination of the generated numbers ... and others are random numbers
generated from the pool of numbers"), on whichever side of the answer
it falls.

Each sentence has two SURFACES. "battery" is what a model reads: the
task files' wording with their grammar slips corrected ("If they
takes", a capital "They" after a comma, "one forth"). "bigbench" is the
task files' wording byte for byte, slips included, and is what the
collision key is built from — a corrected key would never match the
string it is meant to exclude."""
from __future__ import annotations

import itertools
import math
from fractions import Fraction

from .spec import RungSpec, register, with_options

N_OPTIONS = 5
FACTOR_WORD = {2: "twice", 3: "three times", 4: "four times"}
SLOW_WORD = {2: "half", 3: "one third", 4: "one fourth"}
BB_SLOW_WORD = {2: "half", 3: "one third", 4: "one forth"}     # the task file's spelling
SURFACES = ("battery", "bigbench")
CAP = 5000                          # no number of an item exceeds it
P_COMBINATION = 0.75                # a wrong option is a combination, else a pool number


def smooth(lo: int, hi: int) -> tuple:
    """The integers of lo..hi with no prime factor above 5."""
    out = []
    for x in range(lo, hi + 1):
        y = x
        for q in (2, 3, 5):
            while y % q == 0:
                y //= q
        if y == 1:
            out.append(x)
    return tuple(out)


RATE_POOL = smooth(2, 50)           # the README's small and middle pools, 2..50
PERIOD_POOL = (1,) + RATE_POOL      # "every hour" is a period of one
SPEED_POOL = smooth(2, 30)          # level 2's rates (the task file's run to 30)
MULTIPLE_POOL = tuple(range(1, 13))
WRONG_POOL = smooth(2, 250)         # the README's three pools together

# level 1: (subject, verb 3sg, verb base, thing, unit, pronoun, the scaled
# clause's object, the task file's pronoun after the comma)
LV1 = (
    ("A bell", "rings", "ring", "times", "hour", "it", "", "it"),
    ("A patient", "takes", "take", "pills", "day", "they", " pills", "They"),
    ("A newsstand", "sells", "sell", "newspapers", "week", "it", " newspapers", "it"),
    ("A heart", "beats", "beat", "times", "second", "it", "", "it"),
    ("A reporter", "speaks", "speak", "words", "minute", "they", "", "they"),
)
# level 2: (clause, rate unit A, per unit B, tail for A, tail for B, scale verb, fast word)
LV2 = (
    ("A car is driving at {r} miles per hour", "miles", "hours",
     "is {x} miles from destination", "is {x} hours from destination",
     "it drives", "it will be () {u} from destination", "fast"),
    ("A plane is flying at {r} kilometers per hour", "kilometers", "hours",
     "is {x} kilometers from destination", "is {x} hours from destination",
     "it flies", "it will be () {u} from destination", "fast"),
    ("A runner is running at {r} meters per second", "meters", "seconds",
     "is {x} meters from the finish line", "is {x} seconds from the finish line",
     "they run", "they will be () {u} from the finish line", "fast"),
    ("A car is consuming fuel at {r} gallons per mile", "gallons", "miles",
     "has {x} gallons left to run", "has {x} miles left to run",
     "it consumes fuel", "it will have () {u} left to run", "fast"),
    ("The beef costs {r} dollars per pound", "dollars", "pounds",
     "a shopper can buy {x} dollars of beef", "a shopper can buy {x} pounds of beef",
     "the beef costs", "the shopper can buy () {u} of beef", "much"),
    ("A bamboo grows at {r} feet per day", "feet", "days",
     "it grows {x} feet to reach the height of maturity",
     "it grows {x} days to reach the height of maturity",
     "it grows", "it will grow () {u} to reach the height of maturity", "fast"),
)


def _cap(s: str) -> str:
    return s[0].upper() + s[1:]


def _surface(surface: str) -> bool:
    if surface not in SURFACES:
        raise ValueError(f"surface {surface!r} is not one of {SURFACES}")
    return surface == "bigbench"


def lv1_sentence(row: int, n: int, p: int, k: int, often: bool, ask_time: bool,
                 shown: int, *, surface: str = "battery") -> str:
    """One level-1 sentence. `shown` is the number printed in the tail:
    the count when the time is asked, the time when the count is."""
    bb = _surface(surface)
    subj, v3, vb, thing, unit, pron, obj, bb_pron = LV1[row]
    every = f"every {unit}" if p == 1 else f"every {p} {unit}s"
    if k == 0:
        cond = f"{_cap(pron)} will {vb}"
    else:
        does = v3 if (bb or pron == "it") else vb
        how = (f"{FACTOR_WORD[k]} as often" if often
               else f"with intervals {FACTOR_WORD[k]} as long")
        cond = f"If {pron} {does}{obj} {how}, {bb_pron if bb else pron} will {vb}"
    tail = (f"{cond} {shown} {thing} in () {unit}s." if ask_time
            else f"{cond} () {thing} in {shown} {unit}s.")
    return f"{subj} {v3} {n} {thing} {every}. {tail}"


def lv2_sentence(row: int, r: int, given: int, give_a: bool, k: int, faster: bool,
                 ask_a: bool, *, surface: str = "battery") -> str:
    """One level-2 sentence: the rate `r`, the stated quantity `given`
    (in unit A if `give_a`), the quantity asked (unit A if `ask_a`)."""
    bb = _surface(surface)
    clause, ua, ub, tail_a, tail_b, sverb, ask, word = LV2[row]
    stated = tail_a.format(x=given) if give_a else tail_b.format(x=given)
    if k == 0:
        q = (ask.replace("it will be", "It is").replace("they will be", "They are")
                .replace("it will have", "It has").replace("it will grow", "It grows")
                .replace("the shopper can buy", "The shopper can buy"))
        tail = q.format(u=ua if ask_a else ub) + "."
    else:
        slow = BB_SLOW_WORD if bb else SLOW_WORD
        how = (f"{FACTOR_WORD[k]} as {word}" if faster
               else f"{slow[k]} as {word}")
        tail = f"If {sverb} {how}, " + ask.format(u=ua if ask_a else ub) + "."
    return f"{clause.format(r=r)}, and {stated}. {tail}"


def combinations(shown: int, numbers) -> set:
    """Every positive integer `shown` times or over the item's numbers,
    each to the power -1, 0 or 1: the answers of every reading of the
    sentence, right and wrong, and the shown quantity itself."""
    out = set()
    fs = [f for f in numbers if f > 1]
    for es in itertools.product((-1, 0, 1), repeat=len(fs)):
        v = Fraction(shown)
        for f, e in zip(fs, es):
            v *= Fraction(f) ** e
        if v.denominator == 1 and 0 < v <= CAP:
            out.add(int(v))
    return out


def _options(rng, answer: int, combos, pool, pos: int, rank: int):
    """Five distinct positive integers with the answer at 1-based list
    position `pos` AND at 1-based rank `rank` by magnitude. Each wrong
    option is a combination with probability P_COMBINATION and a pool
    number otherwise, on whichever side of the answer it must fall; a
    kind with no number left on that side gives way to the other. None
    when neither has one. Returns (options, kinds)."""
    a = sorted(x for x in combos if x != answer)
    b = sorted(x for x in pool if x != answer and x not in combos)
    got, kind = [], {}
    for below, need in ((True, rank - 1), (False, N_OPTIONS - rank)):
        for _ in range(need):
            ca = [x for x in a if (x < answer) == below and x not in got]
            cb = [x for x in b if (x < answer) == below and x not in got]
            first = bool(rng.random() < P_COMBINATION)
            use, name = (ca, "combination") if first else (cb, "pool")
            if not use:
                use, name = (cb, "pool") if first else (ca, "combination")
            if not use:
                return None
            x = use[int(rng.integers(len(use)))]
            got.append(x)
            kind[x] = name
    got = [got[int(i)] for i in rng.permutation(len(got))]
    opts = got[:pos - 1] + [answer] + got[pos - 1:]
    return opts, ["answer" if x == answer else kind[x] for x in opts]


def _pos_rank(slot: int, n_subjects: int) -> tuple:
    """The answer's list position and its rank by magnitude, both
    1-based. Blocks of `n_subjects` slots share a pair; over twenty-five
    blocks every pair occurs once, so position and rank are balanced and
    crossed whatever the number of subjects."""
    k = slot // n_subjects
    return k % N_OPTIONS + 1, (k // N_OPTIONS + k) % N_OPTIONS + 1


def _pick(rng, seq):
    return seq[int(rng.integers(len(seq)))]


def _draw_lv1(rng, ctx, slot):
    row = slot % len(LV1)
    subj = LV1[row][0]
    n = _pick(rng, RATE_POOL)                             # count per period
    p = _pick(rng, PERIOD_POOL)                           # period length
    j = _pick(rng, MULTIPLE_POOL)
    k = (0, 0, 2, 3, 4)[int(rng.integers(5))]             # 0 = no scaling
    often = bool(rng.integers(2))                         # faster vs slower
    ask_time = bool(rng.integers(2))
    # effective count per period-block after scaling
    if k == 0:
        n_eff, p_eff = n, p
    elif often:
        n_eff, p_eff = n * k, p
    else:
        n_eff, p_eff = n, p * k
    shown = math.lcm(n, p) * (k or 1) * j
    m = shown // (n_eff if ask_time else p_eff)           # periods observed
    T, N = p_eff * m, n_eff * m                           # elapsed time, total count
    answer = T if ask_time else N
    if shown != (N if ask_time else T) or max(shown, answer) > CAP:
        return None
    combos = combinations(shown, (n, p, k)) | {n, p} - {1}
    pool = (set(WRONG_POOL) | {shown + n, shown + p, abs(shown - n), abs(shown - p),
                               n + p, n * p}) - {0, n, p, shown}
    args = (row, n, p, k, often, ask_time, shown)
    pos, rank = _pos_rank(slot, len(LV1))
    got = _options(rng, answer, combos, {x for x in pool if x <= CAP}, pos, rank)
    if got is None:
        return None
    opts, kinds = got
    return {"question": with_options(lv1_sentence(*args), opts),
            "answer": str(answer),
            "bb_key": lv1_sentence(*args, surface="bigbench"),
            "meta": {"subject": subj, "n": n, "p": p, "m": m, "k": k,
                     "often": often, "ask_time": ask_time, "options": opts,
                     "option_kinds": kinds, "answer_pos": pos, "answer_rank": rank}}


def _draw_lv2(rng, ctx, slot):
    row = slot % len(LV2)
    clause = LV2[row][0]
    r = _pick(rng, SPEED_POOL)                            # rate, A per B
    j = _pick(rng, MULTIPLE_POOL)
    k = (0, 0, 2, 3, 4)[int(rng.integers(5))]
    faster = bool(rng.integers(2))
    give_a = bool(rng.integers(2))                        # which quantity is stated
    ask_a = bool(rng.integers(2)) if k else (not give_a)  # unscaled: ask the other
    b = r * j * (k or 1)
    a = r * b                                             # the invariant, in unit A
    if k == 0:
        answer = a if ask_a else b
    else:
        b_new = b // k if faster else b * k
        answer = a if ask_a else b_new
    given = a if give_a else b
    if max(given, answer) > CAP:
        return None
    combos = combinations(given, (r, k)) | {r}
    pool = (set(WRONG_POOL) | {given + r, abs(given - r), r * r}) - {0, r, given}
    args = (row, r, given, give_a, k, faster, ask_a)
    pos, rank = _pos_rank(slot, len(LV2))
    got = _options(rng, answer, combos, {x for x in pool if x <= CAP}, pos, rank)
    if got is None:
        return None
    opts, kinds = got
    return {"question": with_options(lv2_sentence(*args), opts),
            "answer": str(answer),
            "bb_key": lv2_sentence(*args, surface="bigbench"),
            "meta": {"subject": clause.split(" at ")[0].split(" costs")[0],
                     "r": r, "a": a, "b": b, "k": k, "faster": faster,
                     "give_a": give_a, "ask_a": ask_a, "options": opts,
                     "option_kinds": kinds, "answer_pos": pos, "answer_rank": rank,
                     # the scaled rate leaves the stated quantity unchanged
                     # and that quantity is the one asked: the answer is
                     # printed in the sentence (BIG-bench has the class)
                     "answer_stated": bool(k) and give_a and ask_a}}


register(RungSpec(
    name="unit_interp1", task="unit_interpretation", wei_class="E.3",
    rung_type="choice", answer_type="number", seed=20260910, n_options=N_OPTIONS,
    description="level 1 (one implicit unit): a rate stated as a count per "
                "period, the count or the time asked, optionally under a "
                "stated scaling; numbers without a prime factor above 5, "
                "every combination of them an integer; five integer options "
                "listed, three wrong ones in four a combination of the item's "
                "numbers and one in four a pool number; the answer's position "
                "and its rank by size both balanced",
    draw=_draw_lv1))
register(RungSpec(
    name="unit_interp2", task="unit_interpretation", wei_class="E.3",
    rung_type="choice", answer_type="number", seed=20260911, n_options=N_OPTIONS,
    description="level 2 (two implicit units): a rate and one of its two "
                "quantities, the other asked, optionally under a scaled "
                "rate with the numerator quantity invariant; numbers and "
                "options as on level 1",
    draw=_draw_lv2))
