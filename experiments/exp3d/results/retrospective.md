# Experiment 3d — Retrospective

**Verdict: STRUCTURED** (p = 1.622886e-04, |F| = 8, not THIN).
Adjudicated 2026-08-19. The program's first **forecast** result: a
frozen, model-free functional predicted which items would fire in
draws that did not exist when it was frozen.

---

## 1. The projection, graded

Ledgered in `e5ae9c0` before `analyze_3d.run()` was invoked; git
history is the proof of ordering. Drafted by Claude, approved by
Michael's instruction and unamended.

**Verdict level: MISSED.** Called UNSTRUCTURED at .70–.75 with
P(STRUCTURED) ≈ .20–.25. Got STRUCTURED at p = 1.6e-4. The named
disconfirmer — "if 1b p_low ≤ .05 this projection is WRONG at the
verdict level and the retrospective says so without softening" —
fired, and this section is that saying-so.

| # | prediction | outcome | |
|---|---|---|---|
| P1 | 1b \|F\| in 7–9 | 8 | ✅ |
| P2 | no THIN on the 1b verdict | thin = false | ✅ |
| P3 | 410m \|F\| ≤ 4, annotation THIN | 4, thin = true | ✅ |
| P4 | 0 leak voids | 0 | ✅ |
| P5 | 1b p_low > .05, likely .10–.60 | **1.62e-4** | ❌ |
| P6 | ≥ 1 new fire on a previously-fired item | 123 and 447 | ✅ |
| P7 | ℓ-arm also fails to reject at 1b | **p = 7.9e-9** | ❌ |
| P8 | Spearman(functional, ℓ) in 0 to +.35 | **0.878** | ❌ |
| P9 | gate-1 64,000 draws, 0 diffs | exactly that | ✅ |

**6 hit, 3 missed — and the split is the finding.** Every hit is
bookkeeping: counts, flags, gate totals, quantities largely fixed by
the campaign before any inference. Every miss is substantive: whether
the effect exists, whether the model's own scores see it, and whether
the two tiers agree. The projection got the arithmetic of the
experiment right and its science wrong. A projection that predicts its
own instrument well and its subject badly is worth less than its hit
rate suggests, and the hit rate here (67%) should not be quoted
without this paragraph.

**Why the call was wrong.** Four reasons were given; each failed in a
specific way worth recording.

1. *"Power .2616 and realized |F| ≤ 9 makes it lower still."* The
   power figure was computed against a mis-shaped alternative (§3
   below). Deferring to it was the single biggest error.
2. *"Item g: .2616 is itself optimistic."* Correct as far as it went,
   and it pushed the estimate the wrong way. The selection-optimism
   argument says power against a FRESH concentration is lower — but
   the realized effect was not a fresh concentration on new items, it
   was a standing property of a 45-item CLASS that the in-sample fires
   had merely sampled.
3. *"C1's in-sample 1b AUC is only .679."* A real signal misread. The
   .679 is depressed by the len-4 stratum's binary structure, which
   caps achievable AUC when most fires sit in one class — it is not
   evidence of a weak effect. The unstratified realized AUC was .936.
4. *"The len-4 stratum is binary, so most fires land where the
   functional can only say repeat-vs-not."* Stated as a limitation.
   It was in fact the mechanism: the binary contrast is exactly what
   carried p = 1.6e-4. The same observation supported the wrong
   conclusion because it was read as noise-in-the-instrument rather
   than as the signal's shape.

The transferable lesson: **a coarse instrument is not a weak one.**
Tie structure limits what a statistic can express, not how strong the
effect it detects can be.

---

## 2. What was found

All 8 fired items at 1b sat in the len-4 stratum, which the freeze
record printed as binary — 45 repeat-class items (C1 = 6.0) against
149 all-distinct (8.0).

| class | items | fired | per-item rate |
|---|---|---|---|
| repeat-class | 45 | **7** | 15.6% |
| all-distinct | 149 | 1 | 0.67% |
| | | | **23.2×** |

Expected repeat-class fires under the null: 1.86. Observed: 7.

**Persistence does not explain it** — the caveat raised as freeze item
**h** and retired here on evidence. Six of the eight fired items had
never fired before; five of the seven repeat-class fires are on items
with no prior fire. §5.4 excluded persistence as a competing
forecaster on the grounds that it requires having sampled; the data
now shows it was not doing the work anyway.

410m ran the same direction — 2 of 4 repeat-class against 0.93
expected — at p = .230. Non-gating, THIN, disclosed in advance as
thin-powered (P(|F| ≤ 4) = .9234). It neither replicates nor
contradicts.

---

## 3. The power model was mis-SHAPED, not merely pessimistic

The most useful methodological output of this experiment.

3d was **DECLARED UNDERPOWERED IN ADVANCE** at .2616 against the
program's .75 bar, and then rejected at 1.6e-4 — a p-value four orders
of magnitude below α. That gap is not luck; it is a specification
error in the alternative, and it is reproducible from the committed
`power_3d.json`.

The frozen alternative set per-item rates ∝ (c_i + λ) with λ̂ = .0256:
**item-level** concentration on the 13 committed fires. The realized
structure is **class-level** — a 45-item equivalence class, of which
the committed fires were an unrepresentative 6-item sample. Under the
frozen alternative, a new fire had to land on one of ~7 specific items
to help the statistic. Under the truth, it had to land anywhere in a
45-item class. The target was roughly six times larger than modelled,
and the power calculation had no way to know.

The λ sensitivity grid (.374 at λ=.01 → .058 at λ=1.0) explored the
wrong dimension entirely: it varied how much smoothing diluted the
item-level story, never asking whether the story was item-level at
all.

**For successor designs:** when a functional's tie structure is
printed at freeze — as 3d's was, correctly — the power model should be
computed against an alternative expressed *in that tie structure's own
terms* (per-class rates over the realized equivalence classes), not
only against per-item counts. A binary stratum with 45 items in the
cheap class is a hypothesis about classes, and the alternative should
say so.

---

## 4. Scope, stated against the temptation to overclaim

1. **One stratum carried the test.** len-5 and len-6 gave zero fires
   in 470,016 new draws. §8's within-length defence holds; only len-4
   carried information.
2. **C1 collapsed to a single binary contrast.** This is not a test of
   unigram entropy as a graded predictor. The finer gradations that
   made C1 beat C2 by .0006 in selection were never exercised.
3. **No mechanism claim, and a live alternative that survives.**
   Low-entropy answers are a priori more probable strings, and an
   answer sharing more characters with its own input is more reachable
   by copy-like emission — with ctrl_copy showing copying is
   near-perfect at both sizes. This experiment cannot separate "graded
   reversal competence clears threshold first on easy items" from
   "copy-or-prior-driven emission lands correct more often on
   low-entropy targets." §9 disclaimed mechanism in advance; the
   disclaimer is load-bearing, not decorative.
4. **The ℓ arm is near-tautological.** exp(ℓ) approximates the
   probability of emitting the answer and a fire *is* emitting the
   answer, so p = 7.9e-9 is closer to a consistency check than an
   independent forecast. Its real value is that it *agrees*
   (Spearman .878) with a functional needing no model at all.
5. **reverse_string only**, Pythia 410m/1b, T = 1.0 untruncated, these
   budgets. rev_string7's bounds stand untouched.

---

## 5. What it says about the thesis

The essay argues that "emergent" capabilities are a resolution
phenomenon: the structure is latent, the model is a lens, and the
benchmark jump is a detection event read backwards. The discriminator
against genuine percolation-style birth is the three-signature test —
**probeable below threshold, elicitable by exhaustive sampling,
forecastable from below.**

With this verdict, **reverse_string at Pythia 410m/1b satisfies all
three signatures** — the first real-model capability in the program to
do so:

| signature | evidence |
|---|---|
| 1. probeable below threshold | **3b**: same-weights probe margins .5731–.7725 while first-character emission sits at floor (.026–.052) |
| 2. elicitable by sampling | **3**: 1 verified reversal in 128,000 pure T=1.0 draws; **3c**: DEEPENS, pooled 10/512,000, and the 410m wall fell |
| 3. forecastable from below | **3d**: p = 1.6e-4, 23× per-item rate ratio, forecast from the item file alone |

The load-bearing word is **from below**. The functional needed no
weights, no forward pass, and no samples — it is computable from the
item file, and it was committed with all 500 values before the draws
existed. That is the strictest available reading of signature 3, and
it is the one that was tested.

**What this licenses.** The rare successes of a capability that looks
absent are *not* random. Reversal emission at these scales reads as a
flat zero on any ordinary metric, and 3b showed that zero is not a
Schaeffer metric cliff — matching units surfaced no emission. Yet the
successes that do occur concentrate 23× on structurally cheap items,
predictably, in a direction fixed in advance. A capability that is
simply *absent* has no reason to fail non-randomly. A capability being
read through a hard threshold on a graded underlying quantity has
exactly that reason. This is the item-grain version of the essay's
central move: the zero is a property of the measurement, and looking
closer reveals ordered structure underneath it rather than noise.

**What this does not license, and the honest limit.** §4.3 above is
the constraint that matters most here. The 23× concentration is
equally consistent with a boring story: low-entropy strings are more
probable a priori, and answers that share more characters with their
own input are more reachable by the copying the model already does
well. Under that reading, what 3d forecasts is *which items are cheap
to emit*, not *which items the model half-knows how to reverse*. The
experiment was designed to test forecastability, not mechanism, and it
did that; it cannot adjudicate between these readings, and the essay
must not claim it does. A successor that varies input-output overlap
independently of answer entropy would separate them — that is the
obvious next experiment and it is cheap.

**The bridge the experiment does not build.** 3d demonstrates
item-grain rate structure at *fixed* scale. The essay's claim is about
*benchmark* emergence *across* scale. Those connect by an inference
3d does not make: that the order in which items become reachable as
sampling budget grows is the same order in which they become reachable
as model scale grows. 3c's close-out already named the ladder-order
discriminator; 3d makes the ladder prospective rather than
retrospective, at one scale. Nothing here tests whether the ladder
survives a scale change.

**The carve-out is untouched.** Nothing in 3d bears on Lubana-style
percolation. 1c ruled out sub-critical accumulation ≥ 39% of the
super-critical margin at ≥ 90% power, and the observed 0.85 p_c margin
of +0.0053 (4.1%) sits deep inside that blind region. The carve-out
survives at this resolution and is untested below it, exactly as
before.

**Net.** The thesis gains its first complete three-signature case on a
real model, and the essay can now say that the reversal zero — the
famous one, the one that looked like absence — is probeable,
elicitable, and forecastable. It gains that with a named alternative
explanation still standing, on one task family, at two adjacent
scales, through a functional that collapsed to one binary contrast.
Strong enough to state plainly; not strong enough to state broadly.

---

## 6. What went right, for the record

- **The freeze earned its keep twice.** It found the class defect in
  two places (`answer_type` and gate-1 coverage), and it *printed the
  tie structure in advance* — which is why §2's binary-stratum reading
  is a confirmation of a disclosed limitation rather than a discovery
  after the fact.
- **The order held.** gate 1 → scoring → tranche, enforced in three
  layers, with the projection sealed before the analyzer ran. Nothing
  about this verdict depends on trusting anyone's memory of what
  happened when; the git history carries it.
- **Every gate was informative, not ceremonial.** The ctrl_copy gate's
  p̂/r values (.846, .878) landed below r in the direction the
  prefix-mass mechanism predicts and agreed across two independently
  scored cells — a result, not a formality.
- **Five byte-identical stream reproductions** now stand on this
  stack.

## 7. Successors named here

1. **Separate entropy from input-output overlap** (the §4.3 confound).
   Cheap, and it is the difference between "cheap to emit" and
   "half-known." Highest priority.
2. **Class-level power modelling** (§3) as a standing design rule.
3. **Does the ladder survive scale?** The same functional against a
   larger model's fires — the bridge §5 declines to build.
4. Probe-margin × fire-count join at item grain — still blocked by the
   two-stage lock's disjoint splits, still deferred to a possible 3e.
