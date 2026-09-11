# Experiment 4 — build ledger

## Task 1 (2026-09-10): metric_4.py

Built `experiments/exp4/metric_4.py`, the pure-numpy metric layer (no torch, no I/O; a deterministic function of activation bytes):

- `chance_4(n, k=K_4) -> float` — expected mutual-k-NN overlap between two independent rankings, `k / (n - 1)`.
- `sites_4(n_hidden) -> list[int]` — the sorted distinct layer indices of 2f's `site_family(n_hidden)` (every-3rd layer + final, `LAYER_STRIDE=3` confirmed against `SITE_COUNT_PIN_4`).
- `depth_pairs(sites_m, n_hidden_m, sites_q, n_hidden_q) -> list[int]` — for each m-site, the q-site nearest in relative depth, ties to the smaller q.
- `knn_sets(X, k=K_4) -> uint16[n, k]` — cosine k-NN, self excluded, ascending-sorted per row, ties broken by ascending index via a stable sort.
- `overlap_counts(A, B) -> uint8[n]` — per-row intersection size.
- `mutual_knn_from_sets(A, B) -> dict` — per-item overlap fraction, mean, k, n.
- `linear_cka_unbiased(X, Y) -> float` — Song et al. 2012 unbiased linear CKA (Huh et al.'s `unbiased_cka`), symmetric, rows ≥ 4.
- `planted_pair(n, d, signal, seed, d_latent=8) -> (X, Y)` float32 — one shared random projection `A`; X and Y differ only in independent noise (task-1 resolution 3).

### Invariance results (all exact / as specified)

- Self-alignment: `mutual_knn_from_sets(S, S)` gives per-item and mean == 1.0 exactly.
- k-NN sets exclude self, are sorted ascending, contain exactly `K_4` distinct indices per row.
- Orthogonal rotation of one side: exact set equality (or mean overlap > 0.99 as a fallback) — observed exact equality.
- Isotropic rescale by 4.0 (power of two, exact through fp32 and the float64 row-normalisation): exact set equality.
- Determinism: two calls on the same input produce identical uint16 arrays.
- Tie-breaking on an all-identical-row matrix: ascending index, as pinned by the test.
- CKA hand case (5-point 2-D array): self-CKA 1.0, scale invariance (×2.5) 1.0, rotation invariance 1.0, symmetry holds, value in [-1, 1] for an unrelated Y.

### Chance-band numbers (independent-features test, 100 seeds × 500 items × K_4=10)

- `chance_4(500)` = 0.02004008016032064
- observed mean over 100 seeds = 0.020352000000000002
- Clopper–Pearson band computed for the record only (not asserted, per task-1 resolution 2, since the 500,000 trials are dependent within each seed): `[0.019962398246166097, 0.020747173534658745]`
- Assertion actually used: `abs(mean - chance_4(500)) <= 3 * std(means, ddof=1) / sqrt(100)` — passed.

### Calibration fixture

`experiments/exp4/tests/fixtures/calibration_curve_4.json` — 20 signal levels `i/19` for `i` in `0..19`, curve = mean mutual-k-NN overlap over 5 seeds at `n=500, d=64, d_latent=8`. `curve[0] = 0.01896` (< 0.05), `curve[-1] = 1.0` (> 0.9), `curve[10] = 0.31904` (> `curve[0] + 0.1`), non-monotone dips bounded within 0.003 (only levels 0→1 dip, by 0.00004).

sha256: `970c6f80dec81749c1e1c9fb0581dae8190ba028e25b7263860d2a30ec3030f8`

### Tests

`experiments/exp4/tests/test_metric_4.py` — 9 tests, all pass on a second run (the calibration test writes the fixture and skips on the first run, then compares on later runs). `experiments/exp4/tests/conftest.py` registers the `slow` mark (2n's convention).

## Task 2 (2026-09-11): battery_4.py

Built `experiments/exp4/battery_4.py` — the fact layer: model tables from the four frozen manifests (2g/2i/2m/2n), the Pythia metadata scan, the load dispatcher wrapping each family's own frozen loader, committed-outcome readers, rung sets + t_clear, paths, records, gate-1 checkers, tag binding. Also `experiments/exp4/tests/fakes_4.py` (a torch-free numpy shim: `FakeTokenizer`, `FakeModel`, `fake_loaders`) and `experiments/exp4/tests/test_battery_4.py` (48 tests). `.gitignore`'s exp4 block had `experiments/exp4/mutation_*.log` removed per the plan's ruling (2n's Ruling R-7: mutation logs are committed, not ignored).

### Two resolved brief/frozen-code discrepancies (both settled by reading the frozen sources, documented in the module docstring)

1. **`checkpoints_2g.json`'s sha pin.** The brief's `bg.CHECKPOINTS_2G_SHA256` does not exist — `battery_2g.py` defines no such constant. The real pin lives on `analyze_2g.CHECKPOINTS_SHA256` (confirmed: `grep CHECKPOINTS_SHA256 experiments/exp2g/analyze_2g.py` → `CHECKPOINTS_SHA256 = "a5032f74f509669ea97600ad68cfe422e0fb6407a768b478f944868f42d3a2bc"`), and every downstream experiment that reads 2g's manifest (2h/2i/2m/2n's analyzers) pins it from there via the `an2g` alias. `battery_4.py` does the same: `ck.load_manifest(sha_pin=an2g.CHECKPOINTS_SHA256)`.
2. **`free_step_4`'s OLMo-2 branch.** The brief's literal text says `bi.free_checkpoint(bi.REPO_7B, step, cache_root)` — but `battery_2i`'s own `download_entry`/`clean_dir` (inside `load_checkpoint`) key the OLMo-2 cache directory by `entry["revision"]` (e.g. `"stage1-step1000-tokens5B"`), never by the raw step int (unlike Pythia's `_rev_dir`, which genuinely IS keyed by the raw step). Freeing by the raw step would silently no-op against a cache directory that was never created, leaking the real ~15 GB checkpoint. `battery_2m`/`battery_2n`'s own `free_checkpoint_3b`/`_comma` already key by `entry["revision"]`, confirming the reading. Implemented `free_step_4`'s OLMo-2 branch as `bi.free_checkpoint(bi.REPO_7B, entry["revision"], cache_root)`.

### The Pythia metadata scan (the build's ONE network call)

`python -m experiments.exp4.battery_4 --scan` (2026-09-11T04:01:37Z), `HfApi().model_info(repo).sha` for `EleutherAI/pythia-70m`, `-160m`, `-1.4b`:

```json
{
 "commits": {
  "1.4b": "fedc38a16eea3bd36a96b906d78d11d2ce18ed79",
  "160m": "50f5173d932e8e61f858120bcb800b97af589f46",
  "70m": "a39f36b100fe8a5377810d56c3f4789b9c53ac42"
 },
 "scanned": "2026-09-11T04:01:37.508646+00:00"
}
```

`hub_inventory_pythia_4.json` sha256: `2fe269324716fb917a8c3a620a8b2f59f96b4544aabcede0a60259feadc1c09e`. The three commits are pasted as literals into `PYTHIA_COMMITS_4` (merged with `models_2b.PYTHIA_SHAS`'s five) and re-asserted against the committed file at import (`load_pythia_inventory_4`) whenever the file is present — written this way (not a hard requirement) only so the module itself can be imported once, by `--scan`, before the one-time scan has run. No other network call anywhere in the build; no test touches the network.

### Rung sets and t_clear (the `--rungs` known-answer gate)

`python -m experiments.exp4.battery_4 --rungs` computes, per trajectory, `load_outcome_4` (every committed grid step's 34 rung records under `results/sweep/<traj>/`) → `rung_sets_4` with `battery_2g.load_floors()` (2d's frozen floors) → `check_rung_set_pins_4` against the pinned `RUNG_SET_PIN_4` (raises on any mismatch; ran clean). Summary:

| trajectory | endpoint_step | \|R\| | \|flat\| | \|transient\| | transient rungs |
| --- | --- | --- | --- | --- | --- |
| pythia_2.8b | 143000 | 7 | 27 | 0 | — |
| olmo2_7b | 928646 | 13 | 16 | 5 | clock24_d999, count_div13, median5, median7, oct2dec |
| smollm3_3b | 3440000 | 14 | 14 | 6 | clock24_d999, collatz_step2, count_div13, median5, median7, oct2dec |
| comma_7b | 460000 | 16 | 16 | 2 | count_div13, median5 |

`R` for all four exactly reproduces `RUNG_SET_PIN_4` (and, independently, 2g's `R_28` and the committed `rung_set_2i.json`/`rung_set_2m.json`/`rung_set_2n.json` `R_OLMO`/`R_3B`/`R_COMMA` — cross-checked directly against those files before writing the literals). `T_CLEAR_PIN_4` stays `None` per resolution 3 (Task 5 pins the literal); the full per-rung `t_clear`/`clears_and_stays` tables below are this task's record of what that pin will need to reproduce.

Full `--rungs` output:

```json
{
    "comma_7b": {
        "R": [
            "add3_mid",
            "add4_mid",
            "add_base8",
            "antonym",
            "antonym6",
            "arith_next",
            "clock24_d999",
            "median7",
            "oct2dec",
            "odd6",
            "quad_next",
            "rev_string7",
            "reverse_string",
            "sub3_mid",
            "sub4_mid",
            "sub_base8"
        ],
        "clears_and_stays": {
            "add3_mid": 40000,
            "add4_mid": 60000,
            "add_base8": 60000,
            "antonym": 180000,
            "antonym6": 40000,
            "arith_next": 10000,
            "base12_digitsum": null,
            "base13": null,
            "base7": null,
            "caesar": null,
            "caesar_len8": null,
            "clock24": null,
            "clock24_d999": 460000,
            "collatz_step2": null,
            "count_div13": null,
            "count_div7": null,
            "hamming12": null,
            "isqrt_gap": null,
            "median5": null,
            "median7": 380000,
            "mod13": null,
            "mod13_comp": null,
            "mod17": null,
            "mod19": null,
            "oct2dec": 460000,
            "odd6": 420000,
            "odd_one_out": null,
            "quad_next": 440000,
            "rev_string7": 460000,
            "reverse_string": 320000,
            "roman_sum7": null,
            "sub3_mid": 40000,
            "sub4_mid": 60000,
            "sub_base8": 40000
        },
        "endpoint_step": 460000,
        "flat": [
            "base12_digitsum",
            "base13",
            "base7",
            "caesar",
            "caesar_len8",
            "clock24",
            "collatz_step2",
            "count_div7",
            "hamming12",
            "isqrt_gap",
            "mod13",
            "mod13_comp",
            "mod17",
            "mod19",
            "odd_one_out",
            "roman_sum7"
        ],
        "t_clear": {
            "add3_mid": 40000,
            "add4_mid": 60000,
            "add_base8": 60000,
            "antonym": 40000,
            "antonym6": 40000,
            "arith_next": 10000,
            "base12_digitsum": null,
            "base13": null,
            "base7": null,
            "caesar": null,
            "caesar_len8": null,
            "clock24": null,
            "clock24_d999": 380000,
            "collatz_step2": null,
            "count_div13": 380000,
            "count_div7": null,
            "hamming12": null,
            "isqrt_gap": null,
            "median5": 200000,
            "median7": 200000,
            "mod13": null,
            "mod13_comp": null,
            "mod17": null,
            "mod19": null,
            "oct2dec": 460000,
            "odd6": 380000,
            "odd_one_out": null,
            "quad_next": 280000,
            "rev_string7": 420000,
            "reverse_string": 180000,
            "roman_sum7": null,
            "sub3_mid": 40000,
            "sub4_mid": 60000,
            "sub_base8": 40000
        },
        "transient": [
            "count_div13",
            "median5"
        ]
    },
    "olmo2_7b": {
        "R": [
            "add3_mid",
            "add4_mid",
            "add_base8",
            "antonym",
            "antonym6",
            "arith_next",
            "odd6",
            "odd_one_out",
            "quad_next",
            "reverse_string",
            "sub3_mid",
            "sub4_mid",
            "sub_base8"
        ],
        "clears_and_stays": {
            "add3_mid": 64000,
            "add4_mid": 128000,
            "add_base8": 32000,
            "antonym": 32000,
            "antonym6": 8000,
            "arith_next": 16000,
            "base12_digitsum": null,
            "base13": null,
            "base7": null,
            "caesar": null,
            "caesar_len8": null,
            "clock24": null,
            "clock24_d999": null,
            "collatz_step2": null,
            "count_div13": null,
            "count_div7": null,
            "hamming12": null,
            "isqrt_gap": null,
            "median5": null,
            "median7": null,
            "mod13": null,
            "mod13_comp": null,
            "mod17": null,
            "mod19": null,
            "oct2dec": null,
            "odd6": 128000,
            "odd_one_out": 256000,
            "quad_next": 768000,
            "rev_string7": null,
            "reverse_string": 64000,
            "roman_sum7": null,
            "sub3_mid": 64000,
            "sub4_mid": 128000,
            "sub_base8": 32000
        },
        "endpoint_step": 928646,
        "flat": [
            "base12_digitsum",
            "base13",
            "base7",
            "caesar",
            "caesar_len8",
            "clock24",
            "collatz_step2",
            "count_div7",
            "hamming12",
            "isqrt_gap",
            "mod13",
            "mod13_comp",
            "mod17",
            "mod19",
            "rev_string7",
            "roman_sum7"
        ],
        "t_clear": {
            "add3_mid": 64000,
            "add4_mid": 128000,
            "add_base8": 32000,
            "antonym": 32000,
            "antonym6": 8000,
            "arith_next": 16000,
            "base12_digitsum": null,
            "base13": null,
            "base7": null,
            "caesar": null,
            "caesar_len8": null,
            "clock24": null,
            "clock24_d999": 448000,
            "collatz_step2": null,
            "count_div13": 256000,
            "count_div7": null,
            "hamming12": null,
            "isqrt_gap": null,
            "median5": 256000,
            "median7": 256000,
            "mod13": null,
            "mod13_comp": null,
            "mod17": null,
            "mod19": null,
            "oct2dec": 576000,
            "odd6": 128000,
            "odd_one_out": 256000,
            "quad_next": 320000,
            "rev_string7": null,
            "reverse_string": 64000,
            "roman_sum7": null,
            "sub3_mid": 64000,
            "sub4_mid": 128000,
            "sub_base8": 32000
        },
        "transient": [
            "clock24_d999",
            "count_div13",
            "median5",
            "median7",
            "oct2dec"
        ]
    },
    "pythia_2.8b": {
        "R": [
            "add3_mid",
            "add_base8",
            "antonym",
            "antonym6",
            "arith_next",
            "sub3_mid",
            "sub_base8"
        ],
        "clears_and_stays": {
            "add3_mid": 80000,
            "add4_mid": null,
            "add_base8": 130000,
            "antonym": 40000,
            "antonym6": 40000,
            "arith_next": 30000,
            "base12_digitsum": null,
            "base13": null,
            "base7": null,
            "caesar": null,
            "caesar_len8": null,
            "clock24": null,
            "clock24_d999": null,
            "collatz_step2": null,
            "count_div13": null,
            "count_div7": null,
            "hamming12": null,
            "isqrt_gap": null,
            "median5": null,
            "median7": null,
            "mod13": null,
            "mod13_comp": null,
            "mod17": null,
            "mod19": null,
            "oct2dec": null,
            "odd6": null,
            "odd_one_out": null,
            "quad_next": null,
            "rev_string7": null,
            "reverse_string": null,
            "roman_sum7": null,
            "sub3_mid": 70000,
            "sub4_mid": null,
            "sub_base8": 90000
        },
        "endpoint_step": 143000,
        "flat": [
            "add4_mid",
            "base12_digitsum",
            "base13",
            "base7",
            "caesar",
            "caesar_len8",
            "clock24",
            "clock24_d999",
            "collatz_step2",
            "count_div13",
            "count_div7",
            "hamming12",
            "isqrt_gap",
            "median5",
            "median7",
            "mod13",
            "mod13_comp",
            "mod17",
            "mod19",
            "oct2dec",
            "odd6",
            "odd_one_out",
            "quad_next",
            "rev_string7",
            "reverse_string",
            "roman_sum7",
            "sub4_mid"
        ],
        "t_clear": {
            "add3_mid": 80000,
            "add4_mid": null,
            "add_base8": 70000,
            "antonym": 30000,
            "antonym6": 10000,
            "arith_next": 30000,
            "base12_digitsum": null,
            "base13": null,
            "base7": null,
            "caesar": null,
            "caesar_len8": null,
            "clock24": null,
            "clock24_d999": null,
            "collatz_step2": null,
            "count_div13": null,
            "count_div7": null,
            "hamming12": null,
            "isqrt_gap": null,
            "median5": null,
            "median7": null,
            "mod13": null,
            "mod13_comp": null,
            "mod17": null,
            "mod19": null,
            "oct2dec": null,
            "odd6": null,
            "odd_one_out": null,
            "quad_next": null,
            "rev_string7": null,
            "reverse_string": null,
            "roman_sum7": null,
            "sub3_mid": 70000,
            "sub4_mid": null,
            "sub_base8": 90000
        },
        "transient": []
    },
    "smollm3_3b": {
        "R": [
            "add3_mid",
            "add4_mid",
            "add_base8",
            "antonym",
            "antonym6",
            "arith_next",
            "odd6",
            "odd_one_out",
            "quad_next",
            "rev_string7",
            "reverse_string",
            "sub3_mid",
            "sub4_mid",
            "sub_base8"
        ],
        "clears_and_stays": {
            "add3_mid": 80000,
            "add4_mid": 120000,
            "add_base8": 40000,
            "antonym": 40000,
            "antonym6": 40000,
            "arith_next": 40000,
            "base12_digitsum": null,
            "base13": null,
            "base7": null,
            "caesar": null,
            "caesar_len8": null,
            "clock24": null,
            "clock24_d999": null,
            "collatz_step2": null,
            "count_div13": null,
            "count_div7": null,
            "hamming12": null,
            "isqrt_gap": null,
            "median5": null,
            "median7": null,
            "mod13": null,
            "mod13_comp": null,
            "mod17": null,
            "mod19": null,
            "oct2dec": null,
            "odd6": 2200000,
            "odd_one_out": 2200000,
            "quad_next": 1200000,
            "rev_string7": 3200000,
            "reverse_string": 120000,
            "roman_sum7": null,
            "sub3_mid": 600000,
            "sub4_mid": 400000,
            "sub_base8": 40000
        },
        "endpoint_step": 3440000,
        "flat": [
            "base12_digitsum",
            "base13",
            "base7",
            "caesar",
            "caesar_len8",
            "clock24",
            "count_div7",
            "hamming12",
            "isqrt_gap",
            "mod13",
            "mod13_comp",
            "mod17",
            "mod19",
            "roman_sum7"
        ],
        "t_clear": {
            "add3_mid": 80000,
            "add4_mid": 120000,
            "add_base8": 40000,
            "antonym": 40000,
            "antonym6": 40000,
            "arith_next": 40000,
            "base12_digitsum": null,
            "base13": null,
            "base7": null,
            "caesar": null,
            "caesar_len8": null,
            "clock24": null,
            "clock24_d999": 3200000,
            "collatz_step2": 2800000,
            "count_div13": 3000000,
            "count_div7": null,
            "hamming12": null,
            "isqrt_gap": null,
            "median5": 120000,
            "median7": 800000,
            "mod13": null,
            "mod13_comp": null,
            "mod17": null,
            "mod19": null,
            "oct2dec": 360000,
            "odd6": 240000,
            "odd_one_out": 1000000,
            "quad_next": 600000,
            "rev_string7": 1600000,
            "reverse_string": 120000,
            "roman_sum7": null,
            "sub3_mid": 80000,
            "sub4_mid": 200000,
            "sub_base8": 40000
        },
        "transient": [
            "clock24_d999",
            "collatz_step2",
            "count_div13",
            "median5",
            "median7",
            "oct2dec"
        ]
    }
}
```

### Tests

`experiments/exp4/tests/test_battery_4.py` — 48 tests: manifest grids against the frozen sources (`test_manifests_4_grids_match_frozen_sources`); the known-answer gate reproducing all four `RUNG_SET_PIN_4` from the committed sweep bits (`test_rung_set_pin_reproduces_from_the_committed_trees`, parametrized); `t_clear_4`/`clears_and_stays_4`/`rung_sets_4` on a hand-built four-rung/five-step outcome (`flat_r` never clears, `rise_r` clears and stays, `trans_r` clears/reverts/clears again and ends significant — lands in `R`, `blip_r` clears once and reverts for good — lands in `transient`; `t_clear_4` and `clears_and_stays_4` disagree on both `trans_r` and `blip_r`); `committed_step_digest_4` against both digest shapes (pythia's `_checkpoint.json`, the other three's rung-record `weight_sha256` string); `committed_init_digest_4` for all four (pythia's real step0, the other three's `twin`); `load_outcome_4`'s three refusals on a corrupted copy of a real step directory (missing rung file, tampered `items_sha256`, truncated `bits`); `BATCH_4`/`REFS_FOR_4`/`STAGE1_KEYS_4`/`STAGE1_FIRST_UNITS_4`/`N_HIDDEN_PIN_4`/`PYTHIA_COMMITS_4` shape and value checks; `require_prereg_4` on fakes (binds / refuses a missing tag / refuses drift — 2n's own test mirrored); `reference_seal_paths_4`'s exact 849-path shape (19×37 + 4×36 + 2), spot-checked (a reference key's `global.npz` present, a sweep unit's absent); `load_record_4`/`load_record_failures_4` round-tripping through real files on disk (six corrupted-field cases, sets/global sha re-hash mismatches, attested/activation sha presence); `unit_complete_4` true→false on corruption and on a missing tree; `gate1_record_4`/`gate1_failures_4` round-tripping (a bad rung, a bad tag, a bad digest); `gate1_rederive_4` on synthetic trees (all-equal, one rung differing, digest mismatch); `check_frozen_4` no-op when empty / raises on drift.

RED confirmed by temporarily moving `battery_4.py` aside: `test_battery_4.py` fails collection with `ImportError: cannot import name 'battery_4'`. GREEN: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp4/tests/test_battery_4.py -p no:cacheprovider -q` → `48 passed`. Full exp4 suite (`experiments/exp4/tests/`) → `57 passed` (48 + metric_4's 9).

## Task 3

`collect_4.py` (the per-load pipeline) + `run/reference_4.py` (stage 1) + `run/sweep_4.py` (stage 2, gate 1) + `run/preflight_4.py` (dial k) + `run/commit_watcher_4.sh` + `run/__init__.py`.

### Design decisions the brief's Interfaces block names but leaves open

`load_record_4` (Task 1/2, frozen) carries exactly four sha fields — `sets_sha256`, `global_sha256`, `attested_sha256`, `activation_sha256` — so every artifact this module writes had to fold into one of those four file groups. Resolved (documented at the top of `collect_4.py`):

- `sets/<rung>.npz` (COMMITTED): the model's own PROMPT-END k-NN sets, `uint16 [n_sites, 500, k]`, plus one `overlap_<ref>` `uint8 [n_sites, 500]` array per reference being aligned against (§3.8 calls the per-item overlaps "committed"; the record has no separate overlaps sha, so they share the sets file's).
- `attested/<rung>.npz` (gitignored, sha-attested): `question_end` + `pooled` k-NN set tables.
- `activations/<rung>.npz` (gitignored, sha-attested, deleted after its own re-read when `keep_activations=False`): raw `X`/`P`.
- `global.npz` (COMMITTED, reference-stage `str` keys only — never on a `(traj, step)` sweep unit, matching `reference_seal_paths_4`).
- `align.json`: `{rung: {ref: {...align_scalars_4 keys...}}}`.

`load_ref_tables_4` reads a reference's `sets/<rung>.npz` (always, sha-checked against the record) and additionally its `attested/<rung>.npz` when present (`sets_question_end`/`sets_pooled`) — the brief's shown return dict is the minimum, not exhaustive; `process_model_4`/`cross_reference_4` need that data from the same loader call.

The reference stage's own four `process_model_4` calls pass `refs=()` (not "whichever refs are already on disk" per an alternate reading of the brief) — `cross_reference_4` overwrites every reference's `align.json` from stored bytes immediately after, so an order-dependent partial computation on the first pass would be pure waste.

**Real finding, not a fixture artifact:** `align_scalars_4`'s CKA arm catches `ValueError` (`linear_cka_unbiased`'s "degenerate kernel") per site and stores `None` for that site rather than raising. Every rendered prompt ends with the literal `"\nA:"` cue, so the prompt-end TOKEN is identical across every item in a rung — the embedding-layer site (`sites_4`'s family always includes layer 0) therefore has a constant activation row across items at that position, a zero-variance Gram matrix, and `HSIC(K, K) == 0`. This is a property of the site and the render, reproducible on real weights, not only on the FakeModel fixture (which is what surfaced it during Task 3's own test-writing).

`metric_4.depth_pairs` returns, per m-site, the paired q-site as a hidden-state LAYER INDEX (an element of the `sites` list), not its position within that list — a bug caught immediately by the full-reference-stage test (`IndexError`). `collect_4._pairing_positions` converts layer index → array position before any `overlap_table_4`/CKA call indexes into a stored set/activation array.

### collect_4.py

`render_prompts_4`/`positions_4` (2c's `screen._render_prompt`/`_position_indices`, 2n's `render_2n` for the comma family); `collect_rung_4` (2f's `collect_items` with sites selected via `_stacked_sites` before any host transfer — real torch: `torch.stack(...)[sites]` on-device; the FakeModel shim: select-then-`np.stack`, same memory property — and the pooled attention-mask-weighted mean in float32 then cast fp16; `key=` optional kwarg pins `batch_size == battery_4.BATCH_4[key]`, since the Interfaces signature has no room for the key the brief's batching-pin resolution needs); `set_tables_4`/`pooled_sets_4`/`global_sets_4`/`overlap_table_4` (pure numpy over `metric_4`'s primitives); `align_scalars_4`; `write_load_4` (writes + re-reads + asserts array equality per artifact before returning; activations deleted, and their now-empty directory removed, only after that assertion); `process_model_4` (the whole per-rung loop over all 34 `battery_4.RUNGS`); `load_ref_tables_4`; `cross_reference_4`; `real_loaders_4`; small helpers `family_of_traj_4`, `non_pythia_refs_4`, `reference_halt_marker_path` (added here, per resolution 4, since `battery_4.py` has no reference-stage-wide halt path).

### run/reference_4.py

Refusal order `require_prereg_4` → `check_frozen_4` → any `HALTED` anywhere under `results/`. Skip-if-complete via `unit_complete_4` through the five groups (4 references with `refs=()` then `cross_reference_4`; 4 endpoints with the digest pin; 4 first units via `loaders["step"]`, `keep_activations=False`; 4 inits with `committed_init_digest_4`; 7 ladder sizes against the three non-Pythia references). `--only KEY` restricts to one key (used heavily by the tests to isolate a single digest-mismatch scenario without re-running the other 22 units). Eligibility: `run()` takes `eligibility_fn`; when given, writes `eligibility_path(root)` after the loads; `main()` resolves it lazily (`from experiments.exp4 import analyze_4`), prints the deferral line when it isn't buildable yet, and exposes `--only-eligibility` for the later standalone write (resolution 1).

### run/sweep_4.py

Refusal order `require_prereg_4` → `check_frozen_4` → `require_reference_seal_4` (2i's `require_seal_2i` over `battery_4.reference_seal_paths_4`, rejoined to `root` since that function stores paths relative to `root` not `repo_root`) → eligibility + power present → this trajectory's `HALTED`. Gate 1 first (`run_gate1`): a pre-check against both the committed digest and the sealed reference endpoint's digest (a mismatch halts before any processing); then `process_model_4` into `unit_dir`, `keep_activations=False`; then `gate1_rederive_4`/`gate1_record_4`/`gate1_failures_4` (byte-level, from Task 1/2) — any failure halts with `f"gate 1 {traj}: {failures}"`. Then every remaining grid step ascending, per-step digest pin, resumable.

### run/preflight_4.py

`ladder_pythia_2.8b` collected twice (two separate model calls, same weights, same pinned batching) on `antonym`/`add3_mid`; prints seconds, peak MPS memory, fp16 finiteness, `X` byte-identity and `set_tables_4` identity across the two passes; then `load_step_4("comma_7b", 10000)` end to end with the digest comparison printed, then freed. `check_frozen_4()` only (no prereg tag — this runs before the tag exists). Asserts a `(relpath, size)` snapshot of `results/` is unchanged before/after.

### run/commit_watcher_4.sh

2n's watcher verbatim, `--stage reference|sweep`, file glob `*.json`/`*.npz`/`HALTED`, excluding any path containing `/attested/` or `/activations/`, message prefix `exp4`.

### fakes_4.py (extended, per the brief's "you may extend it")

`FakeTokenizer.__call__`'s single-string, non-tensor call (the shape `screen._position_indices` uses) returned a 1-row-batched `input_ids`/`attention_mask` (`[[...]]`), making `len(tok(prompt, ...)["input_ids"])` always 1 regardless of prompt length — `screen._position_indices(tok, prompt)` returned `(0, 0)` for every prompt (verified directly before the fix). Fixed to unwrap to the flat list in that one case (real tokenizers are unbatched for a bare string); the batch/tensor path (`return_tensors="pt"`, always called with a list) is untouched.

### Tests

`test_collect_4.py` — 16 tests: `render_prompts_4` on a real item file (500 prompts, `\nA:`-terminated, comma-prefixed with `<|begin_of_text|>`); `positions_4` against `screen._position_indices` directly; `collect_rung_4` shape/dtype/determinism/device-independence on `FakeModel`, the wrong-`batch_size` raise (and the pinned value accepted); `set_tables_4`/`pooled_sets_4` shape+dtype; `global_sets_4` order (`RUNGS` order, not insertion order, verified with two out-of-order rungs); `overlap_table_4` against `metric_4.overlap_counts` per site plus its pairing-length raise; `align_scalars_4`'s full key set, including a reference with only `sets_prompt_end` (every other key `None`); `write_load_4` round-trips (sets/attested/activations/global re-read equality, shas matching the files, `keep_activations=False` leaving no `activations/` directory at all — not just an empty one); `load_ref_tables_4`'s sha-drift refusal (a hand-corrupted `sets/<rung>.npz` after a real `write_load_4`); `fake_loaders` shape sanity.

`test_stages_4.py` — 20 tests, FAKE loaders throughout, `battery_4.RUNGS` (all 34, hardcoded inside `process_model_4`) backed by a 12-item-per-rung synthetic battery (varied word-phrase questions via a per-rung-seeded `random.Random` — plain digit-suffixed questions produced near-duplicate FakeModel rows and a degenerate CKA kernel even before the real one was found) and a three-point shrunk grid (1000/2000/3000) for all four trajectories. Covers: prereg refusal; dry-run loads nothing (`results/` never created); the full 23-load reference campaign (all 19 `STAGE1_KEYS_4` + 4 first units `unit_complete_4`; `ladder_pythia_12b` never exists — it's `ref_pythia_12b`; a first unit gets no `global.npz`, a reference does; every record stamps `prereg_tag`; eligibility file written from an injected stub); skip-if-complete idempotence (a second run with loaders that raise `AssertionError` on any call proves nothing reloads); `cross_reference_4` fills all four references' `align.json` with exactly the other three; endpoint and init/twin digest-mismatch halts (no record written, `HALTED` under `results/reference/`); the any-`HALTED`-refuses check; sweep refusals (missing reference seal — via one shared `tag_exists` differentiated by tag string, since `require_prereg_4` and `require_reference_seal_4` take the same argument name on `sweep_4.run`; missing eligibility/power; a halt marker; a missing first unit) and its dry-run; gate 1 PASS (writes `gate1.json`, the remaining step runs, records stamp `prereg_tag`/`committed_digest`, no `activations/` dir on any sweep unit); gate 1 digest mismatch (halts before any further step, no `gate1.json`); a per-step digest mismatch (gate 1 itself intact); resume re-entering an incomplete unit; preflight's snapshot assertion (both the clean pass and a poisoned-mid-run failure) and its two-pass identity print line; the watcher's `zsh -n`.

Three test bugs surfaced and fixed while writing this suite, each instructive: (1) mutating one seed dict entry that two different "digest" lookups both read from is not a mismatch — the digest-mismatch tests needed the loader and the "committed" pin to read from genuinely independent sources (the committed side is monkeypatched to lie for one specific key, the loader is untouched); (2) `only=None` on `reference_4.run` runs everything, not "the references" — a partial-campaign test needs one `only=` call per key; (3) writing the "unexpected file" before `run()`'s own before-snapshot proves nothing — it has to land during the run (via a wrapped `loaders["release"]`).

RED confirmed structurally: every one of the five new files was created from nothing in this task (`experiments/exp4/collect_4.py`, `experiments/exp4/run/{reference_4,sweep_4,preflight_4,commit_watcher_4.sh}`), so `test_collect_4.py`/`test_stages_4.py` failed on collection (`ModuleNotFoundError`) until each was written; the `overlap_table_4` pairing-length check and the `metric_4.depth_pairs` layer-index/array-position bug were each verified to fail their respective test before the fix (mutation-tested by hand: reverting the fix reproduces the original failure). GREEN: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m pytest experiments/exp4/tests -p no:cacheprovider -q` → **107 passed**, zero warnings, ≈45s (the 20 `test_stages_4.py` tests, each running a fake-but-real 23-unit reference campaign or a 34-rung sweep unit, account for most of that).
