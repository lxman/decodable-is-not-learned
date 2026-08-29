# Exp 2j retrospective — the projection graded, and what the record teaches

Projection sealed at `b43a414c` (after `exp2j-preregistered`, before
the analyzer ran). Verdict: **RESIDUAL** under POWERED. Projected:
**RESIDUAL** under POWERED — a HIT at the verdict level that is worth
exactly what the projection said it was worth: T_beyond .1311 was
known before the tag (slip c), and the p was arithmetic on the power
record's null SD. The forecast proper was the texture, and the
texture missed in an instructive direction.

## Hits

- Verdict: RESIDUAL, POWERED, fraction absorbed .405 (projected
  .405), p ≈ 1e-4 (landed 9.999e-05, 0/10,000).
- Referents: zero failures; every comparison gate exact; block gate
  exact with per-rung D.
- The asymmetry re-read: projected "roughly equal, no lineage/cross
  split" → landed .28–.46 across all seven pairs with no split.
- A-1 at the reading level: DENSITY projected → DENSITY landed;
  forward thinned x_B → OLMo projected .14–.18 → .1571.
- Sensitivities: LOO-π ≈ .12 → .1289; six rungs ≈ .19 → .1974;
  x_A 410m .06–.09 → .0626. Mid-digit rungs ≈ 0 either way → −.020 /
  .015 / .001.

## Misses (each one points the same way)

1. **The named per-rung disconfirmer FIRED.** antonym and antonym6
   `beyond_all` D ≥ .18 — landed .236 and .221, i.e. UNCHANGED from
   within-alone (.219/.226). The projection said the word prior (π)
   would absorb the most on the option rungs. It absorbed nothing
   there: π alone forecasts only .108/.111 on those rungs.
2. **add_base8 was absorbed far more than projected** (≥ .35 → .196,
   74 % absorbed), and by LENGTH first: the single-functional readings
   put L (.1531) ahead of π (.1759) as the strongest absorber, the
   reverse of the projection. The 2- vs 3-digit octal sum IS the top
   carry — a structural covariate 2g's carry stratum only partly
   captures.
3. **π alone forecasts far more, and elsewhere, than projected.**
   Projected "fires on the option rungs' own D"; landed T .1993 overall
   — nearly the count's .2204 — with add_base8 .782 (above the count's
   .741), sub4_mid .326, sub_base8 .311, add3_mid .269, and near zero
   on the option rungs. The small model's habit of emitting particular
   NUMBER strings as wrong answers forecasts which of those numbers
   the large model learns first, including on the mid-digit rungs
   where the count forecasts nothing. The projection had the sign of
   the mechanism right (an answer prior exists and forecasts) and its
   location wrong (numbers, not words).
4. **A-1's gap magnitudes**: 6.9b projected ≈ .6 [.35, .85] → 1.051;
   2.8b ≈ .5 [.3, .8] → .870. Density explains MORE of the reverse
   asymmetry than projected — all of it on 6.9b. (These two numbers
   reached the controller after the projection was sealed, via the
   independent review of the freeze diff; graded on the sealed range.)
5. **Terciles**: projected lower than the median split (.10–.12) →
   .1395, HIGHER. Finer buckets absorbed less, not more: the
   tercile cut on π/L splits the mid-digit rungs' near-constant
   functionals differently, and the projection's "finer absorbs more"
   intuition was wrong on a partition this coarse.

## Reading the result honestly

RESIDUAL means: the count carries item-specific information the four
functionals do not — at T .131, 60 % of the within-lineage forecast.
It does not say what that information is. The printed decomposition
says where the 40 % went: answer length and answer prior on base-8
addition, and length generally; not the word prior, not repetition,
not input overlap. And it says something the design did not ask:
the answer prior in the small model's mouth is itself a forecaster
of emergence order (.199), on the arithmetic rungs, including rungs
where the count is silent. That is a second mechanism, not a
correction to the first.

A-1 says the 2i reverse-direction asymmetry was information density:
at eight to eleven draws OLMo-2 1B reads Pythia's order exactly as
well as Pythia-1b at sixty-four. On OLMo's own outcome half the
lineage advantage is density and half is not (.157 vs .095 at matched
budget). So 2i's cross-family A (.0949, sub-bar) is partly a
thin-predictor reading, and the ladder gives the exchange rate: one
OLMo-1B draw ≈ eight Pythia-1b draws on Pythia's outcomes, ≈ sixteen
on OLMo's.

## Process notes for Michael's call (methods-paper candidates)

- **The import surface is a verdict input** (freeze F-1). Every
  previous analyzer in this line pinned the files it OPENED and the
  modules it NAMED; none pinned the modules Python executed on its
  behalf, and the read sweep — the tool built to find unpinned inputs
  — cannot see imports by construction. Two lines in an empty
  `__init__.py` moved the primary. Candidate rule: the verdict path's
  `sys.modules` under the repo is pinned, at entry and exit.
- **A sweep that prints the verdict is a disclosure event** (slip c):
  the read sweep at n_perm 30 was a plan step; its incidental output
  was the real T. Rule: any pre-tag execution of the analyzer on the
  real tree is logged as knowledge in §2 before the tag, not after.
- **A projection on known inputs should forecast the TEXTURE and name
  it as the test** — the verdict-level hit here was worth nothing; the
  per-rung and single-functional calls were where the foresight was,
  and two of three missed.

## Numbers at a glance

| | T | p | fires |
|---|---|---|---|
| primary: x_B → OLMo-7B beyond π+L+R+O | .1311 | 9.999e-05 | yes |
| within-alone (2i, reproduced) | .2204 | — | — |
| beyond π / L / R / O singly | .1759 / .1531 / .2167 / .2184 | — | — |
| π alone / L alone / R alone / O alone | .1993 / −.1633 / −.0210 / .0260 | 1e-4 / 1.0 / .98 / .046 | π only |
| A-1 gap fraction closed 2.8b / 6.9b / OLMo | .870 / 1.051 / .505 | — | DENSITY |

Analyzer wall time 94 min at N_PERM 10,000 (≈120 permutation tests;
the sensitivities' discarded singles cost ≈ 30 min — the deferred
minor, now priced). One pre-committed change UNSPENT.
