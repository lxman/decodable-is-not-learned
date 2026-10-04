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

### Validation-only attempt 1 and import-label correction

Code/tests/build ledger committed and pushed at `c9bd0f2fa`. Command
`/Users/michaeljordan/emergence-lab/.venv/bin/python analyses/matched-token/analyze.py --validate-only`
refused (exit 2): `binding: _ops.py absent from
6deb2d55fd170cf76cae325ff41e4c750b2b775f`. No results directory, comparison or
bootstrap was produced. This is the first actual-source validation invocation,
not a production analysis invocation (production count remains **zero**).

**Build finding B5 (closed):** PyTorch's dynamic `torch.ops` namespaces carry
synthetic relative `__file__` labels such as `_ops.py`. The import audit had
mistakenly anchored that label at the repository working directory. A focused
synthetic regression failed first, then the audit was changed to use actual
absolute file/spec origins; synthetic labels with no file origin are not
repository source. The before-execution import finder still binds every actual
repository module, and entry/exit checks retain absolute source paths.
The same full pytest command now reports **26 passed in 2.00 s**. This correction
changes validation-path handling only; the fixed analysis rules are unchanged.

### Validation-only attempt 2: complete

At launch HEAD `e74b6de984c1f89bbd6324d2f02921736c9ea08f` (committed and pushed),
the same `analyze.py --validate-only` command exited **0** and printed only:

```json
{"state": "validated", "units": 60, "rung_records": 2040, "rederived_bits": 1020000, "bound_source_files": 2309, "bound_launch_files": 4}
```

All selected units passed the frozen contracts and additional cross-links;
every bit was rescored. Entry/exit source bindings passed for 2,309 files
(2,257 payload files and 52 imported repository source files); the three new
Python files and PLAN matched launch HEAD. The analysis directory has no
`results/` directory. Actual-source validation tally: **two invocations, one
explicit import-label refusal and one complete validation**. Production
comparison/bootstrap tally: **zero**. Final code is at `e74b6de98` (initial
build `c9bd0f2fa`); ready for independent review. Management owns the single
production invocation and subsequent `verify_outputs.py` saved-output audit.

## Independent review and launch readiness — 2026-10-04

Fresh reviewer inspected the scoped committed diff and actual source at
`e74b6de98`, reproduced **26 tests passing in 2.09 s**, and found no blocking
correctness or plan-compliance defects. Management independently read the
instrument/checker and reproduced **26 passing in 2.03 s**. Checked family
weights and shared draws, all-size transition/nesting arithmetic, measured
parameter slopes, tie handling, exact input coverage, source bindings and
continuation rescoring, write-once refusal and saved-output audit.

**Ruling R1:** accept the nonblocking test-coverage residual — integration
fixtures use three sizes, and miniature checker fixtures bypass its default
production provenance branch. The six-size 64-bin path and default branch
were inspected; the post-run checker will exercise them on the saved full
shape without rerunning statistics. Cost: a production-only checker defect
could require an explicitly recorded audit fix; it cannot authorize another
analysis/bootstrap run. No unaddressed numerical defect was identified.

The owner's descriptive-run approval remains the execution authority. One
detached invocation is prepared with a durable monitor, status/log capture,
and the independent saved-output checker. Before launch the production tally
is still **zero**. No predecessor analyzer will be invoked.

## Production complete and checked — 2026-10-04

**One production invocation**, launch `b770e8ebd83f94db0be6748046e37224bdde82ec`:
16:36:35.718–16:36:39.826 UTC (about 4.11 seconds), exit 0. Detached operator
PID/SID 46545; watchdog `matched-token-20261004` registered before release.
The independent saved-output checker then exited 0 at 16:36:40. Its default
full-shape branch verified all 64-bin histograms and production coverage,
closing R1's operational concern without rerunning analysis or bootstrap.
Management inspected the outputs and acknowledged the watchdog. Completion
arrived through the shell callback; no independent launchd-delivery claim is
made for this short run.

All fixed outputs complete: count 2,040; accuracy 60; contrast 150; transition
5,100; texture 340; time-average 30 rows. Source/launch bindings rechecked
independently against both live bytes and Git trees at 16:37:56 UTC:
2,309 source files, four launch files, eight output hashes. Summary SHA256
`1f385bb8ad606ebd9139555ba0cc8d523b0bd3b5590514e38a3dd6db4ee0ec17`.
Evidence copied byte-for-byte from the approved scratch operator directory
to `operations/`; post-run binding receipt is recorded there too.

**Result:** late aggregate advantage, nonmonotonic size order. Final 12B−410M
is +4.158824 pp, family-resampling CI [1.561286, 8.233500]; equal-family
+4.337500 [1.562422, 8.318906]. Final means in size order:
6.4353/6.7706/6.0529/11.3824/9.6471/10.5941%. Widest final pair has
1,319 gains and 612 losses; 3,695/4,564 ever-correct items have an adjacent
size-axis loss; only 8/34 count trajectories are nondecreasing. The complete
fixed tables and bounded interpretation are in `results/REPORT.md` and
`INTERPRETATION.md`. No PASS/FAIL or parameter-only causal claim.

The analysis is complete. Production tally **one**, subsequent analysis or
bootstrap reruns **zero**. No new model contact/rental or essay/public-release
propagation occurred. Experiment 7's separately reviewed design awaits dials.

**Ruling R2 (publication formatting):** the default staged whitespace check
flags the CSV writer's standard CRLF record endings and the generated report's
final blank line. Preserve the write-once, hashed result bytes. The final
publication check uses per-command `core.whitespace=cr-at-eol,-blank-at-eof`
for these generated files; prose/code retain the normal check. No persistent
Git setting, analyzer edit, output rewrite or recomputation is involved.
