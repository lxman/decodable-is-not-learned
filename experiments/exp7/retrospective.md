# Experiment 7 — retrospective: `UNDETERMINED` (`NO-PREDICTOR-JOINT-LICENCE`)

Written 2026-10-23 UTC by the managing agent. This grades the agent projection
committed at `7998ceb10` (`experiments/exp7/PROJECTION.md`, before any predictor
preflight or new-battery model contact) against the one production verdict,
[`campaign/statistics/analysis/analysis.json`](campaign/statistics/analysis/analysis.json)
(SHA256 `6c52bdb9661392ba6067cd1b02079a8a92b43bce9915af346e66a0d5e149f6da`).
It is an experiment record, not prose in Michael's name. All statistics below
come directly from the saved `analysis.json`, `power.json`, `predictor-seal.json`,
and `complete.json`; no analysis was rerun for this retrospective.

## 1. The decision

**`NO-PREDICTOR-JOINT-LICENCE` (`licensed_predictors: []`). Both `pythia_1b` and
`olmo2_1b` terminate in `UNDETERMINED`.**

Under `experiment-7-design.md` §5–6, a family is eligible for the primary
battery-level evaluation only if at least 20 distinct counterfactual pairs are
ever joint-positive across the 26 `SmolLM3-3B` checkpoints ($n_{\text{pos}} \ge 20$,
where joint positivity at a checkpoint requires greedy continuation to emit $a_0$
on both `q0` and `q0s` and $a_1$ on both `q1` and `q1s`) and at least one
base $\times$ median-availability stratum is outcome-informative. Fewer than
three eligible families places a predictor in `UNDETERMINED`.

Only one of the four families (`units`) cleared the outcome-support floor:

| Family | Ever-joint-positive pairs ($n_{\text{pos}} / 500$) | Outcome histogram ($y \in \{0,\dots,26\}$) | `pythia_1b` conditional selectivity $\bar{x}_f$ | `pythia_1b` within-stratum $D_f$ | `olmo2_1b` conditional selectivity $\bar{x}_f$ | `olmo2_1b` within-stratum $D_f$ | Status |
|---|---:|---|---:|---:|---:|---:|---|
| `units` (`arithmetic`) | `50` | `{'0': 450, '1': 38, '2': 9, '3': 3}` | `+0.002453` (`770717/314160000`) | `-0.161892` (`-356/2199`) | `+0.011499` (`2518872990209766767/219060189739591200000`) | `-0.093077` (`-203/2181`) | **ELIGIBLE** |
| `unscrambling` | `2` | `{'0': 498, '1': 2}` | `+0.002000` (`1/500`) | `0.000000` (`0/1`, denom `60`) | `+0.024000` (`3/125`) | `+0.206897` (`6/29`) | Excluded ($n_{\text{pos}} < 20$) |
| `deduction` | `0` | `{'0': 500}` | `-0.004327` (`-23120123430886319/5342931457063200000`) | `None` (denom `0`) | `+0.010322` (`164475397/15935205000`) | `None` (denom `0`) | Excluded ($n_{\text{pos}} < 20$, flat $y$) |
| `shapes` | `0` | `{'0': 500}` | `-0.006330` (`-368365391/58198140000`) | `None` (denom `0`) | `-0.005817` (`-51906781159/8923714800000`) | `None` (denom `0`) | Excluded ($n_{\text{pos}} < 20$, flat $y$) |
| **All-family mean $\bar{x}$** | — | — | **`-0.001551`** | — | **`+0.010001`** | — | **`UNDETERMINED` (`1/4` eligible)** |

Both predictors carry the frozen `UNDETERMINED` licence (`experiment-7-design.md` §6):
> *"Not enough informative families for the forecast rule. Shared input-sensitive
> difficulty and learned heuristics remain live explanations. This does not
> identify an internal algorithm or distinguish resolution from new computation.
> No unqualified joint POWERED label is available."*

### Realized reading, predictor selectivity, and power disclosure

Two distinct empirical facts are recorded in `analysis.json`:

1. **Outcome joint positivity across all four arms is sparse on three of the four families.**
   `S6_trajectories` separates single-arm correctness across the 26 checkpoints from simultaneous 4-arm joint positivity:
   - On `units`, individual arms have `405 / 411 / 388 / 394` ever-correct items across `(q0, q0s, q1, q1s)`, and `50` pairs achieve simultaneous 4-arm correctness at at least one checkpoint (`54` on sham-joint).
   - On `shapes`, individual arms have `123 / 124 / 120 / 125` ever-correct items across `(q0, q0s, q1, q1s)`, yet **`0/500` pairs** achieve simultaneous 4-arm correctness at the same checkpoint. When `SmolLM3-3B` emits a shape label under greedy decoding at a given checkpoint, it emits the same preferred class on both prompts of a pair rather than switching from $a_0$ on `q0/q0s` to $a_1$ on `q1/q1s`.
   - On `unscrambling`, individual arms have `32 / 50 / 40 / 49` ever-correct items across `(q0, q0s, q1, q1s)`, yielding `2/500` canonical joint-positive pairs (`9` on sham-joint).
   - On `deduction`, zero-shot `Q: ...\nA:` greedy continuation on 5-entity transitivity chains yields `0 / 1 / 0 / 1` ever-correct items across `(q0, q0s, q1, q1s)` and `0/500` joint-positive pairs.

2. **Predictor conditional selectivity $\bar{x}_f$ is itself near zero across all four families (`-0.0063` to `+0.0240`).**
   Even before outcome eligibility is applied, neither 1B predictor approaches the $\bar{x} \ge .05$ selectivity bar on any family:
   - On `shapes` and `deduction`, target-row availability $\bar{u}_f$ is substantial (`0.0843` and `0.2246` for `pythia_1b`; `0.1918` and `0.1194` for `olmo2_1b`, with `0` to `83` unsupported renders out of `1,000`), because the models frequently emit shape names or copy candidate names from the 5-option list. Conditional on emitting one of the two pair targets $\{a_0, a_1\}$, however, the 1B models barely shift between `q0` and `q1` ($\bar{x}_f \in [-0.0063, +0.0103]$).
   - On `units`, $\bar{u}_f$ is `0.0427` (`pythia_1b`) and `0.1699` (`olmo2_1b`), with small positive conditional shifts ($\bar{x}_f = +0.002453$ and $+0.011499$).
   - On `unscrambling`, free-form word emission makes target-row support very sparse at $k=64$ ($\bar{u}_f = 0.000508$ with `996/1000` unsupported renders for `pythia_1b`; $\bar{u}_f = 0.003641$ with `974/1000` unsupported renders for `olmo2_1b`). On the few supported renders (`4/1000` for `pythia_1b`, `26/1000` for `olmo2_1b`), `supported_only_mean_x` is `+0.500000` (`1/2`) and `+0.923077` (`12/13`), but under the preregistered unsupported-row centering rule (`D4`, finite-$k$ attenuation $[1-(1-s_0)^k][1-(1-s_1)^k]$), the all-pair mean $\bar{x}_f$ is `+0.002000` and `+0.024000`.

In `forecast_power`, the frozen pre-outcome simulation (`power.json`, SHA256 `643afd77ab5607423febecebd935483193efdcbc74c81286d28b61f6f3b032ea`) evaluated all 3-family and 4-family subsets (`POWERED` at the 4-family and 3-family levels under the synthetic rank-count alternatives), while the realized eligible set `['units']` (`1` family) has `realized_status: "UNDETERMINED"`, `frozen_declaration: null`, and departures `["units: nonzero count histogram differs from both frozen rank-count shapes", "no single count-shape arm matches every retained family"]`.

## 2. Projection: world, primary gates, and disconfirmers

**World MISS on both predictors.** `PROJECTION.md` called `INPUT-SENSITIVE-FORECAST` for both `pythia_1b` and `olmo2_1b` (with `SELECTIVE-ONLY` and `ORDER-ONLY` as alternatives) and predicted `n_eligible = 4` (fallback $\ge 3$). Both predictors landed in `UNDETERMINED` with `n_eligible = 1` (`['units']`).

The complete numerical grading table is [`projection-grade.md`](projection-grade.md). Across all graded cells:
- **Primary gates**: `0/4` binary calls hit (`4/4 MISS`); `0/4` numerical ranges hit (`4/4 LOW` on both retained `units` and all-family descriptive readings).
- **Per-family selectivity $\bar{x}_f$**: `0/8` ranges hit (`8/8 LOW`).
- **Per-family forecast $D_f$**: `0/2` eligible ranges hit (`2/2 LOW` on `units`; `6` cells ungraded due to $n_{\text{pos}} < 20$, where `olmo2_1b/unscrambling` has descriptive $D = +6/29 \approx +0.206897$ on 2 positive pairs and `pythia_1b/unscrambling` has $D = 0/1 = 0.000000$).

| Projection claim / disconfirmer (`PROJECTION.md` §4) | Observation in `analysis.json` | Grade |
|---|---|---|
| **1. Both 1B predictors exhibit conditional target shifts ($\bar{x} \ge .05, p < .005$)** | All-family $\bar{x} = -0.001551$ (`pythia_1b`) and $+0.010001$ (`olmo2_1b`); retained `units` $\bar{x} = +0.002453$ and $+0.011499$. `pythia_1b` has $\bar{x}_f \le 0$ on `2/4` families (`deduction`, `shapes`). | **DISCONFIRMED** (downward disconfirmer fired) |
| **2. Conditional target sensitivity forecasts paired outcome acquisition ($T \ge .10, p < .005$)** | Both predictors `UNDETERMINED`; on `units`, $D_{\text{units}} = -0.161892$ (`pythia_1b`) and $-0.093077$ (`olmo2_1b`). | **DISCONFIRMED** (downward disconfirmer fired) |
| **3. `olmo2_1b` exceeds `pythia_1b` on both selectivity and forecast** | `olmo2_1b > pythia_1b` on `4/4` families for $\bar{x}_f$, on all-family $\bar{x}$ (`+0.010001` vs `-0.001551`), and on `units` $D_f$ (`-0.093077` vs `-0.161892`, paired difference $+0.068815$). Magnitude of $\bar{x}$ difference (`+0.011552`) is below `[.02, .09]`. | **Direction HIT; magnitude LOW** |
| **4. Shared family witness (`unscrambling` and `shapes`)** | Zero families clear $\bar{x}_f > .05$; both `unscrambling` ($n_{\text{pos}}=2$) and `shapes` ($n_{\text{pos}}=0$) are outcome-ineligible. | **DISCONFIRMED** |

## 3. All named secondary readings (`S1..S8`) and controls, graded

All eight secondary analyses (`S1..S8`) are descriptive, non-gating readings saved in `analysis.json`:

| Reading | Saved result (`analysis.json`) | Projection grade |
|---|---|---|
| **Untrained `twin` ($k=16$)** | $\bar{x}_{\text{twin}} = 0/1 = 0.000000$ across all 4 families (`1000/1000` unsupported renders per family); $T_{\text{twin}} = 0/1 = 0.000000$ on both primary strata. | **HIT** |
| **S1 Competitor scores (`units`)** | `pythia_1b`: $T_x = -0.161892$, $T_d = -0.125057$, $T_{\text{rate}} = +0.013188$, $T_u = +0.141428$, $T_{\text{wrong}} = +0.199636$. `olmo2_1b`: $T_x = -0.093077$, $T_d = -0.060064$, $T_{\text{rate}} = +0.143512$, $T_u = +0.186153$, $T_{\text{wrong}} = +0.198074$. | **$T_u \in [.06, .24]$ HIT; $T_d, T_x$ MISS (negative)** |
| **S2 Canonical vs sham** | On `units`, $\bar{x}_{\text{can}} - \bar{x}_{\text{sham}} = -0.015630$ (`pythia_1b`) and $+0.004432$ (`olmo2_1b`), both within $\pm .05$. Outcome joint agreement across all 26 checkpoints is `0.993000` (`units`), `0.999154` (`unscrambling`), and `1.000000` (`deduction`, `shapes`). | **HIT** |
| **S3 Family coverage & availability $\bar{u}_f$** | $\bar{u}_f$ (`pythia_1b` / `olmo2_1b`): `unscrambling` `0.000508 / 0.003641`, `units` `0.042742 / 0.169891`, `shapes` `0.084250 / 0.191820`, `deduction` `0.224648 / 0.119375`. | **`shapes`/`deduction` highest $\bar{u}_f$ HIT; lowest $\bar{u}_f$ was `unscrambling`, not `units` (MISS)** |
| **S4 Stratification sensitivity (`units`)** | `base -> median -> tercile` $T$: `pythia_1b` `-0.160350 -> -0.161892 -> -0.157822`; `olmo2_1b` `-0.097780 -> -0.093077 -> -0.085517`. | **Partition stability ($\Delta < .013$) HIT; level $T > .08$ MISS** |
| **S5 Draw-budget nesting (`units`)** | Fixed-strata $\bar{x}$ across $k=16 \to 32 \to 64$: `pythia_1b` `+0.000533 -> -0.008565 -> +0.002453`; `olmo2_1b` `+0.015670 -> +0.013909 -> +0.011499`. Disjoint 32-draw halves $T$: `pythia_1b` `-0.115052` vs `-0.107776` (diff `-0.007276`); `olmo2_1b` `-0.120128` vs `-0.049519` (diff `-0.070610`). | **Monotonic $\bar{x}$ growth MISS; split-half $T$ consistency HIT** |
| **S6 Trajectories & outcome definitions (`units`)** | `joint` vs `first_joint_order` $T$: `pythia_1b` `-0.161892` vs `-0.152402`; `olmo2_1b` `-0.093077` vs `-0.098728`. Member arms `q0/q0s/q1/q1s` $T$: `-0.0659` to `-0.0266` (`pythia_1b`), `-0.0374` to `-0.0213` (`olmo2_1b`). Nonmonotonic later losses occur on `46/500` `units` pairs (`572` loss transitions) and `2/500` `unscrambling` pairs. | **Sign agreement and nonmonotonicity HIT** |
| **S7 Model-free baselines** | All `49` applicable / `35` `N/A` baseline cells verified; `deduction/endpoint` scores `500/500` canonical and sham joint successes ($\bar{u}=1, \bar{x}=1$), `deduction/querywordonly` scores `25/500`, and on `units` every applicable deterministic baseline has $\bar{x}=0, T=0$. | **HIT** |
| **S8 Label-reversal identity** | Exact negation of $x_i, d_i$ and invariance of $u_i$ verified (`status: "EXACT"`) across all `8,000` `pythia_1b`, `8,000` `olmo2_1b`, `2,000` `twin`, and `24,500` applicable baseline pair evaluations (`17,500` `N/A`). | **HIT** |

### What `S1` and `S3` reveal on the single eligible family (`units`)

On `units` (`50` joint-positive pairs across 10 informative strata), `S1_competitors` separates prompt-invariant target reachability from prompt-conditional target sensitivity:
- **Target-row availability $u$** ($T_u = +0.141428$ for `pythia_1b`, $+0.186153$ for `olmo2_1b`) and **wrong-target emission rate** ($T_{\text{wrong}} = +0.199636$ for `pythia_1b`, $+0.198074$ for `olmo2_1b`) positively order `SmolLM3-3B`'s joint-success counts at magnitudes matching Experiments 1–6 ($T \approx .14\text{--}.20$).
- **Conditional target contrast $x$** ($T_x = -0.161892$ for `pythia_1b`, $-0.093077$ for `olmo2_1b`) and **raw contrast $d$** ($T_d = -0.125057$ and $-0.060064$) are both negative within the same strata (`paired_T_differences` $T_x - T_u = -0.303320$ for `pythia_1b`, $-0.279230$ for `olmo2_1b`; $T_x - T_{\text{wrong}} = -0.361528$ and $-0.291151$).

Within the bounded `UNDETERMINED` licence, `units` shows that 1B target reachability ($u$ and `wrong`) continues to track which pairs `SmolLM3-3B` solves, whereas 1B prompt-conditional target shifting ($x$) is near zero ($\bar{x} = +0.0025$ and $+0.0115$) and does not positively order paired acquisition.

## 4. Process and verification

All eight production stages ran under `run/stage_7.py` with full provenance, audit-hook, and hash-pinned verification:

1. **Stage 1 (`pythia-digest-baseline`)**: Completed locally on the Mac (`3e5ae9922`), sealing the fp32 tensor-digest baseline for `EleutherAI/pythia-1b-deduped` (`step143000`, `revision: 32993754...`) and its `seed=20261004` random-init `twin` (`result_sha256: 65d628c1ef58cc98ba36e9673d3d4a3a58ef0b044f6a418389b79bf22e35ca06`).
2. **Stage 2 (`predictor-preflight`)**: Completed locally on MPS (`abef051e2`), verifying all 6 historical Experiment 6 anchor units (`144,000` draws) and 12 new-battery `q0` preflight units (`288,000` draws) across `pythia_1b`, `olmo2_1b`, and `twin` (`result_sha256: 7c2e2dd42ca72e34d06923a830c0b8190d3a55f2336fe9a684523b3b9f5b1593`).
3. **Stage 3 (`predictor-collection`) & Stage 4 (`predictor-seal`)**: Completed locally on MPS (`13f67fcdf`), collecting all 48 predictor units (`1,152,000` total new-battery draws: `512,000` `pythia_1b` at $k=64$, `512,000` `olmo2_1b` at $k=64$, `128,000` `twin` at $k=16$), writing `campaign/predictor-seal.json` (`21,990` B, SHA256 `fedcb0b6e107db71f86b8f3632074c467be956d07f046649a1984c30a4cc3e5d`), and cutting annotated tag `exp7-predictor-sealed` (tag object `d5031d50babd62cdaa1eec2d3be173175f8c8aa5` -> commit `13f67fcdfddf00e0aa2ccf9444910a811aab0f93`) before any `SmolLM3-3B` outcome contact.
4. **Stage 5 (`power`)**: Completed locally on the Mac (`cd9bfb3d6`, `562.4s`), writing `campaign/statistics/power/power.json` (`493,365,893` B, SHA256 `643afd77ab5607423febecebd935483193efdcbc74c81286d28b61f6f3b032ea`) and `REPORT.md` (`548,295,672` B, SHA256 `ac0630078d94b22f64bf84d0d1fed156ee27e6d21e1f771ff022e16349bc5c15`).
5. **Stage 6 (`outcome-preflight`) & Stage 7 (`outcome` + `campaign-complete` + `watch` + `secured_7.py` + `release`)**:
   - Executed on Vast.ai Instance `57315143` (`NVIDIA A100-SXM4-80GB`, machine `37857`, `\$1.221/h`).
   - `outcome-preflight` verified byte-identical greedy outputs (`41f4aaf275e82d96e0c54fd258a60ab54a802efee98fb0b153420040dbfb0f2f`) between `thin` and `candidate` loaders on `HuggingFaceTB/SmolLM3-3B-checkpoints` `step_3440000` across all 2,500 anchor prompts and all 8,000 battery prompts (`COMPLETE.json` `result_sha256: efa292cdad06ce58665ed66cba77a80f4e2c441f692656884be7c2eba5f817fa`).
   - `outcome` swept all 26 `SmolLM3-3B` checkpoints (`step_40000` .. `step_3440000`, `208,000` battery continuations + `67,500` anchor continuations) in `2h 40m 45s` (`04:52:35Z`–`07:33:20Z`), writing `campaign/complete.json` (`20,929` B, SHA256 `7c1c6b5bfcd904b1666a317399d7beda00c63600da4af7d124920f3ec7cf64f8`).
   - `watch` (`7fc5e4d77`) pulled and re-verified all 55 remote units and 27 load receipts, ran `secured_7.py` (`watch-output/secured.json` `56,250` B, SHA256 `7a881c9b929157c9b13374d2f773f099eaf4208940100fff1f860397ffd5f4ea`), and automatically destroyed Instance `57315143` (`watch-output/release.json` SHA256 `254de90699c3570e7711dd7d3b153a58f7ac901d249f1d3886941ec61177c88b`, `instances_remaining: 0`, `credit_after: 83.04921951969993`).
6. **Stage 8 (`verdict` / `analysis`)**: Ran once on the Mac (`9ebe3c0d5`, `2026-10-23 14:15:39–14:35:00 UTC`, `19m 21s`), with 10,000 fixed-margin hypergeometric / within-stratum permutations and 1,000 bundle bootstraps, writing `campaign/statistics/analysis/analysis.json` (`98,391,326` B, SHA256 `6c52bdb9661392ba6067cd1b02079a8a92b43bce9915af346e66a0d5e149f6da`) and `REPORT.md` (`241,978,510` B, SHA256 `88f6eca862bf75141e98a2ff786e4bcc4b1847ea393d5d4df32a2cd81e3e0944`).

### Process notes for Michael's consideration

1. **Simultaneous 4-arm joint positivity is qualitatively stricter than single-arm correctness.**
   On `shapes`, `SmolLM3-3B` solved roughly `25%` of items on each individual arm (`120`–`125` out of `500`), yet `0/500` pairs were solved across all four arms at the same checkpoint because checkpoint-level class preferences favored one shape label over its counterfactual partner. Future paired-prompt designs that want to measure within-family trajectory ordering when conditional selectivity is weak should pre-specify whether member-arm correctness (`S6`) or pair-sum correctness supplements strict 4-arm conjunction.
2. **Cross-platform `libm` floating-point differences affect exact float equality in saved power validators.**
   `power.json` was generated on macOS `arm64` (`libsystem_m.dylib`), where `binomial_interval(k, 128)` (`exp7core/simulations.py:142`) differed by 1 bisection step (`4.5e-15`, 1 ULP) on a single cell (`k=53, n=128`: `0.527152875603403` on macOS vs `0.5271528756033985` on Linux `x86_64` GNU `libm.so.6`) when the remote GPU worker re-ran `collection_power_validator`. Providing the exact 129-entry macOS `binomial_interval(k, 128)` table in the remote environment resolved the cross-OS check without altering any pinned source file; future cross-OS validators should store rational or integer bisection representations rather than comparing transcendental `math.exp`/`math.lgamma` floats across OS `libm` implementations.
3. **Vast.ai API `/api/v0` -> `/api/v1` redirect behavior on `PUT`/`DELETE`.**
   Vast.ai's `console.vast.ai/api/v0/asks/<id>/` and `/api/v0/instances/<id>/` endpoints now issue HTTP 307 redirects to `https://cloud.vast.ai/api/v1/...`. Normalizing `/api/v0/` to `https://cloud.vast.ai/api/v1/` in the local runtime transport layer prevented `urllib` redirect errors during rental creation and teardown.
4. **Rental cost accounting and platform content-filter interruption.**
   Instance `57315143` ran for `9.00 h` (`2026-10-22 23:28 EDT` to `2026-10-23 08:28 EDT`) at `\$1.221/h`, for a total Vast credit delta of **`\$11.00`** (`\$94.03 -> \$83.04`, well within the `\$25` planning cap). Of that `9.00 h`, `2.90 h` (`\$3.54`) was active GPU collection (`outcome-preflight` + 26-checkpoint `outcome` sweep), `1.87 h` (`\$2.29`) was provisioning, cross-OS `libm` diagnosis, transfer, and `secured_7.py` verification, and **`4.23 h` (`\$5.17`) was idle** between `03:33 EDT` and `07:47 EDT` after the chat platform's `MODEL_ARMOR` filter blocked a turn containing raw remote log output and halted the agent session until Michael sent a follow-up message. Future remote stages should chain `outcome-preflight -> outcome` inside a single detached remote wrapper script so an interrupted local session cannot leave a rental idling between stages.
