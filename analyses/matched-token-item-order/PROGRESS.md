# Matched-token size-ladder item-order analysis — ledger

## 2026-10-24: authorization and pre-analysis plan

Michael selected **Option 1** ("Let's carry out option 1"): an existing-data
analysis on the committed Pythia matched-token ladder (`analyses/matched-token/`,
`experiments/exp5/results/units/`) testing whether the committed 1B/410M
sampled output tails (`Pythia-1B` $k=256$ and $k=64$, `Pythia-410M` $k=256$ and
$k=64$, and cross-family `OLMo-2 1B` $k=64$) forecast which individual items
resolve across the larger Pythia parameter sizes (`1.4b, 2.8b, 6.9b, 12b`) at
fixed training tokens.

**Pre-analysis reads, disclosed:** `analyses/matched-token/{PLAN.md,INTERPRETATION.md,PROGRESS.md,analyze.py,results/REPORT.md}`
and the `step143000` rows of `analyses/matched-token/results/counts.csv`;
`experiments/exp2g/{stats_2g.py,strata_2g.py}`, `experiments/exp2i/analyze_2i.py`,
and `experiments/exp2k/{analyze_2k.py,battery_2k.py}`. From `counts.csv`, the
11 rungs of `strata_2g.PREDICTOR_RUNGS` (`R_CAP`'s 9 rungs plus `count_div13`
and `median5`) are the exact 11 rungs that clear `2d`'s binomial reference bar
at `step143000` on at least one of `{1.4b, 2.8b, 6.9b, 12b}`. Zero size-axis
item-order concordances ($D$ or $T$) have been computed.

**Ruling S1:** Keep `analyses/matched-token/` untouched (`CLAUDE.md`: "never
rerun this analysis/bootstrap") and place the size-axis item-order analysis in
`analyses/matched-token-item-order/` with the same write-once, Git-blob-bound,
synthetic-tested, saved-output-verified discipline.

**Ruling S2:** Exclude `410m` and `1b` from every outcome vector $y_i$
(`OUTCOME_SIZES = ("1.4b", "2.8b", "6.9b", "12b")`) so predictor and outcome
never share a model size, and also include a greedy-zero restriction
(`410m=0 ∧ 1b=0` at `step143000`) plus the `2.8b`-excluded three-size ladder
(`1.4b, 6.9b, 12b`) and each individual larger size (`1.4b`, `2.8b`, `6.9b`,
`12b`) so neither 1B greedy overlap nor 2.8B's arithmetic peak can masquerade
as a general parameter-ladder effect.

## 2026-10-24: analyzer, synthetic tests, and `--validate-only` check

Implemented `analyze.py`, `test_analyze.py`, and `verify_outputs.py` (committed at `dc119e5d5`):
- `pytest -q analyses/matched-token-item-order/test_analyze.py`: 5 passed in 0.09s.
- `python analyses/matched-token-item-order/analyze.py --validate-only`: verified 7,592 files against `5154f8935dc79e478b0853cbe39a39d931f00177` (`exp7-closed`), re-derived all $60 \times 34 \times 500 = 1{,}020{,}000$ Exp 5 bits and cross-checked every unit's correct count against `analyses/matched-token/results/counts.csv`, and verified all predictor streams (`exp2d`, `exp2k`, `exp2i`, `exp2g`, `exp2j`) without computing any size-axis concordance or writing to `results/`.

## 2026-10-24: single production run and saved-output audit complete

- Executed `python analyses/matched-token-item-order/analyze.py` once (`2026-10-25T02:29:50.710393+00:00`, exit 0).
- Executed `python analyses/matched-token-item-order/verify_outputs.py` (`{'verified_outputs': 6, 'per_rung_rows': 643, 'curve_rows': 60, 'all34_rows': 34}`, exit 0).
- Output SHA-256 digests (`results/provenance.json`):
  - `summary.json`: `b3bc98b196f4aa9e0b83c9725f87748ce05d62bc3c9c9b85a43359494137e99e`
  - `per_rung.csv`: `337e8c54379b9cb067fdd0dc325e681c523a1d240b067319a5c0da957cf30180`
  - `checkpoint_curve.csv`: `cc3f9a937033de696cfecbacfbf6bdd4322617be6c43571e511be64d4c67bbef`
  - `all_rungs_143k.csv`: `1567ff3fe692e78aa6ccf9ea4ab8e5bb71a1888c501c3de03a058e4bbf735e7b`
  - `REPORT.md`: `f0855e8c08138a7bc75d1ac3f5744b8478df24e31b46b52f149836f8bb2c627c`
- Headline findings (`step143000`, `OUTCOME_SIZES = ('1.4b', '2.8b', '6.9b', '12b')`):
  - `pythia_1b_k256` on `R_CAP` (9 rungs): stratified $T = +0.218$ ($p = 0.0001$, family-boot 95% CI $[+0.107, +0.369]$).
  - `olmo2_1b_k64` on `R_CAP` (9 rungs): stratified $T = +0.278$ ($p = 0.0001$, family-boot 95% CI $[+0.130, +0.502]$, positive on 9/9 rungs).
  - `pythia_1b_k64` on `R_CAP` (9 rungs): $T = +0.165$ ($p = 0.0001$); on `R_PRED11` (11 rungs): $T = +0.153$ ($p = 0.0001$, positive on 11/11 rungs).
  - `probe_1b` on `R_CAP`: $T = +0.026$ ($p = 0.1293$); on `R_PRED11`: $T = +0.011$ ($p = 0.2740$).
  - Greedy-zero restriction (`410m = 0 & 1b = 0` at `step143000`): `pythia_1b_k256` $T = +0.194$ ($p = 0.0001$), `olmo2_1b_k64` $T = +0.270$ ($p = 0.0001$).
  - `2.8b`-excluded ladder (`1.4b, 6.9b, 12b`): `pythia_1b_k256` $T = +0.237$ ($p = 0.0001$), `olmo2_1b_k64` $T = +0.306$ ($p = 0.0001$).
  - Full 34-rung unstratified battery (`pythia_1b_k64`): mean $D = +0.286$ ($[+0.165, +0.411]$) across 29 informative rungs, $+0.280$ ($[+0.160, +0.413]$) across 24 rungs with $n_{\text{pos}} \ge 20$.
- Wrote `INTERPRETATION.md`. Analysis complete; do not rerun.
