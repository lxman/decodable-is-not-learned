# Experiment 4 — build ledger

## Task 1 (2026-09-10): metric_4.py

Built `experiments/exp4/metric_4.py`, the pure-numpy metric layer (no torch, no I/O; a deterministic function of activation bytes):

- `chance_4(n, k=K_4) -> float` — expected mutual-k-NN overlap between two independent rankings, `k / (n - 1)`.
- `sites_4(n_hidden) -> list[int]` — the sorted distinct layer indices of 2f's `site_family(n_hidden)` (every-3rd layer + final, `LAYER_STRIDE=3` confirmed against `SITE_COUNT_PIN_4`).
- `depth_pairs(sites_m, n_hidden_m, sites_q, n_hidden_q) -> list[int]` — for each m-site, the q-site nearest in relative depth, ties to the smaller q.
- `knn_sets(X, k=K_4) -> uint16[n, k]` — cosine k-NN, self excluded, ascending-sorted per row, ties broken by ascending index via a stable sort.
- `overlap_counts(A, B) -> uint8[n]` — per-row intersection size.
- `mutual_knn_from_sets(A, B) -> dict` — per-item overlap fraction, mean, k, n.
- `linear_cka_unbiased(X, Y) -> float` — Song et al. 2012 unbiased linear CKA (Huh et al.'s `unbiased_cka`), symmetric, rows ≥ 4.
- `planted_pair(n, d, signal, seed, d_latent=8) -> (X, Y)` float32 — one shared random projection `A`; X and Y differ only in independent noise (task-1 resolution 3).

### Invariance results (all exact / as specified)

- Self-alignment: `mutual_knn_from_sets(S, S)` gives per-item and mean == 1.0 exactly.
- k-NN sets exclude self, are sorted ascending, contain exactly `K_4` distinct indices per row.
- Orthogonal rotation of one side: exact set equality (or mean overlap > 0.99 as a fallback) — observed exact equality.
- Isotropic rescale by 4.0 (power of two, exact through fp32 and the float64 row-normalisation): exact set equality.
- Determinism: two calls on the same input produce identical uint16 arrays.
- Tie-breaking on an all-identical-row matrix: ascending index, as pinned by the test.
- CKA hand case (5-point 2-D array): self-CKA 1.0, scale invariance (×2.5) 1.0, rotation invariance 1.0, symmetry holds, value in [-1, 1] for an unrelated Y.

### Chance-band numbers (independent-features test, 100 seeds × 500 items × K_4=10)

- `chance_4(500)` = 0.02004008016032064
- observed mean over 100 seeds = 0.020352000000000002
- Clopper–Pearson band computed for the record only (not asserted, per task-1 resolution 2, since the 500,000 trials are dependent within each seed): `[0.019962398246166097, 0.020747173534658745]`
- Assertion actually used: `abs(mean - chance_4(500)) <= 3 * std(means, ddof=1) / sqrt(100)` — passed.

### Calibration fixture

`experiments/exp4/tests/fixtures/calibration_curve_4.json` — 20 signal levels `i/19` for `i` in `0..19`, curve = mean mutual-k-NN overlap over 5 seeds at `n=500, d=64, d_latent=8`. `curve[0] = 0.01896` (< 0.05), `curve[-1] = 1.0` (> 0.9), `curve[10] = 0.31904` (> `curve[0] + 0.1`), non-monotone dips bounded within 0.003 (only levels 0→1 dip, by 0.00004).

sha256: `970c6f80dec81749c1e1c9fb0581dae8190ba028e25b7263860d2a30ec3030f8`

### Tests

`experiments/exp4/tests/test_metric_4.py` — 9 tests, all pass on a second run (the calibration test writes the fixture and skips on the first run, then compares on later runs). `experiments/exp4/tests/conftest.py` registers the `slow` mark (2n's convention).
