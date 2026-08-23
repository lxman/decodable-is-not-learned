# Experiment 2g — Progress Ledger

Design doc `experiment-2g-design.md` stays as ruled (dials a–k, tag
`exp2g-preregistered`) — nothing in it is edited during the build. Zero
model contact throughout this session. Two locked stages ahead: stage 1
(the predictor collection — activations at 410m/1b) unlocks only after
the tag `exp2g-preregistered`; stage 2 (the checkpoint sweep — any
checkpoint load) unlocks only after the predictor table is committed
and tagged `exp2g-predictor-sealed`. Neither stage has run.

## 2026-08-23 — BUILD (session 2 of 3)

Build session dispatched at HEAD `5361ad6`. Executed task by task (15
tasks total) with a reviewer per task. Zero model contact throughout —
the only Hub traffic anywhere in the tree is the committed
`hub_inventory.json` metadata scan; no `from_pretrained` of weights, no
`hf_hub_download` of a weight file, no forward pass.

### Modules, what each pins, and its test count at the task that built it

- **`battery_2g.py`** (10 tests) — rung sets (`R_28` 7 rungs, `R_12b` 9
  rungs, `PREDICTOR_RUNGS` 11) re-derived from 2c's committed m4 counts
  under 2d's frozen bar; the grid (finding B: `step64000` excluded at
  2.8b, 21 trained points); 14 frozen-import shas over 2b/2c/2d/2f/3c
  code; 44 probe-activation shas; 2d's floor file sha-pinned; result
  paths.
- **`labels_2g.py`** (6 tests) — one label function per of the 11
  predictor rungs (position / octal ones digit / tens digit / hundreds
  digit / last digit / count); the 500/500 gate against the committed
  `probe_label` on eval AND probe items; class coverage; label floors.
- **`strata_2g.py`** (4 tests) — the §6.2 difficulty covariates
  (carries / borrows / octal carry / octal borrow / option position /
  crosses-100 / count) reproduce the doc's raw level counts on the
  committed items; the merge rule (ties to the lower neighbour, cascading
  merges, `MIN_STRATUM = 10`); position covariates never merged
  (nominal).
- **`stats_2g.py`** (7 tests) — within-stratum Somers' D, the mean-over-
  rungs statistic T, the block permutation null, the cluster bootstrap.
- **`probe_2g.py`** (6 tests) — CV site selection, per-item log-prob
  scores, the 2f-rule sensitivity.
- **`checkpoints_2g.py`** (9 tests) — the committed Hub inventory (155
  revisions × 2 sizes); finding A's candidate-weight-file rule (shards >
  own single safetensors > bin shards > bin); the grid manifest with
  every candidate sha pinned and cross-checked for uniqueness
  (`step64000` excluded with evidence, Hub `step143000` vs `main`
  recorded); the loader into 2c's pinned config with an
  `output_loading_info`-empty refusal; tensor digest; streaming cache.
  `hub_inventory.json`: 155 revisions × 2 sizes, committed. Manifest sha
  (`checkpoints_2g.json`, verified against the committed file):
  `b4c50031e25f861f85609892b75f0b4bfe2ed9c4440cca7dce6ba940d950defe`.
- **`collect_eval_2g.py`** (3 tests) — the stage-1 collector (2f's
  method verbatim); continuity on 8 committed probe rows per rung; gate
  P against 2f's committed eval activations for its two rungs; `pass`
  re-derived from the diffs. No model contact in the build.
- **`predictor_2g.py`** (3 tests + 1 slow) — the sealed table builder
  (labels/coverage/strata/continuity gates run inside it); `require_seal`
  (tag + blob sha + sha file); `load_predictor` shape pins. The slow
  gate (9.6 s): gate P's machinery half reproduces 2f's four committed
  per-site accuracies exactly.
- **`analyze_2g.py`** (8 tests) — the frozen analyzer: gate-1
  re-derivation (counts vs m4, digest equality, continuation diffs),
  step-record refusals with continuation re-verification, outcomes
  (count / first / last / stabilization), the rung-level descriptive,
  the primary (stratified / raw / twin + bootstrap), the §6.3 tree, the
  §6.4 secondaries (410m, eval-site rule, first-correct, label×covariate,
  sampler competitor, probe-beyond-sampler, 1b-performable exclusion,
  12b replication), refusals collected.
- **`run/sweep_2g.py`** (7 tests) — seal-first, gate-1-first (2c's
  loader vs m4 counts; 2g's loader digest + continuation identity), the
  `HALTED` marker + raise on any diff, streamed per-checkpoint records
  (per-item bits + continuations, weight shas, seal sha), skip-if-exists,
  dry run; injectable loaders so the control flow is tested with zero
  model contact.
- **Full-shape worlds** (5 tests, 9 worlds) — every record in the
  production layout with final counts equal to m4's pins: W1 FORECAST,
  W2 SURFACE, W3 DIFFICULTY-ONLY, W4 NO-FORECAST, W5 inverted → NO-
  FORECAST, W6 INSUFFICIENT (missing step), W7 INSUFFICIENT (halted),
  W8 INSUFFICIENT (seal mismatch), W9 FORECAST + 12b replication with
  `sub4_mid` THIN. 74 s.
- **`power_2g.py`** (4 tests) — the power simulation runs in the tie
  structure's own terms (real strata, `n_pos` from m4 counts, ρ
  calibrated to within-stratum D) through the verdict's own tree.
- **Referent battery** — manifest `referents_2g.json`, 139 files, sha
  (verified against the committed file):
  `ab8077e27d838fab7895ec7235fc3cab73ca7fc1ce4a1fb1f3aa0ab138ecff02`.
  `verify_referents_2g` 11/11 cold on the real tree.
- **Mutation harness** — 50 mutants over
  labels/strata/stats/probe/checkpoints/predictor/analyzer/runner.
  First pass 39/50 killed; eleven fixture gaps closed: [labels] gate
  corruption, [labels] 1/K floor, [strata] nominal never merged,
  [strata] pin, [stats] add-one p, [stats] one-sided, [stats]
  unweighted mean, [probe] true-class log-prob, [checkpoints] stale
  grid refused, [analyze] outcomes never counts step0, [analyze]
  load_sweep refuses a missing record — these eleven additional test
  cases landed in the files above and are why today's full-suite count
  exceeds the per-module counts recorded at each task's own commit.
  Second pass 50/50 killed. The harness deselects
  `tests/test_full_shape.py` (`DESELECT` in `mutation_check.py`) — the
  full-shape worlds' coverage is the dedicated worlds suite, not the
  mutation pass; running them under every mutant would be redundant
  and slow. Final-review fix wave (below) adds two more mutants
  (arith_next's 2f-label and mod-7 gates, labels_2g) — 52 in the `M`
  list now; not yet run, per Ruling 17 (the freeze re-runs the
  harness).

### Full suite (verified this session)

```
PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp2g/tests -q
83 passed, 1 skipped in 98.86s (0:01:38)
```

83 passed + 1 skipped = 78 (every module above except the full-shape
worlds) + 5 (the full-shape worlds). Task-time counts sum to 67; the
mutation pass added eleven fixtures — labels +2 (gate corruption; 1/K
floor), strata +2 (nominal never merged; pin), stats +3 (add-one p;
one-sided; unweighted mean), probe +1 (true-class log-prob),
checkpoints +1 (stale grid refused), analyze +2 (outcomes never counts
step0; load_sweep refuses a missing record) — 67 + 11 = 78, plus the 5
world tests = 83. The 1 skip is the slow gate-P machinery-reproduction
test, run explicitly and separately (not part of the default
collection's pass count). `power_2g.log` and `mutation_build.log` are
local run logs, not committed (see `.gitignore`).

### Power record

`power_2g.json`, written once, committed this task (SUPERSEDED — see
the re-roll note below):

- `declared_status`: **POWERED**
- `declaration`: "P(FORECAST | D_true = .15) = .935 against the bar
  .75; null false-FORECAST rate 0.000; null SD of T 0.0247"
- Full curve: D = .10 → P(FORECAST) = .565; D = .15 → .935; D = .20 →
  .940. `p_detect` (P(p_strat < .01), the stratified permutation
  p-value alone — not a verdict category): .985 / 1.0 / 1.0. Null (ρ =
  0): false-FORECAST rate 0.000, verdict is NO-FORECAST in all 200
  simulations. ρ calibrated to each D: .346 / .419 / .481.
- Note for the freeze: the effect bar T ≥ .10 binds at D = .10, as §7
  of the design predicted; the twin's α = .05 test caps FORECAST near
  .95 at every D (≈ 5% of true-FORECAST batteries route to SURFACE by
  construction, not by a weak effect).

**Re-rolled 2026-08-23 (final-review fix wave, I-5):** `N_SIM` raised
200 → 1000 (`N_PERM_POWER` = 500 unchanged, ledgered as a build dial
for ratification at the freeze); the record now also carries
`min_detectable_T` (the null run's empirical .99 quantile of T, from a
newly stored `Ts` list per `power_at` call) and `per_rung_precision`
(one calibrated simulation at `DECLARE_AT`: each R_28 rung's
`n_pairs` and a bootstrap SE on within-stratum D via `st.bootstrap_d`,
`n_boot` 200). The committed `power_2g.json` was `git rm`'d and the
re-rolled run started once, detached (~2 h); the figures above are
from the superseded 200-draw run — final numbers to be filled in by
the controller when the re-rolled `power_2g.json` lands and is
committed.

## Build findings, ledgered for ratification at the freeze

Findings A–E, verbatim from the design→build handoff at the top of
`docs/superpowers/plans/2026-08-23-exp2g-build.md`:

- **A — Hub branch layout (2.8b).** Of 155 revisions: 36 (step0…step25000)
  carry the true weights as `model-0000N-of-00002.safetensors` shards
  AND stale single-file `model.safetensors`/`pytorch_model.bin`
  byte-identical to `main`'s; 119 single-file branches, of which 77
  carry `main`'s `model.safetensors` as a stale copy (their
  `pytorch_model.bin` is the branch's own weights); branches step54000,
  56000, 57000, 58000, 59000, 61000, 62000, 63000, 64000 carry
  step143000's files; step26000, 53000, 103000 carry `main`'s. A naive
  `from_pretrained(revision="stepN")` prefers `model.safetensors` and
  would load the FINAL model under an intermediate label. 12b: every
  branch is three `pytorch_model-0000N-of-00003.bin` shards, unique
  except step50000/step58000 (stale copies of the final); `main`
  additionally carries safetensors shards. **Rule:** the candidate
  weight file per revision is (shards if present) else (single
  safetensors if its sha ≠ main's) else (the bin); a grid point whose
  candidate sha tuple equals any other revision's is excluded; the
  manifest pins every candidate's sha and the runner hashes what it
  downloaded. — Touches doc §4 "Streaming and pins", §5.
- **B — Grid.** 2.8b `step64000` is a stale copy of step143000 →
  EXCLUDED, disclosed; the 2.8b grid has **21 trained points** (not
  22): 1k, 2k, 4k, 8k, 10k, 16k, 20k, 30k, 32k, 40k, 50k, 60k, 70k, 80k,
  90k, 100k, 110k, 120k, 130k, 140k, final; y ∈ 0…21. 12b `step64000`
  is unique and stays. — Touches doc §4 grid paragraph ("22 trained
  checkpoints", "64000") + §11 e.
- **C — Gate 1 restated.** `step143000`'s `model.safetensors` at 2.8b
  (5,550,463,728 bytes, sha 462f2b96…) is a different serialization
  from 2c's pinned `main` (5,684,693,096 bytes, ab496f1c…), so "weight
  files sha-equal to main" cannot pass as written. The final grid point
  IS 2c's pinned `main` commit (`PYTHIA_SHAS[size]`), and gate 1 = (a)
  `main` through 2c's own loader (`models.load_pythia`) reproduces
  m4's correct counts exactly on every sweep rung (stack continuity),
  and (b) `main`'s candidate files through 2g's checkpoint loader give
  the same tensor digest and byte-identical continuations (loader
  path). The Hub's `step143000` branch is compared to `main` by tensor
  digest as a DESCRIPTIVE (at 12b its bytes equal `main`'s; at 2.8b
  they do not). — Touches doc §4 "The gate checkpoint runs first" + §5
  G-1.
- **D — Config pinned.** The sharded 2.8b branches' `config.json`
  differs from `main`'s (`eos_token_id` 2 vs 0, `transformers_version`
  4.36.0, dropout fields). Every checkpoint loads into
  `AutoConfig.from_pretrained(repo, revision=PYTHIA_SHAS[size])` — 2c's
  architecture — with `output_loading_info` asserted empty. — Touches
  doc §4, §5, new sentence.
- **E — Tokenizer pinned.** Branch `tokenizer.json` files differ in
  bytes (2,113,738 vs 2,113,710 at step1000); every checkpoint uses
  2b's `load_tokenizer(size)` at `PYTHIA_SHAS[size]`. — Touches doc §4,
  §5, new sentence.

Additional corrections found during the build, also for ratification:

- **F.** `arith_next`'s label gate compares against 2f's last-digit
  label function, with 2c's committed mod-7 `probe_label` recorded as a
  second referent. — Touches doc §3/§5 G-L wording.
- **G.** §6.2's parenthetical "(count 2, 15 items → into 3)" is wrong
  under its own rule: level 2 stays (15 ≥ `MIN_STRATUM` 10);
  `count_div13` merges 10 → 9 only. — Touches doc §6.2.
- **H.** Borrows are defined for a ≥ b; three committed `sub3_mid`
  items have a = b. §6.2 "(a > b)" → "(a ≥ b)". — Touches doc §6.2.
- **I.** §6.4's "2c's mod-7 label for `arith_next`" secondary is NOT
  built. Ratify either adding an `extra` cell to the predictor builder
  or striking the line. — Touches doc §6.4.
- **J.** Gate-1 record reads go through `collect()`; a torn `gate1.json`
  is INSUFFICIENT_DATA, not a crash. — Touches doc §5 wording.
- **K.** The runner's checkpoint lifecycle is in `try/finally` and the
  gate record is written LAST, so its presence implies the final
  step's records; the resume path refuses otherwise. — Touches doc §4
  "Streaming and pins" / §5 G-1 wording.
- **L.** `power_2g`'s rank→count mapping was inverted in the first
  draft (highest latent should get the most checkpoints) and corrected
  before the committed run.
- **M.** The committed m4 counts put SEVEN rungs over the bar at 2.8b
  (§1/§4.1 already say seven — no correction needed, recorded for
  completeness).
- **N.** §3's phrase "middle digit (tens; hundreds for 4-digit)"
  describes which digit each RUNG's label reads (`sub3_mid` → tens
  digit of a 3-digit answer; `sub4_mid` → hundreds digit of a 4-digit
  answer) — a property of the rung, not a rule that varies per
  individual answer within a rung. Reword at the freeze so it reads
  unambiguously per-rung. — Touches doc §3.

Three implementer-found corrections to brief literals (not doc text,
no ratification needed):

- `744 + 660` has two carries, not one (a fixture-example fix).
- A 50-draw permutation p floors at .0196, not below — a test-tolerance
  fix (`n_perm` raised to 200 for the add-one/one-sided/mean fixtures).
- `build_table` must run over all 11 predictor rungs, not one — a
  one-rung dict `KeyError`s on the rung-level secondary otherwise.

## Next

Adversarial freeze (session 3), tag `exp2g-preregistered`, stage 1
(the predictor collection) on Michael's word.

## 2026-08-23 — final-review fix wave

Opus's whole-branch review of `f7583a9..440ad4a` found 0 Critical, 8
Important (I-1..I-8), 12 Minor; Ruling 17 triaged I-1, I-2, I-3, I-4,
I-5, I-6, I-8, M-1/2/3/5/7/9/10/11/12, plus the four fix-before-freeze
deferred minors, into this wave (I-7's model-contact half and M-4's
trajectory figure PARKED for the freeze/Michael; M-6, M-8 parked as
ratification items). Applied: the four bare loader calls in
`analyze_2g.run()` now go through `collect()` with downstream uses
guarded (I-1); every §6.4 secondary is individually `collect()`ed,
non-gating, with `sec["failures"]` recording every reason (I-2); root
`.gitignore` covers `experiments/exp2g/results/activations_eval/`
(I-3); `sweep_2g.gate1`'s 2c-path clears `model`/`runner` after
`_release` so a 12b fp16 model doesn't stay doubly resident (I-4);
`power_2g` re-rolled at `N_SIM` 1000 with `min_detectable_T` and
`per_rung_precision` (I-5, run detached); a two-process determinism
test on a synthetic FORECAST world (I-6, 20.3 s, unconditional);
`PREREG_TAG` enforced via `predictor_2g.require_prereg()`, called
first in `build_predictor` and (lazily imported) in
`collect_eval_2g.run_one` (I-8); the rung-sets gate result is kept in
`gates["rung_sets"]` instead of being overwritten (M-9); W7's synthetic
halt tree now carries no per-step/per-rung records, matching the real
runner's halt-before-the-loop shape (M-2); `stale_main_copies` only
counts a match when BOTH sides carry the file — `checkpoints_2g.json`
and `referents_2g.json` re-pinned, `verify_referents_2g` 11/11 (M-3);
the label×covariate secondary scoped to `DIGIT_RUNGS ∩ R_28`, renamed
`label_x_covariate_strata_digit_rungs` (M-5); `run_step` and `gate1`
path (b) move the checkpoint download inside `try` with `model`
initialized to `None` first, `_release` tolerant of `None` (M-7); the
watcher's `git push` failure no longer kills the loop (M-10); plus the
12b `descriptive_item_level` for `sub3_mid`/`odd6` inside the 12b
replication block (M-4's fix-wave half). `check_index_files` added to
`checkpoints_2g.py` (I-7's metadata half) and run once by hand — 16
grid entries with a shard index, all confirmed present on the Hub.
