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
