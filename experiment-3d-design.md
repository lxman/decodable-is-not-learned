# Experiment 3d — Design Doc: Rank Prediction — Is the Sampled Channel Forecastable at Item Grain?

**Status: DRAFT — session 1 (design) of the three-session design |
build | freeze protocol** (boundary = context clear; Michael's pacing
ruling 2026-08-15, carried forward). Dials pinned by Michael
2026-08-18 in the design dialogue: (1) primary predictor = a frozen
structural functional of the answer string; teacher-forced log-prob
as the named quantitative secondary; the per-item probe-margin arm
DEFERRED to a possible 3e — the committed record cannot support it
offline (probe records are aggregate-only per (rung, size, seed);
the item files split probe_items 2000 / eval_items 500 disjointly by
2b's two-stage lock, so no probe-signal × fire-count join exists
without new activations). (2) Outcome tranche = reverse_string/1b ×
24 new seeds + reverse_string/410m × 12 new seeds; rev_string7
EXCLUDED, its standing pooled bounds untouched. (3) Primary
statistic = within-length-stratum exact permutation rank test on the
new-fired item set; 1b adjudicates, 410m replicates non-gating.
(4) Contact order = the teacher-forced scoring pass runs BEFORE any
new sampling, committed and sha-pinned. (5) Functional selection =
disclosed in-sample on the 13 committed fires; confirmatory
inference exclusively on new draws. The assembled design was
approved the same day. The build is a later session; the freeze is a
third session that opens adversarially (cold re-read; assignment:
find the class defect; fuzz the verify criterion for totality per
the standing stop-#1 rule; attack the functional's degrees of
freedom) and ends at tag `exp3d-preregistered`. The instrument will
be `experiments/exp3d/`.

**Predecessor:** `experiment-3c-design.md` (tags
`exp3c-preregistered`, `exp3c-closed` — **DEEPENS**: the fired cell
fired again, 9/384,000 new, pooled 10/512,000 = 1.953e-5; the
reverse_string/410m wall fell, 3/384,000, all len-4 at 9.2× the
2.19e-6 luck floor; rev_string7 silent, pooled CP95 ≤ 5.85e-6). 3c's
retrospective pre-named this experiment twice: "any rate model
should condition on answer entropy/compressibility, not raw length"
(the len-6 'rxxxxd' projection miss) and "per-item rate structure is
measurable at feasible k for the easiest items" (item 123 'ecde' =
4 of the 12 new fires, at BOTH sizes). The forward-note asymmetry
rule (binding since Exp 1) is inherited throughout: a fire is strong
evidence; silence is weak evidence bounded by budget.

---

## 1. The question

3c established that the sampled channel is item-heterogeneous: 13
committed fires across exp3+3c land on 9 distinct items out of 500,
with one item ('ecde') carrying 4 fires across two model sizes, and
the single len-6 fire landing on exactly the len-6 answer with the
cheapest internal structure ('rxxxxd', a 4-run). Heterogeneity
observed after the fact is texture. This experiment asks whether it
is FORECASTABLE: **can a frozen, model-free structural functional of
the answer string predict WHICH items fire in draws that do not yet
exist?**

This is signature 3 — forecastable from below — at item grain, and
the doc says so explicitly. The functional is a "from below"
instrument in the strictest sense: it needs no weights, no forward
pass, no samples — it is computable from the item file alone. The
teacher-forced log-prob arm (§5.5) is the same claim one tier up:
the model's own cheap scores (one forward pass per item, no
sampling) as a quantitative rate forecaster. Both forecasts are
committed to the record BEFORE the outcome draws exist (§10's
order). If the fires land where the frozen ranking says, the sampled
channel's reach is not just structured — it is structured in a way a
cheaper instrument sees first, which is the resolution thesis at the
finest grain the program has tested.

## 2. Why 3d will not die its predecessors' deaths

- **3a's death (valueless verdict input):** every verdict input is
  either a committed referent re-derived at analysis time or a
  quantity the analyzer computes from pinned bytes. The functional's
  500 per-item values, the strata assignment, m_min, and the exact
  null tables land IN THE TAG; the analyzer hash-checks its item
  file against the §4 pins (3c finding-A closure, inherited).
- **2c's tie collapse (22 rungs tied at zero → 7 effective blocks):**
  zero-inflation is THE named statistical hazard here — ~490 of 500
  items will have zero new fires. The primary statistic therefore
  lives on the RANKS OF THE FIRED SET, never on per-item counts fed
  to a correlation; the permutation null fixes per-stratum fired
  counts and honors the functional's tie structure by construction.
  The frozen functional's tie structure over the 500 committed
  answers is PRINTED AT FREEZE (checklist item), so the effective
  resolution of the test is known before any data.
- **Selection circularity:** the 13 committed fires are used to
  SELECT the functional, and this is disclosed as in-sample
  motivation (§5.1), the same committed-past / new-outcome split 3c
  used for its rate claims. Overfitting the 13 costs power, never
  validity: the confirmatory statistic sees only new draws.
- **3c finding B (attested-but-uncompared shas):** every committed
  tree the analyzer pools is hash-compared, not merely attested
  (inherited `check_gate1_committed_shas` pattern).
- **The Schaeffer trap (metric cliffs):** the outcome event is the
  same verified full-string fire 3/3c used — no new metric, no new
  threshold; 3d adds only a PREDICTION about where the
  already-frozen event lands.

## 3. The matrix

Two cells, both previously fired, both with committed rate
estimates:

| cell | committed base (16 seeds, 512k draws) | new seeds | new draws |
|---|---|---|---|
| reverse_string/1b/trained | 10 fires / 7 items; pooled 1.953e-5, new-draw 2.34e-5 | 16–39 (24) | 768,000 |
| reverse_string/410m/trained | 3 fires / 3 items; pooled 5.86e-6 | 16–27 (12) | 384,000 |

- 64 draws per item per seed; 500 items; 32,000 draws per seed per
  cell; 1,152,000 new draws total. T = 1.0, untruncated, fp16, the
  same sampler as exp3/3c (a further seed-extension of exp3's frozen
  sampler; module provenance asserted byte-identical at run time).
- Per-item new budget: 1,536 draws (1b), 768 draws (410m).
- Strata (answer length = input length): len-4 194 items, len-5 155,
  len-6 151. Luck floors 26^-L: 2.19e-6 / 8.42e-8 / 3.24e-9.
- **rev_string7 is excluded.** Rationale: pooled 0/512,000 at both
  sizes (CP95 ≤ 5.85e-6) supplies no rankable events at any feasible
  budget; including it buys no item-grain information and costs
  ~6 h. Its silence stands as bounded, per the asymmetry rule;
  nothing in 3d re-adjudicates it.
- Expected new fires at committed rates: ~15–18 at 1b (768k ×
  [1.953–2.344]e-5), ~2–3 at 410m. 3c's 9-fires→6-distinct-items
  conversion suggests roughly 8–12 distinct new-fired items at 1b.

**The committed fires (the complete in-sample set, verbatim):**
1b — item 123 'ecde' (seeds 5, 8, 13), item 200 'rxxxxd' (seed 8),
item 320 'wchw' (seed 15), item 370 'eyxh' (seed 11), item 391
'fkjes' (seed 8), item 447 'dmkd' (seed 13, twice), item 436 'xuvq'
(exp3, seed 0). 410m — item 123 'ecde' (seed 8), item 174 'kbjb'
(seed 15), item 226 'iviz' (seed 6). Note the texture the functional
must capture: 6 of the 9 distinct fired items carry a repeated
character; 3 do not ('eyxh', 'fkjes', 'xuvq') — the signal is real
but not clean, which is what the preregistered test is for.

## 4. Referents — every input, a committed value

To be pinned at build (sha256 list in the doc at freeze):
- The reverse_string item file (2b battery), its sha, and the
  identity of the 500 eval_items across both sizes (asserted).
- The 13 committed fire addresses (exp3 + 3c verdict records).
- 3c's per-seed fire tables and pooled rates (the base the new
  tranche pools with).
- The standing twin record: 0 fires / 576,000 committed twin draws
  (3c's re-assertion) — the contamination referent; NO new twin
  draws are taken.
- Gate-1 slice referent: 3c's committed reverse_string seed-8
  streams at BOTH sizes (32,000 draws each; seed 8 chosen because it
  carries fires at both sizes — re-deriving a fire-carrying stream
  is the strongest byte-identity check available).
- The verify criterion: 3c's ratified total wrapper
  (`load_verify_3c` semantics), inherited verbatim as the frozen
  criterion; its known crasher draw and the 10/10 referent battery
  come with it.
- ctrl_copy's committed T = 1.0 sampled verified rates from exp3's
  tree, both sizes, as the known-answer referent for the scoring arm
  (§5.5) — exact values entered in the pin list at build. NOT the
  greedy .9940, which is a different instrument's number.

## 5. Operationalization

### 5.1 The functional (predictor provenance — disclosed in-sample)

Candidates, each a total function of the answer string s (|s| = L),
cost ascending = predicted cheaper = predicted to fire:

- **C1 unigram bits:** L × H1(s), H1 = −Σ_c f_c log2 f_c over
  within-string character frequencies.
- **C2 distinct ratio:** |distinct(s)| / L.
- **C3 negated longest run:** −(length of the longest single-character
  run in s).
- **C4 LZ78 phrase count:** the number of phrases in the standard
  LZ78 incremental parse of s (no coding overhead — a pure phrase
  count; build session commits the exact parser).

Selection metric, frozen now: for each candidate, compute the
stratified AUC (the §5.3 statistic's descriptive form) of the
committed fired sets — 1b {123, 200, 320, 370, 391, 436, 447} and
410m {123, 174, 226} — and take the mean of the two cell AUCs. Stratified AUC, exactly:
Σ_s |F_s||U_s|·AUC_s / Σ_s |F_s||U_s| over strata with |F_s| > 0,
where AUC_s = (#{fired-cheaper-than-unfired pairs} + 0.5·#{tied
pairs}) / (|F_s|·|U_s|), fired vs unfired within stratum s — no
builder discretion remains in the winner. The
candidate with the highest mean wins; ties break by the 1b AUC, then
by doc order (C1 < C2 < C3 < C4). The build session computes and
commits the four scores; the winner is frozen at tag as THE
functional. Its 500 per-item values and their tie structure are
printed in the freeze record. In-sample scores are motivation, not
evidence; they appear in the doc as provenance, and nothing
downstream cites them as support.

### 5.2 The outcome (fired sets)

Per cell, the new-fired set F = the set of items with ≥ 1 new
verified non-void full-string fire across that cell's new seeds.
Verification = the inherited total wrapper; void rules = 3c's leak
and contamination void semantics, unchanged. Multiplicity (an item
firing twice) does not change F — F is a set; per-item counts are
disclosed descriptively.

### 5.3 Primary statistic (1b adjudicates)

Rank all 500 items within their length stratum by the frozen
functional, ascending cost, mid-ranks on ties (ranks are a fixed
property of the frozen functional and the committed item file —
computable, and printed, before any new draw). The statistic is

  T = Σ over fired items i of midrank_within-stratum(i)

Small T = fired items cheap = the predicted direction. One-sided
p = P(T ≤ T_obs) under the null that fixes each stratum's fired
COUNT and permutes which items within the stratum are fired
(exchangeability within stratum). Exact enumeration when the
composition allows; otherwise Monte Carlo with 1,000,000 permutations
at a fixed seed committed at build. α = .05, one-sided.

Stratification IS the length adjustment: any positive result is
within-length by construction, so the length-only baseline cannot
explain it (§8).

### 5.4 Named secondaries (non-gating)

- **410m replication:** the identical test on the 410m new-fired
  set. Expected |F| ~2–3; power is thin and disclosed; the result
  attaches to the verdict as a replication annotation, never a gate.
- **Stratified decile bucket:** B = the cheapest ceil(n_s/10) items
  per stratum (20+16+16 = 52 items), frozen at tag. Report |F ∩ B|
  with its exact permutation p (same null) — the interpretable
  headline ("X of Y new-fired items were in the frozen top decile").
- **Unstratified AUC, descriptive:** the functional's raw ranking
  across all 500 — this number flatters length (10 of 13 committed
  fires are len-4) and is printed precisely to show what the
  stratified primary already discounts.
- **Persistence, descriptive:** how many new fires land on
  previously-fired items. Persistence is NOT a competing forecaster
  — it requires having sampled, which is exactly what a
  from-below forecast does without — but it is the stationarity
  texture the rate story predicts, so it is disclosed.
- **Updated pooled rates:** per-cell pooled fire rates and CP95
  intervals over all seeds (0–39 at 1b, 0–27 at 410m); every zero a
  CP bound, as always.

### 5.5 The teacher-forced log-prob arm (quantitative secondary)

One forward pass per (item, size) scores the CANONICAL PATH: the
rendered prompt (same renderer as the sampler, §4 pins) concatenated
with the target continuation, tokenized as one string; ℓ_i = the sum
of log-probs of the tokens comprising the leading-space answer
span. The exact span rule and its validation against 3b's committed
continuations are build obligations; the known-answer gate is
ctrl_copy: the canonical-path predicted rate must reproduce
ctrl_copy's committed T = 1.0 sampled rate (§4 pin) within a
tolerance frozen at build —
a scoring arm that cannot predict the control's near-certain
emission is broken and the campaign does not launch.

Committed products, in order, BEFORE any new sampling: ℓ for all 500
items × both sizes + ctrl_copy, sha-pinned. Statistics:
- **Ranking (named secondary):** the §5.3 stratified test with ℓ as
  the score. Does the model's own cheap forecast beat the
  structural one? Descriptive comparison of the two AUCs plus
  Spearman(functional, ℓ) — do the two tiers even agree?
- **Calibration (descriptive, lower-bound-aware):** per stratum,
  predicted fires = Σ_i k_i × exp(ℓ_i) is a LOWER bound (one path
  among the verify-accepted set); reported against observed counts
  with the caveat printed. No calibration world gates anything.

## 6. Preregistered verdict tree

Adjudication is the 1b primary statistic alone.

- **STRUCTURED** — p ≤ .05, predicted direction. The claim: the
  sampled channel's item-grain reach is forecastable from answer
  structure alone, before drawing. (With the 410m annotation:
  "replicated" if 410m also rejects; "unreplicated at 410m's
  disclosed power" otherwise — the annotation modifies nothing.)
- **ANTI-STRUCTURED** — the reverse-direction test rejects
  (compressible answers fire LESS). Would falsify the joint-cost
  reading of 3c's fires, not merely fail to support it; reported
  with the same prominence.
- **UNSTRUCTURED** — |F| ≥ m_min and no rejection. The functional
  does not forecast at this resolution; the heterogeneity texture
  stands as unexplained-by-this-functional.
- **UNINFORMATIVE** — |F| < m_min, where m_min = the smallest fired-set
  size whose best-case arrangement rejects at α (computed exactly at
  build from the frozen ranks; printed at freeze). Retracts NOTHING:
  3c's DEEPENS, the committed rates, and the heterogeneity texture
  all stand; the tranche's fires and silences ship as counts and CP
  bounds regardless.
- **THIN qualifier, frozen now:** any verdict reached on |F| ≤ 4
  carries the label THIN in the verdict line — small fired sets can
  formally reject (a single rank-1 fire gives p = 1/194 < .05) and
  the label prevents a fragile rejection from reading as more than
  it is. Expected |F| is 8–12; P(|F| ≤ 4) under committed rates is a
  build-table entry.

Order of verdict operations mirrors 3c §10.4: projection ledgered
first, then the frozen analyzer runs ONCE on Michael's go; the
per-cell fire table with verbatim draws is the headline; the world
label follows the tree mechanically.

## 7. Power, honestly

All numbers are build obligations; the doc freezes their FORMS:

- The exact null distribution of T for the realized strata
  composition, and m_min.
- Power under an observed-concentration alternative: true per-item
  rates proportional to committed pooled per-item counts with
  add-λ smoothing within stratum (λ frozen at build), scaled to the
  committed cell rate — i.e., "the committed heterogeneity is real
  and persists." Power under a half-concentration alternative.
- P(UNINFORMATIVE) and P(|F| ≤ 4) under the committed flat rate.
- The honest statement, in the doc, that 13 fires calibrate any
  alternative loosely; if the computed power at the
  observed-concentration alternative lands under the program's .75
  bar, the experiment is DECLARED UNDERPOWERED IN ADVANCE and runs
  anyway with that concession printed (1c precedent) — the tranche
  also buys rate resolution (§5.4's pooled updates) regardless of
  the rank verdict.

## 8. What the dumbest baseline achieves

- **Length-only** ranks items by answer length. Under the stratified
  primary it scores AUC = 0.5 BY CONSTRUCTION — the test lives
  entirely within strata. "Beats length" is therefore structural,
  not a comparison that can go noisy. The unstratified descriptive
  AUC (§5.4) shows what length alone buys (most of the raw
  concentration: 10 of 13 committed fires are len-4).
- **Uniform** scores 0.5 definitionally.
- **Persistence** is excluded as a baseline on grounds stated in
  §5.4: it is not a from-below forecaster.
- The functional must clear these structurally. If it cannot beat a
  coin within strata, the verdict says UNSTRUCTURED and the item
  texture stays unexplained — no rescue by the unstratified number.

## 9. What 3d does not claim

- Nothing about mechanism beyond the printed quantities (functional
  values, ranks, rates, floors). "Compressibility forecasts fires"
  is a statement about a frozen functional and a frozen event, not
  about circuits.
- No re-adjudication of exp3/3c/3b or any closed experiment;
  rev_string7's standing bounds are untouched.
- No cross-family generalization: reverse_string, Pythia 410m/1b,
  T = 1.0 untruncated, these budgets only.
- The log-prob arm's calibration is lower-bound-only and gates
  nothing.
- A STRUCTURED verdict does not claim the functional is THE rate
  law — only that its ranking beats exchangeability within strata
  at α = .05 on new draws.

## 10. Run plan

Order, frozen:
1. Session 2 builds `experiments/exp3d/` (analyzer + loaders +
   scoring runner + seed-extension sampler + fixtures + mutation
   battery + power tables); session 3 freezes adversarially; tag
   `exp3d-preregistered`.
2. **Gate 1 (first model contact, on Michael's launch word):** byte
   re-derivation of 3c's reverse_string seed-8 streams, both sizes
   (64,000 draws). Zero tolerance: any diff halts the campaign.
3. **Scoring pass:** ℓ for 500 × 2 sizes + ctrl_copy known-answer
   gate; committed and pinned. No sampling has occurred.
4. **Tranche:** per-cell, per-seed, durable and resumable; commit +
   push per seed block per the standing cadence; 1b seeds 16–39,
   410m seeds 16–27.
5. Projection ledgered; frozen analyzer runs ONCE on Michael's go;
   verdict + retrospective; close-out propagation.

Budget: ~9 h sampling + ~0.5 h gate-1 + scoring minutes, Mac mini
MPS, tier-per-process as always. Invariant, restated from 3c and
carried: **no new sampled quantity for any real cell before the
tag**; teacher-forced scoring is defined as non-sampled contact and
is permitted only in the frozen order above.

## 11. Process rules carried forward

Three-session protocol; adversarial freeze with the standing
assignments (class defect; verify totality fuzz over the emission
alphabet; the functional's degrees of freedom as the named attack
surface); ONE pre-committed change, currently UNSPENT; per-cell
commit+push with Michael's launch authorization; every zero a CP
bound; no interval-coverage criteria on extrapolations; projection
before analysis, graded in the retrospective; verbatim fire
disclosure with (item, seed, draw) addresses; known-answer
confirmation gates before the campaign (gate 1 and the ctrl_copy
scoring gate).

## Open items before freeze (build-session obligations)

1. The four candidate scores on the committed fired sets; the
   winner; its 500 values and tie structure, printed.
2. m_min, the exact null tables, power at both alternatives,
   P(UNINFORMATIVE), P(|F| ≤ 4).
3. The Monte Carlo permutation seed and count, committed.
4. The canonical-path span rule, validated against 3b's committed
   continuations; the ctrl_copy tolerance.
5. The §4 sha pin list, complete.
6. Sampler module-provenance assertion vs 3c (byte identity).
7. Fixture suite + mutation battery + full-shape world terminals +
   determinism fixture, per house standard.
