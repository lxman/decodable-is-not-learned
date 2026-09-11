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
