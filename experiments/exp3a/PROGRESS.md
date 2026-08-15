# Exp 3a — Ledger

## 2026-08-15 — origin

Came from a survey of what research was left after 1c closed. The intent was
to design a sampling experiment on the reversal capability, whose probe
margin (.699, 2nd of 34) and zero eval accuracy make it the program's
sharpest real-model datum.

**The premise did not survive reading the committed items.**
`probe_label_space` for `rev_string7` is "last letter of the 7-letter input
(26)". The probe decodes ONE character; the eval requires the full SEVEN,
exact match. The methods paper's §8 claim — "linearly decodable ... and the
model cannot emit it" — compares a 1-symbol read against a 7-symbol
generation.

14 of 27 rungs share the shape. `ctrl_copy` has the same mismatch and shows
NO gap (.997 probe, .96/.98 argmax), which makes it a confound rather than
an artifact — but the reversal gap cannot be called a dissociation until the
targets match.

Structurally: Exp 1's units failure a third time, 2c's chance-floor defect
one level over. Three instances is why this is tested rather than argued.

## 2026-08-15 — the test the mismatch makes available

`activations.py:65` and `harness.py:67` build the prompt with the identical
call, so probe and eval see the SAME 2-shot prompt, and the probe's target
is by construction the FIRST character of the correct answer. Score the
first character of the continuation against the probe's own label: same
prompt, same 26-way space, same normalization. Commensurable by
construction, which is what Exp 1 died for lacking.

## 2026-08-15 — rulings

| # | ruling | by |
|---|---|---|
| a | Scope: reversal + `ctrl_copy` (positive control, same mismatch) + `clock24_d999` (matched control); matched-target primary, sampling explicitly out of scope | Michael |
| b | Check open item 5, then freeze | Michael |

## 2026-08-15 — FROZEN

Tag `exp3a-preregistered`. Checklist all GREEN, nine items, none disclosed
as gaps. Two design defects and one tooling defect found and fixed before
the tag; see `FREEZE_CHECKLIST.md`.

**One pre-committed change: UNSPENT.**

## Next

1. Untrained twins first, all 12, before any trained cell.
2. Trained cells 2.8b → 6.9b → 12b, commit per cell.
3. Ledger the verdict projection, then run the frozen analysis once.
4. Whatever the outcome, edit the methods paper's §8 accordingly.
