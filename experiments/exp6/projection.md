# Experiment 6 — projection before the training-checkpoint sweeps

Written 2026-10-03 UTC by the managing agent, GPT-6 Astra. This is an
agent forecast to grade at close-out, not a result or a statement in Michael's
name. Committed after `exp6-endpoint-sealed` at `5a6a3a8c2`, before any sweep
record. The design's rules and licences govern every landing.

## Information available at this projection

- The complete record through Exp 5b, especially the eight earlier forecasts
  on 2c's battery and their arithmetic-heavy structure.
- Exp 6's sealed predictors; the endpoint records and rule-derived sets:
  SmolLM3 / OLMo-7B / OLMo-13B / Comma have 12 / 10 / 12 / 10 primary rungs,
  and nine heuristic-clearing rungs each. These are observations, not forecasts.
- The one power record: all eight tests POWERED, 10–12 non-degenerate rungs
  each, 1,000 simulations and 500 permutations per power cell. At D=.15,
  P(fires) ranges .977–1.000; at D=.10 it ranges .386–.614. This measures
  resolution under the simulated alternative, not the likelihood of that
  alternative in the real sweep. The minimum-detectable-T values .0275–.0542
  describe the null quantile; the test also requires T≥.10.
- The disclosed outcome preflight: endpoints and first grid steps were read
  on three diagnostic slices, with shapes/timing/identity reported and no
  new-battery scores. Both 2c anchors were scored. The known OLMo-13B
  step-1000 fp16 collapse recurred. Thus this projection is before recorded
  sweeps, not before all intermediate-weight or item contact.

No Exp 6 verdict runner or real checkpoint-count forecast statistic was run.
Power's latent simulated outcomes are not the sweep's outcomes. Endpoint
composite SHA256:
`cd662c0249161278efd61967c4ad4adb824c73e2853cc16e3ede68f76d6e0e22`.

## World called: GENERAL, with modest confidence

Both predictors hold on at least three outcome families. The main alternative
is OLMO-ONLY: Pythia's advantage on the original battery leaned on the base-8
pair, which is now an anchor rather than an adjudicated rung. Expecting that
advantage to transfer to string and choice tasks is the substantive wager.

The weaker B-independent case is important: OLMo's later corpus can contain
BIG-bench-style material and Pythia's cannot. GENERAL is cleaner than OLMO-ONLY,
but neither establishes the absence of format/content familiarity.

### Eight test forecasts

These are subjective point forecasts and grading ranges, not confidence
intervals or probability-calibrated forecasts. A numerical HIT is inside the
inclusive range; a world or fire-call MISS remains a miss even if its T is
inside the numerical range. There is no additional post-hoc edge tolerance.

| Outcome | A: point T [range] | A fires? | B: point T [range] | B fires? |
|---|---|---|---|---|
| SmolLM3-3B | .14 [.06, .22] | yes | .18 [.09, .27] | yes |
| OLMo-2 7B | .13 [.05, .21] | yes | .17 [.08, .26] | yes |
| OLMo-2 13B | .15 [.07, .23] | yes | .19 [.10, .28] | yes |
| Comma | .09 [.01, .17] | no, effect bar | .13 [.04, .22] | yes |

All eight projected p-values are <.01. Comma's lower call reflects its shorter
training and different corpus; it is a hypothesis, not an inference from its
endpoint accuracy. The A holding set is the first three, the B holding set all
four. A fourth-family A fire would improve the table while missing that cell's
binary forecast.

**Claims with disconfirmers, both directions:**

1. **Transfer beyond arithmetic:** A fires on at least three families with
   positive string-task contributions. Disconfirmed by A holding on fewer
   than three, or by its apparent success depending entirely on choice/other
   rungs while string contributions average ≤0 on three families.
2. **B remains the stronger predictor:** B's unconditioned T exceeds A's on
   at least three families, ordinarily by .01–.08. Disconfirmed by A≥B on
   at least three; B−A>.10 on three is also outside the projected magnitude.
   No significant paired difference on every family is predicted.
3. **The new battery attenuates rather than erases:** at most one family per
   predictor has T≤.02. Two such families for either predictor disconfirm
   this. Conversely, T≥.25 on at least two families for A is an upward miss.
4. **Breadth survives surface controls:** S11 and S13 reduce magnitudes but
   retain positive averages on at least three families for each predictor.
   A sign loss on two families disconfirms it. These are descriptive checks;
   they cannot replace the primary rule.

## Per-rung and type texture

Ranges below concern per-rung D where the rung is actually read. Grade every
eligible predictor/family/rung cell against its row, including negative misses;
report the full hit/miss table, not just examples. Flat endpoint rungs remain
in the collected sweep but do not acquire a primary per-rung forecast here.

| Rungs | A: D range | B: D range | Projected texture |
|---|---|---|---|
| unscramble_short, unscramble_long | [.08, .35] | [.12, .42] | leading string contribution |
| sort3, sort5 | [.03, .28] | [.07, .35] | positive, partly item structure |
| ipa_word | [−.04, .20] | [.00, .28] | convention-sensitive, weaker than unscrambling |
| ascii_bubble | [−.02, .24] | [.00, .30] | positive but variable by family |
| shapes | [−.03, .22] | [.00, .28] | modest; Comma is endpoint-flat |
| deduction3, deduction5 | [.00, .25] | [.03, .32] | positive, attenuates under S11 |
| unit_interp1, unit_interp2 | [−.04, .20] | [−.02, .24] | weaker, substantial shortcut exposure |
| lcs | [−.04, .23] | [−.02, .28] | weak-to-modest; only two endpoint sets |
| modarith_add1 | [−.05, .22] | [−.03, .28] | Comma only, uncertain |

`modarith_sub1`, `modarith_mul1`, `ascii_basic` and `temporal` are flat in all
four observed endpoint sets. Do not count their exclusion as a successful
prediction. Transient clearing of a flat rung remains possible and is reported
in S7; this projection makes no specific transient-clear claim for them.

**Headline condition:** predict the GENERAL licence's two-type condition is
met by strings and choices for B. Specifically, an unscrambling rung and a
deduction rung each have positive intervals on at least three of B's evaluable
families. Failure means the sentence needs the design's type qualifier, even
if GENERAL itself is reached. No arithmetic-led headline is predicted.

## Named secondaries and sensitivities

- S1: 256-draw A exceeds 64-draw A on at least three families; no claim of
  strict monotonicity at every intermediate k. S2: 410m is weaker on average.
- S3: B-beyond-A stays positive on at least three; A-beyond-B is smaller and
  may include zero. Use the actual conditioned tests, not subtraction of T's.
- S4: string means exceed arithmetic means on at least three families for
  each predictor where both are defined. Empty type sets stay undefined.
- S5: the wrong-target answer prior is positive but weaker than B on average.
- S6: pilot, twin and endpoint-init observations are already collected; no
  retrospective forecast is claimed for them.
- S7: some verification is transient; the known OLMo-13B first-step collapse
  persists under the same pinned fp16 path. Other collapses are not predicted.
- S8: outcome-to-outcome mean D is positive for every evaluable pair, usually
  [.05, .35]; the 7B/13B pair is among the strongest two pairs.
- S9: the cross-battery decrease is larger for A than B on average. Earlier
  battery scores are known; only this new-battery comparison is projected.
- S10: new/committed anchor D differences stay inside the declared ±.03.
- S11: extra structure reduces the mean on at least three families per
  predictor; no strict reduction in every cell is predicted.
- S12: relaxed IPA improves counts but is not expected to change the world.
- S13: heuristic-clearing sets still support the same qualitative breadth;
  losing low-D unit/LCS rungs may raise their mean rather than lower it.
- First-correct and the two-of-four naming sensitivity should not reverse
  the general direction. These readings do not adjudicate the primary call.

## Every possible landing remains binding

| Landing | Interpretation fixed by design §6 |
|---|---|
| GENERAL (called) | generalises at item grain, named families/renderings; headline condition still applies |
| PYTHIA-ONLY | bounded to Pythia; the cleaner contamination asymmetry |
| OLMO-ONLY (main alternative) | bounded to OLMo; later-corpus familiarity remains a live alternative |
| SPLIT | report family table; no claim of generality |
| BATTERY-BOUND | if every evaluable test reads its exact powered set, withdraw the one-line thesis under §6; otherwise state the resolution/set limitation |
| UNDETERMINED | name outcome-side or predictor-side shortfall; no conclusion about generality |
| INSUFFICIENT_DATA | report the gate/refusal, not a scientific negative |

Grade the world first, then the eight tests, type/headline call, per-rung cells
and secondary claims. Endpoint inclusion and simulated power are not evidence
that the forecast is correct. A powered, exact-set BATTERY-BOUND result is the
projection's decisive downward miss and receives the preregistered withdrawal.
