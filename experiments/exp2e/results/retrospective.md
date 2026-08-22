# Exp 2e — Retrospective

## Grading the projection (sealed 187206b, before the analyzer)

| Projected | Actual | Grade |
|---|---|---|
| Verdict FAIL via the cluster CI | FAIL, CI [.3733, .8916] | HIT |
| AUC(F1) ≈ .61 (.58–.64) | .6126 | HIT |
| block p ≈ .2–.4 | .3018 | HIT |
| CI lower bound < .5, ≈ [.40, .80] | [.3733, .8916] | direction HIT, width MISS (wider both ends) |
| drops: a few | 2 | HIT |
| 2d comparison exact | exact | HIT (a gate) |
| B0 ≈ .43 | .4209 | HIT |
| F1 − B0 ≈ +.18, CI includes 0 | +.1917, [−.271, .732] | HIT |
| F2 ≈ .60 | .6087 | HIT |
| F3 .5–.7 | .6206 | HIT (bracket too wide to credit) |
| ρ(F1, ascent) ≈ .2–.3, p ≈ .2–.4; B0 negative | .2131, p .2569; B0 −.1446 | HIT |
| pilot AUC .55–.65; rank corr ≈ .9 | .5968; .9684 | HIT |
| 1b ≈ 410m ≈ .6; 12b label similar | .6126 / .6285 / .6311 | HIT |
| ε = 1/3,200 lowers; majority-only raises to .63–.67; drop-two lowers | .5889; .6364; .5844 | HIT |
| Disconfirmer: INDETERMINATE (< 20 %) | did not fire | — |

Every projection hit except the interval's width. That is not
foresight. Every input was known (§2, ruling g); the projection was a
hand evaluation of a fixed function on a known table, and the analyzer
evaluated the same function with more decimals. A projection that
could not have missed tests only one thing — that the functional was
fixed before its correlation was computed, which is the one thing the
preregistration was for. The program's projection convention earns
nothing here and is recorded as such.

## What the numbers say

1. **2d's null was not its threshold's.** The threshold had erased a
   predictor of .61, not .75. Unthresholded, the sampled channel ranks
   this battery's rising rungs above its flat ones by about the same
   margin as the probe did on the same label (.6008), and the
   family-cluster bootstrap cannot tell either from .5.
2. **The signal is small, not noisy.** The pilot tier — a different
   seed at one-eighth the draws — reproduces the ordering (rank
   correlation .97 across rungs, AUC .5968); both sizes agree (.6126 /
   .6285); the ε, floor and battery variants all sit in [.58, .64]. The
   width of the interval is the family structure (16 families, 7 with
   a rising rung), not sampling noise in the predictor.
3. **The floor alone ranks against the label (B0 .4209).** The lowest
   floors belong to flat rungs (base7, oct2dec, the reversal pair at
   .002; add4_mid, caesar_len8 at .006); rising rungs include the
   highest floors (antonym .25, median5 .20). F1's +.19 over B0 is the
   honest size of "what the model adds beyond the answer space", and
   its interval includes zero.
4. **F2 ≈ F1 (.6087 vs .6126).** The floor covariate barely moves the
   ordering, because floor and raw rate are themselves coupled on this
   battery: the option-listing rungs have the highest floors AND the
   highest rates, so dividing by the floor changes their scale, not
   their rank. The ordering F1 produces is "option-listing rungs first,
   then everything else by rate" — answer-space structure first, model
   second.
5. **The three rising mid-digit rungs sit at the bottom** (sub3_mid,
   sub4_mid, add3_mid at −2.5 to −2.7 with the flat base-representation,
   Caesar and reversal rungs). Whatever rises there by 2.8b–12b, the
   410m/1b sampler does not see it at 32,000 draws per cell.

## Process

- Build and freeze in one session held up: nine worlds through the
  production referent path, 55/55 mutants (after ten fixtures for the
  first pass's survivors), the open() sweep, determinism. The one
  substantive freeze finding (F-1) was a boundary decision, not a
  defect.
- Found late, during the ratification edits: the record's caveat
  constant was a paraphrase of §2 where ruling g says verbatim. Closed
  with a fixture that extracts the paragraph from the doc and compares.
  Lesson (small): when a ruling says "verbatim", the test is a
  byte comparison against the source, not a reading.
- Zero model contact; zero stops; one pre-committed change UNSPENT.

## What 2e licenses (§6 FAIL, as written in advance)

The sampled channel at 410m/1b carries at most a little ordering
information about this battery's ascent; the second model family is a
long shot at this scale; the essay's Prediction 2 paragraph gains one
sentence. The §6 FAIL wording "carries no ordering information" is
corrected in VERDICT.txt to "not distinguishable from chance under the
family-cluster bootstrap at a point estimate of .61" — the numbers,
not the sentence, are the record.
