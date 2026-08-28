# Exp 2j — Freeze Checklist (the adversarial freeze = the whole-branch final review, worked 2026-08-28)

The build ledger (`PROGRESS.md`) is the comparison; nothing here is
ticked until re-run in a fresh process (`PYTHONDONTWRITEBYTECODE=1
~/emergence-lab/.venv/bin/python …`). Assignment: find THE CLASS
DEFECT — the defect that would silently DECIDE the verdict — close what
is found ADDITIVELY (refusals, pins, tests; never an accepted dial,
functional, bucket rule, bar or tree element), and leave a ratification
ledger. Zero model contact, zero network throughout (2j is
analysis-only; there is no model to contact).

Baseline at the build's close (`8a1960fb`): suite 89, fast modules 56,
referent battery 12/12, mutation 61 (60 killed + 1 documented
equivalent), read sweep 0 unpinned, power record POWERED.

## Standing adversarial assignments (worked FIRST, cold)

- [x] The class defect, four lineages: (1) every verdict input pinned
      at analysis time (3c F-A) — **FOUND, F-1**; (2) every tree
      `run()` can be handed reaches a frozen terminal (2d F-1 / 2h
      F-1) — swept, no raise; (3) no self-consistent-only check (3d /
      2h F-2) — **FOUND, F-2** (the power record's partition); (4) the
      tag binds the instrument (2h F-3) — exercised against real git in
      a real temp repo, F-4's tightening applied.
- [x] The 18-item attack list — every item CLOSED / CLEARED /
      DISCLOSED with a demonstration.
- [x] The coverage census (the deferred minors) — triaged, each fixed
      additively or DISCLOSED with a reason.
- [x] Cold re-runs: suite, worlds (every terminal), totality, cold
      battery, mutation (both passes through the committed harness),
      read sweep, two-process determinism.
- [x] Ratification package: findings + disclosures + the exact §-level
      doc wording (the design doc itself UNTOUCHED).

## THE CLASS DEFECT: FOUND (F-1)

**F-1 — the instrument's IMPORT surface was pinned by nothing, and the
read sweep is structurally blind to it.** 3c finding A's lineage
(every verdict input pinned at analysis time), one surface over.

`tests/read_sweep_2j.py` wraps `open` / `io.open` / `gzip.open` /
`Path.read_text` / `read_bytes` and reported **0 UNPINNED** — of the
DATA surface. It cannot see the CODE surface and by construction never
could: the import machinery reads a module's bytes before any wrapper
is installed, and the sweep deliberately pre-imports every module first
so import traffic stays out of its table. A scan of `sys.modules`
after one real-tree `run()` found **24 module entries under
`experiments/` loaded into the analyzer's own process and covered by
NO pin — 23 distinct files** (2c's battery package appears twice, as
`battery` and as `experiments.exp2c.battery`, a consequence of 2c's
own `sys.path` manipulation). Not in `FROZEN_SHA256_2J` (26 named
modules), not in `battery_2g.FROZEN_IMPORT_SHA256_2G` (14), not in
`INSTRUMENT_BLOBS_2J` (the 2 the tag binds), not on
`referents_2j.json` (2,621 data files, whose 24 `.py` entries are all
already in `FROZEN_SHA256_2J` — verified cold, so the manifest adds no
code coverage of its own):

    experiments/exp2j/__init__.py        experiments/exp2i/__init__.py
    experiments/exp2c/__init__.py        experiments/exp2d/__init__.py
    experiments/exp2c/battery/__init__.py    experiments/exp2f/__init__.py
    experiments/exp2c/run/__init__.py    experiments/exp2g/__init__.py
    experiments/exp2c/battery/base.py    experiments/exp2h/__init__.py
    experiments/exp2c/battery/generators_controls.py   experiments/exp3/__init__.py
    experiments/exp2c/battery/generators_rescues.py    experiments/exp3c/__init__.py
    experiments/exp2c/battery/generators_rungs.py      experiments/exp3/analyze_3.py
    experiments/exp2c/battery/wordlists_2c.py          experiments/exp2f/make_referents_2f.py
    experiments/exp2c/instrument.py      experiments/exp2g/collect_eval_2g.py
    experiments/exp2c/run/power_table.py experiments/exp2g/probe_2g.py
    experiments/exp2c/stats_bounds.py

Two of these are on the verdict path in substance, not merely in
principle: `experiments/exp2j/__init__.py` executes on every `import
experiments.exp2j.analyze_2j`, before a line of the analyzer runs; and
2c's item generators are reached by `harness.answer_type_of`, which
`battery_2d.load_item_file` calls to set the `answer_type` that
`normalize_answer` — hence π, hence every composite stratum — branches
on.

**The demonstration (verbatim).** Two lines written into the
0-byte-then, 92-byte-now `experiments/exp2j/__init__.py`:

```python
from experiments.exp2j import functionals_2j as _f
_f.repeated_char = lambda cap: [0] * 500
```

then one real-tree run at `n_perm=30`, with every gate called
explicitly first:

```
check_frozen_2j: PASS ; check_frozen_imports_2g: PASS
manifest check: []
require_prereg_2j: ['experiments/exp2j/analyze_2j.py', 'experiments/exp2j/functionals_2j.py']
payload file: experiments/exp2j/__init__.py 92 bytes; in FROZEN_SHA256_2J: False ; on referents_2j.json: False ; in INSTRUMENT_BLOBS_2J: False ; in FROZEN_IMPORT_SHA256_2G: False
VERDICT ABSORBED T_beyond 0.13301873485425933 failures 0
```

against the same run with the file empty:

```
VERDICT ABSORBED T_beyond 0.13111044507864672 failures 0
```

The primary's T moved, every gate passed, `referents["failures"]` was
empty, and the read sweep's table would still have printed
`UNPINNED 0`. A payload with any other content could put T anywhere.

**Closed additively.** `analyze_2j.IMPORTED_SHA256_2J` (28 files: the
23 above plus five reached only when the fixtures or the cold tool are
imported — `experiments/exp2g/run/__init__.py`,
`experiments/exp2i/run/{__init__,endpoint_2i,sample_2i}.py` and
`verify_referents_2j.py`)
and `check_imports_2j()`, which walks `sys.modules`, keeps every module
whose resolved file is under `experiments/`, and refuses if any is
neither covered by an existing pin (`FROZEN_SHA256_2J`,
`FROZEN_IMPORT_SHA256_2G`, `INSTRUMENT_BLOBS_2J` — the last by
membership only, since the prereg tag binds those two by blob and a sha
literal there would also kill every mutation-battery mutant trivially)
nor pinned here, or if a pinned one has drifted. Wired into `run()`
TWICE, each behind `collect_total` with its own prefix-disjoint label:
`"2j import surface (entry)"` beside the other instrument pins, so a
drifted instrument refuses before any expensive load, and `"2j import
surface (exit)"` immediately before the verdict record is built, so a
module imported DURING the run cannot slip in behind the first check.

**After the closure, the same payload:**

```
VERDICT INSUFFICIENT_DATA | T_beyond None | failures 2
   - 2j import surface (entry): RuntimeError: imported module drifted from its pin: (pin) -> /Users/michaeljordan/emergence-paper/experiments/exp2j/__init__.py
   - 2j import surface (exit): RuntimeError: imported module drifted from its pin: (pin) -> /Users/michaeljordan/emergence-paper/experiments/exp2j/__init__.py
```

Every entry of `IMPORTED_SHA256_2J` is verified against disk
UNCONDITIONALLY (as `check_frozen_2j` verifies its own), not only the
entries this process happens to have imported — a payload that ran and
then deleted itself from `sys.modules` would otherwise leave no trace,
and the pin means "these bytes", not "these bytes if I notice them".

**Tests that now kill it:** `test_check_imports_2j_passes_in_this_
process`, `test_imported_pins_match_disk`, `test_check_imports_2j_
refuses_an_unpinned_loaded_module`, `test_check_imports_2j_refuses_a_
drifted_pin`, `test_check_imports_2j_allows_the_dunder_main_path`,
`test_check_imports_2j_excludes_test_helpers`, `test_run_catches_a_
forced_import_surface_failure` (fast module), `test_import_surface_
failure` (totality world), and mutants #26/#27.

**DISCLOSED exclusion.** Files under a `tests/` directory are exempt:
2i's and 2j's world fixtures live there and are in `sys.modules` under
pytest, while the campaign path (`python -m experiments.exp2j.
analyze_2j --write`) imports none of them — the scan itself is the
evidence. `__main__` is covered because the scan matches on the
module's PATH, not its name (`test_check_imports_2j_allows_the_dunder_
main_path`).

## Findings

### F-2 — the power record's composite partition was attested and never compared

3d's lesson / 2h F-2's "self-consistent-only" lineage, one record over.
`power_2j.main` builds the composite strata from `functionals_2j` and
simulates on them, then writes `composite_report` and
`n_composite_strata` beside its `declared_status`. `_load_power_2j`
checked `declared_status`, the rung set and `n_trained_steps` — never
the partition. The record's BYTES are pinned (it is on
`referents_2j.json`), but `functionals_2j.py` is bound only by the
prereg TAG, which is cut AFTER the power record is written: an edit to
the bucket rule between the two would leave POWERED describing a
partition the verdict never used, and POWERED is exactly what decides
how ABSORBED reads (design §6) — i.e. what the verdict LICENSES.

Demonstration: with the world's power record's `composite_report`
altered on one rung (`"L": "median"` → `"terciles"`), the un-closed
analyzer returned the world's normal terminal with no failure
mentioning the record; after the closure it returns INSUFFICIENT_DATA
with `2j power partition: bucket rules on <rung> {...} != the
analyzer's {...}`.

Closed additively: `check_power_partition_2j(power, report, n_strata,
r_cap)` (returns failures, never raises), called behind
`collect_total(..., "2j power partition")` once the core has built the
realized partition. Every message is label-prefixed so a returned
failure list is self-identifying. `_core` now also returns the
realized `n_composite_strata`, which is written into the verdict
record beside `composite_report`. **On the real tree the check
PASSES**: the analyzer's realized counts are `add3_mid 47, add_base8
24, antonym 31, antonym6 48, arith_next 16, odd6 48, sub3_mid 39,
sub4_mid 55, sub_base8 23` — identical to the committed record's, and
every rung's bucket-rule report matches. Tests: five fast unit cases,
three totality worlds (rule mismatch / count mismatch / no partition
attested), cold battery item 12, mutants #28/#29.

### F-3 — the block gate proved the MEAN only

Attack item 4. `t_only` is a second implementation of the per-rung
Somers' D and the unweighted mean over rungs; the k = 64 block gate
compared only its `T` against `within_alone`'s. Every A-1 reading is
built out of per-rung d's, not out of T, so a compensating pair of
per-rung differences would have passed the gate and left the whole A-1
ladder unvalidated. Closed additively: the gate now also requires the
per-rung d dict to be equal bit-for-bit and over the same rung set.
Verified on the real tree BEFORE the check was added — per-rung d's
identical on all 9 rungs (`per-rung d mismatches: {}`), so the
tightening cannot introduce a refusal the current bytes would hit.
Mutant #31 (world/totality).

### F-4 — two cross-experiment label prefixes, DISCLOSED not renamed

Attack item 14, found by the new cross-set test. Only two prefix
relations hold across 2i's and 2j's literal failure labels, both a 2j
label EXTENDING a 2i one: `"battery items"` ⊃ `"battery"` and
`"verify criterion 3c"` ⊃ `"verify criterion"`. Both name the very
same loader on both sides (`battery_2g.load_battery`,
`analyze_2d.load_verify`), and neither can put a 2j-side failure under
a 2i-side name — the direction the "2i …"-prefix rule protects. No 2j
label EQUALS a 2i label. Left as they are and pinned by
`KNOWN_CROSS_PREFIXES_2I` in `test_no_2j_failure_label_collides_with_
a_2i_one`, so a NEW collision fails the test.

Related and disclosed: a check that RETURNS a failure list (rather
than raising) contributes its own message text, not the
`collect_total` label — 2i's own convention, inherited. 2j's new
`check_power_partition_2j` therefore label-prefixes each of its five
messages itself.

### F-5 — the realized-THIN guard was installed on one branch only

The build's fix round 1 (2i's I-4 standard) added a realized-THIN
disclosure — fewer than three eligible rungs after the composite
partition, whatever the power record says — to `verdict_tree_2j`'s
NON-FIRING branch. The firing branch had none: a primary that fires on
two rungs would have been RESIDUAL with the full mechanism licence and
no word about what carried it. Closed additively and
disclosure-only: the same guard now runs in the firing branch, riding
the reason string and (through `_licensed`) the licensed sentence. The
TERMINAL is untouched — a firing THIN primary is still RESIDUAL, which
is the tree Michael accepted; only the sentence gains a clause.
Unreachable on the real tree (all nine R_CAP rungs are eligible under
the composite partition, `thin: []`, `dropped_degenerate: []`).
Mutant #30; tests
`test_a_firing_but_realized_thin_primary_still_carries_the_thin_
disclosure` and `test_a_firing_primary_on_three_or_more_rungs_carries_
no_disclosure`. **If Michael would rather the firing branch stay
silent, deleting the three lines marked `freeze F-5` in
`verdict_tree_2j` restores the build's behaviour exactly.**

## Attack-list disposition (all 18) — CLOSED 4 / CLEARED 12 / DISCLOSED 2

| # | item | disposition | evidence |
|---|---|---|---|
| 1 | the π predicate vs verify, every draw | **CLEARED** | full census, not a sample: 11 strata rungs × 2 predictors × 500 × 64 = **704,000 draws, 0 disagreements** between `normalized_draw(d, at) == a_i` and `verify_fn(d, raw_answer_i, at)`; **0** draws the normalizer raised `IndexError` on; **0** normalized answers equal to `None` (so the draw-side `None` sentinel can never collide). The unreachable-on-this-corpus branch proved by hand: `normalize_answer(".\xa0.", "word")` raises `IndexError`, `normalized_draw` → `None`, `verify_fn(".\xa0.", "cold", "word")` → `False`, predicate == verify. Swapped-target (3e's specificity construction) on sub_base8: 12,800 (draw, target) pairs, 0 disagreements. |
| 2 | same-answer exclusion completeness | **CLEARED** | `wrong_target_propensity` keys `by_answer` on `normalized_answers(cap)`, so items whose RAW answers differ but normalize alike share one class by construction. On the real files raw and normalized coincide (sub_base8 52/52 distinct, add_base8 100/100, antonym 111/111; 0 items where raw ≠ normalized), and the largest same-answer class is **28** on sub_base8 — design §10 d's own example ("28 items share the answer '3'"). Mutant #5 (numerator no longer excludes same-answer draws) is killed. |
| 3 | the bucket rule on the real tables; pairs per rung | **CLEARED** | every (rung, functional) rule printed below; **no `dropped_after_fallback` anywhere**; O `dropped_constant` on antonym/antonym6/odd6 (and median5, outside R_CAP — slip (b)). Composite n_pairs per rung 2,105–14,366, total **44,727** against **297,573** under base strata — the finer partition costs 6.7× the pairs, which is what the power record's null SD 0.0114 (vs 2i's 0.0111 under base strata) prices. Smallest cells are size 1 and contribute no pair by construction. |
| 4 | the block gate is the only k = 64 check | **CLOSED (F-3)** | per-rung d equality now asserted too; identical on all 9 rungs on the real tree. `thinned_counts(bits, 64, 0) == counts_from_bits(bits) == x_B[r]` on all 9 (so the gate really does compare `t_only` against `_run_test` on the same numbers). |
| 5 | `a1_density` mixes thinned and unthinned rungs in one T | **DISCLOSED** | as designed (§5.4 thins "the denser predictor on each rung"): on the committed rates B is denser on 8 of 9 R_CAP rungs and A on exactly one (**sub4_mid**, k = 26, rates .0005 A vs .0002 B), so `thinned_B_matched` carries sub4_mid at B's full 64 draws (one block, mean .0071). Self-consistent: at 2.8b and 6.9b, where B is denser on every rung, `thinned_A_matched` equals the x_A anchor EXACTLY (.16722141085849532 and .2179084483862053). Doc slip (e). |
| 6 | the 6.9b anchor: 8-rung gate vs 7-rung A-1 | **DISCLOSED** | both printed in the verdict record: `referents.comparison["2h"]` = **0.20197097010795367** (2h's own 8-rung R_69, the literal-pinned gate) and `a1.outcomes["6.9b"].anchors.x_A_64` = **0.2179084483862053** (the 7-rung `r69 = R_CAP ∩ R_69` re-derivation the thinned readings are computed on). Same for 2.8b, where `r28 == R_28` as a set so the two coincide. Doc slip (f). |
| 7 | `rederive_2i` must not depend on `r_full` ordering | **CLEARED** | T with the extra rungs present == T with the counts dict trimmed to `r_cap`, EXACTLY (`0.09491251078607414` both). Rung ORDER does move the last ulp (reversed: `0.09491251078607413`) — float summation order in `np.mean`; every gated call uses the predecessor's own order (`tuple(bg.R_28)`, `tuple(bh.R_69)`, `r_cap` from the committed rung-set file), which is what makes the three comparison gates reproduce their literals to full precision. Disclosed as a note, no change. |
| 8 | totality: every tree reaches a terminal, none raises | **CLEARED** | 29 totality shapes green (25 inherited + 4 new: three power-partition shapes and the import surface). No shape raises; every one asserts INSUFFICIENT_DATA, the needle, and `primary`/`secondaries`/`a1` all `None`. |
| 9 | the comparison gate's `verdict_2i_path` default and the 2g/2h verdict files are on the manifest | **CLEARED** | `experiments/exp2i/results/verdict.json`, `experiments/exp2g/results/verdict.json`, `experiments/exp2h/results/verdict.json` all present in `referents_2j.json`, together with 2i's **771** sweep JSONs, `results/power_2j.json` and `power_2j.py`. |
| 10 | power-record provenance: does the analyzer check the record's partition? | **CLOSED (F-2)** | it did not; it does now, and the check passes on the real tree. |
| 11 | read sweep: zero unpinned verdict inputs | **CLOSED (hardened)** | re-run cold, table below. Hardened three ways (coverage census): classification is now against the COMMITTED manifest's key set rather than a live `referent_files()` call (a live call would list any file that appeared on disk since the manifest was built, and so could classify an unpinned read as pinned — the live list is still compared and any difference printed); every stdlib/venv prefix carries its separator; the F-1 import pin joins the `frozen` bucket. The docstring's overclaim (that the stand-ins reach the two 2i seal checks — they reach `require_prereg_2j` only, `blobs_bound` being left at real git) corrected. |
| 12 | determinism, two processes | **CLEARED** | numbers below. |
| 13 | the tag binds the instrument, real git | **CLEARED** | `test_prereg_tag_binds_the_instrument_against_real_git`: a real temp repo, real `git init/add/commit/tag`, the campaign's own `pr.git_tag_exists` / `pr.git_blob_sha256` (`git show <tag>:<path>`) — the two blobs bind; a post-tag edit to `functionals_2j.py` raises "does not bind"; deleting the tag raises "preregistration tag". |
| 14 | label prefixes, incl. against 2i's | **CLOSED (F-4)** + widened | the prefix-disjointness test now scans the instrument-pin loop's tuple labels, `check_pin`'s label argument, `_sec`'s name and the two seal-binding f-string prefixes, not only `collect_total(thunk, "…")` — 2j's own set is prefix-disjoint under the widened scan; the two cross-set extensions are pinned and disclosed. |
| 15 | `decomposition`'s `alone` size label | **CLEARED** | `_scores_predictor_2i` uses the size label as a dict key only: the same functional scored under `"1b:L"` and under `"zzz"` gives the identical T (`-0.16332671085726824` both). Covers the census item about `matched()`'s bare `"A"` too. |
| 16 | the hard-coded "six carried rungs" | **CLEARED** | `six = tuple(r for r in r_cap if r not in ("add3_mid","sub3_mid","sub4_mid"))` = `['add_base8','antonym','antonym6','arith_next','odd6','sub_base8']`, n = **6**, and equals `(R_69 ∩ R_CAP) − {the three mid-digit rungs}` computed independently — the six 2h-carried rungs design §5.6 names. |
| 17 | two-tailed: "inverted" carried into ABSORBED's reason | **CLEARED** | `named_inside_2i` prints `inverted (T = …; one-sided p for T_perm <= T_obs ~ …)` for T < 0 and `verdict_tree_2j` splices it into the ABSORBED reason verbatim — asserted by `test_an_inverted_primary_says_so_in_the_absorbed_reason`, and observed live in world W3. |
| 18 | JSON strictness, `allow_nan=False` | **CLEARED** | NaN proved REACHABLE, not hypothetical: `stats_2g.bootstrap_d` returns `lo`/`hi` NaN with `n_boot: 0` when no resample has a finite d, and those land in `primary["per_rung"][r]["ci"]`. `json.dumps(v, allow_nan=False)` on such a dict raises `ValueError`; the write path's `an2i._json_safe` + `allow_nan=False` turns them into `null` and leaves the finite values untouched — asserted end to end. Nothing in the verdict has a non-string dict key. |

### The composite rule report and pair counts on the real tree (item 3)

| rung | π | L | R | O | composite strata | n_pairs | smallest / largest cell | cells < 10 |
|---|---|---|---|---|---|---|---|---|
| add3_mid | median | tie_fallback | median | median | 47 | 3,165 | 1 / 36 | 27 |
| add_base8 | median | tie_fallback | median | median | 24 | 2,852 | 1 / 58 | 11 |
| antonym | median | median | tie_fallback | dropped_constant | 31 | 4,383 | 2 / 40 | 7 |
| antonym6 | median | median | tie_fallback | dropped_constant | 48 | 2,711 | 1 / 21 | 20 |
| arith_next | median | median | median | median | 16 | 14,366 | 2 / 124 | 3 |
| odd6 | median | median | median | dropped_constant | 48 | 3,567 | 1 / 34 | 31 |
| sub3_mid | median | tie_fallback | median | median | 39 | 4,597 | 1 / 58 | 18 |
| sub4_mid | median | tie_fallback | median | median | 55 | 2,105 | 1 / 25 | 34 |
| sub_base8 | median | tie_fallback | median | median | 23 | 6,981 | 1 / 94 | 10 |

## Coverage census — the deferred minors, triaged

| item | disposition |
|---|---|
| sensitivities discard ~9 permutation tests each (`decomposition(…)["beyond_all"]`) | **DISCLOSED**, no change. A runtime cost on a non-gating printed quantity, not a verdict risk; a `singles=False` flag is neither a refusal, a pin nor a test, and the freeze does not touch the computation path for speed. Cost: roughly 30 extra `_run_test` calls at N_PERM 10,000 inside the ~25-minute run. |
| the two `run()` tests that cannot fail for the right reason | **CLEARED**: `test_run_catches_a_forced_referent_manifest_check_failure` already lets `referents_sha` default to the pinned literal and forces `check_referents` to raise, asserting the `"2j referent manifest"` label — which is exactly the case the minor asked for. The empty-root test is a routing test by design; its sibling assertions (`primary`/`secondaries` None, the caveat) are what it proves. |
| the prefix-disjointness test's blind spot | **CLOSED**: widened scan (F-4 above). |
| `load_pythia_outcomes` runs before the `if not failures` gate | **DISCLOSED**, no change: 2g's and 2h's full sweep re-verification runs even on a doomed tree (a runtime cost of seconds, since both trees are committed and small), and moving a loader would reorder which failures are collected — an ordering change to the refusal path, which the freeze does not make for speed. |
| worlds stub `tag_exists`/`blobs_bound` | **CLOSED at fixture level, DISCLOSED at world level**: no world exercises a tag/blob refusal; the real-git temp-repo test (item 13) and `verify_referents_2j` check 2 do, and the empty-root tests exercise the collected-refusal route. |
| W2's ABSORBED rests on a tuned dial at one seed | **CLEARED**, see the seed-robustness probe below. |
| read_sweep docstring / manifest bucket / prefixes | **CLOSED** (item 11 above). |
| battery `_c12` lacks the `n_trained_steps` check | **CLOSED**: item 12 now checks `n_trained_steps`, that `composite_report` and `n_composite_strata` cover R_CAP, and that the record's partition equals the one the analyzer builds today (F-2, cold). |
| the mutation log's SKIP-vs-survivor summary | **CLOSED**: the summary line now separates real survivors from SKIPs (a stale mutant whose target text is gone), which are different findings. |
| `matched()`'s size label for side A is the bare literal "A" | **CLEARED**: attack item 15's demonstration — the size label is a dict key and moves no statistic. |

## Ratification package — doc slips and disclosures (the design doc UNTOUCHED)

Carried from the build (a)–(d), plus (e)–(h) from the freeze. Exact
§-level wording for Michael:

**(a) §6, after terminal 3 (ABSORBED).** Add: "An undefined primary
(x_B constant inside every composite stratum on every eligible rung,
2i's Ruling 18) or a realized-THIN primary (fewer than three eligible
rungs after the composite partition) lands ABSORBED with the
disclosure carried on the reason string AND the licensed sentence, and
licenses NOTHING — the residual is untested, not absent (2i's I-4
standard). Symmetrically (freeze F-5), a primary that FIRES on fewer
than three eligible rungs is RESIDUAL — the terminal is unchanged —
with the same THIN disclosure on its reason and its licensed
sentence."

**(b) §2, the sentence "the input-overlap functional is constant (1.0)
on the three option-listing rungs".** Amend to: "…constant (1.0) on
the three option-listing rungs of R_CAP (antonym, antonym6, odd6) and
is dropped there by the §5.2 rule; median5, in 2g's eleven covered
rungs but outside R_CAP, drops O too."

**(c) §2 (and §11's build note).** Add: "Also known to the designer
before the tag: the primary's own T_beyond on the real tree
(0.1311), printed by the build's read sweep at n_perm 30 — T does not
depend on n_perm, so the sweep's incidental output is the real value.
No functional, bucket rule, partition or tree element was chosen after
it; §5 was frozen before any computation ran. The projection carries
the same disclosure, on 2e's precedent."

**(d) §5.4, after "the A-1 reading of a rung is the mean over
blocks".** Add: "…that is, per rung: each block's per-rung d exactly
as `t_only` computes it, the rung's reading the mean over ITS OWN
blocks with min and max printed, and T the mean over eligible rungs of
those readings; the ladder is read the same way, and the
zero-fraction sensitivity uses block 0."

**(e) §5.4, after the k table.** Add: "Because the rule thins the
DENSER predictor on each rung, a rung where the other predictor is
denser keeps its full 64 draws in that side's matched reading: on the
committed rates x_B is denser on eight of the nine R_CAP rungs and x_A
on one (sub4_mid), so `thinned_B_matched` carries sub4_mid un-thinned
and `thinned_A_matched` equals the x_A anchor exactly on the two
Pythia outcomes, where x_B is denser everywhere."

**(f) §5.4, reading 1 (reverse direction), after "x_A at 64 (2g .1672 / 2h
.2020)".** Add: "The 6.9b anchor is printed twice and they differ by
construction: the comparison GATE re-derives 2h's primary over 2h's
own eight-rung R_69 (.2020, the literal pin), while A-1's anchor is
x_A at 64 over the seven rungs R_CAP ∩ R_69 that A-1's thinned
readings use (.2179). The gap fraction is computed against the
seven-rung anchor."

**(g) §4 (instrument pins) and §6's terminal 1 (INSUFFICIENT_DATA), the refusal list.** Add two inputs to
INSUFFICIENT_DATA: "the analyzer's own import surface — any module
under `experiments/` in `sys.modules` that is not pinned, or that has
drifted from its pin (freeze F-1; files under a `tests/` directory
excluded and disclosed)" and "the power record's composite partition
not equal to the partition the analyzer realizes (freeze F-2)."

**(h) §5.3/§4, the block gate.** Amend "Thinning at k = 64 (one block)
must reproduce every 64-draw referent above exactly" to add: "…
including the per-rung within-stratum D, not only the mean T."

**Disclosures carrying no doc change:** the two cross-experiment label
prefixes (F-4); T's last-ulp dependence on rung ORDER (item 7); the
`tests/` exclusion in the import-surface check; the sensitivities'
discarded permutation tests and `load_pythia_outcomes`' eager run
(runtime only).

## The W2 seed-robustness probe (coverage census)

W2's ABSORBED rested on a tuned `hot_ratio` at a single seed. Rebuilt
from scratch at three seeds through the real `write_world_2j` +
`run_world` path (n_perm 200, n_boot 20), transcribed from the run:

| seed | verdict | within_alone T | beyond_all T (primary) | fires | fraction absorbed |
|---|---|---|---|---|---|
| 0 | ABSORBED | 0.277696 | 0.062007 | False | 0.7767 |
| 1 | ABSORBED | 0.254894 | 0.038623 | False | 0.8485 |
| 2 | ABSORBED | 0.279176 | 0.093672 | False | 0.6645 |

Seed 0 reproduces the build ledger's numbers exactly
(0.2776959534767129 / 0.06200662138616882 / .7767) after the fixture
gained its composite-partition block, so F-2's change to
`write_world_2j` moved no world statistic. The terminal is stable
across the three seeds. Stated plainly rather than talked up: seed 2's
`beyond_all` is 0.0937, within .007 of `T_BAR` — W2's ABSORBED is not
a wide margin, which is a property of the fixture's tuned habit
mechanism (a single median split over a bimodal habit weight), not of
the instrument. The world's job is to route a habit-driven tree to
ABSORBED, which it does at every seed tried; nothing in the verdict
depends on the margin.

Pin-coverage arithmetic, re-derived cold: the referent manifest lists
24 `.py` files, **all 24** already in `FROZEN_SHA256_2J` (so the
manifest adds no unpinned code); `IMPORTED_SHA256_2J`'s 28 entries
overlap `FROZEN_SHA256_2J` in 0 and the manifest in 0 — they are 28
genuinely new pins, which is the size of the hole F-1 names.

## Cold re-runs at the freeze HEAD

Every number transcribed from the run, fresh process,
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python`.

| check | command | result |
|---|---|---|
| full suite | `pytest -q experiments/exp2j` | **113 passed in 929.84 s (15:29)**, 0 failures, 0 warnings (was 89 at the build's close; +24 — 20 in `test_analyze_2j.py`, 4 in `test_totality_2j.py`) |
| worlds (every terminal) | inside the suite, `test_full_shape_2j.py` (5) + `test_power_2j.py` (2) | all green; the nine terminals (RESIDUAL, ABSORBED ×3, five refusals) reached with the fixture's new composite-partition block |
| totality | inside the suite, `test_totality_2j.py` | **30 shapes**, every one INSUFFICIENT_DATA under its own needle, nothing raised; the control still reaches RESIDUAL |
| cold battery | `python -m experiments.exp2j.verify_referents_2j` | **12/12**, item 12 now including `n_trained_steps` and the F-2 partition re-derivation |
| mutation, fast pass | `python experiments/exp2j/tests/mutation_check.py` (committed harness, detached; log `mutation_build.log`) | **70 mutants, 58 killed, 12 survivors** `[10, 20, 31, 60, 61, 63, 64, 65, 66, 67, 69, 70]` — #10 the documented equivalent, the other 11 world/totality-only by construction |
| mutation, totality pass | `… --totality --only 20,31,60,61,63,64,65,66,67,69,70` (log `mutation_round1.log`) | **11/11 killed, 0 survivors, 0 SKIP** |
| **mutation, final tally** | both logs, both reproducible from the committed harness | **70 mutants — 69 killed (58 + 11), 1 documented equivalent (#10, `matched_k`'s dead upper clip), 0 open survivors** |
| read sweep | `python -m experiments.exp2j.tests.read_sweep_2j` | **4,347 distinct paths read (10,313 open/read calls), 0 writes, UNPINNED 0**; buckets: referents_2j.json 2,622, frozen_module 38, instrument_blob 2, sha_pin_at_load 2, python_stdlib_venv 1,683. (frozen_module 33 → 38: F-1's unconditional pin loop hashes all 28 pinned files, so the import surface is now visible to the DATA sweep too.) |
| determinism ×2 | `run(n_perm=30, n_boot=10)` in two separate processes, sha256 over the JSON-serialized verdict with `git_sha` removed | **byte-identical**: `d9284f6b8ceabfe0cf93b61bfd2de2a76afaf4729a86acb540c6655a998ad976` both times, `ABSORBED T=0.13111044507864672` |

The n_perm-30 verdict printed by the sweep and the determinism runs is
NOT the experiment's verdict (the p-value floor at 30 permutations is
1/31 ≈ .032, which can never clear ALPHA .01) and nothing was written
under `results/`. It is reported here only because doc slip (c)
already discloses that T_beyond's real value is known before the tag.

## Notes for the tagger

- The tag `exp2j-preregistered` must be cut at the commit carrying the
  FINAL `analyze_2j.py` and `functionals_2j.py` — they are the two
  blob-bound instrument files (2h F-3). `functionals_2j.py` was not
  touched by this freeze; `analyze_2j.py` was (F-1, F-2, F-3).
- `power_2j.py` and `make_referents_2j.py` are pinned by sha inside
  `analyze_2j.py` and were NOT touched; `referents_2j.json` was not
  rebuilt (no manifest-listed file changed) and its literal is
  unchanged.
- The power RECORD was not recomputed. The partition it was simulated
  over is now checked against the analyzer's, and matches.
- `verify_referents_2j.py` changed (battery item 12) and is pinned in
  `IMPORTED_SHA256_2J`; the pin was taken after the edit.
- **Operational consequence of F-1, stated plainly:** run the campaign
  as `python -m experiments.exp2j.analyze_2j --write` (or from a driver
  that imports only `analyze_2j`). A driver that imports some other
  `experiments/` module not in the pin sets will REFUSE with
  "unpinned module on the import surface: <name> -> <path>" — loud,
  immediate, and diagnosable from the message, but it will refuse.
- `IMPORTED_SHA256_2J` lives inside `analyze_2j.py`, so the prereg tag
  binds it along with everything else in that file.
