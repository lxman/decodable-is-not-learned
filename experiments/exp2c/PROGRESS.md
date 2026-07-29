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

## 2026-07-28: Rescue label definitions closed (open item 3)

New module `experiments/exp2c/battery/generators_rescues.py` registers
the three named rescues from design §2, each with its label moved off
the surface carrier 2b's dumbest-baseline analysis identified, and
each declaring the taxonomy mechanism it re-tests via `rescue_of` /
`mechanism_tested`:

- **`roman_sum7`** (`rescue_of="roman"`) — roman numeral addition,
  label = (value(A)+value(B)) mod 7. Mechanism tested: "suffix
  sub-alphabet carries value-mod-10" — 2b's `roman` leaked because a
  numeral's own suffix was value-mod-10-legible (margins .64–.82);
  sum-mod-7 is a joint function of both values and is printed on
  neither numeral, so the identified carrier cannot solve it.
- **`collatz_step2`** (`rescue_of="collatz2"`) — two Collatz steps,
  label = ones digit of the second step mod 7 (`result2 mod 7`).
  Mechanism tested: "first step is N-mod-20-legible from final digit
  tokens" — 2b's `collatz2` leaked on the first step's ones digit
  (.74–.81); the second step composes the branch twice and mod 7 is
  off the digit alphabet entirely, so the identified carrier cannot
  solve it.
- **`isqrt_gap`** (`rescue_of="isqrt"`) — integer square root of N
  (100–9999), label = (N − isqrt(N)²) mod 7, the remainder mod 7 (not
  its parity — the brief's draft line self-corrected to this, per
  controller ruling; Step 3 code and Step 1 tests both use the mod-7
  remainder). Mechanism tested: "root's ones digit is constant on
  magnitude bands" — 2b's `isqrt` leaked via wide contiguous bands
  where the root's ones digit holds constant (.36–.44 untrained); the
  gap mod 7 oscillates within every band (period ~2·root+1) and mod 7
  is coprime to 10, so magnitude binning on the identified carrier
  scores chance.

Each rescue's `dumbest_baseline` field states the failure mode
explicitly: a screen failure is constructive confirmation that the
named mechanism, not some other leak, drove 2b's original fire. If a
rescue instead passes tier-1 screening, that is evidence the label
truly moved off the carrier.

Design §2's cap on rescue candidates is 6; these three named rescues
use half of it, leaving headroom for 3 alternates if any of the three
fails tier-1 screening — no additional rescues are registered in this
task, discipline is to name only what was preregistered.

**Tests:** new `test_generators_rescues.py` — `test_registered_with_
mechanisms` (all three in `SPECS`, `validate_spec` clean, `rescue_of`
and `mechanism_tested` both set), `test_roman_sum7_oracle`,
`test_collatz_step2_oracle`, `test_isqrt_gap_oracle` (hand-checked
against `math.isqrt`, including the general-form check across three
N values). Full suite: `20 passed` (`experiments/exp2c/tests/`), no
regressions in the rungs, base, instrument, or stats-bounds tests.

## 2026-07-28: roman_sum7 moved to numeral-string surface (review ruling)

Task-5's report flagged that `roman_sum7`'s `gen` returned raw
integers while its `basis_kind` described a numeral-string pair.
Review upheld the flag as Important: task 6 builds item text by
format-templating over `gen` output, so an int-valued `gen` would have
rendered arabic digits and made the suffix-carrier mechanism test
vacuous. **Michael's ruling 2026-07-28:** `gen` returns the
roman-numeral surface — `(_to_roman(a), _to_roman(b))` for the same
integer draws (same rng call pattern, same seed 20260813) — matching
the caesar_len8 convention (gen returns the transformed surface) and
2b's `_gen_roman`/`to_roman`. `oracle` now takes the two numeral
strings and returns `(_from_roman(A)+_from_roman(B)) mod 7`. Local
helpers `_to_roman`/`_from_roman` (values 1–99) match 2b's notation
exactly but are NOT imported from `experiments/exp2b/battery/`
(importing would fire 2b's own `register()` side effects into the 2c
registry). The label definition (sum mod 7) is unchanged;
`basis_kind`'s "ordered numeral-string pair" text is now accurate
as written. `test_roman_sum7_oracle` updated to string args plus a
1–99 round-trip assert over the helpers.

Same review, factual transcription fix: collatz2's quoted untrained
margin range corrected .74–.82 → .74–.81 (paper Appendix A.2: 410M
.74–.78, 1B .75–.81; the .82 belongs to roman's row) in
`generators_rescues.py` and in the entry above. Two further Minors
(unused numpy import, no gen-determinism test for the rescues) are
ledgered here for final-review triage, deliberately not fixed in the
task-5 amendment.
