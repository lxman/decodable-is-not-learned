# Exp 2g — Projection (sealed BEFORE any intermediate checkpoint is loaded)

Written 2026-08-23 after stage 1 (the sealed predictor is a known input;
no checkpoint quantity exists anywhere). Graded in the retrospective.

**Verdict: FORECAST at 2.8b.** The trained probe carries real signal on
six of the seven primary rungs (1b eval acc vs twin: antonym .702/.296,
add_base8 .754/.096, sub_base8 .424/.146, antonym6 .324/.196, arith_next
.270/.082, sub3_mid .196/.132; add3_mid nearly silent at .126/.100) and
the power record gives .946 at D = .15.

Per-line, for grading:
- p_strat < .001; **T in [.12, .28]**, point guess ≈ .18.
- Twin stratified p > .3 (no SURFACE).
- Raw T > stratified T (structural difficulty carries shared variance),
  but stratified stays significant — not DIFFICULTY-ONLY.
- Per-rung c_r: largest on add_base8 and antonym (strong probe, mid
  n_pos); **add3_mid ≈ 0** (the probe is nearly silent there); arith_next
  positive ≈ .1–.3; sub3_mid small-positive.
- **Named disconfirmer: T lands in [.05, .10)** — item-level signal real
  but under the effect bar → NO-FORECAST "detected below the effect bar".
  Mechanism if it fires: the concordance lives in the option rungs'
  position strata where the label prior is already removed, leaving less
  than the rung-level accuracies suggest.
- 410m replication: same terminal as 2.8b (probe accs comparable).
- 12b: FORECAST over R_12B, sub4_mid THIN; count_div13's probe (.402) and
  median5's (.406) give it two rungs 2.8b's primary lacks.
- Gate 1: PASS — counts exact vs m4, 2c-path and 2g-path digests equal,
  0 continuation diffs.
- s*(rung) guesses (descriptive): antonym earliest (≤ 20k), antonym6 and
  median5-at-12b mid (30–80k), the base-8 and arithmetic rungs late
  (≥ 80k); at least one rung shows a transient clear on the grid.
- Sweep mechanics: zero halts, zero attrition; per-checkpoint wall ≈ the
  m4-derived 24 min ± batching noise.
