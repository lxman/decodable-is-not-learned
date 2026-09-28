# Experiment 6 — Progress Ledger

Design: ../../experiment-6-design.md (dials a–u RULED 2026-09-27).
Battery plan: ../../docs/superpowers/plans/2026-09-27-exp6-battery.md.
Entries are append-only. Every network contact is logged here when made.

## Model contact

None.

## Network contacts (build)

(none yet)

## Plan deltas awaiting ratification

B-1 … B-12, as listed in the battery plan.

## Tasks

### Task 1 — verify_6.py: five answer types (number and word are 2c's normalizer, imported), budgets 8/12/12/16/24, draw side total over 20,016 fuzzed strings per type, answer side a hard error; 8 tests.

### Task 2 — battery/spec.py: RungSpec, the registry (duplicate names and seeds refused, two-way choices refused), check_item, the driver (500 eval + 2 shots on one stream; redraw on reject / duplicate / collision / repeated answer); 9 tests.
