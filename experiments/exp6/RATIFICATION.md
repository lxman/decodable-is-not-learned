# Experiment 6 — ratification record

**RATIFIED by Michael 2026-09-29: “ratified”.** All recommendations below
accepted, including D-1–D-16, O-1–O-5 and the B/N amendment lists. The
corrections are applied; final validation passed. `exp6-preregistered`
at `6ac42458e` is annotated, byte-verified and pushed.
This package was consolidated from the preceding coordinator's battery
and instrument packages at instrument head `2e54bd4cf`. The evidence
below describes the pre-ratification state; the dated completion entries
in `PROGRESS.md` record validation and tag binding.

## State and evidence

The question is whether the small-model item-order forecast transfers to
a benchmark-derived second battery across four outcome families. The
built battery has **17 rungs, 10 tasks, 500 items per rung**, with two
base-8 anchors and a copy control. The original approved design has
18 rungs/11 tasks; `logic_grid` was excluded during the build.

Takeover checks reproduced 395 fast tests and the cold battery's 10 PASS,
0 FAIL, 4 expected SKIP. Its checks cover item/floor/stratum pins, 219
referent files, eight committed tallies, the import surface and 314
read-sweep paths with none unpinned. The committed mutation logs reconcile
369 names: 309 fast kills and the identical 60 survivors killed slow,
none open. The preceding final slow-suite run reported 232 passed.

The adversarial freeze found and closed an import-path defect that could
turn a synthetic null from BATTERY-BOUND into GENERAL with every earlier
pin passing. It also closed lazy-import coverage, cross-host resume and
bytecode/source-identity defects. The final review's fixes were re-reviewed;
the remaining items are listed below. Evidence: `FREEZE_CHECKLIST.md`,
`PROGRESS.md`, `mutation_fast.log`, `mutation_slow.log`.

**Contact disclosure:** on 2026-09-28 a prototype mutation test fetched and
loaded SmolLM3's endpoint weights, then loaded them again from cache. Both
attempts stopped at the move to CUDA on the Mac. No tokenizer, forward
pass, item reading or score occurred. The runners' falsy-loader fallback
was corrected; tests now run offline against an empty cache. The record
must say “no model has read an item”, rather than “zero model contact”.

`PRETAG_AUDIT.md` reconstructs ten real-tree analyzer calls through this
takeover, all cold-battery refusals before any campaign data existed.

## Approved decisions

The D numbers preserve the earlier packages' decision IDs.

| ID | Ratified ruling | Consequence |
|---|---|---|
| D-1 | Ratify 17 rungs/10 tasks; exclude `logic_grid`. | Its clue generator isn't published, so it fails the design's admission rule. |
| D-2 | Keep the original primary rung-set rule; report S13 over the heuristic-clearing rungs beside it. | Maintains comparison with the first battery. `temporal` is solvable by string matching on every item; heuristic floors are also higher on `lcs` and the unit rungs. |
| D-3 | Keep the primary strata; S11 conditions on the extra structure levels descriptively. | Crossed strata can hold only one item. |
| D-4 | Keep both rebuilt unit rungs. | Numbers/options are drawn without seeing the question's roles; shortcuts and fitted-guesser readings remain disclosed. |
| D-5 | Leave `deduction3`'s shots as drawn. | Both demonstrate a directly stated answer; disclose that limitation. |
| D-6 | Keep exact-match IPA as primary, with relaxed-convention S12. | A correct transcription in another convention can miss primary exact match. |
| D-7 | Keep the accidental 5.7 GB cache entry. | It is already disclosed; deletion provides no experimental reset. This is the takeover recommendation where the earlier package left a choice. |
| D-8 | Add the accidental-contact disclosure to the design's status and §2. | Name the two loads, with no item read or scored. |
| D-9 | Replace “on four outcome families” with “on at least three of four outcome families, named for each predictor”. | A holding predictor needs three, and the holding sets needn't be identical. |
| D-10 | Ratify the count-based BATTERY-BOUND sentence quoted below. | Failure of the naming rule permits one firing family per predictor. |
| D-11 | Print “withdrawn” only when every evaluable test was POWERED for the exact rung set it read. | A different realized set gets the resolution-limited reading. |
| D-12 | Ratify gate 1(d), measured weight digests against the earlier Mac records before prompting. | Wrong weights halt before scoring; preflight rehearses cross-host identity. |
| D-13 | Ratify the corrected seal-order caveat below and outcome preflight after the predictor seal. | “It writes no record” replaces “It stores nothing”; anchor scores are printed. |
| D-14 | Count only evaluable families in the headline condition, and say so in its sentence. | Already implemented under the coordinator's ruling; owner ratification remains required. |
| D-15 | Narrow the rental bundle to `master` and the `exp6-*` tags, verifying required refs before use. | This still carries private files/history reachable from master; it is not a content-filtered bundle. |
| D-16 | Accept the three disclosed residuals below. | No further instrument redesign proposed. |

The heuristic-floor choice in D-2 is substantive. Floors (rule → heuristic):
`temporal` .25 → 1.00; `unit_interp2` .20 → .50; `lcs` .10 → .474;
`unit_interp1` .20 → .358. Promoting those floors to the primary would
remove `temporal` and change which other rungs are read. The recommended
package keeps this as the named S13 comparison.

**D-10 sentence:** “Neither predictor reached the naming rule's bar on the
field's tasks: each fired on at most one of its evaluable families. Read
under the power record.”

**D-13 replacement seal-order wording:**

> The predictors were sealed before any outcome model was handed an item
> of this battery; the endpoints, rung sets and power record before any
> intermediate checkpoint was scored into a record; the projection before
> the sweeps. Before the predictor seal, a test on 2026-09-28 loaded the
> same outcome endpoint's weights twice, first by download and then from
> cache (no tokenizer, no forward pass, no item read; the ledger has the
> account). The outcome preflight runs after the predictor seal and loads
> each family's endpoint and first grid step. It writes no record. Of what
> a model writes on an item of this battery it reports shape, timing and
> identity, and no score; it holds 2c's two anchors to their committed counts.

The wording explicitly counts two loads, correcting the earlier package's
“once” shorthand for one incident. The preflight's own file remains exempt
from the tag (N-8); each outcome preflight must be ledgered with UTC time,
HEAD and the predictor-seal hash it checked.

**D-16 residuals:** simulated power probabilities are bound by the seal
rather than recomputed by the analyzer; an endpoint load can't resume on
a different host without moving the partial load aside; `run()` accepts
non-default permutation/bootstrap counts but records `frozen_counts` and
the production CLI uses the frozen defaults. Also disclosed: the predictor
seal skips dotfiles, but a dot-directory containing records would enter
its table; no producer creates one.

## Ratified correction checklist

1. **O-1, disk:** change `run/box_setup_6.sh` from 170 GB on `/workspace`
   to 230 GB on both the home/cache and workspace filesystems; request
   250 GB for the rental. The earlier estimate omitted the retained 55 GB
   OLMo-2 13B step-0 cache. Verify units when comparing provider GB to `df`.
2. **O-2/O-4:** apply the chosen D-9/D-13/D-14 licence wording and its tests.
3. **O-3:** record the outcome preflight's time, commit and predictor-seal
   hash; retain the disclosed preflight exemption.
4. **O-5:** correct the two stale “scores nothing” docstrings in
   `pins_6.py` and `tests/test_preflight_6.py`.
5. Apply D-15's bundle change if approved, with a ref/binding check before
   any box receives it.
6. Apply all design amendments below, reconcile claims with the actual
   instrument, and carry the coordinator rulings into the permanent ledger.

## Design amendment map

The full B-1–B-36 and N-1–N-16 lists are already committed in
`../../docs/superpowers/plans/2026-09-27-exp6-battery.md` and
`../../docs/superpowers/plans/2026-09-27-exp6-instrument.md`. Both lists are
ratified, including the budget/stratum changes. The final
instrument is the repository's, not the plan's older code blocks.

- **Status, §2, §3.1:** 17 rungs/10 tasks; remove `logic_grid`; disclose
  reconstructions, string-level collision limits and content overlap,
  the eleven administration departures of B-29, build contacts and the
  two weight loads; update the real-tree execution tally.
- **§3.1–3.2:** budgets on both instruments: number 8, word 12, span 12,
  sequence 16, IPA 24, with anchors retaining their committed shapes.
  `temporal` uses span; ASCII strata add frequency; IPA uses its built
  length bins. Include the built item/shot, option-count and floor rules.
- **§3.3:** pilot and twin read 17 rungs; pilot is printed in S6, while
  power reads the sealed main tier. State the copy-control referent shape.
- **§3.4:** gate 1 runs on every sweep host: both endpoint loader paths
  identical on 20 rungs; counts against the sealed endpoint and the Mac's
  anchors within 15 items per rung; anchors checked at every grid step;
  measured checkpoint digests held to the Mac's. Endpoint loads resume
  only on their original host.
- **§3.6:** 16 instrument files plus 17 item files bound by the tag;
  import pins from the first runner/analyzer commit, entry and exit
  checks, lazy paths measured, foreign modules refused, executed bytecode
  held to the hashed source.
- **§4:** joint tree-level power reported as bounds; independence between
  families is an explicit modelling assumption.
- **§5:** add S11 structure-conditioned, S12 relaxed IPA on both sides,
  S13 heuristic-clearing rungs. Update S4's types after the exclusion.
- **§6:** the owner-ruled licence text and headline condition; power must
  cover the set read before withdrawal; distinguish predictor degeneracy
  from constant/thin outcomes.
- **§7/§11:** predictor preflight → predictor stage → predictor seal →
  outcome preflight → endpoints/rung sets → power once → endpoint seal →
  projection → sweeps. Preflight scores both anchors on all 500 items at
  each read. Record disk requirements, atomic writes/torn-record refusal,
  halt artifacts, stage ordering, host checks and offline test isolation.

## Execution after ratification

Apply the changes in one pass. Run the final fast suite, slow files, both
mutation passes, import scan and cold battery; append that real-tree
analyzer call to `PRETAG_AUDIT.md`. Long jobs launch detached through
`Popen(start_new_session=True)` with durable logs. The earlier estimate is
about 2.5 hours for the final checks, not a measured new runtime.

Commit and push each meaningful revision. Cut the annotated
`exp6-preregistered` tag only after the checks, verify its binding with
`require_prereg_6` against real git, then push it. Predictor preflight is
the next owner-gated stage. Every rental create/destroy, the analyzer's
scored run, and close-out retain their explicit gates.

Keep the original git-ignored workspaces until their rulings/evidence are
preserved at ratification. Sources: their `ratification-battery.md`,
`ratification-package.md`, `rulings.md`, final review and scoped re-review;
the committed ledger and freeze checklist take precedence for chronology.

## Application — 2026-09-29

The design now incorporates the approved amendments. Licence text names
at least three of four families per holding predictor, two accidental
loads, no preflight campaign record, and evaluable headline families.
The disk guard uses decimal GB on both filesystems; the bundle advertises
only master/exp6 tags and verifies required refs and byte bindings before
use. Both stale preflight docstrings are corrected. All 109 coordinator
rulings are preserved verbatim in `BUILD_RULINGS.md`; the original
workspaces are retained. Final validation: 396 fast tests and 234 slow
tests passed; 369 mutants killed (309 fast, 60 slow); import scan as pinned;
cold battery 10 PASS, 0 FAIL, 4 expected SKIP, 314 reads/zero unpinned.
`PRETAG_AUDIT.md` now records eleven real-tree calls. `PROGRESS.md` records
timings and the tag-binding verification.
