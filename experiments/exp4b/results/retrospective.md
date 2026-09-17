# Exp 4b retrospective — grading projection e3f7c549

The projection was sealed 2026-09-17 after the tag
`exp4b-preregistered` (ef7c8979) and before any placebo quantity had
been computed on the real tree. The analyzer ran once, 2026-09-17
14:43–14:52 (9 min 6 s), on the clean tree at 8842c8f4; the verdict is
committed at 4abb019e and tagged `exp4b-closed`. Everything graded
below is read from `verdict.json` and its two attested companion
records; the three comparisons against Exp 4's frozen S8 are marked as
post-verdict reads of committed bytes.

Design §2's caveat governs every line: every input was committed and
known, including to the designer. The null was the only unknown, and
the null is what is graded.

## Verdict level — HIT on the world, the p and the null's mean; the null's SD MISSED by a factor of two; the mechanism MISSED

**NOT-DISTINGUISHABLE.** p_cal **.2516** (2,516 of 10,000 placebo
batteries at or above T_4 = .6102; Monte Carlo SE .0043, 46 SE from
the .05 bar), placebo null mean **.4357**, SD **.2465**, q95 .813,
q99 .937; T* **+.1745**, interval [−.265, +.695], covering zero; the
F-3 sub-cell does not obtain (p_low .7485).

| quantity | projected | observed | grade |
|---|---|---|---|
| world | NOT-DISTINGUISHABLE (.50) | NOT-DISTINGUISHABLE | HIT |
| p_cal | ≈ .20 in [.08, .40] | .2516 | HIT, point +.05 |
| null mean of T | ≈ .48 in [.40, .55] | .4357 | HIT, point −.04 |
| null SD of T | ≈ .12 in [.08, .18] | .2465 | **MISSED ×2** |
| T* | ≈ +.13 | +.1745 | HIT |
| T* interval | ≈ [−.10, +.37] | [−.265, +.695] | MISSED (width ×2, from the SD) |
| F-3 sub-cell | does not obtain | does not obtain | HIT |
| lower disconfirmer (p_cal > .50) | .05 | not fired | — |

The call and its point came in. The reasoning under it did not. The
projection read the flat pools' S11 series as "noise around a level",
put the null φ near ½ at every clear position, and got the battery SD
from the real cells' spread. What the record shows instead:

- **The null φ depends steeply on the clear index.** Pooled by
  clear-index fraction: **−.44** in [0, .2), then .70 / .75 / 1.04 /
  .65. Cells that clear at the second or third grid point draw placebo
  φ centred well below zero with SD 2–2.6 (Comma c = 2: mean −1.26);
  cells that clear from mid-grid on draw placebo φ centred at .7–1.0.
  The pooled .44 is the average of those two regimes, not a level near
  ½ that every cell shares. The projection's S3 line ("flat in c at
  .45–.55, bins within .10, rising does NOT fire") MISSED outright; the
  S1 conjunct fired with Δ +1.09 between the first and last bins.
- **The shape is neither of the projection's two accounts.** The drift
  account as written put the null at the clear index's fraction of the
  grid (≈ .30 pooled) and made T_4 a strong lead. The flat rungs'
  excess does accumulate — S1 reads **'drift-like'** — but it is
  front-loaded: from a fifth of the way through the grid on, an
  eligible flat rung's excess over the pool sits at .7–1.0 of its
  endpoint level, so a mid-grid clear index inherits a null φ near 1,
  not near its index fraction. (A reading of S3's table over the
  placebo rungs that passed the eligibility bar; §9 stands — S3 and S5
  say whether the drift accumulates, not why.) Accumulation raised the null where the drift account
  said it would lower it. The honesty note asked the retrospective to
  say so if the mechanism was wrong: it was, and the verdict call
  survived because two errors offset — a null mean the projection got
  right for the wrong reason, and an SD twice the projected size that
  moved p_cal the other way.
- **The SD.** Placebo batteries draw 26 cells with replacement from
  eligible pools of 11 / 6 / 5 / 4 rungs (Pythia / SmolLM3 / Comma /
  OLMo-2); a battery carries 5–12 distinct rung names, 8.8 on
  average. Nine OLMo-2 cells drawn from four rungs and nine Comma
  cells from five do not average like 26 independent cells. The pools
  are also narrow in kind: OLMo-2's four eligible flat rungs are all
  arithmetic and Comma's are four arithmetic and one string, while
  four of OLMo-2's nine real cells and three of Comma's are option
  rungs. The projection's SD treated them as if
  they did. Feasibility itself was projected correctly (every pool
  inside its ±4 range, all four below the point: 11 / 4 / 6 / 5
  against 13 / 8 / 7 / 8), and the consequence for the SD was not
  drawn from it.

## Calibration — MISSED below on both α, S1's reading MISSED

- **α_placebo .1171** (1,171 LEADS of 10,000 null batteries; 8,828
  UNDETERMINED, 1 FOLLOWS; every battery in the exact-flip regime)
  against ≈ .30 in [.20, .45]: MISSED below. Exp 4's frozen rule fires
  on one placebo battery in nine — above .05, so the R-7 bound was
  warranted, and well under the third the projection read off Exp 4's
  plateau.
- **α_iid .170** at the observed λ̂ (p_iid .383) against ≈ .27 in
  [.20, .35]: MISSED below. The extended grid shows why the plateau
  was the wrong anchor: P(LEADS) **.205 / .213 / .167 / .162** at
  multiples 4 / 6 / 8 / 12 (Exp 4's arm: .019 / .144 / .246 / .264 at
  1 / 1.5 / 2 / 3). The rule's false-positive rate peaks near a
  multiple of 3 and then falls as the null's SD grows (.32 → .56) and
  the sign-flip p stops reaching .01. The iid null mean stays at
  .50–.51 at every multiple.
- **S1 reads 'drift-like'** (placebo mean .064 below the iid arm's,
  past the .05 tolerance, with S3 rising) against 'same shape' at .55:
  MISSED; the projection had 'drift-like' at .25.

## Per trajectory — 2 of 4, and the naming rule MISSED

| trajectory | T_obs | null mean (SD) | p_cal,M | projected | grade |
|---|---|---|---|---|---|
| OLMo-2 7B | .959 | **.835** (.152) | **.223** | ≈ .03 [.005, .10] | **MISSED** |
| Comma v0.1 | .512 | −.060 (.569) | .161 | ≈ .45 [.30, .60] | MISSED below |
| SmolLM3-3B | .474 | .423 (.581) | .470 | ≈ .50 [.30, .70] | HIT |
| Pythia 2.8b | .183 | .666 (.698) | .781 | ≈ .85 [.65, .97] | HIT |

**Naming rule: zero trajectories at p_cal,M < .05** (projected: OLMo-2
alone; "two or more" at .20). MISSED, and this is the miss that
matters for the record. OLMo-2 7B was the trajectory that carried
Exp 4's licence condition (T .959, p₊ .0039), and the projection
expected it to be the one survivor. Its four eligible flat rungs,
given its own clear indices ({3,4,5,5,5,6,7,9,10} of 21), produce a
null centred at **.835** with SD .15: the task-specific lead over that
is +.124. OLMo-2 is also the one trajectory where the flat rungs'
increments do not mean-revert (S5 −.02; the other three −.24 to −.54)
— the random-walk trajectory is the one whose null sits highest. The
four nulls run from −.06 (Comma) to .84 (OLMo-2): there is not one
null, and the pooled .44 describes none of the four trajectories.
Comma is the mirror case — early clear indices (three cells at c = 2)
put its null below zero, so its T .51 stands +.57 above its null
mean, at p .16 against an SD of .57.

Per type: arithmetic p **.392** against ≈ .22 in [.10, .40] — HIT at
the range's edge. Option: **no p printed** — the type-matched null
does not cover Comma or OLMo-2 (no eligible option placebo rung on
either), and the analyzer refused rather than compare across
constructions: ungradeable, and the refusal is correct. String: p 1.0
from a null of SD 0 — one eligible string placebo rung per trajectory,
both contributing trajectories flagged `deficit: true`, every battery
the same T (.926): ungradeable, and see process note 3. "No type at
p < .05" (.75): HIT.

## Secondaries

- **S3 per-cell calibrated excess — 1 of 3.** OLMo-2's nine cells
  projected at e +.3 to +.5, quantiles ≥ .75: MISSED — e runs −1.14 to
  +2.02; two cells sit at quantile 1.0 (add_base8, antonym6), odd6 at
  .7475, sub3_mid at 0.0, the other five at .24–.50. Pythia's sub3_mid
  e −1.99 against ≈ −1.6, quantile .089 against < .05: point close,
  quantile MISSED narrowly. Comma's cells straddle zero (e −.35 to
  +1.59, quantiles all .40–.60): HIT — with the texture that a
  five-rung pool resolves quantiles in fifths, so all nine Comma cells
  land on .4 or .6.
- **S4 scatter ratio — 2 of 4.** Comma 1.07 and OLMo-2 1.18 inside
  [.7, 1.4]; Pythia **2.28** above it and SmolLM3 .66 just below;
  pooled 1.33. On Pythia the rising rungs wobble twice as hard before
  they clear as the flat rungs do over the whole grid — the one
  trajectory where the placebo null may be too narrow per cell, and
  the one whose p (.78) is furthest from any bar.
- **S5 — sign 4 of 4, range 2 of 4.** Mean-of-rungs lag-1
  autocorrelation: Comma −.402 and Pythia −.245 inside [−.5, −.1];
  SmolLM3 −.537 just below; **OLMo-2 −.023** above. The disconfirmer
  (≥ 0 on three or four) did not fire. The projection took S5's sign
  as the test of wobble against drift; the record shows negative
  increments' autocorrelation and a drift-like null together. The two
  are compatible when the accumulation happens in the first few grid
  steps and the wobble is what follows.
- **S6 (b) twins, site 0 excluded — partly.** Per-trajectory means
  .171 / .144 / .145 / .121 (Exp 4's frozen .240 / .216 / .211 / .194:
  a drop of .066–.073, the site-0 share, against the ≈ .08 projected —
  HIT). Clock formats .27–.35 against .26–.32: HIT within .03. Option
  rungs against .33–.37: MISSED as a band — antonym, antonym6 and odd6
  sit at .25–.40 on Pythia, OLMo-2 and SmolLM3 but .13–.28 on Comma,
  odd_one_out at .15–.30, and median5/median7 at .04–.10 with the
  arithmetic rungs. The rest: medians .08–.14 inside .05–.12 or near
  it, with add_base8 at .20–.26 the outlier on every trajectory.
- **S6 (c) ceiling — MISSED above, ordering half HIT.** Pair means
  over the 34 rungs **.286–.369** against .13–.24. OLMo-2 × Comma is
  the highest (.369) as projected; the second is OLMo-2 × SmolLM3
  (.348), with Pythia-12b × OLMo-2 fourth (.324); SmolLM3 × Pythia-12b
  the lowest (.286). Post-verdict read: Exp 4's frozen all-rung pair
  means are .341–.421, so excluding site 0 lowers every pair by
  ≈ .05, as it should. The projection anchored on the .21–.31 band
  quoted in Exp 4's retrospective, which the frozen record's all-rung
  pair means do not reproduce — **an unreconciled figure in a closed
  retrospective, flagged for Michael** (the frozen `verdict.json` is
  unaffected).
- **S6 (d) within-family — HIT on shape, points .02–.04 high.** Pythia
  2.8b against 12b: **.302** at step 1000 → **.496** at 143000 against
  .28 → .46; monotone through the log head and beyond, one .001 dip at
  100k. Exp 4's frozen .360 → .538 falls by the same .04–.06.
- **S6 (a), (e):** known before the tag, graded on nothing (ladder
  .196 → .315 over 70m → 12b, ρ with log parameters .976; pooled
  max-over-pairs φ .6131).
- **S7 — cell HIT, point MISSED.** Clears-and-stays T .5815 against
  its matched null (mean .532, SD .253): p **.459** against ≈ .25; the
  same cell as the primary, T* +.049. Best-site T .5785 printed
  without a p, as designed.
- **S8 — 1 of 2.** OLMo-2's curves projected at quantiles .6–.9 from
  the second grid point on: MISSED — they start at 1.0 and mostly decay:
  sub3_mid ends at 0.0, quad_next touches 0.0 and ends at .24, antonym and odd_one_out
  end at .25, arith_next and sub_base8 at .50, odd6 at .75; add_base8
  holds 1.0 throughout and antonym6 ends there.
  Pythia's and Comma's curves cross .5: HIT (Pythia's four all decline
  from 1.0 to .09–.37).
- **Bookkeeping — 4 of 5.** Gates 1–6 PASS; feasibility inside every
  range; no floor refusal; F-2's "more than 3 SE from both bars" HIT
  at 46 and 56 SE. Runtime 9 min against 15–25: MISSED below.

## Tally

Verdict level: world HIT, p HIT, null mean HIT, null SD MISSED, the
mechanism MISSED. Calibration 0 of 3. Per trajectory 2 of 4, naming
MISSED. Per type 2 of 2 gradeable. Secondaries roughly half. The
pattern across the misses is one error made several times: the
projection treated the null as a single distribution near ½ and the
record has four, ordered by where each trajectory's cells clear and by
whether its flat rungs' drift mean-reverts.

## What the result says

Exp 4's T = .61 does not separate from what flat rungs produce under
the same selection: a quarter of placebo batteries reach it. The lead
over the pooled null is +.17 with an interval from −.26 to +.70. The
trajectory that looked strongest in Exp 4 is the weakest reading here
— OLMo-2's .96 sits on a flat-rung null of .84. What survives,
as §6 wrote in advance: the construction account stays excluded by
Exp 4's own sign-flip reading against φ ≈ 0 (T .61, p₊ 4.9e-4; the
placebo null's 1st percentile is −.19). The agreement did not arrive
with performance; whether it led the general drift is not
distinguishable at this resolution. Exp 4's verdict is not revised;
the sentence it licenses is demoted.

The resolution is the limit, and it is a small one. The null rests on
4–11 eligible flat rungs per trajectory and its SD is .25 against a
lead of .17. A null that narrow in support cannot be sharpened by more
batteries (B is not the constraint; p_cal's MC SE is .004). It needs
more flat rungs or more trajectories — which is what 4c (6.9b and
13B, T unknown) would add on the trajectory side and nothing planned
adds on the rung side.

## Process notes (Michael's call)

1. **A pooled placebo null over heterogeneous strata should print the
   stratum nulls beside it, and the projection should be made per
   stratum first.** The four trajectory nulls here run −.06 to .84.
   The pooled p answered the preregistered question; the per-trajectory
   table is where the finding was. The projection's largest miss
   (OLMo-2 at .03 → .22) came from projecting the pooled null and
   applying it to each trajectory.
2. **An eligibility-screened placebo pool's effective size belongs in
   the power statement.** Feasibility was gated (a floor of 8 total, a
   per-trajectory deficit flag) and the pools cleared it. But nine
   cells drawn with replacement from four rungs is a different
   instrument from nine cells drawn from eleven, and nothing in the
   frozen record converted pool size into an expected null SD. 2k's
   note (the sampler-noise SD of a bar statistic belongs in the power
   record) one level over.
3. **A degenerate null must not print a p.** The string type's null
   has SD 0 — one eligible placebo rung per contributing trajectory,
   both flagged `deficit: true` — and the record prints p_cal 1.0 with
   a zero-width interval. The option type's refusal is the right
   behaviour and the string type should have met the same one: a
   deficit flag that does not gate the p it qualifies is a disclosure
   nobody will read. Inert here (per-type p's carry no α and no
   licence), and the class is 3a's.
4. **Anchor a projection on the frozen record, not on a
   retrospective's prose.** The ceiling miss came from a band quoted
   in Exp 4's retrospective that the frozen all-rung pair means do not
   reproduce. The α miss came from reading a plateau off a four-point
   grid whose next four points fall.
