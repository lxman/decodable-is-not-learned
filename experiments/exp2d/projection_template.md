# Exp 2d — Projection (SEALED before the analyzer runs)

Standing practice since 1c: the projection is written and committed
before `analyze_2d.run()` executes on the real tranche, then graded in
the retrospective. The known-outcome caveat (§2) applies: the OUTCOME
column was known when 2d was designed. **Disclosure for this
projection:** the pilot and main tranches were complete and committed
by the watcher before this was written, and the runner prints each
rung's verified count as it lands, so the PREDICTOR's per-rung
tallies were visible in the campaign logs; what is projected below
is the frozen analyzer's OUTPUT — the statistics, the tree's branch,
the secondaries — and the argmax tier, whose records did not yet
exist when this was sealed (the argmax driver was launched minutes
before; this file is committed without any of its records).

## Sealed at commit: (this commit) — 2026-08-22

### Verdict
- Projected verdict: **FAIL** (the §6 tree's second branch: the
  family-cluster bootstrap CI on AUC includes .5), read under
  DECLARED UNDERPOWERED IN ADVANCE as "not detected at this
  resolution".
- Projected AUC (point): **.5455** = (23 + 10 × 23 × ½) / (11 × 23):
  one rising rung (arith_next) above every flat rung, ten rising rungs
  tied at zero with all 23 flat rungs.
- Projected block p: **≈ .67** — with a single positive rung the
  permuted AUC is ≥ the observed iff arith_next's slot receives a
  rising label; over the size-2 group (9 families: four (1,0), two
  (1,1), three (0,0) patterns) that slot is labelled rising in 6 of 9
  block assignments. Not below .01 by any route.
- Projected cluster CI: **[.5000, ≈ .59]**; lower bound exactly .5
  because every resample that omits the seq_extrap family has all
  rungs tied (AUC = .5 exactly) and P(omit) = (15/16)^16 ≈ .36 ≫ .025.
  Projected drop count: ~1–2 of 10,000 (resamples with no rising
  family, expected ≈ 1.0).
- Declared status carried from `power_2d.json`: DECLARED
  UNDERPOWERED IN ADVANCE (symmetric rule; power at AUC .85 = 0.000;
  at .75 = 0.000; at .5 = 0.000; the Tobit as built .7365 / .302 /
  0.000, agrees).

### Gate 1 (production path, 128,000 draws)
- Already on the record from the campaign: IDENTICAL in 4/4 cells,
  fire at (reverse_string, 1b, item 436, draw 6) reproduced; the
  analyzer's own re-comparison of the main rows must agree (0 diffs).

### The predictor's zero set (main, 32,000 draws per rung per size)
- Rungs with predictor score 0: **33 of 34** — every rung except
  arith_next.
- Rising rungs with predictor score 0 (the power-killing set): **10**
  — sub4_mid, add3_mid, sub3_mid, antonym6, antonym, count_div13,
  median5, odd6, sub_base8, add_base8.
- Rising rungs with RAW zero at 1b: **0** (every rising rung has
  verified draws at 1b; the smallest is add3_mid at 10 / 32,000).
- Flat rungs with raw zero at 1b: rev_string7 only (reverse_string
  has its committed single fire).

### §5.4 named secondaries
- sub3_mid sampled 1b: 34 verified / 32,000 (rate 1.06e-3, CP95
  ≈ [7.4e-4, 1.5e-3], below its .014 floor) — percolation candidate?
  **no** (the rule needs a zero count).
- arith_next sampled 1b: 531 / 32,000 (1.66e-2, below its .020 floor
  at 1b; above it at 410m) — percolation candidate? **no**.
- Both pair rungs land as candidates: **no** — the named disconfirmer
  does NOT fire. The pair is probe-flat AND sampled-below-floor at 1b,
  but not sampled-SILENT: the sampled channel reads both (1e-3 and
  2e-2) two to three orders of magnitude above the reversal class.
- Probe predictor's AUC on the same label (from committed records):
  .6703 — projected block p ≈ .05–.15, CI including .5; i.e. the
  probe ranks the rising set BETTER than the sampler does on this
  battery (a projection the retrospective should grade explicitly).
- Spearman ρ predictor vs corrected ascent: ≈ +.20–.30 (one positive
  rung on a rising rung against 33 ties; block p ≈ .67 by the same
  argument); vs 2c's frozen ascent: similar magnitude (2c's probe:
  .368).
- Argmax 1b (records did not exist at sealing): projected number of
  rising rungs already performable at 1b: **2–3** — antonym (greedy
  well above .298), antonym6 (above .208), possibly arith_next
  (greedy above .038) — median5 / odd6 / count_div13 / the base-8 and
  mid-digit rungs not. Projected flat rungs performable at 1b: none
  (hamming12 greedy near but under .272; the modulus rungs under).
- Restricted primary AUC (projected): with arith_next removed if
  performable, the restricted set has NO positive rung → AUC exactly
  .5, CI [.5, .5]; if arith_next is kept, AUC ≈ .56 on 8–9 rising vs
  23 flat. Either way the restriction changes nothing about FAIL.
- Argmax vs exp3 redecode (descriptive, 4 reversal cells): 0 diffs
  projected (fp16 greedy on the same stack that just reproduced the
  sampled streams byte for byte).
- Within-family concordance: undefined (NaN) in every mixed family
  except seq_extrap (arith_next > quad_next in both columns: ρ = +1).

### Named disconfirmers
- The projection is WRONG at the verdict level if: the tree returns
  anything other than FAIL — i.e. if the cluster CI excludes .5 (it
  cannot, by the seq_extrap-omission argument) or gate 1 is read as
  dirty (it is not).
- The named disconfirmer of the ladder story (both pair rungs silent
  at 1b with probe margin 0): does NOT fire — 34 and 531 verified
  draws.

### Misses I expect to be graded on
- The block p point value (.67 is an argument, not a computation) and
  the CI's upper bound.
- The argmax performability count (2–3 rising; 0 flat) — greedy at
  1b on option-listing rungs is the least-known quantity here.
- The probe-AUC block p.

### What the numbers already say, written before the analyzer
The sampled channel at 410m/1b does not clear the format-guessing
floor on 10 of the 11 rungs that rise above it by 12b — not because
32,000 draws are too few (the CP95 upper bounds exclude the floors,
with rates 25–75 % of the floor on the option-listing rungs) but
because a T = 1 sampler at these sizes emits non-answer text often
enough to undercut a random option copier. The one rung it clears
(arith_next) it clears at the SMALLER size and not the larger. FAIL
here is the frozen tree's literal output; "not detected at this
resolution" is the §6 reading under the declaration; the blind region
is rates between each rung's pilot/main CP95 upper bound and its
floor. The ladder finding of 3b–3e (sampled > argmax at the bottom of
the ladder) is untouched — it lives on the reversal rungs, which sit
at 0/0/1 verified here as committed — but it does not generalize to
"the sampled rate forecasts ascent across a battery" at this
resolution with this floor.

### What I will NOT do after seeing the numbers
- No slicing of the battery; no alternative floors (the option-copy
  floor stays at 1/n); no second statistic; no k = 128 deepening
  framed as part of 2d; the one pre-committed change stays UNSPENT.
