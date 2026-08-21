# Exp 3e — Retrospective (2026-08-21)

**VERDICT: NO-SHORTCUT (misfire-rate).** n = 17 distinct new-fired
items at 1b, X = 4 of them non-reachable against a null expectation of
4.91; p_low .395, p_high .830; non-THIN. 410m: n = 9, X = 1, THIN,
unreplicated (p_low .186). Specificity arm MISFIRE-RATE: 50 reverse
emissions of 157 matched events (share .318), p .480. Gate 1 clean at
both sizes; 0 leak voids; 0 twin fires; every loader and gate green;
campaign 206.8 min, zero stops, zero attrition; pre-committed change
UNSPENT.

## The projection, graded (sealed in `5a9eed9` before any tranche draw was scored)

| projected | observed | grade |
|---|---|---|
| SHORTCUT at 1b, non-THIN, (misfire-rate) ~.55; NO-SHORTCUT ~.30 | **NO-SHORTCUT (misfire-rate)** | **MISS at the verdict level** |
| n ≈ 14 | n = 17 | hit (inside the gamma/homogeneous band 13.9–24.9) |
| X ∈ {0, 1}; non-reachable ≤ 1 fired item in 106,496 draws | **X = 4; 4 items, 5 fires** (143 `eesq`, 148 `cwee`, 154 `vfdd` ×2, 367 `ttwd`) | **MISS — the named disconfirmer X ≥ 3 FIRED** |
| 410m THIN (n ≤ 10, E ≈ 7), unreplicated | n = 9, THIN, p_low .186 | hit |
| item 123 fires again at 410m | 1 fire (seed 43, draw 62) | hit |
| hot items re-fire: 123 ≥ 2, 447 ≥ 1 | 123: 15, 447: 7 (also 283: 9, 320: 9) | hit |
| specificity MISFIRE-RATE, events ≫ 3, share ≈ .4, p > .05 | MISFIRE-RATE, 157 events, share .318, p .480 | hit (events above the 33–81 scenario — competitor rates were disclosed UNKNOWN; they are higher than the scenario assumed) |
| on (0,2) rotation items the higher-overlap competitor (`qbaa`-type) out-emits the reverse | 283 `qaba` 9 vs `qbaa` 2; 179 `aefe` 2 vs `afee` 1; 174 1 vs 0; 210 0 vs 1 | **MISS** — on the 2-slot items the reverse wins; the competitor mass sits on the (1,3) and (0,3) items instead (below) |
| DIRECTED with p < .01 (disconfirmer) | p .480 | did not fire |
| count-weighted: same direction, smaller p | T_c = 5 of 60, p_low .097 (vs .395) | hit, no rejection |
| S2: neighbours dominate the reverse > 3:1 on non-reachable new draws | 39 vs 5 (7.8:1); all-distinct committed 90 vs 3 | hit |
| persistence: ≥ 4 of the 1b fired items NEW | 11 of 17 new; never-fired reachable 7 of 24 fired (11 fires / 196,608) | hit |
| leak voids 0 | 0 | hit |
| gate 1 (1b) IDENTICAL, fires at (348, 20, 14), (430, 20, 43) | exactly | hit |
| no stops, zero attrition, change unspent | as stated | hit |
| mean draw length ≈ 3d's | 30.20 (1b) / 30.70 (410m) | not graded (3d's referent not pulled into this record) |

Ten hits, three misses, one disconfirmer fired. As in 3d: every hit is
mechanics or bookkeeping, every miss is the science — WHERE the fires
land.

## What the numbers say

**Reachability does not gate which items fire.** 4 of 13 non-reachable
items fired (31%) against 13 of 32 reachable (41%) — indistinguishable
at n = 17 (p_low .395). The five non-reachable fires are correct
reversals of strings whose reverse is NOT one copy-edit from the
input: `qsee→eesq`, `eewc→cwee`, `ddfv→vfdd` (twice, seeds 142 and
146), `dwtt→ttwd`; at 410m `ffre→erff`. The copy-misfire reading
predicted these would be near-silent; they are not.

**Reachable items fire at a higher per-draw RATE — but on four items.**
New 1b rates: reachable 55/262,144 = 2.1e-4, non-reachable 5/106,496 =
4.7e-5 (pooled ratio point .18, CP95 upper bound **.416** — the §6
headline). Forty of the 55 reachable fires sit on items 123 (15), 283
(9), 320 (9) and 447 (7). The count-weighted secondary, which that
concentration feeds, leans the shortcut way (p_low .097) and does not
reject; the primary was made item-level precisely so four hot items
could not manufacture a SHORTCUT, and the design call held. A partial
rate effect of this size sits inside the declared blind region — the
minimum detectable ratio at .75 power was .04 (gamma), and the
experiment was DECLARED UNDERPOWERED IN ADVANCE (freeze F-2 ruling);
NO-SHORTCUT reads "not detected at this resolution", exactly as
frozen. Whether the reachable rate premium is reachability or
item-level heterogeneity that happens to sit on reachable items, 3e
cannot say and does not.

**The entropy reading survives and sharpens.** Non-reachable repeat
items fire at 3.6e-5 pooled (1b) against the all-distinct len-4
committed rate of 7.9e-6 — ~4.5× at a 2× scramble prior — and they
fire with NO one-edit copy route. Low-entropy answers are cheaper to
emit whether or not a copy shortcut exists; 3e still cannot split
"easier to reverse" from "more probable a priori".

**The specificity arm's texture is the campaign's most informative
descriptive.** Among first-character-matched one-edit outputs the
reverse is one misfire among several (MISFIRE-RATE, share .32). Where
the competitor mass sits is legible: on the (1,3) rotation items the
dominant emission is "last character first, then copy forward" —
`cara→acar` 22 vs the reverse `arac` 1; `pmhm→mphm` 12 vs `mhmp` 0;
`zivi→iziv` 4 and `izvi` 10 vs `iviz` 0 — and on (0,3) mirror items it
is "swap the last two" — `izei→izie` 12 vs `iezi` 0; `dkmd→dkdm` 14 vs
`dmkd` 7. On the 2-slot (0,2) items the reverse wins (`qaba` 9 vs
`qbaa` 2). The sampled channel near these items looks like a
position-1-correct-then-garble channel in which the exact reverse is
neither privileged nor absent.

**What §6 NO-SHORTCUT licenses, as written in advance:** 3d's
STRUCTURED stands as a forecast result; the essay's three-signature
case for reversal at ≤ 1b is NOT demoted to the all-distinct residual
(that demotion was SHORTCUT's consequence and SHORTCUT did not
obtain); the "famous zero" paragraph gains the non-reachable fires as
direct evidence that the rare sampled successes are not all copy
errors that happen to be right. The headline number is the CP95 upper
bound .416 on the non-reachable/reachable rate ratio at 1b.

## Process notes

- The freeze's three findings were all live in the verdict path:
  F-1's exclusion rule had nothing to exclude (0 voids, as the census
  said); F-2's declaration is the lens the NO-SHORTCUT is read
  through; F-3's pins passed on real records.
- The frozen alternative's SHAPE was right this time (class-level),
  and the power table's E[n] bracketed the observed n; what the table
  could not price was a partial effect, and it said so.
- One reading to carry forward, not a lesson yet: when an item-level
  primary and a count-level secondary disagree in lean (here .395 vs
  .097), the disagreement itself is the finding — the effect, if any,
  lives in a few items.
