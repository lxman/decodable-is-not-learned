# Experiment 3c — Design Doc: Staged Deepening — What Is the Sampled Channel's Rate Structure?

**Status:** **DRAFT — NOT FROZEN.** Three-session protocol (design |
build | freeze, boundary = context clear; Michael's pacing ruling,
2026-08-15, carried forward). This doc is session 1; the build is a
later session; the freeze is a third session that opens adversarially
(cold re-read, assignment: find the class defect) and ends at tag
`exp3c-preregistered`. The instrument will be `experiments/exp3c/` —
`analyze_3c.py` with its own loaders, a seed-extension of exp3's
frozen sampler, a runner, a committed driver, and a fixture suite.

**Predecessor:** `experiment-3-design.md` (tags `exp3-preregistered`,
`exp3-closed` — **PARTIAL**: reverse_string/1b TAIL-ONLY on one
verified draw in 128,000 — item 436, 'xuvq' → " qvux", seed 0 — the
program's first real-model sampling elicitation; the other three
adjudicated cells WALL at pooled CP ≤ 2.34e-5; the mass arm
sign-inverted everywhere and its question CLOSED). Exp 3's frozen §7
pre-named this experiment: "the staged-deepening follow-up (k = 1024
conditional on WALL) is explicitly a successor experiment." The
forward-note (binding since Exp 1) supplies the asymmetry rule this
design leans on throughout: a fire is strong evidence; silence is
weak evidence bounded by budget.

---

## 1. The question

Exp 3 established existence: the complete reversal output is
reachable by pure T = 1.0 sampling on real weights — once, in the
cell where the joint autoregressive path is cheapest (the
shortest-answer rung, the larger probe size). One draw supports an
existence claim and nothing else. This experiment buys the next
resolution rung on the same committed streams' terms: **what is the
rate structure of the sampled channel — does the fired cell fire
again, does deeper sampling reach any previously walled cell, and
does the fire rate carry the answer-length dependence the joint-path
mechanism predicts?**

The joint-path mechanism makes a crude quantitative prediction: if
per-character emission carries roughly independent per-position
costs, the per-draw full-string rate falls geometrically with answer
length. The committed batteries already span lengths 4–7
(reverse_string: 194/155/151 items at 4/5/6; rev_string7: 500 at 7),
so the length profile comes free — but at these rates most strata
are undetectably rare at any feasible budget, so the length profile
is preregistered as DESCRIPTIVE (exact per-stratum CIs, no trend
test; §7 shows the honest power numbers that forbid one).

**Four worlds, named in advance,** adjudicated on the four exp3
cells (reversal rung × probe size, trained) over the NEW draws:

- **DEEPENS** — the fired cell (reverse_string/1b) fires again in
  the new draws AND at least one previously walled cell fires. The
  sampled channel's reach grows with budget in both rate and extent;
  signature 2's resolution parameter is measurably load-bearing.
- **REPLICATES** — the fired cell fires again; every previously
  walled cell stays silent. The exp3 fire was a draw from a stable
  nonzero rate localized where the mechanism says it should be; the
  walls stand at 4× resolution.
- **RELOCATES** — the fired cell is silent in the new draws but some
  previously walled cell fires. Read as sampling variance at
  single-event rates, pooled across cells (fires are exact-verified;
  there is no instrument doubt to resolve): existence extends to the
  newly fired cell, the fired cell's pooled rate revises downward.
- **LONE-DRAW** — zero new fires anywhere. Exp 3's fire STANDS
  (it is committed, verified, and existence is not retractable by
  later silence — the asymmetry rule, applied symmetrically to our
  own result); the pooled rate at the fired cell becomes 1/512,000
  (point 1.95e-6) and the verdict text states the single-event
  regime plainly: reachability demonstrated, rate below this
  design's resolving power.

No world retracts exp3's PARTIAL; no world re-adjudicates any closed
experiment. The costliest world for the resolution essay is
LONE-DRAW, and its reading is fixed now so it cannot be softened
later.

---

## 2. Why 3c will not die its predecessors' deaths

1. **3a's death (valueless verdict input):** every input is either an
   exp3-committed record verified present at freeze (the 256-draw
   streams, the twin record, the item pins) or produced by a frozen
   loader that hard-errors on malformation; full-shape worlds reach
   every terminal before the tag.
2. **2c's/exp3's death class (a criterion that credits format):** the
   only scored quantity is exact-match full-string fire — 2c's frozen
   verifier, immune to format by construction (the answer never
   appears in any prompt; emitting the quoted input fails). There is
   no mass arm, no floor, no rank statistic to subvert.
3. **Exp 3's stop #1 (real-model glue untested pre-tag):** the
   tokenizer/config width smoke is now a permanent fixture and a
   freeze-checklist line (standing rule from the exp3 ledger); 3c
   additionally byte-gates the ENTIRE pipeline against 128,000
   committed draws before any new quantity counts (gate 1).
4. **Seed cherry-picking / adaptive stopping:** twelve new seeds
   (4–15) preregistered here, per-seed tallies committed, k fixed
   before the first draw, every raw draw stored. Pooling with exp3's
   committed seeds 0–3 is preregistered HERE, not decided at
   analysis.

---

## 3. The matrix

| axis | levels |
|---|---|
| cells (scored) | the 4 exp3 adjudicated cells: `rev_string7`, `reverse_string` × 410m, 1b, trained |
| cells (gate) | seed-0 byte re-derivation on the 4 scored cells + `ctrl_copy`/1b/trained (gate 1; no new scored quantity) |
| draws | NEW: seeds 4–15 (12 × 64 = 768 per item), T = 1.0, no truncation, `MAX_NEW_TOKENS` 12, batch 16 — identical generation law to exp3, same per-(cell, seed, item) substream formula. POOLED with exp3's committed seeds 0–3 → k_total = 1024 per item |
| items | the identical committed item files (sha-pinned to 3b's §4 referents, unchanged); length strata 4/5/6 (194/155/151, reverse_string) and 7 (500, rev_string7) |
| model | Pythia 410m/1b trained, fp32 exact upcast (exp3's ledgered dtype policy, unchanged); untrained twins NOT re-sampled — exp3's committed twin record (0 fires in 8 twin cells, 512k twin draws) is the standing contamination referent |

New-draw volume: 4 × 500 × 768 = 1,536,000 draws (≈ 13 MB gz);
re-derivation volume (gate 1): 5 × 500 × 64 = 160,000 draws,
discarded after byte comparison except the comparison record. At
exp3's measured throughput (1.152M sampling draws ≈ 9.8 h) this is
≈ 14–15 h: two Mac nights with per-cell resume. The Sparks stay
untouched.

---

## 4. Referents — every input, a committed value

| input | referent | location |
|---|---|---|
| exp3 committed draws (pool + gate-1 bytes) | seeds 0–3 raw streams, per cell | `experiments/exp3/results/sampling/*/{rung}.draws.jsonl.gz` (tag `exp3-closed`) |
| item files | sha256 equal to 3b's §4 pins (unchanged through exp3) | `experiments/exp3b/results/*/*.json` `items_sha256`; files in 2c/2b trees |
| stream formula | exp3's frozen `stream_seed` + chunk law | `experiments/exp3/sampler.py`, `stream_map.json` (tag `exp3-preregistered`) |
| verify | 2c's exact-match criterion | `experiments/exp2c/harness.py` (provenance-asserted import) |
| twin contamination record | 0 fires / 512,000 twin draws, 8 cells | `experiments/exp3/results/sampling/*_untrained/*`, `results/verdict.json` |
| throughput + determinism | measured tier times; byte-identical determinism reference | exp3 ledger; `experiments/exp3/determinism_reference.json` |
| the exp3 fire (context, not re-adjudicated) | 1/128,000, item 436, seed 0, draw 6 | `experiments/exp3/results/verdict.json`, VERDICT.txt |

---

## 5. Operationalization

- **Generation:** exp3's frozen sampler, imported (never copied,
  never modified), with 3c's seed set. The substream formula makes
  seeds 4–15 as committed as 0–3 were: generator seed = first 8
  bytes of sha256("exp3|{rung}|{size}|{mode}|s{seed}|i{item}") — the
  SAME namespace string, deliberately, so one formula governs the
  whole pooled set; the extended map (all 16 seeds × cells) is
  dumped and committed at build.
- **Scoring:** a draw fires iff 2c's `verify` accepts it against the
  item's answer. Fires are categorical; every fired draw is disclosed
  verbatim in the verdict record with its (item, seed, draw) address.
- **Pooling:** per-cell counts over k_total = 1024 × 500; per-seed
  and per-length-stratum tallies stored; the analyzer recomputes
  every tally from raw draws (exp3's rule) across BOTH trees and
  refuses disagreement.
- **Bounds:** every zero as a Clopper–Pearson bound, pooled and
  per-stratum; every nonzero count with its exact two-sided CI.
- **Descriptives (never adjudicated):** length-stratum rates with
  CIs; per-seed spread; mean draw length; the pooled-vs-new rate
  comparison at the fired cell.

---

## 6. Preregistered verdict tree

Malformed batteries are hard errors before any gate (missing cells,
count mismatches, seed-set violations, pin disagreements).

1. **Stream continuity fails** — gate 1: the seed-0 re-derivation of
   any of the 5 gate cells differs from exp3's committed bytes in
   ANY draw → `INSUFFICIENT_DATA`. The streams are deterministic on
   this stack (exp3's twin/trained tier times matched to the
   second); a single differing byte means the generation law
   changed, and no new draw is interpretable. Differing draws
   disclosed verbatim regardless of count.
2. **Provenance fails** — any scored cell's items_sha256 ∉ the §4
   pins, answers/labels ≠ the referent's, dtype ≠ float32, seed set
   ≠ {4..15}, or draws_per_seed ≠ 64 → hard error (not a verdict).
3. **Contamination** — no new twin sampling exists to fire; the gate
   is the standing exp3 twin record, cited in the verdict record. If
   any FIRED draw's text is found in its own prompt (the leak class
   the items rule out by construction), that fire is void and the
   fact is a disclosed finding; both rungs' fires void →
   `INSUFFICIENT_DATA`.
4. **Adjudicate** on the four cells' NEW-draw fire counts:
   fired-cell-fires ∧ any-wall-fires → **DEEPENS**;
   fired-cell-fires ∧ no-wall-fires → **REPLICATES**;
   ¬fired-cell ∧ any-wall-fires → **RELOCATES**;
   no new fires → **LONE-DRAW**. The frozen reason text for each
   world carries §1's reading verbatim, the pooled 1024-draw rates
   with CIs/bounds, and the blind-region statement (§7).

---

## 7. Power, honestly

Detection probability 1 − (1−p)^n against true per-draw rate p:

- **Fired cell, new draws** (n = 384,000): ≈ .95 at the observed
  point rate 7.8e-6; .53 at 2e-6; .32 at 1e-6. REPLICATES is the
  expected world iff the exp3 fire reflects a stable rate near its
  point estimate; LONE-DRAW at ~1-in-3 even if the true rate is
  1e-6.
- **Length-4 stratum at 1b** (n = 148,992 new): ≈ .95 at the
  stratum's observed 2.01e-5.
- **Each walled cell** (n = 384,000 new; 512,000 pooled): a
  persistent zero tightens the pooled bound to ≤ 5.85e-6 (from
  2.34e-5) — 4× resolution.
- **Why no trend test:** under geometric length scaling from the
  len-4 point rate, p(5) ≈ 7.7e-7 → stratum detection ≈ .11;
  p(6), p(7) effectively zero at any feasible k. A preregistered
  trend test over strata this blind would be theater; the length
  profile ships as descriptives with CIs, and the §1 mechanism is
  tested only at the resolution the budget actually buys (does
  len-4 replicate; do longer strata stay silent).
- Exact tables recomputed at freeze from the frozen code and
  committed, including the pooled-rate CI machinery.

---

## 8. What the dumbest baseline achieves

| degenerate strategy | outcome |
|---|---|
| any format/letter-statistics emitter | full-string exact match on a reversal it hasn't computed: rate ≈ 26^-L per draw of luck — the 26^-4 ≈ 1.5e-6 luck floor at L=4 is BELOW the fired cell's observed 2e-5 stratum rate but not far below; §7's CI on the replicated rate is the honest comparator, and the luck floor is printed beside it in the verdict record |
| echo model | emits the input; verify fails by construction |
| seed cherry-picking | 12 new seeds preregistered; per-seed tallies committed; a fire on one stream is reported as exactly that |
| adaptive stopping / budget games | k fixed here; pooling preregistered here; no conditional branches read intermediate counts |
| "one fire, declare victory" | REPLICATES requires a NEW fire; exp3's committed draw cannot re-fire this design's tree |
| "zero new fires, retract exp3" | forbidden by the frozen LONE-DRAW reading: existence stands, rate bounds tighten |
| harness drifted since exp3 | gate 1 byte-re-derives 160,000 committed draws end to end |
| verdict input with no value | full-shape worlds to every terminal before the tag; loaders hard-error |

The luck-floor row is the design's honest weak point and is stated
in §9's scope: at L=4 the gap between "computed the reversal
occasionally" and "got lucky against 26^4" is a factor of ~13 on the
point estimate, and the CI from a handful of fires may not exclude
regions near the luck floor. 3c measures the rate; it does not claim
the mechanism behind each fire. (The luck floor is also why longer
strata matter descriptively: luck falls 26× per character while a
computed-path rate should fall far more slowly.)

---

## 9. What 3c does not claim

- **No re-adjudication** of exp3, 3b, or any closed experiment; the
  PARTIAL and the existence claim stand regardless of outcome.
- **Nothing about mechanism per fire** (computed vs lucky) beyond
  the luck-floor comparison printed with the rates.
- **Nothing about temperatures ≠ 1.0, truncation, or search.**
- **Not signature 3** (forecastability) and **not rank prediction**;
  DEEPENS/REPLICATES builds the graded substrate those successors
  need but tests neither.
- **Pythia only, these four cells only, this budget only.** Blind
  below ~2e-6 at the fired cell and ~5.9e-6 per walled cell.

---

## 10. Run plan

1. **Build (session 2):** `experiments/exp3c/` — analyze_3c with own
   loaders (pooling both trees' raw draws, tally recompute both
   directions), seed-extended stream map committed, re-derivation
   runner, tier-per-process driver (2 tiers: 410m, 1b), fixture
   suite + full-shape worlds to every terminal + mutation both
   directions, exact §7 tables from frozen code, storage audit.
2. **Freeze (session 3, adversarial):** cold re-read hunting the
   class defect; the standing tokenizer/config glue smoke; gate-1
   re-derivation rehearsed on ONE cell's committed bytes (creates no
   new quantity — a read + regenerate + compare); determinism
   reference re-verified; tag `exp3c-preregistered`.
3. **Campaign:** gate-1 re-derivation first (all 5 cells), then new
   draws, 410m before 1b, per-cell commit+push (watcher pattern),
   skip-if-exists, preflight per (size, dtype).
4. **Analysis:** projection ledgered, then the frozen script, once,
   on Michael's go.
5. **Close-out:** VERDICT.txt, retrospective with the projection
   graded, tag `exp3c-closed`; essay/experiments.md updates per
   world; the supporting-repo re-extraction gains the exp3 AND exp3c
   rounds together.

---

## 11. Process rules carried forward

- Three-session protocol; adversarial freeze; one pre-committed
  change (exp3's remains unspent and does not carry over).
- Dumbest-baseline analysis before freeze (standing since Exp 2) —
  §8 above, to be re-opened adversarially at the freeze.
- Tokenizer/config glue smoke on the freeze checklist (standing
  since exp3's stop #1).
- Every zero a CP bound; blind regions in the verdict text; numbers
  transcribed, never recalled; verdict projection before the
  analysis; per-cell commit+push; tier-per-process; frozen things
  stay frozen (exp3's sampler is imported with provenance asserts,
  never copied or edited).

---

## Open items before freeze

1. Scaffold + provenance-asserted imports (exp3 sampler frozen
   module; 2c verify; exp2b models).
2. Seed-extended stream map (16 seeds × cells) committed + golden
   literals in fixtures.
3. Re-derivation runner + its synthetic-model fixture (byte gate
   must fire on a planted one-byte drift, both directions).
4. analyze_3c: two-tree pooling loaders, tally recompute, verdict
   tree, full-shape worlds to every terminal (all four worlds, both
   ID routes, the leak-void route).
5. Exact §7 tables from the frozen code, committed.
6. Driver + storage audit (+13 MB gz draws; layout decided at
   build).
7. Mutation testing both directions on analyze_3c.
8. Freeze checklist skeleton: glue smoke, determinism re-verify,
   gate-1 single-cell rehearsal, cold suite, full-shape, mutation,
   empty-tree hard error.
