# Experiment 2c: exact family-block permutation power table

Design Sec 5 preregistered fallback (adopted by ruling 2026-08-01): exact enumeration over same-size family-block permutations, replacing the rho_family-calibrated naive test. Alpha is bounded by construction (<= .01, not calibrated); power still depends on rho_family as a nuisance parameter of the simulated data -- swept below for robustness, not calibration fragility.

Family sizes: [4, 2, 2, 4, 2, 2, 1, 2, 1, 1, 2, 4, 2, 2, 1, 2]
n_perms=100000, resolution=9.9999e-06
n_sims=5000

## Power at rho_family=0.5

| rho_true | alpha | power |
|---|---|---|
| 0.0 | 0.0088 | 0.0076 |
| 0.5 | 0.0088 | 0.5416 |
| 0.6 | 0.0088 | 0.7690 |
| 0.7 | 0.0088 | 0.9266 |
| 0.8 | 0.0088 | 0.9894 |

## Power robustness sweep (rho_true=0.6, rho_family varies)

| rho_family | alpha | power |
|---|---|---|
| 0.3 | 0.0088 | 0.7800 |
| 0.5 | 0.0088 | 0.7690 |
| 0.7 | 0.0076 | 0.7406 |
