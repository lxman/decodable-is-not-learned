# Experiment 2c — Progress Ledger

Design: ../experiment-2c-design.md (ACCEPTED 2026-07-28, freeze
pre-authorized). This ledger records every number, ejection, and
adjudication of the M0 build. Entries are append-only.

## 2026-07-28: Open item 4 closed; order-stats bounds committed

**Mechanism:** Per-fire classification for gate 2 (shuffled labels) uses
quantiles of max-of-2500 null draws. Tolerated = floor fire AND within
central 99%, i.e., z ≤ z₀.₉₉₅. Elevated = floor fire AND z₀.₉₉₅ < z ≤
z₁₋₁₀⁻⁴ (counts toward binomial, never structural abort). Structural
abort = z > z₁₋₁₀⁻⁴.

**Exact bounds (via `experiments/exp2c/stats_bounds.py`):**
- z₀.₀₀₅ = 2.86 (lower tolerance bound; never used for abort)
- z₀.₉₉₅ = 4.61 (upper tolerance bound)
- z₁₋₁₀⁻⁴ = 5.37 (structural abort threshold)

**Worked example:** 2b's two shuffled fires at 3.6 and 4.7 null-SD
classify as tolerated and elevated respectively — count test applies,
no structural abort, matching gate-review ruling (b).

## 2026-07-28: Two design rulings applied to the battery module

Task-4's report (`.superpowers/sdd/task-4-report.md`) flagged two
specs in `experiments/exp2c/battery/generators_rungs.py` rather than
silently redesigning or dropping them. Michael ruled on both.

**Ruling 1 — base5 EJECTED at design time.** N mod 5 = f(N's last
decimal digit), since 10 ≡ 0 (mod 5): the value-mod-10/bin2dec species
design §2 bans, one divisor down from bin2dec's own mod-10. The
`CapabilitySpec` definition stays in source as the record of the catch
(`_base5_spec`) but is never passed to `register()`; it is filed in a
new module-level `EJECTED: dict[str, tuple[CapabilitySpec, str]]`
keyed `"base5"` with the mechanism as the reason string. `base5` is no
longer in `SPECS` or in the tests' `EXPECTED` list. base12 fills the
design's "base-5 or base-12" base_repr slot alone.

**Ruling 2 — caesar_len8 rewired to a real 7-8 letter word pool.**
The prior pool (9 words filtered from 2b's frozen
`experiments/exp2b/battery/wordlists.py` WORDS, read via
`ast.literal_eval`) gave nowhere near the class coverage caesar's own
split needs (n_holdout=39, min_holdout_values=26 vs. 9 words across 7
distinct first letters). New module `experiments/exp2c/battery/
wordlists_2c.py` holds `WORDS_7_8`: **1522** distinct, lowercase,
purely alphabetic, common English words of length 7 or 8 (24 distinct
first letters), built from the intersection of the top-10,000 most
frequent English words (Google Trillion Word Corpus, no-swears list)
and Webster's Second International dictionary headwords, then
hand-reviewed to drop proper nouns/brand names/calendar words that
survive frequency filtering (e.g. bangkok, colorado, webster, zimbabwe,
warcraft, cingular, florence, phoenix, pacific, atlantic, catholic).
2b's wordlists.py is untouched — this is 2c's own data. caesar_len8
now imports `wordlists_2c.WORDS_7_8` directly (normal package import,
not a frozen-file read); `CAESAR_LEN8_WORDS = sorted(WORDS_7_8)` keeps
gen determinism (pool selection driven only by the passed rng and
fixed module list order).

**Tests:** `test_generators_rungs.py` updated — `base5` removed from
`EXPECTED`; new `test_base5_ejected_not_registered` (asserts
`"base5" in EJECTED and "base5" not in SPECS`, reason mentions the
digit-local mechanism); new `test_caesar_len8_pool_is_wordlists_2c`;
new `test_wordlists_2c_sanity` (count ≥ 550, unique, alphabetic
lowercase, length in {7,8}, ≥ 20 distinct first letters). Full suite:
`16 passed` (`experiments/exp2c/tests/`), no regressions in
`test_battery_base.py`, `test_instrument_import.py`,
`test_stats_bounds.py`.
