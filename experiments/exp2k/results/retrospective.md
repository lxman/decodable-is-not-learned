# Experiment 2k — retrospective

Projection `projection.md`, sealed at cb64f15a (2026-08-30 08:17 EDT)
after the campaign, the seal, the power record and the seal tag, before
the analyzer ran once. Graded against `results/verdict.json`.

## Verdict level — HIT, worth what the design said it was worth

Projected DENSITY, T in [.13, .19], point ≈ .155. Landed DENSITY,
T = .1548, p 1e-4. The design (§2) said in advance that 2j's committed
prefix ladder made this call; the post-seal-tag read sweep printed the
same T five minutes after the projection was sealed. The verdict-level
hit carries no foresight and is graded as none.

## The texture — where the foresight was, and where it wasn't

| item | projected | landed | grade |
|---|---|---|---|
| add_base8 D at 256 | .38–.50, the largest gain | .476, +.234, the largest | HIT |
| sub_base8 | .36–.44, stays the top rung | .440, but SECOND (add_base8 overtook) | MISS (rank) |
| arith_next | .14–.22, the second-largest gain | .092, +.028 | MISS |
| antonym6 | .11–.16 | .115 | HIT |
| odd6 | .09–.14 | .096 | HIT |
| antonym | .03–.08, ≈ flat | .024, flat | HIT (flat; range edge) |
| sub3_mid | ≈ 0 (−.02–.06) | **.147** [.091, .204] | **MISS — the named mid-digit disconfirmer fired** |
| add3_mid | ≈ 0 | .027 | HIT |
| sub4_mid | ≈ 0 | −.024 | HIT |
| six-carried mean | .20–.26 | .207 | HIT |
| S1 block SD | [.006, .018]; seed 0 not an outlier | .0066; blocks .0949/.1077/.0948/.0938 | HIT (bottom of range) |
| S2 | monotone, shrinking increments ≈ .03/.02/.015 | .031/.018/.012 | HIT |
| S3 increment sign / size | positive, .01–.05 | +.054 | HIT sign / MISS size (just above) |
| S3 placement | k ≈ 10–16, bracket not [64, None] | k 9.9, bracket [8, 16] | HIT |
| S4 cbw / wbc | .09–.13 / .17–.21 | .1148 / .2044 | HIT / HIT |
| S5 → 2.8b / 6.9b | .21–.26 / .24–.30 | .2277 / .2813 | HIT / HIT |
| S6 410m ≥ 1b; [.14, .21] | | .1695 ≥ .1548 | HIT |
| S7 live items add3/sub3/sub4 | 25–35 / 90–130 / 20–30 | 39 / 130 / 30 | MISS / edge / edge |
| S7 first-correct | ≈ count − .02 | .1658 (count + .011) | MISS |
| power | POWERED, null SD .009–.011, P(.10) .4–.6 | POWERED, .0108, .489 | HIT |

Fifteen hits, five misses; the misses are the science:

1. **sub3_mid.** The density account was applied too timidly to the
   rung where it applies most. At 64 draws sub3_mid had 31 live items
   and D .020; at 256 it has 130 and D .147 [.091, .204]. Density buys
   signal where the 64-draw predictor is sparsest AND the outcome has
   room — sub3_mid's 7B endpoint count is 495/500, so the order in
   which those items became emittable has structure to read once
   enough items are live. The projection reasoned "too few live items
   to carry a D" from the 64-draw count and did not extrapolate the
   live-item growth (31 → 130) it could have computed from the tallies
   it already had. add3_mid (39 live) and sub4_mid (30 live) stayed ≈ 0
   as called: the threshold for a rung to carry a D on this outcome
   sits somewhere between ~40 and ~130 live items.
2. **arith_next barely moved** (+.028 for 4× the draws). Its 64-draw
   rate (.017, 531 verified draws) already put 277 items live; 256
   draws raise that to 468 but the concordance does not follow. The
   count was already informative at 64; what limits arith_next's
   cross-family reading is not density. Named for the mechanism side:
   arith_next is the rung where 2f's probe and 2h's sampler disagreed
   most, and where the answer prior forecast little in 2j.
3. **add_base8 overtook sub_base8.** The sparser of the two octal
   rungs at 64 (rate .0053 vs .0226) gained more (+.234 vs +.102),
   which is the density account's own prediction stated one step
   further than the projection took it: "gains where sparsest" also
   means "ranks change where the sparse rung had the most to gain."
4. **S3's increment (+.054) sat just above the projected range** and
   is essentially 2j's low-density value (+.062): the lineage
   advantage does not shrink with Pythia-1b's draw budget at all. The
   projection expected some closing; there was none. The reading: two
   separable quantities — the cross-family reading's shortfall below
   the bar is density (it clears at 4×), the cross-family-vs-lineage
   GAP is not (it is the same .05–.06 at 64 and at 256 draws, and at
   matched verified-draw density).
5. First-correct above the count outcome — no explanation offered; a
   small item.

## What the record says beyond the primary

- **S1 is the quiet headline.** Four independent 64-draw blocks of the
  same law: three read .094–.095 and one reads .108. 2i's fires = False
  was one block; a different seed-0 would have fired Test A and 2i's
  world would have read BOTH at the same design. The permutation null's
  SD (.0094) is the wrong yardstick for a bar decision at the
  boundary; the sampler-noise SD (.0066 here) is the one that matters,
  and this program had never measured it. Process note (methods-paper
  candidate, Michael's call): a bar decision within one sampler-noise
  SD of the bar is a coin flip and should be read as one at the time
  it is made; the predictor's block SD is a number a preregistered
  design can compute in advance from a pilot.
- **256 Pythia-1b draws ≈ 10 OLMo-1B draws on OLMo's outcome** (S3
  placement k 9.9, bracket [8, 16]; 13.7 at 410m). A-1's exchange rate
  from thinning x_B (≈ 16 on OLMo's outcome) and this one from
  thickening x_A (≈ 26) bracket the truth; the curves are not linear
  in log k on either side.
- **Density is family-blind** (S5): the within-lineage forward gains
  (.1672 → .2277 on 2.8b; .2179 → .2813 on 6.9b) are the size of the
  cross-family one.
- **410m ≥ 1b again** (.1695 vs .1548 at 256; .1154 vs .0949 at 64), on
  the same rungs (add_base8 .692 at 410m). Whichever size is the better
  cross-family predictor, it is not the larger one; a size question
  for approach C's design.

## Process notes for Michael's call

1. **Project the live-item growth, not only the D.** The projection had
   the per-seed tallies (the ledger's table) and did not use them to
   forecast which sparse rung would cross the carry-a-D threshold; the
   miss on sub3_mid was computable from data in hand.
2. **The sampler-noise SD of a bar statistic belongs in the power
   record.** 2i's POWERED declaration was about the permutation null;
   the quantity that decided 2i's world was the block-to-block SD,
   which a k = 8 pilot could have priced. Candidate rule: when a
   design's bar sits within .02 of the predictor's expected T, the
   power record prints the predictor's block SD from the pilot beside
   the null SD.
3. **The post-tag disclosure worked as designed.** The read sweep after
   the seal tag necessarily prints the primary; sealing the projection
   before it made the disclosure inert. The order — projection, then
   any tool that computes a statistic on the complete tree, then the
   analyzer — is the rule.

## Campaign and instrument

648.9 min detached, gate 1 IDENTICAL on 576,000 seed-0 draws (the
twelfth byte-identical reproduction), zero stops, zero attrition; the
tally halt never fired; the seal, power and analyzer each ran once;
every pin real at the verdict; one pre-committed change UNSPENT. Model
contact: the tier and dial i's one-item rehearsal. The freeze's class
defect F-1 (the halt scan blind to the gz-only halt window) did not
bite — there was no halt — but it would have been reachable by a host
kill inside a ~1-second window per cell, eighteen times over.
