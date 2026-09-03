# Experiment 2m — build ledger

## Task 1 (2026-09-03): `battery_2m.py`

Built: constants (two repos, the 26-point `GRID_3B`, the 21-point
`LOG_HEAD_SUBSET_2M`, the prereg/endpoint-seal tags, the four
tag-bound instrument blobs, the tokenizer facts, the two predictor
seal literals + `PREDICTOR_SHA_2M`); the two-repo inventory loader
and the ONE Hub scan (`refresh_inventory_3b`); the manifest builder
(`build_manifest_3b`) over `ck.candidate`/`ck.signature`, its
refusals (duplicate grid points, missing/duplicate stage-1 endpoint,
missing/duplicate stage-3 endpoint, missing base), and the
sha-pinned loader (`load_manifest_3b`); the entry accessors; the
SmolLM3 loader family (`download_entry_3b`, `clean_dir_3b`,
`load_checkpoint_3b`, `load_tokenizer_3b` + `check_tokenizer_2m`,
`load_thin_3b`, `load_twin_3b`, `free_checkpoint_3b`) with its own
tokenizer pins (left padding, SmolLM3's own pad id, the eos id, no
prepended BOS) distinct from OLMo-2's in `battery_2i`; the sweep/
endpoint paths incl. the twin's; the rung-set rule
(`rung_set_from_counts_2m`); the record stamps
(`item_record_2m`/`endpoint_item_record_2m` with the `dtype`
override, `checkpoint_record_2m`, `twin_checkpoint_record_2m`); the
gate-1 checkers (`gate1_failures_3b`, `gate1_rederive_3b`); the
endpoint composite sha (`composite_sha`, `endpoint_files`,
`endpoint_sha256`); the frozen-file pins (`FROZEN_FILES_2M`,
`frozen_from_disk`, `check_frozen_2m` — `FROZEN_SHA256_2M` stays
empty until Task 5); and the prereg blob binding
(`require_prereg_2m`).

Also created: `experiments/exp2m/__init__.py`,
`experiments/exp2m/run/__init__.py`,
`experiments/exp2m/tests/__init__.py`,
`experiments/exp2m/tests/conftest.py` (2l's file, `2l`→`2m`); appended
the named 2m log-file list to `.gitignore` (2l D-1's pattern).

Zero model contact, zero weight download. The one network call was
Step 4's Hub metadata scan (`--scan`), `huggingface_hub.HfApi` only —
no weights, no tokenizer, no model load.

### Step 4: the one Hub scan + manifest

```
HuggingFaceTB/SmolLM3-3B-checkpoints 133 revisions; HuggingFaceTB/SmolLM3-3B-Base 1
sha256 bed5667a53257bd14ebff4f6e37c2772d0b8fd92ffacae8b20d9464547fce939
```

```
entries 26 ; endpoint commit d07a5a83dd011f3f084e9d2f1b47f51e524ca8d4 ; stage3_final commit 20e7817e636d6b1f63cffbee0f384721b1f4bb67 ; base commit d78a42f79198603e614095753484a04c10c2b940 ; endpoint_duplicates []
sha256 1a6dd3361b3e75a7ccc61e8f86c50ef59350bc3429fc4cb3bdcdb2be5ca599bd
```

The endpoint commit reproduces the brief's pinned literal
(`d07a5a83dd011f3f084e9d2f1b47f51e524ca8d4`) exactly; every `GRID_3B`
step matched exactly one `stage1-step-<N>` branch; no STOP condition
was hit. `CHECKPOINTS_2M_SHA256` pasted as
`1a6dd3361b3e75a7ccc61e8f86c50ef59350bc3429fc4cb3bdcdb2be5ca599bd`.

### Tests

`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2m/tests/test_battery_2m.py -q`
— 24 passed / 1 skipped before Step 4 (manifest not yet pinned); 25
passed / 0 skipped after.

## Task 2 (2026-09-03): the stage runners

Built: `run/endpoint_2m.py` (three thin loads — `stage1_final`,
`stage3_final`, `base` — over all 34 rungs; `require_predictor_seals_2m`
re-derives `PREDICTOR_SHA_2M` from 2k's and 2i's sealed artifacts rather
than trusting the literal; the rung set is fixed from `stage1_final`
counts alone, the other two whichs are descriptive; skip-if-exists +
dry-run; an exception mid-which leaves no rung set); `run/sweep_2m.py`
(gate 1 — the endpoint re-derived through the candidate-file loader and
diffed against the committed `stage1_final` records — then the seeded
`from_config` twin, then the 25 remaining grid steps ascending; the
endpoint seal gate binds 102 endpoint records + the rung set + the
power record; halt-and-refuse-resume on a gate-1 mismatch; resume
skips complete steps and re-enters incomplete ones, including the
twin); `run/preflight_2m.py` (the base through the thin loader and one
grid checkpoint through the candidate-file loader, each under a plain
and a `<|begin_of_text|>`-prefixed render, with a per-load fp16
finiteness probe that refuses on any non-finite logit; asserts nothing
was written under `results/`); `run/commit_watcher_2m.sh` (2l's script,
`2l`→`2m` throughout, `chmod +x`); the stub `analyze_2m.py` (only
`_endpoint_seal_paths_2m`, Task 3 will replace the file keeping that
function byte-identical); `tests/test_stages_2m.py` (fake loaders, no
torch, no network, no frozen tree touched).

All four runner/test files transcribed byte-for-byte from the task
brief with one exception, found and fixed while running Step 7:
`test_preflight_prints_both_renders_and_writes_nothing` and
`test_preflight_refuses_if_it_wrote_under_results` both KeyErrored,
because the shared `FakeRunner(amap, 0.5)` instance is reused across
preflight's plain and `bos `-prefixed render passes (one
`loaders["runner"]` call per model load), and at `frac=0.5` with only
20 items every index does a real lookup (`(i % 1000)/1000 < 0.5` for
i in 0..19) — but `amap` (from `_amap_and_battery()`) only carried
unprefixed prompt keys, so every BOS-prefixed prompt was a miss.
Fixed by extending `amap` inside `_preflight_loaders` with a
BOS-prefixed copy of every entry (same answers) — `FakeRunner` itself
is frozen and untouched; no production code in `preflight_2m.py`
changed.

### Tests

Step 2 (before the runners existed):
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2m/tests/test_stages_2m.py -q -x`
— collection ImportError on `experiments.exp2m.run.endpoint_2m`, as
expected.

Step 7 (fast suite):
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2m/tests/test_stages_2m.py -q -m "not slow"`
— 21 passed, 1 deselected.

Step 7 (slow pair, real git against the committed 2k/2i seal tags):
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2m/tests/test_stages_2m.py -q -m slow`
— 1 passed, 21 deselected.

Full `experiments/exp2m/tests/` (fast): 46 passed, 1 deselected.
