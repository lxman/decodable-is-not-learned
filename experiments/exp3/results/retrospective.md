# Experiment 3 — retrospective

Closed 2026-08-17, VERDICT: PARTIAL (per-cell table the headline:
three WALL, one TAIL-ONLY). Verdict record `results/verdict.json`;
this file grades the projection, names what surprised us, and
extracts the lessons that outlive the experiment.

## The projection, graded

Ledgered at 55a34e0, before the frozen analysis ran, attributed to
the assistant. Projected: PARTIAL — both 1b cells BULK-ONLY, both
410m cells WALL; no fires anywhere; all gates clean.

| call | projected | realized | grade |
|---|---|---|---|
| verdict | PARTIAL | PARTIAL | **HIT** (verdict level) |
| 410m cells | WALL, WALL | WALL, WALL | **HIT** ×2 |
| 1b cells | BULK-ONLY ×2 | WALL, TAIL-ONLY | **MISS** ×2 |
| fire arm | 0 fires / 512k adjudicated draws | 1 fire | MISS by exactly one draw |
| mass arm at 1b | θ > .564 (sig) | K = 109, 115 of 500 (θ ≈ .21–.23) | MISS, by SIGN |
| gates | all clean | all clean | HIT |
| twins | silent | 0 fires, no mass arm | HIT |

Both misses were the projection's own *named disconfirmers* — the
ledger entry called out "ANY verified fire anywhere" and mass-arm
uncertainty explicitly. What the projection got wrong is more
instructive than what it got right:

1. **The fire.** One verified success in 128,000 draws
   (reverse_string/1b, item 436, 'xuvq' → " qvux", seed 0). The
   projection reasoned the joint path sat orders below the 1e-5
   detection edge — for the 4-character floor of the answer-length
   distribution, it does not. The fire landed exactly where the
   autoregressive path is cheapest: the shortest answer class of the
   shorter-answer rung, at the larger model. Mechanistically
   coherent, and precisely the asymmetric-evidence regime the
   forward-note preregistered: existence, not rate.
2. **The sign inversion.** The projection treated the 1b mass arm as
   "will the precursor clear the blind edge" — a magnitude question.
   The realized K ≈ 100/500 is not a magnitude miss but a DIRECTION:
   the input's interior characters out-mass the input's final
   character at emission position 1 on ~4 of 5 items. The readout
   carries a primacy-shaped position gradient (the same shape as 3b's
   greedy echo dominance, input[0] at 89–94%), and the reversal
   character sits at the BOTTOM of that gradient, not merely below
   significance. The projection's mechanism set had "consistent small
   elevation" and "noise"; it did not contain "consistent small
   anti-elevation." It should have: 3b's echo numbers were in hand.

## The finding that outlives the omnibus verdict

**The freeze amendment changed what this data means.** Under the
superseded w̃ statistic, input-letter mass concentration — which is
overwhelming in these cells (3b greedy in-answer-set rates
.968–.984) — would have been credited as positive signal on nearly
every item: the correct letter is always an input letter, and the
w̃ competitors are mostly absent letters. The same campaign data
would very plausibly have read "mass significantly elevated in all
four cells" and the verdict would have been BULK-ONLY — a
manufactured, thesis-friendly claim. The amended within-item
statistic instead measured the position gradient and found it
pointing AWAY from the reversal character. (Descriptive commentary,
not a computed re-adjudication — no re-run of the superseded
statistic was or will be performed.) The class defect the
adversarial freeze found was not hypothetical: it would have decided
this verdict.

Three-layer signature-2 profile now on record for the same weights:
present in the residual stream (3b, margins .57–.77); reachable by
exhaustive sampling in the tail (this experiment, one cell,
1/128,000); rank-invisible — indeed rank-inverted — in position-1
mass everywhere. "The information is in the distribution" is TRUE at
depth k in one cell and FALSE as a bulk property everywhere, which
is a sharper statement than either instrument alone could make.

## Estimate misses and operational record

- **6.9b fp32 mass tier: 10.6 h** against a few-hour projection —
  fp32 at ~27 GB under memory pressure; the sub-linear scaling that
  held to 2.8b broke at 6.9b. Future fp32 ladders on this box should
  budget the top size at ~5× the 2.8b tier, or the design should
  accept fp16 keep1-only descriptives there (the 12b pattern).
- **Campaign total 28.4 h** (design's "one overnight" was wrong;
  the revised in-flight estimates converged by mid-run).
- **Stop #1** (padded-vocab class table, 50304 vs 50277) — the one
  campaign irregularity: mechanism-forced fix, ledgered before
  relaunch, zero quantities existed. Root lesson: the build
  invariant "no real-model quantities pre-tag" silently became "no
  real-model GLUE contact pre-tag." A quantity-free tokenizer/config
  smoke now exists as a permanent fixture and belongs on every
  future freeze checklist.
- **Determinism at the wall clock:** twin/trained sampling tiers
  matched to the second (6454 s/6454 s at 410m; 11,214/11,203 at
  1b) — the seeded per-(cell, seed, item) substream design measured
  as identical work.
- The 12b `--keep1-only` preflight (freeze finding #3) passed live;
  without it the driver would likely have halted before its own
  descriptive tier.
- Watcher-based per-cell commit+push worked: every cell in git
  within minutes of landing, three-layer attestation intact, final
  sweep clean.

## Freeze-session findings, recapped for the record

1. **The class defect (2c's class):** §5's w̃ statistic credited
   set-level lexical priming; demonstrated K = 500/500 at
   p ≈ 3e-151 on a position-blind primer; amended pre-tag to the
   within-item interior-competitor form with θ = .5 exact by
   position exchangeability; ratified by Michael. See above for why
   it mattered.
2. **Gate-3 scope:** both gate-1 arms can pass over an incoherent
   positive control; ID trigger widened to adjudicated ∪
   ctrl_copy-trained. (Did not fire; the control cohered to the
   third decimal.)
3. **12b preflight conflation:** fixed as above; proved out live.

The mutation discipline also earned its keep at the freeze: the
official 56-mutant run caught a fixture blind spot the gate-3
widening itself had created (55/56), forcing the world that isolates
gate 1's both-sizes rule.

## What Exp 3 does not claim (unchanged from the frozen doc)

Nothing above the probe sizes; nothing about learned verifiers or
temperatures ≠ 1.0; ELICITABLE-class substrate claims only in the
one fired cell, as existence; WALL cells are resolution statements
(mass blind θ ≲ .563, sampling blind below ~1e-5), never zeros; no
re-adjudication of 3b/2c; Pythia only, these rungs only.

## Next

- Essay + `experiments.md`: signature-2 status update (fires by
  exhaustive sampling in the shortest-answer cell; mass-rank
  inverted by a primacy gradient — the "detection event read
  backwards" story gains a measured position-gradient mechanism).
- Methods paper: the freeze-amendment arc (a preregistered primary
  criterion killed by its own dumbest-baseline analysis AT THE
  FREEZE, with the verdict-deciding consequence documented above) is
  a §-worthy instrument lesson if Michael wants it.
- The staged-deepening follow-up (k = 1024 on the WALL cells) and
  the rank-prediction successor remain explicitly separate
  experiments.
