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

## Rulings needed from Michael before the tag

- [ ] **Survivors' M1 carry (§7 reading):** the 12 reused rungs'
  argmax-absence record carries from 2b's committed M1 ("the 2b fits
  ARE the 2c fits … none recomputed") — §7's enumerated list names
  items/tier-2/Stage-1/shuffled but not M1 explicitly. Adjudicate
  the carry (recommended: carry, consistent with §7's principle and
  identical items/models/sizes) or order a re-measure (~10 min,
  contradicts "none recomputed").
- [ ] **Tier-1 margin rule (ledgered 2026-07-30):** structurally
  vacuous at 500 perms (add-one floors .0359/.0279 > α=.01 →
  `present` never true → margin bar unreachable; reject authority
  was classify_fire alone, which worked — base12 4/4 structural).
  Keep as ledgered-unreachable belt-and-suspenders, or drop from the
  tier-1 description so the frozen record implies no gate that
  cannot fire.
- [ ] **Alpha-bound test looseness (minor, 2026-08-01 review):** the
  exact-test alpha assertion uses a loose 0.05 threshold (true ~.0097
  at the 720-perm shape; the hand-computed-p test is the real net).
  Accept as-is or tighten before the tag.
- [ ] **base12 correction framing (minor, ledgered):** one framing
  sentence conflates the tier-1-screen catch (base12) with the
  human-review catch (coprimality); body attributes correctly.
  One-line touch-up or leave as-is.

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
