# Experiment 7 — Independent Review of `CALIBRATION-1` (`cdaf141a4380`), `FREEZE-1-world-fixture` (`73f8ba2de223`), & Pre-Tag Calibration Archive `calibration-001` (`d20b633b5432`)

- **Audited Amendment Commit (`CALIBRATION-1`)**: `cdaf141a438002b5d84719c732f9a68329305ca9`
- **Audited Calibration Archive Commit**: `d20b633b54324936a00b03ced2ba64a5a26cc114`
- **Audited World-Fixture Amendment Commit (`FREEZE-1-world-fixture`)**: `73f8ba2de2230cf9f3476ac6fa0cf83014a82355` (ruling documented at `7e792d16d7e4b12f05db552530eabe869b88f399`)
- **Host / Interpreter**: Darwin arm64, `/Users/michaeljordan/emergence-lab/.venv/bin/python -I -B -X int_max_str_digits=5000` (CPython `3.11.15`)
- **Disposition**: `ACCEPT` (`open_defects: 0`, `calibration_1_amendment_accepted: true`, `freeze_1_world_fixture_accepted: true`, `accepted_calibration_archive_verified: true`)

---

## 1. Audit of Owner Ruling & `CALIBRATION-1` Source Amendments (`cdaf141a438002b5d84719c732f9a68329305ca9`)

1. **Design Ruling & Coordinator Ruling**:
   - Verified `experiment-7-design.md` §7 (`Pre-tag calibration ruling, 2026-10-20`, `34,277` B, SHA256 `2f34dc4949712d5681d3381efa4616924b1c90e5f96672a174b6918780506876`) and `experiments/exp7/build/amendments/calibration-001/COORDINATOR-RULING.md` (`5,720` B at `7e792d16d7e4b12f05db552530eabe869b88f399`).
   - Confirmed the ruling accurately records Michael's `2026-10-20` Option 1 approval before freeze and before any model contact: retain the unadjusted `F(1, 100)` (`0.01`) one-sided exact binomial defect threshold on all 22 component full-gate `fires` checks (against `F(1, 200)`) and all 9 `either_predictor_joint` checks (against `F(1, 100)`), and apply Bonferroni familywise error control across the 22 true-null component evaluations (`0.01 / 22 = 1/2200`) to the unmasked component `p_reject` defect check.

2. **Exact Source Diff Inspection (`501853e36e4937f0ec8f2307a81b2d3990b0333d..cdaf141a438002b5d84719c732f9a68329305ca9`)**:
   - `experiments/exp7/exp7stats/calibration.py` (`19,184` B, SHA256 `bf4c3202d6afdab349c8e2f052c9f8fccf23a6f09664abc00df177fc0af411f7`):
     - Defines `P_REJECT_DEFECT_ALPHA = F(1, 100 * sum(len(v) for v in TRUE_NULLS.values()))` (`= F(1, 2200)`).
     - Adds keyword-only `defect_alpha=F(1, 100)` to `rate_summary(count, n, null_rate, *, defect_alpha=F(1, 100))`.
     - Passes `defect_alpha=P_REJECT_DEFECT_ALPHA if key == "p_reject" else F(1, 100)` in `case_record` and `verify_calibration_semantics`.
     - Confirmed all simulation generators (`sample_scores`, `count_assignment`, `null_case`, `evaluate_replicate`, `envelope_cell`), RNG namespaces/seeds, `H`/`ENVELOPE`/`DELTAS`/`TRUE_NULLS` tables, and `fires` / `either_predictor_joint` thresholds (`F(1, 100)`) are 100% untouched.
   - `experiments/exp7/statistics_tests/test_SR_saved_math.py` (`10,822` B, SHA256 `a7e20636b752694d3efd7291e2b9fda78b7c7f3e63abe7949f5c07408abd2a58`):
     - Verifies `P_REJECT_DEFECT_ALPHA == F(1, 2200)`, `rate_summary(20, 2000, F(1, 200), defect_alpha=P_REJECT_DEFECT_ALPHA)["defect"] is False`, `rate_summary(23, 2000, F(1, 200), defect_alpha=P_REJECT_DEFECT_ALPHA)["defect"] is True`, `rate_summary(19, 2000, F(1, 200))["defect"] is True`, and `verify_calibration_semantics` acceptance/refusal under `P_REJECT_DEFECT_ALPHA`.
   - `experiments/exp7/local_tests/local_exp7core_live.py` (`18,160` B, SHA256 `6d37c9e18cb680728611d7aac85590e284f2773564a8c05f4d5f9628868ba976`):
     - Saves and restores `builtins.__import__ = guard.guarded_import` in `try ... finally` blocks around `test_default_acquisition_is_guarded` and `test_default_constructor_is_guarded_after_fake_acquisition` so `guard.py`'s `HARD-REFUSED` import boundary is tested deterministically whether run standalone or after `test_INTR2` in `--task all`.
   - `experiments/exp7/calibration/authority/candidate-selection.json` (`12,174` B, SHA256 `3b4dada8df67537b88009d93f8e766c725845559ec4ef659434356460315d207`) and `experiments/exp7/calibration/authority/calibration-candidate.json` (`12,176` B, SHA256 `83f83176efd573496c95be516ced4056d6c5c777d1647c46a189285b22dff3cb`):
     - Updated with the exact new `experiment-7-design.md` and `exp7stats/calibration.py` SHA256 pins while all other 86 pins remain unchanged.

---

## 2. Audit of `FREEZE-1-world-fixture` Amendment (`73f8ba2de2230cf9f3476ac6fa0cf83014a82355`)

1. **File Bindings**:
   - `experiments/exp7/tests/world_fixture.py` (`owner: W-numerical_worker`):
     - `base_sha256` (`501853e36e4937f0ec8f2307a81b2d3990b0333d`): `1e6e727e17a536ec47db7cba0858b53d0c6d91c6a884e46c3422b2b2f2caf1ad`
     - `sha256` (`73f8ba2de2230cf9f3476ac6fa0cf83014a82355`): `4f8ee05ca249d2238ca5988107ff48b4549e8cf97e807beac2f9ef9e732bdc88` (`29,554` B)

2. **Mathematical & RNG-Stream Equivalence of `_fast_forecast`**:
   - Verified that `_fast_forecast` constructs identical `SomersPlan` instances and `kernels.rng(namespace, "forecast", field, f, j)` streams per block, calls `gen.permuted(base_lx[:batch], axis=1)` in the exact same block order (including advancing the RNG stream even when `den == 0`), and contracts the 2D `(x, y)` contingency histogram via `np.bincount` + `np.add.accumulate` + `np.einsum` to compute the exact integer Somers numerator `smaller_y - larger_y` before passing `np.stack(columns, axis=1) - nums[None, :]` to `exact.sign(...)` and `kernels._mc(...)`.
   - Independently verified across synthetic multi-block `Cell` configurations (including tied `x`/`y`, degenerate `den == 0` blocks, `full=True`/`False`, fields `"x"`/`"d"`/`"u"`, and multiple `(B, chunk)` settings) that `_fast_forecast` and `_ORIG_FORECAST` (`exp7stats.kernels.forecast`) produce 100% identical outputs (`B`, `T`, `consumed`, `fires`, `kernel`, `n_ge`, `nonreject`, `p`, `p_high`, `p_low`, `per_family`, `reject`).

3. **Memoization Safety & World-Protocol Invariant Preservation**:
   - Verified `_install_full_world_accelerators` is invoked **only** when `not miniature` (`miniature=False`).
   - Verified `_cached_simulate_cell`, `_cached_verify_cal`, `_cached_verify_env`, `_cached_verify_power`, `_cached_primary`, `_cached_bootstrap`, and `_cached_reversal` key on cryptographic SHA256 digests of their inputs and return `deepcopy` of cached results (or `None` for `_cached_verify_cal`) so callers cannot mutate cached structures.
   - Verified that all 17 clean-world and 23 poison-world invariants are preserved:
     - `once-only` reentry refusal and `CLAIM.json` creation are executed by `stage(adapter, "analysis", ...)` in `analyzer.run` (which is never cached across worlds).
     - `entry-only-pin` and `HALTED-before-final` hook `analyzer.analyze_loaded` in `ProducerWorldFixture.analyze` and truthfully record `statistics_executed=True` before exit-boundary refusal.
     - `changed-init` and `missing-secondary` mutate the disposable package after `install` and are restored by `self.restore_sources()` at the top of the next `install` (before any `_clean_exports` template clone early return).

4. **Independent Test Execution (`python -I -B -X int_max_str_digits=5000`)**:
   - `S-REVIEW-SR1-SR5`: `23` tests ran, `0` failures, `0` errors (`16.035s`).
   - `M-exp7stats-calibration`: `1` test ran, `0` failures, `0` errors (`0.000s`).
   - `M-exp7core-live`: `15` tests ran, `0` failures, `0` errors (`0.018s`).
   - `W-numerical_worker`: `1` test ran, `0` failures, `0` errors (`0.104s`).
   - `W-freeze_worker`: `1` test ran, `0` failures, `0` errors (`0.085s`).
   - `W-producer_export_worker`: `1` test ran, `0` failures, `0` errors (`0.080s`).
   - `I-PRODUCER-WORLDS`: `1` test ran (full export-copy determinism + all 21 raw/chronology/claim/power poisons), `0` failures, `0` errors (`842.618s`).

---

## 3. Audit of Raw Simulation Run (`calibration-001/output/`) & Certified Accepted Archive (`calibration-001/accepted/`)

1. **Execution & Boundary Telemetry (`calibration-001`)**:
   - Inspected `produce.launch.json`, `produce.supervisor.json`, `status.json`, `produce.stdout`, `produce.stderr`, `CALIBRATION-001-REPORT.md`, and `ACCEPTED-CALIBRATION.json`.
   - Confirmed the 30.787-hour (`110,833.05s` wall, `109,989.21s` user / `607.27s` sys) cold pre-tag calibration run executed under `CalibrationContext.entryexit("calibration")`, `CandidateAudit` (`sys.setprofile`), and cold `ReadBoundary` with `0` bytes on `stderr`, `0` boundary/audit violations, and peak aggregate RSS `171,704,320` B (`163.7 MiB`, child peak `158,810,112` B / `151.5 MiB` `<< 8 GiB`).

2. **Raw vs. Accepted Record Equivalence**:
   - Verified `output/calibration.json` (`71,717,111` B, SHA256 `368c559a6ae76ae7f2dc76add6dc42d4f8ed62b7ed5b2ccc41ed3b1f29292289`) and `accepted/calibration.json` (`71,717,136` B, SHA256 `3e4ccd2fe377a0af6ecc39f645b82152caf3bd14a4798fd77bcc5ba9020e3187`):
     - Every case `N1..N9` in `accepted/calibration.json` has the exact same raw `count`, `N = 2000`, `fraction`, `interval95`, `null_rate`, and `binomial_excess_p` for every component (`fires` and `p_reject`) and `either_predictor_joint` as `output/calibration.json` (`fires == 0/2000` on all 22 components, `either_predictor_joint == 0/2000` on all 9 cases).
     - `selectivity_envelope` (`80` cells) and `case_table_sha256` (`a13b1bd8363506187b9f88bf6df87e3ab3ba00f48e7971b687e5884a70263a91`) in `accepted/calibration.json` are 100% identical to `output/calibration.json`.

3. **Independent Semantic & Copy Verification (`python -I -B -X int_max_str_digits=5000`)**:
   - Executed `verify_calibration_semantics(decode(strict_json((accepted / "calibration.json").read_bytes())))`: **PASSED** (`state == "NO-DETECTED-CALIBRATION-DEFECT"`, all 9 null cases and all 80 selectivity envelope cells verified from packed score counts and randomization bounds).
   - Executed `exp7integration.calibration_copy.copy_accepted_calibration` on `experiments/exp7/calibration/calibration-001/accepted/` into an isolated temporary campaign root and verified the returned 4-file digest map matches `ACCEPTED-CALIBRATION.json["accepted_files"]` 100%:
     - `CLAIM.json` (`72` B): `99bdcd855bae89ee8817b53a6b959f4f16303ea5fca55738498ea073f548896d`
     - `COMPLETE.json` (`177` B): `58613e7edbb199ea1c0901f6ec6c153d759dabd1e4c060485e094d95bbfe9df8`
     - `REPORT.md` (`73,157,706` B): `408d144601167a3255650c1a926713e65df6339653c77fc4436f030b041688dd`
     - `calibration.json` (`71,717,136` B): `3e4ccd2fe377a0af6ecc39f645b82152caf3bd14a4798fd77bcc5ba9020e3187`

---

## 4. Disposition

`ACCEPT` — The `CALIBRATION-1` pre-tag amendment (`cdaf141a438002b5d84719c732f9a68329305ca9`), the `FREEZE-1-world-fixture` amendment (`73f8ba2de2230cf9f3476ac6fa0cf83014a82355`), and the certified accepted calibration archive (`experiments/exp7/calibration/calibration-001/accepted/` at `d20b633b54324936a00b03ced2ba64a5a26cc114`) are independently verified and approved with `0` open defects.
