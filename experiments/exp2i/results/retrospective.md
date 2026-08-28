# Exp 2i retrospective — the projection graded, and what the record teaches

Projection sealed at `5b000b7d` (after `exp2i-endpoint-sealed`, before
gate 1 or any intermediate checkpoint). Verdict: **LINEAGE**.
Projected: **BOTH**. **MISSED at the verdict level — and the named
disconfirmer A-i fired verbatim**: "T_A in [.04, .10) at p < .01 —
structured but below the bar … Grades the verdict MISSED (LINEAGE if
B fires)." T_A = .0949, p = 9.999e-05; B fired. The projection also
wrote, in advance, "the bar T ≥ .10 is the live question for A, not
p" and "LINEAGE is therefore the closest alternative world, not
NEITHER" — the miss happened exactly where it said a miss would.

## Hits

- **The mechanism that decided the verdict was named in advance**: the
  three mid-digit rungs "contribute ≈ 0 by construction (x_A fires on
  10/31/13 items of 500)". Landed .005 / .020 / −.022; the six carried
  rungs alone average .1418. The dilution was the verdict.
- T_A range [.08, .16] contained .0949 (the point .11 was high).
- T_B .2153 inside the projected [.10, .22]; no B disconfirmer fired.
- cross-beyond-within projected ≈ .07 → landed **.0701**; within-alone
  projected ≈ .18, above T_B → landed .2204, above T_B. The asymmetry
  call (within-lineage carries it) was right.
- Twin 0 everywhere; gate 1 clean ("the tenth consecutive
  byte-identical reproduction, first on OLMo, first at 7B") — exact.
- A's top loci: projected "sub_base8, antonym6, add_base8, arith_next
  at the top" — landed sub_base8, add_base8, antonym6, odd6,
  arith_next (the pair order antonym6/add_base8 swapped; the set
  right). sub4_mid flagged the likeliest degenerate-looking cell — it
  landed the only NEGATIVE D with a CI excluding zero (−.022
  [−.042, −.003]).
- "T_A's per-rung CI excludes zero on 4 of 9, not the majority" —
  MISSED by one, and directionally: 5 of 9 exclude zero on the
  positive side (sub_base8, add_base8, antonym6, odd6, arith_next —
  the last at lo .0015), a bare majority, so had BOTH landed the
  shared-component headline condition WOULD have been met. Moot in
  LINEAGE; graded a miss. (sub4_mid's CI also excludes zero — on the
  negative side.)

## Misses (each one points the same way)

1. **Verdict-level: BOTH.** The cross-family component was projected
   one notch stronger than it measured against the frozen bar.
2. **antonym under strata**: projected mid-pack for A; landed .028 —
   the position strata absorb nearly all of antonym's raw concordance
   (raw_d .286 → stratified .028). The projection under-weighted how
   much of the cross-family antonym signal IS the option-position
   covariate.
3. **410m cross replication**: projected "same direction, lower T" —
   landed .1154, ABOVE the 1b cross point (and above the bar, on the
   non-gating side). Sparser counts did not mean less rank signal.
4. **Reverse direction**: projected ≈ .08–.14 ("approximately
   symmetric") — landed .2612 / .2974. Not symmetric: x_B forecasts
   Pythia's outcomes at 2–3× the strength with which x_A forecasts
   OLMo's. The projection modelled cross-family concordance as a
   property of the PAIR; the record says it scales with the
   PREDICTOR's information density (x_B's per-item counts are ~5–10×
   x_A's on most rungs). This is the sciencey miss worth keeping: it
   reframes A's sub-bar T as partly a thin-predictor effect, and it
   is the concrete entry point for §6's named mechanism successor.
5. **Texture**: "at least one checkpoint-local collapse (≥ 400/500 on
   one answer) somewhere in the head" — none occurred on OLMo-2 (the
   nearest thing: add_base8's dip to 45/500 at step 512000). 2h's
   collapse phenomenon did not carry across families; its transient-
   clear phenomenon did (median5 ×7, median7 ×6, count_div13 ×3).

## Reading A honestly

T_A = .0949 at the permutation floor is not noise and not a licence.
Under POWERED (min-detectable T .022), it is a measured quantity: the
cross-family trace exists on this battery at roughly half the
within-lineage strength, and the preregistered bar — frozen when BOTH
was still the projected world — held. The §6 LINEAGE licence governs
the essay: lineage-bound wording, no cross-family forecasting claim.
The sub-bar structure is reported, not claimed.

## Process notes for Michael's call (methods-paper candidates)

- **Stop #1** (the transformers-5 directory read; fixed test-first,
  ratified, re-tagged): the lesson candidate is not "write config.json"
  but *an execution path a frozen instrument will take on campaign day
  must be executed once, end to end, before the tag* — 2i's freeze
  executed the sampler and the thin loader against real weights
  (gate-1 rehearsals, preflight) but the candidate-file loader's first
  real execution was gate 1 itself. A one-checkpoint loader rehearsal
  (load, one forward pass, free) would have surfaced this in the
  freeze session.
- **Stale-premise checks**: three tests and two cold-tool items
  encoded the PRE-TAG tree ("the tag does not exist yet", "139 stage
  artifacts absent", "every stage artifact is json") and broke the
  first time the tree grew — none on a verdict path, all fail-loud.
  Candidate rule: a check written before a state transition must
  assert the INVARIANT, not the current state; run every cold tool
  once after each stage lands, not only at close-out.
- **The bar at the boundary**: the power record printed
  P(fires | D = .10) = .44 in advance — the design KNEW a true effect
  at the bar was a coin flip and said so. Nothing to fix; worth citing
  as what "the bar decides, not p" looks like when it actually bites.

## Numbers at a glance

| | T | p | fires |
|---|---|---|---|
| A (cross-family) | .0949 | 9.999e-05 | no — bar .10 |
| B (within, beyond A) | .2153 | 9.999e-05 | yes |
| within-alone | .2204 | 9.999e-05 | — |
| cross-beyond-within | .0701 | 9.999e-05 | — |
| 410m cross (non-gating) | .1154 | 9.999e-05 | — |
| x_B → 2.8b / 6.9b (reverse, known) | .2612 / .2974 | 9.999e-05 | — |

One pre-committed change UNSPENT. Campaign: one ledgered stop, zero
halts, zero attrition after relaunch; gate 1 byte-identical (tenth).
