# Experiment 2k — build ledger

## Task 1: `battery_2k.py`

Built: constants (`EXP2K`, `RESULTS`, `TIER`, `MODE`, `SIZES_2K`, `SEEDS_2K`,
`DRAWS_PER_SEED`, `K_TOTAL`, `LADDER_K`, `N_ITEMS`, `GATE1_SEED`,
`PREREG_TAG_2K`, `SEAL_TAG_2K`, `INSTRUMENT_BLOBS_2K`, `R_CAP_DESIGN`,
`STREAM_MAPS`, `TIER_RECORD_PINS_2K`, `MATCHED_K_DESIGN`), the tier path
helpers (`tier_dir`, `tier_record_path`, `tier_draws_path`,
`halt_marker_path`, `halted_draws_path`, `halt_markers`, `seal_path`,
`power_path`, `committed_draws_path`, `committed_record_path`), the
2b weight-sha lookup (`pythia_sha`), the 4-seed row reader
(`read_rows_2k`) and 2d main-tier reader wrapper (`committed_rows`,
`committed_by_item`, `diff_seed0` via 3d's `diff_seed`), bits/counts at
k (`bits_2k`, `counts_at_k`, `block_counts`, `counts_by_k`,
`tallies_2k`, `mean_rate`), the tier-record literal and its checker
(`tier_record_2k`, `tier_record_failures_2k`), seed freshness
(`_cells_of`, `stream_collisions`, `check_seed_freshness`), and the
256-scaled matched-k rule (`matched_k_256`).

Zero model contact: no `torch`, no `transformers`, no network call,
no `from_pretrained`, anywhere in `battery_2k.py` (checked by grep on
the finished file). Every input this task touches is a committed
file, a frozen module's re-derivation, or a hand-built row set in the
tests.

### Ledgered finding (a): stream-map key format

The brief's `_cells_of` assumed the five committed stream maps carry a
`cells` dict keyed `rung/size/mode/s<seed>`, unverified in the brief.
Read all five directly:

| map | top-level keys | `cells` key format |
|---|---|---|
| `exp3/stream_map.json` | `formula, per_item_substreams, chunk_rows, draw_order, cells` | `rung/size/mode/s<seed>` |
| `exp2d/stream_map_2d.json` | `..., tiers, ..., cells` | `rung/size/mode/s<seed>` |
| `exp3c/stream_map_3c.json` | `..., exp3_seeds, new_seeds, ..., cells` | `rung/size/mode/s<seed>` |
| `exp3d/stream_map_3d.json` | `..., new_seeds, seed_blocks, ..., cells` | `rung/size/mode/s<seed>` |
| `exp3e/stream_map_3e.json` | `..., subset_items, subset_streams, ..., cells` | `rung/size/mode/s<seed>` |

All five carry `cells` and it is exactly `rung/size/mode/s<seed>` in
every one — confirmed by direct read (sample keys e.g.
`rev_string7/410m/trained/s0`, `add4_mid/1b/trained/s0`). No widening
of the parser was needed; the brief's assumption held.

One consequence worth recording: `exp2d/stream_map_2d.json` carries
BOTH a `tiers` block and a `cells` block. `_cells_of` checks `cells`
first, so the `elif "tiers"` branch in the function is dead code on
the five committed maps as they stand today — kept only as a defensive
fallback for a map that might one day lack `cells`. Never exercised by
the test suite (nothing forces it); flagged here rather than silently
carried.

### Ledgered finding (b): matched-k agreement

Re-derived `matched_k_256(rate_A, rate_B)` from
`experiments/exp2j/results/verdict.json`'s `a1.outcomes.olmo7b.per_rung`
rates and compared against §2's `MATCHED_K_DESIGN` table for all nine
`R_CAP` rungs. Every value agrees — no discrepancy to flag for the
controller:

| rung | rate_A | rate_B | computed k | design k |
|---|---|---|---|---|
| antonym | 0.136500 | 0.404844 | 64 | 64 |
| antonym6 | 0.098344 | 0.270000 | 64 | 64 |
| odd6 | 0.099844 | 0.112094 | 64 | 64 |
| sub3_mid | 0.001063 | 0.001687 | 64 | 64 |
| sub4_mid | 0.000469 | 0.000188 | 64 | 64 |
| sub_base8 | 0.022594 | 0.128875 | 45 | 45 |
| arith_next | 0.016594 | 0.116312 | 37 | 37 |
| add_base8 | 0.005313 | 0.048563 | 28 | 28 |
| add3_mid | 0.000313 | 0.003000 | 27 | 27 |

### Seed-freshness table

`check_seed_freshness(R_CAP_DESIGN)` over 9 rungs × 2 sizes = 18
cells, against the five committed stream maps: seeds 1, 2, 3 collide
with none of them on any `R_CAP` cell; seed 0 collides with
`stream_map_2d.json`'s main tier on every one of the 18 cells (the
gate-1 referent, as designed). `reverse_string` and `rev_string7`
(outside `R_CAP`) DO collide on seeds 1–3 with `exp3`/`exp3c`/`exp3d`/
`exp3e`'s committed streams, as expected — `check_seed_freshness`
raises on those rungs, exercised by
`test_check_seed_freshness_refuses_a_reversal_rung`.

### Third finding (not anticipated by the brief): a test-fixture bug in Step 1's literal code

`test_tier_record_failures`'s `over5` case was
`({"answer_type": "word"}, "answer_type")`, built on `rung="antonym"`.
`antonym`'s real `answer_type` (from `bt.load_item_file("antonym")`)
is already `"word"` — so overriding the record's `answer_type` field
to `"word"` is a no-op, not a mutation, and the checker correctly
finds nothing wrong (`bad == []`), failing the test's own assertion
that `bad` is non-empty. Confirmed by reading
`bt.load_item_file("antonym")["answer_type"]` directly.

Fixed by changing that one case's override to `{"answer_type":
"number"}`, which does differ from `"word"` and is caught by
`tier_record_failures_2k`. No other line in the test or in
`battery_2k.py` changed for this. This is not one of the two findings
the brief anticipated (stream-map format, matched-k agreement); it is
a plain test-data collision, recorded here per the working agreement
that every deviation from the brief's literal code gets a reason on
the record.

### Self-review

- Every name the brief's Interfaces section lists exists with the
  stated signature: constants, path helpers, readers, bits/counts,
  records, freshness, matched-k — all present in `battery_2k.py`,
  all exercised by at least one test.
- `pythia_sha` is not in the brief's "Produces" header line but is
  used throughout (`bk.pythia_sha`, including by
  `tier_record_failures_2k` itself); included verbatim from the
  brief's Step 3 code.
- No import of `torch`/`transformers`/network/`from_pretrained`
  anywhere in the module (grep-checked on the finished file).
- `test_battery_2k.py` written and run verbatim from the brief except
  for the one-line `over5` fix above.

### Test run

RED: `ModuleNotFoundError`-class collection error before the module
existed (`ImportError: cannot import name 'battery_2k' from
'experiments.exp2k'`).

GREEN: `39 passed in 2.16s`, pristine output (no warnings), full file
run from the repo root with the project venv.

## Task 2: `run/tier_2k.py`, `run/campaign_2k.py`, `run/rehearse_2k.py`, the commit watcher, `battery_2k.py`'s pin block

Built: `battery_2k.py`'s pin block (`FROZEN_FILES_2K`, `FROZEN_SHA256_2K`
empty pending Task 5, `frozen_from_disk`, `check_frozen_2k`,
`require_prereg_2k`); `run/tier_2k.py` (`run_rung`, `rungs_2k`,
`tier_complete`, `run`, `main`, `real_loader`, `_prompts`,
`_refuse_if_halted`); `run/rehearse_2k.py` (`run`, `main`,
`_snapshot`); `run/campaign_2k.py` (`main`); `run/commit_watcher_2k.sh`.
Zero model contact in the build: `torch` is imported only inside
`real_loader` (via `exp3.run.run_cell._load_model`) and inside
`sample_item`'s own module, both lazy and uncalled by any test — every
test drives `run_rung`/`run`/`rehearse_2k.run` with a fake sampler and
a fake `(tok, model, model_sha)` context.

### Refusal order in `run()`

`require_prereg_2k` (tag exists, three instrument blobs bound) →
`check_frozen_imports_2g` → `check_frozen_2i` → `check_frozen_2k` →
`check_pythia_predictor_files` → seal-exists ("sealed") → halt scan
(`_refuse_if_halted`, any `*.HALTED` under the tier tree) → `rungs_2k`
(2i's committed R_CAP, must equal `R_CAP_DESIGN`) →
`check_seed_freshness` → pending-list / dry-run branch → one model
load per size. Matches the brief's global constraint exactly; exercised
by `test_run_refuses_without_the_tag_and_with_a_seal`,
`test_run_refuses_unpinned_frozen`,
`test_run_dry_run_lists_pending_and_loads_nothing`,
`test_run_one_rung_end_to_end_with_the_fake`.

### Gate-1 file contract

`run_rung` loads 2d's committed record + draws for the cell, checks
the committed record is a seed-0×64 main-tier record whose provenance
(`items_sha256`, `answers`, `answer_type`, `model_sha`) agrees with the
pinned item file and the live model, and checks the committed draws
file's sha256 against 2i's `PYTHIA_PREDICTOR_FILES` pin — so the
comparison target is provably the file 2i read, not just some file on
disk. Then, item by item: `sample_item` runs, the item's 64 seed-0
draws are diffed against the committed row; on the first mismatch
(including a coverage mismatch, i.e. wrong draw count on either side)
it writes `<rung>.HALTED.jsonl.gz` (via `write_draws`, the rows
compared so far including the failing one) THEN `<rung>.HALTED`
(JSON: `rung`, `size`, `item`, `items_compared`, `n_diffs`, `diffs[:5]`,
`model_sha`, `committed_draws_sha256`, `stack`, `git_sha`), writes no
normal tier record or draws file, and raises `RuntimeError` whose
message contains "GATE 1 FIRED". `_refuse_if_halted` scans for any
`*.HALTED` marker under the tier tree before `run_rung` or `run` does
anything else, so a halted rung — or any other rung, any size — refuses
every later call with a message containing "halt". Skip-if-exists
short-circuits before the gate-1 referent is even loaded, so a
completed rung's sampler is never called again (proved with a sampler
that raises `AssertionError` if invoked).

### Commit watcher

`commit_watcher_2k.sh` follows `commit_watcher_2d.sh`'s structure with
the tree swapped to `experiments/exp2k/results` and the find pattern
widened to include bare `*.HALTED` (2d's pattern only matched
`*.HALTED.jsonl.gz`, which has a different suffix). For a
`*.draws.jsonl.gz` file: wait for its sibling `.json` to exist (as
2d's does), then take two size samples ten seconds apart and defer
(without marking the file seen) if the size changed — 2i's
`commit_watcher_2i.sh` lesson (a growing multi-hundred-KB file is not
complete the instant it appears), applied at 10s instead of 2i's 3s
per the brief's dial. Non-draws files (tier records, `.HALTED`
markers) keep 2d's flat 2-second settle. Commit message format
`exp2k campaign: <size>_trained <unit> landed (watcher)` — the `sed`
capture is the tier directory name itself (`k256/<size>_trained/`),
which already reads as `<size>_trained` with no string concatenation
needed. Made executable (`chmod +x`); `bash -n` and `zsh -n` both
parse it clean.

### Concern: `test_require_prereg_2k_refuses_missing_tag_and_drift` and four `test_tier_2k.py` tests fail — not a defect in this task's code

`require_prereg_2k` and every caller of it (`tr.run`) check that all
three of `INSTRUMENT_BLOBS_2K` — `analyze_2k.py`, `battery_2k.py`,
`run/tier_2k.py` — exist on disk before checking anything else about
the tag. `experiments/exp2k/analyze_2k.py` is Task 3's file (see
`task-3-brief.md`'s Files section) and does not exist yet at the end
of Task 2. Five tests fail with the identical root cause
(`RuntimeError: experiments/exp2k/analyze_2k.py not on disk`):
`test_require_prereg_2k_refuses_missing_tag_and_drift` (in
`test_battery_2k.py`) and, in `test_tier_2k.py`,
`test_run_refuses_without_the_tag_and_with_a_seal`,
`test_run_refuses_unpinned_frozen`,
`test_run_dry_run_lists_pending_and_loads_nothing`,
`test_run_one_rung_end_to_end_with_the_fake` — every test that calls
`tr.run(...)` or `require_prereg_2k`'s happy path. Verified this is
the sole cause and not a bug in `tier_2k.py`/`battery_2k.py`: with a
throwaway one-line `analyze_2k.py` stub placed on disk (never
committed), all 51 tests across both files pass; the stub was removed
before committing. `require_prereg_2k`'s pin-block code and `run()`'s
refusal order are both verbatim from the brief/task constraints, so
this is a genuine cross-task ordering dependency, not something in
Task 2's scope to fix — creating `analyze_2k.py` here would step on
Task 3's Produces list. Expect these five to go green once Task 3
lands `analyze_2k.py` (no change needed on the Task 2 side).

### Fixed within scope: `frozen_from_disk()` needed a filter to be usable before Task 5

The brief's verbatim `frozen_from_disk()` (`{p: bg.sha256_file(p) for p
in FROZEN_FILES_2K}`) raises `FileNotFoundError` on the first missing
path — `bg.sha256_file` has no graceful path for a missing file. Since
`FROZEN_FILES_2K` names `power_2k.py`, `make_referents_2k.py` and
`run/seal_2k.py` (Task 3/4's files, not yet on disk), the dict
comprehension never reaches the point where a caller could filter its
*result*; `test_check_frozen_2k_refuses_unpinned_and_drift`'s own
`{p: s for p, s in bk.frozen_from_disk().items() if p.is_file()}` line
crashed before the filter ran. Added `if p.is_file()` inside
`frozen_from_disk()` itself — a one-line, additive change, consistent
with the function's own docstring ("Tests use it to stand in for the
literal before Task 5"): once every `FROZEN_FILES_2K` member exists
(Task 5's state), the filter is a no-op and the function returns the
same dict the verbatim version would have. This is the one deviation
from the brief's literal Step 1 code; every other line is verbatim.

### Test run

RED (Step 3): `ImportError: cannot import name 'rehearse_2k' from
'experiments.exp2k.run'` (collection error — `test_tier_2k.py`
imports `rehearse_2k` before `tier_2k`, so that name surfaces first;
both were absent).

GREEN (Step 7, real end state): `test_battery_2k.py` +
`test_tier_2k.py` together, 46 passed / 5 failed, all 5 failures the
single disclosed `analyze_2k.py`-absence cause above; no warnings, no
other failures. Verified separately (throwaway stub, not committed):
51/51 pass once `analyze_2k.py` exists, confirming Task 2's own code
is correct.
