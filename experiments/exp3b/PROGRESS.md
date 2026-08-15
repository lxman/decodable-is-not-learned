# Exp 3b — Progress Ledger

## Build session, 2026-08-15 (post-design, pre-freeze — NO TAG)

Three-session protocol (Michael's pacing ruling, 2026-08-15): design |
build | freeze are separate sessions, boundary = context clear. The design
session produced `experiment-3b-design.md` (5026249, item 5 resolved in
3f48c94). This session built the instrument. The freeze is a LATER session
that opens adversarially: re-read doc + instrument cold with the assignment
"find the 3a-class defect — input with no value, control missing referent,
unsatisfiable criterion", record findings in the freeze checklist even if
empty, re-run the mechanical checks, then tag `exp3b-preregistered`.

**Invariant holds: first-character accuracy has been computed for NO real
cell, any size, any mode.** Every real-record read this session was
structural or aggregate: inclusion counts, floors, m3 margins, 3a record
shapes. The 3a continuations were loaded only to count them.

### Built

- `analyze_3b.py` — frozen analysis with its own loaders. 3a's floors /
  first_char (non-alphabetic fix) / score_cell / significance ported
  verbatim; new: sha-pinned floors with recompute-assert, CP-overlap
  replication gate against the 16 inclusion referents, byte gate against
  3a's 24 stored cells (tolerance ≤2, diffs disclosed verbatim
  regardless), probe-size-only contamination gate, step-5 quantifiers over
  non-contaminated reversal cells, battery shape refusals (missing /
  duplicate / valueless cells are errors, not verdicts). No branch reads
  results/m4/ anywhere.
- `run/run_cell.py` — 3a's runner on the five-size ladder. sys.path order
  correct from the start (exp2c wins; 3a's post-freeze correction cited in
  the header), `_assert_module_provenance` kept. `committed_2c_acc`
  REMOVED from the record — no m4 input exists anywhere in 3b, which is
  where 3a's `None` lived. Records carry `model_sha` (pinned revision) and
  `items_sha256` instead.
- `run/campaign_3b.py` — driver COMMITTED AT BUILD (1c's practice; 3a
  wrote its driver post-freeze and ate a correction). Order §10: all 20
  untrained twins, then trained 410m → 1b → 2.8b → 6.9b → 12b, sequential,
  skip-if-exists. Dry-run verified: 40 cells, untrained first, probe sizes
  first within each mode.
- `tests/` — 77 fixtures, one per preregistered provision, both
  directions; 9 synthetic full-shape batteries executed end to end through
  the frozen loaders (all four INSUFFICIENT_DATA routes, UNITS_ARTIFACT,
  DISSOCIATION, PARTIAL, one-rung contamination flipping the step-5
  quantifier, both-rungs contamination, eval-size twin fire as
  non-contamination); `mutation_check.py` under the corrected harness
  (pycache cleared, PYTHONDONTWRITEBYTECODE=1).

### Verified this session

- **77/77 fixtures pass**; **35/35 mutants killed** (softening AND
  hardening per gate), baseline clean.
- **`referent_check.json` 48/48**: all 16 inclusion records match design
  §4 verbatim (ctrl_copy 480/490 trained, reversal 0×8, clock24_d999
  18/24, untrained 0×8) with `sha` == the pinned `PYTHIA_SHAS` 3b loads
  and `untrained_seed` 0; all 24 byte referents structurally sound
  (500/500/500, path/content agreement); floors sha pin
  `f299fa08…` + recompute-assert clean; 20 m3 seed records present; both
  probe-size untrained twins CONSTRUCT deterministically at seed 0
  (state-dict sha256 reproduces across double construction: 410m
  `335d46b7…`, 1b `fa3fe1d2…`).
- **`probe_margins.json`**: recomputed means match design §3 to 4dp —
  rev_string7 .6263/.7725, reverse_string .5731/.6749. Per-seed values
  committed; nothing pooled.
- **`power.json`**: crit 46/500 at floor .056 (power .980 @ .12, .745
  @ .10, blind below .092); crit 44 at .054 — design §7 asserted, not
  trusted. Read through `load_floors`, so the table can never desync from
  the floors the verdict uses.
- Runner import path smoke-tested without touching a model: provenance
  assert resolves harness→exp2c / models→exp2b; all four rungs load 500
  items, answer_type `word`, MAX_NEW_TOKENS 12, 2 shots; reverse_string
  through the 2b fallback.

### Two design under-specifications, resolved in the build — FREEZE MUST RULE

The doc is a DRAFT; both resolutions are implemented, fixture-pinned, and
FREE to change until the tag. The freeze session must bless or amend
explicitly — silence is not a ruling:

1. **Gate 4 scope.** §6's step 4 says "any untrained cell"; §6's preamble
   says eval-size cells take NO significance tests. Implemented: the
   preamble governs — contamination quantifies over the 8 PROBE-size
   untrained cells; an eval-size twin fire is a descriptive fact, visible
   in the report, contaminating nothing
   (`test_eval_size_twin_fire_is_not_contamination`, battery
   `eval_twin_fire_is_not_contamination`).
2. **Both reversal rungs contaminated.** §6 says a contaminated rung is
   excluded from step 5's universal quantifiers and does not say what
   happens when the exclusion empties them. Implemented:
   INSUFFICIENT_DATA — `all([])` is vacuously true and must not be allowed
   to read as UNITS_ARTIFACT (or DISSOCIATION)
   (`test_both_rungs_contaminated_is_insufficient_data`, battery
   `contaminated_both_rungs`, mutant "vacuous quantifier allowed to
   adjudicate" killed).

### Open for the freeze session

- Adversarial cold read of doc + instrument (the assignment above), freeze
  checklist written even if empty.
- Rule on the two items above; amend §6 wording if the resolutions stand.
- Re-run cold: fixtures, mutation check, full-shape batteries,
  `verify_referents.py --construct`; record results in the checklist.
- Tag `exp3b-preregistered`.

### After the tag (campaign, §10)

Driver already committed. Untrained twins all 20 → trained 410m → 1b →
2.8b → 6.9b → 12b, commit per cell, verdict projection ledgered HERE
before the frozen analysis runs once. Estimated ~100 minutes inference on
the Mac; Sparks untouched.
