# Experiment 7 — ratification record

**RATIFIED by Michael 2026-10-21: “Proceed with the tag and then we can look up a rental to use.”**
All pre-tag build, validation, numerical resource check, synthetic calibration, and
adversarial synthetic freeze gates are complete and independently reviewed. No model
weights have been loaded on any new item, and no new item has been handed to a model.

## 1. Certified battery and model-free baselines (`feasibility-002/full-003`)

- **Counterfactual battery**: 4 families (`arithmetic`, `deduction`, `shapes`, `unscrambling`) × 500 counterfactual pairs × 4 prompt arms (`q0`, `q0s`, `q1`, `q1s`) = 2,000 pairs / 8,000 prompts.
  - `experiments/exp7/feasibility-002/full-003/pairs.jsonl` (`3,795,213` B, SHA256 `e81ef294e070894f65934bf0996dc1ab306ca8d051a82e0a59cc087beaa2b621`)
  - `experiments/exp7/feasibility-002/full-003/CERTIFICATE.json` (`2,431` B, SHA256 `61f2ef7527c8c33cc7e892a9f4bf7ce434332a0dbdebe1540328eb33d50ef216`)
  - `experiments/exp7/feasibility-002/full-003/levels.json` (`18,653` B, SHA256 `cb0ed7ca70bf5fcdf0fb06dcdebdba44f72f8f82bc9de04133a724d31f925b86`)
- **84-cell baseline catalog** (`49` applicable / `35` explicit `N/A` across 21 methods × 4 families):
  - `experiments/exp7/feasibility-002/full-003/baselines.json` (`21,055` B, SHA256 `d6db1e4ee579b1ab1ca1985a4a9573de7e4bf120d174108b6511c29427029cc4`)
  - `experiments/exp7/feasibility-002/full-003/baseline-outputs.jsonl` (`6,812,683` B, SHA256 `6e8405df06024cb364fd75114f1ee0bcba33ee510c19d74e9e9917e644006c44`)

## 2. Pre-tag tokenizer/config-only cap validation (`operations-007/offline-003-completed`)

- All 28 tokenizer/config-only cap-validation receipts (`pythia_1b`, `olmo2_1b`, and all 26 `SmolLM3-3B` outcome checkpoint revisions `40000..3440000`) were executed offline against pinned Hugging Face tokenizer/config assets (`16,000` prompt × oracle-target checks per receipt, `0` model weights loaded, `0` forward passes) and committed under `experiments/exp7/validation/operations-007/offline-003-completed/offline-003/cap-validation/` (`DONE.json` SHA256 `f434f212767794a0f8c083ab1028c74a4d4c3e2632419ebcefd01d3b5ef6d520`).

## 3. Pre-tag numerical resource verification (`numerical-014/RESOURCE-1`)

- Completed and independently reviewed at `bd44ef025f6a56e4db64bb31c9c6b27f2a101fb3` (`experiments/exp7/resource-check/numerical-014/`):
  - `qualify-produce`, `qualify-read`, `produce`, `reader-inputs`, and `read` all exited `0` with `0` `CandidateAudit` violations and byte-exact roundtrip of `produce.compact.json` (`8,370,450` B, SHA256 `9db9516673c523768991a2a3932f36174545fe97dbc7e297db98c11316f7c1bd`) and `produce.report.md` (`14,262,068` B, SHA256 `a8f178a67fd403a2e9ef7c51bfe5330a0a27121436e004c5b228e59b6ce391ba`).

## 4. Pre-tag full-stage synthetic calibration (`calibration-001`)

- Completed and independently reviewed across `N1..N9` (`2,000` replicates each at `n=500, B=10,000`) plus the 80-cell selectivity envelope (`128` replicates each):
  - Every component full-rule `fires` count was `0/2,000` across all 22 true-null component evaluations (`0/44,000` total).
  - Every `either_predictor_joint` count was `0/2,000` across `N1..N9` (`0/18,000` total).
  - Under Michael's 2026-10-20 Option 1 ruling (`CALIBRATION-1-p-reject-fwer`), Bonferroni familywise error control (`.01 / 22 = 1/2200`) applies to the 22 component unmasked `p_reject` defect checks while unadjusted `.01` remains on all 22 component `fires` checks and all 9 `either_predictor_joint` checks.
  - Accepted calibration record (`state: "NO-DETECTED-CALIBRATION-DEFECT"`, `production: true`):
    - `CLAIM.json`: `72` B, SHA256 `99bdcd855bae89ee8817b53a6b959f4f16303ea5fca55738498ea073f548896d`
    - `COMPLETE.json`: `177` B, SHA256 `58613e7edbb199ea1c0901f6ec6c153d759dabd1e4c060485e094d95bbfe9df8`
    - `calibration.json`: `71,717,136` B, SHA256 `3e4ccd2fe377a0af6ecc39f645b82152caf3bd14a4798fd77bcc5ba9020e3187`
    - `REPORT.md`: `73,157,706` B, SHA256 `408d144601167a3255650c1a926713e65df6339653c77fc4436f030b041688dd`
  - Installed into `experiments/exp7/campaign/statistics/calibration/` via `copy_accepted_calibration`, with `CLAIM.json`, `COMPLETE.json`, and `calibration.json` committed to Git prior to `exp7-preregistered` so `Campaign.statistics_bindings` and `Trust.tag('prereg')` verify the exact calibration blob in the preregistration tag.

## 5. Module-by-module build and full-default adversarial synthetic freeze (`freeze-001`)

- All 75 build tasks (`271` files: `241` literal + `30` amended in `experiments/exp7/build/AMENDMENTS.json` across `CALIBRATION-1` and `FREEZE-1`) are complete and independently reviewed.
- Full-default synthetic freeze `freeze-001` (`experiments/exp7/freeze/freeze-001/`, independently reviewed and accepted at `45674e88f2ecea62faf979f88ee641ded20e530f`):
  - `task-0001.json` and `task-0131.json`: `400/400` tests passed, byte-identical SHA256 `4e79f8a529b78edffcca27d0285aa0a9ca3110f42daa1c81e8fbe0fd41a511ee`
  - `worlds.json`: `40/40` synthetic worlds `COMPLETE`, SHA256 `434975391e696eadc0ecef4e622e9a8f9b055aa98f5752c2e8bc9ff185a41b4e`
  - `import-scan.json`: `state: "COMPLETE"`, SHA256 `f58940a9f554645b08de63f2a4012e339c299a48f0f140992f95154b050a666b`
  - `read-scan.json`: `state: "COMPLETE"`, SHA256 `3b0093faa6f688bb9fa9e74df364c132f4520d1426a95224afac3455341f5570`
  - `determinism/determinism.json`: `byte_identical: true`, worker output SHA256 `0038db847f4c87f9b79e19ad16def07bcfe20904abb1bd71e1135620301d9e45`
  - `mutations/results.json`: `43/43` mutants `KILLED`, SHA256 `28f77d963dce1952bb1ff259a253bcb821eaccec55d3bd2a638216129691b237`
  - `COMPLETE.json`: `state: "COMPLETE"`, `synthetic_only: true`, `mutations: 43`, SHA256 `4fcba8c7001fd2ff71e40bcc968095446b0f50b8addf6584a77346965c449dd2`
