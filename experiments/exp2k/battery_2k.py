# experiments/exp2k/battery_2k.py
"""Experiment 2k — constants, paths, readers, the tier-record literal
and its checker, seed freshness and the 256-scaled matched-k rule
(design §2, §3.1–3.4, §4). Zero model contact: every input is a
committed file or a hand-built row set.

Seed 0 of every 2k cell IS 2d's committed main-tier stream (same rung,
size, mode, exp3's `stream_seed` formula and namespace) — regenerated
on the production path, never copied, and compared draw by draw as
gate 1 (design §3.2). Seeds 1–3 are fresh on every R_CAP cell at both
sizes; `check_seed_freshness` proves it against every committed
stream map before a model loads."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

EXP2K = Path(__file__).resolve().parent
EXPERIMENTS = EXP2K.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402

RESULTS = EXP2K / "results"
TIER = "k256"
MODE = a2d.MODE                                  # "trained"
SIZES_2K = ("1b", "410m")                        # dial c / g: 1b first, 410m second
SEEDS_2K = (0, 1, 2, 3)                          # dial a / b
DRAWS_PER_SEED = 64
K_TOTAL = DRAWS_PER_SEED * len(SEEDS_2K)         # 256
LADDER_K = (64, 128, 192, 256)
N_ITEMS = bt.N_ITEMS
GATE1_SEED = 0
PREREG_TAG_2K = "exp2k-preregistered"
SEAL_TAG_2K = "exp2k-predictor-sealed"
INSTRUMENT_BLOBS_2K = ("experiments/exp2k/analyze_2k.py",
                       "experiments/exp2k/battery_2k.py",
                       "experiments/exp2k/run/tier_2k.py")
# design §3.4: 2i's committed R_CAP; the analyzer READS 2i's record and
# refuses if it differs from this literal.
R_CAP_DESIGN = ("add3_mid", "add_base8", "antonym", "antonym6", "arith_next",
                "odd6", "sub3_mid", "sub4_mid", "sub_base8")
# design §2: k_g = clip(round(256 · r̄_A / r̄_B), 1, 64) on the committed rates
MATCHED_K_DESIGN = {"add_base8": 28, "arith_next": 37, "sub_base8": 45, "add3_mid": 27,
                    "antonym": 64, "antonym6": 64, "odd6": 64, "sub3_mid": 64, "sub4_mid": 64}
STREAM_MAPS = (EXPERIMENTS / "exp3" / "stream_map.json",
               EXPERIMENTS / "exp2d" / "stream_map_2d.json",
               EXPERIMENTS / "exp3c" / "stream_map_3c.json",
               EXPERIMENTS / "exp3d" / "stream_map_3d.json",
               EXPERIMENTS / "exp3e" / "stream_map_3e.json")


# ---------------------------------------------------------------- paths

def tier_dir(root, size) -> Path:
    return Path(root) / "results" / TIER / f"{size}_{MODE}"


def tier_record_path(root, size, rung) -> Path:
    return tier_dir(root, size) / f"{rung}.json"


def tier_draws_path(root, size, rung) -> Path:
    return tier_dir(root, size) / f"{rung}.draws.jsonl.gz"


def halt_marker_path(root, size, rung) -> Path:
    return tier_dir(root, size) / f"{rung}.HALTED"


def halted_draws_path(root, size, rung) -> Path:
    return tier_dir(root, size) / f"{rung}.HALTED.jsonl.gz"


def halt_markers(root) -> list:
    """Every `*.HALTED` marker under the tier tree, ANY size, ANY rung —
    scanned before any tier loads (2d F-1's lesson)."""
    base = Path(root) / "results" / TIER
    return sorted(base.glob("*/*.HALTED")) if base.is_dir() else []


def seal_path(root) -> Path:
    return Path(root) / "results" / "predictor_2k.json"


def power_path(root) -> Path:
    return Path(root) / "results" / "power_2k.json"


def committed_draws_path(size, rung) -> Path:
    return a2d.tier_draws_path(a2d.EXP2D, "main", size, rung)


def committed_record_path(size, rung) -> Path:
    return a2d.tier_record_path(a2d.EXP2D, "main", size, rung)


def pythia_sha(size) -> str:
    """2b's pinned weight revision for a probe size — the `model_sha` 2d
    wrote and the one every 2k record must carry (same weights)."""
    if size not in bt.PROBE_SIZES:
        raise ValueError(f"{size!r} is not a 2d probe size {bt.PROBE_SIZES}")
    for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):   # 2d's order, load-bearing
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
    bt.harness_2c()                 # provenance-asserted
    from models import PYTHIA_SHAS  # 2b's
    return PYTHIA_SHAS[size]


# -------------------------------------------------------------- readers

def read_rows_2k(path, *, seeds=SEEDS_2K, dps=DRAWS_PER_SEED, n_items=N_ITEMS) -> list:
    """2d's row format with FOUR seed streams per item; coverage pinned:
    exactly items 0..n_items−1, each with exactly `seeds` at exactly
    `dps` string draws each. Sorted by item."""
    want = {str(s) for s in seeds}
    rows, seen = [], set()
    with gzip.open(Path(path), "rt") as f:
        for line in f:
            row = json.loads(line)
            i = row.get("item")
            if not isinstance(i, int) or i in seen or not 0 <= i < n_items:
                raise ValueError(f"{path}: bad or duplicate item {i!r}")
            seen.add(i)
            draws = row.get("draws")
            if not isinstance(draws, dict) or set(draws) != want:
                raise ValueError(f"{path} item {i}: seed streams "
                                 f"{sorted(draws) if isinstance(draws, dict) else draws!r}"
                                 f" are not the tier's seeds {sorted(want)}")
            for s, stream in draws.items():
                if not isinstance(stream, list) or len(stream) != dps or \
                        not all(isinstance(x, str) for x in stream):
                    raise ValueError(f"{path} item {i} seed {s}: stream of "
                                     f"{len(stream) if isinstance(stream, list) else stream!r}"
                                     f" draws against draws_per_seed {dps}")
            rows.append(row)
    if len(seen) != n_items:
        raise ValueError(f"{path}: {len(seen)} items against {n_items} — coverage incomplete")
    rows.sort(key=lambda r: r["item"])
    return rows


def committed_rows(size, rung) -> list:
    """2d's committed main-tier seed-0 rows for the cell (the gate-1
    referent), through 2d's own coverage-pinned reader."""
    spec = a2d.TIERS["main"]
    return a2d.read_rows(committed_draws_path(size, rung), seed=spec["seed"],
                         dps=spec["draws_per_seed"], n_items=N_ITEMS)


def committed_by_item(rows) -> dict:
    return {int(r["item"]): list(r["draws"][str(GATE1_SEED)]) for r in rows}


def diff_seed0(rows_2k, committed) -> list:
    """Every differing seed-0 draw between the 2k rows and 2d's committed
    rows, with addresses — exp3d's `diff_seed` (coverage on both sides
    a hard error, never a shorter comparison)."""
    from experiments.exp3d.rederive_3d import diff_seed
    regenerated = {int(r["item"]): list(r["draws"][str(GATE1_SEED)]) for r in rows_2k}
    return diff_seed(committed, regenerated, dps=DRAWS_PER_SEED, seed=GATE1_SEED)


# --------------------------------------------------------- bits / counts

def bits_2k(rows, cap, verify_fn) -> list:
    """N_ITEMS × K_TOTAL verified bits in SEED ORDER (seed 0's 64 draws,
    then 1, 2, 3) — the order every `counts_at_k` prefix reads."""
    n = len(cap["eval_items"])
    bits = [None] * n
    at = cap["answer_type"]
    for row in rows:
        ans = cap["eval_items"][row["item"]]["answer"]
        b = []
        for s in SEEDS_2K:
            b.extend(int(bool(verify_fn(d, ans, at))) for d in row["draws"][str(s)])
        bits[row["item"]] = b
    if any(b is None for b in bits):
        raise ValueError("bits_2k: coverage incomplete")
    return bits


def counts_at_k(bits, k) -> list:
    if k not in LADDER_K:
        raise ValueError(f"k = {k} is not on the ladder {LADDER_K}")
    return [int(sum(b[:k])) for b in bits]


def block_counts(bits, b) -> list:
    return [int(sum(row[b * DRAWS_PER_SEED:(b + 1) * DRAWS_PER_SEED])) for row in bits]


def counts_by_k(bits) -> dict:
    return {k: counts_at_k(bits, k) for k in LADDER_K}


def tallies_2k(rows, cap, verify_fn) -> dict:
    at = cap["answer_type"]
    out = {}
    for s in SEEDS_2K:
        v = n = 0
        for row in rows:
            ans = cap["eval_items"][row["item"]]["answer"]
            for d in row["draws"][str(s)]:
                n += 1
                v += int(bool(verify_fn(d, ans, at)))
        out[str(s)] = {"full_string": int(v), "n_draws": int(n)}
    return out


def mean_rate(counts, dps) -> float:
    return float(sum(counts)) / (len(counts) * dps)


# ------------------------------------------------------------- records

# Every field the checker below re-derives from the pins, by name.
TIER_RECORD_PINS_2K = ("rung", "size", "mode", "tier", "n_items", "answer_type", "n_shots",
                       "dtype", "untrained_seed", "seeds", "draws_per_seed", "k_total",
                       "max_new_tokens", "temperature", "truncation", "items_sha256",
                       "stream_namespace", "model_sha")


def tier_record_2k(*, rung, size, cap, rows, verify_fn, model_sha, stack, git_sha, seconds,
                   committed_gz_sha, committed_record_sha, gate1_items_compared,
                   gate1_draws_compared) -> dict:
    """THE record literal (2d's `run_sampling_rung` record with four
    seeds, a `k_total` of 256 and a `gate1` block). The runner writes
    it; the worlds write it through this same function (2i F-1: a
    world must carry the real shape, not a stub)."""
    return {"rung": rung, "size": size, "mode": MODE, "tier": TIER, "n_items": len(rows),
            "answers": [str(it["answer"]) for it in cap["eval_items"]],
            "answer_type": cap["answer_type"], "n_shots": bt.N_SHOTS,
            "dtype": a2d.SAMPLING_DTYPE, "untrained_seed": None, "model_sha": model_sha,
            "items_sha256": cap["items_sha256"], "stream_namespace": a2d.STREAM_NAMESPACE,
            "seeds": list(SEEDS_2K), "draws_per_seed": DRAWS_PER_SEED, "k_total": K_TOTAL,
            "max_new_tokens": bt.max_new_tokens(rung), "temperature": 1.0,
            "truncation": "none", "per_seed_tallies": tallies_2k(rows, cap, verify_fn),
            "gate1": {"seed": GATE1_SEED, "on_production_path": True,
                      "items_compared": int(gate1_items_compared),
                      "draws_compared": int(gate1_draws_compared), "n_diffs": 0,
                      "committed_draws_sha256": committed_gz_sha,
                      "committed_record_sha256": committed_record_sha},
            "draws_file": tier_draws_path(EXP2K, size, rung).name, "stack": stack,
            "git_sha": git_sha, "seconds": round(float(seconds), 1)}


def tier_record_failures_2k(rec, *, size, rung, cap, committed_sha=None) -> list:
    """`results/k256/<size>_trained/<rung>.json` against everything already
    pinned (2i's `predictor_record_failures_2i` pattern). Returns failure
    strings; never raises for a well-typed dict. `committed_sha` (the
    analyzer passes 2i's `PYTHIA_PREDICTOR_FILES` literal) is the sha the
    gate-1 block must attest for its committed referent."""
    label = f"tier k256/{size}/{rung}"
    bad = []
    want = {"rung": rung, "size": size, "mode": MODE, "tier": TIER, "n_items": N_ITEMS,
            "answer_type": cap["answer_type"], "n_shots": bt.N_SHOTS,
            "dtype": a2d.SAMPLING_DTYPE, "untrained_seed": None, "seeds": list(SEEDS_2K),
            "draws_per_seed": DRAWS_PER_SEED, "k_total": K_TOTAL,
            "max_new_tokens": bt.max_new_tokens(rung), "temperature": 1.0,
            "truncation": "none", "items_sha256": cap["items_sha256"],
            "stream_namespace": a2d.STREAM_NAMESPACE,
            "model_sha": pythia_sha(size) if size in bt.PROBE_SIZES else None}
    for k in TIER_RECORD_PINS_2K:
        if rec.get(k) != want[k]:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {want[k]!r}")
    answers = rec.get("answers")
    want_answers = [str(it["answer"]) for it in cap["eval_items"]]
    if not isinstance(answers, list) or len(answers) != len(want_answers):
        bad.append(f"{label}: answers column is not {len(want_answers)} long")
    else:
        n = sum(1 for a, b in zip(answers, want_answers) if a != b)
        if n:
            bad.append(f"{label}: the record's answer column differs from the pinned item "
                       f"file on {n} item(s)")
    tallies = rec.get("per_seed_tallies")
    if not isinstance(tallies, dict) or set(tallies) != {str(s) for s in SEEDS_2K}:
        bad.append(f"{label}: per_seed_tallies does not carry exactly seeds {list(SEEDS_2K)}")
    else:
        for s, t in tallies.items():
            if not isinstance(t, dict) or t.get("n_draws") != N_ITEMS * DRAWS_PER_SEED:
                bad.append(f"{label}: per_seed_tallies[{s}] tallies "
                           f"{t.get('n_draws') if isinstance(t, dict) else t!r} draws, not "
                           f"the full {N_ITEMS * DRAWS_PER_SEED}")
    g = rec.get("gate1")
    if not isinstance(g, dict):
        bad.append(f"{label}: gate1 block missing")
    else:
        if g.get("seed") != GATE1_SEED or g.get("on_production_path") is not True:
            bad.append(f"{label}: gate1 seed/on_production_path {g.get('seed')!r}/"
                       f"{g.get('on_production_path')!r}")
        if g.get("items_compared") != N_ITEMS:
            bad.append(f"{label}: gate1 items_compared = {g.get('items_compared')!r}, not "
                       f"{N_ITEMS} — coverage, not a rate")
        if g.get("draws_compared") != N_ITEMS * DRAWS_PER_SEED:
            bad.append(f"{label}: gate1 draws_compared = {g.get('draws_compared')!r}")
        if g.get("n_diffs") != 0:
            bad.append(f"{label}: gate1 n_diffs = {g.get('n_diffs')!r} (the runner should "
                       f"have halted)")
        if committed_sha is not None and g.get("committed_draws_sha256") != committed_sha:
            bad.append(f"{label}: gate1 committed_draws_sha256 {g.get('committed_draws_sha256')!r}"
                       f" is not 2i's pinned {committed_sha!r} for the cell")
        for k in ("committed_draws_sha256", "committed_record_sha256"):
            if not isinstance(g.get(k), str) or len(g.get(k)) != 64:
                bad.append(f"{label}: gate1 {k} is not a sha256")
    if rec.get("draws_file") != tier_draws_path(EXP2K, size, rung).name:
        bad.append(f"{label}: draws_file = {rec.get('draws_file')!r}")
    return bad


# ------------------------------------------------------------ freshness

def _cells_of(map_path: Path) -> set:
    """Every `(rung, size, mode, seed)` a committed stream map covers.
    All five committed maps (exp3, exp2d, exp3c, exp3d, exp3e) carry a
    top-level `cells` dict keyed `rung/size/mode/s<seed>` (verified
    against the real files: exp2d's map ALSO carries a `tiers` block,
    but `cells` is present there too, so the cells branch always fires
    on this data — the `tiers` branch below is retained for a future
    map that might lack `cells`, and is unreachable on the committed
    five, disclosed in PROGRESS.md). Any other shape is a hard error —
    the freshness proof must not silently skip a map it cannot parse."""
    m = json.loads(map_path.read_text())
    out = set()
    if "cells" in m and isinstance(m["cells"], dict):
        for key in m["cells"]:
            parts = key.split("/")
            if len(parts) != 4 or not parts[3].startswith("s"):
                raise ValueError(f"{map_path}: unrecognized cell key {key!r}")
            out.add((parts[0], parts[1], parts[2], int(parts[3][1:])))
    elif "tiers" in m and isinstance(m["tiers"], dict):
        for tier in m["tiers"].values():
            for rung in bt.RUNGS:
                for size in bt.PROBE_SIZES:
                    out.add((rung, size, MODE, int(tier["seed"])))
    else:
        raise ValueError(f"{map_path}: neither a cells map nor a tiers map")
    return out


def stream_collisions(rung, size, seeds, *, mode=MODE) -> list:
    hits = []
    for mp in STREAM_MAPS:
        cells = _cells_of(mp)
        for s in seeds:
            if (rung, size, mode, int(s)) in cells:
                hits.append(f"{mp.name}:{rung}/{size}/{mode}/s{s}")
    return hits


def check_seed_freshness(rungs, sizes=SIZES_2K) -> dict:
    """Seeds 1–3 collide with NO committed stream on any (rung, size);
    seed 0 collides with 2d's main tier on EVERY (rung, size) — it must,
    it is the gate-1 referent. Raises otherwise."""
    new = [s for s in SEEDS_2K if s != GATE1_SEED]
    bad = []
    n = 0
    for rung in rungs:
        for size in sizes:
            n += 1
            hits = stream_collisions(rung, size, new)
            if hits:
                bad.append(f"seeds {new} collide with committed streams: {hits}")
            if not any("stream_map_2d" in h for h in stream_collisions(rung, size, (GATE1_SEED,))):
                bad.append(f"seed {GATE1_SEED} on {rung}/{size} is not 2d's main tier")
    if bad:
        raise ValueError("seed freshness: " + "; ".join(bad))
    return {"new_seeds": new, "gate1_seed": GATE1_SEED, "cells": n,
            "maps": [p.name for p in STREAM_MAPS]}


# ---------------------------------------------------------- matched k

def matched_k_256(rate_a64, rate_b64) -> dict:
    """design §2 / §5.2 S3: x_A at 256 draws expects 256·r̄_A verified
    draws per item; x_B's 64-draw count matches it at
    k = clip(round(256 · r̄_A / r̄_B), 1, 64), round = floor(x + 0.5)
    (2j's convention). Capped at 64 when x_A at 256 is at least as dense
    as x_B at 64 (then the B side is not thinned; disclosed)."""
    import numpy as np
    if rate_b64 <= 0 or 256.0 * rate_a64 >= 64.0 * rate_b64:
        return {"k": DRAWS_PER_SEED, "capped": True, "n_blocks": 1}
    k = int(np.floor(K_TOTAL * rate_a64 / rate_b64 + 0.5))
    k = min(DRAWS_PER_SEED, max(1, k))
    return {"k": k, "capped": k == DRAWS_PER_SEED, "n_blocks": DRAWS_PER_SEED // k}


# ------------------------------------------------------------ pins

from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2j import analyze_2j as an2j  # noqa: E402

# Every frozen module 2k executes on the verdict path or in a stage
# tool: 2j's 26 (which carry 2i's 22, 2i's own two, 2j's power/referent
# tools) + 2j's two tag-bound instrument blobs (2j is closed; its blobs
# are frozen bytes to 2k) + the sampler-side modules the tier runner
# and the gate-1 re-derivation use + 2k's own artifact writers. The
# three 2k blobs the prereg TAG binds (analyze/battery/tier) are NOT
# here — a sha literal on them would kill every mutation-battery mutant
# trivially (2j's rule).
FROZEN_FILES_2K = tuple(an2j.FROZEN_SHA256_2J) + (
    EXPERIMENTS / "exp2j" / "analyze_2j.py",
    EXPERIMENTS / "exp2j" / "functionals_2j.py",
    EXPERIMENTS / "exp3d" / "rederive_3d.py",
    EXPERIMENTS / "exp3" / "run" / "run_cell.py",
    EXPERIMENTS / "exp2i" / "run" / "sample_2i.py",
    EXPERIMENTS / "exp2b" / "models.py",
    EXP2K / "power_2k.py",
    EXP2K / "make_referents_2k.py",
    EXP2K / "run" / "seal_2k.py",
    EXP2K / "run" / "campaign_2k.py",
)
FROZEN_SHA256_2K = {   # Task 5: pinned as a literal from frozen_from_disk() (36 modules)
    REPO / "experiments/exp2h/battery_2h.py":
        "2d721cf85bbd85937f45a1135e8b5e102685ab424d8ab0dfada527bd8ab4e80a",
    REPO / "experiments/exp2h/analyze_2h.py":
        "52733e8d4280fb41b76cda2dcac024299ce7dd61090f856ba3147c8098b871bf",
    REPO / "experiments/exp2g/battery_2g.py":
        "aca79dd71ee7dead3c0ce065945bb38eaf1b0b72b5d5f40698dabb0f5a9cf3c1",
    REPO / "experiments/exp2g/stats_2g.py":
        "cf3c4c89c86fa43c5ba49d5c4be12eabad28ac65d9d12a43b1e31ef6e4bc195f",
    REPO / "experiments/exp2g/strata_2g.py":
        "ea0acbbdfde13655a6b89d3afcc981f348ee6312b4448b70d437f1e4d3f7f594",
    REPO / "experiments/exp2g/labels_2g.py":
        "d86e7cdb4dcc10257986e8a85824365972a75ba993be5a8fde8a825d68e3077d",
    REPO / "experiments/exp2g/analyze_2g.py":
        "eab7c5b91d57351ee2a7adb0e85d71cb92cb4d6ed15d0bb90150c95c2076050e",
    REPO / "experiments/exp2g/checkpoints_2g.py":
        "155fee3ec3933db33930d7ddadb99c02604d893205a8f8c037016cc18609fb10",
    REPO / "experiments/exp2d/battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
    REPO / "experiments/exp2d/analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    REPO / "experiments/exp2d/stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    REPO / "experiments/exp2d/results/verdict.json":
        "d5b1b28bf70f4be1a5acf73df8ad03d8c57349ce4acf15e26f690c6dc1347b61",
    REPO / "experiments/exp2c/harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    REPO / "experiments/exp2c/battery/family_map.py":
        "46477b37683c8ea0e1f2f219dce96858a0dcf91710b15cae45a8cf4c4c7ab375",
    REPO / "experiments/exp3/sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
    REPO / "experiments/exp3c/analyze_3c.py":
        "66b78ffbedb808625ed33019f29d2ef8ec9d0f31a1115eb7cb08ad3e67d42d84",
    REPO / "experiments/exp2g/predictor_2g.py":
        "3381b43a34fd1fb1f7ef57eb9d02a6a9e9ec41b3ffcadea425c37b86c1e92a4e",
    REPO / "experiments/exp2g/run/sweep_2g.py":
        "850db5831adeffc46a888ca185ef3f1ad819a8db104c9eafd1df69c470c91a87",
    REPO / "experiments/exp2i/run/_common_2i.py":
        "5cc7c97f68b45656d6dbbb5fbf6d7d895d7b1d96e104df543f8c9f1691e5ad4f",
    REPO / "experiments/exp2i/make_referents_2i.py":
        "6de0278cfe85d9efefa11d0b2549afa78dd8836e1ef2b947d00c8709acc3977b",
    REPO / "experiments/exp2i/power_2i.py":
        "0e5e449ac420e40243ae86eb84e576256e857581ad3c7e000fcea5e08666119d",
    REPO / "experiments/exp2i/run/seal_2i.py":
        "f20132aed4c0b7e995745972abeddec4ba1d7a269147b5d034bff06a3157f078",
    REPO / "experiments/exp2i/analyze_2i.py":
        "85e482fea17e0706476243a0a98a7d2c32efebd6536c5255ae48e729b494c252",
    REPO / "experiments/exp2i/battery_2i.py":
        "e0a8d10cb4dde8a3af1a3e9b32447c407b43201513dc758d6cd9a8c38b5cdfcf",
    REPO / "experiments/exp2j/power_2j.py":
        "19b80593d091663183b7394b101ee5f97c832b5f0dd7dc4227c9b1107721ab1a",
    REPO / "experiments/exp2j/make_referents_2j.py":
        "ac4064ccc0e2a210c6eee720578f2b4c31846cf00d76668070adac5e9ebe1678",
    REPO / "experiments/exp2j/analyze_2j.py":
        "976f1ff1f91affa2fc66d635e6b6d9a8aabfd21bdc7ccc38abfe87482ea09b13",
    REPO / "experiments/exp2j/functionals_2j.py":
        "39375f01de4b5bf06787175e25f7f85394844c005c3c4ea66f69954b1fe8bfce",
    REPO / "experiments/exp3d/rederive_3d.py":
        "8421433ffe328e7e2ad8d2877150f9bfc0279c9337576fd5860e917dc8690870",
    REPO / "experiments/exp3/run/run_cell.py":
        "5c018457d9eb999079b4b0426dc0ecadf10baed6339d32b5eb914f280da35b46",
    REPO / "experiments/exp2i/run/sample_2i.py":
        "6cf3cdfac2f940f12c0365694758578a3655afbf74498f7c7c549ac221b55fe4",
    REPO / "experiments/exp2b/models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
    REPO / "experiments/exp2k/power_2k.py":
        "318ec4266513200e6a018285184cdae5c1fe5cc78400fe07671a9f45bc92ed4e",
    REPO / "experiments/exp2k/make_referents_2k.py":
        "a4d6b6a2d821880eb11a01f2f47137c58d7b8e6b7676b079d11aa4b3c5d71aca",
    REPO / "experiments/exp2k/run/seal_2k.py":
        "0cbdd982a55075e8c8567acb82d7264ce87c88320d2fa4568a5b419f7ca4b2fb",
    REPO / "experiments/exp2k/run/campaign_2k.py":
        "75f2b4c4f66d3d683d875e2a569bc2ec2b7c72fafa3ca1071c103d54df1337e5",
}


def frozen_from_disk(*, strict: bool = True) -> dict:
    """The dict Task 5 prints and pins. Strict (the default, and the
    only mode Task 5 uses): a missing or mistyped path in
    `FROZEN_FILES_2K` must not be silently omitted from the pinned
    literal, so this raises `FileNotFoundError` naming the path —
    `bg.sha256_file`'s own `open()` failure is left to surface
    unfiltered. `strict=False` filters to files that exist; used ONLY
    by the pre-Task-5 tests, before `power_2k.py`, `make_referents_2k
    .py` and `run/seal_2k.py` are on disk (monkeypatching
    `FROZEN_SHA256_2K` with a partial dict to exercise `check_frozen_2k`
    itself, which never filters)."""
    if strict:
        return {p: bg.sha256_file(p) for p in FROZEN_FILES_2K}
    return {p: bg.sha256_file(p) for p in FROZEN_FILES_2K if p.is_file()}


def check_frozen_2k() -> None:
    if not FROZEN_SHA256_2K:
        raise RuntimeError("FROZEN_SHA256_2K is empty — not pinned (build incomplete)")
    for p, want in FROZEN_SHA256_2K.items():
        got = bg.sha256_file(p)
        if got != want:
            raise RuntimeError(f"frozen module drifted: {p} ({got[:12]} != {want[:12]})")


def require_prereg_2k(*, tag_exists=None, blob_sha=None) -> dict:
    """2j's blob binding: the tag must exist and each instrument blob's
    bytes on disk must equal the blob the tag carries."""
    from experiments.exp2g import predictor_2g as pr
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_2K):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_2K} does not exist")
    bound = {}
    for rel in INSTRUMENT_BLOBS_2K:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_2K, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_2K} does not bind {rel}: "
                               f"tag {str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_2K, "instrument_blobs": bound}
