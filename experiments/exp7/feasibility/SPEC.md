# Exp 7 generation-only feasibility — fixed specification

2026-10-04. Prototype, not frozen production instrumentation. Governing files:
`PLAN.md`, design §§3/5/10. No model/tokenizer/imported predecessor instrument,
network source retrieval, sampling, power or verdict execution in this stage.
Git push is the authorized publication of this preregistration record.

## Inputs and pre-spec computations

`source_inventory.json` exhaustively pins 101 old item JSON files at source
snapshot `2d14da44ad882139bc95264697b03d45fe109354`, plus:

- `experiments/exp6/battery/data/words_6.tsv`, SHA256
  `1e19db04ee3a413f00aa59676a4a9a2b1a359c39f7b2347ce067059d8247d2a0`;
- `experiments/exp6/battery/data/bigbench_index_6.json`, SHA256
  `d47c4a4c4057b7dfe7d0ef0feb789625ef1fda81307a30788bcc067e45ef2525`;
  BIG-bench revision `092b196c1f8f14a54bbc62f24759d43bde46dd3b`.

Read generator sources for schema/frame interpretation only; import none.
`inventory.py` compared every resource byte to that Git snapshot. Prior to
this specification, direct parsing counted lexicon signatures and matching
profile capacities, examined four old-item schemas, and enumerated feasible
integer parameter triples. Those computations are disclosed in the inventory.
No proposed full item batch or shortcut result has been inspected. Old
`scored_battery.json` aggregates are excluded; only task item inputs are read.

## Determinism, schedules, evidence

Master namespace **2026100407**. Each stdlib `random.Random` stream is seeded
with the integer represented by SHA256 of UTF-8
`2026100407|<family>|<purpose>`. Families: `words`, `deduction`, `units`,
`shapes`; purposes: `content`, `orientation`, `positions`, `render`.
No Python `hash()`, process time, host name or global random state determines
outputs. Sort every set before randomized selection. Pins checked at entry
and exit. Rendered strings/JSON UTF-8, sorted keys, newline at EOF.

500 independent construction units per family, four arms named `q0,q1,q0s,q1s`.
`a0,a1` designate the two canonical answers. A seed-shuffled vector of 250
zeroes and 250 ones determines orientation, independently of content. The
natural order is the paired-word selection order, left/right endpoint,
lower/higher count-per-cycle, and first/second shape class listed below.
One shared ordered option list for every arm. In units/shapes, each of the
20 ordered target-position pairs appears 25 times, seed shuffled. Deduction
has each graph class × unordered position pair exactly 25 times; the direction
alternates with repeat index + graph index + unordered-pair index, giving
each ordered target-position pair 25 times overall. Shuffle this slot list.
The remaining three options are seed shuffled. Positions are 1-based.
Render order is a seed-shuffled schedule of all 24 arm permutations, repeated
20 times plus the first 20 permutations (counts 20/21); it affects presentation
order only, never answer identities. No model stream is created here.

Each full attempt creates a **new** directory, records candidate rejections,
all accepted bundles, parsed-oracle results, certificate, baseline table and
source/code/spec hashes. Refuse existing directories. Failed attempts retain
their evidence and terminal reason; no overwrite. After success rerun exactly
once in a second directory and compare every deterministic artifact byte.
Operational UTC/HEAD receipts may differ and are kept separately. `RUNS.md`
lists all attempts and repairs. No baseline success is an exclusion criterion.

## Word pairs

Read all 21,540 table words for anagram uniqueness. Eligible answers have
rank ≤10,000, length 4–8, and exactly one lexicon word with their sorted-letter
signature. Frequency terciles use source ranks 1–3333, 3334–6666, 6667–10000
(not terciles re-estimated after filtering). Repetition profile is sorted
character multiplicities, descending. Match length, tercile AND profile.
Each word appears in exactly one pair (1,000 unique words).

For each sorted (length,tercile,profile) group, shuffle rank-ordered words,
pair adjacent words, discard an odd leftover. Within each length×tercile
block shuffle those candidate pairs. Retain first admitted candidates until
quota: 34 in the first five lexicographic blocks, 33 in the other ten, total
500. Available matched-pair capacities are 84–224 per block; profile matching
therefore need not be relaxed. Base blocks omit profile as design §5 says.
No ordinal merges are needed/allowed for these fixed quotas.

For each word use two random letter permutations, rejecting identity,
same-word duplicate scramble, old scramble, BIG-bench key or repeated new
question. At most 1,000 permutation attempts per word; if exhausted reject
that candidate pair, keep the evidence, and try the next unused pair.
Four arm scrambles must all be distinct. Prompt: `Unscramble these letters
into one English word: <scramble>.` No options. Sham changes only scramble.
Oracle: independently parse the rendered scramble and lookup the full-table
sorted-letter signature; exactly one solution required. Vocabulary reuse is
allowed and counted, not called unseen vocabulary.

## Five-object deduction

Objects are five distinct book colors, sampled without replacement from
`red green blue orange yellow purple black white brown gray`. Draw an order
and independently shuffle the listed objects. Four adjacent-order relations
are always present. Graph class `chain4` uses just these four edges (endpoint
distance 4); `chain6` additionally uses order-index edges (0,2),(2,4)
(endpoint distance 2). Each edge is randomly worded as before or after.
No positional or explicit endpoint clue is allowed. These are 2 fixed graph
classes, not a claim of broad deduction diversity. Each gets 250 pairs.
Canonical clue order is shuffled; sham rotates that list by one position.
Both canonical queries use the identical ordered clues, changing only
`leftmost` to `rightmost`; both shams use the identical reordered clues.
Options are the five colors. The prompt fixes left-to-right linear order.
Oracle independently parses each relation and exhaustively tests all **120**
permutations. It must find exactly one total order, then answer the endpoint.
Base blocks: graph class/distance × unordered endpoint-option positions;
20 blocks of 25, no pooling. Reject reused full orders (including old orders,
regardless of context/query position) and old clue keys. Up to 100,000 draws
per slot, then stop with a shortfall rather than change the graph support.

## Unit interpretation

One noncommutative two-step dependency: count-per-cycle `n`, hours-per-cycle
`p`, required count `Q`; elapsed hours = **Q × p / n**. Swap the numerical
assignments of n and p; Q remains fixed. Three statements: `A machine makes
N parts per cycle.`, `Each cycle lasts P hours.`, `The required total is Q
parts.` Query: `How many hours are needed to make the required total?` No
partial-cycle restriction: constant rate, fractional cycles permitted,
explicitly stated. Three quantities distinct. Canonical statements use that
order; sham cyclically shifts them by one. Vocabulary, query unit, printed
number multiset and all five options identical across every arm.

Enumerate 2≤n<p≤30, multiplier m∈[2,12], Q=lcm(n,p)m≤5000; both answers
positive integers ≤9999. Five digit-length strata, 100 pairs each:
**(2,3), (2,4), (3,3), (3,4), (4,4)**. Enumeration before old-collision
filter supplies 616/443/711/1317/1038 parameter triples respectively. The
(2,2) class has only 68 and is not proposed. Operation/depth is fixed
`multiply_divide/depth2`; no nominal pooling or data-dependent digit merging.
Shuffle candidates within these five strata and retain first admitted.
Reject repeated sorted printed-number triple, including matching old unit
triples; scaling/subject changes do not excuse a repeat. Shared options are
both correct answers plus three sampled without replacement from the sorted
set `{Q,n*p,Q+n,Q+p,Q+n+p,p-n,n+p}` minus the targets. Distinct positive
numeric values required. Oracle parses statement roles independently, solves
cycles = required/parts-per-cycle then hours = cycles×hours-per-cycle using
`Fraction`, and requires exactly one numerically equal option.

## Shapes: explicitly narrowed quadrilateral support

Two nominal pair classes, 250 each: **square/kite** (answer length bin 4–6),
**rectangle/rhombus** (bin 7–10). All have exactly four nonzero line segments
and four genuine corners. Shared five options: square, rectangle, rhombus,
kite, trapezoid, in scheduled order. Only four classes are targets. This is
not the predecessor's ten-class diversity; only two label-pair base blocks.
Complexity is `closed_convex_four_segment`; there is no segment-count
counterfactual. Geometry uses exact integer coordinates, no tolerances.

Local constructors: square side s∈[6,40]; rectangle widths/heights∈[6,40],
unequal; rhombus edge vectors (a,b),(b,a), 2≤a≤30, 1≤b<a; kite vertices
(0,a),(b,0),(0,-c),(-b,0), a,b,c∈[6,40], a≠c. Apply integer similarity
(x,y)→(rx−ty,tx+ry), r∈[1,7], t∈[0,7], gcd(r,t)=1; translate each axis
by an integer in [-40,40]. Canonical start is a seeded cyclic rotation.
Sham rotates start by 1–3 and adds dx,dy∈[10,40]. Render `M x,y L x,y L
x,y L x,y L <start>` with explicit closure; never use an open polyline.
Reject repeated geometry including across pairs/old polygons using cyclic/
reversal-normalized squared-distance matrices (translation, rotation,
reflection invariant; scale retained). Reject whole candidate pair if
either member duplicates. Up to 100,000 draws per slot, then shortfall.

Prompt states the exclusive most-specific partition: square (four equal
sides/four right angles), else rectangle (four right angles), else rhombus
(four equal sides), else kite (two adjacent equal-side pairs), else trapezoid
(exactly one opposite parallel-side pair). Other polygons are inadmissible.
Independent oracle parses coordinates; rejects repeated vertices, collinear
corners, zero area, nonconvex/self-intersecting paths and unclosed paths;
computes exact cross products, dot products, squared lengths and parallel
edges, applies that priority, then verifies membership in the option set.
Audit sham transform itself, not merely equality of class labels.

## Collision surfaces and independent validation

Index **all** questions in eval/probe/shot records of the 101 pinned item
files, including literal shot tuples. Exact question equality checked across
all families. Also check whitespace-normalized questions without option
lines so a changed option order is no escape. Disclose coverage by source.
Parse old unscrambling strings from both historical frames, compare bare
scrambles. Word answers are counted for reuse, not excluded. Deduction old
`meta.order` is compared independent of context and queried endpoint;
`meta.clues` is normalized before/after and order-insensitive. Old unit
`n,p,shown` and `r,given` metadata support unordered-number checks; prior
single-quantity metric conversion is a different relation, disclosed.
Old shape M/L polygons parse exactly as decimal Fractions; repeated pen
re-statements are ignored only at the current point; closed polygons get
the invariant distance key. Arcs/open lines cannot equal a closed four-line
path and are counted as structurally incompatible. Do not claim unseen
mathematical isomorphisms or unseen vocabulary.

BIG-bench stores hashed strings, not parsable source examples. Check all
rendered full/stem strings against all index keys; additionally reconstruct
its old unscrambling frame (including trailing space), books paragraph
(both clue render orders), unit level-1 bell time-query frame for each role
assignment, and SVG shape frame with both integer and two-decimal coordinates.
This provides exact indexed-surface coverage, **not** a structural-content
certificate against unavailable BIG-bench source strings or all clue/vertex
permutations. Old committed schemas supply the stronger content gate.

Independent audit re-parses all 8,000 questions, verifies labels/options,
word uniqueness/matching, clue invariance and graph class, quantity swap and
exact equation, shape complexity/partition and actual sham transform, stored
content keys/base strata, no cross-pair content reuse, all counts and
counterbalance schedules. Any oracle/refusal/coverage mismatch is terminal.
Malformed question or unknown family yields a recorded refusal, never an
invented answer. The oracle module imports no generator code or metadata.

## Fixed shortcut baselines (before item inspection)

Each function receives **rendered question only** (plus full lexicon ranks
for frequency rules), never targets, latent facts or pair ID. Case-normalize
answers. Option ties always use first printed option. `None` denotes
abstention, distinct from nonapplicability. No success-based selection.

| Method | Exact behavior and applicability |
|---|---|
| constant | words `time`; deduction `red`; units `1`; shapes `square`, on every prompt |
| position1 … position5 | corresponding printed option, applicable only to the three option families |
| shortest / longest | shortest/longest option string, first-position ties; words: highest-frequency top-10k eligible-length word of the scrambled length (same rule for both because length is fixed), without letter-identity lookup |
| frequency | option with lowest lexicon rank, missing rank=∞, first-position ties; units nonapplicable (no word-frequency ordering); words same length-only most-frequent word rule |
| inputcopy | words: scrambled token; deduction: first listed color; units: first printed statement number; shapes: nonapplicable (coordinate copy is not an answer name) |
| absentoption | first option absent as a whole token from statement/clue/path body, excluding options, query and shared definition text; abstain if none; words nonapplicable (no options) |
| querywordonly | deduction: first listed color for leftmost, last listed color for rightmost; units: first option for `hours`; shapes: first option for `shape`; words: `time` (query has no discriminating word) |
| cluedegree | deduction only: count undirected clue incidences per color; choose minimum degree, tie first option, ignoring query direction |
| endpoint | deduction only: normalize before/after edges; for leftmost choose zero-indegree vertex, for rightmost zero-outdegree; tie first option; abstain if none; no chaining/exhaustive solver |
| numbers_min / numbers_max / numbers_sum / numbers_product / numbers_ratio | units only: ignore roles and order, use three statement numbers. Emit respectively min, max, sum, product, or max/min, Fraction canonical integer or numerator/denominator string; no nearest-option fallback |
| segmentcount | shapes only: 4 segments→`rectangle` (otherwise abstain) |
| boundingbox | shapes only: equal x/y extents→`square`, otherwise `rectangle`, without angles/side lengths |

All other family×method cells are nonapplicable with reasons. For each
applicable cell report prompt attempts/emissions/abstentions, canonical and
sham paired success (each /500), and conditional shift exactly as design §4
with deterministic k=1: both outputs in {a0,a1} required, else render x=0.
Report supported-only mean, unsupported **rows** (/2000) and unsupported
**renders** (/1000), average per-pair x and raw d/u. Nonapplicable cells have
null scores/zero denominators, not failures. A target-sensitive shortcut may
score perfectly and remains in the battery, explicitly limiting interpretation.

## Test/repair policy

TDD miniature known examples/attacks before full run: ambiguous words and
geometry, nonunique/cyclic deduction, zero unit denominator, missing options,
reversed labels, sham drift with same answer class, duplicate content/words,
singleton blocks, malformed parser inputs and oracle totality. Full certificate
tests entire batch. Source hash/coverage/matching failure stops. Genuine
support shortage returns for a design ruling; implementation bugs may be
repaired with append-only ledger, preserving attempt evidence. No substantive
constraint changes after inspecting shortcut results.
