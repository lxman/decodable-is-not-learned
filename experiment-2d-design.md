# Experiment 2d — Design Doc: The Sampling Ladder — Does the Sampled Channel at 410m/1b Forecast Which Capabilities Ascend by 12b?

**Status: DESIGN RULED — session 1 (design) of the three-session
design | build | freeze protocol, with the §12 dials ruled by Michael
on 2026-08-21 and applied in place (rulings c and g reversed the
session-1 proposals; three non-dial fixes applied alongside). Nothing
is built; no model is touched. Session 2 builds `experiments/exp2d/`.**

Lineage: Experiment 2 → 2b → 2c (Prediction 2, the probe ladder: the
instrument died twice to untrained-weights controls and once to an
uninterpretable correlation) and Experiments 3b → 3 → 3c → 3d → 3e
(the sampled channel, on one task, where it never died). 2d is
Prediction 2 with the instrument swapped: the from-below signal is
the frozen sampler's verified rate, not a probe margin.

## 1. The question

Prediction 2 says the order in which capabilities become reliable at
scale is forecastable from below. 2c measured the outcome side —
argmax ascent on 34 screened rungs in 16 families at 2.8b/6.9b/12b —
and a probe predictor that did not forecast it (ρ .368, block p .13,
CI spanning zero), with the cause on the record: 22 of 34 probe
margins tied at zero, and the outcome itself credited format-guessing
as capability.

On one of those rungs the program then ran the sampled channel all
the way down (3b–3e): where the probe read the answer and argmax read
zero, temperature-1 sampling read a rate, the rate forecast which
items would fire, and the instruments disagreed in a fixed order —
probe, then deep sampling, then argmax. The instrument that never
died in five experiments is the one 2c never used as a predictor.

**2d asks: does the sampled channel at 410m/1b, measured by the frozen
sampler on 2c's own eval items, forecast which of the 34 rungs rise
above format-guessing by 12b, and in what order?** A second question
rides on the same draws: the two rungs 2c flagged as probe-flat with
real ascent (sub3_mid, arith_next) — is the sampled channel also
silent on them at 1b? If it is, they are the program's first
percolation-class candidates in the wild; if it is not, the probe's
silence was the instrument.

## 2. What 2d inherits, what it changes, and the one thing it cannot have

**Inherited verbatim (frozen, sha-pinned, imported not copied):** the
34-rung battery and its 16-family map; the 500-item eval sets per
rung (2c's `battery/items`, 2b's for the twelve reused survivors);
2c's rendering (`render_prompt`, two shots), verify criterion
(`normalize_answer` under 3c's total wrapper), `MAX_NEW_TOKENS` per
answer type; 2c's m4 eval records at 2.8b/6.9b/12b (trained and
untrained twins); 2c's exact family-block permutation and
family-cluster bootstrap; exp3's sampler and stream-seed formula.

**Changed: the predictor.** A per-rung verified rate under pure
temperature-1 ancestral sampling at 410m and 1b, on the same 500
items the outcome was measured on. No probe, no split, no basis, no
activation — the whole leak class that killed 2 and 2b has no
surface here, and the sampler's contamination referent is standing
(exp3's untrained twins: 0 verified draws in 576,000).

**Changed: the floors, on both sides.** 2c's empirical untrained floor
is ~0 for every rung because an untrained Pythia emits malformed
text; a trained model that has learned only the output format scores
at its guessing rate and was credited that as capability (2c
retrospective, lesson 1). 2d uses a model-free chance floor computed
from the item file alone — the majority-answer rate over the rung's
500 eval answers — applied identically to the outcome (argmax
accuracy) and the predictor (sampled rate). It is the dumbest
baseline made executable: "emit the most common answer" scores it
exactly.

**The one thing 2d cannot have: an unknown outcome.** 2c's eval side
was queried on 2026-08-12 and its ascent table is committed, public
and known to the designers (§4 prints it). 2d is therefore NOT a
sealed forecast of a hidden outcome. It is a test of whether a
predictor with **zero free parameters** — a frozen sampler, a frozen
item set, a frozen k, a frozen floor, a frozen statistic, the full
battery with no selection — ranks an outcome the designers already
know. The preregistration protects against predictor tuning, not
against outcome knowledge, and the doc says so wherever the result is
read. The successor that restores a sealed outcome is named in §9.

## 3. The matrix

| cell | rungs | items | draws/item | draws per size | model contact |
|---|---|---|---|---|---|
| pilot, 410m + 1b | 34 | 500 | k = 8 (seed 100) | 136,000 | yes |
| main, 410m + 1b | 34 | 500 | k = 64 (seed 0) | 1,088,000 | yes |
| argmax, 410m + 1b (descriptive) | 34 | 500 | greedy | 17,000 | yes |
| outcome, 2.8b/6.9b/12b | 34 | 500 | — | — | **none — 2c's committed record** |

- Sampler: exp3's, byte-pinned; T = 1.0, no truncation, float32 at
  the probe sizes (exp3's cell policy), 16-row chunks, per-(rung,
  size, seed, item) substreams under the `exp3` namespace. Token
  budget per rung = 2c's `MAX_NEW_TOKENS[answer_type]` (6–12), the
  budget the outcome was measured under.
- **Seed 0 is deliberate.** For `reverse_string` and `rev_string7`
  the seed-0, 64-draw streams at both sizes are exp3's committed
  draws (seeds 0–3, dps 64). The main tranche regenerates them through
  2d's production path and compares byte for byte: **gate 1 on the
  production path, 128,000 draws, zero tolerance**, without a
  rehearsal cell. The pilot's seed (100) and depth (8) put it on
  different substreams; pilot and main are never pooled.
- Throughput from the 3e campaign (12-token draws): 1b ≈ 41 draws/s,
  410m ≈ 54/s. Pilot ≈ 1.7 h both sizes; main ≈ 13 h (one night);
  argmax ≈ 1 h. No eval-size model is loaded at any point.
- Resolution at k = 64: 32,000 draws per rung per size; a rung with
  zero verified draws ships as rate ≤ 9.4e-5 (CP95). reverse_string's
  committed 1b rate (1.5e-5 pooled) sits below that floor and is
  expected to read zero or one; that is the ladder's bottom, not a
  defect.

## 4. Referents — every input, a committed value

To be pinned at build (sha256 list in the doc at freeze):
- The 34 item files (22 under `experiments/exp2c/battery/items`, 12
  under `experiments/exp2b/battery/items` per 2c's
  `reuse_manifest.json`), the family map (`battery/family_map.py`,
  16 families), 2c's screen verdicts that define membership.
- 2c's m4 eval records, all 34 × 3 sizes × {trained, untrained}, and
  `results/ascent_scores.json`; 2c's `verdict.json` (ρ .368, block p
  .1305, CI (−.185, .762)) and `probe_scores.json` (the probe
  predictor, for the instrument comparison).
- exp3's sampler, stream map and the committed seed-0 draws of the
  two reversal rungs at both sizes (gate-1 referents; 3c/3d/3e pins
  by value). exp3's twin record (0 / 576,000) as the standing
  contamination referent; no new twin is sampled.
- 2c's `harness.py` (render, normalize, MAX_NEW_TOKENS), 2b's
  `models.py` (weights by revision sha), 3c's total verify wrapper.
- **The known outcome, disclosed here so no reader mistakes 2d for a
  blind forecast.** 2c's trained argmax accuracy at 2.8b / 6.9b / 12b
  and the majority-answer floor, per rung (family in brackets):
  antonym [antonym] .544/.572/.560, floor .026; antonym6 [antonym]
  .298/.286/.398, .020; median5 [order_stat] .226/.158/.262, .008;
  hamming12 [str_align] .198/.206/.232, **.226**; odd_one_out
  [odd_one_out] .162/.250/.208, .014; sub3_mid [mid_digit]
  .528/.028/.022, .014; arith_next [seq_extrap] .274/.116/.152, .020;
  count_div13 [counting] .116/.204/.204, **.158**; odd6 [odd_one_out]
  .122/.214/.188, .026; collatz_step2 [rescue_collatz]
  .154/.164/.154, **.166**; median7 [order_stat] .156/.144/.170, .010;
  sub_base8 [base_arith] .182/.104/.172, .056; isqrt_gap
  [rescue_isqrt] .146/.156/.138, **.164**; roman_sum7 [rescue_roman]
  .158/.144/.148, **.154**; add_base8 [base_arith] .088/.058/.100,
  .028; mod13 [modulus] .092/.076/.046, **.094**; mod17 [modulus]
  .052/.066/.072, **.076**; mod13_comp [modulus] .054/.060/.070,
  **.094**; add3_mid [mid_digit] .086/.038/.052, .006; mod19 [modulus]
  .056/.062/.052, **.066**; clock24_d999 [clock] .044/.058/.050,
  **.060**; count_div7 [counting] .056/.046/.050, **.100**; clock24
  [clock] .050/.050/.050, **.072**; sub4_mid [mid_digit]
  .008/.012/.024, .006; quad_next [seq_extrap] .010/.010/.016, .018;
  add4_mid, base12_digitsum, base13, base7, caesar, caesar_len8,
  oct2dec, rev_string7, reverse_string: ≤ .006 at every size, floors
  ≤ .010. Bold floors are rungs whose accuracy never clears the
  majority-answer rate: **by eye, roughly 11 of 34 rungs rise above
  format-guessing by 12b and 23 do not.** The exact split is an
  output of the frozen floor rule (§5.2), computed at build, not
  this paragraph.

## 5. Operationalization

### 5.1 The predictor (the sampled channel from below)

For rung g at size s, the **sampled rate** r_gs = verified draws /
total draws over the 500 eval items at k = 64 (one seed, 32,000
draws), verification = 3c's total wrapper over 2c's `normalize_answer`
with the rung's answer type. The **corrected sampled margin**
m_gs = max(0, r_gs − c_g) / (1 − c_g), where c_g is the rung's
majority-answer floor (§5.2), zeroed unless r_gs exceeds c_g by a
one-sided exact binomial test at α = .01 over the 32,000 draws. The
**predictor score** per rung = mean of m_gs over the two probe sizes
(2c's rule, mirrored); the 1b column alone is the named replication.
Rungs at zero tie at the bottom under average ranks.

The predictor has no free parameter: sampler, seed, k, items,
verify, floor and the aggregation rule are all fixed here; the
battery is the whole 34.

### 5.2 The outcome (2c's ascent, chance-corrected)

The **majority-answer floor** c_g = the largest share any single
normalized answer string holds among the rung's 500 eval answers —
model-free, computed from the item file, the score of "always emit
the most common answer." For each eval size the **corrected argmax
margin** = max(0, acc − c_g) / (1 − c_g), zeroed unless acc exceeds
c_g by a one-sided exact binomial test at α = .01 over the 500 items
(replacing 2c's Fisher test against the ~0 untrained floor, which is
the defect 2c's retrospective names). The **corrected ascent** =
mean over 2.8b/6.9b/12b. **Rising** ⇔ corrected ascent > 0 — that
is, the rung clears its floor at ANY of the three eval sizes; the
rule mirrors 2c's ascent, and "by 12b" in the title and §1 is
shorthand for it, not a 12b-only condition. sub3_mid (.528 / .028 /
.022) is rising under this rule by 2.8b alone, and stays so. The
12b-only split (clears the floor at 12b) is printed as a sensitivity,
non-gating. Every untrained-twin accuracy is still printed beside
it; the untrained floor is reported, not used.

2c's frozen ascent (untrained floor, Fisher) is carried as a second
outcome column for one purpose only: comparability with 2c's ρ .368.

### 5.3 Primary statistic (class-level, the sixth lesson in advance)

The realized outcome is nearly binary — about a third of the rungs
rise, two thirds do not — so the primary is the statistic that
shape can express: **does the predictor separate the rising rungs
from the flat ones?**

T = the Mann–Whitney / AUC statistic of the predictor score between
rising and non-rising rungs. Null: the rising label is exchangeable
across rungs *within families* — the exact family-block permutation
2c froze (`run/power_table.exact_block_p`, enumerated below its
guard, sampled at 100,000 seeded draws above it), applied to the
rising indicator against the predictor score. One-sided, α = .01
(2c's level), the PASS direction being AUC > .5. The family-cluster
bootstrap 95% CI on AUC (10,000 resamples of families, seeded) is the
falsifier as in 2c: a CI including .5 is FAIL. A resample whose
rungs contain no rising rung, or no non-rising rung, leaves AUC
undefined: such resamples are DROPPED AND COUNTED (the drop count
and the number of valid resamples are printed beside the CI), never
imputed at .5. Six of sixteen families carry all the rising rungs,
so the drop rate is not small and is reported, not hidden.

### 5.4 Named secondaries (non-gating)

- **Ordering, 2c-comparable:** Spearman ρ between predictor rank and
  corrected-ascent rank over all 34, block-permutation p and cluster
  CI exactly as 2c computed them; and the same against 2c's frozen
  ascent, so the sampling predictor and the probe predictor (ρ .368)
  are read against one outcome column.
- **Instrument comparison:** the probe predictor's AUC on the same
  rising label under the same null, beside the sampling predictor's.
  Descriptive: the two instruments' disagreement per rung.
- **The probe-flat-but-rising pair (the §1 second question):**
  sub3_mid and arith_next's sampled rates at both sizes with CP
  bounds. The disconfirmer of the instrument-ladder story, written
  now: a rung that rises (§5.2) with ZERO verified draws in its
  32,000 main-tranche 1b draws (CP95 ≤ 9.4e-5 — one verified draw
  already puts the bound at ~1.5e-4, so the threshold is a zero
  count and is stated as one) AND a probe margin of zero is a
  percolation-class candidate; both rungs landing there is the
  sharpest available disconfirmation of "forecastable from below"
  on this battery.
- **Argmax at 410m/1b (descriptive):** greedy accuracy on the same
  items, giving every rung its ladder reading — probe (2c), sampled
  rate (2d), argmax — at the two small sizes. It also enables the
  **from-below-performability restriction**: the primary AUC
  recomputed with the rising set restricted to rungs whose 1b greedy
  accuracy does NOT clear the floor under §5.2's binomial rule over
  the 500 items, with the count of rising rungs already performable
  at 1b printed beside it. Non-gating. It is the descriptive that
  says whether a PASS forecasts anything the small model cannot
  already perform — a skeptic's first question, answered in advance.
- **410m replication** of the primary alone; **within-family
  concordance** (dial order vs predictor order vs outcome order),
  descriptive.
- **The reversal cells' gate-1 comparison** (byte identity with
  exp3's seed-0 streams) is reported with counts; it is a gate, not a
  secondary (§6).

### 5.5 The pilot (k = 8, seed 100) and what it decides

The pilot exists for one reason: the sixth lesson. Power must be
computed over the realized tie structure of BOTH sides, and the
predictor's is unknown until something is sampled. The pilot measures
the predictor's zero set at 4,000 draws per rung. It decides nothing
about k (fixed at 64), nothing about the battery (all 34), nothing
about the statistic, and — by ruling c — nothing about whether the
main tranche runs. Its output is the input to the frozen power
procedure (§7), which fixes the power statement and the declared
status (POWERED or DECLARED UNDERPOWERED IN ADVANCE) before any
scored data exists. Main runs regardless.

## 6. Preregistered verdict tree

Precedence, mechanical:
1. **INSUFFICIENT_DATA** — gate 1 (the reversal cells' seed-0
   regeneration) differs from exp3's committed bytes in any draw.
   There is no power-based STOP branch (ruling c): a declared-
   underpowered status changes how FAIL is read, not whether main
   runs.
2. **FAIL** — the family-cluster bootstrap CI on AUC includes .5.
3. **PASS** — block-permutation p < .01 AND AUC ≥ .75.
4. **INDETERMINATE** — neither.

What each licenses, written now. **PASS:** the essay may say
exactly this — *a predictor with no free parameter, fixed before
sampling, separates the rungs that rise above format-guessing from
those that do not, on 2c's battery, whose outcome was known* — at
the within-battery, Pile-distribution, ≤ 12b scope 2c defined, with
the known-outcome caveat of §2 attached wherever it is stated; and
the instrument-ladder finding of 3b–3e generalizes from one task to
the battery. **"Prediction 2 supported" is NOT licensed by a 2d PASS
(ruling g)**; that sentence is reserved for the §9 successor with a
sealed outcome. **FAIL:** the sampled channel at small scale does not
forecast ascent on this battery at this resolution; the ladder result
stays task-local; the essay says Prediction 2's first test did not
find the signal. If the status is DECLARED UNDERPOWERED, FAIL reads
"not detected at this resolution" with the blind region stated (1c/3e
precedent), and the essay says that instead. **INDETERMINATE:**
reported with the CI; no slicing.

## 7. Power, honestly

Power is computed at build over the REALIZED outcome vector (known)
and, after the pilot, the REALIZED predictor zero set — not over an
imagined battery. The frozen procedure, to be built in session 2 and
fixed at the freeze:

- The alternative, class-level: rising rungs' predictor scores are
  drawn from a distribution stochastically above the non-rising
  rungs' by a fixed effect; the non-rising rungs that the pilot
  places in the predictor's zero set stay at zero (ties honoured);
  families kept as blocks. Power = P(PASS) under the frozen tree at
  AUC_true ∈ {.75, .85}, by simulation through the exact block test
  and the cluster bootstrap, seeded.
- **Declared-underpowered rule (1c/3e precedent):** if power at
  AUC_true = .85 is below .75, the experiment is DECLARED
  UNDERPOWERED IN ADVANCE.
- **Run-anyway rule (ruling c, Michael 2026-08-21, reversing the
  session-1 STOP proposal):** an underpowered declaration is printed
  and the main tranche runs. Four reasons, on the record. (i) Power
  bounds the miss rate, not α: a PASS at declared-low power is a
  PASS, and a FAIL declared underpowered IN ADVANCE reads "not
  detected at this resolution" — which is how 1c and 3e shipped. 2c's
  FAIL was uninterpretable because its power model was wrong and that
  was found after the data; a declaration before the data is the
  opposite case. (ii) The §5.4 second question cannot be answered at
  pilot resolution — 4,000 draws give CP ≤ 7.5e-4, above the
  disconfirmer's zero-in-32,000 bar — so a STOP would kill the
  percolation-candidate question with the primary. (iii) Gate 1 on
  the production path (128,000 draws against exp3's seed-0 bytes)
  exists only if main runs. (iv) The cost is one night.
- Back-of-envelope, to be replaced: with ~11 rising and ~23 flat
  rungs in 16 families, 6 of which carry all the rising rungs, the
  block test's effective resolution is the 2c problem in a milder
  form; if the pilot shows the predictor separating even half the
  rising rungs from the flat block, AUC .85 is plausible, and the
  permutation count over the 6 mixed families is in the tens of
  thousands. If the predictor's zero set at the pilot swallows most
  of the rising rungs too, the declaration is UNDERPOWERED and main
  runs anyway — a pilot zero is "rate ≤ 7.5e-4," not zero, and main
  has eight times the draws; the pilot's zero set is an upper bound
  on main's, which the power procedure must model as such (a
  pilot-zero rising rung is drawn from the alternative truncated at
  the pilot's CP bound, not held at zero).

## 8. What the dumbest baseline achieves

- **Majority-answer emitter:** scores exactly the floor on both sides
  and enters every rung as zero — by construction it cannot produce
  a rising rung or a nonzero predictor.
- **Uniform over the answer space:** scores below the majority floor
  wherever answers are skewed; dominated.
- **"Predict the 2c probe ranking":** the comparison secondary; it
  scored ρ .368 against the frozen outcome and is printed against
  the corrected one.
- **"Predict by answer-space size":** rungs with small answer spaces
  have high chance rates; the floor correction removes exactly that,
  which is why it is applied to both sides. Printed as a descriptive
  (|A| per rung vs predictor and outcome) so the reader can see the
  correction did its job.

## 9. What 2d does not claim

- Nothing about a hidden outcome. The outcome was known before the
  predictor was designed; 2d establishes that a zero-free-parameter
  from-below measurement does or does not rank it.
- Nothing beyond this battery, this family, ≤ 12b, Pile
  distribution, two-shot prompts, exact-match verification.
- Nothing about mechanism; "rises above format-guessing" is a
  frozen event on a frozen floor.
- **Named successor with a sealed outcome:** Pythia's 154
  intermediate checkpoints at 2.8b/6.9b/12b have never been queried;
  the training step at which each rising rung first clears its floor
  is an unknown ordinal outcome that the same predictor can be
  sealed against before any checkpoint is loaded. It is the natural
  next experiment if 2d PASSes and the wrong one to run if it does
  not.

## 10. Run plan

1. Session 2 builds `experiments/exp2d/`: loaders for the 34 item
   files + 2c's m4 records with pins; the floor rule; the predictor
   and outcome computations; the AUC block test on 2c's frozen
   machinery; the pilot-driven power procedure; the runner (pilot /
   main / argmax tiers, tier-per-process, skip-if-exists, per-rung
   commit unit); fixtures, full-shape worlds, mutation battery;
   projection template. Session 3 freezes adversarially → tag
   `exp2d-preregistered`.
2. **Pilot** (model contact, on Michael's launch word): k = 8, seed
   100, both sizes; committed; the frozen power procedure runs ONCE
   and prints power + the declared status (POWERED / DECLARED
   UNDERPOWERED IN ADVANCE). Main runs regardless (ruling c).
3. **Main:** seed 0, k = 64, 410m then 1b, per-rung commit
   + push by the watcher; the reversal cells' gate-1 comparison is
   computed as they land; any diff halts.
4. **Argmax** at 410m/1b, descriptive, after main.
5. Projection ledgered BEFORE the analyzer runs; frozen analyzer runs
   ONCE on Michael's go; verdict + retrospective; close-out.

Budget: pilot ~1.7 h, main ~13 h, argmax ~1 h, Mac mini MPS. No
eval-size model is loaded for any purpose.

## 11. Process rules carried forward

Three-session protocol; adversarial freeze with the standing
assignments (class defect; totality of the verify path over every
answer type's emission alphabet — 2d scores four answer types where
3e scored one; the floor rule's degrees of freedom; the AUC null's
conditioning; gate 1 = exp3's committed bytes on the production
path); ONE pre-committed change, UNSPENT; every zero a CP bound;
class-level power over realized structure; projection before
analysis; verbatim disclosure of every verified draw on the §5.4
pair; known-answer gates before the campaign; the known-outcome
caveat stated wherever a result is read.

## 12. Dials — RULED (Michael, 2026-08-21), applied in place

Each dial with the ruling and the reason that carried it. Rulings c
and g reversed the session-1 proposals.

a. **Floor rule → majority-answer rate.** Model-free, from the item
   file alone, no "declared answer space" to parse (a degrees-of-
   freedom surface the freeze would otherwise have to attack), and
   strictly harder on the skewed rungs — mod13's floor is .094 where
   uniform would give .077, and that skew is exactly what a
   format-only model exploits.
b. **Primary statistic → AUC over rising / non-rising; Spearman a
   secondary.** The corrected outcome is ~23 zeros and ~11 positives;
   Spearman over 34 with that many ties on both sides is 2c's
   seven-effective-blocks problem re-run with a different instrument.
   AUC is the statistic the realized shape can express — the sixth
   lesson applied before the data.
c. **Underpowered pilot → RUN ANYWAY with the declaration printed
   (reverses the session-1 STOP proposal).** Reasons (i)–(iv) in §7.
   There is no power-based STOP; INSUFFICIENT_DATA is gate 1 only.
d. **PASS bar → AUC ≥ .75 with block p < .01 (unchanged).** The bar is
   not moved to buy power — dial c is the honest way to handle a
   shortfall; the binding constraint is the block p over 6 mixed
   families, not the point estimate, so .70 buys little and costs
   comparability with 2c's strictness.
e. **k → 64 main / 8 pilot.** Gate 1 is free only at k = 64 / seed 0
   (exp3's committed streams are 64 draws per item per seed; k = 128
   would leave half of every substream uncovered). Halving the
   resolution floor to 4.7e-5 does not move an AUC carried by rungs
   with rates orders of magnitude above it. If 2d lands INDETERMINATE
   with rungs at one or two draws, a k = 128 deepening is the
   successor (the exp3 → 3c pattern).
f. **Argmax at 410m/1b → kept, and it carries the from-below-
   performability restriction (§5.4).** If a rising rung is already
   performable at 1b, forecasting its ascent from 1b is no feat; the
   restriction is the descriptive that says whether a PASS forecasts
   anything the small model cannot already do.
g. **Scope sentence → the narrower one.** A PASS licenses "a
   predictor with no free parameter, fixed before sampling, separates
   the rungs that rise above format-guessing from those that do not,
   on 2c's battery, whose outcome was known." "Prediction 2
   supported" is reserved for the §9 successor with a sealed outcome.
   The wider sentence buys one adjective; a reader who meets
   "supported" and then finds the outcome was known discounts the
   rest of the essay.

Three non-dial fixes applied with the rulings:

h. **§5.2 rule/prose agreement.** "Rising" = clears the floor at ANY
   of the three eval sizes (the rule as written, mirroring 2c's
   ascent); the "by 12b" prose was shorthand and now says so.
   sub3_mid is rising by 2.8b alone. 12b-only split printed as a
   sensitivity.
i. **§5.3 undefined-AUC resamples.** A cluster-bootstrap resample
   with no rising or no non-rising rung is dropped and counted, never
   imputed at .5; the drop count is printed.
j. **§5.4 disconfirmer threshold.** "Below 1e-4 at 32,000 draws" is a
   zero count (CP95 of 0/32,000 = 9.4e-5; one draw gives ~1.5e-4) and
   is now stated as one.
