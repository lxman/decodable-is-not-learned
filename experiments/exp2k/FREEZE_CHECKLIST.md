# Exp 2k — Freeze Checklist (the adversarial freeze, fresh eyes, worked 2026-08-29)

The build ledger (`PROGRESS.md`) is the comparison; nothing here is
ticked until re-run in a fresh process (`PYTHONDONTWRITEBYTECODE=1
~/emergence-lab/.venv/bin/python …`). Assignment (2j's, verbatim): find
THE CLASS DEFECT — the defect that would silently DECIDE the verdict —
close what is found ADDITIVELY (a new refusal, a new pin, a new test, a
new disclosure; never an accepted dial: k = 256, seeds 0–3, sizes 1b
then 410m, R_CAP, 2g's strata, T ≥ .10 / α .01, the tree, S1–S7), and
leave a ratification ledger. The design doc is NOT edited here; slips
go to Michael as exact §-level wording.

ZERO MODEL CONTACT and zero network throughout. The tier, rehearsal and
campaign tools were exercised only against fakes and synthetic worlds;
no weight was loaded, no checkpoint fetched.

Baseline at the build's close (`a6e51e3b`): whole-directory suite 156
fast + 5 world = **161 passed, 1 skipped**; referent battery 12/12;
mutation 83 accounted for (82 real killed + 1 documented equivalent);
read sweep 4,389 paths / 0 unpinned; `FROZEN_SHA256_2K` 36,
`IMPORTED_SHA256_2K` 32, manifest 2,649 files.

## Standing adversarial assignments (worked FIRST, cold)

- [x] The class defect, six lineages: (1) every verdict input pinned or
      re-derived at analysis time (3c A / 3d `answer_type`) — swept,
      clean; (2) every tree the runner/seal/power can leave reaches a
      frozen terminal (2d F-1 / 2h F-1) — **FOUND, F-1**; (3) no
      self-consistent-only coverage claim (3d F-2) — **FOUND, F-3**;
      (4) nothing attested that could be measured (2i F-1 / 2j F-2) —
      **FOUND, F-2**; (5) the import surface pinned (2j F-1) — present
      from commit one, entry and exit, cleared with evidence; (6) the
      tag binds the instrument (2h F-3) — exercised against real git in
      a real temp repo, holds.
- [x] The brief's 19-item attack list — every item CLOSED / CLEARED /
      DISCLOSED with a demonstration.
- [x] The SDD ledger's deferred minors and rulings — triaged, each
      closed, cleared or disclosed with a reason.
- [x] Cold re-runs: suite, worlds (every terminal), totality, cold
      battery, mutation (both passes through the committed harness),
      read sweep, two-process determinism on a world.
- [x] Ratification package: findings + disclosures + the exact §-level
      doc wording.

## THE CLASS DEFECT: FOUND (F-1)

**F-1 — the halt scan enumerated ONE of the two artifacts a gate-1 fire
leaves, and the tree carrying only the other reaches a real verdict.**
2d F-1 / 2h F-1's lineage: a tree the runner can leave that the
analyzer's terminal enumeration does not reach.

`run/tier_2k.run_rung`, on the first seed-0 mismatch, writes the
evidence file `<rung>.HALTED.jsonl.gz` (the rows sampled up to the
fire) FIRST and the marker `<rung>.HALTED` SECOND, then raises.
`battery_2k.halt_markers` globbed `*/*.HALTED` only — which does not
match `*.HALTED.jsonl.gz`. A kill inside that window, or a failed
marker write, leaves the evidence file with no marker. Nothing then
refuses:

* the runner's `_refuse_if_halted` sees no marker, and `run_rung`'s
  skip-if-exists reads the NORMAL record+draws pair, not the halted
  one, so a resumed campaign re-samples the rung;
* if the retry clears gate 1 (a transient fire — the only case that
  gets this far) the tier completes;
* `run/seal_2k.seal_predictor` seals it (its halt check is the same
  function), and the stray gz is swept into the seal's `files` table
  by `tier_dir.rglob("*")`, attested and bound like any other file;
* `analyze_2k.run()`'s halt scan — the FIRST thing it does, 2d F-1's
  own lesson — sees nothing.

The verdict then ships DENSITY or NOT-DENSITY over a campaign that had
a gate-1 fire, with the fire's own evidence sitting in the tree.

**Demonstration (verbatim).** On a complete `world="density"` tree, one
file added and nothing else touched:

```
$ gzip a one-row stub to results/k256/1b_trained/sub_base8.HALTED.jsonl.gz
BEFORE
   halt_markers() sees: []
b stale HALTED.jsonl.gz, no marker: DENSITY None T=0.9831911740571431 | nfail=0 []
AFTER
   halt_markers() sees: ['sub_base8.HALTED.jsonl.gz']
b stale HALTED.jsonl.gz, no marker: INSUFFICIENT_DATA None T=None | nfail=1
   ['2k tier HALTED marker present: 1b_trained/sub_base8.HALTED.jsonl.gz']
```

The control (same world, no added file) is DENSITY, T =
0.9831911740571431, 0 failures before and after — the closure is
one-directional.

**Closed additively** (`6abd339d`): `battery_2k.halt_markers` globs both
names. All three call sites read this one function, so the sha-pinned
`run/seal_2k.py` is closed without editing it (no re-pin, no manifest
rebuild). Two existing tests updated to the widened scan; one
regression test added
(`test_halt_markers_sees_the_evidence_gz_without_its_marker`); one
mutant added that narrows the glob back and is killed by the fast
modules. No accepted dial touched.

**What was NOT changed, and why.** The runner still writes the gz
before the marker. Reversing the order would leave the opposite window
(a marker with no evidence), which is the safe direction but is a
behaviour change to a tag-bound blob for no gain now that either
artifact refuses. DISCLOSED rather than reordered.

## Findings

### F-2 — the power record's simulation claims were attested and never compared

2j F-2's lineage, one experiment over. `load_power_2k` bound the record
to the sealed predictor by `predictor_sha256`, to R_CAP by its rung
list, to the 7B grid by `n_trained_steps`, and checked
`declared_status` is one of 2i's three. Everything the simulation
actually DID — which rungs survived the degeneracy screen, what
positive-outcome floor each rung was given, which bar and α the firing
rule used — was attested to nothing. `declared_status` is the field
that picks between NOT-DENSITY's "a measured absence" licence and
NOT-DENSITY_UNDERPOWERED's "not detected at this resolution", so this
is a verdict-level output.

**Demonstration.** On a complete density world, a power record left
coherent on all four checked fields and absurd on the rest —
`declared_status "POWERED"`, `rungs_simulated []`, `dropped_degenerate`
= all nine rungs, `n_pos_lower_bound` all zero, `t_bar 0.0`, `alpha
1.0`, `n_sim 1`, i.e. POWERED declared over a simulation of nothing, at
no bar:

```
BEFORE  verdict: DENSITY | declared_status: POWERED | nfail: 0
AFTER   verdict: INSUFFICIENT_DATA | nfail: 6
  - 2k power claims: dropped_degenerate [all nine] != the re-derivation on x_A^(256) []
  - 2k power claims: rungs_simulated [] != the surviving rungs [all nine]
  - 2k power claims: n_pos_lower_bound {…: 0} != 2i's committed stage1_final counts
  - 2k power claims: t_bar = 0.0, the firing rule's 0.1
  - 2k power claims: alpha = 1.0, the firing rule's 0.01
  - 2k power claims: thin = True against 9 surviving rung(s)
```

**Closed additively** (`90cd05d1`): `check_power_claims_2k`, run after
the primary on the SAME `x_A^(256)` the primary just used —
`dropped_degenerate` and `rungs_simulated` re-derived through
`analyze_2i._degenerate_rungs`, `n_pos_lower_bound` against 2i's
committed `stage1_final` counts, `t_bar`/`alpha` against the firing
rule's own constants, `thin` against the surviving rung count; a record
that attests none of them is refused as uncheckable. A record written
by the real `power_2k.main` satisfies all six by construction (it calls
`power_2i._one_test_power` with exactly these inputs, and that function
writes `t_bar`/`alpha`/`thin` even on its all-degenerate early return).
World W14, four totality tests, eight fast unit tests, two mutants.

**Residual, DISCLOSED.** `predictor_sha256 == seal["sha256"]` proves
the record is a claim about the sealed FILES; the six re-derived fields
now tie it to the sealed COUNTS through the degeneracy partition and
the endpoint floor. Neither is a hash of the x vector the simulation
consumed. Writing one would mean editing `power_2k.py`, a sha-pinned
file, for a residual the seal tag already binds; not done, stated.

### F-3 — the seal's `files` table was a coverage claim checked only against itself

3d F-2's lineage (a zero diff count over a truncated comparison is not
evidence). `seal_failures_2k` hashed every entry of `files` against
disk and recomputed the composite `sha256` FROM that same table — both
checks are satisfied by any table, including an empty one.

**Demonstration.** `files` emptied, `sha256` recomputed over `{}`, and
the power record's `predictor_sha256` re-pointed at the new composite
(one edit, because `load_power_2k` binds them):

```
BEFORE  DENSITY, T = 0.9831911740571431, 0 referent failures
        — from a seal attesting no file at all
AFTER   INSUFFICIENT_DATA
        2k seal: files attests 0 path(s) and does not cover 36 of the 36 tier files
DROP ONE ENTRY (35 of 36, sha recomputed, power re-pointed)
BEFORE  DENSITY   AFTER  INSUFFICIENT_DATA — "does not cover 1 of the 36 tier files"
```

**Closed additively** (`7111e84f`): the table must cover the 2 × 9
record+draws paths. Honest weight: this was **inert, not decisive** —
the seal TAG binds the same 36 paths through `_seal_paths_2k`'s rule
set, which is independent of the seal's own `files` dict, so the tier
bytes were never actually loose. A coverage claim still has to be a
claim about something.

### F-4 — gate 1 covers seed 0; nothing looked at seeds 1–3 as streams

Not a defect in the instrument as built (exp3's `sample_item` gives
each seed a fresh `torch.Generator().manual_seed(stream_seed(...))`, so
the streams are independent by construction) — a fault mode that would
produce a PLAUSIBLE VERDICT rather than a refusal, which is the shape
this freeze exists to catch. If a runner or sampler fault handed the
same 64 draws to more than one seed, `x_A^(256)` would be an exact
multiple of `x_A^(64)`, hence rank-identical inside every stratum,
hence `T` back at 2i's own .0949 — a clean NOT-DENSITY delivered over a
campaign that took no new draws. Gate 1, the record pins, the tallies
re-derivation and the seal all pass on such a tree (the tallies simply
match the copied stream).

**Demonstration.** One cell's seed-2 stream replaced by a byte-copy of
seed 0 on all 500 items, with the record's seed-2 tally updated to
match:

```
BEFORE  DENSITY (the seal's own counts check fires only because the
        world's seed-2 draws differed; on a real campaign the runner
        would have written the copy into the seal too)
AFTER   INSUFFICIENT_DATA
        2k tier 1b/antonym seed-stream census: ValueError: seed 2
        reproduces seed 0's stream on all 500 items — the cell carries
        no independent draws
```

**Closed additively** (`7111e84f`): a per-cell census of items whose
seed-s stream equals seed 0's, printed in
`referents.seed_stream_census_2k` (`{'1': 0, '2': 0, '3': 0}` on a
clean cell); refusal ONLY on the whole-cell copy (all 500 items).

**The refusal is priced** (2j's "unconditional pin priced" precedent).
Measured on 2d's committed draws at these exact cells: on all nine
R_CAP rungs at BOTH sizes, **0 of 9,000 items has a constant 64-draw
seed-0 stream**. A second, independently seeded generator reproducing
seed 0's 64 draws on all 500 items of a rung is therefore not
producible by this model at T = 1.0 untruncated — only by an instrument
fault. Partial duplication is printed and never gates, so a legitimately
peaked item cannot cost a campaign.

### F-5 — design §3.2's fixture was deferred at the build; the freeze wrote it

Not a defect — a spec item the build ledgered as a deviation and the
brief carried as a known doc slip. §3.2 requires a fixture (a fake
model with a recorded generator) proving that seed 0's bytes do not
depend on which other seeds share the `sample_item` call, so that gate
1 is a statement about the stream formula and the weights, not about
call shape. Without it the claim rested on reading the sampler.

`experiments/exp2k/tests/sampler_call_shape_2k.py` (`286097ae`):
exp3's real frozen `sample_item`, a fake model whose forward is a pure
deterministic function of the ids handed to it, a fake tokenizer, no
weights, no network. Standalone — the only 2k module that imports
`torch`, and deliberately without a `test_` prefix so pytest never
collects it and the committed suite stays weight-free (the build's
standing constraint).

```
production call shape seeds=[0, 1, 2, 3]: 256 draws, 60 distinct seed-0 draws
  seed-0 block vs seeds=(0,)           IDENTICAL
  seed-0 block vs seeds=(0, 1)         IDENTICAL
  seed-0 block vs seeds=(0, 1, 2)      IDENTICAL
  seed-0 block vs seeds=(3, 2, 1, 0)   IDENTICAL
PASS: seed 0's bytes are independent of the seeds tuple
```

The reordering case is the one that matters most: seed 0 LAST still
reproduces the same block, so the property is per-seed generator
independence and not merely "seed 0 runs first". The fixture also
asserts seeds 1–3 are not copies of seed 0 (F-4's shape, on the fake).
Doc slip (b) is now a pointer, not a deviation.

### D-1 — a verdict produced with a test-only bypass said nothing about it

`run()` keeps three test-only injection points (`frozen_check`,
`imports_pinned=False`, `referents_sha=False`). No production caller
passes any of them (`__main__` takes the defaults; grep over the
repo: the only callers passing them are `tests/` and the two scan
tools, each documented). But a verdict.json written with a pin skipped
was indistinguishable from a fully-pinned one except by its (empty)
failure list.

**Closed additively** (`7111e84f`): `referents.pins_active` records
`{"frozen_modules": …, "import_surface": …, "referent_manifest": …}`.
On the real analyzer run all three are `true`; a world run shows
`import_surface`/`referent_manifest` false, on the face of the record.

## Attack-list disposition (the brief's 19)

| # | item | disposition | evidence |
|---|---|---|---|
| 1 | gate 1's two legs agree on "the committed row"; one altered byte in a sealed 2k file caught by the analyzer | CLEARED | every world's seed 0 IS the real committed 2d row, so W8 (`missing="gate1_diff"`) already alters a byte of a real 2d stream inside a sealed 2k tree; the analyzer refuses at `2k tier 1b/sub_base8 gate 1 re-derived` AND at the seal's per-file sha. Re-run at the freeze HEAD (worlds 14/14). |
| 2 | seed order inside a row: `counts_at_k(bits,64) == block_counts(bits,0)` | CLEARED | `bits_2k` extends in `SEEDS_2K` order and is the ONLY bits producer (`grep`: `bits_2k` is called by `load_tier_2k._bits` and by nothing else; the worlds go through `tier_record_2k`/`load_tier_2k`, the seal through `load_tier_2k`). Asserted directly by a new fast test and by `test_ladder_2k_k64_equals_block0_and_k256_equals_full`; mutants 3, 4, 5 (prefix, block offset, seed order reversed) all killed. |
| 3 | the comparison gate is exact on counts, not only on T | CLEARED | the count-equality loop is mutant "run()/_cmp: the x_A^(64)-vs-2d comparison loop removed"; it SURVIVES the fast modules and is killed by `test_comparison_gate_x64_vs_2d_mismatch_detected` under `--totality` (round-1 log). |
| 4 | 410m absent → INSUFFICIENT_DATA; 410m gating for completeness, non-gating for the verdict | DISCLOSED | `load_tier_2k` runs for both sizes and any missing cell is a failure (design §3.5 "missing or truncated tier"). W5 deletes a 1b record; a 410m-only deletion behaves identically. Doc slip (c). |
| 5 | the halt scan precedes every loader; a marker at 410m after a clean 1b tier | CLEARED | probe (a): marker at `410m_trained/odd6.HALTED` on an otherwise complete tree → INSUFFICIENT_DATA, single failure `2k tier HALTED marker present: 410m_trained/odd6.HALTED`, primary None. |
| 6 | the seal tag binds the union; a stray file under `results/k256/` | DISCLOSED | probe (c): a `notes.txt` added to the tier dir AFTER the seal is not in `files`, not in `_seal_paths_2k`'s rule set, and inert — verdict DENSITY, 0 failures. A stray present AT seal time is swept in by `rglob` and IS bound. A stray added after the SEAL TAG and listed in `files` would drift and refuse, but the seal cannot be rewritten (`seal_2k` refuses if it exists). Behaviour is as the brief predicts; disclosed, not changed. |
| 7 | `seal_failures_2k` reads `counts_by_k[size][str(k)]`, the seal writes `str(k)` | CLEARED | `seal_2k` writes `by_k[size] = {str(k): …}`; the checker reads `.get(str(k), {})`. `test_seal_counts_by_k_altered` corrupts `["1b"]["64"]` and is caught; mutant "the counts_by_k ladder check removed" killed. |
| 8 | S3's `bi.SIZE_PRED` is a dict key only | CLEARED | `_block_reading` → `t_only(…, size_label, …)` → `_scores_predictor_2i` builds `{"cells": {r: {size: …}}}` and `analyze_2g.cells_for` reads it back with `pr.cell_scores(pred, rung, size_pred, mode)`. The label never reaches a statistic; the values are `bits_b`'s thinned counts. |
| 9 | `placement_on_ladder` above B(64) → `[64, None]` | CLEARED + DISCLOSED | asserted in `test_analyze_2k` (`placement_on_ladder(lad, 0.30)["bracket"] == [64, None]`, and `[None, 1]` below the bottom). `k_equivalent` is `None` there by construction. Projection wording: doc slip (d) — "beyond 64" is a bracket, never a number. |
| 10 | totality: every tree the runner/seal/power can leave | CLOSED (F-1) + CLEARED | halt with marker (W7), halt with only the evidence gz (**F-1**), killed runner mid-rung (W5, "record or draws file missing"), truncated gz (W6 + `test_draws_gz_truncated_is_eof_not_a_raise` — `analyze_2i.collect_total` is the one imported, `EOFError`/`zlib.error` both routed), corrupt gz (`test_draws_gz_corrupt…`), seal present + power missing (W11), power from a different seal (W13), power with absurd claims (**F-2**, W14), truncated seal files table (**F-3**), whole-cell seed copy (**F-4**). No raise reached `run()`'s caller in any of them. |
| 11 | `predictor_sha256` vs the seal's own sha; is the post-power tier drift a gap? | CLEARED, stated | the seal FILE does not change when a tier file drifts, so `predictor_sha256 == seal["sha256"]` still holds — and the drift is refused separately by `seal_failures_2k`'s per-file sha loop (mutant "the per-file sha check removed" killed) and, on the real tree, by the seal tag's blob binding. Not a gap; F-3 removes the one way that loop could be made vacuous. |
| 12 | read sweep: 0 unpinned pre-campaign; campaign side seal-bound | CLEARED, with a coverage caveat | re-run cold at the freeze HEAD (numbers below). The caveat is real and stated: on the pre-campaign tree `run()` refuses at the missing tier, so the sweep enumerates the REFUSAL path only — the comparison gate's and secondaries' reads (2i/2g/2j `verdict.json`) never happen. All four verdict records are on `referents_2k.json`'s manifest (checked), and the success path was swept separately on a world to confirm it opens nothing outside the manifest, the frozen set and the world root. |
| 13 | determinism: `run()` twice in separate processes on a world | CLEARED | byte-identical verdict JSON, numbers below. |
| 14 | the tag binds the instrument, real git, real tag | CLEARED | a real temp repo carrying the three `INSTRUMENT_BLOBS_2K`, committed and annotated-tagged `exp2k-preregistered`: clean → binds 3 blobs; post-tag edit to `run/tier_2k.py` → REFUSED; post-tag edit to `analyze_2k.py` → REFUSED; tag deleted → REFUSED. `tier_2k.run` calls `require_prereg_2k` FIRST, before any frozen check, seal check, halt scan or model load. |
| 15 | label prefixes disjoint, and disjoint from 2i's and 2j's | CLEARED | `test_collect_total_labels_are_prefix_disjoint_and_disjoint_from_2i_2j` (AST + f-string harvest) passes at the freeze HEAD with the two NEW labels ("2k power claims", "2k tier {size}/{rung} seed-stream census") in the set. |
| 16 | `s1_blocks` SD with a `None` T | CLEARED | `finite` filtering: `mean/min/max` over the finite T's, `sd` `None` when fewer than two are finite. New fast test drives a degenerate block through it. |
| 17 | JSON strictness: `allow_nan=False` against a NaN per-rung CI | CLEARED | the write path is `json.dumps(an2i._json_safe(v), …, allow_nan=False)` and `_json_safe` maps every non-finite float (including `np.floating`) to `None` recursively through dicts, lists and arrays; keys are never non-finite (every dict in the verdict is keyed by `str` or `int`). New fast test writes a verdict-shaped object carrying NaN/±inf at four depths. |
| 18 | the rehearsal writes nothing | CLEARED + DISCLOSED | `rehearse_2k.run` snapshots `<out_root>/results` before and after and raises if anything appeared; it prints to stdout only. `real_loader` → exp3's `_load_model` writes to the HuggingFace cache, outside `results/` and outside the repo — disclosed, unchanged. |
| 19 | the pre-tag disclosure list is complete | CLOSED by doc slip (a) | the build's six `analyze_2k.run()` executions on the real tree are correctly recorded; the freeze adds its own, counted exactly below. |

## The SDD ledger's deferred minors and rulings, triaged

| item | disposition |
|---|---|
| T1: `matched_k_256`'s local `numpy` import | CLEARED — a function-local import of an already-loaded module; `numpy` is not under `experiments/`, so it is outside the import scan by design. No change. |
| T1: `_cells_of`'s `tiers` branch dead on all five committed maps | DISCLOSED — the branch is a hard-error guard for a map shape none of the five has; its alternative is silently skipping a map the freshness proof must read. Documented in the docstring and in `PROGRESS.md`. Keep. |
| T2: `frozen_from_disk`'s silent `is_file()` filter | CLOSED at the build (round 1) — `strict=True` default raises; verified at the freeze: `frozen_from_disk()` re-prints the 36-entry literal byte-for-byte (cold re-runs below). |
| T2: short-seed-0-stream branch untested; halt marker at the OTHER size untested; `run()`'s own `_refuse_if_halted` untested | CLOSED — the other-size halt is attack item 5 (demonstrated); `run_rung`'s coverage-diff branch is mutant "the per-item coverage diff (wrong draw count) no longer detected" (killed); `_refuse_if_halted` is mutant "run_rung: _refuse_if_halted removed" (killed) and is now also exercised through the widened F-1 scan. |
| T2: `run_rung`'s dead `committed_root` parameter | DISCLOSED — an unused keyword in a tag-bound blob's signature, verbatim from the brief. Removing it is a signature change to a blob the tag will bind for no gain; left, named here. |
| T2: `PROGRESS.md`'s Task 2 entry still describes the pre-fix filter | CLOSED — corrected in the freeze's ledger entry. |
| T3: `test_check_imports_2k_excludes_test_helpers` is a weak assertion | CLEARED — its positive counterpart is `verify_referents_2k` item 12 (`check_imports_2k()` passes for real in a process that has imported every stage tool), re-run cold 12/12 at the freeze. |
| T3: `s1_blocks` hardcodes `range(4)` | CLOSED at Task 5 (`len(bk.SEEDS_2K)`) — verified by reading the current source. |
| T3: `make_referents_2k` docstring named a nonexistent `allow_missing` | CLOSED at Task 5. |
| T3: unused `T_BAR` import | now USED — `check_power_claims_2k` compares the power record's `t_bar` to it. |
| T3: the exit import check runs before the secondaries | CLEARED — the primary, the comparison gate and the block gate all complete BEFORE the exit check, so every verdict-deciding computation is inside the entry/exit window; the secondaries import nothing lazily (swept: every name they touch is a module-level import of `analyze_2k`). Stated rather than moved: moving the check after the secondaries would let a secondary's own failure flip the verdict, which §5.2 forbids. |
| T4: `load_tier_2k`'s call sites not `collect_total`-wrapped | CLOSED at Task 5; re-verified by `test_load_tier_2k_forced_exception_now_lands_gracefully`. |
| T4: `_gate`'s "gate 1 coverage" arm unreachable | CLEARED as dead defensive code — `read_rows_2k` pins coverage at 500 before `_gate` runs, and `committed_rows` pins the other side. Kept; named. |
| T4: W10 read `pin_a` after mutating on-disk A | CLOSED at Task 5 (captured before). |
| T4: the 9-key sampling block duplicated in `seal_2k` and `seal_failures_2k` | CLEARED, deliberately NOT unified. The failure direction is one-way: `seal_failures_2k`'s `want_sampling` is the authority on the verdict path, so a disagreement can only REFUSE, never decide. The two are exercised against each other by every world (the seal is written by the real `seal_2k.seal_predictor` and read back by `seal_failures_2k`), and `test_seal_sampling_block_altered` plus the "sampling block" mutant hold the comparison. Merging them into one literal would delete the cross-check and require editing a sha-pinned file for no verdict gain. |
| T4: `verify_referents_2k.main` returns on the first failure | DISCLOSED — fail-fast in a cold diagnostic tool, off the verdict path; collecting all twelve would be friendlier but the file is on `IMPORTED_SHA256_2K` and editing it costs a re-pin for a diagnostic nicety. Named, not changed. |
| T5: `PROGRESS.md:722`'s uncited "82/82" summary sentence | CLOSED — superseded by the freeze's own sourced tally. |
| T5: `--with-campaign` inert while `N_FILES_2K` is pinned; the docstring overstates | DISCLOSED — `build(with_campaign=True)` raises on the `n_files` check unless the caller passes `n_files=`; the CLI path is descriptive only and nothing in the pipeline consumes it. Doc-level, in a sha-pinned file; named, not changed. |
| Ruling (branch = master), Ruling (Task 2 expected-red), Ruling (fold two minors), Ruling 3 (`frozen_check` bypass), Ruling (no Task-4 fix round), Ruling (fold the §2 count correction) | all CLEARED as executed; Ruling 3's bypass is the subject of D-1 (now stamped into the record) and was verified to have no production caller. |

## Cold re-runs at the freeze HEAD

Every one in a fresh process from the repo root with
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python`.

| run | result |
|---|---|
| whole-directory suite (`experiments/exp2k/tests`, nine modules + the standalone fixture) | **185 passed, 1 skipped** (was 161 + 1 at the build's close) |
| worlds + totality re-run after the last edit | **50 passed** (5 world tests over **14 worlds**, all three terminals + both annotations reached and every refusal reason asserted; 45 totality tests) |
| cold battery (`verify_referents_2k.py`) | **12/12**, cold, on the real tree; item 10 prints "seal and power record: absent — pre-campaign" |
| mutation, fast pass (`mutation_freeze_fast.log`) | **90 mutants, 72 killed, 18 survivors** |
| mutation, totality pass (`mutation_freeze_totality.log`, `--totality --only 29,30,31,32,35,36,37,48,80,81,82,83,84,85,86,89,90`) | **15/17 killed**; survivors 80 and 85 — both the freeze's own new `collect_total` sites, closed with two tests (the census's failure LABEL pinned, not only its message; a forced-exception test for `check_power_claims_2k`) |
| mutation, second totality pass (`mutation_freeze_totality2.log`, `--totality --only 80,85`) | **2/2 killed, 0 survivors** |
| **mutation, accounted** | **90 = 89 real, all killed (72 + 15 + 2), + 1 documented equivalent (#13, `matched_k_256`'s cap tie — the build's proof stands)**, entirely from the three committed logs |
| read sweep (`tests/read_sweep_2k.py`), real pre-campaign tree | **4,389 distinct paths / 10,079 read calls; UNPINNED 0**; referents 2,650, frozen 50, instrument 3, sha_pin_at_load 2, seal-bound-absent 1, stdlib/venv 1,683; 0 writes |
| read sweep, SUCCESS path (a world — the coverage the pre-campaign sweep structurally cannot reach) | **4,686 distinct paths; UNPINNED 0** — world root (temp) 888, manifest 1,110, frozen/pinned 50, instrument 3, sha_pin_at_load 2, stdlib/venv 2,633. Verdict DENSITY, all 8 secondaries computed, 0 secondary failures |
| import scan (`tests/import_scan_2k.py`), real tree | re-emits **32 modules, byte-identical to `IMPORTED_SHA256_2K`** |
| determinism ×2, separate processes, on a world (`n_perm=30`) | **byte-identical verdict JSON**, sha256 `fffbc2deeba9c3c584ace8e523b437a059eff37c30bee381b9151dd0346ac1d1` both times |
| `frozen_from_disk()` vs the pinned literal | **36 modules, identical: True**; `N_FILES_2K` 2,649 and `referents_2k.json`'s own sha `f00dfe78…` both match, manifest refusals `[]` |
| the §3.2 fixture (`tests/sampler_call_shape_2k.py`) | **PASS**, seed 0's 64 draws identical across five call shapes incl. `(3, 2, 1, 0)` |
| one altered byte in a SEALED 2k draws file (attack item 1) | seed 0 → `2k tier 1b/sub_base8 gate 1 re-derived: … 1 seed-0 draw(s) differ from 2d's committed bytes`; seed 2 (outside gate 1) → `2k seal: … missing or changed since the seal`. Both INSUFFICIENT_DATA — the layers are complementary, not redundant |

**Freeze-time executions of `analyze_2k.run()` on the REAL tree: three**
— `tests/read_sweep_2k.py` once, `tests/import_scan_2k.py` twice (once
printed, once redirected to compare its emitted literal against the
pinned one). All three landed INSUFFICIENT_DATA on the missing tier and
printed no T. Every other number in this checklist came from synthetic
worlds or from 2d's committed draws. Doc slip (a) carries the count.

## Ratification package — doc slips (the design doc UNTOUCHED)

Exact §-level wording for Michael. Nothing here is applied; the design
doc is byte-identical to its state at the build's close.

**(a) §2, the pre-tag disclosure paragraph, after "…that number is
already public and is listed above."** Append:

> The adversarial freeze (2026-08-29) ran the analyzer on the real tree
> THREE more times as its cold re-runs — `tests/read_sweep_2k.py` once
> and `tests/import_scan_2k.py` twice (once printed, once redirected so
> the literal it emits could be compared against the pinned one) — all
> three landing INSUFFICIENT_DATA on the missing 2k tier before
> reaching a primary and printing no T, for **nine `analyze_2k.run()`
> executions on the real, pre-campaign tree in total**. Every other
> number the freeze printed came from synthetic worlds
> (`tests/full_shape.py`, whose 7B outcome is independent of x_A by
> construction) or from 2d's committed draws; none is a 2k statistic.
> The freeze's own probes ran the analyzer only against world roots.

**(b) §3.2, the paragraph beginning "The build proves with a fixture (a
fake model with a recorded generator)…"** — the build DEFERRED that
fixture (ledgered as a deviation); the freeze WROTE it and it passes,
so the sentence stands and only its record needs the pointer. The
production shape is unchanged: ONE `sample_item` call with
`seeds = (0, 1, 2, 3)`. Replace the paragraph's last sentence ("If that
fixture cannot be made to pass…") with:

> The fixture is `experiments/exp2k/tests/sampler_call_shape_2k.py`
> (written at the freeze, standalone because it is the only 2k module
> that imports `torch`, so pytest never collects it and the committed
> suite stays weight-free). It drives exp3's real, frozen `sample_item`
> with a fake model whose forward is a pure deterministic function of
> the ids it is handed, and requires seed 0's 64 draws to be identical
> across `seeds = (0,)`, `(0, 1)`, `(0, 1, 2)`, the production
> `(0, 1, 2, 3)` and the reordering `(3, 2, 1, 0)`. It passes on all
> five (60 distinct seed-0 draws, so the fake is not degenerate), and
> it also asserts that seeds 1–3 are NOT copies of seed 0 — so the
> shape that would silently make gate 1 a statement about call shape,
> or make the three new blocks fake, is caught by a committed artifact
> rather than by argument. Two things carry the claim beside it: the
> pre-tag rehearsal (dial i), which is the same proof on the real model
> for one item, and gate 1 itself, on all 288,000 committed seed-0
> draws per size. The failure direction is a HALT, not a wrong number.

**(c) §3.6, the clause "a referent manifest over every file read
(§4)".** Replace with:

> a referent manifest over every file read BEFORE the campaign (§4) —
> 2,649 files, pinned by `REFERENTS_2K_SHA256`; the campaign's own
> artifacts (the 36 tier files, the seal and the power record) are NOT
> on it and are bound instead by `exp2k-predictor-sealed` over
> `_seal_paths_2k`'s rule set ∪ the seal's own `files` table, so the
> preregistration tag is never re-cut after the campaign runs

**(d) §3.2, the sentence "A halt tree — any `.HALTED` marker, or a rung
whose record is absent or whose draws file is truncated — delivers
INSUFFICIENT_DATA…"** Replace the first clause (freeze F-1):

> A halt tree — EITHER artifact a fire leaves (`<rung>.HALTED` or
> `<rung>.HALTED.jsonl.gz`: the runner writes the evidence file first,
> so a kill or a failed marker write between the two leaves only the
> gz, and either one refuses), or a rung whose record is absent or
> whose draws file is truncated — delivers INSUFFICIENT_DATA…

**(e) §3.5, the refusal list.** Add three items to the parenthesis
(freeze F-1/F-3/F-4) and one clarification:

> …, seal `files` table not covering the 36 tier record+draws paths,
> a cell whose seed-s stream reproduces seed 0's on all 500 items, a
> power record whose simulation claims do not re-derive …

and after the list:

> Both sizes are required for tree completeness even though only 1b
> decides the primary: a missing or truncated 410m cell delivers
> INSUFFICIENT_DATA, not a 1b-only verdict.

**(f) §5.2, S3, after "…by linear interpolation in log k)."** Append:

> If T_A^(256) exceeds x_B's own T at k = 64 the placement is a
> BRACKET — `[64, None]`, with no k-equivalent — and "beyond 64 OLMo-1B
> draws" is the whole of what may be said. The projection and any
> licensed sentence say it as a bracket, never as a number.

**(g) §7, after "…the analyzer refuses if its predictor sha is not the
sealed draws'."** Append (freeze F-2):

> The analyzer also RE-DERIVES the record's own simulation claims
> before reading its declaration: the degeneracy partition
> (`dropped_degenerate` / `rungs_simulated`) from x_A^(256) and 2g's
> strata through `analyze_2i._degenerate_rungs`, `n_pos_lower_bound`
> against 2i's committed `stage1_final` counts, and `t_bar` / `alpha`
> against the firing rule's own constants. A record that attests none
> of them is refused as uncheckable. The seal's sha binds the record to
> the sealed FILES; these six bind it to the sealed COUNTS.

**(h) §5.2, S7, after "…per-rung D with CI."** Append:

> Also printed in every world, non-gating: the per-cell seed-stream
> duplication census (how many of the 500 items have a seed-s stream
> byte-identical to seed 0's; zero on a clean cell), the freeze's F-4
> record.

## Disclosures (no change asked for)

1. **The runner still writes the evidence gz before the marker.**
   Reversing the order would leave the opposite window (a marker with
   no evidence — the safe direction), but it is a behaviour change to a
   tag-bound blob for no gain now that either artifact refuses.
2. **A stray file added to `results/k256/` AFTER the seal is inert.**
   It is not in the seal's `files`, so not in `_seal_paths_2k`'s union,
   so not bound and not refused. A stray present at seal time is swept
   in by `rglob` and IS bound. The 36 required files are covered
   either way (F-3).
3. **`rehearse_2k` writes to the HuggingFace cache** through exp3's
   `_load_model`. Its assertion covers `<out_root>/results` only, which
   is the assertion that matters; the cache is outside the repo.
4. **The read sweep on the pre-campaign tree covers the REFUSAL path
   only** — `run()` stops at the missing tier, so the comparison gate's
   and the secondaries' reads never happen. All four `verdict.json`
   records they read are on the manifest (verified), and the success
   path was swept separately on a world.
5. **`predictor_sha256` is the seal's composite sha, not a hash of the
   x vector the power simulation consumed.** F-2's six re-derived
   fields tie the record to the sealed counts through the degeneracy
   partition and the endpoint floor; a hash of x would need an edit to
   the sha-pinned `power_2k.py` for a residual the seal tag binds.
6. **The 9-key sampling block is still duplicated** in `seal_2k.py` and
   `seal_failures_2k`. Deliberate: the analyzer-side copy is the
   authority, so a disagreement can only REFUSE; every world exercises
   one against the other; merging them would delete a cross-check and
   require editing a sha-pinned file.
7. **`run_rung`'s `committed_root` parameter is dead** (verbatim from
   the build brief) and `_gate`'s "gate 1 coverage" arm is unreachable
   (`read_rows_2k` pins coverage first). Both left in place, named.
8. **`verify_referents_2k.main` returns on the first failure.**
   Fail-fast in a cold diagnostic tool, off the verdict path.

## Notes for the tagger

- The three blobs `exp2k-preregistered` must bind are
  `experiments/exp2k/analyze_2k.py`, `experiments/exp2k/battery_2k.py`
  and `experiments/exp2k/run/tier_2k.py`. Only the first two changed at
  the freeze; `run/tier_2k.py` is untouched.
- No sha-pinned file was edited: `FROZEN_SHA256_2K` (36),
  `IMPORTED_SHA256_2K` (32), `N_FILES_2K` (2,649) and
  `REFERENTS_2K_SHA256` all stand unchanged, re-verified cold.
- `experiments/exp2k/mutation_freeze_fast.log` and
  `mutation_freeze_totality.log` are the freeze's two committed
  mutation logs; `mutation_build.log` / `mutation_round1.log` remain
  the build's.

