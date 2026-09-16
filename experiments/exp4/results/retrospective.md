# Exp 4 retrospective — grading projection 854f526b

The projection was sealed 2026-09-14 after the reference stage, power
and the seal, after campaign stop #1's ruling, before the first sweep
unit loaded. The analyzer ran once, 2026-09-16 05:54–05:58, on the
complete tree at 610a6af3; the verdict is committed at 12d747df and
tagged `exp4-closed`. Everything graded below is read from
`verdict.json`; the two post-verdict re-reads are marked as such
(committed bytes, no model contact, not part of the frozen record).

Design §2's caveat governs every line: a preregistered reading on a
known outcome, not a forecast.

## Verdict level — HIT on the world and the range, the R-7 cell the one that obtained

**LEADS.** T **.6102**, p₊ .00048828 (16 of 32,768 exact sign flips
over 15 rungs), CI95 [.3251, .9501] by rung-clustered bootstrap
(10,000), 26 cells on 15 rungs. Projected: LEADS, T ≈ .50 in
[.35, .65], p₊ < .001. World HIT; range HIT; point MISSED by +.11
(inside the range, short of the .65–.70 "high LEADS" tolerance).
Neither named disconfirmer fired: not PARTIAL (T in (0, .25)), not
the upper (T > .70). Read under POWERED (null SD .0395, min-detectable
T .118).

**The R-7 cell obtained.** The projection put .25 of the LEADS mass on
"LEADS with the licence condition NOT met because the observed λ̂ puts
the realized α above .05", with λ̂ projected at 1.2–1.8 per trajectory.
Observed λ̂ (the flat pool's between-step excess scatter over its
item-bootstrap SE): pythia_2.8b **6.23**, smollm3_3b **6.47**, olmo2_7b
**7.30**, comma_7b **7.32**. Every trajectory sits above the
zero-excess arm's top scatter multiple (3.0), where the LEADS rule's
realized α is already .264 (.019 / .144 / .246 / .264 at 1.0 / 1.5 /
2.0 / 3.0, plateauing between 2.0 and 3.0). The cell was named and it
is the one that obtained: HIT as a cell. The λ̂ point and range MISSED
by a factor of ~4, and the observed value is OFF the calibration
grid — the realized α at λ̂ ≈ 7 is not quantified by the frozen record,
only bounded below by the grid's plateau. Under §6 as written, the
LEADS licence is claimed only where that α is below .05 at the
observed λ̂; it is not, so **the world is LEADS reported with the
calibration disclosed, and the essay sentence is bounded to "above the
selection-inflated null."** Under eligibility selection the null mean
of φ is ≈ .5 (the fix wave's prediction, .499 on the real table), so
the lead over the null is ≈ .11 of T, real in sign on 15 rungs at
p₊ 5e-4 by the exact flip null, of unquantified strength against the
scatter-inflated null.

**The §6 licence condition (≥ 2 of 4 per-trajectory readings at p₊ <
.05 and T ≥ .25) is MET through olmo2_7b and comma_7b** — exactly the
two the projection named. HIT.

## Per trajectory — 2 hits / 2 misses, the spread the real texture

| trajectory | projected | actual | grade |
|---|---|---|---|
| olmo2_7b (9 cells) | ≈ .50, p₊ < .01 | **.9589**, p₊ .0039 | p HIT; T MISS, +.46 above |
| comma_7b (9) | ≈ .55, p₊ < .01 | **.5120**, p₊ .0059 | HIT on both |
| pythia_2.8b (4) | ≈ .40, p₊ may not clear .05 | **.1834**, p₊ .375 | p as projected; T MISS, −.22, under the bar |
| smollm3_3b (4) | ≈ .55, thin | **.4736**, p₊ .125 | within .08, thin as projected |

OLMo-2 7B's nine cells carry almost their entire endpoint excess
before the clear (φ .57–.96 on seven of nine; antonym6 1.32 and
add_base8 2.97 above one at small x_end; sub3_mid −.12 the one
negative). Pythia 2.8b's four sit at .39 / .64 / .82 and sub3_mid
−1.12 (x_end .019, the smallest eligible excess on the trajectory) —
the mean is the −1.12 cell's doing; the other three are inside the
projection's range. The per-trajectory spread (.18 to .96) is where
the texture lives; the projection had them within .15 of each other.

## Per rung type — the ordering's bottom held, the spread did not

Projected string ≈ .75 / arithmetic-order ≈ .50 / option ≈ .35, with
the per-type disconfirmer "option ABOVE string". Actual: arithmetic
**.6282** (13 cells, p₊ .021), string **.6243** (4, p₊ .25), option
**.5780** (9, p₊ .0625). The disconfirmer did NOT fire (option is
last, as projected); string-first missed by .004 — string and
arithmetic are tied; all three points MISSED (string −.13, option
+.23, arithmetic +.13). The projected spread was .40 wide; the actual
is .05. **The window-length mechanism the projection argued from —
long pre-clear windows should carry more of the excess — is not what
the data show: φ is ≈ .6 whatever the window.** No per-type tolerance
was written; 2n's process note ("per-rung tables by rung type with
tolerances") was applied to the trajectories and not to the types.

## Secondaries — 9 hits / 8 misses / 4 ungradeable as projected

- **S1 (order) MISS.** Pooled Somers' D **.109** (projected ≈ .3);
  per trajectory .20 / .24 / −.06 / .05, every block p ≥ .33. The
  reading the projection wrote for this case is the one obtained: a
  null D with a firing primary — the timing carries a lead, not a
  rung-specific order. Quarter/three-quarter variant .166.
- **S2 (the third instrument on 2d's question) HIT.** AUC **.648**
  on the Pythia ladder at 1b, block p .27, cluster CI [.455, .864] —
  under 2d's .75 bar as projected (point +.05). Known-answer gates
  exact (.5455 / .6126). The rung-level from-below forecast now reads
  .5455 (sampled rate), .6126 (floor-adjusted), .648 (representational
  excess): three instruments, none clears the bar.
- **S3 (the Pythia size ladder) — the frozen descriptive MISREADS
  it; the projected phenomenon HOLDS on a post-verdict re-read.**
  As frozen, S3 averages alignment LEVELS over the pinned site family
  INCLUDING hidden-state 0 — the degenerate constant (k-NN sets
  identical in every model at the constant prompt-end token, alignment
  exactly 1.0) that stop #1 excluded from gate 0 and nothing else.
  Its share of a level average is 1/n_sites: .333 at 70m (3 sites),
  .200 at 160m, .111 at 410m, .143 at 1b, .083 at 2.8b/6.9b, .077 at
  12b. So the frozen S3 reads the ladder FALLING with size (global bank
  ρ −.52, 70m .464 → 12b .367; 24 of 34 rungs negative; add3_mid
  −.88, hamming12 −.90) — a MISS against "rises with size, Spearman >
  .8 on the option rungs". Re-read from the committed `align.json`
  tables with site 0 dropped (post-verdict, no model contact): the
  mean level over 34 rungs is .198 (70m), .216, .252, .266, .299,
  .313 (2.8b), .304 (6.9b), .317 (12b) — **34 of 34 rungs rise with
  log parameters, median ρ .89; option rungs antonym .98, antonym6
  .88, odd6 .90, odd_one_out .86, median7 .76, median5 .62** (four of
  six above .8); string rungs .93–1.00; mid-digit .62–.90. The
  projection's phenomenon HIT; the frozen instrument's reading of it
  MISSED in sign. The largest single step MISSED: 160m → 410m (+.036)
  and 1b → 1.4b (+.033), not 410m → 1b or 1b → 2.8b; 2.8b → 6.9b is
  the one negative step (−.009). The primary and S4 are immune (the
  constant cancels in every excess); the level descriptives are not.
- **S4 (size-axis φ) HIT on the median.** Ten rising rungs readable
  (antonym6 clears at index 1, no window): mean .72, median .47
  against ≈ .5; coarse, as declared.
- **S5 — (a) VACUOUS, (b) HIT.** The max-over-pairs reading is 1.0 on
  every model, every rung, every step: the argmax pair is (0, 0), the
  degenerate site pair, so the excess is identically zero and φ is
  null on 26 of 26 cells. Projected "levels ≈ .05 higher, φ within
  ±.05" — MISS, and an instrument blind spot (below). The
  endpoint-best-site variant gives T .5785 against .6102 — within .05
  (magnitude HIT), slightly LOWER where "slightly higher" was
  projected. The final-layer variant reads 1.96, one OLMo-2 cell with
  a tiny final-layer x_end dominating; unprojected.
- **S6 (question-end position) HIT on the excess, ungradeable on T.**
  x_end at the question end is below .05 on 25 of 26 cells (mostly
  under .02), so φ is unstable there (|φ| to 34). The frozen analyzer
  prints per-rung φ only; the projected "lower T" has no number.
- **S7 (Huh's pooled construction) partial.** Per-rung φ only; the
  pooled task-specific excess is NEGATIVE on most cells (OLMo-2 eight
  of nine, Comma five of nine) — "smaller task-specific excess" HIT
  in direction; "higher levels" ungradeable (the pooled global bank
  was not committed by the build: "Task 3 stores the prompt-end
  position's global bank only", disclosed in the record); "T within
  ±.1" ungradeable.
- **S8 — twins MISS, ceiling MISS, within-family direction HIT.**
  Twins .12–.45 per rung (means .24 / .22 / .21 / .19 per trajectory)
  against .11–.18: the option rungs sit at .41–.45 and clock24 at
  .34–.40 — surface structure the untrained twin shares with every
  reference (listed options, clock formats), plus site 0's 1/n_sites
  share (.083 at twelve sites). The references' mutual ceiling
  .21–.31 (OLMo-2 × Comma .311, Pythia-12b × OLMo-2 .302 the two
  highest) against .35–.40. Within-family (Pythia 2.8b against 12b
  along the trajectory): .360 at step 1000 → .538 at 143000, ≈ .2
  above the cross-family endpoint levels (projected ≈ .1 higher: the
  direction HIT); φ not computed.
- **S9 (CKA) HIT at the level it measures.** Unbiased linear CKA on
  the endpoint–reference pairs is positive at every site ≥ 1 (.3–.8);
  site 0 is undefined or negative (a constant input). Levels only, by
  scope.
- **S10 (item grain) HIT.** Mean D **.030** over 26 cells against
  ≈ .03; nine cells at |D| > .1 (rev_string7/SmolLM3 .30, sub3_mid
  .17–.18 on Pythia and OLMo-2, sub_base8/OLMo-2 −.15) — heterogeneity
  the projection did not name.
- **S11 — two hits, one miss, one ungradeable.** The excess's largest
  single step coincides with t_clear on **1 of 26** cells (3.8 %;
  projected ≤ 30 %) HIT. The count's fraction of the bar at t⁻: mean
  **.59**, median .68 (projected ≈ .6) HIT. Per-reference leadership
  MISS: **Pythia-12b leads on 6 of 9 eligible cells on BOTH 7B
  trajectories** (tallies over all cells with a φ: Comma 7 / 5 / 3,
  OLMo-2 6 / 2 / 1 for Pythia-12b / the second / the third) where "no
  single lens on more than half" was projected; on Pythia's own cells
  Comma leads 3 of 4. The flat pool's concavity in log tokens is
  ungradeable as stated — the grid is in training steps and the
  analyzer notes that a token-per-step conversion was not built.
- **Calibration MISS**, graded above.

Sensitivities, unprojected: the clears-and-stays primary reads T
.5815, p₊ .0016 — LEADS holds under the stricter clear, but comma_7b
falls to p₊ .0508 there, so the §6 condition would read 1 of 4 under
that rule — the licence condition sits at a boundary. The
family-matched trend gives .555 over the 4 cells with a sibling.
Endpoint levels at k = 5 / 10 / 20 are .35–.38 / ≈ .37 / .40–.44 per
trajectory. The §7 known answer holds: the ladder's 2.8b `main` set
tables equal the step143000 endpoint's on 34 of 34 rungs.

## What the misses say

1. **The calibration is the finding the verdict has to carry.** The
   flat rungs' alignment wobbles between adjacent checkpoints by 6–7×
   the item-sampling noise on every trajectory — checkpoint-to-
   checkpoint representational drift, not item noise, is the null's
   scale — and the zero-excess arm's grid stopped at 3×. The LEADS
   rule's realized α at the observed λ̂ is therefore known only to be
   ≥ .264. The exact flip null (p₊ 5e-4) says the sign of the lead is
   consistent across rungs; it does not say how far .61 sits above a
   null whose mean is ≈ .5 under selection. The bounded sentence is
   the honest one.
2. **Per-trajectory, not per-type.** The projection spent its
   mechanism on window length and got a flat type table; the real
   spread is OLMo-2 .96 against Pythia .18. Whether that is the
   trajectory (OLMo-2's log-headed grid resolves the early clears;
   Pythia's four cells include the −1.12) or the family is not
   separable on four trajectories.
3. **The degenerate site contaminates every level, and only gate 0
   was fixed.** Stop #1 found hidden-state 0's constant in gate 0 and
   the one pre-committed change excluded it there — correctly scoped,
   since the primary cancels it. But S3, S8's twins and ceiling, and
   S5(a) read levels, and the max-over-pairs variant is exactly the
   construction the constant defeats (the maximum over site pairs is
   the degenerate pair). The frozen S3 reports the size ladder in the
   wrong direction because of it. The re-read above is descriptive
   and post hoc; the frozen record stands as written.
4. **The biggest reference leads.** Pythia-12b, the largest of the
   four lenses, is the reference on which the task-specific excess
   arrives earliest on both 7B trajectories. Descriptive; a lens-size
   effect is one reading, a family effect (Pythia-12b is the odd one
   out in corpus) another.

## Tally

Verdict HIT (LEADS); T range HIT, point MISS (+.11); R-7 cell HIT as
named, λ̂ MISS (×4, off-grid); licence condition HIT (the two named);
per trajectory 2 / 2; per type: disconfirmer did not fire, ordering's
bottom HIT, three points MISSED, spread MISSED; secondaries 9 hits / 8
misses / 4 ungradeable (S6 T, S7 levels and T, S8 within-family φ,
S11 concavity). Every miss that is science points the same way as
2g's: rung-level mechanism stories (window length, lens neutrality)
did not cash out; the cheap verdict-level call was right.

## Process notes (Michael's call whether any earns the methods paper)

1. **A calibration grid must bracket every plausible value of the
   quantity it calibrates.** The zero-excess arm's scatter multiples
   (1, 1.5, 2, 3) were chosen from synthetic worlds; the observed
   λ̂ was 6–7. The cost of a grid to 10× or 20× was minutes; the
   cost of stopping at 3× is a licence read against a lower bound.
2. **A degeneracy fix must be traced to every consumer of the
   degenerate quantity.** Site 0 was excluded from gate 0 (the one
   change); S3, S8 and S5(a) kept reading the constant, and the
   freeze did not ask which other readings the same constant enters.
3. **Every projected number needs a tolerance, per-type ones
   included** (2n's note, applied to trajectories and not to types),
   and a mechanism argued from (window length) needs its own
   disconfirmer written as such.
4. **A secondary projected as a T must print a T.** S6 and S7 were
   projected on T and the frozen analyzer prints per-rung φ for them;
   two of the four ungradeables are that gap.
