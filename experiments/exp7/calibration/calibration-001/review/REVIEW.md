# Experiment 7 — Independent Review of `CALIBRATION-1` (`cdaf141a4380`), `FREEZE-1` (`96cebf393374` & `c80bdba10b48`), & Pre-Tag Calibration Archive `calibration-001` (`d20b633b5432`)

- **Audited Amendment Commit (`CALIBRATION-1`)**: `cdaf141a438002b5d84719c732f9a68329305ca9`
- **Audited Calibration Archive Commit**: `d20b633b54324936a00b03ced2ba64a5a26cc114`
- **Audited World-Fixture Amendment Commit (`FREEZE-1-world-fixture`)**: `96cebf3933744fb0e994184494da71182b102681`
- **Audited Mutant-Kill Assertion Completeness Commit (`FREEZE-1-mutant-kills`)**: `c80bdba10b48fa42532a6955bf9933afca6e5296`
- **Host / Interpreter**: Darwin arm64, `/Users/michaeljordan/emergence-lab/.venv/bin/python -I -B -X int_max_str_digits=5000` (CPython `3.11.15`)
- **Disposition**: `ACCEPT` (`open_defects: 0`, `calibration_1_amendment_accepted: true`, `freeze_1_world_fixture_accepted: true`, `freeze_1_mutant_kills_accepted: true`, `accepted_calibration_archive_verified: true`)

---

## 1. Audit of Owner Ruling & `CALIBRATION-1` Source Amendments (`cdaf141a438002b5d84719c732f9a68329305ca9`)

1. **Design Ruling & Coordinator Ruling**:
   - Verified `experiment-7-design.md` §7 (`Pre-tag calibration ruling, 2026-10-20`, `34,277` B, SHA256 `2f34dc4949712d5681d3381efa4616924b1c90e5f96672a174b6918780506876`) and `experiments/exp7/build/amendments/calibration-001/COORDINATOR-RULING.md` (`8,290` B at `c80bdba10b48fa42532a6955bf9933afca6e5296`).
   - Confirmed the ruling accurately records Michael's `2026-10-20` Option 1 approval before freeze and before any model contact: retain the unadjusted `F(1, 100)` (`0.01`) one-sided exact binomial defect threshold on all 22 component full-gate `fires` checks (against `F(1, 200)`) and all 9 `either_predictor_joint` checks (against `F(1, 100)`), and apply Bonferroni familywise error control across the 22 true-null component evaluations (`0.01 / 22 = 1/2200`) to the unmasked component `p_reject` defect check.

2. **Exact Source Diff Inspection (`501853e36e4937f0ec8f2307a81b2d3990b0333d..cdaf141a438002b5d84719c732f9a68329305ca9`)**:
   - `experiments/exp7/exp7stats/calibration.py` (`19,184` B, SHA256 `bf4c3202d6afdab349c8e2f052c9f8fccf23a6f09664abc00df177fc0af411f7`):
     - Defines `P_REJECT_DEFECT_ALPHA = F(1, 100 * sum(len(v) for v in TRUE_NULLS.values()))` (`= F(1, 2200)`).
     - Adds keyword-only `defect_alpha=F(1, 100)` to `rate_summary(count, n, null_rate, *, defect_alpha=F(1, 100))`.
     - Passes `defect_alpha=P_REJECT_DEFECT_ALPHA if key == "p_reject" else F(1, 100)` in `case_record` and `verify_calibration_semantics`.
     - Confirmed all simulation generators (`sample_scores`, `count_assignment`, `null_case`, `evaluate_replicate`, `envelope_cell`), RNG namespaces/seeds, `H`/`ENVELOPE`/`DELTAS`/`TRUE_NULLS` tables, and `fires` / `either_predictor_joint` thresholds (`F(1, 100)`) are 100% untouched.
   - `experiments/exp7/local_tests/local_exp7core_live.py` (`18,160` B, SHA256 `6d37c9e18cb680728611d7aac85590e284f2773564a8c05f4d5f9628868ba976`):
     - Saves and restores `builtins.__import__ = guard.guarded_import` in `try ... finally` blocks around `test_default_acquisition_is_guarded` and `test_default_constructor_is_guarded_after_fake_acquisition` so `guard.py`'s `HARD-REFUSED` import boundary is tested deterministically whether run standalone or after `test_INTR2` in `--task all`.
   - `experiments/exp7/calibration/authority/candidate-selection.json` (`12,174` B, SHA256 `3b4dada8df67537b88009d93f8e766c725845559ec4ef659434356460315d207`) and `experiments/exp7/calibration/authority/calibration-candidate.json` (`12,176` B, SHA256 `83f83176efd573496c95be516ced4056d6c5c777d1647c46a189285b22dff3cb`):
     - Updated with the exact new `experiment-7-design.md` and `exp7stats/calibration.py` SHA256 pins while all other 86 pins remain unchanged.

---

## 2. Audit of `FREEZE-1` Amendments (`96cebf3933744fb0e994184494da71182b102681` & `c80bdba10b48fa42532a6955bf9933afca6e5296`)

1. **Memory-Bounded World Fixture (`96cebf3933744fb0e994184494da71182b102681`)**:
   - `experiments/exp7/tests/world_fixture.py` (`owner: W-numerical_worker`, `32,760` B, SHA256 `a927c108786179d40aa8835b5e4bc5e24f6a170ecec927acd3ddd183bfb9d7b7`, `base_sha256`: `1e6e727e17a536ec47db7cba0858b53d0c6d91c6a884e46c3422b2b2f2caf1ad`).
   - Verified `_fast_forecast` is mathematically and RNG-stream identical to `exp7stats.kernels.forecast` (`_ORIG_FORECAST`).
   - Verified `_install_full_world_accelerators` is activated only when `miniature=False`, `_POWER_VERIFIED` / `_ENV_VERIFIED` / `_CAL_VERIFIED` are hash-only `set()`s (enforcing all top-level header/seal/battery/geometry/support/declaration/thin/source_binding/envelope/calibration checks on every call), `_CELL_CACHE` / `_PRIMARY_CACHE` / `_METRIC_CACHE` / `_REVERSAL_CACHE` store `zlib`-compressed bytes, `_ACTIVE_SLICE` is evicted immediately after `power.run`, and all 17 clean-world and 23 poison-world invariants are preserved.

2. **Mutant-Kill Assertion Completeness (`c80bdba10b48fa42532a6955bf9933afca6e5296`, `owner: F-INTEGRATED-REGRESSIONS`)**:
   - Audited all 4 amended test files:
     - `experiments/exp7/tests/test_C2.py` (`4,744` B, SHA256 `2dc10eb646cc4c482a393233dab96f4ad28805118504096d6ae3d6487804f1ee`, `base_sha256`: `52a4c22538f7c88190c10eaf6aa31476b5850da01d8dd7e9a8ce7abe354badb1`)
     - `experiments/exp7/tests/test_C4.py` (`4,943` B, SHA256 `a9f0c3340f70c559414fadfdaf9b684bc183d534c86faf01c4b533a42404fd1d`, `base_sha256`: `3498dcbd15d7e6e98b103c45ca5bd265ddd4ea1d37c65f021a8a1a7bfecca99d`)
     - `experiments/exp7/statistics_tests/test_SR_saved_math.py` (`11,047` B, SHA256 `8e262eec1ffc6e8d85ff7a624e57cdff47e267aa5371824d0190b5c674146fe1`, `base_sha256`: `a64685a2f149335af5d5c3f0f062329eb2d48d3dd5950a2c3780491b83e30491`)
     - `experiments/exp7/tests/test_adapter.py` (`21,376` B, SHA256 `c1ac8f75edbdff4ea96feeaade21bb441cc6c2c9e2cdd3c779066422d03cb816`, `base_sha256`: `d2f9711b48bd9cdf47ac858c2ba8a6dfc99f279a1e1b90a11b1c0638f59fff04`)
   - Verified via AST inspection that zero test methods or imports were added or removed (`new_test_methods: []`, `removed_test_methods: []`, `deferred_imports_added: []`, `test_import_closure_added: []`).
   - Verified all 4 baseline task test suites pass cleanly (`failures=0, errors=0, returncode=0`): `C2` (`10` tests), `C4` (`8` tests), `S-REVIEW-SR1-SR5` (`23` tests), `I-ADAPTER` (`26` tests).
   - Independently verified all 7 target mutants are cleanly `KILLED` (`failures > 0, errors == 0, returncode != 0`), bringing total mutant kills to `43 / 43`:
     - `wrong-sign-d` (`C2`): `failures=3, errors=0` (`KILLED`)
     - `availability-half` (`C2`): `failures=3, errors=0` (`KILLED`)
     - `thin-boundary` (`C4`): `failures=2, errors=0` (`KILLED`)
     - `saved-power-unbound-geometry` (`S-REVIEW-SR1-SR5`): `failures=1, errors=0` (`KILLED`)
     - `adapter-drop-claim-order` (`I-ADAPTER`): `failures=1, errors=0` (`KILLED`)
     - `adapter-ignore-authority` (`I-ADAPTER`): `failures=1, errors=0` (`KILLED`)
     - `adapter-drop-source-exit` (`I-ADAPTER`): `failures=1, errors=0` (`KILLED`)

---

## 3. Audit of Raw Simulation Run (`calibration-001/output/`) & Certified Accepted Archive (`calibration-001/accepted/`)

1. **Execution & Boundary Telemetry (`calibration-001`)**:
   - Confirmed the 30.787-hour (`110,833.05s` wall, `109,989.21s` user / `607.27s` sys) cold pre-tag calibration run executed under `CalibrationContext.entryexit("calibration")`, `CandidateAudit` (`sys.setprofile`), and cold `ReadBoundary` with `0` bytes on `stderr`, `0` boundary/audit violations, and peak aggregate RSS `171,704,320` B (`163.7 MiB`, child peak `158,810,112` B / `151.5 MiB` `<< 8 GiB`).

2. **Raw vs. Accepted Record Equivalence & Semantic Verification**:
   - Verified `output/calibration.json` (`71,717,111` B, SHA256 `368c559a6ae76ae7f2dc76add6dc42d4f8ed62b7ed5b2ccc41ed3b1f29292289`) and `accepted/calibration.json` (`71,717,136` B, SHA256 `3e4ccd2fe377a0af6ecc39f645b82152caf3bd14a4798fd77bcc5ba9020e3187`) have 100% identical raw `count`, `N = 2000`, `fraction`, `interval95`, `null_rate`, and `binomial_excess_p` across `N1..N9`, and 100% identical `selectivity_envelope` (`80` cells) and `case_table_sha256`.
   - Executed `verify_calibration_semantics` (`PASSED`, `state == "NO-DETECTED-CALIBRATION-DEFECT"`) and `copy_accepted_calibration` (`PASSED`, exact 4-file digest match to `ACCEPTED-CALIBRATION.json["accepted_files"]`).

---

## 4. Disposition

`ACCEPT` — `CALIBRATION-1` (`cdaf141a438002b5d84719c732f9a68329305ca9`), `FREEZE-1` (`96cebf3933744fb0e994184494da71182b102681` and `c80bdba10b48fa42532a6955bf9933afca6e5296`), and the certified accepted calibration archive (`experiments/exp7/calibration/calibration-001/accepted/` at `d20b633b54324936a00b03ced2ba64a5a26cc114`) are independently verified and approved with `0` open defects.
