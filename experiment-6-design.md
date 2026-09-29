# Experiment 6 — Design Doc: The Second Battery — Does the Item-Order Forecast Hold on the Field's Own Emergent Tasks?

**Status: built, adversarially frozen, final-reviewed; ratified by Michael
2026-09-29 ("ratified"), all recommendations of
`experiments/exp6/RATIFICATION.md`. Final validation precedes the tag.
Session 1 was written 2026-09-27 on his word ("Yeah, let's do it"):
BENCHMARK-DERIVED tasks, FRESH generated items, ALL FOUR outcome families
in ONE preregistration. Dials a–u were approved that day. The original
design admitted eighteen candidate rungs from eleven tasks; the build
excluded `logic_grid` under the admission rule. The ratified battery is
SEVENTEEN rungs from TEN tasks. The amendments below incorporate B-1–B-36,
N-1–N-16 and D-1–D-16/O-1–O-5. No model has read an item of this battery.
A prototype test loaded the same SmolLM3 endpoint weights twice on
2026-09-28, without a tokenizer, forward pass or score (§2).**

The program's forecast line (2g–2n) closed with eight sealed forecasts
on four outcome families from two predictor families, every one of
them on a single battery: 2c's 34 synthetic rungs, built by this
program. The essay says "still one battery" at each step. That is the
limit this experiment removes or confirms. It is a DECISION experiment:
its two clean outcomes license opposite things (§6), and the stake,
stated by Michael on 2026-09-27, is whether the thesis has anything
substantial to say.

## 1. The question

**Do the sampled outputs of a one-billion-parameter model forecast the
order in which a larger model's training makes individual items
emittable, on tasks this program did not invent — the BIG-bench tasks
that Wei et al. (2022) classify as emergent — across four outcome
families?**

Two predictors, four outcome families, eight tests, each 2g's test
verbatim (within-stratum Somers' D between the predictor's per-item
count and the outcome's per-item count, mean over rungs, permutation
within rung × stratum; fires iff T ≥ .10 and p < .01):

- **Predictor A** — Pythia-1b, 256 draws per item (2k's shape).
- **Predictor B** — OLMo-2 1B stage-1 endpoint, 64 draws (2i's shape).
- **Outcomes** — the stage-1 training trajectories of SmolLM3-3B,
  OLMo-2 7B, OLMo-2 13B and Comma v0.1-1T, each on the grid this
  program already committed for it (26, 21, 16 and 24 checkpoints).

**Per-predictor status.** A test is EVALUABLE if it reads at least
three rungs (§4). For predictor P let E_P be its number of evaluable
families and F_P the number on which it fires:

| status | rule |
|---|---|
| **U** (undetermined) | E_P < 3 |
| **H** (holds) | E_P ≥ 3 and F_P ≥ 3 |
| **S** (split) | E_P ≥ 3 and F_P = 2 |
| **F** (fails) | E_P ≥ 3 and F_P ≤ 1 |

**Worlds** (after INSUFFICIENT_DATA), all sixteen status pairs (A, B)
enumerated — 2n's process note 1 applied in advance:

| world | pairs (A, B) |
|---|---|
| **GENERAL** | (H, H) |
| **PYTHIA-ONLY** | (H, S) (H, F) (H, U) |
| **OLMO-ONLY** | (S, H) (F, H) (U, H) |
| **SPLIT** | (S, S) (S, F) (F, S) |
| **BATTERY-BOUND** | (F, F) |
| **UNDETERMINED** | (S, U) (U, S) (F, U) (U, F) (U, U) |

The primary is per family with a naming rule, not pooled: 4c's pooled
U of .45 hid two sealed runs that disagreed in sign. The per-family
T's, p's and per-rung D's are printed in every world.

**What is not α-calibrated, stated.** Each test runs at α .01 behind an
effect bar. The eight tests share items and predictors, so they are not
independent, and no family-wise figure is claimed; the union of the
worlds is not α-calibrated (3d's calibration lesson). The guard against
a shared artifact firing all eight at once is the strata (§4), not the
count of tests.

## 2. What is known and what is sealed (disclosure)

**Known to the designer:** the whole record through Experiment 5b —
the eight sealed forecasts on 2c's battery (.17, .20, .22, .18, .17,
.25, .16, .21), their per-rung texture (the base-8 pair the top locus
on every outcome; the cross-family component arithmetic-heavy; the
antonym sign split), 2j's mechanism reading, 2k's density result, and
the general texture of all four outcome trajectories as read on 2c's
battery (transient verification, checkpoint-local collapses on
SmolLM3 and Comma, OLMo-2 13B's battery-wide collapse at step 1000).

**Not known to anyone in this program:** any output of any model on any
item of the new battery. The four outcome trajectories have been read
on 2c's items only. The predictors do not exist yet.

**The design session's outside reads (2026-09-27), logged:** Wei, Tay,
Bommasani et al., "Emergent Abilities of Large Language Models"
(arXiv 2206.07682, TMLR 08/2022), the PDF fetched once and its text
extracted locally — Appendix E read in full; the READMEs of twenty-five
BIG-bench tasks on GitHub (`google/BIG-bench`, `main`): modified
arithmetic, word unscrambling, IPA transliterate, word sorting, unit
conversion, periodic elements, repeat copy logic, dyck languages,
multistep arithmetic, object counting, boolean expressions, logical
deduction, ASCII word recognition, geometric shapes, tracking shuffled
objects, navigate, temporal sequences, date understanding, CS
algorithms, hyperbaton, logic grid puzzle, logical sequence, unit
interpretation, arithmetic, odd one out. No Hub read, no tokenizer
load, no weight, nothing written under `experiments/`.

**The field's classification, quoted.** Wei et al. classified 210
BIG-bench tasks by hand (Appendix A.3, E). Appendix E.2, "Emergent
with GPT-3 or LaMDA", lists 25 tasks; E.3, "Emergent with PaLM", lists
42. Tasks this design first took for emergent are NOT, on that list:
unit conversion, periodic elements, object counting and simple
arithmetic are E.1 "smoothly increasing"; multistep arithmetic,
navigate and tracking shuffled objects are E.4 "flat"; boolean
expressions and dyck languages are E.5 "not correlated with scale".
They are excluded for that reason alone. The classification is the
field's and is used as given; this program did not re-derive it.

**The selection rule, fixed before the task list was read against it:**
a task enters iff (i) it is in E.2 ∪ E.3; (ii) its items are
procedurally definable from its published definition, so fresh items
can be generated; (iii) its answer is verifiable by exact match after
normalization; (iv) it is not a two-way choice (a floor of one half
makes a per-item count mostly guessing); (v) 500 distinct items can be
generated. Ten tasks pass. Excluded under (ii): every knowledge and
natural-language task on the two lists, and the hand-written tasks
(logical sequence, 39 items; odd one out, 86; repeat copy logic, 32).
Excluded under (iv): hyperbaton, and CS algorithms' valid-parentheses
subtask. `logic_grid` was a candidate in the original design but is
excluded: its published material gives the vocabulary and wording, not
the clue generator. `temporal` and `shapes` are retained as
RECONSTRUCTIONS: their published pattern is their definition. Their
sentence frames and path syntax follow the observable task structure.

**Contamination, stated at the level this program can state it.**
BIG-bench's task files have been public on GitHub since 2021, under
Apache 2.0. The Pile was scraped in 2020: Pythia cannot have seen
them. OLMo-2, SmolLM3 and Comma train on later web and code, and
Comma's corpus is built from permissively licensed code, so BIG-bench's
own strings are plausibly in all three outcome corpora and in
Predictor B's. This design uses none of them. Every item is a fresh
string from a seeded generator committed at the preregistration tag.
A COLLISION GATE at build refuses any item's or shot's key that occurs
in the corresponding BIG-bench task file at commit
`092b196c1f8f14a54bbc62f24759d43bde46dd3b`. Keys render BIG-bench's own
wording, including grammar slips and original object names; the battery
surface can differ. The audit round-trips 16,654 of 17,749 strings,
with 1,095 outside the generators' support for five stated reasons and
none failed, plus all 24,712 modified-arithmetic pair keys (commuting
pairs either way round). Every generated item's and shot's key is
parsed and rendered back. The index holds hashes; 77 audit known answers
hold parsed arguments and BIG-bench's canary. Item writing requires the
pinned audit record to bind the generators, driver and collision module.

The gate is STRING-LEVEL. `ipa_word`'s sentence-to-word gate cannot
fire: its items are fresh by construction. The pinned content-overlap
record counts 491/497 unscrambling answers among BIG-bench's targets,
369/434 sorting items sharing a word (22/2 sharing every word), 137 IPA
input words and 146 IPA answers in BIG-bench's sentences/transcriptions,
and no repeated `lcs` string. The modified-arithmetic QUERY pair is
separately excluded if BIG-bench prints it, either way round for +/*;
worked pairs can overlap (28/13/499 items, either way round). These
overlap counts exclude nothing further. What the gate cannot exclude:
familiarity with task content or a task's FORMAT from
BIG-bench-style text. That can raise a model's level on a rung; it is
part of what the corpus contains, it is asymmetric between the two
predictors (Pythia cannot have it), and the A-versus-B readings are
printed beside each other for that reason (S3).

**Departures from BIG-bench, each disclosed and carried into §6 (B-29).**

1. Every rung uses 2c's two-shot `Q: … A:` frame, without BIG-bench's
   task/example prefixes. Headers can differ from its prefixes.
2. Deduction asks a question with object-name options; BIG-bench scores
   three or five full sentences without printing them. Three object
   names are corrected to single words/correct spelling on the battery
   surface; the key retains the original names.
3. `lcs` is free-form exact match; BIG-bench scores ten unprinted choices.
4. Unit items are generated under the README's rule as far as stated,
   rather than its 25 hand-written examples per level. All candidate
   readings are offered; roles and answer position follow the slot.
   Two sentences in three scale the rate (BIG-bench: 9/25 and 13/25).
   Three unit words with the scaling ignored solve 334/500 of level 2
   (BIG-bench: 19/25); this rule reads roles and does arithmetic, and is
   disclosed outside the heuristic floor. Grammar slips are corrected
   on the battery surface, retained in the collision key.
5. IPA is one direction, one word with one pronunciation, exact match
   under `eng_to_ipa`'s CMUdict convention (314 answers carry stress).
   Other valid conventions can miss. BIG-bench uses both directions,
   sentences, BLEU/ROUGE/exact match. S12 relaxes conventions on both sides.
6. Sorting uses three/five words, rejects already sorted lists and a
   word inside another; BIG-bench lists have two to twenty words.
7. Unscrambling uses 4–5/6–8 letters, one solution in the vendored
   21,540-row table; BIG-bench permits alternatives and 3–18 letters.
8. The word source is mechanically filtered (§3.1), with no semantic
   filter; acronyms, brands and abbreviations remain.
9. ASCII uses two fonts and 3–6 letters; BIG-bench uses five and 3–14.
10. With the two shots, a modified-arithmetic prompt has fifteen worked
    lines and two answered queries; BIG-bench shows five worked lines.
11. `temporal` and `shapes` list shuffled choices under `Options:`;
    BIG-bench appends choices in its own format.

Option-listing rungs are scored by exact match on the emitted option,
not option likelihood. Difficulty parameters define the rungs in §3.1.
A landing concerns these renderings, not BIG-bench scores. The complete
generation choices, discovered shortcuts and historical corrections are
B-1–B-36 in `docs/superpowers/plans/2026-09-27-exp6-battery.md`, ratified
with this design; its historical code blocks are not the final instrument.

**Build contacts and accidental contact.** The ledger records the two
generation-only packages, unigram source, task files/READMEs, and tokenizer
and config files of twelve revisions in eight repositories (62 MB in the
prototype cache; seven revisions in the token record). Prototype contacts
were logged retrospectively. On 2026-09-28 a prototype mutation test
loaded SmolLM3-3B's stage-1 endpoint weights twice, first by download and
then from cache. Both stopped on the move to CUDA on the Mac, before
tokenizer loading or a forward pass. No item was read or scored. The
5.7 GB cache entry is retained, as ratified. Tests now run offline with
an empty cache; loader/sampler injections fall back only on `None`.

**"From below", disclosed.** In parameters both predictors are below
every outcome. In tokens Pythia-1b (≈ 300 B) is below all four;
OLMo-2 1B (≈ 4 T) is above Comma (1 T), level with OLMo-2 7B and below
the other two. The sealed-forecast logic needs the predictor committed
before the outcome is read, not "below"; the essay's "smaller model"
holds for Predictor B in parameters only.

**Sealed in order (§7):** the instrument and item files
(`exp6-preregistered`) before planned model contact; predictors
(`exp6-predictor-sealed`) before any outcome model is handed an item of
this battery; endpoints, rung sets and power (`exp6-endpoint-sealed`)
before any intermediate checkpoint is scored into a record; projection
before sweeps. The two accidental weight loads above precede the first
two seals. Outcome preflight follows the predictor seal and loads each
family's endpoint and first grid step. It writes no record. On new-battery
items it reports shape, timing and identity, with no score; on 2c's two
anchors it checks and prints counts against committed counts. Its own
file is tag-exempt (N-8); each outcome preflight is ledgered with UTC,
HEAD and the predictor-seal sha256 it checked.

**Pre-tag disclosure rule** (checklist item 27): every execution of
the analyzer on the real tree before the tag is logged here before the
tag is cut, with what it printed. Every one must land
INSUFFICIENT_DATA and print no T.

The reconstructed tally and every later increment are in
`experiments/exp6/PRETAG_AUDIT.md`: ten real-tree cold-battery executions
through takeover, all before any campaign record, with no T computed.
The final ratification battery is added there before the tag.

## 3. Instrument

Everything not named here is imported frozen: 2c's harness, exp3's
sampler, 2g's strata machinery and statistics, 2d's floor rule, the
four families' loaders and pins (2i, 2l, 2m, 2n — including 2n's BOS
render and stop-id override for Comma and 2i's per-entry config write),
eligibility n_pos ≥ 20, the count outcome with first-correct printed,
the referent discipline, tree totality, blob-bound tags, the import-
surface pin from the first runner/analyzer commit (2j F-1; N-13), `pins_active` (2k D-1), both
halt artifacts refusing (2k F-1), the window-completeness refusal (5b
F-1: an unfinished campaign delivers no verdict), provenance measured
and not attested (2i F-1, Exp 4 F-1).

### 3.1 The battery

Seventeen candidate rungs from ten tasks, 500 fresh items each, two
fixed shots per rung, one seed per rung, item files committed and
sha-pinned at the tag.

| rung | BIG-bench task, Wei class | rule | answer | floor | stratum covariate |
|---|---|---|---|---|---|
| `modarith_add1` | modified arithmetic, E.2 | five in-prompt examples of a + b → a + b + 1, operands 0–998, query-pair collision gate | number | majority share | carries in a + b |
| `modarith_sub1` | same | a − b + 1, same operands/gate, negative answers occur | number | majority share | sign of a − b × borrows in \|a − b\| |
| `modarith_mul1` | same | a × b + 1, operands 0–98, query-pair collision gate | number | majority share | digit count of a × b |
| `unscramble_short` | word unscrambling, E.2 | 4–5 letter word, letters permuted, unique solution | word | majority share | length × frequency tercile |
| `unscramble_long` | same | 6–8 letters | word | majority share | length × frequency tercile |
| `ipa_word` | IPA transliterate, E.2 | English word → IPA, CMUdict, one pronunciation | ipa | majority share | transcription-length bin (1–4 / 5–6 / 7+) × frequency tercile |
| `sort3` | word sorting, E.2 | three words → alphabetical order | sequence | majority share | longest shared prefix between neighbours (0 / 1 / 2+) |
| `sort5` | same | five words | sequence | majority share | same |
| `deduction3` | logical deduction, E.2 | three objects, minimal clue set, one position queried, options listed | word | 1/3 | position of the correct option |
| `deduction5` | same | five objects | word | 1/5 | position of the correct option |
| `ascii_bubble` | ASCII word recognition, E.3 | figlet `bubble`, word 3–6 letters | word | majority share | word length × frequency tercile |
| `ascii_basic` | same | figlet `basic` | word | majority share | word length × frequency tercile |
| `shapes` | geometric shapes, E.3 | reconstructed SVG path → shape name, ten classes balanced, ten shuffled options | word | 1/10 | answer class (nominal) |
| `temporal` | temporal sequences, E.3 | reconstructed free interval in a schedule, four options listed | span | 1/4 | position of the correct option |
| `lcs` | CS algorithms, E.3 | length of the longest common subsequence of two strings, answers 0–9 balanced | number | 1/10 | answer (ordinal) |
| `unit_interp1` | unit interpretation, E.3 | level 1 (one implicit unit), five options listed | number | 1/5 | position of the correct option |
| `unit_interp2` | same | level 2 (two implicit units) | number | 1/5 | position of the correct option |

Floors by 2d's rule, max(majority share, 1/n_options), computed from
the item files at build and pinned; the table gives the nominal value.
Option counts are declared by the spec and checked per item, not inferred
from a colon in the text (which would misread sorting). Strata by 2g's rule: one covariate
per rung, a pure function of the committed item, raw level counts
pinned at build, ordinal levels below ten items merged, nominal levels
never merged. Where the answer has few classes (`shapes`, `lcs`)
the stratum is the answer itself, so a forecast
there is within answer class and a shared answer prior cannot produce
it. On the word rungs the stratum includes frequency, so "common words
come first for every model" cannot produce it either.

Word source: the unigram list BIG-bench's unscrambling task names (the
Trillion Word Corpus counts, top 10,000), pinned by sha at build. The
vendored table keeps a–z strings of at least three letters with a CMUdict
entry, 21,540 rows; 9,128 are in the top 10,000. No semantic filter:
26 letter-acronyms occur in the single-pronunciation top-10,000 pool;
at most 11 items of a rung touch one, including `phd` on IPA. Words
in BIG-bench's own ASCII task file are excluded from the ASCII rungs:
a figlet rendering is deterministic, so the same word in the same font
would reproduce BIG-bench's string exactly.

**Generation choices (B-11, B-17–B-36).** Seeds are literals
20260901–20260917 on the specs, not in rung-table order. The battery
has its own registry; 2c's is never modified. Each item has two fixed
shots drawn at slots 500 and 537, with the same collision/answer checks.
Word-source rungs (`unscramble_*`, `ascii_*`, `ipa_word`) repeat no
answer among their 500 eval items and two shots. Shot keys and metadata
are retained in `shot_records`; the harness reads `shots`.

Duplicate questions are rejected on the rung's question key as well as
its text. The modified-arithmetic pair is canonicalized where it commutes;
unit keys name numbers/scaling/roles; deduction keys normalize the clue
set; temporal keys name schedule/free interval. A shot is redrawn if its
question, content, guard or shown keys would give an eval item away.
The eval items are not redrawn for a shot. Every committed rung was
independently checked for duplicate questions and revealing shots.
The broader classes not excluded by these keys, including shared unit
relations, are counted in B-35/B-36. At other seeds the shot guard leaves
some wrong-candidate/other-position/relabelled-`lcs` cases open; none is
present on the committed items. Both `deduction3` shots are directly
stated answers, retained as drawn; 108/500 eval items are of that class.
`deduction5` has 168 directly stated eval answers and two derived shots.

The `lcs` lengths are drawn uniformly on 4–31 independently of the target,
then rejected unless their LCS is that target (50 items per answer).
Polygons reject turns below 15 degrees. Unit numbers/options are drawn
without seeing the question's roles, refusals applied to every candidate
reading, all readings integral and at most 5,000. Options contain the
two unscaled/four scaled candidate readings plus fills from combinations
of the item's numbers (nominally three quarters) or the pool. No option
is 1; copied answers occur only in level 2's flagged stated-quantity
class (84/500). The numbers use the README's small-prime-factor rule,
with the bounded pools and departures of B-25. A role change preserves
numbers, options, refusals and relative order of shared wrong options;
the answer alone is moved to the slot's position. Rank by size is not
designed. A roles-blind reader's bound is a third over the rung (B-34);
candidate-aware fitted guessers score about a third held out (B-32),
reported as diagnostics, not gates.

**Floors and structure (D-2/D-3).** The primary retains the rule's
floors and strata. Seventeen fixed surface guessers give pinned heuristic
floors; fitted tables are cross-scored between halves of blocks of ten
slots. Rule → heuristic: `temporal` .25 → 1.00, `lcs` .10 → .474,
`unit_interp1` .20 → .358, `unit_interp2` .20 → .50. Counts carry both
floors; S13 reads the heuristic-clearing sets. In particular, temporal
can be solved by choosing the option absent from the text on every item,
here and in BIG-bench. Pinned extra structure levels capture carry ripple,
fixed scramble letters, sorting inversions, IPA stress, deduction read-off/
end position, free-interval position, LCS length, unit role/scaling cells
and pen restatement. S11 crosses these into the strata without merging;
some crossed cells hold one item, so it is descriptive.

**Anchors, never in a verdict.** 2c's `add_base8` and `sub_base8` item
files verbatim: both sides of every test already have committed
numbers for them (2k's and 2i's draws; the four families' per-item
counts), so the new pipeline is checked against known answers before
it is trusted on unknown ones (§3.3, §3.4). And `ctrl_copy`, the
sampler's known-answer control: a committed stream exists for Pythia
(exp3's) and for nothing else, so it gates the Pythia path by byte
identity and is printed as a sanity rung everywhere else.

### 3.2 The verify criterion

2c's `normalize_answer` verbatim for `number` and `word`. Three additive
types: `sequence` and `span` — first line, lowercased, outer punctuation stripped,
internal whitespace collapsed, the whole line compared; `ipa` — first
line, stripped, first whitespace token, no case folding. Totality is a
build requirement (methods paper §6, lesson 5): every draw-side string
returns a boolean through a total wrapper, the answer side stays a hard
error, fuzzed at build. The anchors' verify path must be byte-for-byte
the committed one; the mutation battery carries a mutant for it.

Token budgets, one per answer type, carried on every record: `number`
8, `word` 12, `span` 12, `sequence` 16 and `ipa` 24 on BOTH instruments.
The pinned seven-tokenizer record puts the longest answers of the new
types at 9/12/17 tokens respectively. The anchors keep their committed
budgets (number 8, word 12), including when sampling; the copy control's
referent budget is 12. The original design's flat sampling budget was
not the committed 2d/2i/2k shape.

### 3.3 The predictors — new sampled quantities, sealed before any outcome item reading

exp3's frozen sampler (seeded ancestral, T = 1.0, untruncated, fp32)
on the Mac, the stack behind every byte-identical reproduction in this
program.

- **x_A** — Pythia-1b, seeds 0–3 × 64 draws = 256 per item (2k's seed
  map). x_A at 64 / 128 / 192 from the same rows (S1).
- **x_A at 410m**, same shape, non-gating (S2).
- **x_B** — OLMo-2 1B stage-1 endpoint, seed 0, 64 draws (2i's tier).
- **Pilot, first:** Pythia-1b, k = 8, seed 1000 (2d's pilot seed), all
  seventeen rungs. It MEASURES liveness and is printed in S6. Power reads
  the sealed main tier, not the pilot. No rung parameter changes after the
  tag, whatever it shows.
- **Untrained twin:** Pythia-1b's seeded `from_config` twin, 64 draws,
  all seventeen rungs — the format floor of the verify criterion under
  sampling, measured and not assumed (process rule 2).
- **Gate 1-P:** the anchors re-sampled through the PRODUCTION path must
  equal the committed streams byte for byte — 2k's 1b and 410m tiers
  at 256 draws on the base-8 pair, 2i's OLMo-2 1B tier at 64 — with
  coverage attested by the runner and re-derived by the analyzer.
  `ctrl_copy` reproduces exp3's committed Pythia stream byte for byte
  at seeds 0–3 × 8 draws, budget 12 (at 1b: 13,460/16,000 verified).
  No committed OLMo copy stream exists; it is a sanity rung there.
- **Degeneracy:** 2i's Ruling 18 — a stratum in which the predictor is
  constant is dropped; a rung with no informative stratum is dropped
  from that test and printed.

Sealed as `exp6-predictor-sealed`: draws, records, the seal file, with
every record's provenance (repo, revision, items sha, seed, k)
re-derived from the raw draws at the seal and again at analysis.

### 3.4 The outcomes — four families, each through its own frozen loader

| family | repo | grid (steps) | init referent |
|---|---|---|---|
| SmolLM3-3B | `HuggingFaceTB/SmolLM3-3B-checkpoints` | every 40k to 400k, every 200k to 3,400k, 3,440,000 — 26 points | seeded twin |
| OLMo-2 7B | `allenai/OLMo-2-1124-7B` | 1k, 2k, 4k, 8k, 16k, 32k, every 64k to 896k, 928,646 — 21 points | seeded twin |
| OLMo-2 13B | `allenai/OLMo-2-1124-13B` | 1k … 32k, every 64k to 576k, 596,057 — 16 points | real step 0 |
| Comma v0.1-1T | `common-pile/comma-v0.1-1t` | 10k, every 20k to 460k — 24 points | seeded twin |

87 checkpoint loads plus four referents. Each grid is the one its own
experiment froze, with its committed manifest and per-file shas; each
family is scored under the render, pad, stop id and tokenizer pins its
own experiment froze. 2c's greedy harness, fp16, batch 16, per-item
bits and continuations stored. y_i = the number of that family's grid
points at which item i verifies; first-correct printed beside it.
Finiteness of the logits is MEASURED per unit and carried on the
record (Exp 5 slip 9); a non-finite unit scores as it emits, as 2l's
step-1000 record did, and is printed.

**Host: a rented A100 80 GB (dial k).** The argmax harness runs 12×
faster there than on the Mac (measured, `tools/vast_bench`), which
turns about five days of Mac time into about half a day. The cost is
that greedy continuations are not byte-comparable across hosts, so the
cross-host check is a tolerance, as in Experiment 5.

**Gate 1-O, per family, on EVERY sweep host (N-1/N-2/N-14):**
(a) the stage-1 endpoint through both loader paths on that host: 0 bit
differences, 0 continuation differences, 500 items on each of all TWENTY
rungs (17 new, two anchors, control), tensor digests equal;
(b) that host's endpoint counts against the SEALED endpoint records,
|Δ| ≤ 15 items per rung;
(c) the two base-8 anchor counts against the Mac's committed counts,
|Δ| ≤ 15 per rung at the endpoint AND every grid step;
(d) the measured tensor digest of each checkpoint against the earlier
Mac record of that same checkpoint, BEFORE rendering a prompt or scoring.
This includes endpoint reads, both sweep-host gate reads, every grid step
and OLMo-2 13B's real step 0; seeded `from_config` twins are outside (d).
The sealed endpoint digest must also equal the sweep host's.

Both host reads are kept under `gate1_<host>/`; the endpoint seal and
analyzer re-derive the gates from bytes. Gate 1(b) at the endpoint stage
checks the final and init anchor counts against the Mac too. The tolerance
15 is Experiment 5's frozen tolerance on this host class; the original
8 was the benchmark's largest observed difference, not its tolerance.
A failure halts the stage/family, carries the full measured digest where
applicable, and the analyzer delivers INSUFFICIENT_DATA. A partial endpoint
load resumes only on its original host; migration requires moving that
partial load aside. A new sweep host repeats its own gate.

### 3.5 The tree

INSUFFICIENT_DATA (any gate, any refusal, any incomplete family) → the
eight tests → the two statuses → the world, by §1's tables. Every
quantity of §5 printed in every world.

### 3.6 Pins

`FROZEN_SHA256_6` over every imported module; `IMPORTED_SHA256_6` over
the resolved module table at entry and exit, in the analyzer AND in
every runner (4c F-1); a pre-campaign referent manifest (the committed
records the anchors, S8 and S9 read) with its sha a literal in the
analyzer; blob-bound tags — `exp6-preregistered` binds SIXTEEN instrument
files and SEVENTEEN item files. The instrument files are analyzer,
battery/floors/strata/verify, families/records/referents/pins/power,
the common runner module and the five predictor/endpoint/sweep/seal
runners (`INSTRUMENT_BLOBS_6`); each new item file is directly bound.
Lazy imports are measured, imports from foreign `experiments` paths
refused, and executed bytecode held to the hashed source. The import pin
landed with the first runner/analyzer commit; the final measured surface
is 73 frozen and five own unbound modules, plus the sixteen tag-bound.
The preflight file itself is exempt; all its imports are checked.

## 4. Rung sets, strata and power

**R_f** — for family f, the candidate rungs whose stage-1 endpoint
count clears 2d's bar against the rung's floor, fixed by rule at the
endpoint stage. Not known now. Foreseeable and disclosed: the five
E.2 tasks emerged with GPT-3 or LaMDA (three of them at 13 B
parameters in Wei et al.'s Figure 2, on 300 B tokens) and are the
likelier to clear at 3–13 B on 1–8 T; the five E.3 tasks emerged only
with PaLM and may be flat at these sizes, in which case they are
printed as flat and no test reads them.

**What a test reads.** Test (P, f) reads the rungs of R_f on which
predictor P is non-degenerate and n_pos ≥ 20. Fewer than three →
the test is not EVALUABLE, prints THIN, and does not count toward
E_P or F_P. Whenever a test reads fewer rungs than R_f the verdict
names them and states SAME or WIDER against the power record's
`rungs_simulated` (2m R-1).

**Power**, written ONCE at the endpoint stage, before the projection,
through the verdict's own tree with 2i's machinery over the REAL
predictors: per test, P(fires | D = .15) against the bar .75, else
DECLARED UNDERPOWERED IN ADVANCE for that test, with P(fires | D = .10),
the null SD of T and the minimum detectable T; Predictor A's four
64-draw blocks' SD (2k's process note); and at tree level, under
latent outcomes drawn independently per family, per-predictor holds/fails
probabilities (Poisson-binomial) and the probability a null predictor
reads H. Joint P(GENERAL | D = .15 everywhere) and P(BATTERY-BOUND | null)
are Fréchet BOUNDS, not point probabilities: the two predictors share
outcomes and their joint is not modelled. Family independence is a modelling
choice and is printed as one: the families' real orders are correlated (2m's S8 read
.23–.46), which the record cannot know before the sweep. Shape note
carried verbatim from 3d: the alternative is item-level; nothing
transfers to a class-level effect.

The analyzer re-derives declarations from the sealed power record's
numbers and verifies its inputs/sets. It does not rerun its simulations;
those probabilities are bound by the endpoint seal (ratified residual).
Withdrawal under §6 requires the POWERED declaration to cover the EXACT
rung set each evaluable test read, not a wider or narrower simulation.

## 5. Named secondaries (printed in every world; no α claim)

- **S1 — the ladder.** T_A at k = 64, 128, 192, 256 and the four
  64-draw blocks, per family.
- **S2 — 410m at 256**, per family.
- **S3 — the two predictors against each other:** B-beyond-A,
  A-beyond-B, the paired difference with its paired item bootstrap
  interval, per family. The contamination asymmetry of §2 reads here.
- **S4 — by type and by class.** Per-test T over the arithmetic rungs
  (`modarith_*`, `lcs`), the string rungs (`unscramble_*`, `ipa_word`,
  `sort*`, `ascii_*`, `shapes`) and the choice rungs (`deduction*`,
  `temporal`, `unit_interp*`); and over Wei et al.'s E.2
  rungs against the E.3 rungs. 2l and 2m read the cross-family
  component as arithmetic-heavy; this is where that repeats or fails.
- **S5 — the answer prior.** 2j's wrong-target propensity on x_B's
  rows as a forecaster of each family's order (its fourth test).
- **S6 — the referents.** The four init referents' per-rung counts and
  the predictor twin's sampled counts, expected at their floors; the
  pilot's counts beside the main tier.
- **S7 — textures.** Ever-versus-final verification, transient clears
  on flat rungs, checkpoint-local collapses, first-correct steps, the
  ceiling fraction per rung under the analyzer's definition.
- **S8 — outcome-to-outcome order** on the new battery: each family's
  per-item count read as x against each other family's, 2g's statistic
  in the same strata. The predictor-free read of "is the order shared".
- **S9 — the two batteries side by side.** Per predictor and family,
  T on 2c's nine rungs (committed verdict records, referents) beside
  T on the new battery.
- **S10 — the anchors.** Per predictor and family, per-rung D on the
  base-8 pair through the new pipeline beside the committed per-rung
  D, difference printed against a declared tolerance of ±.03.
- **S11 — structure-conditioned.** Each test with the pinned extra
  structure levels crossed into its primary strata, no merging (B-21).
- **S12 — relaxed IPA.** Each test re-read with `ipa_word` re-scored
  on BOTH predictor and outcome sides after removing stress marks and
  writing affricate ligatures as digraphs, using the analyzer's fixed
  relaxation table. Primary exact match stays unchanged.
- **S13 — heuristic-clearing.** Each test over R_heuristic, the subset
  of R_f whose sealed endpoint also clears the heuristic floor. Both
  sets are re-derived and committed at the endpoint seal.
- **Sensitivities:** first-correct as y; Test B conditioned on A's
  bucket (2i's form); the naming rule at two of four.

## 6. Licences, written in advance

Every licence is bounded to item grain, to the rungs named as read, to
these renderings of the tasks (§2's eleven departures), and to
predictors at or below 1 B. None licenses the across-task ranking:
which tasks a family clears is R_f, read at the endpoint, not forecast.

- **GENERAL.** The essay's one-line thesis generalises off the battery
  it was found on: "the order in which the field's own emergent tasks
  come into focus during training is forecast, at the level of single
  items, by the sampled outputs of one-billion-parameter models of two
  other families, on at least three of four outcome families, named for
  each predictor." The holding sets need not be identical. The essay leads
  with it.
  **Headline condition:** the phrase "the field's emergent tasks" may
  stand without a type qualifier only if at least two of S4's three
  types each hold a rung whose per-rung interval excludes zero on at
  least three of that predictor's EVALUABLE families for a holding
  predictor; otherwise the sentence names the type that carried it.
  Named next: Michael's call.
- **PYTHIA-ONLY / OLMO-ONLY.** The forecast generalises for the named
  predictor and the sentence is bounded to it. Under PYTHIA-ONLY the
  result is the cleaner of the two (the predictor that cannot have seen
  BIG-bench holds, the one that can does not); under OLMO-ONLY the
  contamination asymmetry of §2 is named as the live alternative and
  the essay's sentence says so. The headline condition applies.
- **SPLIT.** The forecast reaches some families and not others on the
  field's tasks; the essay reports the table and claims no generality;
  the one-line thesis is bounded to "on one battery and, on the field's
  tasks, on the families named". No named successor.
- **BATTERY-BOUND.** "Neither predictor reached the naming rule's bar
  on the field's tasks: each fired on at most one of its evaluable
  families. Read under the power record." If every evaluable test was
  POWERED for the EXACT rung set it read, this is a measured absence
  at the naming rule's bar: the eight sealed forecasts are a property of
  2c's battery, the essay's forecast claim
  is demoted to "on one synthetic battery of this program's making",
  the one-line thesis is withdrawn, and what remains for the essay is
  the within-task ladder (3b–3e, 2f) and the methods paper. Whether
  the program continues is Michael's call, and the record supports
  stopping. If tests were declared underpowered, or any evaluable test
  read a set its power record did not simulate, the reading is "not
  detected at this resolution" with the blind region stated, and the
  demotion is to "not shown beyond one battery".
- **UNDETERMINED.** Too few rungs cleared or too few predictors were
  live for the naming rule to apply; the full table is reported;
  nothing about generality is licensed in either direction. The record
  names which shortfall it was (outcome side: R_f; predictor side:
  degeneracy). Losses to constant-within-stratum or thin outcomes over
  the sweep are named on the outcome side; unexplained losses are said,
  since these shortfalls call for different successors.
- Any world: S1–S13 in full; flat rungs, dropped rungs, the referents
  and the anchors reported.

## 7. Run plan, model contact and cost

| stage | host | model contact | time | money |
|---|---|---|---|---|
| build + adversarial freeze + ratification | Mac | no planned contact; accidental loads disclosed in §2 | ≈ 7–9 days | $0 |
| tag `exp6-preregistered` | — | none | — | — |
| predictor preflight, on Michael's word | Mac | longest-prompt finiteness, gate 1-P rehearsal, one item sampled twice on each preflight rung per predictor | part of ≈ 2 h preflight estimate | $0 |
| predictor stage: pilot, x_A, 410m, x_B, twin, gate 1-P | Mac | predictors only | ≈ 1.5–2 days | $0 |
| tag `exp6-predictor-sealed` | — | — | — | — |
| outcome preflight | A100 80 GB | endpoint and first grid step per family; SmolLM3 endpoint through both paths; 40 items on three new rungs; both anchors on all 500 at each read; no campaign record | rest of ≈ 2 h estimate | ≈ $2 |
| endpoint stage: four stage-1 endpoints + four referents | A100 80 GB | outcome endpoints | ≈ 2 h | ≈ $3 |
| power, once | Mac | none | ≈ 4–5 h | $0 |
| tag `exp6-endpoint-sealed`; projection sealed | — | — | — | — |
| sweeps: gate 1-O then the grid, per family | A100 80 GB | 87 checkpoints | ≈ 11 h compute, ≈ 16 h box | ≈ $18 |
| analyzer once, on Michael's word; tag `exp6-closed` | Mac | none | ≈ 1 h | $0 |
| close-out propagation | Mac | none | ≈ 1 day | $0 |

About three weeks of calendar and about $25, budgeted at $40. The box
is destroyed between the endpoint stage and the sweeps (5b's idle-time
note). About 1.7 TB is streamed on the outcome side, one checkpoint at
a time and deleted, on a host with free ingress, thermally screened
before install (`thermal_screen_5.py`), transports measured per host
(4c's note). The smallest family is swept first so a battery that is
flat at 3 B is found at the least cost. Every record is watcher-
committed; campaign processes launch via
`Popen(start_new_session=True)`. One pre-committed change.

The preflight prints both of Comma's renders and measures peak memory
and finiteness at fp16 for each family on the box, since SmolLM3 and
Comma have never run on a CUDA host in this program.

Each outcome preflight logs UTC time, HEAD and the predictor-seal sha256
it checked. It refuses before any load if that seal does not bind; it
rehearses weight identity and the Mac anchor tolerance, prints anchor
counts, and leaves weights in cache. No new-battery score is printed.

Request **250 GB disk**; setup checks **230 GB free** on both `$HOME`
(the caches) and `/workspace`. These are decimal GB (10^9 bytes), not
GiB; `df -Pk` blocks are multiplied by 1024 before conversion. The peak
allows about 104 GB of retained endpoints, 55 GB of retained OLMo-2 13B
step 0, and 55 GB for one candidate/checkpoint, plus software. The
candidate and next checkpoint are not resident together. The rental
bundle advertises only `master` and `exp6-*` tags, checked for required
refs and byte bindings before use. It still carries the private history
reachable from master; it is not content-filtered. Every instance create
and destroy requires Michael's explicit confirmation.

Records are written beside their destination and renamed atomically;
temporary names carry the writer PID. An existing malformed JSON record
is a torn record, refused rather than resumed over. Stages refuse out of
order, over either halt artifact, or after their successor seal. The
endpoint runner refuses once rung sets exist; the power writer refuses
over a halt. Host-stack validation precedes host-record writing; import
checks also run at exit and write a halt marker on failure. Predictor
seal tables skip dotfiles and temporary files. A dot-directory containing
records would still enter the table; no producer creates one (accepted
residual). The production analysis CLI uses frozen permutation/bootstrap
counts; direct `run()` calls accept others and disclose `frozen_counts`
(accepted residual). Offline tests use isolated empty model caches.

## 8. Alternatives considered

**A second synthetic battery** (Option B): the cleanest replication and
the least informative landing — "it holds on a second set of tasks I
made up". **Both, with the synthetic arm as control** (Option C): adds
a week; the anchors do the control's job at no cost. **BIG-bench's own
items with a memorization gate** (Option 2): keeps the knowledge tasks,
but the gate is a new instrument and a task that passes it can be
contaminated below its resolution. **One family first** (Option 2 of
the outcome question): splits the claim across two preregistrations,
the second written knowing the first. **A pooled primary:** 4c. **The
Mac for the outcome side:** byte identity on the anchors instead of a
tolerance, at about five days and the mlx servers down for 13 B — dial
k. **A smooth-task contrast stratum** (E.1 tasks beside the emergent
ones): it asks whether the forecast is specific to emergent tasks, a
good question this experiment does not need answered to decide. **The
released models as descriptive endpoints:** nothing in §6 reads them.

**Not part of this experiment, named:** the matched-token size ladder
on Pythia's committed bytes (nine shared steps across six sizes,
per-item bits on disk) — analysis-only, zero dollars, a separate
preregistration (dial t).

## 9. What Experiment 6 does not claim

Not BIG-bench scores. Not a statement about tasks outside the ten,
or about the other emergent tasks that could not be regenerated.
Not the across-task ranking. Not a statement about frontier models or
about predictors above 1 B. Not "from below" in tokens for Predictor
B. Not a mechanism result. Not a statement that emergence is a
function of model size: every outcome here is a training trajectory at
fixed size.

## 10. Dials — RULED 2026-09-27; amended by ratification 2026-09-29

Every original dial was approved as recommended. The amendments below
record the approved build corrections; the original text remains in git.

- **a. Name:** Experiment 6, `experiments/exp6`, tags `exp6-*`,
  **recommended** — a new battery is a new instrument, not a variant
  of 2c's line; vs 2o.
- **b. Battery:** the seventeen rungs of §3.1 under §2's five-part rule,
  **recommended**; vs the E.2 tasks alone (ten rungs; drops the tasks
  likeliest to be flat at these sizes, and the PaLM-class breadth with
  them).
- **c. Items:** fresh, seeded, with the collision gate against
  BIG-bench's files at a pinned commit — RULED in conversation.
- **d. Word-rung strata:** length × frequency tercile, **recommended**
  (without frequency the first objection to a landing is "common words
  first"); vs length alone.
- **e. Few-class rungs stratified by the answer** (`shapes`, `lcs`),
  **recommended**; vs a single stratum.
- **f. Predictors:** Pythia-1b at 256 and OLMo-2 1B at 64, with 410m
  at 256 non-gating, **recommended**.
- **g. Pilot:** k = 8, seed 1000, measures only; no rung parameter
  changes after the tag, **recommended**; vs tuning rung difficulty on
  the pilot (predictor-side only, but a forking path).
- **h. Outcomes:** all four families on their committed grids in one
  preregistration — RULED in conversation.
- **i. Naming rule:** H at three of four with at least three
  evaluable, the sixteen-cell map of §1, **recommended**; vs two of
  four (printed as a sensitivity).
- **j. Bars .10 / .01 unchanged,** **recommended**.
- **k. Outcome host:** a rented A100 80 GB with the cross-host anchor
  tolerance, **recommended**; vs the Mac (byte identity, ≈ 5 days).
- **l. Precision and batch:** fp16, batch 16, finiteness measured per
  unit, **recommended**.
- **m. Token budgets:** §3.2's, **recommended**.
- **n. Choice tasks as option-listing generative rungs,** exact match,
  **recommended** (the sampled count needs an emitted answer); the
  departure from BIG-bench's likelihood scoring is disclosed.
- **o. Anchors:** the base-8 pair on both sides and `ctrl_copy` on the
  Pythia path; the outcome-side gate on counts, the D comparison
  descriptive at ±.03, **recommended**.
- **p. The headline condition** of §6 (two of three types),
  **recommended**.
- **q. Endpoints:** the stage-1 endpoint per family only,
  **recommended**.
- **r. Power:** per test and at tree level, once, at the endpoint
  stage, **recommended**.
- **s. Projection:** sealed after the endpoint stage and before the
  sweeps; by rung type and by family; tolerances in both directions;
  the world and every per-predictor status called by name; the prior
  ("the forecast is task-shaped and will hold on arithmetic and string
  rungs") written as a claim with its own disconfirmer,
  **recommended**.
- **t. The size ladder** as a separate analysis-only preregistration
  after this one's tag, **recommended**; vs folding it in; vs not
  running it.
- **u. Build + freeze by SDD,** the import pin from the first runner/analyzer commit,
  **recommended**.

## 11. Process

Design → rulings → build → freeze → ratification → tag → predictor
preflight on his word → predictor stage → predictor seal → outcome
preflight → endpoint stage/rung sets → power
once → endpoint seal → projection → sweeps (detached, watcher) →
analyzer once, on his word → `exp6-closed` → close-out propagation
(essay under §6, `experiments.md`, the graft, Zenodo, paper
inventory).

Ratification applies the committed B-1–B-36 and N-1–N-16 delta lists,
the freeze/final-review closures and D-1–D-16/O-1–O-5 as consolidated in
`experiments/exp6/RATIFICATION.md`. `experiments/exp6/BUILD_RULINGS.md`
preserves all 109 coordinator rulings verbatim, including historical proposals superseded
by Michael's ratification. The final repository instrument supersedes
older code blocks in the two build plans. Final fast/slow suites, both
mutation passes, import scan and cold battery must pass before the
annotated tag is created, byte-bound against real git, and pushed.
