# Exp 2e — Projection (SEALED before the analyzer runs)

Standing practice since 1c: the projection is written and committed
before `analyze_2e.run()` executes, then graded in the retrospective.
**Disclosure, stronger than 2d's:** every input is known to the
author of this projection — the §4 tally table (68 main cells), the
floors, the rising/flat label and the corrected ascent were all in
view when the functional was chosen and when this was written. What
is projected is the frozen analyzer's OUTPUT. The numbers below are
HAND ARITHMETIC from the §4 table (log((r + ε)/c) per cell, then a
pairwise count); no code evaluated any functional against the label
on the real tallies before the tag, and none has since. The
arithmetic is coarse (two significant figures per cell, ties judged
by eye) — the misses will be in the second decimal.

## Sealed at commit: (this commit) — 2026-08-22

### Verdict
- Projected verdict: **FAIL** (§6 branch 2: the family-cluster
  bootstrap CI on AUC(F1) includes .5).
- Projected AUC(F1): **≈ .61** (hand count ≈ 154 of 253 rising–flat
  pairs; range .58–.64). The ordering: arith_next is the only rising
  rung above every flat rung (+.04, the only positive F1 on the
  battery); the four rising option-listing rungs (median5 −.42,
  antonym6 −.46, antonym −.53, odd6 −.58) sit just below the flat
  option-listing pair (odd_one_out −.40, median7 −.41) and mod17
  (−.42) and above ~20 flats; count_div13 (−.70), sub_base8 (−.92),
  add_base8 (−1.5) sit mid-pack; the three rising mid-digit rungs
  (sub3_mid −2.5, sub4_mid −2.7, add3_mid −2.8) beat only the 6–7
  flats at the bottom (base12/base13, caesar ×2, add4_mid, the
  reversal pair).
- Projected block p: **≈ .2–.4** (not below .01 by any route).
- Projected cluster CI: **lower bound < .5** (≈ [.40, .80]); the
  16-family resample of a .61 point estimate does not exclude .5.
- Projected drops: a few of 10,000 (resamples with no rising family).

### The comparison column and the baselines
- 2d comparison: **.5455 / .6675 / [.5000, .6667] / 2 drops — exact**
  (the gate; anything else is INSUFFICIENT_DATA, which I do not
  project).
- **B0 (−log c) AUC ≈ .43** — the floor alone ranks AGAINST the label
  (hand count ≈ 108 of 253): the lowest floors on the battery belong
  to flat rungs (base7, oct2dec, the reversal pair at .002; add4_mid,
  caesar_len8 at .006) and several rising rungs have the highest
  (antonym .25, median5 .20). So **F1 − B0 ≈ +.18**, paired CI wide,
  probably including 0 at the low end.
- **F2 (raw log rate) AUC ≈ .60** — close to F1 (the option-listing
  rungs dominate both orderings).
- **F3 (rank residual) AUC: .5–.7**, no confident point.
- 2c's probe column: AUC .6008 (pin) — F1 and the probe land within
  a few hundredths of each other; ρ .368 pin reproduced.

### Secondaries
- Spearman ρ(F1, corrected ascent) ≈ +.2–.3 (23 zeros on the outcome
  side); block p ≈ .2–.4; the same order for F2; B0 negative or ≈ 0.
- Pilot replication (seed 1000, 4,000 draws): AUC ≈ .55–.65, same
  sign; rank correlation pilot-F1 vs main-F1 ≈ .9 (the pilot tallies
  are ≈ main/8 with Poisson noise; the low-count rungs reorder).
- 1b-only ≈ 410m-only ≈ .6; 12b-only label: similar.
- Sensitivity: ε = 1/3,200 lowers the AUC slightly (the zero- and
  near-zero-draw flats rise toward the mid-digit rising rungs);
  majority-only floors RAISE it (≈ .63–.67: the four rising
  option-listing rungs jump to F1 ≈ +1.3 to +2.8 and beat every flat
  except median7/odd_one_out, which jump too); dropping the two
  first-digit-run rungs lowers it a little (both are flats that
  8 of 11 rising rungs beat).

### Named disconfirmers
- The projection is WRONG at the verdict level if the tree returns
  PASS or INDETERMINATE — i.e. if the cluster CI excludes .5 (an
  INDETERMINATE at AUC ≈ .6 is the live alternative, if the family
  structure happens to carry the rising rungs' advantage in almost
  every resample; I put it under 20 %).
- The B0 projection is WRONG if B0's AUC ≥ .5 (then F1's edge over
  the floor alone is smaller than claimed).

### Misses I expect to be graded on
- The AUC's second decimal; the block p; the CI's width; B0's exact
  value; the ε sensitivity's direction.

### What the numbers already say, written before the analyzer
Removing the threshold restores a dynamic range, and the range
orders the rising rungs slightly above the flat ones — by about the
same margin as the probe did on the same label (.60) — while the
floor alone orders them slightly below. That is consistent with "the
sampled channel at 410m/1b carries a little ordering information
about this battery's ascent, most of it in whether a rung's answer
space is an option list", and not with "2d's null was its
threshold's": the threshold removed a .61, not a .75. The §6 FAIL
sentence reads, under this projection, as "not distinguishable from
chance under the family-cluster bootstrap at a point estimate of
about .6"; the essay's Prediction 2 paragraph gains its one sentence.

### What I will NOT do after seeing the numbers
- No second functional promoted; no re-weighting of sizes; no subset
  of the battery; the one pre-committed change stays UNSPENT.
