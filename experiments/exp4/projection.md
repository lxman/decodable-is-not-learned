# Experiment 4 — projection (sealed before any sweep unit loads)

Written 2026-09-14 after the reference stage, power and the seal
(`exp4-reference-sealed` at 11a0edd5) and after campaign stop #1's
ruling (gate 0 excludes hidden-state 0), before the first trajectory
sweep. Everything quoted below was known at sealing and is disclosed
as design §2 requires; nothing below is an input to the analyzer.

## What was known at sealing

- **Eligibility (endpoint stage):** 26 eligible cells on 15 rungs —
  pythia_2.8b 4 of 7 (arith_next .140, antonym .117, antonym6 .069,
  sub3_mid .019; the base-8 pair and add3_mid NEGATIVE, −.05 to −.07);
  olmo2_7b 9 of 13 (arith_next .081, antonym6 .073, antonym .063,
  odd_one_out .048, quad_next .044, sub_base8 .043, odd6 .039, sub3_mid
  .027, add_base8 .019; add4_mid/reverse_string/sub4_mid/add3_mid
  ineligible, add3_mid −.042); smollm3_3b 4 of 14 (rev_string7 .052,
  add4_mid .024, sub4_mid .021, reverse_string .008; antonym6/antonym/
  sub3_mid clear at grid index 0–1 and have no window; the arithmetic
  rungs negative); comma_7b 9 of 16 (rev_string7 .087, antonym6 .069,
  clock24_d999 .062, antonym .052, sub3_mid .051, reverse_string .044,
  quad_next .019, median7 .013, odd6 .005; arith_next clears at index 0;
  add4_mid −.050, add3_mid −.025, oct2dec −.022). Flat trends: Pythia
  .261 → .354, OLMo-2 .228 → .367, SmolLM3 .383 → .382, Comma .373 →
  .396.
- **Power:** POWERED — P(LEADS | φ = .5) = 1.000, P(LEADS | φ = .25) =
  .323 (PARTIAL .669), null arm FOLLOWS .980; null SD of T .0395;
  min-detectable T .118; flips exact over 15 rungs.
- **R-7:** the zero-excess arm's realized α of the LEADS rule is .019
  at λ̂ = 1, .144 at 1.5, .246 at 2, .264 at 3, with the selected-cell
  mean φ at .499 — the ½ the fix wave predicted, reproduced on the real
  table. The LEADS licence is read against the realized α at the
  observed λ̂ (design §6).
- **Gate 0 (post-ruling, site 0 excluded):** .955 / .989 / .990 / .991
  — pass on all four. Gate 1 not yet run (the sweep's first unit).

## The verdict call

**LEADS.** T ≈ .50, range [.35, .65], p₊ < .001 (exact). The call rests
on the shape of the eligible set: the cells that carry the most
endpoint excess are late-clearing string and order rungs (rev_string7
at grid index 15 and 21, clock24_d999 19, odd6 19, quad_next 10 and 14,
median7 10, reverse_string 9, odd_one_out 9) whose pre-clear window
covers most of the grid, so most of their trend-corrected excess should
be in place before the clear (φ ≈ .7–.9); the option rungs and
arith_next clear early (index 2–7) with short windows (φ ≈ .2–.5); the
mid-grid arithmetic and order cells (sub3_mid, sub_base8, add_base8,
add4_mid, sub4_mid) are projected mixed (φ ≈ .4–.6). Cell-weighted,
that is ≈ .5.

**Named disconfirmers, both directions, with tolerances:**
- **Lower — PARTIAL:** T in (0, .25) with p₊ < .01 fires if the option
  rungs' task-specific agreement arrives WITH the clear (their windows
  are two to five grid points) and the string rungs' excess is
  back-loaded onto the last third of the grid. Tolerance: T in [.25,
  .30] is "at the bar" and read as LEADS-marginal, not a miss.
- **Upper:** T > .70 — the excess is essentially complete before the
  clear on almost every cell, i.e. the task-specific agreement
  converges long before performance. Tolerance .65–.70 is "high LEADS".
- **FOLLOWS** (p₊ ≥ .01 and CI95 upper < .25) is the construction
  account's cell; projected probability .05.
- **The R-7 cell:** LEADS with the licence condition NOT met because the
  observed λ̂ ≥ 1.5 puts the realized α above .05. λ̂ is projected at
  1.2–1.8 per trajectory (the worlds' 2–12 % bar-crossing rate implies
  that range), so this cell is live: probability .25 of the LEADS mass.

**Probabilities over the tree:** LEADS .60 (licence met .35, licence not
met at the observed λ̂ .25), PARTIAL .25, UNDETERMINED .10, FOLLOWS .05,
NO-CONVERGENCE and INSUFFICIENT_DATA ≈ 0 (26 cells; gate 0 passes;
gate 1 has reproduced byte-identically on this stack twelve times).

**Per trajectory** (each at its own p): olmo2_7b (9 cells) T ≈ .50,
p₊ < .01; comma_7b (9) ≈ .55, p₊ < .01; pythia_2.8b (4) ≈ .40, p₊ may
not clear .05 (four rungs, 16 flips); smollm3_3b (4) ≈ .55, thin. The
§6 licence condition (≥ 2 of 4 at p < .05 and T ≥ .25) is projected
MET through OLMo-2 and Comma.

**Per rung type:** string ≈ .75, option ≈ .35, arithmetic/order ≈ .50.
The per-type disconfirmer: option rungs ABOVE string rungs would say
the early-clearing tasks' agreement is front-loaded and the late ones'
is not — the opposite of the window-length reading above.

## Secondaries (descriptive; graded, no α)

- S1 (order): pooled Somers' D ≈ .3 — the late-clearing rungs also
  half-rise late; a null D with a firing primary would say the timing
  carries no rung-specific order, only a lead.
- S2 (the third instrument on 2d's question): AUC ≈ .60 on the Pythia
  ladder at 1b — the option rungs and arith_next sit high, but the
  rising arithmetic rungs carry NEGATIVE excess (below the flat pool),
  so the rung-level forecast stays under 2d's .75 bar, as the sampled
  rate (.55) and the floor-adjusted rate (.61) did.
- S3 (scale): alignment rises with size on most rungs (Spearman > .8 on
  the option rungs), the largest single step between 410m and 1b or 1b
  and 2.8b; the global-bank curve rising monotonically; site 0's
  constant disclosed.
- S4 (size-axis φ): ≈ .5 over the eleven rising rungs, coarse.
- S5: the max-over-pairs reading raises levels by ≈ .05 and leaves φ
  within ±.05 of the primary; the endpoint-best site gives a slightly
  higher T. S6: the question-end position carries smaller excess and a
  lower T. S7 (Huh's pooled construction): higher levels, smaller
  task-specific excess, T within ±.1.
- S8: twins .11–.18, the references' mutual ceiling .35–.40 per rung
  (Pythia-12b vs OLMo-2 highest); the within-family reading (2.8b vs
  12b) higher levels by ≈ .1 and the same φ within ±.1.
- S9: CKA agrees in sign with the k-NN reading on the endpoints.
- S10 (item grain): D ≈ .03, not distinguishable from zero — the
  probe's lesson from 2g at item grain.
- S11: the excess's largest single step coincides with t_clear on ≤
  30 % of cells; the count's fraction of the bar at t⁻ ≈ .6; the flat
  pool's trend concave in log tokens; per-reference leadership split
  with no single lens leading on more than half the cells.
- Calibration: λ̂ 1.2–1.8 per trajectory.

## Honesty note

The verdict-level call is cheap: the endpoint table already shows large
positive excess on late-clearing cells. Foresight is graded on T's
point and range, the per-type ordering, the R-7 cell (met or not at the
observed λ̂), and the secondaries.
