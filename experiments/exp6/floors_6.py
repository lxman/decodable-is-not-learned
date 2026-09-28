# experiments/exp6/floors_6.py
"""Exp 6 floors: 2d's rule, max(majority share, 1/n_options), with the
option count DECLARED per rung and checked against every item, never
detected (2d's detector reads "options after the last colon", which the
sort rungs' own question text would trip). The bar is 2d's
`binomial_bar` verbatim."""
from __future__ import annotations

from collections import Counter

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import verify_6 as v6
from experiments.exp6.battery.spec import OPTIONS_PREFIX


# rung -> [majority count of 500, declared option count], pinned from the
# committed item files; floor = max(majority count / 500, 1 / n_options)
FLOOR_PIN_6 = {
    "modarith_add1": [3, None],
    "modarith_sub1": [4, None],
    "modarith_mul1": [8, None],
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
