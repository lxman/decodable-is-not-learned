# Essay edit draft — exp3 signature-2 results into `emergent-resolution-the-gradient.md`

**Status: DRAFT for Michael's review. Nothing applied.** Three edits,
each anchored to exact current text. Numbers transcribed from
`experiments/exp3/results/verdict.json` and 3b's closed record.

**Publicity dependency, flagged before anything else:** the essay
cites the supporting repo, and exp3 is NOT yet in it —
github.com/lxman/decodable-is-not-learned currently ends at the
exp3a/exp3b round. The citation line in Edit 1 only becomes true
after the next re-extraction (exp3's preregistered+closed tag pair,
the same filter-repo process as before). If the essay ships first,
Edit 1's citation should say "tags exp3b-*" only and drop the exp3
tag reference until the repo catches up.

---

## Edit 1 — new evidence entry

**Anchor:** in "What's Happened Since the Mirage Debate," insert as a
new entry immediately BEFORE the line "**The exception.** Lubana et
al. (2024)..."

**Insert:**

> **I ran the same-weights test myself.** The probing literature and
> the sampling literature usually study different models, different
> tasks, different splits, which leaves room to doubt that the layers
> of the story hold together on one set of weights. So I ran it
> directly, preregistered with frozen analyses: string reversal on
> Pythia, where greedy decoding scores exactly zero out of five
> hundred. On those same weights, a linear probe reads the answer's
> first character from the residual stream at margins between .57 and
> .77 over its own untrained-network floor. Pure temperature-1
> sampling, 128,000 draws per cell, surfaced one complete correct
> reversal — one draw, on the shortest strings, at the larger of the
> two probe sizes. And the distribution's letter ranking at the first
> output position points away from the answer: the mass sits on the
> input's early characters, copying statistics, not reversal. The
> zero was never about absence. It was about where on the instrument
> ladder you're standing: the probe sees the structure, deep sampling
> occasionally reaches it, argmax never does. (Preregistrations,
> frozen analyses, and every raw draw: [supporting repo], tags
> `exp3b-*` and `exp3-*`.)

---

## Edit 2 — the discriminator becomes a ladder

**Anchor:** in "But What If the Resolution View Is Wrong?", the
paragraph beginning "There's real bite to this." currently ends:

> The question is which class the capabilities we care about fall
> into. Here the empirical record leans toward resolution: for the
> canonical emergent abilities (multi-step reasoning, in-context
> learning, instruction following), we can probe the structure in
> small models, elicit it by sampling, and forecast its arrival from
> below. A capability that percolates into existence should show none
> of those signatures. So far, the headline capabilities show all
> three.

**Replace those closing sentences with:**

> The question is which class the capabilities we care about fall
> into. Here the empirical record leans toward resolution: for the
> canonical emergent abilities (multi-step reasoning, in-context
> learning, instruction following), we can probe the structure in
> small models, elicit it by sampling, and forecast its arrival from
> below. A capability that percolates into existence should show none
> of those signatures. But I want to be precise about something my
> own experiments forced me to learn: the three signatures aren't
> three views of one fact — they're rungs on an instrument ladder,
> ordered by power. Probes see deepest. Exhaustive sampling sees
> next, with a floor set by your budget: 128,000 draws resolves
> per-draw rates down to about 1e-5 and nothing below. Argmax sees
> last. On my reversal weights the signatures separate cleanly: the
> probe fires at both model sizes, sampling reaches the capability
> only at the larger size and only on the shortest strings, argmax
> never does. So the discriminator isn't "all three present" versus
> "all three absent"; it's whether the signatures appear in ladder
> order as you increase instrument power. Percolation-class
> capabilities should show nothing at any rung, probes included.
> That's what Lubana-style networks show below threshold, and it's
> what keeps the carve-out testable rather than rhetorical.

**Companion touch, Prediction 1:** append to the paragraph ending
"...I'd love to see someone try to produce one."

> One refinement from my own runs: "nonzero pass rate under
> exhaustive sampling" has to carry its budget with it. A rate of
> 1e-5 is invisible at a thousand draws and obvious at a million;
> below the sampling floor there's a regime where only the probe arm
> of this prediction has teeth.

---

## Edit 3 — the foreground paragraph

**Anchor:** insert as its own paragraph immediately AFTER the
"There's real bite to this." paragraph (as amended by Edit 2) and
BEFORE "I think the resolution framing earns its keep on two
grounds."

**Insert:**

> There's one more thing the measured distributions say that the
> clean version of my own framing got wrong. I'd been picturing the
> output distribution as a blurred image of the capability: lower the
> detection threshold and the right answer brightens smoothly out of
> the noise. It doesn't. At the first output position, the bulk of
> the letter mass tracks shallow lexical statistics — which
> characters appeared in the prompt, with the earliest weighted
> hardest — and by that ranking the correct character loses to the
> input's interior on about four items in five. The capability
> doesn't sit just under the surface of the bulk; it sits below a
> foreground of copying statistics that dominates at every scale I
> measured. That's why the instruments disagree so sharply: probes
> and deep sampling can separate signal from that foreground, argmax
> and bulk probability mass can't. The noise in the noisy-channel
> picture isn't white. It's the model's own shallower habits, and any
> instrument that doesn't cancel them will read format where you
> hoped to read capability.

---

## Fact basis (transcribed, for review)

- Greedy full-string 0/500 on the reversal cells: 3a/3b committed
  records (the "famous zero").
- Probe margins .5731–.7725: `exp3b/probe_margins.json`, doc-pinned.
- 1/128,000: `reverse_string/1b/trained`, item 436 ('xuvq' →
  " qvux", seed 0, draw 6), verified by 2c's frozen criterion.
- "Shortest strings": the fired answer is length 4, the rung's
  minimum; rev_string7 (length 7) walled at ≤2.34e-5 pooled.
- "Four items in five" / early-character weighting: K = 78–115 of
  500 across the four adjudicated cells (sign test, p = 1.0000), the
  primacy gradient; echo (input[0]) was 89–94% of greedy argmax in
  3b.
- Sampling floor ~1e-5 at 128k: the frozen §7 detection table
  (power .72 at 1e-5, .95 at 2.34e-5).
- Em-dash budget: one per inserted section, per the voice profile.
