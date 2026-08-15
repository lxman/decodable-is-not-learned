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

## 2026-08-15 — POST-FREEZE CORRECTION TO A FROZEN FILE, disclosed

**`run/run_cell.py` was modified after the `exp3a-preregistered` tag.** The
frozen artifact now differs from the tag by that one file. Recorded here
rather than folded quietly into a campaign commit.

**What happened.** The first campaign launch failed on all 24 cells with
`ImportError: cannot import name 'ITEMS_DIR' from 'harness'`, resolving to
**exp2b's** harness. The runner's `sys.path` loop inserted exp2c then exp2b,
and `sys.path.insert(0, ...)` puts the last inserted first — so exp2b won.
exp2c must win: only its harness defines `ITEMS_DIR`, `answer_type_of`,
`verify`, and the `render_prompt` that produced 2c's committed eval numbers.

Two changes: the path order is reversed, and `render_prompt` is imported from
2c's `harness` rather than `battery.base` (exp2b defines it in
`battery/base.py`, exp2c in `harness.py`, and the two bodies differ — 2c's is
the one the replication gate checks against).

**Why this is not the pre-committed change.** It alters no criterion, no
threshold, no floor and no verdict branch. It makes a non-executable runner
executable. Zero records existed when it was made — the failed launch wrote
nothing — so there was no data for a design to be tuned against, which is the
thing a freeze protects. Precedent: 1b wrote and committed its missing record
loader after its freeze on the same reasoning. **The one pre-committed change
remains UNSPENT.**

**The crash was lucky, and that is the part worth keeping.** Had exp2b's
harness happened to define `ITEMS_DIR`, all 24 cells would have run to
completion through the wrong tree — a different `MAX_NEW_TOKENS`, a different
`verify` — and produced plausible wrong numbers that nothing downstream would
have flagged. A `_assert_module_provenance()` guard now refuses to run any
cell unless `harness` resolves under exp2c and `models` under exp2b.

**Third occurrence of the same mistake in one session.** The identical
inverted-order bug was written into `paper/refit_per_candidate_2c.py`, caught
there by its mandatory reproduction check, fixed — and I did not go back to
check `run_cell.py`, which already had it. Fixing an instance of a bug is not
fixing the bug.

## Next

1. Untrained twins first, all 12, before any trained cell.
2. Trained cells 2.8b → 6.9b → 12b, commit per cell.
3. Ledger the verdict projection, then run the frozen analysis once.
4. Whatever the outcome, edit the methods paper's §8 accordingly.
