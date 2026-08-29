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
