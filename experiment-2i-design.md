# Experiment 2i — Design Doc: The Cross-Family Test — Is the Sampled Channel's Item Ordering Pythia's, or the Items'?

**Status: session 1 (design) written 2026-08-25, at Exp 2h's closeout,
on Michael's word ("design"); §9 dials a–k RULED the same day ("dials
approved" — every dial as recommended). Build (session 2) and the
adversarial freeze (session 3) follow. Model contact comes in three
locked stages after the tag (§7): the OLMo-2 1B sampled counts
(sealed), the OLMo-2 7B stage-1 endpoint (sealed, fixes the rung set
and the power record), then the 7B checkpoint sweep. No OLMo model has
been queried by this program; no quantity from any OLMo checkpoint
exists anywhere in it.**

Lineage: 2g (NO-FORECAST; sampler competitor fired, T .167) → 2h
(CONFIRMED as a preregistered primary, T .202): at item grain, the
order in which Pythia's training makes 2c's rising items emittable is
forecast by how often Pythia-1b already emits them, through structural
difficulty strata, with the probe adding nothing. Both verdicts
disclosed the same limit (2h §5): a sampled rate is both
*reachability* — how close an item already is to that model's output —
and *un-named difficulty* — how easy the item is for any model trained
on language at scale. Two sealed outcomes inside one family cannot
tell those apart. A second family can.

## 1. The question

**Does Pythia-1b's committed sampled rate per item — 2d's 64
temperature-1.0 draws, on disk since 2026-08-22 — forecast the order
in which OLMo-2 7B's stage-1 training makes the same items emittable,
within the same difficulty strata; and does OLMo-2 1B's own sampled
rate forecast that order beyond it?**

Two preregistered tests on one sealed outcome, read jointly:

- **Test A (cross-family).** Predictor x_A = Pythia-1b's count. Fires
  iff the stratified concordance clears 2g's bar (p < .01, T ≥ .10).
- **Test B (within-family, beyond cross).** Predictor x_B = OLMo-2 1B's
  count, in composite strata = base stratum | 1[x_A > 0] (2g/2h's own
  "beyond" construction, the sampler's zero cut). Fires on the same
  rule.

Worlds (after INSUFFICIENT_DATA):

- **SHARED** — A fires, B does not. The ordering transfers across
  architecture, tokenizer, corpus and recipe, and the same-family small
  model adds nothing beyond it: at this resolution the sampled channel
  reads a property of the items under language-scale training, not of
  Pythia's lineage.
- **LINEAGE** — B fires, A does not. The ordering is family-specific:
  reachability from the smaller model of the SAME lineage forecasts;
  the cross-family predictor does not.
- **BOTH** — both fire: a shared component and a lineage-specific
  increment, each reported with its partial.
- **NEITHER** — neither fires. The 2g/2h finding does not reproduce on
  OLMo even within family (or the battery does not transfer); the
  Pythia result is demoted to "on Pythia".

The tests are firing rules, not a head-to-head of magnitudes: x_A is
heavily zero-inflated (Pythia-1b emits most items in 0 of 64 draws)
and x_B is expected spread (OLMo-2 1B is trained on 4T tokens), so
T_A and T_B live on different tie structures and are never compared
as numbers. Within-alone (x_B unconditioned) and cross-beyond-within
(x_A in strata of x_B's median bucket) are printed beside them.

## 2. What is known and what is sealed (disclosure)

Known: everything 2h knew plus 2h's verdict — the per-rung loci at
2.8b and 6.9b, the 410m replication, the textures. x_A is historically
prior (2d's close). The strata are 2g's committed table, unchanged.
The 2c battery — items, shots, verify criterion, 2d's model-free
floors — is frozen and public. The Hub inventory of OLMo-2's
checkpoint branches was read on 2026-08-25 (metadata only: branch
names, file lists, sizes, commits; no weights touched).

Not known to anyone in this program: any output of any OLMo model on
any item. The design cannot have been tuned to OLMo's behaviour; it
is 2h's design with the family swapped and one predictor added.

Sealed in order (§7): x_B before the endpoint; the endpoint before the
sweep; the projection before gate 1.

What "cross-family" means here, stated plainly: a different
architecture (OLMo-2: QK-norm, reordered norms, no biases), a
different tokenizer (100k GPT-2-style BPE; Pythia's is GPT-NeoX's
50k), a different corpus (OLMo-Mix-1124 / Dolma-derived vs the Pile)
and recipe. It does NOT mean disjoint training data: both corpora
draw on Common Crawl, Wikipedia, arXiv and public code, so shared
content survives at the source level. SHARED therefore reads "the
ordering is not Pythia's lineage's", not "the ordering owes nothing to
shared text".

## 3. Instrument — 2h's, with the family swapped and one predictor added

Everything not named here is `experiments/exp2g` / `exp2h` machinery
imported frozen: 2c's harness (2-shot prompts, `MAX_NEW_TOKENS` by
answer type, greedy fp16, 2c's normalizer + exact match under 3c's
total wrapper), 2g's strata, statistics (within-stratum Somers' D,
mean over rungs, permutation within rung × stratum, 10,000, seed 0;
1,000-resample bootstrap CI per rung), eligibility (n_pos ≥ 20
realized), the count outcome with first-correct printed, the referent
discipline, the tree-totality closure (2h F-1), gate-1 coverage
attestation (2h F-2), blob-bound tags (2h F-3). The deltas:

1. **A second family's loader.** `load_olmo(repo, revision)` for
   `allenai/OLMo-2-0425-1B` (predictor) and `allenai/OLMo-2-1124-7B`
   (outcome), each revision pinned by commit sha and per-file LFS
   sha256 in a committed manifest (2g's candidate-file rule and
   duplicate-signature refusal carried over; OLMo-2 publishes
   safetensors shards under every branch — 6 × ≈4.9 GB fp32 at 7B,
   2 shards at 1B — so the stale-copy counters are structural zeros
   as at 6.9b and the signature rule is what refuses a mislabelled
   copy). Harness deltas, all mechanical and fixture-pinned: left
   padding with OLMo's own `<|pad|>` (Pythia had none and borrowed
   eos); no BOS (OLMo-2 adds none; the prompt is rendered exactly as
   2c renders it); `terminal_ids` for the sampler = the tokenizer's
   special ids, as exp3. The 7B branch has no `stage1-step0`, so the
   init referent is a seeded `from_config` twin (seed 0, the exp2
   convention), descriptive only and disclosed as not OLMo's real
   init. Tensor digests as 2g.
2. **The predictor stage.** x_B = per-item verified count over 64
   pure T = 1.0 draws (seed 0) from OLMo-2 1B at its stage-1 endpoint
   (`stage1-step1907359-tokens4001B`, the same regime as the
   outcome), on all 34 rungs × 500 items, through exp3's sampler
   (2d's main-tier protocol: fp32, CPU-float32 softmax, committed
   RNG substreams under a new namespace `exp2i`, every raw draw
   stored, verified through 3c's total wrapper). Committed and tagged
   `exp2i-predictor-sealed` before any 7B weight loads. ≈ 1.09 M
   draws; 2d's 1b main tier ran ≈ 6 h on the Mac, and OLMo's 100k
   vocabulary makes the per-step softmax ≈ 2× Pythia's, so 7–9 h.
3. **The endpoint stage.** OLMo-2 7B's stage-1 endpoint
   (`stage1-step928646-tokens3896B`) AND `main` (the stage-2 soup —
   three annealed ingredient runs averaged) through the thin loader on
   all 34 rungs, per-item bits and continuations stored. The endpoint
   record fixes **R** (§4) by rule and feeds the power record;
   `main` is descriptive only — "does mid-training change the
   emittable set?" — never in an outcome. Committed and tagged
   `exp2i-endpoint-sealed` before any intermediate checkpoint loads.
4. **The outcome is 7B's stage-1 grid** — 21 trained checkpoints, 2g's
   shape scaled to the run (928,646 steps, ≈ 4.2 M tokens each):

       S = {1k, 2k, 4k, 8k, 16k, 32k}            (log-spaced head)
         ∪ {64k · j : j = 1 … 14}                (every 64k, 64k … 896k)
         ∪ {928646}                              (endpoint; gate 1)

   All 21 exist on the branch (verified 2026-08-25; the branch is
   every 1,000 steps with seven 2,000-step gaps, none on the grid),
   plus the from_config twin as the step-0 referent. y_i = number of
   grid points at which item i verifies (2g's count outcome; ruling
   f); first-correct step printed beside it. Same disclosure as 2g:
   the head puts 6 of 21 points in the first 3.5 % of training, so
   the count weights earliness, which is the intent.
5. **Gate 1** = the endpoint reproduced through the sweep's checkpoint
   loader: per-item bits identical to the endpoint record on all 34
   rungs, tensor digest equal, 17,000/17,000 continuations compared
   with 0 diffs, coverage attested and required (2h F-2). Two loader
   paths as 2g. A diff halts the sweep with the tree the analyzer
   reads as INSUFFICIENT_DATA.
6. **The tree.** INSUFFICIENT_DATA → the joint reading of Tests A and
   B → SHARED / LINEAGE / BOTH / NEITHER. Each test's per-rung D with
   CI, the pooled D, within-alone, cross-beyond-within, the 410m cross
   replication, the reverse-direction descriptives (x_B against 2g's
   committed 2.8b outcome and 2h's committed 6.9b outcome — outcomes
   KNOWN, so non-gating and disclosed as such; the cheapest
   cross-family reading in the other direction, no new model contact),
   the extra-rung raw D (§4), the flat-rung descriptives, the
   from_config twin and `main` are all printed in every world. No
   SURFACE terminal: the untrained twin's sampled counts are zero by
   construction (2h §3.3), and the from_config 7B twin is a referent,
   not a predictor.

## 4. Rung set, strata and power

**R_OLMo** — the rungs whose 7B stage-1 endpoint count clears 2d's bar
(one-sided exact binomial against 2d's model-free floor, max(majority
share, 1/n_options), 2d's α), fixed at the endpoint stage by rule. It
is not known now; at 3.9 T tokens it may be considerably larger than
Pythia-6.9b's eight.

**Strata.** 2g's committed table covers eleven rungs (carries /
borrows / octal carry-borrow / option position / crosses-100 /
count). The primary statistic for BOTH tests runs over
**R_∩ = R_OLMo ∩ those eleven** — the comparable set, no new degrees
of freedom on the stratification. Rungs in R_OLMo outside the eleven
get single-stratum (raw) D, printed as the extra-rung descriptive,
never in the verdict. If R_∩ has fewer than three rungs, the primary
is declared THIN in the power record and the verdict still runs
(every rung with n_pos ≥ 20 counts).

**Predictor degeneracy.** A rung is dropped from a test — printed —
if its predictor has no two distinct values inside any stratum (D is
undefined there); expected on rungs where OLMo-2 1B is at ceiling
(64/64 on nearly every item).

**Power**, written ONCE at the endpoint stage, before the projection,
per test, with 2h's machinery: x is the REAL predictor (x_A known now;
x_B sealed at stage 1), the positive-outcome count bounded below by
the endpoint count, y generated from a latent mixing rank(x) at
calibrated strength, every simulated cell through the verdict's own
tree. Bar: P(fires | D = .15) ≥ .75 per test, else DECLARED
UNDERPOWERED IN ADVANCE for that test. Disclosed as always: the
number is a claim about the alternative's SHAPE (item-level rank
concordance inside sealed strata); and the union of the four worlds
is not α-calibrated — each test is at α .01 and the world is their
conjunction (3d's calibration lesson stated in advance).

## 5. What 2i does not claim

- SHARED does not say the ordering is "difficulty" in any mechanistic
  sense; it says whatever the sampled channel reads is not specific to
  Pythia's lineage at this resolution. LINEAGE does not say the items
  have no shared order; it says the cross-family predictor does not
  reach it at 64 draws from a 300 B-token 1b model.
- Nothing about OLMo-2 13B/32B, nothing about OLMo 3, nothing about
  stage 2 beyond the one descriptive `main` point, nothing about
  mechanism. Nothing resurrects Prediction 2's probe form.
- The 7B twin is not OLMo's init; step-0 statements are about a seeded
  random network with OLMo-2's architecture.

## 6. Licences, written in advance

- **SHARED:** the essay's sentence changes from "how often *the*
  smaller model already emits them" to "how often *a* smaller model
  already emits them, in either family"; the "structure latent in the
  training distribution" reading gains a cross-family leg at item
  grain; the reachability-vs-difficulty limit in 2h §5 is resolved
  toward the items; the named next experiment is a third family or the
  OLMo-2 13B outcome.
- **LINEAGE:** the essay states the finding as lineage-bound
  ("the smaller model of the same lineage"), adds that Pythia-1b's
  counts carry Pythia's own path; cross-family forecasting is not
  licensed; next is the mechanism question (what about the smaller
  model's output makes an item reachable?).
- **BOTH:** the essay states both components with their partials
  (T_A, T_B, within-alone, cross-beyond-within); the shared component
  is the headline only if T_A's CI excludes zero on the majority of
  R_∩.
- **NEITHER:** the two-outcome finding is demoted to "on Pythia" in
  the essay and experiments.md; the OLMo record is reported in full,
  including the endpoint table; the program's next step is Michael's
  call.
- Any world: the reverse-direction descriptives, `main`, the twin, the
  flat rungs and the extra rungs are reported in full.

## 7. Run plan and model contact

Design (this doc + rulings) → build (`experiments/exp2i`: the OLMo
manifest from the committed Hub scan with the candidate rule, the two
loaders, the sampling stage, the endpoint stage, the sweep runner, the
two-test analyzer with the four worlds, power, referents, fixtures,
worlds for every terminal, mutation deltas) → adversarial freeze →
tag `exp2i-preregistered` (blob-bound: the analyzer, battery, sampler
stage, endpoint stage and sweep runner byte-identical to the tag's
blobs or every one of them refuses) → **stage 1** on Michael's word:
OLMo-2 1B stage-1 endpoint sampled on all 34 rungs (7–9 h), committed,
tagged `exp2i-predictor-sealed` → **stage 2**: 7B stage-1 endpoint +
`main` through the thin loader on all 34 rungs (≈ 2 h + 2 × 29 GB
streamed), R fixed by rule, power printed once, committed, tagged
`exp2i-endpoint-sealed` → projection sealed (named disconfirmers
bracketing the null for EACH test, 2g's lesson) → **stage 3**: the 7B
sweep, gate 1 first, 21 checkpoints × 34 rungs, ≈ 60 min each at fp16
from 6.9b's measured pass (same layer count and width), ≈ 21 h, ≈ 610
GB streamed one checkpoint at a time and deleted (327 GB free), the
watcher committing every record, processes detached per the reaping
gotcha → analyzer once → `exp2i-closed`. One pre-committed change.

Compute: the Mac for every stage (fp16 7B ≈ 14.6 GB; fp32 1B ≈ 5.9 GB;
the stack that has produced nine byte-identical reproductions). The HF
GPU is on the table for this experiment — no byte-identity referent
from the Mac stack is inherited — but gate 1 is byte identity between
this experiment's own two loader paths, which is safest on one
deterministic stack; the GPU is the fallback if the Mac is needed
elsewhere, and if used, every stage moves with it.

Sanctioned preflight (dial j): before the tag, 2c's harness on OLMo-2
1B `main` for 20 items each of `antonym` and `add3_mid`, continuations
printed to the ledger and NOT stored anywhere the analyzer reads — a
format check that the prompt renders, the model stops, and the
normalizer parses what OLMo emits. The only pre-tag model contact,
and only on his word.

## 8. Alternatives considered

- **Cross-only** (Test A alone; no 1B sampling; saves 7–9 h): cannot
  tell LINEAGE from "the battery does not transfer to OLMo" — a null
  would be uninterpretable in exactly the way 2c's was.
- **Within-only** (OLMo 1B → 7B, a second-family replication of 2g/2h;
  no cross test): answers "does the phenomenon replicate" but leaves
  the reachability-vs-difficulty limit where 2h left it; the cross
  predictor costs nothing (already on disk), so leaving it out buys
  nothing.
- **Both** (this design): contains both, one sweep.

## 9. Dials — RULED by Michael 2026-08-25 ("dials approved"): every dial as recommended — a OLMo-2 1B → 7B; b stage 1 only, `main` descriptive; c the 21-point grid; d x_B at the 1B's stage-1 endpoint; e x_A's zero cut; f R_∩ with extra rungs raw; g .10 / .01; h reverse-direction descriptives printed; i Mac for every stage; j the 40-item preflight on his word; k licences as §6

a. **Family and sizes** — OLMo-2 1B (predictor) → OLMo-2 7B (outcome)
   (recommended: fp16 7B fits the Mac at 6.9b's cost; 928 stage-1
   points) vs 13B outcome (646 points, 52 GB fp32 shards, fp16 ≈ 27 GB,
   ~2× the time) vs OLMo 3 7B (1,483 points, newer, less studied).
b. **Outcome regime** — stage 1 only, endpoint `stage1-step928646`,
   `main` one descriptive point (recommended: one data mix on the
   grid) vs `main` as the endpoint (mixes the anneal into the count).
c. **Grid** — the 21-point shape in §3.4 (recommended) vs every 32k
   (35 points, ≈ 35 h) vs 2g's literal count with every 100k (16).
d. **Predictor checkpoint for x_B** — the 1B's stage-1 endpoint
   (recommended: regime-matched to the outcome) vs `main` vs both
   (doubles stage 1).
e. **Test B's conditioning** — composite strata with x_A's zero cut
   (recommended: 2g/2h's construction, unchanged direction) vs x_A's
   median (near-degenerate on a zero-inflated predictor).
f. **Primary rung set** — R_∩ with extra rungs raw-descriptive
   (recommended: no new strata) vs extending the covariate table to
   all 34 at build (new degrees of freedom before the outcome, each
   needing its own justification).
g. **Effect bar and α** — 2g's .10 / .01 per test (recommended).
h. **Reverse-direction descriptives** — print x_B against 2g's and
   2h's known outcomes (recommended: no contact, disclosed as known)
   vs omit.
i. **Compute** — Mac for every stage (recommended) vs HF GPU for the
   sweep (every stage moves with it).
j. **Preflight** — the sanctioned 40-item format check on 1B `main`
   before the tag (recommended) vs none (a harness failure would then
   surface at stage 1 as a ledgered stop).
k. **Licences** — as §6.
