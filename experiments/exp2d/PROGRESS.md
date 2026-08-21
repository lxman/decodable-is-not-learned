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
8. **Cold battery at build:** fixture suite 71 (8 files), referent
   battery 14/14, full-shape 4 terminals + 1 restriction world,
   mutation battery: see the entry below (run detached, both
   directions, baseline clean).

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
