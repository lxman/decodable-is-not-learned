# Exp 2f — Progress Ledger

Chronological. The design doc (`experiment-2f-design.md`) stays as
ruled (§10 a–f, 2026-08-22); everything the build discovered that
touches doc TEXT is ledgered here for freeze ratification, never
silently absorbed. **Zero model contact in the build.** The only
model contact the design allows — eval-item activations with the
continuity gate (`collect_eval_2f.py`) — runs after the tag on
Michael's word. **No label-match rate has been computed on the
committed draws or continuations** (design §2: derivable, not
computed).

---

## 2026-08-22 — BUILD (session 2 of 3)

Instrument at `experiments/exp2f/`:

- `labels_2f.py` — the §3 label functions: sub3_mid's middle digit
  (2b/2c's probe label verbatim), arith_next's last digit (ruling a,
  primary) and (a+4d) mod 7 = answer mod 7 (2c's label, printed);
  emissions parsed through 2c's `number` normalization (first line,
  first digit run, commas out), MISS for no digit run / a negative / a
  run outside the domain (sub3_mid: 1–3 digits); total on every
  string (20,000 fuzzed); exact-match through 2c's verify; floors
  c = max(majority share, 1/K) on the 500 eval answers — **sub3_mid
  /mid_digit .132, arith_next/last_digit .120, arith_next/mod7 .156**
  (majority shares; none below 1/K); the two KNOWN-ANSWER GATES
  against 2c's committed `probe_label` fields: sub3_mid == middle
  digit 500/500, arith_next == answer mod 7 500/500.
- `probe_2f.py` — 2c's site family (every third layer + final × 2
  positions, `screen.LAYER_STRIDE`, checked equal to `_thin_layers`:
  18 at 410m, 14 at 1b); 2b's probe (constants imported); the
  eval-item reading per site; detection = 2d's binomial bar against
  c, Bonferroni across the family (2b's), 2c's tie rule for the best
  site; the twin void rule (ruling c) and 1b's trained-exceeds-twin
  correction; the CV secondary (ruling b, printed); `starved_
  accuracies` — 2b's `starving_split` under the committed parameters
  (sub3_mid `SplitParams(n_holdout=20)`, arith_next
  `SplitParams(holdout_frac=0.35)`), the machinery gate.
- `analyze_2f.py` — pins: 12 frozen-import shas (2b's
  probe/splits/models/generators/base, exp1's stats, 2c's
  harness/screen/gen_items, 2d's analyze/stats/battery), the 8
  probe-item activation shas (== the digest lists), the 4 m3 records
  by literal, the 12 exact-match counts (main 35|34|831|531, pilot
  6|3|109|67, argmax 0|0|13|19), the 34-file manifest; loaders: 2d's
  tiers and argmax records through 2d's loaders (provenance + stored
  tallies), the probe-item npz with y == the committed probe_labels,
  the eval-item npz with its provenance meta (model sha, twin seed 0,
  items sha, n_layers == the probe file's, y == the answers), the
  continuity record RE-DERIVED from its diffs (tolerance rtol/atol
  1e-2 on fp16, CONTINUITY_N = 8 per rung); `compute_cell` (the three
  rungs, D, monotone, void); the tree; `run()` with every refusal
  collected (lesson 8); secondaries: arith_next under mod 7 through
  the whole tree, α = .05, the majority share alone as c, the pilot
  tier inside every cell, the CV probe, 2c's committed starved
  records.
- `collect_eval_2f.py` — the post-tag collector: 2c's renderer and
  position rule (the three renderers are byte-identical, fixture),
  trained model and twin via 2b's `load_pythia(seed=0)`, gate 1 =
  the first 8 probe items per rung re-collected and compared to the
  committed rows (max abs / rel deviation recorded; the analyzer
  judges).
- `make_referents_2f.py` / `verify_referents_2f.py` — the manifest
  (34 entries; byte-idempotent; sha b94dab85…) and the 10-check cold
  battery, which stops short of any label-match rate.
- Tests: labels 8, probe 10, analyzer 15, full-shape 6 over nine
  worlds (W1 LADDER, W2 INVERTED sampler-without-probe, W3 SILENT,
  W4 manifest byte, W5 both arith_next cells void, W6 INVERTED
  argmax-without-sampler, W7 LADDER probe-only, W8 continuity gate,
  W9 exact-match pin). Every world pins itself through the production
  builders (`pins_from_world`), so the literal path is the tested
  path.

### Build findings (for the freeze and for ratification)

- **A — the m3 gate is exact.** 2b's starved probe on the committed
  activation files reproduces all four committed m3 records to the
  digit (accuracy, best site, split counts). Probing is
  deterministic on this stack (1b's finding, again).
- **B — the committed starved probes anti-generalize.** At every real
  site the starved-validation accuracy is BELOW chance (sub3_mid
  .03–.09 vs 1/10; arith_next .04–.11 vs 1/7); the "best" site at
  (0, 0) is the constant-feature majority rate. A probe trained on
  basis→label lookups predicts the wrong class on held-out basis
  values systematically. Descriptive; strengthens §1's reframing.
- **C — the probe's bar in numbers.** At n = 500 with the family's
  Bonferroni (18 / 14 sites), the minimum detectable accuracy is
  ≈ .165 against c = .12 (arith_next) and ≈ .18 against c = .132
  (sub3_mid) — §7's "+.045" is right for arith_next, and the blind
  region is exactly that band.
- **D — `sys.path` trap (build-time, closed).** 2b's `activations.py`
  imports `battery.base.render_prompt`, which resolves to 2c's
  package once 2d's path order is in force; the analyzer uses 2c's
  `screen._load_activation_map` (identical code) and the collector
  uses 2c's renderer for both rungs — justified by the fixture that
  the renderers are identical, and enforced by gate 1.
- **E — doc slips.** (a) §5 "18 sites at 410m, 14 at 1b" — correct;
  (b) §7's sampler bar "+.004 over c = .10" — the floors are .12 /
  .132, the bar at 32,000 draws is ≈ +.004 still; (c) §4 should name
  the pilot exact counts (6 | 3, 109 | 67) beside main's; (d) §3
  should say a negative first digit run is a MISS. Proposed text at
  the freeze.

### Mutation battery

56 mutants over labels / probe / analyzer / builder / collector, both
directions. FIRST PASS 37/56: nineteen survivors. Triage: four are
MATHEMATICALLY EQUIVALENT on this design and are documented rather
than chased — [6] the 1/K clause of the floor can never bind (a
majority share over K classes is always ≥ 1/K; the rule reduces to
the majority share — doc slip (e)); [14] "rate above the floor" is
implied by a one-sided p < α; [15] best-by-accuracy equals min-p at
equal n (every site reads the same 500 items); [17] "trained exceeds
the twin at the best site" is implied by "twin not detected there"
(same n, same test). One was a float-rounding no-op ([28], the
altered literal rounded to the same double — retargeted to a digit
that changes the value) and one survived by a test-message accident
([55], numpy's own broadcast error happened to contain "shapes" —
the match is now "compare_rows"). One was dead code ([32], a
redundant model_sha check behind the provenance loop — removed). The
remaining twelve were fixture gaps: `run()`-level routes only the
deselected worlds exercised (continuity and m3 failures collected;
the caveat on the record; the both-void branch; the primary label
through the cell; main vs pilot distinguishable), negatives for the
frozen-import pin, the probe-y and eval-y gates, the manifest hash,
Bonferroni at a raw-p < α site, and a twin that encodes at a
different site than the trained model. Closed with eleven fixtures
(suite 39 → 47: labels 8, probe 11, analyzer 22, full-shape 6).
SECOND PASS on the nineteen (two runs — the first was killed mid-
mutant by a foreground timeout and left [47] STRANDED in
`analyze_2f.py`; healed by hand against the mutation list, diff
verified, memory written): 15/15 killed of the non-equivalent
survivors → **52/56 killed, 4 documented equivalents, 0 real
survivors.** Worlds re-run after the fixture additions: 6/6.

### Process note

The stranded mutant is the build's one incident. A mutation harness
that edits sources in place is only safe under a runner that cannot
be killed between write and restore; the 3e precedent (`.mutation_
backup`) and this one both argue for the harness writing a backup
file FIRST and the freeze checking for its absence. Carried to the
freeze as a standing assignment (checklist).

## 2026-08-22 — FREEZE (session 3, same day on Michael's word "freeze it"; worked cold against the build's record)

Standing assignment: find the class defect. Attacked, in the
checklist's order:

1. **3a's class — an unpinned verdict input at analysis time.** The
   open()/np.load sweep on a world: 61 reads — 49 in a pinned set
   (the world's 34-file manifest, 2f's 12 frozen-import literals, the
   item-file pins, the manifest itself), 12 are the collector's own
   outputs on the tree (eval npz ×8, continuity ×4), each validated
   by its provenance meta and the continuity re-derivation. **Zero
   unpinned non-code reads.** The 12 code files opened are exactly
   the 12 frozen-import pins. CLEARED.
2. **Lesson 8 — the refusal terminal from every tree the collector
   can leave.** Executed: (i) the real trees with no collection at
   all → INSUFFICIENT_DATA, four "continuity record missing"
   failures, no exception; (ii) two of four (size, mode) collected →
   INSUFFICIENT_DATA naming the two missing records; (iii) an eval
   npz present without its continuity record → INSUFFICIENT_DATA;
   (iv) a continuity record claiming `pass: true` with bad diffs →
   INSUFFICIENT_DATA from the RE-DERIVED diffs (the runner's claim
   is ignored); (v) a twin eval file whose meta says seed 1 →
   INSUFFICIENT_DATA from the cell loader. CLEARED.
3. **Gate 1's tolerance (rtol/atol 1e-2 on fp16).** What passes:
   fp16 round-trip 0; 1e-3 relative drift → .0015; 5e-3 → .0055;
   2e-2 → .020 (FAILS). What fails: an independent random network →
   max rel ≈ 2,300; the same network with one row permuted (item
   order wrong) → ≈ 1,800. The tolerance sits five orders of
   magnitude below "a different network" and two above "kernel
   drift"; a uniformly rescaled copy (×1.005) passes — not a
   failure the collector can produce. CLEARED; the numbers go in the
   record beside the gate.
4. **The label parse against what the committed continuations
   actually begin with** (shapes only — NO label scored): argmax
   leads with a digit run in 500/500 on every cell (sub3_mid 3-digit
   498/500 and 467/500; arith_next 2–3 digits); the main draws lead
   with a digit run in 97.6–99.7 %, the first line has no digit run
   in 0.3–2.4 % (→ MISS), a 4+-digit run on sub3_mid in 2.6–5.5 %
   (→ MISS for the middle digit, outside the domain; disclosed). The
   parse reads the number the model meant. CLEARED.
5. **Probe/eval leakage:** 0 shared questions between probe items and
   eval items on both rungs; 0 duplicate eval questions. CLEARED.
6. **Site family == the committed n_candidates** (18 at 410m /
   25 layers, 14 at 1b / 17 layers) on all four cells — now PINNED
   (additive: `n_candidates` in `M3_PIN`, `m3_pin_from_record`, the
   gate, the battery's check 11).
7. **One cell's full permutation null** (arith_next/1b, 14 sites ×
   2,500 refits, 2b's `probe_starved` verbatim on the committed file,
   2,751 s) against the committed m3 record: **EXACT on every
   field** — present, accuracy, chance, null_p 1.0, null_mean
   .1450574585635359, null_std .016314308748046954, margin, best
   site, n_candidates 14, split. The machinery gate's equality is
   earned all the way down, not only on the observed fit.
8. **The bar asymmetry (§7) made executable:** `min_detectable_acc`
   printed in every probe reading (brute-force equal to the bar with
   Bonferroni): .172 / .170 on arith_next, .186 / .184 on sub3_mid
   against floors .120 / .132 — the probe needs +.05, the sampler
   +.004, argmax +.036. §7's "+.045" corrected to "+.05" (slip f).
9. **Determinism:** `compute_cell` on a world in two separate
   processes, byte-identical records. CLEARED.
10. **Unicode digits through the parse — FOUND, F-1 (small).**
    `\d` matches Arabic-Indic and full-width digits and `int()`
    accepts them, so a unicode run matched the mod-7 label while the
    digit labels could not equal an ASCII answer label — the same
    emission scored differently by kind. Closed: the parse is
    ASCII-only (`[0-9]+`); a unicode run is a MISS for every kind;
    fixture + mutant. Implausible on Pythia's outputs here; closed
    because the rule must be uniform, not because it would have
    moved a number.
11. **The mutation harness** now writes a `.mutation_backup` BEFORE
    the in-place edit and removes it after restore; battery check 11
    refuses to run with one present (the stranded-mutant incident,
    closed at the instrument level).

Class defect: **NOT FOUND.** One small finding (F-1) closed
additively; three additive pins/prints; no accepted dial touched.

### Doc slips — proposed text, apply only on Michael's word

- (a) §4: name the pilot exact counts beside main's (sub3_mid 6 | 3,
  arith_next 109 | 67 of 4,000).
- (b) §3: "a continuation with no digit run, a negative first run, a
  non-ASCII digit run, or a run outside the label's domain scores
  MISS".
- (c) §3/§5: the floor clause — "c = max(majority share, 1/K)" is
  vacuous (a majority share over K classes is always ≥ 1/K); state
  c = the majority class share, with 1/K as the lower bound it never
  binds (mutant [6], equivalent).
- (d) §7: the three bars in numbers — sampler +.004 (32,000 draws),
  argmax +.036, probe +.05 with Bonferroni (minimum detectable
  accuracy .172/.170 on arith_next, .186/.184 on sub3_mid); "+.045"
  → "+.05"; the printed `min_detectable_acc` named.
- (e) §5: "eval accuracy clears c by the bar; the site family
  Bonferroni-corrected" — add "at the same n (500) on every site, so
  the best site by corrected p is the best site by accuracy".
- (f) §9: "4,000 forward passes" → "4,064" (the 8 continuity items
  per rung × 2 rungs × 2 sizes × 2 modes) and "gate 1 inside the
  collector".
- (g) §6/§4: the continuity tolerance stated (rtol/atol 1e-2 on fp16
  activations; what passes and what fails, from attack 3).

### Cold battery at the freeze

- Suite **49** (labels 9, probe 12, analyzer 22, full-shape 6);
  referents **11/11**; worlds 6/6 after the freeze edits.
- Mutation battery re-run in full after the edits (60 mutants, four
  added for the freeze's pins): **55/60 killed; the five survivors
  are one equivalence class** — [6] the 1/K floor clause (never
  binds), [10] `min_detectable_acc`'s rate-above-floor conjunct, [18]
  `detect`'s rate-above-floor conjunct (both implied by a one-sided
  p < α), [19] best-by-accuracy at equal n, [21] trained-exceeds-twin
  (implied by the twin not detecting at that site). Documented, not
  chased; slips (c) and (e) put two of them in the doc's words.
- The duplicate null launch (a first attempt under a 10-minute
  tool timeout that survived anyway) was stopped after the first
  completed; no backup file stranded; `git diff` on the sources is
  the freeze's own edits.

### For ratification before the tag

- F-1 (ASCII-only parse), the three additive pins/prints
  (`n_candidates`, `min_detectable_acc`, `.mutation_backup`), the
  five equivalent mutants, doc slips (a)–(g).

## 2026-08-22 — RATIFICATION AND TAG

Michael: "ratified, slips as recommended — apply and tag." Slips
(a)–(g) applied to the design doc in place (§3 MISS rule incl. F-1;
§3 floor = the majority share with 1/K as the non-binding bound; §4
pilot exact counts, the m3 gate's full scope incl. the freeze's
permutation-null reproduction, and gate 1's tolerance with the attack
numbers; §5 the equal-n tie remark; §7 the three bars in numbers and
`min_detectable_acc`; §9 4,000 + 64 passes); no dial, bar or branch
moved. Cold battery re-run in fresh processes after the edits; tag
`exp2f-preregistered`. Next: `collect_eval_2f.py` ×4 on Michael's
word (the only model contact; gate 1 inside), then the projection
sealed, then `analyze_2f.run(write=True)` ONCE → `exp2f-closed`.
