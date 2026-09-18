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
