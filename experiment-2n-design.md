# Experiment 2n — Design Doc: The Corpus Question — Does the Cross-Family Forecast Follow the Training Corpus, on an Outcome With No DCLM-Class Web?

**Status: session 1 (design) written 2026-09-06, at Exp 2m's
close-out, on Michael's word ("Design the corpus question (Comma v0.1)
as 2n"). The outcome family is the one 2m's §6 SHARED licence named:
**Comma v0.1-1T, stage 1** (common-pile; the corpus is the Common Pile
v0.1 — openly licensed text, no DCLM- or FineWeb-class web crawl). §10
DIALS a–r RULED by Michael 2026-09-06 ("Dials as recommended — build
and freeze"): every dial as recommended — a Comma v0.1-1T; b Tests A/B
unconditioned, four worlds, increments + paired difference; c the
uniform 24-point grid with the every-40k control; d three descriptive
whichs; e R_Comma by the floor rule, R_PRIMARY = R_Comma ∩ the nine;
f the projection by rung type with tolerances both directions and the
corpus/predictor accounts as claims; g the corpus annotation C as a
CI rule; h the block SD + the null SD of Δ; i the seeded twin; j the
preflight on his word; k bars unchanged; l fp16 with the pre-tag fp32
fallback; m batch 16; n `render: "bos"`; o `eos_stop_id` 3 set in both
loaders; p the mlx servers stay up unless the preflight shows
pressure; q S8 extended + S8c + S9; r SDD build + freeze in one
session. No model contact of any kind has
occurred; the Hub was read for metadata only, and the tokenizer files
(4.3 MB, no weight) were loaded once through the Mac stack's
transformers into a scratchpad cache to measure the plain render (§2).
Model contact, when sanctioned: Comma v0.1-1T ONLY, on the OUTCOME side
— its stage-1 endpoint, its last cool-down checkpoint and the released
average at the endpoint stage, then its stage-1 grid and a seeded twin
in the sweep. Every predictor is already committed and tagged; nothing
is sampled.
RATIFIED by Michael 2026-09-07 ('Ratified — apply the slips and tag'):
freeze findings F-1..F-4 closed additively (68a0fd42); slips (a)–(n)
applied — (c′) and (n) from the final whole-branch review; the tag
`exp2n-preregistered` CUT 2026-09-07 at 013d67ba (annotated object
5c139c0f), pushed (blob-bound: analyze_2n.py a860a4e7…, battery_2n.py e85165bd…,
run/endpoint_2n.py 62d62959…, run/sweep_2n.py 4d077ae8…; verified
through `require_prereg_2n` against real git). FROZEN. Model contact
from here only on Michael's word (§7: the preflight first).**

2m closed SHARED: both committed predictors — Pythia-1b's 256-draw
count (2k) and OLMo-2 1B's 64-draw count (2i) — forecast the order in
which SmolLM3-3B's training makes 2c's items emittable, each above its
projection. Its retrospective left two accounts standing side by side.
The arithmetic rungs transfer across every family at every density
(task-shaped); the option rungs split in sign between the two
predictors on both sealed cross-family outcomes, and the matched-
density margin of the DCLM-trained predictor was the same on a third
family as on its own — which the retrospective read as "corpus plus
density", with S8 showing both OLMo outcomes far closer to SmolLM3's
order than the Pythia pair. Every sealed outcome so far (OLMo-2 7B,
OLMo-2 13B, SmolLM3-3B) was trained on DCLM-class web. 2n is the
experiment the SHARED licence named: the same two predictors read
against an outcome whose corpus contains none of it.

## 1. The question

**Does Pythia-1b's committed 256-draw count (Experiment 2k, tag
`exp2k-predictor-sealed`) forecast the order in which Comma v0.1-1T's
stage-1 training — an outcome nobody has queried — makes 2c's items
emittable, within 2g's difficulty strata; and does OLMo-2 1B's
committed 64-draw count (Experiment 2i, tag `exp2i-predictor-sealed`)
forecast that same order?**

Both predictors are cross-family with respect to the outcome, as in 2m,
and each is read UNCONDITIONED on its own bar:

- **Test A (Pythia → Comma, 256 draws).** Predictor x_A = Pythia-1b's
  256-draw count (2k). Fires iff the stratified concordance clears 2g's
  bar (p < .01, T ≥ .10).
- **Test B (OLMo-2 → Comma, 64 draws).** Predictor x_B = OLMo-2 1B's
  64-draw count (2i). Fires on the same rule, in the same strata, on
  the same outcome.

Worlds (after INSUFFICIENT_DATA), 2m's four, so that the fourth
outcome family reads on the same tree as the third:

- **SHARED** — both fire: the ordering is read by small models of two
  families on an outcome that shares no web crawl with either
  predictor's corpus and no architecture, tokenizer or recipe with
  either. The cross-family sentence generalises to a fourth family and
  past the DCLM-class corpora.
- **PYTHIA-ONLY** — A fires, B does not: the predictor whose corpus
  shares the outcome's dominant source kinds (the Pile and the Common
  Pile: papers, forums, code, patents, law, books — §2) reaches the
  order, and the DCLM-trained one does not. The corpus account of 2m's
  B-iii becomes the leading account; density is its named competitor
  (x_B has 64 draws), adjudicated by S1 and S4.
- **OLMO-ONLY** — B fires, A does not: the denser, stronger predictor
  reaches the order and the Pile-trained one does not, on the outcome
  whose corpus is closest to the Pile's. The corpus account is
  disconfirmed in the direction it predicted; predictor quality is the
  leading account.
- **NEITHER** — the finding does not reach this family at this
  resolution (or the battery does not transfer to a 7B model trained
  on 1 T tokens of curated text).

What separates 2n from 2m is not the tree but what the two accounts
predict on it, and a preregistered reading that decides between them
where the worlds cannot. The **corpus account** (2m's B-iii mechanism:
x_B's margin came from DCLM-class text shared with the outcome) and the
**predictor account** (2m's retrospective note 1: the counts carry
task-shaped structure, and x_B is simply the denser, better-trained
read) agree on SHARED but disagree on the matched-density margin. The
corpus account says the margin follows the corpus and should vanish or
reverse on Comma; the predictor account says it should be ≈ +.06 again,
as on 7B (+.054), 13B (+.069) and SmolLM3 (+.066). So 2n carries a
**corpus annotation C** beside the worlds (dial g; the program's
precedent is 3e's specificity arm): on Δ = T(x_B thinned to x_A's
per-rung rate) − T(x_A^(256)) — 2k's block rule, S4's quantity — with
a paired item bootstrap CI95 (S3's machinery),

- **B-LEADS** — CI95 lower bound > 0;
- **A-LEADS** — CI95 upper bound < 0;
- **NO-LEAD** — otherwise;

C is printed in EVERY world and its modifier rides on the licence in
every world: §6's cells are written under SHARED because that is where
the two accounts agree on the world and disagree on C, but the
annotation is defined independently of the tests (dial g) and the
licence carries its sentence whichever world fires.

and printed beside it whether the CI95 covers 2m's +.0659
(`covers_3b_increment`). The corpus account predicts A-LEADS or
NO-LEAD with the interval excluding +.066; the predictor account
predicts B-LEADS with the interval covering it. C is a CI rule, not an
α claim; the union of the four worlds is not α-calibrated (each test at
α .01; 3d's calibration lesson), and C adds no test to that union. The
projection (§7) states which cell each account predicts, with the
attenuation prior written as a claim carrying its own disconfirmer
(2m's process note 2).

## 2. What is known and what is sealed (disclosure)

**Known:** everything through 2m's close-out — six sealed forecasts
(2g's sampler competitor on Pythia-2.8b .17, 2h on 6.9b .20, 2i on
OLMo-2 7B .22, 2l on OLMo-2 13B .13/.18, 2m on SmolLM3-3B .17/.25),
2j's mechanism reading, 2k's DENSITY result, and 2m's full texture on
SmolLM3: Test A .1696 (per rung sub_base8 .453, add_base8 .439,
arith_next .220, antonym6 .170, sub3_mid .152, odd6 .133, add3_mid
.019, sub4_mid −.020, antonym −.041), Test B .2514 (add_base8 .750,
arith_next .433, sub_base8 .407, antonym6 .222, odd6 .180, antonym
.168), the 64-draw blocks .0998–.1106 (three of four clear), the ladder
.1095 → .1400 → .1612 → .1696, 410m .1693, B-beyond-A .2306 / A-beyond-B
.1226, the paired difference +.0818 [.057, .106], the matched-density
increment +.0659, S5's answer prior .2417, S8 (7B .4615, 13B .3958,
2.8b .2472, 6.9b .2286), and the antonym sign ledger across outcomes —
A: 7B +.024 (2k), 13B −.066, 3B −.041; B: 7B +.217 (2i, within-
lineage), 13B +.256, 3B +.168. The predictors x_A^(64/128/192/256)
(both sizes), x_B^(64) and 2j's π are historically prior and tag-bound.

**The Hub inventory of Comma v0.1-1T was read on 2026-09-06 (metadata
only, no weight touched):** `common-pile/comma-v0.1-1t` (commit
`5af409118da3cbea94684c622c66ab8c2ea7f4fe` on `main`) carries 55
checkpoint branches besides `main` and a `pr/1` ref: 46 stage-1
revisions `stage1-step010000-tokens21B` … `stage1-step460000-tokens965B`
at 10,000-step spacing (21 B tokens per 10,000 steps: lingua batch 2 ×
seq 4,096 × grad-acc 4 × 64 GPUs = 2,097,152 tokens per step; the
model card: stage 1 = 965 B tokens under a cosine schedule) and 9
stage-2 "cool-down" revisions `stage2-step002000-tokens969B` …
`stage2-step018000-tokens1002B` (35 B tokens from upweighted high-
quality sources; the released `main` is the AVERAGE of ten cool-down
checkpoints, nine of which are published). Every revision holds three
bf16 safetensors shards (14.01 GB in total) with LFS sha256s in the
Hub metadata plus `model.safetensors.index.json`; the 56 first-shard
signatures are all distinct (no stale copies — the structural zero
2g's rule guards). **No step-0 checkpoint exists on the branch** (the
first is step 10,000), so the init referent is 2i/2m's seeded
`from_config` twin. A companion repo `common-pile/comma-v0.1-checkpoints`
holds the raw lingua `model.pth` files and the training `config.yaml`
(read: seed 777, cosine schedule, warm-up 2,000, `add_bos: true`,
`add_eos: true`, a tiktoken tokenizer). The 2T model
(`common-pile/comma-v0.1-2t`, two epochs of the same data) publishes NO
intermediate checkpoints and is not an outcome candidate.

The config (identical on every branch; `main`'s differs only in the
`transformers_version` string): `LlamaForCausalLM`, 32 layers, hidden
4,096, 32 heads / 32 KV heads (no GQA), intermediate 11,008, rope θ
10⁵, `max_position_embeddings` 16,384 (trained at 4,096), `vocab_size`
64,256, `bos_token_id` 1, `eos_token_id` 2, bf16. transformers 5.13.0
(the Mac stack) loads the class natively — no remote code.

**The tokenizer, and a fact that bites (dial n).** Comma's tokenizer is
its OWN 64k byte-level BPE (64,000 entries + 4 specials; the Llama-3
pre-tokenizer regex over a fresh vocabulary — NOT Llama-3's 128k
vocabulary despite the Llama-3 architecture), identical on every
revision (`tokenizer.json`, `tokenizer_config.json` and the index file
hash equal across `main`, the stage-1 and the stage-2 branches). Its
specials: `<pad>` 0, `<unk>` 1, `<|begin_of_text|>` 2, `<|end_of_text|>`
3 — so this is the first outcome family whose tokenizer DECLARES a pad
token, and `config.json`'s `bos_token_id` 1 / `eos_token_id` 2 are
LlamaConfig's defaults, not the tokenizer's ids (config's "eos" 2 is
the tokenizer's BOS). `tokenizer_config.json` says `add_bos_token:
true`; `tokenizer.json`'s post-processor is `ByteLevel` alone (no
template). **Measured 2026-09-06 through transformers 5.13.0
(`TokenizersBackend`), tokenizer files only, scratchpad cache, nothing
in the HF cache:** the plain render adds NO special id (`"Q:"` →
`[52, 29]`; `add_bos_token` reads `False` — the v5 backend does not
honour the config flag for the generic class); left padding pads with
0; ids in the padded vocabulary region (≥ 64,004) decode to the empty
string; id 3 decodes away under `skip_special_tokens`. **But the model
was trained with a BOS on every sequence** (lingua `add_bos: true`).
So for the first time the two conventions this program has scored
under diverge: "the tokenizer's default render" (no BOS here) and "the
model's training-time render" (BOS). Every prior family satisfied
both at once — Pythia, OLMo-2 and SmolLM3 all train without a
prepended BOS and their tokenizers add none. Dial n rules the render
on this evidence before the tag; the preflight prints both on 40
items; §3.2 pins whichever is ruled.

**The harness's stop rule, and a second fact (dial o).** 2c's frozen
`HFRunner.generate` passes `do_sample=False` and `pad_token_id` and
NOTHING else to `generate`, so the stop id comes from the loaded
model's generation config. Comma's `generation_config.json` on `main`
is `_from_model_config: true` (bos 1, eos 2); on every checkpoint
branch it additionally carries `do_sample: true, temperature 0.6,
top_p 0.9` (inert under the harness's explicit `do_sample=False`;
disclosed). Either way the stop id is 2 — the tokenizer's BOS — and
the tokenizer's real EOS (3) never stops generation: an emitted
`<|end_of_text|>` would decode away and the continuation would run on
to `max_new_tokens`, with 2c's `number` regex reading the first digit
run and the `word` path the first word of whatever followed. Every
prior outcome's config eos equalled its tokenizer's eos (Pythia 0,
OLMo-2 100257, SmolLM3 128001), so their continuations stopped at the
real EOS. Dial o: 2n's two loaders set the loaded model's
`generation_config.eos_token_id` to 3 and assert it, restoring the
semantics every prior family was scored under; both loader paths do
it, gate 1's continuation identity checks that they agree.

**The corpus, at the source level — the asymmetry 2m used, inverted.**
Comma's main stage (its published mixing table, effective tokens
1,034 B): peS2o 25.1 %, StackExchange 13.8 %, Stack-v2-edu code 13.1 %,
Wikimedia 9.2 %, **CCCC 8.8 % — Common Crawl pages carrying a Creative
Commons licence, the corpus's ONLY crawl-derived text**, GitHub Archive
6.4 %, USPTO 3.8 %, PubMed 3.5 %, arXiv 3.5 %, Caselaw Access Project
1.9 %, DOAB 1.8 %, wikiteam 1.7 %, UK Hansard 1.4 %, pre-1929 books
1.2 %, Ubuntu IRC 1.1 %, and a tail (regulations, Gutenberg, YouTube
transcripts, Library of Congress, …); the cool-down stage (39.5 B
effective) upweights the same curated sources and thins CCCC to 0.3×.
"No web crawl" in 2m's §6 and §8 was an overstatement, corrected here:
**no DCLM-, FineWeb- or Pile-CC-class general crawl; ≈ 9 % CC-licensed
crawl pages.** The Pile (Pythia's corpus, ≈ 300 B tokens seen): Pile-CC
18 % + OpenWebText2 10 % general crawl, and otherwise PubMed Central
14 %, Books3 12 %, arXiv 9 %, GitHub 8 %, FreeLaw 6 %, StackExchange
5 %, USPTO 4 %, PubMed abstracts 3 %, Gutenberg 2 %, Wikipedia 1.5 %,
Ubuntu IRC, YouTube subtitles, HackerNews, EuroParl, … — **nine source
KINDS in common with Comma** (academic papers, StackExchange, GitHub
code, patents, case law, Gutenberg, Wikipedia, Ubuntu IRC, YouTube
transcripts), together ≈ 60–65 % of Comma's main-stage tokens and ≈
50 % of the Pile's. OLMo-2's stage 1 (OLMo-Mix-1124, 3.9 T; OLMo-2 1B
saw ≈ 4 T) is DCLM-baseline to ≈ 95 %, its curated minority (peS2o,
arXiv, Wikipedia, StarCoder, math) overlapping Comma's MAJORITY kinds
at ≈ 5 % of its own tokens. SmolLM3's stage 1 was DCLM / FineWeb-Edu
dominated. So: on SmolLM3 the DCLM-trained predictor shared the
outcome's dominant source class and the Pile-trained one shared only
curated minorities; **on Comma the Pile-trained predictor shares the
outcome's dominant source kinds and the DCLM-trained one shares only
its curated minority.** The corpus account, if it is what 2m's texture
was, predicts the roles to swap; the predictor account predicts them
not to. Source-level overlap is the only overlap this program can
state (no document-level intersection is computed); it is disclosed
and used, not claimed to be small.

**"From below", disclosed.** In parameters both predictors are from
below (1 B vs 7 B). In tokens only x_A is: Pythia-1b saw ≈ 300 B, Comma
1 T; OLMo-2 1B saw ≈ 4 T, four times the outcome's budget. The sealed-
forecast logic does not need "below" — the predictor is committed
before the outcome exists — but the essay's "smaller model" phrase
holds for Test B in parameters only, and §6 carries that.

**Not known to anyone in this program:** any output of Comma v0.1-1T on
any item, at any checkpoint. The outcome is sealed in 2l/2m's sense:
the predictors were committed (2i 2026-08-26, 2k 2026-08-30) before
this family was named as an outcome, and the design is 2m's with the
outcome swapped and the corpus annotation added.

**What 2m's texture makes foreseeable, stated now:** the per-rung
readings on SmolLM3 are the projection's raw material and the
projection is written by rung TYPE (arithmetic: add3_mid, sub3_mid,
sub4_mid, add_base8, sub_base8, arith_next; option: antonym, antonym6,
odd6) with the sign split as the type-level prior — and this time with
the corpus account's swap and the predictor account's constancy each
written as a claim with its own disconfirmer, tolerances in BOTH
directions. Structural facts about this outcome, foreseeable and
disclosed: (i) a 7 B model at 1 T tokens is a Llama-1-tier model (the
card: MMLU 42.4, ARC-C 52.8); its endpoint rung set may be smaller than
SmolLM3's 14 and the mid-digit rungs (add3_mid, sub3_mid, sub4_mid —
the rungs Pythia never cleared and SmolLM3 cleared late) are the ones
at risk, so R_PRIMARY may be thinner than the nine (§4's THIN guard and
2l F-4's disclosure carry); (ii) the first available checkpoint sits
at 21 B tokens (2.2 % of stage 1) — finer than SmolLM3's 94 B head,
coarser than 13B's 8 B — and on a 1 T run surfacing is expected to be
spread over the whole grid rather than concentrated in the head, which
is why dial c recommends a uniform grid; items at the count ceiling
from step 10,000 are expected to be few (the ceiling fraction is
printed per rung, S7, under the analyzer's definition — items correct
at EVERY grid point — which the projection quotes, 2m's process note
4); (iii) the cool-down stage changes the data mix, so the outcome
stops at the stage-1 endpoint and the cool-down endpoint and the
averaged release are descriptive (S6), as SmolLM3's stages 2–3 were.

**Sealed in order (§7):** the instrument (`exp2n-preregistered`, blob-
bound) before any Comma weight loads; the endpoint stage (`exp2n-
endpoint-sealed`: the endpoint records, the rung set, the power record)
before the sweep; the projection before gate 1. There is no predictor
stage.

**Pre-tag disclosure rule** (checklist item 27): any execution of 2n's
analyzer on the real tree before the tag is logged here before the tag
is cut, with what it printed. At the time of writing the analyzer does
not exist; on the real pre-campaign tree every execution must land
INSUFFICIENT_DATA (no Comma records) and print no T. The design
session's own contacts, logged: Hub API reads (`/api/models/…`,
`/refs`, `/revision/<branch>?blobs=true` for all 56 revisions), file
reads through `/resolve/` of `README.md`, `config.json`,
`generation_config.json`, `special_tokens_map.json`,
`tokenizer_config.json`, `tokenizer.json` and
`model.safetensors.index.json` at five revisions, the checkpoints
repo's `config.yaml`, the training-dataset card; and ONE
`AutoTokenizer.from_pretrained("common-pile/comma-v0.1-1t")` under the
Mac stack with `HF_HUB_CACHE` pointed at the session scratchpad (4.3 MB
of tokenizer files; the real HF cache holds no Comma entry; no weight,
no forward pass). Nothing was written under `experiments/`.

Logged (build Task 5, 2026-09-06, before the tag). Every execution of
`analyze_2n.run()` on the REAL pre-campaign tree landed
INSUFFICIENT_DATA and printed no T — no Comma endpoint, sweep, rung-set
or power record exists, so the run refuses at the endpoint stage after
executing every predictor-side loader:

1. `experiments/exp2n/tests/import_scan_2n.py`, run once, to pin
   `IMPORTED_SHA256_2N`: `INSUFFICIENT_DATA`, 11 referent/loader
   failures (the missing prereg tag plus the absent endpoint/rung-set/
   power/sweep records), no T, nothing written; residual surface 4
   modules (both `__init__.py`, `run/preflight_2n.py`,
   `verify_referents_2n.py`).
2. `experiments/exp2n/tests/read_sweep_2n.py`, run once:
   `INSUFFICIENT_DATA`, 10 referent/loader failures (the prereg tag
   binds through the sweep's own stand-in, so only the absent campaign
   artifacts remain), no T, `write=False`, 0 writes observed, 6,179
   distinct paths read, bucket (e) unpinned = 0.
3. Task 3's real-tree analyzer tests and Task 5's world/totality
   modules, which run `analyze_2n.run()` on SYNTHETIC roots and, in
   `test_run_on_empty_tree_is_insufficient_never_raises`, on an empty
   one: INSUFFICIENT_DATA in every case, no T on the real tree.

The cold battery's item 10 inspects the real `EXP2N` tree directly and
does not call `run()`; it printed "endpoint/rung set: absent —
pre-campaign", "power: absent — pre-campaign", "sweep: absent —
pre-campaign".

Logged (the adversarial freeze, 2026-09-07, before the tag). The freeze
ran `analyze_2n.run()` on the REAL pre-campaign tree twice through its
two cold tools; both landed INSUFFICIENT_DATA, printed no T and wrote
nothing. Its own findings were demonstrated on SYNTHETIC roots
(temporary directories) and on hand inputs, never on `EXP2N`:

4. `experiments/exp2n/tests/import_scan_2n.py`, run once, to re-pin
   `IMPORTED_SHA256_2N` after finding F-1 added assertions to
   `verify_referents_2n.py`: `INSUFFICIENT_DATA`, 11 referent/loader
   failures (the missing prereg tag plus the absent endpoint/rung-set/
   power/sweep records), no T, nothing written; residual surface
   unchanged at 4 modules, one sha moved
   (`verify_referents_2n.py` → `e80653b5…`).
5. `experiments/exp2n/tests/read_sweep_2n.py`, run once after that
   re-pin: `INSUFFICIENT_DATA`, 10 referent/loader failures, no T,
   `write=False`, 0 writes observed, 6,179 distinct paths read (8,553
   open/read calls), bucket (e) unpinned = 0, bucket (f)
   seal-bound-and-absent = 0.
6. The freeze's own fast/world/totality re-runs, which execute
   `analyze_2n.run()` on synthetic roots and, in
   `test_run_on_empty_tree_is_insufficient_never_raises`, on an empty
   one, plus the real-tree forced-exception tests already covered by
   entry 3: INSUFFICIENT_DATA in every case, no T on the real tree.

## 3. Instrument — 2m's, with the outcome model swapped, the render and stop id pinned, and the corpus annotation added

Everything not named here is `experiments/exp2m` / `exp2l` / `exp2k` /
`exp2i` machinery imported frozen: 2c's harness, 2g's strata and
statistics (within-stratum Somers' D, mean over rungs, permutation
within rung × stratum, 10,000, seed 0; bootstrap CI per rung),
eligibility n_pos ≥ 20, the count outcome with first-correct printed,
the referent discipline, the tree-totality closure, gate-1 coverage
attestation + re-derivation, blob-bound tags, the import-surface pin
from commit one (2j F-1), `pins_active` (2k D-1), the candidate-file
loader with the per-entry `config.json` write (2i stop #1), the THIN
guard keyed to |R_PRIMARY| (2l F-4), the halt-marker rule (2k F-1), the
F-1 SAME/WIDER disclosure decided against the power record's own
`rungs_simulated` (2m R-1), 2m's `s3_paired_difference_2m`,
`s4_matched_2m` and `s8_outcome_order_2m`. The deltas:

1. **The outcome model.** `common-pile/comma-v0.1-1t`, stage 1: 7.0 B
   parameters (the config works out to 6.48 B in the blocks + 0.53 B
   in the untied embeddings), three safetensors shards (14.01 GB bf16
   per revision, fp16 at load ≈ 14 GB on the Mac's 48 GB), per-revision commit sha and per-file LFS sha256 in a
   committed manifest `checkpoints_2n.json` (2g's candidate rule,
   duplicate-signature refusal; the Hub inventory committed as
   `hub_inventory_comma.json`); the index file pinned by the revision
   commit alone (2l's disclosure, unchanged). No step-0 checkpoint
   exists, so the init referent is the seeded `from_config` twin of
   the stage-1 config (2i/2m's construction) — descriptive, never in
   an outcome, scored once in the sweep, disclosed as a stand-in for an
   initialisation this program cannot download. The twin's config AND
   tokenizer are taken at the ENDPOINT's commit (`config_commit`); the
   analyzer measures `config_source` against
   `f"{REPO_COMMA}@{config_commit}"`. The checkpoint record attests a
   sha for every candidate file it stages; the analyzer requires that
   coverage plus the record's revision, commit and tensor digest (the
   last against the digest every one of the step's 34 item records
   carries).
2. **A fourth family's tokenizer, pinned.** 2m's `check_tokenizer`
   pattern with Comma's facts: left padding; `PAD_TOKEN_ID_2N = 0`
   (`<pad>`, the tokenizer's OWN declared pad — the loader sets
   nothing; the check refuses if the loaded tokenizer's pad is not 0);
   `EOS_TOKEN_ID_2N = 3`; `BOS_TOKEN_ID_2N = 2`; the vocabulary length
   64,000 + 4 against the config's padded 64,256, both pinned. **The
   render (dial n, recommended: BOS prepended).** The runner renders
   each prompt as `BOS_TOKEN_2N + prompt` — the string
   `<|begin_of_text|>`, which the tokenizer resolves to the single
   added-token id 2 — and `check_tokenizer_2n` asserts BOTH facts on
   every load: that the plain render of `"Q:"` begins with a non-
   special id (the stack adds nothing on its own, so the prefix is the
   only BOS), and that the rendered `"<|begin_of_text|>Q:"` begins
   `[2, 52]` (exactly one BOS, first). With left padding the BOS sits
   after the pads under an attention mask of 1, as the training
   sequences had it at position 0. The pinned render is carried on
   every record (`render: "bos"`), and the analyzer refuses a record
   without it.

   The prefix is applied by `battery_2n.BosRunner`, which wraps 2c's
   frozen `HFRunner` and prepends `BOS_TOKEN_2N` to every prompt
   STRING before delegating to `generate` — `evaluate_items` (2g,
   frozen) renders the prompt text itself, so the prefix has to go
   between it and the model. Every stage builds its runner through
   that class (three factory sites; the preflight additionally builds
   one bare `HFRunner` to print the plain render, and nothing it
   prints is stored). Gate 1 cannot detect a render change between the
   two stages — both loader paths render through the same tag-bound
   `BosRunner` — exactly as it cannot detect a dtype change; the
   tag-bound constant is the check.

   If dial n is ruled the other way, the constant flips to
   `render: "plain"` and the second assertion becomes "no special id
   anywhere in the render" — one constant, ruled before the tag.
3. **The stop id (dial o, recommended: the tokenizer's EOS).** Both
   loader paths set `model.generation_config.eos_token_id = EOS_TOKEN_
   ID_2N` (3) after loading and assert it, and every record carries
   `eos_stop_id: 3`. Because the three
   endpoint `which`es carry no checkpoint record, each ENDPOINT ITEM
   RECORD additionally carries the loader's OWN measured
   `config_eos_token_id` and `generation_eos_token_id`
   (`eos_facts_2n`, read off the loaded model after the override), and
   the analyzer requires the measured generation eos to be the pinned
   stop id — the `eos_stop_id` field is the constant the record
   wrapper stamps and is not, on its own, evidence that the override
   ran (freeze F-1). Sweep steps and the twin carry the same two ids
   on their `_checkpoint.json` and are barred the same way.
   The harness itself is untouched (2c's
   `HFRunner.generate` verbatim). If ruled the other way, nothing is
   set and the record carries `eos_stop_id: 2` with the disclosure.
4. **The predictors, loaded through their own seals** — 2m §3.3
   verbatim: x_A^(256) = 2k's sealed 1b tier through `load_tier_2k`,
   `exp2k-predictor-sealed` required to bind; x_A^(64/128/192) from the
   same rows (S1); x_A^(256) at 410m (S2); x_B = 2i's sealed OLMo-2 1B
   counts, `exp2i-predictor-sealed` required to bind.
   `PREDICTOR_SHA_2N = sha256("2n|" + <2k seal sha> + "|" + <2i seal
   sha>)` — the prefix separates 2n's records from 2l's and 2m's
   composites of the same two seals. π = 2j's `wrong_target_propensity`
   on 2i's x_B rows (S5). No new sampled quantity anywhere in 2n.
5. **The endpoint stage.** Three thin loads on all 34 rungs, per-item
   bits and continuations stored (2c's greedy harness,
   `BATCH_SIZE_2N` = 16, `DTYPE_2N` = fp16 — single pre-tag constants
   as in 2l/2m, dials l, m; `dtype` overridden on every record and
   pinned by the analyzer): `stage1-step460000-tokens965B` (the
   OUTCOME's endpoint: fixes R by rule, feeds the power record, is gate
   1's referent), `stage2-step018000-tokens1002B` (the last published
   cool-down checkpoint, descriptive) and `main` (the released average
   of the cool-down checkpoints, descriptive). Committed and tagged
   `exp2n-endpoint-sealed` before any intermediate checkpoint loads;
   ≈ 3 × 80 min. The seal binds 104 files (3 × 34 endpoint records +
   `rung_set_2n.json` + `power_2n.json`); the composite `endpoint_sha256`
   every sweep record stamps is taken over the same 104; the three
   whichs' coherence measured as 2m's (34 records per which, one
   non-empty tensor digest, commit and config source each).
6. **The outcome is Comma's stage-1 grid** — dial c, recommended shape
   (uniform), on the 10k-step lattice the branch offers:

       S = {10,000} ∪ {20,000 · j : j = 1 … 23}      (10k, 20k, 40k, …, 460k)

   24 points, all present on the branch (verified 2026-09-06, metadata
   only), plus the seeded twin; the endpoint 460,000 is a grid point,
   so gate 1 is the sweep's own first unit. y_i = number of grid points
   at which item i verifies (2g's count outcome; range 0..24); first-
   correct step printed beside it. The **every-40k subset** ({40k · j :
   j = 1 … 11} ∪ {460,000}, 12 points, y re-counted over its own points,
   max 12) is printed as the grid-density CONTROL (2m's process note 3
   — a control, not a descriptive).

   The sensitivity's row is stamped `"control": True` as a LITERAL in
   the verdict record, not as a computed rule — so a reader cannot
   mistake the control for a descriptive that happens to have been
   printed.

   Alternatives: all 46 stage-1 points
   (≈ 65 h) or a 2m-shaped dense head (every 10k to 100k + every 40k
   to 460k, 19 points, ≈ 28 h).
7. **Gate 1** = the endpoint reproduced through the sweep's checkpoint
   loader: per-item bits identical to the endpoint record on all 34
   rungs, continuations identical with the compared count attested and
   required to be 500/rung, tensor digest equal, RE-DERIVED by the
   analyzer from the two committed record sets. Runs first in the
   sweep; a diff halts with the tree the analyzer reads as
   INSUFFICIENT_DATA (both halt artifacts refuse — 2k F-1). The two
   paths differ in how the generation config reaches the model (the
   thin loader takes the branch's file; the candidate-file loader
   stages shards + the pinned `config.json` and derives it) — dial o's
   override makes them agree by construction, and gate 1 measures it.
8. **The corpus annotation C** — new. Computed from S4's thinned x_B
   (2k's block rule: k_g = clip(round(256 · r̄_A / r̄_B), 1, 64) per
   rung, the first k_g draws, no seed) and x_A^(256) over the
   intersection of the two tests' eligible sets, Δ = T_B,matched −
   T_A,256; CI95 by 2m's paired item bootstrap (items resampled with
   replacement within each rung, both predictors read on the same
   resample, `n_boot` beside `n_boot_requested`). Reads B-LEADS /
   A-LEADS / NO-LEAD by the rule in §1; `covers_3b_increment` (+.0659)
   and the three committed increments (+.054 / +.069 / +.066) printed
   beside it. Printed in every world; it never enters the verdict's
   world.

   "The first k_g draws" is exactly `row[:k_g]` on every item — one
   deterministic block. S4's own `per_rung` reading, the MEAN over all
   `64 // k_g` blocks of that width (2j's `_block_reading`), is
   printed beside C in the same verdict under `secondaries["S4 matched
   density"]` — two numbers, one rule, and the rule C reads is the
   first block's.

   C's Δ is a first-block estimator while `covers_3b_increment`'s
   referent — 2m's +.0659 — and the 2k/2l increments printed beside it
   (+.054, +.0687) are all-blocks means (S4's `per_rung` mean over `64
   // k_g` blocks of that width). The comparison is therefore between
   a single-block statistic and a block-averaged one. The asymmetry is
   conservative in direction — the single block carries more sampling
   noise, so C's interval is wider, never narrower, than an all-blocks
   interval would be — and it is disclosed here rather than fixed; the
   projection quotes both numbers, C's first-block Δ and S4's
   all-blocks increment, when it places the annotation.

   `covers_3b_increment` is measured against 2m's OWN committed
   number, read at analysis time from
   `experiments/exp2m/results/verdict.json` → `secondaries["S4 matched
   density"]["increment"]` — a pre-campaign referent-manifest entry,
   so a post-close edit refuses at `check_referents` — and asserted
   equal to the literal `0.0659` to four decimals as a known-answer
   gate. The 2k and 2l increments (+.054, +.0687) are printed as
   literals with their sources named, not read.
9. **The tree.** INSUFFICIENT_DATA → the joint reading of Tests A and
   B → SHARED / PYTHIA-ONLY / OLMO-ONLY / NEITHER, each carrying the
   annotation C. Every quantity of §5 printed in every world. Ruling
   18's undefined branch retained (unreachable for A — x_A^(256) is
   non-degenerate on every strata rung; reachable for B only if x_B is
   constant inside every stratum of every rung, which 2i's tiers rule
   out on the nine).
10. **Pins.** `FROZEN_SHA256_2N` over every module named (2m's list +
    2m's own instrument blobs, now frozen bytes); `IMPORTED_SHA256_2N`
    over the resolved module table at entry and exit; a pre-campaign
    referent manifest (2m's list + 2m's verdict, seal, power, endpoint
    and sweep records — S8 now reads 2m's committed per-item outcome
    too — plus 2n's `checkpoints_2n.json`, the Hub inventory and
    `power_2n.py`) — 4,427 files in total, including 2m's OWN campaign
    artifacts (its 102 endpoint records, rung set, power record,
    946-file sweep tree, `gate1.json` and `verdict.json`), which S8, S9
    and C read — its sha a literal in the analyzer; the campaign's
    own artifacts bound by `exp2n-endpoint-sealed` and cross-checked at
    analysis time exactly as 2m's were, so the preregistration tag is
    never re-cut after the campaign. Blob-bound tags: `exp2n-
    preregistered` binds the analyzer, the battery module, the endpoint
    stage and the sweep runner.

    The mutation battery's four logs (`mutation_build.log`,
    `mutation_fast_survivors.log`, `mutation_totality.log`,
    `mutation_fullshape.log`, plus the freeze's own) are COMMITTED
    (Ruling R-7), so the tally is reproducible from git rather than
    from the ledger's table alone.

## 4. Rung set, strata and power

**R_Comma** — the rungs whose stage-1 endpoint count clears 2d's bar
(one-sided exact binomial against 2d's model-free floor, max(majority
share, 1/n_options), 2d's α), fixed at the endpoint stage by rule. Not
known now. OLMo-2 7B cleared 13 of 34 at 4 T tokens, 13B 18 at 5 T,
SmolLM3-3B 14 at 8.1 T; a 7 B Llama at 1 T tokens of curated text is
the weakest endpoint in the line and may clear fewer.

**Strata.** 2g's committed table (eleven rungs). The primary for both
tests runs over **R_PRIMARY = R_Comma ∩ 2i/2k's nine** (add3_mid,
add_base8, antonym, antonym6, arith_next, odd6, sub3_mid, sub4_mid,
sub_base8) — x_A^(256) exists only on the nine. The rest of the eleven
that clears the bar is printed as **R_ELEVEN_EXTRA** with the 64-draw
x_A and x_B in 2g's strata; the rest of R_Comma as **R_EXTRA** with raw
single-stratum D; neither is ever in the verdict. Fewer than three
rungs in R_PRIMARY → THIN declared in the power record, the verdict
still runs; a test that ends up READING fewer than three rungs carries
2l F-4's disclosure on the reason and the licence. A rung can be inside
R_PRIMARY and outside both tests (2d's endpoint bar clears at k = 9 on
add3_mid and sub4_mid, 15 on sub3_mid, 19 on arith_next — below the
n_pos ≥ 20 eligibility floor); whenever a test reads fewer rungs than
R_PRIMARY the verdict names them and states SAME or WIDER against the
power record's `rungs_simulated` (2m R-1). `primary_is_the_nine`
printed either way. **The corpus annotation C reads over the
intersection of the two tests' eligible sets** and names that set.

**Predictor degeneracy.** As 2m §4: x_A^(256) has at least two live
strata on every strata rung (2k); x_B at ceiling inside a stratum drops
that cell; a rung with no informative cell is dropped from Test B and
printed. **Outcome ceiling:** an item that verifies at every grid point
has y = 24; the ceiling fraction per rung is printed in every world
(S7) under the analyzer's definition, and first-correct is the
sensitivity that reads earliness where the count saturates. No new
rule for it.

**Power**, written ONCE at the endpoint stage, before the projection,
per test, with 2i's machinery over the REAL predictors: n_pos bounded
below by the endpoint count, y from a latent mixing rank(x) at
calibrated strength inside the test's strata, every cell through the
verdict's own tree; bar P(fires | D = .15) ≥ .75, else DECLARED
UNDERPOWERED IN ADVANCE per test; P(fires | D = .10) printed (the bar
decides). Test A's predictor block SD printed as in 2l/2m (dial h).
New line (dial h): the SD of Δ = T(x_B thinned) − T(x_A^(256)) across
simulated outcomes, in THREE arms — a null arm (ρ = 0) and one arm per
test at its own calibrated strength at D = .15 (`delta_null_sd`,
`delta_sd_at_declare_A`, `delta_sd_at_declare_B`) — plus the paired
item bootstrap SD of Δ on the FIRST null outcome
(`delta_boot_sd_null`, taken as the CI95 width over 2 × 1.96), from
which `min_detectable_delta = 2.63 × delta_boot_sd_null` follows by
the normal approximation (CI95 excludes zero with power .75). That
formula is carried on the record as a pinned string AND the number is
re-derived from it at analysis time (freeze F-3). The block also
carries `k_by_rung` and `rungs`; `rungs` is R_PRIMARY minus the UNION
of the two predictors' degeneracy sets, which can be WIDER than the
set the annotation C reads (the intersection of the two tests'
eligible sets, which also drops n_pos-thin rungs) — whenever it is,
the verdict discloses the extra rungs and the licence is bounded to
the rungs C named as read (freeze F-2, Ruling R-6). The projection
places its Δ call against
that SD; the annotation is read under it. Shape note verbatim (item-
level alternative; nothing transfers to a class-level effect).

## 5. Named secondaries (printed in every world; no α claim)

- **S1 — the ladder on a third sealed outcome.** T_A at k = 64, 128,
  192, 256 (2k's nested blocks) → Comma; the four 64-draw blocks' T's
  and their SD. 13B: no block cleared at 64; SmolLM3: three of four.
- **S2 — 410m at 256** → Comma (410m ≥ 1b on 7B and 13B, tied on
  SmolLM3; a fifth reading).
- **S3 — the increments both ways, and the paired difference** (2m
  §5 verbatim): B-beyond-A, A-beyond-B, T_B − T_A with the paired
  bootstrap interval under the density caveat.
- **S4 — the matched comparison** (2m's; it now also feeds C): x_B
  thinned to x_A's per-rung rate against x_A^(256) — "which family's
  small model reads Comma's order better at equal draws".
- **S5 — the answer prior as a sealed-outcome forecaster,** its third
  test: 2j's π on 2i's x_B rows against Comma's order with 2i's
  statistic. 13B .1848, SmolLM3 .2417; the retirement clause (π ≤ .05)
  stands. Non-gating.
- **S6 — the referents.** The seeded twin's per-rung counts (expected
  ≈ 0); the cool-down endpoint and the released average vs the stage-1
  endpoint per rung (what 35 B tokens of upweighted curated text and
  checkpoint averaging change).
- **S7 — textures.** Ever-vs-final verification per rung, transient
  clears on flat rungs, checkpoint-local collapses (2h's class; 55 on
  SmolLM3, 0 on OLMo-2), non-monotone trajectories, first-correct
  steps, the ceiling fraction per rung under the analyzer's definition,
  the reversal pair descriptive.
- **S8 — outcome-to-outcome order,** extended. The committed per-item
  count outcomes of Pythia-2.8b (2g), Pythia-6.9b (2h), OLMo-2 7B (2i),
  OLMo-2 13B (2l) and **SmolLM3-3B (2m)** each read as x against
  Comma's order with 2g's statistic in the same strata — 2m's
  construction plus one row; `fires_2i` mechanical, `no_alpha_claim`
  on every row. **S8c — the corpus contrast:** mean of the two Pile-
  trained rows minus mean of the three DCLM-class rows, paired item
  bootstrap CI95.

  The two groups are exactly `{pythia_2.8b, pythia_6.9b}` and
  `{olmo2_7b, olmo2_13b, smollm3_3b}`, and the contrast is mean(Pile)
  − mean(DCLM-class) over the rungs every one of the five rows covers,
  through the same `paired_contrast_2n` the annotation C uses — every
  row read on the SAME within-rung item resample, `n_boot` reported
  beside `n_boot_requested`.

  On SmolLM3 the DCLM pair read .46 / .40 and the Pile
  pair .25 / .23; the corpus account predicts the sign to flip here,
  the predictor account is silent (S8 involves no predictor). The
  outcome-side, density-free read of the corpus question.
- **S9 — the sign ledger.** Per-rung D on the three option rungs for A
  and B across the four cross-family-readable outcomes (7B from 2k/2i,
  13B from 2l, SmolLM3 from 2m — committed verdict records, referents —
  and Comma from this run), one table, descriptive.

  S9's four sources: this run's per-rung D for A and B; 2l's and 2m's
  per-rung D READ from their committed `results/verdict.json`
  (`tests.A/B.per_rung.<rung>.d`, referent-manifest entries, and a
  known-answer gate in the cold battery); and 2k's / 2i's OLMo-2 7B
  readings as LITERALS with their sources named — antonym A +.024 (2k
  VERDICT, the 256-draw per-rung table) / B +.217 (2i VERDICT, Test B
  per rung), antonym6 A **+.115** / B +.214, odd6 A **+.096** / B
  +.121 (the antonym6 and odd6 A values corrected pre-tag by Ruling
  R-5 from the committed 2k VERDICT).

- **Sensitivities:** the first-correct outcome as y; the every-40k
  subset as y (the density control, §3.6); Test B in 2i/2l's
  conditioned form beside the unconditioned one;
  (struck at ratification, 2026-09-07: 'the primary over the nine when
  R_Comma ∩ eleven ⊋ nine' — x_A^(256) exists only on the nine, so
  R_PRIMARY can never exceed them and that sensitivity has no
  computable row; the eleven's remainder is printed as R_ELEVEN_EXTRA
  with the 64-draw predictors, §4);
  C under the plain (unmatched)
  paired difference beside the matched one.

## 6. Licences, written in advance

The world governs the cross-family sentence; the annotation governs
the corpus sentence. Both are bounded to item grain, one battery, and
the rungs named as read; Test B's "smaller model" is bounded to
parameters (§2).

- **SHARED:** the essay's cross-family sentence generalises to a fourth
  family — "smaller models of two families, given enough draws,
  forecast what a fourth family's training surfaces first, including a
  family trained on no DCLM-class web" — with Prediction 2's output-
  channel form holding across families at item grain on two predictor
  families and three outcome families (still one battery); the
  "structure latent in the training distribution" reading gains a leg
  that does not run through shared web text. Headline condition
  carried from 2l/2m: the shared component may lead the essay's
  sentence only if Test A's per-rung CI excludes zero on at least half
  the rungs it read; otherwise the sentence leads with Test B and
  names A as bar-clearing on a minority of rungs.
  - with **B-LEADS covering +.066:** the DCLM predictor's margin is
    predictor-shaped, not corpus-shaped; 2m's "corpus plus density"
    reading is retired in the essay and `experiments.md` in favour of
    "density plus predictor strength"; the corpus question is answered
    in the negative at this resolution, and the essay says so. Named
    next: the mechanism question, or a predictor-side experiment (x_B
    at 256 draws) — Michael's call.
  - with **A-LEADS, or NO-LEAD excluding +.066:** the margin follows
    the corpus; the shared-text component is real and measurable at
    matched density; the essay's cross-family sentence stands and gains
    "the margin between predictors tracks what their corpora share
    with the outcome's"; S8c and S9 are the descriptive check the
    licence names.
  - with **NO-LEAD covering +.066:** undecided at this resolution;
    the blind region is the annotation's CI; nothing about the corpus
    is licensed beyond the disclosure.
- **PYTHIA-ONLY:** the transfer follows the corpus in the direction
  the corpus account predicted (the predictor sharing the outcome's
  dominant sources reaches it, the DCLM one does not); the essay's
  sentence is bounded to "between corpora that share their dominant
  sources", and the density competitor (x_B at 64 draws) is named as
  the alternative S1/S4 adjudicate descriptively. Named next: x_B at
  256 draws on this outcome.
- **OLMO-ONLY:** the corpus account is disconfirmed in its own
  direction; the stronger predictor reaches a Pile-like outcome the
  Pile predictor cannot; the essay's cross-family sentence is bounded
  to "the DCLM-trained predictor", and the program's next step is
  Michael's call.
- **NEITHER:** the cross-family finding is bounded at the two
  DCLM-class outcome families (three sealed outcomes) in the essay and
  `experiments.md`; the full Comma record reported; the next step is
  Michael's call.
- Any world: S1–S9 and C in full; the twin, the cool-down endpoint and
  the release, the flat and extra rungs reported; S5, S8 and S8c
  stated as descriptive.

## 7. Run plan and model contact

Design (this doc + rulings) → build (`experiments/exp2n`: the Comma
manifest from a committed Hub scan with the candidate rule, the two
loaders with the render and stop-id pins, the seeded twin, the endpoint
stage, the sweep runner, the two-test analyzer with the four worlds,
the annotation C and S1–S9, power with the block-SD and Δ-SD lines,
referents, fixtures, worlds for every terminal and every annotation
cell, totality, mutation, read sweep, import scan) → adversarial
freeze → tag `exp2n-preregistered` → **preflight (dial j) on Michael's
word:** 2c's harness on `main` (the released average) for 20 items each
of `antonym` and `add3_mid`, continuations printed to the ledger and
stored nowhere the analyzer reads — a format, memory and PRECISION
check: logits scanned for NaN/Inf over the 40 prompts at fp16, the
collapse texture noted, **both renders printed** (the pinned BOS render
and the plain one, 40 items each, descriptive — dial n was ruled on
the training-config evidence, and this is where the ruling meets the
model), the rendered ids printed for one item under each; ONE stage-1
checkpoint staged through the candidate-file loader end to end —
**step 10,000** — downloaded (14 GB), sha-verified against the
manifest, hardlinked into a clean directory with the entry's own
`config.json`, loaded, scored on the same 40 items and **freed**; peak
memory printed for dial p. The preflight writes nothing under
`experiments/exp2n/results/` and asserts so afterwards; it applies
`check_frozen_2n` but not `require_prereg_2n`. If the preflight shows
fp16 overflow, `DTYPE_2N` changes once to fp32 (≈ 27 GB; ≈ 2× the time;
the mlx servers come down) before the tag is re-cut (2i's precedent,
disclosed in PROVENANCE); if it shows the pinned render degenerate in
a way the plain one is not (or vice versa), that too is a pre-tag
change plus a re-tag, ruled by Michael on the printed continuations,
never on outcome data (nothing the preflight prints enters any
record). → **stage 1 (endpoint)**: the stage-1 endpoint, the cool-down
endpoint and `main` through the thin loader on all 34 rungs (≈ 4 h,
3 × 14 GB), R fixed by rule, power printed once (with the block-SD and
Δ-SD lines — the Δ-SD line adds three 200-simulation arms and two
`calibrate_rho` calls to the power stage, so budget roughly twice 2m's
127 minutes for `power_2n`), committed, tagged
`exp2n-endpoint-sealed` → projection
sealed (by rung type; the corpus account's swap and the predictor
account's constancy each a claim with its own disconfirmer; tolerances
both directions; the analyzer's ceiling definition quoted; the verdict
calls placed against the block SD and the Δ call against the Δ SD) →
**stage 2 (sweep)**: gate 1 first (the endpoint through the candidate-
file loader), then the twin, then the 23 remaining grid points
ascending, ≈ 80–85 min each at fp16 (2i's 7B measured ≈ 82 min, plus
download), ≈ 35 h, ≈ 340 GB streamed one checkpoint at a time and
deleted, the watcher committing every record after its size stops
changing, processes launched via `Popen(start_new_session=True)` (2m
kill #1: nohup + disown does not hold in a tool shell) with one
disposable tracked poller → analyzer once, detached, on Michael's word
→ `exp2n-closed`. One pre-committed change.

Compute: the Mac for every stage (the stack behind every byte-
identical reproduction in this line; gate 1 is byte identity between
2n's own two loader paths). Memory: fp16 7.0 B ≈ 14 GB + activations
at batch 16 (2i ran OLMo-2 7B at the same shape); the mlx servers stay
up unless the preflight shows pressure (dial p; 2l's kernel panics
were 13B under memory starvation). Disk: peak ≈ 14 GB (one checkpoint)
+ the thin loader's three revisions in the ordinary HF cache (≈ 42 GB);
275 GB free at design time, with 2m's SmolLM3 revisions (≈ 17 GB) and
the Pythia 6.9b/12b caches (≈ 35 GB) clearable by the operator.

## 8. Alternatives considered

Outcome family: Comma v0.1-1T is the one 2m's §6 licence named under
SHARED, and the Hub shortlist's sharpest corpus control (2m §8: Amber
is RedPajama — a Common-Crawl corpus — and Apertus is 15 T of
multilingual web; neither asks the corpus question). Comma v0.1-2T
publishes no intermediate checkpoints. The raw lingua checkpoints in
`comma-v0.1-checkpoints` are the same 46 + 9 points in `model.pth`
form and add nothing.

Design alternatives not taken: **C as a third preregistered test at
2g's bar** (a permutation p on a difference of two T's has no natural
null in 2g's machinery — the item permutation within rung × stratum
nulls both T's at once, not their difference — and a third α-test
widens the uncalibrated union; the CI rule is the honest form);
**S8c as the primary corpus reading** (outcome-side and predictor-free,
but a contrast among five known outcomes read against one sealed one —
kept as the named descriptive check); **the 2T release as a fourth
descriptive which** (≈ 80 min + 14 GB; nothing in §6 reads it — a dial
if Michael wants the second-epoch datum); **the full 46-point grid**
(≈ 65 h; the count at 24 already resolves 0..24 and the every-40k
control measures what density buys); **a Comma-family predictor**
(there is no smaller Comma; a fresh predictor would be predictor-side
contact for a question this design does not ask); **Test B
conditioned on A** (printed as a sensitivity, as in 2m).

## 9. What 2n does not claim

Not "Prediction 2 supported across families" beyond item grain, one
battery, two predictor families and three outcome families. Not a
statement about disjoint text (source-level overlap is disclosed and
used: the Pile and the Common Pile share nine source kinds; no
document-level intersection is computed). Not a statement about the
corpus beyond the annotation's cell and its CI (the corpus and the
predictor accounts are separated only at matched density, on one
outcome, on the rungs read). Not a mechanism result (S5, S8, S8c, S9
descriptive). Not a statement about the cool-down stage or the
averaged release beyond S6's descriptives. Not "from below" in tokens
for Test B. Not a statement about the across-task ranking.

## 10. Dials — RULED by Michael 2026-09-06 ("Dials as recommended — build and freeze"): every dial as recommended

- **a. Outcome model:** Comma v0.1-1T stage 1 (`common-pile/comma-
  v0.1-1t`), **recommended** — the family 2m's licence named; the
  alternatives are §8's and none asks the corpus question.
- **b. Tests and worlds:** A = x_A^(256) and B = x_B^(64) each
  UNCONDITIONED on its own bar; worlds SHARED / PYTHIA-ONLY /
  OLMO-ONLY / NEITHER; the increments both ways and the paired
  difference printed (S3), **recommended** (2m's tree, so the fourth
  family reads on the third's).
- **c. Grid:** uniform — 10k plus every 20k to 460k: 24 points, ≈ 35 h
  with the twin, **recommended** (a 1 T run on a weak model surfaces
  items across the run, not in a head); vs all 46 (≈ 65 h) vs a
  2m-shaped dense head (19 points, ≈ 28 h). The every-40k subset is
  printed as the density control under any choice.
- **d. Descriptive endpoints:** the stage-1 endpoint (outcome) + the
  last cool-down checkpoint `stage2-step018000` + `main` (the averaged
  release), **recommended**; vs adding `comma-v0.1-2t`'s `main` as a
  fourth which (≈ 80 min + 14 GB; the second-epoch datum, read by
  nothing in §6) — not recommended, available on his word.
- **e. Rung set:** R_Comma by 2d's floor rule at the stage-1 endpoint;
  R_PRIMARY = R_Comma ∩ the nine; the eleven's remainder and R_EXTRA
  printed; THIN below three, **recommended**.
- **f. Projection:** sealed after the endpoint stage and before the
  sweep; by rung type; the corpus account's swap and the predictor
  account's constancy each stated as a claim with its own
  disconfirmer; every disconfirmer with a tolerance in BOTH directions
  (2m's note 1); the analyzer's ceiling definition quoted (note 4);
  the verdict calls placed against the block SD and the Δ call against
  the Δ SD, **recommended**.
- **g. The corpus annotation C:** a preregistered CI-rule annotation
  (B-LEADS / A-LEADS / NO-LEAD on Δ = T_B,matched − T_A,256, with
  `covers_3b_increment`), printed in every world, never in the
  verdict's world, **recommended**; vs descriptive only (the corpus
  question then has no preregistered reading — the licence could say
  nothing); vs a third test at 2g's bar (§8: no natural permutation
  null for a difference of T's; widens the union).
- **h. Power record** prints Test A's block SD AND the null SD of Δ
  with `min_detectable_delta`, **recommended**.
- **i. Init referent:** a seeded `from_config` twin of the stage-1
  config (no step 0 on the branch), descriptive, **recommended**.
- **j. Preflight on his word:** 20 items × 2 rungs on `main` + step
  10,000 staged through the candidate-file loader; the fp16 precision
  scan; BOTH renders printed; peak memory printed; nothing stored,
  **recommended**.
- **k. Bars .10 / .01 unchanged,** **recommended**.
- **l. Precision:** `DTYPE_2N` = fp16 (every 7B/13B/3B outcome's
  precision), fp32 the pre-tag fallback (a re-tag, disclosed),
  **recommended**.
- **m. Batch:** `BATCH_SIZE_2N` = 16, **recommended**.
- **n. Render — the dial that bites:** `render: "bos"` — one
  `<|begin_of_text|>` (id 2) prepended to every prompt, after the pads,
  **recommended**, because Comma was trained with a BOS on every
  sequence (lingua `add_bos: true`) and the Mac stack's plain render
  adds none (measured, §2): the model is scored in the input condition
  it was trained under, which is what every prior family's plain
  render also achieved. vs `render: "plain"` (the stack's default and
  the literal convention of every prior family, but the first time it
  would put a model outside its training condition; a Llama trained
  with BOS is known to degrade without it). Pinned as one constant,
  asserted on every load, carried on every record; the preflight
  prints both.
- **o. Stop id:** set `generation_config.eos_token_id` = 3 (the
  tokenizer's `<|end_of_text|>`) in both loader paths and assert it,
  `config.json`'s 2 disclosed on every record, **recommended** (every
  prior family stopped at its real EOS; the harness is untouched); vs
  leaving config's 2 (generation never stops at the real EOS; post-EOS
  text is what 2c's parsers read).
- **p. The mlx servers** stay up unless the preflight shows memory
  pressure, **recommended** (2m kept them up at 3B; 2i ran 7B at this
  shape); vs booting them out for the campaign as in 2l.
- **q. S8 extended** with the SmolLM3 row and the corpus contrast S8c;
  **S9 the sign ledger** over the four outcomes, **recommended**; vs
  2m's S8 unchanged.
- **r. Build + freeze in one session** by SDD, the import pin from
  commit one; licences as §6, **recommended**.

## 11. Process

Design → rulings → build → freeze → tag → preflight on his word →
endpoint stage → seal tag → projection → sweep (detached via Popen,
watcher, one poller) → analyzer once, detached, on his word →
`exp2n-closed` → close-out propagation (essay under §6,
`experiments.md`, the graft with the three tags, Zenodo v1.17, paper
inventory).
