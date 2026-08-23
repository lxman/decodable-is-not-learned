# Experiment 2g — Design Doc: The Sealed Forecast — Does a Probe Reading at 1b Forecast the Order in Which 2.8b's Training Makes Items Emittable?

**Status: session 1 (design) written 2026-08-23; §11 DIALS RULED by
Michael the same day ("dials approved, write the experiment"), applied
in place. Build (session 2) and the adversarial freeze (session 3)
follow on his word. Model contact is in two locked stages (§9): the
predictor collection after `exp2g-preregistered`, the checkpoint sweep
after `exp2g-predictor-sealed`. No intermediate checkpoint of any
Pythia size has ever been queried in this program.**

Lineage: 2c (probe ladder, FAIL) → 2d (sampling ladder, FAIL; §9
named this successor) → 2e (floor as covariate, FAIL) → 2f (ladder
order, LADDER) → 2g. 2d's §9 named the intermediate-checkpoint
experiment as "the natural next experiment if 2d PASSes and the wrong
one to run if it does not", with the sampler as the predictor. 2d did
not pass and 2e showed the sampler's ordering information on this
battery is a .61, threshold or no threshold. What changed the
predictor is 2f: on the two rungs 2c's starved probe had called
silent, a probe with a label the representation could carry read the
answer's digit at 410m and 1b in four cells of four (.23–.27 against
bars of .17–.19, twins .04–.10) where the generators read it in one.
The from-below instrument with signal on this battery is the
matched-label probe. 2g seals it against an outcome nobody has seen.

## 1. The question, and what the design session found

**At item grain, on a sealed outcome: does what a 1b representation
already carries about an item's answer forecast how early in 2.8b's
training that item becomes emittable — beyond the item's structural
difficulty?**

This is Prediction 2 in its resolution form: the larger lens resolves
first what the smaller lens already half-carries. It is also the
shape of 3d (a forecast at item grain, the predictor fixed before the
tranche exists), with the probe in place of a string functional and
training time in place of a new tranche of seeds.

What the design session found, three things:

1. **The rung-level version of this experiment cannot resolve.** On
   the checkpoint axis the only rung-level quantity that is sealed is
   the training step at which a rung first clears its floor; which
   rungs clear at the final checkpoint is 2c's committed table
   (§2). Applying 2d's binomial bar to 2c's committed 2.8b counts,
   **seven** rungs clear at 2.8b final — antonym (272 vs bar 149),
   antonym6 (149 vs 104), add_base8 (44 vs 24), sub_base8 (91 vs 42),
   add3_mid (43 vs 9), sub3_mid (264 vs 15), arith_next (137 vs 19) —
   in five families. median5 (113 vs 122) and sub4_mid (4 vs 9) sit
   above their floors and under the bar; count_div13 (58 vs 99) and
   odd6 (61 vs 104) are below. Seven points in five family blocks
   give a block-permutation group of eight placements; no bar choice
   makes that a test. The rung-level ordering is a descriptive in §6.
2. **The item-level version is powered and sealed.** Within each
   clearing rung, which of the 500 eval items 2.8b's training makes
   emittable, and how early, is 500 outcomes per rung that no one has
   seen, against a per-item predictor that is computed, committed and
   tagged before the first checkpoint loads. 3d's lesson applies in
   advance: the alternative is modelled in the tie structure's own
   terms (most items never verify; the informative pairs are
   (verifies, never) pairs; the count of such items per rung is
   bounded below by the known final-checkpoint count).
3. **The floor problem returns at item grain, and the strata are its
   answer.** 2c's lesson was that a format-level competence is
   credited its guessing rate. At item grain the analogue is: a model
   early in training emits the common answer (the majority option
   slot, the majority count), and a probe trained on the same label
   distribution has the same prior, so "the probe is confident on the
   items the model learns first" can be manufactured by a shared
   class prior with no presence in it. For the option-position and
   count rungs the label IS the structural covariate, and permuting
   within strata of it removes the prior on both sides. For the
   digit rungs the label distribution is near-uniform by construction
   (the floors .006–.056 are full-answer majority shares; the digit
   label's own majority share is ~.1), so the prior is weak; a
   label × covariate stratification is printed as a sensitivity
   (§6.4) rather than made the primary, because two-way strata thin
   the smaller rungs below their eligibility floor.

## 2. What is known to the designer (disclosure)

- 2c's committed m4 argmax records at 2.8b, 6.9b and 12b final
  weights for all 34 rungs: the per-rung correct counts and nothing
  per item (m4 stored counts only). These fix which rungs clear at
  the final checkpoint (§1) and bound the number of items with a
  nonzero outcome from below. The analyzer's rung sets are defined
  from these committed counts, not from the sweep.
- 2d's committed per-item generator records at 410m and 1b final
  weights: argmax continuations (500 per rung) and 64 T=1.0 draws per
  item (seed 0). These supply two named secondaries (§6.4) and were
  known before this doc was written; they are not the predictor.
- 2c's committed probe records (starved split, 2c's labels) and 2f's
  four-cell matched-label probe readings at 410m/1b. 2f's readings
  are the machinery gate's known answers (§5).
- **Not known to anyone:** any quantity at any intermediate
  checkpoint of any Pythia size — no per-item verify bit, no per-rung
  trajectory, no first-clear step. The HF revisions `step0` …
  `step143000` (155 refs per size, listed 2026-08-23) have never been
  downloaded by this program.

A PASS therefore licenses a sentence about a sealed outcome. The
predictor side is protected by the tag (`exp2g-predictor-sealed`,
§5); the outcome side by the fact that it does not exist until the
sweep runs.

## 3. The predictor

**Label, one per rung** (the matched label: a quantity the
representation can carry and every instrument can read):

| rung | label | classes | source |
|---|---|---|---|
| antonym, antonym6 | printed position of the antonym | 4, 6 | 2c `probe_label` |
| median5 | printed position of the median | 5 | 2c `probe_label` |
| odd6 | printed position of the odd word | 6 | 2c `probe_label` |
| add_base8, sub_base8 | ones digit of the octal result | 8 | 2c `probe_label` |
| add3_mid, sub3_mid, sub4_mid | middle digit (tens; hundreds for 4-digit) | 10 | 2c `probe_label` (2f's split) |
| arith_next | last digit of a + 4d | 10 | 2f's label (ruling a there); 2c's mod-7 printed |
| count_div13 | the count | ~10 | 2c `probe_label` |

Known-answer gate per rung: the label function reproduces the
committed `probe_label` field 500/500 on the eval items (2f's gate
pattern); arith_next's against 2f's committed label record.

**Probe:** 2f's `fit_probe` — `StandardScaler` + `LogisticRegression`
with 2b's `C = 1.0`, `MAX_ITER = 100` — trained on the committed
probe-item activations (2c's `results/activations/<size>_<mode>/
<rung>.npz`, 2b's tree for the four carried survivors antonym,
add_base8, add3_mid, sub3_mid; 2,000 probe items, 1,000 for
arith_next and sub_base8; sha-pinned by `activations_sha256.txt`),
**with the label above and a plain item split — no basis starving.**
The ninth lesson applied: a basis-starved split measures
generalization to held-out basis values, not presence, and the
committed starved probes scored below chance at every real site on
these rungs (2f build finding A).

**Site family:** 2f's — every `LAYER_STRIDE`-th layer plus the final
layer, × the two token positions: 18 sites at 410m, 14 at 1b.

**Site selection — by seeded cross-validation on the probe items
only** (2f's `cv_probe_sites`, holdout .2, one seed fixed in the
build): the site with the highest held-out accuracy. The eval items
and the outcome never enter the choice. 2f's rule (best site by eval
accuracy, Bonferroni over the family) is printed as a sensitivity
(§6.4); it is outcome-free too, but it reads the eval labels.

**Per-item score:** x_i = the probe's log-probability of item i's true
label at the CV-chosen site, from a probe refit on all probe items,
applied to the eval item's activation. Not the 0/1 correctness —
binary scores tie most pairs and throw the concordance away (ruling
a). Scores at both sizes; **1b is the primary size** (the rung of the
ladder nearest the outcome), 410m the replication (ruling b).

**Twin:** 2b's `load_pythia(untrained=True, seed=0)` — the seeded init
on this stack, the same network 2c/2f's twins were — with the same
label, the same split, the same site rule and its own per-item
scores. Its role is in the tree (§6.3): a random network's read of
the prompt must not forecast the outcome.

**The seal.** One committed file, `results/predictor/predictor.json`:
for every rung in the sweep set (§4), every eval item, both sizes,
trained and twin — the score, the CV-chosen site, the CV table, the
probe's eval accuracy at that site, and the shas of every input it
was computed from. Listed in `predictor_sha256.txt`; committed; tagged
**`exp2g-predictor-sealed`**. The outcome runner refuses to load any
checkpoint unless that tag exists and the file's sha matches the
tag's (2c's `require_stage1_tag` pattern, enforced in the Python
runner, not the shell); the analyzer pins the same sha and refuses a
tree whose predictor differs.

## 4. The outcome

**Instrument:** 2c's `evaluate_argmax` verbatim — `render_prompt` with
the rung's two committed shots, greedy decoding, `MAX_NEW_TOKENS` by
answer type, `normalize_answer` under 3c's total wrapper, exact match
(with 2d's F-3 disclosure carried: base12_digitsum and base13 are
first-digit-run matched, both flat, not in any rung set) — with one
addition: **the per-item verify bit and the raw continuation are
stored at every checkpoint.** m4 stored counts; 2g's outcome is per
item.

**Size:** 2.8b adjudicates (ruling: 2026-08-23). 12b replicates,
non-gating, on a coarser grid.

**Grid at 2.8b, 23 checkpoints:** `step0` (Pythia's real init, a
descriptive control — never in an outcome) and the 22 trained
checkpoints

    S = {1000, 2000, 4000, 8000, 16000, 32000, 64000}          (log-spaced)
      ∪ {10000, 20000, 30000, …, 140000}                       (every 10k)
      ∪ {143000}                                               (final; gate)

i.e. 1k, 2k, 4k, 8k, 10k, 16k, 20k, 30k, 32k, 40k, 50k, 60k, 64k, 70k,
80k, 90k, 100k, 110k, 120k, 130k, 140k, 143k. All 34 rungs at every
checkpoint (m4's measured 2.8b pass: 34 rungs × 500 items in ~24 min
on the Mac). Disclosed: the log-spaced head puts 7 of 22 points in
the first 14 % of training, so the count outcome weights earliness.
That is the intent — the question is how EARLY — and the first-correct
step is printed beside it as the sensitivity (§6.4).

**Grid at 12b, 8 checkpoints:** 1k, 4k, 16k, 32k, 64k, 100k, 130k,
143k; the 11 rungs of 2d's rising label (§4.1), ~31 min per
checkpoint.

**Per-item outcome:** y_i = |{ s ∈ S : item i verifies at s }| ∈
{0, …, 22}. Printed beside it, per item: the first-correct step, the
last-correct step, and the stabilization step (the first s after
which every later grid point verifies; ∞ if none).

**Rung-level outcome (descriptive):** s*(rung) = the first s ∈ S at
which the rung's correct count clears 2d's binomial bar against its
floor (2d's `binomial_bar`, α .01; floors from 2d's verdict
`per_rung`); ∞ if never. Transient clears on rungs flat at the final
checkpoint are a descriptive on the record — non-monotonicity across
sizes is real (sub3_mid .528 at 2.8b, .028 at 6.9b).

**Streaming and pins:** each checkpoint's weights are downloaded
(revision `stepN`), evaluated, and deleted after its records commit;
peak disk one checkpoint (5.3 GB at 2.8b, 22 GB at 12b). Every record
carries the revision's weight-file shas (from the Hub manifest, and
re-hashed locally), the items sha, the git sha, the predictor tag's
sha, per-item continuations and verify bits. The runner is durable and
resumable per checkpoint × rung (skip-if-exists), with a watcher
committing every checkpoint's records.

**The gate checkpoint runs first (ruling, §5 gate 1):** `step143000`
before any other revision, on both sizes. A halt leaves a tree the
analyzer reads as INSUFFICIENT_DATA by construction — the eighth
lesson built in: no world in the battery may reach a terminal through
a tree the runner cannot leave.

### 4.1 Rung sets, fixed from committed counts

- **R_2.8b (the primary's set):** the rungs whose committed 2c m4
  2.8b correct count clears 2d's bar — antonym, antonym6, add_base8,
  sub_base8, add3_mid, sub3_mid, arith_next (7; families antonym,
  base_arith, mid_digit, seq_extrap). Final counts 272, 149, 44, 91,
  43, 264, 137 — every one ≥ the eligibility floor of 20 (§6.1), so
  the primary's set is fixed now and cannot shrink by the data.
- **R_12b (the replication's set):** the rungs whose 12b count clears
  the bar — antonym, antonym6, add_base8, sub_base8, add3_mid,
  sub4_mid, median5, arith_next, count_div13 (9). sub4_mid's 12b
  count is 12 < 20: THIN in advance, printed, not in T_12b. Eight
  enter.
- **Sweep set:** all 34 rungs at 2.8b; at 12b the union of R_2.8b,
  R_12b and odd6 (11 rungs — 2d's rising label, odd6 clearing only at
  6.9b, carried for the descriptive).
- **Predictor set:** the 11 rungs above, both sizes, trained and twin
  (§9).
- Descriptive only, never in T: item-level c_r for median5, sub4_mid,
  count_div13, odd6 at 2.8b; for sub3_mid and odd6 at 12b.

## 5. Referents — every input a committed value

| referent | where | role |
|---|---|---|
| eval items, shots, answers (34 rungs) | `experiments/exp2c/battery/items/<rung>.json`; `experiments/exp2b/battery/items/<rung>.json` for the 12 carried survivors | prompts, verify keys, labels; shas as 2d pinned (`items_sha256`) |
| probe-item activations, trained + twin, 410m/1b | `experiments/exp2c/results/activations/<size>_<mode>/<rung>.npz` (+ 2b's tree for the four survivors), `activations_sha256.txt` | probe training; site family |
| 2f's eval-item activations + per-site readings | `experiments/exp2f/results/activations_eval/…`, `activations_eval_sha256.txt`, `verdict.json` | machinery gate (§5 G-P) |
| 2f's arith_next label record | `experiments/exp2f/labels_2f.py`, its label gate | label gate |
| 2c m4 records, `2.8b_trained` (34) and `12b_trained` (11 of 34) | `experiments/exp2c/results/m4/<size>_trained/<rung>.json` | gate 1 literals; rung sets (§4.1) |
| Pythia weight shas (final) | `experiments/exp2b/models.py::PYTHIA_SHAS` — 2.8b `2a259cdd…`, 12b `bb1e3e71…` | `step143000` must equal them file-for-file |
| Hub revisions `step0` … `step143000` | EleutherAI/pythia-2.8b, -12b (155 refs each, listed 2026-08-23) | the grid; every record pins the revision's file shas |
| floors (34) and the bar | 2d `verdict.json::per_rung.floor`; `experiments/exp2d/stats_2d.py::binomial_bar` | s*(rung); rung sets |
| 2d argmax continuations at 1b | `experiments/exp2d/results/argmax/1b_trained/<rung>.json` | 1b-performable exclusion (§6.4) |
| 2d main-tier draws at 1b, 64/item | `experiments/exp2d/results/main/1b_trained/<rung>.draws.jsonl.gz` | sampler competitor (§6.4) |
| 2c harness | `experiments/exp2c/harness.py` (`evaluate_argmax`, `render_prompt`, `verify`, `MAX_NEW_TOKENS`), via 2d's `battery_2d` (3c's total wrapper) | the outcome instrument |
| 2f probe machinery | `experiments/exp2f/probe_2f.py` (`fit_probe`, `site_family`, `cv_probe_sites`); 2b `models.load_pythia` | the predictor; the twin |
| difficulty covariates (§6.2) | computed from the item files by `strata_2g.py`, committed with the predictor | the strata |

Every path above is sha-pinned in the build's referent manifest;
every loader refusal is collected and delivered as INSUFFICIENT_DATA
with the reason verbatim (2e's pattern).

**Gates:**

- **G-L (labels):** each rung's label function reproduces the
  committed `probe_label` 500/500 on its eval items and on its probe
  items; arith_next's against 2f's committed record.
- **G-P (predictor machinery):** 2f's four cells (sub3_mid,
  arith_next × 410m, 1b, trained and twin) re-collected by 2g's
  collector and held to 2f's continuity tolerance (rtol/atol 1e-2;
  2f's freeze measured kernel drift ≤ .0055 against ≈ 2,300 for a
  different network); and 2f's per-site eval accuracies reproduced
  exactly by 2g's probe code on 2f's committed activations — probing
  is deterministic on this stack (2f's finding). Gate failure before
  the seal → no seal; the doc's status records it.
- **G-1 (outcome path, 2.8b):** `step143000`'s weight files sha-equal
  to 2c's pinned `main`, and its 34 correct counts equal to m4
  `2.8b_trained` exactly. Runs first; any diff halts; the halted tree
  is INSUFFICIENT_DATA.
- **G-1 (12b):** the same on the 11 sweep rungs against m4
  `12b_trained`. Non-gating for the 2.8b verdict; gating for the 12b
  replication's own record.
- **G-S (the seal):** the predictor file's sha equals the
  `exp2g-predictor-sealed` tag's; the runner refuses to start without
  it; the analyzer refuses a tree without it.
- **Init referent:** `step0`'s per-item verify printed for every rung;
  expected 0 everywhere; a nonzero is a format guess on the record,
  not a halt (floors are model-free).
- **Determinism:** the analyzer byte-identical across two processes on
  the fixture tree; the projection sealed before it runs.

## 6. Statistic, covariates, worlds

### 6.1 The primary

For each rung r ∈ R_2.8b and each eval item i: x_i the sealed 1b
probe score, y_i the count outcome, d_i the rung's difficulty stratum
(§6.2). The informative pairs are

    P_r = { (i, j) : d_i = d_j, y_i ≠ y_j }

and the within-stratum concordance is Somers' D restricted to them:

    c_r = Σ_{(i,j) ∈ P_r} sign(x_i − x_j) · sign(y_i − y_j) / |P_r|

(x-ties contribute 0; range −1 … 1; 0 under exchangeability). The
statistic is the mean over eligible rungs,

    T = mean_{r ∈ R_2.8b, eligible} c_r

— equal weight per rung, class-level (the sixth lesson: the claim is
about the battery's rungs, not its pairs); the pair-weighted pooled D
is printed beside it. **Eligibility:** n_pos(r) = #{ i : y_i > 0 } ≥
20, else THIN. Every rung in R_2.8b has a final-checkpoint count ≥ 43,
so eligibility cannot bite at 2.8b; it is stated for the 12b arm
(sub4_mid) and for completeness.

**Null:** permute x within each (rung, stratum) cell, 10,000 draws,
recompute T; one-sided p = (1 + #{T_perm ≥ T_obs}) / (1 + 10,000).
α = .01. Under this null the probe carries nothing about emission
order beyond the named covariate; family correlation does not enter
it (the permutation is within rung).

**Raw T:** the same with one stratum per rung. **Twin T:** the same
statistic with the twin's sealed scores as x, stratified; its p at
.05.

**Effect bar:** T ≥ .10 (Somers' D .10 ≈ AUC .55; ruling c). Without
it, ~3,000 informative items can make T = .02 significant and
FORECAST would be a statement about n.

### 6.2 Difficulty covariates — fixed now, strata computed at the build

| rung | covariate | levels |
|---|---|---|
| add3_mid | number of carries across the columns | 0–3 (77 / 155 / 184 / 84 items) |
| sub3_mid | number of borrows (a > b: the top column never borrows) | 0–2 (164 / 238 / 98) |
| sub4_mid (12b arm) | number of borrows | 0–3 (84 / 184 / 175 / 57) |
| add_base8, sub_base8 | ones-column carry / borrow | 2 (277 / 223; 309 / 191) |
| antonym, antonym6, median5, odd6 | the answer's printed position | 4 / 6 / 5 / 6 (slot minima 120 / 73 / 89 / 75) |
| arith_next | a + 4d ≥ 100 (the answer has three digits) | 2 (266 / 234) |
| count_div13 (12b arm) | the count itself | 2–10 (15 / 78 / 56 / 79 / 73 / 68 / 67 / 61 / 3) |

Why position, for the option rungs: within one slot, a model that
favours slot 1 and a probe whose prior favours slot 1 have nothing
left to agree on for free; the stratum removes slot bias on both
sides (§1, finding 3). Why the count, for count_div13: the label is
the answer; within one count value a majority-count copier orders
nothing. **Merge rule:** an ordinal stratum with fewer than 10 items
merges into its neighbouring level with the fewer items (ties: the
lower level); nominal strata (positions) are never merged — every slot
carries ≥ 73 items on the committed eval sets. On the committed items
the rule bites only on count_div13 (count 10, 3 items → into 9; count
2, 15 items → into 3); every other stratum is ≥ 57. The counts above
are item-file facts, not outcomes. The strata table is committed with
the predictor and inside the seal.

Disclosed: the stratified null removes the NAMED covariate only. An
unnamed difficulty dimension — the answer token's frequency in the
Pile, say — survives it; the twin is the partial guard (a random
network's read of surface statistics), and the design says so rather
than claiming the confound closed.

### 6.3 Verdict tree (mechanical, in order)

1. **INSUFFICIENT_DATA** — any gate in §5 fails; the 2.8b tree is
   incomplete (any of 23 × 34 records missing; a halted gate leaves
   exactly this); the predictor's sha ≠ the seal tag's; any loader
   refusal.
2. **FORECAST** — p_strat < .01 AND T ≥ .10 AND p_twin ≥ .05.
3. **SURFACE** — p_strat < .01 AND T ≥ .10 AND p_twin < .05: the
   emission order is readable from the prompt by a random network; the
   probe's reading is not evidence of presence for this purpose.
4. **DIFFICULTY-ONLY** — not 2 or 3, AND p_raw < .01 AND p_strat ≥ .01:
   structural difficulty orders emergence; the representation adds
   nothing detectable beyond it.
5. **NO-FORECAST** — everything else. Disclosed inside it by name: a
   significant negative T (the one-sided test leaves it here; printed
   as "inverted at p = …"); p_strat < .01 with T < .10 ("detected
   below the effect bar, T = …").

The tree is complete and exclusive: 2 and 3 partition p_strat < .01
∧ T ≥ .10 by the twin; 4 and 5 partition the remainder by p_raw.

### 6.4 Named secondaries (non-gating, all printed)

- **410m replication:** the same tree on the 410m scores.
- **12b replication:** the same statistic on the 12b grid over R_12b
  (8 eligible); its own tree, its own gate.
- **Rung-level ordering (descriptive):** Spearman between the rung's
  probe margin (1b eval accuracy at the CV site minus the label's
  floor, max(majority label share, 1/K)) and s*(rung) over R_2.8b.
  Seven rungs in five family blocks give 2!·2!·2! = 8 block
  placements; no p is reported, only the point and the table.
- **Sampler competitor:** x = 2d's committed per-item verified count
  at 1b (64 draws); the same T. And the probe's T inside strata of
  (covariate × sampler count 0 / > 0) — the probe beyond the sampler.
- **1b-performable exclusion:** items 2d's committed 1b argmax
  continuation verifies are removed (2d's ruling f at item grain);
  T recomputed. Counts: 87 antonym, 89 antonym6, 4 add_base8, 8
  sub_base8, 1 add3_mid, 0 sub3_mid, 19 arith_next.
- **First-correct step as y** (∞ for never): the same T.
- **Label × covariate strata** for the digit rungs (§1, finding 3).
- **2f's site rule** (best site by eval accuracy) in place of CV.
- **2c's mod-7 label** for arith_next.
- **Per-rung c_r** with a 1,000-draw item bootstrap CI; a figure of
  per-rung accuracy trajectories over S with the per-item first-correct
  histogram.
- **Flat-rung descriptive:** s*(rung) and transient clears for the 27
  rungs not in R_2.8b; `step0` per-rung verify counts.

### 6.5 Licences, written in advance

- **FORECAST:** the essay's Prediction 2 paragraph gains its first
  sealed forecast in scale on a real model: a per-item probe reading
  at 1b, fixed before any checkpoint was loaded, forecast the order in
  which 2.8b's training made 2c's rising items emittable, beyond each
  rung's structural difficulty covariate, on seven rungs in five
  families (T, p, per-rung table; the 12b and 410m replications
  beside it). With 3b–3e it is the program's second complete
  three-signature case and its first in scale rather than in
  sampling. The scope sentence carries: Pythia, this battery, argmax,
  two-shot, exact match, one named covariate per rung, the label's
  presence not the full answer's. Not "Prediction 2 supported"
  unqualified — the rung-level ordering stays descriptive.
- **SURFACE:** the item ordering is visible to a random network; the
  essay's Prediction 2 paragraph says the probe's item-level reading
  at 1b does not separate from surface statistics on this battery,
  and the methods paper gains a candidate lesson (the twin at item
  grain).
- **DIFFICULTY-ONLY:** structural difficulty orders emergence and the
  representation adds nothing detectable; the essay says so, with the
  raw T printed as what a reviewer would have credited.
- **NO-FORECAST:** "not detected at this resolution", blind region
  stated (§7); the sampler competitor and the 12b arm reported
  beside it.
- Any world: the 12b replication, the flat-rung descriptives and the
  `step0` referent are reported in full.

## 7. Power, and the region this design cannot see

**The alternative's shape, modelled in the tie structure's own
terms.** Per rung, most items have y = 0 and the informative pairs are
(y > 0, y = 0); the number of y > 0 items is bounded below by the
committed final-checkpoint count (272, 149, 44, 91, 43, 264, 137) and
above by 500. The build's `power_2g.py` simulates, per rung, x and a
latent w from a bivariate normal within each real stratum with ρ
calibrated so that the within-stratum Somers' D between x and y
equals a target D_true; y = 0 for the 500 − n_pos lowest w (n_pos =
the final count), else a count in 1 … 22 by w's within-positive rank
(a monotone map; the calibration is run on the realized y). Each
simulated battery goes through the verdict's own code (§6.3) and
power = P(FORECAST) over 1,000 simulations at D_true ∈ {.10, .15,
.20}, and P(p_strat < .01) alone beside it. **Bar: .75 at D_true =
.15.** If the bar is not met the experiment is DECLARED UNDERPOWERED
before any checkpoint loads, and the verdict is read under that
declaration. Printed: the minimum detectable T, the null SD of T, each
rung's c_r precision (the small rungs add3_mid and add_base8 at
n_pos ≈ 43 contribute c_r with SE ≈ .09 against ≈ .05 for the large
ones; equal weighting is the class-level choice and its price is
stated).

Rough expectation, to be replaced by the build's numbers: the null SD
of a single D at n_pos 43 is ≈ .09 and at 272 ≈ .05; the mean of
seven has SD ≈ .03; T = .10 is ≈ 3 SD, so the effect bar, not the
α, is the binding constraint at D_true = .15.

**Blind region:** any true within-stratum D below ≈ .10 at 2.8b; any
rung-level ordering at all (descriptive by design); anything at 6.9b;
anything sampling would see that argmax does not (the outcome is
argmax only — sampling across 23 checkpoints is weeks); any item whose
emission depends on a difficulty dimension not named in §6.2 and not
visible to the twin.

**Disclosed weaknesses, written before the data:**

1. The stratified null removes the named covariate only (§6.2).
2. The probe's label is partial — one digit, one position: the
   forecast is of the label's presence, not the full answer's. On the
   option rungs the label is the answer's location, on the digit rungs
   one digit of it.
3. On median5 and antonym, items verified by option-copying chance add
   noise to y; the position strata and the 1b-performable exclusion
   are the partial answer (median5 is not in R_2.8b).
4. Seven rungs in five families: nothing beyond these families is
   licensed.
5. The count outcome's grid weighting (§4).
6. The primary's rung set is defined from known final-checkpoint
   counts (§2) — legitimate, since the item-level outcome is sealed,
   but a reader should know the set was not chosen blind.

## 8. What the dumbest baseline achieves

At item grain the dumbest baseline is the class-prior copier: a
"probe" whose score is the label's training frequency. Its
within-stratum D is exactly 0 on the position and count rungs (the
label is constant within a stratum) and near 0 on the digit rungs
(near-uniform labels). The raw D of the same baseline is what §6.3's
DIFFICULTY-ONLY world catches when the covariate is the label. The
second baseline is the twin: a logistic probe on a random network's
features, with the same label and split — §6.3 makes it a terminal
(SURFACE), not a footnote.

## 9. Model contact

Two locked stages, nothing else.

1. **After `exp2g-preregistered`, on Michael's word — the predictor
   collection:** eval-item activations for the 11 predictor rungs ×
   {410m, 1b} × {trained, twin}: 22,000 forward passes (2f's collector
   did 4 cells in 75 s; ≈ 14 min). G-P runs inside it. Then the probe
   fits (CPU), the strata, the predictor file, the commit, the tag
   **`exp2g-predictor-sealed`**, the projection.
2. **After `exp2g-predictor-sealed` — the sweep:** 2.8b, gate
   checkpoint first, then the remaining 22 in ascending step order;
   34 rungs × 500 items × 23 checkpoints = 391,000 greedy
   generations, ≈ 9.2 h compute plus ≈ 122 GB streamed with the next
   revision downloading while the current one evaluates. Then 12b:
   11 rungs × 500 × 8 = 44,000 generations, ≈ 4.1 h plus ≈ 176 GB.
   Mac only — G-1 is exact equality with m4's Mac-stack counts; the
   HF GPU subscription is disclosed as not usable for this design.

Nothing is sampled. No untrained twin is run at any checkpoint
(`step0` is the init referent; floors are model-free).

## 10. What 2g does not claim

- Nothing about 6.9b or about any size's checkpoints beyond the two
  grids; nothing about sampling at intermediate steps.
- Nothing about mechanism: "emittable at step s" is a verify bit on a
  fixed grid.
- Nothing rung-level (§1, finding 1); nothing beyond the five
  families.
- Nothing about Prediction 2 as a rung-level law of the battery — 2c,
  2d and 2e tested that and found nothing at their resolutions; 2g
  tests the item-grain form.
- **Named successors:** (i) the same design with the predictor taken
  from 2.8b's OWN early checkpoint (Prediction 2 in training time
  rather than in scale — same lineage, same tokenizer; the early step
  is a dial with no referent and would need its own collection); (ii)
  a second model family with intermediate checkpoints (OLMo), where
  the battery's floors and labels transfer and the family's tokenizer
  does not.

## 11. Dials — RULED 2026-08-23 (a–k as recommended)

a. **Score form — RULED log-probability.** log p(true label) at the
   chosen site (recommended) vs 0/1 correctness (ties most pairs).
b. **Primary size — RULED 1b.** 1b primary, 410m replication
   (recommended) vs 2d's mean over sizes.
c. **Effect bar — RULED T ≥ .10.** (recommended) vs significance
   alone.
d. **Eligibility floor — RULED 20.** n_pos ≥ 20 (recommended) vs 10 /
   none. Cannot bite at 2.8b; bites sub4_mid at 12b.
e. **Grid — RULED as §4.** 23 at 2.8b (log head + every 10k + final),
   8 at 12b.
f. **Outcome — RULED the count.** Checkpoints-verified count
   (recommended; first-correct printed) vs first-correct step as
   primary (one lucky emission defines it).
g. **α pair — RULED .01 / .05.** Primary α .01; the twin's forecast
   declared at .05 (the conservative side for SURFACE).
h. **Covariates — RULED as §6.2.** One per rung, fixed now; label ×
   covariate printed for the digit rungs.
i. **Merge rule — RULED as §6.2.** Ordinal strata < 10 merge into the
   smaller neighbour; nominal never.
j. **`step0` — RULED included** as the init referent, never in an
   outcome.
k. **12b grid and set — RULED** 8 checkpoints, the 11 rising rungs,
   R_12b for its T.

Design-session correction applied under the rulings: the rung counts
in the session's first sketch (nine clearing at 2.8b) were by point
estimate; the doc uses 2d's bar (seven). No dial moved.

## 12. Process

Three sessions: this doc; build (label functions with their 500/500
gates, `strata_2g.py`, the collector with G-P, the probe fit with CV
site selection, the predictor file and seal check, the checkpoint
runner with G-1-first and the halt tree, the per-item records, the
analyzer with its tree, worlds for every terminal including the
halted tree, referent manifest, mutation battery, `power_2g.py`
through the verdict's own code, the determinism fixture); adversarial
freeze → tag `exp2g-preregistered`; stage 1 on Michael's word → tag
`exp2g-predictor-sealed` → projection sealed; stage 2 → the analyzer
once → `exp2g-closed`; retrospective; close-out propagation. One
pre-committed change. `PROGRESS.md` from day zero; `FREEZE_CHECKLIST.md`
at the freeze. Timing is budgeted from m4's measured per-pass minutes
and 2f's measured collection, not from a prior experiment's
draws-per-item (2d's timing miss).
