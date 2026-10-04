# Matched-token analysis — ledger

## 2026-10-04: authorization and inventory

Michael: "Do the analysis and plan the experiment." Management interpreted
this as the existing-data matched-token analysis and a sampling-mechanism
successor design. He then explicitly selected **Descriptive analysis** in
the scope ruling: all six sizes, ten exactly shared checkpoints and all
34 rungs, fixed-before-run rules, uncertainty, no PASS/FAIL claim.

Metadata-only inventory found ten shared finite units per size, not the
earlier claimed nine. The common steps are 1k/2k/4k/5k/6k/8k/16k/32k/100k/143k.
The older loss-matching search accounts for 5k/6k; the shared-spine subset
will be printed separately. Invalid 2.8B 64k weights and unshared substitute
steps are excluded by exact matching. No comparison statistic computed.

**Ruling M1:** descriptive analysis rather than numbered confirmatory
experiment — Michael explicitly chose this scope; cost is that it earns
no preregistered hypothesis-test verdict or sealed-forecast claim.

**Ruling M2:** preserve all-rung and all-step tables, equal-rung main means,
family-cluster intervals and equal-family/type readings — prevents a flat
or arithmetic-dominated aggregate from hiding the data's structure; intervals
are conditional descriptions of this battery, not seed-level evidence.

**Ruling M3:** source snapshot `6deb2d55f`, frozen contract functions and
continuation rescoring only — pins the reused evidence without invoking any
closed analyzer. One production descriptive run after tests and review.

Plan: `PLAN.md`. The mechanism successor is being designed separately.

## 2026-10-04: build choices, before any comparison

Fresh implementation task under HANDOFF §3; production execution remains for
management after independent review. Source resolves to
`6deb2d55fd170cf76cae325ff41e4c750b2b775f`; the plan was committed at
`bad597f1e9c43c13361729db569bca747437440c`.

**Ruling B1:** time-average contrasts receive the same paired family-bootstrap
draws as per-checkpoint contrasts; average the selected checkpoints within
each family before taking percentiles. This is the conservative reading of
“macro mean paired accuracy contrasts” and preserves dependence across time.
The eight-point sensitivity removes exactly 5000 and 6000, with no substitutes.

**Ruling B2:** save the six-size binary-pattern histogram in each texture row
as an audit sufficient statistic. This adds no selected comparison: it lets
the independent saved-output checker reconstruct every marginal count, paired
transition, ever-correct denominator and any-loss union without reading source
outcomes or rerunning analysis/bootstrap. All-wrong ever-correct fractions and
constant-count Spearman associations are JSON null / empty CSV fields.

**Ruling B3:** reserve the results directory atomically before a production
attempt, refusing even an existing empty directory. A failed reserved attempt
leaves an explicit refusal receipt and cannot be silently retried over that
directory. Validation-only creates no results and prints coverage/state only.
Repository imports are byte-bound before execution and again at exit; own
three Python files and PLAN are bound to the captured launch HEAD. Build/test
fixtures use temporary synthetic trees and never invoke production analysis.

### Build implementation and synthetic verification

Implemented `analyze.py`, `test_analyze.py` and `verify_outputs.py`. The selected
loader uses every named frozen contract, rederives continuation bits, checks
within-unit collection provenance and cross-checkpoint parameter counts, and
never calls a predecessor `run()` or the broad Exp 5 unit loader. Imports are
compiled from verified source bytes (not cached bytecode). Source payloads,
imported modules and launch-bound files are checked before comparisons and at
exit. Production emits six complete CSVs, summary, report and SHA256 provenance;
the saved checker independently reconstructs counts/transitions/nesting from
histograms, verifies aggregate arithmetic and every report table row. It checks
interval bounds and faithful display without rerunning their bootstrap.

**Build finding B4 (closed before data validation):** Exp 5's producer hashes
all downloaded checkpoint files, including non-LFS shard-index JSON files;
`entry.lfs_sha256` only names LFS payloads. An initial extra equality check was
too strict. A synthetic sharded unit first reproduced the refusal, then the
check was corrected to require exact file coverage, valid SHA256s for every
file, frozen-contract LFS-value matching, and identical rung/checkpoint hash
maps. No frozen source changed and no data comparison motivated the correction.

TDD evidence: first suite invocation failed collection because `analyze.py`
did not yet exist. Final synthetic suite command:
`/Users/michaeljordan/emergence-lab/.venv/bin/python -m pytest -q analyses/matched-token/test_analyze.py`
— **25 passed in 2.06 s**. Covers fixed battery mapping, gains/losses, constant
and decreasing textures, uneven family weights, paired time-grid averaging,
validation-only isolation, write-once refusal, Git/import tampering, full
synthetic unit contracts (including coherent-hash tampering), saved-output
arithmetic tampering and report-number tampering. `git diff --check` is clean.
All statistics/bootstrap exercised by tests used miniature synthetic arrays
and explicit four-draw fixtures; no production comparison or production
bootstrap has been computed. Real validation-only is pending the committed
launch binding. Independent review and management's one production run remain.
