# Exp 3b — Progress Ledger

## Campaign, 2026-08-15 — COMPLETE: 40/40 cells, 0 failed

Committed order held: all 20 untrained twins first, then trained
410m → 1b → 2.8b → 6.9b → 12b. One commit per cell (the committer loop),
each pushed on landing. Total inference ~75 min wall clock. **No
first-character quantity has been computed for any cell; the frozen
analysis has not run.**

Full-string accuracies, all cells (the log's per-cell lines; referent
agreement is gate 2/3's to adjudicate, not this ledger's):

- untrained, all 20 cells: 0.0000 — exactly the committed expectation.
- trained probe sizes: rev_string7 0/0, reverse_string 0/0, ctrl_copy
  **.9600/.9800**, clock24_d999 **.0360/.0480** (410m/1b) — the four
  non-zero referents reproduced to the count (480/490, 18/24 of 500).
- trained eval sizes (2.8b/6.9b/12b): rev_string7 0/0/0 — the famous
  zero, reproduced; reverse_string 0/**.0020**/0; ctrl_copy
  .9900/.9960/.9940; clock24_d999 .0440/.0580/.0500.

**Operational disclosure (provenance, ledgered before analysis):** the
original single-process driver OOM'd the machine mid-campaign — PyTorch's
MPS allocator caches freed weights per process, so one process walking
the five-size ladder ratcheted to a measured 34 GB resident (system
notice attributed 61 GB to the tree) around cell 15/40. The driver was
killed between records (cell records are write-once at completion; the
one in-flight cell re-ran) and the campaign resumed **tier-per-process**
using the frozen driver's own preregistered `--only-mode/--only-size`
flags, in the identical committed order — 7 further invocations, one per
(mode, size) tier, each exiting and freeing memory before the next.
skip-if-exists made the restarts lossless; no frozen file was modified;
the collected records are byte-wise indistinguishable from a
single-process run (same runner, same per-cell code path). Michael's
mlx text-server (com.mlx.text-server, ~7 GB) was booted out for the 12b
tiers at his instruction and restored after the last cell.

## Verdict projection (ledgered 2026-08-15, BEFORE the first cell — §10.4)

Written after the tag and before any cell has run; no first-character
quantity exists anywhere at this commit. Graded at close-out against the
frozen analysis, 1c's practice. Blinder than §10.4 requires (it demands
only pre-analysis): every number the campaign itself will print
(full-string accuracy) is already predicted exactly by the committed
referents, so nothing the driver shows can inform this section — but it
is written first anyway.

**Gates — all four clean:**

- Gate 1 passes: ctrl_copy first-char ≥ its committed full-string
  (.960/.980) ≫ critical .086 at floor .052, significant at both sizes.
- Gate 2 replicates EXACTLY, not merely within CP overlap: greedy is
  deterministic on this stack and 3a reproduced 2c's committed
  accuracies byte-for-byte wherever they existed. Expect full-string
  counts equal to the referents: reversal 0×8, ctrl_copy 480/490,
  clock24_d999 18/24, untrained 0×8.
- Gate 3: 0 differing continuations in all 24 overlap cells; the
  tolerance of 2 goes unused.
- Gate 4 quiet: all 8 probe-size twins non-significant, contamination
  empty. An untrained net's modal emission is a constant or garbage
  first token: a constant letter scores at most its own frequency among
  answer firsts (≤ the marginal floor by construction), a non-letter
  scores 0. Either way, below significance at n_tests=1.

**Step 5 — the claim: DISSOCIATION.** All 4 reversal trained probe-size
cells non-significant (< 46/500 at 410m/1b floors .056, < 44/500 at
.054). Mechanism, stated so the grade can hit it: the first emitted
character at these scales is dominated by copy bias — the induction
pathway reproduces the quoted input's opening character, which matches
the answer's first character only at the measured copy_first rate
(~.038–.04, itself below the .056/.054 marginal floors) — plus format
noise; the probe's .57–.77 margins live in a basis the unembedding does
not read. Point estimates: reversal first-char .03–.06 per trained
probe cell; ctrl_copy ~.97/.985; clock24_d999 ~.50–.56 trained
(marginal-tracking, non-significant against .496); eval-size reversal
descriptives also at floor.

**Named most-likely miss (the PARTIAL route):** rev_string7/1b clears
alone — it carries the battery's strongest probe margin (.7725) and the
most mature emission stack — while 410m sits at floor → PARTIAL with
rev_string7/1b as the fired cell. **Disconfirmer for the mechanism
story:** any reversal trained cell at ≥ .12 first-char accuracy means
copy bias does not dominate and partial emission exists at the probe
sizes.

**Weights, so the grade is honest:** DISSOCIATION .55, PARTIAL .30 (the
split above), UNITS_ARTIFACT .10, INSUFFICIENT_DATA .05.

## Freeze session, 2026-08-15 (third session — tag `exp3b-preregistered`)

Opened adversarially per the protocol: cold re-read of doc + instrument
with the assignment "find the 3a-class defect — input with no value,
control missing referent, unsatisfiable criterion". **The defect was
hunted and not found**; full findings in `FREEZE_CHECKLIST.md`, including
two new verifications the build had not run (gate 2's referent-generating
process read line-by-line against the runner's; `probe_label[0] ==
answer[0]` on all 2000 committed items, so floor space ≡ scored space)
and two note-only observations (clock24_d999's "1-symbol answer" is loose
— 311/500 answers are two digits, no behavioural consequence; the
runner's is-file item routing vs the analyzer's RUNGS_2B constant, closed
by the verified absence of `exp2c/battery/items/reverse_string.json`).

**Rulings** (checklist "Rulings", §6 amended, no code touched):

1. Gate-4 scope BLESSED as implemented — probe-size twins only, preamble
   governs; eval-size twin fire is descriptive. §6 step 4 amended.
2. Both-reversal-rungs-contaminated BLESSED as implemented —
   INSUFFICIENT_DATA; `all([])` must not adjudicate. §6 step 5 amended.
3. NEW (this session's read): gate 1's "not significantly above at both"
   parsed two ways; amended to the built reading — the gate passes only
   when ctrl_copy clears floor at BOTH probe sizes. Fixture-pinned at
   build (`test_gate1_requires_both_probe_sizes_not_either`).

**Mechanical re-runs, cold**: 77/77 fixtures (1.01s); mutation KILLED
35/35, baseline clean, two full passes; full-shape 9/9 ALL TERMINAL
BRANCHES REACHED; `verify_referents.py --construct` 48/48 with
byte-identical `referent_check.json`; `compute_probe_margins.py` and
`compute_power.py` idempotent (zero git diff). Invariant intact: **no
first-character accuracy has been computed for any real cell, any size,
any mode** — no `results/` directory exists; every scored continuation
this session was synthetic.

The frozen artifact: design doc (status flipped, §6 amended) + all exp3b
code byte-identical to the build commits + this ledger + the checklist.
One pre-committed change: UNSPENT.

**Next (campaign, §10)**: verdict projection ledgered HERE before the
frozen analysis runs once; driver `run/campaign_3b.py` — all 20 untrained
twins, then trained 410m → 1b → 2.8b → 6.9b → 12b, commit per cell,
~100 min inference, Mac only, Sparks untouched.

## Build session, 2026-08-15 (post-design, pre-freeze — NO TAG)

Three-session protocol (Michael's pacing ruling, 2026-08-15): design |
build | freeze are separate sessions, boundary = context clear. The design
session produced `experiment-3b-design.md` (5026249, item 5 resolved in
3f48c94). This session built the instrument. The freeze is a LATER session
that opens adversarially: re-read doc + instrument cold with the assignment
"find the 3a-class defect — input with no value, control missing referent,
unsatisfiable criterion", record findings in the freeze checklist even if
empty, re-run the mechanical checks, then tag `exp3b-preregistered`.

**Invariant holds: first-character accuracy has been computed for NO real
cell, any size, any mode.** Every real-record read this session was
structural or aggregate: inclusion counts, floors, m3 margins, 3a record
shapes. The 3a continuations were loaded only to count them.

### Built

- `analyze_3b.py` — frozen analysis with its own loaders. 3a's floors /
  first_char (non-alphabetic fix) / score_cell / significance ported
  verbatim; new: sha-pinned floors with recompute-assert, CP-overlap
  replication gate against the 16 inclusion referents, byte gate against
  3a's 24 stored cells (tolerance ≤2, diffs disclosed verbatim
  regardless), probe-size-only contamination gate, step-5 quantifiers over
  non-contaminated reversal cells, battery shape refusals (missing /
  duplicate / valueless cells are errors, not verdicts). No branch reads
  results/m4/ anywhere.
- `run/run_cell.py` — 3a's runner on the five-size ladder. sys.path order
  correct from the start (exp2c wins; 3a's post-freeze correction cited in
  the header), `_assert_module_provenance` kept. `committed_2c_acc`
  REMOVED from the record — no m4 input exists anywhere in 3b, which is
  where 3a's `None` lived. Records carry `model_sha` (pinned revision) and
  `items_sha256` instead.
- `run/campaign_3b.py` — driver COMMITTED AT BUILD (1c's practice; 3a
  wrote its driver post-freeze and ate a correction). Order §10: all 20
  untrained twins, then trained 410m → 1b → 2.8b → 6.9b → 12b, sequential,
  skip-if-exists. Dry-run verified: 40 cells, untrained first, probe sizes
  first within each mode.
- `tests/` — 77 fixtures, one per preregistered provision, both
  directions; 9 synthetic full-shape batteries executed end to end through
  the frozen loaders (all four INSUFFICIENT_DATA routes, UNITS_ARTIFACT,
  DISSOCIATION, PARTIAL, one-rung contamination flipping the step-5
  quantifier, both-rungs contamination, eval-size twin fire as
  non-contamination); `mutation_check.py` under the corrected harness
  (pycache cleared, PYTHONDONTWRITEBYTECODE=1).

### Verified this session

- **77/77 fixtures pass**; **35/35 mutants killed** (softening AND
  hardening per gate), baseline clean.
- **`referent_check.json` 48/48**: all 16 inclusion records match design
  §4 verbatim (ctrl_copy 480/490 trained, reversal 0×8, clock24_d999
  18/24, untrained 0×8) with `sha` == the pinned `PYTHIA_SHAS` 3b loads
  and `untrained_seed` 0; all 24 byte referents structurally sound
  (500/500/500, path/content agreement); floors sha pin
  `f299fa08…` + recompute-assert clean; 20 m3 seed records present; both
  probe-size untrained twins CONSTRUCT deterministically at seed 0
  (state-dict sha256 reproduces across double construction: 410m
  `335d46b7…`, 1b `fa3fe1d2…`).
- **`probe_margins.json`**: recomputed means match design §3 to 4dp —
  rev_string7 .6263/.7725, reverse_string .5731/.6749. Per-seed values
  committed; nothing pooled.
- **`power.json`**: crit 46/500 at floor .056 (power .980 @ .12, .745
  @ .10, blind below .092); crit 44 at .054 — design §7 asserted, not
  trusted. Read through `load_floors`, so the table can never desync from
  the floors the verdict uses.
- Runner import path smoke-tested without touching a model: provenance
  assert resolves harness→exp2c / models→exp2b; all four rungs load 500
  items, answer_type `word`, MAX_NEW_TOKENS 12, 2 shots; reverse_string
  through the 2b fallback.

### Two design under-specifications, resolved in the build — FREEZE MUST RULE

The doc is a DRAFT; both resolutions are implemented, fixture-pinned, and
FREE to change until the tag. The freeze session must bless or amend
explicitly — silence is not a ruling:

1. **Gate 4 scope.** §6's step 4 says "any untrained cell"; §6's preamble
   says eval-size cells take NO significance tests. Implemented: the
   preamble governs — contamination quantifies over the 8 PROBE-size
   untrained cells; an eval-size twin fire is a descriptive fact, visible
   in the report, contaminating nothing
   (`test_eval_size_twin_fire_is_not_contamination`, battery
   `eval_twin_fire_is_not_contamination`).
2. **Both reversal rungs contaminated.** §6 says a contaminated rung is
   excluded from step 5's universal quantifiers and does not say what
   happens when the exclusion empties them. Implemented:
   INSUFFICIENT_DATA — `all([])` is vacuously true and must not be allowed
   to read as UNITS_ARTIFACT (or DISSOCIATION)
   (`test_both_rungs_contaminated_is_insufficient_data`, battery
   `contaminated_both_rungs`, mutant "vacuous quantifier allowed to
   adjudicate" killed).

### Open for the freeze session

- Adversarial cold read of doc + instrument (the assignment above), freeze
  checklist written even if empty.
- Rule on the two items above; amend §6 wording if the resolutions stand.
- Re-run cold: fixtures, mutation check, full-shape batteries,
  `verify_referents.py --construct`; record results in the checklist.
- Tag `exp3b-preregistered`.

### After the tag (campaign, §10)

Driver already committed. Untrained twins all 20 → trained 410m → 1b →
2.8b → 6.9b → 12b, commit per cell, verdict projection ledgered HERE
before the frozen analysis runs once. Estimated ~100 minutes inference on
the Mac; Sparks untouched.
