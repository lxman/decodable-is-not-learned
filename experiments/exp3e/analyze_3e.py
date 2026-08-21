"""Frozen analysis for Experiment 3e (design §5, §6): shortcut or
reversal — is the sampled channel's item structure copy-reachability
or entropy?

3d established that which items fire is forecastable and that the
forecast collapsed to a binary contrast: the 45 len-4 answers with a
repeated character fire 23× more often per item than all-distinct
answers. Every committed repeat-class fire sits on an item whose
reverse is ONE copy edit from the input (a single transposition or a
rotation by one); the repeat patterns (0,1)/(2,3) have no such route
at identical entropy. This module adjudicates whether NEW draws on
the same 45 items — 1b seeds 40–167 adjudicating, 410m seeds 28–91
replicating non-gating — concentrate their fires on the 32 reachable
items: the §5.3 exact hypergeometric on how many DISTINCT new-fired
items land in the 13 non-reachable, conditional on the fired total.
Worlds: SHORTCUT / NO-SHORTCUT / ANTI-SHORTCUT / UNINFORMATIVE with
the frozen THIN qualifier on n ≤ 10 (§6); the §5.5 specificity arm
annotates (DIRECTED / MISFIRE-RATE / SPARSE) and gates nothing.

THE ONLY SCORED OUTCOME is the same verified full-string fire
3/3c/3d used, under 3c's ratified total verify wrapper — no new
metric, no new threshold (§2). The specificity arm applies that
criterion to a different TARGET string and adds no branch on the draw
side. Every fire and every competitor emission is disclosed verbatim
with its (item, seed, draw) address; every zero ships as a
Clopper–Pearson bound; leak-void semantics are 3c's, applied to every
target string (§4).

FOUR-TREE DISCIPLINE. The committed base (exp3 seeds 0–3, 3c seeds
4–15, 3d seeds 16–39/16–27) is read from sha-pinned raw draws files
and re-scored with the target-swapped scorer at target = answer: the
26 committed fire addresses must reproduce exactly (the §4 pin), and
the 19 repeat-class addresses are the scorer's known-answer gate (a);
ctrl_copy's committed T = 1.0 draws re-scored at target = the copy
answer must reproduce 12787/16000 and 13460/16000 exactly (gate b).
The new tranche loads through the subset-aware shard loaders below
(stored tallies recomputed from raw draws, refused on disagreement).
The partition, the subset, m_min, m_s,min and the stream map are
committed records RECOMPUTED from the item file at every load and
refused on disagreement (3a's class). The item file is hash-checked
against the §4 pin before any prompt is rendered (3c finding A), and
`answer_type` — the verify criterion's normalization branch — is
resolved from the pinned item file, never from a runner-written field
(3d finding F1). Gate 1's coverage is pinned to the literal 45 × 64
(3d finding F2).

LINEAGE. Frozen things are imported, never copied (§11): exp3's
sampler (namespace string 'exp3' DELIBERATELY — seeds 40–167 / 28–91
extend the same committed stream families), exp3's loaders and CP
helpers, 3c's total verify wrapper, leak-void prompt loader, tally
and rate machinery, 3d's item-file loader (sha + strata pins) and
gate-1 comparator. The imported files are sha-pinned below and
asserted at run time: exp3, 3c and 3d are closed, and a changed
frozen byte means these are not the committed streams.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

EXP3E = Path(__file__).resolve().parent
EXPERIMENTS = EXP3E.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from experiments.exp3 import analyze_3 as a3  # noqa: E402
from experiments.exp3.sampler import stream_seed  # noqa: E402
from experiments.exp3c import analyze_3c as c  # noqa: E402
from experiments.exp3d import analyze_3d as d  # noqa: E402
from experiments.exp3e import partition_3e as pt  # noqa: E402
from experiments.exp3e import scorer_3e as sc  # noqa: E402
from experiments.exp3e import stats_3e as st  # noqa: E402

# ------------------------------------------------------------ the matrix

RUNG = "reverse_string"                # the 2b survivor; everything else
                                       # EXCLUDED with bounds standing (§3)
SIZES_3E = ("410m", "1b")
ADJUDICATING_SIZE = "1b"               # §5.3: 1b adjudicates
REPLICATION_SIZE = "410m"              # §5.4: non-gating replication

NEW_SEEDS_3E = {"410m": tuple(range(28, 92)),    # §3: 64 new seeds
                "1b": tuple(range(40, 168))}     # §3: 128 new seeds
COMMITTED_SEEDS = {"410m": tuple(range(0, 28)),  # exp3 0–3, 3c 4–15,
                   "1b": tuple(range(0, 40))}    # 3d 16–27 / 16–39
DRAWS_PER_SEED_3E = 64                           # exp3's reversal dps
BLOCK_SEEDS = 16                                 # §10.4: 16-seed blocks
SEED_BLOCKS = {
    s: tuple(tuple(NEW_SEEDS_3E[s][j:j + BLOCK_SEEDS])
             for j in range(0, len(NEW_SEEDS_3E[s]), BLOCK_SEEDS))
    for s in SIZES_3E}
K_NEW_3E = {s: len(NEW_SEEDS_3E[s]) * DRAWS_PER_SEED_3E
            for s in SIZES_3E}                   # 4,096 / 8,192 per item
K_COMMITTED = {s: len(COMMITTED_SEEDS[s]) * DRAWS_PER_SEED_3E
               for s in SIZES_3E}                # 1,792 / 2,560 per item
K_BLOCK = BLOCK_SEEDS * DRAWS_PER_SEED_3E        # 1,024 draws per item
N_SUBSET = st.N_SUBSET                           # 45
BLOCK_DRAWS = N_SUBSET * K_BLOCK                 # 46,080 per block
N_ITEMS = 500
CI_LEVEL = 0.95

GATE1_SEED_3E = {"1b": 20, "410m": 24}           # §4: fire-carrying seeds
GATE1_COVERAGE = N_SUBSET * DRAWS_PER_SEED_3E    # 2,880 per size, pinned

EXP3 = a3.EXP3
EXP3C = c.EXP3C
EXP3D = d.EXP3D
RESULTS = EXP3E / "results"
PARTITION_PATH = EXP3E / "partition_3e.json"
POWER_PATH = EXP3E / "power_3e.json"
STREAM_MAP_3E_PATH = EXP3E / "stream_map_3e.json"
SCORER_GATES_PATH = RESULTS / "scorer_gates.json"

# ----------------------------------------------------- frozen-file pins
#
# 3d's pins inherited verbatim (exp3 ×4, 3c ×3, 2c harness) plus the
# 3d files 3e's meaning depends on (its analyzer = the item-file
# loader and shard loaders; its gate-1 comparator; its stream map; its
# verdict record = the fires-table referent), exp3's runner (the
# capability loader and model loader the subset path drives), and
# 2b's model loader (the weights' shas).

FROZEN_IMPORT_SHA256_3E = {
    EXP3 / "sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
    EXP3 / "analyze_3.py":
        "aa0cb2374fbdffde2f9eaae26cee1ce51f9f42c0b32fd89f4f8754c983a92274",
    EXP3 / "stream_map.json":
        "ea299282342de59d8267682afbf51931521c742a7950215d7acfdc40584fe7a9",
    EXP3 / "results" / "verdict.json":
        "0bce2f91460dd20dc047127da24f6c650aebbe48fdd8f46f5d24da22fa3489ff",
    EXP3 / "run" / "run_cell.py":
        "5c018457d9eb999079b4b0426dc0ecadf10baed6339d32b5eb914f280da35b46",
    EXP3C / "analyze_3c.py":
        "66b78ffbedb808625ed33019f29d2ef8ec9d0f31a1115eb7cb08ad3e67d42d84",
    EXP3C / "stream_map_3c.json":
        "a49d541ca0bd14c0209ce02749f8109498e4db885305898e6662e55d9a76e402",
    EXP3C / "results" / "verdict.json":
        "5f8999880df37a47c3d5bb000400eac621c369071f9f216ac0e67e22e074589e",
    EXP3D / "analyze_3d.py":
        "1de2039acac181d0af7bf39ccabbadecb3ea236f541cb21036697ef8d75787a9",
    EXP3D / "rederive_3d.py":
        "8421433ffe328e7e2ad8d2877150f9bfc0279c9337576fd5860e917dc8690870",
    EXP3D / "stream_map_3d.json":
        "55ff2294e5bb59943d93308f3761cd01a50e4b7a7a84c8c76cb28343a2ca1cc3",
    EXP3D / "results" / "verdict.json":
        "f812d7191e6b9a220056093fe167ea2647eb9658c9251cd82b6ab45c97916a0c",
    EXPERIMENTS / "exp2c" / "harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    EXPERIMENTS / "exp2b" / "models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
}

# §4: every committed draws file the analyzer reads — the three trees'
# reverse_string streams at both sizes (the committed base, gate (a)'s
# input, gate 1's comparison targets) and exp3's ctrl_copy streams
# (gate (b)'s input). Compared BEFORE any byte is parsed, and the
# gate-1 attestations are compared against these literals AND the tree
# on disk (3c finding B, both directions).
COMMITTED_DRAWS_SHA256 = {
    "reverse_string": {
        "410m": {
            "exp3": "34dd8fc48e9dec001f8575236bad15b1b360d80e4c7785b63267a8692b42cc6c",
            "3c": "b3422b4fcf492519c697ca9bb2a668713c6bcdf178147c157af79c8cad05561e",
            "3d": {
                "reverse_string.s16-s19":
                    "5ad4514ef255b91d4bc130a3c72dbe2cd38d29e21a1fa21dcafa28712753ed1c",
                "reverse_string.s20-s23":
                    "b469ec232a75ae9d069a9d666b7428ea56ad9a1ae2685c7485719c5668277198",
                "reverse_string.s24-s27":
                    "6f1762ed1d45796b97fbb327d9db56cf26c8aef204460c2dafb494c7e9f350ce",
            },
        },
        "1b": {
            "exp3": "45049c9b82a98d8c7fa3816981ce7a33c49b85d3521956b7994feb348b279726",
            "3c": "d673dafceb47f1d5affcbc30080f3c79caf7d3f1053853d7e76a28433a6e0b46",
            "3d": {
                "reverse_string.s16-s19":
                    "baf772c944c5ef40970e16200f8d8e7ace1c6a5f8844b98221aeb497021f6f97",
                "reverse_string.s20-s23":
                    "f1420d777009794785869dafe512654abee31f3a7e1d79df202f61c811d48f13",
                "reverse_string.s24-s27":
                    "f70136e13ba2d9ee2a7127796d0a3acbedc9ab87fda0286eb251c86e8a377634",
                "reverse_string.s28-s31":
                    "d2c5c8a81e7893dce17b49df6d2eda1396742c48beed0f9e9e1acba6168300d2",
                "reverse_string.s32-s35":
                    "5db2102f0559626e49cacefaf807e852b50c182ac46368c7dea3b0e0aba43d2d",
                "reverse_string.s36-s39":
                    "32c3635a200ef54ef010d17cdc48cc5f12cd3939b2dcf0487492595e27147ac5",
            },
        },
    },
    "ctrl_copy": {
        "410m": "8554bfe6116e0fd27d26136619589365632e38d08ba8a43625ba7206784e9834",
        "1b": "ff51ed0a5c0c460d9d9b11f62b2801b484337c107db6f8292a5e72955b24fe13",
    },
}

# §4: the item-file pins — 3d's, inherited by value and re-asserted.
ITEMS_SHA_PIN = dict(d.ITEMS_SHA_PIN)

# §3/§4: the 45-item subset as an explicit index list with its own sha
# (three sources, one value: this literal, the partition record, and
# the recompute from the item file).
SUBSET_ITEMS_PIN = (
    9, 21, 46, 51, 68, 71, 78, 123, 133, 143, 148, 153, 154, 159, 164, 169,
    174, 179, 182, 210, 226, 234, 245, 269, 283, 284, 299, 320, 348, 354,
    359, 361, 367, 375, 403, 405, 415, 430, 435, 439, 447, 463, 472, 485,
    489,
)
NON_REACHABLE_PIN = (9, 46, 78, 143, 148, 154, 361, 367, 415, 435, 439,
                     463, 489)
N_ALL_DISTINCT_LEN4 = 149


def subset_sha256(items) -> str:
    return hashlib.sha256(json.dumps([int(i) for i in items],
                                     separators=(",", ":")).encode()
                          ).hexdigest()


SUBSET_SHA256_PIN = \
    "292aa5e794e48390755edb6fc1f441145c3e4800684622031c47ce08989c89ef"

# §4: the sha256 of the committed partition_3e.json bytes (the file
# carries its own content sha; the loader recomputes the partition
# from the item file and refuses disagreement on top).
PARTITION_FILE_SHA256 = \
    "4a0e346f0b41068f55cfb3db84033b6149f6c918d00c0c69beb0625ff6e91529"

# §3/§4: the COMPLETE committed reverse_string fire record across the
# three trees, verbatim — 19 at 1b, 7 at 410m, 26 in all — transcribed
# from the sha-pinned verdict records and RE-SCORED from committed raw
# bytes at every analysis run (hard error on any disagreement).
COMMITTED_FIRES_PIN = {
    "1b": (
        {"item": 436, "seed": 0, "draw": 6, "source": "exp3"},
        {"item": 123, "seed": 5, "draw": 58, "source": "3c"},
        {"item": 123, "seed": 8, "draw": 53, "source": "3c"},
        {"item": 123, "seed": 13, "draw": 34, "source": "3c"},
        {"item": 200, "seed": 8, "draw": 2, "source": "3c"},
        {"item": 320, "seed": 15, "draw": 26, "source": "3c"},
        {"item": 370, "seed": 11, "draw": 38, "source": "3c"},
        {"item": 391, "seed": 8, "draw": 42, "source": "3c"},
        {"item": 447, "seed": 13, "draw": 39, "source": "3c"},
        {"item": 447, "seed": 13, "draw": 43, "source": "3c"},
        {"item": 72, "seed": 16, "draw": 11, "source": "3d"},
        {"item": 123, "seed": 19, "draw": 21, "source": "3d"},
        {"item": 123, "seed": 36, "draw": 52, "source": "3d"},
        {"item": 153, "seed": 29, "draw": 41, "source": "3d"},
        {"item": 179, "seed": 30, "draw": 8, "source": "3d"},
        {"item": 283, "seed": 25, "draw": 41, "source": "3d"},
        {"item": 348, "seed": 20, "draw": 14, "source": "3d"},
        {"item": 430, "seed": 20, "draw": 43, "source": "3d"},
        {"item": 447, "seed": 17, "draw": 24, "source": "3d"},
    ),
    "410m": (
        {"item": 123, "seed": 8, "draw": 6, "source": "3c"},
        {"item": 174, "seed": 15, "draw": 42, "source": "3c"},
        {"item": 226, "seed": 6, "draw": 40, "source": "3c"},
        {"item": 123, "seed": 24, "draw": 62, "source": "3d"},
        {"item": 283, "seed": 27, "draw": 10, "source": "3d"},
        {"item": 305, "seed": 18, "draw": 60, "source": "3d"},
        {"item": 382, "seed": 20, "draw": 28, "source": "3d"},
    ),
}


def _sorted_addresses(ads) -> list:
    return sorted(({"item": int(a["item"]), "seed": int(a["seed"]),
                    "draw": int(a["draw"])} for a in ads),
                  key=lambda a: (a["item"], a["seed"], a["draw"]))


# the 19 repeat-class addresses = the 26 restricted to the subset; the
# scorer's known-answer gate (a) reproduces exactly these
REPEAT_CLASS_FIRES_PIN = {
    s: _sorted_addresses(a for a in COMMITTED_FIRES_PIN[s]
                         if a["item"] in SUBSET_ITEMS_PIN)
    for s in SIZES_3E}
COMMITTED_FIRE_COUNTS_SUBSET = {
    s: {i: sum(1 for a in REPEAT_CLASS_FIRES_PIN[s] if a["item"] == i)
        for i in sorted({a["item"] for a in REPEAT_CLASS_FIRES_PIN[s]})}
    for s in SIZES_3E}

# §4: the gate-1 referents — the committed fires at the gate-1 seeds on
# subset items, which the re-derivation must reproduce by address
GATE1_EXPECTED_FIRES = {
    s: _sorted_addresses(a for a in COMMITTED_FIRES_PIN[s]
                         if a["seed"] == GATE1_SEED_3E[s]
                         and a["item"] in SUBSET_ITEMS_PIN)
    for s in SIZES_3E}

# §4: ctrl_copy's committed T = 1.0 SAMPLED verified counts (exp3's
# sha-pinned verdict record; 3d's pin by value) — gate (b) must
# reproduce these EXACTLY (same computation, same bytes).
CTRL_SAMPLED_RATE_PIN = dict(d.CTRL_SAMPLED_RATE_PIN)

# the standing twin record (§4): 0 fires / 512,000 reversal-twin +
# 64,000 control-twin committed draws, re-asserted from raw bytes;
# NO new twin draws are taken.
TWIN_PINS = {"reversal": d.TWIN_REVERSAL_DRAWS,
             "control": d.TWIN_CONTROL_DRAWS}

# §5.4: the scramble prior — 12 distinct permutations of a one-repeat
# len-4 multiset vs 24 of an all-distinct one
SCRAMBLE_PRIOR_FACTOR = 24 / 12


def check_frozen_imports_3e() -> None:
    """Hard-error unless every imported frozen file is byte-identical
    to its pin; run before anything reads any committed tree."""
    for path, want in FROZEN_IMPORT_SHA256_3E.items():
        got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if got != want:
            raise ValueError(
                f"frozen file {path} has sha256 {got}, expected {want} — "
                f"exp3/3c/3d are closed and their files are 3e's "
                f"referents; a changed byte means these are not the "
                f"committed streams (frozen things stay frozen, "
                f"executable form)")


def shard_name(block) -> str:
    return f"{RUNG}.s{block[0]}-s{block[-1]}"


def gate1_shard_block(size) -> tuple:
    """The 3d seed block carrying the gate-1 seed."""
    seed = GATE1_SEED_3E[size]
    for b in d.SEED_BLOCKS[size]:
        if seed in b:
            return b
    raise AssertionError(f"gate-1 seed {seed} in no 3d block")


def all_distinct_len4(answers) -> list:
    return [i for i, a in enumerate(answers)
            if len(a) == pt.SUBSET_LENGTH and len(set(a)) == pt.SUBSET_LENGTH]


# ------------------------------------------------- partition + power pins

def load_partition_3e(answers, path=PARTITION_PATH, *, subset_pin=None,
                      file_sha_pin=None, non_reachable_pin=None) -> dict:
    """The committed partition record, RECOMPUTED from the answers and
    compared (3a's class, refused); the subset it names must equal the
    literal pin; the file bytes must equal their §4 sha when pinned."""
    subset_pin = SUBSET_ITEMS_PIN if subset_pin is None else subset_pin
    path = Path(path)
    if file_sha_pin is not None:
        got = hashlib.sha256(path.read_bytes()).hexdigest() \
            if path.is_file() else None
        if got != file_sha_pin:
            raise ValueError(
                f"partition record {path} has sha256 {got} against the "
                f"§4 pin {file_sha_pin} — not the frozen partition file")
    partition = pt.check_partition(answers, path)
    if partition["items"] != [int(i) for i in subset_pin]:
        raise ValueError(
            f"partition subset {partition['items']} is not the §4 "
            f"subset literal {list(subset_pin)} — the 45 items moved")
    if non_reachable_pin is not None and \
            partition["non_reachable"] != [int(i) for i in non_reachable_pin]:
        raise ValueError(
            f"partition non-reachable class {partition['non_reachable']} "
            f"is not the §3 literal {list(non_reachable_pin)}")
    return partition


def power_pin_entries(partition) -> dict:
    """The verdict-load-bearing entries of the power record, computed
    from the partition alone (no data)."""
    N_ = partition["n_items"]
    K_ = len(partition["non_reachable"])
    m_sizes = [len(e["matched_competitors"]) for e in partition["entries"]
               if e["item"] in set(partition["arm_items"])]
    return {"m_min": st.m_min_of(N_, K_, st.ALPHA_3E),
            "m_min_anti_disclosed": st.m_min_anti_of(N_, K_, st.ALPHA_3E),
            "thin_max": st.THIN_MAX,
            "alpha": st.ALPHA_3E,
            "m_s_min": st.m_s_min_of(m_sizes, st.ALPHA_3E),
            "arm_m_sizes": m_sizes,
            "N": N_, "K": K_}


def load_power_pin_3e(partition, path=POWER_PATH) -> dict:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(
            f"no committed power record at {p} — m_min has no value "
            f"(3a's class, refused)")
    rec = json.loads(p.read_text())
    want = power_pin_entries(partition)
    for k, v in want.items():
        if rec.get(k) != v:
            raise ValueError(
                f"committed power record {k} = {rec.get(k)!r} disagrees "
                f"with the recompute {v!r} from the frozen partition — "
                f"the bar moved after the freeze")
    return {**want, "record": rec}


# ------------------------------------------------------- stream map 3e

def dump_stream_map_3e(path=STREAM_MAP_3E_PATH,
                       subset=SUBSET_ITEMS_PIN) -> dict:
    """The committed seed-extension (§3): endpoints (item 0 / item
    499) for EVERY seed each cell will have pooled — duplicating exp3's,
    3c's and 3d's committed entries on purpose (continuity asserted) —
    plus the 45 subset items' substream seeds at every seed, committed
    and new, under exp3's exact formula and namespace (doc Open item 6:
    3d's map carries endpoints only, so the subset substreams are
    derived here by the SAME imported function and pinned)."""
    cells = {}
    subset_streams = {}
    for size in SIZES_3E:
        top = NEW_SEEDS_3E[size][-1] + 1
        subset_streams[size] = {}
        for s in range(top):
            cells[f"{RUNG}/{size}/trained/s{s}"] = {
                "item0": stream_seed(RUNG, size, "trained", s, 0),
                "item499": stream_seed(RUNG, size, "trained", s, 499),
            }
            subset_streams[size][f"s{s}"] = {
                str(i): stream_seed(RUNG, size, "trained", s, int(i))
                for i in subset}
    out = {
        "formula": "int.from_bytes(sha256('exp3|{rung}|{size}|{mode}|"
                   "s{seed}|i{item}').digest()[:8], 'big') & ((1<<63)-1)",
        "namespace_note": "the namespace string stays 'exp3' "
                          "DELIBERATELY (§3): seeds 40-167 / 28-91 "
                          "extend the same committed stream families "
                          "exp3 drew 0-3, 3c 4-15 and 3d 16-39 / 16-27 "
                          "from; each (cell, seed, item) substream is "
                          "independent of batch composition, so "
                          "sampling 45 items changes no stream",
        "per_item_substreams": True,
        "chunk_rows": 16,
        "draw_order": "seeds ascending; within a seed, chunks in index "
                      "order; within a chunk, rows in row order; one "
                      "multinomial call per step over all rows",
        "committed_seeds": {s: list(COMMITTED_SEEDS[s]) for s in SIZES_3E},
        "new_seeds": {s: list(NEW_SEEDS_3E[s]) for s in SIZES_3E},
        "seed_blocks": {s: [list(b) for b in SEED_BLOCKS[s]]
                        for s in SIZES_3E},
        "gate1_seeds": dict(GATE1_SEED_3E),
        "draws_per_seed": DRAWS_PER_SEED_3E,
        "k_new": dict(K_NEW_3E),
        "subset_items": [int(i) for i in subset],
        "subset_sha256": subset_sha256(subset),
        "cells": cells,
        "subset_streams": subset_streams,
    }
    Path(path).write_text(json.dumps(out, indent=1))
    return out


def check_stream_map_3e(path=STREAM_MAP_3E_PATH, *, exp3_map_path=None,
                        exp3c_map_path=None, exp3d_map_path=None,
                        subset=SUBSET_ITEMS_PIN) -> dict:
    """Hard-error unless the committed 3e map is exactly the formula's
    output, its endpoint entries equal exp3's / 3c's / 3d's committed
    maps on every overlapping seed, and every subset substream equals
    the imported formula."""
    exp3_map_path = exp3_map_path or (EXP3 / "stream_map.json")
    exp3c_map_path = exp3c_map_path or (EXP3C / "stream_map_3c.json")
    exp3d_map_path = exp3d_map_path or d.STREAM_MAP_3D_PATH
    m = json.loads(Path(path).read_text())
    others = {"exp3": json.loads(Path(exp3_map_path).read_text()),
              "exp3c": json.loads(Path(exp3c_map_path).read_text()),
              "exp3d": json.loads(Path(exp3d_map_path).read_text())}
    for name, other in others.items():
        if m.get("formula") != other.get("formula"):
            raise ValueError(
                f"stream_map_3e formula {m.get('formula')!r} differs "
                f"from {name}'s committed formula — not one law over "
                f"the pooled set")
    if m.get("subset_items") != [int(i) for i in subset] or \
            m.get("subset_sha256") != subset_sha256(subset):
        raise ValueError("stream_map_3e subset is not the §4 subset "
                         "literal")
    want_keys = {f"{RUNG}/{size}/trained/s{s}" for size in SIZES_3E
                 for s in range(NEW_SEEDS_3E[size][-1] + 1)}
    if set(m.get("cells", {})) != want_keys:
        raise ValueError(
            f"stream_map_3e covers {len(m.get('cells', {}))} endpoint "
            f"entries, not the 2 cells × their full pooled seed ranges "
            f"({len(want_keys)})")
    for size in SIZES_3E:
        ss = m.get("subset_streams", {}).get(size, {})
        if set(ss) != {f"s{s}" for s in range(NEW_SEEDS_3E[size][-1] + 1)}:
            raise ValueError(f"stream_map_3e subset streams for {size} "
                             f"do not cover every pooled seed")
        for s in range(NEW_SEEDS_3E[size][-1] + 1):
            k = f"{RUNG}/{size}/trained/s{s}"
            want = {"item0": stream_seed(RUNG, size, "trained", s, 0),
                    "item499": stream_seed(RUNG, size, "trained", s, 499)}
            if m["cells"][k] != want:
                raise ValueError(
                    f"stream_map_3e entry {k} = {m['cells'][k]} "
                    f"disagrees with the frozen formula {want} — the "
                    f"map is not the formula's output")
            for name, other in others.items():
                if k in other.get("cells", {}) and \
                        other["cells"][k] != m["cells"][k]:
                    raise ValueError(
                        f"stream_map_3e entry {k} disagrees with "
                        f"{name}'s committed map — pooling continuity "
                        f"broken")
            want_sub = {str(i): stream_seed(RUNG, size, "trained", s,
                                            int(i)) for i in subset}
            if ss[f"s{s}"] != want_sub:
                raise ValueError(
                    f"stream_map_3e subset streams at {size} s{s} "
                    f"disagree with the frozen formula — the map is "
                    f"not the formula's output")
    return m


# ------------------------------------------------- committed raw rows

def _sha_checked_path(p, want, label) -> Path:
    p = Path(p)
    if not p.is_file():
        raise FileNotFoundError(f"no committed draws file at {p} ({label})")
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    if got != want:
        raise ValueError(
            f"committed draws file {p} ({label}) has sha256 {got} against "
            f"the §4 pin {want} — these are not the committed streams")
    return p


def _merge_rows(target, rows, label) -> None:
    for row in rows:
        i = int(row["item"])
        tgt = target.setdefault(i, {})
        overlap = set(tgt) & set(row["draws"])
        if overlap:
            raise ValueError(
                f"{label}: item {i} carries seed streams "
                f"{sorted(overlap)} already loaded from another file — "
                f"duplicated seeds")
        tgt.update(row["draws"])


def load_committed_rows(roots=None, *, n_items=N_ITEMS,
                        draws_pins=None) -> dict:
    """Every committed reverse_string draw at both sizes (exp3 seeds
    0–3, 3c 4–15, 3d 16–39/16–27) and exp3's ctrl_copy draws, read
    from sha-pinned files: {rung: {size: {item: {seed_str: [draws]}}}}.
    Shapes are asserted by the predecessors' own row readers."""
    roots = roots or {"exp3": EXP3, "3c": EXP3C, "3d": EXP3D}
    draws_pins = draws_pins or COMMITTED_DRAWS_SHA256
    out = {RUNG: {}, a3.POSITIVE_CONTROL: {}}
    for size in SIZES_3E:
        pins = draws_pins[RUNG][size]
        merged: dict[int, dict] = {}
        p = _sha_checked_path(
            Path(roots["exp3"]) / "results" / "sampling"
            / f"{size}_trained" / f"{RUNG}.draws.jsonl.gz",
            pins["exp3"], f"exp3 {RUNG}/{size}")
        _merge_rows(merged, c._read_rows(p, n_items, a3.SEEDS,
                                         DRAWS_PER_SEED_3E), str(p))
        p = _sha_checked_path(
            Path(roots["3c"]) / "results" / "sampling"
            / f"{size}_trained" / f"{RUNG}.draws.jsonl.gz",
            pins["3c"], f"3c {RUNG}/{size}")
        _merge_rows(merged, c._read_rows(p, n_items, c.NEW_SEEDS,
                                         DRAWS_PER_SEED_3E), str(p))
        for block in d.SEED_BLOCKS[size]:
            name = d.shard_name(block)
            p = _sha_checked_path(
                Path(roots["3d"]) / "results" / "sampling"
                / f"{size}_trained" / f"{name}.draws.jsonl.gz",
                pins["3d"][name], f"3d {name}/{size}")
            _merge_rows(merged, c._read_rows(p, n_items, block,
                                             DRAWS_PER_SEED_3E), str(p))
        want = {str(s) for s in COMMITTED_SEEDS[size]}
        for i, streams in merged.items():
            if set(streams) != want:
                raise ValueError(
                    f"{size}: item {i} covers committed seeds "
                    f"{sorted(streams)} against {sorted(want)}")
        if set(merged) != set(range(n_items)):
            raise ValueError(f"{size}: committed rows cover "
                             f"{len(merged)} items against {n_items}")
        out[RUNG][size] = merged
        p = _sha_checked_path(
            Path(roots["exp3"]) / "results" / "sampling"
            / f"{size}_trained" / f"{a3.POSITIVE_CONTROL}.draws.jsonl.gz",
            draws_pins[a3.POSITIVE_CONTROL][size],
            f"exp3 {a3.POSITIVE_CONTROL}/{size}")
        ctrl: dict[int, dict] = {}
        _merge_rows(ctrl, c._read_rows(
            p, n_items, a3.SEEDS, a3.DRAWS_PER_SEED[a3.POSITIVE_CONTROL]),
            str(p))
        out[a3.POSITIVE_CONTROL][size] = ctrl
    return out


def _source_of_seed(seed: int) -> str:
    if seed in a3.SEEDS:
        return "exp3"
    if seed in c.NEW_SEEDS:
        return "3c"
    return "3d"


def committed_base_3e(rows, answers, answer_type, score_fn, *,
                      fires_pin=None, subset=None, ctrl_answers=None,
                      ctrl_answer_type="word") -> dict:
    """The committed base the tranche pools with, re-scored from raw
    committed bytes with the target-swapped scorer at target = answer,
    and asserted equal to the §4 26-address pin; the subset's 19
    addresses (gate a) and ctrl_copy's counts (gate b) computed from
    the same bytes. ctrl_copy's answers default to what the exp3
    record carries (passed in by run())."""
    fires_pin = COMMITTED_FIRES_PIN if fires_pin is None else fires_pin
    subset = SUBSET_ITEMS_PIN if subset is None else subset
    subset_set = set(int(i) for i in subset)
    out = {}
    for size in SIZES_3E:
        by_item = rows[RUNG][size]
        targets = {i: [answers[i]] for i in sorted(by_item)}
        em = sc.emissions(by_item, targets, answer_type, score_fn)
        got = []
        per_item = [0] * len(answers)
        for i in sorted(em):
            for ad in em[i][answers[i]]["addresses"]:
                got.append({"item": i, "seed": ad["seed"],
                            "draw": ad["draw"],
                            "source": _source_of_seed(ad["seed"]),
                            "text": ad["text"]})
                per_item[i] += 1
        got_key = sorted(((a["item"], a["seed"], a["draw"], a["source"])
                          for a in got))
        want_key = sorted(((int(a["item"]), int(a["seed"]),
                            int(a["draw"]), a["source"])
                           for a in fires_pin[size]))
        if got_key != want_key:
            raise ValueError(
                f"committed fires re-scored for {RUNG}/{size} disagree "
                f"with the §4 pin: got {got_key}, pin {want_key} — the "
                f"in-sample record is not the committed record")
        seeds = sorted(int(s) for s in next(iter(by_item.values())))
        n_per_item = sum(len(v) for v in next(iter(by_item.values()))
                         .values())
        out[size] = {
            "fires": len(got), "addresses": got, "per_item": per_item,
            "seeds": seeds, "n_draws_per_item": n_per_item,
            "n_draws": n_per_item * len(by_item),
            "subset_addresses": _sorted_addresses(
                a for a in got if a["item"] in subset_set),
            "subset_fires_by_item": {
                i: per_item[i] for i in sorted(subset_set)
                if per_item[i]},
            "rows": by_item,
        }
    # gate (b): ctrl_copy at target = the copy answer
    gate_b = {}
    for size in SIZES_3E:
        ctrl_rows = rows[a3.POSITIVE_CONTROL][size]
        if ctrl_answers is None:
            raise ValueError("ctrl_copy answers are required for gate b")
        t = {i: [ctrl_answers[i]] for i in sorted(ctrl_rows)}
        em = sc.emissions(ctrl_rows, t, ctrl_answer_type, score_fn)
        count = sum(em[i][ctrl_answers[i]]["count"] for i in em)
        n = sum(len(v) for r in ctrl_rows.values() for v in r.values())
        gate_b[size] = {"count": int(count), "n_draws": int(n)}
    out["ctrl_gate_b"] = gate_b
    return out


def load_twin_record(exp3_root=EXP3, *, verify_fn=None, pins=None) -> dict:
    """The standing contamination referent (§4): exp3's 8 untrained
    twin cells, re-loaded through exp3's OWN frozen loader — 0 fires
    across the pinned draw totals, or a hard error."""
    pins = TWIN_PINS if pins is None else pins
    verify_fn = verify_fn or c.load_verify_3c()
    cells = a3.load_sampling_cells(Path(exp3_root), verify_fn=verify_fn)
    twin_rev = sum(cells[(r, s, "untrained")]["recomputed"]
                   ["n_draws_total"] for r in a3.REVERSAL_RUNGS
                   for s in a3.PROBE_SIZES)
    twin_ctrl = sum(cells[(r, s, "untrained")]["recomputed"]
                    ["n_draws_total"]
                    for r in (a3.POSITIVE_CONTROL, a3.MATCHED_CONTROL)
                    for s in a3.PROBE_SIZES)
    twin_fires = sum(cells[(r, s, "untrained")]["recomputed"]
                     ["full_string_total"] for r in a3.RUNGS
                     for s in a3.PROBE_SIZES)
    if twin_fires != 0 or twin_rev != pins["reversal"] or \
            twin_ctrl != pins["control"]:
        raise ValueError(
            f"twin record recomputed as {twin_fires} fires / "
            f"{twin_rev} + {twin_ctrl} draws against the standing "
            f"0 / {pins['reversal']} + {pins['control']} — the trees are "
            f"not the committed trees")
    return {"cells": 8, "fires": 0, "reversal_twin_draws": twin_rev,
            "control_twin_draws": twin_ctrl}


# ------------------------------------------------- raw-shard ingestion

def read_subset_rows(path, items, seeds, dps) -> list:
    """3c's row reader, subset-aware: rows must cover EXACTLY `items`
    (the committed 45, by original battery index), each with exactly
    the block's seed streams at exactly dps draws."""
    want_items = set(int(i) for i in items)
    want = {str(s) for s in seeds}
    rows, seen = [], set()
    with gzip.open(Path(path), "rt") as f:
        for line in f:
            row = json.loads(line)
            i = row.get("item")
            if i in seen:
                raise ValueError(f"duplicate item {i} in {path}")
            if i not in want_items:
                raise ValueError(
                    f"{path}: item {i} is not in the preregistered "
                    f"45-item subset — this shard sampled outside it")
            seen.add(i)
            draws = row.get("draws")
            if not isinstance(draws, dict) or set(draws) != want:
                raise ValueError(
                    f"{path} item {i}: seed streams "
                    f"{sorted(draws) if isinstance(draws, dict) else draws!r}"
                    f" are not the preregistered seeds {sorted(seeds)}")
            for s in seeds:
                stream = draws[str(s)]
                if not isinstance(stream, list) or len(stream) != dps or \
                        not all(isinstance(x, str) for x in stream):
                    raise ValueError(
                        f"{path} item {i} seed {s}: stream of "
                        f"{len(stream) if isinstance(stream, list) else stream!r}"
                        f" draws against draws_per_seed {dps}")
            rows.append(row)
    if seen != want_items:
        raise ValueError(
            f"{path}: rows cover {len(seen)} items against the "
            f"{len(want_items)}-item subset — coverage incomplete")
    return rows


def _check_shard_provenance_3e(rec, p, size, block, items, answers,
                               labels) -> None:
    if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
            (RUNG, size, "trained"):
        raise ValueError(
            f"{p} contents ({rec.get('rung')}/{rec.get('size')}/"
            f"{rec.get('mode')}) disagree with its path")
    items = [int(i) for i in items]
    if rec.get("n_items") != len(items) or rec.get("items") != items:
        raise ValueError(
            f"{p}: items {rec.get('items')!r} (n_items "
            f"{rec.get('n_items')!r}) are not the preregistered subset "
            f"— this shard did not sample the 45 items")
    if rec.get("subset_sha256") != subset_sha256(items):
        raise ValueError(f"{p}: subset_sha256 is not the subset's")
    if [str(x) for x in rec.get("answers", [])] != \
            [str(answers[i]) for i in items]:
        raise ValueError(f"{p}: answers are not the subset's committed "
                         f"answers")
    if [str(x) for x in rec.get("probe_labels", [])] != \
            [str(labels[i]) for i in items]:
        raise ValueError(f"{p}: probe_labels are not the subset's")
    sha = rec.get("items_sha256")
    if not isinstance(sha, str) or not sha:
        raise ValueError(f"{p} carries no items_sha256 — the item-file "
                         f"pin has no value there (3a's class, refused)")
    if not isinstance(rec.get("model_sha"), str) or not rec.get("model_sha"):
        raise ValueError(f"{p} carries no model_sha — the weights' pin "
                         f"has no value there (3a's class, refused)")
    if rec.get("dtype") != "float32":
        raise ValueError(
            f"{p}: dtype {rec.get('dtype')!r} violates the ledgered "
            f"sampling policy — every probe-size sampling cell is "
            f"float32 (exp3's cell_policy, inherited)")
    if rec.get("untrained_seed") is not None:
        raise ValueError(
            f"{p}: untrained_seed {rec.get('untrained_seed')!r} on a "
            f"trained cell — 3e samples no twins (§4)")
    if rec.get("seeds") != list(block):
        raise ValueError(
            f"{p}: seeds {rec.get('seeds')!r} are not this shard's "
            f"preregistered block {list(block)} (§3)")
    if rec.get("draws_per_seed") != DRAWS_PER_SEED_3E:
        raise ValueError(
            f"{p}: draws_per_seed {rec.get('draws_per_seed')!r} against "
            f"the preregistered {DRAWS_PER_SEED_3E}")
    if rec.get("k_total") != K_BLOCK:
        raise ValueError(
            f"{p}: k_total {rec.get('k_total')!r} against "
            f"{BLOCK_SEEDS} seeds × {DRAWS_PER_SEED_3E} draws = {K_BLOCK}")


def load_new_cells_3e(root=EXP3E, verify_fn=None, *, items=None,
                      answers=None, labels=None,
                      answer_type_pin=None) -> dict:
    """The 2 cells' NEW draws (§3) on the 45-item subset, shard-per-
    16-seed-block, raw streams beside their records. Stored per-seed
    tallies are convenience copies: the analyzer RECOMPUTES them from
    the raw draws and refuses any disagreement. Shard coverage must be
    EXACTLY the preregistered block partition; row coverage EXACTLY
    the subset. `answers`/`labels` are the FULL committed battery's
    (indexed by original item); `answer_type_pin` comes from the
    pinned item file (3d F1)."""
    if verify_fn is None:
        verify_fn = c.load_verify_3c()
    if items is None or answers is None or labels is None or \
            answer_type_pin is None:
        raise ValueError("items, answers, labels and answer_type_pin are "
                         "required — they come from the pinned item file")
    items = [int(i) for i in items]
    base = Path(root) / "results" / "sampling"
    want = {}
    for size in SIZES_3E:
        names = set()
        for block in SEED_BLOCKS[size]:
            names.add(f"{shard_name(block)}.json")
            names.add(f"{shard_name(block)}.draws.jsonl.gz")
        want[f"{size}_trained"] = names
    c._refuse_strays_3c(base, want)
    out = {}
    for size in SIZES_3E:
        dd = base / f"{size}_trained"
        merged: dict[int, dict] = {}
        items_sha = answer_type = model_sha = None
        stored: dict[str, dict] = {}
        for block in SEED_BLOCKS[size]:
            p = dd / f"{shard_name(block)}.json"
            gz = dd / f"{shard_name(block)}.draws.jsonl.gz"
            if not p.is_file():
                raise FileNotFoundError(
                    f"no 3e shard record for {size} block "
                    f"{block[0]}-{block[-1]} at {p}")
            if not gz.is_file():
                raise FileNotFoundError(
                    f"no raw draws file for {size} block "
                    f"{block[0]}-{block[-1]} at {gz}")
            rec = json.loads(p.read_text())
            _check_shard_provenance_3e(rec, p, size, block, items,
                                       answers, labels)
            if items_sha is None:
                items_sha = rec["items_sha256"]
                answer_type = rec.get("answer_type")
                model_sha = rec["model_sha"]
            elif rec["items_sha256"] != items_sha or \
                    rec.get("answer_type") != answer_type:
                raise ValueError(
                    f"{p}: items_sha256 or answer_type disagree with "
                    f"this cell's other shards — not one battery")
            elif rec["model_sha"] != model_sha:
                raise ValueError(
                    f"{p}: model_sha {rec['model_sha']!r} disagrees with "
                    f"this cell's other shards ({model_sha!r}) — not one "
                    f"model (freeze finding F-3)")
            rows = read_subset_rows(gz, items, block, DRAWS_PER_SEED_3E)
            _merge_rows(merged, rows, str(gz))
            stt = rec.get("per_seed_tallies")
            if not isinstance(stt, dict):
                raise ValueError(f"{p} carries no per_seed_tallies")
            dup = set(stored) & set(stt)
            if dup:
                raise ValueError(
                    f"{p}: per-seed tallies for seeds {sorted(dup)} "
                    f"already stored by another shard")
            stored.update(stt)
        if answer_type != answer_type_pin:
            raise ValueError(
                f"{size}: shard answer_type {answer_type!r} against "
                f"the committed item file's {answer_type_pin!r} — the "
                f"verify criterion's normalization branch is a verdict "
                f"input and must come from the pinned items, not a "
                f"runner-written field (3d F1)")
        seeds = NEW_SEEDS_3E[size]
        rows = [{"item": i, "draws": merged[i]} for i in items]
        for row in rows:
            if set(row["draws"]) != {str(s) for s in seeds}:
                raise ValueError(
                    f"item {row['item']} covers seeds "
                    f"{sorted(row['draws'])} against the preregistered "
                    f"{list(seeds)} — shard coverage incomplete")
        t = c.tally_with_addresses(rows, answers, labels, seeds,
                                   answer_type=answer_type,
                                   verify_fn=verify_fn)
        try:
            normalized = {k: {f: int(v[f]) for f in
                              ("full_string", "first_char", "n_draws")}
                          for k, v in stored.items()}
        except (KeyError, TypeError, ValueError):
            normalized = None
        if normalized != t["per_seed"]:
            raise ValueError(
                f"{size}: stored per-seed tallies disagree with the "
                f"recompute from the raw draws — this battery's runner "
                f"and analyzer do not agree on what was drawn")
        full_total = sum(v["full_string"] for v in t["per_seed"].values())
        n_draws = sum(v["n_draws"] for v in t["per_seed"].values())
        if n_draws != len(items) * K_NEW_3E[size]:
            raise ValueError(
                f"{size}: {n_draws} draws recomputed against "
                f"{len(items)} × {K_NEW_3E[size]}")
        out[size] = {
            "rung": RUNG, "size": size, "mode": "trained",
            "n": len(items), "items": items,
            "answer_type": answer_type, "items_sha256": items_sha,
            "model_sha": model_sha,
            "seeds": list(seeds),
            "rows_by_item": merged,
            "recomputed": {
                "per_seed": t["per_seed"],
                "full_string_total": int(full_total),
                "n_draws_total": int(n_draws),
                "per_item_full_string": {
                    i: int(t["per_item_full_string"][i]) for i in items},
            },
            "addresses": t["addresses"],
            "mean_draw_len": t["total_draw_len"] / n_draws,
        }
    return out


# ------------------------------------------------- gate-1 records (§10.3)

def load_gate1_3e(root=EXP3E, *, items=None, expected_fires=None) -> dict:
    """The 2 byte re-derivation comparison records: 3d's committed
    gate-1 seed streams on the 45 items, re-derived through the
    production subset path and compared with zero tolerance. Coverage
    is pinned to the subset literal × 64 (3d F2); a CLEAN comparison
    must carry the committed fires at their addresses."""
    items = [int(i) for i in (SUBSET_ITEMS_PIN if items is None else items)]
    expected_fires = GATE1_EXPECTED_FIRES if expected_fires is None \
        else expected_fires
    base = Path(root) / "results" / "gate1"
    want = {f"{size}_trained": {f"{RUNG}.json"} for size in SIZES_3E}
    c._refuse_strays_3c(base, want)
    out = {}
    for size in SIZES_3E:
        p = base / f"{size}_trained" / f"{RUNG}.json"
        if not p.is_file():
            raise FileNotFoundError(
                f"no gate-1 comparison record for {RUNG}/{size} at {p}")
        rec = json.loads(p.read_text())
        if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
                (RUNG, size, "trained"):
            raise ValueError(
                f"{p} contents ({rec.get('rung')}/{rec.get('size')}/"
                f"{rec.get('mode')}) disagree with its path")
        if rec.get("dtype") != "float32":
            raise ValueError(f"{p}: dtype {rec.get('dtype')!r} is not "
                             f"the campaign's float32")
        seed = GATE1_SEED_3E[size]
        if rec.get("seeds_rederived") != [seed]:
            raise ValueError(
                f"{p}: seeds_rederived {rec.get('seeds_rederived')!r} — "
                f"3e's gate 1 re-derives 3d's committed seed {seed} "
                f"only at {size} (§4: fire-carrying)")
        if rec.get("n_items") != len(items) or rec.get("items") != items:
            raise ValueError(
                f"{p}: items {rec.get('items')!r} (n_items "
                f"{rec.get('n_items')!r}) are not the preregistered "
                f"subset — gate 1 attests a byte comparison over the "
                f"WHOLE subset, and a record covering anything else has "
                f"no value (3d F2; 3a's class, refused)")
        if rec.get("subset_sha256") != subset_sha256(items):
            raise ValueError(f"{p}: subset_sha256 is not the subset's")
        dps = rec.get("draws_per_seed")
        if dps != DRAWS_PER_SEED_3E:
            raise ValueError(
                f"{p}: draws_per_seed {dps!r} against 3d's committed "
                f"{DRAWS_PER_SEED_3E} — a stream of the wrong depth is "
                f"not byte-comparable")
        compared = rec.get("draws_compared")
        if compared != len(items) * dps or compared <= 0:
            raise ValueError(
                f"{p}: draws_compared {compared!r} against the pinned "
                f"{len(items)} × {dps} = {len(items) * dps}")
        sha = rec.get("committed_draws_sha256")
        if not isinstance(sha, str) or not sha:
            raise ValueError(
                f"{p} carries no committed_draws_sha256 — the record "
                f"does not say what it compared against")
        shard = rec.get("committed_shard")
        want_shard = f"{d.shard_name(gate1_shard_block(size))}.draws.jsonl.gz"
        if shard != want_shard:
            raise ValueError(
                f"{p}: committed_shard {shard!r} is not the 3d shard "
                f"carrying seed {seed} ({want_shard})")
        diffs = rec.get("diffs")
        if not isinstance(diffs, list):
            raise ValueError(f"{p}: diffs {diffs!r} is not a list")
        for j, dd in enumerate(diffs):
            if not (isinstance(dd, dict)
                    and isinstance(dd.get("item"), int)
                    and dd.get("seed") == seed
                    and isinstance(dd.get("draw"), int)
                    and isinstance(dd.get("got"), str)
                    and isinstance(dd.get("committed"), str)):
                raise ValueError(
                    f"{p} diff {j}: {dd!r} is not a verbatim differing "
                    f"draw with an (item, seed, draw) address")
        if rec.get("n_diffs") != len(diffs):
            raise ValueError(
                f"{p}: n_diffs {rec.get('n_diffs')!r} against "
                f"{len(diffs)} disclosed diffs")
        fires = rec.get("fires_reproduced")
        if not isinstance(fires, list):
            raise ValueError(f"{p}: fires_reproduced {fires!r} is not a "
                             f"list")
        fires = _sorted_addresses(fires)
        if len(diffs) == 0 and fires != expected_fires[size]:
            raise ValueError(
                f"{p}: fires_reproduced {fires} against the committed "
                f"{expected_fires[size]} on a comparison with zero "
                f"diffs — a byte-identical stream that does not carry "
                f"the committed fires is incoherent; the record is not "
                f"what it claims")
        out[size] = {"size": size, "n": len(items), "draws_per_seed": dps,
                     "draws_compared": compared,
                     "n_diffs": int(rec["n_diffs"]), "diffs": diffs,
                     "fires_reproduced": fires,
                     "committed_draws_sha256": sha,
                     "committed_shard": shard,
                     "items_sha256": rec.get("items_sha256"),
                     "model_sha": rec.get("model_sha")}
    return out


def check_gate1_committed_shas_3e(gate1_records, exp3d_root=None,
                                  expected=None) -> None:
    """Both directions (3c finding B): the attested sha must equal
    the 3d shard on disk AND the §4 literal."""
    exp3d_root = Path(exp3d_root or EXP3D)
    for size, g in gate1_records.items():
        gz = (exp3d_root / "results" / "sampling" / f"{size}_trained"
              / g["committed_shard"])
        if not gz.is_file():
            raise FileNotFoundError(f"no committed 3d shard at {gz}")
        got = hashlib.sha256(gz.read_bytes()).hexdigest()
        attested = g["committed_draws_sha256"]
        if got != attested:
            raise ValueError(
                f"gate-1 record for {size} attests committed_draws_sha256 "
                f"{attested} but the 3d shard on disk hashes to {got} — "
                f"the comparison was not against these bytes")
        want = expected[size] if expected is not None else \
            COMMITTED_DRAWS_SHA256[RUNG][size]["3d"][
                g["committed_shard"].replace(".draws.jsonl.gz", "")]
        if got != want:
            raise ValueError(
                f"3d shard for {size} hashes to {got} against the §4 "
                f"literal {want} — the committed stream is not the pinned "
                f"stream")


def check_gate1_vs_tranche_3e(gate1_records, new_cells, *,
                              items_sha_pin) -> None:
    """FREEZE FINDING F-3: the gate-1 record's `items_sha256` was
    attested but never compared to the §4 pin by the analyzer (the
    tranche's is), and no check tied the gate-1 weights to the
    tranche's weights. Both additive: a record rendered from other
    items, or a comparison made with other weights, attests nothing
    about the production path the tranche ran."""
    for size, g in sorted(gate1_records.items()):
        if g.get("items_sha256") != items_sha_pin:
            raise ValueError(
                f"gate-1 record for {size} carries items_sha256 "
                f"{g.get('items_sha256')!r} against the §4 pin "
                f"{items_sha_pin!r} — the re-derivation did not render "
                f"the committed prompts")
        tranche_sha = new_cells[size].get("model_sha")
        if not isinstance(g.get("model_sha"), str) or not g.get("model_sha") \
                or g.get("model_sha") != tranche_sha:
            raise ValueError(
                f"gate-1 record for {size} attests model_sha "
                f"{g.get('model_sha')!r} against the tranche's "
                f"{tranche_sha!r} — the byte comparison and the new draws "
                f"were not made with one model")


# ------------------------------------------ scorer-gate record (§5.5)

def load_scorer_gates_3e(root=EXP3E, *, fires_pin=None,
                         ctrl_pin=None) -> dict:
    """The scorer's two known-answer gates, committed BEFORE any
    sampling (§10.2): (a) target = answer reproduces the 19
    repeat-class addresses exactly; (b) target = copy answer
    reproduces ctrl_copy's committed counts exactly. A record that
    did not pass, or compared against the wrong referent, is a HARD
    ERROR — the campaign must not have launched."""
    fires_pin = REPEAT_CLASS_FIRES_PIN if fires_pin is None else fires_pin
    ctrl_pin = CTRL_SAMPLED_RATE_PIN if ctrl_pin is None else ctrl_pin
    p = Path(root) / "results" / "scorer_gates.json"
    if not p.is_file():
        raise FileNotFoundError(
            f"no scorer known-answer gate record at {p} — the §10 order "
            f"requires both scorer gates before any sampling")
    rec = json.loads(p.read_text())
    ga = rec.get("gate_a", {})
    gb = rec.get("gate_b", {})
    for size in SIZES_3E:
        got = _sorted_addresses(ga.get("addresses", {}).get(size, []))
        exp = _sorted_addresses(ga.get("expected", {}).get(size, []))
        if exp != fires_pin[size] or got != fires_pin[size]:
            raise ValueError(
                f"{p}: gate (a) at {size} addresses {got} / expected "
                f"{exp} against the §4 pin {fires_pin[size]} — the "
                f"scorer gate compared against the wrong referent or "
                f"did not reproduce it")
        if gb.get("counts", {}).get(size) != dict(ctrl_pin[size]) or \
                gb.get("expected", {}).get(size) != dict(ctrl_pin[size]):
            raise ValueError(
                f"{p}: gate (b) at {size} counts "
                f"{gb.get('counts', {}).get(size)} / expected "
                f"{gb.get('expected', {}).get(size)} against the §4 pin "
                f"{dict(ctrl_pin[size])}")
    if ga.get("passed") is not True or gb.get("passed") is not True or \
            rec.get("passed") is not True:
        raise ValueError(
            f"{p}: the scorer known-answer gates did not pass ({rec!r}) "
            f"— the campaign must not have launched (§5.5); nothing "
            f"here adjudicates draws taken past a failed gate")
    return {"passed": True, "gate_a": ga, "gate_b": gb}


# ------------------------------------------------------------- verdict

WORLDS_3E = ("SHORTCUT", "NO-SHORTCUT", "ANTI-SHORTCUT", "UNINFORMATIVE")


def _entry_of(partition) -> dict:
    return {e["item"]: e for e in partition["entries"]}


def _first_char_neighbours(x: str) -> list:
    """All one-edit neighbours starting with the reverse's first
    character, overlap clause IGNORED — the descriptive set printed
    for the sit-out items (§5.1: 'reverse-vs-qpff-type counts')."""
    a = x[::-1]
    return sorted(s for s in pt.neighbours(x) if s != a and s[0] == a[0])


def _specificity_arm(size, rows_by_item, partition, prompts, answers,
                     answer_type, score_fn) -> dict:
    """§5.5 on one cell's NEW draws: count vectors for the arm items,
    the designation-exchangeability test, every competitor emission
    verbatim, the void disclosures, and the sit-out descriptives.

    FREEZE FINDING F-1: an item with ANY void target — reverse or
    competitor — is EXCLUDED from the designation test and disclosed
    under `arm_void_excluded` with its raw vector. A void target's
    count is zero by fiat (§4: counted by nothing), not by emission,
    so its slot is no longer exchangeable with the others; zeroing a
    competitor in particular LOWERS the null p (the reverse's share
    rises against a slot that cannot score), i.e. it is anti-
    conservative toward DIRECTED. The primary's void semantics (3c:
    a void fire is void) are untouched; on the committed battery no
    target of any item is void (freeze census), so this rule is inert
    on the real experiment and exists for the frozen semantics."""
    entries = _entry_of(partition)
    vectors = []
    items_out = []
    comp_addresses = []
    comp_voids = []
    void_excluded = []
    for i in partition["arm_items"]:
        e = entries[i]
        targets = [e["answer"]] + list(e["matched_competitors"])
        em = sc.emissions({i: rows_by_item[i]}, {i: targets}, answer_type,
                          score_fn, prompts={i: prompts[i]})[i]
        vec = tuple(em[t]["count"] for t in targets)
        void_targets = [t for t in targets if em[t]["void"]]
        if void_targets:
            void_excluded.append({
                "item": i, "targets": targets,
                "void_targets": void_targets,
                "raw_counts": [em[t]["raw_count"] for t in targets],
                "reason": "a void target's slot is not exchangeable "
                          "(count zero by fiat); the item sits out the "
                          "designation test and is disclosed here "
                          "(freeze finding F-1)"})
        else:
            vectors.append(vec)
        for t in e["matched_competitors"]:
            for ad in em[t]["addresses"]:
                entry = {"item": i, "target": t, **ad,
                         "void": em[t]["void"]}
                (comp_voids if em[t]["void"] else comp_addresses).append(
                    entry)
        items_out.append({
            "item": i, "input": e["input"], "answer": e["answer"],
            "sub_class": e["sub_class"],
            "targets": targets, "counts": list(vec),
            "raw_counts": [em[t]["raw_count"] for t in targets],
            "void_targets": void_targets,
            "in_test": not void_targets,
            "theta": 1.0 / len(targets),
        })
    test = st.designation_test(vectors) if vectors else \
        {"T_obs": 0, "p": None, "events": 0, "n_items": 0}
    sit_out = []
    for i in partition["arm_sit_out"]:
        e = entries[i]
        nb = _first_char_neighbours(e["input"])
        targets = [e["answer"]] + nb
        em = sc.emissions({i: rows_by_item[i]}, {i: targets}, answer_type,
                          score_fn, prompts={i: prompts[i]})[i]
        sit_out.append({
            "item": i, "input": e["input"], "answer": e["answer"],
            "reverse_count": em[e["answer"]]["count"],
            "first_char_neighbours_dropped_by_overlap": nb,
            "neighbour_counts": {t: em[t]["count"] for t in nb},
            "note": "no matched competitor (|M| = 0); descriptive only",
        })
    return {"size": size, "items": items_out, "test": test,
            "n_arm_items": len(partition["arm_items"]),
            "arm_void_excluded": void_excluded,
            "competitor_addresses": comp_addresses,
            "competitor_voids": comp_voids,
            "sit_out": sit_out}


def _s2_block(rows_by_item, items, partition_entries, answers,
              answer_type, score_fn, prompts) -> dict:
    """§5.5 S2: reverse vs first-character-matched one-edit
    neighbours, counts with CP bounds, no test."""
    rev = nb = 0
    n_draws = 0
    per_item = []
    for i in items:
        x = answers[i][::-1]
        comps = pt.matched_competitors(x)
        targets = [answers[i]] + comps
        em = sc.emissions({i: rows_by_item[i]}, {i: targets}, answer_type,
                          score_fn, prompts={i: prompts[i]})[i]
        r = em[answers[i]]["count"]
        cc = sum(em[t]["count"] for t in comps)
        n = sum(len(v) for v in rows_by_item[i].values())
        rev += r
        nb += cc
        n_draws += n
        if r or cc:
            per_item.append({"item": i, "answer": answers[i],
                             "reverse": r,
                             "neighbours": {t: em[t]["count"]
                                            for t in comps},
                             "n_draws": n})
    return {"n_items": len(items), "n_draws": n_draws,
            "reverse": c.rate_entry(rev, n_draws),
            "matched_neighbours": c.rate_entry(nb, n_draws),
            "items_with_emissions": per_item}


def verdict_3e(new_cells, gate1_records, scorer_gates, base, partition,
               power_pin, prompts, twin, *, answers, score_fn,
               answer_type) -> dict:
    """Design §6, adjudicated in precedence order, with everything
    computed and disclosed BEFORE the first branch so no gate can hide
    another's evidence. Provenance failures are hard errors raised by
    the loaders, never verdicts. Adjudication is the 1b primary
    statistic alone; 410m and the specificity arm attach as
    annotations and modify nothing."""
    entries = _entry_of(partition)
    items = partition["items"]
    reach_set = set(partition["reachable"])
    non_set = set(partition["non_reachable"])
    m_min = power_pin["m_min"]
    m_s_min = power_pin["m_s_min"]
    for size in SIZES_3E:
        if new_cells[size]["items"] != items:
            raise ValueError(f"{size}: tranche items are not the "
                             f"partition's subset")
    answers_by_item = list(answers)
    answers_sub = {e["item"]: e["answer"] for e in partition["entries"]}
    for i, a in answers_sub.items():
        if answers_by_item[i] != a:
            raise ValueError(f"item {i}: partition answer {a!r} is not "
                             f"the battery's {answers_by_item[i]!r}")
    all_distinct = [i for i in all_distinct_len4(answers_by_item)
                    if i not in answers_sub]

    # ---- gate 1 (computed first, branched first)
    gate1 = {s: {"draws_compared": g["draws_compared"],
                 "n_diffs": g["n_diffs"], "diffs": g["diffs"],
                 "fires_reproduced": g["fires_reproduced"],
                 "committed_draws_sha256": g["committed_draws_sha256"],
                 "committed_shard": g["committed_shard"]}
             for s, g in sorted(gate1_records.items())}
    gate1_total = sum(v["draws_compared"] for v in gate1.values())
    gate1_diff_cells = {s: v["n_diffs"] for s, v in gate1.items()
                        if v["n_diffs"] > 0}

    # ---- the new fires, leak-void applied per fire (3c semantics)
    fires = {}
    all_new_fires = 0
    all_void = []
    for size in SIZES_3E:
        cell = new_cells[size]
        rc = cell["recomputed"]
        addresses = []
        for ad in cell["addresses"]:
            i = ad["item"]
            answer = answers_sub[i]
            void = sc.is_void(answer, prompts[RUNG][i])
            entry = {**ad, "answer": answer, "input": entries[i]["input"],
                     "class": ("non_reachable" if i in non_set
                               else "reachable"),
                     "sub_class": entries[i]["sub_class"],
                     "void": bool(void)}
            if void:
                entry["void_reason"] = (
                    "the item's answer occurs in its own rendered "
                    "prompt — the leak class the items rule out by "
                    "construction; this fire argues nothing")
                all_void.append({**entry, "size": size})
            addresses.append(entry)
        non_void = [ad for ad in addresses if not ad["void"]]
        all_new_fires += len(addresses)
        fired_items = sorted({ad["item"] for ad in non_void})
        counts = {i: 0 for i in items}
        for ad in non_void:
            counts[ad["item"]] += 1
        fires[size] = {
            "new": c.rate_entry(len(non_void), rc["n_draws_total"]),
            "raw_fire_count_pre_void": len(addresses),
            "addresses": addresses,
            "fired_items": fired_items,
            "fired_reachable": [i for i in fired_items if i in reach_set],
            "fired_non_reachable": [i for i in fired_items if i in non_set],
            "per_item_counts": {str(i): counts[i] for i in items
                                if counts[i]},
            "per_seed_full_string": {s: v["full_string"]
                                     for s, v in rc["per_seed"].items()},
        }

    # ---- primary + replication (computed before branching)
    tests = {}
    count_weighted = {}
    for size in SIZES_3E:
        f = fires[size]
        tests[size] = st.primary_test(
            len(f["fired_items"]), len(f["fired_non_reachable"]),
            N=len(items), K=len(non_set))
        counts_list = [sum(1 for ad in f["addresses"]
                           if not ad["void"] and ad["item"] == i)
                       for i in items]
        non_idx = [j for j, i in enumerate(items) if i in non_set]
        count_weighted[size] = st.count_weighted_test(counts_list, non_idx)

    # ---- specificity arm (§5.5), both sizes, same draws
    specificity = {}
    for size in SIZES_3E:
        specificity[size] = _specificity_arm(
            size, new_cells[size]["rows_by_item"], partition,
            prompts[RUNG], answers_by_item, answer_type, score_fn)
        t = specificity[size]["test"]
        specificity[size]["annotation"] = st.specificity_annotation(
            p=t["p"], events=t["events"], m_s_min=m_s_min)
        specificity[size]["m_s_min"] = m_s_min

    # ---- pooled + class tables (§5.4: reporting, never adjudicated)
    pooled = {}
    texture = {}
    entropy = {}
    persistence = {}
    blind = {}
    s2 = {}
    for size in SIZES_3E:
        b = base[size]
        f = fires[size]
        k_new = K_NEW_3E[size]
        k_base = b["n_draws_per_item"]
        new_counts = {i: sum(1 for ad in f["addresses"]
                             if not ad["void"] and ad["item"] == i)
                      for i in items}

        def cls_entry(idx):
            n_items_ = len(idx)
            new_f = sum(new_counts[i] for i in idx)
            base_f = sum(b["per_item"][i] for i in idx)
            fired = sorted(i for i in idx if new_counts[i])
            return {
                "n_items": n_items_,
                "new_fired_items": fired,
                "new_fired_fraction": (len(fired) / n_items_
                                       if n_items_ else None),
                "new": c.rate_entry(new_f, n_items_ * k_new),
                "committed": c.rate_entry(base_f, n_items_ * k_base),
                "pooled": c.rate_entry(base_f + new_f,
                                       n_items_ * (k_new + k_base)),
            }

        sub = partition["sub_classes"]
        texture[size] = {
            "transposition": cls_entry(sub["transposition"]),
            "rotation": cls_entry(sub["rotation"]),
            "non_reachable": cls_entry(sub["non_reachable"]),
            "reachable": cls_entry(partition["reachable"]),
        }
        rep = cls_entry(items)
        pooled[size] = {
            "repeat_class": {**rep["pooled"],
                             "committed_count": rep["committed"]["count"],
                             "new_count": rep["new"]["count"]},
            "reachable": texture[size]["reachable"]["pooled"],
            "non_reachable": texture[size]["non_reachable"]["pooled"],
            "per_item_pooled_counts": {
                str(i): b["per_item"][i] + new_counts[i] for i in items
                if b["per_item"][i] + new_counts[i]},
        }
        non_pooled = texture[size]["non_reachable"]["pooled"]
        reach_pooled = texture[size]["reachable"]["pooled"]
        non_upper = non_pooled.get("cp95_upper",
                                   (non_pooled.get("ci95") or [None, None])[1])
        pooled[size]["rate_ratio_non_over_reachable"] = {
            "non_reachable_pooled_cp95_upper": non_upper,
            "reachable_pooled_rate": reach_pooled["rate"],
            "ratio_upper_bound": (non_upper / reach_pooled["rate"]
                                  if reach_pooled["rate"] else None),
            "note": "CP95 upper bound on the non-reachable pooled rate "
                    "over the reachable pooled point rate — the "
                    "NO-SHORTCUT headline (§6)",
        }
        ad_f = sum(b["per_item"][i] for i in all_distinct)
        ad_n = len(all_distinct) * k_base
        entropy[size] = {
            "non_reachable_pooled": texture[size]["non_reachable"]["pooled"],
            "non_reachable_new": texture[size]["non_reachable"]["new"],
            "all_distinct_committed": {**c.rate_entry(ad_f, ad_n),
                                       "n_items": len(all_distinct)},
            "entropy_bits": {"non_reachable": 6.0, "all_distinct": 8.0},
            "scramble_prior_factor": SCRAMBLE_PRIOR_FACTOR,
            "note": "descriptive, event-starved by design (§5.4): both "
                    "classes are two-edit from their reverse; the "
                    "all-distinct items are NOT resampled",
        }
        prev = sorted(i for i in items if b["per_item"][i])
        never_reach = [i for i in partition["reachable"]
                       if not b["per_item"][i]]
        persistence[size] = {
            "previously_fired_items": prev,
            "new_fired_items": f["fired_items"],
            "overlap": sorted(set(prev) & set(f["fired_items"])),
            "new_fires_on_previously_fired":
                sum(new_counts[i] for i in prev),
            "never_fired_reachable": {
                "items": never_reach,
                "new": c.rate_entry(sum(new_counts[i] for i in never_reach),
                                    len(never_reach) * k_new),
                "new_fired_items": sorted(i for i in never_reach
                                          if new_counts[i])},
            "note": "persistence is NOT a competing forecaster (§8): it "
                    "requires having sampled",
        }
        blind[size] = {
            "new_zero_bound_per_class": {
                "non_reachable": a3.cp_upper(0, len(non_set) * k_new),
                "reachable": a3.cp_upper(0, len(reach_set) * k_new)},
            "pooled_zero_bound_non_reachable":
                a3.cp_upper(0, len(non_set) * (k_new + k_base)),
        }
        s2[size] = {
            "non_reachable_new_draws": _s2_block(
                new_cells[size]["rows_by_item"], partition["non_reachable"],
                entries, answers_by_item, answer_type, score_fn,
                prompts[RUNG]),
            "all_distinct_committed_draws": _s2_block(
                b["rows"], all_distinct, entries, answers_by_item,
                answer_type, score_fn, prompts[RUNG]),
            "note": "descriptive (§5.5 S2): the copy-misfire reading "
                    "predicts the first-character-matched neighbours "
                    "dominate the reverse by a wide margin; no test",
        }

    out = {
        "worlds": list(WORLDS_3E),
        "adjudicating_size": ADJUDICATING_SIZE,
        "replication_size": REPLICATION_SIZE,
        "partition": {
            "n_items": len(items), "items": items,
            "reachable": partition["reachable"],
            "non_reachable": partition["non_reachable"],
            "sub_class_sizes": {k: len(v) for k, v in
                                partition["sub_classes"].items()},
            "arm_items": partition["arm_items"],
            "arm_sit_out": partition["arm_sit_out"],
            "variants_reachable_counts": {
                v: len(partition["variants"][v]["reachable"])
                for v in partition["variants"]},
            "m_min": m_min,
            "m_min_anti_disclosed": power_pin["m_min_anti_disclosed"],
            "thin_max": power_pin["thin_max"],
            "m_s_min": m_s_min,
            "in_sample_note":
                "the partition was chosen after seeing the 10 committed "
                "fired items (§1) — in-sample motivation, not evidence; "
                "the confirmatory statistic sees only NEW draws",
        },
        "gate1": gate1,
        "gate1_total_draws_compared": gate1_total,
        "scorer_gates": {"passed": scorer_gates["passed"],
                         "gate_a_addresses": scorer_gates["gate_a"].get(
                             "addresses"),
                         "gate_b_counts": scorer_gates["gate_b"].get(
                             "counts")},
        "fires": fires,
        "tests": tests,
        "count_weighted": count_weighted,
        "sub_class_texture": texture,
        "entropy_contrast": entropy,
        "persistence": persistence,
        "pooled": pooled,
        "specificity": specificity,
        "s2_descriptive": s2,
        "mean_draw_len_new": {s: new_cells[s]["mean_draw_len"]
                              for s in SIZES_3E},
        "blind_region": blind,
        "twin_record": {
            **twin,
            "statement": (
                f"no new twin was sampled (§4): exp3's committed twin "
                f"record — 0 fires across all 8 untrained cells, "
                f"{twin['reversal_twin_draws']:,} reversal-twin draws + "
                f"{twin['control_twin_draws']:,} control-twin draws — is "
                f"the standing contamination referent, re-asserted from "
                f"raw draws at this load"),
        },
        "leak_voids": all_void,
        "luck_floor": c.luck_floor(pt.SUBSET_LENGTH),
        "alpha": st.ALPHA_3E,
    }

    # 1. stream continuity: zero tolerance, diffs already disclosed
    if gate1_diff_cells:
        detail = "; ".join(f"{k} ({n} differing draws)"
                           for k, n in sorted(gate1_diff_cells.items()))
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": (
                    f"gate 1 failed — the re-derivation of 3d's "
                    f"committed gate-1 streams through the production "
                    f"45-item path differs from the committed bytes at: "
                    f"{detail}. The streams are deterministic on this "
                    f"stack (five consecutive byte-identical "
                    f"reproductions through 3d); a single differing byte "
                    f"means the generation law changed, and no new draw "
                    f"is interpretable. Differing draws disclosed "
                    f"verbatim in the gate1 table.")}

    # 2. contamination/leak: every observed fire void
    if all_new_fires > 0 and len(all_void) == all_new_fires:
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": (
                    f"every one of the {all_new_fires} new fired draws "
                    f"is void — each fire's answer occurs in its own "
                    f"prompt (evidence in leak_voids, verbatim). The "
                    f"leak class the items rule out by construction is "
                    f"live, so no fire places anything and no silence "
                    f"bounds anything.")}

    # 3. adjudicate (§6): the 1b primary alone, mechanical order
    adj = tests[ADJUDICATING_SIZE]
    rep = tests[REPLICATION_SIZE]
    n_f = adj["n_fired"]
    x_obs = adj["x_non_reachable"]
    thin = bool(adj["thin"])
    thin_txt = " THIN" if thin else ""
    rep_rejects = rep["p_low"] is not None and rep["p_low"] <= st.ALPHA_3E
    rep_txt = ("replicated at 410m" if rep_rejects else
               "unreplicated at 410m's disclosed power")
    spec = specificity[ADJUDICATING_SIZE]
    ann = spec["annotation"]
    ann_txt = f" ({ann.lower()})"
    f_txt = (f"n = {n_f} new-fired item(s), X = {x_obs} of them "
             f"non-reachable (null expectation "
             f"{adj['expected_x_under_null']:.2f})")
    spec_txt = (f"specificity arm: {ann} — T_s = {spec['test']['T_obs']} "
                f"reverse emissions of {spec['test']['events']} matched "
                f"events, p = "
                f"{spec['test']['p'] if spec['test']['p'] is None else format(spec['test']['p'], '.4g')}"
                f", m_s,min = {m_s_min}")
    out = {**out, "adjudication": {
        "n_fired": n_f, "x_non_reachable": x_obs, "thin": thin,
        "m_min": m_min, "p_low": adj["p_low"], "p_high": adj["p_high"],
        "replication_410m": {"n_fired": rep["n_fired"],
                             "x_non_reachable": rep["x_non_reachable"],
                             "p_low": rep["p_low"],
                             "rejects": bool(rep_rejects),
                             "thin": rep["thin"]},
        "specificity": {**spec["test"], "annotation": ann,
                        "m_s_min": m_s_min}}}
    thin_note = (" THIN (§6): n ≤ 10 — a rejection here is possible only "
                 "with X = 0, a fragile arrangement." if thin else "")

    if adj["p_low"] is not None and adj["p_low"] <= st.ALPHA_3E:
        return {**out, "verdict": f"SHORTCUT{thin_txt}{ann_txt}",
                "reason": (
                    f"within the repeat class, at identical entropy, the "
                    f"new fires concentrate on items whose reverse is one "
                    f"copy-edit from the input: {f_txt}, one-sided "
                    f"p_low = {adj['p_low']:.6g} ≤ {st.ALPHA_3E} "
                    f"({rep_txt}; the annotation modifies nothing). 3d's "
                    f"STRUCTURED stands as a forecast result, but what it "
                    f"forecast is emission cost — the copy mechanism's "
                    f"misfire landing on the right string — not graded "
                    f"reversal competence (§6). {spec_txt}. Every fire "
                    f"and every competitor emission disclosed verbatim "
                    f"with its (item, seed, draw) address."
                    + thin_note)}
    if adj["p_high"] is not None and adj["p_high"] <= st.ALPHA_3E:
        return {**out, "verdict": f"ANTI-SHORTCUT{thin_txt}{ann_txt}",
                "reason": (
                    f"the reverse-direction test rejects: {f_txt}, "
                    f"upper-tail p_high = {adj['p_high']:.6g} ≤ "
                    f"{st.ALPHA_3E} — non-reachable items fire MORE. This "
                    f"falsifies the copy-misfire reading outright and is "
                    f"reported with the same prominence; no story was "
                    f"prepared for it (§6). {spec_txt}." + thin_note)}
    if n_f >= m_min:
        return {**out, "verdict": f"NO-SHORTCUT{thin_txt}{ann_txt}",
                "reason": (
                    f"no rejection in either direction: {f_txt}, p_low = "
                    f"{adj['p_low']:.6g}, p_high = {adj['p_high']:.6g}, "
                    f"n = {n_f} ≥ m_min = {m_min} — the fired set was "
                    f"large enough to reject and did not. Reachability "
                    f"does not drive the concentration at this "
                    f"resolution; the entropy reading survives (3e "
                    f"cannot split 'easier to reverse' from 'more "
                    f"probable a priori' and says so). Headline: the "
                    f"CP95 upper bound on the non-reachable/reachable "
                    f"pooled rate ratio is "
                    f"{pooled[ADJUDICATING_SIZE]['rate_ratio_non_over_reachable']['ratio_upper_bound']}. "
                    f"{spec_txt}." + thin_note)}
    return {**out, "verdict": f"UNINFORMATIVE{thin_txt}{ann_txt}",
            "reason": (
                f"n = {n_f} < m_min = {m_min}: no arrangement of so few "
                f"fired items can reject at α = {st.ALPHA_3E}, so the "
                f"tranche cannot adjudicate the reachability hypothesis. "
                f"Retracts NOTHING (§6): 3d's verdict, the committed "
                f"rates, and the partition's in-sample texture all "
                f"stand; the tranche's fires and silences ship as counts "
                f"and CP bounds regardless (pooled repeat class "
                f"{pooled[ADJUDICATING_SIZE]['repeat_class']['count']}/"
                f"{pooled[ADJUDICATING_SIZE]['repeat_class']['n_draws']} "
                f"at 1b). {spec_txt}." + thin_note)}


# ----------------------------------------------------------------- driver

def run(root=EXP3E) -> dict:
    """Load all four trees through the frozen producers, re-assert
    every standing referent, and adjudicate. No model is loaded;
    nothing is sampled; every input is a committed record or a frozen
    loader's output (§2)."""
    check_frozen_imports_3e()
    check_stream_map_3e()
    d.check_stream_map_3d()
    c.check_stream_map()
    verify_fn = c.load_verify_3c()
    score_fn = sc.load_scorer()
    gate2 = a3.load_gate2_referents()
    sha_refs = a3.items_sha_referents(gate2)
    for rung in (RUNG, a3.POSITIVE_CONTROL):
        if sha_refs.get(rung) != ITEMS_SHA_PIN[rung]:
            raise ValueError(
                f"3b-derived items sha for {rung} "
                f"({sha_refs.get(rung)}) disagrees with the §4 literal "
                f"pin ({ITEMS_SHA_PIN[rung]}) — two committed sources, "
                f"one value, and they differ")
    items = d.load_item_file(RUNG)          # sha + strata pins (3d's)
    ctrl_items = d.load_item_file(a3.POSITIVE_CONTROL)
    answers = items["answers"]
    partition = load_partition_3e(answers, subset_pin=SUBSET_ITEMS_PIN,
                                  file_sha_pin=PARTITION_FILE_SHA256,
                                  non_reachable_pin=NON_REACHABLE_PIN)
    if len(all_distinct_len4(answers)) != N_ALL_DISTINCT_LEN4:
        raise ValueError("the all-distinct len-4 class is not the "
                         f"committed {N_ALL_DISTINCT_LEN4}")
    power_pin = load_power_pin_3e(partition)
    rows = load_committed_rows()
    base = committed_base_3e(rows, answers, items["answer_type"], score_fn,
                             ctrl_answers=ctrl_items["answers"],
                             ctrl_answer_type=ctrl_items["answer_type"])
    for size in SIZES_3E:
        if base["ctrl_gate_b"][size] != CTRL_SAMPLED_RATE_PIN[size]:
            raise ValueError(
                f"ctrl_copy re-scored at {size} gives "
                f"{base['ctrl_gate_b'][size]} against the §4 pin "
                f"{CTRL_SAMPLED_RATE_PIN[size]} — gate (b) does not "
                f"reproduce at analysis time")
        if base[size]["subset_addresses"] != REPEAT_CLASS_FIRES_PIN[size]:
            raise ValueError(f"gate (a) does not reproduce at {size}")
    twin = load_twin_record(EXP3, verify_fn=verify_fn)
    new_cells = load_new_cells_3e(root, verify_fn=verify_fn,
                                  items=SUBSET_ITEMS_PIN, answers=answers,
                                  labels=items["probe_labels"],
                                  answer_type_pin=items["answer_type"])
    for size in SIZES_3E:
        if new_cells[size]["items_sha256"] != ITEMS_SHA_PIN[RUNG]:
            raise ValueError(
                f"{size}: tranche items_sha256 "
                f"{new_cells[size]['items_sha256']} against the §4 pin")
    gate1_records = load_gate1_3e(root)
    check_gate1_committed_shas_3e(gate1_records)
    check_gate1_vs_tranche_3e(gate1_records, new_cells,
                              items_sha_pin=ITEMS_SHA_PIN[RUNG])
    scorer_gates = load_scorer_gates_3e(root)
    prompts = c.load_prompts(sha_refs, rungs=(RUNG,))
    return verdict_3e(new_cells, gate1_records, scorer_gates, base,
                      partition, power_pin, prompts, twin, answers=answers,
                      score_fn=score_fn, answer_type=items["answer_type"])


if __name__ == "__main__":
    v = run()
    print(json.dumps({k: v[k] for k in
                      ("verdict", "reason", "adjudication",
                       "gate1_total_draws_compared")
                      if k in v}, indent=1))
