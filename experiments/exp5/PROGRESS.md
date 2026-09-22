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
