# Experiment 2d — Design Doc: The Sampling Ladder — Does the Sampled Channel at 410m/1b Forecast Which Capabilities Ascend by 12b?

**Status: CLOSED 2026-08-22 — VERDICT FAIL (tag `exp2d-closed`), read
under DECLARED UNDERPOWERED IN ADVANCE as "not detected at this
resolution". Frozen 2026-08-21 (tag `exp2d-preregistered`) after the
three-session protocol and the adversarial freeze (F-1 the halt-tree
terminal; F-2/F-3 pins; rulings m/n/o). Campaign 2026-08-21/22: pilot
363 min, main 627.7 min, argmax 13.4 min, zero stops; gate 1 clean
4/4 (128,000 production-path draws byte-identical to exp3's seed-0
streams, the item-436 fire reproduced). Primary: AUC .5455, block p
.6675, cluster CI [.5000, .6667] — 33 of 34 predictor scores are
zero; arith_next, clearing its floor at 410m only, is the one
positive. The §5.4 pair is NOT silent (sub3_mid 34, arith_next 531 of
32,000 at 1b); no percolation candidate. Projection (sealed
`d40a1cf`) HIT at the verdict level. See
`experiments/exp2d/results/VERDICT.txt` and `retrospective.md`. The
doc below is the preregistration record as frozen.**

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
| pilot, 410m + 1b | 34 | 500 | k = 8 (seed 1000) | 136,000 | yes |
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
  rehearsal cell. The pilot's seed (1000 — ruling l, 2026-08-21:
  outside every committed range on this namespace, exp3 0–3, 3c 4–15,
  3d 16–39, 3e 28–167; the session-1 choice of 100 coincided with a
  3e-committed reverse_string/1b substream) and depth (8) put it on
  different substreams; pilot and main are never pooled.
- Throughput from the 3e campaign (12-token draws): 1b ≈ 41 draws/s,
  410m ≈ 54/s. Pilot ≈ 1.7 h both sizes; main ≈ 13 h (one night);
  argmax ≈ 1 h. No eval-size model is loaded at any point.
- Resolution at k = 64: 32,000 draws per rung per size; a rung with
  zero verified draws ships as rate ≤ 1.15e-4 (two-sided CP95, the
  program's convention since 2c; ratified E). reverse_string's
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
  oct2dec, rev_string7, reverse_string: ≤ .006 at every size; floors
  ≤ .010 except base12_digitsum .038 and base13 .068 (answer '2' in
  both; ratified B, 2026-08-21 — the session-1 text listed them under
  "≤ .010"). Why '2' (freeze F-3, ruled 2026-08-21): 2c's `number`
  normalization keeps the FIRST DIGIT RUN of an alphanumeric base-12/13
  answer ('B83' → '83', '2A9' → '2'; 'AAA' passes whole), so on these
  two rungs the verify criterion is a first-digit-run match on both
  sides identically — 2c's m4 records carry counts only and the rule is
  2c's verbatim — 196 / 276 of 500 answers are not matched whole, and
  the majority floor is computed under the criterion as applied. Every
  other rung is exact-match. Pinned (`CRITERION_TRUNCATED_PIN`),
  re-derived at every load, carried per rung in the verdict record.
  Both rungs are flat at ≤ .006 under the lenient criterion and so a
  fortiori under exact match; no label moves. Bold floors are rungs whose accuracy never clears the
  majority-answer rate. The six option-listing rungs' effective floors
  are 1/n_options (ruling k): antonym .250, antonym6 .167, median5
  .200, median7 .143, odd6 .167, odd_one_out .250. **The frozen rule
  (§5.2), computed at build: 11 of 34 rungs rise, 23 do not** — under
  the majority share alone it was 13/21 (median7 and odd_one_out clear
  an option-copy floor at no size); 9 rise at 12b alone.

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

The two bars are the same test at different resolutions (freeze F-6,
disclosed 2026-08-21): at n = 32,000 the predictor clears c by
+.0006–.0057 where the outcome at n = 500 needs +.008–.048, and the
32,000 draws are 64 per item — a deterministic-per-item chance
baseline (an option copier that always takes the same position;
greedy argmax IS such a baseline on the outcome side, where n = 500
prices it) clears the predictor's bar 26–42 % of the time per rung.
The verdict's α is untouched (scores are label-blind; the block test
and bootstrap condition on them); the asymmetry is interpretive — a
predictor "above floor" is a weaker statement than an outcome "above
floor", and a spurious predictor positive on a flat rung can only
LOWER the AUC.

The predictor has no free parameter: sampler, seed, k, items,
verify, floor and the aggregation rule are all fixed here; the
battery is the whole 34.

### 5.2 The outcome (2c's ascent, chance-corrected)

The **floor** c_g is model-free, computed from the item file alone.
For most rungs it is the **majority-answer share** — the largest
share any single normalized answer string holds among the rung's 500
eval answers, the score of "always emit the most common answer." For
the six rungs whose every question LISTS the answer among a fixed
number of options (antonym 4, antonym6 6, median5 5, median7 7, odd6
6, odd_one_out 4) it is **max(majority share, 1/n_options)** — the
score of "copy one listed option at random," which the majority share
cannot see (ruling k, Michael 2026-08-21, from the build's finding
that all six were rising under the majority share alone); membership
and n_options are pinned by literal and re-derived from the item file
at every load, and the rule is applied identically on both sides.
For each eval size the **corrected argmax margin** = max(0, acc − c_g) / (1 − c_g), zeroed unless acc exceeds
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
rising and non-rising rungs. Null: 2c's exact FAMILY-BLOCK permutation
(`run/power_table.exact_block_p` — enumerated below its 5e6 guard,
sampled at 100,000 seeded draws above it; on this battery the group
is 3!·9!·4! = 52,254,720, so sampled, exactly as 2c's verdict was):
the rising-label BLOCKS of same-size families are exchanged
position-for-position while the predictor stays fixed to rung
identity. (Ratified D, 2026-08-21: the session-1 phrase "exchangeable
across rungs within families" described a different null — label
shuffles inside each family, whose group on the realized outcome has
16 elements and cannot reach p < .01 — and is struck.) One-sided, α = .01
(2c's level), the PASS direction being AUC > .5. The family-cluster
bootstrap 95% CI on AUC (10,000 resamples of families, seeded) is the
falsifier as in 2c: a CI including .5 is FAIL. A resample whose
rungs contain no rising rung, or no non-rising rung, leaves AUC
undefined: such resamples are DROPPED AND COUNTED (the drop count
and the number of valid resamples are printed beside the CI), never
imputed at .5. Seven of sixteen families carry the rising rungs
(five of them mixed; ratified C, 2026-08-21), so the drop rate is
small but not zero and is reported, not hidden.

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
  32,000 main-tranche 1b draws (two-sided CP95 ≤ 1.15e-4 — one
  verified draw already puts the bound at ~1.7e-4, so the threshold
  is a zero count and is stated as one) AND a probe margin of zero is a
  percolation-class candidate; both rungs landing there is the
  sharpest available disconfirmation of "forecastable from below"
  on this battery.
- **Argmax at 410m/1b (descriptive):** greedy accuracy on the same
  items, giving every rung its ladder reading — probe (2c), sampled
  rate (2d), argmax — at the two small sizes. For the four reversal
  cells the fp16 continuations are compared to exp3's committed
  redecode records and the diff count is printed in the record —
  descriptive, non-gating (ratified I, 2026-08-21; the §6 tree is
  gate 1 only). It also enables the
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

### 5.5 The pilot (k = 8, seed 1000) and what it decides

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
reported with the CI; no slicing. An anti-predictive result — a CI
entirely BELOW .5 — is INDETERMINATE under this tree, not FAIL (the
same shape 2c's tree had for ρ); stated here so it is read as the
tree's literal output, not an oversight (ratified K, 2026-08-21).

## 7. Power, honestly

Power is computed at build over the REALIZED outcome vector (known)
and, after the pilot, the REALIZED predictor zero set — not over an
imagined battery. The frozen procedure, built in session 2 and
RATIFIED as built (F, J, 2026-08-21; `compute_power_2d.py`):

- The alternative, class-level — a Tobit latent model: L ~ N(μ, 1),
  score = max(0, L − τ); non-rising μ = 0, rising μ = d. τ is set from
  the pilot's NON-RISING zero fraction z0/n0 (zero = pilot corrected
  predictor score 0, i.e. both sizes' margins zero — J), continuity-
  corrected, τ = Φ⁻¹((z0 + ½)/(n0 + 1)), so it is finite even at n0/n0.
  d is the fixed effect, solved by bisection on the exact population
  AUC P(S1 > S0) + ½P(S1 = S0) (ties at zero counted half) for
  AUC_true ∈ {.75, .85}; .5 is run as the α check. Ties honoured: the
  non-rising rungs in the pilot zero set are HELD at zero in every
  simulation, the other non-rising rungs draw from the positive part;
  a rising rung at RAW zero in the pilot (0 verified draws at BOTH
  sizes, 8,000 draws — J) is drawn from the alternative truncated at
  the pilot CP bound in score units, cap = max(0, (9.2e-4 − c)/(1 − c))
  — which is 0 for every rung on this battery because every floor is
  ≥ .002, so under the floor rule the pilot's raw zero set IS main's
  zero set and the "upper bound" below is tight; a rising rung raw-
  zero at one size only is not truncated. Families kept as blocks:
  every simulated battery is judged by the verdict's own code (the
  same sampled block-permutation matrix, the same bootstrap draws,
  `verdict_tree` with gate 1 clean). 2,000 simulations per target,
  seed 20260821. Power = P(PASS).
- **The declaring rule is the SYMMETRIC one (freeze F-4, ruling m,
  Michael 2026-08-21).** The Tobit as built honoured the pilot's zeros
  (flat zeros held, rising raw-zeros truncated) and the flat rungs'
  positives (non-held flat rungs draw from the positive part) but
  redrew every other RISING rung from N(d, 1) — re-silencing a rung
  the pilot already showed clearing its floor with probability
  Φ(τ − d) ≈ .30 at AUC_true .85 — although main's bar at 32,000
  draws is tighter in rate than the pilot's at 4,000, so a
  pilot-positive rung is a main-positive rung with probability ≈ 1.
  The symmetric rule completes "ties honoured" on the rising side: a
  rising rung with a POSITIVE pilot score is held positive (drawn from
  the alternative's positive part, L | L > τ); a rising rung at pilot
  score 0 is truncated at the cap computed from its OWN per-size pilot
  counts' CP95 upper bounds (the raw-zero cap generalized — 0 whenever
  those bounds sit below the floor, as they do for every count up to
  14–79 on this battery); flat rungs as before. The Tobit as built is
  printed beside it as `sensitivity_ratified_rule`, non-declaring, and
  its AUC_true = .5 row is the unconditional α check: under the
  symmetric rule the .5 row is conditional on the pilot's realized
  structure (a pilot that already separates the classes gives
  P(PASS) → 1 at d = 0 — conditioning working, not α failing).
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
  pilot resolution — 4,000 draws give CP95 ≤ 9.2e-4, above the
  disconfirmer's zero-in-32,000 bar — so a STOP would kill the
  percolation-candidate question with the primary. (iii) Gate 1 on
  the production path (128,000 draws against exp3's seed-0 bytes)
  exists only if main runs. (iv) The cost is one night.
- **The build-time envelope (G, ratified 2026-08-21;
  `power_envelope_2d.json`, 300 simulations per cell, AUC_true .85)**
  replaces the session-1 back-of-envelope. Over the realized outcome
  (11 rising / 23 flat, 7 families), P(PASS) by how many of the 23
  flat rungs the pilot places at zero and how many of the 11 rising
  rungs it places at raw zero:

  | flat rungs at pilot zero | rising raw-zero 0 | 2 | 4 | 6+ |
  |---|---|---|---|---|
  | 12 of 23 (τ +.05) | .71 → **.93** | .29 → **.45** | .00 | .00 |
  | 17 of 23 (τ +.61) | .62 → **.99** | .36 → **.80** | .00 | .00 |
  | 23 of 23 (τ +2.04) | .75 → **1.00** | .56 → **1.00** | .21 → **1.00** | .00 |

  (Tobit as built → the declaring symmetric rule; the file carries
  both columns.) Each silent rising rung ties with every flat zero
  and contributes ½ per pair. Model-free, through the verdict's own
  code with every flat rung at zero (freeze, 2026-08-21): the
  statistic PASSes with up to 5 of the 11 rising rungs silent (AUC
  .773, block p .005), is INDETERMINATE at 6 and FAILs at 7; over all
  silent subsets, 3 silent → 139/165 PASS, 4 → 196/330, 5 → 153/462,
  6 → 0. **The PASS bar's own ceiling is therefore 5–6 silent rising
  rungs; the Tobit's lower numbers were its ~30 % re-silencing on top
  of the forced set.** The declaration after the pilot is decided by
  how many rising rungs the 410m/1b sampler is silent on and by
  whether the flat rungs that are positive out-rank them; the pilot
  IS the power statement. Main runs regardless (ruling c) — a pilot zero is
  "rate ≤ 9.2e-4," and the percolation-candidate question (§5.4) and
  gate 1 need main's draws whatever the declaration says.

## 8. What the dumbest baseline achieves

- **Majority-answer emitter:** scores exactly the floor on both sides
  and enters every rung as zero — by construction it cannot produce
  a rising rung or a nonzero predictor.
- **Copy one listed option at random:** scores 1/n_options on the
  six option-listing rungs — above the majority share on every one of
  them; the floor is raised to exactly that rate there (ruling k), so
  it too enters every rung as zero.
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
  distribution, two-shot prompts, exact-match verification
  (first-digit-run match on base12_digitsum and base13, §4).
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
   1000, both sizes; committed; the frozen power procedure runs ONCE
   and prints power + the declared status (POWERED / DECLARED
   UNDERPOWERED IN ADVANCE). Main runs regardless (ruling c).
3. **Main:** seed 0, k = 64, 410m then 1b, per-rung commit
   + push by the watcher; the runner iterates the two reversal rungs
   FIRST in every tier (ruling n, 2026-08-21), so the gate-1
   comparison is the first thing main does at each size — ~5 h
   earlier than their RUNG_ORDER positions; any diff halts. The
   analysis order stays RUNG_ORDER_2D.
4. **Argmax** at 410m/1b, descriptive, after main.
5. Projection ledgered BEFORE the analyzer runs; frozen analyzer runs
   ONCE on Michael's go; verdict + retrospective; close-out.

Budget: pilot ~1.7 h, main ~13 h, argmax ~1 h, Mac mini MPS. No
eval-size model is loaded for any purpose.

## 11. Process rules carried forward

Three-session protocol; adversarial freeze with the standing
assignments (class defect; totality of the verify path over every
answer type's emission alphabet — 2d scores TWO answer types (number,
8 tokens; word, 12 tokens; ratified A, 2026-08-21) where
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
   zero count (two-sided CP95 of 0/32,000 = 1.15e-4; one draw gives
   ~1.7e-4 — figures corrected from the one-sided rule-of-three
   values under ratified E) and
   is now stated as one.

Build-session rulings (Michael, 2026-08-21, applied in place; the
build's findings A–G, I–K stay ledgered in
`experiments/exp2d/PROGRESS.md` for the freeze):

k. **Floor for option-listing rungs → max(majority share,
   1/n_options), both sides (build finding H).** Six rungs list the
   answer among a fixed number of options in the question and all six
   were rising under the majority share; "copy one listed option" is
   the dumbest baseline that actually exists there, and ruling a's
   principle applies to it identically on the outcome and the
   predictor. Effect on the realized outcome: median7 and odd_one_out
   become flat (11 rising / 23 flat; order_stat and odd_one_out become
   mixed families).
l. **Pilot seed → 1000 (build finding L).** Seed 100 coincided with a
   3e-committed reverse_string/1b substream under the shared `exp3`
   namespace; 1000 lies outside every committed range.

Freeze rulings (Michael, 2026-08-21, applied in place; the freeze's
findings F-1 … F-8 are in `experiments/exp2d/PROGRESS.md`):

m. **Power: the symmetric rule declares (freeze F-4).** The Tobit as
   built used the pilot's realized structure on the flat side only;
   the symmetric rule holds rising pilot-positives positive and caps
   rising pilot-zeros from their own counts. The Tobit is printed
   beside it, non-declaring, and supplies the unconditional α check.
n. **Run order: the two reversal rungs first in every tier (freeze
   F-5).** Gate 1 becomes the first thing main does at each size.
o. **Doc slips (a)–(f) as recommended:** §10 seed 1000; §4 + §9 the
   F-3 first-digit-run disclosure; §7 the declaring rule and the
   model-free restatement of the envelope's reading; §5.1 the F-6
   resolution sentence; §10 the run order. The freeze's code
   closures (F-1 halt-tree terminal, F-2 pins, F-3 pin) are additive
   refusals and touch no dial.

Build findings A–G and I–K RATIFIED as recommended (Michael,
2026-08-21) and applied above: A (two answer types, §11), B (the two
floor slips, §4), C (7 families, §5.3), D (the family-block null,
§5.3), E (two-sided CP95 figures, §3/§5.4/§7/j), F + J (the power
procedure as built and its zero-set definitions, §7), G (the envelope
and its reading, §7), I (argmax vs exp3 redecode printed, non-gating,
§5.4), K (anti-predictive CI → INDETERMINATE, stated, §6). No
pre-committed change is spent by any of them: nothing has run.
