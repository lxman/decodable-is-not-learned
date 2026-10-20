# Pre-Tag Synthetic Calibration Report (`calibration-001`)

**Date:** `2026-10-20`
**Candidate Commit:** `501853e36e4937f0ec8f2307a81b2d3990b0333d`
**Candidate Manifest (`calibration-candidate.json`):** `10a6389533c549443d1862fad7566d012777134aa2a86c9ca8008db1b778bbee`
**Runtime Authority (`calibration-runtime.json`):** `16718b298ca146366b2475235ef106bc1659ec7acdad77f8c2b3fb1ededc64fa`
**Synthetic Spec (`synthetic-cases.json`):** `21667d68e26ad0b2d8e329969c2c7d3eb9cccbb0f27ec268f88f69388210d773`
**Stage Terminal Marker:** `REFUSED.json` (`d1d27d5dee32944c4da854704765ed0bd1af37e4634335da93d2a7dbe40a9fa4`)
**Stage State:** `CALIBRATION-FAILED`

---

## 1. Execution & Boundary Integrity

- **Command:** `/Users/michaeljordan/emergence-lab/.venv/bin/python -I -B -X pycache_prefix=/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp7-calibration-001/pycache -X int_max_str_digits=5000 /Users/michaeljordan/emergence-paper/experiments/exp7/calibration/run_calibration_cli.py --root /private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode/exp7-calibration-001/root --repo /Users/michaeljordan/emergence-paper/experiments/exp7 --candidate-commit 501853e36e4937f0ec8f2307a81b2d3990b0333d --manifest calibration/authority/calibration-candidate.json --manifest-sha256 10a6389533c549443d1862fad7566d012777134aa2a86c9ca8008db1b778bbee`
- **Elapsed Wall Time:** `110,833.05s` (`30.787 hours`) under full `CandidateAudit` (`sys.setprofile`) + `ReadBoundary` + `CalibrationContext.entryexit`
- **Child User / System CPU Time:** `109,989.21s` user / `607.27s` sys
- **Peak Aggregate RSS (`ps` 5s polling across 22,116 samples):** `171,704,320` B (`163.7 MiB`, child peak `158,810,112` B / `151.5 MiB` `<< 8 GiB`)
- **Stderr / Boundary Violations:** `0` bytes on `stderr`; `0` `CandidateAudit` or `ReadBoundary` violations; entry and exit candidate manifest checks passed.
- **Output Artifacts:**
  - `CLAIM.json`: `72` B, SHA256 `99bdcd855bae89ee8817b53a6b959f4f16303ea5fca55738498ea073f548896d`
  - `REFUSED.json`: `177` B, SHA256 `d1d27d5dee32944c4da854704765ed0bd1af37e4634335da93d2a7dbe40a9fa4`
  - `calibration.json`: `71,717,111` B, SHA256 `368c559a6ae76ae7f2dc76add6dc42d4f8ed62b7ed5b2ccc41ed3b1f29292289`
  - `REPORT.md`: `73,157,669` B, SHA256 `22089c6427852a41d82454d66f5765273c082fb815ac1056fd4f46f1c80aead3`
- **Saved Arithmetic & Envelope Verification:**
  - All `80` selectivity envelope cells pass `verify_envelope_semantics(record["selectivity_envelope"])` with 100% exact rational equality.
  - All `N1..N9` component and union `rate_summary` records match `rate_summary(count, 2000, null_rate)` with 100% exact digest equality.

---

## 2. Null Calibration Results (`N1..N9`, `2,000` Replicates $\times$ `B = 10,000`)

| Case | Status | Joint `either_predictor_joint` (`null=0.01`) | Component (`null=0.005`) | `fires` (`/2000`) | `fires` `defect` | `p_reject` (`/2000`) | `p_reject` Rate | `p_reject` Exact Binomial Tail $p$ | `p_reject` `defect` (`< 0.01`) |
|---|---|---:|---|---:|:---:|---:|---:|---:|:---:|
| **N1** | **`DEFECT`** | `0/2000` (`p=1.0000`) | `olmo2_1b/forecast` | `0` | `False` | `12` | `0.0060` | `0.302938` | `False` |
| **N1** | **`DEFECT`** | `0/2000` (`p=1.0000`) | `olmo2_1b/selectivity` | `0` | `False` | `9` | `0.0045` | `0.667745` | `False` |
| **N1** | **`DEFECT`** | `0/2000` (`p=1.0000`) | **`pythia_1b/forecast`** | **`0`** | **`False`** | **`20`** | **`0.0100`** | **`0.003371`** | **`True`** |
| **N1** | **`DEFECT`** | `0/2000` (`p=1.0000`) | `pythia_1b/selectivity` | `0` | `False` | `7` | `0.0035` | `0.870490` | `False` |
| **N2** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `olmo2_1b/selectivity` | `0` | `False` | `8` | `0.0040` | `0.780457` | `False` |
| **N2** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `pythia_1b/selectivity` | `0` | `False` | `10` | `0.0050` | `0.542384` | `False` |
| **N3** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `olmo2_1b/selectivity` | `0` | `False` | `4` | `0.0020` | `0.989796` | `False` |
| **N3** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `pythia_1b/selectivity` | `0` | `False` | `12` | `0.0060` | `0.302938` | `False` |
| **N4** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `olmo2_1b/forecast` | `0` | `False` | `0` | `0.0000` | `1.000000` | `False` |
| **N4** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `olmo2_1b/selectivity` | `0` | `False` | `0` | `0.0000` | `1.000000` | `False` |
| **N4** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `pythia_1b/forecast` | `0` | `False` | `0` | `0.0000` | `1.000000` | `False` |
| **N4** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `pythia_1b/selectivity` | `0` | `False` | `0` | `0.0000` | `1.000000` | `False` |
| **N5** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `olmo2_1b/forecast` | `0` | `False` | `16` | `0.0080` | `0.048306` | `False` |
| **N5** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `pythia_1b/selectivity` | `0` | `False` | `11` | `0.0055` | `0.416960` | `False` |
| **N6** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `olmo2_1b/selectivity` | `0` | `False` | `14` | `0.0070` | `0.134987` | `False` |
| **N6** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `pythia_1b/forecast` | `0` | `False` | `10` | `0.0050` | `0.542384` | `False` |
| **N7** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `olmo2_1b/forecast` | `0` | `False` | `7` | `0.0035` | `0.870490` | `False` |
| **N7** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `pythia_1b/forecast` | `0` | `False` | `7` | `0.0035` | `0.870490` | `False` |
| **N8** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `olmo2_1b/forecast` | `0` | `False` | `10` | `0.0050` | `0.542384` | `False` |
| **N8** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `pythia_1b/forecast` | `0` | `False` | `5` | `0.0025` | `0.971031` | `False` |
| **N9** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `olmo2_1b/forecast` | `0` | `False` | `10` | `0.0050` | `0.542384` | `False` |
| **N9** | `NO-DETECTED-DEFECT` | `0/2000` (`p=1.0000`) | `pythia_1b/forecast` | `0` | `False` | `10` | `0.0050` | `0.542384` | `False` |

---

## 3. Diagnosis of the Single Triggered Cell (`N1` `pythia_1b/forecast` `p_reject = 20/2000`)

1. **Zero Gate Fires Across All 9 Null Cases:**
   - Every single component's full gate fire count (`fires`, requiring $p < 0.005$ plus effect threshold) is **`0 / 2000`** (`0 / 44,000` across all 22 true-null component evaluations).
   - Every single case's joint licence count (`either_predictor_joint`) is **`0 / 2000`** (`0 / 18,000` across `N1..N9`).
2. **Mathematical Proof That `N1` `pythia_1b/forecast` Has Exact Super-Uniform Null Size $\le 50/10001 < 0.005$:**
   - In `N1` (`exp7stats/calibration.py:114-136`), both `olmo2_1b` and `pythia_1b` are generated from the exact same pattern `H[0] = ((1, 1, 1/2), (1, 1, 1/2))` with `delta = 0`.
   - Because $s_0 = s_1 = 1$, every item $i \in \{0, \dots, 499\}$ has deterministic availability $u_i = 1$, so `strata[p][f]` is deterministically the 5 fixed base blocks `base-0..4` of 100 items each, and `yy[f]` is deterministically fixed.
   - Within each block `base-b`, the 100 predictor scores $(x_i)_{i \in \text{base-}b}$ are **strictly i.i.d.** and independent of `yy[f]`.
   - Therefore, the observed score vector and the $B = 10,000$ within-stratum permutations drawn in `forecast(...)` are strictly exchangeable under `N1`. By the exactness of Plus-One Monte Carlo permutation p-values ($P = (1 + n_{\text{ge}}) / (B + 1)$), the true single-replicate rejection probability for `N1` `pythia_1b/forecast` (and identically for `N1` `olmo2_1b/forecast`) satisfies:
     $$\Pr\left(P < \frac{1}{200}\right) = \Pr(n_{\text{ge}} \le 49) \le \frac{50}{10001} = 0.0049995 < 0.005.$$
   - `N1` `olmo2_1b/forecast` and `N1` `pythia_1b/forecast` have **the exact same mathematical distribution**, differing only in the string `"olmo2_1b"` vs `"pythia_1b"` in the `PCG64DXSM` seed tuple `("calibration", "N1", replicate, p, f)`. `olmo2_1b/forecast` drew `12 / 2000` (`0.0060`, $p = 0.3029$), while `pythia_1b/forecast` drew `20 / 2000` (`0.0100`, $p = 0.003371$).
3. **Why One Series Crossed $k \ge 19$ (`p < 0.01`):**
   - Across `N1..N9`, `calibration.py` evaluates **17 independent non-degenerate true-null `p_reject` series** (`9` independent forecast series and `8` independent selectivity series; `N4` is constant-score $0$ and `N7` shares scores/outcomes across predictors).
   - Each series is tested individually against an **unadjusted** one-sided $\text{Binomial}(2000, 0.005)$ threshold `excess < 0.01` ($k \ge 19$, per-series false-alarm probability $0.006954$).
   - Under an exact uniform null ($p = 0.005$), the familywise probability that **at least one** of 17 independent series draws $k \ge 19$ by pure Monte Carlo chance is:
     $$1 - (1 - 0.006954)^{17} = 11.19\% \quad (\text{and } 5.58\% \text{ for } k \ge 20).$$
   - Pooled across all non-degenerate true-null replicates in `calibration-001`, the empirical `p_reject` rates are:
     - All 9 independent true-null `forecast` series (`18,000` replicates): **`100 / 18,000 = 0.005556`** (nominal `0.005000`, binomial tail $p = 0.1578$).
     - All 8 independent true-null `selectivity` series (`16,000` replicates): **`75 / 16,000 = 0.004688`** (nominal `0.005000`, binomial tail $p = 0.7289$).
     - All 17 independent true-null series combined (`34,000` replicates): **`175 / 34,000 = 0.005147`** (nominal `0.005000`, binomial tail $p = 0.3582$).
   - Furthermore, re-evaluating the 20 `N1` `pythia_1b/forecast` hits at $B = 100,000$ permutations shows that 4 boundary hits (`replicates 68, 321, 823, 1746` with $T \in [0.0672, 0.0686]$ and $n_{\text{ge}} \in \{41, 47, 48\}$ at $B = 10,000$) have underlying permutation $p \in [0.00516, 0.00605] > 0.005$, leaving `16 / 2000` (`0.0080`, binomial tail $p = 0.0483 \ge 0.01$).
4. **Selectivity Power Envelope (`80` Cells at `128` Replicates):**
   - `10` `ANALYTIC-ZERO-SUPPORT` cells (`E0`), `16` `UNSUPPORTED` cells (`E3` and `E7` at $\delta > 0$), and `54` `SIMULATED` cells.
   - At $\delta = 0$ (`14` `SIMULATED` null cells across `E1..E7`), `fires` is `0 / 128` in all 14 cells (`0 / 1,792` total), and `p_only` is `7 / 1,792 = 0.00391` (nominal `0.00500`).
   - At $\delta = 1/10$ (`E4, E5, E6` with availability $\ge 0.15$), `fires` is `128 / 128` (`1.000`) for both `f3` and `f4`; at $\delta = 1/5$, `fires` is `128 / 128` (`1.000`) for `E2, E4, E5, E6`.
