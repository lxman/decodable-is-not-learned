# experiments/exp6/strata_6.py
"""Exp 6 difficulty strata (design §3.1, §4): one covariate per rung, a
pure function of the committed item, fixed before any model contact.
The table has 2g's shape, so 2g's statistics read it unchanged. The
anchors' strata are 2g's own (`strata_2g.strata_for`).

Beside the stratum, a STRUCTURE level per item (plan delta B-21): the
property of the item's surface that would make it easy for any model
and that the stratum does not condition on — a letter left in place, a
list one swap from sorted, a position a clue states outright. It is
counted, pinned, and crossed into the stratum by a named secondary; the
primary's strata are the design's."""
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
    "modarith_add1": {"0": 80, "1": 188, "2": 159, "3": 73},
    "modarith_sub1": {"neg0": 65, "neg1": 104, "neg2": 61, "pos0": 93, "pos1": 130, "pos2": 47},
    "modarith_mul1": {"1": 10, "2": 19, "3": 129, "4": 342},
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


# rung -> what its structure level reads (None: nothing beyond the stratum)
STRUCTURE_OF_6 = {
    "modarith_add1": "plus_one_ripples", "modarith_sub1": "plus_one_ripples",
    "modarith_mul1": "plus_one_ripples",
    "unscramble_short": "letters_in_place", "unscramble_long": "letters_in_place",
    "ipa_word": "stress_marked",
    "sort3": "inversions", "sort5": "inversions",
    "deduction3": "stated_x_extreme", "deduction5": "stated_x_extreme",
    "ascii_bubble": None, "ascii_basic": None,
    "shapes": "pen_restated", "temporal": "free_position",
    "lcs": "length_for_its_answer",
    "unit_interp1": "scaling", "unit_interp2": "scaling",
}
SORT5_BINS = ((0, 3), (4, 6), (7, 10))      # inversions of five words: 0..10
# level -> item count per rung, pinned from the committed item files
STRUCTURE_COUNT_PIN_6 = {
    "modarith_add1": {"0": 441, "1": 59},
    "modarith_sub1": {"0": 445, "1": 55},
    "modarith_mul1": {"0": 481, "1": 19},
    "unscramble_short": {"0": 145, "1": 198, "2": 157},
    "unscramble_long": {"0": 122, "1": 167, "2": 211},
    "ipa_word": {"marked": 312, "plain": 188},
    "sort3": {"1": 200, "2": 207, "3": 93},
    "sort5": {"0-3": 114, "4-6": 257, "7-10": 129},
    "deduction3": {"derived|end": 287, "derived|inner": 107, "stated|end": 63, "stated|inner": 43},
    "deduction5": {"derived|end": 143, "derived|inner": 189, "stated|end": 50, "stated|inner": 118},
    "ascii_bubble": {},
    "ascii_basic": {},
    "shapes": {"0": 245, "1": 255},
    "temporal": {"first": 101, "last": 99, "middle": 300},
    "lcs": {"long": 258, "short": 242},
    "unit_interp1": {"intervals": 172, "often": 130, "plain": 198},
    "unit_interp2": {"computed": 228, "plain": 196, "stated": 76},
}


def _sg():
    from experiments.exp2g import strata_2g as sg
    return sg


def inversions(words) -> int:
    return sum(1 for i in range(len(words)) for j in range(i + 1, len(words))
               if words[i] > words[j])


def structure_levels(cap: dict) -> list:
    """One level per item, a string; [] for a rung that has none."""
    rung = cap["name"]
    kind = STRUCTURE_OF_6[rung]
    items = cap["eval_items"]
    if kind is None:
        return []
    out = []
    if kind == "length_for_its_answer":
        # the two strings' total length against the median of the
        # items that share the answer: short or long FOR ITS ANSWER
        total = [len(it["meta"]["a"]) + len(it["meta"]["b"]) for it in items]
        by = {}
        for it, t in zip(items, total):
            by.setdefault(it["answer"], []).append(t)
        med = {a: sorted(v)[len(v) // 2] for a, v in by.items()}
        return ["long" if t >= med[it["answer"]] else "short"
                for it, t in zip(items, total)]
    for it in items:
        m = it["meta"]
        if kind == "plus_one_ripples":
            # the +1 changes more than the result's last digit
            base = int(it["answer"]) - 1
            out.append(str(int(str(base)[:-1] != str(base + 1)[:-1])))
        elif kind == "letters_in_place":
            n = sum(1 for a, b in zip(m["word"], m["scrambled"]) if a == b)
            out.append(str(min(n, 2)))
        elif kind == "stress_marked":
            # the transcription carries a stress mark: a model that omits
            # them, as much IPA does, fails these and no others
            out.append("marked" if any(c in it["answer"] for c in "ˈˌ") else "plain")
        elif kind == "inversions":
            n = inversions(m["words"])
            if len(m["words"]) == 3:
                out.append(str(n))
            else:
                out.append(next(f"{lo}-{hi}" for lo, hi in SORT5_BINS if lo <= n <= hi))
        elif kind == "stated_x_extreme":
            extreme = m["asked"] in (1, len(m["listed"]))
            out.append(("stated" if m["stated"] else "derived") + "|" +
                       ("end" if extreme else "inner"))
        elif kind == "pen_restated":
            out.append(str(int(m["path"].count("M ") > 1)))
        elif kind == "free_position":
            out.append(str(m["free_position"]))
        elif kind == "scaling":
            if not m["k"]:
                out.append("plain")
            elif "answer_stated" in m:
                out.append("stated" if m["answer_stated"] else "computed")
            else:
                out.append("often" if m["often"] else "intervals")
        else:
            raise ValueError(kind)
    return out


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


def structure_table_6(battery: dict, table: dict) -> dict:
    """The strata with the structure level crossed in: 2g's shape again,
    so the same statistic reads it. A rung without a structure level
    keeps its strata. Composite strata are NOT merged and may be small;
    the secondary that reads them is descriptive."""
    out = {}
    for rung in b6.RUNGS_6:
        if rung not in battery:
            continue
        lv = structure_levels(battery[rung])
        base = list(table[rung]["strata"])
        strata = [f"{s}|{x}" for s, x in zip(base, lv)] if lv else base
        out[rung] = {"kind": f"{table[rung]['kind']} x {STRUCTURE_OF_6[rung]}",
                     "structure": lv,
                     "structure_counts": {k: int(v) for k, v in
                                          sorted(Counter(lv).items())},
                     "strata": strata,
                     "counts": {k: int(v) for k, v in sorted(Counter(strata).items())}}
    return out


def check_structure_pins_6(stable: dict) -> dict:
    out = {}
    for rung in b6.RUNGS_6:
        if stable[rung]["structure_counts"] != STRUCTURE_COUNT_PIN_6[rung]:
            raise ValueError(f"{rung}: structure counts "
                             f"{stable[rung]['structure_counts']} against the pin "
                             f"{STRUCTURE_COUNT_PIN_6[rung]}")
        if len(stable[rung]["strata"]) != b6.N_ITEMS:
            raise ValueError(f"{rung}: {len(stable[rung]['strata'])} labels")
        out[rung] = "PASS"
    return out


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
