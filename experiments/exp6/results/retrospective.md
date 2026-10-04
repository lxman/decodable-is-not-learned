# Experiment 6 — retrospective: GENERAL beyond the first battery

Written 2026-10-04 UTC by the managing agent, GPT-6 Astra. This grades the
agent projection committed at `98d207404` against the one production verdict,
`exp6-closed` at `1244148082e4696c8a676e3cf3341a6fbb33874a`. It is an
experiment record, not prose in Michael's name. All statistics below come
from the saved `verdict.json`; no analysis was rerun for this retrospective.

## 1. The decision

**GENERAL. Both predictors hold on all four outcome families.** The frozen
headline condition is met by string and choice rungs for both predictors.
The forecast therefore extends beyond this program's first synthetic
battery, under the bounded licence written before collection.

| Outcome | A: Pythia-1b, k=256 | B: OLMo-2 1B, k=64 | Primary rungs read |
|---|---:|---:|---:|
| SmolLM3-3B | .154133 | .194494 | 12 |
| OLMo-2 7B | .143134 | .206738 | 10 |
| OLMo-2 13B | .112472 | .158083 | 12 |
| Comma | .168934 | .183817 | 9 |

Every test clears T≥.10 and p<.01. Every reported p is
**1/10,001 = .000099990001**, the finite-permutation minimum, not zero.
These eight readings share items and predictors; they do not establish an
eight-test family-wise error rate. A is cross-family on all four outcomes;
B is within the OLMo family on the two OLMo outcomes and cross-family on
SmolLM3 and Comma.

The result is at **item grain** on fresh generated items under this
program's renderings of benchmark-defined tasks. It is not an across-task
ranking, a replication of BIG-bench's original scores, or a causal test of
how capabilities are learned. The eleven rendering departures, string-level
collision gate and residual content/format familiarity remain disclosed.
Pythia's corpus predates BIG-bench; B and the outcomes can have encountered
BIG-bench-style material. B is smaller than every outcome in parameters,
but not in training tokens.

### Realized reading and power

Both Comma tests lose `unscramble_long`: only **13 distinct items ever
verify**, below the frozen n_pos≥20 requirement. They read nine of their
ten endpoint rungs, while their POWERED declaration simulated all ten.
That declared probability cannot be assigned to the narrower reading. The
other six tests read exactly the sets simulated for power. The loss is on
the outcome side; no predictor-degenerate rung was dropped.

OLMo-13B's 1k/2k/4k/8k loads each recorded 802,816 non-finite probed logits.
They remain scored as emitted under §3.4. The other 83 grid probes were
finite. All gates passed; no checkpoint was precision-adjusted, excluded
or rerun to improve the result.

## 2. Projection: world, tests and disconfirmers

**World HIT.** GENERAL was called, with OLMO-ONLY the main alternative.
All eight T values fall inside the stated inclusive ranges. **Seven of
eight binary fire calls hit**: A-on-Comma was called below the effect bar
at .09, and returned .168934. It is an upward binary miss even though it
lies just inside the numerical range [.01,.17]. All eight p<.01 calls hit.

The complete eight-test and **86-cell per-rung** grading table is
[`projection-grade.md`](projection-grade.md). Every eligible cell is graded
without a post-hoc tolerance; Comma's two thin cells are ungraded.

| Projection claim/disconfirmer | Observation | Grade |
|---|---|---|
| A holds on ≥3 families with positive string contributions | Four holds; string means .1729/.1530/.1073/.2437 | HIT |
| B>A on ≥3 families, ordinarily by .01–.08 | All four: +.0404/+.0636/+.0456/+.0149 | HIT |
| At most one near-null T≤.02 per predictor; no ≥.25 A on two families | No near-null test; no A≥.25 | Neither named magnitude disconfirmer fires |
| Breadth survives S11 and S13 | Every test remains positive and fires; both descriptive worlds GENERAL | Breadth HIT; attenuation was overstated, below |
| Strings and choices meet the headline condition for B | Both meet it for A and B | HIT, broader support than called |

B's paired advantage has a positive interval on SmolLM3, OLMo-7B and
OLMo-13B. Comma's interval is **[−.0189,.0477]**. The projection explicitly
did not require a significant paired advantage on every family.

### Per-rung texture

**66/86 ranges hit:** A 34/43 (3 low, 6 high); B 32/43 (4 low, 7 high).
All seven low misses are `sort5`: A on the first three families, B on all
four. The forecast expected more five-word sorting signal than appeared.

The thirteen high misses are printed individually in the full table. They
include IPA on Comma for both predictors (A .3111, B .4659), B's IPA on
SmolLM3 (.3533), shapes for A on SmolLM3/7B and for B on all three families
where shapes is in the endpoint set, and several unit/ASCII cells. The
forecast's designation of unscrambling as the leading string contribution
was too narrow: shapes, IPA and ASCII carry substantial signal too.

The headline has specific witnesses. For each predictor, six string rungs
(`unscramble_short`, `unscramble_long`, `ipa_word`, `sort3`, `ascii_bubble`,
`shapes`) and three choice rungs (`deduction3`, `deduction5`, `unit_interp2`)
have a positive per-rung interval on at least three evaluable families.
For B, both deduction rungs and short unscrambling qualify on all four.
No arithmetic rung qualifies on three families.

## 3. All named secondary forecasts, graded

These are descriptive, non-gating comparisons. Their reused `fires` fields
and named worlds make no new alpha claim. The full records, including
undefined and dropped cells, are in `verdict.json`; `VERDICT.txt` renders
the principal tables, flat rungs, referents and anchor comparisons.

| Reading | Saved result | Projection grade |
|---|---|---|
| S1 density ladder | A at k64→256: .1110→.1541, .0946→.1431, .0770→.1125, .1072→.1689. All four nested ladders increase at each recorded k. | HIT (only ≥3 net increases was called) |
| S2 410m | .0632/.0876/.0529/.0811, below A on every family | HIT |
| S3 conditioned predictors | B-beyond-A .1707/.1823/.1417/.1491; A-beyond-B .1309/.1149/.0873/.1365. Both positive; B's conditioned reading larger everywhere. | HIT |
| S4 string versus arithmetic means | B string>arithmetic on all three families with both defined. A does so on only two: 13B arithmetic .1551 exceeds string .1073. 7B arithmetic is undefined. | B HIT; A MISS against the stated ≥3 threshold |
| S5 wrong-target answer prior | .1247/.1263/.1248/.0977, positive and smaller than B on every family | HIT |
| S6 referents | No init referent clears a new-battery rung; the predictor twin has 30 verified draws out of 544,000. Pilot/main liveness is printed. | Already collected at projection; no forecast credit |
| S7 textures | Transient clearing occurs on endpoint-flat rungs in every family. The anticipated first-step 13B collapse persists; non-finite loads also occur at 2k/4k/8k. | Transience/1k claims HIT; later collapses not specifically forecast |
| S8 outcome order | All 12 directed pairs positive, .2081–.4730; six exceed the projected upper range .35. The OLMo pair is among the strongest two unordered pairs. | Positive/rank HIT; magnitude understated (only 6/12 inside range) |
| S9 two batteries | Mean earlier-minus-new T is .00792 for A, .03572 for B. | MISS: decline was projected larger for A |
| S10 anchors | All 16 D differences inside ±.03; maximum absolute .0027483 | HIT |
| S11 structure-conditioned | GENERAL, all eight fire. T decreases on only 2/4 families for each predictor. | Breadth HIT; ≥3 reductions per predictor MISS |
| S12 relaxed IPA | Endpoint strict→relaxed counts: 50→112, 110→222, 224→314, 31→52. Both predictors gain live items; world remains GENERAL. | HIT |
| S13 heuristic-clearing | GENERAL, all eight fire; A .1582/.1406/.1027/.1696, B .2129/.1996/.1520/.1783. Nine rungs per family except Comma's eight. | Breadth HIT; means can rise or fall as the projection's S13 note allowed |
| First-correct | GENERAL, all eight fire; A .1463/.1457/.1307/.1830, B .1991/.1894/.1584/.1700 | HIT |
| Two-of-four naming | GENERAL | HIT |

The four explicit disconfirmer claims were right about transfer, B's
relative strength, non-null magnitudes and retained breadth. They were too
confident that extra structure would reduce the estimates. S11 slightly
raises A on both OLMo outcomes and B on SmolLM3/13B. No sign loss occurs.

The S9 comparison uses the frozen referents' **unconditioned** earlier tests,
with the original battery's named rung sets and conditioning recorded in
each row. It does not substitute remembered headline numbers from the
earlier experiments. A's Comma reading rises from .1599 to .1689; its other
three declines are small. B's declines are larger on average, the reverse
of the projection's expectation.

## 4. Process and verification

The production CLI ran once, **2026-10-04 00:40:05–02:58:15 UTC**, at
`3140369c9`, with all production pins active, 10,000 permutations and
1,000 bootstraps. Elapsed time was **2 h 18 m 10 s**, versus the design's
about-one-hour estimate. It completed all thirteen named secondaries and
sensitivities with no gate or secondary failure.

The post-run verifier checked saved arithmetic in 148 test summaries and
1,290 bootstrap summaries, output finiteness, every primary rule, statuses,
headline support and the frozen decision/licence mapping. No statistic was
recomputed. The cold battery returned **13 PASS / 0 FAIL / 1 expected SKIP**;
the analysis-executing read sweep remained skipped. The JSON retains SHA256
`70c04aef2bdce01d4edf3774c4fbb9bc1ed77148fc1e03707c137127fe23034d`.
The result and evidence were pushed before the annotated `exp6-closed` tag;
fourteen artifact paths, the remote tag object and its commit were verified.

Both rentals were released before analysis. The sweep took 14 h 54 m 43 s.
Latest recorded credit deltas were $2.817529 for endpoint/preflight and
$24.572641 for sweeps, about **$27.39 combined**, with provider settlement
lag disclosed. Their archived evidence and release receipts are in
`../operations/instance-53866292/` and `../operations/instance-53961674/`.

### Process notes for Michael's consideration

1. **Detached computation and agent wake-up are different systems.** The
   earlier tool-shell callback failed; the replacement LaunchAgent actually
   delivered sweep completion and analysis completion. This analysis's event
   arrived 24.66 seconds after terminal status, with one delivery and an ACK
   at 02:58:50 UTC. The record supports this monitoring method with real jobs.
2. **Endpoint eligibility does not guarantee enough ever-correct items.**
   Comma's long-unscrambling endpoint cleared its low floor, yet the entire
   sweep supplied only thirteen distinct successes. The realized-set power
   disclosure correctly fired even in a positive overall world.
3. **Project cross-battery effects from the exact comparable referents.**
   The expected greater attenuation for A was wrong. The unconditioned,
   rung-specific old rows are the relevant comparison, and both batteries'
   arithmetic is printed rather than relying on remembered headline values.
4. **An effect surviving structure controls need not shrink.** The extra
   conditioning can remove opposing variation as well as shared shortcuts.
   The projection's breadth claim held; its predicted attenuation did not.
5. **Provider create responses require field selection.** The accidental
   instance-key commit required a history cleanup. Release was followed by
   HTTP 401 on the exposed key's instance-detail check; GitHub's retained
   historical object still needs the separately recorded Support purge.

No new experiment is authorized by GENERAL. The next substantive question
is Michael's call. **Close-out propagation to the essay/program record,
public experiment archive and paper inventory remains separately gated.**
