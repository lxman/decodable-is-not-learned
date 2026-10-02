# Experiment 6 — Progress Ledger

Design: ../../experiment-6-design.md (dials a–u RULED 2026-09-27).
Battery plan: ../../docs/superpowers/plans/2026-09-27-exp6-battery.md.
Entries are append-only. Every network contact is logged here when made.

## Model contact

One, by accident, on 2026-09-28: the weights of SmolLM3-3B's stage-1 endpoint were fetched and
loaded into memory by a test run. No tokenizer was loaded, no forward pass ran, no item was
read by a model and nothing was scored. The entry "Model contact, 2026-09-28" at the end of
this ledger has the account. (This section read "None." until that entry was written.)

## Network contacts (build)

- 2026-09-27: `pip install --no-deps pyfiglet==1.0.4 eng_to_ipa==0.0.2` — installed clean, no other packages pulled in; stack confirmed unmoved (`torch 2.12.1, transformers 5.13.0, numpy 2.4.6`).
- 2026-09-27: `https://www.norvig.com/ngrams/count_1w.txt` → scratch directory, sha256 `51df159fd3de12b20e403c108f526e96dbd723d9cabdd5f17955cdc16059e690` (matches the pin in `make_data_6.py`). Not committed.
- 2026-09-27: fourteen `task.json` files from `google/BIG-bench` at commit `092b196c1f8f14a54bbc62f24759d43bde46dd3b` → scratch directory (`modified_arithmetic/{three_digit_addition_plus_one,three_digit_subtraction_plus_one,two_digit_multiplication_plus_one}`, `word_unscrambling`, `word_sorting`, `international_phonetic_alphabet_transliterate`, `logical_deduction/{three_objects,five_objects}`, `ascii_word_recognition`, `geometric_shapes`, `temporal_sequences`, `cs_algorithms/lcs`, `unit_interpretation/{lv1,lv2}`). Not committed — only their hashes, in `bigbench_index_6.json`. `SOURCES` enumerates fourteen paths, not the fifteen the brief's prose names; the generated index's sha and every `n_keys` value match the pins exactly.

## Plan deltas awaiting ratification

B-1 … B-12, as listed in the battery plan.

## Tasks

### Task 1 — verify_6.py: five answer types (number and word are 2c's normalizer, imported), budgets 8/12/12/16/24, draw side total over 20,016 fuzzed strings per type, answer side a hard error; 8 tests.

### Task 2 — battery/spec.py: RungSpec, the registry (duplicate names and seeds refused, two-way choices refused), check_item, the driver (500 eval + 2 shots on one stream; redraw on reject / duplicate / collision / repeated answer); 9 tests.

### Task 3 — the vendored data: words_6.tsv (21,540 rows; 9,128 in the top 10,000; 7,649 with exactly one CMUdict pronunciation) sha 1e19db04…; bigbench_index_6.json (17,749 hashes over ten tasks at BIG-bench 092b196c, no BIG-bench text) sha 0970e986…; 7 tests. Network contacts logged above.

### Fix round 1 (Tasks 1–3, 2026-09-27)

- Task 1, from its review: the totality test never reached the `except IndexError` branch it guards (seed 0 draws no trigger). Added `test_the_2c_word_path_raises_and_verify_6_absorbs_it` over five strings on which 2c's word path raises, and added them to the fuzz list (20,021 strings per type); the answer side now turns that IndexError into its documented ValueError; two invisible whitespace literals in the test (U+2009, U+00A0) are explicit escapes. 9 tests.
- Task 2, from its review: `check_item` type-checked the question and nothing else — an answer of None would have been written as the string "None". `question`, `answer` and `bb_key` must be non-empty strings and `meta` a JSON-serialisable dict; a spec with an empty name is refused. 11 tests.
- Task 3: the ledger said 18,749 hashes; the index holds 17,749 (the sum of its ten `n_keys`). The plan had also said fifteen task files; fourteen were fetched, as logged above.
- Event, disclosed: Task 3's nine files were committed inside 8ab89e660, a plan-text commit made by the controller while they were staged. The content is as the task specifies (shas equal the pins); the history is not rewritten.
- Suite: 27 passed.

### Task 4 — generators A: eleven rungs (modarith ×3, lcs, unscramble ×2, sort ×2, ipa_word, unit_interp ×2), each test recomputing the answer independently; design strata balanced by slot; 13 tests.

### Task 4, fix round 1 — the collision keys are BIG-bench's own wording (coordinator rulings R-11, R-12, R-14)

The Task 3 reviewer asked whether the generators' keys have BIG-bench's format. The coordinator ran the
check as an audit of every BIG-bench string (the tool lands in Task 5) and it failed on unit
interpretation: 4 of BIG-bench's 50 strings carry a grammar slip ("If they takes", a capital "They"
after a comma, "one forth") that the keys had corrected, so the gate could not have seen a
reproduction of them. Closed: gen_units renders each sentence on two surfaces — "battery" (what a
model reads, corrected) and "bigbench" (the key, the task files' wording byte for byte); the
reporter's scaled clause drops its object, as the task file's does. gen_arith and gen_words build
their keys through named renderers; no item of theirs changes. unit_interp2 records
meta.answer_stated (71 of 500: the sentence states the quantity asked; BIG-bench's own class;
flagged, not excluded). unscramble_short's description names the table its uniqueness check runs
over (21,540 rows, not 25,000 words). The tests rebuild every item's key from the item's own record
through the renderers. 17 tests, 44 in the suite.

### Task 5 — generators B: six rungs (ascii ×2, shapes, deduction ×2, temporal) and generate.py; every deduction puzzle unique and minimal by brute force; shapes and temporal disclosed as reconstructions (B-2); the collision keys AUDITED against BIG-bench's 17,749 key strings through the generators' own renderers — 17,244 identical, 505 outside for two stated reasons, 0 failed; record sha d012b7b3…, 69 known answers sha 8ab3e7c7… (arguments, not text; the canary carried); 26 tests.
- The audit read the fourteen task files from the coordinator's scratch directory (the files Task 3 downloaded; each file's sha256 checked against the index before it was read). No network contact in this task.

### Task 6 — the seventeen item files (4.4 MB, shas = ITEMS_SHA_PIN_6, generated twice byte-identical), battery_6 / floors_6 / strata_6, the token record (sha cca2df32…); floors: choice rungs at 1/n, lcs and shapes at .10, free-form rungs at .002–.016; strata: every stratum ≥ 10 items, anchors equal to 2g's committed rows; 17 tests, 87 in the suite.
- The token record was measured OFFLINE from the coordinator's scratch cache (coordinator ruling R-16). The seven tokenizer revisions — read them from `token_lengths_6.json` — were downloaded once, by the coordinator, at the prototype stage on 2026-09-27: tokenizer files only, about 62 MB, no weight. No network contact in this task.
- The seventeen item files were generated twice; the seventeen sha256 lines were identical both times and equal `ITEMS_SHA_PIN_6`.

### Tasks 5 and 6, fix round 1 — polygons keep their corners; the audit admits arguments only in the generators' support; items are written only behind the audited gate (coordinator rulings R-17 … R-20)

Task 5's review checked the generators against BIG-bench's own answers — 800 of 800 deduction
examples and 1,000 of 1,000 temporal examples reproduce under the generator's tables — and found two
defects. (1) The shape generator admitted polygons with a nearly straight vertex: 113 of the 350
polygon items had a vertex within 15 degrees of straight, the straightest at 0.54 degrees on an
"octagon" that draws a heptagon; BIG-bench's hand-made set has 12 of 252. A draw with a vertex
turning the path by less than 15 degrees is now rejected (plan delta B-17); none of the 350 is
within 15 degrees. (2) Several of the audit's parsers passed their arguments through and could not
fail. Every parser now admits an argument only in the generator's support; the same parsers read
the key of every generated item (8,500 keys; all parse and render back); each row of the record
says what it establishes. The audit now reads 16,655 identical, 1,094 outside the generators'
support for four stated reasons (87 sort tokens outside a-z, 502 IPA sentences, 501 IPA-direction
strings, 4 spelled-out counts), 0 failed. The item writer refuses unless the committed audit record
is the pinned one, holds no failure, and is of the generator files and spec.py as they are on disk;
every item file's provenance names the record (plan delta B-18), so all seventeen item files and
their pins change. Each deduction sentence is now checked against the clue it renders, from tables
written in the test from English. The audit read the coordinator's scratch copy of the fourteen
task files; the token record was re-measured offline from the coordinator's scratch cache (R-16).
No network contact. 16 + 15 + 17 tests in the three files; 92 in the suite.

### Fix wave 2 (Tasks 1, 2, 4, 5, 6) — what a firing test would mean (coordinator rulings R-21 … R-27)

Task 6's review recomputed every item of ten rungs from its question text and found no wrong answer.
Its findings were about easy classes and floors, and each was checked against BIG-bench's own task
files before it was ruled on.
- The unit rungs' options were skewed, and the skew was this battery's: the answer was the smallest or
  the largest of the five in 20 of 500 items on level 1 and never the largest on level 2, so a guesser
  picking one rank by size scored .45 and .37 against a floor of .20. BIG-bench spreads the answer over
  all five ranks. The answer's rank of size is now designed and cycles with the slot, one level slower
  than its list position; the best single rank scores 100 and 120 of 500 (plan delta B-19).
- Two shortcuts are BIG-bench's own construction and are left in, measured: on `temporal` the right
  interval is the only option the text does not mention, on 500 of 500 items here and 1,000 of 1,000 in
  BIG-bench; on `lcs` the answer follows the strings' length (a length-only rule scores 210 of 500
  here, .40 on BIG-bench's 320). Both are pinned as HEURISTIC FLOORS and will be printed beside every
  count (B-22).
- The easy classes the strata do not condition on are counted and pinned as STRUCTURE LEVELS, for a
  named secondary that crosses them into the strata (B-21); the primary's strata are the design's.
- The two shots are drawn 37 slots apart, so they share no designed value; at consecutive slots they
  shared the answer's position on four rungs and showed only the answers 0 and 1 on `lcs` (B-20).
- The audit's path grammar admits no negative number and holds a path's points to the generator's box;
  `collisions_6.py` joins the files the record binds. The audit reads 16,654 identical, 1,095 outside
  the generators' support for five stated reasons, 0 failed.
- `verify_6` resolves 2c's harness once. A `number` or `word` verification cost 118 microseconds, of
  which 117 were two path lookups; it costs under one now. Behaviour unchanged.
- Three refusals that had no test have one: the pin checks, an option set that omits the answer, a
  tampered control file.
All seventeen item files, the audit record, the token record and every pin were regenerated. The audit
read the coordinator's scratch copy of the fourteen task files; the token record was measured offline
from the coordinator's scratch cache (R-16). No network contact. 102 tests in the suite.

### Fix wave 3 (Tasks 1–6) — the final review's findings (coordinator rulings R-28 … R-35)

The final whole-branch review (on 33d817962) recomputed the answers of twelve rungs and found none
wrong. Its findings, each checked against BIG-bench's own task files before it was ruled on:
- `lcs`: the per-answer length windows were this battery's and made BIG-bench's length cue stronger
  than BIG-bench's. Both lengths are now uniform on 4–31 whatever the target; a draw is kept if its
  longest common subsequence has the target length (11,909 rejected draws; fifty items per answer).
  The answer's correlation with the shorter length is .900 (BIG-bench: .889). This revises the
  "not changed" of fix wave 2 (plan delta B-24).
- The unit rungs' random fills shared no factor with the sentence's numbers while the answer did, so
  "pick an option a number of the text divides" scored .33 on level 1. Fix wave 2's rank design had
  introduced it. A fill is now a multiple of a number the sentence states; the rule scores .22 and
  .16 against a floor of .20 (B-25).
- The heuristic floor has eight guessers, not four, and a guesser that learns a table is scored on
  items it has not seen (two halves of blocks of ten slots). `temporal` stays at 500 of 500.
  `lcs`: 115 of 500 (it was 210 in sample). Unit rungs: 124 and 156 (B-22).
- On the `modarith` rungs the pair asked is a second collision key, gated against every pair
  BIG-bench prints on any line: 16,466 hashes in the index's extra table. Before it, 51 of
  `modarith_mul1`'s items asked a pair BIG-bench asks and 231 a pair it prints. After: none.
  The audit parses and renders back all 16,466 (B-26).
- The content an item can share with BIG-bench inside a new string is counted by `overlap_6.py`, the
  record pinned and bound to the index and the item files. The answer is a BIG-bench unscrambling
  target on 491 and 497 of 500 items; a word of the list is in a BIG-bench sorting list on 369 and
  434; the `ipa_word` word occurs in a BIG-bench sentence on 95; no `lcs` string is BIG-bench's.
  Nothing is excluded on these counts (B-28).
- `ipa_word` is scored by exact match against one transcription convention. Disclosed; whether the
  transcription carries a stress mark is a structure level (312 of 500) (B-27, B-21).
- An item file keeps its two shots' keys (`shot_records`), and the audit's parsers read them: 8,534
  keys and 1,506 pair keys parse and render back (B-30).
- Refusals that had no test have one: the structure and heuristic pin checks, five header guards of
  the item loader, a floor outside the unit interval. The wall-clock test of `verify_6` is replaced
  by a count of path resolutions.

Corrections to this ledger, made here and not in place:
- NETWORK CONTACTS OF THE PROTOTYPE STAGE, not logged when made. Before Task 3 the coordinator
  fetched, into a session scratch directory, none of it committed: fifteen BIG-bench `task.json`
  files at commit 092b196c (the fourteen of `SOURCES` and `logic_grid_puzzle`, read to decide B-1),
  twice; six task READMEs at the same commit (cs_algorithms, geometric_shapes, logic_grid_puzzle,
  logical_deduction, temporal_sequences, unit_interpretation); `pyfiglet==1.0.4` and
  `eng_to_ipa==0.0.2` by `pip install --target` into the scratch directory; `count_1w.txt`; and the
  tokenizer and config files (`tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`,
  `config.json`; 62 MB in all; no weight file) of thirteen revisions of eight Hugging Face
  repositories — EleutherAI/pythia-1b, EleutherAI/pythia-410m, allenai/OLMo-2-0425-1B,
  allenai/OLMo-2-1124-7B, allenai/OLMo-2-1124-13B, common-pile/comma-v0.1-1t,
  HuggingFaceTB/SmolLM3-3B-checkpoints, HuggingFaceTB/SmolLM3-3B-Base — of which the token record
  names seven. The section "Model contact: None" stands: no weight was fetched and no model ran.
- The ledger's header says entries are append-only; at fix round 1 the hash count of Task 3's entry
  was corrected in a later entry, and that is the practice. Counts in earlier entries describe the
  files of their commit: "71" and "72" stated answers on `unit_interp2` were both right when
  written; the committed items now hold 76.

The index, the audit record, the known answers, all seventeen item files, the token record, the
overlap record and every pin were regenerated. The index was rebuilt, and the audit and the overlap
count run, on the coordinator's scratch copy of the task files (each file's sha256 checked against
the index); the token record was measured offline from the coordinator's scratch cache (R-16).
No network contact in this wave. 118 tests in the suite.

### Fix wave 4 (Tasks 3–6) — the re-review of fix wave 3 (coordinator rulings R-36 … R-41)

The re-review (on 0160f669b) recomputed every answer of the six rungs fix wave 3 had changed, from
the question text alone, and found none wrong. It found four things that change what a result
would mean. Each was recomputed by the coordinator and each is right.
- THE UNIT RUNGS ARE REBUILT ON THE README'S RULE (plan delta B-25). A fixed rule — among the
  options the text does not print, the smallest that divides none of its numbers — scored .556 on
  `unit_interp1` against .20 on BIG-bench's own items. Two fix waves had patched the options; the
  cause was upstream of both. BIG-bench's README defines the generation: numbers without large
  prime factors, least common multiples so that every combination of an item's numbers is an
  integer, wrong options mostly the wrong combinations of those numbers and otherwise pool
  numbers. The generator now does that: numbers with no prime factor above 5, one pool for both
  of the rate's numbers, the shown quantity the least common multiple times 1–12, no number above
  5,000, a wrong option a combination three times in four and a pool number once in four on
  either side of the answer. The answer's position and its rank by size are crossed over blocks
  of slots (B-19): level 1 holds every pair twenty times; level 2 every position and rank on 96
  to 102 items. `unit_interp2` flags 57 stated answers.
- THE HEURISTIC FLOOR HAS FOURTEEN GUESSERS AND EVERY COUNT IS PINNED (B-22). Best of the list:
  `temporal` 500 of 500; `lcs` 237 (the letters the two strings share; BIG-bench .46);
  `unit_interp1` 191; `unit_interp2` 222 (BIG-bench's 25 items a level: .28–.36 and .52).
  The share of combinations among the wrong options was scanned from .5 to .9 on three seeds a
  rung before three in four was taken (best fixed rule .41–.48 and .41–.47 across the scan).
- A FITTED guesser — a logistic regression and a gradient-boosted classifier on twenty surface
  features, half the rung against the other — scores .552 / .656 on `unit_interp1` and .626 /
  .746 on `unit_interp2`; fitted on a rung and applied to BIG-bench's 25 items, .28 to .40; on
  BIG-bench's items by leave-one-out, .16 to .40 (`tools/guessers_lab_6.py`, scikit-learn 1.9.0;
  nothing written, nothing gated). Disclosed as B-32, with the option of dropping the two rungs
  put to Michael.
- ON THE `modarith` RUNGS A PAIR IS GATED EITHER WAY ROUND (B-26). 185 of `modarith_mul1`'s
  queries asked a×b where BIG-bench prints b×a. The index's extra table holds a commuting pair
  both ways round (24,712 hashes: 11,920 / 5,983 / 6,809); the operands are drawn on BIG-bench's
  ranges, 0–998 and 0–98; 7 / 3 / 1,026 draws were redrawn.
- THE CONTENT OVERLAP OF `ipa_word` WAS UNDERCOUNTED (B-28). The first tool read one direction of
  BIG-bench's IPA file. Read in both shapes and both directions: 148 of the 500 words occur in
  BIG-bench's sentences (not 95) and 158 of the answers are tokens of BIG-bench's IPA text.
- The unit rungs' structure level is the kind of scaling crossed with the answer's rank by size
  (B-21). `deduction3`'s second shot is a read-off item, left as drawn (B-33).

Corrections to this ledger, made here and not in place:
- The entry of fix wave 3 says the prototype stage fetched tokenizer files of THIRTEEN revisions;
  the scratch cache holds twelve (eight repositories, 48 files, 62 MB, no weight).
- The same entry gives `lcs`'s heuristic floor as 115 of 500 and the unit rungs' as 124 and 156:
  those were the best of the guessers then listed. With the letter guessers `lcs` reads 237.
- BIG-bench's unscrambling file holds 8,917 examples and 9,719 distinct target words.

The index, the audit record, the known answers (77), all seventeen item files, the token record,
the overlap record and every pin were regenerated. The index was rebuilt, and the audit, the
overlap count and the guessers' fit run, on the coordinator's scratch copy of the task files (each
file's sha256 checked against the index); the token record was measured offline from the
coordinator's scratch cache (R-16). No network contact in this wave. 122 tests in the suite.

### Fix wave 5 (Tasks 4–6) — the re-review of fix wave 4 (coordinator rulings R-42 … R-47)

The re-review (on 398ac11ed) recomputed every answer of the unit and `modarith` rungs from the
question text alone, shots included, and found none wrong. It found three things on the unit
rungs that change what a result would mean. Each was recomputed by the coordinator and each is
right; the coordinator's own check of the first repair found a fourth.
- THE WRONG READINGS WERE MISSING FROM THE OPTIONS (the review's I-1). Fix wave 4 drew a wrong
  "combination" uniformly from every pattern of the item's numbers, so the readings the task
  exists to test were offered only when the draw landed on them: the reversed rate on 151 of
  level 1's 500 items, where BIG-bench offers it on 23 of 25. A rule that combines every stated
  number once and reads no unit scored .72 on level 1 and .47 on level 2 (BIG-bench .48, .28).
- THE FIRST REPAIR OPENED ANOTHER DOOR, found by the coordinator's fitted guessers before any
  commit. With the wrong readings placed on the sides a DESIGNED rank by size left room for, the
  options above and below a reading said whether it was the answer; and level 2's stated
  quantity was a multiple of the rate's square when it was in the rate's first unit, so its size
  told its unit. A fitted guesser scored .47 on level 1 and .69 to .75 on level 2.
- THE UNIT RUNGS' NUMBERS AND OPTIONS ARE NOW DRAWN WITHOUT REGARD TO WHAT IS ASKED (plan delta
  B-34). The numbers are drawn the same way whatever the roles of the units, and a draw is
  refused when ANY reading of its sentence exceeds 5,000. The options hold the CANDIDATES — the
  answer of every sentence that prints the same numbers and differs in the roles alone (level 1:
  in the direction of the scaling too): two on an unscaled item, four on a scaled one — and
  fills by the README's rule (B-25). Which candidate is the answer decides its place in the
  list, set by the slot, and nothing else. A test draws the sentences of a group from one state
  of the generator: same numbers, same five options, refused together, their answers the
  candidates, one each. What is asked and the kind of scaling are cells set by the slot: six of
  83 or 84 items on level 1; on level 2 two unscaled cells of 83 and 84 and eight scaled cells
  of 41 or 42. The answer's rank by size is no longer designed (B-19): 78 / 86 / 104 / 129 / 103
  and 127 / 86 / 88 / 105 / 94 items at ranks 1 to 5. `unit_interp2` flags 84 stated answers.
  On level 1 a rate of one, a rate equal to the scaling factor and a sentence that would restate
  its own rate are refused; on level 2 a rate equal to the factor or to its square root.
- THE HEURISTIC FLOOR HAS SIXTEEN GUESSERS (B-22): the review's two rules joined the list. Best
  of the list: `unit_interp1` 158 of 500 by combining every number once (BIG-bench .48; twelve
  other seeds .30 to .37); `unit_interp2` 166 by the product of two stated numbers (BIG-bench
  .52; 166 at every seed: the product is always offered and is the answer on four slots in
  twelve). The rank guesser 129 and 127. `temporal` 500 and `lcs` 237, unchanged.
- FITTED guessers (`tools/guessers_lab_6.py`, scikit-learn 1.9.0; nothing written, nothing
  gated) score .258 / .268 held out on `unit_interp1` and .288 / .304 on `unit_interp2`; fitted
  on a rung and applied to BIG-bench's 25 items .16 to .40; fitted on BIG-bench's items and
  applied to the rung .20 to .34; on BIG-bench's items by leave-one-out .16 to .40 (B-32).
- The unit rungs' structure level is the kind of scaling crossed with what is asked (B-21): six
  levels and ten. Of 2,000 wrong options a level, 1,182 and 1,401 are wrong readings of the
  sentence, 606 and 351 other combinations of its numbers, 212 and 248 pool numbers.
- The content overlap record gains a row: a `modarith` item shows a worked pair BIG-bench prints
  on 16 / 13 / 468 items, and either way round on 28 / 13 / 499 (B-26).

Corrections to this ledger, made here and not in place:
- The entry of fix wave 4 says least common multiples make "every combination of an item's
  numbers" an integer. False on level 1: 287 of its 500 items have a combination that is not
  (none of level 2's). What holds, and is tested: every READING of a sentence is an integer, and
  no other number is offered unless it is one.
- The same entry says "the generator now does that" of the README's rule for wrong options. It
  did not: see the first bullet above.
- The plan of fix wave 4 (B-32) said no fixed rule scored above .44 on the unit rungs. False
  when written: the review's rules scored .47 and .72 on those items.
- The same plan (B-26) gave the share of `modarith_mul1`'s pairs that BIG-bench prints as 68 %.
  It is 6,809 of 9,801, 69.5 %.

The audit record, all seventeen item files (an item file names the audit record, which names the
generator files), the token record, the overlap record and every pin were regenerated; the index
and the known answers (77) are unchanged. The audit, the overlap count and the guessers' fit ran
on the coordinator's scratch copy of the task files (each file's sha256 checked against the
index); the token record was measured offline from the coordinator's scratch cache (R-16). No
network contact in this wave. 127 tests in the suite.

### Fix wave 6 (Tasks 2, 4–6) — the re-review of fix wave 5 (coordinator rulings R-48 … R-53)

The re-review (on 76600eb18) recomputed every answer of the two unit rungs from the question
text alone, shots included, and found none wrong. It attacked fix wave 5's claim — an item's
numbers and options say nothing of what it asks — with fixed rules and fitted models of its
own, overall and per cell, and found no property that tells the answer; it worked out the bound
for a reader who does not read the roles (a third) and found it right. Verdict: ready with
fixes. Each finding below was recomputed by the coordinator before it was ruled.
- A RULE THAT READS TWO UNIT WORDS SCORES A HALF ON LEVEL 2 (the review's I-1, plan delta B-22).
  Where the blank carries the unit word of the stated number, the stated number; otherwise the
  product of the two printed numbers. 250 of 500 at every seed, by the design's cells (the
  stated quantity is the answer on 84 items, the product on 166); .60 on BIG-bench's own 25
  items. It is the task's texture and not the generator's, and it was outside the heuristic
  floor's list. It is now the list's SEVENTEENTH guesser: `unit_interp2`'s heuristic floor is
  250 of 500, and 166 by the best rule that reads no unit word. `unit_interp1`: 170, by
  combining every number once (BIG-bench .48); the unit-word rule scores 92 there.
- THE TEST OF THE CLAIM DID NOT SEE THE ORDER OF THE OPTIONS (I-2, B-34). The reviewer broke the
  generator fourteen ways in a scratch copy; two breaks — the options that are not the answer
  listed by size, always or only under one role — passed every test but the byte pins. The five
  options are now put in an order drawn without the answer in view and the answer is moved to
  its place; the test draws 2,500 groups a level and asserts that any two sentences of a group
  list every option that is neither's answer in the same order, and that in every cell the four
  options that are not the answer stand in each of the 24 orders by size about as often as in
  any other. Both breaks, and five more of the coordinator's, fail that test alone.
- NO ANSWER IS COPIED FROM ITS SENTENCE OUTSIDE THE FLAGGED CLASS, AND NONE IS 1 (M-c, B-25). The
  build of fix wave 5 had 12 and 21 answers that were a number the sentence prints and 16
  answers of 1 ("1 hours"); BIG-bench has none. A draw is now refused when a candidate is 1 or a
  number the sentence prints, level 2's stated quantity aside — on the item's numbers alone,
  never on what it asks.
- A SHOT DOES NOT ASK WHAT AN EVAL ITEM ASKS (M-d, B-35). `unit_interp2`'s item at slot 141
  repeated the second shot's numbers and roles under another subject. The driver takes an
  optional content key from a draw and redraws a shot whose key an eval item carries.
- The numbers, on the committed items: answers at ranks 1 to 5 by size, 54 / 96 / 118 / 106 /
  126 and 131 / 85 / 75 / 90 / 119; the rank guesser 126 and 131. Of 2,000 wrong options a
  level, 1,180 and 1,424 wrong readings of the sentence, 584 and 326 other combinations of its
  numbers, 236 and 250 pool numbers. `unit_interp2` flags 84 stated answers. Over forty other
  seeds (the rung's seed times 100, plus 0 to 39) the best rule that reads no unit word scores
  148 to 188 of 500 on level 1 and 166 to 172 on level 2.
- FITTED guessers (`tools/guessers_lab_6.py`, scikit-learn 1.9.0; nothing written, nothing
  gated), held out: on the tool's twenty surface features .288 / .284 on `unit_interp1` and
  .316 / .314 on `unit_interp2`; told which combination of the text's numbers an option is
  (twenty-one more features), .324 / .336 and .312 / .294. The bound is a third.

Corrections to this ledger, made here and not in place:
- The entry of fix wave 5 gives "twelve other seeds .30 to .37" without naming the seeds, and
  the review could not reproduce the range. The seeds were the rung's seed times 100, plus 0 to
  11. The range over forty is given above.
- The same entry says 287 of level 1's items have a combination of their numbers that is not an
  integer, "none of level 2's". That holds with each number used at most once. With a number
  used twice, as the fills may use it, it is nearly every item of both levels.
- The same entry says the fitted guessers scored "no more than the fixed rules". True, and
  weak: the tool's twenty features could not find the candidates. See the last bullet above.
- The same entry's fitted scores for the uncommitted first repair (.47; .69 to .75) are the
  coordinator's scratch measurements; no committed build reproduces them.

The audit record, all seventeen item files (an item file names the audit record, which names
`spec.py` and the generator files), the token record, the overlap record and every pin were
regenerated; the index and the known answers (77) are unchanged. The audit, the overlap count
and the guessers' fit ran on the coordinator's scratch copy of the task files (each file's
sha256 checked against the index); the token record was measured offline from the coordinator's
scratch cache (R-16). No network contact in this wave. 129 tests in the suite.

### Fix wave 7 (Tasks 2, 4–6) — the re-review of fix wave 6 (coordinator rulings R-54 … R-59)

The re-review (on 375778a06) recomputed every answer of the two unit rungs from the question
text alone with a parser of its own and found none wrong. It re-ran the twin check on 20,000
seeds a level, fitted models that know the candidates in every visible group, and broke the
generator eighteen ways in a scratch copy: no property of an item told the answer, and no break
of the order or of the refusals passed the suite. Verdict: ready with fixes. One Important
finding and three Minor ones; each was recomputed by the coordinator before it was ruled.
- THE SHOT GATE WAS UNTESTED WHERE IT MATTERED AND GATED LESS THAN IT SAID (the review's I-1, plan
  delta B-35). A content key that also named the subject — which reopens the case the gate was
  built for — passed every test. And on level 2, where the numerator quantity does not change
  with the scaling, two sentences with the same numbers and roles and different scalings share
  an answer and had different keys: over forty seeds, 20 items in 13 batteries printed a shot's
  numbers and had its answer (on the committed rungs, none). The key is now the numbers a
  sentence prints together with its answer, whatever the subject, the scaling or the roles. A
  test draws one state of the generator under another subject (the same key), another role
  (another key) and, on level 2, the other scaling with the invariant asked (the same key); four
  breaks of the key fail that test alone. Over forty seeds the gate redraws 2 shots on level 1
  and 44 on level 2; on the committed rungs, none.
- NO OPTION IS 1 (M-3, B-25). The build of fix wave 6 offered 1 as a wrong option on 10 and 6
  items ("() seconds", "1"); BIG-bench offers it on none. An operator's precedence had left it
  among level 1's combinations. 1 is out of the fills on both levels and the test says so.
- THREE UNIT WORDS AND NO SCALING SOLVE TWO THIRDS OF LEVEL 2 (M-1, B-29). Copy the stated
  number, multiply by the rate or divide by it, as the unit words say, and never read the
  scaling: 334 of 500 at every seed, 19 of BIG-bench's 25. The rule reads the roles and does the
  rate's arithmetic; it is disclosed and is not in the heuristic floor, whose .50 it clears.
- The test of the options' order is a chi-square on 23 degrees of freedom, below 60 in every
  cell (M-4); the sixteen cells read 8 to 32.
- The numbers, on the committed items: best of the heuristic list 170 of 500 on `unit_interp1`
  and 250 on `unit_interp2` (166 by the best rule that reads no unit word); the rank guesser 126
  and 132; answers at ranks 1 to 5 by size, 55 / 96 / 119 / 104 / 126 and 132 / 84 / 76 / 91 /
  117; of 2,000 wrong options a level, 1,182 and 1,415 wrong readings of the sentence, 582 and
  335 other combinations of its numbers, 236 and 250 pool numbers. Over forty other seeds the
  best rule that reads no unit word scores 146 to 181 on level 1 and 166 to 172 on level 2.
- FITTED guessers (`tools/guessers_lab_6.py`), held out: on the twenty surface features .286 /
  .274 on `unit_interp1` and .314 / .306 on `unit_interp2`; with the candidates known .322 /
  .314 and .318 / .292.

Corrections to this ledger, made here and not in place:
- The entry of fix wave 6 says a shot "does not ask what an eval item asks". What that build
  gated was narrower than what a prompt can give away: see the first bullet above.
- The same entry says no answer is 1. True; 1 was still offered as a wrong option on sixteen
  items.
- The plan of fix wave 6 (B-32) said the fitted guessers score "no more than a third". One of
  its own figures was .336, and on another seed both fits read .358: about a third, with a
  standard error of .02.

The audit record, all seventeen item files (an item file names the audit record, which names
`spec.py` and the generator files), the token record, the overlap record and every pin were
regenerated; the index and the known answers (77) are unchanged. The audit, the overlap count
and the guessers' fit ran on the coordinator's scratch copy of the task files (each file's
sha256 checked against the index); the token record was measured offline from the coordinator's
scratch cache (R-16). No network contact in this wave. 130 tests in the suite.

### Fix wave 8 (Tasks 2, 4–6) — the re-review of fix wave 7 (coordinator rulings R-60 … R-64)

The re-review (on 784fe256b) found the unit rungs to hold: every answer right by its own
parser, no option 1, a twin check clean on 12,000 seeds a level, no committed shot showing a
committed item's answer. Asked to look at the other fifteen rungs for a prompt that shows the
answer of an item it is scored on, it found one. The coordinator recomputed it, then counted
the same family of defect on every rung.
- A SHOT SHOWED AN EVAL ITEM'S ANSWER ON EVERY PROMPT OF `modarith_mul1` (the review's I-1, plan
  delta B-35). The second shot asked 94 * 85; eval item 199 asks 85 * 94. Over forty seeds of
  that build, 52 items in 30 batteries: the expected rate, not a fluke. The unit rungs' gate
  had two classes open at other seeds (the same numbers the other way round, 4 items in 4 of
  forty batteries; the inverse question of one relation, 5 in 5), and `deduction3` one (the
  same objects, order and position asked under other clues, 5 in 4). None was in the committed
  items but the first.
- THE SAME QUESTION WAS ASKED TWICE UNDER TWO SURFACES, AMONG THE EVAL ITEMS THEMSELVES (the
  coordinator's census; B-36). 137 of `modarith_mul1`'s 500 items asked a pair another item
  asks, either way round; 137 of `unit_interp2`'s asked what another asks under another
  subject; 6 of `unit_interp1`'s; 2 of `modarith_sub1`'s. The driver's duplicate gate read the
  question's text, which changes with the surface.
- THE DRIVER READS THREE OPTIONAL KEYS OF A DRAW and keeps none: `question_key` (what the item
  asks, its surface aside: no two items of a rung carry one, shots included), `content_key`
  (what would give the item away), `shows` (what else it shows beside a result). A duplicate
  question is redrawn; a SHOT is redrawn if its content key, or a key of what it shows, is an
  eval item's content key; an eval item is never redrawn for what a shot shows. `modarith`: the
  pair, either way round where the operation commutes, a shot's worked lines among what it
  shows, and an item whose own worked line shows the pair it asks refused at the draw. Units:
  the question is the numbers, the scaling and the roles; the content is the numbers a sentence
  prints and its answer as one sorted list. Deduction: the content is the context, the true
  order and the position asked; no question key, the names being content there.
- Redraws on the committed rungs: duplicates 106 (`modarith_mul1`), 125 (`unit_interp2`), 6
  (`unit_interp1`), 1 (`modarith_sub1`); shots 2 (`unit_interp2`). Over forty other seeds the
  shot gate redraws 63 on `modarith_mul1`, 25 on `unit_interp2`, 4 on `deduction3`, 1 on
  `unit_interp1`, none elsewhere.
- What moved: `modarith_mul1`, `modarith_sub1`, `unit_interp1` and `unit_interp2` are new
  items from the first redraw on; the other thirteen rungs' items and shots are the ones of fix
  wave 7. `modarith_mul1`: strata by the product's digits 15 / 19 / 136 / 330, the majority
  answer 1 on 15 items. The unit rungs: best of the heuristic list 179 of 500 and 250 (166 by
  the best rule that reads no unit word); the rank guesser 121 and 130; answers at ranks 1 to 5
  by size, 52 / 94 / 123 / 105 / 126 and 130 / 83 / 75 / 98 / 114; of 2,000 wrong options a
  level, 1,182 and 1,416 wrong readings, 578 and 326 other combinations, 240 and 258 pool
  numbers. Over forty other seeds the best rule that reads no unit word scores 148 to 189 on
  level 1 (the committed 179 is a high draw inside the range) and 166 to 169 on level 2.
- FITTED guessers (`tools/guessers_lab_6.py`), held out: on the twenty surface features .274 /
  .276 on `unit_interp1` and .322 / .280 on `unit_interp2`; with the candidates known .348 /
  .342 and .298 / .272.
- Not duplicates, counted: unit items that share the numbers of one relation in other roles or
  under another scaling, 10 and 146; `deduction3` items with the same objects, order and
  position asked under other clues, 22.

Corrections to this ledger, made here and not in place:
- The entry of fix wave 7 says a shot "prints no item's numbers with its answer, whatever the
  subject, the scaling or the roles". At other seeds two classes passed that gate: see the
  first bullet. The key was an ordered list of the printed numbers; it is now one sorted list of
  the numbers and the answer.
- The same entry says an innocent stream exceeds the chi-square's bound "about three times in
  100,000". It is 3.8 in 100,000 a cell, and about 6 in 10,000 over the sixteen.
- The same entry attributes the 1s among the options to an operator's precedence. That holds
  for level 1's ten. Level 2's six were never excluded.
- The same entry says the gate redraws a shot whose key "the shot before it" carries. The
  clause could not fire where a shot's answer may not repeat; it is removed.

The audit record, all seventeen item files (an item file names the audit record, which names
`spec.py` and the generator files), the token record, the overlap record and every pin were
regenerated; the index and the known answers (77) are unchanged. The audit, the overlap count
and the guessers' fit ran on the coordinator's scratch copy of the task files (each file's
sha256 checked against the index); the token record was measured offline from the coordinator's
scratch cache (R-16). No network contact in this wave. 136 tests in the suite.

### Fix wave 9 (Tasks 2, 4–6) — the re-review of fix wave 8 (coordinator rulings R-65 … R-70)

The re-review (on f51ad3764) found that what fix wave 8 set out to do holds: the `modarith`
gate, the unit rungs' question gate, every answer of the four rungs that moved (2,008 of 2,008
by its own parsers), and the unit rungs' central claim under the new gate (a fitted attack on
the roles at chance; the numbers distributed alike across the cells). Asked to look for the two
defects on all seventeen rungs by definitions of its own, it found them on rungs fix wave 8 had
left without a key. Each finding was recomputed by the coordinator before it was ruled.
- TWO RUNGS HELD ONE QUESTION TWICE (the review's I-1, plan delta B-36). `deduction3`'s items at
  slots 98 and 338 were one puzzle: the same context, objects and position asked, and the same
  clues once "newer than" is read as "older than" the other way round. `temporal`'s items at
  slots 1 and 160 were one schedule under other names. Over forty seeds of that build: 257
  `deduction3` items in 39 batteries, 30 `temporal` items in 12. Both rungs now carry a
  question key: a puzzle's context, objects, clues as a set whichever way a clue is worded, and
  position asked; a schedule's hours and free interval.
- A SHOT COULD STILL GIVE AN ITEM AWAY ON THREE RUNGS, AND SHOW A WRONG ANSWER TO ONE ON THE UNIT
  RUNGS (I-1, M-1, M-2, M-7; B-35). At other seeds a `temporal` shot carried an eval item's
  schedule (2 of forty batteries) and an `ipa_word` shot's transcription was an eval item's
  answer (1 of forty). On the committed items a `unit_interp2` shot printed the numbers of the
  item at slot 270 in other roles, and so showed, beside those numbers, one of that item's two
  wrong candidates (over forty seeds 36 items in 28 batteries; on level 1, 6 in 5). `temporal`
  carries a content key; `ipa_word` repeats no answer (chi and kai, dam and damn were both in
  the build); the unit rungs' shots are guarded by the printed numbers with the scaling, in any
  roles, and on level 1 by the rate in lowest terms.
- A SHOT REFUSED FOR ASKING AN EVAL ITEM'S QUESTION IS COUNTED AS SUCH (M-3). The driver checks
  the shot gate before the duplicate gate. Refused candidates on the committed rungs: 10 for
  `unit_interp2`'s shots, 1 for `modarith_mul1`'s. Over forty other seeds: 301 on
  `modarith_mul1`, 263 on `unit_interp2`, 12 on `unit_interp1`, 2 on `deduction3`, 2 on
  `temporal`, none elsewhere.
- THE `modarith` KEYS ARE TESTED WHERE THEY FIRE (M-4): on six other seeds of `modarith_mul1` no
  shot shows an eval item's pair and the gate has fired; a stream built to ask a worked pair the
  other way round is refused on the two rungs whose operation commutes.
- What moved: `deduction3` from slot 338 on, `temporal` from slot 160 on, `ipa_word` from slot
  213 on, and `unit_interp2`'s second shot. The other thirteen rungs' items and shots are the
  ones of fix wave 8. Redraws for a repeated question on the committed rungs: 106
  (`modarith_mul1`), 120 (`unit_interp2`), 6 (`unit_interp1`), 3 (`deduction3`), 1
  (`modarith_sub1`), 1 (`temporal`); for a repeated answer, 2 (`ipa_word`). `ipa_word`: 314 of
  its answers carry a stress mark; 137 of its words occur in BIG-bench's sentences and 146 of
  its answers are tokens of BIG-bench's IPA text; its longest answer is 17 tokens.
  `deduction3`: 108 items ask a position a clue states outright. `temporal`: the longest prompt
  is 618 tokens.
- Not duplicates, counted on the committed items: unit items that share the numbers a sentence
  prints and its answer with another (10 and 146); level-1 items that ask an equivalent question
  under other printed numbers (12); `deduction3` items with the same objects, order and
  position asked under other clues (12).

Corrections to this ledger, made here and not in place:
- The entry of fix wave 8 is headed by "no two items of a rung ask one question under two
  surfaces". It was true of the four rungs that entry keyed and false of `deduction3` and
  `temporal`, one pair each.
- The same entry counts 22 `deduction3` items as sharing objects, order and position asked
  "under other clues". Two of the 22 were under the same clues.
- The same entry's "10 and 146" are items that share the numbers a sentence prints AND its
  answer; by the printed numbers alone the counts are 52 and 424.
- The same entry gives the shot gate's redraws as 2 on the committed `unit_interp2` and 63 / 25 /
  4 / 1 over forty seeds. Those left out the candidates refused for asking an eval item's
  question, which were counted as duplicates: 7 on the committed rung.
- The same entry gives `modarith_mul1`'s fifteen pairs with a zero without saying that fifteen
  is the most in forty seeds (4 to 15, mean 9.65).

The audit record, all seventeen item files (an item file names the audit record, which names
`spec.py` and the generator files), the token record, the overlap record and every pin were
regenerated; the index and the known answers (77) are unchanged. The audit, the overlap count
and the guessers' fit ran on the coordinator's scratch copy of the task files (each file's
sha256 checked against the index); the token record was measured offline from the coordinator's
scratch cache (R-16). No network contact in this wave. 137 tests in the suite.

### Fix wave 10 (Task 5, a test and the record) — the re-review of fix wave 9 (coordinator rulings R-71 … R-74)

The re-review (on 3c82bf0ad) found no Critical and no Important defect. By definitions wider than
the battery's own keys, read from the question text: no two eval items of any of the seventeen
rungs ask one question; no committed shot shows an eval item's answer, or a wrong answer beside
an eval item's numbers; every answer of the rungs that moved is right (502 of 502 on each, and
20,080 of 20,080 at forty other seeds); all seventeen files regenerate byte for byte. Its
judgment: the battery is fit to build the instrument on and to freeze; what remains is at other
seeds, which the frozen battery never uses, or in counters and wording. No module and no item
file changes in this wave. Each finding was recomputed by the coordinator.
- WHAT THE SHOT GATE LEAVES OPEN, none of it on the committed items (plan delta B-35). Over forty
  other seeds: on `unit_interp2` a shot that prints an eval item's numbers under ANOTHER scaling
  and shows one of that item's wrong candidates, 21 items in 11 batteries (the guard names the
  scaling, and the product is a candidate under every scaling); on `deduction3` a shot that
  prints an eval item's paragraph and asks another position, 1 item in 1 battery. Disclosed, not
  gated: a gate would move the committed `unit_interp2` shots for a class the committed items do
  not hold.
- THE COUNTER `shot_content` counts the refusals on the rungs that carry a key. Elsewhere a shot's
  candidate that repeats an eval item's text or answer is refused as a duplicate or a repeated
  answer.
- NOT DUPLICATES, counted on the committed items (B-36): `deduction3` items that are one
  paragraph asked at two positions, 12 in six pairs; `temporal` items with the hours of another
  and another interval free, 10.
- A TEST: a puzzle's key tells a clue that states one position from a clue that states another
  (a mutant of the key that dropped the position was killed by the sha pins alone).

Corrections to this ledger, made here and not in place:
- The entry of fix wave 9 says the unit shots "are guarded by the printed numbers with the
  scaling, in any roles". True as written, and narrower than the plan's headline then said: see
  the first bullet above.
- The same entry corrects an earlier count to "by the printed numbers alone 52 and 424". Those
  are two definitions. In any roles: 91 and 424. In the same printed places: 52 and 424. With
  the scaling: 18 and 253.
- The same entry's "none elsewhere" of the shot gate's refusals holds of the counter, not of the
  refusals: see the second bullet above.

No file but one test and this ledger changed; no pin moved. 137 tests in the suite.

### Model contact, 2026-09-28 — a weight load by a test run; no item read (coordinator ruling R-75)

Found by the coordinator on 2026-09-28 while reading the runners to write tests, then confirmed
from the Mac's model cache, the mutation logs and the session's own record of what it ran.

- WHAT HAPPENED. The instrument is being prototyped in the coordinator's scratch directory; none
  of it is committed. Its mutation harness holds a mutant of the endpoint runner that removes the
  refusal of a host off the stack pin. The test that kills that mutant hands the runner a table
  of loaders that must not be reached. The table was an empty `dict` subclass, and an empty dict
  is falsy; the runner read `loaders = loaders or real_loaders()`. Under the mutant the runner
  therefore fell through to the REAL loaders and called 2m's frozen thin loader on the first
  family in sweep order.
- WHAT WAS LOADED. `HuggingFaceTB/SmolLM3-3B-checkpoints` at commit
  `d07a5a83dd011f3f084e9d2f1b47f51e524ca8d4`, the stage-1 endpoint (step 3,440,000):
  `config.json`, `model.safetensors.index.json`, `generation_config.json` and the two weight
  shards, 4,966,315,264 and 1,183,919,744 bytes, sha256 `76f0129a…` and `5004145c…` (equal to
  2m's committed manifest). `from_pretrained` completed, so the model was built in memory on the
  CPU. The loader's next statement, `model.to("cuda")`, raised `AssertionError: Torch not
  compiled with CUDA enabled` on this Mac. That exception is what failed the test.
- WHAT DID NOT HAPPEN. No tokenizer was loaded: the loader reads it after the move to the
  device, and the cache holds no tokenizer file of that repository. No prompt reached a model,
  no forward pass ran, no tensor digest was taken, nothing was scored. The test ran in a pytest
  temporary directory; nothing was written under any `results/`. Nobody in this program knows
  any output of any model on any item of this battery.
- WHEN, AND HOW OFTEN. Twice. 04:27:39 to 04:29:01 EDT, a run of nine named mutants: the fetch
  (the cache directory and both shards are dated 04:28, `generation_config.json` 04:29). And
  inside the full fast pass of 06:10:37 to 06:17:55 EDT, the same mutant and test, the weights
  read from the cache. The two full passes before 04:27 held the mutant and no test that
  reached it (it survived both); the cache directory did not exist before 04:28. No other
  mutant reaches a loader: the other tests that hand in the table fail at an earlier assertion
  under their mutants. The code as written refuses before its loaders in every test.
- THE DEFECT, in one line: a test double that was falsy, and a fallback written with `or`.
- CLOSED, in the prototype, to land with the instrument: (1) every runner takes what it is
  handed and falls back only on `None` (the endpoint stage, the sweep, the predictor stage's
  loader and sampler, the three of the preflight), each with a test that fails if a stage falls
  through to a real loader and a mutant that restores the `or`; (2) the tests' `conftest.py`
  puts the process offline and points its model cache at an empty directory before anything
  imports `huggingface_hub`, and the mutation harness sets the same in the environment of every
  run, so a test that falls through fails at once with nothing fetched and nothing read.
- LEFT AS FOUND: the cache entry (5.7 GB under
  `~/.cache/huggingface/hub/models--HuggingFaceTB--SmolLM3-3B-checkpoints`). Whether to delete
  it is Michael's call.

Corrections to this ledger, made here and not in place:
- The entries of fix waves 3 and 4 say the section "Model contact: None" stands. It stood when
  they were written. It does not stand as of 04:28 on 2026-09-28; the section now says so.
- The battery plan's standing constraint "zero model contact and zero weight download" was
  broken by the instrument's prototype, not by any step of the battery plan. The design doc's
  status sentence ("no model contact of any kind has occurred") was true when ruled.

### Instrument task 1 — the tests' conftest (every test process offline, its model cache an empty directory: N-12); families_6 (four families dispatched to the loaders, grids and renders their own experiments froze; 87 grid points), records_6 (the layout, the writers, every record's checks), referents_6 (gate 1-P's coverage, gate 1(b) as a pure function, the cross-host tolerance 15), the referent manifest (219 files, sha 09286d10…); 106 tests.

### Instrument task 2 — the pins (sixteen instrument files and seventeen item files bound by the tag), the runners with their gates at entry and exit, the two seals (every gate re-derived from the bytes; the rung sets by rule, R_heuristic beside R_f), the power record (eight tests; the tree as Poisson-binomial figures and Fréchet bounds), the analyzer (INSUFFICIENT_DATA collected, never raised; eight tests through 2i's _run_test; statuses by three of four; sixteen pairs to six worlds; S1–S13); 85 fast tests, 63 worlds, 161 totality.

### Instrument task 3 — the preflight (scratch only; nothing stored, no score printed; forty items of three rungs; the rehearsal of gate 1-P and of gate 1(a)), the cold battery (fourteen items, PASS / FAIL / SKIP, no statistic), the import scan (two interpreters; the analyzer's loads no torch), the read sweep, eight box scripts; 30 tests.

### Instrument task 4 — closure: the import surface and the referent manifest re-derive to their pins; the mutation harness (private tree copies, nothing mutated in place) with the fast pass's log committed (the slow pass is the coordinator's); the read sweep on a synthetic complete tree, 0 unpinned; the cold battery.

### Instrument fix wave 1 (Tasks 1–4) — the task reviews' findings (coordinator rulings I-12 … I-16)

Four task reviews. Tasks 1, 3 and 4: approved, minors only. Task 2 (the code that decides
verdicts): one Critical and two Important, all three in code the plan itself carried. Each was
read in the code or recomputed by the coordinator before it was ruled on.
- THE LICENCE OF BATTERY-BOUND CLAIMED AN ABSENCE (C-1; plan delta N-15). Its sentence read
  "Neither predictor forecasts the order on the field's tasks." Design §6 wrote no such
  sentence, and status F admits one firing family, so the sentence could stand beside two
  tests that fired. It now states the naming rule's count ("each fired on at most one of its
  evaluable families") and leaves the reading to the power record. "Withdrawn" is printed only
  where every evaluable test was declared POWERED for the rung set it READ: a test that read
  another set than the record simulated is not covered by its declaration, and the reading is
  then "not detected at this resolution". A predictor that holds on three of four families says
  on which, as a disclosure; the design's sentences say "on four outcome families" and are
  Michael's to reword.
- THE WEIGHTS THAT SET R_f WERE IDENTIFIED BY NOTHING MEASURED (I-1; plan delta N-14). A load
  record's commit and revision were copied from the manifest and compared with the manifest;
  the endpoint stage reads through the thin loader, which no file sha verifies; gate 1 compared
  digests on the sweep host only. GATE 1(d): every load of a trained checkpoint has the digest
  the loader measured compared with the digest the Mac measured for the same checkpoint in the
  family's own experiment (`weight_sha256` of the anchors' committed records: one digest a
  checkpoint, 88 trained checkpoints, no two alike). The runners compare before a runner is built or a
  prompt is rendered, and halt; the endpoint seal and the analyzer re-derive; gate 1 also holds
  the sealed endpoint read's digest to the sweep host's. Seeded twins are outside the gate. The
  preflight rehearses it.
- THE ENDPOINT RUNNER COULD REWRITE A SEALED FILE (I-2; plan delta N-16). It did not refuse
  after the endpoint seal, and it rewrote the gate record on every run. It refuses once the
  rung sets exist, and writes the gate record only when it read a unit.
- RECORDS ARE WRITTEN WHOLE (N-16). `write_json` writes beside the path and renames. A record
  that exists and does not parse is a torn record: refused, and no unit is resumed over it (the
  completeness checks asked only whether the files existed).
- FIELDS NOTHING COMPARED, now compared: the gate 1(b) record's host, the predictor seal's tag,
  gate 1-P's tag, a power test's own test, family and predictor. The power writer refuses over
  a halt marker.
- UNDETERMINED NAMES EACH CAUSE: R_f short on a family (one family is enough to be named), a
  rung lost to thin outcomes over the sweep (outcome side), a rung degenerate for the predictor
  (predictor side). A loss the result does not explain is said.
- THE FAMILY DISPATCH had no mutant and a test that checked its calls could bind, not what they
  were handed. Ten mutants; the test now holds each loader's repository, commit or entry, dtype
  and device. `families_6.steps` was called by nothing and is removed. `release` says what it
  swallowed.
- THE HARNESS: a hint that matches no test is an ERROR (it was passed over in silence). The
  finiteness probe of the preflight falls back on `None` only (N-12's shape).
- THE PLAN'S OWN DEFECT (ruling I-16): Task 4's count of survivors matched the log's summary
  line as well as its 52 mutant lines. The implementer stopped on it. Both commands that select
  survivors now match mutant lines only.

Corrections to this ledger, made here and not in place:
- The entry of instrument task 2 says "every gate re-derived from the bytes". True of the gates
  there were. The identity of the endpoint stage's weights was not among them until this wave.
- The entry of instrument task 4 gives the fast pass as 282 mutants, 230 killed, 52 survived.
  That was the table of that commit. This wave's table and tally are in its own log.
Measured in the repository: fast suite 368 passed; worlds 70, totality 161; fast mutation pass 325 mutants in 599 s: killed 265, survived-fast 60; read sweep 2,604 reads, 0 unpinned; cold battery 10/14 PASS, 4 SKIP.

### Instrument fix wave 2 — the re-review of fix wave 1 (coordinator ruling I-17)

The re-review (on 26f3996d7) found every finding of the four task reviews addressed, with a
file and a line for each, and gate 1(d) sound end to end: the digest each frozen loader hashes
is the one the Mac's committed records carry, on every family, both loader paths and every
key; the comparison precedes the runner and the finiteness probe; a fire halts and is not
resumed over. It found one Important defect and six Minor in the fix itself. Each was read in
the code by the coordinator.
- A FAMILY THAT WAS NOT EVALUABLE WAS SAID NOT TO HAVE FIRED (I-A). The disclosure of a
  predictor that holds on fewer than four families listed every family outside the ones it
  fired on as one it "did not fire on". A family whose test read fewer than three rungs was
  not read, whether or not its test fired. The disclosure now names apart the families that
  were evaluable and did not fire and the families that were not evaluable.
- A TEMP FILE A KILL LEFT (M-1, M-2). A kill inside the predictor seal's own write left a temp
  file that the next seal's table named and the next write consumed; the seal then never
  re-derived. The seal's table is of records, not of temp files, and a temp file carries its
  writer's process id.
- THE HOST CHECK OF GATE 1(b) HAD A DEFAULT THAT SKIPPED IT (M-3), and the cold battery took
  the default. The argument is required.
- A FIRE OF GATE 1(d) KEPT TWELVE CHARACTERS OF THE DIGEST (M-4) at the endpoint stage and at a
  sweep host's gate. The halt marker carries the whole of what the loader measured.
- WHAT THE PREFLIGHT REHEARSES (M-5): the endpoint and the first grid step of each family. The
  plan's delta N-14 says so; OLMo-2 13B's step 0 meets the gate at the endpoint stage.
- `release`'s print is tested (M-6). Mutants for the checks that had none: the two branches of
  the disclosure, a reading wider than the set the power record simulated, a loss the result
  does not explain, a missing record, the temp file's name, the seal's table, both markers.
Measured in the repository: fast suite 370 passed; worlds 70, totality 161; fast mutation pass 335 mutants in 613 s: killed 276, survived-fast 59; read sweep 2,604 reads, 0 unpinned; cold battery 10/14 PASS, 4 SKIP.

### Instrument — the slow mutation pass, on the repository (coordinator, 2026-09-28; ruling I-5)

Run by the coordinator, detached, at adb3a70ca with no implementer live, over the survivors of
the committed fast pass: `59 mutants in 2093 s: killed 59`, no OPEN, no ERROR, none declared
equivalent (`EQUIVALENT_6` is empty). With the fast pass (335 mutants, 276 killed, 59
survived-fast) every mutant of the table is killed by a named test: 276 by the fast files, 59
by the worlds and the totality files. Both logs are committed (`mutation_fast.log`,
`mutation_slow.log`); the tally is reproducible from them. The harness works on private copies;
the tree was clean before and after. Model cache untouched.

### Instrument — the adversarial freeze and the slow mutation pass after it (coordinator, 2026-09-28)

The freeze's record is `FREEZE_CHECKLIST.md` (commits be0f914dc, cf5fbf074). The class defect
was found and closed: F-2, a frozen module supplied by a second `experiments` directory
earlier on `sys.path` ran with every pin active and moved a null world from BATTERY-BOUND to
GENERAL. Also closed: F-1 (six files the verdict path loads lazily were named by no pin: every
real runner would have halted at its exit gate, and no test had run with the real pins on),
F-3 (an endpoint load resumed across hosts), F-4 (bytecode that is not the hashed source).
Eight items are stated for Michael's ruling in its §D. The coordinator checked the freeze's
commits before building on them: no module that decides a verdict changed (`analyze_6`,
`power_6`, `records_6`, `referents_6`, `families_6` and the battery are byte-identical to
adb3a70ca); fast suite 381 passed, 234 deselected; import scan 73 frozen, 5 own, 16 bound by
the tag, as pinned; cold battery 10/14 PASS, 4 SKIP; model cache untouched.

The slow mutation pass, run by the coordinator on the repository at cf5fbf074 over the 59
survivors of the freeze's fast pass: `59 mutants in 2249 s: killed 59`. With the fast pass
(349 mutants, 290 killed, 59 survived-fast): 349 mutants, every one killed by a named test,
none equivalent. Both logs committed.

### Instrument fix wave 3 — the final whole-branch review (coordinator rulings I-19 … I-23)

The final whole-branch review found one Critical, four Important and seven Minor defects. The
coordinator ruled on each (I-19 … I-22, and I-24 amending I-19's text). What the review found,
one line a finding:
- C-1. The known-inputs caveat, joined into every licence, said the predictors were sealed
  before any outcome weight loaded. A test loaded SmolLM3-3B's endpoint weights on 2026-09-28,
  and the run plan's outcome preflight loads each family's endpoint and first grid step.
- I-1. A runner wrote its host record before checking it: a host off the stack pin left a
  record that refused every later seal and the verdict over a correct campaign.
- I-2. The predictor seal's file table took dotfiles (a Finder `.DS_Store`), which the watcher
  never commits; the box would refuse a correct seal.
- I-3. F-4's closure held a hash-based `.pyc` to its header only. An unchecked `.pyc` whose
  header carries the true source's hash and other code passed.
- I-4 (freeze §D 1). The headline condition counted a family on which the test was not
  evaluable.
- M-1. The UNDETERMINED shortfall named every dropped rung on the predictor side, including
  rungs `_run_test` drops on a retry because the OUTCOME is constant inside every stratum.
- M-2. The projection check sat only in `rebundle_box_6.sh`, which a fresh sweep box need not run.
- M-3. The box's disk was unsized.
- M-4. The preflight never rehearsed gate 1(c): the anchors against the Mac's counts.
- M-5. The status script read a pid file nothing wrote, and called its log gitignored; it is not.
- M-6. The cold battery's read-sweep item runs the analysis, on a swept tree too.
- M-7. `power_6.main`'s last two lines read fixed keys of the tree.
- §D 5. The permutation and bootstrap counts are arguments of `run()` and nothing recorded
  whether they were the frozen ones.

Closed, each test-first (the failing output and the passing output are in the implementer's
report), each new check with a mutant:
- C-1: `KNOWN_INPUTS_CAVEAT_6`'s seal-order sentence replaced. Its text now reads: "The
  predictors were sealed before any outcome model was handed an item of this battery; the
  endpoints, rung sets and power record before any intermediate checkpoint was scored into a
  record; the projection before the sweeps. Outcome weights were loaded before the predictor
  seal once, by a test on 2026-09-28 (no tokenizer, no forward pass, no item read; the ledger
  has the account). The outcome preflight runs after the predictor seal and loads each
  family's endpoint and first grid step. It stores nothing. Of what a model writes on an item
  of this battery it reports shape, timing and identity, and no score; it holds 2c's two
  anchors to their committed counts." (The last three sentences are ruling I-24's: item 7 made
  "stores and scores nothing" untrue.) A test pins the text and that no licence says "before
  any outcome weight loaded" or "scores nothing". `run/preflight_6.run_outcome` refuses, before
  it loads anything or builds a host record, unless the predictor is sealed
  (`endpoint_6.require_predictor_seal`, with the runners' two injections; `main()` passes none).
- I-1: `ensure_host` checks `host_failures` first and writes nothing for a host off the pin.
  `load_hosts` is unchanged.
- I-2: `file_table` skips any file whose name begins with a dot.
- I-3: a hash-based `.pyc` whose header is the source's hash is also unmarshalled and compared
  with the code the source compiles to; an unreadable one is a failure. (The first fast pass
  then showed F-4's header mutant surviving, the code check covering every case the tests
  built; one assertion — a wrong header over the source's own code — restores its kill.)
- I-4: `headline_condition` counts a family only where that predictor's test was evaluable.
- M-1: each primary test carries `dropped_predictor` (`_degenerate_rungs` on the predictor's
  counts, before any retry); the shortfall names the rest of `dropped_degenerate` on the outcome
  side ("lost … to an outcome that is constant inside every stratum").
- M-2: `campaign_sweep_6.sh` refuses at its start without `experiments/exp6/projection.md` in its
  checkout. M-3: `box_setup_6.sh` states about 170 GB, prints `/workspace`'s free space, and
  refuses below 170 GB unless `EXP6_DISK_OK=1`. M-5: both campaign scripts write their pid to
  `/workspace/campaign_6.pid`; the status script's header says its log is not gitignored.
- M-4: every read of the outcome preflight scores both anchors on all 500 items and holds each
  count to the Mac's committed count of that checkpoint within 15; the family passes only if
  every anchor of every read is within. Printed: the anchors' counts and the Mac's.
- M-6: the read-sweep item SKIPs, and says why, once any file exists under `results/sweep/`.
- M-7: the power writer prints every bound the tree record holds, under its own keys.
- §D 5: `pins_active` gains `frozen_counts`.

Stated for Michael's ruling: two closures are licence text or a licence rule. (1) The caveat
sentence above (C-1, rulings I-19 and I-24). (2) The headline condition now counts evaluable
families only (I-4, §D 1, ruling I-20); the licence sentence `HEADLINE_UNQUALIFIED_6` still says
"on at least three families", and the freeze's §F slip ("on at least three of that predictor's
evaluable families") is not applied. Design §2's "Sealed in order" paragraph needs the matching
slip; the design doc is not edited here.

Measured in the repository: fast suite 395 passed, 234 deselected; slow files (worlds,
totality, `test_freeze_6.py -m slow`) 232 passed, 15 deselected, before and after ruling I-24;
import scan 73 frozen, 5 own, 16 bound by the tag, as pinned (no table re-derived); cold battery
10/14 PASS, 0 FAIL, 4 SKIP (its read-sweep item ran `analyze_6.run` once on the real tree, which
refused at the predictor seal — one pre-tag execution); fast mutation pass 369 mutants in 964 s: killed 309, survived-fast 60, no ERROR (the 59 survivors of the committed log, and M-1's `dropped_predictor` mutant, which only the worlds see: HINTS_6 names `test_general`); model
cache untouched. `mutation_slow.log` is stale against the new table and is the coordinator's
to replace.

### Fix wave 3 verified, re-reviewed, and the slow mutation pass after it (coordinator, 2026-09-29)

Verified by the coordinator on the commit (38e6a71e4): 22 files, all under `experiments/exp6`,
no battery file, nothing under `experiments/exp1` … `exp5b`; the only licence text that moved
is the known-inputs paragraph, the only licence rule the headline condition; no preregistered
constant moved. Fast suite 395 passed, 234 deselected. Import scan 73 frozen, 5 own, 16 bound by
the tag: as pinned. Cold battery 10/14 PASS, 0 FAIL, 4 SKIP (its read-sweep item executed the
analyzer once on the real tree, a refusal at the predictor seal: one more pre-tag execution,
the coordinator's). Model cache: no new file.

Slow mutation pass on the repository: the 60 survivors of the fast pass, 60 killed (2,322 s).
The table stands at 369 mutants: 309 killed fast, 60 killed slow, none open, none equivalent.

Scoped re-review of the wave (opus, read-only): every finding of the final review ADDRESSED;
nothing preregistered moved beyond the two ruled changes; no Critical. It read the
known-inputs paragraph clause by clause against the code and found each clause true, with one
note. What it found, and the coordinator's rulings (I-25 … I-32). There is no second fix wave:
each item is carried to Michael and applied in one pass on his word, and the batteries are run
once on the final tree before the tag.

- O-1 (Important; the coordinator's own figure was wrong). The box needs about 230 GB, not
  170: the endpoint stage never frees OLMo-2 13B's step 0 (about 55 GB in the checkpoint
  cache), so one box that runs the endpoint stage and all four sweeps holds about 104 GB of
  endpoints, 55 GB of step 0 and 55 GB of one 13B checkpoint, and the software beside them. A
  candidate copy and a checkpoint are never resident together (the sweep frees each in a
  `finally`). The check measures `/workspace`; both caches live under the home directory.
  Closure, script only and not bound by the tag: `box_setup_6.sh` states and checks 230 GB on
  both filesystems; a box is created with 250 GB. Before any box is rented.
- O-2. "It stores nothing" is proved for `results/` only; the preflight leaves weights in the
  hub cache. Proposed wording: "It writes no record." Licence text: Michael's.
- O-3. The clause "the outcome preflight runs after the predictor seal" is enforced by
  `run/preflight_6.py`, which the tag does not bind (plan delta N-8). The exemption stays; each
  outcome preflight is ledgered with the time, the commit and the predictor seal's sha256.
- O-4. `HEADLINE_UNQUALIFIED_6` says "on at least three families": still true, less exact than
  the rule. It changes only with Michael's ruling on the rule.
- O-5. Two docstrings say the preflight scores nothing (`pins_6.check_imports_6`, the module
  docstring of `tests/test_preflight_6.py`). Corrected with the slips.
- Left: a dot-directory under `results/predictor` would enter the seal's table. Nothing writes
  one.
- Design text that now differs from the instrument (§2 "Sealed in order", §7's preflight row,
  §11's order): slips for ratification. The design doc is not edited.

State: built, frozen, reviewed. No tag. No model has read an item of this battery.

### Management takeover — 2026-09-29 (OpenCode, GPT-6 Astra)

Michael: “Review the ongoing experiment(s) in this folder and begin managing
them please.” Read the project map, handoff, live and preceding ledgers,
designs, both Exp 6 plans, freeze, final-review record and ratification
packages. Exp 6 is the only active experiment; Exp 5b is closed and
propagated. The handoff's “no named successor” and the map's “build next”
were historical snapshots, not the live state.

**Verified at instrument head `2e54bd4cf`:**

- Clean `master` at entry; remote master independently read at the same
  commit. No `exp6-*` tag and no `experiments/exp6/results/` directory.
- Fast suite, offline and with the empty-cache test guard:
  `python -m pytest experiments/exp6/tests -m 'not slow' -q -p no:cacheprovider`
  under the lab venv → **395 passed, 234 deselected, 40.18 s**.
- Cold battery, once, offline: **10/14 PASS, 0 FAIL, 4 SKIP** (prereg tag,
  predictor stage, endpoint stage, sweeps absent). Twenty item files,
  219 referents, all eight committed tallies exact; import scan 73 frozen
  and 5 own modules as pinned; **314 reads, 0 unpinned**.
- Parsed the two committed mutation logs by per-mutant lines: 369 unique
  fast entries, 309 killed and 60 survived-fast; 60 unique slow entries,
  all killed. Fast survivor names equal slow kill names exactly; no open
  name, duplicate or unexpected slow entry. This checks the stored logs;
  the final mutation rerun follows the ratified changes.
- Python 3.11.15 and every package version in HANDOFF §4 match. A first
  metadata query used the system Python (3.14, no torch) and was corrected
  to the lab venv; every experiment test/check used the lab venv.
- No local experiment, pytest, mutation, puller, watcher or status process
  found. Vast's authenticated GET `/api/v1/instances/` returned zero
  instances. No rental operation was made. Mac free disk about 505 GiB.

**Recovered audit gap:** the cold battery executes the analyzer's read
sweep, even though it prints no statistic. Reconstructed the nine prior
real-tree calls from the preceding session's tool commands and results;
this session adds one, making **ten**. All are before campaign data,
refusing at the absent predictor seal. `PRETAG_AUDIT.md` carries the UTC
event list and its scope. Prototype/rehearsal copies and synthetic worlds
aren't counted as the real tree. No analyzer was executed to reconstruct
the tally. The prior ratification draft's claim that a total was already
ledgered was premature.

**Ruling M-1: consolidate the pending approval package in tracked
`RATIFICATION.md` and refresh the management pointers.** The previous
package was only in the git-ignored SDD workspace. Reason: the next agent
must be able to find the active gate from the repository. Cost if wrong:
an editorial correction before ratification. The new package preserves
D-1–D-16 and O-1–O-5, references the committed B/N deltas, recommends
keeping the cache entry, and explicitly says the contact involved two
loads. It is a proposal, not Michael's ratification. The original SDD
workspaces and their full ruling lists remain in place.

The carried instrument changes still await his word under I-32. Next:
ratification → one correction pass → final batteries → verified annotated
preregistration tag → predictor preflight on his word. No campaign or
monitor is running; no item has been read by a model in this takeover.

### Ratification applied — 2026-09-29 (OpenCode, GPT-6 Astra)

Michael: **“ratified”**, in response to the tracked package's recommendations.
All D-1–D-16, O-1–O-5 and B-1–B-36/N-1–N-16 are approved. The primary
retains its floors and strata; both unit rungs and the drawn deduction
shots stay; exact IPA stays primary; S11/S12/S13 carry the named comparisons.
The accidental cache entry stays. This supersedes the pending decisions
in the earlier ledger entries and packages.

Applied together before final validation:

- The design's status, disclosure, battery, budgets, gates, pins, power,
  secondaries, licences and stage order now describe the ratified instrument.
  GENERAL says at least three of four outcome families, named for each
  predictor. The caveat counts both weight loads and says preflight writes
  no record. The headline sentence specifies evaluable families. The two
  stale preflight docstrings are corrected.
- Disk setup checks 230 **decimal GB** on both home/cache and workspace
  filesystems; request 250 GB. `df -Pk` counts are converted from 1024-byte
  blocks, not mislabeled GiB. The existing disk-override mechanism remains.
- Bundles advertise only master and exp6 tags. Before creation, master must
  be checked out with no tracked modifications; required stage tags and
  the sweep projection must exist, and the real prereg/predictor/endpoint
  binding functions run. The bundle's advertised refs are compared to the
  requested set. Rebundle checks the bundle's own required refs, rejects
  unrelated refs, and checks bindings after checkout, so a stale receiver
  tag can't satisfy a missing bundle tag. No rental bundle was produced.
- Outcome preflight's required ledger entry (UTC, HEAD, predictor-seal
  sha256) is in the run plan. Its own file remains tag-exempt as ratified.
- `BUILD_RULINGS.md` is a byte-identical copy of the preceding coordinator's
  combined ruling list: R-0–R-75 and I-0–I-32, 109 unique IDs. SHA256
  `1d889a3f4166de1e73767f7b9ff69b1f33052d46906e7a0aaf5c0665e11b0345`.
  Historical proposals/corrections stay verbatim; the dated ledger and
  ratification decide the current state. Original workspaces are retained.

**Verification so far:** fast suite **396 passed, 234 deselected, 39.54 s**;
all 369 mutation targets still match exactly once. `bash -n` passes for
every Exp 6 shell script. Synthetic-git smoke checks passed for bundle
scope, missing required refs, dirty-tree refusal, sweep projection and
stale receiver tags (binding hook stubbed in these synthetic repos; actual
binding is checked against real git at the tag and before a rental bundle).
Disk smoke checks passed on either filesystem below 230 GB and at the
230-decimal-GB boundary. Nothing was installed or rented by those checks.

**Ruling M-2:** validate every slow-marked test, including regeneration and
real-git pin tests, then the full fast mutation pass and its exact survivors
with `--slow`; run detached through `Popen(start_new_session=True)`.
Reason: this is the final ratified tree; the earlier slow-file selection
omitted two marked tests. Cost if wrong: extra local runtime. Logs and
stage/exit-status timestamps are under the approved OpenCode scratch path,
`exp6-final-checks/`; the mutation logs will replace the committed logs only
after reconciliation. Cold battery and its pre-tag audit increment follow.
No new model contact; no campaign `results/` exists. Tag awaits these checks.

### Final ratification validation — 2026-09-29 EDT / 2026-09-30 UTC

The detached controller completed successfully at **2026-09-29 23:07:40
UTC** (PID/session 11178). Its completion had not yet been propagated to
the ledger/tag when Michael asked “Are they done?”; checked the completed
status and raw logs, then finished the cold battery and release steps.

Validated code is the ratified tree committed as `b7e00e30c`. After the
test launch only documentation changed before that commit; the instrument
and tests were stable throughout. No model contact or campaign record.

| check | result | measured runtime |
|---|---|---|
| fast suite, `-m 'not slow'` | 396 passed, 234 deselected | 39.54 s |
| full slow suite, `-m slow` | 234 passed, 396 deselected | 2,927.09 s |
| full fast mutation pass, six jobs | 369 mutants: 309 killed, 60 survived-fast | 1,270 s |
| exact survivors with `--slow`, six jobs | 60 killed, zero open/error/equivalent | 2,862 s |
| import scan, `--check` | 73 frozen, five own, sixteen tag-bound: as pinned | exit 0 |
| final cold battery | 10 PASS, zero FAIL, four expected SKIP | exit 0 |

The slow suite ran 21:09:56–21:58:43 UTC, fast mutations
21:58:43–22:19:54, slow mutations 22:19:54–23:07:36. The full marked slow
suite includes the two tests omitted by the preceding 232-test selection.
Parsed both new mutation logs by their per-mutant lines: every current
table slug occurs exactly once in the fast log; its 60 survivor names
equal the slow log's 60 kill names exactly. Both committed logs replaced
by these successful runs. Total **369/369 killed**, no equivalent.

Cold battery ran ONCE at **2026-09-30 02:04:17.363609 UTC** on clean
`b7e00e30c`, with the campaign tree confirmed absent beforehand. It
verified twenty item files, floor/stratum/structure/heuristic pins, the
collision audit and 77 known answers, content overlap, token budgets,
219 referents and eight committed tallies/readings. Import pins matched;
the read sweep saw **314 reads, zero unpinned**. Preregistration,
predictor, endpoint and sweep stages were the four expected skips.
`PRETAG_AUDIT.md` increments to **eleven** real-tree analyzer executions;
this one again refused before any Experiment 6 statistic. No verdict
file was written. The scored analysis remains owner-gated.

Final validation is complete. Commit/push these logs and the audit, then
create the annotated `exp6-preregistered`, verify its 33 blob bindings
against real git, and push the tag under the ratification authorization.

### Preregistration tagged and verified — 2026-09-29 EDT / 2026-09-30 UTC

Final evidence committed and pushed at
`6ac42458eda6f901f266421bb5fdc7c44f83a167`. Created annotated tag
**`exp6-preregistered`**, object
`77b8c175834061a2bb4c76aab9959bf5e9fd2895`, at that commit.
`pins_6.require_prereg_6()` against real git returned **33 bound blobs**:
sixteen instrument files and seventeen item files. `check_frozen_6()` and
`check_imports_6()` passed. Pushed the tag, then independently read
`origin` with `git ls-remote`: annotated object and peeled commit match
exactly. No analyzer call was needed to verify the tag.

The model cache has **zero files modified since the validation launch**;
the campaign `results/` directory remains absent. No rental was created.
All ratification work and checks are complete; next is **predictor
preflight on Michael's word**, followed by the ruled predictor stage.
Outcome preflight follows its seal. The explicit rental, scored-analysis
and close-out gates remain in force.

### Predictor preflight authorized — 2026-09-29 EDT / 2026-09-30 UTC

Michael: **“proceed”**, answering “Proceed with predictor preflight?”
The Mac preflight is the next authorized model contact. The production
`run/preflight_6.run_predictor(device='mps')` will run once with its real
loaders/sampler and no injected checks, sequentially on OLMo-2 1B,
Pythia-1b and Pythia-410m. It rehearses item 0 of `add_base8` against each
committed main-tier stream, then samples item 0 twice on `temporal`,
`ipa_word` and `modarith_mul1`. It measures finiteness and diagnostic shape,
timing/memory only; draws and new-battery scores are not retained or printed.

Preparation verified 33 preregistration bindings, pinned Python/packages,
MPS availability and an absent campaign tree. The current OS is
**macOS 26.6.2**, newer than `environment.md`'s historical 26.5.2 note;
the preflight's stream-reproduction and repeatability checks must pass on
this actual stack before any campaign. Pythia's two pinned snapshots are
cached. OLMo-2 1B's pinned snapshot (`9d3e43659f00c17e6da23cf32333afd1fc39fa1a`)
is absent and the real loader may fetch it from the Hub. This is planned
predictor contact under the authorization, not outcome contact. The Mac
uses `HF_HUB_DISABLE_XET=1`; the package pins are not changed.

Operator wrapper is outside the instrument, in the approved OpenCode
scratch directory as `exp6-predictor-preflight.py`; durable stdout, UTC,
HEAD, PID/session and score-free diagnostic summary go to
`exp6-predictor-preflight-20260930/` there. It launches with
`Popen(start_new_session=True)`. Under HANDOFF §4, the three loaded MLX
services are suspended while timing/sampling and restored in `finally`;
no other service is stopped. Completion, any refusal and actual contacts
will be appended here. No campaign record is written by this preflight.

### Predictor preflight passed — 2026-09-29 EDT / 2026-09-30 UTC

The single authorized preflight ran **02:15:59.483346–02:20:18.911627 UTC**,
259.43 seconds, at HEAD `2bacdbe91c1baa97ceb9017abbe2fa0693f7e45e`.
Detached PID/session **58954** exited 0. All three real trained predictors
loaded at their pinned revisions; all three `add_base8` item-0 rehearsals
equaled the committed streams (256 draws for each Pythia, 64 for OLMo).
All **nine** new-rung repeatability checks were byte-identical. On each
predictor, the eight longest-by-character-count `temporal` prompts had
**zero non-finite last-position logits**. This is the preflight's actual
probe scope, not every prompt or a full campaign gate.

| predictor | temporal s/item | IPA s/item | modified multiplication s/item | MPS driver allocation, GiB |
|---|---:|---:|---:|---:|
| OLMo-2 1B, k=64 | 8.30 | 5.86 | 2.09 | 32.01 |
| Pythia-1b, k=256 | 11.34 | 15.30 | 5.36 | 27.66 |
| Pythia-410m, k=256 | 7.98 | 10.34 | 3.45 | 19.93 |

Times are one item's first read, not whole-rung measurements. Multiplying
by 500 gives 0.29–2.12 hours per rung across these nine cases. The summary
field is named `peak_memory_bytes`, but on MPS the implementation samples
`driver_allocated_memory()` after the reads; **it is not a measured peak**.
All normalized outputs were non-empty; no new-battery score or raw draw
was retained. The full gate 1-P remains to be established on all items.

**Model/network contact:** the real loader downloaded OLMo-2 1B's pinned
snapshot (config, generation config, weight index, two weight shards and
three tokenizer files), now present in the Hub cache. The two Pythia
snapshots were already cached; their real loaders were online and may
have made Hub metadata checks. Every predictor read the preflight items;
the earlier “no model has read an item” status is now historical. No
outcome model was loaded. All 33 preregistration bindings and the frozen/
import checks passed afterward; `results/` remained absent. The wrapper
restored all three MLX services and their loaded status was independently
checked. Free space afterward: about 495.6 GiB.

Durable evidence under the approved scratch directory,
`exp6-predictor-preflight-20260930/`:

- `summary.json` SHA256 `bcf4caf9d7f1b52219aef1728267a31f9e057be5c86959ff2b6bad3990274123`
- `status.json` SHA256 `72f88e00ceb1aefbb6029416d296d48a59ec127299c161228d5be705578fe184`
- `preflight.log` SHA256 `39193269a3d5ccf54a7d110b58f866619daaef5c7035e29399be1d2add08e4c0`

### Predictor collection prepared — 2026-09-29 EDT / 2026-09-30 UTC

**Ruling M-3: proceed from the passed preflight to the ruled predictor
stage.** Reason: HANDOFF §2 says everything else in a ruled plan proceeds,
and design §11 places collection next. Michael's “proceed” opened the
preflight gate; no additional predictor-collection gate is named. Cost if
wrong: local compute time; no rental. Rentals, the scored analysis and
close-out retain their explicit owner gates.

Production dry-run plan: **93 units, 6,116,000 draws**. Pythia-1b first:
54 units / 3,060,000 draws (19 main, one control, 17 pilot, 17 twin);
Pythia-410m: 20 units / 2,448,000 draws; OLMo-2 1B: 19 units / 608,000
draws. Within each invocation the frozen runner completes its full anchor
and control gates before new rungs, then the pilot before the main tier,
then the twin. Models run sequentially, with the committed sampler and
unchanged tiers/budgets. Three separate production CLI subprocesses.

**Ruling M-4: use an operator-only complete-pair watcher for the Mac
collection.** Reason: `write_draws` writes its final filename directly and
can be visible before completion; the JSON record is written last. The
existing shell watcher admits a lone gzip after its settle window. This
supervisor admits a result only when both files exist, the JSON parses,
the pair is stable across three seconds, and `seal_predictor_6.load_unit`
re-derives coverage, provenance, digest and tallies successfully. It prints
unit counts only. Halt evidence is retained and committed too. Cost if
wrong: an operator wrapper to inspect; the frozen instrument is unchanged.
An isolated real-git smoke check exercised orphan/temp exclusion, torn
JSON refusal, pair commit/push, unrelated-index refusal and final flush.

Wrapper: `exp6-predictor-campaign.py` in the approved OpenCode scratch
directory. Logs/status: `exp6-predictor-campaign-20260930/` there. Detached
session, one model subprocess at a time, complete-pair watcher every minute,
atomic status with unit counts and UTC/HEAD/PIDs, `caffeinate` for the run.
The three MLX services are suspended again and restored on exit. The
supervisor stops at the first runner failure, flushes the watcher, and
leaves collection for verification and the predictor seal. **While it is
live, do not hand-commit over its watcher.** The launch checks a clean tree,
the real pins/host, passed preflight and exactly 93 pending units. Its
PID/session and exact launch time will be in `status.json`.
Launch wrapper SHA256:
`a3d69a9ac1f386b61f3e67c3c19f67d6b07fea2e40134520dfed1a1095315117`.

### Predictor collection complete; seal written — 2026-10-02 UTC

The detached supervisor (PID/session **61056**) ran at launch HEAD
`a35870f9eefe411a4a30944950a867fe3f37a5a7`, from **2026-09-30
02:30:38.875199 UTC** through **2026-10-02 03:22:15.591216 UTC**:
**48 h 51 m 36.72 s** including the final watcher flush. All three
production CLI invocations exited 0; their entry and exit pin checks passed.

| predictor | units | draws | wall time | finished UTC |
|---|---:|---:|---|---|
| Pythia-1b (including pilot and twin) | 54 | 3,060,000 | 27 h 51 m 14.46 s | Oct 1 06:21:53 |
| Pythia-410m | 20 | 2,448,000 | 13 h 44 m 40.93 s | Oct 1 20:06:34 |
| OLMo-2 1B | 19 | 608,000 | 7 h 15 m 36.49 s | Oct 2 03:22:10 |
| **total** | **93** | **6,116,000** | | |

Every pair was validated, watcher-committed and pushed. At the next
interactive check (Michael: “Has the series finished?”), the tree was
clean, local and remote master both
`e95d31d9247bd91ba594b4f79b3311df60611684`. Counted the actual files against
`predictor_units()`: exactly **186** files / 93 record-draw pairs, all
planned items and tier sizes represented, no orphan or unexpected file,
no halt marker. The supervisor/watcher/model processes were gone, its
watcher error was null, and all three restored MLX services were independently
confirmed loaded. No traceback/error/gate-fire appeared in the run logs.

**Model contact:** the planned trained Pythia-1b, its seed-0 untrained twin,
trained Pythia-410m and trained OLMo-2 1B read their ruled units, including
full anchor/control reproduction before new-rung collection. The real
loaders used the pinned snapshots already present after preflight; they
were online, so Hub metadata checks were possible. No outcome model ran;
`results/endpoint/` and `results/sweep/` remain absent.

The production **`seal_predictor_6.seal()` ran once**, offline with the
real pins, at **12:56:43.603788–12:56:50.793342 UTC** (7.19 s), on
`e95d31d92`. It re-derived all 93 units' provenance, coverage, digest and
tallies from the raw draws and re-derived **gate 1-P across all eight
gated units: 4,000 item comparisons, 608,000 draws, ZERO differences**.
All 33 preregistration bindings and frozen/import checks passed. It wrote
`results/predictor/gate1p.json` and `results/predictor/predictor_6.json`.

- Seal table: **187 files**, the 186 unit files plus gate 1-P.
- Composite seal SHA256:
  `5dbe5f2f700b2d64b28cfb6f29c6334eb7c12978b7bbba6051c7e0f7d9508189`.
- Seal JSON file SHA256:
  `ba36b67aa9518159d9370936b8f2295ca6017b6c8ddc9471860e82637870dd7a`.
- Exact status and gate totals: scratch directory's `seal-summary.json`.

No Experiment 6 analyzer or cold-battery read sweep was invoked. The
predictor seal is a stage-integrity check, not an outcome verdict.
Commit/push these two files and this entry, then cut/verify/push the
annotated `exp6-predictor-sealed` under the ruled run plan.

**Next owner gate: the first Vast rental for outcome preflight/endpoints.**
Read-only account/search calls at **12:58:51 UTC** found **zero instances**.
No free-ingress A100 80 GB offer met the verified/on-demand, reliability
>.95, download ≥500 Mbps, 250 GB disk filters. The current recommended
paid-ingress offer is **46878740**, machine **146514**, A100 SXM4 80 GB in
Czechia: **$1.0763/h including 250 GB storage**, ingress **$0.002/GB**,
egress **$0.003/GB**, advertised 2,078.9 Mbps download, reliability .9973134.
This is an offer for Michael's approval, including its departure from the
design's free-ingress assumption; no instance was created. The live offer
must be rechecked at authorization. Search results are saved outside the
repo as `exp6-vast-offers-20261002.json` in the approved scratch directory;
no credential was printed or written there.

### Predictor tag verified and pushed — 2026-10-02 UTC

Seal/evidence commit **`b4089a72ea225d4e4e100b3612cbb423a2f489c8`** pushed.
Annotated **`exp6-predictor-sealed`**, object
`7a7ff55eb9a0619dc7ea4e6af6049a8bf7060a2f`, points to that commit.
`endpoint_6.require_predictor_seal` passed against real git: **188 bound
files** (187 in the table plus the seal JSON). The preregistration's 33
bindings and frozen/import checks also passed. The production endpoint
dry run lists exactly eight pending loads: final/init for all four families.
No model loaded during these checks. Pushed the tag and independently
verified both its object and peeled commit with `git ls-remote`.

Predictor stage complete and sealed. Next is Michael's authorization of
the Vast rental quoted above, followed by thermal screening, box setup,
outcome preflight and endpoint collection. No rental is active; no
predictor process or watcher remains; the Mac services are restored.
