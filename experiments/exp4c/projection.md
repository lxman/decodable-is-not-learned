# Experiment 4c — projection (sealed after the tag, before any model contact)

Written 2026-09-20 at tag `exp4c-preregistered` (60a7492bb), before the preflight. Dial (m): by family and by type, tolerances both ways, every licence cell the analyzer distinguishes named and one called. Anchored on the frozen record — the pins in `battery_4c.py`/`rank_4c.py` and `results/power_4c.json` — not on any retrospective's prose.

## What the designer knows, declared first

The designer computed, on the four KNOWN runs, the discovery set the design §2 discloses: U .6224 over 42 cells (family-block p .0391); per run .487 / .630 / .694 / .646; arithmetic cells ranked among arithmetic flat tasks .5103 over 26 (p .45); non-arithmetic cells against the whole pool .7595 over 16; family sums of (q − ½): antonym +1.40, odd_one_out +1.43, reversal +1.32, seq_extrap +1.20, order_stat +.19, mid_digit −.27, base_repr −.25, base_arith −.38 (clock +.50 is not a 4c family; counting is a 4c family that carried no discovery cell). From those, arithmetic cells against the WHOLE pool read ≈ .54 by subtraction. Every number below is a belief formed on that set; nothing on the new runs has been read — every a_r(t) on Pythia 6.9b and OLMo-2 13B is sealed. The tag-bound power record says what this instrument can see: P(p₊ < .01 | the discovery shape) = .066, P(p₊ < .05) = .269, realized α .0085 / .0508, minimum detectable uniform lead .743. The projection is therefore a projection of a NOT-REPLICATED modal world around a real, type-bound signal — the design's own §4 sentence.

## The primary

Cells: 26 (8 on 6.9b, 18 on 13B), 17 arithmetic, 9 non-arithmetic, 9 families.

- **U ≈ .61, tolerance [.50, .72].** Construction: 17 arithmetic cells at ≈ .54 against the whole pool, 9 non-arithmetic at ≈ .74 → (17 × .54 + 9 × .74) / 26 = .61; the null SD of U over 26 cells is ≈ .06 (a uniform q has SD .289; family clustering widens it), so ± .10 covers the scatter and the shape uncertainty.
- **p₊ (family block, 512 flips):** with U ≈ .61 over nine families of unequal weight, ≈ .10, range [.02, .35]. Rung-level p lower (≈ .04); placebo p ≈ .06.
- **Disconfirmers, both directions:** U ≥ .72 — the lead is uniform and large, the discovery shape wrong toward a general effect (the record puts P(p₊ < .01) ≈ .78 at a uniform .75); U ≤ .50 — the four known runs' signal was theirs, not the instrument's; U_arith ≥ .62 — the type-bound reading wrong; U_nonarith ≤ .55 — the option/string signal absent where the discovery set placed it.

## Worlds and licence cells (every cell the analyzer distinguishes; one called)

Conditional on a verdict (see INSUFFICIENT_DATA below):

| cell | probability |
|---|---|
| **NOT-REPLICATED · TYPE-BOUND · not bounded · not reversed — THE CALL** | .55 |
| NOT-REPLICATED · NEITHER · not bounded | .10 |
| NOT-REPLICATED · TYPE-GENERAL · not bounded | .04 |
| NOT-REPLICATED · REVERSED (p₋ < .05), any modifier | .02 |
| MARGINAL · TYPE-BOUND · not bounded | .14 |
| MARGINAL · other modifier / bounded | .05 |
| REPLICATES · TYPE-BOUND | .05 |
| REPLICATES · TYPE-GENERAL or NEITHER | .02 |
| any world · BOUNDED (α_placebo > 2 × the deciding bar) | .03 (folded into the rows above) |

The world by p₊ alone: NOT-REPLICATED .71, MARGINAL .19, REPLICATES .07, REVERSED sub-cell .02 — the record's own .73 / .20 / .07 at the discovery shape, nudged for the belief that the real dependence among the flat tasks (§3.6) makes α_placebo(.05) land ≈ .05–.07, not enough to bound.

**INSUFFICIENT_DATA before any of the above: .10.** The named routes: gate 1 on 6.9b is a cross-WRITER byte comparison against Exp 4's ladder table collected 2026-09-13 on the same stack — a torch/transformers/numpy drift since then would fail byte identity honestly (F-3 shows digest and pins equal today; the collected bytes are the sealed question); a 13B load halting on a digest or memory event; an environment kill leaving a tree the analyzer refuses. None of these is a verdict.

## By type

| stratum | cells | projected mean q | tolerance |
|---|---|---|---|
| arithmetic vs the WHOLE pool | 17 | .54 | [.44, .64] |
| arithmetic vs ARITHMETIC flat (U_arith, the modifier's input) | 17 | .51 | [.41, .61]; p₊ over 64 flips ≈ .40 |
| non-arithmetic vs the whole pool (U_nonarith) | 9 | .72 | [.58, .86]; no family p (3 families); rung p ≈ .10; placebo p ≈ .08 |

Modifier: TYPE-BOUND .75, NEITHER .15, TYPE-GENERAL .10.

## By family (mean q; per-family tolerance ± .20 — one to five cells each)

| family | cells (run: task@clear index) | projected | discovery sign |
|---|---|---|---|
| antonym | 6.9b antonym@6, antonym6@6; 13B antonym@4, antonym6@4 | .75 | + |
| odd_one_out | 6.9b odd6@6; 13B odd6@5, odd_one_out@6 | .74 | + |
| reversal | 13B reverse_string@4, rev_string7@11 | .70 | + |
| seq_extrap | 6.9b arith_next@5; 13B arith_next@4, quad_next@7 | .66 | + |
| order_stat | 13B median5@6, median7@6 | .55 | + (weak) |
| counting | 6.9b count_div13@21; 13B count_div13@15 | .55 | (no discovery cell) — the widest uncertainty: late clears, long windows |
| base_repr | 13B oct2dec@6 | .45 | − |
| mid_digit | 6.9b add3_mid@13; 13B add3_mid@6, sub3_mid@5, add4_mid@6, sub4_mid@6 | .45 | − |
| base_arith | 6.9b sub_base8@11, add_base8@13; 13B add_base8@4, sub_base8@4 | .45 | − |

S2's sign ledger (eight shared families): 6 of 8 signs agree with the discovery set (binomial tail ≈ .14); the two most likely to flip are order_stat and base_arith.

## By run (S1)

- **Pythia 6.9b, 8 cells (3 non-arithmetic), 6 families (64 flips):** U ≈ .58, tolerance [.42, .74]; p₊ ≈ .25. The thinnest reading; a NOT-REPLICATED on its own.
- **OLMo-2 13B, 18 cells (6 non-arithmetic), 9 families:** U ≈ .62, tolerance [.50, .74]; p₊ ≈ .12. The run that carries whatever fires — like OLMo-2 7B carried Exp 4's.

## Secondaries (a statistic projected prints that statistic)

- **S3 window mean:** U_window ≈ .59 (the early indices dilute), same world with probability .85.
- **S4 continuity (Exp 4's φ / T through the frozen code; 4b's p_cal, T*, α_placebo, per-run nulls):** eligibility ≈ 60 % of the 26 cells (x_end ≥ 2 SE); T ≈ .5, tolerance [.2, .8] (the ratio's tails, 4b's lesson); λ̂ 5–8 per run; 4b's p_cal ≈ .3, T* ≈ +.1 with an interval covering zero; per-run nulls: 13B's flat-rung null mean ≈ .6–.8 (its 7B sibling's was .84), 6.9b's ≈ .5–.7 — the continuity arm reads NOT-DISTINGUISHABLE, as 4b did.
- **S5 within-riser timing:** U_within ≈ .55, tolerance [.40, .70]; ≤ 14 cells with a comparator; thin as the design says.
- **S6 six runs pooled:** U ≈ .617 over 68 cells (42 at .6224 + 26 at ≈ .61), the split printed, the known-input caveat verbatim.
- **S7 never-performing non-arithmetic vs arithmetic flat over the grid:** mean ≈ .45, tolerance [.30, .60] (discovery .42); 8 task-runs (5 on 6.9b, 3 on 13B).
- **S8 levels, site 0 excluded:** real step 0 ≈ .05–.10 (near the .02 chance floor plus the surface term); endpoints ≈ .25–.40; the references' pairwise ceiling ≈ .35–.45 (4b's site-0-excluded pair means .34–.42); per-reference a_r within .05 of each other.
- **S9 question-end:** U_qe ≈ .58, tolerance [.44, .72], the same direction, weaker.
- **S10 the flat pool's texture:** λ̂ 5–8; lag-1 autocorrelation of the flat increments: 13B ≈ 0 (a random walk like its 7B sibling, 4b's S5 −.02), 6.9b ≈ −.3 (mean-reverting like Pythia 2.8b).
- **Gate 0:** step 0 below the endpoint on ≥ .95 of cells, both runs. **Gate 1:** byte-identical on 34/34 (probability .90; the complement is the INSUFFICIENT route above). **Gate 7:** zero exact ties.
- **Stack consistency:** one stack block per run.

## What would make this projection wrong in a way that matters

A REPLICATES with TYPE-GENERAL (U_arith ≥ .62 and its p₊ < .05) would say the lead is not the option/string tasks' — the discovery set's type split was the four runs' accident. A REVERSED would say the rising tasks' pre-clear agreement sits BELOW the flat pool's — the construction account's shape, one experiment after 4b failed to distinguish it. Either is graded a projection MISS at the verdict level in the retrospective.
