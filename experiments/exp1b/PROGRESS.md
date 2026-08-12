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
