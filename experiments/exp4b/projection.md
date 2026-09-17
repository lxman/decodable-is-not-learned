# Experiment 4b — projection (sealed after the tag, before the analyzer)

Written 2026-09-17 after `exp4b-preregistered` (ef7c8979) and before
any placebo quantity has been computed on the real tree. Everything
below is foresight about the NULL; the observed T_4 = .6102 and every
Exp 4 number are known (design §2) and are not foresight. Two
preregistered quantities are also known and are claimed by nothing
here: S6(a)'s ladder headline and S6(e)'s pooled φ (.6131).

## What was known at sealing

- T_4 .6102 (CI95 [.325, .950]); per trajectory OLMo-2 7B .959 (9
  cells, clear indices {3,4,5,5,5,6,7,9,10} of 21), Comma .512 (9,
  {2,2,2,9,10,14,19,19,21} of 24), SmolLM3 .474 (4, {2,2,4,15} of 26),
  Pythia 2.8b .183 (4, {4,7,7,12} of 21); the 26 cells' φ run from
  −1.12 to 2.97.
- λ̂ 6.23 / 6.47 / 7.30 / 7.32: the flat pool's between-checkpoint
  excess scatter is six to seven times the item-bootstrap SE.
- Exp 4's zero-excess arm (iid per-step noise) at multiples 1 / 1.5 /
  2 / 3: realized α .019 / .144 / .246 / .264, plateauing; the
  selected-cell null mean of φ .499.
- Flat pools of 27 / 16 / 14 / 16 rungs. Exp 4's S11 trend shapes for
  the flat pool (e.g. Comma .373, .369, .384, .364, .372, .365, .367,
  .363, .338, .385, .387, .378, .370, .387, .390, .386, .383, .389,
  .392, .391): wobble around a slowly rising level, one dip — closer
  to noise around a level than to a random walk.

## The verdict call

**NOT-DISTINGUISHABLE**, p_cal ≈ .20, range [.08, .40]. The call
rests on two readings of the null's shape, both from the S11 texture
above. (i) The flat rungs' excess wobble is mostly checkpoint-specific
and mean-reverting rather than accumulating, so the null φ sits near
½ at every clear position (R-7's arithmetic; the iid regime), not at
the index fraction: null mean of T ≈ .48, range [.40, .55]. (ii) The
placebo φ inherit the real cells' spread (−1 to +3 at small x_end), so
the battery mean over 26 cells has SD ≈ .12, range [.08, .18]. T_4's
lead over the null mean is then ≈ .13, about one null SD — real in
sign, not separable at the program's α. T* ≈ +.13, interval ≈ [−.10,
+.37], covering zero from above (the F-3 sub-cell does NOT obtain:
T_4 sits above the null's mean, not below its 2.5th percentile).

**Tolerances and the named alternatives:**
- **The drift account (CALIBRATED), probability .25:** if the wobble
  accumulates (S5 lag-1 autocorrelation of increments ≥ 0 and S3's
  per-index table rising), the null mean sits at roughly the clear
  index's fraction of the grid — ≈ .30 pooled, with OLMo-2's early
  cells against a null near .2 — and T_4 is a strong lead: p_cal <
  .01, T* ≈ +.30. This is the cell the design was built to detect;
  the S11 texture argues against it, which is why it is the
  alternative and not the call.
- **MARGINAL, probability .25:** the null mean ≈ .40 with SD ≈ .10
  (a mix: mild accumulation, or a smaller spread than the real cells
  suggest); p_cal in [.01, .05).
- **NOT-DISTINGUISHABLE, probability .50** — the call.
- Bar tolerances (F-2's resolution is .001–.002; the tolerances here
  are foresight tolerances, not Monte Carlo ones): p_cal in [.04, .06]
  is "at the .05 bar" and grades neither MARGINAL nor
  NOT-DISTINGUISHABLE as a miss; p_cal in [.008, .012] likewise at .01.
- The lower disconfirmer of the call: p_cal > .50 (the null's mean at
  or above T_4 — the placebo φ systematically above ½, which no
  account here predicts). Probability .05.

**α_placebo ≈ .30, range [.20, .45]** — the plateau Exp 4's arm
reached by multiple 3 (.264), read at the real scatter: the LEADS rule
fires on roughly a third of null batteries. α_iid (the observed-λ̂ arm)
≈ .27, range [.20, .35]. **S1 reads "same shape"** (the two null means
within .05): probability .55; "drift-like" .25; "above-iid" .15;
"below-iid, S3 not rising" .05.

**Per trajectory (p_cal,M):** OLMo-2 7B ≈ .03, range [.005, .10] — the
one trajectory likely below .05 (T .96 against a null near .5 over
nine cells); Comma ≈ .45 [.30, .60]; SmolLM3 ≈ .50 [.30, .70]; Pythia
≈ .85 [.65, .97] (its T .18 sits below the null). **Naming rule:**
one trajectory qualifies (OLMo-2), so the licensed sentence, in any
world, names OLMo-2 7B alone; probability that two or more qualify
.20.

**Per type:** arithmetic ≈ .22 [.10, .40]; option ≈ .30 [.15, .50];
string ≈ .35 [.15, .60] (four cells); no type at p < .05 (probability
.75).

## Secondaries (graded; no α)

- **S3 (the null's shape):** null mean of φ per clear index flat in c
  at .45–.55 with per-index SD .5–.9; the pooled c/(G−1) bins within
  .10 of each other; "rising" (the S1 conjunct) does NOT fire
  (probability .70). The per-cell calibrated excess: OLMo-2's nine
  cells +.3 to +.5 (quantiles ≥ .75), Pythia's sub3_mid ≈ −1.6
  (quantile < .05), Comma's cells straddling zero.
- **S4 (scatter ratio):** ≈ 1.0, range [.7, 1.4] per trajectory; the
  rising rungs' pre-clear wobble no larger than the flat rungs'.
- **S5 (lag-1 autocorrelation of flat-rung increments):** NEGATIVE,
  ≈ −.35, range [−.5, −.1] per trajectory (mean-reverting wobble:
  increments of noise around a level correlate at −½). The
  disconfirmer: ≥ 0 on three or four trajectories, which is the drift
  account's signature.
- **S6 with site 0 excluded (b)–(d), unknown:** (b) twins fall by the
  site-0 share (≈ .08 at 12–13 sites): option rungs .33–.37, clock
  formats .26–.32, the rest .05–.12; (c) the references' mutual
  ceiling .13–.24, OLMo-2 × Comma and Pythia-12b × OLMo-2 the two
  highest; (d) within-family .28 at step 1000 → .46 at 143000,
  monotone in the log head.
- **S7:** (a) clears-and-stays T .5815 against its matched null:
  p ≈ .25, the same cell as the primary; (b) best-site T .5785 against
  the primary null: reported without p.
- **S8:** the real cells' curves sit at quantiles .6–.9 on OLMo-2 from
  the second grid point on; Pythia's and Comma's curves cross .5.
- **Gates 1–6 PASS; feasibility:** every trajectory carries ≥ 3
  eligible placebo rungs (the one-sided 2-SE bar under real drift
  admits roughly half of each flat pool: P_M ≈ 13 / 8 / 7 / 8, range
  ±4 each); no floor refusal (probability .95).
- **F-2:** p_cal more than 3 SE from both bars (probability .85).
- **Runtime:** 15–25 min.

## Honesty note

The verdict-level call is a coin weighted by one texture reading (the
flat pool's series look mean-reverting). Foresight is graded on the
null's mean and SD, S5's sign, S3's flatness, α_placebo against α_iid,
the per-trajectory naming outcome, and S6 (b)–(d). If the drift
account obtains, the projection's mechanism (not only its point) was
wrong, and the retrospective should say so.
