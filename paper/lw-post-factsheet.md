# LessWrong post: fact sheet, section order, link block

Working notes for Michael's own write-up of the methods paper. Not a
draft and not for publication. Every number below is transcribed from
`paper/decodable-is-not-learned.md` as of 2026-09-09 (section given in
brackets), which transcribes it from the tagged record; the optional
"beyond the paper" block at the end is transcribed from CLAUDE.md and
the essay, not the paper.

## The rules this document lives under

LessWrong's LLM policy (2025-03-24, tightened 2026-03-14): a first-time
writer may not use any AI text output; text written by an LLM and then
edited by a human counts as LLM output and must sit in a labelled LLM
Content Block; posts above the site's detector threshold are rejected
automatically; a new user's post consisting substantially of such
blocks won't be approved. `paper/af-post.md` is LLM-drafted and is not
usable. Allowed: human prose "researched/developed with LLM
assistance", light editing, structural suggestions. So this document
supplies facts, order and links; the sentences are yours. A new
account's first post waits for moderator approval; submit as Personal
Blog and let the moderators decide on Frontpage. Alignment Forum: a
non-member's submission enters a review queue with a decision within
three days, or an AF member can promote the LessWrong post; treat it as
a bonus.

## Link block

- Repository (public since 2026-08-06): github.com/lxman/decodable-is-not-learned
- Archive: concept DOI 10.5281/zenodo.21830421 (resolves to the latest release, v1.17)
- Paper PDF, named flavour, in the public repo: `paper/tmlr/preprint.pdf`
- Paper source in the public repo: `paper/decodable-is-not-learned.md`
- Tags behind the paper's own numbers: `exp2-preregistered`, `exp2-closed`, `exp2b-preregistered`, `exp2b-closed`, `exp2c-preregistered`, `exp2c-closed`; the same-weights dissociation `exp3b-preregistered`, `exp3b-closed`
- Figures (PNG, upload from disk in the editor): `paper/figures/fig1_split.png` (the basis-starved split), `paper/figures/fig2_margins.png` (trained vs untrained starved margins per capability), `paper/figures/fig3_gates.png` (gate arithmetic)
- Checklist: Table T2, Section 10 of the paper (27 items)

## Suggested order (800 to 1,200 words)

1. The event: a preregistered probing experiment whose untrained twin fired on everything.
2. What the probe was reading: a random network is a feature expansion; the mod-7 lookup-table diagnostic.
3. Why the obvious repair fails: trained-minus-untrained saturates; digit BPE.
4. Starving the basis, and the class underneath it: 86 of 250, thirteen of twenty-five; string reversal as the before-and-after.
5. The screen at inclusion time: what it caught at the cost of a screening pass instead of a campaign.
6. The same error on the outcome side: report both floors.
7. Decodable is not generable: the same-weights dissociation.
8. The one-sentence version, and where the checklist and record are.
9. Status, honestly: what was claimed and what was not.
10. Disclosure, in your words (facts it must carry are listed at the end).

## Fact sheet

### Experiment 2: standard splits [§4.1; tags exp2-*]

- Twelve capabilities on Pythia 410M and 1B; about 2,000 probe items per capability; linear probes swept over (layer, token) candidates; 2,500-draw permutation null; Bonferroni family correction; five probe seeds per cell.
- The untrained control fired on 120 of 120 fits, each at the family-corrected permutation floor (p = 18/2501 ≈ .0072: the observed accuracy beat all 2,500 label permutations).
- 410M seed-0 margins: 1.000 for unit conversion and mod-7 arithmetic; 0.992 two-digit addition; 0.982 roman numerals; 0.970 weekday offsets; the weakest, the cipher, 0.205.
- 1B fired 60 of 60; letter tasks got stronger with width: acronym 0.262 to 0.345, reversal 0.350 to 0.390.
- Mod-7 group-split diagnostic: the untrained probe survives operand pairs it never saw (1.000) and collapses to chance on held-out operand values (0.129 to 0.142 against a 0.143 majority baseline). It stores a per-operand-token offset table.
- The trained mod-7 probe on the same held-out-operand split: 0.009, below chance. Its perfect in-distribution margin was lookup too.
- Trained-minus-untrained saturates: five of twelve capabilities had both readouts at ceiling; 1,500 training rows memorize a 90-value token table on either network.
- Two-digit addition: Pythia's BPE splits numbers into digit chunks, the label is digit-local, an operand-level holdout can't starve a digit-level basis, and the random network generalized across operands at 0.983.
- Verdict: all twelve attrited; battery floor ten; INSUFFICIENT_DATA; zero outcome-side queries.
- Shuffled-label control fired once in 120 fits (expected ≈ 0.86); the design had treated any fire as an abort, a zero-tolerance rule on a nonzero-rate test.
- One of two argmax positive controls failed at 410M: 0.338 against a 0.9 bar, reliability assumed from another model rather than measured.

### Experiment 2b: basis-starved splits [§4.2, §3; tags exp2b-*]

- Every capability declares a surface basis analyzed against the tokenizer; the starving split holds out values per component; validation only on all-held-out items, training only on all-kept, mixed items discarded. Splits must hold out at least 15 values per component and produce at least 300 validation items. Frozen battery 25; floor twenty of twenty-five.
- Rehearsal before the freeze: two known pure-lookup worlds from Experiment 2 replayed through the new splits went silent.
- The mod-7 family: margin 1.000 under standard splits, seed-maximum 0.10 to 0.26 under starved ones.
- Campaign: 770 probe cells over eight days on three machines under a bit-for-bit determinism gate.
- Mid-campaign bug, disclosed: the shuffled-control stage permuted labels before building the split; fixed from mechanism in the ledger, the stage refit.
- The untrained control: 86 of 250 fits fired structurally, on thirteen of twenty-five capabilities. A capability's ten fits expect 0.064 fires; the strong leakers fired on ten of ten; margins reproduce across two independently initialized untrained models (collatz 0.74 to 0.78 at 410M, 0.75 to 0.82 at 1B).
- Verdict: thirteen attrited, twelve survivors below the floor of twenty, INSUFFICIENT_DATA, zero outcome-side queries.
- Other gates: known-present control saw entity tracking at mean starved margins 0.330 and 0.281 across sizes and a copy control at 0.997; shuffled control 2 fires in 250 at its designed rate (count-test p = 0.538); argmax control 0.994 on the prior battery's items, 0.868 (upper bound 0.896) on this battery's at 410M against the 0.9 bar.
- The verdict was projected in the ledger from gate-1 data three days before the frozen report ran.

### The leak taxonomy [§5]

- A label leaks when it is a low-complexity function of surface fragments the starving split can't remove: the basis holds out values, not the alphabet they're written in.
- Strong tier (untrained starved margins): roman numeral addition 0.64 to 0.82 (value mod 10 is printed in the numeral's suffix); unscramble 0.18 to 0.22 (first letter is visible in the prompt); Collatz 0.74 to 0.82 (ones digit of the first step is a function of N mod 20, carried by final digit tokens); integer square root 0.36 to 0.44 (magnitude banding); digit-product mod 7 0.19 to 0.30.
- Weak tier: 0.06 to 0.26 on scattered or systematic seeds (number-times-letter mod 26, three-by-one multiplication's tens digit, binary-to-decimal mod 10, weekday mod 7, the mod-7 family).
- Unit conversion: fired on exactly one seed at both sizes (0.39 and 0.52); basis of sixteen values with three held out; the label is in the prefix morpheme. A leak can be a property of the draw when the basis is small.
- Trained over untrained (Figure 2): six capabilities show training adding real structure on top of the leak, gaps up to 0.25 (isqrt 0.21 and 0.25 at the two sizes, Collatz 0.17, roman 0.16, unscramble 0.10); digit-product and number-times-letter gaps 0.03 to 0.06; five run slightly negative (mod-7 family, binary-to-decimal, weekday).
- The twelve survivors: untrained starved margins 0.000 in every cell, both sizes, all seeds. Eight silent or near-silent on trained weights (seven at exactly zero, one at 0.009). Four show trained structure: string reversal 0.57 and 0.68, antonyms 0.58 and 0.45, odd-one-out 0.32 and 0.27, count-divisible-by-7 0.12 and 0.11.
- String reversal is the before-and-after: untrained twin 0.34 to 0.39 under Experiment 2's standard splits, exactly zero under a basis starved on the solution word, trained margin holding.

### Frozen-criterion defects [§6]

- Lesson 1: the frozen report tolerated a floor fire only within 3 SD of the null mean, but the expected maximum of 2,500 null draws sits about 3.5 SD above it; a clean null was expected to hand the predicate about 1.6 misclassified fires per 250. The two observed shuffled fires sat at 3.6 and 4.7 null SD and were both misread as structural.
- Lesson 2: the report pooled every structural fire into one count test that trips at seven fires in 250 while one leaking capability contributes ten fits, so any attrition was an abort as coded (p = 6.5e-117 on the observed 86); no test had executed the provision before real data did.
- Lesson 4 (selection): the reported site is the best of fourteen to eighteen candidates. On untrained networks it reads 1.28 times the candidate mean (0.2307 vs 0.1808), positive in 246 of 247 fits; on the successor battery 1.33 (0.1393 vs 0.1045), 227 of 227. Not load-bearing there: the primary rank correlation moves .431 to .456 on the profile mean. Report the per-site profile with the twin's value beside each site.
- Corroboration with its weakness attached: the same two-gate apparatus on a synthetic percolation system, forty models below threshold, 0 fires in 480 untrained and 320 trained sites; but that probe's split is entity-wise by construction, so it is close to circular.

### The screen at inclusion time [§7; tag exp2c-preregistered]

- Tier 1 at candidate-design time: two untrained seeds at both sizes against 500 permutations, about an hour per candidate. Tier 2 on survivors before the freeze: five seeds by both sizes by 2,500 permutations, declared to be the campaign's untrained-gate fits.
- Base-12 catch: label "N mod 12" entered with a written argument that a digit-suffix lookup fails; N mod 12 decomposes by the Chinese remainder theorem into N mod 3 (digit sum) and N mod 4 (last two digits). Tier 1 fired structural-abort on four of four fits. Replacement label: digit sum of the base-12 representation mod 5; screen silent on the same prompts and basis.
- Three rescues passed the screen that caught their parents at margins up to 0.82: roman (sum of the two values mod 7), Collatz (second step), integer square root (gap to the largest square below). Three taxonomy rows upgraded from hypothesis to constructively tested.
- New class, positional gather: a letter at a computed interior position of a printed 8-letter string, p = ((i + j) mod 6) + 2 and a product variant; four of four fits structural-abort; family ejected. Reversal's fixed-position label reads zero from untrained weights; a surface-computable variable position leaks.
- A six-word odd-one-out rung's split met its feasibility floors only by swallowing a whole word category; re-blessed to a one-component basis (minimum starved validation 305 items to 2,336).
- A six-option antonym rung with a measured heuristic dose (about 0.20 accuracy against 0.167 chance): screen silent, corrected p 1.0 in every fit.
- A Hamming-match-count rung ejected on the behavioural bar: 0.282 trained accuracy at 1B, upper bound 0.324, over the 0.25 bar; power re-run at 0.769 against the 0.75 floor.
- The battery at the freeze: 34 rungs in 16 families; 220 frozen-configuration fits over the 22 new rungs; two fires, both from a single rung at the add-one floor inside the tolerated band, against an expectation of 1.41 (binomial p = .41); the twelve carried survivors all-zero; argmax control 0.960 and 0.980 against 0.9. The program's first battery to reach its freeze with the untrained gate clean.

### The same error on the outcome side [§8; tag exp2c-closed]

- Outcome: argmax accuracy on held-out items at 2.8b, 6.9b and 12b, normalized against an untrained floor. An untrained model emits malformed text, so the floor sat at or near zero on all thirty-four capabilities, and a model that has learned only the format is credited its whole guessing rate.
- Ten of thirty-four landed within noise of their own chance rate. Modulus-13 arithmetic scored .046 against 1/13 = .077, below chance, credited a margin of .071. A four-option capability scored .208 against .250, below chance, ranked fifth of thirty-four. Two of thirty-four cleared chance by a factor of two or more.
- Re-scoring against within-answer-space chance moved the primary rank correlation down, .368 to .200, and the count of capabilities with nonzero outcome scores from twenty-five to thirteen. The contamination manufactured correlation.
- Invisible to every recommended control: untrained gate clean, shuffled gate clean, known-present controls passed.
- Prescription: report both floors; commit the option count for every multiple-choice item at freeze.

### Decodable is not generable [§8; tags exp3b-*]

- The two capabilities with the second and third highest starved margins, string reversal at two lengths, scored zero at every eval scale (including one item of five hundred at 6.9b, reproduced byte for byte).
- Same-weights test: first character of the greedy continuation scored against the probe's own label in the probe's 26-way space on the probe's models. Probe margins .6263 and .7725 (seven-character reversal, 410m/1b), .5731 and .6749 (variable length); first-character emission .0520/.0280 and .0320/.0260 against marginal floors of .056 and .054; copy control .9940 on the same weights.
- Resolution stated: the design cannot distinguish floor from a true rate below .092. No emission at that resolution, not a certified zero.

### Status, honestly [§9]

- Both campaigns ended INSUFFICIENT_DATA; no outcome variable was measured by either.
- The successor battery passed the screen, reached its outcome, and returned a FAIL its own power analysis had declared uninterpretable in advance: 22 of 34 capabilities at zero probe margin, 9 of 16 family blocks inert, seven effective blocks where the power table assumed sixteen.
- Demonstrated on one model family, one tokenizer, two scales; probes linear; candidate family two token positions and every third layer, so silences are family-relative and fires absolute.
- The untrained control is necessary, not sufficient; the two confound classes were found sequentially and more should be assumed to exist.
- n = 1: the checklist's claims are existence claims, made under preregistration and frozen criteria; no prevalence estimate is claimed.

## The one-sentence version

Run your exact pipeline on an untrained twin of your model, and treat a structural fire as disqualifying the capability, not as a baseline to subtract. [§1, P1]

## Disclosure line: facts it must carry

Infrastructure, analysis code and the paper's text drafting used Claude (Anthropic) under your direction; every design decision, gate ruling, capability ejection and freeze decision is yours; every number is transcribed from the tagged record; you read and approved every section. (The paper's Disclosure section says exactly this; the post's line is yours to phrase.) The post itself contains no AI-written text.

## Optional: beyond the paper (from CLAUDE.md and the essay, not the paper)

If you want one sentence on what the program did after the paper: the same output-channel instrument later produced eight sealed item-grain forecasts of emergence order across Pythia, OLMo-2, SmolLM3 and Comma checkpoints (Somers' D .17, .20, .22, .18, .17, .25, .16, .21, each at p = 1e-4), while the per-item probe reading forecast nothing on the two Pythia outcomes where it was tested as the competitor. Every run is tagged in the same repository. Cite the essay for this, not the paper.
