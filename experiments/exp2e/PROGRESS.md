# Exp 2e — Progress Ledger

Chronological. The design doc (`experiment-2e-design.md`) stays as
ruled (§10 a–g, 2026-08-22); everything the build or the freeze
discovered that touches doc TEXT is ledgered here for ratification,
never silently absorbed (3c's convention). Build and freeze ran in one
session (§11), 2026-08-22, after the rulings. **Zero model contact;
no functional of the §5.1 family was evaluated against the label on
the real tallies before the tag.**

---

## 2026-08-22 — BUILD (session 2 of the compressed protocol)

Instrument at `experiments/exp2e/`:

- `functionals_2e.py` — the §5.1 family, pure functions on 2d's
  tier-loader shape: F1 = mean over sizes of log((r + ε)/c) (PRIMARY,
  ruling a), F2 = mean log(r + ε), F3 = midrank of the mean rate with
  the midrank of the floor partialled out by least squares (intercept
  + slope), B0 = −log c; ε = half a draw at the tier's own resolution
  (`eps_for(n) = 1/(2n)`: 1/64,000 main, 1/8,000 pilot; ruling c);
  the §5.5 variants (ε set, majority-only floor via `floor_key`, the
  reduced layout for the two first-digit-run rungs); the PAIRED
  family-cluster bootstrap for AUC(F1) − AUC(B0) on 2d's counts
  matrix, whose single-arm marginals equal 2d's
  `cluster_bootstrap_auc` CI exactly (fixture); the §6 tree = the
  referent branch first, then 2d's `verdict_tree` verbatim with 2d's
  ALPHA / AUC_BAR objects (ruling d).
- `analyze_2e.py` — every loader is 2d's (`analyze_2d.load_outcome`
  with its m5 known-answer gate and 2d's 250-file manifest,
  `load_sampling_tier` for pilot and main with the re-tally from raw
  bytes through 3c's total verify, `load_probe_predictor`,
  `battery_2d.floor_table` + `check_floors_against_doc`); 2e adds
  pins and gates only: 8 frozen-import shas over 2d's instrument
  (analyze/stats/battery/rederive, referents_2d.json,
  stream_map_2d.json, power_2d.json, power_envelope_2d.json); the
  273-file manifest `referents_2e.json` (272 tier files + 2d's
  verdict.json, relative to the tree root, own sha a literal); the
  §4 MAIN TALLY TABLE by literal (68 cells, compared to the re-tally);
  2d's primary by literal (`VERDICT_2D_PIN`: AUC .5454545454545454,
  block p .6674933250667493, CI [.5, .6666666666666666], 2 drops,
  11/23, FAIL) and the COMPARISON GATE (2d's thresholded predictor +
  `primary_test` re-derived from the same cells == the tree's
  verdict.json == the literal, field by field); 2c's probe AUC pin
  (.6007905138339921, 2d's record). `run()` = the referent phase
  (every refusal COLLECTED via `collect`, ValueError /
  FileNotFoundError only — anything else propagates) → the terminal
  or `verdict_2e` (primary + §5.4 secondaries: F2/F3/B0 through the
  same AUC machinery, F1 − B0 paired CI, Spearman ρ of each
  functional vs the corrected ascent with 2c's block test and
  bootstrap, the pilot replication at ε = 1/8,000 with its own AUC /
  ρ / rank correlation against main-F1, 1b-only / 410m-only, the 12b
  label, the probe column with both pins, the §5.5 sensitivities,
  the 2d comparison column, the full per-rung table). The §2
  disclosure rides verbatim as `known_inputs_caveat` and inside
  `licensed_sentence_if_pass`, which names B0's AUC (rulings f, g).
- `make_referents_2e.py` — the manifest builder (byte-idempotent;
  refuses any count but 273); `verify_referents_2e.py` — 12 numbered
  cold checks that STOP SHORT of any functional-vs-label statistic on
  the real tallies (2d's numbers are known answers; F1's correlation
  is not).
- Tests: `test_functionals_2e.py` (17), `test_analyze_2e.py` (18,
  incl. the disk-free `verdict_2e` fixtures on synthetic tallies with
  the real outcome / floors / probe, and the comparison gate on the
  REAL main tier — a known answer), `test_full_shape.py` (6) over
  nine worlds built by 2d's own world builder, closed by 2d's
  analyzer (the world's verdict.json), pinned by 2e's builder FROM
  THE WORLD, then run through the production referent path: W1 PASS
  (clean separation), W2 FAIL, W3 INDETERMINATE (2d's W3 spec: AUC
  .727, block p .144, CI [.53, .93] under F1), W4 manifest byte
  changed, W5 stored tally edited with the manifest rebuilt (the
  loader's refusal delivered as the terminal), W6 2d's verdict.json
  altered (the comparison gate), W7 the literal tally table disagrees,
  W8 a tier file missing, W9 PASS "floor-relative only" (rising at
  1.05 c, flat at .95 c — F1 AUC 1.0, F2 .60: the world where the
  floor covariate is the whole story, and the one that separates F1
  from F2 for the mutation battery).

Build-time facts (all from synthetic inputs or 2d's known numbers):
- Referent battery 12/12 on the real tree: the 273 files re-hash, the
  main re-tally equals the §4 table 68/68, the pilot re-tallies, and
  the comparison gate reproduces 2d's primary EXACTLY from the
  committed main tier through 2d's code.
- Runtime: 2d's analyzer 9 s on the real tree; a 2e world ≈ 20 s.

## 2026-08-22 — FREEZE (session 3, same session, worked adversarially)

Standing assignment: find the class defect. Attacked:

1. **3a's class — an unpinned verdict input at analysis time.**
   Executable sweep: every `open`/`gzip.open` during `run()` on a
   world logged and classified against the pins. 577 files opened,
   549 in a pinned set (the world's manifest, 2d's 250-file manifest,
   2e's 8 + 2d's 17 frozen-import literals, the 34 item-file pins).
   The 28 unpinned non-code reads are 2c's
   `results/screen/tier1/*.json` (26), `battery/items/hamming8.json`
   and `results/inclusion/m1_ejections.json` — all from
   `family_map.scored_battery_families()`'s screen-aware directory
   listing, consulted ONLY by `battery_2d.check_order_against_2c`,
   which compares the result to the literal `RUNG_ORDER_2D` and can
   refuse but cannot move a number. Not a verdict input. CLEARED
   (same reads existed in 2d; recorded here because the sweep is new).
2. **Lesson 8 — the refusal terminal from the tree the producer
   leaves.** 2e's producer is 2d's closed campaign; the trees that can
   exist are the committed one and its drifts. W4/W5/W6/W7/W8 each
   deliver INSUFFICIENT_DATA executably with the reason verbatim (a
   changed byte, a stored tally that no longer matches its draws, an
   altered 2d primary, a wrong literal table, a missing file). The
   boundary chosen (finding F-1 below) is what needs ratification.
3. **Determinism.** `verdict_2e` on the same synthetic cells in two
   separate processes: byte-identical records (sha
   d3827f26…; FAIL world, AUC .7391, block p .1307).
4. **The known-answer gate for the inherited statistic.** Exact, on
   the real tree (battery 9, fixture): 2d's AUC .5454545454545454 /
   block p .6674933250667493 / CI / 2 drops / 11 / 23 / FAIL.
5. **The functional's remaining freedom.** With ε, c and the label
   fixed by literals and 2d's frozen rules, F1 is a fixed monotone
   map of each rung's two rates; no dial survives the tag. The
   zero-draw ordering (log(ε/c) orders zero-rate rungs by −c, i.e. by
   B0) touches exactly two real cells (rev_string7 both sizes,
   reverse_string 410m), both in the flat reversal family — disclosed
   in §5.1 already.
6. **Mutation battery** (`tests/mutation_check.py`, both directions,
   55 mutants over functionals/analyzer/builder). FIRST PASS 41/55:
   fourteen survivors, every one a FIXTURE gap, none a change to the
   frozen code — four `run()`-routing provisions (tally pin,
   comparison gate, manifest check, failures → the terminal) that
   only the deselected full-shape worlds exercised; a symmetric
   synthetic fixture blind to a 1b/410m column swap and to the ε and
   majority-floor rows coinciding with the primary; no negative case
   for the probe-AUC pin; paired-bootstrap fixtures too weak to see
   kept undefined resamples or a reversed difference; two redundant
   guards (the `_rate` n_draws check behind `_n_draws_of`, the
   manifest count behind `check_manifest`'s) tested only one level
   up; the floor-range guard untested. Closed with ten new fixtures
   (suite 41 → 51: 21 functional, 24 analyzer incl. four `run()`
   routing tests on the module world, 6 full-shape; the synthetic
   verdict fixture made asymmetric — at 410m the rising/flat ORDER
   REVERSES while the mean over sizes still separates; the probe
   check extracted to `probe_auc_matches` so both directions are
   testable). SECOND PASS on the fourteen: 14/14 killed → **55/55**.
   Worlds re-run after the helper extraction: 6/6.

### Findings for ratification

- **F-1 — the §6 terminal's boundary.** §6 says INSUFFICIENT_DATA when
  "any pinned referent fails". Built: a failure among 2e's TREE
  referents (2d's 272 tier files and verdict.json by sha, a stored
  tally disagreeing with its re-tally, the §4 tally table, the 2d
  comparison, the outcome known-answer gate, 2d's manifest entries)
  is collected and delivered as the terminal; a failure of an
  INSTRUMENT pin (2d's code and 2c/2b/exp3's frozen files, the item
  files, the two manifests' own shas, 2d's stream map) is a hard
  error — the instrument is not what was tagged, and no verdict is
  produced. Recommend ratify; §6 text proposed as slip (b).

### Doc slips — proposed text, apply only on Michael's word

- (a) §5.5 / §10 c: the ε sensitivity set {1/64,000, 1/32,000,
  1/3,200} includes the primary's own ε (1/64,000 = half a draw);
  say so: "the first row is the primary, repeated for reference".
- (b) §6 terminal 1: add the F-1 boundary sentence (tree referents →
  the terminal; instrument pins → a hard error, no verdict).
- (c) §5.1 F1: "a rung sampling at exactly its format floor scores 0"
  → "scores log(1 + ε/c), ≈ 0 (at most .0078, at the battery's
  smallest floor .002)".
- (d) §5.1 F3: state the built definition — midrank of the mean rate
  over sizes, least-squares residual on the midrank of the floor with
  an intercept.
- (e) §4 "lists all 272 files": the manifest has 273 entries (the 272
  tier files and 2d's verdict.json, as §11 already says).
- (f) §5.4: the probe column's two numbers come from different
  records — AUC .6008 is 2d's probe-on-the-2d-label secondary, ρ .368
  is 2c's probe against 2c's frozen ascent; label them so.
- (g) §2 disclosure completeness: the pilot tier's per-cell tallies
  were as visible to the designer as main's (2d's runner logs and
  `power_2d.json`'s attested pilot predictor); the replication is
  independent in SEED, not in what the designer knew.

## 2026-08-22 — RATIFICATION AND TAG

Michael: "F-1 ratified, slips as recommended — apply and tag." F-1's
boundary sentence (slip b) and slips (a), (c)–(g) applied to the
design doc in place; no dial, bar or branch moved. While applying
(g): the analyzer's `KNOWN_INPUTS_CAVEAT_2E` was a PARAPHRASE of the
§2 paragraph, and ruling g says verbatim — replaced with the
paragraph itself (extracted from the doc, bold markup and line
breaks normalized), pinned by a fixture that re-extracts and
compares. Cold battery re-run in fresh processes after the edits
(referents 12/12; suite 52); tag `exp2e-preregistered`. Next: the
projection sealed before the analyzer (with the §2 disclosure — its
author has seen the tallies), then `analyze_2e.run(write=True)` ONCE
on Michael's go → `results/verdict.json` → `exp2e-closed`.
