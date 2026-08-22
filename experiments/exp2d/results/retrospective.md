# Exp 2d — Retrospective (written after the frozen analyzer's single run, 2026-08-22)

## The projection, graded

Sealed at `d40a1cf` (correction note `0135e20`) after pilot and main
had landed and before any 1b argmax record existed; the predictor's
per-rung tallies were visible in the runner logs, so the projection
is of the frozen analyzer's OUTPUT, as disclosed in the file.

| line | projected | actual | grade |
|---|---|---|---|
| verdict | FAIL via the cluster CI | FAIL via the cluster CI | **HIT** |
| AUC | .5455 | .5455 | HIT (arithmetic) |
| block p | ≈ .67 (6 of 9 block placements) | .6675 | HIT |
| CI lower bound | exactly .5000 (seq_extrap-omission) | .5000 | HIT |
| CI upper bound | ≈ .59 | .6667 | miss (the resamples that draw seq_extrap twice or more against few flat families) |
| drops | 1–2 of 10,000 | 2 | HIT |
| declared status | DECLARED UNDERPOWERED (0.000) | as carried | HIT (already on the record) |
| gate 1 | 4/4 identical, 436/6 reproduced | as carried; analyzer's own re-comparison 0 diffs | HIT |
| predictor zero set | 33 of 34; 10 rising at zero; 0 rising raw-zero at 1b | 33; 10; 0 | HIT |
| sub3_mid / arith_next candidates | no / no; disconfirmer does not fire | no / no | HIT |
| probe AUC on the same label | .6703 (copied from the template — the BUILD's number under the 13/21 label) | .6008 (block p .383, CI includes .5) | **miss on the point** (stale literal), hit on the reading |
| ρ vs corrected ascent | ≈ .20–.30 | .288 (block p .220) | HIT |
| ρ vs 2c frozen ascent | similar | .188 | HIT |
| argmax performable at 1b | 2–3 rising (antonym, antonym6, maybe arith_next); 0 flat | **1** (arith_next only); 0 flat | **miss** — the 1b model is below a random option copier even at greedy |
| restricted primary | AUC .5, CI [.5, .5] if arith_next removed | AUC .5, CI [.5, .5] | HIT |
| redecode diffs | 0 | 0 (4/4) | HIT (not credited: two lines were printed before the seal) |
| concordance | NaN except seq_extrap = +1 | as projected | HIT |

Verdict-level: **HIT**. Three misses, one of them science: the
option-listing rungs are below their 1/n floors at 1b under greedy
decoding too, not only under T = 1 sampling. That is the finding the
freeze's bar-resolution note (F-6) did not anticipate: the gap
between a 1b Pythia and "copy a listed option at random" is not a
sampling-temperature artefact — the model emits non-option text
under both decodings.

## What the experiment found

1. **The sampled channel at 410m/1b does not clear a model-free
   format floor on 10 of the 11 rungs that clear it at 2.8b–12b**,
   and the bounds exclude the floors: this is a measured absence at
   32,000 draws, not a resolution shortfall. The one rung it clears
   (arith_next) it clears at the SMALLER size and not the larger —
   a size-ordering the ladder story does not predict.
2. **The predictor is a 33-way tie at zero.** The AUC can only be
   what one positive rung makes it (.5455). Under the symmetric power
   rule the pilot said exactly this in advance (P(PASS) = 0 at every
   target); under the Tobit as built it would have said .7365 — F-4
   was the difference between a declaration that reads the data and
   one that reads the model.
3. **The §5.4 pair is not percolation-class on this instrument:**
   sub3_mid and arith_next both have sampled draws at 1b (34 and
   531 of 32,000). The probe's silence on them (2c) was the probe.
   Whether their sub-floor sampled rates are "precursor" signal or
   format-guessing at a rate below the majority share is not
   decidable by this design — the floor rule treats everything
   below c as zero on purpose.
4. **The option-listing rungs undercut a random copier at ≤ 1b under
   both decodings.** antonym greedy 87/500 at 1b vs 2c's 2.8b argmax
   .544: the 1b→2.8b step is where these rungs cross 1/n, and
   nothing at 1b — probe margin (.514 for antonym, 2c), sampled rate
   (.137), greedy (.174) — reads it as imminent in a way the floor
   rule credits. The probe DOES read antonym (.514) and odd6 (.716)
   where the sampler reads zero; the instrument-disagreement
   descriptive is where that sits.
5. **Gate 1 on the production path held:** 128,000 draws byte-
   identical through a different experiment's runner, one seed out
   of four; redecode 0 diffs; both preflights byte-identical. The
   stack has now reproduced exp3's streams eight consecutive times.

## What it does not say

- Nothing about a hidden outcome (§2). Nothing about the reversal
  ladder finding of 3b–3e, which lives on rungs that read 0/0/0/1
  here exactly as committed. Nothing about whether a LARGER k, a
  lower floor, or a different floor rule would change the picture —
  FAIL is "not detected at this resolution" and the blind region is
  the band between each rung's CP95 upper bound and its floor.
- The majority / 1-of-n floor is the frozen rule; that the sampled
  channel lands below it on nearly every rising rung says the floor
  is high relative to what 410m/1b Pythia emits, which is what
  "format-guessing" means here, not that the rule is wrong.

## Freeze findings, revisited after the data

- F-1 (halt-tree terminal): not exercised — gate 1 was clean — but
  the scan ran first on every analyzer call and returned silent.
- F-2 pins: all held (power record == pilot tier; model_sha on gate-1
  and argmax records == 2b's pins).
- F-3 (first-digit-run criterion): both rungs flat and at predictor
  zero (base13 147 | 173 of 32,000 vs .068); the disclosure cost
  nothing and the descriptive carried it.
- F-4 (symmetric rule): decisive for the declaration (0 vs .7365).
- F-5 (reversal rungs first): gate 1 landed 60 min into each size's
  main tier instead of ~4 h in.
- F-6 (bar resolution): the worry was spurious predictor POSITIVES
  from per-item clustering; the data produced none — 33 zeros.

## Process record

Three-session design | build | freeze protocol on one day
(2026-08-21), campaign 2026-08-21/22: pilot 363 min, main 627.7 min,
argmax 13.4 min; 344 artifacts, 209 watcher units, zero stops, zero
attrition, one pre-committed change UNSPENT, projection sealed before
the analyzer, analyzer run once. Timing miss: the doc's 1.7 h / 13 h
estimates (from 3e's 8,192-draws-per-item throughput) were 363 min /
628 min — prompt-forward amortisation at k = 8 and k = 64 is the
difference; successors should budget from draws-per-item.

## Candidate lessons for the methods paper (Michael's call)

- A frozen verdict must be able to deliver its own refusal terminal
  from the tree the runner actually leaves behind (F-1; 3a's class
  one level up — the synthetic world that "reached" the terminal was
  a tree the runner could never produce).
- A power model that honours realized structure on one side of the
  label only is a model of its own assumptions; condition
  symmetrically or not at all (F-4).
- "Exact match" is a property of the normalizer on the answer
  alphabet, not of the experiment's intent; enumerate the normalized
  multiset before calling it exact (F-3).
