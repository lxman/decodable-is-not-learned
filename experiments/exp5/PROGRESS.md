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

## 2026-09-22 — BUILD COMPLETE; RATIFICATION PACKAGE PRESENTED — awaiting Michael's ruling

Seven SDD tasks reviewed and closed (four fix rounds); the adversarial freeze found the class defect (F-1: the sweep runner loaded the smallest size's spine, which gate 4 refuses — every real campaign would have ended INSUFFICIENT_DATA) and closed F-1…F-8 additively; the final whole-branch review (opus) found no Critical, six Important, all fixed in one wave and re-reviewed clean. Batteries at HEAD: fast 137, slow 13, whole directory unfiltered 150, cold battery 11/13 + 2 pre-campaign SKIPs (item 7 PASS), mutation 72 (0 open, reproducible from the two logs), read sweep 0 unpinned, import surface 51 + 6 pins, referents 1,786 at 314fc708…; pre-tag analyzer executions on the real tree: 20 (the tally above). Zero model contact. The package for ratification — twelve design-doc slips (9: gate 3's finiteness clause and the ABSENT rule for a non-finite window member; 10: the UNDETERMINED threshold vs the rung-block flip's floor, recommended 7 rungs with a nonzero block sum; 11: the MATCHED licence's realized pair count), the plan's B-1…B-11 deltas, and the tag — is at `.superpowers/sdd/2026-09-22-exp5-build/ratification-package.md`. On his word: apply the slips, re-run the cold battery (counted), cut `exp5-preregistered` blob-bound over `INSTRUMENT_BLOBS_5`, push.

## 2026-09-23 — RATIFIED ("ratified — apply the slips and tag"); the slips applied; tag `exp5-preregistered` cut

Michael's ruling on the ratification package (`.superpowers/sdd/2026-09-22-exp5-build/ratification-package.md`): ratified as recommended — the twelve design-doc slips (FREEZE_CHECKLIST §F), the plan's B-1 … B-11 deltas, the tag. Applied in this order: the three substantive slips to the instrument test-first, the cold tools, the design doc, the cold battery, the commit, the tag.

**Slip 9 — gate 3's finiteness clause narrowed; a non-finite window member is ABSENT.**
- `search_5.plan_5(..., absent=())` / `replay_5(..., absent=())`: a loaded unit whose loss is not finite is passed as `absent`, never as a table entry (a step in both is refused). A window member in `absent` is dropped from its side — the plan's `b_minus`/`b_plus` list the PRESENT members, `absent` the dropped ones, `edge` counts the present ones (exactly the list-edge rule); the window `need` band skips absent members. A step the search would READ (spine or bisection) that is in `absent` is a fourth terminal status, `nonfinite` (`{"status", "step", "why"}`). The replay reveals absent steps in the runner's own order — a window member is listed as `(step, "window")` and then skipped; a read one ends the replay with `nonfinite` — and raises on a step requested twice (a planner-totality guard).
- `battery_5.loss_is_finite_5(rec)` — MEASURED finiteness (the aggregate a finite float, every per-set component with tokens finite; never the attested flag, F-4). `loss_record_failures_5(..., require_finite=True)`: with `require_finite=False` a CONSISTENT non-finite record passes every other check; an attestation that disagrees with the measurement is refused either way (the F-4 refusal, kept). `loss_table_entry_5(rec)` — ONE construction for the runner's loss table and the analyzer's rebuilt one: a non-finite row is `loss: null, finite: false, per_set: null` (NaN is not an equality-safe JSON value; gate 4 compares the two tables).
- `collect_5.run_unit_5`: the F-7 halt narrowed to `HALT_ON_NONFINITE_WHY_5 = ("spine", "bisect", "final")` on the MEASURED value; any other unit (window, S11, the preflight's, S9's) is written whole and marked — `_unit.json` gains `finite` and `n_nonfinite`, a `[5] NONFINITE (...)` line is printed, the return dict carries `finite` (`reused` too).
- `run/sweep_5.py`: `_losses_of` returns `(losses, absent)` by the measured value; `request()` returns the unit dict, stamps `finite` on the request event and appends `{step, why, pair, n_nonfinite}` to the log's new `nonfinite` list (the marker; printed); the search loop feeds a non-finite unit to `absent`, and HALTS (exit 2, HALTED marker naming the step, its kind and the pair) on `plan_5`'s `nonfinite` status — the case of a unit written whole as a window member that a LATER pair's bisection would read; `requested_all` replays with the same `absent`; S11's log row carries `finite`; the dry run prints the non-finite set.
- `analyze_5.py`: `load_units_5` applies the loss contract with `require_finite=False`, keeps a non-finite step OUT of `losses` and IN a new `nonfinite` map (`{step: {why, n_nonfinite}}`), and refuses a non-finite FINAL at load (a target and a spine point); the replay (gate 4), `expected_steps_5` and `_dropped_detail_5` pass the size's `absent`; a `nonfinite` replay status is a gate-3 failure naming the step and its kind; the logged plan's `absent` is compared to the replay's; the window-completeness check covers the absent members (they exist as units); the loss table is rebuilt through `loss_table_entry_5`; `_s11_stability_5` prints a non-finite S11 unit as absent and never reads it; S10 gains `nonfinite_units`; gate 4's total gains `window_members_absent`; the verdict dict gains `cells` (the per-cell table, so a reader can see which steps each read used) and VERDICT.txt prints the absent members.
- Preflight and S9 are untouched (their units never halt; the preflight's `step256` check stays the early warning); `power_5.py` untouched (it reads finals only).

**Slip 10 — the UNDETERMINED threshold.** `battery_5.MIN_LIVE_RUNGS_5 = 5` (rungs carrying cells) REPLACED by `MIN_NONZERO_BLOCKS_5 = 7` (rungs with a NONZERO block sum — the flip's support; 2^-7 = .0078 < α); `stats_5.tree_5` reads `primary["n_nonzero_blocks"]` and its reason names both counts and the floor; I-5's `p_min_attainable` / `resolution_note` kept as the check behind it. `MIN_LIVE_CELLS_5 = 20` unchanged.

**Slip 11 — the MATCHED licence's pair count.** `analyze_5.licence_block_5(..., pairs=None)`: the MATCHED-POWERED body is a template — "across {n} size pair(s) to {r}×" — filled from gate 4's KEPT pairs with the largest realized ratio n_params(large)/n_params(small) from the checkpoint records (an unrecorded n_params prints as such); the block carries `pairs_realized` and `largest_ratio_realized`; VERDICT.txt prints both.

Slips 1–8, 12 and B-1 … B-11: applied to `experiment-5-design.md` verbatim per §F (the second drop kind; the window's lower edge and `step256` in §3.1/§3.2/§7; gate 3's "scored twice" replaced by the write-once rule; the targets seal's exact file set, cut after the power record; gate 1(a)'s per-document rounding and re-derived flags; gate 5's git-ancestry check and the unedited projection; the stack pins' versions; the budget's B-4 correction and F-8's overlap; the 160m "S11 alone" sentence; B-2's exact 2^21; B-5's power parameters; B-6's 12b descriptive; B-8's batch pins; B-10's second Hub read and the build's downloads; B-11's LR schedule); §3.8 (slip 10), §6 (slip 11), §3.7 gate 3 (slip 9); a record pointer in §11; the status block and the §2 execution count at the tag.

Tests first (the RED step run before each implementation): `test_search_5` +3 (an absent window member shortens its side and is named — incl. the realistic whole-side case, B⁻ = {256, 512} at t_lo = 1000; an absent read step returns `nonfinite`; the replay records an absent window member and stops on a read one), `test_stats_5` (the tree on `n_nonzero_blocks` at the 7/6 boundary; +1 on real cells: eight rungs carrying, two summing to zero → UNDETERMINED, seven nonzero → not), `test_battery_5` (+1: measured finiteness, `require_finite=False`, the attested/measured disagreement, the table entry), `test_stages_5` +4 (a window member written, marked and absent through the production sweep, then the analyzer on that tree; a unit written as a window member that a later bisection reads halts; a non-finite final halts through `finals_5`; `load_units_5` refuses a non-finite final), `test_full_shape_5` (+1 world through the PRODUCTION runner with `nonfinite_at` on a window-only member of the last partner: verdict MATCHED as the clean world's, zero refusals, the member absent in the plan, S10, gate 4 and every cell; the F-4 sub-case now reads the attested-vs-measured refusal; +2 sub-cases: a consistent non-finite BISECT unit and SPINE unit each refuse with gate 3's message), `test_analyze_5` +2 (the licence's realized pairs; S11 absent). Fakes: `fakes_5.make_loaders(nonfinite_at=)`, `full_shape_5.write_world_5(nonfinite_at=)`.

Mutation harness: three pre-existing mutants re-targeted to the changed text (the write-order mutant's unit record; F-4's measured check now on `loss_is_finite_5`; F-7's halt on the narrowed condition); +19 slip mutants (10's constant and the tree's count; 9's spine/bisect `nonfinite` returns, both sides' shortening, the both-tables refusal, the halt's narrowing, `_losses_of`'s table, the sweep's `nonfinite` halt, `load_units_5`'s `losses`, the final's refusal, the replay's gate-3 failure, `expected_steps_5`'s absent set, S11's skip, the measured helper's per-set loop, the table entry's raw NaN, the attested/measured refusal; 11's nominal pairs).

**Batteries after the slips (every run on the real repo tree, the worlds on tmp trees):** fast **148** (was 137; +11 new), slow **14** (was 13; +1 world), whole directory unfiltered one process **162** (was 150); mutation **91 mutants** (was 72): the fast pass on the slip-applied source **64 killed by the fast suite directly + 27 by the slow suite (each re-confirmed via `--worlds-only`), 0 equivalent, 0 unresolved, 0 skip, 0 timeout** (a first fast pass on the same source reported the two world-only slip labels as unresolved before they were registered in `NON_FAST_KILLS_5`; the committed log is the re-run after the worlds pass); the worlds-only pass **32/32 killed, 0 open, 0 errors** (the 28 totality labels + F-4's torn directory + the orphan unit as before; the two slip labels the fast pass could not observe — the analyzer-side gate-3 refusal, #57, and the licence's kept-pairs count, #60 — each survived the totality file and was KILLED by the full-shape file, by exactly the test registered for it in `NON_FAST_KILLS_5`: `test_refusal_routes_deliver_insufficient_data` and `test_a_non_finite_window_member_is_absent_and_the_verdict_stands`) — both logs regenerated from the current source; read sweep **1853 distinct paths (1952 reads), 0 UNPINNED**; import scan **51 frozen + 6 residual, the printed tables equal to the committed pins** (no `IMPORTED_SHA256_5` / `FROZEN_SHA256_5` file changed — the slips touched blob-bound modules only — so no re-pin; the referent manifest lists `power_5.py` alone among the instrument modules and it is untouched, so `REFERENTS_5_SHA256` stands at 314fc708…); cold battery **11/13 + 2 pre-campaign SKIPs** (items 11/13 need the targets stage / a gate-1 record; item 7 PASS — the slice re-derived from the cached pinned file) (the last pre-tag check).

**Pre-tag analyzer executions: 22 now (was 20):**
21. `tests/read_sweep_5.py` after the slips — `pre-campaign run (NOT the experiment's verdict): INSUFFICIENT_DATA — 5 host record: ValueError: host record missing`; 1853 distinct paths, 0 UNPINNED.
22. `tests/import_scan_5.py` after the slips — `pre-campaign run: INSUFFICIENT_DATA — 5 host record: ValueError: host record missing`; 51 frozen + 6 residual, equal to the committed pins.
The cold battery (`verify_referents_5.py`) calls the gate functions, never `run()`, and is not a tally item.

After the harness runs, one wording fix in `stats_5.tree_5`'s UNDETERMINED reason (the p-floor clause printed only when the nonzero-block count is the cause; no mutant target touched, verified; the whole directory re-run: 162 passed).

**The tag.** `exp5-preregistered` cut at the commit that carries this entry (the sha is in the tag's own message and in CLAUDE.md's entry) (annotated), blob-bound over the thirteen `INSTRUMENT_BLOBS_5`, the binding verified through `battery_5.require_prereg_5` against real git, pushed with the commit. Zero model contact end to end; the pre-committed change UNSPENT. Next, each stage on Michael's word: the box → preflight → finals → `exp5-targets-sealed` → projection → sweep → S9 → the analyzer once.

## 2026-09-23 — STAGE 0 (preflight) ON A RENTED 40 GB A100 — the box, the route, the launch

**The ruling.** Michael, on "proceed" after the tag: the box and the preflight. The Vast on-demand market that morning held two A100 80 GB hosts with ≥ 500 Mbps: one with 11 GB of disk (unusable for 24 GB checkpoints) and one at **$1.69/h** (North Carolina, 588 GB, 5 Gbps, 98.3 %) — above the design's $1.06/h figure. Asked whether the preflight and the campaign must share a machine: **no** — the preflight writes nothing under `results/`, checks no tag and prints only; what it establishes (fp16 finiteness of 12b at `step256`/`step1000`, the per-unit peak, the double-run identity) is a property of the host CLASS, and the campaign's own gates re-establish every host fact on the campaign box (gate 0 writes the host record where the finals run; gate 1(a) is the identity check there). What IS bound to one box is the finals plus the whole sweep (gate 0 compares every unit's stack, device and host-record hash to the record the finals wrote; the sweep runner re-uses that record and checks the stack pins and the device). **Ruled ("go"): the preflight now on a cheap 40 GB A100; the campaign later on an 80 GB host nearer $1.00/h.** This departs from §7 stage 0's letter ("Preflight on the host") — a run-plan deviation, disclosed here and in the design's status block; no preregistered statistic moves, the pre-committed change untouched. If the 12b unit does not fit in 40 GB, the peak read is left to the campaign box.

**The box.** Instance **52232335** (label `exp5-preflight`), offer 52067516: **A100-SXM4-40GB** (driver 595.91.07, CUDA 13.2), 192 cores, 503 GB RAM, 80 GB disk requested, California, **$0.43/h**, reliability 95.9 %, advertised ↓1074 ↑382 Mbps; image `vastai/pytorch`, ssh only; created 12:57 UTC by the MCP (the first `create_instance` — for the $1.69 host — was refused by the harness's transaction classifier; the second, after the ruling, went through). Route: the proxy `ssh6.vast.ai:32334` from the Mac's own ssh with the program's key (the MCP's ssh client failed the banner on both ports; port 32335 resets; the direct IP 38.255.16.69:21800 rejects the key, as on 4c's box). Python 3.10.12 on the image → a uv-managed **3.11** venv at `/workspace/venv` with the Mac's pins: **torch 2.12.1+cu130, transformers 5.13.0, numpy 2.4.6, safetensors 0.8.0, tokenizers 0.22.2, huggingface_hub 1.22.0 (hf_xet present), scipy 1.17.1** (`stack_5.sh` = the stack half of `run/box_setup_5.sh`, run first so it overlapped the transfer).

**The route failed for the bundle — disclosed.** `run/make_bundle_5.sh` built the 518 MB bundle (sha256 `0438bb37…`, every ref, the tag). Every push through the proxy died within seconds with "connection closed by remote host": scp at 522 KB; rsync `--partial --append` at 4.3 MB over several attempts (the Mac's openrsync has no `--append-verify`); 33 chunks of 16 MB with per-chunk retries landed nothing at all, and the hundreds of short sessions that loop opened then made even listings fail for a while. Streams FROM the box were fine throughout (pip at full speed). So the box pulled the repo itself: a key pair generated ON the box (the private half never left it), its public half registered on the private repo as a **read-only, repo-scoped deploy key** (id 164200447, 13:13 UTC — the mechanism the rented-host rule names; 4c's bundle route puts no credential on the host and was tried first), a full clone over ssh port 22 that crawled at ≈ 40 KB/s (GitHub over HTTPS measured 0.8 MB/s from this host, Hugging Face 9 MB/s — far under the advertised gigabit), then a **shallow clone (`--depth 2`) over GitHub's ssh port 443** with the same key, ≈ 5 min: **HEAD f03811a8d, tag object dc42d54e, tag commit b3745a72a — equal to the Mac's**. The deploy key was DELETED from the repo the moment the hashes matched (0 keys remain) and the private half removed from the box; the port-22 clone killed. `git status` clean; `check_frozen_5` / `check_imports_5` clean; **`require_prereg_5` on the box's real git: `exp5-preregistered` bound, 13 blobs.**

**The gate and the launch.** `finals_5 --dry-run --device cuda` on the box: `prereg 'exp5-preregistered'; host record pending; gate 1(a) pending; would run 7 final(s)` (the tag verified inside the runner). **Preflight launched 13:36:50 UTC** as pid 2221 (`setsid nohup … preflight_5 --device cuda`, log `/workspace/preflight_5.log`, xet ON), monitored from the Mac. Spend so far ≈ $0.30.

**Lessons for the campaign box (process notes, Michael's call):** filter on the 99.8 %-reliability hosts; test a sustained upload through the proxy before relying on it; the deploy-key clone over port 443 is the fallback when the proxy will not carry a bundle; `pkill -f` self-matches a remote command line that names the target file anywhere in it — kill by pid, in its own call.

**Stage 0 on the 40 GB box — what it delivered, what it could not (2026-09-23, 13:36–13:55 UTC).**
- **Transports (measured by the preflight on the 160m file, xet ON):** classic **5.6 MB/s**, xet **22.2 MB/s** — an order of magnitude under 4c's Japan host (237–355 MB/s xet) and far under this host's advertised gigabit. The campaign box must be chosen on a MEASURED transport, not the listing.
- **12b: the loss forward does not fit in 40 GB.** `slice_loss_5` at 12b `step1000` raised `torch.OutOfMemoryError` on a 640 MiB allocation with 39.14 GiB in use (34.61 allocated + 4.04 reserved) at the fp16 logits of the [8, 2048, 50304] batch (`slice_5.py:262`), after the 24 GB of weights had loaded; the checkpoint was freed in `finally`, nothing written (`experiments/exp5/box-preflight-52232335-12b-oom.log`, machine-local). So the 12b unit's peak is **> 39.5 GiB on this stack at the pinned batch** — the design's 80 GB class is required, as assumed; **the 12b `step256`/`step1000` finiteness read and the per-unit peak remain for the 80 GB box** and are run there BEFORE the finals (the preflight's own 12b loop; ≈ 40 min at a decent transport).
- **The identity read: the 1b final loaded TWICE on A100 CUDA — IDENTICAL** (`_loss.json` loss repr and per-document means, every rung's bits and continuations, the checkpoint digest), through the pinned module's own `run()` with `probe_steps=()` and the measured transports passed back (`/workspace/preflight_1b_5.py`, a nine-line caller; `box-preflight-52232335-1b-identity.log`). "complete: nothing written under results/" — confirmed on the box (no `results/` directory exists; cache freed to 1.5 MB; GPU 0 MiB).
- Spend on the box ≈ $0.45 to this point. The box is left running pending Michael's word to destroy it (its remaining use is nil: every outstanding stage-0 read needs 80 GB). The 80 GB market at 13:45 UTC: one host — offer 49067596, A100 SXM4 80 GB, Texas, **$1.48/h**, 99.6 %, 608 GB disk, ↓9 Gbps advertised — recommended for the 12b preflight reads and, on his word, the finals + sweep on the same box (one host record, as gate 0 wants).

## 2026-09-23 — the preflight box destroyed; THE CAMPAIGN BOX (52266306, A100 SXM4 80 GB, Germany, $0.68/h all-in); stage 0 re-run there in full

**The ruling.** Michael: "Destroy the preflight box and start the campaign." Instance 52232335 (the 40 GB preflight box) destroyed at 16:55 UTC; both of its logs were already on the Mac (`box-preflight-52232335-{12b-oom,1b-identity}.log`, machine-local), nothing else on it was wanted. Spend on it ≈ $0.90 over ≈ 2 h.

**The box hunt — one false start, disclosed.** The first campaign box was created on the Texas A100 SXM4 80 GB host the previous entry had recommended (instance 52265449, offer 47239982, $1.31/h base) and DESTROYED eleven minutes later without ever being started or connected to: reading the instance's full cost record showed its download charge at **$0.039/GB** and storage at $1.00/GB-month — ≈ $117 for the campaign's ≈ 3 TB stream and $0.44/h for 320 GB of disk, against the design's ≈ $0.009/GB budget line. The MCP's offer listing prints neither figure; the 80 GB market was re-read through the API with both columns (the query and its output are in the session's scratch, not committed). Chosen: **offer 47550487 — A100-SXM4-80GB, Germany, $0.600/h base, storage $0.20/GB-month, download $0.0013/GB (≈ $4 for 3 TB), reliability 99.0 %, 48 cores / 251 GB RAM, advertised ↓779 ↑492 Mbps** — instance **52266306** (label `exp5-campaign`, image `vastai/pytorch`, ssh only, 300 GB disk), created 17:06 UTC, **$0.683/h all-in**; route `ssh6.vast.ai:26306` with the program's key (the proxy; the MCP's own ssh client was not used). Driver 595.84, CUDA 13.2 on the image, Python 3.10.12 → the uv-managed 3.11 venv at `/workspace/venv` with the Mac's pins (torch 2.12.1+cu130, transformers 5.13.0, numpy 2.4.6, safetensors 0.8.0, tokenizers 0.22.2, huggingface_hub 1.22.0 with hf_xet, scipy 1.17.1 — `stack_5.sh`, the stack half of `run/box_setup_5.sh` verbatim, run first so it overlapped the transfer). Credit before the campaign: $176.32.

**The route carried the bundle this time.** `run/make_bundle_5.sh` → 543,460,321 bytes, sha256 `3aa4fe48…`; scp through the proxy at ≈ 3.1 MB/s, 2 min 56 s, exit 0; **sha256 on the box equal**. `git clone` from the bundle (the clone half of `box_setup_5.sh`): HEAD **d3632e115** (= the Mac's), tag `exp5-preregistered` → object dc42d54e → commit b3745a72a, tree clean; `check_frozen_5` clean; **`require_prereg_5` on the box's real git: bound, 13 blobs, the shas equal to the Mac's**. No credential on the host (4c's bundle route, as the rented-host rule wants; the deploy-key fallback was not needed). `finals_5 --dry-run --device cuda`: `prereg 'exp5-preregistered'; host record pending; gate 1(a) pending; would run 7 final(s): ['2.8b', '12b', '6.9b', '1.4b', '1b', '410m', '160m']`.

**Stage 0 re-run IN FULL on the campaign box** (the letter of §7 stage 0 — "on the host" — restored for the identity read as well as the 12b reads; the 40 GB box's stage-0 record stands as what it was, a host-class read): `preflight_5 --device cuda` launched **17:17:08 UTC**, pid 1102 (`setsid nohup`, log `/workspace/preflight_5.log`, xet ON). Transports on this host, the preflight's own measurement on the 160m file: **classic 33.0 / xet 24.0 MB/s** — but the small file understates the host: the 12b `step1000` download measured **≈ 83 MB/s sustained** (2.48 GB in 30 s by cache growth), so a 24 GB checkpoint lands in ≈ 5 min, under a 12b unit's scoring time; the runner's prefetch (F-8) should hide most of the stream. Results below as they land.

**The German box was THERMALLY THROTTLED — destroyed; stage 0 aborted there, nothing written.** The preflight's 12b `step1000` read completed on it (digest `45027001…`, n_params 11,846,072,320, **loss finite, n_nonfinite 0, loss 3.70880, peak 37,829,866,496 bytes (35.2 GiB) with the loss batch resident**, antonym 0/500 in 45.0 s) — but the loss forward had taken ≈ 54 min against the design's ≈ 8 min per whole 12b unit, and the `step256` forward had been running an hour with no line. `nvidia-smi` at 19:22 UTC: **SM clock 210 MHz of 1,410, `SW Thermal Slowdown: Active`, 86 °C, power 123 W at "100 %" utilization; the event counters showed 105,779 s (29 h) of SW thermal slowdown and 867 s of HW thermal slowdown accumulated on that GPU** — a host whose cooling cannot hold the part at clock; idle after the kill it still sat at 210 MHz at 78 °C. The preflight was killed at 19:23 UTC (pid 1102; no `results/` directory existed, tree clean), its partial log and the `nvidia-smi` record copied to the Mac (`box-preflight-52266306-partial.log`, `box-thermal-52266306.log`, machine-local), instance 52266306 destroyed at 19:24 UTC. Spend on it ≈ $1.60 over 2 h 18 min. Its `step1000` numbers above are a host read, not a record — stage 0 is re-run whole on the next box. **Process note (Michael's call): a rented host is screened UNDER LOAD before anything is installed on it** — `run/thermal_screen_5.py` (added this session, 120 s of fp16 matmul on the image's own torch, SM clock / temperature / throttle flags every 10 s) — the listing's reliability figure (99.0 %) said nothing about it.

**The campaign box, second attempt: instance 52285720 — A100 80GB PCIe, Oklahoma, offer 47195598** ($0.867/h base, storage $0.60/GB-month, download $0.0026/GB ≈ $8 for 3 TB, reliability 99.8 %, advertised ↓698 Mbps, 32 cores visible / 8 effective, 503 GB RAM, driver 580.126.09, 260 GB disk requested; **$1.08/h all-in**), created 19:27 UTC, route `ssh2.vast.ai:15720`. The A100 80 GB on-demand market at that hour with ≥ 250 GB disk and ≥ 400 Mbps: the throttled German host, this one, and a North Carolina SXM4 at $1.61/h + $0.0133/GB (≈ $40 for the stream) — the H100 class ($1.79–2.07/h at $0.0013/GB) was NOT taken, to keep the host class the design's dial (a) ruled and gate 1(b)'s cross-host tolerance meaningful (it was pinned from an A100). **Thermal screen PASS: 231 TFLOP/s fp16 sustained over 120 s, 37–38 °C, SM 1,110–1,125 MHz under the PCIe part's 300 W power cap, thermal slowdown Not Active throughout** (`box-thermal-52285720.log`). Stack (`stack_5.sh`) and the bundle (the same 543,460,321-byte file, sha256 `3aa4fe48…`) then went to the box; what follows is below.

**Stage 0 on the campaign box — PASSED (19:29:08 → 20:09:57 UTC, 41 min; `box-preflight-52285720.log`, machine-local).** The bundle went through this host's proxy at ≈ 26 MB/s (20 s); clone HEAD **d3632e115**, tag object dc42d54e → b3745a72a, `require_prereg_5` bound 13 blobs on the box's real git; `finals_5 --dry-run`: would run 7 finals. The preflight, whole: **transports classic 45.2 / xet 80.1 MB/s** (the 160m file); **12b `step1000`: digest `45027001…`, n_params 11,846,072,320, loss finite, n_nonfinite 0, loss 3.70880, peak 37,829,866,496 bytes (35.2 GiB) with the loss batch resident, antonym 0/500 in 14.0 s** (45.0 s on the throttled host — the same digest, loss and peak there, so the read is host-independent and only the clock differed); **12b `step256`: digest `8c7b9a99…`, loss finite, n_nonfinite 0, loss 6.22460, peak 61,524,109,312 bytes (57.3 GiB — the second load's peak carries the caching allocator's retained pool from the first, 4c note 3; it fits the 80 GB part with 22 GB to spare), antonym 0/500 in 14.3 s**; **the 1b final loaded TWICE: IDENTICAL**; `complete: nothing written under results/`. Gate 3's early warning (B-3(c)) is clear: the earliest window member any pair can reach is finite at 12b in fp16 on this stack.

**STAGE 1 LAUNCHED — the finals.** `finals_5 --device cuda` on the box at **20:10:29 UTC**, pid 3504 (`setsid nohup`, log `/workspace/campaign_5.log`, pid file `/workspace/campaign_5.pid`, xet ON; box HEAD d3632e115 — the Mac is two ledger-only commits ahead, the thirteen bound blobs identical). The runner writes gate 0's host record first, then gate 1(a), then the seven finals in `FINALS_ORDER_5` (2.8b, 12b, 6.9b, 1.4b, 1b, 410m, 160m), gate 1(b), the loss table. Mac side (`Popen(start_new_session=True)`, the harness-safe form): the puller (`run/pull_units_5.sh`, complete units + the top-level records, every 120 s), the commit watcher (`run/commit_watcher_5.sh`) and the 5-min status logger (`run/status_box_5.sh`) started 20:10 UTC against `ssh2.vast.ai:15720`; logs gitignored under `experiments/exp5/`.

## 2026-09-23 — STAGE 1 COMPLETE: seven finals, gates 1(a)/(b) PASS, landed + committed; power ONCE → DECLARED UNDERPOWERED IN ADVANCE; tag `exp5-targets-sealed`

**The finals on the box (20:10:29 → 21:15:35 UTC, 65 min, zero halts, zero stops).** Gate 0's host record written first (`results/host_5.json`: the stack pins, `cuda`, A100 80GB PCIe, transports classic 45.2 / xet 80.1 MB/s, xet used). **Gate 1(a) PASS** — the 2.8b final through 2c's `main` loader and the candidate-file `step143000` loader: digests equal, **0 continuation diffs on all 34 rungs × 500 items compared, the slice loss equal by `repr` and 0 per-document diffs**. The seven finals in `FINALS_ORDER_5` (2.8b, 12b, 6.9b, 1.4b, 1b, 410m, 160m), 37 files each. **Gate 1(b) PASS on every size with a Mac referent** against the tolerance (per rung ≤ 15, Σ ≤ 120): **410m Σ|Δ| 19 / max 6; 1b 12 / 3; 2.8b 27 / 4; 6.9b 57 / 8; 12b 31 / 7** — the 6.9b figures are the A100 benchmark's own 57 / 8 exactly (the same host class flips the same near-ties); 160m and 1.4b have no referent, disclosed. The loss table's seven rows (ℓ at the final): **160m 2.48962, 410m 2.12913, 1b 1.99513, 1.4b 1.91883, 2.8b 1.82023, 6.9b 1.75215, 12b 1.70396** — monotone in size, all finite; the six small-side targets are the first six.

**Landing.** The puller copied every unit once its 37 files were complete and the four top-level records after `[5 finals] complete`; the watcher committed and pushed each unit as it settled (six watcher commits, 37 + 37 + 37 + 37 + 37 + 39 files, the last carrying gate 1(b), the loss table and the re-pulled host record); `git status` clean under `results/` at 21:17 UTC. The watcher was then stopped (nothing lands until the sweep; the power record and the projection are hand commits — 4c's "no hand commits over a live watcher"). Cold battery on the landed tree: **12/13** (item 11 SKIP before the targets stage; **item 13 reads gate 1(a)/(b) with zero failures**; item 7 PASS from the cached slice file).

**The finals under 2d's bar (this host's reads; the small-side statuses the power record simulates as real):** 160m clears nothing; 410m antonym6 (111); 1b arith_next (19); 1.4b antonym (158), arith_next (38); 2.8b seven — add3_mid 44, add_base8 45, antonym 275, antonym6 148, arith_next 135, sub3_mid 264, sub_base8 92; 6.9b nine — those minus nothing plus count_div13 103 and odd6 108 (sub3_mid 16 clears at a .014 floor); 12b nine — add3_mid 26, add_base8 49, antonym 280, antonym6 206, arith_next 77, count_div13 100, median5 128, sub4_mid 13, sub_base8 83. Two finals the program had never read: **160m** (antonym 60, antonym6 77, count_div13 58, odd_one_out 108 — nothing over its floor) and **1.4b** (antonym 158 and arith_next 38 clear; **count_div13 = 4** against 58 / 74 / 77 at the three smaller finals and 58 / 103 / 100 at the three larger — the checkpoint-local-collapse shape 2h found mid-training, here at a size's FINAL; S11's `step142000` read will say whether it is the final alone).

**Power ONCE (21:18 UTC, 77 s, `results/power_5.json`, finals sha `dc7fbace…`): DECLARED UNDERPOWERED IN ADVANCE.** n_live_simulated **38 cells over 9 rungs** (add3_mid, add_base8, antonym, antonym6, arith_next, count_div13, odd6, sub3_mid, sub_base8; by small side 410m 5, 1b 4, 1.4b 6, 2.8b 14, 6.9b 9), σ_read 15.07 items at noise ×1, drift 4.0. **The deciding arm (spread, ×1, D .05, q ½): P(NOT-MATCHED) = .173** against the bar .75; ×½: .657; the concentrated-on-option arm .000 / .000; realized α .000 / .000; null T −.0078 ± .0020 (×1), −.0051 ± .0012 (×½); D grid at ×1 (its own draw): .01 → .000, .02 → .000, .03 → .001, .04 → .027, .05 → .159, .06 → .364; **min detectable T at .75: none on the grid** (`null`). The reason is arithmetic the design stated: the 25-item offset on half of 38 cells at a per-read SD of 15 items lands inside the design-stage envelope's "noise 15" column (.32–.52 there at 45–66 cells; 38 here). Dial (a) governs: **run, with the declaration printed**; §6's MATCHED sentence is "not distinguishable at this resolution" and nothing more; NOT-MATCHED, if it fires, fires at α .01 regardless. The realized live set will be larger than the simulated one (cells live only through the large side are not simulated) — printed beside it in the verdict.

**Tag `exp5-targets-sealed`** cut at 91d0c3114 (annotated object 40b0ba37, the commit that carries the power record), **`require_targets_seal_5`: 263 paths bound, zero failures**; master and the tag pushed. **Projection SEALED at `experiments/exp5/projection.md`** in the commit after the tag, before any sweep unit (gate 5's ancestry check): THE CALL is **NOT-MATCHED · MIXED (.40)** with LARGE-AHEAD the close alternative (.32); NOT-MATCHED in total .80, MATCHED .08 (read under UNDERPOWERED), UNDETERMINED .02, INSUFFICIENT_DATA .10 (gate 1(c) on an interior 2.8b/6.9b checkpoint the likeliest route); **T ≈ .08 [.04, .16]**, p ≈ .003, 21 pairs kept, ≈ 55 live cells [40, 75]; the designer's prior stated as a claim with two disconfirmers (T over cells outside the 2.8b row and the antonym rungs ≥ .06; the 2.8b row's mean c ≤ .04); per row, per type, per pair and per secondary with tolerances both ways; the sharpest single call S11's 1.4b count_div13 ≥ 40 at `step142000` (its final's 4 a checkpoint-local collapse). Budget ≈ 22 h [18, 30], ≈ $32.

**Post-seal cold tools (2i's lesson — after each stage lands):** `verify_referents_5.py` **13/13** (item 11 now runs: `power_5.json` reproduces byte for byte; item 13 gate 1(a)/(b) zero failures); `tests/read_sweep_5.py` executed on the real tree (pre-campaign analyzer execution **#23**; the capture kept only its tail, so it was run once more with the full output kept — **#24**, summary in the next entry).

## 2026-09-23 — STAGE 2 LAUNCHED: the sweep, 12b first

The Mac's stage-2 bundle (`run/make_bundle_5.sh` at ee4268008, sha256 `25ae8e38…`) through the proxy (≈ 20 s), equal on the box; **`run/rebundle_box_5.sh`: HEAD ee4268008 (= the Mac's), `exp5-targets-sealed` present, the projection's adding commit ee4268008 an ancestor of HEAD, both tags listed, tree clean.** `sweep_5 --size 12b --dry-run --device cuda`: `prereg 'exp5-preregistered'; spine (1000, 2000, 4000, 8000, 16000, 32000, 64000, 100000, 143000); partners ['160m', '410m', '1b', '1.4b', '2.8b', '6.9b']; units complete [143000]; non-finite []; gate 1(c) n/a`. **`run/campaign_5.sh` launched 21:27:36 UTC** (`setsid nohup`, bash pid 9514 in `/workspace/campaign_5.pid`, `sweep_5 --size 12b --device cuda` pid 9516, log appended to `/workspace/campaign_5.log`, xet ON; sizes 12b → 6.9b → 2.8b → 1.4b → 1b → 410m → 160m, largest first per dial i, stop at the first non-zero exit). Mac side: the commit watcher restarted (the puller and the 5-min status logger had stayed up). Every unit is watcher-committed as it lands; the projection (ee4268008) precedes every sweep unit's `git_sha` by construction of the rebundle. Expected ≈ 22 h [18, 30]; the analyzer runs once, on Michael's word, after S9 on the Mac and the cold battery's item 7.

**The post-seal read sweep (executions #23 and #24, the second with the full output kept at `read_sweep_post_seal.log`, machine-local):** `pre-campaign run (NOT the experiment's verdict): INSUFFICIENT_DATA — 5 spine 410m: ValueError: 410m: spine step(s) missing from the committed units` (the refusal now sits one gate later than before the finals — at the spine, not the host record); 2,117 distinct paths opened, 0 writes; categories referents 1,783 / pinned modules 57 / instrument blobs 9 / sha-pin-at-load 4 / **UNPINNED 264**. **Finding, checked by hand and disclosed:** the 264 are EXACTLY the 263 paths `targets_seal_paths_5` binds (the seven finals' 37 files each, gate 1(a)/(b), the host record, the power record) plus `results/loss_table_5.json`, which §3.7 gate 7 re-derives from the unit files and compares rather than binds — the tool has no category for a seal-bound or re-derived read (its own comment: the tag and the seal are "stubbed, since neither exists" — a premise from before the campaign, 2i's stale-premise lesson one experiment later). The analyzer's own check on these reads is gate 7 (`require_targets_seal_5`, verified 263/263 at the tag) and the loss-table comparison; nothing verdict-touching is unpinned. `tests/read_sweep_5.py` is not in `IMPORTED_SHA256_5` or `FROZEN_SHA256_5` (a cold tool); a `targets_seal_bound` / `rederived` category is a one-line fix left for Michael's call rather than edited under a live campaign. Process note candidate: a read-sweep tool's categories are a premise about which stage has landed — rerun it after each seal and expect the seal's set to appear.

Spend to this point (credit $176.32 → $172.10): ≈ $4.22 across the four boxes of the day, the campaign box at $1.08/h from 19:27 UTC.

**First sweep unit landed (12b `step1000`, spine): 21:56 UTC, 38 files watcher-committed (37 + the search log), `git_sha` ee4268008 = the projection's adding commit (gate 5's ancestry holds by construction), loss 3.708800469 (the preflight's 3.70880 to the printed digits), finite.** Timing, the operational fact of the campaign: **the unit took 1,544.8 s = 25.7 min — the loss forward 710.6 s (11.8 min; the 2M-token slice at batch 8 on the PCIe part) and the 34-rung argmax ≈ 14 min** — against the design's ≈ 10 min per 12b unit (§7, from the SXM4 benchmark's 6.9b argmax scaled) and the projection's 22 h [18, 30] budget line. Re-estimate on the measured unit: 12b ≈ 65 units × 26 min ≈ 28 h; 6.9b ≈ 60 × ≈ 13 min ≈ 13 h; 2.8b ≈ 50 × ≈ 6 min ≈ 5 h; the four small sizes ≈ 3 h — **≈ 45–55 h, ≈ $50–60 at $1.08/h plus ≈ $8 of bandwidth; completion ≈ 2026-09-25 late UTC.** The projection's budget line is a miss to grade (the SXM4 → PCIe step and the loss forward's real cost); the credit ($172) covers it twice over. No preregistered quantity is touched by the timing.

## 2026-09-24 — the sweep at 3 h: the 12b spine complete; two Mac-side helper slips found and fixed (the sweep untouched)

**Status 00:31 UTC (3 h 4 min in): the 12b spine is complete and monotone** — ℓ(1000) 3.7088, (2000) 2.7862, (4000) 2.3902, (8000) 2.1713, (16000) 2.0189, (32000) 1.9073, (64000) 1.8049, (100000) 1.7345, (143000) 1.7040 — all finite, no spine substitution (12b's list has its 64000), and the first bisection landed (`step3000`, loss 2.5244, for the 160m target 2.4896, which sits in the spine's [2000, 4000]). **The six targets' crossing intervals on the 12b spine, now known from the committed losses:** 160m [2000, 4000], 410m [8000, 16000], 1b and 1.4b both [16000, 32000], 2.8b [32000, 64000], 6.9b [64000, 100000] (the projection put 6.9b's in the anneal tail 100k–135k and 1b's / 410m's earlier than they are — per-row misses to grade; 2.8b's and 1.4b's inside their ranges). **Rate: 1,132 s per spine unit with the download overlapped, 1,353 s for a bisection unit** (its step is known only after the previous loss, so its 24 GB download is not hidden — ≈ 220 s at ≈ 110 MB/s). Zero halts, zero non-finite, no traceback; the box at 25 °C between units, 37 GB of 260 used. Mac side: 16 units landed and committed, the loops alive. Remaining at 12b ≈ 40–45 units (five more targets' bisections + windows) ≈ 14–15 h → 12b done ≈ 15:00 UTC 09-24; then 6.9b ≈ 8 h, 2.8b ≈ 4 h, the four small sizes ≈ 3 h — **completion ≈ 09-25 06:00–10:00 UTC.**

**Two Mac-side helper slips, found at this check, fixed and restarted — neither touches the box, the runner, or any tag-bound file:**
1. **`run/pull_units_5.sh` never pulled the per-size files.** Its "always" `find` used `-mindepth 2 -maxdepth 2 -path './units/*'` for `search_log.json` / `gate1c.json` / `HALTED`, which live at `units/<size>/<file>` — depth 3 — so the 12b search log (written on the box since 21:27 UTC) had never landed, and a `gate1c.json` or a `HALTED` marker would not have either (a halt would still have been seen: the standing wait loop greps the box's log for HALTED, and the runner stops the campaign). Fixed to `-mindepth 3 -maxdepth 3`, verified with the same `find` on the box (returns `./units/12b/search_log.json`), the puller restarted; the search log landed on its first cycle and the watcher committed it (2323f6351) — its content: the nine spine requests, the 160m pair open with the `step3000` bisection loaded, `nonfinite` empty. Gate 4 reads the search logs; the units themselves had been landing correctly throughout.
2. **`run/status_box_5.sh`'s `last=` field** grepped `\[5 sweep\]` and `\[5 finals\]` only; the runner's per-unit lines are `[5] <size>/<step> (<why>): loss …`, so the field had shown the finals' completion line for three hours. Pattern extended; the logger restarted. Cosmetic — the unit count beside it was live.
Process note (Michael's call): a puller's "always" set is a premise about the tree's shape; test it against the runner's real layout before the campaign, not at the first status check.

## 2026-09-24 — 12b COMPLETE (44 units, six pairs bracketed); 6.9b underway, gate 1(c) PASS on its eight interior checkpoints

**12b (`[5 sweep] 12b: complete`, ≈ 14:30 UTC; 44 units incl. the final; zero halts, zero non-finite).** Brackets and windows from the committed search log (every window full, `edge` 2/2, `absent` []):

| small side | target ℓ_s | bracket A | B⁻ | B⁺ | loads to refine |
|---|---|---|---|---|---|
| 160m | 2.4896 | [3000, 4000] | 1000, 2000 | 5000, 6000 | 3000 |
| 410m | 2.1291 | [9000, 10000] | 7000, 8000 | 11000, 12000 | 12000, 10000, 9000 |
| 1b | 1.9951 | [19000, 20000] | 17000, 18000 | 21000, 22000 | 24000, 20000, 18000, 19000 |
| 1.4b | 1.9188 | [29000, 30000] | 27000, 28000 | 31000, 32000 | 28000, 30000, 29000 |
| 2.8b | 1.8202 | [59000, 60000] | 56000, 57000 | 61000, 62000 | 48000, 56000, 60000, 57000, 59000 |
| 6.9b | 1.7522 | [90000, 91000] | 88000, 89000 | 92000, 93000 | 82000, 91000, 86000, 88000, 89000, 90000 |

The 2.8b pair's B⁻ is {56000, 57000}, not {57000, 58000}: 12b's `step58000` is excluded in the manifest ("candidate files duplicate another revision's" — 2g finding B's rule), so the two available steps before 59000 are 57000 and 56000, exactly §3.2's list rule; the bisection skipped 58000 for the same reason. Every bracket is 1000 steps wide (12b's list has no other gap near a crossing). The crossings sit where the spine put them; against the projection's rows: 2.8b's (59k–60k) and 1.4b's (29k–30k) inside their projected ranges, 6.9b's (90k–91k) below the projected 100k–135k, 1b's (19k–20k) and 410m's (9k–10k) above the projected 10–16k and 5–8k — three of six row placements are misses, to grade. Twelve-b's 43 sweep units took ≈ 17 h (21:27 → ≈ 14:30 UTC): spine units 1,130 s, bisection units ≈ 1,350 s (the download unhidden), one at 1,851 s.

**6.9b (started ≈ 14:30 UTC): gate 1(c) PASS on all eight interior checkpoints** against 2h's Mac reads — Σ|Δ| / max|Δ|: 1000 1/1, 2000 1/1, 4000 5/2, 8000 7/3, 16000 6/1, 32000 11/4, 64000 21/7, 100000 23/4, against 120/15. The interior drift is SMALLER than the finals' (57/8 at 6.9b): the near-tie flips the projection feared on early high-LR checkpoints did not appear (the early checkpoints drift by one item). The projection's likeliest INSUFFICIENT_DATA route is closed for 6.9b; 2.8b's seven coinciding points remain. 6.9b × 160m done (bracket [3000, 4000], window [1000, 2000] + [5000, 6000]); the 410m pair in bisection at 16:12 UTC (13 units at 6.9b; units 700–950 s). Note for 2.8b, from the manifest: its list excludes twelve revisions (26000, 53000–54000, 56000–59000, 61000–64000, 103000 — stale copies), so a 2.8b bracket falling in the 53k–65k band will be wider than 1000 steps by the list rule — adjacent on the available list, as §3.2 defines it; S10 prints the widths.

Mac side at 16:12 UTC: 62 units landed = the box's 62, tree clean, the three loops alive, the puller's per-size set now landing (`units/6.9b/gate1c.json` committed in f78c32d19). Projected completion unchanged: 6.9b ≈ 23:00 UTC, 2.8b ≈ 03:00, the small sizes by ≈ 06:00–08:00 UTC 09-25.

## 2026-09-25 — 6.9b and 2.8b COMPLETE; gate 1(c) 2.8b PASS; the small sizes underway

**6.9b (`complete` ≈ 22:40 UTC 09-24; 39 units incl. the final; no spine substitution, zero non-finite).** Brackets (every window full, edge 2/2): 160m [3000, 4000] (B⁻ 1000, 2000; B⁺ 5000, 6000); 410m [10000, 11000] (8000, 9000 + 12000, 13000); 1b [22000, 23000] (20000, 21000 + 24000, 25000); 1.4b [36000, 37000] (34000, 35000 + 38000, 39000); 2.8b [79000, 80000] (77000, 78000 + 81000, 82000). S11 unit `step142000`: loss 1.75308 against the final's 1.75215.

**2.8b (`complete` ≈ 02:50 UTC 09-25; 31 units; spine substitution 64000 → 65000 as the manifest pins; zero non-finite). Gate 1(c) PASS on all seven interior checkpoints** against 2g's Mac reads — Σ|Δ| / max|Δ|: 1000 1/1, 2000 1/1, 4000 3/1, 8000 3/1, 16000 7/2, 32000 3/1, 100000 16/5 against 120/15. **Every gate-1 known-answer comparison of the campaign is now in: 1(a) 0 diffs; 1(b) five finals Σ ≤ 57; 1(c) fifteen interior checkpoints Σ ≤ 23** — the projection's likeliest INSUFFICIENT_DATA route (.06) is closed. Brackets: 160m [3000, 4000]; 410m [11000, 12000] (9000, 10000 + 13000, 14000); 1b [30000, 31000] (28000, 29000 + 32000, 33000); **1.4b [55000, 60000] — a 5,000-step bracket** (B⁻ 51000, 52000; B⁺ 65000, 66000): 2.8b's list excludes 53000–54000 and 56000–59000 as stale copies (2g finding B), so 55000 and 60000 are adjacent on the available list, exactly §3.2's rule; the 1.4b target's loss displacement inside that bracket is the widest of the campaign (S10 prints it). S11 `step142000`: loss 1.82057 against 1.82023.

**1.4b underway (started ≈ 02:50 UTC; 20 units at 03:35): 160m [3000, 4000] and 410m [20000, 21000] done, the 1b pair in bisection; units ≈ 280 s.** Then 1b (two pairs), 410m (one), 160m (S11 alone). 136 units landed on the Mac = the box's 136, tree clean, loops alive, every per-size search log and both gate 1(c) records committed. Completion ≈ 05:30–06:00 UTC.

## 2026-09-25 — SWEEP COMPLETE (178 units, 21 pairs bracketed, zero halts); landing byte-identical; the box destroyed; S9 launched on the Mac

**`[campaign] complete` at ≈ 05:54 UTC 09-25 — 32 h 27 min after the 21:27:36 UTC 09-23 launch; zero halts, zero experiment-side stops, zero environment-side kills, zero non-finite units, no HALTED marker on any size.** Units by size (incl. each size's final): **12b 44, 6.9b 39, 2.8b 31, 1.4b 27, 1b 21, 410m 14, 160m 2 (its final and its S11 unit alone — F-1's rule: no spine for a size that is never a large side) = 178**, under the ≈ 250–300 budget line because the shared intervals reused units. The small sizes' brackets (every window full, edge 2/2; no spine substitution except 2.8b's 64000 → 65000):

| large | small | bracket A | B⁻ | B⁺ | loads |
|---|---|---|---|---|---|
| 1.4b | 160m | [3000, 4000] | 1000, 2000 | 5000, 6000 | 3 |
| 1.4b | 410m | [20000, 21000] | 18000, 19000 | 22000, 23000 | 7 |
| 1.4b | 1b | [66000, 67000] | 64000, 65000 | 68000, 69000 | 7 |
| 1b | 160m | [4000, 5000] | 2000, 3000 | 6000, 7000 | 4 |
| 1b | 410m | [37000, 38000] | 35000, 36000 | 39000, 40000 | 7 |
| 410m | 160m | [6000, 7000] | 4000, 5000 | 8000, 9000 | 4 |

**All 21 pairs kept, every bracket adjacent on its list; the largest realized ratio is the nominal 73× (12b / 160m).** S11 `step142000` losses beside the finals: 1.4b 1.91930 / 1.91883, 1b 1.99551 / 1.99513, 410m 2.12774 / 2.12913 (the one size whose 142000 loss is BELOW its final's), 160m 2.47050 / 2.48962, 6.9b 1.75308 / 1.75215, 2.8b 1.82057 / 1.82023; 12b has no S11 unit (never a small side).

**Landing: 178 units + every per-size search log, both gate 1(c) records and the four top-level records on the Mac; `git status` clean under `results/` at 05:56 UTC; every one of the box's 6,600 result files SHA-256-IDENTICAL to the Mac's copy — 0 differ, 0 missing, 0 extra** (the box's manifest hashed in place, compared file by file on the Mac). The box's campaign log copied to `experiments/exp5/box-campaign-52285720.log` (machine-local; 399 unit lines). The puller and the status logger stopped; the watcher left up for S9's files.

**Instance 52285720 DESTROYED at 05:57 UTC** (4c note 5: the moment the last unit is verified on the Mac). Vast credit $176.32 → **$131.81: $44.51 for the day's four boxes** — the campaign box ≈ $40 over 34 h 30 min (≈ $37 of time + ≈ $3–4 of bandwidth for ≈ 1.4 TB streamed), the throttled German box ≈ $1.60, the 40 GB preflight box ≈ $0.90, the Texas false start ≈ $0.20. Against the design's ≈ $45–65 with 12b: at the low end, on a slower-per-unit but cheaper-per-hour host.

**S9 launched on the Mac at 05:58 UTC** (`run/s9_mac_5.py`, `--device mps`, the classic transport, `Popen(start_new_session=True)`; logs `sweep_s9_1b.log` / `sweep_s9_6.9b.log`, chain log `sweep_s9_chain.log`): the (410m, 1b) pair's t_lo `1b/step37000`, then the (2.8b, 6.9b) pair's t_lo `6.9b/step79000`, each re-run whole in the Mac's stack and compared to the box's committed counts under gate 1's tolerance — the cross-host drift at interior checkpoints, non-gating (§5 S9). The two units land flat under `results/s9/`; the Mac's host record write-once at `results/s9/host_mac_5.json`. Next after S9: the cold battery (item 7 PASS), the watcher stopped, and **the analyzer ONCE on Michael's word.**

## 2026-09-25 — S9 CANNOT RUN ON THE MAC AS FROZEN (a build gap found at the non-gating stage); cold battery 13/13 on the complete tree; THE ANALYZER AWAITS MICHAEL'S WORD

**The finding.** The S9 chain's first unit (`1b/step37000`, `--device mps`) raised at 05:57:48 UTC, 66 s in, inside the frozen loss forward — `slice_5.py:269`, `nll_cpu = nll.double().cpu().numpy()`: `TypeError: Cannot convert a MPS Tensor to float64 dtype as the MPS framework doesn't support float64`. The line converts to float64 ON THE DEVICE before moving to the CPU; CUDA does that, MPS cannot. The campaign never touched this path (every unit ran on CUDA), the preflight ran on CUDA, and no test in `experiments/exp5/tests/` exercises `slice_loss_5` on MPS (the determinism fixture uses fakes; the string "mps" appears in no test) — so the frozen instrument's Mac path was first executed by S9 itself. The chain was stopped before the 6.9b unit began (its log empty; nothing downloaded for it); `run_unit_5` wrote nothing for the 1b unit (it raised before any record) except the Mac's write-once host record `results/s9/host_mac_5.json` (device mps, the classic transport, the stack pins equal to the box's), which the watcher committed (55bd71d2e) before the watcher was stopped. `slice_5.py` is one of the thirteen blobs `exp5-preregistered` binds; nothing was edited.

**What the analyzer will print as the tree stands:** `_s9_cross_host_5` returns `{"status": "present", "units": []}` when `results/s9/` exists without unit directories, and `{"status": "not run"}` only when the directory is absent. S9 is non-gating by design (§5: "nothing here reaches `run()`'s own failures"); the verdict is unaffected either way. The cross-host question is not unmeasured: gate 1(b) (five finals, Σ|Δ| ≤ 57) and gate 1(c) (fifteen interior checkpoints, Σ|Δ| ≤ 23) measured the box-vs-Mac drift one way; S9's "both ways" half — the Mac re-running the box's window units — is what the record lacks.

**For Michael's ruling, before the analyzer runs (recommendation first):**
- **(A) Leave S9 unrun, disclosed** — remove `results/s9/` in a disclosed commit so the analyzer prints `not run` (or keep the host record and let it print `present, units: []`); the retrospective and the essay's caveat name the gap. Costs nothing; the closed record says exactly what happened.
- **(B) Spend the one pre-committed change** on the value-inert reordering `nll.cpu().double()` in `slice_5.py` (float32 → float64 is exact on either device; the float64 accumulation is unchanged), re-cut `exp5-preregistered` over the thirteen blobs with the post-campaign disclosure (every unit record carries `prereg_tag`; the sweep ran on CUDA where the change is a no-op, so no committed byte would differ on re-run — a claim S9 itself would then test), then run S9 on the Mac (≈ 3 h: the 1b unit ≈ 20 min, the 6.9b unit ≈ 2 h on MPS plus a 14 GB classic download) and the analyzer after. Heavier: a bound-blob edit after the data, spent on a non-gating descriptive.
- (C) `--device cpu` on the Mac: not recommended — fp16 on CPU is hours for 1b and infeasible for 6.9b, and a third device class is not "the Mac's stack" §5 meant.

**Cold battery on the complete tree: 13/13** (item 7 PASS — the slice re-derives from the cached pinned file; item 11 the power record byte-identical; item 13 gate 1(a)/(b)/(c) zero failures). The read sweep is NOT re-run on the complete tree (it would print a T — a disclosure event the design reserves for the analyzer). Mac-side loops all stopped; no instance running; the tree clean.

**State for the analyzer (on his word only):** `results/` = the seven finals, 171 sweep units, seven search logs, two gate 1(c) records, the four top-level records, the S9 host record; tags `exp5-preregistered` (b3745a72a) and `exp5-targets-sealed` (91d0c3114) bound; projection ee4268008 unedited; pre-tag executions 22 + post-seal 2 (#23, #24); one pre-committed change UNSPENT.

Process-note candidates from this campaign, for his call: (1) screen a rented GPU under sustained load before installing anything (`run/thermal_screen_5.py`); (2) a puller's file set is a premise about the tree's shape — test it against the runner's real layout before launch; (3) a read-sweep tool's categories are a premise about which stage has landed — expect the seal's set after each seal; (4) the preflight should time a WHOLE unit of the largest size on the campaign host, not one rung; (5) every device the design names for any stage — including a non-gating one — gets one real execution of the frozen model-contact path on that device before the tag.

**RULED by Michael 2026-09-25 ("leave it unrun, disclosed") — option (A).** `results/s9/` removed from the tree in this commit (its one file, the Mac's write-once host record `host_mac_5.json` — device mps, the classic transport, the stack pins equal to the box's — stays in history at 55bd71d2e, where the watcher committed it after the failed attempt), so `_s9_cross_host_5` prints `{"status": "not run"}` and the verdict carries S9 as absent rather than as an empty table. The disclosure, to be carried into `results/retrospective.md` and the essay's caveat: **S9 (cross-host drift, both ways — §5, non-gating) was not run; its Mac-side attempt raised inside the frozen loss forward (`slice_5.py:269`, float64 on an MPS tensor), a path no test and no earlier stage had executed on that device; the one-way drift stands measured by gates 1(b) and 1(c). Nothing tag-bound was edited; the pre-committed change stays UNSPENT.** Process note (5) above is the lesson. The analyzer runs ONCE, on his word.

## 2026-09-25 — CLOSED: VERDICT NOT-MATCHED · MIXED (tag `exp5-closed` at e0f63e90e); retrospective written

**The analyzer, once, on Michael's word ("Run the analyzer then tag"):** launched 08:17:11 UTC detached (`analyze_5 --write`, pid 29855), complete 08:18:43 UTC (92 s), every pin active, `failures: []`, `secondary_failures: {}`. **VERDICT NOT-MATCHED · MIXED — T .05349 ≥ .01; rung-block p .00061 (13 nonzero blocks, enumerated, resolution 1.22e-4; family-block .0156; cell-level 1.0e-4); 63 live cells with a defined P on 13 rungs (38 simulated in the power record); modifier MIXED, n 48, 24 positive / 24 negative, p 1.0; signed mean offset −.0209, CI95 [−.0736, +.0039] (rung-clustered, 10,000 draws); gate 4: 21 pairs kept, 0 dropped, no unnamed unit, no absent window member; licence pairs_realized 21, largest_ratio_realized 72.98; gate 1(a)/(b)/(c) re-derived clean; S9 `not run`; read under DECLARED UNDERPOWERED IN ADVANCE.** Per type: arithmetic T .067 (31 cells / 9 rungs, p .0059), option .040 (32 / 4, no p), string no cells. Ledger classes: L-AHEAD 5 (all antonym6), S-AHEAD 13, CONCORDANT 20, UNSTABLE 13, PLACEBO-ONLY 12; unstable fraction .206. Per row (mean c): 2.8b .117 (18 cells), 1b .035, 1.4b .032, 410m .029, 6.9b .020, 160m −.025. `results/verdict.json` (813 KB, with the 714-cell table) and `VERDICT.txt` committed at e0f63e90e; **tag `exp5-closed` cut there (annotated object 028430c3), pushed.**

**The campaign's texture finding, seen in the verdict's S10 and confirmed from the loss table: Pythia-12b `step59000` is a loss spike** (2.5618 between 57000's 1.8214 and 60000's 1.8157; antonym 79 against 195–208 either side, the mid-digit rungs 0). The preregistered search landed the (2.8b, 12b) bracket on its edge ([59000, 60000] straddles 1.8202 because 2.5618 ≥ 1.8202 > 1.8157, and 58000 is excluded from 12b's list). Post-verdict sensitivity from the committed cell table (descriptive, labelled so in the retrospective): excluding that pair's 9 cells, T .0417, p .00037 — world and modifier unchanged; the 2.8b row's excess is carried equally by its 6.9b partner at a genuine crossing (residuals .0003 / .0018).

**Retrospective at `results/retrospective.md`:** the verdict cell HIT (NOT-MATCHED · MIXED was the call at .40); T, p, live cells, pairs, ratio, four of six rows, both types, the unstable fraction, S4, gate 1(c), B-6 and the dollar cost inside their ranges; the prior's two disconfirmers did not fire (T outside the 2.8b row and the antonym rungs .011, p .084; the 2.8b row .117) — but the antonym L-AHEAD mechanism MISSED entirely (antonym: 11 live cells, none L- or S-AHEAD, 6 UNSTABLE at its threshold; the option excess is antonym6, large-ahead from the 1b / 1.4b finals AND small-ahead from the 410m final — MIXED cell by cell); the 1.4b row MISSED below (no count_div13 partner); the sharpest call MISSED with its named disconfirmer fired (1.4b count_div13 at 142000 = 5, the anneal lost it); the end-of-training wobble MISSED (|Δ| to 75 in the last 1000 steps, not ≤ 10 — the small side's final is one un-averaged read); the 12b spike unprojected; the hours MISSED (32.5 vs 22). Seven process notes for Michael's call, the spike guard (6) and small-side noise (7) new.

**Licensed (§6 NOT-MATCHED · MIXED, under UNDERPOWERED):** *the discrepancy is real and has no direction the design can read; the essay reports the excess and the performability ledger, no mechanism sentence*; the caveat in every world (one family, one battery of 34 synthetic tasks, sizes to 12b, loss matched on a 2M-token slice); carried disclosures: the spike-edge bracket (verdict unchanged without it), S9 not run, the small final an un-averaged read. NOT licensed: "size-dependent emergence"; any mechanism; any direction. One pre-committed change UNSPENT end to end; pre-tag analyzer executions 22, post-seal 2, the verdict run 1. Close-out propagation (essay, `experiments.md`, the public graft of the three exp5 tags, Zenodo, paper parity) on his word.
