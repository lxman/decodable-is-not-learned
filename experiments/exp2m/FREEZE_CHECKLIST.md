# Experiment 2m — adversarial freeze (build + freeze session, 2026-09-03/04)

Fresh-eyes reviewer, cold, on `experiments/exp2m/` at build HEAD
`3a057f0f`. The standing assignment: find THE CLASS DEFECT — the defect
that would silently DECIDE the verdict — and close what is found
ADDITIVELY (a new refusal, pin, test, disclosure or record field; never
an accepted dial). Zero model contact and zero network throughout;
every execution of `analyze_2m.run()` on the real tree is a disclosure
event, recorded in `PROGRESS.md` and design §2.

Python: `~/emergence-lab/.venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
from the repo root, `-p no:cacheprovider`. Git: `/opt/homebrew/bin/git`.

Baseline before the freeze touched anything: **suite 152 passed**
(`pytest experiments/exp2m/tests -q`, 1312 s).

**Verdict on the assignment: the CLASS DEFECT was NOT FOUND.** No
reachable path was found on which 2m delivers a verdict computed from
the wrong bytes, and every tree the two runners and the power tool can
leave reaches a frozen terminal. Three findings were found and closed
additively — F-1 (a licence stated over a wider rung set than the tests
read), F-2 (an endpoint `which` assembled from two loads, and gate 1's
digest attestations checked only against each other) and F-3 (the
descriptives carried a `fires` key with no rule behind it). F-1 is the
one that would have changed how the result reads; none of the three
would have changed T.

---

## Findings

### F-1 — a reading narrower than R_PRIMARY carried no disclosure (2l F-4's shape one level over). CLOSED.

**The defect.** `R_PRIMARY = R_3B ∩ 2k's nine`, and a rung enters `R_3B`
by clearing 2d's one-sided exact binomial against its own floor at the
stage-1 endpoint. That bar is far below the analysis-time eligibility
floor of `n_pos ≥ 20` on four of the nine rungs. Executed
(`stats_2d.binomial_bar` against `battery_2g.load_floors`, the minimum
`k` that clears):

```
  add3_mid     floor 0.0060  minimum k clearing 2d's bar =  9
  add_base8    floor 0.0280                               24
  antonym      floor 0.2500                              149
  antonym6     floor 0.1667                              104
  arith_next   floor 0.0200                               19
  odd6         floor 0.1667                              104
  sub3_mid     floor 0.0140                               15
  sub4_mid     floor 0.0060                                9
  sub_base8    floor 0.0560                               42
```

So a 3 B model landing at 10–19 correct on `add3_mid`, `sub4_mid`,
`sub3_mid` or `arith_next` puts that rung INSIDE R_PRIMARY and OUTSIDE
both tests. The power record still declares over
`rungs_simulated = R_PRIMARY minus the PREDICTOR-degenerate rungs`, and
`check_power_claims_2m` re-derives exactly that set, so the two agree
and nothing surfaces the gap. 2l F-4's guard (`_thin_eligible_2m`)
speaks only when fewer than THREE rungs survive — the band
`3 ≤ |eligible| < |R_PRIMARY|` was silent, and the licensed sentence is
built from the disclosures.

**The executable demonstration** (before the closure), a world with
`n_pos_cap={"add3_mid": 12}`:

```
verdict: PYTHIA-ONLY
R_PRIMARY              : the nine
power A rungs_simulated: the nine | declared: POWERED
power B rungs_simulated: the nine | declared: POWERED
A eligible             : eight (add3_mid absent) ; A thin: ['add3_mid']
B eligible             : eight (add3_mid absent) ; B thin: ['add3_mid']
disclosures            : []
licence mentions the dropped rung? False
```

**The closure (additive).** `analyze_2m.DISCLOSURE_PARTIAL_ELIGIBLE_
PREFIX_2M` + `_partial_eligible_2m(test, res, r_primary)`, consulted by
`verdict_2m` in the ELSE branch of 2l F-4's guard, so the two are
mutually exclusive by the `< 3` test. It names the rungs the test did
not read, splits them into n_pos-thin and predictor-degenerate, states
that the power record's declaration and `rungs_simulated` cover a WIDER
set than the reading, and rides on `licensed_sentence`. No dial touched;
no bar moved; no test's T changed.

**After the closure**, the same world:

```
- R_PRIMARY is wider than the reading of Test A: it read 8 of the 9 rungs in
  R_PRIMARY — ['add3_mid'] did not carry it, dropped as n_pos-thin ['add3_mid']
  and as predictor-degenerate []; the power record's declaration and its
  rungs_simulated list cover R_PRIMARY minus the degenerate rungs, a WIDER set
  than the reading, so the licence is bounded to the rungs named as read
- (the same for Test B)
licence carries them: True
```

**Fixture / mutants.** `test_verdict_2m_discloses_a_reading_narrower_
than_r_primary` (fast: fires on 8-of-9; silent on the full reading;
silent when 2l F-4's guard speaks; `_partial_eligible_2m` returns None
in both of those cases and on an empty R_PRIMARY). World **W24**
`PYTHIA-ONLY partial eligible set disclosed` +
`test_w24_partial_eligible_set_is_disclosed`, which also asserts the
power record still says POWERED over all nine. Three mutants: the guard
never speaks; `verdict_2m` does not consult it; the disclosure names the
rungs READ instead of the rungs missed.

**Re-runs.** three fast modules 104 passed; worlds 25/25 + totality 50
passed; cold battery 13/13. Commit `62874d32`.

---

### F-2 — an endpoint `which` assembled from two loads, and gate 1's digest/commit attestations checked only against each other (2i F-1 / 3d F-2 / 2l F-2 on the endpoint side). CLOSED.

**The defect.** A sweep step carries a `_checkpoint.json` whose `digest`
is MEASURED against every one of its 34 item records
(`checkpoint_record_failures_2m`). The three endpoint `which`es have no
checkpoint record, and nothing measured that a which's 34 records came
from ONE load. That matters because: the endpoint stage is RESUMABLE
(`endpoint_2m.run` recomputes `which_pending` and re-loads for the
missing rungs only); `load_thin_3b` goes through the ordinary HF cache
and — unlike `load_checkpoint_3b`, which calls `bi.verify_downloads` —
performs no sha check against the manifest's `lfs_sha256`; and the rung
set's own `endpoint_file_sha256` table and the 104-file composite are
BOTH computed after the records, so a mixed which is internally
consistent and passes every existing check. Gate 1 made it worse:
`digest_endpoint` and `commit_endpoint` are attested by `run_gate1` from
`stage1_final[rungs[0]]` — one rung's record — and compared only to
`digest_sweep`/`commit_sweep`, themselves the runner's attestation of
its own load. Two attestations checked against each other.

**The executable demonstration** (before the closure), 17 of the 34
records of every which rewritten with `weight_sha256 = "OTHER-MODEL"`:

```
load_endpoint_which_2m(stage1_final): CLEAN over 34 records; distinct weight_sha256 = ['D', 'OTHER-MODEL']
load_endpoint_which_2m(stage3_final): CLEAN …
load_endpoint_which_2m(base):         CLEAN …
gate1 digest_endpoint: D | distinct digests over the 34 stage1_final records: ['D', 'OTHER-MODEL']
gate1_failures_3b: NO FAILURES
```

**The closure (additive), three parts.**

1. `analyze_2m.which_coherence_failures_2m(which, records)` — every
   record of a which must carry the same NON-EMPTY tensor digest,
   commit and config source — applied inside `load_endpoint_which_2m`
   after the per-record loop.
2. `battery_2m.gate1_failures_3b` now MEASURES `digest_endpoint` and
   `commit_endpoint` against the digest and commit ALL 34 stage1_final
   records carry (and refuses a stage1_final set that carries more than
   one of either).
3. `battery_2m.gate1_rederive_3b` does the same on the sweep side:
   `digest_sweep`/`commit_sweep` measured over the sweep's own 34
   step-3440000 records, which that function already holds. Both halves
   of the gate are now tied to committed bytes rather than to each
   other.

**After the closure**, the same tree:

```
load_endpoint_which_2m(stage1_final): REFUSED -> endpoint smollm3_3b stage1_final: the 34 records carry 2 different tensor digests ['D', 'OTHER-MODEL'] …
load_endpoint_which_2m(stage3_final): REFUSED …
load_endpoint_which_2m(base):         REFUSED …
gate1_failures_3b: ["gate 1 smollm3_3b: the stage1_final endpoint records carry 2 different tensor digests ['D', 'OTHER-MODEL'] — they did not come from one load"]
```

**Fixtures / mutants.** `test_which_coherence_failures_2m` (clean;
mixed digest, commit and config source; the all-empty case).
`test_gate1_failures_3b` gains the mixed-digest, mixed-commit and
coherent-but-different-from-the-attestation cases, and its
`_endpoint_records` fixture now carries the two fields a real record
has (the fixture had been under-specified relative to the production
record — the new check surfaced that too).
`test_gate1_rederive_3b` gains the three sweep-side cases. Cold battery
item 9 gains three F-2 assertions and states the endpoint's REAL commit
where it had used a `"c"*40` placeholder the old gate could not see.
World **W25** `INSUFFICIENT a which assembled from two loads`, built
with `mixed_digest_which="stage3_final"` at WRITE time so the rung
set's sha table and the 104-file composite both agree with the mixed
tree — `stage3_final` deliberately, because gate 1 never reads it and no
sha check fires, so the new coherence measurement is the only thing that
can refuse (`test_w25_a_which_assembled_from_two_loads_refuses` asserts
exactly that: the refusal is present and no `endpoint_file_sha256` /
`endpoint_sha256` failure is). Five mutants.

**Pin moved.** `IMPORTED_SHA256_2M`: `verify_referents_2m.py`
`c06a104f…` → `7baa94e1…` (item 9's fixture correction plus the three
F-2 assertions). `tests/import_scan_2m.py` re-run — 4 modules, the same
four files. `FROZEN_SHA256_2M` unchanged (`power_2m.py`,
`make_referents_2m.py` untouched). `referents_2m.json` unchanged
(`verify_referents_2m.py` is not a manifest entry; the manifest
re-checks clean and its sha still equals the literal).

**Re-runs.** three fast modules 104 passed; worlds 25/25 + totality 50
passed; cold battery 13/13. Commits `cbe3fe93`, `4429a1b8`.

---

### F-3 — the descriptives carried a `fires` key with no rule behind it (build deferred minor 40; the freeze objects). CLOSED.

**The defect.** `analyze_2i._run_test` stamps `fires = fires_2i(prim)` —
2g's bar, T ≥ .10 and p < .01 — on EVERY test it runs, and 2m runs it
for S5 (the answer prior, dial g: non-gating) and S8 (outcome-to-outcome
order, design §5: "descriptive … p printed, no alpha claim"). The
verdict JSON therefore carries
`secondaries["S8 outcome order"][src]["test"]["fires"] == true` for any
source that happens to clear a bar S8 does not have. `descriptive: True`
and `non_gating: True` sat beside it as bare flags. A reader — including
the retrospective grading the projection — could take that as a result.

**The closure (additive).** `NO_ALPHA_NOTE_2M`, formatted per
secondary, added to each S5 and S8 row beside a `no_alpha_claim: True`
field: it says the `fires` key is `fires_2i` applied mechanically at
2g's bar, that it is NOT a firing rule for that secondary, that no alpha
claim is made, and that a failure inside the secondary lands in
`secondaries.failures` and never in `referents.failures`. The `fires`
key itself is untouched — it is frozen upstream shape.

**Fixture / mutants.** `test_s5_s8_rows_say_their_fires_key_is_not_a_
rule`; world assertions on S5's row and on every S8 row; two mutants
(each row dropping the note).

**Re-runs.** three fast modules 104 passed; worlds 25/25 + totality 50
passed. Commit `4429a1b8`.

---

## Attack list — dispositions

Every disposition below names what was EXECUTED and what it printed.

### 1. Six lineages, cold

**(1) Every verdict input pinned or re-derived at analysis time — CLEARED.**
`grep -rn 'item_record_2i(' experiments/exp2m/` → three hits, all in
`battery_2m.py` (one a docstring): the two record wrappers are the only
constructors, and both OVERRIDE `dtype` to `DTYPE_2M`.
`_record_common_failures_2m` pins `dtype == DTYPE_2M` on every endpoint
and sweep record; world **W22** (a record at `bfloat16`) lands
INSUFFICIENT_DATA. `BATCH_SIZE_2M` is carried by NO record — the
tag-bound constant is the only check, and `referents["batch_size"]`
prints it into the verdict; **disclosed** (doc slip (a)). The other
verdict inputs: floors sha-pinned to 2d's committed verdict
(`FLOORS_VERDICT_2D_SHA256`), items by `battery_2d.ITEMS_SHA_PIN` and
re-checked per record via `items_sha256`, strata by
`battery_2h.PREDICTOR_2G_SHA` plus `strata_2g.check_strata_pins`,
`checkpoints_2m.json` by `CHECKPOINTS_2M_SHA256` inside the tag-bound
battery, the verify criterion by the frozen `analyze_2d`. Read sweep
(below): 5,116 distinct paths, bucket (e) = **0**.

**(2) Every tree the two runners and the power tool can leave reaches a frozen terminal — CLEARED.**
Seventeen shapes built on a real world tree and run through
`analyze_2m.run()`; **all seventeen INSUFFICIENT_DATA, none raised**
(each line is the first collected failure):

| shape | verdict | first failure |
| --- | --- | --- |
| T1 endpoint killed mid-`base`, no rung set | INSUFFICIENT_DATA (7) | `2m rung set file: FileNotFoundError` |
| T2 only `stage1_final` present, no rung set | INSUFFICIENT_DATA (8) | `2m rung set file: FileNotFoundError` |
| T3 rung set written, power absent, no sweep | INSUFFICIENT_DATA (5) | `2m power record: FileNotFoundError` |
| T4 sweep killed mid-step600000 | INSUFFICIENT_DATA (2) | `sweep record missing` |
| T5 gate-1 records written, `gate1.json` absent | INSUFFICIENT_DATA (3) | `2m gate 1 smollm3_3b: record missing` |
| T6 twin records, no twin checkpoint record | INSUFFICIENT_DATA (2) | `checkpoint record missing` |
| T7 power record from a DIFFERENT rung set | INSUFFICIENT_DATA (3) | `2m power record: ValueError: … rungs` |
| T8 power `n_trained_steps` 21 (the log-head count) | INSUFFICIENT_DATA (3) | `2m power record: ValueError: … n_trained_steps` |
| T9 a `stage1_final` record edited after the sweep | INSUFFICIENT_DATA (3) | `endpoint_file_sha256[…] … is not the committed record's` |
| T10 the rung set edited after the sweep | INSUFFICIENT_DATA (2) | `endpoint_sha256 … is not the composite` |
| T11 halt marker on an otherwise clean tree | INSUFFICIENT_DATA (1) | `the runner halted (halted mid-sweep)` |
| T12 `gate1.json` attests 3 bit diffs, NO marker | INSUFFICIENT_DATA (2) | `3 bit diffs between the sweep's step3440000 record and …` |
| T13 empty results tree | INSUFFICIENT_DATA (9) | `2m rung set file: FileNotFoundError` |
| T14 `gate1.json` present, endpoint-step records gone | INSUFFICIENT_DATA (2) | `sweep record missing` |
| T15 twin `config_source` at another commit | INSUFFICIENT_DATA (2) | `smollm3_3b/twin: config_source … is not …` |
| T16 twin seed 7 | INSUFFICIENT_DATA (2) | `checkpoint record seed 7 is not 0` |
| T17 a step's sha table over a subset of its shards | INSUFFICIENT_DATA (2) | `downloaded model-00002-of-00002.safetensors sha None !=` |

T12 is the specific 2k F-1 shape the brief named: `run_gate1` writes the
34 records, then `_checkpoint.json`, then `gate1.json`, and only THEN —
if the gate fails — the halt marker, so a kill between the last two
leaves nonzero attested diffs and no marker. It refuses on the
attestation. T11 is the mirror (marker, clean tree): it refuses on the
marker. Both artifacts refuse.

**(3) No self-consistent-only coverage claim — F-2 FOUND, closed; the rest CLEARED.**
`bm.endpoint_files(<empty dir>)` → `FileNotFoundError … rung_set_2m.json`
(it raises on the FIRST missing of the 104, so no composite can ever be
formed over a subset). `gate1_rederive_3b` requires
`len(bits) == len(continuations) == 500` on BOTH sides, re-derives the
diffs from the bytes, requires the attestation to equal the
re-derivation, and requires `continuations_compared == 500` (3d F-2's
lesson, carried). `_check_rung_set_endpoint_shas_2m` measures the rung
set's attested table against exactly the 102 records — missing, extra
and mismatched all reported. The one coverage claim that was
self-consistent only was the endpoint `which`'s (F-2).

**(4) Nothing attested that could be measured — F-2 FOUND, closed; the rest CLEARED.**
The gate record: bits and continuations re-derived (byte identity); the
digest and commit attestations now measured on both sides (F-2). The
power record: `rungs`, `n_trained_steps`, `predictor_sha256`,
`r_primary`, `primary_is_the_nine`, `dropped_degenerate`,
`rungs_simulated`, `n_pos_lower_bound`, `t_bar`, `alpha`, `thin` and
`block_sd_A.rungs` are all re-derived by `load_power_2m` +
`check_power_claims_2m`; `mean_block_sd_at_declare` is a 200-simulation
output and is attested, not re-derived — 2l's position, kept, and stated
here rather than passed over. The two seal shas: compared to
`battery_2m`'s literals AND the composite re-derived from them. The
rung set: re-derived from the endpoint's own counts through
`rung_set_from_counts_2m`. The twin's checkpoint record: revision,
commit `None`, `kind`, seed, `config_source` at the ENDPOINT's commit
and the digest against every one of its 34 item records — all measured
(T15, T16 fire).

**(5) The import surface pinned at entry, exit and post-secondaries — CLEARED.**
`check_imports_2m` runs three times in `run()`: entry, exit (after the
power claims) and after the secondaries (2l F-1). It verifies the sha of
every path in `IMPORTED_SHA256_2M` and in 2j's/2k's/2l's residual pins
whether or not that module was imported, and refuses any module under
`experiments/` (outside a `tests/` directory) not covered by
`FROZEN_FILES_2M`, `FROZEN_IMPORT_SHA256_2G`, `INSTRUMENT_BLOBS_2M` or
those pins. S8 imports nothing new: every module
`load_committed_outcomes_2m` reaches (`analyze_2j`, `analyze_2i`,
`analyze_2l`, `checkpoints_2g`, `battery_2h`, `rederive_3d`, …) is
already in `FROZEN_SHA256_2M`, and `test_s8_production_loader_once`
exercises the production S8 load inside `run()`, so the
post-secondaries check runs after it (it passes). The three
totality tests `test_check_imports_2m_exit_forced_exception`,
`…_post_secondaries_…` and `test_check_imports_2m_real_rule_flags_a_
module_outside_tests` cover the refusal paths. The scan itself
(`tests/import_scan_2m.py`) was re-run at the freeze: **4 modules**.

**(6) The tag binds the instrument, not a name — CLEARED.**
Executed in a REAL temp git repo containing the four
`INSTRUMENT_BLOBS_2M` at their repo-relative paths, with `bm.REPO` and
`predictor_2g.REPO` repointed at it:

```
temp repo tag: ['exp2m-preregistered']
clean tree -> BOUND ['analyze_2m.py', 'battery_2m.py', 'endpoint_2m.py', 'sweep_2m.py']
  post-tag edit to experiments/exp2m/analyze_2m.py       : REFUSED -> tag … does not bind …
  post-tag edit to experiments/exp2m/battery_2m.py       : REFUSED
  post-tag edit to experiments/exp2m/run/endpoint_2m.py  : REFUSED
  post-tag edit to experiments/exp2m/run/sweep_2m.py     : REFUSED
   sweep runner   : REFUSED -> tag … does not bind experiments/exp2m/run/sweep_2m.py
   endpoint runner: REFUSED -> tag … does not bind experiments/exp2m/run/sweep_2m.py
re-tagged at a v2 commit; reverting analyze_2m.py afterwards: REFUSED
blobs_bound on a path the tag does not carry: ['experiments/exp2m/power_2m.py']
```

So a post-tag edit to `run/sweep_2m.py` is refused by the sweep runner,
by the endpoint runner (both call `require_prereg_2m` first) and by the
analyzer (same call, collected as a failure → INSUFFICIENT_DATA). The
binding is content-addressed on both sides; a name is not enough.

### 2. The composite predictor sha with the `"2m|"` prefix — CLEARED

```
2m composite : f5cedf21bcd64a8f471fd71b8a0c18f673748c37ab8e5f67cdbac681506a299c
2l composite : b44b0fca5483580c5c6499241ba0cd941b9d1e30fcd728293c42f333a7aff9d6
sha256("<2k seal>|<2i seal>") (no prefix) == 2l's composite
```

The chain, link by link, each a CHECK and not a convention: the two seal
shas are literals in the tag-bound `battery_2m.py`; `load_predictors_2m`
reads each seal FILE and compares its `sha256` to its literal; it
re-derives the composite from the two file values and compares it to
`PREDICTOR_SHA_2M`; `require_seal_2i` binds each seal tag over that
experiment's own path set with `git rev-parse <tag>:<path>` against
`git hash-object`; every 2m record must carry `predictor_sha ==
PREDICTOR_SHA_2M` (`_record_common_failures_2m`); and
`endpoint_2m.require_predictor_seals_2m` re-runs the whole chain as a
RAISE before either stage writes a byte. A 2l record cannot pass 2m's
check (`b44b0f… != f5cedf…`) and a 2m record cannot pass 2l's (the
same inequality the other way); `size`/`family` separate them a second
time. `PREDICTOR_TAGS_2M == PREDICTOR_TAGS_2L` by construction (the same
two seal tags) — the `seal_tag` field alone does NOT separate the two
experiments; `predictor_sha`, `size` and `family` do. Stated, not fixed.

### 3. Test B unconditioned (dial b) — CLEARED

`run()._core` calls `_run_test(x_b, bi.SIZE_PRED, out, strata,
r_primary, …)` on the BARE base strata; `power_2m` computes
`rec["B"] = pw._one_test_power(strata, x_b, …)` on the same; and
`check_power_claims_2m` re-derives B's degeneracy on `strata`. The
conditioned forms appear ONLY in `S3 B beyond A` / `S3 A beyond B` and
in `sensitivities.B_conditioned_on_A_median` / `B_zero_cut`
(`an2i._composite_strata*` has exactly four call sites, all inside those
two blocks). Three guards ride on it: the AST test asserting `_core`'s B
call passes the bare Name `strata`, the world equality
`B_base["stratified"]["T"] == B["stratified"]["T"]` re-derived from the
world's own tree, and the world inequality against `S3 B beyond A`.
Mutant #88 ("Test B on the composite") is killed in the fast pass.

The requested disclosure, executed on the two single-predictor worlds
(how much of B's synthetic reading the median-bucket conditioning
moves, and vice versa):

```
W1 pythia_only: BASE   T_A=0.7124 fires=True  | T_B=0.0095 fires=False
W1 pythia_only: COMPOS T_A|B=0.7610 fires=True | T_B|A=-0.1811 fires=False
W2 olmo_only  : BASE   T_A=0.0251 fires=False | T_B=0.6527 fires=True
W2 olmo_only  : COMPOS T_A|B=-0.1881 fires=False | T_B|A=0.6851 fires=True
```

The worlds separate on the BASE strata and on the composite alike, so
W1/W2 are a real terminal test of dial b rather than an artefact of the
conditioning.

### 4. The worlds' residualized latents — CLEARED

On the REAL `x_A^(256)` and `x_B`, over all nine strata rungs and every
base stratum with ≥ 3 items and a non-constant `rank(x_other)`:

```
max |within-stratum corr(resid, rank(other))| = 7.11e-15   (sub4_mid, resid(B|A), 184 items)
largest residual SD among the degenerate cells (target constant in the stratum) = 2.08e-15
```

The single stratum where the raw correlation reads 1.0 is `sub4_mid`
stratum 3, where `rank(x_B)` is CONSTANT over its 57 items: the OLS
residual there is float noise of magnitude 2e-15 after standardisation,
i.e. the latent carries no information in that cell. So `_resid_given`
is orthogonal to the other predictor to machine precision, and the
terminal assertions are as strong as they look: `pythia_only` gives
`T_B = .0095`, `olmo_only` gives `T_A = .0251` — both far under the
brief's .05 threshold and under the .10 bar.

### 5. The twin — CLEARED

`outcomes_3b` refuses any `steps` off the frozen grid:
`GRID_3B + (TWIN,)` → `ValueError: … are not all on the frozen grid`;
`(TWIN,)` alone → the same; `(999,)` → the same. The mutant
`trained_steps_3b -> GRID_3B + (TWIN,)` is in the battery and killed.
The twin's 34 records are REQUIRED (`load_sweep_3b` iterates
`GRID_3B + (TWIN,)`; world W21 and shape T4/T6 refuse), its checkpoint
record is bespoke and MEASURED (`twin_checkpoint_record_failures_2m`:
revision, `commit is None`, `kind == "from_config"`, `seed ==
TWIN_SEED`, `config_source == f"{REPO_CKPT}@{entry['config_commit']}"`,
digest against all 34 item records — T15 and T16 fire on the last two),
and the manifest's twin entry carries the ENDPOINT's commit as
`config_commit` (`build_manifest_3b`; the mutant that sets it to
`"main"` is killed). `run_twin` takes its tokenizer at the same
`config_commit`.

### 6. Three whichs — CLEARED

```
stage1_final   repo=HuggingFaceTB/SmolLM3-3B-checkpoints  rev=stage1-step-3440000  commit=d07a5a83dd01
stage3_final   repo=HuggingFaceTB/SmolLM3-3B-checkpoints  rev=stage3-step-4720000  commit=20e7817e636d
base           repo=HuggingFaceTB/SmolLM3-3B-Base         rev=main                 commit=d78a42f79198
which='main' -> ValueError: 'main' is not one of ('stage1_final', 'stage3_final', 'base')
```

`entry_which_3b` routes `base` to `REPO_BASE` and the other two to
`REPO_CKPT`; `endpoint_2m.run` passes `repo=entry["repo"]` into
`ckpt_of`, whose `config_source` fallback is `f"{repo}@{commit}"` (the
thin loader sets none), so a base record's `config_source` names
`SmolLM3-3B-Base`, and F-2's new coherence check now requires all 34 of
a which to agree on it. Only `stage1_final` drives the rung set
(`counts = {r: stage1_final[r]["correct"]}`; the mutant that reads
another which is killed by `test_endpoint_writes_three_whichs…`). A
missing base record is INSUFFICIENT_DATA (**W20**).

### 7. Gate 1 without a marker, and with an attestation but no marker — CLEARED

**W10** (`gate1_diff`): the endpoint and sweep bytes differ by one bit,
the attestation says zero, no marker — refused by
`gate1_rederive_3b` ("… re-derive …", and "attested bit_diffs 0
disagrees with the re-derived 1"). **W11**
(`gate1_attested_mismatch`): the attestation claims a diff the bytes do
not have — refused ("attested bit_diffs 1 disagrees with the re-derived
0"). Shape **T12**: the halt marker deleted (or never written, the kill
between the two writes) and `gate1.json` attesting 3 bit diffs — refused
on the attestation by `gate1_failures_3b`. Shape **T11**: the marker
present on an otherwise clean tree — refused on the marker, first, by
the halt scan `run()` performs before any pin.

### 8. The tokenizer pins — CLEARED

`check_tokenizer_2m` on stubs mimicking SmolLM3's real facts
(`all_special_ids = [128000, 128001, 128004]`, a `__call__` that
optionally prepends BOS):

```
REFUSE no pad declared (the real tokenizer BEFORE the loader sets it) -> pad_token_id is None, not 128004
PASS   pad set to 128004 (after the loader)
REFUSE a DIFFERENT declared pad 128001                               -> pad_token_id is 128001, not 128004
REFUSE right padding                                                 -> padding_side is 'right', not 'left'
REFUSE a BOS prepended on a plain render                             -> a special id 128000 is prepended to 'Q:'
REFUSE a different eos                                               -> eos_token_id is 2, not 128001
```

`load_tokenizer_3b` sets `padding_side = "left"`, then
`if tok.pad_token_id is None: tok.pad_token = PAD_TOKEN_2M`, THEN calls
`check_tokenizer_2m` — so the pad is set before the check, and a
tokenizer that already DECLARES a different pad is not overwritten and
is refused (row 3). Nothing in any stage prepends `BOS_TOKEN_2M`:
`grep -rn BOS_TOKEN experiments/exp2m` finds it only in the descriptive
second render of `run/preflight_2m.py` and in tests.

### 9. Precision — CLEARED

`item_record_2i` hard-codes `"dtype": "float16"`; both 2m wrappers
override it to `DTYPE_2M`, and they are the ONLY constructors in
`experiments/exp2m` (grep above). Every record is checked against the
constant (`_record_common_failures_2m`), so **W22** refuses a
`bfloat16` record. Stated plainly: gate 1 CANNOT detect a dtype change
between the endpoint stage and the sweep — it re-derives the endpoint
step through the sweep's own loader at whatever `DTYPE_2M` currently
says, so both sides move together — and the same is true of
`BATCH_SIZE_2M`, which no record carries at all. The tag-bound constants
in `battery_2m.py` are what prevent a mid-campaign change; the fp32
fallback is a PRE-TAG change plus a re-tag (design §7), and the analyzer
would refuse every already-written record if the constant moved after
they were written. Doc slip (a).

### 10. S8 is descriptive and cannot decide — CLEARED (with F-3 closed on its labelling)

Structural, from the AST of `analyze_2m.py`: all thirteen secondaries
including `S8 outcome order` go through `_sec`, whose `collect_total`
failure lands in `sec[name]["failed"]` and `sec_failures`;
`sec["failures"] = sec_failures` is written into the record and
`sec_failures` is NEVER added to `failures` (no line matches
`failures += … sec_failures`). `load_committed_outcomes_2m` has exactly
ONE call site, inside `_s8`. So a broken S8 leaves the verdict alone.

The manifest question, executed: a read-trace of one production
`load_committed_outcomes_2m` recorded **4,129 distinct paths, 2,447
under the repo**, of which exactly **two** are neither
`referents_2m.json` entries nor pinned modules —
`experiments/exp2g/checkpoints_2g.json` and
`experiments/exp2h/checkpoints_2h.json`. Both are loaded with an
explicit `sha_pin` from a frozen module
(`ck2g.load_manifest(..., sha_pin=an2g.CHECKPOINTS_SHA256)`,
`bh.load_manifest_69(..., sha_pin=an2h.CHECKPOINTS_2H_SHA256)`), i.e.
the read sweep's bucket (g). Everything else S8 reads — 2l's whole
campaign tree included — is a manifest entry, so a post-close edit to a
2l record fails `check_referents` at ENTRY (before the predictors, let
alone the secondaries) and would ALSO be refused by 2l's own loaders
inside S8. S8's rungs are `r_primary ∩ that outcome's rung set` (the
mutant that takes every rung of the committed outcome is killed).

### 11. The paired difference — CLEARED

Executed on the real predictors against a synthetic outcome:

```
full-data T_A -0.017031450294864893 == plain mean of within-stratum D: identical -> True
full-data T_B -0.002537737692319475 == identical -> True
diff == T_B - T_A: True
n_boot 50  n_boot_requested 50   ci95 [-0.0087, 0.0394]
rungs == the given list: True
first bootstrap replicate reproduces b1 - a1 on ONE shared index draw: True
```

The last line is the pairing: re-drawing the same seed-0 index by hand
and scoring BOTH predictors on it reproduces the replicate to 1e-12, so
`_t` reads A and B on the same resample (the "unpaired" mutant is in the
battery). `rungs` is the intersection of the two tests' eligible sets.
Disclosed, not fixed: the interval is a bootstrap of ONE statistic on
ONE tie structure, and the two predictors' DENSITIES differ (256 vs 64
draws) — the record's own `note` says both, and `n_boot_requested` sits
beside `n_boot` so a silently thinned bootstrap is visible.

### 12. The log-head subset — CLEARED

`set(LOG_HEAD_SUBSET_2M) < set(GRID_3B)` is asserted at IMPORT time in
`battery_2m.py` (a `RuntimeError` at module load if it ever stops being
a strict subset) and again in `load_manifest_3b` against the committed
manifest's own `log_head_subset` field; the cold battery's item 4
re-asserts it. 21 of 26 points. `outcomes_3b(sweep, steps=LOG_HEAD_
SUBSET_2M)` re-counts `y` over those 21 points, so `max y == 21`, not 26
— and the world assertion `sens["log_head_subset"]["A"]["stratified"]
["T"] != A["stratified"]["T"]` proves the sensitivity is a DIFFERENT
outcome (mutant #99, which feeds the full grid, is killed). The power
record's `n_trained_steps` is pinned to 26 and describes the PRIMARY
outcome only; the subset sensitivity is descriptive and carries no power
claim — doc slip (g).

### 13. The ceiling fraction — CLEARED (disclosed, not fixed)

`ceiling_fraction_3b` has exactly ONE call site in `analyze_2m.py`,
inside `_s7`; no rule reads it, and it is printed for all 34 rungs
(`n_ceiling`, `fraction`, `n_pos`, `fraction_of_positives`). Stated for
the record, as design §4 already states: SmolLM3's first available
checkpoint is at 94 B tokens (1.2 % of stage 1), so a rung whose items
are already emittable at step 40,000 sits at `y = 26` from the first
grid point and carries little ORDER information; 2g's statistic handles
those ties as informative-pairs-only, the first-correct outcome is the
sensitivity that reads earliness where the count saturates, and no rule
was invented for an outcome nobody has seen.

### 14. `load_tier_2k` on the real tree is the predictor's own gate 1 — CLEARED

Executed on a COPY of `experiments/exp2k` passed as `root_2k`, one byte
flipped inside `results/k256/1b_trained/antonym.draws.jsonl.gz` (the
`"text"` field of one draw, XOR 0x01), everything else untouched:

```
untouched copy: failures 0
one byte flipped -> failures 1
  - 2m predictor 2k tier 1b/antonym gate 1 re-derived: ValueError: gate 1: 1 seed-0 draw(s)
    differ from 2d's committed bytes (first {'…
```

(The injected `blobs_bound` returns `[]` in this probe so the byte gate
is what speaks; in production the copy's paths are outside the repo and
2k's seal tag would ALSO report drift, so the real tree has two
independent refusals.)

### 15. Label prefixes — CLEARED

`test_failure_labels_disjoint_from_2i_2j_2k_2l` walks
`analyze_2m.py`'s AST for every `collect_total(…, "<label>")` and every
f-string label and asserts they all start with `"2m"`. The totality
module asserts its needles against the FULL
`v["referents"]["failures"]` list rather than the truncated `reason`,
and the 31 totality tests pass, so every needle matches a label actually
emitted.

### 16. Determinism — CLEARED

`run()` executed TWICE in SEPARATE processes on ONE world (`shared`,
seed 0) at `n_perm=30, n_boot=10`, each process rebuilding the world's
`tag_exists`/`blob_sha`/`blobs_bound` closures from the same seed via
`write_world_2m` before calling `run(write=True)`:

```
NEITHER | v1.json 478157 bytes
NEITHER | v2.json 478157 bytes
cc6967afe65711bca219fd3f8bb2b374beca59214d7cf4f4ec64db8f3ca10995  v1.json
cc6967afe65711bca219fd3f8bb2b374beca59214d7cf4f4ec64db8f3ca10995  v2.json
BYTE-IDENTICAL
```

(`NEITHER` is the correct reading at `n_perm=30`: the smallest
attainable p is 1/31, above α = .01, so no test can fire — the run is a
determinism probe, not a world check; W3 SHARED is checked at the
world module's own `n_perm`.)

### 17. Read sweep — CLEARED

Re-run cold at the freeze on the real pre-campaign tree:

```
5116 distinct paths opened for reading (7483 total open/read calls)
  writes observed (should be 0, write=False): 0
referents_2m.json  3370 | frozen_module 59 | instrument_blob 4
sha_pin_at_load 0 | seal_bound_campaign_absent 0 | python_stdlib_venv 1683
UNPINNED 0
(e) unpinned verdict input: 0 — clean
```

`referents_2m.json` 3,370 = the manifest's 3,369 files plus the manifest
itself; 2l's committed campaign artifacts are inside that count.
`checkpoints_2m.json` is a manifest entry AND sha-pinned at load through
the tag-bound battery, and `_classify` awards it to the stronger bucket.
`sha_pin_at_load` and `seal_bound_campaign_absent` are 0 for the reason
the build ledger gives (corrected at fix round 1): those files are not
OPENED before the campaign — the run refuses before the secondaries and
never attempts a seal-bound artifact's `open()`. The freeze verified the
S8 side of that claim independently (item 10 above): the only two files
S8 reads that are neither manifest entries nor pinned modules are
exactly the two `sha_pin_at_load` names.

**Disclosure:** this run is a pre-tag execution of `analyze_2m.run()` on
the real tree. It printed INSUFFICIENT_DATA, 10 referent/loader
failures, no T, `write=False`, 0 writes. Recorded in PROGRESS.md and
design §2.

### 18. The power record's `block_sd_A` — CLEARED

`block_sd_A` is Test A's alone, as 2l: per simulation the SD of
`an2j.t_only` across `x_A`'s four 64-draw blocks, averaged over 200
simulations, with the same quantity at rho = 0 as `mean_block_sd_null`.
`load_power_2m` requires the five `BLOCK_SD_FIELDS_2M`,
`blocks == len(bk.SEEDS_2K)` (4), a 4-long
`per_block_mean_T_at_declare`, and — if `n_sim` is non-zero — a `rungs`
field, which `check_power_claims_2m` then MEASURES against Test A's
non-degenerate set. **Test B has one block and prints none**: the string
`"block_sd_B"` does not occur in `analyze_2m.py`, and `load_power_2m`
requires no block line for B (verified by source inspection and by the
worlds, whose power records carry none).

### 19. THIN — CLEARED

Three bands, now all covered. `len(R_PRIMARY) < 3` →
`DISCLOSURE_THIN_2M` (asserted in `test_verdict_2m_worlds_disclosures_
and_licences` with a 2-rung primary). `|eligible| < 3` → 2l F-4's
`DISCLOSURE_THIN_ELIGIBLE_PREFIX_2M` (world **W19**: R_PRIMARY four
rungs, `A["eligible"] == ["add_base8"]`, `A["thin"] == ["add3_mid",
"sub3_mid", "sub4_mid"]`, the disclosure on the licence for BOTH tests).
`3 ≤ |eligible| < |R_PRIMARY|` → **F-1**, world **W24**. The empty
R_PRIMARY edge was executed too: `_run_test` short-circuits to
`_undefined_result_2i` ("no eligible rung", T `None`, p `1.0`), the tree
reads NEITHER, and five disclosures ride on it (two undefined, THIN, and
2l F-4's for each test); `_partial_eligible_2m` returns `None` there, so
it never double-speaks.

### 20. The preflight — CLEARED

`run/preflight_2m.py` snapshots `root/results` before and after and
RAISES if anything appeared (`test_preflight_refuses_if_it_wrote_under_
results`); it frees the one staged checkpoint with the SAME cache key
it was downloaded under (`state["freed"] == state["ckpt"]`, 2i ruling
4); it refuses on a non-finite logit BEFORE the checkpoint load
(`test_preflight_refuses_on_nonfinite_logits` asserts `state["ckpt"] ==
[]`); and the printout test asserts both renders on both models
(20 items × 2 rungs × 2 renders × 2 loads), `batch_size 16`,
`dtype float16`, the two `mps_allocated_bytes` lines, the two
`n_nonfinite` lines and `plain render ids [48, 25]`. The base's thin
load goes to the ordinary HF cache, OUTSIDE `results/` — disclosed. The
preflight calls `check_frozen_2m` but not `require_prereg_2m`; it stores
nothing the analyzer reads, so this is stated rather than closed.

### 21. JSON strictness — CLEARED

**W18** gives `count_div13` and `caesar` an all-fire outcome so their
Somers' D is NaN, then writes the verdict:
`test_w18_verdict_json_is_strict_with_a_nan_secondary` asserts the
written record carries `null` (not `NaN`) and that the string `"NaN"`
does not occur in the file. `run()` writes with
`allow_nan=False` through `an2i._json_safe`, so a NaN that escaped the
sanitiser would RAISE rather than produce an unparseable verdict.

### 22. The pre-tag disclosure — CLEARED, extended

Design §2's logged list (import scan ×2; read sweep ×1; Task 3's
real-tree tests and Task 5's world/totality modules on synthetic roots)
matches PROGRESS.md's Task 5 Step 2 and Step 5 entries exactly. The
freeze adds two more real-tree executions — one import scan (after the
F-2 edit to `verify_referents_2m.py`, the reading that is now pinned)
and one read sweep — both INSUFFICIENT_DATA with no T; and its own
`run()` calls on SYNTHETIC roots (the 17 tree shapes, the F-1/F-2
demonstrations, the determinism pair, the world module), which are the
same class as the build's. Appended to design §2 and to PROGRESS.md.

### 23. Failure needles vs `reason` — CLEARED

`verdict_tree_2m` prints `f"{len(failures)} referent/loader failure(s):
{list(failures)[:5]}"` — the COUNT is complete and the list is
truncated to five. Executed with nine synthetic failures: the reason
reads `9 referent/loader failure(s): ['failure 0', … 'failure 4']`. The
full list is in `v["referents"]["failures"]` (set from `list(failures)`
and reset after the post-secondaries check), and every totality test
asserts its needle against that list, not against `reason`.

---

## Ratification package for Michael

RATIFIED by Michael 2026-09-04 ('go'): slips (a)–(k) applied with the (i) amendment; R-1 applied; M-8 → 2l's gitignore list.

BOUND 2026-09-04: tag `exp2m-preregistered` at 77301c13 (object 7270179d) binds analyze_2m.py 034c8a7359a2…, battery_2m.py 0c5e1f07f888…, run/endpoint_2m.py 52bd2fe173e5…, run/sweep_2m.py 30fa4b4f73cf… — verified through `require_prereg_2m` against real git; any post-tag edit to these four needs a re-tag.

### Findings

| # | finding | status |
| --- | --- | --- |
| F-1 | a reading narrower than R_PRIMARY carried no disclosure (2l F-4 one level over) | CLOSED additively, fixture + world W24 + 3 mutants |
| F-2 | an endpoint `which` assembled from two loads; gate 1's digest/commit attestations checked only against each other | CLOSED additively (analyzer + both gate halves), fixtures + world W25 + 5 mutants; ONE PIN MOVED |
| F-3 | S5/S8 carried a `fires` key with no rule behind it | CLOSED additively (record field + note), fixture + 2 mutants |
| R-1 | the fix wave's SAME-set condition (`all(r in dropped_degenerate for r in missing)`) read SAME even when the power record's own `rungs_simulated` was wider by a rung `_run_test`'s retry loop dropped (final review) | applied post-ratification, fixture ×4 + mutant #103 rewritten |

**Class defect: NOT FOUND.**

### Doc slips — exact §-level wording for `experiment-2m-design.md`

The design doc was NOT edited except §2's disclosure append. These are
proposed wordings, for your ratification.

**(a) §3.4** — after "…`DTYPE_2M` = fp16 likewise — dials l, m)", add:

> Every 2m record's `dtype` field is OVERRIDDEN to `DTYPE_2M` — 2i's
> `item_record_2i`, which 2m's two record wrappers call, hard-codes
> `"float16"` — and the analyzer pins it on every endpoint and sweep
> record. `BATCH_SIZE_2M` is carried by NO record: gate 1 cannot detect
> a batch or a precision change between the stages, because it
> re-derives the endpoint step through the sweep's own loader at
> whatever the constants currently say, so both sides move together.
> The tag-bound constants are what prevent a mid-campaign change; the
> fp32 fallback is a pre-tag change plus a re-tag.

**(b) §3.8** — after "…a pre-campaign referent manifest (2l's list + …)",
add:

> The manifest is PRE-CAMPAIGN and deliberately includes 2l's OWN
> campaign artifacts (its 68 endpoint records, rung set, power record,
> gate 1, verdict and the whole 13B sweep tree), because S8 reads the
> 13B outcome through 2l's frozen loaders: a post-close edit to a 2l
> record is refused at `check_referents` on entry, before the
> predictors and long before the secondaries. The only files S8 reads
> that are not manifest entries are `checkpoints_2g.json` and
> `checkpoints_2h.json`, each sha-pinned at load from a frozen module.

**(c) §3.1** — after "…a seeded `from_config` twin of the stage-1
config", add:

> The twin's config AND its tokenizer are taken at the ENDPOINT's
> commit (`config_commit` in the manifest's twin entry): a twin built
> from another commit's config is a different initialisation, and the
> analyzer measures `config_source` against
> `f"{REPO_CKPT}@{config_commit}"`.

**(d) §3.4** — after "Committed and tagged `exp2m-endpoint-sealed`", add:

> The seal binds 104 files: 3 × 34 endpoint records + `rung_set_2m.json`
> + `power_2m.json`. The composite `endpoint_sha256` every sweep record
> stamps is taken over the same 104, and `endpoint_files` raises on the
> first missing one rather than forming a composite over a subset.

**(e) §5, S8** — after "…with 2g's statistic in the same strata", add:

> S8 uses 2i's permutation machinery, so each row carries a T and a p;
> no α claim is made and its `test.fires` key is `fires_2i` applied
> mechanically at 2g's bar, not a firing rule for S8. Each row says so
> in the record (`no_alpha_claim`, and a note naming the fact that a
> failure inside S8 lands in `secondaries.failures`, never in
> `referents.failures`). The same holds of S5.

**(f) §5, S3** — after "T_B − T_A with a bootstrap interval", add:

> The interval is a PAIRED item bootstrap within each rung — items
> resampled with replacement and BOTH predictors read on the same
> resample — over the intersection of the two tests' eligible sets, and
> the full-data T is the plain mean of within-stratum Somers' D over
> those rungs. It is a bootstrap of one statistic on one tie structure,
> at two different predictor densities (256 vs 64 draws); the record
> carries `n_boot` beside `n_boot_requested` so a silently thinned
> bootstrap is visible.

**(g) §5, sensitivities** — after "the log-head grid subset (21 of the
26 points) as y", add:

> The subset sensitivity RE-COUNTS y over its own 21 points (so
> `max y = 21`, not 26) and is descriptive: the power record's
> `n_trained_steps = 26` describes the primary outcome only and makes
> no claim about the subset.

**(h) §3.3** — after "…`exp2i-predictor-sealed` required to bind", add:

> `PREDICTOR_SHA_2M` is `sha256("2m|" + <2k seal sha> + "|" + <2i seal
> sha>)`. The `"2m|"` prefix is what makes it differ from 2l's
> composite of the SAME two seals, so a 2l record cannot pass 2m's
> `predictor_sha` check and a 2m record cannot pass 2l's. Note that
> `seal_tag` alone does not separate them — both experiments stamp
> `exp2k-predictor-sealed+exp2i-predictor-sealed`; `predictor_sha`,
> `size` and `family` do.

**(i) §4, new — from freeze F-1.** After "Fewer than three rungs in
R_PRIMARY → THIN declared in the power record…", add:

> A rung can be INSIDE R_PRIMARY and outside both tests: 2d's endpoint
> bar clears at k = 9 on `add3_mid` and `sub4_mid`, 15 on `sub3_mid`
> and 19 on `arith_next` — all below the n_pos ≥ 20 analysis-time
> eligibility floor. The power record declares over R_PRIMARY minus the
> predictor-degenerate rungs, so whenever a test READS fewer rungs than
> R_PRIMARY the verdict carries a disclosure naming the rungs it did
> not read and stating that the declaration covers a wider set; the
> licence is bounded to the rungs named as read.

**(j) §3.4, new — from freeze F-2.** After the endpoint-stage paragraph,
add:

> The three endpoint whichs carry no checkpoint record, so the analyzer
> measures each which's coherence directly: all 34 of its records must
> carry the same non-empty tensor digest, commit and config source.
> Gate 1's `digest_endpoint`/`commit_endpoint` and
> `digest_sweep`/`commit_sweep` are likewise measured against the 34
> records on their own side, not merely against each other.

**(k) §7, preflight** — one clause: the preflight applies
`check_frozen_2m` but not `require_prereg_2m`; it stores nothing the
analyzer reads, and design §7 already places it after the tag.

### The instrument delta the freeze leaves for the tag

The four blob paths `exp2m-preregistered` must bind, with their shas at
the freeze's final commit (recomputed and stated in the report, since
the mutation harness restores files in place):

- `experiments/exp2m/analyze_2m.py` — F-1's disclosure, F-2's
  which-coherence check, F-3's note, the re-pinned `IMPORTED_SHA256_2M`;
  the **final-review fix wave** (2026-09-04) additionally carries M-1's
  SAME-set/WIDER-set conditional in `_partial_eligible_2m` and M-2's
  `collapses_3b` docstring correction ("the twin included (last, after
  the grid)"); **the ratification apply (2026-09-04) additionally
  carries R-1** — `_partial_eligible_2m` takes `rungs_simulated=None`
  and decides SAME/WIDER against the power record's own declared list
  (passed by `verdict_2m` from `power[test]["rungs_simulated"]`), not
  against `res['dropped_degenerate']`
- `experiments/exp2m/battery_2m.py` — F-2's two gate-1 measurements
- `experiments/exp2m/run/endpoint_2m.py` — UNCHANGED by the freeze
- `experiments/exp2m/run/sweep_2m.py` — UNCHANGED by the freeze

Also changed (not tag-bound, but pinned elsewhere):
`experiments/exp2m/verify_referents_2m.py` (pinned by
`IMPORTED_SHA256_2M`, re-pinned at the freeze for F-2, and **re-pinned a
second time at the fix wave for M-3** — the restored M-4 comment's
aliased `rec2` split into independently-constructed `rec2`/`rec2b`) and
the test modules (`tests/full_shape.py`, `tests/test_full_shape_2m.py`,
`tests/test_analyze_2m.py`, `tests/test_battery_2m.py`,
`tests/mutation_check.py`) which are outside every pin by the disclosed
`tests/` exclusion. The fix wave additionally changed
`tests/mutation_check.py` (M-1's mutant, M-6's `-k` filter fix),
`tests/test_analyze_2m.py` (M-1's two-branch fixture, M-4's
`pytest.raises` fix) and `tests/test_battery_2m.py` (M-7's dedup) — all
still outside every pin.

### What the freeze did NOT do

- It did not touch the design doc except §2's disclosure append.
- It did not move any accepted dial: SmolLM3-3B and the three whichs,
  the 26-point grid and its 21-point log-head subset, Tests A and B
  unconditioned on 2g's base strata, `R_PRIMARY = R_3B ∩ the nine`, the
  bars .10 / .01, fp16 and batch 16, the plain tokenizer render with pad
  128004, the twin as init referent, S1–S8 — all as ruled.
- It did not run a model, open a network connection, or write anything
  under `experiments/exp2m/results/`.
- It did not re-derive or re-simulate power (there is no rung set yet).
- It did not spend the one pre-committed change.
- It could not exercise the campaign-side reads on the REAL tree (no
  campaign exists); those are exercised on synthetic world roots, and
  the read sweep must be re-run once after `exp2m-endpoint-sealed` is
  cut (the process tail already requires this).

---

## Cold re-runs after every closure

| battery | result |
| --- | --- |
| fast modules (`test_battery_2m`, `test_stages_2m`, `test_analyze_2m`) after F-1 | 103 passed, 182 s |
| the same after F-2 and F-2 (cont.) / F-3 | 104 passed, 186 s |
| worlds + totality after F-1/F-2 (`test_full_shape_2m` + `test_totality_2m`) | **50 passed**, 1150 s — 25 world specs, every terminal reached |
| worlds (fullshape mutation baseline, after every closure incl. W25 and the survivor fixtures) | baseline OK — **26 world specs**, all terminals |
| totality (totality mutation baseline, after every closure) | baseline OK |
| cold referent battery `verify_referents_2m.py` (twice: after F-2's item-9 correction, and after the `IMPORTED_SHA256_2M` re-pin) | **13/13** |
| read sweep `tests/read_sweep_2m.py` | 5,116 distinct paths, 7,483 open/read calls, **(e) unpinned = 0**, 0 writes, INSUFFICIENT_DATA |
| import scan `tests/import_scan_2m.py` | 4 modules, INSUFFICIENT_DATA, no T (the pinned reading) |
| determinism ×2, separate processes, one world, n_perm 30 | **byte-identical** (sha `cc6967af…`, 478,157 bytes) |
| mutation battery, 150 mutants (140 + 10 for the closures) | **150/150 killed**: 122 in the fast pass (`mutation_freeze_fast.log`), 5 more after the survivor fixtures (`mutation_freeze_fast_survivors.log`, `…_survivors2.log`), 21 under `--totality` (`mutation_freeze_totality.log`), 2 under `--fullshape` (`mutation_freeze_fullshape.log`). No stray `.mutation_backup`; the sources are restored (`git status` shows no diff on the four instrument blobs after the harness) |
| tag binding in a real temp git repo | 4/4 blobs bound; every post-tag edit refused by `require_prereg_2m`, by the sweep runner and by the endpoint runner |
| the seventeen runner-left tree shapes | 17/17 INSUFFICIENT_DATA, 0 raises |
| full-suite confirmation run (`pytest experiments/exp2m/tests -q`, every module including the slow real-tree cases the mutation fast pass deselects; detached, read 2026-09-04 after the session boundary) | **157 passed**, 1,393 s (0:23:13) — the 152 pre-freeze baseline + the freeze's five new fixtures (three fast tests; W24 and W25's two world tests), log `freeze_suite_final.log` |
| **fix wave (M-1..M-4, M-6, M-7), fast modules (`test_battery_2m`, `test_stages_2m`, `test_analyze_2m`, `test_power_2m`)** | **109 passed**, 233.6 s (four modules, not three — the brief added `test_power_2m`; 104 + the two new M-1 fixtures + `test_power_2m`'s own tests) |
| **fix wave, worlds + totality** | **50 passed**, 1,161.5 s (0:19:21) — unchanged from the freeze's own reading (25 world specs, every terminal reached); none of the six fixes touch `full_shape.py` or `test_totality_2m.py` |
| **fix wave, cold referent battery `verify_referents_2m.py`** | **13/13**, run twice — once immediately after M-3's `rec2`/`rec2b` code edit and BEFORE the re-pin (item 12 correctly FAILED: "imported module drifted from its pin"), once after the re-pin (13/13 clean, item 9 exercising the M-3 edit) |
| **fix wave, import scan `tests/import_scan_2m.py` (third pre-tag execution)** | 4 modules, INSUFFICIENT_DATA, 11 referent/loader failures, no T — `verify_referents_2m.py` at the new sha, printed literal identical to the pin (no drift) |
| **fix wave, determinism ×2, separate processes, one world (`shared`, seed 0), n_perm 30** | **byte-identical** (sha `177e48cf…`, 478,157 bytes — same byte count as the freeze's reading; sha differs only because the verdict's `git_sha` field now reads HEAD `1c95e3b8` instead of the freeze's commit — confirmed by inspecting the field directly) |
| **fix wave, mutation target resolution + `--only` (M-1's new mutant #103, the three pre-existing F-1 mutants #100-102, `collapses_3b` #97)** | all **151** entries in `mutation_check.M` resolve exactly once (150 + the new mutant, 0 stale, 0 ambiguous); targeted run **5/5 killed**, 0 survivors, 0 SKIP; no stray `.mutation_backup`, `git status --porcelain experiments/exp2m` clean of anything but this wave's own edits after the harness. Full 151-mutant harness NOT re-run (scoped per the brief: wording/docstring/test-only edits, none touching a `collect_total` site or a totality/fullshape-only shape) |
| **ratification apply (2026-09-04), fast modules (`test_battery_2m`, `test_stages_2m`, `test_analyze_2m`, `test_power_2m`)** | **111 passed**, 226.34 s — 109 + R-1's net two new fixtures (three helper fixtures replacing the fix wave's two, plus one `verdict_2m`-level plumbing fixture) |
| **ratification apply, worlds + totality (`test_full_shape_2m` + `test_totality_2m`)** | **50 passed**, 1151.51 s (0:19:11) — matches the freeze's and fix wave's readings exactly (25 world specs, every terminal reached); W24's assertions did not pin the old SAME/WIDER wording, so no fixture edit was needed |
| **ratification apply, cold referent battery `verify_referents_2m.py`** | **13/13** |
| **ratification apply, determinism ×2, separate processes, `shared` world seed 0, n_perm 30** | **byte-identical** (sha `b45721b1…`, 478,157 bytes — same byte count as every prior reading; the `shared` world's eligible sets are full R_PRIMARY on both tests, so `_partial_eligible_2m` returns `None` regardless of R-1; `git_sha` field reads HEAD `7e9e2018`, the pre-commit state) |
| **R-1, mutation target resolution + `--only 100,101,102,103` (R-1's rewritten #103, the three pre-existing F-1 mutants #100-102)** | all **151** entries in `mutation_check.M` resolve exactly once (0 stale, 0 ambiguous); targeted run **4/4 killed**, 0 survivors, 0 SKIP; no stray `.mutation_backup` |

**The full-suite confirmation run** (`pytest experiments/exp2m/tests
-q`, every module including the slow real-tree cases the mutation fast
pass deselects) was launched detached at the end of the freeze session
and READ 2026-09-04 after the session boundary: **157 passed in
1,393 s**, the 152 pre-freeze baseline plus the freeze's five new
fixtures (three fast tests; W24 and W25's two world tests). The log is
`experiments/exp2m/freeze_suite_final.log` (the completed run, copied
from the live scratchpad file; the snapshot committed at d4194641 had
been taken mid-run and lacked the summary line). It is a pytest run,
not a mutation run — it mutates nothing and can leave nothing stranded.

### Note on the state at the session boundary

The freeze is complete: all three findings closed with fixtures and
mutants, all 23 attack items disposed with executions, the mutation
battery green at 150/150, and every cold battery re-run above green.
The full-suite log named above has been read (157 passed); nothing in the freeze is outstanding.
No mutation harness is running; `find experiments/exp2m -name
'*.mutation_backup'` is empty.
