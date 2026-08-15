"""Frozen analysis for Experiment 3b (design doc §5, §6).

The same-weights test of the reversal dissociation: the probe reads the
answer's first character off the 410m and 1b residual streams at margins
.63/.77 (rev_string7) and .57/.67 (reverse_string). This module adjudicates
whether those same weights, on the same prompt, can EMIT that character —
first non-whitespace character of the greedy continuation against the
probe's own label, in the same 26-way label space.

WHAT IS ADJUDICATED. One-sided exact binomial tests of first-character
accuracy against each rung's committed chance floor, Bonferroni-corrected
across the EIGHT probe-size trained cells (4 rungs × 410m/1b). The verdict
is decided entirely at the probe sizes; the eval-size cells (2.8b/6.9b/12b)
are descriptives and no branch below reads them except gate 3's byte
comparison against 3a's stored continuations.

LINEAGE. Floors, scoring and the significance test are Exp 3a's, ported
verbatim (the non-alphabetic first_char fix and the copy_is_the_task floor
exclusion included). What replaces 3a's m4 replication gate — the input
that had no value on its own battery and closed that experiment — is a pair
of gates whose referents are all committed with defined values (design §4):
gate 2 checks full-string accuracy against the 2b/2c inclusion records by
Clopper–Pearson interval overlap, and gate 3 checks the 24 eval-size cells
byte-for-byte against 3a's stored continuations. No branch of this module
reads results/m4/ anywhere.

NO OUTCOME HERE IS A PASS OF A HYPOTHESIS THE AUTHOR HOLDS. UNITS_ARTIFACT
requires correcting a claim already in print; DISSOCIATION strengthens it
to same-weights. The tree is frozen so that neither can be softened after
the fact.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scipy.stats import beta, binom

PROBE_SIZES = ("410m", "1b")          # primary — where the probes were fit
EVAL_SIZES = ("2.8b", "6.9b", "12b")  # descriptive only
SIZES = PROBE_SIZES + EVAL_SIZES
MODES = ("trained", "untrained")
REVERSAL_RUNGS = ("rev_string7", "reverse_string")
POSITIVE_CONTROL = "ctrl_copy"
MATCHED_CONTROL = "clock24_d999"
RUNGS = REVERSAL_RUNGS + (POSITIVE_CONTROL, MATCHED_CONTROL)
ALPHA = 0.01
N_PROBE_TESTS = 8      # design §6: Bonferroni across the probe-size trained cells
BYTE_TOLERANCE = 2     # design §6 gate 3: >2 of 500 differing continuations fires

EXP3B = Path(__file__).resolve().parent
EXPERIMENTS = EXP3B.parent

# 3a's committed floors, pinned by content hash (design §5). The pin is on the
# FILE; load_floors additionally recomputes every floor from the committed
# items and asserts equality, so neither the file nor the items can drift
# silently against the other.
FLOORS_PATH = EXPERIMENTS / "exp3a" / "chance_floors.json"
FLOORS_SHA256 = "f299fa08314b138c5f741739c7de35e22c0b41e3c6be838505f6c6a22c1a5318"

INCLUSION_2C = EXPERIMENTS / "exp2c" / "results" / "inclusion"
INCLUSION_2B = EXPERIMENTS / "exp2b" / "results" / "inclusion"
BYTE_REFERENT_ROOT = EXPERIMENTS / "exp3a" / "results"
ITEMS_2C = EXPERIMENTS / "exp2c" / "battery" / "items"
ITEMS_2B = EXPERIMENTS / "exp2b" / "battery" / "items"
MARGINS_PATH = EXP3B / "probe_margins.json"

# reverse_string is the 2b survivor: its items and inclusion records live in
# the 2b tree; everything else is 2c's (design §4).
RUNGS_2B = ("reverse_string",)


# ----------------------------------------------------------------- floors
# Exp 3a verbatim (chance_floors); the recompute-assert wrapper is new.

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


def load_battery_items(rung: str, *, items_2c=None, items_2b=None) -> list:
    """Committed eval items for a rung, from the tree that owns it."""
    root = (items_2b if rung in RUNGS_2B else items_2c)
    root = Path(root) if root is not None else (
        ITEMS_2B if rung in RUNGS_2B else ITEMS_2C)
    p = root / f"{rung}.json"
    if not p.is_file():
        raise FileNotFoundError(f"no committed item file for {rung!r} at {p}")
    return json.loads(p.read_text())["eval_items"]


def load_floors(floors_path=FLOORS_PATH, *, expected_sha=FLOORS_SHA256,
                items_loader=load_battery_items) -> dict:
    """3a's committed floors: sha-pinned, then recomputed and asserted.

    Two failure modes, both fatal by design: the committed file differing
    from the pinned hash (the file moved under us), and the recompute from
    the committed items differing from the file (the items moved under the
    file). Either way the floors this experiment was designed against no
    longer exist, and nothing downstream is interpretable.
    """
    raw = Path(floors_path).read_bytes()
    got_sha = hashlib.sha256(raw).hexdigest()
    if got_sha != expected_sha:
        raise ValueError(
            f"floors file {floors_path} has sha256 {got_sha}, expected "
            f"{expected_sha} — the committed floors changed after the pin")
    committed = json.loads(raw)
    for rung in RUNGS:
        recomputed = json.loads(json.dumps(chance_floors(items_loader(rung))))
        if recomputed != committed.get(rung):
            raise ValueError(
                f"floors recompute mismatch for {rung!r}: items no longer "
                f"produce the committed floors — {recomputed} vs "
                f"{committed.get(rung)}")
    return committed


# ---------------------------------------------------------------- scoring
# Exp 3a verbatim; the first docstring line there still said "alphabetic"
# after the fix, corrected here to say what the code does.

def first_char(continuation) -> str | None:
    """First non-whitespace character of the continuation, case-folded.

    An empty or whitespace-only continuation returns None and is scored
    INCORRECT rather than dropped: failing to emit anything is the behaviour
    under measurement, not missing data.

    Any non-whitespace character counts. An earlier version required
    `isalpha()`, which silently zeroed the matched control: clock24_d999's
    probe label is a DIGIT, so every correct answer scored False and the
    control would have read exactly zero at every cell — a dramatic-looking
    result produced entirely by the scorer. Found by 3a's mutation testing.
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


def clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Exact binomial CI (2c harness formula, reimplemented so the frozen
    analysis imports nothing from a sys.path-dependent tree). Every
    zero-looking rate ships as a CP bound (program rule since 1c)."""
    alpha = 1.0 - level
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def cp_overlap(k1: int, n1: int, k2: int, n2: int) -> bool:
    """Do the 95% CP intervals of two counts overlap (closed intervals —
    touching counts as compatible)? Gate 2's whole test: against a 0/500
    referent this tolerates up to 8/500 observed before firing (design §6)."""
    lo1, hi1 = clopper_pearson(k1, n1)
    lo2, hi2 = clopper_pearson(k2, n2)
    return bool(lo1 <= hi2 and lo2 <= hi1)


# ---------------------------------------------------- loading and assembly
#
# Frozen WITH the analysis, per design §11. Every input verdict() takes is
# produced by a function in this file, and the freeze executes this whole
# path — loader included — against synthetic full-shape batteries reaching
# every terminal branch (3a's lesson: a producer can exist and return None;
# the check is now on values, not producers).

def cell_key(c: dict) -> tuple[str, str, str]:
    return (c["rung"], c["size"], c["mode"])


def load_cells(root) -> list[dict]:
    """Read every cell record under root/results/{size}_{mode}/{rung}.json.

    Only the canonical 10 subdirectories are read, so verdict artifacts
    written at results/ top level can never be re-ingested as data. A json
    inside a canonical subdirectory that is not a cell record, or one whose
    contents disagree with its path, is an error — not skipped: a battery
    with junk in it is not a battery with less data, it is a broken battery.
    """
    base = Path(root) / "results"
    out = []
    for size in SIZES:
        for mode in MODES:
            d = base / f"{size}_{mode}"
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.json")):
                rec = json.loads(p.read_text())
                if "continuations" not in rec or "probe_labels" not in rec:
                    raise ValueError(
                        f"{p} is inside a cell directory but is not a cell "
                        f"record — refusing to guess what it is")
                if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
                        (p.stem, size, mode):
                    raise ValueError(
                        f"{p} contents ({rec.get('rung')}/{rec.get('size')}/"
                        f"{rec.get('mode')}) disagree with its path")
                if rec.get("n_items") != len(rec["continuations"]):
                    raise ValueError(
                        f"{p}: n_items {rec.get('n_items')} but "
                        f"{len(rec['continuations'])} continuations stored")
                conts = rec["continuations"]
                mean_len = (sum(len(str(c)) for c in conts) / len(conts)
                            if conts else 0.0)
                out.append({**rec,
                            **score_cell(conts, rec["probe_labels"]),
                            "mean_continuation_len": mean_len})
    return out


def load_inclusion_referents(inclusion_2c=INCLUSION_2C,
                             inclusion_2b=INCLUSION_2B) -> dict:
    """Gate 2's referents: the 16 probe-size inclusion records (design §4).

    reverse_string's live in the 2b tree (its decode path verified identical
    to 2c's element by element at design time — doc §4, open item 5); the
    other three rungs' in 2c's. Every record must exist with an integral
    `correct` and n > 0 — a missing or valueless referent is 3a's death, and
    it is refused here rather than discovered mid-verdict.
    """
    out = {}
    for rung in RUNGS:
        root = Path(inclusion_2b if rung in RUNGS_2B else inclusion_2c)
        for size in PROBE_SIZES:
            for mode in MODES:
                p = root / f"{size}_{mode}" / f"{rung}.json"
                if not p.is_file():
                    raise FileNotFoundError(
                        f"no inclusion referent for {rung}/{size}/{mode} at "
                        f"{p} — gate 2 has no defined value there")
                rec = json.loads(p.read_text())
                correct, n = rec.get("correct"), rec.get("n")
                if not isinstance(correct, int) or not isinstance(n, int) \
                        or n <= 0:
                    raise ValueError(
                        f"inclusion referent {p} has no usable value: "
                        f"correct={correct!r} n={n!r}")
                out[(rung, size, mode)] = {"correct": correct, "n": n}
    return out


def load_byte_referents(root=BYTE_REFERENT_ROOT) -> dict:
    """Gate 3's referents: 3a's stored continuations for the 24 eval-size
    cells (design §4 — 3a's collected cells are the reproduction referent,
    not the data; Michael's ruling, 3a retrospective §4)."""
    out = {}
    base = Path(root)
    for rung in RUNGS:
        for size in EVAL_SIZES:
            for mode in MODES:
                p = base / f"{size}_{mode}" / f"{rung}.json"
                if not p.is_file():
                    raise FileNotFoundError(
                        f"no byte referent for {rung}/{size}/{mode} at {p}")
                conts = json.loads(p.read_text()).get("continuations")
                if not isinstance(conts, list) or not conts:
                    raise ValueError(f"byte referent {p} stores no "
                                     f"continuations")
                out[(rung, size, mode)] = [str(c) for c in conts]
    return out


def load_probe_margins(path=MARGINS_PATH) -> dict:
    """Per-size m3 probe margins, recomputed from the committed seed records
    and committed in this tree. Quoted per size, never pooled: the pooled
    .699/.624 of the paper's §8 was part of the original confound and
    appears nowhere in this experiment (design §3)."""
    d = json.loads(Path(path).read_text())
    out = {}
    for rung in REVERSAL_RUNGS:
        out[rung] = {}
        for size in PROBE_SIZES:
            v = d[rung][size]["mean"]
            if not 0.0 < float(v) < 1.0:
                raise ValueError(f"probe margin {rung}/{size} = {v!r} is not "
                                 f"a margin")
            out[rung][size] = float(v)
    return out


# ----------------------------------------------------------- verdict tree

def _shape_check(cells, floors, inclusion, byte_referents) -> dict:
    """The battery must be exactly the preregistered 40 cells with every
    referent present. Anything else is a malformed battery and a hard error,
    not a verdict: INSUFFICIENT_DATA is a statement about the world, and a
    half-copied directory is not the world."""
    by_key: dict[tuple, dict] = {}
    for c in cells:
        k = cell_key(c)
        if k in by_key:
            raise ValueError(f"duplicate cell {k}")
        by_key[k] = c
    want = {(r, s, m) for r in RUNGS for s in SIZES for m in MODES}
    if set(by_key) != want:
        missing = sorted(want - set(by_key))
        extra = sorted(set(by_key) - want)
        raise ValueError(f"battery is not the preregistered 40 cells: "
                         f"missing {missing}, extra {extra}")
    for k, c in by_key.items():
        if not isinstance(c.get("full_string_correct"), int):
            raise ValueError(f"cell {k} has no integral full_string_correct")
    for r in RUNGS:
        if r not in floors or "primary" not in floors[r]:
            raise ValueError(f"no committed floor for rung {r!r}")
    want_inc = {(r, s, m) for r in RUNGS for s in PROBE_SIZES for m in MODES}
    if set(inclusion) != want_inc:
        raise ValueError(f"inclusion referents are not the 16 probe-size "
                         f"cells: {sorted(set(inclusion) ^ want_inc)}")
    want_byte = {(r, s, m) for r in RUNGS for s in EVAL_SIZES for m in MODES}
    if set(byte_referents) != want_byte:
        raise ValueError(f"byte referents are not the 24 eval-size cells: "
                         f"{sorted(set(byte_referents) ^ want_byte)}")
    for k in want_byte:
        if len(byte_referents[k]) != by_key[k]["n"]:
            raise ValueError(
                f"byte referent {k} has {len(byte_referents[k])} "
                f"continuations against the cell's {by_key[k]['n']}")
    return by_key


def verdict(cells, floors, inclusion, byte_referents, margins, *,
            alpha: float = ALPHA) -> dict:
    """Design §6, adjudicated in precedence order.

    Significance is tested for the 16 probe-size cells only — §6: "eval-size
    cells take no significance tests: they are descriptives, and no branch
    below reads them except gate 3's byte comparison." Gate 4's "any
    untrained cell" therefore quantifies over the 8 probe-size untrained
    cells; an eval-size untrained fire is visible in the descriptives but
    marks nothing (scope stated in PROGRESS.md for the freeze read).
    """
    by_key = _shape_check(cells, floors, inclusion, byte_referents)

    n_tests = sum(1 for (r, s, m) in by_key
                  if s in PROBE_SIZES and m == "trained")
    if n_tests != N_PROBE_TESTS:
        raise ValueError(f"{n_tests} probe-size trained cells against the "
                         f"preregistered {N_PROBE_TESTS}")

    sig = {}
    for (r, s, m), c in by_key.items():
        if s not in PROBE_SIZES:
            continue
        sig[(r, s, m)] = significant(
            correct=c["correct"], n=c["n"], floor=floors[r]["primary"],
            n_tests=n_tests if m == "trained" else 1, alpha=alpha)

    contaminated = sorted({r for (r, s, m), v in sig.items()
                           if v and m == "untrained"})

    report = []
    for k in sorted(by_key):
        c = by_key[k]
        fl = floors[c["rung"]]["primary"]
        report.append({
            "rung": c["rung"], "size": c["size"], "mode": c["mode"],
            "n": c["n"], "correct": c["correct"], "acc": c["acc"],
            "cp95": list(clopper_pearson(c["correct"], c["n"])),
            "floor": fl, "m_b": (c["acc"] - fl) / (1.0 - fl),
            "full_string_correct": c["full_string_correct"],
            "full_string_acc": c["full_string_correct"] / c["n"],
            "mean_continuation_len": c["mean_continuation_len"],
            "significant": sig.get(k),   # None for eval-size cells, by design
        })

    byte_diffs = {}
    for k in sorted(byte_referents):
        diffs = [{"item": i, "got": g, "referent": w}
                 for i, (g, w) in enumerate(zip(by_key[k]["continuations"],
                                                byte_referents[k]))
                 if str(g) != str(w)]
        if diffs:
            byte_diffs["/".join(k)] = diffs

    out = {"n_tests": n_tests, "alpha": alpha, "contaminated": contaminated,
           "significant_cells": sorted(f"{r}/{s}" for (r, s, m), v
                                       in sig.items()
                                       if v and m == "trained"),
           "floors": {r: floors[r]["primary"] for r in RUNGS},
           "probe_margins": margins,
           "cells": report,
           # every differing item, disclosed verbatim whether or not the
           # gate fires (design §6 gate 3)
           "byte_diffs": byte_diffs}

    # 1. positive control: emission must be visible where the committed
    # record says it exists (.960/.980 full-string at the probe sizes)
    ctrl = [sig[(POSITIVE_CONTROL, s, "trained")] for s in PROBE_SIZES]
    if not all(ctrl):
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": f"{POSITIVE_CONTROL} first-character accuracy is "
                          f"not above floor at every probe size "
                          f"(410m/1b: {ctrl}) — the instrument does not "
                          f"detect emission on a capability committed at "
                          f".960/.980 full-string on these same weights"}

    # 2. replication against the inclusion referents, CP-interval overlap
    bad = []
    for k in sorted(inclusion):
        c, ref = by_key[k], inclusion[k]
        if not cp_overlap(c["full_string_correct"], c["n"],
                          ref["correct"], ref["n"]):
            bad.append(f"{'/'.join(k)}: {c['full_string_correct']}/{c['n']} "
                       f"against committed {ref['correct']}/{ref['n']}")
    if bad:
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": "replication failed — full-string accuracy "
                          "incompatible with the committed inclusion "
                          "referent (95% CP non-overlap) at: "
                          + "; ".join(bad)}

    # 3. byte identity against 3a's continuations on the 24 overlap cells
    over = {k: len(v) for k, v in byte_diffs.items()
            if len(v) > BYTE_TOLERANCE}
    if over:
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": "byte gate failed — greedy decoding is "
                          "deterministic on this stack, and more than "
                          f"{BYTE_TOLERANCE} of 500 continuations differ "
                          f"from 3a's stored referent at: "
                          + "; ".join(f"{k} ({n} items)"
                                      for k, n in sorted(over.items()))}

    # 4. untrained fires were computed above; contaminated rungs are
    # reported in `out` and excluded from step 5's quantifiers. 5. the claim:
    eligible = [(r, s) for r in REVERSAL_RUNGS if r not in contaminated
                for s in PROBE_SIZES]
    if not eligible:
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": "both reversal rungs' untrained twins fired — "
                          "contamination emptied the claim, and a universal "
                          "quantifier over zero cells decides nothing"}
    fired = [sig[(r, s, "trained")] for r, s in eligible]
    if all(fired):
        return {**out, "verdict": "UNITS_ARTIFACT",
                "reason": "reversal first-character accuracy is above floor "
                          "in all "
                          f"{len(eligible)} adjudicated probe-size cells: "
                          "the famous zero was a metric cliff — the gap in "
                          "the committed record is between reading one "
                          "character and emitting seven"}
    if not any(fired):
        pm = "; ".join(
            f"{r} {'/'.join(f'{margins[r][s]:.4f}@{s}' for s in PROBE_SIZES)}"
            for r in REVERSAL_RUNGS if r not in contaminated)
        return {**out, "verdict": "DISSOCIATION",
                "reason": "reversal first-character accuracy is at floor in "
                          f"all {len(eligible)} adjudicated probe-size "
                          f"cells, against same-weights probe margins of "
                          f"{pm} on the same prompt and label space"}
    named = sorted(f"{r}/{s}" for (r, s), v in zip(eligible, fired) if v)
    return {**out, "verdict": "PARTIAL",
            "reason": "reversal clears its floor in some adjudicated "
                      f"probe-size cells and not others — above floor at: "
                      + ", ".join(named)}


# ----------------------------------------------------------------- driver

def run(root=EXP3B) -> dict:
    """Load everything through the frozen producers and adjudicate."""
    return verdict(load_cells(root), load_floors(),
                   load_inclusion_referents(), load_byte_referents(),
                   load_probe_margins())


if __name__ == "__main__":
    v = run()
    print(json.dumps({k: v[k] for k in ("verdict", "reason", "n_tests",
                                        "contaminated", "significant_cells")},
                     indent=1))
