# Experiment 5b — adversarial freeze (Task 7 step 1, 2026-09-26)

Fresh-eyes freezer, cold, on `experiments/exp5b/` at build HEAD
`d18434c37` (Task 6 fix round 1). The standing assignment: find THE
CLASS DEFECT — the defect that would silently DECIDE the verdict with
every gate passing — and close it additively (a new refusal, pin, check
or test; never a dial, a bar, a statistic's definition or a licence).
The design's §11 named four surfaces (i)–(iv); the Task 7 brief extended
them to (x) and carried C-1..C-4 from the build's reviews.

Zero model contact, zero network. Every attack that needed campaign data
ran on a synthetic `full_shape_5b.write_world_5b` tree in a pytest
`tmp_path` (the production runner `run/units_5b.run` driven by
`experiments/exp5/tests/fakes_5`); gate 2's tamper demonstrations ran on
a byte COPY of `experiments/exp5/` under the session scratchpad
(`/private/tmp/claude-501/…/scratchpad/freeze/exp5copy`), never on the
real tree. Scripts and their verbatim output are in that scratchpad
(`real_run.py`, `gate2_demo.py`, `imports_demo.py`,
`demo_tests/test_f1_before.py`, `*.log`); every demonstration that
survives the session is a committed test in
`tests/test_freeze_5b.py` (slow, 11 cases). Interpreter
`~/emergence-lab/.venv/bin/python`, repo root, `-p no:cacheprovider`;
slow files and the mutation harness ran detached, the harness alone.

## Baseline, measured cold BEFORE the freeze touched anything

| battery | result |
| --- | --- |
| cold referent battery (`verify_referents_5b`, real tree) | **9/12** + 3 pre-campaign SKIPs (9 power record, 10 gate 1, 12 units); item 5 = Experiment 5's own battery in-process, **13/13** (its items 11 and 13 live); 64 frozen + 5 imported pins verified |
| fast suite (`-m "not slow"`) | 78 passed (the build's record; re-run after the closures, §C) |
| slow suite | not re-run cold; the build's record: worlds 13/13, totality 5 passed, determinism 1 |
| mutation logs | 75 considered, 66 fast + 9 slow kills, 0 equivalent, 0 open |
| Experiment 5's tree | snapshot of all 6,686 files (sha256) taken before any tool ran |
| pre-tag analyzer executions (PROGRESS.md) | **3** |

## Verdict on the assignment: **THE CLASS DEFECT WAS FOUND.**

**F-1: an unfinished campaign delivered a verdict.** The analyzer read a
unit the campaign never wrote as an ABSENT member ("not loaded"), a side
the campaign never reached as EXCLUDED, and a tree with the host record
but no unit as UNDETERMINED — each with zero failures. The runner writes
every one of the 24 units (a non-finite member is written whole and
marked by Experiment 5's writer; a non-finite final halts the size with a
marker), so neither the design's ABSENT rule nor its exclusion rule can
be reached by a finished campaign: the only trees that reached them were
killed ones. `run/campaign_5b.sh` stops at the first size that exits
non-zero and sizes run largest first, so a crash while loading the 1.4b
final (an OOM, a Hub error) leaves 6.9b and 2.8b complete, every smaller
side absent, and a `gate1_5b.json` the runner rewrote after 2.8b that
covers exactly those two sides. On such a tree the analyzer at
`d18434c37` delivered, e.g. (synthetic world, three sides):

```
F1-BEFORE control: SURVIVES CALIBRATED T_sym=0.09010171020479951 n=135 p=0.004975…
F1-BEFORE (a) 1b/29000 never written: SURVIVES CALIBRATED T_sym=0.09018813436694453 n=135 … "members_absent": {"1b": {"29000": "not loaded"}}
F1-BEFORE (b') sides 1.4b and 1b never started (campaign stopped after 2.8b): SURVIVES CALIBRATED T_sym=0.07217172432480602 n=32 … "excluded": ["1.4b", "1b"], "cells_dropped": 103
F1-BEFORE (c) killed after the host record, no unit (attestation regenerated empty): UNDETERMINED None T_sym=None n=0
F1-BEFORE (b') failures at HEAD with F-1 patched out: []
```

A verdict over 32 of 135 cells from one side, every gate passing; which
sizes finished decided the reading. On the real record the 2.8b row
carries Experiment 5's excess (retrospective: .117 of T), so a campaign
stopped after 2.8b would have read that row alone. Lineage: 2d F-1 (the
analyzer must deliver its own refusal from the tree the runner leaves)
and 2h F-2 (coverage attested, not measured); the Task 5 reviewer's C-1
was this defect's gate-1 face.

**Closed** (additively): `analyze_5b.window_completeness_failures_5b`
and a new `run()` site `"5b window completeness"` — every small side
must have all four `unit_steps_5b()` units on disk as 5b-complete units,
and nothing but the six small sides may sit under `results/units/`. The
ABSENT rule (measured non-finite member) and the statistic are
unchanged. Plan delta B-4's absent-directory clause is superseded — §D
item 1, for the ruling.

Nothing preregistered moved: `T_BAR_5B`, `ALPHA_5B`, the floors, the
window, `PLACEBO_SIGN_5B`, `SIGMA_GRID_5B`, `ALPHA_CAL_5B`,
`LOSS_TOL_5B`, the six-term M, the tree, the licence bodies and
`power_5b.py` are byte-identical to the build's.

---

## A. Findings

### F-1 — an unfinished campaign delivered a verdict (THE CLASS DEFECT). CLOSED.

**Demonstration (before):** `demo_tests/test_f1_before.py` (scratchpad)
— a SURVIVES world; the closure's one site patched to `[]` reproduces
`d18434c37` exactly; each variant regenerates `gate1_5b.json` the way
the runner does after a completed size (`collect_5b.gate1_record_5b`).
Output quoted above. The committed `tests/test_freeze_5b.py::test_f1_…`
failed on the pre-closure source with `('SURVIVES', {'verdict':
'SURVIVES', 'cell': 'CALIBRATED', … 'members_absent': {'1b': {'29000':
'not loaded'}}})` (`freeze_prefix.log`).

**Closure:** `window_completeness_failures_5b(root)` + the
`"5b window completeness"` site in `run()`; the cold battery's item 10
applies the same function post-campaign. Shapes 7/8 of
`test_totality_5b.py` and `test_full_shape_5b.py::test_side_absent_or_
memberless_refuses` (renamed from `…_is_excluded_not_refused`) now
assert the refusal; `test_site_template_count_is_24` →
`…_is_25`.

**Test:** `test_freeze_5b.py::test_f1_an_incomplete_campaign_never_
delivers_a_verdict` — (a) a member never written, (b) a side never
started, (c) no unit at all, (d) a `12b` directory under `units/` —
each INSUFFICIENT_DATA at `"5b window completeness"`, the clean control
SURVIVES · CALIBRATED before and after. Fast:
`test_analyze_5b.py::test_window_completeness_site_raises_without_the_
wrapper` and `::test_window_completeness_failures_5b_measures_the_tree`.

### F-2 — gate-1 coverage was attested only (carried item C-1). CLOSED.

`gate1_rederive_5b` skipped a re-read step missing from a side, and
`_gate1` compared only the attestation's `pass` flag. **Before:** a
`gate1_5b.json` with the 1b keys removed (10 of 12, `pass` true) →
SURVIVES · CALIBRATED (`freeze_prefix.log`, `test_c1_…` failed).
**Closure:** a missing re-read step is a failure (`"gate 1 <size>/
step<n>: the re-read unit is not on disk"`), and the attestation's
`per_unit` key set must equal the re-derived set. An expected-count
check was drafted and removed: with the missing-step failure it is
redundant (an equivalent mutant by construction). **Tests:**
`test_freeze_5b.py::test_c1_gate1_coverage_is_measured`; totality shape
8b; fast: the extra assertion in `test_collect_5b.py::test_gate1_
rederive_5b_catches_a_runner_attestation_mismatch`.

### F-3 — the calibration read accepted a non-increasing σ̂ axis. CLOSED.

`calibration_read_5b` interpolates with `numpy.interp`, which returns a
number for any `xp` — a non-increasing `sigma_hat_axis` silently reads
garbage for the sub-cell and T\*. Unreachable through `compute_5b` in
practice (σ̂ rises with σ_s) but nothing checked it, and the record is
written once and then bound. **Before:** axis entries 2 and 3 swapped,
`power_gate="skip"` → SURVIVES · CALIBRATED (`test_f3_…` failed).
**Closure:** `power_failures_5b` refuses an axis that is not strictly
increasing (a structural check, before the recompute). **Tests:**
`test_freeze_5b.py::test_f3_…`; fast `test_analyze_5b.py::test_power_
failures_5b_refuses_a_non_increasing_sigma_hat_axis`. The existing fast
fixture `test_power_failures_5b_catches_a_non_reproducing_record` used a
flat axis `[1]*6`; it now uses `[1..6]` so it still reaches the
byte-for-byte comparison it tests.

### F-4 — the design's exclusion rule is unreachable (carried item C-2 and surface (x)). DISCLOSED; slips.

Three facts, each executable:

1. A non-finite `step142000` (the re-read member) refuses at gate 1 — its
   NaN loss is not within 1e-4 of Experiment 5's finite committed loss
   (`test_c2_…`: `"gate 1 1b/step31000 …"`). It is never ABSENT. Kept as
   built (an identity failure on the same bytes); slip S-2.
2. A non-finite final halts the size: Experiment 5's writer halts on
   `why in HALT_ON_NONFINITE_WHY_5 = ("spine", "bisect", "final")` and
   5b passes `why="final"` → HALTED marker → INSUFFICIENT_DATA at
   `"5b halt marker"` (`test_a_nonfinite_final_halts_the_size_and_
   refuses`). The design's "a side's final non-finite excludes the side"
   is unreachable; slip S-3.
3. Hence a side with three non-finite members also refuses (gate 1, on
   142000) — surface (x)'s "EXCLUDED, not refused" cannot occur
   (`test_c2_…`, second world). With F-1, NO exclusion is reachable from
   a finished campaign; `sides.excluded` is always `[]` on a
   verdict-bearing tree, and UNDETERMINED is unreachable on Experiment
   5's 63 cells / 13 rungs (every cell keeps ≥ 1 term). The ABSENT rule
   stays live for 141000/140000 (third world: both non-finite on 1.4b →
   `members_absent == {"1.4b": {"30000": "non-finite loss", "29000":
   "non-finite loss"}}`, no failure).

### F-5 — cheap real minors (carried item C-4). CLOSED.

- `unit5b_record_failures_5b` now cross-checks `why` against `step`
  ("final" iff 143000); fast assertions in `test_unit5b_record_contract`.
- `import subprocess` removed from `analyze_5b.py` (unused, on the pinned
  surface).
- `cell_5b` computes `placebo_terms_5b` once for M and `n_terms` (was
  twice); the one mutant targeting that line re-anchored.
- the cold battery's `_c10` no longer swallows a side's load failure
  (post-campaign it raised nothing and excluded the side): any load
  error, and any F-1 window gap, fails item 10.
- `test_main_reports_ok_skip_and_tallies` was vacuous (`rc in (0, 1)`)
  and ran the whole real cold battery (~3 min) inside every fast pass;
  it now drives `main()` on a stand-in check table (ok + SKIP → 1/2 at
  rc 0; a raising check → FAIL, rc 1, stops).
- the mutation harness's `main()` returned 0 when a mutant's target text
  was not found (a SKIP) — it now fails the run.

### F-6 — the harness's fast-behavioural stage ran without `-m "not slow"` (carried item C-3). CLOSED.

`mutation_check.py`'s `run_worlds_only` passed `extra=[]` to the
fast-behavioural stage, so `test_require_exp5_closed_against_real_git`
(slow) rode along in every totality pre-check. Now `FAST_EXTRA_ARGS`.

---

## B. The attack list

**(i) The primary uncomputable before the campaign.** `real_run.py`
(execution #4 on the real tree, 82.9 s):

```
verdict INSUFFICIENT_DATA None ; n_failures 11
  5b prereg tag: RuntimeError: preregistration tag exp5b-preregistered does not exist
  5b host record: ValueError: host record missing
  5b units 160m … 6.9b: ValueError: manifest, slice, battery, verify criterion or host record missing   (×6)
  5b gate 1: … results/gate1_5b.json (the runner's attestation) missing
  5b power record: ValueError: power_5b.json missing
  5b projection: … experiments/exp5b/projection.md was never added
primary None cells [] secondaries {} calibration None
gate2 {"exp5_verdict": "NOT-MATCHED", "exp5_T": 0.05349206349206348, "exp5_verdict_equal": true, "n_cells5_live": 63}
exp5_pins_active {… "import_surface": false, …}  (every other Experiment 5 pin true)
```

After the closures the same tree adds `"5b window completeness"` (the
read sweep's run, execution #6). The ORDER argument: cells come only from
`counts_by_side`, which comes only from `load_side_5b(root=<5b root>)`;
`cells_5b` drops a cell whose side lacks a final; the block that builds
cells runs only under `if not failures`; the only reader of Experiment
5's committed 142000 counts is `s8_one_member_5b`, inside
`secondaries_5b`, called only under `if not failures` and fed the 5b
cells (`grep -n "S11\|exp5_root" analyze_5b.py stats_5b.py`);
`reread_compare_5b` reads Experiment 5's 142000 files but emits only the
drift table (gate 1 / S11). The mutant "S1–S12 computed regardless of
failures" is killed (totality). **CLEARED.** Answer to the plan's known
gap: with `imports_pinned=False` the ONLY inactive Experiment 5 pin is
`import_surface` (superseded by `check_imports_5b`, B-10).

**(ii) Nothing under Experiment 5's tree.** 6,686-file sha256 snapshot
before any tool; after the first real run, the cold battery, the runner
dry-run, the gate-2 demos (copy only), the import demo, the import scan
and the read sweep: `diff` empty, `git status --short experiments/exp5`
empty. `units_5b --size 1b --dry-run` on the real tree refuses at
`RuntimeError: preregistration tag exp5b-preregistered does not exist`
before touching anything (it cannot run pre-tag). Experiment 5's own
cold battery (item 5 of 5b's) 13/13, before and after. Re-checked after the last change (§C). **CLEARED.**

**(iii) Gate 2's exactness** (`gate2_demo.py` on the copy; the 5b root
an empty scratch directory; `exp5_kwargs={"blobs_bound": …}` because
Experiment 5's targets seal binds REPO paths and the copy lives outside
the repo — disclosed):

```
== control (unmodified copy): … gate2_equal True
== (a) rung record 2.8b/step143000/sub3_mid correct+1: … 5b exp5: ValueError: exp5: 5 finals: … the final (step143000) is not among the complete units …
== (b) verdict.json one digit of T: 5b exp5-closed: … verdict.json hashes to ea37ed7f23d7, pinned 50a6f57e8e4b
                                    5b exp5: … differs from the committed one at key 'primary'
== (c) experiments/exp5/stats_5.py blob sha differs at the tag: 5b exp5-closed: … tag exp5-closed does not bind experiments/exp5/stats_5.py
== (d) verdict.json cells[0].R + 1, verdict sha pin moved to the doctored file: 5b exp5: … differs from the committed one at key 'cells'
```

Every variant INSUFFICIENT_DATA; the copy restored byte-identically.
**CLEARED.**

**(iv) The σ̂ bracketing rule in the licence block.**
`test_freeze_5b.py::test_iv_off_grid_is_not_claimed`: a doctored record
whose simulated axis tops at 0.99 × the observed σ̂ (α axis .001, so
CALIBRATED would be read if the rule were prose) → SURVIVES · OFF-GRID,
`claimed: false`, "NOT claimed" in the sentence, `in_grid: false`.
**CLEARED.** Disclosed (D item 3): `claimed` is also false for INFLATED.

**(v) The re-read comparison at the boundary.** `test_v_…[kw0]`: digest
equal, antonym +16 → the runner records `count_abs_diff_max == 16` and a
tolerance failure; the analyzer refuses naming antonym. `[kw1]`: counts
equal, loss +2e-4 → `loss_within_tol false`, refuses at `|Δℓ|`.
**CLEARED.**

**(vi) The attestation.** `test_vi_…`: 1b's two re-read units with a
different digest, runner not halting; the `_unit_5b.json` records and
`gate1_5b.json` doctored to `digest_equal: true`/`pass: true` → refuses
with "the runner's attested digest_equal True != re-derived False".
(First attempt used a non-hex fake digest and was stopped earlier by
Experiment 5's gate 3 — `"_checkpoint: tensor digest missing"`; the
fixture was corrected to a sha256-shaped digest.) **CLEARED.**

**(vii) The power record.** `test_vii_…`: a record genuinely recomputed
by `compute_5b` at `N_SIM_5B − 1` (the worlds' `N_SIM_5B` is 30, so 29
is the analogue of 999), and one built from 62 of 63 cells (its own
`structure_sha256`) → both refuse at `"5b power record"`; the committed
record restored → clean. **CLEARED.**

**(viii) The import surface.** `imports_demo.py`: two lines appended to
`experiments/exp5b/run/__init__.py`, each surface in a fresh process:
runner → `REFUSED: imported module drifted from its pin: (pin) ->
…/exp5b/run/__init__.py`; `power_5b.main` → the same; the analyzer
(empty scratch roots) → INSUFFICIENT_DATA at `"5b import surface
(entry)"` and `"(exit)"`; file restored (`restored: True`, `git status`
clean). **CLEARED.**

**(ix) The sign-flip null under the matched form.** `test_ix_…`: wobble
0 (every member equals the final; the re-read member mirrors the final
in the world) → for every cell `members == f_B == f`;
`|T_sym − mean((R − P/√2)/500)| < 1e-12` against the hand computation
from the world's Experiment 5 cells, and the rung-block p equals
`stats_5.sign_flip_p_5` on the hand-built per-rung sums. **CLEARED.**

**(x) The exclusion rule (B-4).** A side with its final and three
non-finite members refuses at gate 1 (the 142000 member) — never
EXCLUDED. **F-4 (disclosed).**

**C-1** → F-2 CLOSED. **C-2** → F-4 (kept as a refusal; slip S-2; test
pins it). **C-3** → F-6 CLOSED. **C-4** → F-5 CLOSED for the six named;
the cosmetic rest, one line each:

- `collect_total_5b` catches KeyError/ImportError — Experiment 5's own
  list; left (widening, harmless).
- S4 recomputes the primary; S4/S10 duplicate the clamp-and-interpolate —
  descriptive only; left.
- unused `_THR`/`_g` in `full_shape_5b.py` — test helper; left.
- a test comment says "torn" where the fixture removes the final's
  directory; the weak `refuses("1b")` needle; the blind
  `.replace("30000", "12000")` — test-only wording; left.
- the world test asserts the secondaries' keys, not
  `secondary_failures == {}` — left; the verdict path does not read them.
- `{**pe, "n_cells": pe["n_cells"]}` re-sets a present key (power) — a
  no-op; left (power_5b is tag-bound and untouched by this freeze).
- the unused `bg` import in `test_collect_5b.py`; the bare
  FileNotFoundError path message from `exp5_unit_record_5b`; the private
  `_write` per module — left (safe; codebase convention).
- σ̂ exactly at the bottom knot untested; `sigma_hat_5b` per-side with
  one side — left (both the analyzer's `below_grid` strict `<` and the
  per-side grouping are exercised by the worlds with three sides).
- stale docstring text (34 vs 200 identities; the worlds-only docstring;
  the read sweep's refusal point, pre-campaign "5b prereg tag") and the
  read sweep printing only `failures[0]` — left.
- 8 of the 24 sites' fast kills are collateral through
  `_isolated_kwargs` — disclosed by the build; unchanged.

**Further surfaces read and cleared:** the cell set (gate 2's whole-dict
equality fixes the 63 cells and their R/P); the power gate's recompute
(n_sim/seed measured, structure from the re-derived cells);
`load_side_5b`'s torn/extra/attestation checks (totality shapes 2–6);
the projection's two ancestries (shape 14); S8 behind the units gate;
the non-finite member's counts never read (`counts` built from the final
+ finite members only; S12 and S2 read the same table).

## C. Batteries after the closures

| battery | result |
| --- | --- |
| fast suite (`-m "not slow"`) | **81 passed**, 31 deselected (78 + the F-3 fast test + two F-1 fast tests; the vacuous main() test rewritten); identical under `-W error` |
| `test_freeze_5b.py` (new, slow) | **11 passed** (30:55); on the pre-closure source 7 passed / 4 failed (F-1, C-1, (vi) before its fixture fix, F-3) — `freeze_prefix.log` |
| `test_totality_5b.py` | **5 passed** (27:55) — shapes 7/8 now refusals, shape 8b added, site count 25 |
| `test_full_shape_5b.py` | **13 passed** (33:32) |
| `test_determinism_5b.py` | **1 passed** (2:59) |
| mutation harness | **84 considered: 74 fast-killed, 10 slow-killed, 0 equivalent, 0 unresolved, 0 SKIP, 0 TIMEOUT** (`mutation_build.log`); `--worlds-only` **10/10 killed**, 0 structural-only, 0 open (`mutation_worlds.log`) — the 75 of the build + 8 freeze mutants + the new site's totality mutant; `freeze_c_1_the_attestation_s_key_set_comparison_dropped` survives fast and is killed by totality shape 8b (entered in `NON_FAST_KILLS_5B` after the worlds-only run confirmed it) |
| read sweep (real tree, execution #6) | 8,467 distinct paths; referents 8,395 / pinned modules 61 / instrument blobs 6 / sha-pinned at load 5 / **UNPINNED 0**; writes 0 |
| import scan (real tree, execution #5) | 64 frozen + 5 residual; the printed tables equal the pins (69/69); `FROZEN_SHA256_5B` unchanged; `IMPORTED_SHA256_5B` re-pinned for `verify_referents_5b.py` only |
| `REFERENTS_5B_SHA256` | unchanged (the manifest covers Experiment 5's files only; no referent moved) |
| cold battery (after the last change) | **9/12** + the same 3 pre-campaign SKIPs; item 5 (Experiment 5's own) 13/13 |
| Experiment 5's tree | 6,686-file sha256 snapshot **identical** after every tool; `git status --short experiments/exp5` empty |

## D. Items stated for the ruling

1. **Plan delta B-4 superseded by F-1.** B-4 read the design's gate 4
   literally ("… or is excluded and counted") and made an absent side
   directory an exclusion. F-1 makes it a refusal. Recommendation: ratify
   F-1; B-4 keeps only its measured half (a side whose members are all
   non-finite), which F-4 shows is unreachable. If the ruling keeps
   B-4 as written, revert the F-1 commit.
2. **C-2 kept as a refusal.** Recommendation: keep; slip S-2 writes it
   into §3.2.
3. **`licence.claimed` is false for INFLATED.** Dial (h) says "claimed in
   full below .05", and §6's INFLATED licence is "as above" plus the α
   sentence — i.e. claimed, with a caveat. The block's `claimed` boolean
   reads only CALIBRATED as claimed. The sentence (the governing text) is
   right in every cell; only the flag under-states INFLATED.
   Recommendation: leave the flag (it errs toward not claiming) and add
   one line to §6: "the analyzer's `claimed` flag is true for
   CALIBRATED only; INFLATED's licence is its sentence". Not changed here
   (a licence field).
4. **OFF-GRID's threshold is the simulated axis's top, not the nominal
   45.** §3.4/§3.7 say "σ̂_s above 45"; the analyzer compares to
   `sigma_hat_axis[-1]` (the estimator's mean at σ_s = 45, drift and
   clipping included) — consistent with §3.4's own "the lookup is on the
   quantity the analyzer measures". Slip S-5.
5. **The power record's runtime** is ≈ 11–12 min (Task 3's timing), not
   the plan's 3–6; run detached.

## E. Disclosure tally (pre-tag executions of `analyze_5b.run()`)

On the REAL tree (root = `experiments/exp5b`, exp5_root = the real
`experiments/exp5`): **3 before this session → 6 after it**:

| # | what | printed |
| --- | --- | --- |
| 4 | `real_run.py` (surface (i)), pre-closure | INSUFFICIENT_DATA, 11 refusals (quoted in B(i)); gate 2 equal; no 5b statistic |
| 5 | `tests/import_scan_5b.py` after the re-pin | INSUFFICIENT_DATA at "5b prereg tag"; tables == pins (69/69) |
| 6 | `tests/read_sweep_5b.py` | INSUFFICIENT_DATA — first failure "5b prereg tag: … power_5b.json not on disk"; 8,467 paths, 0 UNPINNED |

Not on the real 5b tree, disclosed beside: **10** executions with
`exp5_root` = a byte copy of Experiment 5's tree and `root` = an empty
scratch directory (`gate2_demo.py`, two passes × five variants — the
first pass refused at Experiment 5's targets seal because the copy is
outside the repo); **1** with both roots empty scratch directories
(`imports_demo.py`). None can compute a 5b statistic (no 5b byte
exists in any of them).

## F. Slips for ratification (the design doc is NOT edited here)

- **S-1 (F-1), §3.6 gate 4.** "Every small side has its final and at
  least one member present as units, or is excluded and counted; nothing
  else was loaded (the unit list re-derived from `SMALL_SIDES_5 ×
  ({143000} ∪ W_s)`, not read from a log)." → "Every small side has all
  four units on disk as complete 5b units — the runner writes every unit
  (a non-finite member written whole and marked; a non-finite final
  halts the size) — so a unit or side not on disk is an unfinished
  campaign and refuses (freeze F-1); nothing else was loaded: no
  directory under `results/units/` but the six small sides and no step
  outside the unit list (re-derived from `SMALL_SIDES_5 × ({143000} ∪
  W_s)`, not read from a log)."
- **S-1b (F-1), §3.6 closing paragraph.** "Every tree the runner can
  leave — a side halted at its first unit, a side with two of three
  members, a torn unit — reaches INSUFFICIENT_DATA or the exclusion rule
  from the production path, demonstrated at the freeze." → "Every tree
  the runner can leave — a side halted at its first unit, a side with
  units never written, a torn unit — reaches INSUFFICIENT_DATA from the
  production path; a side whose 141000/140000 losses are non-finite
  keeps its other members (§3.2's ABSENT rule); demonstrated at the
  freeze."
- **S-2 (C-2), §3.2.** After "a non-finite member is ABSENT under
  Experiment 5's slip-9 rule: its loss not finite, its counts never
  read, the side shorter, printed" insert: "— except the re-read member
  142000, whose non-finite loss fails gate 1's identity comparison with
  Experiment 5's finite committed read and refuses".
- **S-3 (F-4), §3.2.** "a side with no member, or whose f_B is not
  finite, has its cells **excluded and counted** (§3.7 UNDETERMINED if
  the live set falls below Experiment 5's floors)." → "a non-finite
  final halts the size (Experiment 5's writer halts on a non-finite
  final) and refuses; a side cannot lose all three members without
  losing 142000, which refuses at gate 1 — so no side is excluded on a
  finished campaign (freeze F-4)." **§3.6 gate 3**: "a side's final
  non-finite excludes the side" → "a side's final non-finite halts the
  size (INSUFFICIENT_DATA at the halt marker)". **§3.7**: "reachable only
  if sides are excluded" → "unreachable from a finished campaign (no
  side can be excluded — freeze F-4); kept for completeness".
- **S-4 (F-2), §3.6 gate 1.** Append: "Coverage is measured: all twelve
  re-reads re-derived, a missing one a refusal, and the runner's
  attestation's unit set equal to the re-derived set (freeze F-2)."
- **S-5 (D-4), §3.4 and §3.7.** "σ̂_s above 45 is the OFF-GRID sub-cell"
  → "σ̂_s above the simulated axis's top (the estimator's mean at σ_s =
  45) is the OFF-GRID sub-cell"; §3.7 "(σ̂_s above 45 — the licence not
  claimed)" → "(σ̂_s above the simulated axis's top — the licence not
  claimed)"; and add to §3.4: "the simulated axis must be strictly
  increasing, else the power gate refuses (freeze F-3)".
- **S-6 (D-3), §6.** Append to "Every world": "the analyzer's `claimed`
  flag is true for SURVIVES · CALIBRATED only; the INFLATED licence is
  its sentence."
