# Experiment 2c — Freeze-review checklist (design open item 6)

Drafted 2026-08-06 after M1 close. One line per pre-freeze
adjudication, each carrying its arithmetic (design §3's standing rule:
"the number sat in the record unchecked" cannot recur by construction).
Task 14 (tag `exp2c-preregistered`) fires only when every line is
GREEN or RULED and Michael gives the explicit go.

## Adjudicated gates (arithmetic on the line)

- [x] **Gate 1 — untrained-gate fits (tier-2):** 220 fits over the 34
  scored rungs (140 original campaign + 90 growth − 10 hamming8);
  fires k=2, both median5 seed-1 tolerated (z inside the central-99%
  band; zero elevated, zero structural aborts); expected 220 × .0064
  = 1.408; binomtest two-sided p = 0.4114. CLEAN.
- [x] **Gate 4 — argmax reliability (M1, 2c's own items):** ctrl_copy
  trained 0.9600 (410m) and 0.9800 (1b), both ≥ 0.9 (n=500, seed
  20260827 items); untrained 0.0000/0.0000. PASS.
- [x] **M1 absence, new pool:** 22/23 rungs under the 2b inclusion
  bar (normalized 1b margin CP95 UB < 0.25; untrained floors 0.0000,
  so margin = trained acc); hamming8 EJECTED at UB 0.3237 (ruling
  2026-08-06, record: results/inclusion/m1_ejections.json).
- [x] **Power gate (§5):** 34-rung shape [4,4,4, 2×9, 1,1,1,1],
  sampled block permutations (group ~52M > 5e6 guard), 100,000 draws,
  5000 sims, seed 0: power 0.7690 at ρ_true = 0.6 ≥ 0.75; alpha
  0.0076–0.0088 ≤ .01 by construction. DISCLOSED: ρ_family sweep
  0.7800/0.7690/0.7406 at 0.3/0.5/0.7 — the adverse corner sits
  0.0094 under the gate value; the preregistered gate is the main
  cell at ρ_family = 0.5.
- [x] **Fixture suite (§4.5):** 129 passed against the amended
  analyze.py (block-permutation PASS branch at fixed α = .01,
  contiguity contract, enumerated/sampled routing both pinned). The
  freeze requires this suite passing — satisfied.

## Rulings — all four RULED by Michael, 2026-08-06

- [x] **Survivors' M1 carry (§7 reading): CARRY from 2b.** The 12
  reused rungs' argmax-absence record carries from 2b's committed M1
  — identical items, models, sizes; consistent with §7's "none
  recomputed" principle. Declared here as the named checklist line.
- [x] **Tier-1 margin rule: DROPPED.** The vacuous branch and its
  helper removed from run/screen.py (behaviorally identical for
  every tier-1 verdict ever produced — the bar was unreachable at
  500 perms, floors .0359/.0279 > α=.01). Reject authority is
  classify_fire alone, as it always effectively was. The frozen
  record now implies no gate that cannot fire.
- [x] **Alpha-bound test looseness: ACCEPTED as-is.** The 0.05
  threshold stays (true α ~.0097; the hand-computed-p test is the
  real correctness net). Ledgered as an accepted minor.
- [x] **base12 correction framing: touched up.** A clarifying line
  appended to the ledger (append-only): the tier-1 screen caught
  base12's CRT leak; the human review caught the coprimality slip —
  two catchers, two catches, correctly attributed in the entry body.

## On the record, not freeze-blocking

- **antonym6 eval-ambiguity (~2.5% ceiling, wave-3 I2):** remedy
  decision deferred to the M4 horizon by standing ruling (per-cue
  exclusion sets vs accepting the disclosed ceiling).
- **§7 reuse declarations (state at tag):** survivor items verbatim
  from the 2b tagged record; 2b known_absent fits satisfy their
  tier-2; 2b m3 fits are their Stage-1 margins; 2b shuffled fits
  carry for gate 2's count test; honesty clause — survivors' trained
  margins are public, the two-stage eval-side lock is what the
  hypothesis test rests on.
- **hamming8's tier-2 fits remain committed** as honest record of a
  screened candidate; they simply no longer count toward the frozen
  battery's gate-1 arithmetic (restated above at 220).

## Tag contents (2b pattern: acceptance → freeze commit)

design doc (frozen verbatim) + battery/ (34-rung item files,
m1_ejections.json, screen/tier1+tier2 verdicts) + analyze.py +
tests/ (fixture suite, 129) + results/power_table_exact.{json,md} +
results/inclusion/ (M1 record) + this checklist with every box
resolved.
