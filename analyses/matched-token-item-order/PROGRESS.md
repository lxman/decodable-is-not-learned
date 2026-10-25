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

Implemented `analyze.py`, `test_analyze.py`, and `verify_outputs.py`:
- `pytest -q analyses/matched-token-item-order/test_analyze.py`: 5 passed in 0.09s.
- `python analyses/matched-token-item-order/analyze.py --validate-only`: verified 7,592 files against `5154f8935dc79e478b0853cbe39a39d931f00177` (`exp7-closed`), re-derived all $60 \times 34 \times 500 = 1{,}020{,}000$ Exp 5 bits and cross-checked every unit's correct count against `analyses/matched-token/results/counts.csv`, and verified all predictor streams (`exp2d`, `exp2k`, `exp2i`, `exp2g`, `exp2j`) without computing any size-axis concordance or writing to `results/`.
