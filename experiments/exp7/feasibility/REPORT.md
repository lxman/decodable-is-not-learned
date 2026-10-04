# Experiment 7 generation feasibility

**Construction PASS, pending fresh independent review.** Corrected evidence:
`runs/full-003/`; exact repeat: `runs/full-004/`. Both contain **500 pairs
per family, 2,000 pairs and 8,000 distinct questions**. Every rendered
question has exactly one independent-oracle answer, equal to its stored
target. No model/tokenizer contact occurred. This is prototype feasibility,
not frozen production instrumentation or a scientific verdict.

**Main limitation:** the declared zero-indegree/zero-outdegree endpoint
shortcut solves **500/500 deduction pairs**, canonical and sham, with x=1.
Deduction therefore cannot establish a multi-step reasoning mechanism here.
The approved design admits such input-sensitive shortcuts and forbids
success-based filtering; these pairs were retained.

## Coverage and support

| Family | Pairs | Base blocks | Pairs/block | Structural support |
|---|---:|---:|---:|---|
| Words | 500 | 15 | 33–34 | 1,000 unique words; length 4–8 × source-rank tercile, exact repetition-profile matching |
| Deduction | 500 | 20 | 25 | chain4/distance4 or chain6/distance2 × unordered endpoint-option positions |
| Units | 500 | 5 | 100 | one multiply/divide depth-2 relation; digit pairs 2–3, 2–4, 3–3, 3–4, 4–4 |
| Shapes | 500 | 2 | 250 | square/kite and rectangle/rhombus; all closed convex four-segment paths |

No singleton blocks, ordinal merges or nominal pooling. All 500 word pairs
match length, rank tercile and sorted character multiplicities. All 2,000
scrambles differ from their own answer and every other scramble. Uniqueness
is relative to the **entire 21,540-word committed lexicon**. **328/1,000**
answers appeared as old unscrambling answers: fresh questions, not unseen
vocabulary. The source lexicon includes names/brands such as the first
example's `ebay`; no post-inspection lexical filtering was introduced.

Deduction enumerates all 120 orders for each of its 2,000 renders and finds
one solution each. No explicit positional/endpoint clue is admitted.
Unit oracles independently parse dimensional roles and use exact Fractions;
every role swap changes its answer, preserves the printed-number multiset,
vocabulary, unit and option order. All five numeric options are distinct.
Shapes have 1,000 unique congruence keys, four genuine sides each, exact
exclusive labels and verified translation-plus-cyclic shams. Each target
label occurs 250 times across pair members. **Four target labels and two
nominal pair classes, not ten-class shape diversity.** Both paired labels
occupy the same specified answer-length bin.

## Counterbalance

In every family: natural target orientation 250/250; the 24 presentation
orders occur 20 or 21 times. Every ordered pair of distinct target-option
positions occurs **25 times** in each option family; each target individually
occupies each of five positions 100 times. Options/order are shared across
all four arms. Within deduction, each graph class × unordered position pair
has 25 pairs. Orientation is balanced overall rather than forced within
every stratum: shape a0 counts are square 128, kite 122, rectangle 122,
rhombus 128. Full counts are in `certificate.json`.

## Collisions and source scope

All **103 inputs** are hash-pinned: 101 old task-item files, the lexicon,
and available BIG-bench index. The source inventory is byte-compared to the
approval snapshot; source hashes are checked at entry and exit.

- 247,698 old question records, **241,968 unique questions**, across eval,
  probe and shots; both exact and whitespace-normalized option-free checks.
- Structural keys: **5,930 old scrambles**, **968 old solved orders**,
  **674 old unit numeric tuples**, **351 old closed polygons**. Metadata
  coverage includes 1,004 deduction records, 502 unit triples, 502 two-number
  unit records, 351 closed and 151 incompatible arc/open shape records.
- New disjoint content units: 500 deduction orders, 500 unit triples and
  1,000 shape congruence keys. Shared content within a pair is intentional.
- **26,000 BIG-bench surface checks**, including reconstructed legacy frames,
  against all available index tasks. No admitted collision in these checks.
- The index contains hashes, not source examples: it cannot certify unseen
  BIG-bench structural content under every clue/vertex permutation. Old
  committed metadata supplies the stronger structural gate. Old metric-unit
  conversions are a different relation from the new cycle-rate equation.
  No claim of unseen abstract isomorphisms is made.

Candidate rejection counts, identical in corrected runs:

| Family | Rejections |
|---|---|
| Words | 37 identity, 22 repeated scramble, 59 old scramble, 33 BIG-bench surface |
| Deduction | 2 repeated new orders, 1 old order |
| Units | 31 old numeric triples |
| Shapes | 71 repeated new congruence keys |

Every candidate rejection and accepted bundle is retained in `attempts.jsonl`.
No item was rejected for baseline performance.

## Fixed baseline audit

All values below are deterministic finite-batch counts, not population-rate
estimates. **Canonical/sham paired counts share denominator 500 each**.
Unsupported target rows use denominator **2,000**; unsupported renders use
**1,000**. An applicable method emits one answer or explicitly abstains per
prompt. Unsupported renders contribute x=0, exactly as specified. Supported-
only means are null when no render is supported, not silently imputed zero.

Full 84 method×family cells, including every N/A reason, raw d/u and coverage:
`runs/full-003/baselines.json`. Individual outputs/readings:
`runs/full-003/baseline-outputs.jsonl`. There are **49 applicable and 35
nonapplicable cells**; N/A cells have null scores and zero denominators.

### Words

Constant, shortest, longest, frequency, inputcopy and querywordonly each
have **0/500** observed paired successes under both renders, mean x=0,
2,000/2,000 unsupported rows and 1,000/1,000 unsupported renders;
supported-only x is null. All emit, none abstain. Other methods are N/A.

### Deduction

| Method | Paired canonical/sham | Mean x | Unsupported rows/renders |
|---|---:|---:|---:|
| constant | 0 / 0 | 0 | 1636 / 818 |
| position1–5 (each) | 0 / 0 | 0 | 1200 / 600 |
| shortest | 0 / 0 | 0 | 1264 / 632 |
| longest | 0 / 0 | 0 | 1220 / 610 |
| frequency | 0 / 0 | 0 | 1176 / 588 |
| inputcopy | 0 / 0 | 0 | 1232 / 616 |
| absentoption | 0 / 0 | 0 | 2000 / 1000 |
| querywordonly | 25 / 25 | 0 | 1204 / 900 |
| cluedegree | 0 / 0 | 0 | 532 / 266 |
| endpoint | **500 / 500** | **1** | **0 / 0** |

Supported-only x equals mean x except absentoption (null). Absentoption
abstains on all 2,000 prompts because the intro lists every option; all
other applicable methods emit on every prompt. The spec's querywordonly
rule uses query direction to select the first/last **listed** object; its
name does not mean it reads no list. Numeric/path methods are N/A.

### Units

All applicable methods have 0/500 observed paired successes in each render
and mean x=0. All emit. Unsupported row/render counts:

| Method | Unsupported rows/renders | Supported-only x |
|---|---:|---:|
| constant | 2000 / 1000 | null |
| position1–5 (each) | 1200 / 600 | 0 |
| shortest | 1540 / 770 | 0 |
| longest | 656 / 328 | 0 |
| inputcopy | 1982 / 1000 | null |
| absentoption | 1148 / 574 | 0 |
| querywordonly | 1200 / 600 | 0 |
| numbers_min/max/sum/product (each) | 2000 / 1000 | null |
| numbers_ratio | 1968 / 984 | 0 |

Frequency, clue and path methods are N/A.

### Shapes

All applicable methods have 0/500 observed paired successes in each render,
mean and supported-only x=0, and no abstentions.

| Method | Unsupported rows/renders |
|---|---:|
| constant | 1000 / 500 |
| position1–5 (each) | 1200 / 600 |
| shortest | 1000 / 500 |
| longest | 1488 / 744 |
| frequency | 1000 / 500 |
| absentoption | 1200 / 600 |
| querywordonly | 1200 / 600 |
| segmentcount | 1000 / 500 |
| boundingbox | 526 / 526 |

Inputcopy, clue and numeric methods are N/A. Failure of these particular
rules does not establish absence of a cheap geometric shortcut.

## Worked examples (first pair in each family, not selected by results)

- **words-0000:** `eayb`→`ebay`, `iefr`→`fire`; shams `beay`, `frie`.
  Length 4, tercile 0, four distinct-letter profile. No options.
- **deduction-0000:** listed red/black/white/gray/brown; clues gray before
  brown, red after brown, black after red, white after black. Unique order
  gray→brown→red→black→white. q0 asks rightmost (white), q1 leftmost (gray).
  Shared options red/gray/brown/black/white. Sham moves the first clue last.
- **units-0000:** 5 parts/cycle, 10 hours/cycle, required 100 parts gives
  (100/5)×10=200 hours. Swap 5 and 10: (100/10)×5=50 hours. Shared options
  200/110/50/15/100. Sham moves the parts/cycle statement last.
- **shapes-0000:** kite vertices (81,294),(115,−52),(−159,−266),(−291,122);
  square vertices (82,92),(12,82),(22,12),(92,22). Both explicitly close to
  their first vertex. Shared options trapezoid/square/rectangle/kite/rhombus.
  Kite sham: start shift 2, translation (31,17). Square sham: start shift 3,
  translation (27,36). Geometry and class preserved exactly.

## Reproducibility and repair history

Specification was committed/pushed **cf50ef837** before full generation;
prototype **e8e32be4a**. Initial runs 001/002 were preserved at **27dcf1775**
after self-review found separate old-shot metadata omitted from structural
indexing. Regression failed 500≠502, then passed after fix **5ad3ccb07**.
See `RUNS.md`. No construction/spec/baseline rule was relaxed. Adding those
keys changes coverage but **does not change any generated pair or baseline
output byte**. Corrected runs 003/004 each took about 6.2 seconds; all eight
deterministic artifacts match byte-for-byte. Only operational receipts differ.

Key hashes:

- pairs: `361a89652222df8131185f946ded5b8962eb213b42e18890223c7f2eb349fe1b`
- corrected certificate: `00238fa53b313bbefc2cbe75c4dd2ef19054823234d78f9573244b23a1029c96`
- baseline table: `acc0959ee71fb82ce6766391b44beed78defdd8d20aafe6f2f8b2a5fa61b43bf`
- comparison: `runs/determinism-corrected.json`

Commands (from repository root; standard interpreter shown explicitly):

```sh
/Users/michaeljordan/emergence-lab/.venv/bin/python -m unittest experiments.exp7.feasibility.test_feasibility
/Users/michaeljordan/emergence-lab/.venv/bin/python -m experiments.exp7.feasibility.run --run-id full-003
/Users/michaeljordan/emergence-lab/.venv/bin/python -m experiments.exp7.feasibility.run --run-id full-004
/Users/michaeljordan/emergence-lab/.venv/bin/python -m experiments.exp7.feasibility.compare full-003 full-004 --output determinism-corrected.json
```

The run and comparison paths now exist and correctly refuse overwrite.
21 tests passed; import scan found only stdlib and this feasibility package.
Fresh independent review follows. The later complete-code build plan must
carry the checked logic and the disclosed shortcut/support limits through
production review/freeze; these prototypes supply no contact authorization.
