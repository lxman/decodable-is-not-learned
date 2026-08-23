# POST-HOC retrospective: alternative bars against the M6 dataset

**Status: NOT part of the frozen analysis. Computed 2026-07-14, AFTER the frozen
verdict (`analysis_verdict.txt`, VERDICT: FAIL). These bars were chosen with the
data in view; they cannot modify Exp 1's verdict and are recorded solely as (a)
design input for the Exp 3/4 design docs and (b) expository material for the
write-up.** Approved by Michael 2026-07-14 for use as a write-up figure.

## A — the frozen S1 criterion, re-unitized (the figure)

Same structure as frozen §4 (disjoint CIs, predicted direction, Cohen's d ≥ 2);
the only change is the unit: −log₁₀(p) against each run's own permutation null,
instead of raw probe accuracy.

| size | frozen (raw accuracy) d | null-relative d |
|---|---|---|
| 1M | −1.54 | **+12.94** |
| 10M | −1.29 | **+4.21** |
| 100M | +0.40 | **+5.76** |

Same 30 records, same phenomenon; the sign flip and order-of-magnitude jump is
the units misspecification (ledgered 2026-07-08) made visible.

## B — detection rates (S1 fires at p < .01)

grokking 5/5, 4/5, 4/5 (1M/10M/100M; both misses p = .026/.014);
lubana_above 15/15; lubana_below 0/15. A "≥4/5 present-rows AND 0/5 absent-row"
bar passes at every size.

## C — S2 as a one-sided constraint

Below-row elicitability 0/15 (passes at every size). No honest magnitude bar on
the present rows passes at 100M (rates .00004–.0415 across seeds): scale-fragile
elicitability is a finding, not a bar defect — see the Exp 3 forward-note in
`experiments.md`.

## D — S3 with interval coverage dropped (beats-baseline, majority per size)

grokking 5/5, 5/5, 3/5; below ≤1/5 per size. Passes, narrowly at 100M.

## One-line summary

A detection-framed preregistration (null-relative units, fire rates, one-sided
S2) passes this dataset at every size; the magnitude-framed one actually frozen
could not pass in any world. Exp 2 was frozen detection-framed before this
retrospective existed.
