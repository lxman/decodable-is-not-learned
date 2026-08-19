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
   FLAT row: P(reject) = .0482 ≈ α — the machinery is exactly
   null-calibrated. 410m (non-gating): power .0556; P(|F| ≤ 4) = .92,
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
