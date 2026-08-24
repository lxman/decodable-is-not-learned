# Experiment 2h — Progress Ledger

Design doc `experiment-2h-design.md` stays as ruled (dials a–f RULED by
Michael 2026-08-24, "Full 34 rungs, dials as recommended") — nothing in
it is edited during the build. Zero model contact throughout this
session: the only Hub data anywhere in the tree is the committed
`hub_inventory_69.json` metadata scan (copied from
`docs/superpowers/plans/hub_inventory_69_2026-08-24.json`); no
`from_pretrained` of weights, no `hf_hub_download` of a weight file, no
forward pass. Tag `exp2h-preregistered` not yet cut — that is the
freeze session's business. The only model contact in the whole
campaign is the 6.9b checkpoint sweep, which unlocks only after the tag
(design §7).

## 2026-08-24 — BUILD, Task 1: `battery_2h.py` + the 6.9b manifest + loader

Instrument at `experiments/exp2h/`: `__init__.py`, `run/__init__.py`,
`tests/__init__.py`, `hub_inventory_69.json` (copied, sha256
`8762902fe2f194a082e82cffb144efc347b9cad4b597768028a2d521776b8325`),
`battery_2h.py`, `checkpoints_2h.json` (generated), test
`tests/test_battery_2h.py` (15 tests, all pass).

**R_69** re-derives from 2c's committed m4 6.9b counts (all 34 rungs,
`FINAL_COUNT_PIN_69`, read once from
`experiments/exp2c/results/m4/6.9b_trained/*.json` and pinned as
literals; `load_m4_counts_69` re-asserts every value against the pin
at load) under 2d's floor via `battery_2g.rising_by_bar` (reused, not
re-implemented) — exactly the design's eight rungs: antonym 286,
antonym6 143, add_base8 29, sub_base8 52, add3_mid 19, arith_next 58,
count_div13 102, odd6 107. Two (count_div13, odd6) never used by 2g's
2.8b primary (R_28); add3_mid's final count (19) sits under the
20-item eligibility floor (`battery_2g.ELIGIBILITY_MIN_POS`), disclosed
per design §4 and asserted in the test, not enforced at this layer
(eligibility is a primary-time gate on the realized sweep's n_pos, not
on the m4 final count).

**The 6.9b manifest** (`build_manifest_69`) mirrors
`checkpoints_2g.build_manifest`'s body for one size with an injected
repo/grid and no exclusions, using `checkpoints_2g.candidate`/
`.signature` directly (`build_manifest` itself is bound to
`battery_2g.REPO_OF`/`.GRID`/`.EXCLUDED_GRID`, none of which carry a
6.9b entry). From the committed `hub_inventory_69.json` (155
revisions): 23 grid entries (22 trained + step0), every candidate
`bin-shards` except the final point (`safetensors-shards`, main
publishes safetensor shards), every entry's (kind, lfs-shas) signature
distinct — no exclusion needed, confirming the design's "6.9b is the
cleanest size" scan. `stale_main_copies` is `{"model.safetensors": 0,
"pytorch_model.bin": 0}` — zero stale-main copies anywhere in the 155
revisions, also as the design states. Manifest sha256 (`checkpoints_2h.json`,
verified against the committed file):
`c5cd292cbf0d26a6968c5852d8bbf7f872d4b78fd8c7352a8a3e9e11be67cf60`.

**Discrepancy against the plan, disclosed rather than bent:** the
plan's Task 1 key-steps paragraph states the manifest should show
`final_duplicates == ["step143000"]`. The computed value, from the
committed inventory through the reused `candidate`/`signature` rule,
is `final_duplicates == []`. This is not a bug in the data — it is
structural in the frozen rule, and matches the precedent already
sitting in 2g's own committed `checkpoints_2g.json`: BOTH the 2.8b and
12b manifests there also carry `final_duplicates: []`, despite each
having a materially different, byte-identical `hub_step143000` (12b:
`signature_equals_main: true`, `duplicates: ['step58000']`; 2.8b:
`signature_equals_main: false`, 76 stale `model.safetensors` copies
tracked separately under `stale_main_copies`, none of which ever
becomes a revision's *candidate* because the rule steers a
main-matching single safetensors file to the bin branch unless the
revision literally IS main). `signature()` is kind-specific: main's
candidate for 6.9b is `safetensors-shards` (it publishes safetensor
shards), step143000's is `bin-shards` (it does not) — two different
kinds can never produce equal signature tuples, so `dups_of("main")`
structurally cannot list step143000. The design's "step143000
byte-identical to main" fact IS present in the manifest — as
`hub_step143000.signature_equals_main == True` (a direct bin-sha
comparison, the same field 12b's manifest carries its analogous fact
in), with `hub_step143000.duplicates == []` (no OTHER step branch
duplicates step143000's own bin content — the "cleanest size" claim).
The test (`test_manifest_from_committed_inventory`) asserts the
computed values, not the plan's literal, with the reasoning inline as
a comment; this note is the disclosure the build rules require instead
of silently bending a literal. Task 2/3 should read the "step143000 ==
main" fact from `hub_step143000.signature_equals_main`, not from
`final_duplicates`.

**`sampler_counts(size, rungs)`** generalizes `analyze_2g.sampler_counts_1b`'s
body to a `size` argument (a new function in `battery_2h`; exp2g's stays
1b-only and untouched). Verified against `analyze_2g.sampler_counts_1b`
directly (full per-item array equality, not just spot values) on all
six rungs of R_28 ∩ R_69 = {add3_mid, add_base8, antonym, antonym6,
arith_next, sub_base8}; also exercised at 410m for shape. Rejects a
non-probe size (e.g. "6.9b") by construction.

**`FROZEN_2G_SHA256`** pins the 7 exp2g modules this instrument imports
or mirrors (battery/labels/strata/stats/probe/checkpoints/analyze)
plus 3 exp2g data files (`results/predictor/predictor.json`,
`checkpoints_2g.json`, `referents_2g.json`) — 10 pins, `check_frozen_2h`
re-asserts every one. `PREDICTOR_2G_SHA` (the plan's literal,
`9eadbac316ddc5db7f7af716e406d3434033ccbaceb64a39467febdba757adc7`)
verified against a fresh sha256 of `experiments/exp2g/results/predictor/predictor.json`
— matches exactly, and equals `FROZEN_2G_SHA256`'s entry for that path.
The `checkpoints_2g.json`/`referents_2g.json` pins were cross-checked
against `analyze_2g.CHECKPOINTS_SHA256`/`.REFERENTS_FILE_SHA256`
directly in the test — all three agree.

The loader family (`download_entry_69`/`clean_dir_69`/
`load_checkpoint_69`/`free_69`) is a thin, repo/sha-parameterized copy
of `checkpoints_2g`'s loader (`checkpoints_2g`'s is bound to
`battery_2g.REPO_OF`, which lacks 6.9b); `huggingface_hub`/`torch`/
`transformers` are imported lazily inside each function body, never at
module import, and the test suite never calls them — tensor digest is
reused from `checkpoints_2g.tensor_digest` by import, not redefined.

Test suite: 15/15 pass (`experiments/exp2h/tests/test_battery_2h.py`),
zero model contact, zero network. Commit follows this entry.

## 2026-08-24 — BUILD, Task 2: `analyze_2h.py` + `power_2h.py` + referents + worlds

Instrument: `analyze_2h.py`, `power_2h.py`, `make_referents_2h.py`,
`verify_referents_2h.py`, `tests/full_shape.py`, `tests/test_analyze_2h.py`,
`tests/test_full_shape_2h.py`, `tests/test_power_2h.py`. Zero model
contact throughout: no `from_pretrained` of weights, no
`hf_hub_download`, no forward pass; the world builder writes only
JSON records in the production sweep layout, never a checkpoint file.

**Tree** (`verdict_tree_2h`): INSUFFICIENT_DATA → CONFIRMED
(p_strat < .01 ∧ T ≥ .10) → NOT-CONFIRMED (everything else,
"detected below the effect bar" / "inverted" named inside, mirroring
2g). No twin/SURFACE/DIFFICULTY-ONLY terminal — design §3.3: the
untrained sampled count is all-zero by construction (exp3's twin
referent, 0/576,000), so a twin arm would be vacuous; `primary_2h`
computes only stratified + raw (no twin branch at all, not a
zero-valued one). `WORLDS = ("INSUFFICIENT_DATA", "CONFIRMED",
"NOT-CONFIRMED")`.

**`run()`** mirrors `analyze_2g.run`'s collect-everything shape:
`check_frozen_2h` first, then a new `require_prereg_2h` (2h's stand-in
for 2g's `require_seal` — there is no stage-1 predictor build for 2h,
so there is nothing to seal; both predictors, the sampler primary and
the probe competitor, were fixed before this experiment's design was
written, so the only live gate is the freeze tag `exp2h-preregistered`
itself), the checkpoint manifest (sha-pinned), the referents manifest
(sha-pinned, this task), an optional power record (`power_sha=None`
by default — skipped entirely rather than attempted-and-failed, since
`power_2h.json` does not exist until Task 3 runs `power_2h.main()`),
the battery, 2d's floors, the rung-set re-derivation, a fresh label-gate
re-check (`labels_2g.check_label_gates`, defensive, mirrors 2g),
the verify criterion, and 2g's sealed predictor (`PREDICTOR_2G_SHA`,
already hard-pinned in `battery_2h.FROZEN_2G_SHA256` and re-checked
here via `pr.load_predictor`). Then gate 1 (`gate1_failures_69`) and
the halt marker, then the 34-rung sweep (`load_sweep_69`, reusing
`analyze_2g.step_record_failures` UNCHANGED — verified at the call
site: `PYTHIA_SHAS["6.9b"]` exists and `step == 143000` compares equal
regardless of which module's constant supplies the literal).

On success: `outcomes_69`/`rung_level_69` (local re-derivations of
`analyze_2g.outcomes`/`.rung_level` — both are bound to
`bg.trained_steps(size)`/`bg.FINAL_STEP`, which have no 6.9b entry in
`battery_2g.GRID`) over all 34 rungs (dial a); primary = sampler
counts at 1b on R_69 (`battery_2h.sampler_counts`, wrapped into the
predictor-cell shape `cells_for` expects via a new `_scores_predictor`
helper) against `primary_2h` (drops the twin computation entirely —
built from `analyze_2g.cells_for`, which is a pure function of its
arguments, not bound to any exp2g-only global). Secondaries, all
non-gating (`collect()`ed independently, a failure becomes
`{"failed": reason}` without losing the verdict): `probe_competitor`
(2g's sealed scores through the same statistic), `probe_beyond_sampler`
(composite strata = base stratum | sampler's own v>0 bucket — 2g's own
construction, unchanged direction), `sampler_beyond_probe` (the mirror
— 2h's own, since 2g never needed it: composite strata = base stratum
| the probe's own median-split bucket, since probe scores are
continuous log-probabilities with no natural zero cut, unlike the
sampler's raw count), `replication_410m`, `first_correct_outcome`
(y = last trained step + 1 − first-correct step, monotone in
earliness), `beyond_410m_1b` (design §5's one exploratory texture —
partial concordance in strata of the 410m count, the closest committed
thing to a model-specific signal), `rung_level` (s* table +
`mean_sampler_rate_1b` in place of 2g's probe-specific
`probe_margin_1b`, + spearman point over the eight R_69 rungs),
`flat_rungs` (the 26 rungs outside R_69) and `step0_counts` (all 34).

**Disclosed design decision — the two composite-strata directions.**
The design doc names both "probe-beyond-sampler and sampler-beyond-
probe" (§ Task 2 brief) but only specifies 2g's existing construction
for one direction. `probe_beyond_sampler` reuses 2g's exact
construction (bucket on the SAMPLER's v>0, a natural binary cut).
`sampler_beyond_probe` has no such natural cut on the probe's
continuous log-probability scores, so it uses a per-rung median split
— a reasonable, disclosed choice, not a frozen one; if this reads
wrong at freeze time it is a one-line change isolated to that helper.

**Disclosed design decision — the 3 exp2g data files stay in
`FROZEN_2G_SHA256`, not duplicated in the referents manifest.** 2g's
own architecture splits CODE pins (`FROZEN_IMPORT_SHA256_2G`, 14
entries, all code) from DATA pins (`referents_2g.json`, e.g. 2f's
`verdict.json`) for FOREIGN experiments. Task 1's `battery_2h.py`
already mixed 3 of exp2g's DATA files (predictor.json,
checkpoints_2g.json, referents_2g.json) into `FROZEN_2G_SHA256`
alongside the 7 code files — a deviation from that split, but already
committed, tested, and load-bearing (checked eagerly by
`check_frozen_2h()` at the very top of `run()`, the same position
2g's own `check_frozen_imports_2g` occupies). Re-litigating Task 1's
structure mid-Task-2 risked breaking its committed tests for no
executable gain (both mechanisms sha-pin the same bytes). Left as is,
flagged here rather than silently resolved either way. The referents
manifest DOES double-pin 2h's own `checkpoints_2h.json` and
`hub_inventory_69.json` even though `checkpoints_2h.json` is also
pinned directly via `manifest_sha` — this mirrors 2g's own precedent
exactly (`referents_2g.json` lists `checkpoints_2g.json` and
`hub_inventory.json` too, despite `CHECKPOINTS_SHA256` already pinning
the former directly).

**`gate1_failures_69`** mirrors `analyze_2g.gate1_failures`'s pattern:
size, the full 34-rung list, `model_sha`, per-rung counts vs
`FINAL_COUNT_PIN_69`, tensor-digest equality between the 2c and 2h
loader paths, zero continuation diffs, and — 2h's own field, since
there is no predictor seal to check here — `prereg_tag ==
PREREG_TAG_2H` stamped on the record. This field name
(`digest_2h_path`/`continuation_diffs_2h_path`/`prereg_tag`) is a
contract Task 3's runner must write to; documented here for that
task.

**`make_referents_2h.py`**: 89 files (34 item files + 34 m4-6.9b
records + 16 of 2d's committed main-tier `.draws.jsonl.gz` files at
1b/410m for R_69's 8 rungs — exactly what `sampler_counts` opens, no
sibling `.json` tier-record file — + the 5 double-pinned files above).
Verified: `referent_files_2h()` returns 89 paths, all exist on disk.
Built and pinned: `referents_2h.json` sha256
`84e46d1c9d672b330d69694afb694a9ff3aa70b8476af8c0d24c040fe5a5efd7`
(now `analyze_2h.REFERENTS_2H_SHA256`).

**`verify_referents_2h.py`**: 8 checks (frozen-2g pins; R_69 + m4
pins; checkpoint manifest rebuild + sha + hub step143000; sampler_counts
vs `analyze_2g.sampler_counts_1b` on R_28 ∩ R_69; referents_2h.json
literal sha + idempotent rebuild; the tree on literal inputs incl.
boundaries and both named notes; gate-1/prereg-tag refusals fire on
mutated records; stage artifacts absent + no stray mutation backups +
constants == stats_2g's). Ran cold: 8/8 pass.

**`power_2h.py`**: 2g's simulation shape with x REPLACED by the real
committed 1b sampler counts (`battery_2h.sampler_counts`) instead of a
jointly-simulated variable — most items are x=0 (real zero-inflation);
y is generated from a latent w = rho·rank(x) + sqrt(1−rho²)·noise
(rank-normalized so rho has a comparable meaning across rungs on very
different count scales), through the same
positive-count-then-rank-to-step assignment 2g uses
(`_ranks_to_counts`, re-declared locally rather than importing 2g's
private name). No twin arm. `N_SIM=1000`, `N_PERM_POWER=500`,
`D_TARGETS=(.10,.15,.20)`, `BAR=.75`, `DECLARE_AT=.15` — all 2g's
values. Exercised at small n (`simulate_cells_69` respects `n_pos`
exactly and leaves x untouched byte-for-byte; `calibrate_rho` is
monotone at n_cal=5; `power_at` runs end to end through
`verdict_tree_2h`). **`main()` was NOT run in this task** —
`power_2h.json` does not exist; `POWER_2H_SHA256` stays `None` in
`analyze_2h.py` until Task 3 runs it detached and pins the sha.

**Worlds** (`tests/full_shape.py`): x is NEVER synthesized — every
world calls the real `battery_2h.sampler_counts("1b", R_69)` against
the real committed 2d draws; only the synthetic 6.9b sweep varies, via
a per-rung ranking latent built from that real x (`rank` /
`independent` / `inverted`), with final-step counts forced to equal
`FINAL_COUNT_PIN_69` on all 34 rungs so gate 1 passes on the world
exactly as it must on the real tree. Six worlds, all landing on the
plan's specified terminal: W1 CONFIRMED (rank, T=0.98, p≈.005 at
n_perm=200), W2 NOT-CONFIRMED independent, W3 NOT-CONFIRMED inverted
("inverted" named, T=−0.73), W4/W5/W6 INSUFFICIENT_DATA via the three
distinct routes named in the plan (missing step 40000; HALTED marker;
wrong `manifest_sha` passed to `run()`). `add3_mid` (final count 19)
comes back `thin` in every non-insufficient world, exactly as design
§4 discloses — the eligibility floor bites at the primary-time n_pos
check, not at rung-set construction.

**RED/GREEN.** Tests were written interleaved with each module (the
world builder, gate/step-record helpers and the tree needed to exist
before their own tests could exercise anything beyond an ImportError)
rather than strictly test-file-first; every test was run against the
finished module and would fail against an absent/earlier version —
confirmed directly for `load_sweep_69` (a first draft of
`test_load_sweep_69_reuses_step_record_failures` failed with
`FileNotFoundError: checkpoint record missing` because the test itself
omitted writing the `_checkpoint.json` sidecar for the non-final step;
fixed in the test, not the implementation). Full suite: `pytest experiments/exp2h/ -q` → **37 passed** (15 from
Task 1's `test_battery_2h.py` + 22 new: `test_analyze_2h.py` 13,
`test_power_2h.py` 5, `test_full_shape_2h.py` 4 — a module-scoped
fixture running all six worlds once). `experiments/exp2g/tests/`
(87 passed, 1 skipped, 5 deselected, run separately from its slow
`test_full_shape.py`, which then passed on its own — 5 passed, 71 s)
still passes cold: 92/93 total (1 skip), confirming this task touched
nothing frozen. `python -m experiments.exp2h.analyze_2h` against the real,
unmodified repo tree returns INSUFFICIENT_DATA with exactly three
named failures (no prereg tag, no gate 1 record, no sweep record) —
the expected state before Task 3's sweep runs.

Zero model contact, zero network throughout. Commit follows this
entry.
