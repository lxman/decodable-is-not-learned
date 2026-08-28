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

## 2026-08-28 — BUILD, Task 2: `analyze_2j.py` + `make_referents_2j.py`

Instrument at `experiments/exp2j/`: `analyze_2j.py`, `make_referents_2j.py`,
test `tests/test_analyze_2j.py` (12 new tests; full `experiments/exp2j`
suite 33 tests, all pass, 0 warnings, "33 passed in 6.16s"). Zero model
contact — every loader is 2i's own (`analyze_2i`/`battery_2i`), every one
of them called from inside `run()` sits behind `collect_total`, and
`run()` is exercised end to end only against an empty root (Task 4 owns
the real-tree run; the comparison gates alone run ~40s each at N_PERM
10,000).

**Label set.** 34 direct `collect_total(thunk, "literal label")`
call-sites in `analyze_2j.py` (counted by the same AST walk the test
uses); the prefix-disjointness test (`test_collect_total_labels_are_
prefix_disjoint`) passes over all 34. Nine more loader calls run inside
the `_sec(name, thunk)` helper (the six decompositions, the two
sensitivities beyond the primary one, A-1) — `name` is a variable there,
so those don't register on the AST scan, but were checked by hand for
collisions too; none found.

**Two 2i-label collisions avoided by construction.** Every 2i loader
2j calls (checkpoint manifest, predictor seal, rung set, endpoint
records, sweep, gate 1, `x_A`/`x_B` counts) is wrapped with a label
prefixed `"2i …"` rather than reusing 2i's own label text (`"checkpoint
manifest"`, `"predictor seal content"`, etc.) verbatim — 2i's own
`run()` uses those exact strings for its own referents. Reusing them
inside 2j's `referents["failures"]` list would make a 2j-side failure
indistinguishable from (and, under the prefix rule, actually collide
with a substring match against) a 2i-side one if the two lists were
ever concatenated or grepped together. The two spots this actually
would have collided, caught while transcribing the skeleton: 2i's
`"gate 1 olmo7b record"`/`"gate 1 olmo7b attestation"` pair would have
made `"2i gate 1 record"` a near-duplicate needle against `"2i gate 1
byte identity re-derived"` — kept prefix-disjoint (`"2i gate 1 record"`
vs `"2i gate 1 byte identity re-derived"`: they diverge right after
`"2i gate 1 "`), and `"functionals under x_A"` (the brief's literal
label for the tables read under `x_A` at 1b) is an exact string-prefix
of `"functionals under x_A 410m"` (the 410m sensitivity variant) — this
one is a real, not merely cosmetic, violation of the prefix rule caught
by running the test, not by inspection; renamed to `"functionals under
x_A (1b)"` / `"functionals under x_A (410m)"` (diverge at the character
after the shared `"(...)"` open-paren) per the controller's ruling.

**The `_LITERAL` sentinel for `referents_sha`.** The brief's skeleton
included a placeholder `_explicit_kwargs()` function explicitly flagged
as not allowed to survive into code. Implemented instead: a
module-level `_LITERAL = object()`; `run(..., referents_sha=_LITERAL,
...)`; the first line of the body does `if referents_sha is _LITERAL:
referents_sha = REFERENTS_2J_SHA256` (reads the module constant at
*call* time, so a test's `monkeypatch.setattr(an, "REFERENTS_2J_SHA256",
...)` is honored even though the default was bound at import time).
Then: `referents_sha is None` → refusal `"referent manifest: not pinned
(build incomplete)"`; `referents_sha is False` → the check is skipped
entirely (worlds and `test_run_on_an_empty_2i_root_is_insufficient_data`
pass this explicitly); anything else → `make_referents_2j.check_
referents` runs behind `collect_total`. `_explicit_kwargs` does not
exist in the committed file.

**Comparison-gate pins, transcribed and verified against the committed
records** (not merely copied from the brief — read back out of the
files directly before trusting the literals):
`experiments/exp2i/results/verdict.json` → `VERDICT_2I_PIN = {"B":
0.21533409065382436, "within_alone": 0.22041895894950217, "A":
0.09491251078607414, "cross_beyond_within": 0.07006211800715849,
"reverse_2.8b": 0.2612016707857866, "reverse_6.9b":
0.297364446603449}`; `experiments/exp2g/results/verdict.json` →
`VERDICT_2G_PIN = {"sampler_competitor": 0.16722141085849532}`;
`experiments/exp2h/results/verdict.json` → `VERDICT_2H_PIN = {"primary":
0.20197097010795367}`. All six + two values matched the brief's
literals to full float precision on direct read.

**`FROZEN_SHA256_2J` at this task is computed, not literal** —
`_pin_frozen_now()` hashes `FROZEN_FILES_2J` (2i's 22 pinned modules +
`analyze_2i.py` + `battery_2i.py` + `power_2j.py` + `make_referents_2j.
py`) filtered to files that exist on disk. `power_2j.py` doesn't exist
until Task 3, so the dict carries 25 entries (22 + 3), matching the
controller's ruling that `test_frozen_pins_match_disk` should assert
`+3` here, not the brief's original `+4` (edited into the committed
test with a comment explaining why). Task 4 replaces the computed dict
with a literal one once `power_2j.py` lands and re-tightens the test to
`+4`.

**`make_referents_2j.py`** is a straight transcription of the brief
(2i's referent list + 2i's now-committed stage artifacts + 2i's sweep
tree + the three verdict.json files + 2i's own two instrument modules +
2j's own power record), with `N_FILES_2J = None` left unpinned per the
controller's ruling — `check_referents` already treats a `None` pin as
a failure line, by design, so the manifest check refuses cleanly until
Task 4 pins the count.

Every produced name in the brief's Interfaces — Produces list for Task
2 is present with the signature the brief specifies (verified by
`inspect.signature` against the committed module, not just by the tests
passing): `EXP2J`, `RESULTS`, `REFERENTS_PATH_2J`, `REFERENTS_2J_SHA256`,
`PREREG_TAG_2J`, `INSTRUMENT_BLOBS_2J`, `FROZEN_SHA256_2J`, `WORLDS_2J`,
`VERDICT_2I_PIN`/`_2G_PIN`/`_2H_PIN`, `KNOWN_INPUTS_CAVEAT_2J`,
`LICENSED_2J` (five keys), `A1_READINGS`, `check_frozen_2j`,
`require_prereg_2j`, `pin_from_record_2i`/`_2g`/`_2h`, `check_pin`,
`load_pythia_outcomes`, `rederive_2i`, `rederive_2g2h`, `t_only`,
`primary_2j`, `decomposition`, `a1_density`, `verdict_tree_2j`, `run`;
`make_referents_2j.referent_files`/`build`/`check_referents`/
`N_FILES_2J`. Nothing under `experiments/exp2i`, `exp2h`, `exp2g`,
`exp2d`, `exp2c`, `exp3`, `exp3c` touched — every name 2j calls from
those modules is imported and used exactly as documented in the brief's
Consumes list, confirmed against the real source (line numbers,
signatures, and — for the pin literals and the label-source modules —
actual file contents) before writing any call site.

## 2026-08-28 — BUILD, Task 2 fix round 1

Two Important findings closed on review; the rest deferred to the
final review per the controller's instruction. Full `experiments/exp2j`
suite after both fixes: 37 tests (33 + 4 new), all pass, 0 warnings,
"37 passed in 3.09s".

**Finding 1 (2i's I-4 standard, one experiment over).** An undefined
primary — `_run_test` never calling `primary_2i` because every
eligible rung is degenerate inside the COMPOSITE strata, exactly the
construction that can leave x_B constant in every stratum — was
landing ABSORBED with the full positive licence and no disclosure; and
`ABSORBED_THIN` was read only off the power record's `declared_status`,
never off the REALIZED eligible set (a power table fixed before the
composite strata existed can say POWERED while the actual composite
partition leaves fewer than three rungs). `verdict_tree_2j` now carries
a `disclosures` list in every branch (mirroring
`analyze_2i.py:797-806`/`:820-849`); `_licensed` reads it before
falling back to `declared_status`, and joins any disclosure onto the
chosen sentence with `"; "` (`analyze_2i.py:1588-1590`'s pattern). Two
new module constants (`DISCLOSURE_UNDEFINED_2J`, `DISCLOSURE_THIN_2J`)
and one new licence key (`LICENSED_2J["ABSORBED_UNDEFINED"]`, built
through the same `_L`/`KNOWN_INPUTS_CAVEAT_2J` machinery as the rest,
so the §2 disclosure suffix is automatic). The verdict stays ABSORBED
in both cases — this is a disclosure fix, not a new world.

**Finding 2 (design §5.4, per-rung spread).** A-1's matched reading
took ONE shared `n_blocks = min(...)` across every rung thinned on a
side; the design's own k table has rungs (e.g. odd6 k=57, sub3_mid
k=40) where `64 // k == 1`, and any single such rung in the thinned
set collapsed every OTHER rung's block count to 1 too — the per-rung
spread §5.4 asks to be printed was unreachable whenever one difficult
rung shared the call. Fixed by computing each rung's block readings
independently: a new `_block_reading(r, bits_side, k, n_blocks,
size_label, out, strata)` walks one rung's own blocks through
`t_only({r: cnt}, ...)["per_rung"].get(r)` (a rung's d has no
cross-rung term, so this is bit-identical to what a joint call
restricted to that rung would give — proved for k=64 by a bit-exact
test against `t_only` on the full counts). `thinned_B_matched`,
`thinned_A_matched`, `thinned_B_zero_fraction` and every ladder cell
now carry `{"T": <mean over rungs>, "per_rung": {r: {"mean", "min",
"max", "n_blocks_used"}}}`; `n_blocks_used` is per rung (`64 // k_r` on
the thinned side, `1` on the untouched side and on the zero-fraction
sensitivity, one block at the full 64-draw count). `gap_fraction_closed`
now reads `thinned_B_matched["T"]`. Covering toy in
`test_analyze_2j.py` (`_a1_toy`, two rungs at deliberately different
synthetic densities so their `k`s differ) exercises exactly the
regression a shared block count would have shown — both rungs reporting
the SAME `n_blocks_used` instead of `64 // k_r` each.

Commit: "exp2j build: analyze_2j fix round 1 — undefined/THIN primary
disclosed in reason + licence (2i's I-4 standard), A-1 per-rung block
readings with spread (design §5.4)".
