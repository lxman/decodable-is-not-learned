# Exp 3b — Retrospective (2026-08-15)

Closed same day it was frozen, DISSOCIATION, all gates clean, no
attrition, no amendment, the one pre-committed change unspent. The
three-session design | build | freeze protocol plus a campaign and a
single analysis run — the first experiment in the program whose every
phase executed exactly as preregistered.

## What the numbers say

The claim was adjudicated on four cells, and all four came back on the
same side. Where the probe reads the answer's first character at
basis-starved margins .6263/.7725 (rev_string7) and .5731/.6749
(reverse_string), the same weights on the same prompt emit that
character at .052/.028 and .032/.026 — at or below the .056/.054
marginal floors, behavioural margin negative in every cell. The
comparison this time is unit-fair and scale-fair by construction, so
the standing objection to the 2c datum is spent: matching the units did
NOT surface hidden emission. UNITS_ARTIFACT was live, preregistered,
and would have forced a correction to the methods paper; it did not
happen.

The sharpest single fact: emission is lowest exactly where the probe
margin is highest. 1b carries the battery's strongest probe signals
(.7725/.6749) and its weakest emission (.0280/.0260). If the probe were
reading something the output path partially uses, scale should pull the
two together; instead they moved apart.

The mechanism sentence in the projection — copy bias dominates the
first emitted character — is consistent with the data: observed
reversal first-char rates (.026–.052) bracket the measured copy_first
rates (~.038–.040), i.e. the model's first character behaves like an
echo of the input's first character, not like a read of the input's
last. Consistent, not proven: no per-item echo analysis was
preregistered, and none was run. If anyone wants it, the raw
continuations for all 40 cells are committed and it is a two-line
descriptive on existing data.

clock24_d999 earned its place: .372/.374 against a .496 floor with a
0.0 probe margin. BELOW-floor behaviour on the matched control is
itself informative — the model does not even track the modal-hour
statistic — and the quadrant shows what agreement (absent/absent) looks
like on the same instrument that just showed disagreement
(present/absent) one row up.

## The projection, graded

Ledgered at 56e5d0e before any cell ran; every campaign-visible number
(full-string) was referent-predicted, so the projection stayed blind
through collection by construction.

| projected | happened |
|---|---|
| Gates all clean | all clean |
| Gate 2 replicates to the exact count, not merely CP-overlap | exact: 480, 490, 18, 24 of 500; all zeros zero |
| Gate 3 zero byte diffs, tolerance unused | 0 diffs in 24/24 cells — including reverse_string/6.9b's lone 1/500 full-string hit, reproduced |
| Gate 4 quiet, contamination empty | empty; twins .000–.046, all non-significant |
| DISSOCIATION, weight .55 | DISSOCIATION |
| Reversal point estimates .03–.06 | .026–.052 (4/4 inside or under) |
| ctrl_copy ~.97/.985 | .9940/.9940 — slightly above the projected band |
| clock24 ~.50–.56 "marginal-tracking" | **.372/.374 — MISS.** Below floor, not tracking the marginal |
| Eval-size reversal "also at floor" | .038–.078; 12b at .078 (CP hi .105) is elevated but under nominal criticals — graded a weak hit |
| Named miss route: rev_string7/1b clears alone | did not occur, and the direction was wrong: 1b is the LOWEST cell, not the first to clear |
| Disconfirmer: any reversal cell ≥ .12 | never fired |

Two real misses inside a correct verdict, both worth keeping: the
clock24 first-character rate was projected as marginal-tracking and
came in .12 below the marginal — the model's hour-answer first digits
are anti-modal, which nobody predicted; and the PARTIAL hedge assumed
probe margin orders emission onset, when the data ordered them
oppositely. The projection habit is doing its job: a verdict-level hit
with named component misses is more informative than either alone.

## Process notes

- **The OOM was operational, not epistemic.** The single-process driver
  ratcheted to 34 GB (MPS allocator caches freed weights per process)
  and the machine OOM'd at cell 15/40. Recovery used only frozen
  surface: the driver's own preregistered `--only-mode/--only-size`
  flags, one process per (mode, size) tier, identical committed order;
  write-once cell records meant zero data loss; skip-if-exists made the
  restarts free. Disclosed in the ledger before the analysis ran. For
  3c or any future multi-size ladder: either per-tier processes from
  the start, or `torch.mps.empty_cache()` between loads — decided at
  design time, not mid-campaign.
- **Gate 3 is the cheapest strong gate the program has found**: 12,000
  continuations compared byte-for-byte against a sibling experiment's
  record, zero tolerance spent, and it certifies stack determinism
  end-to-end. Reuse the pattern wherever a predecessor collected
  overlapping cells.
- **The freeze session's two new verifications both mattered in
  hindsight**: gate 2's process-identity check is what licenses reading
  the exact-count replication as determinism rather than luck, and the
  probe_label[0]==answer[0] sweep is what makes the marginal floor THE
  chance rate of the scored quantity, with no gap for a scorer/floor
  mismatch to hide in.
- One wart, disclosed at close: the campaign-log commit message cites
  "exp2c precedent" for force-adding the log past `.gitignore`, but
  exp2c's logs are untracked — wrong justification, right decision (the
  ledger cites the log's per-cell lines; provenance belongs in the
  record).

## What this does and does not license

It licenses: "on Pythia-410m/1b, character-reversal's first character
is linearly decodable at .57–.77 basis-starved margins from the same
residual streams that emit it at floor under greedy decoding, and the
instrument demonstrably detects emission when it exists." The methods
paper's §8 claim upgrades from a scale-and-units-confounded contrast to
a same-weights, same-units dissociation (edit drafted, Michael's
approval pending).

It does not license: anything about sampling (Experiment 3's question —
is the information elicitable from the output distribution at all? —
is now the natural next test, with these committed continuations as its
greedy baseline); anything above 1b (the eval-size descriptives are
suggestive of nothing, by design); anything beyond Pythia; any claim
that emission is exactly zero (blind region [floor, .092), every rate
with its CP bound).
