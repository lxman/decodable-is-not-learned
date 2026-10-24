# Matched-token Pythia size-ladder item-order analysis

## Authorization and status

On 2026-10-24, Michael selected **Option 1** ("Let's carry out option 1"):
an existing-data analysis testing whether small-model sampled output tails
(`Pythia-1B`, `Pythia-410M`, and cross-family `OLMo-2 1B`) order which
individual items resolve as **parameter count increases at fixed training
tokens** (`1.4B → 2.8B → 6.9B → 12B`) on the matched-token Pythia ladder.

Like its parent (`analyses/matched-token/`, completed 2026-10-04 at
`b770e8ebd`), this is a fixed-before-run reuse analysis on committed bytes,
with no new model contact and no GPU rental. Every input — the 60 Exp 5
checkpoint units, the `exp2d`/`exp2k` Pythia sampled draws, the `exp2i`
`OLMo-2 1B` sampled draws, and the `exp2g` linear probe readings — is already
on disk and known in principle. Nothing here is a sealed forecast. This plan
is committed and pushed before any size-axis item-order concordance is
computed. The analyzer runs once after synthetic-fixture tests and
`--validate-only` provenance verification pass.

## Question

In Experiments 2g–2n and 6, a 1B model's sampled output tail ordered when
individual items emerge across **training checkpoints of a fixed-size model**.
In `analyses/matched-token/`, holding training tokens fixed across six Pythia
sizes (`410m, 1b, 1.4b, 2.8b, 6.9b, 12b`) showed a +4.159 percentage-point
aggregate accuracy gain from 410M to 12B at the final checkpoint (`step143000`,
299.893B tokens), with nonmonotonic size ordering (2.8B highest in mean
accuracy, 6.9B and 12B clearing the most rungs).

This analysis asks the item-grain question that `analyses/matched-token/PLAN.md`
left open:

1. **Same-lineage size-axis ordering:** Holding training tokens fixed, do
   `Pythia-1B` ($k=256$ and $k=64$) and `Pythia-410M` ($k=256$ and $k=64$)
   sampled counts order which individual items are solved across the larger
   Pythia parameter ladder (`1.4b, 2.8b, 6.9b, 12b`), within structural
   difficulty strata (`strata_2g.py`)?
2. **Cross-family size-axis ordering:** Does `OLMo-2 1B` ($k=64$), trained on
   an independent corpus and architecture, order which individual items resolve
   across Pythia's parameter ladder (`1.4b, 2.8b, 6.9b, 12b`) at fixed training
   tokens?
3. **Greedy-zero restriction (`410m=0 ∧ 1b=0`):** Does the size-axis item
   ordering survive when restricted to items that neither `410m` nor `1b`
   solves under greedy decoding at `step143000`?
4. **Layer and habit decomposition on the size axis:** How does the sampled
   output tail compare against `exp2g`'s committed `1b`/`410m` hidden-state
   linear probe reading (`probe_2g`) and `exp2j`'s wrong-answer emission prior
   (`wrong_answer_prior`) along the parameter-size axis?

## Inputs and inventory disclosure

All inputs are read from committed repository artifacts and byte-verified
against Git tree `5154f8935dc79e478b0853cbe39a39d931f00177` (`exp7-closed`):

1. **Outcome units (60 units, 2,040 rung records, 1,020,000 item bits):**
   `experiments/exp5/results/units/<size>/step<step>/` for
   `SIZES = ("410m", "1b", "1.4b", "2.8b", "6.9b", "12b")` and
   `STEPS = (1000, 2000, 4000, 5000, 6000, 8000, 16000, 32000, 100000, 143000)`.
   Every correctness bit is re-derived from the stored continuation through
   `exp3c`'s total verify wrapper and checked against `analyses/matched-token/results/counts.csv`.
2. **Outcome sizes (`OUTCOME_SIZES`):**
   `("1.4b", "2.8b", "6.9b", "12b")`. The two predictor sizes (`410m`, `1b`)
   are excluded from every outcome vector $y_i$ so predictor and outcome never
   share a model size.
3. **Rung sets:**
   - `R_CAP` (9 rungs, `exp2i`/`exp2k`):
     `("add3_mid", "add_base8", "antonym", "antonym6", "arith_next", "odd6", "sub3_mid", "sub4_mid", "sub_base8")`.
     All 9 clear `2d`'s binomial reference bar at `step143000` on at least one
     size in `OUTCOME_SIZES`, have structural difficulty covariates in
     `strata_2g.py`, and carry both `k=256` Pythia draws (`exp2k`) and `k=64`
     `OLMo-2 1B` draws (`exp2i`).
   - `R_PRED11` (11 rungs, `strata_2g.PREDICTOR_RUNGS`):
     `R_CAP ∪ ("count_div13", "median5")`. All 11 clear `2d`'s binomial
     reference bar at `step143000` on at least one size in `OUTCOME_SIZES`,
     have structural difficulty covariates in `strata_2g.py`, and carry `k=64`
     Pythia draws (`exp2d`) and linear probe readings (`exp2g`).
   - `R_ALL34` (34 rungs, `battery_2d.RUNGS`):
     full battery unstratified reading over all rungs with at least one
     informative outcome pair ($0 < n_{\text{pos}} < 500$), and separately over
     rungs with $n_{\text{pos}} \ge 20$.
4. **Predictor files:**
   - `pythia_1b_k256` and `pythia_410m_k256`: `experiments/exp2k/results/k256/<size>_trained/<rung>.draws.jsonl.gz`
     and `<rung>.json` (9 `R_CAP` rungs, 256 draws/item; seed-0 block verified
     byte-identical to `exp2d` main tier).
   - `pythia_1b_k64` and `pythia_410m_k64`: `experiments/exp2d/results/main/<size>_trained/<rung>.draws.jsonl.gz`
     and `<rung>.json` (all 34 rungs, 64 draws/item).
   - `olmo2_1b_k64`: `experiments/exp2i/results/predictor/olmo_1b/<rung>.draws.jsonl.gz`
     and `<rung>.json` (9 `R_CAP` rungs, 64 draws/item).
   - `probe_1b` and `probe_410m`: `experiments/exp2g/results/predictor/predictor_2g.json`
     (`1b` and `410m` out-of-fold probe margins and `strata` table across all
     11 `R_PRED11` rungs).
   - `wrong_prior_1b` and `wrong_prior_olmo1b`: `exp2j`'s wrong-answer emission
     frequency (`experiments/exp2j/functionals_2j.py:wrong_answer_prior`)
     computed from the committed `exp2d` (`1b`, $k=64$) and `exp2i`
     (`olmo_1b`, $k=64$) draw streams on `R_CAP`.

**Pre-analysis reads, disclosed:** `analyses/matched-token/PLAN.md`,
`INTERPRETATION.md`, `PROGRESS.md`, `analyze.py`, `results/REPORT.md`, and the
`step143000` rows of `results/counts.csv` (which already printed the per-rung
correct counts and `reference_clear` flags); `experiments/exp2g/stats_2g.py`,
`strata_2g.py`, `experiments/exp2i/analyze_2i.py`, and
`experiments/exp2k/analyze_2k.py` / `battery_2k.py`. No size-axis item-order
concordance ($D$ or $T$) was computed during design or inventory.

## Fixed outcomes and comparisons

For each item $i \in \{0, \dots, 499\}$ on rung $r$, let
$b_{t, s, r, i} \in \{0, 1\}$ denote the re-derived greedy correctness bit at
checkpoint $t \in \text{STEPS}$ and size $s \in \text{OUTCOME\_SIZES} = (\text{1.4b}, \text{2.8b}, \text{6.9b}, \text{12b})$.

1. **Primary size-ladder outcome at `step143000` (`y_143k_count`):**
   $$y_i^{(143\text{k})} = \sum_{s \in (\text{1.4b}, \text{2.8b}, \text{6.9b}, \text{12b})} b_{143\text{k}, s, r, i} \in \{0, 1, 2, 3, 4\}$$
   Within-stratum Somers' $D$ (`stats_2g.somers_d_within`) and unstratified
   Somers' $D$ are computed for:
   - `pythia_1b_k256`, `olmo2_1b_k64`, `pythia_1b_k64`, `pythia_410m_k256`,
     `pythia_410m_k64`, `probe_1b`, `probe_410m`, `wrong_prior_1b`, and
     `wrong_prior_olmo1b` on `R_CAP` (9 rungs);
   - `pythia_1b_k64`, `pythia_410m_k64`, `probe_1b`, and `probe_410m` on
     `R_PRED11` (11 rungs);
   - `pythia_1b_k64` and `pythia_410m_k64` unstratified on `R_ALL34` (all
     informative rungs and $n_{\text{pos}} \ge 20$ rungs).
2. **Earliest-size emergence rank at `step143000` (`y_143k_first_size`):**
   $$y_i^{(\text{first}, 143\text{k})} = \max\bigl(\{0\} \cup \{5 - m : m \in \{1,2,3,4\},\; b_{143\text{k}, s_m, r, i} = 1\}\bigr) \in \{0, 1, 2, 3, 4\}$$
   where $(s_1, s_2, s_3, s_4) = (\text{1.4b}, \text{2.8b}, \text{6.9b}, \text{12b})$,
   so an item solved at `1.4b` scores `4`, first solved at `2.8b` scores `3`,
   first solved at `6.9b` scores `2`, first solved at `12b` scores `1`, and
   never solved across `1.4b..12b` scores `0`.
3. **Greedy-zero restriction at `step143000` (`y_143k_greedy_zero`):**
   Within each rung, restrict to items where $b_{143\text{k}, \text{410m}, r, i} = 0$
   and $b_{143\text{k}, \text{1b}, r, i} = 0$, testing whether `pythia_1b_k256`,
   `olmo2_1b_k64`, and `pythia_1b_k64` order which greedy-failed items become
   greedy-solvable across `1.4b..12b`.
4. **Individual larger-size endpoints at `step143000` (`1.4b`, `2.8b`, `6.9b`, `12b`)
   and the `2.8b`-excluded ladder (`1.4b, 6.9b, 12b`):**
   Since `2.8b` has the highest mean accuracy on arithmetic rungs, report
   each of the four larger sizes individually at `step143000` and the three-size
   sum excluding `2.8b` (`y_143k_no28b`) so any `2.8b`-specific effect is
   separated from the rest of the size ladder.
5. **Per-checkpoint size-ladder curve and 10-checkpoint × 4-size grid sum:**
   For each shared checkpoint $t \in \text{STEPS}$, compute $y_i^{(t)} = \sum_{s \in \text{OUTCOME\_SIZES}} b_{t, s, r, i}$
   and report the rung-mean stratified $T$ across all eligible rungs in `R_CAP`
   and `R_PRED11`, plus the 10-checkpoint × 4-size sum $y_i^{(\text{grid})} \in \{0, \dots, 40\}$
   and the 8-checkpoint shared-spine sum $y_i^{(\text{spine})} \in \{0, \dots, 32\}$
   (excluding steps `5000` and `6000`).
6. **Composite-stratum conditioning (probe beyond sampler, and lineage beyond cross-family):**
   Using `exp2h`/`exp2i`'s zero-cut composite strata (`strata × 1{x_base > 0}`
   or median bucket on positive counts), report:
   - `probe_1b` conditioned on `pythia_1b_k64` (`R_PRED11`) and on `pythia_1b_k256` (`R_CAP`);
   - `pythia_1b_k256` conditioned on `olmo2_1b_k64`, and `olmo2_1b_k64` conditioned on `pythia_1b_k256` (`R_CAP`).

## Uncertainty and reference benchmarks

For each multi-rung test on `R_CAP` and `R_PRED11`, compute:
- `stats_2g.perm_test` (`N_PERM = 10,000`, `seed = 20261024`), permuting the
  predictor within `rung × stratum` and recording `T`, `p`, `null_mean`, and
  `null_sd`.
- Per-rung item bootstrap 95% intervals (`stats_2g.bootstrap_d`, `N_BOOT = 1,000`,
  `seed = 20261024`).
- Family-cluster bootstrap 95% intervals (`10,000` draws of the represented
  families with replacement, `seed = 20261004`, matching `analyses/matched-token/`)
  for both the equal-rung mean $T$ and the equal-family mean.

Because both predictors and outcomes are already on disk, `p` and the bootstrap
intervals are reported as descriptive precision/reference benchmarks on
committed data, not as a sealed confirmatory forecast.

## Deliverables and checks

`analyses/matched-token-item-order/` contains:
- `PLAN.md` (this file) and `PROGRESS.md`
- `analyze.py` (write-once production CLI + `--validate-only` mode; byte-binds
  all repository imports and data files against `5154f8935` at entry and exit)
- `test_analyze.py` (synthetic unit tests covering Somers' $D$ orientation,
  `first_size` encoding, greedy-zero restriction, `2.8b`-exclusion, composite
  strata, family bootstrap, tamper refusal, and write-once behavior)
- `verify_outputs.py` (saved-output auditor that recomputes aggregates and
  report tables from `results/summary.json` and CSVs without rerunning
  permutations or bootstraps)
- `results/summary.json`, `results/per_rung.csv`, `results/checkpoint_curve.csv`,
  `results/all_rungs_143k.csv`, `results/provenance.json`, `results/REPORT.md`,
  and `INTERPRETATION.md`.
