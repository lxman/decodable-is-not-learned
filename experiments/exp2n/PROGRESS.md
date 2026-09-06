# Experiment 2n — build ledger

## Task 1 (2026-09-06): `battery_2n.py`

Built: constants (ONE repo `common-pile/comma-v0.1-1t`, the 24-point
uniform `GRID_COMMA`, the 12-point every-40k `EVERY40K_SUBSET_2N`
grid-density control, the prereg/endpoint-seal tags, the four
tag-bound instrument blobs, Comma's own tokenizer facts — pad 0
DECLARED, unk 1, bos 2, eos 3 — the two predictor seal literals +
`PREDICTOR_SHA_2N` with its `"2n|"` prefix); the ONE-repo inventory
loader and the ONE Hub scan (`refresh_inventory_comma`, skipping
`pr/*` refs); the manifest builder (`build_manifest_comma`) over
`ck.candidate`/`ck.signature` with a WEIGHT-BEARING `main` (unlike
2m's weightless checkpoints-repo `main`) — duplicate-signature
refusal now runs across every scanned revision INCLUDING `main`
itself, so a grid revision whose shards duplicate `main`'s refuses;
its other refusals (duplicate grid points, missing/duplicate stage-1
endpoint, missing/duplicate stage-2 endpoint, missing main) and the
sha-pinned loader (`load_manifest_comma`); the entry accessors
(`entry_comma`, `entry_stage2_comma`, `entry_main_comma`,
`entry_which_comma` over `stage1_final`/`stage2_final`/`main`); the
NEW render + stop-id layer (dials n, o): `eos_facts_2n`,
`set_eos_stop_2n` (overrides `model.generation_config.eos_token_id`
to Comma's real EOS, 3, and asserts it reads back — config.json's own
`eos_token_id` is 2, the tokenizer's BOS, a LlamaConfig default),
`render_2n` (prepends `BOS_TOKEN_2N` to every prompt) and `BosRunner`
(wraps a generator to apply the render before `generate`); the Comma
loader family (`download_entry_comma`, `clean_dir_comma`,
`load_checkpoint_comma`, `load_tokenizer_comma` + `check_tokenizer_2n`,
`load_thin_comma`, `load_twin_comma`, `free_checkpoint_comma`), each
of the three model loaders calling `set_eos_stop_2n` right after
`.to(device).eval()` and merging its facts into `info`; the sweep/
endpoint paths incl. the twin's; the rung-set rule
(`rung_set_from_counts_2n`, key `R_COMMA`); the record stamps
(`item_record_2n`/`endpoint_item_record_2n` with the `dtype` override
AND the new `render`/`eos_stop_id` fields, `checkpoint_record_2n`/
`twin_checkpoint_record_2n` with the new `config_eos_token_id`/
`generation_eos_token_id` fields); the gate-1 checkers
(`gate1_failures_comma`, `gate1_rederive_comma`); the endpoint
composite sha (`composite_sha`, `endpoint_files`, `endpoint_sha256`,
104 files: 3 whichs x 34 rungs + rung set + power record); the
frozen-file pins (`FROZEN_FILES_2N` = 2m's 48 + 2m's four
now-frozen instrument blobs + `power_2n.py` + `make_referents_2n.py`
= 54, `frozen_from_disk`, `check_frozen_2n` — `FROZEN_SHA256_2N`
stays empty until Task 5); and the prereg blob binding
(`require_prereg_2n`).

Also created: `experiments/exp2n/__init__.py`,
`experiments/exp2n/run/__init__.py`,
`experiments/exp2n/tests/__init__.py`,
`experiments/exp2n/tests/conftest.py` (2m's file, `2m`→`2n`); appended
the named 2n log-file list (incl. `mutation_*.log`, unlike 2m/2l's
committed-mutation-log convention) to `.gitignore` after the 2m block.

Zero model contact, zero weight download. The one network call was
Step 5's Hub metadata scan (`--scan`), `huggingface_hub.HfApi` only —
no weights, no tokenizer, no model load.

### Step 5: the one Hub scan + manifest

```
common-pile/comma-v0.1-1t 56 revisions
sha256 cdfc33964dbb0354bf7228b1a8bcdfcd41fc334fa37829fac2cb370c6e4eff6f
```

```
entries 24 ; endpoint commit e295235994f32d763c359d324265a176e591f632 ; stage2_final commit 0d77335ff4b7219b1766ceb7103d4f2d780fccad ; main commit 5af409118da3cbea94684c622c66ab8c2ea7f4fe ; endpoint_duplicates []
sha256 ff7996d141fe8e4f0791b143b573c538062bbd4be776fdcf27317d58e90943d5
```

56 revisions matches the design session's count exactly (46 stage-1 +
9 stage-2 + `main`, `pr/1` skipped) — no STOP condition was hit. The
endpoint commit starts with the brief's pinned prefix
(`e295235994`) and the stage2_final commit with `0d77335ff4`; the
`main` commit reproduces the design doc's literal
(`5af409118da3cbea94684c622c66ab8c2ea7f4fe`) exactly. Every
`GRID_COMMA` step matched exactly one `stage1-step<NNNNNN>-tokens<N>B`
branch; `main` carries its own three shards, distinct from every grid
revision's (`endpoint_duplicates` empty). `CHECKPOINTS_2N_SHA256`
pasted as
`ff7996d141fe8e4f0791b143b573c538062bbd4be776fdcf27317d58e90943d5`;
the test's `.startswith` placeholders for the endpoint/stage2_final
commits were tightened to the full 40-char literals once known.

### Tests

Step 2 (RED, before `battery_2n.py` existed):
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2n/tests/test_battery_2n.py -q -x`
— collection ImportError on `experiments.exp2n.battery_2n`, as
expected.

Step 4 (GREEN, before Step 5's scan): 28 passed / 1 skipped
(`test_committed_manifest_is_pinned_and_consistent`, skipped because
`CHECKPOINTS_2N_SHA256` was still empty).

Step 5 (GREEN, after the scan + manifest):
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2n/tests/test_battery_2n.py -q`
— 29 passed, 0 skipped.

Full `experiments/exp2n/tests/` directory: 29 passed, 0 skipped.

### Process notes

- `build_manifest_comma`'s `main_files = table[REV_MAIN_2N]["files"]`
  is dereferenced unconditionally at the top of the function (given
  verbatim in the brief), before any of the later named-revision
  refusal checks run. A hand-built inventory missing `main` entirely
  therefore raises `KeyError`, not the `ValueError` its `stage2_final`
  sibling raises via the `if rev not in table` guard later in the
  function — the `test_build_manifest_comma_refusals` test asserts
  `KeyError` for `drop_main=True` rather than mirroring 2m's
  `ValueError, match="base"` shape. This is a real asymmetry in the
  given code, not something I introduced; it is defensible in
  production (`main` is this repo's default branch and is always
  present in a real Hub scan — the guard on `stage2_final` matters
  because that revision genuinely could be absent from an inventory,
  `main` structurally cannot). Flagged for the reviewer rather than
  silently changed.
- The `_inventory()` test fixture computes stage-1 "tokens" labels via
  `round(step * TOKENS_PER_STEP_2N / 1e9)`, not the brief's literal
  `//` (floor) — floor division gives 964 at step 460,000, not the
  965 the pinned `REV_ENDPOINT_2N` literal requires (round gives 965,
  and 21 at step 10,000, matching the design doc's real label). This
  only affects the test fixture's revision-string generation, never
  production code (which reads real Hub revision names verbatim and
  never computes a tokens label).
