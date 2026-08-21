# Exp 2d — Freeze Checklist (session 3 of 3)

Opened cold in a fresh session 2026-08-21. Assignment: find the class
defect. The build session's own record (`PROGRESS.md`) is the
comparison; nothing here is ticked until it is re-run in a fresh
process. Findings F-1 … F-8 are written up in `PROGRESS.md` (freeze
entry); this file carries the ticks and what still needs Michael.

## Rulings from Michael BEFORE the tag — ALL RULED 2026-08-21 ("F-4 symmetric, F-5 yes, slips as recommended — apply and tag"), applied

- [x] **F-4 — which power rule declares.** RULED symmetric (ruling m), applied. The ratified Tobit (F/J)
      re-randomizes rising rungs the pilot already shows positive
      (re-silenced w.p. Φ(τ−d) ≈ .30) while holding flat positives
      positive; the SYMMETRIC rule (rising pilot-positives held
      positive; rising pilot-zeros capped from their own counts) is
      computed and printed as `sensitivity_symmetric_rule`,
      NON-DECLARING. Envelope, all flat at zero: .75/.56/.21/.00 →
      1.00/1.00/1.00/.00 at 0/2/4/6 silent rising rungs. Recommended:
      the symmetric rule declares (one constant,
      `compute_power_2d.DECLARATION_RULE`, plus §7 text). Either way
      main runs regardless (ruling c).
- [x] **F-5 — run the two reversal rungs FIRST** RULED yes (ruling n), applied: `RUN_ORDER`, every tier.
      so gate 1 makes its first production contact ~5 h earlier per
      size (one line in `run_tier`; loop order is not load-bearing;
      analysis order unchanged). Recommended yes.
- [x] **Doc slips (a)–(f)** RULED as recommended (ruling o), applied to the doc: §10 "seed 100" → 1000;
      §4 + §9 the F-3 first-digit-run disclosure (base12_digitsum 196
      / base13 276 of 500 answers not matched whole; both flat, no
      label moves); §7 the F-4 sensitivity + model-free G restatement
      (the statistic's ceiling is 6 silent rising rungs with every
      flat rung at zero; 59 % of 4-subsets PASS); §5.1 the F-6
      resolution sentence (predictor bar +.0006–.0057 vs outcome
      +.008–.048; a deterministic-per-item chance copier clears the
      predictor's bar 26–42 % of the time; α untouched); §10 order if
      F-5 is ruled. Text proposed in the ledger; apply only on his
      word.
- [x] **Finding H (option-copy floor)** — RULED (ii) by Michael
      2026-08-21; applied (ruling k). Freeze: re-derivation attacked —
      six rungs list 500/500 at one count, answer never duplicated
      among options (copy-random rate == 1/n exactly), clock24's 500
      colon questions list nothing, the other 27 list 0/500.
- [x] **Finding L (pilot seed)** — RULED 1000; applied (ruling l).
- [x] Findings A–E, F, G, I, J, K — ratified, applied; re-read
      against the code at the freeze (one stale §10 line, slip (a)).

## Standing adversarial assignments (worked FIRST, cold)

- [x] **The class defect — FOUND: F-1.** The runner's halt leaves an
      incomplete main tier by construction (no normal draws file for
      the halted rung); `run()` loaded the main tier before gate 1
      and RAISED `FileNotFoundError` instead of delivering
      INSUFFICIENT_DATA — §6's first terminal was unreachable from
      the production tree (W4 reached it only on a complete tree the
      runner cannot produce). Demonstrated with the runner's own halt
      function; closed additively (`scan_gate1_halt` before any tier
      loads, `.HALTED` rows re-verified through 3d's comparator,
      `insufficient_data_record`); world W5, three fixtures, two
      mutants killed. Candidates (1)–(8) of the original list all
      attacked and cleared (ledger).
- [x] **Totality of the verify path over BOTH alphabets** — 480,240
      fuzzed + 22,620 exhaustive inputs: `IndexError` the only
      reachable exception (word path only, 29 hits; number path
      raises nothing); wrapper total; 17,000 answers normalize
      non-empty and self-verify; 512,000 committed draws raise
      nothing raw.
- [x] **The floor rule's degrees of freedom** — every rung's
      normalized multiset enumerated: FOUND F-3 (base12_digitsum /
      base13 answers truncated to their first digit run by 2c's
      `number` regex: 196 / 276 of 500; the criterion is not
      exact-match there; both flat, labels unmoved; pinned +
      disclosed in the verdict record; doc text for ratification).
      Majority ties harmless; no empty normalization; option
      listing clean (above).
- [x] **The AUC null's conditioning** — matrix byte-equal to 2c's;
      block order preserved; size-1 families identities on y;
      midranks invariant; 100k draws reach exactly the group's 3,780
      label orbits on the realized y (MC SE ~3e-4 at α, noted);
      bootstrap drops x-independent (2/10,000).
- [x] **Gate 1 = exp3's committed bytes on the PRODUCTION path** —
      sampler and runner re-read cold against exp3's
      `run_sampling_cell`: same prompt rendering, same `sample_item`
      contract (fresh generator per seed, chunk plan (16,)×4, cache
      cropped between chunks), budget 12 == exp3's, same terminal
      ids, same float32 upcast path; pilot seed 1000 / plan (8,)
      cannot touch seed-0 substreams; comparator on committed bytes
      0 diffs / 4 cells, fire at 436/6 only (referent 9).
- [x] **Power model shape** — FOUND F-4 (asymmetric use of the
      pilot; symmetric rule printed as sensitivity, ruling needed);
      model-free G check through the verdict's own code (PASS
      through k = 5, INDETERMINATE 6, FAIL 7; all subsets tabulated);
      `mean_realized_auc` ≈ .853–.855 at AUC_true .85 in the
      0-silent rows (calibration holds); τ continuity finite at
      23/23.
- [x] **The known-outcome caveat** carried in both verdict records
      (full and halt); the licensed sentence is ruling g's; 2c's
      frozen ascent read only by the comparability secondary.

## Cold battery (fresh processes, pycache cleared)

- [x] Fixture suite cold: **102 passed** (87 + 15 freeze fixtures; after rulings m/n).
- [x] Mutation battery cold, both directions, baseline clean — 87
      mutants (80 + 7): **85/87 killed**, survivors [1] and [38] the
      documented equivalents; [73] survived the first pass (fixture
      bypassed run()) and was closed — ledger.
- [x] Referent battery `verify_referents_2d.py` cold: **15/15**.
- [x] Full-shape worlds cold: PASS / FAIL / INDETERMINATE /
      INSUFFICIENT_DATA (W4) + W5 runner-halt + the restriction world.
- [x] `make_referents_2d.py` byte-idempotent (95eded96…);
      `dump_stream_map_2d` byte-idempotent (136 cells).
- [x] `compute_power_2d.py --envelope` reproduces the committed
      ratified fields byte for byte; regenerated with the F-4 columns.
- [x] Driver dry-run: 6 tiers in the frozen order; runner refusals on
      an empty tree (suite: main without pilot/power; argmax without
      main; any gate-1 diff halts all).
- [x] exp3's `preflight_{410m,1b}_float32.json` exist, `all_ok` 4/4
      each (2026-08-16; stack unchanged since); NOT re-run.
- [x] Empty tree: every loader raises FileNotFoundError, never a
      verdict; `scan_gate1_halt` silent.

## Doc corrections (from PROGRESS.md A–E) — applied in the build session

- [x] §11 two answer types; §4 base12_digitsum .038 / base13 .068;
      §4/§5.3 11/23 in 7 families; §5.3 block null; CP two-sided;
      §7 procedure/envelope/zero sets; §5.4 (I); §6 (K); §3 seed
      1000; §5.2 ruling k. Freeze: re-read against the code — one
      stale line (§10, slip (a)).

## After the tag

- [x] Rulings applied; suite 102 / referents 15/15 re-run cold; power/runner
      mutants re-run; tag `exp2d-preregistered` placed.
- [ ] Pilot on Michael's launch word (both sizes, ~1.7 h), watcher
      running, per-rung commits.
- [ ] `compute_power_2d.py` ONCE → `power_2d.json`; declaration
      printed (both rules printed; the ruled one declares); ledgered.
- [ ] Main 410m → 1b (~13 h); gate 1 as the reversal rungs land.
- [ ] Argmax both sizes (~1 h).
- [ ] Projection (`projection_template.md`) sealed in a commit BEFORE
      `analyze_2d.run()`; analyzer ONCE on Michael's go.
