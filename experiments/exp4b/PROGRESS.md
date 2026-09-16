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

## Task 2: `placebo_4b.py` — the placebo null, the primary, α_placebo, S2–S5, S8

Built the placebo null over in-memory series/arrays — every real-tree
loader stays Task 5's job:

- `loo_trend_4b`/`loo_excess_4b` — the leave-one-out trend/excess a
  placebo rung f is scored against (`analyze_4.excess_4`'s own formula
  called with `{f: a[f]}` and the LOO trend, never reimplemented);
  raise `ValueError` naming f when the leave-one-out pool is empty.
- `placebo_phi_4b` = `analyze_4.phi_4` unchanged.
- `placebo_se_4b` — `eligibility_table_4`'s `boot` shape verbatim
  (brief Step 3), LOO pool substituted for R; deterministic in `seed`.
- `placebo_pool_4b` — `{f: {x_end, se, eligible, excess}}` for every
  flat rung, `SE_MULTIPLE_4`-SE eligibility bar; P_M is the eligible
  subset, read off by the caller.
- `draw_batteries_4b` — the brief's battery loop verbatim, plus the
  `"P"` key (ambiguity resolution 2) and an optional externally-owned
  `rng` (falls back to `np.random.default_rng(seed)`); raises naming
  the trajectory when it has real cells but no eligible placebo rung.
- `p_cal_4b`/`t_star_4b` — the add-one-smoothed calibration and the
  calibrated lead with its placebo interval/quantiles.
- `alpha_placebo_4b` — every battery through the frozen
  `primary_4`/`verdict_tree_4` at `power_4.N_BOOT_POWER_4`; `b_alpha`
  caps the batteries scored (default every one).
- `per_traj_4b` — Exp 4's own per-trajectory T calibrated against that
  trajectory's placebo null; raises on a NaN `per_traj_mean` (a
  trajectory with real cells must never resolve to `n=0`).
- `per_type_4b` (build finding B-2) — type-restricted pools/design per
  `RUNG_TYPE_4`; a trajectory–type with real cells but no eligible
  same-type placebo rung has its design `n` zeroed for the type battery
  (so `draw_batteries_4b`'s totality raise never fires for it) while
  its true `n_real`/deficit is still printed under `feasibility`; a
  type with no real cells at all reads `None`.
- `s3_shape_4b`/`s4_scatter_ratio_4b`/`s5_autocorr_4b`/`s8_curves_4b`
  — S3 (the null's shape per (traj, c), pooled bins by c/(G−1), and
  per real cell the calibrated excess/placebo quantile), S4 (the
  rising-vs-flat increment-RMS scatter ratio), S5 (lag-1 autocorrelation
  of the flat rungs' LOO-excess increments, mean-of-rungs and pooled),
  S8 (per real cell, the placebo quantile curve of `x_r(t_i)/x_r(t_end)`
  for every grid index before the clear). **`s3_shape_4b` takes a third
  argument, `cells` (Exp 4's real cells), beyond the plan's two-argument
  interface line** — the design doc's own S3 spec (`experiment-4b-
  design.md`: "per real cell, the calibrated excess e_(M,r) = φ_obs −
  mean placebo φ at the same (M, c)") needs φ_obs off the real cell,
  which `design` (`real_design_4b`'s reduced clear-index multiset)
  does not carry; flagged for Task 5/6 to read before calling it.

Tests: `experiments/exp4b/tests/fakes_4b.py` (synthetic series/pia/
autocorrelation-world builders) + `experiments/exp4b/tests/
test_placebo_4b.py`, 27 tests, covering the brief's Step 1 (a)–(l) plus
smoke tests for `per_traj_4b`/S3/S8 not in that list. RED confirmed by
moving `placebo_4b.py` aside (`ImportError` on collection); GREEN
after restoring it:
```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp4b/tests/test_placebo_4b.py -p no:cacheprovider -q
27 passed, 2 warnings in 2.58s
```
(The two warnings are an expected `RuntimeWarning` from one deliberate
all-trajectories-infeasible edge case in a `per_type_4b` test — NaN
propagates through `p_cal_4b`/`t_star_4b` rather than crashing, which
is what that test checks.) Full `experiments/exp4b/tests/` (incl.
Task 1's, incl. the `slow` real-git gate): 44 passed.

(d)/(e)'s two calibration-world checks are genuine, seeded Monte Carlo
tests, not hand algebra: Exp 4's own R-7 finding (`FREEZE_CHECKLIST.md`)
shows the correlation between a placebo rung's pre-clear and endpoint
excess is EXACTLY ½ under pure step-independent noise (both share the
same t_1 baseline term), so the regression `E[x_pre|x_end] = x_end/2`
holds independent of the conditioning value — but the conditional
VARIANCE around that regression line does NOT shrink with |x_end|, so
individual placebo φ values near a barely-eligible x_end are wide, and
convergence to ½ is a law-of-large-numbers property of the REALIZED set
of eligible rungs, not of the battery count B. At `n_flat=30` (the
brief's own figure) this makes the check seed-sensitive: a grid search
over world seed and item-noise scale (scratch, not committed) found
`IID_WORLD_SEED=34, IID_ITEM_SIGMA=0.3` (10/30 eligible, max deviation
.0791 of the .08 bound) and `RW_WORLD_SEED=5, RW_ITEM_SIGMA=0.1`
(14/30 eligible, max deviation .050 of the .1 bound) — both fixed,
deterministic, documented in `test_placebo_4b.py`'s module-level
constants with the search method noted; no further tuning attempted
once under the stated tolerance with a comfortable-enough margin. A
`placebo_pool_4b` cost check during the search: O(n_flat²) boot() calls
— 25.6 s at a probed `n_flat=300` vs Exp 4's real `|flat| ≤ 27` (the
design's own "minutes" estimate at `n_boot=2000` over four
trajectories), so this is a property of the search's oversized probe
pools, not of the real instrument.

**Timing run (build finding B-1):** a synthetic pool at Exp 4's real
sizes (`|P| = 27/16/14/16`, design `n = 4/9/4/9`, the exact clear-index
multisets from the brief, `G = 21/21/26/24`) through
`draw_batteries_4b` (0.33 s) then `alpha_placebo_4b` at `B = 10,000`,
`n_boot = power_4.N_BOOT_POWER_4 = 200`:
```
draw_batteries_4b seconds: 0.3281691074371338
distinct rungs per battery, mean: 14.2234 max: 19
alpha_placebo_4b seconds: 32.2765109539032
```
**≈ 32 s, well under the 60-minute bar** — `B_ALPHA_4B` does not need
the cap (that pool is all-eligible with monotone excess curves, so
every battery reads LEADS; the real tree's rung mix will differ, but
the cost driver is battery/cell/bootstrap COUNT, which this probe
matches exactly). The controller rules on whether to keep
`B_ALPHA_4B = B_4B` unchanged.

### Task 2 fix round: five Important review findings

1. `loo_trend_4b` now calls `an.trend_4(a, pool, steps)` (kept the
   `"4b: "`-prefixed empty-pool check, which `trend_4` itself doesn't
   carry) instead of reimplementing the mean — it had been
   `trend_4`'s body verbatim, against the global constraint.
2. `placebo_pool_4b` now refuses (`ValueError` naming the rung) unless
   `series["a"][f][0]`/`[-1]` EXACTLY equal `pia_t1[f].mean()`/
   `pia_end[f].mean()` for every f — nothing had checked the series and
   the per-item alignment arrays came from the same checkpoint, so a
   wrong pair would silently change P_M and the whole null. New
   `fakes_4b.matching_pia` builds a consistent triple (reads back the
   pia arrays' own realized means rather than assuming a target);
   every test calling `placebo_pool_4b` was updated to use it.
3. Added `test_placebo_pool_4b_eligibility_bar_is_two_se_inclusive` —
   the `>=`-at-the-bar boundary itself had no test. **Round-2
   correction (below): this first version fixed `se` at `0.0` via
   constant pia arrays for every rung, which collapses `SE_MULTIPLE_4
   * se` to `0.0` for ANY multiple (untested) and, despite the
   docstring's claim, does NOT place `x_end` at exactly `2*se` —
   the measured value was `1.665e-16` (a hair above zero), hidden by
   `pytest.approx(0.0, abs=1e-9)`. See the round-2 entry.**
4. `per_type_4b` now refuses (`p_cal`/`T_star`/etc. all `None`, with a
   `reason`) when the type battery's null doesn't cover every
   trajectory contributing to `T_obs`, or is empty outright, detected
   BEFORE `p_cal_4b`/`t_star_4b` are called. `draw_batteries_4b`'s
   `T[b]` also gained an empty-cells guard (`float("nan")` directly,
   not `np.mean([])`) so the degenerate path is silent, not merely
   tolerated — both `RuntimeWarning`s the review found are gone,
   proven by `warnings.simplefilter("error")` in the covering test.
5. (d)/(e) rewritten as pooled-over-seeds tests
   (`_pooled_eligible_phi`, `range(60)`, never a searched seed) — the
   single-seed versions passed by seed selection (the reviewer found
   per-seed deviations from .16 to .97 against the committed .3
   item_sigma); pooling every eligible rung's phi across 60
   independent worlds gives deviations of .01–.06 (iid, bound .08) and
   .001–.03 (random-walk, bound .1) with no seed chosen. ~7.9 s each.

Covering tests: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python
-m pytest experiments/exp4b/tests/test_placebo_4b.py -p no:cacheprovider -q`
→ 29 passed, zero warnings, 17.54 s. Full `experiments/exp4b/tests/`
(incl. Task 1 + the `slow` gate): 46 passed. Fix report appended to
`.superpowers/sdd/2026-09-16-exp4b-build/task-2-report.md`.

### Task 2 fix round 2: finding 3 not addressed + a documentation defect

Round 1's eligibility-bar test fixed `se` at exactly `0.0` (every
rung's pia arrays constant), which collapses `SE_MULTIPLE_4 * se` to
`0.0` for ANY multiple — a mutant `multiple = 1.0` or `3.0` passed
every test in the file — and its "AT the bar" case did not land at
`x_end == 0.0`: the measured value was `1.665e-16` (a hair above
zero), reported honestly nowhere and instead hidden behind
`pytest.approx(0.0, abs=1e-9)`, which cannot distinguish `>=` from `>`
(a strictly-positive `x_end` clears either operator) while reading as
if it had proven the inclusive case. The docstring's "bit-for-bit, no
floating-point residual" claim was false.

Replaced with two tests:

- `test_placebo_pool_4b_eligibility_bar_pins_multiple_and_boundary` —
  f's own end-array now carries real, seeded item-level dispersion
  (`N(0, .02)`), so `se` is a genuine nonzero deterministic float,
  measured once (`se_ref`) from a reference build. Every other
  placement shifts that SAME array by a constant (changes the
  realized mean, hence `x_end`; leaves the dispersion, hence `se`,
  unchanged to floating precision) and reads the constructed pool's
  own fresh `x_end`/`se` back. Five cases: `2*se-1e-9` (ineligible),
  `2*se+1e-9` (eligible) — pin the boundary at a resolvable scale;
  `1.5*se` (ineligible under `SE_MULTIPLE_4=2`), `2.5*se` (eligible
  under 2) — pin the MULTIPLE itself; `2*se` exactly ("at") — the
  construction cannot guarantee a bit-exact hit (round-tripping a
  target through subtraction and re-subtraction of the t_1/trend terms
  is not lossless in floating point), so the residual is measured
  (`-5.75e-17` when this was written — NOT exactly zero, and its sign
  is not controllable by this construction) and the assertion is
  written against whichever side it actually lands on
  (`eligible == (residual >= 0)`), not assumed.
- `test_placebo_pool_4b_eligibility_bar_exact_equality_with_stubbed_se`
  (new) — `placebo_se_4b` is monkeypatched to return a literal `0.25`
  (a dyadic fraction, exact in float64); f's t_1, the trend, and f's
  end value are ALSO dyadic fractions, so `x_end = (1.0 - 0.25) -
  (0.5 - 0.25) == 0.5 == 2*0.25` is bit-exact — verified with `==`,
  not `approx`. This is the case the first test's "at" placement
  could not reliably produce, and it is what actually tells `>=` apart
  from `>`.

Confirmed by hand (temporarily editing the source, one mutation at a
time, then reverting): `multiple = 1.0` fails the first test's `below`
assertion (also the second test's `just_below`); `multiple = 3.0`
fails the first test's `above` assertion (also the second test's
`at`); `>` in place of `>=` fails ONLY the second (stubbed-se) test —
the first test's `at` case does not and cannot catch it, since its
residual is never exactly zero by construction, honestly documented
in both the docstring and this entry rather than claimed otherwise.

Covering tests: 30 passed (was 29 — one test added), zero warnings,
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest
experiments/exp4b/tests/test_placebo_4b.py -p no:cacheprovider -q`.
Fix report round 2 appended to
`.superpowers/sdd/2026-09-16-exp4b-build/task-2-report.md`.

## Task 3: `power_ext_4b.py` — the power-record reproduction gate and the extension arms

Built the two pieces design §3.5/§3.6 gate (4) call for:

- `reproduce_power_record_4b(root4, *, rec=None)` — `power_4.compute`
  re-run at the committed record's own `n_sim`/`seed`/`phis`, with
  `elig` read from `battery_4.eligibility_path(root4)` and
  `floors`/`battery`/`rung_sets`/`grids` built exactly as `power_4.
  main` builds them (none of those four depend on `root4` — they read
  the same real committed exp2g/2i/2m/2n bytes and `battery_4.GRID_4`
  regardless of which tree's `power_4.json` is under test), re-
  serialized with `json.dumps(reproduced, indent=1)` after setting
  `eligibility_sha256`/`prereg_tag` exactly as `main` does, and
  compared byte for byte against the FILE at `battery_4.power_path
  (root4)`. `rec=None` loads that file for its own `n_sim`/`seed`/
  `phis`; a `rec` argument overrides only what gets re-run, but
  `identical`/`committed_sha256` always refer to the file on disk
  (ambiguity resolution 1). `first_diff` is the first differing line,
  1-based, both texts truncated to 200 chars (resolution 2). Never
  writes.
- `simulate_zero_excess_scaled` — `power_4._simulate_zero_excess`'s
  body copied verbatim with the two `* scale` noise-draw sites (the
  flat-rung loop, the pool loop) replaced by `* scale_by_traj[traj]`;
  the eligibility bar stays at the unmultiplied SE (it was never
  multiplied by `scale` in the frozen original either). Returns the
  frozen arm shape plus `"Ts"` (draw-order T list, `None` dropped —
  the same list `_arm_from_counts` already reduces to `mean_T`/
  `sd_T`) and `"scale_by_traj"`; `"scatter_multiple"` is `None` (no
  single scalar when the scale is per-trajectory). A line-by-line diff
  against the frozen function (script run, not committed) confirms the
  ONLY changes are: the signature, the two `* scale` sites, the
  qualified names `power_4.N_BOOT_POWER_4`/`power_4._arm_from_counts`
  (necessary — different module), the `"4b: "`-prefixed error message,
  and the appended `scatter_multiple=None`/`Ts`/`scale_by_traj` in
  place of the frozen arm's `scatter_multiple = float(scale)`.
- `_pool_inputs_4b` — reproduces the part of `power_4.compute`'s body
  between `pool = _pool(elig)` and the end of the `trend_arr` loop
  (those three dicts are not exposed as a callable frozen helper, so
  the block is copied; `power_4._pool` itself is CALLED). Skips
  `compute()`'s empty-pool early return (never reachable from real
  `compute()` calls — production data always yields a nonempty pool,
  and `cells_4`/`verdict_tree_4` degrade to a `NO-CONVERGENCE`-only,
  zero-`mean_eligible_cells` reading on an empty `traj_info` without
  needing a special case, disclosed here rather than special-cased)
  and `cell_info`/`m_by_phi`/`construction` (phi-arms-only, not needed
  by the zero-excess arms). A second line-by-line diff against the
  corresponding `compute()` block confirms the only differences are
  the qualified `power_4._pool` call, comments trimmed (explained in
  the docstring instead), and the same `"4b: "` error-message
  re-prefixing.
- `extension_arms_4b(elig, rung_sets, grids, lambda_by_traj, *,
  multiples=EXT_MULTIPLES_4B, n_sim=N_SIM_EXT_4B, seed=EXT_SEED_4B)` —
  ONE `rng = np.random.default_rng(seed)` consumed in order:
  `"observed_lambda"` (`simulate_zero_excess_scaled` at the per-
  trajectory λ̂), then `"4.0"`/`"6.0"`/`"8.0"`/`"12.0"` (the frozen
  function at each multiple), then `"rms_lambda"` (the frozen function
  at `sqrt(mean(λ̂²))` over `lambda_by_traj`'s values) — six arms,
  `scale_index` 0..5 gapless across all of them so their bootstrap
  seeds never collide.
- `p_iid_4b(Ts, T4)` — `p_iid = (1 + #{T >= T4 - 1e-15}) / (len(Ts) +
  1)` plus the null's mean/sample SD (`ddof=1`), `None` below n=2
  (mean additionally `None` at n=0).

Tests: `experiments/exp4b/tests/test_power_ext_4b.py`, 9 tests (4
fast — `p_iid_4b`'s hand example, its exact-boundary case, and its
n=0/n=1 edges; 5 marked `slow` — the reproduction gate identical/
byte-flip/never-writes, the `simulate_zero_excess_scaled` equivalence
gate, `extension_arms_4b`'s six-arm order), against ONE module-scoped
`full_shape.build_world(root, "leads", seed=11, stage="full")` tree
(`test_full_shape_4.py`'s own shared-fixture pattern; mutating tests
work on a `shutil.copytree`). RED confirmed by moving `power_ext_4b.py`
aside (`ImportError` on collection); GREEN after restoring it:

```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp4b/tests/test_power_ext_4b.py -p no:cacheprovider -q -m "not slow"
4 passed, 5 deselected in 1.89s

PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp4b/tests/test_power_ext_4b.py -p no:cacheprovider -q -m slow
5 passed, 4 deselected in 794.43s (0:13:14)
```

The 5 slow tests' 794 s is almost entirely the ONE `stage="full"`
world build (`experiments/exp4/PROGRESS.md`'s own measured ~11
minutes for the real, full 92-point grid) shared across all five — the
reproduction gate at the world's own `n_sim=20`, the equivalence gate
at `n_sim=5`, and `extension_arms_4b` at `n_sim=20` (six arms) each
run in seconds on top of that. Full `experiments/exp4b/tests/` under
`-m "not slow"`: 50 passed in 17.90 s (Tasks 1+2's fast tests
unaffected).

**Note for Task 5**: the REAL exp4 tree's `power_4.json` was written
at `n_sim=1000` (`N_SIM_4`), not the world's `n_sim=20` — gate (4)'s
runtime against the real tree (`design §7`/dial (g)'s "if it exceeds
four hours, fall back" clause) is unmeasured here per the brief's
resolution (4) and is Task 5's job to measure.
