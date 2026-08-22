# Exp 2f — Freeze Checklist (session 3 of 3 — worked 2026-08-22 on Michael's word)

The build session's own record (`PROGRESS.md`) is the comparison;
nothing here is ticked until it is re-run in a fresh process.
Assignment: find the class defect. **Zero model contact until the
tag; no label-match rate on committed bytes until the tag.**

## Standing adversarial assignments (work FIRST, cold)

- [x] **The class defect — NOT FOUND.** Candidates (1)–(8) below all attacked and cleared (PROGRESS.md freeze entry); one small finding F-1 (unicode digits scored inconsistently by kind) closed additively; (6) and (8) made executable as pins/prints. Candidates, in order: (1) an unpinned
      verdict input at analysis time — the open() sweep on a world
      (2e's method), classify every read against the 12 frozen
      pins, the 34-file manifest, the item pins and the world's own
      tree; (2) the refusal terminal from every tree the collector
      can leave (partial collection: two of four (size, mode)
      records; an eval npz without its continuity record; a record
      with `pass: true` and bad diffs — the analyzer must ignore the
      runner's claim); (3) the twin: is `load_pythia(untrained=True,
      seed=0)` the SAME network the committed probe-item activations
      came from on this stack? Gate 1 decides it executably after
      the tag — but the freeze must attack the gate's tolerance
      (rtol/atol 1e-2 on fp16) with synthetic deviations: what
      deviation passes that should not? (4) the label parse: 2c's
      normalizer keeps the FIRST digit run of the FIRST line —
      enumerate what the committed continuations actually begin
      with (without scoring them against the label) and confirm the
      parse reads the number the model meant on both rungs; (5) the
      probe's train set: 2,000 / 1,000 probe items vs 500 eval items
      — any leakage between them (shared questions)? enumerate;
      (6) the site family at 410m (25 layers → 18 sites) vs the
      committed m3 records' n_candidates (18 / 14) — pinned
      equality; (7) the m3 gate reproduces ACCURACY and SPLIT but
      not the permutation null: run ONE cell's full null (2,500
      refits, ~50 min) cold and compare `null_mean` / `null_p` to
      the record; (8) the bar asymmetry (§7): print the minimum
      detectable accuracy per cell beside the record so INVERTED
      cannot be read without it.
- [x] Determinism: `compute_cell` on a world twice in separate
      processes, byte-identical (494cdd21…).
- [x] Label totality with a larger alphabet — FOUND F-1, closed (ASCII-only parse); never raised. Was: (unicode digits, full-
      width, superscripts — does `\d` match them? and does 2c's
      regex?) — the draw side must never raise.
- [x] Doc re-read against the code: slips (a)–(g) in `PROGRESS.md`.
- [x] The mutation harness: `.mutation_backup` written BEFORE the
      in-place edit; battery check 11 refuses with one present.

## Cold battery (re-run, fresh process)

- [x] Suite **49** (labels 9, probe 12, analyzer 22, full-shape 6).
- [x] Referent battery `verify_referents_2f.py`: **11/11** cold, check 10
      reporting "no collection yet".
- [x] Mutation battery re-run in full after the freeze edits: **55/60**,
      the five survivors one documented equivalence class; baseline
      clean; no stranded mutant, no backup file.
- [x] `make_referents_2f.py` byte-idempotent (b94dab85…; battery 3).
- [x] Empty tree: the real trees with no collection →
      INSUFFICIENT_DATA delivered (attack 2-i); never an exception.

## Needs Michael before the tag

- [ ] Build findings A–E, freeze finding F-1 and the three additive
      pins, the five equivalent mutants, doc slips (a)–(g)
      (`PROGRESS.md`); then tag `exp2f-preregistered`.

## After the tag

- [ ] `collect_eval_2f.py` for 410m/1b × trained/untrained on
      Michael's word (the only model contact; gate 1 inside it).
- [ ] Projection sealed (disclosure: every generator-side number is
      derivable from committed bytes; the probe reading is not).
- [ ] `analyze_2f.run(write=True)` ONCE → `exp2f-closed`.
