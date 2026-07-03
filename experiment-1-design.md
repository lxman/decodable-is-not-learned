# Experiment 1 — Design Doc: Validate the Instrument (Synthetic Ground Truth)

**Status:** Preregistered design. Thresholds below are frozen once this file is committed; the analysis script is fixed alongside it and not edited after data collection.

**One-line purpose:** Show that the three-signature test can actually tell a resolution-class transition from a percolation-class one, on cases where the class is known by construction — turning the essay from "a framing with predictions" into "a framing with a validated instrument."

This experiment does **not** test the thesis. It calibrates the measuring instrument the thesis relies on. Every downstream experiment (2, 3, 4) reuses the three signature functions built and validated here, so if the instrument doesn't discriminate on ground truth, nothing downstream is trustworthy. That is why this runs first — not because it is cheapest, but because everything else is load-bearing on it.

---

## 1. Hypothesis and logical structure

**Core hypothesis (preregistered):**
> On a controlled training-progress axis, the three signatures — below-threshold probeability, exhaustive-sampling elicitability, and forecastability-from-below — are jointly **present** for a known amplification/resolution transition (modular-arithmetic grokking) and jointly **absent** for a known percolation transition (Lubana-style formal language below its threshold), with a separation margin exceeding the threshold committed in §4.

**The truth table a pass requires** (two systems, but the percolation system is run at two structural settings — see §2):

| System | Probe (S1) | Sampling (S2) | Forecast (S3) |
|---|---|---|---|
| Grokking (resolution) | present | present | present |
| Lubana-below (percolation ground truth) | absent | absent | absent |
| Lubana-above (control) | present | present | present |

**Why a fail is the valuable outcome.** If a signature fires on the percolation-below side (e.g., a probe reads out a capability that provably does not exist), or fails to fire on the resolution side (e.g., sampling cannot elicit the grokked capability pre-grok), the discriminator is leaky — and we have found it on synthetic data we control, before staking any published verdict on it. Any off-diagonal cell is a **reportable finding, not a result to tune away**. This is the asymmetry the essay already commits to: the fail is worth more than the pass.

**Scope boundary (YAGNI).** Experiment 1 does not attempt to validate the instrument on the *scale* axis with real models — that happens downstream in Experiments 2 and 4 on the Pythia suite. Exp 1's job is calibration on ground truth, nothing more.

---

## 2. The two ground-truth setups

### Threshold axis (locked decision)

The **training-progress axis** (compute/steps at fixed model size) is the primary axis along which the signature readouts are computed. Rationale:

1. **Cleanest known ground truth.** Grokking is natively a training-time transition; Lubana's percolation is analyzed as the network acquiring connected structure over training. Both are crisp on this axis. Forcing them onto a parameter-scale axis muddies whether the observed transition is even *the* percolation transition, eroding the "known by construction" guarantee that is the entire point of the experiment.
2. **Confound control.** On the training-progress axis, the model is held fixed and only the checkpoint advances — one variable moves. On the scale axis, comparing a 1M and a 100M model changes capacity, optimization dynamics, and effective data exposure at once; a signature difference cannot be cleanly attributed.
3. **Extra thesis work.** The deep thesis holds that *fidelity*, not parameter count, is the operative variable, and training time is one fidelity input (Prediction 5). The essay explains grokking as resolution-over-training. If the three-signature test cleanly separates grokking from Lubana over training, that is direct, independent support for the essay's grokking claim, which currently rests on Nanda's mechanistic story alone.

The **1M–100M size sweep** rides along as a **secondary robustness layer**: the present/absent pattern must survive across model sizes. The scale-axis validation of the instrument on *real* models happens downstream in Experiments 2 and 4.

### Resolution exemplar — modular-arithmetic grokking (Nanda et al. 2023)

Small decoder transformer on `(a·b) mod p`, `p = 113`, trained on a fixed fraction of the pair space; generalization groks in over training. Capability *forms* over the training axis.

**Independent ground-truth check** (so class membership does not depend on the signatures we are validating): held-out accuracy plus a Nanda-style progress measure (restricted / excluded loss) showing the structured circuit sharpening while memorization recedes. This certifies the case as "resolution" by construction.

### Percolation exemplar — Lubana-style formal language (arXiv:2408.12578)

A percolation transition is defined by a **graph / data-structure control parameter**, not by training time: below the critical connectivity the capability provably *never* forms, at any training duration. The percolation system is therefore run at two settings:

- **Below threshold** (sparse graph): capability provably absent. This is the **known-percolation ground truth**; signatures should read absent throughout training, forever.
- **Above threshold** (connected graph): capability forms over training. This is the **control**, and a valuable one — it should show the resolution signatures *over training*, proving the signatures track **structure-presence**, not "formal-language-vs-arithmetic." If the discriminator only fired on task identity, this cell would expose it.

**Independent ground-truth check:** the observed transition matches Lubana's percolation threshold *predicted from the bipartite graph*, and shifts as their theory predicts when data structure is altered. That theoretical prediction is what makes membership known by construction.

### Staged build (locked decision)

- **Phase A — own simple task (pipeline debug).** A minimal compositional-binding task with a percolation threshold we can compute in closed form. Cheap; single size, single seed. Its only job is to shake out the three signature functions end-to-end before the expensive runs.
- **Phase B — faithful Lubana replication.** The credibility-grade result. A reviewer sees a known result reproduced, then the signatures run against it.

---

## 3. Signature operationalization

Each signature is a decidable readout with a preregistered present/absent rule. S1 and S2 are measured over the training-progress axis; S3 has an axis wrinkle, noted below.

### S1 — Probeability below threshold

Train a linear probe (logistic regression) on **frozen** residual-stream activations to predict the task-relevant target — for modular arithmetic, the answer class, with the Nanda Fourier features as a secondary readout. Layer and token position selected on a validation split; chance baseline explicit (1/113 for mod-p); multiple-comparison correction across layers.

- **"Below threshold"** = checkpoints where argmax test accuracy < 5%.
- **Present** = probe accuracy beats a label-permutation null at **p < 0.01, Bonferroni-corrected across layers**, at a below-threshold checkpoint.
- **Absent** = fails that bar at every below-threshold checkpoint and layer.
- Predictions: grokking → present; Lubana-below → absent; Lubana-above → present.

### S2 — Elicitability by exhaustive sampling

At pre-threshold checkpoints, draw N samples per query at temperature; estimate the PassUntil rate (pass@k). Sampling budget up to **10⁵** samples per query.

- **Present** = Clopper–Pearson 95% **lower** bound on the pass rate exceeds the empirical guessing floor (estimated from an untrained control model), while argmax fails.
- **Absent** = Clopper–Pearson 95% **upper** bound ≤ guessing floor. The upper bound is reported as a number — **never "zero."**
- Predictions: grokking → present; Lubana-below → absent (bounded, not zeroed); Lubana-above → present.

### S3 — Forecastability from below

Grokking is famously *sudden on the argmax curve*, so naive extrapolation of the surface metric fails even for the resolution exemplar. That is the essay's whole point: you must forecast the **right** quantity. Forecastability is therefore defined on a **smooth precursor** (the S1 probe trajectory, or the log S2 rate), fit on pre-transition points only and extrapolated to predict the transition location.

- **Present** = the 90% forecast interval contains the true transition **and** predicted location is within 25% of true **and** the forecast beats a no-transition baseline.
- **Absent** = precursor slope CI includes zero (nothing to extrapolate), or the interval misses the transition.
- **Axis wrinkle:** forecastability is intrinsically defined relative to the transition, so it is measured along whichever axis the transition lives on — training-time for grokking, the **graph-structure control parameter** for Lubana. This is the one signature where the percolation case uses the structural axis rather than training-time, and it is unavoidable: the essay's sharpest claim is precisely that percolation transitions are not forecastable from below the graph threshold. For Lubana-below the forecast is attempted from below the graph threshold; the essay predicts it fails, and that failure is the "absent."
- Predictions: grokking → present; Lubana-below → absent; Lubana-above → present.

---

## 4. Preregistered pass/fail thresholds and statistics

**These numbers are frozen once this file is committed. The analysis script is fixed alongside it and not edited after data collection.**

### Per-signature decision rules

Restated from §3 for the record:

- **S1 (Probe):** present iff probe accuracy beats a label-permutation null at p < 0.01 (Bonferroni across layers) at a checkpoint with argmax test accuracy < 5%.
- **S2 (Sampling):** present iff Clopper–Pearson 95% lower bound on the pass rate exceeds the empirical guessing floor; absent iff the 95% upper bound ≤ guessing floor, reported as a numeric bound.
- **S3 (Forecast):** present iff the 90% forecast interval contains the true transition, predicted location within 25% of true, beating a no-transition baseline.

### Overall PASS (the preregistered bar)

All three of the following hold:

1. **S1 and S2 (continuous statistics — probe accuracy, pass rate):** the 95% CIs for the **grokking (resolution)** row and the **Lubana-below (percolation)** row are **disjoint, in the predicted direction, with a gap corresponding to Cohen's d ≥ 2**. (S1 and S2 share a continuous scale across the two systems, so a magnitude-of-separation bar applies.)
2. **S3 (categorical — the forecast succeeds or does not):** grokking reads **present** by the §3 rule (smooth precursor forecasts the transition within tolerance) and Lubana-below reads **absent** (no precursor / forecast fails to anticipate the transition). S3 is scored categorically rather than by Cohen's d, because for Lubana-below it is measured on the graph-structure axis rather than the training axis, so the two rows do not share a continuous scale to pool.
3. The **Lubana-above control** row matches the resolution row (all three present).

All of the above **replicated across ≥ 5 seeds per configuration** and **holding across ≥ 3 model sizes** spanning 1M–100M (the secondary size sweep).

### Reportable FAIL (worth more than a pass)

Any of the following is written up as a finding, not tuned away:

- Any off-diagonal cell — a signature present on Lubana-below, or absent on grokking (this covers S3's categorical failure).
- Overlapping CIs or Cohen's d < 2 on S1 or S2 (a leaky, non-discriminating instrument on the continuous signatures).
- The control row (Lubana-above) diverging from the resolution row — which would mean the signatures track task identity, not structure-presence.

### Judgment-call dials (set deliberately, now frozen)

- **Cohen's d ≥ 2** for "clean separation": a strong bar (distributions barely overlap). Chosen strict because the essay's brand rewards a strict-but-passed test.
- **10⁵ sampling budget:** sets the smallest pass rate distinguishable from zero (~3×10⁻⁵ at this budget), which sets how meaningful the "absent" verdict on the percolation side is.

### Statistics hygiene (locked)

- All thresholds frozen pre-run.
- One analysis script committed alongside this doc; not edited after data collection.
- Seeds fixed and logged.
- Every "zero-looking" rate reported as a Clopper–Pearson bound, never as a claimed zero.

---

## 5. Models, configs, and run plan

### Models (all tiny, all Mac-resident; DGX Sparks untouched)

- **Grokking:** Nanda-style decoder transformer on `(a·b) mod 113`. Base config ≈ 1 layer, d_model 128, 4 heads (< 1M params). Size sweep scales depth/width to ≈ **1M, 10M, 100M** for the secondary robustness layer.
- **Lubana (Phase B):** faithful replication of arXiv:2408.12578 — the context-sensitive formal language and small transformer — run at two graph settings (below / above the percolation threshold), same three sizes.
- **Phase A (pipeline debug):** minimal compositional-binding task with a closed-form percolation threshold; single size, single seed.

### Compute reality check

Grokking wants long training (10⁵–10⁶ steps) but the models are tiny — hours per run on MPS. Full matrix ≈ 15 grokking runs + ≈ 30 Lubana runs (2 settings × 3 sizes × 5 seeds) + the 10⁵ sampling campaigns at selected checkpoints. Days-to-weeks of **background** wall-clock on the idle Mac (M4 Pro, 48 GB, MPS validated for fp16 Pythia forward passes). Nothing blocks the machine; nothing needs the Sparks.

### Run order (each gates the next)

1. **Phase A** — build and debug all three signature functions end-to-end on the cheap task.
2. **Grokking full** — the resolution row; 5 seeds, base size first.
3. **Lubana below + above** — the percolation ground-truth row plus the control row.
4. **Secondary size sweep** — repeat the pattern at 1M / 10M / 100M.
5. **Analysis** — run the frozen, pre-committed script; fill the truth table; report.

### Reusability (the payoff)

The three signature functions are written as a standalone module with clean interfaces from day one, because Experiments 2, 3, and 4 import the same probe, sampling, and forecast code. Exp 1 is where that library gets built and validated.

### Code location (locked decision)

Code lives **in this repo** under `experiments/exp1/`, developed and run on the Mac by cloning the repo there, so the preregistered analysis script, configs, seeds, and results sit in git next to this design doc. The whole run is reproducible from one repo.

### Hardware

- **Workhorse:** Mac mini, Apple M4 Pro, 14 cores (10P/4E), 48 GB unified, macOS 26.5.1. PyTorch 2.12.1 + Transformers 5.13.0 in `~/emergence-lab/.venv` (Python 3.11). MPS available; fp16 forward passes on GPTNeoX validated (no NaNs, correct output).
- **Untouched:** both DGX Sparks stay on their serving load. Exp 1 never uses them.

---

## Open items before first run

- Write `experiments/exp1/` scaffolding and the three signature-function interfaces (subject to a separate implementation plan).
- Reproduce the Lubana percolation threshold prediction from their paper and confirm it before running signatures against it.
- Confirm the Nanda grokking config groks reliably at the base size on the Mac before scaling.
- Commit the frozen analysis script alongside this doc before collecting any data.
