# Experiment 2b — Progress Ledger

Traceability ledger (process rule 8), from day zero. Design doc:
`../../experiment-2b-design.md` (status DRAFT, dial review accepted 2026-07-17;
freeze commit + tag `exp2b-preregistered` lands at M0 completion per Michael's
standing authorization at the Exp 2 closeout).

## Milestones

| Milestone | What | Status | Tests |
|---|---|---|---|
| M0 | Battery item files + oracles + starving splits + feasibility + `analyze.py` + power table; FREEZE | **COMPLETE + FROZEN 2026-07-19** (tag `exp2b-preregistered`): 24 scored candidates committed, 5 designed ejections recorded, power table committed, §7 rehearsal PASSED (both known-lookup worlds silent on real activations) | 94 ✓ |
| M1 | Inclusion: argmax at 410m/1b on all candidates; scored battery fixed | COMPLETE 2026-07-19: first pass 13/24 (< frozen floor 20, halted by design) → AMENDMENT #1 (12 harder candidates, Path B approved) → top-up 12/12 survive → **battery FIXED at n=25** (reviewed commit, approved by Michael) | 130 ✓ |
| M2 | Gates: known-absent (starved untrained), known-present, shuffled (binomial tolerances), ctrl_copy argmax | — | — |
| M3 | Stage 1: starved probes at 410m/1b, 5 seeds; scores committed + TAGGED | — | — |
| M4 | Stage 2: argmax at 2.8b/6.9b/12b | — | — |
| M5 | Frozen analysis; verdict; report | — | — |

## M0 build, tranche 1 (2026-07-18) — split machinery + non-wordlist specs

**Design revision applied first** (doc §2 revision note, same date): #3/#4
retargeted to middle-digit-of-result (carry/borrow counts are additive-threshold
composable — a linear probe expresses [Σf(tokᵢ) ≥ θ] via per-token scores and
generalizes across held-out pairs; the mod-10 wrap is not so expressible);
#10 (time arithmetic) to reserve, same mechanism, no clean repair. General rule
recorded in the doc: every field-4 argument must show a non-additive wrap or
interaction.

**Split machinery (`splits.py`):** basis = per-item component tuple; starving
split holds out values per component; val = ALL components held out, train =
ALL kept, mixed dropped. `shared_components` mode draws ONE holdout set over
the union for specs whose components share a value space (gcd operands, sort3
members) — per-position holdouts leak there. Class coverage on both sides
enforced by seeded rejection (≤200 redraws); feasibility = the design's field-5
minima for all 5 seeds, committed per capability inside the item file.

**Build-time catches (each would have been a silent confound):**
- gcd/sort3 positional leak → `shared_components` (above).
- reverse_string basis corrected to the FINAL BPE CHUNK per the design table
  (whole-string holdout starves nothing — random strings share final chunks);
  `_final_chunk` uses the pinned 410m tokenizer (one tokenizer suite-wide).
- bin2dec widened to 8–11 bits (6-bit space = 32 unique questions < 2500) and
  div7 to ≤9999 (990 < 2500) — feasibility, not difficulty; mod-wrap
  composability arguments unaffected.
- month_offset (36 questions) and letter_half (26) CANNOT meet the uniqueness
  rule at full counts: kept in SPECS, expected to EJECT at M0 generation
  (`items/ejections.json`), per the design's field-5 ejection path. An earlier
  draft set `allow_dupes=True` on both to dodge the gate — reverted; duplicate
  eval items would break the CP bounds' independence assumption for scored
  capabilities.

**Conventions:** BASE_SEED=20260718, per-spec seed = BASE_SEED + position in
the FULL spec list (ejections never shift other streams); no sys.path
insertions (exp2's shadowing lesson); oracles AND basis extractors parse
question text only; `models.py` = exp2's SHA-pinned loaders verbatim.

**Tests: 21 pass** — split invariants (value-disjointness, class coverage,
shared-mode no-positional-leak), oracle+basis agreement per generating spec,
small-space ejection behavior, tokenizer-basis suffix property, and the
design's core claim executed directly: a per-value lookup table fit on train
scores 0.0 on starved validation.

## M0 build, tranche 2 (2026-07-19) — wordlists + word/semantic/relational specs

**Wordlists** (`battery/wordlists.py`, exp2's file + 2b additions, all
integrity-checked in-session): CATEGORIES_2B 10×16 (no cross-category member),
ANTONYMS 117 pairs (unique cues), RHYME_FAMILIES 30×8 (every word verified
against its family suffix), CAPITALS 116 (well-known subset, deliberate),
NAMES_2B 40 unique, IRREGULAR_PLURALS 40 / IRREGULAR_PAST 60, UNIT_PAIRS 16
(powers 1–3 balanced 5/5/6).

**Specs** (`battery/generators_t2.py`, 15 more → SPECS = 30): design revision
#2 applied (doc §2 second note — choice formats for #20/21/22/25, #18 parity
retarget, structural-pattern bases for #27/#28). One-way import only
(generators.py imports t2 at its bottom; a two-way import was order-dependent
— caught when the smoke test imported t2 first).

**Build-time catches, tranche 2:**
- **Mention-order canonicalization collapses entity_track's pattern space:**
  raw 3⁴=81 transfer patterns → 14 canonical (first transfer is always
  mention-0→mention-1), under the 15-value minimum → 5 transfers (41 patterns,
  verified empirically over 3000 draws).
- **Uniform value holdout starves rare label classes** (unscramble/caesar
  first letters): added `stratify_by_label` split mode (per-label-group
  holdout, k=1, refuses single-value classes) AND letter-stratified
  generation so no rare class enters the items — exp2's lesson on both sides.
- The `_quick` test helper dropped new SplitParams fields on rebuild →
  `dataclasses.replace` (a silent-drop class of bug).
- cat_parity shot answer was wrong on first draft (hammer, saw, oak = 2 tools,
  not 3) — caught on self-review; the oracle-agreement gate would also have
  caught it at generation.
- deduce3/entity_track probe labels briefly carried a "pos|pattern" packing
  that polluted the class space — label is the position alone; the basis_fn
  recomputes the pattern from text (independence discipline).

**Tests: 36 pass** (oracle+basis agreement for all non-tokenizer specs at
reduced counts, both tokenizer bases against the real tokenizer, ejection
behavior for all five small-space candidates, split invariants incl. the new
stratified mode).

## M0 build, tranche 3a (2026-07-19) — instrument, analysis, committed battery

- **`probe_starved.py`** (the Stage-1 instrument): starved-split probes,
  estimator pipeline mirroring the frozen module verbatim (StandardScaler +
  LogisticRegression, C=1.0, max_iter=100 per the ledgered Exp 2 revision),
  frozen stats primitives via the exp1 alias loader (`permutation_null`
  already returns the null SD the gate floor-signature check needs). Margin
  zeroed below the α=.01 Bonferroni bar, unchanged. Returns its own dict
  schema — nothing frozen edited.
- **Headline test executes Exp 2's failure against the new instrument:** a
  pure-lookup synthetic world, verified decodable in-distribution (>0.9),
  reads present=False / margin 0 under starvation. Plus: structure world
  fires and generalizes; shuffles silent; per-seed determinism; fresh-
  interpreter shadowing regression; analyze thresholds pinned.
- **`analyze.py`**: exp2's frozen logic; MIN_N=20, ALPHA_PERM=0.01,
  SEED=20260718. Verdict precedence unchanged.
- **Battery generated at FULL COUNTS under the canonical venv:** 24 scored
  candidates + ctrl_copy committed (14 MB of item files — the file is the
  operationalization); exactly the 5 designed ejections in
  `items/ejections.json`; starved-val minima 346–816 across all 5 seeds for
  every scored capability. Generation-gate catches, fixed pre-commit:
  bin2dec's space arithmetic was wrong by 2× (fixed leading bit → 1920 < 2500
  at 8–11 bits; widened to 8–12), parens' 4–10 length range gave 2032 unique
  strings (→ 4–12), acronym needed stratified holdout + stratified w2 draw
  (the caesar lesson). Scored candidate count lands exactly on the design's
  n ≥ 24 target before M1 inclusion.
- **Tests: 94 pass**, including oracle-scores-100%-on-committed-items for all
  26 files and basis text-recomputability on committed data.

## Pre-freeze rehearsal + power table (2026-07-19, running)

- **MC power table** (`run/power_table.py`): full verdict machinery simulated
  end-to-end (the actual spearman/permutation/bootstrap functions, FAIL veto
  included), 400 sims/cell over n ∈ {20,24,27,30} × ρ ∈ {0,.3,.4,.5,.6,.7,.8}.
  Output committed with the freeze.
- **Gate rehearsal** (`run/rehearsal.py`, design §7): probe_starved on Exp 2's
  real 410m mod7 activations, trained AND untrained, seed 0, full N_PERM —
  both are known lookup worlds (instrument diagnostics §4), so the instrument
  must read BOTH silent; wall-clock per unit is the M2/M3 campaign
  calibration. Exp 2's 12 GB activation store retained locally for exactly
  this purpose.
## Rehearsal results + FREEZE (2026-07-19)

- **Power table** (400 sims/cell, full verdict machinery): true-null world
  PASS ≤ .01 / FAIL .97–.98 everywhere; PASS power at n=24: .74 (ρ=0.6),
  .92 (ρ=0.7), .98 (ρ=0.8). Honest edge, on the record: at true ρ=0.5 the
  bootstrap-CI falsifier fires ~1/3 of the time at n=24 — the FAIL veto is
  dangerous to the thesis at moderate effects; preregistered price of a
  falsifier with teeth.
- **Rehearsal (§7) PASSED, transcribed from the run output:**
  `410m/untrained/mod7: present=False acc=0.1074 null_mean=0.1431
  margin=0.0000 n_val=391 wall=2565s` and `410m/trained/mod7: present=False
  acc=0.1151 null_mean=0.1428 margin=0.0000 n_val=391 wall=2552s`. The world
  that scored margin 1.000 on Exp 2's instrument scores 0.000 here, on the
  same real activations — the reservoir confound is closed empirically, not
  just synthetically. Trained mod7 silent = a genuine Stage-1 zero (margin 0
  is ordering information), consistent with the group-split diagnostic. No
  gate-threshold changes needed from the rehearsal; none made.
- **Campaign calibration:** ~43 min/unit single-core at 410m, full
  N_PERM=2500, max_iter=100 (measured, not estimated — first run of the
  workload shape). 1b will run ~2× that. The M2/M3-scale program (~720
  units) budgets from THIS number across Mac + llmbox/atom workers per the
  distributed-runs section; per-box determinism gates before results count.
- **FROZEN:** this commit, tag `exp2b-preregistered`, per Michael's standing
  authorization (2026-07-18). Next: M1 inclusion (argmax at 410m/1b, all 24
  candidates + ctrl_copy — first Exp 2b model queries).

## M1 + Amendment #1 (2026-07-19) — battery fixed at n=25

First inclusion pass: 13/24 survived the frozen rule (11 above threshold at
1b — two mechanisms: genuine ability incl. gcd .68 / entity_track .69, and
the small-answer-space format artifact from Exp 2's parity: div7 .50, parens
.39, cat_parity .38). 13 < 20 → the designed halt fired; Michael chose Path B
(battery extension, thresholds untouched, refused-by-name: lowering the
floor). Amendment #1 mini-freeze 0fcf92b: 12 hard large-answer-space
candidates. Top-up result: **12/12 below threshold** (margins −.004 to .154;
isqrt lands BELOW the untrained floor). Battery fixed at **n=25** of 36
candidates (design band 24–30), scored_battery.json committed with this
entry on Michael's approval. Membership is attrition-only from here.

NEXT (M2): activation collection at 410m/1b (trained + untrained) over the
25 scored capabilities + ctrl_copy; probe program (known-absent, known-
present, shuffled — binomial tolerances per design §4) with DISTRIBUTED
fitting: llmbox/atom boxes join only after passing the per-box determinism
gate (design §6); campaign cost budgets from the measured 43 min/unit
(410m, single-core, full depth).

## Distributed fleet online (2026-07-19 afternoon)

All three boxes passed the determinism gate BIT-IDENTICALLY (arm64
Accelerate / x86_64 Linux OpenBLAS / AMD64 Windows) — the cross-BLAS
gamble resolved in our favor; no exclusions. Queue partition: Mac
front-to-back; llmbox (8 procs) 410m from the back; devbox (12 procs) all
of 1b. Two-way sync every 240 s. Atomboxes EXCLUDED (atombox1: 1.2 GiB
free, 23 GiB swap, serving live DSv4 traffic — flagged to Michael as its
own operational concern; atombox2 headroom too thin to risk its cluster
partner). Fleet ops catches, for the record:
- OpenBLAS ignores the in-worker OMP setdefault (pool spawn imports numpy
  first): llmbox's first launch ran 23 threads/proc at load 102. Env is
  now pinned at launch; relaunched before any unit completed, so no
  mixed-threading results exist. Single-threaded BLAS is also what the
  gate certified.
- scp -r into a nonexistent directory renames instead of nesting
  (devbox's untrained shard landed flat; moved).
- Windows sshd kills the process tree at session close — Start-Process
  does not survive; the worker runs as a Task Scheduler job
  (schtasks exp2b-worker → run_worker.bat).

## Push-failure postmortem (2026-07-19 evening) — the bug was ours

Three commits refused to push (HTTP 500 after ~57 s on git-receive-pack;
reads and API healthy). Initial diagnosis — "GitHub server-side wedge" —
was WRONG and survived two retry loops and an HTTP/1.1 workaround attempt
because it sounded right. Preparing a git-data-API workaround forced an
enumeration of the changed files, which exposed the real cause: the
worker-infra commit's bulk `git add experiments/exp2b` had swept the
ENTIRE results/activations/ tree (~19 GB of npz) into history — exp2's
.gitignore line covered exp2/ only, never exp2b/. GitHub was correctly
rejecting a pack beyond its 2 GB limit; the 57 s stall was the upload.
Fix: local history rewrite before anything reached the remote (content
parity verified — only the 46 npz and one .gitignore line differ),
exp2b activations now gitignored; SHA-256 digests will stand in at the
data-freeze, per the exp2 convention. Lesson, verbatim from the exp1
commit-audit family: a plausible external explanation is not a verified
one — enumerate the payload before blaming the pipe.

## Shuffled-gate crash + fleet throughput reality (2026-07-20)

**ABORT 17:13 EDT:** the Mac campaign died in `shuffled/410m` —
`ValueError: basis value 'x4' induces two labels; stratification undefined`
(splits.py:91, raised on caesar). Root cause: `run_probes_2b.py` permutes
labels BEFORE `probe_starved` builds the starving split; the two scored
capabilities with `stratify_by_label=True` (caesar, unscramble) require
basis→label to be a function — true of real labels by construction, violated
almost surely by permuted ones. First-ever execution of this code path
("125 to fit, 0 cached"): the pre-freeze rehearsal exercised the known-lookup
worlds, and no test composes shuffled × stratified — a recorded coverage gap.
Blast radius: shuffled × {caesar, unscramble} × {410m, 1b} = 20 of 770 units.
Every other stage fits TRUE labels (known_absent/410m completed 125/125
through both capabilities hours earlier). 18 shuffled/410m units
(add_base8 5, add3_mid 5, antonym 5, base7 3) completed before the pool died.

**PROPOSED FIX — NOT APPLIED, awaiting Michael's ruling (the one
mechanism-justified fix; written before any re-run, mechanism only):**
build the split from the TRUE labels and permute labels only for the fit.
The frozen instrument already defines this discipline: probe_starved's
permutation null "permutes labels over ALL items under the FIXED split" —
the shuffled gate is that null's campaign-level replication, and design §4
gate 3 specifies only "trained activations, rng(1000+seed) label shuffles",
silent on split construction; shuffle-before-split was an unpreregistered
implementation ordering. Implementation: `probe_starved` gains optional
`split_labels=None` (default = fit labels; every existing call byte-identical),
and the runner passes true labels in the shuffled stage. Uniformity rider
(precedent: 291ec9c estimator-uniformity deletion): delete the 18 completed
shuffled/410m fits and refit under the fixed path — labels enter
non-stratified splits only through the class-coverage redraw check, but a
gate cell with mixed split provenance is not worth ~4 Mac-hours. The
deletion must also sweep the devbox and llmbox result MIRRORS in the same
sync cycle, or the pull side of sync_workers.sh resurrects the stale fits.

**Fleet throughput reality (measured, not assumed):** devbox has completed
ZERO units across two worker generations (gen 1 killed at the console
yesterday; gen 2 = 12 sharded inline workers running since 09:36 today, env
correctly pinned, single-threaded, ~61% of a core and ~4.75 CPU-h each, no
completions). Determinism-gate fixture timed on the live boxes: Mac 2.75 s
vs devbox 17.3 s ≈ 6.3× per-core — a 1b unit ≈ 9 devbox-CPU-h ≈ ~15
wall-h/worker/unit; first devbox completions expected near midnight, box
throughput <1 unit/h, so its assigned 1b half (385 units) is WEEKS of work.
llmbox: 11 m3/410m units in ~28 h, negligible as expected. Net: the Mac
(~5 units/h at 410m, ~2.5/h at 1b) is roughly 6× the rest of the fleet
combined; the 3–4-day fleet ETA is void. Mac-led realistic: gate stages
~5–6 days, full probe program ~8 days from today.

**Ops actions taken with this entry:** (1) disabled the stale one-time
23:59 triggers on devbox tasks exp2b-w0..w11 — creation-time placeholder
start-times due to fire TONIGHT, which would stack a duplicate 12-worker
generation on the running one (tasks intact; Enable-ScheduledTask + /run
relaunches); the running generation is untouched and its results count
(gate PASSED). (2) launched `run/interim_true_label.sh` on the Mac
(17:40 EDT): true-label stages in gate-priority order — known_present:410m →
known_present:1b → known_absent:1b → m3:410m — same frozen runner,
skip-if-exists; NO shuffled units run before the ruling. (3) campaign
relaunch deferred: it would re-enter shuffled/410m and re-crash in minutes.
Known in advance: once the 410m m3/known_present queues exhaust, llmbox's
worker_loop advances into shuffled:410m and dies on this same defect
(reversed order reaches unscramble almost immediately) — harmless at its
throughput; relaunch it after fix deployment. Worker code does NOT
auto-sync (sync loop carries results/activations only): the fix, once
ruled, is deployed to devbox/llmbox by hand.

**Decisions for Michael:** (a) the fix ruling above; (b) queue rebalance —
recommend the Mac owns the 1b gate stages (interim already covers
known_absent:1b) and devbox is reassigned as m3/1b help only; (c) accept
the revised timetable (M2 gate review ~5–6 days out, not 07-22/23).

## Fix applied on Michael's ruling; fleet restructured; campaign relaunched (2026-07-20 evening)

Michael approved both open decisions (~17:45–18:00 EDT): the workload
restructure and the ledgered shuffled-gate fix. Applied exactly as proposed:

- **Code:** `probe_starved` gains keyword `split_labels=None` — when given,
  the starving split is built from these labels instead of the fit labels;
  default path byte-identical (every existing call unchanged). The runner
  passes the TRUE labels in the shuffled stage and permutes only the fit
  labels; rng(1000+seed) stream unchanged. The basis→label guard survives
  for the default path (a real invariant, not loosened).
- **Verification:** regression test (shuffled × stratified) written failing
  first, passes after; suite 131/131. worker_gate PASS bit-identical on all
  three boxes against the unchanged committed reference. Real-data smoke on
  the exact crashing unit (caesar/410m shuffled, seed 0, n_perm=100,
  nothing written): completes, present=False, acc .068 ≈ chance, stratified
  split from true labels (44 held values). Production confirmation = first
  caesar/unscramble units in the relaunched stage (watch armed).
- **Uniformity rider executed:** the 18 pre-fix shuffled/410m fits deleted
  on the Mac AND both worker mirrors with the sync loop paused (restarted
  after); the relaunched stage refits 125/125 under the fixed path.
- **Restructure:** Mac owns the gate stages and all 410m (campaign
  relaunched 18:10, resumed directly into shuffled/410m; collections and
  known_absent/410m fully cached). devbox: running generation left
  untouched — its in-memory queue (known_absent:1b from the back, then
  m3:1b) never reaches shuffled; launch .bats trimmed to
  `known_absent:1b m3:1b`; schtasks remain DISABLED (relaunch =
  Enable-ScheduledTask + /run; fixed code already on disk). llmbox:
  restarted on the fixed code with `shuffled:410m m3:410m` (gate PASS
  before relaunch; reversed order puts unscramble in its first batch —
  its completions double as an independent fix confirmation). Worker code
  hand-deployed to both boxes (sync loop carries results/activations only).
- **Cost of the swap:** the interim runner was killed mid known_present/410m
  with 0 of 10 units finished (~4.7 core-h lost); the campaign refits the
  stage in order. Interim runner retired — the canonical campaign script is
  the sole Mac driver again, and it ends with the M2 report as committed.

**Production confirmation (18:56 EDT):** `shuffled/410m/caesar/seed0` — the
exact unit that killed the campaign — completed at full depth in the
relaunched stage: present=False, p=1, acc .0680, margin 0. Accuracy matches
the reduced-n_perm smoke bit-for-bit (same fixed split, same shuffled
labels; only the null's resolution differed). The fix is confirmed on real
data end-to-end.

## devbox released to Michael (2026-07-21 ~11:35 EDT)

First-wave results were in when Michael asked for the box back: 10
known_absent/1b units (nine seed0s + odd_one_out seed1), filename-verified
identical on the Mac and devbox mirrors before release. Workers stopped by
command-line match (24 python processes → 0; unit writes are
completion-only, so no partial files exist); ~80 CPU-h of second-unit
progress discarded — sunk at shutdown regardless. schtasks remain DISABLED
and nothing auto-starts on boot; the trimmed .bats and fixed code stay on
disk, so re-onboarding when the box returns is: Enable-ScheduledTask
exp2b-w0..w11, then run them. The sync loop tolerates the box going dark
(its devbox legs are `|| true`). known_absent/1b falls fully to the Mac's
campaign queue, as the re-ledgered timetable already assumed.

Overnight, for the record: the relaunched shuffled/410m refit reached
100/125 by 11:30 EDT with zero aborts — caesar clean early (production
confirmation above), unscramble covered from the back by llmbox's first
batch. Combined 410m rate ~5.8 units/h.

## Mid-campaign observation, timestamped before the frozen report (2026-07-23)

Descriptive tally of gate stages banked so far (410m complete; known_absent/1b
52/125). Gates 2 and 3 on-script: known_present 10/10 fires (ctrl_copy at
ceiling, entity_track margins .29-.35 all seeds); shuffled/410m 2 floor-p
fires in 125 (binomial-consistent). Gate 1 is NOT floor-rate: 51 fires in
177 untrained fits. All-seeds structural patterns: collatz2 (margins
.74-.82, BOTH sizes), roman (.64-.78), isqrt (.36-.42), digitprod7
(.20-.28), unscramble (.18-.22); numletter 5/5 weak (.06-.10); scattered
weak singles elsewhere. mod7 family near-silent — the starving works against
exp2's known lookup offender; the strong fires look like per-capability
basis leaks instead (e.g. collatz2 parity via last-digit structure).
Attrition arithmetic: five clear structural candidates → n=20 = MIN_N
exactly; the weak swing cases decide whether the frozen verdict stays
scorable or reads INSUFFICIENT_DATA. No thresholds touched; the ruling is
m2_report_2b's at campaign end. This entry exists so the observation
provably predates the report.

## Gate 1 complete — frozen-criterion projection (2026-07-24 ~00:45 EDT)

known_absent finished 00:29 (250/250 fits). Applying the FROZEN
floor-signature predicate (m2_report_2b: p exactly at the family add-one
floor AND accuracy within 3 null-SD) descriptively to the complete inputs:
**0 floor-signature fires, 86 structural leaks** spanning 13 capabilities
(bin2dec, collatz2, digitprod7, isqrt, mod7_add, mod7_mul, mul3x1,
numletter, roman, sq_mod7, units, unscramble, weekday). Projected frozen
adjudication: attrition of all 13 → n = 12 < MIN_N = 20 → INSUFFICIENT_DATA
at M5. The count test AS CODED pools fires+leaks (p ≈ 7e-117 → pipeline
abort exit 2); the docstring's stated intent counts floor-signature fires
only (0 → p = 1, no abort). Both readings end in a dead battery; the
drafting divergence is recorded here as an exp1-S1-class frozen-criterion
lesson, NOT proposed for change.

Sanity, argued before the report runs: 410m and 1b are independently
initialized untrained models, and per-capability leak margins match across
them (collatz2 .74-.78 / .75-.82; unscramble .18-.22 both; units leaking on
the same probe seed at both sizes) — the signal is input-statistics-through-
random-projections, not a weights or collection artifact. Starving
attenuated exp2's reservoir confound (margins 1.0 → .06-.8) without closing
it: 13 of 25 capabilities retain surface-computable structure under starved
splits on untrained weights. mod7_add/mod7_mul leak at margins ~.09-.11 —
even the family starving demonstrably suppresses still clears the strict
3-SD signature.

Campaign left RUNNING (shuffled/1b in progress; gate 3 completes there).
Open ops decision for Michael: whether m3/1b (~48 h) is worth fitting under
a projected abort/INSUFFICIENT_DATA, or whether to pause after shuffled/1b
and take the redesign discussion first. No thresholds touched, nothing
stopped, ruling remains the report's at campaign end.

## Gate 3 complete — and a frozen-criterion tension, argued from first principles (2026-07-25 ~10:50 EDT)

shuffled done at both sizes: 410m 2 fires / 125, 1b 0 / 125. Both 410m
fires FAIL the frozen floor-signature predicate (3.6 and 4.7 null-SD above
null mean) → as coded, gate 3 projects PIPELINE ABORT on s_leaks.

Recorded objection, mechanism only: the predicate's two conjuncts are in
tension. p at the add-one floor REQUIRES the observed accuracy to beat all
2500 permuted fits; the expected maximum of 2500 null draws lies ~3.4 SD
above the null mean — beyond the 3-SD near_null bar. The "tolerated
floor-signature fire" class is therefore nearly empty by construction, and
a clean null was expected to produce ~0.9 floor-reaching fires across 250
fits (P(>=1) ~ .59) that the predicate would misclassify as structural.
The observed 2/250 matches the designed rate exactly (P(>=2) ~ .23). This
is the same class of misspecification as exp1's S1 magnitude criterion:
the count arithmetic is sound, the per-fire signature bar contradicts the
mechanism that produces floor fires. Any fix is ONE-ledgered-fix territory,
Michael's ruling at the gate review, and this entry is the pre-report
mechanism argument that would justify it — written before m2_report_2b runs.

Gate 1's projection is UNCHANGED by this objection: its 86 fires are
rate-impossible under the null however classified (every leaking capability
fires on >=2 of 10 seeds vs per-cap expectation .07); attrition x13,
n=12 < MIN_N, INSUFFICIENT_DATA stands on count arithmetic alone. The
correct postmortem shape: instrument worked, battery died of real surface-
computability leaks; the signature-test drafting flaw is a separate,
fixable finding. known_present/1b now running; m3/1b auto-starts after it
(campaign default = continue) — Michael's continue-vs-pause call remains
open, noting the 12 surviving caps' m3 fits would feed any descriptive
(non-verdict) salvage analysis.

**Gate 2 complete (2026-07-25 14:28):** entity_track 5/5 present at both
sizes, mean margins .330 (410m) / .281 (1b) — clears the frozen ≥.2 bar;
ctrl_copy .997/.998. Full pre-report projection now on record: gate 1
attrition ×13 → n=12 → INSUFFICIENT_DATA; gate 2 PASS; gate 3 clean in
substance (2/250 at the designed rate), projected abort only via the
ledgered signature-predicate contradiction; gate 4 from committed M1
inclusion. m3/1b running (~48 h); the frozen report fires automatically at
campaign end.

## CAMPAIGN COMPLETE — frozen report ran (2026-07-27 00:47 EDT)

770/770 units (2026-07-19 13:36 → 2026-07-27 00:47, incl. the 07-20 crash
window). m2_report_2b exited GATE ATTENTION REQUIRED. Formal scoreboard vs
the ledgered projections:

- GATE 1: 0 floor-signature fires + 86 structural leaks / 250; attrition
  x13; pooled count p=6.5e-117 → ABORT as coded. Matches projection
  (496c488) exactly.
- GATE 3: 0 floor fires + 2 leaks / 250; COUNT test p=.538 (PASSES —
  confirming the fire rate is the designed one); abort triggered solely by
  the leak classification, i.e. solely through the predicate whose
  self-contradiction was argued pre-report (710ece1).
- GATE 2: all four cells OK (matches).
- GATE 4: ctrl_copy argmax 410m 0.868 (434/500, CP95 [.835,.896] — upper
  bound below the .9 bar) → GATE FAIL; 1b 0.954 OK. NOT projected: the
  number sat in the committed M1 inclusion record since before the freeze
  and the bar was never checked against it at M1 review — a process miss
  (the M1 review checklist lacked the gate-4 arithmetic), surfaced by the
  frozen report as designed. Same phenomenon class as exp2's
  ctrl_next_letter (generation-side argmax reliability weak at 410m) while
  the probe side of ctrl_copy is at ceiling (.997) — output channel vs
  representation channel, on our own control.

GATE REVIEW AGENDA (Michael's rulings, none made here): (a) gate 1
abort-vs-attrition reading (code pools leaks into the count test; docstring
counts floor fires only — either way n=12<20); (b) gate 3: predicate-
misspecification finding vs real contamination (count test at .538 and the
pre-report order-statistics argument support the former); (c) gate 4 410m:
design-assumption finding per the exp2 ctrl_next_letter precedent + the M1
checklist process miss; (d) VERDICT (projected INSUFFICIENT_DATA, n=12);
(e) closeout mechanics: data commit + digests, VERDICT.txt, retrospective,
tag exp2b-closed. Then: methods-paper outline, then 2c design doc, per the
agreed sequencing.

## GATE REVIEW — Ruling (a), ACCEPTED by Michael (2026-07-27)

**RULING: Gate 1 closes as ATTRITION ×13 per design §4.1.** The report
code's pooled-count abort is ruled an IMPLEMENTATION DEVIATION from the
preregistered design (second of its class, after shuffle-before-split):
§4.1 prescribes attrition as gate 1's sole remedy for structural fires and
grants abort only to gate 3; the pooled test trips at 7 fires in 250 while
one leaking capability contributes 10 leak-fits, so as coded the design's
attrition provision could never operate for any possible data — an
implementation that makes a preregistered provision unreachable cannot be
the preregistered rule. The argument is outcome-independent and was
presented with both readings steelmanned; both end at n=12 with no Stage 1
and no thesis evidence, so the ruling selects the accurate label, not a
rescue. Effects: attrition set = the 13 ledgered capabilities; scored
battery falls 25 → 12; §4.5 floor applies (n < 20); instrument
certification STANDS (gate 2 passed, gate 3 count-clean) and 2c inherits
the instrument without re-validation. The report's banked output is
untouched; this is a closeout adjudication in the exp2 pattern.

**STANDING RULE promoted for 2c (and successors):** adjudication code is
frozen WITH fixture tests derived from the design doc's own worked
examples and one synthetic case per preregistered provision (e.g., "one
leaking capability" must yield attrition-without-abort). Both of 2b's
implementation-deviation bugs would have been caught pre-freeze by this
rule; the design text already contains the first fixture (roman/seed3).

## GATE REVIEW — Ruling (b), ACCEPTED by Michael (2026-07-27)

**RULING: Gate 3 closes CLEAN on its count test (p=.538); the two 410m
fires (bin2dec/seed0, odd_one_out/seed4) are ruled floor-rate events; no
pipeline abort.** The per-fire floor-signature predicate is recorded as a
DESIGN-LEVEL CALIBRATION MISSPECIFICATION (Exp 1 S1's class): its 3-SD
near_null conjunct contradicts its at-floor conjunct — the expected max of
2500 null draws lies ~3.4 SD above the null mean, so a clean null was
expected to produce ~0.9 predicate-failing fires per 250 fits (P>=1 ~.59).
The design's own §4 header intent ("no zero-tolerance rules on nonzero-rate
tests") is violated by the predicate one level below its count arithmetic.
Supporting pattern: count at expectation, no capability/seed structure,
zero fires at 1b, uniform refit under the verified fixed-split path — the
opposite profile from gate 1's cross-init-reproducing leaks. The mechanism
argument predates the report (710ece1). Feeds 2c: per-capability binomial
rate tests as primary attrition trigger; signature bars derived from the
max-of-N mechanism.

**Combined effect of (a)+(b): the closeout carries NO pipeline abort.**
Exp 2b closes entirely through its own decision tree — attrition ×13 →
n=12 → §4.5 floor — with the instrument exiting CERTIFIED (gate 2 pass,
gate 3 clean-by-count, gate 1 leaks being real battery properties).

## GATE REVIEW — Ruling (c), ACCEPTED by Michael (2026-07-27)

**RULING: Gate 4 records FAIL at 410m (.868, CP95 [.835,.896]) / PASS at 1b
(.954), ruled a DESIGN-ASSUMPTION FINDING** per the exp2 ctrl_next_letter
precedent: the assumption that argmax-reliability measurements (exp2's
.994/1.000) transfer across battery versions was disproven by 2b's own
committed M1 measurement on its own items. Consequences: (1) documented
reliability caveat on 2b's 410m argmax inclusion readings — bias toward
absence; moot for the dead battery, binding on the record; (2) 2c inclusion
re-anchors on 1b + probe-side evidence or recalibrates its bar against
measured control reliability of its own items; (3) STANDING RULE promoted:
gates whose inputs are committed pre-freeze are adjudicated pre-freeze
(M1/freeze-review checklist line) — this gate was checkable 8 days before
the campaign spent its compute. Recorded observation, explicitly bounded:
ctrl_copy at 410m reads .997 by probe and .868 by argmax generation — a
representation-vs-output-channel gap on our own control; suggestive color
for the essay's pattern, not an emergence claim.

## GATE REVIEW — Ruling (d), ACCEPTED by Michael (2026-07-27)

**VERDICT: INSUFFICIENT_DATA.** Attrition floor breached — 12 of the
required 20 scored capabilities survive gate 1. Per design §4.5, frozen at
exp2b-preregistered: never a smaller test, never a loosened gate. No Stage
1 was committed; NO eval-side model was ever queried (the two-stage lock
was never crossed); the thesis remains untested in both directions. The
instrument exits CERTIFIED (gates 2 and 3); the experiment's positive
product is the leak taxonomy (lookup class closed by starving; surface-
statistics class caught by the untrained control) and the 12-survivor seed
stock. Known-in-advance status: projected in this ledger 07-23/07-24 from
gate-1 data alone, before the frozen report ran; the formal adjudication
confirmed the projection. Closeout mechanics (e) proceed: VERDICT.txt,
activation digests, data commit, retrospective, tag exp2b-closed — drafts
to Michael before the tag.

## EXPERIMENT 2b CLOSED (2026-07-27, tag exp2b-closed)

Closeout commit: 770/770 probe fits, m2_report.json, campaign + interim
logs, activation SHA-256 digests (108 npz, local per convention),
VERDICT.txt (INSUFFICIENT_DATA), retrospective.md. All four gate-review
rulings accepted by Michael this date. Repo CLAUDE.md status updated.
NEXT WORK per agreed sequencing: methods-paper outline from the closed
record, then Experiment 2c design doc (seed stock: the 12 survivors;
untrained-weights screening gate at inclusion; per-capability binomial
rate tests; mechanism-calibrated signature bars; fixture-tested
adjudication code; pre-freeze adjudication of pre-freeze-input gates).
