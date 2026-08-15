# Proposed §8 edit — the DISSOCIATION branch (exp3b §10.5)

**Status: DRAFT for Michael's approval. The paper is not modified.**

Target: `paper/decodable-is-not-learned.md`, §8's third observation —
the paragraph beginning "A third observation from the same scoring…"
(currently ~lines 1098–1116). What changes and why:

- the pooled margins .699/.624 are replaced with the per-size m3 values
  (the pooling was itself part of the confound; design §3);
- the units confound (one character read vs seven emitted, exact match)
  and the scale confound (probes at 410m/1b vs zeros at 2.8b+) are both
  named and both closed by the exp3b result;
- "decodable is not generable" is upgraded from a confounded contrast
  to a same-weights, same-units, same-label-space dissociation, with
  the positive control and the resolution bound stated;
- the 1/500 detail at 6.9b is kept (it was byte-reproduced by 3b's
  gate 3, which is worth one clause of corroboration).

## Replacement text

> A third observation from the same scoring is worth stating because it
> runs the other way and is, if anything, the more useful result. The
> two capabilities carrying the second and third highest starved probe
> margins in the battery — character-level string reversal at two
> lengths — scored an outcome of zero at every eval scale, and as first
> reported that contrast was confounded twice: the probe decoded one
> character where the eval demanded all seven exactly, and the margins
> lived at 410m and 1b while the zeros lived at 2.8b and above. A
> follow-up experiment (preregistered, frozen, run once — tags
> `exp3b-preregistered`, `exp3b-closed` in the supporting record)
> removed both confounds at once: it scored the first character of the
> greedy continuation against the probe's own label, in the probe's own
> 26-way space, on the probe's own models. The dissociation survived
> intact. On the same weights where the starved probe reads the
> answer's first character at margins .6263 and .7725 (seven-character
> reversal, 410m/1b) and .5731 and .6749 (variable-length),
> first-character emission is .0520/.0280 and .0320/.0260 against
> marginal floors of .056 and .054 — at or below floor in all four
> cells, while the same instrument scores a copy control at .9940 on
> the same weights. The eval-scale zeros stand as committed, including
> the one item of five hundred at 6.9b, which the follow-up reproduced
> byte for byte. The information is linearly decodable from the
> representation, survives basis starving, and clears the untrained
> gate, and the model does not emit even its first character above
> chance under greedy decoding — with the resolution stated: the design
> cannot distinguish floor from a true rate below .092, so this is no
> emission at that resolution, not a certified zero. Decodable is not
> learned, and on this evidence decodable is not *generable* either,
> now on the same weights, the same prompt, and the same label space. A
> probe margin licenses a claim about what a representation contains.
> It does not license a claim about what the model will do, and the gap
> between those is not a technicality: here it is the difference
> between the strongest signal in the battery and behaviour
> indistinguishable from chance.

## Knock-ons if accepted

- §8's earlier sentence quoting ".699 and .624" (if retained elsewhere)
  should quote per-size values or drop the numbers; exp3b's criteria
  deliberately never use the pooled means.
- The supporting public repo (github.com/lxman/decodable-is-not-learned)
  would need the exp3b record re-extracted (five existing tags
  preserved, two new ones added) before submission, same filter-repo
  procedure as the exp2c re-extraction.
- Appendix A's reversal rows gain a pointer to the same-weights result
  or stay as-is with §8 carrying the upgrade; either is consistent.
