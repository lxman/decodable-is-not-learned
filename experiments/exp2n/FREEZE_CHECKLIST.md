# Experiment 2n — adversarial freeze (build + freeze session, 2026-09-06/07)

Fresh-eyes reviewer, cold, on `experiments/exp2n/` at build HEAD
`ef0fa6b6`. The standing assignment, verbatim from the program: find
THE CLASS DEFECT — the defect that would silently DECIDE the verdict —
and close what is found ADDITIVELY (a new refusal, pin, test,
disclosure or record field; never an accepted dial). Zero model contact
and zero network throughout; every execution of `analyze_2n.run()` on
the real tree is a disclosure event, recorded in `PROGRESS.md` and
design §2.

Python: `~/emergence-lab/.venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
from the repo root, `-p no:cacheprovider`.

Baseline, measured cold BEFORE the freeze touched anything:

| battery | result |
| --- | --- |
| fast modules (`test_battery_2n`, `test_stages_2n`, `test_analyze_2n`, `test_power_2n`; no `-m` filter) | **135 passed**, 257.5 s (the build's 134 plus the one `slow` real-git case the build's `-m "not slow"` deselects) |
| worlds + totality (`test_full_shape_2n` + `test_totality_2n`) | **58 passed**, 1,306.9 s (27 world specs) |
| cold referent battery (`verify_referents_2n.py`) | **14/14** |

**Verdict on the assignment: the CLASS DEFECT was NOT FOUND.** No
reachable path was found on which 2n delivers a verdict computed from
the wrong bytes. Every tree the endpoint and sweep runners can leave
reaches a frozen terminal — nineteen shapes built and run cold, 19/19
INSUFFICIENT_DATA, zero raises, before and after the closures. Four
findings were found and closed additively. **F-1 is the one that could
have moved a verdict** — a two-sided miss of dial o's stop-id override
would change every Comma continuation, hence the endpoint counts, hence
R_COMMA, hence R_PRIMARY, and the endpoint record carried nothing that
could say so; it is not the class defect only because the tag-bound
loader asserts the override itself and the tag binds `battery_2n.py`.
F-2 and F-3 bound what the annotation's resolution claim covers; F-4 is
a record field. None of the four changes T.

---

## Findings

### F-1 — the endpoint whichs' stop-id attestation was the CONSTANT, not a measurement (2m F-2's shape on the field dial o added). CLOSED.

**The defect.** Dial o rules that both loaders set
`model.generation_config.eos_token_id` to Comma's real EOS (3) —
`config.json` says 2, the tokenizer's own BOS, a LlamaConfig default —
because the frozen harness stops on whatever the loaded model's
generation config carries. `set_eos_stop_2n` applies it and asserts it
reads back, and every sweep step's `_checkpoint.json` carries the
loader's own MEASURED `generation_eos_token_id`, which
`checkpoint_record_failures_2n` requires to be 3 (the twin's too).

The three endpoint `which`es carry **no checkpoint record** (2m F-2's
shape). Their only stop-id evidence was `eos_stop_id`, which
`endpoint_item_record_2n` stamps unconditionally from
`EOS_STOP_ID_2N` — a constant that attests the design's RULING, not
the load. And the endpoint stage is the one that fixes R by rule and
feeds the power record: a stop id that never took effect changes every
continuation on every rung, hence the counts, hence R_COMMA and
R_PRIMARY, hence which rungs the two tests read.

**The executable demonstration (before the closure).** `run/endpoint_2n.run`
driven twice, on two temporary roots, with fake loaders identical but
for the `generation_eos_token_id` their `info` reports — 3 (the
override applied) and 2 (the override missed):

```
[BEFORE] endpoint stage driven twice: loader reports generation eos 3 vs 2
[BEFORE] records compared: 102 (3 whichs x 34 rungs), fields differing
         (seconds/stack/git_sha excluded): NONE — the two trees are the same record
[BEFORE] stage1_final/antonym eos keys, override applied :
         {'eos_stop_id': 3, 'config_eos_token_id': None, 'generation_eos_token_id': None}
[BEFORE] stage1_final/antonym eos keys, override MISSED  :
         {'eos_stop_id': 3, 'config_eos_token_id': None, 'generation_eos_token_id': None}
[BEFORE] override applied: endpoint_record_failures_2n -> [] | load_endpoint_which_2n: OK
[BEFORE] override MISSED : endpoint_record_failures_2n -> [] | load_endpoint_which_2n: OK
[BEFORE] R_PRIMARY, override applied ['add3_mid', …, 'sub_base8']
[BEFORE] R_PRIMARY, override MISSED  ['add3_mid', …, 'sub_base8']
```

**Can gate 1 see it?** Item 25 asked for a demonstration either way.
It cannot, and the reason is structural: gate 1 compares the
thin-loaded `stage1_final` records against the candidate-file-loaded
step-460000 records for byte identity of bits and continuations. Both
paths call `set_eos_stop_2n`, so a change that disables the override
disables it on BOTH sides; the two continuation sets are then equal to
each other (and different from what the design intends), and gate 1
reports zero diffs. A ONE-sided miss it does catch — the stop ids would
differ, the continuations would differ past the first `<|end_of_text|>`,
and the re-derivation would fire. Executed on hand records through
`gate1_rederive_comma`: identical continuation sets → `[]` (gate 1
PASSES); one side's continuation lengthened on one item → `1
continuation diff(s) … (re-derived from the bytes, not the
attestation)`. So gate 1 is not the check here; the record had to
become one.

**The closure (additive).** `battery_2n.endpoint_item_record_2n` takes
a REQUIRED keyword `eos_facts` — the loader's own `info`, whose
`config_eos_token_id` / `generation_eos_token_id` are read off the
loaded model by `eos_facts_2n` AFTER `set_eos_stop_2n` — and stamps
both on the record. `analyze_2n.endpoint_record_failures_2n` requires
`generation_eos_token_id == bn.EOS_STOP_ID_2N`, naming in the refusal
that `eos_stop_id` is the constant and not a measurement.
`run/endpoint_2n.run` passes `eos_facts=info`. Required, not optional,
so no construction site — production, fixture or tool — can omit the
measurement; the seven existing call sites were all updated.

**The demonstration after the closure**, same two roots, same loaders:

```
[AFTER] records compared: 102 … fields differing: ['generation_eos_token_id']
[AFTER] stage1_final/antonym eos keys, override applied :
        {'eos_stop_id': 3, 'config_eos_token_id': 2, 'generation_eos_token_id': 3}
[AFTER] stage1_final/antonym eos keys, override MISSED  :
        {'eos_stop_id': 3, 'config_eos_token_id': 2, 'generation_eos_token_id': 2}
[AFTER] override applied: endpoint_record_failures_2n -> [] | load_endpoint_which_2n: OK
[AFTER] override MISSED : endpoint_record_failures_2n -> ['endpoint comma_7b
        stage1_final/antonym: generation_eos_token_id 2 is not the pinned stop id 3 —
        the loader did not apply set_eos_stop_2n (eos_stop_id 3 is the constant the
        record wrapper stamps, not a measurement)']
        | load_endpoint_which_2n RAISED: endpoint comma_7b stage1_final/add4_mid: …
```

and on a whole tree (shape T18, with the rung set's own
`endpoint_file_sha256` table REBUILT over the edited bytes so the tree
is self-consistent and only the new bar can refuse):

```
[AFTER] T18 an endpoint record measured at generation eos 2 | INSUFFICIENT_DATA (4)
        | 2n endpoint stage1_final: ValueError: endpoint comma_7b stage1_final/odd6:
          generation_eos_token_id …
```

(before the closure the same shape refused only because editing the
record moved its sha out of the rung set's table — i.e. it caught a
post-hoc EDIT, never a loader that produced the record that way.)

**Fixtures.** `test_battery_2n.test_endpoint_item_record_2n_and_checkpoint_records`
(the two measured ids present; a "missed" record keeps `eos_stop_id` 3;
omitting `eos_facts` raises `TypeError`);
`test_analyze_2n.test_endpoint_record_failures_2n_pins_every_field_incl_dtype`
(two new rows in the field table: `generation_eos_token_id` 2 and
`None`); `test_stages_2n.test_endpoint_records_carry_the_loaders_own_eos_measurement`
(the stage end to end under a loader reporting 2);
`verify_referents_2n` item 9 (the measured ids and the refusal, on the
real committed battery); world **W29**. **Mutants 193** (the stamp
removed) and **194** (the bar removed).

**Commit** `68a0fd42`.

---

### F-2 — the `delta_sd` power line could describe a WIDER rung set than the annotation C reads (Ruling R-6; 2l F-4 / 2m F-1's shape on the third declaration). CLOSED.

**The defect.** `power_2n.delta_sd_2n` fixes its `rungs` to R_PRIMARY
minus the UNION of the two predictors' degeneracy sets, and
`check_power_claims_2n` re-derives exactly that set, so the two agree.
But `run()` computes the annotation C over
`[r for r in A["eligible"] if r in B["eligible"]]`, and `_run_test`'s
eligible set additionally drops every n_pos-thin rung (design §4's
`n_pos ≥ 20`). A rung can therefore enter R_PRIMARY by clearing 2d's
endpoint bar (`sub4_mid` and `add3_mid` clear it at k = 9), be
non-degenerate for both predictors, and still be outside both tests —
so `min_detectable_delta`, the annotation's own resolution claim and
the number the projection places its Δ call against, described rungs
the interval never read, with nothing surfacing the gap.

**The executable demonstration (before the closure)**, on hand inputs
of W28's shape:

```
[BEFORE] F-2  delta_sd rungs ['add3_mid', 'add_base8', …, 'sub_base8']   (nine)
[BEFORE] F-2  C read rungs   ['add_base8', …, 'sub_base8']  (extra: ['add3_mid'])
[BEFORE] F-2  min_detectable_delta stated: 0.03156
[BEFORE] F-2  disclosures mentioning delta_sd: NONE
[BEFORE] F-2  on the licence? False
[BEFORE] F-2  verdict PYTHIA-ONLY, n disclosures 2
```

**The closure (additive).** `DISCLOSURE_DELTA_SD_WIDER_PREFIX_2N` +
`_delta_sd_scope_2n(power, annotation)`, consulted by `verdict_2n`
after the two eligibility disclosures and the underpowered ones, so it
lands in `disclosures`, in `reason` and — through `_licensed_2n` — on
the licence. It names the extra rungs and the `min_detectable_delta`
they cover. The same-set case is silent; a missing `delta_sd` block, a
missing annotation and a C without a `rungs` list are all silent and
never raise. **No bar, no rule and no dial moves; C's reading is
untouched.**

**After:**

```
[AFTER] F-2  disclosures mentioning delta_sd: ["the power record's delta_sd line
        describes a WIDER rung set than the annotation C reads: the power record
        simulated Δ over ['add3_mid', …, 'sub_base8'] and C read ['add_base8', …,
        'sub_base8'] — its min_detectable_delta (0.03156) covers also ['add3_mid'],
        rung(s) the annotation did not read, so C's interval is read at its own
        resolution over the rungs named as read"]
[AFTER] F-2  on the licence? True
[AFTER] F-2  verdict PYTHIA-ONLY, n disclosures 3
```

**Fixtures.** `test_analyze_2n.test_delta_sd_scope_2n_names_the_rungs_c_did_not_read`
(the helper, incl. every silent branch) and
`…test_verdict_2n_discloses_a_delta_sd_line_wider_than_c` (the
plumbing: reason + licence, and a full-width reading stays silent);
world **W28** (`n_pos_cap={"sub4_mid": 12}` — nine in `delta_sd.rungs`,
eight in `C["rungs"]`). **Mutants 195** (the guard inverted) and **196**
(the call site dropped).

**Commit** `68a0fd42`.

---

### F-3 — `min_detectable_delta` was attested and never re-derived (attack item 33). CLOSED.

**The defect.** `load_power_2n` pins the `delta_sd["formula"]` STRING
against `DELTA_FORMULA_LITERAL_2N`, and `check_power_claims_2n`
re-derived `rungs` and `k_by_rung` — but nothing compared the NUMBER to
the formula the same record carries. The whole resolution claim of the
annotation is that number.

**Before**, on a record whose `delta_boot_sd_null` is 0.012 (so the
formula gives 0.03156):

```
[BEFORE] F-3  min_detectable_delta = 10.0 against delta_boot_sd_null 0.012
              (formula says 0.03156)
[BEFORE] F-3  check_power_claims_2n flagged the formula? NO
```

**The closure (additive).** `check_power_claims_2n` re-derives
`min_detectable_delta == 2.63 × delta_boot_sd_null` to a 1e-9 relative
tolerance, quoting the record's own formula literal in the refusal.
Both-`None` — `delta_sd_2n`'s own degenerate return, and its
no-bootstrap-interval return — stays legal; one-of-two is refused.

**After:**

```
[AFTER] F-3  check_power_claims_2n flagged the formula? ["2n power claims delta_sd:
        min_detectable_delta 10.0 is not 0.03156 — the record's own
        min_detectable_delta = 2.63 * delta_boot_sd_null (normal approximation:
        CI95 excludes zero with power .75)"]
```

**Fixtures.** Three new assertions in
`test_analyze_2n.test_load_power_2n_and_claims_on_base_strata` (a wrong
number refused; one-of-two refused; both-`None` accepted) and
`test_power_2n.test_delta_formula_literal_is_the_same_string_on_both_sides`
(the writer's `power_2n.DELTA_FORMULA_2N` and the reader's
`analyze_2n.DELTA_FORMULA_LITERAL_2N` are one string — the build's
deferred minor T4-m1, closed here). **Mutant 197.**

**Commit** `68a0fd42`.

---

### F-4 — `pins_active` stated three of `run()`'s seven test-only injections (2k D-1's field, completed). CLOSED.

**The defect.** The verdict record's `pins_active` recorded
`frozen_modules`, `import_surface` and `referent_manifest`. It said
nothing about `tag_exists`, `blob_sha`, `blobs_bound` (which together
stub the prereg-tag binding and every seal binding against real git) or
`s8_loader` (which replaces S8's five committed readers). The campaign
path passes none of them, and a reader of the record could not tell.

**Before:** `pins_active` = `{"frozen_modules": …, "import_surface": …,
"referent_manifest": …}` — three keys, printed from the source.

**The closure (additive).** Three more booleans on the same dict:
`prereg_binding` (`tag_exists is None and blob_sha is None`),
`seal_binding` (`blobs_bound is None`), `s8_committed_readers`
(`s8_loader is None`), with the same "True = the real thing ran"
convention the existing three use.

**Fixtures.** `test_totality_2n.test_untouched_world_still_reaches_pythia_only`
(the world harness stubs git and injects S8 — all three read False);
`test_full_shape_2n.test_pins_active_states_every_injection`;
`test_analyze_2n.test_run_on_empty_tree_is_insufficient_never_raises`
(the exact six-key dict, with `s8_committed_readers` True — that test
does NOT inject one). **Mutant 198** (totality-class).

**Commit** `68a0fd42`.

---

## Attack list — dispositions

Every item names what was EXECUTED and what it printed. Items 1–23 are
2m's twenty-three transposed (design §3's substitutions: Comma / 7B /
`stage2_final` / `main` / `every40k_subset`); 24–33 are the plan's
2n-specific additions; 34 is Ruling R-6.

### 1. The runner-left tree shapes, cold — CLEARED

Nineteen shapes built from one synthetic world, each mutilated the way
a kill, a halt or a hand edit would, each run cold through
`analyze_2n.run()` (n_perm 30). Run twice: before the closures and
after.

| shape | verdict | first failure |
| --- | --- | --- |
| T1 endpoint killed mid-`main`, no rung set | INSUFFICIENT_DATA (7) | `2n rung set file: FileNotFoundError` |
| T2 only `stage1_final` present, no rung set | INSUFFICIENT_DATA (8) | `2n rung set file: FileNotFoundError` |
| T3 rung set written, power absent, no sweep | INSUFFICIENT_DATA (5) | `2n power record: FileNotFoundError` |
| T4 sweep killed mid-step200000 | INSUFFICIENT_DATA (2) | `sweep record missing` |
| T5 gate-1 records written, `gate1.json` absent | INSUFFICIENT_DATA (2) | `2n gate 1 comma_7b: record missing` |
| T6 twin records, no twin checkpoint record | INSUFFICIENT_DATA (2) | `checkpoint record missing` |
| T7 power record over a DIFFERENT rung set | INSUFFICIENT_DATA (3) | `2n power record: ValueError … rungs` |
| T8 power `n_trained_steps` 12 (the every-40k count) | INSUFFICIENT_DATA (3) | `2n power record: ValueError … n_trained_steps` |
| T9 a `stage1_final` record edited after the sweep | INSUFFICIENT_DATA (3) | `endpoint_file_sha256[…] … is not the committed record's` |
| T10 the rung set edited after the sweep | INSUFFICIENT_DATA (2) | `endpoint_sha256 … is not the composite` |
| T11 halt marker on an otherwise clean tree | INSUFFICIENT_DATA (1) | `the runner halted (halted mid-sweep)` |
| T12 `gate1.json` attests 3 bit diffs, NO marker | INSUFFICIENT_DATA (2) | `3 bit diffs between the sweep's step460000 record and …` |
| T13 empty results tree | INSUFFICIENT_DATA (9) | `2n rung set file: FileNotFoundError` |
| T14 `gate1.json` present, endpoint-step records gone | INSUFFICIENT_DATA (2) | `sweep record missing` |
| T15 twin `config_source` at another commit | INSUFFICIENT_DATA (2) | `comma_7b/twin: config_source … is not …` |
| T16 twin seed 7 | INSUFFICIENT_DATA (2) | `checkpoint record seed 7 is not 0` |
| T17 a step's sha table over a subset of its shards | INSUFFICIENT_DATA (2) | `downloaded model-00001-of-00003.safetensors sha None !=` |
| T18 an endpoint record measured at generation eos 2 (freeze F-1) | INSUFFICIENT_DATA (4) | `endpoint comma_7b stage1_final/odd6: generation_eos_token_id …` |
| T19 a checkpoint record with no `generation_eos_token_id` | INSUFFICIENT_DATA (2) | `checkpoint record generation_eos_token_id None …` |

**19/19 frozen terminal, 0 raises**, both before and after. (T18's
before-state refused only via the rung set's sha table — i.e. it caught
the post-hoc EDIT, not the loader; that is exactly F-1, and after the
closure it refuses on the measured field with the sha table rebuilt to
agree with the bytes.)

### 2. The composite predictor sha with the `"2n|"` prefix — CLEARED

Executed against the committed seals: both seal shas equal
`battery_2n`'s literals (`True True`); the composite re-derives
(`True`); and the three composites of the SAME two seals are distinct —
2n `95cec11f77a7b521…`, 2m `f5cedf21bcd64a8f…`, 2l `b44b0fca5483580c…`,
`distinct: True`. The cold battery's item 2 asserts the same chain
against real git tags.

### 3. Test B unconditioned (dial b) — CLEARED

AST: `run()`'s `_core` calls `_run_test(x_b, bi.SIZE_PRED, out, strata,
r_primary)` on the BARE `strata`, not on a composite
(`test_core_reads_both_tests_on_the_bare_base_strata_ast`, in the fast
suite). Behaviourally: in W1, `B["stratified"]["T"] !=
sec["S3 B beyond A"]["stratified"]["T"]` (rules OUT the conditioned
form) and `B_base` re-derived from the world's own tree on the base
strata `== B["stratified"]["T"]` exactly (rules IN the base one) —
`test_w1_pythia_only_shape`.

### 4. The worlds' residualized latents — CLEARED

`_resid_given` residualizes one predictor's rank on the other's inside
each base stratum, so the single-predictor modes do not leak (2i
disclosed x_A/x_B correlate at ρ .06–.32). Executed: W1 A fires / B
does not, W2 B fires / A does not, W3 both, W4 and W5 neither — every
terminal reached (`test_every_terminal_reached`, 29 specs).

### 5. The twin — CLEARED

Executed: `outcomes_comma(steps=(TWIN,))` refuses
(`steps ('twin',) are not all on the frozen grid`); so does an off-grid
step 30000. The manifest's twin entry is
`{'revision': 'twin', 'commit': None, 'kind': 'from_config', 'seed': 0}`
and its `config_commit` equals the endpoint's commit (`True`) — design
§3.1's rule. `twin_checkpoint_record_failures_2n` bars the revision,
the commit, the kind, the seed, the config source, the digest against
the 34 item records and the stop id; shapes T15/T16 and worlds
W13/W21 exercise the tree.

### 6. Three whichs from ONE repo, `main` weight-bearing — CLEARED

Executed on the committed inventory (56 revisions, one repo):
`main` at commit `5af409118da3cbea94684c622c66ab8c2ea7f4fe` carries 3
safetensors shards — weight-bearing, unlike 2m's checkpoints-repo
`main`. A grid revision can never BE `main` (`_STAGE1_RE_2N.fullmatch("main")
is None`). The three whichs read one repo and three distinct commits.
`endpoint_duplicates` in the committed manifest is `[]`. A hand
inventory in which `stage1-step220000-tokens461B`'s shards duplicate
`main`'s is refused — `candidate files duplicate ['main'] — not a
trustworthy grid point` — and an inventory without `main` is refused
with `ValueError` (Task 1's R-4 guard). W20 (`missing="main_record"`)
refuses at `2n endpoint main`.

### 7. Gate 1 without a marker, and with an attestation but no marker — CLEARED

The runner writes `gate1.json` BEFORE the halt marker, so a kill in
that window leaves evidence without a marker. Both halves refuse
anyway: W10 (real byte diff, attestation says zero, no marker) refuses
at the re-derivation; W11 (attested mismatch) at `attested bit_diffs`;
T12 (3 attested bit diffs, no marker) at `gate1_failures_comma`; T11
(marker alone) at the halt scan, which runs FIRST in `run()` (2d F-1).
`gate1_rederive_comma` additionally measures `digest_sweep` /
`commit_sweep` against all 34 sweep step-460000 records, and
`gate1_failures_comma` measures `digest_endpoint` / `commit_endpoint`
against all 34 `stage1_final` records (2m F-2, carried).

### 8. The tokenizer pins — CLEARED (with a stub gap closed)

`check_tokenizer_2n` accepted the good stub and refused all nine broken
ones, each naming its field:

```
padding_side 'right'    -> padding_side is 'right', not 'left'
pad_token_id 128004     -> pad_token_id is 128004, not 0 — Comma's own pad_token_id
eos_token_id 2          -> eos_token_id is 2, not 3
bos_token_id 1          -> bos_token_id is 1, not 2
unk_token_id 0          -> unk_token_id is 0, not 1
len 64256               -> len(tokenizer) is 64256, not 64000
plain_adds_special      -> the plain render of 'Q:' begins with [3] — a special id;
                           the stack must add nothing on its own
swallow_bos             -> the BOS render of 'Q:' begins […], not [2, …] —
                           exactly one BOS, first
```

The two together are the double-BOS guard item 24 asks for: the plain
render must add NO special id (so the pinned prefix is the only BOS),
and the BOS render must begin with exactly one id 2. A stack that
prepends BOS on its own fails the first.

**One gap found and closed:** the COLD BATTERY's `_Tok` treated
`pad_token_id=None` as "use the default", so item 14 could not express
the tokenizer that declares NO pad — the shape that matters most, since
2c's frozen harness passes `tok.pad_token_id` straight into `generate`.
The production check already refuses it (the fast module's own `_Tok`
can express it, and `test_check_tokenizer_2n_on_stubs` asserts the
`pad_token_id` refusal). `_Tok` gained a `pad_absent` flag and item 14
now runs nine refusals instead of four. Additive, test-side only.

### 9. Precision — CLEARED

`DTYPE_2N` is a single pre-tag constant threaded explicitly into every
loader and every `HFRunner`; `item_record_2i` hard-codes `"float16"`
and both 2n record wrappers OVERRIDE it, so a `DTYPE_2N` of `"float32"`
propagates (`test_endpoint_records_carry_the_dtype_constant`). The
analyzer requires `dtype == bn.DTYPE_2N` on every endpoint and sweep
record; W22 (`missing="dtype"`) refuses. Gate 1 cannot detect a dtype
change between the stages for the same reason it cannot detect a render
change — both loader paths read the same constant — and the tag-bound
constant is the check.

### 10. S8 is descriptive and cannot decide — CLEARED

`s8_outcome_order_2n`, `s8c_corpus_contrast_2n` and `s5_answer_prior_2n`
carry `no_alpha_claim: True` and `NO_ALPHA_NOTE_2N` in words (2m's F-3,
carried into 2n from commit one). Their failures land in
`secondaries["failures"]`, never in `referents["failures"]`: executed
by `test_s8c_forced_exception`, `test_s9_forced_exception`,
`test_s8_loader_forced_exception` and
`test_secondary_computation_forced_exception` — each returns
`PYTHIA-ONLY` with the row marked `failed`. The annotation C is the
contrast: it IS preregistered, so `test_annotation_c_forced_exception`
lands INSUFFICIENT_DATA.

### 11. The paired difference — CLEARED

`paired_contrast_2n` with `group_a={B}`, `group_b={A}` reproduces
`s3_paired_difference_2n` at the same seed
(`test_paired_contrast_2n_generalises_s3_and_reads_a_and_b_on_one_index_draw`);
both read every predictor on the SAME within-rung item resample. In W1
the difference is negative with a CI95 upper bound below zero; in W2
positive. `n_boot` is reported beside `n_boot_requested` so a
replicate-dropping interval is visible.

### 12. The every-40k subset — CLEARED

Executed: `set(EVERY40K_SUBSET_2N) < set(GRID_COMMA)` is `True`
(12 of 24), asserted at import AND carried in the committed manifest
(`manifest agrees: True`). On an all-ones sweep, `max y` over the grid
is **24** and over the control subset **12** — the control re-counts y
over its own points, it does not slice the grid's count.
`"control": True` is a literal in the record, not a computed rule
(`test_s8_five_rows_s8c_and_s9`, and mutants 136/137 already closed on
it).

### 13. The ceiling fraction — CLEARED (disclosed, not fixed)

`ceiling_fraction_comma` defines the ceiling as `y == n_steps` — items
correct at EVERY grid point — and prints `n_ceiling`, `fraction`,
`n_pos`, `fraction_of_positives` per rung. Executed on an all-ones
rung: `{'n_ceiling': 500, 'fraction': 1.0, 'n_pos': 500,
'fraction_of_positives': 1.0}`. No rule is built on it; design §2 (iii)
and 2m's process note 4 require the projection to quote this
definition, and the ratification package carries that as a process
note.

### 14. `load_tier_2k` on the real tree is the predictor's own gate 1 — CLEARED

The verdict record carries `referents["gate1_2k"][size][rung]["n_diffs"]`,
asserted zero for both sizes over all nine rungs in
`test_w1_pythia_only_shape`. Cold battery item 5 re-derives x_A^(256)
against `predictor_2k.json` and checks the four 64-draw blocks sum to
the 256-draw counts, at both sizes, with zero failures.

### 15. Label prefixes — CLEARED

`test_failure_labels_disjoint_from_2i_2j_2k_2l_2m` walks the AST of
`analyze_2n.py` for every `collect_total` label and asserts each starts
with `"2n"` and none collides with an upstream label. In the freeze's
own runs every collected failure printed with a `2n `-prefixed label
(or a `gate 1 comma_7b` / `rung set comma_7b` / `endpoint comma_7b`
inner message the label wraps).

### 16. Determinism — CLEARED

Two `analyze_2n.run(write=True)` executions on ONE synthetic world
(`shared`, seed 0, n_perm 30), in SEPARATE processes: see the cold
re-run table for the byte comparison.

### 17. Read sweep — CLEARED

Re-run cold after the closures and after the `IMPORTED_SHA256_2N`
re-pin: **6,179 distinct paths, 8,553 open/read calls, 0 writes
observed**, categories `referents_2n.json` 4,428 / `frozen_module` 64 /
`instrument_blob` 4 / `python_stdlib_venv` 1,683 / **UNPINNED 0**;
bucket (e) unpinned verdict input = **0**, bucket (f) = 0 (no campaign
artifact exists yet). Verdict INSUFFICIENT_DATA, 10 referent/loader
failures, no T.

### 18. The power record's `block_sd_A` — CLEARED

`load_power_2n` requires the five `BLOCK_SD_FIELDS_2N`, `blocks ==
len(bk.SEEDS_2K)` (= 4), a `per_block_mean_T_at_declare` of that
length, and — when `n_sim` is non-zero — an attested `rungs` list ("the
SD is over an unstated set of rungs" otherwise);
`check_power_claims_2n` requires that list to equal Test A's own
non-degenerate set. Executed through
`test_load_power_2n_and_claims_on_base_strata`'s mutation table
(`blocks 3`, a one-element `per_block…`, `rungs` dropped, `rungs` short
— all refused). The nine `DELTA_SD_FIELDS_2N` are required the same
way, plus the formula literal (F-3 adds the number).

### 19. THIN — CLEARED

Three disclosures, mutually exclusive by construction:
`DISCLOSURE_THIN_2N` (|R_PRIMARY| < 3), `_thin_eligible_2n` (a test
READ fewer than three rungs — 2l F-4) and `_partial_eligible_2n`
(3 ≤ |eligible| < |R_PRIMARY| — 2m F-1, with R-1's SAME/WIDER decided
against the power record's own `rungs_simulated`). Executed by
`test_verdict_2n_discloses_a_test_that_read_fewer_than_three_rungs`,
`…_a_reading_narrower_than_r_primary`, the three `_partial_eligible_2n`
cases and worlds W19/W24. F-2 adds a fourth, on the annotation's
resolution rather than on the tests' scope, and it is independent of
the other three.

### 20. The preflight — CLEARED

Source-level and behavioural: it applies `check_frozen_2n` and NOT
`require_prereg_2n` (executed: `check_frozen_2n() True |
require_prereg_2n absent: True`); it snapshots `root/results` before
and asserts nothing new after (`"preflight wrote under" in src: True`);
it prints BOTH renders through a `BosRunner` and a bare `HFRunner`
(`plain_runner` twice, `render_ids` present), the eos facts per load
(`config eos 2 | generation eos 3`, once per load), peak MPS memory,
and refuses on a single non-finite logit.
`test_preflight_prints_both_renders_and_writes_nothing` and
`test_preflight_prints_eos_facts_and_peak_memory` execute it against
fakes.

### 21. JSON strictness — CLEARED

The writer is `json.dumps(an2i._json_safe(v), indent=1,
default=an2i._jsonable, allow_nan=False)` (executed: the line printed
from source). `test_w18_verdict_json_is_strict_with_a_nan_secondary`
writes a world whose `extra rungs` carries a NaN D and asserts the file
contains no `NaN` and the value round-trips as `null`.

### 22. The pre-tag disclosure — CLEARED, extended

Design §2 carried three logged entries from the build. The freeze
appended entries 4–6: the `import_scan_2n` re-pin run
(INSUFFICIENT_DATA, 11 failures, no T), the `read_sweep_2n` run
(INSUFFICIENT_DATA, 10 failures, no T, 0 writes, bucket (e) = 0), and
the freeze's own suite re-runs on synthetic and empty roots. No finding
was demonstrated on the real `EXP2N` tree.

### 23. Failure needles vs `reason` — CLEARED

Every totality case asserts its needle against the FULL
`v["referents"]["failures"]` list, not against `v["reason"]` (which
truncates to five). The module docstring records the one case where two
needles must differ (`gate1.json` torn vs a directory). Confirmed by
reading `_insufficient` and by the 42 totality cases passing.

### 24. The render is a verdict input — CLEARED

`grep 'HFRunner(' experiments/exp2n/run/` finds exactly four sites:
`endpoint_2n.real_loaders`, `sweep_2n.real_loaders`,
`preflight_2n.real_loaders`'s `runner` — each `bn.BosRunner(HFRunner(...))`
— and the preflight's deliberate `plain_runner`, the only bare one.
`test_real_loaders_wrap_the_harness_in_bos_runner` asserts the first
three return a `BosRunner` and the fourth does not. `render == "bos"`
is stamped on every endpoint and sweep record and required by
`_record_common_failures_2n`; W26 refuses a record at `"plain"`.
**Stated plainly:** gate 1 CANNOT detect a render change between the
stages — both loader paths render through the same tag-bound
`BosRunner`, exactly as it cannot detect a dtype change; the tag-bound
constant is the check. `check_tokenizer_2n`'s two assertions together
refuse a stack that prepends BOS on its own (item 8).

### 25. The stop id is a verdict input — F-1, CLOSED

`set_eos_stop_2n` is called in all three loaders
(`load_checkpoint_comma`, `load_thin_comma`, `load_twin_comma`) and
raises if the override does not read back.
`generation_eos_token_id == 3` is required on every checkpoint record
including the twin's (W27; T-shapes T19 with the field absent, and the
world's `missing="eos_stop"` with 2). `eos_stop_id == 3` on every item
record. The endpoint whichs carry NO checkpoint record — that is F-1
above, closed by stamping the loader's own measurement and barring it,
with the gate-1 argument demonstrated both ways.

### 26. The annotation C cannot decide the world — CLEARED

AST: `verdict_tree_2n(failures, A, B)` takes three parameters, never
mentions `annotation` in any name, attribute or string, and its only
subscripts are `A[…]`, `B[…]`, `DISCLOSURE_UNDEFINED_2N[…]` and
`list(failures)[:5]`. `annotation_c_2n`'s result reaches `verdict_2n`
ONLY as `annotation={'C': C}` (the AST walk found one call site, with
that keyword, and three failure-path `verdict_2n(failures, None, None,
None, ())` calls that pass none). Order, by line number:
`check_power_claims_2n` (1457) → `annotation_c_2n` (1491) →
`verdict_2n(…, annotation=…)` (1503) — C is computed AFTER the power
claims and BEFORE the tree. A FAILURE inside C is a referent failure:
`test_annotation_c_forced_exception` lands INSUFFICIENT_DATA with
`tests` and `secondaries` withdrawn.

### 27. `covers_3b_increment` measures against a READ number — CLEARED

The chain, executed end to end: `read_increment_3b_2n(bm.EXP2M)` reads
`experiments/exp2m/results/verdict.json` →
`secondaries["S4 matched density"]["increment"]` = `0.06585331726660634`;
that path IS an entry in `referents_2n.json` (checked: present, in the
104 2m endpoint files + 946 sweep files + verdict the manifest carries),
so a post-close edit refuses at `check_referents`; `run()` asserts
`round(read, 4) == round(INCREMENT_3B_2N, 4)` = 0.0659 and appends a
referent failure otherwise (mutant #192, closed at Task 5 fix round 2 by
`test_run_refuses_a_2m_increment_off_the_literal`); the mutant that
makes `read_increment_3b_2n` return the literal instead of reading
(#129) is killed. Cold battery item 14 re-asserts the equality.

### 28. The thinned predictor is the FIRST block — CLEARED

`thinned_x_b_2n` computes `x_thin[r] = [int(sum(row[:k])) for row in
bits_b[r]]` — one deterministic block, no seed. Mutants `[-k:]` and
`[:64]` are in the battery and killed. `k_by_rung` is re-derived by
`check_power_claims_2n` against the power record (and F-2 now discloses
when that record's rung set is wider than C's). S4's all-blocks mean
(`an2j._block_reading` over `64 // k` blocks) is printed beside C in
`secondaries["S4 matched density"]` — two numbers, one rule, and the
rule is C's. Doc slip (c) states it.

### 29. S8c / S9 are descriptive — CLEARED

Failures land in `secondaries.failures` (item 10's executions). The
SmolLM3 row loads through 2m's frozen readers
(`an2m.load_sweep_3b` + `outcomes_3b`, manifest sha-pinned, endpoint
composite re-derived) over 946 committed files, all manifest entries —
cold battery item 13 loads all five sources with zero failures
(`smollm3_3b: 34 rungs, n_pos sum 9076`). S9's four known-answer
literals reproduce from the committed 2l/2m verdicts, executed:
2l antonym A `-0.06577875529488433` / B `0.25597990523491465`,
2m antonym A `-0.040536876355748375` / B `0.16790943600867678` — the
`_per_rung_d` key name `"d"` is the one `_run_test`/`primary_2i` emits
(the committed records' per-rung dicts are `['ci', 'd', 'n_pairs',
'n_pos', 'raw_d']`). The 7B row's literals were corrected pre-freeze by
Ruling R-5 and verified here against the committed sources: 2k's
VERDICT per-rung table at 256 gives antonym6 **.115** and odd6
**.096**, 2i's VERDICT Test B gives antonym6 .214 and odd6 .121,
antonym .217, and 2k's A antonym .024.

### 30. The every-40k control — CLEARED

See item 12: `max y == 12` executed, the strict-subset assertion runs at
import and against the manifest, `"control": True` is a literal.

### 31. `main` is weight-bearing — CLEARED

See item 6: `entry_which_comma(manifest, "main")` routes to `main`'s own
commit `5af409118da3cbea94684c622c66ab8c2ea7f4fe` with its own three
shards; the thin loader takes `(repo, commit)` through the ordinary HF
cache; W20 refuses a missing `main` record; and `main` never drives the
rung set — `endpoint_2n.run` computes `counts` from `stage1_final`
alone and `test_endpoint_writes_three_whichs_and_the_rung_set_from_stage1_final`
asserts the two descriptive whichs score 0 on every rung while the rung
set still comes out of `stage1_final`.

### 32. The grid's first point is step 10,000 — STATED, not fixed

The grid's head is a 7 B model at 21 B tokens (2.2 % of stage 1), and
the analyzer's ceiling definition is "correct at EVERY grid point"
(item 13), so an item already solved at 10,000 sits at y = 24 and
contributes no ordering information. This is the design's own choice
(dial c, §2 (ii)) and the projection must quote the analyzer's
definition (2m process note 4). Nothing was changed; the ratification
package carries it as a process note.

### 33. `delta_sd` — F-3, CLOSED

The `formula` string is pinned by `load_power_2n` against
`DELTA_FORMULA_LITERAL_2N`; the NUMBER was not, and is now re-derived
(F-3). `rungs` = R_PRIMARY minus the UNION of the two degeneracy sets,
measured by `check_power_claims_2n` — and F-2 discloses when that set
is wider than C's reading.

### 34. The `delta_sd` power line vs the annotation C's rung set — F-2, CLOSED

Ruling R-6's item, closed exactly as the program closed 2l F-4 and
2m F-1: a disclosure naming the extra rungs, riding on the licence; a
world (W28); two mutants (195, 196). No bar or rule changed.

---

## Deferred minors from the build ledger — triage

| item | disposition |
| --- | --- |
| T1 `build_manifest_comma` docstring punctuation (one character) | **parked** — cosmetic, no behaviour |
| T1 the manifest-pin skip guard `if not …` vs 2m's `is None` | **parked** — proved equivalent by the reviewer; `CHECKPOINTS_2N_SHA256` is a non-empty literal |
| T2 `import sys` added inside one test, undisclosed in the report's correction count | **closed here** by disclosure — it is necessary, harmless, and now recorded |
| T3 the S9 test's 7B third re-reads the dict it copies from (tautological) | **closed** — cold battery item 14 now asserts the four committed per-rung D's as LITERALS (−0.066 / +0.256 / −0.041 / +0.168 to 3 dp) and the 7B row against an explicit literal table, so it is a known-answer gate rather than a re-read |
| T3 `s9_sign_ledger_2n` reads the two committed verdicts unguarded | **parked** — both routes end in one collected failure; `test_s9_forced_exception` proves the verdict is unaffected |
| T3 a failed S8 load produces three `sec_failures` rows (2m produced one) | **parked** — cosmetic; the rows are correct, only redundant |
| T3 `paired_contrast_2n`'s docstring names `s3_paired_difference_2m`; a dropped rationale comment | **parked** — the named function is 2m's, correctly, since `paired_contrast_2n` generalises it |
| T4 `test_power_2n` lacks the direct `DELTA_FORMULA` identity assert | **closed** — `test_delta_formula_literal_is_the_same_string_on_both_sides` (F-3's fixture set) |
| T4 the world licence assertion weakened to `startswith`; the exact composition unpinned | **closed** — `test_licensed_2n_appends_the_c_modifier_keyed_by_reading_and_covers` now asserts the EXACT composition, base + every disclosure in order + the one C modifier |
| T4 three provenance comments dropped in `verify_referents_2n` items 9/10 | **parked** — items 9 and 10 both gained freeze provenance comments in their place |
| T4 the power stage will cost ≈ 2× 2m's 127 min | **parked to the process tail** — carried into the ratification package as a process note |
| T4 cold-battery item 14's S9 check is a key-path check, not a literal | **closed** with T3's item above |
| T5 the fix-round-1 paragraph says the totality pass targeted 28 ids where the log shows 27 | **closed** — the interim sentence corrected in `PROGRESS.md` |
| T5 #116's closing test is a static AST check, not a runtime observation | **parked** — 2m's #88 precedent, recorded |

---

## Ratification package for Michael

### Findings

| # | finding | status |
| --- | --- | --- |
| F-1 | the endpoint whichs' stop-id attestation was the CONSTANT, not a measurement | CLOSED additively (record field + refusal + runner), 4 fixtures + world W29 + mutants 193/194 |
| F-2 | the `delta_sd` power line could describe a wider rung set than the annotation C reads (Ruling R-6) | CLOSED additively (a disclosure riding on the licence), 2 fixtures + world W28 + mutants 195/196 |
| F-3 | `min_detectable_delta` was attested and never re-derived | CLOSED additively (a re-derivation in `check_power_claims_2n`), 4 fixtures + mutant 197 |
| F-4 | `pins_active` stated three of `run()`'s seven test-only injections | CLOSED additively (three record fields), 3 fixtures + mutant 198 |

**No accepted dial was touched.** Comma v0.1-1T, the 24-point grid and
its 12-point every-40k control, Tests A/B unconditioned at T ≥ .10 /
α .01, the annotation C's CI rule, `R_PRIMARY = R_COMMA ∩ the nine`,
fp16 / batch 16, `render: "bos"`, `eos_stop_id: 3`, the seeded twin and
S1–S9 all stand exactly as ruled.

**One pin moved:** `analyze_2n.IMPORTED_SHA256_2N`'s entry for
`verify_referents_2n.py`, `d9305ac9…` → `e80653b5…`, because F-1's
closure and item 8's stub gap added assertions to the cold battery. The
scan was re-run (design §2 entry 4) and the printed literal pasted; the
read sweep was then re-run and is clean.

### Doc slips — exact §-level wording for `experiment-2n-design.md`

These are the only edits the freeze asks for in the design doc (§2's
disclosure append is already made). Each is a statement of what was
BUILT, not a change of rule.

**(a) §3.2, after "…the pinned render is carried on every record
(`render: "bos"`), and the analyzer refuses a record without it."** —
add:

> The prefix is applied by `battery_2n.BosRunner`, which wraps 2c's
> frozen `HFRunner` and prepends `BOS_TOKEN_2N` to every prompt STRING
> before delegating to `generate` — `evaluate_items` (2g, frozen)
> renders the prompt text itself, so the prefix has to go between it
> and the model. Every stage builds its runner through that class
> (three factory sites; the preflight additionally builds one bare
> `HFRunner` to print the plain render, and nothing it prints is
> stored). Gate 1 cannot detect a render change between the two
> stages — both loader paths render through the same tag-bound
> `BosRunner` — exactly as it cannot detect a dtype change; the
> tag-bound constant is the check.

**(b) §3.3, after "…and every record carries `eos_stop_id: 3`;
`config.json`'s 2 is disclosed on the record as
`config_eos_token_id`."** — replace that clause with:

> …and every record carries `eos_stop_id: 3`. Because the three
> endpoint `which`es carry no checkpoint record, each ENDPOINT ITEM
> RECORD additionally carries the loader's OWN measured
> `config_eos_token_id` and `generation_eos_token_id` (`eos_facts_2n`,
> read off the loaded model after the override), and the analyzer
> requires the measured generation eos to be the pinned stop id — the
> `eos_stop_id` field is the constant the record wrapper stamps and is
> not, on its own, evidence that the override ran (freeze F-1). Sweep
> steps and the twin carry the same two ids on their `_checkpoint.json`
> and are barred the same way.

**(c) §3.8, after "…(2k's block rule: k_g = clip(round(256 · r̄_A /
r̄_B), 1, 64) per rung, the first k_g draws, no seed)"** — add:

> C's thinned predictor is exactly the FIRST k_g-draw block of x_B
> (`row[:k_g]` on every item), one deterministic block and no seed.
> S4's `per_rung` mean over all `64 // k_g` blocks is printed beside it
> in the same verdict — two numbers, one rule, and the rule C reads is
> the first block's.

**(d) §3.8, after "…and `covers_3b_increment` (+.0659)"** — add:

> `covers_3b_increment` is measured against 2m's OWN committed number,
> read at analysis time from
> `experiments/exp2m/results/verdict.json` →
> `secondaries["S4 matched density"]["increment"]` — a pre-campaign
> referent-manifest entry, so a post-close edit refuses at
> `check_referents` — and asserted equal to the literal `0.0659` to
> four decimals as a known-answer gate. The 2k and 2l increments
> (+.054, +.0687) are printed as literals with their sources named,
> not read.

**(e) §4, replacing the `delta_sd` sentence "New line (dial h): the
null SD of Δ — per simulation, with both predictors mixed at the SAME
strength (D = 0 and D = .15), the SD of Δ … and the smallest |Δ| at
which the paired bootstrap CI95 excludes zero in ≥ 75 % of simulations
(`min_detectable_delta`)."** — with:

> New line (dial h): the SD of Δ = T(x_B thinned) − T(x_A^(256)) across
> simulated outcomes, in THREE arms — a null arm (ρ = 0) and one arm
> per test at its own calibrated strength at D = .15 (`delta_null_sd`,
> `delta_sd_at_declare_A`, `delta_sd_at_declare_B`) — plus the paired
> item bootstrap SD of Δ on the FIRST null outcome
> (`delta_boot_sd_null`, taken as the CI95 width over 2 × 1.96), from
> which `min_detectable_delta = 2.63 × delta_boot_sd_null` follows by
> the normal approximation (CI95 excludes zero with power .75). That
> formula is carried on the record as a pinned string AND the number is
> re-derived from it at analysis time (freeze F-3). The block also
> carries `k_by_rung` and `rungs`; `rungs` is R_PRIMARY minus the UNION
> of the two predictors' degeneracy sets, which can be WIDER than the
> set the annotation C reads (the intersection of the two tests'
> eligible sets, which also drops n_pos-thin rungs) — whenever it is,
> the verdict discloses the extra rungs and the licence is bounded to
> the rungs C named as read (freeze F-2, Ruling R-6).

**(f) §5, after S8c's "…mean of the two Pile-trained rows minus mean of
the three DCLM-class rows, paired item bootstrap CI95"** — add:

> The two groups are exactly `{pythia_2.8b, pythia_6.9b}` and
> `{olmo2_7b, olmo2_13b, smollm3_3b}`, and the contrast is mean(Pile) −
> mean(DCLM-class) over the rungs every one of the five rows covers,
> through the same `paired_contrast_2n` the annotation C uses — every
> row read on the SAME within-rung item resample, `n_boot` reported
> beside `n_boot_requested`.

**(g) §5, after S9's "…one table, descriptive"** — add:

> S9's four sources: this run's per-rung D for A and B; 2l's and 2m's
> per-rung D READ from their committed `results/verdict.json`
> (`tests.A/B.per_rung.<rung>.d`, referent-manifest entries, and a
> known-answer gate in the cold battery); and 2k's / 2i's OLMo-2 7B
> readings as LITERALS with their sources named — antonym A +.024
> (2k VERDICT, the 256-draw per-rung table) / B +.217 (2i VERDICT,
> Test B per rung), antonym6 A **+.115** / B +.214, odd6 A **+.096** /
> B +.121 (the antonym6 and odd6 A values corrected pre-tag by Ruling
> R-5 from the committed 2k VERDICT).

**(h) §3.10, after "…a pre-campaign referent manifest (2m's list + 2m's
verdict, seal, power, endpoint and sweep records…)"** — add:

> — 4,427 files in total, including 2m's OWN campaign artifacts (its
> 102 endpoint records, rung set, power record, 946-file sweep tree,
> `gate1.json` and `verdict.json`), which S8, S9 and C read.

**(i) §3.6, after "The every-40k subset … is printed as the grid-density
CONTROL"** — add:

> y is RE-COUNTED over the subset's own 12 points (its maximum is 12,
> not a slice of the 24-point count), and the row is stamped
> `"control": True` as a literal, not as a computed rule.

**(j) §3.1, after "the init referent is the seeded `from_config` twin of
the stage-1 config (2i/2m's construction)"** — the doc already says
"The twin's config AND tokenizer are taken at the ENDPOINT's commit
(`config_commit`); the analyzer measures `config_source` against
`f"{REPO_CKPT}@{config_commit}"`" — correct `REPO_CKPT` to
`REPO_COMMA` (2n has one repo; the analyzer measures against
`f"{bn.REPO_COMMA}@{entry['config_commit']}"`).

**(k) §1, after the annotation C's three readings and before "and
printed beside it whether the CI95 covers 2m's +.0659"** — add:

> C is printed in EVERY world and its modifier rides on the licence in
> every world: §6's cells are written under SHARED because that is
> where the two accounts agree on the world and disagree on C, but the
> annotation is defined independently of the tests (dial g) and the
> licence carries its sentence whichever world fires.

**(l) §7, in the run-plan sentence "…power printed once (with the
block-SD and Δ-SD lines)"** — add:

> The Δ-SD line adds three 200-simulation arms and two `calibrate_rho`
> calls to the power stage, so budget roughly twice 2m's 127 minutes
> for `power_2n`.

**(m) §3.10, after "Blob-bound tags: `exp2n-preregistered` binds the
analyzer, the battery module, the endpoint stage and the sweep
runner."** — add:

> The mutation battery's four logs (`mutation_build.log`,
> `mutation_fast_survivors.log`, `mutation_totality.log`,
> `mutation_fullshape.log`, plus the freeze's own) are COMMITTED
> (Ruling R-7), so the tally is reproducible from git rather than from
> the ledger's table alone.

### The instrument delta the tag will bind

`exp2n-preregistered` binds four blobs. Their shas after the freeze:

| blob | sha256 |
| --- | --- |
| `experiments/exp2n/analyze_2n.py` | (filled at the end of the freeze) |
| `experiments/exp2n/battery_2n.py` | (filled at the end of the freeze) |
| `experiments/exp2n/run/endpoint_2n.py` | (filled at the end of the freeze) |
| `experiments/exp2n/run/sweep_2n.py` | (filled at the end of the freeze) |

`run/sweep_2n.py` is UNCHANGED by the freeze — no finding touched it.

### What the freeze did NOT do

- It did not run the preflight, the endpoint stage, the power tool or
  the sweep. Zero model contact, zero network, no tokenizer load, no
  weight.
- It did not call `refresh_inventory_comma` (the ONE Hub scan is
  committed).
- It did not touch any frozen upstream module; `FROZEN_SHA256_2N`'s 54
  literals are unchanged, and `power_2n.py` / `make_referents_2n.py`
  (both inside that pin) were not edited.
- It did not re-derive the committed Hub inventory or the manifest; it
  attacked them with hand inventories instead.
- It did not change the design doc except §2's disclosure append; every
  other slip is written above as wording for Michael to ratify.
- It did not compute any statistic against a real Comma outcome — none
  exists.
- It did not re-run the full 198-mutant battery from scratch; the
  freeze's own mutants and the mutants its closures re-targeted were
  run with `--only` (see the cold re-run table), on top of the build's
  committed 192/192.

---

## Cold re-runs after the closures

| battery | result |
| --- | --- |
| fast modules, first pass after F-1..F-4 | 138 passed, 1 failed (the empty-tree test's `pins_active` literal, test-side, fixed), 260.5 s |
| fast modules, after the fixture correction | (filled at the end) |
| worlds + totality | (filled at the end) |
| cold referent battery `verify_referents_2n.py` | **14/14**, run after the closures and after the `IMPORTED_SHA256_2N` re-pin |
| read sweep `tests/read_sweep_2n.py` | 6,179 distinct paths, 8,553 open/read calls, **(e) unpinned = 0**, 0 writes, INSUFFICIENT_DATA |
| import scan `tests/import_scan_2n.py` | 4 modules, INSUFFICIENT_DATA, 11 failures, no T (the re-pinned reading) |
| the nineteen runner-left tree shapes | **19/19 INSUFFICIENT_DATA, 0 raises** — before AND after |
| determinism ×2, separate processes, one world, n_perm 30 | (filled at the end) |
| mutation battery | (filled at the end) |
