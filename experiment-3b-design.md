# Experiment 3b — Design Doc: The Same-Weights Test of the Reversal Dissociation

**Status:** **FROZEN 2026-08-15, tag `exp3b-preregistered`.** Designed,
built and frozen in three separate sessions (boundary = context clear;
Michael's pacing ruling — 3a compressed design-freeze-run-close into
hours, and the defect that closed it was discoverable by any cold read).
The freeze session opened adversarially, assignment "find the 3a-class
defect"; findings, rulings and the mechanical re-runs are recorded in
`experiments/exp3b/FREEZE_CHECKLIST.md`. §6 was amended at freeze —
behaviour identical, every amended reading already fixture-pinned at
build: gate 1's both-sizes requirement made explicit, gate 4 scoped to
the probe-size twins, step 5 given its contamination-emptied
`INSUFFICIENT_DATA` branch. The instrument is `experiments/exp3b/` —
`analyze_3b.py` with its own loaders, the runner, the committed campaign
driver, and the 77-fixture suite.

**Predecessors:** `experiment-3a-design.md` (tag `exp3a-closed`,
INSUFFICIENT_DATA — the frozen verdict could not execute on its own
battery; the primary statistic was never computed, which is what makes
this re-freeze meaningful rather than cosmetic). Exp 2c
(tag `exp2c-closed`) and Exp 2b (tag `exp2b-closed`), whose items,
prompts, harness, probe records and inclusion records this reads and
does not modify.

---

## 1. The hypothesis under test

The program's standing hypothesis, unchanged since the essay: capability
structure exists in the representation before behaviour shows it, and
"emergence" is a detection event, not a birth. The testable corollary: a
sensitive instrument should find a capability inside a model before the
model can perform it.

After seven experiments, that hypothesis has exactly one surviving
real-model datum. Character reversal carries the second and third
highest basis-starved probe margins in the 2c battery while scoring an
outcome of zero at every eval scale — the model appears to *know*
something it cannot *say*. Everything else on a real model came back
negative (2c's rank prediction) or was consumed by instrument repair
(2, 2b — the methods paper).

That datum is currently uncitable, because the comparison behind it is
unfair twice over:

1. **Units.** The probe decodes ONE character ("last letter of the
   7-letter input"); the eval requires SEVEN, exact match. 3a was built
   to fix this and closed before computing anything.
2. **Scale.** The probe margins live at 410m and 1b (`PROBE_SIZES`,
   `exp2b/models.py:25`); the zero emission lives at 2.8b/6.9b/12b
   (`EVAL_SIZES`). "Linearly decodable and the model cannot emit it"
   compares a read of one model against a generation from a different
   one. 3a fixed the units mismatch and inherited this one.

3b makes the comparison fair on both axes at once: **same weights, same
prompt, same one-character target, same 26-way label space.** The probe
reads the answer's first character off the residual stream of the 410m
and 1b models at margins .63 and .77. Can those same models emit that
character?

**Two outcomes, named in advance, both informative:**

- **DISSOCIATION** — first-character emission sits at floor on the same
  weights the probe reads at .77. Information demonstrably present that
  the model's output path does not use: the first real-model support for
  the hypothesis, and Experiment 3 (is it elicitable by sampling?)
  becomes the natural next test.
- **UNITS_ARTIFACT** — first-character emission clears floor once the
  target is matched. The famous zero was a metric cliff:
  exact-match-on-seven scored a partial capability as absent, a
  Schaeffer-style manufactured zero in our own frozen record. The
  methods paper's §8 is corrected, and the hypothesis's real-model
  support stands honestly at nothing.

Neither is a PASS of a hypothesis I hold; the outcome that costs most —
UNITS_ARTIFACT — is the one requiring a correction to a paper about to
be submitted. Recorded so it cannot later be softened.

---

## 2. Why 3b will not die 3a's death

3a closed INSUFFICIENT_DATA because its replication gate did
`float(c["committed_2c_acc"])` and `ctrl_copy` has no committed eval
record at 2.8b/6.9b/12b — a producer existed, its value was `None`, and
the frozen tree crashed before any adjudication. Four changes close that
class of defect, not just that instance:

1. **The primary moves to the probe sizes** — which is where the
   positive control's committed generation records actually live.
   `ctrl_copy` was argmax-evaluated at 410m/1b by 2c's inclusion screen:
   .960 and .980, 500 items, trained and untrained, on disk. The rung 3a
   leaned on hardest and could not check is the best-instrumented rung
   at 3b's primary sizes.
2. **Every cell has a committed referent with a defined value** (§4),
   verified at freeze by rule 3.
3. **New freeze rule:** the frozen verdict is executed against synthetic
   full-shape batteries that exercise **every terminal branch** — each
   gate firing and each verdict — end to end through the frozen loader.
   1c's lesson was "freeze a producer for every input"; 3a showed a
   producer can exist and return `None`. The check is now on values,
   not producers.
4. **The eval-size replication gate becomes byte-identity against 3a's
   own continuations**, which exist for all 24 overlap cells by
   construction — there is no cell whose referent can be missing.

---

## 3. The matrix

| axis | levels |
|---|---|
| rung | `rev_string7`, `reverse_string` (the claim); `ctrl_copy` (positive control — same units mismatch, known generable, committed .960/.980 at the primary sizes); `clock24_d999` (matched control — 1-symbol answer, no units gap, probe margin 0.0) |
| model | **410m, 1b — primary** (where the probes were fit); 2.8b, 6.9b, 12b — descriptive only, no verdict branch reads them |
| mode | trained, untrained twin (2c's `untrained_seed = 0`) |

4 rungs × 5 sizes × 2 modes = **40 cells**, 500 committed eval items
each, 2c's prompts, shots and greedy decode verbatim.

**3a's 24 collected cells are the reproduction referent, not the data**
(Michael's ruling, `exp3a/results/retrospective.md` §4). 3b re-collects
all 40 cells; the 24 that overlap 3a must reproduce byte for byte, since
greedy decoding over fixed prompts is deterministic — 3a itself
reproduced 2c's committed accuracies exactly on all nine cells that had
one. Estimated inference: ~100 minutes, model loads dominating. The DGX
Sparks stay untouched.

**The probe side is not re-run.** Per-size margins are read from the
committed m3 records and quoted per size, never pooled:

| rung | 410m | 1b | source |
|---|---|---|---|
| `rev_string7` | .6263 | .7725 | `exp2c/results/probes/m3/` (5 seeds, mean) |
| `reverse_string` | .5731 | .6749 | `exp2b/results/probes/m3/` (5 seeds, mean) |

(Seed-level values are committed; these means are recomputed and
committed at freeze. The pooled ".699/.624" of the paper's §8 does not
appear in this experiment's criteria — citing a mean over two models was
part of the original confound.)

---

## 4. Referents — every cell, a committed value

| cells | referent | location | values |
|---|---|---|---|
| 16 probe-size | full-string argmax acc, inclusion screens | `exp2c/results/inclusion/{size}_{mode}/{rung}.json`; `reverse_string` from `exp2b/results/inclusion/` | ctrl_copy .960/.980 tr, 0/0 un; rev_string7 0×4; reverse_string 0×4; clock24_d999 .036/.048 tr, 0/0 un |
| 24 eval-size | raw continuations, 3a campaign | `exp3a/results/{size}_{mode}/{rung}.json` | all 24 cells, 500 continuations each |

The eval-size byte gate subsumes 3a's acc-replication gate: byte-equal
continuations imply equal accuracies, and 3a already matched 2c's m4
committed values exactly wherever they existed. No branch of 3b compares
against m4, so the record that is missing for `ctrl_copy` there is not
an input to anything.

**The one cross-harness referent is confirmed compatible** (checked
2026-08-15, at design time). `reverse_string`'s inclusion records were
produced by 2b's harness; every element of that decode path is identical
to the 2c harness 3b runs: `render_prompt`, `normalize_answer`, `verify`
(2c's are "2b scoring, verbatim"), `MAX_NEW_TOKENS`
(`{"number": 8, "word": 12, "letters": 12, "choice": 6}` in both),
`N_SHOTS_PRIMARY = 2`, `evaluate_argmax`, `HFRunner.generate` (greedy,
`do_sample=False`, batch 16), and the tokenizer/model constructors —
3b imports `models` *from* exp2b. `reverse_string`'s `answer_type` is
`"word"` inline in the 2b item file, which is what 3b's loader reads.
A gate-2 divergence on this rung can therefore only be genuine
stack/model drift — the thing the gate exists to detect — not harness
provenance.

---

## 5. Operationalization

Reused from 3a's frozen instrument, verbatim where possible:

- **Generation:** 2c's `render_prompt(question, shots)`, committed 2
  shots, greedy, 2c's `MAX_NEW_TOKENS` (12 for `word` — max answer
  length 7 tokens, measured at 3a's freeze). Raw continuation stored per
  item; everything downstream is recomputable without re-querying.
- **First-character scoring:** first non-whitespace character of the
  continuation, case-folded, against the item's `probe_label` — **not**
  `isalpha()`-gated (3a's mutation testing caught that `clock24_d999`'s
  label is a digit and the alphabetic filter zeroed the control).
  Empty/whitespace-only continuations score incorrect, not dropped.
  Character, not token.
- **Floors:** 3a's committed `chance_floors.json`, reused and pinned by
  sha256; the frozen 3b module recomputes them from the items and
  asserts equality. Max of uniform (1/26), marginal (modal first
  character), copy-first (echo strategy), with `copy_is_the_task`
  derived from the items (`copy_whole > 0.5`) so the copy floor is
  excluded exactly where copying is the capability: rev_string7 .056,
  reverse_string .054, ctrl_copy .052, clock24_d999 .496 — all marginal.
- **Normalization:** behavioural margin `m_b = (acc − floor)/(1 − floor)`,
  reported beside the per-size probe margin `m_p`. Both live in the same
  26-way space; the probe's floor is its permutation null, the
  behaviour's is the max-of-three chance rate — both are competence
  floors in the label space, and the difference in construction is
  stated wherever the two margins are shown together.
- **Also recorded, never adjudicated:** full-string exact-match acc
  (the gate-2/gate-3 quantity), mean continuation length, and the
  eval-size descriptives.

---

## 6. Preregistered verdict tree

Adjudicated in precedence order. Significance = one-sided exact
binomial against the rung's committed floor, α = .01, Bonferroni across
the **8 probe-size trained cells** (4 rungs × 2 sizes). Untrained cells
test at n_tests = 1, per 3a. **Eval-size cells take no significance
tests**: they are descriptives, and no branch below reads them except
gate 3's byte comparison.

1. **Positive control fails** — `ctrl_copy` first-character accuracy
   fails significance against its floor at **either** probe size; the
   gate passes only when it clears at **both**, because one blind size
   already invalidates the instrument (wording amended at freeze — the
   original "not significantly above at both" parsed two ways; the built
   reading was already pinned by
   `test_gate1_requires_both_probe_sizes_not_either` and battery
   `id_gate1_ctrl_dead`) → `INSUFFICIENT_DATA`. A harness that cannot
   see emission on a rung
   committed at .960/.980 full-string is not measuring emission. (First
   character ≥ full string by construction, so the expected value is
   ≥ .96 against a .052 floor; this gate fails only if the instrument is
   broken.)
2. **Replication fails** — any of the 16 probe-size cells' full-string
   accuracy is incompatible with its committed inclusion referent, by
   non-overlap of 95% Clopper–Pearson intervals → `INSUFFICIENT_DATA`,
   discrepancy investigated before anything else is read. (For the
   exact-zero referents this tolerates ≤ 8/500 before firing; for
   ctrl_copy's .960 it tolerates roughly ±.025.)
3. **Byte gate fails** — more than 2 of 500 continuations differ from
   3a's stored referent in any of the 24 overlap cells →
   `INSUFFICIENT_DATA`. Greedy decoding is deterministic on this stack;
   a tolerance of 2 exists only because an exact-tie argmax flip is
   physically possible, and a gate that can kill the experiment over one
   flipped tie is 3a's crash with better manners. Every differing item
   is disclosed verbatim in the record regardless of count.
4. **Untrained twin fires** — any **probe-size** untrained cell
   significantly above its floor → reported, affected rung marked
   contaminated and excluded from step 5's universal quantifiers. The
   scope is the 8 probe-size twins only, per this section's preamble:
   eval-size cells take no significance tests, so an eval-size twin fire
   is a descriptive fact in the record and contaminates nothing (scope
   amended at freeze to state the built reading, ruling 1 in the freeze
   checklist; `test_eval_size_twin_fire_is_not_contamination`, battery
   `eval_twin_fire_is_not_contamination`).
5. **Adjudicate the claim** on the 4 reversal trained cells at the probe
   sizes (`rev_string7`, `reverse_string` × 410m, 1b), quantifying over
   the cells step 4 left eligible:
   - **UNITS_ARTIFACT** — significantly above floor in **all** eligible
     cells (all 4 when nothing is contaminated).
   - **DISSOCIATION** — significantly above floor in **none** of the
     eligible cells, against same-weights probe margins .63/.77
     (rev_string7) and .57/.67 (reverse_string).
   - **PARTIAL** — anything else, reported per cell with sizes and rungs
     named as headline, not caveat.

   If contamination has emptied the eligible set — both reversal rungs
   excluded — the claim has no cells to quantify over and the verdict is
   `INSUFFICIENT_DATA`: `all([])` is vacuously true, and a vacuous
   universal quantifier must not be allowed to adjudicate (branch
   added at freeze, ruling 2 in the freeze checklist;
   `test_both_rungs_contaminated_is_insufficient_data`, battery
   `contaminated_both_rungs`, mutant "vacuous quantifier allowed to
   adjudicate" killed at build).

`clock24_d999` participates in gates and in the Bonferroni count but not
in step 5: it is the no-units-gap, probe-absent quadrant of the 2×2, and
its role is to show what agreement between probe and behaviour looks
like at these sizes.

---

## 7. Power, and the region this design cannot see

n = 500 per cell. Against floor .056 at α = .01/8, the critical count is
46/500 (acc .092): power .98 at a true rate of .12, .75 at .10, .09 at
.075. Floor .054 moves the critical count to 44.

**The blind region is [floor, ≈.09].** A true first-character rate of
.07 — emission barely above chance — is indistinguishable from floor
here and would read DISSOCIATION. Stated up front, 1c's practice: a
DISSOCIATION verdict means "no emission this design can resolve," not
"exactly zero emission," and every zero cell carries its Clopper–Pearson
upper bound. Against same-weights probe margins of .63–.77, the effects
worth arguing about sit far above .092; what the blind region could miss
is a weak-partial-emission world, and that limitation is disclosed in
the verdict text itself. Exact power is recomputed at freeze from the
frozen floors file and committed.

---

## 8. What the dumbest baseline achieves

| degenerate instrument | outcome |
|---|---|
| model that echoes the input | scored against `copy_first`, which the floor maxes over → fails |
| model that always emits the modal letter | scored against `marginal` → fails |
| model that emits nothing parseable | scored incorrect, not dropped → fails |
| scorer that credits any character | ctrl_copy saturates but the untrained twins fire → gates 1 and 4 |
| harness drifted since 2c/3a | inclusion replication or byte gate → gates 2 and 3 |
| verdict input with no value on this battery | impossible to freeze: the synthetic full-shape batteries must reach every terminal branch before the tag |

Six routes. The bar is passable and can genuinely fail.

---

## 9. What Exp 3b does not claim

- **Nothing about sampling.** Greedy only. DISSOCIATION makes
  Experiment 3's elicitation question worth asking; it does not answer
  it.
- **Nothing beyond the probe sizes.** The primary claim is about 410m
  and 1b, where the probes live. The eval-size descriptives will show
  whether the pattern continues upward, but no verdict branch reads
  them, and a DISSOCIATION at 1b is not evidence about 12b.
- **Nothing about the other 12 mismatched rungs**, the other families,
  or model families other than Pythia.
- **Nothing about 2c's verdict**, which stays closed.
- **No probe re-fitting.** The probe side is read from committed
  records; re-fitting would change what the comparison is about (and
  probe-at-eval-sizes is a 3c, not this experiment).

---

## 10. Run plan

1. **Build, later session:** `analyze_3b.py` (loader frozen with it) +
   runner + fixture suite, mutation-tested both directions under the
   corrected harness (3a's stale-`.pyc` fix).
2. **Freeze, cold:** re-read this doc in a session that did not write
   it; execute the synthetic full-shape batteries through every terminal
   branch; commit floors-sha pin, per-size probe margins, exact power;
   tag `exp3b-preregistered`.
3. **Campaign:** driver committed before the first cell (1c's practice,
   3a skipped it and ate a post-freeze correction). Untrained twins
   first, all 20, then trained 410m → 1b → 2.8b → 6.9b → 12b. Commit per
   cell.
4. **Analysis:** verdict projection ledgered in
   `experiments/exp3b/PROGRESS.md`, then the frozen script, once.
5. **Close-out:** `VERDICT.txt`, retrospective, tag `exp3b-closed`, and
   — whichever branch — the corresponding edit to the methods paper's
   §8. UNITS_ARTIFACT rewrites the claim; DISSOCIATION strengthens it to
   same-weights; PARTIAL states the split. INSUFFICIENT_DATA at this
   point, on a battery whose every referent was value-checked at freeze,
   would mean the freeze rule itself failed and gets its own
   retrospective.

---

## 11. Process rules carried forward

- Thresholds, floors and referents frozen pre-run; analysis committed
  with the doc, with its own loader.
- **Every input the verdict takes has a defined VALUE on this battery,
  demonstrated at freeze by executing the frozen tree to every terminal
  branch on synthetic full-shape batteries.** (3a's lesson, superseding
  1c's producer rule, which it contains.)
- **The freeze happens in a session later than the design**, after a
  cold re-read. (Michael's pacing ruling, 2026-08-15: the compressed
  cycle is what ships design-time-discoverable defects.)
- One pre-committed change — available once, reason ledgered before the
  change. 3a's remains unspent and does not carry over.
- Verdict projection ledgered before the analysis runs.
- Every zero as a Clopper–Pearson bound.
- Per-cell results as headline, not caveat.
- Per-size probe margins only; the pooled .699/.624 appears nowhere in
  the criteria.
- Commit per cell; disclose `-dirty` provenance rather than serializing
  for a cosmetic sha.

---

## Open items before freeze

**All seven closed before the tag** — 1–4, 6 and 7 in the build session
(`experiments/exp3b/PROGRESS.md`, commits fbf7819…bb63b54), 5 at design
time (struck below). Freeze evidence: `experiments/exp3b/FREEZE_CHECKLIST.md`.

1. `analyze_3b.py` + fixture suite, one synthetic case per preregistered
   provision, mutation-tested in both directions.
2. Runner with skip-if-exists durability, `_assert_module_provenance`
   guard (2c harness / 2b models), committed campaign driver.
3. Synthetic full-shape batteries reaching all six terminal outcomes
   (INSUFFICIENT_DATA ×3 routes, UNITS_ARTIFACT, DISSOCIATION, PARTIAL),
   **plus one with a contaminated rung** — step 4 modifies step 5's
   quantifiers, and that interaction is where an untested branch hides —
   executed at freeze, results in the freeze checklist.
4. Recompute per-size probe margins from the m3 seed records; commit
   alongside the floors sha-pin.
5. ~~Confirm 2b's inclusion decode parameters match 2c's harness for
   `reverse_string`.~~ **RESOLVED 2026-08-15 (design time, ruled by
   Michael):** verified identical element by element — see §4. Gate 2
   freezes over the 2b referent as written, no special-casing.
6. Exact power from the frozen floors, committed.
7. Confirm the probe-size untrained twins construct at `untrained_seed=0`
   and that their inclusion records' shas match the checkpoints 3b
   loads.
