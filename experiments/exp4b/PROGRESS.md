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
resolution (4) and is Task 5's job to measure. **Measured on the
world** (n_sim=20, captured post-review — see the fix round below):
`reproduce_power_record_4b` took **0.6146 s**; a naive linear scaling
to the real tree's n_sim=1000 (~50x) puts gate (4) in the tens-of-
seconds range, well inside the four-hour bar, but Task 5 measures it
directly rather than relying on this extrapolation.

### Task 3 fix round: two Important test-power gaps (post-review)

The implementation was approved unchanged; both findings were gaps in
`test_power_ext_4b.py`'s coverage, closed with new assertions on the
SAME module-scoped `_leads_world` (no second world build):

1. **The single-stream contract was untested** — nothing distinguished
   `extension_arms_4b`'s one shared `rng`, consumed by every arm in
   order, from a refactor giving each arm its own fresh stream (which
   would still pass every prior assertion: arm names, order, `Ts`
   shape, `scatter_multiple`). Fix: `test_extension_arms_order_and_ts`
   now hand-rolls the SAME first two calls (`simulate_zero_excess_
   scaled` for `"observed_lambda"` at `scale_index=0`, then
   `power_4._simulate_zero_excess` for `"4.0"` at `scale_index=1`) on
   one fresh `default_rng(EXT_SEED_4B)`, in order, and asserts both
   equal what `extension_arms_4b` produced internally, bit for bit.
2. **The equivalence gate never exercised a heterogeneous scale** — a
   uniform `scale_by_traj = {t: 2.0 for t}` cannot distinguish
   `scale_by_traj[traj]` from a mis-keyed lookup (every plausible bug
   also reads `2.0`). Fix: new slow test
   `test_simulate_zero_excess_scaled_per_trajectory_mapping` restricts
   `pool_info`/`traj_info`/`trend_arr`/`rung_sets` to ONE real
   trajectory at a time (dict slices) and asserts `simulate_zero_
   excess_scaled({t: s})` equals the frozen function at `scale=s` for
   that trajectory's own distinct `LAMBDA_BY_TRAJ` value, across all
   four trajectories — the stronger of the two forms the review
   offered, chosen because the restricted inputs are straightforward
   dict slices (one residual, disclosed-not-live gap: a
   `next(iter(scale_by_traj.values()))`-style bug is behaviourally
   unreachable to distinguish on a single-entry map; the actual
   implementation does keyed lookups, not iterator calls, per the
   original report's line-by-line copy-fidelity diff).

Covering tests: `test_extension_arms_order_and_ts`, `test_simulate_
zero_excess_scaled_per_trajectory_mapping`, `test_reproduce_power_
record_identical` (now prints `seconds`). One combined slow run (all
six slow tests, one world build):

```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp4b/tests/test_power_ext_4b.py -p no:cacheprovider -q -m slow -s
reproduce_power_record_4b seconds (world, n_sim=20): 0.6146
......
6 passed, 4 deselected in 795.61s (0:13:15)
```

Full `experiments/exp4b/tests/` under `-m "not slow"`: `50 passed, 7
deselected in 19.56s` (7, was 6 — one new slow test added). Fix report
appended to `.superpowers/sdd/2026-09-16-exp4b-build/task-3-report.md`.

## Task 4: `levels_4b.py` — S6, the level descriptives with hidden-state 0 excluded

Built the site-family filter and the five level descriptives on top of
it, all re-derived from `experiments/exp4/`'s committed set tables
through its own frozen loaders/machinery (`analyze_4._load_one_unit_4`,
`analyze_4._load_global`, `analyze_4.trend_4`/`excess_4`/`phi_4`,
`collect_4.overlap_table_4`/`_max_over_pairs`/`load_ref_tables_4`/
`_pairing_positions`/`non_pythia_refs_4`) — none of it reimplemented:

- `kept_positions_4b(sites, excluded=an.GATE0_EXCLUDED_SITES_4)` —
  `analyze_4._gate0_kept_positions_4`'s array-position rule
  generalised to a raw site list (gate 0's version additionally
  asserts a twin/endpoint site-family match, which does not apply
  here — this module calls it once per already-loaded unit).
- `per_item_level_4b(tables_m, ref_tables, pairing_by_ref, *,
  excluded)` — `analyze_4._alignment_parts_4`'s pooled construction
  (mean over references and M's sites of overlap/k under the FIXED
  depth-matched pairing) with M's site axis filtered to
  `kept_positions_4b` before the mean, plus the `"_by_ref"` per-
  reference half; refuses when the exclusion would drop every site.
  Iterates `sorted(tables_m["sets"])` rather than `battery_4.RUNGS`
  directly (a real unit carries exactly `battery_4.RUNGS` — enforced
  upstream by `_load_one_unit_4` — so production callers see the
  real battery; a fast test can build just the rung(s) it needs).
- `level_ci_4b(vec, *, n_boot=N_BOOT_LEVELS_4B, seed=0)` — an
  item-level percentile bootstrap of `vec`'s mean.
- `ladder_4b(root4, *, excluded)` — S6(a): the Pythia size ladder
  (`analyze_4.s3_scale_4`'s per-rung structure, re-derived with the
  filter) — `a_by_size`/`ci_by_size` per rung per size, Spearman with
  log parameters, the largest single-step share, plus the global bank
  (`_ladder_global_4b`, degrading to `{"available": False, "note":
  ...}` when `global.npz` is missing for a ladder key, exactly as
  `s3_scale_4` itself degrades — ambiguity resolution 2). Carries
  `known_in_advance: True` — design §2 discloses this reading's
  headline as known to the designer before the freeze.
- `twins_4b`/`ceiling_4b`/`within_family_4b(root4, *, excluded)` —
  S6(b)/(c)/(d), each re-derived from `collect_4.load_ref_tables_4`
  rather than Exp 4's own ATTESTED `align.json` reads (`s8_referents_4`'s
  `ceiling` block is attested; this recomputes it from committed set
  tables so the site filter has array positions to act on).
  `ceiling_4b` treats one reference of each ordered pair as "M",
  filtered by its own kept positions (the pairing is re-derived via
  `collect_4._pairing_positions`, since reference units carry no
  pairing of their own — `s3_scale_4`'s own fallback). `within_family_4b`
  is `pythia_2.8b`'s sweep against `ref_pythia_12b`, point values at
  every grid step, an item-bootstrap CI only at t_1/t_end (ambiguity
  resolution 3: `ref_pythia_12b` shares Pythia's family with
  `pythia_2.8b`, so `REFS_FOR_4["pythia_2.8b"]` — cross-family only —
  excludes it, and a sweep unit's `record["pairing"]` never carries a
  `"ref_pythia_12b"` entry on a real tree; the pairing is re-derived via
  `collect_4._pairing_positions` — the `.get(ref)` direct read is kept
  as a no-op fast path only).
- `max_pair_alignment_4b(sets_m, sites_m, sets_q, sites_q, *,
  excluded)` + `max_over_pairs_4b(root4, cells, *, excluded)` — S6(e),
  the Huh max-over-pairs reading Exp 4 could not produce with site 0
  excluded (its own `series_max_pairs` reads an ATTESTED reading
  computed over the FULL site family). Per ambiguity resolution 1,
  this is the ONE place the exclusion applies to BOTH sides of the
  comparison before the full cross product is scanned (everywhere
  else in this module the fixed depth-matched pairing means only M's
  side is filtered, post-hoc, on the already-computed overlap table).
  Per real cell: the flat-rung pool's max-over-pairs series (mean over
  the trajectory's cross-family references) at every grid step builds
  the trend via `analyze_4.trend_4` (called unmodified); the cell's
  own rung reduces to excess/phi via `analyze_4.excess_4`/`phi_4`.
  Returns per cell `{"traj", "rung", "phi", "x_end", "series"}` plus
  `pooled_phi`, `n_cells`, `n_phi`, `excluded_pair_note`.

Tests: `experiments/exp4b/tests/fakes_4b.py` gained `planted_tables`
(two set tables where site 0 is IDENTICAL on both sides — alignment
exactly 1.0 — and every site i >= 1 shares exactly `round(v*k)` ids
between the two models — alignment exactly `v`, bit for bit; each
site additionally owns a private, disjoint id-universe slice, so a
CROSS-site pair reads exactly `0.0`, which is what makes "the best
KEPT pair is v" exact rather than merely likely) and `match_sets`
(a new table sharing a controllable id count with a FIXED reference
table, used by the `max_over_pairs_4b` wiring test below to vary one
side's alignment level per grid step against a reference table that
must otherwise stay fixed across the whole trajectory).

`experiments/exp4b/tests/test_levels_4b.py`, 17 tests. Step 1(a)-(c)
+ (e) are FAST, on `planted_tables`/direct-array tests (13 tests
under `-m "not slow"` incl. three `kept_positions_4b` tests, three
`per_item_level_4b` tests — excluded-equals-v, included-equals-the-
1/n-share, and a refusal when exclusion drops every site — three
`level_ci_4b` tests, three `max_pair_alignment_4b` tests on
`planted_tables` — unfiltered best pair is the degenerate (0, 0) at
1.0, filtered best pair is exactly `v`, and a direct check that an
off-diagonal cross-site pair reads exactly `0.0`). RED confirmed by
attempting to import `levels_4b` before the module existed
(`ImportError` on collection); GREEN after writing it:

```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp4b/tests/test_levels_4b.py -p no:cacheprovider -q -m "not slow"
13 passed, 4 deselected in 2.79s
```

Step 1(d) (`ladder_4b` on a `full_shape` world) is SLOW, and so —
for completeness against the brief's full Interfaces block, which
names five real-tree functions but Step 1 only tests one of them on a
tree — are `twins_4b`/`ceiling_4b`/`within_family_4b`: one
module-scoped `full_shape.build_world(..., "leads", stage="full")`
tree (`test_power_ext_4b.py`'s own pattern) shared read-only by all
four:

```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp4b/tests/test_levels_4b.py -p no:cacheprovider -q -m slow -s
4 passed, 13 deselected in 802.81s (0:13:22)
```

`max_over_pairs_4b` is deliberately NOT exercised against the world:
its full cross product (`collect_4._max_over_pairs` scans every
`(site_m, site_q)` pair, each a python-level `overlap_counts` loop
over every item) at real site counts (3-13 per `metric_4.
SITE_COUNT_PIN_4`) across a real ~21-26-step grid, ~15-27 flat rungs
and 3 references is tens of millions of python-level set-intersection
calls per trajectory — exactly why `full_shape.py` itself restricts
`compute_max_pairs=True` to one trajectory even for the single
ATTESTED reading it stores (a fact discovered by estimating the cost
before running it, not by timing out). Its wiring — the needed-rung
union, per-reference averaging, `trend_4`/`excess_4`/`phi_4`, per-cell
reduction, `pooled_phi` — is instead exercised FAST: the real
committed outcome/grid/rung-set machinery
(`battery_4.load_outcome_4`/`rung_sets_4`/`GRID_4`/`REFS_FOR_4`, all
cheap JSON reads) stays real, and only the per-unit set tables are
monkeypatched to a small `n_sites=4`/`n_items=30` size via
`match_sets`, with the cell rung's alignment rising across grid steps
against a fixed reference so `phi_4` exercises its real (non-`None`)
branch, not just the constant-series degenerate case.

Full `experiments/exp4b/tests/` under `-m "not slow"`: `63 passed, 11
deselected in 18.91s` (63, was 50 — Task 4's 13 fast tests added; 11
deselected, was 7 — Task 4's 4 slow tests added).

One deviation from the brief's Interfaces block, disclosed: an
additional function, `max_pair_alignment_4b`, factors out
`max_over_pairs_4b`'s per-(rung, step, ref) core (the exclusion +
`collect_4._max_over_pairs` call) so it is directly fast-testable on
`planted_tables` without a committed tree — the brief's own Step 1(e)
language ("`max_over_pairs_4b` on planted tables ... returns v")
describes this building block, since the top-level function's
signature (`root4, cells`) cannot itself run on raw arrays.

## Task 5: `analyze_4b.py`, `make_referents_4b.py`, `verify_referents_4b.py` — gates, tree, secondaries, verdict, `run()`, referents, cold battery

Built the whole verdict path: `analyze_4b.py` (`collect_total_4b` =
`analyze_4.collect_total_4` unchanged; `check_imports_4b` — the widened
covered set, ambiguity resolution 1; `gate1_rederive_4b`/
`gate2_rederive_4b`/`gate3_rederive_4b`/`gate5_rederive_4b` — COLD,
standalone re-derivations `run()` wraps in `collect_total_4b` and
`verify_referents_4b.py` calls directly, so the same gate logic is
never computed two different ways; `verdict_tree_4b` — cells decided
by `p_cal` only (ambiguity resolution 2); `verdict_4b`/
`write_verdict_txt_4b` — the 21-key record, the design §2 caveat
sentence verbatim; `run()` — the full refusal order (frozen ->
imports -> prereg -> referents -> exp4 verdict/eligibility/power (B-5)
-> battery/floors/outcomes/rung sets -> stage/sweep tables -> gates
1/2/3/5 -> gate 4 -> `stop_before="placebo"` early exit -> the placebo
pipeline (pools -> feasibility -> batteries -> p_cal/T*/alpha_placebo/
per_traj/per_type/S3/S4/S5/S8) -> S1 (extension arms) -> S6 (levels)
-> S7 (both Exp 4 sensitivities calibrated against the PRIMARY placebo
null, `clear_multiset_source` disclosed for (a), `mismatch_disclosed`
for (b) — ambiguity resolution 5, since `primary_clears_and_stays`'s
committed record never carries a per-cell list) -> the tree ->
`_jsonify_4` -> write); `make_referents_4b.py` (the manifest union,
`N_FILES_4B` = 7,639 — see the count derivation below); `verify_
referents_4b.py` (the 10-check `@check` battery, `DESIGN_CLEAR_
MULTISETS_4B` added to `battery_4b.py` per the carried note);
`tests/full_shape_4b.py` (`build_world_4b` = `full_shape.build_world`
+ `analyze_4.run(write=True, ...)` with `test_full_shape_4.py`'s own
stand-ins); `tests/conftest.py` gained the session-scoped
`_leads_world_4b` fixture (seed=11, exp4's own choice) shared by both
new test modules, and `fresh_copy_4b`.

**Referent manifest build (real-tree execution 1/4, a hash walk):**
`python -m experiments.exp4b.make_referents_4b` against the real,
closed exp4 tree — **7,639 files, 3.7 s** (measured twice, byte-
identical: `sha256 6f83de15ffa13ec4e78c66b1c63a4abf24dc91392bf602ba30
d5d2e85c621d36`, pinned as `analyze_4b.REFERENTS_4B_SHA256`). Count
derivation (in `make_referents_4b.py`'s own comment): 3,615 (exp4's
own referents) + 849 (reference-seal paths) + 3,312 (interior sweep-
unit files, 92 grid steps × 36) + 4 (`gate1.json`) + 5 (exp4 top-level
files) − 146 overlap (the four `STAGE1_FIRST_UNITS_4` already counted
by the interior sweep walk, 4×36=144; `eligibility_4.json`/`power_4.
json` already counted by `reference_seal_paths_4`, which appends both)
= 7,639.

**`verify_referents_4b.py` (real-tree execution 2/4, no placebo
quantity):** all 10 checks pass cold against the real tree, run twice
(before and after the gate-wiring refactor below) — `python -m
experiments.exp4b.verify_referents_4b` → `10/10`. Checks (4)/(5)/(6)/
(9) call `analyze_4b.gate1_rederive_4b`/`gate3_rederive_4b`/
`gate5_rederive_4b`/`gate2_rederive_4b` DIRECTLY (the same functions
`run()` wraps), not a second `run()` execution — printed: gate 1
T_4 = `0.6102443158323546` (bit-for-bit the design doc's own literal,
§3.3); gate 3 lambda_hat = `{comma_7b: 7.3195, olmo2_7b: 7.3043,
pythia_2.8b: 6.2345, smollm3_3b: 6.4691}` (the design's `{6.23, 6.47,
7.30, 7.32}` set, §2); gate 5 fractions `{pythia_2.8b: .9545,
olmo2_7b: .9893, smollm3_3b: .9902, comma_7b: .9911}` (the design's
own gate-(5) literal, §3.6) — every one of these numbers independently
confirms Tasks 1-4's building blocks wire together correctly.

**Real-tree execution 3/4 — `run(root4b=<tmp>, root4=battery_4.EXP4,
stop_before="placebo", write=False, tag_exists=<fake: always True>,
blob_sha=<fake: the file's own sha256>, referents_sha=REFERENTS_4B_
SHA256, imports_pinned=False, power_gate="full")`:** **86.2 s total**;
verdict `INSUFFICIENT_DATA`, reason `"4b: stopped before the placebo
null (pre-tag tool run)"`; **every one of gates 1-5 PASSES** — gate 1
T_4/cells exact (26/26), gate 2 eligibility 0 diffs, gate 3 lambda_hat
0 diffs, gate 5 fractions exact on all four trajectories, **gate 4
(the power-record reproduction) `identical=True` in 21.94 s** — dial
g's four-hour fallback (`POWER_GATE_MODE_4B = "fresh_1.0"`) is not
needed; nothing written (`write=False`; `experiments/exp4b/results/`
confirmed absent afterward).

**Real-tree execution 4/4 — `levels_4b.max_over_pairs_4b(battery_4.
EXP4, cells)` on the real committed 26 cells:** **397.74 s (6.6
minutes)**, well under the design's 30-minute concern; `n_cells=26,
n_phi=26, pooled_phi=0.6130906109635486` — a real, non-degenerate
reading (distinct from the primary's T_4=.6102, as expected: a
different site-pair construction). No restriction to a rung subset
needed.

No other execution in this task touched the real tree; every placebo
quantity (the null, the batteries, p_cal/T*/alpha_placebo, S1/S3-S5/
S7/S8) was computed ONLY on synthetic `full_shape` worlds, per B-4.

**Build finding (Task 5): `IMPLEMENTATION BUG in the test helper, not
in `run()`** — the first draft of `_run4b_kwargs()`'s `blob_sha` fake
returned `None` unconditionally, so `require_prereg_4b`'s equality
check failed on every call; masked on the fast (non-world) tests
(other failures already dominated `v["reason"]`) but fatal once the
slow gate/completion tests ran against a clean synthetic world — every
gate read `"inputs unavailable"`. Fixed by reusing `full_shape_4b.
blob_sha_4b` (the `test_full_shape_4.py` pattern: the "tag-bound" sha
IS the file's own sha) in both test files' `_run4b_kwargs()`, plus a
missing `expected_n_sim=fs.WORLD_POWER_N_SIM_4` injection for world
trees (a world's `power_4.json` is written at `n_sim=20`, not the real
campaign's 1000 — `power4.get("n_sim") != power_n_sim_expected` was
failing every world run for a second, independent reason). Confirmed
by hand: after both fixes, `stop_before="placebo"` on the shared
seed=11 world reaches every gate PASSING, matching the real tree's own
reading above.

**Build finding: the shared seed=11 "leads" world hits the design §4
feasibility floor.** Under the placebo construction's leave-one-out
2-SE eligibility bar, the seed=11 synthetic LEADS world (`conftest.
py`'s `_leads_world_4b`, exp4's own `test_full_shape_4.py` choice)
pools only **7** eligible placebo rungs across the four trajectories —
below `MIN_PLACEBO_TOTAL_4B` (8) — so exp4b's own feasibility floor
fires, correctly, reaching `INSUFFICIENT_DATA` with every one of gates
1-5 still PASSING (`test_leads_world_feasibility_floor`, renamed from
the brief's literal "leads reaches a non-INSUFFICIENT terminal"
language). This is a property of `full_shape.build_world`'s synthetic
noise construction under exp4b's placebo statistic — frozen under
`experiments/exp4/`, never edited here — not a defect in the floor or
in any gate. The "follows" world (`test_follows_world_reaches_not_
distinguishable_or_marginal`, its own fresh `stage="full"` build,
seed=3) DOES clear the floor and completes the full pipeline end to
end, reaching `NOT-DISTINGUISHABLE` at `p_cal=0.9908`, and carries
every full-completion assertion (`s1.arms` six entries, S3-S8 present,
gates 1-5 passing, `placebo_record_sha256`/`power_ext_sha256` set) —
so ambiguity resolution 6's intent (a genuinely completing world
reaching a non-INSUFFICIENT terminal) is still exercised in full, on a
different world than originally assumed.

Tests: `experiments/exp4b/tests/test_analyze_4b.py` (12 fast + 8 slow)
and `experiments/exp4b/tests/test_full_shape_4b.py` (1 fast + 3 slow).
Fast:
```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp4b/tests/ -p no:cacheprovider -q -m "not slow"
77 passed, 20 deselected in 21.04s
```
Slow (both files, one session — the "leads" world built once and
shared, "follows" built once in `test_full_shape_4b.py`):
```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp4b/tests/test_analyze_4b.py \
  experiments/exp4b/tests/test_full_shape_4b.py \
  -p no:cacheprovider -q -m slow -s
9 passed, 13 deselected in 2880.13s (0:48:00)
```
`verify_referents_4b.py` cold: `10/10`.

Real-tree executions in this task (B-4 accounted for, all four listed
above with their measurements): the referent manifest build (hash
walk); `verify_referents_4b.py` (twice, no placebo quantity); ONE
`run(stop_before="placebo")`; ONE `max_over_pairs_4b` timing. No
placebo quantity was ever computed against `battery_4.EXP4`.

### Task 5 fix round: seven Important + two promoted minors (review round 1)

Eight findings, all fixed — full detail (recipes, code, before/after)
in `task-5-report.md`'s "Fix report" section; summary here:

1. `stop_before` was unvalidated (any value but `None`/`"placebo"` ran
   the full placebo pipeline) — now raises, mirroring `power_gate`.
2. Nothing proved `stop_before="placebo"` returns BEFORE a placebo
   call, only that it left `primary` unset — a new fast test
   monkeypatches `placebo_pool_4b`/`draw_batteries_4b` to raise and
   confirms neither fires.
3. No world reached CALIBRATED/MARGINAL end to end — two new slow
   tests force `p_cal_4b`'s return (keeping `p_low`/`B` genuine) on
   the SAME shared "follows" world (no third build), reaching each
   terminal and exercising `write_verdict_txt_4b` on a live record.
4. The feasibility-floor path surfaced no per-trajectory deficits
   (`primary` stays `None` exactly there) — a top-level `feasibility`
   block is now UNCONDITIONAL (`deficit` computed by
   `draw_batteries_4b`'s own rule), merged with the AUTHORITATIVE
   `batteries["feasibility"]` once batteries are actually drawn.
5. S7(a) was calibrated against the PRIMARY null though the
   clears-and-stays cells are re-derivable (controller ruling: build
   the matched null) — three new composable functions
   (`clears_and_stays_rung_sets_4b`/`_eligibility_4b`/`_cells_4b`,
   replicating Exp 4's own `_clears_and_stays_primary` without
   reimplementing `cells_4`/`primary_4`) plus
   `clears_and_stays_design_4b` rebuild the matched design and battery
   (`seed=SEED_4B + 7`); the re-derived T is now a known-answer GATE
   against the committed `sensitivities["primary_clears_and_stays"]
   ["T"]`, bit for bit. S7(b)'s statistic extracted as standalone
   `best_site_mean_phi_4b`; `verify_referents_4b.py` gained check 11,
   the free known-answer pin (no new real-tree execution — `v4`/
   `cells4` already loaded): **measured `0.5784688004650052`** against
   the reviewer's `0.578468800465005` (matches at `1e-12`), `11/11`.
6. `VERDICT.txt` gained a Feasibility section, a combined Calibration
   section (α_placebo vs S1's α_iid/p_iid, the two nulls' mean/SD side
   by side), S3's full per-(trajectory, clear-index) table above the
   pooled bins, and `per_type[typ]["reason"]` verbatim.
7. (promoted minor) `gates["4"]` carried wall-clock `seconds` —
   stripped from the persisted record (kept: `identical`/
   `committed_sha256`/`reproduced_sha256`/`first_diff`), printed to
   stdout instead; audited every other field, nothing else
   environment-varying.
8. (promoted minor) `results/placebo.json`/`power_ext.json` renamed to
   `results/placebo_4b.json`/`power_ext_4b.json` (the plan's B-6
   naming) in `battery_4b.py`; the one test asserting the literal
   paths updated.

Re-verified: fast `79 passed, 22 deselected in ~21s`; slow (both
files, one session, two world builds — leads reused, follows built
once and shared by three tests) `11 passed, 15 deselected in
3960.83s (1:06:00)`; `verify_referents_4b.py` cold, run three times
across this round, `11/11` every time, byte-identical printed numbers.

Real-tree rule (B-4) this round: no execution touched the real tree
beyond `verify_referents_4b.py` (non-placebo, run three times); no
repeat `stop_before="placebo"` run against `battery_4.EXP4`;
`max_over_pairs_4b`'s timing was NOT re-run per instruction. Every
gate-4 timing printed this round (`0.5355s`-`0.6123s`) is from
synthetic-world runs, never the real tree.

## Task 6: totality, mutation, read sweep, import scan, determinism; the import pin

New files: `experiments/exp4b/tests/test_totality_4b.py`,
`mutation_check.py`, `read_sweep_4b.py`, `import_scan_4b.py`,
`test_determinism_4b.py`. Modified: `analyze_4b.py`
(`IMPORTED_SHA256_4B` filled), `verify_referents_4b.py` (cold check 12
added, carried item (a)), `conftest.py`/`full_shape_4b.py`/
`test_full_shape_4b.py`/`test_analyze_4b.py`/`test_placebo_4b.py`/
`test_levels_4b.py`/`test_power_ext_4b.py` (carried items (b)/(c) and
mutation-harness closures, below).

### Carried items (a)-(g) from Task 5's review

(a) Cold check 12 in `verify_referents_4b.py`: re-derives the
clears-and-stays cells via `analyze_4b.clears_and_stays_cells_4b` →
`analyze_4.primary_4(cells, n_boot=N_BOOT_4, seed=0)["T"]`, compares
bit for bit against the committed `sensitivities.
primary_clears_and_stays.T` (0.5814874459089997) — a known-answer
check, no placebo quantity, no new real-tree execution beyond the
existing `_load_real_tree` cache. **12/12 on the real tree.**

(b) The determinism fixture (`test_determinism_4b.py`) uses the
FOLLOWS world, not leads (leads hits the design §4 feasibility floor
and writes no `placebo_4b.json`): two subprocesses run `analyze_4b.
run(write=True, B=200, n_sim_ext=10, power_gate="full")` against the
SAME shared follows-world `root4` (read-only — `run()` never writes
into `root4`, only `root4b`, so no `fresh_copy_4b` needed) into two
different `root4b` tmp dirs; `verdict.json`, `placebo_4b.json` and
`power_ext_4b.json` compared byte-identical. The follows world is now
`conftest.py`'s own SESSION-scoped fixture (promoted from `test_full_
shape_4b.py`'s module-scoped one) so every slow module that needs a
completing world shares the SAME ~15-16 minute `stage="full"` build
rather than paying for its own. First run FAILED on a script bug, not
a real divergence: the subprocess script's stdout carried `run()`'s
own gate-4 wall-clock print (`"4b gate 4: power record reproduction
took {seconds}s ..."`) ahead of the verdict line, and comparing whole-
stdout text caught the (expected) wall-clock difference between the
two processes — fixed by marking the verdict line (`"DETERMINISM_
VERDICT=" + v["verdict"]`) and reading only that; the FILE comparisons
were never affected (`gates["4"]`'s own `seconds` field is stripped
before persisting). Re-run: **1/1 passed**, byte-identical.

(c) `test_stop_before_placebo_never_calls_the_placebo_functions_on_a_
real_world` added to `test_analyze_4b.py` (the fast version kept): the
fast test's empty `root4` never reaches the pools loop regardless of
`stop_before`, so it cannot distinguish "the guard wins" from "nothing
got far enough to call these functions anyway" — this one runs on the
shared LEADS world (gates all pass, the placebo-pool loop IS entered,
the design §4 floor only fires after it) and confirms the guard still
wins. Also added: feasibility-block assertions on `test_full_shape_
4b.py`'s `test_leads_world_feasibility_floor` (`floor_ok is False` +
per-trajectory keys) and on `test_follows_world_reaches_not_
distinguishable_or_marginal` (`per_traj` present, the AUTHORITATIVE
block); `_assert_full_completion` added to both forced-p_cal tests.

(d)-(e) `test_totality_4b.py`: every one of the 37 `collect_total_4b`
call sites in `run()` (AST-enumerated the same way as (g) below)
reached by a corrupted input or a monkeypatched raise — cheap
(no-world) sites (frozen check, prereg tag, referent manifest, battery
items, floors, outcome, rung sets, import-surface entry) via kwarg
injection or monkeypatching a frozen loader; pre-placebo sites needing
a real tree (torn JSON in verdict/eligibility/power, a non-numeric
`T`, an off-grid `t_clear`, a missing sweep unit, a missing reference
key, gate 1-3/5's OWN wrapper — as opposed to the perturbation tests,
which only make the gate function return `pass=False`, never raise;
the WRAPPER needs a genuine raise to be observable) on the shared
LEADS world; placebo-stage sites (draw batteries onward — no committed
file backs them, since the placebo null is computed fresh every run
with no on-disk "placebo-stage input" until it is written) via
monkeypatch-raise on the shared FOLLOWS world, one parametrized test
per site (`_FOLLOWS_SITES`) plus a dedicated test for S7's OWN
internal known-answer check (`_s7`'s `cas_T != committed_cas_T` raise,
distinct from the wrapper around the whole `_s7()` call) — S1/S6 are
stubbed to a cheap, valid shape so the test reaches S7 without paying
S1's real simulation cost or S6's real overlap recomputation.

(f) `read_sweep_4b.py`: `run(stop_before="placebo", B=10, n_sim_ext=2)`
on the real, closed exp4 tree. **7,371 distinct paths** (32,217 total
open/read calls, 0 writes): `referents_4b.json` 7,167, `frozen_module`
57, `instrument_blob` 5, `exp4_closed_module` 6, `sha_pin_at_load` 0
(exp4b's analyzer never loads a checkpoint/Hub inventory — kept for
structural parity with exp4's own sweep only), `exp4_campaign_
artifact_not_in_manifest` **0**, `python_stdlib_venv` 0, `UNPINNED`
**0**. One finding along the way, closed by adding a bucket rather
than by patching data: the FIRST sweep found 136 reads of `results/
reference/<ref>/attested/<rung>.npz` (34 rungs x 4 references) outside
every pin — `collect_4.load_ref_tables_4` (exp4's own frozen code)
unconditionally attempts this read per rung when the file exists;
`collect_4.py`'s own module docstring already discloses these files as
"sha-attested, gitignored", exp4's OWN `referents_4.json` carries ZERO
of them, `load_ref_tables_4` reads them UNCHECKED (no sha comparison,
unlike `sets`), and every one of exp4b's five call sites (`analyze_
4b.run`'s two, `levels_4b.py`'s three, `verify_referents_4b.py`'s one)
reduces the raw dict to `{ref: rt["sets"] for ...}` or reads only
`sets`/`sites`/`n_hidden`/`record` — grepped exhaustively, confirmed:
`sets_question_end`/`sets_pooled` (what `attested/*.npz` populates)
are never read anywhere in `experiments/exp4b/`. Bucketed as (i)
`gitignored_attested_unused`, disclosed rather than pinned (pinning a
gitignored file's content is incoherent — a fresh clone never has it),
leaving (f) itself at its own "should be 0".

`import_scan_4b.py`: `run(stop_before="placebo")` on the real tree,
then imports every exp4b stage tool by hand (`make_referents_4b.py`,
`verify_referents_4b.py`). **3 exp4b-own residual modules**
(`__init__.py`, `make_referents_4b.py`, `verify_referents_4b.py`) —
`IMPORTED_SHA256_4B` filled in `analyze_4b.py`; `check_imports_4b()`
verified to PASS directly, and `run(..., imports_pinned=True)`
verified to reach every gate (1-5) on the real tree without an
"unpinned module" failure. Re-run twice more (after the cold-check-12
edit, which predated the FIRST scan — no drift; and once more as the
final record) — **the hash never moved**.

### Mutation harness (`mutation_check.py`), the import pin's fill, and
### the batteries

The M list: 31 hand-authored mutants across `battery_4b.py`
(`ALPHA_4B`/`MARGINAL_4B`/`MIN_PLACEBO_TOTAL_4B`/`MIN_PLACEBO_PER_
TRAJ_4B`, `check_exp4_closed_4b`'s pin comparison, `require_prereg_
4b`'s two checks), `placebo_4b.py` (the LOO pool exclusion, the
eligibility bar, draw-with-replacement, the clear-index permutation,
α's LEADS count, `p_cal`'s add-one smoothing and `p_low`'s tolerance,
`T*`'s sign and interval), `power_ext_4b.py` (gate (4)'s byte
equality, the scaled arm's two scale sites, its own eligibility bar),
`levels_4b.py` (`kept_positions_4b`'s exclusion, `level_ci_4b`'s
percentiles), `analyze_4b.py` (the tree's two bars, the `stop_before`
guard and its early-return branch, gates 1/2/3/5's comparisons, S7's
cas gate) — plus 37 AST-generated mutants, one per `collect_total_4b`
call site in `run()` (`_totality_mutants_4b`, exp4's own `_totality_
mutants_4` with the name check changed). **68 mutants total.**

**Pass 1** (fast suite only): 21/68 killed, 47 survivors — log
`mutation_build.log`. Investigation found the survivors split into two
classes: genuine fast-suite gaps (6: #11 `draw_batteries_4b`'s
permutation, undetectable because the existing test only checks the
SET of clear indices, not their per-draw assignment; #14 `p_cal_4b`'s
`p_low` boundary, undetectable at any T4 not EXACTLY at `T4 + eps`;
#17 `reproduce_power_record_4b`'s identical flag, #18/#19/#20
`simulate_zero_excess_scaled`'s two scale sites and its eligibility
bar — all four only exercised by `test_power_ext_4b.py`'s OWN slow
suite; #22 `level_ci_4b`'s percentiles, never pinned to the literal
values; #23/#24 `verdict_tree_4b`'s two bars, never probed exactly AT
the boundary; #27-#30 gates 1/2/3/5's comparison logic, only exercised
through a full `run()`; #31 S7's cas gate, no test ever corrupted the
committed T it compares against) and totality/worlds-only sites (the
remaining ~33, all `collect_total_4b` wrapper strips whose
corresponding test lives in `test_totality_4b.py` — not part of the
FAST_TESTS list by design, exp4's own precedent, so these survive the
fast suite by construction).

**Ten new fast tests + one new slow test closed the first class**
(all in the table below); **Pass 2** (fast suite, same M list): 31/68
killed, 37 survivors — log `mutation_build_pass2.log`. Confirmed every
one of #11/#14/#17/#22/#23/#24/#27-#30 now killed; #18/#19/#20 and the
33 totality-AST + S7 survivors remain (as expected — they need a real
or cached world).

| # | Site | Closure |
|---|------|---------|
| 11 | `draw_batteries_4b` permutation | new fast test: 300 draws, first cell's `c` takes >1 distinct value |
| 14 | `p_cal_4b` `p_low` boundary | new fast test: `T_b=[1e-15], T4=0.0` — `T4+eps` hit exactly |
| 17 | `reproduce_power_record_4b` identical flag | new fast test: `power_4.compute` monkeypatched to a stub, real byte comparison |
| 22 | `level_ci_4b` percentiles | new fast test: spies on `np.percentile`, asserts `[2.5, 97.5]` was requested |
| 23/24 | `verdict_tree_4b` bars | two new parametrize cases: `p_cal` exactly `.01`/`.05` |
| 27-30 | gates 1/2/3/5 comparison logic | four new fast unit tests: gate1 hand-built series/cells (pure functions, no I/O); gate2/3/5 with the one real-file read monkeypatched to a fixed stub |
| 39 | import-surface entry (`check_imports_4b`) | new fast test: `imports_pinned=True` + monkeypatched raise (every other test uses `imports_pinned=False`, which skips this site entirely) |
| 43-46 | gates 1/2/3/5's WRAPPER (not the comparison logic) | four new slow tests on the LEADS world: the gate function itself monkeypatched to raise — the perturbation tests never make it raise, only return `pass=False`, so the wrapper strip is unobservable there |
| 31 | S7's cas gate | new slow test on the FOLLOWS world: corrupts the committed T, S1/S6 stubbed cheap so the pipeline reaches S7 without their real cost |
| 18/19 | `simulate_zero_excess_scaled` scale drop | confirmed via `test_power_ext_4b.py -m slow` (its own module-scoped LEADS world) with both mutations applied together — the two equivalence tests against the frozen reference both FAILED as expected (mean_T/sd_T/P_LEADS all diverged); reverted |
| 20 | `simulate_zero_excess_scaled` eligibility bar | **the existing slow tests do NOT catch it even in isolation** (confirmed: applied alone, `6 passed` unchanged) — a measure-zero boundary under real continuous noise; closed instead with a new PERMANENT fast test using a fixed (non-random) `.normal()` stand-in that engineers `excess[rung][-1]` to land EXACTLY on `SE_MULTIPLE_4 * se_r`, empirically verified to read `mean_eligible_cells` 1.0 (original) vs 0.0 (mutant) |
| 33 remaining totality-AST sites | `run()`'s `collect_total_4b` wrappers at every other site | `--fullshape` pass, below |

**`--fullshape` mode + world cache** (`full_shape_4b.build_world_4b`
honors `EXP4B_WORLD_CACHE=<dir>`: a `_BUILD_COMPLETE`-marked cache hit
`shutil.copytree`s the built tree and reads `v4` off its own
`verdict.json`, skipping BOTH the ~15-16 minute sweep generation AND
the `an.run()` re-derivation; unset, every existing caller is
unaffected). Cache built ONCE in the foreground (`/private/tmp/
exp4b_world_cache`, never committed): follows 936.7s, leads 925.5s;
a cache-hit re-build measured at 1.38s. `FULLSHAPE_MUTANT_TEST_4B`
maps each of the 34 remaining survivors (33 totality-AST + S7's hand
mutant) to the ONE test that targets its exact site, run via `-k`
against `test_totality_4b.py` — running the WHOLE file per mutant (as
exp4's own `--totality` does) is not affordable here the way it is for
exp4: exp4's totality base is a cheap `stage="reference_only"` tree,
exp4b's needs a COMPLETE exp4 verdict (`stage="full"`), so even cached
the full file's own test EXECUTION time (not the build) would cost
about an hour per mutant. Launched detached (`Popen(start_new_session
=True)`), polled with short `kill -0` checks, log `mutation_worlds.
log`. **CLOSED 34/34 — every mapped mutant killed, 0 survivors, 0
skips, 0 timeouts.** No stranded `.mutation_backup`; the five
instrument files verified byte-clean after every pass (the one
legitimate diff throughout: `analyze_4b.py`'s `IMPORTED_SHA256_4B`
fill).

**Tally, reconciled across the three logs:** pass 1 fast 21 killed +
pass 2 fast (after the ten-test closure) 31 killed + fullshape-cached
34 killed (of the 37 pass-2 survivors) + power_ext manual confirmation
3 (#18/#19 via the combined slow run, #20 via the new deterministic
fast test) = 31 + 34 + 3 = **68/68 killed. Zero survivors, zero
equivalent, zero open.**

**Race-condition finding, disclosed** (process, not code): editing
`analyze_4b.py` (filling `IMPORTED_SHA256_4B`) WHILE `mutation_check.
py`'s pass-1 harness was still running clobbered the edit — the
harness's own `_acquire_backup`/restore cycle captured the file's
PRE-edit content as that mutant's backup and restored it after the
mutant's test run, silently discarding the concurrent edit with no
error of any kind. Caught by chance (a later `run(..., imports_
pinned=True)` check showed `IMPORTED_SHA256_4B = None` again) rather
than by any guard — `_refuse_if_any_backup_exists()` only protects
against a SECOND harness instance, not a concurrent hand-edit of the
same file. Recovered by waiting for the harness to fully finish (no
stranded backup, file confirmed byte-clean) and re-applying the edit
once nothing else was touching the file. Lesson for future sessions:
never edit ANY of `INSTRUMENT_BLOBS_4B` while a mutation harness pass
is in flight against the same experiment, even if the edit looks
unrelated to that pass's own M list.

### Batteries, final tally

- Fast: **98 passed**, 54 deselected, `~24s` (`-m "not slow"`, whole
  `experiments/exp4b/tests/` tree).
- Slow, by file (each run standalone, `-m slow`, `-k` split where a
  file mixes LEADS- and FOLLOWS-dependent tests to avoid paying for
  both worlds in one invocation that would exceed a foreground
  budget): `test_analyze_4b.py` 7/7, `1367.81s` (0:22:47, includes the
  LEADS build); `test_full_shape_4b.py` LEADS 2/2 `1045.94s` (0:17:25,
  own build) + FOLLOWS 3/3 `2623.02s` (0:43:43, own build);
  `test_totality_4b.py` LEADS 12/12 `1175.98s` (0:19:35, world reused
  from conftest's session fixture — no rebuild) + FOLLOWS 13/13
  `2475.66s` (0:41:15, ditto); `test_determinism_4b.py` 1/1 `1969.15s`
  (0:32:49, after the stdout-comparison fix; world reused). Every
  slow test across every file: **PASS**, no flakes, no skips.
- Cold battery (`verify_referents_4b.py`, real tree): **12/12**
  (checks 1-11 unchanged from Task 5; check 12 new this task).
- Read sweep (`read_sweep_4b.py`, real tree, run 3 times across this
  task as the codebase changed): **7,371 distinct paths, (e) UNPINNED
  = 0, (f) unaccounted campaign artifact = 0** every time.
- Import scan (`import_scan_4b.py`, real tree, run 3 times): **the
  pin never moved** (`3ed5980...` for `verify_referents_4b.py` even
  across the check-12 edit, since that edit predated the first scan).
- Mutation: **68/68 killed** (21 pass-1 fast + 10 pass-2 fast
  closures/31 pass-2 fast + 34 fullshape-cached + 3 power_ext manual
  = 0 survivors); logs `mutation_build.log`, `mutation_build_pass2.
  log`, `mutation_worlds.log`, all three committed.

### Real-tree executions this task (B-4 accounted for)

Every real-tree touch used `stop_before="placebo"` (or, for `verify_
referents_4b.py`, called the cold gate-rederivation functions
directly — never `run()`'s placebo pipeline at all); **no placebo
battery or null was ever computed against `battery_4.EXP4`.** Listed:
`read_sweep_4b.py` (3 runs), `import_scan_4b.py` (3 runs, one scan
call each), two direct `check_imports_4b()`/`run(..., imports_
pinned=True)` sanity calls, `verify_referents_4b.py`'s cold battery
(2 runs, both 12/12). Gate (4)'s own power-record reproduction
(`power_4.compute` at the real `n_sim=1000`, ~22s each time) fires as
part of every one of these `run()` calls' gates 1-5 — a gate
verification, not a placebo quantity, and identical to Task 5's own
established pattern.

### Files

`experiments/exp4b/tests/test_totality_4b.py` (totality suite, **39
tests total at the end of this task's first cut** incl. the S7
known-answer-gate test — see the review-round section below for the
final count of 39 unchanged, one test's kwargs fixed), `mutation_
check.py` (the harness + `FULLSHAPE_MUTANT_TEST_4B` map), `read_
sweep_4b.py`, `import_scan_4b.py`, `test_determinism_4b.py`;
`analyze_4b.py` (`IMPORTED_SHA256_4B` filled); `verify_referents_4b.
py` (check 12); `conftest.py` (`_follows_world_4b` promoted to
session scope); `full_shape_4b.py` (`EXP4B_WORLD_CACHE` support);
`test_full_shape_4b.py`, `test_analyze_4b.py`, `test_placebo_4b.py`,
`test_levels_4b.py`, `test_power_ext_4b.py` (carried-item fixes +
mutation-harness closures). `experiments/exp4b/mutation_build.log`,
`mutation_build_pass2.log`, `mutation_worlds.log` committed (never
gitignored).

### Review round: four Important findings, fixed

A whole-branch review of this task found four issues. All four fixed;
covering tests re-run; a third fast pass and a second worlds pass
committed as logs.

**Finding 1 — the 68/68 tally was narrated, not reproducible.**
`mutation_build_pass2.log` ends at 31/68 with #18/#19/#20 surviving;
the remaining three kills were described in this file's prose (a
JOINT application of #18+#19, a fast test for #20 written after pass
2) with no log behind them, and a joint failure does not attribute a
kill to either mutant individually. Fixed: `test_simulate_zero_
excess_scaled_noise_draws_are_scaled_at_each_site` (new fast test,
`test_power_ext_4b.py`) spies on `.normal()` itself (real value
generation delegated to a genuine `np.random.Generator`, only the
`scale` ARGUMENT recorded) and asserts each of the two calls — the
flat-rung site, the pool-rung site — carries the correct `se *
scale_by_traj[traj]`; verified by hand to independently fail when
EITHER #18 or #19 is applied alone (both checked, both reverted). #20
already had its own dedicated fast test from before the review
(`test_simulate_zero_excess_scaled_eligibility_bar_is_inclusive_at_
the_boundary`) — no change needed there, just a log to show it.

**Finding 2 — nothing asserted the filled pin itself.** Every test
passes `imports_pinned=False`; the one `imports_pinned=True` test
monkeypatches `check_imports_4b` away, never exercising `IMPORTED_
SHA256_4B`'s own content. Fixed: `test_imported_sha256_4b_pin_
matches_disk_and_covers_every_residual_module` (new fast test, `test_
analyze_4b.py`) asserts (a) the pin is not `None` and every pinned
path's CURRENT `sha256_file` matches its literal, (b) the pin's key
set equals `experiments/exp4b/*.py`'s directory listing minus
`INSTRUMENT_BLOBS_4B` — a module added later without re-running
`import_scan_4b.py` now fails THIS test instead of silently existing
uncovered.

**Finding 3 — the import surface was checked at ENTRY only.** Exp 4's
own analyzer checks it twice (entry, then again at exit, "after every
secondary/sensitivity has had the chance to import something the
entry check never saw", 2j F-1); `analyze_4b.run()` lazily imports
`make_referents_4b` after the entry check and runs S1/S6/S7 later,
each of which COULD import something new. Fixed: mirrored exp4's own
exit site verbatim — `collect_total_4b(check_imports_4b if imports_
pinned else (lambda: None), "4b import surface (exit)")` inserted
right after S7, gated `if not failures:` (exp4's own rule). AST site
count: **37 → 38.** New slow test `test_import_surface_exit_check_
raise_gives_insufficient_data` (`test_totality_4b.py`, FOLLOWS world,
S1/S6 stubbed cheap as the S7 test already does) — needs a STATEFUL
monkeypatch (the entry call must succeed for real so the run reaches
the exit site at all; only the SECOND call raises). First version had
a real bug, caught by the fullshape baseline check itself (belt and
suspenders working as designed): the test's hand-written kwargs
omitted `expected_n_sim=fs.WORLD_POWER_N_SIM_4` (every OTHER test gets
this from `_run4b_kwargs()`, which this one couldn't use since it
needs `imports_pinned=True` where that helper hardcodes `False`) — the
power-record `n_sim` mismatch failed FIRST, cascading into gates 1/3/5
also failing before `not failures` was ever true, so the exit site was
never reached and the assertion failed on the WRONG reason string.
Fixed by adding the missing kwarg; re-verified against the cached
world, passes.

**Finding 4 — `--fullshape`'s kill criterion counted "no tests
collected" as a kill.** `ok = r.returncode == 0`; pytest exits 5 when
a `-k` pattern selects nothing, so a typo'd `FULLSHAPE_MUTANT_TEST_4B`
entry would read as `ok=False` (a "kill") with nothing actually run.
Fixed two ways: (1) `run_suite` now also returns `no_tests_collected`
(`returncode == 5`), routed to a NEW "SKIP" category in the tally,
never a kill; (2) `_k_selects_something` runs a `--collect-only` check
against the mapped `-k` BEFORE the mutant is ever applied — a stale
mapping value is a SKIP with a clear reason at that point, never
reaching the timed mutant run at all.

**Pass 3** (fast suite, full M list — now **69 mutants**, `mutation_
build_pass3.log`): **34/69 killed**, 35 survivors — every survivor
confirmed to be genuinely totality/worlds-only (the 33 pre-existing
`collect_total_4b` AST sites, the new exit-site AST mutant, S7's hand
mutant). Confirms #18/#19/#20 are now ALSO fast-suite kills (up from
31 in pass 2).

**`mutation_worlds_pass2.log`** (targeted `--fullshape` confirmation
for the one NEW survivor not already in `mutation_worlds.log` — the
exit-site AST mutant `totality_cf7a1c9dd6`): **1/1 killed.** (First
attempt hit the finding-3 test bug above and was discarded/re-run, not
committed — the committed log is the clean re-run.)

**Reconciled tally, every one of the 69 mutants traceable to a
committed log:**

| Source | Count | Log |
|---|---|---|
| Fast suite, pass 3 (final) | 34 killed | `mutation_build_pass3.log` |
| `--fullshape`, pass 1 | 34 killed | `mutation_worlds.log` |
| `--fullshape`, pass 2 | 1 killed | `mutation_worlds_pass2.log` |
| **Total** | **69/69 killed** | — |

Zero survivors, zero equivalent, zero open, across all 69. (`mutation_
build.log`/`mutation_build_pass2.log` are the pass-1/pass-2 fast
records superseded by pass 3 as the CURRENT fast-suite disposition;
kept committed as the build history, not re-narrated here.)

Fast suite after the review round: **100 passed**, 55 deselected
(`~25-28s`). `test_totality_4b.py` collects **39 tests: 8 fast, 31
slow** (the coordinator's own prediction of "38: 8 fast + 30 slow"
undercounted by one — the exit-site test itself; verified directly via
`pytest --collect-only`, both with and without `-m "not slow"`). No
stranded `.mutation_backup` at any point in the review round; the five
instrument files verified byte-clean except `analyze_4b.py`'s two
legitimate diffs (`IMPORTED_SHA256_4B`'s fill, the new exit-site
check).
