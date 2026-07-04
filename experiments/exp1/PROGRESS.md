# Experiment 1 — Build Ledger

Traceability record for `experiments/exp1/`. Every milestone maps to the design-doc
rule it implements, the commit that landed it, and its test status. Trust this ledger
plus `git log` over recollection. Companion docs: `../../experiment-1-design.md`
(frozen, preregistered) and `../../experiment-1-implementation-plan.md`.

The **M3.5 freeze** (tag `exp1-analysis-frozen`) is the epistemic hinge: everything
above it may still be refined; nothing below it (result-grade data) may change the
thresholds or the analysis. Operational choices made *before* the freeze are logged
here so they are auditable and can never be mistaken for post-hoc instrument-tuning.

## Milestones

| Milestone | What landed | Implements (design §) | Commit | Tests |
|---|---|---|---|---|
| M0 | Scaffold `experiments/exp1/` tree; deps (scikit-learn, scipy, matplotlib, pytest) into `~/emergence-lab/.venv`; `checkpoints/` gitignored | §5 code location | `3123f99` | — |
| M1 | `signatures/stats.py` (Clopper–Pearson, permutation null, Cohen's d, Bonferroni); `signatures/schema.py` (RunRecord + result dataclasses, JSON round-trip, categorical validation) | §4 statistics; the frozen data contract | `8628e33` | 24 ✓ |
| M2 | `signatures/activations.py` (residual-stream hooks); `probe.py` (S1); `sampling.py` (S2); `forecast.py` (S3); planted-signal tests | §3 signature operationalization | `4a8ff29` | 43 ✓ (cumulative) |
| M3 | Phase-A pipeline debug (binding task end-to-end) | §2 staged build (Phase A) | — | — |
| M3.5 | **FREEZE** `schema.py` + `analyze.py`; git tag `exp1-analysis-frozen` | §4 statistics hygiene | — | — |
| M4 | Grokking (base size, 5 seeds) + gt-check | §2 resolution exemplar | — | — |
| M5 | Lubana below + above (base size, 5 seeds) | §2 percolation exemplar + control | — | — |
| M6 | Size sweep 1M/10M/100M | §4 secondary size sweep | — | — |
| M7 | Run frozen `analyze.py`; fill truth table; report | §4 overall PASS / reportable FAIL | — | — |

## Operational choices (pre-freeze, auditable)

Where the frozen design doc specifies a *rule* but leaves the *mechanism* to
implementation, the choice is recorded here and in the relevant module docstring.

**S1 — probe (`probe.py`)**
- Multiple-comparison correction is Bonferroni across every `(layer, token)`
  candidate, not layers alone: token position is also selected on validation, so it
  belongs to the comparison family. Stricter than layer-only — consistent with the
  design's strict-but-passed brand (§4).
- The label-permutation null shares one fixed, seeded train/val split with the
  observed fit, so observed and null differ only in the labels.
- `below_threshold` (argmax test acc < 5% at this checkpoint) is caller-supplied;
  `present` requires it, per the §3 rule.

**S2 — sampling (`sampling.py`)**
- Pass rate is measured at sample granularity, pooled across queries:
  `rate = verified / total`, `n = n_per_query * n_queries`. This is the quantity the
  ~3×10⁻⁵ budget floor (§4) refers to and on which Clopper–Pearson is exact.
- The guessing floor is passed in (design: from an untrained control); this module
  does not define it.
- `present` and `absent` are mutually exclusive; the middle zone
  (`lower ≤ floor < upper`) is reported as neither — an indeterminate campaign
  needing more budget — never coerced. `cp_upper` is always a number (no claimed zero).

**S3 — forecast (`forecast.py`)**
- "Extrapolate to predict the transition" = fit the precursor vs axis on
  pre-transition points, solve for the axis value at which it reaches a preregistered
  `target_level` y\*. y\* is frozen with the task config, never fit to the observed
  transition.
- Uncertainty is by seeded bootstrap over the pre-transition points; `interval90` and
  `slope_ci` are (5th, 95th) percentiles. Avoids fragile analytic inversion near
  slope 0.
- "Beats a no-transition baseline" = bootstrap slope CI excludes 0. A flat precursor
  reads absent.

## Environment notes

- Runs on the Mac mini (M4 Pro, 48 GB, MPS); DGX Sparks untouched. See
  `../../environment.md`.
- sklearn ≥1.7 removed `LogisticRegression(multi_class=...)`; probe relies on the
  automatic multinomial behaviour (venv has scikit-learn 1.9.0).
- Run tests: `cd experiments/exp1 && python -m pytest`.
