# Experiment 2j — Design Doc: The Mechanism Question — What About a Smaller Model's Output Makes an Item Reachable?

**Status: session 1 (design) written 2026-08-28, at Exp 2i's
close-out, on Michael's word ("Approach A, A-1 as named secondary —
design 2j"). §10 DIALS RULED by Michael 2026-08-28 ("dials as
recommended — build and freeze"): a joint composite primary; b median
split with the tie fallback; c the four functionals; d wrong-target
π; e per-rung density-matched block thinning, T per block, no
permutation p; f 2i's power simulation once at the build, governing
how ABSORBED reads; g .10 / .01 unchanged; h build + freeze in one
session; i the asymmetry re-read printed, non-gating; j the §2
disclosure verbatim in the verdict record and any licensed sentence;
k licences as §6. BUILT + FROZEN the same session (SDD build, four
tasks each reviewed; adversarial freeze worked cold by a fresh
reviewer): THE CLASS DEFECT FOUND — F-1, the analyzer's import surface
had no pin (23 files under `experiments/` executed inside `run()`
unpinned and invisible to the read sweep; two lines in
`exp2j/__init__.py` moved T_beyond .13111 → .13302 with every gate
passing) — closed by `IMPORTED_SHA256_2J` (28 files, literal) checked
at entry and exit; F-2 the power record's composite partition
attested, never compared (now a refusal); F-3 the block gate proved
the mean only (now per-rung D); F-4 two cross-experiment label
prefixes (disclosed, pinned); F-5 the realized-THIN guard on one
branch only. Cold at the freeze head: suite 113, nine world terminals,
totality 30, battery 12/12, mutation 70 (69 killed + 1 equivalent, 0
open), read sweep 4,347 paths 0 unpinned, determinism byte-identical
×2; power ONCE POWERED (P(fires | D = .15) = 1.000, null SD .0114,
min-detectable T .0265). Findings and doc slips (a)–(h) RATIFIED by
Michael 2026-08-28 ("ratified — apply the slips and tag") and applied
in place; tag `exp2j-preregistered` follows (blob-bound:
`analyze_2j.py` + `functionals_2j.py`).
ANALYSIS-ONLY: no model is loaded, nothing is sampled; every input is
a committed 2d, 2g, 2h or 2i artifact, re-derived from raw bytes
through the predecessor's own frozen loader. Zero model contact,
minutes of compute.**

Lineage: 2g (NO-FORECAST; the sampler competitor fired, T .167) → 2h
(CONFIRMED, T .202) → 2i (LINEAGE: within-family B .2153 fires;
cross-family A .0949 real and below the bar). Three sealed outcomes
say the same thing: at item grain, the order in which training makes
2c's items emittable is forecast by how often a smaller model of the
same lineage already emits them, through difficulty strata, with the
probe adding nothing. None of the three says WHY. 2h §5 named the
limit — a sampled rate is both *reachability* and *un-named
difficulty* — and 2i's §6 LINEAGE licence named the successor: the
mechanism question. 2i also left the first datum: the reverse
direction. OLMo-2 1B's counts read Pythia-2.8b's committed order at
.2612 and Pythia-6.9b's at .2974, while Pythia-1b's counts read
OLMo-2 7B's at .0949 — the richer predictor crosses families at 2–3×
the strength with which the thin one crosses back.

## 1. The question

**When a smaller model's sampled count forecasts which items training
surfaces first, what in the count carries the forecast?** Three
candidates, each a frozen functional of committed bytes:

1. **The answer's prior in the model's mouth.** The model emits the
   answer string on OTHER items' prompts too — a habit of the output
   distribution, not a reading of the input. A count that forecasts
   because of this forecasts which answers are cheap to say.
2. **The answer's structure.** Short, repetitive, or copyable from
   the input — 3d's repeat class and 3e's copy route, generalised off
   the reversal family. A count that forecasts because of this
   forecasts which answers are cheap to produce, for any model.
3. **The residual** — whatever is left once 1 and 2 are held fixed
   inside the difficulty strata: input-specific partial competence,
   the thing the essay's sentence actually means.

**A-2 (primary): does OLMo-2 1B's count forecast OLMo-2 7B's emission
order BEYOND the answer's prior and structure — in composite strata
that hold 2g's difficulty covariate, the model's own wrong-target
emission rate for the answer, the answer's length, its character
repetition and its overlap with the input all fixed at once?** The
same statistic as 2i's Test B (mean over rungs of within-stratum
Somers' D, permutation null within stratum, T ≥ .10 at α .01), on the
same nine rungs, the same bytes, and a finer partition. The known
referent is 2i's within-alone reading, T = .2204: the primary asks
how much of that survives.

**A-1 (named secondary, non-gating): is the reverse-direction
asymmetry a property of the predictor's information density?** OLMo-2
1B's mean verified rate exceeds Pythia-1b's by 3–9× on five of the six
2h-carried rungs and sits at parity on odd6 (§2). Thin
the denser predictor on each rung to the sparser one's expected
verified draws per item — a preregistered, seed-free subset of the
committed draws — and read both predictors against the same three
outcomes at matched density. If the thinned OLMo-1B falls to
Pythia-1b's level, 2i's sub-bar A reads as a resolution shortfall of a
thin predictor; if it holds, the asymmetry is the model's, not the
draws'.

## 2. What is known, and what this experiment therefore cannot be

Everything. 2i's outcome (OLMo-2 7B's 21-point emission order) was
sealed until its sweep and is now known, with its verdict; 2g's and
2h's outcomes are known; x_A (Pythia-1b, 2d's main tier) and x_B
(OLMo-2 1B, 2i's predictor stage) are known with their per-rung
concordances in every direction. There is no sealed outcome left on
this battery below 12b, and 2j does not pretend to one. It is 2e's
kind of experiment: mechanism attribution on committed bytes, where
preregistration protects against exactly one thing — choosing the
functional, the partition or the tree after seeing what they do to
the concordance — and not against a design written with the
concordances in view. The doc says so here, the verdict record
repeats this paragraph verbatim, and any licensed sentence carries it.

What was computed during the design session (2026-08-28), and nothing
else: per-rung facts about the ITEM FILES alone — the number of
distinct answers, the answer-length distribution, the count of
answers with a repeated character, and the distribution of
answer-in-question character overlap — to check that the functionals
of §5.1 are definable, i.e. not constant, on the nine rungs. No
functional was computed against any predictor or outcome; no
concordance was computed. The item-file facts (verbatim, so the
reader can see what the design knew):

| rung | distinct answers / 500 | answer length (chars) | repeated-char answers | answer verbatim in question |
|---|---|---|---|---|
| antonym | 111 | 3–11 | 274 | 500 (option listing) |
| antonym6 | 127 | 3–10 | 264 | 500 (option listing) |
| odd6 | 80 | 3–8 | 166 | 500 (option listing) |
| add_base8 | 100 | 2: 196, 3: 304 | 165 | 0 |
| sub_base8 | 52 | 1: 157, 2: 343 | 44 | 74 |
| arith_next | 136 | 2: 266, 3: 234 | 111 | 0 |
| add3_mid | 418 | 3: 210, 4: 290 | 222 | 0 |
| sub3_mid | 325 | 1–3 | 113 | 24 |
| sub4_mid | 470 | 1–4 | 216 | 1 |

Two consequences the design takes from that table, stated now: the
input-overlap functional is constant (1.0) on the three
option-listing rungs of R_CAP (antonym, antonym6, odd6) and is
dropped there by the §5.2 rule — median5, in 2g's eleven covered
rungs but outside R_CAP, drops O too (slip (b)); and on
the three mid-digit rungs the answers are nearly unique, so the
wrong-target propensity will be zero on most items and the bucket
rule's tie fallback (§5.2) is what applies — those three rungs
contributed ≈ 0 to every 2i reading and will contribute ≈ 0 here.

Also known to the designer before the tag (slip (c), ratified
2026-08-28): the primary's own T_beyond on the real tree (0.1311),
printed by the build's read sweep at n_perm 30 — T does not depend on
n_perm, so the sweep's incidental output is the real value. No
functional, bucket rule, partition or tree element was chosen after
it; §5 was frozen before any computation ran. The projection carries
the same disclosure, on 2e's precedent.

The known texture of the asymmetry, which A-1 is built to read
(2i `results/verdict.json`, 2h and 2g verdict records; per-rung
stratified D on the SAME outcome, x_A = Pythia-1b at 64 draws, x_B =
OLMo-2 1B at 64 draws):

| rung | x_A → 6.9b (2h) | x_B → 6.9b (2i rev.) | x_A → 2.8b (2g comp.) | x_B → 2.8b (2i rev.) | mean rate x_A | mean rate x_B |
|---|---|---|---|---|---|---|
| add_base8 | .253 | **.651** | .199 | **.667** | .0053 | .0486 |
| arith_next | .231 | **.411** | .168 | **.321** | .0166 | .1163 |
| sub_base8 | .408 | .397 | .386 | .389 | .0226 | .1289 |
| antonym6 | .291 | .206 | .209 | .182 | .0983 | .2700 |
| antonym | .143 | .182 | .186 | .123 | .1365 | .4048 |
| odd6 | .187 | .143 | — | — | .0998 | .1121 |
| add3_mid | .012 | .091 | ≈ 0 | .091 | .0003 | .0030 |
| sub3_mid | — | — | ≈ 0 | .056 | .0011 | .0017 |

The asymmetry is not uniform: it lives on add_base8 and arith_next
(and weakly on add3_mid) — the rungs where Pythia-1b's rate is
thinnest among the six carried rungs — and is absent or reversed on
sub_base8, antonym6, antonym and odd6, where x_A's rate is ≥ .02.
That pattern is what a density account predicts and what A-1 tests
directly; it is disclosed here so that a DENSITY reading is not
mistaken for foresight.

## 3. Instrument — 2i's, with a finer partition and a thinner predictor

Everything not named here is `experiments/exp2i` (and through it
2g/2h/2d/2c/exp3) machinery imported frozen and sha-pinned, by name:

- **x_A** — `battery_2i.sampler_counts_pythia` (= 2h's
  `sampler_counts`): 2d's main tier, `results/main/<size>_trained/
  <rung>.draws.jsonl.gz`, seed 0, 64 T = 1.0 draws per item, rows read
  by 2d's `read_rows` (full 500-item coverage enforced) and each draw
  verified by `load_verify_3c` — 2c's `normalize_answer` on both sides,
  exact match, `IndexError → False` on the draw side only. The 68
  draws files are byte-pinned (`battery_2i.PYTHIA_PREDICTOR_FILES`).
- **x_B** — `battery_2i.sampler_counts_olmo` over
  `results/predictor/olmo1b/<rung>.draws.jsonl.gz` (the same row
  schema: `{"draws": {"0": [64 strings]}, "item": i}`), with 2i F-1's
  provenance re-measurement: `load_predictor_records_2i` +
  `predictor_record_failures_2i` check every record against the
  manifest and battery (repo, revision `stage1-step1907359-tokens4001B`,
  commit, item sha, answer column, answer type, `max_new_tokens`,
  seed 0 / 64 / T 1.0 / no truncation / fp32 / namespace `exp3` /
  `mode = trained`), and the seal `predictor_2i.json` (sha d80ada50…)
  is cross-checked against the re-derived counts, never used as an
  input.
- **y_OLMo** — `analyze_2i.load_sweep_7b` + `outcomes_7b` over the
  22 committed sweep units (21 trained points of `GRID_7B` + the
  twin), every record re-verified from its stored continuations, gate
  1 re-derived from the endpoint and sweep record sets exactly as 2i
  did (0 bit diffs, 0 continuation diffs, digests equal, coverage
  500/rung); y_i = the number of the 21 trained points at which item
  i verifies.
- **The Pythia outcomes** — `analyze_2g.load_sweep` + `outcomes`
  (2.8b, 21 trained points, `R_28`) and `analyze_2h.load_sweep_69` +
  `outcomes_69` (6.9b, 22 trained points, `R_69`), exactly as 2i's
  `_reverse_direction` calls them.
- **Strata** — 2g's committed table, read from the `strata` block of
  2g's sealed `results/predictor/predictor.json` (sha 9eadbac3…) via
  `strata_2g.from_json`, `check_strata_pins` re-run; the eleven
  covered rungs are `strata_2g.COVARIATE_OF`.
- **The statistic** — `stats_2g`: `somers_d_within`, `perm_test`
  (N_PERM 10,000, PERM_SEED 0, one-sided p = (1 + n_ge)/(1 + N_PERM),
  T the unweighted mean over eligible rungs, the predictor permuted
  within rung × stratum), `bootstrap_d` (N_BOOT 1,000, seed 0,
  item-level resample per rung); through `analyze_2i.primary_2i`
  (= 2h's `primary_2h`), `_run_test` and `fires_2i` (p < ALPHA .01
  and T ≥ T_BAR .10).
- **Eligibility and degeneracy** — `battery_2g.ELIGIBILITY_MIN_POS =
  20` positives in the outcome; `analyze_2i._degenerate_rungs` (a
  rung whose predictor has fewer than two distinct values inside
  EVERY stratum is dropped and printed; a stratum with no informative
  pair contributes none).
- **The refusal discipline** — `analyze_2i.collect_total` (the
  widest of the family: 2g's `collect` → 2h's `collect_total` → 2i's,
  which adds `EOFError` and `zlib.error`); every loader refusal is
  COLLECTED and delivered as INSUFFICIENT_DATA with the reason
  verbatim, never raised; 2e's narrower `collect` is not the model.
- **Blob-bound tagging** — `battery_2i.blobs_bound` /
  `analyze_2i.require_prereg_2i` (2h F-3), `check_frozen_2i`'s
  `FROZEN_SHA256` list extended by 2j's own imports.

2j adds four things:

1. **The functionals** (§5.1) — four per-item quantities from the
   item file and the predictor's own committed draws.
2. **The composite-strata builder** (§5.2) — 2i's "beyond"
   construction (a base stratum joined with a bucket of the
   conditioning variable), generalised from one conditioning variable
   to several, with the bucket rule and the constant-drop rule.
3. **The block-thinning of a predictor** (§5.4) — the first k draws
   of each item's committed 64, in disjoint consecutive blocks; the
   per-rung k fixed by a formula of the two predictors' committed mean
   rates.
4. **The tree** (§6) and its power record (§7).

No new loader, no new statistic, no new outcome. Model contact: none.
Runtime: the primary and its printed decompositions are a few dozen
permutation tests at 10,000 permutations over nine rungs; A-1's block
ladder reports T per block without a permutation p (§5.4), so the
whole run is minutes to an hour on the Mac.

## 4. Referents — every input a committed value

- **Predictors.** 2i's x_B: the 34 predictor records and draws files
  at their sealed shas (`exp2i-predictor-sealed`, `predictor_2i.json`
  sha d80ada50…), counts RE-DERIVED from the raw draws by
  `sampler_counts_olmo` with the F-1 provenance check — the seal's
  `counts` and each record's `per_seed_tallies` are cross-checks,
  never inputs. x_A: 2d's main-tier draws through `sampler_counts_
  pythia` (`PYTHIA_PREDICTOR_FILES`, 68 shas). Both tiers' 410m
  columns likewise.
- **Outcomes.** 2i's sweep records (21 trained points, the twin, the
  endpoint) at their committed shas, gate 1 re-derived (0 bit diffs,
  0 continuation diffs, digests equal); 2g's committed 2.8b per-item
  counts and 2h's 6.9b per-item counts through their own loaders,
  by sha.
- **Known-answer gates on the inherited statistic (the comparison
  gates, 2e's pattern).** Through 2i's frozen code on the same bytes,
  2j must reproduce EXACTLY: Test B T .21533409065382436; within-alone
  T .22041895894950217; Test A T .09491251078607414;
  cross-beyond-within .07006211800715849; the reverse direction
  .2612016707857866 (vs 2.8b) and .297364446603449 (vs 6.9b); and,
  through 2g's and 2h's code, the sampler-competitor T .1672 (2g) and
  the primary T .2020 (2h) at their full recorded precision, pinned by
  literal at the build from the verdict records. A mismatch is
  INSUFFICIENT_DATA — the statistic is not what 2i ran.
- **The block machinery's own gate.** Thinning at k = 64 (one block)
  must reproduce every 64-draw referent above exactly — including the
  per-rung within-stratum D, not only the mean T (slip (h), freeze
  F-3).
- **The strata.** 2g's sealed `predictor.json` by sha; the strata
  gate 2i ran (`check_strata_pins`, `RAW_COUNT_PIN`), re-run.
- **The item files** through 2d's `load_item_file` (raw bytes
  sha-checked against `battery_2d.ITEMS_SHA_PIN` before parsing;
  four rungs live under `exp2b/battery/items`, five under
  `exp2c/battery/items`, resolved by `items_path`); the functionals
  read `eval_items[i]["question"]` and `["answer"]` only; the
  item-file table in §2 pinned by literal. 2d's floors
  (`results/verdict.json`, sha d5b1b28b…) enter only through 2i's
  rung-set re-derivation gate.
- **Instrument pins.** Every 2i/2h/2g/2d/2c/exp3 module 2j imports,
  by sha (`FROZEN_SHA256`, 2i's list extended); a pin failure is a
  hard error with no verdict — the instrument is not what was tagged.
  Blob-bound tag: 2j's analyzer and functionals module byte-identical
  to `exp2j-preregistered`'s blobs or the analyzer refuses. Two
  further refusal inputs (slip (g), freeze F-1 and F-2): the
  analyzer's own import surface — any module under `experiments/` in
  `sys.modules` that is not pinned in `IMPORTED_SHA256_2J`, or that
  has drifted from its pin (files under a `tests/` directory excluded
  and disclosed), checked at `run()`'s entry and exit; and the power
  record's composite partition not equal to the partition the
  analyzer realizes.

## 5. Operationalization

### 5.1 The functionals (one family, enumerated, frozen)

For rung g, item i with normalized answer a_i (2c's normalizer, the
one verify uses) and item-specific question text q_i (the item's own
`question` field, not the shots):

- **π_i — wrong-target propensity under the predictor.** Among all
  committed draws of the predictor model on items j of rung g whose
  normalized answer a_j ≠ a_i, the fraction whose normalized output
  equals a_i (verify with the target swapped to a_i — 3e's
  specificity-arm construction). It is the rate at which the model
  says a_i when a_i is wrong: input-blind emission habit, with the
  correctness of same-answer items excluded by construction (a
  leave-one-out marginal would credit them; dial d). Computed per
  predictor model from its own draws — x_B's from 2i's, x_A's from
  2d's — so π is a property of (model, answer string).
- **L_i — answer length** in characters of a_i.
- **R_i — repeated character:** 1 if a_i contains any character
  twice, else 0 (3d's C1, off the reversal family).
- **O_i — input overlap:** the fraction of a_i's characters (with
  multiplicity) that occur anywhere in q_i. On option-listing rungs
  the answer is verbatim in the question, O ≡ 1, and the constant-drop
  rule removes it there (the option-position stratum already carries
  the copy route on those rungs).

Nothing else. No fitted score, no weights, no per-rung choice: the
four are computed identically on every rung, and where one is
constant it is dropped and printed.

### 5.2 Composite strata

Base stratum = 2g's committed covariate for the rung (carries /
borrows / octal carry-borrow / option position / crosses-100 /
count). Each functional is bucketed WITHIN RUNG over the 500 items:

- **Median split** (2i's construction for a spread variable): bucket
  = 1[F_i > med_g(F)], med_g the median over the rung's 500 items.
- **Tie fallback:** if that bucket is constant on the rung (the
  median sits on a heavily tied value — R on antonym, where 274 of 500
  answers repeat a character, so med = 1; L on add_base8, values 2
  and 3 with med = 3; π on the mid-digit rungs, med = 0), bucket =
  1[F_i ≥ med_g(F)]. With med = 0 this is exactly 2i's zero cut for
  x_A; with a binary functional it is the functional itself.
- **Constant-drop:** a functional that is constant on the rung — or
  whose bucket is still constant after the fallback — is dropped from
  that rung's composite, printed.

(2i's `_median_bucket` is the strict `v > med` rule with ties in
bucket 0; the fallback is 2j's addition and is exercised by fixture.)

A composite stratum is the tuple (base, bucket(π), bucket(L), R,
bucket(O)) over the functionals surviving on that rung — the same
string-join construction as 2i's `_composite_strata` (`base|b1|b2|…`),
generalised from one conditioning variable to several. Pairs are
compared only inside a composite stratum (Somers' D within stratum,
as always); a stratum with fewer than two items with distinct
predictor values contributes no pairs. The eligibility and degeneracy
rules are 2i's, applied to the composite. The doc states the cost in
advance: cells are finer, pairs fewer, the null wider — §7 measures
it.

### 5.3 The primary — A-2

**T_beyond = mean over eligible rungs of R_CAP of within-composite-
stratum Somers' D of x_B against y_OLMo** (2i's count outcome over
the 21 trained points), with 2i's permutation null within composite
stratum (10,000, seed 0) and per-rung bootstrap CIs. Fires iff
p < .01 and T_beyond ≥ .10. The rung set is 2i's R_CAP (nine rungs,
fixed by rule at 2i's endpoint stage, unchanged); a rung on which
every functional is dropped keeps its base strata (its D is then
2i's, reproduced).

Printed beside it, same machinery, same bytes:

- **Within-alone** (base strata only): 2i's .2204, reproduced — the
  denominator of the fraction absorbed.
- **Fraction absorbed** = 1 − T_beyond / T_within-alone, with each
  rung's pair printed.
- **x_B beyond each functional singly** (base × one bucket), four
  readings — which functional absorbs what.
- **Each functional alone** (F → y_OLMo within base strata) — what
  structure forecasts by itself, with its own p and D per rung.
- **The twin:** the from_config 7B twin verifies nothing (2i); no
  SURFACE terminal exists (x_B's twin counts are zero by
  construction). The functionals have no twin; their "alone"
  readings are the surface check.

### 5.4 The named secondary — A-1, density matching

For each rung g, from the committed mean verified rates over the 500
items, r̄_A,g (Pythia-1b, 2d) and r̄_B,g (OLMo-2 1B, 2i) — both in 2i's
`rung_level` table and re-derived here:

    the denser predictor D_g ∈ {A, B} is the one with the larger r̄;
    k_g = clip(round(64 · r̄_sparser,g / r̄_denser,g), 1, 64);
    the denser predictor's thinned count = verified draws among the
    FIRST k_g of each item's committed 64 (`row["draws"]["0"][:k_g]`
    in `read_rows`' order — the committed substream order; no seed,
    no selection);
    disjoint consecutive blocks b = 0 … floor(64 / k_g) − 1, block b
    = draws [b·k_g, (b+1)·k_g); T computed per block; the A-1 reading
    of a rung is the mean over blocks, the block min and max printed —
    that is, per rung: each block's per-rung d exactly as `t_only`
    computes it, the rung's reading the mean over ITS OWN blocks with
    min and max printed, and T the mean over eligible rungs of those
    readings; the ladder is read the same way, and the zero-fraction
    sensitivity uses block 0 (slip (d)).

At the committed rates the thinned predictor is x_B on eight rungs
(k_g: add3_mid 7, add_base8 7, arith_next 9, sub_base8 11, antonym 22,
antonym6 23, sub3_mid 40, odd6 57) and x_A on one (sub4_mid, k ≈ 26,
where Pythia-1b is the denser); odd6 is near parity (1.1×) and
sub4_mid's counts are ≈ 0 on both sides. These k are the formula's
values on known numbers, printed here so the reader can see them; the
build re-derives them and refuses on a mismatch. Because the rule
thins the DENSER predictor on each rung, a rung where the other
predictor is denser keeps its full 64 draws in that side's matched
reading: on the committed rates x_B is denser on eight of the nine
R_CAP rungs and x_A on one (sub4_mid), so `thinned_B_matched` carries
sub4_mid un-thinned and `thinned_A_matched` equals the x_A anchor
exactly on the two Pythia outcomes, where x_B is denser everywhere
(slip (e)).

Read at matched density, on the same strata as the 64-draw referents:

1. **Reverse direction:** thinned x_B → 2.8b (2g's seven rungs) and
   → 6.9b (2h's eight rungs), against two anchors on each outcome —
   x_A at 64 (2g .1672 / 2h .2020) and x_B at 64 (.2612 / .2974). The
   6.9b anchor is printed twice and they differ by construction: the
   comparison GATE re-derives 2h's primary over 2h's own eight-rung
   R_69 (.2020, the literal pin), while A-1's anchor is x_A at 64 over
   the seven rungs R_CAP ∩ R_69 that A-1's thinned readings use
   (.2179); the gap fraction is computed against the seven-rung anchor
   (slip (f)). The headline descriptive: **gap fraction closed** =
   (T_64 − T_k) / (T_64 − T_A) per outcome, with the block range.
2. **Forward, within lineage at Pythia-1b's density:** thinned x_B →
   y_OLMo against x_A → y_OLMo (.0949) and x_B at 64 (.2204,
   within-alone; .2153 in composite strata with x_A's cut).
3. **The ladder:** k ∈ {1, 2, 4, 8, 16, 32, 64} for BOTH predictors on
   all three outcomes, T per block, mean and range — the rate
   structure of the forecast in the number of draws.
4. **Sensitivity — matching on the zero fraction instead of the mean
   rate:** k'_g = the k ∈ 1…64 at which the fraction of items with a
   positive thinned count is closest to the sparser predictor's
   fraction of positive items; the same readings printed.

A-1 reports T per block and no permutation p (dial e): it is a
descriptive of where a thinned predictor lands between two known
anchors; the block spread is its uncertainty. Its readings in §6 are
readings, not licences, and they do not touch the primary's world.

### 5.5 The asymmetry re-read under structure (printed, non-gating)

The primary's decomposition (§5.3) run on the other three
predictor–outcome pairs, each with π computed from that predictor's
own draws: x_A → y_OLMo (2i's A, .0949); x_B → 2.8b and → 6.9b (the
reverse direction); x_A → 2.8b (2g's sampler competitor, .1672) and
→ 6.9b (2h's primary, .2020). One table: T_within-alone, T_beyond,
fraction absorbed, per pair. If the cross-family forecasts are more
absorbed by structure than the within-lineage ones, the lineage
increment is the non-structural residual; if equally absorbed, it is
not. Descriptive only — the outcomes were known before the pairs
were chosen.

### 5.6 Sensitivity (pre-declared, printed, non-gating)

Tercile buckets in place of the median split (dial b's alternative);
π under the leave-one-out marginal in place of the wrong-target rate
(dial d's alternative); the primary on the six 2h-carried rungs
alone (the mid-digit rungs removed — 2i's descriptive .1418 for A
has this shape); the 410m columns of x_A in place of 1b wherever x_A
enters.

## 6. Verdict tree, and what each world licenses

1. **INSUFFICIENT_DATA** — any TREE referent fails: a committed file
   not at its sha; a predictor provenance check failing; gate 1 not
   re-deriving; any comparison gate in §4 not reproducing its literal
   exactly; the block gate at k = 64 not reproducing; an unpinned or
   drifted module on the analyzer's import surface; the power
   record's partition differing from the realized one. Delivered as a
   verdict record with every collected reason verbatim, never
   raised. An INSTRUMENT pin failure is a hard error with no verdict.
2. **RESIDUAL** — the primary fires (p < .01, T_beyond ≥ .10).
3. **ABSORBED** — the primary does not fire.

An undefined primary (x_B constant inside every composite stratum on
every eligible rung, 2i's Ruling 18) or a realized-THIN primary
(fewer than three eligible rungs after the composite partition) lands
ABSORBED with the disclosure carried on the reason string AND the
licensed sentence, and licenses NOTHING — the residual is untested,
not absent (2i's I-4 standard). Symmetrically (freeze F-5), a primary
that FIRES on fewer than three eligible rungs is RESIDUAL — the
terminal is unchanged — with the same THIN disclosure on its reason
and its licensed sentence. (Ratified 2026-08-28, slip (a).)

Read under the §7 declaration: under POWERED, ABSORBED is a measured
absence at this resolution; under DECLARED UNDERPOWERED IN ADVANCE it
reads "not detected at this resolution", with the blind region stated
(2d's rule). Every printed decomposition (§5.3–5.5) and A-1 appear in
every world.

**RESIDUAL licenses:** the essay's lineage sentence gains its
mechanism clause — "and what the count carries is not the answer's
length, its repetitiveness, its overlap with the input, or the
smaller model's habit of saying that answer anyway; holding all four
fixed inside the difficulty strata, the forecast survives at T = …"
— a claim bounded to "not these four", with the §2 disclosure
attached. The named next question is representational: what the 1B
computes on the residual items (a 2f-style matched-label probe on
OLMo-2 1B against this residual, or approach C — the OLMo-2 13B
sealed outcome — for a fresh confirmation).

**ABSORBED licenses:** the count's forecast is structural at this
resolution — it reads which answers are cheap to say or to produce,
for the small model and, since the outcome is the large one's, for
the large model too. The essay's "how often the smaller model already
emits them" sentence gains "— and that, on this battery, is
accounted for by answer prior and structure"; the 2g/2h/2i finding is
reframed as an item-property forecast that any small model's output
reads; Prediction 2's "lineage instrument, not a general one" softens
toward "a structural-ease instrument", read with the printed
attribution (which functional carried it). Under DECLARED
UNDERPOWERED, none of this is licensed and the essay gains one
sentence: the mechanism split was attempted and not resolved at this
resolution.

**A-1's readings (non-gating, either world):** DENSITY — the thinned
x_B closes ≥ half the gap to x_A on both Pythia outcomes: 2i's
sub-bar A reads as a thin-predictor effect and the cross-family
question is open, not closed; the named follow-up is approach B (x_A
at k = 256 on R_CAP against the known OLMo outcome, with 2d's caveat)
or approach C. NOT-DENSITY — the thinned x_B holds (< half the gap):
the asymmetry is the model's — a 4T-token 1B reads the shared order
better than a 300B-token 1B regardless of draws — and the next
cross-family test should use the further-trained small model as the
predictor on a third family with a sealed outcome. MIXED —
otherwise, reported per rung.

Calibration: one primary at α .01; the printed decompositions and
A-1 are not tests and carry no α claim; the union of RESIDUAL /
ABSORBED with the declaration is not α-calibrated (3d's lesson,
stated in advance).

## 7. Power — a claim about the instrument, not foresight

Every input is fixed, and once the functionals and buckets are fixed
the statistic is a constant; so this is not a forecast's power table
(2e §7). What it is: 2i's power machinery (`power_2i.simulate_cells_2i`,
`calibrate_rho`, `_one_test_power`; N_SIM 1,000, N_PERM_POWER 500,
n_pos bounded below by the committed endpoint counts; frozen,
imported), run ONCE at the build on the REAL x_B, the REAL composite
strata and y simulated from a latent mixing rank(x_B) at calibrated
strength, every simulated cell through the verdict's own tree — the question
"would a true within-composite-stratum concordance of .15 fire the
primary?" Bar: P(RESIDUAL | D = .15) ≥ .75 → POWERED; else DECLARED
UNDERPOWERED IN ADVANCE, which governs how ABSORBED reads (§6). The
record prints the null SD of T_beyond and the min-detectable T beside
2i's (.0111 / .0257 under base strata), so the cost of the finer
partition is a number. The shape caveat is 2i's, verbatim: the
alternative is item-level rank concordance inside strata; no
class-level sensitivity. Disclosed: the power record is computed
from known inputs and is a statement about resolution, not about
what will be found.

## 8. What the dumbest baseline achieves

- **Each functional alone** (§5.3): if π alone forecasts y_OLMo at
  .10 within base strata, the answer prior is a forecaster of
  emergence order in its own right — reported whichever world lands.
- **A count that equals its prior:** an item whose predictor count is
  entirely wrong-target habit sits in a π bucket with items of the
  same habit; inside the bucket its count carries nothing. That is
  the mechanism ABSORBED names.
- **The thinned predictor at k = 1:** one draw per item, a 0/1
  predictor — the floor of the ladder; if it already reads the
  reverse direction at .1+, density was never the story.

## 9. What 2j does not claim

Nothing about a hidden outcome — none exists; the §2 paragraph is
attached to every licensed sentence. Nothing beyond 2c's battery,
Pythia ≤ 6.9b and OLMo-2 7B stage 1, two-shot prompts, 2c's criterion.
Nothing about representation: RESIDUAL says the count carries
something the four functionals do not, not what that something is.
Nothing about a third family. ABSORBED does not retract 2g/2h/2i —
the forecasts stand; it says what they were forecasts OF.

## 10. Dials — RULED by Michael 2026-08-28 ("dials as recommended — build and freeze"): every dial as recommended

a. **Primary conditioning** — the JOINT composite (base × all
   surviving functionals; recommended: the residual is what is left
   after everything, and the single-functional readings are printed
   anyway) vs one functional at a time with the primary the smallest
   surviving T (a different question: "does any one of these absorb
   it?") vs π alone as the primary with the model-free three as a
   printed second composite (the sharpest mechanism split, but leaves
   structure out of the gating test).
b. **Bucket rule** — within-rung median split with the tie fallback
   (recommended: 2i's construction, coarse enough to keep pairs) vs
   terciles (finer absorption, fewer pairs; printed as sensitivity
   either way).
c. **The functional family** — the four of §5.1 (recommended) vs
   adding a numeric magnitude for the arithmetic rungs (L already
   carries digit count; magnitude within a length is fine-grained and
   partly the carry stratum) vs dropping R (weakest, binary).
d. **π's definition** — wrong-target emission rate (recommended: the
   correctness of same-answer items is excluded by construction) vs
   the leave-one-out marginal (credits the model's success on other
   items with the same answer — on sub_base8, 28 items share the
   answer '3').
e. **A-1's thinning** — per-rung density matching by mean rate, the
   denser predictor thinned, disjoint blocks, T per block without a
   permutation p (recommended) vs a fixed k = 8 for x_B on every rung
   (under-matches antonym/antonym6, where the gap is 2.7×, and
   over-matches odd6) vs the zero-fraction match as primary (printed
   as sensitivity either way).
f. **Power** — 2i's simulation on the composite strata, once at the
   build, bar .75 at D = .15, governing how ABSORBED reads
   (recommended: the finer partition's cost should be a number) vs
   2e's no-table stance.
g. **Bars** — 2g's .10 / .01 unchanged (recommended: T_beyond sits
   beside .2204 on the same scale).
h. **Process** — build + freeze in one session, 2e's shape (zero
   model contact; recommended) vs the three-session protocol.
i. **The asymmetry re-read (§5.5)** — printed non-gating
   (recommended) vs a second gating test on the difference of
   absorbed fractions (a new statistic with no referent; not
   recommended).
j. **Disclosure placement** — the §2 paragraph verbatim in the
   verdict record and any licensed sentence (recommended yes).
k. **Licences** — as §6.

## 11. Process

Design (this doc + rulings) → build + freeze (`experiments/exp2j`:
the functionals module, the composite-strata builder, the block
thinner, the analyzer with the tree, the referent manifest over every
2d/2g/2h/2i file it reads, fixtures, full-shape worlds for every
terminal on synthetic tallies, the comparison gates, a mutation
battery, the read sweep for unpinned opens, the power record ONCE)
→ tag `exp2j-preregistered` (blob-bound) → projection sealed, with
the same disclosure as 2e's: the projection's author has seen every
number → the analyzer ONCE on Michael's go → `exp2j-closed`. One
pre-committed change. No model contact at any stage; the campaign is
the analyzer run.

Build notes carried from the record, for the freeze's attack list:
every failure label prefix-disjoint from every other (2i freeze R-4
found two gate labels sharing a prefix); the comparison gates are
three-way — re-derived == the predecessor's `verdict.json` on disk ==
the literal pin, exact float equality (2e's `check_comparison_2d`);
the block thinner's k = 64 gate and the tie-fallback bucket rule each
get a fixture that would fail under 2i's strict-`>` rule alone; the
read sweep must show every `open`/`gzip.open` on the verdict path
pinned; and the power record is written once and refused twice.
