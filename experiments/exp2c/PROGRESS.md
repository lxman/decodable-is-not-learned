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

## 2026-07-29: analyze.py verdict tree + §4.5 fixture suite (task 10, open item 5 closed)

**Build:** `experiments/exp2c/analyze.py` (the frozen verdict tree:
`AnalyzeInputs` dataclass, `verdict()`) and
`experiments/exp2c/tests/test_analyze_fixtures.py` (8 tests) both
transcribed byte-for-byte from the task-10 brief's Steps 1 and 3 (diffed
against the brief's fenced code blocks — identical). TDD: RED confirmed
first (`ModuleNotFoundError: No module named 'experiments.exp2c.analyze'`
against the test file alone with no analyze.py present), then analyze.py
added, GREEN confirmed (8 passed).

**Runtime, measured not assumed:** un-patched fixture suite (default
`N_PERM=100_000`, `N_BOOT=10_000`) ran in **37.37 s** — under the
brief's ~2-minute bound. Only 4 of the 8 tests reach the costly
permutation/bootstrap loops (the other 4 short-circuit at
`PIPELINE_ABORT` or `INSUFFICIENT_DATA` before `verdict()` gets to the
`spearmanr` loops), so the actual cost is ~4 x 9 s rather than 8 x 9 s.
Per the brief's own instruction to measure before patching, the
pre-authorized `analyze.N_PERM = 2000` / `analyze.N_BOOT = 500`
monkeypatch fixture was **not applied** — both files stand exactly as
given in the brief, with no test-file addition beyond the brief's text.
Full exp2c suite: `38 passed in 39.98s`.

**§4.5 mapping (honest, not papered over).** Design §4.5 names exactly
four provisions verbatim: (P1) one leaking rung -> attrition-without-
abort; (P2) a clean-null shuffled draw at the floor -> classified
tolerated; (P3) an all-flat family -> zero-score ties path; (P4) n below
either floor -> INSUFFICIENT_DATA. All four are covered by at least one
test — no §4.5 provision is untested. But the brief's suite has 8 tests,
not 4: 5 tests map onto the 4 named provisions (P4 covers two floor
types, families and rungs, so it gets two tests), and the remaining 3
tests exercise preregistered rules that live elsewhere in the design
doc, not in §4.5's own list:

| Test | §4.5 provision | Source if not §4.5 |
|---|---|---|
| `test_provision_one_leaking_rung_attrition_without_abort` | P1 | — |
| `test_provision_clean_null_floor_fire_tolerated` | P2 | — |
| `test_provision_elevated_fire_counts_but_never_aborts` | none | Gates §4 item 2 / open item 4 (elevated band never aborts, count-test governs) |
| `test_provision_structural_shuffled_fire_aborts` | none | Gates §4 item 2 ("abort authority lives here and only here") |
| `test_provision_flat_family_zero_ties_path` | P3 | — |
| `test_provision_dual_floor_families` | P4 (families half) | — |
| `test_provision_dual_floor_rungs` | P4 (rungs half) | — |
| `test_verdict_precedence_insufficient_beats_pass` | none | §5 INSUFFICIENT_DATA bullet ("precedence as §1") + analyze.py's own docstring precedence order |

So: no gap on the §4.5 side (4/4 provisions tested), but 3/8 tests are
not §4.5 provisions strictly — they preregister gate-2 classification
behavior and verdict-precedence ordering that the design doc states
elsewhere. Flagging this rather than claiming the suite is "one test per
§4.5 provision, 1:1" — it isn't; it's a superset that happens to fully
cover §4.5 plus two adjacent preregistered rules.

## 2026-07-29: Three review findings amended on ruling (task 10 review)

**Review findings** (transcription approved byte-faithful; the defects
are in the brief's own code, surfaced by preregistration scrutiny):

1. **Vacuous P3 assertion.** `test_provision_flat_family_zero_ties_path`
   asserted `"ties:fam2" in ... or out["rho"] is not None` — the second
   disjunct is unconditionally true for that input (27 rungs, floors
   cleared, rho always computed), so deleting the `ties:` audit line in
   analyze.py could not fail the test.
2. **Unaudited scored=False exclusion.** A rung with no untrained fires
   and `scored=False` was dropped from the scored list silently — no
   audit entry — contradicting analyze.py's own docstring promise that
   every rule that fires appends to the audit list.
3. **Zero fixture coverage on the FAIL branch.** §5's falsifier
   (family-cluster bootstrap CI includes 0 -> FAIL) had no fixture; the
   original 8 tests never reached a FAIL verdict.

**Authorization:** Michael, 2026-07-29. analyze.py and the fixture
suite are ACCEPTED-not-frozen and amendable on his ruling; the design
doc is untouched. Amendments applied exactly as ruled:

1. P3's assertion tightened to `assert "ties:fam2" in
   " ".join(out["audit"])` (first assertion line unchanged).
2. analyze.py's attrition loop gains an `else` branch appending
   `unscored:{name}` for a fire-free scored=False rung — audit-trail
   only; fires keep precedence, verdict logic and the scored list are
   unchanged. New fixture `test_provision_unscored_rung_audited`:
   one `_clean()` rung set scored=False -> `unscored:f0r0` in audit,
   n_rungs 27->26, verdict != PIPELINE_ABORT.
3. New fixture `test_provision_independent_battery_fail_branch`:
   probe and ascent scores independent draws (9 families x 3, battery
   seed 2), full N_PERM=100_000 stats block, asserting FAIL. Seed
   verification: seed 0 gives INDETERMINATE (fluke sample rho 0.4908,
   CI (0.1494, 0.7465) excludes 0 — exactly why the seed had to be
   verified, not assumed); seed 1 FAIL (rho 0.2460); **seed 2 chosen**,
   FAIL with rho -0.0421, naive_p 0.5852, CI (-0.4058, 0.4277) — the
   cleanest independent-battery exemplar. Deterministic: battery seed
   and verdict()'s internal seed (default 0) are both fixed.

**Updated provision map — suite is now 10 fixtures:** the original 8
(P3's assertion now non-vacuous; mapping otherwise as ledgered above),
plus `test_provision_unscored_rung_audited` mapped to the §4.5 audit
premise (the adjudication code's every-rule-audits contract), plus
`test_provision_independent_battery_fail_branch` mapped to §5's
falsifier (FAIL: family-cluster bootstrap 95% CI on rho includes 0).

**Measured:** fixture suite 10 passed in 56.08 s (two new full-stats
calls added ~19 s to the previous 37.37 s; constants NOT reduced, per
the ruling); full exp2c suite 40 passed in 58.58 s.

**Deferred to freeze review (reviewer's Minors, ledgered not applied):**
elevated-attrites breadth, count_test label wording, unused `field`
import in analyze.py, NaN corner.

## 2026-07-29: Reuse manifest built (task 11, design §7)

**Build:** `experiments/exp2c/run/reuse_manifest.py` (design §7: for the 12
survivors, the 2b fits ARE the 2c fits. This manifest pins every reused
artifact by path + SHA-256 so the freeze commit declares exactly what is
reused and `verify()` proves nothing drifted). TDD: RED confirmed first
(`ImportError` with no module present against the test file), then
reuse_manifest.py added, GREEN confirmed (2 passed).

**Manifest contents:** 12 survivors (scored_battery minus attrition list from
m2_report.json). Each survivor has:
- Item file path + SHA-256
- 10 fits per stage (known_absent, m3, shuffled): 2 sizes (410m, 1b) × 5 seeds

**Fit counts per survivor (all 12 identical):**
- known_absent: 10 fits (120 total across 12)
- m3: 10 fits (120 total across 12)
- shuffled: 10 fits (120 total across 12)

(360 is the total across all three stages, not per stage — corrected
2026-07-29 per review Minor.)

**File:** `experiments/exp2c/results/reuse_manifest.json` (82056 bytes).
`verify()` re-hashes all paths at read time — confirmed returning True against
committed file.

**Full exp2c suite:** 42 passed in 58.78s (40 existing + 2 new from this task).

## 2026-07-29: Reuse manifest amended on ruling (task 11 review)

**Review findings** (transcription verified byte-exact and approved; the
defects are in the brief's own code):

1. **Absolute paths contradicting the design's relative-path contract.**
   `build()` stored machine-absolute paths (`/Users/michaeljordan/...`)
   in the committed manifest — the freeze commit's pins would break on
   any other checkout location.
2. **Crash-on-missing verify.** `verify()` called `_sha()` directly on
   each pinned path: a deleted artifact raised `FileNotFoundError`
   instead of reporting drift, and the first mismatch returned a bare
   `False` with no indication of which artifact drifted.

**Michael's ruling (2026-07-29):** pinned paths become repo-relative
(new `ROOT = parents[3]` constant, `_pin()` helper); `verify()` returns
`(ok, drifted)` where `drifted` itemizes every offending repo-relative
path and a missing file counts as drift, never a crash. Tests amended
to match: relative-path assertion added, verify test unpacks the tuple.

**Regeneration:** manifest rewritten with all 372 pins repo-relative
(12 item files + 360 fits; e.g. `experiments/exp2b/battery/items/
add3_mid.json`). `git diff` on the manifest: 372 insertions / 372
deletions, all 744 changed lines are `"path"` lines, zero `"sha256"`
lines changed — hashes unchanged, the artifacts didn't move.

**Tests:** covering pair 2 passed; full exp2c suite 42 passed in
58.19s, no regressions.

## 2026-07-29: Task 12 campaign start — tier-1 smoke pass on mod17

Campaign GO from Michael 2026-07-29. First-ever execution of the
task-7 collection path: `python -m run.screen mod17 --tier 1`
collected both untrained twins (410m npz 13:24, 1b npz 13:51-13:52,
~40 min end-to-end including fits) and returned **tier-1 PASS**.
Per-fit table, transcribed from `results/screen/tier1/mod17.json`:

| size | seed | corrected_p | margin | at_floor | classification |
|------|------|-------------|--------|----------|----------------|
| 410m | 0 | 1.0000 | 0.000 | False | not_fire |
| 410m | 1 | 1.0000 | 0.000 | False | not_fire |
| 1b   | 0 | 1.0000 | 0.000 | False | not_fire |
| 1b   | 1 | 0.0279 | 0.000 | True  | tolerated |

The 1b/seed-1 fit sits exactly at the tier-1 add-one floor
(14/501 ≈ 0.0279) with zero margin — the designed "tolerated"
classification, not a leak signal.

**Cache convention:** activation caches (~190 MB per candidate at
410m, ~258 MB at 1b) are git-ignored at the root, mirroring 2b
(`experiments/exp2c/results/activations/` added to .gitignore,
commit 30021dc). Screen verdict JSONs and campaign fits commit.

**Batch launched:** remaining 13 candidates, sequential
continue-on-error, heavies (count_div13, roman_sum7: 4000 probe
items) last; projected ~9 h. Tier-1 verdict table to be ledgered
from the JSON records when the batch completes.

## 2026-07-29: Instrument observation — tier-1 margin rule is structurally vacuous (freeze-review item)

Observed during the tier-1 batch: `margin` is 0.000 in every fit
record so far, including base12's four `structural_abort` fires.
Traced to the frozen instrument, not a bug in the 2c runner:
`probe_starved` (frozen, exp2b) sets `margin = 0.0` unless
`present = corrected_p < alpha` (lines 139-142), with alpha = 0.01.
At tier-1's n_perm = 500 the Bonferroni add-one floors are
18/501 ≈ 0.0359 (410m) and 14/501 ≈ 0.0279 (1b) — both ABOVE alpha —
so `present` can never be true at tier 1 and margin is always 0.

Consequences, on the record:

1. **Tier-1's margin-bar reject rule (screen.py `_tier1_margin_bar` /
   stats_bounds.TIER1_BAR) can never fire.** All tier-1 reject
   authority rests on the `classify_fire` classification — which is
   working as designed (base12 caught with 4/4 `structural_abort` at
   the p-floor; mod17 correctly tolerated at the floor with a null-
   consistent accuracy).
2. **Tier-2 is unaffected:** at n_perm = 2500 the floors are
   18/2501 ≈ .0072 and 14/2501 ≈ .0056, both below alpha — `present`
   and margins go live exactly as the frozen module's own comment
   intends ("add-one floor x Bonferroni family < alpha", line 56).
3. This also retro-explains task 8's finding that all 40 sibling
   margins in the 2b m3 record are exactly 0.0: those fits were
   `present = False`.

No action taken mid-campaign. Flagged for the freeze-review checklist
(task 13): either ledger the tier-1 margin rule as intentionally
redundant belt-and-suspenders that happens to be unreachable at 500
perms, or drop it from the tier-1 description at freeze so the frozen
record doesn't imply a gate that cannot fire.

## 2026-07-30: Tier-1 screen complete — 13 pass, 1 reject (task 12 step 2)

Batch of 13 finished 03:08:05, zero run failures (all candidates OK;
per-candidate wall-clock 32-98 min, collection-dominated). With the
mod17 smoke run: all 14 new candidates screened at tier 1
(2 seeds x both sizes x 500 perms each). Verdicts transcribed from
`results/screen/tier1/*.json`:

| candidate | verdict | per-fit classifications (410m s0, 410m s1, 1b s0, 1b s1) |
|---|---|---|
| mod17 | pass | not_fire, not_fire, not_fire, tolerated |
| mod19 | pass | not_fire x4 |
| mod13_comp | pass | tolerated, tolerated, not_fire, not_fire |
| add4_mid | pass | not_fire x4 |
| sub4_mid | pass | not_fire x4 |
| base12 | **reject** | structural_abort x4 |
| sub_base8 | pass | not_fire x4 |
| caesar_len8 | pass | not_fire x4 |
| clock24_d999 | pass | not_fire x4 |
| rev_string7 | pass | not_fire x4 |
| count_div13 | pass | not_fire x4 |
| roman_sum7 | pass | not_fire x4 |
| collatz_step2 | pass | not_fire x4 |
| isqrt_gap | pass | not_fire x4 |

All three rescues pass — the label-carrier moves (sum-mod7, step2-mod7,
gap-mod7) survive the untrained screen that caught their 2b parents,
constructive evidence the identified mechanisms were the leaks.
base12 is ejected on the record: the untrained twin decodes the
base-12 label from surface structure in all four fits (add-one
p-floor, structural_abort classification) — the base_repr family's
new rung dies at tier 1, echoing 2b's base-representation leak class.

Pool after ejection: 13 new tier-1 passers across 10 families
(modulus 3, mid_digit 2, base_arith/rotation/counting/clock/reversal
1 each, three rescue families) + 12 reused 2b survivors = 25 rungs,
exactly the >=25 build target; family floor >=9 met by new families
alone. Replacement-rung decision for base_repr goes to Michael
(headroom vs proceed-at-target).

## 2026-07-30: base12_digitsum replacement rung registered (task 12 step 2 iteration)

**Ruling (Michael):** replace base12 in the base_repr family slot rather
than proceed at the 25-rung target without it. `base12`'s own
registration in `battery/generators_rungs.py` stays untouched as the
ejection record — this is a new, separately-registered spec, not an
edit to base12.

**Why base12 fired: the CRT mechanism the module's own analysis
missed.** base12's preregistered `dumbest_baseline` argued a
digit-suffix lookup fails structurally for N mod 12, because 12 never
divides a power of 10. True as far as it goes, but incomplete: N mod
12 CRT-decomposes into N mod 3 (the decimal digit sum) and N mod 4
(the last two decimal digits) — both classic surface carriers, exactly
the kind of statistic an untrained random-projection net can decode
from token structure alone. That is what caught base12
structural_abort x4 at tier 1 (logged above): not a failure of the
"no digit-suffix shortcut" argument on its own terms, but a carrier
the argument never considered.

**Spec definition** (`experiments/exp2c/battery/generators_rungs.py`,
appended immediately after base12's registration): `name=
"base12_digitsum"`, `family="base_repr"`, `dial_name="label_carrier"`,
`dial_value="digitsum_mod5"`, `seed=20260816` (next in the
20260801-20260815 sequence). Label moves off modular arithmetic
entirely: not N mod 12, but the digit-SUM of N's base-12
representation, mod 5. Mod 5 chosen over mod 7 to diversify the
label-move pattern — the three named rescues (roman_sum7,
collatz_step2, isqrt_gap) all moved their label to a mod-7 target;
this rung's mod-5 choice is a different residue count on a different
underlying transform (digit-sum of a base-12 expansion, not a
value-mod computed directly on N). `oracle` reuses base12's own
`_to_base12` helper for the representation and sums digit VALUES (A=10
contributes 10, B=11 contributes 11), then reduces mod 5. `surface_
answer=_to_base12` (identical object to base12's, `is`-equal — the
question asks for the full base-12 string, as base12's does; the
digit-sum-mod-5 probe label is not printed in the question, mirroring
how base12's own last-digit probe label is not printed).
`composability`/`dumbest_baseline` state the CRT-coprimality argument
directly: 5 is coprime to each of 3, 4, and 11, so none of the
surface-legible congruences (mod 3, mod 4, mod 11) that caught base12
determines this label; a random net must fail unless a second,
independent carrier exists. (Coprimality set corrected 2026-07-30 per
review — this entry and the spec originally claimed "5 is coprime to
12, 10, and 11", false since gcd(5,10)=5; the threat model's own
congruence list is {3, 4, 11}, and 5 is coprime to each of those. The
error originated in the controller dispatch text, transcribed
faithfully; see the correction entry below.)

**rescue_of/mechanism_tested: left unset.** Checked `validate_spec`
first — mechanically, `rescue_of="base12"` with a mechanism_tested
string would validate cleanly (the check only requires mechanism_
tested to be truthy alongside rescue_of; no registry cross-reference).
But every existing holder of `rescue_of`/`mechanism_tested`
(roman_sum7, collatz_step2, isqrt_gap) carries a family literally
named `rescue_<x>` (rescue_roman, rescue_collatz, rescue_isqrt) —
100% consistent across all three, and those three name an *original
2b capability* (`roman`, `collatz2`, `isqrt` — real 2b spec names,
confirmed present in `experiments/exp2b/battery/generators*.py`) whose
2b-side leak the rescue re-tests. base12_digitsum's situation is
different in kind, not just in naming: base12 is a 2c-native rung
ejected by 2c's own tier-1 screen, not a 2b capability being
re-imported into 2c under a moved label, and Michael's ruling pins
`family="base_repr"` (matching base12's own family) rather than a
`rescue_` family. Setting `rescue_of="base12"` here would be the first
instance of the field pointing at a same-experiment sibling rather
than a cross-experiment (2b-to-2c) origin, breaking the field's
established, 100%-consistent naming convention. Route taken: leave
both fields `None`; the fire-to-silence contrast is carried in
`dumbest_baseline`'s text alone, which states the CRT mechanism of
base12's catch and why it doesn't reach the new label. Locked in by
`test_base12_digitsum_rescue_route_left_unset` in
`test_generators_rungs.py`.

**TDD.** RED confirmed first: `test_generators_rungs.py` (EXPECTED
list gains `base12_digitsum`; new `test_base12_digitsum_oracle`,
`test_base12_digitsum_surface_answer_matches_base12`,
`test_base12_digitsum_rescue_route_left_unset`) run against the
pre-implementation module — 4 failures, all `KeyError:
'base12_digitsum'`. Then the spec was registered; GREEN — 10 passed.
Worked examples (independently hand-verified before use; all three
candidates checked clean, no corrections needed): 7369 -> "4321" ->
digit sum 10 -> mod 5 = 0; 200 -> "148" -> digit sum 13 -> mod 5 = 3;
9999 -> "5953" -> digit sum 22 -> mod 5 = 2. General-form check across
6 further N values (201, 500, 1728,
4096, 8888, 9998) against an independent in-test divmod-loop digit-sum
reimplementation (not the module's `_to_base12`), mirroring
`test_isqrt_gap_oracle`'s style.

**Wiring:** `battery/gen_items.py` gains `base12_digitsum` entries in
`TEMPLATES` ("Write {a} in base 12." — identical text to base12's),
`BASIS` (`lambda n: (n,)`, identical shape to base12's), and
`SPLIT_PLAN` (`SplitParams()` default, `N_PROBE`, identical to
base12's) — mirrored exactly, no basis-shape derivation needed since
the underlying value space (N token) is unchanged from base12.
`tests/test_gen_items.py`'s `TRUE_ANSWER` registry gains a
`base12_digitsum` entry reusing the test file's own independent
`_to_base12` reimplementation (already present for base12); the
coverage pin `test_true_answer_covers_every_registered_spec` now
passes with 15 specs. New `test_generate_base12_digitsum` (mirroring
`test_generate_mod17`'s probe-label-consistency pattern): recomputes
the digit-sum-mod-5 probe label via an independent divmod loop off the
committed basis N and checks it against every one of the first 50
probe items, plus checks `answer` against the independent
`_to_base12`.

**Generation** (`cd experiments/exp2c && ~/emergence-lab/.venv/bin/
python -m battery.gen_items base12_digitsum`), transcribed from the
printed `[gen]` line, read after the run completed: **500 eval / 2000
probe -> base12_digitsum.json (min val across seeds: 400)** — zero
ejection, matches base12's own committed numbers exactly (500/2000,
min val 400), as expected since the value space and split shape are
unchanged. Spot-checked by hand against the committed file: shots
763->"537", 1548->"A90"; probe item N=7677 -> "4539" (digit sum 21,
probe_label "1"); eval item N=1683 -> "B83" (digit sum 22, probe_label
"2") — all independently recomputed and matching.

**Full suite:** `experiments/exp2c/tests/` — 46 passed in 63.01s
(42 existing + 4 new test functions: `test_base12_digitsum_oracle`,
`test_base12_digitsum_surface_answer_matches_base12`,
`test_base12_digitsum_rescue_route_left_unset` in
`test_generators_rungs.py`, `test_generate_base12_digitsum` in
`test_gen_items.py`; `test_true_answer_covers_every_registered_spec`
and `test_committed_answers_are_true_answers` are existing functions
now iterating one more spec each, not new). No regressions.

**Files changed:** `experiments/exp2c/battery/generators_rungs.py`
(new spec), `experiments/exp2c/battery/gen_items.py` (TEMPLATES/BASIS/
SPLIT_PLAN entries), `experiments/exp2c/tests/test_generators_rungs.py`
(EXPECTED + 3 new tests), `experiments/exp2c/tests/test_gen_items.py`
(TRUE_ANSWER entry + 1 new test), `experiments/exp2c/battery/items/
base12_digitsum.json` (new, generated). `experiments/exp2c/battery/
items/base12.json`, `generators_rescues.py`, and every file under
`experiments/exp2b/` are untouched.

## 2026-07-30: base12_digitsum review corrections (two Important findings)

Review of the base12_digitsum commit (1baa30b) returned two Important
findings, both fixed on this entry's date. Part of the base12 story:
the same review layer that caught base12's missed CRT decomposition
caught a wrong coprimality claim headed for the frozen record.

**1. False arithmetic claim in `composability`.** The spec's text (and
its duplicate in the entry above) claimed "5 is coprime to 12, 10, and
11" — false: gcd(5,10)=5. The error originated in the controller
dispatch text ("your wording, this substance" carried the substance
error verbatim) and was transcribed faithfully; the reviewer caught
it. The sentence's own threat model names the decimal-surface
congruences as mod 3, mod 4, and mod 11, so the correct coprimality
set is {3, 4, 11} (gcd(5,3)=gcd(5,4)=gcd(5,11)=1, all verified). The
`composability` text now checks 5 against 3, 4, and 11 and states
which surface carrier each congruence rides (decimal digit sum, last
two decimal digits, the digit-sum_12 ≡ N mod 11 congruence). Same
pass, the reviewer's Minor: "digit-sum_12(N) = N mod 11 only as a
congruence" used a bare `=` for a congruence; reworded to "is
congruent to N mod 11, but only as a congruence". The entry above
carries an inline dated correction note. The substance of the
argument — none of the surface-legible congruences determines the
digit-sum-mod-5 label — was and remains true; only the stated
coprimality set was wrong.

**2. A/B letter-digit path uncovered by the oracle unit test.**
`test_base12_digitsum_oracle`'s spot values (7369, 200, 9999) and
general-form loop (201, 500, 1728, 4096, 8888, 9998) never produced a
base-12 digit >= 10, so an A/B value mis-mapping in the oracle (the
one normalization wrinkle this spec inherits from base12) would have
passed the suite. Closed with hand-verified letter-digit values:
130 = 10*12+10 -> "AA" -> digit sum 20 -> mod 5 = 0; 143 = 11*12+11
-> "BB" -> digit sum 22 -> mod 5 = 2 (both independently recomputed
before use). Both added as spot asserts, and the general-form loop now
includes 130, 143, and 1548 ("A90", the second committed shot) so the
independent divmod-loop check exercises digit values 10 and 11 too.

**No item regeneration:** the oracle and label definitions are
unchanged — only prose (composability) and test coverage moved.
`git diff` confirmed `battery/items/base12_digitsum.json` untouched.
Full suite after fixes: 46 passed.

## 2026-07-30: base12_digitsum tier-1 PASS — the fire→silence contrast lands (task 12 iteration)

`python -m run.screen base12_digitsum --tier 1` (13:44–14:27, collection
+ fits): **tier-1 PASS**, transcribed from
`results/screen/tier1/base12_digitsum.json`:

| size | seed | corrected_p | at_floor | classification |
|------|------|-------------|----------|----------------|
| 410m | 0 | 1.0000 | False | not_fire |
| 410m | 1 | 1.0000 | False | not_fire |
| 1b   | 0 | 1.0000 | False | not_fire |
| 1b   | 1 | 1.0000 | False | not_fire |

The differential contrast for the base_repr leak is now on the record:
same surface task ("write N in base 12"), same value space, same
basis — base12 (label = N mod 12, CRT-legible via mod-3/mod-4
carriers) fired structural_abort on 4/4 fits; base12_digitsum (label =
digit-sum of the representation mod 5, off those carriers) is silent
on 4/4 with p pinned at 1.0. Fourth fire→silence contrast in the
battery, first at a modulus other than 7 (mod-7 confound caveat
ledgered 2026-07-30). base12_digitsum enters the pool: 14 new tier-1
passers across 11 families + 12 reused = 26 rungs. Tier-2 for
base12_digitsum queued behind the running tier-2 batch.

## 2026-07-30: Tier-2 restructured to 4-way parallel (Michael's ruling)

Measured tier-2 pace: first full-config fit (410m_mod17_seed0) took
69 min wall (12:50 batch start -> 13:59 file mtime), matching the
frozen instrument's known 2b campaign cost at n_perm=2500. Sequential
projection 13 candidates x 10 fits ~ 5.5-6 days. Michael's ruling:
4-way parallel split (2b precedent: its campaign ran these fits
8-way on this machine). Sequential batch killed at ~2 fits of mod17
(deterministic re-run, no loss); relaunched as 4 workers over
disjoint lists, base12_digitsum added to the queue (14 candidates,
4/4/3/3):
A mod17 mod19 mod13_comp add4_mid; B sub4_mid sub_base8 caesar_len8
clock24_d999; C rev_string7 count_div13 roman_sum7; D collatz_step2
isqrt_gap base12_digitsum. Projection ~1.5-2 days wall accounting
for memory-bandwidth contention.

## 2026-07-30: Tier-2 widened to 6-way; llmbox staged for M2 (fleet prep)

Tier-2 widened on Michael's go, 20 min into the 4-way run (loss: two
partial first fits, deterministic redo): workers A/B (4 candidates
each) split into four 2-candidate workers. Now 6 workers — A1 mod17
mod19; A2 mod13_comp add4_mid; B1 sub4_mid sub_base8; B2 caesar_len8
clock24_d999; C rev_string7 count_div13 roman_sum7; D collatz_step2
isqrt_gap base12_digitsum. 2b precedent ran 8-way on this machine.

llmbox assessed and staged for the M2 fit campaign (2b fleet
precedent: llmbox ran m3/410m with 8 workers): idle (load 0.00),
28 GB free RAM, 1.4 TB disk, 12 threads. Repo cloned at 33dfebc via
git bundle over LAN (no GitHub credentials on the box); venv at
~/emergence-lab-venv pinned to the Mac canonical versions
(numpy 2.4.6, scipy 1.17.1, scikit-learn 1.9.0); frozen-instrument
smoke via exp2c screen_arrays on synthetic arrays: not_fire,
p=0.6318, 1.2 s. On the record for M2: cross-architecture BLAS
(x86 vs ARM) can differ in final-ulp float results; 2b's fleet
accepted this; per-candidate box assignments will be ledgered when
M2 dispatches so every fit's provenance is attributable.

## 2026-08-01: Tier-2 screen COMPLETE — 14/14 pass, zero fires in 140 fits

Final worker landed 17:2x 2026-08-01 (clock24_d999). Every candidate
passed tier-2 with not_fire on all 10 full-config fits (5 seeds x both
sizes x 2500 perms); zero fires, zero tolerated, transcribed from
`results/screen/tier2/*.json`:
add4_mid, base12_digitsum, caesar_len8, clock24_d999, collatz_step2,
count_div13, isqrt_gap, mod13_comp, mod17, mod19, rev_string7,
roman_sum7, sub4_mid, sub_base8 — all `pass {'not_fire': 10}`.

**Binomial fire-count test (design §4 gate-1 bookkeeping):** k=0 fires
in n=140 fits vs the preregistered rate 0.064/10 fits (p=0.0064/fit);
expected fires 0.896; binomtest p-value 1.0000 (P(X=0)≈0.41 under the
expectation) — a zero-fire batch is unremarkable, no under-dispersion
signal. These 140 fits ARE the campaign's untrained-gate fits
(known_absent, design §2), all committed.

Campaign mechanics on the record: 6-way parallel on the Mac after the
4-way restructure; per-fit ~100 min under contention; per-candidate
9-22 h (label-space size dominates: caesar 26-class and mod17/19
17/19-class were the slow ones). Tier-2 wall-clock ~2.2 days total.

## 2026-08-01: Scored-battery family map — power-table shape fixed (task 12f, ruling 2026-08-01)

**Two defects in `run/power_table.py::_family_sizes`** (pre-fix, lines
112-123): (1) it counted the screen-ejected `base12`'s item file — tier-1
verdict "reject" (2026-07-30 entry above) — as a live family member; (2)
it never accounted for the 12 reused 2b survivors at all, so the MC
power table modeled only the 14-rung new-spec pool instead of the full
scored battery `analyze.py` will adjudicate.

**Michael's ruling (2026-08-01):** the power table models the FULL
26-rung scored battery. Reused `reverse_string` and `clock24` JOIN their
new siblings' families (`rev_string7` -> reversal, `clock24_d999` ->
clock) — superseding design doc §2's older singleton note, which
predates the new-rung build (that note listed all four of antonym,
odd_one_out, reverse_string, clock24 as singletons). `antonym` and
`odd_one_out` stay singleton: no new sibling was built for either.

**The 13-family map** (26 rungs; sizes sorted desc
`[4, 4, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1]`):

| family | size | members |
|---|---|---|
| modulus | 4 | mod13(reused), mod17, mod19, mod13_comp |
| mid_digit | 4 | add3_mid(reused), sub3_mid(reused), add4_mid, sub4_mid |
| base_repr | 3 | base7(reused), oct2dec(reused), base12_digitsum (base12 excluded: tier-1 reject) |
| base_arith | 2 | add_base8(reused), sub_base8 |
| rotation | 2 | caesar(reused), caesar_len8 |
| counting | 2 | count_div7(reused), count_div13 |
| reversal | 2 | reverse_string(reused), rev_string7 |
| clock | 2 | clock24(reused), clock24_d999 |
| antonym | 1 | antonym(reused) |
| odd_one_out | 1 | odd_one_out(reused) |
| rescue_roman | 1 | roman_sum7 |
| rescue_collatz | 1 | collatz_step2 |
| rescue_isqrt | 1 | isqrt_gap |

**Build:** new module `experiments/exp2c/battery/family_map.py` —
`REUSED_FAMILIES` (the 12 names verified against
`results/reuse_manifest.json`'s `survivors` keys, exact match, no
mislistings to escalate), `scored_battery_families(items_dir,
screen_dir)` (new-pool part: every `items_dir/*.json` spec, skipping
`ejections.json`, whose tier-1 verdict in `screen_dir/tier1/<name>.json`
is "pass" — a missing verdict file or "reject" excludes the rung, so
the map is screen-aware by construction; reused part: `REUSED_FAMILIES`
merged in unconditionally), `family_sizes(...)`. This module is the
freeze-facing family artifact — the analysis-stage family-cluster
bootstrap will use it too, not just the power table.

`run/power_table.py::_family_sizes` now delegates to
`family_map.family_sizes`, screen-aware and reused-inclusive; CLI gained
`--screen-dir` (default `results/screen`) alongside the existing
`--items-dir`. `simulate`/`_run_power_table`/statistics code untouched.

**TDD:** RED confirmed first (`ImportError: cannot import name
'family_map'` against the new test file, no module present). GREEN
after `family_map.py` added: `tests/test_family_map.py`, 4 tests —
real-tree shape (26 rungs / 13 families / exact size multiset), base12
absent + base12_digitsum present with family base_repr, `REUSED_FAMILIES`
keys == manifest survivors keys, synthetic `tmp_path` case (reject
verdict and missing-verdict-file both exclude a new-pool rung; the
reused part still merges in unconditionally). Confirmed on the real
committed tree: `power_table._family_sizes()` returns 26 rungs across 13
families, sorted-desc sizes `[4, 4, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1]` —
matches the ruling exactly. Both import paths exercised (pytest's
`experiments.exp2c...` absolute import, and the `python -m
run.power_table` fallback from `cd experiments/exp2c`).

**Full suite:** `50 passed` (46 existing + 4 new), 58.47s, no
regressions. Power table CLI itself NOT run (controller runs campaign
compute).

## 2026-08-01: Real power table — power gate FAILS at 0.670; FRAGILE fires (open items 1+2 data)

`python -m run.power_table` at the real config (n_sims=5000,
n_perm=5000, 26-rung/13-family ruled shape, rho_family = 0.5
FALLBACK from the degenerate 2b sibling record). Transcribed from
`results/power_table.json`/`.md` (run 19:09–19:15):

| rho_true | calibrated_cutoff | alpha_at_cutoff | power |
|---|---|---|---|
| 0.0 | 0.00400 | 0.0100 | 0.0110 |
| 0.5 | 0.00400 | 0.0100 | 0.4448 |
| 0.6 | 0.00400 | 0.0100 | 0.6702 |
| 0.7 | 0.00400 | 0.0100 | 0.8798 |
| 0.8 | 0.00400 | 0.0100 | 0.9838 |

Fragility sweep (rho_true=0): cutoff 0.00720 / 0.00400 / 0.00140 at
rho_family 0.3 / 0.5 / 0.7 — drift ratio 5.143 > 2, **FRAGILE**.

Readings, on the record:
1. **FRAGILE is load-bearing here**, not formal: rho_family = 0.5 is
   an uninformed fallback (2b siblings all-zero, task 8), and the
   calibrated-naive cutoff depends on it 5x. If true rho_family were
   0.7, the 0.5-calibrated cutoff 0.0040 is anti-conservative
   (true alpha > .01). The calibrated-naive test cannot guarantee its
   alpha under an unknown rho_family.
2. **Design §5's preregistered fallback** for exactly this: "exact
   family-block permutation among same-size families, with the
   achievable permutation count and resolution stated." At the ruled
   shape [4,4,3,2,2,2,2,2,1,1,1,1,1]: same-size groups 2 fours x
   1 three x 5 twos x 5 singletons -> 2! x 1! x 5! x 5! = 28,800
   distinct block permutations; resolution 1/28,800 ~= 3.5e-5 —
   ample for alpha = .01. The exact test needs no rho_family.
3. **Power gate**: 0.6702 at rho_true = 0.6 < 0.75 under the
   calibrated-naive test. Switching to the fallback changes the test,
   so the gate must be re-judged under the fallback's power (not yet
   computed). Battery growth remains the remedy if that also falls
   short. Decisions to Michael before freeze, per §5 ("decided and
   ledgered before freeze").

## 2026-08-01: §5 fallback adopted -- exact family-block permutation test built

**Ruling:** per the FRAGILE finding just above, Michael adopted design
§5's preregistered fallback ("exact family-block permutation among
same-size families, with the achievable permutation count and
resolution stated") for the §5-fallback power computation, decided and
ledgered before freeze as the design's own clause requires. This entry
records the test's build and its operational conventions; `analyze.py`'s
matching amendment (swapping the calibrated-naive test for this one at
adjudication time) is **QUEUED as a separate pre-freeze task, NOT done
here** -- this task built the test and its power machinery only.

**Test, operationally** (`experiments/exp2c/run/power_table.py`, new
functions, `simulate`/`_naive_perm_p*` untouched):

- Rungs are laid out as CONTIGUOUS per-family blocks, in the order of
  the `families` size vector (block *i* occupies indices
  `sum(families[:i])..sum(families[:i+1])`) -- the same layout
  `_battery`/`simulate` already use. Callers own arranging x/y into that
  order; the test carries only sizes, not family labels.
- Under H0, ascent-score family BLOCKS are exchangeable among families
  of the SAME SIZE only (a size-4 block never swaps with a size-2
  block). Within a swapped block, rung order is preserved
  position-for-position (donor's i-th rung -> recipient's i-th
  position) -- blocks are reassigned as units, never internally
  re-permuted. x (probe scores) is never touched; only y (ascent scores)
  is block-permuted, via row-gather on the returned index matrix.
- Exact, exhaustive enumeration: for a same-size group of *m* families,
  *m!* block-reassignments; total = product of *m!* across groups
  (`exact_block_perms`, guarded at 5e6, raises with a clear message
  above that rather than silently exploding). Deterministic and
  RNG-free -- `itertools.permutations`/`itertools.product`'s fixed
  lexicographic order, row 0 always the full identity.
- Statistic: Spearman rho (average-rank ties), same rank-Pearson-on-
  ranks arithmetic as `_naive_perm_p` (Task 9's vectorization
  precedent) -- one matmul across all enumerated rows
  (`_exact_block_p_from_perms`). One-sided exact p = count(rho_perm >=
  rho_obs) / n_perms, identity included (so min p = 1/n_perms exactly;
  no +1 smoothing, unlike the MC test -- enumeration is exhaustive, not
  sampled). `exact_block_p(x, y, families)` returns `{p, rho_obs,
  n_perms, resolution}`.
- **At the real 26-rung/13-family shape**
  (`[4,3,2,2,1,2,1,4,2,1,2,1,1]` from `family_map.family_sizes()`,
  multiset `{4:2, 3:1, 2:5, 1:5}`): total = 2!·1!·5!·5! = **28,800**
  block permutations, resolution = 1/28,800 ≈ **3.472e-5** -- ample
  headroom under alpha=.01 (floor(.01·28800)=288, so p<.01 is easily
  achievable). Verified directly against the committed battery/screen
  tree (not the fixture shapes below), confirming the ledgered figure
  from the FRAGILE entry above; the real `--exact` table itself was NOT
  run (controller runs campaign compute, per task instruction).
- `simulate_exact(families, rho_family, rho_true, n_sims, seed)` reuses
  `_battery`/`_shared_for_target_rho` UNCHANGED; per-sim p comes from
  the exact test at a fixed .01 cutoff (no calibration step -- alpha is
  bounded by construction under exact-permutation exchangeability, not
  estimated against rho_family). Returns `alpha`, `power`, `n_perms`,
  `resolution`.
- `main_exact()` / `python -m run.power_table --exact`: rho_true in
  {0.0, 0.5, 0.6, 0.7, 0.8} at rho_family=0.5, plus a POWER robustness
  sweep at rho_true=0.6 across rho_family in {0.3, 0.5, 0.7} (alpha is
  exact regardless of rho_family -- the sweep is about power
  robustness, not calibration fragility, unlike the naive test's
  fragility sweep). Writes `results/power_table_exact.json`/`.md`;
  family sizes from `family_map.family_sizes()`, screen-aware and
  reused-inclusive, exactly like `main()`. `main()` gained a thin
  `--exact` dispatch at its top (delegates to `main_exact`, returns
  before touching the calibrated-naive body) -- the only edit to
  existing code in this file, beyond relocating the `HERE`/`RESULTS`/
  `ITEMS_DIR`/.../`N_PERM` constants block earlier in the file (default
  parameter values are bound at def-time, not call-time, so the new
  functions' `n_sims=N_SIMS`-style defaults needed those constants
  defined above them; content unchanged, only moved).

**Interaction to name, not pick silently** (escalation clause): the
exact test's block-exchange convention assumes x/y arrive as
contiguous per-family blocks matching `families`' order. The queued
`analyze.py` amendment must group/order its rung score arrays by family
in that same order before calling `exact_block_p` -- e.g. via
`family_map.scored_battery_families()`'s iteration order -- rather than
assuming the raw battery/results ordering already matches family
grouping. This is a mechanical interface contract (the same contiguous-
block layout `_battery`/`simulate` already use), not an ambiguity in the
convention itself, so it did not rise to a STOP; naming it here per the
escalation clause's "don't pick silently."

**TDD:** RED confirmed (`tests/test_power_table_exact.py`'s 7 tests,
stashed against the pre-implementation file, fail with `AttributeError`/
`ImportError` on the new names). GREEN after the implementation: exact
row-set assertions on `families=[2,1,1]` (2 permutations, NOT the naively
expected 2!·2!=4 -- only one size-2 family, so that group contributes
1!=1, worked in the test's comment), a guard-raise assertion at
`[1]*11` (11! > 5e6) vs. a within-guard pass at `[1]*10` (10!
=3,628,800), a hand-computed p=1/6 on `families=[1,1,1]` (x=y=[1,2,3],
Spearman rho worked by hand for all 6 permutations, only the identity
reaches rho_obs=1.0), a determinism check (`exact_block_p` and
`exact_block_perms` both bit-identical across repeat calls), an alpha-
bound check at `[2,2,2,1,1,1,1,1]` (720 perms, chosen because it clears
the p<.01 achievability floor -- `[2,2,1,1,1,1]`'s 48 perms cannot, as
the task brief flagged; alpha slack generous for n_sims=300 MC noise
around the true ~.0097), and a power-monotonicity check (0.8 > 0.4 at
the same 720-perm shape). Full suite: `experiments/exp2c/tests/ -q` ->
**57 passed** (50 existing + 7 new), 70.37s, no regressions.

**Not done here (queued):** `analyze.py`'s amendment to call
`exact_block_p` in place of the calibrated-naive test at adjudication
time; the real `--exact` power table run (`results/power_table_exact.
json`/`.md`) against the committed battery, which will let the ≥0.75-
at-ρ=0.6 gate be re-judged under the test the analysis will actually
use.

**2026-08-01, review hardening (verdict: approved):** multi-rung
block-swap row content pinned (`exact_block_perms([2,2,1])` ==
`[[0,1,2,3,4],[2,3,0,1,4]]`, plus a size-3 pair — the prior fixtures
only swapped singletons, which couldn't distinguish unit-block moves
from internal re-permutation); `exact_block_p` gained a
`sum(families) == len(x) == len(y)` guard raising a named ValueError
(for the queued analyze.py author) instead of a matmul traceback.
Suite 59 passed (57 + 2 new). The review's third minor (alpha-bound
test's loose 0.05 threshold; real net is the hand-computed-p test)
stays open for freeze review, unchanged by ruling.

## 2026-08-01: Integrity incident — leftover 2b fleet-sync loop; record verified intact; loop killed

**Detection:** during task-12x's 19:53 suite run, 4 sha256 pins
(shuffled/410m_sub3_mid_seed0..3) transiently mismatched; implementer
contained it (manifest restored, nothing stale committed) and flagged
upward. Michael confirmed no human activity — investigation followed
(systematic-debugging, full chain in this entry).

**Root cause:** `experiments/exp2b/run/sync_workers.sh` (PID 70644),
the 2b campaign's two-way fleet-sync loop, launched detached
2026-07-20 and never killed when 2b closed (2026-07-27). It cycled
every 240 s for 12 days (4,640 cycles, logs/m2m3/sync.log), rsyncing
between the Mac's frozen `results/probes/` and a stale Jul-25
mid-campaign snapshot at `llmbox:~/exp2b-worker/`. A companion
`tail -f` (PID 97686) was the backing process of the pre-/clear
session's campaign Monitor — same era, same orphaning.

**Integrity verdict:** the Mac record is INTACT. git: every exp2b
file byte-identical to HEAD; reuse-manifest verify(): (True, []) on
all 372 pins. Checksum-mode rsync dry-run over all 770 remote files:
754 content-identical (mtime-only churn); **16 remote files hold
stale mid-campaign content** — m3: 410m_roman_seed0,
410m_sq_mod7_seed0-4, 410m_unscramble_seed3-4; shuffled:
410m_sub3_mid_seed0-3, 410m_units_seed3-4, 410m_unscramble_seed3-4 —
kept off the Mac only by rsync quick-check semantics. The 19:53
transient was this loop's write activity observed mid-cycle.

**Remedies executed:** both processes killed 20:36; stability window
20:36–20:42 confirmed zero further writes, tree clean; llmbox
snapshot quarantined (`~/exp2b-worker` ->
`~/exp2b-worker-ARCHIVED-2026-07-25-snapshot`), so no revival can
sync from it. Session-config note: the stale additional-working-dir
grant (exp2b/results/probes/shuffled) should be dropped at next
session start.

**Hygiene fix (Michael's ruling 2026-08-01):**
`test_verify_detects_no_drift` amended to build to tmp_path
(monkeypatched OUT) — reproduced first (manifest mtime churned on
every pytest run), fixed, verified (mtime stable across runs; suite
59 passed). The ledgered manifest is no longer regenerable by tests.

## 2026-08-01: Exact-test power table — gate fails at 0.416; Michael rules GROW +6-8 rungs

`python -m run.power_table --exact` (20:47-20:48), transcribed from
`results/power_table_exact.md`: at the 26-rung/13-family shape,
n_perms=28,800, resolution 3.47e-5, n_sims=5000 — power at rho_true
0.0/0.5/0.6/0.7/0.8 = 0.008/0.266/0.416/0.616/0.815; observed alpha
0.009-0.011 (MC noise around the exact <=.01 guarantee). Robustness
sweep at rho_true=0.6: power 0.424/0.416/0.416 across rho_family
0.3/0.5/0.7 — flat, as the exact test promises. The alpha guarantee
costs power: block-permutation entropy (28,800) is far below
rung-level entropy.

Growth simulations (simulate_exact on hypothetical shapes, n_sims=
1500, seed 7, decision support only): +2 rungs ~0.54; +3 ~0.56;
+4 best (third 4-rung family + paired singletons) ~0.65. Shapes
reaching 0.75 need ~+6-8 rungs and exceed the 5e6 enumeration guard
-> sampled block permutations (add-one convention preserves exact
alpha) required in the machinery.

**Michael's ruling 2026-08-01: GROW the battery +6-8 rungs toward
the 0.75 gate** (the design's own remedy clause). Sequence: sampled-
permutation machinery extension (reviewed) -> shape sweep -> concrete
rung menu to Michael -> specs/items/screens per the established
pattern -> final power table -> Task 13.

## 2026-08-01: Sampled block-permutation machinery (task 12s, growth ruling 2026-08-01)

Built the sampled-permutation extension the growth ruling flagged as
required for the grown shapes (+6-8 rungs; candidate shapes exceed the
5e6 enumeration guard). `experiments/exp2c/run/power_table.py`, new
functions only -- `simulate`/`_naive_perm_p*` and, for shapes under the
guard, `exact_block_perms`/`_exact_block_p_from_perms`'s OUTPUT are
untouched.

**Statistical basis:** each sampled row is an independent draw of a
UNIFORM permutation within every same-size family group (via
`rng.permutation`, which draws uniformly over the symmetric group),
composed into one rung-index row -- i.e. an i.i.d. uniform draw from the
same block-permutation group `exact_block_perms` would enumerate
exhaustively, not a subset or a distinctness-filtered sample. Rows are
NOT filtered for distinctness and the identity is NOT excluded, per the
spec -- repeats occur with their true group-theoretic probability. The
p-value uses the standard sampled-permutation add-one convention, p =
(1 + #{sampled rho >= rho_obs}) / (M + 1), which preserves
P(p <= t) <= t under H0 for ANY M (the observed statistic counts as one
more draw alongside the M sampled ones) -- this is a different formula
from the exact path's count/n_perms (no +1; valid there specifically
because enumeration is exhaustive, not sampled), implemented as a
SEPARATE function (`_sampled_block_p_from_perms`, arithmetic
deliberately duplicated rather than factored with
`_exact_block_p_from_perms`) so the enumerated path's formula is
untouched by inspection, not just by test coverage.

**Reuse, not duplication:** `sampled_block_perms(families, m, rng)`
shares `exact_block_perms`'s offset/grouping bookkeeping and row-
composition arithmetic via two extracted helpers,
`_block_perm_offsets(families)` (n, per-block offsets, same-size
grouping -- same iteration order as before) and
`_compose_block_perm_row(n, offsets, group_items, combo)`
(within-block-order-preserving row construction, position-for-position,
identical logic to what `exact_block_perms` inlined before). Verified
the refactor byte-preserves `exact_block_perms`'s existing output:
the 9 pre-existing tests, including the two hand-derived row-content
pins (`[2,1,1]`, `[2,2,1]`, `[3,3]`) and the guard-boundary pair
(`[1]*11` raises, `[1]*10` doesn't), all pass unchanged. A third
extracted helper, `_block_perm_total(group_items)`, computes the group
size (product of per-group factorials) without enumerating -- shared by
`exact_block_perms`'s own guard check and the new enumerate-vs-sample
routing in `exact_block_p`/`simulate_exact`, so both always agree on
what counts as "the group size" for a shape.

**Routing:** `exact_block_p(x, y, families, *, max_enumerate=5_000_000,
n_sample=100_000, seed=0)` -- when the exact group size is <=
`max_enumerate`, behavior is byte-unchanged (same enumeration, same
`_exact_block_p_from_perms` dict) plus a new `method: "enumerated"` key;
above it, routes to `sampled_block_perms` with a seeded
`np.random.default_rng(seed)`, add-one p via
`_sampled_block_p_from_perms`, dict gains `method: "sampled"`,
`n_perms`=`n_sample`, `resolution`=1/(n_sample+1).
`simulate_exact(..., *, max_enumerate=5_000_000, n_sample=100_000)`
mirrors the routing: below threshold, unchanged RNG-consumption order
and numeric behavior (perms enumerated once, no RNG use, reused across
all `n_sims`); above threshold, `sampled_block_perms` is drawn ONCE
(also reused across all sims, matching the enumerated path's pattern)
from the SAME seeded `rng` the sim loop's `_battery` draws consume, so
`seed` alone still determines the whole run. Return dict gains
`method`. Defaults: guard 5e6 (matching `EXACT_PERM_GUARD`,
`exact_block_perms`'s own hardcoded ceiling), M=1e5 (resolution 1e-5,
comparable to the enumerated case's typical resolution).

**TDD:** RED confirmed (6 new tests against the pre-implementation
file: `AttributeError`/`TypeError`/`KeyError` on the new
names/kwargs/dict key; the pre-existing 9 tests in the file stayed
green throughout). GREEN after implementation: a uniformity spot check
(500 sampled rows on `families=[2,2,1]`, all members of the enumerated
2-element group -- `tuple(row) in enumerated_set`), a determinism check
on `sampled_block_perms` directly (same seed -> bit-identical rows), an
add-one-vs-enumerated check (`families=[1,1,1]`, x=y=[1,2,3], known
enumerated p=1/6; forced sampled route at M=20,000 lands within .01 of
1/6 and is never below 1/(M+1)), a threshold-routing check (`[2,1,1]`
under the guard -> `"enumerated"` with the pre-extension dict keys
regression-pinned unchanged; forced over a tiny `max_enumerate` ->
`"sampled"` with `n_perms`/`resolution` reflecting `n_sample`, not the
unenumerated exact group size), a determinism check on `exact_block_p`'s
sampled path (same seed -> identical dict), and a `simulate_exact`
method-reporting check (both routes, `n_perms`/`resolution` correct for
each). Full suite: `experiments/exp2c/tests/ -q` -> **65 passed** (59
existing + 6 new), 70.33s, no regressions. Grepped the repo for other
callers of `exact_block_p`/`simulate_exact`/`exact_block_perms` --
none exist yet (the queued `analyze.py` amendment hasn't landed), so
the new keyword-only parameters carry no call-site risk.

**Not done here (per task instruction):** no growth-shape sweep run --
that's the controller's job, next in the ruling's sequence (shape sweep
-> concrete rung menu -> specs/items/screens -> final power table).

## 2026-08-01: Growth composition ruled — B2 (+9 rungs, 35 total, rescues stay singletons)

Sampled-permutation machinery landed (edf83db; sampled-vs-enumerated
agreement verified to 0.0002 on a 36-perm shape; review in flight).
Growth-shape sweep (simulate_exact, n_sims=2000, seed 7, decision
support; +/-0.01 MC noise):

| shape | rungs | group | method | power@0.6 |
|---|---|---|---|---|
| current | 26 | 28,800 | enum | 0.443* |
| +4 pair4+grow3->4 | 30 | 2.18M | enum | 0.682 |
| +6 pair5+grow3->4 | 32 | 21.8M | sampled | 0.731 |
| A: +8 pair5+grow3->4+new2fam | 34 | 240M | sampled | 0.750 |
| B: +7 ling.pairs only | 33 | 13.1M | sampled | 0.722 |
| **B2: +9 ling.pairs + 3 new 2fams** | **35** | **131M** | **sampled** | **0.777** |

(*2000-sim re-read of the 5000-sim 0.416 — MC noise.)

**Michael's ruling 2026-08-01: shape B2.** Composition: base_repr
grows 3->4 (one new rung); antonym and odd_one_out each gain a
sibling (2 rungs); THREE new 2-rung families (6 rungs); the three
rescue families remain pure singletons (their evidential role is the
fire->silence contrast, not ladder statistics). 0.777 gives
certification margin against MC noise and one attrition event.
Certification = full 5000-sim exact table on the BUILT battery after
screening. Next: family/rung design proposals to Michael, then the
established spec->review->items->tier-1->tier-2 loop per rung
(llmbox fleet for tier-2 fits), then recertification, analyze.py
exact-test amendment, Task 13.

## 2026-08-01: Growth design ACCEPTED — 9 rungs, all rulings applied (growth-proposal.md)

The B2 growth design is accepted with Michael's five rulings applied
(drop/reserve, F3 string-as-basis, both wordlists, quad_next replacing
geometric, k=6): build F1 order_stat (median5/median7, position
labels), F2 seq_extrap (arith_next + quad_next, labels mod 7), F3
pos_letter (letter_sum/letter_prod, interior letter labels,
string-as-basis); F4 str_align is the named reserve that promotes on
a full-family tier-1 ejection. Plus base13 (4th base_repr rung),
antonym6 and odd6 (position labels, k=6, new 2c wordlists ANTONYMS_2C
/ CATEGORIES_2C approved with hand-review hygiene criteria). Seeds
20260817-20260825. Full carrier analyses, §4 paper-rejections
(base11 alternating-digit-sum; calendar mod-12 CRT trap; weekday
mod-7 empirical leaker), build sequencing (riskiest first: F3 wave 1),
and the one-attrition margin analysis are in
`experiments/exp2c/growth-proposal.md`.

Two finalization catches on the record: quad_next's attack surface
named at full strength (t4 = 3t3 - 3t2 + t1 identically — a fixed
linear functional of three printed terms; defense = multi-digit mod-7
reservoir opacity, the base7/mod17/mod19/mod13_comp empirical class);
arith_next's generator space is 1,710 < 2,500 default probe items, so
it CERTAINLY needs the reduced-n_probe blessing (sub_base8 precedent)
— queued for a consolidated feasibility-blessing pass at item
generation alongside odd6/order_stat/antonym6's expected overrides.
