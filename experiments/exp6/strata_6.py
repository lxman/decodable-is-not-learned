# experiments/exp6/strata_6.py
"""Exp 6 difficulty strata (design §3.1, §4): one covariate per rung, a
pure function of the committed item, fixed before any model contact.
The table has 2g's shape, so 2g's statistics read it unchanged. The
anchors' strata are 2g's own (`strata_2g.strata_for`)."""
from __future__ import annotations

from collections import Counter

from experiments.exp6 import battery_6 as b6

MIN_STRATUM = 10
N_TERCILES = 3

# kind: how the label is built; merge: 2g's ordinal merge rule applies
COVARIATE_OF_6 = {
    "modarith_add1": "carries", "modarith_sub1": "sign_borrows",
    "modarith_mul1": "product_digits", "lcs": "answer",
    "unscramble_short": "length_x_frequency",
    "unscramble_long": "length_x_frequency",
    "ascii_bubble": "length_x_frequency", "ascii_basic": "length_x_frequency",
    "ipa_word": "ipa_bin_x_frequency",
    "sort3": "prefix_class", "sort5": "prefix_class",
    "shapes": "answer_class",
    "deduction3": "answer_position", "deduction5": "answer_position",
    "temporal": "answer_position",
    "unit_interp1": "answer_position", "unit_interp2": "answer_position",
}
ORDINAL = ("carries", "product_digits", "answer", "prefix_class")

# stratum -> item count per rung, pinned from the committed item files
STRATA_COUNT_PIN_6 = {
    "modarith_add1": {"0": 80, "1": 189, "2": 159, "3": 72},
    "modarith_sub1": {"neg0": 65, "neg1": 104, "neg2": 62, "pos0": 92, "pos1": 130, "pos2": 47},
    "modarith_mul1": {"1": 10, "2": 21, "3": 136, "4": 333},
    "unscramble_short": {"4|0": 84, "4|1": 83, "4|2": 83, "5|0": 84, "5|1": 83, "5|2": 83},
    "unscramble_long": {"6|0": 56, "6|1": 56, "6|2": 55, "7|0": 56, "7|1": 56, "7|2": 55, "8|0": 56, "8|1": 55, "8|2": 55},
    "ipa_word": {"0|0": 56, "0|1": 56, "0|2": 55, "1|0": 56, "1|1": 56, "1|2": 55, "2|0": 56, "2|1": 55, "2|2": 55},
    "sort3": {"0": 167, "1": 167, "2": 166},
    "sort5": {"0": 167, "1": 167, "2": 166},
    "deduction3": {"1": 170, "2": 165, "3": 165},
    "deduction5": {"1": 100, "2": 100, "3": 100, "4": 100, "5": 100},
    "ascii_bubble": {"3|0": 42, "3|1": 42, "3|2": 41, "4|0": 42, "4|1": 42, "4|2": 41, "5|0": 42, "5|1": 42, "5|2": 41, "6|0": 42, "6|1": 42, "6|2": 41},
    "ascii_basic": {"3|0": 42, "3|1": 42, "3|2": 41, "4|0": 42, "4|1": 42, "4|2": 41, "5|0": 42, "5|1": 42, "5|2": 41, "6|0": 42, "6|1": 42, "6|2": 41},
    "shapes": {"circle": 50, "heptagon": 50, "hexagon": 50, "kite": 50, "line": 50, "octagon": 50, "pentagon": 50, "rectangle": 50, "sector": 50, "triangle": 50},
    "temporal": {"1": 126, "2": 126, "3": 125, "4": 123},
    "lcs": {"0": 50, "1": 50, "2": 50, "3": 50, "4": 50, "5": 50, "6": 50, "7": 50, "8": 50, "9": 50},
    "unit_interp1": {"1": 100, "2": 100, "3": 100, "4": 100, "5": 100},
    "unit_interp2": {"1": 102, "2": 102, "3": 102, "4": 98, "5": 96},
}


def _sg():
    from experiments.exp2g import strata_2g as sg
    return sg


def raw_level(rung: str, item: dict):
    """The covariate's raw level for one item; the frequency tercile is
    added by `strata_for_6` (it is a rank within the rung)."""
    kind = COVARIATE_OF_6[rung]
    m = item["meta"]
    if kind == "carries":
        return _sg().carries(str(m["a"]), str(m["b"]))
    if kind == "sign_borrows":
        hi, lo = max(m["a"], m["b"]), min(m["a"], m["b"])
        sign = "neg" if m["a"] < m["b"] else "pos"
        return f"{sign}{_sg().borrows(str(hi), str(lo))}"
    if kind == "product_digits":
        return len(str(m["a"] * m["b"]))
    if kind == "answer":
        return int(item["answer"])
    if kind == "prefix_class":
        return int(m["prefix_class"])
    if kind == "answer_class":
        return str(item["answer"])
    if kind == "answer_position":
        return int(m["answer_pos"])
    if kind == "length_x_frequency":
        return int(m["length"])
    if kind == "ipa_bin_x_frequency":
        return int(m["ipa_bin"])
    raise ValueError(kind)


def frequency_terciles(items, groups) -> list:
    """Tercile (0 = most frequent) of each item's word rank WITHIN its
    group; ranks are unique, so the split is exact."""
    out = [None] * len(items)
    by_group = {}
    for i, g in enumerate(groups):
        by_group.setdefault(g, []).append(i)
    for g, idx in by_group.items():
        order = sorted(idx, key=lambda i: (items[i]["meta"]["rank"], i))
        for pos, i in enumerate(order):
            out[i] = pos * N_TERCILES // len(order)
    return out


def strata_for_6(cap: dict) -> dict:
    rung = cap["name"]
    kind = COVARIATE_OF_6[rung]
    items = cap["eval_items"]
    raw = [raw_level(rung, it) for it in items]
    if kind in ("length_x_frequency", "ipa_bin_x_frequency"):
        ter = frequency_terciles(items, raw)
        levels = [f"{g}|{t}" for g, t in zip(raw, ter)]
    else:
        levels = list(raw)
    counts = Counter(levels)
    if kind in ORDINAL:
        level_map = _sg().merge_levels(dict(counts), MIN_STRATUM)
    else:
        level_map = {lv: str(lv) for lv in counts}
    strata = [level_map[lv] for lv in levels]
    out = {"kind": kind,
           "levels_raw": {str(k): int(v) for k, v in
                          sorted(counts.items(), key=lambda kv: str(kv[0]))},
           "level_map": {str(k): v for k, v in
                         sorted(level_map.items(), key=lambda kv: str(kv[0]))},
           "strata": strata,
           "counts": {k: int(v) for k, v in sorted(Counter(strata).items())}}
    small = {k: v for k, v in out["counts"].items() if v < MIN_STRATUM}
    if small and len(out["counts"]) > 1:
        raise ValueError(f"{rung}: strata below {MIN_STRATUM} items: {small}")
    return out


def build_table_6(battery: dict) -> dict:
    table = {}
    for rung, cap in battery.items():
        if rung in b6.RUNGS_6:
            table[rung] = strata_for_6(cap)
        elif rung in b6.ANCHORS_6:
            t = _sg().strata_for(cap, rung)
            table[rung] = {"kind": t["kind"],
                           "levels_raw": {str(k): v for k, v in t["levels_raw"].items()},
                           "level_map": {str(k): v for k, v in t["level_map"].items()},
                           "strata": list(t["strata"]), "counts": dict(t["counts"])}
    return table


def check_strata_pins_6(table: dict) -> dict:
    """Every Exp 6 rung's strata counts against the pin; the anchors'
    raw level counts against 2g's own pin."""
    out = {}
    for rung in b6.RUNGS_6:
        if table[rung]["counts"] != STRATA_COUNT_PIN_6[rung]:
            raise ValueError(f"{rung}: strata counts {table[rung]['counts']} "
                             f"against the pin {STRATA_COUNT_PIN_6[rung]}")
        if len(table[rung]["strata"]) != b6.N_ITEMS:
            raise ValueError(f"{rung}: {len(table[rung]['strata'])} labels")
        out[rung] = "PASS"
    for rung in b6.ANCHORS_6:
        if rung not in table:
            continue
        want = {str(k): v for k, v in _sg().RAW_COUNT_PIN[rung].items()}
        if table[rung]["levels_raw"] != want:
            raise ValueError(f"{rung}: raw levels {table[rung]['levels_raw']} "
                             f"against 2g's pin {want}")
        out[rung] = "PASS"
    return out
