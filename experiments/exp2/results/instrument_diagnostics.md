# Exp 2 instrument diagnostics — POST-HOC, UNREGISTERED, probe-side only

**Status:** Diagnostic record for the Exp 2b design phase. Nothing here is a
preregistered result; nothing here touches frozen artifacts or adjudicates any
gate (that happens at `m2_report`). All analyses use ONLY probe-side data
(410m/1b activations and probe fits) — the eval-side models (2.8b+) remain
unqueried, so the two-stage lock is intact and Prediction 2's outcome is still
unobserved. Written 2026-07-15/16 while the M2/M3 campaign ran, by the session
operator (Claude), for review with Michael at the m2-report session.

## 1. The untrained control fired on the entire battery (410m, 5/5 seeds each)

Every fire at the family-corrected permutation floor (p = 18/2501 ≈ .0072 —
observed accuracy beat all 2500 label permutations). Seed-0 values:

| capability | untrained acc | chance (maj-class) | margin | best (layer, slot) |
|---|---|---|---|---|
| units | 1.000 | 0.659 | 1.000 | (L3, slot0) |
| mod7 | 1.000 | 0.153 | 1.000 | (L3, slot0) |
| add2 | 0.996 | 0.546 | 0.992 | (L12, slot0) |
| roman | 0.984 | 0.112 | 0.982 | (L9, slot1) |
| weekday | 0.974 | 0.151 | 0.970 | (L12, slot0) |
| mult2 | 0.490 | 0.271 | 0.391 | (L21, slot0) |
| reverse_string | 0.366 | 0.052 | 0.341 | (L12, slot0) |
| unscramble | 0.306 | 0.058 | 0.270 | (L6, slot0) |
| add3 | 0.476 | 0.355 | 0.265 | (L15, slot0) |
| acronym | 0.296 | 0.060 | 0.261 | (L3, slot1) |
| count_category | 0.440 | 0.353 | 0.216 | (L3, slot0) |
| cipher | 0.244 | 0.069 | 0.205 | (L3, slot0) |

**Mechanism (verified, not assumed):** a random-but-fixed network is a
reservoir; a linear readout with n=2000 items and d=1024 features decodes
deterministic functions of the prompt tokens. Group-split diagnostic on
untrained mod7 (best candidate (12,1)): accuracy survives unseen operand
PAIRS (1.000) but collapses on held-out operand VALUES (0.129–0.142 vs chance
0.143) — per-operand-token lookup plus additive mixing, not arithmetic.
Physically sensible winners (slot 0 = question-end token; early/mid layers).
Not a pipeline bug: the shuffled-label stage is 59/60 silent (see §3).

**Frozen consequence:** the §3 attrition rule (fire in ANY seed at EITHER
size → drop) removes all 12 capabilities; n = 0 < 10 → the preregistered
verdict path is INSUFFICIENT_DATA ("not a loosened control").

**1b replication (2026-07-16):** 60/60 untrained fits fire at 1b as well.
Seed-mean margins are near-identical to 410m (mod7/units 1.000, add2 0.976,
roman 0.986, weekday 0.970) and slightly HIGHER for the letter tasks (acronym
0.262 → 0.345, reverse_string 0.350 → 0.390, cipher 0.204 → 0.236): d=2048
gives the linear readout more random features. The floor scales WITH width —
a bigger probe-side model deepens the confound rather than escaping it.

## 2. Trained − untrained margin gap at 410m (seed-means, 5 seeds each)

| capability | trained margin | untrained margin | gap |
|---|---|---|---|
| reverse_string | 0.999 | 0.350 | +0.649 |
| cipher | 0.543 | 0.204 | +0.339 |
| count_category | 0.547 | 0.223 | +0.324 |
| unscramble | 0.433 | 0.265 | +0.168 |
| mult2 | 0.553 | 0.414 | +0.139 |
| acronym | 0.398 | 0.262 | +0.136 |
| add3 | 0.416 | 0.319 | +0.097 |
| roman | 1.000 | 0.977 | +0.023 |
| mod7 | 1.000 | 1.000 | 0.000 |
| units | 1.000 | 1.000 | 0.000 |
| weekday | 0.965 | 0.966 | −0.001 |
| add2 | 0.946 | 0.986 | −0.040 |

A trained−untrained gap score has dynamic range on 7 of 12 capabilities but
SATURATES on 5 (both readouts at ceiling — no ranking information). Saturation
is an n/d artifact: 1500 training rows memorize a ~90-token lookup perfectly
on both networks.

## 3. Shuffled-label stage (410m): machinery honest; zero-tolerance rule miscalibrated

59/60 fits silent (p = 1.0 after Bonferroni saturation). One fire:
roman/seed3, p = .0072 (the floor), acc 0.150 vs null_mean 0.100 — nowhere
near roman's real trained signal (0.984), so the shuffle was applied; this is
the test's own designed false-positive rate. Per-fit fire probability under
clean machinery ≤ 18/2501 ≈ .0072; across the campaign's 120 shuffled fits,
E[fires] ≈ 0.86, P(≥1) ≈ 0.58. **The frozen "any fire anywhere = abort" rule
put zero tolerance on a test whose modal clean-machinery outcome is ≥1 fire**
— a "claimed zero" of exactly the kind the working agreements forbid,
computable before any data existed. Adjudication (one-mechanism-fix candidate:
a binomial tolerance against the floor rate) belongs to the m2-report session.

## 4. Group-split diagnostic on TRAINED activations (the deepest cut)

Validate only on held-out first-operand values (20 operands held out; probe
trained on the rest). Best-candidate features, C=1.0, max_iter=1000:

| capability | mode | group-split acc | majority baseline on val |
|---|---|---|---|
| mod7 | trained | **0.009** | 0.209 |
| mod7 | untrained | 0.083 | 0.209 |
| add2 | trained | 0.932 | 0.613 |
| add2 | untrained | **0.983** | 0.613 |
| weekday | trained | 0.212 | 0.250 |
| weekday | untrained | 0.138 | 0.250 |

Three distinct behaviors, all instrument-critical:

- **mod7 trained collapses below chance (0.009):** the trained 410m probe's
  perfect in-distribution margin is ALSO lookup — systematically wrong on
  unseen operands (consistent with a per-operand offset structure). Whatever
  the probe found at 410m for mod7, it is not generalizing arithmetic
  precursor structure.
- **add2 survives the split for BOTH networks (untrained 0.983):** Pythia's
  BPE tokenizes numbers into digit chunks; add2's probe target is digit-LOCAL,
  so an operand-level split cannot starve a digit-level lookup basis — even a
  random network generalizes across operand values. mod7 is digit-NONLOCAL
  (needs both digits jointly), which is why its lookup collapses under the
  same split.
- **weekday fails for both:** its 0.965 trained margin was lookup too.

## 5. Implications for the Exp 2b design (input to the clarify/propose phase)

1. Absolute probe significance is uninformative in this regime (§1). A
   selectivity-style score is necessary but NOT sufficient: the gap saturates
   at these n/d for easy surface targets (§2).
2. The stronger notion is **generalization across the surface basis**: score a
   probe by validation on splits that hold out the surface tokens the
   reservoir reads. But the split must be keyed to the TOKENIZER'S basis per
   target (§4: operand-level splits don't starve digit-level bases). Each
   battery target needs an explicit "surface basis" analysis and a split that
   starves it — and targets with no feasible starving split (e.g. digit-local
   targets; 26-letter bases) must be excluded at design time.
3. Alternative/complementary instruments worth proposing: sample-efficiency
   probing (cap probe training rows — lookup strategies starve first) and
   MDL/online-codelength probing (Voita & Titov), which price memorization
   explicitly.
4. The mandatory design-doc line item, now with teeth: for every criterion,
   "what does the dumbest baseline (a random network / a lookup table)
   achieve?" — computed BEFORE freeze, on pilot data if needed. Both Exp 1's
   S1-units misspecification and Exp 2's reservoir floor were computable
   pre-data; the shuffled-gate zero-tolerance miscalibration (§3) was one
   multiplication away from the ledgered floor arithmetic.
5. Positive controls as probe targets are hollow in this regime (ctrl_copy /
   ctrl_next_letter fire 5/5 at margin ~1.0 on trained weights, but they are
   single-token surface functions — the reservoir fires on them regardless of
   capability). Only the argmax half of that gate carries information
   (ctrl_next_letter: 0.338 at 410m per M1 — expected GATE FAIL at the
   report, the known one-ledgered-fix conversation).

## 6. What survives for the write-up regardless of Exp 2b

- The control worked and changed the answer: most published probing results
  never run an untrained-weights control; this one did, pre-registered, and it
  vetoed the entire battery before a single outcome-side query. Process
  containment: two-stage lock intact, eval side clean for any successor
  design.
- The reservoir floor is now a quantified, five-seed empirical object for 12
  task types at 410m (and 1b when the campaign completes) — reusable as a
  known quantity in any follow-up design.
