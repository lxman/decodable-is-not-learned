# Exp 2l — adversarial freeze (Task 6)

Fresh-eyes attack on the frozen instrument at `68fb7ed9` (Tasks 1–5
committed, reviewed, clean). The assignment is 2k's verbatim: **find THE
CLASS DEFECT — the defect that would silently DECIDE the verdict rather
than refuse** — and close what is found ADDITIVELY (a new refusal, pin,
test or disclosure; never an accepted dial: 13B, the grid, Tests A/B, the
median bucket, R_PRIMARY, the bars, S1–S7). Zero model contact, zero
network throughout. The design doc is NOT edited; slips go to Michael as
exact §-level wording (Ratification package, below).

Every demonstration below ran cold from the repo root under
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python`.

**Verdict of the freeze: the class defect — a defect that would silently
decide the TERMINAL — was NOT found. Five findings and one disclosure
were, each demonstrated executably and closed additively. The most
consequential, F-4, decides not the terminal but the LICENCE §6 hands to
the essay: a world that fires SHARED at T = .7052, p = .00498 on ONE
eligible rung, with `|R_PRIMARY| = 4` so the frozen THIN guard stayed
silent.**

---

## Findings

### F-4 — the THIN guard counted R_PRIMARY, not the rungs a test read

**What.** §4 says "fewer than three rungs → THIN declared in the power
record, the verdict still runs", and `verdict_2l` implemented that as
`len(r_primary) < 3`. But the rungs a test actually reads are smaller
than R_PRIMARY twice over: `analyze_2g.cells_for` drops any rung whose
outcome has fewer than `ELIGIBILITY_MIN_POS = 20` positive items (they
land in `prim["thin"]`), and `_run_test` drops any rung whose predictor
is constant inside every stratum (`dropped_degenerate`). Neither appears
in the reason string or the licensed sentence.

**Reachable, measured.** The minimum endpoint count that puts each of
2k's nine into R_PRIMARY (the smallest `k` clearing 2d's exact binomial
bar against its floor):

| rung | floor | min k clearing the bar | > min_pos (20)? |
|---|---|---|---|
| add3_mid | .006 | **9** | no |
| add_base8 | .028 | 24 | yes |
| antonym | .250 | 149 | yes |
| antonym6 | .167 | 104 | yes |
| arith_next | .020 | **19** | no |
| odd6 | .167 | 104 | yes |
| sub3_mid | .014 | **15** | no |
| sub4_mid | .006 | **9** | no |
| sub_base8 | .056 | 42 | yes |

y (the count outcome) includes the endpoint step, so `n_pos ≥` the
endpoint count — bounded BELOW by 9, not above 20. Four of the nine can
therefore enter R_PRIMARY and still be dropped by `cells_for`.

**Demonstration (world W19, `tests/full_shape.py`).** R_PRIMARY =
`['add3_mid', 'add_base8', 'sub3_mid', 'sub4_mid']` (four rungs, so
`DISCLOSURE_THIN_2L` does not fire), with add3_mid/sub4_mid capped at 12
firing items and sub3_mid at 18:

```
  verdict            : SHARED
  A eligible / thin  : ['add_base8'] / ['add3_mid','sub3_mid','sub4_mid']
                       fires=True T=0.7052 p=0.004975
  DISCLOSURE_THIN_2L in the reason: False
```

Before the closure that SHARED carried §6's full cross-family licence
with no caveat anywhere.

**Closed additively** (`analyze_2l.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2L`,
`_thin_eligible_2l`, called from `verdict_2l`): a per-test disclosure
naming what the test read and what was dropped, on the reason AND the
licensed sentence. `fires` is untouched; no dial moved. After the
closure the same world reads:

```
  fewer than three rungs actually carried Test A: it read 1 rung(s)
  ['add_base8'] — dropped as n_pos-thin ['add3_mid','sub3_mid','sub4_mid'],
  as predictor-degenerate []; the reading is THIN regardless of the power
  record's declaration, which simulates over R_PRIMARY minus the
  degenerate rungs only
```

Tests: `test_verdict_2l_discloses_a_test_that_read_fewer_than_three_rungs`
(fast), `test_w19_thin_eligible_set_is_disclosed` (world W19). Mutant
`F-4: _thin_eligible_2l never fires`.

---

### F-1 — the import-surface pin's exit check ran BEFORE the secondaries

**What.** 2j's F-1 (the eleventh methods-paper lesson) pins the resolved
module table at entry and exit of `run()`. In 2l the "(exit)" check sits
immediately after `check_power_claims_2l` — i.e. BEFORE the thirteen
secondaries S1–S7, the extra rungs and the sensitivities are computed. A
module first imported inside one of those is never on the checked
surface, and every quantity those secondaries produce is written into
`verdict.json`.

**Demonstration.** `an2k.ladder_2k` wrapped so S1 imports
`experiments.exp3e` (a module no 2l pin covers), on the W1 world:

```
  a secondary imported 'experiments.exp3e' (unpinned); verdict = SHARED,
  secondary failures = []
  the module is on the surface now: True
  check_imports_2l() after the run RAISES: unpinned module on the import
  surface: experiments.exp3e -> .../experiments/exp3e/__init__.py
  => the verdict was delivered with an unpinned module on the import surface
```

**Closed additively**: a third `check_imports_2l` call after the
secondaries; on failure the record is replaced by the frozen refusal
terminal (INSUFFICIENT_DATA, tests and secondaries withdrawn).

**Stated plainly:** not reachable through the real producer — no
secondary imports anything the entry/exit checks have not already seen
(the pre-campaign import scan enumerated the surface and
`IMPORTED_SHA256_2L` covers the residue). This is a pin made total, not
a bug fixed.

Test: `test_check_imports_2l_post_secondaries_forced_exception`
(totality). Mutants: the auto-generated `collect_total`-stripped mutant
at the new site, plus `F-1: the post-secondaries import re-check does not
refuse`.

---

### F-2 — the sweep's checkpoint record was attested, never measured, and its coverage claim was over an unstated subset

**What.** `load_sweep_13b` read the checkpoint record for the 12 LFS
shard shas and for `loading_info`/`size`/`step`. Three things it carries
were never compared to anything: its `revision` and `commit` (the
manifest entry has both), and its `digest` — the tensor digest of the
weights, which is the only quantity tying the step's 34 item records to
the checkpoint the record says was loaded. And the sha table was checked
over 12 names while the loader stages **13** candidate files (the 12
shards plus `model.safetensors.index.json`), so "the shas match" was a
coverage claim over an unstated set — 3d F-2's shape, one file type over.

**Measured.** `entry["files"]` = 13, `entry["lfs_sha256"]` = 12;
the uncovered name is `model.safetensors.index.json`.

**Closed additively** (`analyze_2l.checkpoint_record_failures_2l`, raised
from `load_sweep_13b`): revision and commit against the manifest entry, a
sha attested for **every** candidate file, and the record's digest equal
to the `weight_sha256` every one of the step's item records carries.

**Disclosed, not closed:** the index file carries no LFS sha in the Hub
metadata (`refresh_inventory_13b` records `s.lfs.sha256` only), so it has
no content pin in the manifest — it is pinned by the revision commit
alone, exactly as any non-LFS file in a pinned git tree is. Gate 1's
tensor-digest identity between the two loader paths covers the endpoint
step; the other sixteen grid points rest on the commit. Doc slip (g).

Tests: `test_checkpoint_record_failures_2l_measures_provenance_and_coverage`,
`test_load_sweep_13b_carries_the_checkpoint_record_check` (both fast).
Four mutants.

---

### F-3 — `rung_set_2l.json`'s `endpoint_file_sha256` was required, published, and compared to nothing

**What.** The endpoint runner writes a table of the 68 endpoint records'
shas into `rung_set_2l.json`; `_load_rung_set_2l` REQUIRED the key to be
present and the verdict PUBLISHES the whole rung set inside
`referents["rung_set"]`. Nothing ever measured it. (The world fixtures
wrote `{}` and every world passed.) 2i F-1 / 2j F-2's class: an
attestation that could be measured.

**Closed additively** (`_check_rung_set_endpoint_shas_2l`, its own
`collect_total` site in `run()`): exactly the 68 endpoint records,
missing/extra/mismatched keys all reported, a missing record named.

Tests: `test_check_rung_set_endpoint_shas_2l` (fast),
`test_rung_set_endpoint_shas_check_forced_exception` (totality). Two
mutants + the auto site mutant. The world builder and
`verify_referents_2l` check 10 now write and check the real table.

---

### F-5 — the power record's own top level, and the block-SD block the projection is graded against

**What.** `load_power_2l` checked the two per-test blocks and the
composite predictor sha. The record's top-level `r_primary` and
`primary_is_the_nine` were attested and compared to nothing, and
`block_sd_A` was checked only for the PRESENCE of five keys — while dial
f makes `block_sd_A` load-bearing: "the projection places its verdict
call inside or outside that scatter". A block SD taken over a different
rung set, or over a different number of blocks, would have been accepted
and then used to grade the forecast.

**Closed additively:** `r_primary` against the rung set's R_PRIMARY;
`primary_is_the_nine` against 2k's nine; `blocks` against the predictor's
four 64-draw blocks; `per_block_mean_T_at_declare`'s length; and the rung
set the SD was taken over — required whenever `n_sim > 0`, which is
exactly when `power_2l.block_sd_A` emits it — re-derived in
`check_power_claims_2l` as Test A's non-degenerate set.

The producer→analyzer round trip (`test_power_2l.py`, the record
`power_2l.main` actually writes read back through `load_power_2l`) passes
unchanged.

Tests: the five new mutation cases in `test_load_power_2l_and_claims`
(fast). Five mutants.

---

### D-1 — the campaign logs were not gitignored (2g and 2i ignore theirs)

`experiments/exp2g/*.log` and `experiments/exp2i/*.log` are ignored;
2l had no rule, and the process tail writes `endpoint.log`, `power.log`,
`sweep.log`, `analyzer.log`, `watcher_*.log` — a `git add -A` at
close-out would have committed home paths (2k disclosed exactly that
nuisance in PROVENANCE). Closed by a NAMED list in `.gitignore` rather
than `experiments/exp2l/*.log`, because the committed `mutation_*.log`
files ARE the mutation battery's record and must stay tracked.

---

## Attack list — dispositions

### 1. Six lineages, cold

**(1) Every verdict input pinned or re-derived at analysis time —
CLEARED.** The read sweep on the real pre-campaign tree reports 4,437
distinct paths read in seven buckets with **UNPINNED = 0** and 0 writes
(table under item 11). The chain per input: the 34 item files sha-pinned
at load against `battery_2d.ITEMS_SHA_PIN` (frozen); 2d's floors
sha-pinned against `battery_2g.FLOORS_VERDICT_2D_SHA256`; 2g's predictor
(the strata source) sha-pinned against `battery_2h.PREDICTOR_2G_SHA`;
`checkpoints_2l.json` against `CHECKPOINTS_2L_SHA256` in the tag-bound
battery; `referents_2l.json` against the analyzer's literal; the 42
frozen modules against `FROZEN_SHA256_2L`; the import surface against
`IMPORTED_SHA256_2L` + 2j's + 2k's residual pins; the four instrument
blobs against `exp2l-preregistered`; both predictors re-derived from raw
draws through their own sealed readers; the 13B records re-verified
continuation by continuation.

*Alignment, attacked separately* (the failure that would silently decide
D without any refusal — strata, x_A, x_B and y indexed by different item
orders): 2g's committed strata table re-derived from the sha-pinned item
files is **identical**, all 11 rungs, 500 labels each. Every predictor
vector is built from rows whose item coverage 0..499 is asserted and
sorted; every outcome vector is built from records whose continuations
are re-scored against `cap["eval_items"]` in file order. Three pins
(item files, 2g's predictor, `strata_2g.py`) anchor it; not a convention.

**(2) Every tree the two runners and the power tool can leave reaches a
frozen terminal (2d F-1 / 2h F-1 / 2k F-1) — CLEARED.** Ten enumerated
kill shapes built from a real W1 world and run through the frozen
analyzer; every one INSUFFICIENT_DATA, control still SHARED:

| tree | verdict | first failure |
|---|---|---|
| (a) endpoint stage killed mid-`which` (no rung set, no power, half of `main` absent) | INSUFFICIENT_DATA | `2l rung set file: FileNotFoundError` |
| (b) sweep killed mid-step (10 rungs + checkpoint record of step 320000 absent) | INSUFFICIENT_DATA | `2l sweep olmo13b: FileNotFoundError` |
| (c) `run_gate1` killed between the record writes and `gate1.json` | INSUFFICIENT_DATA | `2l gate 1 olmo13b: record missing` |
| (d) power record over a different rung set | INSUFFICIENT_DATA | `2l power record: ValueError … rungs` |
| (e) endpoint record edited after the sweep stamped `endpoint_sha256` | INSUFFICIENT_DATA | `endpoint_sha256 … is not the composite` |
| (f) `gate1.json` with real attested diffs and NO halt marker | INSUFFICIENT_DATA | `gate 1 olmo13b/sub3_mid: 7 bit diffs` |
| (g) rung set deleted, power present | INSUFFICIENT_DATA | `2l rung set file: FileNotFoundError` |
| (h) a whole grid step's directory missing | INSUFFICIENT_DATA | `2l sweep olmo13b: FileNotFoundError` |
| (i) the real step 0's records missing | INSUFFICIENT_DATA | `2l sweep olmo13b: FileNotFoundError` |
| control (untouched W1, n_perm 200) | SHARED | 0 failures |

Plus the committed worlds W7–W17 (drifted endpoint seal, halted, gate-1
byte diff with a clean attestation, gate-1 attested mismatch, missing
sweep/step-0-checkpoint/power records, power sha, power claims,
post-seal endpoint edit) and the 28-case totality suite (torn JSON, a
list where a dict belongs, a directory where a file belongs, gzip
truncation/corruption, and a forced exception at every `collect_total`
site).

**(3) No self-consistent-only coverage claim (3d F-2) — CLEARED, with
one gap found and closed.** `endpoint_files` raises on a missing file
(mutant 10 kills the removal); `gate1_rederive_13b` requires 500 bits AND
500 continuations on BOTH sides and requires the attestation's
`continuations_compared` to be 500 (mutants 15/20); `load_tier_2k`
re-derives gate 1 against 2d's committed bytes and checks
`draws_compared` against the re-derivation. **The gap:** the checkpoint
record's sha table was checked over 12 of 13 candidate files — F-2,
closed.

**(4) Nothing attested that could be measured (2i F-1 / 2j F-2 / 2k F-2)
— THREE GAPS FOUND, all closed.** The gate record: attested AND
re-derived from the bytes (already). The power claims: re-derived
already for the six per-test fields; **its top level and block-SD shape
were not — F-5.** The seal shas: re-derived from the two seals and
cross-checked against the counts (already). The composite: re-derived
(already). **`rung_set_2l.json`'s `endpoint_file_sha256`: attested,
published, never measured — F-3.** **The checkpoint record's
revision/commit/digest — F-2.**
*Remaining, disclosed:* the power record's `declared_status` is the one
claim the analyzer cannot re-derive (it would have to re-run 200
simulations per test); it drives a disclosure, never a terminal. The
index json has no content pin to measure against (F-2's disclosure).

**(5) The import surface pinned, entry and exit (2j F-1) — GAP FOUND,
closed (F-1).**

**(6) The tag binds the instrument, not a name (2h F-3) — CLEARED,
against real git.** New test
`test_require_prereg_2l_binds_the_instrument_in_a_real_git_repo`: a real
`git init`, the four instrument blobs committed, a real **annotated** tag
`exp2l-preregistered`, `git show <tag>:<path>` as the comparison —
`require_prereg_2l` binds all four; appending one byte to
`run/sweep_2l.py` afterwards raises `tag … does not bind
experiments/exp2l/run/sweep_2l.py`. `require_prereg_2l` is called by the
endpoint runner, the sweep runner, `power_2l` AND the analyzer's `run()`
(inside `collect_total`, so the analyzer refuses rather than raising), so
a post-tag edit stops all four.

### 2. The composite predictor sha is a function of two literals — CLEARED; every link is a check

Chain, stated, each link named with the code that enforces it:

1. `PREDICTOR_SHA_2L = sha256(f"{SEAL_2K_SHA256}|{SEAL_2I_SHA256}")`, both
   literals in `battery_2l.py` — **one of the four blobs
   `exp2l-preregistered` binds** (`require_prereg_2l`, real git, checked
   by the runners AND the analyzer). Editing either literal after the tag
   stops everything.
2. The two seal FILES are bound by their own tags:
   `an2i.require_seal_2i(bk.SEAL_TAG_2K, an2k._seal_paths_2k(...))` and
   the same for `exp2i-predictor-sealed`, via `bi.blobs_bound` = `git
   hash-object` vs `git rev-parse <tag>:<path>`. Demonstrated to be a
   check and not a convention:
   `test_seal_binding_is_a_check_not_a_convention` — the committed set
   binds with zero failures, and adding one path the tag does not carry
   (`experiments/exp2l/analyze_2l.py`, which did not exist when 2k's seal
   was cut) is reported as drift.
3. Each seal's own `sha256` must equal its literal
   (`require_predictor_seals_2l` in the runners, `load_predictors_2l` in
   the analyzer).
4. `an2k.seal_failures_2k` re-derives the seal's composite from its files
   table, hashes every file against disk, requires the table to COVER the
   36 tier files, and compares the sealed counts at 256 and at every
   ladder k to the re-derivation from the raw draws.
5. `an2i._check_predictor_seal_sampling` + `_check_predictor_counts_2i`
   do the same for x_B.
6. Every 2l record must stamp `predictor_sha == PREDICTOR_SHA_2L`.

So the hypothetical — both seal files edited consistently with new
literals — additionally requires re-tagging two CLOSED experiments'
public seal tags (grafted to the public repo and archived under Zenodo
DOIs) and re-deriving 2k's counts from draws that gate 1 pins to 2d's
committed bytes, whose shas are literals in frozen `battery_2i.py`,
itself pinned by `FROZEN_SHA256_2L` in the tag-bound `battery_2l.py`.

### 3. Test B's strata are the analyzer's composite, not the power record's — CLEARED, with the disclosure the projection needs

`check_power_claims_2l` builds `strata_b =
an2i._composite_strata_median(strata, x_a256, r_primary)` from the
analyzer's OWN re-derived x_A^(256) and re-derives B's degeneracy on it.
The mutant that strips the composite (`strata_b = strata`) is
**documented equivalent on the real predictors**: `_degenerate_rungs(x_b,
base)` and `_degenerate_rungs(x_b, composite)` are BOTH empty, so the
claim check cannot distinguish them here. Stated plainly rather than
talked up. (The mutant is not inert in general and the composite is what
§4/dial d specifies; the analyzer keeps it.)

Ties fall in bucket 0 — `_median_bucket` is `int(v > med)`, strict:
verified (`[1,1,1,2] -> [0,0,0,1]`).

**Disclosure for the projection — the median-bucket split of x_A^(256)
at 1b, and the composite cells Test B forms from it** (computable now,
before any 13B weight loads):

| rung | median | max | bucket 0 | bucket 1 | composite cells | smallest cell | singleton cells |
|---|---|---|---|---|---|---|---|
| add3_mid | 0 | 2 | 461 | 39 | 8 | 5 | 0 |
| add_base8 | 1 | 11 | 336 | 164 | 4 | 63 | 0 |
| antonym | 13 | 197 | 253 | 247 | 8 | 5 | 0 |
| antonym6 | 13 | 186 | 262 | 238 | 12 | 11 | 0 |
| arith_next | 3 | 25 | 268 | 232 | 4 | 105 | 0 |
| odd6 | 15 | 199 | 252 | 248 | 12 | 24 | 0 |
| sub3_mid | 0 | 7 | 370 | 130 | 6 | 19 | 0 |
| sub4_mid | 0 | 4 | 470 | 30 | 8 | 1 | **1** |
| sub_base8 | 4 | 25 | 251 | 249 | 4 | 89 | 0 |

**No rung's median bucket is empty on either side.** Test A's own
degeneracy set on x_A^(256) is empty (§3.6's note holds). One composite
cell on `sub4_mid` is a singleton, which contributes no informative pair
and no permutation freedom — it is dropped by `precompute`, not counted.

### 4. R_PRIMARY narrower than §4's wording (doc slip (a)) — CLEARED

2g's eleven minus 2k's nine = `count_div13`, `median5`; `predictor_2k.
json`'s count table has **no entry** for either (verified: ABSENT), so
x_A^(256) does not exist there and Test A has no predictor. A rung
outside the nine can never enter A or B:
`rung_set_from_counts_2l` puts it in `R_ELEVEN_EXTRA`, `_load_rung_set_2l`
refuses any `R_PRIMARY` that is not a subset of the nine (existing test:
`match="subset of 2k's nine"`), `_check_rung_set_derivation_2l` re-derives
the whole partition from the endpoint's own counts and floors, and the
partition check refuses a set that no longer unions to R_13B.
`_extra_rungs_2l` prints `R_ELEVEN_EXTRA` with x_A^(64) (2d's committed
counts) and x_B in 2g's strata, and `R_EXTRA` with raw single-stratum D —
never with a 256-draw count that does not exist. Exercised end to end by
the new world W18.

### 5. The endpoint composite includes the power record — CLEARED, both directions

* A sweep launched before the power record exists is refused:
  `require_endpoint_seal_2l` → `refusing: the endpoint stage (…rung_set_2l.json,
  …power_2l.json) is not complete — the sweep runs only after
  'exp2l-endpoint-sealed' is cut` (demonstrated by deleting `power_2l.json`).
* Writing/rewriting the power record AFTER a sweep record exists moves the
  composite: `2l sweep olmo13b: ValueError: olmo13b/step1000/add4_mid:
  endpoint_sha256 'f3a1588…' is not the composite re-derived from the
  committed endpoint files` (W17's shape, demonstrated on `power_2l.json`
  rather than an endpoint record).

The process tail's order (endpoint → power → seal tag → sweep) is
therefore enforced by the artifacts, not only by the runbook.

### 6. Step 0 — CLEARED

`GRID_13B` has 16 points and `trained_steps_13b()` returns exactly it;
`STEP0 in trained_steps_13b()` is False, `n_trained_13b()` = 16 (mutant
2, `trained_steps_13b returns GRID_13B + (STEP0,)`, is killed).
`load_sweep_13b` REQUIRES step 0 (its default `steps` is `GRID_13B +
(STEP0,)`; kill shape (i) and world W13 both refuse). `rung_level_13b`
iterates `trained_steps_13b()` only. `collapses_13b` iterates
`sorted(sweep)`, so step 0 IS in the collapse texture — descriptive, and
stated as such: a real step 0 that emits one token on every item (a
plausible init) will be the texture's first entry and says nothing about
any rung.

### 7. Gate 1 without a marker — CLEARED, both artifacts refuse

* World W10: a real byte diff between the sweep's endpoint-step record and
  the `stage1_final` record with a CLEAN attestation and no marker →
  INSUFFICIENT_DATA through `gate1_rederive_13b` alone ("re-derived from
  the bytes, not the attestation").
* Kill shape (f): the runner writes `gate1.json` BEFORE the halt marker, so
  a kill between the two leaves nonzero attested diffs and no marker →
  `gate1_failures_13b` refuses on the attestation (`gate 1
  olmo13b/sub3_mid: 7 bit diffs`).
* Kill shape (c): a kill BEFORE `gate1.json` leaves the 34 records and no
  gate record → `2l gate 1 olmo13b: record missing`.
* World W9: the marker present → the halt scan runs FIRST, before any
  loader.

2k F-1 (either artifact refuses) is satisfied in all four directions.

### 8. `load_tier_2k` on the real tree is the predictor's own gate 1 — CLEARED

Method: the real 2k tree is never edited. `experiments/exp2k/results` is
**copied** (14.9 MiB — the whole tier, not the 1.2 GB the brief
budgeted) to a temp root passed as `root_2k`, with 2k's seal TAG bypassed
(a temp root can never bind a git tag) so the tier bytes are judged by
`load_tier_2k` and `seal_failures_2k` alone.

* One character changed in ONE seed-0 draw of `antonym`/1b item 0 →
  `2l predictor 2k tier 1b/antonym gate 1 re-derived: ValueError: gate 1:
  1 seed-0 draw(s) differ from 2d's committed bytes (first {'item': 0,
  'seed': 0, 'draw': 0, …})` → INSUFFICIENT_DATA.
* One byte flipped mid-gzip in `add_base8`/1b →
  `2l predictor 2k tier 1b/add_base8 rows read: JSONDecodeError` →
  INSUFFICIENT_DATA (a `ValueError` subclass, inside `collect_total`).

### 9. Label prefixes and totality needles — CLEARED

`test_failure_labels_disjoint_from_2i_2j_2k` extracts every
`collect_total` label from `analyze_2l.py` by AST and asserts all start
with `2l` and that no label is a prefix of any 2i/2j/2k label in either
direction; the two new labels (`2l rung set endpoint shas`, `2l import
surface (post-secondaries)`) pass it. The needles the totality suite
asserts are matched against the FULL `v["referents"]["failures"]` list,
not the truncated `reason` — 28/28 pass.

### 10. Determinism — CLEARED

`analyze_2l.run()` twice in **separate processes**, each building the W1
world from seed 0 under a DIFFERENT root, dumped canonically
(`sort_keys=True`, `allow_nan=False`, `_json_safe`):

```
0f0106999dc1bf62081ecc865da36a7800b1acfefb5e45c5a35e75c077c715c2  detA.json
0f0106999dc1bf62081ecc865da36a7800b1acfefb5e45c5a35e75c077c715c2  detB.json
```

Byte-identical, and path-independent (no world root leaks into a clean
verdict). The permutation null is seeded (`stats_2g.PERM_SEED`).

### 11. Read sweep — CLEARED, (e) = 0

On the real pre-campaign tree, after every freeze closure:

```
verdict (n_perm=30, NOT the experiment's verdict): INSUFFICIENT_DATA — 9 referent/loader failure(s)
4437 distinct paths opened for reading (6757 total open/read calls)
  writes observed (should be 0, write=False): 0

referents_2l.json               2696
frozen_module                     54
instrument_blob                    4
sha_pin_at_load                    0
seal_bound_campaign_absent         0
python_stdlib_venv              1683
UNPINNED                           0
```

`checkpoints_2l.json` is pinned at load through the tag-bound battery
(`CHECKPOINTS_2L_SHA256`) AND is a member of `referents_2l.json`, so it
lands in the manifest bucket rather than `sha_pin_at_load` — doubly
pinned, as Task 5 recorded. The campaign-side paths classify as
`seal_bound_campaign_absent` (0 before the endpoint seal exists, because
every campaign-side loader refuses at a `Path.is_file()` guard before any
`open`); the sweep is to be re-run once after `exp2l-endpoint-sealed` is
cut (process tail step 5), where (e) must still be 0 and (f) resolves to
real numbers.

### 12. The power record's `block_sd_A` — CLEARED, with F-5 closed on its shape

* `t_only` and `_run_test` agree on T **bit for bit** on all four of 2k's
  real 64-draw blocks against a synthetic outcome:
  `-0.007181449533202082`, `-0.009410190804466255`,
  `-0.0011675983638174087`, `-0.007127823397828086` — identical in both
  paths, all four. The four blocks sum to x_A^(256) on every rung.
* The construction is confirmed by reading `power_2l.block_sd_A`: within
  each simulation, T is computed on each of the four blocks and
  `np.std(ts, ddof=1)` is taken ACROSS THE FOUR BLOCKS; those per-sim SDs
  are then averaged over 200 simulations. It is **not** the SD of the four
  per-block means — those are printed separately as
  `per_block_mean_T_at_declare`. Doc slip (d) states this.
* The null line uses `rho_ = 0.0` on the SAME `n_pos` bound (the 13B
  endpoint counts) and the same strata and rungs — disclosed.
* F-5 closes the shape: `blocks`, the per-block list length and the rung
  set the SD was taken over are now measured.

### 13. THIN — FOUND (F-4), closed

The design's own THIN branch (`|R_PRIMARY| < 3`) works and is asserted on
literal inputs in two places — `test_verdict_2l_worlds_disclosures_and_
licences` (a two-rung R_PRIMARY still reaches SHARED, carrying
`DISCLOSURE_THIN_2L`) and `verify_referents_2l` check 8. It is asserted
there rather than in a world because the world builder's `zero_rungs`
knob can produce a two-rung R_PRIMARY but the resulting one- or two-cell
test is the same shape W19 already exercises end to end; the branch under
attack was the guard's KEY, not its firing. The power tool declares
`THIN` when fewer than three
rungs survive **degeneracy** (`_one_test_power`: `thin = len(keep) < 3`,
and the all-degenerate branch declares THIN outright rather than
simulating over zero rungs). The gap between those two rules and the
rungs a test actually reads is F-4.

### 14. The preflight writes nothing under `results/` — CLEARED

`preflight_2l.run` snapshots `root/results` before and after and raises
if anything appeared; `test_preflight_prints_and_writes_nothing` and
`test_preflight_refuses_if_it_wrote_under_results` cover both directions.
Its writes are (i) the ordinary HF cache for the `main` thin load and
(ii) `~/emergence-lab/ckpt_cache_2l/olmo13b/<revision>` for the one
candidate-file checkpoint, which it frees in a `finally`. Neither is
under `results/`; the `main` thin load is NOT freed (it is the same
snapshot the endpoint stage reuses). Doc slip (e).

### 15. `BATCH_SIZE_2L` — CLEARED; the tag is the check

Every runner threads it explicitly (`real_loaders(batch_size=bl.
BATCH_SIZE_2L)` in `endpoint_2l`, `sweep_2l` and `preflight_2l`; no bare
`HFRunner(tok, model)` anywhere), and neither record-writing runner
exposes a `--batch-size` flag (only the preflight does). **No record
carries the batch size** — verified by dumping a real `item_record_2l`
and searching for `batch`. So gate 1, which compares two loader paths at
the SAME batch size, cannot detect a batch-size-induced drift between the
endpoint stage and the sweep. What prevents it is the tag:
`battery_2l.py` is blob-bound by `exp2l-preregistered`, so changing the
constant mid-campaign makes both runners and the analyzer refuse. Doc
slip (c).

### 16. JSON strictness with a NaN — CLEARED, with a new world

`d_from_pre` returns `float("nan")` (never a `ZeroDivisionError`) when a
rung has no informative pair, so an R_EXTRA or R_ELEVEN_EXTRA rung with a
CONSTANT outcome — plausible on the real tree, where a rung can verify on
every item at every grid point — puts a NaN into `_extra_rungs_2l`'s
printed dict. World **W18** builds exactly that (`count_div13` and
`caesar` firing on all 500 items at every step):
`test_w18_extra_rungs_carry_an_undefined_d` asserts the NaNs are there
and the secondaries did not fail, and
`test_w18_verdict_json_is_strict_with_a_nan_secondary` runs the same
world through `write=True` and asserts the file parses, the NaN is `null`,
and the text contains no `NaN` token. (`an2i._json_safe` maps non-finite
floats to `None` before `json.dumps(..., allow_nan=False)`.) In the
GATING path a non-finite per-rung D raises inside `perm_test` and
`_run_test` drops that rung and retries, so T is finite or the test is
`undefined` with `T = None`.

### 17. The pre-tag disclosure — CLEARED, with an addition for ratification

Design §2's list is accurate for Task 5: the import scan and the read
sweep, both INSUFFICIENT_DATA with no T, plus the eleven forced-exception
cases in `test_analyze_2l.py` that call `an.run()` on the real
pre-campaign tree and re-execute on every fast pass and every mutant. The
freeze session ADDS: one more read-sweep execution (after the closures),
`verify_referents_2l` run cold twice, and the eleven forced-exception
cases re-executed on every mutant of the freeze's mutation rounds. All
INSUFFICIENT_DATA, none producing a T. Doc slip (f) puts this in §2 —
checklist item 27 requires it.

### 18. Failure needles vs `reason` — CLEARED

`verdict_tree_2i` truncates to the first five failures in `reason`; every
totality and full-shape assertion matches against
`v["referents"]["failures"]`, which is the complete list
(`referents["failures"] = list(failures)`), and F-1's closure rewrites
that list before re-deriving the reason.

---

## Ratification package for Michael

### Findings, with status

| # | Finding | Class | Reachable through the real producer? | Status |
|---|---|---|---|---|
| F-1 | The import-surface pin's exit check ran before the thirteen secondaries | 2j F-1, one call site over | No — no secondary imports a new module | Closed additively (a third check; refusal terminal on failure) |
| F-2 | The sweep's checkpoint record: revision, commit and tensor digest attested but never measured; sha coverage over 12 of 13 candidate files | 2i F-1 + 3d F-2 | The coverage claim, yes; a provenance mismatch, not from `run_step` as written | Closed additively (`checkpoint_record_failures_2l`) + one disclosure (the index json has no content pin) |
| F-3 | `rung_set_2l.json`'s `endpoint_file_sha256` required, published, compared to nothing | 2i F-1 / 2j F-2 | Yes (any hand edit or partial rewrite) | Closed additively (`_check_rung_set_endpoint_shas_2l`) |
| F-4 | THIN keyed to `|R_PRIMARY|`, not to the rungs a test read | new | **Yes** — four of the nine clear 2d's bar at 9–19 items, below `min_pos` 20 | Closed additively (per-test disclosure on the reason and the licence) |
| F-5 | The power record's `r_primary`, `primary_is_the_nine` and the block-SD shape attested, never measured — and dial f grades the projection against `block_sd_A` | 2i F-1 / 2k F-2 | Yes | Closed additively (`load_power_2l` + `check_power_claims_2l`) |
| D-1 | Campaign logs not gitignored (2g/2i ignore theirs) | hygiene | Yes | Closed (named list in `.gitignore`; `mutation_*.log` stays tracked) |

**No accepted dial was touched.** Confirmed untouched, each re-read
against §10 after the closures: **a** the outcome model
(`allenai/OLMo-2-1124-13B`, `SIZE_OUT = olmo13b`); **b** Tests A and B
and the four worlds (`WORLDS = an2i.WORLDS`, `verdict_tree_2i`
unchanged, `fires_2i` unchanged); **c** the grid (`GRID_13B`, 16 trained
points + the real step 0); **d** Test B's conditioning
(`_composite_strata_median` on x_A^(256), the zero cut still a printed
sensitivity); **e** the rung-set rule (`rung_set_from_counts_2l`
unchanged; only its `endpoint_file_sha256` attestation is now measured);
**f** the projection's placement against `block_sd_A` (its shape is now
checked, its values untouched); **g** S5 non-gating (`"non_gating":
True`); **h** the block-SD line (construction unchanged); **i** the real
step 0 as init referent; **j** the preflight; **k** the bars (`T_BAR`,
`ALPHA` still 2g's, asserted by `check_power_claims_2l`); **l** the
one-session build+freeze. S1–S7 unchanged in name, order and content.

### Doc slips — exact §-level wording, for Michael to apply (the freeze does not edit the doc)

**(a) §4, second paragraph ("Strata.") — replace from "The primary for
both tests runs over" to the end of that paragraph with:**

> The primary for both tests runs over **R_PRIMARY = R_13B ∩ 2i/2k's
> nine** (add3_mid, add_base8, antonym, antonym6, arith_next, odd6,
> sub3_mid, sub4_mid, sub_base8) — narrower than R_13B ∩ 2g's eleven,
> because x_A^(256) exists only on the nine: 2k sampled R_CAP, so
> `predictor_2k.json` carries no 256-draw counts for `count_div13` or
> `median5` and Test A has no predictor there. The rest of the eleven
> that clears the bar is printed as **R_ELEVEN_EXTRA** with the 64-draw
> x_A and x_B in 2g's strata; the rest of R_13B is printed as
> **R_EXTRA** with raw single-stratum D; neither is ever in the verdict.
> Fewer than three rungs in R_PRIMARY → THIN declared in the power
> record, the verdict still runs; and a test that ends up READING fewer
> than three rungs — `cells_for` drops a rung with fewer than 20
> positive-outcome items, `_run_test` drops one whose predictor is
> constant inside every stratum — carries its own THIN disclosure on the
> reason and the licence, naming what it read and what was dropped
> (freeze F-4: four of the nine clear 2d's bar at 9–19 correct items, so
> this is reachable with |R_PRIMARY| ≥ 3). **R_CAP's comparability:** the
> nine IS the primary set whenever all nine clear;
> `primary_is_the_nine` is printed either way.

**(b) §3.7, point 7 — append:**

> The referent manifest `referents_2l.json` is **pre-campaign** (2,695
> files: 2k's post-campaign referent list, 2k's verdict, seal, power and
> tier files, 2i's predictor stage, 2i's `run/endpoint_2i.py`, and 2l's
> `checkpoints_2l.json`, `hub_inventory_olmo13b.json` and `power_2l.py`),
> and its own sha is a literal in the analyzer. The campaign's own
> artifacts are deliberately NOT in it: the 68 endpoint records, the rung
> set and the power record are bound by `exp2l-endpoint-sealed` and
> cross-checked at analysis time (record failures; the composite
> `endpoint_sha256` re-derived from the committed files and required on
> every sweep record; the rung set re-derived from the endpoint's own
> counts and its `endpoint_file_sha256` measured against the 68 records;
> gate 1 attested AND re-derived), so the preregistration tag is never
> re-cut after the campaign.

**(c) §7, after the preflight sentence — insert:**

> **`BATCH_SIZE_2L` (= 16) is a single pre-tag constant** in
> `battery_2l.py`, threaded explicitly into every `HFRunner` the
> preflight, the endpoint stage and the sweep construct; nothing reads
> the harness's own default, and neither record-writing runner exposes a
> batch-size flag. No record carries the batch size, so gate 1 — the
> endpoint reproduced through the sweep's loader at the SAME batch size —
> cannot detect a batch-size-induced drift between the two stages. What
> prevents it is the tag: `battery_2l.py` is blob-bound by
> `exp2l-preregistered`, so a mid-campaign change makes both runners and
> the analyzer refuse. If the preflight shows 16 does not fit, the
> constant changes once, before the tag, and the tag is re-cut (2i's
> precedent, disclosed in PROVENANCE).

**(d) §4, the "New (2k's process note, applied)" sentence — replace with:**

> **New (2k's process note, applied — dial h):** the power record also
> prints Test A's predictor block SD, constructed as follows. For each of
> 200 simulations an outcome is drawn from the endpoint-bounded latent at
> the D = .15 calibration; T_A is computed by `analyze_2j.t_only` on each
> of x_A's four 64-draw blocks (2k's seeds 0–3); the SD is taken ACROSS
> THE FOUR BLOCKS within that simulation, and those per-simulation SDs
> are averaged over the 200 — it is not the SD of the four per-block
> means, which are printed separately as `per_block_mean_T_at_declare`.
> The whole construction is repeated at rho = 0 on the same n_pos bound,
> the same strata and the same rungs, and printed as
> `mean_block_sd_null`. The record attests the rung set the SD was taken
> over, and the analyzer re-derives it as Test A's non-degenerate set.
> The projection names its verdict call inside or outside that scatter.

**(e) §7, the preflight clause — replace "ONE checkpoint staged through
the candidate-file loader end to end, the tenth lesson" with:**

> ONE checkpoint staged through the candidate-file loader end to end —
> **step 1000** — downloaded (≈ 55 GB), sha-verified against the
> manifest, hardlinked into a clean directory with the entry's own
> `config.json`, loaded, scored on the same 40 items and **freed**; the
> tenth lesson. The `main` thin load goes to the ordinary HF cache and is
> not freed by the preflight (the endpoint stage reuses that snapshot).
> The preflight writes nothing under `experiments/exp2l/results/` and
> asserts so afterwards.

**(f) §2, after the Task-5 paragraph — append (checklist item 27):**

> The adversarial freeze (Task 6, same session) adds these pre-tag
> executions of `analyze_2l.run()` on the real tree, every one
> INSUFFICIENT_DATA with no T: one further read sweep after the freeze's
> closures (9 referent failures, 4,437 distinct paths read, 0 unpinned, 0
> writes); the eleven forced-exception cases in `test_analyze_2l.py`,
> re-executed on every fast pass of the suite and on every mutant of the
> freeze's mutation rounds; and two cold runs of `verify_referents_2l`,
> whose check 10 reads the real tree's 13B status without calling
> `run()`. No execution of the analyzer on the real tree, in any session,
> has produced a T.

**(g) §3, delta 1 or §3.5 — append (freeze F-2's disclosure):**

> Each grid point's candidate set is the 12 safetensors shards **plus**
> `model.safetensors.index.json`, which decides which tensor comes out of
> which shard. The 12 shards carry LFS sha256s in the Hub metadata, are
> pinned in the committed manifest and are re-checked against the
> checkpoint record; the index file does not appear in the Hub's LFS
> listing, so it carries no content pin and is pinned by the revision
> commit alone. The checkpoint record attests a sha for every candidate
> file it stages, and the analyzer requires that coverage plus the
> record's revision, commit and tensor digest (the last against the
> digest every one of the step's 34 item records carries). Gate 1's
> tensor-digest identity between the two loader paths covers the endpoint
> step; the other sixteen points rest on the commit.

### Instrument delta the freeze leaves for the tag

The four blob-bound files that `exp2l-preregistered` must bind are
`analyze_2l.py`, `battery_2l.py`, `run/endpoint_2l.py`, `run/sweep_2l.py`.
The freeze changed **`analyze_2l.py` only** (F-1, F-2, F-3, F-4, F-5 and
the `IMPORTED_SHA256_2L` re-pin of `verify_referents_2l.py`); the battery
and both runners are byte-identical to `68fb7ed9`. Everything else the
freeze touched is test-side (`tests/*`), a cold tool
(`verify_referents_2l.py`, itself re-pinned), the checklist, the ledger,
or `.gitignore`. `referents_2l.json` did NOT need rebuilding: its manifest
lists `power_2l.py` but neither `analyze_2l.py` (tag-bound) nor
`verify_referents_2l.py` (residual-pinned), and neither was rebuilt — the
committed manifest still hashes to `REFERENTS_2L_SHA256` (cold battery
item 3, `ok`).

### What the freeze did NOT do (waiting on Michael's word)

Doc slips are NOT applied; no tag is cut; the HF cache is not cleared;
no model was contacted and no network call was made. The three process-
tail items that follow ratification — apply the slips, commit, tag
`exp2l-preregistered` at the commit carrying the final `analyze_2l.py`,
`battery_2l.py`, `run/endpoint_2l.py` and `run/sweep_2l.py`, push —
remain the supervisor's.

---

## Cold re-runs after every closure

All run from the repo root under `PYTHONDONTWRITEBYTECODE=1
~/emergence-lab/.venv/bin/python`, after the last closure (F-5) landed.

| run | result |
|---|---|
| full suite, all six modules, no marker filter, no `-k` | **136 passed in 956.81s (0:15:56)** (was 124 at `68fb7ed9`; +12 freeze tests) |
| worlds | **19/19** — the committed W1–W17 plus W18 (extra rungs with an undefined D) and W19 (F-4's thin eligible set); `test_every_terminal_reached` still reaches all five terminals |
| totality | **28/28** (26 + the two new forced-exception sites) |
| cold battery `verify_referents_2l` | **12/12**, every item `ok` |
| read sweep `tests/read_sweep_2l.py` | INSUFFICIENT_DATA (9 referent failures), 4,437 distinct paths / 6,757 reads, **UNPINNED 0**, writes 0, (f) 0 |
| determinism ×2 | `39b20b2b2ec4682e7afa6c6f7bf12dfb0db28f9770b359ba107b783be7aa8ba1` from **both** processes, under two different roots — byte-identical |
| mutation, fast round (`mutation_freeze_fast.log`) | **109/125 killed**, 16 survivors, 0 SKIP |
| mutation, totality round (`mutation_freeze_totality.log`, `--only 82,92,107,113,114,115,116,117,118,119,120,123,124,125`) | **14/14 killed**, 0 survivors |
| mutation, full-shape round (`mutation_freeze_fullshape.log`, `--only 63,64`) | **2/2 killed**, 0 survivors |
| **mutation total** | **125/125 killed, 0 survivors, 0 equivalence claims** — reproducible from the three committed logs |

Mutant accounting, no double counting: the fast round's 16 survivors are
`[63]`, `[64]` (only a full-shape world can observe a change to Test A's
predictor or Test B's conditioning), `[82]` (F-1's own refusal, reachable
only once the secondaries have run — a totality shape), and the thirteen
auto-generated `collect_total`-stripped mutants whose sites are reachable
only on a complete synthetic 13B tree. Every one is killed in the round
named beside it. Task 5's tally (110/110) is superseded: the instrument
changed under the freeze's closures, so all three rounds were re-run
against the current bytes, and thirteen mutants that Task 5 had to close
with later fixture rounds are killed on the freeze's FIRST fast pass (the
new real-git prereg test, the seal-binding test and the
checkpoint-record/rung-set/power tests close them).

Hygiene: `find experiments/exp2l -name "*.mutation_backup"` empty and
`git status` clean on the four mutated files before each round and after
all three; no two runs ever concurrent.
