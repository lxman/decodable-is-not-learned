# Exp 2j — projection, sealed before the analyzer runs

Sealed after `exp2j-preregistered` (cec95d77), before `analyze_2j`
has been run with `--write`. Analysis-only; no model is touched by
the campaign; the campaign is the analyzer run.

**Disclosure first (design §2, slip (c), 2e's precedent).** The
author of this projection has seen every input: 2i's committed
outcome and verdict, x_A, x_B, the per-rung concordances in every
direction, and — from the build's read sweep at n_perm 30 — the
primary's own T_beyond on the real tree, **0.1311**, against a
within-alone T of 0.2204 (2i's, reproduced exactly by the comparison
gate). T does not depend on n_perm. What follows is therefore mostly
arithmetic on known numbers plus a forecast of the things the sweep
did not print (the per-rung decomposition, the singles, A-1); a hit
at the verdict level is evidence that the functional was a fixed
map, not of foresight, and is graded as such in the retrospective.

## Verdict level

**RESIDUAL**, with `declared_status = POWERED`. T_beyond = 0.1311
(known) clears the .10 bar; the permutation null under the composite
strata has SD ≈ .0114 (power record) and mean ≈ 0, so the observed T
sits ≈ 11 null SDs out — p at 10,000 permutations ≈ 1.0e-4 (0 of
10,000 ≥ T_obs). Fraction absorbed = 1 − .1311/.2204 = **0.405**.

Named disconfirmer (verdict level): p ≥ .01 at 10,000 permutations —
would mean the composite null is far heavier-tailed than the power
record's simulation says (the null there was calibrated on these
same strata); grades the projection MISSED and the verdict ABSORBED
under POWERED, i.e. a measured absence.

## Per-rung (beyond_all vs within-alone; the forecast proper)

- add_base8 stays the top locus: within-alone .741 → beyond ≥ .35
  (range .30–.55). Its L bucket is the top carry (2 vs 3 digits) and
  overlaps the base stratum; π on an octal answer space of 100
  distinct strings absorbs some.
- sub_base8: .341 → .15–.28 (52 distinct answers; π bites hardest
  here among the arithmetic rungs).
- arith_next: .275 → .12–.22.
- antonym6 .226 and antonym .219 → the MOST absorbed in relative
  terms (a word prior is exactly what π measures on option rungs):
  beyond .05–.13 each.
- odd6 .095 → .03–.08.
- add3_mid .053, sub3_mid .027, sub4_mid .007 → ≈ 0 either way
  (contribute nothing, as in 2i).
- Singles: `beyond_single["pi"]` the lowest of the four on the
  option rungs (π absorbs the most there); `L` the most absorbing on
  add_base8/sub_base8; `R` and `O` absorb little anywhere.
  `alone["pi"]` fires on the option rungs' own D (≥ .10 on antonym /
  antonym6), i.e. the answer prior forecasts emergence order by
  itself on those rungs.
- Named per-rung disconfirmer: antonym or antonym6 `beyond_all` D
  ≥ .18 (π absorbs nothing on an option rung) — would say the word
  prior is not what the count reads there.

## The asymmetry re-read (§5.5, printed)

Cross-family pairs more absorbed than within-lineage: x_A → OLMo
(.0949 → ≈ .05–.07), x_B → 2.8b / 6.9b (.2612/.2974 → ≈ .15–.20),
x_A → 2.8b / 6.9b (.1672/.2020 → ≈ .09–.13). Point: fraction absorbed
≈ .40 within-lineage vs ≈ .35–.45 cross-family — roughly equal, i.e.
the lineage increment is NOT specifically the non-structural
residual. Disconfirmer: cross-family absorbed ≥ .60 while
within-lineage ≤ .40.

## A-1 (non-gating)

Reading **DENSITY** — the thinned x_B closes ≥ half the gap to x_A on
both Pythia outcomes: gap fraction ≈ .6 on 6.9b (range .35–.85), ≈ .5
on 2.8b (range .3–.8). Basis: the §2 table — the asymmetry lives on
add_base8 and arith_next, exactly the rungs where x_A is thinnest
(k_g 7 and 9) and where thinning x_B to 7–9 draws will cost it the
most; sub_base8/antonym/antonym6/odd6 show no asymmetry and are
thinned less. Forward (x_B thinned → OLMo): T falls from .2204 to
≈ .14–.18 — still above x_A's .0949, i.e. lineage survives at Pythia's
density. Disconfirmer: gap fraction < .3 on both outcomes
(NOT-DENSITY: the asymmetry is the model's, not the draws').

## Sensitivities

Terciles: beyond_all lower than .1311 (finer absorption), ≈ .10–.12
— may sit at the bar. LOO-π: slightly lower than the primary (the
leave-one-out marginal credits same-answer correctness), ≈ .12. Six
carried rungs: higher, ≈ .19 (the three mid-digit zeros removed).
x_A 410m → OLMo beyond structure: ≈ .06–.09 (from .1154 within
base strata).

## Referents

Zero failures expected: every 2i/2g/2h comparison gate exact (they
passed at n_perm 30 and T is n_perm-independent); import surface,
frozen pins, manifest, seals, gate 1, power partition all as at the
freeze head; block gate exact including per-rung D.
