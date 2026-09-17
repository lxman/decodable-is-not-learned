# Experiment 4b — adversarial freeze (session 3, 2026-09-17)

Fresh-eyes reviewer, cold, on `experiments/exp4b/` at base `0a87dc2e`
(the final-review fix wave's own state). The standing assignment,
verbatim from the program: find THE CLASS DEFECT — the way this
preregistered analyzer could deliver a wrong or manipulable verdict
with every gate passing — and close what is found ADDITIVELY (a new
refusal, pin, test, disclosure or record field; never an accepted dial,
never a change to a preregistered statistic or bar). Precedents read
first for the form: `experiments/exp4/FREEZE_CHECKLIST.md` (F-1, an
attested-vs-measured digest), `experiments/exp2n/FREEZE_CHECKLIST.md`,
`experiments/exp2j/FREEZE_CHECKLIST.md` (F-1, the import surface).

Zero model contact and zero network throughout. B-4 held: no placebo
quantity was computed against the real tree; every real-tree execution
used `run(stop_before="placebo")` or called a cold gate re-derivation
directly. Every one is listed in §D below and in the freeze report,
for design §2's own count.

Python `~/emergence-lab/.venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
from the repo root, `-p no:cacheprovider`. The environment carries no
`timeout(1)` binary and the session's foreground call cap is 600 s, so
runs longer than that were detached with `Popen(start_new_session=True)`
and polled with short `kill -0` checks — the brief's mutation-harness
pattern, extended to the slow world modules by necessity and disclosed
here rather than silently.

Baseline, measured cold BEFORE the freeze touched anything:

| battery | result |
| --- | --- |
| fast suite (`experiments/exp4b/tests/`, `-m "not slow"`) | **103 passed**, 55 deselected, 23.2 s |
| cold referent battery (`verify_referents_4b.py`, real tree) | **12/12** |
| world cache (`/private/tmp/exp4b_world_cache`) | present, 1.9 GB, `follows_seed3` + `leads_seed11` |
| mutants at base | 71 (36 hand + 35 AST totality sites) |

**Verdict on the assignment: the CLASS DEFECT WAS NOT FOUND.** The
primary chain is closed by construction and the freeze says how: every
input to `p_cal` is either a sha-pinned committed byte (the 7,639-file
manifest, re-verified at the freeze), a re-derivation gated against a
committed answer (gates 1–3, 5), tag-bound code (five blobs), or a
pinned import surface — and an independent exact enumeration of the
null's own distribution reproduced the Monte Carlo at every T (§B,
attack 6), so the wiring between them is right too. Seven findings were
found and closed, all additively. The two carried Important residuals
(NB-1, NB-2) are closed as freeze corrections to §5 secondaries with no
α claim. The most consequential finding is **F-3**: design §6's
NOT-DISTINGUISHABLE sentence asserts a fact about T*'s interval that
the analyzer printed unchecked, and which is FALSE in exactly the
direction the construction account predicts — a wrong licence with
every gate passing, if that world had obtained. Nothing preregistered
moved: `ALPHA_4B`, `MARGINAL_4B`, `B_4B`, `SEED_4B`,
`MIN_PLACEBO_TOTAL_4B`/`_PER_TRAJ_4B`, `EXT_MULTIPLES_4B`,
`N_SIM_EXT_4B`, `EXT_SEED_4B`, the null's construction, the tree, and
every §5 statistic are byte-identical to the fix wave's.

---

## A. Findings

### NB-1 — S4's flat side carried an n/(n−1) rescale that no construction warranted. CLOSED.

Carried to the freeze by the fix-wave re-review. The final review's
Important 3 read the flat side's leave-one-out increments as
"self-included, and therefore n/(n−1) too high relative to the rising
side", and the fix wave divided them by that factor.

**The defect.** Both sides are target-OUTSIDE-pool. A rising rung is
never a member of the flat pool that scores it (`R` and `flat` are
disjoint by `rung_sets_4`), and a placebo rung is left out of its own
leave-one-out pool. They therefore differ only in pool SIZE — n−1 rungs
behind the flat side's trend, n behind the rising side's. At matched
wobble scale σ the increment variances are σ²(1 + 1/(n−1)) and
σ²(1 + 1/n), so the RAW ratio's expectation is

    sqrt((1 + 1/n) / (1 + 1/(n-1))) = sqrt(1 - 1/n^2)

— 1 to within 1/(2n²): 0.07 % at n = 27, 0.26 % at n = 14. The division
inverted the bias, inflating the ratio by n/(n−1) = 3.8 % (n = 27) to
7.7 % (n = 14), in the direction design §4(i) reads as "the rising
rungs wobble more, so the placebo null is too narrow and p_cal is
anti-conservative" — a bias in the very diagnostic that exists to say
whether the null can be trusted.

**Why the build's own test agreed with the code.** `fakes_4b.
rising_rung_series` builds the rising rung as `mean(flat_a) + noise`,
i.e. on the pool's own REALIZED mean, so the full-pool trend cancels
exactly out of its excess and the rising side loses the
−Δ(mean of every flat ε)/n term a real rising rung keeps. On that
construction the raw ratio's expectation is sqrt((n−1)/n), and an
n/(n−1) rescale brings it to 1 — the fix looked like a correction
because the fixture had been built to match it.

**Closure (additive).** The division is dropped; `rms_flat` is the raw
leave-one-out RMS and is what `ratio` divides. `rms_flat_loo` (the same
quantity under its build-time name) and `loo_scale_factor` stay as
DISCLOSURE fields — nothing divides by them — and the residual
pool-size expectation is printed per trajectory as
`pool_size_expected_ratio`. `S4_COMPARED_NOTE_4B` states what is
compared, in the record's `compared` field and on VERDICT.txt's S4
line, with the pre-clear-window-vs-whole-grid asymmetry disclosed
beside it. New tests: a bit-exact `rms_flat == rms_flat_loo` pin (which
a reinstated division fails deterministically), and a calibration test
over 60 pooled `fakes_4b.matched_scale_world` trajectories at n_flat=5,
where the rescale's 25 % bias is far outside the bound. Two mutants
(the reinstated rescale; a faked `rms_flat_loo`).

### NB-2 — S1's reading label was two-sided where design §5 is one-sided, and dropped §5's own conjunct. CLOSED.

**The defect.** Design §5 S1: "Read: same shape (means within .05) or
drift-like (placebo mean BELOW the iid mean by more than .05, WITH the
per-index table S3 rising)." The fix wave's ruled addition r2 labelled
every |difference| > .05 "drift-like". So a placebo null mean ABOVE the
iid mean — the opposite direction, no accumulating drift at all — would
have been printed in VERDICT.txt as "drift-like", i.e. as S1's own
evidence that "the wobble accumulates and Exp 4's arm was the wrong
shape" (design §3.5). The S3 conjunct was absent entirely, and the .05
was a retyped literal.

**Closure (additive).** `analyze_4b.s1_reading_4b` implements §5's rule
with four labels (`S1_READINGS_4B`): §5's two, plus the two cells §5
does not license, named rather than folded into one of its own —
`"above-iid"` and `"below-iid, S3 not rising"`. `None` only when a null
mean is unavailable. The conjunct's rule is made exact in
`placebo_4b.s3_pooled_rising_4b` and stated in its docstring: at least
two of the five pooled c/(G−1) bins carry draws, and the LAST such
bin's pooled mean of placebo φ exceeds the FIRST's by more than
`S1_SHAPE_TOL_4B` (= .05, §5's own tolerance for the same-shape half;
§5 names no second one). Monotonicity across every non-empty bin is
printed beside it as `bins_nondecreasing`, descriptive and never the
rule — five bins estimated from at most |P_M| rungs are too coarse for
a monotonicity test, design §4(iii)'s own point. One fast test per
label; the at-the-bar case is bit-exact (0.0 → 0.05 is the one pair
whose float difference is exactly the tolerance). Four mutants.

### F-1 — the placebo screen's endpoint input is a DIFFERENT FILE from the real rule's, and 4b never measured their identity. CLOSED.

This is the brief's own class-defect item 3 ("the pia identity"),
attacked and found real but inert.

**The defect.** `eligibility_table_4` — the rule design §3.2 says the
placebo eligibility is "Exp 4's rule (ii) with the leave-one-out
quantities" of — reads its endpoint per-item alignments from the
REFERENCE-stage unit `results/reference/endpoint_<traj>/`. The placebo
pool reads them from the SWEEP unit
`results/sweep/<traj>/step<endpoint>/`, because `run()` feeds
`placebo_pool_4b` the alignment series' own `per_item` arrays (Task 2's
carried note: `placebo_pool_4b`'s series/pia consistency refusal
requires it). `battery_4.reference_dir` and `battery_4.unit_dir` are
different paths: the same checkpoint computed twice. Their byte
identity is exactly what makes the placebo screen the analogue of the
real rule — and nothing in exp4b measured it. `gate1.json` (which
attests it) is sha-pinned in the manifest and **never read**; no exp4b
gate compares the two directories to each other. Gate 1 pins the sweep
side (through T), gate 2 pins the reference side (through the
eligibility table), and neither compares them: a tree whose two
endpoint units were never identical — a resumed campaign, a loader that
resolved the wrong revision — would pass both, with P_M (which flat
rungs enter the null) screened on one endpoint and the real cells on
the other.

**What kept it inert, stated plainly.** Exp 4's own closed analyzer DID
measure it from bytes and gated on all four agreements
(`experiments/exp4/analyze_4.py`, "4 gate 1 `<traj>` re-derivation",
its own I-6 closure), over exactly the bytes exp4b's manifest pins. So
on the committed tree this was an INHERITED measurement, not an open
channel — the finding is that 4b rested its own analogue claim on
another experiment's gate.

**Closure (additive).** `analyze_4b.gate6_endpoint_identity_4b` calls
Exp 4's own frozen `battery_4.gate1_rederive_4` unmodified for all four
trajectories and requires all four agreements (per-rung `sets` bytes,
the two records' per-rung `activation_sha256`/`attested_sha256`,
`tensor_digest`), as Exp 4 required them. Wired as gate 6,
unconditional (it needs only `root4`), wrapped in `collect_total_4b`,
refusing the verdict on disagreement; printed in VERDICT.txt; and
re-asserted cold as `verify_referents_4b.py` check 13. Cost ~0.01 s
warm for 4 × 34 × 2 files. Real tree: **13/13, 136 rung comparisons,
all four agreements per trajectory.** Three mutants.

### F-2 — p_cal is a Monte Carlo estimate read against two bars with no tolerance. CLOSED (disclosure).

**The defect.** `p_cal = (1 + #{T_b ≥ T_4}) / (B + 1)` over B = 10,000
seeded battery draws, and design §3.7's tree reads it against .01 and
.05 as hard bars. Its own resolution is the binomial SE
sqrt(p(1−p)/B) — .00099 at p = .01, .00218 at p = .05 — so a p_cal
within about one SE of a bar is decided by the draw rather than by the
data, and nothing in the record said so. The program's own lesson twice
over (2l process note 1, "a named disconfirmer needs a tolerance"; 2n,
"a bar-clear count needs a tolerance at the bar"), applied here to 4b's
own primary.

**Executable demonstration (§B attack 3).** On a synthetic pool at this
design's own sizes (|P| 27/16/14/16, n 4/9/4/9, the committed clear
multisets, G 21/21/26/24), p_cal over twelve seeds ranged .0823–.0911
with SD **.00274** — the binomial law's own .0028 at that p, to the
third decimal. The seed is fixed pre-tag in `battery_4b.SEED_4B` and
tag-bound, so this is a RESOLUTION disclosure, not a manipulation
channel; it is listed as such in §C's degrees-of-freedom table.

**Closure (additive).** `placebo_4b._mc_se_4b` and
`bar_margins_4b`: `p_cal_mc_se` on the `p_cal_4b` block, and a
`mc_resolution` block on the primary giving each bar's margin in MC-SE
units plus `within_2_mc_se`, the list of bars the estimate sits closer
to than 2 SE. Printed in VERDICT.txt with its note. Two mutants.

### F-3 — design §6's NOT-DISTINGUISHABLE licence asserts a fact the analyzer printed unchecked, false in the construction account's own direction. CLOSED.

**The defect.** §6's NOT-DISTINGUISHABLE sentence, which the fix wave's
r1 quotes verbatim into the record and VERDICT.txt, says the essay
"states that the task-specific lead did not separate from the flat
tasks' drift under the same selection (p_cal, T* with its interval
covering zero)". The interval is `[T_4 − Q.975(T_b), T_4 − Q.025(T_b)]`.
Its lower end is ≤ 0 whenever p_cal ≥ .05, but its UPPER end is
negative whenever T_4 sits BELOW the placebo null's 2.5th percentile —
and that world is still NOT-DISTINGUISHABLE (p_cal ≥ .05 says nothing
about the lower tail). That is exactly the direction the construction
account predicts (design §3.2: "the construction account predicts T
well BELOW that distribution"), and design §9 promises that under
NOT-DISTINGUISHABLE "the construction account is still not licensed".
So in the one world where the direction matters, the analyzer would
have printed, as the licensed sentence, a parenthetical the data
contradict — with every gate passing.

**Closure (additive).** `analyze_4b.interval_covers_zero_4b` checks the
clause (inclusive at both edges, `None` when there is no interval); the
licence block carries `interval_covers_zero`, and when it is False in
the NOT-DISTINGUISHABLE cell it also carries
`LICENCE_INTERVAL_BELOW_NULL_4B` — which grants nothing, names the cell
§6 did not, and hands the sentence to Michael (2n's process note 1:
enumerate every licence cell the analyzer distinguishes and call one).
Both are printed in VERDICT.txt. A doc slip for ratification adds the
sub-cell to §6. Six-case fast test; one mutant.

### F-4 — VERDICT.txt disclosed neither `pins_active` nor gate 4's skip, so a TEST-ONLY invocation read identically to the sanctioned run. CLOSED.

**The defect.** `run(power_gate="skip")` is TEST-ONLY and leaves
`gates["4"] = {"pass": True, "skipped": True}`; `referents_sha=False`
and `imports_pinned=False` switch off the manifest and the import
surface; `frozen_check=lambda: None` switches off the `exp4-closed`
pin; `expected_n_sim` can be injected. Every one of these is recorded
in `pins_active` — and `write_verdict_txt_4b` printed none of them, nor
any gate's qualifying flags: its gate block read `gate 4: pass=True`
whether the power record had been reproduced byte for byte or not
reproduced at all. A reader of the committed VERDICT.txt could not tell
the sanctioned run from a stubbed one. Exp 4's own
`write_verdict_txt_4` does not print `pins_active` either — precedent
noted, not followed.

Also closed here, same shape: the read sweep's own coverage claim. The
plain sweep stops before the placebo stage (B-4), and the fix wave's
`--world` mode sweeps the FULL pipeline but on a synthetic tree, where
every exp4-tree read lands in the `world_artifact` bucket instead of
being checked against `referents_4b.json` — so neither answered "is
every REAL-tree file the full pipeline reads in the manifest?". The
placebo stage and S1 open no files (their inputs are already in
memory); S6 is the one stage that adds real-tree reads.

**Closure (additive).** VERDICT.txt gains a `Pins active` block and
per-gate qualifying flags (`skipped`, `identical`, `cells_match`,
`t_match`, `n_rungs_checked`); `pins_active` gains `numpy_version` and
`scipy_version` (nothing gates on them — gate 1's bit-for-bit T
re-derivation is the stack check — but "which numpy decided this"
belongs in the record, as every campaign experiment in this program
records its torch/transformers versions). `read_sweep_4b.py` gains
`--levels` and `--levels-maxpairs`, real-tree modes that sweep S6's
five readers under the wrappers (S6 is no placebo quantity, so B-4
permits it; values are never printed, shapes and seconds only). Results
in §B attack 9: **(e) UNPINNED = 0 and (f) = 0 on both**, with the
`gitignored_attested_unused` 136 in each, now labelled in the module
docstring as the synthetic tree's own copies wherever `--world` reports
it.

### F-5 — a verdict.json could outlive the two records it attests. CLOSED.

**The defect.** `verdict.json` carries `placebo_record_sha256` and
`power_ext_sha256` (B-6), and the write block wrote `verdict.json`
FIRST, then the two companions. A write failure after the first write —
a full disk, a `results` path that is a file, a read-only tree — leaves
a committed verdict attesting two records that do not exist, and the
failure escapes `run()` uncaught (the writes are outside every
`collect_total_4b`).

**Closure (additive).** The companions are written first,
`verdict.json` last, so "verdict.json exists" implies "its attested
companions exist", whatever fails. The writes stay unwrapped
deliberately: a write failure must be loud, not a verdict. A fast test
pins the order, including a source-level assertion that `run()`'s own
write block keeps it.

---

## B. The attack list

Every item attacked EXECUTABLY — a synthetic world, committed bytes, or
a hand fixture. No placebo quantity was computed on the real tree
(B-4); timing runs recorded seconds only.

| # | brief item | what was executed | disposition |
| --- | --- | --- | --- |
| 1 | the placebo construction's degrees of freedom | the enumeration in §C, each entry measured or proved | **CLEARED with a disclosure** (F-2 for the seed/B; §C for the rest) |
| 2 | does any placebo quantity leak into a gate or a refusal? | read of every gate's input set; the three refusals that read a placebo quantity classified (support vs value) | **CLEARED with a disclosure** (below) |
| 3 | is the LOO SE + eligibility bar the EXACT analogue of Exp 4's rule (the pia identity)? | the two loaders' paths traced; `gate1_rederive_4` run on the real tree and on both cached worlds; hand-fixture perturbation of one rung's sweep npz | **F-1, CLOSED** |
| 4 | the flip null over duplicated rungs | a hand battery: one rung drawn twice on one trajectory AND on a second trajectory | **CLEARED** — `primary_4` groups by rung name, so all three cells take ONE sign: 5 cells, `n_rungs` 3, `n_flips` 2³ = 8, per-rung φ sums {r1: 3.0, r2: −1.0, r3: 0.5}, max attainable flipped T = 4.5/5 = 0.9 |
| 5 | totality over Exp 4's tree shapes | the build's 39-site AST battery re-counted and re-run; the write path attacked separately | **CLEARED** (39/39 sites; F-5 closed the write path) |
| 6 | the import surface (2j F-1) | two lines injected into `experiments/exp4b/__init__.py` (a pinned residual); a NEW `experiments/__init__.py` created, making the namespace package regular | **CLEARED** — both REFUSE: "imported module drifted from its pin" and "unpinned module on the import surface: experiments". `experiments` is a namespace package (`__file__ is None`), so no code can hide there without becoming a regular package, which the scan then refuses. 67 `experiments/*` modules imported, 63 covered, 4 drift-pinned, 0 neither |
| 7 | known-answer gates: compared or attested? | each gate's comparison read and re-run cold on the real tree | **CLEARED** — every one compares: T_4 `==` bit for bit (0.6102443158323546), the 26 cells on (traj, rung, φ, t_clear), the eligibility table through `_compare_eligibility_4`, λ̂ per trajectory exactly (7.3195/7.3043/6.2345/6.4691), gate 0's four fractions (.9545/.9893/.9902/.9911), `power_4.json` byte for byte (21.3–21.5 s, `identical=True` on every freeze run), the cas T (0.5814874459089997), the best-site mean φ (0.5784688004650052), and now the endpoint identity (F-1) |
| 8 | the tree: every cell reachable; the 1e-15 band; the [.01,.05) boundaries | the build's parametrized tree tests (incl. p_cal exactly .01 and exactly .05) re-run; the forced-p_cal world tests re-run on the cached follows world | **CLEARED** (see §E) |
| 9 | the read sweep's (e) bucket; manifest coverage | real-tree `--levels` (stop_before + ladder/twins/ceiling/within_family) and `--levels-maxpairs` (max_over_pairs, 390 s) | **F-4, CLOSED** — 7,371 and 6,751 distinct paths, **UNPINNED 0**, (f) 0, `gitignored_attested_unused` 136 on both |
| 10 | determinism across processes | the two-subprocess fixture on the cached follows world, after the closures | **CLEARED** (see §E) |
| 11 | S1's extension arms | the equivalence-at-uniform-scale gate, the single-stream contract, the per-trajectory λ̂ mapping and p_iid's band re-run from the build's own tests | **CLEARED**; the label itself was **NB-2** |
| 12 | S6's site-0 exclusion by LAYER LABEL on both sides; the ladder's known headline | `max_pair_alignment_4b` read and its planted-table tests re-run; `ladder_4b`'s `known_in_advance` flag confirmed | **CLEARED** — `kept_positions_4b` filters on the layer label, both sides are filtered before the cross product, and the winning pair is reported in layer labels |
| 13 | the disclosure ledger | every pre-tag real-tree execution collected from the task reports, the fix-wave report and this session | **§D** |
| 14 | *(freeze's own)* an independent re-derivation of the null | the EXACT distribution of T_b enumerated from the design doc — every (picks, order) outcome over two trajectories, 864 weighted outcomes, 54 distinct T — against `draw_batteries_4b` at B = 400,000 | **CLEARED** — exact vs MC: 1.000000/1.000000, .875000/.874900, .472222/.471869, .208333/.208689 (≤ 0.6 MC SE at every T); the two zero-support cases read the add-one floor 1/(B+1) as they must. The plain-mean weighting recombines from the per-trajectory means to 2.2e-16 |
| 15 | *(freeze's own)* is the C_M permutation a live choice? | 20,000 batteries with and without the permutation, KS two-sample | **CLEARED, inert** — D = .0049, p = .97: with iid with-replacement picks the permutation is a distributional no-op. It consumes rng and nothing else |
| 16 | *(freeze's own)* which way does the with-replacement dial cut? | 20,000 batteries drawn with and without replacement on the same pool | **CLEARED, conservative** — with replacement the null is WIDER (SD .980 vs .906, q99 .841 vs .804) and p_cal LARGER (.0885 vs .0834): the ruled dial (b) is the conservative one for a CALIBRATED reading |
| 17 | *(freeze's own)* α_placebo's denominator and flip regime | `verdict_tree_4`/`primary_4` read on battery cells; `n_distinct_rungs` measured | **CLEARED with a disclosure** — a battery drawing fewer than `MIN_RUNGS_4` = 3 distinct rungs reads NO-CONVERGENCE and cannot read LEADS, yet counts in α_placebo's denominator; and a battery's flip regime (exact ≤ 20 distinct rungs, sampled above) need not be the real verdict's (`exact`, 15 rungs). Both were already in the record (`world_counts`, `flip_method_counts`, `real_regime`); they are now printed in VERDICT.txt's calibration block |
| 18 | *(freeze's own)* can a NaN or an unwritable output turn a verdict into a raise? | `_jsonify_4` read (NaN/±inf → `None`, so the `allow_nan=False` dumps cannot raise on a zero-cell trajectory's `per_traj_mean`); the write path attacked | **CLEARED** for the serializer; **F-5** for the order |
| 19 | *(freeze's own)* does the attested, gitignored npz surface reach a verdict quantity? | `collect_4.load_ref_tables_4` read; `sets_question_end`/`sets_pooled` grepped across `experiments/exp4b/` | **CLEARED** — `sets` is sha-checked against the record and the attested file populates only the two other keys, which no exp4b call site reads (0 hits). The 136-read bucket stays a disclosure |
| 20 | *(freeze's own)* is the stack pinned? | gate 1's exact-equality re-derivation read as the stack check; versions added to the record | **CLEARED with a disclosure** (F-4) — a numpy/BLAS reduction-order change would move the series and fail gate 1's bit-for-bit T |

**Item 2, in full.** No gate reads a placebo quantity: gates 1–3 and 5
compare re-derivations against committed records, gate 4 is a byte
comparison of `power_4.json`, gate 6 is a byte comparison of two unit
directories. Three refusals downstream do read the null, and they
divide cleanly:

* the design §4 feasibility floor (`total_eligible < 8`), the
  per-trajectory deficit, and `draw_batteries_4b`'s "no eligible
  placebo rung on `<traj>`" read the null's **support** (counts), which
  design §3.6 sanctions in as many words;
* `per_traj_4b`'s NaN refusal is also support (a trajectory with real
  cells must have n > 0);
* `draw_batteries_4b`'s "placebo φ undefined for `<traj>`/`<f>` at
  c = `<c>`" reads a **value** — it fires when an eligible placebo
  rung's `x_end` is exactly 0, which requires SE exactly 0. Design
  §3.6's feasibility rules speak only of counts, so this one is
  disclosed here: it is collected by `collect_total_4b` and delivered as
  INSUFFICIENT_DATA with its reason verbatim, never a raise, and it
  cannot fire on a rung whose item bootstrap has any dispersion at all.

---

## C. The placebo construction's degrees of freedom (brief item 1)

Design §2 is explicit that the preregistration "does not protect
against a construction chosen with T_4 in view". The freeze's job is to
enumerate what remained free after the dials were ruled, and to say for
each whether a designer who knew T_4 = .6102 could have chosen it after
the fact. The protection that matters is B-4, verified: **no placebo
quantity has ever been computed on the real tree**, so no construction
choice could have been steered by a realized p_cal. Every real-tree
execution in §D used `stop_before="placebo"` or a cold gate
re-derivation.

| choice | pinned by | free? | direction, if a designer had known T_4 |
| --- | --- | --- | --- |
| P_M's membership (the one-sided 2-SE bar) | `an.SE_MULTIPLE_4` (frozen exp4), dial (d) ruled pre-build; bit-exact boundary tests | ruled, not free | the live one in principle: which flat rungs enter the null. Dial (d)'s alternative (two-sided) would ADMIT rungs with x_end ≤ −2 SE, whose φ has a sign-flipped denominator; not obviously directional, and unmeasurable in advance under B-4 |
| leave-one-out vs full pool (dial c) | proved INERT: x_full = ((n−1)/n)·x_loo pointwise, and both φ and the 2-SE bar are scale-invariant | **not a live choice at all** | none. The only statistic the factor touches is S4 (NB-1) |
| the with-replacement draw (dial b) | dial ruled pre-build; §B attack 16 | ruled | measured: with replacement is CONSERVATIVE (wider null, larger p_cal). The ruled dial is the one that makes CALIBRATED harder |
| the C_M permutation | §B attack 15 | inert | none — a distributional no-op given iid picks (KS p = .97) |
| B = 10,000 (dial e) | tag-bound constant; `primary.B` recorded | ruled | sets p_cal's resolution, not its value; F-2 discloses the resolution |
| `SEED_4B` = 0 | tag-bound constant; recorded in the placebo record | ruled | **the one seed-shopping channel**: ±.0027 at p ≈ .09, ±.001 at the .01 bar (§B attack 3). Enough to cross a bar only within ~1 MC SE of it — which is what F-2 now prints |
| the tie band 1e-15 | fast test | inert | none: it can only bite if a placebo battery's T equals T_4 to 1e-15, which no draw from a different rung set produces |
| the plain mean's implicit weights (4/9/4/9) | matched to the real T by construction; re-derived in §B attack 14 to 2.2e-16 | not free | none |
| the two tree bars (.01/.05) | dial (e) ruled; the program's α | ruled | F-2's tolerance disclosure is the only addition |
| the feasibility floors (8 / 3) | tag-bound constants | ruled | they can only refuse, never move p_cal |

---

## D. Disclosures

1. **Every pre-tag real-tree execution** — the count design §2 must
   carry — is tabulated in the freeze report
   (`.superpowers/sdd/2026-09-16-exp4b-build/freeze-report.md` §5):
   **34** across Tasks 5–6, the fix wave and this freeze, of which 11
   are `run(stop_before="placebo")` calls (each containing one gate-4
   power-record reproduction, 20.9–21.9 s, `identical=True` every time).
   No placebo battery or null was ever drawn against `battery_4.EXP4`.
2. **Known preregistered quantities.** S6(a)'s ladder headline was
   known before the design was written (design §2 says so). S6(e)'s
   pooled φ = 0.6130906109635486 became known at Task 5's timing run
   and is disclosed in the ratification notes; the freeze re-ran
   `max_over_pairs_4b` under the read sweep and printed only
   `n_cells`/`n_phi`/seconds. The projection may claim neither.
3. **Retyped known-answer literals** — four groups, not the two the
   ratification notes list: `DESIGN_CLEAR_MULTISETS_4B` (battery_4b),
   `BEST_SITE_MEAN_PHI_PIN_4B` = 0.578468800465005
   (verify_referents_4b), and in `verify_referents_4b` check 8 the
   zero-excess multiples `[1.0, 1.5, 2.0, 3.0]` and the realized-α
   figures `{.019, .144, .246, .264}` (design §2's own literals). All
   four are pins checked against committed bytes; none is an input to
   any statistic.
4. **α_placebo's denominator** includes batteries Exp 4's own tree
   reads NO-CONVERGENCE, and the placebo batteries' flip regime need
   not match the real verdict's (§B attack 17). Both are in the record
   and now in VERDICT.txt.
5. **S4's residual pool-size mismatch** (NB-1): the two sides differ by
   n vs n−1 behind the trend, expectation sqrt(1 − 1/n²), printed per
   trajectory. The windows also differ in length (pre-clear only vs the
   whole grid), disclosed and uncorrected by design.
6. **S8's i = 0 point** is degenerate by construction (0/x_end on both
   sides, quantile 1.0); carried from the build's deferred minors.
7. **The environment**: no `timeout(1)` binary and a 600 s foreground
   cap, so the slow world modules and the mutation harness ran detached
   with polling (§E).

---

## E. Batteries after the closures

| battery | result |
| --- | --- |
| fast suite (`-m "not slow"`) | **124 passed**, 55 deselected, 24.4 s (was 103) |
| cold referent battery (`verify_referents_4b.py`, real tree) | **13/13** (check 13 = F-1's gate 6: 136 rung comparisons) |
| read sweep, real tree, `--levels` | 7,371 distinct paths, **UNPINNED 0**, (f) 0, attested-unused 136; gates 1–6 all PASS |
| read sweep, real tree, `--levels-maxpairs` | 6,751 distinct paths, **UNPINNED 0**, (f) 0, attested-unused 136 |
| import scan (`import_scan_4b.py`, real tree) | 3 exp4b-own residual modules; `IMPORTED_SHA256_4B` re-pinned after check 13 (its own drift test caught the stale hash first) |
| mutants | **83** (71 + 12 for the freeze's own closures), every target text unique |
| gate 6 on both cached worlds | PASS, 136 comparisons each (the slow world tests still reach their terminals) |

(The slow world/totality/determinism results are recorded in §F.)
