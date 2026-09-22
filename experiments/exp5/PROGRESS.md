# Experiment 5 — ledger

## Task 1 (2026-09-22): `_threads_5.py` + `battery_5.py`

Built: thread pinning (`_threads_5.py`, exp4's shape); the battery module
(`battery_5.py`) — constants and pins (sizes/pairs, spine, bars,
tolerances, LR schedule, rung types, slice pins), the seven-size Hub
inventory reader/builder under 2g's candidate-file rule
(`refresh_inventory_5`/`load_inventory_5`/`build_manifest_5`/
`build_all_5`/`write_manifest_5`/`load_manifest_5`), the available list
and nine-point spine with substitution (`available_5`/`spine_5`/
`spine_substitutions_5`), floors/bar (`load_floors_5`/`clears_5`), the
Mac's committed referents (`mac_final_counts_5`/`mac_interior_counts_5`/
`gate1_interior_steps_5`/`tolerance_failures_5`), the LR-at-step /
tokens-seen functions, every unit path helper, the record-contract
checkers (checkpoint/loss/rung/unit/host), and the two tag bindings
(`require_prereg_5`, `require_targets_seal_5`). `FROZEN_SHA256_5` stays
`None` — Task 6's pin. Tests: `experiments/exp5/tests/test_battery_5.py`
(15 cases incl. one `slow` case against the real committed manifest).

**Deviation from the brief's Step 3 listing, found by TDD (RED before
GREEN), disclosed:** the brief's literal `mac_final_counts_5` routed
every `"2c"`-sourced size (2.8b, 12b) through
`bg.load_m4_counts(size, rungs=RUNGS)` — the full 34-rung request. This
KeyErrors on 12b: `bg.FINAL_COUNT_PIN["12b"]` pins only the 11 rungs
2g's own predictor needed (2.8b's pin covers all 34), while the m4 JSON
records exist on disk for all 34 rungs at both sizes
(`experiments/exp2c/results/m4/12b_trained/*.json`, 34 files, verified).
The docstring's own contract ("all 34 rungs") and the test
(`test_mac_referents_exist_for_five_sizes_and_none_for_two`, which
requires `set(c) == set(bt.RUNGS)` for 12b) settle the intent. Fix:
`_m4_2c_counts(size)` reads `bg.m4_path(size, r)` directly for all 34
`RUNGS`, re-asserting against `bg.FINAL_COUNT_PIN.get(size, {})` only
where the pin carries that rung (a partial check for 12b, the full
34-rung check for 2.8b — behaviourally identical to the brief's code on
2.8b, corrected on 12b). No other brief code changed.

## Inventory refresh (2026-09-22, NETWORK — Hub metadata only; disclosure per resolution 1)

Run: `python -m experiments.exp5.battery_5 --refresh`, ~14:05–14:07 ET
(the seven repos' `list_repo_refs` + `model_info(files_metadata=True)`
scan, 7 × 155 + 7 ≈ 1,092 API calls). No weights downloaded, no
authentication. Output committed: `hub_inventory_5.json` (raw Hub
metadata), `checkpoints_5.json` (the built manifest,
sha256 `82658028d203a65108effe84eb7446bc046067c4f7373f6c584b159125d4b306`).

Every size carries **155 revisions** (`step0`…`step143000` every 1000,
+ `main`; `n_revisions` 155 for all seven, `ignored_revisions` empty —
no non-`step*` branch besides `main` on any repo).

Per-size available count, excluded steps (with reason), and the spine:

- **160m**: 153 available; **no exclusions**; spine unchanged
  `(1000, 2000, 4000, 8000, 16000, 32000, 64000, 100000, 143000)`; Hub
  `step143000` signature equals `main`: True; `stale_main_copies`
  `{model.safetensors: 0, pytorch_model.bin: 1}` (the final's own `.bin`
  reads as a copy of `main`'s `.safetensors` sha slot — expected, no
  candidate confusion since `.safetensors` wins the candidate rule).
- **410m**: 153 available; **no exclusions**; spine unchanged; Hub
  `step143000` == `main`: True; `stale_main_copies` `{0, 1}` (same
  pattern as 160m).
- **1b**: 152 available; **excluded: `step1`** — reason "candidate
  files duplicate another revision's" (duplicates `["step0"]`; `step0`
  and `step1` carry byte-identical `model.safetensors`, sha
  `206bd095bd17ac1826c0d48965a86cb265150114443caf0771821e5d1993b6e7`).
  Spine unchanged (1 is not a spine point). Hub `step143000` == `main`:
  True; `stale_main_copies` `{0, 1}`.
- **1.4b**: 153 available; **no exclusions**; spine unchanged; Hub
  `step143000` == `main`: True; `stale_main_copies` `{0, 1}`.
- **2.8b**: 141 available; **12 exclusions**, all "candidate files
  duplicate another revision's" — `26000` (dup. `step53000`,
  `step103000`), `53000` (dup. `step26000`, `step103000`), `54000`,
  `56000`, `57000`, `58000`, `59000`, `61000`, `62000`, `63000`, `64000`
  (these nine mutually duplicate each other AND `step143000`),
  `103000` (dup. `step26000`, `step53000`). This reproduces 2g's
  findings A/B exactly (nine branches carry `step143000`'s files, three
  carry a three-way-mutual stale set) over the FULL 1000-step grid 2g
  never scanned in full. Spine **substituted**: `64000` → `65000`
  (`spine_substitutions_5` = `{"64000": 65000}`), matching the design
  doc's stated 2.8b substitution exactly. Hub `step143000` == `main`:
  **False** (2g finding C: `step143000`'s `model.safetensors`,
  462f2b96…, is a different serialization from `main`'s pinned commit,
  ab496f1c…/2a259cdd…; the final grid point is `main`, never the Hub's
  `step143000` branch — `hub_step143000.duplicates` lists all nine
  stale steps against it independently). `stale_main_copies`
  `{model.safetensors: 76, pytorch_model.bin: 39}` (2.8b's branches
  widely carry `main`'s file as a stale copy beside their own shards —
  disclosed, not gating; the candidate rule ignores it because shards
  win first).
- **6.9b**: 153 available; **no exclusions** (matches
  `battery_2h.py`'s docstring: "6.9b's Hub branch layout is clean...
  zero stale-main copies"). Spine unchanged; Hub `step143000` == `main`:
  True; `stale_main_copies` `{0, 0}`.
- **12b**: 152 available; **excluded: `step58000`** — reason
  "candidate files duplicate another revision's" (duplicates
  `["step143000"]`; `step58000`'s three `.bin` shards are byte-identical
  to the final's). Spine unchanged (58000 is not a spine point). Hub
  `step143000` == `main`: True (`hub_step143000.duplicates` lists
  `step58000` against it); `stale_main_copies` `{0, 0}`.

Every excluded revision, `step0`, and `hub_step143000`'s record are
readable in full in `checkpoints_5.json`; the counts and reasons above
were read from that committed file, not retyped by hand.

## Cross-check against the closed manifests (2026-09-22)

Ran the brief's Step-5 script with one adaptation, disclosed: the
script's loop does `m5[size]["entries"][step]` for every step key in
the old (2g/2h) manifest's `entries`, including `"0"`. `battery_5`'s
`build_manifest_5` deliberately does NOT carry step 0 in `entries`
(design: "Step 0 is never in a window"; `entries` holds trained steps
only, step 0 lives in the separate `step0` field) — this is the tested
contract (`test_manifest_available_list_excludes_step0_duplicates_and_no_candidate`
asserts `"0" not in m["entries"]`), so the brief's script KeyErrors on
`"0"` against `m5[size]["entries"]` before comparing anything. This is
a shape mismatch between the ad hoc cross-check script and Task 1's
(brief-specified, test-verified) manifest layout, **not** evidence of a
Hub rewrite. Adaptation: compare step `"0"` against `m5[size]["step0"]`
instead of `m5[size]["entries"]["0"]`; every other step compared exactly
as the brief's script does. Result — all three lines printed, all
assertions held (every closed grid entry's LFS sha is byte-identical to
what the fresh Hub scan just read, at every step 2g/2h ever loaded,
including step 0):

```
2.8b every closed grid entry's LFS shas unchanged on the Hub: 22
12b every closed grid entry's LFS shas unchanged on the Hub: 8
6.9b every closed grid entry's LFS shas unchanged on the Hub: 23
```

No Hub rewrite. No BLOCKED condition.

## B-10 disclosure (plan session, 2026-09-22)

Disclosure (plan session, 2026-09-22): a second Hub metadata read —
`dataset_info('monology/pile-uncopyrighted', files_metadata=True)`
(revision 3be90335…, val.jsonl.zst LFS sha db5e5d15…) and `model_info`
for the seven sizes (the main commits pinned as MAIN_SHA_5). No weights,
no files.

## Task 2 (2026-09-22): `slice_5.py` — the loss slice + the batched slice loss

Built: the zstd-streamed document reader (`iter_documents_5`), the
tokenizer pin check (`tokenizer_pins_5` — no specials added on a plain
render, eos id == PAD_ID_5) and the cross-size `tokenizer.json` sha
reader (`tokenizer_json_shas_5`), the exact-fill slice builder
(`build_slice_5` — accumulate documents in file order, skip < 64
tokens, truncate at 2048, truncate the crossing document to land
EXACTLY at `n_scored`, refuse if the file runs out first), the
byte-deterministic npz writer/loader with sha pinning
(`write_slice_5`/`load_slice_5`/`slice_equal_5`), the right-padded
batcher (`slice_batches_5`), the pure loss aggregation
(`loss_from_per_doc_5`, unit-tested without torch) and the MODEL-CONTACT
batched fp16-logits→fp32-log-softmax slice loss (`slice_loss_5`).
Tests: `experiments/exp5/tests/test_slice_5.py` (8 cases incl. one
`slow` case against the real committed `slice_5.npz`). TDD: RED
(`ModuleNotFoundError`-equivalent `ImportError: cannot import name
'slice_5'`) before `slice_5.py` existed; 7 fast tests GREEN immediately
after; 8/8 GREEN after the build + pins. No deviation from the brief's
Step 3 code — written verbatim (the brief's own unused `import hashlib`
kept as given; noted in self-review, harmless, no lint gate in this
repo).

**zstandard**: `~/emergence-lab/.venv/bin/python -m pip install
zstandard` → `Successfully installed zstandard-0.25.0`.

**Step 5 build — NETWORK, three parts, disclosed (resolution 2), run
2026-09-22 14:23:56–14:24:19 ET (~23 s, fast connection):**

1. The Pile-validation file: `hf_hub_download('monology/pile-uncopyrighted',
   'val.jsonl.zst', repo_type='dataset', revision=3be90335…)` into
   `~/emergence-lab/pile_val_5/datasets--monology--pile-uncopyrighted/`.
   Landed blob `338,045,152` bytes, sha256
   `db5e5d1532bf8dc33a6589b50ecba1a8c96f7b4b9cb343d168e603c393007c26` —
   both exactly the pins (`SLICE_FILE_SIZE_5`/`SLICE_FILE_SHA256_5`).
2. The 2.8b tokenizer via `models.load_tokenizer("2.8b")`: re-downloaded
   into the default HF cache (`~/.cache/huggingface/hub/models--EleutherAI--pythia-2.8b/`,
   entry absent since the 2026-09-18 cache clear) —
   `tokenizer_config.json` (99 B), `special_tokens_map.json` (396 B),
   `config.json` (571 B), `tokenizer.json` (2,113,710 B); confirmed no
   `.safetensors`/`.bin` blob present anywhere under that cache entry
   (only the four small config/tokenizer files) — no weight file was
   downloaded.
3. Seven `tokenizer.json` files (one per size, at each size's pinned
   `MAIN_SHA_5` commit) into `~/emergence-lab/pile_val_5/tokenizers/`:
   each `2,113,710` bytes, **all seven sha256 to the same value**
   `c24618a1b3e6a38167beff1c72cffd126c3a66254347304b50547d12c5f25624`
   — no BLOCKED condition (the design's one-tokenizer assumption holds).

**The three printed build lines, verbatim:**

```
tokenizer.json sha256 (all seven sizes): c24618a1b3e6a38167beff1c72cffd126c3a66254347304b50547d12c5f25624
slice meta: {"last_doc_truncated": {"doc_index": 2964, "from": 960, "to": 482}, "max_tokens": 2048, "min_tokens": 64, "n_docs": 2965, "n_read": 3063, "n_scored": 2097152, "n_skipped": 98, "source": {"dataset": "monology/pile-uncopyrighted", "file": "val.jsonl.zst", "revision": "3be90335b66f24456a5d6659d9c8d208c0357119", "sha256": "db5e5d1532bf8dc33a6589b50ecba1a8c96f7b4b9cb343d168e603c393007c26"}, "tokenizer": {"adds_specials": false, "eos_id": 0, "pad_id": 0, "revision": "2a259cdd96a4beb1cdf467512e3904197345f6a9", "size": "2.8b"}}
slice_5.npz sha256: dc48ebd4913309514a30c1acb6e3bbb399ef1b289c51c88758f4db994222c50b (3.1 MB)
```

Pinned in `battery_5.py`: `TOKENIZER_JSON_SHA256_5 =
"c24618a1b3e6a38167beff1c72cffd126c3a66254347304b50547d12c5f25624"`,
`SLICE_SHA256_5 =
"dc48ebd4913309514a30c1acb6e3bbb399ef1b289c51c88758f4db994222c50b"`,
`SLICE_META_PIN_5 = {"n_docs": 2965, "n_read": 3063, "n_skipped": 98,
"n_scored": 2097152, "last_doc_truncated": {"doc_index": 2964, "from":
960, "to": 482}}`.

**Byte-identity re-run**: re-ran `slice_file_path_5` →
`load_slice_tokenizer_5` → `tokenizer_pins_5` → `build_slice_5` →
`write_slice_5` a second time into a scratch path
(`.../scratchpad/slice_again.npz`); `cmp` against the committed
`experiments/exp5/slice_5.npz` reported no differences — byte-identical
(both 3,107,254 bytes). `slice_5.npz` is committed at 3.1 MB.

Full test file: `PYTHONDONTWRITEBYTECODE=1
~/emergence-lab/.venv/bin/python -m pytest
experiments/exp5/tests/test_slice_5.py -p no:cacheprovider -q` → `8
passed`. Full exp5 suite (battery_5 + slice_5 together): `23 passed`, no
warnings under `-W error::DeprecationWarning`.

## Task 3: `search_5.py` + `stats_5.py`

Built the total deterministic matching search (`search_5.plan_5` /
`bisect_step_5` / `replay_5` / `requested_steps_5`) and the statistics
(`stats_5.reads_5` / `cell_5` / `cells_5` / `analysed_5` /
`sign_flip_p_5` / `primary_5` / `modifier_5` / `signed_offset_ci_5` /
`ledger_5` / `tree_5` / `s4_size_ratio_5` / `s5_by_type_5` /
`s7_by_pair_5`), transcribed byte-for-byte from the task-3 brief
(including each file's leading `# experiments/exp5/…py` comment line,
per the brief's resolution note). TDD: wrote the two test files first
(RED — `ModuleNotFoundError`/`ImportError` on `search_5`/`stats_5`),
then the two implementation files, then GREEN.

**Two disclosed test-fixture fixes** (brief's own code vs. brief's own
tests genuinely disagreed on a byte-exact transcription; both traced to
arithmetic/construction mistakes in the test fixtures, not to the
implementation, and both fixed in the test file only):

1. `test_search_5.py::test_replay_lists_the_whole_request_sequence` —
   asserted `count("window") == 4`. Traced the actual bisection path for
   `target=_curve(50500)` (also used by the passing
   `test_plan_bisects_to_an_adjacent_bracket_and_names_the_window`):
   bisection visits 48000, 56000, 52000, 50000, 51000, and 48000/52000
   coincide with the window's `b_minus[0]`/`b_plus[0]`. `plan_5` never
   re-requests a step whose loss is already known (the module docstring:
   "a unit is written once"), so only 2 of the 4 window steps are fresh
   `"window"` requests. Fixed the assertion to `== 2` with a comment.
2. `test_stats_5.py::test_modifier` — the alternating (MIXED-seeking)
   sub-case held `b_minus`/`b_plus` constant at `(139,141)`/`(140,143)`
   while `lo`/`hi` alternated between the small-ahead and large-ahead
   regimes, unlike the two prior sub-cases in the same test which match
   `b_minus`/`b_plus` to each regime's own `lo`/`hi`. The mismatch makes
   `P` large for the small-ahead half, so `R_gt_P` excludes them and only
   5 (all-positive) cells survive → THIN, not MIXED. Alternated
   `b_minus`/`b_plus` together with `lo`/`hi` (matching the established
   pattern); reproduces MIXED (10 cells, 5/5, p=1.0) and THIN for the
   first 7, exactly the test's own assertions.

Verified both fixes empirically (ran `plan_5`/`replay_5` and `cell_5`/
`modifier_5` directly against the fixed fixtures before editing) rather
than adjusting numbers to make failures disappear.

Command: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
pytest experiments/exp5/tests/test_search_5.py
experiments/exp5/tests/test_stats_5.py -p no:cacheprovider -q` → `19
passed, 1 warning` (a `scipy.stats.ConstantInputWarning` in
`test_signed_offset_ci_and_secondaries_run`'s `s4_size_ratio_5` call —
the fixture gives every cell an identical read so `c`/`y` is literally
constant; the code's own `not math.isnan(rho)` guard already turns this
into `spearman: None`, expected and transcribed verbatim from the
brief). Full `experiments/exp5/` suite: `42 passed`.

## Task 4: `collect_5.py`, `run/finals_5.py`, `run/sweep_5.py`, `run/preflight_5.py`, `run/s9_mac_5.py`, box scripts

Built the per-unit pipeline and the two stage runners: `battery_5.py`
additions (`CHECKPOINTS_SHA256_5`, `IMPORTED_SHA256_5` + `check_imports_5`
— 4c's `check_imports_4c` body adapted, the import surface as a verdict
input; `git_sha_5`, `projection_commit_5`, `is_ancestor_5`), `collect_5.py`
(the seven-size candidate-file loader, host attestation, `run_unit_5`
with `_unit.json` written last and the checkpoint freed in `finally`, a
one-slot `Prefetcher`, `rebuild_loss_table_5`), `run/finals_5.py` (stage
1: host record, gate 1(a) through two loader paths, seven finals, gate
1(b)), `run/sweep_5.py` (stage 2: spine, gate 1(c), `search_5.plan_5`'s
request loop per partner, S11, window prefetch), `run/preflight_5.py`
and `run/s9_mac_5.py` (prose-specified, model contact gated by
injectable `loaders=`), and the five box shell scripts + `.gitignore`
additions. TDD: `tests/fakes_5.py`, `tests/test_collect_5.py`,
`tests/test_stages_5.py` written first; `collect_5.py`/`run/finals_5.py`
transcribed byte-for-byte matched the brief's own tests with one
disclosed fixture fix (below); `run/sweep_5.py` transcribed byte-for-byte
except the window-prefetch extension (prose-specified, designed here).

**Window prefetch** (`run/sweep_5.py`): `_window_band` is a read-only
re-derivation of `search_5.plan_5`'s own bracket from the losses already
on hand (mirrors its spine-interval + `bisect_step_5` loop exactly; it
never issues a request — `plan_5` stays the sole authority on what gets
fetched). `_next_known` — the one function `request()` consults —
checks a small `_window_band_ctx` closure that holds the current pair's
band while WINDOW needs are being serviced and is cleared to `None` on
every SPINE/BISECT need, so a bisection step is never prefetched.
`request()` itself and both its call sites are byte-identical to the
brief.

**Disclosed deviations from the brief's given code** (test files only;
no production/frozen code touched beyond the brief's own Modify list):

1. **`tests/fakes_5.py`'s `digest_fn`.** The brief's default,
   `lambda size, step: f"d-{size}-{step}"`, produces a 9-character
   string; `battery_5.checkpoint_record_failures_5` (Task 1-3, frozen,
   never exercised by any Task 1-3 test) requires `len(digest) == 64`
   (a real sha256 hex). `test_run_unit_writes_36_files_then_unit_json
   _last_and_frees` calls both the literal digest assertion AND
   `checkpoint_record_failures_5` on the same record — the two brief-
   given pieces genuinely disagree. Verified empirically (ran the
   assertion in isolation, saw the single "tensor digest missing"
   failure) before editing. Fixed the fake to
   `hashlib.sha256(f"d-{size}-{step}".encode()).hexdigest()` and the
   one literal assertion that checked the old format; no other test
   referenced the digest's literal shape.
2. **`test_stages_5.py`'s `env` fixture.** `require_prereg_5`'s
   `blobs=INSTRUMENT_BLOBS_5` keyword default is bound at module-
   definition time, so monkeypatching the `INSTRUMENT_BLOBS_5` module
   attribute (my first attempt) does not reach `finals_5.run`/
   `sweep_5.run`'s un-parameterized calls; `analyze_5.py`/`power_5.py`
   (Task 5/6 deliverables) are not on disk yet, so every test calling
   `fin.run`/`sw.run` failed with "not on disk" before reaching any
   real logic. Fixed by wrapping `b5.require_prereg_5` itself in the
   fixture to bind a narrower `blobs` default (the files present by
   Task 4's end) — the same reason the fixture already no-ops
   `check_imports_5` next to it (Task 6 not built).
3. **`test_sweep_reuses_units_across_partners_and_records_it`.**
   Verified empirically (a standalone run with debug prints of
   `log["requests"]`/`log["pairs"]`) that for `size="6.9b"` under this
   fixture's `_loss`/`_count`/`SIZES`/`AVAIL`/`SPINE`, no request ever
   returns `action="reused"` inside `log["pairs"]`: `plan_5` is always
   handed the FULL, freshly-rescanned loss table before it is asked
   anything (once before the spine loop, once per partner), so it never
   emits a "need" for a step already on disk — the sharing (spine
   points common to all partners, the final pre-loaded by `finals_5`)
   happens silently inside `plan_5`'s own bookkeeping, never by
   `request()` landing on an already-complete unit. This holds
   structurally, not just for this data: `request()` is only ever
   called when `plan_5` returns `"need"`, and `plan_5` never returns
   `"need"` for a step in the `losses` dict it was handed. An explicit
   `"reused"` action is therefore unreachable in `log["pairs"]` under
   `sweep_5.py`'s given `request()`/`plan_5` wiring, for any loss data —
   changing this would need a production-code change to `sweep_5.py`'s
   given spine loop/`request()` (e.g. always calling `request()` and
   letting `run_unit_5`'s own completeness check discover reuse), which
   I did not make without a ruling. `collect_5.run_unit_5`'s reuse path
   itself IS exercised directly, by `test_run_unit_skips_a_complete_unit`
   in `test_collect_5.py`. Adjusted this one assertion to what the
   search actually guarantees (both partners searched, no unit loaded
   twice — the property "reused" was meant to protect); flagged in the
   Task 4 report for the controller's read.

Two bugs in my own added tests (not brief-given), also fixed: the
preflight smoke test's `cache_root=root` let its own scratch files
count against its "nothing under root changed" snapshot (fixed with a
separate `cache_root`), and a redundant assertion that `results/
host_5.json` was absent ignored that `fin.run()` (called earlier in the
same test) already wrote it (removed; the snapshot equality already
covers it).

`experiments/exp5/tests/test_stages_5.py` also carries the four tests I
designed per the task's resolution notes: window prefetch (spine steps
after the first, window steps after the first per pair, no bisected
step — matched to the box's flat/nested trace, not the naive full-band
reading, since spine/bisect-fetched band members are never themselves
prefetch TARGETS), a preflight smoke test on the fakes (asserts nothing
under `root/` changes at all), an S9 smoke test (write-once Mac host
record, one unit landed flat under `results/s9/<size>/step<k>/`, a
tolerance comparison against itself), and `bash -n`/executable-bit
checks for the five box scripts (folded into this file rather than a
separate `test_scripts_5.py`, to stay inside the brief's Files list).

Command: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
pytest experiments/exp5/tests/test_collect_5.py
experiments/exp5/tests/test_stages_5.py -p no:cacheprovider -q` → `21
passed`. Full `experiments/exp5/` suite: `73 passed` (`-W
error::DeprecationWarning`, no warnings).

### Task 4 fix round 1: rulings A and B on the "reused" concern

The controller ruled on Task 4's disclosed concern #3 (the `"reused"`
action being structurally unreachable in `log["pairs"]`) with two
production-code rulings, implemented together:

**RULING A** (`run/sweep_5.py`): when a pair reaches `done` or
`dropped`, the runner now also computes `rep = se.replay_5(losses,
avail, spine, target)` over the pair's own final loss table (the SAME
`losses` dict the partner loop ended with) and stores `log["pairs"]
[small]["requested_all"]` — the complete spine+bisect+window request
sequence, each step marked `"loaded"` if this run's own `request()`
call fetched it for this pair (i.e. it's in that pair's `requests`
list) or `"reused"` if `plan_5` found it silently already known (a
spine point, or a step an earlier partner/the finals stage already
fetched). The existing `requests` list is untouched (loaded-only, as
before) — `requested_all` is additive.

**RULING B** (`search_5.py` + `run/sweep_5.py`): `plan_5`'s `"need"`
dict for the WINDOW case gains two additive keys, `"bracket": [lo, hi]`
and `"window": b_minus + b_plus` (spine/bisect `need` dicts and the
`done`/`dropped` dicts are unchanged). `run/sweep_5.py`'s window
prefetch no longer re-derives the bracket itself: the now-deleted
`_window_band`/`_window_band_ctx` are replaced by a plain `band`
variable that the partner loop sets from `p["window"]` on a window
need (and clears to `None` on every spine/bisect need); `_next_known`
reads `band` directly. `request()` and its two call sites (the spine
loop, the partner loop) are unchanged.

`test_sweep_reuses_units_across_partners_and_records_it` (test_stages
_5.py) now asserts against `requested_all`: both `"reused"` and
`"loaded"` appear across `log["pairs"].values()`, `set(log["pairs"]) ==
{"1b", "2.8b"}`, no unit loaded twice, AND — for every `done` pair —
`[r["step"] for r in pair["requested_all"]]` equals `se.requested_steps
_5(se.replay_5(<the size's COMMITTED loss table>, avail, spine,
pair["target"]))`, the identity gate 4 will rely on. `test_search_5.py`
gained one assertion inside `test_plan_bisects_to_an_adjacent_bracket
_and_names_the_window`'s loop: on a `"window"` need, `p["bracket"] ==
[50000, 51000]` and `p["window"] == [48000, 49000, 52000, 53000]`.

Commands: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python
-m pytest experiments/exp5/tests/test_search_5.py -p no:cacheprovider
-q -W error::DeprecationWarning` → `9 passed`;
`experiments/exp5/tests/test_stages_5.py` alone → `25 passed`; full
`experiments/exp5/` suite → `73 passed`, no warnings.
