# Experiment 5b — ledger

**Status: DIALS RULED 2026-09-25 — every dial of `experiment-5b-design.md` §10 as
recommended (Michael: "rule accepted"). The build by SDD follows this ledger.**
Nothing has been tagged, no model has been contacted, no computation has run
on Experiment 5's cell table.

## Pre-tag executions of `analyze_5b.run()` on the real tree

Tally: **0**. (`analyze_5b.py` does not exist yet — Task 5.)

## Task 1 (2026-09-25): `battery_5b.py` — constants/pins, the small-side
window, the `_unit_5b.json` contract, Experiment 5's verdict pins, the two
bindings, frozen/import pin scaffolds, git helpers

Built: `experiments/exp5b/battery_5b.py` — every constant the design's §3/§10
fixes (the window steps, the size order, the placebo sign and √2, the σ grid
and belief, the calibration α, the loss tolerance, the spike pair, T-bar/α/
min-live-cells/min-nonzero-blocks carried from `battery_5`, the world and
cell-name tuples, the `WHYS_5B` pair, Experiment 5's post-verdict referents);
paths over an Exp5b results tree (units root, unit dir — delegates to
`battery_5.unit_dir_5` so both experiments' units share one directory shape,
`_unit_5b.json`, host/gate1/power records, the halt marker); the unit
contracts (`unit_steps_5b`/`reread_steps_5b`/`expected_units_5b`,
`unit5b_record_failures_5b` checking size/step/tag pins/why/reread/
reread_record/host/git-sha, `unit_complete_5b` requiring both Experiment 5's
`_unit.json` and 5b's own attestation, `exp5_unit_record_5b` a read-only
window onto Experiment 5's committed unit files); the two bindings
(`require_prereg_5b` over the 5b instrument blobs at `exp5b-preregistered`,
`require_exp5_closed_5b` over Experiment 5's thirteen instrument blobs AND
the committed `verdict.json` sha at `exp5-closed`, with a `verdict_sha=False`
escape for the synthetic worlds); the verdict-pin machinery
(`exp5_verdict_pin_failures_5b` against the literal subset,
`exp5_verdict_equal_failures_5b` for a full re-derivation compared modulo
`meta`/`pins_active`); the frozen/import pin scaffolds
(`FROZEN_SHA256_5B`/`IMPORTED_SHA256_5B` stay `None` until Task 6;
`check_frozen_5b`/`check_imports_5b` refuse until then); git helpers
(`git_sha_5b`, `is_ancestor_5b`, `projection_commit_5b`,
`projection_edits_5b`, `prereg_tag_commit_5b`).

**The verdict sha pinned:** `EXP5_VERDICT_SHA256_5B =
50a6f57e8e4b204adf83d84890fb19cb78eec495a977861e0f6a4cca26d61f11`, from
`shasum -a 256 experiments/exp5/results/verdict.json` run at this task.

**The literal pin verified against the committed file** — the one-liner
`python -c "import json;v=json.load(open('experiments/exp5/results/verdict.json'));print(v['verdict'],v['tree']['modifier'],repr(v['primary']['T']),v['primary']['n_cells'],v['primary']['n_rungs'],repr(v['primary']['rung_block']['p']),v['primary']['n_nonzero_blocks'],v['gate4']['pairs_kept'])"`
printed `NOT-MATCHED MIXED 0.05349206349206348 63 13 0.0006103515625 13 21`,
matching `EXP5_VERDICT_PIN_5B` field for field; the 63-live-cell count was
also re-derived directly from `verdict.json["cells"]` (`live and defined_P`)
in the test suite, independent of the pin dict.

Tests: `experiments/exp5b/tests/test_battery_5b.py` — 11 cases (incl. one
`slow` case against the real committed `exp5-closed` tag and its bound
blobs), plus `experiments/exp5b/tests/conftest.py` (registers the `slow`
mark) and `experiments/exp5b/tests/helpers_5b.py` (the tag-injection and
prereg-wrap helpers later tasks share). `python -m pytest
experiments/exp5b/tests/test_battery_5b.py -q` → 11 passed.

## Task 2 (2026-09-25): `stats_5b.py` — the small-side reads, the matched
placebo, the cell join, the primary (generic key), σ̂_s, the calibration
read, the tree, the modifier, and the pure parts of S1/S2/S6/S7/S8/S9/S10/S12

Pure functions, no I/O, transcribed verbatim from the task brief. `small_reads_5b`
reads a size's `{step: {rung: count}}` table down to the final (`b5.FINAL_STEP_5`)
plus whichever of the three window steps (`b5b.WINDOW_STEPS_5B`) are present.
`placebo_terms_5b` builds the six (outer-window × member) matched-placebo terms
`|(a − b_s) + sign·(f_B − n_j)| / √2` (`b5b.PLACEBO_SIGN_5B`, `b5b.SQRT2_5B`); a
missing outer window (`b_minus` or `b_plus` is `None`) drops its three terms,
leaving three. `cell_5b` joins one of Experiment 5's cells to one small-side read:
carries the nineteen identifiers verbatim, computes `Q` (mean absolute deviation of
the members from `f_B`), `M`/`M_minus` (mean of the placebo terms at `+sign`/`−sign`),
the four sensitivity forms `c_sym` (`(R−M)/n`), `c_naive` (`(R − (P+Q)/2)/n`), `c_max`
(`(R − max(P,Q))/n`), `c_minus` (`(R−M_minus)/n`) — each `None` when its input is
undefined (no members → `Q`/`M`/`M_minus` all `None`) — plus the four small-side reads
(final first, then descending step), their clear status against `battery_5.clears_5`,
whether that status is constant across the four, and the ddof-1 sample SD of the four
reads (`None` below two reads). `primary_5b` takes a generic `key` (default `c_sym`)
and is otherwise Experiment 5's `primary_5` verbatim — rung/family block sums, all
three of `stats_5.sign_flip_p_5`'s block levels (rung, family, cell), `n_nonzero_blocks`
and `p_min_attainable` lifted from the rung-block result. `sigma_hat_5b` pools the
per-cell `small_sd`² over cells with both `small_sd` and `defined_M`, RMS at the top
level and per small side. `calibration_read_5b` linearly interpolates the built power
record's simulated σ̂ axis (`np.interp`, clamped at the bottom, `OFF-GRID` strictly
above the top) for `alpha_realized` and `null_mean_T`, reports `T_star = T_sym −
null_mean_T`, and cells `CALIBRATED` (`alpha_realized < b5b.ALPHA_CAL_5B = .05`) or
`INFLATED` (`≥ .05`, so `alpha == .05` exactly reads `INFLATED`) when in grid.
`tree_5b` is INSUFFICIENT_DATA on any failure, UNDETERMINED below
`MIN_LIVE_CELLS_5B`/`MIN_NONZERO_BLOCKS_5B`, else SURVIVES (cell = the calibration
cell) when `p < ALPHA_5B` and `T ≥ T_BAR_5B` together, else NOT-SURVIVED with cell
INSIDE (neither), SIGN-ONLY (p only) or SIZE-ONLY (T only) — ties go the strict way
on both bars (`p == α` is not `< α`; the SIZE-ONLY/SIGN-ONLY boundary cases in the
brief's fixture both landed as specified). `modifier_5b` is `stats_5.modifier_5`
verbatim with the selector swapped from `R_gt_P` to `R_gt_M`. The eight secondary
functions (S1 by-row + the "outside 2.8b" subset restricted to `outside_2p8b`'s
27-cell slice of the 28-cell fixture; S2 swap/designation tables over `f_B` and the
three window steps; S6 the L-AHEAD/S-AHEAD ledger with the small-side stability
fraction; S7 by-type with the same "fewer than 5 rungs → no p" rule as Experiment 5;
S8 the one-member zero-contact reading using Experiment 5's committed S11 step; S9
the named spike pair excluded, referents attached from `battery_5b.EXP5_REFERENTS_5B`;
S10 the three alternate sensitivity forms run through the same primary; S12 newly-live
cells found by re-checking a dead Experiment-5 cell's small-side reads against the
2d floor) are all pure joins over `cell_5b` output plus `primary_5b`/`modifier_5b`, no
new statistics.

**TDD.** RED: `~/emergence-lab/.venv/bin/python -m pytest
experiments/exp5b/tests/test_stats_5b.py -q` → `ImportError: cannot import name
'stats_5b' from 'experiments.exp5b'` (`stats_5b.py` did not exist yet), as expected.
GREEN, first attempt, no fixture or assertion changes needed: same command → `12
passed`. Full fast set: `python -m pytest experiments/exp5b/tests -m "not slow" -q`
→ `22 passed, 1 deselected`; repeated under `-W error` → identical, no warnings.
Whole `tests/` directory including the one `slow` case: `python -m pytest
experiments/exp5b/tests -q` → `23 passed`.

**Self-review.** Every name in the brief's Produces list exists with the brief's
signature (checked by `inspect.signature` against the list verbatim). The `cell_5b`
output's key set was diffed programmatically against the brief's exact 37-name list
(19 identifiers + 18 computed fields) on a live example — zero missing, zero extra.
No brief assertion needed weakening; nothing papered over.
