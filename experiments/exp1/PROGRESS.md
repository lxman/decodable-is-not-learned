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
| M3.5 | **FREEZE** `schema.py` + `analyze.py`; git tag `exp1-analysis-frozen` | §4 overall PASS / reportable FAIL; statistics hygiene | `8f7198d` (tag `exp1-analysis-frozen`) | 63 ✓ (cumulative) |
| M4 | Grokking harness + confirmation + scored 5-seed run. Harness `150a1b4`/`412f747`; instrument fixes `42cfb5c`; linear-S3 record `ae27930`; log-precursor method `e365c39`; **accepted scored row: S1 5/5, S2 5/5, S3 1/5, gt 5/5** | §2 resolution exemplar; §5 run order step 2 | `ef44e8d` | 73 ✓ (cumulative) |
| M5 | Lubana below + above, COMPLETE. Threshold gate reproduced computationally; language + LM loop + configs + confirmation driver built (`tasks/lubana_lang.py`, `train/lm_loop.py`, `configs/lubana.py`, `run/confirm_lubana.py`); both confirmation gates passed; 10/10 scored RunRecords at paper scale, all gt-certified, unanimous across seeds: above S1 present / S2 absent / S3 fail ×5, below 0/3 signatures ×5. | §2 percolation exemplar + control; §5 run order step 3 | `3a87242` + final-records commit | 89 ✓ (cumulative) |
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

**M4 — grokking (resolution row)**
- Grok-confirmation (seed 0, 40k steps, MPS) succeeded: textbook curve, train→1.0 by
  step 262 (memorization), test grokks 0.51→0.999 across steps 1318→1888. Certified via
  the memorization→generalization gap (mem@262, gen@1578). ~228k params (<1M, the "1M"
  bucket by order of magnitude).
- **Observed instability:** the 40k run showed transient weight-decay "slingshot"
  collapses at steps ~16k and ~40k (both accuracies crash to ~chance, then recover). A
  known grokking artifact. `total_steps` was therefore frozen at 10k (post-confirmation
  recipe refinement, not a threshold change): it captures pre-grok + the transition + a
  stable plateau (steps ~2.3k–13.6k are all perfect) and stops before the first
  slingshot. The trajectory to 10k is identical to the 40k run (no LR schedule).
- S1 is read at the **latest** below-threshold checkpoint (argmax test acc < 5%, the
  frozen §3 rule) — the most informative pre-transition point. Whether the probe fires
  there for grokking is the actual empirical question S1 tests; the verdict is reported
  as-is, not tuned.
- **Seed-0 shakeout of the scored driver exposed three instrument issues, all fixed
  BEFORE any scored data was committed** (the intended Phase-A-style shakeout, now on
  the first grokking seed). Every fix has an outcome-independent justification:
  1. *S2 `argmax_fails` was sample-size-dependent* — coded as "argmax solved zero of
     the 50 queries," which flips to False when the model is a hair above chance (~1
     query). Corrected to §3's intent: argmax UNRELIABLE = argmax pass rate over the
     queries < the frozen 5% level. (A rate threshold, the same frozen number — no new
     free parameter.)
  2. *The guessing floor was hardcoded `1/113`* instead of design §3's "empirical
     floor from an untrained control." Now the driver samples a random-init control
     identically and uses its Clopper–Pearson upper bound as the floor.
  3. *The probe was data-starved* at 2000 examples (~13/class for 113-way): it scored
     BELOW the model's own argmax (objective proof of under-resourcing — a linear
     readout of a linearly-present signal must be able to match the head) and gave a
     noisy, lagging S3 precursor. At 6000 (`probe_n`) the probe leads argmax and rises
     smoothly; S3's forecast lands within 8% of the true transition. `target_level`
     (0.5) was NOT touched.
- **MPS nondeterminism confirmed:** two seed-0 runs at the identical seed picked
  different below-threshold checkpoints (173 vs 602) and transition steps (1796 vs
  1536). Expected (environment.md); absorbed by the ≥5-seed requirement and the d≥2 bar.
- **S3 RECALIBRATION (option 2, log precursor — user-sanctioned, pre-committed).**
  The first 5-seed scored run read grokking (S1 5/5, S2 5/5, **S3 1/5**). Diagnosis:
  the forecaster itself is unstable (predictions ranged 841–3469 for a transition near
  1500), so the earlier "noisy target" hypothesis was insufficient — the linear
  extrapolation is misspecified. **One** principled change, decided on the
  misspecification (NOT by shopping transforms against the outcome): fit the precursor
  in **log space** (`s3_precursor_transform="log"`), because the pre-transition probe
  rise is the ~exponential bottom of a sigmoid, and a straight line there biases the
  forecast late (the ~2000-vs-1500 bias observed). `target_level` (0.5) and the frozen
  25% tolerance are UNCHANGED. The method is committed BEFORE re-running, so it is
  locked, not tuned. **Lubana-below remains the out-of-sample judge:** the same
  log-transformed S3 must keep percolation absent, or the change is rejected. The first
  (linear-S3) 5-seed run is preserved in git history as the pre-recalibration record.
- **S3 VERDICT ACCEPTED (user decision, 2026-07-04): grokking S3 = 1/5, reported
  as-is. No second fix.** Diagnosis on the log-S3 run: the log precursor fixed the
  point forecast (predictions clustered near truth; rel-errors 0.11–0.16 for three
  seeds vs 841–3469 scatter under the linear fit), but the frozen rule also requires
  90%-interval coverage, and the data-bootstrap interval is anti-conservative for
  extrapolation (it omits the prediction-uncertainty term), so seeds 2 and 3 miss
  coverage by 18 and 77 steps despite accurate forecasts. Fixing the interval
  estimator would be change #2; declined to protect the preregistration discipline.
  **Standing finding:** on the resolution exemplar the transition *location* is
  forecastable from the smooth precursor to ~11–16%, but calibrated 90% coverage is
  not achieved — S3 is directionally informative, not certifiable at the frozen bar.
  The essay's forecastability claim should be stated as "visible in advance," not
  "certifiably timeable." S1/S2 carry the discriminator, pending the Lubana absent
  side (M5).
- **INSTRUMENT FREEZE (post-shakeout):** as of the M4 scored run, the signature code
  (`probe.py`, `sampling.py`, `forecast.py`, `activations.py`) and signature params are
  frozen for the rest of Exp 1. **M5 (Lubana) is the honest out-of-sample test of these
  fixes:** the SAME instrument must read *absent* on Lubana-below and *present* on
  Lubana-above. If a fix were outcome-tuning, it would wrongly fire on Lubana-below and
  the experiment would FAIL — which is the adversarial check the design builds in via
  the percolation + control rows. A genuine bug found in M5 would be a reportable
  finding and would force re-running grokking too.

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

**M5 — Lubana (percolation ground truth + control; operationalization preregistered
BEFORE any Lubana training run)**
- Paper grounding fetched (ar5iv, 2026-07-04), not recalled: PCFG rules quoted from
  Appendix A.1.2; type-constraints graph G=(E,K,I); |E|=900/|K|=18000/|C|=10, p=0.1
  base; p_c ≈ 1/√(|E_c|·|K_c|). Appendix C hyperparameter tables are not
  machine-readable via ar5iv — model/optimizer values are nanoGPT-style recipe
  choices, recorded as recipe, not thresholds.
- **Threshold gate (design open item) satisfied computationally:** random bipartite
  graphs at three scales (incl. the paper's 900×18000) show the giant component
  appearing at the predicted p_c = 1/√(|E|·|K|), with the transition location
  tracking the formula across scales.
- **Scored capability = class-structure generalization** (the choice that makes
  "provably absent below threshold" true): masked-argmax over descriptive properties
  the subject entity was NEVER seen with; PASS iff same-class. Plain type-validity was
  rejected as the scored capability because isolated seen edges can be memorized below
  threshold; class inference requires linking entities through shared properties —
  chains that exist only above percolation. Chance = 1/|C|. gt-check = the graph's own
  giant-component fraction (computed from the data structure, independent of any model).
- **Below/above settings:** edge_prob = 0.5·p_c (fragmented) and 10·p_c (connected;
  the paper's base p=0.1 is ~40× its p_c).
- ~~Population simplifications vs the paper, recorded honestly: objects sampled
  same-class... These preserve the type-constraint structure the percolation argument
  needs.~~ **Superseded — the gate proved this wrong (second confirmation catch).**
  With online data the above row was perfect (transition @1278, held at 1.000), but
  the BELOW row learned the capability (metric 0.79 on a giant_frac=0.024 graph).
  Diagnosis: `_same_class_entity()` sampled objects and conjoined subjects same-class
  BY FIAT, making the entity co-occurrence graph complete within class at any edge
  density — the class signal bypassed percolation entirely. The percolation ground
  truth requires that class information travel ONLY through graph edges.
  **Fix (faithful to the paper's type checks):** all entity co-occurrence is now
  graph-mediated — objects are sampled from the verb property's POSSESSORS
  (subject-verb-object matching); conjoined subjects draw the sentence's property
  slots from the INTERSECTION of their property sets (context-sensitivity enforced);
  eAdj from the modified entity's own properties. New invariant test (the one that
  would have caught the bug): any two entities co-occurring in a sentence share a
  trainable-graph component, verified at both densities. Generation cost unchanged
  (~2 ms/batch). lVerb/Conj/Prep/dAdj remain small closed function-word sets.
- **Below-threshold rule preregistered:** argmax capability metric < 1.5×chance (the
  frozen §3 "<5%" is unusable at 10-way chance = 10%, as in Phase A). Set before any
  run; logged here.
- ~~Training is quasi-online: a 60k-sentence corpus with sampled minibatches
  approximates the paper's online sampling at our scale.~~ **Superseded — the
  confirmation gate caught this.** The first reduced-scale above-threshold
  confirmation showed a transient rise (0 → 0.58 @ step ~1.9k) followed by
  memorization collapse to BELOW chance (0.068 vs 0.1): the fixed 60k-sentence corpus
  covered essentially the whole reduced graph (~10.6k pairs seen) and each sentence
  repeated ~32×, so the model bound properties to specific co-occurring entities and
  suppressed same-class-unseen candidates. Fixes (recipe/mechanism, pre-scored-runs,
  no thresholds touched):
  1. **True online data** — `sample_batch` generates fresh sentences every iteration,
     the paper's actual recipe ("a fresh batch of strings every iteration").
  2. **Construction-level holdout** — `holdout_frac=0.1` of edges are reserved and
     never *syntactically bound* in generation; query candidates are never-trainable
     pairs by construction, so the mask is stable under online data (the empirical
     seen-set was a moving target). Invariant: reserved pairs are never BOUND
     (subject–descriptor / entity–adjective); incidental sentence co-occurrence is
     allowed and is precisely the class signal the capability learns from.
  3. **Confirmation gate tightened** — ABOVE must transition AND hold at the final
     checkpoint (a spike-then-collapse no longer passes).
- **Third gate catch — finite-cluster (island) residue, and the singleton-pool fix
  (preregistered before any scored run).** Confirmation v3 (graph-mediated
  population): above perfect (transition @1577, held 0.998); below no longer *forms*
  the capability (no growth after ~step 500 for 30k steps) but plateaus at 0.15–0.22,
  above the 0.15 bar. Diagnosis, verified quantitatively: percolation's own
  finite-size prediction. The below graph contains small multi-entity islands whose
  class-consistent co-occurrence is memorizable; the graph-computable "island oracle"
  ceiling is **0.211**, and the model sat at 0.186 — it learned its islands
  (37/300 entities) essentially perfectly and nothing more. The macroscopic
  capability did NOT form; our chance-based bar simply didn't model the memorizable
  residue. **Fix:** below-row evaluation (capability metric, S1 probe entities, S2
  queries, graph-axis sub-runs) restricts to **singleton-component entities**
  (247/300 here) — entities with zero class evidence in training, for whom the
  no-capability floor is exactly chance and the 1.5×chance bar stands unchanged. The
  capability tested becomes precisely cross-island generalization, the thing
  percolation forbids. Above row stays uniform: there class structure and component
  structure coincide (the giant component IS the capability), so no asymmetry.
  Thresholds untouched; the change is which entities constitute a fair test, computed
  model-free from the graph.
- **Scored-driver operationalizations (`run/run_lubana.py`; preregistered before any
  scored run):**
  - *S1 probe is entity-split by construction:* one prompt per entity, activations at
    the entity + last positions, label = entity class. A random example-split would
    let the probe memorize the entity→class lookup from its own training labels and
    read "present" on an untrained model; one-row-per-entity makes the frozen probe's
    example split an entity split, so above-chance validation requires the model to
    organize HELD-OUT entities by class.
  - *S2:* full-vocab temperature sampling; verifier = the class-generalization check;
    empirical floor from an untrained control (CP upper bound); "argmax fails" =
    masked-argmax metric < 1.5×chance (the preregistered below-threshold rule).
  - *S3 graph-axis (lubana_below):* dedicated sub-critical runs at
    (0.25, 0.45, 0.65, 0.85)×p_c, fixed 10k-step budget each, y = capability metric,
    forecast toward the true transition at p_c with the frozen log method. Per-seed
    (each seed = its own graph + models — honest replication, ~80 min extra per
    below-seed at paper scale). lubana_above uses the training-axis probe precursor,
    as grokking.
  - *S1/S2 checkpoint for lubana_below:* the LAST checkpoint (every checkpoint is
    below threshold; the final one is the strongest case — absent even after full
    training).
  - *Size bucket:* nearest order of magnitude of actual params (paper scale ≈ 12.9M →
    "10M"). Truth-table rows pair per bucket; grokking's matching buckets arrive in M6.
- **Reduced-scale confirmation gate PASSED (2026-07-04):** above transitions and
  holds (transition @1577, final 0.998); below flat at chance for 30k steps with the
  singleton pool (mean ~0.12, final 0.100, peak 0.150 — one +3.7σ sampling excursion
  on 500 queries, at the bar). Paper-scale sanity: below giant 0.007 with 735/900
  singletons; above giant 0.877. Paper-scale above confirmation launched (transition
  expected ~√6 later than reduced, ~4k steps).
- **Paper-scale above confirmation PASSED (2026-07-04):** transition @5574 (in line
  with the ~√6 shift prediction), final 0.998, held from step ~5574 through 30k
  (chance 0.10). *Provenance note:* a power failure killed the session after training
  finished; the stdout curve was lost but every checkpoint (with `eval_metric` in its
  payload) survived in `checkpoints/lubana_confirm_above/seed0/`, so the curve and
  gate verdict were reconstructed from checkpoint payloads — no re-run, no re-scoring.
  30k steps confirmed sufficient at paper scale; scored 2×5 campaign cleared to launch.
- **Scale decision (Michael, 2026-07-04): scored runs at `scale="paper"`**
  (|E|=900, |K|=18000 — the faithful base config; ~59 min/run, ~14 h for the
  10-run scored set). The reduced scale serves as the confirmation vehicle.
  Sequencing: reduced confirmation (above+below) → one paper-scale above
  confirmation (the paper's transition shifts ∝ √|K|, so the reduced-scale
  transition point does not carry over — verify 30k steps suffices before
  committing 14 h) → scored 2×5 runs.
- S3 uses the same frozen log-precursor method as grokking (instrument freeze holds);
  for lubana_below, S3 is attempted on the graph axis per design §3.
- **Scored campaign COMPLETE (2026-07-05, 16:26 Jul 4 → 21:52 Jul 5 wall time
  including one overnight idle):** 10/10 RunRecords in `results/lubana_{above,below}/10M/`,
  all gt-certified, unanimous across seeds:
  - **lubana_above ×5:** S1 PRESENT (probe acc 0.209–0.529 vs chance 0.100, p=0.008
    Bonferroni, at checkpoints ~1–2k steps before the ~5.6k-step transition);
    S2 ABSENT (sampling rate 1.3–1.9% vs empirical floors ~4.8% — the partially
    trained model concentrates mass away from correct rare properties, below even
    uniform guessing); S3 FAIL (predictions 7.6k–13.2k vs true 5574; overshoot
    35%–137%, replicating the grokking S3 finding on a second system).
  - **lubana_below ×5:** 0/3 — S1 at chance (acc 0.134–0.148, p=0.12–0.62);
    S2 absent (rates 0.4–1.7% vs floors ~4.8–5.0%); S3 graph-axis forecast
    uninformative on near-chance sub-critical data (two seeds predicted a negative
    edge probability). gt: giant_frac 0.006–0.007, capability peak 0.116–0.150
    (never over the 0.15 bar; the M4 watch-item excursion did not recur).
  - The below-row S1/S2 nulls double as the untrained/absent controls validating
    that the above-row S1 hits are not probe artifacts: same probe, same entity
    split, same sample sizes — fires only where structure exists in the data.
  - *Provenance:* run code identical across all 10 (no code commits after `22cdcae`);
    recorded git_shas walk through the doc-only commits `c8a3a1c`/`3a87242`, with
    `-dirty` flags caused solely by earlier untracked result JSONs sitting in the
    tree at record-save time. A second power outage occurred the evening of Jul 5
    — after ALL DONE; the detached `nohup` launch (see runner header) is what let
    the campaign finish unattended across the session teardown.
  - Interpretation lives with M7; the standing pattern matches every preregistered
    prediction: detectability below threshold (S1) tracked whether structure exists
    in the training distribution, not whether the model had the capability yet.

## Environment notes

- Runs on the Mac mini (M4 Pro, 48 GB, MPS); DGX Sparks untouched. See
  `../../environment.md`.
- sklearn ≥1.7 removed `LogisticRegression(multi_class=...)`; probe relies on the
  automatic multinomial behaviour (venv has scikit-learn 1.9.0).
- Run tests: `cd experiments/exp1 && python -m pytest`.
