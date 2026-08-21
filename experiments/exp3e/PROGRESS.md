# Exp 3e — Progress Ledger

Chronological, newest entry last inside each dated block. The design
doc (`experiment-3e-design.md`) stays frozen as approved in session 1;
everything the build discovered that touches doc TEXT is ledgered here
for freeze ratification, never silently absorbed (3c's convention).

---

## 2026-08-21 — BUILD SESSION (session 2 of 3 of design | build | freeze)

Instrument built at `experiments/exp3e/`: `partition_3e.py` (N(x),
reachability with the named edit, M(x), the two printed variants, the
subset, the palindrome refusal, dump/check) → `partition_3e.json`;
`stats_3e.py` (exact hypergeometric primary, m_min / THIN_MAX, the
count-weighted subset-count DP, the designation-exchangeability
convolution, m_s,min with its best-case proof, the annotation tree);
`analyze_3e.py` (all §4 pins, the four-tree loaders, the verdict
tree, run()); `scorer_3e.py` (the target-swapped scorer = 3c's total
wrapper with the target as a parameter; the leak-void rule on every
target); `scorer_gates_3e.py` → `results/scorer_gates.json`;
`rederive_3e.py` (gate 1 on the production subset path; 3d's
comparator imported); `compute_power_3e.py` → `power_3e.json`;
`stream_map_3e.json`; `run/run_cell_3e.py` + `run/campaign_3e.py` +
`run/commit_watcher_3e.sh`; `verify_referents_3e.py` (15-check
battery); fixture suite + full-shape worlds + mutation battery under
`tests/`. **Invariant held: zero model contact this session — no
weights, no forwards, no tokenizer files, no new sampled quantity for
any real cell.** Every committed-byte step (partition, power, scorer
gates, referent battery) reads closed trees only.

### Build results (doc Open items 1–8)

1. **Partition (Open item 1) — every doc number reproduces from the
   item file.** 45 items = the len-4 repeat class; 32 reachable (17 by
   a single transposition — mirror (0,3): 6, (1,2): 11 — and 15 by a
   rotation — (0,2): 10, (1,3): 5) / 13 non-reachable ((0,1): 8,
   (2,3): 5; the 13 verbatim = the doc's list). |N(x)| = 7 for all 45;
   no palindromes; every repeat-class answer C1 = 6.0. M(x): |M| = 1
   on the 10 (0,2) items, 2 on the 6 (0,3), 3 on the 5 (1,3), 0 on
   the 11 (1,2) → arm 21 / sit-out 11. Variants printed beside the
   frozen classification: (i) adjacent-only → 21 reachable, (ii)
   rotations-only → 15. Committed as `partition_3e.json` (file sha
   pinned in `analyze_3e.PARTITION_FILE_SHA256`; the loader ALSO
   recomputes the whole record from the answers and refuses
   disagreement). Subset literal `SUBSET_ITEMS_PIN` with sha
   `292aa5e7…89ef`; three sources, one value (literal, partition
   record, recompute).
2. **m_min = 8** (n = 7, X = 0 gives .0742; n = 8 gives .0488);
   anti-direction m_min = 3, disclosed; THIN_MAX = 10 (at n = 11,
   X = 1 already gives .0953 > .05, so n ≤ 10 rejects only with
   X = 0, exactly as the doc's THIN rationale says). The §5.3 table
   reproduces to four decimals (.0488 / .1345 / .0980 / .0015 …).
   Exact by integer combinatorics (Fractions), no Monte Carlo.
   **m_s,min = 3**: best case = one event on the reverse of each of
   the three |M| = 3 items, (1/4)³ = 1/64; two events at best give
   1/16 = .0625. The best-case rule (all-on-reverse, smallest-θ items
   first) is proved in `stats_3e.best_case_specificity_table`'s
   docstring and checked against exhaustive enumeration over every
   allocation of E ≤ 4 events on a small instance.
3. **DPs (Open item 3):** the count-weighted null is an integer
   subset-count DP over items (exact: ways / C(45, 13)); the
   designation-exchangeability null is an integer convolution over
   items (exact: tuples / Π(1 + |M_i|)). Both proved against
   brute-force enumeration in the fixtures (`_brute_count_weighted`
   over all C(8, 3) subsets; `_brute_designation` over the full
   product). The full-shape W2 world's p is cross-checked by
   enumerating the disclosed count vectors through the verdict path.
4. **Power (Open item 4) — exact for the primary, scenario for the
   arm; the sixth lesson applied by construction.** Under per-class
   fire probabilities the fired composition is Binomial(32, q_r) ×
   Binomial(13, q_n) and every pair is classified through the
   verdict's own tails and tree — no simulation. Gamma shape fitted
   to the committed reachable per-item counts at 1b (5, 3, 1 × 6,
   0 × 24 over 2,560 draws) by the program's frozen moment rule (3d's
   λ rule by precedent, population variance): **shape = .3082**.
   Results, 1b at 8,192 draws per item:
   - H_shortcut: **P(SHORTCUT) = .7636 (gamma) / .9991 (homogeneous)**
     — above the .75 bar under the pessimistic variant, by .014.
     E[n] = 13.9 (gamma) vs 24.9 (homogeneous): the doc's §7
     back-of-envelope (n ≈ 24) was the homogeneous figure; the
     dispersion the committed record itself shows nearly halves the
     expected fired-item count.
   - H_half: **.3069 (gamma) / .8878 (homogeneous)** — a partial
     shortcut is NOT reliably detectable at this budget under the
     committed dispersion. **Printed as a concession in advance**
     (`concessions_printed_in_advance` in `power_3e.json`); whether
     H_half counts as a "named alternative" under §7's
     declared-underpowered clause is a ratification item (below).
   - H0 calibration, unconditional: P(SHORTCUT) .0265 / P(ANTI)
     .0259, union .0524 (gamma); .0257 / .0266 / .0523 (homogeneous).
     Conditional table at n ∈ {8, 10, 12, 15, 20, 24, 28, 32}: each
     side ≤ .0488, union ≤ .0881 — never "exactly α" (3d §7's
     corrected sentence, applied in advance).
   - **Minimum detectable non-reachable/reachable rate ratio at .75
     power: 0.04 (gamma) / 0.29 (homogeneous).** Under the committed
     dispersion the design has power only against a near-total
     shortcut.
   - 410m (non-gating): P(n ≤ 10) = .92 (H_shortcut) / .87 (H0) under
     gamma — the replication will almost surely carry THIN,
     disclosed in advance; P(SHORTCUT | H_shortcut, gamma) = .25.
   - Specificity scenarios (1b draws, competitor rates UNKNOWN):
     null rejects at .037 (gamma) / .041 (homogeneous) ≤ .05; power
     .73 / .93 / .98 (gamma) at reverse-share .6 / .75 / .9; expected
     matched events 33–81; P(SPARSE) ≈ 0. MC at seed 20260821,
     20,000 sims per scenario, each arm judged by the exact DP.
   The power record reproduces byte-for-byte from the frozen code
   (fixture `test_power_record_pin_entries_and_committed_file`).
5. **§4 pin list complete (Open item 5):** `FROZEN_IMPORT_SHA256_3E`
   = 3d's nine pins by value (exp3 sampler/analyzer/stream map/
   verdict, 3c analyzer/stream map/verdict, 2c harness) + 3d's
   analyzer, gate-1 comparator, stream map and verdict record + exp3's
   `run/run_cell.py` (the capability/model loader the subset path
   drives) + 2b's `models.py` (the weights' shas) — 14 files.
   `COMMITTED_DRAWS_SHA256` = the 13 reverse_string draws files across
   exp3/3c/3d at both sizes + exp3's 2 ctrl_copy files, compared
   before any byte is parsed; the 3c pair also asserted equal to 3d's
   own `COMMITTED_3C_DRAWS_SHA256` (two sources, one value). The
   26-address committed fire record as a literal with sources
   (19 at 1b, 7 at 410m); the 19 repeat-class addresses DERIVED from
   it by the subset filter and asserted (1b 14 on 8 items, 410m 5 on
   4); ctrl_copy's 12787/16000 and 13460/16000 by value from 3d;
   the twin pins 512,000 + 64,000.
6. **Sampler provenance + stream map (Open item 6):** `sampler.py`'s
   sha is the same literal 3c and 3d pinned; `stream_map_3e.json`
   carries the endpoint entries (item 0 / item 499) for every pooled
   seed at both cells — asserted equal to exp3's, 3c's AND 3d's
   committed maps on every overlapping seed — PLUS the 45 subset
   items' substream seeds at every seed 0–167 (1b) / 0–91 (410m),
   derived by the same imported `stream_seed` and asserted equal to
   the formula at every check. See doc slip (a).
7. **Gate-1 referents (Open item 7):** coverage literal 2,880 per
   size (`GATE1_COVERAGE`); expected fires DERIVED from the 26-address
   pin at the gate-1 seeds on subset items and asserted: 1b seed 20 →
   (348, 14), (430, 43); 410m seed 24 → (123, 62). Referent check 14
   finds all three in the committed 3d shards at those addresses and
   the shards carrying every subset item. The loader refuses a CLEAN
   comparison whose `fires_reproduced` differs from the literal.
8. **Fixture suite + battery (Open item 8):** 118 fixtures; 9
   full-shape worlds reach every terminal (SHORTCUT non-thin /
   thin, NO-SHORTCUT non-thin / thin at n = m_min, ANTI-SHORTCUT,
   UNINFORMATIVE, gate-1 drift, all-void, void-discloses-and-proceeds
   with a void COMPETITOR disclosed) and every specificity annotation
   (DIRECTED / MISFIRE-RATE / SPARSE), end to end through the frozen
   loaders of all four trees; mutation battery (60 mutants, both
   directions; result recorded below); referent battery 15 checks on
   the real trees (below); the determinism fixture is exp3's, byte-
   pinned sampler, run at the freeze per house standard.

### Build-session batteries (fresh processes, PYTHONDONTWRITEBYTECODE)

- **Referent battery `verify_referents_3e.py`: 15/15** on the real
  trees (frozen pins; item-file + strata pins and the 45 + 149 split;
  3b-derived sha_refs; subset literal = recompute = partition record;
  the printed classification vs the doc; power pins; stream map +
  continuity with exp3/3c/3d; all 15 draws-file shas incl. agreement
  with 3d's own 3c pins; the 26 committed fires re-scored and the 19
  subset addresses; ctrl_copy 12787/13460 = exp3's verdict entries;
  the scorer-gate record; the twin record 0/512k+64k through exp3's
  loader; crasher-class totality; the three gate-1 fires present in
  the committed 3d shards at coverage 2,880; 3d's sha-pinned verdict
  addresses = the 3d-source pin entries).
- **Mutation battery: 60/60 killed, both directions, baseline clean.**
  The FIRST run left 4 survivors, each a fixture gap rather than a
  dead provision, closed by kill fixtures before the cold re-run:
  the SPARSE bar at events == m_s,min (inclusive — MISFIRE-RATE);
  `transpositions()` admitting the equal-character identity swap
  (behaviourally masked by `discard(x)`, now asserted directly); the
  frozen-import hash assert (no fixture had tampered a pin — now
  one does, against the real pins); and the out-of-subset row
  refusal (the coverage check masked it — the fixture now requires
  the refusal to NAME the cause).
- Fixture suite: 118.

### Scorer known-answer gates — RUN AT BUILD ON COMMITTED BYTES, PASS

`results/scorer_gates.json` committed. **Gate (a):** target = answer
over the committed exp3/3c/3d draws of the 45 items (1b 2,560/item,
410m 1,792/item) reproduces the 19 repeat-class fire addresses
EXACTLY — 1b 14 (123 s5/8/13/19/36; 447 s13 ×2, s17; 320 s15; 153
s29; 179 s30; 283 s25; 348 s20; 430 s20), 410m 5 (123 s8, s24; 174
s15; 226 s6; 283 s27). The same pass re-scores all 500 items and
reproduces the full 26-address record. **Gate (b):** target = the
copy answer over ctrl_copy's committed T = 1.0 draws reproduces
12787/16000 (410m) and 13460/16000 (1b) EXACTLY. No model was
touched; the runner refuses every tier until this record reads PASS.

### Build slips caught by the instrument's own pins (none survived
### to a committed artifact; recorded because each is the class the
### pins exist for)

- **The hand-typed 45-item subset literal was wrong** (a list typed
  from memory); the sha fixture against the recompute caught it on
  first run; replaced by the derived list. Three sources, one value —
  executable.
- **The partition classified the repeat pattern on the ANSWER**; the
  dump's `pattern_counts` came out (0,1): 5 / (2,3): 8 — the mirror
  image of the doc's (0,1): 8 / (2,3): 5 — and the |M|-by-pattern
  table flipped with it. The doc states patterns on the INPUT; fixed,
  fixture added, partition re-dumped and re-pinned. No class label,
  N(x) or M(x) was affected (those are functions of x throughout).
- **One hand-wrapped sha literal carried a transcription error**
  (the 3c/410m draws file); the sha check refused the first scorer-
  gate run. The whole `COMMITTED_DRAWS_SHA256` block was then
  regenerated programmatically from disk and every pin re-verified.

### Doc slips / readings found at build — LEDGERED FOR FREEZE
### RATIFICATION (no accepted dial touched; the doc stays as approved
### until Michael rules)

a. **Open item 6 "the subset path's stream seeds asserted equal to
   3d's committed `stream_map_3d.json` entries for the 45 items"** —
   3d's map carries item-0 / item-499 endpoints only, so that
   assertion cannot be literal. The build asserts (i) the sampler
   file's sha (formula identity), (ii) endpoint continuity with all
   three predecessor maps, and (iii) the 45 substreams at every seed
   as pinned entries of `stream_map_3e.json` derived by the same
   imported function.
b. **§5.5/§6 annotation attachment:** the specificity annotation is
   attached mechanically to EVERY primary world (SHORTCUT, NO-
   SHORTCUT, ANTI-SHORTCUT, UNINFORMATIVE) in the verdict string, not
   only to the two the doc names; same draws, same arm, more
   disclosure rather than less.
c. **§7's back-of-envelope (n ≈ 24 under H_shortcut) is the
   homogeneous figure;** the committed dispersion gives E[n] = 13.9.
   §7 itself says the build's tables replace it; noted so the
   number is not quoted.
d. **§7 declared-underpowered clause and H_half:** power at the
   named alternative H_shortcut is .7636 (gamma) — above the bar —
   but .3069 at H_half. The record prints the H_half concession
   either way; whether §7's "its named alternative" includes H_half
   (and so whether the experiment is DECLARED UNDERPOWERED in the
   1c sense) is Michael's ruling.
e. **§10.2 ordering, additive:** the runner requires the scorer-gate
   record before gate 1 as well as before sampling (the doc's
   wording is "before any sampling tier"); gate 1 is model contact
   and there is no reason to allow it past a failed scorer.
f. **Leak-void on competitors, the build's reading of §4:** a
   matched competitor string occurring in its item's prompt voids
   THAT (item, target) — its emissions are disclosed verbatim and its
   count-vector entry is 0; the item stays in the arm. (A void
   REVERSE voids the fire exactly as 3c.)

### Build dials frozen here that the doc delegated to the build
### (assembled for the freeze's ratification list)

Gamma shape rule (population-variance moment estimator, 3d's
precedent) and value .3082; power seed 20260821 / 20,000 sims per
specificity scenario; the m_s,min best-case rule (all-on-reverse,
smallest θ first) with its proof; seed blocks of 16 (46,080 draws)
as the durable/commit unit; the gate-1 record's `fires_reproduced`
checked against the literal only on a zero-diff comparison (a
drifted comparison is INSUFFICIENT_DATA regardless); sampling
records carry the 45-item `items` list and `subset_sha256`, and the
shard reader refuses any row outside the subset; exp3's
`run/run_cell.py` and 2b's `models.py` added to the frozen pins.

### Next session (session 3 of 3): the adversarial freeze

Standing assignments: find the class defect; fuzz the target-swapped
scorer for totality over the emission alphabet (stop-#1 rule); the
partition's degrees of freedom — the variants are printed so the
freeze can check no variant was quietly preferred; the overlap clause
in M(x); the designation null's conditioning; the gate-1 single-seed
call vs the tranche's 16-seed call (same `sample_item`, different
seed tuple — byte identity across that difference rests on 3c/3d
gate-1 precedent and on the per-seed generator reseeding, to be
re-read cold). Cold battery per `FREEZE_CHECKLIST.md`. Tag
`exp3e-preregistered` on Michael's ratification of slips (a–f) and
the build-dial list; campaign launch is a SEPARATE go with the
per-block push cadence reconfirmed.

---

## 2026-08-21 — FREEZE SESSION (session 3 of 3 of design | build | freeze)

Opened cold in a fresh context. Assignment per `FREEZE_CHECKLIST.md`:
find the class defect; totality fuzz; the partition's degrees of
freedom; the nulls' conditioning; gate 1's path; the power model's
shape. **Invariant held: no model contact for any real cell** — the
only weights loaded this session were exp3's determinism fixture
(synthetic prompts, its own stream namespace, house standard since
exp3). The gate-1 rehearsal (the single sanctioned contact) awaits
Michael's word and was NOT run.

### The named candidates, cleared with reasons

1. **Partition inputs pinned?** The partition never reads the question:
   x = answer[::-1]. Checked strictly against the pinned item file —
   every one of the 500 questions is exactly
   `Spell the string '<x>' backwards.` with x == answer[::-1]. Answers
   reach the partition only through 3d's sha+strata-pinned loader, and
   `verdict_3e` asserts each partition answer equals the battery's.
2. **Caller-supplied answers/labels/answer_type?** run() passes the
   pinned item file's; the shard's `answer_type` is compared to the
   pin BEFORE `tally_with_addresses` runs; 3c's tally indexes
   `answers[row["item"]]`, so 45 subset rows score against their own
   answers, never positionally.
3. **`fires_reproduced` runner-scored on regenerated draws?** On a
   zero-diff comparison regenerated == committed byte for byte, so the
   runner's scoring IS the committed scoring; independently, run()
   re-scores every committed 3d shard and asserts the 26-address pin,
   which contains (348, 20, 14), (430, 20, 43) and (123, 24, 62).
   Coverage: `draws_compared` is written from the literal, but 3d's
   `diff_seed` hard-errors on a short stream on EITHER side and on
   extra items, and `subset_committed_rows` refuses a shard missing
   any subset item — the literal is true whenever a record exists.
4. **Source attribution by seed range?** Each committed file is read
   with its own expected seed set by the predecessors' row readers
   against its own sha pin, and `_merge_rows` refuses a duplicated
   seed — a 3d shard cannot carry 3c's seeds into the base.
5. **Subset index vs battery index in the arm / S2 prompts?**
   `c.load_prompts` returns a battery-indexed list; every arm and S2
   call passes the ORIGINAL item index; `rows_by_item` is keyed by it
   and `read_subset_rows` refuses any row outside the subset.

### Totality fuzz — cleared

90,000 draw-side inputs through the target-swapped scorer: 60,000
adversarial (punctuation-wrapped non-space whitespace, Unicode line/
paragraph separators, control chars incl. NUL, combining marks, zero-
width joiners, empty, 12-token garbage, case/width variants) + 30,000
real emitted strings from exp3's 1b and 3d's 410m committed shards.
`harness.normalize_answer` raised exactly one exception type,
`IndexError` (59 times); the wrapper raised 0 times; exp3's
`score_first_char` raised 0 times. The reading proof: the function's
only subscripts are `split("\n")[0]` (never empty) and `s.split()[0]`
behind `if s`, and the guard fails precisely for strings that survive
`.strip(".!?\"' ")` non-empty but are whitespace under `.split()`
(`'\t'`, `'\x0b'`, `' '`) — 3c stop #1's class, caught.

### The partition's degrees of freedom — cleared

Void census on the REAL battery through the frozen prompt loader:
zero void targets among the 45 answers, their M(x), all seven
neighbours of every input, the 149 S2 targets and all 500 answers; no
two targets of any item normalize equal; the `variants` block is read
by exactly one downstream line (a printed count); M(x) uses ≥ (the
doc's "at least as copy-like" — with > every mirror item would lose
its arm); first-character matching and the sit-out rule are the doc's.

### The nulls' conditioning — F-1 FOUND (below); the rest cleared

A void item can never fire, so void handling could shift the
hypergeometric's n only if a non-reachable answer were void; the census
is zero. The count-weighted DP conditions on non-void counts. The
designation null was where the leak was.

### Gate 1's path — cleared by re-reading + precedent

`sample_item` builds a fresh `torch.Generator` per seed from
`stream_seed`; `probs1` comes from the prompt forward; the plan is
16 × 4 rows so one cache regime serves the item; `past.crop(prompt_len)`
after every chunk. The only cross-seed state is the cropped prompt
cache, and cropped-vs-fresh equality at chunk 1 is exactly what 3d's
byte-identical re-derivation of 3c's seed 8 — sampled inside a
12-seed call — proved. 3e's gate-1 seeds (20, 24) were block-first in
3d (fresh cache) and are re-derived alone (fresh cache); the tranche's
non-first seeds start on cropped caches, covered by that precedent.

### Power shape — F-2 FOUND (below); the rest cleared

Poisson thinning vs the exact binomial at the reachable rate over
8,192 draws: .75343 vs .75340. Per-item concentration enters only
through the class-level gamma dispersion, as §7 specifies.

### FREEZE FINDINGS — three, each closed executably today

- **F-1 — the arm zeroed a void competitor, which argues FOR
  DIRECTED.** Slip (f) read §4's "applied identically" as: a void
  competitor's count is 0 and the item stays in the test. Under the
  designation-exchangeability null that slot then cannot score, so the
  reverse's share rises and p FALLS — anti-conservative. Closed: an
  item with ANY void target (reverse or competitor) sits out the
  designation test, disclosed under `arm_void_excluded` with its raw
  vector; counts stay "counted by nothing" (§4). Three-way contrast,
  exact and in the fixture: competitor live p = 1/4, item excluded
  1/8, competitor zeroed 1/24. **Inert on the real experiment** (zero
  voids on the pinned battery — it cannot move the verdict in either
  direction); it corrects frozen semantics. W9 re-asserted; new mutant
  killed. Ratification: a doc-text correction to §4's "identically".
- **F-2 — the named-alternative power sits one estimator convention
  from the bar.** Frozen rule (population variance, 3d's λ precedent):
  shape .3082, P(SHORTCUT | H_shortcut) = .7636. Sample variance:
  shape .2921, **.7447 < .75**. The rule is NOT moved (frozen before
  any power number ran); `power_3e.json` now prints
  `dispersion_shape_sensitivity`, a SHAPE-RULE SENSITIVITY concession
  line, and `declared_underpowered_under_sample_variance_shape: true`.
  Load-bearing entries unchanged (m_min 8, m_s,min 3, THIN 10, anti
  3); the record reproduces from the frozen code (fixture). **Ruling
  for Michael:** declare the experiment UNDERPOWERED IN ADVANCE at its
  named alternative on this basis? Recommendation: yes — 1c precedent,
  the concession costs nothing and the tranche runs regardless.
- **F-3 — two unasserted attestations.** The gate-1 record's
  `items_sha256` was never compared to the §4 pin by the analyzer
  (the tranche's is), and nothing tied the gate-1 weights to the
  tranche's weights. Closed, additive: `check_gate1_vs_tranche_3e`
  (called by run() and by the full-shape path), shard `model_sha`
  presence and cross-shard coherence in `load_new_cells_3e`. Four
  fixtures, four mutants. (The real runner could not have produced a
  drifted record — `rederive_cell_3e` refuses an off-pin item file
  BEFORE model contact and 2b's loader pins the HF revision — stated
  plainly; the analyzer now says so itself.)

Fixture suite 118 → **125** (`tests/test_freeze_3e.py` + the W9
extension); mutation list 60 → **65**.

### Cold battery (fresh processes, `PYTHONDONTWRITEBYTECODE`, pycache cleared)

- Suite: 118 passed before any edit; **125 passed** after the closures.
- Full-shape: 9/9 terminals + 3/3 annotations (inside the suite).
- Referent battery: **15/15** on the real trees.
- `partition_3e.json` re-dump: byte-identical, sha = the §4 pin.
- `stream_map_3e.json` re-dump: byte-identical; 3e + 3d + 3c checks clean.
- `results/scorer_gates.json` re-run: byte-identical, PASS/PASS.
- `power_3e.json` re-run: byte-identical BEFORE F-2; regenerated with
  the sensitivity block after (19 s; the reproducibility fixture is the
  byte check from here on).
- Determinism fixture: twice, separate processes, == exp3's committed
  reference byte for byte (torch 2.12.1 / transformers 5.13.0 — no
  stack drift since exp3).
- Driver dry-run: 4 tiers in the frozen §10 order (gate1/410m,
  gate1/1b, sampling/410m ×4 blocks, sampling/1b ×8). Refusals: empty
  tree (gate1 and sampling), failed scorer record; a FORGED-flag scorer
  record passes the runner's precondition and is refused by the
  analyzer — the layers behave as designed.
- Mutation battery: **65/65 killed, baseline clean** (60 build mutants
  + 5 freeze mutants: F-1 exclusion dropped; F-3 items_sha pin,
  gate-1 model_sha, shard model_sha coherence, shard model_sha
  presence), run detached and alone after all closures; suite re-run
  cold afterwards: 125 passed; referents 15/15.

### Incidents, recorded

- A Python crash report at 04:00:57 (torch MPS `tanh_kernel_mps`
  SIGSEGV) belonged to PID 30000, a child of PID 29978 — Michael's
  Hermes agent (`com.reservoir.curator`) — not this session; no
  process of this session loaded torch before the determinism fixture.
- The mutation battery's first launch was stopped by me seconds in
  (the tool's 10-minute ceiling would have killed it mid-run). The
  stop landed inside mutant #1: `analyze_3e.py` on disk carried the
  `if False:` gate-1 mutant and a `.mutation_backup` sat beside it.
  Healed from the backup exactly as the harness's own
  `heal_stranded_mutants` would, verified (mutant text gone, gate-1
  branch present, no backups), relaunched detached in its own session
  before anything else imported the module.

### Ratification list for Michael (before the tag)

Doc slips (a)–(f) and the build dials as ledgered above; F-1 (semantics
correction — ratify, or revert to the literal reading; inert either
way on this battery); F-2 (the declared-underpowered ruling);
F-3 (additive); the standing H_half question under §7's clause; and
one note left UNCHANGED: the 410m replication text reads "unreplicated"
for both a non-rejection and an ANTI rejection at 410m — annotation
wording only, flagged rather than edited.

### RATIFIED — Michael, 2026-08-21 ("Ratified", in session)

Everything on the list above, as presented: doc slips (a)–(f) and the
build dials stand; **F-1** (an item with any void target sits out the
designation test — the doc's §4 "applied identically" is read as
"identically for COUNTS, and an unexchangeable vector leaves the
test") is the frozen semantics; **F-2** → the experiment is **DECLARED
UNDERPOWERED IN ADVANCE at H_shortcut** (recorded as a literal in
`compute_power_3e.DECLARED_UNDERPOWERED_RULING`, printed into
`power_3e.json`'s concessions; the frozen rule's own flag stays
computed beside it), which subsumes the open H_half question under
§7's clause; **F-3** additive. The design doc's text is NOT edited
(3c's convention: corrections live here). The 410m "unreplicated"
wording note stays a note.

Remaining before the tag: the gate-1 single-cell rehearsal
(`rederive_cell_3e("410m")`, 2,880 draws vs 3d's seed-24 shard) on
Michael's explicit word — model contact, asked for separately; then
`exp3e-preregistered`. Campaign launch is a separate go.

### Gate-1 rehearsal RUN — 2026-08-21, on Michael's word ("go — run gate 1, tag, and push")

`run_tier("gate1", "410m")` → `rederive_cell_3e("410m")`, the
campaign's own tier path, detached process, scorer-gate precondition
checked before the model loaded. **2,880/2,880 draws IDENTICAL to 3d's
committed seed-24 shard on the 45 items; n_diffs 0; fires_reproduced
= [(123, 24, 62)] — the 410m 'ecde' fire, by address, through the
production subset path.** Validated against every pin with the
analyzer's own checks: coverage == `GATE1_COVERAGE`; items == the
subset literal with its sha; `items_sha256` == the §4 item-file pin;
the attested shard sha == the 3d shard on disk == the §4 literal
(`check_gate1_committed_shas_3e`); model_sha = 2b's pinned 410m
revision; stack torch 2.12.1 / transformers 5.13.0 — the same stack
that produced exp3, 3c and 3d's streams. **Sixth consecutive
byte-identical reproduction on this stack**, the first through a
subset-restricted path (the stream map's "batch composition changes
no stream" claim, now executable on a real cell). The record is
committed as the campaign's 410m gate-1 cell; the 1b cell runs at
launch. No other model contact; no new sampled quantity for any real
cell — the regenerated draws were compared and discarded.

### TAGGED `exp3e-preregistered` — 2026-08-21

Freeze complete: findings F-1/F-2/F-3 closed and ratified, cold
battery green (suite 125, mutation 65/65, referents 15/15, determinism
×2, gate-1 rehearsal IDENTICAL). Campaign launch (gate1/1b, then the
tranche 410m → 1b in 16-seed blocks with the watcher) is a SEPARATE
go; projection to be ledgered before the analyzer runs.
