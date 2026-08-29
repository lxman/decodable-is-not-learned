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
  forced-exception injection sites + the control, 32 test functions):
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
