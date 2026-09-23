# Experiment 5 — projection (sealed after `exp5-targets-sealed`, before any sweep unit)

Written 2026-09-23 at tag `exp5-targets-sealed` (91d0c3114; object 40b0ba37), after the seven finals, gates 1(a)/(b) and the power record, before the first spine unit loads. Design §7 stage 1: by pair row and by rung type, tolerances on every number in both directions, the disclosed knowledge of §2 in the first paragraph, and the designer's prior stated as a claim with its own disconfirmer (2m's process notes). Anchored on the frozen record — `battery_5.py`'s pins, `results/loss_table_5.json`, `results/power_5.json`, the seven finals' unit files — not on any retrospective's prose. Gate 5 checks this file's adding commit descends from the seal and that the file is unedited afterwards.

## What the designer knows, declared first

**Known before the tag (§2):** 2c's final-checkpoint argmax counts at 2.8b / 6.9b / 12b and 2d's at 410m / 1b (the Mac's reads); 2g's 21-point 2.8b and 2h's 22-point 6.9b trajectories at 10k-step spacing, per item — the outcome curves IN STEP, not in loss; the four design-session computations (flip rates .224 / .319 between adjacent 10k checkpoints; late |Δcount| 17 items; the count-grain envelope).

**Known since the seal (this host's reads, sealed today):** the seven finals' losses on the slice — 160m 2.48962, 410m 2.12913, 1b 1.99513, 1.4b 1.91883, 2.8b 1.82023, 6.9b 1.75215, 12b 1.70396 — and their 34-rung counts, including the two the program had never read: 160m clears nothing at its final; 1.4b clears antonym (158) and arith_next (38) and reads **count_div13 = 4** where every other size reads 58–103. Under 2d's bar the small-side clears are 410m 1 rung, 1b 1, 1.4b 2, 2.8b 7, 6.9b 9 (the 2.8b final: sub3_mid 264 and arith_next 135 — above every other size's final on both, 6.9b's 16 / 55 and 12b's 12 / 77). The power record: 38 simulated live cells over 9 rungs, DECLARED UNDERPOWERED IN ADVANCE (P .173 at the deciding arm, .657 at half noise), null T −.0078 ± .0020.

**Sealed and unknown:** every interior loss, so every crossing step, bracket and window; every interior count at 1.4b, 1b, 410m, 160m and at 12b outside 2g's six replication points; the within-size wobble P at 1000-step spacing anywhere.

**The designer's prior, stated as a claim with its own disconfirmer.** The claim: *at equal loss the profiles differ beyond the within-size wobble, and most of the excess sits in two places — the 2.8b row, where 2.8b's final is anomalously strong on the mid-digit and next-term rungs (no larger model's FINAL reaches its sub3_mid 264 or arith_next 135, so no larger model at the HIGHER loss 1.820 will), and the antonym rungs in the 1b and 410m rows, where the larger models clear antonym at loss ≈ 2.0–2.1 while the 1b and 410m finals never do.* Its disconfirmer: T computed over live cells EXCLUDING the 2.8b row and the antonym/antonym6 rungs ≥ .06 — then the excess is general, not two anomalies. Its second disconfirmer: the 2.8b row's mean c ≤ .04 — then a 6.9b or 12b at loss 1.82 does reach the 2.8b final's arithmetic counts, and Prediction 3 holds where the designer expected it to fail loudest.

## The primary

**Pairs kept: 21 [20, 21]; largest realized ratio ≈ 73× (12b / 160m).** `never_reaches` is impossible (the finals are monotone in size); `crosses_before_spine` needs a large model below ℓ_s at `step1000` — 12b reads 3.709 there against 160m's 2.490, so none. One pair may lose a window member to the list edge only on the B⁺ side of a final-adjacent crossing (the (6.9b, 12b) pair if 12b crosses 1.752 inside its last two available steps) — projected NOT to happen (the anneal's last 20 % of training drops 12b's loss well past 1.752 before 141000).

**Live cells: ≈ 55, tolerance [40, 75]** — the 38 simulated (small side clears) plus 15–35 live through the large side only (antonym / antonym6 at the 410m, 1b and 160m crossings; count_div13, odd6, median5 at the 1.4b and 2.8b crossings of 6.9b / 12b). Rungs with a nonzero block sum ≈ 10 [8, 12] (the nine simulated plus median5 and/or sub4_mid).

**T ≈ .08, tolerance [.04, .16]; p (rung-block flip) ≈ .003, range [.0005, .03].** Construction, row by row (c = (R − P) / 500; P projected at 8–15 items on live rungs at 1000-step spacing — about half the 10k-spacing wobble of 17 — and larger, 20–35 items, on antonym at high-LR early checkpoints):

| small side | pairs | live cells | mean c | what carries it |
|---|---|---|---|---|
| 2.8b | 2 | 14 [12, 16] | **+.11 [+.05, +.20]** | sub3_mid R ≈ 240 (c ≈ +.45) and arith_next R ≈ 70–110 in both pairs; sub_base8 +.08, add3_mid / add_base8 +.03; antonym ≈ 0 (275 against a 6.9b / 12b at 250–300); antonym6 +.02 |
| 6.9b | 1 | 9 [8, 11] | +.02 [−.01, +.06] | 12b late in its anneal (crossing ≈ 100k–135k) against 6.9b's final: antonym6 206 vs 141, sub_base8 83 vs 48; the rest within P |
| 1.4b | 3 | 11 [7, 16] | +.12 [+.04, +.25] | antonym R ≈ 100–270 (2.8b mid-training peaks near 2g's 435-ever); count_div13 R ≈ 60–90 against the final's 4, if the large side clears it; arith_next 0–+.12 |
| 1b | 4 | 9 [5, 14] | +.10 [+.02, +.25] | antonym L-AHEAD on the three largest partners (f 87, a ≈ 200–350); arith_next f 19 against a ≈ 20–80 |
| 410m | 5 | 8 [5, 13] | +.05 [0, +.12] | antonym6 f 111 against a ≈ 80–140 (within P mostly); antonym L-AHEAD on 2–3 partners |
| 160m | 6 | 1 [0, 4] | ≈ 0 [−.03, +.08] | the crossings sit at steps 2k–30k; the large side clears antonym there on at most 2 partners |

Weighted over ≈ 52 cells: ≈ .085. The null's mean is −.008 and its SD ≈ .002 on the simulated set; a T of .08 is forty null SDs out, so p is set by the block count, not by T's size: with eight to eleven positive block sums out of ten or eleven, p ≈ 2⁻⁹ … 2⁻⁸.

**The tolerance's lower edge is the wobble question.** If P at 1000-step spacing on un-annealed, high-LR checkpoints is 25–40 items on antonym and 15–25 on arithmetic (mid-training antonym swung by 200 items over 2.8b's training), the antonym cells' c collapses toward zero or below, the 410m / 1b / 160m rows read ≈ 0 and T falls to ≈ .04 carried by the 2.8b row alone — still NOT-MATCHED (sub3_mid's R of 240 survives any P), still p < .01 if six or more block sums stay positive.

**Modifier (read only under NOT-MATCHED):** among cells with R > P, positive signs (a − f > 0: antonym and antonym6 across the 1b / 410m / 1.4b rows, count_div13 in the 1.4b and 2.8b rows, the 6.9b row) ≈ 20 [12, 30]; negative (the 2.8b row's five arithmetic rungs in both pairs, antonym6 at 2.8b vs a 6.9b mid-training) ≈ 12 [8, 18]. A two-sided exact binomial at .05 on ≈ 32 with ≈ 20 positive has p ≈ .11 — **MIXED, with LARGE-AHEAD the close alternative** if the antonym cells are more numerous than the arithmetic ones by three or more. Signed mean offset (a − f) / 500 over live cells ≈ +.02 [−.04, +.08].

## Worlds and licence cells (every cell the analyzer distinguishes; one called)

| cell | probability |
|---|---|
| **NOT-MATCHED · MIXED — THE CALL** | .40 |
| NOT-MATCHED · LARGE-AHEAD | .32 |
| NOT-MATCHED · SMALL-AHEAD | .06 |
| NOT-MATCHED · THIN (< 8 cells with R > P) | .02 |
| MATCHED (read under UNDERPOWERED: "not distinguishable at this resolution") | .08 |
| UNDETERMINED (< 20 live cells with a defined P, or < 7 nonzero blocks) | .02 |
| INSUFFICIENT_DATA | .10 |

NOT-MATCHED in total .80. The INSUFFICIENT_DATA routes, named: gate 1(c) — a spine unit at 2.8b (1k, 2k, 4k, 8k, 16k, 32k, 100k) or 6.9b (those and 64k) against 2g's / 2h's Mac reads outside the tolerance (per rung 15, Σ 120); the finals' worst was 6.9b at 8 / 57, but a high-LR interior checkpoint sits nearer more ties on antonym and the option rungs, so one rung over 15 on one of fifteen checkpoints is the likeliest failure (≈ .06); a non-finite spine or bisection unit (12b's `step1000` and `step256` are finite; `step2000`–`step8000` unread; ≈ .01); a runner halt or box loss that leaves a torn tree the analyzer refuses (≈ .03). MATCHED's route is the wobble edge above. UNDETERMINED needs the antonym rows to contribute no live cells with a defined P, which the 2.8b and 6.9b rows alone prevent (23 cells, 7+ rungs).

**The power declaration governs the licence in every world:** MATCHED is "not distinguishable at this resolution"; NOT-MATCHED fires at α .01 regardless, and its licence (§6) is by modifier. The realized live set (printed beside the simulated 38) is projected at ≈ 55 — the power record simulated only the small-side-live cells, so the true resolution is somewhat better than the declaration, not worse.

## By rung type (S5)

| type | rungs carrying cells | projected T | tolerance | p (where ≥ 5 rungs) |
|---|---|---|---|---|
| option (antonym, antonym6, odd6, median5, odd_one_out) | 3–5 | +.09 | [+.01, +.20] | no p unless 5 rungs carry cells; if printed, ≈ .05 |
| arithmetic (add/sub base8, add3/sub3/sub4_mid, arith_next, count_div13, …) | 6–8 | +.08 | [+.03, +.18] | ≈ .01 [.002, .06] |
| string (reversal, caesar) | 0 | no T (no live cells) | — | — |

Option carries the sign-positive cells, arithmetic the sign-negative ones; both types positive in c because c is sign-blind. **Disconfirmer:** either type at ≤ +.01 — then the excess is confined to the other, and the "two anomalies" claim above has only one leg.

## By pair (S7)

Largest per-pair mean c: (2.8b, 6.9b) and (2.8b, 12b) at ≈ +.11 each [+.05, +.20]; then (1.4b, 2.8b) ≈ +.14 (2.8b mid-training's antonym peak against 1.4b's 158, count_div13 against 4) and (1b, 2.8b) ≈ +.12; the (410m, ·) pairs +.03 … +.08; (6.9b, 12b) +.02 [−.01, +.06]; the (160m, ·) pairs ≈ 0 with 0–1 live cells each. **The rows, not the ratios, order the pairs** (S4 below).

## Secondaries

- **S1 — the ledger.** L-AHEAD cells named: antonym × (1b, {2.8b, 6.9b, 12b}) and (410m, {6.9b, 12b}); count_div13 × (1.4b, {6.9b, 12b}) if the large side clears it there. S-AHEAD: sub3_mid × (2.8b, {6.9b, 12b}), arith_next × (2.8b, {6.9b, 12b}), sub_base8 and add3_mid × (2.8b, 6.9b). CONCORDANT: antonym and antonym6 × (2.8b, ·), (1.4b, ·) on antonym, the 6.9b row on most rungs. UNSTABLE fraction ≈ .20 [.10, .35] (the design-session flip rates .22 / .32 at 10k spacing, roughly halved at 1000). The essay's falsifier sentence, if written, names antonym in the 1b row: performable at loss 1.995 by a 2.8b at ≈ step 30k, never by 1b's final.
- **S2 — the overlay.** Antonym falls near ONE curve in loss across sizes with the 410m / 1b / 1.4b finals BELOW it (the annealed small finals under-read the curve); the mid-digit rungs SEPARATE by size, the 2.8b points sitting above every larger size's at equal loss (the 2.8b final an outlier at 1.820 on sub3_mid and arith_next). The design's most reusable artifact; no number projected beyond those two shapes.
- **S3 — composition.** Mean absolute per-set gap at the match ≈ .03 nats [.015, .07]; the three largest gaps on small subsets (DM Mathematics, EuroParl, Ubuntu IRC or Github) with the larger model AHEAD on the code-like sets and BEHIND on the prose sets at equal aggregate loss. Disconfirmer: a gap ≥ .07 on Pile-CC (the largest set) — then "equal loss" was not equal on the bulk of the slice.
- **S4 — size ratio.** Spearman(c, log ratio) ≈ −.05 [−.35, +.25]: no growth with the ratio; the 2.8b row (ratios 2.5× and 4.2×) carries the largest c and the 160m row (ratios 6–73×) the smallest.
- **S6 — exposure.** Tokens at t_lo against 300 B: the 2.8b row .35–.60 (6.9b) and .20–.40 (12b); the 1.4b row .35–.55 / .17–.28 / .12–.20; the 1b row .30–.50 / .17–.28 / .10–.15 / .07–.11; the 160m row .01–.10. Learning-rate ratio at t_lo .55–.97. c against exposure: no monotone relation projected (the 2.8b row's large c sits at mid exposure).
- **S8 — 2g / 2h on the loss axis.** 2.8b's 21-point curve and 6.9b's 22-point curve placed by the spine: monotone in loss on antonym; count_div13's step-40000 collapse at 6.9b appears as a single point far below its neighbours at loss ≈ 1.80–1.85.
- **S9 — cross-host drift.** Two window units (1b, 6.9b) re-run on the Mac: per rung |Δ| ≤ 10, Σ ≤ 80 on each — inside gate 1's tolerance; interior drift no larger than the finals'.
- **S10 — the search's texture.** Loss monotone along everything loaded on all seven sizes (no re-crossing on any spine; ≤ 1 re-crossing anywhere among ≈ 150 loaded interior units); bracket widths 1000 steps everywhere except one 2000-step bracket if the (1.4b, 2.8b) crossing falls in [63000, 65000] (2.8b's `step64000` is excluded); 12b `step1000` finite (known). Loads: ≈ 250 [200, 320].
- **S11 — small-side stability at `step142000`.** |Δ| ≤ 10 on every rung at 410m, 1b, 2.8b, 6.9b (the anneal's last 1000 steps); **2.8b sub3_mid ≥ 200 at 142000** (the 264 is a property of the annealed model, not of one checkpoint); **1.4b count_div13 ≥ 40 at 142000** (the final's 4 is a checkpoint-local collapse of 2h's kind) — the projection's sharpest single call; its disconfirmer: 1.4b count_div13 ≤ 15 at 142000 (then 1.4b's anneal itself lost the rung).
- **Gate 1(c):** PASS on all fifteen interior checkpoints at probability .85; the miss, if any, on antonym or antonym6 at a 2.8b checkpoint ≤ 16k.
- **The 12b descriptive (B-6):** the six 2g replication points at 11 rungs within the tolerance on ≥ 5 of 6.

## Budget

The sweep ≈ 250 loads: 12b ≈ 65 units at ≈ 10 min scoring + 5 min streaming (overlapped by the prefetcher) ≈ 12 h; 6.9b ≈ 60 at ≈ 5 min ≈ 5 h; 2.8b ≈ 50 at ≈ 3 min ≈ 2.5 h; the four small sizes ≈ 2 h — **≈ 22 h [18, 30]** on this host at $1.08/h plus ≈ $8 of bandwidth ≈ **$32 [$26, $42]**.

## Process

No number above was computed on sealed data. Every quantity that later grades this projection is produced by the analyzer once, on Michael's word, from the committed sweep; the grading goes in `results/retrospective.md` by cell, by primary, by modifier, per row, per type and per secondary, with the two disconfirmers of the designer's prior graded first.
