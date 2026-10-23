# Experiment 7 — complete numerical projection grading

Source: the pre-contact [`PROJECTION.md`](PROJECTION.md) (committed at `7998ceb10` before Stage 1–3 predictor contact); values from the once-written [`campaign/statistics/analysis/analysis.json`](campaign/statistics/analysis/analysis.json) (SHA256 `6c52bdb9661392ba6067cd1b02079a8a92b43bce9915af346e66a0d5e149f6da`).
`HIT` means inside the stated inclusive range (`[low, high]`), with no post-hoc tolerance.

## 1. World and eligibility calls

| Quantity | `pythia_1b` projected | `pythia_1b` actual | Grade | `olmo2_1b` projected | `olmo2_1b` actual | Grade |
|---|---|---|---|---|---|---|
| Terminal state (`world`) | `INPUT-SENSITIVE-FORECAST` (alt: `SELECTIVE-ONLY`, `ORDER-ONLY`) | `UNDETERMINED` | **MISS** | `INPUT-SENSITIVE-FORECAST` (alt: `SELECTIVE-ONLY`, `ORDER-ONLY`) | `UNDETERMINED` | **MISS** |
| Eligible family count (`n_eligible`) | `4` (fallback `>= 3`) | `1` (`['units']`) | **MISS** | `4` (fallback `>= 3`) | `1` (`['units']`) | **MISS** |
| Aggregate campaign label | At least one licensed predictor | `NO-PREDICTOR-JOINT-LICENCE` (`licensed_predictors: []`) | **MISS** | At least one licensed predictor | `NO-PREDICTOR-JOINT-LICENCE` (`licensed_predictors: []`) | **MISS** |

### Outcome eligibility by family across the 26 `SmolLM3-3B` checkpoints

| Family (`PROJECTION.md` label) | `analysis.json` key | Projected `n_positive >= 20` | Actual `n_positive` | Outcome histogram (`y`) | Informative blocks (`pythia_1b` / `olmo2_1b`) | Eligibility | Grade |
|---|---|---|---:|---|---|---|---:|
| `arithmetic` | `units` | Yes ($\ge 20$) | `50` | `{'0': 450, '1': 38, '2': 9, '3': 3}` | `9/10` / `10/10` | **ELIGIBLE** | **HIT** |
| `unscrambling` | `unscrambling` | Yes ($\ge 20$) | `2` | `{'0': 498, '1': 2}` | `2/25` / `2/30` | **INELIGIBLE** (`< 20`) | **MISS** |
| `deduction` | `deduction` | Yes ($\ge 20$) | `0` | `{'0': 500}` | `0/40` / `0/40` | **INELIGIBLE** (`< 20`, no informative block) | **MISS** |
| `shapes` | `shapes` | Yes ($\ge 20$) | `0` | `{'0': 500}` | `0/4` / `0/4` | **INELIGIBLE** (`< 20`, no informative block) | **MISS** |

## 2. Primary gate forecasts

Because only one family (`units`) cleared the preregistered outcome-support floor ($n_{\text{pos}} \ge 20$ and $\ge 1$ informative block), both predictors terminate in `UNDETERMINED` (`experiment-7-design.md` §6) and the primary `selectivity` and `forecast` gate records are `None` (no primary gate fires). Both the primary gate status and the retained single-family (`units`) and four-family descriptive statistics are graded below:

| Predictor | Gate | Bar | Point forecast | Grading range | Retained `units` actual | All-family actual | Numeric grade | Called fire | Actual fire | Binary grade |
|---|---|---|---:|---|---:|---:|---|---|---|---|
| `pythia_1b` | Selectivity ($\bar{x}$) | $\ge .050, p < .005$ | `.110` | `[.055, .200]` | `+0.002453` (`770717/314160000`) | `-0.001551` (`-1744460795473811/1124827675171200000`) | **LOW** | `True` | `False` (`UNDETERMINED`) | **MISS** |
| `pythia_1b` | Forecast ($T$) | $\ge .100, p < .005$ | `.125` | `[.065, .210]` | `-0.161892` (`-356/2199`) | `None` (1 eligible family) | **LOW** | `True` | `False` (`UNDETERMINED`) | **MISS** |
| `olmo2_1b` | Selectivity ($\bar{x}$) | $\ge .050, p < .005$ | `.165` | `[.090, .260]` | `+0.011499` (`2518872990209766767/219060189739591200000`) | `+0.010001` (`8763137204327652701/876240758958364800000`) | **LOW** | `True` | `False` (`UNDETERMINED`) | **MISS** |
| `olmo2_1b` | Forecast ($T$) | $\ge .100, p < .005$ | `.160` | `[.095, .250]` | `-0.093077` (`-203/2181`) | `None` (1 eligible family) | **LOW** | `True` | `False` (`UNDETERMINED`) | **MISS** |

## 3. Per-family selectivity ($\bar{x}_f$), availability ($\bar{u}_f$), and forecast ($D_f$) cells

### 3.1 Per-family conditional selectivity $\bar{x}_f$ (all 8 cells defined)

| Predictor | Family | Projected $\bar{x}_f$ range | Actual $\bar{x}_f$ (exact rational) | Actual $\bar{x}_f$ (decimal) | Actual $\bar{u}_f$ | Unsupported renders (`/1000`) | Supported-only $\bar{x}_f$ | Grade |
|---|---|---|---|---:|---:|---:|---:|---|
| `pythia_1b` | `unscrambling` | `[0.06, 0.24]` | `1/500` | `+0.002000` | `0.000508` (`13/25600`) | `996` | `+0.500000` (`1/2`) | **LOW** |
| `pythia_1b` | `shapes` | `[0.05, 0.26]` | `-368365391/58198140000` | `-0.006330` | `0.084250` (`337/4000`) | `83` | `-0.006902` (`-368365391/53367694380`) | **LOW** |
| `pythia_1b` | `deduction` | `[0.03, 0.20]` | `-23120123430886319/5342931457063200000` | `-0.004327` | `0.224648` (`5751/25600`) | `2` | `-0.004336` (`-23120123430886319/5332245594149073600`) | **LOW** |
| `pythia_1b` | `units` (`arithmetic`) | `[0.01, 0.16]` | `770717/314160000` | `+0.002453` | `0.042742` (`5471/128000`) | `326` | `+0.003640` (`770717/211743840`) | **LOW** |
| `olmo2_1b` | `unscrambling` | `[0.12, 0.32]` | `3/125` | `+0.024000` | `0.003641` (`233/64000`) | `974` | `+0.923077` (`12/13`) | **LOW** |
| `olmo2_1b` | `shapes` | `[0.08, 0.30]` | `-51906781159/8923714800000` | `-0.005817` | `0.191820` (`24553/128000`) | `0` | `-0.005817` (`-51906781159/8923714800000`) | **LOW** |
| `olmo2_1b` | `deduction` | `[0.07, 0.26]` | `164475397/15935205000` | `+0.010322` | `0.119375` (`191/1600`) | `16` | `+0.010489` (`164475397/15680241720`) | **LOW** |
| `olmo2_1b` | `units` (`arithmetic`) | `[0.04, 0.22]` | `2518872990209766767/219060189739591200000` | `+0.011499` | `0.169891` (`10873/64000`) | `37` | `+0.011940` (`2518872990209766767/210954962719226325600`) | **LOW** |

### 3.2 Per-family within-stratum Somers' $D_f$ (2 eligible cells, 6 ineligible cells)

| Predictor | Family | Projected $D_f$ range | Eligibility | Actual $D_f$ (exact rational) | Actual $D_f$ (decimal) | Outcome-untied pairs (`denominator`) | Grade |
|---|---|---|---|---|---:|---:|---|
| `pythia_1b` | `units` (`arithmetic`) | `[0.00, 0.22]` | **ELIGIBLE** (`n_pos=50`) | `-356/2199` | `-0.161892` | `2199` | **LOW** |
| `olmo2_1b` | `units` (`arithmetic`) | `[0.03, 0.26]` | **ELIGIBLE** (`n_pos=50`) | `-203/2181` | `-0.093077` | `2181` | **LOW** |
| `pythia_1b` | `unscrambling` | `[0.08, 0.28]` | INELIGIBLE (`n_pos=2`) | `0/1` | `0.000000` | `60` | Ungraded (`THIN`; descriptive `LOW`) |
| `olmo2_1b` | `unscrambling` | `[0.12, 0.34]` | INELIGIBLE (`n_pos=2`) | `6/29` | `+0.206897` | `29` | Ungraded (`THIN`; descriptive inside `[0.12, 0.34]`) |
| `pythia_1b` | `shapes` | `[0.02, 0.24]` | INELIGIBLE (`n_pos=0`) | `None` | `None` | `0` | Ungraded (`FLAT`) |
| `olmo2_1b` | `shapes` | `[0.05, 0.28]` | INELIGIBLE (`n_pos=0`) | `None` | `None` | `0` | Ungraded (`FLAT`) |
| `pythia_1b` | `deduction` | `[0.02, 0.24]` | INELIGIBLE (`n_pos=0`) | `None` | `None` | `0` | Ungraded (`FLAT`) |
| `olmo2_1b` | `deduction` | `[0.05, 0.28]` | INELIGIBLE (`n_pos=0`) | `None` | `None` | `0` | Ungraded (`FLAT`) |

Totals across graded per-family cells:
- Selectivity $\bar{x}_f$: `0/8 HIT`, `8/8 LOW` (`pythia_1b`: `0 HIT, 4 LOW`; `olmo2_1b`: `0 HIT, 4 LOW`).
- Eligible forecast $D_f$: `0/2 HIT`, `2/2 LOW` (`pythia_1b`: `0 HIT, 1 LOW`; `olmo2_1b`: `0 HIT, 1 LOW`; `6` cells ungraded due to `n_positive < 20`).

## 4. Claims with disconfirmers (`PROJECTION.md` §4)

| Claim | Stated disconfirmer | Observation in `analysis.json` | Grade |
|---|---|---|---|
| **1. Both trained 1B predictors exhibit conditional target shifts ($\bar{x} \ge .05, p < .005$)** | Either predictor has $\bar{x} < .05$ or $p \ge .005$, or $\bar{x}_f \le 0$ on $\ge 2$ families | Both predictors are `UNDETERMINED` with all-family $\bar{x} = -0.001551$ (`pythia_1b`) and $+0.010001$ (`olmo2_1b`), and retained `units` $\bar{x} = +0.002453$ and $+0.011499` ($< .05$). `pythia_1b` has $\bar{x}_f \le 0$ on `2/4` families (`deduction` $-0.004327$, `shapes` $-0.006330$). | **DISCONFIRMED (downward disconfirmer fired)** |
| **2. Conditional target sensitivity forecasts paired outcome acquisition ($T \ge .10, p < .005$)** | $T < .10$ or $p \ge .005$ for either predictor, or $D_f < 0$ on $\ge 2$ eligible families | Both predictors land in `UNDETERMINED` (`1/4` eligible families); on the sole eligible family (`units`), $D_{\text{units}} = -0.161892$ (`pythia_1b`) and $-0.093077$ (`olmo2_1b`). | **DISCONFIRMED (downward disconfirmer fired)** |
| **3. `olmo2_1b` exceeds `pythia_1b` on both selectivity and forecast** | `pythia_1b` exceeds `olmo2_1b` on the equal-family mean of $\bar{x}$ or $T$, or on $\ge 3$ families | `olmo2_1b` exceeds `pythia_1b` on all 4 families for $\bar{x}_f$ (`+0.022000` on `unscrambling`, `+0.000513` on `shapes`, `+0.014649` on `deduction`, `+0.009045` on `units`), on the all-family mean $\bar{x}$ (`+0.011552`), and on the retained `units` $T$ (`-0.093077` vs `-0.161892`, difference `+0.068815`). However, the `+0.0090` to `+0.0116` $\bar{x}$ gap is below the `.02` to `.09` projected magnitude band. | **Direction HIT (`4/4` families on $\bar{x}_f$, `units` on $D_f$); magnitude LOW on $\bar{x}$** |
| **4. Shared family witness exists (`unscrambling` and `shapes`)** | Selectivity and forecast come from disjoint subsets or no family clears $\bar{x}_f > .05$ and $D_f > .10$ | Zero families clear $\bar{x}_f > .05$ (`max` $\bar{x}_f = +0.024000$ on `olmo2_1b/unscrambling`), and both `unscrambling` (`n_pos=2`) and `shapes` (`n_pos=0`) are outcome-ineligible. | **DISCONFIRMED** |

## 5. Named secondaries (`S1..S8`) and controls

| Secondary | Projection call | Saved result in `analysis.json` | Grade |
|---|---|---|---|
| **Untrained `twin` control ($k=16$)** | $\bar{x}_{\text{twin}} \in [-.015, +.015]$, $T_{\text{twin}} \in [-.040, +.040]$, non-firing | $\bar{x}_{\text{twin}} = 0/1 = 0.000000$ on all 4 families (`deduction`, `shapes`, `units`, `unscrambling`, `1000/1000` unsupported renders per family); $T_{\text{twin}} = 0/1 = 0.000000$ on both primary strata. | **HIT** |
| **S1 (Competitor scores: $d, u, \text{rate}, \text{wrong}$)** | $T_u, T_d \in [.06, .24]$ while $T_x \ge .10$ | On `units`: availability $T_u = +0.141428$ (`pythia_1b`) and $+0.186153$ (`olmo2_1b`) — both inside `[.06, .24]`; wrong-target rate $T_{\text{wrong}} = +0.199636$ and $+0.198074$; correct rate $T_{\text{rate}} = +0.013188$ and $+0.143512$. By contrast, raw contrast $T_d = -0.125057$ and $-0.060064$, and conditional contrast $T_x = -0.161892$ and $-0.093077$. | **$T_u \in [.06, .24]$ HIT; $T_d, T_x$ MISS (negative)** |
| **S2 (Canonical vs sham rendering)** | $\left|\bar{x}_{\text{can}} - \bar{x}_{\text{sham}}\right| \le .05$ and positive paired-success agreement across checkpoints | On `units`, $\bar{x}_{\text{can}} - \bar{x}_{\text{sham}} = -0.015630$ (`pythia_1b`: `-0.005362` vs `+0.010268`) and $+0.004432$ (`olmo2_1b`: `+0.013714` vs `+0.009283`), both well within $\pm .05$. Outcome joint agreement across all 26 checkpoints is `993/1000 = 0.993000` (`units`), `12989/13000 = 0.999154` (`unscrambling`), and `1.000000` (`deduction`, `shapes`). | **HIT** |
| **S3 (Per-family availability $\bar{u}_f$ ordering)** | `arithmetic` (`units`) lowest $\bar{u}_f$; `shapes` and `deduction` highest $\bar{u}_f$ | Actual $\bar{u}_f$: `unscrambling` has by far the lowest $\bar{u}_f$ (`0.000508` `pythia_1b`, `0.003641` `olmo2_1b`, `996` and `974` unsupported renders), followed by `units` (`0.042742`, `0.169891`), while `shapes` (`0.084250`, `0.191820`) and `deduction` (`0.224648`, `0.119375`) have the highest $\bar{u}_f$. | **Partial: `shapes`/`deduction` highest $\bar{u}_f$ HIT; lowest $\bar{u}_f$ was `unscrambling`, not `units` (MISS)** |
| **S4 (Stratification sensitivity: base, median-$u$, tercile-$u$)** | Attenuation by `.00` to `.04` while keeping $T > .08$ | Across `base -> median -> tercile` on `units`, $T$ is stable in magnitude (`pythia_1b`: `-0.160350 -> -0.161892 -> -0.157822`; `olmo2_1b`: `-0.097780 -> -0.093077 -> -0.085517`), changing by less than `.013`, but remains negative throughout ($< .08$). | **Stability across partitions HIT; sign/level $T > .08$ MISS** |
| **S5 (Draw-budget nesting $k=16/32/64$ and split halves)** | Monotonic $\bar{x}$ increase across $k=16 \to 32 \to 64$; positive split-half agreement | On `units`, $\bar{x}$ across $k=16 \to 32 \to 64$ is `0.000533 -> -0.008565 -> +0.002453` (`pythia_1b`) and `+0.015670 -> +0.013909 -> +0.011499` (`olmo2_1b`) — non-monotonic and near zero. Disjoint 32-draw halves give consistent negative $T$ (`pythia_1b`: `-0.115052` vs `-0.107776`, diff `-0.007276`; `olmo2_1b`: `-0.120128` vs `-0.049519`, diff `-0.070610`). | **Monotonic $\bar{x}$ increase MISS; split-half $T$ consistency HIT** |
| **S6 (Outcome definitions and nonmonotonic losses)** | Joint count $y_i$ and first-joint-success speed agree in sign; minority nonmonotonic losses | On `units`, joint count $T$ and `first_joint_order` $T$ agree closely in sign and magnitude (`pythia_1b`: `-0.161892` vs `-0.152402`; `olmo2_1b`: `-0.093077` vs `-0.098728`), as do individual member arms `q0/q0s/q1/q1s` (`-0.0659` to $-0.0266$ for `pythia_1b`; `-0.0374` to $-0.0213$ for `olmo2_1b`). Nonmonotonic later losses occur on `46/500` `units` pairs (`46/50` ever-joint-positive pairs) and `2/500` `unscrambling` pairs. | **Sign agreement and nonmonotonicity HIT** |
| **S7 (Model-free baselines)** | `deduction` endpoint shortcut (`500/500`) and lexical/heuristic baselines retained as scope limitation | `deduction/endpoint` achieves `500/500` canonical and sham joint successes ($\bar{u}=1, \bar{x}=1$), `deduction/querywordonly` achieves `25/500` canonical and sham joint successes, and all `49` applicable / `35` `N/A` baseline cells are retained; on `units`, every applicable deterministic baseline has $\bar{x} = 0$ and $T = 0$. | **HIT** |
| **S8 (Exact target-label reversal identity)** | Swapping $(a_0, a_1) \mapsto (a_1, a_0)$ negates $x_i, d_i$ and preserves $u_i$ with zero exceptions | `status: "EXACT"` across all `8,000` `pythia_1b`, `8,000` `olmo2_1b`, `2,000` `twin`, and `24,500` applicable baseline pair evaluations (`17,500` `N/A` retained), with unchanged raw digests before and after. | **HIT** |
