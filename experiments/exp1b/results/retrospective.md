# Experiment 1b — Closeout Retrospective (2026-08-14)

**VERDICT: PASS** — grokking 9/10, lubana_above 10/10, lubana_below 0/10,
untrained 9/30 diagnostic. The first PASS this program has produced. See
`VERDICT.txt` for the formal record.

## The arc

Exp 1 returned FAIL. The FAIL was not a negative result: its S1 criterion
compared raw probe accuracy across a 113-class system and a 10-class system,
and the predicted direction was unreachable for any instrument whatsoever. That
was identified in July, after the data, and rule 6 meant no amendment — the
FAIL was allowed to stand and the discriminator claim was left **untested
rather than refuted**.

1b exists to run that test properly: same task implementations, same training
recipes, same signature module, fresh seeds, and a criterion an instrument can
actually satisfy. It is a re-test, not a rebuild.

It nearly failed for a reason nobody designed for, and the thing that saved it
was a control that cost almost nothing.

## What almost killed it, before a single trained cell ran

The design added an untrained twin per trained cell — a randomly initialized
network, same architecture, same seed, same probe, no training. This was cheap
insurance against reservoir decodability, the failure mode that terminated Exp 2
at 120 of 120 fits.

Built during Task 3 and smoke-tested on six cells before commit, **both
grokking twins fired S1** at the permutation floor. Extended to all thirty
cells: **grokking 9/10, lubana 0/20**. Untrained networks, no training
whatsoever, and the uncorrected criterion said "structure present" nine times
out of ten.

The mechanism is exact. The label-permutation null permutes labels and refits,
so it controls for probe capacity and for label marginals — but not for
information the random expansion already carries about the label. It answers
*does the probe use the labels?*, not *did training put the structure there?*
For `(a·b) mod 113` the answer decomposes into characters over ℤ₁₁₃*, and the
GELU of a mixture of `emb(a)` and `emb(b)` generates exactly the quadratic
cross-terms that carry bilinear structure. The floor is above chance for a
computable reason.

Structurally this is Exp 2c's chance-floor defect one level down. 2c's outcome
side credited format-only competence as capability because empirical untrained
floors were ~0. 1b's *predictor* side credited reservoir readout as structure
because the criterion's floor was theoretical chance (1/113 = .0088) where the
empirical floor is ~.023 — **2.6× higher**.

Had 1b run as originally frozen, it would have returned FAIL on an untrained
0/30 bar, and the FAIL would have been uninterpretable in precisely the way 2c's
was. Instead the control fired first, and the one pre-committed change was spent
on a floor-corrected S1 with a reason ledgered before the change.

## The correction earned its keep, in the final number

S1-present now additionally requires `accuracy >` the cell's **own** untrained
twin, paired per (system, size, seed), strict inequality.

It demoted exactly one cell: `grokking/10M/seed104`, trained accuracy .017333
against a twin of .017333 — equal to the last digit. Raw S1 fired; the strict
inequality refused it. Grokking's raw 10/10 became the true 9/10.

Without the correction this closeout would report a clean sweep. The clean sweep
would have been wrong, and nothing else in the instrument would have said so.

## What the twins showed that the docstrings only claimed

Same instrument, same seeds, minutes apart in the same block:

| untrained row | fires |
|---|---|
| grokking (1M + 10M) | **9/10** |
| lubana_above | 0/10 |
| lubana_below | 0/10 |

The difference is the example split. Grokking's probe uses held-out test pairs;
lubana's uses an **entity** split, chosen so memorizing the entity→class lookup
cannot produce above-chance validation accuracy. `run_lubana.py`'s docstring
asserted that. Twenty untrained cells now measure it.

**Whether an untrained network passes your probe criterion is a property of how
you split the data, not of the model.** Without the untrained control you cannot
tell which kind of probe you built. That is the transferable result, and it is
the methods paper's thesis reaching the predictor side of this program's own
Experiment 1: three of the four cells Exp 1 scored S1-present at 10M sit at or
below the untrained floor measured here.

## The projection missed, and the reason is the better finding

The verdict projection — ledgered in `PROGRESS.md`, quoted in the
`exp1b-preregistered` tag, written before any trained cell ran — predicted the
grokking row at ~6/10 and an overall FAIL. Actual: 9/10 and PASS.

Grokking's 10M S1 accuracy is **bimodal**. Across ten cells (Exp 1's five seeds
and 1b's five) the values form two clusters — reservoir-level .0140–.0227 and
structure .0927–.3033 — separated by **4.1× with nothing in between**. Exp 1
drew 1 of 5 in the structure mode; 1b drew 4 of 5. **Fisher exact two-sided
p = 0.2063**: statistically indistinguishable, the same distribution sampled
twice.

The projection took Exp 1's *median* as the expectation for a bimodal variable
whose mode split is near a coin flip — it treated a 1-in-5 draw as typical. A
median is the wrong summary of a bimodal outcome, and five seeds cannot
establish which mode is typical.

One mechanism was tested and rejected rather than assumed: that S1 tracks which
checkpoint counts as "latest below 5% argmax", so early-grokking seeds get
probed on barely-trained models. Correlation with S1 accuracy is **−0.432** —
weak, wrong sign, checkpoint ranges overlapping between clusters. What separates
the modes is **not identified**. n = 10; the gap is clean but bimodality on ten
points is suggestive, not established.

## What worked, and should be inherited

- **The untrained twin, per cell, run before the trained matrix.** Cost ~1h46m
  against a 44-hour campaign, and it was the difference between an
  interpretable PASS and an uninterpretable FAIL. No probe experiment in this
  program should run without it again.
- **Commit-per-cell.** Each finished record dirties the tree for the next cell's
  `git_sha`. Exp 1 stamped 25 of 45 records `-dirty`; 1b committed as cells
  landed and stamped clean throughout.
- **Checkpoint mtimes, not the log, as the liveness signal.** The campaign log
  writes only START/DONE, so a hang and a long cell are indistinguishable in it.
- **Mutation-testing the gates.** The floor correction and the campaign dispatch
  were each mutated deliberately (10 mutations, all caught). Argument-order bugs
  in a dispatcher are silent — `run_grokking(size, seed)` is a wrong run, not a
  `TypeError`.
- **Disclosing thin margins before the data.** `lubana_below`'s gate was flagged
  at 84% of bar on the single gate seed. Across ten cells it ran 84/76/95/88/89/
  88/91/97/91/81 — mean 86%, worst .146 against .150. Every cell cleared, none
  by much. Because it was disclosed pre-freeze, the closeout states a property
  of the bar rather than defending a near-miss.

## What to change in any successor

- **`analyze_1b.py` was frozen with `verdict()` and no record loader.** Nothing
  in the frozen tree could read the campaign off disk. Neither the plan nor the
  freeze review caught it, and it surfaced only when the analysis was run.
  Freeze the loader with the analysis, or the freeze is incomplete.
- **Don't project from a median without checking the distribution's shape.**
  Plot the prior experiment's cells before forecasting from them. Ten minutes
  would have caught the bimodality and produced a projection with an honest
  interval instead of a point estimate on the wrong mode.
- **A pooled bar hides per-cell unreliability.** 1b passes 9/10, and one cell in
  ten read exactly what a random network reads. That is fine for an aggregate
  claim and useless for a single-system verdict, which is the actual use case
  the essay wants. A successor should report the per-cell failure rate as a
  headline number, not a caveat.
- **`run_lubana` does not resume mid-cell.** An MPS fault costs the whole cell —
  up to 2h18m at 1M. Checkpoint-resume would have made the one attrition free.
- **Restore the 100M tier if affordable.** It was dropped for cost, and it is
  where Exp 1's discriminator was most stressed. 1b makes no scale-robustness
  claim.

## The results worth keeping

1. **The discriminator's S1 leg works on synthetic ground truth with the
   reservoir confound controlled.** It fires where structure is latent but
   unexpressed and stays silent where percolation forbids the structure from
   existing. This is the test Exp 1 never performed.
2. **Nine of ten untrained grokking twins fire the uncorrected criterion, and
   zero of twenty entity-split twins do.** This is measured, novel, and true
   regardless of the verdict. It is the stronger half of what 1b produced.
3. **Bimodality in grokking's below-threshold probe accuracy**, with a clean 4.1×
   gap and no identified mechanism. Suggestive at n=10 and worth a properly
   powered successor.

The pattern across this program holds: 2 → 2b → 2c → 1b, and the methods
findings outlive the thesis tests. 1b is the first to deliver both, and the
methods half is still the more durable.

## What the PASS does not license

Stated here as well as in `VERDICT.txt`, because a PASS is easier to overread
than a FAIL. Nothing about real models — 2c tested that and returned an
uninterpretable FAIL. Only S1; S2 and S3 are descriptive. Nothing beyond 10M.
Detection, never magnitude. And aggregate, not per-cell.

The essay's predictive claim died with 2c and is not revived by this. What 1b
provides is an instrument behind the carve-out between resolution-type and
percolation-type capabilities — the carve-out stops being an assertion. That is
a smaller thing than a vindicated thesis, and it is real.

## Cost accounting, honestly

| | |
|---|---|
| instrument build (Tasks 1–6) | one day, 2026-08-12 |
| ground-truth gates (Task 5) | 3 cells, 4.1 h |
| untrained twins, pre-freeze | 30 cells, ~1.8 h |
| campaign | 57 cells, **44.0 h** compute over 45.8 h wall-clock |
| attrition | 1 cell (~1.8 h lost) |
| disk | 80 GB checkpoints, 260 KB records |
| commits | 66 |

Wall-clock 2026-08-12 18:08 → 2026-08-14 15:58. The 98% compute-to-wall ratio
reflects a machine doing nothing else; the one interruption was a GPU OOM caused
by another process compiling Metal graphs, which cost 105 minutes and was fixed
by retiring the competing service.

The durable artifact is 260 KB of records. Everything else regenerates —
early checkpoints exactly, late ones not.
