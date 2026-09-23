# Experiment 5 — adversarial freeze (Task 7 step 1, 2026-09-22)

Fresh-eyes freezer, cold, on `experiments/exp5/` at build HEAD
`b31b8c585` (Task 6 review fix round 1). The standing assignment,
verbatim from the program: find THE CLASS DEFECT — the defect that
would silently DECIDE the verdict — and close what is found ADDITIVELY
(a new refusal, pin, test, disclosure or record field; never an
accepted dial, never a change to a preregistered statistic, bar or
licence). Precedents read first for the form:
`experiments/exp4c/FREEZE_CHECKLIST.md` (F-1, the runner's unpinned
import surface) and `experiments/exp4/FREEZE_CHECKLIST.md` (F-1,
attested vs measured digest). The design's §11 assignment for this
experiment: the search runner is adaptive — show that no choice the
search makes can change a committed read, only which reads exist, and
that the analyzer's bracket derivation is total over every tree the
search can leave.

Zero model contact, zero network. Every attack ran on a tmp tree under
the session scratchpad, built by the production runners
(`finals_5.run`, `sweep_5.run`, `power_5.main`) driven by
`tests/fakes_5` through `tests/full_shape_5.write_world_5`; the attack
scripts are `a_*.py` in the session scratchpad
(`/private/tmp/claude-501/…/scratchpad/freeze/`) and their printed
lines are quoted below verbatim. Real git was used only in throwaway
repositories under the scratchpad (attacks iv, v, F-5's test). Every
execution of `analyze_5.run()` against the REAL tree is a disclosure
event; this session made four of them (§E).

Python `~/emergence-lab/.venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
repo root, `-p no:cacheprovider`. The slow suite and the mutation
harness ran detached (`Popen(start_new_session=True)`), the harness
alone.

## Baseline, measured cold BEFORE the freeze touched anything

| battery | result |
| --- | --- |
| fast suite (`tests/ -m "not slow"`) | **106 passed**, 13 deselected, 20.1 s |
| slow suite (`tests/ -m slow`: worlds, totality, determinism) | **13 passed**, 146 s |
| cold referent battery (`verify_referents_5.py`, real tree) | **11/13** + 2 legitimate SKIPs (item 11 power record, pre-targets; item 13 gate records, pre-campaign) |
| `check_frozen_5()` + `check_imports_5()` | clean — 51 frozen, 6 imported pins |
| mutation logs (`mutation_build.log` + `mutation_worlds.log`) | 56 considered — 27 fast-killed, 29 slow-killed (each re-confirmed `--worlds-only`), 0 equivalent, **0 unresolved** |
| pre-tag analyzer executions (PROGRESS.md) | **14** |

## Verdict on the assignment: **THE CLASS DEFECT WAS FOUND.**

**F-1: the production campaign could not deliver any verdict but
INSUFFICIENT_DATA.** `run/campaign_5.sh` runs `sweep_5` for every size,
160m last ("S11 only for 160m"). `sweep_5.run` loaded the spine for
ANY size, so the 160m run wrote eight spine units that no search, final
or S11 names; the analyzer's gate 4 re-derives "nothing else loaded"
(`expected_steps_5`: a size that is never a large side expects
`{final, S11}` only) and refused them. Every tree the campaign can
leave was INSUFFICIENT_DATA, and nothing said so until the analyzer
ran, after ≈ 30 h of rented compute. The worlds never swept the
smallest size, so no test reached it (the deferred Task 4 minor "no
test for a zero-partner size (160m)" was this defect). Eight findings
in all (F-7/F-8 on the controller's rulings), every one closed additively. Nothing preregistered moved:
`T_BAR_5`, `ALPHA_5`, `MODIFIER_ALPHA_5`, `MODIFIER_MIN_CELLS_5`,
`MIN_LIVE_CELLS_5`, `MIN_LIVE_RUNGS_5`, `MAX_ENUMERATE_BLOCKS_5`,
`N_PERM_SAMPLED_5`, `PERM_SEED_5`, `N_BOOT_5`, `BOOT_SEED_5`,
`GATE1_TOL_*`, the window width, the spine, `plan_5`'s search order,
`stats_5` (untouched), `power_5` (untouched), the tree and the licence
bodies are byte-identical to the build's.

---

## A. Findings

### F-1 — the sweep runner loaded the smallest size's spine; gate 4 refuses it (THE CLASS DEFECT). CLOSED.

**Demonstration (before),** a MATCHED world plus
`sweep_5.run(size=<smallest>)` — `run/campaign_5.sh`'s last line:

```
[base MATCHED world (sweep over SIZES_W[1:], as the worlds writer does)] verdict=MATCHED mod=None T=-0.045974999999999995 n_cells=40 n_failures=0
units loaded by sweep_5 --size 1b : [('1b', 1000), ('1b', 6000), ('1b', 16000), ('1b', 32000), ('1b', 31000)]
[after sweep_5 --size 1b (campaign_5.sh's last line)] verdict=INSUFFICIENT_DATA mod=None T=-0.045974999999999995 n_cells=40 n_failures=4
      gate 4 1b: step1000 on disk but never requested (nothing else loaded)
      gate 4 1b: step6000 on disk but never requested (nothing else loaded)
      gate 4 1b: step16000 on disk but never requested (nothing else loaded)
      gate 4 1b: step32000 on disk but never requested (nothing else loaded)
```

(In the world the smallest size is `1b` and the spine has five points;
on the real campaign it is 160m with eight non-final spine points.)

**Closure (commit `dc56e7011`).** `sweep_5.run` loads the spine, and
runs gate 1(c), for a LARGE side only; a size that is never a pair's
large side runs S11 alone. The rule narrows what the runner loads to
what design §3.2 and the plan's process tail already say (the spine
belongs to L; "S11 only for 160m"); gate 4 is unchanged. The worlds
writer now sweeps every size the campaign sweeps.

**After:** the same world + `sweep_5 --size 1b`: `units loaded … : []`
(its S11 already written by the world's own campaign), `verdict=MATCHED
… n_failures=0`. Test
`test_stages_5.py::test_sweep_of_a_size_that_is_never_a_large_side_loads_only_s11`
FAILS with the one closure line reverted (confirmed); mutant
`freeze_f_1_…` added to the harness.

### F-2 — gate 1(a)'s identity flags were attested, never re-derived. CLOSED.

`gate1a_failures_5` read `digests_equal` / `loss_equal` / `pass` as the
runner wrote them; the record carries the measured fields they were
computed from and none was compared. On a MATCHED world:

```
[loss_2c_path moved by 1e-9, loss_equal left True] verdict=MATCHED … n_failures=0
[per_doc_diffs 5, loss_equal left True] verdict=MATCHED … n_failures=0
[digest_2c_path replaced, digests_equal left True] verdict=MATCHED … n_failures=0
[counts_2c_path antonym +40] verdict=MATCHED … n_failures=0
[loss_candidate_path != the final unit's committed loss (both loss fields moved together)] verdict=MATCHED … n_failures=0
```

**Closure (`d5edbda67`).** `gate1a_failures_5` re-derives the digest
and loss equalities from the record's own fields and requires
`per_doc_diffs == 0`; `gate1a_unit_failures_5` ties the candidate path
to the committed 2.8b final unit (digest, loss to the bit, and the
2c-path counts equal to the unit's counts — the continuations being
attested identical). All five attacks now refuse, e.g.
`5 gate 1(a): … loss_2c_path 2.4528885895347945 != loss_candidate_path
2.4528885885347944 to the bit (re-derived; loss_equal is attested)`.
Test `test_analyze_5.py::test_gate1a_flags_are_re_derived_not_attested`;
three mutants. The sealed record is still bound by the targets tag
(attack iv); this closes a runner-side miscomputation, not a post-seal
edit.

### F-3 — gate 0 checked the stack's keys, never its pinned versions; `_checkpoint`/`_unit` host fields unchecked. CLOSED.

Design §3.7 gate 0 names the pins (torch 2.12.1, transformers 5.13.0,
numpy 2.4.6, safetensors, tokenizers, huggingface_hub — the Mac's, on
Python 3.11). `host_record_failures_5` checked only that each key was
present; the per-unit comparison (`_same_host`) covered `_loss.json` and
the rung records, not `_checkpoint.json` or `_unit.json`:

```
[whole campaign consistently on torch 2.11.0 — closure disabled (= before)] verdict=MATCHED … n_failures=0
[window unit 6.9b/step3000: _checkpoint.json stack changed (restamped)] verdict=MATCHED … n_failures=0
```

(The first: host record and every record rewritten to torch 2.11.0,
`power_5.json` re-written from those finals.)

**Closure (`4b9db1148`).** `STACK_PIN_5` / `PYTHON_PIN_5` (the Mac venv's
values, read this session: 2.12.1 / 5.13.0 / 2.4.6 / 0.8.0 / 0.22.2 /
1.22.0 / 3.11 — equal to `run/box_setup_5.sh`'s pip pins; torch's
`+cu130` local suffix is not part of the pin) checked inside
`host_record_failures_5`, so `finals_5` refuses a live host off the pins
and the analyzer refuses the record; `load_units_5` applies `_same_host`
to `_checkpoint.json` and requires `_unit.json`'s `host_sha256`. After:
`5 host record: … torch '2.11.0' is not the pinned '2.12.1' (gate 0)`;
`… 6.9b/step3000/_checkpoint: stack {'torch': '2.13.0', …}`. Tests
`test_battery_5.py::test_stack_pin_is_gate_0s_named_versions`,
`test_stages_5.py::test_units_refuse_a_checkpoint_or_unit_record_from_another_host`;
two mutants.

### F-4 — gate 3's finiteness and completeness held by accident, not by a check. CLOSED.

(a) `finite` is the runner's attestation. `loss_record_failures_5`
compared the loss with its per-set token-weighted mean by
`abs(s/n − loss) > 1e-9`, False for NaN, so a NaN loss with
`finite: true` passed its contract, and the loss-table comparison did
not catch it either (json's `NaN` is a module singleton, so the
rebuilt and committed tables compare equal):

```
   NaN window loss, finite:True — loss_record_failures_5: []
[NaN window loss (finite:True), loss table rebuilt over the tree] verdict=MATCHED … n_failures=0
```

(b) `load_units_5` skips a step directory that is not a complete unit.
For a large size the search log's request check happened to catch a
torn unit; for the smallest size, whose search log the analyzer never
reads, a torn S11 unit vanished from S11 with the verdict MATCHED (the
refusal-routes world, closure reverted: `AssertionError: assert
('MATCHED' == 'INSUFFICIENT_DATA'`).

**Closure (`c87fed60e`).** `loss_record_failures_5` measures the
finiteness of the loss and of every non-empty per-set loss; gate 4's
per-size pass refuses any step directory on disk that is not a
complete unit ("the puller copies complete units only", so the
committed tree holds none). After: `… 6.9b/step3000/_loss: loss nan is
not a finite float (measured; `finite` is attested)`; the torn smallest
S11 → `gate 3 1b: step31000 is on disk but is not a complete unit …`.
Tests: `test_battery_5.py::test_loss_record_refuses_a_nan_loss_the_finite_flag_attests_away`;
both attacks added to `test_full_shape_5.py::test_refusal_routes_deliver_insufficient_data`;
two mutants (the torn-directory one killed by the world only, recorded
in `NON_FAST_KILLS_5`).

### F-5 — gate 5 read the projection's adding commit only; a later revision passed. CLOSED.

`projection_commit_5` resolves the commit that ADDED
`experiments/exp5/projection.md`; gate 5 checks seal → projection →
every sweep unit by ancestry. Nothing compared the projection graded at
close-out with the one sealed. In a throwaway repository with a real
commit DAG:

```
   adding commit unchanged after the edit: True
[projection.md EDITED after every sweep unit (gate 5 reads the adding commit only)] verdict=MATCHED … n_failures=0
```

**Closure (`464919eee`).** `battery_5.projection_edits_5` lists every
commit after the adding commit that touches `projection.md`, and a
working-tree blob that is not the one the adding commit added;
`analyze_5.run()` measures it whenever the projection commit is resolved
from the real repository (an injected commit — the worlds — injects its
edits, default none; `pins_active["projection_edits_measured"]` records
which). After: `5 projection: … commit 06bbcc32… modifies
experiments/exp5/projection.md after its adding commit 7a1ede39…`. Test
`test_battery_5.py::test_projection_edits_are_refused_after_the_adding_commit`
(temp repository, uncommitted and committed revision); one mutant.

### F-6 — a dropped pair's record did not say which of two facts dropped it. CLOSED (record field).

`plan_5` drops a pair when no spine interval crosses the target. §3.2
names one cause — the larger model never reaches the smaller's final
loss. The built rule also drops a pair whose larger model is already
below the target at the spine's FIRST point (the crossing lies in the
log head the spine never searches); both were printed "no spine
interval crosses the target". The MATCHED world carries one: 6.9b × 1b,
target 2.8529, 6.9b at step1000 2.8325. On the real campaign this needs
a larger model at step 1000 already below a smaller model's final loss
— not expected on Pythia, never excluded.

**Closure (`281d05e8d`).** `drop_kind_5` → `never_reaches` /
`crosses_before_spine` / `no_first_crossing_interval` on every
`dropped_detail` row and in VERDICT.txt; never gating. After:
`dropped: 1b -> 6.9b target 2.8529 kind crosses_before_spine`. Test
`test_analyze_5.py::test_drop_kind_names_which_fact_dropped_the_pair`;
one mutant. The design sentence goes to the slips (§F item 1).

### F-7 — a non-finite unit loss did not halt the runner (controller ruling B-3(b)). CLOSED.

Gate 3 as written requires a finite loss on EVERY unit, but `run_unit_5`
wrote the unit and the sweep went on; the refusal surfaced only at the
analyzer, after the campaign (§D). **Closure (`39d512925`).** Right
after the loss record is written and before any rung, `loss["finite"]`
not True → the size's `HALTED` marker (naming the unit, its `why` and
`n_nonfinite`), the unit left incomplete (no `_unit.json`), the
checkpoint freed in `finally`, `SystemExit(2)`. The docstring notes the
one-line narrowing if the ratification narrows gate 3 (slip 9).
Test `test_stages_5.py::test_a_non_finite_unit_loss_halts_the_size`:
NaN at one 2.8b spine step → exit 2, marker present and naming
`step2000` and `n_nonfinite 7`, `_loss.json` written, no `_unit.json`,
no rung record, `(2.8b, 2000)` in the freed list, the runner refuses to
resume, the analyzer lands INSUFFICIENT_DATA at `5 halt marker`; FAILS
with the check disabled (confirmed). Mutant `freeze_f_7_…` killed fast.

### F-8 — the window/spine prefetch never overlapped scoring (controller ruling). CLOSED.

`request()` started the NEXT step's download, then `run_unit_5` called
`prefetcher.wait()` before loading the CURRENT step, so every prefetch
was joined before scoring began (§B's former "DISCLOSED" row; slip 8).
**Closure (`86050f39f`).** `Prefetcher.target` (the `(size, step)` in
flight, None when idle) and `Prefetcher.wait_for(size, step)` (joins
only if `target == (size, step)`); `run_unit_5` calls `wait_for`;
`sweep_5.run` keeps its final `pf.wait()`. Different steps download
into different cache directories (`_rev_dir(size, step)`); the same
step cannot race because `wait_for` joins first. Test
`test_stages_5.py::test_the_next_steps_prefetch_overlaps_the_current_units_scoring`
(a fake prefetch recording start/finish against loads, first-generate
and joins): for every spine step, the next step's prefetch starts
before the current unit is scored and is joined only after it, before
the next unit loads; plus `wait_for`'s idle / different-step /
same-step cases. FAILS with `wait()` restored (confirmed). Mutant
`freeze_f_8_…` (`if True:`, the old behaviour) killed fast.

### The preflight's early warning moves to `step256` (controller ruling B-3(c)). APPLIED (`4487b5e22`).

`PREFLIGHT_STEPS_5` `(1000, 1)` → `(1000, 256)`: the spine starts at
`step1000`, so t_lo ≥ 1000 and B⁻ = {256, 512} at worst on every size;
`step1` is loadable by no window (and is excluded at 1b). Docstring
updated; test
`test_stages_5.py::test_preflight_early_warning_is_the_earliest_step_a_window_can_reach`
derives the earliest window member from the committed manifest.
`run/preflight_5.py` is pinned in `IMPORTED_SHA256_5`: re-pinned
`975b3d50…` → `f32e8c36…`; import scan re-run once (counted, §E).

---

## B. The attack list (the brief's ten surfaces, then the rest)

Each row: what ran, what it printed, the disposition. "World A" = the
MATCHED world written by `write_world_5` (four sizes 1b/1.4b/2.8b/6.9b,
five-point spine, 40 live cells, T −0.0460, zero failures).

**(i) The adaptive search** — the design's §11 assignment.

| # | attack (`a_i.py`, `a_i2.py`, `a_f1.py`) | printed | disposition |
| --- | --- | --- | --- |
| i.1 | World B built by the same runners in the CAMPAIGN order (6.9b, 2.8b, 1.4b, 1b), the 14th sweep unit killed inside its `odd6` rung (a torn unit, `step6000` of 2.8b) and the size resumed; every complete unit compared with World A field by field (`written_utc`, `seconds`, `why` dropped) | `A vs B: 41 units compared …: 0 differences`; `primary`, `modifier`, `signed_offset` identical; `why` differs on no unit | CLEARED — order, crash and resume change no committed read and no statistic |
| i.2 | the LARGE-AHEAD world (different counts, the same loss curve) against World A: every pair's status, bracket and `requested_all` | `every status/bracket/requested_all identical: True` | CLEARED — the search reads losses only; no count can steer which reads exist |
| i.3 | `plan_5` over 108,000 random partial tables (every large size × its real targets + 10 random targets × 3,000 subsets of the available list), off-path steps injected with NaN or a tie with the target | `0 violations of 'need = the first missing step on the full-table path; done/dropped = the full-table plan'` | CLEARED — `plan_5` is total and path-monotone: over any partial table it asks for the first step the full-table replay would name, or returns the full-table plan; the runner can never be steered to a step the analyzer's replay would not request (cold battery item 10 adds 300 partial tables) |
| i.4 | the search log tampered 17 ways on World A, and the loss table once | refuse: `bisected` reversed; one `requested_all` step dropped; two swapped; done→dropped; dropped→done; bracket shifted; `B⁺` replaced; target +1e-6; a stray `12b` pair; a pair removed; a request naming a non-unit; the spine field; `git_sha` removed; the log deleted; `loss_table_5.json` one loss +1e-12. Do NOT refuse: `requested_all` actions flipped, `why` labels scrambled, `plan.residual_lo` altered | CLEARED — the three that pass are informational: cells, residuals and brackets are read from the analyzer's own replay over the committed losses, never from the log |
| i.5 | the worlds (all five modes) | `test_every_terminal_is_reachable` asserts zero failures, so the replay reproduces every logged bracket, window and bisection order on every world | CLEARED |
| i.6 | units written once: `run_unit_5` called on a COMPLETE unit with a different fake model (loss 9.99, 500 correct) | `action=reused … loads=[] files unchanged=True` | CLEARED (B-9) |
| i.7 | a torn unit: a directory holding a bogus `_loss.json` (0.123) and a stray file, then `run_unit_5` | `action=loaded new loss=9.99 stray file survived=False n_files=37` | CLEARED — a torn unit is discarded whole |
| i.8 | the smallest size's sweep (`campaign_5.sh`'s last line) | see F-1 | **CLOSED as F-1 (the class defect)** |
| i.9 | totality over every runner-leavable tree | the 9-shape totality test (slow) + the two new F-4 shapes in the refusal-routes world; a halted mid-160m S11 leaves a torn directory, now refused by F-4 | CLEARED (after F-4) |

**(ii) The loss's determinism / gate 1(a).** The runner's `loss_equal`
compares `repr(loss)` AND the `per_doc_loss` lists (test
`test_finals_gate1a_catches_a_per_doc_loss_mismatch_with_equal_aggregate`;
mutant `gate1a_loss_equal_ignores_per_doc_loss` killed); the preflight's
double run compares the same two. The analyzer read the flag only —
**CLOSED as F-2**. DISCLOSED: `per_doc_loss` is rounded to 1e-6 by
`loss_from_per_doc_5`, so the per-document comparison is to 1e-6; the
scalar comparison is to the bit.

**(iii) Gate 1(b)'s tolerance against a different network.** On the
Mac's committed finals (the five referent sizes), every pair of sizes
differs beyond the tolerance (15 per rung / 120 summed): the closest,
410m vs 1b, max |Δ| 32, Σ|Δ| 206; 6.9b vs 12b 56 / 317; 2.8b vs 6.9b
250 / 665. Every adjacent pair of gate 1(c)'s interior checkpoints also
fails it (smallest: 2.8b 16k vs 32k, 28 / 202; 6.9b 4k vs 8k, 37 / 167).
`gate1b_failures_5` on a tree whose final rung records carry the true
counts: `[]`; with two sizes' counts swapped: `2.8b<->6.9b: 18
failures`, `410m<->1b: 14`, `6.9b<->12b: 14`, `1b<->2.8b: 22`.
CLEARED. (The weights' identity itself is the manifest's LFS shas,
measured by the runner, and the tensor digest; gate 1(b) catches a
different stack/harness, and a swapped network by a wide margin.)

**(iv) The targets seal** (`a_iv_v.py`, a throwaway git repository
holding World A, the tag `exp5-targets-sealed` cut over it,
`battery_2i.blobs_bound` against it): clean → `MATCHED … 0`; a
post-seal edit to one final rung record (restamped) → `5 targets seal:
'exp5-targets-sealed' does not bind [… _unit.json, … antonym.json]`,
and the sweep runner (its production `require_seal_2i` path) →
`refusing: the targets seal: …`; `power_5.json`'s declaration edited →
the seal AND the byte-reproduction refuse, the sweep runner refuses.
CLEARED.

**(v) The projection ancestry** (same repository, a real DAG seal →
projection → sweep): every sweep unit after the projection → `MATCHED
… 0`; every sweep unit at the seal commit (before the projection) →
`5 projection: … 1b/step31000 (why 's11') was built at 87a5e942…,
which is not a descendant of the projection commit …`; a projection on
an orphan branch → `the targets seal (…) is not an ancestor of the
projection commit …`. CLEARED. The projection revised after the
sweep → **CLOSED as F-5**. DISCLOSED: a unit's `git_sha` is the
runner's HEAD, recorded, not re-measurable on the Mac; the finals
(exempt from the projection check, they precede it) are not checked
against the prereg tag's commit — RULED not added (the tag binds
blobs; `require_prereg_5` runs at every runner start and in the
analyzer; a commit check would break on every post-tag ledger commit
and on a re-tag).

**(vi) The host record.** One rung record's torch changed (restamped)
→ `gate 3 contract failure(s): ["6.9b/step3000/antonym: stack …`;
`_loss.json` device `mps` → `… device 'mps' != the host record's
'cuda'`; the host record alone on torch 2.11.0 → every unit refuses
against it. `_checkpoint.json`'s stack, and a whole campaign
consistently on another stack → **CLOSED as F-3**. DISCLOSED: gate 0's
"both transports measured" accepts a `None` measurement (the
subprocess failed); refusing the finals on a failed transport probe
would stop a campaign for a non-verdict field, so it is left printed.

**(vii) Gate 3's coverage.** A rung record with 499 bits (restamped) →
`bits/continuations are not 500 long`; `_unit.json` naming 36 files
with `odd6.json` missing: a window unit → refused (loss table + search
log), the 1.4b FINAL → `1.4b: the final (step143000) is not among the
complete units`, the smallest size's S11 → vanished silently →
**CLOSED as F-4(b)**. DISCLOSED: an S11 unit that was never written at
all (e.g. 160m's sweep never ran) is absent from S11 without a
refusal — S11 is non-gating and prints only the sizes it has.

**(viii) The import surface.** Two lines in `run/__init__.py` —
`from experiments.exp5 import search_5 as _s` /
`_s.bisect_step_5 = lambda available, lo, hi: None` (the bisection
disabled: every bracket collapses to the spine interval) — in a
subprocess each: the sweep runner (`bisect_step_5 is patched: True`)
→ `refused: RuntimeError imported module drifted from its pin: (pin)
-> …/experiments/exp5/run/__init__.py`; the finals runner → the same;
`check_imports_5` (the analyzer's entry and exit) → the same. File
restored byte-identically (sha checked). CLEARED. (Both runners check
at entry only — the Task 4 ruling; the analyzer's gate 4 replay would
refuse a bisection a drifted runner performed anyway.)

**(ix) The power record's D-grid and deciding arm.** On World A's
record: the `arms` dict's key order reversed → `MATCHED … 0` (JSON key
order carries nothing: both sides are compared under
`sort_keys=True`); `d_grid` reversed → `the recomputed record differs
byte-for-byte`; the deciding arm swapped to concentrated × ½ with its
own P and a consistent declaration → refuses; the declaration literal
flipped → refuses; `seed` 1 → `seed 1 != power_5.SEED_5 0 — provenance
is measured, not attested` + byte mismatch. `compute()` twice in one
process byte-identical; `test_determinism_5` covers two processes.
`DECIDING_ARM_5` and the rng order are module constants in a
tag-bound blob; a reader cannot move the declaration without moving a
bound byte. CLEARED.

**(x) B-3.** §D.

**Further surfaces (the B-list and what the reading turned up).**

| surface | attack / reading | disposition |
| --- | --- | --- |
| B-5, the power model | read `power_5` against the plan's B-5 text: σ = 17·√(π/2)/√2 = 15.07, drift 4, offset 25, q ½, factors 1 / ½, deciding arm spread × 1, the D grid .01–.06, POWER_BAR .75 — all as ledgered; the simulated structure is the small finals that clear (cells live only through the large side not simulated, printed beside the realized count) | CLEARED for the freeze; the parameters are the ratification's (B-5) |
| B-7, ancestry | (v) above | CLEARED + F-5 |
| B-9, units written once | (i.6)/(i.7) | CLEARED |
| B-3, the window-only non-finite loss | §D | stated for the ruling; the NaN hole closed as F-4(a) |
| the drop rule | the MATCHED world's 6.9b × 1b drop | CLOSED as F-6 (record field) + slip 1 |
| the earliest reachable window step | the manifest: every size's spine starts at 1000, so t_lo ≥ 1000 and B⁻ ⊆ {256, 512} at worst; `step1` is loadable by no window (and is excluded at 1b) | DISCLOSED; slip 2 and a ruling item (the preflight's early warning checks step1, not step256) |
| the window prefetch | `request()` starts the next download, then `run_unit_5` called `prefetcher.wait()` BEFORE loading the current step, so the download was joined before scoring started — no overlap with scoring at all | **CLOSED as F-8** (controller ruling) |
| the finals' `git_sha` against the prereg tag's commit | the finals are exempt from the projection-ancestry check and no check ties them to the tag's commit | DISCLOSED (controller ruling: NOT added — the tag binds BLOBS, and `require_prereg_5` runs at every runner start and in the analyzer; a commit check would break on every post-tag ledger commit and on a re-tag) |
| a stray size directory | a directory under `results/units/` for a size outside `SIZES_5` is never read | DISCLOSED (nothing reads it; it cannot enter a cell) |

## C. Batteries after the closures

| battery | before | after |
| --- | --- | --- |
| fast suite (`-m "not slow"`) | 106 passed | **113 passed** after F-1..F-6 (+7); **116** after the rulings (+3: F-7 halt, F-8 overlap, the preflight step), 24.6 s |
| slow suite (`-m slow`) | 13 passed | **13 passed**, 161 s after F-1..F-6; **13 passed**, 160 s after F-7/F-8 (the refusal-routes world carries F-4's two attacks and a contract-clean orphan unit; every world sweeps the smallest size too) |
| cold battery (`verify_referents_5.py`) | 11/13 + 2 SKIP | **11/13 + 2 SKIP** (items 11, 13: pre-targets / pre-campaign) — no referent file or pin changed |
| `check_frozen_5` / `check_imports_5` | clean (51 / 6) | **clean (51 / 6)**, checked in a fresh process with every stage module imported (analyzer, power, both runners, preflight, S9, both cold tools): no unpinned module. F-1..F-6 and F-7/F-8 touched tag-bound blobs and tests only; the preflight ruling changed `run/preflight_5.py`, re-pinned in `IMPORTED_SHA256_5` (`f32e8c36…`) |
| mutation harness | 56: 27 fast / 29 slow / 0 equivalent / 0 unresolved | after F-7/F-8 (+2 mutants: the halt condition, `wait_for`'s equality): **68: 43 fast / 25 slow / 0 equivalent / 0 unresolved**, worlds-only 30/30 killed (`f8e590b18`; five former slow-only kills now die in the fast suite, F-7's stage test running the analyzer on a halted tree). Before that, after F-1..F-6: **66: 36 fast / 30 slow / 0 equivalent / 0 unresolved** — RE-RUN, because the closures changed modules mutants target (`run/sweep_5`, `battery_5`, `analyze_5`); +10 freeze mutants; one pre-existing mutant (`gate4 … units_unnamed …`) survived the first worlds pass after F-4 (its only killing case, an empty-`_unit.json` orphan, had become a torn-unit refusal too) — the world now writes a contract-clean orphan unit, and the second pass killed 30/30. Both logs regenerated from the current source (`b2bbd647b`) |
| read sweep (`tests/read_sweep_5.py`) | 1853 paths, 0 UNPINNED (Task 6) | **1853 distinct paths (1952 open/read calls), (e) unpinned verdict input 0 — clean**; run because F-5 adds a read of `projection.md` (through `git hash-object`, a subprocess the sweep's `open()` hook does not see — content-checked by blob identity, and absent pre-campaign). No committed file joined the analyzer's reads, so `referents_5.json` / `REFERENTS_5_SHA256` are unchanged |
| import scan (`tests/import_scan_5.py`) | 51 frozen + 6 residual, pinned | printed pin table's tail identical to `IMPORTED_SHA256_5`; re-run after the preflight re-pin: `# 51 frozen (non-exp5) modules, 6 exp5-own residual module(s)`, table equal to the committed one incl. `run/preflight_5.py` `f32e8c36…` |
| cold battery after F-7/F-8 | — | **11/13 + 2 SKIP** |

## D. B-3, stated for the ruling

What a non-finite loss on a window-only unit does to the verdict, as
built and as written (§3.7 gate 3: "finite loss" on every unit):

- **`finite: false` on a window-only unit** (World A, 6.9b/step3000,
  a B⁺ member whose loss enters no bracket): `load_units_5` is
  all-or-nothing per size, so the whole 6.9b size refuses and every
  size's units with it — `5 finals: ValueError: 6.9b/step3000: gate 3
  contract failure(s): ['6.9b/step3000/_loss: loss not finite (3
  non-finite tokens)']`, `verdict=INSUFFICIENT_DATA`, `n_cells=0`. As
  written: the whole verdict refuses.
- **A NaN loss attested `finite: true`** read MATCHED before F-4(a);
  after it, the same refusal as above.
- **The runner does not halt on a non-finite unit loss.** `run_unit_5`
  writes the unit and the sweep continues; the refusal surfaces only
  when the analyzer runs, after the campaign.
- **Where it can happen.** The earliest checkpoint any window can load
  is `step256` (B⁻ when t_lo = step1000, every size); the preflight's
  early warning loads 12b `step1000` and `step1`, and `step1` is
  loadable by no window.

**Ruled by the controller (2026-09-22):**
(a) the narrowing of gate 3's finiteness to spine + bisection units is
a RATIFICATION SLIP for Michael (slip 9; the tag is not cut, so the
design can be amended at ratification without spending the
pre-committed change) — the build keeps gate 3 AS WRITTEN;
(b) the runners halt on the first non-finite loss on ANY unit — CLOSED
as F-7; (c) the preflight's early warning moves to `step256` —
APPLIED (§A).

## E. Disclosure tally

Executions of `analyze_5.run()` on the REAL tree this session — **4**,
the running total **14 → 18** (appended to `PROGRESS.md`'s tally):

15. `tests/read_sweep_5.py` (after the closures) — `pre-campaign run
    (NOT the experiment's verdict): INSUFFICIENT_DATA — 5 host record:
    ValueError: host record missing`; 1853 distinct paths, 0 UNPINNED.
16. `tests/read_sweep_5.py` again, to capture the summary lines the
    first invocation's filter dropped — identical output.
17. `tests/import_scan_5.py` (after the closures) — the pin table
    printed; only its tail was captured, which matches
    `IMPORTED_SHA256_5`; on the pre-campaign tree `run()` refuses at
    "5 host record" by construction (runs 15/16 in the same state).
18. `tests/import_scan_5.py` after the preflight re-pin (ruling
    B-3(c)) — `pre-campaign run: INSUFFICIENT_DATA — 5 host record:
    ValueError: host record missing`; 51 frozen + 6 residual, the
    printed table equal to the committed pins.

No statistic was computed on the real tree. Every attack ran on tmp
trees (worlds do not count). `check_imports_5` / `check_frozen_5` and
the runners' `--dry-run`-equivalent calls in attack (viii) do not call
`run()`.

## F. Slips for ratification (the design doc is NOT edited here)

1. **§3.2 step 2**, "If no interval crosses (ℓ_L(final) ≥ ℓ_s — the
   larger model never reaches the smaller's loss), the pair is dropped":
   the built rule also drops a pair whose larger model is below ℓ_s at
   the spine's first point (the crossing precedes `step1000`). Suggested
   wording: "… dropped and printed with its kind — `never_reaches`, or
   `crosses_before_spine` when the larger model is already below ℓ_s at
   the spine's first point (the log head is not searched)" (F-6).
2. **§3.2 step 4 and §3.1/§7 stage 0** (the preflight now loads
   `step256` — controller ruling B-3(c)), "t_lo within two of `step1`" and
   "12b `step1000` and `step1`, the earliest checkpoints any window can
   reach": the spine starts at `step1000`, so t_lo ≥ 1000 and B⁻ is
   never short; the earliest window member is `step256` (B⁻ = {256, 512}
   at t_lo = 1000, every size). Only B⁺ can be at an edge (t_hi = the
   final). `step1` is loadable by no window and is excluded at 1b.
3. **§3.7 gate 3**, "a unit scored twice (a bisection revisit) must be
   byte-identical to its first record": vacuous through the runner —
   units are written once and reused (B-9); the preflight's double run
   and S9 carry the measurement.
4. **§3.7 gate 7**, "`exp5-targets-sealed` over the finals' records, the
   loss table's first rows and the power record": built as the seven
   finals' 37 unit files each (their `_loss.json` are the loss table's
   first rows), `gate1a.json`, `gate1b.json`, `host_5.json`,
   `power_5.json` (B-1); `loss_table_5.json` is re-derived from the unit
   files and compared, not bound.
5. **§3.7 gate 1(a)**, "an identical slice loss to the bit": the scalar
   is compared by `repr` (to the bit); the per-document means are
   compared as recorded, rounded to 1e-6 (`loss_from_per_doc_5`). After
   F-2 the analyzer re-derives both from the record and ties the
   candidate path to the 2.8b final unit.
6. **§3.7 gate 5**, "the projection committed before the first window
   unit": built as before the first SWEEP unit, spine included (B-7),
   and — after F-5 — the file unedited since its adding commit.
7. **§3.7 gate 0**, the stack pins: now enforced (F-3) at the Mac venv's
   values; the design names safetensors / tokenizers / huggingface_hub
   without versions — suggested: "safetensors 0.8.0, tokenizers 0.22.2,
   huggingface_hub 1.22.0".
8. **§7 Budget**, "download time that the runner overlaps by prefetching
   the next candidate": as first built the runner joined the prefetch
   before loading the current unit (no overlap); F-8 restores the
   overlap the budget assumes. No wording change needed; the ledger
   records the closure.
9. **§3.7 gate 3 finiteness (B-3(a), controller ruling: a ratification
   slip).** Demonstration (§D): `finite: false` on a window-only unit
   (6.9b/step3000, a B⁺ member whose loss enters no bracket) refuses
   the whole verdict — `5 finals: … gate 3 contract failure(s):
   ['6.9b/step3000/_loss: loss not finite (3 non-finite tokens)']`,
   `n_cells=0`. **Recommendation: narrow.** Suggested wording: "finite
   loss on every spine and bisection unit (the losses the search reads);
   a window-only or S11 unit carries `finite` as a disclosed field, and
   its counts are read as usual." If ratified, the analyzer's
   `loss_record_failures_5` clause and F-7's halt condition narrow with
   it (one line each: the unit's `why` in spine/bisect/final); until
   then the build keeps gate 3 as written.
10. The plan's B-1 … B-11 deltas are not yet in the design doc (the
    ratification package's business); F-1 adds one more sentence §7
    needs: "a size that is never a pair's large side (160m) runs S11
    alone — no spine".

## G. Deferred minors (the final review's; untouched unless named)

From `.superpowers/sdd/2026-09-22-exp5-build/progress.md`, every
`minor (deferred)` line, in its words, with this session's disposition:

- Task 1: record-contract functions untested in that diff (exercised by
  Task 4's `test_collect_5`) — untouched.
- Task 1: `SMALL_SIDES_5` / `LARGE_SIDES_5` untested slices — F-1's
  stage test now exercises `LARGE_SIDES_5` membership in the runner;
  otherwise untouched.
- Task 2: unused `import hashlib` in `slice_5.py` — untouched.
- Task 2: slice edge-case tests (64-token document, exact fill, equal
  lengths, empty stream) — untouched.
- Task 4: `finals_5` docstring order; `_write`/`_halt` duplicated across
  three modules; unused `import time` in `sweep_5`; **"no test for a
  zero-partner size (160m)" — this was the class defect (F-1), closed
  with a test**; "a torn unit dir" — a torn unit is now refused on the
  analyzer side (F-4(b)) and its runner-side discard demonstrated (i.7);
  the rest untouched.
- Task 5: S9's "present" path untested; S9's tolerance message wording —
  untouched.
- Task 6: PROGRESS/report wording "27 hand + 29 AST" vs 28 + 28; the
  stale `make_referents_5` docstring ("6 × 35"); `test_totality_5`'s
  corrupt/restore steps without try/finally — untouched.
