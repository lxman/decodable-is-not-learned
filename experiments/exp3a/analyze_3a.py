"""Frozen analysis for Experiment 3a (design doc §4, §5).

Adjudicates whether the reversal "decodable but not generable" gap is a
dissociation or a units mismatch, by scoring the FIRST CHARACTER of the
model's continuation against the probe's own label — the same prompt, the
same 26-way label space, the same normalization on both sides.

WHAT IS ADJUDICATED. A one-sided binomial test of first-character accuracy
against the rung's committed chance floor, Bonferroni-corrected across the
twelve trained cells. Nothing else touches the verdict.

THE FLOOR IS THE MAX OF THREE, computed from the committed items alone and
frozen before any model is queried: uniform (1/26), marginal (always guess
the modal first character), and copy-first (echo the input instead of
reversing it). Taking the maximum is what stops a degenerate strategy from
passing, and it is the §8 lesson of the methods paper applied in advance
rather than discovered afterwards: an untrained-weights floor answers "is
this signal in the weights", not "is this behaviour competent", and on a
generation task it sits near zero for reasons having nothing to do with
the capability.

NO OUTCOME HERE IS A PASS OF A HYPOTHESIS THE AUTHOR HOLDS. UNITS_ARTIFACT
requires correcting a claim already in print; DISSOCIATION strengthens it.
The tree is frozen so that neither can be softened after the fact.
"""

from __future__ import annotations

import json
from pathlib import Path

from scipy.stats import binom

SIZES = ("2.8b", "6.9b", "12b")
REVERSAL_RUNGS = ("rev_string7", "reverse_string")
POSITIVE_CONTROL = "ctrl_copy"
MATCHED_CONTROL = "clock24_d999"
RUNGS = REVERSAL_RUNGS + (POSITIVE_CONTROL, MATCHED_CONTROL)
ALPHA = 0.01


# ----------------------------------------------------------------- floors

def chance_floors(eval_items) -> dict:
    """The three floors and their maximum, from the items alone.

    `copy_first` is the rate at which the input's first character already
    equals the answer's first character — what a model that echoes rather
    than reverses would score. For random strings it is ~1/26, but it is
    measured because a systematic generator could make it larger.
    """
    n = len(eval_items)
    if not n:
        raise ValueError("no eval items to compute a floor from")
    firsts = [str(it["answer"])[0].casefold() for it in eval_items]
    counts: dict[str, int] = {}
    for c in firsts:
        counts[c] = counts.get(c, 0) + 1
    marginal = max(counts.values()) / n

    copy_first, copy_whole = 0, 0
    for it, f in zip(eval_items, firsts):
        q = str(it["question"])
        # the quoted input string in "Spell the string 'xxxxxxx' backwards."
        if "'" in q:
            inp = q.split("'")[1]
            if inp and inp[0].casefold() == f:
                copy_first += 1
            if inp.casefold() == str(it["answer"]).casefold():
                copy_whole += 1
    copy_first /= n
    copy_whole /= n

    # If the answer IS the input on most items, the task is copying, and
    # copying is then the capability rather than a way of faking it. Including
    # copy_first there would set the floor at 1.0 and make the rung
    # unbeatable — which would fire the positive-control gate unconditionally
    # and let this experiment return only INSUFFICIENT_DATA. Derived from the
    # items rather than declared per rung: a hand-set flag deciding a gate is
    # exactly the kind of thing that gets tuned once an outcome is visible.
    copy_is_the_task = copy_whole > 0.5

    vals = {"uniform": 1.0 / 26, "marginal": marginal, "copy_first": copy_first}
    eligible = {k: v for k, v in vals.items()
                if not (k == "copy_first" and copy_is_the_task)}
    src = max(eligible, key=lambda k: eligible[k])
    return {**vals, "copy_whole": copy_whole,
            "copy_is_the_task": copy_is_the_task,
            "primary": vals[src], "primary_source": src, "n_items": n}


# ---------------------------------------------------------------- scoring

def first_char(continuation) -> str | None:
    """First alphabetic character of the continuation, case-folded.

    An empty or whitespace-only continuation returns None and is scored
    INCORRECT rather than dropped: failing to emit anything is the behaviour
    under measurement, not missing data.

    Any non-whitespace character counts. An earlier version required
    `isalpha()`, which silently zeroed the matched control: clock24_d999's
    probe label is a DIGIT, so every correct answer scored False and the
    control would have read exactly zero at every cell — a dramatic-looking
    result produced entirely by the scorer. Found by mutation testing.
    """
    s = str(continuation).lstrip()
    if not s:
        return None
    return s[0].casefold()


def score_first_char(continuation, probe_label) -> bool:
    got = first_char(continuation)
    return bool(got is not None and got == str(probe_label)[0].casefold())


def score_cell(continuations, probe_labels) -> dict:
    if len(continuations) != len(probe_labels):
        raise ValueError(
            f"{len(continuations)} continuations against {len(probe_labels)} "
            f"labels — an item cannot be dropped from this metric")
    correct = sum(score_first_char(c, l)
                  for c, l in zip(continuations, probe_labels))
    return {"n": len(probe_labels), "correct": int(correct),
            "acc": correct / len(probe_labels)}


# ------------------------------------------------------------ significance

def significant(*, correct: int, n: int, floor: float, n_tests: int,
                alpha: float = ALPHA) -> bool:
    """One-sided binomial: is `correct` above `floor`, Bonferroni-corrected."""
    p = float(binom.sf(correct - 1, n, floor))
    return bool(p * n_tests < alpha)


def n_trained_cells(cells) -> int:
    return sum(1 for c in cells if c["mode"] == "trained")


# ---------------------------------------------------- loading and assembly
#
# Frozen WITH the analysis, per design §9. 1b froze a verdict() with no record
# loader; 1c then shipped a verdict() taking an input it had no frozen way to
# compute. Both gaps are closed here: everything verdict() consumes is either
# produced by a function in this file or pinned by a fixture.

def load_cells(root) -> list[dict]:
    base = Path(root) / "results"
    if not base.is_dir():
        return []
    out = []
    for p in sorted(base.rglob("*.json")):
        d = json.loads(p.read_text())
        if "continuations" in d:
            d = {**d, **score_cell(d["continuations"], d["probe_labels"])}
        out.append(d)
    return out


# ----------------------------------------------------------- verdict tree

def verdict(cells, floors, *, alpha: float = ALPHA) -> dict:
    """Design §5, adjudicated in precedence order."""
    n_tests = n_trained_cells(cells)
    sig = {}
    for c in cells:
        sig[(c["rung"], c["size"], c["mode"])] = significant(
            correct=c["correct"], n=c["n"],
            floor=floors[c["rung"]]["primary"],
            n_tests=n_tests if c["mode"] == "trained" else 1, alpha=alpha)

    contaminated = sorted(k[0] for k, v in sig.items()
                          if v and k[2] == "untrained")
    out = {"n_tests": n_tests, "contaminated": contaminated,
           "significant_cells": sorted(f"{k[0]}/{k[1]}" for k, v in sig.items()
                                       if v and k[2] == "trained"),
           "floors": {r: floors[r]["primary"] for r in floors}}

    ctrl = [sig[(POSITIVE_CONTROL, s, "trained")] for s in SIZES]
    if sum(ctrl) < 2:
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": f"{POSITIVE_CONTROL} first-character accuracy is not "
                          f"above floor at 2 of 3 sizes — the instrument does "
                          f"not detect emission on a capability this battery "
                          f"scored .96 argmax"}

    for c in cells:
        if c["mode"] != "trained":
            continue
        if abs(float(c["full_string_acc"]) - float(c["committed_2c_acc"])) > 0.02:
            return {**out, "verdict": "INSUFFICIENT_DATA",
                    "reason": f"replication check failed: {c['rung']}/{c['size']} "
                              f"full-string accuracy {c['full_string_acc']:.4f} "
                              f"against 2c's committed {c['committed_2c_acc']:.4f} "
                              f"— the harness has drifted"}

    rev = {r: [sig[(r, s, "trained")] for s in SIZES] for r in REVERSAL_RUNGS}
    if all(all(v) for v in rev.values()):
        return {**out, "verdict": "UNITS_ARTIFACT",
                "reason": "reversal first-character accuracy is above floor at "
                          "every size: the gap in the committed record is "
                          "between reading one character and emitting seven"}
    if not any(any(v) for v in rev.values()):
        return {**out, "verdict": "DISSOCIATION",
                "reason": "reversal first-character accuracy is at floor at "
                          "every size, against committed probe margins of "
                          ".699 and .624 on the same prompt and label space"}
    return {**out, "verdict": "PARTIAL",
            "reason": "reversal clears its floor at some sizes and not others"}
