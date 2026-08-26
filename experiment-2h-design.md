# Experiment 2h — Design Doc: The Sampler Confirmation — Does Output-Channel Reachability Forecast Emission Order on a Second Sealed Outcome?

**CLOSED 2026-08-25: VERDICT CONFIRMED** (tag `exp2h-closed`; analyzer run once on Michael's go) — stratified T .2020, p 1.0e-4, POWERED .979; probe competitor NOT-CONFIRMED (−.0187), probe-beyond-sampler null, sampler-beyond-probe .2030; 410m replication .1417 CONFIRMED; gate 1 exact through both loader paths, 23/23 grid points, zero halts; projection 3a450cd8 HIT. See `experiments/exp2h/results/VERDICT.txt` and `retrospective.md`. The doc below stays frozen as the preregistration record.

**Status: session 1 (design) written 2026-08-24, at Exp 2g's closeout,
on Michael's word ("run #1 — the sampler confirmation on 6.9b"); §8
dials RULED the same day (full 34-rung sweep; the rest as recommended). Build and adversarial freeze follow; the ONLY
model contact is the 6.9b checkpoint sweep, after the tag — there is
no stage 1: every predictor in this experiment was committed to the
repository before any intermediate checkpoint of any Pythia size had
ever been queried.**

Lineage: 2g (NO-FORECAST; its preregistered non-gating sampler
competitor fired at T .1672, p 1.0e-4). A finding that arrives as a
secondary is not established until it survives as a preregistered
PRIMARY on an outcome nobody has seen (the 3d → 3e rule). 6.9b's 155
intermediate checkpoints have never been queried by anyone.

## 1. The question

**Does the per-item sampled rate at 1b — 2d's committed 64
temperature-1.0 draws per item, on disk since 2026-08-22 — forecast
the order in which 6.9b's training makes 2c's rising items emittable,
within each rung's structural difficulty strata, as it did for 2.8b's?**

CONFIRMED here plus 2g's record makes "at item grain, emergence order
is output-channel reachability" a finding at the standing of the
reversal case: two sealed outcomes, two resolution steps (1b→2.8b in
2g; 1b→6.9b here), one committed predictor. NOT-CONFIRMED demotes 2g's
secondary to exploratory, and the essay says so.

## 2. What is known and what is sealed (disclosure)

Known: everything 2g knew, PLUS 2g's entire verdict — including the
sampler's per-rung concordances at 2.8b. The DESIGN is therefore
informed by the finding it tests; the OUTCOME is not: no quantity from
any 6.9b intermediate checkpoint exists anywhere. The predictor is
not merely sealed but historically prior: committed at 2d's close,
two experiments before any checkpoint sweep was designed. The probe
competitor is 2g's sealed table (tag `exp2g-predictor-sealed`),
likewise prior to every checkpoint query. m4's 6.9b FINAL counts are
known (they fix R_6.9b below); every intermediate step is not.

## 3. Instrument — 2g's, with three deltas

Everything not named here is `experiments/exp2g`'s machinery,
imported frozen (battery, labels, strata, stats, checkpoints loader
with the candidate rule, runner shape, analyzer shape, referent
discipline). The deltas:

1. **The primary predictor is the sampled count.** x_i = 2d's
   committed per-item verified count at 1b (main tier, seed 0, 64
   draws; `experiments/exp2d/results/main/1b_trained/*.draws.jsonl.gz`,
   re-verified through 3c's total wrapper as in 2g's
   `sampler_counts_1b`). 410m (same files) is the replication size.
   The probe (2g's sealed per-item scores, sha 9eadbac3…) is the
   NAMED COMPETITOR, printed with the same statistic, plus
   probe-beyond-sampler and sampler-beyond-probe partial concordances.
2. **The outcome is 6.9b's grid.** Same shape as 2g at 2.8b: step0 +
   22 trained points (1k, 2k, 4k, 8k, 10k, 16k, 20k, 30k, 32k, 40k,
   50k, 60k, 64k, 70k, 80k, 90k, 100k, 110k, 120k, 130k, 140k, final).
   The 2026-08-24 Hub scan: 6.9b is the cleanest size — every step
   branch two unique bin shards, zero stale-main copies, step143000
   byte-identical to main, step64000 unique (no exclusion). ("Zero
   stale-main copies" is read off a counter of SINGLE-FILE copies;
   6.9b publishes sharded weights, so that counter is structurally
   zero and descriptive only. What refuses a stale copy of the final
   weights published under a step label is the duplicate-signature
   rule, which rejects any grid step whose candidate files match
   another revision's — demonstrated at the freeze on a synthetic
   inventory.) Final
   point = 2c's pinned `main`; gate 1 = 2g's two-loader gate at 6.9b
   (2c's loader must reproduce m4's committed 6.9b counts exactly;
   2g's checkpoint loader must match its tensor digest with byte-
   identical continuations). Gate 1 also attests the COVERAGE of that
   comparison — how many continuation pairs were compared on each
   rung — and the frozen verdict requires the full 500 on all 34: a
   zero diff count over a truncated comparison is not evidence (3d's
   coverage lesson).
3. **The tree has no SURFACE terminal.** The untrained twin's sampled
   counts are all-zero (exp3's twin referent: 0 verified in 576,000),
   so a twin-predictor arm is vacuous by construction — disclosed,
   not silently dropped. Tree: INSUFFICIENT_DATA → **CONFIRMED**
   (p_strat < .01 AND T ≥ .10) → **NOT-CONFIRMED** (everything else;
   "detected below the effect bar" and "inverted" named inside, as
   2g). α, the effect bar, the within-rung × stratum permutation
   (10,000, seed 0), eligibility (n_pos ≥ 20 realized), and the
   count outcome with first-correct printed are 2g's unchanged.
   Every tree the runner can leave — halted at gate 1, killed
   mid-step, a torn or non-dict record, a directory where a file
   belongs — reaches INSUFFICIENT_DATA through the frozen verdict
   rather than raising; so does a sweep on which no rung clears the
   eligibility floor, or on which the outcome is constant within
   every stratum. Demonstrated at the freeze over 32 tree shapes,
   nine of which raised before the closure; the refusal carries its
   reason verbatim.

## 4. Rung set and power

**R_6.9b** — the rungs whose committed m4 6.9b count clears 2d's bar:
antonym 286, antonym6 143, odd6 107, count_div13 102, arith_next 58,
sub_base8 52, add_base8 29, add3_mid 19 — **eight rungs**, all inside
the predictor set, two of them (count_div13, odd6) never used by 2g's
2.8b primary. add3_mid's final count sits under the 20-item
eligibility floor; 2g measured ever-verifies at ≈ 2× final on every
rung (82 vs 43 for add3_mid at 2.8b), so it is expected eligible on
the realized y and the bound is disclosed. Strata: 2g's committed
table (all eight rungs are in it). Power: 2g's simulation machinery
re-run over R_6.9b's n_pos bounds; the observed 2.8b effect was
T .167, and with eight rungs the bar is expected comfortably cleared
at D = .15 — the record is printed once before the tag, with the
declaration, as always. The power record is written once, before the
tag, and read under two disclosures. It sets each rung's
positive-outcome count to the committed FINAL count — a lower bound
on the realized n_pos, since 2g measured ever-verifies at ≈ 2× final
— and it does not apply the primary's own n_pos ≥ 20 eligibility
gate, so add3_mid is modelled at 19 where the run may drop it as
thin; both directions are conservative for P(CONFIRMED). And .979 is
a claim about the alternative's SHAPE: item-level rank concordance
between the committed sampler count and a monotone emission order
inside the sealed strata. 2g found transient verification pervasive
and trajectories non-monotone; if the truth is class-level or
non-monotone, the number does not transfer.

## 5. What 2h does not claim

- The difficulty-proxy entanglement is not fully separable: a sampled
  rate is both reachability and un-named difficulty. What 2h can
  show is replication on a second sealed resolution step with the
  named difficulty held fixed and the probe conditioned out; the
  proxy reading is disclosed in the verdict either way. One
  exploratory texture is printed: 1b-beyond-410m (partial concordance
  in strata of the 410m count), the closest committed thing to a
  model-specific signal.
- Nothing about 12b's checkpoints (2g's 12b arm stands), nothing
  cross-family, nothing about mechanism.
- CONFIRMED does not resurrect Prediction 2's probe form; the essay's
  claim would be about the output channel, and says so.

## 6. Licences, written in advance

- **CONFIRMED:** the essay's 2g paragraph upgrades "a control I'm glad
  I preregistered" to a two-outcome finding: sampled reachability at
  1b forecasts emission order inside both 2.8b's and 6.9b's training,
  through difficulty strata, with the probe adding nothing on either;
  the OLMo generalization becomes the named next experiment.
- **NOT-CONFIRMED:** 2g's secondary is demoted to exploratory in the
  essay and experiments.md; the output-channel sentence is softened
  to one sealed outcome; the program's next step is Michael's call.
- Any world: the probe competitor, the 410m replication, the
  flat-rung descriptives and step0 are reported in full.

## 7. Run plan and model contact

Design (this doc + rulings) → build (a thin `experiments/exp2h`
importing exp2g frozen: the 6.9b manifest from the committed Hub scan,
R_6.9b, the swapped primary, the tree; fixtures, worlds for every
terminal, referents, mutation deltas) → adversarial freeze (the deltas
attacked; cold batteries re-run) → tag `exp2h-preregistered`
(the tag is the only gate: with no stage-1 seal, both the runner and
the analyzer require not merely that the tag exists but that it
CARRIES this instrument — `analyze_2h.py`, `battery_2h.py` and
`run/sweep_2h.py` byte-identical to the blobs at the tag, or both
refuse; a post-tag edit to any of the three requires a re-tag) →
projection sealed → the 6.9b sweep on Michael's word (gate first;
~60 min per checkpoint at 34 rungs from m4's measured pass, 22 + step0
points, ≈ 288 GB streamed; watcher committing; detached processes per
the reaping gotcha) → analyzer once → `exp2h-closed`. One pre-committed
change. The only model contact is the sweep.

## 8. Dials — RULED by Michael 2026-08-24 ("Full 34 rungs, dials as recommended"): a full 34-rung sweep; b 22 trained points incl. 64000; c 1b primary / 410m replication; d no SURFACE terminal (twin sampled counts zero by construction, disclosed); e n_pos ≥ 20 realized; f licences as §6

a. **Sweep breadth** — all 34 rungs (recommended: the flat-rung
   transient descriptive and symmetry with 2g; ~21–22 h) vs the 11
   predictor rungs (~7 h).
b. **Grid** — 2g's 22-trained-point shape incl. 64000 (recommended;
   6.9b's branch is clean) vs 2g's literal 21 points.
c. **Primary size** — 1b, 410m replication (recommended, 2g's).
d. **Tree without SURFACE** — as §3.3 (recommended) vs keeping a
   vacuous twin arm for symmetry.
e. **Eligibility** — n_pos ≥ 20 realized (recommended, 2g's rule;
   add3_mid's bound disclosed) vs lowering to 10 for add3_mid.
f. **Licences** — as §6.
