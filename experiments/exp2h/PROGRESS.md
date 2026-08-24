# Experiment 2h — Progress Ledger

Design doc `experiment-2h-design.md` stays as ruled (dials a–f RULED by
Michael 2026-08-24, "Full 34 rungs, dials as recommended") — nothing in
it is edited during the build. Zero model contact throughout this
session: the only Hub data anywhere in the tree is the committed
`hub_inventory_69.json` metadata scan (copied from
`docs/superpowers/plans/hub_inventory_69_2026-08-24.json`); no
`from_pretrained` of weights, no `hf_hub_download` of a weight file, no
forward pass. Tag `exp2h-preregistered` not yet cut — that is the
freeze session's business. The only model contact in the whole
campaign is the 6.9b checkpoint sweep, which unlocks only after the tag
(design §7).

## 2026-08-24 — BUILD, Task 1: `battery_2h.py` + the 6.9b manifest + loader

Instrument at `experiments/exp2h/`: `__init__.py`, `run/__init__.py`,
`tests/__init__.py`, `hub_inventory_69.json` (copied, sha256
`8762902fe2f194a082e82cffb144efc347b9cad4b597768028a2d521776b8325`),
`battery_2h.py`, `checkpoints_2h.json` (generated), test
`tests/test_battery_2h.py` (15 tests, all pass).

**R_69** re-derives from 2c's committed m4 6.9b counts (all 34 rungs,
`FINAL_COUNT_PIN_69`, read once from
`experiments/exp2c/results/m4/6.9b_trained/*.json` and pinned as
literals; `load_m4_counts_69` re-asserts every value against the pin
at load) under 2d's floor via `battery_2g.rising_by_bar` (reused, not
re-implemented) — exactly the design's eight rungs: antonym 286,
antonym6 143, add_base8 29, sub_base8 52, add3_mid 19, arith_next 58,
count_div13 102, odd6 107. Two (count_div13, odd6) never used by 2g's
2.8b primary (R_28); add3_mid's final count (19) sits under the
20-item eligibility floor (`battery_2g.ELIGIBILITY_MIN_POS`), disclosed
per design §4 and asserted in the test, not enforced at this layer
(eligibility is a primary-time gate on the realized sweep's n_pos, not
on the m4 final count).

**The 6.9b manifest** (`build_manifest_69`) mirrors
`checkpoints_2g.build_manifest`'s body for one size with an injected
repo/grid and no exclusions, using `checkpoints_2g.candidate`/
`.signature` directly (`build_manifest` itself is bound to
`battery_2g.REPO_OF`/`.GRID`/`.EXCLUDED_GRID`, none of which carry a
6.9b entry). From the committed `hub_inventory_69.json` (155
revisions): 23 grid entries (22 trained + step0), every candidate
`bin-shards` except the final point (`safetensors-shards`, main
publishes safetensor shards), every entry's (kind, lfs-shas) signature
distinct — no exclusion needed, confirming the design's "6.9b is the
cleanest size" scan. `stale_main_copies` is `{"model.safetensors": 0,
"pytorch_model.bin": 0}` — zero stale-main copies anywhere in the 155
revisions, also as the design states. Manifest sha256 (`checkpoints_2h.json`,
verified against the committed file):
`c5cd292cbf0d26a6968c5852d8bbf7f872d4b78fd8c7352a8a3e9e11be67cf60`.

**Discrepancy against the plan, disclosed rather than bent:** the
plan's Task 1 key-steps paragraph states the manifest should show
`final_duplicates == ["step143000"]`. The computed value, from the
committed inventory through the reused `candidate`/`signature` rule,
is `final_duplicates == []`. This is not a bug in the data — it is
structural in the frozen rule, and matches the precedent already
sitting in 2g's own committed `checkpoints_2g.json`: BOTH the 2.8b and
12b manifests there also carry `final_duplicates: []`, despite each
having a materially different, byte-identical `hub_step143000` (12b:
`signature_equals_main: true`, `duplicates: ['step58000']`; 2.8b:
`signature_equals_main: false`, 76 stale `model.safetensors` copies
tracked separately under `stale_main_copies`, none of which ever
becomes a revision's *candidate* because the rule steers a
main-matching single safetensors file to the bin branch unless the
revision literally IS main). `signature()` is kind-specific: main's
candidate for 6.9b is `safetensors-shards` (it publishes safetensor
shards), step143000's is `bin-shards` (it does not) — two different
kinds can never produce equal signature tuples, so `dups_of("main")`
structurally cannot list step143000. The design's "step143000
byte-identical to main" fact IS present in the manifest — as
`hub_step143000.signature_equals_main == True` (a direct bin-sha
comparison, the same field 12b's manifest carries its analogous fact
in), with `hub_step143000.duplicates == []` (no OTHER step branch
duplicates step143000's own bin content — the "cleanest size" claim).
The test (`test_manifest_from_committed_inventory`) asserts the
computed values, not the plan's literal, with the reasoning inline as
a comment; this note is the disclosure the build rules require instead
of silently bending a literal. Task 2/3 should read the "step143000 ==
main" fact from `hub_step143000.signature_equals_main`, not from
`final_duplicates`.

**`sampler_counts(size, rungs)`** generalizes `analyze_2g.sampler_counts_1b`'s
body to a `size` argument (a new function in `battery_2h`; exp2g's stays
1b-only and untouched). Verified against `analyze_2g.sampler_counts_1b`
directly (full per-item array equality, not just spot values) on all
six rungs of R_28 ∩ R_69 = {add3_mid, add_base8, antonym, antonym6,
arith_next, sub_base8}; also exercised at 410m for shape. Rejects a
non-probe size (e.g. "6.9b") by construction.

**`FROZEN_2G_SHA256`** pins the 7 exp2g modules this instrument imports
or mirrors (battery/labels/strata/stats/probe/checkpoints/analyze)
plus 3 exp2g data files (`results/predictor/predictor.json`,
`checkpoints_2g.json`, `referents_2g.json`) — 10 pins, `check_frozen_2h`
re-asserts every one. `PREDICTOR_2G_SHA` (the plan's literal,
`9eadbac316ddc5db7f7af716e406d3434033ccbaceb64a39467febdba757adc7`)
verified against a fresh sha256 of `experiments/exp2g/results/predictor/predictor.json`
— matches exactly, and equals `FROZEN_2G_SHA256`'s entry for that path.
The `checkpoints_2g.json`/`referents_2g.json` pins were cross-checked
against `analyze_2g.CHECKPOINTS_SHA256`/`.REFERENTS_FILE_SHA256`
directly in the test — all three agree.

The loader family (`download_entry_69`/`clean_dir_69`/
`load_checkpoint_69`/`free_69`) is a thin, repo/sha-parameterized copy
of `checkpoints_2g`'s loader (`checkpoints_2g`'s is bound to
`battery_2g.REPO_OF`, which lacks 6.9b); `huggingface_hub`/`torch`/
`transformers` are imported lazily inside each function body, never at
module import, and the test suite never calls them — tensor digest is
reused from `checkpoints_2g.tensor_digest` by import, not redefined.

Test suite: 15/15 pass (`experiments/exp2h/tests/test_battery_2h.py`),
zero model contact, zero network. Commit follows this entry.
