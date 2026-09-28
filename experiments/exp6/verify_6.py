# experiments/exp6/verify_6.py
"""Exp 6 verify criterion (design §3.2).

`number` and `word` are 2c's `normalize_answer` VERBATIM (imported, not
copied), so the anchor rungs score byte-for-byte as committed. Three
additive types: `span` and `sequence` compare the whole first line;
`ipa` compares the first whitespace token without case folding.

Totality (methods paper §6, lesson 5): the DRAW side never raises — any
string returns a bool. The ANSWER side stays a hard error: an answer
that normalizes to the empty string is a defect in the item file.
"""
from __future__ import annotations

import sys
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parent.parent

ANSWER_TYPES_6 = ("number", "word", "span", "ipa", "sequence")
# one budget per answer type, both instruments (greedy and sampling);
# number/word are 2d's `max_new_tokens` (8 / 12), the anchors' committed
# budgets.
MAX_NEW_TOKENS_6 = {"number": 8, "word": 12, "span": 12, "ipa": 24,
                    "sequence": 16}
_STRIP = ".!?\"' "


_HARNESS = []


def harness_2c():
    """2c's harness, provenance-asserted (exp3c's pattern) — ONCE. The
    module is resolved and checked on the first call and the same object
    is returned after it: the criterion runs on millions of draws, and
    resolving two paths per draw cost two hundred times the comparison."""
    if _HARNESS:
        return _HARNESS[0]
    for p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    import harness
    got = Path(harness.__file__).resolve()
    if (EXPERIMENTS / "exp2c").resolve() not in got.parents:
        raise ImportError(f"`harness` resolved to {got}, not exp2c's")
    _HARNESS.append(harness)
    return harness


def _first_line(text: str) -> str:
    lines = str(text).strip().split("\n")
    return lines[0].strip() if lines else ""


def _whole_line(text: str) -> str:
    s = _first_line(text).lower().strip(_STRIP)
    return " ".join(s.split())


def _ipa_token(text: str) -> str:
    s = _first_line(text).strip(_STRIP)
    parts = s.split()
    return parts[0] if parts else ""


def normalize_6(text: str, answer_type: str) -> str:
    if answer_type not in ANSWER_TYPES_6:
        raise ValueError(f"unknown answer type {answer_type!r}")
    if answer_type in ("number", "word"):
        return harness_2c().normalize_answer(str(text), answer_type)
    if answer_type == "ipa":
        return _ipa_token(text)
    return _whole_line(text)


def normalize_answer_side(answer: str, answer_type: str) -> str:
    try:
        want = normalize_6(answer, answer_type)
    except IndexError:          # 2c's `word` path; an answer that trips it is empty
        want = ""
    if not want:
        raise ValueError(f"answer {answer!r} normalizes to the empty string "
                         f"under {answer_type!r}")
    return want


def verify_6(pred, answer, answer_type: str) -> bool:
    """Exact match after normalization. Draw side total."""
    want = normalize_answer_side(str(answer), answer_type)
    try:
        got = normalize_6(str(pred), answer_type)
    except IndexError:          # 2c's `word` path on a whitespace-only line
        return False
    return got == want


def exact_under_criterion(answer: str, answer_type: str) -> bool:
    """True iff the criterion reads the WHOLE answer (2d F-3): the
    normalized answer equals the answer's own whole-line form."""
    whole = " ".join(str(answer).strip().split())
    if answer_type != "ipa":
        whole = whole.lower()
    return normalize_answer_side(answer, answer_type) == whole.strip(_STRIP)
