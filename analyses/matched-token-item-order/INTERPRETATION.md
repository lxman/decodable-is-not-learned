# Matched-token item order: small-model tails order resolution across the parameter ladder

**Completed 2026-10-24.** Fixed-before-run reuse analysis on the committed Exp 5
matched-token Pythia ladder (`1.4b, 2.8b, 6.9b, 12b` at ten shared checkpoints;
`410m` and `1b` excluded from all outcome vectors so predictor and outcome never
share a model size). Rules were committed at `15275edd3`, analyzer and synthetic
tests at `dc119e5d5`; one production run against pinned Git tree
`5154f8935dc79e478b0853cbe39a39d931f00177` (`exp7-closed`), 7,592 verified
repository files, 1,020,000 re-derived Exp 5 correctness bits, and saved-output
verification exit 0. Full tables: [results/REPORT.md](results/REPORT.md).

## Main reading: item order transfers to the parameter-size axis

Holding training tokens fixed at the final checkpoint (`step143000`,
**299.893 billion tokens**), the item-level sampled output tails of `Pythia-1b`,
`Pythia-410m`, and cross-family `OLMo-2 1B` order which individual items are
solved across the four larger Pythia parameter sizes (`1.4b, 2.8b, 6.9b, 12b`),
within structural difficulty strata (`strata_2g.py`):

| Rung set | Predictor | Eligible rungs | Stratified $T$ | Perm $p$ | Family-boot 95% CI | Equal-family mean | Unstratified $T$ | Pooled $D$ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `R_CAP` (9) | `pythia_1b_k256` | 9 | **+0.218** | 0.0001 (1/10001) | [+0.107, +0.369] | +0.238 | +0.214 | +0.274 |
| `R_CAP` (9) | `olmo2_1b_k64` | 9 | **+0.278** | 0.0001 (1/10001) | [+0.130, +0.502] | +0.312 | +0.321 | +0.336 |
| `R_CAP` (9) | `pythia_1b_k64` | 9 | **+0.165** | 0.0001 (1/10001) | [+0.070, +0.274] | +0.178 | +0.156 | +0.204 |
| `R_CAP` (9) | `pythia_410m_k256` | 9 | **+0.206** | 0.0001 (1/10001) | [+0.072, +0.385] | +0.243 | +0.199 | +0.248 |
| `R_CAP` (9) | `pythia_410m_k64` | 9 | **+0.145** | 0.0001 (1/10001) | [+0.049, +0.253] | +0.178 | +0.133 | +0.175 |
| `R_CAP` (9) | `probe_1b` | 9 | **+0.026** | 0.1293 | [-0.017, +0.059] | +0.032 | +0.064 | +0.016 |
| `R_CAP` (9) | `wrong_prior_1b` | 9 | **+0.243** | 0.0001 (1/10001) | [+0.130, +0.444] | +0.240 | +0.235 | +0.251 |
| `R_PRED11` (11) | `pythia_1b_k64` | 11 | **+0.153** | 0.0001 (1/10001) | [+0.074, +0.243] | +0.156 | +0.157 | +0.195 |
| `R_PRED11` (11) | `pythia_410m_k64` | 11 | **+0.133** | 0.0001 (1/10001) | [+0.052, +0.225] | +0.150 | +0.135 | +0.172 |
| `R_PRED11` (11) | `probe_1b` | 11 | **+0.011** | 0.2740 | [-0.031, +0.045] | +0.008 | +0.042 | +0.010 |

On `R_CAP`, `olmo2_1b_k64` is positive on **all 9/9 rungs** (`+0.065` on
`sub4_mid` to `+0.737` on `add_base8`), and on `R_PRED11`, `pythia_1b_k64` is
positive on **all 11/11 rungs** (`+0.011` on `add3_mid` to `+0.412` on
`sub_base8`). Raising the Pythia sampling budget from $k=64$ to $k=256$ lifts
size-axis concordance from `+0.165` to `+0.218` at `1b` (`+0.053`, 8/9 rungs
rising) and from `+0.145` to `+0.206` at `410m` (`+0.061`).

Across the full 34-rung battery unstratified at `step143000`, `pythia_1b_k64`
averages **$D = +0.286$** (`[+0.165, +0.411]`) across the 29 informative rungs
(15 families) and **$D = +0.280$** (`[+0.160, +0.413]`) across the 24 rungs with
$n_{\text{pos}} \ge 20$ (13 families).

## Robustness across greedy-zero items, earliest size, and `2.8b` exclusion

1. **Greedy-zero restriction (`410m = 0` and `1b = 0` at `step143000`):**
   Restricting each rung strictly to items that neither `410m` nor `1b` solves
   under greedy decoding leaves the size-ladder ordering intact:
   - `pythia_1b_k256`: **$T = +0.194$** ($p = 0.0001$, 9 rungs)
   - `olmo2_1b_k64`: **$T = +0.270$** ($p = 0.0001$, 9 rungs)
   - `pythia_1b_k64`: **$T = +0.138$** on `R_CAP` and **$+0.129$** on `R_PRED11` ($p = 0.0001$)
   Items that a 1B model cannot emit greedily, but reaches more often under
   temperature-1 sampling, are the items that cross the greedy threshold when
   parameter count increases from 1B to 1.4B–12B at the same token budget.

2. **Earliest-size emergence rank (`y_143k_first_size`, `1.4b = 4 .. 12b = 1`):**
   Scoring each item solely by the smallest parameter count in `{1.4b, 2.8b, 6.9b, 12b}`
   that solves it at `step143000` gives **$T = +0.198$** (`pythia_1b_k256`),
   **$T = +0.263$** (`olmo2_1b_k64`), and **$T = +0.147$** (`pythia_1b_k64` on `R_CAP`;
   `+0.143` on `R_PRED11`, all $p = 0.0001$). Higher small-model sampled rates
   indicate items that resolve at smaller parameter counts first.

3. **Excluding `2.8b` (`1.4b, 6.9b, 12b`) and individual larger sizes:**
   In `analyses/matched-token/`, `2.8b` was the nonmonotonic mean-accuracy peak.
   Removing `2.8b` from the outcome ladder **increases** concordance for every
   sampled predictor: `pythia_1b_k256` rises from `+0.218` to **`+0.237`**,
   `olmo2_1b_k64` rises from `+0.278` to **`+0.306`**, and `pythia_1b_k64`
   rises from `+0.165` to **`+0.184`** on `R_CAP` (`+0.153` to **`+0.172`** on
   `R_PRED11`). Evaluated on each larger model size individually at `step143000`,
   `pythia_1b_k256` and `olmo2_1b_k64` achieve:
   - `1.4b` (6 eligible `R_CAP` rungs): `+0.379` and `+0.440` ($p = 0.0001$)
   - `2.8b` (8 eligible `R_CAP` rungs): `+0.210` and `+0.294` ($p = 0.0001$)
   - `6.9b` (9 eligible `R_CAP` rungs): `+0.235` and `+0.302` ($p = 0.0001$)
   - `12b` (9 eligible `R_CAP` rungs): `+0.235` and `+0.297` ($p = 0.0001$)

4. **All 10 shared checkpoints (`step1000` to `step143000`):**
   From `step2000` (4.194B tokens) through `step143000` (299.893B tokens),
   `pythia_1b_k256` and `olmo2_1b_k64` positively order size-ladder resolution at
   every checkpoint (`+0.218` to `+0.495` for `pythia_1b_k256`; `+0.177` to
   `+0.344` for `olmo2_1b_k64`). Over the full 10-checkpoint × 4-size grid sum
   (`y_grid_40`), `pythia_1b_k256` reaches **`+0.264`** and `olmo2_1b_k64`
   reaches **`+0.262`** ($p = 0.0001$).

## Output tail vs. linear probe and cross-family conditioning on the size axis

The same two decompositions established along the training-step axis in
Experiments 2g–2j reappear along the parameter-size axis:

- **Output tail vs. hidden-state linear probe:** `exp2g`'s committed `1b`
  hidden-state linear probe margin (`probe_1b`) is near zero on the size ladder
  (`T = +0.026, p = 0.1293` on `R_CAP`; `T = +0.011, p = 0.2740` on `R_PRED11`,
  and `T = -0.005, p = 0.5982` on `y_grid_40`). Conditioned on the `1b` sampled
  tail (`probe_1b | pythia_1b_k256 > 0`), the probe adds `+0.033` ($p = 0.0796$),
  whereas `pythia_1b_k256` conditioned on the probe's median split retains its
  full signal (**`T = +0.217`**, $p = 0.0001$ vs. `+0.218` unconditioned).
- **Shared cross-family prior + within-lineage increment:** On `R_CAP`, both
  directions of cross-family conditioning remain positive ($p = 0.0001$):
  `olmo2_1b_k64` conditioned on `pythia_1b_k256 > 0` gives **`T = +0.254`**, and
  `pythia_1b_k256` conditioned on `olmo2_1b_k64 > 0` gives **`T = +0.173`**
  (`+0.159` under median split). And `exp2j`'s wrong-answer emission prior
  (`wrong_prior_1b`, which never inspects whether a sampled draw is right or
  wrong for its own prompt) reaches **`T = +0.243`** ($p = 0.0001$), confirming
  that output-form emission habits carry a major share of the size-axis item
  ordering alongside prompt-specific competence.

## Scope and limitations

This is a fixed-before-run reuse analysis on committed artifacts, not a sealed
forecast. The permutation $p$-values and bootstrap intervals quantify within-stratum
concordance and task-family resampling sensitivity on these committed datasets.
Holding training tokens fixed across Pythia sizes still bundles parameter count
with architectural dimensions and learning-rate schedule choices across the suite.

## Execution and evidence

- Pre-analysis plan commit: `15275edd32fb0b0dbbd676db87eb0e8896fc15f1`
- Analyzer and test commit: `dc119e5d5258d5248332efaa0a3cf3dc3ab6767a`
- Pinned data source commit: `5154f8935dc79e478b0853cbe39a39d931f00177` (`exp7-closed`)
- Generated at: `2026-10-25T02:29:50.710393+00:00`
- `results/summary.json` SHA256: `b3bc98b196f4aa9e0b83c9725f87748ce05d62bc3c9c9b85a43359494137e99e`
- `results/REPORT.md` SHA256: `f0855e8c08138a7bc75d1ac3f5744b8478df24e31b46b52f149836f8bb2c627c`
- **Do not rerun the production analysis.** Use `verify_outputs.py` to audit the saved outputs.
