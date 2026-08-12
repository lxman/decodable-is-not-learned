# Experiment 1b — Design Doc: The Discriminator, Retested Under a Corrected Criterion

**Status:** **FROZEN 2026-08-12** (tag `exp1b-preregistered`, Michael's
explicit go on the all-GREEN/RULED
`experiments/exp1b/FREEZE_CHECKLIST.md`). The instrument is
`experiments/exp1b/` — `analyze_1b.py`, `run/run_untrained.py`,
`run/campaign_1b.py`, and a 38-test fixture suite. Every open item is
closed or disclosed; the two scope discrepancies were ruled DISCLOSE and
are recorded at §8 step 1 and open item 2.

**The one pre-committed change is SPENT** (§9) on the floor-corrected S1
(§4), for a reason ledgered before the change: the untrained twins were
built and run on all thirty cells before any trained data existed, and
the grokking twins fired raw S1 in 9 of 10. Nothing further may change.

**The verdict projection is on the record before the campaign**
(`experiments/exp1b/PROGRESS.md`): the grokking row is expected to return
roughly 6/10 against an ≥8/10 bar, i.e. **FAIL**, with both lubana rows
expected to pass. Written down so a FAIL cannot later be presented as a
surprise, nor a PASS as expected.

**Disclosed at freeze:** §8 step 1's "one commit" did not hold — the
frozen contents landed across the twenty-four commits of the 1b range
rather than in a single freeze commit, and the tag marks the boundary
instead. Recorded rather than reshaped.

**Predecessor:** `experiment-1-design.md` (tag `exp1-analysis-frozen`,
VERDICT: FAIL). Exp 1b reuses that experiment's task implementations,
training recipes, signature module, and ground-truth gates verbatim.
It is a re-test, not a rebuild.

---

## 1. Hypothesis and logical structure

**Hypothesis.** S1 — probeability below threshold — separates
structure-present systems from structure-absent ones. A linear probe
reads the target from a structure-present system's activations at a
checkpoint where the surface metric is still at chance, and does not
read it from a structure-absent system at any checkpoint.

That is the first of the essay's three signatures and the only one this
experiment adjudicates. S2 (elicitability by exhaustive sampling) and S3
(forecastability from below) are measured and reported, but they are
descriptive here and cannot touch the verdict (§6).

**Why this is worth re-running.** The essay's operational content rests
on the claim that resolution cases and percolation cases are
distinguishable *before* the transition. Exp 1 was built to test that on
synthetic ground truth, where which system is which is known by
construction. It returned FAIL on a criterion that could not have been
satisfied by any instrument (§2). The claim is therefore currently
untested, not refuted — and 2c established that the real-model version
of the question is a separate and harder problem, which makes the
synthetic test the one worth getting right.

---

## 2. What changed, and why this is not a post-hoc rescue

Exp 1's overall PASS bar required, for S1 and S2, that the 95% CIs of
the grokking row and the lubana-below row be **disjoint in the predicted
direction with Cohen's d ≥ 2**, on raw probe accuracy.

The grokking probe has 113 classes (chance .0088); the below probe has
10 (chance .100). The below row's accuracy floor therefore sits above
grokking's entire range at 10M. **The predicted direction was
unreachable in every possible world, including for a perfect
instrument.** The criterion was unsatisfiable by construction, not
merely strict.

Three facts about how this was handled, because they determine whether
1b is legitimate:

1. The defect was **discoverable with zero data at design time** and was
   missed in design review, because no size bucket contained both
   systems until M6.
2. It was identified on **2026-07-08 while the campaign was running**,
   noticed post-data, and — per the program's one-change rule, already
   spent on Exp 1's log-space S3 amendment — **no amendment was made and
   the FAIL was allowed to stand.** `analyze.py` stayed frozen as
   tagged.
3. Chance-normalization does **not** rescue it: margins carry
   system-dependent noise floors (below/10M margin .046 ± .008,
   non-significant; grokking/10M .010 ± .004, highly significant). The
   ledger's conclusion, recorded before any re-analysis was contemplated:
   **detection separates; magnitude-of-separation on any
   accuracy-derived scale does not.**

Exp 1b's verdict criterion is therefore detection, not magnitude. That
is a change of criterion after a failure, which the program normally
forbids, and it is admissible here only because the defect is a
demonstrable incommensurability identifiable without data, the failure
was allowed to stand rather than amended, and the replacement is
**tested on fresh seeds** rather than on the records that exposed the
problem. A re-analysis of Exp 1's existing records under the corrected
criterion already exists (`experiments/exp1/results/retrospective_bars.md`,
approved 2026-07-14 as expository material) and is explicitly **not
evidence** for anything in this document.

---

## 3. The matrix

Three trained rows × two sizes (1M, 10M) × five fresh seeds, each with an
**untrained twin**.

| row | ground truth | training |
|---|---|---|
| `grokking` | structure present | Nanda-style `(a·b) mod 113`, Exp 1 recipe |
| `lubana_above` | structure present (task control) | formal language, above percolation threshold |
| `lubana_below` | structure absent | same task, below percolation threshold |
| `untrained` twin of each of the above | no structure, no training | random init at the same architecture, size and seed; same probe data and labels |

Thirty training runs plus **thirty probe-only cells**.

The twin is per-cell rather than a single standalone row because an
untrained network has to be probed on *some* data with *some* labels, and
that choice is not neutral. Exp 1's lubana probe already uses an **entity
split** chosen precisely so that "a random example-split would let the
probe memorize the entity→class lookup and fire on an untrained model"
(`run_lubana.py`); the grokking probe carries no documented equivalent
protection. Matching each twin to its own cell's architecture, data and
labels is the only version of the control that tests the probe actually
used, rather than a probe nobody ran. Cells remain cheap: no training,
one probe fit each. (Amended 2026-08-12, before freeze.)

**Seeds: 100–104.** Exp 1 used 0–4; 1b's are disjoint by construction so
no fresh run reuses an initialization whose S1 outcome is already known.

**The `untrained` row is new.** Exp 1's matrix contained no untrained
control, so nothing in it distinguished S1 firing on *structure* from S1
firing on *reservoir decodability* — a linear readout on a
high-dimensional expansion of the input decodes functions training never
put there. That is exactly what terminated Experiment 2 (120 of 120
fits) and what this program's own methods paper prescribes a control
for. Adding it costs no training compute.

**The 100M tier is dropped**, for cost (~14 of ~19 serial days). This
must be disclosed as a *weakening*: 100M was where Exp 1's discriminator
was most stressed — grokking's S1 fired 4/5 there, and S2/S3 degraded.
1b makes no scale-robustness claim, and a successor that can afford the
tier should restore it.

---

## 4. Signature operationalization

**S1 (verdict-touching).** Carried from Exp 1 §3: present iff probe
accuracy beats a label-permutation null at p < 0.01 (Bonferroni across
layers) at a checkpoint with argmax test accuracy < 5% — **and** exceeds
the accuracy of this cell's own untrained twin, paired per (system, size,
seed). Strict inequality: a tie with the twin is not evidence training
added anything.

**The floor correction is 1b's one pre-committed change (§9), spent
2026-08-12 for a reason ledgered before the change** in
`experiments/exp1b/PROGRESS.md` (commits `6db9788`, `43be192`). The
reason is measured, not anticipated. With the twins built and run on all
thirty cells before any trained data existed, the untrained row fired raw
S1 in **9 of 10 grokking cells** (1M 5/5, 10M 4/5) and **0 of 20** lubana
cells. The label-permutation null permutes labels and refits, so it
controls for probe capacity and for label marginals, but not for
information the random expansion already carries about the label: it
answers "does the probe use the labels?", not "did training put the
structure there?" Only the twin answers the second. Structurally this is
Exp 2c's chance-floor defect again — the criterion's floor was
theoretical chance (1/113 = 0.0088) where the empirical floor is ≈ 0.023,
2.6× higher. Uncorrected, S1 on the grokking row measures the reservoir.

The correction also changes what the twin is *for*. It was a kill-switch;
it is now the calibration every trained cell is read against, which is
the only version that survives its own measurement.

For the `untrained` row there is no training axis and no transition, so
the below-threshold condition is vacuous: the probe is fit at the
matched checkpoint spec against the same null. Twins match their cell's
architecture, size and seed exactly (open item 3, now closed): the runner
constructs each twin through Exp 1's own model constructor and refuses to
record a cell whose parameter-count bucket differs from the one requested.

**S2, S3 (descriptive).** Emitted by the existing pipeline and reported.
Two known findings carry forward and are stated in advance so they are
not later presented as discoveries: S2's elicitability is scale-fragile
(present-row rates .00004–.0415 across seeds at 100M in Exp 1), and S3
under interval coverage is the criterion the program already ruled
against for extrapolations.

**Null-relative magnitudes (descriptive, with a caveat).** −log₁₀(p)
against each run's own permutation null is the only cross-system
continuous scale that is commensurable. It is reported, and it is **not
a bar**, because it is floored by the permutation count: with `n_perm`
permutations the minimum attainable p is 1/(n_perm+1), so a Cohen's d
computed on it partly measures how many permutations were run.

---

## 5. Preregistered pass/fail

Counts are **pooled across the two sizes** — ten runs per row.

| row | required |
|---|---|
| `grokking` | ≥ 8/10 S1-present (floor-corrected) |
| `lubana_above` | ≥ 8/10 S1-present (floor-corrected) |
| `lubana_below` | **0/10** S1-present (floor-corrected) |
| `untrained` (all twins pooled) | **reported, not barred** — see below |

**PASS iff all three bars hold.** Anything else is a **reportable FAIL**,
written up as a finding and not tuned away.

**Why the untrained row lost its bar** (amended 2026-08-12 with the floor
correction, same ledgered reason). It previously required 0/30. Under the
corrected criterion that bar cannot fail: an untrained cell's accuracy
cannot exceed its own, so every twin is absent by construction, and §6's
standing requirement is that an operationalization no baseline can fail
is not a test. Gating on it *and* floor-correcting would also
double-count the same defect. The row is therefore reported — raw fire
rate, per-size split, and Clopper–Pearson bound — and marked
`verdict_touching: False` in the analysis output. Both counts are
reported for every trained row (`present` corrected, `present_raw`
uncorrected) so the correction's effect is visible rather than silently
applied.

The measured row, run before any trained data existed:

| row | raw fires | 1M | 10M | CP95 |
|---|---|---|---|---|
| `grokking` twins | 9/10 | 5/5 | 4/5 | (0.555, 0.997) |
| `lubana_above` twins | 0/10 | 0/5 | 0/5 | (0.000, 0.308) |
| `lubana_below` twins | 0/10 | 0/5 | 0/5 | (0.000, 0.308) |

Pooling is a deliberate trade, stated so it cannot be mistaken for an
oversight. For the absent rows it changes nothing — 0/5 at each size and
0/10 pooled are the same condition — but it lets absence be reported
with a materially tighter Clopper–Pearson bound (95% upper 0.308 at
0/10, against 0.522 at 0/5). The untrained row's own 0/30 bound of 0.116
no longer applies: that row is not barred, and it did not come back zero
(9/30, CP95 0.147–0.494). For the present rows it is **looser** than a
per-size ≥4/5 bar, since ≥8/10 tolerates a (5,3) split that per-size
would fail. **Per-size counts are reported alongside the pooled verdict**
so a "works at 1M, fails at 10M" pattern remains visible even though it
does not flip the result.

Every zero-looking rate ships as a Clopper–Pearson bound, never as a
claimed zero.

---

## 6. What the dumbest baseline achieves

Standing requirement: an operationalization that no baseline can fail is
not a test.

| degenerate instrument | outcome |
|---|---|
| probe that always fires | fails `lubana_below`; and, firing no higher on the trained cell than on its twin, fails both present rows |
| probe that never fires | fails `grokking` and `lubana_above` |
| probe reading **task identity** | fires on above *and* below alike — fails `lubana_below` |
| probe reading **reservoir dimensionality** | reads the same expansion in both cells of a pair, so never exceeds its twin — fails both present rows |

Four distinct failure routes, and the tightest margin in Exp 1's
existing records — grokking at 4/5 on the 10M tier — sits one seed from
breaching the pooled bar. The bar is passable and can genuinely fail.

Routes 1 and 4 previously ran through the `untrained` 0/30 bar. Removing
that bar relocated them rather than eliminating them: under the floor
correction a probe that reads only the expansion cannot clear its own
twin, so it fails the *present* rows instead of the untrained one. Four
routes remain, and the correction is what carries two of them — which is
why the analysis fixture suite mutation-tests it in both directions
(removing the correction, and re-adding the retired gate).

**The bar is now known to be at risk on real numbers, not merely in
principle.** Exp 1's trained grokking accuracies at 10M were 0.0187,
0.0227, 0.0140, 0.0167 and 0.2207; the twins measured here span
0.0140–0.0227. Four of those five trained cells fall inside the twins'
range. If 1b's own trained cells behave similarly, the grokking row
returns roughly 5/5 at 1M and ~1/5 at 10M — pooled ~6/10, a FAIL. That
comparison is distributional, not paired (Exp 1 used seeds 0–4, 1b uses
100–104), so it forecasts rather than settles; the paired test is the
experiment. It is recorded here so a FAIL cannot later be presented as a
surprise.

The `lubana_above` row is what makes the test discriminating rather than
merely descriptive: it is the *same task* as `lubana_below`, differing
only in whether the generating graph is above the percolation threshold.
A signature that tracks task difficulty rather than structure-presence
cannot separate them.

---

## 7. What Exp 1b does not claim

- **Nothing about scale robustness.** The 100M tier is not run.
- **Nothing about S2 or S3.** They are reported, not adjudicated.
- **Nothing about real models.** This is synthetic ground truth. Exp 2c
  tested the real-model version and returned an uninterpretable FAIL at
  ρ = .368 with CI (−.185, .762); a PASS here would not transfer to that
  setting, and should not be described as if it did.
- **Nothing about magnitude of separation.** Only detection.

---

## 8. Run plan

1. **Freeze:** this doc + `analyze_1b.py` + fixture suite, one commit,
   tag `exp1b-preregistered`. Nothing runs before it.

   **DISCLOSED EXCEPTION (Michael, 2026-08-12): three trained cells and
   thirty untrained cells were collected before the tag.** Both were
   required by this document's own open items — item 3 (the untrained
   twins, all thirty, `diagnostics/pre_freeze_untrained/`) and item 2
   (the 1M gate confirmation, seed 100 of each trained row). The three
   trained records sit in the campaign tree at
   `results/<system>/1M/seed100.json`, stamped `fa5dbc5-dirty`,
   `4381ea9` and `7a4ee4a`, and the campaign's skip-if-exists will count
   them rather than re-collect them.

   They are accepted as campaign data rather than moved aside, on this
   reasoning, recorded so it can be judged: **the design was finalized
   before they ran.** The floor-corrected S1 and every §4/§5/§6/§9
   amendment landed at commit `7c7ddb2`, 11:30; the campaign driver at
   `de3c0e2`, 11:51; the first trained cell started at 12:07 and the last
   finished at 16:13. Preregistration protects against a design tuned to
   its outcome data, and that ordering makes it impossible here — the
   amendments were driven entirely by the *untrained* twins, which carry
   no outcome information. Moving the files would change a SHA, not that
   fact, and would re-roll three passing gates — including
   `lubana_below`, which cleared its bar by 16%.

   The thirty untrained cells ARE re-run into the campaign tree after
   the tag (open item 5), because `present` is a derived field whose
   meaning the floor correction changed. The trained records carry no
   such hazard: `analyze_1b` derives the corrected verdict from
   `accuracy` and the twin, never from a record's stored `present`.
2. **Ground-truth gates** per run, as Exp 1 did (`gt_check` in every
   record): a grokking run must exhibit its memorization→generalization
   gap; a `lubana_above` run must reach its transition; a `lubana_below`
   run must stay under its 0.150 bar. A run failing its gate is a
   collection failure, re-run once with a logged reason, then reported
   as attrition — never silently replaced.
3. **1M tier first** (grokking ~31 min for 5 seeds; the lubana rows
   ~24 h each), then **10M** (~25–26 h per row). Untrained cells are
   probe-only and run last, being nearly free.
4. **Analysis:** the frozen script, once, after the verdict projection
   is ledgered.
5. **Close-out:** `VERDICT.txt`, retrospective, tag `exp1b-closed`.

Estimated ~5 days of background wall-clock on the Mac. The DGX Sparks
stay untouched.

---

## 9. Process rules carried forward

- Thresholds frozen pre-run; analysis script committed with the doc and
  not edited after data collection.
- Seeds fixed, logged, and disjoint from Exp 1's.
- **One pre-committed change — SPENT 2026-08-12** on the floor-corrected
  S1 (§4). Exp 1's was spent on the log-space S3 amendment. 1b's reason
  was ledgered before the change, as this rule requires, in
  `experiments/exp1b/PROGRESS.md` (commits `6db9788`, `43be192`): the
  untrained twins were built and run on all thirty cells before any
  trained data existed, and the grokking twins fired 9/10. **No further
  change is available.** If the campaign returns a FAIL, it is reported.
- **Verdict projection ledgered before the analysis runs.**
- No interval-coverage criteria on extrapolations.
- Every zero as a Clopper–Pearson bound.
- Per-run tallies written after reading each record, never inferred from
  the pattern of prior seeds.

---

## Open items before first run

1. ~~`analyze_1b.py` written and frozen with fixture tests, including one
   synthetic case per preregistered provision.~~ **Done** — 17 fixtures
   covering pooled counts, per-size reporting, the floor correction
   (per-cell pairing, strict inequality, raw-vs-corrected reporting,
   absent-row protection), the untrained row's diagnostic status, CP
   bounds on zeros, and four shape refusals. Mutation-tested in both
   directions.
2. Confirm the Exp 1 training recipes reproduce their ground-truth gates
   on seeds 100–104 at 1M before committing the full campaign.

   **SATISFIED ON SEED 100 ONLY — disclosed, not amended (Michael,
   2026-08-12).** This item's wording says five seeds; the confirmation
   ran one seed of each row (3 of 3 PASS, `results/gate_check_1M.md`).
   The remaining four seeds are carried by §8 step 2, which puts a
   `gt_check` in every record and treats a failing run as attrition —
   re-run once with a logged reason, never silently replaced. Closing
   this item literally would cost ~16 h and duplicate the campaign's own
   1M tier. The wording above is left **unchanged**: weakening a
   preregistered requirement to match what was executed would be the
   opposite of recording the gap. The gap is the record.
3. ~~Decide whether `untrained` probes the same architecture per size.~~
   **Closed 2026-08-12: yes, matched per cell** — the runner builds each
   twin through Exp 1's own constructor at the cell's size and seed, and
   refuses to record a cell whose parameter-count bucket differs from the
   one requested (§4). Measured on all thirty cells.
4. Runner script with skip-if-exists durability, per the program's
   resumability rule.
5. **Re-run the thirty untrained cells into the campaign tree after the
   freeze.** The measured row lives in
   `experiments/exp1b/diagnostics/pre_freeze_untrained/`, deliberately
   outside `results/`, because it predates the freeze and `present` is a
   derived field that the floor correction has since changed the meaning
   of. ~1 h 46 min.
