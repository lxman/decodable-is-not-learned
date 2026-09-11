# Experiment 4 — Design Doc: Convergence Tracks Scale — Does Cross-Family Agreement About a Task's Items Arrive Before the Task Performs?

**Status: session 1 (design) written 2026-09-10 on Michael's word
("Let's set up experiment 4"). This is the fourth experiment of the
original five-experiment program (`experiments.md` §"Experiment 4:
Convergence tracks scale (the lens extension)"), never designed until
now; every other line of the program (1/1b/1c, 2 through 2n, 3a
through 3e) has closed. §10 DIALS a–s RULED by Michael 2026-09-10 ("go"): every dial as
recommended — build and freeze. No model
contact of any kind has occurred and none is proposed before the tag;
the Hub has not been read — every checkpoint manifest this design
needs is already committed by 2g, 2i, 2m and 2n and is reused
verbatim. Huh et al. (2024) was read for its construction (the paper
and the released code, `minyoungg/platonic-rep`): mutual k-nearest-
neighbour alignment at k = 10 on cosine-normalised features, language-
model features average-pooled over valid tokens at every block, the
reported score the maximum over layer pairs, the input bank 1,024 WIT
captions. That construction is reproduced here as a sensitivity (§5
S7); the primary uses this program's own positions and site family.
Model contact, when sanctioned: forward passes only — no generation,
no sampling, no new outcome. Every outcome this experiment reads is
committed and tagged (2c/2d for the Pythia size ladder; 2g, 2i, 2m, 2n
for the four training trajectories).**

The essay's convergence paragraph is the one leg of the lens claim the
program has never tested. It cites Huh et al.: as models scale, their
representations converge across architectures and training runs, and
"if each model constructed its capabilities, there would be no reason
for independent constructions to agree." `experiments.md` turned that
into a prediction with two parts — alignment between independently
trained models should rise smoothly with scale on resolution-class
capabilities, and "alignment on a capability's representations
[should rise] *before* the capability becomes reliable at argmax."
The second part is the one that separates the lens view from the
construction view, and it is the primary here. Everything the program
built since 2g — four families' training trajectories scored at item
grain on one 34-rung battery, every checkpoint's tensor digest
committed — makes it cheap to ask: the outcome side already exists on
92 committed checkpoints; only the representation side is new.

## 1. The question

**On the committed training trajectories of four families — Pythia
2.8b (2g), OLMo-2 7B (2i), SmolLM3-3B (2m) and Comma v0.1-1T (2n) —
does the agreement between a model's representation of a task's items
and the representations of three *other* families' released models,
read over the task's own 500 items, run ahead of the general
convergence trend before the task first clears the argmax bar; or
does the task-specific agreement arrive with, or after, performance?**

Three accounts make three predictions, and the design is built so each
lands in its own world:

- **The lens account** (the essay's): the structure is in the data; a
  model resolving a task is a lens sharpening on a scene every other
  lens is pointed at, so independent models agree about the task's
  items *as the resolution arrives*, which is before the argmax count
  clears the bar. Prediction: task-specific agreement precedes the
  clear → **LEADS**.
- **The construction account** (the strongest opposing case in the
  essay's own words): representation and execution are different
  things; two models that both fail a task have no reason to organise
  its items alike beyond surface statistics, and agree only once each
  has built its own solution, i.e. at or after the point where the
  task performs. Prediction: task-specific agreement arrives with or
  after the clear → **FOLLOWS**.
- **General convergence without task specificity** (Huh et al.'s
  global result, read narrowly): representations converge everywhere
  at once as a property of training, and the items of a task that
  clears carry no more agreement than the items of one that never
  does. Prediction: no measurable task-specific excess →
  **NO-CONVERGENCE** (or, where an excess exists but sits between the
  two accounts, **UNDETERMINED**).

The design's spine is the correction that makes the question non-
vacuous. Any quantity that rises monotonically with training "rises
before" a step function placed later in training; a naive precedence
test would pass on the calendar alone. So the primary reads each
rising task's alignment as an **excess over the flat rungs' pooled
trend on the same grid** — the 18–27 rungs of the same battery that
the same model never clears at any grid point — and asks what fraction
of the task's *endpoint* excess was already present at the last grid
point before its clear. Under general convergence that excess is zero
throughout; under construction it appears at or after the clear;
under the lens account it is substantially present before.

Worlds, in tree order: **INSUFFICIENT_DATA** → **NO-CONVERGENCE** →
**LEADS** / **PARTIAL** / **FOLLOWS** / **UNDETERMINED** (§3.9). Each
licence is written in §6 before any activation exists.

## 2. What is known and what is new (disclosure)

**Known, and known to the designer.** Every outcome. For each of the
four trajectories the committed sweep records carry, per grid point and
per rung, the 500 per-item verify bits and the count; 2d's floor rule
(max(majority share, 1/n_options), one-sided exact binomial at 2d's α)
applied to those counts gives, per rung, the first grid point at which
the rung clears (t_clear) and whether it clears at the endpoint (the
committed rung sets: R_OLMO 13, R_3B 14, R_COMMA 16, and 2g's seven at
2.8b). The Pythia size ladder's outcome is 2c's (2.8b/6.9b/12b argmax)
and 2d's (410m/1b argmax): 11 rising rungs, 23 flat. These numbers were
read while designing and are the reason the design can state its cell
counts in advance. This is 2f's situation, not 2g's: **the outcome is
known; the instrument has never been pointed at it.** No alignment
between any two of these models has ever been computed, on this battery
or any other, by this program. Every rule below — the representation,
the metric, the site family, the reference set, the trend correction,
the excess, the window, the eligibility rule, the statistic, the null,
the bars — is fixed in this document before the first forward pass and
bound to a blob-level tag before any activation is stored. The caveat
2d and 2e carried is carried here: **whatever fires is a preregistered
reading on a known outcome, not a forecast**, and the licensed
sentences in §6 say so.

**What the reference stage will reveal before the projection.** The
projection is sealed after the reference stage (§7) and before any
trajectory point loads. The reference stage computes, for every outcome
model at its endpoint and for the Pythia ladder at `main`, the per-rung
alignment with every reference — so the designer will know, before
projecting, whether the rungs each model clears sit above its flat
rungs in endpoint alignment (the eligibility count of §4), and the
per-rung standard errors. That is the same class of disclosure 2n's
endpoint stage made (rung set and power before the projection); it
reveals the endpoint excess, not its time course, and the primary is
entirely about the time course. The projection quotes the endpoint
excess table and projects the time course against it.

**What the surface floor is, and why the twin is not the referent.**
Two networks with independent random weights still agree above chance
about which of a rung's items are neighbours: items sharing question
tokens share embedding mass in both, and a random transformer's
residual stream is close to a bag of those embeddings. So the seeded
`from_config` twin's alignment with a trained reference is a measured
surface floor, not chance, and it is printed as the init referent
(S8), never used as the zero of the primary. The primary's zero is the
**first grid point of the same trajectory** (§3.5), by which point the
token-statistics part of convergence is already in place on every grid
this design reads (the earliest first points are Pythia 2.8b's and
OLMo-2 7B's step 1000; Comma's is 10,000, SmolLM3's 40,000), and its
trend referent is the flat pool, which shares every surface property
of the rising rungs' prompts (the same two-shot render, the same
question-answer cue, the same tokenizer) and none of their eventual
performance.

**Huh et al.'s construction, as read.** Mutual k-NN: for two feature
maps over the same n inputs, the k nearest neighbours of each input
under each map (cosine, k = 10), per-input overlap |S_f(i) ∩ S_g(i)|/k,
averaged over inputs; language-model features average-pooled over the
valid tokens of each input at every transformer block; the reported
alignment between two models the maximum over block pairs; the bank
1,024 Wikipedia captions; CKA and several kNN variants offered beside
it. The primary here departs from that construction in three ways,
each chosen for the question rather than for fidelity to the paper,
and S7 reproduces the paper's construction so the departure is
measurable: the position is 2c's prompt-end token (the position from
which the answer is emitted, where 2f's matched-label probe read the
answer's digit) rather than the token average; the site pairing is
depth-matched and averaged rather than maximised (a maximum over 144
site pairs is a selection, and its chance level rises with the number
of pairs); and the bank is the rung's own 500 items rather than a
generic corpus, because the claim is about a *capability's*
representations.

## 3. Instrument

Everything not named here is imported frozen and sha-pinned from the
committed instruments: 2c's item files (34 rungs × 500 eval items, the
sha pins `battery_2d.ITEMS_SHA_PIN`), render (`screen._render_prompt`,
two shots) and position rule (`screen._position_indices`); 2f's
activation collector (`collect_eval_2f.collect_items`: right padding,
`add_special_tokens=False`, `output_hidden_states`, fp16, the two
positions per item); 2c's site family (`probe_2f.site_family`: every
`LAYER_STRIDE` = 3rd entry of `hidden_states` plus the last — 12 sites
on a 32-block model, 13 on a 36-block one); 2d's floor table and
binomial bar (`battery_2d.majority_floor`/`option_copy_floor`,
`stats_2d.binomial_bar`), family blocks (`RUNG_ORDER_2D`, 16 families)
and AUC machinery (`stats_2d.primary_test`, `block_perm_auc_p`,
`cluster_bootstrap_auc`) for S2; the four checkpoint manifests
(`checkpoints_2g/2i/2m/2n.json`, the candidate rule, the per-revision
commit and per-file LFS sha256), their candidate-file and thin loaders
(2g's `load_checkpoint` with the pinned config; 2i's, 2m's and 2n's
`load_checkpoint_*`/`load_thin_*` with each family's tokenizer check
and, for Comma, the BOS render and the stop-id override — irrelevant
here since nothing generates, but asserted so the loaded object is the
one the outcome came from) and their twins (2b's `load_pythia(untrained
=True, seed=0)` for Pythia's real step 0 is not needed — Pythia has a
step-0 revision; 2i's `load_twin_7b`, 2m's `load_twin_3b`, 2n's Comma
twin); the referent discipline, the tree-totality closure, blob-bound
tags, the import-surface pin from commit one (2j F-1), `pins_active`
(2k D-1), the halt-marker rule (2k F-1), the loader-rehearsal preflight
(2i stop #1). The deltas:

### 3.1 The representation

For every model M loaded (a trajectory point, an endpoint, a reference,
a ladder size, a twin) and every one of the 34 rungs, the residual
stream at the two 2c positions — the question-end token and the
prompt-end token — at every site of M's site family, for all 500 eval
items, rendered exactly as the committed outcome sweep of M's family
rendered them (a literal table `RENDER_4 = {pythia: "plain", olmo2:
"plain", smollm3: "plain", comma: "bos"}`, asserted against the
committed records' `render` field where one exists and against the
tokenizer facts each family's frozen `check_tokenizer_*` pins), through
M's own tokenizer. Stored as fp16 `[500, n_sites, 2, d]` per rung (2f's
layout), gitignored, sha256 per file committed on the record. **The
batch composition is pinned** — item order as in the item file, a fixed
batch size per family (dial l), right padding to the batch's longest
prompt — because a valid position's fp16 residual can move by an ulp
when its batch-mates change; gate 1's identity requirement holds only
if both loader paths batch identically, and the collector refuses any
other layout. **The
primary reads the prompt-end position** (dial c); the question-end
position is S6. Additionally, for S7 only, the average over valid
tokens at every block (Huh's pooling), same storage.

No generation. `max_new_tokens` is never called; the harness's
`generate` path is not imported.

### 3.2 The metric

**Mutual k-NN alignment** (Huh et al. 2024, App. A; the released code's
`mutual_knn` with `topk = 10`, `normalize = True`): for two feature
maps f, g over the same n items, the k nearest neighbours of item i
under cosine similarity, excluding i, with ties broken by item index;
per-item overlap o_i = |S_f(i) ∩ S_g(i)| / k; alignment m(f, g) =
mean_i o_i. k = 10, n = 500 per rung, chance k/(n − 1) = .0200. The
per-item o_i are kept (they are what the standard errors, the item
bootstrap and S10 read). Computed in float32 on CPU from the fp16
stores with a single-threaded, pinned kernel (an exact
`argpartition` on the full similarity row, then a stable sort of the
k winners), so the k-NN sets are a deterministic function of the
activation bytes; the **k-NN sets** (`uint16 [500, 10]` per (rung,
site, position)) are the committed artifact of every load (§3.8), and
the alignment scalar is re-derived from two committed set tables, never
read from a record.

**Linear CKA** (Kornblith et al. 2019, centred, unbiased estimator as
in Huh's `unbiased_cka`) is computed at every site pair at load time
against the stored reference activations and printed beside the k-NN
alignment (S9). It is attested, not re-derivable — the trajectory's
activations are not kept (§3.8) — and is a sensitivity for that
reason.

### 3.3 References and pairing

The references are the released models of the families **other than
M's**: `EleutherAI/pythia-12b` at `main` (dial b; 6.9b the
alternative), `allenai/OLMo-2-1124-7B` at `main`, `HuggingFaceTB/
SmolLM3-3B-Base` and `common-pile/comma-v0.1-1t` at `main` (the
averaged release) — four released lenses, three per trajectory. Each
reference's activations are collected once at the reference stage and
stored (gitignored, sha-pinned, ≈ 13 GB for the four). For a
trajectory point of M and a reference Q, the **site pairing is by
relative depth**: M's site at hidden-state index ℓ of L_M is paired
with Q's site nearest in ℓ/L_M (12-site to 13-site pairings are fixed
by a committed table); the per-rung alignment between M-at-t and Q is
the mean over M's sites of the paired-site mutual k-NN; and

    a_r(t) = mean over the three references Q of m_r(M_t, Q)

is the rung's alignment at t — one number per (M, t, r). The mean over
sites is the reading (1c's mean-over-sites lesson: a mean is stricter
than a maximum and selects nothing); the maximum over all site pairs
(Huh's reading) and the single endpoint-best site are S5's
sensitivities. Per-reference values are printed in every world.

### 3.4 The trajectories and the outcome, verbatim from the record

The four committed grids, unchanged:

| M | grid (trained points) | init referent | endpoint | R_M (clears at the endpoint) |
|---|---|---|---|---|
| Pythia 2.8b (2g) | 1000, 2000, 4000, 8000, 10000, 16000, 20000, 30000, 32000, 40000, 50000, …, 140000, 143000 — 21 points (64000 excluded as a stale copy, 2g finding B) | real step 0 | 143000 | 2g's seven: add3_mid, add_base8, antonym, antonym6, arith_next, sub3_mid, sub_base8 |
| OLMo-2 7B (2i) | 1000, 2000, 4000, 8000, 16000, 32000, 64000, then every 64000 to 896000, 928646 — 21 points | seeded twin | 928646 | R_OLMO, 13 |
| SmolLM3-3B (2m) | every 40000 to 400000, every 200000 to 3400000, 3440000 — 26 points | seeded twin | 3440000 | R_3B, 14 |
| Comma v0.1-1T (2n) | 10000, 20000, then every 20000 to 460000 — 24 points | seeded twin | 460000 | R_COMMA, 16 |

92 trajectory points; the union of the four R_M is 17 rungs; 50 (M, r)
cells before the exclusions of §4. For each (M, r): **t_clear(r)** =
the first grid point at which the committed count clears 2d's bar (the
same rule that fixed R_M; re-derived at analysis time from the
committed per-item bits through 2d's `binomial_bar` and pinned as a
literal table at the build — a known-answer gate); **flat_M** = the
rungs whose count clears at NO grid point; **transient_M** = the rungs
that clear somewhere and not at the endpoint (2h's texture: sub3_mid
on 6.9b at four points; median5 on OLMo-2 7B seven times) — excluded
from both the rising and the flat set and printed. The floor is 2d's
per-rung table, identical on every model (it is a property of the
item file). Each trajectory point's tensor digest must equal the
committed sweep record's `digest` for that step (`_checkpoint.json`,
2g/2i/2m/2n), else the unit halts: the alignment is read on the bytes
the outcome came from, or not at all.

### 3.5 The excess and the pre-clear fraction

With t_1 the first grid point of M and t_end its endpoint:

    trend_M(t) = mean over r ∈ flat_M of a_r(t)                     (the flat pool)
    x_r(t)     = [a_r(t) − a_r(t_1)] − [trend_M(t) − trend_M(t_1)]    (the excess)

x_r is the rung's alignment growth since the first grid point net of
the flat rungs' growth over the same interval; it is zero at t_1 by
construction and zero throughout under general convergence. For a
rising rung with a pre-clear window (t_clear ≥ t_3, so that the last
grid point strictly before the clear, t⁻, is itself past t_1):

    φ_(M,r) = x_r(t⁻) / x_r(t_end)

the fraction of the endpoint excess that was present before the
capability first performed. Under construction φ ≈ 0 (the excess
arrives at or after the clear); under the lens account φ is large.
Cells with t_clear ≤ t_2 have no observable pre-clear window (x_r(t_1)
≡ 0) and are excluded with the reason printed; cells whose endpoint
excess is not measurable are excluded by §4's eligibility rule.

### 3.6 The primary statistic and its null

    T = mean over eligible cells (M, r) of φ_(M,r)

**Null: rung-level sign flips.** Under H0 ("no task-specific agreement
before the clear"), each rung's pre-clear excess is symmetric about
zero; the null distribution of T is obtained by flipping the sign of
φ for ALL cells of a rung together (a rung can appear in up to four
trajectories and its cells are not independent), enumerated exactly
over the 2^n_rungs flips when n_rungs ≤ 20 (the union of R_M is 17, so
this is exact — 131,072 flips), sampled at 10,000 otherwise with the
resolution disclosed. p_+ = the share of flips with T_flip ≥ T; p_− the
mirror. **CI95** on T: rung-clustered percentile bootstrap (resample
rungs with replacement carrying every cell of each; 10,000).

**Bars.** p_+ < .01 and T ≥ .25 fires LEADS (at least a quarter of the
endpoint's task-specific agreement present before the capability first
performs, on average over cells, distinguishable from zero at the
program's α). The effect bar is the dial the power stage prices (§4).

### 3.7 Gates

- **Known-answer gates on the metric** (cold, synthetic, pre-tag):
  self-alignment m(f, f) = 1; two independent Gaussian feature sets at
  n = 500, k = 10 → mean overlap inside the Clopper–Pearson band of
  .0200 over 100 seeds; invariance of m(f, g) to an orthogonal rotation
  and an isotropic rescaling of either side, exactly; a planted-
  structure calibration curve (Exp 1's discipline): f and g sharing a
  latent cluster structure with independent noise, m rising
  monotonically in the shared-signal fraction across 20 levels, the
  curve committed as a fixture so a code change that flattens it is
  caught; the CKA implementation checked against the same fixtures and
  against the published closed form on a 2-D case.
- **Known-answer gates on the outcome side** (cold, committed bytes,
  pre-tag): the four rung sets reproduced 34/34 per model from the
  committed endpoint records through 2d's floor rule; the t_clear
  table reproduced from the committed per-item bits; 2d's primary AUC
  .5455 and 2e's .6126 reproduced exactly from their committed records
  through the machinery S2 will use with the alignment predictor
  swapped in (the swap is a function argument; the referent runs first
  with 2d's own predictor).
- **Gate 0 — the instrument sees training** (reference stage; the
  verdict refuses without it): for every outcome model, the seeded
  twin's per-(rung, site) alignment with each reference is BELOW the
  trained endpoint's on at least 90 % of cells at the prompt-end
  position; the twin's values printed (S8). And the references'
  mutual alignments (each pair of the four released models, per rung)
  printed as the ceiling the trajectories approach.
- **Gate 1 — identity** (first unit of every trajectory's sweep, by
  rule): M's endpoint re-derived through the sweep's candidate-file
  loader against the reference stage's thin-loader collection —
  tensor digest equal to the committed 2g/2i/2m/2n record, activation
  files byte-identical (2f reproduced its collections at 0.0
  deviation eight times on this stack; identity is the requirement,
  not a tolerance), k-NN sets identical on every (rung, site, position)
  — coverage required 34 rungs × every site × both positions, counted
  by the analyzer, not attested (3d/2h's lesson). A diff halts with
  the tree the analyzer reads as INSUFFICIENT_DATA; both halt
  artifacts refuse (2k F-1). If the preflight (§7) shows two loads of
  the same weights disagreeing at the ulp level under the pinned
  batching, the identity requirement is replaced BEFORE the tag by a
  k-NN-set identity requirement alone plus a disclosed activation
  tolerance, ruled by Michael on the printed deviations — never after
  a sweep has started.
- **Per-unit digest pin** (§3.4): every trajectory point's tensor
  digest against the committed sweep record's; a mismatch halts.
- **Coverage per unit**: 34 rungs × 500 items × every site × both
  positions present with the file sha on the record, re-hashed by the
  analyzer; a short unit is INSUFFICIENT_DATA, never a smaller test.

### 3.8 Storage and what is committed

Per load: the k-NN set tables at the prompt-end position (34 × n_sites
`uint16 [500, 10]`, ≈ 4.4 MB raw, gzip-compressed — index data
compresses little, so ≈ 3.5 MB each, **committed** — dial g; ≈ 300 MB
over the 92 trajectory points), the question-end and
Huh-pooled set tables (**sha-attested**, gitignored), the per-(rung,
site, position, reference) alignment and CKA scalars (committed, small),
the per-item overlaps at the prompt-end position (committed, `uint8
[500]` per cell — what S10 and the bootstrap read), the checkpoint
record (revision, commit, per-file sha, tensor digest, download and
compute seconds, stack). The activations themselves are kept for the
references, the endpoints, the ladder sizes and the twins (≈ 40 GB at
the site family, ≈ 80 GB with S7's pooled variant, gitignored, sha on
the record) and DELETED for interior trajectory
points after their set tables are written and re-read (disk: 224 GB
free at design time; one 7B checkpoint's activations are ≈ 3.3 GB at
the site family and ≈ 3.3 GB more for S7's pooled variant). The
primary is re-derivable from committed bytes end to end: the outcome
from the committed sweep records, the alignment from the committed set
tables.

### 3.9 The tree

INSUFFICIENT_DATA (any halt marker; any missing or short unit; any
referent failure; gate 0 or gate 1 not passed; fewer than three
eligible cells) → **NO-CONVERGENCE** (fewer than three eligible cells'
worth of measurable endpoint excess: §4's rule leaves < 3 cells, or <
3 distinct rungs) → the primary: **LEADS** (p_+ < .01 and T ≥ .25) /
**PARTIAL** (p_+ < .01 and 0 < T < .25 — real, below the bar; 2i's
cell, named in advance) / **FOLLOWS** (p_+ ≥ .01 and the CI95 upper
bound < .25 — not distinguishable from nothing-before-the-clear, and
the bar excluded) / **UNDETERMINED** (everything else: the CI covers
the bar without p_+ clearing; or p_− < .01 with T < 0, which is printed
as the "agreement recedes before the clear" cell). Every cell the
analyzer can distinguish is named here (2n's process note 1).

Per-model T with its own sign-flip p is printed in every world, as is
T by rung type (arithmetic / option / string), with no α claim; the
pooled statistic governs.

### 3.10 Pins

`FROZEN_SHA256_4` over every imported module named above and this
instrument's own blobs; `IMPORTED_SHA256_4` over the resolved module
table at entry and exit (2j F-1); a pre-campaign referent manifest
over every committed file read — the four manifests, the four sweep
trees (`_checkpoint.json` and the 34 item records per point), the four
rung sets and endpoint records, 2d's and 2e's verdict records, 2c's
item files — with its sha a literal in the analyzer; the campaign's own
artifacts bound by `exp4-reference-sealed` (§7) and cross-checked at
analysis time. Blob-bound tags: `exp4-preregistered` binds the
analyzer, the battery/loader module, the metric module, the collector
and the sweep runner; a post-tag edit to any of them needs a re-tag
(2h F-3).

## 4. Cells, eligibility and power

**Cells.** (M, r) for r ∈ R_M, four M: 7 + 13 + 14 + 16 = 50 before
exclusions. Two exclusions, both by rule fixed here and both printed
with the cell named: (i) **no pre-clear window**, t_clear(r) ≤ t_2 — on
the committed records, which rungs clear at a trajectory's first or
second grid point is knowable now and is deliberately not tabulated in
this document (the analyzer prints it; the projection may not lean on
it); (ii) **no measurable endpoint excess**, x_r(t_end) < 2 × SE, with
SE the item-bootstrap standard error of x_r(t_end) (items resampled
with replacement within rung r and within each flat rung, per-item
overlaps re-averaged, 2,000 resamples; the neighbour sets are not
recomputed under resampling — the SE is that of the mean over items,
disclosed as an approximation). A cell excluded under (ii) is a cell
where the rung's endpoint agreement is not above the flat pool's: that
is a finding about the lens claim's premise, counted in NO-CONVERGENCE
when it takes the eligible set under three.

**The union of rungs** among eligible cells is the sign-flip null's
unit count n_rungs (≤ 17, exact enumeration).

**Power**, written ONCE at the reference stage, before the projection,
through the verdict's own code: the endpoint excess x_r(t_end) and its
SE are then real numbers for every cell; simulated trajectories place
the excess's rise as a logistic in grid index with its midpoint at
t_clear(r) shifted by a lead ℓ (the alternative: ℓ chosen so that the
pre-clear fraction is φ = .5 for every cell — half the task-specific
agreement in place before the clear; the null: φ = 0, the rise centred
at or after t_clear), noise per grid point at the measured SE, the
flat pool's trend as measured at the endpoint and interpolated
log-linearly in tokens between t_1 and t_end (the simulation's trend
shape is disclosed as an assumption; the analyzer's reading does not
depend on it), N_SIM = 1,000 per arm, every arm through the tree. Bar:
P(LEADS | φ = .5) ≥ .75, else DECLARED UNDERPOWERED IN ADVANCE;
P(LEADS | φ = 0) printed as the realised α; P(LEADS | φ = .25) printed;
the null SD of T, the min-detectable T at power .75 and the exact
resolution of the sign-flip null (1/2^n_rungs) printed. The endpoint
excess table, the SE table and the eligibility count are the power
record's inputs and are committed with it.

Process rule 4 (the bar ≥ 4σ from the null): with n = 500 items per
rung and o_i's SD ≈ .05–.15, a rung's alignment has SE ≈ .003–.007;
the excess is a difference of four such means; φ's noise is that
divided by the endpoint excess, so the rule is satisfiable only where
the excess is well above its SE — which is what eligibility rule (ii)
enforces, and the power record measures rather than assumes.

## 5. Named secondaries (printed in every world; no α claim)

- **S1 — the order.** Somers' D between the excess's half-rise grid
  index (first t with x_r(t) ≥ ½ x_r(t_end)) and t_clear(r) over R_M,
  pooled across M by 2g's mean-over-groups, with 2d's family-block
  permutation within each M as its descriptive p. The concordance BOTH
  accounts predict — rungs that agree earlier perform earlier under
  the lens account, and rungs that perform earlier agree earlier under
  construction — so it is not the primary; its being null while φ is
  not would be the texture to explain.
- **S2 — the third instrument on 2d's question.** The from-below
  alignment reading — x_r at Pythia 1b `main` against the three non-
  Pythia references, with the Pythia ladder's flat pool as trend —
  as the predictor in 2d's rung-level primary (AUC rising vs flat over
  the 34 rungs, family-block permutation, family-cluster bootstrap CI;
  2d's bars printed for comparison, not applied): the sampled rate read
  .5455, the floor-adjusted rate .6126. And the same on each
  trajectory: x_r(t_2) (the first point past the zero) against
  rising-vs-flat at M's endpoint.
- **S3 — alignment as a function of scale** (the experiments.md
  prediction's first clause). Pythia 70m, 160m, 410m, 1b, 1.4b, 2.8b,
  6.9b, 12b at `main`, each against the three non-Pythia references,
  per rung: Spearman of a_r with log parameters; the largest single-
  step share of the total rise from 70m to 12b ("discontinuity" as a
  number, no rule); the global-bank reading (all 17,000 items as one
  bank, k = 10; the k-NN sets for the ladder committed) vs log
  parameters — Huh et al.'s curve on this battery.
- **S4 — the size-axis pre-clear fraction.** For the 11 rising rungs
  on the Pythia ladder, φ computed on the outcome-bearing sizes {410m,
  1b, 2.8b, 6.9b, 12b} (first-clear size from 2d's argmax records and
  2c's m4/m5 counts under 2d's floor; the 12b endpoint; 70m as t_1;
  the 23 flat rungs as trend). Coarse — six of the eleven clear first at
  2.8b with 1b as the only pre-clear point, arith_next clears at 1b or
  below and has no window — and descriptive.
- **S5 — site sensitivities.** The primary re-read with (a) the
  maximum over all site pairs (Huh's reading), (b) the single site per
  (M, r) with the largest endpoint excess, read along the trajectory,
  (c) the final layer only.
- **S6 — the question-end position** as the representation.
- **S7 — Huh et al.'s construction reproduced:** average-pooled
  tokens, every block, maximum over block pairs, k = 10; per rung and
  on the global bank.
- **S8 — the referents.** The twins' alignments per rung (the surface
  floor at init); Pythia 2.8b's real step 0 beside them; the
  references' mutual alignments (the ceiling); the within-family
  reading — Pythia 2.8b's trajectory against Pythia-12b, printed
  beside the cross-family one (Huh's convergence is across independent
  trainings; the within-family value is what shared data and order
  add).
- **S9 — linear CKA** at every site pair, attested from load time
  (§3.2); the primary re-read with CKA in place of k-NN on the
  endpoints and references only, where the activations exist.
- **S10 — item grain, descriptive.** The per-item pre-clear excess
  overlap (o_i at t⁻ minus the item's flat-pool expectation) against
  the committed per-item emission order (2g's count outcome) within
  rung × 2g's strata, 2g's statistic, `no_alpha_claim` — the link to
  the Prediction 2 line, where the probe forecast nothing at item grain
  and the sampled count did.
- **S11 — textures.** The excess trajectories per cell (non-
  monotonicity, the grid point of the largest single step and whether
  it coincides with t_clear); the transient rungs' trajectories; the
  flat pool's own trend shape per M in tokens; per-reference agreement
  and disagreement (does one lens lead the others?); the count's
  fraction of the bar at t⁻ per cell (how close to performing the rung
  already was at the pre-clear point — the skeptic's covariate,
  printed beside φ).
- **Sensitivities:** φ at θ-free form is the primary; the half-rise
  time at ½ replaced by ¼ and ¾ in S1; the "clears and stays" clear
  time (first grid point after which the rung clears at every later
  point) in place of first-clear; the family-matched trend (flat
  siblings from the same 2c family, where any exist) in place of the
  pooled flat trend; k = 5 and k = 20.

## 6. Licences, written in advance

Bounded to: this battery; the four trajectories named; the site family
and position pinned; rung grain; a known outcome (§2's caveat in every
sentence: "a preregistered reading on a known outcome").

- **LEADS:** the essay's convergence paragraph gains a first-person
  sentence — "on N tasks across four families' training runs, the
  agreement between a model's representation of a task's items and
  three unrelated released models' ran ahead of the general
  convergence trend before the task first performed, by a
  preregistered margin" — and the lens reading of Huh et al. is
  upgraded from a citation to a measurement at task grain in the
  scoreboard; `experiments.md` gains the section. Condition: LEADS on
  at least two of the four per-model readings (each at its own p < .05
  and T ≥ .25); otherwise the sentence names the trajectories on which
  it held.
- **PARTIAL:** the sentence reads "a measurable part of the task-
  specific agreement precedes performance, below the preregistered
  quarter"; the lens reading is supported in direction and bounded in
  size; the bar and T printed.
- **FOLLOWS:** the convergence paragraph is BOUNDED: Huh et al.'s
  result stands as a statement about global representation, and the
  essay must say that on this battery the task-specific part of the
  agreement arrived with performance, not before — the construction
  account's prediction, and the first place in the program where it is
  the one that held. The sentence "there would be no reason for
  independent constructions to agree" is struck or qualified: the
  agreement that follows performance is exactly what agreeing on the
  answer produces. `experiments.md` records it as such.
- **UNDETERMINED:** the blind region is the CI95 of T; nothing about
  precedence is licensed; the essay's paragraph gains only the
  disclosure that the test ran and where it stopped.
- **NO-CONVERGENCE:** task-specific agreement above the flat pool is
  not measurable at the endpoint on fewer than three cells: the lens
  claim's premise — that resolving a task makes independent lenses
  agree about *its* items — does not show at this resolution; the
  paragraph is bounded to the global claim, with the endpoint excess
  table as the record. S3's global-bank curve is reported either way.
- Any world: S1–S11 in full; the per-model and per-type readings; the
  twins, the ceiling, the within-family reading; S2's numbers beside
  2d's and 2e's; the known-outcome caveat verbatim.

## 7. Run plan and model contact

Design (this doc + rulings) → build (`experiments/exp4/`: the metric
module with its fixtures and calibration curve; the collector (2f's,
generalised to the four families' loaders and renders, plus the pooled
variant); the reference stage; the sweep runner over the four
manifests with per-unit digest pins, gate 1 per trajectory, halt
markers, resume-by-record; the analyzer with the tree, the excess, the
sign-flip null, the cluster bootstrap, S1–S11 and the sensitivities;
power; referents; worlds for every terminal and every cell; totality;
mutation; the read sweep; the import scan) → adversarial freeze → tag
`exp4-preregistered` → **preflight on Michael's word** (dial k): ONE
cached trajectory model at `main` (Pythia 2.8b, weights already in the
cache) through the collector on two rungs' 500 items, hidden states
at the site family, the k-NN kernel run on the result, nothing under
`experiments/exp4/results/`, the run asserting so afterwards —
a memory, dtype and TIMING check (the per-checkpoint estimates below
are extrapolated from 2f's 4,064 forward passes in 75 s at ≤ 1b and
have never been measured at 7B on this stack); and one interior
checkpoint of the most expensive family (Comma, step 10,000: the
revision 2n's preflight already staged) through the candidate-file
loader end to end and freed, its tensor digest compared to the
committed 2n record as a rehearsal of the per-unit pin (2i stop #1:
the loader is rehearsed before the tag binds) → **stage 1
(references and endpoints)**: the four references at `main`; the
Pythia ladder at `main` (70m, 160m, 1.4b downloaded — ≈ 3.5 GB in all;
the rest cached; 12b doubles as the reference); the three seeded twins
and Pythia's step 0; the four outcome endpoints through
the thin loaders (Comma 460k, SmolLM3 3,440,000, OLMo-2 7B 928646;
Pythia 2.8b's is its step143000 grid point through 2g's loader —
2g's manifest records that branch's files as a DIFFERENT signature
from `main`'s, and 2g's gate 1 found the two byte-identical in their
continuations, so the ladder's 2.8b `main` (2c's pinned revision) is
loaded separately and its activations are required identical to
step143000's as a known-answer check) — 19 loads, forward-only,
≈ 6–8 h; the
endpoint excess and SE tables; eligibility; gate 0; power ONCE;
committed and tagged **`exp4-reference-sealed`** (binds every stage-1
record, the set tables, the activation shas, the power record) →
**projection sealed** by rung type and by trajectory, tolerances both
directions on every disconfirmer (2m's note 1), the attenuation or
lead prior stated as a claim with its own disconfirmer (note 2), every
licence cell of §3.9 named and one called (2n's note 1), the endpoint
excess table quoted → **stage 2 (the sweep)**, one trajectory at a
time, gate 1 first in each: Pythia 2.8b (21 points + step 0, ≈ 25 min
each ≈ 9 h — cheapest, first), SmolLM3-3B (26 points, ≈ 25 min ≈ 11 h),
Comma (24 points, ≈ 45 min ≈ 18 h), OLMo-2 7B (21 points, ≈ 45 min ≈
16 h) — ≈ 54 h of model time, ≈ 1.1 TB streamed one checkpoint at a
time and deleted (Pythia 2.8b ≈ 5.3 GB per revision; SmolLM3 ≈ 6.2 GB;
Comma and OLMo-2 7B ≈ 14 GB; Comma's measured download 128 s per
revision on 2n's record), the watcher committing every record,
processes via `Popen(start_new_session=True)` with one disposable
tracked poller (2m kill #1) → analyzer once, detached, on Michael's
word → `exp4-closed`. One pre-committed change.

Per-point cost, estimated: 17,000 prompts × one forward pass with
hidden states at fp16, batch 16 at 7B (dial l), ≈ 8 prompts/s at 7B
(≈ 35 min), ≈ 18/s at 3B (≈ 16 min); the k-NN kernel over 442 cells
per position (seconds) and the global bank (≈ 1–2 min); load 2–4 min;
download ≈ 2 min. The preflight replaces these estimates with
measurements before the sweep is budgeted.

Compute: the Mac for every stage. Memory: the 12b reference at fp16 is
≈ 24 GB plus hidden states for a batch — the mlx text servers come
down for that one load and go back up (dial j); 7B at 14 GB ran with
them up on 2i/2n. Disk: peak ≈ 14 GB (one checkpoint) + ≈ 80 GB kept
activations + the ordinary HF cache (the four references ≈ 60 GB with
12b); 224 GB free at design time.

## 8. Alternatives considered

**The primary at item grain** (per-item pre-clear overlap forecasting
the committed emission order in 2g's strata): the program's standard
construction, but the lens claim is about a *capability's*
representations, per-item k-NN overlap is a ten-valued score with SD
≈ .1, and 2g's answer at item grain (the probe forecasts nothing; the
count does) is not what this experiment asks — kept as S10. **The
order test as primary** (S1): both accounts predict it; it cannot
separate them. **The size axis as primary** (S3/S4): the outcome grid
has five sizes, seven of eleven rising rungs clear at the same one,
and there is no flat-pool trend to speak of across sizes — kept as the
descriptive the experiments.md clause asked for. **The naive
precedence test** (alignment at t⁻ above its t_1 value): vacuous
against a monotone trend (§1). **The twin as the zero**: a measured
surface floor, not zero (§2). **Huh's construction as the primary**:
the maximum over layer pairs is a selection with a chance level that
rises with the number of pairs, and average pooling dilutes the
answer-emission position with the two shots' tokens — reproduced as
S7. **CKA as the primary**: not re-derivable without keeping ≈ 300 GB
of activations; kept attested (S9). **Committing every set table
(≈ 900 MB)**: the primary's position only (≈ 300 MB), the rest
attested — dial g. **The two Pythia and OLMo grids not read** (6.9b at
23 × 13 GB ≈ 19 h; 13B at 16 × 55 GB — 2l's kernel panics): each adds
cells to rungs already present; dial a keeps them as an extension on
Michael's word. **A sealed outcome** — Pythia 1.4b's never-queried
trajectory swept for argmax and alignment in one pass (≈ 6 h, ≈ 3 GB
per revision): 1.4b would clear one to four rungs, too thin for this
primary; its item-grain outcome is a separate, cheap Prediction-2
successor (the smallest step above the 1b predictor) and is not
bundled here — dial m. **Within-family references**: not independent
trainings; printed (S8).

## 9. What Experiment 4 does not claim

Not Huh et al.'s global result (S3/S7 report it on this battery,
descriptively). Not a forecast: the outcome is known (§2). Not item
grain (S10 descriptive). Not "the same representation": mutual k-NN at
k = 10 reads agreement about neighbourhoods, nothing finer. Not a
mechanism. Not a statement about the flat rungs (their alignment is
the trend referent; that they never clear on a model is the committed
outcome, not a claim about their structure). Not cross-modal. Not a
statement about scale beyond S3's descriptives and S4's coarse
reading. Not about any family, position, site family or metric other
than those pinned. Not "from below" in any sense: the references are
released models larger than most trajectory points.

## 10. Dials — RULED by Michael 2026-09-10 ("go"): every dial as recommended

- **a. Trajectories:** the four cross-family-scored grids — Pythia
  2.8b (2g), OLMo-2 7B (2i), SmolLM3-3B (2m), Comma v0.1-1T (2n) —
  **recommended** (four families, 92 committed points, 50 cells, ≈
  54 h); vs the three non-Pythia only (≈ 45 h; drops the Pile family's
  own trajectory); vs adding Pythia 6.9b (2h; + ≈ 19 h) and OLMo-2 13B
  (2l; + ≈ 30 h and the 55 GB revisions) — available on his word as an
  extension, not in the primary's power model.
- **b. References:** the four released models, three per trajectory,
  with Pythia-12b `main` as the Pile lens, **recommended**; vs
  Pythia-6.9b (13 GB, servers stay up; a weaker lens on a battery it
  clears eight rungs of at its endpoint (2h), against 12b's nine (2d)).
- **c. Representation:** 2c's prompt-end position, the site family
  depth-matched and averaged, **recommended**; the question-end
  position (S6) and Huh's pooled construction (S7) as sensitivities;
  vs Huh's construction as the primary (§8).
- **d. Metric:** mutual k-NN, k = 10, cosine, ties by index,
  **recommended** (Huh's default; re-derivable from committed sets);
  vs CKA (attested only).
- **e. Primary statistic and bars:** T = mean pre-clear fraction φ
  over eligible cells; rung-level exact sign-flip null; p < .01 and
  T ≥ .25 for LEADS; PARTIAL / FOLLOWS / UNDETERMINED as §3.9,
  **recommended**; vs a bar at .50 ("most of the agreement precedes
  performance" — the stronger lens reading; power will say whether it
  is reachable) — the power record prints P(LEADS) at both bars
  whichever is ruled.
- **f. Eligibility:** endpoint excess ≥ 2 × its item-bootstrap SE;
  pre-clear window t_clear ≥ t_3, **recommended**; vs 1 SE (more
  cells, noisier φ).
- **g. What is committed:** the prompt-end k-NN set tables for every
  load (≈ 300 MB over the sweep), per-item overlaps, all scalars;
  question-end and pooled tables sha-attested; trajectory activations
  deleted after use, **recommended**; vs every table committed
  (≈ 900 MB) vs digests only (the primary then attested, not
  re-derivable — not recommended).
- **h. The flat pool:** rungs that clear at no grid point of M;
  transient rungs excluded from both sets and printed,
  **recommended**; vs "not in R_M" (would put transient rungs in the
  trend).
- **i. Power alternative:** φ = .5 at the bar, φ = .25 and the null
  printed; N_SIM 1,000; the logistic-rise simulation with the trend
  interpolated log-linearly in tokens, **recommended**.
- **j. The mlx servers** come down for the Pythia-12b reference load
  only and go back up; every other load at ≤ 14 GB runs with them up
  (2i/2n's shape), **recommended**; vs down for the campaign (2l).
- **k. Preflight on his word:** Pythia 2.8b `main` on two rungs
  through the collector (timing, memory, dtype), plus Comma step
  10,000 through the candidate-file loader and the digest pin, nothing
  stored, **recommended**.
- **l. Batch:** 16 at 7B, 32 at ≤ 3B (2f's), **recommended**; the
  preflight may lower it.
- **m. The sealed 1.4b arm:** NOT bundled, **recommended** (§8); a
  separate successor on his word.
- **n. S2 — the third instrument on 2d's question:** printed with 2d's
  bars beside it, no α claim, **recommended**; vs preregistering it as
  a second test (a second α-claim on a known outcome, the 2e caveat
  again — not recommended).
- **o. S3/S4 — the scale axis:** the eight-size Pythia ladder at
  `main` (three small downloads) with the descriptives as written,
  **recommended**; vs omitting the scale axis (saves ≈ 2 h; leaves
  experiments.md's first clause unread).
- **p. Grid order in the sweep:** Pythia 2.8b → SmolLM3 → Comma →
  OLMo-2 7B (cheapest first; the two 7B families last),
  **recommended**; vs Comma first (the richest R_M).
- **q. Projection:** sealed after the reference stage, by rung type
  and by trajectory, tolerances both directions, the lead prior as a
  claim with its own disconfirmer, every §3.9 cell named and one
  called, the endpoint excess table quoted, **recommended**.
- **r. The CKA and pooled variants** computed at load time and
  attested (S7, S9), **recommended**; vs dropped (saves ≈ 20 % of the
  per-point compute and the pooled storage).
- **s. Build + freeze in one session** by SDD, the import pin from
  commit one; licences as §6, **recommended**.

## 11. Process

Design → rulings → build → freeze → tag → preflight on his word →
reference stage → seal tag → projection → sweep (detached via Popen,
watcher, one poller; four trajectories in the ruled order, gate 1
first in each) → analyzer once, detached, on his word → `exp4-closed`
→ close-out propagation (essay under §6, `experiments.md`, the graft
with the three tags, Zenodo, paper inventory).
