# Experiment 1 — Build Ledger

Traceability record for `experiments/exp1/`. Every milestone maps to the design-doc
rule it implements, the commit that landed it, and its test status. Trust this ledger
plus `git log` over recollection. Companion docs: `../../experiment-1-design.md`
(frozen, preregistered) and `../../experiment-1-implementation-plan.md`.

The **M3.5 freeze** (tag `exp1-analysis-frozen`) is the epistemic hinge: everything
above it may still be refined; nothing below it (result-grade data) may change the
thresholds or the analysis. Operational choices made *before* the freeze are logged
here so they are auditable and can never be mistaken for post-hoc instrument-tuning.

**Frozen at M3.5:** `signatures/schema.py` (the RunRecord contract) and `analyze.py`
(the §4 PASS/FAIL logic). These two files are not edited after the tag; a needed change
becomes a new file plus a note here. Signature *internals* (probe/sampling/forecast/
activations, tasks, models, training) remain editable — the freeze binds the analysis
to the schema, not to how signatures are computed.

## Milestones

| Milestone | What landed | Implements (design §) | Commit | Tests |
|---|---|---|---|---|
| M0 | Scaffold `experiments/exp1/` tree; deps (scikit-learn, scipy, matplotlib, pytest) into `~/emergence-lab/.venv`; `checkpoints/` gitignored | §5 code location | `3123f99` | — |
| M1 | `signatures/stats.py` (Clopper–Pearson, permutation null, Cohen's d, Bonferroni); `signatures/schema.py` (RunRecord + result dataclasses, JSON round-trip, categorical validation) | §4 statistics; the frozen data contract | `8628e33` | 24 ✓ |
| M2 | `signatures/activations.py` (residual-stream hooks); `probe.py` (S1); `sampling.py` (S2); `forecast.py` (S3); planted-signal tests | §3 signature operationalization | `5202fb5` | 43 ✓ (cumulative) |
| M3 | Phase-A pipeline debug: `models/transformer.py`, `tasks/binding_task.py`, `train/{loop,checkpointing}.py`, `configs/phase_a.py`, `run/{run_phaseA,provenance}.py`; end-to-end run → `results/phaseA/seed0.json` | §2 staged build (Phase A); §5 run order step 1 | `5c7afbd` | 54 ✓ (cumulative) |
| M3.5 | **FREEZE** `schema.py` + `analyze.py`; git tag `exp1-analysis-frozen` | §4 overall PASS / reportable FAIL; statistics hygiene | `PENDING` | 63 ✓ (cumulative) |
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

**M3 — Phase A (pipeline debug, added during integration; all pre-freeze)**
- Probe features are standardized (`StandardScaler` fit on the train split only) before
  logistic regression, in both `probe_below_threshold` and `best_probe_accuracy`.
  Unscaled residual-stream activations made lbfgs fail to converge; the scaler leaks no
  validation information. Applies to every downstream probe (Exp 2/4 too).
- Phase-A below-threshold rule is `argmax eval acc < 2 × chance` (not the frozen
  grokking `< 5%`), because 16-way chance (6.25%) already exceeds 5%. This is a
  Phase-A-only convenience; the grokking/Lubana runs use the frozen §3 rules.
- Phase A is NOT scored. Its transition (in-context-retrieval / induction) forms very
  early (~step 108 of 4000) and sharply, so S3's precursor is mostly flat-then-sudden
  and the forecast degenerates (reads absent). That is expected and, if anything,
  re-illustrates the essay's point that naive extrapolation of a sudden transition
  fails — the reason S3 is defined on a smooth precursor in the first place.
- The committed `results/phaseA/seed0.json` carries git SHA `59b1c85-dirty`: it was
  generated from the working tree that became the M3 commit. Debug artifact; M4+ scored
  runs will be generated from a committed (clean) tree so their provenance SHA is exact.

**M3.5 — frozen analysis (`analyze.py`; frozen at the tag)**
- Continuous separation is scored on `s1.accuracy` (S1) and `s2.rate_point` (S2) — the
  two quantities design §4 names as sharing a continuous scale across systems.
- S3 categorical verdicts require the pattern in EVERY seed of an evaluable size
  (grokking present in all, Lubana-below absent in all); a single off-pattern seed is a
  reportable FAIL. Strict, matching the design's brand.
- A size is "evaluable" only if all three scored rows have ≥5 seeds; PASS needs ≥3
  evaluable sizes (design §4 replication). Before enough data exists the verdict is
  `INSUFFICIENT_DATA` — an honest third state; design names only PASS/FAIL for the
  data-complete case, and this never fabricates one of those early.
- Phase A is excluded from the scored table (it is a pipeline-debug system).

## Environment notes

- Runs on the Mac mini (M4 Pro, 48 GB, MPS); DGX Sparks untouched. See
  `../../environment.md`.
- sklearn ≥1.7 removed `LogisticRegression(multi_class=...)`; probe relies on the
  automatic multinomial behaviour (venv has scikit-learn 1.9.0).
- Run tests: `cd experiments/exp1 && python -m pytest`.
