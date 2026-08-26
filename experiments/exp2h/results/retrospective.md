# Exp 2h — Retrospective

## The projection, graded

Sealed at `3a450cd8` after the tag, before gate 1 or any 6.9b checkpoint
loaded (the predictors were known inputs; no checkpoint quantity existed
anywhere).

| line | projected | actual | grade |
|---|---|---|---|
| verdict | CONFIRMED | **CONFIRMED** | **HIT** |
| T | in [.10, .22], point ≈ .15 | .2020 | HIT (inside; point low by .05) |
| p_strat | < .001 | 1.0e-4 (0 of 10,000) | HIT |
| disconfirmer (i) | T in [.05, .10) at p < .01 | did not fire | — |
| disconfirmer (ii) | T ≤ .03, n.s. | did not fire | — |
| probe-beyond-sampler | null | −.0253, p .92 | HIT |
| sampler-beyond-probe | positive | .2030, p 1.0e-4 | HIT |
| probe competitor alone | stays null | −.0187, p .86 (NOT-CONFIRMED in its own tree) | HIT |
| loci repeat: sub_base8, antonym6, add_base8, antonym, arith_next high | — | sub_base8 .408, antonym6 .291, add_base8 .253, arith_next .231 top four; antonym .143 sixth | HIT (antonym the soft spot) |
| count_div13 a likely per-rung miss | low | .090, CI lower bound .013 — weakest of the eight | HIT |
| odd6 a likely per-rung miss | low | .187 [.109, .256] — at the level of the core five | **MISS** |
| add3_mid eligible, contributes little | eligible, ≈ 0 | eligible (n_pos 63), .012 | HIT |
| add3_mid ever ≈ 2× final | 2× | 63 vs 19 = 3.3× | miss (right direction, wrong size) |
| 410m: same direction, lower T, possibly THIN | — | .1417, p 1.0e-4, CONFIRMED in its own tree, nothing THIN | HIT on direction and size; the THIN hedge unneeded |
| gate 1 clean, ninth byte-identical, first at 6.9b | PASS | 34/34 counts exact, digests equal, 17,000/17,000 continuations, 0 diffs | HIT |

Verdict-level HIT with the interval honoured and both bracketing
disconfirmers silent. The one sciencey miss (odd6) points the same way as
the verdict: the concordance is broader across rung types than I allowed
for — the option-listing rung new to a primary behaved like the core five.

## The transferable findings

1. **The 3d → 3e rule paid, at higher T.** A finding that arrived as a
   non-gating secondary in 2g (T .167) was promoted to a preregistered
   PRIMARY on an outcome nobody had seen, with the probe as the named
   competitor, and came back at T .202 (p 1.0e-4, POWERED .979) with the
   same per-rung loci in the same order at the top. Two sealed outcomes,
   two resolution steps (1b → 2.8b, 1b → 6.9b), one committed predictor.
   The output-channel account of item-grain emergence order now has the
   standing the reversal case has — and it is the essay's claim about the
   OUTPUT channel, not a resurrection of Prediction 2's probe form (§5).
2. **The probe adds nothing, twice.** Probe-beyond-sampler is null on
   6.9b as it was on 2.8b (−.025 / −.017); sampler-beyond-probe carries
   the whole effect (.203). Representational presence at 1b, read by the
   instrument that demonstrably reads it at rung level (2f), orders no
   items on either outcome. Presence-before-performability stands where
   it stood (rung level); its predictive arm is an output-channel arm.
3. **The concordance is difficulty-conditional but not difficulty.** With
   the named covariate stratified out and the probe conditioned out, the
   effect survives at every size (410m .142, 1b .202); 1b-beyond-410m
   (.181) says the 1b count carries information the 410m count does not
   in strata of the 410m count — the nearest committed thing to a
   model-specific signal. What 2h cannot do is separate reachability
   from un-named difficulty inside the sampled rate (§5, disclosed on the
   verdict); the successor that could is a cross-family predictor (OLMo),
   where shared un-named difficulty is the null and shared corpus is not.
4. **Checkpoint-local collapses are a real texture of the trajectory.**
   count_div13 at step40000 answers " 13" on all 500 items; mod13_comp at
   step20000 answers " 14" on all 500; roman_sum7 loses two thirds of its
   count at 16k and 30k. Different weight shas, neighbouring rungs
   normal, so this is the model, not the instrument. The count outcome
   (ruling f in 2g, carried here) absorbs them; a rung-level first-clear
   outcome would be hostage to them (count_div13's s* = final is partly
   a collapse artefact). Item-level transience is as pervasive as at
   2.8b (ever/final 1.6× to 4.3×).
5. **Flat rungs can clear transiently at this size.** 2g's "no flat rung
   ever clears" was a 2.8b fact: at 6.9b sub3_mid clears at four
   checkpoints (peak 39/500 at 130k) and ends below its floor; odd_one_out
   clears at 110k only. A "flat" label read at the final checkpoint is a
   statement about where training stopped. The reversal pair, by
   contrast, is flat at every one of 23 points — the famous zero holds at
   greedy across the whole 6.9b trajectory.
6. **The instrument did its job, and the blob-bound tag was exercised.**
   The analyzer re-verified all three instrument blobs against the tag at
   run time (F-3's closure, live); gate 1 ran first with full coverage
   attested (F-2); 23/23 grid points complete and no refusal path taken
   (F-1's 32-tree totality never needed). Zero halts, zero attrition, the
   campaign detached from the session per the reaping gotcha and the
   session survived two restarts without touching it.

## Process notes (for the methods paper, Michael's call)

- Bracketing the null with two disconfirmers (2g's lesson) made this
  projection gradeable in both directions; neither fired, and the
  interval held. A projection line that names a "likely miss" per rung
  (odd6) is itself gradeable — and was wrong in the informative
  direction.
- Promoting a fired secondary to a primary on a sealed outcome, with the
  original primary as the named competitor, is the cheapest replication
  the program has run: zero build novelty beyond the rung set, one
  night of compute, and the strongest result in the arc.
- A count outcome over a checkpoint grid is robust to checkpoint-local
  collapses; a first-clear outcome is not. Worth a sentence wherever
  "first step at which X" is used as an outcome.

## What comes next (Michael's standing conditional)

CONFIRMED → the OLMo cross-family test: a predictor from a different
family and corpus, where shared un-named difficulty survives as the null
and shared training data does not; HF GPU usable (no Mac-stack
byte-identity gate on a fresh family). Rolls into Experiment 4
(convergence / lens) if it holds.
