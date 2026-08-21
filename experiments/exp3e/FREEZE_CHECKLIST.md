# Exp 3e — Freeze Checklist (session 3 of 3)

Opened cold. Assignment: find the class defect. The build session's
own record is below for comparison; nothing here is ticked until it
is re-run in a fresh process.

## Standing adversarial assignments (work these FIRST, cold)

- [x] **The class defect.** Every predecessor's freeze found one (3a's
      valueless input; 3c's unpinned prompts + unattested gate-1
      shas; 3d's unpinned `answer_type` + self-consistent coverage).
      Candidates to attack: (1) the verdict reads `partition` entries
      for answers/inputs — are they pinned to the item file at every
      path? (2) `load_new_cells_3e` takes `answers`/`labels` from the
      caller — does run() pass the sha-pinned item file's, and can a
      runner-written field reach the verify criterion anywhere? (3)
      the gate-1 record's `fires_reproduced` is produced by the runner
      scoring REGENERATED draws — does the analyzer also confirm the
      addresses against the committed shard bytes (referent check 14
      does; does run())? (4) `committed_base_3e` attributes sources by
      seed range — can a 3d shard masquerade as 3c? (5) the
      `_s2_block` and specificity arm call `sc.emissions` with a
      per-item prompt — is the prompt the sha-pinned render for THAT
      item index (subset index vs battery index)?
- [x] **Totality fuzz of the target-swapped scorer** over the
      emission alphabet: the draw side must never raise for any str
      (3c stop #1); the target side is always a committed string. Fuzz
      ≥ 50,000 draw-side inputs incl. punctuation-wrapped non-space
      whitespace, control chars, NUL, combining marks, empty, 12-token
      garbage; prove `IndexError` is the only reachable exception on a
      `str` and that it is caught.
- [x] **The partition's degrees of freedom:** N(x) (all vs adjacent
      transpositions; rotations by one only), M(x)'s overlap clause
      (≥ vs >), first-character matching, the sit-out rule; the
      variants are printed in `partition_3e.json` — confirm the
      frozen choice is the doc's §5.1 and that no downstream branch
      reads a variant.
- [x] **The nulls' conditioning:** the count-weighted DP conditions
      on every item's count; the designation DP on every item's count
      vector; the hypergeometric on n. Attack each for a leak of the
      alternative into the null (e.g., void handling changing n).
- [x] **Gate 1's path = the production path?** `rederive_cell_3e`
      calls `sample_item(..., seeds=(seed,))`; the tranche calls
      `sample_item(..., seeds=block)`. Same function, per-seed
      generator reseeded from `stream_seed`, cache cropped between
      chunks — re-read the sampler cold and confirm nothing carries
      across seeds. Precedent: 3c re-derived exp3's seed 0 alone from
      a 4-seed run, 3d re-derived 3c's seed 8 alone from a 12-seed
      run, both byte-identical.
- [x] **Power model shape (the sixth lesson):** the alternative is
      class-level by construction; attack the gamma-shape rule
      (population vs sample variance moves .3082 → .2921), the
      Poisson thinning, and whether any per-item concentration could
      re-enter through the dispersion.

## Cold battery (fresh processes, pycache cleared, every box)

- [x] Fixture suite cold: 118 expected (plus any freeze additions).
- [x] Mutation battery cold, both directions, baseline clean —
      60/60 expected killed (build record below). **Freeze: 65/65
      killed (60 + 5 freeze mutants), baseline clean, detached run.**
- [x] Full-shape worlds: 9/9 terminals + 3/3 annotations.
- [x] Referent battery `verify_referents_3e.py`: 15/15 on the real
      trees.
- [x] `partition_3e.dump_partition` re-run → `partition_3e.json`
      byte-identical (sha `4a0e346f…1529` recorded in
      `analyze_3e.PARTITION_FILE_SHA256`).
- [x] `compute_power_3e.py` re-run → `power_3e.json` byte-identical.
- [x] `dump_stream_map_3e()` re-run → `stream_map_3e.json`
      byte-identical; `check_stream_map_3e()` + 3d's + 3c's checks
      clean.
- [x] `scorer_gates_3e.py` re-run → `results/scorer_gates.json`
      byte-identical, PASS/PASS.
- [x] Determinism fixture (exp3's `run/determinism_fixture.py`) twice
      in separate processes, byte-identical to exp3's committed
      reference — the sampler is byte-pinned, so the standing
      reference applies verbatim.
- [x] Campaign driver dry-run: 4 tiers in the frozen §10 order;
      runner refusal preconditions verified on an empty tree and on a
      failed scorer-gate record.
- [x] **Gate-1 single-cell rehearsal — the ONLY sanctioned model
      contact before the tag, on Michael's word:**
      `rederive_cell_3e("410m")` end to end against 3d's committed
      seed-24 shard on the 45 items (2,880 draws; the stream carries
      the 410m 'ecde' fire at item 123 draw 62). Expect IDENTICAL /
      n_diffs 0 / `fires_reproduced` == [(123, 24, 62)]; the record
      is kept as the campaign's own comparison made early.
      **RUN 2026-08-21 on Michael's word ("go"): 2,880/2,880 draws
      IDENTICAL, n_diffs 0, fires_reproduced [(123, 24, 62)], items /
      subset / item-file shas on the pins, attested shard sha == disk
      == §4 literal, torch 2.12.1 / transformers 5.13.0 — record at
      `results/gate1/410m_trained/reverse_string.json`, kept as the
      campaign's 410m gate-1 cell (skip-if-exists).**

## Ratification with Michael (before the tag)

- [x] Doc slips (a)–(f) in `PROGRESS.md` (stream-map assertion
      reading; annotation attached to every world; §7 back-of-envelope
      superseded; **H_half underpowered — does §7's clause fire?**;
      scorer gates before gate 1; leak-void on competitors).
- [x] Build dials: gamma shape rule + .3082; power seed/sims;
      m_s,min best-case rule; 16-seed blocks; `fires_reproduced`
      semantics; subset-carrying sampling records; the two added
      frozen pins.
- [x] Any freeze finding, closed or open. **RATIFIED — Michael,
      2026-08-21 (slips a–f, build dials, F-1/F-2/F-3; F-2 → DECLARED
      UNDERPOWERED IN ADVANCE; H_half subsumed).**
- [x] Then: tag `exp3e-preregistered`; campaign launch is a separate
      go. **TAGGED 2026-08-21 after the rehearsal, on Michael's word.**

## Build-session cold-state record (for comparison at freeze)

- Fixture suite: 118 passed (116 at first full green + 2 kill fixtures added after the first mutation run).
- Full-shape: 9 worlds, every terminal and annotation reached.
- Scorer gates on committed bytes: (a) 19/19 addresses, (b)
  12787/16000 and 13460/16000 — PASS/PASS.
- Power: m_min 8, m_s,min 3; P(SHORTCUT | H_shortcut, gamma, 1b)
  .7636; H_half .3069; MDR .04 / .29; shape .3082.
- Referent battery: 15/15 on the real trees.
- Mutation battery: 60/60 killed (first run 56/60; the 4 survivors
  were fixture gaps, closed — PROGRESS.md).

## Freeze record (2026-08-21, session 3 — fresh processes, pycache cleared)

Standing assignments — all worked cold; three findings, each closed
executably the same day (PROGRESS.md freeze entry has the detail):

- **F-1 (the arm's void semantics, statistical).** Slip (f)'s literal
  reading of §4 zeroed a void competitor's count inside the
  designation-exchangeability vector, which LOWERS the null p (the
  reverse's share rises against a slot that cannot score) — anti-
  conservative toward DIRECTED. Closed: any item with a void target
  (reverse or competitor) sits out the designation test, disclosed
  under `arm_void_excluded` with its raw vector; §4's "counted by
  nothing" still holds for the counts. Executable three-way contrast
  in `test_freeze_3e.py`: competitor live p = 1/4, item excluded 1/8,
  competitor zeroed 1/24. **Inert on the real experiment:** the void
  census over every target of the 45 (answers, M(x), all 7 neighbours
  each), the 149 S2 targets and all 500 answers is ZERO. Ratification
  item (a semantics correction to the doc's "applied identically").
- **F-2 (power shape rule).** Population-variance gamma shape .3082
  puts the named-alternative power at .7636; the sample-variance
  estimator (.2921) puts it at **.7447 < .75**. The frozen rule is
  unchanged; the sensitivity is now printed in `power_3e.json`
  (`dispersion_shape_sensitivity`, a concession line, and
  `declared_underpowered_under_sample_variance_shape: true`). Whether
  to DECLARE UNDERPOWERED in advance on this basis is Michael's
  ruling (recommendation: yes — 1c precedent, costs nothing, the
  tranche runs regardless).
- **F-3 (additive pins).** The gate-1 record's `items_sha256` was
  attested but never compared to the §4 pin by the analyzer, and
  nothing tied the gate-1 weights to the tranche's; closed by
  `check_gate1_vs_tranche_3e` (run() + the full-shape path), shard
  `model_sha` presence + coherence in `load_new_cells_3e`.

Cleared under attack (reasons in PROGRESS.md): class-defect
candidates (1)–(5); scorer totality (90,000 draw-side inputs, 60k
adversarial + 30k real emitted — `IndexError` the ONLY exception
`normalize_answer` reaches, 59 times, wrapper 0, `score_first_char`
0); the partition's degrees of freedom (strict input == answer[::-1]
for all 500; ≥ in M(x) is the doc's; variants read by one printed
count only; no normalization collisions); the nulls' conditioning
(void cannot move n on this battery; count-weighted and hypergeometric
condition on non-void counts); the sampler re-read (per-seed generator
from `stream_seed`, cropped prompt cache the only cross-seed state,
cropped-vs-fresh equality proved by 3d's re-derivation of 3c's seed 8
from a 12-seed call); Poisson thinning vs exact binomial (.75343 vs
.75340).

Cold battery: suite **125** (118 + 7 freeze fixtures); full-shape 9/9
+ 3/3 inside it; referents 15/15; partition re-dump byte-identical
(sha = pin); stream map byte-identical + 3e/3d/3c checks clean; scorer
gates byte-identical PASS/PASS; power re-run byte-identical BEFORE F-2,
then regenerated with the sensitivity block (load-bearing entries
unchanged, reproducibility fixture green); determinism fixture twice ==
exp3's committed reference (torch 2.12.1 / transformers 5.13.0); driver
dry-run 4 tiers in §10 order; runner refusals on an empty tree and a
failed scorer record; a FORGED-flag scorer record passes the runner's
precondition and is REFUSED by the analyzer (the layers as designed).
Mutation battery: **65/65 killed** (60 build + 5 freeze mutants),
baseline clean, run detached and alone after the closures.
