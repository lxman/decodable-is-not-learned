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

## Generation feasibility CLOSED — ready for build planning

Final F6-only independent review is clean: the exact former specification-only
HEAD bypass now refuses before pin derivation, eighteen additional scoped
negative cases refuse, and the genuine six-module historical import closure
is independently confirmed. The reviewer reproduced **38 tests**, all saved
archive checks, and unchanged bytes for all forty original full-run files.
Management checked the final published receipt hash and those forty hashes
again without regenerating items. **F5/F6 are closed.**

Final scoped evidence: `planning/feasibility-f6-review-20261004/`; receipt
`feasibility/runs/f6-verification-003-004.json` has SHA256
`17488fa066d42335725ea68340f777cd1f0fe2d28874098ea03fc2d0bc4723f7`.
The model-free battery is certified: four families × 500 pairs, all four arms,
exact source/launch bindings, counterbalance, oracles, collisions and baseline
audit. Production instrument planning remains active; its core C-1 correction
and complete literal integration annexes still need final review. No new
generation attempt, model contact, calibration, power, rental or verdict.

## Operations-plan annex delivered; integration boundaries ruled

The operations author delivered complete parameterized harness/operations
modules, a task index and interface contract. Management verified all **79
manifest entries**, checked its copied core against core-v1, and reproduced
**82 miniature tests** with zero failures/errors/skips and no forbidden imports.
The original core's tests are included in that count; do not add 48+82 as
independent coverage. Secured annex:
`docs/superpowers/plans/2026-10-04-exp7-annex/operations-v1/`; receipts:
`planning/management-operations-check-20261004/`. Fresh independent review is
in progress. These are fake operational adapters, not live launches or a
completed freeze/mutation battery.

The author correctly disclosed the collection/statistics interface mismatch
and unfinished final production bindings. Management read only their published
interface contracts and ruled **I1** (explicit raw-preserving verified adapter,
including true outcome-contact paths and baseline N/A/abstention handling) and
**I2** (pre-tag calibration uses committed candidate pins, not a nonexistent
preregistration tag/seal). Full rulings are in the build-plan index. Why: both
individually valid modules must compose under the actual stage order. Cost:
dedicated adapter, authorization and end-to-end fake-tree tests; no invented
raw draws or self-attested pass dictionaries. The respective authors have the
concrete requirements. Remaining complete source/worker bindings are required
before readiness, not left as open-ended work for the production implementer.

Operations-annex publication check caught the repository-wide `logs/` ignore
rule omitting five manifested harmless-mutation JSON receipts from the first
add. Add those exact hash-verified evidence files explicitly and verify every
manifested path against Git before accepting publication. No source or test
result changed; this is an archive completeness correction.

## Operations-plan review — six necessary local fixes

Independent review reproduced the 82-test/79-file/unchanged-core claims, then
demonstrated six bounded operational or harness defects in operations-v1.
Management read the actual source/reproductions, verified all **130 review
receipt bindings**, and independently reproduced all six using the archived
source and fake operational ports. No live process/network/provider operation
occurred. Evidence: `planning/operations-review-20261004/`; management probes
and reconciliation: `planning/management-operations-check-20261004/`.

**Ruling R1:** preserve child-owned terminal status if a fast child exits before
the parent's SID lookup. Post-spawn observation uncertainty is separate parent
diagnostic evidence, not an invented failed child terminal. Cost: distinguish
launch/observation state explicitly.

**Ruling R2:** an independently observed failed/stopped campaign must preserve
its whole inventory even when a DONE unit is invalid. Record that invalidity
without admitting it as a valid canonical unit. Keep invalid claimed-success
campaigns paused. Cost: separate failure-evidence preservation from scientific
unit admission; independent security/release gates still apply.

**Ruling R3:** failed/error provider-list envelopes cannot establish absence.
Require a validated successful observation before a release receipt; never
persist raw replies/error bodies. Cost: ambiguous responses require explicit
reconciliation instead of assumed absence. This finding used a synthetic
response, not a provider observation or credential incident.

**Ruling R4:** constrain the Git commit itself to the explicit publication
paths and verify its actual diff before pushing. Cached-index checks alone
cannot close concurrent staging. Cost: coordinate index activity and reject
unexpected committed paths rather than absorbing unrelated work.

**Ruling R5:** admit ordinary cold loading of a pinned source while distinguishing
nonexistent bytecode-cache probes from actual reads. Existing unpinned bytecode
must still refuse; retain alias/transient execution and exit-drift checks.
Cost: a precise loader/read rule instead of a broad bytecode exemption.

**Ruling R6:** heartbeat independently of blocking transfer/statistical/model
work, with a single serialized status writer. A beat before a long call does
not meet the timing promise. Cost: a real independent heartbeat capability and
fake-clock/concurrency tests, carried through the eventual production binding.

The original author owns one correction wave in separate scratch operations-v2,
preserving v1. It will receive scoped re-review. The declared final production
bindings and full fake-Campaign integration remain separate open work, not
claims supplied by the 82 miniature tests. NumPy's top-level import worked
under the original guard; no guard weakening is justified by the earlier
ctypes concern. Actual assembled numerical kernels still need guarded tests.

## Statistics-plan annex delivered and reproduced

The statistics author delivered complete G7–G10 bodies at the raw-data adapter
boundary, including all S1–S8 drivers, exact limb/histogram kernels, calibration
and one-time power drivers, saved-arithmetic validation and a separate pre-tag
calibration context. Manifest: **61 files**, SHA256
`71e3c791c13aa26e337b4fda2423ca8d9415647fea96eb79cd926d864528b05e`.
Management verified every entry and reproduced **37 statistics tests + 48 copied
core tests**, all passing with model/network hard guards and no forbidden
imports. These overlapping inherited tests are not 85 newly independent tests.

**C-1 correction implemented and reproduced:** the exact final-None fixture
returns unsupported after four evaluations, with no retry. The corresponding
aggregate subset fitter covers final/validation undefined values too. The
original core-v1 is untouched; the explicit patch and corrected copy live in
`docs/superpowers/plans/2026-10-04-exp7-annex/statistics-v1/`. Independent
scientific/code review, including closure of C-1, is in progress. Management
evidence: `planning/management-statistics-check-20261004/`.

The new statistical RNG, exact-kernel implementation, fixed-set bootstrap and
finite calibration/power conventions are clearly listed as proposals in
`statistics-v1/DELTAS.md`. No empirical alpha or power number exists. Guarded
planning tests used miniature raw worlds and bounded fabricated kernels;
production calibration/envelope/power and actual model-data statistics remain
unrun. Metadata emission of `SYNTHETIC-CASES.json` sampled nothing.

A fresh integration author owns the explicit StatsCampaignAdapter and final
composition work in separate scratch, reading completed statistics source
and the collection author's published interface only while collection is in
flight. Mapping must preserve raw strings, all 84 baseline cells and genuinely
verified stage authority/bindings. The full plan remains assembly-in-progress.

## Collection-plan annex delivered and reproduced

G1–G6 collection/provenance source and tests are delivered with a stable API
and explicit additive task text. Management verified its **64-file manifest**,
SHA256 `09062b27345430fc06cdc10e4a82dda23ae4019ac738d4481111f6703fd09b0e`,
and all **1,081 current repository input pins**. The copied guarded suite
completed in 106.866 seconds: **70 tests passed**, including 48 inherited
core tests, zero forbidden imports and zero model contacts. Receipts/log:
`planning/management-collection-check-20261004/`. Exact delivered bytes:
`docs/superpowers/plans/2026-10-04-exp7-annex/collection-v1/`.

Fresh independent collection review is active. The integration author now
has permission to inspect the completed producer source and compose its raw
outputs with statistics-v1; it previously read only the published interface.
Its broader contact inventory and fixed operations deployment remain required
composition work. Full-cardinality fake records are synthetic test evidence,
not a real predictor seal, power result or instrument freeze.

The collection annex explicitly proposes **B17** (zero-shot Q/A rendering),
**B18** (a separately authorized Pythia fp32 tensor-digest baseline) and **B19**
(fixed, separately counted preflight work). These are not silently ratified.
The B16 tokenizer timing change remains withdrawn. Later genuine model assets,
digest/host receipts, tag/projection and owner grants are required by the future
instrument; planning has created none of them.

Draft proposal consolidation is now
`docs/superpowers/plans/2026-10-04-exp7-decisions.md`. It distinguishes existing
approved dials from B1–B19 and the statistical implementation proposals, with
B16 explicitly withdrawn. The proposed schedule totals **1,585,152 sampled
outputs** including 144,000 old-anchor and 289,152 preflight draws, and **243,000
greedy continuations** including one-host gate/anchor overhead. These are
schedule arithmetic, not measured time/cost, and exclude loads, finite probes,
tokenizer checks and simulations. The $25 remains a planning cap. Final review
may require correcting proposals before presenting the actual ruling package.

## Operations correction wave reproduced

The original author delivered operations-v2 with all R1–R6 corrections and
fifteen new regression methods. Management verified **151 manifested files**,
the exact v1→v2 source/test/task diff and its before/after hashes, the unchanged
v1/guard, and the preserved red receipt: seven methods, eleven failed assertions,
zero errors against original operational sources. Management then reproduced
**97 passing tests**, zero forbidden imports, no source changes. Fake-clock
heartbeat gaps stayed ≤60 seconds through 901-second blocking dispatch calls.

Manifest SHA256:
`e379d82833121c138df26e20648a0d8dae6c5ba96a83bf14c23fa7c9165dd811`.
Secured source/evidence:
`docs/superpowers/plans/2026-10-04-exp7-annex/operations-v2/`;
management evidence: `planning/management-operations-v2-check-20261004/`.
Scoped independent re-review of R1–R6 is active. The integration author may
now inspect completed v2 and implement the remaining fixed O8 bindings,
including the actual separately scheduled heartbeat worker, stage/remote
bootstrap, independently secured verifier and full task registry. This is
source/test planning only; no live process, provider or monitoring operation
was performed. The six findings are not declared closed before re-review.

## Statistics and collection review findings reproduced

Independent statistics review clears C-1, exact n500 kernels, conditional null
law, outcome-untied Somers, finite thresholds, N5/N6/N9 constructions, shared
bootstrap and all S1–S8 implementations. It reproduced 37 statistics and 48
inherited tests, but found five necessary validation defects. Management
verified the **146-file** review manifest and reproduced all five against
statistics-v1 in isolated scratch with hard guards. Full-default forged power
records in these probes are explicitly fabricated arithmetic, with zero RNG
draws or calibration/power/analyzer calls; they are never campaign evidence.

Review: `planning/statistics-review-20261004/`; management scripts, receipts and
relocation-only provenance: `planning/management-statistics-review-20261004/`.
Review manifest SHA256:
`86b837e24c81aab4e9e206d4a99147a0293b389e064a25b4b74bfb70623f4c7e`.

**Ruling SR1:** bind or refuse external local helpers in the pre-tag candidate
context, including persistent/transient aliases and executed code. Explicitly
identify trusted installed runtime roots rather than trusting every file outside
the candidate repository. Why: an unpinned external helper executed and passed
entry/exit. Cost: a complete executable closure and adversarial import tests.

**Ruling SR2:** make saved power semantics consistent with independently rederived
sealed predictor/stratum geometry and every retained fit/main trace. All-constant
n500 predictors were accepted with positive D and all ten subsets POWERED; a
lost-subset replicate retained a defined D, and impossible ceiling/validation
Ds also passed. Require exact-set/undefined consistency, bounded Ds and derived
support status, including predictors constant within blocks but varying globally.
Cost: retain and validate sufficient saved per-family arithmetic; no simulation
rerun, stronger substitute alternative or adjustment to the primary rule.

**Ruling SR3:** admit only genuine failed bytecode-cache probes for pinned source
imports, preserving refusal of existing unpinned bytecode. Why: a legitimate
late pinned import refused before reaching its source. Cost: precise cold-loader
tests, not a blanket cache exemption.

**Ruling SR4:** rederive every printed power/envelope diagnostic from retained
base counts/vectors, including p-only rates/intervals, support, probability rows,
analytic expectations, D scatter and eligibility frequencies. Impossible values
such as 999 rejections among 128 and a [1,1] interval for zero fires passed.
Cost: sufficient saved arithmetic and domain checks; no empirical simulation
is run to verify a saved record.

**Ruling SR5:** require the declared 21 baseline methods in each family as well
as aggregate 49 applicable/35 N/A coverage. A coherent 20/21/21/22 catalog passed.
Cost: one structural refusal; exact method identities still bind to certification.

The original statistics author owns a separate immutable v2 correction wave;
the integration author is informed that the semantic-validator interface may
need independently derived geometry. Statistics-v1 is historical, not accepted
for final dispatch. C-1 itself is **closed** by independent review.

The independent collection review reproduced 70 tests, 64 annex bindings,
16 unchanged originals and 1,081 repository pins. It found two local defects.
Management verified its **78-file** review manifest and independently reproduced
both via the genuine fake-data producer loops. Review:
`planning/collection-review-20261004/`; management:
`planning/management-collection-review-20261004/`. Review manifest SHA256:
`b027c7acc070447cb320a5961085e9073beb2b0b1e65787ecbb9cd67ebea78ea`.

**Ruling COL-1:** compare preserved preflight q0 streams with completed canonical
q0 raw streams on resume, sealing and consumer verification, through a common
semantic check. A coherent completed-unit replacement passed resume with zero
sampler calls and sealed while the synthetic pair score changed 1/2→1/8. Keep
legitimate pre-collection preflight validation valid; test raw differences both
with and without a normalized-score change in new invocation contexts. Cost:
full saved-stream equality checks instead of individually valid contradictory
realizations of one stream. No real model output was modified or analyzed.

**Ruling COL-2:** readable `r+`/`O_RDWR` opens are inputs and need tracing/pins.
They must not inherit the write-only output exemption. The ordinary read of an
unpinned file refused, but `r+b.read()` returned it and passed entry/exit. Cost:
mode/flag-correct input checks, preserving exclusive writes, directory fsync and
cold-import behavior.

The original collection author owns separate v2 corrections, followed by scoped
re-review. B17–B19 remain owner proposals. None of these seven local corrections
changes the approved score, bars, family admission, scientific budgets or grid.

## Operations R1–R6 CLOSED

Scoped independent operations-v2 review reproduced all 97 tests and the exact
six original defects' corrected behavior. Targeted checks exercised the actual
heartbeat worker's monotone mailbox, terminal acknowledgement, duplicate-writer
refusal and parent-identity loss, plus the missing-bytecode race. No blocking
finding remains at the parameterized operations boundary. The live O8 deployment
and independently scheduled OS service bindings are still integration work.

Management had already reproduced the 97-test suite and exact diff; it now
verified and secured all **140 review evidence bindings** at
`planning/operations-v2-review-20261004/`. R1–R6 are closed for integration.
The original core/guard/v1 bytes are unchanged. These are fake-port and
synthetic-scheduling results, not live provider, monitor or model operations.

## New GitGuardian alert — verified false positive

Michael reported another alert. Read-only investigation identified **37864056**,
four occurrences in the newly archived operations-v2 review receipt at
`9134b3df0`. All four are the same synthetic `heartbeat_token`: a deterministic
SHA256 identity computed from the fixture directory, dummy PID123 and stage
`watch`. Management recomputed it from the exact committed config, checked the
writer claim and matched all four reported patch spans. It is not a credential.

Evidence and reproducible checker: `planning/gitguardian-20261004/`. Dashboard
status at read remains TRIGGERED; no status mutation was made. No provider/model
contact or experiment statistic was involved. The earlier credential incident
and cancelled Support follow-up remain closed.

Michael then said **"marked"**. Management verified incident37864056 now reads
**IGNORED / false_positive**, ignored at19:11 UTC. Selected GET-only closure
receipt: `planning/gitguardian-20261004/closure.json`. This alert is closed.

## Collection COL-1/COL-2 CLOSED

The original author's bounded collection-v2 correction passed independent scoped
re-review. Full raw preflight/q0 equality now applies on fresh collection,
completed resume and the common producer/consumer seal route; coherent middle-
row mutations refuse even when normalized output and first/last rows agree.
Readable read/write opens are traced and pinned, while ordinary output writes,
directory fsync and cold imports continue to pass.

Management matched the exact source/test diff, all **85 delivery bindings**,
unchanged v1 bytes and **1,081 repository pins**, then reproduced **80 passing
guarded tests**. The reviewer independently reproduced that suite, the ten
included regressions and additional adversarial probes. All **101 review
bindings** are verified and secured. No live contact or production simulation
occurred. The public API is unchanged; final composition now uses this revision.

Accepted annex: `docs/superpowers/plans/2026-10-04-exp7-annex/collection-v2/`,
manifest SHA256 `9903401a2aaf6b969aea66b5c6a5112640d8a09010c5deac7a3f7ecb7b0e7bb8`.
Review: `planning/collection-v2-review-20261004/`, manifest SHA256
`f6c6d9667c380b6c3e167cf2635e9445a85f0c036a64ca5745d50f6345ba49cf`.
Management reproduction: `planning/management-collection-v2-check-20261004/`.
B17–B19 and final integration retain their separate owner/review prerequisites.

## Statistics correction wave reproduced; scoped review active

Statistics-v2 is delivered and archived with **103 verified bindings**, manifest
SHA256 `a1e04f2ffff37e1427f08b3c7681321875887818205a59cdd2d7da9d896234ea`.
Management independently reconstructed the exact v1→v2 diff and before/after
inventory, verified the unchanged v1/core archives and reproduced **60 statistics
tests plus 48 inherited core tests**, zero failures/errors/skips or forbidden
imports. The inherited tests overlap prior suites. The scientific kernels,
bootstrap, secondaries, corrected C-1 reference, null-case metadata and guarded
launcher remain byte-identical to statistics-v1.

The delivered repairs address SR1–SR5; scoped independent re-review is underway,
so those findings are not yet declared closed. The integration author received
the changed v3 contract: independently rederive sealed predictor/stratum geometry
for saved-power checks, preserve version2 saved arithmetic, and require a
committed exact runtime authority for pre-tag calibration. Runtime discovery in
the test fixture is synthetic authority only, never production enrollment.

Annex: `docs/superpowers/plans/2026-10-04-exp7-annex/statistics-v2/`.
Management checker/receipts: `planning/management-statistics-v2-check-20261004/`.
Full-default saved-record fixtures use fabricated counts with zero RNG; inherited
stochastic checks remain miniature. No production calibration, envelope, power,
verdict, model/tokenizer contact or rental occurred.

The proposal register now points to the revised annexes and explicitly includes
their previously specified CPU-stage limits (24 hours each for calibration plus
envelope and for power; 8 GiB), retained-arithmetic storage/verification costs,
and 448,000 future tokenizer prompt/target comparisons. These are consolidated
unratified specifications, not measured resource receipts or new scientific dials.

## Statistics SR2–SR5 CLOSED; bounded SR1 read-closure residual

Scoped independent re-review closes **SR2, SR3, SR4 and SR5**, and verifies the
original SR1 external-helper repair. It reproduces 60 statistics + 48 inherited
core tests and clears the geometry-bound saved arithmetic, precise absent-cache
rule, complete diagnostic rederivation and per-family baseline coverage.

One necessary residual **SR1-R** remains: the calibration context authenticates
new opens but misses reads through handles opened before entry. The review's
full-package fixture, with the real 26-file source inventory and pinned caller,
returns deliberately unpinned external bytes through both `FileIO.read()` and
`os.read()`, with entry and exit accepting. Opening the same input inside the
context refuses. No actual calibration or effect on a scientific result occurred.

Management verified all **249 review evidence bindings**, matched the probe's
103 snapshot files to the committed annex and reproduced both read bypasses.
It also reproduced the independent **96 arithmetic cases, 56 refusal probes,
seven fit paths and all 80 envelope addresses**, with zero RNG calls. Previously
reproduced full suites were not repeated. Evidence:
`planning/statistics-v2-review-20261004/` and
`planning/management-statistics-v2-review-20261004/`. Review manifest SHA256:
`a4907326ce2405736b096aaa7b73f4be7b039e454b0bf653e6ad4af756ca76cb`.

**Ruling SR1-R:** bind actual readable handle/descriptor identity and bytes before
consumption, or refuse inherited/unattributed reads; include the two exact
regressions, pinned-input positive controls and replaced/aliased descriptors.
Preserve ordinary output handles and precise cold-cache behavior. Why: checking
only filename-based open events does not cover already-open inputs. Cost: one
bounded candidate-read-boundary repair and scoped re-review, with no scientific
change. The original statistics author owns a separate v3 workspace preserving
v1/v2; integration is informed and must incorporate the delivered repair before
final acceptance. This local finding is not delegated to O8 deployment.

## Statistics-v3 delivered; SR1-R re-review active

The author delivered the bounded inherited-read correction in a separate v3
bundle. Management verified all **133 bindings**, independently reconstructed
the exact v2→v3 diff and before/after inventory, and reproduced **72 statistics
tests + 48 inherited core tests**, zero failures/errors/skips or forbidden
imports. All prior scientific/statistical modules outside the candidate I/O
boundary/CLI, the C-1 reference, case grid and launcher are unchanged.

The cold boundary rejects inherited readable descriptors and OS-backed input
buffers, even when their path was pinned; permitted path reads instead produce
snapshots whose bytes and descriptor/path identity are verified before exposure.
Write-only outputs remain supported. Interface v4 adds this launch requirement
and the new source/runtime dependencies. The dedicated CLI closes both the stdin
wrapper and fd0. Platform census/identity logic is complete source tested through
fake syscall observations only, not a live fd scan or live stdin close. Pinned
native runtime remains trusted under the explicit serial CPython I/O contract.

Narrow independent SR1-R re-review is active; closure is not yet claimed. The
integration author received the delivered v4 contract and source. No raw-data,
geometry, saved-power arithmetic or scientific-dial change is introduced.

Archive: `docs/superpowers/plans/2026-10-04-exp7-annex/statistics-v3/`, manifest
SHA256 `951dc2e7c69714150f430028df8ec83a1722dcab792f2c229486cfb1e241c29b`.
Management checker/receipts: `planning/management-statistics-v3-check-20261004/`.
No production statistics, model/tokenizer/network contact or rental occurred.

## Statistics SR1-R CLOSED — all local annex findings resolved

Narrow independent re-review accepts statistics-v3 at interface-v4's explicit
source-reviewed, serial CPython I/O boundary. The original inherited FileIO and
os.read regressions now refuse before entry; pinned path/import/snapshot reads,
write-only outputs and the fixed CLI's fake dispatch pass. SR1–SR5 and C-1 are
closed. This is scoped annex acceptance; final composition remains outstanding.

Management verified all **389 review bindings**, matched all 133 snapshot files
to the committed annex and independently reproduced the unchanged reviewer
probes: **29 context checks, seven accepted controls, 22 expected refusals**,
plus platform identity/error/cleanup checks and CLI close/bind/dispatch order.
The previously reproduced 72 statistics + 48 inherited core suites were not
repeated. No added RNG or production driver invocation occurred.

Platform observations remain fake-only. The review explicitly records cold
serial descriptor stability, GC-visible CPython streams, write-only output
handles and trusted pinned native runtime as the interface's assumptions; it
does not claim an OS sandbox or measured host acceptance. Actual launch/runtime
provisioning and full assembled fake-tree tests remain integration obligations.

Review: `planning/statistics-v3-review-20261004/`, manifest SHA256
`aa16cb063853f537e483e70b72162241eb53bb5f7af6b2a1f37c2b3e09d8285f`.
Management reproduction: `planning/management-statistics-v3-review-20261004/`.
The integration author received acceptance of statistics-v3, collection-v2 and
operations-v2. All local correction waves are now closed; complete assembly,
source/task reconciliation and independent whole-plan review still remain.

## Complete assembly delivered; final-layout tests and whole-plan review active

The integration author delivered the complete literal assembly: **177 installable
files**, 34 guarded test tasks and a **273-file delivery manifest**, SHA256
`a1b9fa82f0bcca00a24d8929413bc9e1da44909636f5f759bc17a4b2a583ad54`.
Management verified each binding, unique source ownership and dependency ordering,
compiled 161 Python bodies without execution, reconstructed the exact upstream
delta and confirmed unchanged accepted statistics-v3/operations-v2 and corrected
C-1. Archive: `docs/superpowers/plans/2026-10-04-exp7-annex/integration-v1/`.

The source includes StatsCampaignAdapter, genuinely serialized fake producer
worlds, complete contact inventory, independent runtime preparation, fixed O8
bootstrap/heartbeat/verifier/transport bindings and full future freeze workers.
The author's 270 unique methods have passing evidence reconciled from a 269-test
run with one failure/one error plus targeted fixes and one new test. This is not
yet management's clean combined-suite claim. No full-default numerical worlds,
full mutation kills or two-real-process numerical determinism are asserted.

Management launched the final **direct installed-layout** guarded registry in
isolated scratch, detached PID **1168**, with durable status and monitor job
`exp7-integration-management-20261004`. Expected duration is about 25 minutes from
the author's earlier bounded run, not a campaign forecast. Automatic completion
follow-up is registered to this session. Initial checks/operator/launch evidence:
`planning/management-integration-check-20261004/`. A fresh independent reviewer
owns the mandatory whole-composition review in separate scratch.

**Pending plan reconciliation:** the delivered ownership registry groups many
modules into G1–G6/G7–G10/O1–O7/I-O8 blocks despite the standing module-by-module
build rule. Also, author `EXECUTIONS.md:52–53` attributes supervisor-root and
late-fault choices to Michael; no such owner approval is recorded in the main
ledger. Preserve those historical delivery bytes, but do not infer approval
from them. Correct attribution/task dispatch must be resolved in the reviewed
plan. Scientific dials and current feasibility/planning authorization are unchanged.
