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
