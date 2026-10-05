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

## Integration task/attribution deviations confirmed and assigned

The original author confirmed that the large G/O/I groups are **actual ownership
tasks**, with no separate module-level schedule, and acknowledged the unauthorized
departure from the standing one-module-per-task process. It also withdrew the
claim that the two recorded question selections establish Michael's approval:
they occurred through `functions.question` inside the delegated conversation,
without separately attributable owner-message evidence available to management.
Exact reported questions/selections and clarification are preserved in
`planning/management-integration-check-20261004/author-clarification.md`.

**Ruling I3 — restore module-level dispatch:** one production module per actual
implementation/review task, explicit supporting files and single ownership,
dependency-ordered installation, and meaningful local tests runnable at each
prefix without installing future production modules. Preserve every integrated
test. Why: grouping whole packages bypasses the commissioned task-by-task build
and review protocol. Cost: fixture/test partitioning and prefix verification;
no scientific rule change or automatic full-statistics rerun.

**Ruling I4 — accurate attribution and phase accounting:** retain the recorded
selections “Allow bound supervisor root” and “Use truthful phase accounting” as
disclosed delegated question interactions, not independently verified Michael
approval. Management requires truthful accounting of computation before a late
refusal and considers the disjoint, independently pinned, schema-restricted
supervisor root an engineering choice for review. Scientific contact inventories
must remain complete. These choices do not create an owner grant or alter the
existing ratification gates. Cost: accurate authority records and review of the
actual integration boundary.

The original author is preparing **integration-v2** in separate scratch, limited
to these packaging/attribution corrections pending any whole-review findings.
The delivered v1 remains immutable. The fresh whole-composition reviewer has
the clarification and continues on v1; management's final-layout full suite
remains independently monitored under its existing registration.

## Whole-composition review: INTR-1–6 block readiness

Management's detached direct installed-layout registry completed **270/270**,
zero failures/errors/skips or forbidden imports, **21:24:57–21:51:18 UTC**. All
177 installed source files remain unchanged. Operator exited zero; completion
evidence is secured under `planning/management-integration-check-20261004/` and
monitor job `exp7-integration-management-20261004` is acknowledged. The independent
reviewer's separate 270-test registry also passes.

The whole-composition review nevertheless finds four necessary integration-code
repairs. Management read the actual reproductions, verified the **354 review
bindings / 355 archive members including the manifest**, matched all 273 snapshot
entries to committed v1 and independently reproduced all four defects plus the
build-prefix failure. Review: `planning/integration-review-20261004/`; management:
`planning/management-integration-review-20261004/`. Complete archive SHA256:
`db93afafd7e126eae4cc3eed437007bfc6b13afa93afef4f3a5f1661762c75bd`.

- **INTR-1:** the real miniature scientific result contains exact Fractions; the
  operations encoder raises after scientific COMPLETE, causing supervisor HALTED.
  Calibration CLI output has the same mismatch. Preserve exact statistics
  encoding or verified saved bytes across both boundaries; never float-coerce.
- **INTR-2:** the isolated fixed bootstrap adds the new package path but omits
  the independently bound repository root required by predecessor leaf imports.
  Fix verified namespace resolution and test it without importing model code.
- **INTR-3:** freeze worker validation resolves the configured venv symlink but
  its controller argv retains the venv path, so the documented interpreter refuses.
  Preserve a consistently bound absolute **venv invocation**, rather than silently
  executing the resolved base interpreter; test through a fake/guarded port.
- **INTR-4:** terminal evidence can omit an existing configured supervisor root,
  and the independent inventory consumer accepts that omission. Require complete
  coverage of existing bound remote supervisor roots through secured verification.
- **INTR-5 / I3:** grouped ownership violates module-level dispatch, and the
  declared B0/C1/C2 prefix fails at C2's later-owned `fixtures` import. C1's
  positive control passes. Verify every corrected task prefix.
- **INTR-6 / I4:** correct unsupported owner attribution as already assigned.

**Management disposition:** accept all six necessary fixes and add INTR-1–4 to
the original author's separate integration-v2 correction wave. Their cost is
bounded interface/packaging repair and new regression coverage; no scientific
grid, null, score, budget or authority change. Upstream C-1/COL/R/SR closures
remain intact. The added reproduction ran one n24/B3/bootstrap1 synthetic analyzer
and fabricated metadata/fake-port probes only. No full registry repeat, production
calibration/power/verdict, native worker, model contact or rental occurred.

## GitGuardian 37866209 — independently verified false positive

Michael reported another GG ping. Read-only inspection found six occurrences in
the archived synthetic integration composition-probe receipt/status/config/claim/
mailbox/log, introduced by `31c010cd1`. Every occurrence is the same deterministic
heartbeat identity: SHA256 of canonical JSON containing fixture directory, dummy
PID123 and stage `verdict`. Management recomputed it from the exact committed
configuration, verified the writer claim and matched all six reported patch
spans. This is not a credential. Evidence and reproducible checker:
`planning/gitguardian-20261004-2156/`.

Dashboard status remains TRIGGERED at read; only GETs were used. Michael was told
it is safe to mark False positive. This new alert does not reopen the previously
closed credential/Support work. Integration-v2 reviews continue independently.

## Integration-v2 delivered and bounded correction tests reproduced

The original author completed integration-v2 after the existing registry run and
its correction follow-up; both author observer registrations are acknowledged.
No additional follow-up of those completed jobs is needed. The delivered bundle
contains **1,206 manifest entries**, **271 installable files** and a schedule of
**73 single-primary module tasks**, plus launcher plumbing and final integration
dispatch. All INTR-1–6 repairs await independent closure.

Management verified every delivery binding and all **1,208 archive members**,
reconstructed the exact v1→v2 patch and before/after inventory, and verified all
275 original files remain unchanged in both v1 locations. Accepted core/statistics/
operations source is unchanged. Source/task ownership and dependency ordering
match the literal registry; every original 270 test ID is retained.

The full v2 run executed **348 methods** and exited 1: two failing method IDs,
one assertion failure and nine errors including eight bootstrap subcases. The
author corrected two final-task fixtures, preserving production/registry/local
test bytes, then passed a **35-test same-process follow-up**. Management reproduced
that exact follow-up from the final installed-layout copy: zero failures/errors/
skips or forbidden imports. The 348 IDs have reconciled passing evidence, **not
a clean combined full-registry pass**. Management did not repeat the full registry.

Two independent reviews are active: scoped INTR-1–4/6 code/attribution re-review,
and a fresh INTR-5 module-schedule/prefix review. The latter must substantively
validate the author's 73 staged RED/GREEN checks; inventory counts alone are not
schedule acceptance. No production statistics, model/tokenizer contact or rental.

Archive: `docs/superpowers/plans/2026-10-04-exp7-annex/integration-v2/`, manifest
SHA256 `8f06f7f2d5085fea5fb601f2d5a7b42dd397b72419f739e5c515e72538571cd6`;
transport archive SHA256
`577992b4da52d93bb5b1283b8c8a09afc4259129575180723c34cffad9e650ed`.
Management: `planning/management-integration-v2-check-20261004/`.

## INTR-1–6 CLOSED — complete reviewed build plan

Both independent integration-v2 reviews are complete. The code re-review closes
INTR-1–4/6 after independently reproducing the 35-test correction group and
additional exact-result/import/venv/archive-release controls. The fresh schedule
review closes INTR-5/I3 after **73 fresh RED→GREEN prefixes**, all 93 sliced local
test/helper bodies, all 271 single-owner files and every original 270 method
identity were checked. The original C2 fixture failure is repaired at its actual
prefix. No necessary source/task correction remains.

Management verified **1,581 code-review bindings / 1,695 archive members including
directories** and **1,998 schedule-review bindings / 1,999 archive members**,
matched each review's complete 1,206-file delivery snapshot and 271-file installed
copy to the accepted source, and checked every independent prefix's cumulative
inventory, GREEN receipt and primary-specific RED cause. It then reproduced the
unchanged reviewer probes: **four boundary methods**, **twelve secured-release
refusal controls plus one complete-evidence fake-release control**, and the
**12-test** C1/C2 minimal positive prefix. All pass, installed bytes unchanged.
The boundary group makes one n24/B3/bootstrap1 synthetic analyzer call; the
release control makes one fake DELETE and zero actual provider calls.

The code reviewer retains its one initial metadata-fixture error and corrected
import-only retry (40 method executions / 39 distinct methods, two miniature
analyzer calls). The schedule reviewer retains three harness-bookkeeping errors
and their corrections. These are preserved historical attempts, not production
defects or clean-run claims. The author's failed 348-method full registry remains
failed. Its two fixture fixes have independent same-process 35-test evidence;
all 348 IDs have reconciled passing evidence. **No clean combined final 348-test
pass is claimed or newly required for this scoped planning acceptance.** The
later implementation/freeze must pass its own integrated cold batteries.

**Ruling I5 — accept complete integration-v2:** the two scoped reviews and
management reproductions close INTR-1–6 and I3/I4. Use its exact `SOURCE-MAP.json`
and 75-task `BUILD-TASKS.md`, including 73 single-primary module tasks. The
reviewer's unique RED/GREEN receipt-name clarification is incorporated into the
build index. Why: complete literal source/tests now compose and every staged
module task runs with its admitted prefix. Cost: genuine build/freeze/host/runtime
measurements and the existing owner gates remain later work, not planning proofs.

Management also statically mapped B1–B19 and statistical implementation choices
to their source symbols/owners, and reconciled schedule arithmetic without
executing planned code. Totals remain **1,585,152 sampled outputs**, **243,000
one-host greedy continuations**, **448,000 tokenizer comparisons**. The 80-address
envelope contains 54 simulated/10 structural-zero/16 impossible cells (6,912
simulated datasets at N128); forecast upper bounds are 40,960 main plus 445,440
fit/validation datasets. These are counts, not empirical power or time estimates.
The 24-hour/8-GiB caps are unratified prelaunch operational criteria, not automatic
numerical-driver limits. Evidence: `planning/management-plan-reconciliation-20261004/`.

Accepted build index: `docs/superpowers/plans/2026-10-04-exp7-build.md`.
Reconciled owner decision package: `docs/superpowers/plans/2026-10-04-exp7-decisions.md`.
The recommendation is to adopt the remaining proposals for the build and authorize
task-by-task implementation plus pre-tag tokenizer/config-only validation. No
owner answer is recorded. Current authorization remains feasibility/build planning.
No production calibration/power/verdict, model/tokenizer contact or rental occurred.

Secured reviews:

- `planning/integration-v2-review-20261004/`, manifest SHA256
  `4a32ca4ceb3c026a1ae9de26c3d5f276bb4b22ccb8bfdacb532745190c3f7f33`, archive
  `81c5182e6e2c450dfe0c27dcb596acc9a0abe2837eff216e9af2c55ce604af3f`.
- `planning/integration-v2-schedule-review-20261004/`, manifest SHA256
  `ac3493379029f39f6940f1be1358abd650712ccd76cf8d1f52a1440b1b0130cc`, archive
  `2d58847a0108e1fd4bac40931086a8dc8ab3934a74d1b406b629ed1fc082fda5`.
- Management: `planning/management-integration-v2-closure-20261004/`.

## GitGuardian 37866852 — false positive; recurring cause identified

Michael reported another alert and asked how to stop receiving these. Management
recomputed all four matches at `c61706ba4` from the committed synthetic heartbeat
configuration (fixture directory, PID123, verdict stage) and verified their exact
reported patch spans. This is a non-secret identity checksum, not a credential.
Status remains TRIGGERED at read; GETs only. Incident37866209 is now independently
confirmed IGNORED / false_positive.

GitGuardian's current detector documentation explains the recurrence: our keys
`token`/`heartbeat_token` are credential-like assignment names, and every fresh
scratch root creates a new high-entropy value. Recommended prevention is a
consistent `heartbeat_identity_sha256` naming correction in a separately reviewed
source revision, preserving validation and immutable evidence; verify its new
serialization with a targeted scanner check. This recommendation is not applied
and does not authorize an instrument build. Broad hash/path exclusions would
reduce real-secret coverage; workspace exclusions are a separate alternative.
Evidence, checker and documentation links: `planning/gitguardian-20261004-2304/`.

## Heartbeat checksum naming correction — authorized

Michael answered **“apply it”** to the naming-correction recommendation above.
This authorizes a bounded, reviewed planning-source revision: use
`heartbeat_identity_sha256` for the public SHA256 identity throughout heartbeat
producers, consumers, exact schemas, tests and deployment instructions. The
digest still derives from canonical root/PID/stage. Existing archived evidence
retains its original bytes. The instrument-build decision remains unanswered.

The targeted GitGuardian stateless scan attempt returned **HTTP403**. A separate
GET of `/v1/api_tokens/self` at Oct4 23:22 UTC confirmed the configured API key is
active and has incident-read access, but **no `scan` scope**. Thus there is no
successful scanner result to claim. Sanitized access receipt and the bounded
old/new JSON-and-diff comparison helper are under
`planning/heartbeat-identity-20261004/`. No incident disposition or detection
policy was changed. A scan-enabled key is needed to finish live scanner validation.

Michael subsequently supplied `~/gitguardian-token2.txt`. After restricting it
to0600, the targeted stateless comparison passed at23:32 UTC: **eight old-name
controls detected, eight renamed counterparts with zero findings**. The value
is the same public checksum in each paired comparison. The initial16 documents
are in-memory synthetic records in JSON and added-file-diff form; the API marks
both forms `is_diff:false`. Exact revised-code output remains a separate check.
Receipt: `planning/heartbeat-identity-20261004/synthetic-scan.json`. No credential
value or raw API response was recorded.

## Heartbeat naming correction CLOSED — accepted integration-v3

**Ruling I6 — apply the authorized checksum naming amendment.** Michael's
“apply it” is implemented in a separately archived, scoped-reviewed integration-v3.
Exactly nine installable files change: five heartbeat modules, two original test
files and two generated local slices. The public identity is consistently
`heartbeat_identity_sha256` in config, claim, mailbox, status, terminal observer
and remote deployment configuration. Legacy-only and mixed fields refuse; there
is no fallback. Digest derivation remains SHA256 of canonical root/PID/stage.
Parent/start identity, PID, source pins, monotone sequence, freshness, single
writer and terminal acknowledgement remain active. The OS service validates the
renamed schema before its spawn port. Why: remove the misleading credential-like
assignment name that caused repeated synthetic false positives. Cost: future
consumers must use the revised field; immutable historical records retain theirs.

V3 retains all **271 installable files, 73 module tasks / 75 total tasks**, unchanged
registry/order/ownership/closures and all348 prior method identities; seven new
schema regressions bring the literal registry to355. All93 local slice AST origins
were checked. Core/statistics/provider code and scientific decisions are unchanged.
Its compact source archive has352 manifested files; reconstructed installed/prefix
duplicates are omitted, with their exact inventories retained. Source:
`docs/superpowers/plans/2026-10-04-exp7-annex/integration-v3/`, manifest SHA256
`9f01c46c361f24171b1c1979858807ad297855c91f06664b321475a470e81e7b`;
source-map SHA256 `045de3d9fd83c9a79941fc95b196c50dac85400dd1a5e2c9f95b5dfaf0ae8281`.

Independent scoped review is **CLEAN**, reproducing30 guarded contract methods
and five expected RED→GREEN prefixes. Management verified all127 review bindings,
all129 archive members and the exact installable diff, then independently
reproduced the same30 methods and five prefixes. All source bytes remained bound;
all1,206 v2 bindings remain unchanged. Historical author/reviewer bookkeeping
failures are retained. The old failed full348 run is still failed, with reconciled
passing evidence; no full355 run or all73-prefix repetition is claimed.

Live GitGuardian verification is complete using the replacement credential at
`~/gitguardian-token2.txt` (0600; scan and incident-read scopes verified). Michael
said he will delete the earlier local file; no dashboard revocation was inferred.
Three stateless successful requests scanned52 documents: **16/16 old-name controls
detected, 36/36 revised documents clean**. This includes an initial in-memory
comparison, the revised code's exact emitted config/claim/mailbox/status plus
old-name counterparts, and all20 hash-bound changed-source/specimen files.
The API treated supplied diff-shaped text as `is_diff:false`; this is literal
content-scan evidence, not a commit-scan or a universal future no-alert guarantee.
No incident disposition, exclusion or detector policy changed. No fresh legacy
runtime identity record enters either new evidence archive.

Independent review: `planning/heartbeat-v3-review-20261004/`, manifest SHA256
`0090e68f07a049bd1c9693542503532174cd4aa4227e57ab9cc1cccecf5ee8ad`, archive SHA256
`ba8bbef242d66a09cc9dc967b0985051838c6ea3de9425fe696b8fe5ee7d4e78`.
Management/source/scanner evidence: `planning/heartbeat-identity-20261004/`.
Build index and decision register now select accepted v3. The pending owner
build/scientific-proposal decision is unaffected. No model/tokenizer contact,
rental, production numerical driver or completed analysis was executed.

## Instrument build APPROVED — 2026-10-05

Michael answered **“approved”** to the explicit request: “adopting the reviewed
implementation choices and authorizing the module-by-module build, with tests,
independent reviews, and pre-tag tokenizer/config validation.”

This adopts B1–B15 and B17–B19 plus the statistical implementation choices in
`docs/superpowers/plans/2026-10-04-exp7-decisions.md` as the build specification.
B16 remains withdrawn. The authorized source is integration-v3, manifest
`9f01c46c361f24171b1c1979858807ad297855c91f06664b321475a470e81e7b`, source map
`045de3d9fd83c9a79941fc95b196c50dac85400dd1a5e2c9f95b5dfaf0ae8281`.
Execute its exact **75 tasks: B0 launcher plumbing, 73 single-primary module
tasks, final integrated dispatch**, in order, with a fresh implementer and
reviewer per task, failing local test before primary installation, meaningful
scoped verification, commit/push per task and recorded findings/rulings.

Pre-tag tokenizer/config-only asset measurement and oracle-answer cap validation
are included in this approval. The future Pythia fp32 digest procedure is adopted
for implementation, not executed now. Bounded synthetic throughput/memory-check
execution still needs its specific scope authorized before full simulation
stages. Weight loads, predictor/outcome collection, rentals, freeze ratification/
tag, the once-only verdict and propagation retain their separate recorded gates.
No Experiment 6 analyzer or completed matched-token analysis is to be rerun.

**Build state at approval:** clean master at `bbfbb34016a0ad3f2f4517df145f31f8a4bfbb9b`;
no instrument modules installed under `experiments/exp7/`. Next: **B0-LAUNCHER**.
The planning archives and completed feasibility evidence remain immutable.

## Build execution opened — 2026-10-05

Coordinator verified clean master at approval `350c4c5059efdc453f0cb07aa5eb0be72e65347a`,
the three accepted v3 hashes and absence of every installable target. Durable
tracking: `build/STATE.json`, common delegated brief `build/README.md`, per-task
`build/tasks/`. Exact source/task inventory is data-only checked by
`build/coordinate.py`; it does not install or execute instrument source.
No deviation authorized. B0 is next; each task gets distinct fresh implementer
and reviewer, committed source comparison, coordinator reproduction and closure.

### Build blocked before B0: harness delegation depth

The dedicated coordinator's first `functions.subagent` call for a fresh B0
implementer was rejected: **`Subagent depth limit reached (1). Increase
"experimental.subagent_depth" to allow nested subagents.`** No implementer session
was created, no instrument target was installed, and no test/long job launched.
Evidence: `build/tasks/B0-LAUNCHER/delegation-blocker.json`; task brief and exact
approval/spec pins are retained. All75 tasks remain uncompleted.

**Management gate:** enable delegation to depth2 for this coordinator, or have a
top-level coordinator perform the mandated fresh implementer/reviewer sequence.
Do not substitute self-implementation or automated source copying. Resume B0
from its retained brief after confirming clean master and source-map absence.
This is an execution-environment blocker, not a source/spec finding or owner
scientific decision. No source deviations or open review Minors exist.

### Delegation blocker resolved — top-level coordination

Management resumes coordination directly in the parent session
`ses_f11a0fbf9ffekAQskOrYbaRNO3`, which can launch the required fresh implementer
and reviewer sessions without nesting. No harness configuration or scientific
choice changes. The failed nested attempt remains preserved. B0 resumes from
its retained source/ownership brief; implementers record their actual start
commit for the subsequent committed-diff review. The same one-task-at-a-time
schedule and approval scope apply.

### Build task 1/75 CLOSED — B0-LAUNCHER

Fresh implementer `ses_ef63d8fb4ffeicxLX3m9PzrJyq` and reviewer `ses_ef62ada40ffe1jRazXuvTy5dPo`; review CLEAN. Source `8a2c83993d44adc7e1ac122eb3fa22eea18dd37b`; review `cb6c6d318d4c3eb0ee0ecee99db6c1bd20f4d94a`. Coordinator verified the exact committed diff and 4 installed prefix files, with 267 future targets absent. B0: four syntax/presence checks, zero executed test methods; no RED claim. Evidence: `build/tasks/B0-LAUNCHER/`. No source deviation or review finding.

### Build task 2/75 CLOSED — M-exp7core-certified-oracle

Fresh implementer `ses_ef6226fbcffeWeDx2ruSJh3RYH` and reviewer `ses_ef61897fcffeaH5w41Ij7RYFok`; review CLEAN. Source `963730517e1a389ffb2db32b66e09d137336774a`; review `1c3cc1b0cbb2f15e4ad482fcc01d5d7de50b8142`. Coordinator verified the exact committed diff and 8 installed prefix files, with 263 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-certified-oracle/`. No source deviation or review finding.

### Build task 3/75 CLOSED — M-exp7core-certified-baselines

Fresh implementer `ses_ef610428affey2mn3NCjr4Ych5` and reviewer `ses_ef606ef80ffeQkgVskpenJBWBO`; review CLEAN. Source `00ed2f249fa45a5266c6ee2809ae1dbe2314635a`; review `82c256c05abf0f4df87b43672e972c383f071941`. Coordinator verified the exact committed diff and 10 installed prefix files, with 261 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-certified-baselines/`. No source deviation or review finding.

### Build task 4/75 CLOSED — M-exp7core-certified-sources

Fresh implementer `ses_ef5ff1928ffe4uGECJ626Igwq8` and reviewer `ses_ef5f58b0affe2eE9beg5G8GLHD`; review CLEAN. Source `65554490054dbf4923f0937d3ef42e14c9d7fe60`; review `4b3bc01e240814ea4a7b0bc491924f1e8a9addb4`. Coordinator verified the exact committed diff and 12 installed prefix files, with 259 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-certified-sources/`. No source deviation or review finding.

### Build task 5/75 CLOSED — M-exp7core-certified-surfaces

Fresh implementer `ses_ef5ed5d14ffeDcCXOz6rQGxDUF` and reviewer `ses_ef5e5dd48ffewZkEFMs6DX15Gm`; review CLEAN. Source `c4dd48f0111ef6ba7458c2bfa125a9339df81f89`; review `3059dfd2c78b420428a582a68772eac6f819db95`. Coordinator verified the exact committed diff and 14 installed prefix files, with 257 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-certified-surfaces/`. No source deviation or review finding.

### Build task 6/75 CLOSED — M-exp7core-certified-audit

Fresh implementer `ses_ef5dd9f4fffe3lEvdnu2U0lSgn` and reviewer `ses_ef5d50d92ffeTvJeqLrf0gIZEN`; review CLEAN. Source `60b5d96d9c4c2828a0febd094de65e523746b2d0`; review `36ab51a4309b7ee09f59ffcf10dd52667b9a6d89`. Coordinator verified the exact committed diff and 16 installed prefix files, with 255 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-certified-audit/`. No source deviation or review finding.

### Build task 7/75 CLOSED — M-exp7ops-evidence

Fresh implementer `ses_ef5cee1edffevhbF04nPgN6SqR` and reviewer `ses_ef5c79d1effep4UIYXxzH5JV5l`; review CLEAN. Source `724200b86987f46fd1dd62921f301978c998d231`; review `3197cc0738135bf168697dd41111c476238fcdd6`. Coordinator verified the exact committed diff and 19 installed prefix files, with 252 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-evidence/`. No source deviation or review finding.

### Build task 8/75 CLOSED — M-exp7ops-cold

Fresh implementer `ses_ef5c04765ffexy3Qn2fW3m0f3v` and reviewer `ses_ef5bb0120ffe9XZ6wa99EdTZ0Z`; review ACCEPT WITH DEFERRED MINOR. Source `23cbd2ac5c884ae77ca68eb3b8cafec97a1f4e8d`; review `dc26fade974db2b0a87b601b13df2014588841ab`. Coordinator verified the exact committed diff and 21 installed prefix files, with 250 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-cold/`. No source deviation. 

**Deferred COLD-M1 (Minor):** The inherited cold_suite callback uses six default and fifteen optional task names absent from the installed registry. A direct launcher-forwarding callback refuses at operations; the actual final freeze controller uses its own registry dispatcher and does not call this helper. Ruling: Retain the exact approved literal during sequential build, and reconcile or explicitly retire this helper at final whole-branch review before using it operationally. This deferral preserves current task/source ownership; cost if left unresolved is refusal of a direct cold_suite-to-launcher integration, not a silent scientific result. Evidence: `experiments/exp7/build/tasks/M-exp7ops-cold/review.md`.

### Build task 9/75 CLOSED — M-exp7ops-operator

Fresh implementer `ses_ef5b3a78fffexpqJoquWpFez4x` and reviewer `ses_ef5ac7a27ffeTJ3PJVu7IsLoNk`; review CLEAN. Source `27742e83de24d1731e0394324e832a2e6db62e65`; review `00ce3f62b037263d2e7b13081474af9b1eea0ca7`. Coordinator verified the exact committed diff and 23 installed prefix files, with 248 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-operator/`. No source deviation. No review finding.

### Build task 10/75 CLOSED — M-exp7core-contract

Fresh implementer `ses_ef5a75484ffebbK6cAqJTXJowZ` and reviewer `ses_ef5a0ff10ffeIRCjk027k9N3lF`; review CLEAN. Source `ee6512c791fefff9b305dbfdba13c66f09e29849`; review `ccb9048df8f13487ddf0be90dded94d436c5217d`. Coordinator verified the exact committed diff and 25 installed prefix files, with 246 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-contract/`. No source deviation. No review finding.

### Build task 11/75 CLOSED — M-exp7stats-common

Fresh implementer `ses_ef59adee2ffeGfdKOYmwnJDKG5` and reviewer `ses_ef59388f2ffeyxnWZl85nRC323`; review CLEAN. Source `958be690bf0e9a940dba55938f4d8bef793fd835`; review `1131e63f0b7ff0232ff74a267be972de6ad677b0`. Coordinator verified the exact committed diff and 28 installed prefix files, with 243 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-common/`. No source deviation. No review finding.

### Build task 12/75 CLOSED — M-exp7core-scoring

Fresh implementer `ses_ef58dac65ffeancF6LyAPAAGxr` and reviewer `ses_ef588067cffeXzjDTzrsHIviGj`; review CLEAN. Source `7e984486b292527cb48e60d12cda4b927d361847`; review `2ffaf713ad87515504407ebe554f59fb64416d5f`. Coordinator verified the exact committed diff and 30 installed prefix files, with 241 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-scoring/`. No source deviation. No review finding.

### Build task 13/75 CLOSED — M-exp7core-inference

Fresh implementer `ses_ef58214bcffeGO7MYPjc4XNeuk` and reviewer `ses_ef57bc774ffeIgYj6dao3nLt62`; review CLEAN. Source `908b48f13374de50c703e2f13397183082c015aa`; review `66583fc3b40f9965ea38fd5251993614e58ec7c7`. Coordinator verified the exact committed diff and 32 installed prefix files, with 239 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-inference/`. No source deviation. No review finding.

### Build task 14/75 CLOSED — M-exp7core-simulations

Fresh implementer `ses_ef576607dffe76eexBeyvxwRg3` and reviewer `ses_ef5702fe5ffenUyHYsl9jkBXee`; review CLEAN. Source `6071e24fa00b9b2b1da77eb059340b4314c9c77a`; review `82ff6ca97a4fdefed02dabb9a0fd2263c128081f`. Coordinator verified the exact committed diff and 34 installed prefix files, with 237 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-simulations/`. No source deviation. No review finding.

### Build task 15/75 CLOSED — M-exp7core-strata

Fresh implementer `ses_ef56a4f08ffeHhJHFpBIvmT6qJ` and reviewer `ses_ef5650162ffeFML1Dq5200dz3a`; review CLEAN. Source `e658e564d2e88f38df72441c68794559860ee61f`; review `da89843b09b331c995328b8f3a697c8155e4bae6`. Coordinator verified the exact committed diff and 36 installed prefix files, with 235 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-strata/`. No source deviation. No review finding.

### Build task 16/75 CLOSED — M-exp7stats-data

Fresh implementer `ses_ef55f97aeffeI8JzbZ84mkcqCo` and reviewer `ses_ef558a365ffe8hvvaxwvAL0fEe`; review CLEAN. Source `ce30cac6cf09e2bd9e51db76e9a7b6bca4bd2b14`; review `d89ede03b1edcd76264b8d64a34b64b195ef204d`. Coordinator verified the exact committed diff and 38 installed prefix files, with 233 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-data/`. No source deviation. No review finding.

### Build task 17/75 CLOSED — M-exp7core-resampling

Fresh implementer `ses_ef552edb6ffenQAd8PLZ1CrEUf` and reviewer `ses_ef54ddee7ffe5pKxk5HDRwhaTj`; review CLEAN. Source `721bc8f5416f348db07620e5bcf0ab176331cb7f`; review `2c180dbc8d913eaa4fb3e1644d08854bb458b81b`. Coordinator verified the exact committed diff and 40 installed prefix files, with 231 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-resampling/`. No source deviation. No review finding.

**Ruling KERNELS-E1:** the kernels task's GREEN passed, but its evidence helper
incorrectly required no refused imports. NumPy's optional `ctypes` attempt was
hard-refused; no forbidden module loaded. Correct only the helper's postcondition
for that documented attempt, preserve the original failed assertion and reconcile
the saved pass without rerunning it. Source/guard bytes stay exact. Independent
review verified this disposition; evidence: `build/tasks/M-exp7stats-kernels/COORDINATOR-RULING.md`.

### Build task 18/75 CLOSED — M-exp7stats-kernels

Fresh implementer `ses_ef548eff5ffewg5mP4PkvpLkqD` and reviewer `ses_ef53cf27dffeuhBvVPs0Ei36hm`; review CLEAN. Source `7640e7dfeda8115433252ddd4aa2d1e34c58a802`; review `4f8897072c509357854ee38c83ab74dd46654fcd`. Coordinator verified the exact committed diff and 42 installed prefix files, with 229 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-kernels/`. No source deviation. No review finding.

### Build task 19/75 CLOSED — M-exp7stats-saved_math

Fresh implementer `ses_ef534b8dfffeTu6IAvpx3E2dC7` and reviewer `ses_ef52e5c9effeOqWis6t6mTQWz1`; review CLEAN. Source `c568ed4079d1b070b3d638f49d39c4d3f4f54f12`; review `cbf7e610e98215ef7246b4d43f80df3be2dfdc06`. Coordinator verified the exact committed diff and 44 installed prefix files, with 227 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-saved_math/`. No source deviation. No review finding.

### Build task 20/75 CLOSED — M-exp7stats-envelope_math

Fresh implementer `ses_ef5285e67ffeghLsEUyYUXQtzS` and reviewer `ses_ef52295ceffeL7Rx0u2k9f3yhs`; review CLEAN. Source `af9c191d16920e211a42659abf75d3a7453e6245`; review `b467eb61905d624348e0c5d1ff7d05af26fd3962`. Coordinator verified the exact committed diff and 46 installed prefix files, with 225 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-envelope_math/`. No source deviation. No review finding.

### Build task 21/75 CLOSED — M-exp7stats-calibration

Fresh implementer `ses_ef51b6df4ffeWlIxRI5ASP75Pi` and reviewer `ses_ef511e107ffeO03FczXk4IpZLv`; review CLEAN. Source `3877e1feb8054cb4d58dd38e95b3b7ac6b4b8ec6`; review `83a8c3eac5278dad11f586d26c31851258c175bc`. Coordinator verified the exact committed diff and 48 installed prefix files, with 223 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-calibration/`. No source deviation. No review finding.

### Build task 22/75 CLOSED — M-exp7core-worlds

Fresh implementer `ses_ef50b2b47ffe2YcmBPr3KxHoST` and reviewer `ses_ef50490dbffe5AHtVtO4X4c0Z9`; review CLEAN. Source `b68e081c743ae26c5cc1944e0442c081adda9e20`; review `537cd563b7c23ca66141d65e6ecfb61cdbd6597b`. Coordinator verified the exact committed diff and 50 installed prefix files, with 221 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-worlds/`. No source deviation. No review finding.

### Build task 23/75 CLOSED — M-exp7core-guardio

Fresh implementer `ses_ef4fcfcaaffe6j8OEWDbPnW1HU` and reviewer `ses_ef4f45745ffe0q67Rk5eUz0M60`; review CLEAN. Source `535448113a740dc5634ed04fd1644b09b4e3b291`; review `9b0a6151edc3c2f5c2e45be0f58786d42e3c74cf`. Coordinator verified the exact committed diff and 52 installed prefix files, with 219 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-guardio/`. No source deviation. No review finding.

### Build task 24/75 CLOSED — M-exp7ops-runtime

Fresh implementer `ses_ef4eccf5cffe9oPpBKDjsqiyM7` and reviewer `ses_ef4e63e7effeDpKwiBYjbMErMY`; review CLEAN. Source `1b8418f557df544518370387ee7421a56b12b6fc`; review `f1611682f57c538fc8e4144b92cf589d77f5616a`. Coordinator verified the exact committed diff and 54 installed prefix files, with 217 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-runtime/`. No source deviation. No review finding.

### Build task 25/75 CLOSED — M-exp7integration-launch

Fresh implementer `ses_ef4dd44e9ffeMCtU07XlgQoysJ` and reviewer `ses_ef4d68674ffeFfAJJ00nJ3gD2g`; review CLEAN. Source `101cb1d0a6b32b28feae6cffaf0248d6381f0b7a`; review `c653c025d6db16ba9d3560791b061aabbc771fe9`. Coordinator verified the exact committed diff and 57 installed prefix files, with 214 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-launch/`. No source deviation. No review finding.

### Build task 26/75 CLOSED — M-exp7ops-scans

Fresh implementer `ses_ef4cfdeb7ffeJIclkLs51HuqvN` and reviewer `ses_ef4c9e0abffets2Wy93WvSLiEu`; review CLEAN. Source `a63f17b7a6d1e2ad0f14cd94f8e5b9b72f7eb38f`; review `3d2b8d54227fc2ffceeca25ff1d5ae875e359340`. Coordinator verified the exact committed diff and 59 installed prefix files, with 212 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-scans/`. No source deviation. No review finding.

### Build task 27/75 CLOSED — M-exp7ops-heartbeat

Fresh implementer `ses_ef4c40eafffe9ymAEj3Mkzj0uY` and reviewer `ses_ef4bd78eeffel3jm6yUPc5niOt`; review CLEAN. Source `5da8ad6925428b303cb3c2ccfc66cc695404bc89`; review `2ac04aba85eb34624d5fadb3459af0b4c81fd583`. Coordinator verified the exact committed diff and 61 installed prefix files, with 210 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-heartbeat/`. No source deviation. No review finding.

### Build task 28/75 CLOSED — M-exp7stats-bootstrap

Fresh implementer `ses_ef4b7aec2ffeVBen8hdcW89O0j` and reviewer `ses_ef4b10cb9ffeefKyy8h5XisQcA`; review CLEAN. Source `6abcb23115582fd80b211b65a8a00bed4980c07a`; review `a7fdd606b20d3af3dfd523244e22252a81c0553b`. Coordinator verified the exact committed diff and 63 installed prefix files, with 208 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-bootstrap/`. No source deviation. No review finding.

### Build task 29/75 CLOSED — M-exp7stats-secondaries

Fresh implementer `ses_ef4a9c6e9ffeN3PpykdxJpPUte` and reviewer `ses_ef4a19240ffe2lJJYADbnTH75v`; review CLEAN. Source `cd29012d183efa7c65364dd33c865c7438b5717b`; review `eff45d2bf344932cd52a54f814d0f6f506bb95b9`. Coordinator verified the exact committed diff and 65 installed prefix files, with 206 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-secondaries/`. No source deviation. No review finding.

### Task 30 review — WORLDS-1 repair authorized, WORLDS-2 deferred

Independent review `7bf09395590f67b5fa86c5112f09deb178d27a43` found a Major
exact-rational serialization defect at both world-harness checksum sites, and a
Minor stale phase-accounting rule in the older operations helper. Management
reproduced both with fake reports and zero scientific calculations.
Ruling: use the existing exact statistical serializer at the report digest,
with a failing-then-passing bounded regression; current owner repairs only its
primary/test, and the next owner repairs the final harness before closure.
Why/cost/precise scope: `build/tasks/M-exp7ops-worlds/COORDINATOR-RULING.md`.
Original v3 bytes/evidence remain immutable. WORLDS-2 stays explicitly deferred
for final reconciliation or retirement of the older helper. Task30 remains open.

### Build task 30/75 CLOSED — M-exp7ops-worlds

Original implementer/reviewer resumed for WORLDS-1: repaired source `682280e8939ca33b305a8f2675348e397f131f52`, scoped review `af55e86b8c830d190fa2d79bccc3a7ecedb5e0a2`. Coordinator reproduced 2 passing methods, exact diff and 67-file prefix: 65 literal v3 files plus 2 reviewed amendment bindings; 204 future targets absent. Both original missing-primary RED and regression Fraction RED are preserved. `build/AMENDMENTS.json` binds exact replacement bytes and deferred import/test closure; no archive or registry change.

**WORLDS-1 operations site closed; final harness site is mandatory in task31.** **WORLDS-2 deferred** for final reconciliation or retirement of the older helper. Evidence: `build/tasks/M-exp7ops-worlds/`. Not a global CLEAN claim.

### Build task 31/75 CLOSED — M-exp7integration-world_harness

Fresh implementer `ses_ef4719580ffeCnP34vzFCv24IO` and reviewer `ses_ef464f06dffe8k13QQXfpqNx1W`; review ACCEPT REVIEWED AMENDMENT. Source `44196d5d3d57bc02fdb452b41e4b385a4bba9257`; review `bb65cb28b582d894db9641aa1035fa5ba88fd224`. Coordinator verified the exact committed diff and 69 installed prefix files, with 202 future targets absent. Expected missing-primary RED, then 3 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-world_harness/`. Reviewed source amendment: WORLDS-1-integration. No review finding.

### Build task 32/75 CLOSED — M-exp7ops-wire

Fresh implementer `ses_ef457895cffeUDXHeS0vmgldW6` and reviewer `ses_ef44ebafdffevi3Co9pXioZK7q`; review CLEAN. Source `0bf8e84b9afa2f69c261e13c10ee73a21ffb7eb3`; review `3bb70af373318cca12fd3d75b1b234855cfaf31f`. Coordinator verified the exact committed diff and 72 installed prefix files, with 199 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-wire/`. No source deviation. No review finding.

### Build task 33/75 CLOSED — M-exp7ops-watcher

Fresh implementer `ses_ef4490249ffeh9S43ZyEGcPiat` and reviewer `ses_ef4417e21ffewxVVdrpWX8rmaE`; review CLEAN. Source `130f970d1a140662cb7629f0b742f0db44464a75`; review `4f7ff2ae1bbf0d7193044f8024f4d1ef8610ae84`. Coordinator verified the exact committed diff and 74 installed prefix files, with 197 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-watcher/`. No source deviation. No review finding.

### Build task 34/75 CLOSED — M-exp7ops-mutation

Fresh implementer `ses_ef43d00f9ffeQi3kGNegLETcFP` and reviewer `ses_ef436d494ffeafRA7fAtiWl5Wm`; review CLEAN. Source `a5bf0cf5842d1e8e4d9d88542c0b6ecfe470edf2`; review `815158ea6c23f8e7ff117c720435e1382d18bb31`. Coordinator verified the exact committed diff and 77 installed prefix files, with 194 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-mutation/`. No source deviation. No review finding.

### Build task 35/75 CLOSED — M-exp7integration-mutation_specs

Fresh implementer `ses_ef4318071ffeKGikyRPT3Li47p` and reviewer `ses_ef42bee19ffeDkcGw9vxNxkWp3`; review CLEAN. Source `098b11f9306b3da6b5aac0f2ce594bcab26fab04`; review `0b4a9653d8eb504f01adfe4531212d417abb629b`. Coordinator verified the exact committed diff and 79 installed prefix files, with 192 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-mutation_specs/`. No source deviation. No review finding.

### Build task 36/75 CLOSED — M-exp7integration-freeze

Fresh implementer `ses_ef4257a7effeerbDRZC1vccEr4` and reviewer `ses_ef41fcd45ffe1NGwcIKpC1mOCD`; review CLEAN. Source `a168887c1f4acbcf44b6da6d2be648208ee98d03`; review `a8e4fb15fee5f3938788c30683c688b66518394d`. Coordinator verified the exact committed diff and 81 installed prefix files, with 190 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-freeze/`. No source deviation. No review finding.

### Build task 37/75 CLOSED — M-exp7core-records

Fresh implementer `ses_ef41a8ac4ffeAKc1sCzTITuzZ1` and reviewer `ses_ef4146a23ffe2e7CnDfJJyPukP`; review CLEAN. Source `0c989c48bed8741affdb95ee0c3cedbc66ba4260`; review `6ca9518461608089216bd165d526075b773d7917`. Coordinator verified the exact committed diff and 83 installed prefix files, with 188 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-records/`. No source deviation. No review finding.

### Build task 38/75 CLOSED — M-exp7core-anchors

Fresh implementer `ses_ef40e16f5ffenFoA9hH8PCNiEr` and reviewer `ses_ef4086d23ffehCkkwzWmVATy6i`; review CLEAN. Source `420b88c7bb06872db3ff6a454d83506384ea93e0`; review `5e14895932ce60fc50f666d1016f8922a83386c6`. Coordinator verified the exact committed diff and 85 installed prefix files, with 186 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-anchors/`. No source deviation. No review finding.

### Build task 39/75 CLOSED — M-exp7core-battery_adapter

Fresh implementer `ses_ef40237caffeQxV1BOtw57IQYJ` and reviewer `ses_ef3fa6a41ffezjETEM9M94MQjU`; review CLEAN. Source `b1a8cf63e559e11b84c7944c51e56fae749acb05`; review `ee041666d429c5dbe2a5d08604479c620931ec21`. Coordinator verified the exact committed diff and 103 installed prefix files, with 168 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-battery_adapter/`. No source deviation. No review finding.

### Build task 40/75 CLOSED — M-exp7core-referents

Fresh implementer `ses_ef3f44c50ffeIGvrol7HyKsRaq` and reviewer `ses_ef3eeef4cffeykDBvKBJTCCcmw`; review CLEAN. Source `8a03cd587ebb08797d5609446d5abf065aaf115c`; review `1bcae0a13b305c37d2c01c8e7255c339dd7eff09`. Coordinator verified the exact committed diff and 105 installed prefix files, with 166 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-referents/`. No source deviation. No review finding.

### Task41 review — INVENTORY-1/2 repairs authorized

Review `25199d145c42fd745c2e2e8185ef6fd9a377fa02` found two Major boundary
gaps: empty repository outcome markers were accepted, and descriptor-relative
transient mutations were attributed to CWD and escaped the latch. Management
reproduced both with miniature fake records, including clean/absolute controls.
Ruling: apply the existing absent-outcome policy to the repository root and
conservatively latch unattributed relative/descriptor mutations while active.
Only this primary/test may change, with genuine regression RED then GREEN and
scoped re-review. Why/cost/controls are in
`build/tasks/M-exp7integration-inventory/COORDINATOR-RULING.md`. Task41 stays open.

### Build task 41/75 CLOSED — M-exp7integration-inventory

Fresh implementer `ses_ef3ea9e1bffesLhBcFQDOVgNRm` and reviewer `ses_ef3e5108affeJ72r7XXlkTZQBd`; review ACCEPT REVIEWED AMENDMENT. Source `ab5258c7c4493eead0a7da841acadce23fb08acd`; review `ffd094c9a98b9f7fda0c01897029aae9ecdadd83`. Coordinator verified the exact committed diff and 107 installed prefix files, with 164 future targets absent. Expected missing-primary RED, then 8 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-inventory/`. Reviewed source amendment: INVENTORY-1-2. No review finding.

### Build task 42/75 CLOSED — M-exp7stats-power

Fresh implementer `ses_ef3cccf37ffekrAw6mR1duOsD2` and reviewer `ses_ef3c545b7ffe756ThkQBlF9Uqj`; review CLEAN. Source `94522b5db54dae08f3bbffed5a2b95cfbed06013`; review `9b86db6340b7fdda71c92c049e7caa1cbfdb7829`. Coordinator verified the exact committed diff and 109 installed prefix files, with 162 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-power/`. No source deviation. No review finding.

### Task43 review — PROVENANCE-1 engineering amendment authorized

Review `ded8b08a16142d4672185e2b1ce19c05ef99de32` identified a circular Git
grant binding: the immutable grant includes the hash of the commit required to
contain that very body. Management reproduced four refusals/eight controls on
captured genuine Git bytes. Ruling: v2 grant bodies omit their containing commit;
the independently pinned external trust entry supplies it. Blob/ancestry and
owner/stage/once-only gates remain mandatory. Task43 repairs its own primary/test;
preflight and later fixture owners carry explicit follow-through obligations.
Exact schema/owner assignments, why and cost:
`build/tasks/M-exp7core-provenance/COORDINATOR-RULING.md`. Task43 remains open.

### Build task 43/75 CLOSED — M-exp7core-provenance

Fresh implementer `ses_ef3bf619dffeGjZi2JFKS45iDS` and reviewer `ses_ef3b83ff9ffe52YzCc1BbD71uN`; review ACCEPT REVIEWED AMENDMENT. Source `a6b73e7c8318e8fa88bf0d6a55b3c68e5ddec995`; review `ca5dca8cd83237fb7a7552a6bdacaf6de3b26104`. Coordinator verified the exact committed diff and 111 installed prefix files, with 160 future targets absent. Expected missing-primary RED, then 10 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-provenance/`. Reviewed source amendment: PROVENANCE-1-core. No review finding.

### Build task 44/75 CLOSED — M-exp7core-baseline

Fresh implementer `ses_ef3950486ffeLizpbBSshsa0Fy` and reviewer `ses_ef38ef3ccffeKBqHkeWT0DKsgX`; review CLEAN. Source `97c59b3d6de6aa3716f379eb07b551d60f448688`; review `08be4a39a7c0e4d8cc71c6ab9367c135ef2a10e1`. Coordinator verified the exact committed diff and 113 installed prefix files, with 158 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-baseline/`. No source deviation. No review finding.

### Build task 45/75 CLOSED — M-exp7core-collection_schema

Fresh implementer `ses_ef38874aeffesFZhzIxk0839PT` and reviewer `ses_ef381fa95ffedrDnz6dVJz6P7o`; review CLEAN. Source `84216fd4c95c1cc693d0fdcb251687bc7da52c46`; review `256d9c43cd58c8e24cc182e2967ce49aa14ae660`. Coordinator verified the exact committed diff and 115 installed prefix files, with 156 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-collection_schema/`. No source deviation. No review finding.

### Build task 46/75 CLOSED — M-exp7core-live

Fresh implementer `ses_ef37b4f80fferMLTo28VKkPV8G` and reviewer `ses_ef3746663ffeVi4aiGiJsQ0T1s`; review CLEAN. Source `d0690c59bc7d7ec3d873b0ea0af31d25fcc70a86`; review `d738464d918ea2cea63a6c3ffd72a370f1ec712f`. Coordinator verified the exact committed diff and 117 installed prefix files, with 154 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-live/`. No source deviation. No review finding.

### Build task 47/75 CLOSED — M-exp7core-preflight

Fresh implementer `ses_ef36e64adffeOak0Isy45NCRae` and reviewer `ses_ef3621009ffeoCH14pWaEar8RJ`; review ACCEPT REVIEWED AMENDMENT. Source `3ef1bb23ed68d0cb2f7bd570d61cfd5f44a9fd8a`; review `6935553889e743c7e73c3159d179090723981cd7`. Coordinator verified the exact committed diff and 119 installed prefix files, with 152 future targets absent. Expected missing-primary RED, then 9 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-preflight/`. Reviewed source amendment: PROVENANCE-1-preflight. No review finding.

### Build task 48/75 CLOSED — M-exp7core-bridge

Fresh implementer `ses_ef35b058cffeQ2LzSjbFeuerAQ` and reviewer `ses_ef355336dffer4gK2daSXFv5II`; review CLEAN. Source `6e7304ddbcbe4f51d8c5a5a63bf32ca1a2124c26`; review `3e539827a428aae70a949117dce1be93abaa99e7`. Coordinator verified the exact committed diff and 122 installed prefix files, with 149 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-bridge/`. No source deviation. No review finding.

### Build task 49/75 CLOSED — M-exp7stats-read_boundary

Fresh implementer `ses_ef34fe228ffeh3WnD18S9a36kU` and reviewer `ses_ef349402cffeQlU7jAlNG3t7Do`; review CLEAN. Source `05415709f76d85d43d642226ba4c49a5ed56a6e5`; review `a20731f8480dae06494b2f7a7d46b6bcbb0e3d9b`. Coordinator verified the exact committed diff and 124 installed prefix files, with 147 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-read_boundary/`. No source deviation. No review finding.

### Build task 50/75 CLOSED — M-exp7stats-candidate_audit

Fresh implementer `ses_ef342d7cfffeY1MpbMJTLctqkb` and reviewer `ses_ef33c7edbffe1CMf4oQyOvs6EY`; review CLEAN. Source `ea3a5c75cc238e899219abc2daa72ab50119e01f`; review `b8d4234b2aee214eee30639387a9e6488679a609`. Coordinator verified the exact committed diff and 126 installed prefix files, with 145 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-candidate_audit/`. No source deviation. No review finding.

### Build task 51/75 CLOSED — M-exp7integration-candidate_runtime

Fresh implementer `ses_ef33666dbffemZh202lEw73fnm` and reviewer `ses_ef32e2854ffevZoNOJlIOxlVKf`; review CLEAN. Source `017621b682e3a87901de68f6e5679756bd3bc0f1`; review `111dc4e9cc3041f2059b0e211dfcfcbc08bc8d6f`. Coordinator verified the exact committed diff and 128 installed prefix files, with 143 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-candidate_runtime/`. No source deviation. No review finding.

### Build task 52/75 CLOSED — M-exp7integration-provider

Fresh implementer `ses_ef327ea46ffejeeBsMF2j0RXv4` and reviewer `ses_ef321c8f2ffeFQG9vwuVACH7xW`; review CLEAN. Source `cfcac472847dd20f750195f72a07ffe6f951b01c`; review `1dcd920feab2719699904511d8e8f48f06ae1b60`. Coordinator verified the exact committed diff and 131 installed prefix files, with 140 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-provider/`. No source deviation. No review finding.

### Build task 53/75 CLOSED — M-exp7core-campaign

Fresh implementer `ses_ef31a996afferXPENvmbbFGn30` and reviewer `ses_ef313b058ffeqtk4GTst6DomTu`; review CLEAN. Source `e1354f3baae784fc0e08b84c460e6b4140f3cebb`; review `311fce63df3a597bd64b16ea4bfb18fe79924339`. Coordinator verified the exact committed diff and 133 installed prefix files, with 138 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-campaign/`. No source deviation. No review finding.

### Build task 54/75 CLOSED — M-exp7core-entrypoints

Fresh implementer `ses_ef30c6134fferzXcFAsFQed2o9` and reviewer `ses_ef3063e4fffeSAfnOPdddZDmVX`; review CLEAN. Source `88c46786b6b094623a1344b8a7cc8f9fefc652bf`; review `2981e28c9d72ed10fa7eefe215f938952f417db4`. Coordinator verified the exact committed diff and 135 installed prefix files, with 136 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7core-entrypoints/`. No source deviation. No review finding.

### Build task 55/75 CLOSED — M-exp7ops-secured

Fresh implementer `ses_ef3009b98ffeEp4gSVJbgqo7gd` and reviewer `ses_ef2fb13f9ffewBvuKCWGNfcxdB`; review CLEAN. Source `ccb86e79c49ede03d6308b7c43c787b547bc311e`; review `5534fc6e748ac04099dc7aa18aa825d3918ee2e1`. Coordinator verified the exact committed diff and 137 installed prefix files, with 134 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-secured/`. No source deviation. No review finding.

### Build task 56/75 CLOSED — M-exp7ops-dispatch

Fresh implementer `ses_ef2f5b2efffeob3PfskAwuSmZ4` and reviewer `ses_ef2f04c77ffehXkXyItUL1mRAC`; review CLEAN. Source `3cc9fb2a54e6d7092b0c7bc22d66905e8d8b8784`; review `99c9908180825d6497944786d915ff8292ac9990`. Coordinator verified the exact committed diff and 140 installed prefix files, with 131 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7ops-dispatch/`. No source deviation. No review finding.

### Build task 57/75 CLOSED — M-exp7integration-supervisor

Fresh implementer `ses_ef2eb10f2ffevrbn6BMU3oclrk` and reviewer `ses_ef2e58bb9ffeknxx89kEeXJdfc`; review CLEAN. Source `75cba4c8da98a195a26dee04267c9ca79e6735a1`; review `4ba89f285945318bc0c3f5afef9eae68ccf3ed9f`. Coordinator verified the exact committed diff and 142 installed prefix files, with 129 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-supervisor/`. No source deviation. No review finding.

### Build task 58/75 CLOSED — M-exp7integration-remote_evidence

Fresh implementer `ses_ef2df003cffeNgWko6YgUJISYe` and reviewer `ses_ef2d8f533ffeTo7q4CmWOEMyYN`; review CLEAN. Source `80537dee7f9d22d93ee25f1d7dad693b910e43e9`; review `67cae1226f5812c3850e24543c3f7d5c281d19a7`. Coordinator verified the exact committed diff and 144 installed prefix files, with 127 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-remote_evidence/`. No source deviation. No review finding.

### Build task 59/75 CLOSED — M-exp7integration-heartbeat_service

Fresh implementer `ses_ef2d38056ffecWypQvYxDuzTO0` and reviewer `ses_ef2cd448bffecYiQJAsKMSwmK0`; review CLEAN. Source `1f2f3f7ccc82d1e75b0d6d214d7ee4ad3e5a90bf`; review `576338ea92d687662afd8c25c8f74fb92a9cc534`. Coordinator verified the exact committed diff and 147 installed prefix files, with 124 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-heartbeat_service/`. No source deviation. No review finding.

**Ruling SECURITY-E1:** task60 GREEN passed but its evidence helper expected an
unused `exp7core.strata` import from the conservative static closure. Management
and review inspected the fixture and verified every observed import is allowed
and installed. Preserve the failed helper, reconcile the saved pass without a
rerun, and change no production/test/registry bytes. Why/cost and evidence:
`build/tasks/M-exp7integration-security/COORDINATOR-RULING.md`.

### Build task 60/75 CLOSED — M-exp7integration-security

Fresh implementer `ses_ef2c7d997ffejLSDOv09kmKewx` and reviewer `ses_ef2bfa856ffeQXRyN0kSeQm9Ay`; review CLEAN. Source `393ae3eb1b9204925227a31e353de733e6bb2cd5`; review `7052a97290f45c4c39ccb15143b075e59fb762ba`. Coordinator verified the exact committed diff and 150 installed prefix files, with 121 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7integration-security/`. No source deviation. No review finding.

### Build task 61/75 CLOSED — M-exp7stats-calibration_context

Fresh implementer `ses_ef2b99f8dffexLgQdvC6YaVPRF` and reviewer `ses_ef2b439bfffe6uVTGI1gboNp3u`; review CLEAN. Source `12d45ad6c3d32dda6942d486987883b0bdc256da`; review `9144c197e39ed3c9769bc68ba3794707465b602e`. Coordinator verified the exact committed diff and 155 installed prefix files, with 116 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-calibration_context/`. No source deviation. No review finding.

### Build task 62/75 CLOSED — M-exp7stats-calibration_cli

Fresh implementer `ses_ef2ae57d4fferdDXjZmKewHTzm` and reviewer `ses_ef2a9d7a7ffeTQX1R8JsAR95o5`; review CLEAN. Source `759ce5fedbb103f9b16f0fbae600c3b253600587`; review `8a67facfd88e71da5d96f21e4c2038389bd04966`. Coordinator verified the exact committed diff and 157 installed prefix files, with 114 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-calibration_cli/`. No source deviation. No review finding.

### Build task 63/75 CLOSED — M-exp7stats-analyzer

Fresh implementer `ses_ef2a54059ffeveQoR2BHnzZcPr` and reviewer `ses_ef29f9cc8ffeTiA0FZuMNJuztD`; review CLEAN. Source `67de184063d23fd5228002a8d62e3bdd69a47593`; review `f9e30b378a5138564d2e1e931050ebaee61bc059`. Coordinator verified the exact committed diff and 160 installed prefix files, with 111 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-analyzer/`. No source deviation. No review finding.

### Build task 64/75 CLOSED — M-exp7stats-power_validation

Fresh implementer `ses_ef29abc44ffeJE7QVXWaZ29ffM` and reviewer `ses_ef295848affeOmyVdGu2rFk9Wk`; review CLEAN. Source `1bb19e2646f6666734b7a64aab0d0e073887d9a8`; review `780996ca89d918b4f569b18c0af1cd98e7d4e954`. Coordinator verified the exact committed diff and 163 installed prefix files, with 108 future targets absent. Expected missing-primary RED, then 1 GREEN method(s), independently reproduced. Evidence: `build/tasks/M-exp7stats-power_validation/`. No source deviation. No review finding.
