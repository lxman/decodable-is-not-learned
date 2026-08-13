# Experiment 1b — Progress Ledger

Design: `../../experiment-1b-design.md` (DRAFT, **not** frozen; tag
`exp1b-preregistered` is Michael's). Plan:
`../../docs/superpowers/plans/2026-08-12-exp1b-instrument.md`.
Entries are append-only.

## 2026-08-12: Tasks 1–3 built

| task | commit | contents |
|---|---|---|
| 1 | `6175741` | `UntrainedRecord` — probe-only cell schema, 5 tests |
| 2 | `9aad2b7` | `analyze_1b.py` — pooled detection verdict, 11 fixture tests, reservoir gate mutation-checked |
| 3 | `f33074e` | `run/run_untrained.py` — untrained probe-only runner, 2 tests |
| 4 | `de3c0e2` | `run/campaign_1b.py` + `campaign_1b.sh` — 60-cell driver, 14 tests |
| 5 | `fffdebb` | `results/gate_check_1M.md` — ground-truth gates, 3 of 3 PASS |

`experiments/exp1/` untouched by all three; verified per commit with
`git show --stat HEAD -- experiments/exp1/`.

**Two interface facts read from the frozen exp1 source during Task 3**, both
of which changed the runner and neither of which was reproducible from memory:

1. `configs/lubana.py:39` — `MODEL_SIZE_TARGETS` has **no `"10M"` key**. The
   10M lubana row is the *base* model at `scale="paper"` with
   `model_size=None` (12,870,144 params), confirmed against
   `experiments/exp1/results/lubana_above/10M/seed0.json`. Only the 1M row
   passes a `model_size`. The runner cross-checks the computed bucket against
   the requested size and raises on mismatch, so a non-twin cannot be
   recorded silently.
2. exp1's runners import their own package absolutely (`from configs.lubana
   import ...`), so `experiments/exp1` must go on `sys.path`. That makes
   `signatures` importable under two names whose `ProbeResult` classes are
   **distinct objects** (`is` → False, verified). `probe_below_threshold` is
   therefore imported through `experiments.exp1.signatures.probe`, so its
   result is the class `records.py` reconstructs. Confirmed by round-trip:
   `type(rec.s1) is ProbeResult` → True.

**Runtimes, seed 100, for campaign sizing (Task 4):** grokking 1M 175 s,
grokking 10M 919 s, lubana_above 1M 27 s / 10M 71 s, lubana_below 1M 25 s /
10M 58 s. One seed's six untrained cells ≈ 21 min; all 30 ≈ 1 h 46 min.

---

## 2026-08-12: The untrained control fires on the grokking row. Decision needed before Task 4.

Task 3's runner was smoke-tested on all six (system × size) cells at seed 100
before committing, because the plan's test exercises only grokking/1M. The
control fired.

**Measured (seed 100, one cell each; records in
`diagnostics/untrained_smoke_seed100/`):**

| system | size | S1 present | acc | chance | null_p | null_mean | 95% CI | cands |
|---|---|---|---|---|---|---|---|---|
| grokking | 1M | **True** | 0.0233 | 0.0088 | 0.000999 | 0.0089 | (0.0163, 0.0323) | 1 |
| grokking | 10M | **True** | 0.0227 | 0.0088 | 0.000999 | 0.0089 | (0.0157, 0.0315) | 1 |
| lubana_above | 1M | False | 0.1378 | 0.1000 | 0.2158 | 0.0982 | (0.0956, 0.1898) | 8 |
| lubana_above | 10M | False | 0.1111 | 0.1000 | 1 | 0.0988 | (0.0732, 0.1596) | 8 |
| lubana_below | 1M | False | 0.1075 | 0.1000 | 1 | 0.0969 | (0.0669, 0.1612) | 8 |
| lubana_below | 10M | False | 0.1290 | 0.1000 | 0.8951 | 0.0989 | (0.0845, 0.1859) | 8 |

Both grokking fires are single-candidate (`cands=1`, layer 0 / token −1), so
Bonferroni does not soften them: the corrected p *is* the raw p, at the floor.
The 95% CIs on the two grokking cells exclude chance (0.0088) entirely.

`null_p = 0.000999` is the permutation floor, 1/(1000+1): the untrained
probe beat **all 1000** label permutations. This is not a marginal fire.

Not a width effect — it fires at d_model=128 (1M) and d_model=904 (10M) alike.
Not a lubana problem — all four lubana twins are silent, exactly as
`run_lubana.py`'s entity-split docstring predicted.

**Mechanism.** The label-permutation null permutes labels and refits, so it
controls for probe capacity and for label marginals. It does **not** control
for information the random expansion already carries about the label.
At the `EQ` position of even an untrained 1-layer transformer, the residual
holds a GELU of a mixture of `emb(a)` and `emb(b)`; the quadratic terms of
that nonlinearity carry bilinear — i.e. multiplicative — information about
the pair, and `(a·b) mod 113` is exactly what a linear readout over such
features can partly recover. Permuting labels destroys the (a,b)→label
correspondence the reservoir exploits, so the null never sees it and sits at
chance (`null_mean` ≈ 0.0089 across exp1's own grokking runs).

Stated plainly: **the label-permutation null answers "does the probe use the
labels?", not "did training put the structure there?"** Only the untrained
twin answers the second question, and it says no.

This is structurally the same error as Exp 2c's chance-floor defect. The S1
criterion's floor is theoretical chance (1/113 = 0.0088); the empirical floor
— what a random network already yields — is ≈ 0.023, **2.6× higher**.

**Retrospective consequence for Experiment 1** (read-only; no exp1 file was
touched). Exp 1's trained grokking S1 accuracies against the untrained floor
measured here:

| grokking 10M, trained | seed 0 | seed 1 | seed 2 | seed 3 | seed 4 |
|---|---|---|---|---|---|
| S1 accuracy | 0.0187 | 0.0227 | 0.0140 | 0.0167 | 0.2207 |
| vs untrained 0.0227 | below | equal | below | below | above |
| exp1 scored | present | present | absent | present | present |

Four of five trained 10M cells sit at or below what a randomly initialized
network yields. exp1 scored that row S1-present in 4/5 — and **three of those
four "present" verdicts (seeds 0, 1, 3) are at or below the untrained floor**.
Only seed 4 (0.2207) clears it by a margin. Seed 2, the one cell exp1 scored
absent, is also the lowest. At 1M all five
trained cells exceed the 0.0233 floor, but seeds 0 and 4 (0.0287, 0.0307)
clear it by only ~1.3×. Lubana is clean at both sizes: `lubana_above` trained
0.19–0.53 vs untrained 0.11–0.14; `lubana_below` trained 0.10–0.15, correctly
absent, vs untrained 0.108–0.129.

**Consequence for 1b as currently designed.** `analyze_1b.verdict` fails on
any untrained fire (design §5 bar: untrained **0/30**). With 2 of 2 grokking
twins firing at seed 100, the expectation is ~10/10 grokking twins firing and
a pooled untrained row of ~10/30. 1b would return **FAIL for reservoir
contamination on the grokking row before a single trained cell runs.**

**Nothing was adjusted.** No change to `probe_n`, `alpha`, `n_perm`, the
probe, the S1 criterion, or the design doc. 1b carries one pre-committed
change and spending it is Michael's call, not the implementer's.

**Routes, for Michael to rule on — none taken:**

- **a.** Let it stand: freeze as designed, run the campaign, report FAIL with
  the reservoir mechanism as the finding.
- **b.** Spend 1b's one pre-committed change on a floor-corrected S1 (the
  untrained twin's accuracy becomes the bar the trained cell must clear,
  replacing theoretical chance) — the direct analogue of the fix 2c's
  chance-floor defect implied.
- **c.** Drop the grokking row and run 1b on the lubana pair only, where the
  entity split is demonstrably untrained-safe. Costs the resolution row, which
  is the row the discriminator claim is about.
- **d.** Re-scope: the finding above may be worth more than the experiment it
  blocks. It extends "decodable is not learned" from Exp 2/2b to Exp 1's own
  grokking row, with numbers.

Task 4 (campaign driver) is **not started** pending this ruling — launching a
~1 h 46 min untrained sweep plus the trained campaign against an already-failed
bar would spend compute to re-measure what these six cells show.

---

## 2026-08-12: Ruling — measure the untrained row before deciding. All 30 cells run.

**Michael's ruling on the four routes: none yet. Confirm across seeds first**
(route as offered: run the grokking twins on all five seeds so the decision
rests on the measured rate rather than an extrapolation from two cells). The
lubana twins were added because they cost ~13 min and turn the pooled figure
from partly-extrapolated into exact.

Records: `diagnostics/pre_freeze_untrained/results/untrained/<system>/<size>/seed<N>.json`
(seeds 101–104) plus `diagnostics/untrained_smoke_seed100/` (seed 100).
**Deliberately NOT in `results/untrained/`**: the design is not frozen, and
`present` is a derived field — pre-freeze records in the campaign path could
feed a stale `present` into `analyze_1b` if the criterion changes, and would
also make Task 4's skip-if-exists treat pre-freeze cells as campaign cells.
Cost of that choice: ~1 h 46 min of recompute after the freeze.

**The complete untrained row, 30/30 cells, seeds 100–104:**

| row | fires | 1M | 10M | CP95 | accuracy range |
|---|---|---|---|---|---|
| `grokking` | **9/10** | 5/5 | 4/5 | (0.555, 0.997) | 0.0140–0.0233 |
| `lubana_above` | 0/10 | 0/5 | 0/5 | (0.000, 0.308) | 0.0933–0.1378 |
| `lubana_below` | 0/10 | 0/5 | 0/5 | (0.000, 0.308) | 0.0842–0.1429 |
| **pooled** | **9/30** | | | (0.147, 0.494) | design bar **0/30** |

Per-cell grokking detail (acc, null_p):

| seed | 1M | 10M |
|---|---|---|
| 100 | 0.0233, 0.000999 ✓ | 0.0227, 0.000999 ✓ |
| 101 | 0.0167, 0.003996 ✓ | 0.0160, 0.005994 ✓ |
| 102 | 0.0167, 0.008991 ✓ | 0.0140, 0.02797 ✗ |
| 103 | 0.0213, 0.000999 ✓ | 0.0213, 0.000999 ✓ |
| 104 | 0.0180, 0.000999 ✓ | 0.0173, 0.001998 ✓ |

**A clean dissociation, not a blanket instrument failure.** The entity-split
probe is untrained-safe in **20/20** cells; the grokking probe is contaminated
in **9/10**. `run_lubana.py`'s docstring claim that the entity split prevents
firing on an untrained model is now measured, not asserted — that is a
positive result for the lubana half of the instrument.

**Where the contamination bites depends on size.** Comparing the untrained
accuracy range against exp 1's trained grokking accuracies:

| | untrained range | trained cells falling *inside* it | trained above the untrained max |
|---|---|---|---|
| 1M | 0.0167–0.0233 | **0/5** | 5/5 (0.0287, 0.0307, 0.0373, 0.0747, 0.1580) |
| 10M | 0.0140–0.0227 | **4/5** (0.0140, 0.0167, 0.0187, 0.0227) | 1/5 (0.2207) |

So the *binary* S1 criterion is contaminated at both sizes — the
label-permutation null is simply the wrong null — but S1 *accuracy* still
separates trained from random cleanly at 1M (min trained 0.0287 vs max
untrained 0.0233, margin 1.23×) and not at all at 10M.

**Caveat, stated because it limits the retrospective claim.** The twins are
seeds 100–104; exp 1's trained cells are seeds 0–4. This comparison is
therefore *distributional, not paired*. The twin-per-cell design gives a
paired test only once 1b's own trained cells run at seeds 100–104. Nothing
above should be read as a per-seed paired result.

**What route (b) would yield, on the unpaired proxy.** A floor-corrected S1
(trained must exceed its untrained twin, not theoretical chance) would admit
roughly 5/5 grokking cells at 1M and ~1/5 at 10M — pooled ~6/10, below the
≥8/10 bar. 1b would still return FAIL on the grokking row, but for a
substantive reason (at 10M the probe genuinely does not beat a random
network) rather than a floor bug. That also independently corroborates exp 1's
own observation that grokking's signatures degraded with scale.

**Still nothing adjusted.** No change to `probe_n`, `alpha`, `n_perm`, the
probe, the S1 criterion, or the design doc. The four routes remain open and
the pre-committed change remains unspent.

---

## 2026-08-12: Ruling — floor-corrected S1. The pre-committed change is SPENT.

**Michael's ruling: route (b).** S1-present now additionally requires
`accuracy > this cell's own untrained twin's accuracy`, paired per (system,
size, seed), strict inequality. This spends 1b's one pre-committed change.
§9's requirement that the reason be ledgered *before* the change is satisfied
by the two entries above (`6db9788`, `43be192`), both of which predate it.

**Applied to three files:**

- `analyze_1b.py` — `_index_twins` + `_apply_floor_correction`; every trained
  row reports `present` (corrected) *and* `present_raw` (uncorrected), with
  per-size splits for both, so the correction is visible rather than silent.
  A trained cell with no twin, or a duplicated twin, is refused — the
  criterion must never fall back to theoretical chance.
- `tests/test_analyze_1b.py` — 17 fixtures (was 11).
- `../../experiment-1b-design.md` — §4 (the criterion + why), §5 (bar table,
  PASS condition, pooling bound), §6 (relocated routes), §9 (change spent),
  open items 1/3 closed and a new item 5.

**Two structural consequences, both handled rather than absorbed.**

1. *The untrained bar had to go.* Under the correction an untrained cell
   cannot exceed its own accuracy, so a 0/30 untrained bar is unfailable —
   and §6's standing requirement is that a gate no baseline can fail is not a
   test. Gating on it as well would also double-count the same defect. The row
   is now reported (rate, per-size, CP) and flagged `verdict_touching: False`.
2. *§6's four failure routes relocated, none lost.* "Always fires" and "reads
   reservoir dimensionality" previously failed via the untrained gate. Under
   the correction neither can clear its own twin, so both fail the **present**
   rows instead. The correction now carries two of the four routes, which is
   why it is mutation-tested in both directions.

**Mutation results (the correction has teeth):**

| mutation | tests failing |
|---|---|
| remove the floor correction | 5 |
| strict `>` → `>=` (ties count) | 4 |
| stop refusing duplicate twins | 1 |
| re-add the retired untrained gate | 1 |
| restored | 0 (17 pass, file byte-identical to backup) |

**Projection, recorded before the campaign runs.** On the unpaired exp 1
proxy the grokking row returns ~5/5 at 1M and ~1/5 at 10M → pooled ~6/10,
below the ≥8 bar → **FAIL**, with `lubana_above` and `lubana_below` expected
to pass. Distributional, not paired (exp 1 seeds 0–4 vs 1b's 100–104), so it
forecasts rather than settles. Written down now so a FAIL cannot later be
presented as a surprise, and a PASS cannot be presented as expected.

**No change remains.** If the campaign FAILs, it is reported.

---

## 2026-08-12: Task 4 — campaign driver

`de3c0e2`. Sixty cells in four blocks (trained/1M → trained/10M →
untrained/1M → untrained/10M). `remaining()` is derived from records on disk,
so the campaign resumes by re-running.

**The twin-recipe invariant is enforced by construction.** `campaign_1b`
imports `LUBANA_SCALE` and `LUBANA_MODEL_SIZE` from `run_untrained` instead of
restating them, and a test asserts *identity*, not equality. If the campaign
declared its own copies they could drift, and the floor-corrected S1 would
then read a trained cell against a floor measured on a different model — the
one silent failure that would invalidate the whole correction.

**Dispatch is mutation-tested** because errors here are silent rather than
loud: `run_grokking(size, seed)` is a wrong run, not a `TypeError`. Five
mutations, all caught — swapped seed/size, size passed as `model_size`,
inverted above/below, untrained ordered first, campaign declaring its own
scale.

**Two plan deviations, both recorded in the plan itself:**

1. `campaign_1b.sh` cds to the **repo root**, not `dirname/..`. exp1b's
   modules import absolutely from the repo root (`experiments.exp1b.*`), so
   exp2c's layout does not transfer; with only `experiments/exp1b` on
   `sys.path` those imports are unresolvable. The log path is derived
   absolutely from the script's own location and still lands at
   `experiments/exp1b/logs/1b/campaign.log`.
2. Task 5's invocation is corrected to
   `python -m experiments.exp1b.run.campaign_1b` from the repo root. As
   written it could not have imported.

Also: `$?` is captured into a local immediately after the command rather than
read inside the `else` branch, where it is one command removed from what it
appears to report.

Suite: 38 passed. Tasks 5 (ground-truth gate, hours of training) and 6
(freeze) remain; the `exp1b-preregistered` tag is Michael's.

---

## 2026-08-12: Task 5 — the STOP GATE passes, 3 of 3

`fffdebb`. Full report at `results/gate_check_1M.md`. Run in the campaign's own
order — grokking first (475 s), its gate read before committing ~4 h to the
lubana rows, which is the point of ordering the cheap tier first.

| row | gate | measured | wall-clock |
|---|---|---|---|
| `grokking` | mem→gen gap | mem @202 → gen @2099, gap 1897, train/test 1.000 | 475 s |
| `lubana_above` | transitioned AND held | giant_frac_min .868, transition @39069, final 1.000 | 5,964 s |
| `lubana_below` | stayed flat | giant_frac_mean .0057, peak .126 < .150, no transition | 8,304 s |

Each tally was written after reading its own record, never inferred from the
previous one, and `certified` was read from the record rather than recomputed.

**The one number worth carrying forward.** `lubana_below` passes, but by the
narrowest margin of the three, and it is the row whose failure would matter
most — the percolation ground truth, the only row asserting a capability
genuinely cannot form. The graph side is not close (giant_frac_mean .0057
against .1, a factor of 18), but the capability side clears by 16% of its bar:
peak .126 against .150, a peak at 1.26× chance where the bar is 1.5×.
`final_metric` .084 is below chance and `transition_step` is None, so the peak
is a fluctuation rather than an approach to a threshold — but a seed
fluctuating 20% higher would fail a gate nothing about the structure suggests
should fail. That is a property of the bar, not the science. Recorded now
rather than discovered at seed 103.

**Provenance practice established for the campaign.** `lubana_above`'s record
was committed the moment it landed, so `lubana_below` began from a clean tree
and stamped a clean SHA. Without that, each finished record dirties the tree
for the next cell — the mechanism that left Exp 1 with 25 of its 45 records
dirty. The campaign should commit per cell. The grokking record keeps
`fa5dbc5-dirty` and was NOT re-run to tidy it: attrition permits a re-run only
for a *failed* gate, with a logged reason, and re-running a passing cell for
cosmetic provenance is the silent replacement that rule forbids.

**Operational risk surfaced.** A Python crash dialog at 14:40 during
`lubana_below` was hermes-agent (PID 98213, SIGTRAP in `libsystem_malloc`
inside `MPSGraph compileWithDevice:`), not this campaign — which was verified
advancing at the time by checkpoint mtimes, not by the log, since the log
records only START/DONE and cannot distinguish running from hung. But another
process was compiling Metal graphs on the same GPU, and `run_lubana` does not
resume mid-cell, so an MPS fault costs a whole cell: up to 2 h 18 min at 1M
and more at 10M.

**Remaining: Task 6 (freeze).** Design doc §4/§5/§6/§9 already amended for the
floor correction; open items 1 and 3 closed, item 5 added. The freeze commit
and the `exp1b-preregistered` tag are Michael's.

---

## 2026-08-12: Task 6 — freeze review. GREEN except two AMBER rulings.

`FREEZE_CHECKLIST.md` drafted, modelled on exp2c's. Verified:

- **Instrument.** 38 fixtures pass (records 5, analyze_1b 17, run_untrained 2,
  campaign_1b 14). Floor correction mutation-tested both ways (remove → 5
  fail; `>`→`>=` → 4; drop duplicate-twin refusal → 1; re-add retired
  untrained gate → 1). Campaign dispatch mutation-tested (5 mutations, all
  caught). Twin-recipe invariant asserted by identity, not equality.
- **Ground truth.** 3 of 3 gates PASS at 1M seed 100, with `lubana_below`'s
  16%-of-bar margin disclosed pre-freeze.
- **Design doc matches the built matrix.** §3 thirty+thirty (85, 95); §4 floor
  correction (132, 136); §5 three bars + reported untrained row (187, 189);
  §6 routes 1 and 4 on the present rows (237, 240); §9 change SPENT (312,
  317).
- **Exp 1 read-only.** `git log 66193a3^..HEAD -- experiments/exp1/` empty
  across all twenty commits, and `git diff --stat` over the same range is
  empty: the exp1 tree is byte-identical to its pre-1b state.
- **Recorded before the data.** Untrained row measured 9/30; verdict
  projection (grokking ~6/10, FAIL) ledgered; seeds disjoint from exp 1's and
  asserted by test.

**Two AMBER lines, both document-versus-execution discrepancies about scope,
neither mine to rule on:**

1. **Open item 2 says "seeds 100–104"; Task 5 ran seed 100 only.** The plan
   specified one seed per row and that is what ran. §8 step 2 covers the rest
   in principle — a `gt_check` sits in every record and a failing run is
   attrition, re-run once with a logged reason. Fully closing item 2 costs
   ~16 h and duplicates the campaign's own 1M tier. Accept the one-seed
   confirmation, or amend item 2's wording?
2. **Seed 100's three trained cells are pre-freeze data in the campaign
   tree.** §8 step 1 says "Nothing runs before it." The gate runs went through
   the campaign driver, which writes to `results/<system>/<size>/seed<N>.json`
   by construction, so `remaining()` will skip them and the campaign will
   count them. This is the hazard the thirty untrained cells were deliberately
   kept out of `results/` to avoid. Mitigating: the runs are deterministic in
   seed and recipe, and `analyze_1b` derives the corrected verdict from
   `accuracy` and the twin rather than the stored `present`, so nothing stale
   can leak. Accept as campaign data, or move to `diagnostics/` and re-run
   post-tag (~4 h 6 min)?

**No tag cut. The freeze commit and `exp1b-preregistered` are Michael's.**

---

## 2026-08-12: Ruling — DISCLOSE on both scope discrepancies. Checklist all GREEN/RULED.

Michael's ruling on the two AMBER lines from the freeze review: **record the
gap, do not rearrange the work so the gap stops needing to be recorded.**
Applied to both, since both are the same shape — a document saying one thing
and the execution doing another, with no defect in either.

**1. Open item 2 ("seeds 100–104") satisfied on seed 100 only.** Accepted; §8
step 2 carries the remaining four via the per-record `gt_check` and the
attrition rule. The item's wording is left **unchanged**. Weakening a
preregistered requirement to match what was executed is the opposite of
disclosure — the gap is the record. Closing it literally would have cost ~16 h
and duplicated the campaign's own 1M tier.

**2. Seed 100's three trained cells stay in the campaign tree.** Disclosed at
§8 step 1 rather than moved to `diagnostics/`. The reasoning is recorded in the
design doc so it can be judged rather than taken on trust:

| | |
|---|---|
| 11:30 | `7c7ddb2` — floor correction, all §4/§5/§6/§9 amendments |
| 11:51 | `de3c0e2` — campaign driver |
| 12:07 | first trained cell starts |
| 16:13 | last trained cell finishes |

Preregistration protects against a design tuned to its outcome data. The design
was finalized 37 minutes before the first trained cell began, and every
amendment was driven by the *untrained* twins, which carry no outcome
information. Moving the files would change a SHA, not that ordering, and would
re-roll three passing gates — including `lubana_below`, which cleared its bar
by 16%. Records stamp `fa5dbc5-dirty`, `4381ea9`, `7a4ee4a`.

The asymmetry with the untrained cells is deliberate and is stated in the doc:
those thirty ARE re-run post-tag (open item 5) because `present` is a derived
field whose meaning the floor correction changed. The trained records carry no
such hazard — `analyze_1b` derives the corrected verdict from `accuracy` and
the twin, never from a stored `present`.

**`FREEZE_CHECKLIST.md` is now all GREEN or RULED. The remaining action is the
`exp1b-preregistered` tag, which is Michael's.**

---

## 2026-08-12: Reproducibility measured — early training is bit-exact, late training is not

Run because the "move to diagnostics and re-run" question turned on whether a
re-run reproduces. `run_grokking(100, '1M')` executed a second time into a
scratch tree and compared field by field against the committed record.

| quantity | committed | re-run | |
|---|---|---|---|
| `mem_step` | 202 | 202 | same |
| `transition_step` | 1796 | 1796 | same |
| `below_threshold_checkpoint` | 126 | 126 | same |
| `s1.accuracy` | 0.035333333333333335 | 0.035333333333333335 | **bit-identical** |
| `s1.null_p` / `present` / `best_layer` / `best_token` | — | — | all same |
| `gt_check.certified` | True | True | same |
| `gen_step` | 2099 | **2454** | **differs, 17%** |
| `gap_steps` | 1897 | **2252** | **differs** |

**The pattern is accumulation, not noise.** Everything up to and including the
0.5 crossing at step 1796 reproduces exactly; the 0.90 crossing does not. MPS
nondeterminism is present but too small to perturb early training, and
compounds into a visibly different trajectory later.

**Three consequences.**

1. **The verdict is safe.** S1 is measured at the *below-threshold* checkpoint
   — step 126 here — which is early enough to be bit-exact. 1b's
   verdict-touching quantity reproduces to 16 decimal places. Any
   reproduction claim should be scoped to that, not to the whole trajectory.

2. **The decision not to re-run seed 100's trained cells was right, and now on
   evidence rather than caution.** `lubana_below`'s gate is `peak_metric`, a
   **max over the entire 100,000-step trajectory** — precisely the late-window
   quantity that does not reproduce. Re-running a cell that cleared its bar by
   16% would have been a genuine fresh draw at the exact quantity least likely
   to come back the same.

3. **`.gitignore`'s justification needs qualifying.** Checkpoints are
   discarded on the grounds that they are "regenerable from configs + seeds"
   (`.gitignore`, exp1's rule, inherited by exp1b). That holds for early
   checkpoints and does **not** hold for late ones: regenerating gives a
   different late-training model. The records remain the durable artifact —
   which is the point — but a late checkpoint deleted is gone, not
   reconstructible. Not changed here; recorded so a successor does not assume
   otherwise.

Method note: three launches were needed. The first two died — one killed when
its wrapper task exited, one with a relative-path import error — before the
third ran clean. Neither failure was signal about the code.

---

## 2026-08-12: FROZEN — tag `exp1b-preregistered` (Michael's explicit go)

Cut at `2dbbc77`, annotated, pushed. Verified immediately before: tree clean,
HEAD == origin/master, 38 fixtures passing, and `experiments/exp1/`
byte-identical to its pre-1b state across all twenty-five commits of the range.

The tag message carries the full freeze record: why 1b exists (Exp 1's S1
criterion was unsatisfiable by any instrument, so the discriminator claim is
untested rather than refuted), what is frozen, the spent pre-committed change
with its ledgered-first reason, the structural consequence of removing the
untrained bar, the 3-of-3 gate result with `lubana_below`'s 16% margin
disclosed, the pre-campaign FAIL projection, the exp1 read-only proof, all
three freeze disclosures, and the reproducibility scope.

**Nothing of the scored campaign runs before this tag. It may now run.**

Launch, detached:

    nohup zsh ~/emergence-paper/experiments/exp1b/run/campaign_1b.sh \
      </dev/null >/dev/null 2>&1 & disown

Two practices the campaign should carry, both learned today:

1. **Commit per cell.** Each finished record dirties the tree for the next
   cell's `git_sha`. Task 5 committed `lubana_above` the moment it landed and
   `lubana_below` stamped clean as a result. Exp 1 did not, and 25 of its 45
   records stamp `-dirty`.
2. **Checkpoint mtimes are the liveness signal, not the log.** The campaign
   log records only START/DONE and cannot distinguish running from hung.

First post-tag work item is open item 5: re-run the thirty untrained cells
from `diagnostics/pre_freeze_untrained/` into the campaign tree (~1 h 46 min).

---

## 2026-08-12: CORRECTION to the reproducibility entry — "17%" overstated it

The entry above reports `gen_step` drifting 2099 → 2454 on a re-run and calls
it a 17% difference. Arithmetically true, materially misleading, and corrected
here rather than left standing.

**The checkpoint grid is log-spaced:** … 1536, 1796, **2099**, **2454**, 2868 …
So 2099 → 2454 is **exactly one grid step** — the smallest non-zero change the
instrument can register, not a 17% change in the underlying trajectory. All
that is established is that the 0.90 crossing landed in a different checkpoint
bin; the true difference in crossing time is bounded only by the bin width
(~658 steps), and could be arbitrarily small.

Caught because `grokking/1M/seed104` returned mem=202, gen=2454, gap=2252 —
identical to the seed-100 re-run — which looked alarming until the grid
explained it. Matching mem/gen/transition values across seeds are
**quantization, not spurious determinism**: seeds 100/101/102 all transition at
1796 and 103/104 both at 2099, on a grid whose spacing there is ~300 steps.

**What survives unchanged, and is the important part:** `s1.accuracy`
reproduced to 16 decimal places (0.035333333333333335), along with `null_p`,
`present`, `best_layer`, `best_token`, `transition_step`,
`below_threshold_checkpoint` and `mem_step`. The verdict-touching quantity is
reproducible. That claim rests on an exact match, not on a grid-quantized one.

**What weakens:** the argument that re-running seed 100's trained cells was
risky *because* late-trajectory quantities drift. `lubana_below`'s
`peak_metric` is still a max over the whole trajectory and so is structurally
more exposed than an early-checkpoint measurement, but the evidence that late
quantities meaningfully diverge is now one grid step, which is weak. The
DISCLOSE ruling does not depend on it — it rests on the ordering (design
finalized 11:30, first trained cell 12:07), which is unaffected.

---

## 2026-08-12 ~21:50: GPU OOM during lubana_above/1M/seed102 — cell flagged for gate scrutiny

A Metal command buffer failed mid-run on this cell:
`Insufficient Memory (00000008:kIOGPUCommandBufferCallbackErrorOutOfMemory)`,
with the accompanying "The Metal Performance Shaders operations encoded on it
may not have completed."

**The campaign did not die.** Both processes stayed alive, no ABORT was logged,
and the cell continued to step 79,060 of 100,000. PyTorch surfaced the error
and training proceeded.

**The risk this leaves:** if operations encoded on the failed buffer did not
complete, the run took a step on incomplete state, and nothing downstream would
say so directly. **This cell's `gt_check` must therefore be read on its own
merits, not assumed** — `lubana_above` must reach its transition AND hold
(`giant_frac_min` > 0.3, transition exists, `final_metric` >= 0.5). A failure
is attrition under §8 step 2 — re-run once with a logged reason — and the
reason is this entry.

Context: `hermes-agent` crashed inside `MPSGraph compileWithDevice:` earlier the
same day (14:40), so a second process was contending for the GPU. Swap sat at
14.2 GB of 15.4 GB, though `memory_pressure` reported 33% free at the time and
total RSS was only 5.3 GB across 542 processes — the swap figure is an
accumulated high-water mark, not live starvation.

**Method note, second occurrence today.** The initial read of this incident was
"campaign hung, zero checkpoints in 5 minutes." Both halves were wrong.
`find -newermt` silently matches nothing on macOS — the same idiom that missed
the hermes crash report at 14:40 — and the checkpoint interval at that point in
training was 18 minutes and widening, so a 5-minute window proves nothing even
when the command works. **`ls -lt` on the in-flight cell's checkpoint directory
is the liveness check.** Likewise `vm_stat`'s `Swapouts` and `Pageins` are
cumulative counters since boot, not gauges, and reading them as current state
manufactured a memory crisis that was not occurring.

---

## 2026-08-12 22:00: ABORT — lubana_above/1M/seed102 lost to the GPU OOM. Attrition, re-run once.

The cell flagged two entries above did not merely need scrutiny; it died.

    ABORT trained/lubana_above/1M/seed102 after 6312s:
    ValueError('Input X contains NaN.')

**Diagnosis — the OOM corrupted the final stretch of training.** All 47
checkpoints were scanned:

| checkpoints | NaN params | train_loss |
|---|---|---|
| step_0000001 … step_0079060 (46) | **0** | finite |
| **step_0100000** | **824,232 of 939,312** | **nan** |

Training was clean through step 79,060 (written 21:37) and NaN by step 100,000.
The Metal command-buffer failure at ~21:50 sits inside that window. Its own
message said "operations encoded on it may not have completed"; they did not,
the weights diverged, and the S1 probe then refused NaN activations. The
corrupt checkpoint's `eval_metric` is 0.118 — chance for a 10-class task.

**The failure was loud, which is the good outcome.** No record was written, so
nothing entered the campaign tree; the run died rather than recording a
plausible-looking wrong number. Record count is unchanged at 8. The campaign
aborted the whole `trained/1M` block on non-zero exit, as designed, rather than
pressing on.

**Disposition: attrition under §8 step 2** — "a run failing its gate is a
collection failure, re-run once with a logged reason, then reported as
attrition — never silently replaced." The logged reason is this entry plus the
OOM entry above. This is the first attrition of the 1b campaign.

**Before the re-run, two things:**

1. **Delete `checkpoints/lubana_above_m1M/seed102/`.** The corrupt final
   checkpoint would otherwise sit in the directory the re-run writes to. A
   fresh run should overwrite every step on the same grid, but leaving a known
   NaN artifact in the path that `list_checkpoints` reads is an avoidable risk.
2. **Reduce GPU contention.** `com.mlx-vlm-server` (port 8080) holds
   `EleutherAI/pythia-410m` resident — a leftover from the now-closed exp2c —
   and its catalog includes `Meta-Llama-3-70B-Instruct-4bit` (~37 GB) and
   `pythia-12b`. Any request loading one of those would take most of the 48 GB
   unified pool from under a five-day GPU job. Steady-state cost of these
   services is trivial (~0.5 GB total); the hazard is entirely in what they
   load on demand.

The campaign resumes by re-running `campaign_1b.sh` — `remaining()` reads the
disk, so it restarts at exactly this cell.
