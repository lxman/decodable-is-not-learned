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
