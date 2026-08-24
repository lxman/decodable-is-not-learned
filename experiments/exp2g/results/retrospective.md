# Exp 2g — Retrospective

## The projection, graded

Sealed at `dfdaf79` after stage 1 (the sealed predictor a known input; no
checkpoint quantity existed anywhere).

| line | projected | actual | grade |
|---|---|---|---|
| verdict | FORECAST | **NO-FORECAST** | **MISS** |
| T | .18 in [.12, .28] | −.0165 | MISS |
| named disconfirmer | T in [.05, .10) — "signal real but under the bar" | T ≈ 0/negative — no signal at all | MISS (the disconfirmer was not disconfirming enough) |
| p_strat | < .001 | .8218 | MISS |
| twin | p > .3, no SURFACE | p .19, no SURFACE | HIT in effect |
| raw > stratified, raw significant | yes / yes | yes (.0194 > −.0165) / NO (p .124) | half MISS |
| per-rung: largest on add_base8, antonym | — | both ≈ 0 (−.036, −.013) | MISS |
| per-rung: add3_mid ≈ 0 | ≈ 0 | −.050 | HIT |
| 410m: same terminal as 2.8b | same | same (NO-FORECAST) | HIT by letter — projected in the spirit of FORECAST |
| 12b: FORECAST over R_12B, sub4_mid THIN | — | NO-FORECAST, sub4_mid THIN | terminal MISS, THIN HIT |
| gate 1 PASS both paths | PASS | PASS, 0 diffs | HIT |
| s*: antonym earliest ≤ 20k | — | antonym6 earliest (10k); antonym 30k | MISS |
| s*: base-8/arithmetic late ≥ 80k | — | sub_base8 90k, add3_mid 80k HIT; add_base8 70k near; arith_next 30k MISS | mixed |
| ≥ 1 rung-level transient clear | yes | none — but ITEM-level transience is pervasive (435 vs 272 etc.) | MISS at the projected grain; the phenomenon is real one level down |
| mechanics: zero halts, ~24 min/ckpt | yes | yes (environment kills aside, nothing partial landed) | HIT |

Verdict-level MISS with the sciencey misses all pointing one way: I
projected the probe's rung-level presence would cash out as item-level
ordering. It does not.

## The transferable findings

1. **Presence does not order items.** The same probe that reads rung-level
   presence at .20–.85 (twins at chance) carries ZERO item-grain forecast
   (T −.02, powered to see .05), under every preregistered variant. The
   thesis's descriptive arm (presence before performability — 2f, 3b)
   survives untouched; its predictive arm, given its best instrument and a
   sealed outcome, does not hold on this battery.
2. **The output channel forecasts; the representation does not.** 2d's
   committed 64-draw sampled counts — a rung-level FAIL in 2d — forecast
   the item order at T .167 (p 1e-4) through the same difficulty strata,
   and the probe adds nothing beyond them. Together with 3d (STRUCTURED)
   and 3e (reachability, not reversal), the consistent account: what
   predicts which items a bigger/longer-trained model emits first is how
   close those items already are to the smaller model's OUTPUT — sampling
   reachability — not what its residual stream linearly carries. Emergence
   order, at item grain, is an output-channel phenomenon at this
   resolution.
3. **Transient verification is the dominant texture of training.** On
   every rung, far more items verify somewhere on the grid than at the
   end (antonym 435 vs 272; antonym6 359 vs 149); rung accuracies are
   non-monotone within one size (antonym 300→272 after 110k), echoing
   sub3_mid's cross-size non-monotonicity from m4. "When does an item
   emerge" is not well-posed as a single step; the count outcome (ruling
   f) was the right choice, and first-correct (also null) the right
   sensitivity.
4. **The instrument did its job.** Gate 1 exact through two loader paths
   at both sizes; 162-file manifest, zero unpinned reads; seal enforced
   in code; zero referent failures; the environment killed processes
   twice and the tree never held a torn record. The NO-FORECAST is the
   cleanest negative this program has produced, and the first with a
   sealed outcome.

## Process notes (for the methods paper, Michael's call)

- A projection's "named disconfirmer" should bracket the NULL, not just
  the nearest failure mode: mine named T ∈ [.05,.10) and reality was ~0 —
  the projection ritual caught the miss, but a disconfirmer that includes
  "nothing at all" would have graded sharper.
- A non-gating competitor secondary can carry the experiment's most
  important finding; preregistering it (ruling: sampler competitor, §6.4)
  is what makes the FORECAST there reportable at all.
- Host-side process reaping is survivable iff every runner is
  skip-if-exists with whole-file writes and campaign processes are
  detached from the session ([[gotcha-tracked-background-tasks-reaped]]).
