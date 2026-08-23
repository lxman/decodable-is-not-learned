# Exp 1c — Closeout Retrospective

**VERDICT: FAIL.** No detectable sub-critical accumulation. Written
2026-08-14, the same day the experiment was designed, frozen and run.

---

## 1. What was asked, and what came back

Below the percolation threshold, does linearly decodable class structure
accumulate with graph density while the capability metric stays flat?

No — at the resolution this battery could deliver. 40 cells across
0.25/0.45/0.65/0.85 p_c, 8 probe sites each, every one compared against its
own untrained twin: **0 of 320 sites fire.** 40 of 40 cells classify
`silent`. The pooled slope is +0.0246 at block p = .074, short of the α = .01
bar, and it is driven by the lowest density reading *below* its twins rather
than by the highest density rising.

The capability half of the conjunction was measured too, not assumed:
0.0878–0.1040 against a chance of 0.1000, flat and at chance throughout. Both
halves are flat. The interesting conjunction — structure rising while
capability sits still — does not occur.

## 2. The thing that makes this experiment cheap, and why it existed at all

1c trained nothing. It read 1,800 checkpoints that `run_lubana.py`'s S3 graph
branch had written during the 1b campaign and from which exactly one scalar
per cell had ever been taken — `sub_hist.eval_metric[-1]`, a y-value for a
forecast. `best_probe_accuracy` is called once in that file, at line 192, in
the *training-steps* branch. The graph branch never probed anything.

So a whole sub-critical dose-response axis had been sitting on disk since the
1b campaign closed, fully trained, never looked at. Finding it cost one
careful read of a file the program had already run hundreds of times.

**Transferable:** when an experiment discards intermediate state to compute a
summary statistic, the discarded state is a dataset. Ask what was thrown away
before commissioning new compute.

## 3. The projection missed, in a specific and instructive way

On the record before the analysis ran (commit `c54ca41`, pushed while Stage B
was still executing): *flat depth slope, L0 fires and tracks pool size* —
`FAIL (layer-0 leakage)`, the stronger of the two named variants because it
commits to a mechanism.

| component | projected | measured |
|---|---|---|
| flat depth slope | yes | slope +.0246, p .07431 — flat at the bar |
| L0 fires | yes | **0 of 320 sites**, 0 of 40 cells (CP95 ≤ .0881) |
| L tracks pool size | yes | slope −2.4e−05, **p .81261** — zero, wrong sign |

The outcome held; the mechanism did not. And the mechanism was the
interesting half — it was the program's own accumulated experience talking,
since in four of five closed experiments the finding had come from the
measurement apparatus rather than the models.

**Why the expectation was wrong.** The generalisation "the apparatus
manufactures the signal" was drawn from experiments whose probes ran on
*real* models (Pythia) with rich token statistics, or on grokking, whose
probe has a single site, 1500 validation rows, a 0.0088 chance floor and a
Bonferroni family of one. The lubana entity probe has none of those
properties: one prompt per entity, a fixed lVerb, an entity split by
construction, 100 validation rows, a 0.1 floor and a family of 8. It was
already the hygienic case — `run_lubana.py:14` says so in a comment written
long before 1c. Generalising the leak from the leaky probes to the clean one
was the error, and it was available to spot before the data.

This is the second consecutive projection miss (1b forecast ~6/10 and FAIL,
got 9/10 and PASS). Both were legible only because they were written first.

## 4. What is genuinely new

**The first clean null in the program.** Exp 2's untrained control fired on
120 of 120 fits and ended the experiment. 2b's caught surface-statistics
leaks in 13 of 25 capabilities. 2c's empirical untrained floors were ≈0, so
format-only competence was credited its guessing rate, and correcting it took
ρ from .368 to .2005 — the contamination was *manufacturing* signal. 1c:
**0 of 480 twin sites and 0 of 320 trained sites fire.** Neither the models
nor the apparatus produced a spurious fire.

That matters beyond this verdict. It shows the two-gate rule can return a
clean null, which is the property that makes a null informative rather than
merely uninformative.

**The mean-over-sites statistic is stricter than the argmax it replaces.**
Stage A reproduced 1b's known answers but demoted two of ten `lubana_above`
cells (10/10 S1-present on the argmax → 9/10 positive, 8/10 classed `depth`).
An argmax over 8 candidates is biased upward; removing the selection removes
the bias with it. Any probing result reported as "best layer" carries that
bias silently.

**Layer 0 and depth are separable, measured.** In trained above-threshold
cells every one of ten has a positive layer-0 margin (+0.020 to +0.080) while
none classifies `L0-only`, because depth dominates throughout. In the
sub-critical sweep both are flat together. L and M move independently, which
is what makes the layer-0 diagnostic a real discriminator rather than a
restatement of the depth measure.

**Power was fixed against measured variance before the scored run.** A first
for this program. 2c's power table assumed 16 permutable blocks where 7 were
live, and the shortfall was only visible afterwards. 1c measured sd = 0.031042
on Stage A's known-answer cells, computed power = .713 at a 0.04 margin,
found it under the preregistered .75 bar, and declared the experiment
underpowered in advance — in a commit pushed before any sweep cell was
probed.

## 5. What this FAIL does not license

The observed margin at 0.85 p_c is +0.0053, **4.1% of the super-critical
margin** (+0.1297). The declared resolution rules out accumulation at ≥39% of
that margin with ≥90% power and ≥31% at 71%; below roughly 23% power falls
under one half. The observed value sits deep inside the blind region.

So the honest statement is narrow: **sub-critical accumulation, if it exists,
is smaller than about a quarter of the super-critical signal.** The carve-out
survives its own measurement at this resolution and is untested below it. A
successor that wants the tail needs more seeds, which needs training, which
1c deliberately did not do.

Two further limits carried from the design. The **composition confound** is
unfixed and unfixable here: at higher density the surviving singletons are a
more selected set — the entities that failed to join a component — which
biases the primary test toward the null, i.e. toward the result obtained.
And the sweep probes only the terminal checkpoint of a 10,000-step budget; a
capability that never forms may still have a trajectory, and this reads one
point on it.

## 6. Process: what went right and what did not

**Right.** Twins ran first, all 100, before any trained cell was read. The
loader was frozen *with* the analysis, closing 1b's gap — records on disk fed
`verdict()` with no glue written afterwards. Mutation testing killed 20 of 20
deliberate defects, and the one mutant that initially survived (a per-site
train/val split) was the exact invariant that had been rationalised away
while writing the suite. The capability metric was measured before the
freeze, which is what made the conjunction live rather than hopeful. The
power table was finalised against measured variance and the underpowered
declaration was made before the data.

**Not right.** `verdict()` accepts `natural_l0_tracks_pool` but the frozen
module has no function computing it — verdict-*adjacent* glue, missing from
the frozen artifact. The rule was preregistered in §4; the implementation was
written after Stage B and committed before being run. It changed nothing
here, because `variant` was `none` regardless. But this is precisely 1b's
missing-loader defect reproduced one level over, **in the experiment whose
design doc explicitly congratulated itself on fixing it**. The lesson did not
generalise from "the loader" to "every input the verdict function takes".

**Provenance.** 99 of 100 twin records carry `git_sha …-dirty`, because a
parallel campaign writes its own output into the tree it stamps. An empty
diff across every `.py` and `.md` confirms no code changed mid-run. 1b avoided
this by committing per cell, which serial campaigns permit and 8-worker ones
do not.

## 7. Successors

1. **Freeze every input the verdict function takes, not just the loader.** A
   frozen `verdict(a, b, c)` whose `c` has no frozen producer is not frozen.
   Mechanical check: every parameter of the verdict entry point either has a
   frozen computing function or a fixture that pins its value.
2. **Do not generalise a failure mode across probe designs without checking
   the design.** The layer-0 leakage expectation came from probes with token
   overlap, large validation sets and low chance floors. The lubana entity
   probe has none of those and was documented as hygienic before 1c existed.
3. **Report the effect as a fraction of a measured reference.** "+0.0053" is
   uninterpretable; "4.1% of the super-critical margin" is the sentence that
   makes the null's scope obvious.
4. **A dose-response axis beats a two-point contrast** when the region between
   the points is the claim. 1b left `lubana_below` and `lubana_above` as
   endpoints; the sweep read the interior for no new compute.
5. **Restore the 100M tier if affordable** — carried forward unaddressed from
   1b, and still the tier where the discriminator was most stressed.
6. **The tail needs training.** Resolving accumulation below ~23% of the
   super-critical margin requires more seeds than the 5 the sweep has. That
   is a training campaign, not a re-probe.
