# Experiment 4b — the calibration successor: how far above the drift-and-selection null does the lens lead sit?

**Status: DRAFT — session 1 (design) of three (design | build | freeze), written 2026-09-16 on Michael's word ("Design the calibration successor."). §10 dials await his ruling. ANALYSIS-ONLY on Experiment 4's committed bytes: zero model contact end to end.**

Predecessor: `experiment-4-design.md` (CLOSED 2026-09-16, VERDICT LEADS at T .6102, tag `exp4-closed` at 12d747df). Exp 4's §6 licence was claimed only where the LEADS rule's realized α at the observed λ̂ is below .05, and the observed λ̂ (6.2–7.3) fell above the zero-excess arm's grid (top multiple 3.0, realized α already .264), so the essay's sentence went out bounded to "above the selection-inflated null" with the strength of the lead unquantified. 4b quantifies it, on the bytes already on disk, with a null built from the flat rungs' own drift.

## 1. The question

Experiment 4 measured, for 26 eligible (trajectory, rung) cells on 15 rungs across four training runs, the fraction φ of each rung's endpoint task-specific alignment excess that was already in place before the rung first cleared the argmax bar, and read the mean, T = .6102, against a rung-level sign-flip null. That null tests the SIGN of the pre-clear excess; it does not say how far .61 sits above what a rung with NO task-specific structure would show under the same measurement — because φ's null value is not 0 but ≈ ½ (the shared first-checkpoint baseline sits in numerator and denominator, and eligibility selects a large positive denominator), and because the realized between-checkpoint scatter of the flat rungs' excess is six to seven times the item-sampling noise the power record's null arm was scaled to.

4b asks one question: **is Experiment 4's committed T distinguishable from the distribution of T that the flat rungs themselves produce when they are put through the identical measurement — the same excess, the same eligibility rule, the same clear positions — as if they were the rising rungs?** The flat rungs are the null realized: rungs whose task-specific structure never clears the bar, drifting with the actual checkpoint-to-checkpoint wobble, selected by the actual rule. Their T distribution is the calibration Exp 4 lacked.

Worlds (§3.7): **CALIBRATED** (T_4 beyond the placebo null at the program's α), **MARGINAL** (beyond it at .05 but not .01), **NOT-DISTINGUISHABLE** (inside it), with INSUFFICIENT_DATA the refusal terminal. Each carries a licence written in advance (§6). In every world the construction account's cell — task-specific agreement arriving with performance, φ ≈ 0 — is restated: Exp 4's own sign-flip reading against it (T .61, p₊ 4.9e-4) is repeated verbatim, and the placebo null's position relative to zero is printed beside it.

Beside the primary, the parametric arm Exp 4 froze is completed at the observed λ̂ (§5 S1), so Exp 4's §6 condition is also read literally; and the level descriptives that Exp 4's frozen record computes with the degenerate hidden-state-0 constant inside them are recomputed with it excluded, preregistered (§5 S6).

## 2. What 4b inherits, what it changes, and what it cannot be

**Inherited, frozen, blob-pinned to `exp4-closed`:** Exp 4's instrument — `analyze_4.py`, `battery_4.py`, `metric_4.py`, `collect_4.py`, `power_4.py` — imported by name and sha-checked at entry and exit (2j's lesson, checklist item 26); its committed campaign bytes — the 92 sweep units, the 23 reference-stage units, the eligibility table, the power record, `verdict.json` — every file read listed in a pinned manifest; its rung sets, grids, references, depth pairing, site family, position, k = 10, the item-bootstrap SE at 2,000 resamples, the one-sided 2-SE eligibility bar, the pre-clear-window rule (t_clear index ≥ 2), `trend_4`/`excess_4`/`phi_4`/`cells_4`/`primary_4` verbatim. 4b calls Exp 4's functions; it reimplements none of them.

**Changed:** nothing in the measurement. 4b adds a null (the placebo construction, §3.2), a statistic over it (§3.3), and descriptives (§5). Exp 4's verdict is not re-litigated: its LEADS stands as the reading of its own preregistered tree; 4b decides what that reading is worth against a null of the right shape.

**What 4b cannot be: a forecast, or a test on unseen data.** Every input is committed and known, INCLUDING TO THE DESIGNER. In particular the designer knows: T_4 = .6102 (CI95 [.325, .950]; per trajectory OLMo-2 7B .959, Comma .512, SmolLM3 .474, Pythia 2.8b .183); the 26 cells' φ and clear positions; λ̂ = 6.23 / 6.47 / 7.30 / 7.32; the zero-excess arm's realized α .019 / .144 / .246 / .264 at multiples 1 / 1.5 / 2 / 3; and one post-verdict descriptive computed for Exp 4's retrospective on 2026-09-16 from the committed tables — the Pythia size ladder with site 0 excluded (34 of 34 rungs rising with log parameters, median Spearman .89, mean level .198 at 70m → .317 at 12b) — which §5 S6 preregisters in its fuller form and which the projection may not claim as foresight. **What nobody has computed: the placebo null.** No flat rung has been put through the pre-clear-fraction measurement; no placebo battery exists; the null's mean, its spread and its dependence on the clear position are unknown, and p_cal with them. The preregistration protects one thing: that the null's construction — which rungs, which clear positions, how many draws, leave-one-out or not, which bar — is fixed before any of it is seen. It does not protect against a construction chosen with T_4 in view, and the doc says so; §10's dials are the construction, ruled before the build.

**Disclosure rule (checklist item 27):** every execution of the 4b analyzer against the real tree before the tag is a disclosure event, counted in this section at the freeze; the build's tests run on synthetic worlds and on Exp 4's committed bytes only through the known-answer gates (§3.6), which compute no placebo quantity.

## 3. Instrument

### 3.1 Inputs

For each trajectory M ∈ {pythia_2.8b, olmo2_7b, smollm3_3b, comma_7b}: the alignment series a_r(t) for every rung r of the battery over `GRID_4[M]` (21 / 21 / 26 / 24 points), depth-matched mean over the three cross-family references, at the prompt-end position, from the committed k-NN set tables through `analyze_4.alignment_series_4`; the per-item alignments at t_1 and t_end for the item bootstrap; Exp 4's rung sets (R_M, flat_M, transient_M) through `battery_4.rung_sets_4`; the eligibility table (`results/reference/eligibility_4.json`) with its `se` per rising rung and `se_at_end` per flat rung; the 26 committed cells with their φ, t_clear and t_clear_index (`verdict.json`).

### 3.2 The placebo null

A **placebo cell** is a flat rung f ∈ flat_M read exactly as Exp 4 reads a rising rung, with a clear position it never had:

    trend_{M,−f}(t) = mean over r ∈ flat_M \ {f} of a_r(t)               (leave-one-out pool)
    x_f(t)          = [a_f(t) − a_f(t_1)] − [trend_{M,−f}(t) − trend_{M,−f}(t_1)]
    φ_f(c)          = x_f(t_{c−1}) / x_f(t_end)                            for an assigned clear index c ≥ 2

The pool is leave-one-out so that f's own wobble is not subtracted from itself — the exact analogue of a rising rung, which is not in the pool either (the real cells' pool is all of flat_M; the one-rung difference in pool size is disclosed, not corrected).

**Placebo eligibility** is Exp 4's rule (ii) with the leave-one-out quantities: x_f(t_end) ≥ 2 × SE_f, SE_f the item-bootstrap SE of x_f(t_end) under the leave-one-out trend, 2,000 resamples, items resampled within f and within each pooled flat rung, neighbour sets not recomputed — Exp 4's bootstrap (`eligibility_table_4`'s construction) applied to f. The set of eligible placebo rungs per trajectory, P_M ⊆ flat_M, is fixed by the data (eligibility does not depend on c). Its size is not tabulated here (it is knowable from the committed bytes and is part of what the analyzer reads; §4's feasibility rules cover the small-P_M case).

**A placebo battery** reproduces Exp 4's design on placebo cells: for each trajectory M with n_M real eligible cells (4 / 9 / 4 / 9) and their real clear-index multiset C_M (Pythia {4, 7, 7, 12}; OLMo-2 {3, 4, 5, 5, 5, 6, 7, 9, 10}; SmolLM3 {2, 2, 4, 15}; Comma {2, 2, 2, 9, 10, 14, 19, 19, 21} — from the committed cells, printed here because the projection is graded on the null's shape at exactly these positions), draw n_M rungs from P_M with replacement and assign C_M to them in a uniformly random order; the battery's T_b is the plain mean of φ over its 26 placebo cells (trajectory weights 4/9/4/9 fall out of the count, as in the real T). B = 10,000 batteries, one seeded generator, the seed fixed in the build. Drawing with replacement keeps the cell count matched to the real design when |P_M| < n_M and lets a placebo rung carry more than one clear position, as a real rung carries cells on more than one trajectory; a rung drawn twice on one trajectory is one rung for the sign-flip null (§3.4).

**What the null represents.** Under "no task-specific agreement before the clear, only the general drift every rung shares", a rising rung's excess trajectory is exchangeable with a flat rung's, and the real T is one draw from the placebo distribution. The construction account (φ ≈ 0, the excess arriving at or after the clear) predicts T well BELOW that distribution; the lens account predicts T above it. The null's shape is the open question: under checkpoint-to-checkpoint wobble that is independent across steps, φ's null mean is ≈ ½ at every clear position (Exp 4's R-7 arithmetic); under drift that accumulates, it rises with the clear position — roughly the fraction of the grid elapsed — and the early-clearing OLMo-2 cells (indices 3–10 of 21) would sit against a much lower null than the late-clearing Comma cells (up to 21 of 24). The matched C_M carries whichever shape obtains into the battery-level null.

### 3.3 The primary statistic

    p_cal = (1 + #{b : T_b ≥ T_4}) / (B + 1)              T_4 = .6102443158323546, re-derived (§3.6)
    T*    = T_4 − mean_b(T_b)                              the calibrated lead, with the placebo interval
                                                           [T_4 − Q_{.975}(T_b), T_4 − Q_{.025}(T_b)]

p_cal is one-sided (the lens account's direction); p_low = (1 + #{b : T_b ≤ T_4}) / (B + 1) is printed as its two-sided complement, nothing more. No effect-size bar is set on T* (dial f): the world is decided by p_cal at the program's α, and T* is reported with its interval in every licensed sentence. **Per trajectory:** p_cal,M from the trajectory's own placebo means (the 10,000 batteries restricted to M's cells) against T_4,M — descriptive, and the naming rule of §6 reads it.

### 3.4 The realized α of Exp 4's LEADS rule under the placebo null

Every battery is also pushed through Exp 4's own decision: `primary_4` (the rung-level sign-flip null over the battery's distinct placebo rungs, exact up to 20 rungs, 10,000 sampled flips above; the rung-clustered bootstrap at 200 resamples as the power record used) and `verdict_tree_4`. α_placebo = the share of batteries reading LEADS. This is the number Exp 4's §6 asked for — the LEADS rule's false-positive rate at the scatter that obtained — computed on the real scatter rather than on an iid multiple of the item SE. It moves no bar in 4b (§6 says how it is carried).

### 3.5 The parametric completion (S1)

Exp 4's `power_4._simulate_zero_excess` — E_r = 0 for the whole candidate pool, iid Gaussian noise per grid point at scale × the measured SE, the eligibility bar at the unmultiplied SE, the tree re-applied per draw — is run on a fresh seeded stream at (i) the observed per-trajectory λ̂ (scale_M = λ̂_M: 6.23 / 6.47 / 7.30 / 7.32) and (ii) the grid {4, 6, 8, 12}, N_SIM = 1,000 per arm. Arm (i) gives α_iid, the realized α at the observed λ̂ in the frozen arm's own terms, and the iid null's T distribution, from which p_iid = P(T_iid ≥ T_4) and the iid null mean are read. The two nulls' means and SDs are printed side by side: where the placebo null sits below the iid null, the wobble accumulates (drift-like) and Exp 4's arm was the wrong shape; where they agree, it does not.

### 3.6 Gates (INSUFFICIENT_DATA on failure)

**Known-answer gates**, exact: (1) T_4 re-derived from the committed set tables through `alignment_series_4` → `trend_4` → `excess_4` → `cells_4` → `primary_4` equals `verdict.json`'s `primary.T` bit for bit, and the 26 cells' (traj, rung, φ, t_clear) equal the committed cells; (2) the eligibility table re-derived through `eligibility_table_4` equals the committed `eligibility_4.json` (Exp 4's own check, repeated); (3) λ̂ per trajectory re-derived through `lambda_hat_4` equals the committed calibration block; (4) the power record: `power_4.compute` re-run at the committed seed reproduces `power_4.json` byte for byte (the same stream, the same arms, the same four multiples) before the extension arms are drawn on their own stream — so the completion is provably the same machinery (dial g prices this gate's runtime); (5) gate 0 with site 0 excluded reproduces .9545 / .9893 / .9902 / .9911.

**Referents:** a manifest of every file 4b opens — Exp 4's sweep and reference units (set tables, records, alignment records), `verdict.json`, `power_4.json`, `eligibility_4.json`, the four upstream outcome records Exp 4 reads for its rung sets, 2c's battery and 2d's floors through Exp 4's loaders — sha256-pinned at the tag; a read sweep at the freeze (0 unpinned, campaign artifacts included this time, since they are closed); the import surface pinned (the five Exp 4 modules at their `exp4-closed` blob shas plus 4b's own, and the upstream modules Exp 4 imports, at their closed-tag shas).

**Feasibility rules** (§4): fewer than 3 eligible placebo rungs on a trajectory that carries real cells → that trajectory's placebo cells are drawn from what exists and the deficit is printed in the verdict (the null is narrower there than the design intends; disclosed, not corrected); fewer than 8 eligible placebo rungs in total across the four trajectories → INSUFFICIENT_DATA (the null cannot be built at the design's grain).

**Totality:** every loader refusal collected (`collect_total`), delivered as INSUFFICIENT_DATA with the reason verbatim; every tree shape a corrupted or truncated committed file can leave reaches the refusal terminal, never a raise (2d F-1, 2h F-1).

### 3.7 The tree

INSUFFICIENT_DATA (any gate or referent failure; the feasibility floor) → **CALIBRATED** (p_cal < .01) / **MARGINAL** (.01 ≤ p_cal < .05) / **NOT-DISTINGUISHABLE** (p_cal ≥ .05). Every cell the analyzer distinguishes is named (2n's process note 1); there is no effect bar and no sub-cell on T*. In every world the analyzer prints the construction-account statement: Exp 4's own sign-flip reading of T_4 against φ ≈ 0 (p₊ 4.9e-4, T ≥ .25), repeated verbatim, and the placebo null's .01 lower quantile — so a reader sees that under NOT-DISTINGUISHABLE the data agree with "drift and selection", not with "agreement arrives with performance". 4b adds no new test of the construction account; it says where its prediction sits relative to the null it built.

### 3.8 Pins and storage

Everything 4b writes goes under `experiments/exp4b/results/`: `verdict.json` (the primary, the placebo distribution's summary and its 10,000 T_b values, α_placebo, S1–S8, the gates, the pins), `VERDICT.txt`, and the parametric extension record. The placebo batteries are re-derivable from the seed; the T_b vector is committed so the p is checkable without re-running. Blob-bound tags: `exp4b-preregistered` (analyze_4b, battery_4b, placebo_4b, power_ext_4b), `exp4b-closed` at the verdict commit. No stage tags: nothing is sealed between the freeze and the analyzer because nothing is collected.

## 4. Cells and resolution

**Cells** are Exp 4's 26, unchanged; the placebo batteries mirror them. There is no power table — every input is fixed and known, and the experiment's own output is the null's resolution. The analyzer prints, in the null's own terms: the placebo null's mean and SD of T; Q_{.99} and Q_{.95} of T_b (the T that would have cleared each cell); the null mean of φ per trajectory and per clear index (S3); and, beside them, the iid arm's mean and SD at the observed λ̂. What is declared in advance is the reading rule: the world is p_cal's cell, and T* is reported with its interval whatever the cell.

**Where the design is weak, said now.** (i) The placebo null takes the flat rungs' drift as representative of a rising rung's non-task-specific drift. If a rising rung's representation wobbles more between checkpoints than a flat rung's for reasons that are not the lead — because it is changing more, full stop — the placebo null is too narrow and p_cal is anti-conservative; the reverse makes it conservative. S4 measures the two scatters (rising rungs' excess SD outside the pre-clear window against the flat rungs') and prints their ratio; the design does not correct for it. (ii) The placebo pool is small on three trajectories (14–16 flat rungs, fewer eligible), so the battery-level null on OLMo-2 and Comma (9 cells each) rests on few distinct rungs — the with-replacement draw keeps the count honest and the distinct-rung count is printed. (iii) The null's shape at a clear index is estimated from at most |P_M| rungs; the per-index table (S3) is coarse and says so.

## 5. Named secondaries (printed in every world; no α claim)

- **S1 — the parametric completion (§3.5):** α_iid and p_iid at the observed λ̂; the {4, 6, 8, 12} grid; the iid null's T mean and SD beside the placebo null's. Read: same shape (means within .05) or drift-like (placebo mean below the iid mean by more than .05, with the per-index table S3 rising).
- **S2 — per-trajectory and per-type calibration:** p_cal,M and T*_M with intervals for each trajectory; the same for Exp 4's three rung types (arithmetic / option / string), each type's placebo distribution built from the batteries' cells of that type.
- **S3 — the null's shape:** mean and SD of placebo φ per trajectory and per clear index c present in C_M (from the batteries), and the pooled null-mean-of-φ as a function of c/(G−1); per real cell, the calibrated excess e_(M,r) = φ_obs − mean placebo φ at the same (M, c), and the cell's placebo quantile. Read: flat in c (≈ ½ everywhere: wobble) or rising in c (drift).
- **S4 — the scatter ratio:** for each trajectory, the RMS between-step SD of the rising rungs' excess over grid points strictly before each rung's clear (the pre-clear window only, so no lead enters) against the flat rungs' RMS scatter (λ̂'s numerator); the ratio printed with its interpretation (§4 (i)).
- **S5 — autocorrelation of the drift:** lag-1 autocorrelation of the flat rungs' excess increments per trajectory, pooled over flat rungs; Read: near zero (independent wobble) or positive (accumulating drift). Together with S3 this is the mechanism reading behind whichever world obtains.
- **S6 — the level descriptives with hidden-state 0 excluded**, each with an item-bootstrap CI95 (2,000 resamples), computed from the committed set tables: (a) the Pythia size ladder — per rung and the global bank over 70m / 160m / 410m / 1b / 1.4b / 2.8b / 6.9b / 12b, Spearman with log parameters, the largest single step; (b) the untrained twins per rung; (c) the references' mutual ceiling per pair; (d) the within-family series (2.8b against 12b along the trajectory); (e) the max-over-pairs alignment with the degenerate (0, 0) pair excluded, per eligible cell, as the S5(a) reading Exp 4 could not produce. The (a) part's headline is known (§2) and is disclosed as such; (b)–(e) are not.
- **S7 — the two Exp 4 sensitivities, calibrated:** the clears-and-stays primary (T .5815) and the endpoint-best-site variant (T .5785), each against a placebo null built with the matching clear rule / site choice.
- **S8 — the pre-clear-window reading Exp 4's S11 hinted at:** for each real cell, the placebo quantile of x_r(t⁻)/x_r(t_end) at every grid index before the clear (a curve, not one number), so a reader can see where in training the real cell parts from the null.

## 6. Licences, written in advance

Bounded to: Exp 4's battery, trajectories, position, site family and rung grain; a preregistered reading on a known outcome and a known T, with the null the only unknown. Exp 4's verdict (LEADS) is not revised by any world below; what changes is the sentence it licenses.

- **CALIBRATED:** the essay's convergence sentence loses its bound — "bounded below rather than measured" and "above the selection-inflated null" are replaced by "above the null built from the flat tasks' own drift under the same selection, p = p_cal, a lead of T* (interval) beyond it" — and the scoreboard sentence follows; the lens reading of Huh et al. is a measurement at task grain with a calibrated p. Exp 4's §6 condition on the rule's realized α is read against α_placebo and stated either way: where α_placebo < .05 the Exp 4 licence is claimed in full; where it is not, the sentence adds that the preregistered decision rule's own false-positive rate at that scatter was α_placebo, and rests on p_cal. The naming rule carries over: the sentence names the trajectories at p_cal,M < .05 where fewer than two qualify.
- **MARGINAL:** the sentence reads "above the drift null at p = p_cal, short of the program's α; the lead T* (interval)"; the bound is replaced by a measured margin, no more. The scoreboard says "marginal".
- **NOT-DISTINGUISHABLE:** Exp 4's measurement is DEMOTED in the essay: the convergence paragraph keeps the disclosure that the test ran and states that the task-specific lead did not separate from the flat tasks' drift under the same selection (p_cal, T* with its interval covering zero); the scoreboard sentence is rewritten to say so; the lens claim's task-grain measurement retreats to Huh et al.'s global result plus the disclosure; `experiments.md` records the demotion beside Exp 4's section. What survives in every world: the construction account's cell stays excluded by Exp 4's own sign-flip reading (T .61 at p₊ 4.9e-4 against φ ≈ 0), and the sentence says so — "the agreement did not arrive with performance; whether it led the general drift is not distinguishable at this resolution".
- **INSUFFICIENT_DATA:** nothing changes in the essay; the reason is ledgered.
- **Any world:** S1–S8 in full in `experiments.md`; S6's site-0-excluded ladder replaces Exp 4's frozen S3 in the program record as the reading of the size axis, with the frozen number kept beside it as what the instrument printed; the known-input caveat verbatim in every sentence.

## 7. Run plan and model contact

**Zero model contact.** Inputs are committed bytes. Runtime: the placebo null is minutes (26 cells × 10,000 batteries, plus 10,000 sign-flip evaluations at up to 2^20 flips — vectorized, under half an hour); the per-rung leave-one-out bootstrap SEs are 2,000 resamples × up to 27 flat rungs × 4 trajectories on 500-item vectors, minutes; the parametric completion is five arms × 1,000 draws through the tree (Exp 4's power stage ran four φ-arms and four multiples on the same machinery; the build measures it); the power-record reproduction gate is one full re-run of that stage (dial g). Order: build (SDD) → adversarial freeze → ratification → tag `exp4b-preregistered` → projection sealed → analyzer ONCE, detached, on Michael's word → `exp4b-closed` → retrospective → close-out on his word. The projection is graded on the null's mean and SD, p_cal's cell and point, α_placebo against α_iid, S3's shape and S5's sign, and S6 (b)–(e); S6 (a) is disclosed as known and graded on nothing.

## 8. Alternatives considered

- **Replication on the two trajectories Exp 4 never touched** — Pythia 6.9b (2h's 23 scored checkpoints) and OLMo-2 13B (2l's 16) — with the calibrated instrument, where T is unknown to everyone: the natural next experiment (≈ 2 days of forward passes at 7B and 13B), named here as 4c and not folded in, because it answers a different question (does the lead replicate?) and its outcome is also known at item grain.
- **A parametric-only completion** (extending Exp 4's arm to bracket λ̂): kept as S1, not the primary — the arm's iid-per-step noise is an assumption the realized λ̂ already strained, and the placebo null needs no shape assumption.
- **A time-block permutation null** (circularly shifting the flat rungs' excess series): rejected — it destroys the t_1 anchoring that makes x_r(t_1) ≡ 0 and would test a different exchangeability.
- **A calibrated per-cell primary** (mean of e_(M,r) with its own null): equivalent at the battery level to p_cal with matched C_M, and it would put a second statistic beside T_4 where one is enough; kept as S3's descriptive.
- **An effect-size bar on T*:** rejected (dial f): with the null mean unknown, any bar written now would be either arbitrary or chosen with T_4 in view; the retrospective's boundary lesson says report the interval.

## 9. What Experiment 4b does not claim

No forecast: T_4 and the outcome are known. No claim about the size axis beyond S6's descriptive. No mechanism: S3/S5 say whether the drift accumulates, not why. No statement about other batteries, positions, site families, or models. Under CALIBRATED the essay's sentence is calibrated against the flat rungs' drift on this battery — it does not become a claim that the lead would survive on rungs whose non-task-specific drift differs from the flat rungs' (§4 (i)). Under NOT-DISTINGUISHABLE the construction account is still not licensed — Exp 4's sign-flip reading against φ ≈ 0 stands, and the placebo null's own lower quantile is printed beside it.

## 10. Dials — for Michael's ruling

- (a) **Primary** = the placebo-calibrated p of Exp 4's committed T (recommended), the iid-parametric p at the observed λ̂ as S1; or the parametric reading as primary with the placebo as secondary.
- (b) **Placebo battery** = n_M rungs drawn with replacement from P_M, the real clear multiset C_M permuted onto them (recommended); or all eligible placebo rungs per trajectory, weighted 4/9/4/9, each with an independent clear draw.
- (c) **Leave-one-out pool** for placebo rungs (recommended); or the full pool with the self-shrinkage disclosed.
- (d) **Placebo eligibility** = the one-sided 2-SE bar with the leave-one-out item-bootstrap SE at 2,000 resamples (recommended); or two-sided.
- (e) **B = 10,000** batteries, α = .01 for CALIBRATED, the MARGINAL cell at [.01, .05) (recommended).
- (f) **No effect-size bar on T*** — the world by p_cal only, T* with its interval in every sentence (recommended); or T* ≥ .10 as a second condition on CALIBRATED.
- (g) **Power-record gate** = full byte-identical reproduction of `power_4.json` before the extension arms (recommended, the build measures the runtime; if it exceeds four hours, fall back to a fresh-stream multiple-1.0 arm within Monte Carlo tolerance |Δα| ≤ .02, disclosed).
- (h) **Parametric completion arms** = the observed per-trajectory λ̂ plus {4, 6, 8, 12}, N_SIM 1,000 (recommended).
- (i) **S6 with site 0 excluded** = (a)–(e) as listed, each with an item-bootstrap CI95, (a) disclosed as known (recommended).
- (j) **S3/S5 as the mechanism readings** — the per-index null table and the lag-1 autocorrelation, both projected (recommended).
- (k) **Tags** `exp4b-preregistered` (blob-bound) and `exp4b-closed`, no stage tags (recommended).
- (l) **Naming rule** for the licensed sentence = trajectories at p_cal,M < .05, the sentence unqualified at two or more (recommended).

## 11. Process

Session 1 (this document) → dials ruled → session 2: build by SDD under `experiments/exp4b/` (battery_4b: pins, manifest, loaders through Exp 4's; placebo_4b: the null, the batteries, the flip evaluation; power_ext_4b: the completion; analyze_4b: gates, tree, secondaries, verdict; verify_referents_4b; tests incl. synthetic worlds reaching every terminal, a totality harness, a mutation battery, a determinism fixture across processes) → session 3: adversarial freeze (the class-defect hunt: the placebo construction's degrees of freedom, whether any placebo quantity leaks into a gate, whether the leave-one-out SE and the eligibility bar are the real rule's exact analogue, the flip null over duplicated rungs, totality over Exp 4's tree shapes) → ratification → tag → projection → analyzer once on Michael's word. Zero model contact at every step; every pre-tag execution on the real tree disclosed in §2.
