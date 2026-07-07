# Experiment 2 — Design Doc: The Probe Ladder (Prediction 2)

**Status:** **Preregistered** — frozen 2026-07-07 in this dedicated commit (tag `exp2-preregistered`), before any model query. The dial review that preceded the freeze is recorded in the ledger and landed in 347936c. From this commit on: thresholds, the battery and its inclusion rules, and `experiments/exp2/analyze.py` do not change. A failed gate permits at most one mechanism-justified fix, locked in the ledger before the re-run, never touching thresholds (process rule 6); the untrained-control attrition rule in §3 operates as preregistered, not as an edit. Written against the process rules in `experiments.md` (carried forward from Experiment 1); each rule's application is called out where it bites.

**One-line purpose:** Test the thesis's most original prediction on real models — that a linear probe applied to *small* models, below the capability threshold, already contains the ordering information that determines which capabilities become reliable first as scale grows. The phase-transition view gives no reason for this correlation to exist; the resolution view requires it.

Unlike Experiment 1, this experiment **tests the thesis**. It uses the instrument Exp 1 validated (the same frozen probe module, the same empirical-floor methodology) on models where nobody knows the answer in advance.

---

## 1. Hypothesis and logical structure

**Core hypothesis (preregistered):**
> Across a battery of capabilities that are below reliability threshold at Pythia-1B, the ranking of capabilities by below-threshold linear-probe margin (measured at Pythia-410M and 1B) positively rank-correlates with the ranking by argmax progress across Pythia-2.8B / 6.9B / 12B. Under the resolution view this correlation is required: probe margin measures how strongly the training distribution's structure is already represented, and that latent strength is what argmax reliability later surfaces. Under the capability-birth view, small-model internals for a capability that "does not exist yet" carry no ordering information, and the expected correlation is zero.

**Why this is the sharpest available test.** Exp 1 showed detectability-below-threshold tracks whether structure exists in the data, on ground truth we constructed. Exp 2 asks the same question where the ground truth is the Pile and the "construction" is whatever structure natural data actually contains. A positive result means emergence-order is *readable in advance* from models too small to perform the capabilities — cause running ahead of the detection event, exactly as the essay's inversion claims.

**The falsifier is cheap and specific.** If probe rankings at 410M/1B are noise with respect to the scale-ascent ordering (correlation ~0, CI covering 0), Prediction 2 is wrong as stated and the essay's claim that "the capability is present at partial fidelity before the jump" loses its most direct support. Publishable either way; the design treats the null respectfully (see §4 power analysis).

**Relation to prior work.** Schaeffer et al. (arXiv:2304.15004) showed metric choice manufactures discontinuities; Hu et al. (arXiv:2310.03262) showed pass-rate resolution reveals smooth progress. Both are about *measuring the surface behavior better*. Exp 2 is different in kind: it reads *internal* state of *smaller* models and predicts the *ordering* at scales those models have never seen. Nobody has done this.

---

## 2. Models and capability battery

### Models (locked decision)

The **Pythia suite** (arXiv:2304.01373), standard (non-deduped) branch, final checkpoints (`main` revision), fp16 on MPS:

- **Probe side (below threshold):** `pythia-410m`, `pythia-1b`.
- **Eval side (scale ascent):** `pythia-2.8b`, `pythia-6.9b`, `pythia-12b`.

Rationale: every model trained on the same data in the same order — the training distribution is *held fixed* while only scale moves, which is precisely the thesis's experimental frame (same structure, lenses of increasing fidelity). 12B fp16 ≈ 24 GB of weights, validated comfortable on the 48 GB Mac (`environment.md`).

### Capability battery

**Inclusion criteria (preregistered; applied before any probing):**

1. **Below threshold at the probe scales:** Clopper–Pearson 95% *upper* bound on normalized argmax margin (see §3 for the margin definition) **< 0.25 at pythia-1b**. A capability already half-formed at 1B would let the probe read the behavior rather than the latent structure — the probe must run genuinely below threshold, as in Exp 1.
2. **Machine-verifiable answers** with a closed-form verifier (no LLM judging), and a defined **intermediate quantity** for the probe target (§3).
3. **Well-formed items:** an oracle solver scores 100% on the item set (known-answer check on the battery itself).

**Candidate battery (16 candidates; the scored battery is whichever survive inclusion, in this fixed order, minimum 10):**

| # | Capability | Probe target (intermediate quantity) | Answer format |
|---|---|---|---|
| 1 | 2-digit addition (carry mixed 50/50) | carry bit of the ones column (0/1) | number |
| 2 | 3-digit addition | number of carry operations (0–3) | number |
| 3 | 2-digit multiplication | ones digit of the product (0–9) | number |
| 4 | Modular addition, (a+b) mod 7 | first operand mod 7 (0–6) | number |
| 5 | Parity of 8–12-bit strings | parity of the first half of the string (0/1) | "even"/"odd" |
| 6 | Word unscrambling (4–6 letter anagrams) | first letter of the solution word | word |
| 7 | Entity tracking (3 entities, 2 transfers) | holder after the FIRST transfer (mid-episode state) | name |
| 8 | 2-hop deduction (A>B, B>C ⟹ A?C) | the shared middle term | name |
| 9 | First-letter acronym construction | first letter of the 2nd word | letters |
| 10 | Reversed-string reading (random 4–6 letters) | first letter of the input string | word |
| 11 | Roman-numeral addition (values 1–99) | ones digit of the first numeral's value (0–9) | number |
| 12 | Alphabetical ordering (4 words) | list position of the answer (1–4) | word |
| 13 | Units conversion (metric, 1-step) | the conversion factor's power of 10 (1–3) | number |
| 14 | Day-of-week offset (day + N days, N ≤ 499) | N mod 7 (0–6) | day name |
| 15 | Counting category members in a 6-word list | category count among the first 3 words (0–3) | number |
| 16 | Caesar-shift decode (shift k ∈ 1–5, k stated) | first letter of the decoded word | word |

Item-construction decisions made at implementation and locked with the files (M0):
random strings rather than dictionary words for #10 (a memorized word-reversal
lookup can't substitute for the manipulation, and the unique-question space stays
large); question spaces widened where 2500 unique items demanded it (#5 string
length, #11 value range, #14 offset range, #16 shift range); first-letter probe
targets sampled letter-stratified over letters with support in both splits, so no
probe class falls below ~30 examples; #12's probe target is the answer's list
position (balanced by construction) rather than its first letter. The two positive
controls have small question spaces and allow duplicate items — they are gates,
not scored data. The battery generator's oracle recomputes every answer from the
question TEXT alone (independent of the generator's sampled variables), and the
oracle-agreement test runs against the committed files.

Battery reputations deliberately staggered: several have documented "emergent" jumps in the BIG-bench/emergent-abilities literature (unscrambling, multi-digit arithmetic, modular arithmetic), several are believed smooth. The exact item sets (≥ **500 eval items** and ≥ **2000 probe items** per capability, disjoint), prompt templates (fixed, one per capability, zero-shot + 2-shot variants with the 2-shot as primary), and verifiers are committed in `experiments/exp2/battery/` **before any model is queried** (process rule 1: the operationalization is the item file, not a description of it).

**Positive controls (gates, excluded from the scored correlation):** two capabilities known reliable already at 410M (exact-copy of a short string; next letter of the alphabet). The pipeline must show both: probe fires AND argmax reliable at every size. A pipeline that can't detect a capability that is plainly present is broken (process rule 2).

---

## 3. Operationalizations

All continuous quantities are **normalized margins** so capabilities with different chance floors share a scale:

> m = (acc − chance) / (1 − chance), with chance measured **empirically** per capability from an untrained-weights control model (Exp 1's lesson: never assume the theoretical floor), reported with CP bounds.

### Probe side (the predictor)

The **frozen Exp 1 probe module** (`signatures/probe.py`: StandardScaler + logistic regression, label-permutation null, Bonferroni across layer×position) applied to residual-stream activations of pythia-410m and pythia-1b at the last prompt token and the capability's designated intermediate-quantity position:

- **Probe margin** per (capability, model) = best cross-validated normalized probe margin across layers, at the frozen Bonferroni-corrected significance bar (p < 0.01). Probes failing the significance bar score margin 0 (not excluded — "no signal" is ordering information).
- **Probe score** per capability = mean of the two models' probe margins.
- **Probe ranking** = capabilities ranked by probe score.
- **Controls (process rule 2, run before scored probing):** (a) the same probes on randomly-initialized 410M/1B weights must NOT beat the permutation null on any scored capability (catches tokenizer/surface leakage — a probe that fires on an untrained model is reading the prompt, not the model); (b) shuffled-label probes must fail everywhere; (c) probe train/test splits are item-disjoint and template-disjoint (Exp 1's entity-split discipline).
- **Untrained-control attrition rule (fixed now, before any gate runs):** an untrained-weights probe beating the null on a capability **drops that capability from the scored battery** — reported as attrition, battery re-committed before Stage 1. This is a property of that capability's probe target (surface leakage), not a pipeline defect: it neither aborts the campaign nor spends the one-pre-committed-change budget. A shuffled-label failure anywhere, by contrast, remains a pipeline abort. Flagged in advance as most at risk: **mod7** ("first operand mod 7"), **reversed-string** ("first letter of the input"), and **acronym** ("first letter of the 2nd word") are pure functions of a single prompt token, and random-but-fixed embeddings propagate token identity well enough that an untrained-model probe may decode them. Their computed-intermediate peers (carry counts, unscramble/Caesar first letters) are the targets the control is meaningful for. If attrition here drives n below 10, the verdict is INSUFFICIENT_DATA per §4 — not a loosened control.
- **Seeds (process rule 5):** 5 probe seeds (split + initialization) per (capability, model); the margin is the seed-mean; seed scatter reported.

### Eval side (the outcome)

- **Scale-ascent score** per capability = mean normalized argmax margin across pythia-2.8b, 6.9b, 12B, each measured on the full ≥500-item eval set with CP bounds. This is a continuous "how early/strongly does it climb" measure using only *measured* points — no fitted crossing, no extrapolated threshold (process rule 3: the S3 lesson — no criteria on extrapolated quantities).
- **Scale-ascent ranking** = capabilities ranked by scale-ascent score.
- **Descriptive secondary (not scored):** smallest size whose CP-95% lower bound on m exceeds 0.5 ("reliable at"), with never-reliable ranked last — reported for interpretability, not part of pass/fail (it is heavily tied and coarser than the primary).
- **Sample size (process rule 4):** 500 items put the chance-level σ of m̂ at ≈ 0.022 for a mid-range chance floor, so the score differences the ranking depends on (≥ 0.1) sit > 4σ from noise; item counts may rise, never fall, before measurement begins.

### Two-stage measurement lock (anti-garden-path)

Stage 1 (probe side) completes and its per-capability probe scores are **committed to git** before any eval-side model (2.8B+) is queried. The prediction is thereby on the record before the outcome exists. Battery membership cannot change after Stage 1 begins (a capability failing item-quality checks mid-run is reported as attrition, not silently replaced).

---

## 4. Preregistered pass/fail and statistics

**Frozen once this file is committed. One analysis script (`experiments/exp2/analyze.py`) committed alongside, not edited after data collection.**

- **Primary statistic:** Spearman rank correlation ρ between the probe ranking and the scale-ascent ranking over the scored battery.
- **Test:** one-tailed exact permutation test (all battery permutations or 10⁵ Monte-Carlo, seeded), H₁: ρ > 0.
- **PASS:** p < 0.05 **and** point estimate ρ ≥ 0.5. (With n = 12 the p < 0.05 critical value is ρ ≈ 0.50; the conjunction keeps the bar meaningful if attrition shrinks n.)
- **FAIL (reportable, the falsifier):** bootstrap 95% CI on ρ (case resampling, seeded, 10⁴ draws) includes 0.
- **INDETERMINATE:** neither (e.g., positive but weak) — reported as such with the CI; no post-hoc battery slicing to rescue it.
- **Power (computed at design time, before data):** with n = 12 and true ρ = 0.8, one-tailed α = 0.05 power ≈ 0.9; at true ρ = 0.6, power ≈ 0.6. The battery reserve (§2) exists to keep n ≥ 10; below n = 10 the verdict is INSUFFICIENT_DATA, not a smaller test.
- **Known limitation, stated in advance (process rule 4 caveat):** the ≥4–5σ decision-bar discipline from Exp 1 applies here to per-capability *measurement* (500 items put score differences > 4σ from noise), but cannot apply to the correlation test itself: the null SD of ρ is ~1/√(n−1) ≈ 0.30 at n = 12, so the PASS bar sits ~1.7σ from the null and a true-null world passes ~5% of the time. That is a battery-size ceiling (a 4σ correlation bar would need n ≈ 30+ capabilities), accepted openly rather than papered over. Mitigations already in the design: the exact permutation p is always reported (never just "p < 0.05"), and FAIL takes precedence over PASS (a bootstrap CI covering 0 vetoes a nominal pass).
- **Descriptive secondary #2 (preregistered here, never scored):** ρ recomputed over the subset of capabilities whose scale-ascent score exceeds **0.05** (~2.3σ of the 500-item noise floor — "has measurably begun climbing by 12B"). Rationale: capabilities still flat at 12B (plausible for several battery members — parity is famously flat well past this scale) contribute noise-rank ties that drag the primary ρ toward 0, so a null result could mean "Prediction 2 is wrong" *or* "Pythia's range is too short to spread the outcome." This diagnostic separates the two readings. It is computed in `analyze.py` (frozen alongside the primary), reported with its subset n, and can never alter the verdict — the primary stands regardless.
- **One pre-committed change rule (process rule 6):** if the pipeline (not the hypothesis) fails a gate, at most one mechanism-justified fix, locked in writing before the re-run; its justification may not reference the correlation it would produce.
- Every "zero-looking" rate reported as a CP bound, never as a claimed zero.

### What a PASS does and does not claim

PASS = emergence *ordering* at 2.8B–12B is predictable from sub-threshold internals at ≤1B, on the Pile distribution. It does not claim the ordering is predictable at frontier scale, and it does not by itself distinguish "structure strength in data" from any correlated notion of task easiness — the essay's frame is precisely that these are the same variable (resolution required), and the discussion section must say so plainly rather than overclaiming.

---

## 5. Run plan and compute

Code in `experiments/exp2/` mirroring Exp 1's layout (PROGRESS.md ledger from day zero — process rule 8; durable, resumable, detached campaigns — process rule 7). The signature library is imported from `experiments/exp1/signatures/` unchanged; any change to it for Exp 2 needs is a new function, never an edit to the frozen ones.

**Order (each stage gates the next):**

1. **M0:** scaffold + battery files + verifiers + oracle known-answer checks; `analyze.py` frozen and tagged.
2. **M1 (inclusion):** argmax at 410M/1B on all 16 candidates + positive controls → scored battery fixed and committed.
3. **M2 (gates):** untrained-weights probe control (per-capability attrition rule, §3 — a firing control drops that capability, re-commit the battery), shuffled-label control and positive-control probes (these must land as predicted; a failure is a pipeline abort). All resolved before Stage 1.
4. **M3 (Stage 1, probe side):** probes at 410M/1B, 5 seeds; probe scores committed.
5. **M4 (Stage 2, eval side):** argmax at 2.8B/6.9B/12B.
6. **M5:** frozen analysis; verdict; report.

**Compute:** all inference, no training. Probe side: activation collection for ~2000 items × ~14 capabilities × 2 small models — hours. Eval side: ~500 items × ~14 × 3 large models; 12B on MPS is throughput-bound (~single-digit tok/s) but answers are short — the 12B pass is the long pole, estimated 1–3 days of detached background wall-clock. Fits alongside Exp 1's M6 campaign only if serialized; eval-side runs start after M6 finishes (one MPS device). DGX Sparks untouched.

---

## Open items before first run — all closed at the freeze

- ~~Write the 16 battery item files + verifiers + oracle checks.~~ Closed at M0: 18 committed item files (16 candidates + 2 positive controls), oracle-agreement enforced by tests against the committed files.
- ~~Freeze `experiments/exp2/analyze.py` alongside this doc.~~ Closed: dial-review revisions in (347936c), 110 tests passing, pinned by the `exp2-preregistered` tag on this commit.
- ~~Verify Pythia revision pinning and record exact model SHAs in the ledger.~~ Closed 2026-07-07: all five models staged, `main`-revision SHAs in the ledger (40eca80); run code loads by SHA.
- **Still pending by design:** the two-stage lock executes when Stage 1 completes — probe scores committed and tagged before the first 2.8B+ query. The M1 inference harness is built post-freeze (mechanics, not dials); the M2 known-answer gates certify it before anything scored.
