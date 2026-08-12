# Experiment 2c — Closeout Retrospective (2026-08-12)

**VERDICT: FAIL** — rho .368, block p .131, CI (-.185, .762). The
hypothesis is not falsified; it is untested at the resolution this
battery could deliver. See `VERDICT.txt` for the formal record.

## The arc

2b closed INSUFFICIENT_DATA because the untrained control caught surface-
statistics leaks in 13 of 25 capabilities, emptying the battery before
Stage 1. 2c was built to fix exactly that: a screened battery with a
tiered untrained gate at inclusion, difficulty families with dials,
family-honest statistics, and 12 leak-free survivors carried from 2b as
seed stock. The screen worked. Gate 1 came back clean — 338 not_fire out
of 340 — and for the first time in the program a Stage 1 predictor was
assembled, committed, tagged, and tested against an eval side.

So 2c got further than any prior experiment in this line, and then failed
on a different axis than the one it was designed to defend.

## What killed it: the battery went quiet, not dirty

2b died of contamination. 2c died of silence. Of 34 scored rungs, 22
returned exactly zero probe margin, and **9 of 16 family blocks were
entirely flat**. Because the primary test permutes families as blocks, an
all-flat family is inert — it contributes identical values under every
permutation. The frozen power table assumed 16 permutable blocks; the
realized test had 7.

This was measured before the eval side ran, not discovered afterwards.
Conditional power at rho_true = .6 came in at **.5604** against the frozen
table's .7690, with the tie-corrected ceiling at .8541 and alpha
unaffected (pooled .01050). Both the Stage 1 tag and the verdict
projection state, in advance, that a FAIL at rho <= .6 would be
uninterpretable. The realized CI, spanning -.185 to .762, is that
prediction coming true rather than an excuse constructed afterwards.

## The defect we did not anticipate

The outcome operationalization was contaminated in a way none of the
design reviews caught. Design §3 normalizes against **empirical untrained
floors** — and those floors are ~0 for every rung, because an untrained
model emits malformed text rather than plausible wrong answers. A trained
model that has learned only the output format scores at 1/|answer space|
and is credited that as capability. Ten rungs sat at their guessing rate.
`odd_one_out` scored below its own chance rate and ranked fifth.

The lesson generalizes and belongs in the methods paper: **above the
untrained floor is not the same as capable.** It is the same error as
"decodable is not learned," one level up, and this program committed it in
its own outcome variable after writing a paper about the probe-side
version. An untrained-weights control answers "is this signal in the
weights?" It does not answer "is this behaviour competent?" Those need
different floors — a chance floor within the answer space, not a
malformed-output floor.

Correcting it as a disclosed descriptive moved rho **down**, .368 -> .200.
The contamination was manufacturing signal, not hiding it.

## What worked, and should be inherited

- **The screen.** Gate 1 clean on 340 fits. 2b's failure mode did not
  recur. Basis-starving plus a tiered inclusion gate closes the
  surface-statistics class.
- **The two-stage lock, machine-enforced.** The M4 runner refuses to query
  an eval-side model without the `exp2c-stage1` tag, mutation-tested both
  ways. The predictor, the outcome rule, and the projection were each
  committed before the data that would judge them existed. That ordering
  is now checkable by anyone from the git history alone, not taken on
  trust.
- **Freezing the outcome rule mid-campaign.** `m5_ascent` was written and
  frozen with 68 of 204 cells on disk and none read. Had it been written
  afterwards, the chance-floor defect would have been discovered while
  choosing the rule — and no reader could distinguish a principled fix
  from a fitted one.
- **Writing the power analysis against the realized predictor.** Computing
  conditional power before the eval side ran is what makes the FAIL
  honest rather than embarrassing.

## What to change in any successor

1. **Chance floors, not just untrained floors.** Every eval-side margin
   needs a within-answer-space chance baseline. Report both.
2. **Require monotonicity, or report the profile.** A mean across sizes
   reads a 2.8b spike that collapses as moderate ascent (`sub3_mid`:
   .528 / .028 / .022 -> .193). "Scale-ascent" should mean ascent.
3. **Gate on predictor spread before spending the eval side.** The 22-way
   tie was visible at M2, and its power cost was computable then — as it
   in fact was. A successor should treat "fewer than N live family blocks"
   as a stop-and-redesign condition BEFORE the eval campaign, not a
   disclosed limitation afterwards. The eval side cost 5h48m of compute
   that a pre-registered spread gate would have deferred.
4. **Multiple-choice rungs need their option count in the record.** The
   chance rate was recoverable only by re-parsing question text.

## The two results worth keeping

Both are qualitative, both survive the omnibus test's failure, and both
were predicted in advance.

**Decodable but not generable.** The reversal family holds probe ranks 2
and 3 (.699, .624) and scores exactly 0.000 argmax at 2.8b, 6.9b and 12b.
The information is sitting in the representation, linearly readable, and
the model cannot emit it. This is the essay's "necessary, not sufficient"
limitation converted from a caveat into a measurement, and it is the
cleanest thing 2c produced.

**The carve-out case appeared.** `sub3_mid` and `arith_next` are
probe-flat with real eval signal that survives chance correction. The
projection named "a probe-flat rung with substantial ascent" as the
sharpest available disconfirmation of the resolution thesis, and it fired
on two rungs. That is the Lubana-style percolation shape, not the
detection-event shape.

Neither result needs the rank correlation to be true. Both are directly
relevant to the essay, and the second cuts against it.

## Cost accounting, honestly

Probe side ~5 Mac-days (M2, 460 fits). Eval side 5h48m (204 cells, 12b the
long pole at 1h35m per arm — the estimate built from M1 timings predicted
96 minutes and was accurate to within a minute). Total human-facing
elapsed: 2026-07-28 design through 2026-08-12 verdict.

The experiment returned a FAIL it could not interpret. It also returned a
clean screen, a machine-enforced lock, a measured power deficit stated
before the fact, a named defect in its own outcome measure, and two
qualitative findings that bear directly on the essay. That is a worse
outcome than a PASS and a considerably better one than 2b.
