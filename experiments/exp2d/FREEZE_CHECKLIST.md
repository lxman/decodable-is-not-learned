# Exp 2d — Freeze Checklist (session 3 of 3)

Opened cold in a fresh session. Assignment: find the class defect.
The build session's own record (`PROGRESS.md`) is the comparison;
nothing here is ticked until it is re-run in a fresh process.

## Rulings needed from Michael before the tag

- [x] **Finding H (option-copy floor)** — RULED (ii) by Michael
      2026-08-21: max(majority, 1/n_options) on the six option-listing
      rungs, both sides; applied in the build session (doc ruling k;
      `OPTION_LISTING_PIN`). Freeze: attack the re-derivation rule
      (every question, uniform count, colon-introduced list) and
      confirm the 28 non-listing rungs list 0/500.
- [x] **Finding L (pilot seed)** — RULED 1000 by Michael 2026-08-21;
      applied (doc ruling l; stream map regenerated).
- [x] Findings A–E (doc slips) applied to the doc text; F, G, I, J, K
      ratified as recommended — Michael 2026-08-21, applied in the
      build session. Freeze: re-read each doc site against the code.

## Standing adversarial assignments (work these FIRST, cold)

- [ ] **The class defect.** Every predecessor's freeze found one (3a's
      valueless input; 3c's unpinned prompts + unattested gate-1
      shas; 3d's unpinned `answer_type` + self-consistent coverage;
      3e's sign-flipping void rule). Candidates to attack:
      (1) the verify criterion's answer_type: `load_sampling_tier`
      scores with `cap["answer_type"]` from the sha-pinned item file /
      registry (`ANSWER_TYPE_PIN` re-asserted) — can a runner-written
      field reach the criterion anywhere (the record's `answer_type`
      is only COMPARED)? (2) `predictor_from_tier` takes `floors` from
      the caller — does every path (run(), compute_power_2d.main)
      compute them from the pinned battery, and could a floor for the
      wrong rung be paired with a rung's counts? (3) the block layout:
      `FAMILY_SIZES` and the x/y arrays are both built from
      `RUNG_ORDER_2D` — is there any path that builds one from the
      family map's dict order instead? (4) `check_gate1_vs_main` reads
      main rows the loader kept only for reversal rungs — confirm the
      loader keeps them for BOTH sizes and the cross-check cannot be
      skipped by a missing key; (5) the argmax tier's `redecode_diffs`
      is runner-written and never recomputed (descriptive, finding I)
      — confirm no verdict branch reads it; (6) the restriction's
      reduced family vector: `_restricted_layout` recomputes sizes in
      first-appearance order — is a family that loses all rungs
      dropped, and does the block group regenerate for the new vector
      (it does, via `primary_test(...)` without `group`)? (7) the
      power procedure's inputs: `pilot_zero_set` reads `score` and
      `raw_zero` — both from `predictor_from_tier` on the pilot tier
      with `n_draws_per_rung` pinned at 4,000; (8) the gate-1 record's
      `fires_reproduced` is produced by the runner scoring the
      REGENERATED rows — the analyzer checks them against the pin when
      clean; does run() also re-score the committed bytes (referent
      check 9 does; run() relies on `load_gate1`'s equality to the
      pin)?
- [ ] **Totality of the verify path over BOTH answer types' emission
      alphabets** (`number`: regex path, `word`: split path). Fuzz
      ≥ 50,000 draw-side inputs per type incl. punctuation-wrapped
      Unicode whitespace (the em-space slip the build's own referent
      probe made), control chars, NUL, combining marks, empty, 8- and
      12-token garbage, digits with commas/signs; prove `IndexError`
      is the only reachable exception on a `str` and that 3c's wrapper
      catches it; confirm the answer side can never raise on any of
      the 17,000 committed answers (enumerate them all through
      `normalize_answer`).
- [ ] **The floor rule's degrees of freedom**: majority-answer rate
      under 2c's normalization (ties in the majority count; answers
      that normalize to the empty string; the `number` regex taking
      the first integer of a multi-number answer) — enumerate every
      rung's normalized answer multiset and confirm the floor table;
      then Michael's ruling on finding H applied identically to both
      sides if (ii).
- [ ] **The AUC null's conditioning**: the block group exchanges
      whole-family outcome patterns among same-size families with x
      fixed; confirm the sampled matrix is byte-equal to 2c's
      (`test_block_group_is_2cs_routing_and_matrix`), the add-one
      convention, that `rankdata` midranks are permutation-invariant
      under y-permutation (x untouched), and that the 4 size-1
      families (all flat) contribute nothing to the null (their
      swaps are identities on y). Attack the bootstrap's drop rule:
      a resample with no rising rung is dropped — can the drop rate
      itself carry information about the alternative (it depends on
      which families are rising, which is the label, not the
      predictor)?
- [ ] **Gate 1 = exp3's committed bytes on the PRODUCTION path.** The
      runner calls `sample_item(..., seeds=(0,), draws_per_seed=64,
      max_new_tokens=bt.max_new_tokens(rung) [= 12 for both reversal
      rungs], terminal_ids=exp3's rule)`; exp3 called it with
      `seeds=(0,1,2,3)` and `SAMPLING_MAX_NEW_TOKENS = 12`. Same
      per-seed generator reseeded from `stream_seed` under namespace
      `exp3`, same 16-row chunk plan, cache cropped between chunks —
      re-read the sampler cold and confirm nothing carries across
      seeds (precedent: 3c/3d/3e re-derived single seeds out of
      multi-seed runs byte-identically, six times). Confirm the pilot
      (k = 8 → one 8-row chunk) cannot touch main's streams (different
      seed). Confirm `_load_model(size, "trained", "float32")` is
      exp3's exact upcast path.
- [ ] **Power model shape (the sixth lesson)**: the alternative is
      class-level by construction; attack the Tobit choice (a
      two-point or rate-space alternative would change P(PASS) how?),
      the τ continuity correction, the population-AUC calibration
      (does the realized-structure AUC under the model match AUC_true
      when no rung is held/truncated? — `mean_realized_auc` ≈ .856 at
      .85 in the envelope's 0-raw-zero rows), and the envelope's
      conclusion G (the PASS bar dies at ~4 silent rising rungs) —
      is that a property of the model or of the statistic? (Compute
      the deterministic AUC with k silent rising rungs and all flat
      at zero: (13 + (13 − k))/26 … = 1 − k/26; AUC < .75 at k > 6.5;
      with block p and the CI it binds earlier.)
- [ ] **The known-outcome caveat** is carried in the verdict record,
      the licensed sentence is ruling g's, and no branch reads the
      2c frozen ascent except the comparability secondary.

## Cold battery (fresh processes, pycache cleared, every box)

- [ ] Fixture suite cold: 87 expected (plus any freeze additions).
- [ ] Mutation battery cold, both directions, baseline clean — the
      build record's kill count expected (PROGRESS.md).
- [ ] Referent battery `verify_referents_2d.py` cold: 14/14.
- [ ] Full-shape worlds cold: PASS / FAIL / INDETERMINATE /
      INSUFFICIENT_DATA + the restriction world.
- [ ] `make_referents_2d.py` re-run is byte-idempotent (sha
      95eded96… unchanged); `dump_stream_map_2d` byte-idempotent.
- [ ] `compute_power_2d.py --envelope` reproduces
      `power_envelope_2d.json` (seeded).
- [ ] Driver dry-run: 6 tiers in the frozen order; runner refusals on
      an empty tree (main without pilot/power; argmax without main;
      any gate-1 diff halts all).
- [ ] exp3's `run/preflight_paths.py` artifacts for 410m/1b float32
      exist and pass on the current stack (no model contact needed to
      CHECK; re-running them IS model contact — Michael's word).
- [ ] Empty tree: every loader raises FileNotFoundError/ValueError,
      never a verdict.

## Doc corrections to apply at the freeze (from PROGRESS.md A–E)

- [x] §11: "four answer types" → two (number / word). APPLIED.
- [x] §4: base12_digitsum .038, base13 .068. APPLIED.
- [x] §4/§5.3: 11 rising / 23 flat in 7 families (5 mixed); 9 at 12b.
      APPLIED.
- [x] §5.3: null = 2c's family-BLOCK permutation; "within families"
      struck. APPLIED.
- [x] §3/§5.4/§7/j: CP figures to the two-sided convention. APPLIED.
- [x] §7: the built procedure (F), the envelope (G), the zero-set
      definitions (J). APPLIED.
- [x] §5.4 (I) and §6 (K). APPLIED.
- [x] §3: pilot seed 1000 (ruling l) — applied.
- [x] §5.2: floor per ruling k — applied.

## After the tag

- [ ] Pilot on Michael's launch word (both sizes, ~1.7 h), watcher
      running, per-rung commits.
- [ ] `compute_power_2d.py` ONCE → `power_2d.json`; declaration
      printed; ledgered.
- [ ] Main 410m → 1b (~13 h); gate 1 as the reversal rungs land.
- [ ] Argmax both sizes (~1 h).
- [ ] Projection (`projection_template.md`) sealed in a commit BEFORE
      `analyze_2d.run()`; analyzer ONCE on Michael's go.
