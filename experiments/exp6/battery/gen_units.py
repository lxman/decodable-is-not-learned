# experiments/exp6/battery/gen_units.py
"""Unit interpretation, levels 1 and 2 (BIG-bench unit_interpretation
lv1 / lv2; Wei class E.3). The subjects, units and sentence frames are
the README's and the task files'; the grammar slips in BIG-bench's own
25 examples per level ("If they takes", "one forth") are NOT reproduced.
Every number in an item and its answer is a positive integer."""
from __future__ import annotations

from .spec import RungSpec, register, with_options

N_OPTIONS = 5
FACTOR_WORD = {2: "twice", 3: "three times", 4: "four times"}
SLOW_WORD = {2: "half", 3: "one third", 4: "one fourth"}
SMALL, MIDDLE = (2, 7), (8, 50)     # README's number pools (large unused here)

# level 1: (subject, verb 3sg, verb base, thing, unit, pronoun)
LV1 = (
    ("A bell", "rings", "ring", "times", "hour", "it"),
    ("A patient", "takes", "take", "pills", "day", "they"),
    ("A newsstand", "sells", "sell", "newspapers", "week", "it"),
    ("A heart", "beats", "beat", "times", "second", "it"),
    ("A reporter", "speaks", "speak", "words", "minute", "they"),
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
    subj, v3, vb, thing, unit, pron = LV1[slot % len(LV1)]
    n = int(rng.integers(SMALL[0], MIDDLE[1] + 1))       # count per period
    p = int(rng.integers(1, 13))                          # period length
    m = int(rng.integers(2, 13))                          # periods observed
    k = (0, 0, 2, 3, 4)[int(rng.integers(5))]             # 0 = no scaling
    often = bool(rng.integers(2))                         # faster vs slower
    ask_time = bool(rng.integers(2))
    every = f"every {unit}" if p == 1 else f"every {p} {unit}s"
    head = f"{subj} {v3} {n} {thing} {every}."
    # effective count per period-block after scaling
    obj = "" if thing == "times" else f" {thing}"
    does = v3 if pron == "it" else vb
    if k == 0:
        n_eff, p_eff, cond = n, p, f"{_cap(pron)} will {vb}"
    elif often:
        n_eff, p_eff = n * k, p
        cond = (f"If {pron} {does}{obj} {FACTOR_WORD[k]} as often, "
                f"{pron} will {vb}")
    else:
        n_eff, p_eff = n, p * k
        cond = (f"If {pron} {does}{obj} with intervals {FACTOR_WORD[k]} as "
                f"long, {pron} will {vb}")
    T = p_eff * m                                         # elapsed time
    N = n_eff * m                                         # total count
    if ask_time:
        tail = f"{cond} {N} {thing} in () {unit}s."
        answer, wrong = T, [N, m, N * p, N // n if N % n == 0 else 0, p * m, T * n]
    else:
        tail = f"{cond} () {thing} in {T} {unit}s."
        answer, wrong = N, [T, m, T * n, n * m, T // p if T % p == 0 else 0, N * p]
    sentence = f"{head} {tail}"
    pos = _pos(slot, len(LV1))
    opts = _options(rng, answer, wrong, pos)
    return {"question": with_options(sentence, opts), "answer": str(answer),
            "bb_key": sentence,
            "meta": {"subject": subj, "n": n, "p": p, "m": m, "k": k,
                     "often": often, "ask_time": ask_time, "options": opts,
                     "answer_pos": pos}}


def _draw_lv2(rng, ctx, slot):
    clause, ua, ub, tail_a, tail_b, sverb, ask, word = LV2[slot % len(LV2)]
    r = int(rng.integers(2, 31))                          # rate, A per B
    k = (0, 0, 2, 3, 4)[int(rng.integers(5))]
    faster = bool(rng.integers(2))
    give_a = bool(rng.integers(2))                        # which quantity is stated
    ask_a = bool(rng.integers(2)) if k else (not give_a)  # unscaled: ask the other
    b = int(rng.integers(2, 25)) * (k if k and faster else 1)
    a = r * b                                             # the invariant, in unit A
    given = (tail_a.format(x=a) if give_a else tail_b.format(x=b))
    if k == 0:
        q = (ask.replace("it will be", "It is").replace("they will be", "They are")
                .replace("it will have", "It has").replace("it will grow", "It grows")
                .replace("the shopper can buy", "The shopper can buy"))
        tail = q.format(u=ua if ask_a else ub) + "."
        answer = a if ask_a else b
        wrong = [b if ask_a else a, r, a * r, r * r, b * b]
    else:
        how = (f"{FACTOR_WORD[k]} as {word}" if faster
               else f"{SLOW_WORD[k]} as {word}")
        tail = f"If {sverb} {how}, " + ask.format(u=ua if ask_a else ub) + "."
        b_new = b // k if faster else b * k
        answer = a if ask_a else b_new
        wrong = [b, a, b_new, a * k, a // k if a % k == 0 else 0, r, b * k]
    sentence = f"{clause.format(r=r)}, and {given}. {tail}"
    pos = _pos(slot, len(LV2))
    opts = _options(rng, answer, wrong, pos)
    return {"question": with_options(sentence, opts), "answer": str(answer),
            "bb_key": sentence,
            "meta": {"subject": clause.split(" at ")[0].split(" costs")[0],
                     "r": r, "a": a, "b": b, "k": k, "faster": faster,
                     "give_a": give_a, "ask_a": ask_a, "options": opts,
                     "answer_pos": pos}}


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
