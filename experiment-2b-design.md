# Experiment 2b — Design Doc: The Probe Ladder, Reservoir-Proofed (Prediction 2, second instrument)

**Status:** **DRAFT** — not frozen. Becomes Preregistered in a dedicated commit (tag `exp2b-preregistered`) only after (a) Michael's dial review of this doc, and (b) Experiment 2's formal closure (m2 report, attrition ledgered, INSUFFICIENT_DATA verdict recorded). Until that commit, everything here is revisable. After it: thresholds, the battery and its inclusion rules, and `experiments/exp2b/analyze.py` do not change; one mechanism-justified fix per failed gate, ledgered before the re-run (process rule 6).

**One-line purpose:** Same as Experiment 2 — test whether sub-threshold internals of small models carry the ordering information for which capabilities become reliable first with scale — with the instrument redesigned so that a lookup strategy scores chance **by construction**, closing the reservoir-floor confound that ended Exp 2.

**Why a 2b exists.** Exp 2's untrained-weights control fired on all 12 battery capabilities at both probe sizes (margins 0.20–1.00 at the permutation floor; `experiments/exp2/results/instrument_diagnostics.md`): at n≈2000 items and d≥1024, a linear readout on a random-but-fixed network decodes any deterministic function of the prompt's surface tokens. Group-split diagnostics showed the trained probes' ceiling margins were also lookup (trained mod7: 1.000 in-distribution → 0.009 on held-out operands). "Probe fires vs a permutation null" therefore cannot measure precursor structure in this regime. Exp 2 closed as INSUFFICIENT_DATA with the two-stage lock intact — **the eval-side models were never queried**, so the outcome of Prediction 2 remains unobserved and a redesigned test is still a genuine prospective prediction.

---

## 1. Hypothesis and logical structure

**Core hypothesis (to be preregistered at the freeze):**
> Across a battery of capabilities below reliability threshold at Pythia-1B, the ranking of capabilities by **basis-starved probe margin** (measured at Pythia-410M and 1B) positively rank-correlates with the ranking by argmax progress across Pythia-2.8B / 6.9B / 12B. The resolution view requires this; under capability-birth, sub-threshold internals carry no ordering information and the expected correlation is zero.

The falsifier is unchanged from Exp 2 and remains cheap and specific: starved-margin rankings that are noise with respect to the scale-ascent ordering (CI covering 0) falsify Prediction 2 as stated.

**What changed and why it is stronger, not just different.** Exp 2's probe asked "is the target *decodable*?" — answered "yes" by surface memorization. Exp 2b's probe asks "does the decoding *generalize across the surface basis*?" — a lookup table answers "no" by construction. This is closer to what Prediction 2 actually claims: partial-fidelity *computation* of the capability, not retrievability of its inputs.

**Relation to prior work.** As in Exp 2 (Schaeffer et al. 2304.15004; Hu et al. 2310.03262), plus the probing-methodology line this redesign operationalizes: Hewitt & Liang (1909.03368) on selectivity/control tasks; Voita & Titov (2003.12298) on MDL probes (considered, not adopted — §3 note). Verify all on arXiv before the freeze commit per working agreement.

---

## 2. Models and capability battery

### Models (locked decision, carried from Exp 2)

Same five SHA-pinned Pythia models (ledger, 40eca80), fp16 on MPS: probe side 410m/1b, eval side 2.8b/6.9b/12b. Rationale unchanged (one training distribution, only scale moves). The eval side is unqueried by Exp 2 — its cleanliness is an asset no alternative ladder has.

### The battery-design discipline (new, the heart of 2b)

Every candidate capability ships, in this doc, with **five declared fields**:

1. **Probe target** — the intermediate quantity the probe predicts.
2. **Surface basis** — the prompt tokens a lookup strategy would key on, analyzed against Pythia's actual BPE tokenization (Exp 2's add2 lesson: numbers tokenize into digit chunks, so operand-level splits do not starve digit-level bases).
3. **Starving split** — which basis values are held out of probe training; validation uses only held-out-basis items. Constructed so a lookup scores chance by construction.
4. **Composability analysis (the dumbest-baseline line item)** — written argument that the target is NOT linearly composable from sub-basis pieces shared across the split (per-digit, per-chunk, per-letter contributions). Targets failing this are **excluded on paper, before any data**.
5. **Feasibility counts** — frozen at battery generation (M0): ≥ 15 held-out basis values, ≥ 300 starved validation items, every probe class present in both train and starved-validation sets. A candidate failing the counts at generation is excluded and reported.

**Worked exclusions (the analysis doing its job in advance):** ones-column carry of 2-digit addition (digit-pair-local: ones(a)+ones(b) decides it; the 100-value pair basis is starvable but the target is then class-starved — excluded), digit-sum targets (linearly composable from per-digit embeddings), string-length targets (composable from per-chunk lengths), letter-counting targets (composable from per-chunk counts). Each was or would have been a reservoir gift in Exp 2's design.

### Candidate battery (30 candidates; scored battery = survivors of inclusion + gates, minimum 20)

Answer formats and item counts as in Exp 2 (≥500 eval / ≥2000 probe items, disjoint; 2-shot primary). Basis notation: "→ hold out" = starving split.

| # | Capability | Probe target | Surface basis → hold out | Composability note |
|---|---|---|---|---|
| 1 | (a+b) mod 7, 2-digit operands | a mod 7 | operand a values → 18/90 | mod-7 of a 2-digit number is digit-nonlocal |
| 2 | (a×b) mod 7 | a mod 7 | operand a values → 18/90 | as #1 |
| 3 | 3-digit addition | carry count (0–2, ones+tens) | (ones-pair, tens-pair) combos → 20/100 each | chain carry is pair-nonlocal through the chain |
| 4 | 3-digit subtraction | borrow count (0–2) | digit-pair combos → 20/100 | as #3 |
| 5 | GCD of two 2-digit numbers ∈ {1..12} | gcd class | operand pairs → both-operand holdout | gcd is jointly nonlocal |
| 6 | Divisibility by 7 (yes/no) | true divisibility bit | dividend values → 20% | digit-nonlocal |
| 7 | Binary→decimal (5–6 bits) | value mod 10 | bit-string values → 12/96 | value is nonlocal across bit positions |
| 8 | Day-of-week offset (N ≤ 499) | N mod 7 | N values → 20% | digit-nonlocal |
| 9 | Roman-numeral value (1–99) | ones digit of value | numeral strings → 20% | subtractive notation is sequence-nonlocal |
| 10 | Time arithmetic (min-add across hour) | hour-carry bit | minute-pair combos → 20% | carry across 60 is pair-nonlocal |
| 11 | Sorting 3 two-digit numbers | middle element's ones digit | number triples → value holdout | comparison chain; composability note reviewed at M0 (first-digit shortcut risk) |
| 12 | Word unscramble (4–6 letters) | first letter of solution | solution words → 20% | held-out word = unseen letter multiset |
| 13 | Caesar decode (k ∈ 1–5 stated) | first decoded letter | (first-cipher-letter, k) combos → 1–2 per class | letter-pair basis starved directly; classes covered by remaining combos |
| 14 | Alphabet offset ("3 letters after m") | result letter | (letter, offset) combos → 1–2 per class | as #13 |
| 15 | Acronym (first letter of 2nd word) | that letter | 2nd word's first BPE token → 20% of tokens | basis is the token, not the word (shared-prefix leakage) |
| 16 | Reversed random string | last letter of input | final BPE chunk values → 20% | last letter lives in the final chunk |
| 17 | Balanced parentheses (depth ≤ 3) | valid/invalid bit | paren strings → 20% | validity is chain-nonlocal |
| 18 | Category counting (6-word list) | count among first 3 (0–3) | member words → 20% of category vocab | membership for unseen words is semantic, not lookup |
| 19 | Odd-one-out (4 words) | odd word's position | member words → 20% | as #18 |
| 20 | Hypernym ("A robin is a …") | answer's first letter | cue nouns → 20% | semantic retrieval for unseen cues |
| 21 | Antonym retrieval | answer's first letter | cue words → 20% | as #20 |
| 22 | Rhyme choice (4 options) | answer position | cue words → 20% | rhyme for unseen cues requires phonology |
| 23 | Plural formation (irregular/regular mixed 50/50) | irregularity bit (0/1) | nouns → 20% | irregularity of unseen nouns is lexical knowledge, not lookup |
| 24 | Past-tense formation (irregular/regular mixed 50/50) | irregularity bit (0/1) | verbs → 20% | as #23 |
| 25 | Country → capital | capital's first letter | countries → 20% | semantic; inclusion rule may eject (above threshold) |
| 26 | Month offset ("2 months after March") | result month | (month, offset) combos → 1–2 per class | 36-combo basis starved directly |
| 27 | 3-hop deduction (A>B>C>D ⟹ A?D) | middle term (B or C, fixed rule) | entity-name assignments → 20% of name pool | relational, name-nonlocal |
| 28 | Entity tracking, 3 transfers | holder after 2nd transfer | name-role assignments → 20% of name pool | harder variant of Exp 2's (which was above threshold); M0 reviews leakage via positional name statistics |
| 29 | Units conversion (metric) | factor's power of 10 | unit pairs → 3/15 | small basis; feasibility counts decide at M0 (flagged at-risk) |
| 30 | Letter-position parity ("is 'k' in the first half of the alphabet?") | the bit | letters → 5/26 | single-letter basis, starved directly; at-risk for class starvation, M0 counts decide |

**Inclusion criteria (carried from Exp 2, fresh runs):** CP-95% upper bound on normalized argmax margin < 0.25 at pythia-1b; machine-verifiable oracle scoring 100% on committed items; oracle parses question text only. All 30 candidates get fresh M1 inclusion runs in Exp 2b's own record (Exp 2's M1 measurements are cited as expectations, not reused as data).

**Positive control (gate, not scored):** ctrl_copy only (measured reliable at both probe sizes in Exp 2 M1: 0.994/1.000). ctrl_next_letter is dropped on Exp 2's M1 measurement (0.338 at 410m — the "known reliable" design assumption was empirically false). **Known-present gate capabilities (§4):** entity-track-2-transfer (Exp 2 form, 1b argmax margin 0.951) and ctrl_copy.

---

## 3. Operationalizations

Normalized margins throughout, m = (acc − floor) / (1 − floor), floors measured empirically (untrained controls), CP bounds on everything, never a claimed zero.

### Stage 1 instrument (the predictor)

**Primary, scored: basis-starved probe margin.**

- Linear probes (StandardScaler + logistic regression, C=1.0, max_iter=100 — the ledgered Exp 2 benchmark carries over) on residual-stream activations at the frozen candidate family: every 3rd layer + final, × 2 positions (question-end token, last prompt token).
- **Split:** per capability, the starving split from §2 — probes train on kept-basis items, validate ONLY on held-out-basis items. The split is deterministic per seed (5 seeds re-draw which basis values are held out; process rule 5).
- **Null:** label-permutation null with N_PERM = 2500 refits under the identical group split, Bonferroni across the candidate family (floors 18/2501 ≈ .0072 at 410m, 14/2501 ≈ .0048 at 1b — reachable against α = .01).
- **Margin** = (starved-val acc − null mean) / (1 − null mean), set to 0 below the significance bar. Probe score per capability = seed-mean, then mean over the two probe sizes. Probe ranking = capabilities ranked by probe score.
- **Implementation note:** the frozen Exp 1 probe module does not support caller-supplied group splits; per the never-edit rule, Exp 2b adds a NEW function (`probe_starved`, in `experiments/exp2b/`) reusing the frozen `stats` primitives (permutation_null, bonferroni, clopper_pearson) unchanged. The new function is validated by the known-answer gates (§4) before any scored use.

**Secondary, descriptive, never scored: in-distribution selectivity gap** — trained minus untrained margin under Exp 2's original random splits, computed from the same activations at zero marginal collection cost. Reported for continuity with Exp 2's diagnostics; known to saturate on easy surface targets; cannot affect the verdict.

**Not adopted:** MDL/online-codelength probing — a lookup strategy still compresses after covering the basis vocabulary, so it prices the reservoir floor without removing it; adds machinery without closing the confound (YAGNI).

### Eval side (the outcome) — verbatim from Exp 2

Scale-ascent score = mean normalized argmax margin across 2.8b/6.9b/12b on the full ≥500-item eval sets, CP bounds, empirical untrained floors, no fitted crossings or extrapolated quantities. Descriptive "reliable-at" secondary unchanged. 500 items keep score differences ≥ 0.1 at > 4σ from noise.

### Two-stage measurement lock — verbatim from Exp 2

Stage 1 probe scores committed AND tagged before any 2.8b+ query. Battery membership frozen when Stage 1 begins; later item-quality failures are attrition, never replacement.

---

## 4. Gates (all calibrated — no zero-tolerance rules on nonzero-rate tests)

Exp 2's shuffled-label gate aborted on a statistically expected event (one floor-rate fire in 120 fits; E ≈ 0.86, P(≥1) ≈ 0.58). Every 2b gate states its expected false-fire arithmetic and a binomial tolerance.

1. **Known-absent gate (replaces Exp 2's binary attrition rule):** untrained-weights probes under the identical starving splits, all capabilities, both sizes, 5 seeds. Expected fires = F × family/(N_PERM+1) where F = total fits (at n=30: F = 300, E ≈ 1.8). **Gate passes** if observed fires are consistent with the floor rate (one-sided binomial p ≥ .01) AND every fire is a floor-signature fire: p at the add-one floor AND observed accuracy within 3 SD of the permutation-null mean (`probe_starved` records the null SD per fit for exactly this check — Exp 2's roman/seed3 fluke, acc 0.150 vs null 0.100 ± 0.015, would fail the 3-SD check and correctly read as a leak if it recurred at that magnitude on a starved split; on Exp 2's non-starved split it was a fluke because lookup was available to the null too). A fire with accuracy structurally above the null is a real leak: that capability is dropped (attrition, battery re-committed, not the one-change budget) — expected to be RARE now, by construction, rather than universal as in Exp 2.
2. **Known-present gate (new):** on trained weights, entity-track-2-transfer and ctrl_copy must clear the starved-split bar with seed-majority (≥3/5) at both sizes and seed-mean starved margin ≥ 0.2 at 1b. An instrument that cannot see capabilities that plainly exist is broken (process rule 2). Failure = gate failure for the one-ledgered-fix process.
3. **Shuffled-label control:** trained activations, rng(1000+seed) label shuffles, same binomial tolerance as gate 1 plus the floor-signature check per fire. Structurally-above-null fire = pipeline abort, as before.
4. **Positive control, argmax side:** ctrl_copy argmax ≥ 0.9 at both probe sizes (measured 0.994/1.000 in Exp 2 M1).
5. **Attrition floor:** if gates + inclusion drive the scored battery below **n = 20**, the verdict is INSUFFICIENT_DATA — never a smaller test, never a loosened gate.

---

## 5. Preregistered pass/fail and statistics

**Frozen at the freeze commit alongside `experiments/exp2b/analyze.py`.**

- **Primary statistic:** Spearman ρ (average-rank ties) between starved-probe ranking and scale-ascent ranking.
- **Test:** one-tailed MC permutation (10⁵, seeded), H₁: ρ > 0.
- **PASS:** exact p < **0.01** AND point ρ ≥ 0.5. At n = 24–30 the null SD of ρ is ≈ 0.19–0.21, so ρ = 0.5 sits ≈ 2.4–2.6σ from the null — the redesign's statistical payoff over Exp 2's 1.7σ bar, bought with battery size, not looser criteria.
- **FAIL (the falsifier):** bootstrap 95% CI on ρ (10⁴ case resamples, seeded) includes 0.
- **INDETERMINATE:** neither; reported with the CI; no post-hoc slicing.
- **INSUFFICIENT_DATA:** n < 20 (verdict precedence as in Exp 2: INSUFFICIENT_DATA → FAIL → PASS → INDETERMINATE).
- **Power (normal-approximation estimates, design-time):** at n = 27: true ρ = 0.6 → ~0.8; ρ = 0.7 → ~0.97; ρ = 0.8 → ≈ 1. Exact MC power table computed and committed with the freeze (before any data), replacing these approximations.
- **Descriptive secondary (carried from Exp 2):** restricted-ρ over capabilities with scale-ascent > 0.05, with subset n; never alters the verdict.
- **Dumbest-baseline line item (now a standing rule):** every criterion in this section carries a written analysis of what a lookup table / random network / majority class scores against it. For the primary: a reservoir strategy scores starved-margin 0 by construction (§2), so the correlation input for a structureless capability is a zero-margin tie, not a spurious rank.

### What a PASS does and does not claim — verbatim from Exp 2 §4, plus:

A PASS additionally does not claim the starved margin isolates *all* non-lookup structure — only that it excludes the lookup family the splits starve. The discussion must say so.

---

## 6. Run plan, compute, and distribution

Code in `experiments/exp2b/` mirroring exp2's layout (ledger from day zero, durable resumable detached campaigns, per-unit JSONs, skip-if-exists). Frozen modules imported via the exp2 alias-loading pattern (no sys.path shims — the shadowing lesson, commit 018cde3).

**Order (each stage gates the next):**

1. **M0:** battery item files + oracles + feasibility counts + starving-split definitions committed; `analyze.py` + MC power table frozen; **freeze commit + tag `exp2b-preregistered`** (after Exp 2 closure and the dial review).
2. **M1 (inclusion):** argmax at 410m/1b, all 30 candidates + controls → scored battery fixed, reviewed commit.
3. **M2 (gates):** §4 gates 1–4, in that order. Resolved before Stage 1.
4. **M3 (Stage 1):** starved probes at 410m/1b, 5 seeds → probe scores committed AND tagged.
5. **M4 (Stage 2):** argmax at 2.8b/6.9b/12b.
6. **M5:** frozen analysis; verdict; report.

**Compute.** GPU stages (collection, eval) on the Mac mini's MPS as before; 12b eval is the long pole (~500 × ~25 × 12b ≈ 2–4 days detached). CPU probe fitting is the bottleneck: ~920 fit-units (30 caps × 5 seeds × 2 sizes × 3 probe stages + controls) at the MEASURED contention-adjusted unit cost (Exp 2: ~1.4 h/unit effective at 8 workers on the M4 Pro — the solo benchmark underestimates by ~3×; first parallel run is the calibration run).

**Distributed probe fitting (new):** llmbox and atom boxes join as CPU workers (DGX Sparks remain off-limits). Mechanics: activations rsync out, per-unit result JSONs rsync back; the per-unit skip-if-exists layout makes the merge trivial and idempotent. **Determinism gate per box:** identical pinned environment (Python 3.11, numpy/sklearn versions locked in a committed requirements file) and a known-answer fixture fit whose accuracy counts must reproduce the Mac reference exactly before a box's results count; each result JSON records its hostname. A box failing the gate is excluded, not debugged mid-campaign. Target: probe program in days, not weeks.

---

## 7. What Exp 2's record contributes (data reuse policy)

- **Measured reservoir floors** (in-distribution untrained margins, 12 caps × 2 sizes × 5 seeds) — cited as design inputs and expectations; not reused as 2b data.
- **M1 argmax table** — expectations for reused capabilities; 2b runs its own inclusion.
- **Trained/untrained activations for the 12 Exp 2 caps** — MAY be reused for pre-freeze instrument rehearsal (probe-side only; the two-stage lock protects the outcome), and this rehearsal is encouraged: the known-answer gates should be dry-run on Exp 2's collected activations before the freeze, so gate thresholds (§4) are set with eyes open. Any such rehearsal is ledgered.
- **Nothing eval-side exists** — Exp 2 never queried 2.8b+; Stage 2 stays prospective.

---

## Open items before the freeze

- Dial review of this draft with Michael (battery composition, gate tolerances, PASS bar).
- Exp 2 formal closure (m2 report → attrition ledger → closeout commit).
- ~~arXiv verification of the two new methodology citations.~~ Closed at drafting: 1909.03368 (Hewitt & Liang, "Designing and Interpreting Probes with Control Tasks") and 2003.12298 (Voita & Titov, "Information-Theoretic Probing with Minimum Description Length") verified on arXiv 2026-07-17.
- Pre-freeze rehearsal of gates 1–2 on Exp 2's collected activations (§7); thresholds adjusted only in this window, ledgered.
- Feasibility counts at M0 may eject candidates (#11, #28, #29, #30 flagged); the 30-candidate reserve exists so ejections land the scored battery at n ≥ 24.
- MC power table computed and committed with the freeze.
- **Probe-target siblings for dial review:** #1/#2 share the identical probe target (a mod 7) and #3/#4 are near-siblings (carry/borrow counts) — their Stage 1 scores will be correlated measurements, a mild pseudo-replication in the correlation's effective n. Options for the review: diversify the targets, keep one of each pair as scored + one as reserve, or accept with the correlation caveat stated. Decision belongs to the dial review, not to silent drafting.
