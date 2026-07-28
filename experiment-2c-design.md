# Experiment 2c — Design Doc: The Probe Ladder on a Screened Battery (Prediction 2, third instrument)

**Status:** DRAFT — dial review completed 2026-07-28; five structural
dials accepted in discussion (ledger: this doc's acceptance commit).
NOT frozen. The freeze is a dedicated commit + tag
`exp2c-preregistered` after the open items in the final section close,
per the process rules in `experiments.md`. Until then nothing here
binds; after it, thresholds, battery membership rules, and
`experiments/exp2c/analyze.py` do not change, one ledgered
mechanism-fix per failed gate, never touching thresholds.

**Inheritance:** the instrument enters CERTIFIED per Exp 2b gate-review
ruling (a) (gate 2 pass, gate 3 clean-by-count) — no re-validation.
The five standing rules promoted at 2b's closeout are load-bearing
here: untrained screening at inclusion; per-capability binomial rate
tests; mechanism-calibrated signature bars; adjudication code frozen
WITH fixture tests; pre-freeze gates adjudicated pre-freeze.

---

## 1. Hypothesis and logical structure

**Hypothesis (Prediction 2, carried from Exp 2b §1):** basis-starved
probe margins measured at sub-threshold scales (410m, 1b) rank-predict
the scale-ascent ordering — which capabilities appear earlier as the
same-distribution model family grows through 2.8b/6.9b/12b. Predictor
= Stage 1 starved margin (§3). Outcome = scale-ascent score (§3).

**What 2c changes structurally: the unit inventory.** The battery is
organized as difficulty families — task shapes with a dial (digit
count, modulus, composition depth) — each contributing 2–3 rungs, plus
singleton families. The primary claim stays at rung level with
inference that treats families as the independent units (§5). A
within-family secondary is preregistered as descriptive only: below
threshold, a family's rungs should show margins ordered against
difficulty and ascent scores ordered with it; per-family concordance
reported, never verdict-touching.

**Logical chain:** instrument (certified) → battery constructed under
the tiered untrained screen, membership fixed at freeze → probe side
run, Stage 1 committed AND tagged (manual step) → only then any
eval-side query → frozen analysis. **Verdict precedence:**
INSUFFICIENT_DATA → FAIL → PASS → INDETERMINATE. INSUFFICIENT_DATA
binds to the dual floor: fewer than **8 families** or fewer than
**20 rungs** scored at analysis time — never a smaller test, never a
loosened gate.

**Two-stage lock: absolute.** No eval-side model (2.8b/6.9b/12b) is
queried before the Stage 1 commit. Battery membership decisions use
only probe-side measurements (410m/1b, trained and untrained twins)
and no eval-side information of any kind — including published
benchmark numbers, which do not exist for these custom tasks and are
not sought. Emergence-within-ladder risk is managed by construction
(families straddling plausible thresholds), not by peeking; the cost
of that choice is that a battery-wide flat outcome reads as shrunken
effective n (§5), and the design accepts it.

**What a PASS does and does not claim** — verbatim from Exp 2b §5
(within-battery, Pile-distribution, ≤12b; excludes the starved lookup
family, not all non-lookup structure), plus: rung-level support with
family-honest inference claims nothing about capability families not
represented in the battery.

---

## 2. Models and capability battery

### Models (locked, carried)

Pythia standard (non-deduped) branch, final checkpoints, fp16, loaded
by the SHA-pinned loaders (`experiments/exp2b/models.py` pattern;
PYTHIA_SHAS carried verbatim). Probe sizes 410m/1b; eval sizes
2.8b/6.9b/12b; untrained twins per size at seeded random init
(torch.manual_seed(0), no pretrained weights).

### Spec discipline (six mandatory fields)

Exp 2b's five fields carry: probe target; surface basis analyzed
against the tokenizer; starving split with feasibility count; oracle;
dumbest-baseline analysis. New sixth: **family membership and dial
value**. Cross-family basis sharing gets the sibling treatment
(declared, option-3 style); within-family sharing is by design and
declared. Digit-local targets remain banned at design time.

### Candidate pool (~35–40 candidates → target ≥ 25 scored rungs, ≥ 9 families at freeze)

Membership is decided by the screen; every rejection recorded with its
tier-1/tier-2 fits, like 2b's feasibility ejections. Composition:

1. **Survivor-derived families** (12 survivors enter with 2b record
   reuse per §7):
   - *mid-digit arithmetic:* add3_mid, sub3_mid + a 4-digit rung
     (dial: digit count / carry depth)
   - *base representation:* base7, oct2dec + a base-5 or base-12 rung
     (dial: base unfamiliarity; new rungs must dodge bin2dec's
     value-mod-10 lesson — no target sharing a modulus with the
     surface digit alphabet)
   - *base arithmetic:* add_base8 + a subtraction rung
   - *modulus off the digit alphabet:* mod13 + mod17, mod19 rungs and
     a composition rung (((a+b)·c) mod 13)
   - *rotation ciphers:* caesar + a rung varying shift arithmetic or
     word length
   - *counting:* count_div7 + a count_div13 rung
   - *singleton families:* antonym, odd_one_out, reverse_string,
     clock24 (kept singleton deliberately: sibling weekday leaked)
2. **Rescues, capped at 6 candidates:** isqrt, collatz, roman first;
   each re-enters with its label moved off the identified surface
   carrier (roman: a function of the sum, not any numeral's suffix;
   collatz: second-step target, not the N-mod-20-legible first step;
   isqrt: a target the dumbest-baseline analysis clears of magnitude
   banding). Each rescue names the taxonomy mechanism it tests; a
   rescue that fails its screen is recorded as constructive
   confirmation of that mechanism, not lost work.
3. **New families as needed** to reach the pool target, drawn only
   from the taxonomy's defensible shapes: labels at the end of
   multi-step transformation, carry chains, relational composition.

### The tiered untrained screen (the promoted P1)

- **Tier 1 (candidate-design time):** 2 seeds × both sizes × 500
  permutations per candidate (~1–1.5 h; same-day redesign loop).
  Rejection bar derived from the order statistics of the max of 500
  null draws (worked example committed with the doc), not an SD rule.
  Both sizes always — mod7_add's 1b-only fire is the standing reason
  one-size screening is banned.
- **Tier 2 (pre-freeze, screen survivors only):** the identical frozen
  config — 5 seeds × 2 sizes × 2,500 permutations. These fits are
  declared at freeze to BE the campaign's untrained-gate fits (§4
  gate 1); no recomputation.

---

## 3. Operationalizations

Normalized margins throughout, m = (acc − floor)/(1 − floor), floors
measured empirically, CP bounds on everything, never a claimed zero.

### Stage 1 instrument (the predictor) — carried frozen

`probe_starved` unchanged: StandardScaler + logistic regression
(C = 1.0, max_iter = 100) on residual-stream activations at the frozen
candidate family (every 3rd layer + final, × 2 positions), starving
split per §2 with 5 seeds redrawing held-out basis values,
label-permutation null with N_PERM = 2500 refits under the identical
split, Bonferroni across the family (floors 18/2501 ≈ .0072 at 410m,
14/2501 ≈ .0056 at 1b, against α = .01; the 2b doc's "≈ .0048" for 1b
is an arithmetic slip, corrected in the exp2b ledger's post-closeout
section). **Margin** = (starved-val acc − null mean)/(1 − null mean),
zero below the significance bar. **Probe score per rung** = seed-mean,
then mean over the two probe sizes (2b §3 verbatim). **Probe ranking**
= rungs ranked by probe score.

### Eval side (the outcome) — verbatim from the Exp 2 lineage

**Scale-ascent score** = mean normalized argmax margin across
2.8b/6.9b/12b on full ≥ 500-item eval sets, CP bounds, empirical
untrained floors, no fitted crossings or extrapolated quantities.
Flat rungs enter as zero-score ties under average-rank ρ; a
battery-wide flat outcome shrinks effective n and is reported as such
(§5 restricted-ρ secondary).

### Two-stage measurement lock — verbatim, with the screen boundary

Stage 1 probe scores committed AND tagged before any 2.8b+ query.
Battery membership frozen when Stage 1 begins; later item-quality
failures are attrition, never replacement. The screen, feasibility
counts, and M1 argmax-absence measurements live entirely on the
probe side of the line.

### Pre-freeze adjudication (standing rule, ruling c)

Every gate whose inputs exist at freeze time is adjudicated at freeze
time, as named checklist lines in the freeze review: gate 1 (tier-2
fits), gate 4 (argmax reliability, measured on 2c's own items at M1).
Each line carries the gate's arithmetic; "the number sat in the record
unchecked" cannot recur by construction.

---

## 4. Gates (all calibrated; two adjudicated at freeze)

1. **Untrained-weights gate (= tier-2 screen, adjudicated at
   freeze):** per-rung one-sided binomial rate test against the floor
   arithmetic (10 fits/rung expect 5×.0072 + 5×.0056 = 0.064 fires;
   at 25 rungs, 250 fits expect ≈ 1.6, P(≥1) ≈ .8), plus per-family
   aggregation as a second view. Per-fire classification per gate 2's
   mechanism-calibrated bound. Structural fire = screen rejection
   (recorded, replaced before freeze). Post-freeze attrition remains
   defined for residual defects; the §1 dual floor is the backstop.
2. **Shuffled-label gate (campaign):** trained activations,
   rng(1000+seed) label shuffles applied AFTER the split is built from
   true labels (the corrected ordering is canonical). Binomial count
   tolerance at the floor rate. Per-fire classification: a tolerated
   floor fire sits at the add-one floor AND within the central 99% of
   the distribution of the max of 2,500 null draws (exact quantile
   bound and worked example committed with the doc; replaces 2b's
   contradictory 3-SD conjunct). Structurally-beyond fire = pipeline
   abort. Abort authority lives here and only here.
3. **Known-present gate (campaign):** entity-track and ctrl_copy clear
   the starved bar with seed-majority (≥3/5) at both sizes and
   seed-mean starved margin ≥ 0.2 at 1b.
4. **Argmax positive control (adjudicated at freeze):** ctrl_copy
   argmax ≥ 0.9 at both probe sizes, measured on 2c's own items at M1
   — never transferred from a prior battery.
5. **Fixture suite (standing rule 1):** the adjudication code freezes
   together with fixture tests derived from this doc's worked examples
   plus one synthetic case per preregistered provision. Provision
   list, explicit: one leaking rung → attrition-without-abort; a
   clean-null shuffled draw at the floor → classified tolerated; an
   all-flat family → zero-score ties path; n below either floor →
   INSUFFICIENT_DATA. **The freeze does not happen until the fixture
   suite passes.**

---

## 5. Preregistered pass/fail and statistics

**Frozen at the freeze commit alongside `experiments/exp2c/analyze.py`.**

- **Primary statistic:** Spearman ρ (average-rank ties) between probe
  ranking and scale-ascent ranking over all scored rungs.
- **Test (family-honest):** the naive one-tailed MC permutation
  (10⁵, seeded) runs as machinery; its PASS cutoff is **calibrated**
  by the frozen MC table, which simulates the null under the declared
  within-family correlation model and selects the naive-p threshold
  yielding true α = .01. The correlation parameter is estimated from
  the 2b record's sibling pairs (add3_mid/sub3_mid, base7/oct2dec),
  source ledgered. **Fallback** (if the MC work shows calibration
  fragility, decided and ledgered before freeze): exact family-block
  permutation among same-size families, with the achievable
  permutation count and resolution stated in the doc.
- **PASS:** calibrated p < .01 AND point ρ ≥ 0.5. Departures from
  these numbers require a ledgered mechanism rationale before freeze,
  never after.
- **FAIL (the falsifier):** family-cluster bootstrap 95% CI on ρ
  (10⁴ resamples of families as units, seeded) includes 0.
- **INDETERMINATE:** neither; reported with the CI; no post-hoc
  slicing.
- **INSUFFICIENT_DATA:** dual floor (< 8 families or < 20 rungs).
  Precedence as §1.
- **Power:** exact MC power table computed under the family-correlation
  model and committed with the freeze; design proceeds only if power
  at ρ = 0.6 is ≥ 0.75 at the target battery, else the battery grows
  before freeze (ledgered decision).
- **Descriptive secondaries (never verdict-touching):** restricted-ρ
  over rungs with scale-ascent > 0.05 (carried); within-family
  concordance (dial order vs margin order vs ascent order, per
  family); the rescue scorecard (per rescue: screen outcome, named
  mechanism, confirmation status).
- **Dumbest-baseline line item (standing):** for the primary, a
  reservoir strategy scores starved-margin 0 by construction, so a
  structureless rung enters as a zero-margin tie, not a spurious
  rank; a flat eval side produces zero-score ties and shrinks
  effective n rather than manufacturing correlation. Every criterion
  in this section carries its written analysis; every zero a CP
  bound.

---

## 6. Run plan, compute, and distribution

- **Environment:** Mac mini (M4 Pro, 48 GB) alone by default, canonical
  venv, MPS-validated status per `environment.md`; no OS updates, no
  torch/transformers changes mid-campaign; brew-pinned python. The
  distributed machinery (per-box determinism gate, idempotent
  skip-if-exists merge) is dormant capability: it reactivates only if
  a box returns, gate first, results counted only after bit-identical
  fixture reproduction.
- **Phases:** **M0** battery construction with tier-1 screening inside
  the design loop (item generation under the canonical venv). **M1**
  inclusion: argmax absence at 410m/1b on candidates + ctrl_copy
  reliability on 2c items, each adjudicated against its bar the day
  it is measured. **Tier-2** untrained fits on screen survivors
  (~10 fits/new rung). **FREEZE:** doc + battery + analyze.py with
  passing fixture suite + MC calibration/power table + gate-1/gate-4
  adjudications, one commit, tag `exp2c-preregistered`. **M2**
  trained-side campaign (m3 + shuffled + known-present). **M3**
  Stage 1 assembly → manual commit + tag. **M4** eval side (12b the
  long pole, days-scale). **M5** frozen analysis; verdict projections
  ledgered before the report runs (standing practice).
- **Compute envelope (measured basis, refined at freeze):** probe-side
  campaign is new rungs and rescues only (§7): ~15–18 rungs × ~30
  fits ≈ 4–6 Mac-days at 2b's measured pace (~43 min/unit at 410m
  full depth, ~2× at 1b). Eval side is the program's first: all
  scored rungs × 3 eval sizes on ≥ 500-item sets, spent only after
  the Stage 1 tag.
- **Durability:** resumable skip-if-exists campaign scripts, detached
  launches, monitor patterns, crash recovery — carried verbatim from
  2b's infrastructure. UPS in the loop.

---

## 7. What the 2b record contributes (data reuse policy)

Reuse is exact because the instrument is bit-deterministic and the
items are committed: for the 12 survivors, the 2b fits ARE the 2c
fits. Declared at freeze, none recomputed:

- **Items:** survivor item files carried verbatim from the tagged 2b
  record (identical items = exact comparability).
- **Tier-2 / gate 1:** 2b's known_absent fits (all-zero, on the
  record) satisfy the survivors' tier-2 requirement.
- **Stage 1:** 2b's m3 fits are the survivors' Stage 1 margins.
- **Shuffled:** 2b's shuffled fits carry for the survivors' share of
  gate 2's count test.
- **Honesty clause, stated plainly:** the survivors' trained margins
  are already public in the closed 2b record (and in the methods
  paper), so probe-side blindness is not a property 2c can claim. The
  hypothesis test's integrity rests entirely on the eval side being
  unqueried — which is exactly what the two-stage lock protects, and
  why it is absolute.
- **Nuisance-parameter source:** the within-family correlation for
  §5's calibration is estimated from 2b sibling fits; using closed-
  record probe data for a nuisance parameter touches no outcome
  quantity.

---

## Open items before the freeze (all must close at or before the freeze commit)

1. MC calibration + power table under the family-correlation model
   (§5); fallback decision if fragile; final thresholds ledgered.
2. Family roster finalized through tier-1 screening; pool generated
   under the canonical venv; every ejection recorded.
3. Rescue label definitions with written dumbest-baseline analyses
   (the §2 cap of 6 stands even if all three named rescues fail
   screening and alternates are attempted).
4. Exact quantile bound + worked example for the gate-2 per-fire
   classification (§4).
5. Fixture suite implemented and passing against analyze.py and the
   gate/report code (§4.5).
6. Freeze-review checklist drafted with one line per pre-freeze
   adjudication (§3), each carrying its arithmetic.
7. Eval-side item sets (≥ 500/rung) generated and committed for all
   scored rungs before the Stage 1 tag (they exist on the probe side
   of the lock: generation uses oracles, not models).
