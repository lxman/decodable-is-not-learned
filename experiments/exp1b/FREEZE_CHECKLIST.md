# Experiment 1b — Freeze-review checklist

Drafted 2026-08-12 at Task 6 close, modelled on `../exp2c/FREEZE_CHECKLIST.md`.
One line per pre-freeze condition, each carrying the check that verifies it, so
that "the number sat in the record unchecked" cannot recur by construction.

**The freeze commit and the `exp1b-preregistered` tag are Michael's.** Nothing
below tags anything. Design §8 run plan step 1 defines the freeze as "this doc
+ `analyze_1b.py` + fixture suite, one commit, tag `exp1b-preregistered`.
Nothing runs before it." Everything named there is already committed across the
twenty commits of the 1b range, so the remaining action is the tag itself.

## Instrument — GREEN

- [x] **`analyze_1b.py` frozen with a fixture suite.** 38 tests, all passing
  (`records` 5, `analyze_1b` 17, `run_untrained` 2, `campaign_1b` 14). One
  synthetic case per preregistered provision: pooled counts, per-size
  reporting, CP bounds on zeros, the floor correction (per-cell pairing,
  strict inequality, raw-vs-corrected reporting, absent-row protection), the
  untrained row's diagnostic status, and four shape refusals. No test reads a
  real record.
- [x] **The floor correction is mutation-tested in both directions.** Removing
  it fails 5 tests; `>` → `>=` fails 4; dropping the duplicate-twin refusal
  fails 1; re-adding the retired untrained gate fails 1. Restored file
  byte-identical to backup. A gate no test can break is not a gate, and this
  one now carries two of §6's four failure routes.
- [x] **Campaign dispatch is mutation-tested.** Five mutations, all caught:
  swapped seed/size in `run_grokking`, size passed as `model_size`, inverted
  above/below, untrained ordered first, campaign declaring its own lubana
  scale. Argument-order errors here are silent rather than loud —
  `run_grokking(size, seed)` is a wrong run, not a `TypeError`.
- [x] **The twin-recipe invariant holds by construction.** `campaign_1b`
  imports `LUBANA_SCALE` and `LUBANA_MODEL_SIZE` from `run_untrained` rather
  than restating them, and a test asserts *identity*, not equality. A second
  declaration could drift, and the floor correction would then read a trained
  cell against a floor measured on a different model.
- [x] **Runner is skip-if-exists and resumable.** `remaining()` is derived from
  records on disk, never from a progress file that can disagree with reality.
  Verified in practice during Task 5: the second invocation reported
  "1/60 cells already on disk; 2 selected to run" and skipped the completed
  grokking cell.

## Ground truth — GREEN

- [x] **Design open item 2 — recipes reproduce on fresh seeds.** 3 of 3 PASS at
  1M, seed 100. `grokking` mem @202 → gen @2099, gap 1897, train/test 1.000
  (475 s). `lubana_above` giant_frac_min .868, transition @39069, final 1.000
  (5,964 s). `lubana_below` giant_frac_mean .0057, peak .126 < .150 bar, no
  transition, final .084 below chance (8,304 s). Full report:
  `results/gate_check_1M.md`.
- [x] **DISCLOSED — `lubana_below`'s margin is the thinnest of the three.** It
  clears by 16% of its bar (peak .126 against .150; 1.26× chance where the bar
  is 1.5×). The graph side is not close (giant_frac_mean .0057 against .1, a
  factor of 18) and `transition_step` is `None`, so the peak is a fluctuation
  rather than an approach to a threshold — but a seed fluctuating 20% higher
  would fail a gate nothing about the structure suggests should fail. That is
  a property of the bar, not the science. Recorded pre-freeze so it cannot be
  presented as a discovery at seed 103.

## Design doc matches the built matrix — GREEN

- [x] **§3** reads "Three trained rows × two sizes × five fresh seeds, each
  with an untrained twin" and "Thirty training runs plus thirty probe-only
  cells" (lines 85, 95).
- [x] **§4** carries the floor correction — "the accuracy of this cell's own
  untrained twin, paired per (system, size, seed)" — and records it as the
  pre-committed change (lines 132, 136).
- [x] **§5** shows three bars plus a reported untrained row: "reported, not
  barred" and "PASS iff all three bars hold" (lines 187, 189).
- [x] **§6** routes 1 and 4 point at the present rows, not the retired gate
  (lines 237, 240).
- [x] **§9** records the change as SPENT with "No further change is available"
  (lines 312, 317).
- [x] **Open items:** 1 closed (fixture suite), 3 closed (twins match
  architecture per cell, measured on all thirty), 4 satisfied by Task 4, 5
  added — the thirty untrained cells re-run into the campaign tree
  post-freeze. **Item 2 is PARTIALLY closed — see below.**

## Two questions for Michael before the tag — AMBER, not GREEN

Both are discrepancies between documents, not defects in the work. Neither is
mine to rule on, and marking this checklist all-green without them would be
the kind of quiet reconciliation the program exists to avoid.

- [ ] **AMBER — open item 2 says five seeds; Task 5 ran one.** Verbatim:
  "Confirm the Exp 1 training recipes reproduce their ground-truth gates **on
  seeds 100–104** at 1M before committing the full campaign." The plan's Task
  5 specifies one seed of each row, and that is what ran (seed 100, 3 of 3
  PASS). The remaining four seeds are covered in principle by §8 step 2, which
  puts a `gt_check` in **every** record and treats a failing run as attrition —
  re-run once with a logged reason, never silently replaced. So the mechanism
  exists; the pre-freeze confirmation is simply narrower than item 2's
  wording. Fully closing it costs ~16 h (four more 1M seeds × three rows) and
  would duplicate the campaign's own 1M tier. **Ruling needed:** accept the
  one-seed confirmation and let §8 step 2 carry the rest, or amend item 2's
  wording to match what was actually preregistered as sufficient.

- [ ] **AMBER — seed 100's three trained cells are pre-freeze data sitting in
  the campaign tree.** §8 step 1 says of the freeze: "Nothing runs before it."
  Task 5's gate runs wrote to `results/<system>/1M/seed100.json` — the campaign
  paths — so `remaining()` will skip those three cells and the campaign will
  count them. This is the same hazard I kept the thirty untrained cells out of
  `results/` to avoid, but the gate runs went through the campaign driver,
  which writes there by construction.
  *Mitigating:* the runs are deterministic in seed and recipe, so the records
  are byte-equivalent to what the campaign would produce; and `analyze_1b`
  derives the corrected verdict from `accuracy` and the twin, not from the
  record's stored `present`, so nothing stale can leak through the way it
  could for an untrained cell.
  **Ruling needed:** accept them as campaign data, or move them to
  `diagnostics/` alongside the untrained cells and let the campaign re-run
  them post-tag (~4 h 6 min).

## Exp 1 read-only constraint — GREEN

- [x] **No 1b commit touched `experiments/exp1/`.**
  `git log --oneline 66193a3^..HEAD -- experiments/exp1/` returns nothing
  across all twenty commits of the range, and
  `git diff --stat 66193a3^ HEAD -- experiments/exp1/` is empty: the exp1
  tree is byte-identical to its state before 1b began. Verified per commit
  during the work with `git show --stat HEAD -- experiments/exp1/`.
  (Not checked against `exp1-analysis-frozen` — that tag marks the *analysis*
  freeze, cut before the campaign finished, so thousands of lines legitimately
  postdate it and that diff is never empty.)

## Recorded before the data — GREEN

- [x] **The untrained row is measured, not assumed.** All thirty twins ran
  before any trained cell: `grokking` 9/10 (1M 5/5, 10M 4/5, CP95
  .555–.997), `lubana_above` 0/10, `lubana_below` 0/10 (both CP95 .000–.308),
  pooled 9/30. This is what the pre-committed change was spent on.
- [x] **Verdict projection ledgered before the analysis runs** (§9). On the
  unpaired exp 1 proxy the grokking row returns ~5/5 at 1M and ~1/5 at 10M —
  pooled ~6/10, below the ≥8 bar, i.e. **FAIL**, with both lubana rows
  expected to pass. Recorded in `PROGRESS.md` so a FAIL cannot later be called
  a surprise, nor a PASS called expected. The comparison is distributional,
  not paired (exp 1 used seeds 0–4, 1b uses 100–104), so it forecasts rather
  than settles.
- [x] **Seeds fixed, logged, disjoint from Exp 1's.** 100–104 against exp 1's
  0–4, asserted by test (`test_plan_never_uses_an_exp1_seed`).

## Carried into the campaign — not freeze blockers

- [ ] **Commit per cell.** Each finished record dirties the tree for the next
  cell, which is how Exp 1 ended up with 25 of its 45 records stamping
  `-dirty`. Task 5 committed `lubana_above` the moment it landed and
  `lubana_below` stamped clean as a result. The campaign should do the same.
- [ ] **MPS contention is a live risk.** A `hermes-agent` child crashed with
  SIGTRAP inside `MPSGraph compileWithDevice:` during Task 5's `lubana_below`
  run. Ours was unaffected, but `run_lubana` does not resume mid-cell, so an
  MPS fault costs a whole cell — up to 2 h 18 min at 1M and more at 10M.
- [ ] **Campaign cost.** Task 5's three 1M cells took 4 h 6 min for one seed.
  The trained side is thirty cells across two tiers; the untrained side is
  ~1 h 46 min total. Multi-day.
- [ ] **`experiments/exp1/` stays read-only for the campaign too.** The
  constraint does not expire at the freeze.

## Remaining action

**Michael's, and only Michael's.** Every instrument, ground-truth,
design-match, read-only and recorded-before-the-data condition is GREEN. Two
AMBER lines above need a ruling first — both are document-versus-execution
discrepancies about *scope*, not defects in what was built:

1. open item 2's five seeds against Task 5's one, and
2. whether seed 100's three trained cells count as campaign data or move to
   `diagnostics/`.

Once ruled, cut `exp1b-preregistered`. The campaign must not launch before the
tag.
