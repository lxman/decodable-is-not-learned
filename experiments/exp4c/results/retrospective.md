# Exp 4c retrospective — grading projection 25361b9ef

Written 2026-09-22 after the single analyzer run (09:18:49 EDT on `6ada124cf`; record `git_sha 64a71e30e`; tag `exp4c-closed` at `cc751b449`). The projection was sealed 2026-09-20 at the original tag (`60a7492bb`), before the preflight, and stands unchanged through the bf16 amendment (re-tag `0a6c5ea83`), the host change (ruling 3) and the transport relaunch (ruling 4): none touched a statistic, a cell, a grid, a pin on the outcome or a power input. Every grade below reads the projection's own numbers against `results/VERDICT.txt` / `verdict.json`. The known-outcome caveat applies to every line: this is a preregistered reading on a known outcome, not a forecast.

## Verdict level — the WORLD hit; the CELL, U, p and the MODIFIER missed; the named disconfirmer fired

| quantity | projected | realized | grade |
|---|---|---|---|
| world by p₊ | NOT-REPLICATED .71 | NOT-REPLICATED (p₊ .7324) | **HIT** |
| licence cell (the call) | NOT-REPLICATED · TYPE-BOUND · not bounded · not reversed, .55 | NOT-REPLICATED · **NEITHER** · not bounded · not reversed (the .10 row) | **MISS** |
| U | .61, tolerance [.50, .72] | **.4500**, CI95 [.3296, .6094] | **MISS below the range** |
| p₊ (family block, 512 flips) | ≈ .10, range [.02, .35] | .7324 (p₋ .2715) | MISS |
| rung-level p₊ | ≈ .04 | .8122 | MISS |
| placebo p | ≈ .06 | .8451 (null mean .5176, sd .0671) | MISS |
| INSUFFICIENT_DATA | .10 | did not occur; gate 1 byte-identical on both runs | HIT |

**The named disconfirmer fired:** "U ≤ .50 — the four known runs' signal was theirs, not the instrument's." U is .45, the CI's upper end .61 just brushes the projected point. The second disconfirmer in the same direction also fired: "U_nonarith ≤ .55 — the option/string signal absent where the discovery set placed it" (realized .4435). The two disconfirmers in the other direction (U ≥ .72; U_arith ≥ .62) did not.

## The modifier — MISSED; by type 2 of 3

| stratum | projected | realized | grade |
|---|---|---|---|
| arithmetic vs the WHOLE pool | .54 [.44, .64] | .4534 (17 cells) | HIT, at the low edge |
| arithmetic vs ARITHMETIC flat (U_arith) | .51 [.41, .61], p₊ ≈ .40 | .4198, p₊ .7812 (6 families, 64 flips) | HIT on U, at the low edge; p above |
| non-arithmetic vs the whole pool (U_nonarith) | .72 [.58, .86] | **.4435** (no family p printable — 3 families, 8 flips; rung p .83; placebo p .72) | **MISS below** |
| modifier | TYPE-BOUND .75 / NEITHER .15 / TYPE-GENERAL .10 | NEITHER | MISS |

The type split the discovery set showed (arithmetic ≈ .51, non-arithmetic ≈ .76) did not carry to the sealed runs: both strata sit below one-half. The arithmetic projections hit only because they were projected near the null to begin with.

## Calibration — HIT

α_placebo at the .05 bar was projected ≈ .05–.07, "not enough to bound"; realized **.0763**, `bounded = False` (α at .01: .0178). The projection's sentence on the flat tasks' real dependence held: the rule is slightly anti-conservative at the bar, not enough to change a world. (Contrast Exp 4's LEADS rule on these same runs, S4 below.)

## By family — 4 of 9 inside ± .20; the sign ledger MISSED (4 of 8, projected 6 of 8)

| family | cells | projected | realized mean q | grade | discovery sign → realized |
|---|---|---|---|---|---|
| antonym | 4 | .75 | .492 | MISS (−.26) | + → − (sum −.03, at zero) |
| odd_one_out | 3 | .74 | .408 | MISS (−.33) | + → − |
| reversal | 2 | .70 | .400 | MISS (−.30) | + → − |
| seq_extrap | 3 | .66 | **.956** | MISS (+.30, the one family ABOVE) | + → + |
| order_stat | 2 | .55 | .133 | MISS (−.42, the largest) | + → − |
| counting | 2 | .55 | .529 | HIT | (none) → + |
| base_repr | 1 | .45 | .400 | HIT | − → − |
| mid_digit | 5 | .45 | .283 | HIT (−.17) | − → − |
| base_arith | 4 | .45 | .425 | HIT | − → − |

The projection named order_stat and base_arith as the two signs most likely to flip; order_stat flipped, base_arith held. What actually flipped were the three families that carried the discovery set's lead — antonym, odd_one_out, reversal — every one to the wrong side of one-half. The families the discovery set had negative stayed negative. seq_extrap is the exception in the other direction: `arith_next` and `quad_next` rank at or near the top of the flat pool on both runs (q .93 / .93 / 1.00) — a family whose pre-clear alignment growth genuinely outruns the never-performing tasks, on both families of model.

## By run — the split the pooled number hides

| run | cells | projected U | realized U | p₊ / p₋ | grade |
|---|---|---|---|---|---|
| Pythia 6.9b | 8 (6 families, 64 flips) | .58 [.42, .74], p₊ ≈ .25, "a NOT-REPLICATED on its own" | **.7292**, CI [.5938, .8819] | p₊ **.0312** / .9844 | U HIT (near the top); p MISS — on its own the run clears .05 |
| OLMo-2 13B | 18 (9 families) | .62 [.50, .74], p₊ ≈ .12, "the run that carries whatever fires" | **.3259**, CI [.2105, .5042] | p₊ .9551 / p₋ **.0488** | U MISS below; the run sits BELOW one-half |

The two sealed runs disagree in sign. The 6.9b's rising tasks rank in the upper third of its flat pool (.73); the 13B's rank in the lower third (.33). The pooled U of .45 is their cell-weighted average, and the family-block null over nine families cannot tell "no lead" from "opposite leads on the two runs". Both per-run readings are S1 secondaries with no α claim; the 13B's p₋ of .0488 is the closest thing in the record to the REVERSED sub-cell (projected at .02 for the primary; the primary's own p₋ is .27), and the licence does not let it be named as such. What the record does license: the 13B — 18 of the 26 cells, the run the projection said would "carry whatever fires" — carried the opposite. Read with 4b: the two OLMo-2 runs (7B in Exp 4/4b, 13B here) share a high flat-rung null (.835 / .836) and no detectable lead over it; the two Pythia runs disagree with each other (2.8b at .18 in Exp 4, 6.9b at .73 here).

## Secondaries — 14 hits, 12 misses, on the projection's own tolerances

| item | projected | realized | grade |
|---|---|---|---|
| S3 window mean U | ≈ .59, same world .85 | .5053 (p₊ .48) | point MISS; world HIT |
| S4 eligibility | ≈ 60 % of 26 | 11 of 26 (42 %) | MISS |
| S4 T (Exp 4's φ on the new runs) | ≈ .5 [.2, .8] | .6307 (p₊ .042 over 11 cells) | HIT |
| S4 T per run | (not projected) | 6.9b **1.1761** (p .0156, 6 cells); 13B **−.0237** (p .56, 5 cells) | — the same split as S1 |
| S4 λ̂ | 5–8 per run | 5.99 (6.9b) / 6.11 (13B) | HIT |
| S4 4b's p_cal | ≈ .3; "NOT-DISTINGUISHABLE" | .5518 (null mean .6446, sd .2483); T* −.0138 | point MISS; world HIT |
| S4 per-run null means | 13B ≈ .6–.8; 6.9b ≈ .5–.7 | 13B .8356 (sd .249); 6.9b .4854 (sd .406) | MISS above / MISS below |
| S4 per-run p_cal | (not projected) | 13B 1.0 (T* −.86); 6.9b **.0071** (T* +.69) | — |
| S4 α_placebo of Exp 4's LEADS rule | (not projected; 4b's was .1171) | **.3164** | — the rule fires on one null battery in three here |
| S5 U_within | ≈ .55 [.40, .70]; ≤ 14 cells with comparators | .5117; 24 cells | U HIT; count MISS |
| S6 six runs pooled | ≈ .617 over 68; split printed | .5565 (discovery .6224 over 42, confirmation .4500 over 26); split printed | point MISS; split HIT |
| S7 never-performing non-arith vs arith flat | ≈ .45 [.30, .60] (discovery .42) | .2329 (8 task-runs) | MISS below |
| S8 step 0 (site 0 excluded) | ≈ .05–.10 | means .1452 (13B) / .1519 (6.9b); option tasks .24–.41 at step 0 | MISS above — the surface term is larger than projected |
| S8 endpoints | ≈ .25–.40 | .3361 / .3037 | HIT |
| S8 per-reference spread ≤ .05 | | 13B .324/.339/.345 (.021); 6.9b .313/.270/.328 (.058) | HIT / MISS by .008 |
| S9 question-end U | ≈ .58 [.44, .72], same direction weaker | .4356 (p₊ .79; modifier NEITHER) | MISS below; direction agrees with the primary (both below one-half) |
| S10 autocorr | 13B ≈ 0; 6.9b ≈ −.3 | 13B −.119 pooled (−.165 mean of rungs); 6.9b −.342 (−.285) | HIT / HIT |
| Gate 0 | ≥ .95 both | .9678 / .9840 | HIT |
| Gate 1 | byte-identical 34/34, probability .90 | 34/34 both runs, digest equal | HIT |
| Gate 7 | zero ties | 0 | HIT |
| Stack consistency | one block per run | consistent (one block per run; `2.12.1` on the Mac for 6.9b, `2.12.1+cu130` on the box for 13B) | HIT |

Two S4 lines deserve a sentence each. Exp 4's own statistic on the new runs (T .63, p .042 over 11 eligible cells) is carried entirely by the 6.9b (T 1.18, its own placebo p .007); the 13B contributes T −.02. And Exp 4's LEADS rule, calibrated at α .1171 on 4b's placebo batteries, fires on **.3164** of null batteries built from these two runs' flat pools — the rule's false-positive rate is a property of the run, not of the rule, and 4b's figure could not have been carried forward.

## Tally

Verdict level: world HIT; cell, U, p₊, rung p, placebo p MISS; disconfirmer FIRED. Modifier MISS; by type 2 of 3. Calibration HIT. By family 4 of 9; sign ledger MISS. By run: 6.9b U HIT / p MISS, 13B U MISS / p MISS. Secondaries 14 / 12. INSUFFICIENT_DATA modal HIT.

Every miss at the verdict level points the same way: the projection carried the four known runs' type-bound shape (option and string tasks leading) onto two runs that did not have it, and put the larger run on the side that "carries whatever fires" when it carried the reverse.

## What the result says

1. **On two training runs nobody had read, the sealed rank test finds the rising tasks' pre-clear alignment growth at the flat pool's median** (U .45, CI [.33, .61], p₊ .73), at a resolution that would have missed an effect of the discovery set's size three times in four (.066 at p < .01; declared before the tag). "Still a citation" stands; this is not evidence of absence.
2. **The discovery set's shape was the four known runs', not the instrument's.** The three families that carried the post hoc lead (antonym, odd_one_out, reversal; .75 / .74 / .70 on the known runs) sit at .49 / .41 / .40 on the sealed ones. The design's §2 said this was the live risk and the power record priced it; the retrospective records that it happened.
3. **The two sealed runs disagree in sign, and the pooled primary cannot say so.** Pythia 6.9b above one-half (.73, its own p .03 over 8 cells); OLMo-2 13B below (.33, p₋ .049 over 18 cells) — the same split under Exp 4's φ statistic (T 1.18 vs −.02) and under 4b's per-run placebo (p_cal .007 vs 1.0). Neither per-run number is licensed as a finding; together they say the next design needs a per-run naming rule or a heterogeneity test, because averaging opposite readings into a null is the one outcome the primary cannot distinguish from a true null.
4. **One family outruns the flat pool on both runs and both families of model:** seq_extrap (`arith_next`, `quad_next`; q .93 / .93 / 1.00). Descriptive, three cells, one family — but the only place in two experiments where a rising task's pre-clear representation demonstrably moves ahead of never-performing tasks on a sealed run.
5. **Exp 4's LEADS rule is run-calibrated, not rule-calibrated:** α .12 on 4b's placebos, .32 on these runs' — one more reason Exp 4's measurement stays demoted (4b's licence) and the convergence paragraph stays a citation.

## Licensed for the essay (design §6, NOT-REPLICATED · NEITHER)

"On two training runs no one had read, a sealed rank test did not detect the rising tasks' pre-clear alignment lead (U .45, CI [.33, .61]), at a resolution declared in advance to miss an effect of the size seen on the four known runs three times in four; the post hoc type split did not carry; the two runs disagree in sign, which the pooled test cannot resolve." Bounded to 2c's battery, two runs, the prompt-end position, Exp 4's references, a known outcome. Not licensed: a reversal; a per-run finding; any mechanism.

## Process notes (Michael's call)

1. **A preflight must size the per-unit peak, not the model's residency.** The frozen 13B unit holds a 10.4 GB fp32 activation bank (34 rungs × 307 MB) until it closes, on top of 27 GB of bf16 weights and the MPS pool's 33 GiB peak: ≈ 48 GB on a 51.5 GB machine. The two-rung preflight (peak 35.3 GB) could not show it; the design's "27 GB resident" was the weights. Two Mac attempts failed (compressor thrash; OOM under an allocator cap) and the trajectory moved to a rented A100 — a host change disclosed after the tag (rulings 3–4, ledgered). Rule: a design states the per-unit peak including every bank that scales with rung count × storage dtype, and the preflight collects enough rungs to reach it.
2. **Download transport is an environment knob with a 30× range.** The Hub's classic path throttled the rented host per IP to 11 MB/s; the xet path measured 237–355 MB/s on the same host. A Mac-side workaround (`HF_HUB_DISABLE_XET=1`, from a preflight hang) carried to the rented box cost ≈ 5 h and ≈ $5 before the boundary relaunch. Rule: measure both transports on the host before a multi-hundred-GB sweep; do not carry a workaround across hosts.
3. **A hand commit while the watcher has pending files strands a file permanently** (its `git add` fails on the index lock; its seen-list is append-only). One file of one unit was stranded and fixed by hand. Rule: no hand commit without a clean tree and no timeout on that wait; after every unit, the tracked-file count for the unit is checked (70 here). Corollary, for a remote host: pull complete units only (the unit's last-written file as the signal) and verify counts and contracts read-only before anything is committed by hand.
4. **Two runs that disagree in sign average to a null the primary cannot distinguish from a true null.** The projection carried the pooled U onto each run as if the runs were homogeneous — the four known runs were (.49–.69); these two are not (.33 vs .73). A per-run naming rule (4b had one) or a preregistered heterogeneity reading belongs beside any pooled primary over runs.
5. **A rule's calibration is a property of the runs it is calibrated on.** Exp 4's LEADS rule: α .12 on 4b's placebo batteries, .32 on these runs'. The projection quoted 4b's figure as if fixed. Rule: a carried-forward rule is re-calibrated on every new run's own placebo pool before its α is quoted.

## Environment-side record

6.9b on the Mac: 23 loads, 20 h 0 min, zero halts, zero kills (2026-09-20/21). 13B: Mac attempt 1 thrashed (14:01–14:49 EDT 09-21), attempt 2 OOM'd under `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.78` (14:49–14:51), both tree-clean; ruling 3 → Vast instance 51956148 (A100 80GB PCIe, Japan, $1.06/h all-in), repo by git bundle at `5ec95fa1b`, Python 3.11.16 venv with the Mac's pins, launched 15:37 EDT 09-21; thin endpoint = the CUDA rehearsal (digest == 2l's, finite, contract clean on the Mac); gate 1 PASS 17:47 (0 byte diffs — the first byte-identical reproduction on a CUDA host, the eighteenth consecutive on the program); ruling 4 → xet relaunch at the step-1000 boundary 20:57 (pid 11975); 18 units complete 08:38 EDT 09-22; every unit pulled to the Mac, 70/70 tracked, contracts clean; instance destroyed ≈ 09:05, final spend $20.23; one watcher miss (hand-fixed); GPU memory on the box plateaued at 57 GB; the three Mac mlx LaunchAgents restored 07:55 (a reservoir-curator MPS segfault at 04:00 that morning was unrelated to the experiment). The analyzer once, 4 min 20 s, zero referent failures, every pin active. One pre-committed change SPENT (the bf16 amendment, before the sweep); nothing else preregistered moved.
