# Experiment 7 — Does the sampled forecast follow the target when the answer changes?

**Status: proposed design, 2026-10-04.** Michael requested the matched-token
analysis and a plan for the sampling-mechanism experiment. This document is
the latter. The dials in §10 await his ruling. No generator has been built,
no new item has been handed to a model, and no rental is authorized.
The parallel descriptive analysis is `analyses/matched-token/PLAN.md`.

## 1. The question and the distinction this experiment can make

The item-order forecast now transfers across two batteries and four outcome
families. Its unresolved interpretation is what the small model's sampled
success is measuring. Experiment 2j already found that answer length and
wrong-target answer propensity absorb part of the forecast, with a residual
remaining. Experiment 6's wrong-target prior also forecasts item order.
Another set of correlations with hand-chosen covariates would leave that
same interpretation open.

**When a controlled change to the question changes the correct answer from
`a` to `b`, does the smaller model's output shift toward the newly correct
answer, and does the strength of that target-sensitive shift predict which
question pairs a larger model learns to answer correctly?**

Each unit is a counterfactual pair of valid tasks with two different correct
answers. Both answer strings are scored under both prompts. Compare their
**conditional proportions within each prompt**, so fixed odds of saying `a`
rather than `b` cancel even if the total probability of emitting either
target changes. Meaning-preserving variants check sensitivity to rendering.

The result can distinguish **prompt-invariant conditional target odds** from
**input-sensitive, correctly directed output structure** that transfers to
a later model. It cannot distinguish every form of general item difficulty
from partial competence. Nor can it establish that an internal algorithm
already existed, that representations were merely sharpened, or that no new
computation was learned. Those stronger accounts can predict the same
target-sensitive behavior. The experiment's name and licences must keep
that boundary; "the mechanism is resolution" is not an available verdict.

## 2. What the design knows

All results through Experiment 6 are known. Relevant predecessors:

- Exp 2j: the four-functionals residual was T=.1311; the wrong-target answer
  prior itself forecast strongly, especially on arithmetic. Its residual
  did not identify what information survived.
- Exp 6: all eight primary forecasts fired; sampled counts also survived
  the extra-structure and heuristic-clearing descriptives. Wrong-target
  prior T was .1247/.1263/.1248/.0977 across the four outcomes.
- Single-checkpoint greedy performance can reverse during training. An
  outcome that counts paired successes over a grid is preferable to assuming
  every item has a permanent first-acquisition time.

The separate matched-token analysis uses known old-battery outcomes. Its
results were not computed when this first design was written; any later
change motivated by them must be disclosed as such.

Unknown: every model output on the proposed new pairs, their target-sensitive
sampled scores, and the outcome trajectory on those pairs. Choosing task
families with demonstrated liveness is informed by the old record. This is
a new-item forecast within known task families, not blind task selection.

Relevant outside context, verified against the arXiv abstracts on Oct 4:
[Zhao et al., *Calibrate Before Use*](https://arxiv.org/abs/2102.09690) describe
answer and prompt-position biases and content-free calibration;
[Holtzman et al., *Surface Form Competition*](https://arxiv.org/abs/2104.08315)
describe competition among answer strings and a task-context prior correction.
They motivate treating answer propensity as a serious alternative; neither
abstract establishes the proposed cross-model counterfactual forecast.
The cancellation used here is derived directly in §4.

Frozen predecessor files are references, not files to edit. New generators,
scorers and records belong to `experiments/exp7/`.

## 3. Battery: four families, paired answers, sham changes

**Recommended:** 500 independent base pairs in each of four families,
2,000 pairs total. Each pair has two counterfactual prompts, q0 and q1,
with distinct normalized answers a0 and a1, plus one meaning-preserving
variant of each prompt, q0s and q1s. That is **8,000 prompts**.

Pair construction is deterministic from committed seeds and independent of
any model output. Each pair stays together in every split, bootstrap and
permutation. Do not count four renderings as four independent items.

| Family | Counterfactual change | Invariants and sham |
|---|---|---|
| Word unscrambling | Replace the scrambled letters with those of a different, matched word | Same answer length and source-frequency tercile; same repetition-pattern class where the source supports 500 disjoint pairs. Two unique dictionary solutions. Sham: a different nonidentity scrambling of the same word. |
| Five-object deduction | Ask for the opposite endpoint of the same uniquely ordered set | Same objects, relational clues and option list in exactly the same order. No clue directly states an endpoint. Sham: reorder the clues without changing their content. |
| Unit interpretation | Exchange the numerical assignments to two distinct dimensional roles, changing the correct numerical result | Same quantities as a multiset, same role vocabulary, same query unit and same five numeric options. All candidate values distinct. Sham: reorder the quantity statements. |
| Shape recognition | Change a generated path to a different shape in the same fixed complexity bin | Same answer-option list and order; paired answer names matched by length bin. Oracle labels both paths. Sham: translate and cyclically re-index the vertices without changing the shape. |

These are **proposals to be certified by generation-only feasibility work**,
not claims that the current frozen generators already implement them.
The build must demonstrate 500 disjoint valid pairs per family before a
preregistration tag. If any rule cannot supply that support, stop for a
design ruling before model contact; do not silently relax it.

### Admission and shortcut audit

- Exactly one answer under an independent oracle for each question. q0/q1
  must differ in answer; the shams must preserve their own answer.
  Unscrambling uniqueness is relative to the committed lexicon. Unit-role
  swaps must change the oracle result; swapping interchangeable operands of
  a commutative operation is not a counterfactual. Shape re-indexing must
  operate on a closed-path representation whose geometry is preserved.
- Neither pair member or sham may duplicate an old evaluation question or
  another pair's question. Word content can have appeared before; a fresh
  scrambling is not evidence of unseen vocabulary. State that limitation.
- Counterbalance which target is a0, the option positions and render order
  by seeded assignment. Never sort the pair by the smaller model's output.
- Option order is identical throughout a pair. Fixed-position and fixed-word
  responders therefore cannot answer both counterfactuals correctly.
- Fix the model-free baseline list before generated-item inspection: constant
  answer; option position; answer length/frequency; input-copy; option absent
  from the question; query-word-only and clue-degree/endpoint rules;
  dimensional-role-blind numeric rules; path segment-count/bounding-box rules.
  Audit each per family and
  commit its paired success/selectivity. Do not discard items merely because
  a baseline succeeds; fix actual generator/definition defects before freeze.
- Shapes with a direct segment-count solution are a foreseeable weak control.
  The complexity bin must compare distinct labels at equal segment count
  where possible. If the retained classes cannot meet this, remove or replace
  that family by an explicit pre-contact ruling, not a post-result sensitivity.
- Shape labels must form a mutually exclusive oracle partition. If common
  names overlap (a square is also a rectangle), the shared prompt must state
  the fixed most-specific-label convention and the oracle must enforce it.
  Do not count an otherwise valid geometric name as an arbitrary model error.
- The feasibility certificate must demonstrate usable stratum support as
  well as 500 valid pairs; hundreds of singleton nominal blocks do not make
  a usable forecast instrument.

A positive result measures input-sensitive target emission, which can include
an inexpensive task-specific shortcut. Passing this audit does not certify
an abstract reasoning algorithm.

## 4. Predictor and the answer-prior cancellation

**Predictors:** Pythia-1B and OLMo-2 1B stage-1 endpoint, using their frozen
tokenizer/render/load pins and the existing seeded, T=1.0, untruncated fp32
sampler. **k=64 draws per prompt for both predictors**, an equal measurement
budget. Use a new committed seed namespace with distinct streams across
pair members and shams; no accidental shared-seed coupling.

Both predictors are smaller than the outcome in parameter count. Their
training exposure is not matched to each outcome checkpoint. This is not
an independent causal manipulation of model size or of training tokens.

For one pair and one render v (canonical or sham), form the target-coded
2×2 count table from its two sets of k independent draws:

| | Emits a0 | Emits a1 |
|---|---:|---:|
| q0v, correct a0 | n00 | n01 |
| q1v, correct a1 | n10 | n11 |

Other outputs contribute to neither column. Let m0=n00+n01 and m1=n10+n11.
The **within-render conditional target shift** is

`x_iv = n00/m0 - n10/m1` if both m0 and m1 are positive, otherwise **0**.

The **primary predictor** is `x_i = (x_i,canonical + x_i,sham)/2`, bounded
in [-1,1]. Always average the two render-level contrasts; never pool their
tables first. A render with an empty target row contributes zero and is
counted as unsupported, not silently removed from the family mean. Report
supported-only means as descriptives beside this support-penalized score.

At population level, x_iv is the difference between the conditional
probabilities of a0 given that one of the two targets was emitted. It is
zero if the a0:a1 odds are equal under q0v and q1v, regardless of their total
target availability. The prior can differ between pairs and between the
canonical/sham renders. Conditional on the two row totals and the a0 column
total K=n00+n10, the null gives

`n00 ~ Hypergeometric(population=m0+m1, a0_count=K, draws=m0)`.

Each row's expected a0 proportion is K/(m0+m1), so E[x_iv]=0. Empty rows
give the defined zero. This supplies the selectivity randomization in §5.
It assumes independent sampled draws conditional on each fixed prompt and
independent render streams, not arbitrary dependence with equal marginals.

**Why the first draft changed, before data:** probabilities (.18,.02) under
q0 and (.09,.01) under q1 preserve odds 9:1, but produce raw contrast .04.
The earlier pooled conditional score was also nonzero. The revised x is
.9−.9=0. This becomes a mandatory calibration fixture. Prompt-dependent
lexical compatibility, copying and heuristics that change the target odds
remain live explanations, not cancelled nuisance variables.

Retain the following diagnostics. Across all four prompts C counts that
prompt's correct target and W the other target; normalized a0≠a1 ensures
disjoint matches. Raw absolute shift `d_i=(C-W)/(4k)`, total availability
`u_i=(C+W)/(4k)`, raw rate C/(4k), and wrong-target rate W/(4k) are printed.
Check `C/(4k)=(u_i+d_i)/2` exactly. This raw identity is not a decomposition
of x. Print all four target-row totals, C/W, unsupported renders, ties and
both conditional and raw shifts by family and predictor in every world.
There are no pseudocounts or data-dependent denominator cutoffs.

**Primary volume:** 8,000 prompts × 64 draws × 2 predictors = **1,024,000 draws**.
An untrained Pythia-1B twin supplies **16 draws on all 8,000 prompts**, another
128,000 draws, as a non-gating surface control. Total planned new-item sampling
is **1,152,000 draws**, plus the separately counted preflight/anchor work.
The twin has its own seed namespace and tagged config/initialization seed.
Token caps are fixed by answer type before sampling and validated for all
oracle answers using tokenizer-only reads at build. Both targets are scored
with the same total normalization function. No answer-likelihood substitution
after observing thin sampling.

## 5. Sealed outcome and comparisons

**Recommended first outcome:** SmolLM3-3B's existing 26-point stage-1 grid,
with its existing candidate-weight manifest, BOS/stop rules, dtype and host
checks. Both predictors cross families to this outcome. Same family as a
past experiment does not make the new items known: all new outcomes remain
unqueried until the predictor seal.

For pair i at checkpoint t, canonical paired success is

`z_it = 1[greedy(q0)=a0 AND greedy(q1)=a1]`.

The primary outcome is `y_i = sum_t z_it` over the 26 trained checkpoints.
A prompt-invariant fixed answer cannot pass both members of a pair. This
does not require success to persist at every later checkpoint. The sham
outcome uses q0s/q1s identically and is a named secondary. All four prompts
are collected at every checkpoint: **208,000 greedy continuations**.

### Stratification and eligibility

Base strata are fixed, model-free functions of pair construction:

- unscrambling: answer length × source-frequency tercile;
- deduction: query-to-clue-graph distance/shape class, with the two queried
  endpoint option positions treated as an unordered pair;
- unit interpretation: operation/dependency-depth class × output digit-length
  pair;
- shapes: path complexity bin × unordered shape-label pair.

The build must print block sizes before freeze. Ordinal adjacent levels with
fewer than 10 pairs are merged by a deterministic low-to-high rule; nominal
levels are not merged. The exact executable levels become tagged constants.
For each predictor, cross the base stratum with a **median availability u
bucket within that stratum**; ties at the median go together, and a constant
u contributes one bucket. This is a coarse control; residual variation within
buckets is disclosed. Print base-only and finer-availability sensitivities.

Use the existing within-stratum Somers' D: sum
`sign(x_i-x_j)*sign(y_i-y_j)` over unordered pair-of-pair comparisons within
the same stratum, divided by their number with y_i≠y_j. Outcome ties are
excluded from the denominator; predictor ties contribute zero numerator.
Pool numerator and denominator across strata within a family, then take
the equal-family mean T. This is the outcome-untied denominator implemented
by `experiments/exp2g/stats_2g.py`, not a symmetric Kendall coefficient.
A family
is eligible only if at least 20 distinct pairs ever succeed jointly and
there is an informative outcome pair within a stratum. A constant predictor
contributes D=0; it is printed, not dropped to improve the mean. Require at
least three eligible families; otherwise UNDETERMINED.
Print every excluded family and every uninformative block. Nothing selects
families by sign or significance.

### Two gates per predictor

1. **Input selectivity:** mean x_i, equal weight to each eligible family,
   at least **.05**, with one-sided conditional randomization p<**.005**.
   For each (pair, render), independently draw n00 from §4's hypergeometric
   null, preserving both target-row totals and the a0 column total, and
   reconstruct its other three cells. Recompute x from both render tables
   and then the same family means. Hold items, answer designations and
   outcome records fixed. Use 10,000 seeded randomizations and
   `(1+n_ge)/(1+B)`. The null permits prompt-dependent availability and
   pair/render-specific conditional answer odds; it forbids those odds from
   changing between q0v and q1v. Independence of the sampler streams is
   required for this product conditional null.
2. **Forecast:** T≥**.10**, within-family/stratum predictor permutation p<**.005**,
   10,000 permutations and the same finite-permutation correction. The null
   is conditional exchangeability within the declared strata, not the claim
   that every unmeasured aspect of item difficulty has been removed.

Both gates read the **same eligible family set** for that predictor. This
prevents a target shift confined to an excluded family from licensing a
forecast on different families. Eligibility depends on y and u, which are
unchanged by conditional target-label randomization; keeping constant x
families also makes eligibility invariant under that null. Report
all-four-family selectivity descriptively
beside the gate's reading, including in UNDETERMINED.

This is a **battery-level conjunction**, not a requirement that the same
family supplies both effects. Print each family's contribution to both
gates. Selectivity can be concentrated in one retained family and forecast
association in another; the headline cannot claim a shared family witness
unless its printed per-family results actually supply one.

Both gates must fire for a predictor to earn the input-sensitive forecast
licence. With valid component tests, this conjunction has size at most .005
under the union of its component nulls; allowing either of two predictors
to earn the licence is bounded by .01 via Bonferroni. No independence between
predictors is assumed. Effect bars do not increase that bound. This is not
a correction for every secondary or a universal causal identification result.

Bootstrap pair bundles within family (1,000 draws) for descriptive x, d, D,
paired predictor/competitor differences and canonical-versus-sham readings.
Only four fixed families exist: these intervals do not estimate uncertainty
over all task families or over independently trained networks.

## 6. Worlds and licences

Report the following state **separately for each predictor**, with all x, d,
T, p, intervals, eligible sets and power disclosures. Both models need not
land in the same state; do not replace their table with one pooled label.

| State | Rule | Licensed reading |
|---|---|---|
| INSUFFICIENT_DATA | Any input/provenance/collection gate fails | Instrument could not adjudicate. |
| UNDETERMINED | Fewer than three eligible families | Not enough informative families for the forecast rule. |
| INPUT-SENSITIVE-FORECAST | Both gates fire | On this battery, the conditional target-response score shifts in the correct direction on average and forecasts paired success in the named cross-family outcome. Fixed within-pair/render target odds with changing availability alone cannot supply its expected conditional shift. This is an aggregate conjunction; per-family witnesses are named separately. |
| SELECTIVE-ONLY | Selectivity fires, forecast does not | The small model responds in the correct direction, but transfer does not reach the forecast rule at the declared resolution. |
| ORDER-ONLY | Forecast fires, selectivity does not | A relative item ordering exists without the specified mean conditional target-shift evidence. No partial-competence mechanism licence. |
| NO-JOINT-SUPPORT | Neither gate fires | The proposed joint account is not supported at this resolution. No conclusion that outputs contain no task information. |

If both predictors earn the licence, name both; if one does, name that one.
An underpowered non-firing gate cannot be described as an absence. Under a
powered null reading for that particular gate, bound the absence to its
simulated alternative and the exact realized eligible set/support. There is
no unqualified joint POWERED label. A successful forecast still leaves shared
input-sensitive difficulty and learned heuristics as live explanations.

## 7. Calibration, power and refusal gates

**Before the tag, synthetic fixtures only:**

- Answer-only generators with highly unequal string priors, varying target
  availability, sparse/tied counts, and y correlated with availability and
  word length. These must not manufacture the joint licence.
- The fixed-9:1-odds/varying-availability counterexample of §4, including
  different canonical/sham priors. Check the conditional gate itself, not
  only whether a second gate masks an incorrect rejection.
- Correctly directed responses with conditionally exchangeable, nonpredictable
  outcomes, to isolate the forecast-null component of the joint claim.
- Correctly directed context responses, anti-directed responses, q0/q1 label
  swaps, unequal sample counts, missing sham arms and shared-stream mistakes.
- An adversarial shortcut that genuinely tracks the answer: the instrument
  should register input sensitivity and the report must not call it algorithm
  recovery. This verifies the stated limitation rather than hiding it.
- Full worlds, total scoring, record coverage, item/pair identity, import
  pins, write-once stages and all terminal refusal paths.

Measure each component-null rejection frequency against **.005**, and the
either-predictor joint-licence frequency against **.01**, with binomial
intervals. Include asymmetric cases where only one predictor/component has
a real effect. A conservative companion gate cannot certify the other.
Measure selectivity power at conditional shifts 0/.025/.05/.10/.20, with
availability spanning sparse
through dense. For the forecast use the predecessor's within-stratum power
construction, including effects D=.10/.15/.20, explicit shape assumptions and
null tests with difficulty-correlated availability. Do not assert calibrated
α merely because the permutation API was reused.

Before running that calibration, the build plan must freeze its replicate
count and acceptance rule. Recommended failure rule: reject calibration if
a component's null fire rate exceeds .005, or the either-predictor joint
rule exceeds .01, by a one-sided exact binomial test at .01. Check each
prespecified null generator separately and
print the intervals; this is a defect-detection rule, not proof of exact
calibration. Neither the acceptance rule nor the synthetic cases may be
selected after their rejection frequencies are seen.

**One predictor-conditioned power record** is written after predictor sealing
and before any outcome collection. It binds the actual strata/tie structure
and prints every three-family subset and the four-family set, so the final
realized set can be matched without assigning a wider-set power number to it.
The outcome-count simulations fix 20/50/125/250 ever-correct pairs per family,
with nonzero counts either spread over 1–26 or concentrated at 1–3. Add the
10-positive case as a required THIN refusal fixture. Simulate a conditional
rank signal using the existing power construction and print the realized
mean D; a target D unattainable under the sealed predictor's ties is an
underpowered/unsupported alternative, never silently replaced by a stronger
one. FORECAST-POWERED requires ≥.75 at D=.15 in the worst arm of this declared grid
for the exact eligible subset. This is conditional power on that finite
grid, not a prediction that the outcome will supply those positive counts.
The separate **selectivity-power envelope** uses valid three-category prompt
probability tables (a0/a1/other): probabilities nonnegative and summing to
one, conditional proportions within [0,1], raw |d|≤u. Unsupported rows use
the actual zero convention. Impossible combinations of availability and
effect are marked unsupported, not simulated by clipping. Report power of
the finite-k, support-penalized mean x, not merely its population conditional
contrast. There is no claim that FORECAST-POWERED powers this gate or their
conjunction. The one-time verdict computes the actual selectivity gate,
not the power writer.

At verdict time, print realized ever-correct counts, informative blocks and
target-row support beside the frozen grids. Matching the family subset is
not matching this distribution. Flag out-of-envelope support and do not
borrow a power number or rerun power after the outcome is known.

The design does not yet claim a power number. Gate/threshold failures in
calibration return to Michael before freeze. At the sealed-predictor stage,
an underpowered declaration is printed and paused for a run/stop ruling;
there is no automatic draw deepening or family replacement.

**Data gates:** independent generation oracles; exact four-arm × k coverage;
normalizer totality and a0≠a1; reproduction of existing sampled-stream anchors;
complete/provenance-valid untrained-twin and model-free controls (their
numerical performance is non-gating); prediction seal before first outcome
item contact; per-host endpoint two-loader identity and baseline tolerances;
weight/config/tokenizer/host provenance; complete 26-point outcome windows;
all imported sources and all read inputs pinned at entry and exit. Every
failure is a recorded INSUFFICIENT_DATA terminal. The analyzer runs once.

## 8. Named secondaries, all printed

1. Raw-rate, availability and wrong-target forecasts beside the conditional
   target score, with paired differences. Availability winning is a substantive
   result; the raw-rate identity prevents independent-mechanism overcounting.
2. Canonical versus sham selectivity/forecast, and paired-success agreement.
3. Each family separately, with its contribution to both gates; all-rung
   versus eligible-set coverage, target-row support and ties.
4. Base-only, median-availability and tercile-availability partitions, with
   realized block support and dropped pairs printed. No choosing the best.
5. Equal 16/32/64 nested draw budgets, and disjoint 32-draw halves to reveal
   sampling stability. No new samples are added in response to those results.
6. Individual-member success, joint success and first joint success, with
   observed later losses. The primary is joint-success count over the grid.
7. Model-free baseline readings through the same outcome comparison and the
   untrained predictor's target shift. A baseline explaining a family is
   reported in the headline's limitations.
8. Exact per-pair output-label reversal check: swapping target designation
   reverses d and x, preserves u and never changes a stored generated string.

## 9. Run plan, resources and alternatives

1. Rule §10, generation-only feasibility, then a committed build plan.
2. New package built task by task with fresh implementers/reviewers; synthetic
   calibration, adversarial freeze, final review, ratification and tag.
3. Commit the projection, with hypotheses and numerical tolerances, before
   the first predictor preflight/model contact. Then predictor preflight and
   collection on the Mac; frozen two-stream anchors,
   new pair streams and the twin control, then predictor seal and the one
   power record. Restore
   local services after heavy collection. No outcome prompts before the seal.
4. On separately authorized rental, the outcome preflight/gates and 26-point
   SmolLM3 sweep. Detached operator, complete-unit publication and durable
   watchdog registration before leaving it unattended. Release after verified
   evidence is secured under Michael's standing release authorization.
5. One analyzer invocation on his word, retrospective, and separately approved
   propagation to the essay/public record if warranted.

Tag names proposed: `exp7-preregistered` binds the design/instrument/items;
`exp7-predictor-sealed` binds the raw predictor/twin streams and measured
provenance; a separate committed, hashed power record precedes outcome contact;
`exp7-closed` binds the one verdict and its inputs. The sampler seal cannot
be rewritten to incorporate a power result computed afterward.

**Planning envelope, not a measured quote:** about 1.15 million new-item draws
suggests roughly 9–23 hours on the Mac from Exp 6's aggregate throughput;
longer deduction prompts can exceed that extrapolation. Time complete units
of every family during preflight. 208,000 outcome prompts and 26 3B loads
suggest an A100 campaign of roughly 4–10 hours, plus setup/gates and download
time: budget **$10–20**, with an explicit **$25 proposal cap**. The provider
quote and measured preflight must replace these estimates before commitment.
Request disk from the measured cache peak; do not inherit a larger campaign's
disk allocation without sizing it. No money is authorized by this document.

**Alternatives considered:**

- Recompute 2j's covariates on Exp 6: inexpensive but does not intervene on
  which answer is correct; useful supplementary work, weaker discrimination.
- Exact answer likelihood instead of sampling: cheaper and avoids missed
  targets, but changes the instrument and inherits normalization/tokenization
  choices. Keep it as a separately ruled instrument, not an escape hatch.
- One predictor: halves trained-predictor sampling (640,000 total new-item
  draws if the 128,000-draw twin is retained); loses the question of whether
  the target-sensitive component transfers for both known forecasters.
- Comma as a second outcome: valuable corpus contrast, approximately another
  24 checkpoints and 192,000 prompts. Defer until the first instrument is
  calibrated; no automatic successor collection is authorized.
- Training-data interventions or controlled training from scratch: closer
  to distinguishing learning mechanisms, substantially different cost and
  external validity. Required eventually for a causal construction-versus-
  resolution claim; this experiment does not substitute for that evidence.

## 10. Dials for Michael — recommendations

1. **Scope/name:** Experiment 7, a target-sensitive forecast test. Keep its
   claim narrower than resolving the learning-mechanism question.
2. **Battery:** four families × 500 counterfactual pairs × four prompts;
   generation feasibility is a pre-contact gate, with explicit reruling
   if a family cannot supply the promised support.
3. **Predictors:** both existing 1B families, equal k=64; untrained Pythia
   control at k=16. No adaptive deepening.
4. **Score:** average within-prompt conditional target contrast x; empty
   target rows contribute zero. Conditional target-label randomization;
   raw shift d and availability u retained as diagnostics.
5. **Outcome:** SmolLM3-3B, the full existing 26-checkpoint grid; canonical
   joint-success count primary, sham reading secondary.
6. **Controls:** pair matching, unchanged option order, fixed heuristic audit,
   availability conditioning, pair-bundle resampling; accept that unmeasured
   input-sensitive difficulty is not identified away.
7. **Bars:** mean conditional selectivity ≥.05 and forecast T≥.10, each
   p<.005 for each predictor;
   require both for the licence. At least three eligible families.
8. **Power:** synthetic calibration first; sealed-predictor power across every
   possible eligible set; pause for a decision if declared underpowered.
9. **Resources:** local predictors, rented outcome only after separate create
   approval; planning cap proposal $25, subject to preflight and provider price.
10. **Process:** full build/review/freeze/ratification; one verdict invocation;
    no new model contact or essay propagation on design approval alone.
