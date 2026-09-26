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
