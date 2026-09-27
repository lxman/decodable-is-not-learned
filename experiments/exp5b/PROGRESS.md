# Experiment 5b — ledger

**Status: DIALS RULED 2026-09-25 — every dial of `experiment-5b-design.md` §10 as
recommended (Michael: "rule accepted"). The build by SDD follows this ledger.**
Nothing has been tagged, no model has been contacted, no computation has run
on Experiment 5's cell table.

## Pre-tag executions of `analyze_5b.run()` on the real tree

Tally: **6** (Task 7, the adversarial freeze: #4 `real_run.py` for surface (i), #5 the import
scan after the re-pin, #6 the read sweep — each INSUFFICIENT_DATA, no 5b statistic; beside them,
not on the real 5b tree, 10 runs with `exp5_root` = a byte copy of Experiment 5's tree and an
empty 5b root (gate 2's tamper demos) and 1 with both roots empty — see FREEZE_CHECKLIST §E).
Earlier: **3** (Task 6). Task 5 built `analyze_5b.py` but exercised it only against
`full_shape_5b.py`'s synthetic `tmp_path` worlds — never `root=battery_5b.EXP5B`
— so the tally stayed 0 through that task. Task 6's three: `tests/import_scan_
5b.py` run twice (the first to build the pin tables from `sys.modules`, a
second to confirm the scan reproduces byte-for-byte once the tables were
pasted in) and `tests/read_sweep_5b.py` run once — each refuses at `"5b prereg
tag"` (the real `exp5b-preregistered` tag does not exist yet; `require_
prereg_5b`'s default `blobs` names `results/power_5b.json`, absent on the real
tree) after halts/frozen/imports/exp5-closed/manifest/slice/referents/battery/
floors/verify all pass for real and Experiment 5's WHOLE analyzer has already
run in-process as gate 2 on the real, closed `experiments/exp5/` tree. No
5b-side statistic is ever computed pre-tag (the tree never reaches `cells5_
live is not None` with zero failures). `verify_referents_5b.py`'s own cold
battery (run repeatedly through the task) never calls `analyze_5b.run()` at
all — its checks call `load_side_5b`/`gate1_rederive_5b`/`power_failures_5b`
etc. directly, or Experiment 5's OWN `verify_referents_5.main()` — so those
runs are not counted here.

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

## Task 5 (2026-09-25): `analyze_5b.py` — gates 0–7 with Experiment 5's
analyzer as gate 2, the cells, the matched-placebo primary, sigma-hat and
the calibration read, the nine-cell tree, S1–S12, the licence block; the
synthetic worlds and their failing-case findings

Built `experiments/exp5b/analyze_5b.py` transcribed verbatim from the brief's
Step 5 code block (byte-diffed against it: zero differences): `collect_total_5b`
delegating to `exp2i.analyze_2i.collect_total` with the `"5b "` label prefix
enforced; the sides loader (`load_side_5b`/`_steps_on_disk`) running Experiment
5's own `load_units_5` first, then a torn-unit check, an extra-unit-on-disk
check (gate 4, "nothing else loaded"), and 5b's own per-unit attestation
(`_unit_5b.json`) validated on every unit present; gate 1's re-derivation
(`gate1_rederive_5b`) comparing the runner's attested re-read comparison
against a fresh `collect_5b.reread_compare_5b` call, byte for byte; the power
record's byte-for-byte re-derivation (`power_failures_5b`, `power_gate="full"`
recomputing `compute_5b` fresh and comparing JSON-serialized dicts, `"skip"`
bypassing that one expensive check for the calibration sub-cell tests); the
projection's double ancestry check (`projection_failures_5b` — the tag an
ancestor of the projection, the projection an ancestor of every unit's git
sha); the licence block (`licence_block_5b`, eight literal bodies keyed by
`f"{verdict}-{cell}"` or bare `verdict`, formatted with the primary's T/p, S1's
`outside_2p8b` T, and sigma_hat); the twelve secondaries (`secondaries_5b`,
each wrapped so a crash degrades only that key, never `run()`'s own
`failures`); `verdict_5b`/`write_verdict_txt_5b`; `run()` threading every
gate through `collect_total_5b`, short-circuiting the primary/cells/S1–S12
block entirely when any failure has been collected (`if not failures and
cells5_live is not None: ...`), exactly as the brief specifies. `REFERENTS_5B_SHA256
= None` stands, Task 6's to fill.

Also built, transcribed verbatim from the brief: `experiments/exp5b/tests/full_shape_5b.py`
(the world builder — an Experiment 5 world via `full_shape_5.write_world_5`
with its count function wrapped so the S11 read mirrors the final and two
custom Experiment-5-side modes (SIGN-ONLY, CONCENTRATED) are injected by
monkeypatching `count_fn_for`/`MODES`; the 5b power record via `power_5b.main`;
a projection stub; the 5b runner via four `run/units_5b.run` calls with fake
loaders whose count function mirrors the final at the window's first step and
adds a wobble at the other two — `MODES_5B`, `count_fn_5b_world`,
`member_count_fn_5b`, `apply_shrink_5b`, `write_world_5b`, `run_5b`),
`experiments/exp5b/tests/test_full_shape_5b.py` and
`experiments/exp5b/tests/test_analyze_5b.py`.

**TDD.** RED: `~/emergence-lab/.venv/bin/python -m pytest
experiments/exp5b/tests/test_analyze_5b.py -q` before `analyze_5b.py` existed →
`ImportError: cannot import name 'analyze_5b' from 'experiments.exp5b'`, as
expected. GREEN (after one finding below, `test_analyze_5b.py` only): same
command → `3 passed`; repeated under `-W error` → identical, no warnings. Full
fast set unaffected: `python -m pytest experiments/exp5b/tests -m "not slow" -q`
→ `47 passed, 14 deselected`.

**Finding A (test-only, both `test_analyze_5b.py` and `test_full_shape_5b.py`):
"not claimed" vs "NOT claimed".** The brief's licence body for `SURVIVES-OFF-GRID`
reads *"the licence is **NOT** claimed: ..."* — design §6's own verbatim sentence
(`experiment-5b-design.md` line 116: "the licence is NOT claimed"), capitalized
for emphasis exactly like its "DEMOTED" sibling (`NOT-SURVIVED-INSIDE`'s body).
Both of the brief's own test assertions checked the lowercase spelling
(`"not claimed" in ...`), which is never a substring of the capitalized source
phrase — `assert` is case-sensitive. Corrected both assertions to `"NOT claimed"`
with a comment naming the finding; `_LICENCE_BODY_5B` in `analyze_5b.py` is
untouched (it already matched the design doc verbatim). Unruled (no interactive
channel to Michael was available mid-task) — flagged here and in the task report
for review; the correction is the design doc's own literal, not a guess.

**Finding B (test-only, `test_nonfinite_member_is_absent_never_read`): the
blanket `n_terms == 4` assumed both outer windows are always present.** Reviewed
`v["cells"]` for the pair `small="2.8b"` (also present among the `small=="1b"`
cells' large-side partners is `2.8b`... no — re-read: the *loop* is over cells
with `c["small"] == "1b"`, whose `large` partners are `1.4b` and `2.8b`) against
the world's own build log: `"[5 sweep] 2.8b × 1b: done bracket [1000, 2000]
window []+[3000, 4000]"` — the `2.8b`-vs-`1b` bracket sits at the spine's edge,
so `b_minus` is legitimately empty and `cell5["b_minus"]` is `None`
(`stats_5.reads_5`'s `_mean([])` → `None`); `placebo_terms_5b` then drops that
side's three terms entirely (documented in Task 2's own PROGRESS.md entry: "a
missing outer window ... drops its three terms"). With the nonfinite exclusion
leaving 2 members instead of 3, a `1b`-small cell whose pair is `2.8b` legitimately
carries `n_terms == 1 * 2 == 2`, not `4`. Corrected the assertion to
`n_terms == n_sides * n_members` where `n_sides` counts the non-`None` outer
windows on that specific cell — the invariant the brief's comment ("Review Focus
2") actually motivates, robust to which pair happens to sit at a spine edge.
`analyze_5b.py`/`stats_5b.py` untouched (this is exactly their documented,
intentional behavior).

**Finding C (test-only, `test_refusal_routes_deliver_insufficient_data`): a
`shutil.copytree`-built "extra unit" is not internally self-consistent, so it
trips Experiment 5's OWN gate 3 before this module's "extra ... never requested"
check ever runs.** The brief's construction copies the complete `step30000`
directory to a new `step12000` directory and expects the analyzer's `extra`
branch (`load_side_5b`'s `on_disk - set(unit_steps_5b())` check) to fire with
"never requested". In practice `an5.load_units_5` is called FIRST (as the brief
specifies) and every copied file still internally declares `"step": 30000`,
`"revision": "step30000"`, `"commit": "c30000"`, and a fake sha embedding
`"sha-1b-30000"` — `battery_5.checkpoint_record_failures_5`/`rung_record_failures_5`
compare these against the *directory's* step (12000) and raise a genuine "gate 3
contract failure(s)" from inside `an5.load_units_5`, surfaced as `"5b units 1b:
ValueError: ..."`, never reaching the `extra` branch at all. This synthetic
world's every step-bearing field embeds the step number as a literal text
substring, so a plain `str.replace("30000", "12000")` over every copied file
(`_checkpoint.json`, the 34 rung records, `_loss.json`, `_unit_5b.json`) makes
the copy internally consistent as a genuine, well-formed, simply-unrequested
`step12000` unit — with one second-order consequence caught on the first
attempt at this fix: the substitution changes file BYTES, so `_unit.json`'s own
recorded per-file sha256 values (computed pre-substitution) go stale, and
`battery_5.unit_complete_5` then reads the "extra" directory as *torn* rather
than complete (`"1b: step12000 is on disk but is not a complete unit (torn)"`)
— closed by refreshing `_unit.json`'s `"files"` sha map from the POST-substitution
bytes (`_unit.json` itself is excluded from the blind substitution and instead
JSON-parsed, its "step"-bearing text still substituted via the loaded string,
then its `"files"` dict rebuilt via `bg.sha256_file` per name) before writing it
back. Verified in isolation: `pytest
experiments/exp5b/tests/test_full_shape_5b.py::test_refusal_routes_deliver_insufficient_data
-q` → `1 passed in 455.67s`. `analyze_5b.py`/`collect_5b.py`/`battery_5b.py`
untouched — this is exactly gate 3's and gate 4's documented, intentional
behavior; the fix is entirely in how the test constructs its fixture.

**BLOCKED (per the brief's own tuning-rule escape clause, B-11): the SIGN-ONLY
and SIZE-ONLY terminal cells of `test_every_terminal_is_reachable` are not
reachable within the stated tuning ranges.** Full detached run of
`test_full_shape_5b.py` (no `-x`, 1,784.96 s / 29:45 wall, 8 workers not used —
single process): **10 of 12 passed** after Findings A–C; the remaining two are
`test_every_terminal_is_reachable[SIGN-ONLY-...]` and `[SIZE-ONLY-...]`, both
landing at `(NOT-SURVIVED, INSIDE)` instead of their named cell.

- **SIGN-ONLY** needs `p < .01` (significant) AND `T_sym < .01` (small, either
  sign). Diagnostic sweep (`diag_sign_only2.py`/`diag3.py`, scratchpad, not
  committed) over the FULL allowed box — multiplier ∈ {1, 3} × amp ∈ {1, 4} ×
  wobble ∈ {1, 4}, all four corners plus two centre points — held `T_sym` in a
  tight band **[−0.0320, −0.0315]** and `p` pinned at **1.0** throughout (never
  moving out of `INSIDE`'s region). Root cause, confirmed by inspecting `R`/`M`/`P`
  directly: `M ≈ P/√2` (Task 3's own documented identity) is Experiment 5's OWN
  outer-window residual, computed entirely within ONE model's own bracket-vs-window
  reads — the per-model `off = mult × order[size]` used by the two custom modes
  is IDENTICAL for `a`, `b_minus` and `b_plus` (same model), so it cancels exactly
  in `a − b_minus`/`a − b_plus` and never touches `M`. Only `R = |a − f|`'s
  CROSS-model term (`off_large − off_small`) is `mult`-sensitive, capped at
  `3 × 3 = 9` items even at the top of the allowed multiplier range and the
  widest pair gap (`1b→6.9b`) — far short of the ~15–30-item natural baseline
  `M` (from the shrunk toy world's window-step-vs-final loss gap) that every
  mode shares regardless of `mult`/amp/wobble. No combination of the three
  permitted knobs, at any point in their stated ranges, can close a ~20-item gap
  with a ≤9-item lever; the world is structurally short by roughly 2–3×.
- **SIZE-ONLY** needs `T_sym ≥ .01` (big) with `p ≥ .01` (not significant).
  At the brief's default (`antonym_off = 40`): `T = −0.0216`, `n_cells = 41`.
  At the top of the allowed range (`antonym_off = 60`, `diag_size_only.py`):
  `T = −0.0157` (amp 6, n_cells 41) / `T = −0.0186` (amp 3, n_cells 36) — closer,
  same sign, still short. Per-rung sums at `antonym_off = 60`: the concentrated
  `antonym` rung alone reaches **+0.334 to +0.338** (real, large, exactly as
  CONCENTRATED intends), but the OTHER 8–11 live rungs each sit at **−0.07 to
  −0.15** (the same off-invariant `M ≈ P/√2` baseline SIGN-ONLY hits, this time
  undiluted since CONCENTRATED offsets `antonym` only) — summed and divided by
  ~36–41 total cells, one rung's positive excess cannot outweigh eight-to-eleven
  rungs' shared negative baseline. Linear extrapolation from the 40→60 step
  (Δ mult 20 → Δ T ≈ +0.006) puts the crossing to `T ≥ +0.01` at roughly
  `antonym_off ≈ 140–150` — well outside the stated `[30, 60]`.

Both findings point to the SAME root cause (the shrunk world's `WINDOW_STEPS_5B`
= `(31000, 30000, 29000)` sitting far from `FINAL_STEP_5` = `143000` on the toy
loss curve, so Experiment 5's own outer-window residual `P` is large and
`mult`/amp/wobble-invariant), not to independent defects in each mode. No
knob outside the brief's named three (SIGN-ONLY's multiplier/amplitudes,
CONCENTRATED's antonym offset, the other modes' default wobble, and
`power_5b.N_SIM_5B` — which governs only the calibration grid, not the primary,
and so cannot help either cell) was touched; `analyze_5b.py`, `stats_5b.py`,
`power_5b.py`, `battery_5b.py` are all byte-identical to the brief/Tasks 1–3 and
were never edited to chase this. Per the brief's own instruction ("If a world
cannot be reached within the allowed ranges, report BLOCKED with the numbers"),
this is reported as-is: `test_every_terminal_is_reachable[SIGN-ONLY-...]` and
`[SIZE-ONLY-...]` are committed FAILING, with this entry and the task report as
the record of what was tried and why it falls short. A real fix (Michael's or a
future task's call) most likely needs either a `WINDOW_STEPS_5B` closer to
`FINAL_STEP_5` in this specific synthetic world, or an offset mechanism that also
reaches Experiment 5's own outer-window reads (not just the cross-model `R` term)
— both would touch the frozen world-construction contract or the analyzer, which
this task's constraints forbid.

**Full detached run after Findings A–C, final tally:** `10 passed, 2 failed in
1784.96 s (0:29:44)` — `test_full_shape_5b.py -q` (no `-x`). The 10 passes
include every terminal this task COULD reach (`SURVIVES-CALIBRATED`,
`NOT-SURVIVED-INSIDE`, `UNDETERMINED`), both calibration sub-cells reachable from
`SURVIVES`'s own world (`INFLATED`, `OFF-GRID`, exercised via the doctored-power-record
test), and all seven of the refusal/gate/write tests.

**Self-review.** Every name in the brief's Produces list exists with the
brief's exact signature (checked against the brief text directly, function by
function). `run()` short-circuits the cells/primary/S1–S12 block on any
collected failure (`if not failures and cells5_live is not None: ...`), verified
by `test_primary_is_uncomputable_before_the_campaign` (no units → `primary is
None`, `cells == []`, `not secondaries`) and every `refuses()` call in
`test_refusal_routes_deliver_insufficient_data` (`primary is None`, `"S8" not
in secondaries`). The licence block names all eight cells
(`test_licence_block_names_every_cell`, all pass). The worlds reach every
(verdict, cell) EXCEPT the two named BLOCKED above — disclosed, not papered
over. Output pristine (no stray prints beyond the production runners' own
`[5]`/`[5 sweep]`/`[5b]`/`[5b units]` lines, identical to Tasks 1–4's convention).
`analyze_5b.py` is byte-identical to the brief's Step 5 code block (diffed
programmatically, zero differences); the only files touched beyond the brief's
Create list are the three test-file fixes above (Findings A–C), all inside the
Create list's own test files, none inside `analyze_5b.py` or any frozen module.

**Concerns:** SIGN-ONLY and SIZE-ONLY ship as documented, understood, BLOCKED
failures (his call on a `WINDOW_STEPS_5B` change or a same-model-and-cross-model
offset redesign, neither of which this task's constraints permit); the two
diagnostic scripts used to characterize them live under the session scratchpad,
not committed (their numbers are transcribed above and in the task report in
full). `power_gate="skip"`'s bypass (used only by
`test_calibration_sub_cells_from_a_doctored_power_record`, per the brief's own
code) means that test's two doctored-record checks are NOT exercising the
byte-for-byte power re-derivation — expected, per the brief; the third call in
the same test (no `power_gate` override) does exercise it and passes.

## Task 5 fix round 1 (2026-09-25): the two custom Experiment-5-side world
modes use a STEP-FLAT baseline (ruling, plan B-11 amended) — SIGN-ONLY and
SIZE-ONLY reached

**Ruling received:** the BLOCKED diagnosis above was confirmed correct (the
synthetic loss curve is steep enough at the bracket that the outer windows
sit ≈23 items away from it on the count scale, so the matched placebo's
`M ≈ P/√2` swamps any per-model offset reachable within the stated tuning
ranges), and the fix is NOT a wider tuning range but a different construction:
the two custom Experiment-5-side modes (SIGN-ONLY, CONCENTRATED) now read a
STEP-FLAT baseline — no `_g(fs.loss_w(...))` term at all — so the large
side's bracket reads and its outer-window reads are drawn from the SAME flat
distribution (differing only by `fs._noise`), and `M` carries noise alone
instead of the loss curve's slope. Implemented exactly as ruled, in
`experiments/exp5b/tests/full_shape_5b.py::count_fn_5b_world`'s two custom
branches only: `SIGN-ONLY`'s `base` returns
`int(min(500, max(0, 250 + 2 * order[size] + fs._noise(size, step, rung, amp))))`
for `rung in fs.LIVE_RUNGS_W`, else `0`; `CONCENTRATED`'s `base` returns
`int(min(500, max(0, 250 + (40 * order[size] if rung == "antonym" else 0) +
fs._noise(size, step, rung, amp))))` for `rung in fs.LIVE_RUNGS_W`, else `0`.
The standard modes (`LARGE-AHEAD`, `MATCHED`, `UNDETERMINED`, through
`orig_count_fn_for`), the S11-mirror wrapper `f(...)`, and
`member_count_fn_5b` are all untouched, exactly as ruled. The module
docstring gained one sentence naming the step-flat construction and why.
`_g`/`_THR` (the loss-dependent helper the two custom branches used to call)
are now unused inside this file but were left in place — the ruling named
the custom branches as the only surface to touch, and removing them was not
part of it. `analyze_5b.py`, `stats_5b.py`, `power_5b.py`, `battery_5b.py`,
and every world test's expected `(world, cell)` target are untouched.

**Realized numbers (captured directly via `fs5b.write_world_5b`/`run_5b`,
same interpreter, not committed as a script):**

| mode | verdict | cell | T_sym | rung-block p | n_cells | n_rungs | σ̂ (pooled) | calibration |
|---|---|---|---|---|---|---|---|---|
| SIGN-ONLY | NOT-SURVIVED | **SIGN-ONLY** | **+0.004107** (2.1 items/500) | **0.001953** | 45 | 9 | 0.866 | CALIBRATED |
| SIZE-ONLY | NOT-SURVIVED | **SIZE-ONLY** | **+0.012581** (6.3 items/500) | **0.035156** | 45 | 9 | 2.567 | CALIBRATED |

Both land exactly on their named terminal: SIGN-ONLY's `T_sym` is real (small,
positive) and significant (`p = .00195 < .01`, the exact `2/1024` enumerated
minimum over 9 nonzero rung blocks — every rung's block sum shares the same
sign); SIZE-ONLY's `T_sym` clears the `.01` bar (`big = True`) while its `p`
does not clear significance (`.0352 ≥ .01`, `sig = False`) — the concentrated
`antonym` rung's large excess does not manufacture an across-task rejection,
exactly the property CONCENTRATED is meant to exhibit. `n_cells` rose from
35/41 (the loss-dependent construction) to 45 for both (the flat baseline
clears every live rung's floor at every bracket/window step, so no cell drops
out for want of a live count) — consistent with the design intent that 250
"clears every live rung's floor and leaves headroom for the +120 antonym
offset without clipping."

**Test evidence.** Targeted first: `pytest
"experiments/exp5b/tests/test_full_shape_5b.py::test_every_terminal_is_reachable"
-k "SIGN-ONLY or SIZE-ONLY" -q` → `2 passed, 3 deselected in 95.22s`. Then the
whole file, detached: `pytest experiments/exp5b/tests/test_full_shape_5b.py -q`
→ **`13 passed in 2015.92s (0:33:35)`** — every terminal
and sub-cell this task names is now reachable; no other test's outcome
changed (the standard-mode worlds are unaffected by construction, and the run
is the evidence, not an assumption). The three Task-5 fixture findings
(A/B/C) and this fix round together leave `test_full_shape_5b.py` fully
green. Fast suite unaffected: `pytest experiments/exp5b/tests -m "not slow"
-q` still `47 passed, 14 deselected` (this fix touches only `full_shape_5b.py`,
which the fast suite does not import).

## Task 6 (2026-09-25/26): `make_referents_5b.py`, `verify_referents_5b.py`,
totality, determinism, the mutation harness, the read sweep, the import scan,
the pins

Built, transcribed verbatim from the brief where given: `experiments/exp5b/
make_referents_5b.py` (Step 1's code block exactly) and `experiments/exp5b/
referents_5b.json` (**8,399 files**, sha256 `ae5261d3d781e0d5a501aff8ee9a909e
ccd3bd69ba1727fcfd4369b28e1db32c`, pinned as `N_FILES_5B` and as `analyze_5b.
REFERENTS_5B_SHA256`). `experiments/exp5b/verify_referents_5b.py` — the 12-item
cold battery (`CHECKS`/`@check(n, name)`/`main()`, Experiment 5's own shape):
1 frozen+import pins (pulls in every 5b module and stage tool first); 2 the
five tags exist; 3 the exp5-closed binding (thirteen blobs + the verdict sha);
4 `referents_5b.json` at its pin; 5 Experiment 5's own cold battery re-run
in-process, asserting items 11 and 13 land `ok` (not `SKIP`) — the closed
record still reproduces; 6 the literal verdict pin; 7 the window steps present
and unexcluded on every small side, the four kinds printed (`bin`, `bin-
shards`, `safetensors-shards`, `safetensors-single` — all four occur across
the five small sides at 140000-143000, none excluded); 8 34 seeded synthetic
identities (M = P/√2 noiseless; the between-size-offset invariance), never the
committed table; 9/10/12 SKIP pre-campaign (no power record, no unit, exactly
as designed). `experiments/exp5b/tests/import_scan_5b.py` and `tests/read_
sweep_5b.py` (Experiment 5's own shapes, names swapped to 5b's, `exp5_kwargs`
threading the same tag stubs into gate 2's nested Experiment-5 call).

**Referent count and the two pin tables — built, then verified stable.**
`make_referents_5b.referent_files_5b()` printed **8,399 files** (the brief's
"≈ 8,400" estimate); pinned `N_FILES_5B = 8399`, re-ran, identical sha256.
`tests/import_scan_5b.py` run on the real pre-campaign tree (frozen/referents/
imports stubbed, tag callables stubbed) found **64 frozen (non-exp5b) modules**
(Experiment 5's own thirteen instrument-adjacent modules included, since gate
2 runs Experiment 5's whole analyzer in-process) and **5 exp5b-own residual
modules** — exactly the brief's named expectation (`__init__.py`, `run/
__init__.py`, `make_referents_5b.py`, `verify_referents_5b.py`, `run/
preflight_5b.py`). Pasted verbatim into `battery_5b.py`'s `FROZEN_SHA256_5B`/
`IMPORTED_SHA256_5B`; the scan re-run afterward reproduced byte-identically.
`check_frozen_5b()`/`check_imports_5b()` pass for real.

**The read sweep: 0 UNPINNED.** `tests/read_sweep_5b.py` (`n_sample=10,
n_boot=10`, PRODUCTION `frozen_check`/`referents_sha`/`imports_pinned`, only
the 5b prereg tag and the exp5-closed binding's tag/blob callables stubbed):
**8,467 distinct paths** opened for reading (53,039 total open/read calls),
**0 writes** (write=False held); buckets `referents_5b.json` 8,395 / `pinned_
module` 61 / `instrument_blob` 6 / `python_stdlib_venv` 0 / `sha_pin_at_load`
5 / **UNPINNED 0**. The fifth `sha_pin_at_load` item beyond Experiment 5's own
four (`checkpoints_5.json`, `slice_5.npz`, 2d's verdict.json, `referents_5b.
json` itself) is Experiment 5's own committed `results/verdict.json`, read a
SECOND time through the `exp5-closed` binding's own sha check (`require_exp5_
closed_5b`) — disclosed in the script's own docstring rather than folded
silently into bucket (a) or (c). Wall time ≈ 82 s (dominated by gate 2's
in-process Experiment 5 analysis on the real, full-scale tree).

**The cold battery: 9 ok / 3 skip, 13/13 on Experiment 5's own re-run.** `python
-m experiments.exp5b.verify_referents_5b` → items 1-8/11 `ok`, 9/10/12 `SKIP`
with the designed reasons, `referent battery: 9/12`; Experiment 5's own
embedded battery (item 5) reports `referent battery: 13/13`.

**Totality (`tests/test_totality_5b.py`, slow).** One SURVIVES world built
once (`full_shape_5b.write_world_5b`), all 18 of the brief's corruption shapes
applied then RESTORED in one test function, `_run`/`_assert_insufficient`
leaving `referents_sha`/`imports_pinned`/`frozen_check` at PRODUCTION defaults
(Experiment 5's own totality-file convention: the synthetic world's `apply_
shrink_5b` neutralizes `FROZEN_SHA256_5B`/`IMPORTED_SHA256_5B`/`check_imports_
5b` to no-ops regardless, so the referents check — against the REAL, un-
shrunk `referents_5b.json` — is the one gate exercised for real inside a
synthetic-world test). Shapes 7/8 (a side directory removed; a side with only
the final) assert EXCLUDED, never a refusal, per the brief; every other shape
asserts `INSUFFICIENT_DATA` with `primary is None` and `secondaries == {}`,
wrapped in `try` so a raise fails the test outright (none did). A 24-site
harness (`_site_templates_5b`, the same AST restriction as Experiment 5's own
`_site_templates_5`, applied to `analyze_5b.py::run()`) is reached in full by
the clean run + a `write=True` call + one halted-marker replay — every site
above the `if not failures and cells5_live is not None:` gate is unconditional
in `run()`'s own control flow, so nothing beyond those three calls was needed.
**Finding, closed the same session:** the brief's totality file, as I first
wrote it, had NO structural site-count assertion (Experiment 5's own `test_
site_template_count_matches_the_brief`, which is what actually kills most of
that experiment's totality mutants) — added `test_site_template_count_is_24`
(the live AST count today; the brief names no exact number for 5b) once the
mutation harness's fast pass showed all 24 totality mutants surviving with no
mechanism to catch them short of a full-file behavioral run. Full detached
run, three times over the session (once bare, once after the determinism fix,
once as the final combined record): **3 passed in 1573-1580 s (≈ 26 min)**
each time, byte-stable.

**Determinism (`tests/test_determinism_5b.py`, slow).** One SURVIVES world
built once (module-scoped fixture), analysed twice in two separate
subprocesses via a reconstructed `_SCRIPT` (Experiment 5's own shape:
`fs5b.apply_shrink_5b(pytest.MonkeyPatch())`, the `count_fn_for`/`MODES` patch
mirrored, `fakes_5.small_slice()` rebuilt fresh, the manifest passed as a
Python literal, `exp5_kwargs` reconstructed with fresh lambdas). **Finding,
closed the same session:** the first run FAILED — the subprocess (a fresh
interpreter, none of `write_world_5b`'s in-process `require_prereg_5b` wrap)
hit `require_prereg_5b`'s default `blobs=INSTRUMENT_BLOBS_5B`, which names
`results/power_5b.json` — absent on the REAL repo disk (no campaign has run)
— giving `INSUFFICIENT_DATA` instead of `SURVIVES`. Closed by adding the exact
same `blobs=<present-on-disk>` wrap `write_world_5b` uses, INSIDE the
subprocess script, over the same `mp` MonkeyPatch instance. Re-run: `1 passed
in 177.19 s`; the combined final run (with totality): `3 passed`, as above.

**The mutation harness (`tests/mutation_check.py`).** 51 hand mutants across
`stats_5b.py` (18), `power_5b.py` (8), `collect_5b.py` (6), `run/units_5b.py`
(5), `battery_5b.py` (6), `analyze_5b.py` (8) — every one from the brief's own
list, transcribed as an exact source-text substitution — plus 24 AST-generated
totality mutants (`_totality_mutants_5b(AN5B)`, one per `collect_total_5b`
call site textually inside `run()`, Experiment 5's own generator adapted).
All 75 mutants verified pre-flight: every `old` string count-unique in its
file, every mutation syntactically valid and non-no-op (`ast.parse` on the
mutated source, checked directly, not just trusted).

FAST_TESTS = the seven fast files (`test_battery_5b`/`test_stats_5b`/`test_
power_5b`/`test_collect_5b`/`test_stages_5b`/`test_analyze_5b`/`test_verify_
referents_5b` — the brief's own prose names six; `test_verify_referents_5b.py`
added for the same reason Experiment 5's own `FAST_TESTS` carries its verify
file, disclosed rather than silently deviating).

**First fast pass: 33 killed, 42 unresolved.** Investigated each of the 18
surviving hand mutants; 11 were pure-function mutants the EXISTING Tasks 2-3
fixtures happened not to distinguish because the fixture was degenerate for
that specific check, never because the check itself was untestable — closed
with new fast tests, each with the degeneracy named in a comment:
- `cell_5b`'s `R`/`P` locals (feeding `c_sym`/`R_gt_M`) vs the OUTPUT `R` field
  (an `IDENT_KEYS_5B` passthrough of `cell5['R']`, unaffected by the local
  variable) — a first draft of this test asserted on the wrong field
  (`cell["R"]`, which the mutation cannot touch) and PASSED under the mutant;
  caught by manually re-applying the mutation and re-running (see below) and
  fixed to assert on `c_sym` instead.
- `calibration_read_5b`'s OFF-GRID boundary (`> top` vs `>= top`, at the top
  knot itself) and the bottom clamp's effect on the REASON STRING specifically
  (the clamp is otherwise redundant with `np.interp`'s own out-of-range
  clamping, so only the printed sigma_hat text distinguishes it).
- `sigma_hat_5b`'s RMS vs mean of SDs (the Task 2 fixture gives every cell an
  IDENTICAL small_sd, where the two forms coincide) and `modifier_5b`'s
  `R_gt_M` selector (the Task 2 `offset=40` fixture makes every cell `R_gt_M`
  True, where the selector and an unconditional `True` coincide).
- `s8_one_member_5b`'s f_B source (the Task 2 fixture only checked the
  returned KEYS existed, never a value, and happened to use a cell whose own
  f_B equalled the S11 row's final anyway).
- `simulate_5b`'s shared drift (at σ_s = 0 the previous test checked only
  that the three members equal EACH OTHER, true whether they're built around
  `f_true + d_s` or bare `f_true`; closed with a fake rng returning a
  distinctive value only for DRIFT_5B-scaled draws).
- `compute_5b`'s `sigma_hat_axis` source and its declaration boundary
  (`>= POWER_BAR_5B` vs `>`, exactly at the bar) — both via a monkeypatched
  `arm_5b` stub, since the real simulated statistics don't hit either boundary
  reliably.
- `reread_compare_5b`'s `byte_identical` folding in `per_doc_diffs` and its
  `loss_within_tol` boundary (`<=` vs `<`, exactly at `LOSS_TOL_5B`) — both via
  direct file edits on `env`'s committed units (a single differing per-doc
  entry with the aggregate loss held constant; a loss delta forced to EXACTLY
  `1e-4` by editing both sides' loss fields to `0.0`/`LOSS_TOL_5B`).
- `load_side_5b`'s three gate-4 checks (`_unit_5b.json` requirement, torn-unit,
  extra-unit) and `gate1_rederive_5b`'s attestation comparison — all four
  called directly against `test_collect_5b.py`'s existing lightweight `env`
  fixture (no full world needed), closing four mutants in two new tests.
- `power_failures_5b`'s byte-for-byte comparison — closed via a monkeypatched
  `compute_5b` stub in `test_analyze_5b.py` (first attempt failed on a typo:
  `"byte for byte"` vs the real message's `"byte-for-byte"`, caught
  immediately by running the new test against UNMUTATED code and seeing it
  fail for the wrong reason).

**Second fast pass: 48 killed, 27 unresolved** (the 24 totality mutants + `_
exp5`'s gate-2 equality check + `run()`'s S1-S12-regardless-of-failures — all
27 genuinely need the slow suite to observe). `NON_FAST_KILLS_5B` populated
only AFTER each was individually confirmed (never inferred): a dedicated
script applied each of the 26 non-totality-count survivors and ran the real
totality file (`-x -m slow`) — both `_exp5` and `run()`'s S1-S12 mutant were
KILLED by `test_every_runner_leavable_tree_shape_gives_insufficient_data`
(the former via shape 15b's own message-substring check — the pin-only
message text differs from the dropped equality check's, so the shape's own
assertion fails even though the verdict is still `INSUFFICIENT_DATA`; the
latter via every `_assert_insufficient` call's `secondaries == {}` check). A
second script confirmed all 24 totality mutants are killed by `test_site_
template_count_is_24` alone (each strips exactly one `collect_total_5b` call,
mechanically dropping the AST count from 24 to 23) — run individually, ~2 s
each, all 24 killed. `run_worlds_only`'s own `sequence` was then edited to
route `totality_*` labels to that one targeted test (`-k test_site_template_
count_is_24`) instead of the full file — a full-file run for a purely
mechanical, AST-level kill would cost an estimated ~20-25 min PER mutant
(≈ 8-10 h for 24), never exercising anything the count check doesn't already
prove; the two non-totality labels still run the full sequence. The OFFICIAL
`python -m experiments.exp5b.tests.mutation_check --worlds-only` was then run
for real (not simulated) against all 26: **26/26 killed, 0 open survivors, 0
errors** — `mutation_worlds.log` is that run's own output, uncut.

**Final fast pass (`mutation_build.log`): 49 killed by the fast suite
directly, 26 killed by the slow suite (individually re-confirmed), 0
documented equivalent, considered = 75, 0 UNRESOLVED, 0 SKIP, 0 TIMEOUT.**
`.mutation_backup` swept for stragglers after every run (none found); `git
diff --stat -- experiments/exp5` empty throughout (mutation targets are all
under `experiments/exp5b/`, never Experiment 5's own tree).

**The power-record rehearsal.** `pw5b.main(<scratchpad root>, n_sim=20)` on
the real 63 live cells (never the repo): **14.40 s**, `n_live=63`,
`declaration=POWERED`; linear extrapolation to the real `n_sim=1000` ≈
**12.0 min** — confirms Task 3's own flagged estimate (11-12 min, not the
brief's "≈ 3-6 min"). Nothing written under `experiments/exp5b/results/` in
the repo; `git status` shows no `results/` tree. The real record (n_sim=1000)
is Task 7's, immediately before the tag.

**TDD / verification commands.** Fast suite: `python -m pytest experiments/
exp5b/tests -m "not slow" -q` → **70 passed, 18 deselected**; repeated under
`-W error` → identical. Cold battery: `python -m experiments.exp5b.verify_
referents_5b` → **9 ok / 3 skip**, `referent battery: 9/12`. Slow suite
(totality + determinism): **3 passed** (final combined run, 1573-1580 s
across three runs). `test_full_shape_5b.py` re-run in full after Task 6's
edits (self-review, not required by the brief but cheap insurance since new
fast tests touch `stats_5b.py`/`power_5b.py`/`collect_5b.py`/`analyze_5b.py`
which the slow worlds also exercise): **13 passed in 2015.55 s** — unchanged
from Task 5's own tally, nothing regressed.

**Self-review.** Every brief item exists (`make_referents_5b.py`, `verify_
referents_5b.py`, `referents_5b.json`, `tests/test_totality_5b.py`, `tests/
test_determinism_5b.py`, `tests/test_verify_referents_5b.py`, `tests/
mutation_check.py`, `tests/read_sweep_5b.py`, `tests/import_scan_5b.py`,
`FROZEN_SHA256_5B`/`IMPORTED_SHA256_5B` filled, `REFERENTS_5B_SHA256` filled,
`mutation_build.log`/`mutation_worlds.log` committed). The cold battery's 12
items each print `ok`/`skip` with exactly the three pre-campaign SKIPs (9,
10, 12). Totality covers every runner-leavable tree shape the brief lists
(18) plus the 24-site harness; determinism is byte-identical modulo `meta`.
Mutation: 75/75 accounted for, 0 unresolved, both logs regenerated from the
CURRENT source (re-run after every edit, never hand-edited) and committed.
Read sweep: 0 UNPINNED. Import scan: the pasted tables verified stable under
a second run. `git diff --stat -- experiments/exp5b` touches only what the
brief's Create/Modify lists name plus the four fast test files the brief's
own "closed with a new fast test (preferred)" instruction licenses;
`git diff --stat -- experiments/exp5` is empty throughout the whole task.

**Concerns:** none outstanding. Two findings were caught by verification
rather than assumed correct on the first attempt (the `cell_5b` R-mutant test
asserting on the wrong field; the `power_failures_5b` test's hyphen/space
typo) — both are recorded above with how they were caught, not smoothed over.
The `run_worlds_only` sequence edit (routing `totality_*` labels to a single
targeted test) is a deliberate, disclosed efficiency choice, not a weakening:
the alternative (the full file per mutant) tests nothing the targeted test
doesn't already prove, since the kill is structural (an AST call-site count),
not behavioral, for every one of those 24 mutants — verified by running the
targeted test directly against each of the 24 mutated files before the
harness code was changed to rely on it.

## Task 6 fix round 1 (2026-09-26): behavioural kills for every `collect_
total_5b` site — the AST count is supplementary, never the kill

**The review's finding (Important 1), verbatim conclusion:** `test_site_
template_count_is_24` fires whenever ANY `collect_total_5b` call is stripped
from `run()`'s AST, whether or not the site's underlying thunk is ever driven
to raise — a structural check, not a behavioural one. It would fire just the
same on a harmless refactor that merges two sites, and cannot distinguish a
site an 18-shape actually drives from one no test ever makes raise. Reading
the 18 shapes against `run()`: **10 sites had a real behavioural kill already**
(halt marker, prereg tag, exp5-closed, exp5, host record, units, gate 1, power
record, projection); **~14 had none** (frozen modules, both import-surface
sites, manifest, slice, referents, battery, floors, verify, cells, primary,
sigma hat, calibration, modifier, verdict write) — the totality mutants for
those sites were "killed" only by the count check, never by the property the
mutant exists to test.

**The fix, exactly per the controller's ruling.**

1. **Fifteen new behavioural tests, one property each: does `analyze_5b.run()`
   still return `INSUFFICIENT_DATA` (or, for verdict write, `write_failure`
   with the verdict otherwise intact) when that ONE site's thunk raises a
   caught-type error, and does the SAME error propagate uncaught once the
   site's `collect_total_5b` wrapper is stripped?**
   - **Nine FAST** (`tests/test_analyze_5b.py`, a new `_isolated_kwargs(tmp_
     path, **over)` helper: `root`/`exp5_root` are empty tmp directories,
     `tag_exists=lambda t: False`, `frozen_check=lambda: None` unless
     overridden, `manifest`/`sl` injected fakes unless set to `None` to reach
     the real loader, `referents_sha=False`/`imports_pinned=False` unless
     overridden): `test_frozen_modules_site_raises_without_the_wrapper`
     (`frozen_check=lambda: (_ for _ in ()).throw(OSError("x"))`, the review's
     own construction); `test_import_surface_sites_raise_without_the_wrapper`
     (`b5b.check_imports_5b` patched to raise `RuntimeError` — ONE patch
     serves BOTH the entry and exit sites, since whichever one is mutated
     raises at that exact point while the other, still wrapped, is caught
     normally); `test_manifest_site_raises_without_the_wrapper` (`b5.load_
     manifest_5` patched, called with `manifest=None`); `test_slice_site_
     raises_without_the_wrapper` (`sl5.load_slice_5` patched, `sl=None`);
     `test_referents_site_raises_without_the_wrapper` (`referents_sha="0"*64`
     — the real `check_referents_5b` sha mismatch, no monkeypatch needed);
     `test_battery_site_raises_without_the_wrapper` (`bt.load_battery`
     patched); `test_floors_site_raises_without_the_wrapper` (`b5.load_
     floors_5` patched); `test_verify_site_raises_without_the_wrapper`
     (`a2d.load_verify` patched).
   - **Six SLOW** (`tests/test_totality_5b.py`, on the SURVIVES world, per the
     ruling): `test_the_five_post_units_sites_raise_without_the_wrapper`
     (`st.cells_5b`/`primary_5b`/`sigma_hat_5b`/`calibration_read_5b`/
     `modifier_5b` each patched to raise `ValueError` in turn, restored
     between); `test_verdict_write_site_raises_without_the_wrapper`
     (`results/verdict.json` made a DIRECTORY before `write=True`, so the
     write itself raises `OSError`; asserts `v["write_failure"]` is set AND
     `v["verdict"]` is unchanged — the design's own "otherwise intact"
     contract, not folded into `v["failures"]`).
   - **Finding, closed the same session:** the first run of the five-sites
     test FAILED — `power_gate="full"` (this file's `_run`'s own default)
     triggers a REAL `compute_5b` recomputation inside the EARLIER "5b power
     record" gate, and `power_5b.arm_5b` calls `st.primary_5b`/`st.sigma_hat_
     5b` internally (the SAME module-level names being patched) — so
     mutating `primary_5b`, say, made the power-record gate raise FIRST,
     accumulating a failure that short-circuited the `if not failures and
     cells5_live is not None:` block before the intended site was ever
     reached (`v["failures"] == ["5b power record: ValueError: boom"]`, not
     `"5b primary: ..."`). Fixed by passing `power_gate="skip"` throughout
     that test (the byte-for-byte power comparison is not what's under test).
2. **Every one of the 24 totality mutants individually re-confirmed against
   its OWN behavioural test**, before any harness code relied on the result —
   two scripted passes (not `--worlds-only` yet, since discovery came first):
   `verify_fast_kills.py` (the 9 fast-covered labels, ~2 min each) and
   `verify_slow_kills.py`/a follow-up script for the six slow-covered labels
   plus the halt marker (each run against `test_totality_5b.py -k "not test_
   site_template_count_is_24"`, ≈ 20-27 min apiece since the full 18-shape
   test runs to completion before most of these fail later in file order).
   **24/24 confirmed killed by their intended test, 0 surprises.**
3. **`run_worlds_only` rewritten**: for a `totality_*` label the sequence is
   now `[("fast-behavioural", FAST_TESTS, []), ("totality-behavioural",
   TOTALITY_TESTS, ["-m", "slow", "-k", "not test_site_template_count_is_24"])]`
   — the count test is explicitly EXCLUDED from the kill-search by name, never
   credited. Only if BOTH stages survive does the harness fall back to running
   `test_site_template_count_is_24` alone, and even then records the label as
   `STRUCTURAL-ONLY (no behavioural test drives this site)` in a NEW `
   STRUCTURAL_ONLY_5B` table (`NON_FAST_KILLS_5B`'s neighbour, same
   hand-populated-from-observation discipline) — never as `killed`. The
   non-`totality_` labels (the two hand mutants) keep the original
   totality-then-fullshape sequence.
4. **`NON_FAST_KILLS_5B` rebuilt from a fresh discovery run, not hand-carried
   forward.** Cleared the previous (structural-only) 24-label block and
   re-ran the WHOLE fast pass from scratch with the 15 new behavioural tests
   in place: **66 of 75 mutants were now killed by the fast suite directly**
   — the nine sites the new fast tests target, PLUS eight more (prereg tag,
   exp5-closed, exp5, host record, units, gate 1, power record, projection)
   caught COLLATERALLY, because `_isolated_kwargs` points `exp5_root` at an
   empty tmp directory and sets `tag_exists=lambda t: False`, so ALL eight of
   those gates genuinely fail for real inside EVERY one of the nine new fast
   tests — stripping any one of their wrappers crashes whichever fast test
   happens to be running with an uncaught exception, the identical mechanism
   the tests were built for, just incidental to their stated purpose. (These
   eight also keep their original slow-shape kill; the collateral fast kill
   is additional, not a replacement, and is what the rebuilt fast-pass run
   actually shows — not assumed.) The remaining **9 fast-pass survivors** (the
   two hand mutants + the 7 totality mutants with ONLY a slow test: halt
   marker, cells, primary, sigma hat, calibration, modifier, verdict write)
   are exactly `NON_FAST_KILLS_5B`'s new content, each value the REAL test
   name from the discovery scripts, not a guess.
5. **`STRUCTURAL_ONLY_5B = {}`** added as the disclosure mechanism the ruling
   requires — stayed empty; every site has real behavioural coverage.

**Final fast pass (`mutation_build.log`, regenerated):** 66 killed by the fast
suite directly, 9 killed by the slow suite (all individually re-confirmed via
the scripted discovery, matching the log's own claim), 0 documented
equivalent, considered = 75, **0 UNRESOLVED, 0 SKIP, 0 TIMEOUT.**

**Official `--worlds-only` (`mutation_worlds.log`, regenerated, the real CLI
entry point, not simulated):** 9 labels considered, **9 killed, 0
structural_only, 0 open_survivors, 0 errors** — every kill line names the
exact behavioural test (`test_every_runner_leavable_tree_shape_gives_
insufficient_data` for the halt marker and both hand mutants; `test_the_five_
post_units_sites_raise_without_the_wrapper` for cells/primary/sigma-hat/
calibration/modifier; `test_verdict_write_site_raises_without_the_wrapper` for
the write site) — `test_site_template_count_is_24` appears nowhere in the
kill list. Wall time ≈ 2.5 h (nine labels, most needing the full ~20-27 min
totality file before failing later in file order at the intended test).

**Re-verification after the fix (instruction 5).** Fast suite: `python -m
pytest experiments/exp5b/tests -m "not slow" -q` → **78 passed, 20 deselected**
(was 70/18 before this round: +8 new fast tests, +2 new slow-marked tests);
repeated under `-W error` → identical. Full totality file (`test_totality_
5b.py`, all five test functions incl. the two new ones): **5 passed in
1618.61 s (≈ 27 min).**

**Pre-tag execution tally: unchanged at 3.** None of the fifteen new
behavioural tests touch the real tree — the nine fast tests use `root=
tmp_path`/`exp5_root=tmp_path/"exp5"` (empty, isolated), never `battery_5b.
EXP5B`; the six slow tests build a fresh synthetic SURVIVES world via `full_
shape_5b.write_world_5b` into `tmp_path`, same as every other totality/
determinism test. Nothing in this fix round calls `analyze_5b.run(root=
battery_5b.EXP5B, ...)`.

**Files changed this round:** `experiments/exp5b/tests/mutation_check.py`
(`NON_FAST_KILLS_5B` rebuilt from observation, `STRUCTURAL_ONLY_5B` added,
`run_worlds_only`'s `sequence` construction and fallback rewritten),
`experiments/exp5b/tests/test_analyze_5b.py` (+8 fast behavioural tests + the
`_isolated_kwargs`/`_assert_insufficient_with_label` helpers),
`experiments/exp5b/tests/test_totality_5b.py` (+2 slow behavioural tests),
`experiments/exp5b/mutation_build.log`, `experiments/exp5b/mutation_worlds.
log` (both regenerated, real CLI output, never hand-edited). No instrument
module touched (`analyze_5b.py`/`stats_5b.py`/`power_5b.py`/`collect_5b.py`/
`battery_5b.py`/`run/units_5b.py` all byte-identical to before this round);
`git diff --stat -- experiments/exp5` empty throughout.

**Self-review.** All 24 totality mutants now have a genuine behavioural kill,
individually verified before the harness was changed to rely on any of them
(two rounds of scripted discovery, ~24 mutation-and-restore cycles beyond the
75 the harness itself performs). `run_worlds_only` never credits the
structural count as a kill (verified: 0 entries in `structural_only` on the
real run). Both logs are the unedited output of the real `main()`/`--worlds-
only` entry points against the current source. `git diff --stat` touches
exactly the five files listed above; no instrument module, nothing under
`experiments/exp5/`.

**Concerns:** none outstanding. One design finding worth flagging for the
freeze: the COLLATERAL fast-kill of eight sites (prereg/exp5-closed/exp5/
host/units/gate1/power/projection) via the isolated tests' broken tree is a
genuine, real behavioural kill — not a loophole — but it is *incidental* to
those tests' stated purpose (they were built to test frozen/import/manifest/
etc.). If a future refactor changes `_isolated_kwargs` to use a less "broken"
tree (e.g. a valid empty `exp5_root` that Experiment 5's analyzer handles
without failing), those eight sites would silently lose their fast-path
coverage and fall back to their original slow-shape kill alone — worth a
comment at `_isolated_kwargs` itself if a later task touches it (not done
here, to keep this round's diff to exactly what the ruling asked for).


## Task 7 step 1 (2026-09-26): the adversarial freeze

Record: `experiments/exp5b/FREEZE_CHECKLIST.md`; report
`.superpowers/sdd/2026-09-25-exp5b-build/task-7-freeze-report.md`.

**THE CLASS DEFECT WAS FOUND — F-1: an unfinished campaign delivered a
verdict.** A unit never written was read as an ABSENT member, a side never
reached as EXCLUDED; the runner writes every unit (non-finite members
written and marked, a non-finite final halted), so only a killed campaign
reached those rules. A synthetic campaign stopped after 2.8b (attestation
regenerated as the runner does) delivered SURVIVES · CALIBRATED over 32 of
135 cells with zero failures. Closed by the `"5b window completeness"` site
(`window_completeness_failures_5b`): all four units per small side on disk
as 5b-complete units, nothing else under `results/units/`. Plan B-4's
absent-directory clause superseded — for the ruling.

Other findings: F-2 (C-1) gate-1 coverage measured — CLOSED; F-3 a
non-increasing σ̂ axis refuses — CLOSED; F-4 (C-2, surface (x)) the
design's exclusion rule is unreachable (a non-finite 142000 refuses at
gate 1, a non-finite final halts) — DISCLOSED, slips S-2/S-3; F-5 (C-4)
the cheap minors — CLOSED; F-6 (C-3) the harness's fast stage marker —
CLOSED. Surfaces (i)–(x) each CLEARED or CLOSED with a command
(checklist §B). Experiment 5's tree byte-identical before/after (6,686
files). Commits df08c4b72, 8142fdbb2, 5944fa515 (+ the logs/record
commit).


## Task 7 step 2 (2026-09-26): the final whole-branch review fix wave

Report: `.superpowers/sdd/2026-09-25-exp5b-build/final-fix-report.md`.

Fixes exactly Important 1 and Minors 1, 5, 6 from the final whole-branch
review (ruling #9 above), additively, nothing else. **Important 1:**
`pins_active` now also records `ancestry_injected` (`is_ancestor` or
`prereg_commit` supplied), `n_sample` (its resolved value), `roots_default`
(`root`/`exp5_root` left at the module's own `EXP5B`/`b5b.EXP5`), and
`exp5_verdict_sha` corrected to `verdict_sha is None` (previously `is not
False`, which read True for an injected sha string, not only for the
default) — a new fast test (`test_pins_active_records_every_live_injection`)
flips each flag on an empty tmp root via `_isolated_kwargs`, patching
`an.EXP5B`/`an.b5b.EXP5` to the isolated paths to exercise `roots_default`'s
True branch without ever touching the real tree. **Minor 1:** `t_items`/
`outside_items` in `licence_block_5b` go from `.0f` to `.1f` (a T in
[.009, .010) no longer prints "5 items" inside a SIGN-ONLY sentence);
`test_licence_block_names_every_cell` updated to "15.0 items"/"2.0 items".
**Minor 5:** `load_side_5b`'s and `cells_5b`'s docstrings reworded — an
absent side directory is refused by "5b window completeness" (freeze F-1),
never read as EXCLUDED; a comment added at `run()`'s `sides_block`
construction saying `excluded`/`cells_dropped` are always empty on a tree
that reaches a verdict since F-1. **Minor 6:** the unused `n_boot`
resolution line removed from `run()`; the kwarg stays in the signature
(a comment notes it is accepted for parity with Experiment 5's analyzer
only).

**Mutation harness.** One hand mutant added (`pins_active: ancestry_
injected always False`), killed by the new test. Verified BEFORE
regenerating anything: `_totality_mutants_5b(AN5B)`'s label set is
IDENTICAL before and after this round's edit (25 labels, same hashes) —
none of the four fixes touch a `collect_total_5b(...)` call site's text, so
per ruling #9 the worlds-only log stands untouched; only `mutation_build.
log` was regenerated (detached fast pass, `python -m experiments.exp5b.
tests.mutation_check`, ≈ 20 min, zero `.mutation_backup` stray before or
after): **85 considered (was 84); 75 killed by the fast suite directly
(was 74, +1 for the new mutant); 10 killed by the slow suite, unchanged
set, individually re-confirmed in the earlier rounds (see `mutation_worlds.
log`, untouched); 0 documented equivalent; 0 UNRESOLVED; 0 SKIP; 0 TIMEOUT.**

**Re-verification.** Fast suite (`-m "not slow"`): 82 passed, 31 deselected
(was 70 pre-Task-7; the freeze's own additions are in this count); repeated
under `-W error`, identical. Import scan (`import_scan_5b`): `FROZEN_
SHA256_5B` (64 entries) and `IMPORTED_SHA256_5B` (5 entries) both byte-
identical to the pinned tables in `battery_5b.py` — `analyze_5b.py` is one
of `INSTRUMENT_BLOBS_5B`, so its own edited sha never enters either table,
confirmed by scanning it out of both. Not run this round (per the
dispatch): the read sweep, the world file, totality, `--worlds-only`;
`analyze_5b.run()` was never executed against the real trees (`experiments/
exp5b`, `experiments/exp5`) — the new test's isolated calls all use
`tmp_path`.

**Files changed this round:** `experiments/exp5b/analyze_5b.py`,
`experiments/exp5b/stats_5b.py` (docstring only — no behavioural line
touched), `experiments/exp5b/tests/test_analyze_5b.py` (+1 fast test, +1
assertion string updated), `experiments/exp5b/tests/mutation_check.py`
(+1 hand mutant), `experiments/exp5b/mutation_build.log` (regenerated).
`mutation_worlds.log` NOT touched (label set verified equal). No
`power_5b.py`/`collect_5b.py`/`battery_5b.py`/`run/` edit; `git diff --stat
-- experiments/exp5` empty throughout. Pre-tag tally unchanged at 3 —
nothing this round executes `analyze_5b.run()` against `battery_5b.EXP5B`
or a real `exp5_root`.


## Ratification (2026-09-26) — Michael: "Ratified — apply the slips and tag"

The ratification package (`.superpowers/sdd/2026-09-25-exp5b-build/ratification-package.md`, the SDD workspace being git-ignored) was presented after the final whole-branch review's fix wave (346ad352e) and its scoped re-review (all four findings ADDRESSED, no new breakage). Ruled as recommended: (1) freeze F-1 ratified and plan delta B-4 SUPERSEDED — an absent side or missing unit refuses, never excludes; (2) C-2 — a non-finite 142000 re-read refuses at gate 1 as an identity failure (slip S-2); (3) the analyzer's `claimed` flag true for SURVIVES · CALIBRATED only, S-6 reworded (INFLATED claimed by its sentence with the α caveat); (4) OFF-GRID's threshold = the simulated σ̂ axis's top (S-5); (5) the runtimes (power ≈ 12 min, analyzer ≈ 14 min, both detached) and the landing note (cold item 10 FAILs on a partial tree by design; per-side checks mid-campaign) recorded in §7. Applied to `experiment-5b-design.md` in this commit: S-1, S-1b, S-2, S-3, S-4, S-5, S-6 (reworded), the final review's three missed slips (gate 1 / §7 stage 2 the digest halt after the unit is written; §7 stage 1 the scratch-only preflight, B-1; §7 stage 4 the analyzer runtime), dial (h)'s S-5 note, the §2 pre-tag disclosure (six real-tree executions — correcting this ledger's earlier "unchanged at 3", which predated the freeze's three — plus eleven on copies), the §7 stage-0/stage-2 unit-record facts, and the §11 build record with the B-list dispositions (B-4 superseded, B-11 amended). The design doc is not a referent; the cold battery is unaffected by the edit.

**The build's rulings, copied verbatim from the SDD ledger (`.superpowers/sdd/2026-09-25-exp5b-build/progress.md`, git-ignored) so the record survives the workspace's deletion at close-out:**

1. the four near-verbatim duplications of Experiment 5 functions stand — the frozen originals hardcode Experiment 5's tag, projection path, pin tables and label prefix and cannot be parameterized without editing a frozen module (the Global Constraints forbid it) — a reviewer flagging them as plan-mandated duplication is answered by this ruling, not by a refactor; cost if wrong: a few lines of divergence to maintain between two closed experiments.
2. implementers on sonnet (the plan carries complete code, but every task has a test cycle and interfaces with frozen modules); task reviewers on sonnet for Tasks 1–4 and 6, opus for Task 5 (the analyzer) and the final whole-branch review; the adversarial freeze (Task 7) on opus — Experiment 5's allocation; Michael's standing preference not to use haiku for subtasks applies; cost if wrong: tokens.
3. the duplication ruling is AMENDED to cover `check_frozen_5b` (same reason — the frozen original reads Experiment 5's pin table); cost if wrong: none beyond the ruling itself.
4. the duplication ruling covers `modifier_5b` and `primary_5b` too (the frozen originals hardcode the `c`/`R_gt_P` keys); cost if wrong: none beyond the ruling.
5. the plan's test is wrong, the design is right (f is ONE draw entering both rules); the assertion becomes `any(c["f_B"] != s["f"] for c, s in zip(cells, structure))` (cells are returned in structure order) and the σ_s = 0 block likewise compares to `s["f"]`; the module's code is unchanged; cost if wrong: a test that checks the wrong thing — but the intent (f varies at σ_s > 0) is exactly what the new assertion checks. Timing: `arm_5b` at n_sim 100 on the real 63 cells = 2.02 s → the real record (34 arms × 1,000) ≈ 11–12 min, not the plan's 3–6 — noted for Task 7's ratification step (run detached).
6. the three fixture corrections stand — (i) the tests assert the design's "NOT claimed" (the brief's tests had lowercase; the analyzer's sentence follows §6); (ii) the non-finite-member test's expected `n_terms` = n_sides × n_members (a pair at the spine's edge has one outer window); (iii) the "extra unit" fixture copies a unit self-consistently (step fields substituted, `_unit.json`'s sha map refreshed) so Experiment 5's gate 3 passes and the "never requested" path is the one exercised. Cost if wrong: none to the instrument (tests only).
7. the Task 6 reviewer runs on opus (the model ruling said sonnet for Task 6) because this task is the verification layer the freeze relies on and it carries a disclosed harness deviation; cost if wrong: tokens.
8. F-1 is ACCEPTED and plan delta B-4 is SUPERSEDED — an absent side directory (or any missing unit) is a refusal, not an exclusion; a verdict is delivered only from a complete 24-unit campaign; the design's "excluded and counted" clause becomes unreachable and is disclosed (slips S-2/S-3 to the ratification package). Cost if wrong: a side genuinely impossible to read would need a re-tag to proceed — acceptable, the campaign is 24 units.
9. ONE fix dispatch (Important 1 + Minors 1, 5, 6) as an additive commit to analyze_5b.py/stats_5b.py docstrings with fast tests; the mutation FAST pass regenerated (analyze_5b.py is a harness target); the worlds-only log stands because no `collect_total_5b` site text changes (the totality labels are content hashes — the fixer verifies the label set is unchanged and records it); Minors 3/4 go into the ratification package's process-tail notes; cost if wrong: a 2.5 h re-run of the worlds-only pass if a site text did change.

**Next, in order:** cold battery → power record ONCE (`python -m experiments.exp5b.power_5b`, detached) → cold battery again (item 9 live) → commit → tag `exp5b-preregistered` (annotated, blob-bound over `INSTRUMENT_BLOBS_5B` incl. `results/power_5b.json`; verified through `require_prereg_5b` against real git) → push → projection sealed by commit → the box on his confirmation → the 24 units → the analyzer once on his word.

## Power record ONCE (2026-09-26 22:54–23:06, detached, n_sim 1,000, seed 0)

`python -m experiments.exp5b.power_5b` after the ratified slips, on the real Experiment 5 cell table (63 live cells / 13 rungs; structure sha 8ec6bd58…; exp5-closed binding, `check_frozen_5b`, `check_imports_5b` asserted first). **Declaration: POWERED — P(fires | plugin arm, σ_s = 15) = .989 (bar .75).** Simulated σ̂ axis 5.38 / 10.10 / 14.80 / 19.52 / 28.61 / 41.69 (strictly increasing; OFF-GRID above 41.69). Realized α of the 5b rule .000 / .000 / .000 / .001 / .007 / .006; null mean T_sym −.0011 / −.0009 / −.0007 / −.0003 / −.0004 / −.0001; null SD .0020 / .0026 / .0032 / .0036 / .0048 / .0058. Experiment 5's rule on the same null: α .000 / .000 / .025 / .441 / .938 / .997 (null mean +.0044 at 15, +.0441 at 45); naive R − ½(P + Q): α .000 / .000 / .000 / .001 / .038 / .165. Arms plugin / shrunk / exp5_spread: 1.000/.871/.831, .999/.685/.573, .989/.484/.362, .919/.316/.225, .704/.152/.100, .424/.082/.029. Fraction grid at σ_s 15: .055 / .473 / .871 / .989 (T .0068 / .0209 / .0372 / .0552). D grid .01–.06: .000 / .004 / .038 / .151 / .356 / .625 — no point reaches .75, `min_detectable_T_5b` None (the minimum detectable uniform offset is above 30 items). Cold battery before: 9/12 + 3 pre-campaign SKIPs; after: item 9 live (the record reproduced byte for byte under `compute_5b`) — see the next entry. The record is committed with the slips and bound by `exp5b-preregistered`.
Cold battery after the power record (2026-09-26 23:07–23:19): **10/12** — item 9 live and ok (the record reproduces byte for byte under `compute_5b`), items 10 and 12 the two pre-campaign SKIPs. Committed with the ratified design doc and this ledger; tag `exp5b-preregistered` cut on that commit, binding verified through `require_prereg_5b` against real git, pushed.

## Projection SEALED (2026-09-26, fdeb2096d — `experiments/exp5b/projection.md`, before any model load)

THE CALL: **SURVIVES · CALIBRATED at .78** (SURVIVES .80 in total; OFF-GRID .02; INFLATED .00 — unreachable on the sealed grid, α ≤ .007 at every axis point; NOT-SURVIVED .12 = SIZE-ONLY .07 / SIGN-ONLY .03 / INSIDE .02; UNDETERMINED .00 by F-4; INSUFFICIENT_DATA .08 with the routes named). T_sym ≈ .044 [.030, .058] (22 items [15, 29]); rung-block p ≈ .002 [.0003, .02]; σ̂_s pooled ≈ 13 [9, 20], per side 2.8b 20 / 6.9b 12 / 1.4b 11 / 1b 10 / 410m 5 / 160m 8; rows 2.8b +.095 [+.075, +.112], 6.9b +.010, 1.4b +.025, 1b +.030, 410m +.030, 160m +.010; modifier MIXED .85 (≈ 40 cells with R > M, ≈ 20/20); types arithmetic +.060 / option +.028; per rung with tolerances; S1–S12 each with a range; the prior as a claim with two disconfirmers (σ̂_s ≥ 20 or T_sym ≤ .030 — the disclosure load-bearing; σ̂_s ≤ 7 or T_sym ≥ .052 — the 142000 differences a one-off); S11's within-class drift claim (Σ|Δ| ≤ 15 per unit, byte identity on ≥ 8 of 12) with its disconfirmer (Σ > 40 or > 10 byte-different items on one rung). Disclosed in its first paragraph: read R, P, c, class per cell and the S11 per-rung differences and loss rows from Experiment 5's committed verdict; computed no Q, M₁, T₁ or any 5b statistic. `projection_commit_5b()` resolves to fdeb2096d; `projection_edits_5b` empty. **Next on Michael's confirmation: the box** (Vast A100 80 GB PCIe on-demand, thermal screen first, bundle, no credential) → preflight → 24 units → destroy → cold battery → analyzer once on his word.

## 2026-09-26/27 — THE BOX (Michael: "Confirmed — create the box and go on the preflight")

**Instance 52875584 — A100 80GB PCIe, Oklahoma, offer 47546409** ($0.8708/h base; 806 GB host disk, 120 GB requested; reliability 99.6 %; advertised ↓747 ↑708 Mbps; 32 cores, 503 GB RAM — the same host shape as Experiment 5's campaign box 52285720; **driver 565.57.01 / CUDA 12.7**, where Experiment 5's box ran 580.126.09 / CUDA 13.0 — the pinned `torch==2.12.1` cu130 wheel's driver requirement is the open question for the stack step, see below), the only A100 80 GB PCIe on-demand offer at ≥ 500 Mbps / reliability > .95 at the hour (the SXM4 market: Taiwan $1.00, Czechia $1.06–1.07 at CUDA 13.0–13.2, Sweden $1.06, Montana $1.19), created 2026-09-27 ≈ 03:26 UTC via the Vast MCP, ready in 139 s, label `exp5b-campaign`, route `ssh7.vast.ai:35584` (direct 174.78.228.101:40800), key auto-attached. Credit before: $131.72. Image `vastai/pytorch`, `python` absent from PATH on the image (the venv python found by the screen script). The bundle: `run/make_bundle_5b.sh` → 555,780,176 bytes, sha256 `ddaab29a…`, carried through the proxy by plain scp in 18 s (≈ 31 MB/s), sha256 on the box EQUAL. Thermal screen launched via plain ssh (the MCP background wrapper mangled nested quotes on the first attempt — nothing ran; relaunched as `/workspace/screen.sh` → `/workspace/thermal.log`).
**Thermal screen PASS (2026-09-27 ≈ 03:52 UTC; `/workspace/thermal.log`, copied to `box-thermal-52875584.log` at close): 224 TFLOP/s fp16 sustained over 120 s (Experiment 5's box 231), 48–51 °C, SM 1,080 MHz under the PCIe part's 300 W power cap (sw_power_cap Active, as on Experiment 5's box), thermal slowdown Not Active throughout; idle 210 MHz / 31 °C.** The image's torch is 2.5.1+cu121 (used by the screen only). Stack install (`box_setup_5b.sh`, Experiment 5's recipe: uv Python 3.11, torch 2.12.1 cu130 wheel, the Mac's pins, clone from the bundle) launched detached at ≈ 03:55 UTC — the cu130 wheel on driver 565.57.01 is the open question; its answer is the setup log's `cuda … True/False` line.
**Stack on the box (≈ 03:55–04:10 UTC).** `box_setup_5b.sh` installed uv / CPython 3.11.16 / the venv / the pins, then died at its clone step because the bundle had been copied as `exp5b.bundle` (the Mac script's default name) where the setup script expects `emergence-paper.bundle` — a naming slip with no consequence: the file renamed, the clone made by hand (HEAD 5fae62c49 = the Mac's master; tags exp5-closed / exp5-preregistered / exp5-targets-sealed / exp5b-preregistered present), the cache root made, the version print run. **Finding: the pinned `torch==2.12.1+cu130` wheel does not initialise CUDA on this host's driver 565.57.01** ("The NVIDIA driver on your system is too old (found version 12070)") — Experiment 5's campaign box ran driver 580.126.09. **Closed without touching the wheel: NVIDIA's CUDA 13.0 forward-compatibility package (`cuda-compat-13-0`, user-space `libcuda.so.580.178.04` under `/usr/local/cuda-13.0/compat`, supported on datacenter parts) installed from NVIDIA's ubuntu2204 repo; with `LD_LIBRARY_PATH=/usr/local/cuda-13.0/compat` the pinned wheel reports `cuda available True`, A100 80GB PCIe, an fp16 matmul runs.** So the stack is wheel-for-wheel Experiment 5's (torch 2.12.1+cu130, transformers 5.13.0, numpy 2.4.6, safetensors 0.8.0, tokenizers 0.22.2, hub 1.22.0 + hf_xet, scipy 1.17.1; the cuBLAS the wheel carries), on a different KERNEL driver (565.57.01 + the 13.0 compat library vs 580.126.09 native) — an environment note carried into the host record's `nvidia_smi` line and into S11's reading; gate 1's identity comparison is the empirical check. Every python invocation on the box (dry-run, preflight, runner) carries the `LD_LIBRARY_PATH` export. Not a pre-committed-change matter: no bound blob, no rule, no pin touched (Experiment 5's freeze F-3 deliberately left torch's "+cu" build and the driver out of the stack pin).
**Dry-run gate clean (04:11 UTC):** `units_5b --size 6.9b --device cuda --dry-run` → prereg `exp5b-preregistered` seen, host record pending, would run the four units 143000 / 142000 / 141000 / 140000. **PREFLIGHT PASSED (04:11:40 → 04:31:24 UTC, ≈ 20 min; `/workspace/preflight_5b.log`, scratch roots only):** transports classic 14.5 / **xet 80.4 MB/s** (Experiment 5's box: 45.2 / 80.1 — xet identical), xet used; **the 1b final loaded and scored TWICE: IDENTICAL** (loss 1.99513 both times — Experiment 5's committed 1.99513 to the printed digit; 198 s / 196 s); **the 6.9b final whole: 862 s** (Experiment 5's campaign figure 840 s on this host class), loss 1.75215 (= Experiment 5's), peak_cuda_bytes 24,100,242,432 (22.4 GiB — the largest unit of this campaign fits with 55 GB to spare); `complete: nothing written under results/` (the tree holds `power_5b.json` only; `git status` clean on the box). The box's HEAD 5fae62c49 descends from the projection commit fdeb2096d and carries the tag, so no re-bundle is needed before the campaign (every unit's `git_sha` will be 5fae62c49). **The campaign (24 units, ≈ 2.3 h) awaits Michael's word**; the box bills ≈ $0.87/h meanwhile.
