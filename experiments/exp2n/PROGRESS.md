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

## Task 2 (2026-09-06): the stage runners

Built: `run/endpoint_2n.py` (three thin loads — `stage1_final`,
`stage2_final`, `main` — over all 34 rungs, all from the ONE Comma
repo; `require_predictor_seals_2n` re-derives `PREDICTOR_SHA_2N` from
2k's and 2i's sealed artifacts rather than trusting the literal; the
rung set is fixed from `stage1_final` counts alone (`R_COMMA`), the
other two whichs are descriptive; skip-if-exists + dry-run; an
exception mid-which leaves no rung set); `run/sweep_2n.py` (gate 1 —
the endpoint re-derived through the candidate-file loader and diffed
against the committed `stage1_final` records — then the seeded
`from_config` twin, then the 23 remaining grid steps ascending; the
endpoint seal gate binds 102 endpoint records + the rung set + the
power record; halt-and-refuse-resume on a gate-1 mismatch; resume
skips complete steps and re-enters incomplete ones, including the
twin); `run/preflight_2n.py` (main through the thin loader and one
grid checkpoint through the candidate-file loader, each under BOTH a
pinned `BosRunner`-wrapped pass and a plain unwrapped pass, printing
the eos facts and peak MPS memory after every load, with a per-load
fp16 finiteness probe that refuses on any non-finite logit; asserts
nothing was written under `results/`); `run/commit_watcher_2n.sh` (2m's
script, `2m`→`2n` throughout, `chmod +x`); the stub `analyze_2n.py`
(only `_endpoint_seal_paths_2n`, Task 3 will replace the file keeping
that function byte-identical); `tests/test_stages_2n.py` (fake
loaders, no torch, no network, no frozen tree touched).

Every runner factory returns `bn.BosRunner(HFRunner(...))` for its
production `"runner"`; the preflight additionally exposes a bare
`"plain_runner"`, `"eos_facts"` (`bn.eos_facts_2n`) and a `"memory"`
returning `{"current", "peak"}`. Neither stage runner (`endpoint_2n.py`,
`sweep_2n.py`) mentions `RENDER_2N`/`EOS_STOP_ID_2N` — grepped clean;
the render lives in the factory and the stop-id/render stamps live in
`battery_2n`'s record functions.

Two corrections to the brief's literal transcription, both forced by
`battery_2n.py`'s (Task 1's, frozen) actual interface rather than
found by running tests — the mechanical `2m`→`2n` substitution alone
does not touch upper-case `_3B`-style tokens, but the real function
`rung_set_from_counts_2n` (already on disk) returns the key `R_COMMA`,
not `R_3B`:

1. `endpoint_2n.run`'s closing print and every `rs["R_3B"]` reference
   in `test_endpoint_writes_three_whichs_and_the_rung_set_from_
   stage1_final` use `R_COMMA` (`rung_set['R_COMMA']`, `rs["R_COMMA"]`,
   `bn.rung_set_from_counts_2n(...)["R_COMMA"]`) — matching Task 1's
   committed return key exactly (mirrors `GRID_3B`→`GRID_COMMA`, which
   the brief already spelled out explicitly for the same reason).
2. The autouse `_blobs_that_exist` fixture also carries the
   Task-2-era `FROZEN_SHA256_2N` stand-in 2m's own history shows and
   later dropped at its Task 5 (`if not bn.FROZEN_SHA256_2N:
   monkeypatch.setattr(bn, "FROZEN_SHA256_2N", bn.frozen_from_disk
   (strict=False))`) — the CURRENT `test_stages_2m.py` no longer
   carries it (2m already reached Task 5), but `battery_2n.py`'s
   `FROZEN_SHA256_2N` is still the empty literal Task 1 left it
   (`{}`, "pinned as a literal from `frozen_from_disk()` at Task 5"),
   so every call to `check_frozen_2n()` inside `ep.run`/`sw.run`/
   `pf.run` would otherwise raise "not pinned" unconditionally.
   Confirmed against 2m's build history (`git show a57595c6:experiments/
   exp2m/tests/test_stages_2m.py`, its own Task-2 commit) before
   adding it back, rather than guessed.

Everything else — every identifier, docstring, print label, and the
new-test bodies — is 2m's file verbatim under: `2m`→`2n` throughout;
`bm.`→`bn.` with the five import lines rewritten to `battery_2n`/
`endpoint_2n`/`preflight_2n`/`sweep_2n`/`analyze_2n`; `_2M`→`_2N`;
`_3b`→`_comma`; `smollm3_3b`→`comma_7b`; `stage3_final`→`stage2_final`;
`base`→`main` (as a which); `REPO_CKPT`/`REPO_BASE`→`REPO_COMMA`
(collapsing the two-repo load-state assertion to `assert all(l[0] ==
bn.REPO_COMMA for l in state["loads"])`); `REV_BASE_2M`→`REV_MAIN_2N`;
`entry_base_3b`→`entry_main_comma`; `bm.BOS_TOKEN_2M`→`bn.BOS_TOKEN_2N`;
the stale-tag literal `"exp2l-preregistered"`→`"exp2m-preregistered"`;
`SHORT_GRID = (10000, 20000, bn.ENDPOINT_STEP_2N)` and every grid-step
literal in the test bodies (40000→10000, 80000→20000) with it;
`SHORT_SUBSET = (20000, bn.ENDPOINT_STEP_2N)`; `_shrink_grid` setting
`GRID_COMMA`/`EVERY40K_SUBSET_2N`/`load_manifest_comma`; the preflight
default `checkpoint_step=10000`; `"plain render ids [48, 25]"`→
`"plain render ids [52, 29]"`; `"[2m preflight]"`/`"[2m sweep]"`/
`"[2m endpoint]"`→their `2n` forms; the preflight printout's two label
families (pinned unlabelled vs `plain `-labelled, `ckpt ` vs
`ckpt plain `); the extended `amap` (BOS-prefixed copy of every key)
and `eos_facts`/`render_ids` fakes in `_preflight_loaders`; the three
new eos fields on every fake `info` dict in `_endpoint_loaders`/
`_sweep_loaders`; and the three new tests from the brief verbatim.

### Tests

Step 2 (before the runners existed):
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2n/tests/test_stages_2n.py -q -x`
— collection ImportError on `experiments.exp2n.run.endpoint_2n`, as
expected (confirmed by running the file-writing and test-writing in a
single pass, then re-verifying the RED state is what step 2
describes before proceeding — not separately re-triggered, since the
runners were already on disk by the time the suite next ran).

Step 4 (fast suite):
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2n/tests/test_stages_2n.py -q -m "not slow"`
— 25 passed, 1 deselected.

Step 4 (slow, real git against the committed 2k/2i seal tags):
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2n/tests/test_stages_2n.py -q -m slow`
— 1 passed, 25 deselected.

Full `experiments/exp2n/tests/` (fast): 55 passed, 1 deselected.
Full `experiments/exp2n/tests/` (slow): 1 passed, 55 deselected.

### Self-review

Diffed each runner against 2m's original run through a substitution
script (`2m`→`2n`, `_3b`→`_comma`, `smollm3_3b`→`comma_7b`,
`stage3_final`→`stage2_final`); every remaining line traces to a
brief-named delta (BosRunner wrapping, the `base`→`main`/`REPO_COMMA`
rename, `GRID_COMMA`/`R_COMMA`, the preflight's eos-facts/memory-dict/
plain-runner additions, checkpoint-step default, docstring prose).
`commit_watcher_2n.sh` reproduces `2m`→`2n`-substituted
`commit_watcher_2m.sh` byte-for-byte (confirmed with `diff`), including
its "Mirrors experiments/exp2i/run/commit_watcher_2i.sh" comment line
left unchanged (a first pass had rewritten it to reference exp2m,
which the literal substitution rule does not call for — reverted).
`grep -n "RENDER_2N\|EOS_STOP_ID_2N" experiments/exp2n/run/{endpoint,sweep}_2n.py`
returns nothing. `git status` shows nothing under `experiments/exp2m`
and `experiments/exp2n/battery_2n.py` untouched.

## Task 3 (2026-09-06): `analyze_2n.py` + `make_referents_2n.py`

Built (replacing Task 2's stub, `_endpoint_seal_paths_2n` kept
byte-identical — confirmed by extracting both function bodies and
comparing them programmatically): `analyze_2n.py` — the pins
(`check_imports_2n`, folding `an2j`'s/`an2k`'s/`an2l`'s/`an2m`'s own
residual import pins into `upstream` beside `IMPORTED_SHA256_2N`); the
record-failure functions (`_record_common_failures_2n` — gains
`render`/`eos_stop_id` to the pinned tuple, `endpoint_record_failures_2n`,
`step_record_failures_2n`, `checkpoint_record_failures_2n`,
`twin_checkpoint_record_failures_2n` — both gain the
`generation_eos_token_id` pin against `EOS_STOP_ID_2N`) with the
`dtype` pin and the twin's bespoke shape; the Comma loaders
(`load_endpoint_which_2n`, `load_sweep_comma` over the 24-point grid +
twin); the outcomes (`outcomes_comma` over the grid or the every-40k
subset, `rung_level_comma`, `_first_correct_outcome_comma`,
`collapses_comma`, `non_monotone_comma`, `ceiling_fraction_comma`); the
rung set (`_load_rung_set_2n` + `_check_rung_set_vs_endpoint_2n` /
`_check_rung_set_derivation_2n` / `_check_rung_set_endpoint_shas_2n`,
all on the `R_COMMA` key); the power record (`load_power_2n`,
`check_power_claims_2n` — B on 2g's BASE strata per dial b, not a
composite); the predictors through their own seals (`load_predictors_2n`
— x_A^(256) via 2k's `load_tier_2k` + `seal_failures_2k`, x_B via 2i's
`sampler_counts_olmo` after `load_predictor_records_2i` +
`_check_predictor_seal_sampling`, cross-checked by
`_check_predictor_counts_2i`); the secondaries (`s3_paired_difference_2n`
— 2m's paired item bootstrap of T_B − T_A unchanged, `s4_matched_2n`,
`s5_answer_prior_2n`, `load_committed_outcomes_2n` — 2m's four sources
plus a fifth (SmolLM3-3B via `analyze_2m.load_sweep_3b` +
`outcomes_3b`) — + `s8_outcome_order_2n`, `_extra_rungs_2n`); the NEW
generalised paired bootstrap `paired_contrast_2n` (every predictor in
both groups read on the SAME within-rung resample; 2n's
`s3_paired_difference_2n` is the case group_a={B}, group_b={A}); the
NEW thinned predictor `thinned_x_b_2n` (2k's block rule, first k_g
draws, no seed) and the NEW annotation `annotation_c_2n` (Δ = thinned-B
T − A256 T, the CI rule B-LEADS/A-LEADS/NO-LEAD/UNDEFINED,
`covers_3b_increment` against `read_increment_3b_2n`'s read of 2m's
own committed `results/verdict.json`); the NEW `s8c_corpus_contrast_2n`
(Pile rows Pythia-2.8b/6.9b vs DCLM-class rows OLMo-2 7B/13B/SmolLM3-3B,
same paired bootstrap) and the NEW `s9_sign_ledger_2n` (per-rung D on
the three option rungs for this run beside 2l's and 2m's committed
per-rung D read from their `verdict.json` files, plus 2k's/2i's 7B
readings as literals); the tree (`verdict_tree_2n` → SHARED /
PYTHIA-ONLY / OLMO-ONLY / NEITHER, `verdict_2n` — gains `annotation`
and carries `"C: <reading> (delta …, ci95 […])"` in the reason,
`_licensed_2n` — gains the `C_MODIFIERS_2N` clause keyed by
`_c_modifier_key_2n`) with 2n's disclosures; `run()` (halt scan first,
pins/prereg/manifest/referents, upstream pins, battery/floors/verify/
strata, the NEW increment-3b read + literal check right after strata,
the predictors, the Comma endpoint stage + rung set + power record +
seal, gate 1 attested then re-derived, the gating core with both tests
UNCONDITIONED on the base strata, the NEW annotation C computed and
gated as a REFERENT failure before the tree, S1–S9 + C + the paired
difference + extra rungs + sensitivities with the every-40k control,
the import-surface re-check after the secondaries). Also built
`make_referents_2n.py` (`referent_files` = 2m's whole pre-campaign list
+ 2m's OWN campaign artifacts — endpoint records, rung set, power
record, sweep tree, gate1.json, verdict.json, since S8 reads the
SmolLM3-3B outcome through 2m's frozen loaders — + 2m's four
instrument blobs + 2n's own `checkpoints_2n.json`,
`hub_inventory_comma.json`, `power_2n.py`; `build`, `check_referents`);
`tests/test_analyze_2n.py`; `power_2n.py` as a docstring-only STUB
(Task 4 owns its content — the same role `power_2m.py` played for
`make_referents_2m` before its own Task 4).

### The per-rung D key finding

The brief asked for one entry of 2m's committed `results/verdict.json`
(`tests.A.per_rung.antonym`) to be read before writing `_per_rung_d`,
to confirm the key name `_run_test` emits. Read directly: the key is
`"d"` (alongside `n_pairs`, `n_pos`, `ci`, `raw_d`) — `2m`'s
`tests.A.per_rung.antonym.d` is `-0.040536876355748375` (rounds to
`-0.041`) and `tests.B.per_rung.antonym.d` is `0.16790943600867678`
(rounds to `0.168`), matching the brief's literals exactly. Cross-
checked against 2l's committed `results/verdict.json` the same way:
`tests.A.per_rung.antonym.d` = `-0.06577875529488433` (rounds to
`-0.066`), `tests.B.per_rung.antonym.d` = `0.25597990523491465`
(rounds to `0.256`) — both match the brief's literals too. No
deviation from the brief needed; `_per_rung_d` reads `v.get("d")`.

### `power_2n.py` and `DELTA_SD_FIELDS_2N`/`check_power_claims_2n`

Per the task's own resolution #2, `check_power_claims_2n` keeps 2m's
exact signature (`power, x_a256, x_b, strata, r_primary, stage1_final`)
in this task; `load_power_2n` does NOT require a `delta_sd` block yet.
Correspondingly `DELTA_SD_FIELDS_2N` and `DELTA_FORMULA_LITERAL_2N`
(named in the brief's "Produces" list, but explicitly deferred by
resolution #2) are NOT defined in this task's `analyze_2n.py` — Task 4
adds both alongside the power record's real content. `POWER_CLAIM_
FIELDS_2N` and `BLOCK_SD_FIELDS_2N` are defined (unchanged from 2m's
values).

### A documentation-only note on `bm.`'s survival in `check_imports_2n`

The self-review checklist names `check_imports_2n` among the functions
where `bm.` should survive. In the actual file `bm.` appears only
inside `load_committed_outcomes_2n` and the default `root_2m=bm.EXP2M`
— `check_imports_2n`, `read_increment_3b_2n` and `s9_sign_ledger_2n`
take `root_2m` (or reach 2m only via `an2m.IMPORTED_SHA256_2M`) as
explicit parameters/attributes rather than reaching for `bm.` directly,
exactly as the brief's own verbatim NEW-code bodies for the latter two
do (neither snippet given in the brief references `bm.` at all).
`bn.FROZEN_FILES_2N` (built in `battery_2n.py`, already committed)
transitively carries 2m's `FROZEN_SHA256_2M` bytes and
`INSTRUMENT_BLOBS_2M` paths, so `check_imports_2n`'s `covered` set
already covers everything 2m contributes without a second, redundant
`bm.` reference at the analyzer level. Flagged for the reviewer as a
defensible reading rather than silently asserted.

### Pre-tag disclosure (design §2 / checklist 27)

`an.run()` executed on the real committed tree many times during this
task's test runs (no `results/` directory exists yet, no Comma record
of any kind, no prereg tag cut). A representative bare
`an.run(n_perm=20, n_boot=5)` call prints:

```
verdict: INSUFFICIENT_DATA
n_failures: 14
 - 2n frozen modules: RuntimeError: FROZEN_SHA256_2N is empty — not pinned (build incomplete)
 - 2n import surface: not pinned (build incomplete)
 - 2n prereg tag: RuntimeError: preregistration tag exp2n-preregistered does not exist
 - 2n referent manifest: not pinned (build incomplete)
 - 2n rung set file: FileNotFoundError: .../experiments/exp2n/results/endpoint/rung_set_2n.json
 - 2n power record: ValueError: rung set missing
 - 2n endpoint seal binding: the tag 'exp2n-endpoint-sealed' does not exist
 - 2n endpoint stage1_final/stage2_final/main: FileNotFoundError (endpoint records missing)
 - 2n endpoint composite sha: FileNotFoundError
 - 2n gate 1 comma_7b: record missing
 - 2n sweep comma_7b: ValueError: manifest/battery/verify/endpoint sha missing
 - 2n gate 1 comma_7b re-derivation (byte identity): ValueError: sweep, endpoint or gate 1 record missing
```

The increment-3b read against 2m's committed `verdict.json` SUCCEEDS
even on this empty tree (it depends only on `root_2m`, which defaults
to the real, closed `experiments/exp2m`) — it never appears among the
failures above. Every `an.run()` call the test suite makes (the six
`test_run_forced_exceptions_on_the_real_tree_are_graceful` cases,
`test_run_strata_pins_forced_exception`, `test_run_frozen_check_
forced_exception`, `test_run_import_surface_entry_forced_exception`,
`test_run_referent_manifest_check_forced_exception`, plus
`test_run_on_empty_tree_is_insufficient_never_raises` on a `tmp_path`
root) lands the same way: `verdict == "INSUFFICIENT_DATA"`, with the
injected label present among `referents["failures"]`. No statistic of
any kind is computed or printed — the gating core (`_core`) is never
reached because `failures` is non-empty by the time it would run.
Nothing here is a projection or a result; it is the expected shape of
every pre-tag execution while Tasks 4–5 (power record,
`FROZEN_SHA256_2N`, `IMPORTED_SHA256_2N`, `REFERENTS_2N_SHA256`, the
prereg tag) remain unbuilt.

### Tests

Step 2 (RED, before `analyze_2n.py` existed): collection failed with
`AttributeError`s on `an.WORLDS_2N` etc. against the Task-2 stub, as
expected.

Step 4 (fast suite, single module):
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2n/tests/test_analyze_2n.py -q -m "not slow"`
— 67 passed (≈ 179 s; the real-tree predictor/run cases dominate the
wall time, as in 2m's own Task 3).

Step 4 (full `experiments/exp2n/tests/` directory, fast):
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2n/tests/test_analyze_2n.py experiments/exp2n/tests/test_stages_2n.py experiments/exp2n/tests/test_battery_2n.py -q -m "not slow"`
— 122 passed, 1 deselected (the slow real-git seal-binding test in
`test_stages_2n.py`; ≈ 189 s).

### Self-review

`_endpoint_seal_paths_2n` confirmed byte-identical to the Task-2 stub
(extracted and compared both function bodies programmatically, not by
eye). `bm.` in `analyze_2n.py` appears only inside
`load_committed_outcomes_2n` (the fifth S8 source, SmolLM3-3B) and the
`run()` default `root_2m=bm.EXP2M` (see the note above on
`check_imports_2n`). A programmatic scan confirmed every name in the
brief's "Produces" list for `analyze_2n.py` (minus the deferred
`DELTA_SD_FIELDS_2N`/`DELTA_FORMULA_LITERAL_2N`) and for
`make_referents_2n.py` is actually defined; `referent_files()` returns
4,427 files, all unique (no duplicates from the merge of 2m's list,
2m's campaign files, 2m's instrument blobs and 2n's own three paths).
`git status` shows nothing under `experiments/exp2m` and nothing
changed in Tasks 1–2's files (`battery_2n.py`, `run/*`,
`test_battery_2n.py`, `test_stages_2n.py`, `conftest.py`) — only
`analyze_2n.py` (modified from the stub), `make_referents_2n.py`,
`power_2n.py` and `tests/test_analyze_2n.py` are new/changed.

## Task 4 (2026-09-06): power_2n.py, the worlds, totality, power tests, cold battery

### What was built

`power_2n.py` (replacing Task 3's stub): 2m's `power_2m.py` verbatim
with the substitutions (`3b`→`comma`, `SmolLM3-3B`→`Comma v0.1-1T`,
`n_trained_steps = 24`) plus the new `delta_sd_2n(strata, bits_b,
x_a64, x_a256, x_b, n_pos, rungs, *, n_steps, n_sim, n_boot, seed)` —
the SD of Delta = t_only(x_B thinned) − t_only(x_A256) across simulated
outcomes at the null and at each test's own calibrated D=.15 latent,
plus the paired-bootstrap SD of Delta on the first null draw, from
which `min_detectable_delta = 2.63 * delta_boot_sd_null` follows.
`main()` now also computes `bits_b`/`x_a64` from the predictor context
and writes `rec["delta_sd"]`.

`analyze_2n.py` extended (only as the brief/rulings allow):
`DELTA_SD_FIELDS_2N` and `DELTA_FORMULA_LITERAL_2N` added beside
`BLOCK_SD_FIELDS_2N`; `load_power_2n` now requires the `delta_sd` block
with every field and the pinned formula literal; `check_power_claims_2n`
gained required keyword-only `bits_b`/`x_a64` and now also re-derives
`delta_sd.k_by_rung` (via `thinned_x_b_2n`) and `delta_sd.rungs`
(R_PRIMARY minus the union of both predictors' degenerate rungs, computed
per-test inside the same loop that already computed each test's own
degeneracy set); `run()`'s call site wraps the extra `x64` computation
inside the same `collect_total`-wrapped closure as the claims check
itself, so a malformed `cells_2k` there still reaches INSUFFICIENT_DATA
rather than raising.

`tests/full_shape.py`: 2m's world builder verbatim with the
substitutions (`3b`→`comma`, `smollm3_3b`→`comma_7b`, `stage3`→`stage2`,
`base`→`main`, `600000`→`200000` as the edited/unlinked mid-grid step,
`26`→`24` trained steps) plus `x_a64_real()`, `bits_b_real()` (both
cached on the real committed 2i/2k data) and `s8_cached()` now loading
the FIVE committed outcomes via `an.load_committed_outcomes_2n(...,
root_2i=bi.EXP2I, root_2l=bl.EXP2L, root_2m=bm.EXP2M)`. Every checkpoint
record (grid steps and the twin) now carries `"config_eos_token_id": 2,
"generation_eos_token_id": 3`. Two new `missing` modes: `"render"`
(rewrites the step-200000/odd6 sweep record's `render` to `"plain"`) and
`"eos_stop"` (rewrites the step-200000 checkpoint record's
`generation_eos_token_id` to `2`). `world_specs()` = 2m's 25 (with the
`base`→`main`/`stage3`→`stage2` renames, including
`"main_record"`/`"stage2_final"` mode names) plus W26 and W27.

`tests/test_full_shape_2n.py`, `tests/test_totality_2n.py`,
`tests/test_power_2n.py`: 2m's three files verbatim with the
substitutions plus the brief's literal new tests
(`test_annotation_c_cells_across_the_worlds`,
`test_s8_five_rows_s8c_and_s9`, `test_w26_w27_render_and_stop_id_
refusals`; `test_increment_3b_read_forced_exception`,
`test_annotation_c_forced_exception`, `test_s8c_forced_exception`,
`test_s9_forced_exception`, `test_stage2_endpoint_record_is_a_list`;
`test_delta_sd_2n_shape_and_formula`, the `test_main_writes_once_with_
both_tests_on_base_strata` extension).

`verify_referents_2n.py`: 2m's 13-item cold battery verbatim with the
substitutions (item 1 gains `bm.check_frozen_2m()` as a real upstream
check since 2m is now frozen; item 2 gains 2m's three tags; item 4's
literals rebuilt from the real `checkpoints_2n.json` — 24 grid entries,
3 shards each, endpoint commit `e295235994f32d763c359d324265a176e591f632`;
item 7 prints 2m's committed endpoint's R_PRIMARY instead of 2l's; item
13 checks the FIVE sources) plus item 14: a pure `_Tok` stand-in
exercising `check_tokenizer_2n`'s accept path and its four refusal
paths (right padding, a foreign pad id, a plain render beginning with a
special id, a BOS render the stub swallows), `set_eos_stop_2n` on a
`_Model`/`_Config`/`_GenConfig` stub, `render_2n`'s prefixing,
`read_increment_3b_2n(bm.EXP2M)` against the literal, and
`s9_sign_ledger_2n` reproducing the four known-answer per-rung D
literals (2l's and 2m's own committed `A`/`B` on `antonym`) read
straight from their committed `verdict.json` files.

### Test commands and results (RED before, GREEN after)

Step 2 (RED): `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest -p no:cacheprovider experiments/exp2n/tests/test_power_2n.py -v`
against the Task-3 stub failed on `pw.delta_sd_2n` missing (`AttributeError`),
and the world module failed collecting/asserting on the W26/W27/C/S8c/S9
keys, as expected — `power_2n.py` didn't yet define `delta_sd_2n` and
`analyze_2n.py` didn't yet carry the annotation-C/S8c/S9 secondaries
(those actually landed in Task 3; the RED here was specifically the new
Task-4 surface: `pw.delta_sd_2n`, the `delta_sd` power-record block, and
W26/W27).

Step 4 (GREEN), run in the sequence below:

```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest -p no:cacheprovider experiments/exp2n/tests/test_power_2n.py -q
```
4 passed in 63.0 s.

```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest -p no:cacheprovider experiments/exp2n/tests/test_analyze_2n.py -m "not slow" -q
```
67 passed in 167.0 s (Ruling R-1's `_power_rec` extension and the two
new refusal cases included).

```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest -p no:cacheprovider experiments/exp2n/tests/test_full_shape_2n.py -v
```
16 passed in 804.5 s (≈ 13.4 min), after two test-side corrections (below).

```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest -p no:cacheprovider experiments/exp2n/tests/test_totality_2n.py -v
```
41 passed in 480.3 s (8.0 min).

```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m experiments.exp2n.verify_referents_2n
```
12/14 (items 3 and 12 skip, pending Task 5's `REFERENTS_2N_SHA256`/
`N_FILES_2N`/`IMPORTED_SHA256_2N`), after one test-side fix (below).

### Test-side corrections (and why)

1. **`power_2n.py`'s own `frozen_check` bypass, four call sites.**
   `power_2n.main()` (like `analyze_2n.run()`) calls `bn.check_frozen_2n`
   unconditionally unless `frozen_check` is passed, and `FROZEN_SHA256_2N`
   is still `{}` pending Task 5. The brief's Ruling 5 named this stand-in
   for `run_world` and the direct `an.run()` calls but not for
   `pm.main()`; by the same logic it needed the identical bypass
   (`frozen_check=(None if bn.FROZEN_SHA256_2N else (lambda: None))`) at
   both `pm.main()` call sites in `test_power_2n.py`'s
   `test_main_writes_once_with_both_tests_on_base_strata` (including the
   "written ONCE" re-call) and in `test_main_refuses_without_rung_set`.
   Root cause diagnosed by reading `power_2n.main()`'s call order (the
   frozen check runs before the `out_path.exists()`/rung-set checks the
   tests are actually exercising). Also caught the same gap in
   `tests/full_shape.py`'s `run_world` and the two direct `an.run()`
   calls in `test_full_shape_2n.py` and `test_totality_2n.py`'s `_run`
   — all four now pass `frozen_check`/`imports_pinned` per Ruling 5's
   stated pattern; Task 5 removes all of these once the real pins exist
   (2m's own history repeats: "the bypasses this defaulted while they
   were empty are gone").
2. **`test_delta_sd_2n_shape_and_formula`'s explicit `_small(monkeypatch)`
   call.** `_small` is already `@pytest.fixture(autouse=True)` on every
   test in the module (as in 2m's file); this pytest version (9.1.1)
   raises "Fixture ... called directly" on a bare call to a fixture
   function. The brief's literal snippet included the call; removed as
   redundant (autouse already applies it) rather than worked around.
3. **`test_w1_pythia_only_shape`'s exact-equality licensed-sentence
   check.** 2m's own test (never carrying an annotation) checked
   `v["licensed_sentence"] == an.LICENSED_2M["PYTHIA-ONLY"]` exactly; 2n's
   `_licensed_2n` ALWAYS appends the `C_MODIFIERS_2N` text after the base
   licence (2n always carries the annotation C), so an exact match can
   never hold here — changed to `.startswith(...)`, the same style
   already used by the referent battery's item-8 "licence prefix" checks.
4. **`test_annotation_c_cells_across_the_worlds`'s unrounded
   `increment_3b` comparison.** The brief's literal snippet compared
   `c["increment_3b"] == an.INCREMENT_3B_2N` directly, but
   `c["increment_3b"]` is the RAW value `read_increment_3b_2n` pulls from
   2m's committed `verdict.json` (0.06585331726660634), while
   `INCREMENT_3B_2N` is the literal rounded to 4 dp (0.0659) — the same
   comparison `run()` itself makes with `round(increment_3b, 4)`, and the
   same rounding the SAME test's next assertion already applies two
   lines down. Fixed to `round(c["increment_3b"], 4) == an.INCREMENT_3B_2N`.
5. **`verify_referents_2n.py` item 14's `_Model` stub.**
   `set_eos_stop_2n` calls `eos_facts_2n`, which reads
   `getattr(model.config, "eos_token_id", None)` — `getattr`'s default
   only covers the attribute lookup, not the `model.config` expression
   itself, so a bare `_Model` with only `generation_config` raised
   `AttributeError: '_Model' object has no attribute 'config'`. Fixed by
   adding a `_Config` stub (`eos_token_id`/`bos_token_id`) as
   `_Model.config`.

### World statistics (W1/W2/W3) and the three C readings

```
W1 PYTHIA-ONLY: A T=0.7127 p=0.004975 fires=True | B T=0.0091 p=0.2289 fires=False
  C: A-LEADS, delta=-0.6985, ci95=[-0.7292, -0.6797], covers_3b_increment=False
W2 OLMO-ONLY:   A T=0.0246 p=0.0199  fires=False | B T=0.6527 p=0.004975 fires=True
  C: B-LEADS, delta=+0.5820, ci95=[0.5536, 0.6150], covers_3b_increment=False
W3 SHARED:      A T=0.5948 p=0.004975 fires=True  | B T=0.5371 p=0.004975 fires=True
  C: A-LEADS, delta=-0.0969, ci95=[-0.1224, -0.0655], covers_3b_increment=False
```

All three synthetic-latent readings land far outside 2m's committed
±0.0659 increment (the latents here are engineered to fire hard, unlike
a real sealed outcome), so `covers_3b_increment` is `False` in every
world — expected and orthogonal to the assertions, which check the
mechanics of the CI rule and the disclosure plumbing, not a real-outcome
prediction.

### Cold battery output (12/14)

```
 [ 1] ok    frozen pins (incl. check_frozen_2m; check_frozen_2n: empty, printed)
 [ 2] ok    2k/2i/2j/2l/2m tags exist; both predictor seals bind; PREDICTOR_SHA_2N re-derives
 [ 3] skip  referents_2n.json (pending Task 5)
 [ 4] ok    manifest: 24 grid + twin + stage2_final + main; 3 shards each; candidate reproduces files
 [ 5] ok    2k tier: zero failures; x_A^(256) == predictor_2k.json; four blocks sum to 256
 [ 6] ok    x_B == 2i's sealed counts; 2i's R_CAP == the nine
 [ 7] ok    rung_set_from_counts_2n hand case + 2m's committed endpoint descriptive
             (R_PRIMARY the nine minus none: full R_CAP_2K)
 [ 8] ok    the tree on literal inputs: every terminal, THIN/UNDERPOWERED, T_BAR/ALPHA
 [ 9] ok    record round trips incl. twin; gate1_failures_comma/gate1_rederive_comma clean
 [10] ok    real EXP2N tree: no halt marker; endpoint/rung-set/power/sweep all absent (pre-campaign)
 [11] ok    s4_matched_2n: k in [1,64], n_blocks == 64 // k
 [12] skip  import surface (pending Task 5)
 [13] ok    S8's five sources load clean (pythia_2.8b 7 rungs/1769 pos, pythia_6.9b 8/2088,
             olmo2_7b 34/8793, olmo2_13b 34/8737, smollm3_3b 34/9076)
 [14] ok    check_tokenizer_2n accept + 4 refusals; set_eos_stop_2n; render_2n; read_increment_3b_2n; s9_sign_ledger_2n
referent battery: 12/14
```

### Self-review

Diffed each file against its 2m original with the brief's substitutions
applied: every remaining difference is one the brief/rulings name (the
new `delta_sd`/C/S8c/S9/W26/W27 surfaces) or a NEW block, no stray
edits. `grep` for `import torch`/`import transformers`/`from torch`/
`from transformers` across every Task-4 file: zero hits. `git status`
shows nothing under `experiments/exp2m` and nothing changed in Tasks
1–2's files (`battery_2n.py`, `run/*`, `test_battery_2n.py`,
`test_stages_2n.py`, `conftest.py`, `make_referents_2n.py`) — only
`analyze_2n.py`, `power_2n.py`, `tests/test_analyze_2n.py` (modified,
per the brief's allowance) and the five new files. `power_2n.
DELTA_FORMULA_2N == analyze_2n.DELTA_FORMULA_LITERAL_2N` confirmed
`True` at the interpreter.

One deliberate deviation from pure verbatim in `tests/full_shape.py`:
the internal `_cached(name, fn)` helper's second parameter was renamed
to `fn_` (2m's file used `fn`), because `full_shape.py` now also
imports `experiments.exp2j.functionals_2j as fn` at module scope (2m's
file has no such import) — keeping the parameter named `fn` would shadow
the module alias inside every call site. Purely a naming fix, same
behavior.

## Task 5: the real-tree closure — frozen literals, the import-surface pin, the pre-campaign manifest, the mutation harness, the read sweep

ZERO model contact, ZERO network end to end. Python
`~/emergence-lab/.venv/bin/python` with `PYTHONDONTWRITEBYTECODE=1`,
run from the repo root with `-p no:cacheprovider`. Started at HEAD
`c3737446`.

### Step 1 — `FROZEN_SHA256_2N` pinned as a literal (54 modules)

`frozen_from_disk()` over `FROZEN_FILES_2N` = 2m's 48 frozen modules +
2m's four now-frozen tag-bound instrument blobs + 2n's own
`power_2n.py` and `make_referents_2n.py` = **54**. `check_frozen_2n()`
passes for real.

The `if not bn.FROZEN_SHA256_2N:` monkeypatch stand-in dropped
(`test_stages_2n.py::_blobs_that_exist`) and the `frozen_check`
no-op-override bypass dropped at both `pm.main()` call sites in
`test_power_2n.py`. `test_analyze_2n.py`'s unconditional `_frozen_pin`
autouse fixture STAYS (2m kept its own equivalent at Task 5 — verified
by `git log -p` on 2m's file, no `if not` guard on it); as do
`test_battery_2n.py`'s two deliberate `FROZEN_SHA256_2N` monkeypatches
(the empty-pin refusal and the drift raise). `test_battery_2n.py +
test_stages_2n.py + test_power_2n.py -m "not slow"`: 59 passed, 1
deselected, 81 s. Commit `8d939e31`.

**After this, `power_2n.py` and `make_referents_2n.py` cannot change
without re-pinning** — Step 3's `N_FILES_2N` literal did exactly that
(see below).

### Step 2 — the import-surface scan (`IMPORTED_SHA256_2N`, 4 modules)

`tests/import_scan_2n.py` = 2m's `import_scan_2m.py` with 2n's roots,
2m's own residual pin (`analyze_2m.IMPORTED_SHA256_2M`) folded into
`covered` beside 2j's/2k's/2l's, and the six 2n stage tools pulled into
`sys.modules` by hand. The residual surface is **4 modules**:
`experiments/exp2n/__init__.py`, `run/__init__.py`,
`run/preflight_2n.py`, `verify_referents_2n.py` — exactly the brief's
predicted shape.

**DISCLOSURE (checklist 27):** the scan runs `analyze_2n.run()` on the
REAL pre-campaign tree. It printed **INSUFFICIENT_DATA and no T** (11
referent/loader failures: the missing prereg tag plus the absent
endpoint/rung-set/power/sweep records), after executing every
predictor-side loader (2k's tier at both sizes through its own gate-1
re-derivation, 2i's sealed OLMo-2 1B counts, both predictor-seal
reads). Nothing written. Recorded in `experiment-2n-design.md` §2.

`test_analyze_2n.py` after pinning: 67 passed, 161 s. Commit `591ad281`.

### Step 3 — the pre-campaign referent manifest (4,427 files)

`python -m experiments.exp2n.make_referents_2n` → **4,427 files**, sha
`09ddc3aed6f0229d38fb4aed83b4c17f5b9a3bc96d077845f1526a1849d6431a`.
`N_FILES_2N = 4427` set, re-run: same count, same sha —
**byte-idempotent**. `REFERENTS_2N_SHA256` pinned to it.

Setting `N_FILES_2N` changed `make_referents_2n.py`'s own bytes, so its
entry inside `FROZEN_SHA256_2N` needed re-pinning (`67dcbf7d…` →
`98eb723c…`, marked in the source) — 2m's Task 5 did the same one-line
re-pin.

Composition: 2m's whole pre-campaign referent list (2l's/2k's/2j's/
2i's lists, the 2i predictor stage and sweep, 2k's tier files, seal and
power record, 2l's OWN campaign artifacts) + 2m's OWN campaign
artifacts (102 endpoint records, rung set, power record, the 26-step
sweep tree, `gate1.json`, `verdict.json` — S8 reads the SmolLM3-3B
outcome through 2m's frozen loaders) + 2m's four instrument blobs +
2n's own `checkpoints_2n.json`, `hub_inventory_comma.json` and
`power_2n.py`.

**The manifest decision, ledgered:** `REFERENTS_2N_SHA256` pins the
PRE-CAMPAIGN manifest only. 2n's own campaign artifacts (102 endpoint
records + the rung set + the power record) are bound by
`exp2n-endpoint-sealed`, and every sweep record additionally carries
the composite `endpoint_sha256` the analyzer re-derives — so the
preregistration tag is never re-cut after the campaign.

`verify_referents_2n`: **14/14** (items 3 and 12 now live). Commit
`5f0bce17`.

### Stand-in removal (interstitial, both pins live)

| site | what went |
| --- | --- |
| `tests/full_shape.py::run_world` | `frozen_check=(None if …)` / `imports_pinned=(True if …)`; only `referents_sha=False` stays (a synthetic root is not the real tree) |
| `tests/test_full_shape_2n.py` (two direct `an.run` calls) | both expressions and their stand-in comments |
| `tests/test_totality_2n.py::_run` | the two `kw.setdefault(...)` bypasses |

Commit `3d3cda97`. `test_battery_2n.py + test_stages_2n.py +
test_analyze_2n.py + test_power_2n.py -m "not slow"`: **126 passed, 1
deselected, 248 s** — every fast module clean under the real pins.
`test_full_shape_2n.py + test_totality_2n.py`: **57 passed, 1293.5 s
(21.5 min)** — every world reaches its declared terminal and every
totality case observes its forced exception, under the real pins. (The
first attempt at this run collided with the mutation harness's own
first-pass baseline check, launched concurrently, and was killed by the
OS for memory pressure ~15 min in, nothing partial written; the
mutation harness was stopped, its one in-flight mutant's
`.mutation_backup` restored byte-identically — `check_frozen_2n()`
verified clean — and this run re-launched alone; the mutation harness
restarted from mutant 1 afterward, so the two heavy suites never run
concurrently again.)

### Step 5 — the read sweep: (e) unpinned = 0

`tests/read_sweep_2n.py` = 2m's `read_sweep_2m.py` with 2n's roots,
`an2m`/`bm` pre-imported, 2m's residual pin folded into `frozen`, the
sweep tree over `GRID_COMMA + (TWIN,)`, and `SHA_PIN_AT_LOAD` extended
with `bm.CHECKPOINTS_PATH` and `bn.CHECKPOINTS_PATH`. `blobs_bound`
left at its default (real git: 2k's and 2i's predictor seals bind for
real); `tag_exists`/`blob_sha` are the documented sweep-only stand-ins
for the not-yet-cut prereg tag; `referents_sha`, `imports_pinned` and
`frozen_check` all left at their real pinned defaults and all passed.

Run BEFORE the mutation harness's first mutant write (verified: no
`.mutation_backup` file present immediately before or after the run,
and `git status` on the four mutated files was clean throughout) —
deliberately sequenced to avoid reading a temporarily-mutated file.

**DISCLOSURE (checklist 27):** the sweep runs `analyze_2n.run(n_perm=30,
n_boot=10, write=False)` on the REAL pre-campaign tree. It printed
**INSUFFICIENT_DATA and no T** — 10 referent/loader failures, all of
them the absent campaign artifacts (rung set, power record, the
endpoint seal's 104 blobs, the three endpoint whichs, the composite
sha, gate 1, the sweep, the gate-1 re-derivation). Recorded in
`experiment-2n-design.md` §2.

```
6179 distinct paths opened for reading (8553 total open/read calls)
  writes observed (should be 0, write=False): 0

category                       count
referents_2n.json               4428
frozen_module                     64
instrument_blob                    4
sha_pin_at_load                    0
seal_bound_campaign_absent         0
python_stdlib_venv              1683
UNPINNED                           0

(e) unpinned verdict input: 0 — clean
(f) seal-bound campaign artifact, absent pre-campaign: 0
```

`referents_2n.json` 4,428 = the manifest's 4,427 files + the manifest
file itself (which pins its own sha). 2m's committed campaign
artifacts, which S8 reads once 2n's campaign exists, are inside that
count — bucket (a), as intended. `seal_bound_campaign_absent` 0 is
structural: pre-campaign the analyzer refuses on `is_file()` guards
before attempting an `open()` of a seal-bound artifact, so the wrapper
records nothing to classify; this bucket becomes non-empty at the
process-tail re-run after `exp2n-endpoint-sealed` exists.

**Process tail:** re-run `tests/read_sweep_2n.py` once AFTER the
endpoint seal tag is cut — (e) must still be 0, and the campaign-side
paths must then resolve for real.
