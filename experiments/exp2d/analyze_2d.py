"""Exp 2d frozen analysis (design §5–§6): the sampling ladder.

Every input is a committed value or a frozen loader's output; every
referent is re-asserted from bytes at analysis time; no model is
loaded here and nothing is sampled. The verdict tree (§6) is
mechanical: INSUFFICIENT_DATA (gate 1 only) → FAIL → PASS →
INDETERMINATE. The known-outcome caveat of §2 is carried in the
record wherever a result is read.

What this module imports, never copies: 2c's harness (render,
normalize, MAX_NEW_TOKENS), family map, exact block-permutation
machinery and m5 ascent rule (the known-answer gate for the outcome
loader); exp3's sampler contract (stream map) and runner helpers;
3c's total verify wrapper; 3d's gate-1 comparator. Every such file is
sha-pinned (`FROZEN_IMPORT_SHA256_2D`) and checked before any byte of
any tree is parsed.

Record layout (the runner's, `run/run_cell_2d.py`):
  results/pilot/<size>_trained/<rung>.json + .draws.jsonl.gz   k=8, seed 1000
  results/main/<size>_trained/<rung>.json  + .draws.jsonl.gz   k=64, seed 0
  results/gate1/<size>_trained/<rung>.json    (the 2 reversal rungs)
  results/argmax/<size>_trained/<rung>.json   greedy fp16, descriptive
  power_2d.json                                the frozen §7 procedure, run ONCE
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

EXP2D = Path(__file__).resolve().parent
EXPERIMENTS = EXP2D.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402

EXP2B, EXP2C = bt.EXP2B, bt.EXP2C
EXP3 = EXPERIMENTS / "exp3"
EXP3C = EXPERIMENTS / "exp3c"
EXP3D = EXPERIMENTS / "exp3d"
RESULTS = EXP2D / "results"
POWER_PATH = EXP2D / "power_2d.json"
STREAM_MAP_2D_PATH = EXP2D / "stream_map_2d.json"
REFERENTS_PATH = EXP2D / "referents_2d.json"

RUNGS = bt.RUNGS
FAMILY_OF = bt.FAMILY_OF
FAMILY_SIZES = bt.FAMILY_SIZES
PROBE_SIZES = bt.PROBE_SIZES
EVAL_SIZES = bt.EVAL_SIZES
N_ITEMS = bt.N_ITEMS
MODE = "trained"
REPLICATION_SIZE = "1b"          # §5.1: the 1b column alone, named
OTHER_SIZE = "410m"              # §5.4: the 410m replication

# §3: the matrix
TIERS = {
    "pilot": {"seed": 1000, "draws_per_seed": 8},   # ruling L (2026-08-21):
    # outside every committed range (exp3 0–3, 3c 4–15, 3d 16–39, 3e 28–167)
    "main": {"seed": 0, "draws_per_seed": 64},
}
SAMPLING_DTYPE = "float32"       # exp3's probe-size policy (exact upcast)
ARGMAX_DTYPE = "float16"         # 2c's m4 path / 3b's redecode
STREAM_NAMESPACE = "exp3"        # the sampler's — gate 1 depends on it
REVERSAL_RUNGS = ("rev_string7", "reverse_string")
PAIR_5_4 = ("sub3_mid", "arith_next")   # §5.4: probe-flat but rising
GATE1_SEED = 0
GATE1_COVERAGE = N_ITEMS * TIERS["main"]["draws_per_seed"]   # 32,000 / cell
MAIN_DRAWS_PER_RUNG = GATE1_COVERAGE
PILOT_DRAWS_PER_RUNG = N_ITEMS * TIERS["pilot"]["draws_per_seed"]  # 4,000

KNOWN_OUTCOME_CAVEAT = (
    "2c's eval side was queried 2026-08-12 and its ascent table is "
    "committed and known to the designers; 2d tests whether a predictor "
    "with ZERO free parameters ranks a KNOWN outcome, not a sealed "
    "forecast (design §2). A PASS licenses only the §6/ruling-g "
    "sentence; 'Prediction 2 supported' is reserved for the §9 "
    "successor.")

# ----------------------------------------------------- frozen-file pins

FROZEN_IMPORT_SHA256_2D = {
    EXP2C / "harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    EXP2C / "analyze.py":
        "ccb06ea82ba92fc29332c9acc123551746fef466274b8081d00db40ef6a05e73",
    EXP2C / "run" / "power_table.py":
        "89816cf0e7e2418e748104dbc32fd50e12ded78988f2c2c04b05ff1a89c58da1",
    EXP2C / "run" / "m5_ascent.py":
        "f85494f29a0f56dfc0c892db38151b4187678488fc02f7580d22c1cf5bbf25f5",
    EXP2C / "battery" / "family_map.py":
        "46477b37683c8ea0e1f2f219dce96858a0dcf91710b15cae45a8cf4c4c7ab375",
    EXP2C / "battery" / "base.py":
        "6d77c3c91c5ca0eb84e1a011ef64af0e04ade6fe8d1ad42d526be3a37fbacbb2",
    EXP2C / "results" / "ascent_scores.json":
        "2ef0430c455880fdb201c9444b28aef3365b9a68ac373b66d7a3e822959169d8",
    EXP2C / "results" / "verdict.json":
        "786e30e240ef4da576bdc970abe4f6e9f22dc3ee455766f37381827c3a4ebbb1",
    EXP2C / "results" / "probe_scores.json":
        "9d009e82c427adae08705bf01b169e00a154eb17601ee44eb6bde8b6ec736a42",
    EXP2C / "results" / "reuse_manifest.json":
        "b1c90f7b6221868348e2d815a2e55bfa31e870333dbbd779b305489b031f4126",
    EXP2B / "models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
    EXP3 / "sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
    EXP3 / "run" / "run_cell.py":
        "5c018457d9eb999079b4b0426dc0ecadf10baed6339d32b5eb914f280da35b46",
    EXP3 / "analyze_3.py":
        "aa0cb2374fbdffde2f9eaae26cee1ce51f9f42c0b32fd89f4f8754c983a92274",
    EXP3 / "stream_map.json":
        "ea299282342de59d8267682afbf51931521c742a7950215d7acfdc40584fe7a9",
    EXP3C / "analyze_3c.py":
        "66b78ffbedb808625ed33019f29d2ef8ec9d0f31a1115eb7cb08ad3e67d42d84",
    EXP3D / "rederive_3d.py":
        "8421433ffe328e7e2ad8d2877150f9bfc0279c9337576fd5860e917dc8690870",
}

# §4: exp3's committed seed-0..3 reversal streams — gate 1's comparison
# targets, by literal (reverse_string's two equal 3c/3d/3e's pins).
COMMITTED_DRAWS_SHA256 = {
    "reverse_string": {
        "410m": "34dd8fc48e9dec001f8575236bad15b1b360d80e4c7785b63267a8692b42cc6c",
        "1b": "45049c9b82a98d8c7fa3816981ce7a33c49b85d3521956b7994feb348b279726",
    },
    "rev_string7": {
        "410m": "7554c88f2f1576efac24506c1b0e60c6cf54e4be6874494f1727f9f9d830a42e",
        "1b": "4b8afc4b6eb14764bbd48649b6e07fd46caa4a7af3a2f2929f15d66b21f876f0",
    },
}
# exp3's committed fp16 greedy continuations for the same 4 cells — the
# argmax tier's printed comparison (non-gating; build dial, ledgered).
COMMITTED_REDECODE_SHA256 = {
    "reverse_string": {
        "410m": "ef8609cd515097acb4f6c2da04dc66cbacc69278741253a06ba31af98d27a23f",
        "1b": "59faee21f273f58b710cce36265248fbfca7b42b19100a63af33abf2d20bd77f",
    },
    "rev_string7": {
        "410m": "d905ea6bd16681a1cf1f081656caf44cd5dfa9820b7da22ca17dc09a746b1099",
        "1b": "616b77dcd76959848f69a728fcac91a0ab5df35436fa5852cc1b4d87abb02554",
    },
}
# §4: the verified draws exp3's seed-0 streams carry (its sha-pinned
# records' per_seed_tallies["0"].full_string) — gate 1 must reproduce
# them by address. Re-scored from committed bytes by the referent
# battery and at every run().
GATE1_EXPECTED_FIRES = {
    ("reverse_string", "1b"): ({"item": 436, "seed": 0, "draw": 6},),
    ("reverse_string", "410m"): (),
    ("rev_string7", "1b"): (),
    ("rev_string7", "410m"): (),
}
# §4: the standing contamination referent — exp3's untrained twins,
# 0 verified / 512,000 reversal + 64,000 control draws (3d's pins by
# value). No new twin is sampled.
TWIN_REVERSAL_DRAWS = 512_000
TWIN_CONTROL_DRAWS = 64_000

# §4: 2c's verdict literals, for the comparability column
VERDICT_2C_PIN = {"rho": 0.3679488492919918, "block_p": 0.13054869451305487,
                  "ci": [-0.18452329508460297, 0.7624136653919262],
                  "verdict": "FAIL"}

# referents_2d.json: per-file sha256 of every committed input that is
# not pinned by literal above (2c's 204 m4 records, the 34 item files
# again, exp3's 4 shard records). Generated by make_referents_2d.py at
# build; the FILE's own sha is the literal here.
REFERENTS_FILE_SHA256 = \
    "95eded96af9b9c7b52ab1d1eb457d9a4fd6af94749f040f2655859183a97ad59"


def check_frozen_imports_2d() -> None:
    for path, want in FROZEN_IMPORT_SHA256_2D.items():
        got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if got != want:
            raise ValueError(
                f"frozen file {path} has sha256 {got}, expected {want} — "
                f"2c/2b/exp3/3c/3d are closed and their files are 2d's "
                f"referents; a changed byte means these are not the "
                f"committed streams (frozen things stay frozen, "
                f"executable form)")


_LITERAL_PIN = object()


def load_referents(path=REFERENTS_PATH, *, file_sha_pin=_LITERAL_PIN) -> dict:
    """The per-file sha manifest; its own bytes pinned by literal
    (`file_sha_pin` defaults to the literal; None skips the file pin —
    tests only), and every entry re-hashed against the tree."""
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    pin = REFERENTS_FILE_SHA256 if file_sha_pin is _LITERAL_PIN else file_sha_pin
    if pin is not None and got != pin:
        raise ValueError(f"{path} has sha256 {got} against the pinned {pin}")
    rec = json.loads(raw)
    bad = []
    for rel, want in rec["files"].items():
        p = REPO / rel
        if not p.is_file():
            bad.append((rel, "missing"))
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != want:
            bad.append((rel, h))
    if bad:
        raise ValueError(f"{len(bad)} referent file(s) differ from the "
                         f"manifest: {bad[:5]}")
    return rec


# ------------------------------------------------------------ stream map

def stream_seed(rung, size, mode, seed, item_idx) -> int:
    from experiments.exp3.sampler import stream_seed as ss
    return ss(rung, size, mode, seed, item_idx)


def dump_stream_map_2d(path=STREAM_MAP_2D_PATH) -> dict:
    """(rung, size, trained, seed ∈ {0, 1000}) → item-0/499 endpoints
    under exp3's exact formula and namespace. The seed-0 reversal
    entries duplicate exp3's committed map on purpose; the continuity
    check asserts the overlap byte-equal."""
    cells = {}
    for rung in RUNGS:
        for size in PROBE_SIZES:
            for tier, spec in TIERS.items():
                s = spec["seed"]
                cells[f"{rung}/{size}/{MODE}/s{s}"] = {
                    "tier": tier,
                    "item0": stream_seed(rung, size, MODE, s, 0),
                    "item499": stream_seed(rung, size, MODE, s, 499),
                }
    out = {
        "formula": "int.from_bytes(sha256('exp3|{rung}|{size}|{mode}|"
                   "s{seed}|i{item}').digest()[:8], 'big') & ((1<<63)-1)",
        "namespace_note": "the namespace string stays 'exp3' DELIBERATELY "
                          "(design §3): the seed-0 reversal substreams ARE "
                          "exp3's committed ones — gate 1 on the "
                          "production path",
        "per_item_substreams": True,
        "chunk_rows": 16,
        "draw_order": "within a seed, chunks in index order; within a "
                      "chunk, rows in row order; one multinomial call per "
                      "step over all rows",
        "tiers": TIERS,
        "pilot_seed_note": "1000 (ruling L, 2026-08-21): outside every "
                           "committed seed range on this namespace — exp3 "
                           "0–3, 3c 4–15, 3d 16–39, 3e 28–167",
        "max_new_tokens": {r: bt.max_new_tokens(r) for r in RUNGS},
        "cells": cells,
    }
    Path(path).write_text(json.dumps(out, indent=1))
    return out


def check_stream_map_2d(path=STREAM_MAP_2D_PATH, *,
                        exp3_map_path=None) -> dict:
    """The committed 2d map == the frozen formula, and its seed-0
    reversal entries == exp3's committed map entries."""
    rec = json.loads(Path(path).read_text())
    cells = {}
    for rung in RUNGS:
        for size in PROBE_SIZES:
            for tier, spec in TIERS.items():
                s = spec["seed"]
                cells[f"{rung}/{size}/{MODE}/s{s}"] = {
                    "tier": tier,
                    "item0": stream_seed(rung, size, MODE, s, 0),
                    "item499": stream_seed(rung, size, MODE, s, 499),
                }
    if rec.get("cells") != cells:
        raise ValueError("stream_map_2d.json disagrees with the frozen "
                         "formula")
    if rec.get("max_new_tokens") != {r: bt.max_new_tokens(r) for r in RUNGS}:
        raise ValueError("stream_map_2d.json token budgets disagree with "
                         "2c's MAX_NEW_TOKENS")
    exp3_map = json.loads(Path(exp3_map_path or EXP3 / "stream_map.json")
                          .read_text())
    for rung in REVERSAL_RUNGS:
        for size in PROBE_SIZES:
            key = f"{rung}/{size}/{MODE}/s0"
            mine = {k: rec["cells"][key][k] for k in ("item0", "item499")}
            if exp3_map["cells"].get(key) != mine:
                raise ValueError(f"{key}: 2d's substream endpoints differ "
                                 f"from exp3's committed map — gate 1 "
                                 f"could not be byte identity")
    return {"n_cells": len(cells), "continuity_cells": 4}


# ------------------------------------------------------------- verify

def load_verify() -> callable:
    """3c's total wrapper over 2c's normalize (draw-side IndexError →
    False; answer side stays a hard error)."""
    from experiments.exp3c.analyze_3c import load_verify_3c
    return load_verify_3c()


# ------------------------------------------------------------ outcome

def _m4_path(size, mode, rung) -> Path:
    return EXP2C / "results" / "m4" / f"{size}_{mode}" / f"{rung}.json"


def load_outcome(floors: dict, *, referents=None) -> dict:
    """§5.2: the corrected outcome from 2c's committed m4 records.
    Per rung per eval size: trained acc vs the majority floor by the
    binomial bar → corrected margin; ascent = mean over sizes;
    RISING ⇔ ascent > 0 (any size); 12b-only as a sensitivity; the
    untrained twin acc printed, not used. KNOWN-ANSWER GATE: 2c's own
    `m5_ascent.rung_ascent_score` on the same records reproduces
    `ascent_scores.json` EXACTLY, rung by rung."""
    from experiments.exp2c.run import m5_ascent as m5

    ascent_2c = json.loads((EXP2C / "results" / "ascent_scores.json")
                           .read_text())
    if ascent_2c["n_rungs"] != len(RUNGS) or \
            set(ascent_2c["rungs"]) != set(RUNGS):
        raise ValueError("2c's ascent_scores.json does not cover the 34")
    rungs = {}
    gate_mismatch = []
    for rung in RUNGS:
        cells = {}
        for size in EVAL_SIZES:
            pair = []
            for mode in ("trained", "untrained"):
                p = _m4_path(size, mode, rung)
                raw = p.read_bytes()
                if referents is not None:
                    rel = str(p.relative_to(REPO))
                    if rel not in referents["files"]:
                        raise ValueError(f"{rel} is not in the referent "
                                         f"manifest")
                rec = json.loads(raw)
                if (rec.get("capability"), rec.get("size"),
                        rec.get("mode")) != (rung, size, mode):
                    raise ValueError(f"{p}: contents disagree with path")
                if rec.get("n") != N_ITEMS:
                    raise ValueError(f"{p}: n {rec.get('n')} != {N_ITEMS}")
                pair.append(rec)
            cells[size] = tuple(pair)
        # the known-answer gate: 2c's frozen rule on the same bytes
        got = m5.rung_ascent_score(cells)
        want = ascent_2c["rungs"][rung]
        if got["ascent_score"] != want["ascent_score"] or any(
                got["per_size"][s]["margin"] != want["per_size"][s]["margin"]
                for s in EVAL_SIZES):
            gate_mismatch.append(rung)
        c = floors[rung]["floor"]
        per_size = {}
        for size in EVAL_SIZES:
            tr, un = cells[size]
            m = st.corrected_margin(tr["correct"], tr["n"], c)
            per_size[size] = {**m, "trained_acc": tr["correct"] / tr["n"],
                              "untrained_acc": un["correct"] / un["n"],
                              "untrained_correct": int(un["correct"]),
                              "model_sha": tr.get("sha")}
        ascent = sum(per_size[s]["margin"] for s in EVAL_SIZES) / \
            len(EVAL_SIZES)
        rungs[rung] = {
            "family": FAMILY_OF[rung], "floor": c,
            "per_size": per_size,
            "corrected_ascent": float(ascent),
            "rising": bool(ascent > 0),
            "rising_12b": bool(per_size["12b"]["margin"] > 0),
            "ascent_2c": float(want["ascent_score"]),
        }
    if gate_mismatch:
        raise ValueError(
            f"known-answer gate: 2c's m5 rule on the committed m4 records "
            f"does not reproduce ascent_scores.json for {gate_mismatch} — "
            f"the outcome records are not the ones 2c scored")
    return {"rungs": rungs,
            "n_rising": sum(r["rising"] for r in rungs.values()),
            "n_rising_12b": sum(r["rising_12b"] for r in rungs.values()),
            "families_with_rising": sorted({r["family"] for r in
                                            rungs.values() if r["rising"]}),
            "known_answer_gate": "PASS (34/34 rungs reproduce 2c's ascent)"}


# ------------------------------------------------------ probe predictor

def load_probe_predictor() -> dict:
    probe = json.loads((EXP2C / "results" / "probe_scores.json").read_text())
    order = tuple((r["name"], r["family"]) for r in probe["rungs"])
    if order != bt.RUNG_ORDER_2D:
        raise ValueError("probe_scores.json order != RUNG_ORDER_2D")
    return {r["name"]: float(r["probe_score"]) for r in probe["rungs"]}


# ------------------------------------------------------ sampled tiers

def tier_record_path(root, tier, size, rung) -> Path:
    return Path(root) / "results" / tier / f"{size}_{MODE}" / f"{rung}.json"


def tier_draws_path(root, tier, size, rung) -> Path:
    return (Path(root) / "results" / tier / f"{size}_{MODE}"
            / f"{rung}.draws.jsonl.gz")


def read_rows(path, *, seed, dps, n_items=N_ITEMS) -> list:
    """exp3's row format, coverage pinned: exactly items 0..n_items−1,
    each with exactly the tier's seed stream at exactly dps draws."""
    rows, seen = [], set()
    with gzip.open(Path(path), "rt") as f:
        for line in f:
            row = json.loads(line)
            i = row.get("item")
            if not isinstance(i, int) or i in seen or not 0 <= i < n_items:
                raise ValueError(f"{path}: bad or duplicate item {i!r}")
            seen.add(i)
            draws = row.get("draws")
            if not isinstance(draws, dict) or set(draws) != {str(seed)}:
                raise ValueError(
                    f"{path} item {i}: seed streams "
                    f"{sorted(draws) if isinstance(draws, dict) else draws!r}"
                    f" are not the tier's seed {seed}")
            stream = draws[str(seed)]
            if not isinstance(stream, list) or len(stream) != dps or \
                    not all(isinstance(x, str) for x in stream):
                raise ValueError(
                    f"{path} item {i}: stream of "
                    f"{len(stream) if isinstance(stream, list) else stream!r}"
                    f" draws against draws_per_seed {dps}")
            rows.append(row)
    if len(seen) != n_items:
        raise ValueError(f"{path}: {len(seen)} items against {n_items} — "
                         f"coverage incomplete")
    rows.sort(key=lambda r: r["item"])
    return rows


def tally_rows(rows, answers, answer_type, verify_fn, *, seed) -> dict:
    """Verified draws and addresses, recomputed from raw bytes."""
    fires, n = [], 0
    for row in rows:
        i = row["item"]
        for d_idx, text in enumerate(row["draws"][str(seed)]):
            n += 1
            if verify_fn(text, answers[i], answer_type):
                fires.append({"item": i, "seed": seed, "draw": d_idx,
                              "text": text})
    return {"verified": len(fires), "n_draws": n, "fires": fires}


def _check_tier_provenance(rec, p, *, tier, size, rung, cap) -> None:
    spec = TIERS[tier]
    want = {"rung": rung, "size": size, "mode": MODE, "tier": tier,
            "n_items": N_ITEMS, "answer_type": cap["answer_type"],
            "n_shots": bt.N_SHOTS, "dtype": SAMPLING_DTYPE,
            "seeds": [spec["seed"]], "draws_per_seed": spec["draws_per_seed"],
            "k_total": spec["draws_per_seed"],
            "max_new_tokens": bt.max_new_tokens(rung),
            "items_sha256": bt.ITEMS_SHA_PIN[rung],
            "stream_namespace": STREAM_NAMESPACE}
    for k, v in want.items():
        if rec.get(k) != v:
            raise ValueError(f"{p}: {k} = {rec.get(k)!r}, expected {v!r}")
    if [str(a) for a in rec.get("answers", [])] != \
            [str(it["answer"]) for it in cap["eval_items"]]:
        raise ValueError(f"{p}: answers disagree with the sha-pinned item "
                         f"file — not the committed battery")
    from models import PYTHIA_SHAS   # 2b's, sys.path-ordered
    if rec.get("model_sha") != PYTHIA_SHAS[size]:
        raise ValueError(f"{p}: model_sha {rec.get('model_sha')} != 2b's "
                         f"pinned {PYTHIA_SHAS[size]}")


def load_sampling_tier(root, tier, battery, verify_fn, *,
                       rungs=RUNGS, sizes=PROBE_SIZES) -> dict:
    """One tier's cells, raw draws re-tallied with 3c's total verify;
    stored tallies must agree; provenance pinned. Refuses an
    incomplete tier (2c's m5 discipline): a rung scored against a
    different amount of evidence carries a different meaning."""
    spec = TIERS[tier]
    out = {}
    missing = []
    for size in sizes:
        for rung in rungs:
            p = tier_record_path(root, tier, size, rung)
            g = tier_draws_path(root, tier, size, rung)
            if not (p.exists() and g.exists()):
                missing.append(f"{tier}/{size}/{rung}")
    if missing:
        raise FileNotFoundError(
            f"{tier} tier incomplete: {len(missing)} of "
            f"{len(sizes) * len(rungs)} cells missing (e.g. {missing[0]})")
    for size in sizes:
        for rung in rungs:
            p = tier_record_path(root, tier, size, rung)
            g = tier_draws_path(root, tier, size, rung)
            rec = json.loads(p.read_text())
            cap = battery[rung]
            _check_tier_provenance(rec, p, tier=tier, size=size, rung=rung,
                                   cap=cap)
            rows = read_rows(g, seed=spec["seed"], dps=spec["draws_per_seed"])
            answers = [str(it["answer"]) for it in cap["eval_items"]]
            t = tally_rows(rows, answers, cap["answer_type"], verify_fn,
                           seed=spec["seed"])
            stored = rec.get("per_seed_tallies", {}).get(str(spec["seed"]))
            if not stored or stored.get("full_string") != t["verified"] or \
                    stored.get("n_draws") != t["n_draws"]:
                raise ValueError(
                    f"{p}: stored tallies {stored} disagree with the "
                    f"recompute ({t['verified']}/{t['n_draws']}) — runner "
                    f"and analyzer no longer agree on what was drawn")
            if t["n_draws"] != N_ITEMS * spec["draws_per_seed"]:
                raise ValueError(f"{p}: {t['n_draws']} draws")
            out[(rung, size)] = {
                "verified": t["verified"], "n_draws": t["n_draws"],
                "rate": t["verified"] / t["n_draws"],
                "cp95": list(st.clopper_pearson(t["verified"], t["n_draws"])),
                "fires": t["fires"],
                "rows": rows if rung in REVERSAL_RUNGS and tier == "main"
                else None,
                "record_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "draws_sha256": hashlib.sha256(g.read_bytes()).hexdigest(),
                "model_sha": rec["model_sha"], "stack": rec.get("stack"),
            }
    return out


def predictor_from_tier(cells, floors, *, n_draws_per_rung,
                        rungs=RUNGS, sizes=PROBE_SIZES) -> dict:
    """§5.1: corrected sampled margin per (rung, size) by the binomial
    bar over the tier's draws; score = mean over the two sizes; the
    per-size columns kept for the named replications."""
    out = {}
    for rung in rungs:
        c = floors[rung]["floor"]
        per = {}
        for size in sizes:
            cell = cells[(rung, size)]
            if cell["n_draws"] != n_draws_per_rung:
                raise ValueError(f"{rung}/{size}: {cell['n_draws']} draws")
            per[size] = st.corrected_margin(cell["verified"], cell["n_draws"],
                                            c)
        out[rung] = {
            "per_size": per,
            "score": float(sum(per[s]["margin"] for s in sizes) / len(sizes)),
            "raw_zero": {s: bool(cells[(rung, s)]["verified"] == 0)
                         for s in sizes},
        }
    return out


# ---------------------------------------------------------------- gate 1

def gate1_record_path(root, size, rung) -> Path:
    return Path(root) / "results" / "gate1" / f"{size}_{MODE}" / f"{rung}.json"


def _check_gate1_record(rec, p, *, rung, size, root, expected_fires,
                        committed_shas) -> dict:
    """One gate-1 record's pins (shared by the complete-tree loader and
    the halt scan): path/contents, seed/dps, coverage (3d F2), items
    sha, attested committed sha == §4 literal (== disk on the real
    tree, 3c B), model_sha == 2b's pin (freeze F-2; 3e F-3's analogue),
    n_diffs/diffs coherence, fires == the committed addresses when
    clean."""
    if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
            (rung, size, MODE):
        raise ValueError(f"{p}: contents disagree with path")
    if rec.get("seeds_rederived") != [GATE1_SEED] or \
            rec.get("draws_per_seed") != TIERS["main"]["draws_per_seed"]:
        raise ValueError(f"{p}: seed/dps are not the main tier's")
    if rec.get("n_items") != N_ITEMS or \
            rec.get("draws_compared") != GATE1_COVERAGE:
        raise ValueError(
            f"{p}: coverage {rec.get('n_items')} items / "
            f"{rec.get('draws_compared')} draws against the pinned "
            f"{N_ITEMS} / {GATE1_COVERAGE} — gate 1 must cover the "
            f"whole committed stream (3d F2)")
    if rec.get("items_sha256") != bt.ITEMS_SHA_PIN[rung]:
        raise ValueError(f"{p}: items_sha256 against the §4 pin")
    want = committed_shas[rung][size]
    if rec.get("committed_draws_sha256") != want:
        raise ValueError(
            f"{p}: attested committed sha "
            f"{rec.get('committed_draws_sha256')} != the §4 literal "
            f"{want}")
    if Path(root) == EXP2D:
        disk = hashlib.sha256(
            (EXP3 / "results" / "sampling" / f"{size}_{MODE}"
             / f"{rung}.draws.jsonl.gz").read_bytes()).hexdigest()
        if disk != want:
            raise ValueError(f"exp3 shard {rung}/{size} on disk "
                             f"hashes to {disk} against the §4 "
                             f"literal {want}")
    from models import PYTHIA_SHAS   # 2b's, sys.path-ordered
    if rec.get("model_sha") != PYTHIA_SHAS[size]:
        raise ValueError(f"{p}: model_sha {rec.get('model_sha')} != 2b's "
                         f"pinned {PYTHIA_SHAS[size]} — the gate-1 "
                         f"comparison was not made with the pinned weights")
    diffs = rec.get("diffs")
    if not isinstance(diffs, list) or \
            rec.get("n_diffs") != len(diffs):
        raise ValueError(f"{p}: n_diffs/diffs disagree")
    fires = [{"item": int(f["item"]), "seed": int(f["seed"]),
              "draw": int(f["draw"])}
             for f in rec.get("fires_reproduced", [])]
    exp = [dict(a) for a in expected_fires[(rung, size)]]
    if len(diffs) == 0 and sorted(fires, key=lambda a: (
            a["item"], a["draw"])) != sorted(exp, key=lambda a: (
            a["item"], a["draw"])):
        raise ValueError(
            f"{p}: a clean comparison that does not carry the "
            f"committed fires {exp} (got {fires}) — the comparator "
            f"or the scorer is wrong")
    return {"n_diffs": len(diffs), "diffs": diffs,
            "draws_compared": rec["draws_compared"],
            "fires_reproduced": fires,
            "model_sha": rec.get("model_sha"),
            "stack": rec.get("stack")}


def load_gate1(root, *, expected_fires=None, committed_shas=None) -> dict:
    """The 4 production-path comparison records: coverage pinned at
    500 × 64, seed 0, committed sha == literal == disk (3c finding B
    both directions), fires reproduced == the expected addresses when
    clean. A missing record is a hard error (main incomplete); a
    record with diffs is a VERDICT input (INSUFFICIENT_DATA)."""
    expected_fires = GATE1_EXPECTED_FIRES if expected_fires is None \
        else expected_fires
    committed_shas = COMMITTED_DRAWS_SHA256 if committed_shas is None \
        else committed_shas
    out, diff_cells = {}, []
    for rung in REVERSAL_RUNGS:
        for size in PROBE_SIZES:
            p = gate1_record_path(root, size, rung)
            if not p.exists():
                raise FileNotFoundError(f"gate-1 record missing: {p}")
            rec = json.loads(p.read_text())
            cell = _check_gate1_record(rec, p, rung=rung, size=size, root=root,
                                       expected_fires=expected_fires,
                                       committed_shas=committed_shas)
            out[(rung, size)] = cell
            if cell["diffs"]:
                diff_cells.append(f"{rung}/{size}")
    return {"cells": out, "diff_cells": diff_cells,
            "total_draws_compared": sum(c["draws_compared"]
                                        for c in out.values())}


def halted_draws_path(root, size, rung) -> Path:
    """Where the runner parks a halted reversal rung's rows (the normal
    draws file is deliberately NOT written on a diff)."""
    return tier_draws_path(root, "main", size, rung).with_suffix(
        ".HALTED.jsonl.gz")


def scan_gate1_halt(root, *, expected_fires=None, committed_shas=None,
                    exp3_root=None) -> dict:
    """§6 precedence, EXECUTABLE BEFORE ANY TIER IS LOADED (freeze
    finding F-1, 3a's class): after a gate-1 halt the runner leaves a
    gate-1 record with diffs, a .HALTED draws file and NO normal draws
    file, so the main tier is incomplete by construction and the
    complete-tree loaders would refuse with FileNotFoundError instead
    of delivering the INSUFFICIENT_DATA terminal. This scan validates
    every gate-1 record that EXISTS (same pins as `load_gate1`),
    collects the cells with diffs, and — not trusting the runner —
    re-derives each halted cell's diff count from the .HALTED rows
    through 3d's comparator when that file is present (absent: the
    record's diffs stand, noted; the terminal is the conservative
    one). A clean scan decides nothing; `load_gate1` still runs on
    the complete tree."""
    from experiments.exp3.run.run_cell import read_draws
    from experiments.exp3d.rederive_3d import diff_seed
    expected_fires = GATE1_EXPECTED_FIRES if expected_fires is None \
        else expected_fires
    committed_shas = COMMITTED_DRAWS_SHA256 if committed_shas is None \
        else committed_shas
    exp3_root = Path(exp3_root or EXP3)
    dps = TIERS["main"]["draws_per_seed"]
    cells, halted, present = {}, [], 0
    for rung in REVERSAL_RUNGS:
        for size in PROBE_SIZES:
            p = gate1_record_path(root, size, rung)
            if not p.exists():
                continue
            present += 1
            rec = json.loads(p.read_text())
            cell = _check_gate1_record(rec, p, rung=rung, size=size, root=root,
                                       expected_fires=expected_fires,
                                       committed_shas=committed_shas)
            if not cell["diffs"]:
                continue
            hp = halted_draws_path(root, size, rung)
            if hp.exists():
                committed = read_draws(exp3_root / "results" / "sampling"
                                       / f"{size}_{MODE}"
                                       / f"{rung}.draws.jsonl.gz")
                regenerated = {int(r["item"]): list(r["draws"][str(GATE1_SEED)])
                               for r in read_draws(hp)}
                again = diff_seed(committed, regenerated, dps=dps,
                                  seed=GATE1_SEED)
                if len(again) != cell["n_diffs"]:
                    raise ValueError(
                        f"gate 1 {rung}/{size}: the halt record says "
                        f"{cell['n_diffs']} diffs, the analyzer's own "
                        f"comparison of the .HALTED rows finds {len(again)}")
                cell["halted_rows_reverified"] = True
            else:
                cell["halted_rows_reverified"] = False
            cells[(rung, size)] = cell
            halted.append(f"{rung}/{size}")
    return {"halted_cells": halted, "cells": cells,
            "records_present": present}


def _tier_completeness(root) -> dict:
    out = {}
    for tier in ("pilot", "main"):
        for size in PROBE_SIZES:
            n = sum(1 for r in RUNGS
                    if tier_record_path(root, tier, size, r).exists()
                    and tier_draws_path(root, tier, size, r).exists())
            out[f"{tier}/{size}"] = {"rungs_complete": n, "of": len(RUNGS)}
    for size in PROBE_SIZES:
        n = sum(1 for r in RUNGS if argmax_record_path(root, size, r).exists())
        out[f"argmax/{size}"] = {"rungs_complete": n, "of": len(RUNGS)}
    return out


def insufficient_data_record(halt, *, root, outcome, twin, power) -> dict:
    """The §6 terminal-1 record built from what a halted campaign
    leaves: the tree's verdict, the diffs verbatim, the completeness of
    every tier, the known outcome and the standing referents. No
    primary is computable and none is faked."""
    tree = st.verdict_tree(gate1_diff_cells=halt["halted_cells"],
                           auc_obs=None, block_p=None, ci=[None, None])
    return {
        "verdict": tree["verdict"], "reason": tree["reason"],
        "known_outcome_caveat": KNOWN_OUTCOME_CAVEAT,
        "halted_before_completion": True,
        "tiers": _tier_completeness(root),
        "primary": None,
        "outcome_summary": {
            "n_rising": outcome["n_rising"],
            "n_rising_12b": outcome["n_rising_12b"],
            "families_with_rising": outcome["families_with_rising"],
            "known_answer_gate": outcome["known_answer_gate"],
        },
        "gate1": {"diff_cells": halt["halted_cells"],
                  "records_present": halt["records_present"],
                  "cells": {f"{r}/{s}": {k: v for k, v in c.items()
                                         if k != "diffs"}
                            for (r, s), c in halt["cells"].items()},
                  "diffs_verbatim": {f"{r}/{s}": c["diffs"]
                                     for (r, s), c in halt["cells"].items()}},
        "power": None if power is None else {
            "declared_status": power["declared_status"],
            "power": power["power"]},
        "twin_referent": twin,
        "n_rungs": len(RUNGS), "n_families": bt.N_FAMILIES,
    }


def check_gate1_vs_main(gate1, main_cells) -> None:
    """The gate-1 record for a cell must have been computed against the
    SAME main-tier draws the analyzer loaded: the main cell's raw
    rows, compared again here to exp3's committed bytes through 3d's
    comparator, give the same diff count. (The runner wrote the
    record; the analyzer does not trust it.)"""
    from experiments.exp3.run.run_cell import read_draws
    from experiments.exp3d.rederive_3d import diff_seed
    dps = TIERS["main"]["draws_per_seed"]
    for rung in REVERSAL_RUNGS:
        for size in PROBE_SIZES:
            committed = read_draws(EXP3 / "results" / "sampling"
                                   / f"{size}_{MODE}"
                                   / f"{rung}.draws.jsonl.gz")
            regenerated = {row["item"]: row["draws"][str(GATE1_SEED)]
                           for row in main_cells[(rung, size)]["rows"]}
            diffs = diff_seed(committed, regenerated, dps=dps,
                              seed=GATE1_SEED)
            if len(diffs) != gate1["cells"][(rung, size)]["n_diffs"]:
                raise ValueError(
                    f"gate 1 {rung}/{size}: the runner's record says "
                    f"{gate1['cells'][(rung, size)]['n_diffs']} diffs, the "
                    f"analyzer's own comparison of the main draws finds "
                    f"{len(diffs)}")


# ---------------------------------------------------------------- argmax

def argmax_record_path(root, size, rung) -> Path:
    return Path(root) / "results" / "argmax" / f"{size}_{MODE}" / f"{rung}.json"


def load_argmax(root, battery, verify_fn, *, rungs=RUNGS,
                sizes=PROBE_SIZES, required=True) -> dict | None:
    """§5.4 descriptive: greedy fp16 accuracy at 410m/1b from the
    committed continuations (re-verified; stored count must agree).
    `required=False` returns None on an absent tier (the argmax tier
    runs AFTER main; the verdict's primary does not need it — but
    run() requires it so the record is complete)."""
    missing = [f"{s}/{r}" for s in sizes for r in rungs
               if not argmax_record_path(root, s, r).exists()]
    if missing:
        if required:
            raise FileNotFoundError(f"argmax tier incomplete: {missing[:3]}")
        return None
    out = {}
    for size in sizes:
        for rung in rungs:
            p = argmax_record_path(root, size, rung)
            rec = json.loads(p.read_text())
            cap = battery[rung]
            from models import PYTHIA_SHAS   # 2b's, sys.path-ordered
            if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
                    (rung, size, MODE) or rec.get("dtype") != ARGMAX_DTYPE \
                    or rec.get("items_sha256") != bt.ITEMS_SHA_PIN[rung] \
                    or rec.get("max_new_tokens") != bt.max_new_tokens(rung) \
                    or rec.get("n_shots") != bt.N_SHOTS \
                    or rec.get("answer_type") != cap["answer_type"] \
                    or rec.get("model_sha") != PYTHIA_SHAS[size]:
                raise ValueError(f"{p}: provenance disagrees with the pins")
            conts = rec.get("continuations")
            if not isinstance(conts, list) or len(conts) != N_ITEMS:
                raise ValueError(f"{p}: {len(conts) if isinstance(conts, list) else conts!r} continuations")
            correct = sum(verify_fn(c, str(it["answer"]), cap["answer_type"])
                          for c, it in zip(conts, cap["eval_items"]))
            if rec.get("correct") != correct:
                raise ValueError(f"{p}: stored correct {rec.get('correct')} "
                                 f"!= recompute {correct}")
            out[(rung, size)] = {
                "correct": int(correct), "n": N_ITEMS, "acc": correct / N_ITEMS,
                "cp95": list(st.clopper_pearson(correct, N_ITEMS)),
                "redecode_diffs": rec.get("redecode_diffs"),
            }
    return out


# ------------------------------------------------------------------ twin

def load_twin_record(exp3_root=EXP3, *, verify_fn=None) -> dict:
    """exp3's 8 untrained twin cells through exp3's OWN frozen loader:
    0 verified across 512,000 + 64,000 committed draws, or a hard
    error. The standing contamination referent; no new twin."""
    from experiments.exp3 import analyze_3 as a3
    verify_fn = verify_fn or load_verify()
    cells = a3.load_sampling_cells(Path(exp3_root), verify_fn=verify_fn)
    rev = sum(cells[(r, s, "untrained")]["recomputed"]["n_draws_total"]
              for r in a3.REVERSAL_RUNGS for s in a3.PROBE_SIZES)
    ctrl = sum(cells[(r, s, "untrained")]["recomputed"]["n_draws_total"]
               for r in (a3.POSITIVE_CONTROL, a3.MATCHED_CONTROL)
               for s in a3.PROBE_SIZES)
    fires = sum(cells[(r, s, "untrained")]["recomputed"]["full_string_total"]
                for r in a3.RUNGS for s in a3.PROBE_SIZES)
    return check_twin_totals(fires, rev, ctrl)


def check_twin_totals(fires: int, rev: int, ctrl: int) -> dict:
    """The standing referent, as a pure comparison: 0 fires AND the
    pinned draw totals, or a hard error."""
    if fires != 0 or rev != TWIN_REVERSAL_DRAWS or ctrl != TWIN_CONTROL_DRAWS:
        raise ValueError(
            f"twin record recomputed as {fires} fires / {rev} + {ctrl} "
            f"draws against the standing 0 / {TWIN_REVERSAL_DRAWS} + "
            f"{TWIN_CONTROL_DRAWS}")
    return {"cells": 8, "fires": 0, "reversal_twin_draws": rev,
            "control_twin_draws": ctrl}


# ------------------------------------------------------------- power rec

def load_power_record(path=POWER_PATH, *, required=True) -> dict | None:
    p = Path(path)
    if not p.exists():
        if required:
            raise FileNotFoundError(
                f"{p} missing — the frozen §7 procedure has not run on the "
                f"pilot; main does not start without the declaration")
        return None
    rec = json.loads(p.read_text())
    for k in ("declared_status", "power", "pilot_zero_set", "pilot_predictor"):
        if k not in rec:
            raise ValueError(f"{p}: no {k!r}")
    return rec


def check_power_vs_pilot(power, pilot_predictor) -> None:
    """The declaration was computed from the pilot tier AS IT WAS; the
    record attests the predictor it saw (`pilot_predictor`), and that
    attestation is COMPARED here to the pilot tier the analyzer just
    recomputed from raw bytes (freeze F-2; 3c B's class — attested but
    never compared). A regenerated or edited pilot behind a standing
    declaration is a hard error, not a verdict."""
    seen = power["pilot_predictor"]
    bad = []
    for r in RUNGS:
        got = seen.get(r)
        if not isinstance(got, dict) \
                or got.get("score") != pilot_predictor[r]["score"] \
                or got.get("raw_zero") != pilot_predictor[r]["raw_zero"]:
            bad.append(r)
    if bad:
        raise ValueError(
            f"power_2d.json's attested pilot predictor disagrees with the "
            f"pilot tier on disk for {len(bad)} rung(s) (e.g. {bad[0]}): "
            f"the declaration was not computed from these pilot draws")


# --------------------------------------------------------------- verdict

def percolation_candidates(outcome, main_cells, probe, *, rungs=RUNGS) -> list:
    """§5.4 / fix j: rising AND zero verified draws in the 32,000
    main-tranche 1b draws AND probe margin 0."""
    return [r for r in rungs
            if outcome["rungs"][r]["rising"]
            and main_cells[(r, REPLICATION_SIZE)]["verified"] == 0
            and probe[r] == 0]


def _family_contiguous(values: dict) -> np.ndarray:
    return np.asarray([values[r] for r in RUNGS], dtype=float)


def _labels(outcome, key="rising") -> np.ndarray:
    return np.asarray([int(outcome["rungs"][r][key]) for r in RUNGS])


def _restricted_layout(keep_mask) -> tuple:
    """Rungs kept (bool per RUNGS) → (rungs, family sizes in first-
    appearance order, family labels) for a reduced battery."""
    kept = [r for r, k in zip(RUNGS, keep_mask) if k]
    fams = [FAMILY_OF[r] for r in kept]
    order = list(dict.fromkeys(fams))
    sizes = [sum(1 for f in fams if f == fam) for fam in order]
    return kept, sizes, fams


def _ordering_secondary(x, y, label, group) -> dict:
    """§5.4 ordering: Spearman ρ over all 34 with 2c's block test and
    cluster bootstrap (drops counted)."""
    fams = [FAMILY_OF[r] for r in RUNGS]
    rho = float(spearmanr(x, y).statistic) if len(set(x)) > 1 and \
        len(set(y)) > 1 else None
    block = st.spearman_block_p(x, y, FAMILY_SIZES) if rho is not None \
        else None
    boot = st.cluster_bootstrap_spearman(x, y, fams)
    return {"against": label, "rho": rho,
            "block_p": None if block is None else float(block["p"]),
            "method": None if block is None else block["method"],
            "n_perms": None if block is None else int(block["n_perms"]),
            "bootstrap": boot}


def verdict_2d(*, outcome, predictor, probe, gate1, floors, main_cells,
               argmax, twin, power, pilot_predictor=None) -> dict:
    """§5.3 primary + §5.4 secondaries + §6 tree. `predictor` is the
    MAIN tier's (§5.1); `pilot_predictor` is printed only."""
    fams = [FAMILY_OF[r] for r in RUNGS]
    group = st.block_perm_group(FAMILY_SIZES)
    counts = st.bootstrap_counts_matrix(bt.N_FAMILIES)

    y = _labels(outcome, "rising")
    y12 = _labels(outcome, "rising_12b")
    x = _family_contiguous({r: predictor[r]["score"] for r in RUNGS})
    x1b = _family_contiguous({r: predictor[r]["per_size"]["1b"]["margin"]
                              for r in RUNGS})
    x410 = _family_contiguous({r: predictor[r]["per_size"]["410m"]["margin"]
                               for r in RUNGS})
    xp = _family_contiguous(probe)
    asc = _family_contiguous({r: outcome["rungs"][r]["corrected_ascent"]
                              for r in RUNGS})
    asc2c = _family_contiguous({r: outcome["rungs"][r]["ascent_2c"]
                                for r in RUNGS})

    primary = st.primary_test(x, y, FAMILY_SIZES, fams, group=group,
                              counts=counts)
    tree = st.verdict_tree(gate1_diff_cells=gate1["diff_cells"],
                           auc_obs=primary["auc"],
                           block_p=primary["block"]["p"],
                           ci=primary["bootstrap"]["ci"])

    # --- secondaries (non-gating) ---
    sec = {}
    sec["replication_1b_only"] = st.primary_test(
        x1b, y, FAMILY_SIZES, fams, group=group, counts=counts)
    sec["replication_410m_only"] = st.primary_test(
        x410, y, FAMILY_SIZES, fams, group=group, counts=counts)
    sec["sensitivity_12b_only_label"] = st.primary_test(
        x, y12, FAMILY_SIZES, fams, group=group, counts=counts) \
        if 0 < y12.sum() < len(y12) else None
    sec["ordering_vs_corrected_ascent"] = _ordering_secondary(
        x, asc, "corrected ascent (§5.2)", group)
    sec["ordering_vs_2c_frozen_ascent"] = _ordering_secondary(
        x, asc2c, "2c's frozen ascent (untrained floor, Fisher)", group)
    sec["ordering_vs_2c_frozen_ascent"]["comparability"] = {
        "2c_probe_predictor": VERDICT_2C_PIN}
    sec["probe_predictor_auc"] = st.primary_test(
        xp, y, FAMILY_SIZES, fams, group=group, counts=counts)
    sec["instrument_disagreement"] = {
        r: {"sampled_score": float(x[i]), "probe_score": float(xp[i]),
            "rising": bool(y[i]),
            "agree_on_zero": bool((x[i] == 0) == (xp[i] == 0))}
        for i, r in enumerate(RUNGS)}

    # §5.4 the probe-flat-but-rising pair and the percolation candidates
    pair = {}
    for r in PAIR_5_4:
        pair[r] = {
            "rising": bool(outcome["rungs"][r]["rising"]),
            "probe_score": float(probe[r]),
            "sampled": {s: {"verified": main_cells[(r, s)]["verified"],
                            "n_draws": main_cells[(r, s)]["n_draws"],
                            "cp95": main_cells[(r, s)]["cp95"],
                            "fires_verbatim": [
                                {k: f[k] for k in ("item", "draw", "text")}
                                for f in main_cells[(r, s)]["fires"]]}
                        for s in PROBE_SIZES},
        }
    candidates = percolation_candidates(outcome, main_cells, probe)
    sec["pair_5_4"] = pair
    sec["percolation_candidates"] = {
        "rule": "rising (§5.2) AND zero verified draws in the 32,000 "
                "main-tranche 1b draws AND probe margin 0 (fix j)",
        "rungs": candidates,
        "both_pair_rungs_land": all(r in candidates for r in PAIR_5_4),
        "cp95_zero_of_32000": list(st.clopper_pearson(0, MAIN_DRAWS_PER_RUNG)),
    }

    # §5.4 argmax + the from-below-performability restriction
    perf = {}
    for r in RUNGS:
        c = floors[r]["floor"]
        a1b = argmax[(r, "1b")]
        bar = st.binomial_bar(a1b["correct"], a1b["n"], c)
        perf[r] = {"acc_1b": a1b["acc"], "acc_410m": argmax[(r, "410m")]["acc"],
                   "performable_at_1b": bool(bar["significant"]),
                   "p_1b": bar["p"]}
    removed = [r for r in RUNGS if outcome["rungs"][r]["rising"]
               and perf[r]["performable_at_1b"]]
    keep = [r not in removed for r in RUNGS]
    kept, sizes_r, fams_r = _restricted_layout(keep)
    y_r = np.asarray([int(outcome["rungs"][r]["rising"]) for r in kept])
    x_r = np.asarray([predictor[r]["score"] for r in kept], dtype=float)
    restricted = None
    if 0 < y_r.sum() < len(y_r):
        restricted = st.primary_test(x_r, y_r, sizes_r, fams_r)
    sec["argmax_from_below"] = {
        "per_rung": perf,
        "rising_already_performable_at_1b": removed,
        "n_removed": len(removed),
        "restricted_primary": restricted,
        "note": "rising rungs whose 1b greedy accuracy clears the floor "
                "under §5.2's binomial bar are REMOVED; families "
                "recomputed on the reduced battery",
    }

    # within-family concordance (descriptive) and |A|
    conc = {}
    for fam in bt.FAMILY_ORDER:
        members = [r for r in RUNGS if FAMILY_OF[r] == fam]
        if len(members) < 2:
            continue
        pred = [predictor[r]["score"] for r in members]
        outc = [outcome["rungs"][r]["corrected_ascent"] for r in members]
        rho = spearmanr(pred, outc).statistic if len(set(pred)) > 1 and \
            len(set(outc)) > 1 else None
        conc[fam] = {"rungs": members, "predictor": pred, "outcome": outc,
                     "rho": None if rho is None or np.isnan(rho) else float(rho)}
    sec["within_family_concordance"] = conc
    sec["answer_space_descriptive"] = {
        r: {"n_distinct_answers": floors[r]["n_distinct_answers"],
            "floor": floors[r]["floor"], "predictor": predictor[r]["score"],
            "corrected_ascent": outcome["rungs"][r]["corrected_ascent"],
            # freeze F-3: 2c's `number` normalization keeps the FIRST
            # DIGIT RUN of an alphanumeric answer; on base12_digitsum /
            # base13 the criterion is therefore not exact-match
            # (196 / 276 of 500 answers truncated), on every other rung
            # it is. Pinned and re-derived; descriptive.
            "criterion_exact": floors[r]["criterion"]["exact"],
            "n_answers_truncated": floors[r]["criterion"]["n_truncated"]}
        for r in RUNGS}

    per_rung = {}
    for i, r in enumerate(RUNGS):
        per_rung[r] = {
            "family": FAMILY_OF[r], "floor": floors[r]["floor"],
            "rising": bool(y[i]), "rising_12b": bool(y12[i]),
            "corrected_ascent": float(asc[i]), "ascent_2c": float(asc2c[i]),
            "trained_acc": {s: outcome["rungs"][r]["per_size"][s]["trained_acc"]
                            for s in EVAL_SIZES},
            "untrained_acc": {s: outcome["rungs"][r]["per_size"][s]
                              ["untrained_acc"] for s in EVAL_SIZES},
            "predictor_score": float(x[i]),
            "sampled": {s: {"verified": main_cells[(r, s)]["verified"],
                            "n_draws": main_cells[(r, s)]["n_draws"],
                            "rate": main_cells[(r, s)]["rate"],
                            "cp95": main_cells[(r, s)]["cp95"],
                            "margin": predictor[r]["per_size"][s]["margin"],
                            "p": predictor[r]["per_size"][s]["p"]}
                        for s in PROBE_SIZES},
            "probe_score": float(xp[i]),
            "argmax": {s: argmax[(r, s)]["acc"] for s in PROBE_SIZES},
            "pilot_score": None if pilot_predictor is None
            else pilot_predictor[r]["score"],
        }

    return {
        "verdict": tree["verdict"], "reason": tree["reason"],
        "known_outcome_caveat": KNOWN_OUTCOME_CAVEAT,
        "licensed_sentence_if_pass": (
            "a predictor with no free parameter, fixed before sampling, "
            "separates the rungs that rise above format-guessing from "
            "those that do not, on 2c's battery, whose outcome was known"),
        "primary": {
            "statistic": "AUC of the predictor score, rising vs non-rising",
            "auc": primary["auc"],
            "block_p": primary["block"]["p"],
            "block_method": primary["block"]["method"],
            "n_perms": primary["block"]["n_perms"],
            "group_size": primary["block"]["group_size"],
            "ci": primary["bootstrap"]["ci"],
            "bootstrap_n_valid": primary["bootstrap"]["n_valid"],
            "bootstrap_n_dropped": primary["bootstrap"]["n_dropped"],
            "n_rising": primary["n_rising"], "n_flat": primary["n_flat"],
            "alpha": st.ALPHA, "auc_bar": st.AUC_BAR,
        },
        "outcome_summary": {
            "n_rising": outcome["n_rising"],
            "n_rising_12b": outcome["n_rising_12b"],
            "families_with_rising": outcome["families_with_rising"],
            "known_answer_gate": outcome["known_answer_gate"],
        },
        "gate1": {"diff_cells": gate1["diff_cells"],
                  "total_draws_compared": gate1["total_draws_compared"],
                  "cells": {f"{r}/{s}": {k: v for k, v in c.items()
                                         if k != "diffs"}
                            for (r, s), c in gate1["cells"].items()},
                  "diffs_verbatim": {f"{r}/{s}": c["diffs"]
                                     for (r, s), c in gate1["cells"].items()
                                     if c["diffs"]}},
        "power": {"declared_status": power["declared_status"],
                  "power": power["power"]},
        "twin_referent": twin,
        "secondaries": sec,
        "per_rung": per_rung,
        "n_rungs": len(RUNGS), "n_families": bt.N_FAMILIES,
    }


# ------------------------------------------------------------------ run

def run(root=EXP2D, *, write=False) -> dict:
    check_frozen_imports_2d()
    bt.check_order_against_2c()
    check_stream_map_2d()
    referents = load_referents()
    battery = bt.load_battery()
    floors = bt.floor_table(battery)
    bt.check_floors_against_doc(floors)
    verify_fn = load_verify()
    outcome = load_outcome(floors, referents=referents)
    probe = load_probe_predictor()
    twin = load_twin_record(verify_fn=verify_fn)
    # §6 precedence, executable first (freeze F-1): a gate-1 halt leaves
    # an incomplete main tier by construction; the terminal is read
    # from the halt record, not refused by the complete-tree loaders.
    halt = scan_gate1_halt(root)
    if halt["halted_cells"]:
        v = insufficient_data_record(
            halt, root=root, outcome=outcome, twin=twin,
            power=load_power_record(Path(root) / "power_2d.json",
                                    required=False))
        if write:
            out = Path(root) / "results" / "verdict.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(v, indent=1, default=str))
        return v
    power = load_power_record(Path(root) / "power_2d.json")
    pilot_cells = load_sampling_tier(root, "pilot", battery, verify_fn)
    pilot_pred = predictor_from_tier(pilot_cells, floors,
                                     n_draws_per_rung=PILOT_DRAWS_PER_RUNG)
    check_power_vs_pilot(power, pilot_pred)
    main_cells = load_sampling_tier(root, "main", battery, verify_fn)
    predictor = predictor_from_tier(main_cells, floors,
                                    n_draws_per_rung=MAIN_DRAWS_PER_RUNG)
    gate1 = load_gate1(root)
    check_gate1_vs_main(gate1, main_cells)
    argmax = load_argmax(root, battery, verify_fn)
    v = verdict_2d(outcome=outcome, predictor=predictor, probe=probe,
                   gate1=gate1, floors=floors, main_cells=main_cells,
                   argmax=argmax, twin=twin, power=power,
                   pilot_predictor=pilot_pred)
    if write:
        out = Path(root) / "results" / "verdict.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(v, indent=1, default=str))
    return v


if __name__ == "__main__":
    v = run(write="--write" in sys.argv)
    print(json.dumps({k: v[k] for k in ("verdict", "reason", "primary",
                                        "outcome_summary", "gate1")},
                     indent=1, default=str))
