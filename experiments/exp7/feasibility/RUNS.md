# Exp 7 feasibility execution ledger

## 2026-10-04 — pre-spec inventory

- Read repository protocol, Exp 7 approved design and feasibility PLAN.
- `inventory.py` ran once with `/Users/michaeljordan/emergence-lab/.venv/bin/python`.
  Direct-source metadata only; 101 item files and lexicon/BB index pinned and
  byte-compared to approval snapshot. No old analyzer or model library import.
- Word repetition-matched pair capacities: 84–224 across 15 proposed blocks.
- Arithmetic support enumeration led to proposing digit classes (2,3), (2,4),
  (3,3), (3,4), (4,4); the (2,2) class has only 68 pre-collision triples.
- Ruling F2: use two exact quadrilateral pair classes (square/kite and
  rectangle/rhombus), as PLAN explicitly permits; cost: four target labels,
  two nominal shape blocks, not ten-label geometric diversity.
- `SPEC.md` fixes all construction, matching, rejection, collision and
  shortcut behavior before full generation or shortcut computation.

Full generation attempts: **none yet**. Tokenizer/model contact: **none**.

## Specification publication and prototype TDD

- Specification/inventory committed and pushed **cf50ef837**, before full
  generation or shortcut audit. Parent included concurrent management's work;
  only the four owned feasibility files were staged.
- First TDD invocation of `python -m unittest
  experiments.exp7.feasibility.test_feasibility` failed as expected because
  `oracle.py` did not exist (`ModuleNotFoundError`).
- Implemented stdlib-only independent rendered-question solvers, direct-source
  collision indexes, generation, audit, fixed baselines and write-once runner.
- Four initial oracle tests passed; expanded to **20 tests, all passed in
  2.181 s**. Miniature fixture is 12 pairs/family, never the full batch; it
  tests byte determinism, same-class wrong sham, old/new content duplicates,
  word reuse under new scrambles, options, endpoint uniqueness, malformed
  inputs, singleton support, label reversal and explicit N/A denominators.
- The miniature endpoint baseline succeeds on every deduction fixture. This
  was foreseeable from the declared relational graphs and is retained, not
  used to filter or redesign items. No full batch/baseline executed yet.

## Full attempts 001/002 — preserved, superseded for collision coverage

- Prototype committed/pushed **e8e32be4a** after 20 tests passed (2.164 s).
- Command `python -m experiments.exp7.feasibility.run --run-id full-001`:
  2026-10-04 17:04:40–17:04:47 UTC, 2,000 pairs / 8,000 prompts, initial
  certificate PASS. `full-002` was the one exact repeat of that version;
  `python -m experiments.exp7.feasibility.compare full-001 full-002` found
  all eight deterministic artifacts byte-identical. Receipts carry exact times.
- **Self-review defect F3, before contact:** old Exp 6 `shot_records` carry
  `meta` without a `question` field; their question bytes live separately in
  `shots`. Source indexing covered those question strings/scrambles, but the
  structural-metadata branch only ran on dicts containing `question`. Thus
  old shot deduction orders, unit number tuples and polygon keys were omitted.
  The initial certificates' structural scope is incomplete and **superseded**.
  Every initial artifact is retained unchanged under `runs/full-001` and
  `runs/full-002`; the initial byte comparison is `runs/determinism.json`.
- Ruling F3: repair this implementation omission, add a regression requiring
  all `shot_records` metadata keys, recertify in new directories, then repeat
  the corrected version once. No source/matching/stratum/baseline choice or
  substantive design constraint changes. Candidate exclusions may change if
  an omitted shot key was encountered. The endpoint shortcut remains retained.

### F3 regression and repair

- `python -m unittest experiments.exp7.feasibility.test_feasibility.OracleTests.test_old_shot_metadata_is_indexed_without_question_field`
  failed before the repair: **500 != 502** old deduction metadata records.
- Moved structural indexing to the presence of `meta`, independently of the
  question-field branch. Existing shot string indexing is retained. Added
  explicit per-shot order/number membership and 351 closed / 151 arc-or-open
  shape-record assertions.
- Full prototype suite: **21 tests passed, 2.130 s**. This fixes declared
  source coverage, without a specification change. Initial evidence committed
  and pushed at **27dcf1775** before this repair.

## Corrected full attempts 003/004 — current evidence

- Fix and regression committed/pushed **5ad3ccb07**.
- `python -m experiments.exp7.feasibility.run --run-id full-003`:
  **17:08:06.790995–17:08:13.012576 UTC**, PASS, 2,000 pairs / 8,000 questions.
- Exact repeat once: `--run-id full-004`, **17:08:16.571030–17:08:22.823846
  UTC**, PASS. Launch HEAD for both: `5ad3ccb078b559d275c6f505bad0a9d42414aa8e`.
- `python -m experiments.exp7.feasibility.compare full-003 full-004 --output
  determinism-corrected.json`: PASS, all eight deterministic artifacts equal;
  103 source pins rechecked. Receipts excluded only for run ID/UTC fields.
- The repaired coverage includes all old shot metadata: 1,004 deduction
  records, 502 unit triples, 502 unit two-number records, 351 closed polygons
  and 151 arc/open records. 241,968 unique old questions / 247,698 records.
- Adding omitted keys did not affect selection: corrected pairs, attempt
  logs, oracle results and baseline bytes equal initial runs. Certificates
  and code bindings correctly changed. No substantive reruling required.
- All 8,000 independent rendered-question oracles agree; 1,000 unique matched
  words (328 old answer-word reuses), 500 new orders, 500 new numeric triples,
  1,000 distinct shape congruence keys. No admitted old/new content or question
  collision. BIG-bench checked on 26,000 exact/legacy surfaces, with its
  hash-only structural limitation disclosed.
- Base blocks: words 15×33–34; deduction 20×25; units 5×100; shapes 2×250.
  Orientation 250/250 each family, ordered target positions 20×25 each option
  family, render orders 20/21 each. No nominal pooling.
- Fixed baseline audit: endpoint deduction **500/500** canonical and sham,
  x=1; query-direction/list-index deduction **25/500**, x=0. Every other
  applicable baseline has 0 observed paired successes /500 and x=0; explicit
  unsupported counts and 35 N/A cells retained. Full results/limitations and
  first-pair worked examples are in `REPORT.md`.
- Source inventory discovery rechecked against approval-snapshot Git paths:
  no additional committed task-item JSON/JSONL/TSV paths outside the declared
  item directories (other battery data are indexes/overlap/token-length files).
- AST import scan: stdlib plus this feasibility package only. No predecessor
  instrument import, no analyzer, tokenizer, model library or model output.

**Full generation tally: four attempts total**, two original-version runs,
two corrected-version runs (one deterministic repeat per version). All evidence
preserved, none overwritten. 21 tests pass. Fresh independent review pending.

### Saved-byte self-check before handoff

A separate inline stdlib-only check (no prototype imports or generation)
rechecked all four archived artifact manifests, 103 current source hashes,
12 current code/spec launch pins, 2,000 pair IDs and 8,000 saved oracle-answer
bindings. It independently recomputed paired success, conditional x and
unsupported counts from all **24,500 saved baseline output records**, agreeing
with all **84 cells (49 applicable / 35 N/A)**. PASS. This is an implementer
self-check, not the pending fresh review. No additional full run occurred.
