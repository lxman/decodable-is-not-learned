# experiments/exp4/battery_4.py
"""Experiment 4's fact layer (design `experiment-4-design.md` §3-§5):
model tables read from the four frozen manifests (2g/2i/2m/2n), the
Pythia metadata scan for the three ladder sizes 2b never pinned, the
load dispatcher wrapping each family's own frozen loader family,
readers for the committed per-checkpoint outcome (2c's argmax record,
already on disk under each experiment's `results/sweep/`), the rung-
set rule (2d's bar applied along a training trajectory instead of a
model-size ladder), paths, records, the gate-1 byte-equality checkers,
and the prereg tag binding (2n's `require_prereg_2n` pattern).

Everything imported from `experiments/exp2*` is FROZEN: read, never
edited. `checkpoints_2g.candidate`/`.signature`/`.tensor_digest`, each
family's own `load_manifest*`/`entry_*`/`load_checkpoint*`/
`load_thin*`/`load_twin*`/`load_tokenizer*`/`free_checkpoint*`, 2g's
`load_floors` (2d's floor verdict), 2d's `stats_2d.binomial_bar` (the
same one-sided exact-binomial bar every experiment in this program has
used since 2d).

Two resolved brief/frozen-code discrepancies, both settled by reading
the frozen sources rather than guessed at:

1. `checkpoints_2g.json`'s own sha pin lives on `analyze_2g.
   CHECKPOINTS_SHA256` (`battery_2g` itself defines no
   `CHECKPOINTS_2G_SHA256` — every downstream experiment that reads
   2g's manifest, 2h through 2n, pins it from `analyze_2g`; this
   module does the same, via the `an2g` alias).
2. `free_step_4`'s OLMo-2 branch frees by `entry["revision"]` (e.g.
   `"stage1-step1000-tokens5B"`), the SAME cache key
   `battery_2i.download_entry`/`.clean_dir` actually key by inside
   `load_checkpoint` — not the raw step int. Freeing by the raw step
   would silently no-op against a cache directory that was never
   created (OLMo's `_cache_dir` is keyed by revision string, unlike
   Pythia's `_rev_dir`, which IS keyed by the raw step), leaving the
   real ~15 GB checkpoint cache never freed. `battery_2m`/`battery_2n`
   already key their own `free_checkpoint_3b`/`_comma` by
   `entry["revision"]`, confirming this reading.

`PYTHIA_COMMITS_4`'s three scanned shas (70m/160m/1.4b) are asserted
against the committed `hub_inventory_pythia_4.json` at import time
WHEN THAT FILE IS PRESENT (it always will be once committed; the
check is written this way, rather than a hard requirement, only so
the module can be imported once — by `--scan` itself — before the
one-time scan has run)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXP4 = Path(__file__).resolve().parent
EXPERIMENTS = EXP4.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import analyze_2g as an2g  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402
from experiments.exp2n import battery_2n as bn  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402

import models as models_2b  # noqa: E402  (exp2b's; on sys.path via battery_2d's own insertion)

RESULTS = EXP4 / "results"

PREREG_TAG_4 = "exp4-preregistered"
REFERENCE_SEAL_TAG_4 = "exp4-reference-sealed"
INSTRUMENT_BLOBS_4 = (
    "experiments/exp4/analyze_4.py",
    "experiments/exp4/battery_4.py",
    "experiments/exp4/metric_4.py",
    "experiments/exp4/collect_4.py",
    "experiments/exp4/run/reference_4.py",
    "experiments/exp4/run/sweep_4.py",
)

DTYPE_4 = "float16"
K_4 = metric_4.K_4
N_ITEMS = bt.N_ITEMS                    # 500
RUNGS = bt.RUNGS                        # 34 rungs
FAMILY_OF = bt.FAMILY_OF                # rung -> one of 16 families

POSITIONS_4 = ("question_end", "prompt_end")
PRIMARY_POSITION_4 = 1

RENDER_4 = {"pythia": "plain", "olmo2": "plain", "smollm3": "plain", "comma": "bos"}

TRAJECTORIES_4 = ("pythia_2.8b", "olmo2_7b", "smollm3_3b", "comma_7b")
REFERENCES_4 = ("ref_pythia_12b", "ref_olmo2_7b", "ref_smollm3_3b", "ref_comma_7b")

_FAMILY_OF_TRAJ_4 = {"pythia_2.8b": "pythia", "olmo2_7b": "olmo2",
                     "smollm3_3b": "smollm3", "comma_7b": "comma"}
_FAMILY_OF_REF_4 = {"ref_pythia_12b": "pythia", "ref_olmo2_7b": "olmo2",
                    "ref_smollm3_3b": "smollm3", "ref_comma_7b": "comma"}

LADDER_SIZES_4 = ("70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b")
PYTHIA_PARAMS_4 = {"70m": 70e6, "160m": 160e6, "410m": 410e6, "1b": 1.0e9,
                   "1.4b": 1.4e9, "2.8b": 2.8e9, "6.9b": 6.9e9, "12b": 12e9}

# --------------------------------------------------- the Pythia metadata scan

HUB_INVENTORY_PYTHIA_PATH = EXP4 / "hub_inventory_pythia_4.json"
_PYTHIA_SCAN_SIZES = ("70m", "160m", "1.4b")


def refresh_pythia_inventory_4(out_path=HUB_INVENTORY_PYTHIA_PATH) -> dict:
    """NETWORK (metadata only) — the ONE Hub call of this build. Refuses
    if `out_path` already exists: this runs once, ever, and every later
    read is of the committed file it wrote."""
    p = Path(out_path)
    if p.exists():
        raise RuntimeError(
            f"{p} already exists — refresh_pythia_inventory_4 is the ONE scan "
            f"of this build and refuses to overwrite a committed inventory")
    from datetime import datetime, timezone
    from huggingface_hub import HfApi
    api = HfApi()
    commits = {s: api.model_info(f"EleutherAI/pythia-{s}").sha for s in _PYTHIA_SCAN_SIZES}
    out = {"scanned": datetime.now(timezone.utc).isoformat(), "commits": commits}
    p.write_text(json.dumps(out, indent=1, sort_keys=True))
    return out


def load_pythia_inventory_4(path=HUB_INVENTORY_PYTHIA_PATH) -> dict:
    obj = json.loads(Path(path).read_text())
    if set(obj.get("commits", {})) != set(_PYTHIA_SCAN_SIZES):
        raise ValueError(f"{path}: does not carry exactly {_PYTHIA_SCAN_SIZES}")
    return obj


# The three commits the scan wrote (`hub_inventory_pythia_4.json`,
# committed) — pasted as literals per the build's resolution 2, and
# re-asserted against that file below (when it is present).
PYTHIA_COMMITS_4 = {
    **models_2b.PYTHIA_SHAS,
    "70m": "a39f36b100fe8a5377810d56c3f4789b9c53ac42",
    "160m": "50f5173d932e8e61f858120bcb800b97af589f46",
    "1.4b": "fedc38a16eea3bd36a96b906d78d11d2ce18ed79",
}

if HUB_INVENTORY_PYTHIA_PATH.exists():
    _scanned_4 = load_pythia_inventory_4()
    for _s in _PYTHIA_SCAN_SIZES:
        if PYTHIA_COMMITS_4[_s] != _scanned_4["commits"][_s]:
            raise ValueError(
                f"PYTHIA_COMMITS_4[{_s!r}] literal {PYTHIA_COMMITS_4[_s]!r} != the "
                f"committed scan {_scanned_4['commits'][_s]!r} in "
                f"{HUB_INVENTORY_PYTHIA_PATH}")
    del _scanned_4
    del _s

# ------------------------------------------------------------------- params

_BASE_PARAMS_4 = {"pythia_2.8b": PYTHIA_PARAMS_4["2.8b"], "olmo2_7b": 7.3e9,
                  "smollm3_3b": 3.1e9, "comma_7b": 7.0e9}
_REF_PARAMS_4 = {"ref_pythia_12b": PYTHIA_PARAMS_4["12b"], "ref_olmo2_7b": 7.3e9,
                 "ref_smollm3_3b": 3.1e9, "ref_comma_7b": 7.0e9}


def _init_key_of(traj: str) -> str:
    if traj == "pythia_2.8b":
        return "init_pythia_2.8b"
    return f"twin_{traj}"


INIT_KEY_4 = {traj: _init_key_of(traj) for traj in TRAJECTORIES_4}

PARAMS_4 = {}
PARAMS_4.update(_BASE_PARAMS_4)
PARAMS_4.update(_REF_PARAMS_4)
for _traj in TRAJECTORIES_4:
    PARAMS_4[f"endpoint_{_traj}"] = _BASE_PARAMS_4[_traj]
    PARAMS_4[INIT_KEY_4[_traj]] = _BASE_PARAMS_4[_traj]
for _s in LADDER_SIZES_4:
    if _s != "12b":
        PARAMS_4[f"ladder_pythia_{_s}"] = PYTHIA_PARAMS_4[_s]
del _traj, _s

BATCH_4 = {k: (16 if v >= 6e9 else 32) for k, v in PARAMS_4.items()}

# ---------------------------------------------------------------- n_hidden

_N_HIDDEN_TRAJ_4 = {"pythia_2.8b": 33, "olmo2_7b": 33, "smollm3_3b": 37, "comma_7b": 33}
_N_HIDDEN_REF_4 = {"ref_pythia_12b": 37, "ref_olmo2_7b": 33, "ref_smollm3_3b": 37,
                   "ref_comma_7b": 33}
_N_HIDDEN_LADDER_4 = {"70m": 7, "160m": 13, "410m": 25, "1b": 17, "1.4b": 25,
                      "2.8b": 33, "6.9b": 33}

N_HIDDEN_PIN_4 = {}
N_HIDDEN_PIN_4.update(_N_HIDDEN_TRAJ_4)
N_HIDDEN_PIN_4.update(_N_HIDDEN_REF_4)
for _traj in TRAJECTORIES_4:
    N_HIDDEN_PIN_4[f"endpoint_{_traj}"] = _N_HIDDEN_TRAJ_4[_traj]
    N_HIDDEN_PIN_4[INIT_KEY_4[_traj]] = _N_HIDDEN_TRAJ_4[_traj]
for _s, _v in _N_HIDDEN_LADDER_4.items():
    N_HIDDEN_PIN_4[f"ladder_pythia_{_s}"] = _v
del _traj, _s, _v

# -------------------------------------------------------------------- grid

GRID_4 = {
    "pythia_2.8b": (1000, 2000, 4000, 8000, 10000, 16000, 20000, 30000, 32000,
                    40000, 50000, 60000, 70000, 80000, 90000, 100000, 110000,
                    120000, 130000, 140000, 143000),
    "olmo2_7b": (1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000, 192000,
                 256000, 320000, 384000, 448000, 512000, 576000, 640000,
                 704000, 768000, 832000, 896000, 928646),
    "smollm3_3b": (40000, 80000, 120000, 160000, 200000, 240000, 280000, 320000,
                   360000, 400000, 600000, 800000, 1000000, 1200000, 1400000,
                   1600000, 1800000, 2000000, 2200000, 2400000, 2600000,
                   2800000, 3000000, 3200000, 3400000, 3440000),
    "comma_7b": (10000, 20000, 40000, 60000, 80000, 100000, 120000, 140000,
                 160000, 180000, 200000, 220000, 240000, 260000, 280000,
                 300000, 320000, 340000, 360000, 380000, 400000, 420000,
                 440000, 460000),
}
ENDPOINT_STEP_4 = {traj: GRID_4[traj][-1] for traj in TRAJECTORIES_4}
FIRST_STEP_4 = {traj: GRID_4[traj][0] for traj in TRAJECTORIES_4}

FAMILY_OF_KEY_4 = {}
FAMILY_OF_KEY_4.update(_FAMILY_OF_TRAJ_4)
FAMILY_OF_KEY_4.update(_FAMILY_OF_REF_4)
for _traj in TRAJECTORIES_4:
    FAMILY_OF_KEY_4[f"endpoint_{_traj}"] = _FAMILY_OF_TRAJ_4[_traj]
    FAMILY_OF_KEY_4[INIT_KEY_4[_traj]] = _FAMILY_OF_TRAJ_4[_traj]
for _s in LADDER_SIZES_4:
    if _s != "12b":
        FAMILY_OF_KEY_4[f"ladder_pythia_{_s}"] = "pythia"
del _traj, _s

REFS_FOR_4 = {traj: tuple(r for r in REFERENCES_4 if FAMILY_OF_KEY_4[r] != FAMILY_OF_KEY_4[traj])
             for traj in TRAJECTORIES_4}

STAGE1_KEYS_4 = (
    REFERENCES_4
    + tuple(f"endpoint_{traj}" for traj in TRAJECTORIES_4)
    + tuple(INIT_KEY_4[traj] for traj in TRAJECTORIES_4)
    + tuple(f"ladder_pythia_{s}" for s in LADDER_SIZES_4 if s != "12b")
)  # 4 + 4 + 4 + 7 = 19

STAGE1_FIRST_UNITS_4 = tuple((traj, FIRST_STEP_4[traj]) for traj in TRAJECTORIES_4)  # 4

# ------------------------------------------------------------- rung-set pins

# The four committed R_M, each reproduced from the sweep bits by
# `rung_sets_4(load_outcome_4(traj), battery_2g.load_floors())["R"]`
# (the known-answer gate `check_rung_set_pins_4` enforces).
RUNG_SET_PIN_4 = {
    "pythia_2.8b": ("add3_mid", "add_base8", "antonym", "antonym6", "arith_next",
                    "sub3_mid", "sub_base8"),
    "olmo2_7b": ("add3_mid", "add4_mid", "add_base8", "antonym", "antonym6",
                 "arith_next", "odd6", "odd_one_out", "quad_next", "reverse_string",
                 "sub3_mid", "sub4_mid", "sub_base8"),
    "smollm3_3b": ("add3_mid", "add4_mid", "add_base8", "antonym", "antonym6",
                   "arith_next", "odd6", "odd_one_out", "quad_next", "rev_string7",
                   "reverse_string", "sub3_mid", "sub4_mid", "sub_base8"),
    "comma_7b": ("add3_mid", "add4_mid", "add_base8", "antonym", "antonym6",
                 "arith_next", "clock24_d999", "median7", "oct2dec", "odd6",
                 "quad_next", "rev_string7", "reverse_string", "sub3_mid",
                 "sub4_mid", "sub_base8"),
}
# Task 5: the literal `{traj: {rung: step or None}}` t_clear table,
# reproduced from `python -m experiments.exp4.battery_4 --rungs` and
# verified byte-for-byte against Task 2's own printed table in
# PROGRESS.md (`check_rung_set_pins_4` re-asserts it on every real run).
T_CLEAR_PIN_4 = {'comma_7b': {'add3_mid': 40000,
              'add4_mid': 60000,
              'add_base8': 60000,
              'antonym': 40000,
              'antonym6': 40000,
              'arith_next': 10000,
              'base12_digitsum': None,
              'base13': None,
              'base7': None,
              'caesar': None,
              'caesar_len8': None,
              'clock24': None,
              'clock24_d999': 380000,
              'collatz_step2': None,
              'count_div13': 380000,
              'count_div7': None,
              'hamming12': None,
              'isqrt_gap': None,
              'median5': 200000,
              'median7': 200000,
              'mod13': None,
              'mod13_comp': None,
              'mod17': None,
              'mod19': None,
              'oct2dec': 460000,
              'odd6': 380000,
              'odd_one_out': None,
              'quad_next': 280000,
              'rev_string7': 420000,
              'reverse_string': 180000,
              'roman_sum7': None,
              'sub3_mid': 40000,
              'sub4_mid': 60000,
              'sub_base8': 40000},
 'olmo2_7b': {'add3_mid': 64000,
              'add4_mid': 128000,
              'add_base8': 32000,
              'antonym': 32000,
              'antonym6': 8000,
              'arith_next': 16000,
              'base12_digitsum': None,
              'base13': None,
              'base7': None,
              'caesar': None,
              'caesar_len8': None,
              'clock24': None,
              'clock24_d999': 448000,
              'collatz_step2': None,
              'count_div13': 256000,
              'count_div7': None,
              'hamming12': None,
              'isqrt_gap': None,
              'median5': 256000,
              'median7': 256000,
              'mod13': None,
              'mod13_comp': None,
              'mod17': None,
              'mod19': None,
              'oct2dec': 576000,
              'odd6': 128000,
              'odd_one_out': 256000,
              'quad_next': 320000,
              'rev_string7': None,
              'reverse_string': 64000,
              'roman_sum7': None,
              'sub3_mid': 64000,
              'sub4_mid': 128000,
              'sub_base8': 32000},
 'pythia_2.8b': {'add3_mid': 80000,
                 'add4_mid': None,
                 'add_base8': 70000,
                 'antonym': 30000,
                 'antonym6': 10000,
                 'arith_next': 30000,
                 'base12_digitsum': None,
                 'base13': None,
                 'base7': None,
                 'caesar': None,
                 'caesar_len8': None,
                 'clock24': None,
                 'clock24_d999': None,
                 'collatz_step2': None,
                 'count_div13': None,
                 'count_div7': None,
                 'hamming12': None,
                 'isqrt_gap': None,
                 'median5': None,
                 'median7': None,
                 'mod13': None,
                 'mod13_comp': None,
                 'mod17': None,
                 'mod19': None,
                 'oct2dec': None,
                 'odd6': None,
                 'odd_one_out': None,
                 'quad_next': None,
                 'rev_string7': None,
                 'reverse_string': None,
                 'roman_sum7': None,
                 'sub3_mid': 70000,
                 'sub4_mid': None,
                 'sub_base8': 90000},
 'smollm3_3b': {'add3_mid': 80000,
                'add4_mid': 120000,
                'add_base8': 40000,
                'antonym': 40000,
                'antonym6': 40000,
                'arith_next': 40000,
                'base12_digitsum': None,
                'base13': None,
                'base7': None,
                'caesar': None,
                'caesar_len8': None,
                'clock24': None,
                'clock24_d999': 3200000,
                'collatz_step2': 2800000,
                'count_div13': 3000000,
                'count_div7': None,
                'hamming12': None,
                'isqrt_gap': None,
                'median5': 120000,
                'median7': 800000,
                'mod13': None,
                'mod13_comp': None,
                'mod17': None,
                'mod19': None,
                'oct2dec': 360000,
                'odd6': 240000,
                'odd_one_out': 1000000,
                'quad_next': 600000,
                'rev_string7': 1600000,
                'reverse_string': 120000,
                'roman_sum7': None,
                'sub3_mid': 80000,
                'sub4_mid': 200000,
                'sub_base8': 40000}}

SWEEP_ROOT_4 = {
    "pythia_2.8b": bg.sweep_dir(bg.EXP2G, "2.8b"),
    "olmo2_7b": bi.sweep_dir(bi.EXP2I),
    "smollm3_3b": bm.sweep_dir(bm.EXP2M),
    "comma_7b": bn.sweep_dir(bn.EXP2N),
}

# ------------------------------------------------------- manifests + grids

_GRID_FIELD_4 = {"pythia_2.8b": "trained_steps", "olmo2_7b": "grid_7b",
                 "smollm3_3b": "grid_3b", "comma_7b": "grid_comma"}


def manifests_4() -> dict:
    """Each trajectory's own (family-native) manifest object, each
    grid re-asserted equal to `GRID_4`."""
    m = {
        "pythia_2.8b": ck.load_manifest(sha_pin=an2g.CHECKPOINTS_SHA256)["2.8b"],
        "olmo2_7b": bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256),
        "smollm3_3b": bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256),
        "comma_7b": bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256),
    }
    for traj, field in _GRID_FIELD_4.items():
        got = tuple(m[traj][field])
        if got != GRID_4[traj]:
            raise ValueError(f"{traj}: manifest {field} {got} != GRID_4 {GRID_4[traj]}")
    return m


def grid_entry_4(traj: str, step) -> dict:
    """The family-native manifest entry for one grid step, read fresh
    (the FULL, un-sliced manifest — `manifests_4()`'s per-trajectory
    value is already sliced to the trajectory for the grid check)."""
    if traj == "pythia_2.8b":
        m = ck.load_manifest(sha_pin=an2g.CHECKPOINTS_SHA256)
        return ck.entry_for(m, "2.8b", step)
    if traj == "olmo2_7b":
        m = bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256)
        return bi.entry_7b(m, step)
    if traj == "smollm3_3b":
        m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
        return bm.entry_3b(m, step)
    if traj == "comma_7b":
        m = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
        return bn.entry_comma(m, step)
    raise ValueError(f"{traj!r} is not an exp4 trajectory")


# --------------------------------------------------- the committed outcome

def committed_step_digest_4(traj: str, step) -> str:
    """`<SWEEP_ROOT_4[traj]>/step<step>/_checkpoint.json`'s `digest`
    (2g: `sweep_dir/step0` reads too — the real init)."""
    p = SWEEP_ROOT_4[traj] / f"step{int(step)}" / "_checkpoint.json"
    obj = json.loads(p.read_text())
    digest = obj.get("digest")
    if not digest:
        raise ValueError(f"{p}: no digest")
    return digest


def committed_init_digest_4(traj: str) -> str:
    """`pythia_2.8b`: step0's own digest (a real checkpoint). The other
    three: the sweep's `twin/_checkpoint.json` digest (no true step 0
    on those branches)."""
    if traj == "pythia_2.8b":
        return committed_step_digest_4(traj, 0)
    p = SWEEP_ROOT_4[traj] / "twin" / "_checkpoint.json"
    obj = json.loads(p.read_text())
    digest = obj.get("digest")
    if not digest:
        raise ValueError(f"{p}: no digest")
    return digest


def load_outcome_4(traj: str, *, battery=None) -> dict:
    """The committed per-checkpoint argmax outcome over `GRID_4[traj]`:
    `{"steps": [...], "per_step": {step: {"digest": str, "rungs":
    {rung: {"correct": int, "n": 500, "bits": [500]}}}}}`. Every one of
    the 34 rungs is required at every step (a missing rung file raises
    `FileNotFoundError`); `n == 500`, `len(bits) == 500`, and
    `items_sha256` must equal the committed battery's own pin, or this
    refuses with `ValueError`."""
    if battery is None:
        battery = bt.load_battery()
    root = SWEEP_ROOT_4[traj]
    steps = list(GRID_4[traj])
    per_step = {}
    for step in steps:
        step_dir = root / f"step{int(step)}"
        ckpt = json.loads((step_dir / "_checkpoint.json").read_text())
        digest = ckpt.get("digest")
        if not digest:
            raise ValueError(f"{step_dir}/_checkpoint.json: no digest")
        rungs = {}
        for rung in RUNGS:
            p = step_dir / f"{rung}.json"
            rec = json.loads(p.read_text())
            if rec.get("rung") != rung:
                raise ValueError(f"{p}: rung field {rec.get('rung')!r} != {rung!r}")
            if int(rec.get("step")) != int(step):
                raise ValueError(f"{p}: step field {rec.get('step')!r} != {step}")
            if rec.get("n") != N_ITEMS:
                raise ValueError(f"{p}: n {rec.get('n')!r} != {N_ITEMS}")
            bits = rec.get("bits")
            if not isinstance(bits, list) or len(bits) != N_ITEMS:
                raise ValueError(f"{p}: bits is not a {N_ITEMS}-length list")
            want_sha = battery[rung]["items_sha256"]
            if rec.get("items_sha256") != want_sha:
                raise ValueError(f"{p}: items_sha256 {rec.get('items_sha256')!r} "
                                 f"!= the committed battery's {want_sha!r}")
            # FREEZE F-3 (2n F-1's shape, one field over): design §3.1
            # says the representation is collected "rendered exactly as
            # the committed outcome sweep of M's family rendered them
            # ... asserted against the committed records' `render`
            # field where one exists". Nothing asserted it. Gate 1 is
            # structurally blind here — both of its sides are exp4
            # loads through the same `RENDER_4`, so a wrong render
            # agrees with itself — and nothing in exp4 generates, so no
            # continuation can disagree either. The committed outcome
            # record is the only witness, and it is on disk: 2n's carry
            # `render: "bos"`, 2g/2i/2m carry no `render` key at all
            # (plain by construction of their frozen harness).
            want_render = RENDER_4[_FAMILY_OF_TRAJ_4[traj]]
            got_render = rec["render"] if "render" in rec else "plain"
            if got_render != want_render:
                raise ValueError(f"{p}: the committed outcome's render {got_render!r} != "
                                 f"RENDER_4[{_FAMILY_OF_TRAJ_4[traj]!r}] {want_render!r} — "
                                 f"exp4 would read the representation off prompts the "
                                 f"outcome never saw")
            if rec.get("dtype") != DTYPE_4:
                raise ValueError(f"{p}: the committed outcome's dtype {rec.get('dtype')!r} != "
                                 f"DTYPE_4 {DTYPE_4!r}")
            want_shots = len(battery[rung]["shots"])
            if int(rec.get("n_shots", -1)) != want_shots:
                raise ValueError(f"{p}: the committed outcome's n_shots "
                                 f"{rec.get('n_shots')!r} != the battery's {want_shots}")
            rungs[rung] = {"correct": int(rec["correct"]), "n": int(rec["n"]),
                           "bits": list(bits)}
        per_step[step] = {"digest": digest, "rungs": rungs}
    return {"steps": steps, "per_step": per_step}


def _outcome_rungs(outcome: dict) -> list:
    steps = outcome["steps"]
    if not steps:
        return []
    return sorted(outcome["per_step"][steps[0]]["rungs"])


def t_clear_4(outcome: dict, floors: dict) -> dict:
    """`{rung: first grid step (ascending) at which `stats_2d.
    binomial_bar` is significant, or None}`. Rungs are read from the
    outcome itself (its first step's rung set), not from the global
    34-rung constant, so this also works on a hand-built fixture."""
    steps = outcome["steps"]
    out = {}
    for rung in _outcome_rungs(outcome):
        first = None
        for step in steps:
            rec = outcome["per_step"][step]["rungs"][rung]
            if st.binomial_bar(rec["correct"], rec["n"], floors[rung])["significant"]:
                first = step
                break
        out[rung] = first
    return out


def clears_and_stays_4(outcome: dict, floors: dict) -> dict:
    """`{rung: first step S such that every step from S through the
    end (inclusive) is significant, or None}`. Differs from
    `t_clear_4` exactly on a TRANSIENT rung (significant, then not,
    then significant again): `t_clear_4` reports the first rise;
    `clears_and_stays_4` reports the last rise that never reverts."""
    steps = outcome["steps"]
    sig = {}
    for rung in _outcome_rungs(outcome):
        sig[rung] = [st.binomial_bar(outcome["per_step"][s]["rungs"][rung]["correct"],
                                     outcome["per_step"][s]["rungs"][rung]["n"],
                                     floors[rung])["significant"] for s in steps]
    out = {}
    for rung, flags in sig.items():
        result = None
        for i, step in enumerate(steps):
            if all(flags[i:]):
                result = step
                break
        out[rung] = result
    return out


def rung_sets_4(outcome: dict, floors: dict) -> dict:
    """`{"R": sorted rising, "flat": sorted never-significant, "transient":
    sorted rest, "t_clear": ..., "clears_and_stays": ..., "endpoint_step":
    int}`. R = significant at the LAST grid step; flat = significant at
    NO step; transient = the rest (fired at some point, not at the
    endpoint)."""
    steps = outcome["steps"]
    endpoint_step = steps[-1]
    rungs = _outcome_rungs(outcome)
    endpoint_rungs = outcome["per_step"][endpoint_step]["rungs"]
    tc = t_clear_4(outcome, floors)
    cas = clears_and_stays_4(outcome, floors)
    rising, flat = [], []
    for rung in rungs:
        rec = endpoint_rungs[rung]
        if st.binomial_bar(rec["correct"], rec["n"], floors[rung])["significant"]:
            rising.append(rung)
        elif tc[rung] is None:
            flat.append(rung)
    transient = sorted(set(rungs) - set(rising) - set(flat))
    return {"R": sorted(rising), "flat": sorted(flat), "transient": transient,
            "t_clear": tc, "clears_and_stays": cas, "endpoint_step": int(endpoint_step)}


def check_rung_set_pins_4(traj: str, rung_sets: dict) -> list:
    bad = []
    got_r = tuple(sorted(rung_sets["R"]))
    want_r = tuple(sorted(RUNG_SET_PIN_4[traj]))
    if got_r != want_r:
        bad.append(f"{traj}: R {list(got_r)} != the pinned {list(want_r)}")
    if T_CLEAR_PIN_4 is not None:
        pin = T_CLEAR_PIN_4.get(traj, {})
        if rung_sets["t_clear"] != pin:
            bad.append(f"{traj}: t_clear does not match the pin")
    return bad


# ------------------------------------------------------------------ loaders
# (MODEL CONTACT — the functions below are never executed by a test.)

CKPT_CACHE_4 = Path.home() / "emergence-lab" / "ckpt_cache_4"

# The eight fields every loader's `info` dict must carry (design's
# loader-dispatch contract) and the closed set of loader-path labels
# `info["kind"]` may take. "2b" = 2b's `load_pythia` path; "thin" =
# any family's plain `load_thin*` (no candidate-file selection);
# "candidate" = the candidate-file/clean-dir path (`ck.load_checkpoint`
# and each family's own `load_checkpoint*`); "from_config" = a seeded
# init-referent twin (no weights loaded from any file at all).
_INFO_CONTRACT_FIELDS_4 = ("tensor_digest", "commit", "revision", "repo", "kind",
                           "config_source", "n_hidden", "loading_info")
_INFO_KIND_VALUES_4 = ("2b", "thin", "candidate", "from_config")

# A `from_config` build (a twin) loads no weights from any file, so
# there is no missing/unexpected/mismatched-key comparison to make —
# the all-zero record is the true statement "nothing was compared",
# not a laundered absence. The same true statement holds for the 2b
# path (`models_2b.load_pythia` does not request
# `output_loading_info`, but the frozen `from_pretrained` call it makes
# is a full, untouched checkpoint — no candidate-file subsetting to
# verify against).
_ZERO_LOADING_INFO_4 = {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}


def _complete_info(info: dict, *, commit, revision, repo, kind, config_source,
                   n_hidden, loading_info) -> dict:
    """Fills only the fields `info` is missing (absent or `None`) with
    the given values — never overrides a value the underlying frozen
    loader already set — then asserts every one of the eight
    contractual fields (`_INFO_CONTRACT_FIELDS_4`) is present and
    non-null, and that `kind` is one of `_INFO_KIND_VALUES_4`. A
    caller that has no real default for a field it EXPECTS the frozen
    loader to have already supplied (e.g. `tensor_digest`, or
    `loading_info` on a real weight load) passes `None` for it: if the
    loader really did supply it, `None` never overrides; if it did
    not, this raises rather than papering over the gap with a made-up
    value."""
    info = dict(info)
    defaults = {"commit": commit, "revision": revision, "repo": repo, "kind": kind,
                "config_source": config_source, "n_hidden": n_hidden,
                "loading_info": loading_info}
    for field, value in defaults.items():
        if info.get(field) is None and value is not None:
            info[field] = value
    missing = [f for f in _INFO_CONTRACT_FIELDS_4 if info.get(f) is None]
    if missing:
        raise ValueError(f"info is missing required field(s) {missing} after _complete_info")
    if info["kind"] not in _INFO_KIND_VALUES_4:
        raise ValueError(f"info[\"kind\"] {info['kind']!r} is not one of {_INFO_KIND_VALUES_4}")
    return info


def _assert_n_hidden(info: dict, key: str) -> dict:
    pin = N_HIDDEN_PIN_4[key]
    got = info.get("n_hidden")
    if got != pin:
        raise ValueError(f"{key}: n_hidden {got!r} != the pinned {pin}")
    return info


def load_key_4(key: str, *, cache_root=CKPT_CACHE_4, device: str = "mps"):
    """MODEL CONTACT. Dispatches one of `STAGE1_KEYS_4` to its family's
    own frozen loader (design's "Loader dispatch" table). Returns
    `(model, tok, info)`; `info["n_hidden"]` is asserted against
    `N_HIDDEN_PIN_4[key]` before returning. Never executed by a test."""
    import torch

    if key == "ref_pythia_12b" or key.startswith("ladder_pythia_"):
        size = "12b" if key == "ref_pythia_12b" else key[len("ladder_pythia_"):]
        repo = f"EleutherAI/pythia-{size}"
        commit = PYTHIA_COMMITS_4[size]
        if size in models_2b.PYTHIA_SHAS:
            tok, model = models_2b.load_pythia(size, device=device)
            info = {"tensor_digest": ck.tensor_digest(model)}
            info = _complete_info(info, commit=commit, revision="main", repo=repo, kind="2b",
                                  config_source=f"{repo}@{commit}",
                                  n_hidden=int(model.config.num_hidden_layers) + 1,
                                  loading_info=_ZERO_LOADING_INFO_4)
        else:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            tok = AutoTokenizer.from_pretrained(repo, revision=commit)
            tok.padding_side = "left"
            if tok.pad_token is None:
                tok.pad_token = tok.eos_token
            model, li = AutoModelForCausalLM.from_pretrained(
                repo, revision=commit, dtype=torch.float16, output_loading_info=True)
            counts = bi._check_loading_info(li, f"{repo}@{commit} (thin load)")
            model = model.to(device).eval()
            info = {"loading_info": counts, "tensor_digest": ck.tensor_digest(model)}
            info = _complete_info(info, commit=commit, revision="main", repo=repo, kind="thin",
                                  config_source=f"{repo}@{commit}",
                                  n_hidden=int(model.config.num_hidden_layers) + 1,
                                  loading_info=None)
        return model, tok, _assert_n_hidden(info, key)

    if key in ("endpoint_pythia_2.8b", "init_pythia_2.8b"):
        step = ENDPOINT_STEP_4["pythia_2.8b"] if key == "endpoint_pythia_2.8b" else 0
        m = ck.load_manifest(sha_pin=an2g.CHECKPOINTS_SHA256)
        entry = ck.entry_for(m, "2.8b", step)
        model, info = ck.load_checkpoint("2.8b", step, entry, cache_root=cache_root,
                                         device=device)
        tok = models_2b.load_tokenizer("2.8b")
        info = dict(info)
        info["tensor_digest"] = ck.tensor_digest(model)
        info["kind"] = "candidate"  # ck.load_checkpoint's own "kind" is the candidate FILE
                                    # FORMAT (e.g. "safetensors-shards"), not a loader-path
                                    # label — _complete_info would never override an
                                    # already-present value, so this must be set explicitly
        info = _complete_info(info, commit=entry["commit"], revision=entry["revision"],
                              repo=bg.REPO_OF["2.8b"], kind="candidate",
                              config_source=None,
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, key)

    if key == "ref_olmo2_7b":
        m = bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256)
        entry = bi.entry_main(m, bi.REPO_7B)
        model, tok, info = bi.load_thin(bi.REPO_7B, entry["commit"], device=device)
        info = _complete_info(info, commit=entry["commit"], revision=entry["revision"],
                              repo=bi.REPO_7B, kind="thin",
                              config_source=f"{bi.REPO_7B}@{entry['commit']}",
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, key)

    if key == "endpoint_olmo2_7b":
        m = bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256)
        entry = bi.entry_7b(m, ENDPOINT_STEP_4["olmo2_7b"])
        model, tok, info = bi.load_thin(bi.REPO_7B, entry["commit"], device=device)
        info = _complete_info(info, commit=entry["commit"], revision=entry["revision"],
                              repo=bi.REPO_7B, kind="thin",
                              config_source=f"{bi.REPO_7B}@{entry['commit']}",
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, key)

    if key == "twin_olmo2_7b":
        m = bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256)
        entry = bi.entry_7b(m, ENDPOINT_STEP_4["olmo2_7b"])
        model, info = bi.load_twin_7b(device=device)
        tok = bi.load_tokenizer(bi.REPO_7B, entry["commit"])
        info = _complete_info(info, commit=entry["commit"], revision=bi.TWIN, repo=bi.REPO_7B,
                              kind="from_config",
                              config_source=f"{bi.REPO_7B}@{entry['commit']}",
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=_ZERO_LOADING_INFO_4)
        return model, tok, _assert_n_hidden(info, key)

    if key == "ref_smollm3_3b":
        m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
        e = bm.entry_base_3b(m)
        model, tok, info = bm.load_thin_3b(e["repo"], e["commit"], device=device)
        info = _complete_info(info, commit=e["commit"], revision=e["revision"], repo=e["repo"],
                              kind="thin", config_source=f"{e['repo']}@{e['commit']}",
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, key)

    if key == "endpoint_smollm3_3b":
        m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
        e = bm.entry_3b(m, ENDPOINT_STEP_4["smollm3_3b"])
        model, tok, info = bm.load_thin_3b(e["repo"], e["commit"], device=device)
        info = _complete_info(info, commit=e["commit"], revision=e["revision"], repo=e["repo"],
                              kind="thin", config_source=f"{e['repo']}@{e['commit']}",
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, key)

    if key == "twin_smollm3_3b":
        m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
        config_commit = m["twin"]["config_commit"]
        model, info = bm.load_twin_3b(config_commit=config_commit, device=device)
        tok = bm.load_tokenizer_3b(m["twin"]["repo"], config_commit)
        info = _complete_info(info, commit=config_commit, revision=bm.TWIN,
                              repo=m["twin"]["repo"], kind="from_config",
                              config_source=f"{m['twin']['repo']}@{config_commit}",
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=_ZERO_LOADING_INFO_4)
        return model, tok, _assert_n_hidden(info, key)

    if key == "ref_comma_7b":
        m = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
        entry = bn.entry_which_comma(m, "main")
        model, tok, info = bn.load_thin_comma(bn.REPO_COMMA, entry["commit"], device=device)
        info = _complete_info(info, commit=entry["commit"], revision=entry["revision"],
                              repo=bn.REPO_COMMA, kind="thin",
                              config_source=f"{bn.REPO_COMMA}@{entry['commit']}",
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, key)

    if key == "endpoint_comma_7b":
        m = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
        entry = bn.entry_which_comma(m, "stage1_final")
        model, tok, info = bn.load_thin_comma(bn.REPO_COMMA, entry["commit"], device=device)
        info = _complete_info(info, commit=entry["commit"], revision=entry["revision"],
                              repo=bn.REPO_COMMA, kind="thin",
                              config_source=f"{bn.REPO_COMMA}@{entry['commit']}",
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, key)

    if key == "twin_comma_7b":
        m = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
        config_commit = m["twin"]["config_commit"]
        model, info = bn.load_twin_comma(config_commit=config_commit, device=device)
        tok = bn.load_tokenizer_comma(bn.REPO_COMMA, config_commit)
        info = _complete_info(info, commit=config_commit, revision=bn.TWIN, repo=bn.REPO_COMMA,
                              kind="from_config",
                              config_source=f"{bn.REPO_COMMA}@{config_commit}",
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=_ZERO_LOADING_INFO_4)
        return model, tok, _assert_n_hidden(info, key)

    raise ValueError(f"{key!r} is not a recognised exp4 key")


def load_step_4(traj: str, step, *, cache_root=CKPT_CACHE_4, device: str = "mps"):
    """MODEL CONTACT. The candidate-file loader of the family (every
    branch's `info["kind"]` is `"candidate"`) — the sweep's own path.
    Never executed by a test."""
    if traj == "pythia_2.8b":
        m = ck.load_manifest(sha_pin=an2g.CHECKPOINTS_SHA256)
        entry = ck.entry_for(m, "2.8b", step)
        model, info = ck.load_checkpoint("2.8b", step, entry, cache_root=cache_root,
                                         device=device)
        tok = models_2b.load_tokenizer("2.8b")
        info = dict(info)
        info["kind"] = "candidate"
        info["tensor_digest"] = ck.tensor_digest(model)
        info = _complete_info(info, commit=entry["commit"], revision=entry["revision"],
                              repo=bg.REPO_OF["2.8b"], kind="candidate", config_source=None,
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, traj)

    if traj == "olmo2_7b":
        m = bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256)
        entry = bi.entry_7b(m, step)
        model, info = bi.load_checkpoint(bi.REPO_7B, entry, cache_root=cache_root,
                                         device=device, dtype=DTYPE_4)
        tok = bi.load_tokenizer(bi.REPO_7B, entry["commit"])
        info["kind"] = "candidate"
        info = _complete_info(info, commit=entry["commit"], revision=entry["revision"],
                              repo=bi.REPO_7B, kind="candidate", config_source=None,
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, traj)

    if traj == "smollm3_3b":
        m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
        entry = bm.entry_3b(m, step)
        model, info = bm.load_checkpoint_3b(entry, cache_root=cache_root, device=device,
                                            dtype=DTYPE_4)
        tok = bm.load_tokenizer_3b(entry["repo"], entry["commit"])
        info["kind"] = "candidate"
        info = _complete_info(info, commit=entry["commit"], revision=entry["revision"],
                              repo=entry["repo"], kind="candidate", config_source=None,
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, traj)

    if traj == "comma_7b":
        m = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
        entry = bn.entry_comma(m, step)
        model, info = bn.load_checkpoint_comma(entry, cache_root=cache_root, device=device,
                                               dtype=DTYPE_4)
        tok = bn.load_tokenizer_comma(bn.REPO_COMMA, entry["commit"])
        info["kind"] = "candidate"
        info = _complete_info(info, commit=entry["commit"], revision=entry["revision"],
                              repo=bn.REPO_COMMA, kind="candidate", config_source=None,
                              n_hidden=int(model.config.num_hidden_layers) + 1,
                              loading_info=None)
        return model, tok, _assert_n_hidden(info, traj)

    raise ValueError(f"{traj!r} is not an exp4 trajectory")


def free_step_4(traj: str, step, cache_root=CKPT_CACHE_4) -> None:
    """Frees the SAME cache key each family's own download used inside
    `load_step_4` (2i ruling 4) — Pythia keys by the raw step (2g's
    `_rev_dir`); OLMo-2/SmolLM3/Comma key by `entry["revision"]` (their
    `_cache_dir`s)."""
    if traj == "pythia_2.8b":
        ck.free_checkpoint("2.8b", step, cache_root)
        return
    if traj == "olmo2_7b":
        entry = bi.entry_7b(bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256), step)
        bi.free_checkpoint(bi.REPO_7B, entry["revision"], cache_root)
        return
    if traj == "smollm3_3b":
        entry = bm.entry_3b(
            bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256), step)
        bm.free_checkpoint_3b(entry["revision"], cache_root)
        return
    if traj == "comma_7b":
        entry = bn.entry_comma(
            bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256), step)
        bn.free_checkpoint_comma(entry["revision"], cache_root)
        return
    raise ValueError(f"{traj!r} is not an exp4 trajectory")


# -------------------------------------------------------------------- paths

def reference_dir(root, key: str) -> Path:
    return Path(root) / "results" / "reference" / str(key)


def load_record_path(root, key: str) -> Path:
    return reference_dir(root, key) / "_load.json"


def sets_path(root, key: str, rung: str) -> Path:
    return reference_dir(root, key) / "sets" / f"{rung}.npz"


def global_sets_path(root, key: str) -> Path:
    return reference_dir(root, key) / "global.npz"


def align_path(root, key: str) -> Path:
    return reference_dir(root, key) / "align.json"


def attested_path(root, key: str, rung: str) -> Path:
    return reference_dir(root, key) / "attested" / f"{rung}.npz"


def activations_path(root, key: str, rung: str) -> Path:
    return reference_dir(root, key) / "activations" / f"{rung}.npz"


def sweep_dir(root, traj: str) -> Path:
    return Path(root) / "results" / "sweep" / traj


def step_key(step) -> str:
    return f"step{int(step)}"


def unit_dir(root, traj: str, step) -> Path:
    return sweep_dir(root, traj) / step_key(step)


def gate1_path(root, traj: str) -> Path:
    return sweep_dir(root, traj) / "gate1.json"


def halt_marker_path(root, traj: str) -> Path:
    return sweep_dir(root, traj) / "HALTED"


def eligibility_path(root) -> Path:
    return Path(root) / "results" / "reference" / "eligibility_4.json"


def power_path(root) -> Path:
    return Path(root) / "results" / "reference" / "power_4.json"


def verdict_path(root) -> Path:
    return Path(root) / "results" / "verdict.json"


def verdict_txt_path(root) -> Path:
    return Path(root) / "results" / "VERDICT.txt"


def key_dir_4(root, key_or_unit):
    """A key str -> `reference_dir`; a `(traj, step)` tuple/list ->
    `unit_dir`."""
    if isinstance(key_or_unit, (tuple, list)):
        traj, step = key_or_unit
        return unit_dir(root, traj, step)
    return reference_dir(root, key_or_unit)


# ------------------------------------------------------------------ records

def load_record_4(*, key, family, info, sites, d, render, batch_size, refs, pairing,
                  sets_sha, global_sha, attested_sha, activation_sha, committed_digest,
                  seconds, stack, git_sha, prereg_tag, threads_pinned=None) -> dict:
    """The `_load.json` record for a reference key or a sweep unit.
    `key` is a str for a reference key, a `[traj, step]` pair for a
    sweep unit (JSON has no tuples)."""
    return {
        "key": list(key) if isinstance(key, (tuple, list)) else key,
        "family": family,
        "commit": info.get("commit"),
        "revision": info.get("revision"),
        "repo": info.get("repo"),
        "kind": info.get("kind"),
        "config_source": info.get("config_source"),
        "n_hidden": info.get("n_hidden"),
        "loading_info": info.get("loading_info"),
        "tensor_digest": info.get("tensor_digest"),
        "sites": list(sites),
        "d": int(d),
        "render": render,
        "batch_size": int(batch_size),
        "refs": list(refs),
        "pairing": pairing,
        "sets_sha256": dict(sets_sha),
        "global_sha256": global_sha,
        "attested_sha256": dict(attested_sha) if attested_sha is not None else None,
        "activation_sha256": dict(activation_sha) if activation_sha is not None else None,
        "committed_digest": committed_digest,
        "seconds": round(float(seconds), 3),
        "stack": dict(stack),
        # Final review Minor 7: whether this process had the four BLAS
        # thread variables pinned to 1 when the k-NN sets were built.
        "threads_pinned": threads_pinned,
        "git_sha": git_sha,
        "prereg_tag": prereg_tag,
    }


def load_record_failures_4(rec: dict, *, key, expected_family, expected_render,
                           expected_batch, expected_committed_digest, expected_refs,
                           root) -> list:
    """Every plain field checked; `sets_sha256`/`global_sha256`
    re-hashed against the files on disk; `attested_sha256`/
    `activation_sha256` required PRESENT (their files may be absent for
    a sweep unit, where they are deleted after the gate-1 re-read)."""
    bad = []
    if rec.get("family") != expected_family:
        bad.append(f"{key}: family {rec.get('family')!r} != {expected_family!r}")
    if rec.get("render") != expected_render:
        bad.append(f"{key}: render {rec.get('render')!r} != {expected_render!r}")
    if rec.get("batch_size") != expected_batch:
        bad.append(f"{key}: batch_size {rec.get('batch_size')!r} != {expected_batch!r}")
    if rec.get("committed_digest") != expected_committed_digest:
        bad.append(f"{key}: committed_digest {rec.get('committed_digest')!r} != "
                   f"{expected_committed_digest!r}")
    # FREEZE F-1 (2i F-1 / 3d's lesson): `committed_digest` is the
    # runner's copy of the EXPECTATION; `tensor_digest` is the loader's
    # own MEASUREMENT of the weights that produced these activations.
    # Comparing only the former checks that the runner wrote the right
    # number down, not that the right checkpoint was loaded — design
    # §3.4 says "the alignment is read on the bytes the outcome came
    # from, or not at all", and the runner's own halt was, from the
    # analyzer's side, an attestation. Required wherever a committed
    # outcome digest exists (references and ladder sizes have none).
    if expected_committed_digest is not None \
            and rec.get("tensor_digest") != expected_committed_digest:
        bad.append(f"{key}: tensor_digest {rec.get('tensor_digest')!r} != the committed "
                   f"outcome's digest {expected_committed_digest!r} — the loader's own "
                   f"measurement, not the record's copy of the expectation (design §3.4)")
    if tuple(rec.get("refs") or ()) != tuple(expected_refs):
        bad.append(f"{key}: refs {rec.get('refs')!r} != {list(expected_refs)!r}")
    if rec.get("prereg_tag") != PREREG_TAG_4:
        bad.append(f"{key}: prereg_tag {rec.get('prereg_tag')!r} != {PREREG_TAG_4!r}")

    for field in _INFO_CONTRACT_FIELDS_4:
        if rec.get(field) is None:
            bad.append(f"{key}: {field} is not present on the record")
    if rec.get("kind") is not None and rec.get("kind") not in _INFO_KIND_VALUES_4:
        bad.append(f"{key}: kind {rec.get('kind')!r} is not one of {_INFO_KIND_VALUES_4}")

    d = key_dir_4(root, key)
    sets_sha = rec.get("sets_sha256") or {}
    for rung, want in sets_sha.items():
        p = d / "sets" / f"{rung}.npz"
        if not p.is_file():
            bad.append(f"{key}/{rung}: sets file missing on disk")
            continue
        got = bg.sha256_file(p)
        if got != want:
            bad.append(f"{key}/{rung}: sets sha {got} != the recorded {want}")

    global_sha = rec.get("global_sha256")
    if global_sha is not None:
        gp = d / "global.npz"
        if not gp.is_file():
            bad.append(f"{key}: global.npz missing on disk")
        elif bg.sha256_file(gp) != global_sha:
            bad.append(f"{key}: global sha {bg.sha256_file(gp)} != the recorded {global_sha}")

    if not rec.get("attested_sha256"):
        bad.append(f"{key}: attested_sha256 is not present on the record")
    if not rec.get("activation_sha256"):
        bad.append(f"{key}: activation_sha256 is not present on the record")
    return bad


def unit_complete_4(root, key_or_unit) -> bool:
    """`_load.json` + all 34 `sets/<rung>.npz` + `align.json` present,
    AND every sets sha the record carries matches the file on disk."""
    d = key_dir_4(root, key_or_unit)
    rec_path = d / "_load.json"
    if not rec_path.is_file() or not (d / "align.json").is_file():
        return False
    try:
        rec = json.loads(rec_path.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    sets_sha = rec.get("sets_sha256") or {}
    if set(sets_sha) != set(RUNGS):
        return False
    for rung in RUNGS:
        p = d / "sets" / f"{rung}.npz"
        if not p.is_file():
            return False
        if bg.sha256_file(p) != sets_sha[rung]:
            return False
    return True


# -------------------------------------------------------------------- gate 1

def gate1_record_4(*, traj, sweep_rec, reference_rec, sets_equal: dict,
                   activation_sha_equal: dict, attested_sha_equal: dict,
                   digest_equal: bool, seconds) -> dict:
    return {
        "traj": traj,
        "rungs": sorted(sets_equal),
        "sets_equal": dict(sets_equal),
        "activation_sha_equal": dict(activation_sha_equal),
        "attested_sha_equal": dict(attested_sha_equal),
        "digest_equal": bool(digest_equal),
        "sweep_commit": sweep_rec.get("commit"),
        "reference_commit": reference_rec.get("commit"),
        "sweep_digest": sweep_rec.get("tensor_digest"),
        "reference_digest": reference_rec.get("tensor_digest"),
        "seconds": round(float(seconds), 3),
        "prereg_tag": PREREG_TAG_4,
    }


def gate1_failures_4(g1: dict, *, traj) -> list:
    """Attested: every rung's `sets_equal`/`activation_sha_equal`/
    `attested_sha_equal` True, `digest_equal` True, all 34 rungs
    present, the prereg tag stamped."""
    bad = []
    rungs = g1.get("rungs") or []
    if sorted(rungs) != sorted(RUNGS):
        bad.append(f"gate 1 {traj}: rung list is not the full 34-rung sweep set")
    se, ae = g1.get("sets_equal", {}), g1.get("activation_sha_equal", {})
    tae = g1.get("attested_sha_equal", {})
    for r in RUNGS:
        if se.get(r) is not True:
            bad.append(f"gate 1 {traj}/{r}: sets_equal is not True")
        if ae.get(r) is not True:
            bad.append(f"gate 1 {traj}/{r}: activation_sha_equal is not True")
        if tae.get(r) is not True:
            bad.append(f"gate 1 {traj}/{r}: attested_sha_equal is not True")
    if g1.get("digest_equal") is not True:
        bad.append(f"gate 1 {traj}: digest_equal is not True")
    if g1.get("prereg_tag") != PREREG_TAG_4:
        bad.append(f"gate 1 {traj}: prereg_tag {g1.get('prereg_tag')!r} != {PREREG_TAG_4!r}")
    return bad


def gate1_rederive_4(root, traj: str) -> dict:
    """From bytes, not attestation: `reference/endpoint_<traj>/sets/
    <rung>.npz` vs `sweep/<traj>/step<endpoint>/sets/<rung>.npz`
    byte-equal per rung; the two `_load.json`s' `activation_sha256` per
    rung equal; the two records' `attested_sha256` per rung equal
    (design §3.7: identity on every (rung, site, position) — equal
    shas of the attested npz means the question-end/pooled sets are
    identical too, not only the committed prompt-end sets); `tensor_
    digest` equal."""
    ref_key = f"endpoint_{traj}"
    ref_dir = reference_dir(root, ref_key)
    sweep_d = unit_dir(root, traj, ENDPOINT_STEP_4[traj])

    sets_equal = {}
    for r in RUNGS:
        a = (ref_dir / "sets" / f"{r}.npz").read_bytes()
        b = (sweep_d / "sets" / f"{r}.npz").read_bytes()
        sets_equal[r] = (a == b)

    ref_rec = json.loads((ref_dir / "_load.json").read_text())
    sweep_rec = json.loads((sweep_d / "_load.json").read_text())
    ref_act = ref_rec.get("activation_sha256") or {}
    sweep_act = sweep_rec.get("activation_sha256") or {}
    activation_sha_equal = {r: (ref_act.get(r) is not None and ref_act.get(r) == sweep_act.get(r))
                            for r in RUNGS}
    ref_att = ref_rec.get("attested_sha256") or {}
    sweep_att = sweep_rec.get("attested_sha256") or {}
    attested_sha_equal = {r: (ref_att.get(r) is not None and ref_att.get(r) == sweep_att.get(r))
                          for r in RUNGS}
    digest_equal = bool(ref_rec.get("tensor_digest") is not None
                        and ref_rec.get("tensor_digest") == sweep_rec.get("tensor_digest"))
    return {"sets_equal": sets_equal, "activation_sha_equal": activation_sha_equal,
            "attested_sha_equal": attested_sha_equal,
            "digest_equal": digest_equal, "n_rungs": len(RUNGS)}


# --------------------------------------------------------- pins & binding

FROZEN_SHA256_4 = {
    REPO / "experiments/exp1/signatures/stats.py":
        "ceab3eb7f6daf9346b9231f0e4af7e458b43ba4e7361556aef926e1abde2611f",
    REPO / "experiments/exp2b/models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
    REPO / "experiments/exp2b/probe_starved.py":
        "e6c81df28e4a7e07db3a123e4b06d3c8a98a7d330cd726596d41b1136c4cd27b",
    REPO / "experiments/exp2b/splits.py":
        "49df4c62c3c3bd611b9cf49be46001c12220045a3611a39be5e2bc5b89ded6e0",
    REPO / "experiments/exp2c/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2c/battery/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2c/battery/base.py":
        "6d77c3c91c5ca0eb84e1a011ef64af0e04ade6fe8d1ad42d526be3a37fbacbb2",
    REPO / "experiments/exp2c/battery/family_map.py":
        "46477b37683c8ea0e1f2f219dce96858a0dcf91710b15cae45a8cf4c4c7ab375",
    REPO / "experiments/exp2c/battery/generators_controls.py":
        "baab6da475f90f8c07acb6d1eb317484bf36afeb40705684f43ecd5ec9fdade6",
    REPO / "experiments/exp2c/battery/generators_rescues.py":
        "d70215c89ffd58d3f18f9dcd99940c7e92655ba8185919f50b2090b7e900c257",
    REPO / "experiments/exp2c/battery/generators_rungs.py":
        "778bf30da104f71773c26aa909ef2fddcd81291676a2db5d30130581b8d162d0",
    REPO / "experiments/exp2c/battery/wordlists_2c.py":
        "f46c6092d6429a59b95531d1a58b1bbfc0576d692d1162b8dfd2b6daf051790f",
    REPO / "experiments/exp2c/harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    REPO / "experiments/exp2c/instrument.py":
        "c486213bfa4753a83593b5383e2c0c90a6379b156f59a236ceeac7d68961e052",
    REPO / "experiments/exp2c/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2c/run/power_table.py":
        "89816cf0e7e2418e748104dbc32fd50e12ded78988f2c2c04b05ff1a89c58da1",
    REPO / "experiments/exp2c/run/screen.py":
        "fef1814142955912066837fbd2119f5c2ae27fe31393ede890584313e2b06873",
    REPO / "experiments/exp2c/stats_bounds.py":
        "39057433f1d67cbbf803141dc25ee36cda9e96270b0634006c0fcab245ee49f8",
    REPO / "experiments/exp2d/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2d/analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    REPO / "experiments/exp2d/battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
    REPO / "experiments/exp2d/stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    REPO / "experiments/exp2f/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2f/analyze_2f.py":
        "79018ff34b6f41bd2a5e8fa0f922a2de567861750057a5eca1a3dad6cf3f61d3",
    REPO / "experiments/exp2f/collect_eval_2f.py":
        "189e3738471185b7205f106fdac9bc5da1d564caafc60e39f4d6e3546915d071",
    REPO / "experiments/exp2f/labels_2f.py":
        "8dc31850e5c47b7a1cc171b0388521ebe01005ddc123954c0073734cf9aaac25",
    REPO / "experiments/exp2f/make_referents_2f.py":
        "c08eec5cea9f49a05c6754c84b81e1cb8560537881b002faee02bcf085af1c10",
    REPO / "experiments/exp2f/probe_2f.py":
        "63c714d6e899dd9d6d5610a3d54c9254ec0749d03f44a703790d4a4354854f62",
    REPO / "experiments/exp2g/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2g/analyze_2g.py":
        "eab7c5b91d57351ee2a7adb0e85d71cb92cb4d6ed15d0bb90150c95c2076050e",
    REPO / "experiments/exp2g/battery_2g.py":
        "aca79dd71ee7dead3c0ce065945bb38eaf1b0b72b5d5f40698dabb0f5a9cf3c1",
    REPO / "experiments/exp2g/checkpoints_2g.py":
        "155fee3ec3933db33930d7ddadb99c02604d893205a8f8c037016cc18609fb10",
    REPO / "experiments/exp2g/collect_eval_2g.py":
        "392ab84e2bac360bf041858a4b991824a3bda9ca414e34d0f84e44b22610efaf",
    REPO / "experiments/exp2g/labels_2g.py":
        "d86e7cdb4dcc10257986e8a85824365972a75ba993be5a8fde8a825d68e3077d",
    REPO / "experiments/exp2g/predictor_2g.py":
        "3381b43a34fd1fb1f7ef57eb9d02a6a9e9ec41b3ffcadea425c37b86c1e92a4e",
    REPO / "experiments/exp2g/probe_2g.py":
        "63abc9e6518ac1ab53e4a70e0c716bccd357a11ea3fc2733de52e2ec4e23d451",
    REPO / "experiments/exp2g/stats_2g.py":
        "cf3c4c89c86fa43c5ba49d5c4be12eabad28ac65d9d12a43b1e31ef6e4bc195f",
    REPO / "experiments/exp2g/strata_2g.py":
        "ea0acbbdfde13655a6b89d3afcc981f348ee6312b4448b70d437f1e4d3f7f594",
    REPO / "experiments/exp2h/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2h/analyze_2h.py":
        "52733e8d4280fb41b76cda2dcac024299ce7dd61090f856ba3147c8098b871bf",
    REPO / "experiments/exp2h/battery_2h.py":
        "2d721cf85bbd85937f45a1135e8b5e102685ab424d8ab0dfada527bd8ab4e80a",
    REPO / "experiments/exp2i/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2i/analyze_2i.py":
        "85e482fea17e0706476243a0a98a7d2c32efebd6536c5255ae48e729b494c252",
    REPO / "experiments/exp2i/battery_2i.py":
        "e0a8d10cb4dde8a3af1a3e9b32447c407b43201513dc758d6cd9a8c38b5cdfcf",
    REPO / "experiments/exp2i/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2i/run/_common_2i.py":
        "5cc7c97f68b45656d6dbbb5fbf6d7d895d7b1d96e104df543f8c9f1691e5ad4f",
    REPO / "experiments/exp2j/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2j/analyze_2j.py":
        "976f1ff1f91affa2fc66d635e6b6d9a8aabfd21bdc7ccc38abfe87482ea09b13",
    REPO / "experiments/exp2j/functionals_2j.py":
        "39375f01de4b5bf06787175e25f7f85394844c005c3c4ea66f69954b1fe8bfce",
    REPO / "experiments/exp2k/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2k/battery_2k.py":
        "1066265d689573cc009c73df1b036a9453be7a807d79e153b53ccf52177eec0a",
    REPO / "experiments/exp2l/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2l/battery_2l.py":
        "c85726b9909dfe11dd6481b96e773ce27aa507d83ac05348e0125f79aae50b8b",
    REPO / "experiments/exp2m/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2m/battery_2m.py":
        "0c5e1f07f8881c537304b496240605b95027306962ec2e4f389b42843323bffd",
    REPO / "experiments/exp2n/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2n/battery_2n.py":
        "e85165bd0ca1dd9f93eb07c89b74851ea2413d32f7ef9e694082ade49170a3e8",
}   # Task 5: every module experiments/exp4 imports transitively outside experiments/exp4,
    # derived from tests/import_scan_4.py's scan; check_frozen_4 raises on drift.


def check_frozen_4() -> None:
    for path, want in FROZEN_SHA256_4.items():
        got = bg.sha256_file(path)
        if got != want:
            raise ValueError(f"frozen file {path} has sha256 {got}, expected {want} — "
                             f"exp2*/exp3* are closed and their code is exp4's instrument")


def require_prereg_4(*, tag_exists=None, blob_sha=None) -> dict:
    """2n's `require_prereg_2n` body (itself 2k's blob binding), on
    exp4's tag and instrument blobs."""
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_4):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_4} does not exist")
    bound = {}
    for rel in INSTRUMENT_BLOBS_4:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_4, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_4} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_4, "instrument_blobs": bound}


def reference_seal_paths_4(root) -> list:
    """Every committed file `REFERENCE_SEAL_TAG_4` binds, RELATIVE to
    `root`, sorted: for each of the 19 `STAGE1_KEYS_4`, `_load.json` +
    34 `sets/<rung>.npz` + `global.npz` + `align.json`; for each of the
    four `STAGE1_FIRST_UNITS_4` units, `_load.json` + 34 `sets/<rung>.
    npz` + `align.json` (no `global.npz`); plus `eligibility_4.json`
    and `power_4.json`. 19*37 + 4*36 + 2 = 849 paths."""
    root = Path(root)
    paths = []
    for key in STAGE1_KEYS_4:
        paths.append(load_record_path(root, key))
        for r in RUNGS:
            paths.append(sets_path(root, key, r))
        paths.append(global_sets_path(root, key))
        paths.append(align_path(root, key))
    for traj, step in STAGE1_FIRST_UNITS_4:
        d = unit_dir(root, traj, step)
        paths.append(d / "_load.json")
        for r in RUNGS:
            paths.append(d / "sets" / f"{r}.npz")
        paths.append(d / "align.json")
    paths.append(eligibility_path(root))
    paths.append(power_path(root))
    return sorted(p.relative_to(root) for p in paths)


if __name__ == "__main__":
    if "--scan" in sys.argv:
        out = refresh_pythia_inventory_4()
        print(json.dumps(out, indent=1, sort_keys=True))
        print("sha256", bg.sha256_file(HUB_INVENTORY_PYTHIA_PATH))
    elif "--rungs" in sys.argv:
        floors = bg.load_floors()
        battery = bt.load_battery()
        table = {}
        for traj in TRAJECTORIES_4:
            outcome = load_outcome_4(traj, battery=battery)
            rs = rung_sets_4(outcome, floors)
            fails = check_rung_set_pins_4(traj, rs)
            if fails:
                raise ValueError(f"{traj}: {fails}")
            table[traj] = rs
        print(json.dumps(table, indent=1, sort_keys=True))
    else:
        print("usage: python -m experiments.exp4.battery_4 --scan | --rungs")
