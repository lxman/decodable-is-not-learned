"""Frozen analysis for Experiment 3d (design §5, §6): rank prediction —
is the sampled channel forecastable at ITEM grain?

3c established that the sampled channel is item-heterogeneous: 13
committed fires (exp3 + 3c) land on 9 distinct items out of 500, with
'ecde' carrying 4 across two model sizes and the single len-6 fire
landing on the len-6 answer with the cheapest internal structure. This
module adjudicates whether that heterogeneity is FORECASTABLE: a
frozen, model-free structural functional of the answer string —
selected in-sample on the committed fires (disclosed, §5.1), committed
with its 500 values and tie structure BEFORE any new draw — predicts
which items fire in a tranche that does not yet exist
(reverse_string/1b seeds 16–39 adjudicating; /410m seeds 16–27
replicating, non-gating). The primary is the §5.3 within-length-stratum
exact permutation rank test on the new-fired item set; worlds are
STRUCTURED / ANTI-STRUCTURED / UNSTRUCTURED / UNINFORMATIVE with the
frozen THIN qualifier on |F| ≤ 4 (§6).

THE ONLY SCORED OUTCOME is the same verified full-string fire 3/3c
used, under 3c's ratified total verify wrapper — no new metric, no new
threshold (§2: the Schaeffer trap, refused by construction). Every
fire is disclosed verbatim with its (item, seed, draw) address; every
zero ships as a Clopper–Pearson bound; leak-void semantics are 3c's,
unchanged (§5.2).

TWO-TREE-PLUS-ONE DISCIPLINE. The committed base loads through the
predecessors' OWN frozen loaders (exp3's analyze_3, 3c's analyze_3c —
both recompute every tally from raw draws and refuse disagreement);
the new tranche loads through the shard loaders below (same rule,
seed blocks 16–39/16–27). The 13 committed fire addresses are
re-extracted from committed raw bytes at every analysis run and must
equal the §4 pin. The teacher-forced scoring records (§5.5) are
validated non-gating inputs: their ctrl_copy known-answer gate must
read PASS or the load hard-errors — a campaign that sampled past a
failed scoring gate violated the frozen order, and nothing here will
adjudicate it.

LINEAGE. Frozen things are imported, never copied (§11): exp3's
sampler (namespace string 'exp3' DELIBERATELY — seeds 16–39 extend
the same committed stream families), exp3's loaders and CP helpers,
3c's total verify wrapper, leak-void prompt loader (finding-A pinned),
tally/loader machinery, and rate entries. The imported files are
sha-pinned below and asserted at run time (3c's
FROZEN_IMPORT_SHA256 superset): exp3 and 3c are closed, and a changed
frozen byte means these are not the committed streams.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import sys
from pathlib import Path

from experiments.exp3 import analyze_3 as a3
from experiments.exp3.sampler import stream_seed
from experiments.exp3c import analyze_3c as c
from experiments.exp3d import functional_3d as fl
from experiments.exp3d import rank_test_3d as rt

# ------------------------------------------------------------ the matrix

RUNG = "reverse_string"                # the 2b survivor; rev_string7 is
                                       # EXCLUDED with bounds standing (§3)
SIZES_3D = ("410m", "1b")
ADJUDICATING_SIZE = "1b"               # §5.3: 1b adjudicates
REPLICATION_SIZE = "410m"              # §5.4: non-gating replication
CELLS_3D = tuple((RUNG, s, "trained") for s in SIZES_3D)

NEW_SEEDS_3D = {"410m": tuple(range(16, 28)),   # §3: 12 new seeds
                "1b": tuple(range(16, 40))}     # §3: 24 new seeds
DRAWS_PER_SEED_3D = 64                          # exp3's reversal dps
# §10.4's durable/commit unit: blocks of 4 seeds — each block is one
# shard on disk, one skip-if-exists campaign unit, one commit+push
SEED_BLOCKS = {
    "410m": (tuple(range(16, 20)), tuple(range(20, 24)),
             tuple(range(24, 28))),
    "1b": (tuple(range(16, 20)), tuple(range(20, 24)),
           tuple(range(24, 28)), tuple(range(28, 32)),
           tuple(range(32, 36)), tuple(range(36, 40))),
}
K_NEW_3D = {s: len(NEW_SEEDS_3D[s]) * DRAWS_PER_SEED_3D
            for s in SIZES_3D}                  # 768 / 1536 per item
K_BLOCK = 4 * DRAWS_PER_SEED_3D                 # 256 draws per item

GATE1_SEED_3D = 8      # §4: 3c's seed-8 streams, fire-carrying at both
                       # sizes — the strongest byte-identity check
SCORING_RUNGS = (RUNG, a3.POSITIVE_CONTROL)     # §5.5: + ctrl_copy gate

N_ITEMS = 500
CI_LEVEL = 0.95        # program reporting convention since 1c

EXP3D = Path(__file__).resolve().parent
EXPERIMENTS = EXP3D.parent
EXP3 = a3.EXP3
EXP3C = c.EXP3C

RESULTS = EXP3D / "results"
SAMPLING_ROOT = RESULTS / "sampling"
GATE1_ROOT = RESULTS / "gate1"
SCORING_ROOT = RESULTS / "scoring"
STREAM_MAP_3D_PATH = EXP3D / "stream_map_3d.json"
SELECTION_PATH = EXP3D / "functional_selection_3d.json"
POWER_PATH = EXP3D / "power_3d.json"

# ----------------------------------------------------- frozen-file pins
#
# 3c's four exp3 pins inherited verbatim, plus the 3c files 3d's
# meaning depends on (the verify wrapper and loaders, the committed
# stream map, the committed verdict record = the fires-table referent),
# plus 2c's harness (the verify criterion and the prompt renderer ARE
# verdict inputs — finding A's spirit, one level down), plus the item
# files themselves (§4: "the reverse_string item file, its sha").

FROZEN_IMPORT_SHA256_3D = {
    EXP3 / "sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
    EXP3 / "analyze_3.py":
        "aa0cb2374fbdffde2f9eaae26cee1ce51f9f42c0b32fd89f4f8754c983a92274",
    EXP3 / "stream_map.json":
        "ea299282342de59d8267682afbf51931521c742a7950215d7acfdc40584fe7a9",
    EXP3 / "results" / "verdict.json":
        "0bce2f91460dd20dc047127da24f6c650aebbe48fdd8f46f5d24da22fa3489ff",
    EXP3C / "analyze_3c.py":
        "66b78ffbedb808625ed33019f29d2ef8ec9d0f31a1115eb7cb08ad3e67d42d84",
    EXP3C / "stream_map_3c.json":
        "a49d541ca0bd14c0209ce02749f8109498e4db885305898e6662e55d9a76e402",
    EXP3C / "results" / "verdict.json":
        "5f8999880df37a47c3d5bb000400eac621c369071f9f216ac0e67e22e074589e",
    EXPERIMENTS / "exp2c" / "harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
}

# §4: the committed 3c draws files — gate 1's comparison targets and
# the pooling base's new-seed half. Literal, and ALSO compared against
# what the gate-1 records attest (finding B, both directions).
COMMITTED_3C_DRAWS_SHA256 = {
    "410m":
        "b3422b4fcf492519c697ca9bb2a668713c6bcdf178147c157af79c8cad05561e",
    "1b":
        "d673dafceb47f1d5affcbc30080f3c79caf7d3f1053853d7e76a28433a6e0b46",
}

# §4: the item-file pins. reverse_string lives in the 2b battery,
# ctrl_copy in the 2c battery; both must ALSO equal the 3b-derived
# sha_refs at run time (two committed sources, one value).
ITEMS_SHA_PIN = {
    "reverse_string":
        "ad5bdcd944e3b983da42825a493eb813269b0ffebadb64f40fb1ee0f834f68c9",
    "ctrl_copy":
        "b75141477beecbd2933a02d93777bf787a1d39a5693b88436b68d0bdcdab6832",
}

# §3/§4: the complete committed in-sample fire record, verbatim —
# exp3's one fire + 3c's twelve, transcribed from the sha-pinned
# verdict records and RE-EXTRACTED from committed raw bytes at every
# analysis run (hard error on any disagreement). NOTE the item-436
# answer is 'qvux' (the question string is 'xuvq'; the design doc's §3
# list carries the question string there — ledgered at build,
# PROGRESS.md, for freeze ratification).
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
    ),
    "410m": (
        {"item": 123, "seed": 8, "draw": 6, "source": "3c"},
        {"item": 174, "seed": 15, "draw": 42, "source": "3c"},
        {"item": 226, "seed": 6, "draw": 40, "source": "3c"},
    ),
}

# §4: committed per-item fire counts and cell totals — the base the
# tranche pools with (§3's table) and the power alternatives'
# calibration (§7). Derived from COMMITTED_FIRES_PIN; asserted
# consistent at import (a pin that disagrees with its own derivation
# is a transcription error, caught before anything runs).
COMMITTED_FIRE_COUNTS = {
    "1b": {123: 3, 200: 1, 320: 1, 370: 1, 391: 1, 436: 1, 447: 2},
    "410m": {123: 1, 174: 1, 226: 1},
}
COMMITTED_BASE_DRAWS = {"410m": 512_000, "1b": 512_000}   # 16 seeds × 32k

for _s in SIZES_3D:
    _derived: dict[int, int] = {}
    for _ad in COMMITTED_FIRES_PIN[_s]:
        _derived[_ad["item"]] = _derived.get(_ad["item"], 0) + 1
    if _derived != COMMITTED_FIRE_COUNTS[_s]:
        raise AssertionError(
            f"COMMITTED_FIRE_COUNTS[{_s}] disagrees with the address "
            f"pin: {COMMITTED_FIRE_COUNTS[_s]} vs derived {_derived}")

# §4/§5.5: ctrl_copy's committed T = 1.0 SAMPLED verified rates from
# exp3's sha-pinned verdict record — the scoring arm's known-answer
# referent. NOT the greedy .9940, which is a different instrument's
# number (§4). Cross-checked against the pinned record at load.
CTRL_SAMPLED_RATE_PIN = {
    "410m": {"count": 12787, "n_draws": 16000},
    "1b": {"count": 13460, "n_draws": 16000},
}

# §5.5: the ctrl_copy known-answer gate band, frozen at build. The
# canonical-path predicted rate p̂ = mean_i exp(ℓ_i) must satisfy
#   LOWER_FACTOR × committed_rate ≤ p̂ ≤ committed_rate + UPPER_MARGIN.
# Upper side: canonical-path mass cannot exceed total verified mass
# except through the prefix-mass edge (a canonical span continued by a
# word character fails verify but counts in exp(ℓ)) plus CP-scale
# sampling noise on the committed rate (±.006 at n = 16,000) — 0.02
# absolute covers both with room. Lower side: the observed committed
# fires all begin with the canonical leading-space form (13/13,
# span_validation_3d.json) and 3b's greedy control emits it in ≥ .99
# of items, so a scorer finding less than HALF the committed verified
# mass on the canonical path is broken (wrong span, wrong offsets,
# wrong base), not merely loose — every real bug class lands orders of
# magnitude off, and the band is deliberately generous to path
# multiplicity while staying lethal to bugs. Rationale ledgered at
# build (PROGRESS.md); the freeze attacks the band.
CTRL_GATE_LOWER_FACTOR = 0.5
CTRL_GATE_UPPER_MARGIN = 0.02

# §3: strata of the committed battery — asserted from the item file at
# every load, never assumed.
STRATA_PIN = {4: 194, 5: 155, 6: 151}

# 3c's standing twin record (§4): re-asserted from exp3's raw draws at
# every analysis run; NO new twin draws are taken.
TWIN_REVERSAL_DRAWS = 512_000
TWIN_CONTROL_DRAWS = 64_000


def check_frozen_imports_3d() -> None:
    """Hard-error unless every imported frozen file is byte-identical
    to its pin. Superset of 3c's check (its four exp3 pins are the
    same literals); run before anything reads any committed tree."""
    for path, want in FROZEN_IMPORT_SHA256_3D.items():
        got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if got != want:
            raise ValueError(
                f"frozen file {path} has sha256 {got}, expected {want} — "
                f"exp3/3c are closed and their files are 3d's referents; "
                f"a changed byte means these are not the committed "
                f"streams (frozen things stay frozen, executable form)")


def _key(k) -> str:
    return "/".join(k)


# --------------------------------------------------------- item files

def load_item_file(rung: str) -> dict:
    """The committed item file, sha-checked against the §4 pin BEFORE
    parsing (finding A: the analysis-time source must match the pin
    the campaign records carry). Returns answers, probe labels,
    questions, shots, answer_type, and the raw sha."""
    if rung == "reverse_string":
        p = EXPERIMENTS / "exp2b" / "battery" / "items" / f"{rung}.json"
    elif rung == "ctrl_copy":
        p = EXPERIMENTS / "exp2c" / "battery" / "items" / f"{rung}.json"
    else:
        raise ValueError(f"{rung!r} is not a 3d rung")
    raw = p.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != ITEMS_SHA_PIN[rung]:
        raise ValueError(
            f"item file {p} has sha256 {got} against the §4 pin "
            f"{ITEMS_SHA_PIN[rung]} — these are not the committed items")
    cap = json.loads(raw.decode())
    ev = cap["eval_items"]
    if len(ev) != N_ITEMS:
        raise ValueError(f"{p} carries {len(ev)} eval items, not "
                         f"{N_ITEMS}")
    answers = [str(it["answer"]) for it in ev]
    if rung == "reverse_string":
        strata_counts = {L: len(idx)
                         for L, idx in fl.strata_of(answers).items()}
        if strata_counts != STRATA_PIN:
            raise ValueError(
                f"strata {strata_counts} are not the committed "
                f"{STRATA_PIN} — this is not the preregistered battery")
    return {"path": p, "sha256": got,
            "answers": answers,
            "probe_labels": [str(it["probe_label"]) for it in ev],
            "questions": [str(it["question"]) for it in ev],
            "shots": [tuple(s) for s in cap.get("shots", [])][:2],
            "answer_type": cap.get("answer_type", "word")}


def committed_fired_sets() -> dict:
    """The in-sample fired ITEM sets per cell, from the address pin —
    the §5.1 selection inputs (motivation, never evidence)."""
    return {s: sorted({ad["item"] for ad in COMMITTED_FIRES_PIN[s]})
            for s in SIZES_3D}


# ------------------------------------------------------- stream map 3d

def dump_stream_map_3d(path=STREAM_MAP_3D_PATH) -> dict:
    """The committed seed-extension (§3): reverse_string × both sizes ×
    ALL seeds each cell will have pooled (0–39 at 1b, 0–27 at 410m)
    under exp3's exact formula and namespace. Seeds 0–3 duplicate
    exp3's committed entries and 4–15 duplicate 3c's ON PURPOSE — the
    continuity check asserts both overlaps byte-equal, making 'one
    formula governs the whole pooled set' executable across three
    experiments."""
    cells = {}
    for size in SIZES_3D:
        top = NEW_SEEDS_3D[size][-1] + 1
        for s in range(top):
            cells[f"{RUNG}/{size}/trained/s{s}"] = {
                "item0": stream_seed(RUNG, size, "trained", s, 0),
                "item499": stream_seed(RUNG, size, "trained", s, 499),
            }
    out = {
        "formula": "int.from_bytes(sha256('exp3|{rung}|{size}|{mode}|"
                   "s{seed}|i{item}').digest()[:8], 'big') & ((1<<63)-1)",
        "namespace_note": "the namespace string stays 'exp3' "
                          "DELIBERATELY (§3): seeds 16-39 extend the "
                          "same committed stream families exp3 drew 0-3 "
                          "and 3c drew 4-15 from",
        "per_item_substreams": True,
        "chunk_rows": 16,
        "draw_order": "seeds ascending; within a seed, chunks in index "
                      "order; within a chunk, rows in row order; one "
                      "multinomial call per step over all rows",
        "exp3_seeds": list(a3.SEEDS),
        "exp3c_seeds": list(c.NEW_SEEDS),
        "new_seeds": {s: list(NEW_SEEDS_3D[s]) for s in SIZES_3D},
        "seed_blocks": {s: [list(b) for b in SEED_BLOCKS[s]]
                        for s in SIZES_3D},
        "draws_per_seed": DRAWS_PER_SEED_3D,
        "k_new": dict(K_NEW_3D),
        "cells": cells,
    }
    Path(path).write_text(json.dumps(out, indent=1))
    return out


def check_stream_map_3d(path=STREAM_MAP_3D_PATH,
                        exp3_map_path=None,
                        exp3c_map_path=None) -> dict:
    """Hard-error unless the committed 3d map is exactly the formula's
    output AND its overlap entries equal exp3's committed map (seeds
    0–3) and 3c's committed map (seeds 4–15) for both 3d cells."""
    exp3_map_path = exp3_map_path or (EXP3 / "stream_map.json")
    exp3c_map_path = exp3c_map_path or (EXP3C / "stream_map_3c.json")
    m = json.loads(Path(path).read_text())
    e3 = json.loads(Path(exp3_map_path).read_text())
    e3c = json.loads(Path(exp3c_map_path).read_text())
    for other, name in ((e3, "exp3"), (e3c, "exp3c")):
        if m.get("formula") != other.get("formula"):
            raise ValueError(
                f"stream_map_3d formula {m.get('formula')!r} differs "
                f"from {name}'s committed formula — not one law over "
                f"the pooled set")
    want_keys = {f"{RUNG}/{size}/trained/s{s}" for size in SIZES_3D
                 for s in range(NEW_SEEDS_3D[size][-1] + 1)}
    if set(m.get("cells", {})) != want_keys:
        raise ValueError(
            f"stream_map_3d covers {len(m.get('cells', {}))} entries, "
            f"not the 2 cells × their full pooled seed ranges "
            f"({len(want_keys)})")
    for size in SIZES_3D:
        for s in range(NEW_SEEDS_3D[size][-1] + 1):
            k = f"{RUNG}/{size}/trained/s{s}"
            want = {"item0": stream_seed(RUNG, size, "trained", s, 0),
                    "item499": stream_seed(RUNG, size, "trained", s, 499)}
            if m["cells"][k] != want:
                raise ValueError(
                    f"stream_map_3d entry {k} = {m['cells'][k]} "
                    f"disagrees with the frozen formula {want} — the "
                    f"map is not the formula's output")
            if s in a3.SEEDS and m["cells"][k] != e3["cells"][k]:
                raise ValueError(
                    f"stream_map_3d entry {k} disagrees with exp3's "
                    f"committed map — pooling continuity broken")
            if s in c.NEW_SEEDS and m["cells"][k] != e3c["cells"][k]:
                raise ValueError(
                    f"stream_map_3d entry {k} disagrees with 3c's "
                    f"committed map — pooling continuity broken")
    return m


# ------------------------------------------- the frozen functional load

def load_selection(answers, path=SELECTION_PATH, *,
                   fired_sets=None) -> dict:
    """The committed selection record, RECOMPUTED and compared (3a's
    class, refused): the winner, its 500 values, the midranks, the tie
    structure, and the decile bucket are all re-derived from the
    committed answers through the frozen functional code and must
    equal the committed record exactly. The ranks the verdict uses are
    the recomputed ones — the file proves the freeze, the code
    produces the numbers."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(
            f"no committed functional selection record at {p} — the "
            f"frozen functional has no value (3a's class, refused)")
    rec = json.loads(p.read_text())
    fired = fired_sets if fired_sets is not None \
        else committed_fired_sets()
    sel = fl.select_winner(answers, fired["1b"], fired["410m"])
    if rec.get("winner") != sel["winner"]:
        raise ValueError(
            f"committed winner {rec.get('winner')!r} disagrees with the "
            f"recompute {sel['winner']!r} — the selection record is not "
            f"the frozen formula's output on the committed answers")
    name, fn = fl.CANDIDATES[sel["winner_index"]]
    values = fl.candidate_values(fn, answers)
    if rec.get("winner_values") != values:
        raise ValueError(
            "committed winner values disagree with the recompute from "
            "the committed answers — not the frozen functional's output")
    strata = fl.strata_of(answers)
    mids = fl.stratified_midranks(values, strata)
    bucket = fl.decile_bucket(values, strata)
    if rec.get("decile_bucket") != bucket:
        raise ValueError(
            "committed decile bucket disagrees with the recompute — "
            "B is frozen at tag (§5.4) and must reproduce")
    ties = fl.tie_structure(values, strata)
    for L, entry in ties.items():
        want = rec.get("tie_structure", {}).get(L)
        if want != json.loads(json.dumps(entry)):
            raise ValueError(
                f"committed tie structure for stratum {L} disagrees "
                f"with the recompute — the test's effective resolution "
                f"is frozen at tag (§2)")
    return {"winner": sel["winner"], "values": values, "strata": strata,
            "midranks": mids, "bucket": bucket, "ties": ties,
            "selection_table": sel["table"], "record": rec}


def load_power_pin(selection, path=POWER_PATH) -> dict:
    """The committed power record's verdict-load-bearing entries —
    m_min (§6's UNINFORMATIVE bar) recomputed from the frozen ranks
    and compared against the committed value; the rest of the record
    is disclosure, read by no branch."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(
            f"no committed power record at {p} — m_min has no value "
            f"(3a's class, refused)")
    rec = json.loads(p.read_text())
    m_min = rt.m_min_of(selection["values"], selection["strata"])
    if rec.get("m_min") != m_min:
        raise ValueError(
            f"committed m_min {rec.get('m_min')!r} disagrees with the "
            f"recompute {m_min} from the frozen ranks — the "
            f"UNINFORMATIVE bar moved after the freeze")
    return {"m_min": m_min, "record": rec}


# ------------------------------------------------- raw-shard ingestion

def shard_name(block) -> str:
    return f"{RUNG}.s{block[0]}-s{block[-1]}"


def _check_shard_provenance(rec, p, size, block) -> None:
    if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
            (RUNG, size, "trained"):
        raise ValueError(
            f"{p} contents ({rec.get('rung')}/{rec.get('size')}/"
            f"{rec.get('mode')}) disagree with its path")
    n = rec.get("n_items")
    if not isinstance(n, int) or n <= 0:
        raise ValueError(f"{p}: n_items {n!r} is not a count")
    for field in ("probe_labels", "answers"):
        v = rec.get(field)
        if not isinstance(v, list) or len(v) != n:
            raise ValueError(
                f"{p}: {field} has "
                f"{len(v) if isinstance(v, list) else v!r} entries "
                f"against n_items {n}")
    sha = rec.get("items_sha256")
    if not isinstance(sha, str) or not sha:
        raise ValueError(f"{p} carries no items_sha256 — the item-file "
                         f"pin has no value there (3a's class, refused)")
    if rec.get("dtype") != "float32":
        raise ValueError(
            f"{p}: dtype {rec.get('dtype')!r} violates the ledgered "
            f"sampling policy — every probe-size sampling cell is "
            f"float32 (exp3's cell_policy, inherited; the design doc's "
            f"§3 'fp16' is a ledgered slip, PROGRESS.md)")
    if rec.get("untrained_seed") is not None:
        raise ValueError(
            f"{p}: untrained_seed {rec.get('untrained_seed')!r} on a "
            f"trained cell — 3d samples no twins (§4)")
    if rec.get("seeds") != list(block):
        raise ValueError(
            f"{p}: seeds {rec.get('seeds')!r} are not this shard's "
            f"preregistered block {list(block)} (§3)")
    if rec.get("draws_per_seed") != DRAWS_PER_SEED_3D:
        raise ValueError(
            f"{p}: draws_per_seed {rec.get('draws_per_seed')!r} against "
            f"the preregistered {DRAWS_PER_SEED_3D}")
    if rec.get("k_total") != K_BLOCK:
        raise ValueError(
            f"{p}: k_total {rec.get('k_total')!r} against "
            f"4 seeds × {DRAWS_PER_SEED_3D} draws = {K_BLOCK}")


def load_new_cells_3d(root=EXP3D, verify_fn=None, *,
                      n_items=N_ITEMS) -> dict:
    """The 2 cells' NEW draws (§3), shard-per-seed-block, raw streams
    beside their records. Stored per-seed tallies are convenience
    copies: the analyzer RECOMPUTES them from the raw draws and
    refuses any disagreement (exp3's rule, all three trees). Shard
    coverage must be EXACTLY the preregistered block partition — no
    stray files, no missing blocks, no duplicated seeds."""
    if verify_fn is None:
        verify_fn = c.load_verify_3c()   # 3c stop #1: total wrapper
    base = Path(root) / "results" / "sampling"
    want = {}
    for size in SIZES_3D:
        names = set()
        for block in SEED_BLOCKS[size]:
            names.add(f"{shard_name(block)}.json")
            names.add(f"{shard_name(block)}.draws.jsonl.gz")
        want[f"{size}_trained"] = names
    c._refuse_strays_3c(base, want)
    out = {}
    for size in SIZES_3D:
        d = base / f"{size}_trained"
        merged_rows: dict[int, dict] = {}
        answers = labels = answer_type = items_sha = None
        stored_tallies: dict[str, dict] = {}
        for block in SEED_BLOCKS[size]:
            p = d / f"{shard_name(block)}.json"
            gz = d / f"{shard_name(block)}.draws.jsonl.gz"
            if not p.is_file():
                raise FileNotFoundError(
                    f"no 3d shard record for {size} block "
                    f"{block[0]}-{block[-1]} at {p}")
            if not gz.is_file():
                raise FileNotFoundError(
                    f"no raw draws file for {size} block "
                    f"{block[0]}-{block[-1]} at {gz}")
            rec = json.loads(p.read_text())
            _check_shard_provenance(rec, p, size, block)
            if answers is None:
                answers = [str(x) for x in rec["answers"]]
                labels = [str(x) for x in rec["probe_labels"]]
                answer_type = rec.get("answer_type")
                items_sha = rec["items_sha256"]
            else:
                if [str(x) for x in rec["answers"]] != answers or \
                        rec["items_sha256"] != items_sha:
                    raise ValueError(
                        f"{p}: answers or items_sha256 disagree with "
                        f"this cell's other shards — not one battery")
            rows = c._read_rows(gz, rec["n_items"], block,
                                DRAWS_PER_SEED_3D)
            for row in rows:
                i = row["item"]
                tgt = merged_rows.setdefault(i, {"item": i, "draws": {}})
                overlap = set(tgt["draws"]) & set(row["draws"])
                if overlap:
                    raise ValueError(
                        f"{gz}: item {i} carries seed streams "
                        f"{sorted(overlap)} already loaded from another "
                        f"shard — duplicated seeds")
                tgt["draws"].update(row["draws"])
            st = rec.get("per_seed_tallies")
            if not isinstance(st, dict):
                raise ValueError(f"{p} carries no per_seed_tallies")
            dup = set(stored_tallies) & set(st)
            if dup:
                raise ValueError(
                    f"{p}: per-seed tallies for seeds {sorted(dup)} "
                    f"already stored by another shard")
            stored_tallies.update(st)
        seeds = NEW_SEEDS_3D[size]
        rows = [merged_rows[i] for i in sorted(merged_rows)]
        for row in rows:
            if set(row["draws"]) != {str(s) for s in seeds}:
                raise ValueError(
                    f"item {row['item']} covers seeds "
                    f"{sorted(row['draws'])} against the preregistered "
                    f"{list(seeds)} — shard coverage incomplete")
        if len(rows) != n_items:
            raise ValueError(
                f"{size}: {len(rows)} items merged against {n_items}")
        t = c.tally_with_addresses(rows, answers, labels, seeds,
                                   answer_type=answer_type,
                                   verify_fn=verify_fn)
        normalized = None
        try:
            normalized = {k: {f: int(v[f]) for f in
                              ("full_string", "first_char", "n_draws")}
                          for k, v in stored_tallies.items()}
        except (KeyError, TypeError, ValueError):
            normalized = None
        if normalized != t["per_seed"]:
            raise ValueError(
                f"{size}: stored per-seed tallies disagree with the "
                f"recompute from the raw draws — this battery's runner "
                f"and analyzer do not agree on what was drawn")
        full_total = sum(v["full_string"] for v in t["per_seed"].values())
        n_draws = sum(v["n_draws"] for v in t["per_seed"].values())
        if n_draws != n_items * K_NEW_3D[size]:
            raise ValueError(
                f"{size}: {n_draws} draws recomputed against "
                f"{n_items} × {K_NEW_3D[size]}")
        out[size] = {
            "rung": RUNG, "size": size, "mode": "trained", "n": n_items,
            "answers": answers, "probe_labels": labels,
            "answer_type": answer_type, "items_sha256": items_sha,
            "seeds": list(seeds),
            "recomputed": {
                "per_seed": t["per_seed"],
                "full_string_total": int(full_total),
                "n_draws_total": int(n_draws),
                "per_item_full_string": t["per_item_full_string"],
            },
            "addresses": t["addresses"],
            "mean_draw_len": t["total_draw_len"] / n_draws,
        }
    return out


# ------------------------------------------------- gate-1 records (§10.2)

def load_gate1_3d(root=EXP3D) -> dict:
    """The 2 byte re-derivation comparison records: 3c's committed
    seed-8 streams, both sizes, 64 draws/item — re-derived end to end
    and compared with zero tolerance. Shape rules are 3c's
    (reading 8): counts must cover the full stream, every diff
    verbatim with its address, the committed-file sha attested."""
    base = Path(root) / "results" / "gate1"
    want = {f"{size}_trained": {f"{RUNG}.json"} for size in SIZES_3D}
    c._refuse_strays_3c(base, want)
    out = {}
    for size in SIZES_3D:
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
        if rec.get("seeds_rederived") != [GATE1_SEED_3D]:
            raise ValueError(
                f"{p}: seeds_rederived {rec.get('seeds_rederived')!r} — "
                f"3d's gate 1 re-derives 3c's committed seed "
                f"{GATE1_SEED_3D} only (§4: fire-carrying at both sizes)")
        n = rec.get("n_items")
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"{p}: n_items {n!r} is not a count")
        dps = rec.get("draws_per_seed")
        if dps != DRAWS_PER_SEED_3D:
            raise ValueError(
                f"{p}: draws_per_seed {dps!r} against 3c's committed "
                f"{DRAWS_PER_SEED_3D} — a stream of the wrong depth is "
                f"not byte-comparable")
        compared = rec.get("draws_compared")
        if compared != n * dps or compared <= 0:
            raise ValueError(
                f"{p}: draws_compared {compared!r} against n_items {n} "
                f"× draws_per_seed {dps} — a gate-1 record that "
                f"compared nothing has no value (3a's class, refused)")
        sha = rec.get("committed_draws_sha256")
        if not isinstance(sha, str) or not sha:
            raise ValueError(
                f"{p} carries no committed_draws_sha256 — the record "
                f"does not say what it compared against")
        diffs = rec.get("diffs")
        if not isinstance(diffs, list):
            raise ValueError(f"{p}: diffs {diffs!r} is not a list")
        for j, dd in enumerate(diffs):
            if not (isinstance(dd, dict)
                    and isinstance(dd.get("item"), int)
                    and dd.get("seed") == GATE1_SEED_3D
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
        out[size] = {"size": size, "n": n, "draws_per_seed": dps,
                     "draws_compared": compared,
                     "n_diffs": int(rec["n_diffs"]), "diffs": diffs,
                     "committed_draws_sha256": sha,
                     "items_sha256": rec.get("items_sha256"),
                     "model_sha": rec.get("model_sha")}
    return out


def check_gate1_committed_shas_3d(gate1_records, exp3c_root=None,
                                  expected=None) -> None:
    """Finding B, inherited: each gate-1 record attests the sha256 of
    the committed 3c draws file it byte-compared against; the analyzer
    pools those very draws from the 3c tree on disk. This closes the
    loop in BOTH directions: record attestation == hash of the file on
    disk == the §4 literal pin (`expected`, defaulting to
    COMMITTED_3C_DRAWS_SHA256; full-shape worlds pass the true hashes
    of their synthetic trees)."""
    root = Path(exp3c_root) if exp3c_root is not None else EXP3C
    want_pin = expected if expected is not None \
        else COMMITTED_3C_DRAWS_SHA256
    for size in sorted(gate1_records):
        gz = (root / "results" / "sampling" / f"{size}_trained"
              / f"{RUNG}.draws.jsonl.gz")
        if not gz.is_file():
            raise FileNotFoundError(
                f"no committed 3c draws file at {gz} to check gate-1 "
                f"record {size} against")
        got = hashlib.sha256(gz.read_bytes()).hexdigest()
        attested = gate1_records[size]["committed_draws_sha256"]
        if got != attested:
            raise ValueError(
                f"gate-1 record {size} attests a byte comparison "
                f"against committed draws sha256 {attested}, but the "
                f"tree this analysis pools carries {got} at {gz} — the "
                f"continuity attestation and the pooled bytes are not "
                f"about the same file (finding B)")
        if got != want_pin[size]:
            raise ValueError(
                f"3c draws file {gz} has sha256 {got} against the §4 "
                f"literal pin {want_pin[size]} — the pooled base is not "
                f"the committed base")


# ------------------------------------------------ scoring records (§5.5)

def load_scoring_3d(root=EXP3D, *, items_sha_pin=None,
                    ctrl_rate_pin=None, n_items=N_ITEMS) -> dict:
    """The teacher-forced canonical-path records, committed BEFORE any
    new sampling (§10's order): ℓ for all 500 items × both sizes for
    reverse_string, plus ctrl_copy with its known-answer gate. A
    missing record, a failed span round-trip, or a FAILED ctrl gate is
    a HARD ERROR, never a verdict: sampling past a failed scoring gate
    would have violated the frozen order, and nothing downstream may
    adjudicate it. The ℓ arm itself remains non-gating (§5.5) — these
    checks gate the RECORD's integrity, not any hypothesis."""
    items_sha_pin = items_sha_pin if items_sha_pin is not None \
        else ITEMS_SHA_PIN
    ctrl_rate_pin = ctrl_rate_pin if ctrl_rate_pin is not None \
        else CTRL_SAMPLED_RATE_PIN
    base = Path(root) / "results" / "scoring"
    want = {f"{size}_trained": {f"{r}.json" for r in SCORING_RUNGS}
            for size in SIZES_3D}
    c._refuse_strays_3c(base, want)
    out = {}
    for size in SIZES_3D:
        for rung in SCORING_RUNGS:
            p = base / f"{size}_trained" / f"{rung}.json"
            if not p.is_file():
                raise FileNotFoundError(
                    f"no scoring record for {rung}/{size} at {p} — the "
                    f"§10 order requires the scoring pass before any "
                    f"tranche draw")
            rec = json.loads(p.read_text())
            if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
                    (rung, size, "trained"):
                raise ValueError(
                    f"{p} contents ({rec.get('rung')}/"
                    f"{rec.get('size')}/{rec.get('mode')}) disagree "
                    f"with its path")
            if rec.get("dtype") != "float32":
                raise ValueError(f"{p}: dtype {rec.get('dtype')!r} is "
                                 f"not the scoring pass's float32")
            if rec.get("items_sha256") != items_sha_pin[rung]:
                raise ValueError(
                    f"{p}: items_sha256 {rec.get('items_sha256')!r} "
                    f"against the §4 pin {items_sha_pin[rung]} — these "
                    f"are not the committed items")
            n = rec.get("n_items")
            if n != n_items:
                raise ValueError(f"{p}: n_items {n!r} against "
                                 f"{n_items}")
            ell = rec.get("ell")
            if not isinstance(ell, list) or len(ell) != n_items:
                raise ValueError(
                    f"{p}: ell has "
                    f"{len(ell) if isinstance(ell, list) else ell!r} "
                    f"entries against {n_items} (3a's class, refused)")
            for j, v in enumerate(ell):
                if v is not None and not isinstance(v, (int, float)):
                    raise ValueError(f"{p}: ell[{j}] = {v!r} is neither "
                                     f"a float nor the committed None "
                                     f"zero-probability marker")
            spans = rec.get("span_token_ids")
            if not isinstance(spans, list) or len(spans) != n_items:
                raise ValueError(f"{p} carries no complete span table")
            if rec.get("span_round_trip_failures") != 0:
                raise ValueError(
                    f"{p}: span_round_trip_failures "
                    f"{rec.get('span_round_trip_failures')!r} — the "
                    f"canonical path is ill-defined somewhere and the "
                    f"scoring pass should have hard-errored (§5.5)")
            entry = {"rung": rung, "size": size, "ell": ell,
                     "model_sha": rec.get("model_sha"),
                     "items_sha256": rec.get("items_sha256")}
            if rung == a3.POSITIVE_CONTROL:
                gate = rec.get("known_answer_gate")
                if not isinstance(gate, dict):
                    raise ValueError(f"{p} carries no known_answer_gate")
                pin = ctrl_rate_pin[size]
                if gate.get("committed_count") != pin["count"] or \
                        gate.get("committed_n_draws") != pin["n_draws"]:
                    raise ValueError(
                        f"{p}: gate referent "
                        f"({gate.get('committed_count')}/"
                        f"{gate.get('committed_n_draws')}) against the "
                        f"§4 pin ({pin['count']}/{pin['n_draws']}) — "
                        f"the known-answer gate compared against the "
                        f"wrong committed rate")
                if gate.get("passed") is not True:
                    raise ValueError(
                        f"{p}: ctrl_copy known-answer gate did not pass "
                        f"({gate!r}) — the campaign must not have "
                        f"launched (§5.5); nothing here adjudicates "
                        f"draws taken past a failed gate")
                entry["known_answer_gate"] = gate
            out[(rung, size)] = entry
    return out


# ------------------------------------------- committed base (exp3 + 3c)

def build_committed_base(exp3_cells, c3_cells, exp3_addresses,
                         c3_referent_fires=None, *, fires_pin=None,
                         base_draws_pin=None) -> dict:
    """The committed base the tranche pools with (§3's table),
    re-derived from raw committed bytes through the predecessors' own
    frozen loaders, and asserted equal to the §4 address pin — the
    two-pass discipline (3c reading 6) extended across three trees.
    `c3_referent_fires` is the fires table from 3c's sha-pinned
    verdict record; the recompute must reproduce its counts."""
    fires_pin = fires_pin if fires_pin is not None \
        else COMMITTED_FIRES_PIN
    base_draws_pin = base_draws_pin if base_draws_pin is not None \
        else COMMITTED_BASE_DRAWS
    out = {}
    for size in SIZES_3D:
        key = (RUNG, size, "trained")
        cell_key = _key(key)
        e3 = exp3_cells[key]
        c3 = c3_cells[key]
        e3_ads = [{"item": a["item"], "seed": a["seed"],
                   "draw": a["draw"], "source": "exp3"}
                  for a in exp3_addresses[cell_key]]
        c3_ads = [{"item": a["item"], "seed": a["seed"],
                   "draw": a["draw"], "source": "3c"}
                  for a in c3["addresses"]]
        got = sorted(e3_ads + c3_ads,
                     key=lambda a: (a["item"], a["seed"], a["draw"]))
        want = sorted(fires_pin[size],
                      key=lambda a: (a["item"], a["seed"], a["draw"]))
        if got != want:
            raise ValueError(
                f"committed fires re-extracted for {cell_key} disagree "
                f"with the §4 pin: got {got}, pin {want} — the "
                f"in-sample record is not the committed record")
        if c3_referent_fires is not None:
            ref = c3_referent_fires.get(cell_key)
            if not (isinstance(ref, dict)
                    and ref.get("new", {}).get("count")
                    == len(c3_ads)
                    and ref.get("new", {}).get("n_draws")
                    == c3["recomputed"]["n_draws_total"]):
                raise ValueError(
                    f"3c's sha-pinned verdict record disagrees with "
                    f"the recompute at {cell_key}: record "
                    f"{ref.get('new') if isinstance(ref, dict) else ref!r}"
                    f" vs {len(c3_ads)}/"
                    f"{c3['recomputed']['n_draws_total']}")
        n_base = e3["recomputed"]["n_draws_total"] + \
            c3["recomputed"]["n_draws_total"]
        if n_base != base_draws_pin[size]:
            raise ValueError(
                f"{cell_key}: committed base draws {n_base} against the "
                f"§3 table's {base_draws_pin[size]}")
        per_item = [0] * len(c3["answers"])
        for a in got:
            per_item[a["item"]] += 1
        per_seed = {**{s: v["full_string"] for s, v in
                       e3["recomputed"]["per_seed"].items()},
                    **{s: v["full_string"] for s, v in
                       c3["recomputed"]["per_seed"].items()}}
        out[size] = {"fires": len(got), "n_draws": n_base,
                     "addresses": got, "per_item": per_item,
                     "per_seed_full_string": per_seed,
                     "answers": [str(x) for x in c3["answers"]]}
    # the standing twin record, re-asserted from raw draws (§4)
    twin_rev = sum(exp3_cells[(r, s, "untrained")]["recomputed"]
                   ["n_draws_total"] for r in a3.REVERSAL_RUNGS
                   for s in a3.PROBE_SIZES)
    twin_ctrl = sum(exp3_cells[(r, s, "untrained")]["recomputed"]
                    ["n_draws_total"]
                    for r in (a3.POSITIVE_CONTROL, a3.MATCHED_CONTROL)
                    for s in a3.PROBE_SIZES)
    twin_fires = sum(exp3_cells[(r, s, "untrained")]["recomputed"]
                     ["full_string_total"] for r in a3.RUNGS
                     for s in a3.PROBE_SIZES)
    if twin_fires != 0:
        raise ValueError(
            f"{twin_fires} fires recomputed across exp3's untrained "
            f"twin cells — the committed twin record is 0 and a "
            f"nonzero recompute means the trees are not the committed "
            f"trees")
    out["twin"] = {"cells": 8, "fires": 0,
                   "reversal_twin_draws": twin_rev,
                   "control_twin_draws": twin_ctrl}
    return out


# --------------------------------------------------------- descriptives

def _spearman(x, y) -> float:
    """Spearman rank correlation by hand (midranks, Pearson on ranks) —
    descriptive only (§5.5: 'do the two tiers even agree?')."""
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: (v[i], i))
        out = [0.0] * len(v)
        j = 0
        while j < len(order):
            k = j
            while k + 1 < len(order) and \
                    v[order[k + 1]] == v[order[j]]:
                k += 1
            mid = (j + 1 + k + 1) / 2.0
            for t in range(j, k + 1):
                out[order[t]] = mid
            j = k + 1
        return out

    rx, ry = ranks(x), ranks(y)
    n = len(rx)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def ell_cost_values(ell) -> list:
    """The scoring arm's cost vector for the §5.3 test: cost = −ℓ,
    ascending = cheaper; a None ℓ (fp32-zero canonical path) is the
    most expensive value, tied at +inf."""
    return [float("inf") if v is None else -float(v) for v in ell]


WORLDS_3D = ("STRUCTURED", "ANTI-STRUCTURED", "UNSTRUCTURED",
             "UNINFORMATIVE")

CALIBRATION_CAVEAT = (
    "predicted fires = Σ_i k_i × exp(ℓ_i) is a LOWER bound on expected "
    "verified fires in the leading-space form (the canonical "
    "tokenization is one path among the verify-accepted set), except "
    "for the prefix-mass edge: a canonical span continued by a word "
    "character counts in exp(ℓ) but fails verify. Descriptive only; "
    "no calibration world gates anything (§5.5).")


def verdict_3d(new_cells, gate1_records, scoring, base, selection,
               power_pin, prompts) -> dict:
    """Design §6, adjudicated in precedence order, with everything
    computed and disclosed BEFORE the first branch so no gate can hide
    another's evidence. Provenance failures are hard errors raised by
    the loaders, never verdicts. Adjudication is the 1b primary
    statistic alone; 410m attaches as annotation and modifies
    nothing."""
    values = selection["values"]
    strata = selection["strata"]
    m_min = power_pin["m_min"]
    for size in SIZES_3D:
        if new_cells[size]["answers"] != base[size]["answers"]:
            raise ValueError(
                f"{size}: tranche answers disagree with the committed "
                f"base's — not one battery across the three trees")

    # ---- gate 1 (computed first, branched first)
    gate1 = {s: {"draws_compared": g["draws_compared"],
                 "n_diffs": g["n_diffs"], "diffs": g["diffs"],
                 "committed_draws_sha256": g["committed_draws_sha256"]}
             for s, g in sorted(gate1_records.items())}
    gate1_total = sum(v["draws_compared"] for v in gate1.values())
    gate1_diff_cells = {s: v["n_diffs"] for s, v in gate1.items()
                        if v["n_diffs"] > 0}

    # ---- the new fires, leak-void applied per fire (3c semantics,
    # unchanged, §5.2)
    fires = {}
    all_new_fires = 0
    all_void = []
    for size in SIZES_3D:
        cell = new_cells[size]
        rc = cell["recomputed"]
        addresses = []
        for ad in cell["addresses"]:
            i = ad["item"]
            answer = cell["answers"][i]
            void = str(answer).casefold() in prompts[RUNG][i].casefold()
            entry = {**ad, "answer": answer,
                     "answer_len": len(str(answer)), "void": bool(void)}
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
        fires[size] = {
            "new": c.rate_entry(len(non_void), rc["n_draws_total"]),
            "raw_fire_count_pre_void": len(addresses),
            "addresses": addresses,
            "fired_items": fired_items,
            "per_seed_full_string": {s: v["full_string"]
                                     for s, v in rc["per_seed"].items()},
        }

    # ---- the primary and replication tests (computed before branching)
    tests = {}
    for size in SIZES_3D:
        tests[size] = rt.stratified_rank_test(values, strata,
                                              fires[size]["fired_items"])

    # ---- pooled + strata tables (§5.4: reporting, never adjudicated)
    pooled = {}
    strata_tables = {}
    for size in SIZES_3D:
        non_void_n = fires[size]["new"]["count"]
        k_pool = base[size]["fires"] + non_void_n
        n_pool = base[size]["n_draws"] + \
            new_cells[size]["recomputed"]["n_draws_total"]
        pooled[size] = {**c.rate_entry(k_pool, n_pool),
                        "committed_count": base[size]["fires"],
                        "new_count": non_void_n}
        cell_t = {}
        base_per_item_draws = base[size]["n_draws"] \
            // new_cells[size]["n"]
        for length, idx in sorted(strata.items()):
            idx_set = set(idx)
            new_f = sum(1 for ad in fires[size]["addresses"]
                        if not ad["void"] and ad["item"] in idx_set)
            base_f = sum(base[size]["per_item"][i] for i in idx)
            n_new = len(idx) * K_NEW_3D[size]
            n_p = len(idx) * (K_NEW_3D[size] + base_per_item_draws)
            cell_t[str(length)] = {
                "n_items": len(idx),
                "new": c.rate_entry(new_f, n_new),
                "pooled": c.rate_entry(base_f + new_f, n_p),
                "luck_floor": c.luck_floor(length),
            }
        strata_tables[size] = cell_t

    # ---- named secondaries (§5.4)
    bucket = selection["bucket"]
    bucket_tests = {s: rt.bucket_tail_p(strata, bucket,
                                        fires[s]["fired_items"])
                    for s in SIZES_3D}
    committed_fired = committed_fired_sets()
    persistence = {}
    for size in SIZES_3D:
        prev = set(committed_fired[size])
        f_new = set(fires[size]["fired_items"])
        persistence[size] = {
            "previously_fired_items": sorted(prev),
            "new_fired_items": sorted(f_new),
            "overlap": sorted(prev & f_new),
            "note": "persistence is NOT a competing forecaster (§5.4): "
                    "it requires having sampled, which is exactly what "
                    "a from-below forecast does without",
        }
    unstrat_auc = {}
    for size in SIZES_3D:
        f = fires[size]["fired_items"]
        u = [i for i in range(new_cells[size]["n"])
             if i not in set(f)]
        unstrat_auc[size] = (fl.stratum_auc(values, f, u)
                            if f and u else None)

    # ---- the scoring arm (§5.5: named secondary + descriptive
    # calibration; gates nothing)
    scoring_arm = {}
    for size in SIZES_3D:
        ell = scoring[(RUNG, size)]["ell"]
        cost = ell_cost_values(ell)
        s_test = rt.stratified_rank_test(cost, strata,
                                         fires[size]["fired_items"])
        f = fires[size]["fired_items"]
        u = [i for i in range(new_cells[size]["n"])
             if i not in set(f)]
        calib = {}
        for length, idx in sorted(strata.items()):
            pred = sum(K_NEW_3D[size] * math.exp(ell[i])
                       for i in idx if ell[i] is not None)
            obs = sum(1 for ad in fires[size]["addresses"]
                      if not ad["void"] and ad["item"] in set(idx))
            calib[str(length)] = {"predicted_fires_lower_bound": pred,
                                  "observed_non_void_fires": obs}
        scoring_arm[size] = {
            "rank_test": s_test,
            "unstratified_auc": (fl.stratum_auc(cost, f, u)
                                 if f and u else None),
            "spearman_functional_vs_ell_cost": _spearman(values, cost),
            "none_ell_items": sum(1 for v in ell if v is None),
            "calibration_by_stratum": calib,
            "calibration_caveat": CALIBRATION_CAVEAT,
            "known_answer_gate":
                scoring[(a3.POSITIVE_CONTROL, size)]["known_answer_gate"],
        }

    # ---- blind region + descriptives
    blind = {}
    for size in SIZES_3D:
        n_new = new_cells[size]["recomputed"]["n_draws_total"]
        n_pool = n_new + base[size]["n_draws"]
        blind[size] = {
            "new_zero_bound": a3.cp_upper(0, n_new),
            "pooled_zero_bound": a3.cp_upper(0, n_pool),
        }
    per_seed_view = {}
    for size in SIZES_3D:
        per_seed_view[size] = {
            **base[size]["per_seed_full_string"],
            **fires[size]["per_seed_full_string"]}

    out = {
        "worlds": list(WORLDS_3D),
        "adjudicating_size": ADJUDICATING_SIZE,
        "replication_size": REPLICATION_SIZE,
        "functional": {
            "winner": selection["winner"],
            "m_min": m_min,
            "m_min_anti_direction_disclosed":
                rt.m_min_of(values, strata, direction="high"),
            "tie_structure": selection["ties"],
            "decile_bucket": bucket,
            "in_sample_selection_table": selection["selection_table"],
            "in_sample_note":
                "in-sample scores are motivation, not evidence (§5.1); "
                "nothing downstream cites them as support",
        },
        "gate1": gate1,
        "gate1_total_draws_compared": gate1_total,
        "fires": fires,
        "tests": tests,
        "pooled": pooled,
        "strata": strata_tables,
        "bucket_tests": bucket_tests,
        "persistence": persistence,
        "unstratified_auc_descriptive": unstrat_auc,
        "scoring_arm": scoring_arm,
        "mean_draw_len_new": {s: new_cells[s]["mean_draw_len"]
                              for s in SIZES_3D},
        "per_seed_pooled_view": per_seed_view,
        "blind_region": blind,
        "twin_record": {
            **base["twin"],
            "statement": (
                f"no new twin was sampled (§4): exp3's committed twin "
                f"record — 0 fires across all 8 untrained cells, "
                f"{base['twin']['reversal_twin_draws']:,} reversal-twin "
                f"draws + {base['twin']['control_twin_draws']:,} "
                f"control-twin draws — is the standing contamination "
                f"referent, re-asserted from raw draws at this load"),
        },
        "leak_voids": all_void,
        "luck_floor_by_length": {str(L): c.luck_floor(L)
                                 for L in (4, 5, 6)},
        "alpha": rt.ALPHA_3D,
    }

    # 1. stream continuity: zero tolerance, diffs already disclosed
    if gate1_diff_cells:
        detail = "; ".join(f"{k} ({n} differing draws)"
                           for k, n in sorted(gate1_diff_cells.items()))
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": (
                    f"gate 1 failed — the seed-{GATE1_SEED_3D} "
                    f"re-derivation differs from 3c's committed bytes "
                    f"at: {detail}. The streams are deterministic on "
                    f"this stack (three consecutive byte-identical "
                    f"reproductions through 3c); a single differing "
                    f"byte means the generation law changed, and no "
                    f"new draw is interpretable. Differing draws "
                    f"disclosed verbatim in the gate1 table.")}

    # 2. contamination/leak: every observed fire void
    if all_new_fires > 0 and len(all_void) == all_new_fires:
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": (
                    f"every one of the {all_new_fires} new fired draws "
                    f"is void — each fire's answer occurs in its own "
                    f"prompt (evidence in leak_voids, verbatim). The "
                    f"leak class the items rule out by construction is "
                    f"live, so no fire ranks anything and no silence "
                    f"bounds anything.")}

    # 3. adjudicate (§6): the 1b primary alone, mechanical order
    adj = tests[ADJUDICATING_SIZE]
    rep = tests[REPLICATION_SIZE]
    n_f = adj["n_fired"]
    thin = bool(n_f <= rt.THIN_MAX)
    thin_txt = " THIN" if thin else ""
    rep_rejects = rep["p_low"] is not None and \
        rep["p_low"] <= rt.ALPHA_3D
    rep_txt = ("replicated at 410m" if rep_rejects else
               "unreplicated at 410m's disclosed power")
    f_txt = (f"|F| = {n_f} new-fired item(s) "
             f"{tests[ADJUDICATING_SIZE]['composition']}, "
             f"T = {adj['T']}, path {adj['path']}")
    out = {**out, "adjudication": {
        "n_fired": n_f, "thin": thin, "m_min": m_min,
        "p_low": adj["p_low"], "p_high": adj["p_high"],
        "replication_410m": {"n_fired": rep["n_fired"],
                             "p_low": rep["p_low"],
                             "rejects": bool(rep_rejects)}}}

    if adj["p_low"] is not None and adj["p_low"] <= rt.ALPHA_3D:
        return {**out, "verdict": f"STRUCTURED{thin_txt}",
                "reason": (
                    f"the frozen functional forecast the new fires: "
                    f"{f_txt}, one-sided p = {adj['p_low']:.6g} ≤ "
                    f"{rt.ALPHA_3D} in the predicted direction — the "
                    f"sampled channel's item-grain reach is "
                    f"forecastable from answer structure alone, before "
                    f"drawing ({rep_txt}; the annotation modifies "
                    f"nothing). Every fire disclosed verbatim with its "
                    f"(item, seed, draw) address."
                    + (" THIN (§6): |F| ≤ 4 — a small fired set can "
                       "formally reject, and this label prevents a "
                       "fragile rejection from reading as more than "
                       "it is." if thin else ""))}
    if adj["p_high"] is not None and adj["p_high"] <= rt.ALPHA_3D:
        return {**out, "verdict": f"ANTI-STRUCTURED{thin_txt}",
                "reason": (
                    f"the reverse-direction test rejects: {f_txt}, "
                    f"upper-tail p = {adj['p_high']:.6g} ≤ "
                    f"{rt.ALPHA_3D} — compressible answers fire LESS. "
                    f"This falsifies the joint-cost reading of 3c's "
                    f"fires, not merely fails to support it, and is "
                    f"reported with the same prominence (§6)."
                    + (" THIN (§6): |F| ≤ 4." if thin else ""))}
    if n_f >= m_min:
        return {**out, "verdict": f"UNSTRUCTURED{thin_txt}",
                "reason": (
                    f"no rejection in either direction: {f_txt}, "
                    f"p_low = {adj['p_low']:.6g}, p_high = "
                    f"{adj['p_high']:.6g}, |F| = {n_f} ≥ m_min = "
                    f"{m_min} — the fired set was large enough to "
                    f"reject and did not. The functional does not "
                    f"forecast at this resolution; the heterogeneity "
                    f"texture stands as unexplained-by-this-functional "
                    f"(§6). Rates and CP bounds ship regardless."
                    + (" THIN (§6): |F| ≤ 4." if thin else ""))}
    return {**out, "verdict": f"UNINFORMATIVE{thin_txt}",
            "reason": (
                f"|F| = {n_f} < m_min = {m_min}: no arrangement of so "
                f"few fires can reject at α = {rt.ALPHA_3D}, so the "
                f"tranche cannot adjudicate the rank hypothesis. "
                f"Retracts NOTHING (§6): 3c's DEEPENS, the committed "
                f"rates, and the heterogeneity texture all stand; the "
                f"tranche's fires and silences ship as counts and CP "
                f"bounds regardless (pooled "
                f"{pooled[ADJUDICATING_SIZE]['count']}/"
                f"{pooled[ADJUDICATING_SIZE]['n_draws']} at 1b)."
                + (" THIN (§6): |F| ≤ 4." if thin else ""))}


# ----------------------------------------------------------------- driver

def run(root=EXP3D) -> dict:
    """Load all three trees through the frozen producers, re-assert
    every standing referent, and adjudicate. No model is loaded;
    nothing is sampled; every input is a committed record or a frozen
    loader's output (§2)."""
    check_frozen_imports_3d()
    check_stream_map_3d()
    c.check_stream_map()
    verify_fn = c.load_verify_3c()
    exp3_cells = a3.load_sampling_cells(EXP3, verify_fn=verify_fn)
    exp3_addresses = c.extract_fire_addresses(EXP3, exp3_cells,
                                              verify_fn=verify_fn)
    c3_cells = c.load_new_cells(EXP3C, verify_fn=verify_fn)
    gate2 = a3.load_gate2_referents()
    sha_refs = a3.items_sha_referents(gate2)
    for rung in SCORING_RUNGS:
        if sha_refs.get(rung) != ITEMS_SHA_PIN[rung]:
            raise ValueError(
                f"3b-derived items sha for {rung} "
                f"({sha_refs.get(rung)}) disagrees with the §4 literal "
                f"pin ({ITEMS_SHA_PIN[rung]}) — two committed sources, "
                f"one value, and they differ")
    c3_verdict = json.loads(
        (EXP3C / "results" / "verdict.json").read_text())
    items = load_item_file(RUNG)
    selection = load_selection(items["answers"])
    power_pin = load_power_pin(selection)
    new_cells = load_new_cells_3d(root, verify_fn=verify_fn)
    for size in SIZES_3D:
        if new_cells[size]["answers"] != items["answers"]:
            raise ValueError(
                f"{size}: tranche answers disagree with the committed "
                f"item file — not the preregistered battery")
        if new_cells[size]["items_sha256"] != ITEMS_SHA_PIN[RUNG]:
            raise ValueError(
                f"{size}: tranche items_sha256 "
                f"{new_cells[size]['items_sha256']} against the §4 pin")
    base = build_committed_base(exp3_cells, c3_cells, exp3_addresses,
                                c3_referent_fires=c3_verdict["fires"])
    gate1_records = load_gate1_3d(root)
    check_gate1_committed_shas_3d(gate1_records)
    scoring = load_scoring_3d(root)
    prompts = c.load_prompts(sha_refs, rungs=(RUNG,))
    return verdict_3d(new_cells, gate1_records, scoring, base,
                      selection, power_pin, prompts)


if __name__ == "__main__":
    v = run()
    print(json.dumps({k: v[k] for k in
                      ("verdict", "reason", "adjudication",
                       "gate1_total_draws_compared")
                      if k in v}, indent=1))
