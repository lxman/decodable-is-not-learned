# Experiment 7 Full-Default Synthetic Freeze Review (`freeze-001`)

- **Disposition**: `ACCEPT` (`open_defects: 0`, `full_freeze_accepted: true`)
- **Coordinator Commit Reviewed**: `5fe75c512dc42f9844a36e34a9374ba5ce3694b7`
- **Coordinator Inventory Baseline Commit**: `977d4ca02113ab91735774dd4974f0beec8e5995` (`experiments/exp7/build/amendments/calibration-001/coordinator-inventory.json`, 271 files)
- **Staged Package Path**: `/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp7-freeze-001/staged-package`
- **Scratch Freeze Output Path**: `/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp7-freeze-001/freeze-out`
- **Producer Export Receipt Path**: `/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp7-freeze-001/producer-export.json` (`173233` bytes, SHA256 `f7bb85daf6b92bc2337f8e976dc7a0d46685e217d69d42beb292416affeda561`, `516` exported files)

---

## 1. Staged Package & Coordinator Inventory Verification

1. **Coordinator Inventory Match**:
   - Verified all `271` entries in `experiments/exp7/build/amendments/calibration-001/coordinator-inventory.json` (`977d4ca02113ab91735774dd4974f0beec8e5995`) against `/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp7-freeze-001/staged-package` via `exp7ops.evidence.verify_files(..., exact=True)` and against `experiments/exp7/freeze/freeze-001/mutations/original-manifest.json` (`272` entries = `271` coordinator-inventory files + `DISPOSABLE-SYNTHETIC-SOURCE.json`).
   - `mutations/original-manifest.json` raw file size: `29855` bytes, SHA256 `539ced310faa6eeaeac8f448253cee84d1757c0afdcf1e1bfd0b8aa893ca109f`; canonical JSON size: `29855` bytes, SHA256 `539ced310faa6eeaeac8f448253cee84d1757c0afdcf1e1bfd0b8aa893ca109f`.
2. **Task-Boundary Package Integrity (`task-0001.json` .. `task-0131.json`)**:
   - Verified `task-0001.json` (`20304` bytes, SHA256 `4e79f8a529b78edffcca27d0285aa0a9ca3110f42daa1c81e8fbe0fd41a511ee`) and `task-0131.json` (`20304` bytes, SHA256 `4e79f8a529b78edffcca27d0285aa0a9ca3110f42daa1c81e8fbe0fd41a511ee`) and all `131` task snapshots (`task-0001.json` through `task-0131.json` in `freeze-out`) across the entire freeze run.

---

## 2. Archived Freeze Artifacts (`experiments/exp7/freeze/freeze-001/`)

Every archived file in `experiments/exp7/freeze/freeze-001/` was verified byte-for-byte against `/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp7-freeze-001/freeze-out/` and `HEAD` (`5fe75c512dc42f9844a36e34a9374ba5ce3694b7`):

| Path | Bytes | SHA256 |
| --- | ---: | --- |
| `experiments/exp7/freeze/freeze-001/COMPLETE.json` | 35309 | `4fcba8c7001fd2ff71e40bcc968095446b0f50b8addf6584a77346965c449dd2` |
| `experiments/exp7/freeze/freeze-001/task-0001.json` | 20304 | `4e79f8a529b78edffcca27d0285aa0a9ca3110f42daa1c81e8fbe0fd41a511ee` |
| `experiments/exp7/freeze/freeze-001/task-0131.json` | 20304 | `4e79f8a529b78edffcca27d0285aa0a9ca3110f42daa1c81e8fbe0fd41a511ee` |
| `experiments/exp7/freeze/freeze-001/worlds.json` | 4266 | `434975391e696eadc0ecef4e622e9a8f9b055aa98f5752c2e8bc9ff185a41b4e` |
| `experiments/exp7/freeze/freeze-001/import-scan.json` | 133701 | `f58940a9f554645b08de63f2a4012e339c299a48f0f140992f95154b050a666b` |
| `experiments/exp7/freeze/freeze-001/read-scan.json` | 202079 | `3b0093faa6f688bb9fa9e74df364c132f4520d1426a95224afac3455341f5570` |
| `experiments/exp7/freeze/freeze-001/determinism/determinism.json` | 116 | `deac7faa61091132694856f40719fe6569155bed6ab1d996b328e94febd5e72b` |
| `experiments/exp7/freeze/freeze-001/mutations/original-manifest.json` | 29855 | `539ced310faa6eeaeac8f448253cee84d1757c0afdcf1e1bfd0b8aa893ca109f` |
| `experiments/exp7/freeze/freeze-001/mutations/results.json` | 132301 | `28f77d963dce1952bb1ff259a253bcb821eaccec55d3bd2a638216129691b237` |
| `experiments/exp7/freeze/freeze-001/FREEZE-001-REPORT.md` | 2713 | `10275ef02bf1479e0fcf11c4f2297efb930e6e1c7019ae00b6135e9d434b700d` |

---

## 3. World Suite, Import Scan, Read Scan, and Determinism Verification

1. **40-World Matrix (`worlds.json`)**:
   - `40/40` worlds passed (`17` clean worlds: `W-clean-full`, `W-clean-mid-001..006`, `W-clean-min-001..005`, `W-clean-s3`, `W-clean-stat-001..004`; `23` poison worlds: `W-poison-001..023`).
   - All `17` clean worlds exited `0` with expected validator pass receipts; all `23` poison worlds failed closed with their exact expected error codes.
2. **Import Scan (`import-scan.json`)**:
   - `ok: true`, `file_count: 21`, `violations: []`. Zero prohibited imports across all `21` validator Python modules.
3. **Read Scan (`read-scan.json`)**:
   - `ok: true`, `event_count: 18312`, `violations: []`. Zero out-of-scope file reads across `18,312` traced read events.
4. **Determinism Check (`determinism/determinism.json`, `first.json`, `second.json`)**:
   - `ok: true`. Both full-suite determinism runs (`first.json` and `second.json` in `freeze-out/determinism/`) are `98,579,894` bytes with identical SHA256 `0038db847f4c87f9b79e19ad16def07bcfe20904abb1bd71e1135620301d9e45`.

---

## 4. 43/43 Mutation-Kill Verification (`mutations/results.json` & `mutations/logs/`)

All `43` mutations were independently verified against `mutations/results.json` and the `215` per-mutant log files (`*.intent.json`, `*.original.json`, `*.mutant.json`, `*.restored.json`, `*.result.json` in `freeze-out/mutations/logs/`):
- `43/43` mutants had `status: "KILLED"` (`returncode != 0`, `model_contacts: 0`, `actual_operational_process_spawns: 0`) and restored cleanly to `mutations/original-manifest.json` (`272` entries, canonical SHA256 `539ced310faa6eeaeac8f448253cee84d1757c0afdcf1e1bfd0b8aa893ca109f`).

| # | Mutant ID | Target File | Task | Status | Returncode | Failures/Errors | Restored |
| ---: | --- | --- | --- | --- | ---: | ---: | --- |
| 1 | `conditional-sign` | `exp7core/scoring.py` | `C2` | `KILLED` | `1` | `4` | `True` |
| 2 | `render-sum` | `exp7core/scoring.py` | `C2` | `KILLED` | `1` | `3` | `True` |
| 3 | `drop-unsupported` | `exp7core/scoring.py` | `C2` | `KILLED` | `1` | `2` | `True` |
| 4 | `unsupported-positive` | `exp7core/scoring.py` | `C2` | `KILLED` | `1` | `3` | `True` |
| 5 | `wrong-sign-d` | `exp7core/scoring.py` | `C2` | `KILLED` | `1` | `3` | `True` |
| 6 | `availability-half` | `exp7core/scoring.py` | `C2` | `KILLED` | `1` | `3` | `True` |
| 7 | `joint-is-or` | `exp7core/scoring.py` | `C2` | `KILLED` | `1` | `1` | `True` |
| 8 | `losses-suppressed` | `exp7core/scoring.py` | `C2` | `KILLED` | `1` | `1` | `True` |
| 9 | `all-pairs-denominator` | `exp7core/inference.py` | `C4` | `KILLED` | `1` | `1` | `True` |
| 10 | `thin-boundary` | `exp7core/inference.py` | `C4` | `KILLED` | `1` | `2` | `True` |
| 11 | `drop-constant` | `exp7core/inference.py` | `C4` | `KILLED` | `1` | `1` | `True` |
| 12 | `drop-negative` | `exp7core/inference.py` | `C4` | `KILLED` | `1` | `2` | `True` |
| 13 | `two-families-enough` | `exp7core/inference.py` | `C4` | `KILLED` | `1` | `1` | `True` |
| 14 | `forecast-bar` | `exp7core/inference.py` | `C4` | `KILLED` | `1` | `1` | `True` |
| 15 | `p-edge-inclusive` | `exp7core/inference.py` | `C4` | `KILLED` | `1` | `1` | `True` |
| 16 | `median-ties-upper` | `exp7core/strata.py` | `C3` | `KILLED` | `1` | `1` | `True` |
| 17 | `tail-not-merged` | `exp7core/strata.py` | `C3` | `KILLED` | `1` | `1` | `True` |
| 18 | `shared-arm-stream` | `exp7core/contract.py` | `C1` | `KILLED` | `1` | `1` | `True` |
| 19 | `wrong-trained-budget` | `exp7core/contract.py` | `C1` | `KILLED` | `1` | `1` | `True` |
| 20 | `missing-grid-endpoint` | `exp7core/contract.py` | `C1` | `KILLED` | `1` | `1` | `True` |
| 21 | `label-swap-disabled` | `exp7core/scoring.py` | `C2` | `KILLED` | `1` | `1` | `True` |
| 22 | `entry-only-pin` | `exp7core/guardio.py` | `C7` | `KILLED` | `1` | `1` | `True` |
| 23 | `overwrite-once` | `exp7core/guardio.py` | `C7` | `KILLED` | `1` | `2` | `True` |
| 24 | `no-completion-hash` | `exp7core/guardio.py` | `C7` | `KILLED` | `1` | `1` | `True` |
| 25 | `accept-attested-pass` | `exp7core/guardio.py` | `C7` | `KILLED` | `1` | `1` | `True` |
| 26 | `ignore-record-context` | `exp7core/records.py` | `C10` | `KILLED` | `1` | `5` | `True` |
| 27 | `no-duplicate-json` | `exp7core/records.py` | `C10` | `KILLED` | `1` | `1` | `True` |
| 28 | `bootstrap-undefined-zero` | `exp7core/resampling.py` | `C6` | `KILLED` | `1` | `1` | `True` |
| 29 | `saved-power-unbound-geometry` | `exp7stats/power_validation.py` | `S-REVIEW-SR1-SR5` | `KILLED` | `1` | `1` | `True` |
| 30 | `cold-inherited-fd` | `exp7stats/read_boundary.py` | `S-REVIEW-SR1-R` | `KILLED` | `1` | `2` | `True` |
| 31 | `cold-inherited-buffer` | `exp7stats/read_boundary.py` | `S-REVIEW-SR1-R` | `KILLED` | `1` | `1` | `True` |
| 32 | `adapter-drop-claim-order` | `exp7integration/adapter.py` | `I-ADAPTER` | `KILLED` | `1` | `1` | `True` |
| 33 | `adapter-ignore-authority` | `exp7integration/adapter.py` | `I-ADAPTER` | `KILLED` | `1` | `1` | `True` |
| 34 | `adapter-model-none` | `exp7integration/adapter.py` | `I-ADAPTER` | `KILLED` | `1` | `3` | `True` |
| 35 | `adapter-abstention-lost` | `exp7integration/adapter.py` | `I-ADAPTER` | `KILLED` | `1` | `1` | `True` |
| 36 | `adapter-drop-source-exit` | `exp7integration/adapter.py` | `I-ADAPTER` | `KILLED` | `1` | `1` | `True` |
| 37 | `o8-unbound-site` | `exp7integration/bootstrap.py` | `O8-BOOTSTRAP` | `KILLED` | `1` | `1` | `True` |
| 38 | `o8-no-cold-input-close` | `exp7integration/bootstrap.py` | `O8-BOOTSTRAP` | `KILLED` | `1` | `1` | `True` |
| 39 | `o8-stale-worker` | `exp7integration/heartbeat_service.py` | `O8-PORTS` | `KILLED` | `1` | `1` | `True` |
| 40 | `o8-supervisor-in-campaign` | `exp7integration/supervisor.py` | `O8-DEPLOYMENT` | `KILLED` | `1` | `1` | `True` |
| 41 | `runtime-unreviewed` | `exp7integration/candidate_runtime.py` | `I-RUNTIME-PREPARATION` | `KILLED` | `1` | `1` | `True` |
| 42 | `inventory-unknown-files` | `exp7integration/inventory.py` | `I-ADAPTER` | `KILLED` | `1` | `5` | `True` |
| 43 | `inventory-transient-write` | `exp7integration/inventory.py` | `I-ADAPTER` | `KILLED` | `1` | `2` | `True` |

---

## 5. Conclusion

The full-default synthetic freeze (`freeze-001`) at commit `5fe75c512dc42f9844a36e34a9374ba5ce3694b7` satisfies all protocol, inventory, world-matrix (`40/40`), import-scan (`21` files, `0` violations), read-scan (`18,312` events, `0` violations), determinism (`98,579,894` B identical runs), and mutation-testing (`43/43` killed and restored) gates.

**Disposition**: `ACCEPT` (`open_defects: 0`, `full_freeze_accepted: true`).
