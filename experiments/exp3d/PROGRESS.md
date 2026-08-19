# Exp 3d — Progress Ledger

Chronological, newest entry last inside each dated block. The design
doc (`experiment-3d-design.md`) stays frozen as approved in session 1;
everything the build discovered that touches doc TEXT is ledgered here
for freeze ratification, never silently absorbed (3c's convention).

---

## 2026-08-18 — BUILD SESSION (session 2 of 3 of design | build | freeze)

Instrument built at `experiments/exp3d/`: `analyze_3d.py` (loaders,
§4 pins, verdict tree), `functional_3d.py` (the four candidates + the
frozen §5.1 selection formula + ranks/ties/bucket), `rank_test_3d.py`
(exact-DP null, the §5.3 statistic, m_min, MC fallback),
`select_functional.py` → `functional_selection_3d.json`,
`compute_power_3d.py` → `power_3d.json`, `span_validation_3d.py` →
`span_validation_3d.json`, `scoring_3d.py` (teacher-forced arm),
`rederive_3d.py` (gate 1), `run/run_cell_3d.py` + `run/campaign_3d.py`
+ `run/commit_watcher_3d.sh`, `verify_referents_3d.py` (13-check
battery), `stream_map_3d.json`, fixture suite + mutation battery under
`tests/`. **Invariant held: zero model contact this session — no
weights, no forwards, no tokenizer files, no new sampled quantity for
any real cell.** All committed-byte work (selection, power, span
validation, referent battery) reads closed trees only.

### Build results (doc Open items 1–7)

1. **Winner: C1 unigram-bits** — mean stratified AUC .784503 (1b
   .678932, 410m .890052); C2 .783927 (margin .0006 — the frozen
   tie-chain never fired), C3 .470235, C4 .557774. Committed with all
   500 values, midranks, tie structure, and the 52-item decile bucket
   in `functional_selection_3d.json`; `analyze_3d.load_selection`
   recomputes everything from the item file at every run and refuses
   disagreement.
2. **Tie structure (the §2 print, the test's effective resolution):**
   len-4 is BINARY — 45 items with a repeated character (C1 = 6.0) vs
   149 all-distinct (8.0); len-5 has 4 distinct values; len-6 has 7.
   The len-4 stratum can only ever say "repeat-class vs not."
3. **m_min = 1**, realized in the len-6 stratum: 'rxxxxd' (item 200)
   is the UNIQUE cheapest len-6 answer, so a single fire there gives
   p = 1/151 = .00662 ≤ .05. Anti-direction m_min = 4, disclosed.
   Best-case table m = 1..12 committed in `power_3d.json`.
4. **Power, honestly (§7): DECLARED UNDERPOWERED IN ADVANCE.** At the
   observed-concentration alternative (λ̂ = .025641), 1b power = .2616
   (half-concentration .1889) against the program's .75 bar — the
   experiment runs anyway with this concession printed (1c precedent;
   §7 pre-authorized exactly this outcome: "13 fires calibrate any
   alternative loosely"). The tranche buys rate resolution (§5.4
   pooled updates to 1.28M/896k draws) regardless of the rank verdict.
   FLAT row — CORRECTED AT FREEZE (item f): P(STRUCTURED) = .0482
   AND P(ANTI-STRUCTURED) = .0450. Each DIRECTION calibrates at α; the
   tree tests both tails in sequence, so under no signal P(a
   directional verdict) = .0932, not .05. The earlier wording
   ("exactly null-calibrated") described the STRUCTURED branch alone.
   Also corrected at freeze (item g): the .2616 is an OPTIMISTIC
   figure, not a neutral one — the observed-concentration alternative
   puts its rate mass on the same 13 fires that SELECTED C1, so the
   simulated truth and the predictor agree by construction. Power is
   therefore AT MOST .2616 against a fresh concentration, which makes
   the underpowered declaration stronger, not weaker.
   410m (non-gating): power .0556; P(|F| ≤ 4) = .92,
   so its annotation will almost surely carry THIN. P(UNINFORMATIVE)
   under committed flat rate: ~0 at 1b (m_min = 1, E|F| ≈ 14.8),
   .1055 at 410m (= e^-2.25, closed form agrees). E|F| at 1b: 14.8
   flat, 12.3 observed-concentration.
5. **The λ rule, frozen BEFORE any power number ran:** λ = μ̂²/(V̂−μ̂)
   on the 1b committed per-item counts — the Gamma-shape moment
   estimator, i.e. the committed record's own overdispersion
   measurement. λ̂ = .025641. Rationale: §7's alternative is "the
   committed heterogeneity is real and persists"; Jeffreys add-half
   would CONTRADICT the committed overdispersion it is meant to encode
   (the smoothing mass dwarfs 10 counts and flattens the alternative
   to near-null). The sensitivity grid is committed non-gating:
   power .374 at λ=.01, .134 at .1, .069 at .5, .058 at 1.0 — the λ
   dial IS the power number, which is exactly why the rule had to be
   frozen by rationale first. One λ for the design, from the
   adjudicating cell (410m's three singleton fires carry no
   overdispersion signal: V̂ < μ̂ there, estimator undefined, cell
   non-gating throughout). Half-effect = counts at half strength,
   same λ.
6. **Alternative normalization reading (for the freeze to attack):**
   r_i ∝ (c_i + λ) across the cell, scaled so the MEAN per-item rate
   equals the committed pooled cell rate. §7's "within stratum" is
   read as smoothing-floor semantics (every item in every stratum gets
   λ), not per-stratum renormalization — which would zero out strata
   with no committed fires. Between-strata allocation is second-order
   for the conditional test anyway (it moves composition mix only).
7. **MC seed/count committed (Open item 3):** exact-DP null
   adjudicates every composition with per-stratum fired counts ≤ 64
   (the frozen cap; expected |F| is ~12 against it); past the cap, the
   §5.3 Monte Carlo clause runs at 1,000,000 permutations, seed
   20260818. Power-sim seed 20260819, 200,000 sims. The DP is exact
   enumeration in the design's sense — subset-count combinatorics to
   float64, proved against brute-force enumeration in the fixtures
   (max abs error ~2e-17).
8. **Span rule + ctrl tolerance (Open item 4), two-phase by design:**
   the build touches committed TEXT only. Committed-text half, in
   `span_validation_3d.json`: among ctrl_copy's VERIFIED committed 3b
   continuations, canonical-start rate = 478/480 (.9958) at 410m and
   489/490 (.9980) at 1b against the frozen ≥ .99 bar — and the
   verified counts REPRODUCE exp3's pinned GATE1_INCLUSION_REFERENT
   (480/490), a committed-referent cross-check. The two non-canonical
   verifiers are no-leading-space emissions, disclosed verbatim
   (item 82 'vezdlr' at both sizes; item 120 'aelqk' at 410m).
   All 13 committed sampled fires begin with " " + answer, re-proved
   from raw bytes. reverse_string's committed greedy: 0/500 canonical
   at BOTH sizes (the dissociation, descriptively). The
   real-tokenizer half (prefix property + round-trip on all 500 × 2
   rungs × 2 sizes) is computed, hard-asserted, and committed INSIDE
   the post-tag scoring pass per §10's order; a synthetic-tokenizer
   fixture proves the algorithm's refusal paths cold.
   **Build slip, disclosed:** the validator's first form used an
   UNCONDITIONAL .98 canonical-start bar, which conflates greedy
   ERRORS with form coverage; it fired on 410m (.956 unconditional)
   and was recast to the conditional form before anything froze. Both
   rates are in the committed record either way.
9. **ctrl_copy known-answer gate band, frozen:** p̂ = mean_i exp(ℓ_i)
   must land in [0.5 × r, r + 0.02] of the committed T = 1.0 sampled
   rate r (.79919 at 410m, .84125 at 1b — §4 pins 12787/16000,
   13460/16000, cross-checked against exp3's sha-pinned verdict at
   every load). Upper side: canonical-path mass cannot exceed total
   verified mass beyond the prefix-mass edge + CP noise (±.006);
   lower side: every real scorer bug class (wrong span, wrong offset,
   wrong base, dtype garbage) lands orders of magnitude off, while
   path multiplicity costs percent-scale — 0.5 is generous to the
   second and lethal to the first. exp(ℓ) is canonical-path PREFIX
   mass under the sampler's own law (step_probs, CPU fp32 softmax —
   exp(ℓ) is exactly the probability the frozen sampler emits the
   canonical token path); the §5.5 lower-bound framing carries the
   printed caveat that a canonical span continued by a word character
   counts in exp(ℓ) but fails verify.
10. **§4 pin list complete (Open item 5):** 3c's four exp3 pins
    inherited verbatim + exp3c/analyze_3c.py, exp3c/stream_map_3c.json,
    exp3c/results/verdict.json, exp2c/harness.py (the verify criterion
    and prompt renderer ARE verdict inputs — finding A's spirit one
    level down) as FROZEN_IMPORT_SHA256_3D; the two 3c draws-file shas
    (COMMITTED_3C_DRAWS_SHA256) checked in BOTH directions against
    gate-1 attestations (finding B); the two item-file shas
    (ITEMS_SHA_PIN) cross-asserted against the 3b-derived sha_refs at
    run time (two committed sources, one value); the 13 fire addresses
    (COMMITTED_FIRES_PIN) re-extracted from raw bytes at every run;
    the ctrl_copy sampled rates; the strata pin; the twin record.
11. **Sampler provenance (Open item 6):** exp3/sampler.py byte-pinned
    (same literal as 3c's) and `stream_map_3d.json` committed covering
    both cells' full pooled seed ranges (0–39 / 0–27), overlap-equal
    to exp3's map on seeds 0–3 AND 3c's on 4–15 — one formula, three
    experiments, executable. The runner asserts module provenance
    (exp3's `_assert_module_provenance`) before any cell.
12. **Fixtures (Open item 7):** suite 117 passed; full-shape worlds
    8/8 terminals (13 tests: STRUCTURED non-thin replicated,
    STRUCTURED THIN unreplicated, ANTI-STRUCTURED THIN, UNSTRUCTURED
    THIN, UNINFORMATIVE at |F| = 1 < m_min, INSUFFICIENT_DATA ×2
    (gate-1 drift; every-fire-void), void-discloses-and-proceeds);
    referent battery 13/13 on the real trees; all three committed
    artifacts (selection / power / span validation) byte-identical on
    same-session re-run (shas 2a2c358e… / 88a0b74c… / c36e3714…).
    Synthetic worlds carry a structure GRADIENT (runs/pairs/distinct
    per stratum, non-palindromic) because an all-uniform battery ties
    every midrank; the synthetic m_min = 2 exercises UNINFORMATIVE at
    a nonzero |F|.
13. **Mutation battery, both directions — first official run 50/51
    with ONE SURVIVOR, disclosed and closed.** The survivor:
    "gate: band exclusive at the edges (hardening)" (`lo <= p̂ <= hi`
    → `lo < p̂ < hi`) — the intended kill test's boundary value rode
    through an `exp(log(r))` float round-trip and landed strictly
    inside the band, so both semantics passed it. Closed
    structurally: the inclusivity convention is now a named frozen
    function (`scoring_3d.in_band`) with a DIRECT edge fixture
    (0.25 ∈ [0.25, 0.5]), and the mutant targets that line; the
    fragile round-trip test was reworked to a safely-interior point.
    Second full run: **KILLED 51/51, baseline clean** — every
    softening and hardening mutant dies, including the resurrected C1
    float-order defect and the retargeted band-edge misread.
    **Harness note:** the battery's first invocation (before any
    result) was killed by a 2-minute timeout mid-mutant and left the
    bucket-tail mutant ON DISK — caught immediately by the next suite
    run (the flipped tail is unmistakable: p .95 where 1/21 belongs)
    and reverted; the harness now writes a `.mutation_backup` before
    every mutation and self-heals stranded mutants at startup, so a
    killed run can never masquerade as a baseline failure again.

### Defect found at build and closed (the freeze's named attack
### surface, hit early)

**C1 float-summation order.** The first implementation summed H1
terms in character-first-occurrence order (dict insertion order), so
two answers in the SAME character-count partition could differ by
1 ulp — 'aabadc' vs 'dcbaaa' — silently splitting tie groups by an
accident of float addition (the committed battery's len-6 stratum
showed 9 "distinct" values where the partition structure has 7).
Closed by canonical sorted-order summation; the selection outcome is
unchanged (C1 wins with identical printed AUCs to 4 decimals; m_min,
λ, power unmoved at the printed precision); the kill-pair fixture
asserts bit-identity and the mutation battery carries the resurrected
defect as a mutant. The freeze session re-attacks the functional's
remaining degrees of freedom (log base, LZ78 conventions, tie
handling, the selection formula's freedom) per its standing
assignment.

### Doc slips found at build — LEDGERED FOR FREEZE RATIFICATION
### (no accepted dial touched; the doc stays as approved until Michael
### rules)

a. **§3 "fp16" → float32.** exp3's ledgered dtype policy samples
   probe sizes at fp32 exact upcast (cell_policy, inherited by 3c);
   gate 1 byte-compares against 3c's fp32-committed streams, so an
   fp16 tranche could not pool with the committed base under one
   generation law. The build codes float32 throughout; the doc's §3
   word "fp16" is a slip.
b. **§3 committed-fires list: item 436's answer is 'qvux'** (the
   question string is 'xuvq'; the doc lists the question string where
   every other entry lists the answer). All four candidates are
   anagram-invariant on this pair, so no number moves; the §3 texture
   sentence's "3 do not ('eyxh', 'fkjes', 'xuvq')" should read
   'qvux'.
c. **§5.4/§8 "10 of 13 committed fires are len-4" → 11 of 13** (1b:
   8 of 10; 410m: 3 of 3; and 7 of 9 distinct fired items are len-4).
d. **§6's illustrative "a single rank-1 fire gives p = 1/194 < .05"
   is impossible under the realized tie structure** — len-4 has no
   unique rank-1 (cheapest tied class = 45 items; a single len-4 fire
   can never do better than 45/194 = .23). The m_min MECHANISM is
   exactly as designed (computed from frozen ranks); the realized
   m_min = 1 arrives via len-6's unique-cheapest item at p = 1/151.
e. **§6 "expected |F| is 8–12" → computed 12.3** under the frozen
   observed-concentration alternative (14.8 flat); the doc's range
   came from 3c's rough fires→distinct conversion. Marginal, but the
   committed number is 12.3.

### Build dials frozen here that the doc delegated to the build
### (assembled for the freeze's ratification list)

λ rule + value (item 5 above); ctrl gate band (item 9); MC/power
seeds and the DP-cap crossover (item 7); the conditional ≥ .99
canonical-among-verified span bar (item 8); seed blocks of 4 as the
§10.4 durable/commit unit; harness.py added to the frozen pins
(item 10); the alternative-normalization reading (item 6).

### Next session (session 3 of 3): the adversarial freeze

Standing assignments: find the class defect; fuzz the verify
criterion for totality over the emission alphabet (stop-#1 rule); the
functional's degrees of freedom (one instance already found+closed at
build — assume more). Cold battery per FREEZE_CHECKLIST.md. Tag
`exp3d-preregistered` on Michael's ratification of the slips (a–e)
and the build-dial list; campaign launch is a SEPARATE go with the
per-block push cadence reconfirmed.

---

## 2026-08-18 — FREEZE SESSION (session 3 of 3), opened cold

Adversarial cold re-read of `experiment-3d-design.md` and every module
under `experiments/exp3d/` against the three standing assignments, then
the model-free cold battery. **Two findings of the named class found and
CLOSED; three disclosure items raised for ratification.** No accepted
dial touched; both closures are additive refusals (3c's freeze
precedent). Doc text left untouched pending Michael's ruling on slips
a–e.

### F1 (CLOSED) — `answer_type` was a verdict input resolved outside the pins

`load_new_cells_3d` took `answer_type` from the FIRST shard record and
passed it to the verify criterion, where it selects the normalization
branch — i.e. **what counts as a fire**. It was compared to nothing:
not across the six shards (`answers` and `items_sha256` were), not to
the committed item file's value (which `load_item_file` already reads
and nothing consumed), not to exp3/3c. **3c pinned exactly this field**
(`analyze_3c` check_shapes: `for field in ("answers", "probe_labels",
"answer_type")`) and 3d had dropped the leg — 3c finding A's shape one
level over.

Demonstrated executably before closure: flipping one of six shards to
`"number"` loaded clean and applied to all six blocks.

Severity, stated honestly: **not reachable through the real producer** —
`run_cell_3d` writes `cap["answer_type"]` from an item file whose sha it
checks against `ITEMS_SHA_PIN` before sampling. Note the
stored-vs-recompute tally check could never have caught it: runner and
analyzer read the same field, so both sides move together.

Closure (additive refusal, two legs): `answer_type` joins the
cross-shard identity comparison, and the resolved value is checked
against `answer_type_pin`, defaulting to `load_item_file(RUNG)
["answer_type"]` — the sha-pinned source. Synthetic worlds pass their
own pin, the `items_sha_pin` convention `load_scoring_3d` already uses.

### F2 (CLOSED) — gate 1's coverage was unpinned

`load_gate1_3d` validated `draws_compared == n_items × draws_per_seed`
— internal consistency only; `n_items` was checked as a positive int
and never against the battery. A truncated re-derivation would pass the
ZERO-TOLERANCE stream gate having compared a subset, and
`gate1_total_draws_compared` would report the short number. The
acceptance was fixtured in (`test_gate1_record_round_trips_through_
loader` builds an `n_items=20` record and asserts it loads).

Demonstrated before closure: a record hand-truncated to `n_items=3 /
draws_compared=192` — self-consistent — loaded clean.

Both sibling loaders pin their count (`load_new_cells_3d`,
`load_scoring_3d` each take `n_items=N_ITEMS`); this one had no such
parameter. 3c pinned it by cross-tree comparison (`if g["n"] !=
exp3_cells[key]["n"]`).

Severity: **not reachable through the real producer** —
`rederive_cell_3d` writes `n_items=len(answers)` = 500 and `diff_seed`
hard-errors on incomplete coverage in both directions.

Closure: `load_gate1_3d(root, *, n_items=N_ITEMS)` with a hard refusal
on mismatch; synthetic worlds pass their N.

### Ratification items raised by the freeze (no code change)

f. **The §7 concession's calibration sentence is true of ONE tail.**
   "FLAT row: P(reject) = .0482 ≈ α — the machinery is exactly
   null-calibrated" (ledger item 4) describes the STRUCTURED branch. The
   committed 1b FLAT row is STRUCTURED .0482 **and ANTI-STRUCTURED
   .0450**; the tree tests both tails in sequence, so under no signal
   **P(a directional verdict) = .0932**. Each direction calibrates at α;
   their union does not. ANTI-STRUCTURED is a preregistered world
   reported with equal prominence (§6), so this is a wording precision
   item, not a defect — the number is already in `power_3d.json`.

g. **The .2616 is selection-flavoured, which STRENGTHENS the
   concession.** The observed-concentration alternative puts rate mass
   ∝ (c_i + λ) on the same 13 fires that SELECTED C1, so the simulated
   truth and the predictor agree by construction. Power is therefore
   optimistic: ≤ .2616 against a fresh concentration, versus the .75
   bar. (Attacked separately and cleared: the λ dial cannot be accused
   of flattering — λ̂ = .0256 sits on the MORE powerful side of the
   committed grid, .374 @ .01 → .058 @ 1.0, and still declares
   underpowered.)

h. **m_min = 1 is realized at an in-sample item.** It comes from item
   200 'rxxxxd', the unique-cheapest len-6 answer, which is itself one
   of the 13 committed fires — so the single-fire rejection path is most
   likely a REPEAT ('ecde' already fired 4× across sizes). Formally
   valid (the null is over items, not fire history), but a THIN
   STRUCTURED verdict riding on item 200 would be a persistence event
   wearing a forecast's p-value, and §5.4 excludes persistence as a
   forecaster. Immaterial at the adjudicating cell (1b P(|F| ≤ 4) =
   .0022); material at 410m (.9234), which is non-gating and already
   annotated THIN. Proposed handling: a sentence in the verdict reading
   and the retrospective, no design change.

### Attacked and CLEARED (standing assignments, no action)

- **Verify-criterion totality (stop-#1 rule), fuzzed:** 81,026 draw-side
  inputs — the full 29-character Python whitespace class × the strip
  set, unicode (incl. the committed item-370 fire's ' eyxh?\n\nA: 现在'),
  lone surrogates, zero-width/format chars, empty and whitespace-only
  and newline-first draws, the no-leading-space verified class
  ('vezdlr'), 40,000 seeded random strings, and non-str JSON values —
  **0 escaped exceptions, 0 non-bool returns**, 7 scoring True (live).
  Proved by construction too: on a `str`, `normalize_answer` can raise
  only `IndexError`, from `s.split()[0]` when the string survives both
  strips as pure non-space whitespace ("'\t'" → "\t") — exactly the
  committed crasher class. Answer side stays hard, 3/3.
- **The functional's remaining degrees of freedom:** sorted-count
  summation makes same-partition strings bit-identical; len-4's two
  values (6.0 / 8.0) are exact in binary FP so the binary stratum
  carries no ulp risk; `-0.0` for an all-one-character answer compares
  and hashes equal to `0.0`; `math.log2` used consistently; the LZ78
  trailing-phrase convention matches its worked parses ('rxxxxd' →
  r|x|xx|xd = 4); the selection tie-chain is deterministic and never
  fired (margin .0006).
- **The exact null:** the convex-combination recurrence is correct, all
  coefficients in [0,1], and no mass is truncated (the max reachable sum
  for m items is ≤ smax by construction); the observed T always lies in
  the support, so the exact path cannot emit p = 0. m_min's best-case
  search is the true minimum (p_low is monotone in T at fixed
  composition, and the search minimises over both placement and
  composition).
- **The empty-fired path:** `stratified_rank_test` omits `thin` at
  |F| = 0, but `verdict_3d` computes `thin` locally and guards every
  `None` p; the UNSTRUCTURED branch (which formats p) is unreachable at
  |F| = 0 because m_min ≥ 1.
- **Frozen-order enforcement:** three layers confirmed. Noted: the
  analyzer enforces the RULES, not the temporal order — git's per-block
  commit history is the order record, as in 3c.

### Non-blocking observation

`scoring_3d.score_items` never rebinds `past`; correctness depends on
transformers' Cache being mutated in place across steps. True on the
pinned stack and the ctrl_copy known-answer gate would catch a
regression, but nothing asserts the cache length. Left as-is: adding an
assert is a change to a scoring path that cannot be exercised before
first model contact.

### Freeze cold battery (fresh processes, pycache cleared)

| item | result |
|---|---|
| fixture suite | **121 passed** (117 + 4 new F1/F2 fixtures) |
| mutation battery, both directions | **KILLED 56/56, baseline clean** (51 + 5 new) |
| full-shape worlds | **13 tests / 8 worlds**, all terminals |
| referent battery, real trees | **13/13** |
| `functional_selection_3d.json` | byte-identical `2a2c358e…` |
| `power_3d.json` | byte-identical `88a0b74c…` |
| `span_validation_3d.json` | byte-identical `c36e3714…` |
| `stream_map_3d.json` | byte-identical `55ff2294…`, both overlap laws |
| campaign dry-run | 6 tiers in the frozen §10 order |
| runner refusals, empty tree | scoring + sampling refuse BEFORE model load |
| verify totality fuzz | 81,026 inputs, 0 escapes |

The closures move no committed number: all four artifacts reproduce
byte-identically with the refusals in place, as pure refusals must.

**Harness lesson (ledgered, house-standard candidate):** the mutation
battery mutates repo sources IN PLACE, so nothing may run beside it.
Running the referent battery and full-shape concurrently with it early
this session produced three spurious failures that re-ran clean —
the battery is sequential-only, and a "failure" observed during a
mutation run is evidence of nothing. Related: three mutants came back
`[broken-target]` after the closures (two new ones whose bare
`if n != n_items:` pattern also matched the scoring loader's 12-space
occurrence, and the PRE-EXISTING cross-shard mutant whose target text
F1 had extended). All three retargeted; the harness naming
broken-targets rather than counting them killed is what caught it.

### Still open at the end of session 3

- Michael's ratification: slips a–e, the build-dial list, the §7
  concession line, and freeze items f–h above.
- Determinism fixture ×2 and the gate-1 rehearsal — both load a model,
  both held for his word.
- Tag `exp3d-preregistered`; campaign launch a SEPARATE go.
- One pre-committed change still UNSPENT.

### Sanctioned model contact (2026-08-18, on Michael's word)

**Determinism fixture ×2 — byte-identical three ways.** Two fresh
processes and exp3's committed reference all hash
`791ce4779c29b566ac3e3e0a78d2488df7257229e8dd7006a00b40eb0450f4cb`.
torch/transformers versions are serialized into the compared bytes by
design, so this is a stack-drift check as well as a determinism check:
**no drift since exp3.**

**Gate-1 rehearsal — IDENTICAL.** `rederive_cell_3d("410m")` against
3c's committed seed-8 reverse_string stream: **32,000/32,000 draws
byte-identical, n_diffs 0**, no diffs to disclose. The stream carries
the 410m 'ecde' fire, so a fire reproduced byte-for-byte. The record
attests committed-draws sha `b3422b4f…`, which equals both the file on
disk and the §4 literal pin — the finding-B loop closes in both
directions on real bytes. Stack torch 2.12.1 / transformers 5.13.0,
model_sha 9879c9b5, dtype float32.

This is the **fourth consecutive byte-identical reproduction** of the
committed streams on this stack (three through 3c, now 3d's).

It also gave the F2 closure its first live pass: the real producer
writes `n_items=500`, the new coverage pin accepted it, and the loader
then correctly demanded the still-missing 1b record — so the pin
refuses synthetic truncations AND admits the genuine article. The 1b
gate-1 half runs at campaign launch per §10's order; the 410m record is
kept as the campaign's own comparison made early (3c's precedent).

---

## 2026-08-18/19 — CAMPAIGN (launched on Michael's go)

**Complete in 448.4 min (7.5 h), zero attrition, zero stops.** Frozen
§10 order executed exactly: gate 1 → scoring → tranche, 410m before 1b,
seed blocks ascending. Preflight passed for both sizes at float32, and
both preflight artifacts reproduced BYTE-IDENTICALLY to exp3's
committed ones — a further stack-stability check nobody asked for.

### Gate 1 — both cells IDENTICAL

410m re-derived at the freeze (32,000 draws, 0 diffs); 1b at launch in
800 s (32,000 draws, 0 diffs). **64,000/64,000 draws byte-identical**,
the §10.2 requirement met exactly. Fourth and fifth consecutive
byte-identical reproductions of the committed streams on this stack.

### Scoring — both known-answer gates PASS

| cell | p̂ | committed r | band | p̂/r |
|---|---|---|---|---|
| ctrl_copy/410m | .6764 | .7992 | [.3996, .8192] | .846 |
| ctrl_copy/1b | .7382 | .8413 | [.4206, .8613] | .878 |

All four scoring cells reported **0 zero-probability items**, so the ℓ
arm has complete coverage and the `+inf` tie path the freeze attacked
is unexercised at both sizes.

The gate values are worth more than the PASS flags. Both land BELOW r,
which is the direction §5.5's mechanism requires (exp(ℓ) is
canonical-path prefix mass, so verified draws reached by a
non-canonical tokenization count in r but not in p̂), and the two
independently scored cells agree to within three points — .846 vs .878.
A per-cell scorer bug would not reproduce that agreement. The ~13% gap
is the concrete size of the lower-bound caveat the calibration arm
carries.

### Tranche — 13 new fires in 1,152,000 draws

Per block (descriptive; the analyzer recomputes everything from raw
draws at verdict time):
- 410m: s16–19 **1**, s20–23 **1**, s24–27 **2** → **4 / 384,000** =
  1.042e-5
- 1b: s16–19 **3**, s20–23 **2**, s24–27 **1**, s28–31 **2**,
  s32–35 **0**, s36–39 **1** → **9 / 768,000** = 1.172e-5

### Two observations, recorded before any verdict

1. **The 1b cell came in LOW.** 9 fires against 15 expected at the
   committed pooled rate — about a 7th-percentile Poisson outcome. The
   new-draw rate 1.172e-5 is almost exactly HALF exp3c's new-draw point
   estimate of 2.34e-5, and 3c's DEEPENS rested partly on that estimate
   running 3.0× exp3's. This does not touch 3c's verdict, which was
   adjudicated on its own committed draws under the asymmetry rule, but
   it is a downward regression on that figure and the retrospective
   should say so. Pooled 1b now **19/1,280,000 = 1.484e-5**.
2. **The two cells CONVERGED on new draws.** The committed base had 1b
   at 3.3× the 410m rate (1.953e-5 vs 5.86e-6); on new draws they sit
   within 12% (1.172e-5 vs 1.042e-5). Pooled 410m **7/896,000 =
   7.81e-6**. Whether that is noise or size-independence is a question
   for the retrospective, not something two cells can settle.

Consequence for the primary, stated in advance: |F| at 1b will land
below the committed E|F| of 12.3 — bounded above by 9. Still far above
THIN_MAX = 4 and m_min = 1, so no THIN qualifier attaches and the cell
can adjudicate; but a smaller fired set is a coarser rank test, so
realized power sits BELOW the .2616 already declared underpowered in
advance, on top of item g's selection-optimism.

This also largely retires freeze item **h**: the persistence hazard was
specific to a THIN rejection riding on in-sample item 200, and at
|F| ≈ 7–9 spread across strata no single item can carry the statistic.
Retired by the data, not by argument.

### Contamination discipline held

Per-block COUNTS were visible during the run (the runner prints them,
the watcher commits them — disclosed by design). **No fired-item
IDENTITY has been inspected by anyone at any point**, and the analyzer
has not been run. The §10.5 projection is therefore still writable
against an uncontaminated item-level record; counts constrain a
rank-order projection barely at all, addresses would constrain it a
lot.

### Durable cadence, verified

14 watcher commits (1 gate-1 + 4 scoring + 9 shard pairs; the 410m
gate-1 record rode in with the freeze commit). First watcher commit was
inspected live and carried exactly its one record. All 15 units on
disk, all committed, master in sync with origin throughout.

Watcher cosmetic note for the NEXT experiment, not fixed mid-campaign:
it names commits by bare basename, so the two gate-1 records both read
"reverse_string.json landed" and are distinguishable only by their
diff. Shards are unambiguous.

### Still open

- §10.5 **projection**, ledgered BEFORE the analyzer runs.
- Frozen analyzer runs ONCE on Michael's go → verdict + retrospective.
- One pre-committed change still UNSPENT.

---

## 2026-08-19 — PROJECTION (§10.5), ledgered BEFORE the analyzer runs

Drafted by Claude, approved by Michael's instruction ("ledger the data
then run the analyzer") and NOT amended by him — attribution recorded
precisely so the retrospective grades the right author. Committed and
pushed before `analyze_3d.run()` is invoked; git history is the proof
of ordering.

**Contamination position at the time of writing:** per-block fire
COUNTS were visible during the campaign (printed by the runner,
committed by the watcher — disclosed by design). **No fired-item
identity has been inspected, and the analyzer has not been run.** Counts
constrain a rank-order projection barely at all.

### Primary call

**UNSTRUCTURED** — |F| ≥ m_min with no rejection in either direction.

Odds attached, so the call is gradeable rather than hedged:
- P(UNSTRUCTURED) ≈ .70–.75
- P(STRUCTURED) ≈ .20–.25
- P(ANTI-STRUCTURED) < .05
- P(UNINFORMATIVE) ≈ 0 (m_min = 1, |F| ≥ 4 already guaranteed)

Reasoning, in order of weight:
1. Power at the observed-concentration alternative was **.2616**, and
   the realized |F| ≤ 9 against the assumed E|F| = 12.3 makes the
   realized figure LOWER still. An underpowered test's modal outcome is
   no rejection.
2. Item **g**: that .2616 is itself optimistic, since the alternative
   concentrates rate mass on the same 13 fires that selected C1.
3. C1's in-sample 1b AUC is only **.679** — modest even where it was
   fitted. The 410m .890 is the flattering half and 410m is non-gating.
4. The len-4 stratum is BINARY (45 repeat-class vs 149 all-distinct),
   and 11 of 13 committed fires are len-4, so most of the fired set
   lands in a stratum that can only say "repeat vs not."

### Gradeable sub-predictions

| # | prediction |
|---|---|
| P1 | 1b \|F\| lands in **7–9** inclusive |
| P2 | 1b verdict carries **no THIN** qualifier |
| P3 | 410m \|F\| ≤ 4 and its annotation **carries THIN** |
| P4 | **0 leak voids** across both cells |
| P5 | 1b p_low **> .05**, most likely in **.10–.60** |
| P6 | **≥ 1 new fire lands on a previously-fired item** (persistence; 'ecde' carried 4 of 13 committed fires) |
| P7 | the ℓ-arm rank test **also fails to reject** at 1b |
| P8 | Spearman(functional, ℓ-cost) **weakly positive, 0 to +.35** — the two tiers agree a little, not a lot |
| P9 | gate-1 total draws compared = **64,000**, 0 diffs (mechanical, but it is a verdict input) |

### Named disconfirmer

**If 1b p_low ≤ .05, this projection is WRONG at the verdict level** and
the retrospective says so without softening. A STRUCTURED result on a
test this underpowered would be the strongest single datum the program
has produced on signature 3 at item grain — and it would also mean I
mis-weighted C1's modest in-sample AUC.

Restated so the projection cannot claim credit either way: I am
predicting the null outcome of an experiment DECLARED UNDERPOWERED IN
ADVANCE. UNSTRUCTURED is the cheap call and deserves little credit if
it lands; STRUCTURED against these odds would be the informative one.

---

## 2026-08-19 — VERDICT: STRUCTURED (analyzer run once, on Michael's go)

**p = 1.622886e-04, |F| = 8, not THIN.** Full record in
`results/VERDICT.txt`; grading and thesis reading in
`results/retrospective.md`.

All 8 fired items landed in the len-4 stratum, binary by the freeze's
own printed tie structure: **7 of 8 in the 45-item repeat class**
against 1.86 expected — a 23.2× per-item rate ratio (7/45 = 15.6% vs
1/149 = 0.67%). T = 281.0 re-derived by hand as 7×23 + 1×120.
Persistence does NOT explain it: six of eight fired items had never
fired before, and five of the seven repeat-class fires are on items
with no prior fire — freeze item **h** retired on evidence.

410m: |F| = 4, p = .230357, same direction, THIN, non-gating.

Secondaries: ℓ arm p = 7.91e-09 (1b) / 4.32e-04 (410m),
Spearman(functional, ℓ-cost) = .878 — but exp(ℓ) approximates the
probability of emitting the answer and a fire IS that emission, so the
ℓ arm is closer to a consistency check than an independent forecast.
Decile bucket 3/8, p = .0377, diluted exactly as the freeze predicted
(20 of 45 tied items chosen by arbitrary index). Pooled updates:
1b 19/1,280,000 = 1.484e-05, 410m 7/896,000 = 7.813e-06.

Gates all clean: gate 1 64,000/64,000 byte-identical 0 diffs, both
ctrl gates PASS, 0 leak voids, 0 twin fires across 8 cells, determinism
byte-identical to exp3's committed reference. Campaign 448.4 min, zero
attrition. **Pre-committed change UNSPENT** through the entire
experiment.

**Projection MISSED at the verdict level** (`e5ae9c0`, sealed before
the run). Named disconfirmer fired. Sub-predictions 6 hit / 3 missed,
and the split is the finding: every hit was bookkeeping, every miss was
science. Graded in full in the retrospective.

**The transferable result: the power model was mis-SHAPED, not merely
pessimistic.** Declared underpowered at .2616, rejected at 1.6e-4. The
frozen alternative modelled ITEM-level concentration on the 13
committed fires; the truth is a CLASS-level contrast over 45 items — a
target ~6× larger. The λ sensitivity grid explored the wrong dimension
throughout. Successor rule proposed: when the tie structure is printed
at freeze, model the alternative in that structure's own terms.

**Thesis bearing (retrospective §5):** reverse_string at 410m/1b now
satisfies **all three signatures** — probeable (3b), elicitable (3/3c),
forecastable from below (3d) — the program's first complete case on a
real model. Stated with its limit: a live alternative survives (cheap
strings are a priori more probable, and answers sharing characters
with their own input are more reachable by copying), so 3d forecasts
which items are cheap to emit, not necessarily which the model
half-knows. The carve-out is untouched.
