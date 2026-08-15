# Exp 3b — Freeze Checklist

Adjudicated 2026-08-15, before the `exp3b-preregistered` tag, in the third
session of the design | build | freeze protocol (Michael's pacing ruling:
separate sessions, boundary = context clear; all three fell on the same
calendar day, but each opened with a cleared context). This session opened
adversarially, per the ruling that created it: cold re-read of
`experiment-3b-design.md` and `experiments/exp3b/` with the assignment
**"find the 3a-class defect — input with no value, control missing
referent, unsatisfiable criterion."** Findings recorded here even where
empty. Every item is GREEN (verified) or RULED (a judgement call, recorded
with its reasoning). Nothing is left as "probably fine".

## The frozen artifact

`experiment-3b-design.md` (§6 amended at freeze, rulings 1–3 below) +
`experiments/exp3b/analyze_3b.py` + `run/run_cell.py` +
`run/campaign_3b.py` + `verify_referents.py` + `compute_probe_margins.py`
+ `compute_power.py` + the committed artifacts (`probe_margins.json`,
`power.json`, `referent_check.json`) + the 77-fixture suite under
`tests/`. No code file was modified in the freeze session — the code
frozen is byte-identical to the code mutation-tested at build
(fbf7819…bb63b54); the freeze session touched only the design doc, this
checklist, and `PROGRESS.md`.

## The adversarial read — findings

**The 3a-class defect was hunted and not found.** The hunt, by class:

**Input with no value.** `verdict()` takes five inputs: cells, floors,
inclusion referents, byte referents, probe margins. Four of the five are
committed records that exist with defined values TODAY, before any cell
runs — floors (sha-pinned `f299fa08…`, recompute-asserted from committed
items), 16 inclusion records (values match design §4 verbatim,
`referent_check.json`), 24 byte referents (500 continuations each,
structure verified), margins (`probe_margins.json`, design §3 asserted to
4dp). The fifth — cells — is the only campaign-produced input, and
`load_cells` + `_shape_check` hard-error on anything other than the
preregistered 40 cells with integral values. 3a's specific death
(`float(None)` from an m4 record) has no analogue: `grep -rn m4` over
exp3b finds only the documentation of its absence. No branch reads
`results/m4/`.

**Control missing referent.** All four rungs carry all referents at every
size/mode the verdict reads: gate 1's ctrl_copy referent is the committed
480/490 at the probe sizes (the best-instrumented rung at the primary
sizes, by design §2.1); gate 2's 16 inclusion records exist including all
8 untrained twins; gate 3's 24 byte referents exist by construction (3a
collected exactly those 24 cells). `load_inclusion_referents` and
`load_byte_referents` refuse missing or valueless records at load, before
adjudication.

**Unsatisfiable criterion.** Checked gate by gate, this session, against
the committed records and code:

- *Gate 1:* expected ctrl_copy first-char count ≥ 480/500 (first char ≥
  full string by construction) against critical count 43 at floor .052.
  Satisfiable with ~10× margin.
- *Gate 2:* satisfiable **by construction of the process, verified line
  by line this session** — see "new verifications" below.
- *Gate 3:* referents exist for exactly the 24 cells compared;
  determinism precedent on this stack (3a reproduced 2c's m4 accuracies
  exactly on all nine overlapping cells); tolerance 2 for tie flips so a
  single flip cannot kill the experiment.
- *Step 5:* floors are the committed marginals (.052–.496), critical
  counts 43–46 (letter rungs) / 283 (clock24) out of 500 — reachable
  from both directions; power committed in `power.json`. The 1b-class
  cross-system criterion defect (raw accuracy compared across
  incommensurable label spaces) is structurally absent: probe margin and
  behavioural margin are reported side by side but never compared
  numerically; the verdict quantifies only over behavioural significance
  against behavioural floors in the behavioural label space.

**New verifications performed this session** (beyond re-running the build
checks):

1. **Gate 2's referent-generating process is the runner's process.**
   Read 2c's `run/run_inclusion.py` → `harness.evaluate_argmax` →
   `load_items` against 3b's `run_cell.py` → `load_capability`:
   identical shots slice (`[tuple(s) for s in cap["shots"]][:2]`,
   `N_SHOTS_PRIMARY = 2`), identical `render_prompt`, identical
   `MAX_NEW_TOKENS[cap["answer_type"]]`, identical `verify`, identical
   `HFRunner` (default batch 16, greedy, `do_sample=False`), identical
   `models.load_pythia(size, untrained=..., seed=0)`, same item files.
   A gate-2 divergence at campaign can therefore only be genuine
   stack/model drift — the thing the gate exists to detect. (For
   `reverse_string`'s 2b-produced referent this identity was ruled at
   design time, open item 5, and is not re-litigated.)
2. **The floor space and the scored space coincide.**
   `chance_floors` builds the marginal from ANSWER first characters;
   `score_first_char` compares against PROBE_LABEL first characters. If
   any item had `probe_label[0] != answer[0]`, the floor would not be
   the chance rate of the scored quantity. Checked all 2000 committed
   eval items (500 × 4 rungs, 2c items for three rungs, 2b's for
   reverse_string): **0 divergent items**. The identity holds
   everywhere, so the marginal floor is exactly the modal rate of the
   scored label.
3. **The runner/analyzer item-routing divergence is closed by fact.**
   `run_cell.load_capability` routes reverse_string to exp2b by
   is-file fallback; `analyze_3b.load_battery_items` routes it by the
   explicit `RUNGS_2B` constant. These diverge only if
   `exp2c/battery/items/reverse_string.json` ever exists — verified
   absent (and the 2c tree is closed at `exp2c-closed`). Recorded as
   the mechanism's one asymmetry, benign on this battery.
4. **No first-character quantity exists for any real cell.** No
   `results/` directory under exp3b; the invariant that first-character
   accuracy has never been computed for any real cell/size/mode
   survives the freeze session (the mechanical runs below score
   synthetic continuations and count real ones, never score real ones).

**Findings that are observations, not defects** (no criterion touched):

- Design §3's matrix row calls `clock24_d999` a "1-symbol answer":
  311/500 committed answers are two digits (hours 10–23), so the literal
  phrase is loose. No behavioural consequence: `probe_label[0] ==
  answer[0]` on all 500 (check 2 above), the .496 floor is the marginal
  of exactly the scored first character, the power table's critical
  count 283 is computed against that floor, and the rung never enters
  step 5 — it is gates, Bonferroni count, and the probe-absent quadrant
  only. Left as prose; recorded here.
- `first_char` scoring credits the first character only, so for
  two-digit clock24 answers the behavioural task is the first digit.
  Consistent with §5 ("Character, not token"), the floor, and the rung's
  descriptive role.

## Rulings

The build ledgered two design under-specifications with the instruction
that the freeze must bless or amend explicitly — silence is not a ruling.
Both are BLESSED as implemented, and §6 is amended to say what the code
does. A third wording ambiguity found by this session's cold read is
amended the same way. All three amendments change no behaviour; every
amended reading was pinned by fixtures and mutants at build, before this
session existed.

**Ruling 1 — gate 4 quantifies over the 8 probe-size untrained cells
only.** §6's step 4 said "any untrained cell"; §6's preamble says
eval-size cells take no significance tests. The preamble governs: a
significance test the preamble forbids cannot be the trigger of a
contamination flag, and an eval-size twin fire is a descriptive fact in
the record, contaminating nothing. Pinned at build:
`test_eval_size_twin_fire_is_not_contamination`, battery
`eval_twin_fire_is_not_contamination`, mutant "significance computed for
eval-size cells too" killed. §6 step 4 amended to state the scope.

**Ruling 2 — both reversal rungs contaminated → `INSUFFICIENT_DATA`.** §6
excluded contaminated rungs from step 5's universal quantifiers without
saying what happens when the exclusion empties them. `all([])` is
vacuously true; a vacuous universal quantifier reading as UNITS_ARTIFACT
(or DISSOCIATION) would be the program's exact defect class — an
adjudication with no data behind it. Pinned at build:
`test_both_rungs_contaminated_is_insufficient_data`, battery
`contaminated_both_rungs`, mutant "vacuous quantifier allowed to
adjudicate" killed. §6 step 5 amended with the branch.

**Ruling 3 — gate 1's "both" made explicit (found by this session's
read).** "Not significantly above its floor at both probe sizes" parses
two ways in English: ¬(above at both) — fires if either size fails — or
(¬above) at both — fires only if both fail. The implementation, the
doc's own parenthetical ("this gate fails only if the instrument is
broken" — one blind size is a broken instrument at that size), and the
build's fixtures all take the first reading: the gate passes only when
ctrl_copy clears floor at BOTH probe sizes. Pinned at build:
`test_gate1_requires_both_probe_sizes_not_either`, battery
`id_gate1_ctrl_dead` (ctrl dead at ONE size → INSUFFICIENT_DATA), mutant
"either probe size suffices instead of both" killed. §6 step 1 amended
to the unambiguous phrasing.

## The checklist

| # | item | status |
|---|---|---|
| 1 | Adversarial cold read performed by a session that wrote neither doc nor code, findings recorded even if empty | **GREEN** — this file; defect hunt above came back empty, 2 note-only observations |
| 2 | The two build-ledgered under-specifications ruled on explicitly | **GREEN** — rulings 1–2, blessed + §6 amended |
| 3 | Every verdict input has a defined VALUE on this battery (3a's rule) | **GREEN** — four of five inputs are committed records verified present with values today; the fifth (cells) is shape-refused unless exactly the preregistered 40 |
| 4 | Frozen tree executed to every terminal branch through the frozen loaders | **GREEN** — 9/9 full-shape batteries, re-run cold this session (below) |
| 5 | Fixture suite passes cold | **GREEN** — 77/77 (below) |
| 6 | Mutation testing both directions, cold, corrected harness | **GREEN** — 35/35 killed, baseline clean (below) |
| 7 | Referents verified incl. twin construction (`--construct`) | **GREEN** — 48/48, byte-identical re-run (below) |
| 8 | Floors sha-pinned + recompute-asserted | **GREEN** — `f299fa08…`, executed via `load_floors` in the referent re-run |
| 9 | Per-size probe margins recomputed from seed records, committed, design-asserted | **GREEN** — `probe_margins.json` idempotent re-run, zero diff (below) |
| 10 | Exact power from the frozen floors, committed, design-asserted | **GREEN** — `power.json` idempotent re-run, zero diff (below); blind region [floor, .092) disclosed in §7 |
| 11 | No first-character accuracy computed for any real cell, any size, any mode | **GREEN** — no `results/` dir exists; every scored continuation in the test runs is synthetic |
| 12 | `experiments/exp2b/`, `exp2c/`, `exp3a/` unmodified | **GREEN** — `git status` clean against their closed tags; 3b only reads |
| 13 | Campaign driver committed before the freeze (1c's practice) | **GREEN** — `run/campaign_3b.py` at build commit, dry-run verified |
| 14 | One pre-committed change | **GREEN — UNSPENT** (3a's did not carry over, per §11) |
| 15 | Verdict projection | **RULED — deferred by design** (§10.4): the projection is ledgered in `PROGRESS.md` after the tag and before the frozen analysis runs once; writing it at freeze would collapse the projection step into the freeze the way 3a collapsed its sessions |

## Mechanical re-runs (cold, this session)

Venv `~/emergence-lab/.venv`, repo root, `__pycache__` cleared,
`PYTHONDONTWRITEBYTECODE=1` (3a's corrected harness):

| command | result |
|---|---|
| `python -m pytest experiments/exp3b/tests/ -q` | **77 passed** in 1.01s |
| `python experiments/exp3b/tests/mutation_check.py` | **KILLED 35/35**, baseline clean — two consecutive full passes this session, both clean |
| `python -m experiments.exp3b.tests.full_shape` | **9/9 ok — ALL TERMINAL BRANCHES REACHED**; verdicts and contamination sets exactly as specified (4× INSUFFICIENT_DATA routes, UNITS_ARTIFACT, DISSOCIATION, PARTIAL, one-rung contamination → UNITS_ARTIFACT over the survivor, eval-twin fire → DISSOCIATION uncontaminated) |
| `python experiments/exp3b/verify_referents.py --construct` | **48 checks, 0 failed**; twins constructed twice per size on CPU, state hashes reproduced — `referent_check.json` byte-identical to the build commit (zero git diff) |
| `python experiments/exp3b/compute_probe_margins.py` (idempotency) | design §3 asserts pass; **zero git diff** — byte-identical to build commit |
| `python experiments/exp3b/compute_power.py` (idempotency) | design §7 asserts pass; **zero git diff** — byte-identical to build commit |

All six commands exited 0. The only working-tree changes at tag time are
the freeze session's own documents: the design doc's status flip + §6
amendments, this checklist, and the `PROGRESS.md` freeze section. Code
and committed artifacts are byte-identical to the build commits.
