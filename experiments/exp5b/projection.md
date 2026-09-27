# Experiment 5b — projection (sealed after `exp5b-preregistered`, before the box)

Written 2026-09-26 at tag `exp5b-preregistered` (46dadbdd6; object 9c879204b), after the power record and before any model load. Design §7 stage 0: by row and by type, T_sym's point and range, the sub-cell with its probabilities, σ̂_s pooled and per side, the S2 swap range, the cross-box drift as a claim with its own disconfirmer, tolerances on every number in both directions, per-rung tables by type. The grading goes in `results/retrospective.md` by cell, primary, sub-cell, modifier, row, type and secondary, with the designer's prior's two disconfirmers graded first.

## What the designer read, declared first

**Read for this projection (Experiment 5's committed record, `experiments/exp5/results/verdict.json`):** the 63 live cells' f, a, R, P, c and class, and the S11 block — every small side's `step142000` count beside its final on all 34 rungs, and the six loss rows (the four larger finals 0.0003–0.0009 nats better than their 142000; 410m's 0.0014 worse; 160m's 0.019 worse). On the live rungs the 142000 − final differences are: 2.8b sub3_mid −75, arith_next +23, sub_base8 −21, antonym6 −14, add_base8 +13, median5 −11, antonym −10, add3_mid −6, odd6 +2, odd_one_out +1; 6.9b count_div13 −24, arith_next +23, sub_base8 −14, median5 −13, odd6 +11, antonym6 −7, add3_mid +6, antonym +5, add_base8 −4, sub3_mid +3, sub4_mid −2; 1.4b odd6 +19, antonym −17, median5 +12, antonym6 −7, arith_next +6, median7 −2; 1b antonym −17, odd6 −13, antonym6 −6, arith_next +5; 410m antonym6 −8, arith_next −3, median5 −1; 160m antonym +8. **Not computed, by §2's rule:** any Q, M₁, T₁ or other 5b statistic on those bytes — the row-level reasoning below uses the printed per-rung differences and the committed R and P, nothing combined at the cell level. S8's one-member reading is a known-input quantity in principle and is graded lightly for that reason.

**Sealed and unknown:** the 24 box-B reads — every f_B and the three members per side — hence every Q, M, σ̂_s, T_sym, the sub-cell, and every secondary that touches a 5b read. The members at 141000 and 140000 are the genuinely new information: whether the 142000 differences are the last 1,000 steps' monotone move (the members sit further from the final) or a checkpoint-local wobble (the members sit near it).

**The designer's prior, stated as a claim with its own disconfirmers (2m's note 2).** *The claim:* the small side's wobble over the anneal's last 3,000 steps is of the large side's order — σ̂_s pooled ≈ 13 items against σ_L 15.07 — so the matched placebo M averages ≈ 17 items against Experiment 5's P of 12.4, and subtracting it costs ≈ 5 of the 27 items: T_sym ≈ 22 items, the excess survives, the rung-block flip still rejects, and the 2.8b row still carries most of it (sub3_mid's 264 → 189 costs those two cells a fifth of their c and nothing else). *Disconfirmer (i), the disclosure was load-bearing:* σ̂_s pooled ≥ 20 or T_sym ≤ .030 (15 items) — the small side's wobble was the larger part of what Experiment 5 read as an excess. *Disconfirmer (ii), the 142000 differences were a one-off:* σ̂_s pooled ≤ 7 or T_sym ≥ .052 — the members sit on the finals and the anneal's last 1,000 steps were checkpoint-local, so M ≈ P/√2 and the excess GROWS under the correctly scaled statistic.

## The primary

**T_sym ≈ .044, tolerance [.030, .058] (22 items [15, 29]); rung-block p ≈ .002, range [.0003, .02]; live cells 63 (fixed), rungs with a nonzero block sum 13 [12, 13], positive block sums 10 [8, 12].** Construction by row (c_sym = (R − M)/500; M projected from each row's printed 142000 differences taken as the scale of all three members, with the large side's own moves entering at Experiment 5's P):

| small side | cells | Exp 5 mean c (known) | projected mean c_sym | what moves |
|---|---|---|---|---|
| 2.8b | 18 | +.1173 | **+.095 [+.075, +.112]** | sub3_mid's two cells fall from ≈ .51 to ≈ .41 each (M ≈ 50 from the −75 move against a large side at 4–8); arith_next (+23) and sub_base8 (−21) lose ≈ .02–.03 per cell; antonym6 (−14), add_base8 (+13), median5 (−11), antonym (−10) lose ≈ .01–.02; add3_mid, odd6, odd_one_out unmoved |
| 6.9b | 11 | +.0198 | +.010 [−.010, +.030] | count_div13 (−24) and arith_next (+23) go further negative; median5 (−13) and sub_base8 (−14) shrink; antonym and antonym6 (5, 7) hold at ≈ +.05 |
| 1.4b | 12 | +.0316 | +.025 [0, +.050] | antonym (−17) and odd6 (+19) cost their cells .01–.03; antonym6, arith_next, median5, median7 hold |
| 1b | 13 | +.0352 | +.030 [+.010, +.050] | antonym (−17) against R 47–78: still +.06–+.11; odd6 (−13) → ≈ −.03; the rest within .01 |
| 410m | 8 | +.0286 | +.030 [+.010, +.050] | antonym6 (−8) against R 25–40 and P 3.5–14.5: +.03–+.06 on all five; arith_next, median5 ≈ 0 |
| 160m | 1 | −.0245 | +.010 [−.050, +.050] | one antonym cell with P 56.8 (M at ≈ 40 from the 8-item move; the sign is a coin flip) |

Weighted over 63: ≈ .044. The null at σ̂_s ≈ 13 has mean −.0008 and SD ≈ .003 (the sealed record between its 10 and 15 points), so a T_sym of .044 is fifteen null SDs out and p is set by the block count and sub3_mid's dominance, as in Experiment 5 (p .00061 with 13 blocks).

**The tolerance's edges are the members' question.** If 141000 and 140000 continue the 142000 moves monotonically (sub3_mid at ≈ 150–170, arith_next at ≈ 170, sub_base8 at ≈ 60 at 2.8b; count_div13 at ≈ 60 at 6.9b), M grows on exactly the cells carrying the excess and T_sym lands near .032; if they sit near the finals (the 142000 reads checkpoint-local), M ≈ P/√2 + a little and T_sym lands near .055. Neither edge crosses the bar (.01) or, on the projection, the α line.

## The calibration sub-cell

**σ̂_s pooled ≈ 13 [9, 20]; per side 2.8b ≈ 20 [14, 30], 6.9b ≈ 12 [8, 18], 1.4b ≈ 11 [7, 16], 1b ≈ 10 [6, 15], 410m ≈ 5 [3, 10], 160m ≈ 8 [3, 15].** The pooled RMS is carried by the 2.8b row's two sub3_mid cells (a four-read SD near 38 if the members sit near 189) over 61 cells at SD 8–14. On the sealed axis (5.38 / 10.10 / 14.80 / 19.52 / 28.61 / 41.69) that reads the realized α of this experiment's rule at ≈ .000 — **CALIBRATED** wherever σ̂_s lands on the grid, because the record's α never exceeds .007: **INFLATED is unreachable on this record** (it needs α ≥ .05 somewhere on the axis) and only OFF-GRID (σ̂_s > 41.69) escapes, which needs a four-read SD near 40 on most cells. T* = T_sym + .0008 ≈ .045.

## Worlds and licence cells (every cell the analyzer distinguishes; one called)

| cell | probability |
|---|---|
| **SURVIVES · CALIBRATED — THE CALL** | .78 |
| SURVIVES · OFF-GRID | .02 |
| SURVIVES · INFLATED | .00 (unreachable on the sealed grid: α ≤ .007 at every axis point) |
| NOT-SURVIVED · SIZE-ONLY (T_sym ≥ .01, p ≥ .01) | .07 |
| NOT-SURVIVED · SIGN-ONLY (p < .01, T_sym < .01) | .03 |
| NOT-SURVIVED · INSIDE | .02 |
| UNDETERMINED | .00 (unreachable from a finished campaign — freeze F-4) |
| INSUFFICIENT_DATA | .08 |

SURVIVES in total .80. The INSUFFICIENT_DATA routes, named: the count tolerance (per rung 15, Σ 120) exceeded on one of the twelve re-reads — the likeliest, ≈ .03 (Experiment 5's worst cross-class unit was 8 / 57; within one class the drift should be a third of that); a tensor-digest mismatch, ≈ .01 (the manifest is Experiment 5's, pinned); an environment-side kill leaving a partial tree that is not resumed before the analyzer, ≈ .03; a non-finite read, ≈ .01 (Experiment 5 read all six finals and six 142000s finite on this class).

**Modifier (read only under SURVIVES/NOT-SURVIVED, on cells with R > M):** cells with R > M ≈ 40 [32, 48] (Experiment 5's 48 at R > P, less the cells where the small side's move lifts M past a modest R — the 6.9b row's count_div13 and arith_next, 1b's odd6, 410m's arith_next pair); signed positives (a > f: the antonym/antonym6 cells of the 1b, 410m and 1.4b rows, the 6.9b row's option rungs) ≈ 20 [15, 25], negatives (the 2.8b row's arithmetic rungs) ≈ 20 [14, 24] — **MIXED at .85**, LARGE-AHEAD .08, SMALL-AHEAD .05, THIN .02. Signed offset over those cells ≈ −.02 [−.06, +.02] (known referent −.021).

## By rung type (S7) and by rung

| type | rungs | cells | projected T_sym | tolerance | p (≥ 5 rungs) |
|---|---|---|---|---|---|
| arithmetic (sub3_mid, sub_base8, arith_next, add3_mid, add_base8, count_div13, sub4_mid) | 7 | ≈ 33 | +.060 | [+.035, +.090] | ≈ .01 [.002, .06] |
| option (antonym, antonym6, median5, median7, odd6, odd_one_out) | 6 | ≈ 30 | +.028 | [+.010, +.050] | ≈ .05 [.01, .30] |
| string | 0 | 0 | no T | — | — |

Per rung, mean c_sym over its cells (Experiment 5's block sign known): sub3_mid +.27 [+.20, +.34] (3 cells; the two 2.8b cells at ≈ .41); sub_base8 +.08 [+.05, +.11]; add3_mid +.04 [+.02, +.06]; antonym +.04 [+.02, +.07] (11 cells); odd_one_out +.04 [+.01, +.06] (1); arith_next +.03 [+.01, +.05] (12); antonym6 +.03 [+.015, +.045] (14); median5 +.02 [0, +.05] (4); add_base8 +.015 [−.01, +.04]; median7 +.01 [−.02, +.04] (1); sub4_mid 0 [−.01, +.01] (1); odd6 −.01 [−.04, +.01] (5); count_div13 −.03 [−.05, −.01] (1). **Disconfirmer by type:** either type at ≤ +.01 — the excess would then be one type's alone; the projection says both survive the symmetric window.

## Secondaries

- **S1 — by row, and outside the 2.8b row.** Rows as the primary's table. Outside the 2.8b row (45 cells): T_sym ≈ .024 [.010, .040] (12 items [5, 20]), its own rung-block p ≈ .05 [.005, .30] — the excess outside the row is real in size but rests on antonym/antonym6 at 1b and 410m and may not reject on its own; the SURVIVES licence will quote ≈ 12 items. Experiment 5's referents (.117 the row; .0112 outside the row and the antonym rungs) beside.
- **S2 — the target swap.** Experiment 5's R − P with f replaced by f_B: T ≈ .053 [.050, .056] (the same bytes, one host class); by n₁₄₂₀₀₀: ≈ .048 [.040, .056] (sub3_mid's two cells lose ≈ .15 each, arith_next's gain ≈ .05 each, sub_base8 lose ≈ .04); by n₁₄₁₀₀₀ / n₁₄₀₀₀₀: ≈ .040–.050 — the range across the four targets ≈ .010 wide [.005, .020], its floor ≈ .040 [.032, .048]. The designation sensitivity of T_sym (each member the target, the other three the window): range width ≈ .010 [.004, .020]. Loss mismatch δ_j per side: for the four larger sides +.0004 to +.003 nats growing with distance from the final (142000 → 140000); 410m ≈ −.0014 to −.003 (its 142000 is the better checkpoint); 160m ≈ −.02 to −.04.
- **S3 — the two sides' wobble.** Q (mean over the three members of |f_B − n_j|) over live cells: mean ≈ 14 [9, 22], SD ≈ 16 [10, 25] (sub3_mid's 75 inflates it) — against P's 12.4 / 13.6: the small side's wobble comparable to the large side's, the belief of §2; σ̂_s as above. The loss displacements ℓ_s(member) − ℓ_s(final) per side as in S2; the large side's bracket residuals and window displacements are Experiment 5's record.
- **S4 — Experiment 5's rule calibrated.** At σ̂_s ≈ 13 its realized α interpolates to ≈ .015 [.000, .030] (between the record's .000 at σ_s 10 and .025 at 15) against its nominal .01, with null mean ≈ +.002 and T* ≈ .051; this experiment's α ≈ .000 with T* ≈ .045. **What the "one un-averaged read" disclosure was worth: a factor of ≈ 1.5 on α, not the .44–.997 the higher grid points show** — disconfirmer: σ̂_s ≥ 20 pooled (then Experiment 5's α ≥ .44 and the disclosure was load-bearing).
- **S5 — modifier.** As above: MIXED, ≈ 40 cells, ≈ 20 / 20, offset ≈ −.02.
- **S6 — the ledger with the window.** Fraction of live cells whose small-side clear status is constant across the four reads ≈ .85 [.70, .95] (the finals sit far from their bars on most live rungs; the exceptions on odd6 and median5 at 1.4b/6.9b, arith_next at 1b/410m). The 2.8b row's S-AHEAD cells stable across all four reads on 8 of 8 [6, 8] (sub3_mid at ≥ 150 still ≫ 4–8); the L-AHEAD cells (antonym6 × 1.4b and 1b) stable on ≥ 4 of 5 [3, 5]. 1.4b count_div13 (not live; 4 at the final, 5 at 142000): ≤ 30 at both 141000 and 140000 [0, 30] — the anneal itself lost it well before the end; disconfirmer: ≥ 40 at 140000 (the loss inside the last 2,000 steps).
- **S8 — the one-member reading on Experiment 5's bytes.** T₁ ≈ .046 [.035, .056] (graded lightly); T_sym − T₁ ≈ −.002 [−.010, +.006] — the two new members and the own-box reads subtract a little more, not a lot.
- **S9 — the spike pair excluded.** T_sym without (2.8b, 12b) ≈ .035 [.022, .048], p ≈ .001 [.0002, .010] (Experiment 5's .0417 / .00037 beside); the verdict cell unchanged at .90.
- **S10 — forms.** Naive (R − ½(P + Q))/500 ≈ .052 [.043, .060]; conservative (R − max(P, Q))/500 ≈ .040 [.030, .050]; the subtracted-sign placebo ≈ T_sym ± .008; every p < .01 at .85 each. The grid's null means at σ̂_s ≈ 13: 5b −.0008, naive −.0006, Experiment 5's +.002.
- **S11 — cross-box drift within the A100 class, as a claim with its disconfirmer.** *Claim:* the same host class reproduces Experiment 5's reads to within a third of the Mac-vs-A100 drift — byte-identical continuations on ≥ 8 of 12 units [6, 12], per-rung |Δ| ≤ 3 on every unit, Σ|Δ| ≤ 15 per unit [0, 40], |Δℓ| ≤ 2e-5 [0, 1e-4] — gate 1 PASS at .92. *Disconfirmer:* any unit with Σ|Δ| > 40, or byte-different continuations on more than 10 items of one rung — the class is not one stack, and gate 1's tolerance (pinned from one cross-class measurement) was the wrong instrument for a within-class comparison.
- **S12 — cells newly live through a member.** ≈ 3 [0, 10], all on option rungs of the two smallest sides (160m antonym6 at 99 at 142000 against a final of 77 is the shape); not added (dial f).

## Budget

24 units ≈ 8,100 s of scoring (6.9b 4 × 840, 2.8b 4 × 466, 1.4b 4 × 270, 1b 4 × 185, 410m 4 × 175, 160m 4 × 92) + setup, thermal screen and the scratch-only preflight ≈ 35 min → **≈ 3 h [2.5, 4.5] on the box, ≈ $4 [$3, $7]** at $1.08/h; one false start adds ≈ $2.

## Process

No number above was computed on sealed data, and no 5b statistic was computed on Experiment 5's committed bytes. Every quantity that grades this projection is produced by the analyzer once, on Michael's word, from the committed 24-unit campaign.
