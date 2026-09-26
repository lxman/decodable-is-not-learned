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
