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

### Step 4 — the mutation harness: 192 mutants (191 + the round-guard mutant added in fix round 1), **192 killed, 0 survivors, 0 SKIP — CLOSED (fix round 2)**

**Survivor #6** (`build_manifest_comma: main duplicate refusal removed`)
needs a NEW fast test (dropping `("main", REV_MAIN_2N)` from the
duplicate-refusal loop's iteration tuple is unobserved by the existing
suite) — deferred to the follow-up round. **`_STAGE1_RE_2N`'s
documented-equivalent CANDIDATE (#11) was KILLED**, resolving it as
NOT equivalent, no proof needed. The `run/sweep_2n.py` reorder
candidate has not been reached yet.

`tests/mutation_check.py` = 2m's harness (the `_totality_mutants`
import from 2i, `_refuse_if_any_backup_exists`, `_acquire_backup`,
`run_suite`, `_parse_only`, `main`, the FAST/TOTALITY/FULLSHAPE
switches) with 2n's paths and `M` = **147 hand-written mutants**
(2m's 110 hand-written mutants transposed to 2n's identifiers, minus
one dropped, plus one split into two, plus the brief's 2n-specific
additions — see below) **+ 44 AST-generated `collect_total` totality
mutants** via `_totality_mutants(Path("experiments/exp2n/analyze_2n.py"))`
= **191**. Before launch: a target-resolution check confirmed every
`old` occurs EXACTLY ONCE in the pristine source (0 mismatches across
191 entries) and every mutation, applied, still parses (`ast.parse`,
0 syntax errors across 191).

**Transposition notes (2m's 110 hand-written mutants → 2n):**

- **Dropped, no 2n analog:** `LOG_HEAD_SUBSET_2M with 120000 added` —
  2n has no two-tier grid/log-head-subset pair; its single
  `EVERY40K_SUBSET_2N` control is covered instead by the brief's own
  "`EVERY40K_SUBSET_2N` fed `GRID_COMMA`" mutant (drop 460000 from the
  tuple, still a valid strict subset so the load-time check stays
  silent) plus the analyze-level "sensitivities: every40k_subset fed
  GRID_COMMA" mutant (2m's #99 transposed).
- **Split into two:** 2m's "the stage-3 duplicate refusal removed"
  (#6) has no clean 1:1 map — 2n's `build_manifest_comma` checks
  `stage2_final` and `main` (both duplicate-signature-checked, unlike
  2m's weightless `base`) in ONE shared loop over
  `(("stage2_final", REV_STAGE2_FINAL_2N), ("main", REV_MAIN_2N))`, so
  a single textual edit cannot isolate either check. Two mutants
  target the SAME `old` (the loop line) with different `new` (drop one
  tuple entry each): "main duplicate refusal removed" and "the
  stage2_final duplicate refusal removed" — both explicitly named in
  the brief's own list.
- **Structure changed, replaced rather than transposed:** 2m's #32–34
  (`check_tokenizer_2m`'s separate `if pad_id != …`/`if eos_id != …`/
  BOS-prepend checks) don't exist in 2n's form — `check_tokenizer_2n`
  merges pad/eos/bos/unk into ONE loop tuple. Replaced by the brief's
  four `check_tokenizer_2n`-specific mutants (plain-render special
  check, BOS-render check, `len(tok)` check, the bos/unk loop entries)
  which target the actual 2n shape.
- **Consolidated with a brief-listed 2n mutant:** 2m's #41 ("the
  endpoint loop skips the base") IS the brief's "the stage2_final load
  dropped from the loop" (`ENDPOINT_WHICH_2N` → `("stage1_final",
  "main")`); 2m's #51 ("the tokenizer commit -> bm.REV_BASE_2M") IS
  the brief's "the twin's tokenizer commit → REV_MAIN_2N". Not
  double-counted.
- **All other 106 of 2m's 110** transposed 1:1 (`bm`→`bn`, `_2m`→`_2n`,
  `_3b`→`_comma`/`comma`, `GRID_3B`→`GRID_COMMA`, `SIZE_OUT`/`FAMILY`/
  `N_ITEMS`/`TWIN_SEED` unchanged, `ENDPOINT_WHICH_2M`
  `("stage1_final","stage3_final","base")` → `ENDPOINT_WHICH_2N`
  `("stage1_final","stage2_final","main")`), each verified against the
  real 2n source text before inclusion.

**2n-specific additions (44 mutants, the brief's named list):** the
BOS render + eos-stop plumbing (`render_2n`, `BosRunner.generate`,
`set_eos_stop_2n` ×2); the render/eos_stop_id overrides on
`item_record_2n` (×2) and `endpoint_item_record_2n` (×2, alongside the
transposed dtype-override mutants on both); `checkpoint_record_2n`'s
`generation_eos_token_id` key; `check_tokenizer_2n`'s four checks;
`EVERY40K_SUBSET_2N`/`_STAGE1_RE_2N`/the two duplicate-refusal splits/
`R_COMMA` key rename; both files' `real_loaders` BosRunner; the twin's
`REV_MAIN_2N`/stage2_final-loop-drop (both = transposed #51/#41, not
double-counted); `_record_common_failures_2n`'s render/eos_stop_id pin
drops (×2, alongside the transposed dtype-pin-drop); the checkpoint/
twin `generation_eos_token_id` failure checks (×2); `thinned_x_b_2n`'s
two variants (last-block, no-thinning); `paired_contrast_2n`'s
unpaired-draws variant + `_contrast` sign flip; `annotation_c_2n`'s
four CI-rule mutants (ci[0], ci[1], branches swapped, covers negated);
`read_increment_3b_2n`'s literal-substitution; the `round(…,4)` guard
in `run()`; `s8c_corpus_contrast_2n`'s groups-swapped + smollm3_3b-
dropped-from-dclm; `load_committed_outcomes_2n`'s smollm3_3b key drop;
`s9_sign_ledger_2n`'s OPTION_RUNGS_2N→the-nine; `verdict_2n`'s
annotation-not-returned; `_licensed_2n`'s modifier-dropped;
`_c_modifier_key_2n`'s covers/excludes swap; the C-failure-misrouted-
to-`sec_failures_c` mutant (named in the brief as "must be KILLED by
the totality case" — `test_totality_2n.py`'s existing
`_insufficient(root, seal, "2n annotation C")` case is expected to
catch it, since the misrouted failure leaves `failures` empty and the
run proceeds past the INSUFFICIENT_DATA gate into a real verdict,
failing that test's `v["verdict"] == "INSUFFICIENT_DATA"` assertion —
unconfirmed, the harness has not reached this mutant yet); the
sensitivities' every40k_subset-fed-GRID_COMMA + control-flag flip;
`load_power_2n`/`check_power_claims_2n`'s delta_sd requirement/
formula/k_by_rung/rungs mutants.

Documented-equivalent CANDIDATES named by the brief, not yet resolved
(the harness has not reached them): `_STAGE1_RE_2N`'s `\d{6}` → `\d+`
(2n's real inventory/manifest data is always 6-digit zero-padded, so
this may be observationally equivalent absent a fixture with a
malformed step name — needs a hand inventory with a 5-digit step name
to prove or kill, per the brief); the `run/sweep_2n.py` reorder mutant
(`endpoint_sha` computed before the endpoint seal binds) — 2m's own
identical candidate was KILLED by the fast suite in pass 1, so this
one may resolve the same way.

**The fast pass EXITED (2026-09-06, before fix round 1): 153/191
killed, 38 survivors, 0 SKIP, tree clean, no stray backup.**

### Fix round 1 (2026-09-06 evening)

**Important finding (from review): mutant "the `round(…, 4) !=` guard
in run() removed" was DESCRIBED in this ledger and in the build report
but was never actually added to `M`.** Corrected: appended as mutant
**#192** (after `M += _totality_mutants(AN)`, so it does not renumber
any of 1–191) — `run(): the round(…, 4) != guard removed`, on
`analyze_2n.py`'s `if increment_3b is not None and round(increment_3b,
4) != round(INCREMENT_3B_2N, 4):` guard. Ran alone with `--only 192`:
**SURVIVED** on the first run (the guard is unreachable on any real
committed tree, where `read_increment_3b_2n` already agrees with
`INCREMENT_3B_2N` to 4dp). Closed with a new totality test,
`test_increment_3b_mismatch_is_a_referent_failure` (mocks
`read_increment_3b_2n` to return a mismatched-but-non-raising value) —
queued for `--totality --only 192` confirmation alongside the other
totality-class survivors (below); not yet confirmed killed.

**38 fast-pass survivors, split by what can observe them:**

**11 closable at fast-test speed** (no `run()` on a synthetic tree
needed) — all now closed and CONFIRMED KILLED via `--only <id>`:

| id | mutant | closed by |
| --- | --- | --- |
| 6 | `build_manifest_comma`: main duplicate refusal removed | NEW `test_battery_2n.py::test_build_manifest_comma_refuses_a_non_grid_revision_duplicating_main` + `_inventory(dup_main=True)`: the EXISTING `test_build_manifest_comma_main_is_a_weight_bearing_entry_and_grid_dups_against_it_refuse` makes a GRID revision duplicate main, which the per-grid-step loop ALSO catches (`step != ENDPOINT_STEP_2N and same`) — doesn't isolate the `("main", …)` tuple entry. A NON-grid, non-canonical revision (step 99997, not in `GRID_COMMA`) duplicating main is reachable ONLY through that entry |
| 71 | `verdict_2n`: annotation not carried into the return | extended `test_verdict_2n_reason_carries_the_annotation` with `assert t["annotation"] == {...}` / `t2["annotation"] is None` — the existing test only checked the `reason` STRING, never the returned dict's `annotation` key |
| 73 | `_licensed_2n`: the annotation modifier dropped | NEW `test_licensed_2n_appends_the_c_modifier_keyed_by_reading_and_covers` — no existing test called `_licensed_2n` on a tree carrying an `annotation` at all |
| 74 | `_c_modifier_key_2n`: covers/excludes swapped | same new test, two cases (`covers_3b_increment` True/False) asserting the OPPOSITE modifier text is absent |
| 116 | `run()/_core`: Test A predictor -> counts[64] instead of counts[K_TOTAL] | NEW `test_core_x256_indexes_k_total_not_a_bare_literal`, extending the existing AST-based `_core` test (2m's #88 pattern) to the `x256` dict-comprehension's subscript index (`DictComp.value`, not `.elt`) |
| 125 | `annotation_c_2n`: ci[0] > 0 -> >= 0 | NEW `test_annotation_c_2n_ci_boundary_readings_and_covers_flag`, `paired_contrast_2n` mocked to return `ci95=[0.0, 0.05]` — the real bootstrap in the existing test never lands a bound exactly on zero |
| 126 | `annotation_c_2n`: ci[1] < 0 -> <= 0 | same new test, `ci95=[-0.05, 0.0]` |
| 128 | `annotation_c_2n`: covers -> not covers | same new test, `ci95=[0.01, 0.03]` against `increment_3b` inside vs. outside the interval |
| 129 | `read_increment_3b_2n`: returning the literal instead of the file's value | NEW `test_increment_reader_returns_the_files_own_value_not_a_hardcoded_literal` — **two names needed**: the first attempt, `test_read_increment_3b_2n_returns_...`, itself matched the `-k "not test_read_increment"` substring exclusion (the same trap `mutation_check.py`'s own docstring warns about for `test_s4`/`test_s5`/`real_tree`) and SURVIVED under that name; renamed, confirmed killed |
| 140 | `load_committed_outcomes_2n`: the smollm3_3b key dropped | NEW `test_load_committed_outcomes_2n_covers_all_five_sources`, all five upstream loaders (`an2j.load_pythia_outcomes`, `bi.load_manifest`, `an2i.load_sweep_7b`/`outcomes_7b`, `bl.load_manifest_13b`/`endpoint_sha256`, `an2l.load_sweep_13b`/`outcomes_13b`, `bm.load_manifest_3b`/`endpoint_sha256`, `an2m.load_sweep_3b`/`outcomes_3b`) mocked to sentinels — no real tree reads |
| 141 | `s9_sign_ledger_2n`: OPTION_RUNGS_2N -> the nine | NEW `test_sign_ledger_rows_are_exactly_the_three_option_rungs` (hand-built 2l/2m verdict.json stand-ins in `tmp_path`) — the EXISTING `test_s9_sign_ledger_2n_reads_the_committed_option_rung_ds` already asserts the same thing but is excluded from the fast pass by the same `-k "not test_s9_sign"` substring filter |

Confirmation commands and results:
```
--only 6,71,73,74,116,125,126,128,129,140,141   (first pass)
-> 10/11 killed; 1 survivor: 129 (the -k substring-exclusion trap, above)
--only 129   (after the rename)
-> 1/1 killed; 0 survivors
```

**27 need `run()` on a synthetic tree** (the fast pass structurally
cannot observe them — `test_totality_2n.py`/`test_full_shape_2n.py`
aren't in `FAST_TESTS`), queued for the confirmation passes, NOT YET
RUN: `run()`-internal ids **134, 135, 136, 137**, and totality-class
`collect_total`-strip ids **153, 157, 158, 159, 160, 161, 162, 171,
173, 175, 177, 178, 179, 180, 181, 182, 183, 184, 187, 188, 189, 190,
191**, plus the new **192** (the round-guard mutant, above) = **28
ids total**. Plan: `--totality --only <the 28 ids>` first (cheaper,
≈ 6 min/mutant ≈ 2.8 h); whatever survives THAT escalates to
`--fullshape --only <survivors>` (≈ 15–20 min/mutant) as a second
pass. `test_totality_2n.py`'s own existing ~40-case suite is expected
to kill most of these outright (they were never given a dedicated
totality test — the suite's EXISTING forced-exception/world coverage
is the first line of defense); #134/#135/#192 additionally got NEW
totality cases in this fix round (`test_increment_3b_mismatch_is_a_
referent_failure` for #192; #134/#135 not yet covered by name — the
existing `test_check_imports_2n_post_secondaries_forced_exception` and
`test_annotation_c_forced_exception` may already reach them, unverified
until the pass runs).

**[CORRECTED AT THE FREEZE, 2026-09-07 — the T5 deferred minor.** The
28-id plan above was superseded within the hour: mutant #192 is closed
by `test_analyze_2n.py::test_run_refuses_a_2m_increment_off_the_literal`,
a FAST test outside the totality module, so it was dropped from the
totality list. The pass that actually ran — the controller's clean
single-instance relaunch at 22:58, after the two-instance incident
ledgered below — targeted **27** ids, and the round-2 tally table is
the right one. The paragraph is kept verbatim as the interim record.]

**SUPERSEDED (the committed `mutation_totality.log` shows 27 ids;
#192 was never in the totality pass — see the fix-round-2 table):
STATUS: totality confirmation pass LAUNCHED detached, pid `27702`,
log `experiments/exp2n/mutation_totality.log`, targeting the 28 ids
`134,135,136,137,153,157,158,159,160,161,162,171,173,175,177,178,179,
180,181,182,183,184,187,188,189,190,191,192`. Full fast-suite sanity
check re-run first (after all fix-round-1 test edits): `test_battery_2n.py
+ test_stages_2n.py + test_analyze_2n.py + test_power_2n.py -m "not
slow"` → **133 passed, 1 deselected, 252.8 s** (7 more passing than
the pre-fix-round 126, matching the 7 new/extended test functions).
NOT YET COMPLETE.** This build session is reporting
**DONE_WITH_CONCERNS** again for exactly this reason.

### Ruling R-7 (fix round 1): `.gitignore`

Removed `experiments/exp2n/mutation_*.log` from `.gitignore` (the
committed mutation logs ARE the mutation battery's record, 2l D-1's
precedent — kept for 2l/2m but never applied to 2n's own block); the
seven 2n stage logs (`preflight.log`, `endpoint.log`, `power.log`,
`sweep.log`, `analyzer.log`, `watcher_endpoint.log`,
`watcher_sweep.log`) stay ignored. `mutation_build.log`,
`mutation_fast_survivors.log` (the two `--only` confirmation runs
above), and `mutation_totality.log` (once it exists) are committed.

### Fix round 2 (2026-09-06/07) — mutation harness CLOSED, 192/192 killed

**The 22:58 incident (one sentence):** the previous implementer, stopped
but not yet reaped, briefly launched a second `--totality` instance
beside the controller's own relaunch — both were killed within minutes,
no `.mutation_backup` was left, the four instrument blobs stayed
byte-clean against HEAD, and the one partial `mutation_totality.log`
from that overlapping window was discarded and overwritten by the
clean single-instance relaunch, so nothing from it is counted below.

**Final tally by pass:**

| pass | command | log | result |
| --- | --- | --- | --- |
| 1 (fast) | `mutation_check.py` (detached) | `mutation_build.log` | 153/191 killed, 38 survivors, 0 SKIP |
| 2 (fast, `--only`) | 11 fast-closable survivors, first try | `mutation_fast_survivors.log` | 10/11 killed; #129 survived (a `-k "not test_read_increment"` substring-exclusion trap on the closing test's own name) |
| 3 (fast, `--only 129`) | after renaming the closing test | `mutation_fast_survivors.log` | 1/1 killed |
| 4 (fast, `--only 192`) | the round-guard mutant, added to `M` in fix round 1 after review found it missing; its own closing test lives in `test_totality_2n.py`, not one of the four `FAST_TESTS` files, so the fast pass never saw a covering test | `mutation_fast_survivors.log` | 0/1 killed — SURVIVED |
| 5 (totality, `--only` 27 ids) | `134,135,136,137` + 23 `collect_total`-strip ids | `mutation_totality.log` | 25/27 killed; survivors #136, #137 (the `every40k_subset` sensitivity — observable only through the world module) |
| 6 (fast, `--only 192`, round 2) | after `test_run_refuses_a_2m_increment_off_the_literal` (a NEW `test_analyze_2n.py` test, monkeypatching `read_increment_3b_2n` to a mismatched-but-non-raising 0.07) | `mutation_fast_survivors.log` | 1/1 killed |
| 7 (fullshape, `--only 136,137`) | detached, ≈ 25 min | `mutation_fullshape.log` | 2/2 killed — both already asserted by the existing world test `test_s8_five_rows_s8c_and_s9` (`sens["every40k_subset"]["control"] is True` and `["steps"] == list(bn.EVERY40K_SUBSET_2N)`), no new assertion needed |

**192 mutants total (the 147 hand-written + 44 AST-generated `collect_total` totality mutants = 191, plus the round-guard mutant added post-hoc as #192), 192/192 killed, 0 open survivors, 0 SKIP across every pass.**

**Documented-equivalent candidates: none needed a proof.** Both
mutants the brief flagged as possible equivalents —
`_STAGE1_RE_2N`'s `\d{6}` → `\d+` (#11) and the `run/sweep_2n.py`
reorder mutant, `endpoint_sha` computed before the endpoint seal binds
(#65) — were **killed outright by the fast pass** (`mutation_build.log`
lines 13 and 67), so both resolve as NOT equivalent with no fixture or
proof required.

**Every gap closed:**

| id(s) | mutant | closed by |
| --- | --- | --- |
| 6, 71, 73, 74, 116, 125, 126, 128, 129, 140, 141 | see the fix-round-1 table above (unchanged this round) | fix round 1's eleven new/extended fast tests |
| 192 | `run()`'s `round(increment_3b, 4) != round(INCREMENT_3B_2N, 4)` guard removed | NEW `test_analyze_2n.py::test_run_refuses_a_2m_increment_off_the_literal` (fix round 2) — monkeypatches `an.read_increment_3b_2n` to return `0.07` (a mismatch that does NOT raise, unlike the sibling forced-exception tests) and asserts `an.run(n_perm=20, n_boot=5)` lands `INSUFFICIENT_DATA` with `"2n increment 3b"` and `"0.07"` in `v["referents"]["failures"]`. Fix round 1's totality-side test, `test_totality_2n.py::test_increment_3b_mismatch_is_a_referent_failure`, stands as additional coverage but does not sit in a `FAST_TESTS` file, so it could not close the fast-pass survivor by itself |
| 136, 137 | `sensitivities`: `every40k_subset` computed over `bn.GRID_COMMA` instead of `EVERY40K_SUBSET_2N`; `every40k_subset`'s `"control"` `True` → `False` | ALREADY closed by the existing world test `test_full_shape_2n.py::test_s8_five_rows_s8c_and_s9` (`sens["every40k_subset"]["control"] is True and sens["every40k_subset"]["steps"] == list(bn.EVERY40K_SUBSET_2N)`), confirmed by a targeted `--fullshape --only 136,137` run — no new test written |

**Test counts, reconciled (correcting the original Task 5 report's
unreconciled "793 total tests" claim — see the report's Fix round 2
section):** fast modules (`test_battery_2n.py` + `test_stages_2n.py` +
`test_analyze_2n.py` + `test_power_2n.py`, `-m "not slow"`) **134
passed, 1 deselected** (133 after fix round 1's seven new/extended
functions, +1 for this round's new test); world + totality
(`test_full_shape_2n.py` + `test_totality_2n.py`, full, no `-m`
filter) **58 passed** (0 deselected — full_shape 16 + totality 42
raw `def test_` counts under-report the parametrized total; 58 is the
pytest-collected figure, 22:12 wall); cold battery (`verify_referents_2n`)
**14/14**. No figure anywhere adds to 793; that number never
corresponded to a run this build actually made.

Confirmed clean at the close of this round: no `*.mutation_backup`
anywhere under `experiments/exp2n`; the four instrument blobs
(`analyze_2n.py`, `battery_2n.py`, `run/endpoint_2n.py`,
`run/sweep_2n.py`) byte-equal to HEAD; `mutation_totality.log` and
`mutation_fullshape.log` committed alongside this ledger entry.

## Task 6 — the adversarial freeze (2026-09-07)

Fresh opus reviewer, cold, on `experiments/exp2n/` at build HEAD
`ef0fa6b6`; brief `.superpowers/sdd/2026-09-06-exp2n-build/task-6-brief.md`
(the plan's attack list 1–33 + item 34 from Ruling R-6); template
`experiments/exp2m/FREEZE_CHECKLIST.md`. Zero model contact and zero
network throughout. Full record: `experiments/exp2n/FREEZE_CHECKLIST.md`.

**Verdict on the assignment: the CLASS DEFECT was NOT FOUND.** No
reachable path was found on which 2n delivers a verdict computed from
the wrong bytes; every tree the two runners can leave reaches a frozen
terminal (19 shapes, 19/19 INSUFFICIENT_DATA, 0 raises). Four findings
were found and closed additively.

### Chronology

| when | what | result |
| --- | --- | --- |
| baseline, cold | fast modules (four, no `-m` filter) | 135 passed, 257.5 s |
| baseline, cold | worlds + totality | 58 passed, 1,306.9 s |
| baseline, cold | `verify_referents_2n.py` | 14/14 |
| before the closures | F-1/F-2/F-3/F-4 demonstrations + attack executions | see FREEZE_CHECKLIST |
| before the closures | the 19 runner-left tree shapes | 19/19 frozen terminal |
| closures | F-1..F-4 applied, `IMPORTED_SHA256_2N` re-pinned | commit `68a0fd42` |
| after | the same demonstrations, the same shapes | every refusal fires |
| after | cold battery, read sweep, worlds + totality, determinism, mutation | see the cold re-run table |

### Findings

- **F-1 — the endpoint whichs' stop-id attestation was the CONSTANT,
  not a measurement.** The three endpoint `which`es carry no checkpoint
  record (2m F-2's shape), so unlike every sweep step nothing measured
  that dial o's `set_eos_stop_2n` had run: `eos_stop_id` is stamped
  from `EOS_STOP_ID_2N` whatever the load did. Demonstrated:
  `run/endpoint_2n.run` driven twice with loaders whose `info` reported
  generation eos 3 and 2 produced **102 records with ZERO differing
  fields**, both clean through `endpoint_record_failures_2n`, both
  yielding the same R_PRIMARY. Gate 1 cannot see it either — it
  compares the thin-loaded endpoint against the candidate-loaded
  step 460000, and a miss on BOTH sides leaves both continuation sets
  equal (a one-sided miss it does catch). Closed additively:
  `endpoint_item_record_2n` takes a REQUIRED `eos_facts` (the loader's
  own `info`) and stamps `config_eos_token_id` /
  `generation_eos_token_id`; `endpoint_record_failures_2n` requires the
  measured id to equal the pinned stop id; `run/endpoint_2n` passes
  `info`. World W29, four fixtures, mutants 193/194.
- **F-2 (Ruling R-6) — the `delta_sd` power line could describe a wider
  rung set than the annotation C reads.** `power_2n.delta_sd_2n` fixes
  `rungs` to R_PRIMARY minus the two predictors' degeneracy union;
  `run()` computes C over the two tests' ELIGIBLE intersection, which
  also drops n_pos-thin rungs. So `min_detectable_delta` — the number
  the projection places its Δ call against — could cover rungs the
  interval never read, with no disclosure. Closed additively:
  `_delta_sd_scope_2n` + a disclosure in `verdict_2n` naming the extra
  rungs, riding on the licence (2l F-4 / 2m F-1's shape on the third
  declaration). No bar, rule or dial moved. World W28, two fixtures,
  mutants 195/196.
- **F-3 (attack item 33) — `min_detectable_delta` was attested and
  never re-derived.** `load_power_2n` pinned the `formula` STRING; the
  NUMBER rode under it, so `min_detectable_delta = 10.0` against a
  `delta_boot_sd_null` of 0.012 passed every check. Closed additively:
  `check_power_claims_2n` re-derives it from the record's own
  `delta_boot_sd_null` by that literal (both-`None`, the writer's
  degenerate return, stays legal). Three fixtures, mutant 197.
- **F-4 — `pins_active` stated three of `run()`'s seven test-only
  injections.** A record produced with git stubbed
  (`tag_exists`/`blob_sha`/`blobs_bound`) or with S8's committed readers
  replaced said nothing about it. Closed additively: `prereg_binding`,
  `seal_binding`, `s8_committed_readers` (2k D-1's field, completed).
  Three fixtures, mutant 198.

### Disclosures (design §2 entries 4–6)

The freeze ran `analyze_2n.run()` on the REAL pre-campaign tree twice —
`tests/import_scan_2n.py` (the `IMPORTED_SHA256_2N` re-pin;
INSUFFICIENT_DATA, 11 failures, no T) and `tests/read_sweep_2n.py`
(INSUFFICIENT_DATA, 10 failures, no T, 0 writes, 6,179 distinct paths,
bucket (e) = 0). Every finding was demonstrated on synthetic roots or
hand inputs.

### Cold re-runs and the mutation battery (the freeze)

| battery | baseline (cold, before) | after the closures |
| --- | --- | --- |
| fast modules (four, no `-m` filter) | 135 passed, 257.5 s | **139 passed**, 263.2 s |
| worlds + totality | 58 passed, 1,306.9 s (27 specs) | **61 passed**, 1,374.2 s (**29 specs**, every terminal) |
| cold referent battery `verify_referents_2n.py` | 14/14 | **14/14** (after the closures AND after the `IMPORTED_SHA256_2N` re-pin) |
| read sweep `tests/read_sweep_2n.py` | — | 6,179 distinct paths, 8,553 open/read calls, **(e) unpinned = 0**, 0 writes, INSUFFICIENT_DATA |
| import scan `tests/import_scan_2n.py` | — | 4 modules, INSUFFICIENT_DATA, 11 failures, no T; one sha re-pinned (`verify_referents_2n.py`) |
| the nineteen runner-left tree shapes | 19/19 | **19/19 INSUFFICIENT_DATA, 0 raises** |
| determinism ×2, separate processes, one world (`shared`, seed 0), n_perm 30 | — | **byte-identical**, 482,499 bytes, sha `ec00395b3a702d0bfae5eb23c874916cbc41842f77e40ceddb5e84a68328c041` |
| mutation, fast `--only 24,25,26,71,73,74,193,194,195,196,197` | — | **11/11 killed** (`mutation_freeze_fast.log`) |
| mutation, `--totality --only 198` | — | **1/1 killed** (`mutation_freeze_totality.log`) |
| mutation battery size | 192 | **198**, every target resolving exactly once |

The instrument delta the tag will bind (post-freeze shas):
`analyze_2n.py` `a860a4e7…`, `battery_2n.py` `e85165bd…`,
`run/endpoint_2n.py` `62d62959…`, `run/sweep_2n.py` `4d077ae8…`
(sweep UNCHANGED by the freeze).

Both mutation logs are committed (Ruling R-7). No stray
`.mutation_backup` after either run; the four instrument blobs
byte-clean against the working tree after each.

### Ratification apply (2026-09-07)

Michael: "Ratified — apply the slips and tag." Applied to
`experiment-2n-design.md`: doc slips (a)–(m) from
`FREEZE_CHECKLIST.md`, verbatim, at their named anchors (§1, §3.1,
§3.2, §3.3, §3.6, §3.8 ×2, §3.10 ×2, §4, §5 ×2, §7); plus the two
slips from the final whole-branch review, (c′) (§3.8, the first-block-
vs-all-blocks asymmetry beside slip (c)) and (n) (§5 Sensitivities,
striking the uncomputable "primary over the nine when R_Comma ∩
eleven ⊋ nine" row in favour of R_ELEVEN_EXTRA); the status block now
records the ratification, the F-1..F-4 closure commit, and the four
tag-bound blob shas. `experiments/exp2n/tests/test_analyze_2n.py`
gains `test_licence_composes_every_annotation_modifier_key` (final
review Minor 3): all six `_c_modifier_key_2n` outcomes (NO-LEAD ×2,
UNDEFINED, B-LEADS ×2, A-LEADS) driven through `verdict_2n` →
`_licensed_2n` and checked against `an.C_MODIFIERS_2N`, plus a lock on
`C_MODIFIERS_2N`'s key set — run alone (PASSED) and as the full module
`-m "not slow"` (**77 passed, 169.07 s**). This file's fix-round-1
"targeting the 28 ids" sentence (Minor 7) is marked SUPERSEDED in
place, pointing at the fix-round-2 27-id table. Verified: the four
tag-bound blobs (`battery_2n.py`, `analyze_2n.py`,
`run/endpoint_2n.py`, `run/sweep_2n.py`) are byte-identical to
`4d6e1663` (`git diff --quiet` empty) and their shas match the
FREEZE_CHECKLIST table exactly; `git status --porcelain` touches only
this file, `experiment-2n-design.md` and `tests/test_analyze_2n.py`.
No tag cut here — the controller cuts `exp2n-preregistered` after
verifying this diff.

## 2026-09-07 — RATIFIED + TAG `exp2n-preregistered` CUT at 013d67ba (annotated object 5c139c0f), pushed

Michael: "Ratified — apply the slips and tag." Slips (a)–(n) applied (1e3d1c96; the four prose seams the application left rejoined at 013d67ba, ratified wording unchanged); the licence-modifier composition test and the superseded ledger sentence landed with them. The tag binds analyze_2n.py a860a4e7fe3d…, battery_2n.py e85165bd0ca1…, run/endpoint_2n.py 62d62959361e…, run/sweep_2n.py 4d077ae89481… — verified through `require_prereg_2n` against real git; `check_frozen_2n` clean. Any post-tag edit to these four needs a re-tag. FROZEN. Model contact from here only on Michael's word (§7: the preflight first).

## 2026-09-07 — PREFLIGHT (dial j) PASSED on Michael's word ("Go on the preflight"): 05:2x → 05:48, detached, the first model contact of 2n

fp16 STANDS — 0 non-finite logits on both loads (max_abs 18.34 on `main`, 12.53 on step 10,000). Renders as pinned: bos render ids [2, 52, 29], plain render ids [52, 29]. Stop ids: `config eos 2 | generation eos 3` on both loads — the override runs. Memory: `main` (thin) 14.0 GB allocated / 15.0 GB peak; step 10,000 (candidate files) 28.0 GB allocated / 29.0 GB peak — the second load did not reclaim the first's pool (dial p input). Verify tallies over 20 items: main antonym 13/20 (bos) vs 15/20 (plain), main add3_mid 20/20 both; step-10k antonym 5/20 both, step-10k add3_mid 0/20 both — the pinned BOS render is not degenerate where the plain one is not; dial n stands, no re-tag. Nothing written under results/; the staged checkpoint freed. Full printout (download progress lines stripped):

```
[2n preflight] batch_size 16 dtype float16
[2n preflight] main: config eos 2 | generation eos 3
[2n preflight] main loaded (thin): mps_allocated_bytes 14005314048 peak_mps_bytes 15041249280
[2n preflight] bos render ids [2, 52, 29]
[2n preflight] plain render ids [52, 29]
[2n preflight] main: n_nonfinite 0 max_abs 18.34375
[2n preflight] antonym …"ns the opposite of 'awake': asleep, genuine, open, exact?\\nA:" -> ' asleep\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] antonym …"he opposite of 'sturdy': deep, fragile, tall, horizontal?\\nA:" -> ' fragile\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] antonym …"e opposite of 'noisy': minimum, silent, expensive, small?\\nA:" -> ' silent\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] antonym …"pposite of 'mobile': heavy, stationary, dangerous, brave?\\nA:" -> ' heavy\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] antonym …"s the opposite of 'early': plentiful, harsh, late, eager?\\nA:" -> ' late\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] antonym …"means the opposite of 'tender': sharp, limp, arid, tough?\\nA:" -> ' limp\n\nQ: Which of these means the opposite' verify=0
[2n preflight] antonym …"ns the opposite of 'thick': slender, sad, graceful, thin?\\nA:" -> ' slender\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] antonym …"he opposite of 'absent': forced, present, diligent, tall?\\nA:" -> ' forced\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] antonym …"ans the opposite of 'sober': graceful, matte, drunk, wet?\\nA:" -> ' drunk\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] antonym …"s the opposite of 'young': old, simple, straight, scarce?\\nA:" -> ' old\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] antonym …" opposite of 'graceful': clumsy, rigid, timid, plentiful?\\nA:" -> ' clumsy\n\nQ: Which of these means the' verify=1
[2n preflight] antonym …"te of 'exact': alive, superficial, approximate, wasteful?\\nA:" -> ' superficial\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] antonym …"e opposite of 'certain': broad, doubtful, occupied, cold?\\nA:" -> ' doubtful\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] antonym …"ite of 'optimistic': idle, slender, visible, pessimistic?\\nA:" -> ' pessimistic\n\nQ: Which of these means the' verify=1
[2n preflight] antonym …"posite of 'guilty': glossy, foolish, innocent, temporary?\\nA:" -> ' innocent\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] antonym …"the opposite of 'clean': timid, dirty, pessimistic, tidy?\\nA:" -> ' timid\n\nQ: Which of these means the opposite' verify=0
[2n preflight] antonym …"pposite of 'victory': destitute, open, difficult, defeat?\\nA:" -> ' defeat\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] antonym …"the opposite of 'glossy': free, sick, approximate, matte?\\nA:" -> ' matte\n\nQ: Which of these means the opposite' verify=1
[2n preflight] antonym …"opposite of 'permanent': chaotic, temporary, exact, loud?\\nA:" -> ' chaotic\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] antonym …"ns the opposite of 'polite': wet, rude, inferior, opaque?\\nA:" -> ' rude\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 744 + 660?\\nA:' -> ' 1404\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 317 + 663?\\nA:' -> ' 980\n\nQ: What is ' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 280 + 950?\\nA:' -> ' 1230\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 460 + 152?\\nA:' -> ' 612\n\nQ: What is ' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 446 + 134?\\nA:' -> ' 580\n\nQ: What is ' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 808 + 867?\\nA:' -> ' 1675\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 510 + 864?\\nA:' -> ' 1374\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 491 + 593?\\nA:' -> ' 1084\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 514 + 340?\\nA:' -> ' 854\n\nQ: What is ' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 831 + 889?\\nA:' -> ' 1720\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 154 + 631?\\nA:' -> ' 785\n\nQ: What is ' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 415 + 522?\\nA:' -> ' 937\n\nQ: What is ' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 734 + 706?\\nA:' -> ' 1440\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 431 + 250?\\nA:' -> ' 681\n\nQ: What is ' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 996 + 133?\\nA:' -> ' 1129\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 780 + 495?\\nA:' -> ' 1275\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 835 + 681?\\nA:' -> ' 1516\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 959 + 638?\\nA:' -> ' 1597\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 895 + 363?\\nA:' -> ' 1258\n\nQ: What is' verify=1
[2n preflight] add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 571 + 578?\\nA:' -> ' 1149\n\nQ: What is' verify=1
[2n preflight] plain antonym …"ns the opposite of 'awake': asleep, genuine, open, exact?\\nA:" -> ' asleep' verify=1
[2n preflight] plain antonym …"he opposite of 'sturdy': deep, fragile, tall, horizontal?\\nA:" -> ' fragile' verify=1
[2n preflight] plain antonym …"e opposite of 'noisy': minimum, silent, expensive, small?\\nA:" -> ' silent' verify=1
[2n preflight] plain antonym …"pposite of 'mobile': heavy, stationary, dangerous, brave?\\nA:" -> ' heavy' verify=0
[2n preflight] plain antonym …"s the opposite of 'early': plentiful, harsh, late, eager?\\nA:" -> ' late' verify=1
[2n preflight] plain antonym …"means the opposite of 'tender': sharp, limp, arid, tough?\\nA:" -> ' limp' verify=0
[2n preflight] plain antonym …"ns the opposite of 'thick': slender, sad, graceful, thin?\\nA:" -> ' slender' verify=0
[2n preflight] plain antonym …"he opposite of 'absent': forced, present, diligent, tall?\\nA:" -> ' forced' verify=0
[2n preflight] plain antonym …"ans the opposite of 'sober': graceful, matte, drunk, wet?\\nA:" -> ' drunk' verify=1
[2n preflight] plain antonym …"s the opposite of 'young': old, simple, straight, scarce?\\nA:" -> ' old' verify=1
[2n preflight] plain antonym …" opposite of 'graceful': clumsy, rigid, timid, plentiful?\\nA:" -> ' clumsy' verify=1
[2n preflight] plain antonym …"te of 'exact': alive, superficial, approximate, wasteful?\\nA:" -> ' approximate' verify=1
[2n preflight] plain antonym …"e opposite of 'certain': broad, doubtful, occupied, cold?\\nA:" -> ' doubtful' verify=1
[2n preflight] plain antonym …"ite of 'optimistic': idle, slender, visible, pessimistic?\\nA:" -> ' pessimistic' verify=1
[2n preflight] plain antonym …"posite of 'guilty': glossy, foolish, innocent, temporary?\\nA:" -> ' innocent' verify=1
[2n preflight] plain antonym …"the opposite of 'clean': timid, dirty, pessimistic, tidy?\\nA:" -> ' timid' verify=0
[2n preflight] plain antonym …"pposite of 'victory': destitute, open, difficult, defeat?\\nA:" -> ' defeat' verify=1
[2n preflight] plain antonym …"the opposite of 'glossy': free, sick, approximate, matte?\\nA:" -> ' matte' verify=1
[2n preflight] plain antonym …"opposite of 'permanent': chaotic, temporary, exact, loud?\\nA:" -> ' temporary' verify=1
[2n preflight] plain antonym …"ns the opposite of 'polite': wet, rude, inferior, opaque?\\nA:" -> ' rude' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 744 + 660?\\nA:' -> ' 1404' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 317 + 663?\\nA:' -> ' 980' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 280 + 950?\\nA:' -> ' 1230' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 460 + 152?\\nA:' -> ' 612' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 446 + 134?\\nA:' -> ' 580' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 808 + 867?\\nA:' -> ' 1675' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 510 + 864?\\nA:' -> ' 1374' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 491 + 593?\\nA:' -> ' 1084' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 514 + 340?\\nA:' -> ' 854' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 831 + 889?\\nA:' -> ' 1720' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 154 + 631?\\nA:' -> ' 785' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 415 + 522?\\nA:' -> ' 937' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 734 + 706?\\nA:' -> ' 1440' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 431 + 250?\\nA:' -> ' 681' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 996 + 133?\\nA:' -> ' 1129' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 780 + 495?\\nA:' -> ' 1275' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 835 + 681?\\nA:' -> ' 1516' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 959 + 638?\\nA:' -> ' 1597' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 895 + 363?\\nA:' -> ' 1258' verify=1
[2n preflight] plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 571 + 578?\\nA:' -> ' 1149' verify=1
[2n preflight] stage1-step010000-tokens21B: config eos 2 | generation eos 3
[2n preflight] stage1-step010000-tokens21B loaded (candidate files): digest 7961bac0f077, mps_allocated_bytes 28010628096 peak_mps_bytes 29002137600
[2n preflight] bos render ids [2, 52, 29]
[2n preflight] plain render ids [52, 29]
[2n preflight] stage1-step010000-tokens21B: n_nonfinite 0 max_abs 12.53125
[2n preflight] ckpt antonym …"ns the opposite of 'awake': asleep, genuine, open, exact?\\nA:" -> ' open\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"he opposite of 'sturdy': deep, fragile, tall, horizontal?\\nA:" -> ' deep\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"e opposite of 'noisy': minimum, silent, expensive, small?\\nA:" -> ' silent\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] ckpt antonym …"pposite of 'mobile': heavy, stationary, dangerous, brave?\\nA:" -> ' mobile\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"s the opposite of 'early': plentiful, harsh, late, eager?\\nA:" -> ' late\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] ckpt antonym …"means the opposite of 'tender': sharp, limp, arid, tough?\\nA:" -> ' tender\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"ns the opposite of 'thick': slender, sad, graceful, thin?\\nA:" -> ' slender\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"he opposite of 'absent': forced, present, diligent, tall?\\nA:" -> ' forced\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"ans the opposite of 'sober': graceful, matte, drunk, wet?\\nA:" -> ' graceful\n\nQ: Which of these means the opposite' verify=0
[2n preflight] ckpt antonym …"s the opposite of 'young': old, simple, straight, scarce?\\nA:" -> ' simple\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …" opposite of 'graceful': clumsy, rigid, timid, plentiful?\\nA:" -> ' rigid\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"te of 'exact': alive, superficial, approximate, wasteful?\\nA:" -> ' superficial\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"e opposite of 'certain': broad, doubtful, occupied, cold?\\nA:" -> ' certain\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"ite of 'optimistic': idle, slender, visible, pessimistic?\\nA:" -> ' slender\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"posite of 'guilty': glossy, foolish, innocent, temporary?\\nA:" -> ' innocent\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] ckpt antonym …"the opposite of 'clean': timid, dirty, pessimistic, tidy?\\nA:" -> ' tidy\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"pposite of 'victory': destitute, open, difficult, defeat?\\nA:" -> ' defeat\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] ckpt antonym …"the opposite of 'glossy': free, sick, approximate, matte?\\nA:" -> ' free\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt antonym …"opposite of 'permanent': chaotic, temporary, exact, loud?\\nA:" -> ' temporary\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] ckpt antonym …"ns the opposite of 'polite': wet, rude, inferior, opaque?\\nA:" -> ' wet\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 744 + 660?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 317 + 663?\\nA:' -> ' 1,000\n\nQ: What' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 280 + 950?\\nA:' -> ' 1050\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 460 + 152?\\nA:' -> ' 1\n\nQ: What is ' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 446 + 134?\\nA:' -> ' 1\n\nQ: What is ' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 808 + 867?\\nA:' -> ' 1238\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 510 + 864?\\nA:' -> ' 1025\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 491 + 593?\\nA:' -> ' 1,000\n\nQ: What' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 514 + 340?\\nA:' -> ' 1145\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 831 + 889?\\nA:' -> ' 1,000\n\nQ: What' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 154 + 631?\\nA:' -> ' 123\n\nQ: What is ' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 415 + 522?\\nA:' -> ' 1,000\n\nQ: What' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 734 + 706?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 431 + 250?\\nA:' -> ' 1000\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 996 + 133?\\nA:' -> ' 1217\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 780 + 495?\\nA:' -> ' 1050\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 835 + 681?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 959 + 638?\\nA:' -> ' 1217\n\nQ: What is' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 895 + 363?\\nA:' -> ' 1,000\n\nQ: What' verify=0
[2n preflight] ckpt add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 571 + 578?\\nA:' -> ' 571\n\nQ: What is ' verify=0
[2n preflight] ckpt plain antonym …"ns the opposite of 'awake': asleep, genuine, open, exact?\\nA:" -> ' open\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"he opposite of 'sturdy': deep, fragile, tall, horizontal?\\nA:" -> ' deep\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"e opposite of 'noisy': minimum, silent, expensive, small?\\nA:" -> ' silent\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] ckpt plain antonym …"pposite of 'mobile': heavy, stationary, dangerous, brave?\\nA:" -> ' mobile\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"s the opposite of 'early': plentiful, harsh, late, eager?\\nA:" -> ' late\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] ckpt plain antonym …"means the opposite of 'tender': sharp, limp, arid, tough?\\nA:" -> ' tender\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"ns the opposite of 'thick': slender, sad, graceful, thin?\\nA:" -> ' slender\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"he opposite of 'absent': forced, present, diligent, tall?\\nA:" -> ' forced\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"ans the opposite of 'sober': graceful, matte, drunk, wet?\\nA:" -> ' graceful\n\nQ: Which of these means the opposite' verify=0
[2n preflight] ckpt plain antonym …"s the opposite of 'young': old, simple, straight, scarce?\\nA:" -> ' simple\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …" opposite of 'graceful': clumsy, rigid, timid, plentiful?\\nA:" -> ' rigid\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"te of 'exact': alive, superficial, approximate, wasteful?\\nA:" -> ' superficial\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"e opposite of 'certain': broad, doubtful, occupied, cold?\\nA:" -> ' certain\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"ite of 'optimistic': idle, slender, visible, pessimistic?\\nA:" -> ' slender\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"posite of 'guilty': glossy, foolish, innocent, temporary?\\nA:" -> ' innocent\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] ckpt plain antonym …"the opposite of 'clean': timid, dirty, pessimistic, tidy?\\nA:" -> ' tidy\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"pposite of 'victory': destitute, open, difficult, defeat?\\nA:" -> ' defeat\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] ckpt plain antonym …"the opposite of 'glossy': free, sick, approximate, matte?\\nA:" -> ' free\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain antonym …"opposite of 'permanent': chaotic, temporary, exact, loud?\\nA:" -> ' temporary\n\nQ: Which of these means the opposite o' verify=1
[2n preflight] ckpt plain antonym …"ns the opposite of 'polite': wet, rude, inferior, opaque?\\nA:" -> ' wet\n\nQ: Which of these means the opposite o' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 744 + 660?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 317 + 663?\\nA:' -> ' 1035\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 280 + 950?\\nA:' -> ' 1050\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 460 + 152?\\nA:' -> ' 1\n\nQ: What is ' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 446 + 134?\\nA:' -> ' 1\n\nQ: What is ' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 808 + 867?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 510 + 864?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 491 + 593?\\nA:' -> ' 1,000\n\nQ: What' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 514 + 340?\\nA:' -> ' 1048\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 831 + 889?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 154 + 631?\\nA:' -> ' 154\n\nQ: What is ' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 415 + 522?\\nA:' -> ' 555\n\nQ: What is ' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 734 + 706?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 431 + 250?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 996 + 133?\\nA:' -> ' 1217\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 780 + 495?\\nA:' -> ' 1050\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 835 + 681?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 959 + 638?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 895 + 363?\\nA:' -> ' 1057\n\nQ: What is' verify=0
[2n preflight] ckpt plain add3_mid …'801\\n\\nQ: What is 912 + 145?\\nA: 1057\\n\\nQ: What is 571 + 578?\\nA:' -> ' 571\n\nQ: What is ' verify=0
[2n preflight] complete: 2 rung(s) × 20 item(s) × 2 renders on main and on stage1-step010000-tokens21B; nothing written under results/
```

## Endpoint stage — 2026-09-07 (Michael: 'Go on the endpoint stage.')

Launched 12:21 detached with the commit watcher (`--stage endpoint`), exited 15:31 (≈ 3 h 10 min wall; summed record time 3.10 h). 102 records (three thin loads × 34 rungs × 500 items, greedy, fp16, `render: "bos"`, stop id 3) + `results/endpoint/rung_set_2n.json`, every file watcher-committed and pushed; zero halts, zero attrition, no HALTED marker. Measured on every record: `render` bos, `dtype` float16, `eos_stop_id` 3, `config_eos_token_id` 2 (the LlamaConfig default — the tokenizer's BOS, dial o's trap) overridden to `generation_eos_token_id` 3 on every load; n = 500 on all 102.

Rung set (2d's floor rule on stage1_final, step 460000): **R_COMMA = 16** — add3_mid, add4_mid, add_base8, antonym, antonym6, arith_next, clock24_d999, median7, oct2dec, odd6, quad_next, rev_string7, reverse_string, sub3_mid, sub4_mid, sub_base8; **R_PRIMARY = the nine** (`primary_is_the_nine: true`); R_ELEVEN_EXTRA = ∅; **R_EXTRA = 7** — add4_mid 360, clock24_d999 52, median7 105, oct2dec 9, quad_next 64, rev_string7 5, reverse_string 41. Flat (18): base12_digitsum 12, base13 0, base7 0, caesar 0, caesar_len8 0, clock24 25, collatz_step2 75, count_div13 80, count_div7 42, hamming12 98, isqrt_gap 71, median5 114, mod13 37, mod13_comp 31, mod17 32, mod19 20, odd_one_out 127, roman_sum7 76.

Counts on the nine (stage1_final / stage2_final / main): add3_mid 490/492/496 | add_base8 118/119/119 | antonym 327/344/350 | antonym6 327/280/302 | arith_next 491/476/486 | odd6 127/141/147 | sub3_mid 500/500/500 | sub4_mid 407/401/418 | sub_base8 306/308/307. `main` ≥ stage1_final on 7/9; stage2_final ≥ stage1_final on 6/9.

Against 2m's SmolLM3-3B stage-1 endpoint (Comma stage1_final vs SmolLM3): add3_mid 490 vs 330, add_base8 118 vs 118, antonym 327 vs 435, antonym6 327 vs 199, arith_next 491 vs 473, odd6 127 vs 120, sub3_mid 500 vs 494, sub4_mid 407 vs 243, sub_base8 306 vs 309. Comma at 1 T is stronger on the mid-digit rungs and antonym6, weaker on antonym; the base-8 pair and odd6 land within a few items of SmolLM3's — recorded here before the projection.

Power LAUNCHED ONCE 2026-09-07 15:35 (detached, log `power.log`); the record `results/endpoint/power_2n.json` is written once and watcher-committed. Next: seal tag `exp2n-endpoint-sealed` → read sweep + cold battery → projection → the sweep on Michael's word.

## Power record — 2026-09-07 17:40 (written ONCE; `results/endpoint/power_2n.json`, watcher-committed 7e2852eb)

Launched 15:33 detached after the rung set, exited 17:40 (2 h 7 min — under the ≈ 4 h budget). Both tests on 2g's base strata, unconditioned, over R_PRIMARY = the nine, n_pos bounded below by the stage1_final counts, n_trained_steps 24, n_sim 1000, n_perm 500:

- **Test A (Pythia-1b at 256 draws, cross-family): POWERED** — P(fires | D_true = 0.15) = 1.000 against the bar 0.75; null false-fire rate 0.000; null SD of T 0.0115. Targets: D 0.1: {"rho": 0.16624661104381086, "n_sim": 1000, "n_perm": 500, "p_fires": 0.454, "p_detect": 1.0, "mean_T": 0.09840344016226, D 0.15: {"rho": 0.2512191994339228, "n_sim": 1000, "n_perm": 500, "p_fires": 1.0, "p_detect": 1.0, "mean_T": 0.1488728024940057,, D 0.2: {"rho": 0.3343310350924731, "n_sim": 1000, "n_perm": 500, "p_fires": 1.0, "p_detect": 1.0, "mean_T": 0.19877025088074493. min_detectable_T 0.0261. No degenerate rung; rungs_simulated = the nine.
- **Test B (OLMo-2 1B at 64 draws, cross-family): POWERED** — P(fires | D_true = 0.15) = 1.000 against the bar 0.75; null false-fire rate 0.000; null SD of T 0.0119. Targets: D 0.1: {"rho": 0.1783805206865072, "n_sim": 1000, "n_perm": 500, "p_fires": 0.427, "p_detect": 1.0, "mean_T": 0.098065821476823, D 0.15: {"rho": 0.2682328251153231, "n_sim": 1000, "n_perm": 500, "p_fires": 1.0, "p_detect": 1.0, "mean_T": 0.14781087651518934, D 0.2: {"rho": 0.35780547626316556, "n_sim": 1000, "n_perm": 500, "p_fires": 1.0, "p_detect": 1.0, "mean_T": 0.1980794636052456. min_detectable_T 0.0269. No degenerate rung; rungs_simulated = the nine.
- **block_sd_A** (dial h; n_sim 200, calibrated ρ 0.2512): mean block SD **0.0069 at D = .15 / 0.0067 null** (2l .0070/.0068, 2m .0070/.0068 — the third reading of the same scatter); the four 64-draw blocks' mean T at declare [0.0973, 0.0959, 0.0954, 0.0958] — ≈ .096, so a k = 64 reading of a D = .15 effect lands just BELOW the bar on average, as on 13B and SmolLM3.
- **delta_sd** (dial h, the annotation C's resolution; n_sim 200, n_boot 200): delta_null_sd **0.0143**, at declare A 0.0134 / B 0.0145; delta_boot_sd_null **0.0124**; **min_detectable_delta 0.0325** (`min_detectable_delta = 2.63 * delta_boot_sd_null (normal approximation: CI95 excludes zero with power .75)`) — 2m's +.0659 increment sits ≈ 2× above the minimum detectable Δ, so `covers_3b_increment` is a live question, not a foregone one. k_by_rung (the first-block thinning densities): {'add3_mid': 27, 'add_base8': 28, 'antonym': 64, 'antonym6': 64, 'arith_next': 37, 'odd6': 64, 'sub3_mid': 64, 'sub4_mid': 64, 'sub_base8': 45}. `delta_sd.rungs` = the nine = R_PRIMARY (the R-6/F-2 WIDER disclosure fires only if a test drops a rung at analysis).
- predictor_sha256 95cec11f77a7b521…; primary_is_the_nine true; the calibration and shape notes verbatim on the record.

Endpoint watcher stopped by PID after the record's commit. Next: tag `exp2n-endpoint-sealed` at HEAD → read sweep + cold battery → projection → the sweep (authorized 16:2x: 'Go on the sweep.').

## Seal + projection — 2026-09-07 17:47

Tag `exp2n-endpoint-sealed` cut at 024b7e30 (annotated object fde3c52c) after the power record's commit; `require_endpoint_seal_2n` binds; master and the tag pushed. Post-seal cold tools (2i's lesson — run after each stage lands): `tests/read_sweep_2n.py` → INSUFFICIENT_DATA (gate 1 / sweep absent), no T, `write=False`, bucket (e) unpinned = 0, bucket (f) seal-bound-absent = 104; `verify_referents_2n.py` 14/14 (item 10 reads endpoint / rung set / power present, sweep absent — pre-campaign; item 13 loads S8's five committed outcomes; item 14 reproduces S9's literals). Projection SEALED at `projection.md` before gate 1 or any intermediate Comma checkpoint loads — SHARED, T_A ≈ .15 [.10, .20], T_B ≈ .18 [.11, .25], C = B-LEADS at Δ_C ≈ +.04 [−.01, +.09] (covers +.0659 a coin flip), the two accounts each a claim with its own disconfirmer, per-rung by type, S8c ≈ −.05, S9 antonym A ≈ +.02 / B ≈ +.12. Sweep launch follows on Michael's word of 16:2x ('Go on the sweep.').

## 2026-09-07 — SWEEP LAUNCHED 17:48:21 (pid 60719; watcher `--stage sweep` pid 60720) on Michael's word ('Go on the sweep.', 16:2x)

Dry run first: the refusal chain passes (prereg tag bound, both predictor seals, the endpoint seal at 024b7e30), dtype float16, gate 1 pending, 25 units — gate 1 (the stage-1 endpoint step 460,000 re-derived through the candidate-file loader against the thin-loader records), the seeded twin, then the 23 remaining grid points ascending (10k, 20k, then every 20k to 440k). Launched via `Popen(start_new_session=True)` with `PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1`, log `sweep.log`; the watcher commits and pushes every record after its size stops changing. ≈ 82 min per point at fp16 plus the 14 GB download each, ≈ 35 h. Health checks twice hourly (records counted, HALTED absent, gate 1 PASS, watcher alive); an environment-side kill with a clean tree is relaunched the same way; an experiment-side HALTED marker waits for Michael's ruling. The analyzer runs ONCE, detached, on his go.

## GATE 1 PASS — 2026-09-07 ≈ 19:05 (the stage-1 endpoint through the candidate-file loader against the thin-loader records)

34 rungs, `continuations_compared` 500 on every rung (17,000 continuations), **0 bit diffs, 0 continuation diffs**, tensor digest and commit equal on both sides. The first byte-identical reproduction on Comma v0.1-1T and the twelfth consecutive on this stack — and the first across two generation-config paths that dial o forces to agree (the thin loader takes the branch's file, the candidate-file loader stages the shards plus the pinned `config.json`; both set the stop id to 3 and gate 1 measures the agreement). `gate1.json` + the 34 `step460000` records watcher-committed. The seeded twin followed (0/500 on every rung so far). The projection (f1fc3370) was sealed before this record existed.

## 2026-09-08 ≈ 20:31 — SWEEP COMPLETE

Launched 2026-09-07 17:48:21, "comma_7b: complete" at ≈ 20:31 the next day: 26.7 h wall, 24 units (gate 1 + the seeded twin + 23 grid points) at 3,760–3,891 s each (mean 3,847 s; 25.65 h of model time). 876 files — `gate1.json` plus 25 directories of 34 rung records and a `_checkpoint.json` — every one watcher-committed and pushed as it landed; the tree is clean and master equals origin. **Zero experiment-side stops, zero halts, zero environment-side kills of the sweep** (a harness-tracked poller was reaped under memory pressure at 19:2x; the sweep, in its own session, was untouched). The seeded twin verifies 1 item in 17,000. Descriptive only, no predictor read against any outcome: at step 440,000 the nine stand at add3_mid 481, add_base8 118, antonym 308, antonym6 297, arith_next 440, odd6 118, sub3_mid 499, sub4_mid 403, sub_base8 195 against the endpoint's 490 / 118 / 327 / 327 / 491 / 127 / 500 / 407 / 306; sub_base8 is non-monotone through the cosine tail (265 at 240k, 309 at 380k, 207 at 420k, 195 at 440k, 306 at 460k).

Post-sweep cold tool: `verify_referents_2n.py` only (it computes no functional-vs-label statistic by construction). `tests/read_sweep_2n.py` is deliberately NOT run on the complete tree — it executes the analyzer at n_perm 30 and would print a T ahead of the single sanctioned run (2j's disclosure lesson). Sweep watcher stopped by PID; the health-check cron deleted. **Next, on Michael's go only: the analyzer ONCE, detached (`--write`), then `exp2n-closed`, the retrospective against projection f1fc3370, and close-out propagation.**
