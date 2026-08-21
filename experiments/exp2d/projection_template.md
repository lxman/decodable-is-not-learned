# Exp 2d — Projection (to be sealed BEFORE the analyzer runs)

Standing practice since 1c: the projection is written and committed
before `analyze_2d.run()` executes on the real tranche, then graded in
the retrospective. Fill every line; leave no field to be filled after
the number is known. The known-outcome caveat (§2) applies to the
projection as it applies to the verdict: the OUTCOME column was known
when this was written; only the PREDICTOR column was not.

## Sealed at commit: `________` (date ________)

### Verdict
- Projected verdict: `PASS | FAIL | INDETERMINATE | INSUFFICIENT_DATA`
- Projected AUC (point): ____  Projected block p: ____
- Projected cluster CI: [____, ____]; projected drop count: ____
- Declared status carried from `power_2d.json`: `POWERED | DECLARED UNDERPOWERED IN ADVANCE`
  (power at AUC .85 = ____; at .75 = ____; at .5 = ____)

### Gate 1 (production path, 128,000 draws)
- Projected: IDENTICAL in 4/4 cells, fire at (reverse_string, 1b, item 436, draw 6) reproduced.
  Basis: the sixth consecutive byte-identical reproduction on this stack (3e); stack unchanged.

### The predictor's zero set (main, 32,000 draws per rung per size)
- Projected rungs with predictor score 0: ____ of 34 (list): ______
- Projected rising rungs with predictor score 0 (the power-killing set): ____ (list): ______
- Projected rising rungs with RAW zero at 1b: ____ (list): ______

### §5.4 named secondaries
- sub3_mid sampled 1b: ____ verified / 32,000 (projected) — percolation candidate? `yes | no`
- arith_next sampled 1b: ____ verified / 32,000 (projected) — percolation candidate? `yes | no`
- Both pair rungs land as candidates (the sharpest disconfirmation): `yes | no`
- Probe predictor's AUC on the same label (computed now from committed records): .6703 (block p ____, CI ____)
- Spearman ρ predictor vs corrected ascent (projected): ____; vs 2c's frozen ascent: ____ (2c's probe: .368)
- Argmax 1b: projected number of rising rungs already performable at 1b: ____ (list): ______
- Restricted primary AUC (projected): ____

### Named disconfirmers
- The projection is WRONG at the verdict level if: ______________________
- The named disconfirmer of the ladder story fires if: both sub3_mid and arith_next have zero verified 1b draws in 32,000 AND probe margin 0 (they do have probe margin 0).

### Misses I expect to be graded on
- ______

### What I will NOT do after seeing the numbers
- No slicing of the battery; no alternative floors; no second statistic; the one pre-committed change stays UNSPENT unless the freeze ratified a use.
