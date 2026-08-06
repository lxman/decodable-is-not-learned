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

## 2026-08-01: Growth wave 1 built — pos_letter registered + items committed; two wordlists drafted (tasks W1a/W1b)

**Wave-1 rungs (proposal §6: riskiest first).** `letter_sum` (seed
20260824) and `letter_prod` (seed 20260825) registered in
`battery/generators_rungs.py` exactly per the accepted proposal §3 F3 +
ruling 2 (string-as-basis): 8-letter uniform a–z string S, i,j ∈ [1,8]
printed alongside, read position p = ((i∘j) mod 6) + 2 (1-indexed,
interior 2–7 only), probe label = the letter at p, `surface_answer=None`
(the question asks for the letter directly, so answer == probe_label —
the rescue-style shape, not Fix A's). Basis = (S,) alone; i and j are
printed decoys that never enter the basis. SPLIT_PLAN: default
`SplitParams` + `stratify_by_label=True` (caesar precedent), N_PROBE
2000. The position-distribution arithmetic is IN the spec texts at full
strength and pinned by enumeration in
`test_pos_letter_position_distribution`: sum 10,10,11,12,11,10 of 64
(near-uniform, max 0.1875); prod 21,5,14,7,13,4 of 64 (0.328
concentrated on p=2 — the named F3b risk; sharpest fixed-slot attack
~0.35 accuracy against ~0.04 chance IF slot-letter identity is
decodable untrained, which reverse_string's fixed-position 0.000
precedent says it is not; the screen adjudicates).

**TDD.** RED first: 12 failures against the pre-implementation modules
(KeyError-shaped on the new names, coverage-pin set mismatch,
FileNotFoundError on the not-yet-generated item files), 12 pre-existing
tests green throughout. GREEN after registration + wiring: 9 new test
functions (6 in test_generators_rungs.py: registration/dial/seed pins,
hand-worked oracle vectors on 'qwertyui' for both ops, gen
shape/interior-position sweep, the position-distribution enumeration
pin, determinism; 3 in test_gen_items.py: per-rung generate checks
recomputing the label from question text + committed basis, and the
SPLIT_PLAN stratification pin). TRUE_ANSWER gains both rungs
(`_true_pos_letter`, independent recompute from the question text; i, j
are the first two integers printed, constants 6/2/1 follow).

**Generation** (canonical venv, `python -m battery.gen_items`): both
rungs 500 eval / 2000 probe, zero ejections; min val across seeds 397
(letter_sum) / 400 (letter_prod), floors 300/15 cleared; all 26 letter
classes populated on both rungs (min class 56). Hand spot-checks of
shots + first probe/eval items recomputed clean. Full suite after
generation: **74 passed** (65 + 9), no regressions.

**Adversarial review (subagent, verified):** every one of the 2,500
items + 2 shots per rung independently recomputed from question text
alone — zero mismatches; committed files bit-reproduced from their
seeds; both distributions re-enumerated and every number in the spec
texts confirmed; reverse_string's 0.000-margin precedent verified
against all 10 committed 2b known_absent fits. **No Critical or
Important findings.** Three Minors, adjudicated:

1. **Proposal §5 wording contradiction (fixed in place):** §5's
   override row said "pos_letter: default SplitParams() expected,"
   contradicting §3 F3's own `stratify_by_label=True` text and §5's
   k-class row ("stratified"). The build follows §3 (the specific
   clause); §5's row corrected with a dated note. No code change.
2. **Feasibility record under-specifies the split (ledgered, no
   action):** the frozen `splits.feasibility_report` serializes only
   holdout_frac/n_holdout/min_holdout_values/min_val_items, so the
   committed item JSONs cannot show `stratify_by_label` (or
   caesar_len8/count_div13's flags before them). Battery-wide,
   chargeable to the frozen instrument; runtime reads SPLIT_PLAN, not
   the JSON. Preregistration readers: the JSON alone is not the full
   split spec.
3. **letter_sum shot collision (FLAG for Michael, no unilateral
   change):** both committed letter_sum shots land on p=2 by seed
   luck, and shot 1's string ('wwvhyodg', S[1]=S[2]='w') is jointly
   consistent with a spurious "answer = 2nd letter" rule — the
   family's own named fixed-slot attack, handed to the M4 eval model
   as two consistent exemplars (~0.22 accuracy for a slot-2 reader on
   the sum op). letter_prod's shots show p=5/p=2 (fine). No
   preregistered criterion governs shot diversity, the seed is
   proposal-assigned, and shots are a constant prefix for probe-side
   activations — so tier-1 proceeds unaffected; but if Michael wants
   shot-position diversity enforced (e.g. redraw shots from the same
   seeded stream until the two demonstrate distinct p, as a
   battery-wide forward rule), the change must land BEFORE tier-2,
   whose fits are the campaign's untrained-gate fits and whose cached
   activations embed the shot prefix. Queued as a ruling question.

**Wordlists (ruling 3, long-pole per §6, drafted in parallel):**
`wordlists_2c.ANTONYMS_2C` — 130 pairs (65 adjective + 65 noun,
POS-segregated sublists so antonym6's distractor draws can stay within
the cue's own POS; floors ≥90 total / ≥60 per sublist). Construction
rules, each excluding a named carrier (module docstring): no
derivational-negation pairs, no shared prefix/suffix ≥3 or edit
distance <3 within a pair (the §2(b) answer-resembles-cue carrier), no
pair length gap >4, every token unique across the pool, and pair- AND
token-level disjointness from 2b's frozen ANTONYMS (stronger than the
ownership rule: the antonym family's two rungs share zero vocabulary,
so the family-honest ρ cannot ride shared word idiosyncrasies).
`wordlists_2c.CATEGORIES_2C` — 10 fresh territories × 8 members
(floors ≥8×6), all disjoint from CATEGORIES_2B's ten; morphological-
clustering rule (no ≥3-letter prefix/suffix shared by ≥3 members of a
category), mean-length band 4.0–6.0, ≥5 distinct first letters per
category — occupations (-er/-or/-ist) and ball sports (-ball) rejected
as territories on exactly this rule. All criteria are programmatic in
the new `tests/test_wordlists_2c.py` (9 tests; RED confirmed on the
missing names first). The tests earned their keep immediately: the
first draft shipped four violations my hand check missed
(meek/assertive, cluttered/bare, shy/outgoing at length gap 5;
predator/prey at shared prefix "pre") — two dropped, one replaced
(bashful/outgoing), predator/prey dropped. **Still pending: Michael's
hand review of both lists (his ruling requires it) before antonym6/odd6
items generate in waves 2–3.**

**Next:** tier-1 screens on letter_prod (first — position-concentration
risk) then letter_sum; verdicts ledgered here; then wave 2 (order_stat,
seq_extrap, odd6) per §6.

## 2026-08-02: pos_letter FULL-FAMILY EJECTION at tier-1 — F4 str_align promotes (pre-ruled fallback)

Tier-1 verdicts, screened riskiest-first per §6: **letter_prod REJECT**
(structural_abort x4: 410m p=0.03593 at floor both seeds, 1b p=0.02794
at floor both seeds, null_mean 0.038) and **letter_sum REJECT**
(structural_abort x4, same shape, null_mean 0.038-0.039). Both rungs
beat every one of 500 null permutations in at least one (layer, slot)
candidate with z past the abort gate -- the base12 classification
pattern, now on the growth battery's riskiest family.

**Diagnostic reading (record, not reinterpretation):** the proposal
flagged F3b's position concentration (21/64 on p=2) as the named risk
and F3a's near-uniform distribution (max 12/64) as the safer sibling.
BOTH fired identically. So the carrier is not the concentration dial --
the family's disclosed structural gamble lost outright: the position
arithmetic is unstarvable (i, j printed, low-complexity map), the
per-string holdout starves only string identity, and the screen says
untrained random projections DO express enough of the
computed-position/slot-letter composition to decode the label. The
honest-disclosure text in both specs ("the untrained screen is the
arbiter of the variable-index gather") is now the ejection record's
own epitaph. reverse_string's fixed-position 0.000 precedent does not
extend to variable-index reads -- a genuinely new datum for the
methods-paper leak taxonomy (positional-gather class: probeable from
untrained activations when the index is surface-computable).

**Consequences:**
- Registrations stay in `generators_rungs.py` as the ejection record
  (base12 pattern); `family_map` auto-excludes both via the tier-1
  verdict files; items/*.json stay committed as generated.
- The letter_sum shot-diversity flag (2026-08-01 entry, Minor 3) is
  MOOT for letter_sum itself (rung dead); the underlying ruling
  question -- whether shots must demonstrate distinct
  positions/labels battery-wide -- stays open and now applies
  forward to str_align and the wave-2/3 builds.
- **F4 promotion is automatic, not a new decision:** ruling 1 named
  str_align the reserve "enters only under §7's fallback," and §7's
  fallback is exactly this case ("a full new 2-rung family ejects:
  ...F4 str_align enters, seeds 20260826-20260827, spec at build
  rigor in §3, restoring ...the 35-rung shape"). hamming8 (20260826)
  and hamming12 (20260827) build next through the same
  spec -> review -> items -> tier-1 loop, screened at the front of
  their wave (MEDIUM-HIGH: the shared-chunk carrier vs the 4-letter
  alphabet, §3 F4), before the wave-2/3 low-risk rungs are built.

## 2026-08-02: F4 str_align build BLOCKED at generation — label-tail infeasibility, ruling requested

hamming8 (20260826) and hamming12 (20260827) registered per §3 F4 at
build rigor (4-letter alphabet, Hamming match count, shared_components
basis over both strings, holdout 0.45, n_probe 4000 — the count_div13/
roman_sum7 figures), TDD RED (10 failures) -> GREEN, with the alphabet
arithmetic and both Binomial spreads verified by enumeration and
written into the spec texts. The composability text records the
pos_letter lesson explicitly: no data-dependent index anywhere in this
family.

**The catch (the proposal's own flag, now empirical):** generation
fails in the frozen `starving_split` — full label-class coverage is
required on both split sides, and the Binomial(L, 1/4) tails cannot
provide it. hamming8's assigned seed realizes a match-count-7
singleton (~1.5 expected per 4000 items; P(7) = 24/4^8 ≈ 0.00037);
hamming12 is infeasible outright (classes through 10 realized, ≥8
sparse; P(8) ≈ 0.0024). §5's constraint row predicted this exact
failure ("label imbalance may fail min_holdout_values on the sparse
high-count classes — flag") and its remedy verb is *flag*, so the fix
is a ruling, not a unilateral build decision.

**Verified remedy (data, not speculation) — rejection-sample the tail
at generation; feasibility 5/5 split seeds at n_probe 4000:**

| L | cap (max label) | classes | min-class expectation | verdict | n_val range |
|---|---|---|---|---|---|
| 8 | none (as spec'd) | 9 nominal | ~1.5 items @ 7 | INFEASIBLE at assigned seed | — |
| 8 | 6 | 7 | ~15 @ 6 | feasible, fragile margin | 807–825 |
| 8 | **5** | **6** | **~92 @ 5** | **feasible, robust** | 790–824 |
| 12 | none (as spec'd) | 13 nominal | — | INFEASIBLE | — |
| 12 | **7** | **8** | **~46 @ 7** | **feasible** | 781–844 |
| 12 | 6 | 7 | ~160 @ 6 | feasible, very robust | 801–826 |

Recommendation carried to Michael: **cap 5 for hamming8 (labels 0–5,
6-class exact), cap 7 for hamming12 (labels 0–7, 8-class exact)** —
robust core for the 8-length rung, richer label space preserved on the
12-length rung so the length dial keeps its wider-count-range story;
fall back to cap 6 on hamming12 only if the real generation stream's
per-seed report wobbles. k ∈ [5,26] holds either way. The oracle stays
exact on every printed item; the question surface is unchanged; the
probe_label_space text will state the truncation explicitly if ruled.

**State pinned pending the ruling:** the registered specs keep the
proposal's uncapped construction;
`test_generate_hamming_blocked_infeasible` pins generate() raising
SplitInfeasible for both rungs (the catch IS the record), and the
committed-answers sweep skips the two blocked names via
_BLOCKED_ON_RULING. Full suite 89 passed. Tier-1 for str_align waits
on items; waves 2–3 wait per §6 (F4 screens at the front of its wave,
before the low-risk rungs are built).

**Also open for Michael (carried forward):** (1) wordlist hand review
(ANTONYMS_2C 130 pairs, CATEGORIES_2C 10×8) before antonym6/odd6
generate; (2) the shot-diversity forward rule (letter_sum's flag is
moot, the question now applies to str_align and waves 2–3); (3) push
authorization for today's commits.

## 2026-08-02: Label-tail ruling applied — str_align built at caps 5/7; review clean; SUPERSEDES the blocked-pin state

**Ruling (Michael, 2026-08-02): "Follow your recommendation"** on the
ledgered feasibility table — hamming8 caps its label at 5 (labels 0–5
exact, 6-class; rejects P(>=6) ≈ 0.0042 of pairs at generation) and
hamming12 caps at 7 (labels 0–7 exact, 8-class; rejects P(>=8) ≈
0.0028 — the ledgered per-class table's 0.0024 was P(8) alone). The
previous entry's pinned state is superseded exactly as designed:
`test_generate_hamming_blocked_infeasible` and `_BLOCKED_ON_RULING`
are deleted, replaced by real generation checks that enforce the cap
over the WHOLE committed file plus a gen-level cap-and-coverage sweep
(1000 draws must respect AND reach the cap).

**TDD:** RED 5 failures against the uncapped generators (label-space
text pins, cap violations, SplitInfeasible where success now expected)
→ caps applied in `_gen_hamming(rng, L, cap)`'s rejection loop only
(oracle untouched — exact match count on every printed pair) → GREEN.
**Generation:** both rungs 500 eval / 4000 probe, zero ejections; min
n_val across seeds 784 (hamming8) / 806 (hamming12) — dead on the
0.45² × 4000 ≈ 810 expectation; every retained class populated. Full
suite **90 passed**. Spec texts state the truncation and its ruling
provenance; growth-proposal.md §3 F4 and §5 now carry dated
annotations for the promotion and the amended label spaces (the §5
pos_letter row also annotated ejected).

**Adversarial review (subagent, verified): no Critical.** All 9,004
items + 4 shots recomputed independently from question text — zero
mismatches; both committed files byte-identical under full-pipeline
regeneration; simulating the UNCAPPED stream at the same seeds
reproduces the ledgered infeasibility exactly (hamming8: single
count-7 item; hamming12: classes through 10 with 9/10 singletons) —
independent attestation that the catch was real. Label distributions
fit truncated Binomial (χ² p=0.92 / 0.30). Findings adjudicated:
1. **Important (fixed by THIS entry):** the ledger ended on the
   blocked-pin state while the tree carried the ruled build, and the
   ruling text lived only in code comments. This entry is the ledger
   record of the ruling, the build, and the supersession.
2. **Minor (fixed):** `generators_rungs.py` ruling comment said
   P(>=8) ≈ 0.0029; exact value 46666/4^12 = 0.00278 → 0.0028.
   Independently reverified before the fix.
3. **Minor (fixed):** growth-proposal.md annotations above.
Reviewer observation (no action, noted): importing exp2c's `battery`
after `instrument` can let exp2b's same-named package shadow it via
the shim's sys.path entry — fails loudly if tripped; the documented
`-m battery.gen_items` path is unaffected.

**Shot-diversity note:** both rungs' committed shots demonstrate
distinct counts (hamming8: 4/1; hamming12: 3/5), so the still-open
battery-wide shot-diversity ruling question is satisfied de facto
here; the forward rule remains open for waves 2–3.

**Next:** tier-1 verdicts (screens running: hamming8 then hamming12);
then wave 2 per §6 (order_stat, seq_extrap, odd6 — odd6 gated on
Michael's CATEGORIES_2C hand review).

## 2026-08-02: Wordlists HAND-REVIEWED and APPROVED (ruling 3 gate closed) — 4 category swaps applied

**Michael's hand review of the growth wordlists returned.** Structural
checks clean (independently confirming test_wordlists_2c.py's gates);
four ambiguity classes flagged, each verified against HEAD and
adjudicated:

1. **Borderline proper nouns in WORDS_7_8** (nirvana, griffin,
   heather, mustang, buffalo; + boulder, same class): ACCEPTED as-is.
   The caesar pool's items are committed with tier-1+tier-2 fits done;
   the probe label (first letter of the decoded word) is
   semantics-free; the six words appear in only 16 of 2,500 committed
   items. A swap would invalidate 10 campaign fits for zero
   measurement gain.
2. **WORDS_7_8 ∩ ANTONYMS_2C tokens = 35** (list enumerated in the
   review exchange, reproduced exactly against HEAD): ACCEPTED as-is.
   Cross-family (rotation ↔ antonym) with no plausible coupling
   mechanism — rotation margins are semantics-free; ~2.3% of caesar
   items surface any overlap word. Dropping the ~31 affected pairs
   would sink the noun sublist below its 60 floor (65 → ~43), so
   removal is not the cheap direction; acceptance is.
3. **WORDS_7_8 ∩ CATEGORIES_2C = 4** (cricket, emerald, shoulder,
   thunder): SWAPPED on Michael's instruction — cricket→cicada,
   emerald→onyx, shoulder→hip, thunder→gale. CATEGORIES_2C had
   generated no items, so the swap is free. Verified after: overlap
   with WORDS_7_8 = ∅, overlap with ANTONYMS_2C tokens = ∅ (the
   cross-list case no test pins), all floors/bands/anti-clustering
   tests green (29 passed).
4. **Charged words in WORDS_7_8** (abortion, suicide, assault,
   asbestos, torture, violence, poverty, disease, disaster, funeral,
   tragedy — all present; 28 of 2,500 committed caesar items, 1.1%):
   ACCEPTED for measurement (subjects are Pythia checkpoints; no
   human-subject dimension; semantics cannot reach the rotation
   label). **Standing note: do not quote these items as examples in
   the paper or any human-facing material.**

Also on the record: the reviewing tool's own totals were stale (it
reported 858 WORDS_7_8 / 186 antonym tokens vs the committed
1522/260), but every substantive finding reproduced exactly against
HEAD — flagged back to Michael for his next review pass.

**Ruling 3 gate CLOSED: "Perform the category swaps and the list is
approved" (Michael, 2026-08-02).** ANTONYMS_2C (130 pairs) and
CATEGORIES_2C (10×8, post-swap) are approved including semantic
validity — odd6 and antonym6 are UNBLOCKED for waves 2–3.

## 2026-08-02: str_align tier-1 PASS x2 — B2's 35-rung shape restored; wave 1 arc CLOSED

Tier-1 verdicts: **hamming8 PASS** (not_fire x4; 410m null_mean 0.320,
1b 0.240-0.321; no fit at floor, margins 0.000) and **hamming12 PASS**
(not_fire x4; null_mean 0.249-0.251). The elevated null means are the
truncated-Binomial majority-class baselines (modal class ~0.31 of items
at L=8, ~0.26 at L=12) — the permutation null absorbs the ruled label
imbalance exactly as intended; nothing fired above it.

**The session's own fire→silence contrast, on the record:** within one
build wave, the variable-index gather (pos_letter: position computable
from printed integers, letter fetched at that data-dependent slot)
fired structural_abort in ALL EIGHT fits, while the fixed-position
alignment reduction (str_align: same 4-letter random-string surface
family, but every comparison slot static and the label a
whole-sequence count) sat at not_fire in all eight. Untrained random
projections express the surface-computable-index gather but not the
position-wise count composition — the sharpest single datum yet for
the methods paper's positional-gather leak class, produced by the
screen sequence the proposal preregistered (riskiest first, reserve
promoted on ejection).

**Battery state:** the B2 shape stands restored at 35 rungs — 16
families with str_align the third new 2-rung family (screened), and
order_stat + seq_extrap pending build in wave 2 alongside odd6;
antonym6/base13 in wave 3. Wordlists approved (ruling 3 closed above),
so odd6/antonym6 are unblocked. Certification remains the full
5000-sim exact/sampled table on the BUILT battery post-screen, per the
growth ruling.

**Next:** wave 2 — order_stat (median5 20260820, median7 20260821;
odd_one_out-style blessed override expected), seq_extrap (arith_next
20260822 with the pre-flagged reduced-n_probe blessing, quad_next
20260823), odd6 (20260819, CATEGORIES_2C, override expected). Open
ruling question carried: the battery-wide shot-diversity forward rule
(both hamming rungs satisfy it by luck: shots 4/1 and 3/5).

## 2026-08-02: Consolidated feasibility sweep for waves 2–3 (the pre-queued blessing pass) — data ledgered, ruling requested

The growth design queued "a consolidated feasibility-blessing pass at
item generation alongside odd6/order_stat/antonym6's expected
overrides." Run synthetically against the frozen splits module before
any wave-2 spec registers (the F4 lesson applied proactively). Full
grid and n_train sides:

| rung | basis tested | params | verdict | n_val | n_train |
|---|---|---|---|---|---|
| median5 | 5-comp shared | 0.45/8000 (odd_one_out figs) | INFEASIBLE | — | — |
| median5 | 5-comp shared | 0.52/8000 | feasible | 305–332 | **223** (7458 dropped) |
| median5 | 5-comp shared | 0.55/8000 | feasible | 390–420 | **158** |
| median5 | first-number 1-comp | default/2000 | feasible | 378–407 | 1593 |
| median7 | 7-comp shared | 0.55–0.65/8000 | INFEASIBLE (all) | — | — |
| median7 | first-number 1-comp | default/2000 | feasible | 392–441 | 1598 |
| odd6 | 6-comp shared | 0.45/8000 (proposal's expected figs) | feasible, fragile (attempt 40 seed 0) | 311–335 | **342** (7326 dropped) |
| odd6 | 6-comp shared | 0.55–0.60/8000 | feasible | 327–661 | 116 / **29** |
| odd6 | odd-word 1-comp | default/2000 | feasible (16 held vs 15 floor) | 379–411 | 1589 |
| odd6 | odd-word 1-comp | 0.30/2000 | feasible | 575–635 | 1365 |
| arith_next | a 1-comp | 0.35/1000 (sub_base8 figs) | feasible | 344–368 | 652 |
| arith_next | a 1-comp | 0.30/1200 | feasible | 344–365 | 849 |
| quad_next | a 1-comp | default/2000 | feasible | 378–411 | 1622 |
| antonym6 | cue 1-comp | default/2000 | feasible | 380–408 | 1620 |

**The structural finding:** the multi-component AND-holdout collapses
BOTH split sides as component count grows (train = (1-h)^k, val =
h^k). 2b's own precedents sit at the edge (sort3_mid 3-comp 0.37 →
train 25%; odd_one_out 4-comp 0.45 → train 9%); at k=5 the train side
is 2–3% of items, at k=6–7 it is nothing. The proposal's expected
overrides for order_stat (odd_one_out figures) are unbuildable at k=5
without a 223-item train side and outright infeasible at k=7.

**Recommendations carried to Michael (one consolidated ruling):**
1. **order_stat — first-printed-number basis for BOTH rungs**, default
   SplitParams, n_probe 2000: the mod17-lesson reduction the growth
   ruling already adopted for seq_extrap ("the joint-AND trap of a
   multi-component basis is avoided"), applied uniformly so the
   family's two rungs starve identically. Deviates from the proposal's
   stated shared-components basis — hence the ruling.
2. **odd6 — 6-comp shared at 0.45/8000** (the proposal's own expected
   figures, which DO clear): precedent-faithful to 2b's odd_one_out
   family treatment; accepted costs flagged: train side 342 (2b's own
   was 732), attempt-40 fragility on one seed.
3. **arith_next — 0.35/1000** (exact sub_base8 precedent, the
   pre-flagged certain blessing; 1500 of 1710 generator space used).
4. quad_next, antonym6: defaults, no blessing needed (ledgered for
   completeness). base13: direct base12 precedent, default.

## 2026-08-02: Wave 2 BUILT — five rungs registered + items committed under the approved blessing

median5 (20260820), median7 (20260821), arith_next (20260822),
quad_next (20260823), odd6 (20260819) registered per the accepted
proposal §3 + the approved consolidated blessing: medians on the
first-printed-number basis (default/2000), arith_next at the sub_base8
figures (0.35/1000; 1,500 of its 1,710-run space), quad_next
default/2000, odd6 on all six words at the 2b odd_one_out family
figures (0.45/8000). Every spec text carries its carrier analysis at
full strength (2t3−t2 and 3t3−3t2+t1 identities for seq_extrap;
translation-invariance for the medians; the §2(c) vocab-hygiene
provenance for odd6) and its blessing citation.

**TDD:** RED 18 failures against pre-implementation modules → GREEN.
9 new generator tests (registration/dial/seed pins, hand-worked oracle
vectors for all five, gen-shape sweeps incl. shuffle-position coverage
and the 2q>=2 non-degeneracy check, determinism) + 6 gen_items tests
(per-rung question-text recomputation incl. the first-number/all-six
basis pins, split-plan pins) + TRUE_ANSWER x5. **Generation:** all five
clean, zero ejections — min val across seeds: median5 385, median7
377, arith_next 348, quad_next 388, odd6 305 (the flagged fragility
real but clear of the 300 floor, 5/5 seeds). Shots spot-checked by
hand recomputation, all correct; shot diversity satisfied de facto on
all five (distinct labels within each pair).

**family_map pin updated** (test_family_map): the 2026-08-01 26/13 pin
was superseded by str_align's two tier-1 passes — now 28 rungs / 14
families with the growth trajectory noted (B2 target 35/16); the pin
stays exact and screen-aware (letter_sum/letter_prod/base12 excluded
by verdict). Full suite **105 passed**.

**Paper decision (Michael, 2026-08-02), cross-referenced here since the
screening arc is now its clock:** the methods paper is HELD for the 2c
screening results — the 2c arc's by-construction confirmations
(base12→base12_digitsum; pos_letter→str_align) and the
screen-admits-a-battery record discharge two of the paper's §7
limitations; a confirmations section lands once waves 2–3 + tier-2 +
recertification close.

**Next:** adversarial review + tier-1 screens (risk order: arith_next,
quad_next, median5, median7, odd6), then wave 3 (base13, antonym6).

## 2026-08-02: Wave-2 review adjudicated — data clean x17,500; four record defects, three fixed, one to ruling (odd6 split)

**Adversarial review (subagent, claims independently verified):** every
committed wave-2 item + shot recomputed clean from question text; all
five files byte-reproduce from their seeds; generator boxes enumerated;
suite figure confirmed. **The data is correct; the defects are in the
record.** Adjudication:

1. **F1 (fixed): quad_next's "exactly uniform, verified by
   enumeration" was false as stated.** 15,390 = 7×2198 + 4, so exact
   uniformity is impossible; the enumeration's true output is counts
   2198/2199 (±1). Independently re-enumerated before fixing. Spec
   text corrected, proposal §3 F2b annotated in place, quad_next.json
   regenerated (diff = exactly the one corrected string; items
   byte-identical). The lesson ledgered plainly: the proposal misread
   its own enumeration output, and two review passes (growth
   finalization, wave-1) carried it.
2. **F2 (RULING REQUESTED, odd6 tier-1 held): the blessed 6-comp split
   achieves feasibility only degenerately.** Frozen-split reruns on
   the committed bases show every seed clears the floors only when the
   45% holdout swallows one complete 8-word category; starved val is
   then 88–100% that single category (weather, insects, insects,
   weather, metals — seeds 1/2 correlated on the same category), and
   the real costs exceed the blessed disclosure: attempts 40/37/8/
   139/4 (vs "one seed at 40"), n_train 350/203/255/129/345 (vs
   "~342"; 2b's own was ~732). The starved val is effectively
   leave-one-category-out, which changes what the rung's margin
   means and confounds the n_words dial comparison. Options to
   Michael, recommendation first: (a) **re-bless the basis to the
   odd word alone (1-comp) at holdout 0.30** — swept clean
   (no degeneracy, val ≈ 30% of items, train ≈ 70%), committed items
   and prompts UNCHANGED (only the basis field regenerates), the
   asterisk on the dial comparison honestly smaller than the
   degenerate-split asterisk; (b) keep the blessed split with the
   degeneracy disclosed as the price of family-symmetric treatment;
   (c) something else. odd6 is last in the tier-1 queue (~2h out);
   its screen will not run until this is ruled.
3. **F3 (corrected here): the build entry's "shot diversity satisfied
   de facto on all five" was FALSE for odd6** — both shots put the odd
   word at printed slot 5 (labels 5/5; the answers differ, but the
   metric this ledger itself established for str_align is labels).
   The other four rungs' pairs are genuinely distinct (5/1, 5/1, 5/1,
   6/5). odd6 joins the letter_sum precedent as a live instance of
   the open battery-wide shot-diversity ruling question; per that
   precedent, tier-1 is unaffected (constant prefix) and any shot
   remedy must land before tier-2.
4. **F4 (closed here): the consolidated blessing's approval event.**
   For the provenance chain the sweep entry left implicit: **Ruling
   (Michael, 2026-08-02): "approved" — the sweep entry's four
   recommendations adopted verbatim**, authorizing the order_stat
   basis deviation (shared components → first printed number), the
   arith_next reduced pool, and the odd6 figures (now superseded in
   part by F2's ruling request above).

Minors: M1 fixed — new test pins every CATEGORIES_2C category at
EXACTLY 8 members (the committed generator's rng.integers(8)
dependency; a 7-member category would IndexError, a 9-member one would
silently shrink the odd-word space). M4 hardened — TRUE_ANSWER's
seq_extrap entries now recompute by the difference chain (infer d, q
from printed terms), independent of the oracle's linear functionals.
M2 noted, no change: odd6's basis is committed in printed order vs
2b's sorted-tuple precedent — behaviorally nil under shared_components
(conjunction over one shared holdout set, order-invariant; confirmed
by exact split reproduction), disclosed here. M3 noted, no change:
median7's committed label distribution is the one non-flat draw of
the five (chi^2 p = 0.0095); the mechanism is provably slot-uniform
and one p≈0.01 in five is unremarkable — on the record for the
freeze reader.

Full suite after fixes: **106 passed**.

## 2026-08-02: Wave 3 BUILT — base13 + antonym6 registered + items committed (defaults per blessing table)

base13 (20260817): N mod 13 label, N-token basis, default split —
the base12_digitsum pattern at a prime modulus (no CRT decomposition
possible; the one named carrier is base7's own cleared 3-digit-block
alternating rule, 10^3 ≡ −1 mod 13, pinned by identity test).
antonym6 (20260818): position label at k=6 (ruled), cue-word basis
(130 cues, no override — the sweep's 380–408 val), distractors from
the cue's own POS sublist per the approved wordlist convention, 2b
_gen_antonym exclusions carried. TDD: RED 12 → GREEN; hand-worked
oracle vectors both rungs (incl. base13 letter-digit path BB/CC and
the block-rule identity pin); generation clean (min val 400/388,
zero ejections); shots hand-recomputed correct. Full suite **115
passed**.

**Self-caught flag, ledgered before review: antonym6's two shots both
demonstrate slot 4** (outgoing at 4; placid at 4) — the THIRD
shot-label collision in the growth build by seed luck (letter_sum 2/2
dead with its rung; odd6 5/5, wave-2 review F3; now antonym6 4/4).
base13's shots are distinct (labels 6/11). Three collisions in nine
growth rungs is the empirical case for the still-open battery-wide
shot-diversity ruling; per the standing precedent, tier-1 is
unaffected (constant prefix) and any remedy must land before tier-2's
campaign fits.

**Next:** wave-3 adversarial review; tier-1 screens queue behind
wave-2's four (odd6's screen stays HELD on the F2 basis ruling).

## 2026-08-02: Two rulings executed (odd6 re-bless + shot-diversity rule); wave-3 review adjudicated

**Ruling (Michael, 2026-08-02): "Re-bless odd6 to the odd-word basis,
and adopt the shot-diversity rule."** Both executed TDD (RED on the
three behavior pins -> GREEN):

1. **odd6 re-blessed:** basis = the odd word alone (1-comp, 80 values),
   SplitParams(holdout_frac=0.30), n_probe unchanged 8000. Regenerated:
   min n_val across seeds **2336** (vs 305 under the degenerate 6-comp
   plan) with no whole-category swallowing and no seed correlation --
   the F2 finding closed. Spec basis_kind text carries the supersession
   and its reason. HOLD LIFTED: odd6 screens with wave 3.
2. **Shot-diversity rule (battery-wide forward):** generate() now
   requires the two shots to demonstrate DISTINCT probe labels,
   redrawing from the same seeded stream (rejected same-label draws
   are not marked seen; 1000-attempt guard). Proven a byte-identical
   no-op for compliant rungs: hamming8 regenerated under the rule ->
   empty diff. The two live non-compliant rungs regenerated: odd6
   (new shots + full re-draw under its new basis) and antonym6 (new
   shots 4/6; the item stream is a one-slot rotation -- git diff 40
   lines, nearly all committed items unchanged). Neither rung had
   been screened or collected; nothing invalidated.

**Wave-3 review adjudicated (no Critical; both files verified 100%
correct + byte-reproducible by the reviewer before these changes):**

- **I1 (disclosed dose, ledgered pre-screen per the base12 lesson):**
  antonym6's answer sits in the pair's SECOND slot while distractors
  draw from both slots, and the ADJ sublist is slot-asymmetric (cue
  slot mean 5.892 vs answer slot 6.431 letters; NOUN side balanced).
  Draw-level heuristic accuracies vs 1/6 chance, measured on the
  CURRENT (regenerated) committed items: argmin-Levenshtein-to-cue
  0.2016, argmax-length 0.1972, max-shared-letters 0.1976
  (reviewer's figures on the superseded draw: 0.2046/0.1946/0.1905 --
  the dose is a wordlist-level property, stable across draws). At the
  pair level (n=130) the effect is n.s. (t=+1.58), but the committed
  battery is a fixed object and these are its true doses. The
  preregistered adjudicator is the untrained screen, which now runs
  against a named carrier, not a discovered-later one.
- **I2 (disclosed, remedy deferred to Michael before M4, NOT
  screen-blocking):** ~2.5% of items (floor; 14/500 eval on the
  superseded draw) carry a distractor that is a defensible
  alternative antonym of the cue (glum->merry with jolly present;
  order->chaos with discord). The probe label is unaffected (position
  of the LISTED partner is well-defined); the cost is an M4 eval
  ceiling depressor of <= ~3% on this rung. Options when M4 nears:
  per-cue exclusion sets (a wordlist-adjacent artifact needing hand
  review) or accept the disclosed ceiling. 2b's antonym had the same
  structural exposure at k=4; k=6 within-POS raises the dose.
- **M1 (count corrected):** under the ledger's own label metric the
  growth build had TWO shot-label collisions (odd6 5/5, antonym6 4/4);
  letter_sum's 2/2 was a POSITION collision with distinct letter
  labels ('w'/'b') -- the wave-3 entry's "third instance" framing was
  loose. All three flags stand as flags; the rule now closes the
  class.
- **M2 (closed):** standing committed-file LABEL sweep added --
  TRUE_LABEL recomputes the probe label from question text for all 26
  registered specs and test_committed_labels_are_true_labels sweeps
  EVERY item (probe + eval) of every committed file. Passed on first
  run against the whole battery.
- **M3 (closed):** _true_antonym6 now asserts exactly one listed
  option pairs with the cue under order-free frozenset membership --
  independent of the oracle's direction dict.
- **M4 (noted, no change):** base13 answer_type="number" with A/B/C
  in 1331/2500 answers -- inherited verbatim from base12's committed
  precedent; consistency wins.

Full suite **118 passed** (115 + shot-rule test + TRUE_LABEL coverage
+ committed-label sweep). Screens: wave-2's four still running; odd6 +
base13 + antonym6 launch when they finish.

## 2026-08-02: Wave-2 tier-1 — FOUR PASSES (arith_next, quad_next, median5, median7); tier-2 fleet STAGED

**Verdicts:** arith_next PASS (not_fire x4), quad_next PASS (not_fire
x4), median7 PASS (not_fire x4), median5 PASS with 2 tolerated fits
(at floor, z inside the tolerated band — the calibrated allowance, not
a fire). The seq_extrap result is the notable one: both rungs carry
disclosed ON-SURFACE mod-7 functionals (label ≡ 2t3−t2 and 3t3−3t2+t1
mod 7), and neither leaked — base7's full-digit mod-7 composition
stays unexpressed by random projections even at three-fold token
composition. The order_stat first-number reduction also held.

**Tier-2 fleet staged (Michael's instruction), dispatch pending the
last three tier-1 verdicts (odd6/base13/antonym6 screening now):**
- `run/tier2_worker.sh` committed (per-box venv resolution, npz
  presence guard, hostname+UTC stamps for provenance).
- `run/tier2_fleet_plan.md` committed: cost model (n_probe × k units),
  box assignments — llmbox takes the heavy four (odd6 48u, hamming12
  32u, base13 26u, hamming8 24u; one worker each), Mac takes the
  light five (57u across quad_next/median7/antonym6/median5/
  arith_next) — dispatch checklist, bundle-sync and npz-return
  procedures, and the standing constraints (activations Mac-only;
  odd6/antonym6 npz must postdate the regeneration; hamming8's cache
  proven valid).
- llmbox verified live and pinned (load 0.32, 26 GB avail, venv
  2.4.6/1.17.1/1.9.0); clone refresh to current HEAD via git bundle
  follows this commit; hamming npz pairs (1.8 GB) ship at staging.

## 2026-08-02: GROWTH TIER-1 COMPLETE — 9/9 surviving rungs PASS; battery at the ruled B2 shape (35/16)

**Final three verdicts:** odd6 PASS (not_fire x4 on the re-blessed
odd-word basis — the F2 remedy validated end to end), base13 PASS
(not_fire x4; the prime-modulus argument held as base7's precedent
predicted), antonym6 PASS (not_fire x4, corrected p = 1.0 in every
fit — the ledgered ~0.20 draw-level heuristic dose did not express
through random projections).

**Provenance note:** the first launch of these three screens was
KILLED externally mid-run (2026-08-02 afternoon; not by this session
— Michael confirmed not him either; his remote session killed as the
suspected cause). No committed artifact was touched: zero verdicts
existed, the repo was clean, and odd6's two cached activation files
were integrity-validated (shape, finiteness, metadata item counts)
before the resume reused them. The resume re-ran odd6's fits from the
validated cache and collected base13/antonym6 fresh.

**Growth tier-1 tally, complete:** letter_sum/letter_prod REJECTED
(pos_letter family ejection, 2026-08-02) — every other growth rung
PASSED: hamming8, hamming12 (str_align, the promoted reserve),
arith_next, quad_next (seq_extrap), median5, median7 (order_stat),
odd6, base13, antonym6. **The scored battery stands at exactly the
ruled B2 shape: 35 rungs, 16 families, [4,4,4, 2x10, 1,1,1]** —
base_repr at 4 (base7, oct2dec, base12_digitsum, base13), ten 2-rung
families, the three rescues singleton by ruling. family_map pin
updated 28/14 -> 35/16; full suite **118 passed**.

**Fleet state at this entry:** llmbox holds Mac HEAD + verified
hamming npz pairs; odd6/base13 npz pairs ship next (its remaining
assigned candidates). Launch set per run/tier2_fleet_plan.md = all
nine passers. Dispatch on Michael's word; then binomial fire-count
bookkeeping, and the 5000-sim recertification against the 0.75 power
gate on the BUILT battery — the certification the growth ruling
requires and the last item before the freeze path (analyze.py exact
amendment, Task 13/14) and the methods paper's screening-arc section.

## 2026-08-02: Mac tier-2 workers relaunched DETACHED (controlled, pre-harness-restart)

Michael needed to restart the Claude Code harness (~12 versions
behind). The Mac fleet's five workers had been dispatched as a
harness background task: the wait-group shell was a child of the
harness process and still tethered to the pre-/clear session's task
tracker (proven at kill time — the old tracker reported the task
failed with exit 144 when the group was terminated). A harness
restart would therefore likely have killed the fleet mid-run, a
repeat of the tier-1 external-kill incident.

Controlled relaunch, 13 minutes after dispatch: process group
TERMed at 23:54 UTC with ZERO fits landed (fits take ~100 min; the
known_absent and screen/tier2 dirs were verified at the prior
campaign's baseline, 140 fits / 14 verdicts, before and after).
Relaunched all five candidates via nohup, wrappers now parented to
launchd (PPID 1) — same worker script, same venv, same per-candidate
log paths (append), new start stamps 2026-08-02T23:5xZ. Same seeds,
same frozen config: results are deterministic and identical to what
the first launch would have produced. Cost: ~13 min recompute on the
light candidates, absorbed entirely by llmbox's odd6 critical path
(48u); fleet completion unchanged. llmbox untouched (its four
workers were nohup-detached from dispatch). No committed artifact
touched.

## 2026-08-03: Mac tier-2 COMPLETE — five PASS; llmbox relaunched thread-pinned (BLAS oversubscription, zero artifacts lost)

**Mac verdicts (done stamps 07:36–12:22 UTC):** arith_next, antonym6,
quad_next, median7 all PASS not_fire x10; median5 PASS with 8
not_fire + 2 tolerated — both at seed 1 (410m and 1b), the calibrated
allowance again, echoing its tier-1 shape. All 50 known_absent fit
files validated (parse + stage/size/capability/host consistent with
filenames, host Michaels-Mini); committed with this entry. Battery
Mac assignment closed: +50 fits, +5 verdicts, exactly the staged
expectation.

**Housekeeping:** a stray codeassist-mcp server log directory
appeared inside results/probes/known_absent/ this morning (the MCP
server inherited a stale shell cwd after the harness restart and
dropped its own startup log there). Relocated out of the results
tree; no campaign artifact touched.

**llmbox diagnosis:** at 14h22m elapsed the four llmbox workers had
written ZERO fits; load average 64 on the 12-thread box; NLWP 23 per
worker. Cause: scipy-openblas defaults each process to a 12-thread
spin-wait pool — 4 workers ≈ 48 BLAS threads fighting 12 hardware
threads. Throughput was pathological vs the Mac's ~66–70 min/unit
pace (base13 at 2.6u/fit should have landed ~4 fits in that window;
it landed none).

**Remedy (no artifacts existed, so nothing lost):** all four workers
killed and relaunched 14:06 UTC with OPENBLAS/OMP/MKL_NUM_THREADS=3
— 4 x 3 = the box's 12 hardware threads exactly; NLWP now 5/worker.
Threading env pins sit outside the frozen statistical config; seeds
deterministic; reduction-order/final-ulp variation already covered
by the standing cross-architecture caveat; per-fit host provenance
unchanged. Health signal: first base13/hamming8 fits within a few
hours. Ops gotcha for the record: the first kill attempt used
pkill -f 'run.screen', which matched the SSH shell's own command
line and severed the session before reaching the workers; completed
by explicit PID.

## 2026-08-03: Fleet REBALANCED — odd6 + hamming12 moved to the idle Mac (Michael's ruling)

Michael flagged what the plan's "12 threads" framing hid: llmbox's
i7-1265U has only 2 P-cores (plus 8 E-cores). Even thread-pinned,
its per-unit throughput projects 2-4x below the Mac's ~66-70
min/unit, putting odd6 (48u) at 4-9 days — while the Mac sat idle
after finishing its five. Ruling executed 14:20 UTC:

- llmbox's odd6 + hamming12 workers killed by explicit PID with
  known_absent still at the 140-fit baseline — zero llmbox fits ever
  landed, so nothing was lost and no cross-box duplication is
  possible (each candidate runs on exactly one box).
- odd6 + hamming12 launched detached on the Mac at 14:20:51Z from
  the Mac-local npz (odd6's pair postdates the re-bless regeneration
  and was integrity-validated at tier-1).
- llmbox keeps base13 + hamming8 at the 3-thread pins, deliberately
  not raised: OpenBLAS's even GEMM chunking means added E-core
  threads gate the fast cores; the freed 6 threads already migrate
  the remaining workers onto the best cores (load fell 64 -> 19).
- Assignment amendment recorded in run/tier2_fleet_plan.md.

Revised fleet close: ~2-3 days; Mac's odd6 is the long pole. Harvest
procedure unchanged: llmbox returns base13/hamming8 verdicts + fits
by scp; binomial fire-count over all 90 fits, then the 5000-sim
recertification.

## 2026-08-04: Let-it-ride ruling; hamming12 PASS on the record

hamming12 tier-2 verdict landed 00:47 UTC: PASS, not_fire x10 —
seventh of nine candidates closed, all PASS so far. Michael ruled
"let it ride like it is" on the flagged option to migrate base13 to
the Mac once odd6 completes: base13 finishes on llmbox (~Aug 6
morning UTC, fleet long pole; k=13 multinomial cost runs ~1.6x the
n_probe x k unit model — noted for future cost planning). Remaining:
odd6 (Mac, ~Aug 4 evening), hamming8 (llmbox, ~Aug 5 morning),
base13 (llmbox). Harvest after the last verdict.

## 2026-08-04: odd6 tier-2 PASS — Mac assignment fully closed (7 of 9 all-PASS)

odd6 verdict landed 21:49 UTC: PASS, not_fire x10 on the re-blessed
odd-word basis — the F2 remedy now validated at full config, closing
the Mac's amended assignment (7 candidates, 70 fits, all PASS; only
median5's two seed-1 tolerated fits across the whole Mac set). odd6's
10 fits + verdict and hamming12's 10 fits + verdict validated
(stage/size/capability/host all consistent, host Michaels-Mini) and
committed with this entry. Remaining: hamming8 (llmbox, 7/10 fits,
~4h pace, verdict ~Aug 5 morning) and base13 (llmbox, 4/10, ~6.7h
pace, verdict ~Aug 6 morning) — then harvest, binomial fire-count
over all 90 fits, 5000-sim recertification.

## 2026-08-05: hamming8 tier-2 PASS harvested — 8 of 9 closed, all PASS

hamming8 verdict landed on llmbox 15:06 UTC: PASS, not_fire x10.
Its 10 fits + verdict scp'd back, validated (stage/size/capability
consistent, host llmbox — first cross-box artifacts of the campaign),
committed with this entry. base13 alone remains: 7/10 fits, three 1b
fits to go at the ~7h 1b pace — verdict projected ~Aug 6 evening
UTC. Then: final harvest, binomial fire-count over all 90 growth
fits, 5000-sim recertification.

## 2026-08-06: TIER-2 FLEET COMPLETE — 9/9 PASS, 90/90 fits; binomial fire-count clean

base13's verdict landed 13:51 UTC (PASS, not_fire x10; the k=13
1b fits ran ~7h each, closing the fleet 3.7 days after dispatch).
Harvested by scp, validated (host llmbox), committed with this
entry. Full growth-campaign accounting: every one of the nine
candidates has exactly 10 fits + a pass verdict — 90/90 fits, the
only non-not_fire cells the entire campaign are median5's two
tolerated fits (seed 1, both sizes), both z inside the central-99%
tolerance band; zero elevated, zero structural aborts.

**Binomial fire-count (design §4 gate-1 bookkeeping, same test as
the 2026-08-01 entry):** growth batch k=2 fires in n=90 fits vs
p=0.0064/fit, expected 0.576, binomtest two-sided p=0.1136; full
campaign (140 original + 90 growth = 230 untrained-gate fits) k=2
in n=230, expected 1.472, p=0.6617. Unremarkable in both scopes —
the untrained gate closes clean on the grown battery.

**Growth screening arc CLOSED.** The scored battery stands at the
ruled B2 shape: 35 rungs / 16 families, every rung through the
two-tier untrained screen with zero rejections at tier-2 (the two
tier-1 rejections, letter_sum/letter_prod, never reached tier-2).
Next: 5000-sim MC recertification of the built 35-rung battery
against the 0.75 power gate — the certification the growth ruling
requires and the last item before the freeze path.

## 2026-08-06: RECERTIFICATION PASSED — built 35-rung battery clears the 0.75 power gate (0.7728)

`python -m run.power_table --exact` on the BUILT battery (the
certification the growth ruling requires), transcribed from
`results/power_table_exact.md`: family sizes resolve to the ruled B2
multiset [4,4,4, 2x10, 1,1,1] (35 rungs / 16 families); sampled
block permutations n_perms=100,000 (group ~131M > 5e6 enumeration
guard), resolution 1.0e-5, n_sims=5000, seed 0.

**Gate cell: power 0.7728 at rho_true=0.6, rho_family=0.5 — >= 0.75,
the gate PASSES** (B2 projection was 0.777; agreement within MC
noise). Full rho_true sweep 0.0/0.5/0.6/0.7/0.8 =
0.0110/0.5588/0.7728/0.9276/0.9902; alpha 0.0088-0.0098 everywhere,
inside the exact test's <= .01 construction.

**Disclosed for the freeze reader:** unlike the 26-rung table's flat
sweep, the robustness sweep now tilts with the nuisance parameter —
power at rho_true=0.6 is 0.7976/0.7728/0.7414 across rho_family
0.3/0.5/0.7. The adverse corner (rho_family=0.7) sits at 0.7414,
just under the gate value; the preregistered gate is the main-table
cell at the default rho_family=0.5 (the same cell the 26-rung
battery failed at 0.416), and alpha stays bounded everywhere. On
the record verbatim; whether the corner warrants any response is
Michael's read at freeze review.

Old 26-rung power_table_exact.{json,md} superseded in place (the
failure table remains in git history at the 2026-08-01 entry).

**The growth arc is fully closed: build -> two-tier screens (9/9
PASS) -> binomial bookkeeping (clean) -> recertification (0.7728 >=
0.75).** Remaining before the freeze tag per the pre-authorization:
analyze.py exact-test amendment + fixture suite, then Task 13/14.

## 2026-08-06: analyze.py exact-test amendment LANDED (queued 2026-08-01, pre-freeze)

Executed TDD (RED 15 -> GREEN; the 5 new exact-path fixtures plus the
10 existing rewritten off the removed constructor arg). The PASS
branch now adjudicates with `run.power_table.exact_block_p` at fixed
ALPHA_EXACT = .01 — the design §5 fallback the 2026-08-01 ruling
adopted — replacing the calibrated-naive permutation test;
`AnalyzeInputs.calibrated_cutoff` is gone (no rho_family-dependent
input remains). Guard routing is inherited from the certified
machinery: enumerated below the 5e6 group-size guard, sampled at
100,000 seeded draws above it — the fixture suite pins both routes
([3]*9 -> enumerated 362,880; [2]*11 -> sampled 100,000, the same
path the built 35-rung battery (~131M) will take at adjudication).

**Contiguity contract (ledgered 2026-08-01, "don't pick silently"):**
implemented as first-appearance family grouping over the SCORED list
— the sizes vector and array layout are built from the same pass, so
block i of `families` is family i's rungs by construction, for any
input order. Pinned by a fixture comparing interleaved vs contiguous
input (identical block_p) and both against a hand-grouped direct
`exact_block_p` call.

**Output record:** `naive_p` replaced by `block_p` + `n_perms` +
`resolution` + `method` (the design's "achievable permutation count
and resolution stated" clause, now in the verdict record itself).

**Disclosed:** removing the naive-perm loop shifts the seeded rng
stream feeding the family-cluster bootstrap (its draws now come
first). No adjudication has ever run on real data (no eval-side
model has been queried), so nothing is invalidated; the FAIL-branch
fixture is structurally robust to the shift. Full suite **123
passed**, and faster — the 100k-call spearmanr loop is gone.

## 2026-08-06: M1 inclusion harness BUILT + ctrl_copy control committed (Task 13 opens)

Michael's go: "Start M1." Built in this order, TDD throughout, suite
**129 passed**:

- **ctrl_copy control (gate 4):** `battery/generators_controls.py` —
  2b's `_gen_ctrl_copy`/`_oracle_ctrl_copy` ported verbatim to 2c's
  gen(rng) convention; spec fills 2c's mandatory fields; scored=False;
  **seed 20260827** (next unused in the growth sequence, this line is
  the ledger entry for that choice). Items committed: 500 eval / 2000
  probe, min val 397 across seeds (letter_sum split plan verbatim, a
  feasibility formality — control items are never probe-fitted).
  Registration proven shape-neutral: no tier-1 verdict + scored=False
  keeps it out of scored_battery_families (pinned by test at 35).
- **harness.py:** exp2b's argmax harness ported; render_prompt/
  normalize_answer/verify carried with BEHAVIORAL identity pinned
  against exp2b's module by test (the §7 comparability requirement);
  answer_type resolved from the SPECS registry (2c item files don't
  carry it); MAX_NEW_TOKENS covers the M1 set (number/word only).
- **run/run_inclusion.py + run/campaign_m1.sh:** 2b's resumable
  per-(size,mode,cap) pattern; model loading through exp2b's pinned
  models.py via the instrument shim (same SHAs, no second loader);
  MPS-conflict guard. **M1 scope = 23 new-pool rungs + ctrl_copy**;
  the 12 reused survivors' M1 record CARRIES from 2b per §7 ("none
  recomputed") — that carry is a named freeze-checklist line for
  Michael's adjudication, since §7's enumerated list does not name M1
  explicitly.

## 2026-08-06: M1 COMPLETE — gate 4 PASS (ctrl_copy .960/.980); absence table transcribed; ONE bar question to Michael

Campaign ran 11:17-11:36 EDT (~19 min, matching 2b's pace), 96 cells
(24 caps x 410m/1b x trained/untrained), zero failures after one
import-order abort (fixed 57df585, no cells lost — skip-if-done).
All results committed under results/inclusion/.

**Gate 4 (adjudicated now, per the pre-freeze standing rule): PASS.**
ctrl_copy trained argmax 0.9600 (410m) / 0.9800 (1b), both >= 0.9,
on 2c's own items (seed 20260827). Untrained 0.0000 at both sizes.
The measurement machinery is reliable at both probe sizes.

**Untrained floors:** 0.0000 in 47 of 48 untrained cells (CP95 upper
0.0074); median7/1b at 0.0020. Empirical chance for a random-init
model is textual garbage, as in 2b — normalized margin therefore
equals trained accuracy almost everywhere.

**Absence readings (1b trained acc, CP95 UB in parens), the 2b
inclusion rule as reference — CP-95 UB of normalized 1b margin
< 0.25 (frozen at exp2b-preregistered):** 22 of 23 new-pool rungs
sit UNDER the reference bar: eleven at literal zero (UB .0074:
add4_mid, sub4_mid, base12_digitsum, base13, caesar_len8,
rev_string7 at both sizes; and near-zero: quad_next .0080/.0204,
sub_base8 .0160/.0313, arith_next .0380/.0587, mod19 .0380/.0587,
clock24_d999 .0480/.0706, mod13_comp .0660/.0914, mod17
.0720/.0983); the visibly non-zero remainder are at or near their
option-guessing rates (median7 .1600/.1951 ~ 1/7; median5
.1860/.2229 ~ 1/5; odd6 .1440/.1779 < 1/6; antonym6 .1780/.2144 vs
1/6; collatz_step2 .1400/.1735; count_div13 .1500/.1844; isqrt_gap
.1460/.1800; roman_sum7 .1480/.1822; hamming12 .1920/.2293).

**The exception: hamming8, 1b trained .2820, CP95 UB .3237 — ABOVE
the 2b reference bar** (410m reads the same: .2800/.3216). Its
answer distribution concentrates mid-range, so modal-answer guessing
is the plausible mechanism (a dumbest-baseline artifact, not task
competence) — but 2b's rule is mechanical, no mechanism escape.

**Adjudication to Michael (battery membership + certified shape at
stake, not a controller call):** 2c's design inherits 2b's five
standing rules and says M1 is "adjudicated against its bar" without
restating a number — the natural referent is 2b's frozen UB < 0.25.
If that bar governs and hamming8 ejects: battery 35 -> 34 (str_align
drops to singleton hamming12), the certified B2 shape changes, and
the 0.75 power gate must be re-run on the 34-rung shape (projection
territory ~0.75 — borderline; a re-fail re-triggers the growth
clause). If Michael rules the bar inherited-but-adjudicated-with-
mechanism (guessing-rate artifact), hamming8 stays with the reading
disclosed. Decision and its rationale will be ledgered verbatim.

## 2026-08-06: hamming8 EJECTED (Michael's ruling: the 2b bar applies); 34-rung battery RE-CERTIFIED at 0.7690

**Ruling (Michael, 2026-08-06): "Apply the 2b bar: eject."** The M1
inclusion rule frozen at exp2b-preregistered — normalized argmax
margin at pythia-1b, CP95 upper bound < 0.25 — governs 2c's M1, and
hamming8's 0.3237 fails it mechanically. Executed TDD:

- **Adjudication record:** results/inclusion/m1_ejections.json
  carries the ejection with its arithmetic and the plausible
  mechanism (modal-answer guessing over the mid-range count
  distribution) — the same record-the-catch pattern as base12.
- **family_map is now M1-adjudication-aware:** scored_battery_families
  excludes any rung named in the committed m1_ejections record,
  exactly as a tier-1 reject. Battery pins updated 35/16 ->
  **34 rungs / 16 families, [4,4,4, 2x9, 1,1,1,1]** (str_align drops
  to singleton hamming12). Suite **129 passed**.
- **hamming8's tier-2 fits stay committed as record** (they were
  honest untrained-gate fits of a screened candidate); the frozen
  battery's gate-1 binomial restates over the 34 scored rungs' 220
  fits: k=2 (median5's tolerated pair), expected 1.408, p=0.4114 —
  clean.

**Re-certification (5000-sim exact table, sampled 100k, seed 0, on
the 34-rung shape): power 0.7690 at rho_true=0.6 — >= 0.75, the gate
HOLDS.** Full sweep 0.0076/0.5416/0.7690/0.9266/0.9894; alpha
0.0076-0.0088 everywhere. Robustness sweep 0.7800/0.7690/0.7406
across rho_family 0.3/0.5/0.7 — the same adverse-corner pattern as
the 35-rung table (0.7406 at 0.7), disclosed identically for the
freeze reader. No growth-clause re-trigger.

**M1 is CLOSED.** Remaining before the freeze tag: the freeze-review
checklist (design open item 6), then Task 14 on Michael's explicit go.

## 2026-08-06: Four freeze-review rulings executed (Michael, 2026-08-06) — checklist ALL GREEN

1. **Survivors' M1 carry: CARRY from 2b** — declared on the
   checklist; identical items/models/sizes, §7's principle.
2. **Tier-1 margin rule: DROPPED from run/screen.py** — the vacuous
   branch and `_tier1_margin_bar` removed with the ruling cited
   inline; behaviorally identical for every verdict ever produced
   (the bar was unreachable at 500 perms); suite 129 passed.
3. **Alpha-bound test looseness: ACCEPTED as-is** (minor); the
   hand-computed-p test remains the correctness net.
4. **base12 correction framing, clarifying line (append-only per the
   ruling):** in the 2026-07-30 base12_digitsum correction entry, the
   framing sentence's "caught by the screen" wording covers TWO
   distinct catches — the tier-1 untrained screen caught base12's
   CRT digit-leak (the ejection), while the human re-review caught
   the coprimality slip in the replacement's design argument. The
   entry body attributes both correctly; this line closes the
   framing conflation flagged at wave-review.

**FREEZE_CHECKLIST.md is ALL GREEN.** Every pre-freeze gate is
adjudicated with its arithmetic on the line; every queued triage item
is ruled. Task 14 — the freeze commit + tag `exp2c-preregistered`
(design doc, 34-rung battery with m1_ejections and screen verdicts,
amended analyze.py, 129-test fixture suite, 0.7690 power table, M1
record, the checklist) — awaits Michael's explicit go.
