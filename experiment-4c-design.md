# Experiment 4c — the sealed replication: pre-clear alignment growth ranked against the whole flat pool, on the two training runs Experiment 4 never touched

**Status: RATIFIED 2026-09-20 — built + frozen by SDD (plan `docs/superpowers/plans/2026-09-18-exp4c-build.md`; six tasks, seven fix rounds, the adversarial freeze's F-1..F-7 closed additively, the final whole-branch review and one fix wave, re-review clean; record `experiments/exp4c/FREEZE_CHECKLIST.md`), the slips below applied on Michael's word ("Ratified — apply the slips and tag"), tag `exp4c-preregistered` cut at the commit that carries them (blob-bound over analyze_4c, battery_4c, rank_4c, collect_4c, power_4c, run/sweep_4c and `results/power_4c.json`). §10's dials a–o were ruled as recommended 2026-09-18 ("Proceed with 4c"): dial (a) = RUN with §4's declaration printed. Session 1 (design) was written 2026-09-17 on his word ("begin 4c"). No model has been contacted; the power record was written once, before the tag. The design session ran five analysis-only computations on committed bytes, all listed in §2; two of them changed what 4c is, and §2 says how.**

## 1. The question

Experiment 4 read the lens claim at task grain — does the agreement between a model's representation of a task's items and three unrelated released models run ahead of the general convergence trend before the task first performs? — and closed LEADS at T = .61 with its licence bounded. Experiment 4b built the null the bound asked for and closed NOT-DISTINGUISHABLE: a quarter of placebo batteries reach .61, the lead over the null is +.17 with an interval from −.26 to +.70, and the limit was named in the record — the null rests on the 4–11 flat tasks per trajectory that pass the eligibility screen, and φ is a ratio with a small denominator (26 cells running from −1.12 to 2.97).

4b's §8 named 4c as the replication on the two trajectories the program has scored at item grain and Exp 4 never read: **Pythia 6.9b** (2h: 22 trained checkpoints) and **OLMo-2 13B** (2l: 16). There T is unknown to everyone, the null is unknown to everyone, and nothing about the representation along either run has been computed.

4c asks the same question there, with an instrument that does not have 4b's limit:

> On Pythia 6.9b and OLMo-2 13B, at the last checkpoint before each task first performs, does the task's alignment growth since the first checkpoint rank above the alignment growth of the tasks that never perform, at the same checkpoint of the same run?

One number per cell — a rank among the run's whole flat pool — with no ratio, no eligibility screen, a null mean of exactly ½ and a null distribution that does not depend on the data. §3 says why that is the same question Exp 4 asked, and §2 says what the design session already knows about the answer on the four known runs, because it bears on whether this experiment is worth two days of the Mac.

## 2. What is known, what the design session computed, and what is sealed

**Known from the closed record, to everyone:** Exp 4's and 4b's verdicts and every number in them; 2h's and 2l's committed per-item outcomes on both new trajectories (so which tasks rise, when each first clears, which never clear — §3.2's table is derived from committed bytes and is not foresight); the four released references' k-NN set tables at `main` (Exp 4's reference stage, committed); and, through Exp 4's size ladder, the k-NN set tables of `ladder_pythia_6.9b` at `main`, which 2h's Hub scan found byte-identical to step 143000. **So the 6.9b run's ENDPOINT alignment level is derivable from committed tables today.** Nobody has derived it, and 4c's cell statistic does not read it (it reads t_1 and t⁻), but it is disclosed as known-in-principle.

**What the design session computed (2026-09-17, analysis-only, committed bytes, zero model contact; scripts committed under `experiments/exp4c/design_session/`).** Each is a disclosure event:

1. **The outcome-side tables for the two new runs**, through `battery_4.rung_sets_4` on 2h's and 2l's committed sweep records: §3.2.
2. **The alignment series a_r(t) of all 34 tasks on the four KNOWN runs**, through Exp 4's own `alignment_series_4` on its committed set tables (read-only; the tree was clean before and after).
3. **The cell statistic of §3.3, fixed on a priori grounds before any value was looked at** (the reasoning is §3.3's: the trend cancels within a checkpoint, so a rank needs no excess, no ratio and no eligibility screen, and the whole flat pool becomes the null's support — the direct answer to 4b's two named limits), computed on the four known runs over every rising task with a pre-clear window, 42 cells: **mean rank quantile U = .6224.** Against an independent-draw placebo null (mean .5004, SD .0464) p = .0049; against an exact rung-level sign flip of (q − ½) over 17 tasks p = .0092; against an exact family-block sign flip over 2c's 9 families present p = **.0391**. Per run: Pythia 2.8b .487 (7 cells), OLMo-2 7B .630 (13), SmolLM3 .694 (7), Comma .646 (15).
4. **The type split, named before it was computed because the confound is visible in the battery's composition** (the rising tasks are where the option and string tasks live; the flat pool is two-thirds modular and base arithmetic): arithmetic rising cells ranked among arithmetic flat tasks only, **U = .5103 over 26 cells** (rung-level p .43, family-block p .45; per run .270 / .448 / .667 / .633); non-arithmetic rising cells against the whole flat pool, **U = .7595 over 16 cells** (rung-level p .016; family-block p .125 — three families cannot reach .05).
5. **One direct check of the task-type reading of (4):** the non-arithmetic tasks that NEVER perform on a run, ranked among that run's arithmetic flat tasks over the whole grid — 18 task-runs, **mean quantile .42.** Non-arithmetic tasks do not out-grow arithmetic ones as a class. The exceptions point the other way from a type artifact: odd6 and odd_one_out sit at .80 and .91 on Pythia 2.8b, where they never perform, and they are tasks that do perform one size up.

**What those five computations say, stated as the designer's belief and not as evidence:** the rank instrument finds a pooled signal on the known four that φ could not resolve (.62, family-block p .04); the signal is absent where the comparison is type-matched (.51) and lives in nine option and string tasks (.76); and a plain "option tasks align faster" artifact does not explain it (.42 for the never-performing ones). None of this is a result. Every number in (3)–(5) was computed after T_4, the 26 cells and 4b's null were known to the designer, on a statistic chosen by the designer; it cannot enter the essay except as the stated motivation for a sealed test. It is here because a design that hid it would be preregistering with its eyes closed, and because it sets the power statement's alternative (§4).

**No other statistic was computed.** No window-mean variant, no other k, no other position, no per-reference split, no threshold on g. The five items above are the whole list, plus the nine per-family sums of (q − ½) on the discovery set (`DISCOVERY_PIN_4C["family_sums"]`, pinned at the build as S2's sign ledger); the scripts are the evidence.

**What is sealed:** every a_r(t) on both new runs at every checkpoint but 6.9b's endpoint, hence every g, every rank, U, both type strata and every secondary. The outcome is known; the representation along the run is not. A sealed representation read against a known outcome is what Exp 4 was before it ran, with one difference that matters: this time the statistic, its null and the alternative's shape were all fixed by a discovery set of four runs before the confirmation set of two is touched.

**Disclosure rule (checklist item 27)** applies from the build's first commit: every execution of the 4c analyzer against the real tree before the tag is counted and printed. **Count at the tag: 20** (Tasks 2–5, the freeze and the final-review fix wave; each in `experiments/exp4c/PROGRESS.md` with what it printed), every one INSUFFICIENT_DATA before any table of the new runs was read; the discovery gate printed the known U .6224 each time.

## 3. Instrument

Everything not named here is Exp 4's, imported by name and sha-pinned to `exp4-closed` at entry and exit (2j's lesson): the representation (2c's items, render and prompt-end position; 2f's collector; fp16; the pinned batch composition), the metric (mutual k-NN, k = 10, cosine, n = 500; committed `uint16 [500, 10]` set tables as the artifact of every load, the alignment re-derived from two committed tables and never read from a record), the site family (every third hidden state plus the last), depth pairing by relative depth re-derived at analysis time, `RENDER_4`/`DTYPE_4`/shot-count asserts against the committed outcome records, per-unit tensor-digest pins measured by the loader and compared by the analyzer to the committed `_checkpoint.json` digest (Exp 4 F-1), gate 1's two-loader-path identity, the halt-marker rule, tree totality, blob-bound tags, the import-surface pin, `pins_active`.

### 3.1 References — zero new reference-side contact

The references are Exp 4's four released models at `main`, three per trajectory, own family excluded: for Pythia 6.9b — OLMo-2 7B, SmolLM3-3B, Comma; for OLMo-2 13B — Pythia-12b, SmolLM3-3B, Comma. **Their k-NN set tables are already committed under `experiments/exp4/results/reference/ref_*` and are read from there, sha-pinned; no reference is loaded.** The pairing tables are new for one case (OLMo-2 13B has 40 blocks, 41 hidden states, 15 sites against 12- and 13-site references; `SITE_COUNT_PIN_4C[41] = 15` is a 4c pin, `metric_4`'s own table having no 41-hidden-state entry) and come from Exp 4's `depth_pairs` rule, committed and re-derived. Hidden-state 0 is excluded everywhere a level is averaged (Exp 4 stop #1; 4b S6) — it cancels in g exactly as it cancelled in Exp 4's excess, and the exclusion is applied anyway so that no consumer reads the constant (Exp 4 retrospective, note 2).

### 3.2 The trajectories and the outcome, verbatim from the record

| M | grid (trained points) | init referent | endpoint | rising R_M | flat | transient |
|---|---|---|---|---|---|---|
| Pythia 6.9b (2h) | 1000, 2000, 4000, 8000, 10000, 16000, 20000, 30000, 32000, 40000, 50000, 60000, 64000, 70000, …, 140000, 143000 — 22 points | real step 0 | 143000 | 8 | 24 | odd_one_out, sub3_mid |
| OLMo-2 13B (2l) | 1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000, then every 64000 to 576000, 596057 — 16 points | real step 0 | 596057 | 18 | 15 | clock24_d999 |

Clear indices (0-based, first grid point at which the committed count clears 2d's bar; `battery_4.t_clear_4` on the committed per-item bits), a known-answer pin at the build:

- **6.9b:** arith_next 5; antonym, antonym6, odd6 6; sub_base8 11; add3_mid, add_base8 13; count_div13 21.
- **13B:** add_base8, antonym, antonym6, arith_next, reverse_string, sub_base8 4; odd6, sub3_mid 5; add3_mid, add4_mid, median5, median7, oct2dec, odd_one_out, sub4_mid 6; quad_next 7; rev_string7 11; count_div13 15.

Every rising task on both runs has a pre-clear window (index ≥ 2): **26 cells**, 8 + 18, on 18 distinct tasks in **9 of 2c's families** (antonym, base_arith, base_repr, counting, mid_digit, odd_one_out, order_stat, reversal, seq_extrap). By Exp 4's type table: **17 arithmetic cells, 9 non-arithmetic** (antonym ×2, antonym6 ×2, odd6 ×2, odd_one_out, reverse_string, rev_string7). The 13B flat pool is a subset of the 6.9b flat pool, and it contains no option task and two string tasks (caesar, caesar_len8) plus hamming12: **no type-matched comparator pool exists for the non-arithmetic cells, on either run.** That is a fact about the battery and it bounds what any result can license (§6, §9). No real cell sits at the window's boundary — the smallest clear index is 4 on 13B and 5 on 6.9b — so index 2 is exercised by fixtures only.

Transient tasks are excluded from both sides, as in Exp 4. Each checkpoint's measured tensor digest must equal the committed 2h/2l `_checkpoint.json` digest for that step or the unit halts, and the analyzer re-checks the measured value.

### 3.3 The cell statistic

With a_r(t) the task's alignment at checkpoint t (Exp 4 §3.3: mean over M's sites of the depth-paired mutual k-NN, mean over the three references), t_1 the first grid point, c the task's clear index and t⁻ = t_(c−1):

    g_r(t) = a_r(t) − a_r(t_1)                                   (alignment growth since the first checkpoint)
    q_(M,r) = [ #{f ∈ flat_M : g_f(t⁻) < g_r(t⁻)} + ½ #{f : g_f(t⁻) = g_r(t⁻)} ] / |flat_M|

q is the mid-rank quantile of the rising task's pre-clear growth among the growth of every task that never performs on that run, at the same checkpoint.

**Why this is Exp 4's question.** Exp 4's excess is x_r(t) = g_r(t) − [trend_M(t) − trend_M(t_1)], and the bracket is one number per (run, checkpoint): ranking x within a checkpoint is ranking g. The flat pool's trend — the thing the excess was built to remove, and whose scatter (λ̂ 6–7) broke Exp 4's calibration — cancels identically. What remains is the comparison Exp 4 was after: before the task performs, is its agreement with unrelated models ahead of the tasks whose agreement is general drift by construction?

**What is dropped, and why each drop is a repair.** (i) The ratio φ = x(t⁻)/x(t_end): its denominator is small on most cells, its tails are what moved 4b's T\* (two OLMo-2 cells at 2.97 and 1.32), and it reads the endpoint — a checkpoint at which the task performs, which the pre-clear question does not need. (ii) The eligibility screen x(t_end) ≥ 2 SE: it existed to keep the ratio's denominator away from zero; it is what pushed φ's null mean to ≈ ½ under selection (R-7) and what cut 4b's placebo pools to 4–11. With no ratio there is no screen: every rising task with a window is a cell, every flat task is a comparator. (iii) The leave-one-out question: the rising task is never in the pool it is ranked against, so nothing is left out and 4b's NB-1 cannot recur.

**What is lost, stated:** q says whether the pre-clear growth is ahead, not what fraction of the endpoint's task-specific agreement it is. φ and T are printed on the new runs as S4, with 4b's placebo null beside them, for continuity and with no α.

### 3.4 The primary statistic and its null

    U = mean over the 26 cells of q_(M,r)            (null value exactly ½)

**Null: an exact family-block sign flip of (q − ½).** Under H0 — a rising task's pre-clear growth is exchangeable with a never-performing task's — q is symmetric about ½. All cells of one of 2c's families are flipped together, across both runs (a task recurs on both runs and siblings such as antonym/antonym6 are near-copies; the family is the program's unit of independence since 2c). Nine families: 2⁹ = 512 flips enumerated, resolution 1/512 = .00195. p₊ = the share of flips with a sum ≥ the observed sum. CI95 on U: family-clustered percentile bootstrap, 10,000.

The rung-level flip (18 tasks, 262,144 flips) and a rung-coupled placebo null in 4b's idiom (for each battery, each rising task is replaced by a flat task drawn from the pool common to both runs and used on both, ranked among the remaining flat tasks at the cell's own checkpoint; B = 10,000) are printed beside it. **Known on the discovery set: the family-block null is the most conservative of the three (p .039 against .009 and .005).** It is the primary for that reason.

**Worlds** (by p₊ alone; no effect bar — dial d): INSUFFICIENT_DATA → **REPLICATES** (p₊ < .01) / **MARGINAL** (.01 ≤ p₊ < .05) / **NOT-REPLICATED** (p₊ ≥ .05), with one sub-cell of NOT-REPLICATED named in advance, **REVERSED** (p₋ < .05: the rising tasks' pre-clear growth sits BELOW the flat pool's — 4b F-3's lesson: a licence sentence's direction is a claim about the data, checked by the analyzer).

### 3.5 The type reading — a licence modifier, enumerated

    U_arith    = mean q over the 17 arithmetic cells, each ranked among the ARITHMETIC flat tasks of its run only
    U_nonarith = mean q over the 9 non-arithmetic cells, ranked among the whole flat pool (no matched pool exists)

U_arith gets its own exact family-block flip (6 families, 64 flips, resolution .0156). The modifier, read in every world: **TYPE-GENERAL** (U_arith's p₊ < .05) / **TYPE-BOUND** (U_arith's p₊ ≥ .05 and U_nonarith > ½) / **NEITHER** (U_arith's p₊ ≥ .05 and U_nonarith ≤ ½). U_nonarith carries no p of its own under the primary null — three families give 8 flips — and the analyzer refuses to print one (4b process note 3: a null that cannot resolve the bar must not print a p); its rung-level flip (6 tasks, resolution .0156) and its placebo p are printed as descriptives and labelled so.

### 3.6 The rule's calibration, measured before it is needed

4b's lesson was that Exp 4's decision rule had a false-positive rate nobody had measured at the real scatter. 4c measures its own in the same run: **α_placebo(.01) and α_placebo(.05)** — the share of the 10,000 rung-coupled placebo batteries on which the family-block rule fires at each bar, the placebo cells put through the identical q. If α_placebo at the bar that decided the world exceeds twice that bar, the licence is read as BOUNDED and the sentence says so (§6). The build's record (§4; n_sim 4,000) puts the rule at .0085–.0115 and .0508–.0525 under exchangeable ranks with and without cross-run task correlation; the real flat tasks' dependence is what the placebo arm adds. No synthetic world reaches the BOUNDED read through the production path — every existing mode's placebo is symmetric by construction, a placebo cell being a common-pool flat task ranked among the remaining flat tasks of its own run — so the rule is pinned by a unit test at its boundary; a sixth mode that would reach it (depressing the nine tasks flat on 6.9b but absent from the common pool) is sketched in the freeze record and not built.

### 3.7 Gates (INSUFFICIENT_DATA on failure)

1. **Known-answer gate on the statistic:** 4c's code, run on Exp 4's committed tables, reproduces the design session's discovery-set numbers exactly — U .6224 over 42 cells, per-run .487 / .630 / .694 / .646, family-block p .0391, rung-level .0092, U_arith .5103 over 26, U_nonarith .7595 over 16 (pinned to full precision at the build).
2. **Outcome pins:** §3.2's rising / flat / transient sets and clear indices re-derived from 2h's and 2l's committed bits equal the pinned literals.
3. **Gate 0** (Exp 4's, site 0 excluded): each run's real step 0 sits below its endpoint on ≥ .90 of cells.
4. **Gate 1:** each run's endpoint through two loader paths, set tables identical on 34 tasks, coverage 500/task attested by the runner and required by the analyzer. On Pythia 6.9b the two paths are two WRITERS: Exp 4's committed `ladder_pythia_6.9b` table (2b's `from_pretrained` path, written by Exp 4's own collector; its digest equals 2h's committed step143000) against the sweep's candidate-file endpoint. On OLMo-2 13B, where Exp 4 holds no table, the runner writes a thin-loader endpoint unit before the sweep (one extra ≈ 55 GB load, ≈ 1.5–2 h) against the candidate-file endpoint — two loader paths through one writer, a check on the load and not on the collection.
5. **Per-unit digest equality**, measured.
6. **Reference reuse:** every reference set table read hashes to its pin in Exp 4's closed manifest; pairing re-derived and equal to the stored one, key set included.
7. **Rank determinism:** ties are counted at ½ and the analyzer prints the number of exact ties per cell (expected zero on float64 means of 500 overlaps; a nonzero count is printed, never broken by an index).

### 3.8 The tree

INSUFFICIENT_DATA (any gate, any loader refusal collected and delivered with its reason — lesson 8) → REPLICATES / MARGINAL / NOT-REPLICATED (sub-cell REVERSED), each carrying the type modifier and the calibration read. Three inputs that feed only S4 (the first-point and endpoint per-item alignment through Exp 4's own instrument) sit on the refusal path: a refusal there delivers INSUFFICIENT_DATA for the whole experiment — disclosed, not narrowed (the freeze's F-5). Every terminal and every modifier cell is reached by a synthetic world through the production path before the tag.

### 3.9 Pins and storage

Blob-bound tag over the instrument (analyzer, battery, the statistic module, the runner, the power module). Set tables committed for BOTH positions — the prompt-end `sets/` and the question-end `attested/` tables, the latter measured at ≈ 2.9 MB per unit against ≈ 1.6 MB of sets, ≈ 150–200 MB over the 41 units, inside the 0.3 GB budget (≈ 39 units × 34 tasks × ≤ 15 sites × 2 positions × 10 KB was the estimate); activations not kept (dial k drops CKA, the one consumer that needed them). The per-load pipeline is `collect_4c.process_model_4c`: Exp 4's primitives in Exp 4's order with 4c's tag and batch pin, no CKA, no global bank. Power record committed BEFORE the tag (§4) — the first time the program can do that.

## 4. Cells, resolution and power — declared before any model contact

Because q is a rank and the null is a sign flip of (q − ½), **the null distribution of the decision does not depend on the data**: the cell structure of §3.2 fixes it. Power is therefore computed at the build, through the verdict's own code, before the tag and before any model is loaded, and the declaration is part of the preregistration. The built record (`experiments/exp4c/results/power_4c.json`, written once, tag-bound, byte-reproduced by the analyzer: 4,000 draws per arm and ρ, seed 0, 26 cells on the real family structure, ranks on |flat| = 24 and 15 comparators with 19 and 12 arithmetic, the placement δ(μ) = √2·Φ⁻¹(μ), independent comparator pools per simulated cell — the placebo arm measures the real dependence — cross-run task correlation ρ ∈ {0, .5}; the design-stage estimate of 2,000 draws it supersedes read .09 / .32–.33 on the discovery shape and ≈ .70 for the detectable lead):

| alternative | P(p₊ < .01), ρ 0 / .5 | P(p₊ < .05), ρ 0 / .5 |
|---|---|---|
| null (realized α) | .0115 / .0085 | .0525 / .0508 |
| uniform lead, every cell's mean q = .60 | .161 / .126 | .436 / .374 |
| uniform lead .65 | .366 / .306 | .732 / .648 |
| uniform lead .70 | .644 / .543 | .925 / .865 |
| **the discovery set's shape: arithmetic .51, non-arithmetic .76** | **.079 / .066** | **.289 / .269** |

**DECLARED UNDERPOWERED IN ADVANCE against the alternative the designer believes.** At the program's α the rule reaches .75 power only for a uniform lead of .743 (interpolated on the record's grid), and against the discovery set's shape it fires at .01 about one time in fifteen and reaches MARGINAL or better about one time in four. Three times in four (.73 on the record), **a real effect of the size and shape seen on the four known runs returns NOT-REPLICATED**. The sixth lesson applied in advance: the pooled primary is mis-shaped for a type-bound alternative, and the shape-matched stratum cannot be adjudicated at all — six distinct non-arithmetic tasks in three families is the whole battery. The blind region, stated: any type-bound effect, and any uniform lead under the record's detectable value (.743).

What a NOT-REPLICATED therefore means is written into §6 before the data: "not detected at this resolution", with the power table quoted, never "absent".

## 5. Named secondaries (printed in every world; no α claim)

- **S1 per run:** U, its family-block p and cluster CI on 6.9b (8 cells) and 13B (18) separately.
- **S2 per type and per family:** §3.5's strata; the nine family sums; sign agreement between each family's sum here and on the discovery set (nine signs, printed with the binomial tail, labelled descriptive — the discovery set's signs are known to the designer).
- **S3 window mean:** q averaged over every pre-clear checkpoint (indices 1 … c−1) instead of read at t⁻.
- **S4 continuity with Exp 4 and 4b:** φ, T, eligibility, λ̂ and 4b's p_cal, T\*, α_placebo and per-run nulls on the two new runs, through 4's and 4b's own frozen code.
- **S5 within-riser timing:** each rising task at its t⁻ ranked among the run's rising tasks that have NOT yet cleared at t⁻ (comparators that will all perform): does imminent clearing predict more growth among tasks that all eventually perform? The cleanest control for task type the battery allows; thin by construction (13B's clear indices bunch at 4–7), printed with its comparator counts.
- **S6 six runs pooled:** U over all 68 cells with the discovery/confirmation split printed and the known-input caveat verbatim; the essay may not quote the pooled number without the split.
- **S7 the type check, replicated sealed:** never-performing non-arithmetic tasks ranked among arithmetic flat tasks over each new run's grid (discovery set: .42 over 18 task-runs).
- **S8 levels, site 0 excluded:** real step 0, the endpoint, the references' ceiling; per-reference a_r(t).
- **S9 the question-end position** through the identical statistic.
- **S10 the flat pool's texture:** λ̂ and the lag-1 autocorrelation of flat-task increments per run (4b S5: −.02 on OLMo-2 7B, −.24 to −.54 elsewhere — is 13B a random walk like its 7B sibling?).

## 6. Licences, written in advance

Bounded in every world to: 2c's battery; two runs, one from each of two families; the prompt-end position; Exp 4's site family and references; a sealed representation read against a KNOWN outcome; a statistic, a null and an alternative fixed on four runs the designer had seen. Exp 4's verdict and 4b's verdict are not revised by any world.

- **REPLICATES:** the essay's convergence paragraph regains a first-person sentence: on two training runs nobody had read, at the last checkpoint before each task first performed, the task's agreement with three unrelated released models had grown more than that of the tasks which never perform (U, its interval, p), a test whose statistic and null were fixed beforehand on four other runs where the same reading gave .62. The modifier governs the noun: TYPE-GENERAL licenses "tasks"; TYPE-BOUND licenses "the option and string tasks — nine cells on six tasks — with the type-matched arithmetic comparison showing nothing (U_arith)" and nothing wider; NEITHER cannot co-occur with REPLICATES without U_arith carrying it, and if it does the sentence says so. The scoreboard moves from "still a citation" to "measured on two sealed runs", bounded as above. If α_placebo at .01 exceeds .02 the sentence adds the rule's measured false-positive rate and rests on the placebo p.
- **MARGINAL:** "ahead at p = p₊, short of the program's α" with U and its interval and the modifier; the scoreboard says "marginal"; the lens claim stays a citation with this beside it.
- **NOT-REPLICATED:** the essay adds one sentence to the demotion: a sealed rank test on two more runs did not detect the lead (U, interval, p), at a resolution that would have missed an effect of the size seen on the first four runs three times in four (.73 on the tag-bound record) — quoted from §4 as the build's record made it. "Still a citation" stands. **REVERSED** sub-cell: the sentence says the pre-clear growth sat below the never-performing tasks', nothing about precedence is licensed, and Exp 4's sign-flip reading against the construction account is re-examined in `experiments.md` rather than left standing unremarked.
- **INSUFFICIENT_DATA:** nothing changes; the reason is ledgered.
- **Any world:** S1–S10 in full in `experiments.md`; the discovery-set numbers of §2 appear there as motivation with their post hoc status stated, and nowhere in the essay as evidence; the battery limit (no type-matched pool for non-arithmetic tasks) stated wherever a type is named; S9's reference-side inputs — Exp 4's question-end set tables, gitignored and present only on the build machine, hash-checked against Exp 4's sealed records before use — are disclosed as machine-local wherever S9 is quoted (S9 is descriptive, no α claim).
- **The licence block:** the analyzer prints the reached cell, its sentence, the modifier's outcome, the calibration read and the REVERSED check (2n note 1).

## 7. Run plan and model contact

Design (this doc + rulings) → build (`experiments/exp4c/`: the statistic module with §3.7(1)'s known-answer pins; battery_4c with the two manifests (2h's and 2l's, already committed), outcome pins, loaders (2h's `load_checkpoint` path for 6.9b, 2l's for 13B, each with its thin endpoint loader for gate 1), reference reuse and pairing; the sweep runner — Exp 4's, over two trajectories; power; analyzer; referents; worlds; totality; mutation; read sweep; import scan) → adversarial freeze → **power record committed** → ratification → tag `exp4c-preregistered` → projection sealed (by family and by type, tolerances both directions, the designer's discovery-set knowledge stated) → preflight on Michael's word (one 13B interior checkpoint end to end and freed: memory, timing, digest) → **sweep, 6.9b first**: 22 points + step 0, 13.8 GB per revision (≈ 320 GB streamed), ≈ 40 min each ≈ 15 h, mlx servers up (Exp 4 ran 7B with them up) → **13B**: the thin-loader endpoint unit first (gate 1's second path; one extra ≈ 55 GB load, ≈ 1.5–2 h), then 16 points + step 0, 54.9 GB per revision (≈ 990 GB streamed), 27 GB resident at fp16 (2l's preflight), ≈ 1.5–2 h each ≈ 30 h, **mlx text server down for the duration** (2l's arrangement) → gate 1 first in each → the watcher committing every unit; `Popen(start_new_session=True)`; one disposable poller → analyzer once, detached, on Michael's word → `exp4c-closed` → retrospective → close-out on his word. ≈ 45 h of model time, ≈ 1.26 TB streamed one checkpoint at a time. One pre-committed change.

**Disk, an operational dial (j):** 90 GB free at design time; a 13B revision is 55 GB. The HF hub cache holds 201 GB and Exp 4's gitignored kept activations 56 GB (sha-pinned on the record; nothing downstream reads them once 4c drops CKA). The 13B sweep wants ≈ 120 GB free. Which of the two is dropped is Michael's call; nothing is deleted without it. **Resolved 2026-09-18 on his word: both dropped, together with Exp 1/1b's checkpoint trees, Exp 2/2b/2c's activations (2f's eight pinned files kept), Exp 2's m2m3 log and five closed-experiment HF cache entries — 548 GB free; the itemised record, the rule applied and the post-deletion cold batteries (2f 11/11, Exp 4 12/12) are in `experiments/exp4c/PROGRESS.md`.**

## 8. Alternatives considered

- **4b's 4c as named — φ, T and the placebo p_cal on the two new runs as the primary:** kept as S4, rejected as the primary. 4b measured that instrument's resolution: a null SD of .25 over 26 cells and eligible placebo pools of 4–11. Two runs would halve the cells and leave the pools no larger; the modal outcome is NOT-DISTINGUISHABLE whatever the truth.
- **Preregistering the rank statistic as an analysis-only re-read of Exp 4's bytes (2e's route):** impossible honestly — the design session had to compute it to learn whether an instrument without 4b's limit exists, and the number is known. Disclosed instead, and used as the known-answer gate.
- **A shape-matched primary on the non-arithmetic cells:** not adjudicable — six tasks in three families; a family-block flip tops out at p = .125, a rung-level one at .0156. It is the licence modifier, not the test.
- **Pythia 12b's eight scored checkpoints (2g) as a third run:** ≈ 10 h and 190 GB for up to nine cells on a coarse grid, the same tasks and families (no new blocks, so the primary's resolution does not move). Named, not recommended (dial g).
- **New flat or new option tasks to widen the comparator pool:** each needs a generation sweep along a 7B–13B run to certify that it never performs or when it does (2l's sweep was 35 h). The right experiment if 4c lands TYPE-BOUND; out of scope here.
- **Not running it (dial a's alternative):** the design session already moved the question — the rank instrument exists, the pooled signal is there on four runs, and it is type-bound. What is missing is any of it on data the designer has not seen, and that is the only thing 4c buys.

## 9. What Experiment 4c does not claim

No forecast — the outcome is known. No statement about "tasks" in general from nine non-arithmetic cells on six tasks; no type-matched comparison exists for them on this battery, so a TYPE-BOUND result cannot distinguish "option and string tasks lead" from "option and string tasks align faster than modular arithmetic before they perform" beyond what S5 and S7 show descriptively. No effect size in Exp 4's units: q is a rank. No mechanism. Nothing about other positions, site families, k, references or models. A NOT-REPLICATED is not evidence of absence (§4). The discovery-set numbers are not evidence of anything.

## 10. Dials — RULED 2026-09-18 ("Proceed with 4c"): every dial as recommended (recommendation first in each)

- **(a) Run it, given §4's declaration?** Recommended: **RUN, with the declaration printed** — the Mac is idle, the cost is compute and bandwidth, the one thing the program lacks on this question is a reading on unseen data, and the secondaries (S4's continuity with 4b, S5, S7, S10) are informative in every world. Alternative: STOP here and record §2 in `experiments.md` as 4b's addendum; defensible, since two outcomes in three are uninformative between the hypotheses.
- **(b) The primary statistic:** the pre-clear growth rank U (§3.3). Alternative: 4b's φ / p_cal (§8).
- **(c) The primary null:** the exact family-block sign flip; rung-level and placebo printed beside it. Alternative: the placebo p as the primary (finer resolution, 4b's idiom, less conservative on the discovery set).
- **(d) Worlds by p alone, α .01 / .05 as in 4b, no effect bar, REVERSED named.** Alternative: a one-sided .05 bar for REPLICATES on the argument that this is a directional confirmation of a discovered effect — not recommended; the program's α has been .01 throughout and the bar should not move to buy power (2d dial d).
- **(e) The type modifier as written (§3.5), arithmetic matched to arithmetic, U_nonarith without a p.**
- **(f) t⁻ = the last checkpoint before the clear; the window mean is S3.**
- **(g) Trajectories: 6.9b and 13B only.** Alternative: add Pythia 12b's eight checkpoints (§8).
- **(h) References: Exp 4's committed set tables, no reference loaded.**
- **(i) Two tags (`exp4c-preregistered`, `exp4c-closed`); no intermediate seal** — there is no eligibility stage to seal and the power record precedes the tag.
- **(j) Order and operations:** 6.9b first with the mlx servers up; 13B second with the text server down; the disk decision above.
- **(k) CKA dropped** (it needs kept reference activations and was attested, never re-derivable).
- **(l) The prompt-end position is the primary; question-end is S9.**
- **(m) Projection by family and by type, written after the tag, with the designer's discovery-set knowledge declared in its first paragraph.**
- **(n) Calibration bound: α_placebo more than twice the deciding bar → licence BOUNDED (§3.6).**
- **(o) One pre-committed change.**

## 11. Process

Three sessions: design (this) | build by SDD, each task reviewed | adversarial freeze, then a final whole-branch review. Carried forward by name: 4b's four process notes (stratum readings printed beside the pooled one — S1/S2 here; pool size in the power statement — §4 states |flat| per run and the family count; a null that cannot resolve the bar prints no p — §3.5; projections anchored on the frozen record); Exp 4's four (calibration grids bracket the quantity — moot, the null is data-free, and §3.6 measures the rule on the real dependence instead; a degeneracy fix traced to every consumer — §3.1; tolerances on every projected number; a secondary projected as a statistic must print that statistic); lesson 6 (§4's shape declaration); lesson 8 (every refusal a terminal); lesson 11 and checklist items 26–27 (import surface, disclosure events). Disclosed about the closed Exp 4 instrument, not edited: its frozen analyzer computes its verdict tree before its exit import check (`analyze_4.py:2322/2420`); 4c's tree is recomputed after the last failure can be appended. Process notes from the build, for the methods paper's call: a PRODUCER pins its own import surface, not only its consumers (the freeze's F-1 — the runner that writes every byte the verdict reads checked only the tag-bound blobs); a mutation tally is reproducible only from committed logs, a class-inferred kill being an attestation; a world cache is keyed on the content of every module that writes a world; the worlds-only mutation pass runs only the named killing test per label.
