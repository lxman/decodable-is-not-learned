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

The untrained row is verdict-touching: one fire means the probe reads the
high-dimensional expansion rather than the structure, which is the failure
mode that terminated Experiment 2 at 120 of 120 fits.
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


def _per_size(cells):
    return {s: sum(bool(c["present"]) for c in cells if c["size_bucket"] == s)
            for s in SIZES}


def _tally(cells):
    present = sum(bool(c["present"]) for c in cells)
    return {"present": present, "n": len(cells),
            "per_size": _per_size(cells),
            "cp95": list(clopper_pearson(present, len(cells)))}


def verdict(trained, untrained) -> dict:
    """PASS iff every row meets its preregistered bar. Anything else FAILs and
    is written up as a finding, not tuned away."""
    _check_shape(trained, TRAINED_ROWS, "trained")
    _check_shape(untrained, TRAINED_ROWS, "untrained")

    rows = {s: _tally([c for c in trained if c["system"] == s])
            for s in TRAINED_ROWS}
    rows["untrained"] = _tally(untrained)

    failures = []
    for system in PRESENT_ROWS:
        if rows[system]["present"] < PRESENT_BAR:
            failures.append(
                f"{system}: {rows[system]['present']}/{POOLED_N} S1-present, "
                f"bar is >= {PRESENT_BAR}")
    for system in ABSENT_ROWS:
        if rows[system]["present"] > 0:
            failures.append(
                f"{system}: {rows[system]['present']} S1-present, bar is 0")
    if rows["untrained"]["present"] > 0:
        failures.append(
            f"untrained: {rows['untrained']['present']} S1-present, bar is 0 — "
            f"the probe is reading the expansion, not the structure")

    return {"verdict": "FAIL" if failures else "PASS",
            "rows": rows, "failures": failures}
