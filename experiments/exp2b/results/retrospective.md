# Experiment 2b — Closeout Retrospective (2026-07-27)

Companion to `VERDICT.txt` (INSUFFICIENT_DATA, n = 12 < 20). This document
records what the experiment bought, what it cost, and what its successors
inherit. The adjudication record is in `PROGRESS.md` (rulings a–d, all
accepted 2026-07-27); this file distills, it does not adjudicate.

## The arc

Exp 2 died when the untrained-weights control fired on the entire battery
at margin 1.0: linear probes were reading lookup tables out of a random
network (reservoir decodability). 2b's answer was the basis-starved split —
validation items whose surface components were entirely held out — plus
calibrated gates with binomial tolerances. The starving worked against the
class it was designed for: the mod7 family, Exp 2's proven offender, fell
from margin 1.0 to ≈.1 untrained, and both known-lookup rehearsal worlds
went silent. The campaign then found the class underneath: 13 of 25
capabilities remained decodable from untrained weights at margins .06–.82,
reproducing almost exactly across two independently initialized models —
labels partially computable from input surface statistics through random
projections, a leak that generalizes across held-out items and is
therefore immune to starving. Attrition took the battery below its floor.
No Stage 1, no eval query, no bits on the thesis in either direction.

## What worked (inherited as-is by 2c)

- **The instrument.** probe_starved + starving splits: bit-deterministic
  across three architectures/BLAS stacks; saw plainly-present capabilities
  (gate 2: entity_track .330/.281, ctrl_copy at ceiling); silent under
  label destruction (gate 3 count test p = .538); and caught real
  contamination with cross-init reproducibility (gate 1). Both experiment
  deaths were detections, not misses.
- **The projection discipline.** The verdict was projected in the ledger
  from gate-1 data on 07-23/24, days before the frozen report ran, and the
  report confirmed it line for line. Timestamped observation-before-
  adjudication is now demonstrated practice, not aspiration.
- **The distributed harness.** Determinism gate (bit-identical fixture
  across arm64 Accelerate / x86_64 OpenBLAS / AMD64 Windows), idempotent
  skip-if-exists merging, resumable campaign. Survived a mid-campaign
  crash, a fleet restructure, and a box release without losing a unit.

## What failed, in three distinct classes

1. **The battery (scientific failure, the verdict's cause).** Surface-
   computability leaks. The taxonomy — which task families leak and why
   (parity-adjacent structure riding digit tokens, length/character
   statistics, roman-form cues) — is the raw material for both the 2c
   battery design and the methods paper. The trained-vs-untrained margin
   comparison (m3 vs known_absent, both sizes, all 25 capabilities) marks
   which leakers carry real learned structure atop the leak (rescuable
   with a redesigned basis) and which are surface all the way down.
2. **Frozen-criterion drafting (two bugs, two classes).** (i) Implementation
   deviation: the report's pooled-count abort made §4.1's attrition
   provision unreachable for any possible data (trips at 7 fires; one
   leaking capability contributes 10). Same class as the shuffle-before-
   split runner bug. (ii) Design-level miscalibration: the floor-signature
   predicate's 3-SD conjunct contradicts its at-floor conjunct (expected
   max of 2500 null draws ≈ 3.4 SD) — Exp 1's S1 lesson recurring one
   level down.
3. **Assumption transfer (gate 4).** Argmax reliability measured on Exp 2's
   items (.994) did not transfer to 2b's items (.868 at 410m). Controls
   must be re-measured per battery version, and gates whose inputs exist
   at freeze time must be adjudicated at freeze time — this one was
   checkable eight days before the campaign spent its compute.

## Standing rules promoted at this closeout

1. Adjudication code is frozen WITH fixture tests derived from the design
   doc's worked examples plus one synthetic case per preregistered
   provision ("one leaking capability" must yield attrition-without-abort).
2. Signature bars are calibrated against the mechanism that generates the
   events (order statistics of the permutation max), never against an SD
   intuition. Second occurrence; now standing.
3. Gates whose inputs are committed pre-freeze are adjudicated pre-freeze.
4. (Carried forward unchanged: dumbest-baseline before freeze; binomial
   tolerances on nonzero-rate tests; per-box determinism gates; the
   two-stage lock; one-pre-committed-change; every zero as a CP bound.)

## What 2c starts with

Twelve surviving capabilities as seed stock (listed in VERDICT.txt); an
untrained-weights screening gate promoted from post-hoc control to
pre-inclusion acceptance test; a certified instrument requiring no
re-validation; measured campaign economics (43 min/unit at 410m, 2× at 1b,
Mac-led); and a leak taxonomy that turns battery design from hopeful
generation into constraint satisfaction. The observation that ctrl_copy at
410m reads .997 by probe and .868 by argmax generation — a representation-
vs-output-channel gap on our own control — is recorded as bounded color
for the essay's pattern, not as evidence.

## Cost accounting, honestly

Two batteries and roughly six weeks of wall time bought: a validated
instrument class (Exp 1), a production instrument certified under fire
(2b), two empirically mapped confound classes with countermeasures, three
new standing process rules, and the methods paper's complete arc. The
thesis experiment has not yet run. It is now one constraint-satisfying
battery away, and every failure mode it must survive is enumerated and
testable in advance.
