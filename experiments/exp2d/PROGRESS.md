# Exp 2d — Progress Ledger

Chronological, newest entry last inside each dated block. The design
doc (`experiment-2d-design.md`) stays as ruled in session 1 (§12);
everything the build discovered that touches doc TEXT or a dial is
ledgered here for freeze ratification, never silently absorbed (3c's
convention).

---

## 2026-08-21 — BUILD SESSION (session 2 of 3 of design | build | freeze)

Instrument built at `experiments/exp2d/`:

- `battery_2d.py` — the 34 rungs / 16 families in 2c's verdict order
  (`RUNG_ORDER_2D`, family-contiguous; checked against BOTH committed
  sources: `family_map.scored_battery_families()` and
  `probe_scores.json`'s row order — the block layout 2c's permutation
  machinery exchanges position-for-position); 34 item-file sha pins by
  literal (the 12 survivors' also == 2c's reuse manifest — three
  sources, one value); answer-type pins re-asserted against the SPECS
  registry; 2c's `MAX_NEW_TOKENS` per rung; the MAJORITY-ANSWER FLOOR
  (ruling a) under 2c's own `normalize_answer`, with §4's printed
  table as a known-answer referent; the option-copy DESCRIPTIVE
  (finding H below; enters no verdict branch).
- `stats_2d.py` — the one-sided exact binomial bar at α .01 (both
  sides identically), the corrected margin, the midrank AUC, 2c's
  EXACT FAMILY-BLOCK PERMUTATION GROUP with the AUC as the statistic
  (generators, routing and p-value conventions IMPORTED from
  `exp2c/run/power_table.py`: enumerate ≤ 5e6, else 100,000 seeded
  draws with add-one p), the family-cluster bootstrap with undefined
  resamples DROPPED AND COUNTED (fix i; computed from rung
  multiplicities through the pairwise matrix, proved identical to the
  expanded-multiset midrank AUC), 2c's Spearman block test and
  bootstrap for the ordering secondary, and the §6 tree as a pure
  function so the power procedure runs the verdict's own code.
- `analyze_2d.py` — every §4 pin (17 frozen-import shas; exp3's 4
  reversal shards + 4 redecode records by literal; the gate-1
  expected-fire addresses; the twin totals; 2c's verdict literals;
  a 250-file referent manifest `referents_2d.json` whose own sha is a
  literal), the loaders (outcome with the m5 KNOWN-ANSWER GATE;
  pilot/main tiers re-tallied from raw bytes with 3c's total verify
  and stored tallies refused on disagreement; gate-1 records with
  coverage/seed/sha/fires pinned AND the analyzer's own recomputation
  of the comparison from the main draws it loaded; argmax records
  re-verified; probe predictor; twin through exp3's own loader; the
  power record as a required input), `verdict_2d` (primary + every
  §5.4 secondary + the from-below-performability restriction + the
  §5.4 pair with verbatim fires + the percolation-candidate rule) and
  `run()`.
- `rederive_2d.py` — GATE 1 ON THE PRODUCTION PATH: the main tier's
  freshly sampled seed-0 rows for the two reversal rungs compared to
  exp3's committed bytes through 3d's `diff_seed` (imported), coverage
  pinned at 500 × 64 around the comparator (3d F2), committed shard
  hashed against the §4 literal BEFORE comparison (3c B), fires
  recorded by address; the record is written first and ANY diff
  raises — the runner writes the rows to a `.HALTED` file (never the
  normal draws file, so skip-if-exists cannot treat a halted rung as
  done) and the campaign stops.
- `compute_power_2d.py` — the frozen §7 procedure (finding F below)
  + the build-time ENVELOPE (finding G) → `power_envelope_2d.json`.
- `stream_map_2d.json` (136 cells; seed-0 reversal entries == exp3's
  committed map, asserted), `referents_2d.json` (250 files),
  `make_referents_2d.py`, `verify_referents_2d.py` (14-check battery),
  `run/run_cell_2d.py` (tiers pilot | main | argmax; frozen order
  executable: main refuses without both pilot tiers AND
  `power_2d.json`; argmax refuses without both main tiers + clean
  gate 1; any gate-1 diff on record halts every tier),
  `run/campaign_2d.py` (tier-per-process, preflight per size),
  `run/commit_watcher_2d.sh`, `projection_template.md`, fixture suite
  + full-shape worlds + mutation battery under `tests/`.

**Invariant held: ZERO model contact this session — no weights, no
forwards, no tokenizer files, no new sampled quantity for any cell.**
Every committed-byte step (floors, outcome, gate-1 comparator on
exp3's own rows, twin, referents) reads closed trees only.

### Build results

1. **Floors reproduce §4's printed table exactly** for all 34 rungs
   (with two doc slips, finding B). Every floor ≥ 1/500 (reverse_string,
   rev_string7, base7, oct2dec at .002 with |A| = 500).
2. **The outcome known-answer gate PASSES 34/34**: 2c's own
   `m5_ascent.rung_ascent_score` on the committed m4 records
   reproduces `ascent_scores.json` rung for rung (ascent and every
   per-size margin, exact equality).
3. **The frozen §5.2 rule yields 13 RISING / 21 FLAT** (the doc's
   by-eye "~11/23" missed count_div13 — 6.9b and 12b at .204 vs floor
   .158, p = .0037 — and sub4_mid — 12b at .024 vs .006, p = 6.6e-5);
   12b-only sensitivity: 12 (sub3_mid drops out, .022 at 12b, p .097).
   Rising: add3_mid, add_base8, antonym, antonym6, arith_next,
   count_div13, median5, median7, odd6, odd_one_out, sub3_mid,
   sub4_mid, sub_base8. **SEVEN families carry them** (doc §5.3 says
   six): three mixed (mid_digit 3/4, seq_extrap 1/2, counting 1/2),
   four all-rising (antonym, order_stat, odd_one_out, base_arith);
   nine families all-flat. Both numbers are OUTPUTS of the frozen rule,
   as the doc says they would be; the prose should be brought current
   (finding C).
4. **The block-permutation group for the pinned family vector
   (4,2,2,4,2,2,1,2,1,1,2,4,2,2,1,2) is 3!·9!·4! = 52,254,720 > 5e6 →
   SAMPLED at 100,000 seeded draws** — the same routing 2c's verdict
   took on the same vector (`method: sampled`, n_perms 100,000,
   resolution 1e-5). The perm matrix is byte-equal to what
   `exact_block_p` generates (fixture). The AUC over all 100,000 rows
   is one gather + one matvec (~10 ms); the bootstrap ~50 ms.
5. **Gate-1 comparator known-answer check on committed bytes**: exp3's
   own seed-0 rows through `compare_rows` → 0 diffs in all four cells,
   32,000 draws compared each, fires == the pin (item 436 / draw 6 at
   reverse_string/1b; none elsewhere); one altered draw → exactly one
   diff at its address; a 499-item stream refused.
6. **Twin referent** re-asserted through exp3's own loader: 0 verified
   / 512,000 reversal + 64,000 control draws.
7. **Full-shape worlds** (synthetic predictor on the REAL known outcome
   and the REAL committed reversal streams): W1 PASS (AUC 1.0, block p
   3.4e-4, CI [1, 1]), W2 FAIL (AUC .430, CI [.243, .592]; both §5.4
   rungs land as percolation candidates by construction), W3
   INDETERMINATE (six rising rungs positive, one per family: AUC
   .7308, block p .0107, CI [.636, .85] — CI excludes .5, neither
   PASS condition met), W4 INSUFFICIENT_DATA (one altered draw at
   reverse_string/1b item 7 draw 11 → gate 1 fires; the mutated draw
   is disclosed verbatim in the verdict). Every terminal reached
   through `run()` end to end. A fifth world exercises the
   from-below-performability restriction (two rising rungs
   performable at 1b → removed, restricted primary 11/21, the primary
   untouched).
8. **Cold battery at build:** fixture suite 71 at the first cold run, 85 after the mutation closures (9 files), referent
   battery 14/14, full-shape 4 terminals + 1 restriction world,
   mutation battery **76/78 killed** (detail below).

### Mutation battery (`tests/mutation_check.py`, 78 mutants, both directions)

Run 1 (detached, baseline clean): 59/78 killed, 19 survivors. Triage:
three equivalent mutants, sixteen fixture gaps — constants read back
from the module instead of pinned by literal (perm seed/sample size,
bootstrap seed/count, power bar/target), provisions covered only by
the world tests the battery deselects (restriction, percolation
conjuncts), and refusals with no direct fixture (answer-type pin,
probe-order and manifest checks, outcome n pin, frozen-import check,
referent re-hash, twin totals, truncated-vs-held rising rungs). Closed
by literal-pin fixtures, a row-wise sampled-group fixture for the
block statistic, two pure factor-outs (`percolation_candidates`,
`check_twin_totals`) with unit tests, `check_order_against_2c`
taking the two committed-source paths as parameters, and the
restriction world test renamed into the selected set. Run 2 on the
19: 17 killed. **Final: 76/78 killed; 2 documented equivalents:**

- [1] `significant = p < α` without `rate > floor`: with a one-sided
  `greater` binomial, p < .01 already implies k > n·floor — the
  conjunct is belt-and-braces, unreachable by any input.
- [36] floor replaced by max(floor, untrained acc + ε): no committed
  untrained-twin accuracy EXCEEDS its rung's floor (102 records; the
  closest is oct2dec/12b, untrained .002 = floor .002, whose trained
  accuracy .002 clears neither), so no margin moves and the mutant is
  equivalent on the committed outcome records; the untrained column
  is printed, never used, as §5.2 says. (A synthetic outcome tree
  would separate it; altering one committed record fires the
  known-answer gate first, by design.)

Mutant [11] (x's ranks permuted instead of y) survived run 1 as a
mathematically equivalent mutant over an ENUMERATED group (closed
under inversion) and is now killed by a row-for-row fixture on the
sampled 100,000-row group. Suite after the closures: 85 fixtures.

### Findings for ratification (doc slips A–E, build dials F–L)

**A. §11 "four answer types" → TWO.** The battery uses only `number`
(8 tokens, 23 rungs) and `word` (12 tokens, 11 rungs); 2c's `letters`
and `choice` budgets never occur. The freeze's totality assignment
covers two emission alphabets, not four.

**B. §4 floor clause slip.** base12_digitsum and base13 are listed
among "floors ≤ .010"; their accuracies ARE ≤ .006 at every size as
stated, but their majority floors are .038 and .068 (answer '2' in
both). Pinned at the computed values (`DOC_FLOOR_SLIPS`).

**C. Prose counts to bring current:** 13/21 rising/flat in 7 families
(item 3), not "~11/23" and "six of sixteen". The bootstrap drop rate
is correspondingly lower than the doc anticipates (W1: 2 of 10,000
resamples dropped).

**D. §5.3 null: prose vs machinery.** The prose says "the rising
label is exchangeable across rungs *within families*"; the machinery
named in the same sentence (2c's `exact_block_p`) exchanges whole
FAMILY BLOCKS among same-size families, position-for-position, with x
fixed to rung identity. The build implements the NAMED MACHINERY. The
within-family reading would permute labels inside each family: its
group size on the realized outcome is Π_f C(n_f, r_f) =
C(4,3)·C(2,1)·C(2,1) = 16 (all-rising and all-flat families
contribute 1), resolution 1/16 = .0625 — **p < .01 is unreachable
under that reading**, so the prose cannot be the intended null. Ratify
the block reading and fix the sentence.

**E. CP convention.** The doc's "CP ≤ 7.5e-4 at 4,000 draws" (§7) and
"CP95 ≤ 9.4e-5 at 32,000" (§3, §5.4, fix j) are one-sided
rule-of-three figures; the program's `clopper_pearson` (2c's harness,
two-sided 95%, the convention since Exp 2) gives **9.22e-4** and
**1.153e-4**. The disconfirmer's zero-count statement is unaffected;
the instrument's caps and bounds use the two-sided figures. Recommend
correcting the doc's numbers to the program convention.

**F. The power procedure as built (§7 left it to the build).** A
Tobit latent model: L ~ N(μ, 1), score = max(0, L − τ); non-rising
μ = 0, rising μ = d. τ = Φ⁻¹((z0 + ½)/(n0 + 1)) from the pilot's
NON-RISING zero fraction (zero = pilot corrected predictor score 0;
continuity-corrected so τ is finite at 21/21). d solved by bisection
on the exact population AUC (quadrature; MC-verified) for AUC_true ∈
{.5 (α check), .75, .85}. Ties honoured: non-rising pilot zeros HELD
at 0; other non-rising rungs draw from the positive part. Rising
rungs at RAW zero in the pilot (0 verified at BOTH sizes, 8,000
draws) are drawn from the alternative truncated at the pilot CP bound
mapped to score units, cap_g = max(0, (9.22e-4 − c_g)/(1 − c_g)) —
**which is 0 for every rung because every floor ≥ .002**: under the
floor rule the pilot's raw zero set IS main's zero set; §7's "upper
bound" is tight. (A rising rung raw-zero at one size only is not
truncated.) Every simulated battery is judged by the verdict's own
`primary_test` + `verdict_tree` (same perm matrix, same bootstrap
draws). N_SIMS 2000 per target, seed 20260821. Declared underpowered
iff P(PASS | .85) < .75; the declaration target is always computed.
Main runs regardless (ruling c). **Ratify each choice.**

**G. ENVELOPE (the build's central power fact; `power_envelope_2d.json`,
300 sims per cell, AUC_true .85):**

| flat rungs at pilot zero | rising raw-zero 0 | 2 | 4 | 6+ |
|---|---|---|---|---|
| 10 of 21 (τ −.06) | .81 | .40 | .00 | .00 |
| 16 of 21 (τ +.67) | .69 | .32 | .00 | .00 |
| 21 of 21 (τ +2.0) | .87 | .64 | .37 | .00 |

**The PASS bar (AUC ≥ .75 with block p < .01) is unreachable once
more than ~3 of the 13 rising rungs have zero sampled margin**: each
silent rising rung ties with every flat zero and contributes ½ per
pair, and the expected realized AUC falls by ~.05 per silent rung
(.856 → .50 at 13). The declared status after the pilot will be
decided almost entirely by how many rising rungs the 410m/1b sampler
is silent on. This is structural to a class-level AUC on 13 vs 21,
not a defect — but it means the pilot's output is effectively the
power statement, and the freeze should read it knowing that.

**H. OPTION-COPY — a floor-rule observation for Michael's ruling.**
Six rungs present the answer among options LISTED IN THE QUESTION:
antonym (4 options → copy-one-at-random scores .25), antonym6 (6,
.167), median5 (5, .2), median7 (7, .143), odd6 (6, .167),
odd_one_out (4, .25). **All six are in the rising 13.** The majority
floor (ruling a) is .008–.026 on them and does not see option-copying.
Against an option-copy floor (binomial bar, 500 items): antonym and
antonym6 clear at every size; median5 clears at 12b only (.262,
p ≈ 2e-4); odd6 at 6.9b only (.214, p ≈ .004); **median7
(.156/.144/.170 vs .143) and odd_one_out (.162/.250/.208 vs .25)
clear at NO size** — under max(majority, option-copy) the rising set
would be 11/23 and order_stat and odd_one_out would become mixed
families. On the predictor side the same hole is symmetric: a 410m/1b
model that has learned only "answer with one of the listed options"
samples a verified draw at ~1/n, far above the majority floor, so
those rungs would be predicted rising by format competence alone —
2c's lesson 1 in a new guise, on both sides at once, which is exactly
the kind of agreement an AUC rewards. Options: (i) keep ruling a as
frozen and disclose; (ii) floor = max(majority-answer, 1/n_options)
for the option-listing rungs, both sides identically (a dial change
before anything has run; the pre-committed change is not spent by
it); (iii) keep the primary and print the option-copy floor as a
sensitivity. **Recommendation: (ii)** — it is ruling a's own
principle ("the dumbest baseline made executable") applied to the
baseline that actually exists for those rungs. The descriptive is
built (`battery_2d.option_copy_table`, tested); it enters no verdict
branch until ruled.

**I. Argmax tier vs exp3's committed redecode.** For the four reversal
cells the fp16 greedy continuations are compared to exp3's committed
redecode records (sha-pinned) and the diff count is PRINTED in the
record. Non-gating as built (the §6 tree is gate 1 only). Ratify:
printed descriptive, or a second INSUFFICIENT_DATA route? (exp3's own
gate 2 tolerated 2/500 fp16 byte diffs.)

**J. Pilot zero-set definitions** (used by F): non-rising "zero set"
= pilot corrected predictor score 0 (both sizes' margins zero);
rising "raw zero" = 0 verified draws at BOTH sizes. Ratify.

**K. Tree edge: an anti-predictive result** (CI entirely BELOW .5)
is INDETERMINATE under the literal §6 tree, not FAIL (2c's tree had
the same shape for ρ). Flagged; recommend leaving as is and saying so
in the doc.

**L. Pilot seed 100 overlaps a 3e-committed substream.** Under the
`exp3` namespace (§3, deliberate), `reverse_string/1b/trained/s100`
is one of 3e's committed seeds (3e drew seeds 40–167 at 1b on its
45-item subset; 410m's 28–91 does not include 100). The generator
seeds coincide on those 45 items; with k = 8 the chunk plan is one
8-row chunk against 3e's 16-row chunks, so the draws are not the same
bytes, and the pilot is never pooled with anything — no defect, but
"different substreams" (§3) is not literally true for that one cell.
**Recommend ratifying a pilot seed outside every committed range
(e.g. 1000)** — costless now; the stream map regenerates.

### Dials carried into the freeze unchanged
- Main k = 64 / seed 0 (gate 1 is free only there — ruling e); pilot
  k = 8; both tiers float32 exact upcast (exp3's policy); argmax
  float16 via 2c's HFRunner (the path that produced the outcome and
  3b/exp3's redecode); stream namespace `exp3`; per-rung token budget
  = 2c's MAX_NEW_TOKENS[answer_type]; α .01 both bars; AUC bar .75;
  N_BOOT 10,000 (seed 0), perm sample 100,000 (seed 0) — 2c's.
- Rising = clears the floor at ANY eval size (fix h); 12b-only printed.
- Percolation candidate = rising ∧ 0 verified in the 32,000 main 1b
  draws ∧ probe margin 0 (fix j).
- Restriction = rising rungs performable at 1b REMOVED (families
  recomputed), count printed.
- One pre-committed change: UNSPENT.

### Next
Session 3 (fresh session): the adversarial freeze — standing
assignments in `FREEZE_CHECKLIST.md`; ratify A–L (H and L need
Michael); cold battery; tag `exp2d-preregistered`. Then the pilot on
Michael's launch word.

---

## 2026-08-21 — RULINGS k AND l (Michael), applied in place the same session

Michael ruled on the two build findings that needed him:
**H → floor = max(majority share, 1/n_options) on both sides** (doc
§12 ruling k); **L → pilot seed 1000** (ruling l). Applied in the
build session rather than left to the freeze, so the freeze opens cold
on the ruled instrument.

What changed:
- `battery_2d.py`: `OPTION_LISTING_PIN = {antonym: 4, antonym6: 6,
  median5: 5, median7: 7, odd6: 6, odd_one_out: 4}` by literal;
  `option_copy_floor` re-derives membership from the item file
  (EVERY question must list the normalized answer among a
  uniform-length colon-introduced option list; a partial or
  non-uniform listing is REFUSED, never guessed — on the committed
  battery every one of the six lists 500/500 at one count, the other
  28 list 0/500); `rung_floor` = max(majority, 1/n) with the pin and
  the re-derivation required to agree on membership and n; the §4
  doc check compares the MAJORITY component (what §4 prints) and
  asserts the effective floor is the max. Both sides read
  `floors[r]["floor"]`, so the predictor gets the same floor
  automatically.
- `analyze_2d.py`: `TIERS["pilot"]["seed"] = 1000`; stream map
  regenerated (136 cells; the 4 seed-0 reversal entries still ==
  exp3's); a glue fixture proves 1000 ∉ {exp3 0–3, 3c 4–15, 3d 16–39,
  3e 28–167}.
- Design doc: §3 table + prose, §4 floors paragraph, §5.2 floor rule,
  §5.5 heading, §8 baselines (+ "copy one listed option"), §12
  rulings k/l, status line. Findings A–G, I–K stay ledgered for the
  freeze (not yet ruled).

**Realized outcome under the ruled floor: 11 RISING / 23 FLAT** (was
13/21): median7 (.156/.144/.170 vs 1/7 = .143; 12b p = .0499) and
odd_one_out (.162/.250/.208 vs .25) become flat; median5 rises at 12b
only (.262, p = 5e-4), odd6 at 6.9b only (.214, p = .0035); antonym
and antonym6 rise at every size. 12b-only sensitivity: 9. Families
with rising: still 7, now FIVE mixed (mid_digit 3/4, seq_extrap 1/2,
counting 1/2, order_stat 1/2, odd_one_out 1/2) and two all-rising
(antonym, base_arith). Rising set: add3_mid, add_base8, antonym,
antonym6, arith_next, count_div13, median5, odd6, sub3_mid, sub4_mid,
sub_base8.

**Envelope regenerated** (`power_envelope_2d.json`, AUC_true .85,
300 sims/cell) — the same shape, a little lower (11 vs 13 rising):

| flat rungs at pilot zero | rising raw-zero 0 | 2 | 4 | 6+ |
|---|---|---|---|---|
| 12 of 23 (τ −.05) | .71 | .29 | .00 | .00 |
| 17 of 23 (τ +.68) | .62 | .36 | .00 | .00 |
| 23 of 23 (τ +2.04) | .75 | .56 | .21 | .00 |

Finding G stands: the PASS bar is unreachable once more than ~3 of
the 11 rising rungs are silent in the pilot; with none silent the
procedure sits AT the .75 bar only when every flat rung is at zero.
The declaration after the pilot will most likely read DECLARED
UNDERPOWERED IN ADVANCE unless the 410m/1b sampler is live on nearly
every rising rung. Main runs regardless (ruling c).

Cold battery after the rulings: referent battery 14/14 (checks 5 and
6 now assert the option-listing pin and the 11/23/9 split), fixture
suite 87 (W3 rebuilt on five spread rising rungs; W1's probe-AUC
assertion computed from the committed records instead of a literal),
full-shape all four terminals + the restriction world, mutation
battery re-run on the ruled instrument with two new mutants for the
floor rule (option component dropped; pin check dropped) — result
appended below.

**Mutation battery on the ruled instrument (80 mutants): 78/80
killed; both new floor-rule mutants ("option-copy component dropped",
"option-listing pin check dropped") killed; the two survivors are the
documented equivalents — [1] the redundant rate-above-floor conjunct
and [38] the untrained-twin floor (no committed twin accuracy exceeds
its rung's floor; the six raised floors only widen that gap).**
Baseline clean; sources restored (git status shows only the intended
edits).

---

## 2026-08-21 — RATIFICATION of findings A–G, I–K (Michael: "as recommended")

All eleven applied to the design doc in place, none touching code
(I is already the printed non-gating comparison, J is the code's
definition of the two zero sets, K is the tree as built):
A §11 two answer types; B §4 base12_digitsum .038 / base13 .068;
C §5.3 seven families (five mixed); D §5.3 the null is 2c's
family-BLOCK permutation, "within families" struck (its 16-element
group could not reach p < .01); E the CP figures brought to the
program's two-sided CP95 convention (0/32,000 → 1.15e-4, one draw
→ ~1.7e-4, 0/4,000 → 9.2e-4) in §3, §5.4, §7 and fix j; F + J §7
now states the built procedure (Tobit latent model, τ rule, d from
the population AUC, held/truncated sets, the cap = 0 arithmetic, 2,000
sims at seed 20260821); G §7 carries the envelope table and its
reading (the pilot is the power statement); I §5.4 argmax bullet;
K §6 anti-predictive CI → INDETERMINATE, stated. No pre-committed
change spent — nothing has run. With k and l this closes every item
the build raised; the freeze opens cold on a doc and an instrument
that agree.

---

## 2026-08-21 — FREEZE SESSION (session 3 of 3), opened cold

Assignment: find the class defect. Worked `FREEZE_CHECKLIST.md` top
to bottom in fresh processes (pycache cleared, `PYTHONDONTWRITEBYTECODE=1`,
stack torch 2.12.1 / transformers 5.13.0 — the stack of 3c/3d/3e's
six byte-identical gate-1 reproductions). ZERO model contact: no
rehearsal cell, no preflight re-run (the 410m/1b float32 preflight
artifacts of 2026-08-16 exist and read `all_ok` on 4/4 checks each —
checked, not re-run).

### F-1 — THE CLASS DEFECT (3a's lineage): INSUFFICIENT_DATA unreachable from the runner's tree. CLOSED.

`run_sampling_rung` halts a reversal main rung on a gate-1 diff by
writing the gate-1 record (n_diffs > 0), parking the rows in
`<rung>.draws.jsonl.HALTED.jsonl.gz` and NOT writing the normal
draws file (so skip-if-exists never treats a halted rung as done);
the tier process exits non-zero and the driver stops. The tree a
halted campaign leaves is therefore an INCOMPLETE main tier by
construction — and `run()` loaded `load_sampling_tier(root, "main")`
before `load_gate1`, so on that tree the frozen verdict RAISED
`FileNotFoundError: main tier incomplete: 39 of 68 cells missing`
instead of delivering §6's first terminal. Demonstrated executably
on a tree built with the runner's own halt function
(`rederive_2d.record_and_halt_on_diff`): halt at main/410m
rev_string7 (RUNG_ORDER index 29), pilot complete, power present,
main/410m rungs 0–28 present → the runner refused every later tier
as designed, and `run()` crashed. The synthetic W4 world had reached
INSUFFICIENT_DATA only because it writes a COMPLETE tree with a
drifted stream — a tree the runner can never produce. The frozen
verdict's own terminal was unreachable from the production path:
3a's class ("closed INSUFFICIENT_DATA when its frozen verdict
crashed"), one level up.

Closure, additive, §6's precedence made executable BEFORE any tier
loads: `scan_gate1_halt(root)` validates every gate-1 record that
EXISTS with the same pins as `load_gate1` (factored into
`_check_gate1_record`), collects the cells with diffs, and — not
trusting the runner — re-derives each halted cell's diff count from
the `.HALTED` rows through 3d's `diff_seed` against exp3's committed
bytes (a disagreement is a hard error; an absent `.HALTED` file lets
the record's diffs stand, flagged `halted_rows_reverified: false` —
the terminal is the conservative one either way). `run()` returns
`insufficient_data_record(...)` on any halted cell: the tree's
verdict via `verdict_tree`, the diffs verbatim, every tier's
completeness, the known outcome, the twin referent, the declaration
if present, `primary: None`, `halted_before_completion: true`. A
clean scan decides nothing; the complete-tree path (`load_gate1` +
`check_gate1_vs_main`) runs unchanged. New: `build_halt_world` in
`tests/full_shape.py` (the runner's halt tree, built with the
runner's halt function), world W5 → INSUFFICIENT_DATA, three
fixtures (delivers the terminal with tiers 29/34, 0/34 for main;
`.HALTED` rows re-verified and a doctored file refused; clean/empty
scans silent, a bad pin on a halt record refused), and two mutants
(scan dropped; re-verification dropped) — both killed.

### F-2 — attestation gaps (3c B / 3e F-3 class), three additive pins. CLOSED.

(a) `power_2d.json` attests the pilot predictor it declared from
(`pilot_predictor`) and nothing compared it to the pilot tier on
disk: a regenerated or edited pilot behind a standing declaration
would carry a stale status into the verdict record and into how a
FAIL is READ. `check_power_vs_pilot` compares every rung's `score`
and `raw_zero` to the analyzer's own recompute from bytes;
`load_power_record` requires the key. (b) gate-1 records'
`model_sha` was stored, never compared: now == 2b's `PYTHIA_SHAS`
(the main tier already pinned it). (c) argmax records' `model_sha`
and `answer_type` likewise. Fixtures for each; mutants for each —
killed. The synthetic world builder now writes `pilot_predictor`
through the analyzer's own loaders, as the real procedure does.

### F-3 — the criterion is NOT exact-match on two rungs (inherited from 2c, undisclosed until now). PINNED, DISCLOSED; doc text for ratification.

The floor-DoF attack enumerated every rung's normalized answer
multiset: `base12_digitsum` and `base13` have 500 DISTINCT raw
answers (raw majority .002) yet normalized majorities .038 / .068.
Cause: 2c's `number` normalization `re.search(r"-?\d[\d,]*", s)`
keeps the FIRST DIGIT RUN, and both rungs write their answers as
full base-12/13 strings with letter digits (`surface_answer =
_to_base12 / _to_base13`, registered `answer_type="number"` in 2c's
SPECS): 'B83' → '83', '2A9' → '2', '47A8' → '47'; 196 of 500
base12_digitsum answers and 276 of 500 base13 answers are not
reproduced whole (base13's two all-letter answers 'AAA'/'BAB' pass
whole — no digit run, the raw string is returned). The build's
finding B saw the numbers ("answer '2' in both") and not the cause.
2c's own ledger knew a "normalization wrinkle" on these rungs only
as an ORACLE letter-digit mapping; the verify-side truncation was
not recorded anywhere. Consequences, stated plainly: on those two
rungs the criterion is a first-digit-run match on BOTH sides
identically (2c's m4 records carry counts only — the outcome cannot
be rescored, and the rule is 2c's verbatim, frozen); the majority
floor is computed under the criterion as applied, so "always emit
'2'" scores exactly it; both rungs are flat at ≤ .006 under the
lenient criterion and so a fortiori under exact match — no label
moves; on the predictor side a spurious positive is possible only in
the direction that LOWERS the AUC (a flat rung leaving the zero
tie). Every other rung — all 32 — is exact. Closed executably:
`CRITERION_TRUNCATED_PIN = {base12_digitsum: 196, base13: 276}`,
re-derived at every `rung_floor` (a changed count is a hard error),
carried per rung in the verdict's `answer_space_descriptive`
(`criterion_exact`, `n_answers_truncated`), referent check 15 (with
the option-listing 500/500 vs 0/500 census), fixture, mutant
(killed). DOC: §4 floors paragraph and §9 "exact-match
verification" need the disclosure — text proposed below, for
ratification.

### F-4 — the power model discards the pilot's POSITIVE information on one side only. SENSITIVITY PRINTED; the declaring rule needs Michael.

The ratified Tobit (F/J) holds flat pilot-zeros at zero, draws
non-held flat rungs from the POSITIVE part (they are held positive),
truncates rising raw-zeros — and re-randomizes every other RISING
rung from N(d, 1), re-silencing it with probability Φ(τ − d) (≈ .30
at AUC_true .85 with every flat rung at zero: d = 2.56 against τ =
2.04). A rising rung the pilot already shows clearing its floor at
4,000 draws clears main's at 32,000 with probability ≈ 1 (main's bar
is tighter in rate: +.0057 vs +.016 at c = .25). So the model honours
realized structure on the flat side and discards it on the rising
side; the asymmetry, not the Tobit, is the finding. Model-free check
of finding G through the verdict's own code (all flat at zero, k
lowest-ascent rising rungs silent, the rest at distinct positives):
PASS through k = 5 (AUC .773, block p .0051), INDETERMINATE at k = 6
(AUC .727, p .026), FAIL at k = 7 (CI touches .5); over ALL silent
subsets: k = 3 → 139/165 PASS, k = 4 → 196/330, k = 5 → 153/462,
k = 6 → 0/462. The envelope's ".21 at 4 silent, 0 at 6" is the
statistic's own ceiling at 6 plus the model's ~30 % re-silencing on
top of the forced set. Also: a rising rung with 1–14 pilot fires at
floor .006 (up to 79 at the option-listing floors) has a CP95 upper
bound still BELOW its floor — the same information as a raw zero —
yet the ratified rule treats it as alive (power overstated there).

Implemented as a NON-DECLARING sensitivity on the same seed (3e F-2
precedent — the rule moves only on Michael's word): the SYMMETRIC
rule — rising rungs with a positive pilot score held positive
(L | L > τ from N(d, 1)); rising rungs at pilot score 0 truncated at
the cap from their OWN per-size pilot counts' CP95 upper bounds
(`score_cap_from_counts`, == the raw-zero cap when both counts are
0); flat rungs unchanged. `run_procedure` prints it as
`sensitivity_symmetric_rule` with `would_declare` and
`agrees_with_declaration`; `declaration_rule = "ratified"`. The
ratified draw sequence is untouched call for call (fixture: identical
arrays; envelope: ratified fields byte-identical to the committed
file). Envelope under both rules (AUC_true .85, 300 sims):

| flat at pilot zero | silent rising 0 | 2 | 4 | 6 |
|---|---|---|---|---|
| 12/23 | .71 → **.93** | .29 → **.45** | .00 → .00 | .00 |
| 17/23 | .62 → **.99** | .36 → **.80** | .00 → .00 | .00 |
| 23/23 | .75 → **1.00** | .56 → **1.00** | .21 → **1.00** | .00 |

(ratified → symmetric). Under the symmetric rule the declaration is
decided by the silent-rising count against the statistic's own
ceiling (dies between 4 and 6), not by the model's re-silencing.
RULING NEEDED: which rule declares. Recommendation: the symmetric
rule (it is the "realized tie structure of BOTH sides" §5.5 already
commits to, completed on the rising side; the ratified rule's
asymmetry has no stated rationale). Either way the procedure runs
ONCE after the pilot and main runs regardless (ruling c).

### F-5 — gate 1 reaches its first production contact late. RECOMMENDATION, ruling needed.

`run_tier` iterates `RUNG_ORDER_2D`; the reversal rungs sit at
indices 29–30, so the first byte comparison against exp3's streams
happens after the whole pilot (~1.7 h) and 29 rungs of main/410m
(~5 h). Every predecessor's gate 1 ran FIRST (rehearsal). Iterating
the two reversal rungs first within each main tier would surface a
generation-law drift ~5 h earlier per size at no statistical cost
(the runner's loop order is not load-bearing anywhere; skip-if-
exists; the analysis order stays `RUNG_ORDER_2D`). Not applied — §10
is the run plan as ruled; one line in `run_tier` if ruled.

### F-6 — the bars' resolution differs 8× between the sides. DISCLOSURE, doc text for ratification.

"Applied identically" holds at the level of the formula, not the
unit: the outcome's bar (n = 500) clears at +.008–.048 above c, the
predictor's (n = 32,000) at +.0006–.0057. The 32,000 draws are 64
per item; a DETERMINISTIC-per-item chance baseline (the option
copier that always copies the same position; greedy argmax IS this
on the outcome side, where n = 500 already prices it) clears the
predictor's bar 26–42 % of the time per rung (exact binomial over
items, every rung tabulated in the freeze record). The verdict's α
is untouched — the scores are label-blind and the block test and
bootstrap condition on them — so this is interpretive: a predictor
"above floor" is a weaker statement than an outcome "above floor",
and a spurious predictor positive on a flat rung can only LOWER the
AUC. Recommend a sentence in §5.1; a sensitivity AUC under an
item-resolution bar (k' = round(rate × 500) against n = 500) is one
line if Michael wants it printed — not added unasked.

### F-7 — AUC null conditioning: CLEARED, with one observation.

Sampled matrix == 2c's `sampled_block_perms(fams, 100000, rng(0))`
byte for byte; every row a permutation with within-block order
preserved; size-1 families permute among their four slots but all
four are flat, so they are identities on y; midrank matvec == loop
AUC over 5,000 rows; n₁ preserved in every row. The group acting on
the realized y has exactly 3,780 distinct label vectors (3!/2! ×
9!/(2!·4!·3!) × 1 = 3 × 1,260) and the 100,000 draws reach all
3,780, so the sampled p is a Monte-Carlo estimate of an enumerable
one (p_min 1/3,780 = 2.65e-4; the add-one sampled value at perfect
separation is 26/100,001 = 2.6e-4); MC standard error at p = .01 is
~3e-4. 2c's routing kept deliberately (§5.3: "exactly as 2c's
verdict was"); noted so a p within ±3e-4 of α is read as such.
Bootstrap drop rule: the drop count depends on the label and the
counts matrix only (identical for two unrelated x; 2/10,000 on the
realized label; 0–5 over 300 block-permuted labels) — it carries no
information about the predictor.

### F-8 — totality of the verify path over both alphabets: CLEARED.

480,240 fuzzed draw-side inputs (em/ideographic/zero-width/NBSP/BOM
whitespace, quote- and bracket-wrapped, control chars, NUL, combining
marks, non-ASCII digits, surrogates, 8- and 12-token garbage, comma/
sign digits) × both answer types + 22,620 exhaustive 1–4-character
products: `IndexError` the only exception, reachable on the `word`
path only (29 hits; the `number` path raises nothing); 3c's wrapper
returned a bool every time. All 17,000 committed answers normalize
non-empty and self-verify under their own type (and raise nothing
under the other). The 512,000 committed reversal draws raise nothing
raw.

### Other attacks, cleared (candidates 1–8 of the standing list)

(1) `answer_type` reaches the criterion only from the sha-pinned
item file / registry (`ANSWER_TYPE_PIN` re-asserted); the records'
field is compared, never read. (2) every floor consumer reads
`floors[rung]["floor"]` from `bt.floor_table` on the pinned battery
(run(), compute_power_2d.main, full_shape). (3) x/y and
`FAMILY_SIZES` both from `RUNG_ORDER_2D`; the bootstrap's
`sorted(fams)` is 2c's. (4) the loader keeps main reversal rows for
BOTH sizes; `check_gate1_vs_main` iterates them and cannot skip (a
missing row set is a TypeError, not a pass). (5) `redecode_diffs` is
read by no branch. (6) `_restricted_layout` drops emptied families,
keeps contiguity, regenerates the group for the reduced vector.
(7) `pilot_zero_set` reads `score`/`raw_zero` from
`predictor_from_tier` at 4,000 draws pinned. (8) gate-1 fires are
checked against the pin when clean; the main rows are byte-compared
independently, which entails the fires. Gate-1 production path
re-read cold against exp3's `run_sampling_cell`: same `render_prompt`
with `shots[:2]`, same `sample_item` signature (seeds=(0,) vs
(0,1,2,3): a fresh `torch.Generator` per seed from `stream_seed`,
chunk plan (16,16,16,16), cache cropped to the prompt between chunks,
nothing carried across seeds), `max_new_tokens` 12 == exp3's
`SAMPLING_MAX_NEW_TOKENS` for both reversal rungs, same
`terminal_ids`, same `_load_model(size, "trained", "float32")`; the
pilot's seed 1000 / chunk plan (8,) cannot touch seed-0 substreams.
Floor DoF beyond F-3: ties in the majority count on 12 rungs are
harmless (the share is the floor; `majority_answer` is descriptive);
no answer normalizes to empty; the six option-listing rungs list
500/500 at one count each with the answer never duplicated among
options (mean copy-random-option rate == 1/n exactly); clock24's
500/500 colon questions ("Answer as H:00") list nothing — the
re-derivation is robust to them; the other 27 list 0/500.

### Doc slips found at the freeze (ledgered, NOT applied — ratification)

(a) §10 step 2 still says "k = 8, seed 100" — ruling l made it 1000
(§3 is right). (b) §4 floors paragraph: add the F-3 disclosure after
"answer '2' in both": *because 2c's `number` normalization keeps
the first digit run of an alphanumeric base-12/13 answer ('B83' →
'83', '2A9' → '2'); on these two rungs the criterion is a
first-digit-run match on both sides, 196 / 276 of 500 answers are
not matched whole, and every other rung is exact-match*. (c) §9
second bullet "exact-match verification" → "exact-match verification
(first-digit-run match on base12_digitsum and base13, §4)". (d) §7:
the symmetric-rule sensitivity and the model-free restatement of G
(the statistic's ceiling is 6 silent rising rungs with every flat
rung at zero; PASS for 59 % of 4-subsets), plus the ruling on which
rule declares. (e) §5.1: the F-6 resolution sentence. (f) §10 run
order if F-5 is ruled. Code-comment slips FIXED in place (not doc
text): `analyze_2d.dump_stream_map_2d` docstring "{0, 100}" → "{0,
1000}"; `run_cell_2d` header "seed 100" → "1000"; `compute_power_2d`
comments "7.49e-4" (one-sided) → "9.22e-4" — the code had always
computed the two-sided value the doc prints.

### Cold battery on the closed instrument (fresh processes)

- Fixture suite: **100 passed** (87 + 13 freeze fixtures), 94 s.
- Referent battery: **15/15** (check 15 added).
- Full-shape worlds: PASS / FAIL / INDETERMINATE / INSUFFICIENT_DATA
  (W4 drifted-complete) + **W5 runner-halt tree** + the restriction
  world — all terminals, in the suite.
- `make_referents_2d.py` byte-idempotent (sha 95eded96… unchanged);
  `dump_stream_map_2d` byte-idempotent (136 cells, 4 == exp3's).
- `compute_power_2d.py --envelope`: the ratified fields reproduce the
  committed `power_envelope_2d.json` byte for byte (21 rows, 300
  sims); the file is regenerated with the F-4 columns beside them.
- Driver dry-run: 6 tiers, pilot → main → argmax, 410m then 1b.
- Empty tree: pilot/main/gate1/argmax/power loaders and run() all
  refuse (FileNotFoundError), `scan_gate1_halt` silent.
- Preflight artifacts 410m/1b float32 (2026-08-16): present, `all_ok`
  4/4 each; not re-run (model contact).
- Mutation battery (87 mutants: 80 + 7 freeze), detached, sources
  mutated in place and restored, baseline clean: **85/87 killed**; the
  two survivors are the documented equivalents [1] (the redundant
  rate-above-floor conjunct) and [38] (the untrained-twin floor — no
  committed twin accuracy exceeds its rung's floor). Two passes: the
  first found 8 entries whose targets the F-1/F-2 refactors had moved
  (the seven `load_gate1` pins now live in `_check_gate1_record` at a
  different indentation; the argmax provenance line gained two
  conjuncts) and ONE genuine survivor — [73] "power record not
  compared to the pilot tier": the F-2 fixture called
  `check_power_vs_pilot` directly, so deleting the call inside run()
  went unnoticed. Closed with a fixture that drives the mismatch
  through run() on a full synthetic tree; the 8 retargeted + [73]
  re-run with a fresh baseline: 9/9 killed. Suite after the addition:
  101.
- Fixture suite final cold count: **101 passed**.
