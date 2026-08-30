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

**Correction (Task 5):** the description above is Task 2's point-in-time
state. `frozen_from_disk` is now `frozen_from_disk(*, strict: bool =
True)` — strict (raise on any missing path) BY DEFAULT; the `if
p.is_file()` filter described above lives behind `strict=False`, used
only by the pre-Task-5 tests that still monkeypatch a partial
`FROZEN_SHA256_2K`. Task 5's own Step 1 pin uses the strict default.

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

## Task 3: `analyze_2k.py` + `make_referents_2k.py`

Built: `analyze_2k.py` (pins and the import-surface check
`check_imports_2k`, `pin_a_from_record_2i`/`pin_a410_from_record_2i`/
`ladder_b_from_record_2j`, `load_2i_tree` — 2j's `run()` prefix with
2k-prefixed labels, `load_tier_2k` with the gate-1 re-derivation,
`_seal_paths_2k`/`seal_sha_of`/`seal_failures_2k`, `load_power_2k`,
`ladder_2k`/`s1_blocks`/`placement_on_ladder`/`s3_matched`/
`s4_partials`/`s5_within_lineage`/`s7_texture`, `verdict_tree_2k`/
`_licensed`, `run()`) and `make_referents_2k.py`
(`referent_files`/`build`/`check_referents`), both transcribed from
the brief's Step 4/5 code verbatim except the three deviations below.
The five Task 1+2 tests that were RED only because `analyze_2k.py`
didn't exist are now GREEN with no change to their own files.

### The 410m literal (Step 3)

`experiments/exp2i/results/verdict.json`'s `secondaries` dict has no
`cross_410m` key. Printing `list(v["secondaries"])` and each entry's
`stratified.T` found `replication_410m_cross` at T =
0.11537934925951784 — inside the brief's own sanity bound (0.10, 0.13)
and matching CLAUDE.md's "410m cross .1154 (a projection miss)" for
2i. `pin_a410_from_record_2i` reads
`v["secondaries"]["replication_410m_cross"]["stratified"]["T"]` as the
PRIMARY path, falling back to `secondaries["cross_410m"]["stratified"]
["T"]` only if the primary key is absent — that fallback is inert on
every committed record; `VERDICT_2I_PIN_A410 = 0.11537934925951784`.

### `_first_correct_outcome`'s shape (no adaptation needed)

`analyze_2i._first_correct_outcome(out, rungs)` (analyze_2i.py:1175)
returns exactly `{r: {"y": [...], "n_pos": ...}}` — an outcome dict
with `"y"` per rung, precisely what the brief's `s7_texture` assumed
and passes straight into `_run_test` as the `out` argument. No
adaptation needed; the brief's assumption held.

### Deviation 1: `_L["NOT-DENSITY_UNDERPOWERED"]`'s leading case

The brief's literal string starts "Not detected at this resolution"
(capital N); `test_licensed_sentences_carry_the_caveat_and_the_status`
asserts the lowercase substring `"not detected at this resolution"`
(matching 2j's own `ABSORBED_UNDERPOWERED` string, which is lowercase).
Lowercased the one word to match the test and 2j's precedent. No other
change to that sentence.

### Deviation 2: `imports_pinned`'s sentinel resolution in `run()`

The brief's literal line `imports_pinned = IMPORTED_SHA256_2K is not
None` collapses the tri-state (unset sentinel / explicit False / real
dict) to a plain bool at the point of resolution, so a caller taking
the default with `IMPORTED_SHA256_2K = None` becomes indistinguishable
from a caller who explicitly passed `imports_pinned=False` (skip the
check) — both end up `False`, and `run()`'s
`elif imports_pinned is not False` never fires, so the "not pinned
(build incomplete)" refusal is silently lost. Caught by
`test_run_refuses_when_the_manifest_or_imports_are_not_pinned`'s
second half. Fixed to mirror `referents_sha`'s own tri-state exactly:
`imports_pinned = None if IMPORTED_SHA256_2K is None else True` at
sentinel-resolution time, preserving `None` (refuse) as distinct from
an explicitly-passed `False` (skip) all the way to the `if
imports_pinned: ... elif imports_pinned is not False: ...` branch,
unchanged from the brief.

### Deviation 3: `check_imports_2k`'s covered set

The brief's literal `covered` set (`bk.FROZEN_SHA256_2K` +
`bg.FROZEN_IMPORT_SHA256_2G` + `bk.INSTRUMENT_BLOBS_2K`) is
structurally unable to pass `test_check_imports_2k_refuses_a_drifted_
pin` at ANY point in this build, not only before Task 5: that test
monkeypatches `IMPORTED_SHA256_2K` down to one (deliberately wrong)
entry, so any coverage that would otherwise come from
`IMPORTED_SHA256_2K` itself (Task 5's eventual full dict) is wiped for
the duration of the test — the residual `__init__.py`-chain modules
(exp2c/exp2d/exp2f/exp2g/exp2h/exp2i/exp2j package inits, 2c's
generators/instrument/stats_bounds/power_table, 2f's
collect_eval/probe/make_referents, exp3's analyze_3, 2j's
verify_referents_2j — all already in `sys.modules` because
`analyze_2k.py` imports `an2j` which imports the whole tree
transitively) have no OTHER source of coverage in the brief's literal
code, so `check_imports_2k()` always reports them "unpinned" before it
ever reaches "drifted", regardless of `FROZEN_SHA256_2K`'s pin state.
Verified this empirically (removed the fix, reran the test in
isolation — same failure, same file list, independent of the
whole-suite ordering issue below).

Fixed in two parts, both inside `check_imports_2k()` only (no change
to `battery_2k.py`, out of this task's scope):
- `covered` now derives from `bk.FROZEN_FILES_2K` (the documented path
  tuple, populated today — 2j's 26 frozen paths carried verbatim plus
  the sampler-side/2k-artifact additions) rather than
  `bk.FROZEN_SHA256_2K` (the pinned-hash literal, still `{}` until
  Task 5); hash-checking those paths stays `check_frozen_2k`'s job,
  called separately in `run()`.
- 2j's own residual import-surface pin (`an2j.IMPORTED_SHA256_2J`,
  closed and immutable since 2j tagged) is folded into the SAME
  verified-against-disk dict as `IMPORTED_SHA256_2K`'s own entries
  (not merely added to `covered` untrusted) — a hand-edit to one of
  2j's residual files is still caught as drift, not silently trusted.
  2k's `run()` never calls 2j's own `check_imports_2j` to verify this
  independently (it would also flag 2k's own files, which 2j's
  covered-set knows nothing about), so this is the only place that
  verification happens for 2k.

With both parts: `test_analyze_2k.py` alone is 17/17 green, matching
the brief's own precedent for what a passing single-experiment
`covered` set looks like. Recorded so Task 5's own scan does not need
to duplicate 2j's residual pins — only what is genuinely new to 2k.

### Known gap (Task 5's, not this task's): `run/rehearse_2k.py` / `run/__init__.py` under whole-suite collection

`experiments/exp2k/tests -q` (all three test files together) is 69
tests, 68 pass, 1 fails —
`test_check_imports_2k_refuses_a_drifted_pin`, same test as above,
now reporting "unpinned module" for `experiments/exp2k/run/__init__.py`
and `experiments/exp2k/run/rehearse_2k.py`. Cause: `test_tier_2k.py`
imports `rehearse_2k` at module scope (`from experiments.exp2k.run
import rehearse_2k as rh`), and pytest's collection phase imports every
test module before running any test body, so by the time this test's
body executes, `rehearse_2k` (and the `run` package `__init__.py`) are
already in `sys.modules` — neither file is frozen, an instrument blob
(`INSTRUMENT_BLOBS_2K` names only `tier_2k.py`), or yet in
`IMPORTED_SHA256_2K`. This is the identical category of gap
`test_check_imports_2k_excludes_test_helpers` is explicitly written to
tolerate (Step 6: "may report a real gap in this process — that is
information for Task 5's scan, not a failure of the test's
assertion"), just surfacing on a second test the brief did not name.
Not fixed here: `rehearse_2k.py` is Task 2's own live, unclosed
tooling (not a closed experiment's immutable bytes, unlike 2j's
residual pin above), so treating it as pre-covered would be actively
wrong — it is real, in-progress code Task 5's `IMPORTED_SHA256_2K`
scan is supposed to discover and pin, not something this task should
paper over. Confirmed the isolated single-file run
(`test_analyze_2k.py` alone, the brief's own Step-6 command) is
17/17 green; the gap appears only when Task 1+2's tests are collected
alongside it. Test counts: `test_battery_2k.py` + `test_tier_2k.py` =
52 (unchanged), `test_analyze_2k.py` = 17, whole directory = 69.

---

## Task 4: `run/seal_2k.py`, `power_2k.py`, the worlds, totality, the
## seal/power tests, the cold battery

Built exactly the brief's file list: `run/seal_2k.py`, `power_2k.py`,
`tests/full_shape.py`, `tests/test_full_shape_2k.py`,
`tests/test_totality_2k.py`, `tests/test_seal_2k.py`,
`tests/test_power_2k.py`, `verify_referents_2k.py`. `seal_2k.py` and
`power_2k.py` are the brief's Step 1/2 code verbatim (rulings 1/4
already matched the literal). One edit to `analyze_2k.py` (Ruling 3,
the only edit made to it): `run()` gained a test-only `frozen_check`
keyword (default `None` → `bk.check_frozen_2k`), used at the "2k
frozen modules" `collect_total` site — `bk.check_frozen_2k` refuses
unconditionally until Task 5 pins `FROZEN_SHA256_2K`, so without the
bypass every synthetic world lands INSUFFICIENT_DATA on that refusal
alone regardless of the world's real content. `write_world_2k` returns
`"frozen_check": lambda: None` in its seal dict so `run_world`'s
`**seal` expansion carries it through automatically; the campaign
never passes the kwarg; Task 5 drops the bypass call site once the
real pin lands (the `frozen_check or bk.check_frozen_2k` reverts to
just `bk.check_frozen_2k` — or the parameter is removed outright, on
Task 5's call).

### Build finding: the "independent" 2i tree's natural R_CAP is eleven rungs, not design's nine

`fs2j.write_world_2j(world="independent")` — the world builder the
brief's Step 3 names verbatim as 2k's 2i-tree source — assigns every
one of 2i's ELEVEN `STRATA_RUNGS` exactly `N_POS_FIRING=200` positive
items by the endpoint step, for EVERY world type it supports (not just
"independent"): its `first[r]` builder applies to `r in RUNGS_CAP`
unconditionally, with `RUNGS_CAP = tuple(bi.STRATA_RUNGS)` and no
parameter to restrict which rungs get "hot" treatment. Confirmed by
direct query (seed 0): the resulting `rung_set.json`'s `R_CAP` is
`R_CAP_DESIGN`'s nine PLUS `count_div13` and `median5` — eleven, not
nine. `analyze_2k.load_2i_tree` refuses UNCONDITIONALLY when the live
2i tree's derived `R_CAP` differs from `battery_2k.R_CAP_DESIGN`
(design §3.4: 2k's analyzer reads 2i's real, closed nine-rung R_CAP as
a literal and checks the live tree reproduces it) — with the brief's
Step 3 code used as given, EVERY world would have failed this check
and landed INSUFFICIENT_DATA on "R_CAP != design's", never reaching
DENSITY/NOT-DENSITY at all. 2j itself never hits this because 2j has
no equivalent frozen-nine restriction (`RUNGS_CAP` = the full eleven
throughout `analyze_2j.py`); the mismatch is new to 2k's own design.

Fixed in `full_shape.py`, not in frozen code: `_restrict_r_cap_to_design`
runs immediately after `write_world_2j`, zeroing the two extra rungs'
ENDPOINT_STEP_7B sweep record AND `stage1_final` endpoint record (both,
so 2i's gate-1 byte-identity re-derivation still sees a consistent
pair — the sweep-at-endpoint and stage1_final records must agree
byte-for-byte) and re-deriving `rung_set.json` fresh through 2i's own
`bi.rung_set_from_counts` over the (now-corrected) 34-rung count table
— a real world-construction fix, not a hand-edit of `R_CAP` itself, so
`analyze_2i._check_rung_set_derivation` (which RE-DERIVES from the
endpoint's own counts rather than trusting the file) still passes. A
second, smaller consequence: `write_world_2j` had already written
`verdict.json`'s `tests.A` (the pin `pin_a_from_record_2i` reads) using
its OWN eleven-rung R_CAP, computed internally before the restriction
ran — `write_world_2k` now re-derives and overwrites `v2i["tests"]["A"]`
over the corrected nine-rung `r_cap` at the same point it already
re-derives the 410m secondary (only `T`/per-rung `d` are compared by
the comparison gate, both permutation-independent, so the re-derivation's
own `n_perm=20` need not match `run()`'s). No other `verdict.json` field
2k reads (`B`, `within_alone`, `cross_beyond_within`, `reverse_direction`)
needed a parallel fix — `analyze_2k.py`'s `run()` reads only `tests.A`
and `secondaries.replication_410m_cross` from the 2i verdict.

### Known gap, not fixed here (Task 5 / the freeze's, per the brief's own edit restriction): `load_tier_2k`'s two `run()` call sites are unwrapped

`analyze_2k.run()`'s tier-loading block (`# ---- the 2k tiers, the
seal, the power record`) calls `load_tier_2k(root_2k, size, ...)`
directly, once per size, NOT through `collect_total` — unlike every
other loader/statistic in this file (`seal_failures_2k`, `_run_test`
inside `_core`, every secondary's own thunk via `_sec`). Confirmed
empirically before writing the totality suite: a monkeypatched
`load_tier_2k` that always raises propagates straight out of `run()`
as an uncaught exception rather than landing on INSUFFICIENT_DATA
under a "2k tier" label — the brief's Step 5 bullet ("a forced
exception from `load_tier_2k` … → `2k tier`") cannot be satisfied as a
graceful terminal on the code as it stands. Task 4's Code-Organization
constraint restricts every edit to `analyze_2k.py` to the one
`frozen_check` change (Ruling 3), so this was left unfixed here rather
than adding a second `collect_total` wrapper on my own judgment.
`test_load_tier_2k_forced_exception_is_a_known_gap` (`test_totality_2k
.py`) documents the CURRENT (crashing) behaviour with `pytest.raises`
instead of asserting the brief's literal expectation or silently
dropping the shape — same lineage as 2d F-1 / 2i F-1 / 2j F-1, one
call site over, for the freeze (or Task 5) to close additively (wrap
both `load_tier_2k(...)` calls in `collect_total("2k tier {size}", ...)`
or similar, matching the pattern everywhere else in `run()`).

**Closed (Task 5, follow-up 2):** both `load_tier_2k(...)` call sites
in `run()`'s tier-loading block are now wrapped in `collect_total(...,
f"2k tier {size} load")`. Restated precisely, since "unwrapped"
overstated the exposure even before this fix: every RAISER reachable
inside `load_tier_2k` itself was ALREADY either `collect_total`-wrapped
(the record read, the rows read, `_gate`, `_bits`) or TOTAL over its
inputs (`tier_record_failures_2k` never raises, only returns a list of
strings) — the two plain dict lookups in the function body,
`battery[rung]` and (inside `tier_record_failures_2k`, via
`load_tier_2k`'s `committed_sha=bi.PYTHIA_PREDICTOR_FILES[(size,
rung)]` argument) `bi.PYTHIA_PREDICTOR_FILES[(size, rung)]`, are keyed
over R_CAP x SIZES_2K, a set `load_2i_tree`/2i's rung-set check and
`bi`'s own committed pin table both hold complete for every design
rung at both sizes — so neither lookup is a reachable `KeyError` on any
tree the two upstream checks have already passed. The outer wrap is
therefore defence in depth against a FUTURE change to `load_tier_2k`'s
body reopening a raiser at this call site, not a fix for a reachable
crash today; `test_load_tier_2k_forced_exception_now_lands_gracefully`
replaces the "known gap" test, confirming the wrap is live regardless.
`test_totality_2k.py`'s own `_gate`, one level in: the "gate 1
coverage" arm (`if len(rows) != bk.N_ITEMS or len(committed) !=
bk.N_ITEMS: raise ValueError(...)`) is likewise DEAD DEFENSIVE CODE on
any tree reaching `_gate` — `rows` comes from `bk.read_rows_2k`, which
already refuses (`"... coverage incomplete"`) unless it sees exactly
`n_items` distinct items 0..n_items-1, and `committed` comes from 2d's
own equally coverage-pinned reader; kept as belt-and-suspenders, not
because either side can arrive short.

### Step 6: W3 ("structured") tuning

`STRUCTURED_STRENGTH` scales the same density mechanism as W1 (`q_i =
clip(strength · y_i / 21, 0, 0.95)` over 192 additional draws per
item), so even small `strength` compounds heavily; the brief's "each
halving roughly halves T" heuristic does not hold here — T falls much
slower than strength near 1.0 and much faster below it. A fast
scan (one 2i tree built once, only the tier + primary statistic
recomputed per candidate, bypassing the full `run()`/secondaries
pipeline) located the landing band before touching the real file:

| strength | T | p |
|---|---|---|
| 0.12 (brief's starting value) | 0.8255 | 0.0050 |
| 0.03 | 0.5832 | 0.0050 |
| 0.01 | 0.3237 | 0.0050 |
| 0.003 | 0.1189 | 0.0050 |
| 0.001 | 0.0350 | 0.0050 |
| 0.0003 | 0.0003 | 0.4776 |
| 0.0012 | 0.0443 | 0.0050 |
| 0.0015 | 0.0564 | 0.0050 |
| 0.0018 | 0.0704 | 0.0050 |
| 0.0025 | 0.0977 | 0.0050 |

Shipped `STRUCTURED_STRENGTH = 0.0015` (comfortable margin from both
0 and the 0.10 bar). Confirmed through the REAL `write_world_2k` /
`run_world` path (not the fast scan) at the brief's own `n_perm=200,
n_boot=20`: `NOT-DENSITY structured`, T=0.056427895826048485,
p=0.004975124378109453 — `0.0 < T < 0.10` and `p < 0.01`, both
conditions `test_w3_structured_lands_under_the_bar_with_p_below_alpha`
checks. Landed on the third distinct value tried in the real file
(0.12 → 0.001 → 0.0015), each an actual edit + real-path re-run, not
merely a fast-scan reading.

### Test counts and commands run

- `experiments/exp2k/tests/test_full_shape_2k.py` (13 worlds, 5 test
  functions): 5 passed, ~409 s.
- `experiments/exp2k/tests/test_totality_2k.py` (one representative
  upstream 2i-tree shape + every shape new to 2k's own readers + the
  forced-exception injection sites + the control, 31 test functions —
  corrected from the "32" originally recorded here):
  31 passed after one fix (see below), ~252 s.
  - One totality test needed a needle correction after the first
    run: `test_tier_record_is_a_directory` expected the "record read"
    needle, but `load_tier_2k`'s FIRST check is `rp.is_file() and
    dp.is_file()` — a directory in the record's place is caught
    THERE ("record or draws file missing"), never reaching the
    `json.loads` attempt the torn/list shapes exercise. Needle
    corrected to match; re-run 31/31 green.
- `experiments/exp2k/tests/test_seal_2k.py` (2), `test_power_2k.py`
  (2): both green as part of the fast-module and whole-directory runs
  below.
- Fast modules (`test_battery_2k.py` + `test_tier_2k.py` +
  `test_analyze_2k.py` + `test_seal_2k.py` + `test_power_2k.py`):
  73 passed, 1 known pre-Task-5 failure
  (`test_check_imports_2k_refuses_a_drifted_pin`, Task 3's ledgered
  gap above — unchanged, still reproduces the same way), 1 skipped.
- Whole directory (`experiments/exp2k/tests -q`, all seven test
  files): 109 passed, 1 known failure (same test, same reason), 1
  skipped — 111 collected. ~715 s.
- Cold battery (`python -m experiments.exp2k.verify_referents_2k`):
  10 PASS + 2 SKIPPED ("pending Task 5" — item 3 `referents_2k.json`,
  item 12 the import surface), item 10 printed "(seal and power
  record: absent — pre-campaign)" as expected pre-campaign.

Zero model contact end to end (the seal/power tests and the worlds
build synthetic trees and re-derive from committed bytes only; no
`torch`/`transformers` import, no network call, anywhere in the seven
new files).

---

## Task 5: the real-tree closure — frozen literals, the import-surface
## pin, the pre-campaign manifest, the mutation harness, the read
## sweep

### The three literals

`FROZEN_SHA256_2K` pinned from `frozen_from_disk()` (strict): **36
modules** — 26 inherited from `an2j.FROZEN_SHA256_2J` + 10 new to 2k
(2j's two tag-bound blobs `analyze_2j.py`/`functionals_2j.py`, the
three sampler-side modules `rederive_3d.py`/`run_cell.py`/
`sample_2i.py`, 2b's `models.py`, and 2k's own four artifact writers
`power_2k.py`/`make_referents_2k.py`/`run/seal_2k.py`/
`run/campaign_2k.py`). The brief's own count estimate ("38") was
`wc -l` on the printed JSON, not the entry count; the real count is 36,
stated and used throughout.

`IMPORTED_SHA256_2K` pinned from `tests/import_scan_2k.py`: **32
modules**. The first scan (a bare pre-campaign `an.run()` plus
importing every 2k stage tool) found 28 — matching the brief's
estimate minus the sampler-side gap it also flagged: 2k's own
`__init__.py`s, `run/rehearse_2k.py`, `verify_referents_2k.py`,
`exp2j/__init__.py`, `exp3/__init__.py` + `analyze_3.py`,
`exp3c/__init__.py`, and the 2c-battery chain 2i's tree already
imports. Missing: `battery_2k.diff_seed0` LAZILY imports
`experiments.exp3d.rederive_3d.diff_seed` (gate-1 re-derivation),
invisible to a plain pre-campaign run since every rung fails "record
or draws file missing" before `_gate()` ever calls it, and invisible
to a bare `import experiments.exp2k.run.tier_2k` since the RUNNER's
own gate-1 is a separate inline comparison that never imports
`rederive_3d`. `rederive_3d.py` itself is in `FROZEN_FILES_2K`, but
its own module-level import of `analyze_3d.py` (which imports
`functional_3d.py`/`rank_test_3d.py`) was not previously pinned
anywhere. Confirmed by direct dependency read (`analyze_3d.py`'s other
imports — `exp3.analyze_3`, `exp3.sampler`, `exp3c.analyze_3c` — are
already frozen) and reproduced by the whole-suite `test_seal_2k.py`
run, which builds a real tier and genuinely imports this chain: the
scan script now explicitly `import experiments.exp3d.rederive_3d` to
capture it without needing real tier data or model contact. Final: 28
+ `exp3d/__init__.py` + `analyze_3d.py` + `functional_3d.py` +
`rank_test_3d.py` = 32.

`REFERENTS_2K_SHA256` / `N_FILES_2K`: **2649 files**,
`f00dfe78fb2cc2e4886a51366b03c97fb15814f21c8fc23cacdf0c1818a9e937`,
byte-idempotent (built twice, same sha). `make_referents_2k.build`'s
default flipped to `with_campaign=False` (the manifest decision
already ruled): 2j's 2,621-file list + 2j's verdict/`analyze_2j.py`/
`functionals_2j.py` + `power_2k.py`/`run/seal_2k.py` + the five stream
maps + 2d's 36 main-tier record+draws files (18 overlap with 2j's own
list — 2j already reads 2d's main-tier draws directly — so 2621 + 46
extras − 18 overlap = 2649, confirmed by direct set intersection, not
just arithmetic). `--with-campaign` stays for a descriptive
post-campaign listing nothing in the pipeline consumes.

A `bg.load_battery`/re-pin correction along the way: setting
`N_FILES_2K` in Step 3 edits `make_referents_2k.py`, one of
`FROZEN_FILES_2K`'s own members — `FROZEN_SHA256_2K` was re-derived
and re-pinned a second time (only that one file's hash moved, verified
by diffing the two literals key-by-key) after this edit, per the
brief's own contingency ("must not change without re-pinning").

### The bypasses

`full_shape.py`: `_TAG_OK` no longer carries `frozen_check`;
`write_world_2k`'s return no longer carries it either; `run_world` no
longer passes `imports_pinned=False`. All three now run for real in
every world, the seal, and the power tool. Re-run after dropping them:
`test_full_shape_2k.py` 13/13 worlds still reach their terminal (410s);
`test_totality_2k.py` unaffected by this change directly but re-run
throughout as tests were added (see below).

### Six follow-ups from the Task 4 review

1. PROGRESS.md corrections applied in place: the `load_tier_2k`
   exposure restated precisely (every raiser inside is
   `collect_total`-wrapped or total; the two dict lookups are over
   sets proven complete for R_CAP x both sizes — defence in depth, not
   a reachable crash) with the outer wrap now CLOSED (not just
   proposed); `_gate`'s "gate 1 coverage" arm declared dead defensive
   code (`read_rows_2k` already pins coverage); "32 test functions" ->
   "31" for `test_totality_2k.py`; `frozen_from_disk`'s stale
   Task-2-era description refreshed (strict by default now).
2. `analyze_2k.py` `run()`: both `load_tier_2k(...)` calls wrapped in
   `collect_total(..., f"2k tier {size} load")`; unpacked with
   `f3, c = result if result is not None else ([], {})`.

   **Correction (fix round 1 / Finding 2):** the original entry here
   ("skipped by the disjointness test's `a != b` guard") was WRONG —
   the site was not colliding with anything, it was invisible to
   `_all_failure_labels_2k` entirely. That harvester's f-string branch
   (`collect_total\([^,]+,\s*f"([^"{]+)`) requires the call's FIRST
   argument to contain no commas; the original inline
   `lambda size=size: load_tier_2k(root_2k, size, battery=battery,
   verify_fn=verify_fn, rungs=r_cap)` has several (one per keyword
   argument), so the regex could not match past the first internal
   comma and never captured this label at all — `test_collect_total_
   labels_are_prefix_disjoint_and_disjoint_from_2i_2j` passed
   VACUOUSLY, not because of any prefix-collision guard. Fixed by
   binding the thunk to a local name first, `def _tier(size=size):
   return load_tier_2k(...)` then `collect_total(_tier, f"2k tier
   {size} load")`, matching how `_gate`/`_bits`/`_cmp` are already
   written; the regex now matches (`[^,]+` = `_tier`, no internal
   commas). The test now asserts `any(l.startswith("2k tier ") for l
   in labels)` so a future regression is caught rather than silently
   passing.
3. `full_shape.py` W10: `pin_a`/`pin_a410` now captured BEFORE the
   `wrong_pin` mutation, so the world passes the honestly re-derived
   literal and only the on-disk `verdict.json` is corrupted; needle
   `"comparison gate 2k A"` still holds (now via `re-derived != on-disk`
   rather than coincidentally-equal wrong values on both sides).
4. `full_shape.py`: dropped the dead `shutil` and `analyze_2d as a2d`
   imports (grep-confirmed unused).
5. `power_2k.py`: a missing seal now raises
   `RuntimeError(f"refusing: {seal_p} missing — run seal_2k first")`
   instead of a bare `FileNotFoundError`; `test_power_2k.py`'s
   missing-seal test matches `RuntimeError` alone.
6. `analyze_2k.py`: `T_BAR` checked, NOT removed — `verify_referents_2k
   .py` references `an.T_BAR` directly (five call sites), so it is
   live, not dead; `s1_blocks`'s `"per_rung"` dict comprehension:
   `range(4)` -> `range(len(bk.SEEDS_2K))`.

### The mutation harness

`tests/mutation_check.py`, 2j's shape: **83 mutants total** (43
hand-picked — 15 in `battery_2k.py`, 6 in `run/tier_2k.py`, 22 in
`analyze_2k.py` — plus 40 AST-generated via 2i's `_totality_mutants`
over every `collect_total(...)` call site in `analyze_2k.py`, which
has three such functions — `load_2i_tree`, `load_tier_2k`, `run()` —
not one). **89/89 real mutants killed (72 fast + 15 totality + 2 in a
second totality pass); 1 documented equivalent — three committed logs:
`mutation_freeze_fast.log`, `mutation_freeze_totality.log`,
`mutation_freeze_totality2.log`** (the 83-mutant count above is the
build-time snapshot; the freeze added five more, see "Cold re-runs at
the freeze HEAD" below for the sourced tally).

**Equivalent (not a gap): `matched_k_256`'s cap condition `>=` -> `>`.**
At the EXACT tie `256*rate_a64 == 64*rate_b64` (the only point where
the two operators diverge), the fall-through branch computes
`k = floor(64.0 + 0.5) = 64`, `min(64, max(1, 64)) = 64`,
`capped = (64 == 64) = True`, `n_blocks = 64 // 64 = 1` — algebraically
identical to the early return's hardcoded `{"k": 64, "capped": True,
"n_blocks": 1}` for ANY `(rate_a64, rate_b64)` satisfying the tie, not
merely the four numeric pairs checked (0.25/1.0, 0.025/0.1, 0.5/2.0,
0.001/0.004, all confirmed byte-identical). Same lineage as 2j's
`matched_k` upper-clip precedent, one experiment over, same function
family.

**Fixture gaps closed with a new fast test (preferred route, per the
ruling), 10 hand-picked mutants:**
- `read_rows_2k`'s `dps` floor (a stream ONE DRAW LONGER than 64 now
  refused): new parametrize case, `test_read_rows_2k_refusals`.
- `bits_2k`'s seed order: `_rows()`'s existing fixture is seed-symmetric
  by construction (every seed carries the identical i-correct pattern),
  so a reversed seed order was invisible to it; new
  `test_bits_2k_preserves_seed_order` (seed 0 all-correct, seeds 1-3
  all-wrong, asserts the first 64 bits are the all-correct block).
- `tier_record_failures_2k`'s `items_compared` floor (a value ABOVE
  `N_ITEMS` now refused): new parametrize case,
  `test_tier_record_failures`.
- `check_seed_freshness`'s seed-0 assertion, isolated from the
  seeds-1-3 assertion via a `stream_collisions` monkeypatch returning
  `[]` unconditionally: new
  `test_check_seed_freshness_refuses_when_seed_0_is_not_2ds_main_tier`.
- `run_rung`'s model_sha refusal: the committed record's OWN
  `model_sha` field equals 2b's real pin on every real committed cell,
  so a wrong `model_ctx` sha is ALWAYS also caught by the second,
  later refusal (`crec.get("model_sha") != model_sha`) regardless of
  the first — the two checks are behaviorally redundant on real data.
  Isolated by monkeypatching `bk.pythia_sha` to a fake value while
  passing the REAL committed model_sha as `model_ctx`'s sha: new
  `test_run_rung_refuses_against_2bs_pin_even_when_it_matches_the_
  committed_record`.
- `run_rung`'s per-item coverage diff: a seed-0 stream one draw SHORT
  whose matching prefix is byte-identical defeats the per-draw `g != w`
  comparison alone (`zip` stops at the shorter side) — only the
  explicit length check catches it. New
  `test_gate1_catches_a_short_draw_list_even_when_the_matching_
  prefix_agrees`.
- `verdict_tree_2k`'s annotation boundary (`p < ALPHA` -> `p < 0.05`,
  ALPHA = 0.01, not 0.05 — a real gap, not a rounding artifact): new
  `test_tree_annotation_boundary_is_alpha_not_a_looser_literal`
  (p = 0.03, between the two bars).
- `_licensed`'s POWERED branch: no fast test previously asserted the
  plain-POWERED NOT-DENSITY licence distinct from the
  DECLARED-UNDERPOWERED one; extended
  `test_licensed_sentences_carry_the_caveat_and_the_status`.
- `placement_on_ladder`'s log2 interpolation: the existing test only
  bracketed the interior case (`8 < k_equivalent < 16`), which a
  LINEAR interpolation also satisfies; extended
  `test_placement_on_ladder_interpolates_in_log_k` with the exact log2
  value AND a `!=` against the linear one.
- `s3_matched`'s `n_blocks` (hardcoded to 1 would silently pass the
  existing test, since `per[r]["n_blocks"]` reads `matched_k_256`'s
  OWN dict, unaffected by what gets PASSED to `_block_reading`):
  extended `test_s3_matched_thins_b_to_matched_k_and_caps` with
  `n_blocks_used == n_blocks > 1` (the real fixture's k=1/n_blocks=64
  reproducibly gives `n_blocks_used == 64`; a hardcoded 1 caps
  `n_blocks_used` at 1).

**`load_2i_tree` exercised directly on the REAL committed `bi.EXP2I`
tree (2.85s, zero failures on the control), closing 22 of the
AST-generated survivors as fast tests instead of a ~250s/mutant
totality confirmation** — a parametrized
`test_load_2i_tree_collect_total_sites_land_gracefully` (20 cases) plus
three standalone tests for shapes the parametrize form can't express:
the frozen-imports loop (one `collect_total` site executed four times,
`test_load_2i_tree_frozen_imports_loop_forced_exception`), the strata
double-call (`sg.check_strata_pins` is ALSO called internally by
`pr.load_predictor` — a blanket monkeypatch breaks the upstream call
first and never reaches the target; closed with a call-counting
wrapper letting the first call through,
`test_load_2i_tree_strata_pins_direct_call_forced_exception`), and
`outcomes_7b` (guarded by `if not failures:`, so it must run with
nothing else broken, `test_load_2i_tree_outcomes_7b_forced_exception`).
Plus a control, `test_load_2i_tree_clean_on_the_real_committed_tree`.

**`load_tier_2k` exercised directly on one real committed cell
(`_tier_fixture`, ~1s)**, closing 6 more: record read torn, rows read
torn, `_gate` forced exception, `_bits` forced exception, a REAL
seed-0 diff (isolates the `if diffs: raise` line itself, not just
`diff_seed0` raising), and a wrong `committed_draws_sha256` in the
record (isolates `committed_sha=` actually being passed through).

**`run()` exercised directly on an empty root (~1s each)**, closing 3
more: `check_frozen_2k` forced exception, `require_prereg_2k` forced
exception, `mkr.check_referents` forced exception (needs
`referents_sha` set to the real pin, since every other test defaults
it to `False`).

**Correction (fix round 1 / Finding 1):** #26/#27 (`load_tier_2k`'s
`draws_compared`/`per_seed_tallies` checks) are NOT totality-closed —
they are FAST-closed, by two new tests
(`test_load_tier_2k_gate1_catches_a_wrong_draws_compared_attestation`,
`test_load_tier_2k_bits_catches_a_wrong_per_seed_tallies`) added in
fix round 1 after the review found the two `load_tier_2k`-fixture
tests originally listed above (`..._gate1_forced_exception`,
`..._bits_forced_exception`) exercise a DIFFERENT failure inside the
same wrapped function (`diff_seed0`/`bits_2k` raising outright) and
never actually corrupt `draws_compared` or `per_seed_tallies` — the
committed fast log genuinely showed both SURVIVED before this fix.
Confirmed killed by the fast harness: `mutation_check.py --only 26,27`
-> `2/2 killed`.

**Totality confirmation (`test_totality_2k.py` alone, ~250-280s per
run), 14 mutants genuinely require it** — 7 hand-picked (#29-32
`seal_failures_2k`'s four sub-checks, #35-37 the comparison/block
gates) plus 7 AST-generated sites whose guard conditions require a
full, successful pipeline (`check_imports_2k` entry AND exit,
`seal_failures_2k`'s own wrapper, `_cmp`, `_core`, the outer
`load_tier_2k` wrap, the `_sec` secondary-statistic loop). Two new
totality tests were needed beyond what already existed:
- `test_seal_counts_altered` (mutant #29): no existing test isolated
  the plain 256-draw `counts` check from `counts_by_k` — the world
  builder's `missing="seal_counts"` corruption always touches BOTH
  (Ruling 5), so `counts_by_k`'s OWN check alone was enough to fail
  the world regardless of #29's state. New test corrupts `counts`
  only.
- `test_import_surface_exit_failure` (mutant #79): the existing
  `test_import_surface_entry_failure` monkeypatches
  `check_imports_2k` globally, which fails ENTRY first and never
  reaches EXIT (both calls share the same module-level name). Closed
  with a call-counting wrapper, same pattern as the strata double-call
  above.
- `test_comparison_gate_x64_vs_2d_mismatch_detected` /
  `test_comparison_gate_per_rung_d_mismatch_detected` (mutants #35/36):
  gate 1 GUARANTEES x_A^(64) equals 2d's committed count on every
  world this file builds (seed 0 is always the real committed row),
  so neither loop has anything to catch on any EXISTING world
  corruption — confirmed empirically (both survived a dedicated
  `--totality` run before these tests existed). Closed by
  monkeypatching `bi.sampler_counts_pythia` directly (x64-vs-2d) and
  by corrupting v2i's per-rung `d` WITHOUT touching `stratified.T`
  (isolating the per-rung loop from the T-value check that runs
  first).
- `test_comparison_gate_forced_exception` (mutant #77): points
  `verdict_2i_path` at a nonexistent file so `_cmp()`'s first read
  raises before any bad-entry logic runs.

**A process hazard, recorded so it is not repeated:** two
`mutation_check.py` invocations were run concurrently early in this
task (a background `--totality` batch racing a foreground `--only`
run), both targeting `analyze_2k.py` by path. One crashed
(`FileNotFoundError` on its own `.mutation_backup` — the other
process's restore-then-delete cycle raced it) leaving TWO stripped
`collect_total` sites in the live file (`a2d.load_verify` — caught
immediately via a leftover `.mutation_backup`; `bg.load_battery` —
NOT caught by that restore, since the backup itself already carried
the corruption, and silently changed `_totality_mutants`'s own count
from 83 to 82 until noticed). Found by diffing the mutant count
across two fresh imports and confirmed by `git diff` showing the
`((bg.load_battery)(), [])` stripped form in the tracked file; fixed
by hand-restoring the one line and re-verifying `git diff --stat` plus
the fast suite. **Rule going forward, applied for the rest of this
task: never run two `mutation_check.py` processes concurrently** —
`--totality`/`--fullshape` confirmation runs and any `--only` run
against the same three files are strictly sequential, one at a time,
each verified clean (`git diff --stat`, no `*.mutation_backup`) before
the next starts.

### The read sweep

`tests/read_sweep_2k.py`, 2j's shape, run on the real pre-campaign
tree: **4389 distinct paths, 10079 total open/read calls.**
`referents_2k.json` 2650 (2649 manifest files + the manifest pinning
itself), `frozen_module` 50 (36 `FROZEN_SHA256_2K` + 14 upstream
`FROZEN_IMPORT_SHA256_2G`), `instrument_blob` 3, `sha_pin_at_load` 2
(`checkpoints_2g.json`/`checkpoints_2h.json` — read inside
`load_pythia_outcomes`, sha-pinned by the LOADER against a literal
baked into `analyze_2g.py`/`analyze_2h.py`, both frozen — 2j's own
`read_sweep_2j.py` finding, one experiment over, not newly discovered
here), `seal_bound_campaign_absent` 1 (only `bk.seal_path` is
UNCONDITIONALLY attempted pre-`load_power_2k`'s guard; the 36 tier
record/draws paths are never opened at all — `load_tier_2k` checks
`.is_file()` first, which does not go through the wrapped `open()`,
so a missing file never becomes a read attempt), `python_stdlib_venv`
1683. **(e) unpinned: 0 — clean.** The re-run-after-the-seal-tag half
of the brief's instruction does not apply yet: no campaign has run,
so there is no seal tag to re-run after; left for whoever runs the
campaign.

### Design doc §2 disclosure

**Corrected (fix round 1 / Ruling 4):** the original entry here
undercounted — "the import scan and the read sweep each ran
`analyze_2k.run()` once" was wrong on both halves. The exact count,
recovered from the distinct scratchpad output files and moments each
script ran: `tests/import_scan_2k.py` ran **three** times (28 modules;
32 modules after fixing the gate-1 re-derivation import gap; a third,
confirmatory run after an unrelated residual-pin file edit, still 32)
and `tests/read_sweep_2k.py` ran **three** times (first pass, two
unpinned reads found; second pass after adding the `sha_pin_at_load`
bucket, clean; a third, confirmatory pass at Task 5's close) — **six
`analyze_2k.run()` executions on the real, pre-campaign tree total**,
all landing INSUFFICIENT_DATA on the missing 2k tier before reaching a
primary, none printing a T. `experiment-2k-design.md`'s §2 disclosure
paragraph updated to state six and name each script's run count, plus
a clause noting `test_load_2i_tree_*` (`tests/test_analyze_2k.py`)
executes `load_2i_tree` — not `run()`, no statistic, no number — on
the real committed 2i tree on every fast-suite run; disclosed for
completeness though it sits outside the "prints numbers" rule.

### Final numbers

- `FROZEN_SHA256_2K`: 36 modules.
- `IMPORTED_SHA256_2K`: 32 modules.
- Pre-campaign manifest: 2649 files,
  `f00dfe78fb2cc2e4886a51366b03c97fb15814f21c8fc23cacdf0c1818a9e937`.
- Mutation: 83/83 mutants accounted for — 82 real, all killed; 1
  documented equivalent (#13). The tally sums from two committed logs
  (fix round 1 / Finding 1): `experiments/exp2k/mutation_build.log`
  (fast mode, the full 83-mutant run) shows **68/83 killed**, 15
  survivors — mutant ids 13 (the equivalent) and
  {29,30,31,32,35,36,37,75,76,77,78,79,82,83} (14 ids). Every one of
  those 14 is then shown killed in
  `experiments/exp2k/mutation_round1.log`
  (`--totality --only 29,30,31,32,35,36,37,75,76,77,78,79,82,83`):
  `14/14 killed; 0 survivor(s)`. 68 + 14 = 82 real mutants killed + 1
  equivalent = 83 accounted for, entirely from the two committed logs.
- Read sweep: 4389 distinct paths, 0 unpinned.
- Cold battery: 12/12.
- Whole-directory suite (`experiments/exp2k/tests`, all nine test
  files): 157 passed, 1 skipped (the pre-Task-5
  `frozen_from_disk(strict=False)` test, now naturally skipped since
  every `FROZEN_FILES_2K` member is on disk) — 158 collected, up from
  111 at the start of this task.

## FREEZE (task 6, the adversarial freeze) — 2026-08-29, fresh reviewer

Full record: `experiments/exp2k/FREEZE_CHECKLIST.md` (the class defect
with its verbatim demonstration, all 19 attack items disposed, the SDD
ledger's deferred minors and rulings triaged, the cold re-runs, the
ratification package). Zero model contact, zero network. The design doc
is byte-identical to its state at the build's close; slips go to Michael
as exact §-level wording, unapplied.

### THE CLASS DEFECT: FOUND (F-1) — `6abd339d`

The halt scan enumerated ONE of the two artifacts a gate-1 fire leaves.
`run/tier_2k.run_rung` writes `<rung>.HALTED.jsonl.gz` FIRST and the
marker `<rung>.HALTED` SECOND; `battery_2k.halt_markers` globbed
`*/*.HALTED`, which does not match the gz. A kill (or a failed marker
write) in that window leaves the evidence with no marker; `run_rung`'s
skip-if-exists reads the NORMAL pair, so a resumed campaign re-samples
the rung, and if the retry clears gate 1 the tier completes with the
fire's own evidence in the tree and nothing refusing on it. Demonstrated
on a complete density world with
`1b_trained/sub_base8.HALTED.jsonl.gz` present and its marker absent:
BEFORE `halt_markers()` = [] and `run()` = DENSITY, T =
0.9831911740571431, 0 referent failures; AFTER INSUFFICIENT_DATA naming
the gz. All three call sites (analyzer, runner, seal) read that one
function, so the sha-pinned `run/seal_2k.py` is closed without editing
it. 2d F-1 / 2h F-1's lineage.

### Findings

- **F-2** (`90cd05d1`, 2j F-2's lineage): the power record's simulation
  claims were attested and compared to nothing. A record declaring
  POWERED over `rungs_simulated []` with every rung dropped,
  `n_pos_lower_bound` all zero, `t_bar 0.0`, `alpha 1.0`, `n_sim 1`
  passed with 0 failures and its `declared_status` shipped as the field
  that picks between NOT-DENSITY's two licences. Closed with
  `check_power_claims_2k`: `dropped_degenerate`/`rungs_simulated`
  re-derived through `analyze_2i._degenerate_rungs` on the same
  x_A^(256) the primary ran on, `n_pos_lower_bound` against 2i's
  committed `stage1_final` counts, `t_bar`/`alpha` against the firing
  rule's constants, `thin` against the surviving rung count; a record
  attesting none of them is refused as uncheckable. Six failures on the
  same record; world W14, four totality tests, eight fast unit tests.
- **F-3** (`7111e84f`, 3d F-2's lineage): the seal's `files` table was
  checked only against itself, so an emptied table (composite sha
  recomputed, power record re-pointed) attested nothing and the verdict
  stood at DENSITY with 0 failures. Coverage of the 36 tier
  record+draws paths is now required. Honest weight: inert, because the
  seal TAG binds the same 36 paths independently of the table.
- **F-4** (`7111e84f`): gate 1 covers seed 0 and nothing looked at
  seeds 1–3 AS STREAMS. A fault duplicating a stream leaves x^(256) an
  exact multiple of x^(64) — rank-identical, so T back at 2i's own
  .0949: a plausible NOT-DENSITY over a campaign that took no new
  draws, not a refusal. Per-cell duplication census printed in
  `referents.seed_stream_census_2k`; the whole-cell copy refuses. The
  refusal is priced: on 2d's committed draws at these exact cells, 0 of
  9,000 items has a constant 64-draw seed-0 stream, so the shape is not
  producible by the model.
- **F-5** (`286097ae`): design §3.2's fixture, deferred at the build,
  was written — `tests/sampler_call_shape_2k.py`, exp3's real frozen
  `sample_item` against a fake deterministic model, no weights, no
  network, no `test_` prefix so the suite stays torch-free. Seed 0's 64
  draws are IDENTICAL across `seeds=(0,)`, `(0,1)`, `(0,1,2)`, the
  production `(0,1,2,3)` and the reordering `(3,2,1,0)`; seeds 1–3 are
  not copies of seed 0.
- **D-1** (`7111e84f`): `referents.pins_active` stamps which of the
  three test-only bypasses a run took, so a verdict written with a pin
  skipped says so on its face. No production caller passes any of them
  (grep: only `tests/` and the two scan tools).

### Cold re-runs at the freeze HEAD

- whole-directory suite **185 passed, 1 skipped** (161 + 1 at the
  build's close); worlds + totality re-run **50 passed** (14 worlds,
  every terminal and annotation, every refusal reason asserted).
- cold battery **12/12**.
- mutation **90 accounted**: 89 real, ALL killed (72 fast + 15 totality
  + 2 in a second totality pass), 1 documented equivalent (#13). Three
  committed logs: `mutation_freeze_fast.log`,
  `mutation_freeze_totality.log`, `mutation_freeze_totality2.log`. Five
  mutants were added for the freeze's own closures; the two survivors
  of the first totality pass were both new `collect_total` sites and
  were closed with two tests, not documented away.
- read sweep, real pre-campaign tree: **4,389 paths, 0 unpinned**.
- read sweep, SUCCESS path on a world (the coverage the pre-campaign
  sweep structurally cannot reach): **4,686 paths, 0 unpinned**;
  DENSITY, all 8 secondaries computed, 0 secondary failures.
- import scan re-emits **32 modules byte-identical** to
  `IMPORTED_SHA256_2K`; `frozen_from_disk()` re-prints the **36**-entry
  literal identically; `N_FILES_2K` 2,649 and the manifest's own sha
  both match with zero refusals.
- determinism: `run()` twice in separate processes on a world →
  byte-identical verdict JSON, sha256 `fffbc2de…`.
- one altered byte in a SEALED 2k draws file: seed 0 caught by gate 1's
  re-derivation against 2d's committed bytes, seed 2 (outside gate 1)
  caught by the seal's per-file sha. Both INSUFFICIENT_DATA.

### For the tagger

No sha-pinned file was edited, so `FROZEN_SHA256_2K` (36),
`IMPORTED_SHA256_2K` (32), `N_FILES_2K` (2,649) and
`REFERENTS_2K_SHA256` all stand unchanged. Of the three tag-bound
blobs, `analyze_2k.py` and `battery_2k.py` changed at the freeze;
`run/tier_2k.py` did not. Three freeze-time `analyze_2k.run()`
executions on the real tree (read sweep ×1, import scan ×2), all
INSUFFICIENT_DATA, no T — nine pre-tag executions in total, which doc
slip (a) records.

## FINAL REVIEW fix wave

The one fix wave after the final whole-branch review, before the
preregistration tag is cut. All five items additive; no sha-pinned
file touched; the tag not yet cut, so the three tag-bound blobs
(`analyze_2k.py`, `battery_2k.py`, `run/tier_2k.py`) were edited
freely.

1. **§3.2's promised tally comparison.** `run_rung` now compares the
   rung's re-derived seed-0 tally (`bk.tallies_2k(rows, cap,
   verify_fn)["0"]`, both `full_string` and `n_draws`) against 2d's
   committed `crec["per_seed_tallies"]["0"]`, after every seed-0 draw
   has already compared byte-identical and before any normal file is
   written. A mismatch writes the same two artifacts a byte-diff halt
   writes (`<rung>.HALTED` with `kind: "tally"`, both tallies,
   `model_sha`, `committed_draws_sha256`, `stack`, `git_sha`, and
   `<rung>.HALTED.jsonl.gz`), writes no normal files, and raises
   `RuntimeError` containing "GATE 1 FIRED" and "tally". New test:
   `test_run_rung_halts_on_a_tally_mismatch_even_with_byte_identical_
   draws` (a `verify_fn` wrapper that flips exactly the first call's
   verdict). The existing clean-path test already asserted tally
   equality; unchanged.
2. **Pairwise seed-stream census.** `load_tier_2k`'s F-4 census widened
   from the three pairs against seed 0 to all six unordered pairs (0-1,
   0-2, 0-3, 1-2, 1-3, 2-3), with the identical whole-cell-copy refusal
   rule applied to every pair. Caught a real gap while widening:
   `test_analyze_2k.py`'s `_tier_fixture` gave seeds 1-3 the IDENTICAL
   placeholder stream (`" x"` for all three), which the old census never
   exercised (it only ever compared seeds 1-3 against seed 0, the real
   committed data) but the new one immediately flagged as three
   whole-cell copies; fixed by giving each placeholder seed a distinct
   string (`" x1"`/`" x2"`/`" x3"`). The freeze's regression test
   (`test_whole_cell_seed_stream_copy_refuses`) and the clean-tree
   census-shape test (`test_seed_stream_census_is_printed_on_a_clean_
   tree`, now asserting the 6-key dict) updated to match; new case
   `test_whole_cell_seed_stream_copy_between_non_zero_seeds_refuses`
   (seed 2 copied from seed 1 on all 500 items refuses). A second real
   finding surfaced running the cold totality suite: on the "density"
   world fixture, `census["1b"]["antonym"]` is NOT all-zero — pairs
   1-2, 1-3 and 2-3 read **300** (of 500), not 0, because `_tier_rows`
   fills every off-target draw that misses its per-item Bernoulli(q[i])
   with the same literal `" zzz"`, so on any item with q[i] == 0 seeds
   1, 2 and 3 all degenerate to the identical constant 64-draw stream
   — a real, benign partial duplication, well short of the 500-item
   whole-cell-copy bar. The seed-0 pairs stay exactly 0 (seed 0 is the
   real committed stream). `test_seed_stream_census_is_printed_on_a_
   clean_tree`'s assertion corrected to the observed values, with the
   mechanism recorded in the test's own comment.
3. **Torn-pair refusal on resume.** `run_rung`'s skip-if-exists now
   validates before trusting the pair: the record must parse as a dict
   and `bk.read_rows_2k(dpath)` must succeed; any failure raises
   `RuntimeError` naming the cell and both paths and saying the pair is
   torn, must be inspected and removed by the operator before a resume,
   and is never silently overwritten. New test:
   `test_run_rung_refuses_a_torn_pair_on_resume` (a truncated draws gz
   with an intact record; the fake sampler is a bare `AssertionError`
   stub, never called).
4. **`placement_on_ladder` on an empty ladder.** Returns
   `{"k_equivalent": None, "bracket": None}` for `{}` instead of raising
   `IndexError` on `ks[-1]`. New assertion in
   `test_placement_on_ladder_interpolates_in_log_k`.
5. **Dead code in the tag-bound blobs.** Removed the unused
   `from experiments.exp2i import battery_2i as bi` line in
   `battery_2k.py` (grep-confirmed: no `bi.` reference anywhere in the
   file; `analyze_2k.py` and `run/tier_2k.py` import their own `bi` and
   are unaffected) and `run_rung`'s dead `committed_root` parameter
   (grep-confirmed: no caller or test passed it). `ANNOTATIONS_2K` kept
   (plan-mandated, documented).

Verification: fast modules 137 passed / 1 skipped; cold battery 12/12;
`test_totality_2k.py` 46/46 and `test_full_shape_2k.py`'s
density-shape + every-terminal cases 2/2, both in the foreground.
`git status --short` touches only files under `experiments/exp2k/`;
the four sha-pinned files (`power_2k.py`, `make_referents_2k.py`,
`run/seal_2k.py`, `run/campaign_2k.py`) untouched. Mutation harness not
re-run (the controller's call).

## 2026-08-29 — REHEARSAL (dial i, pre-tag, on Michael's word) and the pre-tag cold tools

`python -m experiments.exp2k.run.rehearse_2k --rung antonym --item 0 --size 1b`:
model_sha f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2; 256 draws; seed-0
block vs 2d's committed row: IDENTICAL (64/64). Per seed verified:
0 → 5/64, 1 → 6/64, 2 → 3/64, 3 → 3/64; seeds 1–3 distinct from seed 0
and from each other (first draws differ). Nothing under `results/`
before or after (0 files); tree clean. The four-seed call shape on the
real model reproduces 2d's committed stream — the executable proof
beside the freeze's fixture (`tests/sampler_call_shape_2k.py`).

Cold tools immediately before the tag: `tests/read_sweep_2k.py` — the
TENTH pre-tag `analyze_2k.run()` execution on the real tree
(INSUFFICIENT_DATA, no T; 4,389 distinct paths: manifest 2,650, frozen
50, instrument blobs 3, sha_pin_at_load 2, seal-bound-absent 1,
stdlib/venv 1,683, UNPINNED 0; 0 writes) and `verify_referents_2k.py`
12/12. Both disclosed in design §2. Tag `exp2k-preregistered` follows
at the commit carrying this entry.

## 2026-08-29/30 — CAMPAIGN (on Michael's word "Begin the campaign")

Launched 2026-08-29 20:18 EDT, detached (`campaign_2k`, one child process
per size) with the watcher beside it; complete 2026-08-30 ~07:08 EDT,
**648.9 min**: preflight 1b/float32 OK; the 1b tier 373.0 min (nine
rungs, 33–59 min each); preflight 410m/float32 OK; the 410m tier
275.8 min (26–40 min each). **Gate 1 IDENTICAL on all 18 cells —
32,000 seed-0 draws per cell, 288,000 per size, 576,000 in all,
compared item by item on the production path** (the twelfth
byte-identical reproduction on this stack; the first on nine
non-reversal cells at two sizes). The tally halt never fired (each
cell's seed-0 verified count equals 2d's committed tally by
construction of the identity). No halt marker; zero stops; zero
attrition. Verified per seed, 1b [s0, s1, s2, s3] of 32,000:
add3_mid 10/11/8/12; add_base8 170/150/155/169; antonym
4368/4251/4356/4290; antonym6 3147/3145/3167/3249; arith_next
531/555/518/489; odd6 3195/3208/3268/3214; sub3_mid 34/37/59/45;
sub4_mid 15/9/7/5; sub_base8 723/684/688/704. 410m: add3_mid
17/23/17/14; add_base8 242/241/259/222; antonym 5015/5074/5077/5067;
antonym6 3616/3594/3747/3588; arith_next 831/805/773/797; odd6
2804/2657/2779/2757; sub3_mid 35/33/23/28; sub4_mid 12/12/2/6;
sub_base8 710/637/685/657. The seed-0 column reproduces 2d's committed
main-tier tallies exactly (e.g. antonym/1b 4368 = 2d's .1365 × 32,000).
All 36 record+draws pairs committed and pushed by the watcher (36
commits); watcher stopped after the last pair. Campaign log
`campaign.log`, watcher log `watcher.log` committed with this entry.

## 2026-08-30 — SEAL, POWER, SEAL TAG, PROJECTION, the post-tag sweep, the analyzer

Seal `results/predictor_2k.json` (07:10): 36 files, composite sha
3c4778b06de20c38…, gate 1 re-derived 0 diffs on 18 cells; committed
97d433b3. Power ONCE (07:10 → 08:13, detached): **POWERED — P(fires |
D = .15) = 1.000 against .75; null false-fire rate 0.000; null SD of T
0.0108; P(fires | D = .10) = .489** (the bar decides); rho .171/.256/
.340 at D .10/.15/.20; committed 478f0b5b. Seal tag
`exp2k-predictor-sealed` at 478f0b5b, binds 38 paths (0 failures).
Projection sealed cb64f15a (08:17). Cold battery 12/12 with the seal
and power present. The post-seal-tag read sweep (design: re-run once
after the seal tag) on the complete tree: 4,426 paths, 0 unpinned, the
38 campaign files seal-bound, 0 writes — and it printed the primary at
n_perm 30: **T = 0.1548** (p .032 at 30 permutations, not the
experiment's), five minutes AFTER the projection was sealed. Disclosed
in design §2 (post-tag paragraph) and here. Analyzer launched once,
detached, `--write`, 08:18 EDT.

## 2026-08-30 — CLOSED: VERDICT DENSITY

Analyzer ONCE (08:18–08:49, 31 min, detached): **DENSITY — T .1548,
p 9.999e-05 (0/10,000), POWERED; nine of nine rungs eligible; zero
referent failures; comparison gates exact (A64 = 0.09491251078607414,
A64/410m = 0.11537934925951784, A64 → 2.8b = 0.16722141085849532); gate
1 re-derived 0 diffs on 18 cells; pins_active all real.** Per-rung D:
add_base8 .476, sub_base8 .440, sub3_mid .147, antonym6 .115, odd6
.096, arith_next .092, add3_mid .027, antonym .024, sub4_mid −.024.
S1 blocks .0949/.1077/.0948/.0938 (SD .0066 — one block of four clears
the bar); S2 .0949/.1256/.1433/.1548; S3 thinned-B .2089 vs .1548
(+.054), placement k 9.9 [8, 16]; S4 .1148/.2044; S5 .2277/.2813; S6
410m .1695 (fires), block SD .0034; S7 six-rung mean .207, live items
39/130/30. Projection cb64f15a: verdict-level HIT (worth nothing),
texture 15 hits / 5 misses — sub3_mid .147 (the named mid-digit
disconfirmer fired), add_base8 overtook sub_base8, arith_next +.028
only, S3 increment above range, first-correct above the count.
VERDICT.txt + retrospective.md written; tag `exp2k-closed` follows.
One pre-committed change UNSPENT. Next: close-out propagation on
Michael's word (essay under §6 DENSITY, experiments.md, the supporting
repo graft with the exp2k three tags, Zenodo v1.14, paper inventory).
