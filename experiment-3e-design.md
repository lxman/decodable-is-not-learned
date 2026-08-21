# Experiment 3e — Design Doc: Shortcut or Reversal? — Is the Sampled Channel's Item Structure Copy-Reachability or Entropy?

**Status: DRAFT — session 1 (design) of the three-session design |
build | freeze protocol** (boundary = context clear; Michael's pacing
ruling 2026-08-15, carried forward). Dials pinned by Michael
2026-08-21 in the design dialogue: (1) approach C — the committed
45-item repeat class resampled, a label-permutation primary on
which items fire, PLUS a specificity arm scoring the same draws
against each item's one-edit neighbour set (no extra sampling, no
new item file); (2) item set = the 45 len-4 repeat-class items of
the committed reverse_string battery, len-4 ONLY (len-5/6 gave 0
fires in 470,016 draws in 3d and keep their standing bounds); (3)
budget = 1b × 128 new seeds adjudicates, 410m × 64 new seeds
replicates non-gating; (4) primary statistic = exact hypergeometric
on the number of DISTINCT fired items that land in the 13
non-reachable items, given the fired-item total; (5) the neighbour
set = all single transpositions ∪ the two rotations by one; (6) the
specificity arm's competitors = the one-edit neighbours sharing the
reverse's first character AND with positional overlap to the input
no lower than the reverse's (so every named nuisance runs against
the reverse; the 11 (1,2)-mirror items have no such competitor and
sit out the arm, disclosed). The assembled design was approved the
same day; the overlap clause was added in the design session's
self-review, before any build. The build is a later session; the freeze is a third
session that opens adversarially (cold re-read; assignment: find
the class defect; fuzz the target-swapped scorer for totality per
the standing stop-#1 rule; attack the partition's degrees of
freedom) and ends at tag `exp3e-preregistered`. The instrument will
be `experiments/exp3e/`.

**Predecessor:** `experiment-3d-design.md` (tags
`exp3d-preregistered`, `exp3d-closed` — **STRUCTURED**: p =
1.622886e-04, |F| = 8, 7 of 8 fired items in the 45-item repeat
class against 1.86 expected, a 23.2× per-item rate ratio; 410m
p = .230 THIN non-gating). 3d's retrospective named this experiment
as its first successor: "the 23× concentration is equally
consistent with a boring story: low-entropy strings are more
probable a priori, and answers that share more characters with
their own input are more reachable by the copying the model already
does well … A successor that varies input-output overlap
independently of answer entropy would separate them." The
forward-note asymmetry rule (binding since Exp 1) is inherited
throughout: a fire is strong evidence; silence is weak evidence
bounded by budget.

---

## 1. The question

3d established that which items fire is forecastable from the
answer string alone, and that the forecast collapsed to a single
binary contrast: answers with a repeated character fire 23× more
often per item than all-distinct answers. 3d was designed to test
forecastability, not mechanism, and its §9 said so. This experiment
asks the mechanism question at the only grain the record supports:
**is the repeat-class concentration a property of the answer's
ENTROPY, or of its COPY-REACHABILITY from the input?**

The retrospective's phrasing ("input-output overlap") is
under-specified for reversal — every answer is a permutation of its
input, so character overlap is total by construction. Lining the
committed fires up against their inputs gives the precise version.
Every fire in the repeat class sits on an item where the reverse
coincides with a single copy error:

| input → answer | repeat pattern | the one edit that yields the reverse |
|---|---|---|
| `edce`→`ecde`, `dkmd`→`dmkd`, `whcw`→`wchw` | mirror (0,3) | swap the middle two |
| `pffq`→`qffp`, `dxxxxr`→`rxxxxd` | mirror (1,2); len-6 (1,4)+(2,3) | swap the outer two |
| `abaq`→`qaba`, `efea`→`aefe`, `bjbk`→`kbjb` | (0,2) | rotate right by one |
| `pmhm`→`mhmp`, `dpbp`→`pbpd`, `zivi`→`iviz` | (1,3) | rotate left by one |

whereas the repeat patterns (0,1) `aabc` and (2,3) `abcc` have NO
one-edit route to their reverse: same unigram entropy (C1 = 6.0),
one repeated character, but the reverse needs two transpositions —
exactly like an all-distinct string. The committed item file splits
the 45-item repeat class into **32 one-edit-reachable / 13 not**
(§5.1, computed from the item file, no draws touched). All 10
distinct fired repeat-class items across both sizes are in the
reachable 32 — P = .0202 under exchangeability. That number is
IN-SAMPLE MOTIVATION and is disclosed as such, exactly as 3d
disclosed its selection AUCs; nothing downstream cites it as
evidence.

So the "cheap to emit" reading has a concrete, model-free form:
**3d's 23× is the copy mechanism misfiring in its two most common
ways — off-by-one start, single swap — on precisely the strings
where that misfire equals the reverse.** And the partition delivers
the separation the retrospective asked for, without constructing a
single new item:

- reachable vs non-reachable repeat items hold entropy fixed
  EXACTLY (both classes: one repeated character, C1 = 6.0, 12
  distinct permutations) and vary copy-reachability;
- non-reachable repeat vs all-distinct items hold reachability
  fixed (both need two transpositions) and vary entropy.

The cell "one-edit-reachable AND all-distinct" cannot exist — for an
all-distinct string the reverse changes every position and no
single transposition or rotation reaches it — so the design is a
three-cell contrast, not a 2×2, and says so.

The specificity arm (§5.5) asks the sharper follow-up on the same
draws: among the one-edit outputs of a reachable item, is the
reverse SPECIAL — emitted more than the other copy misfires — or is
it emitted at the misfire rate, full stop?

## 2. Why 3e will not die its predecessors' deaths

- **3a's death (valueless verdict input):** every verdict input is a
  committed referent re-derived at analysis time or a quantity the
  analyzer computes from pinned bytes. The 45-item subset, its
  32/13 partition, every item's neighbour set and matched competitor
  set, m_min, and the exact null tables land IN THE TAG; the
  analyzer hash-checks the item file against the §4 pin before
  reading it (3c finding A, inherited) and resolves `answer_type`
  from the pinned file, never from a runner-written field (3d F1,
  inherited).
- **3d's mis-shaped power model:** the alternative is expressed in
  the partition's own terms — per-CLASS rates over the realized
  32/13 split — never as per-item concentration on the 10 committed
  fired items (3d retrospective §3, the sixth lesson). Per-item
  heterogeneity enters the power model as dispersion within class,
  not as the alternative's shape.
- **Hot-item dominance (item 123 'ecde' carries 7 of the 19
  repeat-class committed fires):** the primary counts DISTINCT fired
  items, not fires, and its null is label exchangeability ACROSS
  items conditional on the fired-item total — a single hot item is
  one item. Fire counts enter only a named secondary with a null
  that conditions on every item's own count (§5.4).
- **2c's tie collapse:** the primary has no ranks and no ties; it
  is a 2×2 count with an exact hypergeometric null.
- **3d F2 (self-consistent coverage):** gate 1's coverage is pinned
  to the literal 45 × 64 = 2,880 draws per size, not to whatever the
  re-derivation happened to produce.
- **Selection circularity:** the partition was chosen after seeing
  the 10 committed fired items (§1), and this is disclosed as
  in-sample motivation. The confirmatory statistic sees only NEW
  draws. Overfitting the 10 costs power, never validity.
- **The Schaeffer trap:** the outcome event is the same verified
  full-string fire 3/3c/3d used — no new metric, no new threshold.
  The specificity arm applies the same criterion to a different
  target string, and its known-answer gate is that with target =
  answer it reproduces the committed fire addresses exactly.

## 3. The matrix

One rung, two sizes, one item subset, new seeds only:

| cell | items | committed draws per item (seeds) | new seeds | new draws |
|---|---|---|---|---|
| reverse_string/1b/trained | 45 | 2,560 (0–39) | 40–167 (128) | 368,640 |
| reverse_string/410m/trained | 45 | 1,792 (0–27) | 28–91 (64) | 184,320 |

- 64 draws per item per seed; T = 1.0, untruncated, float32,
  MAX_NEW_TOKENS 12; the same sampler as exp3/3c/3d (a further
  seed-extension of exp3's frozen sampler, namespace `exp3`,
  per-item substreams — so restricting to 45 items changes no
  stream: each (cell, seed, item) substream is derived independently
  of batch composition, and the committed streams for these 45 items
  are exactly what gate 1 re-derives). Module provenance asserted
  byte-identical at run time.
- Per-item new budget: 8,192 draws (1b), 4,096 draws (410m).
  552,960 new draws total, ~3.5 h on the Mac mini.
- **The 45 items** = every len-4 eval item whose answer carries a
  repeated character (the 3d freeze record's "repeat class", C1 =
  6.0). No palindromic inputs exist in the battery (asserted at
  build; a palindrome's reverse is its copy and would have to be
  excluded).
- **Partition** (§5.1): 32 reachable — 17 by a single transposition
  (mirror patterns (0,3): 6, (1,2): 11) and 15 by a rotation
  (patterns (0,2): 10, (1,3): 5) — and 13 non-reachable (patterns
  (0,1): 8, (2,3): 5). The 13, verbatim: items 9 `ndqq`, 46 `eexw`,
  78 `hhep`, 143 `qsee`, 148 `eewc`, 154 `ddfv`, 361 `cpbb`, 367
  `dwtt`, 415 `ffre`, 435 `bbqp`, 439 `wwtj`, 463 `wwra`, 489 `ntjj`
  (inputs shown; answers are their reverses).
- **The all-distinct len-4 items (149) are NOT resampled.** Their
  committed record (1b: 381,440 draws, 3 fires; 410m: 267,008
  draws, 2 fires) supplies the entropy contrast descriptively
  (§5.4) and the reversal-proper residual rate (§6). A deepening
  tranche on them is a separate decision, not part of 3e.
- rev_string7, len-5 and len-6 are excluded; every standing bound
  is untouched.

**The committed repeat-class fires (the complete in-sample set,
verbatim, with the partition label):**
1b — item 123 `ecde` (seeds 5, 8, 13, 19, 36; transp), 447 `dmkd`
(seed 13 twice, 17; transp), 320 `wchw` (15; transp), 153 `qffp`
(29; transp), 179 `aefe` (30; rot), 283 `qaba` (25; rot), 348
`mhmp` (20; rot), 430 `pbpd` (20; rot) — 14 fires on 8 items.
410m — 123 `ecde` (8, 24; transp), 174 `kbjb` (15; rot), 226 `iviz`
(6; rot), 283 `qaba` (27; rot) — 5 fires on 4 items.
Non-reachable: 0 fires in 33,280 (1b) and 23,296 (410m) committed
draws. The texture the partition must survive out of sample: 10 of
10 distinct fired items reachable, where 32/45 would put ~7 of 10.

Committed class rates (in-sample, used only to size the tranche and
the power model): 1b repeat class 14/115,200 = 1.215e-4 per draw;
reachable 14/81,920 = 1.709e-4; non-reachable 0/33,280 (CP95 ≤
9.0e-5); all-distinct len-4 3/381,440 = 7.86e-6. 410m: repeat class
5/80,640 = 6.20e-5; all-distinct 2/267,008 = 7.49e-6.

## 4. Referents — every input, a committed value

To be pinned at build (sha256 list in the doc at freeze):
- The reverse_string item file (2b battery), its sha (3d's
  `ITEMS_SHA_PIN`, inherited by value and re-asserted), and the
  identity of the 45-item subset as an explicit index list with its
  own sha.
- The partition: every one of the 45 items' neighbour set N(x),
  reachability label, matched competitor set M(x), printed and
  sha-pinned.
- The 19 committed repeat-class fire addresses (exp3 + 3c + 3d
  verdict records) and the full 26-address committed set the scorer
  gate reproduces.
- 3d's per-seed fire tables and pooled rates (the base the new
  tranche pools with).
- The standing twin record: 0 fires / 576,000 committed twin draws
  (3c's re-assertion, 3d's re-assertion) — the contamination
  referent; NO new twin draws are taken.
- Gate-1 referents: 3d's committed streams at **1b seed 20** and
  **410m seed 24**, restricted to the 45 items — seeds chosen
  because each carries repeat-class fires (1b: items 348 and 430;
  410m: item 123), so the re-derivation must reproduce fires
  byte-for-byte through the PRODUCTION subset path (3c's lesson:
  test the path that runs, not a sibling).
- The verify criterion: 3c's ratified total wrapper
  (`load_verify_3c` semantics), inherited verbatim; the
  target-swapped scorer (§5.5) calls the same function with a
  different second argument and adds no branch on the draw side.
- The leak-void rule: 3c's (answer casefold-present in the rendered
  prompt → fire void), applied identically to competitor strings.
- ctrl_copy's committed T = 1.0 sampled verified rates (410m .7992,
  1b .8413) as the scorer's second known-answer referent: with
  target = the copy answer, the scorer must reproduce them EXACTLY
  (they are the same computation).

## 5. Operationalization

### 5.1 The partition (predictor provenance — disclosed in-sample)

For an input string x with |x| = L and reverse a = rev(x):

- **Neighbour set N(x)** = { every string obtained from x by one
  transposition of two unequal characters } ∪ { x rotated left by
  one, x rotated right by one } \ { x }. For len-4 single-repeat
  inputs |N(x)| = 7.
- **Reachable** ⇔ a ∈ N(x). **Non-reachable** otherwise.
- **Matched competitor set M(x)** = { s ∈ N(x) \ {a} : s[0] = a[0]
  and ov(s, x) ≥ ov(a, x) }, where ov counts positions at which two
  strings agree — the one-edit outputs that begin with the same
  character as the reverse and are at least as copy-like. Over the
  32 reachable items, by sub-pattern: (0,2) rotation items |M| = 1
  (10 items; e.g. `abaq`→`qaba` vs `qbaa`); (0,3) mirror items
  |M| = 2 (6 items; `edce`→`ecde` vs `edec`, `eecd`; the rotation
  `eedc` is dropped by the overlap clause); (1,3) rotation items
  |M| = 3 (5 items; `pmhm`→`mhmp` vs `mphm`, `mmhp`, `mpmh`); (1,2)
  mirror items |M| = 0 (11 items, incl. `pffq` — the only
  first-character match `qpff` is a rotation with lower overlap than
  the reverse). The arm therefore runs on 21 of the 32 reachable
  items; the 11 sit out with their reverse-vs-`qpff`-type counts
  printed descriptively, no test.

Rationale for the neighbour set, frozen now: a copy mechanism's two
elementary errors are starting at the wrong position (rotation by
one, either direction) and swapping two characters (transposition,
adjacent or not — the committed fires require both: `edce`→`ecde` is
adjacent, `pffq`→`qffp` is outer). Rationale for first-character
matching: exp3's mass arm found position-1 emission mass
primacy-shaped (interior input characters out-mass the input-final
character ~4:1), so strings that begin with different characters
carry different position-1 mass for reasons that have nothing to do
with reversal; matching removes that nuisance. The remaining
positional effects (which character is emitted second, third) are
exactly what "reversal-directed" means behaviourally and are not
matched away.

**Variants considered and rejected, with their classifications
printed at freeze so the choice is visible:** (i) adjacent
transpositions only — reclassifies the (1,2)-mirror items (11, incl.
`pffq`) as non-reachable; (ii) rotations only — drops all 17 mirror
items; (iii) Hamming or Damerau–Levenshtein distance — a rotation
is Hamming-4 from its source, so edit distance does not express the
copy-error notion at all. The build prints the 45-item
classification under (i) and (ii) beside the frozen one. No
builder discretion remains: N(x) is a total function of x, frozen
here.

### 5.2 The outcome (fired sets)

Per cell, the new-fired set F = the set of items (of the 45) with
≥ 1 new verified non-void full-string fire across that cell's new
seeds. Verification = the inherited total wrapper; void rules =
3c's, unchanged. Multiplicity does not change F — F is a set;
per-item counts are disclosed descriptively and feed only §5.4.

### 5.3 Primary statistic (1b adjudicates)

Let N = 45, K = 13 non-reachable, n = |F| (the fired-item total at
1b), X = |F ∩ non-reachable|. Under H0 — reachability does not
matter; the label is exchangeable across items with respect to
firing — X is Hypergeometric(N = 45, K = 13, n), conditional on n.

  p_low  = P(X ≤ X_obs)   (SHORTCUT direction: non-reachable under-fires)
  p_high = P(X ≥ X_obs)   (ANTI direction)

α = .05, one-sided each way; each directional world calibrates at
≤ .05 (discreteness makes the realized size smaller) and the two
together spend ≤ .10 of null probability, not "exactly α" — 3d §7's
corrected calibration sentence, applied in advance; the build
prints the realized sizes at the expected n. Exact, closed-form,
no Monte Carlo. The table, fixed by N and K alone and
therefore printable now:

| n | p_low at X = 0 | X = 1 | X = 2 |
|---|---|---|---|
| 8 | .0488 | .2518 | .5797 |
| 10 | .0202 | .1345 | .3917 |
| 12 | .0079 | .0662 | .2411 |
| 15 | .0016 | .0194 | .0980 |
| 20 | .0001 | .0015 | .0131 |
| 25 | <.0001 | <.0001 | .0007 |

**m_min = 8**: the smallest fired-item total whose best-case
arrangement (X = 0) rejects; at n = 7, X = 0 gives .0742. Expected
n at 1b is ~24–28 (§7), so m_min is not the binding constraint, and
the table shows the test's real shape: a rejection requires the
non-reachable 13 to be nearly silent while the reachable 32 fire
broadly.

Conditioning on n IS the rate adjustment: the primary asks only
WHERE the fires land, never how many there are, so a tranche that
fires more or less than the committed rate predicted changes
nothing about the test's validity.

### 5.4 Named secondaries (non-gating)

- **410m replication:** the identical test on the 410m new-fired
  set. Expected n ≈ 10 (§7); power thin and disclosed; the result
  attaches to the verdict as an annotation, never a gate.
- **Count-weighted contrast:** T_c = total new fires on
  non-reachable items; null = the label permutation over the 45
  items (choose which 13 are "non-reachable") conditional on every
  item's OWN new fire count — exact by DP over items (a subset-sum
  on small integer weights), so hot items produce a correspondingly
  heavy null. Reported with its exact p_low. This is the more
  powerful statistic when multiplicity is informative and the more
  fragile one when a single item dominates; the primary is the
  item-level one for that reason.
- **Sub-class texture, descriptive:** fired-item fractions and
  per-class rates for transposition-reachable (17), rotation-
  reachable (15), non-reachable (13), with CP95 on each. Whether the
  two reachable mechanisms fire alike is disclosed, not tested.
- **The entropy contrast, descriptive and pooled:** non-reachable
  repeat items (new + committed draws) vs all-distinct len-4 items
  (committed draws only): both two-edit, entropies 6.0 vs 8.0 bits.
  Rates with CP95; the scramble-prior factor between the classes
  (12 vs 24 distinct permutations, a 2× a-priori difference) printed
  beside them. Event-starved at any budget 3e can afford; it ships
  as bounds.
- **Persistence, descriptive:** how many new fires land on the 10
  previously-fired items; the rate on never-fired reachable items
  separately. 3d retired persistence as an explanation; the
  disclosure continues.
- **Updated pooled rates:** per-cell, per-class pooled rates and
  CP95 over all seeds; every zero a CP bound.

### 5.5 The specificity arm (named secondary, same draws)

For every reachable item, the same verify criterion is applied to
each string in M(x) as the target, over the same new draws. Let
r_i = new emissions of the reverse a_i, c_i = the vector of new
emissions of each matched competitor, n_i = r_i + Σ c_i.

**Null (designation exchangeability):** under "the reverse is
nothing special among one-edit outputs that begin the same way,"
which of the 1 + |M_i| matched strings is designated "the reverse"
is exchangeable with respect to its emission count. The null
distribution of T_s = Σ_i r_i is generated by designating, for
each item independently, one of its 1 + |M_i| count values
uniformly at random — exact by DP over items, conditional on every
item's observed count vector. One-sided p = P(T_s ≥ T_s,obs).
Conditioning on the count vectors means an item where one
competitor happens to be an English word and soaks up emissions
produces a correspondingly heavy null — the per-item string prior
is not assumed away.

**Direction of the known nuisances:** by construction of M(x),
every matched competitor begins with the reverse's first character
(position-1 mass matched away) and has positional overlap with the
input ≥ the reverse's (copy-overlap neutral or favouring the
COMPETITOR — e.g. `abaq`: reverse `qaba` overlap 0 vs competitor
`qbaa` overlap 2). The per-item string prior is handled by the
conditioning above. No named nuisance favours the reverse. A
rejection is therefore conservative evidence that the channel is
reversal-directed beyond copy misfire; a non-rejection is read at
the arm's disclosed event total and no further.

**Outcomes, annotated onto the verdict line, never gating:**
DIRECTED (p ≤ .05) — even among one-edit outputs the reverse is
over-represented; MISFIRE-RATE (events ≥ m_s,min, no rejection) —
the reverse is emitted like any other copy error, with the
reverse-share estimate and CI printed; SPARSE (events < m_s,min).
m_s,min = the smallest matched-event total whose best case rejects,
computed exactly at build from the |M| structure (10 items at θ =
1/2, 6 at θ = 1/3, 5 at θ = 1/4).

**Known-answer gates for the scorer, both before the tranche:**
(a) with target = answer, scoring the committed exp3/3c/3d draws for
the 45 items reproduces the 19 committed repeat-class fire addresses
exactly — no more, no fewer, same (item, seed, draw); (b) with
target = the copy answer, scoring ctrl_copy's committed T = 1.0
draws reproduces r = .7992 / .8413 exactly. A scorer that fails
either does not run on new draws.

**S2, descriptive:** for the 13 non-reachable items (new draws) and
the 149 all-distinct items (committed draws), emissions of the
reverse vs emissions of its first-character-matched one-edit
neighbours (|M| = 2 or 3; for `abcd`: `dabc`, `dbca`). The
copy-misfire reading predicts the neighbours dominate by a wide
margin; printed as counts with CP bounds, no test.

## 6. Preregistered verdict tree

Adjudication is the 1b primary statistic alone.

- **SHORTCUT** — p_low ≤ .05. The claim: within the repeat class,
  at identical entropy, fires concentrate on items whose reverse is
  one copy-edit from the input. What it licenses, written now:
  3d's STRUCTURED stands as a forecast result, but what it forecast
  is emission cost — the copy mechanism's misfire landing on the
  right string — not graded reversal competence. The essay's
  three-signature case for reversal at ≤ 1b must be restated:
  signatures 2 and 3 are carried by the all-distinct residual
  (1b: 3 fires / 381,440 committed draws, 7.86e-6, CP95 printed at
  verdict), which is the reversal-proper rate, and the "famous
  zero" paragraph says that most of the sampled channel's rare
  successes are copy errors that happen to be correct. Annotated
  from §5.5: "(misfire-rate)" if the specificity arm fails to
  reject — the reverse is not special even among misfires — or
  "(directed)" if it rejects — reachability gates WHICH items can
  fire, but within them the reverse still beats the other misfires.
- **NO-SHORTCUT** — n ≥ m_min and no rejection in either direction.
  Reachability does not drive the concentration at this resolution;
  the entropy reading survives (low-entropy strings are easier to
  reverse per se, or more probable a priori — 3e cannot split those
  two and says so); the upper CP bound on the non-reachable/
  reachable rate ratio is the headline number. The specificity
  annotation attaches as above.
- **ANTI-SHORTCUT** — p_high ≤ .05. Non-reachable items fire MORE.
  Would falsify the copy-misfire reading outright and is reported
  with the same prominence; no story is prepared for it.
- **UNINFORMATIVE** — n < m_min = 8. Retracts nothing: 3d's
  verdict, the committed rates, and the partition's in-sample
  texture all stand; the tranche's fires and silences ship as counts
  and CP bounds regardless.
- **THIN qualifier, frozen now:** any verdict reached on n ≤ 10
  carries the label THIN — at n ≤ 10 a rejection is possible only
  with X = 0, which is a fragile arrangement. Expected n at 1b is
  well above this (§7); the label exists for the case where the
  tranche under-fires.

Order of verdict operations mirrors 3d §6: projection ledgered
first, then the frozen analyzer runs ONCE on Michael's go; the
per-class fire table with verbatim (item, seed, draw) addresses is
the headline; the world label follows the tree mechanically; the
specificity annotation follows its own tree mechanically.

## 7. Power, honestly

All numbers are build obligations; the doc freezes their FORMS, and
the alternative's SHAPE is fixed here per the sixth lesson:

- **The alternative is class-level.** H_shortcut: reachable items
  fire at the committed reachable-class rate (1b 1.709e-4 per
  draw), non-reachable at the committed all-distinct rate (7.86e-6)
  — "reachability is the whole story." H_half: non-reachable at the
  geometric mean of the two. H0: every item at the committed
  repeat-class rate (1.215e-4).
- **Within-class heterogeneity enters as dispersion, not shape:**
  per-item rates drawn from a gamma with the class mean above and
  a dispersion fitted to the committed per-item counts in the
  reachable class (one item at 5, one at 3, six at 1, twenty-four
  at 0 over 2,560 draws each); a homogeneous variant reported
  beside it. Heterogeneity lowers the number of DISTINCT fired
  items for a given fire total, which is the quantity the primary
  runs on — so it is the direction that costs power and must be
  modelled.
- **Back-of-envelope now, to be replaced by the build's tables:**
  at 8,192 draws per item, a homogeneous reachable item fires with
  P = 1 − exp(−1.40) = .75, so n ≈ 24 reachable + ≈ 0.8
  non-reachable under H_shortcut; under H0 each item fires with
  P = .63, n ≈ 28, X ≈ 8.2 expected. The table in §5.3 puts p_low
  at X ≤ 1, n ≈ 25 below .0001. Power is not the constraint here;
  what the build must establish is the minimum detectable rate
  ratio at .75 power and the null calibration at exactly α.
- **410m:** at 4,096 draws per item and the committed 410m rates,
  n ≈ 10 under either hypothesis; P(n ≤ 10) is a build-table entry
  and the replication is disclosed thin in advance.
- **Specificity arm:** power as a function of the reverse-share
  under H_directed ∈ {.6, .75, .9} against θ ∈ {1/2, 1/3, 1/4}, at the
  matched-event totals implied by the committed reachable rate
  (the competitors' rates are UNKNOWN — no committed draw has ever
  been scored against them — so the arm's event total is a
  scenario, and the build prints it as one).
- If any computed power lands under the program's .75 bar at its
  named alternative, the experiment is DECLARED UNDERPOWERED IN
  ADVANCE and runs anyway with that concession printed (1c
  precedent); the tranche buys rate resolution regardless.

## 8. What the dumbest baseline achieves

- **Entropy-only** (3d's C1) assigns every one of the 45 items the
  same value, 6.0 bits. Under the primary it has NOTHING to say:
  the test lives entirely inside the class C1 cannot split. "Beats
  entropy" is therefore structural, not a comparison that can go
  noisy — the same move 3d made against length.
- **Uniform** predicts X ≈ 13n/45 — the null itself.
- **Persistence** predicts fires on the 10 committed items, all
  reachable; it is excluded as a competing forecaster on 3d's
  grounds (it requires having sampled), and the never-fired
  reachable items' rate (§5.4) shows directly whether the partition
  forecasts beyond them.
- **Scramble prior** (uniform over the 12 distinct permutations of
  the multiset) predicts equal rates for reachable and
  non-reachable items — the null again — and a 2× repeat/all-
  distinct ratio where 3d observed 23×.

## 9. What 3e does not claim

- Nothing about mechanism beyond the printed partition. "Reachable
  items fire" is a statement about a frozen structural property of
  the input–answer pair and a frozen event, not about circuits.
  "Copy misfire" names the reading the partition was built to
  test; a SHORTCUT verdict supports that reading against the
  entropy reading and no further.
- No re-adjudication of 3d (STRUCTURED stands — the functional
  forecast; 3e asks what it forecast), nor of 3b/3/3c or any closed
  experiment.
- No cross-family generalization: reverse_string, len-4, Pythia
  410m/1b, T = 1.0 untruncated, these budgets only. len-5/6 and
  rev_string7 keep their bounds untouched.
- The entropy contrast (§5.4) ships as bounds, not a result; 3e
  cannot separate "low-entropy strings are easier to reverse" from
  "low-entropy strings are more probable a priori," and does not
  try.
- The specificity arm annotates; it gates nothing, and a DIRECTED
  annotation is a statement about first-character-matched one-edit
  competitors, not about all strings.
- Silence on the 13 non-reachable items is bounded evidence, never
  a zero: every silent class ships with its CP95.

## 10. Run plan

Order, frozen:
1. Session 2 builds `experiments/exp3e/` (partition module with
   printed classification + variants; analyzer with the
   hypergeometric primary, the DP count-weighted null, the
   designation-exchangeability DP, loaders with sha pins; the
   target-swapped scorer and its two known-answer gates; the
   subset-aware seed-extension runner; fixtures + mutation battery
   + full-shape world terminals + determinism fixture; power
   tables). Session 3 freezes adversarially; tag
   `exp3e-preregistered`.
2. **Scorer known-answer gates (no model contact):** §5.5 (a) and
   (b) on committed draws. Both must PASS before any sampling tier
   will run; the runner refuses otherwise.
3. **Gate 1 (first model contact, on Michael's launch word):** byte
   re-derivation of 3d's committed 1b seed-20 and 410m seed-24
   streams through the production 45-item path — 2,880 draws per
   size, coverage pinned to exactly that number, the three fires
   (348, 430 at 1b; 123 at 410m) reproduced at their committed
   (item, draw) addresses. Zero tolerance: any diff halts the
   campaign.
4. **Tranche:** per-cell, per-seed-block (blocks of 16 seeds =
   46,080 draws, the durable commit unit), 410m then 1b, blocks
   ascending; every raw draw stored; per-seed convenience tallies
   beside them, recomputed and refused on disagreement by the
   analyzer. Commit + push per block per the standing cadence.
5. Projection ledgered; frozen analyzer runs ONCE on Michael's go;
   verdict + retrospective; close-out propagation (essay §
   signature-2/3 wording, `experiments.md`, methods paper if a
   lesson earns it).

Budget: ~3.5 h sampling + minutes for gate 1, Mac mini MPS,
tier-per-process as always. Invariant, restated from 3c/3d and
carried: **no new sampled quantity for any real cell before the
tag**; the scorer's known-answer gates touch committed bytes only.

## 11. Process rules carried forward

Three-session protocol; adversarial freeze with the standing
assignments (class defect; totality fuzz of the target-swapped
scorer over the emission alphabet; the partition's degrees of
freedom as the named attack surface — the build prints the variant
classifications so the freeze can check that no variant was
quietly preferred); ONE pre-committed change, currently UNSPENT;
per-block commit+push with Michael's launch authorization; every
zero a CP bound; no interval-coverage criteria on extrapolations;
projection before analysis, graded in the retrospective; verbatim
fire disclosure with (item, seed, draw) addresses for the reverse
AND for every matched competitor emission; known-answer
confirmation gates before the campaign (gate 1 and both scorer
gates); class-level power modelling (the sixth lesson, first
applied here by design rather than in retrospect).

## Open items before freeze (build-session obligations)

1. The 45-item index list, the 32/13 partition, N(x) and M(x) for
   every item, the variant classifications (i)/(ii), all printed
   and sha-pinned; the no-palindrome assertion.
2. m_min (= 8, to be recomputed by the analyzer), the exact
   hypergeometric table, THIN_MAX = 10; m_s,min for the
   specificity arm.
3. The DP implementations for the count-weighted null and the
   designation-exchangeability null, each with a brute-force
   enumeration fixture on a small synthetic instance.
4. Power tables at H_shortcut / H_half / H0 with gamma dispersion
   and homogeneous variants; minimum detectable rate ratio at .75;
   null calibration; 410m P(n ≤ 10); specificity scenarios.
5. The §4 sha pin list, complete; the 19-address and 26-address
   committed fire sets as literals.
6. Sampler module-provenance assertion vs 3d (byte identity); the
   subset path's stream seeds asserted equal to 3d's committed
   `stream_map_3d.json` entries for the 45 items at the gate-1
   seeds.
7. Gate-1 coverage literal (2,880 per size) and the three expected
   fire addresses, pinned.
8. Fixture suite + mutation battery + full-shape world terminals
   (every world and annotation reachable) + determinism fixture,
   per house standard.
