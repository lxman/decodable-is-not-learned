# Experiment 7 — generation-only feasibility

Owner approval: 2026-10-04, §10 of `experiment-7-design.md`. This stage asks
whether the proposed battery can be supplied and independently checked. It
does not collect or analyze any model output. Source snapshot at approval:
`2d14da44ad882139bc95264697b03d45fe109354`.

## Deliverables

1. Deterministic four-arm pairs, 500 per family: unscrambling, deduction5,
   unit interpretation, shapes. JSON records include canonical/sham questions,
   answers, shared options where relevant, latent construction facts, base
   strata and content keys. New seed namespace `2026100407`; per-family streams.
2. Independent oracles that parse the rendered question, not just generator
   metadata: lexicon anagram lookup, exhaustive order constraint solver,
   dimensional equation evaluation, geometric path classification. Compare
   oracle answers with recorded targets for all four arms; require uniqueness.
3. Collision audit against each other, all committed old experiment item files
   and the available BIG-bench key index. Exact rendered questions alone are
   not enough: check structural content where old schemas support it, and
   disclose exactly which old surfaces/keys were checked.
4. Coverage, source pins, base-block support, counterbalance, shortcut-baseline
   tables, worked examples and prototype tests. Reproducible certificate from
   committed code. A fresh reviewer checks the certificate/code before it is
   used to write the instrument build plan.

## Nonnegotiable requirements from the approved design

- Distinct normalized counterfactual answers, unchanged options/order across
  all four arms, and identical target answers under the meaning-preserving
  transformations. No target or pair orientation chosen from model output.
- Unscrambling: use the committed `words_6.tsv` dictionary and frequency ranks;
  unique solution relative to the entire table; top-10,000 source vocabulary,
  same length and source-frequency tercile, same repetition profile if it
  supplies 500 disjoint pairs. Each word used by one pair. Each of four
  scramblings distinct from its answer and the other render of that answer.
- Deduction: five objects; a unique total order; query both opposite endpoints
  of the same clues; no explicit endpoint-position clue. Reorder clues for
  shams, preserve their meaning. Check all 120 candidate orders independently.
- Units: exchange distinct numerical assignments to distinct dimensional roles,
  keeping the quantity multiset, role vocabulary, query unit and five options.
  Use a noncommutative relation with exact rational/integer oracle arithmetic.
  Sham reorders statements. Every candidate answer distinct. No float-rounding
  tie or ambiguous unit convention.
- Shapes: counterfactuals with equal path-segment/complexity counts and
  answer-name length bin; same option list/order. Closed polygon path, sham
  translation and cyclic start change. Oracle classes form an exclusive
  partition with any specificity convention stated in the question. Simpler
  quadrilateral classes are permissible, but their narrowed support must be
  explicit; neither “four families” nor 500 pairs establishes label diversity.
- All base-block sizes printed, minimum target 10 per retained base block.
  Ordinal merge rules fixed before selection; nominal blocks never combined
  after the fact. No filtering by model or baseline success.

## Exact choices before generated-item inspection

The implementer first writes `SPEC.md`: concrete answer lengths/word strata,
deduction clue classes, unit equations/ranges, shape classes/length bins,
counterbalance scheme, collision keys, model-free baseline behavior (including
tie breaking/abstention) and rejection rules. Commit and push that specification
before a full generation or shortcut audit. Any subsequent choice changes get
an append-only rationale. Pure miniature tests may precede full generation.

The baseline list is fixed now: constant answer; option position; answer
length/frequency; input-copy; option absent from the question; query-word-only;
clue-degree/endpoint; dimensional-role-blind numeric rules; path segment-count
and bounding-box rules. Each is either executable with an exact rule or
explicitly nonapplicable with a reason. No undefined baseline silently counts
as wrong. Print paired success and conditional selectivity with coverage;
these are shortcut audits, not model results or exclusion gates.

## Execution and limits

Standard-library/numpy generation only; no torch, transformers, MLX, tokenizer,
model loader, model endpoint, rented box, network or predecessor analyzer.
Read committed input resources directly or via safe pure helpers; pin them.
Each full generation gets a distinct output directory and run receipt. Unlike
the later once-only verdict, generation can be repaired and rechecked when a
model-free defect is found, with every attempt ledgered and old evidence kept.
Do not relax a substantive approved requirement to turn a shortfall into a pass.

The fresh implementer owns this feasibility package only; management owns the
design/ledger and subsequent build plan. Test oracle disagreement, sham drift,
answer collisions, options mismatch, duplicates, ambiguous geometry, singleton
strata, and seed determinism. Check the entire generated batch, not a sample.
