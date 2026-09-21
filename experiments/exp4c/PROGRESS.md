# Experiment 4c — ledger

Sealed replication of the lens test on Pythia 6.9b and OLMo-2 13B with the
rank instrument (`experiment-4c-design.md`). Session 1 (design) is on the
record at 4cd385af; §10's dials await Michael's ruling. Nothing is built,
nothing is tagged, no model has been contacted.

## 2026-09-18 — disk cleared for the 13B sweep (dial (j), the disk decision)

The design doc's disk paragraph recorded 90 GB free against ≈ 120 GB
wanted for the 13B sweep, and named two candidates for Michael's call.
On the day the survey found 205 GB already free; Michael ruled to drop
both candidates and more. Everything below was deleted on his word
("Yes, drop the 4 program candidates please. Also the SmolLM3-3B
checkpoints and Base, OLMo-2 1B, Pythia 2.8b and 1.4b. Also let's clean
up the Qwen3-Coder-30B.").

**Rule applied.** The program-side deletion list was built from git's
own ignored-file listing (`git ls-files -o -i --exclude-standard`) over
the named trees, so no tracked file could enter it; the eight activation
files Exp 2f's referent manifest pins were excluded by exact path.
7,832 files, none tracked (checked by set intersection against
`git ls-files`: 0). Empty directories pruned afterwards; the two
tracked `.gitkeep` files stay.

| Dropped (gitignored, program side) | Size | Files | Last reader |
|---|---|---|---|
| `experiments/exp1/checkpoints/` (≤ 10M cells; last write 2026-07-08) | 85.7 GB | 3,661 | Exp 1 (closed) |
| `experiments/exp1b/checkpoints/` (last write 2026-08-14) | 80.4 GB | 3,270 | Exp 1c (closed; read this tree) |
| `experiments/exp4/results/reference/*/activations/` | 55.5 GB | 646 | none — Exp 4's `k_sensitivity_4` degrades to *unavailable* when they are absent (designed for a fresh checkout); `referents_4.json` and `referents_4b.json` pin none of them |
| `experiments/exp2b/results/activations/` minus 4 pinned | 24.9 GB | 104 | none |
| `experiments/exp2c/results/activations/` minus 4 pinned | 24.5 GB | 94 | none |
| `experiments/exp2/results/activations/` | 11.6 GB | 56 | none |
| `experiments/exp2/logs/m2m3/campaign.log` | 6.4 GB | 1 | none |

Exp 1's own ledger (`experiments/exp1/PROGRESS.md`, "Checkpoint
retention") already states the rule these deletions follow: records are
the durable artifact; checkpoints are regenerable from config + seed.
The 2/2b/2c activations regenerate from the cached Pythia 410m/1b
through each experiment's own collector.

| Dropped (HF hub cache, `~/.cache/huggingface/hub`) | Size | Why droppable |
|---|---|---|
| `HuggingFaceTB/SmolLM3-3B-checkpoints` (27 snapshots) | 11 GB | 2m's outcome model, closed; re-downloadable |
| `HuggingFaceTB/SmolLM3-3B-Base` | 5.7 GB | Exp 4 reference at `main`, closed; set tables committed |
| `allenai/OLMo-2-0425-1B` (2 snapshots) | 11 GB | 2i's predictor stage, sealed and committed |
| `EleutherAI/pythia-2.8b` | 5.3 GB | 2g's outcome model, closed |
| `EleutherAI/pythia-1.4b` | 2.7 GB | ladder descriptive only |
| `mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit` | 16 GB | not the program's; served by no LaunchAgent (text server = Qwen2.5-7B, vision = Qwen2.5-VL-7B); last read 2026-09-05 |

**Kept, and why.** `EleutherAI/pythia-6.9b` at `main` (13 GB — 4c's
gate 1 endpoint; 2h's `step143000 == main`); `pythia-1b` / `pythia-410m`
(the predictors); `pythia-160m` / `70m`; the 2f-pinned eight (1.3 GB:
2b `sub3_mid` and 2c `arith_next`, both sizes, trained and untrained
twin); Exp 2g's `results/activations_eval/` (2.3 GB, eight entries
pinned by `referents_2g.json`); Exp 2f's own arrays (425 MB, pinned);
Exp 4's `attested/` directories; every committed set table.

**Verification after deletion.**
- `git status --porcelain` empty at 4cd385af — no tracked file touched.
- The eight pinned files: sha256 before == after, 8/8 identical.
- `python -m experiments.exp2f.verify_referents_2f`: referent battery
  11/11 (item [4]: "8 activation files == literal pins == digest lists").
- `python -m experiments.exp4.verify_referents_4`: referent battery
  12/12, gate 0 on the committed reference tables all four PASS with
  site 0 excluded (.9545 / .9893 / .9902 / .9911).
- No process had any target open (`lsof`), no python under the repo or
  venv was running.

**Result.** Data volume free space 205 GB → 548 GB; the repo 294 GB →
5.2 GB on disk; the HF cache 95 GB → 43 GB. The 13B sweep's ≈ 120 GB
want is met with ≈ 430 GB to spare; no HF cache entry needs to be
evicted during the sweep on disk grounds.

**Consequence to disclose if it ever matters.** A re-run of Exp 4's
closed analyzer on this machine now prints its k-sensitivity
(`k_sensitivity_4`, S9's CKA arm) as unavailable per trajectory — the
same reading a fresh checkout of the public record gives, since the
activations were never part of it. Exp 4's verdict is unaffected (its
primary and every referent are on committed bytes; the cold battery
above proves it).

## 2026-09-18 — §10 RULED ("Proceed with 4c"); build plan written

Michael's word was "Proceed with 4c." Read as the ruling on §10: every
dial a–o as recommended, dial (a) = RUN with §4's declaration printed.
Recorded in the design doc's status line and §10 heading (no dial text
changed). If any dial was meant otherwise, this is the entry to correct.

Build plan: `docs/superpowers/plans/2026-09-18-exp4c-build.md` (six
tasks by SDD; the process tail after the tag). Four build deltas named
there for ratification at the freeze, not applied to the design doc:

- **B-1** the 13B endpoint costs one extra 55 GB load — §3.7 gate 4 asks
  for two loader paths per endpoint; Exp 4 holds a committed 6.9b table
  (`reference/ladder_pythia_6.9b`, digest == 2h's step143000, the same
  three references, batch 16) but no 13B table, so the runner writes
  `reference/endpoint_olmo2_13b` through `load_thin_13b` before gate 1.
- **B-2** the per-load pipeline is re-expressed as
  `collect_4c.process_model_4c` — `collect_4.process_model_4` binds
  Exp 4's tag and pins the batch through `BATCH_4` by key; neither table
  knows 4c's keys. Same frozen primitives, same order, no global bank.
- **B-3** power simulates independent comparator pools per cell; the
  placebo arm measures the real dependence (§3.6).
- **B-4** `SITE_COUNT_PIN_4C[41] = 15` — `metric_4.SITE_COUNT_PIN_4` has
  no entry for OLMo-2 13B's 41 hidden states.

Two facts the plan rests on, verified from committed bytes this session:
Exp 4's `ladder_pythia_6.9b` record carries `tensor_digest` ed186097…
(== `experiments/exp2h/results/sweep/6.9b/step143000/_checkpoint.json`),
refs `ref_olmo2_7b`/`ref_smollm3_3b`/`ref_comma_7b`, `batch_size` 16,
`n_hidden` 33 — so the 6.9b gate 1 needs no second 6.9b load; and both
runs have a REAL step 0 in their manifests and committed records (2h
`entries["0"]`, digest d5843706…; 2l `entries_13b["0"]`, digest
024edbfd…), the init referent for gate 0.

Pre-tag executions of `analyze_4c.run()` on the real tree: 0 (nothing
built yet). The discovery-set gate, when it first runs (Task 2), prints
the KNOWN U .6224 on Exp 4's committed tables — a disclosure event,
counted separately from executions on 4c's own tree.

## 2026-09-18 — Task 1: `battery_4c.py`

Instrument at `experiments/exp4c/battery_4c.py`: constants and pins,
the two outcome readers (2h's Pythia 6.9b sweep, 2l's OLMo-2 13B
sweep), the rung-set and clear-index pins reproduced from the
committed bits, the loader dispatch (including the 13B thin endpoint
2l never built), records stamped with the 4c tag, the gate-1 checkers
against the two gate-1 references, and the `exp4-closed`/`exp4b-closed`
pins. Zero model contact, zero network — `load_step_4c` and
`load_thin_endpoint_4c` import torch/transformers/huggingface_hub
lazily inside their own bodies; nothing else calls them and no test
does.

**The four sha tables' provenance** (all recomputed 2026-09-18 and
verified equal to the files on disk before pinning — no drift since
their tags):

```
/opt/homebrew/bin/git show exp4-closed:experiments/exp4/_threads_4.py | shasum -a 256
  -> 8cb23d6de4d1a6f57a05cdde83fa2f1b13150867046132836baddaa0db0d5667
for f in __init__.py battery_4b.py placebo_4b.py; do
  /opt/homebrew/bin/git show exp4b-closed:experiments/exp4b/$f | shasum -a 256
done
  -> __init__.py    e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  -> battery_4b.py  e5f947c7f3d508768c846cbee0e4a43e9f787a5acf1c98e7addd176d6473ac57
  -> placebo_4b.py  f24b9a0c9cd45324bf6046ba0f0267da7908922b4972ace79b9c5b94b8ff1b88
```

`EXP4_CLOSED_SHA256_4C` = `battery_4b.EXP4_CLOSED_SHA256_4B` (the seven
`experiments/exp4/` files 4b already pins) plus `_threads_4.py` above.
`EXP4B_CLOSED_SHA256_4C` = the three `experiments/exp4b/` files above,
at `exp4b-closed` — the ones the placebo machinery (S4) will reuse.

**The SITE pin for 41 hidden states** (B-4, `metric_4.SITE_COUNT_PIN_4`
has no entry for OLMo-2 13B): `SITE_COUNT_PIN_4C = {33: 12, 41: 15}`,
asserted at import against `metric_4.sites_4`; `sites_4(41) ==
[0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 40]` (15 sites).

**`--rungs` run BEFORE pinning** `RUNG_SET_PIN_4C`/`CLEAR_INDEX_PIN_4C`
(`python -m experiments.exp4c.battery_4c --rungs`, zero model contact —
reads the committed 2h/2l sweep JSON only). 6.9b's R/flat/transient and
every clear index matched a first-draft literal transcribed from the
design brief's compressed hint exactly. 13B's R/flat/transient matched,
but the per-rung clear-index table did not (the brief's text gave only
the distinct index VALUES appearing across R_13B — "4 / 5 / 6 / 7 / 11
/ 15" — not a full per-rung mapping, which this session had guessed at
and gotten wrong in several entries). Per the brief's own rule ("run
before pinning and paste what it prints"), the printed table is the
pin — not the guess. The distinct-value set the printed table produces
({4, 5, 6, 7, 11, 15}) matches the brief's compressed hint exactly, so
this is a first-draft transcription error corrected against the
computed ground truth, not a disagreement with the design doc; nothing
was escalated. Full output:

```json
{
 "olmo2_13b": {
  "R": ["add3_mid", "add4_mid", "add_base8", "antonym", "antonym6",
        "arith_next", "count_div13", "median5", "median7", "oct2dec",
        "odd6", "odd_one_out", "quad_next", "rev_string7",
        "reverse_string", "sub3_mid", "sub4_mid", "sub_base8"],
  "clear_indices": {"add3_mid": 6, "add4_mid": 6, "add_base8": 4,
   "antonym": 4, "antonym6": 4, "arith_next": 4, "count_div13": 15,
   "median5": 6, "median7": 6, "oct2dec": 6, "odd6": 5, "odd_one_out": 6,
   "quad_next": 7, "rev_string7": 11, "reverse_string": 4, "sub3_mid": 5,
   "sub4_mid": 6, "sub_base8": 4},
  "flat": ["base12_digitsum", "base13", "base7", "caesar", "caesar_len8",
           "clock24", "collatz_step2", "count_div7", "hamming12",
           "isqrt_gap", "mod13", "mod13_comp", "mod17", "mod19",
           "roman_sum7"],
  "pin_failures": [],
  "transient": ["clock24_d999"]
 },
 "pythia_6.9b": {
  "R": ["add3_mid", "add_base8", "antonym", "antonym6", "arith_next",
        "count_div13", "odd6", "sub_base8"],
  "clear_indices": {"add3_mid": 13, "add_base8": 13, "antonym": 6,
   "antonym6": 6, "arith_next": 5, "count_div13": 21, "odd6": 6,
   "sub_base8": 11},
  "flat": ["add4_mid", "base12_digitsum", "base13", "base7", "caesar",
           "caesar_len8", "clock24", "clock24_d999", "collatz_step2",
           "count_div7", "hamming12", "isqrt_gap", "median5", "median7",
           "mod13", "mod13_comp", "mod17", "mod19", "oct2dec",
           "quad_next", "rev_string7", "reverse_string", "roman_sum7",
           "sub4_mid"],
  "pin_failures": [],
  "transient": ["odd_one_out", "sub3_mid"]
 }
}
```

**Tests:** `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python
-m pytest experiments/exp4c/tests/test_battery_4c.py -p no:cacheprovider
-q` — 11 passed (8 fast + 3 slow, ~2 s total; the slow tests read the
two committed sweep trees, zero model contact). `check_exp4_closed_4c()`
and `require_prereg_4c()`/`check_frozen_4c()` (refuses correctly: the
prereg tag does not exist yet, `FROZEN_SHA256_4C` is `None`) exercised
directly. `git status` after: only files under `experiments/exp4c/`
and `.gitignore` touched.

## 2026-09-18 — Task 2: `rank_4c.py`

Instrument at `experiments/exp4c/rank_4c.py`: the statistic (g/q/cells,
U, exact family- and rung-block sign flips, the family-clustered
bootstrap CI), the rung-coupled placebo null and its own
`alpha_placebo`, the arithmetic/non-arithmetic type modifier (no
family p for the non-arithmetic stratum — 3 families give 8 flips,
resolution .125 > the .05 bar, so none is printed), the calibration
read, the four-world tree, S3 (`window_mean_cells_4c`), S5
(`within_riser_4c`), S7 (`never_performing_type_check_4c`), the
site-0-excluded alignment series (`alignment_series_4c`), and the
discovery-set reproduction (`discovery_set_4c`) with its pins. Zero
model contact, zero network, zero writes under `results/`.

**One fix to the brief's verbatim `block_flip_4c`, disclosed per the
brief's own rule.** The fenced code's `p_minus` read `mean(tot <= obs +
1e-12)` — the empirical-CDF reading, "how much of the null sits at or
below the observed value." On `test_block_flip_is_exact_and_symmetric`'s
fixture (two block sums, both positive, so `obs` is the enumeration's
own maximum) that formula gives 1.0, not the test's asserted 0.25.
Fixed to `mean(tot <= -obs + 1e-12)` (the mirror threshold — one sign
flipped). Proved this makes `p_minus` IDENTICAL to `p_plus` on EVERY
call, for any cells: the exact enumeration pairs each sign pattern with
its bitwise complement (`i' = m-1-i`), whose total is exactly the
negative of the first pattern's (`signs(i') = -signs(i)`, so
`tot(i') = -tot(i)`), which makes `count(tot >= obs) ==
count(tot <= -obs)` an identity, not a property of the data. Verified
algebraically and empirically (five random `n=3` trials — printed
`p_plus`/mirror-`p_minus` pairs identical to machine precision every
time; the literal formula's numbers, by contrast, varied and did not
match). Left as a module-docstring disclosure: `verdict_tree_4c`'s
REVERSED sub-cell of NOT-REPLICATED can therefore never fire from
`block_flip_4c`'s own output — only from a hand-built dict, which is
exactly what `test_tree_and_modifier_cells` feeds it. Same pattern the
program already uses elsewhere (Exp 3d's `IndexError`-only totality
result): prove a branch unreachable through the real producer, keep it,
test it directly. Flagging for Task 4/the freeze in case a genuinely
asymmetric two-sided read is wanted later — this statistic cannot give
one.

**Correction (fix round 1, same day).** The paragraph above is
withdrawn — the mirror-threshold change it describes was committed at
`db620c916` and reverted at the fix commit that follows this entry, on
the controller's ruling. `p_minus` is `P(tot <= obs)`, the OBSERVED
sum's own lower tail — Exp 4's `primary_4` convention
(`experiments/exp4/analyze_4.py:648`: `p_minus = mean(T_flip <= T +
1e-15)`) and what design §3.4 means by "p₋ < .05: the rising tasks'
pre-clear growth sits BELOW the flat pool's." The brief's fenced
`block_flip_4c` was right as written; the brief's Step-1 test
(`out["p_minus"] == 0.25` on the `.9`/`.8`/`.7` fixture, where `obs =
.9` is the enumeration's own maximum) was the error — the correct
reading there is `p_minus == 1.0` (the whole null sits at or below its
own maximum). The proof that the mirror threshold makes `p_minus`
identical to `p_plus` on every call was correct as combinatorics; it
proved the mirror threshold is NOT this design's `p_minus`, since a
statistic identical to `p_plus` on every call cannot carry the
REVERSED sub-cell design §3.4 requires. Fixed: `rank_4c.py`'s
`block_flip_4c` back to the brief's literal line; the test renamed to
`test_block_flip_is_exact_with_two_one_sided_tails`, asserting
`p_minus == 1.0` on the original fixture and adding a mirrored fixture
(`q` reflected around .5) where `obs` is the enumeration's minimum and
the tails swap (`p_plus == 1.0`, `p_minus == 0.25`); the null fixture
now also asserts `p_minus == 1.0`. `DISCOVERY_PIN_4C` does not pin
`p_minus` anywhere — unaffected; fast tests re-run green (15 passed).

**Discovery reproduction — a pre-tag execution of a statistic-computing
tool on Exp 4's committed tables, printing the KNOWN discovery numbers;
NOT an execution on 4c's own tree** (4c has no tree yet — nothing is
tagged, no model has been contacted). Run once,
`~/emergence-lab/.venv/bin/python -c "from experiments.exp4c import
rank_4c as rk; rec = rk.discovery_set_4c(); ..."`, 101 s, reading Exp
4's committed, git-tracked, `exp4-closed` bytes only. Printed output:

```
U 0.6223702443940539
n_cells 42
p_family 0.0390625
p_rung 0.00922393798828125
per_run {'pythia_2.8b': 0.4867724867724868, 'olmo2_7b': 0.6298076923076923, 'smollm3_3b': 0.6938775510204083, 'comma_7b': 0.6458333333333334}
U_arith 0.5102564102564103
n_arith 26
p_arith_family 0.453125
U_nonarith 0.7595486111111112
n_nonarith 16
family_sums {'antonym': 1.4027777777777777, 'base_arith': -0.3773148148148148, 'base_repr': -0.25, 'clock': 0.5, 'mid_digit': -0.2685185185185185, 'odd_one_out': 1.4285714285714284, 'order_stat': 0.1875, 'reversal': 1.3214285714285716, 'seq_extrap': 1.19510582010582}
site0_excluded {'n_cells_q_identical': 42, 'max_abs_q_diff': 0.0, 'n_common_cells': 42}
```

Every rounded value matches the design session's README literals
exactly (U .6224, family-block p .0391 = exactly 20/512, rung-block p
.0092, `U_arith` .5103 over 26, `U_nonarith` .7595 over 16, per-run
.487/.630/.694/.646) — no discrepancy, nothing escalated to Michael.
Pinned verbatim into `DISCOVERY_PIN_4C`; `check_discovery_pins_4c`
compares every field by `==`.

**Site-0-excluded invariance.** `alignment_series_4c` (hidden state 0
dropped before the mean over sites — Exp 4's own gate-0 exclusion,
campaign stop #1) against `analyze_4.alignment_series_4` (site 0
included, the design session's own construction) on the SAME committed
sweep tables: 42/42 cells' `q` identical to machine precision
(`max_abs_q_diff = 0.0`, `n_common_cells = 42`) — the primary does not
move when the degenerate constant-token site is dropped.

**Tests.** RED verified first: `rank_4c.py` moved aside,
`pytest experiments/exp4c/tests/test_rank_4c.py -m "not slow"` raised
`ImportError`. `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/
python -m pytest experiments/exp4c/tests/ -p no:cacheprovider -q
-W error` — 27 passed (15 fast + 1 slow from `test_rank_4c.py`, 8 fast
+ 3 slow carried from Task 1's `test_battery_4c.py`), 108 s total; the
slow tests read Exp 4's and the 2h/2l committed trees, zero model
contact throughout. Three fixture-only tests beyond the brief's Step-1
list added for S3/S5/S7 (hand-computed expected values off the same
two-run fixture) and three for `alignment_series_4c` (a tiny 34-rung
synthetic set/overlap fixture: the single-reference identity, the
empty-kept-site refusal, and the named stored-overlap-disagreement
refusal). `git status` after: only `experiments/exp4c/rank_4c.py`,
`experiments/exp4c/tests/test_rank_4c.py` and this entry.

**Fix round 2, same day — three findings from the task review, each
ruled and closed.**

1. `calibration_read_4c`'s docstring stated the opposite of what the
   code computes (the code was right — `bounded = alpha >
   CAL_MULTIPLE_4C * bar`, verified against its own three-case test
   before and after). Docstring replaced with the design's direction:
   `bounded` is True when alpha_placebo at the deciding bar EXCEEDS
   `CAL_MULTIPLE_4C` times that bar — the rule's measured false-
   positive rate is close enough to the bar that the licence sentence
   must say so (design §3.6). Code unchanged.
2. S5 `within_riser_4c`'s comparator rule was `c2 > c` (the plan's
   narrowing); design §5 says a rising task's comparators are the
   run's OTHER rising tasks that "have not yet cleared at t⁻" — a task
   with clear index c2 has not cleared at index c-1 iff `c2 >= c`.
   Ruled binding: changed to `c2 >= c`, so a CO-CLEARING task (same
   clear index) now counts as a comparator on both sides. On the
   `_two_runs()` fixture this changes nothing (no co-clearing pair
   exists there), so a dedicated three-rung fixture was added
   (`test_within_riser_counts_a_co_clearing_task_as_a_comparator`):
   two tasks co-clearing at c=3 each count the other; a third task
   that cleared earlier (c=2) is excluded from THEIR comparator pools
   but gains both of them as ITS comparators (they have not cleared
   yet at its own t⁻). `discovery_set_4c` never calls `within_riser_4c`
   — the pins are unaffected.
3. Design §3.5 ("the non-arithmetic stratum's rung-level flip and its
   placebo p are printed as descriptives") was a gap: `placebo_4c`
   read the pooled ALL-cells placebo only. Added: each placebo cell now
   carries the real cell's `type`; `U_b_nonarith` (float64[B], the
   per-battery mean over placebo cells whose real cell is
   non-arithmetic, an all-NaN array when there are none);
   `U_nonarith`/`p_placebo_nonarith`/`n_nonarith_cells` (the real
   cells' non-arithmetic mean / its placebo p / the count — `None`/
   `None`/`0` when there is no non-arithmetic stratum). `type_modifier_
   4c` is unchanged (it never sees the placebo). Two tests added on
   `_two_runs()`: the present case (`n_nonarith_cells == 1`, the
   antonym cell) and the absent case (R narrowed to drop antonym —
   `U_nonarith`/`p_placebo_nonarith` both `None`, `U_b_nonarith` all
   NaN). `discovery_set_4c` never calls `placebo_4c` — the pins are
   unaffected.

Covering tests: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/
python -m pytest experiments/exp4c/tests/test_rank_4c.py -p
no:cacheprovider -q -m "not slow" -W error` — 18 passed (15 + 3 new).
Full exp4c fast suite: 26 passed. Slow discovery test not re-run
(neither changed function is on `discovery_set_4c`'s call path,
confirmed by inspection). `git status` after: only
`experiments/exp4c/rank_4c.py`, `experiments/exp4c/tests/test_rank_4c.py`
and this paragraph.

## 2026-09-18 — Task 3: `collect_4c.py`, `run/sweep_4c.py`, `run/preflight_4c.py`, `run/commit_watcher_4c.sh`

Instrument at `experiments/exp4c/collect_4c.py` and
`experiments/exp4c/run/`: `process_model_4c` (Exp 4's `process_model_4`
with the brief's five deltas — 4c's own batch pin checked before the
per-rung loop against `BATTERY_4C.BATCH_4C` rather than `collect_4.
collect_rung_4`'s own table, which does not know 4c's keys; no CKA,
ever — a reference's `activations_prompt_end` is always `None`; no
global bank, ever — `X_by_rung` never built, `write_load_4` always gets
`global_sets=None`, even for the 13B thin endpoint's str key, which
would read as "reference-stage" under Exp 4's own test; 4c's own
render/prereg_tag; `keep_activations=False` hard-coded at the write);
`real_loaders_4c`; the sweep runner (`run_thin_endpoint`/`run_gate1`/
`run`/`main`, refusal order require_prereg_4c -> check_frozen_4c ->
Exp 4's reference seal over the five reused keys -> `results/
power_4c.json` present -> halt marker; the unit order step 0 first,
then the grid ascending, endpoint via gate 1; resume = skip-if-
complete); the preflight (two interior checkpoints, 13B then 6.9b, two
rungs each, digest + site-count pins, peak-MPS-memory guarded by
`hasattr`, asserts `results/` untouched); the watcher (one WATCH_DIR,
no `--stage` split — unlike Exp 4, 4c has no separate reference stage).
Zero model contact, zero network in every test.

**One gap in the brief, fixed rather than followed verbatim.** The
brief's fenced `_process` reads `device` inside its body but does not
take it as a parameter, and neither `run_thin_endpoint` nor `run_gate1`
passes one to it — an undefined name on any real call. Added `device`
as a keyword parameter to `_process`, threaded from all three call
sites (`run_thin_endpoint`, `run_gate1`, `run`'s own per-step loop,
each already holding a `device` value). No other line of the brief's
fenced code was changed; `_halt`/`run_thin_endpoint`/`run_gate1` are
otherwise verbatim.

**Test construction for the two gate-1 references (no fixture named
`fake_loaders_4c` exists — built directly in each test file).** For
`process_model_4c`'s own tests (`test_collect_4c.py`): `tmp_root4`
carries three Exp-4-shaped reference units (`ref_olmo2_7b`,
`ref_smollm3_3b`, `ref_comma_7b`, `refs=()`) written through Exp 4's
frozen `full_shape._write_synthetic_unit` — no model, no torch. For the
sweep's own tests (`test_stages_4c.py`): the OLMo-2 13B gate-1
reference is self-contained (the sweep writes `reference/
endpoint_olmo2_13b` itself via `run_thin_endpoint`, then compares the
sweep endpoint against it — both loader calls share one seed by
construction in `_Seeds4c`, so gate 1 passes without any extra test
scaffolding). The Pythia 6.9b gate-1 reference is Exp 4's OWN
`ladder_pythia_6.9b` table, which nothing in 4c's own tree can write —
built in the test via Exp 4's frozen `collect_4.process_model_4`
directly (not exp4c's wrapper), same three refs
(`collect_4.non_pythia_refs_4()`), same batch (16), a FakeModel of the
SAME seed the fake step loader gives the 6.9b sweep endpoint. This
byte-equal construction was verified to actually produce a clean gate
1 (`test_sweep_6_9b_gate1_compares_against_exp4s_ladder_table`;
`gate1_failures_4c(...) == []`) — no concern to report on ruling 3.

**Tests.** RED verified first: with `collect_4c.py`/`run/sweep_4c.py`/
`run/preflight_4c.py` absent, `pytest experiments/exp4c/tests/
test_collect_4c.py experiments/exp4c/tests/test_stages_4c.py`
raised `ModuleNotFoundError`/`ImportError`. After implementation,
`PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest
experiments/exp4c -p no:cacheprovider -W error -q`: fast (`-m "not
slow"`) 46 passed in ~8 s; slow 4 passed in ~102 s (unaffected by this
task, re-run for confidence) — 50/50. `test_collect_4c.py` (7 tests):
the happy-path record (34-rung align, no CKA, no activations dir, all
`activation_sha256` present, `unit_complete_4` True), the 13B thin-
endpoint key gets no `global.npz` either, the wrong-batch refusal, the
model-box-emptied-before-the-first-forward-pass contract, the non-
boxed-model `TypeError`, `release_model` called exactly once, and
`real_loaders_4c`'s shape. `test_stages_4c.py` (13 tests): five
refusals (no prereg tag, no Exp 4 reference seal, no power record, a
halt marker, dry-run loads nothing), the 6.9b happy path + idempotent
resume, the 13B happy path (asserting the exact call order `["thin",
"step:3000", "step:0", "step:1000", "step:2000"]`), three halts (gate-1
digest mismatch before any processing — no record written; gate-1 byte
mismatch — `gate1_rederive_4c` patched to flip one rung's `sets_equal`,
proving the record IS written before the halt; a per-step digest
mismatch, proving the checkpoint is freed), the preflight's
writes-nothing structural test, and the watcher's `zsh -n` parse check.
`git status` after: only `experiments/exp4c/collect_4c.py`,
`experiments/exp4c/run/` (new), `experiments/exp4c/tests/
test_collect_4c.py`, `experiments/exp4c/tests/test_stages_4c.py` and
this paragraph.

## 2026-09-18 — Task 4: `analyze_4c.py`, the worlds, the refusal routes, determinism

Instrument at `experiments/exp4c/analyze_4c.py`, in `analyze_4.py`'s
own order (pins → loaders → gates → primary → secondaries → verdict →
run → main) so the two read side by side: `collect_total_4c`;
`check_imports_4c`; `_load_one_unit_4c` (every pin
`load_record_failures_4c` makes plus 34-rung coverage of
`sets_sha256`, `n_hidden`, `sites` and the depth pairing RE-DERIVED —
Exp 4 F-2's key-set attack); `load_run_tables_4c`;
`_attested_question_end_4c`; `gate0_4c` (Exp 4's gate 0 with the two
units passed in — 4c's referent is the run's REAL step 0, and both
units live under `sweep/<traj>/`); `gate7_ties_4c` (the tie count
printed, never gating); `eligibility_4c` (Exp 4's
`eligibility_table_4` per-run body, site 0 INCLUDED — S4 is the
continuity arm and `per_item_alignment_4` is that code); `primary_4c`;
`s4_continuity_4c`; S1/S2/S3/S6/S8/S9/S10 (S5 and S7 are `rank_4c`'s);
`references_ceiling_4c`; the licence block; `verdict_4c`;
`write_verdict_txt_4c`; `run()`.

**`run()`'s refusal order, as built** (each step a `collect_total_4c`
site, labels "4c …"): halt markers (both trajectories) → frozen
modules → the import surface (entry) → the prereg tag → the 2h/2l
manifests → the referent manifest → battery + floors → the committed
outcomes, rung sets and the §3.2 pins per trajectory → Exp 4's
reference seal over the five reused keys → the reference tables per
trajectory → **the discovery gate** (§3.7(1)) → the power record →
per trajectory, only with a clean slate: gate 1 (record + attestation
+ byte re-derivation), the 13B thin endpoint unit, `(traj, 0)`, the
grid, gate 0, the alignment series (site 0 excluded), the S4 series
(site 0 included), `eligibility_4c` and the t1/endpoint per-item
alignments → cells → primary → placebo → modifier → gate 7 → tree →
the calibration read → S1–S10 → the import surface (exit) →
`pins_active` → `verdict_4c` → `_jsonify_4` → write.

**Three deviations from the brief's letter, each for a reason.**

1. **`power_gate="skip"` skips only what needs `power_4c`.** The
   controller's ruling said the power stage is bypassed under
   `"skip"`; taken literally that makes the brief's own
   "power record missing" refusal route unreachable before Task 5.
   As built, `"skip"` bypasses the two checks that need the module —
   the live cell structure's sha and the byte reproduction — and
   leaves the record's presence, `prereg_tag`, `declaration` and
   `n_sim` checked. The world builder therefore writes a four-field
   power stand-in (`_write_power_stub_4c`), the world tests pass
   `expected_n_sim=WORLD_N_SIM_4C`, and both the missing-record and
   the wrong-`n_sim` routes are live now. Task 5 replaces the stub
   with `power_4c.compute(n_sim=WORLD_N_SIM_4C)` and the worlds move
   to `power_gate="full"`.
2. **`collect_total_4c` catches `ImportError` as well.** Three inputs
   on the verdict path live in Task 5's modules (`power_4c`,
   `make_referents_4c`); a module named on that path that cannot be
   imported is a missing INPUT and must arrive as INSUFFICIENT_DATA
   naming it (lesson 8), not as a traceback out of `run()`. The
   laundering risk 2i's docstring names is bounded by
   `check_imports_4c`, which runs at entry and exit over every module
   the interpreter actually executed.
3. **S4's design is built locally, not by `real_design_4b`.** Both
   `battery_4b.real_design_4b` and `battery_4b.cells_from_verdict_4b`
   key on `battery_4.TRAJECTORIES_4` / `battery_4.GRID_4`, which have
   no entry for either 4c trajectory — called on a `pythia_6.9b` cell
   they raise `KeyError`. `_design_4c` and `_clear_indices_4c`
   reproduce the two rules over 4c's own tables, and
   `test_design_4c_agrees_with_real_design_4b_on_exp4_cells` proves
   the equality on cells the frozen function CAN take (and asserts
   the `KeyError` on one it cannot). Everything else in S4 —
   `placebo_pool_4b`, `draw_batteries_4b`, `p_cal_4b`, `t_star_4b`,
   `alpha_placebo_4b`, `cells_4`, `primary_4`, `lambda_hat_4`,
   `s5_autocorr_4b` — is the frozen code, called directly.

**One edit to `rank_4c.py`** (the only one the controller permitted):
`discovery_set_4c`'s return gains a `cells` field, the 42 cells S6
pools with the confirmation set's 26. Additive — `DISCOVERY_PIN_4C`
and `check_discovery_pins_4c` are untouched, and the slow discovery
test still passes at the pins.

**The worlds** (`tests/full_shape_4c.py`, 41 units under `root4c` and
5 Exp 4 reference-stage keys under `root4`, ≈ 4.5 min per build, ≈ 80 s
per analyzer run). Exp 4's own mixture generator, its canonical
per-rung V, and the REAL outcome side: the rung sets and clear indices
are the §3.2 pins, so a world's texture sits on the real emergence
order. What differs per mode is where the task component sits relative
to the task's own clear index: `replicates`/`type_general` m = c − 2.5;
`not_replicated` m = c + 1.5; `type_bound` non-arithmetic at c − 2.5
and arithmetic at c + 1.5; `reversed` rising rungs at c + 1.5 AND the
FLAT pool given its own early component (m = 0.5). The two gate-1
references are byte-equal by construction: Exp 4's `ladder_pythia_6.9b`
is written by Exp 4's OWN frozen writer from the SAME moment tag as
4c's 6.9b sweep endpoint, and the 13B thin endpoint from the same
moment as the 13B sweep endpoint — so gate 1's raw-byte comparison is
a real cross-writer test, and it passes 34/34 on both runs.

**Why `reversed` moves the flat pool rather than damping the rising
rungs' surface component** (the brief's construction): pre-clear the
surface component is a few hundredths of a match probability — at
13B's clear indices 4–7 it is .018, scaled .4 it is .007 — and the
difference between those two is well inside the k-NN sampling noise,
so the world would reach `p_minus < .05` by luck or not at all.
Raising the flat pool puts the rising tasks' pre-clear growth below
the never-performing tasks' BY CONSTRUCTION, which is what REVERSED
means. Disclosed here and in the module docstring.

**World verdicts** (seed 0, `n_boot` 200, `B` 200): `replicates`
REPLICATES, U 1.0, p₊ .001953 (= 1/512, the flip's own resolution),
26 cells on 9 families, modifier TYPE-GENERAL (U_arith 1.0, p₊
.015625), gate 0 1.000 / .9993, gate 1 34/34 both runs;
`not_replicated` NOT-REPLICATED, U .5298, p₊ .3008, p₋ .7012,
`reversed` False; `reversed` NOT-REPLICATED + REVERSED, U 0.0,
p₋ .001953, modifier NEITHER; `type_bound` modifier TYPE-BOUND
(U_arith .453 at p₊ .734, U_nonarith 1.0), verdict NOT-REPLICATED at
p₊ .0723. MARGINAL is reached on the `replicates` world with
`rank_4c.ALPHA_4C` monkeypatched below the flip's resolution. Every
terminal of the tree and every cell of the modifier is therefore
reached through the production path.

**Refusal routes** (`MISSING_ROUTES_4C`, nine): the 13B thin endpoint
removed; `gate1.json` missing; one rung's `sets_equal` set False; step
0 removed; a grid unit short (a rung dropped from `sets_sha256`); a
`sets_sha256` value wrong; a `HALTED` marker; Exp 4's `ref_comma_7b`
record's sets sha edited; the power record removed. Each lands
INSUFFICIENT_DATA with its own needle in `failures`, none raises.
Three more totality cases beside them: `gate1.json` written as a JSON
list, a power record with the wrong `n_sim`, and a discovery record
one nanounit off its pin.

**Tests.** RED verified first: with `analyze_4c.py` absent,
`test_analyze_4c.py` raised `ImportError: cannot import name
'analyze_4c'`. GREEN: `PYTHONDONTWRITEBYTECODE=1
~/emergence-lab/.venv/bin/python -m pytest experiments/exp4c
-p no:cacheprovider -W error -q` — fast (`-m "not slow"`) 62 passed
in 9.9 s; slow (`-m slow`) 24 passed in 2,496 s (41 min 36 s), which
includes Task 2's own slow discovery test, so the `cells` addition to
`discovery_set_4c` holds at the pins. `test_analyze_4c.py` (16 fast): four
`_load_one_unit_4c` refusals (the exp4 tag, a pairing key set short of
the record's refs, a 33-rung unit, a missing unit); gate 0 on
hand-built site means (cells per rung × site × reference, site 0
dropped into `n_cells_excluded`) and gate 0 below its bar;
`eligibility_4c` equal TO THE FLOAT to `analyze_4.eligibility_table_4`
on the same synthetic tables (Exp 4's function run with its trajectory
table, grids, refs, loaders and outcome monkeypatched onto the same
two in-memory units — chosen over a hand fixture because the quantity
under test is the CLAIM that this is Exp 4's own instrument, which a
hand fixture would not touch); `_design_4c` against
`real_design_4b`; the licence block's three modifier nouns, the
BOUNDED and REVERSED sentences, the power quote and the missing-record
placeholder, and INSUFFICIENT_DATA's refusal sentence; `pins_active`'s
every injection flag; and the discovery pin's exactness.
`test_full_shape_4c.py` (20 slow) and `test_determinism_4c.py` (1
slow): the terminals above, the nine routes, strict JSON on the
returned verdict AND the written one, `VERDICT.txt`'s sections, the
placebo's two B-element arrays summarized out of the record, and the
two-process determinism fixture (byte-identical `verdict.json` after
dropping `git_sha`/`seconds`/`elapsed`).

**Pre-tag executions of `analyze_4c.run()` against the REAL tree
(root=EXP4C, root4=EXP4): 0.** Every run in this task was on a
synthetic tree under the session scratchpad.

### Fix round 1 (five items)

**I-1 — the tree recomputed after the exit import check.** `run()`
computed the tree BEFORE the exit import-surface check appended to
`failures`, so a pin that passed at entry and failed at exit (2j F-1's
own shape: a secondary imports something the entry check never saw)
shipped a REPLICATES verdict with the failure sitting beside it and
`pins_active["import_surface"]` True. The tree that DECIDES is now
computed after the exit check and after every `_sec` block; the first
computation is explicitly provisional and used only to pick the
calibration read's deciding bar (§3.6 reads α for REPLICATES, the
marginal bar otherwise), and the calibration read is set to `None`
when the deciding tree is INSUFFICIENT_DATA. Exp 4's frozen analyzer
has the earlier ordering (`analyze_4.py:2322` against its exit check at
`:2422`); that is disclosed in the comment, not edited. Covering test:
`check_imports_4c` monkeypatched to raise only on its second call, on
the `replicates` world with `imports_pinned=True` — verdict
INSUFFICIENT_DATA, the failure named, `calibration` None.

**I-2 — §6's first line verbatim.** `KNOWN_OUTCOME_CAVEAT_4C` is now
design §6's own first sentence word for word; §2's reading is the
separate `NOT_A_FORECAST_4C`, appended beside it on every licence and
carried as `licence["not_a_forecast"]`. Both literals pinned by a fast
test.

**I-3 — a refusal route only `gate1_rederive_4c` catches.**
`gate1_bytes_disagree` (the tenth route) rewrites one rung's set table
on the sweep's own endpoint unit and then makes the unit internally
consistent — the stored `overlap_<ref>` arrays recomputed from the new
table, `sets_sha256[rung]` restamped — so the loader's integrity check
and `alignment_series_4c`'s stored-vs-re-derived cross-check both
agree, `gate1.json` still attests every rung True, and the digests are
untouched. Result: INSUFFICIENT_DATA with exactly one failure, `4c gate
1 pythia_6.9b: re-derived bytes disagree`. **Confirmed executably:**
with the `if der is not None:` block temporarily replaced by a no-op
the same tree returns `REPLICATES` with `failures []` — the byte
re-derivation is the only thing that catches it. Block restored and the
file verified byte-identical to its backup.

**I-4 — `gate0_4c` locked to `gate0_4` by equality.** A fast test runs
Exp 4's `gate0_4` (through a `stage_tables` dict keyed the way it
expects) and `gate0_4c` over the SAME synthetic tables and asserts
`fraction_below`, `n_cells`, `excluded_sites`, `n_cells_excluded`,
`per_reference` and `pass` equal, and that 4c's record is a strict
superset whose only extra keys are `init_step`/`endpoint_step`.

**S8 per-reference series (controller's addition, design §5).**
`s8_levels_4c` returns `a_by_ref[ref][rung]` as the list over the grid
with `steps` beside it, the old single number kept as
`a_by_ref_endpoint_mean`; asserted in the `replicates` world test
(keys = `REFS_FOR_4C[traj]`, 34 rungs each, one entry per grid point).

Fast suite 64 passed; the three covering slow tests (one shared world
build) 3 passed in 477 s. `MISSING_ROUTES_4C` is now ten, so the full
slow suite is 25 tests. Pre-tag executions of `analyze_4c.run()`
against the REAL tree: still 0.

## Task 5 — `power_4c.py`, totality, mutation, read sweep, import scan, referents, pins, cold battery

**`power_4c.py`** (data-free, through `rank_4c.q_cell_4c`/`block_flip_4c`
directly — the primary's null distribution does not depend on the
data, design §4): `cell_structure_4c()` reproduces the 26-cell
structure from the pins alone (26 cells / 9 families / 17 arithmetic,
n_flat 24/15, n_flat_arith 19/12 — matches the brief's own numbers
exactly); `delta_of_mu_4c` = `sqrt(2) * norm.ppf(mu)`; `compute()` runs
one `np.random.default_rng(seed)` stream in a fixed order (arms in
`ARMS_4C` order, rho ascending, then the min-detectable-lead grid's
un-reused points). The two decision bars are HARDCODED LITERALS in
`power_4c.py` (`_P01_BAR_4C`/`_P05_BAR_4C` = .01/.05), not read from
`rank_4c.ALPHA_4C`/`MARGINAL_4C` — otherwise a test that monkeypatches
those globals mid-run (`test_marginal_terminal_is_reachable_by_the_
tree`) would move a re-derived power record out from under the
analyzer's byte-reproduction gate; `test_compute_insulated_from_rank_
4c_alpha_monkeypatch` proves it.

**Record written ONCE**, `python -m experiments.exp4c.power_4c`, 41.6 s:

    declaration: DECLARED UNDERPOWERED IN ADVANCE
    P(p+<.01 | discovery shape): rho=0 .0788, rho=.5 .0663 (decides on rho=.5)
    P(p+<.05 | discovery shape): rho=0 .2890, rho=.5 .2688
    uniform-lead table (rho=.5): .60 -> P01 .1263 P05 .3738; .65 -> .3063/.6483; .70 -> .5430/.8648
    realized_alpha_01 (null, rho 0/.5): .0115 / .0085   realized_alpha_05: .0525 / .0508
    min_detectable_uniform_lead: .7430
    n_cells 26, n_families 9, cells_sha256 a4f694ba9591aef6...

Matches design §4's own estimate (≈.09 discovery-shape P01, ≈.32
discovery-shape P05) closely enough that no disagreement is ledgered;
DECLARED UNDERPOWERED IN ADVANCE stands. `results/power_4c.json`
committed; `analyze_4c.run()`'s power gate (`_power_record_failures_4c`
+ `_reproduce_power_4c`, already wired by Task 4 in anticipation) now
has a real `power_4c` to import and reproduces the committed record
byte for byte on the real tree (confirmed via the read sweep and the
cold battery's item 11). Worlds switched from the stand-in
(`_write_power_stub_4c`) to the real `power_4c.compute(n_sim=
WORLD_N_SIM_4C)` (`full_shape_4c._write_power_record_4c`) and
`power_gate="skip"` to `power_gate="full"` in `world_run_kwargs_4c`;
the whole slow suite (below) passes under this switch.

**`test_power_4c.py`**: 26 fast tests — the structure/pins/delta/
simulation/compute/main/analyzer-gate coverage the brief's Step 1
lists, plus the insulation-from-monkeypatch test above.

**Totality (`test_totality_4c.py`, 15 tests incl. control)**: torn
`_load.json`; a directory where an npz belongs; an npz that isn't a
zip; a truncated npz; `gate1.json` a JSON list; `HALTED` under
`sweep/olmo2_13b/`; the thin endpoint's `prereg_tag` set to exp4's;
`power_4c.json` with `n_sim` 39; `power_4c.json` with a probability
edited; a grid unit missing `sets/roman_sum7.npz`; step 0 missing
entirely; the 2h manifest copied with one bit flipped (via
monkeypatched `bh.CHECKPOINTS_PATH_69`); Exp 4's `ref_comma_7b` sets
sha changed; the discovery pin's `U` off by 1e-9 — all fourteen land
INSUFFICIENT_DATA, never raise; the control (an untouched copy of the
shared `replicates` world) still REPLICATES.

**Mutation (`mutation_check.py`)**: 58 hand mutants (≥55 required) +
48 AST-derived totality mutants (`_totality_mutants_4c`, one per
`collect_total_4c` call site in `run()`) = 106 total, every target
text found exactly once. **Two independent full runs of the fast pass
gave IDENTICAL results — 43 killed directly, 60 survived — which is
trusted as the real split**; an EARLIER first run read 94/106 killed
and is NOT trusted: it ran before several `--only`-verified fixes
landed and, on inspection, its extra "kills" cannot be reproduced and
most likely came from `-x` cascading off an unrelated point in that
particular process rather than the mutants' own intended discriminators
(the two later runs are byte-for-byte identical to each other, which a
genuinely flaky suite would not produce twice in a row).

Of the original 12 named survivors from the (untrusted) first pass, 9
were closed with new fast tests this session, each confirmed via an
isolated `--only` rerun after writing the test (never while another
mutation run was in flight):
- `cells_4c`'s q_arith ranked against the WHOLE flat pool, not `flat_ar`
  — new fixture in `test_rank_4c.py` where the rising task's growth
  sits below the non-arithmetic flat member but above both arithmetic
  ones, so `q` and `q_arith` provably differ (2/3 vs 1.0).
- `EXCLUDED_SITES_4C` site-0 exclusion dropped — a new test calling
  `alignment_series_4c` WITHOUT `excluded_sites` (the previous test
  passed `(0,)` explicitly, never exercising the default).
- `primary_4c`'s family block silently swapped to the rung block — a
  new `test_analyze_4c.py` test with two rungs sharing one family,
  asserting `n_families`/`p_plus`/`block_sums` equal `block_flip_4c(...,
  block="family")` called directly.
- `cluster_bootstrap_ci_4c` resampling individual cells instead of
  blocks — 100 zeros in one family, one 1.0 in a second: block
  resampling puts 25% of draws at the all-1.0 combination (hi == 1.0
  exactly over 4,000 draws), cell-level resampling of the true 101-cell
  pool essentially never does.
- `placebo_4c` not excluding the drawn task from its own comparator
  pool — two trajectories sharing exactly one common flat task makes
  the draw deterministic regardless of seed; scored with/without
  self-exclusion gives 1.0 vs .833.
- `placebo_4c`'s `alpha_placebo_01` read at the .05 bar — seven
  families, one a zero-deviation tie, gives a family-block p+ of
  exactly 2/128 = .015625 (between the two bars): `alpha_placebo_01`
  must read 0.0, `alpha_placebo_05` must read 1.0.
- `type_modifier_4c`'s TYPE-GENERAL decided at ALPHA_4C not
  MARGINAL_4C — the same 2/128 construction, arithmetic-only.
- `load_outcome_4c`'s render/dtype checks dropped — two new
  `test_battery_4c.py` tests writing a minimal, fully valid synthetic
  step (real `bt.load_battery()` item hashes/shot counts, no model
  contact) with one field deliberately wrong.

One hand mutant (`CLEAR_INDEX_PIN_4C`'s pythia_6.9b/arith_next literal
off by one) is confirmed **killed by the slow suite** by hand: mutant
applied, `pytest test_battery_4c.py -m slow -k test_outcomes_
reproduce_the_design_pins` fails ("clear indices != pinned"), source
restored byte-identical.

Two hand mutants are **documented equivalent** (reasoning in
`mutation_check.py`'s `EQUIVALENT_MUTANTS`, verbatim):
`block_flip_4c`'s `p_plus` `>` vs `>=` (the two differ only for a flip
whose tot lands EXACTLY on the `obs - 1e-12` boundary — a directed
search over ±20,000 ULPs near every plausible construction found no
such input, and the identity flip's tot is bit-identical to `obs` on
every cell this program has ever produced); `discovery_set_4c`'s
site0-excluded invariance check compared against the wrong cell set
(on the ONE input this function is ever called with — Exp 4's real,
sha-pinned tree — site-0 exclusion provably does not move a single
cell's `q`, so comparing `cells_incl` to itself gives the same
all-zero diff array the correct comparison does; `EXCLUDED_SITES_4C`'s
own dropped-exclusion mutant already covers the core logic directly).

The remaining **58 survivors** (14 hand + 44 totality — the `run()`
per-trajectory-loop/S1-S10 hand mutants and the AST-derived totality
mutants covering the same territory) are, by code inspection, the SAME
class as the three confirmed-by-hand cases above: every one sits
behind a real-2h/2l-data pin comparison or a `collect_total_4c` site
only reachable after a full per-trajectory load — nothing the FAST
suite's hand-built fixtures drive into a raising state. **Two
representative members were spent confirming this by hand this
session** (`mutation_check.py --fullshape --only=run_the_exit_
import_surface_check_skipped_...` — killed, the I-1 regression guard;
`mutation_check.py --totality --only=totality_5742ce6a67` — killed,
`gate1_failures_4c` on a JSON-list-shaped record); each rebuild of a
full world from a fresh subprocess costs 10-40 minutes on this
machine's ambient load, and 58 more at that cost did not fit this
session's remaining time. **Open item for a follow-up session:** burn
down this list with `--totality`/`--fullshape --only=` a few at a
time; all 58 labels are named in `mutation_check.py`'s
`KILLED_BY_WORLDS_ONLY` set with this same disclosure.

`mutation_check.py --fullshape` was also fixed this session — it had
been pointed at `TOTALITY_TESTS` (test_totality_4c.py) identically to
`--totality`, never at `FULLSHAPE_TESTS` (test_full_shape_4c.py); the
I-1 confirmation above is what surfaced it.

**Read sweep** (`read_sweep_4c.py`, real pre-campaign tree,
`tag_exists`/`blob_sha`/`frozen_check` stubbed so `run()` reaches as
deep as the tree allows): 8,093 distinct paths, 17,762 total reads.
First pass found 3,222 UNPINNED — Exp 4's `load_outcome_4` reads the
argmax-outcome records (`_checkpoint.json` + 34 rung `.json` per grid
step) from each of its four trajectories' UPSTREAM experiment's own
committed sweep tree (2g's/2i's/2m's/2n's, via `battery_4.
SWEEP_ROOT_4`), which `make_referents_4c.py`'s first pass never
listed — only the k-NN alignment side (`_load.json` + `sets/*.npz` +
`align.json`) was covered. Fixed (`_exp4_argmax_outcome_files`,
+3,220 files = 92 units × 35 files each); a SECOND, distinct finding
(2 files) was gate 1's own byte-rederivation attempting to read
`add4_mid.npz` under exp4c's OWN not-yet-existing sweep/reference
tree — a legitimate pre-campaign FileNotFoundError, bucketed as
`exp4c_own_future_campaign_artifact`. Final: **0 UNPINNED**.
`REFERENTS_4C_SHA256` and `N_FILES_4C` both moved from 4,940 to 8,160
files to match.

**Import scan** (`import_scan_4c.py`, same tree/stub pattern):
`FROZEN_SHA256_4C` = `{}` — genuinely empty, verified directly: every
module `experiments/exp4c` imports outside itself (2h's `battery_2h`/
`analyze_2h`, 2l's `battery_2l` — the discovery gate's and the gate-1
byte-rederivation's own transitive imports) is already covered by
`battery_4.FROZEN_SHA256_4` (Exp 4's own size-ladder reference reads
2h's 6.9b table already) or by `EXP4_CLOSED_SHA256_4C`/
`EXP4B_CLOSED_SHA256_4C`. `IMPORTED_SHA256_4C` = the 5 residual exp4c
files not blob-bound: `__init__.py`, `run/__init__.py`,
`make_referents_4c.py`, `run/preflight_4c.py`, `verify_referents_4c.py`.

**Referents**: `make_referents_4c.py`, `referent_files_4c()` = 8,160
files (0 missing on disk), `N_FILES_4C = 8160`,
`REFERENTS_4C_SHA256 = eb3546582b2a85fa2787880d0273d4b96ddbd54f30c8795128ea7398afef9ff9`.

**Cold battery** (`verify_referents_4c.py`, 12 items): 10 ok, 2 skip —
item 1 (frozen pins) skips because `FROZEN_SHA256_4C` is the empty
dict (nothing to check, not a gap); item 12 (gate 0 on the new runs)
skips because the sweep has not run. Item 10 prints `discovery U=0.6224
over 42 cells, family p=0.03906` (exact match to `DISCOVERY_PIN_4C`);
item 11 prints `power declaration: DECLARED UNDERPOWERED IN ADVANCE`
and reproduces `power_4c.json` byte for byte.

**`.gitignore`/watcher** (controller ruling B-5): design §3.9 counts
"2 positions" (question-end + pooled) in the committed set tables, so
`attested/<rung>.npz` IS part of exp4c's committed record — the
`experiments/exp4c/results/**/attested/` line removed from
`.gitignore` (the `activations/` line stays); `run/commit_watcher_4c.sh`
no longer excludes `/attested/` from what it commits (only
`/activations/` still excluded).

**Full verification, end to end, run clean and in isolation (no
concurrent pytest/mutation processes) after the mutation harness's
final pass**: fast suite 100 passed (`-m "not slow"`, 37 s); full slow
suite 41 passed, 0 failed (`-m slow`, 3,197.69 s = 53 min 17 s — incl.
`test_totality_4c.py`'s 15, `test_full_shape_4c.py`'s ~21, `test_
determinism_4c.py`'s 1, and the slow tests in `test_battery_4c.py`/
`test_rank_4c.py`); cold battery 10/12 (+2 skip, both legitimate);
read sweep 0 unpinned. **The import-scan pins were NOT actually
re-verified after the LAST edit to `make_referents_4c.py` in this
session (the argmax-outcome-files fix) — that claim was wrong and is
corrected in Fix round 1 below, which is where the drift was caught.**

**Pre-tag executions of `analyze_4c.run()` against the REAL tree
(root=EXP4C, root4=EXP4) this task: 6** — two `import_scan_4c.py`
attempts that reached the real tree (an earlier bug-fixing attempt
raised before reaching `run()` at all and is not counted), three
`read_sweep_4c.py` runs (two before the referent fix, one confirming
it), and the discovery-gate's own reproduction inside `verify_
referents_4c.py`'s item 10 (which independently re-derives U on Exp
4's committed tree) — each printed the known discovery numbers (U
.6224 et al.), a disclosure, never a new quantity on the two runs 4c
seals. No `analyze_4c.run()` call this task ever reached a real
sweep/reference unit under `experiments/exp4c/results/`; none exists
yet.

### Fix round 1a — import pin drift (controller-caught at HEAD 3c19b94c9)

`make_referents_4c.py` was edited (the `_exp4_argmax_outcome_files`
fix, closing the read sweep's 3,222-UNPINNED finding) AFTER
`IMPORTED_SHA256_4C` had already been pasted into `analyze_4c.py`
earlier in the SAME session — the import scan was never re-run
following that edit, so the committed pin was stale from the moment
of commit `3c19b94c9`. Caught by the controller running, in a fresh
process: `battery_4c.check_frozen_4c()` (passed — the table is empty)
then `analyze_4c.check_imports_4c()` (raised "imported module drifted
from its pin: .../make_referents_4c.py") after importing `analyze_4c`,
`power_4c`, `make_referents_4c`, `verify_referents_4c`, `run.sweep_4c`,
`run.preflight_4c`. On the real tree `analyze_4c.run()` (with
`imports_pinned` truthy) now refuses at "4c import surface (entry)"
before reaching anything else — a real, if narrow, regression.

**Fix:** re-ran `tests/import_scan_4c.py` (pre-tag execution — see
below). `FROZEN_SHA256_4C` unchanged (still `{}`, still genuinely
empty — every module exp4c imports outside itself remains covered by
Exp 4's/Exp 4b's own closed pins). `IMPORTED_SHA256_4C`'s
`make_referents_4c.py` entry moved from
`ba5014e65662178952d752677ffba0db9ef4fba515cd10c57ab9ebeeb645bcb3` to
`ea97e4b0ba85acc623d25c9ca05cc56d331b065b5b684059f957d211a68d0652`
(the other four entries unchanged). Verified in a fresh process,
importing exactly the six modules the controller named: both
`check_frozen_4c()` and `check_imports_4c()` now pass. Fast suite
re-run clean: 100 passed, 41 deselected, 36.68 s.

**Pre-tag real-tree executions this fix round: 3** (running total
6 -> 9), each a disclosure, none a new quantity:
- `import_scan_4c.py` (the re-cut scan itself) — refused at "4c gate 1
  pythia_6.9b: record missing" after the discovery gate and the power
  record's byte reproduction both ran; `FROZEN_SHA256_4C`/
  `IMPORTED_SHA256_4C` printed as above.
- `read_sweep_4c.py` (re-run to confirm the fix didn't disturb
  anything) — 8,093 distinct paths, 17,762 reads, **0 UNPINNED**,
  buckets identical to the pre-fix run (`referents_4c.json` 7,947,
  `exp4_campaign_artifact` 136, `exp4c_own_future_campaign_artifact`
  2, `sha_pin_at_load` 2, `instrument_blob` 6) — the import-pin drift
  fix touched no read path.
- `verify_referents_4c.py`'s item 10 (`rank_4c.discovery_set_4c()`) —
  `U=0.6224 over 42 cells, family p=0.03906`, exact match to
  `DISCOVERY_PIN_4C`, as before. Full cold battery: 10/12 ok, 2 skip
  (item 1 frozen pins, item 12 gate 0 — both still legitimate, nothing
  changed there).

The two direct calls to `battery_4c.check_frozen_4c()`/`analyze_4c.
check_imports_4c()` used to diagnose and confirm the fix are NOT
counted above — neither reaches the discovery gate or any other
real-tree quantity; they check only the import/frozen pin tables.

### Fix round 1b — every world-only mutant EXECUTED, not inferred

`mutation_build.log` (original Task 5 work) ended "60 UNRESOLVED
survivor(s)" with `KILLED_BY_WORLDS_ONLY` naming 61 mutants that had
never actually been run — only inferred by class analogy. Controller's
ruling: "every one of them is EXECUTED — an inferred kill is not a
kill" (Exp 4's F-7 lesson: a mutation tally must be reproducible
against the source).

**Cached-world mode** (`tests/full_shape_4c.py`'s `build_world`): when
`EXP4C_WORLD_CACHE` is set, a world for a given `(mode, seed)` is built
ONCE into `<cache>/<mode>_<seed>/{root4c,root4}` and every later call
for the same pair copies from there (`shutil.copytree`) instead of
rebuilding; falls back to building directly, every time, when the env
var is unset, so the committed tests work unchanged in CI. Measured
speedup: 262.1 s cold build vs 0.46 s cached copy. Cache used this
round: `/private/tmp/exp4c_world_cache` (4 pre-built worlds:
`replicates_0`, `not_replicated_0`, `reversed_0`, `type_bound_0` —
gitignored scratch, not committed).

**`tests/mutation_check.py --worlds-only`** (new driver, `run_worlds_
only`): iterates `WORLD_ONLY_LABELS` (the 61 original minus 5 already
closed with fast tests during the SAME round — see below — leaving
56), applies each mutation alone, tries `totality` then `fullshape`
(or `battery -m slow` for the four battery-pin labels), restores, logs
KILLED/OPEN per label. Detached run (`nohup`-equivalent via a plain
background process, `ps aux | grep mutation_check` checked before/
after, nothing else touching exp4c meanwhile), logged verbatim to
`mutation_worlds.log` (committed). **Result: 56 considered, 11 killed
by the EXISTING totality/fullshape suite, 0 errors, 45 OPEN SURVIVORS**
— i.e. 45 of the 61 original labels had a real, uncaught defect no
existing test reached, exactly the "inferred, not executed" gap the
controller flagged.

**Closing the 45 (plus the 6 that were open even before this round's
`--worlds-only` run, since 4 of the "5 already closed" battery-pin
labels and one totality label were resolved with brand-new fast tests
in the SAME session before the 56-mutant batch — 5 there, 8 in total
across the whole 61 once the run-worlds-only batch's own survivors are
folded in):**

- **8 closed with brand-new FAST unit tests** (call the mutated
  function directly, hand-built inputs at the exact boundary the
  mutant moves — no world, no `run()`):
  - `test_battery_4c.py`: `test_check_rung_set_pins_4c_catches_a_
    clear_index_mismatch`, `test_manifests_4c_catches_the_69_grid_
    mismatch`, `test_manifests_4c_catches_a_missing_step0_entry` (3
    battery-pin-vs-real-data mutants — a monkeypatched `bh.load_
    manifest_69`/`bl.load_manifest_13b` pair, no real 2h/2l fetch
    needed for the corruption itself).
  - `test_analyze_4c.py`: `test_load_one_unit_refuses_an_n_hidden_
    pin_mismatch` (n_hidden=34 written, `sites`/`pairing` built from
    the PINNED 33 so only the n_hidden check itself fires);
    `test_gate0_4c_fails_between_half_and_the_bar` (9/14 kept sites
    below → fraction .643, strictly between .5 and the real .90 bar);
    `test_eligibility_4c_2se_bar_is_inclusive_at_the_boundary`
    (constant per-item alignments → x_end and 2·SE both EXACTLY 0.0,
    no floating-point tolerance needed).
  - `test_power_4c.py`: `test_interpolate_min_detectable_4c_bar_is_
    inclusive_at_the_crossing` (`[(1.0, 0.75)]` at bar 0.75 — `>=`
    returns 1.0, `>` returns `None`); `test_cell_structure_4c_catches_
    an_r_vs_clear_index_mismatch` (a trimmed `CLEAR_INDEX_PIN_4C`
    copy via monkeypatch).
- **40 closed with new `test_totality_4c.py` tests** (37 new test
  functions; 2 of them — `test_alignment_series_raising_gives_
  insufficient_data` and `test_per_item_alignment_raising_gives_
  insufficient_data` — each kill TWO labels with one unconditionally-
  raising fake, because the mutation harness only ever strips ONE of a
  function's two call sites at a time: whichever one is unprotected in
  a given mutant is the one that lets the raise through uncaught).
  Two patterns cover all 40:
  - **Hard-gate sites** (raise → `INSUFFICIENT_DATA`): `run()`'s
    TEST-ONLY kwarg injections (`frozen_check`, `discovery_check`)
    override directly; everything else is `monkeypatch.setattr` on the
    real module attribute `run()` calls unqualified or through its own
    `a4`/`rk`/`bt`/`bg`/`an2i`/`placebo_4b`/`mkr` aliases — the SAME
    module object `analyze_4c.py` holds, so patching it in the test
    reaches the call inside `run()`. Two are file-corruptions instead
    (a torn power record / gate-1 JSON payload; a halt-marker path
    turned into a directory so `.read_text()` raises
    `IsADirectoryError`). One (`run_the_reference_seal_s_own_failures_
    are_never_appended`) is the inverse: `require_seal_2i` returns
    CLEANLY with a non-empty `failures` list, proving `run()` itself
    appends them rather than dropping them silently.
  - **S4-continuity / secondaries / licence-block sites** (raise →
    the OUTER verdict is untouched, only ONE descriptive block
    degrades): `_sec`'s shared wrapper catches an S1-S10 secondary's
    raise without moving the top-level verdict off REPLICATES;
    `s4_continuity_4c`'s nine inner `collect_total_4c` calls (`a4.
    cells_4`, `a4.primary_4`, `a4.lambda_hat_4`, `placebo_4b.
    placebo_pool_4b`/`draw_batteries_4b`/`p_cal_4b`/`t_star_4b`/
    `alpha_placebo_4b`, `_design_4c`) each independently catch their
    own raise so the REST of the S4 dict keeps populating — a mutant
    stripping just one inner wrapper instead collapses the WHOLE S4
    block to `{"failed": [...]}`, which is the assertion each test
    checks (`"lambda_hat" in s4` etc., never merely the top verdict);
    `licence_block_4c` raising still returns the tree's real verdict
    with the documented default licence sentinel.

**Every one of the 45 open survivors (the 5 fast-suite-only + 40
totality-only) was individually re-confirmed this round** — its own
mutation applied alone, `pytest test_totality_4c.py -k <test_name>` (or
the fast-suite equivalent) run, source restored, repeated once per
label rather than trusted from the batch survey. `-k` narrowing
(rather than the full-file `-x` runs `--worlds-only`/`--totality` use)
turned confirmation from ~10-40 min/label into single-digit seconds to
tens of seconds each: **40/40 confirmed KILLED, 0 problems.** The 5
fast-suite ones were confirmed together via `mutation_check.py
--only=<the 5 labels>` (no `--totality`/`--fullshape`): 5/5 killed
directly by the fast suite.

**`KILLED_BY_WORLDS_ONLY` (the stale, never-executed 61-label set) is
GONE.** Replaced by `NON_FAST_KILLS_4C` — 53 entries, each `label:
"file.py::test_name"` naming the ACTUAL confirmed killing test (13
pre-existing kills from before this round + the 40 closed here); the
8 labels closed with brand-new FAST tests are documented in a comment
and simply absent from the dict, since `main()`'s default fast run now
kills them directly. `main()`'s special-case branch (for a label that
survives the FAST suite but is known to need the slow suite) now
prints the specific killing test from `NON_FAST_KILLS_4C` instead of
"confirmed by hand". Zero new EQUIVALENT mutants found this round —
`EQUIVALENT_MUTANTS` is unchanged (2 entries, both from before this
task). **Zero OPEN survivors remain.**

**Verification after all edits, in a fresh process / clean tree:**
fast suite green under `-W error` (108 passed, 4 deselected, 36.31 s —
the same 4 slow-marked `test_battery_4c.py` tests deselected as
before); `battery_4c.check_frozen_4c()` and `analyze_4c.
check_imports_4c()` both pass after importing `analyze_4c`, `power_
4c`, `make_referents_4c`, `verify_referents_4c`, `run.sweep_4c`, `run.
preflight_4c` — no source file drifted from its pin (only test files
changed, which are outside `FROZEN_SHA256_4C`/`IMPORTED_SHA256_4C` by
design); `read_sweep_4c.py` re-run: 8,093 distinct paths, 17,762
reads, **0 UNPINNED**, same buckets as fix round 1a, landing at "4c
gate 1 pythia_6.9b: record missing" after the discovery gate and power
record both ran; `verify_referents_4c.py` cold battery re-run: 10/12
ok, 2 skip (items 1 and 12, both still legitimate, unchanged); `git
status` clean of anything but the intended edits; no stray
`.mutation_backup`.

**Pre-tag real-tree executions this fix round: 2** (running total
9 -> 11), neither a new quantity: the `read_sweep_4c.py` and `verify_
referents_4c.py` re-runs above (both reproduce their fix-round-1a
numbers exactly). The totality/fullshape/fast suites' many `run()`
calls this round are ALL on synthetic worlds or in-memory fixtures,
never the real committed tree, so — consistent with fix round 1a's own
convention — they are not counted here.

**Wall-clock this fix round:** the `--worlds-only` batch (56 labels,
cached worlds) ran ~2-3 h detached; the 40-label `-k`-narrowed
confirmation pass ran a few minutes; fast-suite/pin/read-sweep/cold-
battery re-verification a few more minutes. Cache directory:
`/private/tmp/exp4c_world_cache` (gitignored scratch).

### Fix round 2 — five task-review findings (four Important, one promoted minor)

**1. The tally must reproduce from committed logs.** `mutation_build.
log`/`mutation_worlds.log` were snapshots from earlier states of the
source — 8 of `mutation_build.log`'s recorded survivors were already
fast-killed by fix round 1b's own new tests, and the "45 closures"
narrative lived only in PROGRESS.md prose, not in either committed
log. Fixed by making the CANDIDATE SET itself derived, not hand-
maintained: `WORLD_ONLY_LABELS = sorted(NON_FAST_KILLS_4C)` and
`WORLD_ONLY_BATTERY_PIN_LABELS = {"clear_index_pin_4c..."}` (the one
label whose recorded killer is `test_battery_4c.py -m slow`, not
totality/fullshape) — a future label can only enter `run_worlds_only`'s
survey by first being added to `NON_FAST_KILLS_4C`, so the two can
never drift apart again. Both logs regenerated from a clean tree by
re-running `main()`'s default (fast) pass and `--worlds-only`
detached, one at a time, nothing else touching exp4c meanwhile. The
stale pointer at the top of `mutation_check.py` (which named a
PROGRESS.md transcript with no committed record) now names the two
logs themselves as the reproducible record.

**2. Two kills were world-cache artifacts.**
`delta_of_mu_4c_the_sqrt_2_unit_normal_placement_factor_dropped` and
`power_bar_4c_the_declared_power_bar_75_5` were recorded as killed by
`test_control_untouched_copy_still_replicates` — but that test can
never observe a `power_4c` mutation on a FRESHLY BUILT world (the
world's own committed `power_4c.json` and the analyzer's re-derived
reproduction are written by the SAME `compute` call chain, so they
move together regardless of the mutation); they had only "died" because
the CACHED world's `power_4c.json` had been written by the unmutated
source before caching, and the mutated `power_4c.py` was never actually
exercised to build a NEW committed record. Fixed three ways: (a) two
direct pins in `test_power_4c.py` —
`test_delta_of_mu_4c_pins_the_sqrt2_unit_normal_placement_factor`
(`sqrt(2) * norm.ppf(0.76)` == 0.9988626635073269, not `norm.ppf(0.76)`
alone) and `test_power_bar_4c_pins_design_section_4s_bar`
(`POWER_BAR_4C == 0.75`) — both moved OUT of `NON_FAST_KILLS_4C`
entirely, now killed directly by the fast suite; (b) `WORLD_WRITING_
PATHS_4C` (`power_4c.py`, `battery_4c.py`, `collect_4c.py`, `tests/
full_shape_4c.py`) — the harness now FORCES `EXP4C_WORLD_CACHE=""`
(bypass, build fresh) for any mutant on this list, in both `run_worlds_
only` and `main()`'s own totality/fullshape loop, documented in both
the constant's own docstring and here; (c) the two labels re-recorded
under their new fast tests (visible in `mutation_build.log` as `killed`
directly, not `survived-fast, killed by the slow suite`).

**3. Cold battery item 1 skipped the frozen-pin check entirely.**
`verify_referents_4c.py`'s `_c1` returned `"SKIP"` whenever `bc.
FROZEN_SHA256_4C` was empty — but `bc.check_frozen_4c()` ALSO verifies
`battery_4.FROZEN_SHA256_4` (57 files) + `EXP4_CLOSED_SHA256_4C` (8) +
`EXP4B_CLOSED_SHA256_4C` (3) = 68 real, committed pins, entirely
independent of whether 4c's OWN residual table has anything in it yet.
Fixed: item 1 now ALWAYS calls `bc.check_frozen_4c()` and, only when
`FROZEN_SHA256_4C` is (still, legitimately) empty, prints "FROZEN_
SHA256_4C empty (covered by exp4/exp4b's own tables); 68 pinned files
verified" instead of skipping. The referent battery now reads 11/12 (+
1 legitimate skip, item 12 — 4c's own sweep hasn't run yet).

**4. The read sweep's bucket (f) absorbed 136 files its own docstring
never described.** Every one of the 136 `exp4_campaign_artifact`
entries was, verified directly, `experiments/exp4/results/reference/
<ref>/attested/<rung>.npz` — gitignored, untracked, absent from
`referents_4c.json`, read by `collect_4.load_ref_tables_4` with NO sha
check at all — while the docstring described the discovery gate's
OTHER inputs (`_load.json`, `sets/*.npz`, etc.), which never actually
reach this bucket (they're covered by `battery_4.FROZEN_SHA256_4`
before the classifier ever sees them). Fixed two ways: (a) a new named
bucket `exp4_reference_attested_unhashed` carries exactly these 136
paths, with a printed disclosure line, and the docstring corrected —
bucket (f) `exp4_campaign_artifact` is now (correctly) EMPTY in this
pre-campaign sweep; (b) ADDITIVE in the analyzer: `_reference_attested_
sha_ok_4c(root4, ref, rec)` re-hashes a reference's `attested/<rung>
.npz` on disk against ITS OWN `_load.json` record's `attested_sha256
[rung]` — the reference-side counterpart to `_attested_question_end_
4c`, which already did this for the MODEL side. `s9_question_end_4c`
gained a `root4` parameter (threaded from `run()`, which already has
it) and now calls this check for every reference BEFORE trusting its
`sets_question_end`; on any absence or mismatch S9 reads `available:
False` with the check's own reason. Two new fast tests in `test_
analyze_4c.py`: `test_reference_attested_sha_ok_4c_catches_a_tampered_
file` (a 2-rung fake universe — absent, then tampered, then matching)
and `test_s9_question_end_4c_reads_unavailable_on_a_reference_attested_
mismatch` (the integration point, via monkeypatch). Read sweep re-run:
`exp4_reference_attested_unhashed` 136, `exp4_campaign_artifact` 0, 0
UNPINNED — identical landing point and every other bucket unchanged.

**5. "Byte for byte" compared restricted key sets.**
`analyze_4c._reproduce_power_4c` (line ~1567) and `verify_referents_
4c.py`'s item 11 (`_c11`, line ~203) both built the comparison string
as `{k: power[k] for k in rec2 if k in power}` — a key present in the
COMMITTED record but ABSENT from `compute`'s live output (or vice
versa) would be silently dropped from one side before the string
comparison ever ran, passing a genuine drift as byte-identical. Fixed
in both places: `set(power) == set(rec2)` asserted first, naming the
extra/missing keys, before the byte comparison. Four new fast tests:
`test_analyzer_reproduction_catches_an_extra_committed_key`/`_a_
missing_committed_key` in `test_power_4c.py` (targets `_reproduce_
power_4c` directly) and `test_c11_catches_an_extra_key_in_the_
committed_power_record`/`_a_missing_key_in_the_committed_power_record`
in the new `test_verify_referents_4c.py` (targets `_c11` via a `vr.
EXP4C` monkeypatch to a `tmp_path`, since `_c11` hard-codes its own
results path) — plus `test_c11_skips_when_no_power_record_is_on_disk`
for the pre-existing SKIP route. `test_verify_referents_4c.py` added to
`FAST_TESTS`.

**Import pin drift (same class as fix round 1a, caught before commit
this time):** editing `verify_referents_4c.py` (items 3 and 5) moved
its sha, so `analyze_4c.check_imports_4c()` raised on a fresh-process
check. Caught by running that exact check BEFORE committing (the fix
round 1a lesson applied in advance) — re-ran `import_scan_4c.py`,
confirmed only `verify_referents_4c.py`'s sha moved (`a67ca232...` ->
`52aced84...`), pasted the fresh `IMPORTED_SHA256_4C` entry, re-
verified `check_frozen_4c()`/`check_imports_4c()` clean in a fresh
process.

**Verification after every edit, in a fresh process / clean tree:**
fast suite green under `-W error` (117 passed, 4 deselected, ~45 s —
was 108 after fix round 1b, +9 new tests: 2 S9, 2 delta_of_mu/
power_bar pins, 2 power-reproduction key-set, 3 in the new `test_
verify_referents_4c.py`); the FULL slow totality suite re-run in full
(53 passed, 1746 s) to confirm the S9 signature change and the
`WORLD_WRITING_PATHS_4C` cache-bypass mechanism introduced no
regression; `check_frozen_4c()`/`check_imports_4c()` both clean after
importing all six modules; read sweep re-run (0 UNPINNED, new bucket
present, landing point unchanged); cold battery re-run (11/12 + 1
legitimate skip); `git status` clean; no `.mutation_backup` anywhere.

**The two harness logs, regenerated from the CURRENT source on a clean
tree, detached (`Popen(start_new_session=True)`), one at a time:**
`mutation_build.log` (fast pass): **53 killed by the fast suite
directly; 51 killed by the slow suite (each individually reconfirmed);
2 documented equivalent; considered=106; 0 UNRESOLVED.** `mutation_
worlds.log` (`--worlds-only`, cached worlds, `WORLD_WRITING_PATHS_4C`
bypass active for the one battery-pin label that needed it):
**considered=51, killed=51, open_survivors=0, errors=0** — every
label's logged killer matches `NON_FAST_KILLS_4C` exactly. (53 fast +
51 non-fast + 2 equivalent = 106, matching `M`'s total; the 53/51 split
differs from this finding's own "51/53" description because finding
2's fix moves 2 mutants from non-fast to fast in the SAME round — the
pre-finding-2 state was 51 fast / 53 non-fast, exactly as described.)

**Wall-clock this fix round:** items 3-5's code/tests: under an hour.
The full slow-suite regression check: ~29 min. The fast mutation pass:
~2 runs (one before, one after the wording fix to the summary line
and `NON_FAST_KILLS_4C`/`WORLD_ONLY_LABELS` refactor), each a few
minutes. **The `--worlds-only` re-run: ~7.5 h** — each of the 51
labels applies its mutation alone and runs pytest with `-x` against
the FULL `test_totality_4c.py` (now 91 tests after fix rounds 1b/2);
`-x` stops at the first failure, so a label whose killing test sits
LATE in file order (most of fix round 1b's ~37 new tests, appended at
the end) costs nearly the full ~29-30 min baseline regardless of
caching (the cache only amortizes the one-time world BUILD, not each
test's own `run()` computation). No interruption was attempted mid-run
at any point (the apply/run/restore cycle has no externally-observable
safe window between mutants short enough to poll for, and interrupting
mid-mutation risks stranding a mutated source file — the same
constraint documented from earlier mutation-harness work this task).

## 2026-09-19 — Task 6: the adversarial freeze

Fresh-eyes reviewer, cold, on `experiments/exp4c/` at build HEAD
`d2cbc8fb8`. Zero model contact, zero network. Full record:
`experiments/exp4c/FREEZE_CHECKLIST.md`; report at
`.superpowers/sdd/2026-09-18-exp4c-build/task-6-report.md`.

**THE CLASS DEFECT WAS FOUND — F-1: `run/sweep_4c.py`, the producer of
every set table the verdict is read on, never pinned its own import
surface.** The analyzer pins it at entry and exit (2j F-1, lesson 11);
the runner checked only the seven instrument blobs and the frozen
upstream tables, and on its own import chain exactly two modules sit
outside every table it checks — `experiments/exp4c/__init__.py` and
`experiments/exp4c/run/__init__.py`, both covered only by
`IMPORTED_SHA256_4C`, which only the ANALYZER reads. A drift present
during the 45-hour sweep and reverted before the analyzer ran was
invisible on both sides. Demonstrated executably in two halves: two
lines in `experiments/exp4c/__init__.py` repointing
`collect_4.set_tables_4` passed the runner's whole refusal chain with NO
REFUSAL (the analyzer's own check raised on the same file); and on a
`replicates` world, randomising every rung's set table of ONE interior
13B checkpoint moved U from 1.0000 to 0.9487 with ZERO failures and gate
0 and gate 1 passing on both trajectories — an interior unit has no
comparator anywhere, and on `olmo2_13b` gate 1 compares two units the
same code wrote. Closed additively: the runner calls the analyzer's own
`check_imports_4c()`.

**Seven findings, every one closed additively; nothing preregistered
moved** (`ALPHA_4C`, `MARGINAL_4C`, `MIN_CLEAR_INDEX_4C`,
`CAL_MULTIPLE_4C`, `N_BOOT_4C`, `B_PLACEBO_4C`, `SEED_4C`,
`EXCLUDED_SITES_4C`, `MAX_ENUMERATE_4C`, the family-block null, the
placebo's construction, the tree, the modifier rule, §5's statistics and
`results/power_4c.json` are byte-identical to the build's):

- **F-1** the runner's unpinned import surface (THE CLASS DEFECT).
- **F-2** the power record's cell structure was compared only to a
  second re-derivation from the same pins, never to the cells the
  verdict is read on (3d's lesson) — `power_structure_failures_4c`
  added as a `collect_total_4c` site; not reachable through the real
  producer, stated that way.
- **F-3** gate 1's comparator is answerable COLD and nothing answered it
  until ~40 min of shard streaming — `gate1_comparator_failures_4c`,
  called by the runner before any loader is built, plus cold-battery
  item 13; the checkpoint identity is reported, not refused, so
  `run_gate1`'s own halt route is not pre-empted. Measured today:
  6.9b's ladder comparator is digest-equal and pin-equal.
- **F-4** the world cache was keyed on `(mode, seed)` alone, so a freeze
  closure could silently invalidate its own verification — the four
  world-writing modules' content now enters the key.
- **F-5** three S4-only inputs append to `failures` and would deliver
  INSUFFICIENT_DATA for the whole experiment; not independently
  reachable, DISCLOSED in `run()`'s docstring, routing handed up (R-3)
  because narrowing a refusal is not an additive closure.
- **F-6** the design doc's discovery literals were asserted five-of-many
  and the pins were checked only against themselves — the rest of
  §3.7(1)'s list now asserted, in the slow test and in a new fast one.
- **F-7** the NOT-REPLICATED licence sentence quotes §4's DESIGN-STAGE
  "two times in three" while the committed, tag-bound power record makes
  it .7312 — 4b F-3's class against the record rather than the data, and
  NOT-REPLICATED is the modal world by the record's own numbers. The
  sentence is not rewritten (R-1); the analyzer checks it and prints the
  record's figure.

**Batteries after the closures** (every cold tool re-run last, in a
fresh process, `IMPORTED_SHA256_4C` re-cut once for item 13): fast
suite **153 passed**; cold referent battery **12/13** + 1 legitimate
skip; import scan 5 residual modules, `scan == committed pins: True`;
read sweep 8,093 distinct paths, **0 UNPINNED**, 0 writes; slow suite
**80 passed, 0 failed** (totality 55, full-shape 24, determinism 1) in
50 min; mutation fast pass **113 considered — 59 fast-killed, 52
slow-killed, 2 equivalent, 0 UNRESOLVED**. The five world modes were
rebuilt from scratch under F-4's new cache key and reach **all three
modifier cells** (TYPE-GENERAL, TYPE-BOUND, NEITHER) and the REVERSED
sub-cell through the production path; `calibration.bounded` is False in
all five because at the worlds' `B = 200` four of them land on
α₀₁ = 0.02 = 2 × 0.01 **exactly**, one placebo battery short of a
strict `>` — the campaign runs at B = 10,000 where no such tie exists
(carried item 3, handed up as R-4).

**Pre-tag executions of `analyze_4c.run()` / a statistic-computing tool
against the REAL tree this session: 7** (running total 11 → 18), none a
new quantity on the two runs 4c exists to read:

1. the baseline cold battery (`verify_referents_4c`) — item 10 printed
   the KNOWN discovery `U=0.6224 over 42 cells, family p=0.03906`, item
   11 the power declaration; 11/12 + 1 legitimate skip.
2. the baseline import scan — `INSUFFICIENT_DATA — 4c gate 1
   pythia_6.9b: record missing`; 0 frozen + 5 residual modules,
   byte-identical to the committed pins.
3. the slow discovery test re-run after F-6's added literals —
   `discovery_set_4c()` on Exp 4's committed tree, the same pinned
   numbers, 106 s.
4. the read sweep after F-1..F-4 — 8,093 distinct paths, **0
   UNPINNED**, same landing point, 136 files in the named (h) attested
   bucket.
5. the read sweep again with every closure in place — the same table
   byte for byte (neither F-6 nor F-7 adds a file read).
6. the post-closure cold battery — 12/13 + 1 legitimate skip; item 13
   printed `pythia_6.9b: exp4/ladder_pythia_6.9b digest_equal, pins
   equal`.
7. the post-closure import scan — `scan == committed pins: True`.

Everything else this session ran on synthetic worlds under the session
scratchpad; worlds on tmp trees do not count.

---

## Final-review fix wave (2026-09-20, ONE dispatch, base `9615ff93c`)

The final whole-branch review read READY WITH FIXES — 0 Critical, 2
Important, the rest minors triaged. The controller's ruling dispatched
ONE fix wave: I-1, I-2 and the minors the review marked FIX or that are
one line on a gate. Everything below is ADDITIVE — a refusal, a record
field, a test, a descriptive. No preregistered bar, statistic, null,
tree or modifier rule was touched; `results/power_4c.json` is
byte-identical to `9615ff93c`; the frozen directories (`exp2*`,
`exp3*`, `exp4/`, `exp4b/`) were not edited. Zero model contact, zero
network.

**I-1 — the bare assert on the verdict path.** `_reproduce_power_4c`
compared the committed power record's key SET against `power_4c.
compute`'s live output with a bare `assert`, and `AssertionError` is
deliberately NOT in `collect_total_4c`'s caught set (widening it there
would launder logic defects as refusals). So a post-tag key drift in
`power_4c.py` RAISED out of `run()` instead of arriving as
INSUFFICIENT_DATA. It now RETURNS `{"identical": False, "first_diff":
"key set mismatch: extra [...], missing [...]"}` and travels the
existing "not reproduced byte for byte" failure. `collect_total_4c` was
NOT widened. The cold tool (`verify_referents_4c._c11`) keeps its
assert — a cold tool's raise IS its failure mode. Two existing fast
tests in `test_power_4c.py` asserted the RAISE and were updated to
assert the returned shape.

**I-2 — design §5 S4's "per-run nulls".** §5 S4 names "φ, T,
eligibility, λ̂ and 4b's p_cal, T\*, α_placebo **and per-run nulls** on
the two new runs"; the build computed all but the last and discarded
`batteries["per_traj_mean"]`. `s4_continuity_4c` now calls
`placebo_4b.per_traj_4b(batteries, design, primary["per_traj"])` under
its own `collect_total_4c` site, inside the existing `if batteries is
not None:` block, under the block's `no_alpha_claim`. A refusal
degrades S4 alone.

**Cold battery item 12, per trajectory.** The SKIP was decided from
`TRAJECTORIES_4C[0]` alone and then BOTH trajectories were looped — so
between the two sweeps (6.9b complete, 13B not) the item would have
reported a gate-0 FAILURE for a run that had not been collected at
all. The skip is now decided per trajectory (`"<traj> SKIP (sweep not
run)"`), the item passes when every trajectory present passes, and it
SKIPs outright only while neither is on disk.

**Cold battery item 6, pairwise-distinct digests.** Readable-and-64-hex
is not enough: a unit copied from one step to another carries a digest
that matches its own record and passes every pin in the analyzer. The
40 committed digests must be pairwise distinct; duplicates are named.
**On the real tree they are distinct** — the item passed this run.

**S9's unit side reads `available: False`.** The docstring promised it;
the code let `_attested_question_end_4c` raise and `_sec` landed
`{"failed": ...}` — a different shape from the reference side's, for
the same gitignored-artifact cause. A missing or sha-mismatched
`attested/<rung>.npz` on the MODEL side now reads unavailable with the
rung/path in `reason`.

**One collect site around the verdict write.** The two writes sat
outside every collect site: an unwritable `results/` raised out of
`run()` AFTER the whole computation. The block is collected — an
`OSError` lands in the returned verdict as `write_failure` and the
in-memory verdict is still returned — and `VERDICT.txt` is RENDERED
before either write, so a rendering failure can never leave a
`verdict.json` on disk with no `VERDICT.txt` beside it. `write_failure`
is set only on failure, so on success the returned dict is byte-for-byte
the dict that was written. (`_git_sha_4c()` and `a4._jsonify_4(v)`
remain outside a collect site — named in the review, left as is: the
only way `_git_sha_4c` can raise is a missing `git` binary, and
`_jsonify_4` is pure. Disclosed, not closed.)

**`p_family_reason` self-checking.** The sentence beside
`nonarith["p_family"] = None` asserted, unconditionally, that the
family null "cannot resolve the .05 bar" — true at the 3 non-arithmetic
families design §3.5 expects (8 flips, finest p .125), FALSE at 5 or
more (32 flips, finest p .03125). `_p_family_reason_4c(n_fams)` now
conditions on `1 / 2**n_fams > MARGINAL_4C` and says "the refusal is
categorical by design §3.5" in the other branch. The REFUSAL itself
stays unconditional; the statistic and the modifier rule are untouched.

**A per-trajectory stack-consistency descriptive.** `stack_consistency_
4c` prints, per trajectory, the DISTINCT `stack` blocks (numpy / torch
/ transformers) across every grid unit, that run's own step 0 and — on
the trajectory whose gate-1 comparator is 4c's own thin endpoint — that
endpoint's record. Gate 1's whole claim is byte identity of `.npz`
files, and what writes those bytes is numpy's zip writer on top of
torch and transformers; a campaign spanning a library upgrade would
pass every pin in this analyzer and the reader would have no way to see
it. Under `secondaries["stack_consistency"]`, `no_alpha_claim`, never a
refusal.

### The batteries after the wave

| battery | at the freeze (`9615ff93c`) | after the wave |
| --- | --- | --- |
| fast suite (`-m "not slow" -W error`) | 153 passed | **175 passed**, 90 deselected, 45.6 s |
| slow: `test_full_shape_4c.py` | 24 | **26 passed**, 1,207.7 s (0:20:07) |
| slow: totality S4/S9/power subset (`-k "s4_ or s9 or power_record or control_untouched"`) | — | **20 passed**, 39 deselected, 1,060.3 s (0:17:40) |
| cold referent battery | 12/13 + 1 skip | **12/13** + 1 legitimate skip (item 12, pre-campaign, now SKIPping because NEITHER run is on disk) |
| import scan | 5 residual, byte-identical | 5 residual; `verify_referents_4c.py`'s sha moved, **`IMPORTED_SHA256_4C` re-cut a FOURTH time, LAST** |
| mutation | 113 considered — 59 fast / 52 slow / 2 equivalent / 0 unresolved | **115 considered — 60 fast / 53 slow / 2 equivalent / 0 UNRESOLVED** (`mutation_fixwave.log`) |
| pins in a fresh process | OK | `check_frozen_4c()` OK, `check_imports_4c()` OK after importing all nine exp4c modules |
| `results/power_4c.json` | — | **byte-identical to `9615ff93c`** |

**The mutation tally moved by TWO, not one.** The review's dispatch
anticipated 114 considered (one new `collect_total_4c` site, S4's
per-run nulls). Item 6 — the verdict write — adds a SECOND site, so the
AST walker generates two new totality mutants, not one:

- `totality_02e3a8ac32` (the verdict write) — **killed by the FAST
  suite**, by `test_an_unwritable_results_dir_lands_as_write_failure_
  not_a_raise`; it needs no `NON_FAST_KILLS_4C` entry.
- `totality_54171f1735` (S4's per-run nulls) — killed by the slow
  suite; entered in `NON_FAST_KILLS_4C` against
  `test_s4_per_traj_4b_raising_collapses_only_s4`.

**A finding about the harness, not the instrument.** The targeted
`--worlds-only --only=totality_54171f1735` run reported the kill
against a DIFFERENT test — `test_s4_p_cal_4b_raising_collapses_only_s4`
— because `run_worlds_only` runs `pytest -x` over the whole totality
file and logs the FIRST failure, and with the per-traj site stripped
`per_traj_4b` calls `p_cal_4b` internally, so the earlier test's
monkeypatch already escapes `run()`. The kill is real either way, but
the table entry names the test written FOR the site, so that test was
confirmed DIRECTLY (mutate → run only that test → restore → assert the
source came back byte-for-byte): baseline rc=0, mutated rc=1, killed.
Both transcripts are in `mutation_fixwave.log`. This is R-8's
`--only-named-test` item showing its edge, one wave later; the
committed logs from the freeze (`freeze_mutation_fast.log`,
`mutation_worlds.log`, `mutation_build.log`) were left exactly as they
were.

**Pre-tag executions of `analyze_4c.run()` / a statistic-computing tool
against the REAL tree this wave: 2** (running total **18 → 20**),
neither a new quantity on the two runs 4c exists to read:

19. **the import scan** (`tests/import_scan_4c.py`, which runs
    `analyze_4c.run()` on the real pre-campaign tree) — `INSUFFICIENT_
    DATA — 4c gate 1 pythia_6.9b: record missing`; 0 frozen + 5
    exp4c-own residual modules, one sha moved
    (`verify_referents_4c.py`), re-pasted into `IMPORTED_SHA256_4C`.
20. **the cold referent battery** — **12/13** + 1 legitimate skip; item
    6 printed the new distinct check passing on the real 40 digests,
    item 10 the same KNOWN `discovery U=0.6224 over 42 cells, family
    p=0.03906`, item 11 `DECLARED UNDERPOWERED IN ADVANCE`, item 12
    `skip ... (not yet applicable)`, item 13 `pythia_6.9b: exp4/ladder_
    pythia_6.9b digest_equal, pins equal; olmo2_13b: exp4c/endpoint_
    olmo2_13b not written yet (this run's own)`.

The read sweep was NOT re-run this wave: no closure adds or removes a
file read (the write block's two paths were already opened by the same
code, and the new descriptive reads a `_load.json` the analyzer's own
loaders already read). Worlds on tmp trees do not count.

No `.mutation_backup` anywhere under `experiments/exp4c` at the end;
the working tree is clean apart from the wave's own files.

## 2026-09-20 — RATIFIED ("Ratified — apply the slips and tag"); slips applied; tag cut

Michael's word after the package: every item ratified as recommended. Slips applied verbatim to `experiment-4c-design.md`: the status line; §2 gains the nine discovery family sums (R-2b) and the pre-tag execution count (R-9: 20 at the package, 21 with the cold battery run after the slips — below); §3.1 the 41-hidden-state site pin (B-4); §3.2 the no-real-cell-at-index-2 sentence (R-6b); §3.6 the record's realized α and the BOUNDED-unreached disclosure (R-1, R-4); §3.7 gate 4's two paths per run — Exp 4's ladder writer on 6.9b, the thin endpoint on 13B, one writer (B-1, R-6a); §3.8 the S4-only inputs on the refusal path (R-3); §3.9 both positions committed with the measured cost, the wrapper (B-2, B-5, R-10); §4 the built power table, the declaration's figures and "three times in four (.73 on the record)" (R-1); §6 the quoted sentence and S9's machine-local reference side (R-1, R-11 = accepted as machine-local, disclosed); §7 the 13B thin endpoint in the run plan (B-1); §11 Exp 4's stale-tree disclosure and the build's process notes (R-5, R-8). The analyzer's NOT-REPLICATED body carries the same literal (`POWER_MISS_LITERAL_4C = 0.73125`, the record's own figure); the F-7 check stays and now guards a future divergence — its two tests inverted accordingly (silent on the committed record; fires on a stand-in with P_05 .5). Fast suite 175/175 after the edits.

Cold battery re-run after the slips (a counted pre-tag execution, the 21st): the line above this entry's commit records what it printed (12/13 + the gate-0 skip). `check_frozen_4c` and `check_imports_4c` pass in a fresh process after importing every exp4c module (analyze_4c is a tag-bound blob, not an IMPORTED pin, so the literal change moves no pin).

**Tag `exp4c-preregistered` cut at this commit** (annotated; blob-bound over analyze_4c.py, battery_4c.py, rank_4c.py, collect_4c.py, power_4c.py, run/sweep_4c.py and results/power_4c.json), binding verified through `require_prereg_4c` against real git, pushed with the commit. Next, on his word: the projection (dial m), then the preflight.

## 2026-09-20 — PREFLIGHT launched (pre-clear); STALL #1 environment-side; relaunched with the xet client disabled

The preflight (`python -m experiments.exp4c.run.preflight_4c --device mps`, pid 59958, detached, ppid 1) was running from 06:17 when this session picked the tree up after a `/clear`; its launch is not ledgered above (the pre-clear session's entry did not land). At 09:10 it had been inside the OLMo-2 13B step-1000 download the whole time: 7 of 12 shards complete (34.2 of 54.9 GB), the eighth shard's `.incomplete` blob frozen at 4.43 GB since 08:21 (50 min, +0 bytes over a 10 s sample), process at 0 % CPU, `preflight.log` holding only the thread-pin line. The `hf_xet` transfer log (`~/.cache/huggingface/xet/logs/xet_20260920T061716896-0400_59958.log`) ends at 12:48:05Z (08:48 local) on `Retry on 403 (Forbidden) ... s3::get_range ... retry 2` after `Retrieval URLs refreshed successfully` — a signed-URL expiry the client retried and then hung on; 20 earlier `Request error` WARNs at 10:22Z had recovered. Environment-side (hf-xet 1.5.1 / huggingface_hub 1.22.0), the class of 2i's and 2l's stops. The preflight writes nothing under `results/` (prints only, asserts the tree unchanged), so no frozen artifact is touched and nothing is un-ledgered.

Recovery on Michael's word ("go", 09:13): pid 59958 killed (TERM, exited clean); the partial shard `2bf22063…c7414412.incomplete` (4.43 GB) and its `.lock` removed — a partial written by the parallel-range client is not a contiguous prefix, so it must not be resumed by the plain downloader; the seven verified shards kept. `preflight.log` rotated to `preflight.stall1.log`. Relaunched 09:14:30 as pid 81364 via `Popen(start_new_session=True)` from the venv with `HF_HUB_DISABLE_XET=1` (the plain resumable HTTP downloader; no xet log open on the new process), stdout+stderr to `preflight.log`, pid in `preflight.pid`. After 25 s the shard was at 0.39 GB and growing. Memory 92 % free; the three mlx services resident but idle (< 0.1 GB each), left up for this single 27 GB load — 2l's text-server-down arrangement applies at the 13B sweep, not here. Watchdog (session Monitor) armed on the new pid: exit, log progress, download stall.

## 2026-09-20 — PREFLIGHT complete (fp16): 13B step 1000 NON-FINITE on both rungs; AMENDMENT (the pre-committed change, SPENT): the 13B forward moves to bfloat16; batteries; re-tag

**The preflight's reading (relaunched run, pid 81364, `preflight.fp16.log`).** `olmo2_13b step1000`: sites 15 == pin, digest `e45d7d39…` == committed → True; `antonym` 185.1 s **finite=False**, `add3_mid` 95.6 s **finite=False**, peak MPS 36.5 GB (not memory — the load and both collections completed with the right shapes); released and freed. `pythia_6.9b step1000`: digest `ae068890…` == committed → True; `antonym` 199.8 s finite=True, `add3_mid` 44.7 s finite=True (peak 41.9 GB with the 13B's driver allocation still cached). `complete: nothing written under results/`. Corroboration on committed bytes (2l's sweep records, no model contact): the share of rungs whose 500 continuations ALL begin with "!" is 34/34 at steps 1000, 2000 and 4000, 33/34 at 8000, 0/34 from 16000 on — greedy decoding over NaN logits; the fp16 forward of this model overflows at those checkpoints. Consequence under the frozen instrument: `metric_4.knn_sets` refuses non-finite rows and `process_model_4c` has no catch around `set_tables_4`, so the first 13B grid point after gate 1 would have crashed the sweep (no halt marker, every relaunch the same), and the statistic's t_1 is step 1000 — the 13B run could not have produced its own baseline; six of its eighteen cells (clear index 4) read their rank at step 8000 besides. Reported to Michael with three options (A: bf16 forward; B: drop the four early points, t_1 := 16000, losing 8 of 18 cells; D: 6.9b only); **RULED "Okay, make the change to bf16" (11:0x).**

**The amendment (code), test-first.** `battery_4c.py`: `FORWARD_DTYPE_4C` (pythia float16; olmo2_13b and the thin endpoint bfloat16), `X_DTYPE_4C` (pythia float16; olmo2 float32), `dtype_key_4c`, `cast_forward_4c(model, key, *, torch_mod=None)` — cast only when the forward dtype differs from `DTYPE_4C`, the result READ BACK from the model object and refused if it is not the pin; `load_step_4c`/`load_thin_endpoint_4c` cast AFTER `tensor_digest` (so the identity digest against 2l's committed one is unchanged — the preflight had just shown it equal) and record `info["forward_dtype"]`/`info["load_dtype"]`; `expected_fields_4c` and `load_record_failures_4c` carry and require `forward_dtype`/`x_dtype`/`load_dtype`. `DTYPE_4C` itself unchanged (the load dtype; the outcome records' pin). `collect_4c.py`: `collect_rung_4c_fp32` (the frozen collector's body without its fp16 storage casts; `collect_4`'s helpers by name), `collect_rung_for_4c` (float16 keys → the FROZEN `collect_4.collect_rung_4` object itself; float32 keys → the fp32 variant; the returned X dtype asserted), `process_model_4c` refuses a loader `info` whose forward dtype is not the pin before any forward pass and records the MEASURED `x_dtype`, `stamp_dtypes_4c` writes the three fields onto `_load.json` after the frozen writer returns (`battery_4.load_record_4` copies a fixed key set). `run/preflight_4c.py`: the same dispatch; prints `forward_dtype`/`x_dtype`. Tests: 9 new (`test_battery_4c`: pins cover every key and keep the load dtype; the cast is a no-op object for pythia and a measured cast for olmo; a model that does not land on the pin is refused; expected fields + record failures for missing/wrong/pre-amendment values. `test_collect_4c`: the fp32 collector equals the frozen one after an fp16 cast; stays finite where fp16 storage overflows (×1e5 activations — the frozen path goes inf); the dispatch by key; `process_model_4c` records the measured dtypes and refuses a mismatch or a missing field, nothing written. `test_analyze_4c`: a 13B unit stamped float16 is refused at load). Fixtures: `_info` and the stage tests' fake loaders carry what the real loaders now measure; `_write_unit_on_disk` and `full_shape_4c._write_synthetic_unit_4c` stamp the pins. `IMPORTED_SHA256_4C`: the preflight's sha re-pasted (`31cffdd3…` → `4c9956ed…`). Not touched: `rank_4c.py`, `power_4c.py`, `run/sweep_4c.py`, `results/power_4c.json`, every frozen upstream module.

**Batteries after the amendment.** Fast suite `pytest experiments/exp4c/tests -m "not slow"`: **184 passed** (175 + 9). Slow: `test_full_shape_4c` + `test_totality_4c` + `test_determinism_4c` **86 passed** (1 h 23 min; an earlier pass errored 83× on a missing `c4c` import in the synthetic writer, fixed). Cold battery `verify_referents_4c`: **12/13 + the gate-0 skip** (item 10 the KNOWN discovery U .6224 / p .03906; item 11 DECLARED UNDERPOWERED IN ADVANCE; item 13 the comparator cold). Read sweep: **UNPINNED 0** (136 reference attested files disclosed as before). Import scan: the table reproduced with the preflight's new sha, `analyze_4c.run()` on the real tree → INSUFFICIENT_DATA (the 22nd pre-tag execution; §2). The three cold tools were run AGAIN after the upcast fix below — 12/13, UNPINNED 0, the scan's run INSUFFICIENT_DATA (the 23rd). Mutation: **8 amendment mutants, 8 killed by the fast suite** (`mutation_amendment.log`, labels `amendment_*`: the cast skipped; its refusal dropped; the 13B pin flipped back to float16; the record contract blind to forward_dtype; float32 keys routed to the fp16 collector; the per-load refusal dropped; the stamp writing a constant; the fp32 collector storing fp16), 0 survivors, sources restored, no `.mutation_backup`.

**The bf16 rehearsal, first attempt (pid 6080, `preflight.bf16crash.log`): a defect in the amendment, caught by the rehearsal.** The 13B checkpoint re-downloaded (55 GB, plain downloader, ≈ 45 min), sites 15 == pin, digest `e45d7d39…` == committed (the cast is after the digest — the identity pin held under the amendment), then `TypeError: Got unsupported ScalarType BFloat16` inside `collect_rung_4c_fp32` at the frozen `collect_4._to_numpy` — numpy has no bfloat16, so a bf16 forward's hidden states cannot cross to the host as they are. That the crash was there says the cast took and the forward ran in bf16. The preflight's `finally` freed the checkpoint on the exception path. Fixed test-first: `test_fp32_collector_upcasts_bf16_hidden_states_before_numpy` (a torch-backed stub whose hidden states are bf16 with values beyond fp16's range; the frozen collector raises `TypeError` on them; the fp32 collector must return finite float32 with the > 65,504 values kept) failed on the code as written, then `_to_f32_numpy_4c` (a bf16 tensor is `.float()`ed ON THE TENSOR SIDE, then the frozen helper, then float32) made it pass. Fast suite **185 passed**; a ninth amendment mutant (the bf16 branch dropped) **killed** (`mutation_amendment.log`, 9/9); sources restored. No slow test executes the collector paths (the synthetic writer bypasses them; grep in the ledger's own record), so the 86-passed slow run stands for this helper. Second attempt launched 12:13:07 as pid 13015, narrowed to the 13B unit — `preflight_4c.run(device="mps", units=(("olmo2_13b", 1000),))` from a launcher (the 6.9b half passed this morning under the unchanged Pythia path) — same code path, same `results/` snapshot assertion, `HF_HUB_DISABLE_XET=1`, the third 55 GB download of the day.

**The bf16 rehearsal, second attempt (pid 13015, `preflight.log`): PASS.** 13B step 1000: sites 15 == pin, digest `e45d7d39…` == committed → True; **`antonym` 162.4 s finite=True forward_dtype=bfloat16 x_dtype=float32**, **`add3_mid` 96.3 s finite=True forward_dtype=bfloat16 x_dtype=float32**, shape (500, 15, 2, 5120), peak MPS 35.3 GB (fp16's run peaked at 36.5); released and freed; `complete: nothing written under results/`. The fp16 forward's non-finiteness on this checkpoint (both rungs, this morning) is gone under the amendment with the identity pin held. Model contact today, all preflight: fp16 13B step 1000 ×1 (+ one stalled download), fp16 6.9b step 1000 ×1, bf16 13B step 1000 ×2 (one crashed before any collection returned); every load freed; nothing written under `results/`.

**Design doc.** Status line; §2 the amendment paragraph (finding, corroboration, consequence, ruling, what is unchanged, what moved, the mantissa disclosure, the rehearsal as the amendment's known-answer gate); §3.1; §7; §10 (o) SPENT; §11 two process notes (a dtype is part of the representation's validity range — the same committed bytes read as texture for an emission count and as no reading at all for a representation; a preflight should print finiteness per site). The projection (`25361b9ef`, sealed after the original tag) stands: the amendment touches no statistic, cell, grid, pin on the outcome, or power input.

**Environment-side, same day (ledgered above):** the first preflight run stalled in `hf_xet` and was relaunched with `HF_HUB_DISABLE_XET=1`; the A100 benchmark (`tools/vast_bench/`) ran in parallel on a rented box — unrelated to 4c, recorded there.

**RE-TAG.** On Michael's word ("cut the tag when you're ready"): `exp4c-preregistered` re-cut at the amendment commit (annotated, the original message carried forward with the amendment appended; previous object at `60a7492bb500`), binding verified through `require_prereg_4c` against real git, pushed with the commit. The projection `25361b9ef` stands. The 6.9b sweep is next, on his word.

## 2026-09-20 — 6.9b SWEEP LAUNCHED on Michael's word ("Go on the 6.9b sweep.")

Dry run first (`--dry-run`: prereg tag 'exp4c-preregistered' verified against the re-cut tag; thin endpoint n/a for 6.9b; gate 1 pythia_6.9b pending; 22 units), tree clean, no HALTED marker, `results/` holding only `power_4c.json`. Launched 2026-09-20 14:17:52 as pid 29417: `python -m experiments.exp4c.run.sweep_4c --traj pythia_6.9b --device mps` via `Popen(start_new_session=True)` from the venv, `HF_HUB_DISABLE_XET=1` (the plain downloader, after this morning's hf_xet hang), stdout+stderr to `sweep_pythia_6.9b.log` (gitignored by name), pid in `sweep_pythia_6.9b.pid`. Gate 1 (the endpoint against Exp 4's committed `ladder_pythia_6.9b` table, two loader paths) runs first; then step 0 and the 22-point grid; every unit watcher-committed (`run/commit_watcher_4c.sh`, started after this entry's commit). mlx servers up (Exp 4 ran 7B with them up). Disk 541 GB free at launch. Session watch: unit completions, HALTED, tracebacks, exit.

**Gate 1 pythia_6.9b: PASS** (logged by the runner at the endpoint unit's close: 34 rungs, digest equal, 0 byte diffs vs `exp4/ladder_pythia_6.9b` — the seventeenth byte-identical reproduction on this stack, the first through the amended instrument, the Pythia path being the frozen one). Step 0 and the 22-point grid follow; the watcher is committing every file as it lands.

## 2026-09-21 — 6.9b SWEEP COMPLETE (checked on Michael's word, "Check back on it.")

`[4c sweep] pythia_6.9b: complete` logged after the step140000 unit closed at 10:18 (2026-09-21); the runner exited on its own. Twenty-three loads in grid order — gate 1's endpoint unit (step143000, PASS 15:08), step 0, then the twenty-one remaining grid points 1000 → 140000 — 20 h 0 min wall from the 14:17:52 launch. Per-unit compute 2,604–2,646 s (the runner's own `done in` figures; step130000 the slowest at 2,646 s); wall per unit ≈ 49–57 min, the difference being the 13.8 GB stream per checkpoint (faster overnight than in the evening). **Zero halts** (no `HALTED` anywhere under `results/`), zero tracebacks in `sweep_pythia_6.9b.log`, zero experiment-side stops, zero environment-side kills — the first 4-series sweep to run end to end without one. `forward_dtype` float16 on all 23 `_load.json` records (the frozen Pythia path; the bf16 amendment applies to `olmo2_13b` only). Every unit watcher-committed and pushed as it landed: 1,611 files (70 per unit — 34 `sets/`, 34 `attested/`, `_load.json`, `align.json`; 96 MB on disk; the per-unit `activations/` dropped by the runner once the unit closed), one commit per file, tree clean, `master == origin/master`. Disk 545 GB free.

The instrument's own reading of the tree: `--dry-run --traj pythia_6.9b` → "gate 1 pythia_6.9b done; would run 0 unit(s)". Not run on the complete tree: anything that prints U, a q, or a rank — the analyzer runs once on his word, and (2n's record) a read sweep on a complete tree is a disclosure event.

The watcher (pid 29448) is left up and idle: it watches `experiments/exp4c/results` as a whole, so it covers the 13B run without a relaunch.

**NEXT, on his word: the 13B sweep.** `--dry-run --traj olmo2_13b` reads "thin endpoint pending; gate 1 olmo2_13b pending; would run 16 unit(s)". Before launch, per 2l's arrangement: the mlx text server down (`launchctl bootout gui/501/com.mlx.text-server`, port 11436; the CodeAssist mlx-server on 11435 and mlx_vlm on 8080 are the other two residents — 2l took the text server down and restored it at close-out). The OLMo-2 13B cache entry (`models--allenai--OLMo-2-1124-13B`) holds the preflight's step-1000 revision; ≈ 55 GB streamed per grid point, ≈ 30 h under the bf16 amendment (`FORWARD_DTYPE_4C["olmo2_13b"]`), `HF_HUB_DISABLE_XET=1`, `Popen(start_new_session=True)`, the same watcher.

## 2026-09-21 — 13B SWEEP LAUNCHED on Michael's word ("Go on the 13B sweep.")

Pre-launch: tree clean at `6c8235b53`, `master == origin/master`, no `HALTED` under `results/`, 544 GB free, 41 GB of memory free; `--dry-run --traj olmo2_13b` (13:2x): "prereg tag 'exp4c-preregistered'; thin endpoint pending; gate 1 olmo2_13b pending; would run 16 unit(s)". The A100 question raised and answered the same hour (Michael: "Is it time to use the A100 yet?"): not for this sweep — the design's §7 names the Mac, the pre-committed change is spent, and the hidden-state collector has never run on CUDA (the benchmark exercised argmax and the sampler); the rank statistic and the 13B gate 1 are both within-run, so the reading would survive the switch, which is why it was a judgment call and not a blocker. Recorded here so the choice is on the record before any 13B byte exists.

**mlx text server down** per 2l's arrangement: `launchctl bootout gui/501/com.mlx.text-server` at 13:28 (launchctl printed "Bad request." and the service is gone: `launchctl print` → "Could not find service", nothing listening on 11436, no `mlx_lm.server` process). Left up: the CodeAssist mlx-server (11435) and `mlx_vlm` (8080), both idle, as at the preflight; an unrelated `vllm-mlx` serve process from another project (15 days up) also left alone. Restore at close-out: `launchctl bootstrap gui/501 ~/Library/LaunchAgents/com.mlx.text-server.plist`.

**Launched 2026-09-21 13:28:05 as pid 39594:** `python -m experiments.exp4c.run.sweep_4c --traj olmo2_13b --device mps` via `Popen(start_new_session=True)` from the venv, `HF_HUB_DISABLE_XET=1` (the plain downloader), stdout+stderr to `sweep_olmo2_13b.log` (gitignored by name), pid in `sweep_olmo2_13b.pid`. Order under the runner: the thin-loader endpoint unit (gate 1's second path, one extra ≈ 55 GB load), then gate 1 (the candidate-file endpoint against it — two loader paths through one writer, the check on the load), then the 16-point grid; the 13B forward in bfloat16 after the fp16 identity digest (the spent amendment), pooled activations fp32, every record's measured dtypes required against the pins. The watcher (pid 29448, up since the 6.9b launch) covers the tree. First minute: "Fetching 12 files", the cache growing at ≈ 90 MB/s (3.8 GB in 40 s) — the datacenter-side rate, not the 6.9b's. Session watch: the thin endpoint's close, gate 1's line, `HALTED`, tracebacks, exit.

## 2026-09-21 — 13B ATTEMPT 1 KILLED (memory thrash, environment-side), RELAUNCHED with the MPS allocator capped — on Michael's rulings

**What was seen.** The thin endpoint loaded at 13:39 (52 GB endpoint in the HF cache at ≈ 90 MB/s, weights 443/443) and then wrote nothing for 77 minutes against a rehearsal pace of ≈ 100–160 s per rung (a unit's files land in a burst at its close, so silence itself was expected until ≈ 14:40–15:10; the alarm came from the memory readings). At 14:01: GPU-resident memory 28.8 GB, swap 32.4/33.8 GB, 69 MB unused, `vllm-mlx serve Qwen3-Coder-30B-A3B-Instruct-4bit` (pid 71922, port 11437, hand-launched 2026-09-05 from `~/dotnetbench-serve`, idle, no clients) holding 21 GB of which 16 GB compressed, `com.mlx-vlm-server` (port 8080) 5.6 GB compressed. At 14:35: GPU-resident 14.4 GB, compressor 15 GB, compressions ≈ 230 MB/s + decompressions ≈ 350 MB/s + swap-out ≈ 96 MB/s over a 10 s window, the sweep's threads in `__psynch_cvwait`/`semaphore_wait_trap` (waiting on the GPU), zero process page-ins, GPU "utilization" 98 % — the forward passes being served through the compressor. **Ruling 1 (Michael, "Stop both for the run"):** vlm booted out 14:40 (`launchctl bootout gui/501/com.mlx-vlm-server`); vllm-mlx TERM, then KILL, reaped after ≈ 60 s of uninterruptible kernel teardown (`Us`). Settled reading at 14:45 with both gone: compressor 23 GB, GPU-resident 9.5 GB, ≈ 500 MB/s each way, 1.5 GB unused, the sweep process at 48 GB (6.8 GB of it compressed) — **not relieved: the frozen 13B unit's own footprint exceeds the box.** Arithmetic: bf16 weights 27.4 GB; the MPS allocator's pool at its rehearsal peak 35.3 GB (cache included); the per-unit activation bank `activations_by_rung[rung] = {"X": X, "P": P}` held for all 34 rungs until the unit's writer runs — at 13B in fp32 (`X_DTYPE_4C`, the amendment's storage dtype) 500 × 15 × 2 × 5120 × 4 B = 307 MB per rung, **10.4 GB per unit** (6.9b: 3.3 GB at fp16/4096); overhead ≈ 3 GB; ≈ 48 GB on a 52 GB machine. The two-rung preflight (peak 35.3 GB) could not show the bank; the design's "27 GB resident" was the weights alone. Process note for the retrospective: a preflight sized on the model's residency misses a per-unit bank that scales with rung count × storage dtype.

**Ruling 2 (Michael, "Kill, relaunch on the Mac with the MPS allocator capped" — the first try; the A100 named as the fallback, "Leave it running" declined).** Attempt 1 (pid 39594) TERM'd 14:49:03, exited clean: **0 files under `results/` newer than its log, no `HALTED`, tree clean at `ddb62c8cd`** — nothing scored, nothing to retract; the run's log rotated to `sweep_olmo2_13b.attempt1.log` (gitignore rule `experiments/exp4c/sweep_olmo2_13b.*.log` added). `com.mlx-embeddings.server` (CodeAssist, port 11435, 0.5 GB) booted out as well. Memory before relaunch: 8.7 GB used, 39 GB unused, compressor 55 MB. **Relaunched 14:49:33 as pid 53136**, the same command and detachment (`Popen(start_new_session=True)`, `HF_HUB_DISABLE_XET=1`), with `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.78` and `PYTORCH_MPS_LOW_WATERMARK_RATIO=0.7` in the environment (verified on the live process): torch's MPS pool capped at 0.78 × the 40.2 GB recommended maximum ≈ 31.4 GB and its cached free blocks released above 28 GB — the weights' 27.4 GB plus the per-batch transient fit under it. **What this touches: the allocator's ceiling and cache policy, not a number** — batch composition, dtypes, sites, code and pins are untouched; a cap set too low raises a torch OOM (a crash, no halt marker, a relaunch), never a different value. Expected footprint ≈ 45 GB: likely, not certain, to hold; the decisive reading is at the unit's close with the bank full. Check points: GPU residency and compressor rates ≈ 10 min after the load; the thin endpoint's close (≈ 60–90 min at the rehearsal pace); if the thrash returns, the A100 on his ruling. **Four services now down for the run — restore at close-out:** `launchctl bootstrap gui/501 ~/Library/LaunchAgents/com.mlx.text-server.plist`, `…/com.mlx-vlm-server.plist`, `…/com.mlx-embeddings.server.plist`; `cd ~/dotnetbench-serve && .venv/bin/python launch.py` (writes its own `server.pid`/`server.log`; original command line: `vllm-mlx serve mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit --served-model-name qwen3-coder-30b-a3b --host 0.0.0.0 --port 11437 --max-num-seqs 8 --continuous-batching --timeout 1800`). Campaign stops: none experiment-side; one environment-side kill (this one), tree-clean.

## 2026-09-21 — 13B ATTEMPT 2 CRASHED (torch MPS OOM under the cap) — the Mac cannot hold the frozen 13B unit

Attempt 2 (pid 53136, watermarks 0.78/0.7) died at ≈ 14:51 in the thin endpoint's first rungs: `RuntimeError: MPS backend out of memory (MPS allocated: 29.08 GiB, other allocations: 18.73 MiB, max allowed: 29.20 GiB). Tried to allocate 153.12 MiB` inside `collect_rung_4c_fp32` (`collect_4c.py:114`, via `process_model_4c` ← `_process` ← `run_thin_endpoint`). A crash, not a halt: **tree clean — 0 files under `results/`, no `HALTED`, git clean at `0c88d0379`**; nothing scored. The log stays as `sweep_olmo2_13b.log` (attempt 1's beside it).

**What the two attempts establish together.** The forward's working set on MPS is above 29.2 GiB (attempt 2) and peaked at 32.9 GiB in the bf16 rehearsal (`peak_mps_bytes` 35,344,220,160; the recommended maximum is 37.4 GiB, so a cap must be ≥ 0.88 to run at all); the per-unit fp32 bank is 10.4 GB and the overhead ≈ 3 GB. A cap that runs therefore lands the process at ≈ 49 GB on a 51.5 GB machine — attempt 1's regime, which thrashed (compressor 23 GB, GPU-resident 9.5 of 27 GB, ≈ 500 MB/s each way) even after every other resident was stopped. The two levers the environment offers — free memory, cap the pool — are exhausted; what remains changes either the host or the instrument. Not tried: `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` (no limit; the same thrash by construction). A missing 13B tree is a missing verdict input — the frozen analyzer delivers INSUFFICIENT_DATA (lesson 8) with the 6.9b tree as record only. **Options put to Michael:** (A) the A100 for the 13B trajectory — a ledgered host change, the thin endpoint as the CUDA rehearsal, gate 1 and the rank statistic within-run; (B) the Mac at cap 0.90 with nothing else resident — attempt 1's footprint, expected to thrash; (C) close 4c INSUFFICIENT_DATA on the 6.9b record, the 13B to a successor with the bank sized. Awaiting his ruling; nothing launched.

## 2026-09-21 — RULING 3 (Michael, "Rent a GPU for the 13B trajectory"): the 13B moves to a rented CUDA box — a HOST CHANGE, disclosed here before any 13B byte exists

**What is and is not changed.** The instrument is not: every tag-bound blob (`analyze_4c.py`, `battery_4c.py`, `collect_4c.py`, `rank_4c.py`, `power_4c.py`, `run/sweep_4c.py`, the battery), the statistic, cells, grid, pins, batch composition (`BATCH_4C` 16), dtypes (fp16 load → bf16 forward → fp32 bank, the spent amendment), the outcome records and the power record stay as tagged at `0a6c5ea83`; the runner takes `--device cuda` where it took `--device mps`, a parameter it has always had. The record contract (`expected_fields_4c`: family, render, batch, refs, n_hidden, committed_digest, the three dtypes) carries no device; each unit's `stack` block (torch/transformers/numpy — `stack_record_4`) will read the box's torch build (`2.12.1+cu130`-class) beside the Mac's `2.12.1`, and the analyzer's stack descriptive (S9-class, never a refusal) will show two blocks across trajectories and one within each — the disclosure the record carries by itself. Gate 1 on the 13B is two loader paths through one writer within the run (design §7 item 4), so it is intact on either host; the rank statistic q compares rising against flat tasks of the same run at the same checkpoint, so a host offset cancels within it; the reference side (Exp 4's committed set tables, three references) is read as committed bytes. **What a reader must know:** the 13B trajectory's set tables are CUDA-computed in bf16 against Mac-computed references, with no committed 13B referent to compare to — the same disclosure the bf16 amendment already made about rounding, one level over; S6 (six runs pooled) and S4 (continuity with 4b) pool a CUDA run with five MPS runs, disclosed wherever they are quoted. The design's §7 named the Mac as the host in its planning text; the tag binds code, not hosts; this entry is the record that the host was changed after the tag, why, and on whose word.

**Why.** Two attempts on the Mac today (above): attempt 1 thrashed through the compressor with every other resident stopped (the frozen 13B unit's footprint ≈ 48 GB: bf16 weights 27.4 GB, the MPS pool at its 32.9 GiB rehearsal peak, the 10.4 GB fp32 per-unit bank, ≈ 3 GB overhead — on a 51.5 GB machine); attempt 2 under an allocator cap OOM'd at 29.2 GiB inside the collector. A cap that runs (≥ 0.88) reproduces attempt 1. The environment's levers are exhausted; the alternatives put to Michael were the Mac at cap 0.90 (expected to thrash) and closing 4c INSUFFICIENT_DATA on the 6.9b record; he chose the host change.

**Plan (each step ledgered as it lands).** (1) Rent on Vast.ai on-demand: a 96 GB RTX PRO 6000 or an 80 GB A100 (the 40 GB A100 would leave ≈ 4–7 GiB of headroom over the rehearsal's 32.9 GiB peak — declined for the same reason we are here), ≥ 64 GB RAM, ≥ 200 GB disk, ≥ 500 Mbps, reliability > .97; image `vastai/pytorch`, ssh only, no Jupyter. (2) The repo reaches the box as a **git bundle** (`git bundle create … --all`, every ref and tag; no GitHub credential on the rented host — memory's rule: treat the host as untrusted, no tokens), cloned there and checked out at this ledger's commit so every `sweep_commit` names the commit that discloses the host; `require_prereg_4c` verifies the tag object and blob shas against the box's real git in the runner's own dry-run. (3) Copied beside it, the only gitignored inputs the 13B path reads: Exp 4's `attested/<rung>.npz` for the three references (`ref_pythia_12b`, `ref_smollm3_3b`, `ref_comma_7b`; 34 files each, ≈ 9 MB), sha-checked against their committed `_load.json` by `load_ref_tables_4` on load. (4) The Mac's stack pinned on the box: torch 2.12.1, transformers 5.13.0, numpy 2.4.6 (the `.npz` writer gate 1 rests on), safetensors 0.8.0, huggingface_hub 1.22.0, tokenizers 0.22.2, scipy 1.17.1; `HF_HUB_DISABLE_XET=1`. (5) `--dry-run --traj olmo2_13b --device cuda` must read "thin endpoint pending; gate 1 olmo2_13b pending; would run 16 unit(s)". (6) The sweep detached on the box (`nohup … &`, its own session); the thin endpoint is the CUDA rehearsal of the collector — digest must equal 2l's committed one, finiteness is the collector's own refusal. (7) Results return by `rsync` (excluding `activations/`) from the box into this tree every few minutes, where the standing watcher commits them as it has all day; the box holds nothing the tree does not. (8) Destroy the instance on Michael's word after the last unit is on the Mac and verified.

## 2026-09-21 — 13B SWEEP LAUNCHED ON THE RENTED BOX (ruling 3, plan steps 1–7 landed)

**The box.** Vast.ai instance **51956148** (label `exp4c-13b`), on-demand, created ≈ 15:35 EDT: **NVIDIA A100 80GB PCIe** (81,920 MiB; driver 595.71.05; CUDA 13.2), 24 cores, 251 GB RAM, 220 GB disk, Japan, **$1.06/h all-in** — chosen over a 40 GB A100 (≈ 4–7 GiB of headroom over the rehearsal's 32.9 GiB peak, declined for the reason we are here) and over 96 GB RTX PRO 6000 offers (the A100 is the architecture the 09-20 benchmark ran torch 2.12.1 on; this host advertised 5.2 Gbps down). Image `vastai/pytorch`, ssh only; the SSH key is the program's dedicated `~/.ssh/vastai_ed25519`; the direct-IP route refuses the key and the proxy route (`ssh5.vast.ai:36148`) works. No GitHub credential and no HF token on the host (memory's rule; OLMo-2 is ungated — the Hub's unauthenticated rate limit is the download's ceiling).

**The stack on the box** (`setup_box.sh`, its log at `/workspace/setup_box.log`): the image ships only Python 3.10.12, under which the Mac's numpy pin cannot install (2.4.x requires ≥ 3.11) — a uv-managed **Python 3.11.16** venv at `/workspace/venv` (the Mac: 3.11.15); **torch 2.12.1+cu130, transformers 5.13.0, numpy 2.4.6, safetensors 0.8.0, huggingface_hub 1.22.0, tokenizers 0.22.2, scipy 1.17.1** — every pin the Mac carries, torch's build string the one difference the `stack` block will show. The repo: cloned from the 456 MB git bundle (sha256 `2f04772d62c56ec3…` verified on both ends; every ref and tag) and checked out at **`5ec95fa1b`** (the ruling-3 ledger commit); `git tag --list 'exp4c-*'` on the box: `exp4c-preregistered` only, as it should be. The three references' gitignored `attested/` files placed (34/34/34). Cache roots created. **Dry-run on CUDA:** `[4c sweep] prereg tag 'exp4c-preregistered'; thin endpoint pending; gate 1 olmo2_13b pending; would run 16 unit(s)` — the tag verified against the box's real git by `require_prereg_4c` inside the runner.

**Launched 19:37:21 UTC (15:37 EDT)** as the box's pid **1293**: `HF_HUB_DISABLE_XET=1 setsid nohup /workspace/venv/bin/python -m experiments.exp4c.run.sweep_4c --traj olmo2_13b --device cuda > /workspace/sweep_olmo2_13b.log 2>&1` from `/workspace/emergence-paper` (pid file `/workspace/sweep_olmo2_13b.pid`). Order under the runner as on the Mac: thin endpoint (the CUDA rehearsal of the collector — digest must equal 2l's committed one; finiteness is `metric_4.knn_sets`' own refusal) → gate 1 → the 16 grid points. First minutes: the endpoint's 12 shards fetching, ≈ 8 GB in the first 2.5 min.

**Results return (plan step 7).** `run/pull_13b_results.sh` (committed `eca44d388`) runs detached on the Mac (pid in `experiments/exp4c/pull_13b.pid`, log `pull_13b.log`, both gitignored): every 180 s it asks the box for unit directories under the 13B paths that hold a `_load.json` (written last by the frozen writer, so its presence means the unit is complete), pulls exactly those with `activations/` excluded, plus `gate1.json` and any halt marker; the standing watcher (pid 29448) commits each file as it lands, one commit per file, as for the 6.9b. The box holds nothing the tree will not. Step 8 (destroy) waits on Michael's word after the last unit is on the Mac and verified.
