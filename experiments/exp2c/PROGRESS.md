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

## 2026-07-29: Item generation + eval sets committed (task 6, open item 7)

New module `experiments/exp2c/battery/gen_items.py` (`generate(name) ->
dict`, CLI `python -m battery.gen_items <name|all>`) generates and commits
the item file for every registered spec: 2b's item-file schema
(`question, answer, probe_label, basis` per item; `name, description,
probe_label_space, basis_kind, seed, shots, eval_items, probe_items,
feasibility` at the top level) plus the three family fields (`family,
dial_name, dial_value`). `eval_items` floor is 500 (open item 7); `shots`
(2 per spec) are drawn programmatically from each spec's own seeded
`gen`/`oracle` — 2c's `CapabilitySpec` carries no hand-authored `shots`
field the way 2b's does. Feasibility runs through the frozen `splits`
module reached only via `instrument.py` (never a direct `experiments.exp2b`
import).

**BASIS is not the raw `gen()` tuple.** `TEMPLATES` renders question text
directly from `gen()` output (gen output is the item surface, per today's
ruling), but the tuple recorded as `basis` for the starving split is a
*separate*, per-spec derivation (a new `BASIS` dict) matching each spec's
own committed `basis_kind` text — mirroring 2b's `basis_fn` discipline,
which 2c's `CapabilitySpec` has no field for. Verified empirically before
being committed: recording the raw 2-component `(a, b)` for `mod17` (basis_
kind says "first operand token", a single component) starves val to ~80 of
2000 probe items (splits.py's per-component-AND holdout: two independent
20% holds join to ~4%) — confirmed below the 300 floor; reducing to `(a,)`
alone gives 383–440 val items across the 5 seeds. `caesar_len8`'s bare
2-component `(word, shift)` fails a different way — `shift` has only 5
possible values, structurally below `min_holdout_values=15` regardless of
item count; matches 2b's own `caesar` spec (`generators_t2.py`), which
combines `(first cipher letter, shift)` into one string with
`stratify_by_label=True` (each combo value induces exactly one label).
Every `BASIS`/`SPLIT_PLAN` entry was run through `splits.feasibility_report`
before being written into `gen_items.py`; see `.superpowers/sdd/
task-6-report.md` for the full per-spec derivation and the mod17/caesar
worked examples.

**Generation run** (`cd experiments/exp2c && ~/emergence-lab/.venv/bin/
python -m battery.gen_items all`), all 14 registered specs, **zero
ejections**:

| spec | eval | probe | min val (5 seeds) | family |
|---|---|---|---|---|
| add4_mid | 500 | 2000 | 390 | mid_digit |
| sub4_mid | 500 | 2000 | 339 | mid_digit |
| base12 | 500 | 2000 | 400 | base_repr |
| sub_base8 | 500 | 1000 | 355 | base_arith |
| mod17 | 500 | 2000 | 382 | modulus |
| mod19 | 500 | 2000 | 395 | modulus |
| mod13_comp | 500 | 2000 | 402 | modulus |
| caesar_len8 | 500 | 2000 | 381 | rotation |
| count_div13 | 500 | 4000 | 753 | counting |
| clock24_d999 | 500 | 2000 | 383 | clock |
| rev_string7 | 500 | 2000 | 349 | reversal |
| roman_sum7 | 500 | 4000 | 805 | rescue_roman |
| collatz_step2 | 500 | 2000 | 400 | rescue_collatz |
| isqrt_gap | 500 | 2000 | 400 | rescue_isqrt |

14 specs, 11 distinct families, 0 ejections (counts transcribed from the
`[gen] ...` lines the run printed, read after the run completed, per the
Step-5 discipline). Two specs needed a non-default `SplitParams`/`n_probe`
beyond the reduced-basis treatment above: `sub_base8`'s value space (two-
digit octal operands, `a > b`) holds only 1540 unique `(a, b)` pairs, so
`n_probe` is cut to 1000 (1500 of 1540 used); its basis cardinality is
capped at 64 (8×8 ones-digit pairs), so `holdout_frac` is raised to 0.35
(0.2 would hold out 12–13 values, under the 15 floor). `count_div13` and
`roman_sum7` both declare a shared-value-space 2-component basis in their
own `basis_kind` text; both use `shared_components=True`, `holdout_frac
=0.45`, `n_probe=4000` — the same shape and the same fix 2b used for
`gcd`/`sort3_mid`.

**rev_string7's basis needs the Pythia tokenizer.** Its `basis_kind`
("final BPE chunk... as reverse_string") points directly at 2b's
`reverse_string` mechanism, which computes basis via `AutoTokenizer` at
generation time (`experiments/exp2b/battery/generators.py::_final_chunk`).
`gen_items.py` replicates this (`_final_chunk`, lazy-loaded, `models.
load_tokenizer("410m")`), reached through the sys.path entry `instrument`
already opens — no new access path, no forward pass, no model weights.
Flagged here because the task environment's "no language model of any
kind is loaded or queried" reads, on its face, like it could rule this
out; the reading applied is that the lock guards against querying the
eval-side model for predictions, not against a fixed tokenizer vocabulary
identical across trained and untrained checkpoints — matching 2b's own
audited practice (its committed `reverse_string.json` contains real
multi-character BPE chunks, e.g. `'ipe'`, `'cki'`, `'db'`, not truncated
substrings). If this reading is wrong, `rev_string7.json` is the one file
to regenerate.

**Tests:** `experiments/exp2c/tests/test_gen_items.py` — `test_generate_
mod17` (probe ≥1800, eval ≥500, item schema, oracle-consistency on 50
items, family fields), `test_feasibility_recorded` (`min_holdout_values
=15`, `min_val_items=300`, all 5 seed keys present). Full suite: `22
passed` (`experiments/exp2c/tests/`), no regressions. Reproducibility
checked separately (not part of the committed test suite): regenerating
all 14 items into a scratch dir reproduced the committed files byte-for-
byte.

## 2026-07-29: Answer/probe-label conflation caught in review; Fix A applied

**The defect, plainly.** Task-6's `_make_item` stored the PROBE LABEL as
the item's `answer` and baked it into the 2-shot prompts. For the 9 specs
whose templated question asks for the full task result, every committed
answer was false and the shots taught false Q→A mappings (add4_mid:
"What is 6311 + 4830?" → stored "1", true 11141; mod17: stored a mod 17,
true (a+b) mod 17; caesar_len8: stored the first letter, true the full
decoded word). The task-6 report's own self-review line — "oracle-
consistency holds by construction (labels computed from the same gen
outputs...)" — described exactly this defect as if it were a property:
label and answer were consistent with each other because they were the
same value, which is the bug. In 2b the two were always separate
(`collatz2.json`: answer "6998", probe_label "6"). The 5 rescue-style
specs (clock24_d999, count_div13, roman_sum7, collatz_step2, isqrt_gap)
were correct as generated: their templates ask directly for the oracle
output.

**Michael's ruling (Fix A — surface-answer function).** `CapabilitySpec`
gains an optional `surface_answer` callable (default None = the oracle
output IS the true answer). `answer` and `shots` are computed from it;
`probe_label` stays on `oracle`. Rung task definitions (gen/oracle/seed/
description/label spaces) do not change. Source of truth for each repair
is the spec's own preregistered `description` field. Routes taken — all
nine descriptions demand the full task result, so all nine took the
surface_answer route (no retemplating, no ambiguity escalations):

| spec | description (route source) | surface_answer |
|---|---|---|
| add4_mid | "4-digit addition, hundreds digit of the sum" | a+b |
| sub4_mid | "4-digit subtraction, hundreds digit of the difference (a>b)" | a−b |
| base12 | "write N in base 12, last digit of the representation (...values 10/11 are letters in the surface answer only)" | full base-12 string, hex-style A/B letter digits |
| sub_base8 | "octal subtraction, ones digit of the difference, ..." | full octal difference |
| mod17 | "(a+b) mod 17, 3-digit operands" | (a+b) mod 17 |
| mod19 | "(a+b) mod 19, 3-digit operands" | (a+b) mod 19 |
| mod13_comp | "((a+b)*c) mod 13, ...; probe label is the first-stage intermediate" | ((a+b)*c) mod 13 |
| caesar_len8 | "decode a Caesar shift (k stated, 1-5) of a 7-8 letter word" — the capability is decoding the word | full decoded word |
| rev_string7 | "reverse a random 7-letter string" | full reversed string |

The other 5 keep `surface_answer=None` (answer == oracle output ==
probe_label, the 2b div7/month_offset precedent).

**Same review, holdout_frac blessing.** The per-spec `SplitParams`
overrides in `gen_items.py` are blessed as ledgered: 0.35 for sub_base8
(64-value basis; 0.2 holds 12–13 values, under the 15 floor), 0.45 for
count_div13 and roman_sum7 (shared-2-component bases, 2b's gcd/
sort3_mid precedent and figure), the 0.2 default for the other 11.
Floors (`min_holdout_values=15`, `min_val_items=300`, 5/5 seeds) bind
throughout. The BASIS-dict derivation and the rev_string7 static-
vocabulary tokenizer path were both upheld on review.

**Regeneration** (`cd experiments/exp2c && ~/emergence-lab/.venv/bin/
python -m battery.gen_items all`): counts identical to the first run —
the rng streams are untouched by the fix — 0 ejections. add4_mid
500/2000 (min val 390), sub4_mid 500/2000 (339), base12 500/2000 (400),
sub_base8 500/1000 (355), mod17 500/2000 (382), mod19 500/2000 (395),
mod13_comp 500/2000 (402), caesar_len8 500/2000 (381), count_div13
500/4000 (753), clock24_d999 500/2000 (383), rev_string7 500/2000 (349),
roman_sum7 500/4000 (805), collatz_step2 500/2000 (400), isqrt_gap
500/2000 (400). `git diff` confirmed exactly the 9 affected item files
changed and only their answer/shots lines (questions, probe labels,
bases, feasibility untouched); the 5 unaffected files regenerated
byte-identical. mod17's diff arithmetic reconciles: 175 of 2500 answers
unchanged = exactly the 175 items with b ≡ 0 (mod 17), where the old
stored label coincided with the true answer.

**Verification discipline restored.** New test
`test_committed_answers_are_true_answers` reads the COMMITTED
`items/*.json` for all 14 specs and independently recomputes the true
answer from the question TEXT alone (2b's oracle discipline), over the
shots plus the first 25 probe and 25 eval items per spec;
`test_true_answer_covers_every_registered_spec` pins the verifier table
to `SPECS` so a future spec cannot land unverified. This test fails
against the pre-fix committed items (RED confirmed on add4_mid's first
shot before the fix was applied) — it is the test that would have caught
the defect. Full-file checks (all 2500/1500 items, not the sample) were
additionally run on base12 and sub_base8: 0 mismatches. Full suite:
`24 passed`.

## 2026-07-29: Family-correlation nuisance parameter estimated (task 8)

**Source:** Experiment 2b sibling-pair seed-margin vectors, m3 fits, tag
exp2b-closed (all 40 committed files verified present).

**Finding — all sibling vectors degenerate:** The seed-margin vectors
for both sibling pairs (add3_mid/sub3_mid and base7/oct2dec) across both
model sizes (410m, 1b) are uniformly all-zero. Standard deviation = 0
for all 4 size-pair combinations; correlation undefined. The code
correctly returns None for per-pair r values and applies the documented
fallback.

**Nuisance parameter:** `rho_family = 0.5` (fallback, no valid
correlations to estimate). Per design §5, this feeds open item 1's
fragility decision: if all sibling margins remain zero at the eval stage
(no family structure to exploit), MC calibration defaults to the
symmetric conjugate prior ρ=0.5, and the discovery procedure's power
bounds widen accordingly.

## 2026-07-29: Permutation-p vectorization ruling (task 9, plan deviation)

**Ruling (Michael):** the task-9 brief's verbatim `_naive_perm_p` — a
Python loop of per-permutation `scipy.stats.spearmanr` calls — is kept
in `run/power_table.py` as `_naive_perm_p_loop`, docstringed as the
reference implementation from the plan text; the path that actually
runs is a vectorized equivalent (`rankdata` once with spearmanr's own
average-rank semantics, the SAME `rng.permutation` call sequence, only
the Pearson-on-ranks arithmetic vectorized, p-value formula unchanged).

**Guard:** `test_naive_perm_p_equivalence` asserts EXACTLY equal
p-values (no tolerance) between loop and vectorized paths across 3
seeds x 2 family shapes at n_perm=200 — all 6 combinations equal.
Exactness is not luck: centered rank products are dyadic rationals
whose float64 sums are exact, so within each pipeline the statistic is
strictly monotone in the exact rank-covariance and the `perms >= obs`
counts coincide.

**Why:** the brief's Step 1 header claims "tiny config, seconds not
minutes," but its verbatim test parameters (n_sims=400/300, default
n_perm=1000) drive ~2.0M spearmanr calls through the loop — measured
164.9 s for the two-test pair on the M4 Pro, breaching the 2-minute
suite bound; the same loop projected Task 12's real table (n_sims=5000,
n_perm=5000, 8 simulate calls) at ~9-10 h. Escalated rather than
patched silently (preregistration text); ruled as above.

**Measured after vectorization:** focused pair + equivalence test
2.30 s (was 164.9 s for the pair alone); Task 12 projection ~5-6 min
total (0.41 s measured at n_sims=50/n_perm=5000 on the real 14-rung
family shape, x100 x8 calls) — was ~9-10 h. The brief's two verbatim
tests are byte-untouched and now run through the vectorized path.
main() wiring smoke-tested at tiny config to a temp dir only
(family sizes [3,2,1x9] read correctly, ejections.json skipped,
rho_family=0.5 read from results/family_corr.json); results/ gains no
files from task 9 — the real table lands at task 12.
