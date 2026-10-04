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
