# Experiment 6 — Progress Ledger

Design: ../../experiment-6-design.md (dials a–u RULED 2026-09-27).
Battery plan: ../../docs/superpowers/plans/2026-09-27-exp6-battery.md.
Entries are append-only. Every network contact is logged here when made.

## Model contact

None.

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
