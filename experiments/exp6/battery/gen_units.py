# experiments/exp6/battery/gen_units.py
"""Unit interpretation, levels 1 and 2 (BIG-bench unit_interpretation
lv1 / lv2; Wei class E.3). The subjects, units and sentence frames are
the README's and the task files'. Every number in an item and its answer
is a positive integer.

The numbers and the wrong options follow the README's generation rule
(its steps 3 and 5), as far as it is stated. Numbers are drawn from the
integers with no prime factor above 5 ("excluding numbers with large
prime factors"); the quantity a sentence shows is a multiple of each of
the item's numbers ("applying the least common multiples"), so that a
wrong reading of the sentence gives an integer too. "Most incorrect
answers are the wrong combination of the generated numbers based on
incorrect unit interpretation, and others are random numbers generated
from the pool of numbers".

WHAT A SENTENCE'S NUMBERS AND OPTIONS SAY OF ITS ANSWER: NOTHING. Two
sentences that differ only in the ROLES of their units — which quantity
is stated, which is asked — have different answers. An item's numbers
are drawn without regard to the roles: the quantity shown is built from
them the same way whichever quantity it is, and a draw is refused when
any reading of the sentence exceeds the cap, not when its answer does.
An item's options are drawn without regard to the roles: they are
  the CANDIDATES — the answer of every sentence that differs from the
    item's in the roles alone (on level 1, in the direction of the
    scaling too), so the item's own answer among them;
  then FILLS — another combination of the item's numbers (the shown
    quantity times or over them, a number used twice or left out; the
    sentence's other misreadings are among these) three times in four,
    a pool number once in four.
Only the answer's place in the list depends on which candidate it is,
and that place is set by the slot. A reader who does not read the units
can do no better than the share of the commonest role.

What an item asks, the kind of its scaling and the answer's list
position are set by the slot; its numbers and its fills are drawn. The
answer's rank by size is not designed: it follows from what is asked.

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
P_COMBINATION = 0.75                # a fill is a combination, else a pool number
SCALINGS = ("plain", "up", "down")  # none; the rate scaled up; the rate scaled down
FACTORS = (2, 3, 4)


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


def combinations(shown: int, numbers, depth: int = 1) -> set:
    """Every positive integer `shown` times or over the item's numbers,
    each to a power of -depth .. depth, that does not exceed CAP."""
    out = set()
    fs = [f for f in numbers if f > 1]
    for es in itertools.product(range(-depth, depth + 1), repeat=len(fs)):
        v = Fraction(shown)
        for f, e in zip(fs, es):
            v *= Fraction(f) ** e
        if v.denominator == 1 and 0 < v <= CAP:
            out.add(int(v))
    return out


def readings(shown: int, rate: Fraction, k: int, *, steps=(-1, 1)) -> dict:
    """The readings of a sentence, right and wrong: `shown` times the
    rate to each power of `steps`, times the scaling factor to the power
    -1, 0 or 1 (0 alone when the sentence has no scaling). Returns
    {"all": every integer reading, "each": those that use every number
    of the sentence once — the rate, and the factor if there is one,
    "dropped": how many readings are no integer or exceed CAP}."""
    every, each, dropped = set(), set(), 0
    for e in steps:
        for c in ((-1, 0, 1) if k else (0,)):
            v = Fraction(shown) * rate ** e * Fraction(k or 1) ** c
            if v.denominator == 1 and 0 < v <= CAP:
                every.add(int(v))
                if e != 0 and (c != 0) == bool(k):
                    each.add(int(v))
            else:
                dropped += 1
    return {"all": every, "each": each, "dropped": dropped}


def candidates_lv1(shown: int, n: int, p: int, k: int) -> set:
    """The answers of the level-1 sentences that print these numbers:
    the count asked or the time, the rate scaled up or down."""
    return readings(shown, Fraction(n, p), k)["each"]


def candidates_lv2(given: int, r: int, k: int, faster: bool) -> set:
    """The answers of the level-2 sentences that print these numbers
    and this scaling: the stated quantity in either unit, either unit
    asked. Unscaled, the other quantity is asked: the product and the
    quotient. Scaled: the stated quantity itself (the invariant, stated
    and asked), the product (the invariant asked), the stated quantity
    rescaled, and the quotient rescaled."""
    g = Fraction(given)
    if not k:
        out = {g * r, g / r}
    else:
        c = Fraction(1, k) if faster else Fraction(k)
        out = {g, g * r, g * c, g * c / r}
    if any(v.denominator != 1 or not 0 < v <= CAP for v in out):
        raise AssertionError("a candidate is no integer within the cap")
    return {int(v) for v in out}


def _offer(rng, answer: int, candidates, read, combos, pool, pos: int):
    """Five distinct positive integers, the answer at 1-based list
    position `pos`: every candidate, then fills — a combination with
    probability P_COMBINATION, else a pool number; a kind with no number
    left gives way to the other. Which candidate the answer is decides
    its place in the list and nothing else. Returns (options, kinds), or
    None when the fills run out."""
    if answer not in candidates or len(candidates) >= N_OPTIONS:
        raise AssertionError("the answer is not one of the candidates")
    got = sorted(candidates)
    a = sorted(x for x in combos if x not in candidates)
    b = sorted(x for x in pool if x not in candidates and x not in combos)
    while len(got) < N_OPTIONS:
        ca = [x for x in a if x not in got]
        cb = [x for x in b if x not in got]
        combo_first = bool(rng.random() < P_COMBINATION)
        use = ca if combo_first else cb
        if not use:
            use = cb if combo_first else ca
        if not use:
            return None
        got.append(use[int(rng.integers(len(use)))])
    others = [x for x in got if x != answer]
    others = [others[int(i)] for i in rng.permutation(len(others))]
    opts = others[:pos - 1] + [answer] + others[pos - 1:]

    def kind(x):
        return ("answer" if x == answer else "misreading" if x in read["all"]
                else "combination" if x in combos else "pool")
    return opts, [kind(x) for x in opts]


# level 1: (the kind of scaling, the time asked); a cycle of six slots,
# every pair of the two once
CELLS_LV1 = tuple((SCALINGS[i % 3], bool(i % 2)) for i in range(6))
# level 2: (the kind of scaling, unit A stated, unit A asked); a cycle of
# twelve slots — an unscaled sentence, then two scaled ones — with the
# two unscaled cells twice each and the eight scaled cells once
_SCALED_LV2 = tuple((s, g, a) for s in ("up", "down") for g in (True, False)
                    for a in (True, False))
CELLS_LV2 = tuple(
    ("plain", i % 2 == 0, i % 2 == 1) if j == 0 else _SCALED_LV2[2 * i + j - 1]
    for i in range(4) for j in range(3))


def design_lv1(slot: int) -> dict:
    """What the slot fixes on level 1. The subject cycles with the slot,
    the list position with the block of five slots, the cell with the
    slot: over 150 slots every (subject, position, cell) occurs once."""
    scaling, ask_time = CELLS_LV1[slot % len(CELLS_LV1)]
    return {"row": slot % len(LV1), "pos": (slot // len(LV1)) % N_OPTIONS + 1,
            "scaling": scaling, "ask_time": ask_time}


def design_lv2(slot: int) -> dict:
    """What the slot fixes on level 2. The cell and the list position
    cycle with the slot, the subject with the block of twelve slots:
    over 60 slots every (cell of the twelve, position) occurs once, over
    360 every (subject, cell, position)."""
    scaling, give_a, ask_a = CELLS_LV2[slot % len(CELLS_LV2)]
    return {"row": (slot // len(CELLS_LV2)) % len(LV2), "pos": slot % N_OPTIONS + 1,
            "scaling": scaling, "give_a": give_a, "ask_a": ask_a}


def _pick(rng, seq):
    return seq[int(rng.integers(len(seq)))]


def _rank(opts, answer: int) -> int:
    return sorted(opts).index(answer) + 1


def _draw_lv1(rng, ctx, slot, d=None):
    d = d or design_lv1(slot)
    row, ask_time = d["row"], d["ask_time"]
    subj = LV1[row][0]
    n = _pick(rng, RATE_POOL)                             # count per period
    p = _pick(rng, PERIOD_POOL)                           # period length
    j = _pick(rng, MULTIPLE_POOL)
    k = _pick(rng, FACTORS) if d["scaling"] != "plain" else 0
    often = d["scaling"] == "up"                          # faster vs slower
    if Fraction(n, p) in {Fraction(f) ** e for f in (1, k or 1) for e in (-1, 1)}:
        return None                  # a rate of one, or the factor's: a reading of
                                     # the sentence is the number it shows
    shown = math.lcm(n, p) * (k or 1) * j
    if shown in (n, p):
        return None                  # the sentence would restate its own rate
    if shown * max(Fraction(n, p), Fraction(p, n)) * (k or 1) > CAP:
        return None                  # a reading over the cap, whatever is asked
    # effective count per period-block after scaling
    if k == 0:
        n_eff, p_eff = n, p
    elif often:
        n_eff, p_eff = n * k, p
    else:
        n_eff, p_eff = n, p * k
    m = shown // (n_eff if ask_time else p_eff)           # periods observed
    T, N = p_eff * m, n_eff * m                           # elapsed time, total count
    answer = T if ask_time else N
    if shown != (N if ask_time else T):
        raise AssertionError("the shown quantity is not the one the sentence states")
    read = readings(shown, Fraction(n, p), k)
    cands = candidates_lv1(shown, n, p, k)
    if read["dropped"] or shown in cands or len(cands) != (4 if k else 2):
        raise AssertionError("the readings of the sentence are not what the draw says")
    combos = combinations(shown, (n, p, k), depth=2) | {n, p} - {1}
    pool = (set(WRONG_POOL) | {shown + n, shown + p, abs(shown - n), abs(shown - p),
                               n + p, n * p}) - {0, n, p, shown}
    got = _offer(rng, answer, cands, read, combos, {x for x in pool if x <= CAP},
                 d["pos"])
    if got is None:
        return None
    opts, kinds = got
    args = (row, n, p, k, often, ask_time, shown)
    return {"question": with_options(lv1_sentence(*args), opts),
            "answer": str(answer),
            "bb_key": lv1_sentence(*args, surface="bigbench"),
            "meta": {"subject": subj, "n": n, "p": p, "m": m, "k": k,
                     "often": often, "ask_time": ask_time, "shown": shown,
                     "options": opts, "option_kinds": kinds,
                     "candidates": sorted(cands), "answer_pos": d["pos"],
                     "answer_rank": _rank(opts, answer)}}


def _draw_lv2(rng, ctx, slot, d=None):
    d = d or design_lv2(slot)
    row, give_a, ask_a = d["row"], d["give_a"], d["ask_a"]
    clause = LV2[row][0]
    r = _pick(rng, SPEED_POOL)                            # rate, A per B
    j = _pick(rng, MULTIPLE_POOL)
    k = _pick(rng, FACTORS) if d["scaling"] != "plain" else 0
    faster = d["scaling"] == "up"
    if k and (r == k or r * r == k):
        return None                  # two candidates would be one number
    given = r * j * (k or 1)         # the stated quantity, whichever unit it is in
    if given * r * (k or 1) > CAP:
        return None                  # a reading over the cap, whatever is asked
    a, b = (given, given // r) if give_a else (given * r, given)   # a = r b
    if k == 0:
        if ask_a == give_a:
            raise AssertionError("an unscaled sentence asks the other quantity")
        answer = a if ask_a else b
    else:
        b_new = b // k if faster else b * k
        answer = a if ask_a else b_new
    read = readings(given, Fraction(r), k, steps=(-1, 0, 1))
    cands = candidates_lv2(given, r, k, faster)
    if read["dropped"] or not cands <= read["all"] or len(cands) != (4 if k else 2):
        raise AssertionError("the readings of the sentence are not what the draw says")
    combos = combinations(given, (r, k), depth=2) | {r}
    pool = (set(WRONG_POOL) | {given + r, abs(given - r), r * r}) - {0, r, given}
    got = _offer(rng, answer, cands, read, combos, {x for x in pool if x <= CAP},
                 d["pos"])
    if got is None:
        return None
    opts, kinds = got
    args = (row, r, given, give_a, k, faster, ask_a)
    return {"question": with_options(lv2_sentence(*args), opts),
            "answer": str(answer),
            "bb_key": lv2_sentence(*args, surface="bigbench"),
            "meta": {"subject": clause.split(" at ")[0].split(" costs")[0],
                     "r": r, "a": a, "b": b, "k": k, "faster": faster,
                     "give_a": give_a, "ask_a": ask_a, "given": given,
                     "options": opts, "option_kinds": kinds,
                     "candidates": sorted(cands), "answer_pos": d["pos"],
                     "answer_rank": _rank(opts, answer),
                     # the scaled rate leaves the stated quantity unchanged
                     # and that quantity is the one asked: the answer is
                     # printed in the sentence (BIG-bench has the class)
                     "answer_stated": bool(k) and give_a and ask_a}}


register(RungSpec(
    name="unit_interp1", task="unit_interpretation", wei_class="E.3",
    rung_type="choice", answer_type="number", seed=20260910, n_options=N_OPTIONS,
    description="level 1 (one implicit unit): a rate stated as a count per "
                "period, the count or the time asked, optionally under a "
                "stated scaling; numbers without a prime factor above 5, the "
                "shown quantity a multiple of each; five integer options "
                "listed: the answer of every sentence that prints the same "
                "numbers, then other combinations of them three times in "
                "four and pool numbers once in four; numbers and options "
                "drawn without regard to what is asked; what is asked, the "
                "kind of scaling and the answer's list position set by the "
                "slot",
    draw=_draw_lv1))
register(RungSpec(
    name="unit_interp2", task="unit_interpretation", wei_class="E.3",
    rung_type="choice", answer_type="number", seed=20260911, n_options=N_OPTIONS,
    description="level 2 (two implicit units): a rate and one of its two "
                "quantities, either asked, optionally under a scaled "
                "rate with the numerator quantity invariant; numbers and "
                "options as on level 1",
    draw=_draw_lv2))
