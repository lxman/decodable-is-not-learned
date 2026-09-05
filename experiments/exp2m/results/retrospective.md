# Exp 2m retrospective — grading projection eaf69ad4

Sealed after `exp2m-preregistered` (77301c13) and `exp2m-endpoint-sealed`
(3c70fdb5), before gate 1 or any intermediate SmolLM3-3B checkpoint was
queried. Graded against `verdict.json` (git 601a2227): verdict level
first, then texture BY RUNG TYPE as dial f required. The projection's
honesty note stands: the verdict-level call for A repeated a
construction already read twice; the foresight was staked on the
per-rung table, the paired difference, S4 and S8.

## Verdict level — HIT on the world, MISS on both points

Projected SHARED; realized SHARED. But T_A projected ≈ .11 [.06, .16]
"placed INSIDE the block-SD scatter around the bar" landed at **.1696 —
above the range**, and T_B projected ≈ .15 [.09, .21] landed at
**.2514 — above the range and across the named upper disconfirmer
B-iii (T_B ≥ .25) by .0014**. A-iii (≥ .20) did not fire (.1696). The
named alternative OLMO-ONLY via A-i never came into play: A cleared the
bar by .07, seven null-SDs, nowhere near the scatter the projection
placed it in.

**B-iii fired on its stated number.** Its reading, written in advance:
"x_B forecasts a third family as well as it forecast its own; would
need the DCLM-class overlap to be doing most of the work (S8's ordering
would have to agree: 13B/7B closest to 3B)". S8 agrees: the OLMo-2 pair
reads .46 / .40 against SmolLM3's order, the Pythia pair .25 / .23.
The disconfirmer named the mechanism and the mechanism's own check, and
both held. The tolerance lesson from 2l was applied only to the
low-side disconfirmers (A-i / B-i carried ".015"); the -iii's carried
none, so B-iii's firing by .0014 is read on its letter and disclosed as
such rather than argued away.

## Per-rung foresight by type — 9 hits / 9 misses, EVERY miss above the range

Arithmetic (A | B):
- add_base8: A .439 vs [.18, .42] — MISS (above); B .750 vs [.25, .55] — MISS (above). Top locus for B as projected; for A second by .014.
- sub_base8: A .453 vs [.12, .38] — MISS (above); B .407 vs [.08, .32] — MISS (above).
- arith_next: A .220 vs [.00, .16] — MISS (above); B .433 vs [.08, .28] — MISS (above).
- sub3_mid: A .152 vs [−.02, .16] — HIT; B .052 vs [−.03, .11] — HIT.
- add3_mid: A .019 vs [−.04, .10] — HIT; B .050 vs [−.02, .12] — HIT.
- sub4_mid: A −.020 vs [−.05, .05] — HIT; B −.001 vs [−.03, .07] — HIT.

Option (A | B):
- antonym: A −.041 vs [−.10, +.05] — HIT (the sign split repeats on a third family, as called); B .168 vs [.00, .20] — HIT.
- antonym6: A .170 vs [−.02, .16] — MISS (above by .010); B .222 vs [.02, .22] — MISS (above by .002).
- odd6: A .133 vs [−.03, .15] — HIT; B .180 vs [−.04, .16] — MISS (above).

Type-level disconfirmers: none fired (add_base8 A ≥ .15 ✓; sub4_mid A
< .12 ✓; antonym A < +.10 ✓; antonym B > .00 ✓). Ordering claims,
graded on adjacent pairs: A 4 of 5 (add_base8 ≥ sub_base8 inverted by
.014, inside both CIs); B 6 of 8 (antonym > odd6 inverted by .012;
add3_mid ≥ sub3_mid inverted by .002).

The shape of the misses is one shape: every rung the projection
attenuated for "a third family, a different tokenizer, no Pile
overlap" came in stronger, on both predictors. The mid-digit rungs and
sub4_mid, where the projection expected near-zero, were near zero.

## Secondaries — 13 hits / 11 misses; the misses again lean one way

- S1 ladder monotone with shrinking increments — HIT (.1095/.1400/.1612/.1696). "The four 64-draw blocks all BELOW the bar" — MISS: three of four clear it (.1095/.1106/.1106/.0998). "256 above the blocks by ≥ .03" — HIT (+.059 over the best).
- S2 "410m ≥ 1b a fourth time" — MISS by .0003 (.1693 vs .1696, a tie to the third decimal); range [.07, .18] — HIT.
- S3 "B beyond A's bucket ≈ .10" — MISS (.2306); "A beyond B's bucket ≈ .04" — MISS (.1226); "the asymmetry favours the denser predictor" — HIT.
- Paired difference: positive — HIT (+.0818); "interval includes zero" — MISS (CI95 [.057, .106] excludes it).
- S4 increment ≈ +.03 [−.03, +.09] — HIT on the range (+.0659); "SMALLER than 2k's +.054 and 2l's +.069" — MISS (between them). The reading "density-not-lineage sealed a second time" does not follow as written: at matched draws the DCLM-class predictor leads a third family by the margin the lineage predictor led its own — the increment is corpus-shaped, not lineage-shaped.
- S5 π ≈ .15 [.08, .22] — MISS (above: .2417); "π ≤ .05 retires the mechanism" — did not fire; the mechanism's second sealed test is its strongest reading.
- S6 stage3 ≥ endpoint on ≥ 10 of 14 — HIT (12); Base ≥ endpoint on ≥ 10 of 14 — HIT (12); the named exceptions sub_base8 and antonym — HIT (exactly those two, both whichs).
- S7 twin "0 items on every rung" — MISS on the letter (1/500 on quad_next and roman_sum7; chance-level); "NO battery-wide collapse" — HIT; "≤ 2 checkpoint-local collapses on the dense head" — MISS (55 over the grid, all on flat rungs; 2h's class at a scale nothing in the line predicted); "the reversal pair shows positive raw D" — MISS (≈ 0 at both densities, as on 13B); "first-correct within .02 of the count outcome" — HIT (.0055 / .0083). The projection's "ceiling fractions at the endpoint .99 / .95 / .87" used the endpoint count as the ceiling; the analyzer's ceiling is items correct at every grid point (arith_next 47, sub_base8 23, antonym 23, add_base8 15) — the two definitions do not meet, ungradeable, and the analyzer's is the one that matters: the coarse head cost little.
- S8 "all four positive" — HIT; "OLMo pair ≥ .15" — HIT (.46 / .40); "Pythia pair in [.05, .15]" — MISS (above: .25 / .23); "13B ≥ 7B" — MISS (7B .46 > 13B .40); "6.9b ≥ 2.8b" — MISS (2.8b .25 > 6.9b .23); "the OLMo pair above the Pythia pair" — HIT, and by a wide margin.

## What the misses say

1. **Cross-family attenuation did not happen.** Two sealed outcomes in
   a row (13B, now SmolLM3-3B) have read the Pythia-1b predictor at or
   above its known-outcome readings, and the third family read it
   HIGHER than the second. The projection's prior — a third family, a
   different tokenizer and no corpus overlap cost signal — was wrong in
   direction on every rung it touched. The item ordering the counts
   carry on the base-8 and arith rungs is task-shaped.
2. **x_B's within-lineage readings were not a lineage effect.** Its
   first cross-family reading (.2514) is its highest. What 2i/2j/2l
   called "the lineage advantage" reads, on this outcome, as the
   DCLM-class corpus plus density: S8 puts both OLMo outcomes far
   closer to SmolLM3's order than either Pythia outcome, and S4's
   matched-density increment is unchanged from the within-lineage
   ones.
3. **The 64-draw density story is outcome-dependent.** On 13B no
   64-draw block cleared the bar; on SmolLM3 three of four do. The
   ladder still adds +.06 to 256, but "2i's sub-bar reading was
   density" was one outcome's finding, not a constant.
4. **The named disconfirmer fired by .0014, and it was right.** B-iii
   was written as the reading under which x_B forecasts a third family
   as well as its own, with S8 as its check; both came true. A
   disconfirmer that names its mechanism and the mechanism's own
   verification is worth more than the tolerance it lacked.

## Tally

Verdict: HIT (SHARED). Points: 0 of 2 (both above range; B-iii fired).
Per-rung ranges: 9 of 18 (every miss above). Type-level disconfirmers:
0 of 4 fired (as projected). Orderings: 10 of 13 adjacent pairs.
Secondaries: 13 of 24. Every miss but four (the tie at S2, the twin's
two chance hits, and the S8 within-pair orderings) is the same miss:
the structure was stronger than projected.

## Process notes (Michael's call whether any earns the methods paper)

- **Every disconfirmer needs a tolerance, the upper ones included.** 2l's
  lesson was applied to A-i / B-i only; B-iii fired by .0014 on a bare
  number. The rule should read: a named disconfirmer states its number
  AND its tolerance, in both directions.
- **A projection that attenuates for "a new family" has now missed low
  on two consecutive sealed outcomes.** The prior itself is the finding:
  what the sampled counts carry across families is more task-shaped
  than the design's corpus-overlap reasoning assumed. The next
  projection should state the attenuation prior explicitly as a claim
  and give it its own disconfirmer.
- **A grid-density sensitivity is a control, not a descriptive.** The
  21-point log-head subset re-read both tests within .002 of the
  26-point grid; without it, the higher readings on SmolLM3 could have
  been attributed to the denser head. Worth keeping as a standing
  secondary wherever grids differ across outcomes.
- **Define the ceiling the analyzer computes, in the projection.** The
  projection's "ceiling fraction" and the analyzer's did not meet; the
  projection should quote the analyzer's definition and forecast that.
