# Exp 2h — Freeze Checklist (session 3 of 3 — worked 2026-08-24)

The build ledger (`PROGRESS.md`) is the comparison; nothing here is
ticked until re-run in a fresh process. Assignment: find THE CLASS
DEFECT — the defect that would silently DECIDE the verdict — close what
is found ADDITIVELY (refusals, pins; never an accepted dial), and leave
a ratification ledger. Zero model contact, zero network throughout: the
only Hub data anywhere in the tree remains the committed
`hub_inventory_69.json` metadata scan. Baseline at the build's close
(`15e0b1ba`): suite 52, referent battery 8/8, mutation 26/26, POWERED
.979.

## Standing adversarial assignments (worked FIRST, cold)

- [x] The class defect, three lineages: (1) every verdict input pinned
      at analysis time (3c F-A); (2) every tree the runner can leave
      reaches a frozen terminal (2d F-1); (3) gate-1 coverage not
      self-consistent-only (3d).
- [x] The 17-item standing attack list, every item CLOSED / CLEARED /
      DISCLOSED with a demonstration.
- [x] Cold re-runs: suite, referent battery, worlds (every terminal),
      two-process determinism, mutation harness.
- [x] Ratification package: findings F-1…F-3 + the disclosures, with
      the exact §-level doc wording drafted (the doc itself untouched).

## THE CLASS DEFECT: FOUND (F-1)

**F-1 — the frozen verdict RAISED instead of delivering
INSUFFICIENT_DATA on nine tree shapes.** 2d F-1's lineage one level
over: §6's first terminal was unreachable from trees the analyzer can
actually be handed. Enumerated executably over 32 tree shapes built on
a full-shape world; pre-fix **9 RAISED / 23 terminal**, post-fix
**0 RAISED / 32 terminal**, with the healthy control still CONFIRMED at
the identical T (0.9812) and p (0.004975).

The nine, by route:

| tree | pre-fix exception | now |
|---|---|---|
| `gate1.json` is a JSON list | `AttributeError` | INSUFFICIENT_DATA |
| `gate1.json` is a JSON string | `AttributeError` | INSUFFICIENT_DATA |
| `gate1.json` `rungs` not iterable | `TypeError` | INSUFFICIENT_DATA |
| `gate1.json` `continuation_diffs` a list | `AttributeError` | INSUFFICIENT_DATA |
| `HALTED` is a DIRECTORY | `IsADirectoryError` | INSUFFICIENT_DATA |
| a step record is a JSON list | `AttributeError` | INSUFFICIENT_DATA |
| a `_checkpoint.json` is a JSON list | `AttributeError` | INSUFFICIENT_DATA |
| every R_69 rung thin (n_pos 0) | `ValueError` (`primary_2h`) | INSUFFICIENT_DATA |
| y constant everywhere | `ValueError` (`perm_test`) | INSUFFICIENT_DATA |

Root cause: `analyze_2g.collect` names four exceptions (ValueError,
FileNotFoundError, KeyError, RuntimeError). A torn/hand-edited tree
presents `TypeError`/`AttributeError` (a record that parses but is not a
dict) and `OSError` (`IsADirectoryError` is not a `FileNotFoundError`);
and the primary itself — `outcomes_69` → `rung_level_69` →
`sampler_counts` → `primary_2h` — sat OUTSIDE any `collect()` at all
(attack-list item 10, "argued unreachable but not gated").

Closed additively: `analyze_2h.collect_total` (2g's `collect` with the
surface widened to those shapes; frozen `collect` untouched and still
used where the input's BYTES are sha-pinned, so its shape cannot vary),
applied at the four runner-written surfaces (halt marker, gate-1 record,
gate-1 re-derivation, sweep load), at the m4/rung-set check, at every
non-gating secondary, and around a new `_primary_core` that packages the
primary computation unchanged. Plus an `isinstance(gate1, dict)` guard
on the referent echo. **One-directional by construction: a caught
failure lands in `failures` verbatim and the verdict is
INSUFFICIENT_DATA; no tree that produced a verdict can now produce a
different one.** Regression-locked in `tests/test_totality_2h.py` (16
tests) and referent check 9.

## Findings

- [x] **F-1 (above) — CLOSED.** Dial touched: NONE.
- [x] **F-2 — gate 1's zero-diff check was self-consistent only (3d's
      lesson).** `continuation_diffs_2h_path[r] == 0` is produced by a
      `zip()` over the two loader paths' continuation lists, and `zip`
      truncates to the shorter: a zero over a comparison of ZERO pairs
      reads identically to a zero over 500. The analyzer could not tell
      them apart — the record carried the result, never the coverage.
      (Not producible through 2h's own runner — `evaluate_items` raises
      if `len(preds) != len(cap["eval_items"])` — but the ANALYZER's
      zero-tolerance gate was anchored only to itself, which is exactly
      what 3d's `draws_compared == n × dps` finding was.) Closed
      additively: the runner attests `continuations_compared_2h_path`
      per rung, and `gate1_failures_69` requires it to equal
      `battery_2d.N_ITEMS` on all 34 rungs — a record without the field,
      or with a short count on any rung, is refused. Both sides
      exercised against the shared shape, not against each other's
      mocks. Dial touched: NONE.
- [x] **F-3 — the freeze tag bound a NAME, not the instrument.**
      `require_prereg_2h` asked `git tag --list exp2h-preregistered`,
      which a lightweight tag on any commit satisfies. 2h has NO stage-1
      seal (design §7), so this tag is the ONLY gate between the design
      and 6.9b's checkpoints, and the name alone cannot say the tag
      captured THIS analyzer. 2g's own `require_seal` bound its sealed
      predictor's blob; 2h dropped the binding along with the seal.
      Closed additively: `INSTRUMENT_BLOBS_2H` — `analyze_2h.py`,
      `battery_2h.py`, `run/sweep_2h.py` — each compared at the tag
      (`predictor_2g.git_blob_sha256`) to the working copy, at analysis
      time AND before the sweep; drift or a missing blob is a refusal,
      and the three shas ride on the verdict in
      `referents.prereg.instrument_blobs`. The mechanism was verified
      byte-exact against two existing tags first
      (`exp2g-predictor-sealed` → the predictor blob;
      `exp2g-closed` → `analyze_2g.py`). Dial touched: NONE.
      **Consequence for the tagger, stated plainly: the tag must be cut
      at the commit that carries the final instrument, and any post-tag
      edit to those three files requires a re-tag.** The committed data
      files need no entry — their sha literals live in `analyze_2h.py`,
      which is itself now tag-bound.

## Attack-list disposition (all 17)

| # | item | disposition |
|---|---|---|
| 1 | median-split bucketing in `sampler_beyond_probe` | **CLEARED, executably.** Replacing `_median_bucket` with a constant leaves the verdict, the reason, the primary and every other secondary byte-identical; exactly one key changes (`sampler_beyond_probe`). `tests/test_totality_2h.py::test_median_split_touches_only_its_own_secondary`. |
| 2 | W5 fires three failure causes at once (halt-check not isolated) | **CLOSED.** `test_halt_marker_present` writes ONLY the marker onto an otherwise healthy world: exactly one failure, the halt. The check is now load-bearing on its own and has its own mutant ("run(): halt marker not consulted"). |
| 3a | every runner-leavable tree → a frozen terminal (2d F-1) | **CLOSED — this is F-1.** 32 trees, 0 raised. |
| 3b | every verdict input pinned at analysis time (3c F-A) | **CLEARED.** Full read sweep (`open`/`Path.open`/`read_text`/`read_bytes`/`gzip.open`/`np.load`) over `run()` on a complete world with the real referents AND power pins in force: **918 distinct paths, 2,122 reads — 805 world-tree (the run's own records, every one content-re-derived) + 113 committed inputs, ZERO of them unpinned.** Breakdown below. |
| 3c | gate-1 coverage not self-consistent-only (3d) | **CLOSED — this is F-2.** |
| 4 | verify-criterion totality on 2h's parse surfaces | **CLEARED.** 50,072 fuzzed draw-side inputs (both answer types on the battery, adversarial + random + answer-embedding), **0 escapes**. The other parse surfaces are frozen and coverage-pinned upstream (`a2d.read_rows`: exactly items 0..499, exactly the tier's seed, exactly 64 str draws) or now behind `collect_total`. |
| 5 | would the manifest CATCH a stale-copy hazard on 6.9b? | **CLOSED, executably.** A synthetic inventory with one grid step's bin shards replaced by main's own is REFUSED (`candidate files duplicate [...]`) — `tests/test_battery_2h.py::test_manifest_refuses_a_sharded_stale_main_copy_on_the_grid`. The same test records that `stale_main_copies` stays `{0, 0}` through it (item 14). |
| 6 | no-stage-1 surface: ordering + tag spoof | **Ordering CLEARED, spoof CLOSED (F-3).** With `loaders=None` (the real path) neither `_assert_provenance` nor `real_loaders` is reached before the refusal — `test_prereg_refusal_precedes_any_loader_construction`, which also asserts the same for a present-but-drifted tag. |
| 7 | determinism across processes | **CLEARED.** Two separate processes, same referent tree, verdict JSON **byte-identical** (sha256 `a413666f397b9461477a514a5c95aeaf3ca8cf4e311796116151bc857cddc4a9`, n_perm 200, n_boot 50). |
| 8 | power record: write-once, sha-pinned, one-sided conditioning | **CLEARED + DISCLOSED.** `main()` refuses if the file exists (write-once, never re-run this session); the sha is pinned and now rides on the verdict (W9 proves the passing route). Conditioning: the sim's `n_pos` is each rung's COMMITTED FINAL count — a lower bound on the realized n_pos (2g measured ever-verifies ≈ 2× final), so the table under-states power; and `x` is the REAL committed predictor, not a resampled one, so the zero-inflation and tie structure the run will face are already inside the .979. No asymmetry of 2d F-4's kind (nothing is re-randomized on one side only). The shape caveat is the disclosure — see item 13 and the doc drafts. |
| 9 | fold in the opus review's additions | **DONE** — items 10–17 below. |
| 10 | `primary_2h`/`perm_test` outside `collect()` | **CLOSED — part of F-1.** Both refusals demonstrated on constructed trees, both now terminals. |
| 11 | `gate1_failures_69` outside `collect()` | **CLOSED — part of F-1.** Four non-dict/wrong-type gate-1 shapes demonstrated. |
| 12 | no world exercises the referents / power refusal routes | **CLOSED.** Worlds **W7** (wrong referents sha), **W8** (wrong power sha) and **W9** (BOTH real pins in force → CONFIRMED, the power declaration riding on the verdict) added to `world_specs()`; `run_world` now takes both shas. Cheap real-tree twins added in `test_analyze_2h.py` so the mutation harness kills the two "check skipped" mutants without the slow world module. |
| 13 | power sim bypasses `cells_for` eligibility | **DISCLOSED** (record is write-once; wording drafted). It models add3_mid at n_pos 19 < the 20 floor, i.e. it credits a rung the run may drop as `thin`; and it uses the final count where the realized n_pos will be larger. Both directions conservative for P(CONFIRMED) — the modelled rung is the weakest (10 of 500 items positive in x at 1b) and every other rung gains pairs. |
| 14 | `stale_main_copies` counts single-file copies only | **DISCLOSED + demonstrated** (item 5's test): true claim, wrong reason — 6.9b publishes SHARDED weights, so that counter is structurally `{0, 0}` and the duplicate-signature refusal is the load-bearing check. All 155 revisions' candidate signatures re-verified pairwise distinct inside the same test. |
| 15 | `pytorch_model.bin.index.json` downloaded unpinned | **CLEARED.** `download_entry_69` fetches every file at `revision=entry["commit"]` — an immutable, content-addressed git commit taken from the sha-pinned manifest — so the index cannot vary for a given entry. Belt and braces beyond that: the shards themselves are sha-checked, `from_pretrained` must report empty loading info (a mis-mapping shows up as missing/unexpected keys), and gate 1 re-derives the final point's tensor digest and 34 rungs of continuations through both loader paths. |
| 16 | `load_inventory_69` has no `sha_pin` | **CLEARED, executably.** The analyzer never calls it: in the 918-path read sweep `hub_inventory_69.json` appears exactly once, read by `sha256_file` for the referent manifest — hashed, never parsed, on the verdict path. Its content is re-derived (manifest rebuild) only in referent check 3. |
| 17 | `HALTED` read with `read_text()` after `.exists()` | **CLOSED — part of F-1** (`IsADirectoryError`, demonstrated and now a terminal). |

### The read sweep (item 3b), classified

| class | paths | how pinned |
|---|---|---|
| world/sweep tree (the run's own records) | 805 | re-derived, not trusted: every (step, rung) record through `an2g.step_record_failures` (bits re-verified from the continuations, `items_sha256` vs the pinned item file, commit vs the manifest entry, `predictor_sha` vs the seal); every `_checkpoint.json` sha vs the manifest's `lfs_sha256`; `gate1.json` through `gate1_failures_69` (counts vs `FINAL_COUNT_PIN_69`, digests, diffs, coverage, tag) |
| 34 item files | 34 | `battery_2d.load_item_file` sha-checks against `ITEMS_SHA_PIN` BEFORE parsing; also listed in `referents_2h.json` |
| 34 m4 6.9b records | 34 | every `correct` re-asserted against `FINAL_COUNT_PIN_69`; also in `referents_2h.json` |
| 16 committed 2d draws files | 16 | `referents_2h.json` + `read_rows`' coverage pins |
| 2d `verdict.json` (the floors) | 1 | `battery_2g.FLOORS_VERDICT_2D_SHA256` + `referents_2h.json` |
| 14 upstream code files | 14 | `battery_2g.FROZEN_IMPORT_SHA256_2G` |
| 7 exp2g code + 3 exp2g data files | 10 | `battery_2h.FROZEN_2G_SHA256` (predictor also re-pinned at `load_predictor`) |
| 2h's own `checkpoints_2h.json` / `power_2h.json` / `referents_2h.json` / `hub_inventory_69.json` | 4 | `CHECKPOINTS_2H_SHA256` / `POWER_2H_SHA256` / `REFERENTS_2H_SHA256` (self-pinned) / referent manifest |
| **unpinned verdict inputs** | **0** | — |

## The named-disconfirmer question (2g's retrospective lesson candidate)

2g's projection MISSED at the verdict level and its miss pointed one
way; the lesson candidate was that a named disconfirmer should BRACKET
the null. For 2h the projection template the supervisor seals before
the analyzer runs should name both edges, because both are informative
and only one of them is the "we were wrong" direction:

- **Low edge (the disconfirmer proper):** T < .05 with p > .5 — the
  committed sampler counts carry nothing about 6.9b's emission order.
  That is NOT-CONFIRMED and it demotes 2g's secondary to exploratory.
- **High edge (the other miss, easy to forget to name):** T ≥ .40, i.e.
  more than twice 2g's 2.8b T of .1672. CONFIRMED, but a miss all the
  same: it would say the 2.8b estimate was badly low and that something
  about the second resolution step — two new rungs (count_div13, odd6),
  a larger model, a longer grid — is doing work the design did not
  model. The record should say so rather than banking the win.
- The blind region to state either way: the null SD of T is .0209 and
  the min-detectable T at the null's 99th percentile is .0463, so the
  interval (.0463, .10) is "detected but below the effect bar" —
  NOT-CONFIRMED with the note, not silence.

## Cold battery at the freeze HEAD

- [x] Suite **79 passed** (`pytest experiments/exp2h/tests/ -q`, ~86 s;
      52 at the build + 27 new). By file: `test_battery_2h` 20 (+1, the
      sharded stale-copy refusal), `test_analyze_2h` 22 (+6: referents
      and power refusals on the real tree, the power declaration riding
      on the verdict, gate-1 coverage, the tag-drift refusal and the
      same refusal through `run()`), `test_power_2h` 5, `test_sweep_2h`
      9 (+1, the ordering test), `test_full_shape_2h` 6 (+2, W7/W8 and
      W9), `test_totality_2h` 17 (new).
- [x] Referent battery **9/9** cold (check 9 new: the three closures).
- [x] Full-shape worlds **9/9 terminals**: W1 CONFIRMED, W2/W3
      NOT-CONFIRMED (inverted named), W4/W5/W6/W7/W8 INSUFFICIENT_DATA
      by five distinct routes, W9 CONFIRMED through the real referents
      and power pins.
- [x] Totality **32 trees, 0 raised** (pre-fix 9 raised).
- [x] Determinism: byte-identical verdict across two processes.
- [x] Verify-criterion fuzz: 50,072 draw-side inputs, 0 escapes.
- [x] Mutation harness **36/36 killed** (26 from the build + 10 new:
      7 for F-1's refusal surface, 1 halt-marker, 1 F-2 coverage,
      1 F-3 drift), run detached, sources restored byte-identical.
- [x] The real tree today still delivers its own refusal: `run()` on
      the unmodified repo returns INSUFFICIENT_DATA naming the prereg
      tag, gate 1 and the sweep; the runner refuses at
      `require_prereg_2h` before any loader is built.
- [x] Zero model contact, zero network. `power_2h.json` untouched
      (write-once; never re-run).

## Notes for the tagger

1. Cut `exp2h-preregistered` at the commit that carries the FINAL
   instrument. F-3 makes the analyzer and the runner compare
   `analyze_2h.py`, `battery_2h.py` and `run/sweep_2h.py` to the blobs
   that tag holds; a post-tag edit to any of the three requires a
   re-tag, by design.
2. The design doc is NOT edited by this session. The four drafted
   paragraphs (F-1/F-2/F-3 + the two disclosures) are in
   `.superpowers/sdd/2026-08-24-exp2h-build/freeze-report.md` for
   Michael's ratification.
3. Analyzer runtime at the frozen `N_PERM = 10,000`: ≈ 5–6 minutes on
   this Mac (measured 10.0 s at n_perm 200 and 34.9 s at n_perm 1,000
   on a full-shape tree; ~31 ms per permutation across the primary and
   the five permuting secondaries, ~3.8 s of fixed cost).
