# Exp 3a — Closeout Retrospective

**VERDICT: INSUFFICIENT_DATA.** The frozen analysis could not execute on the
battery it was frozen against. Designed, frozen, run and closed 2026-08-15.

## 1. What happened

3a was built to test whether the methods paper's strongest real-model claim —
reversal is "linearly decodable ... and the model cannot emit it" — survives
matching the probe's target to the eval's. The probe decodes one character;
the eval requires seven. Matching them means scoring the first character of
the continuation against the probe's own label, on the same prompt.

The campaign collected cleanly: 24 of 24 cells, 0 failures, 81.2 minutes. The
replication gate reproduced 2c's committed accuracy exactly on all nine cells
that had a committed value. Then the frozen tree hit `float(None)` on the
three `ctrl_copy` cells and could not proceed.

## 2. The defect, precisely

The design chose `ctrl_copy` as the positive control because it carries the
same probe/eval units mismatch as reversal (1-character probe label, 5-character
answer) and yet shows no gap — probe .997, argmax .960/.980. That reasoning is
sound and I still believe it.

What I did not check is where those argmax numbers live. They are 2c's gate 4,
measured at the **probe** sizes, 410m and 1b. 2c's eval ladder is 2.8b/6.9b/12b
and it never ran `ctrl_copy`. So the rung the design leans on hardest for the
replication gate is the one rung with nothing to replicate against.

This was available at freeze. It needed one `ls` of `results/m4/*/`.

## 3. Why it closed strictly

Three amendments were on the table and Michael declined all three. The
argument for amending was real: the gate is undefined rather than violated,
and the nine cells that could be checked all passed. The argument against is
that every amendment would have been authored with the data already on disk,
and every one would have made `INSUFFICIENT_DATA` less reachable than the
frozen text made it.

A frozen criterion that binds only when it is convenient is not frozen. The
program has now spent six experiments arguing that; declining to amend here
is the first time it cost something concrete — 81 minutes of 12b inference
and a full design cycle.

## 4. What protects the successor

**The primary statistic was never computed.** First-character accuracy has
not been calculated for any cell. The tree halts at a gate that precedes the
claim, and nothing was run past it. A successor can therefore be frozen
without its designer having seen the outcome, which is the only property that
makes a re-freeze meaningful rather than cosmetic.

**The collected continuations are deterministic.** Greedy decoding over fixed
prompts reproduces byte for byte, so a successor's collection can be checked
against 3a's rather than merely repeated. What cost 81 minutes buys the
successor a reproduction referent it would not otherwise have.

## 5. Successors

1. **Verify that every verdict input has a defined VALUE on this battery, not
   only a frozen producer.** 1c's lesson was "freeze a producer for every
   input"; 3a shows the producer can exist and return `None`. The mechanical
   check is to run the frozen verdict against a synthetic full-shape battery
   at freeze time and require it to reach a terminal branch.
2. **A control chosen for one property must be checked for the others.**
   `ctrl_copy` was selected for its units mismatch and no-gap behaviour, both
   true, while the property the gate needed — an eval-ladder referent — was
   assumed.
3. **State which sizes a quoted number came from.** ".960/.980" read as
   eval-ladder accuracies in the design doc and were probe-size accuracies.
   The methods paper quotes the same figures; they are correct there, but the
   ambiguity is what propagated into this design.
4. Carry forward from 1c, unspent: report per-cell results as headline, and
   commit the driver before the campaign so records carry a clean sha.
