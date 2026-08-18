# Exp 3c retrospective — the projection graded

Projection ledgered at `86328c2` (before the frozen analysis; written
with the runner's convenience tallies visible, exp3's precedent).
Verdict: **DEEPENS**.

## Verdict level: HIT

Projected DEEPENS on (fired_again ∧ any_wall); the frozen tree
returned exactly that, with the projected pooled numbers exact:
10/512,000 = 1.953e-5 at the fired cell, 3/512,000 = 5.859e-6 at the
fallen wall, rev_string7 zeros ≤ 5.851e-6. Gates all clean as
projected, including ZERO leak-voids and stored-vs-recompute
agreement at all four cells.

## Finer predictions

1. **"Fires concentrate in len-4; len-6 stays zero; len-5 carries
   0–2" — PARTIAL, with the named miss FIRING.** Len-4 concentration
   held (10 of 12 new fires); len-5 carried exactly 1. But len-6 did
   NOT stay zero: item 200 'rxxxxd' fired once at 1b. The projection
   itself named "any length-6 fire (strains the geometric story)" as
   the miss that would matter — it happened. Reading: the geometric
   anchor treats per-position costs as homogeneous; 'rxxxxd' has a
   4-run of a single letter, and the joint path over a repeated
   character is far cheaper than the length-6 generic cost. The
   MECHANISM (joint autoregressive cost sets the rate) survives —
   arguably strengthened, since the one len-6 fire is exactly the
   len-6 answer with the cheapest internal structure — but the
   scalar length-anchor extrapolation is too coarse an instrument
   for structured answers. Successor note: any rate model should
   condition on answer entropy/compressibility, not raw length.
2. **"Thin Poisson across the 12 new seeds" — HIT.** 1b fires on 5
   distinct seeds, max 3 on one seed (seeds 8 and 13); 410m on 3
   distinct seeds, 1 each. No stream carries the result.
3. **"Mean new-draw lengths near exp3's committed values" —
   UNGRADEABLE AS WRITTEN.** exp3's committed verdict record
   discloses no mean draw lengths (its descriptives were not part of
   the verdict output), so there is no committed referent to compare
   against. The 3c values (26.2–30.4 chars across the four cells)
   are internally consistent and disclosed; the prediction should
   not have named a referent that was never committed. Ledgered as a
   projection-craft lesson, not a data finding.
4. **"Len-4 rates meaningfully above the luck floor (~9× at 410m,
   ~25× at 1b)" — HIT within resolution.** 410m: 2.01e-5 = 9.2×.
   1b: 4.70e-5 = 21× (projected ~25× under full len-4
   concentration; two fires landed in longer strata instead).

## What the projection did not name

**Item-level heterogeneity is the strongest texture in the fires.**
Item 123 ('ecde') fires at BOTH sizes — 4 of the 12 new fires — and
item 447 fires twice on a single seed. The sampled channel is not a
uniform trickle over the battery; a few items carry most of the
reachable mass. Consistent with the same-weights profile (3b's probe
margins are item-averaged; per-item margins presumably vary) and
directly relevant to rank-prediction successors: per-item rate
structure is measurable at feasible k for the easiest items.

## Instrument notes carried forward

- Stop #1 (2c's verify partial on punctuation-wrapped interior
  whitespace) — the totality wrapper pattern (guard the draw side,
  hard-error the answer side) belongs in the methods paper's
  criterion-hygiene section: a frozen criterion must be TOTAL over
  the emission alphabet, and freezes should fuzz for totality, not
  only semantics.
- The len-6 'rxxxxd' fire is the program's cleanest demonstration
  that answer-internal structure, not surface length, sets the
  sampled channel's cost — worth a sentence in the essay's
  signature-2 discussion.

## Verdict-level summary

Projection HIT at the verdict and gate level with exact pooled
numbers; one named-in-advance miss fired (len-6), one prediction was
ungradeable by referent absence (mean lengths), everything else
held. The DEEPENS world is the strongest of the four for the
resolution thesis: raising k by 3× both replicated the known channel
(3.0× point-rate consistency at the fired cell) and dropped a wall
(410m), exactly what "signature 2's resolution parameter is
load-bearing" predicts.
