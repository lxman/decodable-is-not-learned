# Exp 2j — build ledger

## 2026-08-28 — BUILD, Task 1: `functionals_2j.py`

Instrument at `experiments/exp2j/`: `__init__.py`, `tests/__init__.py`,
`functionals_2j.py`, test `tests/test_functionals_2j.py` (21 tests,
all pass, 0 warnings, "21 passed in 0.49s"). Zero model contact —
every input is a committed item file (`battery_2g.load_battery`) or
committed gzip draw rows (`analyze_2d.read_rows` via
`battery_2i.predictor_draws_path`), read frozen and unmodified.

**Scope**: the four item functionals of design §5.1 (π wrong-target
propensity, L answer length, R repeated-char indicator, O input
overlap), the §5.2 bucket rule and composite-strata builder, verified
bits/counts over committed draw rows, and the §5.4 density-matched
block thinner. Nothing under `experiments/exp2c`, `exp2d`, `exp2g`,
`exp2h`, `exp2i`, `exp3`, `exp3c` touched — imported only
(`harness.normalize_answer`, `analyze_2d.read_rows`/
`tier_draws_path`/`EXP2D`/`load_verify`, `battery_2i.
predictor_draws_path`/`DRAWS_PER_ITEM`/`SAMPLING_SEED`/`N_ITEMS`/
`EXP2I`/`sampler_counts_olmo`, `battery_2g.load_battery`).

**O's lowercasing decision.** `input_overlap` lowercases the item's
`question` before checking each normalized-answer character for
membership; the normalized answer itself is already lowercase (2c's
`normalize_answer`), so both sides of the membership test are
case-folded the same way. Pinned by
`test_input_overlap_lowercases_the_question` (question has
`'Hot': COLD, big?`, answer `cold`, answer_type `word` — overlap 1.0
only because the question is folded before comparison).

**The bucket rule's three branches**, pinned on four rung-scale
(n=500 shape) cases in `test_bucket_median_tie_fallback_and_drop`
(a fifth, six-value case checks the branch logic at toy scale only):
`[2]*196 + [3]*304` → median 3, `v > med` constant → **tie_fallback**,
`sum(b) == 304`; `[0]*400 + [1]*100` → median 0, `v > med` already
two-valued → **median**, `sum(b) == 100`; `[1]*274 + [0]*226` (the R
functional's actual shape on `antonym`) → median 1, `v > med`
constant (nothing exceeds the max) → **tie_fallback**, `sum(b) ==
274`; `[7]*500` → single value → **dropped_constant**, `b is None`.

**`verified_bits` reproduces `sampler_counts_olmo` exactly** on the
two real committed x_B rungs exercised
(`test_bits_reproduce_2i_counts_and_pi_matches_swapped_verify[sub_base8]`,
`[antonym]`): `counts_from_bits(verified_bits(...))` equals
`battery_2i.sampler_counts_olmo((rung,), ...)[rung]` item-for-item
against the committed `experiments/exp2i/results/predictor/olmo1b/
{sub_base8,antonym}.draws.jsonl.gz` files, on both rungs. On the same
two rungs, `normalized_draw(draw, answer_type) == normalized_answers(
cap)[i]` agrees with `verify_fn(draw, cap["eval_items"][i]["answer"],
answer_type)` on 200 randomly sampled `(i, draw)` pairs per rung (seed
0, `np.random.default_rng`) — 400 checks total, 0 disagreements — i.e.
the π predicate's draw-side classification is exactly `verify_fn`
with the target item swapped.

**Build finding (closed same session): a bad label in the brief's own
`test_composite_strata_joins_surviving_functionals_in_order`.** The
brief's table has `pi = [0, 0, 1, 1]` and `R = [1, 0, 1, 0]` — literal
permutations of the identical value multiset `{0, 0, 1, 1}` — yet
expects `report["r"]["pi"] == "median"` and `report["r"]["R"] ==
"tie_fallback"`. `bucket()` is a pure function of the value multiset
(median, then a `>`/`>=` threshold on that median); its classification
cannot depend on item order, so no implementation consistent with
`bucket()`'s own directly-tested cases (median 0.5 on this multiset,
`v > med` already two-valued → "median") can produce different labels
for `pi` and `R` here. Confirmed by direct computation
(`np.median([1,0,1,0]) == 0.5`, `[v > 0.5 for v in [1,0,1,0]] ==
[1, 0, 1, 0]`, two values present → "median", not "tie_fallback"). The
bucketed *values* in the brief's expected `strata["r"]["strata"]`
output were already correct (matching the "median" branch); only the
`"R": "tie_fallback"` label was wrong. Corrected in the committed test
to `"R": "median"`, with the reasoning recorded inline as a comment at
the assertion. `bucket()` and `composite_strata()` are otherwise
implemented and tested exactly as the brief specifies.
