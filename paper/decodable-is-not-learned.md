# Decodable Is Not Learned: Untrained-Weights Controls and Basis-Starved Splits for Linear Probing

**Author:** Michael Jordan
*Draft in progress. Sections 1–3 and 6–8 are stubs; 4 and 5 are first
drafts (2026-07-27). Every number is transcribed from the tagged record
(`exp2-preregistered`, `exp2-closed`, `exp2b-preregistered`,
`exp2b-closed`) or from `paper/fig2_data.json`, which recomputes from the
committed fit files.*

## Abstract

*(stub — written last)*

## 1. The problem and the prescription

*(stub — see methods-paper-outline.md §1: the decodable→learned leap; the
free-computation floor; P1 untrained twin, P2 basis-starved splits, P3
mechanism-calibrated tolerances)*

## 2. Background

*(stub — probing critiques interrogate the probe's expressivity; these
controls interrogate what the substrate computes for free; reservoir
computing, random features, Cover's capacity arithmetic)*

## 3. The instrument

*(stub — starved-probe pipeline, basis functions, split construction,
the four gates and their false-fire arithmetic, determinism
infrastructure)*

## 4. Two preregistered stress tests

The evidence for the prescription isn't a benchmark built to flatter it.
It's two preregistered experiments that the controls killed, in sequence,
for different reasons, before either one was allowed to touch its outcome
variable. Both designs were frozen and tagged before any data existed;
both adjudications ran as committed code against written rules; both
verdicts were projected in a timestamped ledger before the formal report
executed. The full record, including every number below, is in the tagged
repository history.

Both experiments serve a larger program that asks whether linear-probe
margins at small scale forecast which capabilities later emerge up a model
ladder. That question imposes an unusual discipline: probe results at
410M and 1B parameters had to be committed before any larger model was
queried, so the probe instrument had to be trustworthy on its own, with no
outcome data available to rescue it. The controls below exist because of
that constraint. Neither experiment ever queried the larger models. The
program's question remains open, and this paper makes no claim about it.

### 4.1 Experiment 2: standard splits, and what a random network decodes

The first experiment probed twelve capabilities on Pythia at 410M and 1B:
modular arithmetic, two- and three-digit addition, two-digit
multiplication, roman numeral conversion, weekday offsets, unit
conversion, string reversal, unscramble, acronym formation, category
counting, and a substitution cipher. Roughly
two thousand probe items per capability; linear probes swept over
(layer, token) candidates against a 2,500-draw permutation null with a
Bonferroni family correction; five probe seeds per cell. The design
included the control this paper argues for: the identical pipeline run on
an untrained twin of each model, same architecture and tokenizer, weights
at seeded random initialization. What it lacked was any defense in the
split. Probe train and validation rows were drawn from the same item pool
the standard way, stratified but otherwise random.

The untrained control fired on everything. All twelve capabilities, both
sizes, every seed: 120 of 120 fits significant, each at the
family-corrected permutation floor (p = 18/2501 ≈ .0072, meaning the
observed accuracy beat all 2,500 label permutations). These weren't
marginal detections. At 410M, seed-0 margins were 1.000 for unit
conversion and mod-7 arithmetic, 0.992 for two-digit addition, 0.982 for
roman numerals, 0.970 for weekday offsets; the weakest, the cipher, still
cleared 0.205 against its own null. Replication at 1B fired 60 of 60 with
near-identical margins, and the letter tasks got stronger (acronym 0.262
to 0.345, reversal 0.350 to 0.390): doubling the width hands the linear
readout twice the random features, so the bigger probe-side model deepens
the confound instead of escaping it.

The mechanism is what the reservoir-computing literature would predict. A
fixed random network is a feature expansion; with roughly 2,000 examples
against 1,024 features, a linear readout can assemble any deterministic
function of the visible tokens by regression, and every capability label
in the battery is a deterministic function of its prompt. A group-split
diagnostic made this concrete for mod-7: the untrained probe's accuracy
survives operand pairs it never saw (1.000) but collapses to chance on
held-out operand values (0.129–0.142 against a 0.143 majority baseline).
It isn't computing arithmetic; it's storing a per-operand-token offset
table and mixing it additively.

The diagnostic's sharper finding is about the trained network. On the
same held-out-operand split, the trained mod-7 probe collapses to 0.009 —
below chance, the signature of a lookup that's systematically wrong off
its table. The trained probe's perfect in-distribution margin was lookup
too. And a trained-minus-untrained gap score, the obvious repair, turned
out to saturate exactly where it was needed most: five of twelve
capabilities had both readouts at ceiling, because 1,500 training rows
memorize a 90-value token table perfectly on either network. Two-digit
addition explained the residue: Pythia's BPE splits numbers into digit
chunks, the addition label is digit-local, and an operand-level holdout
can't starve a digit-level basis, so even the random network generalized
across operands (0.983). The lesson that became the successor's design
rule: the split has to starve the basis the readout actually uses, and
that basis is a per-capability, tokenizer-specific object.

The frozen attrition rule dropped all twelve capabilities; the battery
floor was ten; the verdict was INSUFFICIENT_DATA with zero outcome-side
queries. Two smaller findings from the same closeout carried forward. The
shuffled-label control fired once in 120 fits, which the design treated
as an abort condition; the closeout ruled it the test's own designed
false-positive rate (expected fires ≈ 0.86), a zero-tolerance rule
mistakenly placed on a nonzero-rate test. And one of two argmax positive
controls failed at 410M (0.338 against a 0.9 bar) because its reliability
had been assumed from another model rather than measured, which is the
same assumption-transfer mistake in a different costume. Both reappear in
Section 6.

### 4.2 Experiment 2b: basis-starved splits, and the class underneath

The successor was designed around the diagnosis. Every candidate
capability now declares a surface basis: the tuple of prompt components a
lookup strategy would key on, analyzed against the tokenizer (the operand
token, the solution word, the unit pair, the letter-shift combination). A
starving split holds out a set of values per component; validation items
are those whose components are all held out, training items those whose
components are all kept, and mixed items are discarded. A readout keyed
on any basis component therefore scores chance on validation by
construction. Capabilities with no feasible starving split, including
anything digit-local, were excluded at design time. Gates got binomial
tolerances derived from the permutation-floor arithmetic instead of
zero-tolerance rules. The battery floor rose to twenty of a frozen
twenty-five.

Before the freeze, the construction was rehearsed against Experiment 2's
own activations, replaying two worlds known to be pure lookup through the
new splits. Both went silent. The class that killed Experiment 2 is
demonstrably closed by starving; that much is a positive result for the
construction, and the campaign data repeats it at scale: the mod-7 family
that fired at margin 1.000 under standard splits fired at seed-maximum
margins of 0.10 to 0.26 under starved ones, scattered one-to-two-seed
events at the weak edge of detection.

The campaign fit 770 probe cells over eight days on three machines, with
a determinism gate requiring each worker to reproduce a reference fixture
bit-for-bit before its results counted (the fixture passed identically on
arm64 Accelerate, x86-64 OpenBLAS, and Windows). One implementation bug
surfaced mid-campaign: the shuffled-control stage permuted labels before
building the split, which is undefined for label-stratified splits. The
fix was argued from mechanism in the ledger before rerunning (the
instrument's own permutation null already defined the correct order:
split from true labels, permute only the fit), and the affected stage was
refit uniformly. It's recorded here because hiding it would misrepresent
what preregistered infrastructure work looks like.

The untrained control then found the class underneath the lookup class.
Eighty-six of 250 untrained fits fired structurally, spanning thirteen of
the twenty-five capabilities. These fires don't resemble the tolerated
floor class: per-capability counts are binomially impossible against the
floor rate (a capability's ten fits expect 0.07 fires; the strong leakers
fired on ten of ten), and the margins reproduce across the two
independently initialized untrained models to within a few hundredths
(the strongest, collatz steps, at 0.74–0.78 at 410M and 0.75–0.82 at 1B).
Whatever carries these labels through a random network, it isn't the
particular weights, and starving the basis didn't remove it. Section 5
dissects what it is.

The frozen rules did what they were written to do. Attrition removed all
thirteen; twelve survivors sat below the floor of twenty; the verdict was
again INSUFFICIENT_DATA, again with zero outcome-side queries. The other
gates behaved: the known-present control confirmed the instrument sees
capabilities that plainly exist (entity tracking at mean starved margins
0.330 and 0.281 across sizes; a copy control at 0.997), and the shuffled
control's two fires in 250 sat at its designed rate (count-test
p = 0.538). The argmax positive control repeated Experiment 2's
assumption-transfer lesson in miniature: measured at 0.994 on the prior
battery's items, it failed the 0.9 bar on this battery's items at 410M
(0.868, upper confidence bound 0.896), a reliability that had been
assumed to transfer and didn't. The verdict was projected in the ledger from gate-1 data
three days before the frozen report ran; the report confirmed it without
surprise. For a preregistered program, that's the intended shape of even
a failure.

One honesty note on the adjudication itself. The frozen report contained
two drafting defects, caught at closeout: a pooled count test that would
have declared pipeline abort under any attrition event at all, and a
floor-signature check whose two conditions contradict each other on order
statistics grounds. Neither changed the verdict, both were ruled from
mechanism arguments written before the report ran, and both became
design rules for successors. Section 6 treats them as first-class
results: frozen criteria are code, and code written to implement a
preregistration can misimplement it.

## 5. The leak taxonomy

Thirteen capabilities survived basis starving on a network that has never
seen data. The question with reuse value is what property of a task
predicts that. The detection facts below are preregistered results; the
mechanism attributions are post-hoc hypotheses, formed by reading each
capability's label definition against its basis, and they should be
tested by construction in future batteries rather than trusted from this
one.

The pattern, stated up front: a label leaks when it is a low-complexity
function of surface fragments that the starving split cannot remove,
because the fragments are shared across held-out basis values. The basis
holds out values; it cannot hold out the alphabet the values are written
in. Labels that are morphological or low-modulus functions of that
alphabet ride through. Labels that require jointly composing the starved
components do not.

The strong tier makes this concrete. Roman numeral addition leaked at
margins 0.64–0.82: its probe label is the first numeral's value mod 10,
and roman numerals write value-mod-10 directly into the numeral's suffix
(I, II, III, IV...), so the label is literally printed on the surface in
a shared sub-alphabet that value-level starving can't touch. Unscramble
leaked at 0.18–0.22: its label is the solution's first letter, and that
letter is one of the five or six letters sitting visibly in the prompt;
a random expansion plus English letter statistics narrows the candidates.
The Collatz task leaked strongest of all (0.74–0.82 across both sizes):
its label is the ones digit of the first Collatz step, which is (up to
the parity branch) a function of N mod 20, and N mod 20 is carried by
the final digit tokens that all operand values share. Integer square
root (0.36–0.44) is a magnitude-binning label: the ones digit of the
root is constant on wide contiguous bands of N, and magnitude is legible
from leading digits and token length. Digit-product mod 7 (0.19–0.30) is
a fixed function of four visible digits that random nonlinear mixtures
partially express. In each case the leak is not memorization of held-out
values, which starving forbids, but computation over a shared surface
vocabulary that starving cannot forbid.

The weak systematic tier says the same thing at lower amplitude:
number-times-letter mod 26, three-by-one-digit multiplication's tens
digit, binary-to-decimal mod 10, weekday mod 7, and the mod-7 family all
fired at margins between 0.06 and 0.26 on scattered or systematic seeds.
These labels need joint composition of digits that random features
mostly can't provide, and starving removes the rest; what survives is
the weak shadow of partial digit statistics. Unit conversion is the
instructive oddball: it fired on exactly one probe seed at both sizes
(0.39 and 0.52), and its basis has only sixteen values with three held
out. Its label, the power of ten, is written in the unit's prefix
morpheme (kilo-, centi-, milli-), so whether the leak shows depends on
whether a particular holdout draw splits a prefix family across the
train-validation boundary. A leak can be a property of the draw, not
just the task, when the basis is small.

The trained side of the same fits, computed from the closeout data,
separates the thirteen into fates that matter for battery design. For
six of them, training adds real structure on top of the leak: the
trained starved margins exceed the untrained ones by up to 0.25
(integer square root by 0.21 and 0.25 at the two sizes, Collatz by 0.17,
roman by 0.16, unscramble by 0.10, three-by-one multiplication and unit
conversion by smaller and less stable gaps). These are tasks the models genuinely
partially compute below threshold, sitting on bases that leak; with the
label redefined off the surface carrier, they're candidates for rescue.
For digit-product and number-times-letter the gap is 0.03 to 0.06, and
what the probe reads is mostly the surface floor with training adding
little. And for five, the gap runs slightly negative: the mod-7 family,
binary-to-decimal, and weekday show trained starved margins at or near
zero while the random network fires weakly. Training appears to
specialize features away from the generic surface mixing a random
expansion provides, so on a starved split the trained network is less
decodable than noise. All three regimes produce identical
absolute-significance results under standard splits; they're only
distinguishable because both controls exist.

The twelve survivors sharpen the contrast from the other side. Their
untrained starved margins are 0.000 in every cell, both sizes, all
seeds. Eight are also silent or near-silent on trained weights at these
scales (seven at exactly zero, one at a single 0.009), which is what the
parent program would have scored against the eval ladder. Four show
trained structure where the random network shows none: string reversal
at 0.57 and 0.68 across the sizes, antonyms at 0.58 and 0.45,
odd-one-out at 0.32 and 0.27, count-divisible-by-7 at 0.12 and 0.11.
String reversal is the cleanest before-and-after in the record: under
Experiment 2's standard splits its untrained twin fired at 0.34–0.39,
and under a basis starved on the solution word the untrained margin is
exactly zero while the trained margin holds. That's the construction
doing precisely what it was designed to do, on a capability whose label
isn't written in a shared surface alphabet.

What the survivors share is that their labels sit at the far end of a
composition: the middle digit of a three-digit sum with its carry
structure, a base-7 or base-8 or octal conversion, a Caesar rotation, a
modulus of 13 rather than of the digit alphabet. The design guidance
this yields is checkable rather than aesthetic. Before including a
capability, write down its label as a function of the prompt and ask
what the cheapest surface approximation of that function is: whether the
label appears in the prompt's visible fragments, whether it's constant
on magnitude bands, whether it's a small-modulus function of single
tokens, whether the basis vocabulary is small enough for one holdout
draw to matter. Then measure it: run the untrained twin on the starved
split at generation time, before inclusion, and let the acceptance test
rather than the designer's intuition say whether the basis is starved.
Every mechanism above was legible in the label definitions before the
campaign ran. We found them afterward because we hadn't yet learned to
ask the question in that order.

## 6. Calibration lessons for frozen criteria

*(stub — the pooled-count and floor-signature defects as first-class
results; mechanism-derived bars; fixture tests from the design's worked
examples; pre-freeze gates adjudicated pre-freeze)*

## 7. Limitations

*(stub)*

## 8. Recommendations

*(stub — the checklist, T2)*

## References

*(stub — all citations arXiv-verified before entering §2)*
