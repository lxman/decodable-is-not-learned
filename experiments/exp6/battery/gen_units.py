# experiments/exp6/battery/gen_units.py
"""Unit interpretation, levels 1 and 2 (BIG-bench unit_interpretation
lv1 / lv2; Wei class E.3). The subjects, units and sentence frames are
the README's and the task files'. Every number in an item and its answer
is a positive integer.

Each sentence has two SURFACES. "battery" is what a model reads: the
task files' wording with their grammar slips corrected ("If they
takes", a capital "They" after a comma, "one forth"). "bigbench" is the
task files' wording byte for byte, slips included, and is what the
collision key is built from — a corrected key would never match the
string it is meant to exclude."""
from __future__ import annotations

from .spec import RungSpec, register, with_options

N_OPTIONS = 5
FACTOR_WORD = {2: "twice", 3: "three times", 4: "four times"}
SLOW_WORD = {2: "half", 3: "one third", 4: "one fourth"}
BB_SLOW_WORD = {2: "half", 3: "one third", 4: "one forth"}     # the task file's spelling
SURFACES = ("battery", "bigbench")
SMALL, MIDDLE = (2, 7), (8, 50)     # README's number pools (large unused here)

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


def _options(rng, answer: int, wrong, pos: int) -> list:
    """The answer at 1-based position `pos` among four distinct wrong
    positive integers. `wrong` lists the unit-confusion candidates
    first; random fill after; the wrong ones are shuffled."""
    picks = []
    for w in wrong:
        if isinstance(w, int) and w > 0 and w != answer and w not in picks:
            picks.append(w)
    picks = picks[:N_OPTIONS - 1]
    while len(picks) < N_OPTIONS - 1:
        w = int(rng.integers(2, 4 * answer + 10))
        if w != answer and w not in picks:
            picks.append(w)
    picks = [picks[int(i)] for i in rng.permutation(len(picks))]
    return picks[:pos - 1] + [answer] + picks[pos - 1:]


def _pos(slot: int, n_subjects: int) -> int:
    """The answer's position cycles with the slot, crossed with the
    subject cycle, so the position strata are balanced by design."""
    return (slot // n_subjects) % N_OPTIONS + 1


def _draw_lv1(rng, ctx, slot):
    row = slot % len(LV1)
    subj = LV1[row][0]
    n = int(rng.integers(SMALL[0], MIDDLE[1] + 1))       # count per period
    p = int(rng.integers(1, 13))                          # period length
    m = int(rng.integers(2, 13))                          # periods observed
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
    T = p_eff * m                                         # elapsed time
    N = n_eff * m                                         # total count
    if ask_time:
        shown, answer = N, T
        wrong = [N, m, N * p, N // n if N % n == 0 else 0, p * m, T * n]
    else:
        shown, answer = T, N
        wrong = [T, m, T * n, n * m, T // p if T % p == 0 else 0, N * p]
    args = (row, n, p, k, often, ask_time, shown)
    pos = _pos(slot, len(LV1))
    opts = _options(rng, answer, wrong, pos)
    return {"question": with_options(lv1_sentence(*args), opts),
            "answer": str(answer),
            "bb_key": lv1_sentence(*args, surface="bigbench"),
            "meta": {"subject": subj, "n": n, "p": p, "m": m, "k": k,
                     "often": often, "ask_time": ask_time, "options": opts,
                     "answer_pos": pos}}


def _draw_lv2(rng, ctx, slot):
    row = slot % len(LV2)
    clause = LV2[row][0]
    r = int(rng.integers(2, 31))                          # rate, A per B
    k = (0, 0, 2, 3, 4)[int(rng.integers(5))]
    faster = bool(rng.integers(2))
    give_a = bool(rng.integers(2))                        # which quantity is stated
    ask_a = bool(rng.integers(2)) if k else (not give_a)  # unscaled: ask the other
    b = int(rng.integers(2, 25)) * (k if k and faster else 1)
    a = r * b                                             # the invariant, in unit A
    if k == 0:
        answer = a if ask_a else b
        wrong = [b if ask_a else a, r, a * r, r * r, b * b]
    else:
        b_new = b // k if faster else b * k
        answer = a if ask_a else b_new
        wrong = [b, a, b_new, a * k, a // k if a % k == 0 else 0, r, b * k]
    args = (row, r, a if give_a else b, give_a, k, faster, ask_a)
    pos = _pos(slot, len(LV2))
    opts = _options(rng, answer, wrong, pos)
    return {"question": with_options(lv2_sentence(*args), opts),
            "answer": str(answer),
            "bb_key": lv2_sentence(*args, surface="bigbench"),
            "meta": {"subject": clause.split(" at ")[0].split(" costs")[0],
                     "r": r, "a": a, "b": b, "k": k, "faster": faster,
                     "give_a": give_a, "ask_a": ask_a, "options": opts,
                     "answer_pos": pos,
                     # the scaled rate leaves the stated quantity unchanged
                     # and that quantity is the one asked: the answer is
                     # printed in the sentence (BIG-bench has the class)
                     "answer_stated": bool(k) and give_a and ask_a}}


register(RungSpec(
    name="unit_interp1", task="unit_interpretation", wei_class="E.3",
    rung_type="choice", answer_type="number", seed=20260910, n_options=N_OPTIONS,
    description="level 1 (one implicit unit): a rate stated as a count per "
                "period, the count or the time asked, optionally under a "
                "stated scaling; five integer options listed",
    draw=_draw_lv1))
register(RungSpec(
    name="unit_interp2", task="unit_interpretation", wei_class="E.3",
    rung_type="choice", answer_type="number", seed=20260911, n_options=N_OPTIONS,
    description="level 2 (two implicit units): a rate and one of its two "
                "quantities, the other asked, optionally under a scaled "
                "rate with the numerator quantity invariant; five integer "
                "options listed",
    draw=_draw_lv2))
