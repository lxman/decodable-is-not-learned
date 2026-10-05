# Statistics v3 — bounded SR1-R correction

**SR1-R is implemented and ready for narrow independent re-review.** SR2–SR5,
the original SR1 helper repair, and C-1 retain management's independent closure.
This new sibling preserves v1/v2. All scientific/statistical code and settings
are byte-identical to v2; only the candidate input boundary/CLI and its tests change.

## Exact defect and correction

`SR1-R-before.log` records **two failures, zero errors** against unchanged v2
source. Both the preopened `FileIO.read()` and `os.read(fd,...)` returned the
fabricated unpinned bytes while entry/exit accepted. The new tests use the same
expressions and complete fabricated file contents; they now refuse before entry.

The correction uses a cold boundary and verified snapshots, not inferred C-call
arguments:

1. At entry and exit, the actual `SystemReadPort` enumerates Darwin `/dev/fd`
   or Linux `/proc/self/fd`, applies `F_GETFL`, and refuses every readable inherited
   descriptor. Write-only outputs remain. Enumeration-fd EBADF is the sole skipped
   observation; other errors refuse. Existing Python workers refuse.
2. It separately inventories OS-backed readable `IOBase` streams, refusing
   preopened raw, buffered and text inputs. An absent/replaced underlying fd
   cannot authenticate stale prefetched bytes. Pure memory buffers are not
   represented as new filesystem reads.
3. During the operation, ordinary read-only `open`/`io.open`/Path reads and
   `_io.open_code` use a controlled wrapper. It preserves the reviewed source-pin
   and precise absent-cache rule, reads the actual opened regular file, checks
   descriptor/path identity before and after, and checks size and independent SHA.
   It closes that descriptor **before** releasing an in-memory snapshot. Binary,
   buffered, text, method aliases and iteration therefore consume verified bytes.
4. Readable raw-descriptor opens, inherited handles, original-open aliases,
   direct FileIO constructors, custom openers and update modes refuse. File
   mappings refuse. Ordinary write-only output opens continue to work. All
   temporary input descriptors close on both success and refusal.

This supplies a concrete answer to descriptor replacement: inherited readable
source descriptors are absent/refused, and newly loaded inputs expose no kernel
fd to replace or alias. Internal snapshot replacement is checked against actual
fstat identity and exact bytes before any data is returned. The profiler's raw
read identity refusal is defense in depth; it is **not** an argument-aware fd check.

## Integration changes — interface v4

`interface.json` is **exp7.statistics-collection-interface.v4**. The raw data,
saved-power geometry callback and saved-math version2 requirements are unchanged.
Runtime authority remains `exp7.calibration-runtime.v1`, with exactly pinned
files/frozen/generated code and no wildcard-root trust.

- Include `read_boundary.py` and its gc/fcntl/runtime dependencies in independently
  reviewed candidate/runtime closure.
- Launch calibration cold, with no inherited readable descriptors or OS-backed
  input buffers. Even pinned inherited inputs must close and reopen through the
  snapshot API. Keep stdout/stderr/output handles write-only.
- The dedicated CLI now closes both its own stdin wrapper **and kernel fd0**.
  Interpreter standard streams can have `closefd=False`; closing the wrapper
  alone is insufficient. This helper is fake-tested, not run on live stdin here.
- `CalibrationContext(..., read_port=None)` defaults to the complete actual
  platform implementation. Injected ports in `annex/tests/read_fixture.py` are
  explicitly synthetic observations, never a production claimed-empty census.
- Inputs must use the supported read-only path API. `.fileno()`, raw readable
  `os.open`, update modes such as `r+b`, and custom openers are not supported
  input routes. File publication/fsync already occurs after context exit.
- No preregistration tag, seal, projection or contact grant is newly required
  by pre-tag calibration. Management retains adapter/operations ownership.

## Guarantee boundary — explicit limit

This is a checked **CPython file-I/O contract for the source-reviewed serial
calibration program**, not an operating-system sandbox. Byte-pinned native
runtime remains trusted. Arbitrary direct native syscalls, deliberate reflective
mutation of the guard, and the provenance of already loaded non-stream Python
values are not instrumented. Alternate native filesystem APIs are outside the
permitted candidate call graph; direct fromfile/mmap refusals are not a claim to
intercept every native alias. The complete source pins and call-graph review remain
necessary. There is no unresolved conflict for the requested FileIO/os.read,
buffered/text and descriptor-alias scope under this cold-input contract. If an
arbitrary-native-code sandbox were required, this bounded repair would not claim it.

## Evidence and execution scope

- Final full suite: **72 statistics methods +48 inherited core methods pass**,
  zero failures/errors/skips. `SR1-R-full-statistics-final.log` and
  `SR1-R-full-reference.log`. Twelve new methods cover this residual.
- Scoped:10 initial boundary methods;7 preserved source/cache methods pass.
  The final suite also includes the later pinned-inherited-input and stdin-fd
  controls. No re-run of production calibration, power or arithmetic review probes.
- Full-package cold probe: `SR1-R-cold-package-receipt.json` — real27-source
  inventory, no inventory-method override; positive pinned read/import, both
  inherited-input refusals, and external-helper refusals. The OS observations
  are explicitly fake; this is not a live host census result.
- Platform logic tests call the actual census/snapshot algorithms with fake
  syscalls, covering aliases/replaced fds, fstat/path mismatch, changed bytes,
  mid-read replacement, write-only descriptors and observation errors.
  No dup2, live fd-table inspection, thread/process start, or live stdin close ran.
- `V2-V3.diff`, `V2-V3-CHANGES.json`, `ANNEX-MANIFEST.json` and
  `packaging-receipt.json` bind the complete delivery. `EXECUTIONS.md` preserves
  every invocation, including the two red-before failures and the stdin follow-up.

No repository edits/commits, subagents, model/tokenizer/network contact,
production statistics, full generation or historical analyzer execution occurred.
Earlier statistical/RNG/resource proposals remain unratified. Future authorized
tokenizer validation remains before tag.
