# Experiment 2c — Progress Ledger

Design: ../experiment-2c-design.md (ACCEPTED 2026-07-28, freeze
pre-authorized). This ledger records every number, ejection, and
adjudication of the M0 build. Entries are append-only.

## 2026-07-28: Open item 4 closed; order-stats bounds committed

**Mechanism:** Per-fire classification for gate 2 (shuffled labels) uses
quantiles of max-of-2500 null draws. Tolerated = floor fire AND within
central 99%, i.e., z ≤ z₀.₉₉₅. Elevated = floor fire AND z₀.₉₉₅ < z ≤
z₁₋₁₀⁻⁴ (counts toward binomial, never structural abort). Structural
abort = z > z₁₋₁₀⁻⁴.

**Exact bounds (via `experiments/exp2c/stats_bounds.py`):**
- z₀.₀₀₅ = 2.86 (lower tolerance bound; never used for abort)
- z₀.₉₉₅ = 4.61 (upper tolerance bound)
- z₁₋₁₀⁻⁴ = 5.37 (structural abort threshold)

**Worked example:** 2b's two shuffled fires at 3.6 and 4.7 null-SD
classify as tolerated and elevated respectively — count test applies,
no structural abort, matching gate-review ruling (b).
