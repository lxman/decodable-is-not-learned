# Exp 2i — Freeze Checklist (session 3 of 3 — worked 2026-08-26)

The build ledger (`PROGRESS.md`) is the comparison; nothing here is
ticked until re-run in a fresh process. Assignment: find THE CLASS
DEFECT — the defect that would silently DECIDE the verdict — close what
is found ADDITIVELY (refusals, pins; never an accepted dial or
statistic), and leave a ratification ledger. Zero model contact, zero
network throughout: the only Hub data anywhere in the tree remains the
committed `hub_inventory_olmo.json` metadata scan, and
`power_2i.json` was never created (it is a stage-2 artifact).
Baseline at the build's close (`301bbf64`): suite 235, referent
battery 11/11, mutation 89/89.

## Standing adversarial assignments (worked FIRST, cold)

- [x] Ruling 21's residuals R-1…R-4, before anything else.
- [x] The class defect, four lineages: (1) every verdict input pinned
      at analysis time (3c F-A); (2) every tree the three runners can
      leave reaches a frozen terminal (2d F-1 / 2h F-1); (3) gate-1
      coverage not self-consistent-only (3d / 2h F-2); (4) the tag
      binds the instrument, not a name (2h F-3).
- [x] The 28-item standing attack list, every item CLOSED / CLEARED /
      DISCLOSED with a demonstration.
- [x] Cold re-runs: suite, referent battery, worlds (every terminal),
      totality sweep, verify-criterion fuzz, two-process determinism,
      read sweep, mutation harness.
- [x] Ratification package: findings F-1…F-5 + the disclosures, with
      the exact §-level doc wording drafted (the doc itself untouched).

## Residuals from the fix-wave re-review (Ruling 21) — all four CLOSED

| # | what | closure |
|---|---|---|
| R-1 | the specified bits-not-continuations mutant was substituted by `cont_diff = 0`, and nothing in the 235-test battery would have killed it (every gate-1 test flips a bit and its continuation together) | `test_gate1_rederive_7b_catches_a_continuation_only_mismatch` — two continuations differ, both items verify identically, bits held equal — plus the specified mutant. Killed. |
| R-2 | `_undefined_result_2i` wrote `float("nan")` into `stratified.T`, so an undefined test put a bare `NaN` token in verdict.json (json `allow_nan` defaults True) | T is `None`; `fires_2i`/`named_inside_2i` guard on it, `verdict_tree_2i` formats through `_fmt_T` ("undefined"). The WRITE path is sanitized too (`_json_safe` + `allow_nan=False`) because NaN is also reachable from `stats_2g.d_from_pre` in the non-gating `extra_rungs_raw` descriptive and from `bootstrap_d`'s lo/hi. A strict-parser test (`parse_constant` raises) loads the written file. Presentation only — `v` itself is untouched, asserted. |
| R-3 | the resume deadlock: `records_complete_7b` checked rung records only, so an interrupt between the last rung write and the checkpoint-record write left a step the runner skipped forever and a tree `load_sweep_7b` refused forever | a step is complete only when its checkpoint record exists; the resume re-enters, skips every rung record present, writes the record (cost ≈ one checkpoint load). Both `run_step` and `run_twin` tested against the exact on-disk state an interrupt leaves. |
| R-4 | `seal_2i` used `bt.load_battery`; the attested-only gate-1 `collect_total` label was a PREFIX of the byte-identity one ("… re-derivation" matched both); `test_gate1_rederive_7b_missing_records` never reached the stage1_final-missing branch (the sweep branch `continue`d past it); two dead imports | all four applied; the label is now "gate 1 olmo7b attestation". |

## THE CLASS DEFECT: FOUND (F-1)

**F-1 — the predictor stage's provenance was ATTESTED and never
MEASURED.** 2h's F-2 / 3d's lesson, one stage over.

`analyze_2i.run()` read x_B from `results/predictor/olmo1b/<rung>.draws
.jsonl.gz` (`sampler_counts_olmo` opens ONLY the draws file) and never
once opened `results/predictor/olmo1b/<rung>.json` — the record that
says WHICH OLMo-2 1B checkpoint produced those draws, against WHICH
item file, at which seed / k / temperature / truncation / dtype. Nor
was `predictor_2i.json`'s own `sampling` block ever compared with
anything: `run/seal_2i.py` writes `revision` from the code LITERAL
`battery_2i.REV_1B_ENDPOINT`, so the seal's attestation is true by
construction and carries no information about what actually ran.

Demonstrated executably on a full-shape world: rewriting all 34
records to claim `revision: "main"`, `family: "pythia"`, `size: "1b"`,
a wrong `items_sha256`, `n_items: 7`, `seeds: [99]`, `draws_per_seed:
1`, `temperature: 0.0`, `truncation: "top_p"` — and the seal's own
`sampling` to match — left the verdict **byte-identical** (SHARED,
same sha256 over the whole dict) with **zero** failures mentioning a
predictor record. The worlds were the tell: `tests/full_shape.py` had
been writing the one-key stub `{"rung": r}` as the per-rung record and
every terminal passed.

Why it would DECIDE the verdict: x_B is Test B's entire predictor. A
stage 1 run at OLMo-2 1B's `main` instead of the pinned stage-1
endpoint — design §9 dial d's explicitly rejected alternative, a
different data mixture and a different question — would have supplied
it in silence, moving the world between SHARED and LINEAGE/BOTH with
nothing in the record to say so.

Closed additively, in the shape 2h's F-2 fix took — every field
re-derived against a source that was ALREADY pinned (the sha-pinned
manifest, the `ITEMS_SHA_PIN`-pinned battery, 2i's own frozen
constants), nothing new trusted:

* `predictor_record_failures_2i(rec, rung, cap, entry_1b)` — repo
  family/size, `mode`, revision (`stage1-step1907359-tokens4001B`,
  never `main`), commit vs the manifest's own, `items_sha256` AND the
  record's own 500-entry answer column vs the pinned item file,
  answer type, 2c's `max_new_tokens`, and the protocol
  (`seeds == [0]`, `draws_per_seed == k_total == 64`, `temperature ==
  1.0`, `truncation == "none"`, `dtype == float32`, `untrained_seed
  is None`, exp3's `stream_namespace`), plus the tallied draw count
  required to be the full 32,000 — 2h's F-2 coverage standard applied
  to the predictor stage.
* `load_predictor_records_2i` — all 34, its own `collect_total` site.
* `_check_predictor_seal_sampling` — the seal's literals measured
  against 2i's frozen constants AND against all 34 records
  (revision and commit, rung by rung).
* `_check_predictor_counts_2i` — the record's own attested
  `full_string` total and the seal's own per-item `counts` compared
  against x_B **as the verdict re-derives it from the raw draws**,
  through the production reader. An attestation that disagrees with
  the bytes is a failure whichever side is right (3d's shape).
* `run/seal_2i.py` applies the SAME function (not a copy) and refuses
  to seal, so a stage 1 at the wrong checkpoint is refused BEFORE the
  predictor tag exists rather than at close-out.

**One-directional by construction:** every new check contributes to
`failures`, whose only effect is INSUFFICIENT_DATA. No tree that
produced a verdict can now produce a different one. Dial touched:
NONE. Eleven killing mutants; six totality shapes; nine unit tests;
two runner-side refusal tests.

## Findings

- [x] **F-1 (above) — CLOSED.** Dial touched: NONE.
- [x] **F-2 — a truncated or corrupt gzip draws file RAISED out of the
      frozen verdict.** 2h F-1's lineage one file type over: 2i is the
      first analyzer in this line to read a GZIP file on the verdict
      path (`sampler_counts_olmo` → `analyze_2d.read_rows`), and a
      truncated stream raises `EOFError` while a corrupt one raises
      `zlib.error` — neither an `OSError` nor a `ValueError`, so 2h's
      widened `collect_total` let both straight through. Demonstrated:
      `antonym`'s draws truncated to 50% and to 99% on a full-shape
      world, `run()` raised `EOFError` both times. The tree is not
      hypothetical — it is what an interrupted `write_draws` leaves
      and what the commit watcher's two-second settle could commit for
      a ~1 GB file (attack item 25). Closed by a local widening that
      keeps the NAME `collect_total`, so the mutation harness's AST
      totality generator still finds all 31 sites. `IndexError` is
      deliberately NOT added and the reason is in the docstring: the
      freeze swept every runner-leavable tree and found none reachable
      (`read_rows` bounds-checks `item` before any list is indexed by
      it), and a reachable one would be an instrument logic defect,
      which must crash rather than be laundered into a refusal.
      **Three sibling silent-skips closed with it** — a `counts` that
      is not a dict, a `counts` missing a rung, and a `per_rung` that
      is not a dict or is short each switched their own check off
      (`r not in []` is True for every rung). Dial touched: NONE.
- [x] **F-3 — two producers of verdict inputs were neither tag-bound
      nor sha-pinned.** I-2's lesson, two files it missed.
      `INSTRUMENT_BLOBS_2I` binds five files; `FROZEN_SHA256` pinned
      twenty; `power_2i.py` and `run/seal_2i.py` were in neither, yet
      `power_2i.py` produces `power_2i.json` — the preregistered
      POWERED / DECLARED UNDERPOWERED IN ADVANCE declaration, whose
      SHAPE the analyzer validates and whose SIMULATION it cannot —
      and `run/seal_2i.py` produces `predictor_2i.json`, whose
      `sha256` becomes every endpoint and sweep record's
      `predictor_sha` and which is now also F-1's runner-side gate.
      Both pinned (20 → 22); `referents_2i.json` rebuilt (1843 files,
      `8e9a7ab5…`); the two count assertions updated.
      `run/preflight_2i.py` and `verify_referents_2i.py` are
      **deliberately not pinned and the choice is disclosed in place**:
      neither writes anything on the verdict path, and the preflight
      asserts that at run time by snapshotting `results/` before and
      after. Dial touched: NONE.
- [x] **F-4 — the ONE call outside every `collect_total` could raise.**
      `_git_sha()` is evaluated while building the verdict dict, on
      BOTH branches, and `subprocess.run` raises `FileNotFoundError`
      with no git on PATH. On exactly the machine where
      `require_prereg_2i` must refuse (it needs git), the
      INSUFFICIENT_DATA terminal was unreachable — the refusal would
      have come out as a traceback. Total now: an empty string, never
      a raise. Dial touched: NONE.
- [x] **F-5 — `_load_power` accepted a power table over a strict
      SUBSET of R_CAP.** `power_2i._one_test_power` writes `rungs =
      list(R_CAP)`, so a record naming three of eleven rungs is not a
      power statement about the test that will run, and `issubset`
      accepted it. Equality now, with both directions named in the
      message. Dial touched: NONE.

## Attack-list disposition (all 28) — CLOSED 7 / CLEARED 13 / DISCLOSED 8

CLOSED (a change landed): 1, 5, 8, 10, 23, 24, 25.
CLEARED with a demonstration: 2, 3, 4, 7, 9, 11, 15, 16, 17, 18, 19,
21, 28.
DISCLOSED (accepted, wording drafted): 6, 12, 13, 14, 20, 22, 26, 27.

| # | item | disposition |
|---|---|---|
| 1 | 2h F-1 lineage — TOTALITY over every runner-leavable tree | **CLOSED — part of F-2.** 33 shapes swept executably in a fresh process (predictor draws truncated/corrupt/empty/directory/plain-text; predictor records missing/list/torn/wrong-typed fields; seal `counts`/`sampling` of the wrong shape; the R-3 checkpoint-record window; a `_checkpoint.json` list; a step record's `bits` a dict; the twin gone; a whole step directory gone; `gate1.json` a number; `continuations_compared` a string; `HALTED` a directory; `results/` replaced by a file; `rung_set`'s `per_rung`/`R_OLMO` wrong-typed; `power`'s `rungs` a string; an endpoint record's `continuations` an int; stage-1-only; stage-1+2-only; everything gone; control). **Pre-fix 2 RAISED (`EOFError`), post-fix 0 RAISED / 33 terminal**, control still a real world. |
| 2 | 2h F-2 lineage — gate-1 COVERAGE | **CLEARED (already closed in the build) + EXTENDED.** `gate1_failures_7b` requires `continuations_compared[r] == 500` on all 34 and `gate1_rederive_7b` requires it again alongside the byte re-derivation; both mutants killed; R-1 added the one input that separates a bits-derived `cont_diff` from a real one. The same coverage standard is now applied to the PREDICTOR stage (F-1: `per_seed_tallies[0]["n_draws"] == 32,000`). |
| 3 | 2h F-3 lineage — TAG BINDING | **CLEARED, executably.** `require_prereg_2i` compares the working copy of all five `INSTRUMENT_BLOBS_2I` files to the blob the tag carries (`predictor_2g.git_blob_sha256`), at analysis time AND in all three stage runners; a lightweight tag on the wrong commit fails on the blobs, not the name. `require_seal_2i` does the same for the two seal tags over their artifact sets, and NEVER raises (failures are collected). Missing-tag and drifted-blob routes are tested for both seals and killed by four mutants. **Extended by F-3** (the two unbound producers) and by item 24's union. |
| 4 | 3d/3e lineage — the verify criterion on OLMo continuations | **CLEARED.** 101,040 draw-side inputs through 3c's total wrapper, both answer types on the real battery: OLMo-shaped undecoded specials (`<|endoftext|>`, `<|pad|>`, `<|im_start|>`, U+FFFD, NUL, ANSI), CJK/Arabic/Indic punctuation, zero-width and bidi marks, combining marks, emoji with modifiers, fullwidth and mathematical digits, empty, whitespace-only (incl. NBSP/ideographic space), answer-embedding and answer-interleaved shapes, up to ~200-piece concatenations; plus an adversarial exhaustive pass (every piece alone, doubled, prefixed and suffixed to 40 real answers). **0 escapes.** The answer side stays a hard error by design (3c's rule) and is unchanged. |
| 5 | 2f lineage — item alignment of x_A, x_B, the strata and the outcome | **CLOSED (x_B) + CLEARED with a demonstration (x_A).** x_B: F-1 asserts `items_sha256` AND the record's own 500-entry answer column against the pinned item file, for all 34 rungs, in the analyzer AND in the seal runner. Sweep and endpoint records already asserted `items_sha256` (`_record_common_failures`). x_A: 2d's per-rung tier RECORDS are not on 2i's referent manifest and reading them would ADD an unpinned verdict input, so both sides are pinned by CONTENT instead — the 68 draws files by `PYTHIA_PREDICTOR_FILES`, the item files by `ITEMS_SHA_PIN` — and a new test re-derives that 2d's own 68 committed records name exactly those item files (sha + full answer column + n_items + k + seed), at both sizes. The strata come from 2g's sha-pinned sealed predictor and `stats_2g.precompute` raises on any length mismatch with y. |
| 6 | the from_config twin's cross-process determinism | **DISCLOSED.** `torch.manual_seed(seed)` immediately precedes `from_config`, but two-process byte-identity of a 7B random init cannot be checked without model contact, which this session has none of. Design §3.1 makes the twin descriptive only: it is excluded from `outcomes_7b` by construction (`steps` never contains `bi.TWIN`), it is never a predictor (§3.6, no SURFACE terminal), and its counts appear only in the non-gating `twin_counts` secondary. **What a non-zero twin count would mean, stated in advance: not a referent failure but a finding** — a seeded random OLMo-2 7B emitting a verified answer would say the item is reachable from the architecture and the tokenizer alone, and it belongs in the retrospective, not in a refusal. |
| 7 | the degeneracy quantifier | **CLEARED, executably.** `_degenerate_rungs` drops a rung only if EVERY stratum has fewer than two distinct predictor values; unit-tested both ways (one live stratum among degenerate ones keeps the rung; a constant predictor drops it) and killed by a mutant. A rung with two values only inside a stratum too small to matter is handled downstream, not here: `stats_2g.precompute` keeps only strata with at least one informative y-pair, and `perm_test` raises "no informative pair" for a rung with none — which `_run_test` catches, drops that ONE rung, and retries (Ruling 18), so the fine-grained case is a named drop rather than a crash. Both paths tested. |
| 8 | power's alternative SHAPE (3d's sixth lesson) | **CLOSED as a disclosure, DECISION FLAGGED.** `power_2i.SHAPE_NOTE_2I` now rides on the record: the simulation's alternative is ITEM-LEVEL rank concordance inside sealed strata, so neither declaration transfers to a CLASS-level effect — the shape 3d's own frozen power model mis-specified by ~6×. A class-level sensitivity is a NEW STATISTIC, not a pin, so the freeze declined to add it unilaterally; doc slip (j) puts it to Michael. |
| 9 | the THIN rule (`len(R_CAP) < 3`) | **CLEARED + one wording disclosure.** `referents.rung_set` carries R_OLMO/R_CAP/R_EXTRA and `per_rung` in EVERY world including INSUFFICIENT_DATA (`referents` is built before the branch), so R_CAP's size is always printed. `power_2i` prints `thin: len(keep) < 3` per test. Disclosure: `declared_status == "THIN"` is a DIFFERENT thing (Ruling 18's power-side analogue — every rung lost to degeneracy), so a reader must not read `declared_status != "THIN"` as "R_CAP ≥ 3"; both fields are present, doc slip (o). |
| 10 | the rung-set rule reads `stage1_final`, not `main` | **CLOSED.** A mutant re-deriving the rung set from `main_rec`'s counts instead of `stage1_final`'s is now in the harness and killed (the worlds' `main` is all-zero, so R_OLMO collapses and `_check_rung_set_derivation` fires). `endpoint_2i.run` builds `counts` from the `stage1_final` dict alone; `main` never enters the rule. |
| 11 | the reverse-direction descriptives can never reach the verdict | **CLEARED, executably.** `verdict_tree_2i(failures, A, B)` reads only `A["fires"]`/`B["fires"]`; `_reverse_direction` lands in `secondaries["reverse_direction"]`, stamped `known_outcome: True` on both legs (asserted in the world shape test). `_sec`'s own `collect_total` means a broken secondary lands in `secondaries[name]["failed"]` without demoting the verdict — tested. |
| 12 | left padding + OLMo's real pad token under batching | **DISCLOSED.** `evaluate_items` (2g's, frozen) drives 2c's `HFRunner` at batch 16 with left padding; OLMo-2's `<|pad|>` is a real token rather than a borrowed eos, and `check_tokenizer` asserts the id live. Batch-composition effects in fp16 cannot be measured without model contact — but they cancel at gate 1, which compares the sweep's candidate-file loader against the endpoint stage's thin loader under the SAME batching, and a real instability there halts the sweep into INSUFFICIENT_DATA rather than biasing a count. Dial j's preflight is the pre-tag format check. |
| 13 | fp16 on MPS with QK-norm / RMSNorm | **CLEARED for the half that matters, DISCLOSED for the other.** exp3's fp16-MPS full-logits defect was a SAMPLING defect; 2i samples at `a2d.SAMPLING_DTYPE` = float32 with a CPU-float32 softmax (stage 1), so the predictor is not exposed. fp16 is used only for greedy argmax at 7B — 2c/2g/2h's convention across nine byte-identical reproductions on this stack. A gross fp16 failure on OLMo-2 shows up as empty or degenerate continuations in the preflight's 40 printed items, and as a gate-1 halt if it is load-dependent. |
| 14 | disk | **DISCLOSED with the arithmetic** (doc slip (l)). `free_checkpoint` runs in a `finally` on every model-touching branch of the sweep including gate 1 and on exception (tested with the real cache-path helper). The THIN loader's ordinary HF cache is NOT cleared by anything: 29.2 GB per 7B revision × 2 at stage 2, plus 5.9 GB for the 1B at stage 1, on top of the sweep's 29.2 GB per step (613.1 GB streamed over 21 points, freed each time). Peak ≈ 93 GB against 324 GB free. |
| 15 | would the manifest CATCH a stale copy? | **CLEARED, executably (build test, re-run cold).** The duplicate-signature refusal fires on a synthetic inventory carrying one grid step's shards replaced by another's; on the real inventory `final_duplicates == []` and `signature_equals_main == False` across all 965 scanned 7B revisions, so the counter is a structural zero and the signature rule is the load-bearing check — 2h's own disposition, reproduced. |
| 16 | the watcher's coverage | **CLEARED.** `commit_watcher_2i.sh --stage sweep` watches `results/sweep` for `*.json`, `*.jsonl.gz` and a file literally named `HALTED`, so `gate1.json` and the halt marker are both committed; `--stage predictor`/`endpoint` cover their own directories. Push failure is caught and retried on the next unit. |
| 17 | READ SWEEP — zero unpinned verdict inputs | **CLEARED, executably.** See the table below: **1,968 distinct data paths, 2,092 reads, ZERO unpinned.** |
| 18 | determinism across processes | **CLEARED.** Same built world, three separate processes (one with `PYTHONHASHSEED=12345`), verdict JSON **byte-identical** modulo `git_sha` — sha256 `2cf719d23cdae631ecccf1ae4d07e4f80a1650f7572796238e2e0efd2e887e6b` (BOTH, n_perm 300, n_boot 25). Every RNG on the path is explicitly seeded (`stats_2g.PERM_SEED`/`BOOT_SEED`); the composite-strata builders and the degeneracy drop are order-preserving list comprehensions over `rungs`, and `_degenerate_rungs` uses sets only for a cardinality test. |
| 19 | `PAD_TOKEN_ID` one literal for two repos | **CLEARED.** The literal is never assumed — `check_tokenizer` ASSERTS it on whatever tokenizer is handed to it, and every path that loads one calls it with its own repo: `load_tokenizer(repo, commit)` (the sweep's 7B), `load_thin` → `load_tokenizer` (stage 1's 1B, stage 2's 7B), and the preflight's explicit call. So the 7B tokenizer is first checked at stage 2 — before the endpoint seal — and a wrong id is a cheap ledgered stop, not a silent mislabel. (The committed inventory records LFS files only, so tokenizer bytes could not be compared offline; the live assertion is what closes it.) |
| 20 | exp3's `sample_item` has never touched an Olmo2 model | **DISCLOSED, with an option** (doc slip (m)). Dial j's preflight exercises only `HFRunner.generate`. An API/shape mismatch surfaces on item 0 of stage 1's first rung — the first minute of a 7–9 h stage — as a ledgered stop. The freeze did not widen dial j on its own because that is sanctioned pre-tag model contact, i.e. a dial. |
| 21 | `model.safetensors.index.json` downloaded but not sha-verified | **CLEARED** (2h item 15's disposition, re-derived here). `download_entry` fetches every candidate file at `revision=entry["commit"]` — an immutable, content-addressed git commit read from the sha-pinned manifest — so the index cannot vary for a given entry; the six shards ARE sha-checked (`verify_downloads`); `_check_loading_info` requires empty missing/unexpected/mismatched keys, which a mis-mapped index would violate; and gate 1 re-derives the endpoint's tensor digest and 17,000 continuations through the other loader path. |
| 22 | design §3.2's "new namespace `exp2i`" vs the code's `STREAM_NAMESPACE = "exp3"` | **DISCLOSED** — doc slip (a), unchanged. The substreams are separated by the size label `olmo1b` inside the formula; F-1 now asserts the record's `stream_namespace` against exp3's own constant, so the code and the record cannot drift from each other either. |
| 23 | the two reads outside `collect_total`, and `IndexError` | **CLOSED (one) + CLEARED (the other).** `sg.from_json(pred2g["strata"])` is guarded by `if pred2g` and reads a sha-pinned object, so it cannot vary; `_git_sha()` COULD raise and is **F-4**. `IndexError`: swept across all 33 tree shapes and found unreachable — `analyze_2d.read_rows` rejects an out-of-range or duplicate `item` before any list is indexed by it; `outcomes_7b`'s `hits[0]`/`hits[-1]` and `rung_level_7b`'s `clears[0]` are guarded; `stats_2g.d_from_pre`'s fancy indexing of `x` by `y`'s stratum indices is unreachable because every predictor is built as `[0] * N_ITEMS` and `precompute` raises a `ValueError` on a y/strata length mismatch first. Deliberately NOT added to the widened surface, with the reason recorded in the docstring. |
| 24 | `_predictor_seal_paths` (from `bt.RUNGS`) vs `endpoint_2i._seal_blob_paths` (from the seal's `files` dict) | **CLOSED.** The analyzer's set is now the UNION of the two (the seal file is itself blob-bound, so its `files` dict is bound too, and binding more is never weaker); on the real shape they are equal at 1 + 34 + 34 = 69, and a stray file under `results/predictor/` is now bound by both gates. Tested in both directions, including that a malformed seal degrades to the rule's own set rather than a shorter one. Killed by a mutant. |
| 25 | the watcher race on a ~1 GB draws file | **CLOSED (two ways).** The watcher now waits for each unit's size to stop changing before `git add`, and defers to the next 30-second sweep if it is still growing — the fixed two-second settle was the exposure, and the `seen` list is append-only so a partially committed file is never revisited. Independently, a truncated blob now fails CLOSED rather than raising: F-2 makes the analyzer deliver INSUFFICIENT_DATA, `run/seal_2i.py` re-verifies every one of the ≈1.09 M draws before writing the seal, and `blobs_bound` refuses at the endpoint stage if the working tree and the tag disagree. |
| 26 | `main`'s manifest commit is fixed at scan time | **DISCLOSED.** Intended and stated: if HF `main` moves, the descriptive `main` point is the commit scanned on 2026-08-25 (`7df9a825…`), which is what the manifest pins and what `download_entry`/`load_thin` request. `main` never enters the rung-set rule or any outcome (design §3.3). |
| 27 | Ruling 18 — an all-degenerate test is `fires=False` + disclosure | **DISCLOSED, DECISION FLAGGED, and both directions built.** See the section below. |
| 28 | `weight_sha256` is a digest STRING in 2i's records, a dict in 2g's | **CLEARED, re-derived.** `item_record_2i` stamps `weight_sha256 = ckpt["weight_sha256"]`, which `_common_2i.ckpt_of` sets from `info["tensor_digest"]` — a single hex string on BOTH loader paths (`load_checkpoint` and `load_thin` each call `ck.tensor_digest(model)`). Gate 1 reads it as a digest on both sides (`digest_sweep` from the sweep's own `ckpt`, `digest_endpoint` off a `stage1_final` record) and compares like with like. The per-FILE shas live in the separate `_checkpoint.json`, where `load_sweep_7b` checks them against the manifest's `lfs_sha256` name by name. Internally consistent; no dict/string confusion is reachable. |

### The read sweep (item 17), classified

Instrumented `open` / `Path.read_text` / `Path.read_bytes` /
`gzip.open` / `np.load` around `analyze_2i.run()` on a complete
full-shape world, in a fresh process.

| class | distinct paths | how pinned |
|---|---|---|
| world tree (the run's own records) | 886 | re-derived, not trusted: every (step, rung) and (which, rung) record through `step_record_failures_2i` / `endpoint_record_failures_2i` (bits re-verified from the continuations, `items_sha256` vs the pinned item file, commit vs the manifest entry, `predictor_sha` vs the seal, `seal_tag` by kind); every `_checkpoint.json` sha vs the manifest's `lfs_sha256`; `gate1.json` through `gate1_failures_7b` AND `gate1_rederive_7b`; `rung_set_2i.json` re-derived by the rule from the endpoint's own count column; **the 34 predictor records and the seal now through F-1's checks**; the predictor draws re-verified item by item. The predictor and endpoint artifacts are additionally blob-bound to their two seal tags. |
| files on `referents_2i.json` (sha-pinned) | 1,078 | the 34 item files (also `ITEMS_SHA_PIN`-checked before parsing), 2d's 68 committed x_A draws files (also `PYTHIA_PREDICTOR_FILES`), 2g's sealed predictor, 2g's 771-file 2.8b sweep tree and 2h's 806-file 6.9b sweep tree (also re-derived by their own frozen loaders), 2i's manifest and hub inventory, the 22 `FROZEN_SHA256` modules |
| sha-pinned by a code literal, off the manifest | 4 | `checkpoints_2i.json` (`CHECKPOINTS_2I_SHA256`), `referents_2i.json` (`REFERENTS_2I_SHA256`, self-pinned), 2g's `checkpoints_2g.json` (`analyze_2g.CHECKPOINTS_SHA256`), 2h's `checkpoints_2h.json` (`analyze_2h.CHECKPOINTS_2H_SHA256`) |
| **unpinned verdict inputs** | **0** | — |

(1,528 further paths are Python source opened by the import system —
1,493 of them `transformers`' lazy-module machinery — and are not
verdict inputs.)

## Ruling 18, worked both ways (battery item 11)

Built and run, not argued:

* **B undefined** — `W10`, x_B constant on every R_CAP rung: Test A
  fires, Test B is `fires=False` / `named_inside` starting
  "undefined", `dropped_degenerate` is all eleven, the world is
  **SHARED**, and `DISCLOSURE_UNDEFINED_2I["B"]` appears verbatim in
  BOTH `reason` and `licensed_sentence` (and A's does not).
* **A undefined** — a new world in which the production reader for
  x_A (`sampler_counts_pythia`) returns a constant table: Test A is
  undefined, Test B fires, the world is **LINEAGE**, A's disclosure
  is in both fields, and the reason string reads `A: T=undefined`
  (R-2: `None`, never NaN).
* **Both undefined** — already covered through `run()` by the
  no-eligible-rung route: verdict NEITHER, both disclosures in both
  fields.

**Measured, and it narrows the question.** On the real committed x_A
no rung of 2g's eleven is degenerate at either size — live strata per
rung 4/3/3/2/2/4/6/5/6/2/8 at 1b and 3/3/3/2/2/4/6/5/6/2/8 at 410m,
`_degenerate_rungs` returns `[]` both times. The undefined-A branch is
unreachable on this data; **Ruling 18 bites on Test B alone**, where
OLMo-2 1B at 4 T tokens may genuinely sit at ceiling.

**Could SHARED-with-B-undefined mislead? Yes, in one specific way, and
it is worth Michael's minute.** The verdict STRING is the bare word.
§1 defines SHARED as "A fires, B does not", and "B does not fire"
normally means the within-family increment was tested and not found —
which is not what an undefined B means. The disclosure now rides on
`reason` and `licensed_sentence`, so no one who reads a sentence can
miss it; only a reader who reads the word alone can. **What
INSUFFICIENT_DATA would discard instead:** Test A's real, computed
result over R_CAP; the 21-checkpoint sweep and its gate; the rung-level
table; the reverse-direction descriptives; `main`; the twin — i.e. it
would convert a measured cross-family answer into no answer because a
DIFFERENT predictor was at ceiling. The freeze's recommendation is
Ruling 18 as written. The cheap middle option, offered rather than
taken because it changes §1's four-world vocabulary (a dial, not a
pin): name the world `"SHARED (Test B undefined)"` in the verdict
string itself — doc slip (n).

## The named-disconfirmer question (2g's lesson, 2h's precedent)

The projection the supervisor seals before the analyzer runs must
bracket the null **for each test separately**, because 2i has two, and
only one edge of each is the "we were wrong" direction. Written here
in advance:

**Test A (cross-family).**
* *Low edge — the disconfirmer proper:* T_A < .05 with p > .5.
  Pythia-1b's committed counts carry nothing about OLMo-2 7B's
  emission order. The world is LINEAGE or NEITHER, and 2h's finding
  stays lineage-bound.
* *High edge — the other miss, easy to forget to name:* T_A ≥ .30,
  i.e. cross-family transfer at or above 2h's own WITHIN-family T of
  .202. SHARED or BOTH, but a miss all the same: it would say the
  sampled channel reads something almost entirely item-intrinsic and
  that 2h's number was never lineage-specific — and it would raise
  the question whether 2g's committed strata (built on 2c's items) are
  doing the work rather than the predictor. The record should say so
  rather than bank the win.
* *Blind region either way:* between the null's 99th percentile of T
  (`power_2i.json`'s `min_detectable_T`) and T_BAR = .10 — "detected
  but below the effect bar", which is not-fires WITH the note, not
  silence.

**Test B (within-family, beyond cross).**
* *Low edge — the disconfirmer:* T_B < .05 with p > .5. OLMo-2 1B's
  own counts add nothing beyond x_A's zero cut. SHARED (if A fires) or
  NEITHER.
* *High edge:* T_B ≥ .35, a within-family increment larger than 2h's
  whole within-family T after conditioning on the cross predictor.
  LINEAGE or BOTH, but a miss: x_B is expected SPREAD and possibly
  near ceiling at 4 T tokens, so a very large T_B is as likely to mean
  "the 1B already emits what the 7B will" as it is to mean a forecast.
* *Third edge, unique to B and required by Ruling 18:* the projection
  must ALSO name what it expects `dropped_degenerate` to be. "B
  undefined" is a real outcome of this design, not an error, and a
  projection that does not mention it cannot be graded on it.

Both tests are at α .01 on their own; the WORLD is their conjunction
and the union of the four is not α-calibrated
(`CALIBRATION_SENTENCE_2I`, on the verdict in every world).

## Cold battery at the freeze HEAD

- [x] Suite **284 passed**, 0 warnings, 5:35 (`pytest
      experiments/exp2i/tests -q`), run cold AFTER the mutation
      harness restored every source; baseline 235 at the build's
      close. By file: `test_analyze_2i` 81, `test_battery_2i` 35,
      `test_totality_2i` 77 + 6 parametrized expansions,
      `test_stages_2i` 28, `test_sweep_2i` 22, `test_power_2i` 13,
      `test_full_shape_2i` 10.
- [x] Referent battery **11/11** cold on the real tree; the one
      expected refusal is still "0 stage artifact(s) present, 139 still
      missing".
- [x] Full-shape worlds **12**, reaching **all 5 terminals**: W1
      SHARED, W2 LINEAGE, W3 BOTH, W4/W5 NEITHER (inverted named on
      both tests in W5), W6/W7/W8/W9/W9b INSUFFICIENT_DATA by five
      distinct routes, W10 SHARED with Test B undefined, plus the new
      undefined-A LINEAGE world.
- [x] Totality **33 tree shapes, 0 raised** (pre-fix 2 raised,
      `EOFError`).
- [x] Verify-criterion fuzz **101,040 draw-side inputs, 0 escapes**.
- [x] Determinism: **byte-identical verdict across three processes**,
      one with a varied `PYTHONHASHSEED`.
- [x] Read sweep: **1,968 distinct data paths, 2,092 reads, 0
      unpinned verdict inputs**.
- [x] Mutation harness **118 mutants** (89 at the build + 29 new:
      4 for R-1…R-3, 11 for F-1, 6 for F-2 and its siblings, 2 for
      F-4/F-5, 1 for attack item 24, 1 for attack item 10, plus the
      two new `collect_total` sites the AST generator picks up).
      **118/118 killed, survivors: [].** Run detached (nohup +
      disown) — it outlived a mass reaping of this session's tracked
      background tasks midway through, which is exactly why the
      convention exists. Sources restored byte-identical (`git diff`
      empty on all seven targets), no `.mutation_backup` left.
- [x] The real tree still delivers its own refusal: `run()` on the
      unmodified repo returns INSUFFICIENT_DATA naming the missing
      `exp2i-preregistered` tag and every missing stage artifact, with
      no traceback and no `results/verdict.json` written.
- [x] Zero model contact, zero network. `power_2i.json` NOT created.

## Notes for the tagger

1. Cut `exp2i-preregistered` at the commit that carries the FINAL
   instrument. F-3 raises the pin count to 22, so a post-tag edit to
   `power_2i.py` or `run/seal_2i.py` now breaks `check_frozen_2i()`
   everywhere as well; and 2h F-3's own binding means a post-tag edit
   to any of the five `INSTRUMENT_BLOBS_2I` files
   (`battery_2i.py`, `analyze_2i.py`, `run/sample_2i.py`,
   `run/endpoint_2i.py`, `run/sweep_2i.py`) requires a re-tag.
2. `referents_2i.json` is `8e9a7ab50fc1a5a5239d842cc436bcb17f692cd4d83f64ecb1664b8113df8f6c`
   (1,843 files) and is pinned in `analyze_2i.REFERENTS_2I_SHA256`.
   `checkpoints_2i.json` is unchanged (`029b1cca…`).
3. The design doc is NOT edited by this session. Doc slips (a)–(e)
   from the build and (f)–(n) from the freeze are in
   `.superpowers/sdd/2026-08-25-exp2i-build/doc-slips.md` for
   ratification. Three of them are DECISIONS rather than wording:
   (b)/(n) Ruling 18, (j) the class-level power sensitivity, and
   (m) whether dial j's preflight gains one sampled item.
4. F-1's closure means stage 1 can no longer be sealed against the
   wrong checkpoint: `run/seal_2i.py` refuses. If stage 1 is ever
   re-run for any reason, the records must be regenerated with it —
   editing them by hand now fails at the seal and again at the
   verdict.
