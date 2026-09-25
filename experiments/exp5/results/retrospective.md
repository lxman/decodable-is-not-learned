# Experiment 5 — retrospective (written after `exp5-closed`, 2026-09-25)

The frozen analyzer ran once on Michael's word ("Run the analyzer then tag") at 08:17 UTC and delivered **NOT-MATCHED · MIXED** — T .0535 ≥ .01, rung-block p .00061 (13 blocks, enumerated; family-block .0156; cell-level 1e-4), 63 live cells on 13 rungs, modifier 24 positive / 24 negative (p 1.0), signed mean offset −.021 with CI95 [−.074, +.004], 21 pairs kept, largest ratio 72.98×, every gate clean, zero failures — read under DECLARED UNDERPOWERED IN ADVANCE (P .173 at the deciding arm; the realized live set 63 against the simulated 38). Tag `exp5-closed` at e0f63e90e. This file grades `projection.md` (sealed at ee4268008, before any sweep unit) against `results/VERDICT.txt` and `verdict.json`, then records what the campaign taught. Every number below that is not in the verdict record was computed AFTER the verdict from the committed cell table (`verdict.json["cells"]`), is descriptive, and is labelled so.

## The verdict cell — HIT

The projection called **NOT-MATCHED · MIXED at .40**, LARGE-AHEAD .32, NOT-MATCHED .80 in all. The analyzer's cell is NOT-MATCHED · MIXED. The call is a hit at the cell level, and the worlds it put nearest — LARGE-AHEAD — did not obtain: the modifier's sign count is exactly even (24 / 24), where the projection had ≈ 20 positive / ≈ 12 negative and a p of ≈ .11 (it read .11 as MIXED for the right reason and the wrong counts).

## The primary

| quantity | projected | realized | grade |
|---|---|---|---|
| pairs kept | 21 [20, 21] | 21 | HIT |
| largest realized ratio | ≈ 73× | 72.98× | HIT |
| live cells | ≈ 55 [40, 75] | 63 | HIT |
| rungs with a nonzero block sum | ≈ 10 [8, 12] | 13 | MISS above (odd6, median5, median7, odd_one_out, sub4_mid, count_div13 carry cells; the projection had 9 + 1–2) |
| T | ≈ .08 [.04, .16] | .0535 | HIT, at the low third |
| p (rung-block) | ≈ .003 [.0005, .03] | .00061 | HIT |
| modifier | MIXED (≈ 20 / 12) | MIXED (24 / 24) | cell HIT, counts MISS |
| signed mean offset | +.02 [−.04, +.08] | −.021 [−.074, +.004] | inside the range; the point's SIGN missed — the lean is small-ahead |
| gate 1(c) | PASS at .85 | PASS on 15/15 (Σ|Δ| ≤ 23, max ≤ 7) | HIT; the interior drift smaller than the finals' |
| INSUFFICIENT_DATA | .10 | did not obtain | HIT |

**T's low third, explained by the wobble edge the projection named:** P (the within-size discrepancy at the window) averages 12.4 items with SD 13.6 (S11's `P_distribution`), i.e. at the upper end of the 8–15 the projection assumed, and on antonym at early high-LR checkpoints the cells read UNSTABLE rather than L-AHEAD (below). The 2.8b row alone carries T above the bar; every other row sits at .02–.035.

## The designer's prior and its two disconfirmers — graded first, as promised

The claim: *most of the excess sits in two places — the 2.8b row (2.8b's final anomalously strong on the mid-digit and next-term rungs) and the antonym rungs in the 1b / 410m rows (the larger models clear antonym at loss ≈ 2.0–2.1 while the small finals never do).*

- **Disconfirmer 1 — T over live cells outside the 2.8b row and outside antonym / antonym6 ≥ .06:** realized **.0112** over 33 cells (10 blocks, flip p .084) — post-verdict, from the cell table. **Did not fire.** The excess is concentrated where the claim put it.
- **Disconfirmer 2 — the 2.8b row's mean c ≤ .04:** realized **.117** over 18 cells (2.8b→6.9b .110, 2.8b→12b .124). **Did not fire.** No larger model at loss 1.820 reaches the 2.8b final's sub3_mid 264 (6.9b reads 6 / 9 at [79000, 80000], a genuine crossing with residuals .0003 / .0018; 12b reads 0 / 9 at [59000, 60000]) or its sub_base8 92 (20 / 29 and 12 / 34).
- **But the second leg's MECHANISM was wrong.** The claim said the option rungs' contribution would be antonym L-AHEAD cells. Realized: **antonym has 11 live cells and NOT ONE is L-AHEAD or S-AHEAD** — 3 CONCORDANT, 6 UNSTABLE, 2 PLACEBO-ONLY. At loss 1.995 (the 1b row) the larger models read antonym 120–174 at t_lo and 120–193 at t_hi — hovering at the 125-item bar, clearing on one side of the bracket and not the other; at loss 2.129 (the 410m row) no antonym cell is live at all — the larger models do not clear it there. Antonym is not "cleared by size at equal loss"; it is cleared by LOSS, and at these losses it is at its threshold for every size. The option rungs' excess is instead **antonym6**: the 5 L-AHEAD cells of the whole ledger are all antonym6 (1b→2.8b, 1b→12b, 1.4b→2.8b, 1.4b→6.9b, 1.4b→12b: f 86 / 99 against 109–138 at the bracket), and — unprojected — **the 410m row's five antonym6 cells are all S-AHEAD**: the 410m final's 111 clears the 1/6 floor while every larger model at loss 2.129 reads 67–90. The same rung is large-ahead from the 1b and 1.4b finals and small-ahead from the 410m final. That is what MIXED means here, cell by cell.

## By row (S7)

| small side | projected mean c | realized | cells | grade |
|---|---|---|---|---|
| 2.8b | +.11 [+.05, +.20] | +.117 | 18 | HIT |
| 6.9b | +.02 [−.01, +.06] | +.020 | 11 | HIT |
| 1.4b | +.12 [+.04, +.25] | +.032 | 12 | MISS below — no antonym L-AHEAD, no count_div13 cells (the larger models at 1.4b's loss do not clear count_div13 either; its 4 at the 1.4b final has no live partner) |
| 1b | +.10 [+.02, +.25] | +.035 | 13 | inside, low — antonym UNSTABLE, not L-AHEAD |
| 410m | +.05 [0, +.12] | +.029 | 8 | HIT — carried by antonym6 S-AHEAD, not by antonym L-AHEAD |
| 160m | ≈ 0 [−.03, +.08] | −.025 | 1 | HIT |

The projection's crossing placements, from the loss table: 2.8b's and 1.4b's inside their ranges; 6.9b's (90k–91k at 12b; 79k–80k at 6.9b's own 2.8b crossing) below the projected anneal tail; 1b's and 410m's later than projected. Three of six 12b placements missed.

## By type (S5)

| type | projected T | realized | grade |
|---|---|---|---|
| arithmetic | +.08 [+.03, +.18], p ≈ .01 | +.067 over 31 cells / 9 rungs, p .0059 | HIT |
| option | +.09 [+.01, +.20], no p unless 5 rungs | +.040 over 32 cells / 4 rungs, no p | HIT, low |
| string | no T | no live cells | HIT |

## Secondaries

- **S1 ledger.** L-AHEAD 5 (all antonym6, above), S-AHEAD 13, CONCORDANT 20, UNSTABLE 13, PLACEBO-ONLY 12 (live only through a B member — a class the projection did not name), unstable fraction .206 (projected .20 [.10, .35]: HIT). S-AHEAD named right: sub3_mid × (2.8b, {6.9b, 12b}), sub_base8 × (2.8b, {6.9b, 12b}), add3_mid and add_base8 at (2.8b, 12b). Named wrong: arith_next at 2.8b is not S-AHEAD (2.8b's 135 against 6.9b's 79k–80k reads sits inside the UNSTABLE / CONCORDANT classes); count_div13 L-AHEAD at 1.4b does not exist; antonym L-AHEAD does not exist. Unprojected S-AHEAD: antonym6 × (410m, every partner), arith_next × (1b, 12b) (f 19 against 11 / 11), odd6 × (6.9b, 12b). **The essay's falsifier sentence, if written from this ledger, has both directions on one rung and no direction on the aggregate; §6's MIXED licence — "the discrepancy is real and has no direction the design can read; the excess and the ledger reported, no mechanism sentence" — is the one that applies.**
- **S2 overlay.** Antonym on one loss curve across sizes with the finals at their threshold — the projected shape; the mid-digit rungs separating by size with 2.8b above — the projected shape. Both descriptive.
- **S3 composition.** Mean absolute per-set gap .012–.029 nats per pair (projected ≈ .03 [.015, .07]: at and below the low edge); the largest gaps on EuroParl (.08–.16 — the larger model AHEAD there at equal aggregate loss), DM Mathematics, Github, NIH ExPorter. EuroParl and DM Mathematics were named; the direction ("ahead on code-like, behind on prose") only partly (EuroParl is prose). The Pile-CC disconfirmer did not fire.
- **S4 size ratio.** Spearman(c, log ratio) −.084 (projected −.05 [−.35, +.25]: HIT). The rows order the pairs, not the ratios.
- **S6 exposure.** Exposure ratios inside the projected bands for the 2.8b, 1.4b and 1b rows (2.8b→6.9b .55, 2.8b→12b .41; 1.4b→ .38 / .25 / .20; 1b→ .46 / .21 / .15 / .13); the 160m row .02–.04 (projected .01–.10). Spearman(c, log exposure) +.33 — the projection said "no monotone relation": MISS, mild; the 2.8b row has both the largest c and the largest exposure, which is the anomaly's signature, not exposure's.
- **S8.** 2g's and 2h's curves placed by the spine; 6.9b's count_div13 collapse at 40000 appears where projected.
- **S9.** Not run (Michael's ruling of 2026-09-25, disclosed in `PROGRESS.md`): the frozen loss forward converts to float64 on the device (`slice_5.py:269`), which MPS refuses — a path no test and no stage had executed on the Mac. The one-way drift stands measured by gates 1(b) and 1(c).
- **S10 texture.** Bracket widths all 1000 except (1.4b, 2.8b) at 5,000 — the projection named the exclusion band as the cause and put it at 2,000 in [63000, 65000]: mechanism HIT, magnitude and location MISS. Re-crossings on the spines: none (HIT). Loads 178 (projected ≈ 250 [200, 320]: MISS below — shared intervals reused units). 12b `step1000` finite (known). B-6: 12b's six 2g replication points within the scaled tolerance 6 / 6 (projected ≥ 5 / 6: HIT). **And the campaign's texture finding, unprojected — "loss monotone along everything loaded" MISSED: Pythia-12b `step59000` is a loss spike, 2.5618 between 57000's 1.8214 and 60000's 1.8157, with the counts collapsed (antonym 79 against 195–208 either side; the mid-digit rungs 0). The preregistered search — the first crossing spine interval, bisected to an adjacent straddling pair — found [59000, 60000] straddling ℓ_2.8b = 1.8202 because the spike's edge satisfies the rule (2.5618 ≥ 1.8202 > 1.8157; 58000 is excluded from 12b's list, so (57000, 59000) is the other adjacent pair and it does not straddle). The bracket is a spike edge, not the smooth crossing (which lies between 57000 and 60000 on the loss curve).** Post-verdict sensitivity from the cell table: excluding the (2.8b, 12b) pair's 9 cells, **T .0417, 13 blocks, p .00037** — the verdict is unchanged in world and modifier; the 2.8b row's excess is carried equally by its 6.9b partner at a genuine crossing. Two smaller rises elsewhere (12b 89000→90000 +.010 inside the (6.9b, 12b) window; 6.9b 77000→78000 and 80000→81000, +.002 / +.003) are wobble, not spikes. Two finals are WORSE than their `step142000`: 160m 2.4896 vs 2.4705 and 410m 2.1291 vs 2.1277.
- **S11 small-side stability — the projection's sharpest call MISSED, and its named disconfirmer fired.** 1.4b count_div13 at `step142000` reads **5** against the final's 4 (projected ≥ 40; the disconfirmer "≤ 15 — then 1.4b's anneal itself lost the rung" is what obtained). 2.8b sub3_mid at 142000 reads 189 against 264 (projected ≥ 200; miss by 11 — a third of the 264 arrives in the last 1000 steps). "|Δ| ≤ 10 on every rung at 410m / 1b / 2.8b / 6.9b" — MISS broadly: the anneal's last 1000 steps move rising rungs by 14–75 items (2.8b sub3_mid −75, arith_next +23, sub_base8 −21, antonym6 −14; 6.9b median7 −26, count_div13 −24, arith_next +23, odd_one_out +23; 1b antonym −17, hamming12 +17; 1.4b hamming12 +32, odd6 +19, antonym −17). **The small side's final is itself one noisy read**, and the design fixed f without noise (§4: "f fixed") — the within-size wobble the primary subtracts is measured on the large side only. A successor should read the small side at its own window too.
- **Budget.** ≈ 22 h [18, 30] projected; 32 h 27 min realized — MISS (the SXM4-benchmark-derived unit time against a PCIe host; the loss forward's real cost; bisection downloads unhidden). ≈ $32 [26, 42] projected; ≈ $40 realized — HIT.

## What stands, in §6's words

**NOT-MATCHED · MIXED, under UNDERPOWERED:** *the discrepancy is real and has no direction the design can read; the essay reports the excess and the performability ledger, no mechanism sentence.* The caveat in every world: one family, one battery of 34 synthetic tasks, sizes to 12b, loss matched on a 2M-token validation slice. Carried into the licensed sentence as disclosures: the (2.8b, 12b) bracket sits on a loss-spike edge and the verdict is unchanged without it; S9 was not run; the small side's final is one un-averaged read.

What the excess IS, descriptively: the 2.8b final's arithmetic profile is not reproduced by any larger model at its loss (in either direction of the ratio — 6.9b at 2.5×, 12b at 4.2×) or, by S11, quite by 2.8b itself 1000 steps earlier; and antonym6 is large-ahead from the 1b / 1.4b finals and small-ahead from the 410m final. Loss is not the whole currency on this battery, and the part it is not does not point one way.

## Process notes, for Michael's call

1. **Screen a rented GPU under sustained load before installing anything** (`run/thermal_screen_5.py`, 120 s of fp16 matmul with clocks and throttle flags) — the listing's reliability figure said nothing about a host throttled to 210 MHz.
2. **A puller's file set is a premise about the tree's shape** — test it against the runner's real layout before launch (the per-size search logs never landed until the first status check).
3. **A read-sweep tool's categories are a premise about which stage has landed** — after each seal, the seal's own set appears as "unpinned" unless the tool knows the seal.
4. **Time a WHOLE unit of the largest size on the campaign host in the preflight**, not one rung and the smallest unit — the budget's miss was exactly the number the preflight did not measure.
5. **Every device a design names for any stage — including a non-gating one — gets one real execution of the frozen model-contact path on that device before the tag** (S9 on MPS).
6. **A monotone-loss assumption inside a search needs a spike guard** — the bisection's straddle test is satisfied by a spike edge; the design should have printed each bracket's loss residuals against the neighbouring spine points and flagged a bracket whose t_lo loss exceeds the previous spine point's (here 2.56 against 1.907 at 32000). The analyzer's S10 monotonicity count saw it; the search did not.
7. **Noise on the small side too.** The primary fixes f; S11 shows the last 1000 steps of the anneal move rising rungs by up to 75 items. A successor reads the small final's own neighbours.

## Foresight, graded honestly

The verdict cell was called and obtained; T, p, the live-cell count, the pairs, the ratio, the 2.8b / 6.9b / 410m / 160m rows, both types, the unstable fraction, S4, gate 1(c), the B-6 descriptive and the dollar cost landed inside their ranges. The prior's two disconfirmers did not fire. The misses are the ones that matter for the science: the antonym L-AHEAD mechanism (wrong rung, wrong direction — antonym6, both ways), the 1.4b row (no count_div13 partner), the sharpest single call (1.4b count_div13 at 142000: 5, not ≥ 40 — the anneal lost it), the end-of-training wobble (|Δ| up to 75, not ≤ 10), the 12b spike, and the hours. The call survived because the 2.8b row carried it; the reasons the projection gave for the other rows were mostly wrong.
