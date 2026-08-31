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
neither is a gap, but they are zero for different reasons and only two
of the four `sha_pin_at_load` candidates are pinned elsewhere. Checked
directly (not assumed): `checkpoints_2i.json` and `checkpoints_2l.json`
ARE members of `referents_2l.json`'s own manifest on this tree
(`make_referents_2l.referent_files` lists `bi.CHECKPOINTS_PATH` via
2k's referent chain and `bl.CHECKPOINTS_PATH` directly), so
`_classify`'s manifest branch claims their one read each first — doubly
pinned. `checkpoints_2g.json` and `checkpoints_2h.json` are NOT in the
manifest, and are in no other bucket either (not `FROZEN_SHA256_2L`,
not `FROZEN_IMPORT_SHA256_2G`, not any `IMPORTED_SHA256_*`, not
`INSTRUMENT_BLOBS_2L`) — confirmed by instrumenting the sweep and
counting read attempts by filename: zero for both. The real reason
those two read 0 is that `analyze_2l.run()` never reads 2g's or 2h's
checkpoint manifests on this tree at all; the `SHA_PIN_AT_LOAD` set
carries them as entries inherited from 2k's own sweep bucket, unread
rather than shadowed. An unread file cannot be an unpinned read, so (e)
is still genuinely 0 — but a later code path that DOES start reading
them would need its own pin, not free coverage from this bucket.
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

## Task 6: the adversarial freeze

Fresh-eyes attack on the frozen instrument at `68fb7ed9`, against the
brief's eighteen-item attack list. Zero model contact, zero network. The
full disposition of every item, with its demonstration, and the
ratification package (findings table, dials confirmed untouched, doc
slips (a)–(g) as exact §-level wording) are in
`experiments/exp2l/FREEZE_CHECKLIST.md`.

**THE CLASS DEFECT — one that would silently decide the TERMINAL — was
NOT found.** Five findings and one hygiene item were, each demonstrated
executably before closure and each closed additively (a new refusal, pin,
test or disclosure). No accepted dial was touched; the design doc was not
edited.

### Findings

- **F-4 (the most consequential): the THIN guard counted `|R_PRIMARY|`,
  not the rungs a test actually read.** `cells_for` drops any rung with
  fewer than `ELIGIBILITY_MIN_POS = 20` positive-outcome items and
  `_run_test` drops any rung whose predictor is constant inside every
  stratum; neither appeared in the reason or the licence. Reachable, and
  measured: the smallest endpoint count that puts each of 2k's nine into
  R_PRIMARY is 9 (add3_mid), 9 (sub4_mid), 15 (sub3_mid), 19
  (arith_next) — all below 20 — while y includes the endpoint step, so
  n_pos is bounded BELOW by that count. Demonstrated on new world W19:
  R_PRIMARY of four rungs (so the frozen guard is silent), three of them
  capped below 20 firing items, **verdict SHARED at T = .7052,
  p = .004975, on ONE eligible rung**, carrying §6's full cross-family
  licence with no caveat. It decides not the terminal but the LICENCE.
  Closed with a per-test disclosure on the reason and the licence naming
  what was read and what was dropped; `fires` untouched.
- **F-1 (2j F-1's lineage, one call site over): the import pin's "(exit)"
  check ran BEFORE the thirteen secondaries.** Demonstrated by importing
  an unpinned `experiments/` module inside S1: verdict SHARED, zero
  failures, and `check_imports_2l()` raised only when called afterwards
  by hand. Closed with a post-secondaries re-check that delivers the
  frozen refusal terminal. Stated plainly: not reachable through the real
  producer — no secondary imports anything new — so this is a pin made
  total, not a bug fixed.
- **F-2 (2i F-1's shape one record type over, with 3d F-2's coverage
  rule): the sweep's checkpoint record was attested, never measured, and
  its sha table covered an unstated subset.** Its `revision`, `commit`
  and `digest` (the only quantity tying the step's 34 item records to the
  checkpoint the record claims was loaded) were never compared, and the
  sha table was checked over 12 of the **13** candidate files the loader
  stages. All three measured now. Disclosed rather than closed: the 13th,
  `model.safetensors.index.json`, carries no LFS sha in the Hub metadata,
  so it is pinned by the revision commit alone (doc slip (g)).
- **F-3 (2i F-1 / 2j F-2): `rung_set_2l.json`'s `endpoint_file_sha256`
  was required present, published in the verdict's referents, and
  compared to nothing** (the world fixtures wrote `{}` and all seventeen
  worlds passed). Measured now against the 68 endpoint records on disk.
- **F-5 (2i F-1 / 2k F-2, on the power record's own top level): its
  `r_primary`, `primary_is_the_nine` and the shape of `block_sd_A` were
  attested and compared to nothing** — and dial f grades the projection
  against `block_sd_A`. All measured now, including the rung set the SD
  was taken over, re-derived as Test A's non-degenerate keep. The
  producer→analyzer round trip in `test_power_2l.py` passes unchanged.
- **D-1: the campaign logs were not gitignored** (2g and 2i ignore
  theirs); closed with a named list, so the committed `mutation_*.log`
  record stays tracked.

### What was attacked and cleared

Ten enumerated kill shapes built from a real world (endpoint killed
mid-`which`, sweep killed mid-step, `run_gate1` killed before
`gate1.json`, power over a different rung set, an endpoint record edited
after the sweep stamped its sha, `gate1.json` with attested diffs and no
marker, rung set deleted, a whole grid step missing, step 0 missing) —
every one INSUFFICIENT_DATA, control still SHARED. The tag binding
against **real git** in a real temp repository with a real annotated tag
(a post-tag byte appended to `run/sweep_2l.py` is refused). The composite
predictor sha's chain, link by link, each a check. One character changed
in one seed-0 draw of a **copy** of 2k's tier (the real tree untouched)
fires `load_tier_2k`'s gate 1; one flipped byte mid-gzip is collected.
`t_only` and `_run_test` agree on T bit for bit on all four of 2k's real
64-draw blocks. 2g's committed strata **re-derive identically** from the
sha-pinned item files, so the item index shared by strata, x_A, x_B and y
is anchored by three pins rather than by convention. Determinism
byte-identical across two processes and two roots.

### Disclosure for the projection (computable now, before any 13B weight)

Test B's median-bucket split of x_A^(256) at 1b: **no rung's bucket is
empty**; bucket-1 sizes run 30 (sub4_mid) to 249 (sub_base8); composite
cells per rung 4–12; the smallest cell is a singleton on `sub4_mid`
(dropped by `precompute`, not counted). Test A's degeneracy set on
x_A^(256) is empty, so §3.6's note holds. Ties fall in bucket 0
(`_median_bucket` is strict `>`).

### Cold re-runs after every closure

| run | result |
|---|---|
| full suite, all six modules, no marker filter, no `-k` | **136 passed in 956.81s** (was 124 at `68fb7ed9`; +12 freeze tests) |
| worlds | **19/19** — W1–W17 plus W18 (extra rungs, undefined D, strict-JSON write path) and W19 (F-4) |
| totality | **28/28** |
| cold battery `verify_referents_2l` | **12/12** |
| read sweep | INSUFFICIENT_DATA, 4,437 distinct paths, **UNPINNED 0**, writes 0 |
| determinism ×2, separate processes, two roots | `39b20b2b2ec4682e7afa6c6f7bf12dfb0db28f9770b359ba107b783be7aa8ba1` both — byte-identical |
| mutation, fast (`mutation_freeze_fast.log`) | 109/125 killed, 16 survivors, 0 SKIP |
| mutation, totality (`mutation_freeze_totality.log`) | 14/14 killed |
| mutation, full shape (`mutation_freeze_fullshape.log`) | 2/2 killed |
| **mutation total** | **125/125 killed, 0 survivors, 0 equivalence claims** |

The three rounds were re-run in full against the CURRENT bytes rather
than inherited from Task 5, because the closures changed the instrument.
Thirteen mutants Task 5 had to close with later fixture rounds die on the
freeze's first fast pass (the real-git prereg test, the seal-binding test
and the checkpoint-record / rung-set / power tests close them). The
sixteen fast-round survivors are exactly the shapes another suite must
observe: `[63]`/`[64]` (a full-shape world alone can see Test A's
predictor or Test B's conditioning change), `[82]` (F-1's own refusal,
reachable only after the secondaries run) and the thirteen
auto-generated `collect_total` strips whose sites need a complete
synthetic 13B tree. No two runs ever concurrent; no `.mutation_backup`
left behind; the four mutated files clean in `git diff` before and after
each round.

### Instrument delta the tag will bind

Of the four blob-bound files, the freeze changed **`analyze_2l.py`
only**; `battery_2l.py`, `run/endpoint_2l.py` and `run/sweep_2l.py` are
byte-identical to `68fb7ed9`. Everything else is test-side, the cold tool
`verify_referents_2l.py` (re-pinned in `IMPORTED_SHA256_2L` the moment
the totality suite caught the drift), the checklist, this ledger, or
`.gitignore`. `referents_2l.json` needed no rebuild — neither changed
file is a member of its manifest — and still hashes to
`REFERENTS_2L_SHA256` (cold battery item 3).

### Concerns

- None blocking. Two process notes for the record: (1) the mutation
  harness's fast pass cost 5:24 per mutant because `_tree` re-read and
  re-sha'd all 34 item files for every one of the 578 records it writes;
  memoising the three pure loaders in `test_analyze_2l.py` (test-side,
  behaviour identical) took it to 2:56 and made a full 125-mutant
  re-run feasible in one session. (2) `verify_referents_2l.py` is
  pinned by `IMPORTED_SHA256_2L`, so editing the cold tool breaks every
  world until the pin is refreshed — caught immediately by the totality
  suite, but worth knowing before touching it during a campaign.
