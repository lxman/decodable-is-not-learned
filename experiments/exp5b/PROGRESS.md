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

## Task 3 (2026-09-25): `power_5b.py` — the noise-grid power and calibration
record, transcribed verbatim from the brief. `structure_5b`/`structure_sha256_5b`
carry Experiment 5's 63 committed live cells (13 `STRUCTURE_KEYS_5B` fields plus
the committed a−f offset) through to a content hash. `simulate_5b` draws f ONCE
per cell at σ_s around its truth and feeds that single draw into both
Experiment 5's rule (via `stats_5.cell_5`, becoming `cell5["f"]`) and 5b's rule
(via `stats_5b.cell_5b`'s `f_B`) — by design the two are the same value, never
independently noised; the large side's reads and placebo drifts mirror
Experiment 5's own `simulate_battery_5` exactly; the three window members share
one small-side drift N(0, DRIFT_5B). `arm_5b` runs `n_sim` batteries through
three rules at once (5b's `c_sym` via `stats_5b.tree_5b`, Experiment 5's own
rule replayed on the noised f via `stats_5.tree_5`, and the naive `c_naive`
form) plus the simulated σ̂ mean. `compute_5b` sweeps the σ_s grid (six points ×
four arms), then the D grid, then the fraction grid, one rng consumed in that
fixed order; the declaration reads the plugin arm at σ_s = 15 against the 0.75
bar. `main()` requires `exp5-closed`, the frozen/import pins, and refuses a
second write.

**A ruled correction to the brief's own test.** First GREEN attempt: 8 of 9 new
tests passed; `test_simulate_reads_f_once_and_members_with_a_shared_drift`
FAILED deterministically (not a seed fluke — confirmed by direct inspection)
on `assert any(c["f_B"] != c["f"] for c in cells)`. Root cause: `c["f_B"]` and
`c["f"]` on a `simulate_5b` output cell are provably the SAME value on every
cell, by construction — both are sourced from the one `f_read` draw threaded
into `ss.cell_5(f=reads["f_read"], ...)` (becoming `cell5["f"]`, then copied
into `c["f"]` by `stats_5b`'s `IDENT_KEYS_5B`) and into `st.cell_5b(...,
{"f_B": f_read, ...}, ...)` — exactly what the module's own docstring says is
intentional ("f is ONE draw at σ_s around its truth, entering both R and M").
No true, un-noised small-side value is exposed on the returned cell dict at
all; the assertion as written was unsatisfiable for any σ_s > 0 at any seed.
Reported as a finding per the task's binding constraints (not fixed by
weakening the assertion or altering `power_5b.py`); ruling received and
ledgered: the brief's test was wrong, the design/code were right — the truth
being compared against is the *structure's* `f` (`structure_5b`'s output,
which `simulate_5b` returns in the same order), not the simulated cell's `f`.
Applied exactly as ruled: the sigma_s = 0 block now zips `cells` against the
structure (`st_ = pw5b.structure_5b(_cells5())`, `for c, s in zip(cells,
st_)`) and asserts `c["f_B"] == s["f"]`; the sigma_s = 15 block asserts
`any(c["f_B"] != s["f"] for c, s in zip(cells, st_))`; both carry the comment
`# ruling (Task 3): c["f"] IS the draw; the truth is the structure's f`. No
other line of the test file or of `power_5b.py` touched — both remain
otherwise byte-identical to the brief.

**TDD.** RED: `~/emergence-lab/.venv/bin/python -m pytest
experiments/exp5b/tests/test_power_5b.py -q` before `power_5b.py` existed →
`ImportError: cannot import name 'power_5b'`, as expected. GREEN (post-ruling):
same command → `9 passed in 23.19s`; repeated under `-W error` → identical, `9
passed`, no warnings. Full `experiments/exp5b/tests` directory (Tasks 1+2's
suites plus this one): `32 passed in 23.57s` — nothing regressed.

**Timings.** Whole test file: 23.02 s pre-ruling (8 passed/1 failed) / 23.19 s
post-ruling (9 passed) / 23.57 s for the full `tests/` directory. One `arm_5b`
call at `n_sim=100` on the real 63-cell live structure
(`pw5b.structure_5b(pw5b.load_cells5_live_5b(b5b.EXP5))`, σ_s 15, offset_scale
1.0): **2.02 s** (`n_live` 63; `P_fire_5b` .99, `P_fire_exp5` 1.0,
`sigma_hat_sim_mean` 14.95). Linear extrapolation only (not measured): the real
record at `n_sim=1000` over 6×4 + 6 + 4 = 34 arm-equivalents is ≈ 34 × 10 ×
2.02 s ≈ **11–12 min**, longer than the brief's "expected ≈ 3–6 min" — flagged
for Task 6, not resolved here.

**Self-review.** Every name in the brief's Produces list exists with the
brief's signature; `power_5b.py` verified byte-identical to the brief's Step-3
code block by programmatic diff (zero differences). `compute_5b`'s record
carries every key in the brief's "record's keys" list (exercised by
`test_compute_record_shape_axes_and_determinism`). The rng is consumed in the
documented fixed order (`test_rng_order_is_fixed_grid_then_d_then_fractions`:
the record's `grid[0]["arms"]["null"]` equals a direct `arm_5b` call on a
fresh rng at the same seed; a different seed differs). `main`'s ONCE/
exp5-closed refusal behavior passes. Output pristine under `-W error`. The one
finding above was reported rather than papered over, and resolved only after
an explicit ruling.

## Task 4 (2026-09-25): `collect_5b.py`, `run/units_5b.py`,
`run/preflight_5b.py` — the per-unit pipeline over Experiment 5's writer,
the twelve-unit re-read comparison, the digest halt, the stage runner

Built: `experiments/exp5b/collect_5b.py` (`reread_compare_5b` — gate 1's
twelve-unit comparison of this box's `_checkpoint.json`/`_loss.json`/per-rung
files against Experiment 5's committed unit of the same `(size, step)`,
returning digest/loss/count/continuation diffs plus `byte_identical` and
`tolerance_failures` via `battery_5.tolerance_failures_5`; `write_unit5b_record_5b`
writing `_unit_5b.json`; `run_unit_5b` — Experiment 5's `run_unit_5` called
verbatim into 5b's tree, `_unit_5b.json` written LAST, the re-read run only on
`battery_5b.reread_steps_5b()` (the final and the first window step), a digest
mismatch halting via `SystemExit(2)` after the unit and its attestation are
already on disk (`halt_on_digest=True` by default, `False` for the analyzer's
refusal-tree tests); a unit complete under Experiment 5's own rule but missing
`_unit_5b.json` is removed WHOLE and redone, never adopted (Review Focus 1);
`gate1_record_5b` — the runner's attestation over every re-read unit present,
rewritten after each side, digest/loss/tolerance failures collected, the
analyzer left to re-derive the comparison itself per F-2's lesson).
`experiments/exp5b/run/units_5b.py` (`run` — refusal order 5b prereg tag →
`exp5-closed` binding → frozen → imports → `power_5b.json` present → the
projection an ancestor of HEAD → a size's HALTED marker → not-a-small-side →
[dry run stops here] → the host record written once (reused, checked against
a live record on every later call, refusing on mismatch) → the four units in
order (final, then the window descending) with a one-slot prefetcher
overlapping the next unit's download → `gate1_record_5b`; `main` = the CLI).
`experiments/exp5b/run/preflight_5b.py` (`run` — `check_frozen_5b` only, not
the tag (4c's rule); `twice_size`'s final loaded and scored TWICE into
sibling scratch roots under `cache_root`, compared byte-for-byte via
Experiment 5's `_compare_units`; `timed_size`'s final run whole and timed,
peak CUDA memory read via `_peak_cuda_memory`; a `root/results`
before/after snapshot via `_results_snapshot` that must be unchanged, or the
run raises). The seven shell scripts (`campaign_5b.sh`, `box_setup_5b.sh`,
`make_bundle_5b.sh`, `rebundle_box_5b.sh`, `pull_units_5b.sh`,
`commit_watcher_5b.sh`, `status_box_5b.sh`) each a copy of Experiment 5's
namesake with exactly the brief's differences applied (5b's own paths, tags,
log/grep patterns, the 38-file completeness count vs Experiment 5's 37, the
`exp5b-preregistered` refusal gate on the box side, no search-log/gate1c
pulling — 5b has neither). The thermal screen is NOT copied — Experiment 5's
`run/thermal_screen_5.py` is called directly on the box before install, as
the brief specifies. `.gitignore` gained the `# exp5b` block (fourteen
machine-local log/pid/bundle patterns, mirroring Experiment 5's).

**TDD.** RED: `~/emergence-lab/.venv/bin/python -m pytest
experiments/exp5b/tests/test_collect_5b.py experiments/exp5b/tests/test_stages_5b.py -q`
before `collect_5b.py` existed → `ImportError: cannot import name 'collect_5b'
from 'experiments.exp5b'` (test_collect_5b.py) and `ImportError: cannot
import name 'preflight_5b' from 'experiments.exp5b.run'` (test_stages_5b.py),
both at collection, as expected. GREEN: same command after Steps 3–6 → `13
passed in 7.45s`; repeated under `-W error` → identical, `13 passed`, no
warnings; the full `experiments/exp5b/tests` directory (Tasks 1–4 combined,
`-m "not slow"`) → `44 passed, 1 deselected in 29.05s` — nothing regressed.

**Byte-identity check.** `collect_5b.py`, `run/units_5b.py` and
`run/preflight_5b.py` are programmatically diffed against the brief's Step
3/4/5 code blocks: zero differences, all three IDENTICAL. The two test files
are identical to the brief's Step 1 blocks except for the leading `#
experiments/exp5b/tests/test_*.py` path-comment line, which — following
Tasks 1–3's own test files (`test_battery_5b.py`, `test_power_5b.py`, neither
carries that comment) — is a fence label, not file content, so it is omitted
on disk; confirmed this is the only difference by line-level diff.

`bash -n` on all seven `.sh` files: all seven print `OK` (`box_setup_5b.sh`,
`campaign_5b.sh`, `commit_watcher_5b.sh`, `make_bundle_5b.sh`,
`pull_units_5b.sh`, `rebundle_box_5b.sh`, `status_box_5b.sh`).

**Self-review.** Every name in the brief's Produces list exists with the
brief's signature (`reread_compare_5b`, `write_unit5b_record_5b`,
`run_unit_5b`, `gate1_record_5b`, `units_5b.run`, `preflight_5b.run` —
checked via `inspect.signature` against the brief text). `_unit_5b.json` is
written strictly after `_unit.json` (`test_run_unit_5b_writes_the_5b_record_last_and_compares_a_reread`'s
mtime assertion passes). The digest halt fires only after
`write_unit5b_record_5b` has already run — `_unit_5b.json` carries
`reread_record.digest_equal: false` when the `SystemExit` is caught in
`test_reread_digest_mismatch_halts_after_writing_the_unit`. Nothing under
`exp5_root` changes across four `run_unit_5b` calls
(`test_nothing_is_written_under_the_exp5_root`, snapshot equality via
Experiment 5's own `_results_snapshot`). Zero model contact, zero network in
any test (all fakes). No file outside the brief's Create/Modify list was
touched. Output pristine (no stray prints beyond the module's own `[5b]`/`[5b
units]`/`[5b preflight]` lines, which match the brief verbatim).

**Concerns:** none. The two open items noted in the brief ("two facts the
brief's code relies on") were honored as-is and not touched: `why` values
`"final"`/`"member"` pass through `run_unit_5` unchanged, and Experiment 5's
`_unit.json`/rung records carry `prereg_tag: "exp5-preregistered"` (Experiment
5's own tag, not 5b's) by design, per plan delta B-2.
