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
