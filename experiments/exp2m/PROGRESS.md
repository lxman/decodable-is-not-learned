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

## Task 4 (2026-09-03): `power_2m.py`, the worlds, totality, power tests, cold battery

Built (Step 1-6, transcribed from the brief verbatim apart from the
disclosed corrections below): `power_2m.py` (`block_sd_A` — 2j's
`t_only` on each of x_A's four 64-draw blocks against outcomes drawn
from the endpoint-bounded latent, at D=.15 and at the null; `main` —
2i's `_one_test_power` run TWICE on the REAL sealed predictors, Test A
(x_A^(256)) and Test B (x_B), BOTH on 2g's plain base strata, dial b),
wholesale-replacing the Task-3 docstring-only stub; `tests/full_shape.py`
(the 22-world SmolLM3 builder — three endpoint whichs, 26-step sweep,
twin, gate 1, rung set, power record; the residualized-latent
construction so each single-predictor mode's rank is orthogonalized
against the OTHER predictor inside every base stratum, since 2i
disclosed x_A/x_B correlated at rho .06-.32 within them);
`tests/test_full_shape_2m.py` (every terminal end to end, W1's full
secondary shape, W2/W3/W5/W6/W18/W19 spot checks, the strict-JSON NaN
case, the production S8 loader); `tests/test_totality_2m.py` and
`verify_referents_2m.py` (2l's files mirrored per the brief's exact
substitution/addition lists — diff summaries below).

### Task-4 ruling carried out (disclosed per the brief's instruction)

`FROZEN_SHA256_2M` is empty and `IMPORTED_SHA256_2M` is `None` until
Task 5, so a bare `an.run()` call lands every synthetic world on
"2m frozen modules"/"not pinned" INSUFFICIENT_DATA regardless of mode
— the same shape Task 3 already documented on the real (pre-campaign)
tree above. Per the ruling: `full_shape.run_world` and the two direct
`an.run()` calls in `test_full_shape_2m.py` (`test_w18_verdict_json_
is_strict_with_a_nan_secondary`, `test_s8_production_loader_once`) pass
`frozen_check=(None if bm.FROZEN_SHA256_2M else (lambda: None))` and
`imports_pinned=(True if an.IMPORTED_SHA256_2M is not None else
False)`; `test_totality_2m.py`'s `_run` sets the same two via
`kw.setdefault`. Both expressions revert to the real checks
automatically once Task 5 pins the two literals — no edit needed here
then (2l's own Task 5 dropped the equivalent bypass).

### Test-side corrections (disclosed; no production code touched)

1. **`test_totality_2m.py`'s `_run`** — the brief's literal call
   hardcodes `s8_loader=fs.s8_cached` as an explicit keyword AND
   unpacks `**kw`; the moment a case (the new `test_s8_loader_forced_
   exception`) passes `s8_loader` through `kw`, that raises `TypeError:
   got multiple values for keyword argument 's8_loader'` before `an.run`
   is even reached. Fixed by `kw.setdefault("s8_loader", fs.s8_cached)`
   instead of the hardcoded keyword — same default for every other
   case, overridable by the one that needs to.
2. **`test_check_imports_2m_exit_forced_exception` /
   `test_check_imports_2m_post_secondaries_forced_exception`** — found
   only running the FULL suite, not this file alone. The brief's
   pattern (`real = an.check_imports_2m; ...; return real()` for the
   "passing" calls) depends on the REAL `check_imports_2m()` actually
   succeeding, which depends on which OTHER `experiments/*` modules
   already sit in `sys.modules` — a property of pytest's collection
   order across the whole suite (e.g. `test_stages_2m.py` importing
   `run/preflight_2m.py`, explicitly not yet covered before Task 5),
   not of this file in isolation, where both passed. A first fix
   (monkeypatching `IMPORTED_SHA256_2M` to a dict covering just
   `experiments/exp2m/__init__.py`) also passed in isolation but broke
   again in the full-suite run for the same underlying reason. Since
   what these two cases exist to exercise is `run()`'s CALL-SITE
   SEQUENCING (entry -> exit -> post-secondaries — Task 5/the freeze's
   target), not `check_imports_2m`'s own correctness, the fix replaces
   the "passing" calls with a plain no-op and passes `imports_pinned=
   True` explicitly to `_run` (the default stays `False` while
   `IMPORTED_SHA256_2M` is `None`). Neither assertion was weakened.

### Tests

`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2m/tests/test_power_2m.py -q` — 3 passed in 44 s.
`... pytest experiments/exp2m/tests/test_totality_2m.py -q` — 31 passed in 332 s (0:05:32) after the corrections above.
`... pytest experiments/exp2m/tests/test_full_shape_2m.py -q` — 10 passed in 649 s (0:10:49).
`... pytest experiments/exp2m/tests -q -m "not slow"` (the whole suite, once, per Step 7) — 141 passed, 1 deselected in 1212 s (0:20:12).
`... python -m experiments.exp2m.verify_referents_2m` — `referent battery: 11/13` (items 3, 12 skip pending Task 5); item 13 (S8's four committed outcomes) printed per-source rung/n_pos counts: pythia_2.8b 7 rungs/1769, pythia_6.9b 8 rungs/2088, olmo2_7b 34 rungs/8793, olmo2_13b 34 rungs/8737.

Every world's terminal matched `world_specs()`'s expectation (`test_every_terminal_reached`, all 5 `WORLDS_2M` terminals covered). W1/W2/W3's printed statistics, from a standalone re-run of `write_world_2m`/`run_world` at the default `n_perm=200`:
- W1 PYTHIA-ONLY: verdict PYTHIA-ONLY — T_A=.7124 p_A=.004975 fires_A=True; T_B=.0095 p_B=.2289 fires_B=False
- W2 OLMO-ONLY: verdict OLMO-ONLY — T_A=.0251 p_A=.0199 fires_A=False; T_B=.6527 p_B=.004975 fires_B=True
- W3 SHARED: verdict SHARED — T_A=.5942 p_A=.004975 fires_A=True; T_B=.5367 p_B=.004975 fires_B=True

No world landed the wrong terminal (no leak found); nothing was loosened to make a world pass.

Files changed: `experiments/exp2m/power_2m.py` (replaced wholesale),
`experiments/exp2m/verify_referents_2m.py` (new),
`experiments/exp2m/tests/full_shape.py` (new),
`experiments/exp2m/tests/test_full_shape_2m.py` (new),
`experiments/exp2m/tests/test_totality_2m.py` (new),
`experiments/exp2m/tests/test_power_2m.py` (new). Nothing outside
`experiments/exp2m` touched; no Task 1-3 file edited.

## Task 5: the real-tree closure — frozen literal, import-surface pin, pre-campaign manifest, mutation harness, read sweep

ZERO model contact, ZERO network end to end. Python
`~/emergence-lab/.venv/bin/python` with `PYTHONDONTWRITEBYTECODE=1`,
run from the repo root with `-p no:cacheprovider`; git
`/opt/homebrew/bin/git`. Started at HEAD `1bf59266`.

### Step 1 — `FROZEN_SHA256_2M` pinned as a literal (48 modules)

`frozen_from_disk()` over `FROZEN_FILES_2M` = 2l's 42 frozen modules +
2l's four tag-bound instrument blobs (2l is closed; frozen bytes to 2m)
+ 2m's own `power_2m.py` and `make_referents_2m.py` = **48**, pasted in
`FROZEN_FILES_2M` order. `check_frozen_2m()` passes for real.

The two `if not bm.FROZEN_SHA256_2M:` monkeypatch stand-ins dropped
(`test_stages_2m.py::_blobs_that_exist`, `test_power_2m.py::_small`).
`test_analyze_2m.py`'s autouse `_frozen_pin` fixture STAYS (it exercises
the checker, 2l's precedent), as do `test_battery_2m.py`'s two
deliberate `FROZEN_SHA256_2M` monkeypatches (the empty-pin refusal and
the drift raise). `test_battery_2m.py + test_stages_2m.py +
test_power_2m.py -m "not slow"`: 49 passed, 1 deselected, 64 s.
Commit `7e1e8a2d`.

**After this, `power_2m.py` and `make_referents_2m.py` cannot change
without re-pinning** — and Step 3's `N_FILES_2M` literal does exactly
that, so `make_referents_2m.py`'s one entry inside `FROZEN_SHA256_2M`
was re-pinned (`5f07bbd1…` → `36340a89…`, marked in the source). 2l's
Task 5 did the same one-line re-pin.

### Step 2 — the import-surface scan (`IMPORTED_SHA256_2M`, 4 modules)

`tests/import_scan_2m.py` = 2l's tool with 2m's roots, 2l's own
residual pin folded into `covered` beside 2j's and 2k's, and the six 2m
stage tools pulled into `sys.modules` by hand. The residual surface is
**4 modules**: `experiments/exp2m/__init__.py`, `run/__init__.py`,
`run/preflight_2m.py`, `verify_referents_2m.py` — exactly what the
brief predicted, and exactly 2l's shape one experiment over.

**DISCLOSURE (checklist 27):** the scan runs `analyze_2m.run()` on the
REAL pre-campaign tree. It printed **INSUFFICIENT_DATA and no T** (11
referent/loader failures: the missing prereg tag plus the absent
endpoint/rung-set/power/sweep records), after executing every
predictor-side loader (2k's tier at both sizes through its own gate-1
re-derivation, 2i's sealed OLMo-2 1B counts, both predictor-seal
reads). Nothing written. The scan was run TWICE — before and after this
task's edits to `verify_referents_2m.py` — and the pinned literal is
the second reading. Recorded in `experiment-2m-design.md` §2.

`test_analyze_2m.py` after pinning: 51 passed, 158 s.

### The stand-ins, all removed

| site | what went |
| --- | --- |
| `tests/full_shape.py::run_world` | `frozen_check=(None if …)` / `imports_pinned=(True if …)`; only `referents_sha=False` stays (a synthetic root is not the real tree) |
| `tests/test_full_shape_2m.py` (two direct `an.run` calls) | both expressions and their stand-in comments |
| `tests/test_totality_2m.py::_run` | the two `kw.setdefault(...)` bypasses |
| `tests/test_stages_2m.py`, `tests/test_power_2m.py` | the `FROZEN_SHA256_2M` monkeypatches (Step 1) |

The world module re-run ONCE under the real pins (both pins live):
`test_full_shape_2m.py + test_totality_2m.py -m "not slow"` — **42
passed in 1036 s**. `test_every_terminal_reached` passed, so every
world reached its declared terminal and all five `WORLDS_2M` terminals
were covered; no world landed on "unpinned module", so the pin covers
every module the suite imports.

### Step 3 — the pre-campaign referent manifest (3,369 files)

`python -m experiments.exp2m.make_referents_2m` → **3,369 files**, sha
`b237454c88f4de511faa3bf12f348089ff34fafe9e2e2eeaf32878ebfecfc9e1`.
`N_FILES_2M = 3369` set, re-run: same count, same sha —
**byte-idempotent**. `REFERENTS_2M_SHA256` pinned to it.

Composition: 2l's 2,695 pre-campaign list + 2l's OWN campaign
artifacts (68 endpoint records — 2l has two whichs × 34 rungs, where 2m
has three — `rung_set_2l.json`, `power_2l.json`,
`gate1.json`, `verdict.json`, the 595-path sweep tree — S8 reads the
13B outcome through 2l's frozen loaders) + 2l's four instrument blobs +
2m's `checkpoints_2m.json`, `hub_inventory_smollm3.json` and
`power_2m.py`.

**The manifest decision, ledgered:** `REFERENTS_2M_SHA256` pins the
PRE-CAMPAIGN manifest only. 2m's own campaign artifacts (102 endpoint
records + the rung set + the power record) are bound by
`exp2m-endpoint-sealed`, and every sweep record additionally carries
the composite `endpoint_sha256` the analyzer re-derives — so the
preregistration tag is never re-cut after the campaign.

Cold battery: **13/13** (items 3 and 12 live). Item 10 printed
"endpoint/rung set: absent — pre-campaign", "power: absent —
pre-campaign", "sweep: absent — pre-campaign". Item 13's four sources:
pythia_2.8b 7 rungs / n_pos 1769, pythia_6.9b 8 / 2088, olmo2_7b 34 /
8793, olmo2_13b 34 / 8737. Commit `befb6f8b`.

### Task-4 review carry-overs (same commit)

| # | what | where |
| --- | --- | --- |
| 4 | world spec **W23** (`olmo_only` + `power_status_a="DECLARED UNDERPOWERED IN ADVANCE"` → OLMO-ONLY) and `test_w23_underpowered_a_disclosure_rides_on_the_licence` | `tests/full_shape.py`, `tests/test_full_shape_2m.py` |
| 5 | the REAL power record from `pm.main(...)` re-derived through `an.check_power_claims_2m(rec, x256, x_b, strata, RUNGS_PRIMARY, stage1) == []` | `tests/test_power_2m.py` |
| 2 | the unused `from experiments.exp2l import analyze_2l as an2l` dropped (item 7 keeps its raw read) | `verify_referents_2m.py` |
| 3 | 2l's M-4 (item 9, two independently-constructed record dicts) and M-3 (item 10, each artifact tested independently) rationale comments restored with 2l→2m names | `verify_referents_2m.py` |
| 7 | `'{"R_13B": ['` → `'{"R_3B": ['`; "synthetic 13B tree" → "synthetic SmolLM3 tree" (×2) | `tests/test_totality_2m.py` |
| — | Task 3's deferred minor: `"n_boot_requested": n_boot` added beside `"n_boot": len(diffs)` (additive; the existing key is unchanged and `s3["n_boot"] == 40` still holds) | `analyze_2m.py::s3_paired_difference_2m` |

`test_every_terminal_reached` does not hard-code the world count, so
W23 needed no counter change.

### Step 4 — the mutation harness: 140 mutants, **140 killed, 0 survivors, 0 SKIP**

`tests/mutation_check.py` = 2l's harness (the `_totality_mutants`
import from 2i, `_refuse_if_any_backup_exists`, `_acquire_backup`,
`run_suite`, `_parse_only`, `main`, the FAST/TOTALITY/FULLSHAPE
switches) with 2m's paths and `M` = **99 hand-written mutants** (35
`battery_2m`, 6 `run/endpoint_2m`, 10 `run/sweep_2m`, 48 `analyze_2m`)
**+ 41 AST-generated `collect_total` totality mutants** = **140**. Every
`old` occurs exactly once in the pristine source (checked before the
run and confirmed by the harness: 0 SKIP in every pass). No stray
`.mutation_backup` before any launch; 0 after every run; `git status`
after each run showed no production file modified.

| pass | command | result |
| --- | --- | --- |
| 1 | `nohup … mutation_check.py` (fast) | **113/140 killed**, 27 survivors, 0 SKIP (baseline 143 s) |
| 2 | `… --only 35,47,51` (fast, after three new fast tests) | 3/3 killed |
| 3 | `… --totality --only 98,105,109,110,111,112,113,122,124,126,128,129,130,131,132,133,134,135,138,139,140` | 15/21 killed, 6 survivors |
| 4 | `… --totality --only 110,111,112,113,124,126` (after six new totality tests) | 6/6 killed |
| 5 | `… --fullshape --only 88,89,99` | 1/3 killed (89), 88 and 99 survived |
| 6 | `… --fullshape --only 88,99` (after two new world assertions) | 2/2 killed |

Logs, all COMMITTED under `experiments/exp2m/` (fix round 1 removed the
`.gitignore` line that had been ignoring `experiments/exp2m/
mutation_*.log` — a plan defect: 2l's ten mutation logs are tracked, and
`.gitignore`'s own comment says the committed mutation logs ARE the
battery's record): `mutation_build.log` (pass 1),
`mutation_fast_survivors.log` (pass 2), `mutation_totality.log` (3),
`mutation_totality_rerun.log` (4), `mutation_fullshape.log` (5),
`mutation_fullshape_rerun.log` (6), `mutation_fast_88.log` (fix round
1's fast re-confirmation of #88).

**Every gap closed, with the closure:**

| # | mutant | closed by |
| --- | --- | --- |
| 35 | `load_tokenizer_3b`: `padding_side "left"` → `"right"` | NEW fast test `test_battery_2m.py::test_load_tokenizer_3b_sets_left_padding_and_the_pad_token` — a `_LoadTok` stub in SmolLM3's real shape (right padding, no pad token declared) behind a stub `transformers` module in `sys.modules`; no network, nothing downloaded. The loader's two assignments and its `check_tokenizer_2m` call were previously untested (only `check_tokenizer_2m` itself was) |
| 47 | `run_twin`: the checkpoint record written BEFORE the rung loop | NEW fast test `test_stages_2m.py::test_run_twin_reads_the_config_commit_and_records_itself_only_after_every_rung` — `sw.evaluate_items` raises on the 3rd rung; the twin's checkpoint record must be absent and `records_complete_3b(root, TWIN)` False (2i's R-3 resume rule: that record is what marks the step done) |
| 51 | `run_twin`: the tokenizer commit → `bm.REV_BASE_2M` | the same test: `state["tok"] == [(REPO_CKPT, entry_twin["config_commit"])]`. The pre-existing world test only asserted `(REPO_CKPT, e["commit"]) in state["tok"]`, which gate 1's own tokenizer call already satisfied — a membership check where an identity check was needed |
| 88 | `run()/_core`: Test B on 2l's composite strata | **Killed by the FAST pass and by `--fullshape`** (fix round 1). Fast: NEW `test_analyze_2m.py::test_core_reads_both_tests_on_the_bare_base_strata_ast` — dial b as a property of the SOURCE (both `_run_test` calls inside `run()`'s `_core` pass `strata`, an `ast.Name`, as their fourth positional argument, never an `ast.Call`; labels `"1b:k256"` and `bi.SIZE_PRED`), 0.5 s, no predictor load. Worlds: `test_w1_pythia_only_shape` rules the composite OUT (`B["stratified"]["T"] != sec["S3 B beyond A"]["stratified"]["T"]` — W1 .0095 vs −.1811, W2 .6527 vs .6851) AND rules the base form IN by exact equality (`an2i._run_test(fs.x_b_real(), bi.SIZE_PRED, out, fs.strata(), fs.RUNGS_PRIMARY, n_perm=200, n_boot=20)["stratified"]["T"] == v["tests"]["B"]["stratified"]["T"]`, re-derived from the world's own tree; the `worlds` fixture now carries the root for it). Confirmed: `mutation_check.py --only 88` (fast) → `1/1 killed` |
| 99 | sensitivities' `log_head_subset` built from `GRID_3B` | NEW assertions in the same test: `sens["log_head_subset"]["A"/"B"]["stratified"]["T"] != A/B["stratified"]["T"]` — the 21-point subset is a different outcome from the 26-point grid (W1: .7165 vs .7124). Killed under `--fullshape` |
| 110, 111, 112, 113, 124, 126 | `collect_total` stripped from `bg.load_battery`, `bg.load_floors`, `a2d.load_verify`, `pr.load_predictor` (the strata source), the upstream frozen-pin `thunk` loop, and the three-which `entry_which_3b` map | SIX NEW totality tests in `test_totality_2m.py` (`test_load_battery_forced_exception`, `…_load_floors_…`, `…_load_verify_…`, `…_load_predictor_2g_…`, `test_upstream_frozen_import_thunk_forced_exception`, `test_entry_which_3b_forced_exception`), each monkeypatching the callee to raise and asserting INSUFFICIENT_DATA with its own label. These six `collect_total` sites had no forcing case at all — a real totality gap, not a harness artefact |
| 89, 98, 105, 109, 122, 128–135, 138, 139, 140 | the rest of the first pass's survivors | already covered: killed by `--totality` (the collect_total sites with an existing forcing case, plus F-1's post-secondaries re-check) or by `--fullshape` (89: `S1 ladder 1b[256]["T"] == A["T"]`), confirmed by the targeted runs above. Recorded as "killed by worlds/totality only" per the harness's own rule |

**No documented-equivalent mutant.** The one candidate the brief named
— `sweep_2m.run`: `endpoint_sha` computed BEFORE the endpoint seal
binds (#49) — was **killed by the fast suite in pass 1**, so no
equivalence proof was needed.

### Step 5 — the read sweep: (e) unpinned = 0

`tests/read_sweep_2m.py` = 2l's tool with 2m's roots, `an2l`/`bl`
pre-imported, 2l's residual pin folded into `frozen`, the sweep tree
over `GRID_3B + (TWIN,)`, and `SHA_PIN_AT_LOAD` extended with
`bm.CHECKPOINTS_PATH`. `blobs_bound` left at its default (real git:
2k's and 2i's predictor seals bind for real); `tag_exists`/`blob_sha`
are the documented sweep-only stand-ins for the not-yet-cut prereg tag;
`referents_sha`, `imports_pinned` and `frozen_check` all left at their
real pinned defaults and all passed.

**DISCLOSURE (checklist 27):** the sweep runs `analyze_2m.run(n_perm=30,
n_boot=10, write=False)` on the REAL pre-campaign tree. It printed
**INSUFFICIENT_DATA and no T** — 10 referent/loader failures, all of
them the absent campaign artifacts (rung set, power record, the
endpoint seal's 104 blobs, the three endpoint whichs, the composite
sha, gate 1, the sweep, the gate-1 re-derivation). Recorded in
`experiment-2m-design.md` §2.

```
5116 distinct paths opened for reading (7483 total open/read calls)
  writes observed (should be 0, write=False): 0

category                       count
referents_2m.json               3370
frozen_module                     59
instrument_blob                    4
sha_pin_at_load                    0
seal_bound_campaign_absent         0
python_stdlib_venv              1683
UNPINNED                           0

(e) unpinned verdict input: 0 — clean
```

Two bucket readings worth stating rather than passing over:

- `referents_2m.json` 3,370 = the manifest's 3,369 files + the manifest
  file itself (which pins its own sha). 2l's committed campaign
  artifacts, which S8 reads once 2m's campaign exists, are inside that
  count — bucket (a), as intended.
- `sha_pin_at_load` 0. `SHA_PIN_AT_LOAD` names five checkpoint
  manifests, and they divide into two cases. `checkpoints_2i.json`,
  `checkpoints_2l.json` and `checkpoints_2m.json` ARE read on this
  path, but each is also a `referents_2m.json` entry, and `_classify`
  tests the manifest bucket first, so the stronger pin claims them —
  they land in (a). `checkpoints_2g.json` and `checkpoints_2h.json` are
  NOT `referents_2m.json` entries; the bucket is empty of them because
  they are never OPENED pre-campaign. Their only reader is S8's Pythia
  path (`an2j.load_pythia_outcomes` → `ck2g.load_manifest` /
  `an2h.load_manifest_69`), which lives inside the secondaries, and the
  pre-campaign run refuses long before the secondaries are reached.
  Both files stay in `SHA_PIN_AT_LOAD` (no code change): the bucket
  exists so that when they ARE read they are classified correctly.
- `seal_bound_campaign_absent` 0 is structural: pre-campaign the
  analyzer refuses on `is_file()` guards and never attempts an `open()`
  of a seal-bound artifact, so the wrapper records nothing to classify.
  This bucket becomes non-empty at the process-tail re-run after
  `exp2m-endpoint-sealed` exists. `sha_pin_at_load` does NOT: the
  endpoint seal adds no sweep, so the analyzer still refuses before S8
  and the two Pythia manifests still go unread — that bucket first
  fills at the post-campaign analyzer run, when the secondaries
  actually execute.

**Process tail:** re-run `tests/read_sweep_2m.py` once AFTER the
endpoint seal tag is cut — (e) must still be 0, and the campaign-side
paths must then resolve for real.

### Step 6 — ledger, design §2 disclosure

`experiment-2m-design.md` §2's pre-tag disclosure paragraph gains the
record of every pre-tag execution of `analyze_2m.run()` on the real
tree (the import scan ×2, the read sweep, Task 3's real-tree tests and
the world/totality modules on synthetic roots), each INSUFFICIENT_DATA
with no T; the paragraph's original "the analyzer does not exist"
sentence is kept, the log appended after it. The cold battery's item 10
is noted as inspecting the tree WITHOUT calling `run()`.

### Files changed by Task 5

Production (only at the named literals, plus the one additive record
field and the two `verify_referents_2m.py` items the Task-4 review
asked for): `experiments/exp2m/battery_2m.py` (`FROZEN_SHA256_2M`
literal + the one re-pin), `experiments/exp2m/analyze_2m.py`
(`IMPORTED_SHA256_2M`, `REFERENTS_2M_SHA256`, `n_boot_requested`),
`experiments/exp2m/make_referents_2m.py` (`N_FILES_2M`),
`experiments/exp2m/verify_referents_2m.py` (unused import dropped, two
rationale comments restored). New: `experiments/exp2m/referents_2m.json`,
`experiments/exp2m/tests/import_scan_2m.py`,
`experiments/exp2m/tests/mutation_check.py`,
`experiments/exp2m/tests/read_sweep_2m.py`. Tests:
`tests/full_shape.py`, `tests/test_full_shape_2m.py`,
`tests/test_totality_2m.py`, `tests/test_stages_2m.py`,
`tests/test_power_2m.py`, `tests/test_battery_2m.py`,
`tests/test_analyze_2m.py`. Doc: `experiment-2m-design.md` §2. Nothing
else in the repo touched; no frozen upstream module edited.
