# Experiment 5b — retrospective: the projection (fdeb2096d) graded against the verdict (exp5b-closed at 6b7dd013a)

Written 2026-09-27 after the analyzer's one run (13:36:56 → 13:50:16 UTC). The projection was sealed at tag `exp5b-preregistered` before any model load; every number below is the analyzer's, from `results/verdict.json` / `VERDICT.txt`, against the projection's stated points and tolerances. The two disconfirmers of the designer's prior are graded first.

## 1. The prior's two disconfirmers

**Disconfirmer (ii) FIRED on its T criterion.** The projection wrote: *"σ̂_s pooled ≤ 7 or T_sym ≥ .052 — the members sit on the finals and the anneal's last 1,000 steps were checkpoint-local, so M ≈ P/√2 and the excess GROWS under the correctly scaled statistic."* T_sym came in at **.0552**, above the .052 line; σ̂_s pooled 10.3 did not cross its 7 line. The mechanism named with the disconfirmer is what the record shows: **the small side's wobble is the smaller of the two** (Q mean 9.2 items, SD 6.8, against P's 12.4 / 13.6; σ̂_s 10.3 against σ_L 15.07), the matched placebo M averages 11.5 against P's 12.4, and c_sym exceeds Experiment 5's c on 36 of 63 cells. On the cells that carried the projection's cost — 2.8b sub3_mid — the 142000 read (189) was a dip between reads of 252 and 255 at 141000 and 140000, not the front of a monotone move; M there is 18–24 items, not the projected ≈ 50, and the two cells read .47 / .48 (Experiment 5's .51), not the projected ≈ .41.

**Disconfirmer (i) did not fire** (σ̂_s ≥ 20 or T_sym ≤ .030): the disclosure was NOT load-bearing, in the strongest form — S4 puts Experiment 5's own rule at realized α .0012 at the measured σ̂_s, below its nominal .01, with a null mean of −.0011. The "one un-averaged read" cost Experiment 5 nothing; the projection's S4 claim ("a factor of ≈ 1.5 on α") was right in direction (the disclosure was not worth the .44–.997 the higher grid points show) and wrong in size — the realized factor is 0.12, not 1.5.

**The prior's claim** — "subtracting the small side's wobble costs ≈ 5 of the 27 items, T_sym ≈ 22" — **MISSED**: the cost was −0.9 items; the symmetric window gave back a little of what Experiment 5's R − P over-subtracted (§2's √2 argument realized: at σ_s below σ_L/√2 ≈ 10.7, R − P over-subtracts, and the measured σ̂_s of 10.3 sits just there).

## 2. The verdict, cell by cell

| projected | realized | grade |
|---|---|---|
| **SURVIVES · CALIBRATED at .78** (SURVIVES .80) | **SURVIVES · CALIBRATED** | **HIT** |
| INFLATED unreachable (α ≤ .007 on the sealed grid) | α realized .000; INFLATED not reached | HIT (a property of the record, not foresight) |
| INSUFFICIENT_DATA .08 (routes named: the count tolerance, a digest mismatch, a kill, a non-finite read) | none: gate 1 byte-identical on all twelve re-reads, zero halts, zero attrition | HIT |
| UNDETERMINED .00 (unreachable, F-4) | not reached | HIT |

## 3. The primary

| quantity | projected | realized | grade |
|---|---|---|---|
| T_sym | .044 [.030, .058] (22 items [15, 29]) | **.0552 (27.6 items)** | inside the range; **the point MISSED by +.011** (the direction the fired disconfirmer names) |
| rung-block p | ≈ .002 [.0003, .02] | .00085 | HIT |
| positive block sums | 10 [8, 12] of 13 | 12 of 13 (count_div13 the one negative block; sub4_mid and odd6 positive but tiny) | MISSED above by one |
| live cells / nonzero blocks | 63 / 13 [12, 13] | 63 / 13 | HIT |

By row (projected → realized): **2.8b +.095 [+.075, +.112] → .1177, ABOVE the range** (the sub3_mid dip story above; sub_base8's four reads 92 / 71 / 114 / 64 wobble by ±25 with no trend, so its M is 13 not the projected 16+); 6.9b +.010 [−.010, +.030] → .0170 HIT; 1.4b +.025 [0, +.050] → .0344 HIT; 1b +.030 [+.010, +.050] → .0391 HIT; 410m +.030 [+.010, +.050] → .0307 HIT; 160m +.010 [−.050, +.050] → .0087 HIT. **Five of six rows inside their ranges; the one miss is the row that carries the verdict, above.** The tolerance's own account of its edges ("if the members continue the 142000 moves monotonically … T_sym near .032; if they sit near the finals … near .055") named the realized end exactly — the members sit near the finals — and the point was placed in the middle.

## 4. The calibration sub-cell and σ̂_s

| quantity | projected | realized | grade |
|---|---|---|---|
| σ̂_s pooled | 13 [9, 20] | 10.3 | inside; point high by 2.7 |
| 2.8b | 20 [14, 30] | 16.3 | HIT |
| 6.9b | 12 [8, 18] | 7.3 | MISSED below |
| 1.4b | 11 [7, 16] | 7.2 | HIT (at the edge) |
| 1b | 10 [6, 15] | 5.5 | MISSED below |
| 410m | 5 [3, 10] | 5.3 | HIT |
| 160m | 8 [3, 15] | 11.2 | HIT |
| realized α at σ̂_s | ≈ .000 | .000 | HIT |
| T\* | ≈ .045 | .0561 | inside nothing (no range given); follows T_sym's miss |

Four of six per-side points inside; the two misses both BELOW — the projection over-estimated the small side's wobble on the two sides whose 142000 reads it had taken as the scale of all three members (6.9b's count_div13 −24 and arith_next +23; 1b's antonym −17). The 160m side, projected from one antonym cell, read 11.2 because its four reads on that rung are 60 / 68 / 66 / 76 — the anneal's odd end at 160m (its final 0.019 nats worse than 142000) shows in the counts too.

## 5. Modifier, types, rungs

Modifier: MIXED projected at .85 → **MIXED, HIT**; cells with R > M projected 40 [32, 48] → **50, MISSED above** (M below P leaves more cells with R > M than R > P's 48); the split 20/20 → 26/24 HIT; signed offset ≈ −.02 [−.06, +.02] → the analyzer prints Experiment 5's −.021 as the referent and the 5b split; consistent.

By type: arithmetic +.060 [+.035, +.090] → **.0633, HIT**, p ≈ .01 [.002, .06] → .0098 HIT; option +.028 [+.010, +.050] → **.0475, HIT** (at the top); the option type's rung count was projected 6 and is 4 in the analyzer's typing (median7 and odd_one_out fall elsewhere), so "no p" was right for the wrong reason. The type disconfirmer (either type ≤ +.01) did not fire.

Per rung (projected mean c_sym → realized): sub3_mid +.27 [+.20, +.34] → **+.317 HIT**; sub_base8 +.08 [+.05, +.11] → +.082 HIT; add3_mid +.04 [+.02, +.06] → +.043 HIT; antonym +.04 [+.02, +.07] → +.076, **MISSED above** (M 20.3 against P 28.5 on the antonym cells — the large side's antonym wobble, not the small side's, is where R − P over-subtracted most); odd_one_out +.04 [+.01, +.06] → +.060 HIT; arith_next +.03 [+.01, +.05] → +.034 HIT; antonym6 +.03 [+.015, +.045] → +.041 HIT; median5 +.02 [0, +.05] → +.043 HIT; add_base8 +.015 [−.01, +.04] → +.022 HIT; median7 +.01 [−.02, +.04] → +.027 HIT; sub4_mid 0 [−.01, +.01] → +.003 HIT; odd6 −.01 [−.04, +.01] → +.0025 HIT; count_div13 −.03 [−.05, −.01] → −.038 HIT. **Twelve of thirteen rungs inside their ranges**; the miss (antonym) is above and on the option side, where P is large and Q small.

## 6. Secondaries

- **S1** outside the 2.8b row: T ≈ .024 [.010, .040] → **.0303 HIT**; p ≈ .05 [.005, .30] → .028 HIT. The licence quotes 15.1 items (projected ≈ 12).
- **S2** target swap: f_B .053 [.050, .056] → .0535 HIT (the same bytes); n₁₄₂₀₀₀ ≈ .048 [.040, .056] → .0525 HIT; range width ≈ .010 [.005, .020] → .0082 HIT; **the range's floor ≈ .040 [.032, .048] → .0492, MISSED above** (no target read pulls T under .049); designation width ≈ .010 [.004, .020] → .0089 HIT. Loss mismatch: the four larger sides +.0003 to +.0012 (projected +.0004 to +.003, HIT — the growth with distance from the final holds for 2.8b and 1.4b only; 6.9b's and 1b's are non-monotone); 410m −.0005 to −.0014 (projected −.0014 to −.003; HIT in sign, small); 160m −.019 / −.016 at 142000 / 141000 and **+.0036 at 140000** (projected −.02 to −.04 throughout — MISSED on the third member: 160m's loss dips for two checkpoints and returns).
- **S3** Q mean ≈ 14 [9, 22] → **9.2, HIT at the edge**; Q's SD ≈ 16 [10, 25] → **6.8, MISSED below** (no cell has a Q near 75: the 142000 dip on sub3_mid averaged with two near-final members gives Q 30, not 75); "the small side's wobble comparable to the large side's" → it is smaller, by a quarter on the mean and by half on the SD.
- **S4** as in §1: α(Exp 5's rule at σ̂_s) ≈ .015 [.000, .030] → .0012 HIT; T\* .051 → .0546 HIT; the "factor 1.5" MISSED (0.12).
- **S6** fraction constant ≈ .85 [.70, .95] → .841 HIT; the 2.8b S-AHEAD cells stable 8/8 → 8/8 HIT; the L-AHEAD antonym6 cells stable ≥ 4/5 → 5/5 HIT; **the 410m antonym6 S-AHEAD cells: not projected, and unstable on all five** (111 / 103 / 104 / 95 crosses its bar twice — the texture the projection did not name); 1.4b count_div13 ≤ 30 at both members → 5 / 4 HIT (its disconfirmer, ≥ 40 at 140000, did not fire: the anneal lost the rung before its last 3,000 steps).
- **S8** T₁ ≈ .046 [.035, .056] → .0527 HIT; T_sym − T₁ ≈ −.002 [−.010, +.006] → **+.0025, HIT** (inside, the sign opposite the point).
- **S9** ≈ .035 [.022, .048] → .0427 HIT; p ≈ .001 [.0002, .010] → .0011 HIT.
- **S10** naive ≈ .052 [.043, .060] → .0567 HIT; conservative ≈ .040 [.030, .050] → .0471 HIT; the subtracted-sign placebo ≈ T_sym ± .008 → .0545 HIT; every p < .01 → all four HIT.
- **S11** the within-class drift claim: byte identity on ≥ 8 of 12 units → **12 of 12**; Σ|Δ| ≤ 15 per unit → **0 on every unit**; |Δℓ| ≤ 2e-5 → **0.0**; gate 1 PASS at .92 → PASS. HIT, and stronger than claimed — through a different kernel driver (565 + the CUDA 13.0 compat library vs 580 native): the same wheels give the same bytes.
- **S12** ≈ 3 [0, 10] → **0, HIT** (the 160m antonym6 shape the projection named — 99 at 142000 against a final of 77 — did not clear the bar).

Secondaries: 27 graded HIT, 5 MISSED (S2's floor, S2's 160m third member, S3's SD, S4's factor, S6's unnamed 410m instability).

## 7. What the projection got right and wrong, in one paragraph each

**Right:** the verdict cell, the INFLATED-unreachable reading of the record, every gate, p, five of six rows, twelve of thirteen rungs, both types, the modifier, twenty-seven secondaries, and the S11 drift claim in its strongest form. The instrument did what the design said it would: a calibrated symmetric statistic that neither manufactures nor removes an excess under the null, read against a sealed grid.

**Wrong, and in one direction:** every miss on the small side's wobble is the same miss — the projection took each side's printed 142000-vs-final difference as the scale of all three members, and on the sides where that difference was one large move (2.8b sub3_mid −75; 6.9b count_div13 −24; 1b antonym −17) the other two members sat near the final. The 142000 checkpoint is, on those rungs, a dip, not the front of a trend; so σ̂_s came in low on 6.9b and 1b, Q's SD came in at half the projection, the 2.8b row and antonym came in above their ranges, and T_sym landed above the point at the edge the tolerance's own prose had named. The prior's claim missed in size and sign because its mechanism ("subtracting a wobble of the large side's order costs a fifth of the excess") assumed the small side's wobble was as large as the large side's; it is smaller, and the correctly scaled statistic returns what R − P over-subtracted.

## 8. Process notes (for Michael's call)

1. **Project a three-member window from its members' likely shape, not from one member's displacement.** The one committed member was, on the rungs that mattered, an outlier among three; a projection that had asked "dip or trend?" per rung and put probability on both would have bracketed the 2.8b row. The retrospective's rule: when one read of a window is known, project the window's SD from a mixture over "the known read is typical" and "the known read is the extreme", not from the known read alone.
2. **A calibration grid whose α never reaches the INFLATED line makes that sub-cell unreachable on the record; say so in the projection, as this one did, and in the design's §4 at the power stage** — the sub-cell's probability is a property of the sealed record, not a forecast, and the licence table should mark it as such before the campaign.
3. **The forward-compatibility driver arrangement reproduced Experiment 5's reads byte for byte** (twelve of twelve units, zero count diffs, zero loss difference) on a host whose kernel driver is a generation older: on this stack the wheels, not the driver, fix the arithmetic. The host-record line `nvidia_smi` should carry the compat library's version beside the kernel driver's when one is used (this campaign's does not; the ledger does).
4. **Idle box time cost more than the campaign** ($9.89 against a $4–6 projection: ≈ 4.6 h waiting for the launch word after the preflight and ≈ 2 h after the campaign for the destroy word). Where a stage boundary needs a word, the design's budget should carry the wait, or the process tail should authorise "destroy when the tree verifies" in advance.

One pre-committed change UNSPENT; zero experiment-side stops; zero attrition; model contact = the 24 units and the scratch-only preflight, nothing else.
