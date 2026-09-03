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

## Task 3 (2026-09-03): `analyze_2m.py` + `make_referents_2m.py`

Built (replacing Task 2's stub, `_endpoint_seal_paths_2m` kept
byte-identical): `analyze_2m.py` — the pins (`check_imports_2m`, 2j's
import-surface rule from commit one); the record-failure functions
(`_record_common_failures_2m`, `endpoint_record_failures_2m`,
`step_record_failures_2m`, `checkpoint_record_failures_2m`,
`twin_checkpoint_record_failures_2m`) with the `dtype` pin and the
twin's bespoke shape; the SmolLM3 loaders (`load_endpoint_which_2m`,
`load_sweep_3b` over the 26-point grid + twin); the outcomes
(`outcomes_3b` over the grid or the log-head subset, `rung_level_3b`,
`_first_correct_outcome_3b`, `collapses_3b`, `non_monotone_3b`,
`ceiling_fraction_3b`); the rung set (`_load_rung_set_2m` +
`_check_rung_set_vs_endpoint_2m` / `_check_rung_set_derivation_2m` /
`_check_rung_set_endpoint_shas_2m`); the power record
(`load_power_2m`, `check_power_claims_2m` — B on 2g's BASE strata per
dial b, not a composite); the predictors through their own seals
(`load_predictors_2m` — x_A^(256) via 2k's `load_tier_2k` +
`seal_failures_2k`, x_B via 2i's `sampler_counts_olmo` after
`load_predictor_records_2i` + `_check_predictor_seal_sampling`, cross-
checked by `_check_predictor_counts_2i`); the secondaries
(`s3_paired_difference_2m` — the paired item bootstrap of T_B − T_A on
one tie structure, `s4_matched_2m`, `s5_answer_prior_2m`,
`load_committed_outcomes_2m` + `s8_outcome_order_2m` — new, reads each
of the four committed big-model orders against 3B's, `_extra_rungs_2m`);
the tree (`verdict_tree_2m` → SHARED / PYTHIA-ONLY / OLMO-ONLY /
NEITHER, `verdict_2m`, `_licensed_2m`) with 2m's disclosures
(`DISCLOSURE_THIN_2M`, `DISCLOSURE_THIN_ELIGIBLE_PREFIX_2M`,
`DISCLOSURE_UNDERPOWERED_2M`, `DISCLOSURE_UNDEFINED_2M`); `run()`
(halt scan first, pins/prereg/manifest/referents, upstream pins,
battery/floors/verify/strata, the predictors, the SmolLM3 endpoint
stage + rung set + power record + seal, gate 1 attested then
re-derived, the gating core with both tests UNCONDITIONED on the base
strata, S1–S8 + the paired difference + extra rungs + sensitivities,
the import-surface re-check after the secondaries). Also built
`make_referents_2m.py` (`referent_files` = 2l's whole pre-campaign
list + 2l's OWN campaign artifacts — endpoint records, rung set, power
record, sweep tree, gate1.json, verdict.json, since S8 reads the 13B
outcome through 2l's frozen loaders — + 2l's four instrument blobs +
2m's own `checkpoints_2m.json`, `hub_inventory_smollm3.json`,
`power_2m.py`; `build`, `check_referents`); `tests/test_analyze_2m.py`.

`power_2m.py` created as a docstring-only STUB (2l's Task 3 precedent
exactly: `git show a8566c61:experiments/exp2l/power_2l.py`) — 2l's
Task 4 equivalent (power record + `block_sd_A` + worlds + totality)
owns this file's real content. `battery_2m.FROZEN_FILES_2M` (Task 1)
and `make_referents_2m.referent_files()` (this task, verbatim from the
brief) both reference `experiments/exp2m/power_2m.py` unconditionally
but never import it, so the placeholder only needs to exist on disk
for `make_referents_2m.build()` — called by the referents test — to
reach GREEN; nothing in `analyze_2m.py` or `make_referents_2m.py` reads
its contents. Left uncommitted-as-final on purpose: Task 4 replaces it.

Two test-side corrections, both the same root cause as one already
seen in Task 2 — the brief's test file was transcribed with cases
copied from LATER stages of exp2l's own test suite (post-Task-5, once
`IMPORTED_SHA256_2L`/`REFERENTS_2L_SHA256` were real pinned values),
which don't hold at Task 3 for 2m:

1. `test_endpoint_record_failures_2m_pins_every_field_incl_dtype`'s
   `seal_tag` mutation case used `bl.PREDICTOR_TAGS_2L` as the "wrong"
   value — but `PREDICTOR_TAGS_2L` and `PREDICTOR_TAGS_2M` are BOTH
   `f"{bk.SEAL_TAG_2K}+{bi.PREDICTOR_SEAL_TAG}"` (no `2l`/`2m` component
   in the formula), so they are byte-identical strings and the mutation
   was a no-op. exp2l's OWN test avoids exactly this by using
   `bi.PREDICTOR_SEAL_TAG` (a real single-tag string) for the analogous
   endpoint-record case; applied the same fix here.
2. `test_run_import_surface_entry_forced_exception` and
   `test_run_referent_manifest_check_forced_exception` call `an.run()`
   bare and rely on `imports_pinned`/`referents_sha` defaulting to a
   value that reaches `check_imports_2m()` / `mkr.check_referents()`.
   That default only resolves that way once `IMPORTED_SHA256_2M` /
   `REFERENTS_2M_SHA256` are real pinned values (Task 5); at Task 3 both
   are `None`, so `run()`'s default takes the "not pinned (build
   incomplete)" branch and never calls either function, and the
   injected exception is never seen. Confirmed by git history: both
   tests were added to exp2l's suite at its "build closed" commit
   (`62489985`), after `IMPORTED_SHA256_2L` was pinned — 2l's own
   Task-3-era test file did not contain them. Fixed by passing
   `imports_pinned=True` / `referents_sha="0" * 64` explicitly so each
   test reaches the code path it actually means to exercise; the
   assertions themselves are untouched.

No production code was changed for either correction — only the two
test files' fixture values.

### Pre-tag disclosure (design §2 / checklist 27)

`an.run()` executed on the real committed tree many times during this
task's test runs (no `results/` directory exists yet, no SmolLM3
record of any kind, no prereg tag cut). A representative bare
`an.run(n_perm=20, n_boot=5)` call prints:

```
verdict: INSUFFICIENT_DATA
n_failures: 14
 - 2m frozen modules: RuntimeError: FROZEN_SHA256_2M is empty — not pinned (build incomplete)
 - 2m import surface: not pinned (build incomplete)
 - 2m prereg tag: RuntimeError: preregistration tag exp2m-preregistered does not exist
 - 2m referent manifest: not pinned (build incomplete)
 - 2m rung set file: FileNotFoundError: .../experiments/exp2m/results/endpoint/rung_set_2m.json
 - 2m power record: ValueError: rung set missing
 - 2m endpoint seal binding: the tag 'exp2m-endpoint-sealed' does not exist
 - 2m endpoint stage1_final/stage3_final/base: FileNotFoundError (endpoint records missing)
 - 2m endpoint composite sha: FileNotFoundError
 - 2m gate 1 smollm3_3b: record missing
```

The forced-exception tests (`test_run_forced_exceptions_on_the_real_tree_are_graceful`
×6, `test_run_strata_pins_forced_exception`, `test_run_frozen_check_
forced_exception`, `test_run_import_surface_entry_forced_exception`,
`test_run_referent_manifest_check_forced_exception` — 10 real-tree
`an.run()` calls in total) each land the same way: `verdict ==
"INSUFFICIENT_DATA"`, with the injected label present among
`referents["failures"]`. No statistic of any kind is computed or
printed — the gating core (`_core`) is never reached because `failures`
is non-empty by the time it would run. Nothing here is a projection or
a result; it is the expected shape of every pre-tag execution while
Tasks 4–5 (power record, `FROZEN_SHA256_2M`, `IMPORTED_SHA256_2M`,
`REFERENTS_2M_SHA256`, the prereg tag) remain unbuilt.

### Tests

Step 5:
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2m/tests/test_analyze_2m.py experiments/exp2m/tests/test_stages_2m.py experiments/exp2m/tests/test_battery_2m.py -q -m "not slow"`
— 97 passed, 1 deselected (≈ 3 min; the real-tree cases in
`test_analyze_2m.py` — `test_load_predictors_2m_on_the_real_trees_is_clean`,
the six `test_run_forced_exceptions_on_the_real_tree_are_graceful`
cases, `test_s4_matched_2m_uses_2k_rule_and_2j_blocks`,
`test_s5_answer_prior_2m_is_2j_functional_on_2i_rows` — together with
the rest of `test_analyze_2m.py` ran in ≈ 157 s of the total).
