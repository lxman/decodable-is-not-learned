# Experiment 2 — Progress Ledger

Traceability ledger (process rule 8), maintained as the build proceeds. Design doc:
`../../experiment-2-design.md` (status DRAFT until flipped to Preregistered in a
dedicated commit — that flip must precede the first model query).

## Milestones

| Milestone | What | Status | Tests |
|---|---|---|---|
| M0 | Scaffold + battery item files + oracles + frozen `analyze.py` | built; committed with the DRAFT design doc; dials reviewed 2026-07-06 (see below) | 110 ✓ |
| — | **Preregistered flip** (dedicated commit, tag `exp2-preregistered`) | 2026-07-07 — thresholds/battery/analysis frozen before any model query; models staged and SHA-pinned (40eca80) | 110 ✓ |
| M1 | Inclusion: argmax at 410M/1B on all 16 candidates; scored battery fixed (`battery/items/scored_battery.json`) | runs COMPLETE 2026-07-14 (14 min total); 12/16 survive (excluded by 1b margin CP-UB vs frozen .25: alpha_order .357, deduce2 .497, entity_track .951, parity .545); battery-fixing commit awaits Michael's review | 118 ✓ |
| M2 | Gates: untrained-weights probe control, shuffled-label control, positive-control probes | — | — |
| M3 | Stage 1 (probe side): probes at 410M/1B, 5 seeds; probe scores committed + tagged | — | — |
| M4 | Stage 2 (eval side): argmax at 2.8B/6.9B/12B | — | — |
| M5 | Frozen analysis; verdict; report | — | — |

## M1 harness build, 2026-07-07 (post-freeze mechanics — no dials touched)

Inference harness built after the `exp2-preregistered` freeze, deliberately:
prompting, greedy decoding, and counting are mechanics; every threshold they are
measured against was frozen first. Operational choices, recorded per convention:

- **Chance floors are per (capability, size):** the untrained control model
  (same architecture, seeded random init, `UNTRAINED_SEED=0`) answers the same
  committed eval items; margin = (acc − chance)/(1 − chance) with trained-acc CP
  bounds mapped through the chance point estimate and the chance floor's own CP
  bounds carried alongside (not compounded).
- **Generation:** greedy (`do_sample=False`), left-padded batches of 16, pad=eos;
  `MAX_NEW_TOKENS` per answer type {number 8, word 12, letters 12, choice 6} —
  `normalize_answer` takes the first line/token, so overshoot is harmless.
- **Inclusion runs the 2-shot primary** (design §2); the zero-shot variant is
  supported by the harness for later descriptive use.
- **`run/fix_battery.py` applies the frozen rule** (1b margin CP-UB < 0.25),
  refuses to overwrite an existing `scored_battery.json`, and the campaign only
  dry-runs it: fixing the battery is a reviewed commit, not a side effect.
- **`run/campaign_m1.sh` refuses to start while M6 holds MPS** (pgrep guard).
- **Verification:** whole loop driven by fake runners in tests (118 pass);
  end-to-end CPU smoke with real pythia-410m on ctrl_copy scored 8/8 without
  touching the MPS device mid-campaign.

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

## M2/M3 probe harness build (2026-07-14, post-M1 — mechanics, ledgered BEFORE any gate runs)

- **Frozen probe module imported unchanged** via `probe_frozen.py` (sys.path shim
  to `experiments/exp1/signatures/probe.py`; design §5).
- **Positions** (the token axis of the Bonferroni family): slot 0 = last token of
  the final question text (before the "\nA:" cue; per-item index computed by
  prefix tokenization, verified against the real tokenizer in tests); slot 1 =
  last prompt token. Collection is right-padded forwards, indices from true
  lengths; storage fp16 npz per (size, mode, capability), ALL layers collected.
- **Candidate family + permutation budget:** fit-time layer thinning to every 3rd
  layer plus the final layer, ×2 positions (410m: 18 candidates, 1b: 12);
  N_PERM=2500 (add-one floor × Bonferroni: .0072 / .0048, both < the frozen .01).
  Chosen because the refit-per-permutation null at full family (50 candidates)
  needs ≥5000 perms for the bar to be reachable and ~10× the CPU. Measured fit
  cost 10–15 ms (d=1024/2048, n=2000); estimated probe program ≈ 4–8 h at 8-way
  multiprocessing (OMP_NUM_THREADS=1 per worker). All layers remain on disk, so
  this family choice is revisable pre-gate without recollection.
- **`chance` recorded per probe = empirical majority-class label frequency;
  margin normalization uses the permutation null_mean** (the probe's own
  measured no-signal accuracy); margin = 0 below the significance bar (design §3).
- **below_threshold flag = scored-battery membership** (the frozen 1b inclusion
  rule IS the below-threshold certification; design §2 keys the threshold to 1b
  only). Controls: trivially True (gates, never scored).
- **Shuffled-label stage reuses trained activations** with rng(1000+seed) permutations.
- **Runners:** `run/collect_activations.py`, `run/run_probes.py` (parallel,
  resumable per (stage,size,cap,seed)), `run/m2_report.py` (applies the frozen
  attrition/abort rules, exit 2 on shuffled fire), `run/m3_stage1.py` (assembles
  `probe_scores.json` in analyze.py's schema; refuses without a clean m2 report;
  refuses overwrite — the two-stage lock's commit+tag is manual and reviewed),
  `run/campaign_m2_m3.sh` (detached, durable logs).
- **Tests: 127 pass** — incl. a permutation-floor guard (the arithmetic bit the
  synthetic test first: 200 perms × 4 candidates makes p<.01 unreachable — the
  same trap at full scale motivated the family/N_PERM choice above).

## M1 findings (2026-07-14)

- **Empirical chance floors are 0.0 across the battery** (CP-UB .0074 at n=500,
  both sizes): untrained models emit garbage/EOS, so open-generation floors
  carry no format prior. Margins ≈ raw accuracy for this battery.
- **ctrl_next_letter is NOT reliable at 410m** (acc .338 fp16/MPS; CPU-fp32
  diagnostic: the model answers " o" to every item — model limitation, not
  harness: ctrl_copy scores .994/1.000 through identical machinery, and at 1b
  ctrl_next_letter reaches .848). The design's "known reliable already at 410M"
  assumption is empirically false for this control. Expect the M2 positive-
  control gate to fail for it at 410m; the one-ledgered-fix decision happens
  THEN, with Michael — nothing changed now.
- **parity's exclusion** (margin .500) is the answer-format prior, not parity
  ability: the trained model answers "even"; binary format does the rest. The
  frozen rule excludes it conservatively, as designed.
- **entity_track at .93 margin at 1b** (and .98 raw at 410m) suggests the task
  is surface-solvable; the inclusion rule ejecting it is the rule working.
- Campaign wall-clock 14 minutes total (est. was hours): short prompts + small
  models are fast on MPS; untrained passes near-instant (immediate EOS).

## Model staging (2026-07-07, pre-freeze; design doc "Open items" — revision pinning)

All five Pythia models staged into the HF cache (`main` revision = final
checkpoint, standard non-deduped branch, safetensors), downloaded while Exp 1's
M6 campaign held the MPS device (network/disk only). Resolved commit SHAs,
pinned here for the ledger; the run code must load by these SHAs, not by branch
name:

| Model | `main` SHA |
|---|---|
| pythia-410m | `9879c9b5f8bea9051dcb0e68dff21493d67e9d4f` |
| pythia-1b | `f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2` |
| pythia-2.8b | `2a259cdd96a4beb1cdf467512e3904197345f6a9` |
| pythia-6.9b | `c0e3eee36dc47af0c49f361c74cfe459c09f7f23` |
| pythia-12b | `bb1e3e710cdf6b524461d543cfb5ba773f0a81b6` |

## Environment notes

- Same Mac mini + venv as Exp 1 (`../../environment.md`); DGX Sparks untouched.
- 2026-07-06: macOS upgraded 26.5.1 → 26.5.2; MPS revalidated on the new OS
  (pythia-410m fp16 smoke test PASSED — no NaNs/Infs, correct greedy output). No
  Exp 2 model queries had run yet, so nothing here was invalidated.
- M1+ (model inference) queues behind Exp 1's M6 campaign — one MPS device.
- Run tests: `cd experiments/exp2 && source ~/emergence-lab/.venv/bin/activate && python -m pytest`.
