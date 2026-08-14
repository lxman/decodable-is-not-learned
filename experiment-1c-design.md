# Experiment 1c — Design Doc: Sub-Critical Structure, Read From a Sweep That Was Never Probed

**Status:** **DRAFT — NOT FROZEN.** Nothing runs until §8 step 1 is
executed and tagged `exp1c-preregistered`. The instrument will be
`experiments/exp1c/` — `analyze_1c.py`, `run/run_profile.py`,
`run/campaign_1c.py`, and a fixture suite.

**The prediction is on the record before any probe runs** (Michael,
2026-08-14, before `experiments/exp1c/` existed): **layer-0 only —
leakage, not structure.** Any signal that appears will sit at layer 0
and track the shrinking singleton pool rather than the graph density.
Under this prediction the experiment returns **FAIL** on its primary
test. It is written down first so a FAIL cannot later be presented as a
surprise, nor a PASS as expected. 1b's projection missed; this one may
too, and the miss is the record.

**Predecessors:** `experiment-1-design.md` (tag `exp1-analysis-frozen`,
FAIL), `experiment-1b-design.md` (tag `exp1b-closed`, PASS). 1c reuses
Exp 1's task implementation, model constructor, activation collector and
probe verbatim, and 1b's untrained-twin construction verbatim. It trains
nothing.

---

## 1. Hypothesis and logical structure

**Hypothesis.** Below the percolation threshold, linearly decodable
class structure accumulates continuously with graph density, while the
capability metric stays flat.

If it does, percolation gates when structure becomes *expressible*, not
when it *exists*, and the essay's carve-out — that Lubana-style
capabilities genuinely do not exist below threshold — is wrong in a
specific and interesting direction. If it does not, the carve-out is
confirmed by our own measurement rather than borrowed from Lubana's
paper, and the three-signature discriminator acquires a real referent.

**Why the carve-out is the right target.** The essay's whole operational
content is a boundary: resolution cases on one side, percolation cases
on the other. Exp 1b established that the S1 discriminator separates
them at the two endpoints (`lubana_above` 10/10 present, `lubana_below`
0/10). Two points do not describe a boundary. This experiment reads the
region *between* them, which is where a boundary either exists or
dissolves.

**The competing hypothesis is the program's own track record.** In four
of five closed experiments the finding came from the measurement
apparatus rather than the models: Exp 2's untrained control fired on the
entire battery; Exp 2b's caught leaks in 13 of 25 capabilities; Exp 2c's
empirical untrained floors were ≈0, so format-only competence was
credited its guessing rate and correcting it moved ρ from .368 to .2005;
Exp 1b's twins fired raw S1 in 9 of 10 grokking cells. The frozen
prediction (§ header) is that this experiment makes it five of six.
The design must therefore be able to *detect* that outcome and name it,
not merely fail to reject.

---

## 2. What is on disk, and why it has never been read

`experiments/exp1/run/run_lubana.py:211-227` — the graph-axis branch of
S3 — trains a dedicated sub-critical density sweep:

```
for mult in cfg.s3_graph_points:          # (0.25, 0.45, 0.65, 0.85)
    sub_kw["edge_prob_mult"] = mult
    ... _train_setting(sub_lang, cfg, seed, cfg.s3_graph_budget_steps, sub_dir, ...)
    ys.append(float(sub_hist.eval_metric[-1]))
```

Four densities × two sizes × five seeds = **40 trained cells**, 10,000
steps each, checkpoints saved throughout — **1,800 checkpoint files
across 8 directories**, 45 per cell, terminal `step_0010000.pt` verified
present in all 40.

The only quantity ever extracted from them is `sub_hist.eval_metric[-1]`:
one scalar per cell, consumed as a y-value for the S3 forecast toward
p_c. `best_probe_accuracy` is called exactly once in that file, at line
192, inside the *training-steps* branch. **The probe has never touched
the density sweep.**

These are not new runs. They are 44 hours of already-purchased compute
from the 1b campaign, from which one number per cell was taken and the
rest discarded.

**The densities.** `edge_prob_mult` is a multiple of the per-class
bipartite giant-component threshold p_c ≈ 1/√(|E_c|·|K_c|)
(`tasks/lubana_lang.py:87`). At the paper scale p_c = 0.00248452.

| p / p_c | edge_prob | singleton pool (mean of 5 seeds) | classes | smallest class |
|---|---|---|---|---|
| 0.25 | 0.000621 | 866 | 10/10 | 80 |
| 0.45 | 0.001118 | 773 | 10/10 | 67 |
| **0.50** | 0.001242 | 752 | 10/10 | 62 |
| 0.65 | 0.001615 | 659 | 10/10 | 53 |
| 0.85 | 0.002112 | 536 | 10/10 | 40 |
| 10.0 | 0.024845 | **0** | — | — |

The 0.50 row is `lubana_below`, already scored in 1b (0/10 S1-present).
It sits *inside* the sweep, which supplies a free consistency check
(§5). The 10.0 row is `lubana_above`: zero singletons, the giant
component having absorbed every entity — the percolation ground truth
confirming itself by construction.

**Why grokking is not in this experiment.** `configs/grokking.py:28`
sets `n_layers=1`, the size-scaled configs hold depth fixed
(`grokking.py:85`), and `run_phaseA.py:45` collects `token_indices=(-1,)`.
One layer × one token = **one probe site**, which the 1b records confirm
(`n_layers_tested: 1`). Grokking has no depth profile to read, so the
measure defined in §4 does not exist for it. Its exclusion makes the
matrix homogeneous — same architecture, same 8 sites, same task, same
label space throughout — which is the defect Exp 1 was killed by (§2 of
`experiment-1b-design.md`) and this design does not reintroduce.

That exclusion carries a finding worth stating separately, since it
bears on how 1b's PASS should be read. Grokking's S1 is Bonferroni-
corrected across **1** candidate; lubana's across **8**. Grokking probes
1500 validation rows against a 0.0088 chance floor; lubana probes 225
against 0.100. Grokking's untrained twin therefore fires with 6.7× the
rows, an 11× lower floor, and an 8× looser correction — three
compounding advantages, none of them properties of the model. This is
descriptive here and touches no verdict, but it belongs in the methods
paper.

---

## 3. The matrix

| axis | levels |
|---|---|
| density p/p_c | 0.25, 0.45, 0.65, 0.85 (all sub-critical) |
| size | 1M, 10M |
| seed | 100, 101, 102, 103, 104 |

40 trained cells, each paired with an **untrained twin profile**.

**Twins.** The model architecture does not depend on density —
`_make_model` reads `vocab_size` and `max_len`, which are fixed across
the sweep — so there are **10 distinct random-init models** (2 sizes × 5
seeds), each probed on all four density pools, yielding 40 twin
profiles. Each twin shares its cell's architecture, size, seed, probe
data and labels exactly, per 1b §4. No training. Total cost: 10 model
constructions and 40 probe fits.

**Stage A cells.** 1b's 20 lubana cells (`lubana_above` and
`lubana_below`, 2 sizes × 5 seeds) and their 20 twins, re-probed at all
8 sites. These carry known answers and are the confirmation gate (§8).

Nothing under `experiments/exp1/` or `experiments/exp1b/results/` is
modified. 1c reads checkpoints and writes its own records.

---

## 4. The measure

**Probe sites.** `_entity_probe_data` collects at
`token_indices=(1, -1)` over 4 blocks: **8 sites**, indexed
(layer ∈ {0,1,2,3}) × (token ∈ {1, −1}). Token 1 is the entity token;
token −1 is the fixed `lVerb0` position.

**Channel profile.** For each cell, probe accuracy at all 8 sites — no
argmax, no selection — minus the accuracy of that cell's own twin at the
*same* site. An 8-vector of paired differences.

The argmax collapse is what 1b's records store and it is what this
experiment exists to stop doing. An argmax over 8 sites is biased
upward, discards which channel carried the signal, and reduces a profile
to one bit. Subtracting the twin at the matched site removes the
site-specific reservoir contribution, which is the quantity the frozen
prediction says is the whole effect.

**Primary statistic — the depth margin M.** Mean of the paired
differences over the six sites with layer ≥ 1. Mean, not max: a max over
differences is biased upward and its null distribution depends on the
number of sites, which is precisely the defect §2 identifies in
grokking's Bonferroni family.

**Diagnostic statistic — the layer-0 margin L.** Mean of the paired
differences over the two layer-0 sites. **L is the frozen prediction's
own statistic.** It is reported for every cell and it cannot touch the
verdict (§5), for the same reason 1b's untrained row lost its bar: a
statistic that the prediction says will fire is not a test of the
prediction unless something else can fail.

**Per-site fire rule (ruled 2026-08-14, closing open item 4).** Site *s*
of cell *c* fires iff **both**:

- (a) the label-permutation null at *s*, Bonferroni-corrected across all
  8 sites, gives p < 0.01 — the same family and α as 1b's S1; **and**
- (b) the trained accuracy at *s* strictly exceeds the twin's accuracy at
  *s* — 1b's floor correction, applied per site rather than at an argmax.

Both are required because 1b measured that they are load-bearing on
different rows and neither is sufficient alone. The floor correction
demoted a grokking cell the null had admitted (10/10 raw → 9/10). The
null blocked `lubana_below`/1M/seed100 at p = .847 where the margin was
positive, which the correction alone would have let fire. A rule
carrying only (b) admits reservoir decodability; a rule carrying only (a)
admits anything the random expansion already separates.

**`n_perm` is raised to 10,000, from 1b's 1,000.** At 1,000 the
corrected p for *k* exceedances is 8(k+1)/1001, so k = 0 gives 0.00799
(passes) and k = 1 gives 0.01598 (fails): the bar is attainable only by a
zero-exceedance sweep and the test is binary with no resolution. This is
not hypothetical — all ten of 1b's `lubana_above` fires report
`null_p = 0.007992007992007992`, exactly 8/1001, every one pinned to the
quantization floor. One such decision per cell was tolerable; 1c makes
**960 site-level decisions** and compares them across sites within a
cell, where a zero-or-nothing estimate is noise. At 10,000 the bar
tolerates up to 11 exceedances and the reported p carries resolution.
Grokking's Bonferroni family of 1 gave it resolution 1b's lubana rows
never had — another asymmetry between the two systems (§2).

**Cell classification**, by precedence:

| class | condition |
|---|---|
| `depth` | at least one site with layer ≥ 1 fires |
| `L0-only` | no depth site fires, at least one layer-0 site fires |
| `silent` | no site fires |

The pair (n_depth_fired, n_L0_fired) is reported for every cell
alongside its class, so precedence never hides a co-fire.

**Fixed, class-stratified sampling.** The singleton pool shrinks
monotonically with density (866 → 536), so statistical power would fall
exactly as the predicted effect rises, and a flat result would be
uninterpretable. Every cell therefore probes a **class-stratified
subsample of 40 entities per class × 10 classes = 400 rows**, 40 being
the smallest per-class count observed across all densities and seeds
(0.85 p_c). Validation fraction 0.25 → **n_val = 100**. The trained cell
and its twin use the identical subsample. n and class balance are then
constant along the swept axis by construction rather than adjusted for
afterwards.

**Natural-n diagnostic arm (non-verdict-touching).** Fixing n at 400
designs the power confound out of the primary test, but it also removes
the variation the frozen prediction is *about*: if L "tracks the
shrinking singleton pool," a design in which the pool does not shrink
cannot show it. Every Stage B cell is therefore additionally profiled at
its **natural pool size** (866 / 773 / 659 / 536), and L is regressed on
pool size across that arm.

This arm computes paired margins only — **no permutation null**, since
the quantity of interest is a slope, not a fire — so it costs 80 profiles
× 8 sites = 640 fits, which is negligible against the fixed-n arm's
9.6 M. It is marked `verdict_touching: False` in the analysis output and
cannot enter the verdict tree, for 1b's reason: a statistic the
prediction says will move is not a test of the prediction. It exists so
that a FAIL can confirm the predicted *mechanism* rather than merely be
consistent with its *outcome*.

**Residual confound, disclosed not fixed.** Subsampling equalizes count
and class balance but not *composition*: at higher density the surviving
singletons are a more selected set — the entities that failed to join a
component. If sub-critical structure exists, those are plausibly the
entities carrying least of it, which biases the primary test toward the
null and therefore toward the frozen prediction. No subsample repairs
this. It is a limitation of reading a sweep built for another purpose,
and it is stated here rather than discovered at analysis time.

**Checkpoint.** Terminal, `step_0010000` — the full training budget the
sweep was given, and the same checkpoint whose `eval_metric` supplied
the S3 y-values. Sub-critical cells have no transition and therefore no
"below-threshold checkpoint" to select; the question is what is decodable
after a fixed budget. Verified present for all 40 cells.

**Capability metric.** Each cell's `eval_metric[-1]` is recorded
alongside its margins, so "structure accumulates while capability stays
flat" is a measured conjunction rather than an assumption.

---

## 5. Preregistered pass/fail

**Primary test.** Pooled OLS slope of the depth margin M on p/p_c,
one-sided positive, α = 0.01. Null by **exact within-block relabeling of
the four density levels** (4! = 24 arrangements per block, sampled),
across 10 blocks = 2 sizes × 5 seeds. Blocking on (size, seed) is what
makes the test paired against initialization and scale.

**Verdict tree, adjudicated in this precedence order:**

1. **Stage A gate fails** → `INSUFFICIENT_DATA`. The measure did not
   reproduce known answers; the sweep is not probed. (Conditions in §8.)
2. **0.50 p_c consistency check fails** → `INSUFFICIENT_DATA`, with the
   discrepancy investigated before anything else is reported. The sweep
   brackets the scored `lubana_below` row; if 1c's measure implies
   structure at 0.50 p_c where the closed 1b record found none, the new
   measure is wrong, not the closed record.
3. **Attrition leaves < 8 of 10 blocks** → `INSUFFICIENT_DATA`.
4. **Slope p < 0.01 and slope > 0** → **PASS**: sub-critical
   accumulation detected.
5. **Otherwise** → **FAIL**: no detectable sub-critical accumulation,
   reported with the L diagnostic alongside.

**Pre-committed robustness, reported as headline and not as caveat.**
Per-cell classification of all 40 cells by the §4 per-site rule into
{`silent`, `L0-only`, `depth`}, with counts per density. This is 1b's
own closeout lesson — a pooled statistic hid that its 10/10 was really
9/10 — and 2c's: a pooled correlation over a battery with 22 tied rungs
had no per-unit story to fall back on when the omnibus failed. The
per-cell table is published whatever the slope test returns.

**The frozen prediction's outcome is a named FAIL variant.** If the
depth slope is null while L is non-zero on the fixed-n arm **and** L
rises with pool size on the §4 natural-n diagnostic arm, the result is
`FAIL (layer-0 leakage)` — a positive finding about the instrument, not
an absence, with its mechanism confirmed rather than merely consistent.
If L is non-zero but flat in pool size, the result is
`FAIL (layer-0, mechanism unconfirmed)`: the prediction's outcome held
and its stated cause did not, and both halves are reported. The analysis
reports the L-versus-M contrast for every cell so either outcome is
distinguishable from a flat
null rather than inferred from it.

### Power

Simulated against the primary test as specified, two independent
implementations agreeing within Monte Carlo error. Effect parameterized
as the true depth margin at 0.85 p_c, rising linearly from 0 at 0.25.

| true margin @0.85 p_c | sd = 0.015 | sd = 0.023 | sd = 0.035 |
|---|---|---|---|
| 0.000 | 0.013 | 0.011 | 0.009 |
| 0.020 | 0.736 | 0.332 | 0.146 |
| 0.040 | 1.000 | 0.942 | 0.580 |
| 0.060 | 1.000 | 1.000 | 0.927 |
| 0.100 | 1.000 | 1.000 | 1.000 |

Type-I error is calibrated (0.009–0.013 at α = 0.01). Reference margins
measured in 1b on the argmax-over-8 statistic: **+0.0123** where the
capability is absent (0.50 p_c), **+0.2178** where it is present
(10 p_c).

**The underpowered region is disclosed in advance.** If sub-critical
accumulation reaches only ≈0.02 by 0.85 p_c — about 9% of the
super-critical margin — power is 0.33 at sd = 0.023 and 0.15 at
sd = 0.035. A FAIL in that regime cannot separate "no accumulation" from
"too little to see," exactly as 2c's conditional power of .5604 could
not. That concession is recorded here, before data, and it will be
repeated in the verdict.

**The sd is not yet known and will not be guessed.** 1b stored only the
argmax, so the variance of the mean-over-six-sites margin at n = 400 is
not estimable from any existing record. Stage A measures it directly on
the 20 known-answer cells. The power table is then finalized against the
measured sd and ledgered **before Stage B runs** (§8). If measured power
falls below 0.75 against a margin of 0.04, that is stated in advance and
the experiment either adds seeds or proceeds explicitly underpowered —
declared, not discovered.

Only the *variance* transfers from Stage A to Stage B. Stage A cells sit
at 0.50 and 10 p_c and carry no information about the sweep's outcome.

---

## 6. What the dumbest baseline achieves

Standing requirement: an operationalization that no baseline can fail is
not a test.

| degenerate instrument | outcome |
|---|---|
| probe that always fires | fires equally on trained and twin; M ≈ 0 at every density; slope null → FAIL |
| probe that never fires | M ≡ 0; slope null → FAIL |
| probe reading **reservoir dimensionality** | identical in cell and twin at every site; differences vanish → FAIL |
| probe reading **entity-token identity** | loads on layer 0, appears in L, contributes nothing to M → FAIL, and is *named* as the layer-0 variant |
| probe reading **pool composition** | held constant by the stratified fixed-n subsample; cannot produce a density slope |
| measure that inflates with site count | excluded by using the mean rather than the max over sites |

Six routes. The test can fail, and the frozen prediction is that it will.

**The bar is passable on real numbers.** The measured separation between
capability-absent and capability-present margins in 1b is 0.0123 versus
0.2178, a factor of 18. A sub-critical accumulation reaching a fifth of
the super-critical value by 0.85 p_c would be detected at power 1.000.

---

## 7. What Exp 1c does not claim

- **Nothing about real models.** Synthetic ground truth only. Exp 2c
  tested the real-model version and returned an uninterpretable FAIL.
- **Nothing about grokking**, which has one probe site and is excluded
  (§2).
- **Nothing about scale beyond 10M.** The 100M tier was never run for
  the sweep, as it was dropped from 1b for cost.
- **Nothing about S2 or S3.** Not measured here.
- **Nothing about the super-critical side.** Every density is below p_c.
- **A FAIL does not establish that no sub-critical structure exists** —
  see the disclosed underpowered region (§5) and the composition
  confound (§4).

---

## 8. Run plan

1. **Freeze:** this doc + `analyze_1c.py` + fixture suite, tagged
   `exp1c-preregistered`. Nothing probes before it.
2. **Twins first**, before any trained sweep cell is read. Under the
   frozen prediction the twins are the load-bearing measurement, and
   running them first is what made 1b's floor correction possible while
   it was still legitimate. 10 model constructions, 40 probe profiles.
3. **Stage A — confirmation gate**, on 1b's 20 lubana cells and their 20
   twins at all 8 sites, using the **identical n = 400 class-stratified
   subsample specified in §4** so that the measured variance transfers to
   Stage B rather than describing a different sample size. Required to
   proceed:
   - `lubana_above` depth margin M > 0 in ≥ 8 of 10 cells;
   - `lubana_below` depth margin M not significantly > 0 pooled, by a
     one-sided paired test at α = 0.01;
   - the measured sd of M recorded and the §5 power table finalized
     against it and ledgered.
   Failing any of these, the experiment stops at `INSUFFICIENT_DATA` and
   the sweep is not probed.
4. **Stage B — the sweep**, 40 cells at the terminal checkpoint, on both
   arms: the fixed-n = 400 primary arm with the full per-site null, and
   the natural-n diagnostic arm with margins only. Commit per cell, per
   the campaign rule.
5. **Analysis:** the frozen script, once, after the verdict projection is
   ledgered in `experiments/exp1c/PROGRESS.md`.
6. **Close-out:** `VERDICT.txt`, retrospective, tag `exp1c-closed`.

**Cost.** No training. **120 probe profiles**: 40 in Stage A (20 known-
answer cells + 20 twins), 80 in Stage B (40 sweep cells + 40 twin
profiles). At 8 sites each with an `n_perm` = 10,000 permutation null,
that is 120 × 8 × 10,001 = **9,600,960 logistic-regression fits** at
n = 400. The §4 natural-n diagnostic arm adds 80 profiles × 8 sites × 1
fit = **640 more**, since it runs no null — four decimal places below
the primary arm, which is why it is affordable at all. Activation
collection is 48,000 prompts of length 3 for the fixed-n arm plus ~55,000
for the diagnostic arm.

Measured 3.4–3.6 ms/fit at d_model 128 and 256 on synthetic data of the
right shape, giving **≈9.3 h single-threaded**; real activations converge
more slowly than Gaussians, so budget 9–20 h of background wall-clock and
parallelize across cells. That is under half of 1b's 44-hour training
campaign and buys the resolution §4 requires. The permutation null, not
the observed fits, is the entire cost: the observed fits alone are 960.
The DGX Sparks stay untouched.

**This consumes the 80 GB of 1b checkpoints** that has been sitting
undisposed since the campaign closed. Disposition should wait until 1c
closes; note that late checkpoints were measured to be non-reproducible
(training diverges late; only early steps are bit-exact), so
"regenerable from config + seed" is false for exactly the terminal
checkpoints this experiment reads.

---

## 9. Process rules carried forward

- Thresholds frozen pre-run; analysis script committed with the doc and
  not edited after data collection.
- **The loader is frozen with the analysis.** 1b froze `analyze_1b.py`
  with a `verdict()` but no record loader, and the gap surfaced at
  analysis time. `analyze_1c.py` ships with its loader and the loader is
  fixture-tested.
- **One pre-committed change — UNSPENT.** Available once, with the
  reason ledgered *before* the change.
- **Verdict projection ledgered before the analysis runs.**
- Per-cell failure rate reported as headline, not caveat (1b closeout).
- No interval-coverage criteria on extrapolations.
- Every zero as a Clopper–Pearson bound; never a claimed zero.
- Per-cell tallies written after reading each record, never inferred
  from the pattern of prior cells.
- Commit per cell during the campaign, so no uncommitted record dirties
  the next cell's `git_sha`.

---

## Open items before first run

1. ~~`analyze_1c.py` written and frozen with fixtures.~~ **Written
   2026-08-14, pending the freeze commit.** `analyze_1c.py` carries the
   per-site rule, both margins, the classification, the block-permutation
   slope test, the Stage A gate **and its own loader** (§9). 83 fixtures
   across four files, one synthetic case per preregistered provision.
   **Mutation-tested: 20 of 20 deliberate defects killed**
   (`tests/mutation_check.py`), covering both directions of each gate —
   removing the floor, removing the null, removing Bonferroni, admitting
   a tie, max-for-mean, inverted classification precedence, a relaxed
   block floor, a between-block null, two-sided p, population-for-sample
   sd, a lowered present-row bar, letting the diagnostic arm force a
   PASS, and skipping either INSUFFICIENT_DATA branch.

   One defect initially **survived** — a per-site train/val split, which
   would make the eight accuracies incomparable and the mean-over-sites
   margin an average of eight different experiments. The first repair
   still missed it, because at the fixture's signal strength the probe
   scored exactly 1.000 under every split. The test now runs at a
   separation where accuracy responds to the split. Recorded because the
   suite's own blind spot is the kind of thing that is invisible
   afterwards.
2. ~~`run/run_profile.py` — the 8-site profile runner.~~ **Written
   2026-08-14.** Torch-free decision logic in `run/profile_lib.py`
   (subsample, checkpoint mapping, per-site probe) so it is testable
   without a GPU; orchestration in `run/run_profile.py`. Skip-if-exists
   durability, one JSON per cell. Checkpoint→model reconstruction
   verified `strict=True` on 4 of 4 spot cells (939,312 params at 1M;
   12,870,144 at 10M), state dict only — **not probed**, per §8 step 1.
3. ~~Confirm the stratified subsample is constructible at 40/class for
   all 40 (density, size, seed) combinations.~~ **Closed 2026-08-14.**
   `lang_kwargs` is a function of `scale` alone — verified identical for
   `model_size="1M"` and `None` — so the 4 densities × 5 seeds = **20
   languages are all the languages**, each serving both sizes. Minimum
   per-class singleton count across all 20 is **exactly 40**, and
   `lubana_above`'s full pool gives 90. The subsample is feasible with
   **zero margin**: one entity fewer in any class at any (density, seed)
   and the design drops to 39/class. The runner must therefore assert the
   count rather than assume it, and record the realized per-class count
   in every profile.
4. ~~Decide whether the per-cell classification rule thresholds on the
   permutation null per site or on the margin alone.~~ **Ruled
   2026-08-14 (Michael): permutation null per site**, conjoined with the
   per-site floor correction. Rule, family, α and the raised `n_perm` are
   specified in §4. Ruled before any 1c probe ran and before the
   analysis script exists.
5. ~~Record the capability metric for all 40 sweep cells, so the
   "capability stays flat" half of the hypothesis is measured rather than
   assumed.~~ **Closed 2026-08-14 with data.** No history reconstruction
   was needed — every sweep checkpoint stores its own `eval_metric`. Read
   from all 40 terminal checkpoints:

   | p / p_c | 1M | 10M |
   |---|---|---|
   | 0.25 | 0.0896 | 0.1068 |
   | 0.45 | 0.1024 | 0.0988 |
   | 0.65 | 0.0820 | 0.0936 |
   | 0.85 | 0.1088 | 0.0992 |

   Overall mean **0.0976** against a chance of **0.1000**, range
   0.0680–0.1360, no trend in density. Capability is flat and at chance
   across the entire sub-critical sweep. **The preregistered conjunction
   is therefore live**: if the depth margin rises with density, it rises
   while the capability metric is pinned at its guessing rate. Had
   capability itself risen, a positive slope would have been
   uninterpretable — structure and capability would have moved together
   and the experiment could not have separated them. The runner reads
   this same field per cell rather than trusting this table.
