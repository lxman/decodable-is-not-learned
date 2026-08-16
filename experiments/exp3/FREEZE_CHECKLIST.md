# Exp 3 freeze checklist (build sessions wrote it; the freeze session
# of 2026-08-16 executed it COLD and ruled on it)

**Status: NOT FROZEN. Do not tag until every box is checked in the
freeze session itself. One box remains open by design: the freeze
amendment awaits MICHAEL'S ratification — the tag is his go.**

The freeze session opens adversarially: cold re-read of
`experiment-3-design.md` and this tree, assignment = find the class
defect (3a's was a verdict input with no value on its own battery;
2c's was a floor that credits format; the build session's was an
arithmetic path that was wrong at the kernel level — assume this
tree still contains one and hunt for it).

**The assignment was met (ledger 2026-08-16): the class defect was in
§5's original w̃ mass statistic — 2c's class, a criterion crediting
lexical/format letter statistics. Demonstrated executably (a
position-blind set-level primer scored K=500/500, p ≈ 3e-151), both
degenerate shapes shown live in 3b's committed continuations, amended
to the within-item interior-competitor form with the θ = .5 null
exact by position exchangeability. A second, smaller crack (gate-3
scope behind a passing gate 1) was ruled and closed the same session.**

## Rulings required (build-session readings, PROGRESS.md 2026-08-15)

- [ ] **THE FREEZE AMENDMENT (ledger 2026-08-16) — MICHAEL'S RULING,
      blocks the tag:** §5's primary mass statistic amended from the
      w̃ cross-item form (found to credit set-level lexical priming —
      the class defect; θ ≈ 1 false fire demonstrated, both degenerate
      shapes visibly live in 3b's committed continuations) to the
      within-item interior-competitor form (θ = .5 exact for the whole
      position-symmetric mechanism class; echo read on neither side).
      power.json untouched (sign_test_significance unchanged). Ratify
      the amendment → tag; or reject → revert to w̃ + disclose-only
      (recorded in the ledger) before any tag.
- [x] Bracket ends: lower end adjudicates, upper end disclosed,
      disagreement its own finding — **RATIFIED.** Unattributed
      whitespace-path mass can only suppress a fire, never manufacture
      one; unchanged in force under the amended statistic (the upper
      end credits the residual to the answer's first character,
      interior competitors at computed masses). World
      `bracket_disagreement` pins both ends.
- [x] Gate-3 trigger scope: computed for 16 — **WIDENED, not
      ratified as drafted**: the ID trigger fires on the 4 adjudicated
      cells AND the 2 ctrl_copy trained cells (`GATE3_FATAL_CELLS`).
      Reading 2's "a control incoherence in practice also takes gate 1
      down" has a demonstrated crack — both gate-1 arms pass over a
      disagreeing control (rank-fired sign test + healthy full-string
      CP over a low mass bracket); world
      `id_gate3_ctrl_incoherent_behind_passing_gate1` pins it. Twins
      and clock24 stay disclosed-only, reasons in the ledger ruling.
- [x] All-ties cell: significant=False, p=1.0, n_eff=0 disclosed —
      **RATIFIED**, with the amendment note that ties now carry
      mechanism information (a fully-primed, position-blind model
      cancels to exact ties; n_ties is disclosed per cell).
- [x] Stream map refinement: per-(cell, seed, item) substreams —
      **RATIFIED.** Restart-order and batch-composition independence;
      map committed (`stream_map.json`), formula pinned in fixtures.
- [x] Terminal (eos/pad) mass bucket — neither letter mass nor
      residual; sampler stops at EOS — **RATIFIED.** Generate's
      semantics (3b's committed bytes); routing eos mass through
      depth 2 would credit letter paths sampling cannot realize and
      manufacture gate-3 incoherence from bookkeeping.
- [x] **Dtype policy** — **RATIFIED.** fp32 mass+sampling is an exact
      upcast of the same fp16 checkpoint 3b probed (same-weights claim
      survives, strictly more accurate arithmetic); 12b fp16 depth-1
      keeps to the verified-sane batch-1 keep1 class with the whole ws
      mass honestly widening the residual bracket; re-decode stays
      3b's exact fp16 generate path because gate 2 must reproduce 3b's
      bytes. The corruption record (rows 1–15 garbage in fp16-MPS
      batched cached steps; quantized overflow ties) and the
      per-(size, dtype) preflight gate stand as built.
- [x] Letter-support rule (reading 5, RE-KEYED by the freeze
      amendment): computable iff every character the statistic reads —
      each item's answer[0] and interior answer[1:-1] — lies in the
      stored a–z block; clock24's digit cells computable=False and
      never significant (gate-5 mass arm inert there, full-string arm
      live); items with answer length < 3 are structural ties (none
      exist: committed lengths 7 / 4–6 / 4–6, verified 100% lowercase
      alpha); an adjudicated cell without computable support is a HARD
      ERROR — **RATIFIED as re-keyed; the stored vector stays a–z**
      (widening to digits buys nothing: no adjudicated or gate-1 rung
      reads a digit).
- [x] Gate-1 CP form (reading 6): two-sided .95 CP lower end on the
      recomputed pooled full-string count — **RATIFIED** (program
      reporting convention since 1c; fixture-pinned).
- [x] Cross-battery pins (reading 7): items_sha256 + labels/answers +
      n equal to the 3b referent's, per rung, all three batteries —
      **RATIFIED** (`_shape_check_3`; mutants on both the sha and
      array arms).
- [x] Eval-size scope (reading 8): no significance test on eval-size
      mass cells; scale trend descriptive only — **RATIFIED** (world
      `eval_mass_is_descriptive`; mutants in both directions).
- [x] Coherence bracket (reading 9): cell bracket = mean over items;
      recomputed first-char count against it at 1 − .01/16 —
      **RATIFIED** (binomial CP on the pooled count is conservative
      for heterogeneous per-item rates — Poisson-binomial variance is
      maximal at equal rates — so the gate under-fires, the safe
      direction for an ID trigger; world `coherence_level_margin`
      pins the level).
- [x] SIGN_TIE_EPS = 1e-12 — **RATIFIED** (above f64 dust on 26-term
      sums, below any fp32-expressible mass difference; the amended
      statistic's interior means change neither bound). Two documented
      equivalence notes: the explicit all-ties branch is unobservable
      because binom.sf(-1, 0, .5) = 1.0 (belt-and-braces); and the
      self-inclusion competitor mutant is sign-preserving (scales s_i
      by n/(n+1)) everywhere except the epsilon boundary, which
      `test_epsilon_boundary_sign_is_counted` pins.

## Cold re-runs (all must pass, from a fresh process, before the tag)

- [x] Full fixture suite green (`PYTHONDONTWRITEBYTECODE=1 python -m
      pytest experiments/exp3/tests/`), pycache cleared first —
      **139 passed** cold, 2026-08-16 (131 at build close; +8 amendment
      kill/boundary fixtures, −1 retired w̃ guard, +1 gate-3 world).
- [x] Mutation check both directions (`tests/mutation_check.py` —
      54/54 at build; retargeted at the freeze amendment and the
      gate-3 ruling: three w̃ mutants retired, six added, 56 total;
      single run on a quiescent tree, snapshot/restore verified) —
      **56/56 KILLED, baseline clean, git tree clean**, 2026-08-16.
      The first official run scored 55/56: the gate-3 widening had
      made `id_gate1_mass` non-isolating for the gate-1 any() mutant
      (it died at widened gate 3 instead). Repaired with the
      `id_gate1_mass_one_size_behind_coherent_instruments` world
      (12/8 split, p=.2517, CP arm passing, instruments coherent) —
      the mutation discipline catching a fixture blind spot the same
      day the gate moved, exactly its job.
- [x] Full-shape batteries reach EVERY terminal: four worlds, PARTIAL,
      every INSUFFICIENT_DATA route, one-rung and both-rung
      contamination, coherence fire, residual-bracket disagreement,
      coherence level margin (`python -m
      experiments.exp3.tests.full_shape`) — **16/16 ok, ALL TERMINAL
      BRANCHES REACHED** cold, 2026-08-16 (15 at build + the gate-3
      ruling's control-incoherence world).
- [x] `verify_referents.py --construct`: 14/14, twin hashes equal to
      3b's records — **14/14, 0 failed**, cold 2026-08-16; twins
      construct deterministically twice per size, hashes `335d46b7…`
      (410m) and `fa3fe1d2…` (1b) equal to 3b's records; rewritten
      `referent_check.json` byte-identical to the committed one.
- [x] Determinism fixture re-run cold: byte-identical to the committed
      `determinism_reference.json` (fp32; stack versions inside the
      compared bytes) — **BYTE-IDENTICAL**, cold 2026-08-16
      (torch 2.12.1 / transformers 5.13.0 / mps unchanged since
      build).
- [x] Preflight `run/preflight_paths.py` re-run for 410m/float32 (and
      any size whose model is already local) — **ALL FIVE LOCAL SIZES
      PASS**, cold 2026-08-16: 410m/f32 and 1b/f32 (410m artifact
      differs from the committed one only by the new `keep1_only:
      false` disclosure field), 2.8b/f32 and 6.9b/f32 full checks
      (worst batched-row diff 8.64e-06 / 6.88e-06 against the 1e-4
      tolerance), 12b/f16 `--keep1-only` per freeze finding #3 (keep1
      diffs exactly 0.0; the report discloses the mode). Every
      campaign tier's arithmetic is verified on this stack before the
      tag; the campaign driver re-gates each (size, dtype) at launch
      regardless.
- [x] Power tables recomputed from the frozen code, equal to the
      committed `power.json` — **BYTE-IDENTICAL** cold, 2026-08-16
      (282 critical; .9539 at θ=.60; .2799 at .55; blind edge .563;
      2.340e-05 detectable rate — `sign_test_significance` untouched
      by the amendment, exactly as the ledger claimed).
- [x] `analyze_3.run()` on an empty results tree hard-errors (no
      silent verdict on a missing battery) — **FileNotFoundError**
      cold, 2026-08-16, and pinned in pytest
      (`test_run_on_an_empty_results_tree_hard_errors`).

## At the tag

- [ ] Tag `exp3-preregistered` on the ruling-complete, cold-green
      commit; push tag.
- [ ] Campaign preflight ladder + per-cell push authorization
      reconfirmed with Michael (§10.3).
