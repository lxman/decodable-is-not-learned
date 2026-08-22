# Exp 2e — Freeze Checklist (build + freeze in one session, 2026-08-22)

Worked adversarially after the build in the same session (§11's
compressed protocol, on Michael's word "build and freeze"). Findings
and slips are written up in `PROGRESS.md`; this file carries the
ticks and what still needs Michael. Nothing here touched a real
tally with a functional: the referent battery and every fixture on
the real tree stop at 2d's known numbers.

## Needs Michael BEFORE the tag — RULED 2026-08-22 ("F-1 ratified, slips as recommended — apply and tag")

- [x] **F-1 — the §6 terminal's boundary** (tree referents → the
      terminal, delivered; instrument pins → a hard error). RATIFIED;
      slip (b) applied to §6.
- [x] **Doc slips (a)–(g)** RATIFIED as recommended, applied to the
      doc (§2, §4, §5.1 ×2, §5.4, §5.5, §6, §10 c). Found while
      applying (g): `KNOWN_INPUTS_CAVEAT_2E` was a paraphrase of §2,
      not the paragraph — ruling g says verbatim; replaced with the
      doc paragraph extracted from the file, with a fixture that
      compares the two. Cold battery re-run in fresh processes after
      the edits; tag `exp2e-preregistered` placed.

## Standing adversarial assignments (worked)

- [x] **The class defect — NOT FOUND.** Candidates attacked and
      cleared: (1) an unpinned verdict input at analysis time — the
      open() sweep: 577 reads, 549 pinned, 28 unpinned all from 2c's
      screen-aware battery listing, consulted only by the rung-order
      cross-check (refuse-only); (2) the refusal terminal unreachable
      from a real tree (lesson 8) — five drift worlds each deliver
      INSUFFICIENT_DATA with the reason; (3) the inherited statistic
      not reproduced — exact on the real tree; (4) a hidden dial in
      the functional — none survives the literals; (5) ε mis-scaled
      between tiers — derived from n_draws, fixture + mutant; (6) the
      paired bootstrap disagreeing with 2d's marginal — exact;
      (7) the primary reading a functional other than F1 — W9 and the
      disk-free fixture separate F1 from F2/B0, mutants killed.
- [x] Determinism: two processes, byte-identical records.
- [x] Doc re-read against the code: seven slips, none a dial.

## Cold battery

- [x] Suite: 21 functional + 24 analyzer + 6 full-shape = 51 (41 at
      the first mutation pass; ten fixtures added for its survivors).
- [x] Referent battery `verify_referents_2e.py` cold: **12/12** on the
      real tree (273 files; main re-tally == §4 table 68/68; 2d's
      primary reproduced exactly).
- [x] Full-shape worlds: W1 PASS / W2 FAIL / W3 INDETERMINATE /
      W4–W8 INSUFFICIENT_DATA (five routes) / W9 PASS floor-relative.
- [x] `make_referents_2e.py` byte-idempotent (51a3cc2a…).
- [x] Mutation battery `tests/mutation_check.py` (55 mutants, both
      directions): first pass 41/55, all fourteen survivors fixture
      gaps (ledger), closed; second pass 14/14 → **55/55 killed**.

## After the tag

- [ ] Projection sealed before the analyzer, with the §2 disclosure
      (the projection's author has seen the tallies).
- [ ] `analyze_2e.run(write=True)` ONCE on Michael's go →
      `results/verdict.json`; tag `exp2e-closed`.
