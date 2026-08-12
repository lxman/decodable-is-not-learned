# Experiment 1b — Design Doc: The Discriminator, Retested Under a Corrected Criterion

**Status: DRAFT, not frozen.** Freezes when committed with its analysis
script and fixture suite, per the program's standing rule. Nothing runs
before the freeze commit.

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

Four rows × two sizes (1M, 10M) × five fresh seeds.

| row | ground truth | training |
|---|---|---|
| `grokking` | structure present | Nanda-style `(a·b) mod 113`, Exp 1 recipe |
| `lubana_above` | structure present (task control) | formal language, above percolation threshold |
| `lubana_below` | structure absent | same task, below percolation threshold |
| `untrained` | no structure, no training | random init, probed at the same checkpoint spec |

Thirty training runs plus ten probe-only cells.

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

**S1 (verdict-touching).** Carried verbatim from Exp 1 §3: present iff
probe accuracy beats a label-permutation null at p < 0.01 (Bonferroni
across layers) at a checkpoint with argmax test accuracy < 5%. The
readout is unchanged; only the *cross-system criterion built on it*
(§5) is new.

For the `untrained` row there is no training axis and no transition, so
the below-threshold condition is vacuous: the probe is fit at the
matched checkpoint spec against the same null.

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
| `grokking` | ≥ 8/10 S1-present |
| `lubana_above` | ≥ 8/10 S1-present |
| `lubana_below` | **0/10** S1-present |
| `untrained` | **0/10** S1-present |

**PASS iff all four hold.** Anything else is a **reportable FAIL**,
written up as a finding and not tuned away.

Pooling is a deliberate trade, stated so it cannot be mistaken for an
oversight. For the absent rows it changes nothing — 0/5 at each size and
0/10 pooled are the same condition — but it lets absence be reported
with a materially tighter Clopper–Pearson bound (95% upper 0.308 at
0/10, against 0.522 at 0/5). For the present rows it is **looser** than
a per-size ≥4/5 bar, since ≥8/10 tolerates a (5,3) split that per-size
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
| probe that always fires | fails `lubana_below` and `untrained` |
| probe that never fires | fails `grokking` and `lubana_above` |
| probe reading **task identity** | fires on above *and* below alike — fails `lubana_below` |
| probe reading **reservoir dimensionality** | fires on random init — fails `untrained` |

Four distinct failure routes, and the tightest margin in Exp 1's
existing records — grokking at 4/5 on the 10M tier — sits one seed from
breaching the pooled bar. The bar is passable and can genuinely fail.

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
- **One pre-committed change**, unspent. Exp 1's was spent on the
  log-space S3 amendment; 1b starts with a fresh one, and spending it
  requires a ledgered reason recorded before the change.
- **Verdict projection ledgered before the analysis runs.**
- No interval-coverage criteria on extrapolations.
- Every zero as a Clopper–Pearson bound.
- Per-run tallies written after reading each record, never inferred from
  the pattern of prior seeds.

---

## Open items before first run

1. `analyze_1b.py` written and frozen with fixture tests, including one
   synthetic case per preregistered provision (pooled counts, per-size
   reporting, the untrained gate, CP bounds on zeros).
2. Confirm the Exp 1 training recipes reproduce their ground-truth gates
   on seeds 100–104 at 1M before committing the full campaign.
3. Decide whether `untrained` probes the same architecture per size
   (matched d_model/depth) — assumed yes, needs stating in the frozen
   config.
4. Runner script with skip-if-exists durability, per the program's
   resumability rule.
