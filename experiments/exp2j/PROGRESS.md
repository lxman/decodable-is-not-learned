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

## 2026-08-28 — BUILD, Task 3: worlds, totality, `power_2j.py`, the cold battery

Instrument at `experiments/exp2j/`: `tests/full_shape.py` (synthetic
2j worlds — a complete 2i tree, provenance-valid, with x_B draws and
the 7B outcome generated under a controlled mechanism, plus a
synthetic 2i `verdict.json` carrying the world's own re-derived pins
and a 2j `power_2j.json`), test `tests/test_full_shape_2j.py` (5
tests, "5 passed in 630.73s (0:10:30)"), `tests/test_totality_2j.py`
(18 tests, "18 passed in 204.43s (0:03:24)"), `power_2j.py` + test
`tests/test_power_2j.py` (2 tests, "2 passed in 12.69s"),
`verify_referents_2j.py` (12 items, 10/12 executed — items 3 and 12
print "pending Task 4" and are counted separately from the 10 `ok`s,
not as failures). Full `experiments/exp2j` suite: **62 passed in
848.60s (0:14:08), 0 warnings** (Tasks 1–2's 37 + this task's 25).
Zero model contact throughout — every world is synthetic bytes on a
2i-shaped tree, read by 2i's own production loaders.

**World generator, tuned (controller's note applied).** The brief's
literal draft habit-weight generator — `rng.gamma(0.5, 1.0)` over
every distinct answer, continuous — left W2 (the habit-driven ABSORBED
world) landing RESIDUAL, not ABSORBED: π's bucket rule is a single
MEDIAN split, and a continuous habit weight still varies substantially
within each half, so `beyond_all`'s T stayed at .24–.39 (T_BAR .10)
across every gamma shape tried (.5/.2/.1/.05 — grid search against a
lightweight debug harness reusing `an._run_test`/`fn.composite_strata`
directly, bypassing the ~140s full `run()` pipeline per iteration).
Swapped in a two-level (bimodal) habit weight for the non-`'residual'`
worlds instead: half the distinct answers "hot" at a fixed ratio of
the other half's weight, with small multiplicative noise so ties never
degenerate the bucket. Because π averages over ~32,000 draws per rung,
it becomes an almost noise-free readout of hot/cold membership, so its
median split matches the habit partition closely.

**Fix round 1 correction (2026-08-28): the {10, 30, 100} grid-search
numbers first recorded here were mislabeled and wrong.** They were
computed by the same lightweight debug harness as the gamma-shape
sweep above, not — as the text then claimed — "the real `write_world_2j`
pipeline". The harness iterates rungs in `RUNGS_CAP`'s own tuple
order; `write_world_2j` iterates `bt.RUNGS`'s 34-rung order restricted
to `RUNGS_CAP` membership, a DIFFERENT order (e.g. `sub4_mid` is third
in `RUNGS_CAP` but first among `RUNGS_CAP` members within `bt.RUNGS`),
so the two consume the shared `rng` in different sequences and land on
different draws at the same seed and dial — confirmed directly, not
inferred. The harness's numbers only ever motivated trying the bimodal
approach; they do not characterize the shipped code, and `hot_ratio`
100's harness figure in particular (T .09998, a hair under `T_BAR`)
does not reproduce.

Re-verified against the REAL pipeline instead —
`write_world_2j(root, world="absorbed")` + `run_world(root, seal,
n_perm=200, n_boot=20)`, seed 0 — transcribed directly from that run:

| hot_ratio | within_alone T | beyond_all (primary) T | fires? |
|---|---|---|---|
| 10 | 0.2776959534767129 | 0.06200662138616882 | no |
| 30 | 0.2920507442584531 | 0.03272027753582865 | no |
| 100 | 0.30255423071138204 | 0.03975761954629447 | no |

All three land ABSORBED with `beyond_all` comfortably under `T_BAR`
(.10); none of the debug harness's near-boundary numbers (which had
suggested 30 fires and 100 is borderline) hold against the shipped
code. **Final parameters, unchanged: `hot_ratio=10.0, hot_frac=0.5,
weight_noise=0.02`** (named `_HOT_RATIO`/`_HOT_FRAC`/`_WEIGHT_NOISE`
in `full_shape.py`, with the finding recorded inline). `'residual'`
keeps the original continuous gamma unaffected — W1 was never the
world in question (its own T stayed at .93, comfortably firing
throughout). No change to `analyze_2j.py`/`functionals_2j.py`.

**All nine worlds reach their spec'd terminal**
(`test_every_terminal_reached`, `n_perm=200, n_boot=20`):
- **W1 RESIDUAL**: primary fires (T .932, p .005); `within_alone`'s T
  equals the block-gate T64 equals `referents.comparison.2i.
  within_alone`; `decomposition x_B to olmo7b`'s `beyond_all` T equals
  the primary's T exactly (same construction); `a1.reading` in
  `A1_READINGS`; every outcome's `ladder["64"]["B"].n_blocks == 1`.
- **W2 ABSORBED (habit)**: `within_alone` fires (T .2777); primary does
  not (T .0620, "below the effect bar"); `beyond_single["pi"]` does not
  fire (T .0766); `alone["pi"]` fires (T .6449); `fraction_absorbed`
  .7767 (> .5); licensed sentence == `LICENSED_2J["ABSORBED"]`.
- **W3 ABSORBED (independent)**: primary does not fire (T −.018,
  "inverted"); `declared_status` POWERED.
- **W4 ABSORBED (underpowered)**: same independent world,
  `power_status="DECLARED UNDERPOWERED IN ADVANCE"` passed through
  `write_world_2j`'s own synthetic `power_2j.json` — `declared_status`
  reads back UNDERPOWERED and the licensed sentence downgrades to
  `LICENSED_2J["ABSORBED_UNDERPOWERED"]` ("not detected at this
  resolution...").
- **W5–W9 INSUFFICIENT_DATA**: missing x_B draws (needle "x_B counts
  olmo1b"), missing `power_2j.json` (needle "power record"), missing
  2i `verdict.json` (needle "comparison gate re-derivation"),
  comparison pin mismatch (needle "comparison gate 2i:..."), HALTED
  marker present (needle "HALTED"); on W5/W8, `primary`/`secondaries`/
  `a1` are all `None`.

**Totality** (`test_totality_2j.py`, 18 tests, `n_perm=30/n_boot=10`
throughout except the control): a module-scoped `residual` base world,
`shutil.copytree` per test, `an.run(root_2i=root, root_2j=root,
referents_sha=False, ...)`. The upstream 2i-tree shapes 2i's own
totality already proved reach a terminal through ITS loaders,
exercised once each here through 2j's `run()`: predictor seal missing
/ non-dict-or-torn (3 payloads) / a directory; a truncated x_B draws
gzip at 50% (needle "x_B counts olmo1b", `EOFError` in
`referents.failures`); a torn sweep record (needle "2i sweep
olmo7b"); rung set missing `R_CAP` (needle "2i rung set file"). The
2j-only shapes: `power_2j.json` torn / a bare list (needle "power
record"), wrong `rungs`, an unrecognized `declared_status`; the 2i
`verdict.json` torn / missing `secondaries` / `reverse_direction`
missing `vs_6.9b` (needle "comparison gate re-derivation" in all
three); 2g's `verdict.json` monkeypatched to a torn file (see below);
an x_B predictor record whose `per_seed_tallies.0.full_string` is
mutated while the draws are untouched — 2i's own F-1
attested-vs-re-derived check, reached through 2j's own label "x_B
counts vs the sealed attestation" (needle "attested full_string").
Every case asserts `INSUFFICIENT_DATA`, the needle in `reason`,
`primary`/`secondaries`/`a1` all `None`, nothing raised. The control
(untouched world) reaches RESIDUAL.

**Process note for the controller: "2g's verdict.json path
monkeypatched" needed a symlinked stand-in, not a bare empty
directory.** A bare empty tmp dir assigned to `bg.EXP2G` breaks an
EARLIER `bg.EXP2G`-rooted load first — `strata source 2g predictor`
(`bg.predictor_path(bg.EXP2G)`) and `pythia outcomes 2g 2h`
(`an2g.load_sweep(bg.EXP2G, ...)` inside `load_pythia_outcomes`), both
read `bg.EXP2G` well before `_cmp()` ever opens its `verdict.json` —
proven directly (probe script, not committed) before writing the
test. `experiments/exp2g` is ~2.3 GB, too large to `shutil.copytree`
per test, so `_fake_exp2g_with_torn_verdict` builds a directory that
symlinks every entry under the real `bg.EXP2G` (including every entry
under `results/`) except `results/verdict.json`, which it writes
torn — every OTHER `bg.EXP2G`-rooted read still succeeds through the
symlinks, isolating the one read the shape targets. With that
stand-in the refusal lands exactly at "comparison gate re-derivation"
as the brief's shape names.

**Process note: the control test needs `n_perm=200`, not the file's
`n_perm=30` default.** At `n_perm=30` the permutation p-value floor is
`1/(n_perm+1) ≈ .032`, which can never clear `ALPHA=.01`
(`fires_2i` requires `p < ALPHA` strictly) regardless of how large T
is — the control's first run at `n_perm=30` landed ABSORBED
(T .932, p .032) instead of RESIDUAL, not because the world stopped
forecasting but because 30 permutations cannot resolve a p-value below
.01. 2i's own totality control test hits the same floor and raises
`n_perm` for exactly this reason (300 there); 2j's control raises to
`n_perm=200` (floor ≈ .005), matching what `test_full_shape_2j.py`
already uses. Every refusal test in the file stays at 30/10 — only the
routing to INSUFFICIENT_DATA is at stake there, which n_perm cannot
affect.

**`power_2j.py`** (`tests/test_power_2j.py`, 2 tests): `main()`
writes once, from 2i's machinery, on a synthetic `residual` world
(`pw.N_SIM=4, pw.N_PERM_POWER=10, pw.D_TARGETS=(0.15,)`, monkeypatched)
— `primary.declared_status` in `an2i.DECLARED_STATUSES_2I`,
`primary.rungs`/`composite_report`/`n_composite_strata` all cover
R_CAP exactly, `shape_note`/`note` equal the module's own constants. A
second call against the same `out_path`, and a fresh call against a
pre-existing `out_path`, both raise `RuntimeError("... written
ONCE")`. The `base_strata_reference_2i_B` literals
(`null_sd_T=0.0111`, `min_detectable_T=0.02569`) equal 2i's committed
`experiments/exp2i/results/endpoint/power_2i.json`'s `B.null.
null_sd_T` (rounded 4dp) and `B.min_detectable_T` (rounded 5dp)
exactly — read from the committed file in the test, not re-typed as a
second literal.

**Cold battery** (`verify_referents_2j.py`, `python -m
experiments.exp2j.verify_referents_2j`): **10/12** — items 3
(`referents_2j.json`) and 12 (`power_2j.json` exists) print "pending
Task 4" and are counted separately from the 10 `ok`s (`REFERENTS_2J_
SHA256`/`N_FILES_2J` are still unpinned; no real `power_2j.json` has
been run against the committed tree yet). The other ten ran against
the real committed trees, zero model contact:
- Item 6's real-table drop report surfaced a finding beyond design
  §2's own worked example: O (input overlap) drops `dropped_constant`
  on a FOURTH rung the design doc's three (antonym/antonym6/odd6)
  don't name — **`median5`**, whose answer is always one of the
  option-listing numbers already verbatim in its own question
  (`fn.input_overlap` == 1.0 on all 500 items). Recorded as a finding
  in the check itself, not silently reconciled to the design doc's
  illustrative three.
- Item 7's `matched_k` on the real committed mean rates reproduces
  design §5.4's k table **exactly**: x_B k = {add3_mid 7, add_base8 7,
  arith_next 9, sub_base8 11, antonym 22, antonym6 23, sub3_mid 40,
  odd6 57}; x_A k = {sub4_mid 26} (design's own "≈ 26").
- Item 11 reads `power_2j.py`'s literal off its own source text
  (regex on the `base_strata_reference_2i_B` dict literal) rather than
  re-typing the two numbers a third time, so a future edit to the
  carried literal without a matching edit to 2i's committed reference
  fails this check, not merely `test_power_2j.py`.

Files: `experiments/exp2j/tests/full_shape.py`,
`experiments/exp2j/tests/test_full_shape_2j.py`,
`experiments/exp2j/tests/test_totality_2j.py`,
`experiments/exp2j/power_2j.py`,
`experiments/exp2j/tests/test_power_2j.py`,
`experiments/exp2j/verify_referents_2j.py`. Nothing under
`experiments/exp2i`, `exp2h`, `exp2g`, `exp2d`, `exp2c`, `exp2b`,
`exp3`, `exp3c` touched; `analyze_2j.py`/`functionals_2j.py` (Tasks
1–2) untouched.

Commit: "exp2j build: worlds (RESIDUAL/ABSORBED×3/5 refusals),
totality sweep, power_2j (once), cold battery".
