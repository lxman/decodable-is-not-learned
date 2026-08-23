# experiments/exp2g/strata_2g.py
"""Exp 2g difficulty covariates (design §6.2, ruling h) and the
stratum merge rule (ruling i). One covariate per rung, a pure function
of the committed item; the raw level counts are pinned to the doc's
table and re-asserted at build and at analysis."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

EXP2G = Path(__file__).resolve().parent
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import labels_2g as lb  # noqa: E402

COVARIATE_OF = {
    "add3_mid": "carries", "sub3_mid": "borrows", "sub4_mid": "borrows",
    "add_base8": "oct_carry", "sub_base8": "oct_borrow",
    "antonym": "position", "antonym6": "position", "median5": "position",
    "odd6": "position",
    "arith_next": "crosses_100", "count_div13": "count",
}
NOMINAL = ("position",)          # never merged (ruling i)
MIN_STRATUM = 10
_NUMS = re.compile(r"\d+")

# §6.2's printed counts (item-file facts), pinned
RAW_COUNT_PIN = {
    "add3_mid": {0: 77, 1: 155, 2: 184, 3: 84},
    "sub3_mid": {0: 164, 1: 238, 2: 98},
    "sub4_mid": {0: 84, 1: 184, 2: 175, 3: 57},
    "add_base8": {0: 277, 1: 223},
    "sub_base8": {0: 309, 1: 191},
    "antonym": {1: 132, 2: 120, 3: 128, 4: 120},
    "antonym6": {1: 78, 2: 73, 3: 79, 4: 99, 5: 89, 6: 82},
    "median5": {1: 102, 2: 93, 3: 100, 4: 116, 5: 89},
    "odd6": {1: 75, 2: 77, 3: 90, 4: 82, 5: 87, 6: 89},
    "arith_next": {0: 266, 1: 234},
    "count_div13": {2: 15, 3: 78, 4: 56, 5: 79, 6: 73, 7: 68, 8: 67, 9: 61,
                    10: 3},
}


def _operands(question: str) -> tuple:
    nums = _NUMS.findall(question)
    if len(nums) < 2:
        raise ValueError(f"fewer than two operands in {question!r}")
    return nums[0], nums[1]


def carries(a: str, b: str) -> int:
    """Column carries in the decimal addition a + b."""
    da, db = a[::-1], b[::-1]
    n, carry = 0, 0
    for k in range(max(len(da), len(db))):
        x = int(da[k]) if k < len(da) else 0
        y = int(db[k]) if k < len(db) else 0
        carry = 1 if x + y + carry >= 10 else 0
        n += carry
    return n


def borrows(a: str, b: str) -> int:
    """Column borrows in the decimal subtraction a − b (a ≥ b)."""
    if int(a) < int(b):
        raise ValueError(f"borrows: {a} − {b} is not positive")
    da, db = a[::-1], b[::-1]
    n, borrow = 0, 0
    for k in range(max(len(da), len(db))):
        x = int(da[k]) if k < len(da) else 0
        y = int(db[k]) if k < len(db) else 0
        borrow = 1 if x - y - borrow < 0 else 0
        n += borrow
    return n


def covariate(rung: str, item: dict) -> int:
    kind = COVARIATE_OF.get(rung)
    if kind is None:
        raise ValueError(f"{rung!r} has no 2g covariate")
    q = item["question"]
    if kind == "carries":
        a, b = _operands(q)
        return carries(a, b)
    if kind == "borrows":
        a, b = _operands(q)
        return borrows(a, b)
    if kind in ("oct_carry", "oct_borrow"):
        a, b = _operands(q)
        if not (re.fullmatch(r"[0-7]+", a) and re.fullmatch(r"[0-7]+", b)):
            raise ValueError(f"{rung}: operands {a}, {b} are not octal")
        if kind == "oct_carry":
            return int(int(a[-1]) + int(b[-1]) >= 8)
        return int(int(a[-1]) < int(b[-1]))
    if kind == "position":
        return int(lb.answer_label(rung, item))
    if kind == "crosses_100":
        ans = str(item["answer"]).strip()
        if not re.fullmatch(r"[0-9]+", ans):
            raise ValueError(f"{rung}: answer {ans!r} is not a non-negative "
                             f"integer")
        return int(int(ans) >= 100)
    if kind == "count":
        return int(lb.answer_label(rung, item))
    raise ValueError(kind)


def merge_levels(counts: dict, min_n: int = MIN_STRATUM) -> dict:
    """Ruling i: an ordinal level with fewer than `min_n` items merges
    into its neighbouring level with the fewer items (ties: the lower);
    smallest stratum first; repeat until every stratum holds ≥ min_n
    or one stratum remains. Returns level → stratum id ('a+b')."""
    groups = [[lvl] for lvl in sorted(counts)]

    def size(g):
        return sum(counts[lv] for lv in g)

    while len(groups) > 1:
        small = [i for i, g in enumerate(groups) if size(g) < min_n]
        if not small:
            break
        i = min(small, key=lambda k: (size(groups[k]), k))
        nb = [j for j in (i - 1, i + 1) if 0 <= j < len(groups)]
        j = min(nb, key=lambda k: (size(groups[k]), k))
        lo, hi = sorted((i, j))
        groups[lo:hi + 1] = [groups[lo] + groups[hi]]
    return {lvl: "+".join(str(lv) for lv in g) for g in groups for lvl in g}


def strata_for(cap: dict, rung: str) -> dict:
    kind = COVARIATE_OF[rung]
    levels = [covariate(rung, it) for it in cap["eval_items"]]
    raw = Counter(levels)
    if kind in NOMINAL:
        level_map = {lvl: str(lvl) for lvl in sorted(raw)}
    else:
        level_map = merge_levels(dict(raw))
    strata = [level_map[lv] for lv in levels]
    return {"kind": kind,
            "levels_raw": {int(k): int(v) for k, v in sorted(raw.items())},
            "level_map": {int(k): v for k, v in sorted(level_map.items())},
            "strata": strata,
            "counts": {k: int(v) for k, v in sorted(Counter(strata).items())}}


def build_table(battery: dict) -> dict:
    return {r: strata_for(battery[r], r) for r in bg.PREDICTOR_RUNGS}


def check_strata_pins(table: dict) -> dict:
    out = {}
    for rung in bg.PREDICTOR_RUNGS:
        got = table[rung]["levels_raw"]
        if got != RAW_COUNT_PIN[rung]:
            raise ValueError(f"{rung}: raw level counts {got} against the doc's "
                             f"{RAW_COUNT_PIN[rung]}")
        if any(v < MIN_STRATUM for v in table[rung]["counts"].values()) and \
                len(table[rung]["counts"]) > 1:
            raise ValueError(f"{rung}: a stratum under {MIN_STRATUM} survived "
                             f"the merge: {table[rung]['counts']}")
        out[rung] = "PASS"
    return out


def to_json(table: dict) -> dict:
    return {r: {"kind": t["kind"],
                "levels_raw": {str(k): v for k, v in t["levels_raw"].items()},
                "level_map": {str(k): v for k, v in t["level_map"].items()},
                "strata": list(t["strata"]), "counts": dict(t["counts"])}
            for r, t in table.items()}


def from_json(obj: dict) -> dict:
    return {r: {"kind": t["kind"],
                "levels_raw": {int(k): int(v) for k, v in t["levels_raw"].items()},
                "level_map": {int(k): v for k, v in t["level_map"].items()},
                "strata": list(t["strata"]), "counts": {k: int(v) for k, v in t["counts"].items()}}
            for r, t in obj.items()}


if __name__ == "__main__":
    t = build_table(bg.load_battery(bg.PREDICTOR_RUNGS))
    check_strata_pins(t)
    for r in bg.PREDICTOR_RUNGS:
        print(f"{r:12s} {t[r]['kind']:12s} {t[r]['counts']}")
