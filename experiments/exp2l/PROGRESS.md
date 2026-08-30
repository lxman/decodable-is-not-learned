# Experiment 2l — build ledger

## Task 1: `battery_2l.py`

Built: constants (`EXP2L`, `EXPERIMENTS`, `REPO`, `RESULTS`,
`HUB_INVENTORY_PATH`, `CHECKPOINTS_PATH`, `CHECKPOINTS_2L_SHA256`,
`FAMILY`, `SIZE_OUT`, `REPO_13B`, `REV_13B_ENDPOINT`, `REV_13B_STEP0`,
`REV_13B_MAIN`, `ENDPOINT_STEP_13B`, `STEP0`, `GRID_13B`,
`PREREG_TAG_2L`, `ENDPOINT_SEAL_TAG_2L`, `INSTRUMENT_BLOBS_2L`,
`N_ITEMS`, `STRATA_RUNGS`, `R_CAP_2K`, `BATCH_SIZE_2L`,
`SEAL_2K_SHA256`, `SEAL_2I_SHA256`, `PREDICTOR_TAGS_2L`,
`PREDICTOR_SHA_2L`, `CKPT_CACHE_2L`, `FROZEN_FILES_2L`,
`FROZEN_SHA256_2L` (empty, pinned Task 5), `GATE1_FIELDS_2L`), the
inventory + manifest builder (`trained_steps_13b`, `n_trained_13b`,
`load_inventory_13b`, `refresh_inventory_13b`, `build_manifest_13b`,
`write_manifest`, `load_manifest_13b`, `entry_13b`, `entry_main_13b`),
the 13B-keyed loader family (`_cache_dir_13b`, `download_entry_13b`,
`clean_dir_13b`, `load_checkpoint_13b`, `load_thin_13b`,
`load_tokenizer_13b`, `free_checkpoint_13b`), the sweep/endpoint path
helpers (`sweep_dir`, `record_path`, `checkpoint_record_path`,
`gate1_path`, `halt_marker_path`, `endpoint_dir`,
`endpoint_record_path`, `rung_set_path`, `power_path`), the rung-set
rule (`rung_set_from_counts_2l`), the endpoint composite sha
(`composite_sha`, `endpoint_files`, `endpoint_sha256`), the record
stamps (`item_record_2l`, `checkpoint_record_2l`), the gate-1 checkers
(`gate1_failures_13b`, `gate1_rederive_13b`) and the pins/prereg
binding (`frozen_from_disk`, `check_frozen_2l`, `require_prereg_2l`).

Zero model contact in any test: no `torch`, no `transformers`, no
`huggingface_hub` imported at module top level (checked by
`test_loader_family_imports_torch_lazily`, an AST walk of the finished
file); the four MODEL CONTACT functions
(`download_entry_13b`/`clean_dir_13b`'s caller/`load_checkpoint_13b`/
`load_thin_13b`) import those libraries lazily inside their bodies and
are never executed by a test.

### Step 4: the one network call — the Hub inventory scan

`python -m experiments.exp2l.battery_2l --scan`, ~metadata only,
completed clean on the first run (the refuse-if-exists guard means it
cannot run twice). Facts:

- **718 revisions** on `allenai/OLMo-2-1124-13B` (646 stage-1
  checkpoints + stage-2 ingredient branches + `main`, matching the
  design's disclosed order of magnitude).
- Endpoint (`stage1-step596057-tokens5001B`) commit:
  `08d2aca2e28ab67ad859793f76ef5c923e94ac11` — matches the design's
  2026-08-30 reading (`08d2aca2…`).
- `main` commit: `3fefddc1bf18a30e1d9b91000271630718f2aa8b` — matches
  the design's reading (`3fefddc1…`).
- Step-0 (`stage1-step0-tokens0B`, the real init referent) commit:
  `ac13d34ab7cc393bd8de803dbbc382c396ac35a3`.
- `final_duplicates`: `[]` — the endpoint revision has no stage-2
  ingredient copy on this repo (unlike 2i's 7B case).
- `signature_equals_main`: `False` — the endpoint's file signature
  differs from `main`'s.
- Shard naming: `model-000NN-of-00012.safetensors` — `ck.candidate`
  (frozen, imported unmodified from `checkpoints_2g`) accepted it
  without change; **no STOP triggered**.
- Shard count per entry: **12** safetensors shards + 1
  `model.safetensors.index.json` = 13 files, uniformly across all 16
  grid points, step 0, and `main` (verified: every one of the 17
  `entries_13b` rows plus `main` carries exactly 12 `lfs_sha256`
  entries).
- Per-revision LFS total: **≈ 54.86 GB** (54,864,845,120 bytes on the
  endpoint, step 0, and `main` alike — the design's ≈ 55 GB estimate
  confirmed).

`python -m experiments.exp2l.battery_2l --manifest` built
`checkpoints_2l.json` (17 entries: 16 `GRID_13B` points + step 0),
printed sha256
`3dd466f5130c1406c84d8bc856e5f98b0db0f73782119a0b2c0dffa7e424b83c`,
pasted into `CHECKPOINTS_2L_SHA256` as a literal, and **re-run once
more with the literal in place: the sha was unchanged** (byte-
idempotent manifest build). `test_committed_manifest_is_pinned_and_
consistent` is live (not skipped) as of this commit.

Zero model contact beyond the one metadata scan: no weight bytes were
downloaded, no loader function was called.

### Findings/rulings pending

None. No shard-naming or count surprise, no STOP. `SEAL_2K_SHA256` /
`SEAL_2I_SHA256` (2k's and 2i's committed predictor seals, transcribed
from the brief) matched the committed seal files on disk exactly —
`test_seal_literals_match_the_committed_seals` passed on the first
run.

### Test run

`pytest experiments/exp2l/tests/test_battery_2l.py -q`: 21 passed, 0
skipped (post-scan; 20 passed / 1 skipped pre-scan, the skip being
`test_committed_manifest_is_pinned_and_consistent` before
`CHECKPOINTS_2L_SHA256` was pinned).

zero model contact; one network call — the inventory scan,
`ef458b435ddcc5c415dbe719d2bb499d7cbb876b9f958016e9b15947e1ffc8f2`
(`hub_inventory_olmo13b.json`'s sha256).
