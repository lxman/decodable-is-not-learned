# Experiment 2c — Battery-Growth Design (shape B2) — ACCEPTED 2026-08-01, rulings applied

**Status:** ACCEPTED with rulings applied 2026-08-01. Drafted the same
day as a proposal for Michael's review; his five rulings (table below)
are folded into the body, and the previously open questions of §8 are
now a rulings record. No code written; every rung here still has to pass
the established spec → review → items → tier-1 → tier-2 loop before it
counts.

**Rulings applied (all Michael, 2026-08-01):**

| # | decision | ruling |
|---|---|---|
| 1 | drop decision (four candidates, three slots) | build F1 (order_stat), F2 (seq_extrap), F3 (pos_letter); **F4 (str_align) is the named reserve** |
| 2 | F3 starving basis | **string-as-basis**: the printed string S, per-string holdout (N-token-basis shape); position arithmetic disclosed as inherently unstarvable |
| 3 | new 2c wordlists | approved at the stated floors (ANTONYMS_2C ≥ ~90 pairs, CATEGORIES_2C ≥ ~8×6), 2c-owned, hand-reviewed per §2's hygiene criteria |
| 4 | F2b dial | **quadratic replaces geometric**: `quad_next`, t_k = a + d·k + q·k², label t_4 mod 7, seed 20260823 |
| 5 | antonym6/odd6 class count | **k = 6 confirmed** for both siblings |

**Binding parent:** the B2 growth ruling (PROGRESS.md 2026-08-01, "Growth
composition ruled — B2"). B2 = +9 rungs to the 26-rung scored battery,
target 35 rungs, simulated power@ρ=0.6 = 0.777 (sampled block-permutation
test, n_sims=2000). This document turns B2's composition into concrete
rung specs; the four-candidate/three-slot drop decision it posed is now
ruled (table above).

Nothing here changes any frozen or committed artifact. The base12 episode
is the standard I'm holding every carrier argument to: base12's own
preregistered `dumbest_baseline` reasoned past a CRT decomposition
(N mod 12 = N mod 3 × N mod 4) that fired 4/4 at tier-1. Each carrier
argument below shows the modular arithmetic explicitly so a skeptic can
try to break it with pencil and paper. Where I could not clear a
territory on paper, I say so and reject it (§4) rather than register it
and hope the screen catches it.

---

## 0. The ruled composition and the shape arithmetic

B2 is +9 rungs, allocated exactly as ruled:

| ruling | change | rungs |
|---|---|---|
| (a) | base_repr grows 3 → 4 | +1 |
| (b) | antonym gains a sibling (singleton → 2) | +1 |
| (c) | odd_one_out gains a sibling (singleton → 2) | +1 |
| (d) | THREE new 2-rung families | +6 |
| | rescues stay pure singletons (no change) | 0 |
| | **total** | **+9** |

Family shape, before → after:

| | size-4 | size-3 | size-2 | size-1 | rungs |
|---|---|---|---|---|---|
| current (26) | modulus, mid_digit | base_repr | base_arith, rotation, counting, reversal, clock (5) | rescue×3, antonym, odd_one_out (5) | 26 |
| **B2 (35)** | modulus, mid_digit, **base_repr** | — | base_arith, rotation, counting, reversal, clock, **antonym**, **odd_one_out**, **+3 new** (10) | rescue×3 | **35** |

(B2 promotes base_repr 3→4, antonym and odd_one_out 1→2, and adds three
2-rung families; no size-3 family remains.)

3×4 + 10×2 + 3×1 = 12 + 20 + 3 = **35 rungs, 16 families**, shape
`[4,4,4, 2×10, 1,1,1]`. Matches the ruling. The three rescue families
stay size-1 by ruling: their evidential job is the fire→silence contrast,
not ladder statistics, so they never join the family-honest ρ as
multi-rung units.

**Seeds.** Continue the sequence from **20260817** (last used:
base12_digitsum = 20260816). The nine built rungs take 20260817–20260825
in proposal order; F4's two rungs hold 20260826–20260827, assigned only
if the reserve is promoted (§7), so the built set stays contiguous.

---

## 1. The leak classes every rung below is checked against

Named from the 2b VERDICT, the methods-paper leak taxonomy (§5), and the
tier-1 ejections of base5/base12. Each carrier argument in §2–§3 states
which of these it dodges and why:

1. **digit-local** — label is a function of a fixed-width decimal-digit
   suffix. `N mod d` when `gcd(d,10) > 1` (base5: `N mod 5`, since
   `10 ≡ 0 mod 5`; bin2dec `mod 10`).
2. **value-mod-10 carrier** — label rides the final decimal-digit tokens
   shared across held-out values (roman's numeral suffix; Collatz first
   step ≈ `N mod 20`).
3. **N-mod-k CRT decomposition** — `N mod k` where `k` factors into
   coprimes each of which is surface-legible. base12 died here:
   `12 = 3×4`, `N mod 3` = decimal digit-sum, `N mod 4` = last two
   decimal digits. Both computable from the printed digits; together they
   pin `N mod 12`.
4. **magnitude banding** — label constant on wide contiguous ranges of N;
   magnitude legible from leading digits + token length (isqrt root ones
   digit).
5. **suffix / sub-alphabet** — label written into a shared morphological
   fragment (roman suffix, unit prefix kilo/centi/milli).
6. **first-letter / char-class legibility** — label is a visible letter
   or a low-modulus function of the visible character alphabet
   (unscramble first letter; English letter-frequency shortcut).

The one structural move that dodges all six at once, on 2b's record, is a
**position label under a randomized presentation** (antonym, odd_one_out:
untrained margin 0.000 in every cell). Position is not a function of any
surface token because the correct item sits at a uniformly random slot.
Three of the proposals below (antonym6, odd6, order_stat) lean on exactly
this.

---

## 2. The three binding single rungs

### (a) `base13` — the 4th base_repr rung

- **Task / surface.** "Write N in base 13." N ∈ [200, 9999], drawn as a
  single decimal integer token, exactly like base7/base12. Surface answer
  is the base-13 string (digits 0–9 then A/B/C for 10/11/12, the base12
  hex-style convention).
- **Probe label.** `N mod 13` — the last base-13 digit, read as an
  integer 0–12 (13-class). Not printed in the question (the question asks
  for the full representation), mirroring base12/base12_digitsum.
- **Carrier analysis (dumbest-baseline register).** 13 is prime, so there
  is **no CRT decomposition** — the exact defect that killed base12
  (`12 = 3×4`) cannot exist for a prime modulus. Not digit-local:
  `gcd(13,10)=1` and `10^k mod 13` cycles `1,10,9,12,3,4` with period 6,
  never 0, so no fixed decimal suffix determines the label. Not
  value-mod-10: `N mod 13 ≠ f(N mod 10)` (23→10, 33→7 share last digit 3,
  differ mod 13). Not magnitude-banding: `N mod 13` oscillates with
  period 13 across the whole range. The only surface carrier is the
  three-digit-block alternating rule — `10^3 ≡ -1 (mod 13)` (verified:
  1000 mod 13 = 12), so `N mod 13 = ((N mod 1000) − (N div 1000)) mod 13`
  for our ≤4-digit N. That same rule exists for base7: `10^3 ≡ -1
  (mod 7)` (1000 mod 7 = 6), and **base7 survived at untrained margin
  0.000**. base13's carrier is base7's carrier at a larger residue count;
  the direct precedent already cleared it.
- **Dial.** family `base_repr`, `dial_name="base"`, `dial_value=13`
  (base7 anchors 7; oct2dec 8; base13 13 — the "prime coprime to 10, last
  digit = N mod b" slot, extended).
- **Screen-risk: LOW.** The mechanism that fires if I'm wrong: a random
  net approximates the 2-block alternating sum `(N mod 1000) − thousands
  digit` and reads it mod 13. base7's 0.000 says it doesn't; a 13-class
  label is strictly harder to leak through the same random projections
  than base7's 7-class one.
- **Oracle / surface.** oracle: `N mod 13`. surface_answer: N written in
  base 13 (A/B/C for 10/11/12).
- **Feasibility.** basis = N token (~9800 values), default `SplitParams()`,
  N_PROBE 2000 — identical shape to base12/base12_digitsum (min val ~400).
  No blessed override expected.
- **Seed 20260817.** No new wordlist (numeric).

### (b) `antonym6` — the antonym sibling

- **Task / surface.** "Which of these means the opposite of 'X': w1, w2,
  w3, w4, w5, w6?" — the reused antonym task at 6 options (1 antonym + 5
  distractors) instead of 4.
- **Probe label.** answer **position** (1–6), 6-class — assigned by the
  generation-time shuffle, identical construction to reused antonym
  (position 1–4).
- **Carrier analysis.** Position is uniform over the six slots and is not
  a function of any surface token: no digit-local, value-mod-10, CRT,
  magnitude, suffix, or first-letter carrier can predict a randomized
  slot. This is the exact survivor mechanism — 2b's antonym fired at
  untrained margin 0.000 in every cell. The only way position leaks is if
  the answer word is surface-distinguishable from its distractors (e.g.
  systematically shortest, or sharing more letters with the cue). The
  distractor pool must be drawn from the same antonym vocabulary and
  balanced on length / first-letter distribution, exactly as 2b's
  `_gen_antonym` did.
- **Dial.** family `antonym`, `dial_name="n_choices"`, `dial_value=6`
  (reused antonym is the implicit 4). Difficulty rises with distractor
  count; within-family secondary expects the 6-choice margin below the
  4-choice one.
- **Screen-risk: LOW.** Fires if the 2c antonym list leaves the answer
  length- or letter-separable from distractors — a wordlist-construction
  defect, not a label defect; caught by the same balancing 2b applied.
- **Oracle / surface.** oracle: position (1–6) of the antonym. surface_
  answer: the antonym word.
- **Feasibility.** basis = the cue word (2b antonym used holdout 0.2,
  min_holdout_values 15, min_val_items 300). Needs a 2c antonym pool large
  enough that a 0.2 holdout leaves ≥15 held cues AND ≥300 val items —
  roughly **≥ 90 antonym pairs**. Flag if the 2c list comes in smaller
  (blessed holdout override or a wider n_probe).
- **Seed 20260818.** **Requires a new 2c wordlist** `wordlists_2c.
  ANTONYMS_2C` (2b's frozen ANTONYMS is off-limits to a new 2c rung, same
  rule that forced caesar_len8 onto WORDS_7_8). Hand-reviewed for
  length/first-letter balance across each cue's answer+distractor set.

### (c) `odd6` — the odd_one_out sibling

- **Task / surface.** "Which word is not like the others: w1..w6?" — the
  reused odd_one_out task at 6 words (5 from one category + 1 from
  another) instead of 4.
- **Probe label.** answer **position** (1–6), 6-class, shuffle-assigned,
  identical construction to reused odd_one_out (1–4).
- **Carrier analysis.** Same position-label dodge as antonym6 (2b
  odd_one_out: untrained 0.000). The category-specific risk: if the five
  same-category words share a morphological fragment the odd one lacks
  (e.g. a category of `-ing` verbs), that fragment is a **suffix /
  char-class carrier** (leak class 5/6) and the position becomes
  surface-legible. The 2c category vocab must be semantically but not
  morphologically clustered — the property 2b's CATEGORIES_2B (birds,
  tools, flowers) had by construction.
- **Dial.** family `odd_one_out`, `dial_name="n_words"`, `dial_value=6`
  (reused is the implicit 4). More words = more comparisons.
- **Screen-risk: LOW–MEDIUM.** Fires if a 2c category is morphologically
  clustered (suffix carrier) or if one category's words are systematically
  longer/rarer (magnitude-of-length proxy). Mechanism is a vocab-build
  defect; medium rather than low only because a 6-word draw touches more
  vocabulary and gives a coincidental shared fragment more chances to
  appear.
- **Oracle / surface.** oracle: position (1–6) of the odd word. surface_
  answer: the odd word.
- **Feasibility.** basis = all 6 words (shared_components over the
  category vocab), the odd_one_out shape. 2b odd_one_out used
  `holdout_frac=0.45, min_val_items=300, shared_components=True,
  n_probe=8000`. **Blessed override expected**: same 0.45 / 8000 figures.
- **Seed 20260819.** **Requires a new 2c wordlist** `wordlists_2c.
  CATEGORIES_2C` (≥6 members per category, ≥ ~8 categories), hand-reviewed
  against morphological clustering.

---

## 3. The three new families — RULED: F1/F2/F3 build, F4 reserve

Each candidate is a 2-rung family with a dial. Four were proposed so one
could be dropped; **Michael's ruling 2026-08-01: F1 (order_stat), F2
(seq_extrap), and F3 (pos_letter) are built; F4 (str_align) is the named
reserve** and enters only under §7's fallback. Risk ordering, lowest
first: order_stat, seq_extrap, pos_letter, str_align.

### Candidate F1 — `order_stat` (order statistics over a small set) · MEDIUM · BUILD

- **Family composability.** The k-th order statistic of a set is a rank
  interaction: non-additive in any single element, requiring a full
  pairwise comparison across the set (the odd_one_out composability story,
  with magnitude comparison in place of category membership). The dial
  (set size) scales the number of comparisons.
- **Construction (both rungs).** Print n distinct 3-digit integers
  (all drawn from [100, 999] so every element has the same token width —
  this kills the digit-count / magnitude-band carrier at the element
  level) in random order. Ask "which of these is the median?" Answer = the
  median value; **probe label = its position** (1..n) — the odd_one_out
  construction exactly (answer = the selected element, label = its slot).
- **Rung F1a `median5`** — n=5, label position 1–5 (5-class). Seed 20260820.
- **Rung F1b `median7`** — n=7, label position 1–7 (7-class). Seed 20260821.
- **CRT / carrier arithmetic.** The label is a **position, not a numeric
  value** — there is no modulus, nothing to CRT-decompose, no digit-local
  or value-mod-10 target. The decisive argument against a magnitude
  carrier: the median's position is **translation-invariant** — add any
  constant c to all n numbers and the ordering, hence the median's slot,
  is unchanged — so the label cannot be a function of absolute magnitude
  (leading digits, token length). It depends only on the relative order.
- **Screen-risk: MEDIUM.** Fires if a random net partially ranks by crude
  per-position magnitude proxies (leading digit) well enough to guess the
  median slot above chance. Same-width elements blunt this but do not kill
  it; median (not min/max) is chosen precisely because extremes correlate
  with gross magnitude and would leak harder — the median needs the full
  ranking. median7's 7-way rank is strictly harder to leak than median5's
  5-way.
- **Oracle / surface.** oracle: position (1..n) of the median. surface_
  answer: the median integer.
- **Feasibility.** basis = the set of printed numbers (shared_components).
  Blessed override expected: odd_one_out figures (holdout 0.45, n_probe
  ~8000); the numeric value space is huge so item count is not the
  constraint, the shared holdout is.
- **2b precedent.** sort3_mid (median of 3) existed in 2b's pool; this is
  the same statistic with a position label and a size dial.

### Candidate F2 — `seq_extrap` (sequence extrapolation) · MEDIUM · BUILD

- **Family composability.** Extrapolation is rule inference then one
  application then a modular reduction: infer the generating rule from
  the shown terms, apply it once more, reduce the result off the digit
  alphabet. Non-local in the shown terms; the dial is the **polynomial
  degree** of the generating rule (1 vs 2), which sets the depth of the
  difference chain the model must infer (first differences constant vs
  second differences constant). *The original F2b was geometric
  (a·rᵏ); Michael's ruling 2026-08-01 replaced it with the quadratic
  below — the geometric generator space was structurally small (16
  (a,r) pairs at the leak-safe magnitude bound), the feasibility weak
  point the proposal itself flagged.*
- **Rung F2a `arith_next`** — print an arithmetic run a, a+d, a+2d, a+3d
  (a ∈ [10,99], d ∈ [2,20]); ask for the next term. **Probe label =
  (a+4d) mod 7** (7-class). surface_answer = a+4d (the full next term, not
  printed). Seed 20260822.
- **Rung F2b `quad_next`** (ruled 2026-08-01) — print the four terms
  t_k = a + d·k + q·k² for k = 0..3 (a ∈ [10,99], d ∈ [2,20],
  q ∈ [1,9]); ask for the next term t_4 = a + 4d + 16q. **Probe label =
  t_4 mod 7** (7-class). surface_answer = t_4. Seed 20260823. The
  inference chain is one deeper than F2a's: three first differences
  (d+q, d+3q, d+5q) → two second differences (both 2q, constant) →
  recover the step → t_4 = t_3 + (d+7q). q ≥ 1 keeps the second
  difference 2q ≥ 2, well clear of the degenerate 0 that would collapse
  the rung into F2a. All first differences ≥ 3, so every printed run is
  strictly increasing (no ambiguous presentations). t_4 spans [34, 323],
  2–3 digit.
- **CRT / carrier arithmetic.** 7 is prime, coprime to 10: no CRT
  decomposition, not digit-local, not value-mod-10; t_4 mod 7 is uniform
  to within ±1 over the (a,d,q) box — counts 2198/2199 per class by
  enumeration of all 15,390 triples *(corrected 2026-08-02, wave-2
  review: this sentence originally said "exactly uniform (verified by
  enumeration)," but 15,390 = 7×2198 + 4 makes exact uniformity
  arithmetically impossible; the enumeration's actual output is the
  ±1 spread stated here)*. The next term itself is **not printed** — the model computes
  it — so its magnitude/last-digit are not on the surface. The residual
  carrier, named at full strength (sharper than "last term + inferable
  step"): because third differences of a quadratic vanish, **t_4 is a
  fixed linear functional of three printed terms — t_4 = 3t_3 − 3t_2 +
  t_1 exactly** (check: 3(a+3d+9q) − 3(a+2d+4q) + (a+d+q) = a+4d+16q),
  so the label ≡ (3t_3 − 3t_2 + t_1) mod 7 with no inference required.
  F2a has the same shape one order down: a+4d = 2(a+3d) − (a+2d), so its
  label ≡ (2t_3 − t_2) mod 7. The defense is not that the label is off
  the surface — it isn't — but that evaluating the functional requires
  the mod-7 residue of multi-digit printed tokens, which is the
  full-digit composition base7 cleared at untrained 0.000 (10ᵏ mod 7
  cycles with period 6, never 0; no digit suffix carries it), composed
  across **three** tokens rather than base7's one. A pencil-and-paper
  attacker gets the linear combination for free; the mod-7 of its inputs
  is the part a random projection has never expressed in this program's
  record. One more surface bit, disclosed: t_4 − a = 4d + 16q is even,
  so **t_4's parity equals t_0's parity** — legible from the first
  printed term's last digit. Parity is mod 2; gcd(2,7) = 1 and the label
  is a pure mod-7 residue, so the parity bit determines nothing about
  the 7-class label (it would only matter for a mod-14-style target,
  which this is not).
- **Screen-risk: MEDIUM.** Fires if a random net approximates the mod-7
  residues of the printed terms well enough to evaluate the 3-term
  functional — i.e., if base7's mechanism leaks at three-fold
  composition despite never leaking at one-fold. Note the **mod-7
  saturation** caveat — seq_extrap and the three rescues share the
  residue; a diversity concern for the battery, not a correctness one,
  ruled acceptable by keeping F2 in the build set.
- **Feasibility.** basis = the (a,d)/(a,d,q) generator reduced per the
  mod17 lesson (record the first printed term a as the basis component;
  holding out a starves the a→label lookup, and the joint-AND trap of a
  multi-component basis is avoided). The ruled quadratic **resolves the
  old weak point**: the (a,d,q) map is injective onto printed sequences
  (verified: 15,390 triples → 15,390 distinct 4-term runs), comfortably
  supporting 2000 probe + 500 eval; F2a's (a,d) space is 90×19 = 1,710
  distinct runs — **below the 2,500 default item target**, so F2a (not
  F2b) needs the sub_base8-style reduced-n_probe blessing (1,540 pairs →
  n_probe 1000 there; n_probe 1000–1200 here), certain, not
  contingent.

### Candidate F3 — `pos_letter` (positional letter arithmetic) · MEDIUM-HIGH · BUILD

- **Family composability.** A data-dependent gather: compute an index from
  two printed integers, then read the letter at that index of a printed
  string. Random projections are weak at variable-index gather — that
  weakness is the test. The dial is the index operation (sum vs product),
  which changes the index distribution.
- **Construction (both rungs).** Print a random 8-letter string S (uniform
  over a–z, so no English letter-frequency shortcut) and two integers
  i, j ∈ [1,8]. The read position is **interior only**: p =
  ((i∘j) mod 6) + 2, giving 1-indexed positions 2–7 (never the first or
  last letter). **Probe label = S[p]**, a letter a–z (nominally 26-class,
  `stratify_by_label` to hold classes across the split). Answer = the
  letter (the question asks for it directly, surface_answer = None).
- **Rung F3a `letter_sum`** — index op is i+j. Seed 20260824.
- **Rung F3b `letter_prod`** — index op is i×j. Seed 20260825.
- **CRT / carrier arithmetic.** The label is a letter, not a number — no
  modulus to decompose. But note honestly: the **position is trivially
  computable** from the printed i, j — `p = ((i+j) mod 6) + 2` is
  low-complexity arithmetic on two small printed integers, so position is
  NOT starvable, only the string is. The entire leak-resistance rests on
  the gather being hard for a random net. Interior-only positions dodge
  the first-letter carrier (leak class 6) and the final-BPE-chunk carrier
  (reverse_string's Exp-2 mechanism). Uniform random letters dodge the
  char-frequency shortcut. `(i∘j) mod 6` must be checked for **position
  uniformity**: if the index concentrates on a few slots, a fixed-position
  read ("always read slot 3") leaks; the product op i×j mod 6 is more
  concentrated than the sum (products cluster on 0 mod 6), which is the
  named risk for F3b specifically.
- **Screen-risk: MEDIUM-HIGH** (the riskiest of the built set → screen
  first). Fires if a random net gathers the letter at the computed
  position, OR if the position distribution concentrates enough that a
  fixed-slot read scores above chance. Precedent cuts both ways:
  reverse_string (last-letter-of-random-string) survived at 0.000 under
  starving with a **fixed** read position; here the position **varies** —
  that is the capability under test, and the screen adjudicates it.
- **Feasibility (basis ruled 2026-08-01: string-as-basis).** basis = the
  printed string S itself, per-string holdout — the N-token-basis shape
  (base12/collatz_step2 pattern: one component, huge value space). Every
  S is fresh-random over 26⁸ strings, so held-out val items always carry
  strings the probe never trained on, and a string→label lookup starves
  by construction. `stratify_by_label=True` (caesar precedent) keeps the
  26 letter classes populated on both split sides; otherwise default
  `SplitParams()`, N_PROBE 2000 — buildable now, no open design
  question. **Honest disclosure, carried into the spec text:** the
  position arithmetic p = ((i∘j) mod 6) + 2 is inherently unstarvable —
  i and j are printed and the map is low-complexity, so no holdout can
  remove position computability. What the starving basis removes is the
  string; what remains is exactly the gather-from-a-fresh-string
  capability the rung exists to measure, and the untrained screen is the
  arbiter of whether a random net expresses it.

### Candidate F4 — `str_align` (string alignment) · MEDIUM-HIGH · RESERVE (ruled)

> **PROMOTED 2026-08-02** under §7's fallback: pos_letter ejected as a
> full family at tier-1 (structural_abort ×8, PROGRESS 2026-08-02).
> **Label spaces amended by ruling 2026-08-02** (label-tail
> infeasibility: the frozen split's full-class-coverage requirement is
> unsatisfiable on the Binomial tails — hamming8 infeasible at its
> assigned seed, hamming12 outright): match counts above a cap are
> rejection-sampled out at generation, so the built label spaces are
> **0–5 exact (6-class) for hamming8** and **0–7 exact (8-class) for
> hamming12**, not the 9/13-class "nominal" ranges below. Oracle
> unchanged; feasibility table and ruling in PROGRESS 2026-08-02.

- **Family composability.** A position-wise alignment reduction: compare
  two equal-length strings position-by-position and count agreements. A
  2-D interaction over the pair, non-additive in either string; the dial
  is string length.
- **Construction (both rungs).** Two random strings over a **4-letter
  alphabet {a,b,c,d}** (not 26 — see arithmetic), equal length L. **Probe
  label = Hamming match count** = #{positions where S1[k]=S2[k]}, 0..L.
- **Rung F4a `hamming8`** — L=8, label 0–8 (9-class nominal). Seed
  20260826 (assigned only on promotion).
- **Rung F4b `hamming12`** — L=12, label 0–12 (13-class nominal). Seed
  20260827 (assigned only on promotion).
- **CRT / carrier arithmetic.** The reason for the 4-letter alphabet,
  shown explicitly: for a 26-letter alphabet, two random strings match at
  a position with probability 1/26, so **P(any match) is tiny and the
  label is ~always 0** — a degenerate label, unusable. The natural
  alignment statistic, longest common prefix length, is worse:
  P(LCP=0) = 25/26 ≈ 0.96 for random 26-letter strings, so LCP length is
  ~always 0 too. A 4-letter alphabet gives match probability 1/4 and a
  real spread: Hamming count over L=8 is Binomial(8, 1/4) ≈
  {0:.10, 1:.27, 2:.31, 3:.21, 4:.09, 5:.02, ≥6:.004} — modal at 2,
  effective ~5 classes, tails sparse (**class-imbalance flag**: labels ≥6
  are rare; the CP-bounded floor and label stratification must absorb
  this). No modulus, no CRT — the label is a count. The carriers to beat
  are **length-count legibility** (the count correlates with how many BPE
  chunks the two strings share) and the **shared-chunk carrier** (a
  4-letter alphabet produces frequent coincidental shared 2-grams, which
  the tokenizer emits as shared chunks a net can detect).
- **Screen-risk: MEDIUM-HIGH.** Fires if shared-chunk detection lets a net
  approximate the match count. The 4-letter alphabet that fixes the label
  degeneracy simultaneously **worsens** the shared-chunk carrier — the two
  pressures trade off, which is why this was rated drop-first and is now
  the ruled reserve. If promoted (§7), screen it first in its build wave.
- **Feasibility.** basis = the two strings (shared_components), override
  expected (holdout ~0.45, wide n_probe). Label imbalance may fail
  `min_holdout_values` on the sparse high-count classes — flag.

**The drop, RULED (Michael, 2026-08-01): build F1, F2, F3; F4 is the
named reserve.** The reasoning the proposal offered and the ruling
adopted: F1 and F2 are the two MEDIUM candidates with the cleanest
carrier arguments and direct survivor-mechanism precedent (position
label; off-alphabet modulus); of the two MEDIUM-HIGH candidates, F3 has
the stronger precedent (reverse_string) and a letter label that
diversifies the battery's label spaces, while F4's 4-letter-alphabet fix
fights its own shared-chunk carrier. The mod-7 saturation alternative
(dropping F2 for F3+F4) was considered and not taken; the caveat stays
ledgered in F2's screen-risk block. F4's full specification above stays
in the document at build rigor so promotion under §7 requires no new
design work.

---

## 4. Territories rejected on paper (the hygiene showcase)

Not registered, because the carrier arithmetic kills them before a screen
would — the base12 discipline applied forward instead of backward:

- **`base11` (would-be base_repr rung).** `N mod 11`: `10 ≡ -1 (mod 11)`,
  so `N mod 11` is the **alternating single-digit sum** of N's decimal
  digits — a low-complexity, single-digit-granularity carrier a random net
  can plausibly approximate. This is strictly easier to leak than base13's
  three-digit-**block** alternating rule (`10^3 ≡ -1 mod 13`). base11 is
  rejected for the same reason base5 was: the modulus rides a simple
  decimal-digit function. base13 is the base_repr 4th rung, not base11.
- **Calendar / month arithmetic mod 12.** Tempting as an
  "interval arithmetic distinct from clock24" family, but `(month + D)
  mod 12` is the **base12 CRT trap** in calendar costume: `12 = 3×4`, and
  `(m+D) mod 3 = (digitsum(m) + digitsum(D)) mod 3` while
  `(m+D) mod 4 = (m+D) mod 4` is fixed by the last two decimal digits of
  the printed m and D. Both congruences are computable from the printed
  digits and together pin `(m+D) mod 12`. Rejected.
- **Calendar / weekday arithmetic mod 7.** The obvious off-alphabet
  calendar modulus (`(weekday + D) mod 7`) is a **known 2b leaker** —
  "weekday mod 7" is in the methods-paper weak-systematic tier (fired
  0.06–0.26), and the design doc kept clock24 singleton precisely because
  "sibling weekday leaked." Not re-attempted. The net effect: the calendar
  territory has no leak-safe modulus available (7 leaks empirically, 12
  CRT-traps, 24 is clock24's, 60/365 decompose through mod-5/last-digit),
  so no calendar family is proposed.

---

## 5. Constraint compliance

| constraint | status across the 9 built rungs (+2 reserve) |
|---|---|
| k-class, k ∈ [5,26] | base13 13; antonym6/odd6 6 (k=6 ruled); median5 5, median7 7; arith_next/quad_next 7; pos_letter ≤26 (stratified) *(ejected at tier-1 2026-08-02)*; str_align **6/8 exact** *(promoted + label-tail caps ruled 2026-08-02; originally "9/13 nominal, imbalanced, flagged" as reserve)* — all in range |
| oracle-only generation (no models) | all — median/rank, modular/polynomial arithmetic, string indexing, Hamming count are pure oracles. The string-as-basis ruling removes pos_letter's only would-be tokenizer dependency: basis = the printed string itself, no BPE computation at generation time for any built rung |
| ~2000 probe + 500 eval items | value spaces support it everywhere except F2a `arith_next` (1,710 distinct (a,d) runs < 2,500 — takes the sub_base8-style reduced-n_probe blessing, §3 F2); elsewhere the constraint is the holdout, not item count |
| min 15 holdout values/component, min 300 val @ holdout 0.2 | **blessed-override flags:** odd6 and order_stat (shared-component, expect holdout ~0.45 + n_probe ~8000, the odd_one_out/roman_sum7 precedent); antonym6 (holdout override only if ANTONYMS_2C lands near its ~90-pair floor); F2a (reduced n_probe, above). base13, quad_next: default `SplitParams()` expected; pos_letter: default + `stratify_by_label=True` per §3 F3's own feasibility text *(wording corrected 2026-08-01, wave-1 build review — this row originally said plain default for pos_letter, contradicting §3 and this table's own k-class row, which already read "stratified")*. [reserve: str_align shared-component + label-imbalance flags stand] |
| 2c's own wordlists (never 2b frozen) | **APPROVED (ruling 3):** `wordlists_2c.ANTONYMS_2C` (≥ ~90 pairs, antonym6) and `wordlists_2c.CATEGORIES_2C` (≥ ~8 categories × ≥6 members, odd6), 2c-owned, hand-reviewed per §2's hygiene criteria. base13/order_stat/seq_extrap/pos_letter are numeric or random-string (no wordlist) |
| seeds continue from 20260817 | built rungs 20260817–20260825 in proposal order; 20260826–20260827 held for F4 on promotion only |

---

## 6. Build-sequencing (screen the riskiest first)

Tier-1 screening is the same-day redesign loop; screen the highest-risk
rungs first so ejections surface before wordlist/basis build effort is
sunk on rungs that would die anyway.

1. **First wave (MEDIUM-HIGH, ejection-likely):** F3 `pos_letter`, both
   ops — F3b `letter_prod` especially, for position concentration
   (products cluster on 0 mod 6). The string-as-basis ruling makes both
   rungs buildable immediately, so this wave can start first as well as
   screen first. If the family ejects here, F4 `str_align` is promoted
   (§7) and screened at the front of its own build wave, before the
   low-risk rungs are built.
2. **Second wave (MEDIUM):** F1 `order_stat`, F2 `seq_extrap` (arith_next
   + quad_next), odd6 (morphological-clustering risk in the new category
   vocab).
3. **Third wave (LOW):** base13, antonym6 — strong precedent, expected to
   pass; build once the risky slots have resolved so the final shape is
   known.

The two approved wordlists (ANTONYMS_2C, CATEGORIES_2C) gate odd6 and
antonym6 in waves 2–3, so start them in parallel with wave 1; they are
the long-pole build items. F4 is NOT built in the normal sequence — its
spec sits at build rigor in §3 so promotion costs no design time, only
generation + screening.

---

## 7. Margin and fallback if candidates eject

B2 simulated at **power@ρ=0.6 = 0.777** (sampled block-permutation,
n_sims=2000), against the 0.75 gate. The ruling reads that 0.777 as
"certification margin against MC noise and one attrition event."
Concretely, from the growth sweep on the record:

- **One rung attrites** (a family drops from 2→1 or 4→3): absorbed. The
  0.777 sits ~0.027 above the gate and ~2.7× the ±0.01 MC noise band; a
  single-rung loss perturbs the shape modestly and does not, on the sweep,
  drop below 0.75 on its own. Certification is still the full 5000-sim
  exact/sampled table on the **built** battery post-screen, per the
  ruling — the margin is not a substitute for that.
- **A full new 2-rung family ejects** (both rungs die at tier-1): NOT
  absorbed. 35 → 33 rungs moves into the neighborhood of the sweep's B
  shape (+7, 33 rungs, **0.722** — below the gate). This is the case the
  reserve covers, and the reserve is now named by ruling: **F4
  `str_align` enters** (seeds 20260826–20260827, spec at build rigor in
  §3), restoring a third new 2-rung family and the 35-rung shape, and
  the battery is re-screened and re-certified. Because screening order
  (§6) resolves the risky families first, a full-family ejection is
  detected while there is still time to promote F4 without disturbing
  the low-risk rungs.
- **Two families wobble** (e.g. one full-family loss + one rung): the
  reserve restores one; if the shape still misses 0.75 on the post-build
  table, that triggers a re-simulation and, per the design's own remedy
  clause, a further growth decision to Michael — not a silent proceed.

The honest statement: 0.777 is a one-attrition cushion, not a two-family
cushion. The four-candidate design exists so that one full-family ejection
is a promotion, not a re-open.

---

## 8. Rulings record (questions closed 2026-08-01)

The five questions this document originally posed, and how each was
ruled. All rulings Michael, 2026-08-01; the body above reflects them.

1. **Drop decision — RULED.** Build F1 (order_stat), F2 (seq_extrap), F3
   (pos_letter); F4 (str_align) is the named reserve (§3, §7). The
   mod-7-saturation alternative (drop F2 for F3+F4) was on the table and
   not taken; the caveat stays ledgered in F2's screen-risk block.
2. **pos_letter basis — RULED: string-as-basis.** Basis = the printed
   string S, per-string holdout (the N-token-basis shape); every string
   is fresh-random, so val items always carry unseen strings. The
   proposed BPE-chunk-at-computed-position basis is superseded; F3 is
   buildable now. The position arithmetic remains inherently unstarvable
   (i, j printed; the map is low-complexity) — disclosed in F3's
   feasibility block and to be carried into the spec's own
   `dumbest_baseline` text.
3. **New wordlists — APPROVED.** ANTONYMS_2C (≥ ~90 pairs) and
   CATEGORIES_2C (≥ ~8 categories × ≥6 members), 2c-owned
   (`wordlists_2c` pattern, 2b's frozen lists untouched), hand-reviewed
   per the §2(b)/(c) hygiene criteria (length/first-letter balance;
   no morphological clustering). In scope for the growth build.
4. **antonym6/odd6 label class — RULED: k = 6 confirmed** as the
   n_choices/n_words dial value for both siblings.
5. **seq_extrap second rung — RULED: quadratic replaces geometric.**
   `quad_next` (t_k = a + d·k + q·k², label t_4 mod 7, seed 20260823)
   takes F2b's slot; full carrier analysis in §3, including the exact
   linear-functional identity t_4 = 3t_3 − 3t_2 + t_1 found while
   verifying the sketch (a sharper statement of the residual carrier
   than the ruling's "last term + inferable step" — same mechanism
   class, named at full strength). The geometric rung's 16-generator
   feasibility defect is thereby closed; the one feasibility flag that
   moved in the process: F2a `arith_next`'s own space is 1,710 runs
   < 2,500, so it takes the sub_base8-style reduced-n_probe blessing.
