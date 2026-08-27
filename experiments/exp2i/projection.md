# Exp 2i projection — SEALED before any intermediate 7B checkpoint loads

Committed after tags `exp2i-preregistered`, `exp2i-predictor-sealed`
and `exp2i-endpoint-sealed`, before gate 1 or any of the 21 grid
points is queried. Graded at close-out against the verdict. Inputs
drawn on: x_A (Pythia-1b's committed 2d counts), x_B (OLMo-2 1B,
sealed), the 7B endpoint table, R_CAP, the two sealed-predictor
descriptives ledgered in `PROGRESS.md` (weak x_A/x_B agreement,
ρ .06–.32 within strata; x_A near-silent on the three mid-digit rungs),
and the power record. No outcome has been seen.

**Verdict-level: BOTH.** Test A fires (cross-family concordance
survives the family swap, attenuated) AND Test B fires (OLMo-2 1B's
own sampled counts carry item-grain information beyond x_A's zero cut).

**Test A — cross-family (x_A → 7B stage-1 emission order, 2g's strata,
R_CAP = 9).** Point T_A ≈ .11, range [.08, .16]; p_strat < .01. The
reasoning: 2h's six carried rungs averaged D ≈ .25 within family
(sub_base8 .41, antonym6 .29, add_base8 .25, arith_next .23, odd6 .19,
antonym .14); a family swap plausibly halves that (item difficulty
inside a stratum — which antonym pairs are common English, which
octal operands are awkward — is partly corpus-independent, partly
Pile-specific); and the three rungs new to a primary contribute ≈ 0
by construction (x_A fires on 10/31/13 items of 500). Six rungs at
≈ .13 and three at ≈ .02 give ≈ .09–.11: **the bar T ≥ .10 is the
live question for A, not p.** LINEAGE is therefore the closest
alternative world, not NEITHER.

Named disconfirmers for A (the null bracketed in both directions):
- (A-i) T_A in [.04, .10) at p < .01 — structured but below the bar:
  cross-family concordance exists and is too weak to license the
  sentence. Grades the verdict MISSED (LINEAGE if B fires).
- (A-ii) T_A ≤ .02, p n.s. — no item-grain concordance across
  families: 2g/2h's reachability was Pythia's own path.
- (A-iii) T_A ≥ .22 — as strong across families as within: item
  difficulty is entirely corpus-independent structure. A miss in the
  other direction; would make SHARED-vs-BOTH turn on B alone.

**Test B — within-family beyond cross (x_B → the same outcome, 2g's
strata × x_A's zero cut).** Point T_B ≈ .15, range [.10, .22];
p_strat < .001. Same lineage, same data mix, same tokenizer, 4 T
tokens; x_B has more live items than x_A on eight of nine rungs and is
at ceiling nowhere; the two predictors' orderings barely overlap, so
conditioning on x_A's zero cut costs B little.

Named disconfirmers for B:
- (B-i) T_B in [.04, .10) at p < .01 — the within-lineage increment is
  real but under the bar (SHARED if A fires).
- (B-ii) T_B ≤ .02, p n.s. — beyond the cross-family predictor the
  smaller OLMo adds nothing: the shared component is the whole story.
- (B-iii) T_B ≥ .30 — a within-lineage signal stronger than anything
  2g/2h measured on Pythia; would say OLMo-2's 1B→7B path is far more
  item-concordant than Pythia's.

**Partials (BOTH's licence turns on them):** within-alone (x_B in
2g's strata) ≈ .18, above T_B; cross-beyond-within (x_A in strata ×
x_B's median bucket) ≈ .07, positive and under the bar — i.e. the
asymmetry favours the within-lineage predictor, and the shared
component is the headline only if T_A's per-rung CI excludes zero on
≥ 5 of 9 rungs, which I project it does NOT (expect 4 of 9: sub_base8,
antonym6, add_base8, arith_next).

**Per-rung texture, A:** the 2g/2h loci repeat in order at the top —
sub_base8, antonym6, add_base8, arith_next > odd6 > antonym; the three
mid-digit rungs ≈ 0 with CIs straddling zero (sub4_mid the likeliest
degenerate-looking cell: 13 live x_A items against 308 endpoint
positives). **B:** add3_mid and sub3_mid carry real signal for the
first time in any primary (x_B 70 / 35 live items); antonym and
antonym6 highest (x_B mean 26 / 17 draws per item — the richest rank
information anywhere in the program); sub4_mid ≈ 0 for B too (6 live
items).

**Reverse-direction descriptives (non-gating; outcomes known):** x_B
against 2g's 2.8b outcome and 2h's 6.9b outcome positive at roughly
Test A's magnitude (≈ .08–.14) — cross-family concordance should be
approximately symmetric. **410m cross replication:** same direction,
lower T (≈ .06–.10), possibly THIN on the mid-digit rungs.

**Extra rungs (raw D, descriptive):** reverse_string clears R_OLMo at
28/500; its raw D for A is undefined or ≈ 0 (x_A has ONE live item at
1b — 3e's item 436 — and none at 410m) and for B small positive (38
draws over 24 items). odd_one_out positive both tests (x_A 487 live
items, x_B 489); quad_next uncertain for A (100 live x_A items against
28 endpoint positives, barely eligible) and small for B; add4_mid ≈ 0
for A (1 live item) and ≈ 0 for B (10).

**Twin and `main`:** the from_config 7B twin verifies 0 items on
every rung (any nonzero is a harness finding, not a model one).
`main` reproduces the endpoint's rung ordering with the mid-digit
rungs lifted (already on disk; descriptive only).

**Transient verification:** pervasive as in 2g/2h — ever-verifies
exceeding final-verifies by 1.5–4× on the option-listing rungs;
at least one checkpoint-local collapse (a single answer emitted on
≥ 400 of 500 items at one grid point) somewhere in the head of the
grid.

**Gate 1:** clean — 34/34 rungs, digest equal, 17,000/17,000
continuations 0 diffs: the tenth consecutive byte-identical
reproduction on this stack, the first on OLMo and the first at 7B.

**Power declaration in force:** both tests POWERED (P(fires | D = .15) = 1.000; null SD of T .0096 / .0111; min-detectable T .022 / .026; P(fires | D = .10) = .44 / .38). A verdict of NEITHER or a non-firing test is therefore read as a measured absence at item grain (the shape caveat standing: nothing here transfers to a class-level effect).
