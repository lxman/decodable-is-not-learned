# Experiment 7 — design ledger

## 2026-10-04: scope authorized, design proposed

Michael requested "Do the analysis and plan the experiment" after considering
the matched-token size analysis, a sampling-mechanism experiment, and an
across-task forecast. Management took this as the first two, and he then
explicitly approved the descriptive matched-token scope. That analysis lives
under `analyses/matched-token/`; this package records the separate design.

Draft: `experiment-7-design.md`. No dials ruled yet. No generator build,
tokenizer/weight download, model load, sample or new outcome contact.

**Ruling D1 (proposed):** counterfactual answer pairs and a difference of
target emission under both prompts, rather than another covariate-only
residual — the pair contrast cancels prompt-invariant answer preference
algebraically. Cost if wrong: it can still measure input-sensitive shortcuts
and shared item difficulty; it cannot adjudicate resolution versus construction.
The design makes that limit part of every possible licence.

**Ruling D2 (proposed):** one cross-family outcome, both 1B predictors, four
task families and meaning-preserving shams — useful discrimination at about
one million sampled draws, with no automatic second-outcome rental.

The first draft was written before the concurrent matched-token comparisons
were computed. Its generation rules are proposals requiring an independent
oracle/coverage feasibility check, not claims about existing implementation.
Thresholds, strata, power and budget recommendations await Michael's ruling.

**Design self-review D3:** both gates must read the same eligible families;
otherwise selectivity in an excluded family could license a forecast
elsewhere. Eligibility uses outcome support and availability only. Constant
predictors stay with D=0, keeping the eligible set invariant under the
arm-swap null. Also accounted explicitly for the k=16 untrained twin:
128,000 additional draws, 1,152,000 new-item draws in total.

Outside reads during design: arXiv abstract pages for Pythia (2304.01373),
Calibrate Before Use (2102.09690), and Surface Form Competition (2104.08315).
The latter two are cited narrowly for answer-bias/calibration context; no
full-paper methods review or novelty claim is implied. No Hub/model contact.

## Independent design review and revision — 2026-10-04

The first independent review found the core raw contrast's literal null
correct but its ordinary-language claim too broad. Fixed conditional answer
odds with prompt-dependent target availability can produce a positive raw
contrast: (.18,.02) versus (.09,.01) keeps 9:1 odds yet gives d=.04. The
draft's pooled conditional score did not close that loophole either.

**Ruling D4 (proposed, supersedes D1's score/null):** use the difference of
within-prompt conditional a0 proportions, averaged over canonical/sham
renders, with empty target rows contributing zero. Randomize target labels
conditionally within each pair/render's 2×2 table, fixing row/column margins,
under the independent-stream hypergeometric null. This cancels fixed target
odds even when target availability differs. Cost: sparse rows reduce usable
signal, and input-sensitive shortcuts/shared difficulty remain alternatives.
The proposed effect bar changes from raw d≥.01 to mean conditional x≥.05;
both are still unruled recommendations before any new-item contact.

**Ruling D5 (proposed, supersedes D3's arm-swap wording):** same-set eligibility
is invariant under the conditional randomization because y/u stay fixed and
constant x families remain. The two gates are a battery-level conjunction;
different retained families can drive the two aggregates. Per-family
contributions are mandatory, not an assumed common-family witness.

Other review fixes applied: component-null calibration at .005 and the
either-predictor joint rule at .01; feasible probability-table simulations;
separate forecast-power and selectivity-power-envelope disclosures; realized
support printed beside the frozen power grid; exact Somers' D denominator
and tie/stratum pooling; twin numerical performance non-gating; committed
projection before preflight; stronger generation/shortcut feasibility checks;
single-predictor draw accounting corrected to 640,000 including the twin.

Scoped independent re-review requested on the revised instrument. These
changes precede matched-token comparisons and all new model contact. No
Exp 7 build, synthetic calibration, sampling, power or outcome run occurred.

### Scoped re-review: ready for owner dials

The independent reviewer reread the revised source and found no remaining
necessary scientific-design fix. Checked: fixed-margin hypergeometric null,
unsupported-row centering, separate render conditioning, invariant eligibility,
component/union calibration, bounded power readings, Somers denominator,
twin gate wording, projection order and generation feasibility requirements.

**Interpretation retained:** under a true conditional contrast δ, finite-k
support attenuates the expected score by
`[1-(1-s0)^k][1-(1-s1)^k]`. Fixed-odds null cancellation is exact under the
sampling assumptions; the forecast is not availability-independent under
alternatives. This formula was checked algebraically and added to §4.
D4/D5 explicitly supersede the earlier score and arm-swap wording. Design
is ready for Michael's §10 ruling; all new model contact remains unstarted.

## Concurrent descriptive analysis complete

The matched-token analysis ran once at 16:36 UTC on Oct 4, after this design's
review and revisions. It finds a late aggregate size advantage with
nonmonotonic greedy correctness; see `analyses/matched-token/INTERPRETATION.md`.
No Exp 7 score, threshold, family, outcome or other rule was changed in
response. Design remains ready for the owner dials, not approved for contact.

## Dials approved — 2026-10-04

Michael: **"approved"**, answering "Approve these dials for generation-only
feasibility and build planning?" All ten §10 recommendations are ruled as
presented. Execute that scope: certify the paired battery model-free, then
write the complete-code/test build plan for the instrument. The budget is a
planning cap; model contact, rentals, ratification/tag, the once-only verdict
and essay/public propagation retain their explicit gates.

**Ruling F1:** generation-only feasibility is an explicitly separate precursor
to the instrument build — put prototypes and their independent checks under
`experiments/exp7/feasibility/`, with a pre-run specification, generation
certificates and a fresh review. Do not present prototype code as frozen
production instrumentation. Cost: validated logic still has to be carried
through the full build-plan/review/freeze chain. Stop for a design ruling
if a required family cannot supply support under its admitted constraints.

## Prototype feasibility delivered; independent review in progress

Implementer published specification before generation (`cf50ef837`), prototype
(`e8e32be4a`), preserved first-attempt evidence (`27dcf1775`), an old-shot
metadata indexing repair (`5ad3ccb07`), and corrected evidence (`fc80876ad`).
Current runs are `feasibility/runs/full-003` and its exact repeat `full-004`.
The report records 500 pairs per family / 8,000 prompts; 15/20/5/2 base blocks
(words/deduction/units/shapes). Management has read the specification, report
and execution ledger; fresh independent code/certificate review is in progress.
Treat their construction PASS as pending that review, not a final instrument
claim. The implementer's claimed 21 passing tests still require management's
reproduction before acceptance.

**Ruling F4:** retain and foreground the declared endpoint shortcut's
500/500 deduction-pair successes — the approved design forbids selection by
baseline performance and already bounds the result to input sensitivity.
Cost: this family cannot establish multi-step reasoning, and a later aggregate
result must print each family's contributions. No post-audit replacement.
The shape support is four target labels in two quadrilateral pair classes,
explicitly disclosed rather than equated with the predecessor's ten classes.

Build-plan index is being assembled at
`docs/superpowers/plans/2026-10-04-exp7-build.md`. A separate plan author is
preparing complete source/test annexes in approved scratch with synthetic-only
checks; it owns no production repository files. Missing annexes are explicit
and the index is not yet execution-ready. No calibration, power, sampler,
outcome or model contact has occurred in this approved planning stage.

## Feasibility review cleared; complete-code plan assembly

Fresh independent review of `91294c9aa..fc80876ad` found no necessary
construction/scientific fix and cleared the battery for build planning. It
reproduced 21 tests, the saved-pair oracle audit and all baseline summaries;
independently reconstructed every seeded assignment and checked all source/
launch bindings. Full disposition: `planning/README.md`.

**Ruling F5:** close both nonblocking verification gaps now: require the
fixed repeat-artifact inventory with historical launch/certificate bindings,
and exact slots plus seeded counterbalance assignments. Why: current evidence
passes independent checks, but reusable checkers should enforce those checks.
Cost: another scoped synthetic/saved-evidence verification round; no new
generation attempt or change to admitted items. Original implementer owns the
repair, followed by scoped re-review.

Management independently verified the 103 source pins at the approval commit,
12 launch pins per corrected run, exact saved artifact inventories, all
8,000 stored oracle/target labels per run and eight byte-identical artifacts.
Receipt: `planning/management-check-20261004/feasibility-binding-receipt.json`.

The first instrument-plan author delivered ten complete pure core modules,
not a complete campaign plan. Its 29-file manifest is verified and archived
at `docs/superpowers/plans/2026-10-04-exp7-annex/core-v1/`. Management reproduced
**48 miniature tests**, with no forbidden imports, and secured the log/receipt
under `planning/management-check-20261004/`. A fresh independent core review
is in progress. Three non-overlapping scratch authors are completing data/
collection, statistics/reporting, and freeze/operations annexes; no production
package is being built. Assembly must not claim readiness while any load-bearing
source/test composition remains absent.

**Ruling B16-disposition:** the first plan's proposed post-tag tokenizer-cap
check deferral is unnecessary and not adopted. The approved design requires
tokenizer-only cap validation during the later instrument build. This planning
stage writes the checker and fake tests only; no tokenizer is executed now.
Preserve the historical proposal in core-v1 and explicitly supersede it in
the assembled plan. Cost if wrong: a tokenizer-only build check needs its
proper later authorization, but a too-short cap must be caught before tag.

## Scoped checker repair and core-plan review

Feasibility hardening landed at `2a9fbef6c`, evidence at `98a0e899e`. Management
checked the stored scoped diff against actual Git bytes and reproduced
**35 tests, zero failures/errors/skips**, with model/tokenizer imports and
network operations refused. The tests revalidate archived evidence and
counterbalance assignments; no fifth full generation occurred. The old eight
deterministic artifacts retain their original hashes. Receipts/log:
`planning/management-check-20261004/feasibility-hardened-suite.*`. Scoped fresh
re-review is in progress before F5 closes.

The independent core-plan review cleared the conditional score, fixed-margin
null, Somers denominator, eligibility, finite thresholds, resampling and the
specified component-null cases, after 48 tests and additional exhaustive
checks. It found **C-1**, a necessary local totality fix: the single-family
power-fitting helper subtracts the target from a final undefined D. Management
reproduced the TypeError on the review's three-item deterministic fixture.

**Ruling C-1:** return unsupported with an explicit uninformative-outcome reason
when the final fit is undefined; never retry with different noise or strengthen
the target. Add the exact regression and apply the same rule to the aggregate
subset fitter. Why: a sparse/tied simulation must produce its diagnostic,
not crash. Cost: an undefined alternative remains unsupported. This is a
prototype helper defect, not a production power result. The statistics-plan
author owns the correction in the next annex; core-v1 remains historical.

Full review and executable evidence are secured under
`planning/core-review-20261004/`; management's reproduced failure is
`planning/management-check-20261004/core-c1-reproduction.json`. B3/B6/B7–9/B13
remain explicit implementation/scientific proposals for ratification, not
quietly approved choices. B16's stage change is already rejected above.

### Feasibility scoped re-review — one historical inventory gap

The exact-slot and seeded-schedule repair is cleared. Re-review reproduced
the 35-test suite, all ten pre-fix failures, the saved audit, and unchanged
bytes for all 40 archived full-run files. It found a remaining comparator
path: replacing launch HEAD with the real specification-only `cf50ef837`
and coherently replacing its pin inventory admits a commit with no runner
or generator (four historical pins instead of twelve). Management reproduced
that acceptance against the actual `2a9fbef6c` comparator. The original
battery's launch commit has the required executable files and remains valid.

**Ruling F6:** require the explicit execution-module inventory at the historical
HEAD before accepting its exact blob pins. A real but unsuitable commit is
not evidence for the attested launch command. Add the coherent specification-
only-HEAD attack as a refusal regression. Cost: another narrow provenance
check; no item selection, generation or scientific rule changes. The original
implementer owns this follow-on, then scoped re-review of F6 only.

Evidence: `planning/feasibility-rereview-20261004/`; management reproduction:
`planning/management-check-20261004/missing-runner-reproduction.json`.

F6 repair: `78ffc8c99`, evidence publication `eb957a6cc`. The comparator now
requires all six execution modules, walks their historical relative-import
closure, and refuses unbound package initializers. Management matched the
stored `review-f6.diff` to Git, checked all thirteen verifier pins against
the recorded commit, and reproduced **38 passing tests** with model/tokenizer
imports and network operations blocked. The exact coherent specification-only
HEAD attack is included. Receipt/log:
`planning/management-check-20261004/feasibility-f6-suite.*`. Scoped independent
F6-only re-review is in progress; no regeneration or archive rewrite occurred.
