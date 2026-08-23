"""Frozen analysis for Experiment 1b (design doc §5).

Verdict = DETECTION, pooled across sizes. Magnitude-of-separation is not
adjudicated on any scale. Exp 1's ledger established why: raw probe accuracy
is incommensurable across systems with different class counts (113 vs 10), so
the predicted direction was unreachable for any instrument; chance-normalizing
does not rescue it, because margins carry system-dependent noise floors; and
the one commensurable continuous scale, -log10(p), is floored by the
permutation count, so a Cohen's d on it partly measures how many permutations
were run. Detection separates. That is what this file scores.

Per-size counts are reported alongside the pooled verdict so a "works at 1M,
fails at 10M" pattern stays visible without flipping the result — the
deliberate cost of pooling, recorded in §5 rather than discovered later.

FLOOR-CORRECTED S1 (amended 2026-08-12; this is 1b's one pre-committed change,
ruled by Michael after the untrained row was measured). S1-present requires,
in addition to Exp 1's criterion:

    accuracy > the accuracy of this cell's OWN untrained twin

paired per (system, size, seed). The reason is measured, not hypothetical: the
untrained twins fire raw S1 in 9 of 10 grokking cells (1M 5/5, 10M 4/5), while
the entity-split lubana probe is silent in 20 of 20. The label-permutation null
permutes labels and refits, so it controls for probe capacity and for label
marginals — but not for information the random expansion already carries about
the label. It answers "does the probe use the labels?", not "did training put
the structure there?" Only the twin answers the second question. Structurally
this is the same error as Exp 2c's chance-floor defect: the criterion's floor
was theoretical chance (1/113 = 0.0088) where the empirical floor is ~0.023.

Strict inequality: a tie with the twin is not evidence training added anything.

CONSEQUENCE — the untrained row is no longer verdict-touching. Under the
corrected criterion an untrained cell cannot exceed its own accuracy, so a
"0/30 untrained" bar would be unfailable, and design §6's standing requirement
is that an operationalization no baseline can fail is not a test. The row is
reported as a diagnostic (rate + Clopper-Pearson) and flagged
`verdict_touching: False`. The two degenerate instruments that §6 routed
through that gate still fail, one row over: a probe that always fires, and a
probe reading reservoir dimensionality, neither exceeds its twin, so both fail
the PRESENT rows instead. Four distinct failure routes survive.
"""

from __future__ import annotations

from experiments.exp1.signatures.stats import clopper_pearson

SIZES = ("1M", "10M")
SEEDS = (100, 101, 102, 103, 104)
TRAINED_ROWS = ("grokking", "lubana_above", "lubana_below")
PRESENT_ROWS = ("grokking", "lubana_above")
ABSENT_ROWS = ("lubana_below",)
PRESENT_BAR = 8
POOLED_N = len(SIZES) * len(SEEDS)


def _check_shape(cells, expected_systems, label):
    for c in cells:
        if c["size_bucket"] not in SIZES:
            raise ValueError(
                f"{label}: size_bucket {c['size_bucket']!r} is outside the 1b "
                f"matrix {SIZES}")
    for system in expected_systems:
        got = [c for c in cells if c["system"] == system]
        if len(got) != POOLED_N:
            raise ValueError(
                f"{label}: incomplete matrix — {system} has {len(got)} cells, "
                f"expected {POOLED_N}")


def _key(cell):
    return (cell["system"], cell["size_bucket"], cell["seed"])


def _index_twins(untrained):
    twins: dict[tuple, dict] = {}
    for c in untrained:
        k = _key(c)
        if k in twins:
            raise ValueError(
                f"duplicate untrained twin for {k} — one cell cannot have two "
                f"floors")
        twins[k] = c
    return twins


def _apply_floor_correction(trained, twins):
    """Attach each cell's twin floor and recompute `present` against it.

    `present_raw` preserves Exp 1's uncorrected verdict so the correction's
    effect is reported rather than silently applied.
    """
    out = []
    for c in trained:
        k = _key(c)
        if k not in twins:
            raise ValueError(
                f"trained cell {k} has no untrained twin — the floor-corrected "
                f"criterion is undefined without one, and must never fall back "
                f"to theoretical chance")
        floor = float(twins[k]["accuracy"])
        out.append({**c,
                    "twin_accuracy": floor,
                    "present_raw": bool(c["present"]),
                    "present": bool(c["present"]) and float(c["accuracy"]) > floor})
    return out


def _per_size(cells, field="present"):
    return {s: sum(bool(c[field]) for c in cells if c["size_bucket"] == s)
            for s in SIZES}


def _tally(cells):
    present = sum(bool(c["present"]) for c in cells)
    return {"present": present, "n": len(cells),
            "per_size": _per_size(cells),
            "cp95": list(clopper_pearson(present, len(cells)))}


def verdict(trained, untrained) -> dict:
    """PASS iff every verdict-touching row meets its preregistered bar.
    Anything else FAILs and is written up as a finding, not tuned away."""
    _check_shape(trained, TRAINED_ROWS, "trained")
    _check_shape(untrained, TRAINED_ROWS, "untrained")

    twins = _index_twins(untrained)
    corrected = _apply_floor_correction(trained, twins)

    rows = {}
    for system in TRAINED_ROWS:
        got = [c for c in corrected if c["system"] == system]
        row = _tally(got)
        row["present_raw"] = sum(c["present_raw"] for c in got)
        row["per_size_raw"] = _per_size(got, "present_raw")
        rows[system] = row

    u_present = sum(bool(c["present"]) for c in untrained)
    rows["untrained"] = {
        "present": u_present, "n": len(untrained),
        "per_size": _per_size(untrained),
        "cp95": list(clopper_pearson(u_present, len(untrained))),
        # Diagnostic only: see the module docstring. The floor correction
        # discounts this cell by cell, so gating on it as well would both
        # double-count and make the bar unfailable.
        "verdict_touching": False,
    }

    failures = []
    for system in PRESENT_ROWS:
        if rows[system]["present"] < PRESENT_BAR:
            failures.append(
                f"{system}: {rows[system]['present']}/{POOLED_N} S1-present "
                f"(floor-corrected; {rows[system]['present_raw']}/{POOLED_N} "
                f"raw), bar is >= {PRESENT_BAR}")
    for system in ABSENT_ROWS:
        if rows[system]["present"] > 0:
            failures.append(
                f"{system}: {rows[system]['present']} S1-present "
                f"(floor-corrected), bar is 0")

    return {"verdict": "FAIL" if failures else "PASS",
            "rows": rows, "failures": failures}
