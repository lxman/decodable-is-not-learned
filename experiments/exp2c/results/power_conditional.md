# Experiment 2c: power CONDITIONAL on the realized predictor

The frozen table (`power_table_exact.md`, tag `exp2c-preregistered`) simulates predictor and outcome jointly from a continuous latent model, and was computed before the predictor existed. This table holds the predictor FIXED at the Stage 1 probe scores measured at M2 and simulates only the outcome, scoring every sim with the same frozen block-permutation machinery (`sampled_block_perms`, the add-one sampled p convention, alpha = .01).

**No eval-side quantity enters this computation.** The fixed predictor is probe-side only (410m/1b trained-twin margins); the outcome is simulated, never measured. Running this before the Stage 1 tag does not touch the two-stage lock.

## The realized predictor

- 22 of 34 rungs scored exactly zero, so they enter as one tie block under average-rank rho.
- 9 of 16 families are entirely flat. A flat family is inert under the block permutation — it contributes the same values in every row — so the realized test has 7 effective blocks, not 16.
- Tie-corrected ceiling: the largest Spearman rho any outcome can attain against this predictor is **0.8541**, not 1.0. Grid points above it are questions the battery cannot be asked.
- Family sizes: [4, 2, 2, 4, 2, 2, 1, 2, 1, 1, 2, 4, 2, 2, 1, 2]
- n_sims=5000, alpha=0.01

## Power at rho_family=0.5

| rho_true | conditional power | frozen (marginal) | delta |
|---|---|---|---|
| 0.0 | 0.0124 | 0.0076 | +0.0048 |
| 0.5 | 0.3460 | 0.5416 | -0.1956 |
| 0.6 | 0.5604 | 0.769 | -0.2086 |
| 0.7 | 0.8234 | 0.9266 | -0.1032 |
| 0.8 | 0.9926 | 0.9894 | +0.0032 |

## Robustness sweep (rho_true=0.6, rho_family varies)

| rho_family | conditional power | frozen (marginal) | delta |
|---|---|---|---|
| 0.3 | 0.6084 | 0.78 | -0.1716 |
| 0.5 | 0.5604 | 0.769 | -0.2086 |
| 0.7 | 0.5258 | 0.7406 | -0.2148 |

## Validity: realized type I error

The tie structure must not inflate alpha. A single null row at n_sims=5000 has SE ~= .0014, too coarse to judge, so this is pooled across seeds:

- alpha_hat = **0.01050** over n=24000 (target 0.01)
- 95% CI [0.00921, 0.01179], z = +0.76
- per seed [0, 1, 2, 3]: 0.0122, 0.0092, 0.0088, 0.0118

Not a significant excursion: alpha is controlled at the nominal level with the realized predictor.

## Reading this

The row to compare is rho_true=0.6, where the frozen table reports 0.7690. Two mechanisms run in opposite directions and the table is their net: the tie block removes information (costing power), while it also narrows the permutation null (gaining it). The loss dominates in the mid range and washes out at rho_true=0.8, which sits close to the 0.8541 ceiling where only near-maximal arrangements are possible at all.
