# Experiment 6 — adversarial freeze (2026-09-28)

Freezer, cold, on `experiments/exp6/` at build HEAD `f3a9bf046` (the slow
mutation pass on the repository). The assignment (brief
`.superpowers/sdd/2026-09-27-exp6-instrument/freeze-brief-final.md`): find
THE CLASS DEFECT — a defect that silently decides or changes a verdict, a
status, a licence sentence or a sealed record with every gate passing —
demonstrate it executably, and close it additively (a new refusal, pin,
check or test; never a dial, a bar, a statistic's definition, a rung set's
rule, a stratum or a licence sentence).

Zero model contact, zero network. Every attack that needed campaign data
ran on a synthetic tree built under the session scratchpad by the REAL
runners with the fake loaders of `tests/_world_6.py`
(`w_general`: `W.spec(rho=W.general(0.6))`; `w_null`: `W.spec()`); nothing
was written under `experiments/exp6/results/`. Scripts and their verbatim
output are in the scratchpad
(`/private/tmp/claude-501/-Users-michaeljordan-emergence-paper/18e29de9-8d76-4d63-ba15-9314534cd7e1/scratchpad/freeze/`:
`an.py`, `f1_runner.py`, `f2_*.log`, `f12_before.log`, `f3_endpoint_hosts.py`,
`f4_pyc.py`, `licences.py`, `fuzz.py`, `killpoints_record.py`,
`killpoints_run.py`, `kp_all.jsonl`, `det.py`, `d_headline.py`); every
demonstration that survives the session is a committed test in
`tests/test_freeze_6.py` (11 fast, 1 slow). Interpreter
`~/emergence-lab/.venv/bin/python`, repository root, `-p no:cacheprovider`,
`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1`.

Model-cache check (`find ~/.cache/huggingface/hub -newermt '2026-09-28 20:29:08' -type f | grep -v refs/main`):
empty at the start (20:29) and at the end (§C).

## Baseline, measured cold BEFORE the freeze touched anything

| battery | result |
| --- | --- |
| fast suite (`-m "not slow"`) | **370 passed**, 233 deselected (25 s) |
| slow files (`test_worlds_6.py`, `test_totality_6.py`, detached) | **231 passed** in 3,054 s |
| cold battery | not run before the first closure (it runs the analyzer on the real tree: a disclosure event); the build's record: 10/14 PASS, 4 SKIP |
| mutation logs (committed) | fast 335 mutants: 276 killed, 59 survived-fast; slow 59 of 59 killed; none open, none equivalent |
| import scan `--check` | 67 frozen, 5 own, 16 bound: as pinned |

## Verdict on the assignment: **THE CLASS DEFECT WAS FOUND (F-2), with a stated reach.**

**F-2: a frozen module from a second `experiments` directory changed the
verdict with every pin active.** `experiments` is a namespace package. The
import-surface check (`pins_6.import_surface`) counted only files lying
under this repository's `experiments/`; the frozen-module check hashes the
repository's files on disk, not the modules that ran. A second
`experiments` directory earlier on `sys.path` merges as a namespace
portion and supplies any package it holds; its files are outside the
repository, so the surface check passed them over, and the frozen check
hashed the untouched repository copy. Demonstrated on the null world
(`w_null`, no forecast anywhere), the analyzer run with the REAL frozen,
import and referent pins (only the git tag lookups injected, since a
synthetic tree has no tags), F-1 simulated closed in-process
(`an.py`, `PATCH_F1=1`), a shadow `experiments/exp2i/` of symlinks except
`analyze_2i.py`, whose `fires_2i` returns `T > -1`:

```
== baseline (PYTHONPATH=REPO)
VERDICT BATTERY-BOUND
FAILURES []
PINS_ACTIVE {'frozen_modules': True, 'import_surface': True, 'referent_manifest': True, 'prereg_tag': False, 'seal_tags': False}
LICENSED Neither predictor reached the naming rule's bar on the field's tasks: each fired on at most one of its evaluable families. Read under the power record. Bounded
ANALYZE_2I_FROM /Users/michaeljordan/emergence-paper/experiments/exp2i/analyze_2i.py
== shadow (PYTHONPATH=shadow:REPO)
VERDICT GENERAL
FAILURES []
PINS_ACTIVE {'frozen_modules': True, 'import_surface': True, 'referent_manifest': True, 'prereg_tag': False, 'seal_tags': False}
LICENSED The order in which the field's own emergent tasks come into focus during training is forecast, at the level of single items, by the sampled outputs of one-billi
ANALYZE_2I_FROM /private/tmp/.../scratchpad/freeze/shadow/experiments/exp2i/analyze_2i.py
```

A withdrawn thesis became the GENERAL headline, no failure, every pin
active. Lineage: 2j F-1 and 4c F-1 (the import surface is a verdict
input); this is the surface's other edge — WHERE a module came from, not
only whether a file under the repository drifted.

**Reach, stated plainly.** The shadow wins only where a second
`experiments` directory precedes the repository on `sys.path`: a
`PYTHONPATH` that lists another checkout (the public repository, a
worktree) before this one while the repository is also on the path, or a
driver launched from another directory with both on the path. The
campaign's documented invocations (`cd` to the repository,
`python -m experiments.exp6...`) put the repository first, and the
analyzer inserts it at position 0 when it is absent. No such directory
exists on this Mac today (`find ~ -maxdepth 4 -type d -name experiments`:
the repository's only). So: silent and verdict-changing when reached; not
reached by the scripts as written.

**Closed** (additively, `pins_6.foreign_modules`, called first inside
`check_imports_6`, so at the analyzer's entry, exit and post-secondaries
checks and at every runner's entry and exit gate): a namespace portion of
`experiments` outside the repository refuses; any `experiments.*` module,
or any module under one of the bare names the frozen code imports by
sys.path (`BARE_TOPS_6`: `battery`, `exp1_signatures_stats`, `harness`,
`models`, `probe_starved`, `splits` — measured by the import scan, which
refuses a difference), whose file lies outside the repository refuses. The
mutation harness's private trees (exp6 copied, the siblings linked) are
read through their links (`_linked_6`), as the read sweep already did.

Also found and closed: F-1 (the import pins did not name six files the
verdict path loads lazily: every real runner would have halted at its exit
gate after its stage's work, and the analyzer refused a complete tree — a
loud failure, not a silent one), F-3 (an endpoint load resumed across hosts
completes into an unsealable tree), F-4 (bytecode that is not the hashed
source runs with every pin passing).

Nothing preregistered moved: `ALPHA`, `T_BAR`, `N_PERM`, `N_BOOT`,
`MIN_RUNGS`, `HOLDS_AT`, `WORLD_OF_6`, the licence sentences, the rung-set
rule, the floors, the strata, `TOL_PER_RUNG_6`, `D_TOLERANCE_6`, the power
machinery are byte-identical to the build's.

## A. Findings

### F-2 — a frozen module from a second `experiments` directory (THE CLASS DEFECT). CLOSED.

Demonstration: above (`f2_baseline.log`, `f2_shadow.log`). As tests, at
`f3a9bf046` (`f12_before.log`):

```
E       AssertionError: LOADED /private/var/folders/.../test_f2_a_frozen_module_from_a0/shadow/experiments/exp2i/analyze_2i.py
E         PASSED
E       AssertionError: PORTIONS 2
E         PASSED
E       AssertionError: PASSED            (a bare `battery.base` from outside the repository)
```

Closure: `pins_6.BARE_TOPS_6`, `pins_6._linked_6`, `pins_6.foreign_modules`,
the refusal at the head of `check_imports_6`; `_under_experiments` also maps
a module reached through a link's target back to its experiment (so in the
harness's trees those modules are hashed against the pins instead of being
passed over); `tools/import_scan_6.py` reports `bare_tops` and `foreign`
and `--check` refuses a difference; `verify_referents_6` item "frozen and
imported modules" checks both.

Tests: `test_f2_a_frozen_module_from_a_second_experiments_directory`,
`test_f2_a_namespace_portion_outside_the_repository`,
`test_f2_a_bare_named_module_from_outside`, `test_f2_the_repository_alone_passes`,
`test_f2_the_bare_names_are_the_ones_the_scan_measures`. Mutants (killed
by name): `f_2_a_module_loaded_from_outside_the_repository_is_accepted`,
`f_2_a_namespace_portion_outside_the_repository_is_accepted`,
`f_2_a_bare_named_module_is_not_held_to_the_repository`,
`f_2_an_experiments_module_s_file_is_not_held_to_the_repository`.

### F-1 — the import pins did not name what the verdict path loads lazily. CLOSED.

`tools/import_scan_6.py` measured the surface by IMPORTING the modules and
forcing a list of lazy calls; it did not load the battery. Loading the
battery (`battery_6.load_battery_6`, on every verdict path: the analyzer,
both seals, the power writer, every runner) reaches
`battery_2d.load_item_file` → `harness.answer_type_of`, whose relative
import fails on the bare-named `harness` and falls back to the bare
`battery` package — 2c's registry: `experiments/exp2c/battery/{base,
generators_controls, generators_rescues, generators_rungs, wordlists_2c}.py`.
And the Pythia predictor's real loader (`run_cell._assert_module_provenance`,
`_load_model`) imports exp2b's `models` by name. Six files no pin named.
Every test that ran a stage or the analyzer injected the import check off
(`frozen_check`, `imports_pinned=False`), so the check never saw a stage's
real surface; the task-3 review had left "the exhaustiveness of the lazy
import forcing" unverified.

Demonstrations at `f3a9bf046`:

```
# the analyzer on a COMPLETE synthetic tree, every real pin (an.py w_general 200)
VERDICT INSUFFICIENT_DATA
FAILURES ['6 import surface (exit): RuntimeError: unpinned module on the import surface: experiments/exp2c/battery/base.py']

# after a full analysis with the import pin off (surface_diff.py)
after a full analysis UNPINNED: ['experiments/exp2c/battery/base.py', 'experiments/exp2c/battery/generators_controls.py', 'experiments/exp2c/battery/generators_rescues.py', 'experiments/exp2c/battery/generators_rungs.py', 'experiments/exp2c/battery/wordlists_2c.py']

# the predictor stage, OLMo-2 1B, real entry and exit gates, fake loader and sampler (f1_runner.py)
RAISED: RuntimeError EXIT GATE FIRED: unpinned module on the import surface: experiments/exp2c/battery/base.py
HALT MARKERS: ['results/predictor/HALTED']
UNITS WRITTEN: 19

# the Pythia loader's import path (fresh interpreter)
UNPINNED after the predictor loader imports: ['experiments/exp2b/models.py']
```

On the campaign this is a day of Mac sampling per predictor ended by a halt
marker the seal refuses, the endpoint stage and every sweep halted at their
exit gates on the box, and the analyzer refusing the finished record. Loud,
not silent; fatal to the campaign as built.

Closure: the scan forces `battery_6.load_battery_6()` (analyzer interpreter)
and `run_cell._assert_module_provenance()` (runner interpreter); pins
re-derived WITH THE TOOL: `FROZEN_SHA256_6` 67 → 73 (the six files added;
none removed, none changed), `IMPORTED_SHA256_6` unchanged; `--check`:
`73 frozen, 5 own, 16 bound by the tag: as pinned`. The scan's subprocess
now runs offline (`HF_HUB_OFFLINE`, `TRANSFORMERS_OFFLINE`).

Tests: `test_f1_the_analyzers_lazy_path_is_pinned`,
`test_f1_the_pythia_loaders_import_path_is_pinned`,
`test_f1_the_import_scan_forces_both_lazy_paths`, and the slow
`test_f1_f2_a_complete_world_under_every_real_pin` (a complete world
analysed in a fresh process with the frozen, import and referent pins
real: a verdict, no failure, nothing loaded from a `tests/` directory).
Mutants: `f_1_2c_s_battery_registry_loaded_lazily_is_not_pinned`,
`f_1_exp2b_s_models_loaded_by_the_pythia_loader_is_not_pinned`,
`f_1_the_import_scan_does_not_load_the_battery`.

Determinism after the closure (surface 13): `w_general` analysed in two
processes with every real pin: `GENERAL []` twice, verdict JSON
byte-identical, sha256 `47cbd8a9…c046`.

### F-3 — an endpoint load resumed across hosts completes into a tree the seal refuses. CLOSED.

`endpoint_6.run_which` skips every record a killed load left and writes the
rest and the load record LAST under the resuming host. Each skipped record
names the first host, the load record the second; `unit_record_failures`
refuses the pair, so the seal refuses — after the stage "completed" and
gate 1(b) passed. Demonstration (`f3_endpoint_hosts.py`):

```
box one: box one died
records left by box one: 6
box two: the endpoint stage COMPLETED, gate 1(b) pass = True
seal: cannot seal: 6 failure(s): ["6 outcome smollm3_3b/stage1_final/modarith_add1: host_sha256 is not the host record's", ...
```

No verdict is reached over it (the refusal is correct); the cost is a stage
that reports success on a rented box and cannot be sealed. Closure: before
anything is loaded, a load whose existing records name another host
refuses ("a load is not resumed across hosts; move … aside first"). Test:
`test_f3_an_endpoint_load_is_not_resumed_across_hosts` (the same host
resumes past the check to its loader). Mutant:
`f_3_a_load_is_resumed_across_hosts`. Whether a partial load should
instead be rescored whole, as `sweep_6.run_step` does, is §D item 4.

### F-4 — bytecode that is not the hashed source runs with every pin passing. CLOSED.

The pins hash SOURCE files; the interpreter executes a module's cached
`.pyc` whenever it finds it valid — a hash-based `.pyc` marked unchecked is
never compared with the source, and a timestamp `.pyc` is accepted when the
recorded mtime and size match. Demonstration in a private tree built by the
mutation harness's own `make_tree` (`f4_pyc.py`; `records_6.counts_of`
compiled `+ 1` into an unchecked-hash `.pyc`, the source untouched):

```
source untouched, pins hash it: True
the code that RAN is the other source: SHADOW_PYC = True ; counts_of([[1,0,1]]) = [3]
check_frozen_6 and check_imports_6: PASSED
the tag binding compares the SOURCE on disk: True
```

Reach: a `.pyc` compiled from another source must be placed (or a
same-size edit made with its mtime restored); `__pycache__` is gitignored
and the campaign runs with `PYTHONDONTWRITEBYTECODE=1`, which stops writes,
not reads. Closure: `pins_6.bytecode_failures`, called by
`check_imports_6`: for every loaded module under `experiments/` whose
`.pyc` Python would accept, a hash-based `.pyc` must carry the source's own
hash and a timestamp `.pyc` must unmarshal to the code the source compiles
to (read from the module's own namespace: a transformers lazy module
imports on a missing attribute). 0.17 s over 80 modules; no false positive
on the repository's own caches. Tests:
`test_f4_bytecode_that_is_not_the_hashed_source[unchecked]`, `[timestamp]`.
Mutants: `f_4_bytecode_that_is_not_the_pinned_source_is_accepted`,
`f_4_a_hash_based_pyc_of_another_source_is_accepted`,
`f_4_a_timestamp_pyc_of_other_code_is_accepted`.

## B. The attack list

| # | surface | what was done | disposition |
|---|---|---|---|
| 1 | trees the runners can leave | Every write of a complete world build RECORDED through the real runners, both seals and the power writer (`killpoints_record.py`: 4,633 writes; each `write_json` two kill points — temp file written, rename done — each `write_draws` two — torn gzip, whole — 4,726 kill points in all, enumerated, not sampled); the tree each kill leaves materialized and handed to `analyze_6.run` (`killpoints_run.py`; the two pure re-derivations memoized on exact bytes for speed, behaviour-preserving). Result (`kp_all.jsonl`): 4,726 of 4,726 analysed; **4,725 RETURN INSUFFICIENT_DATA with a reason, none raises**; the one verdict is kill point 4,725 — the last write, the complete tree (BATTERY-BOUND at the kill harness's `n_perm = 20`, where nothing can fire). By stage: predictor 279 + 93 torn draws, predictor seal 4, endpoint 340, endpoint seal 2, power 2, sweeps 4,006. | CLEARED |
| 2 | an unfinished campaign | A family swept to step k, a family never started, a host that died after its gate, two hosts on one family (`test_a_sweep_the_box_abandoned`, re-run in the slow files), an endpoint stage short of one load (`test_an_incomplete_endpoint_stage_is_not_swept`), and every prefix of the kill-point enumeration. The endpoint stage resumed across hosts: F-3. | F-3; rest CLEARED |
| 3 | gates attested, not measured | Read every record check (`records_6`, `seal_*`, `_load_gate_read`, `gate1_failures`, `load_sweep_family`, `claim_failures`). Every count, bit, tally, digest, coverage figure, rung set, tree figure and the seals' file tables is re-derived from bytes and compared; host records hash to their own key and pass the stack pin. Not re-derivable and bound instead: a load record's measured tensor digest (held to the Mac's, gate 1(d)); the power record's simulated probabilities (declarations re-derived from them; the record bound by the endpoint seal tag and by `endpoint_sha256` on every sweep record — §D 3); `n_nonfinite_logits` (descriptive, S7). A load record's `kind` is not compared with the manifest entry's, so a checkpoint load claiming `thin-loader` skips the per-file sha comparison; identity still rests on gate 1(d)'s digest. Descriptive fields (`stack`, `git_sha`, `seconds`, `device`) are not compared. | CLEARED (notes) |
| 4 | inputs nothing pins | Read sweep on the synthetic complete tree (§C): 2,686 reads, 0 UNPINNED. Import surface: F-1 (lazy loads unpinned), F-2 (a second `experiments` directory; namespace merge), F-4 (bytecode). An `experiments/__init__.py` appearing in the repository is caught by the existing unpinned-module refusal (it has a `__file__` under experiments/). The environment: `HF_*` variables and cwd do not enter the analyzer; `sys.path` did (F-2). | F-1, F-2, F-4 |
| 5 | the three tags | `require_tag` compares `git show tag:path` with the disk; `seal_failures` compares `git hash-object` with `git rev-parse tag:path`; a missing tag, a missing path or a drifted file refuses. A file edited after the tag refuses. A seal tag cut before its stage is whole: the seal file is written only after every unit is present and re-derived, and the tag must bind the seal file itself. The item files: all seventeen in `ITEM_BLOBS_6`. The anchors' 2c item files are in the referent manifest. | CLEARED |
| 6 | rung sets, strata, degeneracy | R_f re-derived from the sealed endpoint counts and the pinned floors (`derive_rung_sets`), compared whole; a rung degenerate for one predictor is dropped from that test only (`_run_test`); the THIN guard keys to `eligible` (what the test read); the power THIN guard to `rungs_simulated`; "withdrawn" keys to `eligible == rungs_simulated`. The headline condition counts a family on which the test was NOT evaluable (`d_headline.py`: MET with `lcs` excluding zero on two evaluable families and one family read at two rungs) — §D 1. | CLEARED; §D 1 |
| 7 | statuses and worlds | `licences.py`: all 3^8 test states (not evaluable / fired / quiet per test) × 4 power scenarios = 26,244 cases through `verdict_6`, held to an independent restatement of design §1's table: 0 failures; all sixteen pairs reached; every UNDETERMINED names a shortfall. A test that fires and is not evaluable counts toward neither E nor F. | CLEARED |
| 8 | licences | Same enumeration: 32 distinct sentence shapes, each one of `_L`, the BATTERY-BOUND modifiers, the headline modifiers, the THIN / PARTIAL / UNDERPOWERED / HOLDS_ON disclosures, or a shortfall line. "withdrawn" appears iff BATTERY-BOUND and every evaluable test POWERED over the set it read: 0 violations either way. The "four outcome families" sentence beside a hold on three: carried, §D 2. The BATTERY-BOUND underpowered sentence would misname a test declared THIN that the result found evaluable; unreachable (THIN in the record means R_f minus the predictor's degenerate rungs < 3, and the test can read no more). | CLEARED; §D 2 |
| 9 | the power record | Written once (refuses if present, over a halt marker, before the rung sets); every claim but the simulated probabilities re-derived by `claim_failures` from the analyzer's own inputs; a test whose rungs were dropped declares THIN; the tree figures re-derived. | CLEARED; §D 3 |
| 10 | secondaries and sensitivities | Each `_sec` is collected, so a raising secondary is `{"failed": …}` and cannot move the verdict, which is computed before them; the import surface is checked again after them. Inputs read against design §5 one by one (S1 bits of A over R_f; S2 410m; S3 composite median strata both ways + paired difference over the jointly eligible; S4 type/class subsets of R_f; S5 x_B's rows; S6 init records, twin, pilot; S7 textures; S8 R_f ∩ R_g; S9/S10 committed tests; S11 structure strata; S12 relaxed IPA on both sides; S13 R_heuristic; sensitivities). The relaxed IPA form is total on the draw side (empty and whitespace-only draws return ""). | CLEARED |
| 11 | the criterion | `fuzz.py`: 100,080 draw-side strings over the five answer types (random unicode, whitespace, IPA marks, embedded answers) through `verify_6` and `relaxed_ipa`: 0 escapes; the answer side raises `ValueError` on answers that normalize to empty. Option-listing rungs: floors 1/n from the item files, pinned. | CLEARED |
| 12 | referents | Anchors' tolerance 15 a rung (plan delta N-1); the init referent is never in an outcome (`outcomes_6` refuses a step off the grid; neither `init` nor 13B's step 0 is on a grid); the control never in a verdict (R_f ⊆ RUNGS_6, re-derived); gate 1-P's committed streams in the referent manifest, sha pinned by a literal in the tag-bound analyzer. | CLEARED |
| 13 | determinism | Two processes, one tree, every real pin: byte-identical verdict JSON (F-1 above). | CLEARED |
| 14 | the preflight | Snapshots every file under `results/` before and after and refuses a difference; prints finiteness, identity, shape (empty count, most-common count), seconds and memory; `_score` computes bits it never prints or stores. Its own file is the only exemption from the import pin; everything it imports is pinned (F-1's closure covers its battery load). | CLEARED |
| 15 | the mutation harness | Mutants are written into a private copy of exp6 whose siblings are LINKS; frozen modules resolve their own paths and put the REAL repository (and its exp2b, exp2c) on `sys.path` (`tree_path.py`). `experiments.exp6` is imported from the tree before any of them runs, so every exp6 module still comes from the mutated copy (the fast kills of analyze_6 and pins_6 mutants confirm it); the frozen siblings come through the real paths with the same bytes. F-2's check reads those links (`_linked_6`). Every kill in the new `mutation_fast.log` names a test id that collects (§C). | CLEARED (note) |
| 16 | a test, tool or mutant that can reach a real loader or the Hub | `tests/conftest.py` offline + empty cache; the harness sets the same per run; runners fall back to real loaders only on `None` (`test_*_the_one_used`); `tools/import_scan_6.py`'s subprocess had NO offline variables (imports only, no loader call) — hardened; the read sweep and the cold battery call no loader. `test_f1_the_pythia_loaders_import_path_is_pinned` imports exp2b's `models` (torch, transformers) and builds nothing. Model-cache check empty before and after. | CLEARED (hardened) |
| 17 | the box scripts | No credential is placed on a rented host (bundle in, rsync pull out by the Mac); `rebundle_box_6.sh` refuses a missing tag and a sweep stage whose projection is not an ancestor; the campaign scripts stop at the first non-zero exit; a stage whose precondition is missing is refused by its runner (predictor seal, endpoint seal) before any load. The bundle is `git bundle --all`: the whole private repository's history on a third-party host — not a credential, §D 6. Five scripts under `set -uo pipefail` without `-e`: the two campaigns check each command explicitly; the watcher, puller and status loop are meant to survive a failed cycle. | CLEARED; §D 6 |
| 18 | carried: `frozen_check` switches off the import check | No production path passes it (every `main` calls with no injection; grep). What it hid: F-1. | CLEARED; F-1 |
| 19 | carried: the Pythia twin by revision | Read by S6 only (and by the seal's completeness: `n_units`, the file table). | CLEARED |
| 20 | carried: halt markers in three shapes | Nothing parses a marker; existence decides (`halt_markers`, `refuse_if_halted`). | CLEARED |
| 21 | carried: mutant density | Added: `holds_on`'s `unread` (killed), two on `make_referents_6.check_referents` (killed), and the fourteen of F-1..F-4. Judged not worth a mutant: `battery/gen_ascii.py`, `gen_shapes.py`, `words_6.py`, `audit_bbkeys_6.py` (frozen battery; a generator change changes item bytes, which the tag and `ITEM_BLOBS_6` bind); `tools/read_sweep_6.py`, `verify_referents_6.py`, `tools/guessers_lab_6.py` (report, decide no verdict). | CLEARED |
| 22 | own: the permutation count | `run()` takes `n_perm`/`n_boot`; a verdict at `n_perm = 50` cannot fire (p ≥ 1/51) and reads BATTERY-BOUND with every pin active. The count is printed in the verdict and the campaign's `__main__` uses the frozen defaults. | §D 5 |
| 23 | own: a leftover temp file | A kill between a temp write and its rename leaves `<name>.<pid>.tmp`; the analyzer's globs (`gate1_*.json`, `hosts/*.json`) and the predictor seal's file table pass it over; covered by the kill-point enumeration. | CLEARED |

## C. Batteries after the closures

| battery | result |
| --- | --- |
| fast suite (`-m "not slow"`) | **381 passed**, 234 deselected (370 + 11 of `test_freeze_6.py`) |
| slow files (`test_worlds_6.py`, `test_totality_6.py`, `test_freeze_6.py -m slow`, detached) | **232 passed**, 11 deselected in 2,925 s (231 + `test_f1_f2_a_complete_world_under_every_real_pin`) |
| cold battery (`verify_referents_6`, real tree) | **10/14 PASS, 0 FAIL, 4 SKIP** (preregistration tag, predictor stage, endpoint stage, sweeps: no tag, no campaign); "frozen and imported modules: 73 frozen and 5 own modules as pinned; no torch" (now also bare names and foreign modules); "read sweep: 314 reads, 0 unpinned". The battery exits 0 with SKIPs present: pre-campaign by design |
| import scan `--check` | **73 frozen, 5 own, 16 bound by the tag: as pinned** (re-derived by the tool; +6 frozen, F-1) |
| referent manifest | unchanged, 219 files, sha `09286d10…` (no referent file touched) |
| read sweep on the synthetic complete tree (`w_general`, tag lookups injected) | **2,686 reads, 0 UNPINNED**, 0 outside unexplained; classes a 33 / b 73 / c 219 / d 186 / e 172 / f 2,000 / g 3 |
| determinism (two processes, `w_general`, every real pin) | byte-identical, sha256 `47cbd8a9…c046`, verdict GENERAL, failures [] |
| kill points (surface 1) | 4,726 enumerated; 4,725 INSUFFICIENT_DATA, 0 raised, 1 verdict (the complete tree) |
| fast mutation pass (`--jobs 8`, committed `mutation_fast.log`) | **349 mutants in 852 s: killed 290, survived-fast 59**; no ERROR. The 59 survivors are exactly the 59 of the build's fast pass (same slugs), each killed by the build's slow pass at `f3a9bf046`; the 14 new mutants are all killed in the fast pass. Every killing test id in the log matches a collected test (four parametrized ids are recorded truncated at their first space by the harness's parser; each is a prefix of a collected id) |
| mutants left alive for the coordinator's slow pass | the same 59 as `mutation_slow.log` at `f3a9bf046` (no new survivor): the slow pass is to confirm them against the closures |
| model-cache check (end) | empty (no line) |

## D. Items stated for the ruling

1. **The headline condition counts a family on which the test was not
   evaluable.** `headline_condition` counts a rung's interval on every
   family where the test's `per_rung` holds it, and a test read at one or
   two rungs still carries per-rung intervals. Design §6: "a rung whose
   per-rung interval excludes zero on at least three families for a holding
   predictor". The naming rule counts only evaluable families. Demonstrated
   (`d_headline.py`): `PYTHIA-ONLY`, A holds on its three evaluable families,
   `lcs` excludes zero on two of them and on the fourth family (read at two
   rungs, not evaluable) → "Headline condition MET". Changing it changes a
   licence rule: not closed. Recommendation: count evaluable families only.
2. **"On four outcome families" beside a hold on three** (carried, N-15
   iii). The instrument prints the design's sentence and the disclosure.
   The sentence is Michael's.
3. **The power record's simulated probabilities are attested, not
   re-derived.** The declarations are re-derived from them and the record
   is bound twice (the endpoint seal tag; `endpoint_sha256` on every sweep
   record, so it cannot change after the sweeps without every sweep record
   refusing). Re-deriving one test through `power_2i._one_test_power`
   (deterministic seeds) in the cold battery would measure it; the record
   is written once, before the sweeps, on the Mac.
4. **F-3's closure is a refusal.** Alternative: rescore a partial load
   whole, as `sweep_6.run_step` rewrites a partial step. The refusal leaves
   a manual move-aside on a rented box.
5. **The permutation count is an argument of `run()`.** A write at
   `n_perm` other than `N_PERM` could refuse, or `pins_active` could record
   it; today the count is printed and nothing checks it.
6. **The bundle carries the whole private repository** (every branch and
   tag, the essay drafts, the outreach notes) to a rented host. Not a
   credential; a filtered bundle is possible.
7. **F-2's reach.** Closed for every path; the environment that reaches it
   is an operator's `PYTHONPATH`. The campaign could also assert at launch
   that `sys.path[0]` is the repository (a process note).
8. **The commit message of the closures says "17 mutants added"; the
   number is 14** (335 → 349). The history is not rewritten.

## E. Disclosure tally (pre-tag executions of `analyze_6.run()` on the REAL tree)

**1** by this freeze: the cold battery's read-sweep item on the real tree
(`verify_referents_6`, after the closures). The tree holds no campaign
record, so the run refuses at the predictor seal; the tool prints no
verdict and no statistic (`314 reads, 0 unpinned`). No other call of
`analyze_6.run()` touched the real tree: the fast suite's calls run on
`tmp_path`, the world and totality files on `tmp_path`, every demonstration
on the scratchpad's synthetic trees. The build's own cold-battery runs (its
records say 10/14 PASS, 4 SKIP) also executed the read sweep on the real
tree and are not tallied in the ledger; they are not counted here.

Every other analyzer execution of this freeze ran on a synthetic tree under
the scratchpad or a pytest `tmp_path`.

## F. Slips for ratification (the design doc is NOT edited here)

- **§3.6, after "`IMPORTED_SHA256_6` over the resolved module table at
  entry and exit, in the analyzer AND in every runner (4c F-1);"** insert:
  "the table is measured by RUNNING the verdict path's lazy imports (the
  battery load, the Pythia loader's module provenance), not by importing
  alone (freeze F-1); a module that answers to this repository's names —
  a namespace portion of `experiments`, an `experiments.*` module, or one
  of the bare names the frozen code imports by `sys.path` — and was loaded
  from outside the repository refuses (freeze F-2); and the bytecode that
  ran must be the source that was hashed (freeze F-4);"
- **§3.4, after "Gate 1-O, per family, first in that family's sweep:"
  block, add a sentence:** "An endpoint-stage load is resumed only on the
  host that began it; a partial load another host began is refused before
  anything is loaded (freeze F-3)."
- **§6 GENERAL, the headline condition, if §D 1 is ruled as recommended:**
  replace "on at least three families for a holding predictor" with "on at
  least three of that predictor's evaluable families".
