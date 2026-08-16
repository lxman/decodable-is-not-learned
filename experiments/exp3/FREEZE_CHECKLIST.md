# Exp 3 freeze checklist — SKELETON (build sessions write it; the
# freeze session executes it COLD and rules on it)

**Status: NOT FROZEN. Do not tag until every box is checked in the
freeze session itself.**

The freeze session opens adversarially: cold re-read of
`experiment-3-design.md` and this tree, assignment = find the class
defect (3a's was a verdict input with no value on its own battery;
2c's was a floor that credits format; the build session's was an
arithmetic path that was wrong at the kernel level — assume this
tree still contains one and hunt for it).

## Rulings required (build-session readings, PROGRESS.md 2026-08-15)

- [ ] Bracket ends: lower end adjudicates, upper end disclosed,
      disagreement its own finding — ratify or amend §5 wording.
- [ ] Gate-3 trigger scope: computed for 16, fires on the 4
      adjudicated — ratify or widen.
- [ ] All-ties cell: significant=False, p=1.0, n_eff=0 disclosed.
- [ ] Stream map refinement: per-(cell, seed, item) substreams.
- [ ] Terminal (eos/pad) mass bucket — neither letter mass nor
      residual; sampler stops at EOS.
- [ ] **Dtype policy**: mass+sampling fp32 (exact upcast); 12b mass
      fp16 depth-1 with ws mass in the residual bracket; re-decode
      fp16 generate. The fp16 batched-step corruption record and the
      preflight gate design.
- [ ] Letter-support rule (reading 5): sign test over the empirical
      a–z support; clock24's digit cells computable=False and never
      significant (gate-5 mass arm inert there, full-string arm
      live); an adjudicated cell without computable support is a
      HARD ERROR — ratify, or widen the stored vector to digits.
- [ ] Gate-1 CP form (reading 6): two-sided .95 CP lower end on the
      recomputed pooled full-string count.
- [ ] Cross-battery pins (reading 7): items_sha256 + labels/answers +
      n equal to the 3b referent's, per rung, all three batteries.
- [ ] Eval-size scope (reading 8): no significance test on eval-size
      mass cells; scale trend descriptive only.
- [ ] Coherence bracket (reading 9): cell bracket = mean over items;
      recomputed first-char count against it at 1 − .01/16.
- [ ] SIGN_TIE_EPS = 1e-12 (sign-vs-tie resolution above f64 dust,
      below fp32 resolution), and the documented EQUIVALENT mutant:
      the explicit all-ties branch is unobservable because
      binom.sf(-1, 0, .5) = 1.0 — belt-and-braces, not behaviour.

## Cold re-runs (all must pass, from a fresh process, before the tag)

- [ ] Full fixture suite green (`PYTHONDONTWRITEBYTECODE=1 python -m
      pytest experiments/exp3/tests/`), pycache cleared first.
- [ ] Mutation check both directions (`tests/mutation_check.py`,
      written in build session 2b, 54/54 killed at build; run it
      FOREGROUND on a quiescent tree — it snapshots and restores
      analyze_3.py in place).
- [ ] Full-shape batteries reach EVERY terminal: four worlds, PARTIAL,
      every INSUFFICIENT_DATA route, one-rung and both-rung
      contamination, coherence fire, residual-bracket disagreement,
      coherence level margin (`python -m
      experiments.exp3.tests.full_shape`).
- [ ] `verify_referents.py --construct`: 14/14, twin hashes equal to
      3b's records.
- [ ] Determinism fixture re-run cold: byte-identical to the committed
      `determinism_reference.json` (fp32; stack versions inside the
      compared bytes).
- [ ] Preflight `run/preflight_paths.py` re-run for 410m/float32 (and
      any size whose model is already local) — all rows match.
- [ ] Power tables recomputed from the frozen code, equal to the
      committed `power.json`.
- [ ] `analyze_3.run()` on an empty results tree hard-errors (no
      silent verdict on a missing battery).

## At the tag

- [ ] Tag `exp3-preregistered` on the ruling-complete, cold-green
      commit; push tag.
- [ ] Campaign preflight ladder + per-cell push authorization
      reconfirmed with Michael (§10.3).
