# Experiment 2c: MC calibration + power table

Family sizes: [4, 3, 2, 2, 1, 2, 1, 4, 2, 1, 2, 1, 1]
rho_family estimate: 0.5
n_sims=5000, n_perm=5000

## Power at rho_family estimate

| rho_true | calibrated_cutoff | alpha_at_cutoff | power |
|---|---|---|---|
| 0.0 | 0.00400 | 0.0100 | 0.0110 |
| 0.5 | 0.00400 | 0.0100 | 0.4448 |
| 0.6 | 0.00400 | 0.0100 | 0.6702 |
| 0.7 | 0.00400 | 0.0100 | 0.8798 |
| 0.8 | 0.00400 | 0.0100 | 0.9838 |

## Fragility sweep (rho_family, rho_true=0.0)

| rho_family | calibrated_cutoff |
|---|---|
| 0.3 | 0.00720 |
| 0.5 | 0.00400 |
| 0.7 | 0.00140 |

Drift ratio across sweep: 5.143
FRAGILE: True
