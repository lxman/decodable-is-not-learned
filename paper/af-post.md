# Your Probe May Be Reading a Lookup Table

*Announcement and distillation of "Decodable Is Not Learned:
Untrained-Weights Controls and Basis-Starved Splits for Linear
Probing" (arXiv link TBD; supporting record:
github.com/lxman/decodable-is-not-learned, public with the arXiv
upload). Every number below is transcribed from that record.*

Last month I closed out a preregistered probing experiment: twelve
capabilities, linear probes on Pythia-410M and 1B, a 2,500-draw
permutation null per fit, Bonferroni correction, five seeds. One of
the frozen controls was an untrained twin of each model — the
identical probe pipeline, same prompts, same splits, same statistics,
run on a network with seeded random weights that had never seen a
token of training data.

The untrained control fired on everything. All twelve capabilities,
both sizes, every seed: 120 of 120 fits significant, each at the
permutation floor, with margins up to 1.000 for modular arithmetic and
unit conversion. A probe reading a never-trained network "detected"
arithmetic as cleanly as any probe result I've seen published. The
experiment terminated with zero scientific output, and terminating was
the correct behavior: the instrument had just demonstrated that its
readings didn't mean what the experiment needed them to mean.

This post is about what the probe was actually reading, why the
obvious repair doesn't work, what construction does work, and the
second confound class we found hiding under the first. If you publish
probing results, the one-sentence version is: run your exact pipeline
on an untrained twin of your model, and treat a structural fire as
disqualifying the capability, not as a baseline to subtract.

## What the probe was actually reading

A frozen random network is a feature expansion. Reservoir computing
builds working systems on exactly this: fix a random network, treat
its state as a rich nonlinear mixture of the input, and train only a
linear readout. Cover's capacity arithmetic says when to worry: a
linear separator with d degrees of freedom shatters about 2d points,
and a typical probe fits ~1,500 training rows against hidden widths of
1,024 or 2,048. At that ratio, a clean training fit is free. Whether
the probe generalizes to validation depends only on whether the label
is a simple enough function of the input that the random expansion
preserves it, and every label in a probing battery is some function of
the prompt. That's what makes it a task.

A group-split diagnostic made the mechanism concrete for mod-7
arithmetic. The untrained probe's accuracy survives operand *pairs* it
never saw (1.000) and collapses to chance on held-out operand *values*
(0.129–0.142 against a 0.143 majority baseline). It isn't computing
anything; it's storing a per-operand-token offset table and mixing the
entries additively. The readout memorized a 90-value lookup table
through the random network, and the standard train-validation split
never forced it to do anything else.

The sharper finding is about the trained network. On the same
held-out-operand split, the trained probe reads 0.009 — *below*
chance, the signature of a lookup that's systematically wrong off its
table. The trained probe's perfect in-distribution margin was a lookup
table too. And the obvious repair, scoring trained-minus-untrained,
saturates exactly where you need it most: five of twelve capabilities
had both readouts at ceiling, because 1,500 rows memorize a 90-entry
table perfectly on either network. In the successor experiment the gap
sometimes ran *negative*: training can specialize features away from
the generic surface mixing a random expansion provides, leaving the
trained network less decodable than noise on a fair split. Subtraction
treats decodability as one scalar channel. It isn't one channel.

## Starving the split, and the class underneath

The successor experiment redesigned the split around the diagnosis.
Every capability now declares a surface basis: the tuple of prompt
components a lookup would key on, analyzed against the tokenizer
rather than against intuition about the task (Pythia's BPE splits
numbers into digit chunks, so anything digit-local is banned rather
than starved badly). A starving split holds out values of every
component; validation items are those whose components are *all* held
out; items mixing kept and held-out values are discarded. A readout
keyed on any component meets only unseen values at validation and
scores chance by construction.

Starving killed the lookup class. Replaying two known-lookup worlds
from the first experiment through the new splits produced silence, and
the mod-7 family that fired at margin 1.000 under standard splits fell
to scattered fits at 0.10–0.26 under starved ones.

Then the untrained control found the class underneath: 86 of 250
untrained fits fired structurally, on thirteen of twenty-five
capabilities, at margins from .06 to .82 — reproducing across two
independently initialized untrained models to within a few hundredths.
Whatever carries these labels through a random network, it isn't the
particular weights, and holding out basis values can't remove it.

The anatomy is the useful part. A label leaks when it's a
low-complexity function of surface fragments that are *shared across*
held-out values — the split holds out values, but it can't hold out
the alphabet the values are written in. Roman numeral addition leaked
at margins .64–.82 because its label (first numeral's value mod 10) is
literally printed in the numeral's suffix: I, II, III, IV is a shared
sub-alphabet that no value-holdout touches. The Collatz task leaked at
.74–.82 because the ones digit of the first step is, up to the parity
branch, a function of N mod 20, and N mod 20 rides on final digit
tokens every operand shares. Unscramble leaked at .18–.22 because the
solution's first letter is sitting visibly among the prompt's letters.

The clean before-and-after is string reversal. Under standard splits
its untrained twin fired at 0.34–0.39. Starved on the solution word,
the untrained margin is exactly zero in every cell while the trained
margin holds at 0.57 and 0.68 across the two sizes. That's what a real
probe result looks like: a trained network reading out structure that
a random network, on a fair split, cannot. The twelve capabilities
that survived the screen all share that shape — untrained margins of
0.000 everywhere, labels at the far end of a genuine composition: a
carry chain's middle digit, a base conversion, a Caesar rotation, mod
13 instead of mod 10.

## Why this matters for the probes you run

Probing is load-bearing in this community: deception probes,
elicitation of latent knowledge, capability-precursor arguments,
"the model represents X" claims of every kind. Most of that work runs
in exactly the regime above — hundreds to thousands of labeled
examples against a residual stream of a few thousand dimensions — and
most of it reads absolute probe significance, sometimes with a
control task in the Hewitt-and-Liang sense. Control tasks interrogate
the probe: they randomize the labels and keep the trained
representation, bounding what an expressive probe could learn from
anything. The untrained twin interrogates the substrate: it keeps the
true labels and randomizes the representation, measuring what your
architecture gives away for free. These catch different failures, and
the second one is the one I've rarely seen run.

The operational point is the acceptance-test framing. When the
untrained twin fires structurally on a capability, that measurement
channel is contaminated, and nothing the trained network scores on it
is interpretable — the trained margin might be real structure, might
be the same surface channel read slightly better, and you cannot
decompose the sum. You don't subtract the floor. You drop the
capability or redesign its task until the twin reads zero, and only
then does the trained margin mean anything. My program found two
confound classes sequentially, each invisible until the previous one
was removed. I'd assume there are more.

## The checklist

The paper compresses everything above into a checklist written for
verbatim adoption. The short form:

1. Write every probe label as an explicit function of the prompt, and
   record what a lookup table and a random network should score before
   the capability enters the battery.
2. Name the surface basis a lookup would key on, against the
   tokenizer's actual token inventory.
3. Reject label targets local to single surface tokens.
4. Starve the basis: validate only on items whose every component
   value was held out of probe training; discard mixed items.
5. Run the untrained twin through the identical pipeline as a
   pre-inclusion acceptance test, not a post-hoc baseline.
6. Give every control a tolerance derived from the pipeline's own
   false-positive arithmetic; no zero-tolerance rules on nonzero-rate
   tests.
7. Derive significance bars near a permutation floor from order
   statistics (the expected max of N permuted fits), not SD intuition.
8. Measure control reliability on the current battery's items; never
   transfer it across battery versions.
9. Adjudicate at freeze time every gate whose inputs exist at freeze
   time.
10. Freeze adjudication code together with fixture tests from the
    design's worked examples.
11. Report every zero as a Clopper–Pearson bound.
12. Project the verdict in a timestamped ledger before the frozen
    report runs.
13. If fits are distributed, admit a machine's results only after it
    reproduces a reference fixture bit for bit.

## Status, honestly

Both experiments returned INSUFFICIENT_DATA under their preregistered
rules: the first lost its whole battery to the lookup class, the
second lost thirteen of twenty-five capabilities to the
surface-statistics class and fell below its frozen floor. No outcome
variable was ever measured. The controls have so far only killed
batteries, which means they've demonstrated they detect bad batteries
and not yet that a good battery exists — the twelve survivors, at
exactly zero untrained margin in every cell, are the existence proof
that the screen is passable, and the successor experiment is the test.
The parent question these batteries served (whether small-model probe
margins forecast which capabilities later emerge up a model ladder)
remains open; nothing here argues it either way.

The full record is public: preregistered designs frozen and tagged
before data, every probe fit, the campaign ledgers including the
mid-campaign bug and the two defects we found in our own frozen
adjudication code, and scripts that regenerate every figure and table
from the committed fits. The paper (link above) carries the leak
taxonomy per capability and the calibration lessons for frozen
criteria.

*Experiment infrastructure, analysis code, and drafting were produced
with substantial assistance from Claude (Anthropic); all
preregistration decisions, gate rulings, and final text are mine.*
