# Experiment 2k — projection, sealed before the analyzer runs

Written 2026-08-30 after the campaign, the seal and the power record,
before `analyze_2k.run()` has been executed on the complete tree (its
ten pre-tag executions all landed INSUFFICIENT_DATA on the missing
tier; none printed a primary). Graded in `results/retrospective.md`
after the analyzer runs ONCE.

**Disclosure (design §2, verbatim).** The outcome. 2i's 7B stage-1
sweep — per-item bits at 21 grid points on all 34 rungs, y_i the count
of points at which item i verifies — is committed under `exp2i-closed`.
This is 2d's and 2e's situation, not 2g's or 2i's: 2k tests a
zero-free-parameter predictor fixed before sampling against an outcome
that is already on disk. It is not a sealed forecast. A DENSITY verdict
licenses "the cross-family predictor clears its preregistered bar at
256 draws on 2i's outcome"; it does not license "Prediction 2 supported
across families", which stays reserved for a sealed-outcome experiment
(approach C).

What the projector knows beyond the design doc: the campaign's per-seed
verified tallies (ledger), which show seeds 1–3 firing at seed 0's rate
on every cell (antonym/1b 4368/4251/4356/4290; add_base8/1b
170/150/155/169; sub4_mid/1b 15/9/7/5) — i.e. the three new blocks are
draws from the same law, not a different regime. No concordance has
been computed.

## The verdict-level call — stated as expected, worth little

**DENSITY.** T_A^(256) in **[.13, .19]**, point ≈ .155, p at the
permutation floor. The 2j ladder's per-doubling increments
(.012/.016/.021/.025 at 4→8→16→32→64) continue at ≈ .025–.03 for
64→128 and 128→256, from .0949; the x_B-shape alternative puts 256 at
x_B's k ≈ 12–16 ≈ .16–.18. Both clear .10 with margin, which is why the
design said in advance that this call carries no foresight. **Named
disconfirmer: T_A^(256) < .10** — it would say the prefix-thinned
ladder does not extrapolate to independent blocks, or that seed 0 was
a favourable block (S1 shows which).

## The texture — where the foresight is

**Per-rung D at 256 (1b), the named calls.** The density account
predicts the gain lands where x_A^(64) was thinnest among the six
carried rungs (2j §2's table) and nowhere on the mid-digit rungs:

| rung | D at 64 (2i) | projected D at 256 | call |
|---|---|---|---|
| sub_base8 | .338 | .36–.44 | stays the top rung |
| add_base8 | .242 | **.38–.50** | the largest absolute gain (rate .0053 at 64: 170 → 644 verified draws) |
| arith_next | .064 | **.14–.22** | the second-largest gain |
| antonym6 | .101 | .11–.16 | modest |
| odd6 | .078 | .09–.14 | modest |
| antonym | .028 | .03–.08 | ≈ flat: already dense at 64 (rate .137) |
| sub3_mid | .020 | −.02–.06 | ≈ 0 (175 verified draws over 500 items) |
| add3_mid | .005 | −.02–.05 | ≈ 0 (41) |
| sub4_mid | −.022 | −.04–.03 | ≈ 0 (36) |

Named: **add_base8 and arith_next gain the most; the three mid-digit
rungs stay ≈ 0; sub_base8 remains the top rung.** The six carried
rungs' mean ≈ .20–.26 (2i: .1418). Disconfirmers: a mid-digit rung
above .08; add_base8 not among the two largest gains; antonym gaining
more than antonym6.

**S1 — block replication.** The four 64-draw blocks read T in
[.07, .12] each; **block SD in [.006, .018]**, i.e. of the order of the
.005 bar gap or larger — the reading that 2i's fires = False was inside
sampler noise. Seed 0 is not an outlier (its T sits inside the other
three's range). Disconfirmer: block SD < .004, or seed 0 the extreme
block.

**S2 — the nested ladder.** Monotone: 64 < 128 < 192 < 256, increments
shrinking (≈ .03, .02, .015): the curve is past its linear-in-log phase
by 256. Disconfirmer: a non-monotone step.

**S3 — the matched comparison.** x_B thinned to k_g (28/37/45/27, cap
elsewhere) reads **.16–.19**, ABOVE x_A^(256): the lineage increment
survives at high density, at ≈ .01–.05 (2j measured .062 at low
density). Placement: x_A^(256) lands between x_B's k = 8 (.1451) and
k = 16 (.1764) — k-equivalent ≈ 10–16 — not beyond 64. Disconfirmer:
the increment's sign negative (x_A^(256) above thinned x_B), or a
placement bracket at [64, None].

**S4.** cross_beyond_within_256 ≈ .09–.13 (2i: .0701 — the shared
component grows with density); within_beyond_cross_256 ≈ .17–.21 (2i:
.2153 — the zero cut at 256 removes more of x_B's information).

**S5 — within-lineage forward density.** x_A^(256) → 2.8b (R_28, seven
rungs) **.21–.26** (from .1672); → 6.9b (seven rungs) **.24–.30** (the
seven-rung 64-draw anchor ≈ .20–.22). Gains of the same size as the
cross-family one — density is family-blind.

**S6 — 410m.** The 410m primary-form T at 256 **≥ the 1b one** (2i:
.1154 vs .0949 at 64), in [.14, .21]; 410m's per-rung ordering the same
(add_base8, sub_base8 on top). Disconfirmer: 410m below 1b at 256.

**S7.** Live items at 256: add3_mid ≈ 25–35, sub3_mid ≈ 90–130, sub4_mid
≈ 20–30 (from 10/31/13 at 64) — still too few to carry a D.
First-correct outcome ≈ the count outcome − .02.

**Power.** POWERED at D = .15 (P ≈ 1.0), null SD of T ≈ .009–.011,
P(fires | D = .10) ≈ .4–.6: the bar decides, not p.

## What would change the reading

If NOT-DENSITY(structured): the shortfall is not density; the essay's
lineage wording stands. If S1's block SD is large (≥ .015) the 2i bar
verdict is re-read as a coin flip regardless of the 256 result. If the
mid-digit rungs move, the density account has a rung it did not
predict.
