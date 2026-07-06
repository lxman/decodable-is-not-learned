# Experiment 2 — Progress Ledger

Traceability ledger (process rule 8), maintained as the build proceeds. Design doc:
`../../experiment-2-design.md` (status DRAFT until flipped to Preregistered in a
dedicated commit — that flip must precede the first model query).

## Milestones

| Milestone | What | Status | Tests |
|---|---|---|---|
| M0 | Scaffold + battery item files + oracles + frozen `analyze.py` | built; committed with the DRAFT design doc; dials reviewed 2026-07-06 (see below) | 110 ✓ |
| M1 | Inclusion: argmax at 410M/1B on all 16 candidates; scored battery fixed (`battery/items/scored_battery.json`) | — (needs MPS; queued behind Exp 1 M6) | — |
| M2 | Gates: untrained-weights probe control, shuffled-label control, positive-control probes | — | — |
| M3 | Stage 1 (probe side): probes at 410M/1B, 5 seeds; probe scores committed + tagged | — | — |
| M4 | Stage 2 (eval side): argmax at 2.8B/6.9B/12B | — | — |
| M5 | Frozen analysis; verdict; report | — | — |

## Dial review, 2026-07-06 (pre-freeze; Michael accepted all four)

1. **PASS bar kept** (p < 0.05 ∧ ρ ≥ 0.5) with an explicit limitation added to
   design §4: the correlation bar sits ~1.7σ from the null at n = 12 — a
   battery-size ceiling, not fixable by item counts; exact p always reported.
2. **Inclusion threshold confirmed** at CP-95% upper bound < 0.25 at 1B (no change).
   If attrition threatens n ≥ 10, the answer is INSUFFICIENT_DATA, never loosening.
3. **Descriptive restricted-ρ secondary preregistered** (design §4 + `analyze.py`,
   ASCENT_FLOOR = 0.05): diagnoses outcome-side flatness at Pythia scale vs a true
   null. Never scored; cannot alter the verdict.
4. **Untrained-control attrition rule fixed** (design §3): a firing untrained-weights
   control drops that capability (attrition, battery re-committed before Stage 1);
   it does not abort or spend the one-change budget. Shuffled-label failure remains
   an abort. Flagged in advance as at-risk (single-prompt-token probe targets):
   mod7, reversed-string, acronym.

## Operational choices (pre-freeze record)

- **Item files are the operationalization** (design §2): 18 files under
  `battery/items/`, generated deterministically (`battery/gen_items.py`,
  BASE_SEED=20260706, seed=BASE_SEED+spec_index) **under the canonical venv**
  (`~/emergence-lab/.venv`) — regeneration must be run there; a different
  numpy build could produce different streams.
- **Oracle independence:** every oracle parses the question TEXT (regex), never the
  generator's variables; oracle-agreement is enforced at generation time AND by
  tests against the committed files (`test_oracle_scores_100_percent_on_committed_items`).
- **Shot hygiene:** the 2 fixed few-shot examples per capability are excluded from
  item pools (a duplicated shot would carry its own answer in the prompt).
- **Split hygiene:** word-pool tasks (unscramble, acronym, alpha_order, cipher,
  ctrl_copy) partition their word pools eval/probe-disjoint (Exp 1's entity-split
  discipline); number-space tasks are item-disjoint by uniqueness.
- **Letter-stratified sampling** for first-letter probe targets (unscramble,
  acronym, cipher, ctrl_copy): letters drawn uniformly over letters with ≥3 eval /
  ≥12 probe pool words, then the word — otherwise rare first letters starve the
  rarest probe class below ~30 examples (caught by
  `test_probe_labels_have_usable_cardinality` before any data).
- **alpha_order probe target changed at implementation** from "first letter of the
  answer" to "list position of the answer (1–4)": balanced by construction, and a
  cleaner intermediate (letter-stratifying a min-of-4 draw is awkward). Recorded in
  the design doc's implementation-decisions note.
- **Positive controls allow duplicate items** (question spaces of 25 and ~1.2k);
  they are gates, never scored.
- **analyze.py frozen logic:** verdict precedence INSUFFICIENT_DATA → FAIL → PASS →
  INDETERMINATE (conservative: a CI including 0 can never be published as a pass);
  Spearman with average-rank ties; one-tailed MC permutation (10⁵, seeded, add-one);
  case-resampling bootstrap (10⁴, seeded). Tag to be applied at the Preregistered
  flip, before any model query.

## Environment notes

- Same Mac mini + venv as Exp 1 (`../../environment.md`); DGX Sparks untouched.
- 2026-07-06: macOS upgraded 26.5.1 → 26.5.2; MPS revalidated on the new OS
  (pythia-410m fp16 smoke test PASSED — no NaNs/Infs, correct greedy output). No
  Exp 2 model queries had run yet, so nothing here was invalidated.
- M1+ (model inference) queues behind Exp 1's M6 campaign — one MPS device.
- Run tests: `cd experiments/exp2 && source ~/emergence-lab/.venv/bin/activate && python -m pytest`.
