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

## Task 4: `power_2l.py`, the worlds, totality, power tests, cold battery

Transcribed Steps 1/2/3/5 (`power_2l.py`, `tests/full_shape.py`,
`tests/test_full_shape_2l.py`, `tests/test_power_2l.py`) verbatim from
the task brief. `power_2l.py` overwrote Task 3's 9-line stub wholesale.
Wrote `tests/test_totality_2l.py` and `verify_referents_2l.py` in
2k's shape from the brief's prose spec (Steps 4/6).

### Deviation: `full_shape.py`'s `_latent` — coordinator's ruling, applied

First run of the 17-world module: W1 SHARED and W2 LINEAGE both landed
BOTH instead of their own terminal (W1: A T=.7660 p=.00498 fires=True,
B T=.1216 p=.00498 fires=True). Diagnosis (coordinator): the brief's
`_latent` modes were transcribed from 2i's own worlds, which mixed a
SYNTHETIC x_B independent of x_A by construction; 2l's worlds use the
REAL, correlated x_A^(256)/x_B (2i disclosed within-stratum rho
.06-.32), so a latent built from x_A's raw rank alone still leaks into
Test B through the correlated x_B inside x_A's own median bucket (Test
B's conditioning), and symmetrically for x_B into Test A. Fix: replace
`_latent(rng, x_a, x_b, mode)` with `_latent(rng, x_a, x_b, strata_r,
mode)`, orthogonalizing each mode's latent against the OTHER predictor
under the analyzer's OWN conditioning — `bucket_A =
an2h._median_bucket(x_a)` (exactly Test B's own composite-cell split)
for `a_only`; `resid_B` (x_b's rank with x_a's linear signal regressed
out WITHIN EACH BASE STRATUM, standardized over the rung) for
`b_only`; the sum for `both`; the negated sum for `inverted`;
`independent` unchanged. No production code (analyzer, `power_2l.py`)
or test assertion touched — only `tests/full_shape.py`'s `_latent` and
its one call site. Byte-diff against the brief: `power_2l.py`,
`test_full_shape_2l.py`, `test_power_2l.py` IDENTICAL; `full_shape.py`
differs only in this function, its new imports (`scipy.stats.
rankdata`, `experiments.exp2h.analyze_2h`) and the call site passing
`strata0[r]["strata"]`.

### W1–W5 T's (post-fix; the world's latent is synthetic — a sanity
### band, not a projection)

Standalone re-derivation (`fs.write_world_2l` + `fs.run_world`, fresh
tmp dirs, default `n_perm=200, n_boot=20`):

- **W1 SHARED**: verdict SHARED (want SHARED) — A T=.5233 p=.004975
  fires=True | B T=.0077 p=.378109 fires=False
- **W2 LINEAGE**: verdict LINEAGE (want LINEAGE) — A T=.0243 p=.019901
  fires=False | B T=.6889 p=.004975 fires=True
- **W3 BOTH**: verdict BOTH (want BOTH) — A T=.3118 p=.004975
  fires=True | B T=.7156 p=.004975 fires=True
- **W4 NEITHER independent**: verdict NEITHER (want NEITHER) — A
  T=-.0013 p=.532338 fires=False | B T=-.0042 p=.597015 fires=False
- **W5 NEITHER inverted**: verdict NEITHER (want NEITHER) — A
  T=-.2222 p=1 fires=False | B T=-.6200 p=1 fires=False

### Test run (post-fix)

- `test_power_2l.py`: 3 passed in 44.78s (unaffected by the fix — no
  `_latent` dependency).
- `verify_referents_2l`: 10/12 (items 3 and 12 SKIP, pending Task 5),
  clean, unaffected.
- `test_full_shape_2l.py` (17 worlds, background, real 2k tier + 2i
  draws at both sizes each): 6 passed in 405.52s (0:06:45).
- `test_totality_2l.py` (base world + ~22 copies, background): 22
  passed in 172.40s (0:02:52), including the SHARED control.
- Whole `experiments/exp2l` suite, no marker filter (the `slow`
  real-git rehearsal test included, first run in this session): 83
  passed in 718.84s (0:11:58); `--collect-only` confirms 83 tests
  collected, matching 83 passed exactly — zero skips.

`git status --short` after `git add experiments/exp2l`: only the six
Task 4 files (one modified, five new). Committed `914f3508`, pushed
`origin master` clean.

## Task 5: the real-tree closure

Picked up mid-Step-4 after a session restart killed the original
implementer (state supplement written by the controller, verified from
disk/git rather than trusted at face value). Steps 1–3 and roughly half
of Step 4 were already correct in the working tree; the rest below is
what this session did, distinguishing inherited-and-verified from
newly done.

### Steps 1–3 (inherited, verified, committed `8cd3c39d`)

Step 1 (`FROZEN_SHA256_2L`, 42 modules) was already committed
(`d2a356ab`). Step 2's `IMPORTED_SHA256_2L` (4 modules —
`experiments/exp2l/__init__.py`, `run/__init__.py`,
`run/preflight_2l.py`, `verify_referents_2l.py`) and Step 3's
`referents_2l.json` (2695 files, `REFERENTS_2L_SHA256 =
ae4db62b326642766418323df1abe3d188cf78eeff3c0cbe013a7e38f7b7e902`)
were inherited uncommitted; both re-verified by re-running
`tests/import_scan_2l.py` and `make_referents_2l` fresh — both
reproduced their pinned literals exactly (byte-idempotent). Committed
just the five files that make `verify_referents_2l` 12/12
(`analyze_2l.py`, `battery_2l.py`'s one-line re-pin of
`make_referents_2l.py`'s hash inside `FROZEN_SHA256_2L`,
`make_referents_2l.py`, `referents_2l.json`, `tests/import_scan_2l.py`)
— the test-file mutation-gap fixtures (Step 4, below) stayed
uncommitted for the closing commit, since splitting them out of the
same files would have needed hunk-level staging for no benefit.

### Step 4: the mutation harness — final tally 110/110 killed, 0 survivors, 0 equivalents

Inherited state (verified from the logs, not re-trusted blindly):
round 1 fast pass (`mutation_build.log`) 45/110 killed, 65 survivors
(24 semantic + 41 `collect_total`); round 2 totality pass
(`mutation_totality.log`) 18/41 of the `collect_total` survivors
killed, 23 left; round 3 fullshape pass (`mutation_fullshape.log`)
killed `[63]` cleanly before the crash, `[64]`'s verdict discarded
(the controller restored the file mid-pytest) and marked due for
re-run. Fixture closures for most of the 24 semantic + 23 totality
survivors were already written into `test_battery_2l.py` (+47),
`test_stages_2l.py` (+46), `test_totality_2l.py` (+64) and
`test_analyze_2l.py` (+271) but never re-run against them.

Re-run this session, in order:

1. **22 of the 24 semantic survivors** (`[63]`/`[64]` excluded — they
   need `--fullshape`) under FAST with the inherited fixtures:
   `mutation_semantic_rerun.log`, **22/22 killed**, no new gaps.
2. **`[36]` (the documented-equivalent candidate the brief flagged —
   `run: endpoint_sha computed BEFORE the endpoint seal binds`):
   checked the ORIGINAL fast-pass log directly — it was already
   `killed` in round 1, never a survivor at any point.** No equivalence
   proof needed; the brief's "prove or kill" framing anticipated a
   possibility that didn't materialize.
3. Attempted the 23 totality survivors under `--totality` per the
   state supplement's suggested method
   (`mutation_totality_rerun.log`, not committed — see below).
   **Wrong suite for most of them**, discovered mid-run: the
   `test_analyze_2l.py` fixtures that actually close 19 of the 23 are
   FAST-suite tests (direct `monkeypatch` unit tests on
   `load_predictors_2l`/`run()`, the harness's own "preferred" close
   route over a world-fixture detour — their docstrings say so
   explicitly), and `--totality` mode's covering suite is
   `test_totality_2l.py` alone, which never forces those specific
   exceptions. Confirmed by watching the run sit on mutant `[99]` for
   over an hour with 0% CPU between subprocess calls — legitimate
   progress, wrong destination. Killed the run and its pytest child,
   restored `analyze_2l.py` from `.mutation_backup` (byte-diff
   confirmed it matched the pre-mutation working tree exactly after
   restore), deleted the backup, re-split correctly:
   - **19 entry-side survivors** (`70,71,72,73,77,80,81,82,83,91,92,
     93,95,96,97,98,99,106,107` — all closed by `test_analyze_2l.py`'s
     `_TOTALITY_FORCED_CASES_2L`/`_RUN_FORCED_CASES_2L` parametrized
     tests and five dedicated ones) under **FAST**:
     `mutation_entry_fast_rerun.log`, **19/19 killed**.
   - **4 genuine totality-only survivors** (`100,104,108,110` — closed
     by four new `test_totality_2l.py` world-based forced-exception
     tests, reachable only once `core` has computed on a synthetic
     13B tree) under **`--totality`**: `mutation_totality_final.log`,
     **4/4 killed**.
4. **`[64]`** under `--fullshape --only 64`: `mutation_fullshape_64.log`,
   **1/1 killed**; `[63]`'s pre-crash verdict stands unchanged.

**New gap found and closed (not inherited): `[67]`/`[68]` had no FAST-
reachable coverage at all.** The assertions that would catch a sign
flip in `s4_matched_2l`'s `increment` and a literal flip in
`s5_answer_prior_2l`'s `non_gating` live in
`test_s4_matched_2l_uses_2k_rule_and_2j_blocks` /
`test_s5_answer_prior_2l_is_2j_functional_on_2i_rows` — both correct,
both pre-existing — but both are excluded from FAST by the covering-
suite ruling's own `-k "not test_s4 and not test_s5"` (they load real
2i draws / real 2k counts, ~95 s together) and neither `--totality` nor
`--fullshape` observes either value (confirmed by grep: `"increment"`
appears nowhere outside that one deselected assertion;
`test_full_shape_2l.py` checks `non_gating is True` but only inside
`test_w1_shared_shape`, which `--fullshape --only 64` doesn't run and
which `[68]` was never targeted against). So `[67]`/`[68]` genuinely
had zero coverage under the three declared suites, independent of
whatever residual doubt the 22/19/4/1 re-runs settled. Closed with two
new FAST tests in `test_analyze_2l.py`,
`test_matched_density_increment_is_thinned_minus_a256` and
`test_answer_prior_non_gating_is_a_hardcoded_literal` — named without
the `test_s4`/`test_s5` substrings so the `-k` deselection can't sweep
them up too — built on hand-synthesized `bits_b`/`x_a64` (for `[67]`)
and stubbed `fn.wrong_target_propensity`/`an._run_test` (for `[68]`)
rather than the real 2i/2k trees, so both run in milliseconds
(prototyped standalone first: 3 ms and ~3 μs respectively) and are
reachable from the existing FAST invocation with no suite change.
Verified (not just written): the full FAST baseline re-run after
adding them still passes, and the full unfiltered suite (below) passes
124/124 including both.

`mutation_totality_rerun.log` (the wrong-suite attempt, never reached a
summary line, "SURVIVED" labels stale by definition) was deleted
rather than committed — it doesn't represent a completed round and
would misdescribe the historical record.

**Final: 110/110 killed across all rounds combined (45 + 18 + 1[`63`]
+ 22 + 19 + 4 + 1[`64`] + the two newly-covered = accounted for
without double-counting — every one of the original 65 fast-pass
survivors now traced to a kill). Zero survivors. Zero equivalence
claims.**

### Step 5: the read sweep — clean, (e) unpinned = 0

`tests/read_sweep_2l.py` run once on the real pre-campaign tree
(`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp2l.tests.read_sweep_2l`, exit 0): verdict
`INSUFFICIENT_DATA` (9 referent/loader failures, all the expected
missing-13B-record/tag reasons), 4437 distinct paths opened for
reading (6757 total open/read calls), 0 writes.

```
referents_2l.json               2696
frozen_module                     54
instrument_blob                    4
sha_pin_at_load                    0
seal_bound_campaign_absent         0
python_stdlib_venv              1683
UNPINNED                           0
```

`sha_pin_at_load` and `seal_bound_campaign_absent` both read 0 —
neither is a gap. `sha_pin_at_load`'s four candidate files
(`checkpoints_2g.json`/`checkpoints_2h.json`/`checkpoints_2i.json`/
`checkpoints_2l.json`) are all ALSO already members of
`referents_2l.json`'s own manifest on this tree (2k's referent list
inherits 2g's/2h's, and `make_referents_2l.referent_files` lists
`bl.CHECKPOINTS_PATH` directly), so `_classify`'s manifest check
claims them first — doubly pinned, not unpinned.
`seal_bound_campaign_absent` is 0 because every campaign-side loader
on the real pre-campaign tree fails via a bare `Path.is_file()` guard
(`_load_rung_set_2l` and its siblings) BEFORE ever calling
`read_text`/`open` — `Path.is_file` isn't one of the five wrapped
calls, so a guard-refusal is never an attempted-and-failed read;
confirmed by reading `_load_rung_set_2l`'s body directly. Matches the
script's own docstring ("attempted-but-failed opens the wrapper still
records" — there are none here because nothing was attempted) and the
design's disclosure: bucket (f) resolves to real numbers only after
`exp2l-endpoint-sealed` exists (process tail, not this task).

Design doc §2 disclosure (both sentences now literally true — the
second was premature in the inherited working tree since the read
sweep hadn't run yet; it has now): Task 5 ran `analyze_2l.run()` on the
real pre-campaign tree twice before any tag (the import scan and the
read sweep), both `INSUFFICIENT_DATA`, no T, both exercising 2k's and
2i's real closed predictor stages cleanly first.

### Manifest re-pin check — unchanged

Re-ran `make_referents_2l` after every edit settled (Step 4's new
tests touch only `experiments/exp2l/tests/*`, which
`referent_files()` never lists — it covers 2k's post-campaign referent
list plus a handful of 2l's own data files, not 2l's own python
source or its tests): sha
`ae4db62b326642766418323df1abe3d188cf78eeff3c0cbe013a7e38f7b7e902`,
byte-identical to the committed pin. No re-pin needed.

### Cold battery — 12/12

`verify_referents_2l`: 12/12, all items `ok` (items 3 and 12 — the two
that were `SKIP` at the end of Task 4 — now live and passing).

### Test run

Full `experiments/exp2l` suite, every test file, no marker filter and
no `-k` exclusion (`test_battery_2l.py test_stages_2l.py
test_analyze_2l.py test_totality_2l.py test_full_shape_2l.py
test_power_2l.py`): **124 passed in 908.30s (0:15:08)** — up from
Task 4's 83 (41 new: the two `[67]`/`[68]` closures plus the Task-5
mutation-gap fixtures already counted at Task 4 time are folded in
here for the first time under the real pins, since Task 4's 83-test
run predates Step 2's bypass-drop).

### Self-review findings

- `.mutation_backup` and stray logs: confirmed none remain
  (`find experiments/exp2l -name "*.mutation_backup"` empty) before
  every run and before the closing commit.
- The wrong-suite totality attempt (item 3 above) cost real time but
  left no residue: the restored file byte-diffed clean against the
  working tree's Step-1-pinned state before any further run.
- `mutation_totality_rerun.log` and an ad-hoc `full_suite_check.log`
  (a personal sanity re-run, not a brief deliverable) deleted rather
  than committed.
- Checked `git diff` on every touched production file
  (`analyze_2l.py`, `battery_2l.py`, `make_referents_2l.py`) against
  what Steps 1–3 were supposed to produce before staging; only the pin
  literals and the one hash re-pin are present, no incidental changes.

### Concerns

- None blocking. The one process note worth carrying forward: the
  state supplement's suggested re-run method (`--totality` for all 23
  collect_total survivors) didn't match where the fixtures actually
  landed; a future ledger for a sibling experiment should record WHICH
  suite closes each survivor at fixture-writing time, not just that a
  fixture was written, so a resuming session doesn't have to
  re-derive it from docstrings and a stuck process.

Committed `8cd3c39d` (Steps 2+3) and the closing commit below (Steps
4–6), pushed `origin master` after each.
