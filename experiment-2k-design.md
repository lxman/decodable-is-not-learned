# Experiment 2k — Design Doc: The Density Question — Does the Cross-Family Predictor Clear Its Bar at Four Times the Draw Budget?

**Status: session 1 (design) written 2026-08-28, at Exp 2j's
close-out, on Michael's word ("Design approach B"). §10 DIALS a–j
AWAIT HIS RULING; nothing is built, nothing is sampled.** Model
contact, when sanctioned: Pythia-1b (and, dial c, Pythia-410m)
SAMPLING ONLY on nine rungs — the same weights, harness, sampler and
stream namespace as Experiment 2d's main tier, with three new seeds
beside the committed one. No eval-side model is loaded, no OLMo
weight is touched: the outcome is Experiment 2i's committed 7B
sweep, on disk since 2026-08-28.

Approach B is the follow-up 2j's §6 named under its A-1 DENSITY
reading: "x_A at k = 256 on R_CAP against the known OLMo outcome,
with 2d's caveat". Approach C (the OLMo-2 13B sealed outcome) is the
other, and §6 says which of 2k's worlds hands off to it.

## 1. The question

**Does Pythia-1b's sampled count per item at k = 256 — four 64-draw
blocks: Experiment 2d's committed seed-0 block, regenerated on the
production path as gate 1, plus seeds 1, 2 and 3 — forecast the
committed order in which OLMo-2 7B's stage-1 training made 2c's
items emittable, above 2i's bar (T ≥ .10, p < .01) on 2i's nine
rungs and 2g's strata? That is: was 2i's sub-bar cross-family
reading, T_A = .0949, a thin-predictor effect?**

One preregistered test, 2i's Test A verbatim with the predictor at
256 draws instead of 64:

- **Primary.** x_A^(256) = per-item verified count over 256 pure
  T = 1.0 draws from Pythia-1b, on R_CAP (2i's nine rungs), in 2g's
  strata; mean over rungs of within-stratum Somers' D against y = 2i's
  per-item count over the 21-point 7B grid; permutation within rung ×
  stratum, 10,000, seed 0; fires iff T ≥ .10 and p < .01.

Worlds (after INSUFFICIENT_DATA):

- **DENSITY** — the primary fires. The cross-family predictor clears
  its bar at four times the budget: 2i's shortfall was, at least in
  part, predictor information density, as A-1 read it. §6 says what
  this licenses and, more carefully, what it does not — the outcome
  was known.
- **NOT-DENSITY** — the primary does not fire, annotated `structured`
  (p < .01, T < .10: real, still under the bar) or `null` (p ≥ .01).
  Four times the draws did not buy the bar; whatever limits the
  cross-family reading is not density at this budget.

The named secondaries (§5.2) are where the experiment's information
mostly lives, and §2 says why: the verdict-level outcome is largely
foreseeable from 2j's committed ladder, and the design says so before
a draw is taken.

## 2. What is known, and what this experiment therefore cannot be

**Known, to the designer and to anyone who opens the record:**

- **The outcome.** 2i's 7B stage-1 sweep — per-item bits at 21 grid
  points on all 34 rungs, y_i the count of points at which item i
  verifies — is committed under `exp2i-closed`. This is 2d's and 2e's
  situation, not 2g's or 2i's: **2k tests a zero-free-parameter
  predictor fixed before sampling against an outcome that is already
  on disk.** It is not a sealed forecast. A DENSITY verdict licenses
  "the cross-family predictor clears its preregistered bar at 256
  draws on 2i's outcome"; it does not license "Prediction 2 supported
  across families", which stays reserved for a sealed-outcome
  experiment (approach C).
- **x_A^(64) and its reading.** T_A = .0949 (p 1.0e-4), per rung
  sub_base8 .338, add_base8 .242, antonym6 .101, odd6 .078, arith_next
  .064, antonym .028, sub3_mid .020, add3_mid .005, sub4_mid −.022; the
  six 2h-carried rungs alone .1418; the 410m cross replication .1154.
  The predictor is 2d's seed-0 block; x_B^(64) reads the same outcome
  at .2204.
- **The ladder.** 2j's A-1 thinned x_A by prefix inside the committed
  seed-0 block and read the OLMo outcome at every k:

      k        1      2      4      8     16     32     64
      T_A   .0071  .0125  .0211  .0334  .0491  .0701  .0949
      T_B   .0495  .0775  .1104  .1451  .1764  .2025  .2204

  x_A's increments per doubling are .005, .009, .012, .016, .021,
  .025 — still growing at 64, where x_B's are shrinking (.035, .031,
  .026, .018). Two naive continuations of x_A's curve: at the last
  increment, 128 ≈ .120 and 256 ≈ .145; at x_B's saturating shape
  shifted to x_A's exchange rate (x_A at 64 sits between x_B at 2 and
  at 4), 256 ≈ x_B at 12–16 ≈ .16–.18. Either way the bar is expected
  to clear. **So the verdict-level projection is worth little, and
  this doc says so now, before the tag, so that a DENSITY verdict is
  not mistaken for foresight** (2j's lesson: on known inputs, project
  the texture and grade it as the test). The bar at the boundary cuts
  the other way too: .0949 is .005 under .10, and no one has ever
  measured how far T_A moves from one 64-draw block to the next — the
  permutation null's SD (.0094) is a different quantity. Secondary S1
  measures it for the first time, with three fresh blocks.
- **What density matching means at 256.** A-1's rate rule, k_g =
  clip(round(64 · r̄_sparser / r̄_denser), 1, 64), matched x_B DOWN to
  x_A's verified-draw density at 7–57 draws per rung. Read the other
  way with x_A at 256: x_A's expected verified draws per item match
  x_B's 64-draw count at k_g = clip(round(256 · r̄_A / r̄_B), 1, 64) =
  add_base8 28, arith_next 37, sub_base8 45, add3_mid 27, and the cap
  (64) on antonym, antonym6, odd6 and sub3_mid; sub4_mid is the one
  rung where Pythia-1b is already the denser. So at 256 Pythia-1b's
  count is at OLMo-1B's 64-draw density on four rungs and at 42–70 %
  of it on the arithmetic rungs where 2i's asymmetry lived. 256 is
  the named budget, not full matching (dial a).
- The 2c battery, 2d's records and floors, 2g's strata, 2h's and 2g's
  outcomes (for S5), 2i's and 2j's verdict records: all frozen and
  public.

**Not known to anyone:** a single draw from seeds 1, 2 or 3 on any of
these cells. The sampler is a pure function of (cell, seed, item) and
nobody has evaluated it there (§4 verifies the seeds are fresh against
every committed stream map).

**Pre-tag disclosure rule (checklist item 27, 2j's slip c):** any
execution of 2k's analyzer on the real tree before the tag — a read
sweep, a determinism check, a smoke run — prints numbers, and every
number so printed is logged HERE before the tag is cut. At the time
of writing the analyzer does not exist. The comparison gate (§3.3)
necessarily reproduces 2i's .0949 pre-tag; that number is already
public and is listed above.

**Model contact is predictor-side only.** The outcome side is not
touched, so nothing in 2k can leak the outcome into the predictor
except through the designer's knowledge of it, and every design
choice here — the rung set, strata, statistic, bar, k, seeds — is
either 2i's verbatim or fixed by a rule stated in this doc.

## 3. Instrument — 2i's Test A, with 2d's sampling tier at four seeds

Everything not named here is imported frozen: 2c's harness (2-shot
prompts, `MAX_NEW_TOKENS` by answer type — 8 on the arithmetic rungs,
12 on the word rungs — 2c's normalizer, exact match under 3c's total
wrapper); exp3's sampler (`sample_item`, the stream formula
sha256("exp3|rung|size|mode|s{seed}|i{item}") masked to 63 bits, chunk
rows 16, fixed per-step consumption so every seed's stream is a pure
function of (cell, seed, item)); 2d's main-tier protocol (fp32,
CPU-float32 softmax, T = 1.0, no truncation, every raw draw stored,
per-seed tallies beside the draws, `model_sha` of the weights); 2g's
strata and statistics (within-stratum Somers' D, mean over rungs,
permutation within rung × stratum, 10,000, seed 0; 1,000-resample
bootstrap CI per rung; eligibility n_pos ≥ 20 realized); 2i's sweep
loader with its record checks, its rung-set rule and its
cross-beyond-within / composite-strata constructions. The deltas:

### 3.1 The sampling tier `k256`

For each rung in R_CAP and size 1b (410m under dial c): all 500 items
through `sample_item` with `seeds = (0, 1, 2, 3)`, `draws_per_seed =
64`, 2d's dtype and softmax path, 2c's token budget for the rung —
256 draws per item, 128,000 per rung, 1,152,000 per size over the
nine rungs. Records in 2d's row format (`{"item": i, "draws": {"0":
[...], "1": [...], "2": [...], "3": [...]}}`), a per-rung record with
`seeds = [0, 1, 2, 3]`, `draws_per_seed = 64`, `k_total = 256`, the
per-seed tallies, `model_sha`, `items_sha256`, the stream namespace
and the stack.

The seed-0 substream of every cell IS 2d's committed main-tier stream
— same rung, size, mode, seed, item, formula and namespace — so it is
regenerated, not copied (dial b), and that regeneration is gate 1.

### 3.2 Gate 1 — continuous, item by item, on the production path

Before any draw for a rung is taken the runner loads 2d's committed
`results/main/<size>_trained/<rung>.draws.jsonl.gz` and `.json` for
that rung (sha-pinned in §4). After every item's `sample_item`
returns, the runner compares the item's 64 seed-0 draws to the
committed row's 64, byte for byte, and its running seed-0 tally to
the committed per-seed tally at the end of the rung; the first
mismatch writes `<rung>.HALTED` with the item index and both strings
and stops the campaign. Every one of the 288,000 committed seed-0
draws per size is compared — coverage is attested by the runner
(items compared, draws compared) AND re-derived by the analyzer from
the committed 2d files against the sealed 2k draws (2h F-2 / 2i C-1:
attestation is not a check). A halt tree — any `.HALTED` marker, or
a rung whose record is absent or whose draws file is truncated —
delivers INSUFFICIENT_DATA from `run()` by construction (2d F-1),
scanned before any tier loads.

What gate 1 buys: the twelfth byte-identical reproduction on this
stack if it holds, on nine cells never re-derived before (2d's own
gate 1 was the two reversal rungs against exp3); and the guarantee
that the pooled predictor's first block is exactly the predictor 2i
read, so the nested ladder (S2) starts at 2i's number by identity,
not by assumption.

The build proves with a fixture (a fake model with a recorded
generator) that seed 0's bytes do not depend on which other seeds are
in the same `sample_item` call — the per-seed generator independence
the sampler's docstring asserts — so that gate 1 is a statement about
the stream formula and the weights, not about call shape. If that
fixture cannot be made to pass, the tier runs seed 0 in its own call
and seeds 1–3 in a second, which is then the production shape
(disclosed in the build ledger).

### 3.3 The predictor, the comparison gate and the nested ladder

x_A^(k) for k ∈ {64, 128, 192, 256} = per-item verified count over
the first k/64 seeds in seed order (0; 0–1; 0–2; 0–3), re-derived by
the analyzer from the raw draws through 3c's total verify wrapper —
never read from a tally; the per-seed tallies are cross-checked
against the re-derivation and a mismatch refuses.

**Comparison gate (known-answer, exact):** x_A^(64) from the sealed
2k draws, through 2k's Test-A code path, must reproduce 2i's
committed primary EXACTLY — T = 0.09491251078607414 and every
per-rung D — from 2i's `verdict.json` (pinned literal AND file), and
the same from 2d's committed files directly. As 2e reproduced 2d's
.5455 and 2j reproduced 2i's .2204: the reproduction of the
predecessor's primary is the proof that the statistic, strata, rung
set and outcome loader are the predecessor's.

### 3.4 Rung set, strata, outcome — none of them new

R_CAP = 2i's nine (add3_mid, add_base8, antonym, antonym6, arith_next,
odd6, sub3_mid, sub4_mid, sub_base8), read from 2i's committed
`rung_set` record AND re-derived by 2i's rule from 2i's endpoint
records (a mismatch refuses). Strata = 2g's committed table. Outcome
= 2i's sweep records through 2i's loader with every one of its
record checks live (`model_sha`, coverage 500, bits re-verified from
continuations). Predictor degeneracy: x_A^(256) has strictly more
live items than x_A^(64), which was non-degenerate on every rung in
2i; the undefined branch is retained in code and unreachable on this
data, stated as such.

### 3.5 The tree

INSUFFICIENT_DATA (any collected refusal: halt tree, missing or
truncated tier, seeds ≠ [0,1,2,3], `draws_per_seed` ≠ 64, `model_sha`
≠ 2d's committed value for the size — the same weights are required,
not merely the same repo — `items_sha256` ≠ 2c's, tally ≠
re-derivation, comparison gate inexact, rung set or strata or outcome
pin failure, any frozen-module or import-surface pin failure, power
record absent or its predictor sha ≠ the sealed draws') → DENSITY →
NOT-DENSITY (`structured` / `null`). Refusals are COLLECTED, never
raised (2h F-1); every tree the runner can leave has been enumerated
at the freeze and reaches a terminal.

### 3.6 Pins

`FROZEN_SHA256_2K` over every module 2k names (2i's list extended);
`IMPORTED_SHA256_2K` over the resolved module table under
`experiments/` at `run()`'s entry and exit (the eleventh lesson, from
the start rather than from the freeze); a referent manifest over every
file read (§4); blob-bound tags: `exp2k-preregistered` binds the
analyzer, the runner and the tier module; `exp2k-predictor-sealed`
binds the eighteen (or nine) new draw files and records, the seal
record and the power record. A post-tag edit to any bound blob makes
every runner and the analyzer refuse until a re-tag (2h F-3), and a
re-tag is disclosed as 2i's was.

## 4. Referents — every input a committed value

| input | value / rule | where |
|---|---|---|
| outcome y (7B grid counts, 21 points, 34 rungs) | 2i's sweep records, re-verified through 2i's loader | `experiments/exp2i/results/sweep/…` (tag `exp2i-closed`) |
| 2i's primary (comparison gate) | T_A = 0.09491251078607414, per-rung D as committed | `experiments/exp2i/results/verdict.json` |
| 2i's rung set R_CAP | nine rungs; re-derived from the endpoint records by 2i's rule | `experiments/exp2i/results/endpoint/…` |
| 2i's x_B (S3, S4) | the sealed OLMo-2 1B counts, re-derived from the raw draws through 2i's provenance checks | `experiments/exp2i/results/predictor/olmo1b/*` (tag `exp2i-predictor-sealed`) |
| 2d's seed-0 block (gate 1; the first ladder rung) | `main/1b_trained/<rung>.{json,draws.jsonl.gz}` for the nine rungs (410m likewise under dial c); `model_sha` per size | `experiments/exp2d/results/main/…` (tag `exp2d-closed`) |
| 2j's ladder and A-1 anchors (S3) | T_A / T_B at k = 1…64 on the OLMo outcome; x_B thinned matched .1571; rates r̄_A, r̄_B per rung | `experiments/exp2j/results/verdict.json` (tag `exp2j-closed`) |
| 2g's strata; 2g's and 2h's outcomes (S5) | committed tables | `experiments/exp2g/…`, `experiments/exp2h/…` |
| 2c items, shots, verify | frozen | `experiments/exp2c/…` |
| the stream formula and namespace | exp3's, `stream_map.json`; 2d's `stream_map_2d.json` | `experiments/exp3/`, `experiments/exp2d/` |
| seed freshness | seeds 1–3 on (rung ∈ R_CAP, size ∈ {1b, 410m}, mode trained) coincide with NO committed stream: 2d main = seed 0, 2d pilot = seed 1000, exp3/3c/3d/3e = reversal rungs only; the build checks the tuple against every committed stream map and refuses on a hit (2d dial l's precedent) | this doc + build |

Every file above is sha-pinned in `referents_2k.json`; every literal
above is a pinned constant; `verify_referents_2k.py` checks them cold
and is deliberately short of any predictor-vs-outcome statistic.

## 5. Operationalization

### 5.1 The primary

Test A at k = 256 on R_CAP, 2g's strata, exactly §1. Fires iff
T ≥ .10 and p < .01. The bar is 2i's, unchanged (dial d) — moving it
would make 2k a different question.

### 5.2 Named secondaries (printed in every world; no α claim)

- **S1 — block replication.** T_A on each seed alone (0, 1, 2, 3):
  four independent 64-draw predictors on the same outcome; seed 0
  equals 2i's .0949 by the comparison gate. Printed: the four values,
  their mean, min, max and SD, per rung too. This is the first
  measurement of the sampler-noise SD of T_A at k = 64. Reading: if
  the block SD is not small against the .005 bar gap, 2i's
  fires = False was inside sampler noise, and that is said plainly.
- **S2 — the nested ladder.** T_A at k = 64, 128, 192, 256, nested in
  seed order, against 2j's prefix-thinned ladder at 1…64 (which S2's
  first point equals by identity). Whether the increments keep
  growing, flatten or turn.
- **S3 — the matched comparison, at high density.** x_B thinned by
  2j's block rule to k_g = clip(round(256 · r̄_A / r̄_B), 1, 64) per
  rung (values in §2, re-derived by the build), T per block, mean over
  blocks, min and max printed — against x_A^(256) on the same outcome
  and strata. 2j's A-1 measured the lineage increment at LOW density
  (.1571 − .0949 = .062 with x_B thinned to x_A's 64-draw density);
  S3 measures it at x_A's 256-draw density. Also printed: x_A^(256)'s
  placement on 2j's x_B ladder (the OLMo-1B-draw equivalent of 256
  Pythia-1b draws, by linear interpolation in log k).
- **S4 — the 2i partials at 256.** Cross-beyond-within (x_A^(256) in
  2i's composite strata of x_B's median bucket; 2i's .0701) and
  within-beyond-cross (x_B in composite strata conditioning on
  x_A^(256)'s zero cut — a different partition from 2i's, since the
  256-draw zero set is smaller; 2i's .2153 printed beside it).
- **S5 — within-lineage forward density.** x_A^(256) → 2g's committed
  2.8b outcome (seven rungs) and 2h's committed 6.9b outcome (eight
  rungs), 2j's ladder read forward: .1672 and .2179 at 64 → ? at
  256. Outcomes known; descriptive.
- **S6 — 410m** (dial c): S1–S5 at 410m; 2i's 410m cross .1154.
- **S7 — texture.** The six 2h-carried rungs' mean (2i: .1418); the
  three mid-digit rungs' live-item counts at 64 and 256 (2i: 10, 31,
  13 of 500); first-correct outcome (2i: .1127); per-rung D with CI.

### 5.3 Sensitivities (printed, non-gating)

Zero-fraction density matching for S3 (2j's alternative rule); the
first-correct outcome as the primary's y; the primary over the six
carried rungs alone.

## 6. Verdict tree, and what each world licenses

INSUFFICIENT_DATA → DENSITY → NOT-DENSITY, mechanical, §3.5.

**DENSITY licenses:** the essay's "the cross-family sentence stays
unlicensed" clause gains its qualification — "at four times the draw
budget Pythia-1b's counts clear the same bar on the same outcome
(T = …) — an outcome that was already on disk, so a bar cleared, not
a forecast made" — with §2's disclosure attached verbatim; the
scoreboard's "stopped short of its preregistered bar at .095" gains
"and clears it at 256 draws"; Prediction 2's "a lineage instrument,
not a general one" becomes "a lineage instrument at 64 draws; at 256,
cross-family on a known outcome — the sealed cross-family test is the
next experiment". The named next experiment is approach C with the
predictor at 256 draws, since 64 is now known to be too thin for the
cross-family reading. What DENSITY does NOT license: "Prediction 2
supported across families" (no sealed outcome); any sentence about
mechanism (S3's increment is descriptive).

**NOT-DENSITY licenses:** the essay's lineage wording stands unchanged
and gains one sentence — the cross-family shortfall is not predictor
density at four times the budget (the 2j ladder's extrapolation
failed, and S2 says where); under `null`, the sub-bar structure 2i
reported did not replicate at 256 and that is said. Approach C's
design then needs a different reason to expect a cross-family
forecast, and the honest next step is the mechanism question on the
cross-family gap rather than a bigger outcome model.

**Any world:** S1–S7 in full. If S1's block SD ≥ .005, the record says
2i's bar decision was inside sampler noise — in either direction.

## 7. Power — a claim about the instrument, not foresight

Written ONCE at the sealed stage (after the draws, before the
projection and the analyzer), with 2i's machinery over the REAL
x_A^(256): y generated from a latent mixing rank(x) at calibrated
strength inside 2g's strata, every simulated cell through the
verdict's own tree; P(fires | D = .15) ≥ .75 is the bar, else
DECLARED UNDERPOWERED IN ADVANCE; P(fires | D = .10) printed as the
coin-flip statement (2i: .44 at 64 draws — the bar decides, not p).
2i's shape note carried verbatim: the alternative is item-level rank
concordance inside sealed strata; nothing here transfers to a
class-level effect. Calibration: one test at α .01 for its p
component; the T ≥ .10 component is an effect-size rule and carries
no α; the two worlds are a partition, so no union caveat arises; the
`structured` / `null` annotation is descriptive. The power record is
pinned by the seal tag; the analyzer refuses if its predictor sha is
not the sealed draws' (2j F-2's lineage).

## 8. What the dumbest baseline achieves

x_A^(64) is the baseline and its number is known: .0949. The dumbest
forecast of x_A^(256) is 2j's ladder continued, .145–.18; a predictor
that adds three blocks of pure noise to seed 0 would sit at .0949 ±
S1's block SD. 2k's information is the distance between those two.

## 9. What 2k does not claim

Not a sealed forecast (§2, 2d's caveat, carried into every licensed
sentence). Not full density matching (256 reaches OLMo-1B's 64-draw
verified density on four rungs and 42–70 % of it on the arithmetic
rungs). Not a mechanism result: S3's high-density lineage increment
is descriptive. Not a statement about a third family. Not "Prediction
2 supported cross-family" under any world.

## 10. Dials — for Michael's ruling

- **a. Draw budget.** k = 256 (four blocks) as named, ≈ 6.5 h at 1b
  by 2d's measured rate (366 min for 34 rungs × 32,000 draws → 10.8
  min per block-rung, an upper bound: the nine rungs carry the
  battery's shortest token budgets), **recommended**; k = 512 (eight
  blocks, ≈ 13 h) reaches full matching on the arithmetic rungs but
  doubles the night and S2 will say whether 512 is worth a successor.
- **b. Seed 0 regenerated as the continuous gate 1** (every committed
  seed-0 draw compared item by item on the production path; the
  pooled predictor's first block is 2i's by identity; +25 % of the
  tier), **recommended**; the alternative pools seeds 1–3 with 2d's
  committed files and gates one rung.
- **c. 410m.** Run the same tier at 410m as a non-gating replicate
  (S6), ≈ 4.6 h after the 1b tier, **recommended** — the 410m cross
  read ABOVE 1b at 64 (.1154 vs .0949), so which size is the better
  cross-family predictor is a live question and one more point is
  cheap; the alternative is 1b only (≈ 6.5 h total).
- **d. Primary and bar.** 2i's Test A at 256, T ≥ .10 / α .01
  unchanged, worlds DENSITY / NOT-DENSITY with the `structured` /
  `null` annotation, **recommended**.
- **e. Secondaries S1–S7** all printed, S3 under the 256-scaled rate
  rule with 2j's block machinery, **recommended**.
- **f. Projection**, sealed before the tier runs: texture-first — per-
  rung D at 256 (named calls: add_base8 and arith_next gain the most,
  the three mid-digit rungs stay ≈ 0, sub_base8 stays on top), S1's
  block SD (a range), S3's increment sign, S5's two values; the
  verdict-level call stated as expected-from-the-ladder and worth
  little; named disconfirmer T_A^(256) < .10. Graded in the
  retrospective as the test of foresight.
- **g. Run order.** 1b first (the primary), 410m second; within a size
  the rungs in R_CAP's alphabetical order — no reversal rung is in
  R_CAP, so there is no exp3 gate-1 cell to front-load; gate 1 is
  continuous on every rung.
- **h. Tags.** `exp2k-preregistered` (blob-bound: analyzer, runner,
  tier module) → the tier on Michael's word → `exp2k-predictor-sealed`
  (draws, records, seal, power) → projection → analyzer once →
  `exp2k-closed`. One pre-committed change.
- **i. Pre-tag rehearsal** (checklist item 24, the tenth lesson): the
  only path element new to this stack is `seeds = (0, 1, 2, 3)` with
  the item-level comparator — rehearse it on ONE item of ONE rung at
  1b (256 draws, ≈ 1 min), the seed-0 block required identical to the
  committed row, the output kept in the ledger and nowhere the
  analyzer reads, on his word; **recommended**. The sampler, weights
  and harness are otherwise 2d's exact production path.
- **j. Build + freeze in one session** by SDD (fresh implementers,
  reviewed tasks, an adversarial freeze by a fresh reviewer), the
  import pin from the first commit; licences as §6.

## 11. Process

Design (this doc) → rulings → build (`experiments/exp2k/`: tier
runner with the continuous gate 1 and the halt marker, the analyzer
with the tree and S1–S7, power, referents, `verify_referents_2k.py`,
fixtures, worlds for every terminal, mutation deltas) → adversarial
freeze → tag → rehearsal on his word → the 1b tier, then 410m,
detached (nohup + disown, a watcher committing each rung's record
after its size stops changing) → seal tag → power once → projection
sealed → analyzer once → `exp2k-closed` → close-out propagation
(essay under §6, `experiments.md`, the supporting repo graft, Zenodo
v1.14, paper inventory).

Compute: the Mac (Pythia-1b fp32 ≈ 4 GB, cached; 410m cached); disk
negligible (2d's whole main tier is 14 MB; 2k's is ≈ 4 × nine rungs
≈ 15 MB per size). Nothing else runs.
