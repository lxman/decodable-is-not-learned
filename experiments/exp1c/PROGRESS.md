# Exp 1c — Ledger

Every ruling, in order, with the reason it was made and when relative to the
data. The point of this file is that "we decided X before we saw Y" is
checkable rather than asserted.

## 2026-08-14 — origin

Came out of a question about where to point the beam after 1b closed PASS,
not out of the 1b successor list. The survey that produced it: in four of
five closed experiments the finding came from the measurement apparatus
rather than the models (Exp 2's untrained control fired on the whole
battery; 2b's caught leaks in 13 of 25; 2c's ~0 untrained floors meant
correcting them moved ρ from .368 to .2005; 1b's twins fired raw S1 in 9 of
10 grokking cells).

**Correction made during that survey, before any design existed.** The claim
that "all ten grokking cells read at layer 0, trained and untrained" was
asserted twice and is **vacuous**: grokking has `n_layers=1` and collects
`token_indices=(-1,)`, so there is exactly one probe site. Layer 0 was not
selected; it was the only candidate. Grokking is excluded from 1c entirely.
The `lubana_above` half stands — 8 candidates, layers 1–3 chosen in 10 of
10, never layer 0, twins scattered at p ≈ 1.

**What the exclusion exposed** (descriptive, not verdict-touching): grokking's
S1 is Bonferroni-corrected across **1** candidate, lubana's across **8**, on
6.7× the validation rows against an 11× lower chance floor. Three compounding
advantages for firing, none of them properties of the model.

## 2026-08-14 — the object of study

Found while reading `run_lubana.py`: the S3 graph branch (lines 211–227)
trains a sub-critical density sweep at 0.25/0.45/0.65/0.85 p_c, 2 sizes × 5
seeds, 10,000 steps each, and keeps `sub_hist.eval_metric[-1]` — one scalar
per cell. `best_probe_accuracy` is called once in that file, at line 192, in
the *training-steps* branch. **The probe has never touched the sweep.** 40
trained cells, 1,800 checkpoints, terminal `step_0010000` present in all 40.

Ruled: this is the experiment, not the split-sweep proposed an hour earlier,
which it subsumes. The sweep is a dose-response axis through the exact region
the essay's carve-out is about, where 1b left only two endpoints.

## 2026-08-14 — rulings, in order

| # | ruling | by | before |
|---|---|---|---|
| a | Primary claim is the percolation sweep; the instrument is a Stage A gate, not the result | Michael | any design text |
| b | **Frozen prediction: layer-0 only — leakage, not structure** (i.e. FAIL) | Michael | any probe |
| c | Primary statistic: depth-margin slope, with per-cell classification as pre-committed robustness | Michael | analysis code |
| d | Per-cell classification thresholds on the **permutation null per site**, conjoined with the per-site floor correction | Michael | analysis code |

**On (d).** Both gates are required because 1b measured them load-bearing on
different rows: the floor correction demoted grokking/10M/seed104 (trained
.017333 against a twin of .017333) which the null had admitted; the null
blocked lubana_below/1M/seed100 at p = .847 where the margin was positive.

**Consequence of (d), found while implementing it.** At 1b's `n_perm=1000`,
Bonferroni across 8 sites makes the corrected p 8(k+1)/1001 — only a
zero-exceedance sweep passes, so the per-site test is binary with no
resolution. Not hypothetical: all ten of 1b's `lubana_above` fires report
`null_p = 0.007992007992007992`, exactly 8/1001, pinned to the quantization
floor. `n_perm` raised to 10,000. Cost restated honestly at the same time:
the null, not the observed fits, is the entire budget — 9,600,960 fits at a
measured 3.4–3.6 ms, ≈9–20 h. §8 had said 960, having omitted the null.

## 2026-08-14 — defect found in my own design, before freeze

The fixed-n = 400 subsample designs the power confound out of the primary
test, but it also holds the singleton pool constant — which made the frozen
prediction's *mechanism* ("L tracks the shrinking pool") unmeasurable inside
the design meant to test it. Added the natural-n diagnostic arm: margins
only, no null, 640 fits, `verdict_touching: False`. A FAIL can now confirm
the predicted mechanism rather than merely match its outcome, and
`FAIL (layer-0, mechanism unconfirmed)` is a distinct named result.

## 2026-08-14 — open items closed

| item | how |
|---|---|
| 3 — stratified subsample feasible | Measured. `lang_kwargs` depends on `scale` alone, so 4 densities × 5 seeds = **20 languages are all the languages**. Minimum per-class singleton count across all 20 is **exactly 40** — zero margin. The runner asserts the count rather than shrinking. |
| 4 — classification rule | Ruled (d) above. |
| 1 — analysis + fixtures | 83 fixtures, **20/20 mutants killed**. |
| 2 — runner | Torch-free decisions in `profile_lib.py`; orchestration in `run_profile.py`. |
| 5 — capability metric | Measured, no history reconstruction needed — every checkpoint stores its own `eval_metric`. All 40: mean **0.0976** vs chance **0.1000**, range 0.068–0.136, no density trend. **The conjunction is live.** |

## 2026-08-14 — what the mutation testing caught in me

One mutant survived the first run: a **per-site train/val split**, which
would make the eight accuracies incomparable and turn the mean-over-sites
margin into an average of eight different experiments. That is the exact
invariant I had talked myself out of testing properly while writing the
suite, on the reasoning that determinism covered it. It does not.

The first repair also missed it: at the fixture's signal strength the probe
scored exactly 1.000 under every split, so identical accuracies were
consistent with eight different partitions. The test now runs at a
separation where accuracy responds to the split (0.66–0.74 across six
splits). Recorded because a suite's own blind spot is invisible afterwards.

## 2026-08-14 — FROZEN

Tag `exp1c-preregistered`. Freeze checklist all GREEN or RULED
(`FREEZE_CHECKLIST.md`), three rulings disclosed: no campaign driver
(non-verdict-touching), seeds not disjoint from 1b (unavoidable — 1c trains
nothing and reads checkpoints that exist only at 100–104), Stage A steps
sourced from 1b's own `s1.checkpoint_id`.

**One pre-committed change: UNSPENT.**

## Next

1. Campaign driver (after the tag; not part of the frozen artifact).
2. Twins first — all 80 twin profiles, before any trained cell is read.
3. Stage A on 1b's 20 lubana cells; **finalise and ledger the power table
   against the measured sd before Stage B runs.**
4. Stage B, both arms. Commit per cell.
5. Ledger the verdict projection, then run the frozen analysis once.
