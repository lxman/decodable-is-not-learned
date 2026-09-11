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
T_CLEAR_PIN_4 = None  # Task 5 pins the literal {traj: {rung: step or None}}

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
            info = {"repo": repo, "commit": commit, "revision": "main", "kind": "2b",
                    "config_source": f"{repo}@{commit}", "loading_info": None,
                    "tensor_digest": ck.tensor_digest(model),
                    "n_hidden": int(model.config.num_hidden_layers) + 1}
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
            info = {"repo": repo, "commit": commit, "revision": "main", "kind": "thin",
                    "config_source": f"{repo}@{commit}", "loading_info": counts,
                    "tensor_digest": ck.tensor_digest(model),
                    "n_hidden": int(model.config.num_hidden_layers) + 1}
        return model, tok, _assert_n_hidden(info, key)

    if key in ("endpoint_pythia_2.8b", "init_pythia_2.8b"):
        step = ENDPOINT_STEP_4["pythia_2.8b"] if key == "endpoint_pythia_2.8b" else 0
        m = ck.load_manifest(sha_pin=an2g.CHECKPOINTS_SHA256)
        entry = ck.entry_for(m, "2.8b", step)
        model, info = ck.load_checkpoint("2.8b", step, entry, cache_root=cache_root,
                                         device=device)
        tok = models_2b.load_tokenizer("2.8b")
        info = dict(info)
        info["repo"] = bg.REPO_OF["2.8b"]
        info["kind"] = "candidate"
        info["tensor_digest"] = ck.tensor_digest(model)
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, key)

    if key == "ref_olmo2_7b":
        m = bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256)
        commit = bi.entry_main(m, bi.REPO_7B)["commit"]
        model, tok, info = bi.load_thin(bi.REPO_7B, commit, device=device)
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, key)

    if key == "endpoint_olmo2_7b":
        m = bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256)
        commit = bi.entry_7b(m, ENDPOINT_STEP_4["olmo2_7b"])["commit"]
        model, tok, info = bi.load_thin(bi.REPO_7B, commit, device=device)
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, key)

    if key == "twin_olmo2_7b":
        m = bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256)
        commit = bi.entry_7b(m, ENDPOINT_STEP_4["olmo2_7b"])["commit"]
        model, info = bi.load_twin_7b(device=device)
        tok = bi.load_tokenizer(bi.REPO_7B, commit)
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, key)

    if key == "ref_smollm3_3b":
        m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
        e = bm.entry_base_3b(m)
        model, tok, info = bm.load_thin_3b(e["repo"], e["commit"], device=device)
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, key)

    if key == "endpoint_smollm3_3b":
        m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
        e = bm.entry_3b(m, ENDPOINT_STEP_4["smollm3_3b"])
        model, tok, info = bm.load_thin_3b(e["repo"], e["commit"], device=device)
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, key)

    if key == "twin_smollm3_3b":
        m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
        model, info = bm.load_twin_3b(config_commit=m["twin"]["config_commit"], device=device)
        tok = bm.load_tokenizer_3b(m["twin"]["repo"], m["twin"]["config_commit"])
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, key)

    if key == "ref_comma_7b":
        m = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
        commit = bn.entry_which_comma(m, "main")["commit"]
        model, tok, info = bn.load_thin_comma(bn.REPO_COMMA, commit, device=device)
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, key)

    if key == "endpoint_comma_7b":
        m = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
        commit = bn.entry_which_comma(m, "stage1_final")["commit"]
        model, tok, info = bn.load_thin_comma(bn.REPO_COMMA, commit, device=device)
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, key)

    if key == "twin_comma_7b":
        m = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
        model, info = bn.load_twin_comma(config_commit=m["twin"]["config_commit"], device=device)
        tok = bn.load_tokenizer_comma(bn.REPO_COMMA, m["twin"]["config_commit"])
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, key)

    raise ValueError(f"{key!r} is not a recognised exp4 key")


def load_step_4(traj: str, step, *, cache_root=CKPT_CACHE_4, device: str = "mps"):
    """MODEL CONTACT. The candidate-file loader of the family — the
    sweep's own path. Never executed by a test."""
    if traj == "pythia_2.8b":
        m = ck.load_manifest(sha_pin=an2g.CHECKPOINTS_SHA256)
        entry = ck.entry_for(m, "2.8b", step)
        model, info = ck.load_checkpoint("2.8b", step, entry, cache_root=cache_root,
                                         device=device)
        tok = models_2b.load_tokenizer("2.8b")
        info = dict(info)
        info["repo"] = bg.REPO_OF["2.8b"]
        info["tensor_digest"] = ck.tensor_digest(model)
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, traj)

    if traj == "olmo2_7b":
        m = bi.load_manifest(sha_pin=bi.CHECKPOINTS_2I_SHA256)
        entry = bi.entry_7b(m, step)
        model, info = bi.load_checkpoint(bi.REPO_7B, entry, cache_root=cache_root,
                                         device=device, dtype=DTYPE_4)
        tok = bi.load_tokenizer(bi.REPO_7B, entry["commit"])
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, traj)

    if traj == "smollm3_3b":
        m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
        entry = bm.entry_3b(m, step)
        model, info = bm.load_checkpoint_3b(entry, cache_root=cache_root, device=device,
                                            dtype=DTYPE_4)
        tok = bm.load_tokenizer_3b(entry["repo"], entry["commit"])
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
        return model, tok, _assert_n_hidden(info, traj)

    if traj == "comma_7b":
        m = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
        entry = bn.entry_comma(m, step)
        model, info = bn.load_checkpoint_comma(entry, cache_root=cache_root, device=device,
                                               dtype=DTYPE_4)
        tok = bn.load_tokenizer_comma(bn.REPO_COMMA, entry["commit"])
        info["n_hidden"] = int(model.config.num_hidden_layers) + 1
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
                  seconds, stack, git_sha, prereg_tag) -> dict:
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
    if tuple(rec.get("refs") or ()) != tuple(expected_refs):
        bad.append(f"{key}: refs {rec.get('refs')!r} != {list(expected_refs)!r}")
    if rec.get("prereg_tag") != PREREG_TAG_4:
        bad.append(f"{key}: prereg_tag {rec.get('prereg_tag')!r} != {PREREG_TAG_4!r}")

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
                   activation_sha_equal: dict, digest_equal: bool, seconds) -> dict:
    return {
        "traj": traj,
        "rungs": sorted(sets_equal),
        "sets_equal": dict(sets_equal),
        "activation_sha_equal": dict(activation_sha_equal),
        "digest_equal": bool(digest_equal),
        "sweep_commit": sweep_rec.get("commit"),
        "reference_commit": reference_rec.get("commit"),
        "sweep_digest": sweep_rec.get("tensor_digest"),
        "reference_digest": reference_rec.get("tensor_digest"),
        "seconds": round(float(seconds), 3),
        "prereg_tag": PREREG_TAG_4,
    }


def gate1_failures_4(g1: dict, *, traj) -> list:
    """Attested: every rung's `sets_equal`/`activation_sha_equal` True,
    `digest_equal` True, all 34 rungs present, the prereg tag stamped."""
    bad = []
    rungs = g1.get("rungs") or []
    if sorted(rungs) != sorted(RUNGS):
        bad.append(f"gate 1 {traj}: rung list is not the full 34-rung sweep set")
    se, ae = g1.get("sets_equal", {}), g1.get("activation_sha_equal", {})
    for r in RUNGS:
        if se.get(r) is not True:
            bad.append(f"gate 1 {traj}/{r}: sets_equal is not True")
        if ae.get(r) is not True:
            bad.append(f"gate 1 {traj}/{r}: activation_sha_equal is not True")
    if g1.get("digest_equal") is not True:
        bad.append(f"gate 1 {traj}: digest_equal is not True")
    if g1.get("prereg_tag") != PREREG_TAG_4:
        bad.append(f"gate 1 {traj}: prereg_tag {g1.get('prereg_tag')!r} != {PREREG_TAG_4!r}")
    return bad


def gate1_rederive_4(root, traj: str) -> dict:
    """From bytes, not attestation: `reference/endpoint_<traj>/sets/
    <rung>.npz` vs `sweep/<traj>/step<endpoint>/sets/<rung>.npz`
    byte-equal per rung; the two `_load.json`s' `activation_sha256` per
    rung equal; `tensor_digest` equal."""
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
    digest_equal = bool(ref_rec.get("tensor_digest") is not None
                        and ref_rec.get("tensor_digest") == sweep_rec.get("tensor_digest"))
    return {"sets_equal": sets_equal, "activation_sha_equal": activation_sha_equal,
            "digest_equal": digest_equal, "n_rungs": len(RUNGS)}


# --------------------------------------------------------- pins & binding

FROZEN_SHA256_4: dict = {}   # Task 5 fills; check_frozen_4 raises on drift when non-empty


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
