# Experiment 4b — build ledger

Analysis-only successor to the closed Experiment 4 (`experiments/exp4/`,
tag `exp4-closed`): re-reads Exp 4's committed bytes, builds a placebo
null. Zero model contact throughout the build.

## Task 1: `battery_4b.py` — constants, pins, paths, binding, Exp 4 record loaders

Built the foundation module every later task imports:

- `EXP4_CLOSED_SHA256_4B` — the seven files of `experiments/exp4/`
  (`__init__.py`, `analyze_4.py`, `battery_4.py`, `metric_4.py`,
  `collect_4.py`, `power_4.py`, `make_referents_4.py`) pinned to their
  content at tag `exp4-closed`. Provenance:
  ```
  for f in __init__.py analyze_4.py battery_4.py metric_4.py \
           collect_4.py power_4.py make_referents_4.py; do
    /opt/homebrew/bin/git show exp4-closed:experiments/exp4/$f | shasum -a 256
  done
  ```
  Re-run against the working tree and confirmed identical — exp4 has
  not drifted since it closed.
- `check_exp4_closed_4b()` — calls `battery_4.check_frozen_4()` first
  (the exp2*/exp3* transitive imports), then compares each of the
  seven pins against `battery_2g.sha256_file` on disk; raises naming
  every drifted file.
- `require_prereg_4b(*, tag_exists=None, blob_sha=None)` —
  `battery_4.require_prereg_4`'s body, renamed onto exp4b's own tag
  (`exp4b-preregistered`) and `INSTRUMENT_BLOBS_4B` (the five files
  Tasks 1-4 will add: `analyze_4b.py`, `battery_4b.py`,
  `placebo_4b.py`, `power_ext_4b.py`, `levels_4b.py`).
- Constants (`B_4B`, `SEED_4B`, `ALPHA_4B`, `MARGINAL_4B`,
  `MIN_PLACEBO_TOTAL_4B`, `MIN_PLACEBO_PER_TRAJ_4B`,
  `EXT_MULTIPLES_4B`, `N_SIM_EXT_4B`, `EXT_SEED_4B`,
  `N_BOOT_LEVELS_4B`, `WORLDS_4B`, `TYPES_4B`) and paths
  (`verdict_path_4b`, `verdict_txt_path_4b`, `placebo_record_path_4b`,
  `power_ext_path_4b`) for exp4b's own `results/` tree.
- Loaders over Exp 4's committed `results/`: `load_exp4_verdict_4b`
  (refuses on `INSUFFICIENT_DATA`/`NO-CONVERGENCE` or a missing
  `primary.T`), `load_exp4_eligibility_4b`, `load_exp4_power_4b`
  (record + sha256 of the file bytes), `cells_from_verdict_4b` (each
  committed cell reduced to `traj, rung, phi, t_clear, t_clear_index`,
  `t_clear_index` by grid lookup on `battery_4.GRID_4[traj]`, never
  retyped — raises on a step not on the grid), `real_design_4b` (per-
  trajectory `n`/sorted `clear_indices`/sorted `rungs`, every
  trajectory in `battery_4.TRAJECTORIES_4` present even with zero
  cells), `T_4_from_verdict_4b`.

Tests: `experiments/exp4b/tests/test_battery_4b.py`, 17 tests, all
against the real committed exp4 tree where the brief calls for it (no
model contact — file reads and one `slow`-marked real-git gate).
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest
experiments/exp4b/tests/test_battery_4b.py -p no:cacheprovider -q` →
17 passed (16 passed, 1 deselected under `-m "not slow"`).

The real-git test confirms both halves of the binding read correctly
at this point in the build: `check_exp4_closed_4b()` passes (exp4
hasn't drifted from its `exp4-closed` pin), and `require_prereg_4b()`
against real git refuses, naming `exp4b-preregistered` — the tag does
not exist yet, as expected before Task 6 freezes and tags the
instrument.
