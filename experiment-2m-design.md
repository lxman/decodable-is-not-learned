# Experiment 2m — Design Doc: The Third Family — Does the Cross-Family Forecast Hold on an Outcome That Is Neither Pythia Nor OLMo?

**Status: session 1 (design) written 2026-09-03, at Exp 2l's
close-out, on Michael's word ("Let's continue with the next
experiment"). The outcome family was RULED by Michael the same day
from a four-candidate shortlist (SmolLM3-3B, Comma v0.1-1T, Amber,
Apertus-8B; the shortlist and its reasons are §8): **SmolLM3-3B, stage
1.** §10 DIALS b–p RULED by Michael 2026-09-03 ("as recommended"):
b Tests A/B unconditioned, four worlds, increments + paired difference
printed; c the dense-head 26-point grid; d three descriptive endpoints;
e R_3B by the floor rule, R_PRIMARY = R_3B ∩ the nine; f the projection
by rung type with tolerances, placed against the block SD; g S5
non-gating; h the block-SD line; i the seeded from_config twin; j the
preflight on his word; k bars unchanged; l fp16 with the pre-tag fp32
fallback; m batch 16; n the plain render, pad 128004, left; o the mlx
server stays up unless the preflight shows pressure; p SDD build +
freeze in one session. No model contact of any kind has occurred; the
Hub was read for metadata only (§2).** Model contact,
when sanctioned: SmolLM3-3B ONLY, on the OUTCOME side — its stage-1
endpoint, its last pretraining checkpoint and the released base at the
endpoint stage, then its stage-1 grid and a seeded twin in the sweep.
Every predictor is already committed and tagged; nothing is sampled.
**RATIFIED by Michael 2026-09-04 ('go'): freeze findings F-1..F-3 closed;
slips (a)–(k) applied with the (i) amendment; final-review R-1 applied;
tag `exp2m-preregistered` follows.**

2l closed BOTH — the program's first cross-family forecast to clear
its preregistered bar on a sealed outcome — and its §6 licence named
the next experiment under that world: a third family. 2m is that
experiment: 2l's construction with the outcome model swapped for one
that shares neither architecture, tokenizer, corpus nor recipe with
Pythia or OLMo, and both committed predictors read against it.

## 1. The question

**Does Pythia-1b's committed 256-draw count (Experiment 2k, tag
`exp2k-predictor-sealed`) forecast the order in which SmolLM3-3B's
stage-1 training — an outcome nobody has queried — makes 2c's items
emittable, within 2g's difficulty strata; and does OLMo-2 1B's
committed 64-draw count (Experiment 2i, tag `exp2i-predictor-sealed`)
forecast that same order?**

Both predictors are cross-family with respect to the outcome. That
changes what the second test means: in 2i and 2l, Test B was the
same-lineage increment beyond the cross-family read; here there is no
same-lineage small model, and the two tests are symmetric reads of one
sealed outcome by small models of two other families. So each is read
UNCONDITIONED on its own bar, and the increments are printed beside
them (§5, S3) rather than made the test:

- **Test A (Pythia → third family, 256 draws).** Predictor x_A =
  Pythia-1b's 256-draw count (2k). Fires iff the stratified
  concordance clears 2g's bar (p < .01, T ≥ .10).
- **Test B (OLMo-2 → third family, 64 draws).** Predictor x_B =
  OLMo-2 1B's 64-draw count (2i). Fires on the same rule, in the same
  strata, on the same outcome.

Worlds (after INSUFFICIENT_DATA):

- **SHARED** — both fire: the ordering is read by small models of two
  families that share nothing with the outcome family's architecture,
  tokenizer or recipe; the cross-family sentence generalises past one
  predictor family and one outcome family.
- **PYTHIA-ONLY** — A fires, B does not: the Pile-trained predictor
  reaches the third family's order and the Dolma-trained one does
  not. Density is the first suspect (x_B has 64 draws; 2k placed 256
  Pythia-1b draws at ≈ 10 OLMo-2 1B draws, so x_B is the DENSER read
  and this world would be surprising on density grounds — S1 and S4
  adjudicate descriptively).
- **OLMO-ONLY** — B fires, A does not: the read that transfers is the
  one whose corpus overlaps the outcome's (§2: OLMo-2 and SmolLM3 both
  draw on DCLM-derived web; the Pile predates DCLM). The shared-text
  caveat 2i and 2l carried becomes the leading account, and the
  corpus question is the named next experiment.
- **NEITHER** — the 2g/2h/2i/2k/2l finding does not reach this family
  at this resolution (or the battery does not transfer to it).

Test A and Test B share the outcome, the strata and the rung set, so
unlike 2l their magnitudes ARE comparable on one tie structure; the
paired difference T_B − T_A is printed with a bootstrap interval as a
descriptive (S3), with the density caveat (256 vs 64 draws) attached.
The worlds are firing rules on each test alone; the union of the four
is not α-calibrated (each test at α .01; 3d's calibration lesson).

## 2. What is known and what is sealed (disclosure)

**Known:** everything through 2l's close-out — four sealed forecasts
(2g's sampler competitor on Pythia-2.8b, 2h on 6.9b, 2i on OLMo-2 7B,
2l on OLMo-2 13B), 2j's mechanism reading, 2k's DENSITY result, and
2l's full texture on 13B: Test A .1261 (per rung add_base8 .459,
sub_base8 .292, arith_next .139, odd6 .104, sub3_mid .098, antonym6
.098, add3_mid .013, sub4_mid −.002, antonym −.066), Test B .1814
(antonym +.256, antonym6 +.239, add_base8 +.566), the 64-draw blocks
all sub-bar (.072–.080), the ladder .0760 → .1005 → .1115 → .1261,
410m .1270 ≥ 1b, within-alone .2045 / cross-beyond-within .0770, the
matched increment +.0687, S5's answer prior .1848, and the antonym
SIGN SPLIT — the cross-family component is arithmetic-heavy and the
option-rung structure lineage-private. The predictors x_A^(64/128/192/
256) (both sizes), x_B^(64) and 2j's π are historically prior and
tag-bound.

**The Hub inventory of SmolLM3-3B was read on 2026-09-03 (metadata
only, no weight touched):** `HuggingFaceTB/SmolLM3-3B-checkpoints`
carries 86 stage-1 revisions `stage1-step-40000` … `stage1-step-
3440000` at 40,000-step spacing (the README: checkpoints every 40,000
steps = 94.4 B tokens at a global batch of 2,359,296 tokens; stage 1 =
steps 0–3,450,000, stage 2 = 19 revisions to 4,200,000, stage 3 = 13
revisions to 4,720,000, then two long-context stages), each revision
two safetensors shards (4.97 + 1.18 GB, bf16) with LFS sha256s in the
Hub metadata plus `model.safetensors.index.json`; the 86 stage-1
first-shard signatures are all distinct (no stale copies — the
structural zero 2g's rule guards). The stage-1 endpoint's revision
commit is `d07a5a83dd011f3f084e9d2f1b47f51e524ca8d4`. The repo's
`main` holds no weights; the released base is a separate repo,
`HuggingFaceTB/SmolLM3-3B-Base` (one branch, commit `d78a42f7…`, 3.08 B
parameters, 65,536-token context after extension, rope θ 5·10⁶ against
stage 1's 4,096 / 5·10⁴). The tokenizer is a 128,256-entry Llama-3-
style BPE whose post-processor adds NO special token on a plain render
(`TemplateProcessing` with an empty special-token map), declares no
BOS and no pad token, and carries `<|finetune_right_pad_id|>` (128004)
and `<|end_of_text|>` (128001) in its vocabulary. The stage-1 config:
`SmolLM3ForCausalLM`, 36 layers, hidden 2048, GQA 16/4, NoPE on every
fourth layer. transformers 5.13.0 (the Mac stack) exposes the class
natively — no remote code.

**Not known to anyone in this program:** any output of SmolLM3-3B on
any item, at any checkpoint. The outcome is sealed in 2l's sense: the
predictors were committed (2i 2026-08-26, 2k 2026-08-30) before this
family was named, and the design is 2l's with the outcome swapped.

**What "cross-family" means here,** in 2i §2's terms: a different
architecture (NoPE-hybrid attention, GQA), a different tokenizer
(128k Llama-3-style BPE; Pythia's is GPT-NeoX's 50k, OLMo-2's a 100k
GPT-2-style BPE), a different corpus and a different recipe (a three-
stage curriculum, 11.2 T tokens in total, stage 1 ≈ 8.1 T). It does
NOT mean disjoint training data — and the overlap is asymmetric, which
§1's worlds use: SmolLM3's stage-1 mix (its published config) lists
DCLM, FineWeb-Edu, FineMath, FineWeb2 and code sources; OLMo-2's stage
1 is OLMo-Mix-1124, DCLM-baseline-dominated; Pythia's Pile predates
DCLM and FineWeb entirely, sharing only Common Crawl, Wikipedia, arXiv
and public code at the source level. SHARED therefore reads "the
ordering is not any one lineage's and not any one web corpus's";
OLMO-ONLY reads "the transfer follows the corpus".

**What 2l's texture makes foreseeable, stated now:** the per-rung
readings on 13B are the projection's raw material, and 2l's process
note 3 is applied — the projection is written by rung TYPE (arithmetic:
add3_mid, sub3_mid, sub4_mid, add_base8, sub_base8, arith_next;
option: antonym, antonym6, odd6), with the sign split as the type-level
prior. But the transfer of ITEM order from OLMo-2's training to a
third family's is unmeasured; the verdict-level call is a genuine
forecast, and its texture is graded as the test. Two structural facts
about this outcome are foreseeable and disclosed: (i) the first
available checkpoint sits at 94 B tokens (1.2 % of stage 1) where 13B's
grid began at 8 B (0.17 %), so the head is coarser, the step-1000
collapse window 2l saw is not observable, and items already emittable
at step 40,000 sit at the count ceiling from the first grid point —
the ceiling fraction is printed per rung (§5, S7); (ii) at 3 B
parameters and 8 T tokens the endpoint may clear rungs 13B did not,
or fail some it did (R_3B is fixed by rule at the endpoint stage, §4).

**Sealed in order (§7):** the instrument (`exp2m-preregistered`, blob-
bound) before any SmolLM3 weight loads; the endpoint stage (`exp2m-
endpoint-sealed`: the endpoint records, the rung set, the power
record) before the sweep; the projection before gate 1. There is no
predictor stage.

**Pre-tag disclosure rule** (checklist item 27): any execution of 2m's
analyzer on the real tree before the tag is logged here before the
tag is cut, with what it printed. At the time of writing the analyzer
does not exist; on the real pre-campaign tree every execution must
land INSUFFICIENT_DATA (no SmolLM3 records) and print no T.

Logged (build Task 5, 2026-09-03/04, before the tag). Every execution
of `analyze_2m.run()` on the REAL pre-campaign tree landed
INSUFFICIENT_DATA and printed no T — no SmolLM3-3B endpoint, sweep,
rung-set or power record exists, so the run refuses at the endpoint
stage after executing every predictor-side loader:

1. `experiments/exp2m/tests/import_scan_2m.py`, run three times (once
   before Task 5's edits to `verify_referents_2m.py`, once after, and
   once more after the final-review fix wave's M-3 correction to the
   same file re-moved its sha a second time) to pin
   `IMPORTED_SHA256_2M`: `INSUFFICIENT_DATA`, 11 referent/loader
   failures (the missing prereg tag plus the absent endpoint/rung-set/
   power/sweep records), no T, nothing written, same 4-module shape all
   three times.
2. `experiments/exp2m/tests/read_sweep_2m.py`, once:
   `INSUFFICIENT_DATA`, 10 referent/loader failures (the prereg tag
   binds through the sweep's own stand-in, so only the absent campaign
   artifacts remain), no T, `write=False`, 0 writes observed.
3. Task 3's real-tree analyzer tests and Task 5's world/totality
   modules, which run `analyze_2m.run()` on SYNTHETIC roots and, in
   `test_run_on_empty_tree_is_insufficient_never_raises`, on an empty
   one: INSUFFICIENT_DATA in every case, no T on the real tree.

The cold battery's item 10 inspects the real `EXP2M` tree directly and
does not call `run()`; it printed "endpoint/rung set: absent —
pre-campaign", "power: absent — pre-campaign", "sweep: absent —
pre-campaign".

Logged (the adversarial freeze, 2026-09-04, before the tag). Two more
executions of `analyze_2m.run()` on the REAL pre-campaign tree, both
INSUFFICIENT_DATA with no T and nothing written:

4. `experiments/exp2m/tests/import_scan_2m.py`, once more, after freeze
   F-2's edit to `verify_referents_2m.py` — this is the reading now
   pinned as `IMPORTED_SHA256_2M` (4 modules, unchanged in membership):
   `INSUFFICIENT_DATA`, 11 referent/loader failures (the missing prereg
   tag plus the absent endpoint/rung-set/power/sweep records), no T.
5. `experiments/exp2m/tests/read_sweep_2m.py`, once more, cold at the
   freeze: `INSUFFICIENT_DATA`, 10 referent/loader failures, no T,
   `write=False`, 0 writes observed, 5,116 distinct paths read, bucket
   (e) unpinned = 0.

The freeze's own other `run()` calls were all on SYNTHETIC roots — the
seventeen runner-left tree shapes it enumerated, the F-1 and F-2
demonstrations, the determinism pair and the world/totality modules —
the same class as the build's, and none of them touched the real tree.
No model was loaded and no network call was made at any point in the
freeze.

## 3. Instrument — 2l's, with the outcome model swapped and Test B unconditioned

Everything not named here is `experiments/exp2l` / `exp2k` / `exp2i`
machinery imported frozen: 2c's harness, 2g's strata and statistics
(within-stratum Somers' D, mean over rungs, permutation within rung ×
stratum, 10,000, seed 0; bootstrap CI per rung), eligibility n_pos ≥
20, the count outcome with first-correct printed, the referent
discipline, the tree-totality closure, gate-1 coverage attestation +
re-derivation, blob-bound tags, the import-surface pin from commit one
(2j F-1), `pins_active` (2k D-1), the candidate-file loader with the
per-entry `config.json` write (2i stop #1), the THIN guard keyed to
|R_PRIMARY| (2l F-4), the halt-marker rule (2k F-1). The deltas:

1. **The outcome model.** `HuggingFaceTB/SmolLM3-3B-checkpoints`,
   stage 1: 3.08 B parameters, two safetensors shards (6.15 GB bf16 per
   revision, fp16 at load ≈ 6.2 GB on the Mac's 48 GB), per-revision
   commit sha and per-file LFS sha256 in a committed manifest (2g's
   candidate rule, duplicate-signature refusal); the index file pinned
   by the revision commit alone (2l's disclosure, unchanged). No step-0
   checkpoint exists on the branch, so the init referent is 2i's
   construction: a seeded `from_config` twin of the stage-1 config —
   descriptive, never in an outcome, scored once in the sweep, and
   disclosed as a stand-in for an initialisation this program cannot
   download.

   The twin's config AND its tokenizer are taken at the ENDPOINT's
   commit (`config_commit` in the manifest's twin entry): a twin built
   from another commit's config is a different initialisation, and the
   analyzer measures `config_source` against
   `f"{REPO_CKPT}@{config_commit}"`.

   The checkpoint record attests a sha for every candidate
   file it stages; the analyzer requires that coverage plus the
   record's revision, commit and tensor digest (the last against the
   digest every one of the step's 34 item records carries).
2. **A third family's tokenizer, pinned.** 2i's `check_tokenizer`
   pattern with SmolLM3's facts: left padding; `PAD_TOKEN_ID_2M =
   128004` (`<|finetune_right_pad_id|>`, the vocabulary's own pad —
   the tokenizer declares none, and the harness pads left, so the id
   is inert to greedy decoding under the attention mask but is pinned
   so that the two loader paths cannot differ on it); EOS 128001; and
   NO BOS on a plain render, which is this tokenizer's own default
   (the post-processor adds nothing) and the harness convention every
   prior family was scored under. Dial n: the plain render
   (recommended) vs a forced `<|begin_of_text|>` prefix; the preflight
   prints both renders' continuations on 40 items, descriptive, so
   the choice is visible before the tag.
3. **The predictors, loaded through their own seals.** x_A^(256) =
   2k's sealed 1b tier through `load_tier_2k` (record provenance, the
   gate-1 re-derivation against 2d's committed rows, tallies),
   `seal_failures_2k`, `exp2k-predictor-sealed` required to bind;
   x_A^(64/128/192) from the same rows (S1); x_A^(256) at 410m (S2).
   x_B = 2i's sealed OLMo-2 1B counts through `load_predictor_records_
   2i` + provenance + `_check_predictor_counts_2i`, `exp2i-predictor-
   sealed` required to bind.

   `PREDICTOR_SHA_2M` is `sha256("2m|" + <2k seal sha> + "|" + <2i seal
   sha>)`. The `"2m|"` prefix is what makes it differ from 2l's
   composite of the SAME two seals, so a 2l record cannot pass 2m's
   `predictor_sha` check and a 2m record cannot pass 2l's. Note that
   `seal_tag` alone does not separate them — both experiments stamp
   `exp2k-predictor-sealed+exp2i-predictor-sealed`; `predictor_sha`,
   `size` and `family` do.

   π = 2j's `wrong_target_propensity` on 2i's x_B rows (S5). No new
   sampled quantity anywhere in 2m.
4. **The endpoint stage.** Three thin loads on all 34 rungs, per-item
   bits and continuations stored (2c's greedy harness, `BATCH_SIZE_2M`
   = 16 a single pre-tag constant as in 2l, `DTYPE_2M` = fp16 likewise
   — dials l, m): the stage-1 endpoint `stage1-step-3440000` (the
   OUTCOME's endpoint: fixes R by rule, feeds the power record, is
   gate 1's referent), `stage3-step-4720000` (the last pretraining
   checkpoint before context extension — the `main` analogue, 2l S6,
   descriptive) and `HuggingFaceTB/SmolLM3-3B-Base` (the released
   base, descriptive).

   Every 2m record's `dtype` field is OVERRIDDEN to `DTYPE_2M` — 2i's
   `item_record_2i`, which 2m's two record wrappers call, hard-codes
   `"float16"` — and the analyzer pins it on every endpoint and sweep
   record. `BATCH_SIZE_2M` is carried by NO record: gate 1 cannot
   detect a batch or a precision change between the stages, because it
   re-derives the endpoint step through the sweep's own loader at
   whatever the constants currently say, so both sides move together.
   The tag-bound constants are what prevent a mid-campaign change; the
   fp32 fallback is a pre-tag change plus a re-tag.

   Committed and tagged `exp2m-endpoint-sealed` before any intermediate
   checkpoint loads. ≈ 3 × 40 min.

   The seal binds 104 files: 3 × 34 endpoint records + `rung_set_2m.json`
   + `power_2m.json`. The composite `endpoint_sha256` every sweep record
   stamps is taken over the same 104, and `endpoint_files` raises on the
   first missing one rather than forming a composite over a subset.

   The three endpoint whichs carry no checkpoint record, so the analyzer
   measures each which's coherence directly: all 34 of its records must
   carry the same non-empty tensor digest, commit and config source.
   Gate 1's `digest_endpoint`/`commit_endpoint` and
   `digest_sweep`/`commit_sweep` are likewise measured against the 34
   records on their own side, not merely against each other.
5. **The outcome is SmolLM3-3B's stage-1 grid** — dial c, recommended
   shape (the "dense head"), on the 40k-step lattice the branch offers:

       S = {40k · j : j = 1 … 10}                (every 40k, 40k … 400k)
         ∪ {600k + 200k · j : j = 0 … 14}        (every 200k, 600k … 3,400k)
         ∪ {3,440,000}                           (endpoint; gate 1)

   26 points, all present on the branch (verified 2026-09-03, metadata
   only), plus the seeded twin. y_i = number of grid points at which
   item i verifies (2g's count outcome; range 0..26); first-correct
   step printed beside it. The head puts 10 of 26 points in the first
   11.6 % of training (94 B … 944 B tokens); the count weights
   earliness, which is the intent, and the dense head is where a
   3 B model trained on 8 T tokens is expected to surface most of the
   battery. Alternatives: 2i's log-head shape ({40k, 80k, 160k, 320k}
   + every 200k + endpoint = 21 points, ≈ 14 h) or all 86 (≈ 57 h).
6. **Gate 1** = the endpoint reproduced through the sweep's checkpoint
   loader: per-item bits identical to the endpoint record on all 34
   rungs, continuations identical with the compared count attested and
   required to be 500/rung, tensor digest equal, RE-DERIVED by the
   analyzer from the two committed record sets. Runs first in the
   sweep; a diff halts with the tree the analyzer reads as
   INSUFFICIENT_DATA (both halt artifacts refuse — 2k F-1).
7. **The tree.** INSUFFICIENT_DATA → the joint reading of Tests A and
   B → SHARED / PYTHIA-ONLY / OLMO-ONLY / NEITHER. Every quantity of
   §5 printed in every world. Ruling 18's undefined branch retained (a
   test all of whose eligible rungs are degenerate is `fires = False`
   with "undefined" named inside) — unreachable for A on this data
   (x_A^(256) is non-degenerate on every strata rung: 2k), reachable
   for B only if x_B is constant inside every stratum of every rung,
   which 2i's tiers rule out on the nine.
8. **Pins.** `FROZEN_SHA256_2M` over every module named (2l's list +
   2l's own instrument blobs, now frozen bytes); `IMPORTED_SHA256_2M`
   over the resolved module table at entry and exit; a pre-campaign
   referent manifest (2l's list + 2l's verdict, seal, power, endpoint
   and sweep records — S8 reads 2l's, 2i's, 2g's and 2h's committed
   per-item outcomes — plus 2m's `checkpoints_2m.json`, the Hub
   inventory and `power_2m.py`), its sha a literal in the analyzer;
   the campaign's own artifacts (the endpoint records, the rung set,
   the power record) bound by `exp2m-endpoint-sealed` and cross-
   checked at analysis time exactly as 2l's were (record failures; the
   composite `endpoint_sha256` required on every sweep record; the
   rung set re-derived from the endpoint's own counts; gate 1 attested
   AND re-derived), so the preregistration tag is never re-cut after
   the campaign.

   The manifest is PRE-CAMPAIGN and deliberately includes 2l's OWN
   campaign artifacts (its 68 endpoint records, rung set, power record,
   gate 1, verdict and the whole 13B sweep tree), because S8 reads the
   13B outcome through 2l's frozen loaders: a post-close edit to a 2l
   record is refused at `check_referents` on entry, before the
   predictors and long before the secondaries. The only files S8 reads
   that are not manifest entries are `checkpoints_2g.json` and
   `checkpoints_2h.json`, each sha-pinned at load from a frozen module.

   Blob-bound tags: `exp2m-preregistered` binds the
   analyzer, the battery module, the endpoint stage and the sweep
   runner.

## 4. Rung set, strata and power

**R_3B** — the rungs whose stage-1 endpoint count clears 2d's bar
(one-sided exact binomial against 2d's model-free floor, max(majority
share, 1/n_options), 2d's α), fixed at the endpoint stage by rule. Not
known now. 13B cleared 18 of 34 at 5.0 T tokens; a 3 B model at 8.1 T
may land above or below that.

**Strata.** 2g's committed table (eleven rungs). The primary for both
tests runs over **R_PRIMARY = R_3B ∩ 2i/2k's nine** (add3_mid,
add_base8, antonym, antonym6, arith_next, odd6, sub3_mid, sub4_mid,
sub_base8) — 2l's slip (a) carried: x_A^(256) exists only on the nine.
The rest of the eleven that clears the bar is printed as
**R_ELEVEN_EXTRA** with the 64-draw x_A and x_B in 2g's strata; the
rest of R_3B as **R_EXTRA** with raw single-stratum D; neither is ever
in the verdict. Fewer than three rungs in R_PRIMARY → THIN declared in
the power record, the verdict still runs; a test that ends up READING
fewer than three rungs carries 2l F-4's disclosure on the reason and
the licence.

A rung can be INSIDE R_PRIMARY and outside both tests: 2d's endpoint
bar clears at k = 9 on `add3_mid` and `sub4_mid`, 15 on `sub3_mid`
and 19 on `arith_next` — all below the n_pos ≥ 20 analysis-time
eligibility floor. The power record declares over R_PRIMARY minus the
predictor-degenerate rungs, so whenever a test READS fewer rungs than
R_PRIMARY the verdict carries a disclosure naming the rungs it did
not read and stating whether the declaration covers a wider set than
the reading or the same set reached by a different route, decided
against the power record's own `rungs_simulated` list; the licence is
bounded to the rungs named as read.

`primary_is_the_nine` printed either way.

**Predictor degeneracy.** x_A^(256) has at least two live strata on
every strata rung (2k). x_B at ceiling (64/64) inside a stratum drops
that cell; a rung with no informative cell is dropped from Test B and
printed. **Outcome ceiling (new to this family):** an item that
verifies at every grid point has y = 26; a rung whose endpoint clears
near 100 % and whose items are mostly at ceiling from step 40,000
carries little order information, and 2g's statistic handles the ties
as it always has (informative pairs only). The ceiling fraction per
rung is printed in every world (S7), and the first-correct outcome is
the sensitivity that reads earliness where the count saturates. No
new rule is added for it — a rule invented for an outcome nobody has
seen would be a dial without a referent.

**Power**, written ONCE at the endpoint stage, before the projection,
per test, with 2i's machinery over the REAL predictors: n_pos bounded
below by the endpoint count, y from a latent mixing rank(x) at
calibrated strength inside the test's strata, every cell through the
verdict's own tree; bar P(fires | D = .15) ≥ .75, else DECLARED
UNDERPOWERED IN ADVANCE per test; P(fires | D = .10) printed (the bar
decides). Test A's predictor block SD printed as in 2l (dial h; 2k's
process note): per simulation the SD across x_A's four 64-draw blocks,
averaged over 200 simulations, and the same at rho = 0 as
`mean_block_sd_null`; Test B has one block and prints none. Shape
note verbatim (item-level alternative; nothing transfers to a class-
level effect).

## 5. Named secondaries (printed in every world; no α claim)

- **S1 — the ladder on a second sealed outcome.** T_A at k = 64, 128,
  192, 256 (2k's nested blocks) → 3B; the four 64-draw blocks' T's and
  their SD. 2l: no block cleared at 64, 256 cleared.
- **S2 — 410m at 256** → 3B (410m ≥ 1b on 7B and 13B; a fourth
  reading).
- **S3 — the increments both ways, and the paired difference.**
  x_B in strata of x_A^(256)'s median bucket (B-beyond-A: 2l's Test B
  form) and x_A^(256) in strata of x_B's median bucket (A-beyond-B:
  2l's cross-beyond-within); T_B − T_A with a bootstrap interval,
  under the density caveat.

  The interval is a PAIRED item bootstrap within each rung — items
  resampled with replacement and BOTH predictors read on the same
  resample — over the intersection of the two tests' eligible sets, and
  the full-data T is the plain mean of within-stratum Somers' D over
  those rungs. It is a bootstrap of one statistic on one tie structure,
  at two different predictor densities (256 vs 64 draws); the record
  carries `n_boot` beside `n_boot_requested` so a silently thinned
  bootstrap is visible.
- **S4 — the matched comparison** (2j/2k's block rule): x_B thinned to
  k_g = clip(round(256 · r̄_A / r̄_B), 1, 64) per rung against
  x_A^(256) on the sealed outcome — with both predictors cross-family
  this reads "which family's small model reads the third family's
  order better at equal draws", the corpus-overlap texture at matched
  density.
- **S5 — the answer prior as a sealed-outcome forecaster,** its second
  test: 2j's π on 2i's x_B rows against 3B's order with 2i's
  statistic. 2l read .1848; the retirement clause (π ≤ .05) stands
  as written there. Non-gating (dial g).
- **S6 — the referents.** The seeded twin's per-rung counts (expected
  ≈ 0; nonzero is a floor-guessing texture, printed); the stage-3
  endpoint and the released base vs the stage-1 endpoint per rung
  (what the later stages and context extension change).
- **S7 — textures.** Ever-vs-final verification per rung, transient
  clears on flat rungs, checkpoint-local collapses (2h's pathology),
  non-monotone trajectories, first-correct steps, the ceiling fraction
  per rung (§4), the reversal pair descriptive.
- **S8 — outcome-to-outcome order (new).** The committed per-item
  count outcomes of Pythia-2.8b (2g), Pythia-6.9b (2h), OLMo-2 7B (2i)
  and OLMo-2 13B (2l), each read as x against 3B's order with 2g's
  statistic in the same strata.

  S8 uses 2i's permutation machinery, so each row carries a T and a p;
  no α claim is made and its `test.fires` key is `fires_2i` applied
  mechanically at 2g's bar, not a firing rule for S8. Each row says so
  in the record (`no_alpha_claim`, and a note naming the fact that a
  failure inside S8 lands in `secondaries.failures`, never in
  `referents.failures`). The same holds of S5.

  Not a from-below forecast (those are
  large models with known outcomes); a descriptive of whether
  emergence ORDER itself is shared across three families at item
  grain, independent of any small-model read — the "structure latent
  in the distribution" reading taken directly. Its 13B row is the
  natural ceiling for what any predictor could transfer.
- **Sensitivities:** the first-correct outcome as y; the primary over
  R_CAP's nine when R_3B ∩ eleven ⊋ nine; Test B in 2i/2l's
  conditioned form beside the unconditioned one; the log-head grid
  subset (21 of the 26 points) as y, to show what the dense head
  bought.

  The subset sensitivity RE-COUNTS y over its own 21 points (so
  `max y = 21`, not 26) and is descriptive: the power record's
  `n_trained_steps = 26` describes the primary outcome only and makes
  no claim about the subset.

## 6. Licences, written in advance

- **SHARED:** the essay's cross-family sentence generalises — "smaller
  models of two families, given enough draws, forecast what a third
  family's training surfaces first" — with Prediction 2's output-
  channel form holding across families at item grain on two predictor
  families and two outcome families (still one battery); the "structure
  latent in the training distribution" reading gains its second cross-
  family leg. Carried verbatim: NOT disjoint text — the corpus question
  (an outcome trained without web crawl: Comma v0.1) is the named
  next; the mechanism question stays open.
- **PYTHIA-ONLY:** the transfer does not follow corpus overlap (the
  predictor sharing the least text with the outcome is the one that
  reaches it); OLMo-2 1B's 64-draw read is the suspect, S1/S4 the
  descriptive adjudication; the essay's sentence stands as 2l wrote it
  and gains "on a second outcome family"; the named next is the
  OLMo-2 1B predictor at 256 draws (a predictor-side experiment).
- **OLMO-ONLY:** the transfer follows the corpus; the shared-text
  caveat becomes the leading account; the essay's cross-family sentence
  is bounded to "between corpora that share DCLM-era web"; the corpus
  question is the named next, and the essay says so.
- **NEITHER:** the cross-family finding is bounded at OLMo-2 as the
  outcome family in the essay and `experiments.md`; the full SmolLM3
  record reported; the program's next step is Michael's call.
- Any world: S1–S8 in full; the twin, the stage-3 endpoint and the
  base, the flat and extra rungs reported; S5 and S8 stated as
  descriptive.

## 7. Run plan and model contact

Design (this doc + rulings) → build (`experiments/exp2m`: the SmolLM3
manifest from a committed Hub scan with the candidate rule, the two
loaders, the tokenizer pins, the seeded twin, the endpoint stage, the
sweep runner, the two-test analyzer with the four worlds and S1–S8,
power with the block-SD line, referents, fixtures, worlds for every
terminal, totality, mutation, read sweep, import scan) → adversarial
freeze → tag `exp2m-preregistered` → **preflight (dial j) on Michael's
word:** 2c's harness on `SmolLM3-3B-Base` for 20 items each of
`antonym` and `add3_mid`, continuations printed to the ledger and
stored nowhere the analyzer reads — a format, memory and PRECISION
check: logits scanned for NaN/Inf over the 40 prompts at fp16, the
collapse texture noted, the tokenizer's rendered ids printed for one
item under both renders (dial n); ONE stage-1 checkpoint staged through
the candidate-file loader end to end — **step 40,000** — downloaded
(6.15 GB), sha-verified against the manifest, hardlinked into a clean
directory with the entry's own `config.json`, loaded, scored on the
same 40 items and **freed**. The preflight writes nothing under
`experiments/exp2m/results/` and asserts so afterwards. The preflight
applies `check_frozen_2m` but not `require_prereg_2m`; it stores
nothing the analyzer reads, and design §7 already places it after the
tag. `BATCH_SIZE_2M`
(= 16) and `DTYPE_2M` (= fp16) are single pre-tag constants in
`battery_2m.py`, threaded explicitly into every runner (2l's
construction; no record carries them, the tag is what prevents a mid-
campaign change). If the preflight shows fp16 overflow, `DTYPE_2M`
changes once to fp32 (12.3 GB; ≈ 2× the time) before the tag, and the
tag is re-cut (2i's precedent, disclosed in PROVENANCE). →
**stage 1 (endpoint)**: the stage-1 endpoint, the stage-3 endpoint and
the base through the thin loader on all 34 rungs (≈ 2 h, 3 × 6.15 GB),
R fixed by rule, power printed once (with the block-SD line),
committed, tagged `exp2m-endpoint-sealed` → projection sealed (by rung
type, named disconfirmers bracketing the null for EACH test WITH
TOLERANCES — 2l's process notes 1 and 3 applied — the verdict call
placed against the block SD) → **stage 2 (sweep)**: gate 1 first,
then the twin, then the 25 remaining grid points ascending, ≈ 40 min
each at fp16 (7B's measured 82 min scaled by parameters, plus
download), ≈ 17.5 h, ≈ 160 GB streamed one checkpoint at a time and
deleted, the watcher committing every record after its size stops
changing, processes detached → analyzer once, detached → `exp2m-
closed`. One pre-committed change.

Compute: the Mac for every stage (the stack behind every byte-
identical reproduction in this line, most recently 2l's at 13B; gate 1
is byte identity between 2m's own two loader paths). Memory: fp16 3B ≈ 6.2 GB + activations at batch 16
— the mlx text-server stays up unless the preflight shows pressure
(dial o; 2l's kernel panics were 13B under memory starvation). Disk:
peak ≈ 6.2 GB (one checkpoint) + the thin loader's three revisions in
the ordinary HF cache (≈ 18.5 GB); 220 GB free at design time with
2l's 13B revisions (≈ 110 GB) still cached and clearable by the
operator now that 2l is closed and propagated.

## 8. Alternatives considered — the shortlist (Hub metadata, 2026-09-03)

Four genuine third families carry intermediate checkpoints as
revisions, fit the Mac and load natively under transformers 5.13:

- **SmolLM3-3B** (chosen): 3.08 B; 86 stage-1 points every 94 B
  tokens; 6.15 GB per revision; ≈ 40 min per point. The most distant
  architecture from both predictors, the cheapest sweep, and "from
  below" holds against both 1B predictors in parameters AND tokens
  (Comma and Amber saw fewer tokens than OLMo-2 1B's ≈ 4 T); shares
  DCLM-class web with OLMo-2 (disclosed, §2).
- **Comma v0.1-1T** (common-pile): 7.0 B Llama on 1 T tokens of openly
  licensed text — no web crawl at all; 46 stage-1 points every 21 B
  tokens + 9 cool-down; ≈ 80 min per point. The sharpest corpus
  control the Hub offers, at ≈ 2× the sweep cost and a weaker expected
  rung set (Llama-2-7B tier). §6's named next under SHARED and
  OLMO-ONLY.
- **Amber** (LLM360): 6.7 B Llama on 1.26 T RedPajama; 360 points every
  3.5 B tokens; `.bin` weights. The oldest and weakest model; the dense
  grid is its only edge.
- **Apertus-8B** (swiss-ai): 8.05 B, xIELU activation, 15 T
  multilingual tokens, ≈ 44 main-run points every 210 B; 16 GB. The
  strongest model, with untested MPS coverage for its activation and
  the heaviest sweep (≈ 30 h).

Excluded: OLMo-1 and OLMo-3 (same lineage as an existing outcome
family), SmolLM2-1.7B and TinyLlama-1.1B (dominated by SmolLM3 at the
same architecture class), BLOOM-intermediate (8 tags), CrystalCoder
(remote code), K2 (65 B), MAP-Neo and Marin (no revision grid).

Design alternatives not taken: **Test B conditioned on A** as in 2i/2l
(asymmetric between two symmetric reads; printed as a sensitivity
instead); **the full 86-point grid** (≈ 57 h; the count at 26 already
resolves 0..26, and a finer grid is the density-of-grid successor if
the head saturates); **a fresh SmolLM3-3B-class predictor** (there is
no smaller SmolLM3; SmolLM2-360M would be a fourth family's small
model, predictor-side contact for a question this design does not ask).

## 9. What 2m does not claim

Not "Prediction 2 supported across families" beyond item grain, one
battery, two predictor families and two outcome families. Not a
statement about disjoint text (the overlap is disclosed and used).
Not a mechanism result (S5, S8 descriptive). Not a statement about
stages 2–3, the context extension or the released base beyond S6's
descriptives. Not a statement about the across-task ranking.

## 10. Dials — RULED by Michael 2026-09-03: a (SmolLM3-3B, from the shortlist); b–p "as recommended" — every dial as recommended

- **a. Outcome model:** SmolLM3-3B stage 1 (`HuggingFaceTB/SmolLM3-
  3B-checkpoints`) — **RULED**; the alternatives are §8's.
- **b. Tests and worlds:** A = x_A^(256) and B = x_B^(64) each
  UNCONDITIONED on its own bar; worlds SHARED / PYTHIA-ONLY /
  OLMO-ONLY / NEITHER; the increments both ways and the paired
  difference printed (S3), **recommended**; the alternative is 2i/2l's
  conditioned Test B with the LINEAGE/BOTH names, which no longer
  describe what B is.
- **c. Grid:** the dense head — every 40k to 400k, every 200k to
  3,400k, the endpoint: 26 points, ≈ 17.5 h, **recommended**; vs the
  log-head shape (21 points, ≈ 14 h) vs all 86 (≈ 57 h). The log-head
  subset is printed as a sensitivity under the recommendation, so the
  dense head costs ≈ 3.5 h and nothing in comparability.
- **d. Descriptive endpoints:** the stage-1 endpoint (outcome) + the
  stage-3 endpoint `stage3-step-4720000` (the `main` analogue) + the
  released base, **recommended**; vs the stage-1 endpoint + base only.
- **e. Rung set:** R_3B by 2d's floor rule at the stage-1 endpoint;
  R_PRIMARY = R_3B ∩ the nine, the eleven's remainder and R_EXTRA
  printed, **recommended**.
- **f. Projection:** sealed after the endpoint stage and before the
  sweep; written BY RUNG TYPE with 2l's sign split as the prior, named
  disconfirmers bracketing the null for each test with stated
  tolerances (a disconfirmer that fires by .002 means less than it
  says — 2l's note 1), the verdict call placed against the printed
  block SD, **recommended**.
- **g. S5 (the answer prior) non-gating,** **recommended**; the
  alternative is a third preregistered test at the same bar (a
  mechanism claim on a second sealed outcome — strong if it fires, but
  it widens the α-uncalibrated union of worlds).
- **h. Power record prints Test A's block SD,** **recommended**.
- **i. Init referent:** a seeded `from_config` twin of the stage-1
  config (no step 0 exists on the branch), 2i's construction,
  descriptive, **recommended**; vs no init referent (step 40,000 is in
  the grid either way).
- **j. Preflight on his word:** 20 items × 2 rungs on the released base
  + step 40,000 staged through the candidate-file loader; the fp16
  precision check; both tokenizer renders printed; nothing stored,
  **recommended**.
- **k. Bars .10 / .01 unchanged,** **recommended**.
- **l. Precision:** `DTYPE_2M` = fp16 (the precision every 7B/13B
  outcome was scored at), with fp32 as the pre-tag fallback if the
  preflight shows overflow (a re-tag, disclosed), **recommended**; vs
  fp32 throughout (no overflow risk at 12.3 GB, ≈ 2× the sweep).
- **m. Batch:** `BATCH_SIZE_2M` = 16 (2i/2l's constant; nothing reads
  the harness default), **recommended**; vs 32 (faster; a different
  padding geometry from every prior outcome, for ≈ 5 h saved).
- **n. Tokenizer render:** the plain render (no BOS — the tokenizer's
  own default and every prior family's convention), pad
  `<|finetune_right_pad_id|>` 128004, left padding, **recommended**;
  vs a forced `<|begin_of_text|>` prefix. The preflight prints both.
- **o. The mlx text-server** stays up unless the preflight shows
  memory pressure, **recommended**; vs booting it out for the campaign
  as in 2l.
- **p. Build + freeze in one session** by SDD, the import pin from
  commit one; licences as §6, **recommended**.

## 11. Process

Design → rulings → build → freeze → tag → preflight on his word →
endpoint stage → seal tag → projection → sweep (detached, watcher, one
poller) → analyzer once, detached → `exp2m-closed` → close-out
propagation (essay under §6, `experiments.md`, the graft with the
three tags, Zenodo v1.16, paper inventory).
