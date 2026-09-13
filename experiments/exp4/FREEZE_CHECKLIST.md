# Experiment 4 — adversarial freeze (Task 6, 2026-09-11)

Fresh-eyes reviewer, cold, on `experiments/exp4/` at build HEAD
`304c9e9f`. The standing assignment, verbatim from the program: find
THE CLASS DEFECT — the defect that would silently DECIDE the verdict —
and close what is found ADDITIVELY (a new refusal, pin, test,
disclosure or record field; never an accepted dial, never a change to a
preregistered statistic or bar). Zero model contact and zero network
throughout; every execution of `analyze_4.run()` on the real tree
(`experiments/exp4/results/`, empty pre-campaign) is a disclosure event
recorded in `PROGRESS.md` with what it printed.

Python: `~/emergence-lab/.venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
from the repo root, `-p no:cacheprovider`.

Baseline, measured cold BEFORE the freeze touched anything:

| battery | result |
| --- | --- |
| fast modules (`test_metric_4`, `test_battery_4`, `test_collect_4`, `test_stages_4`, `test_analyze_4`, `test_power_4`; `-m "not slow"`) | **151 passed**, 5 deselected, 138.1 s |
| cold referent battery (`verify_referents_4.py`) | **11/11** |
| import scan (`tests/import_scan_4.py`) | 57 frozen + 6 exp4-own residual modules, **byte-identical to the committed pins** |
| read sweep (`tests/read_sweep_4.py`, real pre-campaign tree) | 3,684 distinct paths, **0 UNPINNED**, INSUFFICIENT_DATA at "4 reference seal" |
| totality (`test_totality_4.py`) | **15 passed**, 327.8 s |
| worlds (`test_full_shape_4.py`, slow) | not re-measured cold — the build's own last run was 18 passed / 1 xfailed (review round 2); re-run AFTER the closures (below) |
| mutants (`tests/mutation_check.py`) | 108 at build HEAD (78 static + 30 totality); **109 after the closures** (one new `collect_total_4` call site), every anchor still unique |

**Verdict on the assignment: the CLASS DEFECT WAS FOUND.** F-1: the
analyzer never compared any unit's MEASURED tensor digest to the
committed outcome's. A record naming a different checkpoint in
`tensor_digest` — the loader's own measurement — passed every analyzer
check as long as `committed_digest` (the runner's copy of the
*expectation*) read correctly, and that unit's alignment entered
`a_r(t)` and decided T. Design §3.4's spine is "the alignment is read
on the bytes the outcome came from, or not at all"; the runner's halt
was, from the analyzer's side, an attestation — 2i F-1's shape, 3d's
self-consistency lesson. Six further findings were found and closed,
all additively — including F-7, which the assignment's own item 20
uncovered: the build's mutation tally was not reproducible against the
current source, and the protection of every preregistered bar rested
on tests that no battery had ever shown could see them. Nothing
preregistered moved: `T_BAR_4`, `ALPHA_4`, `MIN_CLEAR_INDEX_4`,
`SE_MULTIPLE_4`, `GATE0_MIN_FRACTION_4`, `MIN_CELLS_4`/`MIN_RUNGS_4`,
the null, the bootstrap, the tree and every §5 secondary are
byte-identical to the build's — and are now pinned by a test that says
so, which is F-7's own closure.

---

## Findings

### F-1 — the per-unit digest pin compared the runner's EXPECTATION, never the loader's MEASUREMENT (THE CLASS DEFECT; 2i F-1 / 3d's lesson). CLOSED.

**The defect.** `load_record_4` stores two digests per unit:
`committed_digest` (what the runner read out of the committed 2g/2i/2m/
2n record and passed in) and `tensor_digest` (what the loader measured
on the weights it actually loaded). `battery_4.load_record_failures_4`
compared the FIRST to `battery_4.committed_step_digest_4(...)` and
required the second merely to be *present and non-null* (via
`_INFO_CONTRACT_FIELDS_4`). The two were never compared to each other.
So the only thing standing between a wrong checkpoint and `a_r(t)` was
`run/sweep_4.py`'s and `run/reference_4.py`'s own run-time halt — an
attestation from the analyzer's side, exactly what 2i F-1 closed one
experiment over and what 3d's gate-1 lesson ("self-consistent only")
names. The realistic producer of the mismatch is not tampering: it is a
loader path that silently resolves the wrong revision (2i stop #1's
class) or a resumed campaign whose `free_step_4` no-oped and whose
cache served a stale checkpoint — in which case the runner halts only
if its own comparison fires, and if it does not, nothing downstream
ever looks again.

**The executable demonstration (before the closure).** A synthetic
`(pythia_2.8b, 1000)` unit written through the real `collect_4.
write_load_4`, then its record's `tensor_digest` replaced, twice, with
`committed_digest` left correct:

```
committed_step_digest_4  : fa9362ec5c94d86b60a1aff4 ...
record committed_digest  : fa9362ec5c94d86b60a1aff4 ...
record tensor_digest     : fa9362ec5c94d86b60a1aff4 ...
[truth]  _load_one_unit_4: OK
[ATTACK] tensor_digest := 0000000000000000... -> _load_one_unit_4: NO REFUSAL
        load_record_failures_4 -> []
[ATTACK] tensor_digest := e60235f845bf3890... -> _load_one_unit_4: NO REFUSAL
        load_record_failures_4 -> []
```

The second value is **OLMo-2 7B step 1000's committed digest** — i.e. a
record that says, in its own measured field, that the activations came
off a different family's checkpoint, accepted.

**The closure (additive).** `battery_4.load_record_failures_4` now
requires `tensor_digest == expected_committed_digest` wherever a
committed digest exists, with the refusal naming the distinction. Where
no committed outcome digest exists — the four references and the seven
ladder sizes, `expected_committed_digest is None` — the bar does not
fire (there is nothing to compare to) and the contract's own
present-and-non-null check stands.

**Tests.** `test_battery_4.py`:
`test_load_record_failures_4_refuses_a_tensor_digest_that_is_not_the_committed_one`
(three wrong values: another trajectory's digest, all-zeros, `None`) and
`test_load_record_failures_4_does_not_require_a_tensor_digest_match_where_none_is_committed`.
`test_totality_4.py`:
`test_unit_tensor_digest_not_the_committed_one_gives_insufficient_data` —
the same attack through `analyze_4.run()` on the totality base tree,
INSUFFICIENT_DATA with the `tensor_digest` needle.

---

### F-2 — the depth pairing was a runner-written verdict input the analyzer never re-derived, and its KEY SET was unchecked. CLOSED.

**The defect.** Design §3.3's site pairing decides which reference site
every M site is compared against, so it fixes `a_r(t)`, hence the
trend, the excess, φ and T. `collect_4.process_model_4` computes it and
stores it on `_load.json`; `alignment_series_4` and `_gate0_site_means_4`
read `unit["record"]["pairing"]` and used it as given. `_load_one_unit_4`
pinned `sites` and `n_hidden` but never the pairing, although the
pairing is a pure function of exactly those pinned constants on both
sides.

Two attacks, with different dispositions:

- **rotated VALUES** — caught, downstream, by `per_item_alignment_4`'s
  stored-overlap cross-check (the stored `overlap_<ref>` arrays were
  computed with the true pairing, so re-deriving with a rotated one
  disagrees). Not caught on the gate-0 path: `_gate0_site_means_4`
  makes no cross-check at all, so a rotated pairing on the twin's
  record silently lowers the twin's alignment — and gate 0 is a
  "twin below endpoint" test, so lowering the twin makes it *more*
  likely to pass.
- **a dropped reference KEY** — caught nowhere. The record's `refs`
  field is checked against `REFS_FOR_4[traj]`, and all three
  `overlap_<ref>` arrays are still required on disk, but
  `per_item_alignment_4` iterates the PAIRING's keys, so a `pairing`
  naming two of three references makes `a_r` a mean over two lenses
  instead of the design's three, with every gate passing.

**The executable demonstration (before the closure).**

```
[truth]  _load_one_unit_4: NO REFUSAL (record refs field = ['ref_olmo2_7b',
         'ref_smollm3_3b', 'ref_comma_7b'], pairing keys = ['ref_comma_7b',
         'ref_olmo2_7b', 'ref_smollm3_3b'])
[truth]  antonym=0.027067 add3_mid=0.028767 mean over 34 rungs=0.028437
[ATTACK B: ref_comma_7b dropped from pairing] _load_one_unit_4: NO REFUSAL
         (record refs field = [...all three...], pairing keys = ['ref_olmo2_7b',
          'ref_smollm3_3b'])
[ATTACK B] antonym=0.026983 add3_mid=0.028650 mean over 34 rungs=0.028465
[ATTACK A: pairing values rotated by one site]
         ValueError: per_item_alignment_4: add4_mid/ref_olmo2_7b/site0:
         stored overlap disagrees with the re-derived value   <- caught
```

The synthetic references are statistically interchangeable, so the
delta here is +2.8e-5; on the real tree the three references are three
different models whose per-reference agreement S11 prints precisely
because it differs, so dropping one moves `a_r(t)` by a real amount.

**The closure (additive).** `analyze_4.expected_pairing_4(n_hidden_m,
refs)` re-derives the pairing from the pinned site families alone —
`metric_4.sites_4` on both sides and `N_HIDDEN_PIN_4` for each
reference — through the producer's own `collect_4._pairing_positions`.
`_load_one_unit_4` now requires the record's pairing to equal it
exactly, keys first (naming the reference-set error) and then values
(naming §3.3). Everything that reads a pairing on the verdict path goes
through `_load_one_unit_4` — the stage tables, the sweep tables, gate 0
and `eligibility_table_4` — so the gate-0 hole closes with the rest.
The re-derivation agrees with an honest record by construction, which a
test asserts over every real key.

**Tests.** `test_analyze_4.py`:
`test_expected_pairing_4_matches_the_producers_own_re_derivation` (all
19 stage keys + 4 first units, against `_pairing_positions` itself) and
`test_expected_pairing_4_on_the_real_33_to_37_shape_is_not_the_identity`
(the only non-identity real pairing, `[0,1,2,3,4,6,7,8,9,10,11,12]`).
`test_totality_4.py`:
`test_unit_pairing_missing_a_reference_gives_insufficient_data` and
`test_unit_pairing_rotated_gives_insufficient_data`.

---

### F-3 — the committed outcome's render, dtype and shot count were never compared to the instrument's own pins, and gate 1 is structurally blind to all three (2n F-1's shape, one field over). CLOSED.

**The defect.** Design §3.1: the representation is collected "rendered
exactly as the committed outcome sweep of M's family rendered them (a
literal table `RENDER_4 = {...}`, **asserted against the committed
records' `render` field where one exists**)". Nothing asserted it.
`RENDER_4` was a literal, checked only against itself by a unit test.

This is not reachable through gate 1, and the reason is structural:
gate 1 compares two exp4 loads of the same weights, and both render
through the same `RENDER_4`, so a wrong render agrees with itself
(2n F-1's two-sided miss, exactly). Nor can a continuation disagree —
exp4 never generates. The committed outcome record is the only witness,
and it is on disk: 2n's carry `render: "bos"`; 2g's, 2i's and 2m's
carry no `render` key at all (plain by construction of their frozen
harness). A two-sided miss of dial n's BOS prefix would put every Comma
trajectory point's representation on prompts the committed outcome
never saw, on the family with the largest `R_M` (16 rungs of the 50
cells), and nothing would say so.

The same argument applies to two neighbours of the render that the
committed record also carries and the instrument also pins: `dtype`
(`DTYPE_4 = "float16"`, a literal) and `n_shots` (2c's two shots, which
reach the prompt through `cap["shots"]`).

**The closure (additive).** `battery_4.load_outcome_4` — the one
function every consumer of the committed outcome goes through
(`analyze_4.run`, `eligibility_table_4`, `power_4.main`,
`verify_referents_4`, `full_shape`) — now refuses, per record, unless

- the record's `render` (absent ⇒ `"plain"`) equals
  `RENDER_4[family-of-this-trajectory]`,
- `dtype == DTYPE_4`,
- `n_shots == len(battery[rung]["shots"])`.

Measured on the real tree: the cold battery's item 5 runs
`load_outcome_4` over all four trajectories × 92 committed checkpoints
× 34 rungs and passes, so all 3,128 committed records agree with the
three pins.

**Tests.** `test_battery_4.py`: a parametrized
`test_load_outcome_4_refuses_an_outcome_whose_render_dtype_or_shots_disagree`
(render/dtype/n_shots, on a real copied Comma step directory),
`test_load_outcome_4_refuses_a_comma_record_with_the_render_key_removed`
(the absent-key branch — dial n's two-sided miss itself), and
`test_load_outcome_4_accepts_the_three_plain_families_with_no_render_key`
(the other three families must pass, not refuse).

---

### F-4 — the power record's `declaration`, what the verdict is READ UNDER, was attested. CLOSED.

**The defect.** Review round 1's IMPORTANT 3 had already made
`_check_power_matches_eligibility_4` check every arm's fields for
VALUE. It did not check the one field the verdict quotes:
`declaration`, which `write_verdict_txt_4` prints as "read under
{declaration}". The check accepted any member of the two-element
domain, so a record claiming `POWERED` with
`arms["0.5"]["P_LEADS"] = .10` passed, and the verdict would have been
read under a declaration its own numbers contradict. The record's
`prereg_tag` (written by `power_4.main`) was likewise never checked.

**The closure (additive).** `_check_power_matches_eligibility_4` now
re-derives the declaration from the record's OWN arms by design §4's
rule — `POWERED` iff `P(LEADS | φ = .5) ≥ POWER_BAR_4 = .75` — and
refuses a disagreement in either direction; and requires
`prereg_tag == PREREG_TAG_4`. `POWER_BAR_4` is a new analyzer constant
mirroring `power_4`'s own literal; a test asserts a real
`power_4.compute()` record passes the re-derivation.

**Tests.** `test_power_4.py`:
`test_analyzer_re_derives_the_power_declaration_from_the_records_own_arms`
(both directions, the bar's own boundary value, and three wrong prereg
tags) and
`test_a_real_compute_record_passes_the_re_derived_declaration_check`.
The pre-existing `_valid_power_record` helper gained `prereg_tag` — it
claims to model a record `power_4.main()` writes, and it lacked a field
that function stamps.

---

### F-5 — design §7's ladder/endpoint known-answer check was never built. CLOSED as a measured, recorded, NON-GATING field (ruling requested).

**The defect.** Design §7: "2g's manifest records that branch's files
as a DIFFERENT signature from `main`'s, and 2g's gate 1 found the two
byte-identical in their continuations, so the ladder's 2.8b `main`
(2c's pinned revision) is loaded separately and its activations are
**required identical** to step143000's as a known-answer check." The
build implements the two loads and nothing else: no comparison, no
record field, no refusal. A grep for the check finds only the
preflight's unrelated use of the same key.

The comparison is well defined on committed bytes, which is better
than on activations (gitignored, deleted for sweep units, possibly
absent at analysis time): `ladder_pythia_2.8b` and
`endpoint_pythia_2.8b` are both reference-stage keys with the same
pinned `n_hidden` (33), the same 12 sites, the same battery, the same
render and the same batch (32 — `PARAMS_4` gives both 2.8e9), so their
committed prompt-end set tables are comparable rung by rung.

**The closure (additive).** `analyze_4.ladder_known_answer_4(root)`
measures it from the committed set tables and `run()` carries the
result in the verdict under `known_answer`, with a `VERDICT.txt` line.
**Non-gating**: the result is never added to `failures`.

**Why non-gating, and the ruling requested (R-1).** The two loads take
different loader paths — 2b's `from_pretrained` at `PYTHIA_SHAS["2.8b"]`
(`main`, fp16) versus 2g's candidate-file path with 2g's pinned config —
and §3.7's identity-escape-hatch covers gate 1 only. Making §7's
"required identical" a refusal would let a descriptive check (the
ladder feeds S3/S4 only) halt the whole analysis on a difference the
program has never measured. Michael's call: keep it descriptive, or
promote it to a refusal.

**Tests.** `test_analyze_4.py`:
`test_ladder_known_answer_4_equal_absent_and_unequal` (both sides
absent, one side absent, equal, and one rung differing).

---

### F-6 — `load_ref_tables_4` skipped its sha check when the record did not cover a rung. CLOSED.

**The defect.** `if want is not None and got != want` — a reference
record whose `sets_sha256` lacked a rung had that rung's bytes read
unchecked. `_load_one_unit_4` requires full 34-rung coverage, so the
analyzer's own path is covered; but `eligibility_table_4` — which is
what `run/reference_4.py` calls to WRITE the committed
`eligibility_4.json`, before any analyzer has run — reaches
`load_ref_tables_4` directly, and `eligibility_4.json` is a seal-bound
verdict input.

**The closure (additive).** An absent sha is now a refusal naming the
reference and rung.

**Tests.** `test_collect_4.py`:
`test_load_ref_tables_4_refuses_a_rung_with_no_recorded_sha`.

---

## Attack list, with dispositions

The numbering is the assignment's; items 23+ are the freeze's own.

1. **A reference-set table changed after the seal.** DISPOSED — clean.
   Every reference key's `sets/<rung>.npz` is re-hashed at analysis
   time twice: by `load_record_failures_4` against the record's
   `sets_sha256`, and by `collect_4.load_ref_tables_4` on every read
   (now unconditionally — F-6). `reference_seal_paths_4` binds, per
   stage-1 key, `_load.json` + 34 `sets/*.npz` + `global.npz` +
   `align.json`, and per first unit the same minus `global.npz`, plus
   `eligibility_4.json` and `power_4.json` — 849 paths. Every file the
   reference stage WRITES is covered: the only other artifacts are
   `attested/<rung>.npz` and `activations/<rung>.npz`, which are
   gitignored (so no git tag can bind them) and whose shas are on the
   bound `_load.json`; and the reference-stage halt marker, whose
   presence is itself a refusal (item 15). `cross_reference_4`
   overwrites the four references' `align.json` AFTER `_load.json` is
   written and BEFORE the seal, so the sealed bytes are the final ones.
2. **Stored vs re-derived overlap.** DISPOSED — the primary's alignment
   is re-derived from TWO committed set tables in every case
   (`per_item_alignment_4` → `collect_4.overlap_table_4` →
   `metric_4.overlap_counts`), and a stored `overlap_<ref>` array is
   used only as a cross-check that must agree exactly. No `align.json`
   scalar reaches T: `align.json` is read only by S5/S6/S7/S9, each
   labelled ATTESTED and each non-gating. Units written with `refs=()`
   (the four references) carry no stored overlaps, so nothing is
   un-cross-checked there that matters — their sets are the *other*
   side of every re-derivation and are sha-pinned. The ladder units DO
   carry `refs` (the three non-Pythia references) and are cross-checked
   like any other unit. **The gap this attack did surface is F-2's**:
   the cross-check iterates the PAIRING, so it cannot see a reference
   the pairing omits, and `_gate0_site_means_4` does not cross-check at
   all.
3. **Can the sweep overwrite a sealed first unit?** DISPOSED — clean.
   `run/sweep_4.run` builds `rest = [s for s in GRID_4[traj] if s not
   in (endpoint_step, first_step)]`, so the sealed first unit is never
   in the work list; and it REFUSES outright (`RuntimeError`) if that
   unit is not complete. "Skip if complete" is `unit_complete_4`, which
   re-hashes all 34 files against the record, so a resumed unit whose
   bytes differ from the record is re-entered and rewritten, not
   skipped.
4. **The per-unit digest pin.** FINDING F-1.
5. **The batching pin.** DISPOSED — clean. `collect_rung_4` takes
   `key=` and refuses unless `batch_size == BATCH_4[key]`; it forces
   `tok.padding_side = "right"` itself (restoring it in `finally`) and
   `add_special_tokens=False`; items are in item-file order by
   construction (`render_prompts_4` maps over `cap["eval_items"]`). The
   record carries `batch_size` and `load_record_failures_4` pins it.
   Could the reference stage and the sweep batch differently and still
   pass gate 1? No: `BATCH_4` is derived from `PARAMS_4`, and
   `PARAMS_4["endpoint_<traj>"] == PARAMS_4[traj]` by construction, so
   the two sides of gate 1 are pinned to the same value and the
   analyzer checks each against its own key.
6. **The trend's flat set.** DISPOSED — clean. `flat_M` comes from
   `rung_sets_4(load_outcome_4(traj), load_floors())` — the committed
   argmax bits through 2d's frozen bar — and is additionally pinned by
   `RUNG_SET_PIN_4`/`T_CLEAR_PIN_4`. No alignment value can reach it:
   `rung_sets_4` never sees an alignment, and `cells_4`/`trend_4` take
   the flat list as an argument.
7. **Eligibility.** DISPOSED — clean. `run()` re-derives the whole
   table (`eligibility_table_4(root)`) and compares it to the committed
   file with `_compare_eligibility_4`, which is two-sided (a key
   present in only one side is reported) and numeric to 1e-12. The
   window rule: `phi_4` returns `None` for `t_clear_index < 2`, so
   index 0 and index 1 are excluded and index 2 gives
   `x[1] / x[-1]` — t⁻ is strictly past t_1, as §3.5 requires. A rung
   clearing at the LAST grid point is eligible and reads
   `x[G-2] / x[G-1]`.
8. **φ's arithmetic and the ties.** DISPOSED — clean. `T ≥ .25`
   exactly ⇒ LEADS; `p_+` exactly `.01` ⇒ not LEADS (strict `<`);
   `ci[1]` exactly `.25` ⇒ not FOLLOWS (strict `<`) ⇒ UNDETERMINED —
   each matching §3.9's wording. `_flip_signs` with one rung enumerates
   `[[+1], [-1]]`, so `p_+ ≥ .5` and a one-rung test can never fire;
   irrelevant in practice, since `MIN_RUNGS_4 = 3` refuses first.
   `x[-1] == 0.0` gives `phi = None` (the cell drops), and eligibility
   admits only `x_end ≥ 2·SE > 0`, so the denominator is positive
   wherever a cell exists.
9. **k-NN ties and determinism.** DISPOSED — clean, with a ruling
   requested. `knn_sets` promotes to float64, fills the diagonal with
   `-inf`, takes `np.argsort(-sims, kind="stable")[:, :k]` (so equal
   similarities break by ascending index) and sorts the winners
   ascending — a pure function of the activation bytes, asserted
   identical across two calls by `test_metric_4`. Two loads of
   identical weights therefore agree iff their fp16 activations do,
   which the preflight measures and prints. **Ruling R-2**: design
   §3.7's escape hatch, if the preflight fires it, replaces activation
   identity with "k-NN-set identity plus a disclosed activation
   tolerance" — but the build's gate 1 requires FOUR agreements
   (`sets_equal`, `activation_sha_equal`, `attested_sha_equal`,
   `digest_equal`), and the hatch's wording covers neither
   `activation_sha_equal` (a sha over the fp16 activation npz) nor the
   `pooled` member inside `attested_sha_equal` (a float32 mean, the
   most ulp-sensitive quantity in the instrument). If the hatch is ever
   invoked it must say what happens to those two.
10. **A large NEGATIVE endpoint excess.** DISPOSED — one-sided by
    design §4 rule (ii), which is what the code implements
    (`below_se = not (x_end_point >= 2·se)`), so a strongly negative
    endpoint excess is INELIGIBLE with `reason` printed, not a cell
    with an inverted φ. The recession case is not lost: §3.9's
    UNDETERMINED branch prints `p_− < .01 with T < 0` as the
    "agreement recedes before the clear" cell, and `s11_textures_4`
    carries the trajectories.
11. **The 2.8b `main` vs step143000 identity.** FINDING F-5.
12. **`RENDER_4` for comma and the position indices.** Positions
    DISPOSED — clean: `screen._position_indices` tokenizes the
    RENDERED prompt and its own prefix, both with
    `add_special_tokens=False`, so 2n's one-token `<|begin_of_text|>`
    string prefix shifts `len(full)` and `len(prefix)` by exactly one
    each and both indices still land on the question-end and prompt-end
    tokens; `_question_end_char` finds the cue by `rfind`, which the
    prefix does not disturb. The render's agreement with the committed
    outcome is FINDING F-3.
13. **Disk and memory.** DISPOSED as a disclosure (D-1). There is no
    free-space precheck before a load, and none is added: the failure
    mode is not a wrong verdict. `write_load_4` writes the 34 rungs'
    files, re-reads each and asserts array equality, writes
    `align.json`, and writes `_load.json` LAST; `unit_complete_4`
    requires `_load.json` + `align.json` + all 34 files at their
    recorded shas. So an ENOSPC (or a kill) mid-unit leaves a unit the
    runner re-enters and rewrites, and an analyzer run over it refuses
    (`_read_sets_and_overlaps` names the short unit; a torn
    `_load.json` is collected as a `JSONDecodeError`). The residual
    risk is operational: a full disk stalls the sweep without a halt
    marker. Disclosed, not closed.
14. **The import surface.** DISPOSED — clean, run by the freeze.
    `tests/import_scan_4.py` (which itself imports every stage tool by
    hand and calls `an.run()` on the real tree) printed **57 frozen +
    6 exp4-own residual modules, byte-identical to the committed
    `FROZEN_SHA256_4` / `IMPORTED_SHA256_4` literals**;
    `check_imports_4` raises on an unpinned OR drifted module and
    `run()` calls it at entry AND exit (2j F-1), both sites
    `collect_total_4`-wrapped and both killed by totality mutants. The
    closures added no import: `battery_4`, `analyze_4` and `collect_4`
    are tag-bound blobs (not sha-pinned entries), `power_4` was not
    touched, and `referents_4.json`'s only exp4 entries are
    `hub_inventory_pythia_4.json`, `power_4.py` and the calibration
    fixture — so no pin needed regenerating. Re-confirmed after the
    closures: scan output byte-identical, cold battery item 1 and
    item 3 pass.
15. **Every tree the runners can leave.** DISPOSED — clean. The
    totality battery is 19 cases after the freeze (15 before), every
    one INSUFFICIENT_DATA with a named needle and no raise: a torn
    `_load.json`; a directory where a file belongs; garbage bytes for
    an npz; a truncated npz; `gate1.json` as a list and `gate1.json`
    torn mid-token; a trajectory halt marker; an eligibility cell
    dropped; a power record naming a rung eligibility does not; a
    sweep unit with 33 of 34 rungs; a first unit with
    `committed_digest` deleted; a reference key's sets sha off by one
    hex character; the `_power_summary_4` and
    `_check_power_matches_eligibility_4` call sites' own wrappers; and
    the freeze's four: F-1's wrong measured digest, F-2's dropped
    reference and rotated pairing, and **the reference-STAGE halt
    marker** — `run()` reads five halt paths and the world builder's
    `halted` route only ever wrote a trajectory's, so
    `collect_4.reference_halt_marker_path` (what
    `run/reference_4._halt_reference` writes on a digest mismatch) had
    no case at all. Plus the empty pre-campaign tree itself, exercised
    by every real-tree disclosure below.
16. **The twin digest pin.** DISPOSED — clean. `run/reference_4.run`
    halts (no record written) when an init/twin load's measured digest
    differs from `committed_init_digest_4(traj)` — 2g's real `step0`
    digest for Pythia, the other three's `twin/_checkpoint.json` — and
    the analyzer now compares the twin record's MEASURED
    `tensor_digest` to the same value (F-1), so a twin that does not
    reproduce its committed digest cannot reach gate 0.
17. **Gate 0 per (rung, site, reference).** DISPOSED — clean on the
    reference set, with F-2's leg closed. Both the twin and the
    endpoint are written with `refs=REFS_FOR_4[traj]`, and the
    analyzer pins each record's `refs` field to that tuple and now its
    `pairing` keys to the same set (F-2), so gate 0 cannot pass on a
    twin with fewer references than the endpoint: the cell count is
    `34 × n_sites × n_refs`, and a twin missing a reference used to
    shrink the loop silently.
18. **The power record.** FINDING F-4 for the declaration and the
    prereg tag. Otherwise DISPOSED — clean: `cells`/`rungs` are
    compared to eligibility's own eligible set, `eligibility_sha256`
    to the sha of the file on disk (so a record built from a DIFFERENT
    eligibility file is refused), `n_sim` to the campaign constant with
    the test injection disclosed in `pins_active`
    (`power_n_sim_expected` / `power_n_sim_injected`), `phis` to the
    exact triple, every arm's five `P_*` and `mean_eligible_cells` for
    float type, `mean_T`/`sd_T` and `null_sd_T`/`min_detectable_T`
    `None`-legitimate only against a zero `mean_eligible_cells`, and
    `construction` for presence. The arms' own simulated numbers stay
    attested — re-deriving them means re-running the simulation — which
    is the disclosed residual (D-2), now bounded by the declaration
    being derivable from them.
19. **The read sweep's "0 unpinned" covers only the pre-seal path.**
    DISPOSED by execution — see "Post-seal read sweep" below.
20. **The mutation battery, re-run against the current source.** See
    "Mutation battery" below.
21. **Determinism.** See "Determinism" below.
22. **The design deltas B-1..B-4 and the build's own notes.** DISPOSED
    — see "Ratification items".
23. (freeze's own) **`_compare_eligibility_4`'s totality.** DISPOSED —
    two-sided, numeric to 1e-12, and its `a is None or b is None`
    branch is unreachable dead code (the branch it sits in requires
    both operands to be int/float); a `None` against a float falls to
    the final `a != b` and is reported.
24. (freeze's own) **Gate 1's coverage: counted or attested?**
    DISPOSED — counted. `gate1_rederive_4` iterates `battery_4.RUNGS`
    itself and compares whole-file bytes per rung (so every site and
    both positions of the committed prompt-end table are covered),
    plus the two records' per-rung `attested_sha256` (question-end and
    pooled) and `activation_sha256`, plus the two `tensor_digest`s;
    `gate1_failures_4` requires the rung list to BE the 34-rung set,
    not merely to be self-consistent (3d's lesson), and `run()`
    requires all four re-derived agreements (I-6's fix, verified
    present).
25. (freeze's own) **Can an `align.json` scalar reach the primary or a
    gate?** DISPOSED — no. `align.json` is read by `_align_by_step_4`
    (S5/S6/S7/S11) and `s9_cka_4` only, each inside a `_sec` wrapper
    and each labelled non-gating; the primary, eligibility, gate 0 and
    gate 1 read `sets/*.npz` bytes.
26. (freeze's own) **Does `cross_reference_4` leave a record whose
    `refs`/`pairing` no longer describe its `align.json`?** DISPOSED —
    it rewrites only `align.json`, and the four references' records
    keep `refs: []`/`pairing: {}`, which is exactly what
    `_expected_fields_4` expects for a reference key and what F-2's
    re-derivation produces for `refs=()`.

---

## Post-seal read sweep (attack item 19) — DISPOSED by execution, no finding

The pre-campaign sweep refuses at "4 reference seal", so it never
reaches the reads that happen only past it: S2's 2d and 2e verdict
records, 2d's argmax records, 2c's m4 files, 2g's predictor and strata.
Those are the reads item 19 says the "0 unpinned" result does not yet
cover. Built and run rather than argued:

- A full `stage="full"` LEADS world (seed 11, the 111-unit tree: 19
  reference keys + 4 first units + 92 sweep points + gate-1 records +
  a real `power_4.compute()` record) at
  `scratchpad/w_postseal`, built by `full_shape.build_world` — 13 min.
- `tests/read_sweep_4.py` gained a `--root=` option (a test tool; not
  a pinned module — `check_imports_4` excludes `tests/`, and
  `referents_4.json`'s only exp4 entries are
  `hub_inventory_pythia_4.json`, `power_4.py` and the calibration
  fixture, so nothing needed re-pinning). With a root given, every
  path under `<root>/results/` buckets as `world_campaign_artifact` —
  on the real tree those ARE bucket (f)'s seal-bound files — so
  UNPINNED answers the question the pre-campaign sweep structurally
  cannot. Frozen pins, the import surface and the referent manifest
  stay REAL in that run.

```
verdict (n_boot=10, NOT the experiment's verdict): LEADS — T 0.5329 ≥ 0.25, p+ 7.629e-06 < 0.01
POST-SEAL sweep against the synthetic world .../w_postseal

8084 distinct paths opened for reading (48662 total open/read calls)
  writes observed (should be 0, write=False): 0

category                       count
referents_4.json                3611
frozen_module                     62
instrument_blob                    6
sha_pin_at_load                    5
seal_bound_campaign_absent         0
world_campaign_artifact         4400
python_stdlib_venv                 0
UNPINNED                           0
```

The verdict line is the point: the run reached a TERMINAL (LEADS), so
it executed the whole tree — gate 0 per trajectory, gate 1's four
re-derived agreements, eligibility, the primary, and every one of
S1–S11 and the sensitivities — and still opened **zero** paths that
neither the referent manifest, a frozen/instrument/at-load pin, nor the
campaign tree itself covers. The `referents_4.json` count is 3,611 in
both sweeps: the post-seal secondaries opened no manifest file the
pre-seal run had not already opened, and no file outside it.

## Determinism (attack item 21) — DISPOSED, clean

`test_full_shape_4.py::test_determinism_fixture_two_processes` runs
`analyze_4.run()` twice in SEPARATE processes against the shared
`_leads_world` tree and compares the JSON byte-for-byte (git_sha and
timings excluded) — passed inside batch A's 47-test run, with the
freeze's closures in place. The k-NN kernel's own two-call determinism
on the same bytes is `test_metric_4.py`'s
`test_rotation_and_scale_invariance_exact` (its third assertion,
`np.array_equal(knn_sets(X), knn_sets(X))`).

## Mutation battery (attack item 20) — FINDING F-7, closed

### F-7 — the build's mutation tally was not reproducible against the current source. CLOSED.

**The defect.** The build ledger records "108 mutants, 106 confirmed
killed, 1 proven equivalent, 1 not killable through the harness, 0
open", with 26 of the 30 totality mutants' kills "traced by content" to
`mutation_build_part2.log`'s original run rather than re-executed. The
build itself flagged the residual risk and asked for a ruling on
whether a full re-sweep was warranted. It was. Re-run in full against
the current source, one harness instance at a time, detached, log
committed as `mutation_freeze_full.log`:

| pass | scope | suite | result |
| --- | --- | --- | --- |
| B1 | the 78 static mutants | fast modules, `--timeout=300` | **61 killed, 16 SURVIVED, 1 TIMEOUT** |
| B2 | all 31 totality mutants | `--totality`, `--timeout=900` | **7 killed, 24 SURVIVED** |

**The structural reason, established at the freeze.** `grep` over the
six FAST_TESTS modules: **no fast-suite test calls
`analyze_4.run()`** — the only callers anywhere are
`test_full_shape_4.py`, `test_totality_4.py` and the two cold tools.
A totality mutant strips a `collect_total_4(thunk, label)` wrapper
INSIDE `run()`, so the fast suite cannot observe any of mutants
79–109 even in principle; yet `mutation_build_part2.log`'s fast pass
reports every one of them killed. Those log lines cannot mean what
they appear to mean. And the sixteen static survivors are
preregistered dials (`T_BAR_4`, `ALPHA_4`, `MIN_CELLS_4`,
`SE_MULTIPLE_4`, `GATE0_MIN_FRACTION_4`) and verdict-path rules
(`cells_4`'s trend, `primary_4`'s rung-clustered bootstrap,
`_flip_signs`, the 1e-12 comparison tolerances, S1's sign, gate 0's
inclusive bar, run()'s four gate-1 agreements) whose only behavioural
cover is the world suite — which no mutation pass, at the build or
since, has ever run (`--fullshape` is ~100 minutes per mutant).

So the instrument's protection against a lowered bar or an inverted
rule rested on tests that no battery had ever demonstrated could see
them. Nothing in the instrument was wrong; the EVIDENCE that it was
right did not exist.

**The closure (additive — eleven new fast tests, no source change).**
`test_analyze_4.py` gains:

- `test_preregistered_bars_and_dials_are_at_their_design_values` —
  every §3.6/§4 dial pinned as a literal (kills #50, #51, #52, #54,
  #56 and any future edit to a preregistered bar).
- `test_verdict_tree_4_decides_at_the_exact_bars` — T at exactly .25,
  T at .22 and .21, p at exactly .01 and at .02, CI95 upper at exactly
  .25, and the cell/rung floors at 2 and 3.
- `test_cells_4_uses_the_flat_pool_as_the_trend_not_r` (#57) — built so
  a trend over R gives an excess of exactly zero at every step.
- `test_primary_4_bootstrap_resamples_whole_rungs_not_cells` (#60) —
  one 4-cell rung at .9 against three 1-cell rungs at .1: rung
  clustering reads CI95 [.1, .8385] (four cold picks at 31.6 %, three
  hot of four at 5.1 %), cell-level resampling of the same seven cells
  reads [.214, .786] and can reach neither bound.
- `test_flip_signs_values_are_exactly_plus_minus_one` (#64).
- `test_compare_eligibility_4_resolves_drift_far_below_a_tenth` (#71).
- `test_eligibility_summary_4_counts_only_the_eligible_rungs` (#73).
- `test_gate0_4_bar_is_inclusive_at_exactly_the_fraction` (#74) — a
  hand-built 170-cell case landing on exactly .90, where `>` and `>=`
  disagree.
- `test_s2_known_answer_gates_4_refuses_a_perturbed_auc` (#68, #69) —
  the 2d and 2e verdict records copied to a tmp tree and perturbed, so
  a tolerance of 1e-1 would accept a reproduction that is wrong.
- `test_s1_order_4_reports_concordance_not_discordance` (#72).
- `test_every_collect_total_4_refusal_label_is_present` — the general
  closure for all 31 wrapper mutants: the refusal surface is read from
  the source by AST and pinned by its own 31-label set, so stripping a
  wrapper removes its label and fails in milliseconds.
- `test_run_requires_all_four_gate1_agreements` (#67) — run()'s
  gate-1 condition must name `sets_equal`, `activation_sha_equal`,
  `attested_sha_equal` and `digest_equal`, with all three per-rung
  dicts fully quantified.

The last two pin a STRUCTURE rather than a behaviour, because no fast
test can reach the behaviour; disclosed as ratification item R-5.

**The confirming pass (B3), same log, against the current source:**
the 16 static survivors + all 31 totality mutants, fast suite,
`--timeout=400` — **46/47 killed**. The one survivor is #34, re-proved
equivalent below. A four-mutant probe before launching (`#50`, `#57`,
`#67` and a totality wrapper) read 4/4 killed.

**The reconciled tally, every kill pointing at a committed log line of
a run against the CURRENT source:**

| | count | evidence |
| --- | --- | --- |
| mutants | **109** (78 static + 31 totality) | `mutation_check.M`, introspected; 109 not 108 because F-5's closure added a `collect_total_4` call site |
| killed | **107** | `mutation_freeze_full.log`: B1 (61 static) + B3 (15 static + 31 totality); B2 independently killed 7 of the totality mutants under `--totality` |
| proven equivalent | **1** (#34) | below |
| not killable through the harness | **1** (#38) | B1's `TIMEOUT` line at 300 s; the build's own bounded runs at 60 s and 180 s |
| open | **0** | |
| SKIP (stale target) | **0** | every anchor still unique after the closures, checked by introspection before B1 |

**#34 re-proved equivalent at the freeze** (not taken from the ledger):

```
mutant: FAMILY_OF_KEY_4[f'endpoint_{traj}']  ->  FAMILY_OF_KEY_4[traj]
  pythia_2.8b    real 'pythia'    mutant 'pythia'    equal True
  olmo2_7b       real 'olmo2'     mutant 'olmo2'     equal True
  smollm3_3b     real 'smollm3'   mutant 'smollm3'   equal True
  comma_7b       real 'comma'     mutant 'comma'     equal True
```

`battery_4` populates both keys from the SAME source dict
(`FAMILY_OF_KEY_4.update(_FAMILY_OF_TRAJ_4)` and
`FAMILY_OF_KEY_4[f"endpoint_{t}"] = _FAMILY_OF_TRAJ_4[t]`), and
`family_of_traj_4` is only ever called on a member of
`TRAJECTORIES_4`, so no black-box test on the real module can
distinguish the mutant.

**#38 — not killable through the harness, disclosed.** Removing
`run/reference_4.run`'s any-HALTED-marker guard makes the one test
that does not mock `bt.load_battery` (it does not need to: in
unmutated code the guard raises first) proceed to collect the real
500-item × 34-rung battery through the fake-loader path. Bounded
confirmations at 60 s (build), 180 s (review round 1) and 300 s (this
freeze) all time out without resolving. A timeout is not a kill, per
the controller's standing ruling; the mechanism is understood and the
mutated path is genuinely expensive real work, not a hang.

## Cold battery, after the closures

| battery | result |
| --- | --- |
| fast modules (`-m "not slow"`) | **176 passed**, 5 deselected, 149.2 s (151 before: six closure tests for F-1/F-3/F-4/F-6, two for F-2 and F-5, twelve for F-7, and one pre-existing pin test) |
| totality (`test_totality_4.py`) | **19 passed**, 327.8 s (15 before; four new cases) |
| cold referent battery | **11/11** |
| import scan | 57 + 6, byte-identical to the pins |
| read sweep, real pre-campaign tree | 3,684 paths, **0 UNPINNED**, INSUFFICIENT_DATA at "4 reference seal" |
| read sweep, synthetic POST-SEAL world | 8,084 paths, **0 UNPINNED**, terminal reached (LEADS) |
| worlds + slow analyzer (`test_full_shape_4` + `test_analyze_4`) | **47 passed, 1 xfailed**, 6,296.5 s — every terminal (LEADS / PARTIAL / FOLLOWS / UNDETERMINED / NO-CONVERGENCE), all missing routes, gate 0's pass path, the determinism fixture, strict JSON. The xfail is the build's own pre-existing `test_leads_world_every_cell_phi_in_band` (one synthetic cell 0.0067 below the fixture's band), unrelated to the closures |
| mutants | **109; 107 killed, 1 proven equivalent (#34), 1 not killable through the harness (#38), 0 open** — every kill on a committed `mutation_freeze_full.log` line of a run against the current source |
| `check_imports_4()` / `check_referents(...)` called directly | no unpinned module, no drift, 0 referent drift |

## Real-tree disclosures (checklist item 27; every `analyze_4.run()` on `experiments/exp4/results/`)

Recorded in `PROGRESS.md` under `## Freeze`. The freeze made three,
all INSUFFICIENT_DATA, none writing anything under `results/`.

## Ratification items

### Design deltas the build raised (attack item 22)

Each is in `docs/superpowers/plans/2026-09-10-exp4-build.md` under
"Design deltas raised by this plan, ledgered for ratification"; none is
applied to `experiment-4-design.md` yet. The freeze's reading of each:

- **B-1 — the first grid point joins the reference stage.** §4's
  eligibility rule (ii) and the power stage need `a_r(t_1)` and
  `trend(t_1)`, which the design's reference stage never loads. The
  build adds the four first grid points (Pythia 1000, OLMo-2 1000,
  SmolLM3 40000, Comma 10000) to stage 1, writing them into their
  natural sweep paths, binding them with `exp4-reference-sealed`, and
  having the sweep treat them as complete and REFUSE if they are not
  (`run/sweep_4.run`). 23 loads at stage 1, not 19. **Touches a
  preregistered quantity only in the sense that §4's rule becomes
  computable at all**; the rule itself is unchanged. Needs Michael's
  word in §7, and §7's "19 loads, forward-only, ≈ 6–8 h" becomes 23.
- **B-2 — S7's pooled variant is thinned to the site family.** §3.1
  says "the average over valid tokens at every block (Huh's
  pooling)"; the build stores the pooled mean at the SITE FAMILY's
  layers only (every-3rd + final), because every-block pooled storage
  is ≈ 4.6 GB per 7B load. S7 is a named sensitivity with no α claim
  (§5, dial r), so this narrows a sensitivity, not the primary — but
  it does mean S7 is "Huh's construction at this program's depths",
  not Huh's construction verbatim, and §5's S7 wording should say so.
- **B-3 — the Pythia metadata scan.** One Hub call, metadata only
  (`HfApi().model_info(repo).sha` for 70m/160m/1.4b, the three ladder
  sizes 2b never pinned), run once on 2026-09-11T04:01:37Z, written to
  the committed `hub_inventory_pythia_4.json`, asserted against the
  `PYTHIA_COMMITS_4` literals at import, and refusing to run twice.
  Disclosed in the build ledger; belongs in §2's disclosure paragraph.
- **B-4 — the global bank is committed for reference-stage keys only;**
  the sweep records its global scalar attested. Dial g's own shape
  (only the primary's position is committed for every load) one field
  over; S3's global-bank curve is the affected reading.

### Rulings the freeze needs

- **R-1 — F-5: should §7's ladder known-answer check GATE?** The design
  says the ladder's 2.8b `main` activations are "required identical" to
  step143000's. The freeze implements the comparison on committed
  bytes and records it, non-gating. The two loads take different loader
  paths (2b's `from_pretrained` at `main` vs 2g's candidate-file path
  with 2g's pinned config) and the program has never measured whether
  they agree; §3.7's identity escape hatch covers gate 1 only. Making
  it a refusal risks halting the analysis over a descriptive check
  (the ladder feeds S3/S4 only). **Recommended: keep it descriptive,
  and read the printed number in the projection.**
- **R-2 — the escape hatch's scope (attack item 9).** §3.7: if the
  preflight shows two loads of the same weights disagreeing at the ulp
  level, the identity requirement is replaced BEFORE the tag "by a
  k-NN-set identity requirement alone plus a disclosed activation
  tolerance". The build's gate 1 requires FOUR agreements, and the
  hatch's wording covers neither `activation_sha_equal` (a sha over the
  fp16 activation npz — a tolerance cannot be expressed as a sha
  equality) nor the `pooled` member inside `attested_sha_equal` (a
  float32 mean over valid tokens, the most ulp-sensitive quantity in
  the instrument). **If the hatch is ever invoked, it must say what
  becomes of those two.** Recommended wording: k-NN-set identity on
  the committed prompt-end tables AND on the attested question-end
  tables; `activation_sha_equal` and the pooled tables demoted to a
  printed max-abs deviation under the disclosed tolerance.
- **R-3 — the `refs=()` cross-check gap.** `per_item_alignment_4`
  cross-checks its re-derived overlaps against the stored
  `overlap_<ref>` arrays, but the four reference keys are written with
  `refs=()` and carry none, and `_gate0_site_means_4` cross-checks
  nothing at all. After F-2 the pairing is re-derived, so the only
  remaining unchecked input on those paths is the reference set tables
  themselves — which ARE sha-pinned on their own records, re-hashed at
  every read (twice: `load_record_failures_4` and `load_ref_tables_4`),
  and seal-bound. **The freeze judges the gap closed by the shas and
  recommends no further change**; recorded because the asymmetry
  (trajectory units carry a second, independent check that reference
  keys do not) is real and a reader should know it.
- **R-4 — torch on the analyzer's import surface (M-7).** exp4's own
  modules import torch and transformers only inside function bodies,
  as the build's Global Constraints require — but importing
  `analyze_4` still pulls both into `sys.modules`, via the FROZEN
  `experiments/exp2b/models.py`, which imports torch at module level
  and which `battery_4` imports for `PYTHIA_SHAS`/`load_pythia`/
  `load_tokenizer`. Frozen code is never edited, so this cannot be
  closed inside exp4 without a lazy-import wrapper around `models_2b`.
  Verdict-inert: the analyzer's numerics are numpy/scipy only, no exp4
  code calls a torch function outside `run/`, and `check_imports_4`
  scopes to `experiments/` by construction (torch, numpy and scipy are
  unpinned in every prior experiment too, bucketed
  `python_stdlib_venv` by the read sweep). **Recommended: disclose in
  §7 and leave it**; the "zero model contact" claim rests on which
  functions run, not on torch being unimportable, and always has.
- **R-5 — F-7's structural tests.** Two of the freeze's closures pin a
  STRUCTURE rather than a behaviour, because no fast test can reach
  the behaviour: `test_every_collect_total_4_refusal_label_is_present`
  (the 31-label refusal surface, read by AST) and
  `test_run_requires_all_four_gate1_agreements` (the gate-1 condition
  must name all four re-derived agreements). They are honest about
  what they check and they kill the mutants that no fast test could,
  but they are not behavioural. **Recommended: accept them, and read
  the world suite as the behavioural cover** — `test_full_shape_4.py`
  exercises both paths for real, at 100 minutes a run.
- **R-6 — the 2.8b `main` vs step143000 loader paths (a consequence of
  R-1).** If Michael wants §7's check to gate, the cheap version is to
  require it only where it is cheap to satisfy: equality of the two
  keys' `tensor_digest`s, which the reference stage already measures
  and records for both.

- **R-7 — φ's null mean is ≈ .5, not 0, for cells selected at the
  eligibility bar. What does the LEADS licence get read against?**
  (Raised by the final whole-branch review, not the freeze; the code
  below is in, additively, and the reading is Michael's call.)

  **The mechanism, exactly.** §3.5's excess is
  `x_r(t) = [a_r(t) − a_r(t₁)] − [trend(t) − trend(t₁)]`, and
  `φ = x_r(t⁻) / x_r(t_end)`. The baseline `a_r(t₁) − trend(t₁)` is
  therefore in BOTH the numerator and the denominator, so under pure
  noise `Cov(x_pre, x_end) = Var(the t₁ term)` and the correlation is
  exactly ½. Conditioning on `x_end ≥ 2·SE` — §4's eligibility rule
  (ii) — selects cells with a large positive denominator and drags the
  numerator up with it. **The reviewer measured a selected-cell mean φ
  of .4957 under pure noise**; this build's own fixture reproduces it
  (`test_zero_excess_arm_selected_cell_phi_sits_near_one_half`:
  mean_T .4608 at n_sim 120, .53/.51 at two other seeds). The
  preregistered φ = 0 power arm CANNOT see this: it injects each
  cell's real `E_r`, so the eligibility bar is not binding in that arm
  and the selection never happens. Nothing preregistered is wrong —
  T's null is the SIGN-FLIP null, not "φ = 0" — but the number a
  reader will take as "the null value of φ" is ½, and the realized α
  of the LEADS rule depends on how much between-checkpoint scatter the
  real tree carries.

  **What was added (additive; no bar, statistic, rule or tree
  touched).** (a) A fourth power arm, `zero_excess`: `E_r = 0` for
  EVERY rung of R_M — the whole candidate pool, not only the cells the
  eligibility stage selected — at the measured SEs, the flat pool as
  trend, the eligibility rule re-applied per draw, through
  `cells_4 → primary_4 → verdict_tree_4`, recording the same fields as
  the other arms plus `realized_alpha_leads = P_LEADS`. (b) A
  `lambda_hat` readout computed in the ANALYZER from the sweep tables
  (the flat pool's between-step scatter of `x_r(t)` about its own
  trend, pooled in quadrature over flat rungs, over the quadrature-
  pooled item-bootstrap SE of the same quantity), carried per
  trajectory in the verdict under `calibration`; and the zero-excess
  arm re-run at noise multiples λ ∈ {1, 1.5, 2, 3} as
  `zero_excess_scatter`, so the realized λ̂ can be placed against the
  grid. (c) The analyzer REQUIRES the arm, its `realized_alpha_leads`
  (which must equal that arm's own `P_LEADS`) and the four-key scatter
  grid. (d) `verdict.json` carries `power.realized_alpha_leads`,
  `power.zero_excess_scatter` and `calibration.lambda_hat`;
  `VERDICT.txt` prints them and every arm's `P_LEADS`. (e) Tests
  above, plus the worlds' power record (n_sim 20) gains the arm.

  **The reviewer's measured numbers, which are what this is for.**
  P(LEADS | zero excess) = **.000 / .073 / .260 / .327 at λ = 1 / 1.5
  / 2 / 3**; the zero-signal worlds read T .38 / .28 at 6 eligible
  cells. So at λ = 1 the LEADS rule is calibrated (α ≈ 0 ≪ .01) and at
  λ ≥ 2 it is not (a quarter to a third of pure-noise trees reach
  LEADS) — and λ is not assumed, it is measured, per trajectory, on
  the real tree.

  **Recommended reading (Michael rules):** the LEADS licence is read
  against the zero-excess arm's realized α AT THE OBSERVED λ̂ — i.e.
  the verdict quotes `calibration.lambda_hat` beside
  `power.zero_excess_scatter`, and a LEADS that lands where the grid
  says pure noise reaches LEADS a quarter of the time is disclosed as
  such in the projection and the licence sentence. The alternative
  readings, both rejected here as changes to a preregistered quantity
  rather than disclosures: re-centring φ on ½ (that IS a new
  statistic), or raising `T_BAR_4` (that IS moving a bar after seeing
  a mechanism). Neither is proposed.

### Doc slips (apply to `experiment-4-design.md` with the ratification)

- (a) §7's "19 loads, forward-only, ≈ 6–8 h" → 23 loads (B-1).
- (b) §3.1's "the average over valid tokens at every block (Huh's
  pooling)" → at the site family's layers (B-2), with S7's §5 wording
  matched.
- (c) §2's disclosure paragraph gains the one Hub metadata call (B-3).
- (d) §3.8's storage list gains "the global bank is committed for the
  reference-stage keys; the sweep's global scalar is attested" (B-4).
- (e) §3.4's "Each trajectory point's tensor digest must equal the
  committed sweep record's `digest` for that step ... else the unit
  halts" gains "and the analyzer requires the same equality on the
  record, so the halt is not the only check" (F-1).
- (f) §3.3's pairing sentence gains "re-derived at analysis time from
  the pinned site families; the stored pairing is required to equal
  it" (F-2).
- (g) §3.1's "asserted against the committed records' `render` field
  where one exists" gains dtype and the shot count, which are asserted
  the same way (F-3).
- (h) §7's ladder sentence gains "recorded as a descriptive
  known-answer field in the verdict" or "and required" per R-1 (F-5).
- (i) §7's timing sentence is wrong about the global bank, and stage 1's
  budget follows from it (final review IMPORTANT 4). "the k-NN kernel
  over 442 cells per position (seconds) and the global bank (≈ 1–2 min)"
  → the global bank is **≈ 8–11 minutes per key**: `knn_sets` on the
  17,000-row bank is a 17,000 × 17,000 float32 similarity matrix (≈ 1.2
  GB) plus a full `argsort` of every row, once per site — 12 or 13 sites
  per key, at d ≈ 5,120 for the 12b reference. With slip (a)'s 23 loads
  (19 of which build a bank), **stage 1 should be budgeted at 10–12 h,
  not "≈ 6–8 h"**. Operationally, and not a design change: run
  `--only ref_pythia_12b` FIRST, alone, with the mlx agents down (dial
  j) — it is the one load whose weights (≈ 24 GB) and bank (≈ 4.5 GB of
  collected activations held while the bank runs) coincide as the
  campaign's memory peak, and the build now releases the weights before
  the bank rather than after the write, so the peak is the weights OR
  the bank, not both.

### Ratified 2026-09-12

Michael: "Ratified — apply the slips, close the open items, and tag."
One line per item, as ruled; the application is recorded in
`PROGRESS.md` under `## Ratification`.

- **B-1** accepted as written: the four first grid points join stage 1
  (23 loads, not 19), bound by `exp4-reference-sealed`, the sweep
  refusing if they are not complete — slip (a) applied to §7.
- **B-2** accepted as written: S7's pooled variant is stored at the
  site family's layers, and §3.1/§5 say so — slip (b) applied.
- **B-3** accepted as written: the one Hub metadata call is disclosed
  in §2 — slip (c) applied.
- **B-4** accepted as written: the global bank is committed for the
  reference-stage keys, the sweep's global scalar attested — slip (d)
  applied to §3.8.
- **R-1** ruled: §7's ladder known-answer check stays DESCRIPTIVE
  (non-gating), its printed number read in the projection — slip (h)
  applied in the descriptive form.
- **R-2** ruled: the §3.7 escape hatch takes the recommended wording —
  k-NN-set identity on the committed prompt-end tables AND on the
  attested question-end tables, with `activation_sha_equal` and the
  pooled tables demoted to a printed max-abs deviation under the
  disclosed tolerance. Applied to §3.7 as a slip.
- **R-3** ruled: no change. The `refs=()` cross-check asymmetry stands,
  closed by the shas that cover it; recorded here so a reader knows the
  trajectory units carry a second check the reference keys do not.
- **R-4** ruled: disclose in §7 and leave it. Torch reaches the process
  through the frozen `experiments/exp2b/models.py`; frozen code is
  never edited and the claim rests on which functions run. Applied as a
  §7 paragraph.
- **R-5** ruled: the two structural tests
  (`test_every_collect_total_4_refusal_label_is_present`,
  `test_run_requires_all_four_gate1_agreements`) are accepted, with the
  world suite read as their behavioural cover.
- **R-6** ruled: not needed (it was the cheap gating form of R-1, and
  R-1 does not gate).
- **R-7** ruled YES: the LEADS licence is read against the zero-excess
  arm's realized α at the observed λ̂. §6's LEADS bullet gains the
  ruled sentence verbatim, and §4 gains a paragraph naming the
  mechanism (the shared t₁ baseline in φ's numerator and denominator,
  correlated at exactly ½ under noise, with eligibility rule (ii)
  selecting on the denominator) and the zero-excess arm that prices it.
- **Doc slips (a)–(i)** applied to `experiment-4-design.md`, with
  (i)'s last sentence KEPT: the weakref test proves the weights are
  unreachable before the bank on the production runner path (open item
  1 below), so "the peak is the weights OR the bank, not both" is a
  measurement, not a hope.

### Ratification open items, closed (2026-09-12)

- **1 — the model release did not free the weights.** Three references
  outlived the release: `release_once_4`'s closure CELL, the
  `process_model_4` frame's own `model`, and — the one that decides it
  — the runner's frame, because CPython retains a call's positional
  arguments in a tuple for the whole of a keyword call. Closed: the
  closure holds the model in mutable state and clears it before the
  frozen release; `process_model_4` takes a ONE-ELEMENT BOX it empties
  before the first forward pass and clears its own binding before the
  release; both runners `del` their local and hand the box through. A
  weakref read inside an injected `global_sets_4` finds the model dead
  — on the direct call and on the real runner path. Doc slip (i)'s
  last sentence is kept on that evidence.
- **2 — S11's per-reference values** now cover every rising rung of
  R_M, not only the eligible cells, with `phi_by_ref` None + the
  eligibility reason where there is no pre-clear window, and the tally
  over the cells that have a phi. Nothing enters T.
- **3 — the two undisposed totality mutants**, one at a time, detached,
  on the committed `mutation_ratification.log`:
  `totality_aac94f02b5` (licence condition) SURVIVED, was closed with a
  totality case and re-run **1/1 killed**; `totality_330c0ce640`
  (lambda_hat) is UNOBSERVABLE under `--totality` — its site is guarded
  by `not failures` and the totality base is reference-only, measured
  (`calibration` is None with and without an injected raise, failure
  list byte-identical) — so it was killed by the FAST suite's
  structural label pin (**1/1 killed**) and given behavioural cover in
  the full-shape world, where the site is actually reached and where
  its contract is "degrade the calibration block, leave the verdict
  alone". A false pass was caught writing it: `_needle_in_failures`
  searches text containing the world PATH, and pytest names `tmp_path`
  after the test, so a needle that is a substring of its own test's
  name passes for free.

### Cold battery, after the ratification

| battery | result |
| --- | --- |
| fast (`experiments/exp4/tests -m "not slow"`) | **203 passed**, 45 deselected, 402.9 s (11 new tests: three for open item 1, one for open item 2, one totality case, and the four ruled-minor tests) |
| totality (`test_totality_4.py`) | **20 passed**, 346.7 s (19 + the licence-condition case) |
| LEADS world (the fix wave's three + the lambda_hat case) | **4 passed**, 20 deselected, 1,336.0 s |
| cold referent battery | **11/11** |
| import scan | **57 frozen + 7 exp4-own**, output byte-identical to the committed pins |
| read sweep, real pre-campaign tree | **3,685 paths, 0 UNPINNED**, INSUFFICIENT_DATA at "4 reference seal" |
| referent manifest | **3,615 files**, sha unchanged |
| mutants | the two `collect_total_4` sites the fix wave added — the only mutants of the 120 never run — are **both disposed**, one killed after its totality case, one killed by the fast suite's structural pin; the freeze's #34 (equivalent) and #38 (timeout) dispositions are untouched |

Pre-tag `analyze_4.run()` executions now total **18** (8 import scans,
9 real-tree read sweeps, 1 synthetic post-seal world), disclosed in
design §2 and itemised in `PROGRESS.md`.
