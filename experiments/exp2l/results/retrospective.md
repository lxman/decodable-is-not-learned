# Exp 2l retrospective — grading projection 9d3b39f4

The projection was sealed after `exp2l-endpoint-sealed`, before gate 1
or any intermediate 13B checkpoint was queried. Its own honesty note
governs the grading: 2k had already measured x_A^(256) at .1548 on the
KNOWN 7B outcome, so the verdict-level call was cheap; the foresight
is graded on the 13B-specific texture and the per-rung table.

## Verdict level — HIT (discounted per the honesty note)

BOTH projected; BOTH delivered. T_A = .1261 landed inside [.10, .19]
but below the .14 point — the transfer attenuation the projection
priced in ("minus a little for 5.0T-vs-4T timing and the endpoint
ceiling") was real and slightly larger than priced. T_B = .1814
landed inside [.11, .23], above the .16 point — the denser
conditioning bucket ate less of the lineage signal than projected.
The bar-placement claim held: .1261 sits ~3.7 block-SDs (.0070) above
the bar, and no 64-draw block's scatter reaches it — a bar miss would
indeed have been transfer attenuation, not sampler noise. Disconfirmer
A-i ([.05,.10) structured-but-below-bar) did NOT fire this time —
at 256 draws the cross-family forecast clears on a sealed outcome,
which is the exact claim 2i could not make and 2k could not seal.

## The named per-rung disconfirmer FIRED — by a hair

"antonym6 BELOW .10 while odd6 clears would invert 2h's option-rung
ordering": antonym6 came in at .0977, odd6 at .1038. Fired as
written, by .002 and .004 respectively — the two option rungs sit
statistically on top of each other (CIs [.026,.164] vs [.032,.173]),
so the honest reading is "the 2h option-rung ordering does not
reproduce at 13B," not a reversal. It goes in the miss column all the
same; the disconfirmer was written without a tolerance.

## Per-rung foresight — 4 hits, 4 misses, every miss informative

HITS: add_base8 top (~.42 projected, .459 delivered); sub3_mid above
the other two mid-digit rungs (.098 vs .013/-.002 — 2k's
130-live-item column carried exactly as projected); the mid-digit
band .05–.10 caught sub3_mid; S1's monotone shrinking-increment shape.

MISSES:
- **antonym NEGATIVE (-.066) for A** while projected ~.04 flat — and
  simultaneously +.256 for B. The sharpest new datum in the table:
  the two predictors DISAGREE IN SIGN on a rung for the first time.
  Pythia's antonym item-ordering anti-correlates with OLMo-2 13B's
  while OLMo-2 1B's correlates strongly — lexical/option rungs are
  where lineage identity lives, arithmetic rungs are where the shared
  component lives. (Consistent with 2j: the option rungs were the
  functionals' untouched residual.)
- sub_base8 .292 vs ~.42 projected (the "both base-8 rungs at .42"
  pairing broke; only add_base8 held).
- antonym6 .098 vs ~.20; odd6 .104 vs ~.17 — both option rungs came
  in at half the projected D for A.
- arith_next .139 vs ~.08 — projected thin from 2k's small gain,
  delivered mid-table.
  Pattern in the misses: the projection over-priced option rungs and
  under-priced arithmetic rungs for the cross-family predictor —
  same direction as the antonym sign split. One story covers all
  five: **the cross-family component is arithmetic-heavy; the
  option-rung structure is lineage-private.**

## Secondaries — S1–S6 all HIT, S7 mixed

- S1 ladder .0760 → .1005 → .1115 → .1261 monotone, increments
  shrinking (projected ".09 → .12 → .13 → T_A"; start lower). The
  four k=64 blocks (.0719–.0798, SD .0032) all MISS the bar — the
  density claim (2k) confirmed on a sealed outcome: at 64 draws
  there is no cross-family forecast of 13B; at 256 there is.
- S2 410m .1270 in [.12,.21] and ≥ 1b — third consecutive
  410m ≥ 1b on cross-family transfer. A real pattern now, not a
  quirk: the smaller Pythia's ordering transfers at least as well.
- S3 within-alone .2045 (~.19 projected), cross-beyond-within .0770
  (~.06 projected) — both in range.
- S4 matched-density increment +.0687 (projected +.04–.07, top edge).
  Density does not close the lineage gap at 13B either.
- S5 π T .1848 (projected .15–.20) — **2j's second mechanism survives
  its first sealed-outcome test**; the retirement clause (≤ .05) is
  dead. The answer prior alone forecasts a sealed emergence order.
- S6 step 0 = 0 items on all 34 rungs; main ≥ endpoint on 15/18
  R_13B rungs (projected ≥ 12/18).
- S7 collapse window: HIT and then some — the projection named the
  1k–8k log head as the candidate window from the preflight's
  all-'!' texture; step 1000 delivered "!"-collapse on ALL 500 items
  across the battery (156 collapse records, count outcome absorbing
  them as designed). Transient verification pervasive with real
  drops (antonym 353 → 175 across 16k → 32k). MISS inside S7: the
  reversal descriptive — projected positive raw D with repeat-class
  items earliest; delivered ~0 for A (.008), +.08 for B on
  reverse_string, exact 0.0/0.0 on rev_string7. No reversal forecast
  exists at either density; the reversal channel stays 3c/3e's
  story, not a forecastable one at this resolution.

## Tally

Verdict HIT (cheap), both T's in range (one low, one high), named
per-rung disconfirmer FIRED (hair-thin, tolerance lesson), per-rung
4/4+4 with one clean new phenomenon (the antonym sign split), S1–S6
six for six, S7 half. The projection's systematic error is one
sentence: it priced the cross-family transfer as uniform across rung
types, and it is not — arithmetic transfers, option-rung structure is
lineage-private.

## Process notes (Michael's call whether any earns the methods paper)

1. **A named disconfirmer without a tolerance fires on a .002 margin
   and then means less than it says.** 3e's bracket lesson one level
   down: brackets need widths, not just directions.
2. The three environment-side kills cost ~11 h wall time and zero
   bytes of evidence — the per-record watcher-commit design paid for
   itself three times; worth stating as the standing pattern for
   multi-day sweeps on a shared machine.
3. The projection's per-rung table should stratify by rung TYPE
   (arithmetic / option / string) rather than projecting each rung
   independently off the last outcome's table — the misses were all
   one type-level error appearing five times.
