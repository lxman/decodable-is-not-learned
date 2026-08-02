# Experiment 2c: exact family-block permutation power table

Design Sec 5 preregistered fallback (adopted by ruling 2026-08-01): exact enumeration over same-size family-block permutations, replacing the rho_family-calibrated naive test. Alpha is bounded by construction (<= .01, not calibrated); power still depends on rho_family as a nuisance parameter of the simulated data -- swept below for robustness, not calibration fragility.

Family sizes: [4, 3, 2, 2, 1, 2, 1, 4, 2, 1, 2, 1, 1]
n_perms=28800, resolution=3.47222e-05
n_sims=5000

## Power at rho_family=0.5

| rho_true | alpha | power |
|---|---|---|
| 0.0 | 0.0106 | 0.0078 |
| 0.5 | 0.0106 | 0.2664 |
| 0.6 | 0.0106 | 0.4156 |
| 0.7 | 0.0106 | 0.6164 |
| 0.8 | 0.0106 | 0.8146 |

## Power robustness sweep (rho_true=0.6, rho_family varies)

| rho_family | alpha | power |
|---|---|---|
| 0.3 | 0.0110 | 0.4236 |
| 0.5 | 0.0106 | 0.4156 |
| 0.7 | 0.0094 | 0.4158 |
