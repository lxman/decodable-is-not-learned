# Experiment 7 Pre-Tag Calibration — Independent Candidate Manifest Review

- **Audited Candidate Commit**: `501853e36e4937f0ec8f2307a81b2d3990b0333d`
- **Governing Specification**: `docs/superpowers/plans/2026-10-04-exp7-annex/integration-v3/RUNTIME-PREPARATION.md` (Section 4)
- **Host / Interpreter**: Darwin arm64, `/Users/michaeljordan/emergence-lab/.venv/bin/python -I -B -X int_max_str_digits=5000` (CPython `3.11.15`)
- **Disposition**: `ACCEPT` (`open_defects: 0`)

## 1. Audited Candidate & Runtime Artifacts

| Artifact | Path | Bytes | SHA256 |
|---|---|---:|---|
| Materialized Runtime | `experiments/exp7/calibration/authority/calibration-runtime.json` | `145,506` | `16718b298ca146366b2475235ef106bc1659ec7acdad77f8c2b3fb1ededc64fa` |
| Candidate Selection | `experiments/exp7/calibration/authority/candidate-selection.json` | `12,174` | `bbab6199987c38ecde923a98eacbf93b6152a094ec626dedd655632deac2976c` |
| Candidate Manifest | `experiments/exp7/calibration/authority/calibration-candidate.json` | `12,176` | `10a6389533c549443d1862fad7566d012777134aa2a86c9ca8008db1b778bbee` |
| Standalone Cold CLI Wrapper | `experiments/exp7/calibration/run_calibration_cli.py` | `284` | `565dc6d449eaa8a49541d89700bd451a664e86d9dfba149221e4fa7ae589ed26` |
| Full-Stage Extrapolation | `experiments/exp7/resource-check/FULL-STAGE-EXTRAPOLATION.md` | `8,661` | `b633458a8eb31b7b06d7481679ac81483104ee0e260b3ecb6e7e4900b646b4ff` |

## 2. Independent Verification Findings

1. **Materialized Runtime (`calibration-runtime.json`)**:
   - Verified `schema == "exp7.calibration-runtime.v1"` and exact SHA256 `16718b298ca146366b2475235ef106bc1659ec7acdad77f8c2b3fb1ededc64fa`, matching the approved `runtime_sha256` from the Section 3 independent runtime review (`e2f915bc2c0bf5c8bc8d7bd60841eb846fe00f17`).
   - Verified byte-for-byte identity between the working tree and `git show 501853e36e4937f0ec8f2307a81b2d3990b0333d:experiments/exp7/calibration/authority/calibration-runtime.json`.

2. **Candidate Selection & Manifest (`candidate-selection.json` & `calibration-candidate.json`)**:
   - Verified `candidate-selection.json` (`schema == "exp7.candidate-selection.v1"`, `12,174` B, SHA256 `bbab6199987c38ecde923a98eacbf93b6152a094ec626dedd655632deac2976c`) and `calibration-candidate.json` (`schema == "exp7.calibration-candidate.v1"`, `12,176` B, SHA256 `10a6389533c549443d1862fad7566d012777134aa2a86c9ca8008db1b778bbee`) have identical `files` maps covering `88` repository-relative paths:
     - `85` `source` files: complete executable `.py` closure across `experiments/exp7/exp7core` (`26`), `experiments/exp7/exp7stats` (`16`), `experiments/exp7/exp7ops` (`14`), `experiments/exp7/exp7integration` (`19`), `experiments/exp7/run` (`8`), plus `experiments/exp7/calibration/run_calibration_cli.py` (`1`).
     - `1` `design` file: `experiment-7-design.md` (`6216a65b2946548a7933d50cfaa231f1d1979ff0261f960d3f30fdd4ecd765d8`).
     - `1` `synthetic_spec` file: `experiments/exp7/calibration/authority/synthetic-cases.json` (`21667d68e26ad0b2d8e329969c2c7d3eb9cccbb0f27ec268f88f69388210d773`).
     - `1` `runtime_spec` file: `experiments/exp7/calibration/authority/calibration-runtime.json` (`16718b298ca146366b2475235ef106bc1659ec7acdad77f8c2b3fb1ededc64fa`).
   - Verified that all `88` files in `calibration-candidate.json` match both their on-disk bytes and `git show 501853e36e4937f0ec8f2307a81b2d3990b0333d:<path>`, with zero `.pyc` files across all five candidate packages.

3. **Coordinator Inventory Non-Drift (`coordinator-inventory.json`)**:
   - Verified all `271` installed files in `experiments/exp7/` recorded in `experiments/exp7/build/amendments/live-tokenizer-001/coordinator-inventory.json` remain byte-for-byte unchanged (`drifted == 0`).

4. **Cold `CalibrationContext` Binding Check**:
   - In a cold `/Users/michaeljordan/emergence-lab/.venv/bin/python -I -B -X pycache_prefix=<scratch_empty_pycache> -X int_max_str_digits=5000` process, constructed `CalibrationContext(scratch_out, "/Users/michaeljordan/emergence-paper", candidate_commit="501853e36e4937f0ec8f2307a81b2d3990b0333d", manifest_path="experiments/exp7/calibration/authority/calibration-candidate.json", manifest_sha256="10a6389533c549443d1862fad7566d012777134aa2a86c9ca8008db1b778bbee")` using the default real `git_blob`, `prereg_exists`, and `SystemReadPort` (`read_port=None`).
   - Verified `context._manifest()` and `context._check(manifest)` pass cleanly (confirming `refs/tags/exp7-preregistered` is absent, output root separation is enforced, all `88` manifest pins match both working tree and committed Git blobs at `501853e36e4937f0ec8f2307a81b2d3990b0333d`, and zero project bytecode cache exists).

5. **CLI Wrapper & Operational Extrapolation Audit**:
   - Inspected `experiments/exp7/calibration/run_calibration_cli.py` (`284` B, SHA256 `565dc6d449eaa8a49541d89700bd451a664e86d9dfba149221e4fa7ae589ed26`), confirming it prepends `experiments/exp7` to `sys.path` and invokes `exp7stats.calibration_cli.main()` directly under cold `-I -B` execution, and is enrolled as `"kind": "source"` in `calibration-candidate.json`.
   - Inspected `experiments/exp7/resource-check/FULL-STAGE-EXTRAPOLATION.md`, confirming the `RESOURCE-1` (`numerical-014`) full-stage memory (`< 500 MiB << 8 GiB`), power (`4.5 – 8.5 hours <= 24.0 hours`), and calibration (`14.27 hours` pure kernel + audit hook + `ReadBoundary`; `28.11 hours` with `CandidateAudit` `sys.setprofile` active across all ~`320B` Python calls) extrapolations are accurately documented.

## 3. Disposition

`ACCEPT` — Candidate commit `501853e36e4937f0ec8f2307a81b2d3990b0333d` and manifest `experiments/exp7/calibration/authority/calibration-candidate.json` (`10a6389533c549443d1862fad7566d012777134aa2a86c9ca8008db1b778bbee`) are approved for pre-tag calibration execution.
