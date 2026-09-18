# experiments/exp4c/battery_4c.py
"""Experiment 4c's foundation (design `experiment-4c-design.md`
§3.1-§3.2, §3.7, §3.9): constants, the pins to Experiment 4's and
Experiment 4b's closed trees, the two outcome readers (2h's Pythia
6.9b sweep, 2l's OLMo-2 13B sweep), the rung-set and clear-index pins
reproduced from the committed bits, the loader dispatch (including the
13B thin endpoint 2l never built), records stamped with the 4c tag,
the gate-1 checkers against the two gate-1 references, and the
preregistration binding.

Everything under `experiments/exp2*`, `experiments/exp3*`,
`experiments/exp4/` and `experiments/exp4b/` is FROZEN: read, never
edited. `battery_4.check_frozen_4()` covers exp4's own transitive
exp2*/exp3* pins; `EXP4_CLOSED_SHA256_4C` adds the seven files of
`experiments/exp4/` this module imports or reuses at their
`exp4-closed` content (2b's `EXP4_CLOSED_SHA256_4B` plus
`experiments/exp4/_threads_4.py`, which 4b's table does not carry);
`EXP4B_CLOSED_SHA256_4C` pins the three `experiments/exp4b/` files
(`__init__.py`, `battery_4b.py`, `placebo_4b.py`) at their
`exp4b-closed` content, the ones later tasks reuse for S4's placebo
machinery. `FROZEN_SHA256_4C` (Task 5) pins every other module the
import scan finds outside exp4's own table (2h, 2l, 2k, ...); it is
`None` here — `check_frozen_4c` raises until Task 5 fills it.

Zero model contact, zero network: `load_step_4c` and
`load_thin_endpoint_4c` import `huggingface_hub`/`torch`/
`transformers` lazily inside their own bodies; nothing here calls
them, and no test does."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP4C = Path(__file__).resolve().parent
EXPERIMENTS = EXP4C.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp4 import _threads_4  # noqa: F401,E402 (thread pin, before numpy)
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2h import analyze_2h as ah  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402
from experiments.exp4 import analyze_4 as a4  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402

RESULTS_4C = EXP4C / "results"

PREREG_TAG_4C = "exp4c-preregistered"
CLOSED_TAG_4C = "exp4c-closed"

INSTRUMENT_BLOBS_4C = (
    "experiments/exp4c/analyze_4c.py",
    "experiments/exp4c/battery_4c.py",
    "experiments/exp4c/rank_4c.py",
    "experiments/exp4c/collect_4c.py",
    "experiments/exp4c/power_4c.py",
    "experiments/exp4c/run/sweep_4c.py",
    "experiments/exp4c/results/power_4c.json",
)

# The seven files of `experiments/exp4/` pinned to their content at tag
# `exp4-closed` — 4b's own pin (`battery_4b.EXP4_CLOSED_SHA256_4B`)
# plus `_threads_4.py`, which 4b's table never needed (4b makes no
# model contact and so never imports the thread-pinning module). Both
# literals recomputed 2026-09-18 with:
#   /opt/homebrew/bin/git show exp4-closed:experiments/exp4/_threads_4.py | shasum -a 256
EXP4_CLOSED_SHA256_4C = dict(battery_4b.EXP4_CLOSED_SHA256_4B)
EXP4_CLOSED_SHA256_4C["experiments/exp4/_threads_4.py"] = \
    "8cb23d6de4d1a6f57a05cdde83fa2f1b13150867046132836baddaa0db0d5667"

# The three files of `experiments/exp4b/` pinned to their content at
# tag `exp4b-closed` — the placebo machinery (S4) reuses `placebo_4b`,
# which imports `battery_4b`, which imports its package `__init__.py`.
# Recomputed 2026-09-18 with:
#   for f in __init__.py battery_4b.py placebo_4b.py; do
#     /opt/homebrew/bin/git show exp4b-closed:experiments/exp4b/$f | shasum -a 256
#   done
EXP4B_CLOSED_SHA256_4C = {
    "experiments/exp4b/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiments/exp4b/battery_4b.py":
        "e5f947c7f3d508768c846cbee0e4a43e9f787a5acf1c98e7addd176d6473ac57",
    "experiments/exp4b/placebo_4b.py":
        "f24b9a0c9cd45324bf6046ba0f0267da7908922b4972ace79b9c5b94b8ff1b88",
}

# Task 5's import scan (`tests/import_scan_4c.py`), run on the REAL
# pre-campaign tree with `tag_exists`/`blob_sha` stubbed so `run()`
# reaches as deep as the tree allows (through the discovery gate and
# the power record's byte reproduction, refusing at "4c gate 1
# pythia_6.9b: record missing"): EMPTY — every module `experiments/
# exp4c` imports outside itself (2h's battery_2h/analyze_2h, 2l's
# battery_2l, plus everything `rank_4c.discovery_set_4c`/`power_4c`
# touch) is already covered by `battery_4.FROZEN_SHA256_4` (Exp 4's own
# ladder reference reads 2h's 6.9b table already) or by
# `EXP4_CLOSED_SHA256_4C`/`EXP4B_CLOSED_SHA256_4C` above — verified
# directly (2h/2l modules already present in `battery_4.
# FROZEN_SHA256_4`'s covered set before this scan ever ran).
# `check_frozen_4c` no longer raises "not pinned" once this is a real
# (even if empty) dict.
FROZEN_SHA256_4C = {}

RUNG_TYPE_4C = a4.RUNG_TYPE_4
FAMILY_OF = bt.FAMILY_OF
RUNGS = bt.RUNGS
N_ITEMS = bt.N_ITEMS

TRAJECTORIES_4C = ("pythia_6.9b", "olmo2_13b")
FAMILY_OF_TRAJ_4C = {"pythia_6.9b": "pythia", "olmo2_13b": "olmo2"}

_REFERENCES_4C = ("ref_pythia_12b", "ref_olmo2_7b", "ref_smollm3_3b", "ref_comma_7b")
_FAMILY_OF_REF_4C = {"ref_pythia_12b": "pythia", "ref_olmo2_7b": "olmo2",
                     "ref_smollm3_3b": "smollm3", "ref_comma_7b": "comma"}
REFS_FOR_4C = {traj: tuple(r for r in _REFERENCES_4C if _FAMILY_OF_REF_4C[r] != FAMILY_OF_TRAJ_4C[traj])
              for traj in TRAJECTORIES_4C}

RENDER_4C = {"pythia": "plain", "olmo2": "plain"}
DTYPE_4C = "float16"
BATCH_4C = {"pythia_6.9b": 16, "olmo2_13b": 16, "endpoint_olmo2_13b": 16}

THIN_ENDPOINT_KEY_4C = "endpoint_olmo2_13b"
GATE1_REFERENCE_4C = {"pythia_6.9b": ("exp4", "ladder_pythia_6.9b"),
                      "olmo2_13b": ("exp4c", "endpoint_olmo2_13b")}

N_HIDDEN_PIN_4C = {"pythia_6.9b": 33, "olmo2_13b": 41, "endpoint_olmo2_13b": 41}
SITE_COUNT_PIN_4C = {33: 12, 41: 15}

for _n, _c in SITE_COUNT_PIN_4C.items():
    if len(metric_4.sites_4(_n)) != _c:
        raise RuntimeError(f"SITE_COUNT_PIN_4C[{_n}] = {_c} but metric_4.sites_4 gives "
                           f"{len(metric_4.sites_4(_n))}")
del _n, _c

# ------------------------------------------------------------------- grid

# design §3.2 / dial c: 2h's/2l's own TRAINED-point grids, read fresh
# through their manifests at their pins in `manifests_4c()` and
# asserted equal to these literals. `INIT_STEP_4C` (0) is a real
# checkpoint on both runs — the init referent for gate 0, never a grid
# point (both manifests carry a step-0 entry, asserted below).
GRID_4C = {
    "pythia_6.9b": (1000, 2000, 4000, 8000, 10000, 16000, 20000, 30000, 32000,
                    40000, 50000, 60000, 64000, 70000, 80000, 90000, 100000,
                    110000, 120000, 130000, 140000, 143000),
    "olmo2_13b": (1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000, 192000,
                  256000, 320000, 384000, 448000, 512000, 576000, 596057),
}
ENDPOINT_STEP_4C = {traj: GRID_4C[traj][-1] for traj in TRAJECTORIES_4C}
FIRST_STEP_4C = {traj: GRID_4C[traj][0] for traj in TRAJECTORIES_4C}
INIT_STEP_4C = 0

SWEEP_ROOT_4C = {
    "pythia_6.9b": bh.sweep_dir_2h(bh.EXP2H),
    "olmo2_13b": bl.sweep_dir(bl.EXP2L),
}

CKPT_CACHE_4C = Path.home() / "emergence-lab" / "ckpt_cache_4c"


# ------------------------------------------------------------- manifests

def manifests_4c() -> dict:
    """Each trajectory's own manifest, read at its pin, grid re-asserted
    equal to `GRID_4C`, and the real step-0 entry re-asserted present
    (the init referent for gate 0 on both runs)."""
    m69 = bh.load_manifest_69(bh.CHECKPOINTS_PATH_69, sha_pin=ah.CHECKPOINTS_2H_SHA256)
    m13 = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    if tuple(m69["trained_steps"]) != GRID_4C["pythia_6.9b"]:
        raise ValueError(f"2h manifest trained_steps {m69['trained_steps']} != GRID_4C")
    if tuple(m13["grid_13b"]) != GRID_4C["olmo2_13b"]:
        raise ValueError(f"2l manifest grid_13b {m13['grid_13b']} != GRID_4C")
    if "0" not in m69["entries"] or "0" not in m13["entries_13b"]:
        raise ValueError("a manifest lacks its step-0 entry (the real init referent)")
    return {"pythia_6.9b": m69, "olmo2_13b": m13}


# --------------------------------------------------- the committed outcome

def committed_step_digest_4c(traj: str, step) -> str:
    """`<SWEEP_ROOT_4C[traj]>/step<step>/_checkpoint.json`'s `digest` —
    `step=0` reads the real init checkpoint on both runs."""
    p = SWEEP_ROOT_4C[traj] / f"step{int(step)}" / "_checkpoint.json"
    digest = json.loads(p.read_text()).get("digest")
    if not digest:
        raise ValueError(f"{p}: no digest")
    return digest


def load_outcome_4c(traj: str, *, battery=None) -> dict:
    """The committed per-checkpoint argmax outcome over `GRID_4C[traj]`
    (`battery_4.load_outcome_4`'s body over `SWEEP_ROOT_4C`/`GRID_4C`
    with the record checks 2h's and 2l's own records support: rung,
    step, n, bits, items_sha256, dtype, n_shots; `render` absent or
    "plain"). Exactly `battery_4.load_outcome_4`'s return shape:
    `{"steps": [...], "per_step": {step: {"digest": str, "rungs":
    {rung: {"correct": int, "n": int, "bits": [...]}}}}}`."""
    battery = battery or bt.load_battery()
    steps, per_step = list(GRID_4C[traj]), {}
    for step in steps:
        d = SWEEP_ROOT_4C[traj] / f"step{int(step)}"
        digest = json.loads((d / "_checkpoint.json").read_text()).get("digest")
        if not digest:
            raise ValueError(f"{d}/_checkpoint.json: no digest")
        rungs = {}
        for rung in RUNGS:
            p = d / f"{rung}.json"
            rec = json.loads(p.read_text())
            if rec.get("rung") != rung:
                raise ValueError(f"{p}: rung {rec.get('rung')!r}")
            if int(rec.get("step")) != int(step):
                raise ValueError(f"{p}: step {rec.get('step')!r} != {step}")
            if rec.get("n") != N_ITEMS:
                raise ValueError(f"{p}: n {rec.get('n')!r}")
            bits = rec.get("bits")
            if not isinstance(bits, list) or len(bits) != N_ITEMS:
                raise ValueError(f"{p}: bits")
            if rec.get("items_sha256") != battery[rung]["items_sha256"]:
                raise ValueError(f"{p}: items_sha256")
            if rec.get("render", "plain") != RENDER_4C[FAMILY_OF_TRAJ_4C[traj]]:
                raise ValueError(f"{p}: render {rec.get('render')!r}")
            if rec.get("dtype") != DTYPE_4C:
                raise ValueError(f"{p}: dtype {rec.get('dtype')!r}")
            if int(rec.get("n_shots", -1)) != len(battery[rung]["shots"]):
                raise ValueError(f"{p}: n_shots")
            rungs[rung] = {"correct": int(rec["correct"]), "n": int(rec["n"]), "bits": list(bits)}
        per_step[step] = {"digest": digest, "rungs": rungs}
    return {"steps": steps, "per_step": per_step}


rung_sets_4c = battery_4.rung_sets_4


def clear_indices_4c(rung_sets: dict, steps: list) -> dict:
    """`{rung in R: 0-based index of its t_clear on `steps`}`."""
    return {r: steps.index(rung_sets["t_clear"][r]) for r in rung_sets["R"]}


# design §3.2's own printed rung-set / clear-index literals, reproduced
# from `python -m experiments.exp4c.battery_4c --rungs` on the committed
# 2h/2l sweep trees (zero model contact — file reads only) and pasted
# once. `check_rung_set_pins_4c` re-asserts them on every real run.
RUNG_SET_PIN_4C = {
    "pythia_6.9b": {
        "R": ("add3_mid", "add_base8", "antonym", "antonym6", "arith_next",
              "count_div13", "odd6", "sub_base8"),
        "transient": ("odd_one_out", "sub3_mid"),
        "flat": ("add4_mid", "base12_digitsum", "base13", "base7", "caesar",
                 "caesar_len8", "clock24", "clock24_d999", "collatz_step2",
                 "count_div7", "hamming12", "isqrt_gap", "median5", "median7",
                 "mod13", "mod13_comp", "mod17", "mod19", "oct2dec",
                 "quad_next", "rev_string7", "reverse_string", "roman_sum7",
                 "sub4_mid"),
    },
    "olmo2_13b": {
        "R": ("add3_mid", "add4_mid", "add_base8", "antonym", "antonym6",
              "arith_next", "count_div13", "median5", "median7", "oct2dec",
              "odd6", "odd_one_out", "quad_next", "rev_string7",
              "reverse_string", "sub3_mid", "sub4_mid", "sub_base8"),
        "transient": ("clock24_d999",),
        "flat": ("base12_digitsum", "base13", "base7", "caesar", "caesar_len8",
                 "clock24", "collatz_step2", "count_div7", "hamming12",
                 "isqrt_gap", "mod13", "mod13_comp", "mod17", "mod19",
                 "roman_sum7"),
    },
}

CLEAR_INDEX_PIN_4C = {
    "pythia_6.9b": {
        "arith_next": 5, "antonym": 6, "antonym6": 6, "odd6": 6,
        "sub_base8": 11, "add3_mid": 13, "add_base8": 13, "count_div13": 21,
    },
    "olmo2_13b": {
        "add3_mid": 6, "add4_mid": 6, "add_base8": 4, "antonym": 4,
        "antonym6": 4, "arith_next": 4, "count_div13": 15, "median5": 6,
        "median7": 6, "oct2dec": 6, "odd6": 5, "odd_one_out": 6,
        "quad_next": 7, "rev_string7": 11, "reverse_string": 4,
        "sub3_mid": 5, "sub4_mid": 6, "sub_base8": 4,
    },
}


def check_rung_set_pins_4c(traj, rung_sets, steps) -> list:
    """`[]` when `rung_sets`' R/flat/transient and clear indices agree
    with the pins above."""
    bad, pin = [], RUNG_SET_PIN_4C[traj]
    for k in ("R", "flat", "transient"):
        if tuple(sorted(rung_sets[k])) != tuple(sorted(pin[k])):
            bad.append(f"{traj}: {k} {sorted(rung_sets[k])} != pinned {sorted(pin[k])}")
    if clear_indices_4c(rung_sets, steps) != CLEAR_INDEX_PIN_4C[traj]:
        bad.append(f"{traj}: clear indices != pinned")
    return bad


def flat_arith_4c(rung_sets) -> list:
    """flat ∩ arithmetic — the §3.5 type-modifier's flat pool."""
    return [r for r in rung_sets["flat"] if RUNG_TYPE_4C[r] == "arithmetic"]


# ------------------------------------------------------------------ loaders
# (MODEL CONTACT — never executed by a test.)

def load_step_4c(traj, step, *, cache_root=CKPT_CACHE_4C, device="mps"):
    """MODEL CONTACT. The candidate-file loader of the trajectory's own
    family — the sweep's own path. Never executed by a test."""
    if traj == "pythia_6.9b":
        m = bh.load_manifest_69(bh.CHECKPOINTS_PATH_69, sha_pin=ah.CHECKPOINTS_2H_SHA256)
        entry = bh.entry_69(m, step)
        model, info = bh.load_checkpoint_69(int(step), entry, cache_root=cache_root, device=device)
        from models import load_tokenizer            # exp2b's, via battery_2d's sys.path (2h's own route)
        tok = load_tokenizer(bh.SIZE)
        info = dict(info)
        info["kind"] = "candidate"
        info["tensor_digest"] = ck.tensor_digest(model)
        info = battery_4._complete_info(info, commit=entry["commit"], revision=entry["revision"],
                                        repo=bh.REPO_69, kind="candidate", config_source=None,
                                        n_hidden=int(model.config.num_hidden_layers) + 1,
                                        loading_info=None)
    elif traj == "olmo2_13b":
        m = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
        entry = bl.entry_13b(m, step)
        model, info = bl.load_checkpoint_13b(entry, cache_root=cache_root, device=device,
                                             dtype=DTYPE_4C)
        tok = bl.load_tokenizer_13b(entry["commit"])
        info = dict(info)
        info["kind"] = "candidate"
        info = battery_4._complete_info(info, commit=entry["commit"], revision=entry["revision"],
                                        repo=bl.REPO_13B, kind="candidate", config_source=None,
                                        n_hidden=int(model.config.num_hidden_layers) + 1,
                                        loading_info=None)
    else:
        raise ValueError(f"{traj!r} is not an exp4c trajectory")
    if info["n_hidden"] != N_HIDDEN_PIN_4C[traj]:
        raise ValueError(f"{traj}: n_hidden {info['n_hidden']} != pinned {N_HIDDEN_PIN_4C[traj]}")
    return model, tok, info


def load_thin_endpoint_4c(key, *, device="mps"):
    """MODEL CONTACT. The second loader path for the OLMo-2 13B endpoint
    (design §3.7 gate 4's two-loader-paths requirement, B-1: Exp 4 holds
    no committed 13B reference table). `key` must be
    `THIN_ENDPOINT_KEY_4C`. Never executed by a test."""
    if key != THIN_ENDPOINT_KEY_4C:
        raise ValueError(f"{key!r} has no thin endpoint path")
    m = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    entry = bl.entry_13b(m, ENDPOINT_STEP_4C["olmo2_13b"])
    model, tok, info = bl.load_thin_13b(entry["commit"], device=device, dtype=DTYPE_4C)
    info = battery_4._complete_info(info, commit=entry["commit"], revision=entry["revision"],
                                    repo=bl.REPO_13B, kind="thin",
                                    config_source=f"{bl.REPO_13B}@{entry['commit']}",
                                    n_hidden=int(model.config.num_hidden_layers) + 1,
                                    loading_info=None)
    if info["n_hidden"] != N_HIDDEN_PIN_4C[key]:
        raise ValueError(f"{key}: n_hidden {info['n_hidden']}")
    return model, tok, info


def free_step_4c(traj, step, cache_root=CKPT_CACHE_4C) -> None:
    if traj == "pythia_6.9b":
        bh.free_69(int(step), cache_root)
        return
    if traj == "olmo2_13b":
        entry = bl.entry_13b(bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256), step)
        bl.free_checkpoint_13b(entry["revision"], cache_root)
        return
    raise ValueError(traj)


# ------------------------------------------------------------------ records

def expected_fields_4c(key) -> dict:
    """`{family, render, batch, refs, n_hidden, committed_digest}` for a
    `(traj, step)` unit (a tuple/list — step 0 included) or
    `THIN_ENDPOINT_KEY_4C`."""
    if isinstance(key, (tuple, list)):
        traj, step = key
        fam = FAMILY_OF_TRAJ_4C[traj]
        return dict(family=fam, render=RENDER_4C[fam], batch=BATCH_4C[traj], refs=REFS_FOR_4C[traj],
                    n_hidden=N_HIDDEN_PIN_4C[traj], committed_digest=committed_step_digest_4c(traj, step))
    if key == THIN_ENDPOINT_KEY_4C:
        traj = "olmo2_13b"
        fam = "olmo2"
        return dict(family=fam, render=RENDER_4C[fam], batch=BATCH_4C[key], refs=REFS_FOR_4C[traj],
                    n_hidden=N_HIDDEN_PIN_4C[key],
                    committed_digest=committed_step_digest_4c(traj, ENDPOINT_STEP_4C[traj]))
    raise ValueError(f"{key!r} is not an exp4c key")


def load_record_failures_4c(rec, *, key, root) -> list:
    """`battery_4.load_record_failures_4`'s body with two deltas: the
    expected fields come from `expected_fields_4c(key)` (this module's
    own trajectories/keys, not exp4's), and the tag is `PREREG_TAG_4C`."""
    e = expected_fields_4c(key)
    bad = []
    for f_, want in (("family", e["family"]), ("render", e["render"]),
                     ("batch_size", e["batch"]), ("committed_digest", e["committed_digest"])):
        if rec.get(f_) != want:
            bad.append(f"{key}: {f_} {rec.get(f_)!r} != {want!r}")
    if rec.get("tensor_digest") != e["committed_digest"]:
        bad.append(f"{key}: tensor_digest {rec.get('tensor_digest')!r} != the committed "
                   f"outcome's digest (the loader's own measurement)")
    if tuple(rec.get("refs") or ()) != tuple(e["refs"]):
        bad.append(f"{key}: refs {rec.get('refs')!r}")
    if rec.get("prereg_tag") != PREREG_TAG_4C:
        bad.append(f"{key}: prereg_tag {rec.get('prereg_tag')!r} != {PREREG_TAG_4C!r}")
    for f_ in battery_4._INFO_CONTRACT_FIELDS_4:
        if rec.get(f_) is None:
            bad.append(f"{key}: {f_} is not present on the record")
    if rec.get("kind") is not None and rec.get("kind") not in battery_4._INFO_KIND_VALUES_4:
        bad.append(f"{key}: kind {rec.get('kind')!r}")
    d = battery_4.key_dir_4(root, key)
    for rung, want in (rec.get("sets_sha256") or {}).items():
        p = d / "sets" / f"{rung}.npz"
        if not p.is_file():
            bad.append(f"{key}/{rung}: sets file missing on disk")
            continue
        if bg.sha256_file(p) != want:
            bad.append(f"{key}/{rung}: sets sha != the recorded")
    if not rec.get("attested_sha256"):
        bad.append(f"{key}: attested_sha256 is not present on the record")
    if not rec.get("activation_sha256"):
        bad.append(f"{key}: activation_sha256 is not present on the record")
    return bad


# -------------------------------------------------------------------- gate 1

def gate1_reference_dir_4c(root, root4, traj) -> Path:
    """`GATE1_REFERENCE_4C[traj]` names which root ("exp4" or "exp4c")
    and which reference key gate 1 compares the sweep endpoint against."""
    where, key = GATE1_REFERENCE_4C[traj]
    return battery_4.reference_dir(root4 if where == "exp4" else root, key)


def gate1_rederive_4c(root, root4, traj) -> dict:
    """From bytes, not attestation: the reference dir's `sets/<rung>.npz`
    vs the sweep's endpoint unit, byte-equal per rung; the two
    `_load.json`s' `attested_sha256` per rung equal; `tensor_digest`
    equal."""
    ref_dir = gate1_reference_dir_4c(root, root4, traj)
    sweep_d = battery_4.unit_dir(root, traj, ENDPOINT_STEP_4C[traj])
    sets_equal = {r: (ref_dir / "sets" / f"{r}.npz").read_bytes() ==
                  (sweep_d / "sets" / f"{r}.npz").read_bytes() for r in RUNGS}
    ref_rec = json.loads((ref_dir / "_load.json").read_text())
    sweep_rec = json.loads((sweep_d / "_load.json").read_text())
    ra, sa = ref_rec.get("attested_sha256") or {}, sweep_rec.get("attested_sha256") or {}
    attested_sha_equal = {r: (ra.get(r) is not None and ra.get(r) == sa.get(r)) for r in RUNGS}
    digest_equal = bool(ref_rec.get("tensor_digest") is not None and
                        ref_rec.get("tensor_digest") == sweep_rec.get("tensor_digest"))
    return {"sets_equal": sets_equal, "attested_sha_equal": attested_sha_equal,
            "digest_equal": digest_equal, "n_rungs": len(RUNGS)}


def gate1_record_4c(*, traj, sweep_rec, reference_rec, rederived, seconds) -> dict:
    where, key = GATE1_REFERENCE_4C[traj]
    return {"traj": traj, "rungs": sorted(rederived["sets_equal"]),
            "n_rungs": int(rederived["n_rungs"]),
            "sets_equal": dict(rederived["sets_equal"]),
            "attested_sha_equal": dict(rederived["attested_sha_equal"]),
            "digest_equal": bool(rederived["digest_equal"]), "reference_key": key,
            "reference_root": where, "sweep_commit": sweep_rec.get("commit"),
            "reference_commit": reference_rec.get("commit"),
            "sweep_digest": sweep_rec.get("tensor_digest"),
            "reference_digest": reference_rec.get("tensor_digest"),
            "sweep_kind": sweep_rec.get("kind"), "reference_kind": reference_rec.get("kind"),
            "seconds": round(float(seconds), 3), "prereg_tag": PREREG_TAG_4C}


def gate1_failures_4c(g1, *, traj) -> list:
    """Attested: every rung's `sets_equal`/`attested_sha_equal` True,
    `digest_equal` True, all 34 rungs present, the right reference key
    and root, the prereg tag stamped."""
    bad = []
    where, key = GATE1_REFERENCE_4C[traj]
    if sorted(g1.get("rungs") or []) != sorted(RUNGS):
        bad.append(f"gate 1 {traj}: rung list is not the full 34")
    if g1.get("n_rungs") != len(RUNGS):
        bad.append(f"gate 1 {traj}: n_rungs {g1.get('n_rungs')!r} != {len(RUNGS)} (coverage)")
    for r in RUNGS:
        if (g1.get("sets_equal") or {}).get(r) is not True:
            bad.append(f"gate 1 {traj}/{r}: sets_equal is not True")
        if (g1.get("attested_sha_equal") or {}).get(r) is not True:
            bad.append(f"gate 1 {traj}/{r}: attested_sha_equal is not True")
    if g1.get("digest_equal") is not True:
        bad.append(f"gate 1 {traj}: digest_equal is not True")
    if g1.get("reference_key") != key or g1.get("reference_root") != where:
        bad.append(f"gate 1 {traj}: reference {g1.get('reference_root')}/{g1.get('reference_key')} "
                   f"!= {where}/{key}")
    if g1.get("prereg_tag") != PREREG_TAG_4C:
        bad.append(f"gate 1 {traj}: prereg_tag")
    return bad


def exp4_reference_paths_4c(root4) -> list:
    """The five keys' seal-bound files exp4c reuses from Exp 4's
    committed reference tree (the three cross-family refs plus
    `ladder_pythia_6.9b`, the 6.9b gate-1 reference — the union of
    `REFS_FOR_4C`'s values): 37 files each (`_load.json` + 34
    `sets/<rung>.npz` + `global.npz` + `align.json`), 185 total."""
    keys = tuple(sorted({r for refs in REFS_FOR_4C.values() for r in refs})) + ("ladder_pythia_6.9b",)
    out = []
    for key in keys:
        out.append(battery_4.load_record_path(root4, key))
        out += [battery_4.sets_path(root4, key, r) for r in RUNGS]
        out.append(battery_4.global_sets_path(root4, key))
        out.append(battery_4.align_path(root4, key))
    return out


# --------------------------------------------------------- pins & binding

def check_exp4_closed_4c() -> None:
    battery_4.check_frozen_4()
    bad = []
    for table in (EXP4_CLOSED_SHA256_4C, EXP4B_CLOSED_SHA256_4C):
        for rel, want in table.items():
            p = REPO / rel
            got = bg.sha256_file(p) if p.is_file() else None
            if got != want:
                bad.append(f"{rel}: {got} != {want}")
    if bad:
        raise RuntimeError("4c: a closed upstream module drifted from its pin: " + "; ".join(bad))


def check_frozen_4c() -> None:
    check_exp4_closed_4c()
    if FROZEN_SHA256_4C is None:
        raise RuntimeError("FROZEN_SHA256_4C is None — not pinned (build incomplete)")
    for path, want in FROZEN_SHA256_4C.items():
        if bg.sha256_file(path) != want:
            raise RuntimeError(f"frozen file {path} drifted")


def require_prereg_4c(*, tag_exists=None, blob_sha=None) -> dict:
    """`battery_4.require_prereg_4`'s body over `PREREG_TAG_4C` /
    `INSTRUMENT_BLOBS_4C`."""
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_4C):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_4C} does not exist")
    bound = {}
    for rel in INSTRUMENT_BLOBS_4C:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_4C, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_4C} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_4C, "instrument_blobs": bound}


if __name__ == "__main__":
    if "--rungs" in sys.argv:
        floors = bg.load_floors()
        battery = bt.load_battery()
        table = {}
        for traj in TRAJECTORIES_4C:
            outcome = load_outcome_4c(traj, battery=battery)
            rs = rung_sets_4c(outcome, floors)
            ci = clear_indices_4c(rs, outcome["steps"])
            fails = check_rung_set_pins_4c(traj, rs, outcome["steps"])
            table[traj] = {"R": rs["R"], "flat": rs["flat"], "transient": rs["transient"],
                           "clear_indices": ci, "pin_failures": fails}
        print(json.dumps(table, indent=1, sort_keys=True))
    else:
        print("usage: python -m experiments.exp4c.battery_4c --rungs")
