# Experiment 2e — Design Doc: The Floor as a Covariate — Does the Raw Sampled Rate at 410m/1b Rank 2c's Outcome Once the Threshold Is Removed?

**Status: §10 DIALS RULED by Michael 2026-08-22 ("dials as
recommended — build and freeze"): a F1 primary; b AUC on the
rising/flat label, Spearman the named secondary; c ε = half a draw;
d 2d's bars and tree unchanged; e pilot replication non-gating; f B0
printed beside F1 and named in the licensed sentence, not a PASS
conjunct; g the §2 disclosure repeated verbatim in the verdict record
and in any licensed sentence. Build + freeze in one session
(2026-08-22) per §11; freeze finding F-1 and doc slips (a)–(g)
RATIFIED by Michael the same day ("F-1 ratified, slips as
recommended — apply and tag") and applied below; FROZEN, tag
`exp2e-preregistered`. Analysis-only: no model is loaded, nothing is
sampled; every input is a committed 2d or 2c artifact. Session 1
(design) was written 2026-08-22 at Michael's request after Exp 2d
closed FAIL.**

Lineage: 2c (probe ladder, FAIL) → 2d (sampling ladder, FAIL under a
declared-underpowered status) → 2e. 2d applied a model-free format
floor as a *threshold*: a rung's predictor score was zero unless its
sampled rate cleared the floor by a binomial bar, and 33 of 34 rungs
read zero. That rule was chosen so a format-only model would enter
every rung as zero, and it did its job; it also erased the
predictor's dynamic range — the raw rates span four orders of
magnitude across the battery (antonym .157, reversal 0) and none of
that ordering reached the statistic. 2e asks the question a reviewer
of 2d asks first.

## 1. The question

**Does the sampled rate at 410m/1b, adjusted for the format floor as
a covariate rather than cut at it as a threshold, separate the rungs
of 2c's battery that rise above the floor by 12b from the ones that
do not, and does it rank the corrected ascent?** Two readings of a
null: if the floor-adjusted rate still carries nothing, 2d's FAIL is
about the 1B Pythia sampled channel, not about 2d's rule, and a
second model family is a long shot. If it carries signal, 2d's null
was the threshold's doing and the from-below story is alive at this
scale.

## 2. What 2e inherits, what it changes, and what it cannot be

**Inherited, frozen, sha-pinned:** 2d's main tier — 68 cells, 32,000
draws each, re-tallied from raw bytes by 2d's own frozen loader; 2d's
pilot tier (68 cells, 4,000 draws, seed 1000) as an independent-seed
replication; 2d's floor table (majority share, raised to 1/n on the
six option-listing rungs; first-digit-run criterion disclosed on two
rungs); 2c's outcome (the 11/23 rising/flat label and the corrected
ascent) through 2d's loader with its known-answer gate; 2c's
family-block permutation group and family-cluster bootstrap; 2d's
verdict record as the comparison referent (AUC .5455, block p .6675,
CI [.5000, .6667]).

**Changed:** the predictor functional only. No threshold; the floor
enters as a covariate.

**What 2e cannot be: a forecast, or even 2d's kind of test.** 2d's
outcome was known; 2e's predictor inputs are known too — every
per-rung tally is in 2d's committed verdict record, and the designer
of this document has read them alongside the outcome. The
preregistration therefore protects against exactly one thing: picking
the functional after computing its correlation. It does not protect
against a functional chosen with the tallies in view, and the doc
says so. Three guards are built in: the family of admissible
functionals is small and enumerated here (§5.1), one is primary and
the rest are printed; the pilot tier — a different seed, drawn before
any of this was written — replicates the primary (independent in
SEED, not in what the designer knew: its per-cell tallies were as
visible as main's, in 2d's runner logs and in `power_2d.json`'s
attested pilot predictor); and the dumbest baseline,
rank-by-floor-alone, is reported beside every result (§8). A PASS licenses a sentence about 2d's rule, not about
Prediction 2.

## 3. The matrix

Nothing is sampled. Inputs: 2d's `results/main/<size>_trained/<rung>.json`
+ `.draws.jsonl.gz` (68 cells), the same for `pilot`, 2d's
`results/verdict.json`, 2c's m4 records and `ascent_scores.json`,
the 34 item files. Every loader is 2d's, imported and sha-pinned;
2e adds no loader of its own. Model contact: none. Runtime: minutes.

## 4. Referents

- 2d's main and pilot cell records and draws files, by sha (the
  referent manifest `referents_2e.json` has 273 entries: the 272 tier
  files and 2d's `verdict.json`); the re-tally must reproduce
  each record's stored `per_seed_tallies` exactly (2d's loader
  already refuses otherwise).
- 2d's `verdict.json` by sha; 2e's comparison column must reproduce
  its primary (AUC .5455, block p .6675, CI [.5000, .6667], 2 drops)
  from the same cells through 2d's `primary_test` — the known-answer
  gate for the inherited statistic.
- 2d's floor table (`CRITERION_TRUNCATED_PIN`, `OPTION_LISTING_PIN`)
  and 2c's outcome (known-answer gate 34/34), both through 2d's code.
- The per-rung main tallies, pinned by literal in the design at the
  build (the table below is the outcome side's twin: known, disclosed):
  arith_next 831 | 531; sub_base8 710 | 723; antonym 5015 | 4368;
  odd_one_out 5324 | 5356; median5 3930 | 4481; antonym6 3616 | 3147;
  odd6 2804 | 3195; median7 2714 | 3370; hamming12 4322 | 3977;
  roman_sum7 3033 | 2461; collatz_step2 2820 | 3145; count_div13
  2250 | 2795; isqrt_gap 1795 | 2719; mod13 1668 | 1709; mod17 1624 |
  1564; mod19 1230 | 1203; mod13_comp 922 | 1353; clock24_d999 1082 |
  931; clock24 933 | 927; count_div7 652 | 838; add_base8 242 | 170;
  base13 147 | 173; quad_next 145 | 156; base12_digitsum 52 | 85;
  sub3_mid 35 | 34; add3_mid 17 | 10; sub4_mid 12 | 15; oct2dec 8 |
  13; caesar 7 | 7; base7 6 | 7; caesar_len8 1 | 3; add4_mid 1 | 1;
  reverse_string 0 | 1; rev_string7 0 | 0 (410m | 1b, of 32,000).

## 5. Operationalization

### 5.1 The predictor family (one primary, the rest printed)

For rung g at size s: rate r_gs = verified / 32,000, floor c_g,
continuity ε = 1 / (2 · 32,000) (half a draw).

- **F1 — log excess over the floor (PRIMARY, proposed):**
  x_g = mean over s ∈ {410m, 1b} of log((r_gs + ε) / c_g). The
  quantity 2d thresholded at zero, in log units and unthresholded: a
  rung sampling at exactly its format floor scores log(1 + ε/c_g) ≈ 0
  (at most .0078, at the battery's smallest floor .002), above it
  positive, below it negative. Rungs at zero draws sit at
  log(ε / c_g), ordered by their floors among themselves (a known
  artefact; disclosed, and the reason F3 exists).
- **F2 — raw log rate:** mean over s of log(r_gs + ε). No floor
  adjustment; what a naive reviewer would compute.
- **F3 — rank residual:** R_g = midrank (over the 34) of the mean
  rate over sizes, Z_g = midrank of c_g; F3_g = R_g − (â + b̂ Z_g)
  with (â, b̂) the least-squares fit of R on Z with an intercept — the
  Spearman partial's residual. Floor-adjusted without a functional
  form.
- **B0 — the floor alone:** −log c_g. The dumbest baseline (§8); if
  F1's separation is no better than B0's, the signal is the answer
  space's, not the model's.

The 1b column alone is the named replication within main; the pilot
tier (seed 1000, 4,000 draws) is the independent-seed replication of
F1 (ε there = 1 / 8,000).

### 5.2 The outcome

2d's, unchanged: the rising/flat label (11 rising / 23 flat under
the max(majority, 1/n) floor and 2c's argmax at 2.8b/6.9b/12b by the
binomial bar) and the corrected ascent (mean corrected margin over
the three eval sizes). Both through 2d's loader with its known-answer
gate.

### 5.3 Primary statistic

AUC of F1 between rising and flat rungs under 2c's family-block
permutation null (the same sampled 100,000-draw matrix 2d used, seed
0) and the family-cluster bootstrap 95% CI (10,000 resamples, seed 0,
undefined resamples dropped and counted) — exactly 2d's §5.3 with the
functional swapped, so the number sits beside 2d's .5455 on the same
scale. PASS direction AUC > .5, α = .01.

### 5.4 Named secondaries (non-gating)

- F2, F3 and B0 through the same AUC machinery; the difference
  AUC(F1) − AUC(B0) printed as the headline descriptive, with its
  cluster-bootstrap CI (paired resamples).
- Spearman ρ of F1 against the corrected ascent over all 34, block p
  and cluster CI as 2c/2d computed them; the same for F2, F3, B0.
- The pilot replication: F1 on the pilot tier, AUC and ρ, with the
  rank correlation between pilot-F1 and main-F1 across rungs (the
  predictor's own seed-to-seed stability).
- 1b-only and 410m-only F1.
- The 2c probe predictor beside F1's: its AUC on THIS label (.6008,
  2d's `probe_predictor_auc` secondary, recomputed from 2c's committed
  probe scores) and 2c's own ρ (.368, the probe against 2c's frozen
  ascent, from 2c's verdict) — two records, labelled as such.
- The 2d comparison column: 2d's thresholded predictor re-derived
  from the same cells (known-answer gate: AUC .5455 exactly).
- Per rung: r_410m, r_1b, c, F1, F2, F3, B0, label, corrected ascent
  — the whole table, so a reader can compute anything else.

### 5.5 Sensitivity (pre-declared, printed, non-gating)

ε ∈ {1/64,000, 1/32,000, 1/3,200} (the first is the primary's own ε,
repeated for reference); F1 with the majority share alone
as c_g (ruling k undone) on the six option-listing rungs; F1 with
the two first-digit-run rungs (base12_digitsum, base13) removed.

## 6. Verdict tree

1. **INSUFFICIENT_DATA** — any pinned TREE referent fails (a 2d file
   not at its sha; the re-tally disagreeing with a stored tally; the
   §4 tally table; the known-answer gates — 2c's ascent 34/34, 2d's
   primary reproduced exactly — failing). Delivered as a verdict
   record with the reasons verbatim, never raised (freeze finding
   F-1, ratified): the loaders' refusals are collected. A failure of
   an INSTRUMENT pin — 2d's code and 2c/2b/exp3's frozen files, the
   item files, the two manifests' own shas, 2d's stream map — is a
   hard error with no verdict: the instrument is not what was tagged.
2. **FAIL** — the cluster CI on AUC(F1) includes .5.
3. **PASS** — block p < .01 AND AUC(F1) ≥ .75.
4. **INDETERMINATE** — neither.

What each licenses. **PASS:** "a floor-adjusted sampled rate at
410m/1b, fixed before the correlation was computed, separates the
rungs that rise above format-guessing from those that do not on 2c's
battery; 2d's null was its threshold's" — with the §2 disclosure
attached wherever it is stated, and B0's AUC printed in the same
sentence (a PASS that B0 matches is a PASS about answer spaces). It
licenses running the same predictor on a second model family, and
nothing about Prediction 2. **FAIL:** the 1B Pythia sampled channel
carries no ordering information about this battery's ascent, with or
without the threshold; the second family is a long shot at this scale
and the essay's Prediction 2 paragraph gains one sentence saying so.
**INDETERMINATE:** reported with the CI; the B0 comparison decides
what the essay says.

## 7. Power

Not a power table. Every input is fixed; once the functional is fixed
the statistic is a constant, and the only randomness is the null's.
What stands in for power is stated honestly: the pre-specified
family is three functionals and one baseline, the primary is named,
the independent-seed pilot replicates it, and the 2d comparison is
reproduced exactly as a gate. The program's "declared underpowered in
advance" rule has no object here and is not claimed.

## 8. What the dumbest baseline achieves

- **Rank by floor alone (B0 = −log c_g):** rising rungs in this
  battery have low floors (the mid-digit rungs .006, add_base8 .028)
  and several flat rungs have high ones (hamming12 .226, collatz
  .166, isqrt_gap .164, roman_sum7 .154), so B0 may itself separate
  the classes. That is why B0 is printed beside F1 and why the
  licensed sentence names it: F1 earns nothing B0 already has.
- **Rank by raw rate (F2):** credits a large answer-space share for
  free (odd_one_out .167 under sampling is the highest raw rate on the
  battery and the rung is flat).
- **The majority emitter:** scores c_g on both sides, F1 = 0 exactly.

## 9. What 2e does not claim

Nothing about a hidden outcome or hidden draws — both were known to
the designer; nothing beyond this battery, Pythia, ≤ 12b, two-shot
prompts, 2c's criterion (first-digit-run on two rungs); nothing about
mechanism. A PASS is a statement about 2d's rule; the experiment
that would turn it into a statement about the thesis is the second
family (or Pythia's intermediate checkpoints, where the predictor is
already committed and the outcome is sealed), and it is worth
running only on a PASS here.

## 10. Dials — RULED 2026-08-22 (a–g as recommended)

a. **Primary functional — RULED F1.** F1 (log excess over the floor; proposed)
   vs F3 (rank residual; no functional form, less interpretable) vs
   F2 (raw; the reviewer's first computation, but it credits answer
   spaces). Recommend F1.
b. **Primary outcome — RULED AUC on the label.** The rising/flat label with AUC (comparable to
   2d; proposed) vs the corrected ascent with Spearman (uses the
   magnitude; 23 zeros on the outcome side). Recommend AUC, Spearman
   as the named secondary.
c. **ε — RULED half a draw.** Half a draw (proposed, = 1/64,000 at
   main's resolution); the sensitivity prints 1/32,000 and 1/3,200
   beside it.
d. **Bars and tree — RULED unchanged.** 2d's (α .01, AUC ≥ .75, CI falsifier)
   unchanged, for comparability. Recommend unchanged.
e. **Pilot replication — RULED non-gating.** Non-gating (proposed) vs a conjunct of PASS
   (pilot AUC > .5 with the same sign). Recommend non-gating, printed.
f. **The B0 clause — RULED the clause, not the conjunct.** Print B0 beside F1 and
   name it in the sentence (proposed) vs require AUC(F1) > AUC(B0) as
   a PASS conjunct. Recommend the clause, not the conjunct — the
   conjunct would make the verdict depend on a baseline's own
   sampling noise — but it is a fair reading either way.
g. **Disclosure placement — RULED yes.** The §2 paragraph is repeated verbatim in
   the verdict record and in any essay sentence a PASS licenses.
   Recommend yes.

## 11. Process

Three-session protocol compressed: this doc (session 1); build +
freeze in one session (every loader is 2d's; 2e adds the functionals,
the baseline, the comparison gate, the sensitivity and the tree, with
fixtures, full-shape worlds on synthetic tallies, a mutation battery,
and the referent manifest over 2d's 272 files + verdict.json); tag
`exp2e-preregistered`; the analyzer run once on Michael's go; tag
`exp2e-closed`. Projection sealed before the run as always, with the
same disclosure: the projection's author has seen the tallies.
