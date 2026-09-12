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
self-consistency lesson. Five further findings were found and closed,
all additively. Nothing preregistered moved: `T_BAR_4`, `ALPHA_4`,
`MIN_CLEAR_INDEX_4`, `SE_MULTIPLE_4`, `GATE0_MIN_FRACTION_4`,
`MIN_CELLS_4`/`MIN_RUNGS_4`, the null, the bootstrap, the tree and
every §5 secondary are byte-identical to the build's.

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

## Mutation battery (attack item 20)

PENDING — one harness instance, detached, `mutation_freeze_full.log`.

## Cold battery, after the closures

| battery | result |
| --- | --- |
| fast modules (`-m "not slow"`) | **162 passed** (151 before; eleven new tests) |
| totality (`test_totality_4.py`) | **19 passed**, 327.8 s (15 before; four new cases) |
| cold referent battery | **11/11** |
| import scan | 57 + 6, byte-identical to the pins |
| read sweep, real pre-campaign tree | 3,684 paths, **0 UNPINNED**, INSUFFICIENT_DATA at "4 reference seal" |
| read sweep, synthetic POST-SEAL world | 8,084 paths, **0 UNPINNED**, terminal reached (LEADS) |
| worlds + slow analyzer (`test_full_shape_4` + `test_analyze_4`) | **47 passed, 1 xfailed**, 6,296.5 s — every terminal (LEADS / PARTIAL / FOLLOWS / UNDETERMINED / NO-CONVERGENCE), all missing routes, gate 0's pass path, the determinism fixture, strict JSON. The xfail is the build's own pre-existing `test_leads_world_every_cell_phi_in_band` (one synthetic cell 0.0067 below the fixture's band), unrelated to the closures |
| mutants | PENDING |

## Real-tree disclosures (checklist item 27; every `analyze_4.run()` on `experiments/exp4/results/`)

Recorded in `PROGRESS.md` under `## Freeze`. The freeze made three,
all INSUFFICIENT_DATA, none writing anything under `results/`.

## Ratification items

PENDING.
