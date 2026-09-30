# Experiment 6 — pre-tag analyzer audit

Reconstructed 2026-09-29 during the OpenCode takeover. Instrument head:
`2e54bd4cf` at reconstruction. **Eleven confirmed executions on the real
Experiment 6 tree** through final ratification validation: nine in the
preceding build session, one in the takeover, one on the ratified tree
`b7e00e30c`. No campaign record existed during any of them.

Each was the read-sweep item of `verify_referents_6`. It calls
`analyze_6.run(root, n_perm=20, n_boot=5, imports_pinned=False)`, discards the
returned verdict and reports file reads. The absent predictor seal refuses
before a primary or secondary statistic can be computed. Each invocation
reported 10 PASS, 0 FAIL, 4 SKIP. This is a disclosure tally, not eleven
analyses of model output. (The count was ten at the initial reconstruction.)

## Recovered events

Times below are UTC invocation times. The event IDs identify the executed
tool calls, not repeated mentions in reports.

| # | Time | Caller | Read paths | Tool event |
|---|---|---|---:|---|
| 1 | 2026-09-28 19:48:36 | Task 3 reviewer | 308 | `toolu_019RrPHTpWgmQxTneT9xpZjQ` |
| 2 | 2026-09-28 20:01:39 | Task 4 implementer | 308 | `toolu_019MTSoem8jQ1WCxKjfNL4st` |
| 3 | 2026-09-28 20:13:25 | Task 4 reviewer | 308 | `toolu_01N4dzARsZnGXKWAxtHAbyjX` |
| 4 | 2026-09-28 21:22:47 | Fix wave 1 implementer | 308 | `toolu_01CKLHeWHBPgk2WW2YVZCtg3` |
| 5 | 2026-09-28 23:09:01 | Fix wave 2 implementer | 308 | `toolu_01Rx64ZQp3oDJFeDntiyzzoX` |
| 6 | 2026-09-29 01:35:19 | Adversarial freezer | 314 | `toolu_01DkDbGAxhAxxwJzc5m2agyB` |
| 7 | 2026-09-29 02:12:20 | Coordinator, freeze verification | 314 | `toolu_012HsQcg4iHFJRUpQAZAcyG7` |
| 8 | 2026-09-29 03:07:04 | Fix wave 3 implementer | 314 | `toolu_01SWJw7WNcF7kUjww5TpKQLK` |
| 9 | 2026-09-29 05:23:18 | Coordinator, final verification | 314 | `toolu_01J4Ltw4EujcqUCk4v7CH4JR` |
| 10 | 2026-09-29 takeover | OpenCode coordinator | 314 | Current session's single cold-battery call |
| 11 | 2026-09-30 02:04:17.363609 | OpenCode coordinator, final ratification battery | 314 | `verify_referents_6` at `b7e00e30c`; 10 PASS, 0 FAIL, 4 SKIP; no campaign tree |

The preceding session was `18e29de9-8d76-4d63-ba15-9314534cd7e1`. Its
local tool-call records and subagent records were read for the command,
working-directory context and returned output. They confirm the nine
historical invocations above. The task reports and coordinator ledger
corroborate them. Full conversation transcripts are not copied into this
repository.

## Scope and correction

The search distinguished executed commands from code written into briefs,
and the canonical repository from the prototype/rehearsal copies named
`proto`, `real` and `stage3` under the earlier session's scratch directory.
In particular, a scratch directory named `real` was a copy, not the live
Experiment 6 tree. Synthetic worlds, mutation trees and pytest temporary
roots are outside this real-tree tally. The build ran many such analyses;
the count above is not a count of every execution on every copy.

`FREEZE_CHECKLIST.md` §E correctly counted the freezer's own one call and
said the earlier build calls were untallied. Later ledger entries counted
individual calls without a program-wide total. The git-ignored ratification
draft's claim that the total was already tallied was premature. This file
supplies the recovered event list. Future calls must append to it; the
final ratification battery is now event 11. Its UTC date is September 30;
the local ledger date is September 29 (EDT).

No analyzer was run separately to reconstruct the count. No result was
written, no model or tokenizer was loaded, and no experiment rule changed.
