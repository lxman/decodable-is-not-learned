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
