# Experiment 4c — adversarial freeze (Task 6, 2026-09-19)

Fresh-eyes reviewer, cold, on `experiments/exp4c/` at build HEAD
`d2cbc8fb8` (Task 5 fix round 2's own state). The standing assignment,
verbatim from the program: find THE CLASS DEFECT — the defect that
would silently DECIDE the verdict — and close what is found ADDITIVELY
(a new refusal, pin, test, disclosure or record field; never an
accepted dial, never a change to a preregistered statistic or bar).
Precedents read first for the form: `experiments/exp4/FREEZE_CHECKLIST.md`
(F-1, attested vs measured digest), `experiments/exp4b/FREEZE_CHECKLIST.md`
(F-3, a licence sentence that asserts a fact about the data).

Zero model contact and zero network throughout. Every execution of
`analyze_4c.run()` against the REAL tree (`root=EXP4C`, `root4=EXP4`)
is a disclosure event; the running total was **11** at the start of the
session and is **15** at the end — §D below lists this session's four
and what each printed. Worlds on tmp trees do not count.

Python `~/emergence-lab/.venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
from the repo root, `-p no:cacheprovider`. The environment carries no
`timeout(1)` binary and the session's foreground call cap is 600 s, so
runs longer than that were detached with `Popen(start_new_session=True)`
(the harness's `run_in_background`) and polled — the brief's own
pattern.

## Baseline, measured cold BEFORE the freeze touched anything

| battery | result |
| --- | --- |
| fast suite (`experiments/exp4c/tests/`, `-m "not slow" -W error`) | **117 passed**, 79 deselected, 42.4 s |
| cold referent battery (`verify_referents_4c.py`, real tree) | **11/12** + 1 legitimate skip (item 12, gate 0, pre-campaign) |
| import scan (`tests/import_scan_4c.py`) | 0 frozen + **5 exp4c-own residual modules, byte-identical to the committed `IMPORTED_SHA256_4C`** |
| read sweep (`tests/read_sweep_4c.py`) | not re-measured cold at the baseline; measured after the closures (§C) |
| totality + worlds (slow) | build HEAD's own last run: totality 53, worlds 24 + 1 xfail |
| mutants (`tests/mutation_check.py`, committed logs) | 106 considered — 53 fast-killed, 51 world-only killed, 2 equivalent, **0 unresolved** |
| world cache (`/private/tmp/exp4c_world_cache`) | present, 1.4 GB, four modes, keyed `<mode>_<seed>` |
| npz byte determinism (numpy 2.4.6) | two `savez_compressed` of the same array 2.2 s apart: **byte-identical** (the zip timestamp is zeroed) — gate 1's byte comparison across writers is feasible |
| Exp 4's `ladder_pythia_6.9b` record vs 4c's 6.9b endpoint pins | `tensor_digest` == 2h's committed step143000 digest, render `plain`, batch 16, sites 12/33, refs and pairing equal, numpy 2.4.6 both sides |

## Verdict on the assignment: **the CLASS DEFECT WAS FOUND.**

**F-1: `run/sweep_4c.py` — the producer of every set table the verdict
is read on — never pinned its own import surface.** `analyze_4c.run()`
pins it at entry and exit (2j F-1, lesson 11), but the runner checked
only `require_prereg_4c` (seven instrument blobs) and `check_frozen_4c`
(exp2\*/exp3\*/exp4/exp4b). On the runner's own import chain exactly two
modules sit outside every table it checks —
`experiments/exp4c/__init__.py` and `experiments/exp4c/run/__init__.py`
— and both are covered only by `IMPORTED_SHA256_4C`, which only the
ANALYZER reads. A drift present during the 45-hour sweep and reverted
before the analyzer ran was invisible on both sides. Six findings in
all, every one closed additively. Nothing preregistered moved:
`ALPHA_4C`, `MARGINAL_4C`, `MIN_CLEAR_INDEX_4C`, `CAL_MULTIPLE_4C`,
`N_BOOT_4C`, `B_PLACEBO_4C`, `SEED_4C`, `EXCLUDED_SITES_4C`,
`MAX_ENUMERATE_4C`, the family-block null, the placebo's construction,
the tree, the modifier rule, §5's statistics and
`results/power_4c.json` are byte-identical to the build's.

---

## A. Findings

### F-1 — the RUNNER never pinned its own import surface (THE CLASS DEFECT; 2j F-1 / lesson 11, on the producer). CLOSED.

**The defect.** Everything downstream of the sweep verifies the set
tables against *themselves*: `load_record_failures_4c` re-hashes each
`sets/<rung>.npz` against the record that names it, `_read_sets_and_overlaps`
asserts the shape, `unit_complete_4` re-hashes on resume. The only
checks that reach OUTSIDE a unit are the measured `tensor_digest`
against the committed 2h/2l digest (which pins the *checkpoint*, not
the *collection*), gate 0, and gate 1 — and gate 1 covers the ENDPOINT
only. On `pythia_6.9b` gate 1 is a genuine two-writer comparison (Exp
4's own `collect_4.process_model_4` wrote the ladder table); on
`olmo2_13b` both sides are written by `collect_4c.process_model_4c` in
the same process, so it is a two-LOADER-path check that cannot see a
collector-level defect at all. An interior checkpoint has no comparator
anywhere. What stands behind those tables is therefore exactly the code
the runner executed — and the runner did not pin it.

**The executable demonstration, in two halves.**

*(i) the drift is not refused by the producer, and the consumer sees it
only if it is still there.* Two lines in `experiments/exp4c/__init__.py`:

```python
from experiments.exp4 import collect_4 as _c
_orig = _c.set_tables_4
_c.set_tables_4 = lambda X, k=10: _orig(X, k=k)[:, ::-1, :, :]   # swap prompt_end/question_end
```

```
collector patched at import time: <lambda>
[4c sweep] prereg tag 'exp4c-preregistered'; thin endpoint pending; gate 1 olmo2_13b pending; would run 16 unit(s)
RUNNER: NO REFUSAL — the drifted __init__.py passed the whole chain
ANALYZER check_imports_4c RAISED: imported module drifted from its pin: (pin) -> .../experiments/exp4c/__init__.py
```

The runner's whole refusal chain — prereg tag, frozen modules, Exp 4's
reference seal, the power record, the halt marker — passed it. The
analyzer catches it, but only at analysis time; the sweep runs for 45
hours before that, and the same two lines make `dial (l)`'s primary
position (prompt-end) into the question-end everywhere.

*(ii) what a drift buys.* On a `replicates` world, every rung's set
table of ONE interior 13B checkpoint (grid index 4, `step16000`)
replaced by random neighbour sets of the same shape and dtype, with the
stored `overlap_<ref>` arrays recomputed and `sets_sha256` restamped —
i.e. exactly what a differently-behaving collector would have written:

```
[baseline] verdict=REPLICATES U=1.0                p+=0.001953125 n_failures=0
    gate1 olmo2_13b: n_rungs=34 digest_equal=True all_sets_equal=True
    gate1 pythia_6.9b: n_rungs=34 digest_equal=True all_sets_equal=True
    gate0 olmo2_13b: pass=True frac=0.9993 | gate0 pythia_6.9b: pass=True frac=1.0000
[ATTACK]   verdict=REPLICATES U=0.9487179487179487 p+=0.001953125 n_failures=0
    gate1 olmo2_13b: n_rungs=34 digest_equal=True all_sets_equal=True
    gate1 pythia_6.9b: n_rungs=34 digest_equal=True all_sets_equal=True
    gate0 olmo2_13b: pass=True frac=0.9993 | gate0 pythia_6.9b: pass=True frac=1.0000
```

U moved, every gate passed, `failures` stayed empty. (A companion probe
perturbed the 13B *endpoint* and its thin-endpoint comparator
identically: gate 1 still reported `all_sets_equal=True` and zero
failures — the 13B gate cannot see a change common to both sides.)

**The closure (additive).** `run/sweep_4c.py`'s `run()` calls
`analyze_4c.check_imports_4c()` immediately after `check_frozen_4c()`
and before the seal, so the producer and the consumer are pinned by ONE
surface. Verified that the runner's own import chain is fully covered
by the existing tables (71 modules with the analyzer loaded, 0
unpinned), so the new refusal is a gate and not a permanent halt. No
new record field is needed: `require_prereg_4c` binds
`run/sweep_4c.py` itself to the tag, so a unit written under the tag
was written by a runner that ran the check.

**Tests.** `test_stages_4c.py::test_sweep_refuses_a_drifted_import_surface`,
`::test_sweep_refuses_an_unpinned_module_on_its_own_import_surface`
(both FAIL with the one closure line replaced by `pass` — confirmed),
`::test_the_runners_own_import_surface_is_covered_by_the_analyzers_table`.

---

### F-2 — the power record's cell structure was never compared to the cells the verdict is read on (3d's lesson, one experiment over). CLOSED.

**The defect.** `_power_record_failures_4c` checks the committed
record's `cells_sha256` against `power_4c.cell_structure_4c()` — a
structure re-derived from the SAME pins the record was written from.
That is a self-consistency check: it says the record has not been
edited, never that the decision §4 modelled is the decision the verdict
delivers. §4's whole claim ("the null distribution of the decision does
not depend on the data — the cell structure of §3.2 fixes it
completely") is a claim about the realized cells, and nothing compared
the two.

**Reachability, stated plainly rather than talked up.** Not reachable
through the real producer: `check_rung_set_pins_4c` fixes R, flat,
transient and every clear index against the tag-bound literals before
`cells_4c` runs, and a missing `t_clear` raises inside
`clear_indices_4c` and is collected. The finding is closed because the
power record's own claim names this comparison and because a future
amendment to either side would otherwise move the modelled structure
away from the realized one in silence.

**The closure (additive).** `analyze_4c.power_structure_failures_4c(power,
cells)` compares the realized cells to the COMMITTED record's own
`structure` on `(traj, rung, family, type, n_flat, n_flat_arith)`,
wired in as a `collect_total_4c` site immediately after the cells are
built; any disagreement is INSUFFICIENT_DATA naming the pair.

**Tests.** eight fast in `test_analyze_4c.py` (clean on the committed
record; a cell the verdict never read; a cell the record never
modelled; each of `n_flat`, `n_flat_arith`, `family`, `type` changed; a
record with no structure) and a totality route
(`test_a_cell_the_power_record_never_modelled_gives_insufficient_data`
— `cells_4c` returning one cell fewer gives INSUFFICIENT_DATA naming
`antonym`).

---

### F-3 — gate 1's comparator is answerable COLD, and nothing answered it until ~40 minutes of shard streaming had been spent (2i's pre-tag loader-rehearsal lesson). CLOSED.

**The defect.** Gate 1 compares the sweep's endpoint unit byte for byte
against the reference `GATE1_REFERENCE_4C[traj]` names. For
`pythia_6.9b` that reference is Exp 4's committed, seal-bound
`ladder_pythia_6.9b` table, and every field that decides whether a byte
comparison CAN succeed — the checkpoint it was collected on, the
render, the batch composition, the site family, the reference set, the
depth pairing, 34-rung coverage — is readable from committed bytes with
no model loaded. `run_gate1` learned it only after loading the
endpoint, and a mismatch halts the campaign rather than the launch. The
design's §7 plan runs 6.9b first for ~15 h; a comparator that cannot
match would be discovered at the end of the first load.

**The closure (additive).** `battery_4c.gate1_comparator_failures_4c(root,
root4, traj)` — cold, model-free — called by `sweep_4c.run()` before
any loader is built, plus cold-battery item 13. The checkpoint identity
is REPORTED (`digest_equal`), not refused, so `run_gate1`'s own
preregistered halt-with-marker route is not pre-empted; that boundary
is pinned by a test in both directions. `available` is False for
`olmo2_13b`, whose comparator is this run's own thin endpoint.

**Measured today, cold:**

```
pythia_6.9b: exp4/ladder_pythia_6.9b digest_equal, pins equal
olmo2_13b:   exp4c/endpoint_olmo2_13b not written yet (this run's own)
```

**Tests.** nine fast in `test_battery_4c.py` (the real committed
ladder; a synthetic matching comparator; each of render / batch_size /
n_hidden / sites / refs wrong; a wrong pairing; a short `sets_sha256`;
a digest mismatch REPORTED and not refused; an unreadable record) and
two in `test_stages_4c.py` (the runner refuses on a `failures` entry;
the runner does NOT refuse on `digest_equal` False).

---

### F-4 — the world cache was keyed on `(mode, seed)` alone, so a freeze closure could silently invalidate its own verification. CLOSED.

**The defect.** `full_shape_4c.build_world` cached a built world under
`<cache>/<mode>_<seed>/`. Four modules decide what
`_build_world_uncached` writes — `battery_4c.py`, `collect_4c.py`,
`power_4c.py`, `tests/full_shape_4c.py`, the same set
`mutation_check.WORLD_WRITING_PATHS_4C` names — and an edit to any of
them left the cached world stale while the key stayed the same. The
mutation harness has a per-mutant workaround (it forces
`EXP4C_WORLD_CACHE=""` for those paths); an ORDINARY edit has none. The
shape that bites is this session's own: a closure edits
`battery_4c.py`, and the worlds run that is meant to verify it copies
the PRE-closure world out of the cache.

**The closure (additive).** `world_inputs_digest_4c()` over the four
modules' bytes joins the cache key
(`<cache>/<mode>_<seed>_<digest>/`), so a stale world is a cache MISS,
never a stale hit; the harness's own bypass stays as belt-and-braces
and a test asserts the two sets are the same four files. The
pre-existing 1.4 GB cache was dropped and the post-closure worlds run
built fresh.

**Tests.** `test_full_shape_4c.py`: the two sets agree; the digest moves
when a world-writing module moves; the key is not mode+seed alone.

---

### F-5 — three of S4's inputs are on the verdict path, against the analyzer's own stated contract. DISCLOSED (not edited), ratification item.

**The defect.** `analyze_4c.run()`'s docstring says "A refusal inside a
secondary degrades that secondary alone", and `_sec` implements exactly
that. But three per-trajectory steps feed ONLY the S4 continuity arm
(and S10, for the site-0-included series) — `alignment series (site 0
included)`, `eligibility (S4)`, `per-item alignment (S4)` — and each
does `failures += f`. A refusal in a descriptive arm with no α would
therefore deliver INSUFFICIENT_DATA for the whole experiment, i.e.
throw away 45 hours of model time and the primary with it.

**Why it is disclosed and not closed.** None of the three is
independently reachable: each reads exactly the units and reference
tables the primary's own `alignment_series_4c` has already read
successfully (same `tables`, same `ref_tables_by_traj[traj]`, same
pinned `pairing`/`sites`), and everything after that is pure numpy over
arrays whose shapes those loaders asserted; `excluded_sites=()` cannot
empty the site family. And the correction would NARROW a refusal, which
is not an additive closure. Recorded in `run()`'s docstring and handed
to the controller as ratification item R-3.

---

### F-6 — the design doc's discovery literals were asserted five-of-many, and the pins were checked only against themselves. CLOSED.

**The defect.** `check_discovery_pins_4c` compares `DISCOVERY_PIN_4C`
to a record computed by the same code — it cannot see a pin mistyped
relative to §2/§3.7(1), the doc it was copied from. Only `U` .6224,
`n_cells` 42, `p_family` .0391, `U_arith` .5103 and `U_nonarith` .7595
were asserted against the doc; `p_rung` .0092, `n_arith` 26,
`n_nonarith` 16 and the four per-run values .487 / .630 / .694 / .646
were not.

**The closure (additive).** `_assert_design_doc_literals_4c` in
`test_rank_4c.py`, called from the slow discovery test on the real
record, and a new FAST test that runs the same assertions against
`DISCOVERY_PIN_4C` itself (minus the two stratum counts the pin does
not carry) so the doc-vs-pin comparison is not confined to the slow
lane. The slow test passed with the additions in 106 s on Exp 4's
committed tree.

---

## B. The attack list, disposed

Each item states what was executed. "CLEARED" means attacked and found
sound; the four items that became findings say so.

1. **q's tie rule.** ½ is applied in `q_cell_4c` (`(below + 0.5*ties)/pool.size`);
   the per-cell count is printed by `gate7_ties_4c` (`tie_rule`
   "counted at one half", `gating: False`); no index can break a tie —
   the statistic contains no index at all, only `np.sum(pool < g)` and
   `np.sum(pool == g)`. CLEARED. *Residual, disclosed:* the
   arithmetic-stratum tie count `n_ties_arith` rides on the cell but is
   not printed by gate 7, which prints `n_ties` only.
2. **t⁻ off-by-one both ways.** `i = c − 1` with `MIN_CLEAR_INDEX_4C = 2`,
   so `i ≥ 1` and index 0 — where every `g` is identically 0 and every
   cell would read exactly ½ by ties — is unreachable. `c` is
   `steps.index(t_clear)` on the same grid the outcome's steps come
   from (`GRID_4C`, asserted equal to the 2h/2l manifests, and
   `check_rung_set_pins_4c` re-derives every clear index against the
   pin on `oc["steps"]`). Last grid point: 6.9b's `count_div13` has
   c = 21 = `len(GRID)−1`, t⁻ = index 20 — inside. Computed the
   realized structure from the pins: 26 cells, 6.9b 8 / 13B 18, min
   c = 4, 9 families, 17 arithmetic / 7 option / 2 string, `n_flat`
   24/15 and `n_flat_arith` 19/12. CLEARED. *Disclosed:* no real cell
   has c == 2, so that boundary is exercised by fixtures only.
3. **The flat pool's provenance.** `rung_sets` come from
   `battery_4.rung_sets_4` on the COMMITTED 2h/2l bits, never from
   anything the sweep produced, and R/flat/transient plus every clear
   index are then asserted against tag-bound literals. Transients
   (`odd_one_out`, `sub3_mid` on 6.9b; `clock24_d999` on 13B) are in
   neither side by construction — `rung_sets_4` makes the three
   disjoint and 8+24+2 = 18+15+1 = 34. CLEARED.
4. **The family-block flip.** `blocks = sorted({c["family"]})` over ALL
   cells of BOTH runs, so a family recurring on both runs is one block
   (9 blocks, 512 flips, resolution .001953). The observed
   configuration is the all-`+1` row, so `p_plus ≥ 1/512` always; the
   `1e-12` tolerance can only ADD flips to a tail, i.e. only make a p
   larger. CLEARED.
5. **The placebo.** Common pool = `sorted(set.intersection(...))` of the
   two flat pools (15 tasks; 13B's flat is a subset of 6.9b's); the
   drawn task is removed from its own comparator set; ONE draw per real
   task NAME, reused on both runs; every placebo cell carries the REAL
   cell's `family`, `rung`, `type` and `t_minus_index`, so the
   battery's family structure is identical to the real one and
   `block_flip_4c` sees 9 blocks every time. CLEARED.
6. **The modifier.** `q_arith` is computed in `cells_4c` only for an
   arithmetic rung with a non-empty arithmetic-flat pool, and
   `type_modifier_4c` takes `q_arith is not None`, so an arithmetic
   cell is ranked among ARITHMETIC flat tasks only; `nonarith["p_family"]`
   is `None` with its reason (4b process note 3) and the two
   descriptives are labelled; `licence_block_4c` reads the modifier in
   every non-refusal world and substitutes `MODIFIER_NOUN_4C`.
   CLEARED. *Disclosed:* with no arithmetic cell at all the tree falls
   through to the TYPE-BOUND/NEITHER branch, a case §3.5 does not
   define — unreachable on the pinned structure (17 arithmetic cells).
7. **Site 0.** Excluded in `alignment_series_4c` by LAYER index (not
   array position), in gate 0 via `a4._gate0_kept_positions_4` +
   `GATE0_EXCLUDED_SITES_4`, and in S8 (`excluded_sites` printed). The
   discovery gate's invariance check really does compare q's:
   `discovery_set_4c` builds `cells_incl` through Exp 4's own
   `alignment_series_4` and `cells_excl` through `alignment_series_4c`
   on the same committed bytes and pins `n_cells_q_identical == 42`,
   `max_abs_q_diff == 0.0`. Executed (cold battery item 10). CLEARED.
8. **The two gate-1 references.** 6.9b's comparator is Exp 4's
   `ladder_pythia_6.9b`; its `_load.json`, 34 `sets/*.npz`,
   `global.npz` and `align.json` are in `exp4_reference_paths_4c` (185
   files over 5 keys), bound by `require_seal_2i` in BOTH the analyzer
   and the runner and hashed again by `referents_4c.json` — so an
   edited `sets_sha256` on that record breaks the seal. 13B's
   comparator is 4c's own thin endpoint, fully pinned by
   `_load_one_unit_4c`. CLEARED, and F-3 adds the cold pre-check.
   *Disclosed, load-bearing:* 13B's gate 1 is a two-LOADER-path check,
   not a two-WRITER one — both sides come from
   `collect_4c.process_model_4c` in the same process — so it cannot see
   a collector-level defect; demonstrated under F-1.
9. **The per-unit digest.** `load_record_failures_4c` requires
   `rec["tensor_digest"] == committed_step_digest_4c(traj, step)` — the
   loader's own MEASUREMENT against the committed outcome, Exp 4 F-1's
   closure carried in by construction, not merely present-and-non-null.
   CLEARED.
10. **Coverage.** `gate1_failures_4c` requires the full 34-rung list AND
    `n_rungs == 34`; `_load_one_unit_4c` requires
    `set(sets_sha256) == set(RUNGS)`; `a4._read_sets_and_overlaps`
    asserts each table's shape is exactly `(n_sites, 500, K_4)` with
    `n_sites` pinned through `sites == metric_4.sites_4(n_hidden)` and
    `n_hidden == N_HIDDEN_PIN_4C`, and requires one `overlap_<ref>` per
    (ref, rung); `unit_complete_4` re-hashes every sets file against
    the record, so a resumed sweep cannot skip a half-written unit.
    CLEARED.
11. **The power record.** Tag-bound; byte-reproduced with FULL key-set
    equality; `cells_sha256` against the live structure, which is a
    pure function of the tag-bound pins, so it cannot change after the
    tag without the blob binding failing. The missing comparison —
    record vs REALIZED cells — is **F-2**.
12. **The discovery gate.** Pinned to full float precision and compared
    with `==`, no tolerance. The doc's 4-decimal literals: five of them
    were asserted, the rest were not — **F-6**. Exp 4's sweep units:
    `referents_4c.json` lists all 92 units × 36 files (`_load.json` +
    34 `sets/*.npz` + `align.json`) plus each trajectory's upstream
    argmax-outcome records — 8,160 files — and `check_referents_4c`
    re-hashes every one at analysis time. The reference seal does not
    cover sweep units; the manifest does. Cold battery item 9 confirms
    live == `N_FILES_4C` == committed `n_files`. CLEARED.
13. **The import surface, entry and exit.** On the analyzer: entry
    before the prereg tag, exit after every `_sec` and BEFORE the
    deciding tree (I-1's ordering, verified by reading `run()`). On the
    RUNNER: **F-1**.
14. **Every `collect_total_4c` site reachable.** The totality battery
    plus the harness's per-site totality mutants; re-run after the
    closures (§C).
15. **S4's refusal must not touch the verdict.** It does — **F-5**
    (disclosed; not independently reachable; ratification item R-3).
16. **The licence block.** The REVERSED sentence is appended whenever
    `tree["reversed"]`, the BOUNDED sentence whenever
    `calibration["bounded"]`, the modifier noun is substituted from
    `MODIFIER_NOUN_4C`, and the power quote is appended in
    NOT-REPLICATED only, read from the record (`_POWER_MISSING_4C` when
    absent). `licence_block_4c` is itself inside a `collect_total_4c`.
    CLEARED. *Residual, disclosed:* that site appends its failure AFTER
    `world` is fixed, so a licence-block refusal would print the
    INSUFFICIENT_DATA body under a non-refusal `verdict` with the
    failure listed beside it; no way to make it raise was found — it is
    string formatting over values already computed and `.get`-guarded
    throughout.
17. **The thin endpoint vs the sweep endpoint.** `expected_fields_4c`
    gives both the same `render` (`RENDER_4C["olmo2"]` = "plain"), the
    same `batch` (16), the same `refs` and the same `n_hidden` (41), so
    no render or batch delta is constructible; the pairing is
    re-derived from (n_hidden, refs) on both sides. A batch delta would
    make gate 1 fail honestly; a render delta cannot arise. CLEARED.
18. **The runner's unit order and the halt tree.** thin endpoint → gate
    1 (the endpoint) → step 0 → the grid ascending with the endpoint
    excluded, each unit skipped when `unit_complete_4`. Every tree the
    runner can leave gives INSUFFICIENT_DATA: a halt marker (read and
    named), `gate1.json` missing, `gate1.json` attesting False, an
    endpoint unit incomplete behind a present `gate1.json` (the
    analyzer's `load_run_tables_4c` raises "unit missing", collected),
    a short unit, a sha-off unit, step 0 missing, the thin endpoint
    missing, the power record missing. Executed through the totality
    battery and `MISSING_ROUTES_4C`. CLEARED.
19. **The world builder.** REPLICATES is reached for the right reason:
    `_offsets_for` puts a rising rung's task component at
    `m = c + LEAD_OFFSET_4C (−2.5)`, i.e. up BEFORE t⁻, while flat
    rungs carry only the surface schedule; the reversed world instead
    raises the FLAT pool (`REVERSED_FLAT_M_4C`), so `p_minus` comes
    from the flat pool being ahead, which is what §3.4's REVERSED
    sub-cell means. CLEARED. *Residual:* carried item 3 below.
20. **The mutation tally reproducible against the current source.**
    Re-run at the freeze — §C.

### The eight items the build carried to the freeze

1. **`FROZEN_SHA256_4C = {}` vacuous?** Sound, and now sound on every
   path. `battery_4.FROZEN_SHA256_4` covers `battery_2h.py`,
   `analyze_2h.py`, `battery_2l.py`, `checkpoints_2g.py`,
   `predictor_2g.py` and `experiments/exp2i/run/_common_2i.py`
   directly, and `check_frozen_4c` → `check_exp4_closed_4c` →
   `battery_4.check_frozen_4()` runs on the analyzer's path, the
   runner's path and cold-battery item 1. The question "do THEY call
   `check_imports_4c`?" is the one that was open: the analyzer did, the
   runner did not, the power tool and the referent builder do not need
   to (the power record is data-free from tag-bound pins and is
   byte-reproduced by the analyzer; the manifest is sha-pinned and
   re-verified by the analyzer). Executed: enumerating the runner's own
   import surface against every table showed **exactly two uncovered
   modules**, the two `__init__.py` files — **F-1**.
2. **`WORLD_WRITING_PATHS_4C` complete?** Yes. The builder's write path
   uses `full_shape_4c` itself, `battery_4c` (pins, grids, digests,
   gate-1 records), `power_4c` (the record) and `collect_4c` (by the
   same deltas); `rank_4c` and `analyze_4c` are RUN-time, not
   build-time, and `collect_4`/`metric_4`/`battery_4` are frozen. The
   set is right; the KEY was not — **F-4**.
3. **No world reaches `calibration.bounded = True` through production.**
   Still true after the freeze, and now measured rather than assumed:
   §C records α_placebo in all five world modes. The reason it is not
   synthesizable in the existing modes is structural and worth stating
   — a placebo cell is a common-pool flat task ranked among the
   remaining flat tasks of its own run, which is symmetric unless the
   9 tasks that are flat on 6.9b but NOT in the common pool grow
   differently from the 15 that are, and no world mode makes them do
   so. Handed up as ratification item R-4 with the one-mode sketch
   (depress the 9 non-common 6.9b flat tasks), since adding a world
   mode after the batteries are measured is the controller's call, and
   §3.8 requires a world for every terminal and every MODIFIER cell —
   `bounded` is a licence flag, not a modifier cell.
4. **Exp 4's frozen analyzer computes its tree before its exit import
   check** (`analyze_4.py:2322` against `:2420`). Confirmed by reading;
   4c fixed its own ordering (I-1) and the comment in `run()` says so.
   Disclosed here as a property of the CLOSED Exp 4 instrument, not
   editable — ratification item R-5.
5. **The power declaration's basis.** The committed record gives
   `P(p₊ < .01 | discovery shape, ρ = .5) = .06625` (ρ = 0: .07875) and
   `P(p₊ < .05) = .26875 / .289`, against §4's design-stage ≈ .09 and
   .32–.33; realized α .0115/.0085 at the .01 bar and .0525/.05075 at
   .05 against §4's .007–.009 and .042–.043; min-detectable uniform
   lead .7430 against §4's "about .70". The build record supersedes the
   design-stage table (§4 says it does); the doc's table should gain
   the built numbers — ratification item R-1.
6. **S5's comparator rule** was corrected from the plan's `c2 > c` to
   the design's `c2 >= c` (controller ruling); design §2's "no other
   statistic" list gains the nine discovery family sums — ratification
   item R-2.
7. **A `--only-named-test` mode for the worlds pass.** Not built: the
   freeze's own re-run did not need it. The harness already accepts
   `--only=<labels>`, and `NON_FAST_KILLS_4C` names the killing test
   per label, so the mode is a small addition whenever the worlds pass
   must be repeated; left as an efficiency item, not a finding.
8. **Deferred minors** are the FINAL review's triage. Two were checked
   here because they touch the verdict path and both are sound: the
   `a_by_ref` reduction order (a last-bit difference between
   `alignment_series_4c`'s per-reference mean and
   `_alignment_parts_4`'s, which cannot move a rank unless two `g`
   values are equal to within an ulp — gate 7 prints exactly that
   count) and `verdict_tree_4c`/`_jsonify_4`/`json.dumps(allow_nan=False)`
   outside every collect site (Exp 4's `_jsonify_4` maps NaN and ±inf
   to `None` for numpy floats, numpy arrays via `.tolist()` and plain
   Python floats, so the `allow_nan=False` write cannot raise on a
   non-finite value; `write_verdict_txt_4c` guards every block it
   prints and is total on the INSUFFICIENT_DATA shape, where `primary`,
   `placebo`, `modifier` and `calibration` are all `None`).

### Cleared under attack, beyond the list

- **npz byte determinism.** Gate 1 compares raw file bytes across two
  writers months apart. numpy 2.4.6 zeroes the zip timestamp: two
  `savez_compressed` of the same array 2.2 s apart hashed identically.
  Exp 4's ladder record stamps `numpy 2.4.6` and the venv is on 2.4.6,
  so the format has not moved under the comparison.
- **The 13B depth pairing, the one new case (15 sites against 12- and
  13-site references).** `expected_pairing_4` calls the same
  `_pairing_positions` the collector used, so the re-derivation catches
  a tampered record but is a tautology for the RULE. Checked the rule
  directly: every pairing is monotone, the maximum relative-depth error
  is .042, hidden state 40 (relative depth 1.0) pairs with each
  reference's last site, and the duplicates are exactly where 15 sites
  map into 12 or 13. CLEARED.
- **Determinism against `PYTHONHASHSEED`.** `rung_sets_4` returns
  SORTED lists, so `eligibility_4c`'s `for r in flat` (which consumes
  `rng` draws in iteration order) is deterministic; `cells_4c`,
  `window_mean_cells_4c` and `never_performing_type_check_4c` sort
  their pools explicitly; `placebo_4c`'s unsorted comprehension feeds
  only integer counts, which are order-free. CLEARED.
- **The provisional vs the deciding tree.** `calibration_read_4c` takes
  the PROVISIONAL tree's world to pick its deciding bar, and the
  deciding tree is recomputed after the exit import check. The two can
  differ only by failures appended in between, and the only such site
  is the exit check — whose failure sets the final verdict to
  INSUFFICIENT_DATA and `calibration = None`. CLEARED.

---

## C. Post-closure batteries

(filled in below)

---

## D. Pre-tag executions of `analyze_4c.run()` on the REAL tree this session

(filled in below)

---

## E. For ratification

(filled in below)
