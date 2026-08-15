# Exp 3a — Freeze Checklist

Adjudicated 2026-08-15, before the `exp3a-preregistered` tag. GREEN =
verified, RULED = a judgement call recorded with its reasoning.

## The frozen artifact

`experiment-3a-design.md` + `experiments/exp3a/analyze_3a.py` (with its own
loader) + `chance_floors.json` + `run/run_cell.py` + the 24-fixture suite.

| # | item | status |
|---|---|---|
| 1 | Analysis written, loader frozen with it | **GREEN** — `chance_floors` → `load_cells` → `verdict` is one fixture-tested path |
| 2 | Runner | **GREEN** — `run/run_cell.py`, skip-if-exists, reuses 2c's prompt/decode/verify path unmodified |
| 3 | Chance floors computed from items and committed | **GREEN** — `chance_floors.json`, before any model is queried |
| 4 | Untrained twin constructible | **GREEN** — `models.load_pythia(size, untrained=True, seed=0)`, 2c's own `UNTRAINED_SEED` |
| 5 | Token cap cannot truncate before a first character | **GREEN** — measured (below) |
| 6 | Fixtures, mutation-tested both directions | **GREEN** — 24 fixtures, **15/15 mutants killed** |
| 7 | Every input the verdict takes has a frozen producer | **GREEN** — `verdict(cells, floors)`; `cells` from `load_cells`, `floors` from `chance_floors`, both in the frozen module (1c's gap, closed) |
| 8 | Nothing queried before the freeze | **GREEN** — items, tokenizer and committed 2c records only |
| 9 | One pre-committed change | **GREEN — UNSPENT** |

## Item 5, resolved by measurement

`answer_type` is `word` for all four rungs → `MAX_NEW_TOKENS = 12`. Answer
token lengths (pythia tokenizer, leading space): `rev_string7` max 7 / mean
4.3; `reverse_string` max 5 / 3.1; `ctrl_copy` max 5 / 3.2;
`clock24_d999` max 1 / 1.0. Five tokens of headroom on the worst case, so
the cap cannot truncate a correct answer, and can only prevent a first
character if all twelve tokens are whitespace — which is a genuine failure
to emit and is scored incorrect, not dropped. The runner stores the raw
continuation per item, so "truncated" and "emitted nothing" stay separable
after the fact.

## Two defects found before the freeze

**The positive control's floor was unbeatable.** `ctrl_copy`'s `copy_first`
floor is **1.0000** by construction — it is a copy task, so echoing the
input scores perfectly. Taking the maximum of the three floors would have
set its floor at 1.0, made the positive-control gate fire unconditionally,
and left `INSUFFICIENT_DATA` as the only reachable verdict. Fixed by
deriving `copy_is_the_task` from the items (`copy_whole > 0.5`) and
excluding `copy_first` where copying IS the capability. Derived, not
declared: a hand-set per-rung flag deciding a gate is exactly what gets
tuned once an outcome is visible.

**The scorer zeroed the matched control.** `first_char` required
`isalpha()`. `clock24_d999`'s probe label is a **digit**, so every correct
answer scored False and that rung would have read exactly zero at all six
cells — a dramatic-looking result manufactured entirely by the scorer.
Found by mutation testing, not by reading. Now any non-whitespace character
counts.

## A defect in the mutation harness itself

The first 3a run reported 11/15, then 13/15 with two survivors that died
when applied by hand. Cause: the harness wrote a mutated file and
immediately ran pytest, and Python invalidates cached bytecode on
(mtime, size). `max` → `min` is the same length, so a same-second write
left a stale `.pyc` and the mutation never reached the interpreter. The
harness now clears `__pycache__` and sets `PYTHONDONTWRITEBYTECODE=1`
before every run.

**Exp 1c's published 20/20 was re-verified under the corrected harness and
holds at 20/20.** That claim appears in `experiment-1c-design.md` and was
worth re-checking rather than assuming.

## Amendment, 2026-08-15

`run/run_cell.py` was corrected after the tag — inverted `sys.path` order and
the `render_prompt` source. The frozen artifact differs from
`exp3a-preregistered` by that one file. No criterion, threshold, floor or
verdict branch changed; zero records existed at the time. See PROGRESS.md.
The pre-committed change remains UNSPENT.

## What could still make this experiment worthless

1. **A null could be a decoding artifact rather than a capability fact.**
   Greedy decoding only. If the model would emit the right first character
   under sampling but not greedily, DISSOCIATION overstates. §7 says this
   is Experiment 3's question; a DISSOCIATION result makes that experiment
   worth running and does not pre-empt it.
2. **Four rungs, one family.** A units artifact on reversal says nothing
   about the other twelve mismatched rungs.
3. **The replication gate could fail for uninteresting reasons** —
   transformers or tokenizer drift since 2c — and would halt the
   experiment at `INSUFFICIENT_DATA` before the claim is reached.
