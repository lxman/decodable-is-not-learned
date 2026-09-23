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

## Task 5: `analyze_5.py` + `power_5.py` + the full-shape worlds

`power_5.py` transcribed byte-for-byte from the brief (the B-5
parameters, `live_structure_5`/`simulate_battery_5`/`_arm`/`compute`
reading through `stats_5.cell_5`/`primary_5`/`tree_5`, `main` writing
`results/power_5.json` ONCE). `analyze_5.py` built new: `collect_total_5`
(`analyze_2i.collect_total` widened by `zipfile.BadZipFile`, `KeyError`,
`OSError`, `ImportError`, `EOFError` — **and, past the brief's literal
list, by every other `Exception`**, disclosed below); `load_units_5`
(gate 3 over every COMPLETE unit of a size, all-or-nothing per size —
an incomplete/torn step directory is silently absent from its `steps`
list, never raised on, so a legitimate in-progress unit doesn't crash
the loader; only the size's FINAL is required present); `gate1a_
failures_5`/`gate1b_failures_5`/`gate1c_failures_5` (the last two
RE-DERIVE from the referent files under `root`, never trusting the
runner's own attested `counts`); `replay_pairs_5` (gate 4: per DONE
pair, `search_5.replay_5` re-run over the size's own committed losses
and checked against the logged `requested_all`/`plan`/`status`; per
DROPPED pair, status/target only); `power_failures_5`/`projection_
failures_5`; `licence_block_5` (the eight §6 cells: MATCHED-POWERED/
-UNDERPOWERED, NOT-MATCHED×{LARGE-AHEAD,SMALL-AHEAD,MIXED,THIN},
UNDETERMINED, INSUFFICIENT_DATA); eleven S1-S11 secondary functions,
each its own `collect_total_5` site inside `secondaries_5` (a
degrading secondary never touches `run()`'s own `failures`); `verdict_
5`/`write_verdict_txt_5`/`run()` (17-step refusal order exactly as the
brief's bullet list orders it, ending in the tree/licence/pins_active
assembly and an optional `write=True` that renders `results/
verdict.json` + `results/VERDICT.txt`).

**Disclosed deviations from the brief's literal text:**

1. **`collect_total_5` catches `Exception`, not only the five named
   types.** `test_collect_total_5_prefix_and_never_raises` calls
   `collect_total_5(lambda: 1 / 0, "5 x")` and asserts a `(None,
   [...])` return — `ZeroDivisionError` is not in the five-type list
   inherited through `analyze_2i.collect_total`'s chain (`ValueError`,
   `FileNotFoundError`, `KeyError`, `RuntimeError`, `TypeError`,
   `AttributeError`, `OSError`, `EOFError`, `zlib.error`, plus this
   task's five). Since the brief's own contract for `run()` is "nothing
   raises out of `run()` except [the prefix check]" (Interfaces line;
   resolution note 2), and the given test requires it, the
   implementation catches `Exception` broadly at the outermost `except`
   — a superset of the five named types, so every named type is still
   caught, and the totality contract (a bug inside a gate or a
   secondary degrades to a refusal, never a crash) is honoured for
   bugs of any kind, not only the five anticipated ones. Verified: the
   given test passes as written; no other test's expectations changed.
2. **`secondaries_5` returns `(secondaries, secondary_failures)`, a
   2-tuple, not a bare `dict`** as the Interfaces line's `-> dict`
   literally states. `run()` needs the per-secondary failure list kept
   OUT of `failures` (§ "Secondaries... NOT in failures") and IN a
   separate `secondary_failures` dict the verdict carries — the
   2-tuple is the natural shape for that, mirroring `replay_pairs_5`'s
   own `-> tuple` (which correctly matches the brief). No test calls
   `secondaries_5` directly (only `run()`'s output is asserted), so
   this is a design choice, not something a test forced or a test
   revealed as wrong; noted for the reviewer's judgment.
3. **The per-secondary `collect_total_5` sites live inside `secondaries
   _5`, not spelled out individually in `run()`.** "Code Organization"
   asked for the sites to be "in `run()`"; keeping `run()`'s own body to
   its 17 gate steps (already ~350 lines) and delegating the eleven
   S1-S11 sites to a dedicated aggregator (itself using the exact same
   `collect_total_5(fn, "5 S<k>")` pattern) was judged the better
   trade-off given the file's overall size (~1070 lines, in 4c's
   range). Functionally identical either way; flagged per the "report
   DONE_WITH_CONCERNS rather than splitting on your own" instruction,
   in the other direction (consolidating, not splitting).
4. **`load_units_5` and `secondaries_5` take one keyword the brief's
   Interfaces line doesn't list** (`load_units_5(..., n_scored=None)`;
   `secondaries_5(cells, units_by_size, pairs_data, root)` — the
   arguments are as named but the return shape is the tuple in (2)).
   `n_scored` is needed to thread the injected slice's true scored-
   token count (197 in the fakes, 2**21 for real) into `loss_record_
   failures_5`'s contract check inside `load_units_5`, per resolution
   note 1's "`loss_record_failures_5(..., n_scored=sl["meta"]
   ["n_scored"]...)` is the contract call" — the note doesn't say
   where that call lives, and `load_units_5` (the only place gate 3's
   loss contract is checked) is where it has to be for the test slice
   to validate at all.
5. **`write_verdict_txt_5` additionally prints a `gate 1` block (gates
   1(a)/(b)/(c) one line each with max/sum |Δ|) and a `dropped:` line
   per dropped pair with its spine losses** — both explicitly required
   by the brief's `write_verdict_txt_5` bullet ("gates 1(a)/(b)/(c) one
   line each... the pairs dropped with their spine losses") but not
   present in a first draft; caught in self-review before commit and
   required threading `gate1a_rec`/`gate1b_rec`/`gate1c_recs` and a new
   `gate4_total["dropped_detail"]` list through `run()` into `verdict_
   5` (which gained one new optional keyword, `gate1=None`, beyond the
   brief's literal `verdict_5(...)` signature — again undocumented in
   the Interfaces line, needed to carry the data).
6. **A real bug caught by the worlds, not by design:** the first
   `_gate4` draft computed `units_unnamed` for reporting but never
   turned a non-empty result into a failure, so the "a unit nobody
   asked for" refusal route (`test_refusal_routes_deliver_insufficient
   _data`) silently passed through to `MATCHED`. Fixed by appending one
   `"gate 4 {size}: step{s} on disk but never requested..."` message
   per unnamed step into the returned failures list.

**World-constant tuning (Step 5, sanctioned).** The brief's `full_shape
_5.py` block, transcribed verbatim, needed two numeric changes to reach
all five terminals cleanly:

- `SPINE_W`'s second point widened from `4000` to `6000` (the gap after
  `1000`). At `(1000, 4000)` the 6.9b×1.4b crossing — the pair that
  ends up first in `log["pairs"]` once 6.9b×1b drops (6.9b's loss is
  already below 1b's target at the very first spine point, on every
  `BASE_W`/mode tried) — resolves in exactly ONE bisection probe, so
  `test_refusal_routes_deliver_insufficient_data`'s "reverse the
  logged `bisected` order" tamper is a no-op on a length-1 list and the
  gate 4 refusal route was unreachable by that specific test. `(1000,
  6000)` reliably needs >= 2 probes on every mode (verified: MATCHED,
  LARGE-AHEAD, SMALL-AHEAD, MIXED, UNDETERMINED all still land
  correctly with the wider gap; `BASE_W` tuning was tried first and
  rejected — it fixed the bisection depth but flipped MIXED's world to
  LARGE-AHEAD-dominant, since `BASE_W` shifts every mode's live-cell
  set simultaneously in ways that are hard to reason about jointly,
  whereas widening one spine gap only changes bisection depth).
- SMALL-AHEAD's per-size offset magnitude lowered from `40` (LARGE-
  AHEAD's and MIXED's magnitude, unchanged) to `32`. The offset there
  is SUBTRACTIVE and applies to every read of a ranked size INCLUDING
  the small side's own final (scaled by its own rank), so at `40` it
  crushes too many cells toward zero to clear `MIN_LIVE_CELLS_5 = 20`
  (empirically 18 cells / 6 rungs, landing UNDETERMINED, and the rung-
  block p at that cell count was 0.0156 > 0.01 regardless). A magnitude
  sweep (15/20/22/24/25/26/28/30/32/35, `experiments/exp5/tests/
  full_shape_5.py` git history none of it kept — the sweep script was
  scratch, not committed) found 21 cells / 7 rungs stable across
  22-32, all-negative signs from 24 up; 32 was kept for the largest T/p
  margin (T .0354, p .0078) without drifting into LARGE-AHEAD's own
  magnitude (keeping the two modes visibly distinct).

**Tests.** Fast (`test_power_5.py` + `test_analyze_5.py`): 9 passed —
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest
experiments/exp5/tests/test_power_5.py experiments/exp5/tests/test_
analyze_5.py -p no:cacheprovider -q` → `9 passed in 7.70s`. Slow
(`test_full_shape_5.py`, `-m slow`): 7 passed (five terminals incl.
`UNDETERMINED`, the six-tamper refusal-route test, the write test) —
`... -m slow -q` → `7 passed in 76.22s`. Full `experiments/exp5/`
suite: `89 passed in 94-95s`, no warnings (`-W error::RuntimeWarning`
clean). Zero model contact, zero network, zero edits outside
`experiments/exp5/`. No pre-tag execution against the real
`experiments/exp5/` tree — every `run()` call in every test targets a
`tmp_path`.

### Task 5 fix round 1: controller ruling on `collect_total_5`'s exception surface

**Deviation 1 above (this entry's own text) is SUPERSEDED, not
retracted — kept verbatim for the record.** The controller ruled:
`collect_total_5` must NOT catch bare `Exception`. The totality
contract protects DATA problems only, not logic defects — 2i's own
`collect_total` docstring already says a reachable exception outside
its named set "would be a logic defect in the instrument, which must
surface as a crash rather than be laundered into a refusal."
`collect_total_5`'s `except` clause is now restored to the named list
exactly: `analyze_2i.collect_total` (2h's/2g's chain) wrapped by
`except (zipfile.BadZipFile, KeyError, OSError, ImportError,
EOFError)` — every OTHER exception now propagates out of `run()`; the
`"5 "`-prefix `ValueError` check is unchanged. `test_collect_total_5_
prefix_and_never_raises` was replaced with the controller's own
`test_collect_total_5_prefix_named_types_and_crash_on_logic_defect`
(transcribed verbatim): a named type (`OSError`) is caught and
formatted exactly; a clean call passes through; `1 / 0`
(`ZeroDivisionError`, no longer caught) now propagates via
`pytest.raises(ZeroDivisionError)`; the prefix check still raises.
Checked every `collect_total_5` call site in `run()` against the
narrowed list (every JSON parse error is a `ValueError` subclass, every
missing-file error is an `OSError` subclass, every explicit raise in
this module is `ValueError`/`RuntimeError`, every malformed-record
dict access is `KeyError`) — no site needed the bare-`Exception` catch,
confirmed by re-running the slow worlds (all six refusal-route tamper
scenarios still land `INSUFFICIENT_DATA`, no traceback). Full detail
in the fix report (`.superpowers/sdd/2026-09-22-exp5-build/task-5-
report.md`, gitignored). Commit `780e94afc`.

### Task 5 review, fix round 1: four review findings

**1. Gate 4's "nothing else loaded" check was incomplete.** It ran only
inside the `LARGE_SIDES_5` loop (the smallest size, never swept as
large, was never checked at all), and its `expected` set was built
from the LOG's own `requested_all` field — an attested, not measured,
quantity, so a stray `pairs` key naming an already-complete unit could
hide a real orphan. Fixed: a new `expected_steps_5(units_by_size,
manifest, size)` RE-DERIVES the expected set for every size in
`b5.SIZES_5` (spine + every legitimate partner's fresh `search_5.
replay_5` result + `{final}` + `{S11 step}` when applicable — never
read from any log), the gate-4 orphan check now runs for every size
(spine/gate1c/search-log stay conditional on `LARGE_SIDES_5`, since
the smallest size never gets a search log to check), and
`replay_pairs_5` now refuses any `search_log["pairs"]` key that is not
a legitimate (strictly smaller) partner of the size. Two new tamper
scenarios added to `test_refusal_routes_deliver_insufficient_data`: an
orphan unit under the world's smallest size (`"1b"`), and a stray
`pairs` key naming an existing unit — both land `INSUFFICIENT_DATA`
with a gate-4 failure.

**2. S8/S9/S10 were narrower than design §5.** S8 now reads 2g's FULL
committed 2.8b grid (`battery_2g.trained_steps("2.8b")`, 21 points —
`GRID["2.8b"]` already excludes 0 and the stale-copy step64000) and
2h's full 6.9b grid (`battery_2h.trained_steps_69()`, 22 points), each
record read via `battery_5.interior_record_path_5` directly (chosen
over `battery_4.load_outcome_4`: exp4's accessor would add an import
outside 2g/2h/exp5's existing surface for the same committed bytes
`interior_record_path_5` already reaches) — every point's loss is
MEASURED when it coincides with a step this experiment's own run
loaded, else LOG-STEP INTERPOLATED between the two bracketing loaded
points (flat past the ends), each point carrying `"interpolated":
true/false` and each size carrying a one-line `"disclosure"` string.
S9 now prints, per re-run unit under `results/s9/`, `battery_5.
tolerance_failures_5(mac_counts, box_counts, label=...)` against the
box's own committed unit for the same (size, step) plus the loss
difference; `"not run"` unchanged when `results/s9/` is absent. S10
gained `"re_crossings"` (a new `_re_crossings_5` helper: every spine
interval where `loss(t_i) >= target > loss(t_{i+1})` per legitimate
partner, with the first crossing distinguished from any re-crossings
beyond it) and `"b6_12b"` (a new `_b6_12b_5` helper: for every
`GATE1_DESCRIPTIVE_12B_5` step present as a 12b unit, `tolerance_
failures_5` against `mac_interior_counts_5("12b", step)` with max/sum
|Δ|) — both non-gating, into the S10 dict only, never `run()`'s own
`failures`. `secondaries_5` and `_s10_texture_5` each gained a
`manifest` parameter to thread the spine lookup through. Two new fast
tests (`test_re_crossings_5_counts_intervals_beyond_the_first`,
`test_s8_grid_points_interpolates_and_flags_measured_points`, both in
`test_analyze_5.py`) exercise the new helpers on synthetic tables;
`test_every_terminal_is_reachable` gained assertions that `S8` carries
both grids (21/22 points, a mix of interpolated and measured) and
`S10` carries `re_crossings` (keyed by every `LARGE_SIDES_5` member)
and `b6_12b` (empty in the worlds — no 12b size).

**3. Stale exception-surface prose.** `analyze_5.py`'s MODULE docstring
still said `collect_total_5` widens "all the way to `Exception`" after
fix round 1's ruling had already changed the function itself — the
function's own docstring was correct, the module's was not. Rewritten
to state the five-type widened list and that any other exception is a
logic defect that crashes `run()`.

**4. Promoted minor: the power gate must MEASURE its provenance, and
the named gate function must be the whole of the gate.** `power_
failures_5` now takes `power_gate="full"` and: (a) pins `rec["n_sim"]
== power_5.N_SIM_5` and `rec["seed"] == power_5.SEED_5` (a record
written at a different n_sim/seed reproduces itself under `pw.compute`
— self-consistency is not provenance); (b) — choosing to USE its
`finals_counts`/`floors` arguments rather than drop them — the
`finals_sha256` check plus the `power_5.compute` byte-reproduction
check (guarded by `power_gate != "skip"`) both moved INTO `power_
failures_5` from `run()`'s own `_check_power` closure, which is now a
thin wrapper: load the record, call `power_failures_5(root, rec,
finals_counts, floors, power_gate=power_gate)`, raise on any failure.
One new fast test, `test_power_failures_5_pins_n_sim_and_seed`: a
clean record passes at `power_gate="skip"`; `n_sim` changed refuses
with `"n_sim"` in the message; `seed` changed refuses with `"seed"` in
the message.

**Tests after this round:** fast `test_analyze_5.py` + `test_power_5.py`
→ `12 passed`; slow `test_full_shape_5.py` (`-m slow`) → `7 passed in
81.42s`; full `experiments/exp5/` suite → `92 passed in 100.25s`, no
warnings (`-W error::RuntimeWarning` clean). Full detail (per-finding
diffs, commands, output) in the fix report
(`.superpowers/sdd/2026-09-22-exp5-build/task-5-report.md`, gitignored).

## Task 6: `make_referents_5.py`, `verify_referents_5.py`, totality, determinism, the mutation harness, the read sweep, the import scan, the pins

Built: `make_referents_5.py` (`referent_files_5()` — 34 item files, 2d's
`results/verdict.json`, 2c's m4 finals at 2.8b/6.9b/12b, 2d's argmax
finals at 410m/1b, 2g's FULL committed 2.8b trained grid, 2g's 12b
sweep at the six B-6 descriptive steps, 2h's FULL committed 6.9b
trained grid, `checkpoints_5.json`/`hub_inventory_5.json`/`slice_5.npz`/
`power_5.py`; `build`/`check_referents_5` 4c's shape verbatim);
`referents_5.json` (**N_FILES_5 = 1786**, sha `e7a1ea3b…`, pinned as
`analyze_5.REFERENTS_5_SHA256`); `verify_referents_5.py` (the 13-item
cold battery, 4c's `@check` shape); `tests/test_totality_5.py` (the 9
named tree shapes in one test function + the site-template census, two
tests); `tests/test_determinism_5.py` (two-process byte-identity);
`tests/mutation_check.py` (56 mutants: 28 hand-written across
`battery_5.py`/`slice_5.py`/`search_5.py`/`stats_5.py`/`collect_5.py`/
`run/finals_5.py`/`run/sweep_5.py`/`analyze_5.py`/`power_5.py` + 28
AST-generated `collect_total_5`-site mutants restricted to `run()`'s
own body); `tests/read_sweep_5.py`; `tests/import_scan_5.py`;
`tests/test_verify_referents_5.py` (fast unit coverage on individual
`@check` functions). Modified: `battery_5.py` (`FROZEN_SHA256_5` — 51
files, `IMPORTED_SHA256_5` — 6 files, exactly the brief's predicted
residual: `__init__.py`, `run/__init__.py`, `make_referents_5.py`,
`verify_referents_5.py`, `run/preflight_5.py`, `run/s9_mac_5.py`);
`analyze_5.py` (`REFERENTS_5_SHA256` pinned; `power_failures_5`'s
None-refusal fix below; `verdict_5`'s `meta` refactor below).

**Finding 1 (referent-manifest reconciliation): 12b's committed sweep
records cover only the 11 `PREDICTOR_RUNGS`, never all 34.** The
brief's Step 1 literal ("2g's 12b sweep records at the six B-6
descriptive steps") assumed 34-rung coverage matching 2.8b's; the real
tree (`experiments/exp2g/results/sweep/12b/step*/`) holds exactly 12
files per step (11 rungs + `_checkpoint.json`) at every one of the
eight committed 12b grid points, verified directly. `battery_2g.
sweep_rungs("12b")` already names this set (`REPLICATING` →
`PREDICTOR_RUNGS`), so `make_referents_5.py` reads `bg.sweep_rungs
(size)` for both 2.8b (`ADJUDICATING` → all 34) and 12b, rather than
the module-level `RUNGS` constant — N_FILES_5 lands at 1786, not the
brief's implied ≈2,244 for a 34-rung 12b grid. **Left open, disclosed,
not fixed (out of Task 6's scope):** `battery_5.mac_interior_counts_5`
and `analyze_5._b6_12b_5` still iterate all 34 `RUNGS` unconditionally
for every size, including 12b — the first time a real 12b unit lands
at one of the six `GATE1_DESCRIPTIVE_12B_5` steps, `_b6_12b_5`'s call
to `mac_interior_counts_5("12b", step)` will raise `FileNotFoundError`
on a rung outside `PREDICTOR_RUNGS`. This is caught by `collect_total_5`
(a `KeyError`/`OSError`-class exception via the missing-file read) and
degrades S10's `"b6_12b"` block to a recorded secondary failure — never
reaches `run()`'s own gating `failures` list, so the VERDICT is
unaffected, but the B-6 12b comparison silently loses its data every
time. `test_full_shape_5.py`'s worlds never include a 12b size, so this
path has never been exercised (Task 5's own PROGRESS entry: "`b6_12b`
(empty in the worlds — no 12b size)"). A future task should scope both
functions to `battery_2g.sweep_rungs("12b")`.

**Finding 2 (the brief's "27-site harness" is 28 in the committed
source).** The AST walk restricted to `run()`'s own FunctionDef body
(the exact scope `test_totality_5.py::_site_templates_5` and `tests/
mutation_check.py::_totality_mutants_5` both use) finds 28 distinct
`collect_total_5(thunk, label)` call sites, not 27 — the extra one is
`"5 verdict write"`, the `if write: ...` block near the end of `run()`,
gated behind `write=True`. It is a real, textually-present call inside
`run()`'s body, so it is covered as a superset of the brief's count
(`test_site_template_count_matches_the_brief` asserts 28 and documents
the discrepancy) rather than excluded to force the number to match; the
27-/28-site census test reaches it with one extra `_run(..., write=
True)` call.

**Finding 3 (`verify_referents_5.py` build bug, fixed before commit):**
item 5's first draft assumed `checkpoints_2h.json` was keyed by size at
the top level like `checkpoints_2g.json` (`{"2.8b": {...}, "12b":
{...}}`); it is flat (one size, no top-level key) — `KeyError: '6.9b'`
on first cold run. Fixed: the plan tuple reads `old_2h` directly for
6.9b, `old_2g["2.8b"]`/`old_2g["12b"]` for the other two, disclosed in
the function's own comment.

**`verdict_5`'s `"meta"` refactor (the brief's own words: "put those
under one `meta` key... if they are not already").** The verdict's only
volatile top-level field was `git_sha` (captured fresh by `b5.git_sha_
5()` on every `run()` call) — no other timestamp exists anywhere in the
verdict tree (checked: no `written_utc`/similar leaks into the top
level; S9's cross-host block does carry committed units' own
`written_utc` fields, but those are FIXED once written, not
re-captured per analysis, and S9 is `"not run"` in every synthetic
world/real pre-campaign tree used here). `verdict_5`'s return now nests
it as `{"meta": {"git_sha": git_sha}}` instead of a bare `"git_sha"`
key; `run()`'s `__main__` printout and the new `test_determinism_5.py`
both updated to read `result["meta"]["git_sha"]`. This is the ONLY
verdict-shape change in Task 6.

**The flagged Task 5 minor, closed:** `power_failures_5` now REFUSES
(one line, `"power record: cannot reproduce — finals_counts or floors
missing (power_gate='full')"`) when `power_gate == "full"` and either
`finals_counts`/`floors` is `None`, instead of silently no-op'ing the
byte-reproduction check the caller explicitly asked for; `power_gate ==
"skip"` is unaffected (still the normal test-only shape). New fast
test: `test_power_failures_5_refuses_on_missing_inputs_when_gate_is_
full`.

**A process incident, disclosed in full.** While manually verifying
individual mutant kills against the LIVE (shared) source files, this
session twice used `git checkout -- <file>` to restore after a
one-off hand-mutation — safe for a file with NO uncommitted changes,
but `battery_5.py` and `analyze_5.py` both carried uncommitted Task 6
edits (the FROZEN_SHA256_5/IMPORTED_SHA256_5 tables; the REFERENTS_
5_SHA256 pin, the power-gate fix, the meta refactor) at the time. The
first incident (`analyze_5.py`) coincided with the BACKGROUND mutation
harness's own concurrent backup/restore cycle for a DIFFERENT mutant
under test at the same moment — the two processes' file writes raced,
and a stray totality-mutant fragment (`"5 host record"`'s stripped
`collect_total_5` call) was briefly left applied; it self-healed when
the harness's own `finally` block restored from ITS OWN backup shortly
after. The second incident (`battery_5.py`) had no such luck: `git
checkout --` reverted `FROZEN_SHA256_5`/`IMPORTED_SHA256_5` all the way
back to `None` (Task 5's committed state), caught immediately via `git
diff --stat` reading empty for a file that should have carried ~120
new lines, fixed by re-running `import_scan_5.py` and re-pasting both
tables (the fresh scan reproduced the prior output byte-for-byte except
for `verify_referents_5.py`'s own hash, confirming no other drift).
**Lesson applied for the remainder of the task and left here for any
future session:** manual mutation-kill verification against a file
that carries uncommitted legitimate edits must use a `cp`-based
snapshot/restore (`cp file file.safe; …mutate/test…; cp file.safe
file; rm file.safe`), never `git checkout --`, and must never run
concurrently with the background mutation harness (which the brief
already says explicitly: "run alone, detached" — this incident is the
concrete reason why). Every fast-mutant kill claimed in `mutation_
build.log` was independently re-confirmed this way AFTER both
incidents were resolved (#1/#2 bar/alpha boundaries; #9 the crossing
test's closed/open ends; #11 `clears_5`'s significance-vs-rate
distinction; #15 `unit_complete_5`'s content check; #18 the
prefetcher's failure print; #19 gate 1(a)'s per-doc-loss comparison;
#20 `replay_pairs_5`'s logged-vs-derived target; #22 the projection
ancestry's final-step exclusion; #27 `slice_equal_5`'s set_index
comparison — nine confirmations, each shown killing its own mutant and
nothing else).

**Six new fast tests closing hand-mutant survivors** (all in the
existing fast files, none new): `test_stats_5.py::test_tree_precedence`
gained two boundary assertions (`T == T_BAR_5` → NOT-MATCHED, closed;
`p == ALPHA_5` → MATCHED, open) killing the bar/alpha widening mutants;
`test_search_5.py::test_plan_crossing_is_closed_at_the_low_end_exactly`
(a target equal to the first spine point's own loss — the max loss a
decreasing table can hit — must still cross, not drop) kills the `>=`/`>`
swap; `test_battery_5.py::test_clears_5_is_a_significance_test_not_a_
bare_rate_comparison` (count exactly at the floor reads False under the
real binomial-significance rule, True under a bare-rate mutant) kills
the `clears_5` weakening; `test_collect_5.py` gained `test_unit_
complete_5_checks_content_not_only_presence` (a file present but
content-changed after `run_unit_5` must read incomplete) and `test_
prefetcher_wait_prints_on_a_failed_download` (capsys-checked); `test_
stages_5.py::test_finals_gate1a_catches_a_per_doc_loss_mismatch_with_
equal_aggregate` (a custom `loaders["loss"]` that returns the SAME
aggregate scalar on both loader paths but a DIFFERENT `per_doc_loss`
list); `test_analyze_5.py` gained `test_replay_pairs_5_uses_the_
committed_loss_not_the_logged_target` (a hand-built 4-point spine where
the re-derived target crosses at one bracket and a tampered logged
target would cross at another) and one more assertion in `test_
projection_failures` (an `is_ancestor` that fails specifically on the
FINAL step's own sha must still read clean — the final's exclusion is
by design, its unit is built in stage 1 before the projection exists);
`test_slice_5.py::test_slice_equal_5_catches_a_set_index_mismatch`
(matching ids/offsets/set_names, differing set_index, must not read
equal). Plus one new hand mutant not in the brief's literal list but
matching its intent ("the mutants... applied in place... `run/sweep_
5.py`"): the halted-size refusal in `sweep_5.run()` dropped — killed by
the EXISTING `test_stages_5.py::test_sweep_resumes_and_refuses_when_
halted`.

**The remaining 30 hand+totality survivors after the fast pass all
route to the SLOW suite, confirmed via `--worlds-only` (29/29 killed,
0 open, 0 errors) — `mutation_worlds.log` committed.** One genuinely
needed the full-shape world (`gate4_an_orphan_unit_units_unnamed_is_
never_turned_into_a_failure` → `test_full_shape_5.py::test_refusal_
routes_deliver_insufficient_data`, the ONLY mutant that needed
`--fullshape` after totality alone failed to catch it). **Process note
(disclosed, not hidden): 23 of the 28 AST-generated totality mutants
are killed by `test_site_template_count_matches_the_brief` — a
STRUCTURAL check** (removing any `collect_total_5` call drops the
AST-detected site count from 28), not a behavioural one. This is a
legitimate kill under the ordinary mutation-testing convention (some
test in the covering suite fails), and it is not accidental — every
totality mutant IS also exercised behaviourally by the 9-shape test
and by the census test's own recording pass, which both run FIRST in
file order and pass cleanly under every one of these 23 mutants (the
underlying `collect_total_5` call, even stripped of its try/except
wrapper, only differs observably from the real one when its thunk
RAISES, and none of the 9 named corruption shapes happens to drive
exactly these 23 sites into a raising state — they cover loaders that
succeed regardless of the wrapper on a clean/partially-corrupted world,
the primary/modifier/cells pipeline, gate 1(a)/(b)/(c)'s already-tested
contract functions, and the import-surface/referents checks). The
other 5 (`_check_halts`, `_check_projection`, `_check_loss_table`,
`_check_power`, `_gate4`, `_load_search_log`, `_load_all_units` — one
per shape) are killed by `test_every_runner_leavable_tree_shape_gives_
insufficient_data` directly, matching the 9-shape list's own coverage
one-for-one where a shape exists for that exact site. **This is the
methods-paper-lesson-candidate this task surfaces, Michael's call:** a
structural site-count test is a cheap, real backstop for "the wrapper
exists at all," but it does not by itself demonstrate that stripping
the wrapper changes BEHAVIOUR at that site — the 9-shape test's own
coverage is what does that, for the 6 sites it reaches; the other 23
sites' wrappers are exercised for PRESENCE, not for a demonstrated
behavioural difference, on this instrument.

**Pin tables (import scan, run cold against the real tree — identical
across three separate runs):** `FROZEN_SHA256_5` 51 files (every
`experiments/` module `battery_2d`/`battery_2g`/`checkpoints_2g`/
`predictor_2g`/`battery_2h`/`analyze_2i`/`battery_2i` pull in
transitively — the full exp2b/exp2c/exp2d/exp2f/exp2g/exp2h/exp2i/exp3/
exp3c/exp1-signatures surface, `models`/`harness` included via their
resolved FILE PATH under `experiments/exp2b/`/`experiments/exp2c/`
even though imported as bare top-level names); `IMPORTED_SHA256_5` 6
files (`__init__.py`, `run/__init__.py`, `make_referents_5.py`,
`verify_referents_5.py`, `run/preflight_5.py`, `run/s9_mac_5.py` —
exactly the brief's predicted residual).

**Read sweep (run cold against the real tree, identical across two
runs after the referents_sha/imports_pinned/frozen_check overrides
were dropped in favour of the PRODUCTION defaults — `an.run(root=
b5.EXP5, tag_exists=lambda t: True, blob_sha=…, blobs_bound=lambda
t, p, **k: [], n_sample=10, n_boot=10)`):** refuses at `"5 host
record"` (no `results/host_5.json` on the pre-campaign tree, exactly
as the brief predicted) — **1853 distinct paths, 1952 total open/read
calls, 0 UNPINNED.** Buckets: `referents_5.json` 1783 (the manifest's
1786 listed files minus the 3 that ALSO carry their own independent
sha-pin, reclassified into the next bucket), `sha_pin_at_load` 4
(`checkpoints_5.json`, `slice_5.npz`, 2d's `results/verdict.json` via
`battery_2g.load_floors`'s own pin, and `referents_5.json` ITSELF via
`check_referents_5`'s own pin — a fourth item beyond the brief's
literal three, disclosed in the tool's own docstring), `pinned_module`
57 (the 51+6 pin-table files, read via `bg.sha256_file` inside `check_
frozen_5`/`check_imports_5`, now exercised for real since those two
checks run at PRODUCTION defaults), `instrument_blob` 9, `python_
stdlib_venv` 0 (the sweep covers the DATA surface only, matching
4c's own precedent — python source loading doesn't route through the
wrapped `open`/`read_text`/`read_bytes`/`np.load`).

**Totality (`test_totality_5.py`, 3 tests, all pass):** the 9 named
shapes in one test function, each corruption applied then restored
before the next, `try`-wrapped so ANY exception fails the test (none
raised) — 1. finals halted at gate 1(a) (marker + a partial 2.8b unit,
one rung file gone); 2. a torn unit (no `_unit.json`, a non-final
spine step); 3. `_unit.json` present, one rung file gone (a different
step from #2); 4. the search log's pair left `"open"` (stale against
the committed units); 5. a pair `dropped` — NOT a refusal, asserted
directly on the clean world (6.9b×1b drops naturally on the synthetic
curve, per Task 5's own PROGRESS note); 6. a size with no search log
at all; 7. a corrupt json (torn mid-token); 8. a missing power record;
9. a projection not in history (`is_ancestor` returns False). The
27-/28-site census (two tests): `test_site_template_count_matches_the_
brief` (28, Finding 2 above) and `test_every_collect_total_5_site_in_
run_is_reached_across_the_shapes` (every one of the 28 templates hit
at least once, via the clean run + one probe with `GATE1_INTERIOR_5`
patched non-empty for gate 1(c) + replays of 4 of the 9 shapes + one
`write=True` call for the 28th site).

**Determinism (`test_determinism_5.py`, 1 test, passes):** the same
MATCHED world analysed in two SEPARATE `subprocess.run([sys.executable,
…])` interpreters (each re-applying `full_shape_5.apply_shrink` via a
standalone `pytest.MonkeyPatch()`, never undone — a one-shot process),
`verdict.json` byte-identical after dropping `"meta"` wholesale (the
one volatile key, per the refactor above) — confirmed the strip is
real work, not a no-op, by asserting `"meta"` and `"git_sha"` are
present in the raw output before stripping.

**Mutation harness final tally (`mutation_build.log`, 56 mutants):
27 killed by the fast suite directly; 29 killed by the slow suite
(each individually re-confirmed via `--worlds-only`, not inferred);
0 documented equivalent; 0 unresolved survivors; 0 skips; 0 timeouts.**

**Pre-tag analyzer executions on the real tree (`root=battery_5.EXP5`),
counted per the brief's disclosure rule — 10 total, none altering the
committed campaign tree (write=False throughout):**
1. `import_scan_5.py`, first attempt — `an.run()` succeeded (`"5
   targets seal"` refusal) before the subsequent `ModuleNotFoundError`
   on `verify_referents_5` (not yet written).
2. `import_scan_5.py`, second attempt (after writing `verify_
   referents_5.py`) — `"5 targets seal"`.
3. `scan()` via a one-off `python -c` invocation, to verify `check_
   imports_5()`/`check_frozen_5()` pass in a fresh process after the
   first table paste — `"5 targets seal"`.
4. `read_sweep_5.py`, first attempt (`referents_sha=False, imports_
   pinned=False`, matching exp4c's original template literally) —
   `"5 targets seal"`.
5. `read_sweep_5.py`, second attempt (overrides dropped in favour of
   production defaults) — refused at `"5 import surface (entry)"` on a
   stale `verify_referents_5.py` pin (Finding 3's fix landed between
   scans 2 and this one).
6. `import_scan_5.py`, re-run after Finding 3's fix and adding the
   `blobs_bound` stub to both cold tools — `"5 host record"`, the
   brief's predicted refusal point, reached for the first time.
7. `read_sweep_5.py`, clean run with the fix and the `blobs_bound`
   stub — `"5 host record"`, 0 UNPINNED.
8. `scan()` via `python -c`, to re-verify `check_imports_5()`/`check_
   frozen_5()` after the `battery_5.py` accidental-revert incident
   (disclosed above) was fixed — `"5 host record"`.
9. `import_scan_5.py`, final verification (after all fast-test/
   mutation-harness edits landed) — byte-identical output to run 6/8
   except run 6's own stale-pin line, confirming no further drift.
10. `read_sweep_5.py`, final verification — identical to run 7 (1853
    paths, 0 UNPINNED).
`verify_referents_5.py`'s own cold-battery runs (five, including the
one that caught Finding 3) are NOT counted — the tool reads committed
files directly and never calls `analyze_5.run()`, per the brief's own
carve-out.

**Final state.** Fast suite (`experiments/exp5/tests/ -m "not slow"`):
**101 passed** (was 92 at the end of Task 5; +9: 6 new mutation-kill
tests, 2 power-gate/None-refusal tests, 1 replay_pairs_5 test — the
`test_verify_referents_5.py` file itself contributes 10 of the 101).
Slow suite (`test_totality_5.py` + `test_determinism_5.py` + `test_
full_shape_5.py`, `-m slow`): **11 passed in 150.77s** (was 7 at the
end of Task 5; +4: the 9-shape totality test, the two census tests,
the determinism test). Cold battery: **11/13 + 2 legitimate SKIPs**
(item 11 power record, pre-targets; item 13 gate records,
pre-campaign). Import scan: **0 unpinned** (51 frozen, 6 residual).
Read sweep: **0 unpinned** (1853 distinct paths). Mutation: **56/56
resolved, 0 open survivors**. Zero model contact, zero network beyond
the two cached-file reads item 7's slice re-derivation needed (both
served from the local HF cache, no download), zero edits outside
`experiments/exp5/`.

## Task 6 fix: B-6's 12b comparison (controller ruling, 2026-09-22)

**Ruling accepted verbatim.** Concern 1 from the Task 6 report — 2g's
committed 12b replication sweep carries records for `battery_2g.
PREDICTOR_RUNGS` (11) only, never all 34, so B-6's comparison was
silently comparing an 11-file-per-step referent as if it were a
34-rung one — is a real defect in the design's B-6 comparison. Fixed
before the review is dispatched, exactly the four points ruled, nothing
else touched.

**(a) `battery_5.mac_interior_counts_5(size, step)`.** New pin:
`GATE1_DESCRIPTIVE_12B_RUNGS_5` — a literal 11-rung tuple, checked at
IMPORT against `battery_2g.PREDICTOR_RUNGS` (`if set(...) != set(bg.
PREDICTOR_RUNGS): raise RuntimeError(...)`), the same pattern
`MAIN_SHA_5` already uses for the Hub SHAs (a hard-coded copy that
refuses to import if the live source has drifted — not a tautological
self-reference). For `size == "12b"`, the function now ALSO discovers
which rung record files actually exist under `interior_record_path_5`
and asserts that SET equals `GATE1_DESCRIPTIVE_12B_RUNGS_5`, raising
`ValueError` (a genuine data-shape defect, not a missing-checkpoint
gap — same philosophy as the function's pre-existing "not the expected
shape" raise) on any other set; only those 11 rungs are then read.
2.8b/6.9b are untouched — still all 34 `RUNGS`, unconditionally.
Docstring updated to say so. Verified live against the real committed
tree: all six `GATE1_DESCRIPTIVE_12B_5` steps (1000/4000/16000/32000/
64000/100000) return exactly the 11 pinned rungs; 2.8b/6.9b interior
steps still return 34.

**(b) `analyze_5._b6_12b_5`.** Now computes `rungs = tuple(sorted(set(
counts) & set(ref)))` — the intersection of the REAL unit's rungs
(always 34; `load_units_5` reads all `b5.RUNGS` for every size,
12b included) and the referent's rungs (11, after (a)) — rather than
iterating the full 34 and reading 23 "count missing on one side"
failures out of `tolerance_failures_5`. Calls `battery_5.
tolerance_failures_5(counts, ref, label=..., rungs=rungs)` (new
optional parameter, (b) below) and prints `n_rungs_compared` (11),
`sum_abs_diff`/`max_abs_diff` over exactly those 11, `gate1_tol_
per_rung` (120→ no, `GATE1_TOL_PER_RUNG_5`, 15, unchanged — the
per-rung bound does not scale), and `gate1_tol_sum_scaled` =
`GATE1_TOL_SUM_5 * 11/34 ≈ 38.82` — the descriptive, EXPLICITLY
SCALED sum bound (`GATE1_TOL_SUM_5`, 120, was set for a 34-rung
comparison; unscaled it would almost never fire over 11 rungs, which
is not a meaningful "the 12b replication tracks the referent" read).
Stays entirely NON-GATING — `_b6_12b_5`'s return value only reaches
`_s10_texture_5`'s `"b6_12b"` key, never `run()`'s own `failures`
(unchanged from before this fix; re-confirmed by reading the call
chain: `_s10_texture_5` → `secondaries_5`/S10, never `failures_5`).

`battery_5.tolerance_failures_5` gained the optional `rungs=` keyword
(chosen over a hand-written local subset comparison in `_b6_12b_5`, per
the ruling's own "or give tolerance_failures_5 an optional rungs=
argument" branch — keeps the per-rung/sum logic in one place). Default
`None` → all of `RUNGS` (34), sum bound `GATE1_TOL_SUM_5` unscaled —
byte-identical to the pre-fix function for every existing call site
(`gate1b_failures_5`, `gate1c_failures_5`, S9's `_s9_cross_host_5`),
none of which pass `rungs=`. When `rungs` names a proper subset, the
sum bound scales and the failure message names the scaling explicitly
(`"... (GATE1_TOL_SUM_5 scaled to {n}/{34} rungs)"`).

Existing mutant `(BAT5, "tolerance_failures_5: the per-rung tolerance
widened from > to >=", ...)` targets the line `"if d >
GATE1_TOL_PER_RUNG_5:"`, which is untouched verbatim by this edit
(confirmed by `grep` against the live file before re-running anything)
— no mutation-harness update needed; no other mutant in `tests/
mutation_check.py` targets `mac_interior_counts_5`/`tolerance_
failures_5`/`_b6_12b_5` (confirmed by grep, zero hits beyond the one
already-intact mutant).

**(c) Referent manifest / pin tables.** `make_referents_5.py`/
`referents_5.json`/`N_FILES_5` were already reconciled to the 11-rung
12b reality in Task 6 (Finding 1) — re-verified live: `referent_
files_5()` returns 1786, matching both `N_FILES_5` and the committed
`referents_5.json`'s own `n_files`, unchanged; `REFERENTS_5_SHA256`
does not need re-pinning. `battery_5.py`/`analyze_5.py` are both
`INSTRUMENT_BLOBS_5` (tag-bound, not tracked by `FROZEN_SHA256_5`/
`IMPORTED_SHA256_5`) — confirmed unchanged by re-running `import_
scan_5.py` and diffing its `FROZEN_SHA256_5` block against the
committed one programmatically: byte-identical (51 entries). `verify_
referents_5.py` DID change (item 8's docstring + `_c8` body, part (d)
below) and IS one of the six `IMPORTED_SHA256_5` entries — its hash
re-derived and re-pasted (`80696db1e843b7bfa37f362a7789e430452d000a4a
5e436fb370c75512bd3ae9`, was `366e0e92c9306cb2a270cc8ca06c1680ce85a7e8
d873298b8d330352314a801a`). Both `check_frozen_5()` and `check_
imports_5()` re-run cold after the fix: clean (`None`, no raise).

New pre-tag executions (real-tree `analyze_5.run()` calls), added to
the tally — **13 total now** (was 10 at the end of Task 6):
11. `import_scan_5.py`, run to inspect the fresh scan output before
    deciding what changed — `"5 host record"`.
12. `import_scan_5.py`, re-run to capture the full output to a
    scratchpad file for a programmatic diff against the committed
    tables — byte-identical to run 11 (confirms the scan is
    deterministic across invocations, as expected — no campaign state
    exists to vary it).
13. `read_sweep_5.py`, re-run after the `IMPORTED_SHA256_5` update —
    `"5 host record"`, 1853 distinct paths (unchanged from Task 6's
    count), 0 UNPINNED.

**(d) Tests.** Two new fast tests, both TDD'd against the real
committed 12b tree / a synthetic unit, both verified passing in
isolation before the full-suite run:
- `test_battery_5.py::test_mac_interior_counts_5_12b_is_eleven_rungs_
  others_stay_34` — `mac_interior_counts_5("12b", 1000)` returns
  exactly `GATE1_DESCRIPTIVE_12B_RUNGS_5` (11); `mac_interior_
  counts_5("6.9b", 64000)` still returns all 34.
- `test_analyze_5.py::test_b6_12b_5_compares_on_the_intersection_and_
  scales_the_sum_bound` — a synthetic 34-rung unit (`bt.RUNGS`) against
  a monkeypatched 11-rung referent: `n_rungs_compared == 11`, zero
  failures and zero diffs on a matched synthetic pair, `gate1_tol_
  sum_scaled` == `GATE1_TOL_SUM_5 * 11/34` exactly; a second case
  pushes one rung's count past `GATE1_TOL_PER_RUNG_5` and confirms the
  failure names that rung with NO spurious "count missing on one side"
  entries for the other 23.

`verify_referents_5.py` item 8: docstring and `_c8` both extended.
Item 8 now ALSO loads 12b's six `GATE1_DESCRIPTIVE_12B_5` steps and
asserts each equals exactly `GATE1_DESCRIPTIVE_12B_RUNGS_5` (11
rungs) — printed as "5 final referents + 15 interior referents (34
rungs each) + 6 12b descriptive steps (11 rungs each)". Re-run cold:
item 8 still `ok`; the battery is 11/13 + 2 legitimate SKIP, unchanged
in shape from Task 6.

**Commands + output (verification, this fix).**
```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp5/tests/ -m "not slow" -q
  → 103 passed, 13 deselected in 20.53s

PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp5/tests/ -m slow -q          # run detached, alone
  → 13 passed, 103 deselected in 149.65s (0:02:29)

PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m \
  experiments.exp5.verify_referents_5
  → referent battery: 11/13 (items 11, 13 SKIP; item 8 confirms the
    six 12b descriptive steps at 11 rungs each)
```
Fast suite: 103 passed (was 101; +2, exactly the two new tests above).
Slow suite: 13 passed (was reported as 11 in Task 6's own report — see
process note below), 0 failed either way.

**Process note (disclosed, not fixed — out of this fix's scope):**
running the WHOLE `experiments/exp5/tests/` directory in one pytest
invocation with no `-m` filter (a shortcut I tried before reverting to
the ruling's own "fast once / slow once, detached" instruction)
produces four spurious `test_power_5.py` failures (`KeyError:
'410m'`). Root cause: `test_determinism_5.py::_world` is a
module-scoped fixture that calls `pytest.MonkeyPatch()` directly (not
the function-scoped built-in) and never calls `.undo()` — its own
comment says so ("Never undone — this module never needs it reverted,
and the process exits with the test run"), an assumption that holds
only when the slow suite is its own process, as the established
convention (and this ruling's own instructions) always run it. In one
combined session, `full_shape_5.apply_shrink`'s `b5.SIZES_5` patch
(applied via that never-undone `MonkeyPatch()`) leaks past `test_
determinism_5.py` into every test file pytest collects afterward
alphabetically (`test_power_5.py`, `test_search_5.py`, ...), which is
what `test_power_5.py`'s hard-coded `"410m"`/`"antonym6"` fixture data
collided with. Not fixed here — the ruling's own instructions already
run fast and slow SEPARATELY (which sidesteps this entirely, confirmed
clean above), and "nothing else changes" governs this fix. Flagging
for whoever reviews `test_determinism_5.py` next: either give `_world`
a `request.addfinalizer(mp.undo)`, or add an explicit `pytestmark =
pytest.mark.slow` isolation note warning against combined invocation —
Michael's/the reviewer's call, methods-paper-lesson-candidate-adjacent
(test isolation assumptions are themselves a kind of unpinned
surface).

## Task 6 review fix round 1 (2026-09-22): item 7's network path + the determinism leak

Two Important findings from the whole-branch review; both fixed exactly as
ruled, nothing else touched (the three deferred minors — the 27/29 wording,
`make_referents_5.py`'s stale "6 × 35" docstring line, the totality test's
restore without try/finally — untouched, on the reviewer's own instruction).

**Finding 1: cold-battery item 7 could perform a real network download.**
`verify_referents_5._c7` already avoided a download for the val file
(`hf_hub_download(..., local_files_only=True)`), but its second half called
`slice_5.load_slice_tokenizer_5()`, which delegates to the FROZEN `models.
load_tokenizer` → `AutoTokenizer.from_pretrained(repo, revision=…)` with no
`local_files_only` at all — item 7 read "ok" only because the tokenizer
happened to already be cached on this Mac. Fixed without editing anything
frozen:
- `slice_5.load_slice_tokenizer_5` gained `local_files_only: bool = False`.
  `True` builds the tokenizer itself (`AutoTokenizer.from_pretrained(b5.
  REPO_OF_5[b5.TOKENIZER_SIZE_5], revision=b5.MAIN_SHA_5[b5.TOKENIZER_
  SIZE_5], local_files_only=True)`) and applies the SAME two settings 2b's
  loader applies (`padding_side = "left"`; `pad_token = eos_token` if unset)
  — verified these are exactly `models.load_tokenizer`'s own two lines
  (`experiments/exp2b/models.py:34-36`). `False` (the default) delegates to
  `models.load_tokenizer` exactly as before — the build path is byte-for-
  byte unchanged. Docstring states both paths must produce the same
  tokenizer (same repo, same revision, same two settings).
- `verify_referents_5._c7` now calls `sl5.load_slice_tokenizer_5(local_
  files_only=True)` and catches `OSError` only (checked live:
  `AutoTokenizer.from_pretrained(..., local_files_only=True)` on an uncached
  revision raises plain `OSError` — "We couldn't connect to
  'https://huggingface.co'..."; `huggingface_hub`'s own `LocalEntryNot
  FoundError` also subclasses `FileNotFoundError` → `OSError`, confirmed via
  `LocalEntryNotFoundError.__mro__`) — never a bare `except Exception`. The
  item's own module-header docstring and its `@check` one-liner both
  updated to say neither call reaches the network here.
- Two new fast tests: `test_slice_5.py::test_load_slice_tokenizer_5_
  local_files_only_never_reaches_the_network` (monkeypatches `transformers.
  AutoTokenizer.from_pretrained` with a recorder; asserts `local_files_
  only is True`, the exact repo/revision, and that `padding_side`/`pad_
  token` land correctly on a fake tokenizer object) and `test_load_slice_
  tokenizer_5_local_files_only_propagates_a_not_cached_oserror` (a raising
  fake confirms the OSError isn't swallowed inside `slice_5.py` itself).
  `test_verify_referents_5.py::test_c7_skips_rather_than_downloads_when_
  the_tokenizer_is_not_cached` drives `_c7` itself (val file faked as
  already-cached; the tokenizer call raises `OSError`) and asserts the
  result STARTS WITH "SKIP" and names the tokenizer, never raises.
  Re-ran the full cold battery live afterward: item 7 still `ok` (the real
  Mac cache has the tokenizer, so the `local_files_only=True` path finds it
  exactly as before — same re-derived 2,097,152 scored tokens).

**Finding 2: `test_determinism_5.py`'s module-scoped `MonkeyPatch` was never
undone.** Searched the whole `experiments/exp5/tests/` tree
(`grep -rn "pytest.MonkeyPatch()"` and `grep -rn "scope=\"module\"\|scope=
\"session\""`) — the ONLY other hit is the subprocess-side `pytest.
MonkeyPatch()` inside `_SCRIPT` (test_determinism_5.py line 39), which is a
genuinely separate one-shot interpreter that exits after printing its
verdict — that one's "never undone" comment is correct as written and was
left untouched. The `_world` fixture (module scope, parent process) is the
only leak. Fixed: `_world` now takes `request` and calls `request.
addfinalizer(mp.undo)` right after constructing `mp`, before `write_
world_5` uses it — `b5.SIZES_5`/etc. are reverted at module teardown
regardless of how the suite is invoked. Docstring updated to name the
review finding and the mechanism (`full_shape_5.apply_shrink`'s `SIZES_5`
patch leaking into every alphabetically-later file when the whole
directory runs in one process — the exact `test_power_5.py` `KeyError:
'410m'` collision disclosed in the Task 6 fix-round B-6 entry above).

**Verification.**
```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp5/tests/test_determinism_5.py -m slow -v
  → test_two_processes_agree PASSED (1 passed in 16.02s)

PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp5/ -p no:cacheprovider -q          # WHOLE directory,
                                                      # UNFILTERED, one process
  → 119 passed in 165.87s (0:02:45)                  # was 4 failed before
                                                      # this fix (test_power_5.py
                                                      # KeyError: '410m' x4)

PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest \
  experiments/exp5/tests/ -m "not slow" -q
  → 106 passed, 13 deselected in 20.45s              # was 103; +3 new tests

PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m \
  experiments.exp5.verify_referents_5
  → referent battery: 11/13 (items 11/13 legitimate SKIP; item 7 ok,
    real cached tokenizer found through local_files_only=True)
```
119 = 106 fast + 13 slow, self-consistent with the fast/slow split; no test
skipped, none failed, in EITHER the split or the combined invocation — the
combined run is now exactly as safe as the split one.

**Pin re-derivation.** `slice_5.py` is one of the thirteen `INSTRUMENT_
BLOBS_5` files (tag-bound, not tracked by `FROZEN_SHA256_5`/`IMPORTED_
SHA256_5`) — its change needs no re-pin. `verify_referents_5.py` (item 7's
`_c7` body + docstring changed) IS one of the six `IMPORTED_SHA256_5`
entries — re-derived and re-pasted (`c4a54a20274fb1993a815c94ffe7423fe349
f042d7c21ab78dbfcf81c036645b`, was `80696db1e843b7bfa37f362a7789e430452d0
00a4a5e436fb370c75512bd3ae9`). `test_determinism_5.py`/`test_slice_5.py`/
`test_verify_referents_5.py` are all under `tests/`, excluded from both
pin tables by construction (the scan walks `sys.modules` and drops
anything under a `tests/` directory). Re-ran `import_scan_5.py` once
(a counted pre-tag execution — **14 total now**, was 13 at the end of the
B-6 fix) and confirmed `FROZEN_SHA256_5` byte-identical (51 entries,
programmatic diff) while only `verify_referents_5.py`'s hash in `IMPORTED_
SHA256_5` changed. `check_frozen_5()`/`check_imports_5()` both re-run cold
after the re-pin: clean (`None`, no raise).

**Mutation harness:** confirmed unaffected by grep — no mutant in `tests/
mutation_check.py` targets `load_slice_tokenizer_5`, `_c7`, or the
`_world` fixture; no re-run needed.

**Final state after fix round 1.** Fast suite: **106 passed**, 13
deselected. Slow suite (run separately): **13 passed**. WHOLE directory,
unfiltered, one process: **119 passed, 0 failed** (the review's own
required check). Cold battery: **11/13 + 2 legitimate SKIP**, item 7 `ok`
via the real cached tokenizer through `local_files_only=True`. Import
scan: **0 unpinned** (51 frozen, 6 imported). Zero model contact, zero
network (item 7's two loads both served from the local cache, neither a
download; confirmed by the new tests that the code path CANNOT download
when `local_files_only=True` regardless of cache state), zero edits
outside `experiments/exp5/`.

## Task 7 step 1: the adversarial freeze (2026-09-22)

Fresh-eyes freezer on build HEAD `b31b8c585`; record in
`experiments/exp5/FREEZE_CHECKLIST.md`, report in
`.superpowers/sdd/2026-09-22-exp5-build/task-7-freeze-report.md`.
**The class defect was found (F-1):** `run/campaign_5.sh` runs
`sweep_5` for 160m last (S11 only), and `sweep_5.run` loaded the spine
for any size — eight 160m units no search, final or S11 names, which
gate 4 refuses: every verdict the production campaign could leave was
INSUFFICIENT_DATA. Six findings, all closed additively: F-1 `dc56e7011`
(spine and gate 1(c) for a large side only), F-2 `d5edbda67` (gate
1(a)'s flags re-derived from the record and tied to the 2.8b final
unit), F-3 `4b9db1148` (gate 0's stack pins enforced; `_checkpoint`/
`_unit` host fields compared), F-4 `c87fed60e` (loss finiteness
measured; a step directory that is not a complete unit refused), F-5
`464919eee` (a projection edited after its adding commit refused), F-6
`281d05e8d` (a dropped pair's record names why it dropped); mutants +
logs `b2bbd647b`. Nothing preregistered moved; `stats_5.py`,
`search_5.py`, `power_5.py` untouched.

Batteries after: fast 113, slow 13, cold battery 11/13 + 2 SKIP,
mutation 66 (36 fast / 30 slow / 0 equivalent / 0 unresolved), read
sweep 1853 paths / 0 UNPINNED, frozen/imported pins clean (51 / 6, no
re-pin — no pinned file changed).

**Pre-tag analyzer executions this session: 3 — the running total is
17 now (was 14):**
15. `tests/read_sweep_5.py` after the closures — `INSUFFICIENT_DATA — 5
    host record: ValueError: host record missing`; 1853 paths, 0
    UNPINNED.
16. `tests/read_sweep_5.py` again (the first invocation's filter had
    dropped the summary lines) — identical.
17. `tests/import_scan_5.py` after the closures — pin table tail equal to
    `IMPORTED_SHA256_5` (only the tail captured); pre-campaign `run()`
    refuses at "5 host record" by construction.
Every attack ran on tmp trees; no statistic was computed on the real
tree.

For the ruling (checklist §D, §F): B-3 (a runner halt on the first
non-finite unit loss; the preflight's early warning at step256, not
step1 — no window can load step1); the finals' `git_sha` not checked
against the prereg tag; the prefetch joins before scoring (no overlap,
the budget's assumption); ten design-doc slips.

## Task 7 step 1, the controller's rulings applied (2026-09-22)

- **B-3(a)**: the narrowing of gate 3's finiteness to spine + bisection
  units is a RATIFICATION SLIP for Michael (FREEZE_CHECKLIST §F slip 9,
  with the demonstration and the recommendation: narrow; window-only
  units carry `finite` as a disclosed field). The build keeps gate 3 as
  written.
- **F-7 `39d512925` (B-3(b))**: `run_unit_5` halts the size on the first
  non-finite unit loss — HALTED marker naming the unit and
  `n_nonfinite`, unit incomplete, checkpoint freed, exit 2.
- **B-3(c) `4487b5e22`**: the preflight's early warning loads 12b
  `step1000` and `step256` (the earliest window member), not `step1`;
  `run/preflight_5.py` re-pinned in `IMPORTED_SHA256_5` (`f32e8c36…`).
- **F-8 `86050f39f`**: `Prefetcher.target` / `.wait_for(size, step)`;
  `run_unit_5` joins only its own download, so the next step's download
  overlaps the current unit's scoring.
- **Finals' `git_sha` vs the tag's commit**: NOT added (ruling) —
  recorded as DISCLOSED in the checklist.
- Mutants for F-7/F-8; harness re-run `f8e590b18`: 68 considered, 43
  fast / 25 slow / 0 equivalent / 0 unresolved, worlds-only 30/30.

Batteries: fast 116, slow 13, cold battery 11/13 + 2 SKIP, pins clean
(51 / 6).

**Pre-tag analyzer executions: 18 now (was 17):**
18. `tests/import_scan_5.py` after the preflight re-pin — `pre-campaign
    run: INSUFFICIENT_DATA — 5 host record: ValueError: host record
    missing`; 51 frozen + 6 residual, table equal to the committed pins.

## Task 7 step 2: the final review's fix wave (2026-09-22)

The final whole-branch review (opus) read "Ready for the tag WITH FIXES", no
Critical; one fix wave, every item as the controller ruled (itemized with commits
in FREEZE_CHECKLIST §H): I-1 `7de480da5`; I-2/I-3/I-4/M-13 `d7a09dc01`; I-5
(additive) `3f524237a`; M-1/M-2/M-3/M-4/M-7/M-9 `bfc8a56e8`; M-5/M-6/M-10/M-11/M-12
`d843b319f`; the referent manifest rebuilt for M-5's power_5.py edit
(REFERENTS_5_SHA256 e7a1ea3b -> 314fc708) + four wave mutants `5c9e4d6d2`; I-5's
threshold, I-6 and M-8 are ratification slips 10, 9 (rewritten) and 11. A
mutation run started over the stale referent manifest was stopped with SIGINT
(finally restored the mutated file; no backup, tree clean) and re-run from the
corrected source.

Batteries: fast 137, slow 13, whole directory unfiltered 150, cold battery 11/13
+ 2 SKIP (item 7 ok), mutation 72 (47 fast / 25 slow / 0 equivalent / 0
unresolved; worlds-only 30/30), read sweep 1853 paths / 0 UNPINNED, import scan
51 + 6 equal to the pins (verify_referents_5 c7468181, make_referents_5 76d5d959,
preflight_5 f32e8c36).

**Pre-tag analyzer executions: 20 now (was 18):**
19. `tests/read_sweep_5.py` after the wave (M-1 removed a read) — `INSUFFICIENT_DATA
    — 5 host record: ValueError: host record missing`; 1853 paths, 0 UNPINNED.
20. `tests/import_scan_5.py` after the wave (three pinned files changed) — the same
    refusal; 51 frozen + 6 residual, table equal to the committed pins.
