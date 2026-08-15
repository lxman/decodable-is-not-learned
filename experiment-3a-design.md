# Experiment 3a — Design Doc: The Units Gap Between a Probe and a Behaviour

**Status:** **DRAFT — NOT FROZEN.** Nothing queries a model until §8 step 1
is executed and tagged `exp3a-preregistered`. The instrument will be
`experiments/exp3a/` — `analyze_3a.py` with its own loader, a runner,
and a fixture suite.

**Numbering.** This is not Experiment 3 of `experiments.md` (the
test-time-compute edge, which needs the Sparks). It is a prerequisite
that experiment cannot skip: 3a asks whether the probe-to-behaviour gap
that motivates a sampling campaign is a real dissociation or a units
mismatch. If it is a mismatch, Experiment 3 would be sampling for
something no probe ever claimed.

**Predecessors:** `experiment-2c-design.md` (tag `exp2c-closed`, FAIL),
whose battery, items, prompts, harness and eval records this reads and
does not modify.

---

## 1. What was found, and why it needs its own experiment

The methods paper's strongest real-model claim (§8) is that two
character-reversal capabilities carry the second and third highest
starved probe margins in the Exp 2c battery — .6994 and .6240 — while
scoring an outcome of zero at 2.8b, 6.9b and 12b. Stated there as:
*the information is linearly decodable from the representation, survives
basis starving, and clears the untrained gate, and the model cannot emit
it.*

Reading the committed items rather than the paper:

| | what it measures |
|---|---|
| probe target | `probe_label_space`: "last letter of the 7-letter input (26)" — one character, 1-of-26 |
| eval target | the full reversed string, exact match, 7 characters |

**The probe decodes one character. The eval requires seven.** Those are
not the same information, and a model can hold the first without being
able to emit the seventh. The claim as written compares a 1-symbol read
against a 7-symbol generation and attributes the difference to a
representation-versus-behaviour dissociation.

This is not confined to reversal. Of 27 rungs with committed items,
**14 have an eval answer longer than their probe label** — including
`ctrl_copy`, whose probe reads "first letter (26)" against a 5-character
answer. That `ctrl_copy` shows *no* gap (probe .997, argmax .960/.980)
is what makes this a confound rather than an artifact: the mismatch does
not by itself produce a gap. It does mean the reversal gap cannot be
attributed to dissociation until the targets are matched.

Structurally this is Exp 1's units failure again — comparing quantities
on incommensurable scales and reading the difference as signal — and 2c's
chance-floor defect again, one level over. The program has now made the
same class of error three times, which is the reason to test it rather
than to reason about it.

---

## 2. The test the mismatch makes available

`activations.py:65` and `harness.py:67` build the prompt with the
identical call, `render_prompt(it["question"], shots)`. **The probe and
the eval see the same 2-shot prompt.** They diverge only in what happens
next: a linear readout of one designated character, versus generate-then-
exact-match on the whole answer.

So the matched comparison needs no new prompt and no prompt engineering.
The probe decodes the last letter of the input, which is by construction
the **first** character of the correct answer. Continuing that same
prompt, a model that is reversing must emit that character first.

**Primary measurement: first-character accuracy of the model's
continuation, scored against the probe's own label, on the same prompt.**

Both sides then live in the same 26-way space and normalize the same way
— `(acc − floor)/(1 − floor)` — so probe margin and behavioural margin
are commensurable. Commensurability is precisely what Exp 1 lacked, and
this design gets it by construction rather than by argument.

---

## 3. The matrix

| axis | levels |
|---|---|
| rung | `rev_string7`, `reverse_string` (the claim); `ctrl_copy` (positive control, same mismatch, known generable); `clock24_d999` (matched control, 1-symbol answer) |
| model | Pythia 2.8b, 6.9b, 12b — 2c's eval ladder |
| mode | trained, untrained twin |

4 rungs × 3 sizes × 2 modes = **24 cells**, 500 committed eval items
each. Items, shots and prompts are 2c's, unmodified, verified by the
sha256 in `reuse_manifest.json`.

**The untrained twin is the floor**, per this program's standing
practice, and it is measured on the same items and the same prompt.
Note what §8 of the methods paper establishes about it: an untrained
model emits malformed text, so its floor on a generation task sits at or
near zero for reasons having nothing to do with the capability. **Both
floors are therefore reported** — the untrained twin's rate and the
within-answer-space chance rate — and the second is the one the primary
criterion uses.

**The within-answer-space chance rate is not 1/26.** It is the rate at
which the first character is correct under a null that knows the task's
surface but not the answer. Three are computed and committed before any
model is queried, from the item pool alone:

- `uniform`: 1/26.
- `marginal`: the empirical frequency of the modal first-character over
  the 500 items, which is what "always guess the most common letter"
  achieves.
- `copy-first`: the rate at which the input's **first** character equals
  the answer's first character — i.e. what a model that echoes the input
  instead of reversing it scores. For random 7-letter strings this is
  ≈1/26, but it is measured, not assumed, because a systematic
  generator could make it larger.

The primary floor is the **maximum of the three**, so a degenerate
strategy cannot pass.

---

## 4. Operationalization

**Generation.** 2c's harness verbatim: `render_prompt(question, shots)`
with the committed 2 shots, greedy decoding, `MAX_NEW_TOKENS` for the
rung's `answer_type`. Nothing about the prompt or the decode changes;
if it did, this would not be measuring 2c's own claim.

**Scoring the first character.** Take the model's continuation, strip
leading whitespace, and compare its first character to the item's
`probe_label`, case-folded. Character, not token: the answer's first
character need not be a token boundary, and scoring the first *token*
would silently measure tokenization. A continuation that is empty or
begins with a non-alphabetic character is scored **incorrect**, not
dropped — an unparseable answer is a failure to emit, which is exactly
what is being measured.

**Also recorded, per cell, not adjudicated:** full-string exact-match
accuracy (reproducing 2c's own number, as a replication check), and the
mean length of the continuation.

**The probe side is not re-run.** It is read from the committed
`probe_scores.json` at `exp2c-closed`. This experiment adds a
behavioural measurement to an existing probe measurement; re-fitting the
probe would change what the comparison is about.

---

## 5. Preregistered pass/fail

**Primary quantity.** Per (rung, size): the behavioural margin
`m_b = (acc_first_char − floor)/(1 − floor)`, with `floor` the §3
maximum-of-three chance rate, alongside the committed probe margin `m_p`.

**Verdict tree, adjudicated in this precedence order:**

1. **Positive control fails** — `ctrl_copy` first-character accuracy not
   significantly above its floor at 2 of 3 sizes → `INSUFFICIENT_DATA`.
   An instrument that cannot see a capability the same battery scored
   .96 argmax is not measuring emission.
2. **Replication check fails** — the re-measured full-string accuracy
   for any rung differs from its committed 2c value by more than
   Clopper–Pearson overlap → `INSUFFICIENT_DATA`, discrepancy
   investigated first. This is 2c's own number; if it does not
   reproduce, the harness has drifted and nothing else is trustworthy.
3. **Untrained twin fires** — any untrained cell significantly above its
   floor → reported, and the affected rung's result is marked
   contaminated.
4. **Otherwise adjudicate the claim**, by one-sided binomial test of
   `acc_first_char` against `floor`, α = .01, Bonferroni across the 12
   trained cells:

   - **UNITS ARTIFACT** — reversal first-character accuracy is
     significantly above floor at **all three** sizes. The §8 claim does
     not survive as stated; the gap is between reading one character and
     emitting seven, and the paper must say so.
   - **DISSOCIATION** — reversal first-character accuracy is **not**
     significantly above floor at **any** size, while `m_p` = .699/.624.
     The §8 claim survives in a much stronger form: same prompt, same
     target, same label space, and the model still cannot say it.
   - **PARTIAL** — anything else, reported per cell with the sizes named.

**No outcome is a PASS or a FAIL of a hypothesis I hold.** This
experiment adjudicates a claim already in print under my name, and the
result that costs me most — UNITS ARTIFACT — is the one requiring a
correction to a paper I am about to submit. Recorded here so that
outcome cannot later be softened.

**Effect size the design can resolve.** With n = 500 and a floor near
.038, a one-sided binomial at α = .01/12 detects a true rate of .075
with power ≈ .97 and .06 with power ≈ .74. Anything the probe's .699
margin would plausibly imply about a matched behaviour is far above
that, so a null here is a real null rather than a resolution failure.
Exact power is computed and committed at freeze from the realized
floors.

---

## 6. What the dumbest baseline achieves

| degenerate instrument | outcome |
|---|---|
| model that echoes the input | first char = input's first char; scored against `copy-first`, which the floor already maxes over → fails |
| model that always emits the modal letter | scored against `marginal` → fails |
| model that emits nothing parseable | scored incorrect, not dropped → fails |
| scorer that credits any character | `ctrl_copy` and the matched control would both saturate; the untrained twin would fire → caught by gates 1 and 3 |
| harness that has drifted from 2c | full-string replication check fails → gate 2 |

Five routes. The bar is passable and can genuinely fail.

---

## 7. What Exp 3a does not claim

- **Nothing about sampling.** Greedy decoding only. Whether exhaustive
  sampling elicits the full string is Experiment 3's question and this
  design deliberately does not touch it.
- **Nothing about the other 12 mismatched rungs.** Four rungs are run.
  A units artifact demonstrated on reversal does not establish one for
  `median5` or `antonym6`, though it would make the same test worth
  running there.
- **Nothing about 2c's verdict**, which is closed and stays closed. If
  the primary correlation is affected by this mismatch, that is a
  disclosed descriptive for a successor, not a re-opening.
- **Nothing about model families other than Pythia.**

---

## 8. Run plan

1. **Freeze:** this doc + `analyze_3a.py` + fixture suite, tagged
   `exp3a-preregistered`. The three chance floors are computed from the
   committed items and **committed in the freeze**, before any model
   is queried.
2. **Untrained twins first**, all 12, before any trained cell — 1b's
   sequencing, and under the §5 tree the twins are a gate.
3. **Trained cells**, 2.8b → 6.9b → 12b. Commit per cell.
4. **Analysis:** the frozen script, once, after the verdict projection
   is ledgered in `experiments/exp3a/PROGRESS.md`.
5. **Close-out:** `VERDICT.txt`, retrospective, tag `exp3a-closed`, and
   — whatever the outcome — the corresponding edit to the methods
   paper's §8.

**Cost.** 24 cells × 500 items, a few tokens of greedy generation each.
The 12b model is ~24 GB in fp16 and fits the Mac's 48 GB with headroom;
2.8b and 6.9b are comfortable. This is inference, not training, and the
model loads dominate. Estimate under a day of background wall-clock. The
DGX Sparks stay untouched.

---

## 9. Process rules carried forward

- Thresholds and floors frozen pre-run; analysis script committed with
  the doc, **with its own loader** (1b's gap, and 1c reproduced it one
  level over — see below).
- **Freeze a producer for every input the verdict function takes**, not
  only the primary statistic. 1c shipped a `verdict()` taking a
  diagnostic it had no frozen way to compute. Mechanical check at
  freeze: every parameter of the adjudication entry point has a frozen
  producer or a fixture pinning its value.
- **One pre-committed change** — available once, reason ledgered before
  the change.
- Verdict projection ledgered before the analysis runs.
- Every zero as a Clopper–Pearson bound.
- Per-cell results reported as headline, not caveat.
- Commit per cell; expect `-dirty` provenance if cells run in parallel,
  and disclose it rather than serializing for a cosmetic sha.

---

## Open items before first run

1. `analyze_3a.py` + fixture suite, one synthetic case per preregistered
   provision, mutation-tested in both directions.
2. Runner reusing 2c's `harness.evaluate_argmax` path for the
   full-string replication and adding first-character scoring alongside,
   with skip-if-exists durability.
3. Compute and commit the three chance floors from the committed items.
4. Confirm the 12b untrained twin can be constructed at 2c's
   `untrained_seed` and that its records reproduce 2c's own untrained
   eval numbers where they exist.
5. Decide whether `MAX_NEW_TOKENS` for the reversal rungs is large
   enough that a first character is always emitted — if the cap can
   truncate before any character appears, the metric is measuring the
   cap.
