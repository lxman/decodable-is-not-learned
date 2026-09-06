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
