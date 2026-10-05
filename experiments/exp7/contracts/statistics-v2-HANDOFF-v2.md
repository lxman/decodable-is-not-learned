# Statistics v2 — SR1–SR5 delivery

All five requested repairs are implemented in this sibling, ready for scoped
independent re-review. Statistics-v1 is immutable. C-1 remains independently
closed; the corrected reference copy is byte-identical to statistics-v1's.

## Integration changes — action required

`interface.json` is now **exp7.statistics-collection-interface.v3**. Management
owns `StatsCampaignAdapter`; this bundle contains no active collection adapter.

1. **Saved power requires independent sealed geometry.** In the collection
   semantic callback, independently verify the predictor seal and raw payload,
   load/re-score through the statistics loader, then call:

   ```python
   predictors = load_predictors(verified_raw_predictors, verified_battery)
   geometry = predictor_geometry(predictors)
   verify_power_semantics(record, seal_sha256, battery_sha256, geometry=geometry)
   ```

   `verified_battery` here is the `Battery` returned by `load_battery` on the
   verified raw battery payload. Never take geometry from the power record.
   The analyzer independently derives the same geometry after raw loading.
   The record must carry `saved_math_version:2`, `geometry_sha256`, retained
   fit/main outcome-count matrices, every prescribed fit evaluation and both
   full/p-only CP95 intervals. Old saved traces deliberately refuse.

2. **Pre-tag candidate manifests require exactly one `runtime_spec`.** The
   complete schema is in `interface.json`. Explicit runtime roots confer no
   wildcard permission: every runtime/helper file has an independent exact pin;
   frozen/generated code has a fingerprint. Commit/review the host-specific
   runtime authority with the candidate before invocation. The automatically
   enumerated authority in `annex/tests/runtime_fixture.py` is solely fabricated
   test data. Copying that discovery-and-trust pattern into production would
   defeat the independent binding requirement. No tag, seal, projection or
   model-contact grant is introduced into calibration's prerequisites.

3. **Calibration/envelope saved math is version2.** Preserve packed eight-count
   render tables and randomization bounds; probabilities, expectation, raw and
   conditional means, support histograms, full/p-only rates and CP95 intervals
   are all reconstructed. Carry the accepted immutable record into power.

4. **Exactly21 baseline catalog entries per family** is enforced alongside49/35.
   Raw strings, N/A reasons, abstentions and model-None refusal retain their
   original contract. Invalid catalog coverage names `baseline_missing`.

## What the mathematics verifies

- **SR1:** external/local reads and Python execution require exact authority,
  including persistent/transient aliases, precompiled calls and generated exec.
- **SR2:** count-domain/multiset checks and sealed geometry rederive per-family
  Somers numerators/denominators, exact eligible sets, all Ds, every fit path and
  final/validation/main support status. Fixed-margin rearrangement extrema check
  deterministic impossible exceedance counts; constants within blocks remain D=0.
- **SR3:** pinned-source absent cache probes raise ENOENT inside the hook;
  existing/dangling bytecode refuses, including a synthetic creation race.
- **SR4:** every printed derived power/envelope quantity is recomputed from
  retained arithmetic inputs; impossible/structural-zero rows are exact too.
- **SR5:** per-family catalog shape and aggregate applicability both hold.

Saved count matrices and MC exceedance counts still require independently
authenticated provenance. These checks do not replay RNG draws or establish
the common Gaussian/tie bank, independence of validation/main streams, interior
rho latent law, sampled permutation identities or actual exceedance sequence.
They do establish the exact finite-p arithmetic and listed deterministic
constraints. Byte authentication alone is not claimed as a mathematical proof.
Power never computes the actual sealed-predictor selectivity gate.

## Verification and evidence

- Failing-first: `SR-before-corrected-fixture.log` — six methods, five failures
  and one expected Refusal error. All SR1–SR5 reproduced against unmodified v1
  source. The earlier log preserves the initially aliased subset-loss fixture.
- Final: **60 statistics +48 inherited core tests pass**, zero failures/errors/
  skips; `SR-full-statistics-final.log`, `SR-full-reference.log`.
- Full-package cold boundary: `SR-cold-package-receipt.json`; real source
  inventory, no method replacement, pinned import accepted, both unbound external
  helpers refused. The initial probe correctly refused its omitted launcher pin;
  the corrected probe explicitly bound it.
- `V1-V2.diff`, `V1-V2-CHANGES.json`, `ANNEX-MANIFEST.json`, and
  `packaging-receipt.json` bind the complete delivered source and exact changes.
  `EXECUTIONS.md` preserves all invocations and failures.

The n500/default-grid fixtures are fabricated saved arithmetic with zero RNG.
Stochastic inherited tests remain miniature. No production calibration, envelope,
power, analyzer or real-data statistics ran. No model/tokenizer/network contact,
subagents, repository edits or commits occurred. The primary kernels, scientific
bars and existing dials are unchanged; RNG/grid/operational proposals remain
unratified. Pre-tag tokenizer validation remains a future authorized build step.
