# Exp 2l projection — SEALED before any intermediate 13B checkpoint loads

Committed after tags `exp2l-preregistered` and `exp2l-endpoint-sealed`,
before gate 1 or any of the 15 remaining grid points is queried. Graded
at close-out against the verdict. Inputs drawn on: x_A^(256) (2k's
sealed tier), x_B (2i's sealed OLMo-2 1B counts), the 13B endpoint
table (R_13B = 18; R_PRIMARY = the full nine, `primary_is_the_nine` =
true), the power record (A and B both POWERED at 1.000; null SD of T
.0111; block_sd_A .0070 at declare / .0068 null), and every closed
result of 2g/2h/2i/2j/2k. No intermediate checkpoint has been seen.
**Honesty note carried from §2:** 2k already measured x_A^(256) at
T .1548 on the KNOWN 7B outcome, so the verdict-level call here is
worth little; the foresight is graded on the 13B-specific texture and
the per-rung table.

**Verdict-level: BOTH.** Test A fires (the 256-draw cross-family
predictor carries to a second, sealed, same-family-as-7B outcome) AND
Test B fires (OLMo-2 1B's counts forecast its own lineage's 13B order
beyond x_A's median bucket).

**Test A — cross-family (x_A^(256) → 13B stage-1 emission order, 2g's
strata, the nine).** Point T_A ≈ .14, range [.10, .19]; p_strat < .01.
Reasoning: 2k's .1548 is the anchor; 7B→13B is one size step inside
the same lineage and recipe, so the item ordering should be largely
shared, minus a little for 5.0T-vs-4T timing differences and the
endpoint ceiling on sub3_mid/antonym/arith_next (499/486/474 of 500 —
earliness alone carries those rungs' variance). The bar sits ≈ .04
below the point — ≈ 6 block-SDs (.0070) and ≈ 4 null-SDs (.0111) — so
**the call is placed OUTSIDE the block-SD scatter around the bar**:
unlike 2i's k=64 coin-flip, a bar miss here would be a real transfer
attenuation, not sampler noise.

Named disconfirmers for A (the null bracketed in both directions):
- (A-i) T_A in [.05, .10) at p < .01 — structured but below the bar:
  the transfer to a sealed outcome attenuates what the known-outcome
  bar-clearing did not show (LINEAGE if B fires). This is 2i A-i one
  experiment later; it firing again at k = 256 would say the shortfall
  was never only density.
- (A-ii) T_A ≤ .02, p n.s. — the 7B concordance was that outcome's
  own quirk; no cross-family forecast exists at any density.
- (A-iii) T_A ≥ .25 — stronger on the sealed 13B than on the known 7B;
  would say the 13B order is MORE Pythia-like than 7B's, which nothing
  in the line predicts.

**Test B — within-family beyond A (x_B → the same outcome, 2g's strata
× x_A^(256)'s median bucket, the nine).** Point T_B ≈ .16, range
[.11, .23]; p_strat < .001. 2i's B read .2153 against 7B; the 13B
outcome is one size further from the 1B predictor, and the conditioning
bucket is now built from a denser x_A (more information absorbed before
B is scored), so attenuate to ≈ .16. Same lineage, same data mix, same
tokenizer; x_B at ceiling nowhere (2i seal: 0 items at 64/64).

Named disconfirmers for B:
- (B-i) T_B in [.05, .10) at p < .01 — the within-lineage increment
  exists but dies under the bar once the denser A-bucket has eaten the
  shared component (SHARED if A fires).
- (B-ii) T_B ≤ .02, p n.s. — beyond a 256-draw cross-family predictor
  the small same-family model adds nothing.
- (B-iii) T_B ≥ .30 — the 1B forecasts 13B better than it forecast 7B
  despite the larger gap; would need a mechanism nothing in 2i–2k
  supplies.

**Per-rung foresight for A (the table that costs something):** the
committed-fires ordering carries over — sub_base8 ≈ .42 and add_base8
≈ .42 the top loci (both on all three prior outcomes), antonym6 ≈ .20,
odd6 ≈ .17, sub3_mid ≈ .13 despite its 499/500 ceiling (earliness
still orders it), arith_next ≈ .08 (its 2k gain was thin), antonym
≈ .04 flat, add4_mid-class mid-digit rungs (add3_mid, sub4_mid) ≈
.05–.10 — sub3_mid's 130-live-item x_A^(256) column (2k's named
disconfirmer firing) should hold it above the other two mid-digit
rungs. Named per-rung disconfirmer: antonym6 BELOW .10 while odd6
clears would invert 2h's option-rung ordering.

**Secondaries.** S1 (the 64→256 ladder as a forecast): monotone
increasing, roughly .09 → .12 → .13 → T_A, increments shrinking (2k's
S2 shape). S2 (410m): T ≥ the 1b reading again (2k S6: .1695 ≥ .1548),
range [.12, .21]. S3 (2i's partials): within-alone ≈ .19; cross-beyond-
within ≈ .06 — the asymmetry favours the lineage predictor again.
S4 (matched-density increment): the lineage gap at matched draws
persists ≈ +.04–.07 (2k S3: +.054). S5 (answer prior π, sealed outcome,
non-gating): FIRST TRUE TEST of 2j's second mechanism on an unseen
outcome — project ≈ .15–.20, strongest on add_base8/sub_base8/the
mid-digit rungs; π ≤ .05 would retire the mechanism claim to a
known-outcome artifact. S6: step 0 verifies 0 items on every rung
(the preflight's step-1000 all-'!' texture says the first grid points
may be degenerate; the count outcome absorbs collapses); `main` ≥
stage1_final on the mid-digit rungs (2i's soup lift), and BELOW
stage1_final on odd6/odd_one_out (main 464/446 vs endpoint 395/328 —
wait: main is ABOVE there too; named miss risk accepted: project main
≥ endpoint on ≥ 12 of 18 R_13B rungs). S7 textures: transient
verification pervasive (ever/final 1.5–4×); at least one checkpoint-
local collapse in the log head (a rung emitting one string on all 500
— 2h's class, which OLMo-2 7B did NOT show; 13B's early grid at 1k–8k
steps is the candidate window); the reversal pair (R_EXTRA,
descriptive) shows positive raw D with 3d/3e's repeat-class/one-edit
items verifying earliest.

**Falsifiable summary:** BOTH, T_A ≈ .14 [.10, .19], T_B ≈ .16
[.11, .23]; the named alternative is LINEAGE via A-i; every
disconfirmer above brackets its test's null in both directions; the
verdict call for A stands outside the block-SD scatter around the bar.
