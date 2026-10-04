# Matched-token Pythia size analysis

## Authorization and status

Michael requested "Do the analysis and plan the experiment" on 2026-10-04,
then explicitly chose **Descriptive analysis**: all six sizes, all ten exact
shared checkpoints and all 34 rungs, under committed-before-run rules.
This is a descriptive reuse analysis, with no PASS/FAIL verdict. It replaces
the earlier proposal to take this question through a separate confirmatory
preregistration. The sampling-mechanism successor is a separate design.

This plan is committed and pushed before any size comparison is computed.
The analyzer will run once after synthetic-fixture verification and review.
All inputs are previously collected and known in principle. Nothing here
is a sealed forecast. No model contact, rental or essay propagation is part
of this authorization.

## Question

At the same number of training tokens, how does greedy performance change
across Pythia sizes? Does a larger model's set of correct items contain the
smaller model's, or do gains coexist with losses? Separate the empirical
size association from a causal claim about parameters alone.

## Inputs and inventory disclosure

Use only Experiment 5's on-host records, under
`experiments/exp5/results/units/`, from repository commit `6deb2d55f`.
Use the measured parameter counts in each `_checkpoint.json`, not rounded
model names, when computing log-size slopes. All records must agree on each
size's parameter count and the original host/stack. The six sizes, ordered:

`410m, 1b, 1.4b, 2.8b, 6.9b, 12b`.

The complete intersection of recorded steps is:

`1000, 2000, 4000, 5000, 6000, 8000, 16000, 32000, 100000, 143000`.

Training tokens = step × **2,097,152**, the existing Pythia convention.
There is no interpolation or nearest-checkpoint matching. 2.8B's excluded
64k weight alias is not a matched point; its 65k substitute is not mixed
with the other sizes' 64k records. 160M has only 142k/final units and is
excluded by the six-size scope. No seventh-size endpoint is added later.

**Pre-analysis reads, disclosed:** directory inventories and JSON field
names; each shared unit's `finite` flag (all true); one checkpoint record's
metadata; predecessor source/design/retrospective records. Ten, rather than
the earlier nine, shared points were found. No count, size slope, paired
accuracy difference or nesting statistic was computed during inventory.
The shared 5k/6k units were collected by the earlier loss-matching search,
so the time grid is partly selected by that earlier procedure.

Use all **34 rungs × 500 items**, without outcome-based liveness selection.
Rung ordering, 16-family map, three-type map, item files, verification
criterion, floors and per-rung binomial clear rule are the frozen Exp 2d/5
definitions. This reads the older synthetic battery, not Exp 6's battery.

## Validation and provenance

Before summarizing, verify every selected record and every imported repository
source file against the pinned source commit. Bind the new analysis's own
source and this plan to its launch commit. Record file SHA-256s and the
source/launch commits in the output. Check bindings again at exit.

Use Exp 5's frozen unit, checkpoint, loss, host and rung contract functions.
Re-derive every stored correctness bit from the stored continuation and
the pinned item/verify criterion; compare bits, counts and coverage. Require
each selected unit to be finite by the measured loss rule, not its flag
alone. Verify unit payload hashes, item hashes, checkpoint identity and
constant per-size parameter counts. No predecessor analyzer `run()` or CLI
is invoked. Any missing, corrupt or inconsistent input stops the analysis
with an explicit refusal; do not omit a cell to make the analysis finish.

## Fixed descriptive outputs

1. **Complete count table:** every checkpoint × size × rung, correct count,
   accuracy, floor and reference-clear status; 2,040 rows. Also print each
   checkpoint's six-size mean-accuracy and number-of-clearing-rungs table.
2. **Matched-size contrasts:** all 15 ordered size pairs at every checkpoint.
   Mean accuracy difference in percentage points, equal weight to each
   rung. The main displayed contrast is 12B minus 410M; display all five
   adjacent-size contrasts too. Report the equal-family-weighted contrast
   and each of the three rung-type contrasts beside the all-rung reading.
   Checkpoint 143k is the fixed final comparison, not a chosen peak.
3. **Gains and losses:** for every size pair × checkpoint × rung, count the
   paired item outcomes 00, 01, 10, 11. Gains are 01, losses 10. Verify
   gains minus losses equals the correct-count difference. Print gross
   gains/losses for the widest and adjacent pairs. Clear-status gains and
   losses use the existing per-rung rule; they are descriptions, not a new
   multiplicity-controlled capability test.
4. **Size-order texture:** per rung/checkpoint, OLS accuracy slope against
   log2(measured parameters), Spearman rank association with size (null for
   constant counts), number of adjacent count decreases, and whether counts
   are nondecreasing. At item grain, count any 1→0 transition along the six
   sizes, both out of 500 and out of the ever-correct items. An all-wrong
   item is vacuously nested; the ever-correct denominator prevents that
   observation from being hidden by trivial items.
5. **Grid and weighting disclosures:** retain all per-checkpoint tables as
   the main view. Any across-time average weights the ten checkpoints
   equally and is labelled as such, not as a time integral or ten independent
   replications. Print the eight-point shared-spine sensitivity excluding
   the search-added 5k/6k points. Print type counts and family weights so
   arithmetic's 25/34 representation is visible.

No statistics are chosen after the observed comparisons. Additional readings
would require a separately dated, explicitly post-analysis addition.

## Uncertainty

For macro mean paired accuracy contrasts, use **10,000 family-cluster
bootstrap draws**, seed **20261004**, sampling the 16 families with
replacement and retaining every rung, item, size and checkpoint in each
selected family. The same draws apply to every contrast. For the equal-rung
estimand, each replicate divides its repeated rung sum by its repeated
rung count; for the equal-family estimand, it averages the selected family
means. Report percentile 95% intervals in percentage points. Within a type,
point estimates suffice; no interval is manufactured from a one-family
type or treated as independent evidence.

These intervals describe sensitivity to resampling the represented task
families. The families were not sampled randomly from all possible tasks.
They do not quantify training-seed uncertainty, model-population uncertainty,
checkpoint measurement noise, or extrapolation beyond this battery. Individual
items/checkpoints are not treated as independent experiment replicates.
No p-values, effect-threshold worlds or absence verdicts are computed.

## Limits and interpretation fixed in advance

Positive size association permits "larger Pythia models tend to score higher
at matched token exposure on these tasks," at the printed resolution. It
does not isolate parameter count from the training recipe, architecture or
size-specific learning rates. The same token count fixes schedule position,
not learning rate or FLOPs. Equal tokens are not equal loss.

Nonnested correctness permits "the recorded greedy successes are not a
strictly growing set across size." It does not establish irreversible
capability loss: these are single fp16 greedy reads without repeated-read
noise correction. Constant/zero counts are reported as observations with
finite resolution, never as proof that capability probability is zero.

This analysis does not test whether the old sampled predictor forecasts
size-axis ordering. That would require a separately specified predictor,
eligible outcome and dependence-aware comparison. It does not identify a
learning mechanism or establish capability birth versus resolution.

## Deliverables and checks

`analyze.py`, synthetic-fixture tests, `results/summary.json`, complete
count/contrast/transition/texture CSV tables, `results/REPORT.md`, and a
provenance manifest. A separate saved-output checker verifies row coverage,
paired-count identities, aggregates and displayed numbers without rerunning
the analysis or bootstrap. Test known gains/losses, decreasing/nested and
constant cases, family-bootstrap weighting, record tamper refusal and
write-once behavior. Production results are never generated by tests.

## Ruled dials

Michael chose the descriptive scope on Oct 4: fixed-before-run rules; six
sizes; all ten exact common checkpoints; all 34 rungs; size effects, gains,
reversals and uncertainty; no confirmatory PASS/FAIL claim. Implementation
choices above are ledgered before execution. Formal experiment ratification
and rental gates apply to the separate mechanism successor, whose design
will be presented for ruling.
