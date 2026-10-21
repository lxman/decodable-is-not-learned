# Experiment 7 — projection before predictor preflight and model contact

Written 2026-10-21 UTC by the managing agent. This is an agent forecast to
grade at close-out, not a result or a statement in Michael's name. Committed
after `exp7-preregistered` (`819d537c5a51c92f2e3f98419ab81ebc5b5b1f24`, annotated
tag object `5371b8f904bb17b6ddf363c154d02b962313cc6f`) and **before the first
predictor preflight or any model weight/item contact on the new battery**. The
design's rules and licences (`experiment-7-design.md` §5–8) govern every landing.

## Information available at this projection

- The complete record through Experiment 6 (`GENERAL` across all four outcome
  families for both `pythia_1b` and `olmo2_1b`; wrong-target prior $T = .1247 /
  .1263 / .1248 / .0977$) and Experiment 2j (four-functionals residual $T = .1311$).
- Experiment 7's certified model-free battery (`feasibility-002/full-003`):
  4 families (`arithmetic`, `deduction`, `shapes`, `unscrambling`) × 500
  counterfactual pairs × 4 prompt arms (`q0`, `q0s`, `q1`, `q1s`) = 2,000 pairs /
  8,000 prompts, with base strata sizes `5 / 20 / 2 / 15` (`arithmetic /
  deduction / shapes / unscrambling`).
- The certified 84-cell model-free baseline catalog (`49` applicable / `35`
  explicit `N/A`), including the disclosed `deduction` endpoint-option shortcut
  (`500/500` pair successes) and the four-label/two-class `shapes` structure.
- Pre-tag tokenizer/config-only cap validation (`offline-003`): 28 receipts
  (`pythia_1b`, `olmo2_1b`, and 26 `SmolLM3-3B` checkpoints), zero model weights
  loaded, zero forward passes.
- Pre-tag synthetic calibration (`calibration-001`, accepted at `d20b633b5`):
  `0/44,000` component `fires` and `0/18,000` `either_predictor_joint` fires
  across `N1..N9` (`2,000` replicates each at $n=500, B=10,000$), plus the
  80-cell selectivity envelope (`128` replicates each).
- Full-default synthetic freeze (`freeze-001`, accepted at `45674e88f`): `400/400`
  cold tests twice, `40/40` worlds, `43/43` mutants `KILLED`.

No predictor preflight, predictor sampling, Pythia digest baseline, outcome
preflight, or outcome sweep has been executed on the new battery.

---

## Worlds enumerated and called (`experiment-7-design.md` §6)

Each predictor (`pythia_1b` and `olmo2_1b`) is evaluated separately across the
six preregistered terminal states:

| State | Rule | Call for `pythia_1b` | Call for `olmo2_1b` |
|---|---|---|---|
| `INSUFFICIENT_DATA` | Any input/provenance/collection gate fails | Not called | Not called |
| `UNDETERMINED` | Fewer than 3 eligible families ($\ge 20$ joint-positive pairs and $\ge 1$ informative block per family) | Not called | Not called |
| **`INPUT-SENSITIVE-FORECAST`** | **Both gates fire ($\bar{x} \ge .05, p < .005$ and $T \ge .10, p < .005$)** | **CALLED (primary call, modest confidence)** | **CALLED (primary call, moderate confidence)** |
| `SELECTIVE-ONLY` | Selectivity fires ($\bar{x} \ge .05, p < .005$), forecast does not | Main alternative for `pythia_1b` | Secondary alternative for `olmo2_1b` |
| `ORDER-ONLY` | Forecast fires ($T \ge .10, p < .005$), selectivity does not | Secondary alternative | Secondary alternative |
| `NO-JOINT-SUPPORT` | Neither gate fires | Disconfirmer | Disconfirmer |

- **Predicted eligible family set**: all 4 families (`arithmetic`, `deduction`,
  `shapes`, `unscrambling`) clear $\ge 20$ ever-joint-positive pairs across the
  26-checkpoint `SmolLM3-3B` grid (`n_eligible = 4`). If `arithmetic` (unit
  interpretation) or `deduction` falls below 20 joint-positive pairs across all
  26 checkpoints, the 3-family subset retains eligibility (`n_eligible >= 3`).

---

## Primary gate point forecasts and grading ranges

These are subjective point forecasts and inclusive grading ranges (`[low, high]`),
not confidence intervals. A numerical HIT is inside the inclusive range; a binary
gate or state MISS remains a miss even if the continuous statistic lands inside
the numerical range.

| Predictor | Gate | Bar | Point forecast | Grading range | Fires? |
|---|---|---|---:|---|---:|
| `pythia_1b` | **Selectivity** ($\bar{x}$, equal-family mean) | $\ge .050, p < .005$ | `.110` | `[.055, .200]` | **yes** |
| `pythia_1b` | **Forecast** ($T$, within-stratum Somers' $D$) | $\ge .100, p < .005$ | `.125` | `[.065, .210]` | **yes** |
| `olmo2_1b` | **Selectivity** ($\bar{x}$, equal-family mean) | $\ge .050, p < .005$ | `.165` | `[.090, .260]` | **yes** |
| `olmo2_1b` | **Forecast** ($T$, within-stratum Somers' $D$) | $\ge .100, p < .005$ | `.160` | `[.095, .250]` | **yes** |

All four primary one-sided randomization/permutation $p$-values are projected at
$p \le .002$ ($< .005$).

---

## Per-family texture (selectivity $\bar{x}_f$, availability $\bar{u}_f$, forecast $D_f$)

Grade every retained predictor × family cell against its inclusive range:

| Family | `pythia_1b` $\bar{x}_f$ range | `olmo2_1b` $\bar{x}_f$ range | `pythia_1b` $D_f$ range | `olmo2_1b` $D_f$ range | Projected texture |
|---|---|---|---|---|---|
| `unscrambling` | `[.06, .24]` | `[.12, .32]` | `[.08, .28]` | `[.12, .34]` | Strongest joint witness; high target availability on 3–5 letter words and clear within-stratum difficulty ordering. |
| `shapes` | `[.05, .26]` | `[.08, .30]` | `[.02, .24]` | `[.05, .28]` | Closed 4-label answer set yields high target-row availability ($u_f$) and clean conditional target shifts. |
| `deduction` | `[.03, .20]` | `[.07, .26]` | `[.02, .24]` | `[.05, .28]` | Endpoint-option presence gives high $u_f$; conditional target shift is positive and transfers to `SmolLM3-3B` paired success. |
| `arithmetic` | `[.01, .16]` | `[.04, .22]` | `[.00, .22]` | `[.03, .26]` | Free integer answers make target-row availability $u_f$ sparser ($[1-(1-s_0)^k][1-(1-s_1)^k]$ attenuation), yielding the smallest $\bar{x}_f$. |

---

## Claims with disconfirmers, both directions

1. **Both trained 1B predictors exhibit genuine conditional target shifts ($\bar{x} \ge .05, p < .005$):**
   When the prompt changes the correct target from $a_0$ to $a_1$, both `pythia_1b`
   and `olmo2_1b` shift conditional probability mass toward the newly correct
   target within target-emitting draws.
   - *Downward disconfirmer*: either predictor has $\bar{x} < .05$ or $p \ge .005$,
     or $\bar{x}_f \le 0$ on two or more families.
   - *Upward miss*: $\bar{x} > .30$ for `pythia_1b` or $\bar{x} > .35$ for `olmo2_1b`.
2. **Conditional target sensitivity forecasts paired outcome acquisition ($T \ge .10, p < .005$):**
   Higher pair-level conditional contrast $x_i$ predicts more joint-success
   checkpoints $y_i$ in `SmolLM3-3B` within base × median-availability strata.
   - *Downward disconfirmer*: $T < .10$ or $p \ge .005$ for either predictor
     (landing in `SELECTIVE-ONLY`), or negative $D_f < 0$ on two or more eligible
     families.
   - *Upward miss*: $T > .26$ for `pythia_1b` or $T > .30$ for `olmo2_1b`.
3. **`olmo2_1b` exceeds `pythia_1b` on both selectivity and forecast:**
   `olmo2_1b`'s $\bar{x}$ and $T$ exceed `pythia_1b`'s by `.02` to `.09` on the
   equal-family mean and on at least three of the four families.
   - *Disconfirmer*: `pythia_1b` exceeds `olmo2_1b` on the equal-family mean of
     either $\bar{x}$ or $T$, or on at least three families.
4. **Shared family witness exists (`unscrambling` and `shapes`):**
   At least two individual families (`unscrambling` and at least one of `shapes`
   or `deduction`) have both $\bar{x}_f > .05$ and $D_f > .10$ for `olmo2_1b`.
   - *Disconfirmer*: selectivity and forecast association come from completely
     disjoint family subsets (e.g., $\bar{x}_f > .05$ only where $D_f \le .02$).

---

## Named secondaries (`S1..S8`) and controls

- **Untrained `twin` control ($k=16$):** expected conditional selectivity
  $\bar{x}_{\text{twin}} \in [-.015, +.015]$ ($p > .05$) and forecast
  $T_{\text{twin}} \in [-.040, +.040]$ ($p > .05$). Disconfirmed if `twin` fires
  on either gate ($p < .005$ and clearing the effect bar).
- **S1 (Competitor scores — raw contrast $d$, availability $u$, wrong-target rate):**
  Availability $u$ and raw contrast $d$ also forecast $y$ positively ($T_u, T_d \in [.06, .24]$),
  reflecting shared item easiness/target reachability, while conditional contrast $x$
  retains a positive forecast $T_x \ge .10$ within availability-crossed strata.
- **S2 (Canonical vs sham rendering):**
  Canonical and sham renderings have similar selectivity ($\left|\bar{x}_{\text{can}} - \bar{x}_{\text{sham}}\right| \le .05$)
  and positive paired-success agreement across checkpoints.
- **S3 (Per-family decomposition and support):**
  `arithmetic` has the lowest target-row availability $u_f$ (highest unsupported-row
  fraction at $k=64$), whereas `shapes` and `deduction` have the highest $u_f$.
- **S4 (Stratification sensitivity — base-only, median-$u$, tercile-$u$):**
  Moving from base-only to median-$u$ to tercile-$u$ strata attenuates $T$ slightly
  (by `.00` to `.04`) while keeping $T > .08$ for both predictors.
- **S5 (Draw-budget nesting $k=16/32/64$ and split-half stability):**
  Mean selectivity $\bar{x}$ increases monotonically from $k=16$ to $k=32$ to $k=64$
  as finite-$k$ row support $[1-(1-s_0)^k][1-(1-s_1)^k]$ grows, and disjoint
  32-draw halves correlate positively.
- **S6 (Outcome definitions — individual member, joint success, first joint success):**
  Joint-success count $y_i$ and first-joint-success speed agree in sign across all
  eligible families; nonmonotonic later checkpoint losses occur on a minority of pairs.
- **S7 (Model-free baselines):**
  The declared `deduction` endpoint shortcut (`500/500`) and fitted lexical/heuristic
  baselines explain part of `deduction` and `arithmetic` ordering; this limitation is
  retained in the headline reading.
- **S8 (Exact target-label reversal identity):**
  Swapping target labels $(a_0, a_1) \mapsto (a_1, a_0)$ negates $x_i$ and $d_i$
  and preserves $u_i$ with zero exceptions across all 2,000 pairs.
