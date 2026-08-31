# Experiment 2l — Design Doc: The Sealed Cross-Family Forecast — Does the 256-Draw Predictor Forecast an Outcome Nobody Has Seen?

**Status: session 1 (design) written 2026-08-30, at Exp 2k's
close-out, on Michael's word ("Design approach C"). §10 DIALS a–l RULED
by Michael 2026-08-30 ("as recommended"): a OLMo-2 13B; b Tests A/B,
four worlds; c 64k spacing, 16 points + step 0; d Test B on x_A's
median bucket; e R_∩ by the floor rule, the nine printed; f the
projection sealed after the endpoint stage, placed against the block
SD; g S5 non-gating; h the power record prints Test A's block SD; i
the real step 0 as the init referent; j the preflight on his word; k
bars unchanged; l SDD build + freeze in one session. Build follows;
no model is touched before the tag and his word.** Model
contact, when sanctioned: OLMo-2 13B ONLY, on the OUTCOME side — its
stage-1 endpoint and `main` at the endpoint stage, then its stage-1
grid in the sweep. Every predictor is already committed and tagged;
nothing is sampled.

Approach C is the follow-up 2k's §6 named under DENSITY: "the sealed
cross-family test is approach C with the predictor at 256 draws". 2k
showed the 256-draw predictor clears the bar on an outcome that was
already on disk; 2l asks whether it forecasts one that is not.

## 1. The question

**Does Pythia-1b's committed sampled count at k = 256 (Experiment 2k,
sealed 2026-08-30, tag `exp2k-predictor-sealed`) forecast the order in
which OLMo-2 13B's stage-1 training makes 2c's items emittable —
an outcome no one in this program has ever queried — within 2g's
difficulty strata; and does OLMo-2 1B's committed count (Experiment 2i,
tag `exp2i-predictor-sealed`) forecast that order beyond it?**

Two preregistered tests on one sealed outcome, read jointly — 2i's
construction with the cross-family predictor at 256 draws instead of
64 and a larger, never-touched outcome model:

- **Test A (cross-family, 256 draws).** Predictor x_A = Pythia-1b's
  256-draw count (2k). Fires iff the stratified concordance clears
  2g's bar (p < .01, T ≥ .10).
- **Test B (within-family, beyond cross).** Predictor x_B = OLMo-2 1B's
  64-draw count (2i), in composite strata = base stratum | the median
  bucket of x_A (dial d — 2i used x_A's zero cut, which at 256 draws
  is nearly empty: 471 of 500 antonym items are live). Fires on the
  same rule.

Worlds (after INSUFFICIENT_DATA), 2i's four:

- **SHARED** — A fires, B does not: the ordering transfers across
  architecture, tokenizer, corpus and recipe, and the same-family
  small model adds nothing beyond it.
- **LINEAGE** — B fires, A does not: 2k's bar-clearing was a property
  of the known outcome, or of 7B; the cross-family sentence stays
  unlicensed and 2k's DENSITY reading is demoted to "on a known
  outcome".
- **BOTH** — both fire: a shared component and a lineage increment,
  each reported with its partial.
- **NEITHER** — the 2g/2h/2i/2k finding does not reproduce at 13B (or
  the battery does not transfer to it).

The tests are firing rules, not a head-to-head of magnitudes (2i §1):
T_A and T_B live on different tie structures. Within-alone (x_B
unconditioned) and cross-beyond-within (x_A in strata of x_B's median
bucket) are printed beside them.

## 2. What is known and what is sealed (disclosure)

**Known:** everything through 2k's close-out — the three sealed
forecasts on Pythia and on OLMo-2 7B, 2i's LINEAGE verdict (A .0949, B
.2153), 2j's mechanism reading, and 2k's DENSITY result with its full
texture: on OLMo-2 7B's KNOWN outcome, x_A^(256) reads .1548 (per rung
add_base8 .476, sub_base8 .440, sub3_mid .147, antonym6 .115, odd6 .096,
arith_next .092, add3_mid .027, antonym .024, sub4_mid −.024), the four
64-draw blocks .0949/.1077/.0948/.0938, the ladder .0949 → .1256 →
.1433 → .1548, x_B's lineage increment +.054 at matched density, the
410m predictor ahead at .1695. The predictors x_A^(64), x_A^(256) (both
sizes) and x_B^(64) are historically prior and tag-bound. The Hub
inventory of OLMo-2 13B's branches was read on 2026-08-30 (metadata
only: 646 stage-1 checkpoints from `stage1-step0-tokens0B` to
`stage1-step596057-tokens5001B`, every 1,000 steps with no gap, 12
safetensors shards of 54.9 GB per revision; no weight touched).

**Not known to anyone in this program:** any output of OLMo-2 13B on
any item. The outcome is sealed in the strongest sense this program
has: the predictors were committed before the outcome model was named,
and the design cannot have been tuned to 13B's behaviour — it is 2i's
design with the outcome model swapped and the cross-family predictor
at 256 draws.

**What 2k's texture makes foreseeable, stated now:** 2k's per-rung
readings on 7B are the projection's raw material — but 7B and 13B are
different runs (5.0T vs 3.9T tokens, 596k vs 929k steps, a real step 0
here where 7B had none), and the transfer of ITEM order from 7B's
training to 13B's is itself unmeasured. The verdict-level call is a
genuine forecast this time; the projection (dial f) names it and its
texture in advance and is graded as the test.

**Sealed in order (§7):** the instrument (`exp2l-preregistered`, blob-
bound) before any 13B weight loads; the endpoint stage
(`exp2l-endpoint-sealed`: the 68 endpoint records, the rung set, the
power record) before the sweep; the projection before gate 1. There is
no predictor stage — every predictor is already sealed by 2k and 2i.

**What "cross-family" means here** is 2i §2's paragraph verbatim: a
different architecture, tokenizer, corpus and recipe; NOT disjoint
training data. SHARED reads "the ordering is not Pythia's lineage's",
not "the ordering owes nothing to shared text".

**Pre-tag disclosure rule** (checklist item 27): any execution of 2l's
analyzer on the real tree before the tag is logged here before the
tag is cut, with what it printed. At the time of writing the analyzer
does not exist; on the real pre-campaign tree every execution lands
INSUFFICIENT_DATA (no 13B records) and prints no T.

Build Task 5 ran `analyze_2l.run()` on the real pre-campaign tree twice
before any tag as a standalone tool invocation: the import-surface scan
(`tests/import_scan_2l.py`) and the read sweep (`tests/read_sweep_2l.py`),
both at `n_perm=30, n_boot=10` — both printed INSUFFICIENT_DATA (the 13B
endpoint/rung-set/power/sweep records are absent) and no T; both fully
exercised the real, closed predictor stages (2k's sealed 256-draw tier
and 2i's sealed OLMo-2 1B counts, zero failures on either) before
refusing. Task 5's own test suite adds eleven more real-tree executions
on top of those two: `test_analyze_2l.py`'s five forced-exception tests
(`test_run_forced_exceptions_on_the_real_tree_are_graceful`, parametrized
×7 over `_RUN_FORCED_CASES_2L`; `test_run_strata_pins_forced_exception`;
`test_run_frozen_check_forced_exception`;
`test_run_import_surface_entry_forced_exception`;
`test_run_referent_manifest_check_forced_exception`) each call
`an.run(n_perm=20, n_boot=5)` with the default `root_2l = EXP2L` — the
real pre-campaign tree — and these eleven re-execute on every FAST pass,
including every round of the mutation harness. Every one of the eleven
lands INSUFFICIENT_DATA with no T: an exception is injected into an
early loader before any statistic is reached, and the 13B records are
absent regardless of the injection.

## 3. Instrument — 2i's, with the outcome model swapped and the cross-family predictor at 256

Everything not named here is `experiments/exp2i` / `exp2k` machinery
imported frozen: 2c's harness, 2g's strata and statistics (within-
stratum Somers' D, mean over rungs, permutation within rung × stratum,
10,000, seed 0; bootstrap CI per rung), eligibility n_pos ≥ 20, the
count outcome with first-correct printed, the referent discipline,
the tree-totality closure, gate-1 coverage attestation + re-derivation,
blob-bound tags, the import-surface pin from commit one (2j F-1 / 2k),
`pins_active` (2k D-1), 2i's candidate-file loader with the per-entry
`config.json` write (2i stop #1), 2i's totality over compressed
streams. The deltas:

1. **The outcome model.** `allenai/OLMo-2-1124-13B`: 13B, the same
   tokenizer as 7B (100k BPE, `<|pad|>` 100277, no BOS — `check_
   tokenizer` applies unchanged), 12 safetensors shards (54.9 GB fp32
   per revision, fp16 at load ≈ 26 GB on the Mac's 48 GB). Per-
   revision commit sha and per-file LFS sha256 in a committed manifest
   (2i's candidate rule, duplicate-signature refusal). The stage-1
   branch has a REAL step 0 (`stage1-step0-tokens0B`), so the init
   referent is the model's own initialisation, not a seeded
   `from_config` twin (2i's disclosed stand-in) — descriptive, never in
   an outcome, scored once in the sweep.
2. **The predictors, loaded through their own seals.** x_A^(256) =
   2k's sealed 1b tier: re-derived from the raw draws through 2k's
   `load_tier_2k` (record provenance, gate-1 re-derivation against 2d's
   committed rows, tallies), cross-checked against `predictor_2k.json`
   (`seal_failures_2k`), the seal tag `exp2k-predictor-sealed` required
   to bind. x_A^(64/128/192) from the same rows (the ladder, §5). x_B =
   2i's sealed OLMo-2 1B counts through 2i's `load_predictor_records_2i`
   + provenance + `_check_predictor_counts_2i`, `exp2i-predictor-sealed`
   required to bind. x_A^(256) at 410m likewise (S2). No new sampled
   quantity anywhere in 2l.
3. **The endpoint stage.** 13B's stage-1 endpoint
   (`stage1-step596057-tokens5001B`) AND `main` (the stage-2 soup)
   through the thin loader on all 34 rungs, per-item bits and
   continuations stored (2c's greedy fp16 harness, the path that
   produced every outcome in this line). The endpoint record fixes R
   (§4) by rule and feeds the power record; `main` is descriptive
   only. Committed and tagged `exp2l-endpoint-sealed` before any
   intermediate checkpoint loads. ≈ 2 × 2.6 h and 2 × 55 GB streamed.
4. **The outcome is 13B's stage-1 grid** — 2i's shape scaled to the
   run (596,057 steps, ≈ 8.4 M tokens each):

       S = {1k, 2k, 4k, 8k, 16k, 32k}            (log-spaced head)
         ∪ {64k · j : j = 1 … 9}                 (every 64k, 64k … 576k)
         ∪ {596057}                              (endpoint; gate 1)

   All 16 exist on the branch (verified 2026-08-30, metadata only),
   plus step 0 as the real init referent. y_i = number of grid points
   at which item i verifies (2g's count outcome; range 0..16);
   first-correct step printed beside it. Same disclosure as 2i: the
   head puts 6 of 16 points in the first 5.4 % of training, so the
   count weights earliness, which is the intent. Dial c: 64k spacing
   (16 points, ≈ 44 h of sweep) vs 32k (24 points, ≈ 65 h).
5. **Gate 1** = the endpoint reproduced through the sweep's checkpoint
   loader: per-item bits identical to the endpoint record on all 34
   rungs, continuations identical with the compared count attested and
   required to be 500/rung, tensor digest equal, RE-DERIVED by the
   analyzer from the two committed record sets. Runs first in the
   sweep; a diff halts with the tree the analyzer reads as
   INSUFFICIENT_DATA (both halt artifacts refuse — 2k F-1).
6. **The tree.** INSUFFICIENT_DATA → the joint reading of Tests A and
   B → SHARED / LINEAGE / BOTH / NEITHER. Every quantity of §5 printed
   in every world. Ruling 18's undefined branch retained (a test all of
   whose eligible rungs are degenerate is `fires = False` with
   "undefined" named inside) — unreachable for A on this data
   (x_A^(256) is non-degenerate on every strata rung: 2k), reachable
   for B only if x_B sits at ceiling inside every composite cell.
7. **Pins.** `FROZEN_SHA256_2L` over every module named (2k's list +
   2k's own instrument blobs, now frozen bytes); `IMPORTED_SHA256_2L`
   over the resolved module table at entry and exit; a pre-campaign
   referent manifest (2k's list + 2k's verdict, seal, power and tier
   files, 2i's predictor stage); the campaign's own artifacts (68
   endpoint records, the rung set, the power record) bound by
   `exp2l-endpoint-sealed`; the sweep records read through the
   endpoint seal's sha as 2i's are. Blob-bound tags: `exp2l-
   preregistered` binds the analyzer, the battery module, the endpoint
   stage and the sweep runner.

## 4. Rung set, strata and power

**R_13B** — the rungs whose 13B stage-1 endpoint count clears 2d's bar
(one-sided exact binomial against 2d's model-free floor, max(majority
share, 1/n_options), 2d's α), fixed at the endpoint stage by rule. Not
known now; at 5.0T tokens it may exceed 7B's thirteen.

**Strata.** 2g's committed table (eleven rungs). The primary for both
tests runs over **R_∩ = R_13B ∩ those eleven**; rungs outside get raw
single-stratum D, printed, never in the verdict; fewer than three
rungs → THIN declared in the power record, the verdict still runs.
**R_CAP's comparability:** 2i/2k's nine (add3_mid, add_base8, antonym,
antonym6, arith_next, odd6, sub3_mid, sub4_mid, sub_base8) is printed
as the comparable subset whenever R_∩ ⊇ it; the primary is over R_∩ as
fixed by rule, not over the nine (dial e).

**Predictor degeneracy.** x_A^(256) has at least two live strata on
every one of the eleven strata rungs (2k's tiers). x_B at ceiling
(64/64) inside a composite cell drops that cell; a rung with no
informative cell is dropped from Test B and printed.

**Power**, written ONCE at the endpoint stage, before the projection,
per test, with 2i's machinery over the REAL predictors: n_pos bounded
below by the endpoint count, y from a latent mixing rank(x) at
calibrated strength inside the test's strata, every cell through the
verdict's own tree; bar P(fires | D = .15) ≥ .75, else DECLARED
UNDERPOWERED IN ADVANCE per test; P(fires | D = .10) printed (the bar
decides). **New (2k's process note, applied):** the power record ALSO
prints Test A's predictor block SD — T_A computed on each of x_A's four
64-draw blocks against the endpoint's n_pos-bounded latent — beside
the null SD, so the record says in advance how far a k = 64 reading of
the same predictor would scatter; and the projection names its
verdict call inside or outside that scatter. Shape note verbatim
(item-level alternative; nothing transfers to a class-level effect);
the union of the four worlds is not α-calibrated (each test at α .01).

## 5. Named secondaries (printed in every world; no α claim)

- **S1 — the ladder on a sealed outcome.** T_A at k = 64, 128, 192,
  256 (2k's nested blocks) → 13B. The density story as a FORECAST: does
  the 64-draw predictor miss the bar on a sealed outcome as it did on
  7B, and does 256 clear it? The four 64-draw blocks' T's and their SD
  (2k's S1 on the new outcome).
- **S2 — 410m at 256** → 13B (2k: 410m ≥ 1b on 7B at both budgets).
- **S3 — within-alone** (x_B unconditioned) and **cross-beyond-
  within** (x_A^(256) in strata of x_B's median bucket) — 2i's partials.
- **S4 — the matched comparison** (2j/2k's block rule): x_B thinned to
  k_g = clip(round(256 · r̄_A / r̄_B), 1, 64) per rung against
  x_A^(256) on the sealed outcome; the lineage increment at matched
  density, its sign and size (2k: +.054 on 7B).
- **S5 — the answer prior as a sealed-outcome forecaster.** 2j found
  that OLMo-2 1B's wrong-target propensity π (how often it says answer
  a_i when a_i is wrong) forecasts 7B's order at .199 on a KNOWN
  outcome; π is a committed functional of committed draws (2j's
  `wrong_target_propensity` on 2i's x_B rows). Printed against 13B's
  sealed order with 2i's statistic — the second mechanism's first test
  on an outcome it could not have been fitted to. Non-gating (dial g:
  non-gating vs a third preregistered test).
- **S6 — the real init referent and `main`.** Step 0's per-rung counts
  (expected ≈ 0; a nonzero count is a floor-guessing texture, printed);
  `main` vs the stage-1 endpoint per rung (what mid-training changes).
- **S7 — textures.** Ever-vs-final verification per rung, transient
  clears on flat rungs, checkpoint-local collapses (2h's pathology,
  absent on 7B), non-monotone trajectories, first-correct steps; the
  reverse readings (13B's order is new, so none).
- **Sensitivities:** the first-correct outcome as y; the primary over
  R_CAP's nine when R_∩ ⊋ nine; Test B under the zero cut (2i's
  construction) beside the median bucket.

## 6. Licences, written in advance

- **SHARED:** the essay's cross-family sentence is licensed as a
  forecast — "a smaller model of a different family, given enough
  draws, forecasts what training surfaces first" — with 2k's density
  reading confirmed on a sealed outcome; Prediction 2's output-channel
  form is no longer "a lineage instrument"; the "structure latent in
  the training distribution" reading gains a cross-family leg at item
  grain on a hidden outcome; the named next experiment is a third
  family.
- **LINEAGE:** 2k's DENSITY reading is demoted to "on a known outcome":
  the essay says the 256-draw predictor cleared the bar on 7B's
  already-known order and did not forecast 13B's; the lineage sentence
  stands; the cross-family sentence stays unlicensed; next is the
  mechanism question on what 7B's order and 13B's share.
- **BOTH:** both components with their partials (T_A, T_B, within-
  alone, cross-beyond-within, the matched increment); the shared
  component is the headline only if T_A's CI excludes zero on the
  majority of R_∩.
- **NEITHER:** the two-family, four-outcome finding is bounded at 13B
  in the essay and experiments.md; the full 13B record reported; the
  program's next step is Michael's call.
- Any world: S1–S7 in full; the step-0 referent, `main`, the flat and
  extra rungs reported; S5's reading stated as descriptive.

## 7. Run plan and model contact

Design (this doc + rulings) → build (`experiments/exp2l`: the 13B
manifest from a committed Hub scan with the candidate rule, the two
loaders, the endpoint stage, the sweep runner, the two-test analyzer
with the four worlds and S1–S7, power with the block-SD line,
referents, fixtures, worlds for every terminal, totality, mutation,
read sweep, import scan) → adversarial freeze → tag `exp2l-
preregistered` → **preflight (dial j) on Michael's word:** 2c's
harness on 13B `main` for 20 items each of `antonym` and `add3_mid`,
continuations printed to the ledger and stored nowhere the analyzer
reads — a format and MEMORY check (fp16 13B at ≈ 26 GB on 48 GB; the
generation batch is the dial if it does not fit; ONE checkpoint staged
through the candidate-file loader end to end, the tenth lesson) →
**stage 1 (endpoint)**: 13B's stage-1 endpoint + `main` through the thin
loader on all 34 rungs (≈ 5 h, 2 × 55 GB streamed), R fixed by rule,
power printed once (with the block-SD line), committed, tagged
`exp2l-endpoint-sealed` → projection sealed (named disconfirmers
bracketing the null for EACH test; the verdict call placed against the
block SD) → **stage 2 (sweep)**: gate 1 first, then step 0 and the 15
remaining grid points, ≈ 2.6 h each at fp16 by 7B's measured 82 min
scaled by parameters, ≈ 44 h, ≈ 935 GB streamed one checkpoint at a
time and deleted (260 GB free; the 7B revisions in the HF cache, 54 GB,
cleared first), the watcher committing every record after its size
stops changing, processes detached → analyzer once, detached (2i's
tree plus S1–S7: ≈ 1–2 h) → `exp2l-closed`. One pre-committed change.

Compute: the Mac for every stage (the stack that has produced twelve
byte-identical reproductions; gate 1 is byte identity between 2l's own
two loader paths). Disk: peak ≈ 55 GB (one checkpoint) + the thin
loader's endpoint and `main` in the ordinary HF cache (110 GB) — the
operator clears `~/.cache/huggingface` of the 7B revisions before
stage 1 and of 13B's after stage 2 if the margin matters.

## 8. Alternatives considered

- **32k spacing** (24 points): finer count outcome, ≈ 65 h; 2i/2k used
  64k on 7B and the count outcome at 16 points already spans 0..16;
  deferred to dial c.
- **A fresh OLMo-2 7B predictor at 256 draws** (the lineage predictor
  at 2k's budget): predictor-side model contact at 7B (≈ 60+ h of
  sampling) for a question 2k already answered at matched density
  (+.054 either way); not taken.
- **A third family** (a non-OLMo, non-Pythia outcome): the right next
  step under SHARED; premature before the sealed cross-family test has
  been run once.

## 9. What 2l does not claim

Not "Prediction 2 supported across families" unless SHARED or BOTH
fires — and then only at item grain, on one battery, one predictor
family, one outcome family. Not a mechanism result (S4/S5 are
descriptive). Not a statement about 13B's mid-training `main`. Not a
statement about the across-task ranking.

## 10. Dials — RULED by Michael 2026-08-30 ("as recommended"): every dial as recommended

- **a. Outcome model:** OLMo-2 13B stage-1 (`allenai/OLMo-2-1124-13B`),
  **recommended**; the alternative (a third family) is §8's.
- **b. Tests:** A = x_A^(256) cross-family; B = x_B^(64) within-family
  beyond A; four worlds as 2i, **recommended**.
- **c. Grid:** 64k spacing → 16 trained points + step 0 (≈ 44 h),
  **recommended**; 32k → 24 points (≈ 65 h).
- **d. Test B's conditioning:** x_A^(256)'s MEDIAN bucket (the zero cut
  is nearly empty at 256 draws), **recommended**; the zero cut printed
  as a sensitivity.
- **e. Rung set:** R_∩ by 2d's floor rule at the endpoint, the nine
  printed as the comparable subset, **recommended**.
- **f. Projection:** sealed after the endpoint stage and before the
  sweep; a genuine verdict-level forecast this time, placed against
  the printed block SD, plus the texture (per-rung D at 256 from 2k's
  7B readings as the prior, the ladder at 64 vs 256, the matched
  increment's sign, 410m vs 1b, step 0 ≈ 0), named disconfirmers
  bracketing the null for each test, **recommended**.
- **g. S5 (the answer prior) non-gating,** **recommended**; the
  alternative is a third preregistered test at the same bar (a
  mechanism claim on a sealed outcome — strong if it fires, but it
  widens the α-uncalibrated union of worlds).
- **h. Power record prints Test A's block SD** (2k's process note
  applied), **recommended**.
- **i. The real step 0 as the init referent** (descriptive, in the
  sweep, never in an outcome), **recommended**; 2i's from_config twin
  not needed.
- **j. Preflight on his word:** 20 items × 2 rungs on `main` + one
  checkpoint staged through the candidate-file loader; no sampling
  (nothing to sample), **recommended**.
- **k. Bars .10 / .01 unchanged,** **recommended**.
- **l. Build + freeze in one session** by SDD, the import pin from
  commit one; licences as §6, **recommended**.

## 11. Process

Design → rulings → build → freeze → tag → preflight on his word →
endpoint stage → seal tag → projection → sweep (detached, watcher, one
poller) → analyzer once, detached → `exp2l-closed` → close-out
propagation (essay under §6, `experiments.md`, the graft with the
three tags, Zenodo v1.15, paper inventory).
