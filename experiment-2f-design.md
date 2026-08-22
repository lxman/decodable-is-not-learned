# Experiment 2f — Design Doc: Ladder Order on the Probe-Flat-but-Rising Pair — One Label, Three Instruments, the Same Weights

**Status: §10 DIALS RULED by Michael 2026-08-22 ("dials as
recommended — build"): a last-digit label for arith_next, 2c's mod-7
printed; b the eval-item probe primary, probe-item CV printed; c void
on twin detection; d Bonferroni over 2c's site family; e INVERTED
includes argmax-without-sampler; f licences as written. Session 1
(design) written 2026-08-22 after Exp 2e closed; BUILD is session 2.
Model contact is confined to one small activation collection (§9),
after the tag, on Michael's word; nothing is sampled.**

Lineage: 2c (probe ladder, FAIL) → 2d (sampling ladder, FAIL) → 2e
(floor as covariate, FAIL) → 2f. 2d's §5.4 found that the two rungs
2c had flagged as probe-flat with real ascent — `sub3_mid` and
`arith_next` — are NOT silent under sampling (34 and 531 verified
draws in 32,000 at 1b), and its verdict said "the probe's silence was
the probe". The essay now leans on an instrument ladder — probes see
deepest, exhaustive sampling next, argmax last — established on
reversal (3b → 3e). On `arith_next` the record reads the other way
round: 2c's probe margin 0 at both sizes, the sampler above its floor
at 410m, greedy decoding performable at 1b (19/500, p .0066 against
the .020 floor). If that inversion is real, the ladder is a property
of reversal, not of instruments, and the essay's discriminator loses
its ordering clause.

## 1. The question, and what the design session found

**On `arith_next` and `sub3_mid` at 410m and 1b, with ONE label, ONE
floor and ONE bar, do the three instruments detect in ladder order —
argmax ⇒ sampling ⇒ probe — or not?**

What the design session found, which reframes the anomaly: 2c's
probe and 2d's generation instruments never read the same quantity.
2c's probe label for `arith_next` was **(a + 4d) mod 7** — a
seven-class residue chosen so that holding out the first term `a`
would starve an a-to-label lookup — and for `sub3_mid` the middle
digit of the difference under a split that held out tens-digit
pairs; both probes were scored on basis-STARVED validation sets, i.e.
on compositional generalization to held-out basis values. 2d's
sampler and argmax were scored on the FULL answer over the 500 eval
items, no starving. And the committed probe records show that at
every candidate site the corrected p was 1.0 and the "best" site
defaulted to (layer 0, token 0) — the embedding of the question's
last token, a constant feature — whose accuracy (.135 / .130) is the
train-majority rate, below the majority share. So "probe 0, sampler
34" was two instruments, two targets, two item sets. 2f puts all
three on one target, one item set, one floor.

## 2. What is known to the designer (disclosure)

Known and committed: 2d's exact-match counts on the four cells
(sub3_mid 35 | 34, arith_next 831 | 531 of 32,000 at 410m | 1b; argmax
0 | 0 and 13 | 19 of 500); 2c's probe records (margin 0, degenerate
best site, at both sizes for both rungs); the 2c/2b activation files
for the rungs' probe items at both sizes, trained and untrained twin,
on disk and sha-pinned. **Derivable but not computed:** the
label-match rates of the committed draws and continuations under §3's
label functions. This doc is committed before they are computed;
what §7 says about them is arithmetic from the known exact counts,
graded in the retrospective. **Genuinely unmeasured:** the probe's
reading on the eval items (the activations do not exist yet) — the
one quantity in the design that is neither known nor derivable.

## 3. The label — one per rung, readable by every instrument

A label function L maps an answer (or an emitted string) to a class:

- **sub3_mid:** the middle digit of the zero-padded three-digit
  difference — 2b/2c's probe label verbatim (10 classes).
- **arith_next (dial a):** (i) the LAST digit of the next term (10
  classes; new; the kind of feature a residual-stream probe can
  plausibly read linearly, and the kind a partially competent model
  gets right before the whole number) — recommended primary; (ii)
  2c's (a + 4d) mod 7 (7 classes; the committed label) — printed in
  full as the secondary.

Emission scoring: 2c's `number` normalization (the first digit run of
the continuation) → L. A continuation with no digit run, or with a
digit run outside the label's domain (sub3_mid: 1–3 digits;
arith_next: any non-negative integer), scores MISS. Total on every
string; the answer side is the committed answer. Exact-match under
the same parse is the known-answer gate (§4).

Floor per (rung, L): c = max(majority class share over the 500 eval
answers, 1/K) — 2d's rule, the same c for all three instruments. The
bar: one-sided exact binomial, α = .01, and the rate above c (2d's
`binomial_bar`, imported).

## 4. Referents

- 2d's main and pilot draws files and records for the four cells, by
  sha (2e's manifest entries, reused); the re-parse must reproduce
  2d's exact-match tallies exactly (35 | 34, 831 | 531; pilot counts
  as committed).
- 2d's four argmax records, by sha; exact-match 0 | 0, 13 | 19
  reproduced.
- 2c/2b probe-item activation files for the two rungs × two sizes ×
  {trained, untrained seed 0}, by the shas in
  `activations_sha256.txt`; **probe-machinery known-answer gate:**
  2b's `probe_starved` on those files under 2c's committed split
  parameters reproduces the committed m3 records for the rungs
  (accuracy, null mean, corrected p) exactly — probing is
  deterministic (1b's finding).
- The 34 item files' shas (2d's pins); 2b's model shas; the untrained
  twin's seed (0).
- The essay's ladder sentence, quoted in the doc so the licence is
  unambiguous (§6).

## 5. Instruments — same weights, same items, same label

All three read Pythia 410m and 1b (2b's pinned shas) on the rung's
500 eval items.

**Probe (the new measurement).** Activations at 2c's candidate family
(every third layer + final, × 2 positions: question end and prompt
end; 18 sites at 410m, 14 at 1b), collected for the 500 eval items on
the trained model AND its untrained twin (2b's `load_pythia(untrained=
True, seed=0)`), fp16 as 2b. Probe = StandardScaler + logistic
regression (C = 1, max_iter = 100, 2b's machinery), **trained on all
of the rung's committed probe items** (2,000 / 1,000, activations on
disk), **evaluated on the 500 eval items**. Detection at a site:
eval accuracy clears c by the bar; the site family Bonferroni-
corrected (2c's convention; the best site reported). **Twin
control (2/2b's lesson, 1b's correction):** the same procedure on
the twin's activations; a cell is VOID if the twin detects at the
trained model's best site, and the trained reading must exceed the
twin's at that site. Printed beside it: 2c's committed starved
margins; a probe-item cross-validated reading (random split over the
probe items, twin-controlled) as the higher-n "presence in the
population" secondary (dial b).

**Sampling (committed bytes).** Label-match rate over 2d's 32,000
main draws per cell (seed 0, T = 1, untruncated) against c by the
bar; the pilot tier (seed 1000, 4,000) as the replication.

**Argmax (committed bytes).** Label-match accuracy over 2d's 500
committed fp16 greedy continuations per cell against c by the bar.

## 6. Per-cell pattern and verdict tree

Four cells (2 rungs × 2 sizes), each D = (D_probe, D_samp, D_arg) ∈
{0,1}³. **Monotone** (ladder-consistent) iff D_arg ≤ D_samp ≤ D_probe.

1. **INSUFFICIENT_DATA** — any pinned referent fails; any known-answer
   gate fails; or both `arith_next` cells VOID (twin detection).
2. **INVERTED** — at least one non-void cell violates monotonicity
   (a sampler or argmax detection without a probe detection; or an
   argmax detection without a sampler detection).
3. **LADDER** — every non-void cell monotone AND at least one
   detection somewhere.
4. **SILENT** — every non-void cell is (0, 0, 0).

Precedence as listed. Sensitivities (printed, non-gating): label (ii)
for `arith_next` through the whole tree; the pilot tier for the
sampling rung; α = .05 uncorrected; the full per-site probe table
(trained and twin); label-match under the majority share alone as c.

**What each licenses.** *LADDER:* the essay's "probes see deepest …
argmax last" stands on a second task class (arithmetic), and 2c's
silence on these rungs is attributed to its targets — a probe label
chosen for starving can be linearly unreadable, and a basis-starved
validation set measures generalization, not presence (a methods
note, Michael's call). *INVERTED:* the ladder is reversal's, not the
instruments'; the essay's instrument-ladder paragraph is demoted to
"on reversal", and the discriminator's ordering clause is withdrawn
as general — a real loss, stated as one. *SILENT:* 2d's "not silent"
was at guessing level under a matched criterion; 2d's "the probe's
silence was the probe" is retracted; no anomaly.

## 7. Power, and the region this design cannot see

The three bars are not equally sharp, and the asymmetry runs one way.
At 32,000 draws the sampler detects an excess over c = .10 of about
+.004; at 500 items argmax needs about +.035; the probe at 500 items
with Bonferroni over 14–18 sites needs about +.045. **The probe has
the highest bar of the three** — so a true small probe reading with a
true small sampler reading lands INVERTED. Declared: the blind region
is probe accuracy in (c, c + .045); a reading there is "not detected
at this resolution", and the verdict record carries the probe's best
accuracy and CP95 so the reader sees where it sat.

What the known counts say in advance (graded later): under label (i)
for `arith_next`, the sampler's label-match rate is at least the
exact-match rate plus chance on the rest — ≈ .026 + .974 × c at 410m
— which clears c = .10 by the bar at 32,000 draws trivially, and more
if the model gets last digits right without getting the number right;
argmax at 1b (.038 exact) lands near .135, at the edge of its bar; for
`sub3_mid` the exact rate (.001) is at the level of guessing a
plausible three-digit number, so its sampling rung likely reads 0 and
the rung acts as the all-silent control. The test is carried by
`arith_next`, and its unknown is the probe.

## 8. What the dumbest baseline achieves

A majority-label emitter scores exactly c on all three instruments:
(0, 0, 0). A token-identity probe (reading the question's last token)
reads the same on the twin and voids the cell. A probe that overfits
the probe items scores at chance on the eval items.

## 9. Model contact

Activation collection for the 500 eval items: 2 rungs × 2 sizes ×
{trained, twin} = 4,000 forward passes, 2b's collector, fp16, two
positions — minutes on the Mac. No sampling; no eval-size model. The
probe-item activations are the committed 2b/2c files on disk.

## 10. Dials — RULED 2026-08-22 (a–f as recommended)

a. **arith_next label — RULED (i).** Last digit (i; recommended primary) vs 2c's
   mod-7 residue (ii; printed). Recommend (i) primary, (ii) in full
   as the secondary.
b. **Probe primary — RULED eval-item.** Eval-item probe (n = 500, item-matched,
   recommended) vs probe-item cross-validation (n = 1,000–2,000,
   higher power, not the items the generators are scored on).
   Recommend eval-item, CV printed.
c. **Void rule — RULED void.** Twin detects at the trained best site → cell VOID
   (recommended) vs → INSUFFICIENT_DATA outright.
d. **Bonferroni over the site family — RULED.** (2c's convention; recommended)
   vs the single prompt-end site.
e. **INVERTED includes argmax-without-sampler — RULED yes.** (recommended — the
   bottom of the ladder was established in 3b/3) vs sampler-without-
   probe only.
f. **Licences as written in §6 — RULED yes.**

## 11. Process

Three sessions: this doc; build (the label scorer with its totality
fuzz, the activation collector for eval items, the probe fit with the
2c machinery known-answer gate, the committed-bytes rungs with their
exact-match gates, the tree, fixtures, full-shape worlds, mutation
battery, referent manifest); adversarial freeze → tag
`exp2f-preregistered`; the activation collection on Michael's word
(model contact); projection sealed; the analyzer once → `exp2f-closed`.
Nothing computes a label-match rate on committed bytes before the
tag.
