# Tier-2 fleet plan — growth battery (staged 2026-08-02, dispatch pending tier-1)

Staged on Michael's instruction while the tier-1 screens finish. This
document is the dispatch checklist and the provenance ledger's source
for per-candidate box assignments (promise made in the 2026-07-30
llmbox staging entry). **Nothing here launches until every candidate's
tier-1 verdict is on disk; the launch set is exactly the tier-1
passers.**

## Workload

Tier-2 = 10 full-config fits per candidate (5 seeds × both sizes ×
2,500 perms); these fits ARE the campaign's untrained-gate fits
(known_absent), written by `run/screen.py::_write_campaign_fit`.
Original 14-candidate campaign: ~100 min/fit under 6-way Mac
contention, 2.2 days wall. Cost model from that campaign: fit cost
scales with n_probe × label-class count.

Growth candidates and cost units (n_probe/1000 × k):

| candidate | n_probe | k | units | tier-1 status at staging |
|---|---|---|---|---|
| odd6 | 8000 | 6 | 48 | screening |
| hamming12 | 4000 | 8 | 32 | **PASS** |
| base13 | 2000 | 13 | 26 | screening |
| hamming8 | 4000 | 6 | 24 | **PASS** |
| quad_next | 2000 | 7 | 14 | **PASS** |
| median7 | 2000 | 7 | 14 | **PASS** |
| antonym6 | 2000 | 6 | 12 | screening |
| median5 | 2000 | 5 | 10 | **PASS** (2 tolerated fits) |
| arith_next | 1000 | 7 | 7 | **PASS** |

## Box assignments (ledger these verbatim at dispatch)

Every candidate gets its own worker (9 candidates ≤ 14 worker slots).
Heavy candidates go to llmbox — it is otherwise idle, while the Mac
carries interactive work; rebalance at dispatch if any candidate
ejects at tier-1.

- **llmbox (x86, 12 threads, 4 workers):** odd6, hamming12, base13,
  hamming8 — 130 units.
- **Mac mini (6-way precedent, 5 workers):** quad_next, median7,
  antonym6, median5, arith_next — 57 units.

Cross-architecture caveat (already on the record, 2026-07-30): x86 vs
ARM BLAS can differ in final-ulp float results; the 2b fleet accepted
this; per-fit provenance is attributable via the `host` field
`_write_campaign_fit` records.

## Dispatch checklist

1. Tier-1 verdicts on disk for all 9; launch set = passers only.
2. Mac → llmbox sync (documented git-bundle path, no GitHub creds on
   the box):
   - `git bundle create /tmp/exp2c-update.bundle <llmbox-HEAD>..master`
   - scp bundle; on llmbox: `git pull /path/to/bundle master` and
     verify HEAD == Mac HEAD.
   - scp the assigned candidates' npz pairs to
     `~/emergence-paper/experiments/exp2c/results/activations/{410m,1b}_untrained/`
     (hamming8/hamming12 shipped at staging; odd6/base13 npz exist
     only after their tier-1 collection).
   - Smoke: `~/emergence-lab-venv/bin/python -c "import instrument"`
     from experiments/exp2c, then one screen_arrays synthetic fit.
3. Launch per box, one worker per candidate:
   `cd experiments/exp2c && nohup ./run/tier2_worker.sh <candidate> &`
   (Mac: 5 workers; llmbox: 4 workers via ssh.)
4. Ledger the dispatch (boxes, HEADs, npz shas if shipped) in
   PROGRESS.md.
5. Return path (one source of truth = the Mac): scp llmbox's
   `results/screen/tier2/*.json` and `results/probes/known_absent/*`
   back to the Mac; verify fit counts (10/candidate); commit on the
   Mac only.
6. After all verdicts: binomial fire-count bookkeeping vs the
   preregistered 0.0064/fit rate (the 2026-08-01 pattern), family_map
   pin update, recertification power table (5000-sim) against the
   0.75 gate — the certification the growth ruling requires.

## Standing constraints

- Activations are collected ON THE MAC ONLY (MPS provenance +
  two-stage lock); llmbox receives npz files, never loads a model.
- odd6/antonym6 npz must postdate the 2026-08-02 regeneration
  (shot-diversity rule + odd6 re-bless). No stale caches exist for
  either (never collected before regeneration); letter_sum/
  letter_prod caches are dead rungs, never ship them.
- hamming8's cache is valid despite the shot rule (byte-identical
  regeneration, proven 2026-08-02).
