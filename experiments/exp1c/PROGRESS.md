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

## 2026-08-14 — TWINS PHASE COMPLETE (100/100, 0 failed, 40.6 min)

Run before any trained cell was read, per §8 step 2. 8 workers, BLAS pinned
to one thread each.

**Count correction.** The freeze report said "80 twin profiles". It is **100**:
20 Stage A (fixed) + 40 Stage B (fixed) + 40 Stage B (natural). The 80 figure
omitted the Stage A and natural-arm twins.

**Shape verified, not assumed.** All 100 are twins; all carry 8 sites; all 60
fixed-arm profiles have n_rows 400 / n_val 100 / per_class 40; all 40
natural-arm profiles carry no permutation null; capability_metric is None on
every one. Natural-arm pool sizes reproduce the design §2 table exactly:
865.6 / 773.4 / 659.2 / 536.0 at 0.25 / 0.45 / 0.65 / 0.85 p_c.

**THE CONTROL: 0 of 480 sites clear the Bonferroni bar on random weights.**
Against Exp 2, whose untrained control fired on 120 of 120 fits and ended the
experiment, and 2b, whose control caught leaks in 13 of 25 capabilities. The
per-site two-gate rule does not fire spuriously on this battery.

**Empirical floor.** Twin accuracy over all 480 sites: mean **0.1038**,
sd 0.0285, against a theoretical chance of 0.1000. A real bias of ~0.4
percentage points, small but in the same direction throughout — which is why
the margin is defined against each cell's own twin rather than against 1/K.
(An earlier partial read over 176 sites gave 0.1108 and overstated this; the
full set is 0.1038.)

**Provenance: 99 of 100 records carry `git_sha 1c4a7e7-dirty`.** Disclosed
rather than cleaned up. The only untracked path during the campaign was
`experiments/exp1c/results/` — the campaign's own output — and an empty diff
across every `.py` and `.md` confirms no code changed while it ran. The code
at every cell was exactly `1c4a7e7`. 1b avoided the suffix by committing per
cell, which a serial campaign permits and an 8-worker one does not; the
alternative would have been to serialize the run for a cosmetic sha.

**Timing, measured.** 178 s per fixed-arm 1M profile, ~400 s per 10M — the
wider model gives the probe larger features. The design's 9–20 h estimate was
single-threaded; at 8 workers the full 200-profile campaign is ~1.2 h.

## 2026-08-14 — STAGE A: PASS (20/20 cells, 0 failed, 28.7 min)

The confirmation gate, run on 1b's 20 lubana cells at the checkpoints 1b
itself scored, against the twins already on disk.

| row | 1b (argmax S1) | 1c (depth margin) | bar | result |
|---|---|---|---|---|
| `lubana_above` | 10/10 present | **9/10 positive**, mean M **+0.1297** | ≥ 8 | pass |
| `lubana_below` | 0/10 present | sign-flip **p = .71148**, mean M **−0.0055**, 4/10 positive | p ≥ .01 | pass |

Classification: `lubana_above` 8 `depth`, 2 `silent`, **0 `L0-only`**;
`lubana_below` 10 `silent`.

**The new statistic is stricter than the one it reproduces.** 1b scored
`lubana_above` 10/10 S1-present on the argmax over 8 sites. The mean over
the six depth sites demotes two of those cells (10M/seed101 at M = +0.0150,
1M/seed102 at M = −0.0050) — 9/10 positive, 8/10 classified `depth`. That is
the intended direction: an argmax over 8 candidates is biased upward, and
removing the selection removes the bias with it.

**Layer 0 is not silent in the trained above-threshold row.** Every one of
the ten cells has a positive L (+0.020 to +0.080), yet none classifies
`L0-only`, because the depth channel dominates in all of them. Descriptive,
not verdict-touching, and it is the first direct evidence that L and M
measure different things rather than one leaking into the other.

## 2026-08-14 — POWER TABLE FINALIZED AND LEDGERED, BEFORE STAGE B

Design §5 committed to finalising power against Stage A's **measured** sd
rather than a guessed one, before Stage B runs. Measured sd of the depth
margin on the absent row: **0.031042**.

| true margin @0.85 p_c | power | as a fraction of the super-critical margin (+0.1297) |
|---|---|---|
| 0.000 | 0.011 | — (Type-I, calibrated at α = .01) |
| 0.020 | 0.189 | 15% |
| 0.030 | 0.440 | 23% |
| **0.040** | **0.713** | **31%** |
| 0.050 | 0.900 | 39% |
| 0.060 | 0.977 | 46% |
| 0.080 | 1.000 | 62% |

**DECLARED UNDERPOWERED, IN ADVANCE.** §5's rule: power ≥ 0.75 at a 0.04
margin → proceed as designed; below it → declare in advance and either add
seeds or proceed explicitly underpowered. Measured power at 0.04 is
**0.713**, under the bar. **Adding seeds is impossible** — 1c trains nothing,
and the sweep exists only at seeds 100–104. So the experiment proceeds
explicitly underpowered, declared here before any sweep cell is probed.

What that buys, stated as resolution rather than as a hedge: 1c can detect
sub-critical accumulation reaching **39% or more** of the super-critical
margin with ≥90% power, and **31%** with 71% power. Below roughly **23%**,
power falls under one half and a FAIL cannot separate "no accumulation" from
"too little to see". That is 2c's epitaph written before the data instead of
after it, and it is the first time in this program that a power table has
been fixed against measured variance ahead of the scored run.

## 2026-08-14 — VERDICT PROJECTION, ledgered before the analysis runs

§9 requires the projection on the record before `analyze_1c.verdict()` is
called. Committed while Stage B was still running, so the git order is not a
matter of trust.

**Michael's projection: flat depth slope; L0 fires and tracks pool size.**

That is `FAIL (layer-0 leakage)` — the frozen prediction's outcome *and* its
mechanism, i.e. the strongest of the two FAIL variants the design names. It
is unchanged from the pre-freeze prediction, and it is now made with Stage A
in hand: the super-critical margin is +0.1297, the absent-row margin is
−0.0055 at sd 0.031, layer 0 carries a real but subordinate signal in trained
above-threshold cells (+0.020 to +0.080, never dominant), and the experiment
resolves ≥39% of the super-critical margin at 90% power and nothing below
~23%.

For it to be right, three things must hold together: the depth slope is null;
the fixed-n L is non-zero; and the natural-n L rises with pool size. Any two
without the third lands on `FAIL (layer-0, mechanism unconfirmed)` or on a
plain null, both of which the analysis reports as distinct results.

Recorded so that a hit is not retrofitted and a miss is not quietly dropped.
1b's projection **missed** — forecast ~6/10 grokking and FAIL, got 9/10 and
PASS — and the miss was only legible because it had been written down first.

## 2026-08-14 — STAGE B COMPLETE, then CLOSED: VERDICT FAIL

Stage B 80/80, 0 failed, 42.4 min. Campaign total **200 profiles, 0 failures**
across three phases (twins 100/100 in 40.6 m, Stage A 20/20 in 28.7 m,
Stage B 80/80 in 42.4 m).

    depth-margin slope  +0.02458   block p 0.07431   n_blocks 10 of 10
    per-cell classes    silent 40 / 40   depth 0   L0-only 0
    site-level fires    0 of 320 trained sub-critical sites (CP95 <= .01146)
    capability          0.0878-0.1040 vs chance 0.1000 — flat, as measured
                        before the freeze

**The projection missed.** Ledgered at `c54ca41` before the analysis: flat
depth slope, L0 fires, L tracks pool size. Flat slope RIGHT (p .07431); L0
fires WRONG (0 of 320 sites, 0 of 40 cells); L tracks pool WRONG (slope
−2.4e−05, p .81261, wrong sign). Outcome held, mechanism did not; the analysis
returns `variant: none` because nothing fired to name. Second consecutive
projection miss, and both were legible only because written first.

**First clean null in the program.** 0 of 480 twin sites and 0 of 320 trained
sites. Exp 2's control fired 120/120; 2b's caught 13/25; 2c's chance floor
manufactured signal. Neither the models nor the apparatus fired spuriously
here.

**Process gap, disclosed.** `verdict()` takes `natural_l0_tracks_pool` and the
frozen module has no function computing it. Rule frozen in §4; implementation
(`run/pool_trend.py`) written after Stage B, committed before being run
(`7e49f6e`), and it changed nothing — `variant` was `none` regardless. This is
1b's missing-loader defect one level over, in the experiment that fixed the
loader.

**The one pre-committed change was NOT spent.**

See `results/VERDICT.txt` and `results/retrospective.md`. Tag `exp1c-closed`.

## Next

1. ~~Campaign driver.~~ Built, `run/campaign_1c.py`, 9 fixtures.
2. ~~Twins first.~~ **Done: 100/100.**
3. ~~Stage A gate.~~ **PASS.** Power table finalized and ledgered.
4. ~~Verdict projection.~~ Ledgered before the analysis.
5. ~~Stage B + analysis + closeout.~~ **CLOSED, VERDICT FAIL.**

Successors are in `results/retrospective.md` §7. The load-bearing one: freeze
every input the verdict function takes, not just the loader.
3. Stage A on 1b's 20 lubana cells; **finalise and ledger the power table
   against the measured sd before Stage B runs.**
4. Stage B, both arms. Commit per cell.
5. Ledger the verdict projection, then run the frozen analysis once.
