"""Exp 2f labels (design §3): one label per rung, readable by every
instrument — from a committed answer (the probe's target and the
scoring key) and from an emitted string (the sampling and argmax
rungs), through 2c's own `number` normalization (first line, first
digit run, commas out). Floors are 2d's rule: c = max(majority class
share over the 500 eval answers, 1/K), one c for all three
instruments.

The committed probe_label fields of 2c/2b's item files are the
known-answer gates for the two label functions that 2c already used
(sub3_mid's middle digit; arith_next's (a+4d) mod 7 == answer mod 7).
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

EXP2F = Path(__file__).resolve().parent
if str(EXP2F.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2F.parent.parent))

from experiments.exp2d import battery_2d as bt  # noqa: E402

RUNGS = ("sub3_mid", "arith_next")
SIZES = bt.PROBE_SIZES                     # ("410m", "1b")
LABEL_KINDS = {"sub3_mid": ("mid_digit",),
               "arith_next": ("last_digit", "mod7")}
PRIMARY = {"sub3_mid": "mid_digit", "arith_next": "last_digit"}   # ruling a
ANSWER_TYPE = "number"                     # both rungs (2d's pin)
N_ITEMS = bt.N_ITEMS
MISS = None                                # an emission with no valid label

_N_CLASSES = {"mid_digit": 10, "last_digit": 10, "mod7": 7}
_DIGITS = re.compile(r"\d+")


def n_classes(kind: str) -> int:
    if kind not in _N_CLASSES:
        raise ValueError(f"unknown label kind {kind!r}")
    return _N_CLASSES[kind]


def _label_of_digits(kind: str, digits: str):
    """The class of a non-negative integer written as digits, or MISS
    when the digits lie outside the label's domain."""
    if kind == "mid_digit":
        if not 1 <= len(digits) <= 3:
            return MISS
        return digits.zfill(3)[1]
    if kind == "last_digit":
        return digits[-1]
    if kind == "mod7":
        return str(int(digits) % 7)
    raise ValueError(f"unknown label kind {kind!r}")


def answer_label(kind: str, answer: str) -> str:
    """The committed answer's class — a hard error on anything outside
    the domain (the answer side is never MISS)."""
    n_classes(kind)
    s = str(answer).strip()
    if not _DIGITS.fullmatch(s):
        raise ValueError(f"{kind}: answer {answer!r} is not a non-negative "
                         f"integer")
    out = _label_of_digits(kind, s)
    if out is MISS:
        raise ValueError(f"{kind}: answer {answer!r} outside the label's "
                         f"domain")
    return out


def normalize(text: str) -> str:
    """2c's `number` normalization, through 2c's harness."""
    return bt.harness_2c().normalize_answer(text, ANSWER_TYPE)


def emission_label(kind: str, text: str):
    """The class of an emitted string, or MISS. Total: every string
    maps to a class or MISS; a negative or non-numeric first run is a
    MISS (a negative next term or difference is never right)."""
    n_classes(kind)
    try:
        s = normalize(text)
    except Exception:              # noqa: BLE001 — the draw side is total
        return MISS
    if not s or not _DIGITS.fullmatch(s):
        return MISS
    return _label_of_digits(kind, s)


def exact_match(answer_type: str, text: str, answer: str) -> bool:
    """2c's verify, through 2c's harness — the gate that must reproduce
    2d's committed exact-match tallies."""
    h = bt.harness_2c()
    return h.normalize_answer(text, answer_type) == \
        h.normalize_answer(str(answer), answer_type)


# -------------------------------------------------------------- floors

def eval_labels(cap: dict, kind: str) -> list:
    return [answer_label(kind, it["answer"]) for it in cap["eval_items"]]


def floor_table(battery: dict) -> dict:
    """(rung, kind) → {floor, majority_share, majority_label, n_classes,
    class_shares, n_items}; c = max(majority share, 1/K)."""
    out = {}
    for rung in RUNGS:
        cap = battery[rung]
        if len(cap["eval_items"]) != N_ITEMS:
            raise ValueError(f"{rung}: {len(cap['eval_items'])} eval items")
        for kind in LABEL_KINDS[rung]:
            y = eval_labels(cap, kind)
            counts = Counter(y)
            top, n_top = counts.most_common(1)[0]
            K = n_classes(kind)
            maj = n_top / len(y)
            out[(rung, kind)] = {
                "floor": float(max(maj, 1.0 / K)),
                "majority_share": float(maj), "majority_label": top,
                "n_classes": K, "n_items": len(y),
                "class_shares": {k: v / len(y) for k, v in sorted(counts.items())},
                "floor_rule": "max(majority share, 1/K)",
            }
    return out


def check_probe_label_gates(battery: dict) -> dict:
    """sub3_mid's committed probe_label == the middle digit, 500/500;
    arith_next's committed probe_label == answer mod 7, 500/500."""
    gates = {}
    for rung, kind in (("sub3_mid", "mid_digit"), ("arith_next", "mod7")):
        cap = battery[rung]
        bad = [i for i, it in enumerate(cap["eval_items"])
               if str(it.get("probe_label")) != answer_label(kind, it["answer"])]
        if bad:
            raise ValueError(
                f"{rung}: the committed probe_label disagrees with the "
                f"{kind} of the answer on {len(bad)} item(s), e.g. {bad[:3]} "
                f"— the label function is not 2c's")
        gates[f"{rung}/{kind}"] = f"PASS ({len(cap['eval_items'])}/{N_ITEMS})"
    return gates
