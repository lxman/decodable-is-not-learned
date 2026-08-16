# Experiment 3 — Design Doc: Elicitation — Is the Dissociated Information in the Output Distribution?

**Status:** **FROZEN 2026-08-16 — tag `exp3-preregistered`.**
Three-session protocol (design | build | freeze, boundary = context
clear; Michael's pacing ruling, 2026-08-15). The freeze session
opened adversarially and FOUND THE CLASS DEFECT: §5's original w̃
mass statistic credited set-level lexical priming; §5 was amended
pre-tag to the within-item interior-competitor form (ledger
`experiments/exp3/PROGRESS.md`, 2026-08-16), the amendment was
**ratified by Michael 2026-08-16**, and the tag was applied on the
ratification commit over the cold-green tree (suite 140, worlds
17/17, mutation 56/56, referents 14/14, determinism and power tables
byte-identical, preflight all five local sizes). Two further freeze
rulings are frozen with it: the gate-3 ID trigger covers the
adjudicated cells AND ctrl_copy's trained cells (§6.3), and fp16
tiers preflight on the paths they use (`--keep1-only`). The instrument will be `experiments/exp3/` —
`analyze_3.py` with its own loaders, a mass module, a seeded sampler,
a runner, a committed tier-per-process driver, and a fixture suite.

**Predecessors:** `experiment-3b-design.md` (tags `exp3b-preregistered`,
`exp3b-closed` — **DISSOCIATION**: reversal first-character emission at
floor in all 4 probe-size trained cells against same-weights
basis-starved probe margins .6263/.7725 (rev_string7) and .5731/.6749
(reverse_string); ctrl_copy .9940 both sizes; every gate clean). Exp 3a
(byte-referent lineage), 2c and 2b (items, prompts, shots, harness —
read, never modified). The **forward-note for this design doc**
(`experiments.md`, added 2026-07-14, approved by Michael 2026-07-12) is
binding and §11 carries its rules verbatim. Exp 1/1b supply the S2
lineage: `lubana_above` was probeable 15/15 and samplable 0/15 —
internal structure with zero output mass is a real, reproducible state,
which is why this experiment exists as a question and not a formality.

---

## 1. The hypothesis under test

The three-signature discriminator (thesis carve-out) separates
resolution-class capabilities from percolation-class ones: probeable
below threshold, elicitable by exhaustive sampling, forecastable from
below. 3b certified signature 1 on a real model: the reversal answer's
first character is linearly decodable at margins .57–.77 from the same
residual streams whose greedy emission sits at floor. Experiment 3 is
signature 2 on the same cells: **is that information in the output
distribution at all?**

Two adjudicated instruments, roles preregistered:

- **First-character mass** — the distribution itself, read exactly:
  the probability the model's next-emission begins with the probe
  label's character, computed from forward passes (§5), deterministic,
  no sampling budget. This is the direct follow-up to 3b: the probe
  read the residual stream; the mass reads the model's own readout of
  that stream through the unembedding.
- **Full-string reachability** — verified exact-match successes among
  k seeded ancestral draws per item at T = 1.0 (§3). This is the
  capability itself (all seven characters), the literal "elicitable by
  exhaustive sampling," and the falsifiable edge the original
  Prediction 4 framing named: gap-closing wherever the base rate is
  nonzero, a hard wall where it is genuinely zero.

A full-string success on a draw implies a first-character success on
that draw, so the instruments order themselves and **four worlds are
named in advance**, adjudicated per reversal rung × probe size:

- **ELICITABLE** — mass significant under §5's within-item positional
  statistic ("mass elevated"/"at floor" throughout this tree means
  that statistic significant / not significant) AND full-string fires
  (≥1 verified success; seed spread reported). The famous zero was an
  argmax cliff over nonzero distribution mass. Signature 2 fires; the
  future rank-prediction successor (the spread-gated battery
  experiment) gains its graded substrate.
- **BULK-ONLY** — mass elevated, full-string walled at the CP bound.
  The first character is in the distribution's bulk; the
  seven-character joint path carries no measurable mass. The units gap
  relocates from the metric into the autoregressive channel.
- **TAIL-ONLY** — mass at floor, full-string fires anyway. Rare-event
  reachability below the mass floor's resolution: the answer lives in
  the tail, invisible to argmax and to position-1 mass alike. By the
  forward-note's asymmetry rule a fire is strong evidence, so this
  world is reported as elicitation, with the mass result beside it.
- **WALL** — mass at floor AND zero successes in 128,000 pooled draws
  (per-draw rate bounded above at ≈2.3×10⁻⁵). The dissociation extends
  through the entire output channel at this resolution. Signatures 1
  and 2 then disagree on a real model, and the reading is fixed now:
  per the forward-note, sampling silence is weak evidence and **the
  frozen probe module is the preregistered arbiter** — WALL means
  "present in representation, absent from the output channel at depth
  k," not evidence against signature 1. The discriminator's clean
  dichotomy takes that hit honestly, in print.

No outcome is a PASS of the rank-prediction thesis. ELICITABLE builds
the substrate a future rank test needs; WALL is the outcome that costs
the framework most and is recorded so it cannot later be softened.

---

## 2. Why Exp 3 will not die its predecessors' deaths

1. **3a's death (verdict input with no value):** every input
   `verdict()` takes is either a committed record verified present
   with a defined value at freeze, or is produced by a frozen loader
   that hard-errors on anything malformed; the frozen tree is executed
   to **every terminal branch** (four worlds, every INSUFFICIENT_DATA
   route, contamination interactions) on synthetic full-shape
   batteries before the tag.
2. **2c's death (a floor that credits format):** caught TWICE in this
   document. At design time: the mass criterion as first drafted
   paired trained mass against the untrained twin's mass; the
   dumbest-baseline analysis (§8) kills that pairing — a model that
   learned only "answers are lowercase letters" beats the twin ~500/0
   with zero reversal knowledge. At the freeze (ledger 2026-08-16):
   the within-distribution w̃ replacement itself credited set-level
   lexical priming — the answer is a permutation of the input, so its
   first letter is always among the input's characters — and was
   amended to the within-item interior-competitor form (§5), whose
   θ = .5 null is exact for the entire position-symmetric mechanism
   class. The twin demotes to contamination gate.
3. **3b's operational lesson (MPS allocator ratchet):** the driver is
   tier-per-process from the first commit — one process per (mode,
   size) tier, sizes ascending, no process ever holds more than one
   tier's cache.
4. **Harness drift:** gate 2 re-decodes all 16 probe-size greedy cells
   and byte-gates them against 3b's committed records before any new
   quantity is read (§6); gate 3 cross-checks the two new instruments
   against each other (§6).

---

## 3. The matrix

| axis | levels |
|---|---|
| rung | `rev_string7`, `reverse_string` (the claim); `ctrl_copy` (positive control); `clock24_d999` (matched control — probe margin 0.0, the agreement quadrant) |
| instrument | first-character mass (exact, forward passes); full-string pass@k (seeded ancestral sampling) |
| model | mass: 410m, 1b, 2.8b, 6.9b, 12b trained + 410m, 1b untrained (28 cells; adjudication at 410m/1b only, eval sizes descriptive). sampling: 410m, 1b × trained/untrained (16 cells) |
| sampling | T = 1.0, **no truncation** (top-p = top-k = off; truncation deletes tail mass and tail mass is the question). k = 256 per item for the reversal rungs (4 RNG seeds × 64), k = 32 for the controls (4 × 8). Seeds 0–3, streams committed per (cell, seed), per-seed tallies stored |
| items | 2c's committed 500-item files, prompts, and 2 shots, verbatim (`reverse_string` from 2b's tree, 3b's loader logic) |

Raw draws are stored per item (2c's lesson: aggregates only is a
regret), and the full 26-letter mass vector plus residual buckets is
stored per item for every mass cell, so every downstream quantity is
recomputable without re-querying a model.

Budget: ≈1.15M draws of ≤12 new tokens (≈4 h at 410m, ≈10 h at 1b,
batch 16) + ~1 h of mass passes across the ladder + ~10 min of gate-2
greedy re-decode. One overnight Mac campaign, sequential,
skip-if-exists. The Sparks stay untouched — at this k they are not
needed.

---

## 4. Referents — every input, a committed value

| input | referent | location |
|---|---|---|
| item files | sha256 equal to the values recorded in 3b's cell records | `experiments/exp3b/results/*/*.json` `items_sha256` |
| gate-2 byte referents | 3b's 16 probe-size greedy cells, 500 continuations each | `experiments/exp3b/results/{410m,1b}_{trained,untrained}/` |
| gate-1 anchor | ctrl_copy committed .960/.980 full-string argmax (2c inclusion) and 3b first-char .9940/.9940 | `exp2c/results/inclusion/`, 3b verdict record |
| marginal floors (descriptive) | 3a's committed floors, sha-pinned `f299fa08…` | `experiments/exp3a/chance_floors.json` |
| probe margins (context, arbiter) | per-size m3 margins | `experiments/exp3b/probe_margins.json` |
| untrained twins | construct at `untrained_seed = 0`, state-hash verified | 3b `referent_check.json` procedure, re-run at freeze |

All referents exist with defined values today, before any Exp 3 code
exists. The verdict reads nothing produced outside this list and the
campaign's own cells.

---

## 5. Operationalization

- **First-character mass, to whitespace depth 2.** For each item, one
  forward pass on the committed prompt yields the next-token
  distribution. mass₁ = Σ P(t) over tokens t whose decoded text,
  whitespace-stripped, begins with the probe label (case-folded);
  plus, for each whitespace-only token w at position 1, P(w) × Σ P(t|w)
  over matching t at position 2 (one extra forward pass per (item,
  whitespace token) — the tokenizer has only a handful of pure-
  whitespace tokens, and the passes batch). The residual whitespace-path mass beyond depth 2 is
  computed and disclosed per cell; if it exceeds .01 in any
  adjudicated cell, that cell's mass is reported as a bracket
  [mass, mass + residual] and the sign test (below) is run at both
  ends, with disagreement reported as its own finding. The letter-mass
  vector m_i(c), c ∈ a–z (same depth-2 convention per letter), is
  stored per item. Fixtures verify the computation on synthetic
  distributions with hand-computable answers.
- **The mass statistic (within-item, position-null — AMENDED AT THE
  FREEZE, ledger 2026-08-16; the w̃ cross-item form it replaces is
  recorded below).** Per item i with answer a_i of length L:
  s_i = m_i(a_i[0]) − mean_{j=1..L−2} m_i(a_i[j]) — the answer's
  first-character mass against the mean mass of the answer's own
  INTERIOR characters, multiplicity kept. The answer's LAST character
  (= the input's first character, the echo target) is read on neither
  side. Exact one-sided sign test on sign(s_i) across items, zeros
  dropped and their count disclosed, α = .01 Bonferroni across the
  **4 adjudicated reversal cells**. The null is exact by
  construction: the permutation rungs' input characters are iid
  uniform, so ANY mechanism reading the input only through
  position-symmetric features — item-independent letter priors,
  format priors, set-level lexical priming — makes the read positions
  exchangeable and lands at θ = P(s_i > 0) = .5 exactly; echo
  (input-first-character favoritism) is read on neither side and
  moves nothing. What fires is mass favoring the input's LAST
  character over its interior — the position-1 reversal signature 3b
  probed (on ctrl_copy, first-position favoritism = the copy
  signature). An item with L < 3 is a structural tie (none exists:
  committed answer lengths are 7 / 4–6 / 4–6 on the letter rungs);
  the statistic is computable for a rung iff every character it reads
  lies in the stored a–z block (clock24_d999 reads digits →
  computable=False, gates/descriptives only). Controls test at
  n_tests = 1, descriptive.
  *Superseded original (for the record):* s_i = m_i(y_i) −
  Σ_{c≠y_i} w̃_c m_i(c) with w̃ the empirical answer-first-letter
  distribution renormalized to exclude y_i. Killed by the freeze's
  adversarial read: because the answer is a permutation of the input,
  y_i is always among the input's characters while the w̃-competitors
  mostly are not, so a set-level lexical primer (mass boost on every
  character present in the quoted input — position-blind context
  copying) fires it on essentially every item (θ ≈ 1) with zero
  reversal knowledge, and an anti-concentrated item-independent prior
  reaches θ = w̃-mass{f > Σw̃f} up to ≈ .77. Both shapes are visibly
  live in 3b's committed continuations (in-answer-set greedy rates
  .968–.984 against .17–.24 chance; one cell collapsed to a single
  letter 498/500). The original's "θ = .5 by construction" held only
  for exactly-uniform spread and letter-uniform guessing.
- **Sampling.** Seeded ancestral generation, T = 1.0, no truncation,
  `MAX_NEW_TOKENS` 12, batch 16, four committed RNG streams per cell
  (seeds 0–3), 2c's `render_prompt`/shots verbatim. Every raw draw
  stored. **Full-string fire:** ≥1 draw in the cell's pooled 4 × k
  verified correct by 2c's exact-match `verify`, per-seed tallies
  reported with any fire. Fires are categorical: the verifier is
  exact, so there is no statistical false positive, only leaks (gate
  5's job). **Every zero as a Clopper–Pearson bound**, pooled and
  per-item-max forms both reported.
- **Sampled first-char rate** (gate 3 input): 3b's `first_char`
  scoring, verbatim, applied to every draw.
- **Also recorded, never adjudicated:** eval-size mass descriptives
  (the scale trend of the correct-letter mass — the precursor curve),
  full-string rates per seed, mean draw length, and per-item pass
  counts.

---

## 6. Preregistered verdict tree

Adjudicated in precedence order. Malformed batteries (missing cells,
duplicate cells, count mismatches, missing referents) are hard errors
before any gate, never verdicts.

1. **Positive control fails** — ctrl_copy's mass sign test not
   significant at **either** probe size (the gate passes only when it
   clears at both), OR its pooled sampled full-string rate's 95% CP
   lower bound ≤ .5 at either probe size → `INSUFFICIENT_DATA`. An
   instrument pair that cannot see the distribution and reachability
   of a capability committed at .960/.980 argmax and .9940 first-char
   is not measuring either.
2. **Harness continuity fails** — the greedy re-decode of any of the
   16 probe-size cells differs from 3b's committed record in more
   than 2 of 500 continuations (3b's own tolerance) →
   `INSUFFICIENT_DATA`; every differing item disclosed verbatim
   regardless of count.
3. **Instrument coherence fails** — in any adjudicated cell **or
   either ctrl_copy trained cell** (widened at the freeze, ruling on
   reading 2, ledger 2026-08-16: gate 1's two arms can both pass while
   the control's instruments disagree — a rank-fired sign test plus a
   healthy full-string rate over a low mass bracket — and a run must
   not proceed past a disagreeing positive control), the sampled
   first-char success count is incompatible with the computed mass
   bracket: the count's exact two-sided CP interval at α = .01/16
   (Bonferroni across the 16 sampling cells) is disjoint from
   [mass, mass + residual] → `INSUFFICIENT_DATA`. Computed and
   disclosed for all 16 cells; twin and matched-control incoherence
   stay disclosed-only. The two instruments measure the same
   distribution; disagreement is a code-path defect (BOS, padding,
   prompt drift), not a finding.
4. **Sampler reproducibility** is a freeze-time gate, not a runtime
   branch: the seeded sampler must reproduce a pinned fixture draw set
   byte-identically across two runs on this stack before the tag, and
   campaign records carry seeds and library versions. Recorded in the
   freeze checklist.
5. **Untrained twin fires** — any **probe-size** twin cell significant
   on the mass sign test (n_tests = 1) or carrying ≥1 verified
   full-string success → the rung is contaminated and excluded from
   step 6's quantifiers (a random-weights model emitting a
   seven-character reversal is a harness leak by definition). Both
   reversal rungs contaminated → `INSUFFICIENT_DATA`: a universal
   quantifier over zero cells decides nothing (3b §6, verbatim).
6. **Adjudicate the claim** on the eligible reversal cells
   (rung × 410m/1b), each cell labeled by its (mass significant?,
   full-string fired?) pair:
   - all eligible cells **(sig, fire)** → **ELICITABLE**
   - all **(sig, no fire)** → **BULK-ONLY**
   - all **(not sig, fire)** → **TAIL-ONLY**
   - all **(not sig, no fire)** → **WALL**
   - any mixture → **PARTIAL**, per-cell table as headline, not
     caveat.

   `clock24_d999` participates in gates and descriptives only: probe
   margin 0.0, so it shows what agreement looks like in mass space.
   The WALL reading of §1 (probe as arbiter, silence as weak evidence)
   is part of this tree's frozen text, not post-hoc interpretation.

---

## 7. Power, and the regions this design cannot see

- **Mass side** (exact sign test, n = 500, α = .01/4 one-sided):
  critical count ≈ 282 of 500 non-tied items; power ≈ .95 at θ = .60,
  ≈ .26 at θ = .55; **blind for θ ≲ .57**. Exact table recomputed at
  freeze from the frozen code and committed, including recomputation
  at the realized post-tie n per cell. Under the freeze-amended
  statistic θ reads as P(the answer's first-character mass exceeds
  its interior mean) — the binomial machinery, critical counts, and
  the committed table are unchanged; only θ's interpretation moved
  from the w̃ form to the within-item form.
- **Sampling side:** detection probability 1 − (1−p)^128,000 against
  true per-draw rate p: ≈ .95 at p = 2.3×10⁻⁵, ≈ .72 at 10⁻⁵, ≈ .12
  at 10⁻⁶. **Blind below p ≈ 10⁻⁵.** A WALL verdict therefore means
  "no output-channel mass this design can resolve," never "zero," and
  ships with these bounds in the verdict text. The staged-deepening
  follow-up (k = 1024 conditional on WALL) is explicitly a successor
  experiment, not a branch of this one.

---

## 8. What the dumbest baseline achieves

| degenerate strategy | outcome |
|---|---|
| format-only emitter (learned "answers are lowercase letters," nothing else) | uniform spread cancels exactly (all ties); ANY item-independent letter prior, however shaped, sits at θ = .5 exactly under the freeze-amended within-item statistic by position exchangeability. This baseline class KILLED the twin-paired criterion at design time and the w̃ cross-item criterion at the freeze (an anti-concentrated prior reached θ ≈ .77 there) |
| set-level lexical primer (mass boost on every character present in the quoted input — position-blind context copying; visibly live in 3b's continuations at .968–.984 in-answer-set greedy rates) | cancels algebraically under the within-item statistic: every character the statistic reads carries the same boost → exact ties. Under the superseded w̃ form this fired with θ ≈ 1 — the freeze's class-defect finding |
| echo model (mass on the input's first character) | full-string verify fails on reversal by construction; the echo character is the answer's LAST character, which the amended statistic reads on neither side → moves nothing. (Recency-toward-the-input's-last-character mass is not a confound: favoring the input's last character at emission position 1 IS the reversal capability's first-character signature, the same quantity 3b's probe certified) |
| letter-uniform guesser | θ = .5 exactly (special case of the item-independent class) |
| "128k draws, zero successes, therefore zero" | banned; CP bounds only, blind region stated in the verdict |
| cherry-picked sampling seed | seeds 0–3 preregistered; per-seed tallies committed; a fire on one stream is reported as exactly that |
| adaptive stopping when a result looks close | none exists; k is fixed before the first draw |
| verifier leak | the answer string never appears in any prompt; emitting the quoted input verbatim fails exact-match |
| harness drifted since 3b | gate 2 byte re-decode; gate 3 cross-instrument coherence |
| verdict input with no value on this battery | impossible to freeze: full-shape batteries must reach every terminal branch (all four worlds, PARTIAL, every INSUFFICIENT_DATA route, both contamination interactions) before the tag |

Ten routes. The bar is passable and can genuinely fail.

---

## 9. What Exp 3 does not claim

- **Nothing above the probe sizes.** The mass ladder to 12b is
  descriptive; no verdict branch reads it.
- **Nothing about learned verifiers.** The oracle verifier tests the
  distribution; Prediction 4's verifier-economy claims (best-of-n
  closing gaps in the wild) are out of scope.
- **Nothing about temperatures other than 1.0** or truncated
  distributions.
- **ELICITABLE is not rank-prediction.** It establishes signature 2
  and the graded substrate a future rank test would correlate against
  probe margins; the thesis's core claim stays untested here.
- **WALL is not evidence against signature 1.** The probe is the
  preregistered arbiter for that disagreement; silence is weak
  evidence (forward-note, binding).
- **No re-adjudication** of 3b, 2c, or any closed experiment; **no
  probe re-fitting**.
- **Pythia only, these four rungs only.**

---

## 10. Run plan

1. **Build, later session:** mass module + seeded sampler + runner +
   `analyze_3.py` (own loaders) + fixture suite, mutation-tested both
   directions under the corrected harness; tier-per-process driver
   committed at build.
2. **Freeze, cold, third session:** adversarial re-read; synthetic
   full-shape batteries through every terminal branch; sampler
   determinism fixture (gate 4) attested; power tables committed from
   frozen code; tag `exp3-preregistered`.
3. **Campaign:** gate-2 greedy re-decode → mass cells (ladder) → all
   twin sampling → trained sampling, 410m before 1b. Commit per cell,
   push per cell (standing authorization to be reconfirmed at
   campaign time), skip-if-exists, one process per tier.
4. **Analysis:** verdict projection ledgered in
   `experiments/exp3/PROGRESS.md`, then the frozen script, once.
5. **Close-out:** `VERDICT.txt`, retrospective with the projection
   graded, tag `exp3-closed`, and the corresponding updates: essay
   (signature-2 status, whichever world), `experiments.md`
   (Prediction 4's edge: found or walled), methods paper only if an
   instrument lesson emerges.

---

## 11. Process rules carried forward

- Three-session protocol; the freeze session opens adversarially.
- Thresholds, floors, statistics, and the four-world tree frozen
  pre-run; analysis committed with the doc's freeze, with its own
  loaders; every verdict input value-checked at freeze (3a's rule).
- **Forward-note bindings, verbatim:** sampling elicitation is
  scale-fragile and seed replication is part of the budget (4 streams,
  per-seed tallies); **a fire is strong evidence, silence is weak** —
  no criterion reads "no samples passed" as "structure absent"; the
  frozen probe module is the arbiter wherever sampling and probing
  disagree; no cross-system or cross-capability continuous criteria on
  accuracy-derived scales — null-relative units and within-system
  comparisons only.
- Every zero as a Clopper–Pearson bound; blind regions in the verdict
  text.
- One pre-committed change, reason ledgered before the change; 3b's
  remains unspent and does not carry over.
- Verdict projection ledgered before the analysis runs once.
- Per-cell results as headline; commit per cell; disclose provenance
  irregularities in the ledger before analysis (3b's OOM precedent).
- Tier-per-process campaign from the first commit.

---

## Open items before freeze

1. Mass module (depth-2 expansion, letter vectors, residual
   disclosure) + fixtures with hand-computable synthetic cases.
2. Seeded sampler with committed (cell, seed) → stream mapping; MPS
   seeded-sampling determinism verified twice on a pinned fixture set
   (gate 4's freeze artifact).
3. `analyze_3.py` + full fixture suite, one case per provision, both
   directions; mutation testing both directions.
4. Synthetic full-shape batteries reaching **all** terminal branches:
   four worlds, PARTIAL, every INSUFFICIENT_DATA route, one-rung and
   both-rung contamination, a coherence-gate fire, and a
   residual-bracket disagreement case.
5. Tier-per-process campaign driver, committed at build, dry-run
   verified.
6. Exact power tables (sign test incl. post-tie recomputation;
   detection curve) from the frozen code, committed.
7. Storage audit: ~1.15M raw draws (~tens of MB compressed) and
   28 × 500 letter-mass vectors — commit layout decided at build,
   nothing discarded.
8. Confirm 3b's `items_sha256` values match the item files 3 will
   load, and the twin construction procedure re-verifies at seed 0.
