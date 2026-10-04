# Matched tokens: a late size advantage, not a monotonic ladder

**Completed 2026-10-04.** Descriptive reuse of six Pythia sizes at ten exactly
shared training checkpoints, on all 34 older-battery rungs (17,000 items).
Rules were committed before comparisons; one production run, 10,000 shared
family-bootstrap draws. All stored correctness bits were rederived, and the
saved-output audit passed. Full tables: [results/REPORT.md](results/REPORT.md).

## Main reading

At the fixed final checkpoint—**299.893 billion training tokens**—12B exceeds
410M by **4.159 percentage points**, with a family-resampling 95% interval
of **[1.56, 8.23]**. Equal weighting of the 16 task families gives a similar
**4.338-point** difference, interval **[1.56, 8.32]**.

But the size ordering is not monotonic. **2.8B has the highest final mean
accuracy**, exceeding both 6.9B and 12B in this recorded read:

| Size | Final accuracy | Rungs clearing the existing reference bar |
|---|---:|---:|
| 410M | 6.44% | 1/34 |
| 1B | 6.77% | 1/34 |
| 1.4B | 6.05% | 2/34 |
| 2.8B | 11.38% | 7/34 |
| 6.9B | 9.65% | 9/34 |
| 12B | 10.59% | 9/34 |

Mean accuracy and the breadth of reference-bar crossings are different
readings: 2.8B wins the former, while 6.9B and 12B clear more rungs. These
reuse the original per-rung bar; they are not new multiplicity-controlled
capability tests.

## The advantage depends on training stage and task type

The 12B-minus-410M difference is small and changes sign early. Its printed
family-resampling interval includes zero at every shared checkpoint through
32k. The differences reach **+3.365 points at 100k** and **+4.159 at 143k**.
These are descriptions of the fixed checkpoint table, not significance calls.

The equal-checkpoint average over all ten points is **+0.835 points**,
interval **[0.271, 1.663]**. Removing the two search-added points, 5k/6k,
gives **+1.078**, interval **[0.387, 2.117]**. Neither average is a time
integral or ten independent replications.

At the final checkpoint, the widest contrast is **+17.050 points on the
four option rungs**, **+2.928 on the 25 arithmetic rungs**, and **0.000 on
the five string rungs**. The last is an observed aggregate difference,
not evidence that string capability probability is zero. The complete
per-rung counts and contrasts remain available, including all 15 size pairs.

## Correctness is not a nested set across sizes

For 410M → 12B at the final checkpoint:

- **1,319 gains:** 410M wrong, 12B right.
- **612 losses:** 410M right, 12B wrong.
- Net **707** more correct answers out of 17,000, giving the 4.159-point gain.

Across all six sizes, **3,695 of the 4,564 items correct at any size (80.96%)**
have at least one adjacent right→wrong transition. Only **8/34 rungs** have
nondecreasing correct counts throughout the six-size ladder. The other
items' all-wrong patterns must not be mistaken for positive nesting evidence.

These are single fp16 greedy reads. They do not measure irreversible loss,
establish that a larger model cannot produce an answer by sampling, or remove
the possibility of near-tie/kernel variation. “Recorded greedy successes do
not form a strictly growing set” is the supported statement.

## What follows

Matched token exposure preserves a late, aggregate size advantage on this
battery. It does **not** restore a universal size ordering or a strict
containment relation among correct items. Holding tokens fixed also does
not isolate parameters from architecture, learning rates, recipe or compute.

The intervals measure sensitivity to resampling these represented task
families. They are not training-seed uncertainty or generalization guarantees
over tasks/models. No confirmatory verdict was sought or generated.

This does not test whether sampled counts forecast **size-axis** item order,
and does not choose between resolution and construction. The separate
[Experiment 7 design](../../experiment-7-design.md) asks what task-sensitive
information the sampled forecast contains. Its reviewed rules were written
before these comparisons; no rule was changed in response to this result.

## Execution and evidence

Launch commit: `b770e8ebd83f94db0be6748046e37224bdde82ec`.
Analysis: **16:36:35–16:36:39 UTC**, Oct 4, exit 0; saved-output audit exit 0.
Coverage: 2,040 count rows, 150 contrasts, 5,100 paired-transition rows,
340 texture rows, 60 accuracy rows and 30 time-average contrasts.
The audit checked their identities, aggregates and displayed numbers without
rerunning the bootstrap. Independent post-run verification rechecked 2,309
source files, four launch bindings and eight output checksums.

Summary SHA256:
`1f385bb8ad606ebd9139555ba0cc8d523b0bd3b5590514e38a3dd6db4ee0ec17`.
Logs, invocation count and verification receipt: [operations/](operations/).
The durable monitor is acknowledged. **Do not rerun the analysis/bootstrap.**
