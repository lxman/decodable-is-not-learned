# Exp 2f — Retrospective

## Grading the projection (sealed 13c835d, before the analyzer)

| Projected | Actual | Grade |
|---|---|---|
| Verdict INVERTED (≈ .6), LADDER the named alternative (≈ .35) | **LADDER** | **MISS at the verdict level**; the named alternative fired |
| Mechanism: a true small probe reading under the probe's higher bar | every probe reading clears its bar by .05–.10 | MISS — the asymmetry never bit |
| arith_next/1b decides; probe best .15–.20 vs bar .170 | probe **.270** | MISS (disconfirmer "LADDER with the 1b probe ≥ .20" FIRED) |
| arith_next probe at 410m .13–.17 | .262 | MISS |
| arith_next sampling detected both sizes, .16–.24 | 410m .1348 detected; **1b .1001, below the floor** | half MISS — the alternative I named ("the wrong numbers are not near-misses") fired at 1b |
| arith_next argmax 1b detected .17–.22; 410m marginal | 1b .140 n.s.; 410m .162 detected | MISS / partial |
| sub3_mid (0, 0, 0) both sizes; probe at chance | **(1, 0, 0)** both sizes; probe .234 / .252 | MISS — the probe reads the middle digit where no generator reads anything |
| Void: no; twin ≈ .10–.13 | no; twin .04–.10 at the trained best site | HIT |
| mod 7: sampling detected (weakly); probe not; argmax not | sampling .142/.139 n.s.; probe .124 n.s.; argmax n.s. | probe/argmax HIT, sampling MISS |
| α = .05 may flip INVERTED → LADDER | LADDER under every sensitivity | moot |
| CV probe ≥ eval reading | CV .26/.24/.19/.22 vs eval .26/.27/.23/.25 | MISS in direction (eval higher), HIT in magnitude |
| Gate 1 on the record (IDENTICAL ×8) | as recorded | HIT (known before sealing) |

**Every projection about the probe was low, by .07–.10, and every
projection about the generators was high.** The projection reasoned
that the prompt-end representation would carry "the last digit of
what the model is about to say" — argmax-level information — and
that the sampled channel would carry partial last-digit competence.
Both were wrong in the same direction: the representation carries
MORE than the output, and the output carries LESS than chance. That
is the ladder, measured, and the projection's author did not believe
it enough to bet on it.

## What the numbers say

1. **Presence before performability, on arithmetic, four cells of
   four.** The linear probe reads the answer's digit at .23–.27 in
   every cell; the generators read it in one cell (arith_next/410m)
   and nowhere on sub3_mid. The essay's instrument ladder — probes
   see deepest, sampling next, argmax last — holds on a second task
   class with the same weights, the same items, the same label, the
   same floor and the same bar.
2. **The sampled channel at 1b is BELOW chance on arith_next's last
   digit** (8.5 % among the 31,469 non-exact draws against 10 %
   uniform). A model that is wrong about a + 4d is wrong about its
   last digit: the errors are off by a step (±d changes the last
   digit unless d ≡ 0 mod 10), not arithmetic slips. Meanwhile its
   residual stream carries the right last digit at .270. The
   representation knows something the sampler actively avoids
   emitting.
3. **2c's silence was its target and its split, executably.** The
   same 1b activations read the last digit at .270 and the mod-7
   residue at .124 (bar .212); the committed starved records sat
   below chance at every real site. A probe label chosen to defeat
   lookup (a residue) is not a linear feature; a basis-starved
   validation set measures compositional generalization, not
   presence. 2d's "the probe's silence was the probe" stands, with
   the reason now specific.
4. **Where the probe reads:** late layers at the PROMPT END on
   arith_next (layers 21 / 15 of 25 / 17 — the model is about to
   emit the number), mid-to-late layers at the QUESTION END on
   sub3_mid (layers 15 / 9 — the difference's middle digit is
   represented before the answer cue). Descriptive, unpreregistered,
   noted.
5. **The pilot tier at arith_next/410m did not detect** (.127, p .09
   at 4,000 draws) where main did (.1348 at 32,000): the sampling
   rung's detection there is a resolution effect at the bar, and the
   .1348 is itself small. The ladder's middle rung is faint on this
   battery; the top rung is not.

## Process

- The projection missed at the verdict level, and the miss is
  instructive: the declared bar asymmetry (§7) was a real design
  weakness that the data made irrelevant — the probe readings were
  never near the bar. "Declared in advance" protected the reading
  either way.
- Build and freeze in one day held: gate 1 IDENTICAL on every
  comparison; every referent exact; the mod-7 sensitivity did the
  explanatory work the design asked of it.
- Model contact 4,064 forward passes; zero stops; one pre-committed
  change UNSPENT; no label-match rate computed before the tag.

## What 2f licenses (§6 LADDER, as written in advance)

The essay's instrument-ladder paragraph stands on a second task
class; 2c's silence on the pair is attributed to its targets; and a
methods note is earned for Michael's call: **the target is part of
the instrument** — a probe's silence is a statement about a label
and a split, not about a representation, until the same activations
have been read against a label the representation could carry.
