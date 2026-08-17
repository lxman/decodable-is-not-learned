"""Frozen analysis for Experiment 3c (design §5, §6): staged deepening —
the rate structure of the sampled channel.

Exp 3 (tag `exp3-closed`, PARTIAL) established existence: one verified
full-string reversal in 128,000 pure T = 1.0 draws at the cell where
the joint autoregressive path is cheapest (reverse_string/1b, item 436,
seed 0, draw 6 — the length-4 stratum). This module adjudicates the
next resolution rung on the same committed streams' terms: 12 new
preregistered seeds (4–15, 64 draws each) on the four exp3 adjudicated
cells, pooled with exp3's committed seeds 0–3 to k_total = 1024 per
item. Four worlds are named in advance — DEEPENS / REPLICATES /
RELOCATES / LONE-DRAW — branching ONLY on the new draws' non-void
verified fire counts (fired cell × walls). Everything else — pooled
1024-draw rates, per-seed tallies, length strata, mean draw length,
the pooled-vs-new comparison — is computed and disclosed but read by
no branch (§5 "descriptives, never adjudicated"; no trend test, §7).

THE ONLY SCORED QUANTITY is exact-match full-string fire under 2c's
frozen `verify` (design §2.2): no mass arm, no floor, no rank
statistic. A fire is categorical and is disclosed verbatim with its
(item, seed, draw) address. Every zero ships as a Clopper–Pearson
bound; the 26^-L luck floor is printed beside every rate it contextualizes
(PROGRESS.md reading 2: 26^-4 = 2.19e-6 from code; the doc's ≈1.5e-6
is an arithmetic slip recorded by compute_power_3c, not absorbed).

TWO-TREE DISCIPLINE. The analyzer loads exp3's committed tree through
exp3's OWN frozen loader (which recomputes every tally from raw draws
and refuses disagreement) and 3c's new tree through the loaders below
(same rule, seeds 4–15), then re-asserts the standing referents
executable: the committed verdict.json fires table (sha-pinned), the
fired-cell address pin, and the twin record — 0 fires across all 8
untrained cells, 512,000 reversal-twin + 64,000 control-twin draws
(PROGRESS.md readings 4 and 6). No new twin is ever sampled; a
*_untrained directory inside 3c's tree is a hard error, not data.

GATE 1 (stream continuity, PROGRESS.md reading 1): the campaign's
first act re-derives exp3's committed seed-0 streams for the four
scored cells (64 draws/item) and ctrl_copy/1b (8 draws/item) —
132,000 draws — and byte-compares them. ANY differing draw →
INSUFFICIENT_DATA, differing draws disclosed verbatim regardless of
count. The doc's "160,000" (5×500×64) mis-multiplied ctrl_copy's
committed 8 draws/seed; the committed record is what a byte gate can
compare against, so the committed record wins (freeze to ratify the
doc correction).

LEAK-VOID (PROGRESS.md reading 3): a new fire is VOID iff its item's
answer occurs case-folded in the item's own rendered prompt. Partial
voiding is a disclosed finding and adjudication proceeds on the
survivors; ≥1 fire existing AND every fire void → INSUFFICIENT_DATA;
zero fires leaves the gate vacuous (LONE-DRAW proceeds). Reported
rates and strata count non-void fires; voids carry their own table.

BUILD-SESSION STATE. This module grows through the build session (doc
Open items 1–8) and freezes, with its fixture suite, at tag
`exp3c-preregistered` after a third session that opens adversarially.
No new sampled quantity is computed for any real cell before that tag;
the gate-1 single-cell rehearsal at the freeze (a read + regenerate +
compare) is the only sanctioned model contact.

LINEAGE. Frozen things are imported, never copied (design §11):
exp3's sampler (the generation law and the stream formula — the
namespace string stays 'exp3' DELIBERATELY so one formula governs the
whole pooled set), exp3's loaders/scoring/CP helpers, 2c's verify via
exp3's provenance-asserted resolver. The imported files are sha-pinned
below and asserted at run time: exp3 is closed, and a changed frozen
file means these are not the committed streams (frozen things stay
frozen, executable form).
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

from experiments.exp3 import analyze_3 as a3
from experiments.exp3.sampler import stream_seed

# ------------------------------------------------------------ the matrix

PROBE_SIZES = a3.PROBE_SIZES                  # ("410m", "1b")
REVERSAL_RUNGS = a3.REVERSAL_RUNGS            # ("rev_string7", "reverse_string")
POSITIVE_CONTROL = a3.POSITIVE_CONTROL        # "ctrl_copy"

# the four exp3 adjudicated cells — 3c's scored cells (§3)
SCORED_CELLS = tuple((r, s, "trained") for r in REVERSAL_RUNGS
                     for s in PROBE_SIZES)
# gate-1 byte re-derivation cells: the scored four + ctrl_copy/1b (§3)
GATE1_EXTRA_CELL = (POSITIVE_CONTROL, "1b", "trained")
GATE1_CELLS = SCORED_CELLS + (GATE1_EXTRA_CELL,)

# §1: THE fired cell and the walls, frozen by exp3's committed verdict
FIRED_CELL = ("reverse_string", "1b", "trained")
WALLED_CELLS = tuple(k for k in SCORED_CELLS if k != FIRED_CELL)

NEW_SEEDS = tuple(range(4, 16))               # §3: seeds 4–15, preregistered
DRAWS_PER_SEED_3C = 64                        # identical to exp3's reversal dps
K_NEW = len(NEW_SEEDS) * DRAWS_PER_SEED_3C    # 768 new draws per item
K_POOLED = K_NEW + a3.K_TOTAL["rev_string7"]  # 1024 pooled draws per item

CI_LEVEL = 0.95        # program reporting convention since 1c

EXP3C = Path(__file__).resolve().parent
EXPERIMENTS = EXP3C.parent
EXP3 = a3.EXP3

RESULTS = EXP3C / "results"
SAMPLING_ROOT = RESULTS / "sampling"
GATE1_ROOT = RESULTS / "gate1"
STREAM_MAP_3C_PATH = EXP3C / "stream_map_3c.json"

# ----------------------------------------------------- frozen-file pins
#
# Design §11: frozen things stay frozen, executable form. These are the
# exp3 files 3c's meaning depends on: the generation law, the loader
# semantics and constants, the committed stream map (continuity), and
# the committed verdict record (the fires-table referent). exp3 is
# CLOSED — if any byte of these moves, the pooled set is no longer
# exp3's, and nothing here is interpretable.

FROZEN_IMPORT_SHA256 = {
    EXP3 / "sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
    EXP3 / "analyze_3.py":
        "aa0cb2374fbdffde2f9eaae26cee1ce51f9f42c0b32fd89f4f8754c983a92274",
    EXP3 / "stream_map.json":
        "ea299282342de59d8267682afbf51931521c742a7950215d7acfdc40584fe7a9",
    EXP3 / "results" / "verdict.json":
        "0bce2f91460dd20dc047127da24f6c650aebbe48fdd8f46f5d24da22fa3489ff",
}

EXP3_VERDICT_PATH = EXP3 / "results" / "verdict.json"

# §4: the exp3 fire, transcribed from the committed record (VERDICT.txt
# / verdict.json, tag exp3-closed) — context and referent, never
# re-adjudicated. The address is re-extracted from the committed raw
# draws at load and must equal this pin (PROGRESS.md reading 6).
EXP3_FIRE_ADDRESSES_PIN = {
    "rev_string7/410m/trained": [],
    "rev_string7/1b/trained": [],
    "reverse_string/410m/trained": [],
    "reverse_string/1b/trained": [{"item": 436, "seed": 0, "draw": 6}],
}
EXP3_FIRE_ANSWER_LENGTHS_PIN = {
    "rev_string7/410m/trained": [],
    "rev_string7/1b/trained": [],
    "reverse_string/410m/trained": [],
    "reverse_string/1b/trained": [4],
}

# PROGRESS.md reading 4: the standing twin contamination referent —
# exp3's 8 untrained cells, re-asserted at every load.
TWIN_CELLS = tuple((r, s, "untrained") for r in a3.RUNGS
                   for s in PROBE_SIZES)
TWIN_REVERSAL_DRAWS = 512_000     # 4 reversal twin cells × 128,000
TWIN_CONTROL_DRAWS = 64_000       # 4 control twin cells × 16,000


def check_frozen_imports() -> None:
    """Hard-error unless every imported frozen file is byte-identical
    to its pin. Run before anything reads the exp3 tree."""
    for path, want in FROZEN_IMPORT_SHA256.items():
        got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if got != want:
            raise ValueError(
                f"frozen file {path} has sha256 {got}, expected {want} — "
                f"exp3 is closed and its files are 3c's referents; a "
                f"changed byte means these are not the committed streams")


def _key(k) -> str:
    return "/".join(k)


def luck_floor(length: int) -> float:
    """§8: the per-draw rate at which blind uniform letter emission
    exact-matches an L-letter answer — 26^-L, printed beside every
    rate it contextualizes. 26^-4 = 2.19e-6 (PROGRESS.md reading 2)."""
    if not (isinstance(length, int) and length > 0):
        raise ValueError(f"no luck floor for answer length {length!r}")
    return 26.0 ** (-length)


# ------------------------------------------------------- stream map 3c

def dump_stream_map_3c(path=STREAM_MAP_3C_PATH) -> dict:
    """The committed seed-extension (§5): the 5 gate/scored cells × ALL
    16 seeds (0–15) under exp3's exact formula and namespace. Seeds
    0–3 duplicate exp3's committed map entries on purpose — the
    continuity check below asserts the overlap byte-equal, making
    'one formula governs the whole pooled set' executable."""
    cells = {}
    for (rung, size, mode) in GATE1_CELLS:
        for s in range(16):
            cells[f"{rung}/{size}/{mode}/s{s}"] = {
                "item0": stream_seed(rung, size, mode, s, 0),
                "item499": stream_seed(rung, size, mode, s, 499),
            }
    out = {
        "formula": "int.from_bytes(sha256('exp3|{rung}|{size}|{mode}|"
                   "s{seed}|i{item}').digest()[:8], 'big') & ((1<<63)-1)",
        "namespace_note": "the namespace string stays 'exp3' DELIBERATELY "
                          "(design §5): seeds 4-15 extend the same "
                          "committed stream families exp3 drew 0-3 from",
        "per_item_substreams": True,
        "chunk_rows": 16,
        "draw_order": "seeds ascending; within a seed, chunks in index "
                      "order; within a chunk, rows in row order; one "
                      "multinomial call per step over all rows",
        "exp3_seeds": list(a3.SEEDS),
        "new_seeds": list(NEW_SEEDS),
        "draws_per_seed": DRAWS_PER_SEED_3C,
        "k_new": K_NEW,
        "k_pooled": K_POOLED,
        "cells": cells,
    }
    Path(path).write_text(json.dumps(out, indent=1))
    return out


def check_stream_map(path=STREAM_MAP_3C_PATH,
                     exp3_map_path=EXP3 / "stream_map.json") -> dict:
    """Hard-error unless the committed 3c map is exactly the formula's
    output AND its seed-0–3 entries equal exp3's committed map for
    every gate/scored cell (PROGRESS.md reading 7)."""
    m = json.loads(Path(path).read_text())
    e = json.loads(Path(exp3_map_path).read_text())
    if m.get("formula") != e.get("formula"):
        raise ValueError(
            f"stream_map_3c formula {m.get('formula')!r} differs from "
            f"exp3's committed formula — not one law over the pooled set")
    want_keys = {f"{r}/{s}/{mo}/s{sd}" for (r, s, mo) in GATE1_CELLS
                 for sd in range(16)}
    if set(m.get("cells", {})) != want_keys:
        raise ValueError(
            f"stream_map_3c covers {len(m.get('cells', {}))} entries, "
            f"not the 5 gate/scored cells × 16 seeds")
    for (rung, size, mode) in GATE1_CELLS:
        for sd in range(16):
            k = f"{rung}/{size}/{mode}/s{sd}"
            want = {"item0": stream_seed(rung, size, mode, sd, 0),
                    "item499": stream_seed(rung, size, mode, sd, 499)}
            if m["cells"][k] != want:
                raise ValueError(
                    f"stream_map_3c entry {k} = {m['cells'][k]} disagrees "
                    f"with the frozen formula {want} — the map is not the "
                    f"formula's output")
            if sd in a3.SEEDS and m["cells"][k] != e["cells"][k]:
                raise ValueError(
                    f"stream_map_3c entry {k} disagrees with exp3's "
                    f"committed map — pooling continuity broken")
    return m


# ------------------------------------------------- raw-draw ingestion
#
# 3c's own loaders (§11; design: "analyze_3c with its own loaders").
# Same discipline as exp3's: duplicate-refusing, coverage-checking,
# stream-complete, hard-erroring on anything malformed (3a's class,
# refused at load).

def _read_rows(path, n_items, seeds, dps) -> list:
    rows, seen = [], set()
    want = {str(s) for s in seeds}
    with gzip.open(Path(path), "rt") as f:
        for line in f:
            row = json.loads(line)
            i = row.get("item")
            if i in seen:
                raise ValueError(f"duplicate item {i} in {path}")
            seen.add(i)
            draws = row.get("draws")
            if not isinstance(draws, dict) or set(draws) != want:
                raise ValueError(
                    f"{path} item {i}: seed streams "
                    f"{sorted(draws) if isinstance(draws, dict) else draws!r} "
                    f"are not the preregistered seeds {sorted(seeds)}")
            for s in seeds:
                stream = draws[str(s)]
                if not isinstance(stream, list) or len(stream) != dps or \
                        not all(isinstance(d, str) for d in stream):
                    raise ValueError(
                        f"{path} item {i} seed {s}: stream of "
                        f"{len(stream) if isinstance(stream, list) else stream!r} "
                        f"draws against draws_per_seed {dps}")
            rows.append(row)
    if len(rows) != n_items or seen != set(range(n_items)):
        raise ValueError(
            f"{path}: {len(rows)} item rows covering {len(seen)} distinct "
            f"items against n_items {n_items}")
    return rows


def tally_with_addresses(rows, answers, labels, seeds, *, answer_type,
                         verify_fn) -> dict:
    """Per-seed tallies recomputed from raw draws (2c's verify, 3b's
    first_char — the same frozen functions the runner's convenience
    copies used), plus the address and verbatim text of every verified
    full-string fire, and the total draw length for the mean-length
    descriptive."""
    per_seed = {str(s): {"full_string": 0, "first_char": 0, "n_draws": 0}
                for s in seeds}
    per_item_full = [0] * len(answers)
    addresses = []
    total_len = 0
    for row in rows:
        i = row["item"]
        for s in seeds:
            k = str(s)
            for d_idx, d in enumerate(row["draws"][k]):
                per_seed[k]["n_draws"] += 1
                total_len += len(d)
                if verify_fn(d, answers[i], answer_type):
                    per_seed[k]["full_string"] += 1
                    per_item_full[i] += 1
                    addresses.append({"item": i, "seed": int(s),
                                      "draw": d_idx, "text": d})
                if a3.score_first_char(d, labels[i]):
                    per_seed[k]["first_char"] += 1
    return {"per_seed": per_seed, "per_item_full_string": per_item_full,
            "addresses": addresses, "total_draw_len": total_len}


def _refuse_strays_3c(base, want: dict) -> None:
    """`want` maps directory name → set of allowed file names. Any
    other entry under `base` — including a *_untrained directory,
    which would mean new twin sampling this design forbids — is a
    half-copied or wrong-tree directory and is refused, not skipped."""
    base = Path(base)
    if not base.is_dir():
        return
    for d in sorted(base.iterdir()):
        if d.name.startswith("."):
            continue
        if d.is_file() or d.name not in want:
            raise ValueError(
                f"unexpected entry {d} inside a canonical 3c battery "
                f"directory — this tree is not the preregistered battery")
        for f in sorted(d.iterdir()):
            if f.name.startswith("."):
                continue
            if f.name not in want[d.name]:
                raise ValueError(
                    f"unexpected file {f} inside a canonical 3c battery "
                    f"subdirectory — this tree is not the preregistered "
                    f"battery")


def _check_new_provenance(rec, p, rung, size) -> None:
    if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
            (rung, size, "trained"):
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
            f"policy — every 3c sampling cell is float32")
    if rec.get("untrained_seed") is not None:
        raise ValueError(
            f"{p}: untrained_seed {rec.get('untrained_seed')!r} on a "
            f"trained cell — 3c samples no twins")
    if rec.get("seeds") != list(NEW_SEEDS):
        raise ValueError(
            f"{p}: seeds {rec.get('seeds')!r} are not the preregistered "
            f"new seeds {list(NEW_SEEDS)} (design §6.2)")
    if rec.get("draws_per_seed") != DRAWS_PER_SEED_3C:
        raise ValueError(
            f"{p}: draws_per_seed {rec.get('draws_per_seed')!r} against "
            f"the preregistered {DRAWS_PER_SEED_3C} (design §6.2)")
    if rec.get("k_total") != K_NEW:
        raise ValueError(
            f"{p}: k_total {rec.get('k_total')!r} against "
            f"{len(NEW_SEEDS)} seeds × {DRAWS_PER_SEED_3C} draws "
            f"= {K_NEW}")


def load_new_cells(root=EXP3C, verify_fn=None) -> dict:
    """The 4 scored cells' NEW draws (§3), raw streams beside their
    records. Stored per-seed tallies are convenience copies: the
    analyzer RECOMPUTES them from the raw draws and refuses any
    disagreement (exp3's rule, both trees)."""
    if verify_fn is None:
        verify_fn = a3.load_verify()
    base = Path(root) / "results" / "sampling"
    want_names = {f"{r}.json" for (r, _s, _m) in SCORED_CELLS} \
        | {f"{r}.draws.jsonl.gz" for (r, _s, _m) in SCORED_CELLS}
    _refuse_strays_3c(base, {f"{s}_trained": want_names
                             for s in PROBE_SIZES})
    out = {}
    for (rung, size, mode) in SCORED_CELLS:
        d = base / f"{size}_{mode}"
        p = d / f"{rung}.json"
        if not p.is_file():
            raise FileNotFoundError(
                f"no 3c sampling cell for {rung}/{size}/{mode} at {p}")
        rec = json.loads(p.read_text())
        _check_new_provenance(rec, p, rung, size)
        dpath = d / f"{rung}.draws.jsonl.gz"
        if not dpath.is_file():
            raise FileNotFoundError(
                f"no raw draws file for {rung}/{size}/{mode} at {dpath}")
        n = rec["n_items"]
        rows = _read_rows(dpath, n, NEW_SEEDS, DRAWS_PER_SEED_3C)
        answers = [str(x) for x in rec["answers"]]
        labels = [str(x) for x in rec["probe_labels"]]
        t = tally_with_addresses(rows, answers, labels, NEW_SEEDS,
                                 answer_type=rec.get("answer_type"),
                                 verify_fn=verify_fn)
        stored = rec.get("per_seed_tallies")
        normalized = None
        if isinstance(stored, dict):
            try:
                normalized = {k: {f: int(v[f]) for f in
                                  ("full_string", "first_char", "n_draws")}
                              for k, v in stored.items()}
            except (KeyError, TypeError, ValueError):
                normalized = None
        if normalized != t["per_seed"]:
            raise ValueError(
                f"{p}: stored per-seed tallies disagree with the "
                f"recompute from the raw draws — stored {stored!r}, "
                f"recomputed {t['per_seed']!r}; this battery's runner "
                f"and analyzer do not agree on what was drawn")
        full_total = sum(v["full_string"] for v in t["per_seed"].values())
        n_draws = sum(v["n_draws"] for v in t["per_seed"].values())
        out[(rung, size, mode)] = {
            "rung": rung, "size": size, "mode": mode, "n": n,
            "answers": answers, "probe_labels": labels,
            "answer_type": rec.get("answer_type"),
            "items_sha256": rec["items_sha256"], "dtype": rec["dtype"],
            "seeds": list(NEW_SEEDS), "draws_per_seed": DRAWS_PER_SEED_3C,
            "k_total": rec["k_total"],
            "recomputed": {
                "per_seed": t["per_seed"],
                "full_string_total": int(full_total),
                "first_char_total": int(sum(v["first_char"]
                                            for v in
                                            t["per_seed"].values())),
                "n_draws_total": int(n_draws),
                "per_item_full_string": t["per_item_full_string"],
                "fired": bool(full_total > 0),
            },
            "addresses": t["addresses"],
            "mean_draw_len": t["total_draw_len"] / n_draws,
        }
    return out


# ------------------------------------------------- gate-1 records

def load_gate1_records(root=EXP3C) -> dict:
    """The 5 byte re-derivation comparison records (§6.1). The raw
    re-derived draws are discarded by design; what persists — and what
    this loader refuses to accept valueless — is the comparison: how
    many draws were compared (must equal the committed stream size:
    64/item on scored cells, 8/item on ctrl_copy — PROGRESS.md
    reading 1), how many differed, and every differing draw verbatim
    with its (item, seed, draw) address."""
    base = Path(root) / "results" / "gate1"
    want = {"410m_trained": {f"{r}.json" for (r, s, _m) in GATE1_CELLS
                             if s == "410m"},
            "1b_trained": {f"{r}.json" for (r, s, _m) in GATE1_CELLS
                           if s == "1b"}}
    _refuse_strays_3c(base, want)
    out = {}
    for (rung, size, mode) in GATE1_CELLS:
        p = base / f"{size}_{mode}" / f"{rung}.json"
        if not p.is_file():
            raise FileNotFoundError(
                f"no gate-1 comparison record for {rung}/{size}/{mode} "
                f"at {p}")
        rec = json.loads(p.read_text())
        if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
                (rung, size, mode):
            raise ValueError(
                f"{p} contents ({rec.get('rung')}/{rec.get('size')}/"
                f"{rec.get('mode')}) disagree with its path")
        if rec.get("dtype") != "float32":
            raise ValueError(f"{p}: dtype {rec.get('dtype')!r} is not the "
                             f"campaign's float32")
        if rec.get("seeds_rederived") != [0]:
            raise ValueError(
                f"{p}: seeds_rederived {rec.get('seeds_rederived')!r} — "
                f"gate 1 re-derives exp3's committed seed 0 only")
        n = rec.get("n_items")
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"{p}: n_items {n!r} is not a count")
        dps = rec.get("draws_per_seed")
        if dps != a3.DRAWS_PER_SEED[rung]:
            raise ValueError(
                f"{p}: draws_per_seed {dps!r} against exp3's committed "
                f"{a3.DRAWS_PER_SEED[rung]} for {rung} — a stream of the "
                f"wrong depth is not byte-comparable (PROGRESS.md "
                f"reading 1)")
        compared = rec.get("draws_compared")
        if compared != n * dps or compared <= 0:
            raise ValueError(
                f"{p}: draws_compared {compared!r} against n_items {n} × "
                f"draws_per_seed {dps} — a gate-1 record that compared "
                f"nothing has no value (3a's class, refused)")
        sha = rec.get("committed_draws_sha256")
        if not isinstance(sha, str) or not sha:
            raise ValueError(
                f"{p} carries no committed_draws_sha256 — the record "
                f"does not say what it compared against")
        isha = rec.get("items_sha256")
        if not isinstance(isha, str) or not isha:
            raise ValueError(f"{p} carries no items_sha256")
        diffs = rec.get("diffs")
        if not isinstance(diffs, list):
            raise ValueError(f"{p}: diffs {diffs!r} is not a list")
        for j, dd in enumerate(diffs):
            if not (isinstance(dd, dict)
                    and isinstance(dd.get("item"), int)
                    and dd.get("seed") == 0
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
        out[(rung, size, mode)] = {
            "rung": rung, "size": size, "mode": mode, "n": n,
            "draws_per_seed": dps, "draws_compared": compared,
            "n_diffs": int(rec["n_diffs"]), "diffs": diffs,
            "committed_draws_sha256": sha, "items_sha256": isha,
            "model_sha": rec.get("model_sha"),
        }
    return out


# ------------------------------------------------- exp3-side referents

def load_exp3_referent(path=EXP3_VERDICT_PATH) -> dict:
    """The standing exp3 referent expectations, from the sha-pinned
    committed verdict record plus the §4 address pins: the 16-cell
    fires table, the fired-cell addresses, and the fired answers'
    lengths. Everything the two-tree load must reproduce exactly
    (PROGRESS.md reading 6)."""
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    want = FROZEN_IMPORT_SHA256[EXP3_VERDICT_PATH]
    if got != want:
        raise ValueError(
            f"exp3 verdict record {path} has sha256 {got}, expected "
            f"{want} — the committed fires-table referent changed "
            f"after the pin")
    rec = json.loads(raw)
    fires = rec.get("fires")
    if not isinstance(fires, dict):
        raise ValueError(f"{path} carries no fires table")
    table = {}
    for key in a3.SAMPLING_CELLS:
        k = _key(key)
        e = fires.get(k)
        if not (isinstance(e, dict) and isinstance(
                e.get("full_string_total"), int)
                and isinstance(e.get("n_draws"), int)):
            raise ValueError(
                f"{path} fires table has no usable entry for {k} — the "
                f"referent has no value there (3a's class, refused)")
        table[k] = {"full_string_total": e["full_string_total"],
                    "n_draws": e["n_draws"]}
    return {"fires": table,
            "fire_addresses": EXP3_FIRE_ADDRESSES_PIN,
            "fire_answer_lengths": EXP3_FIRE_ANSWER_LENGTHS_PIN}


def extract_fire_addresses(root, exp3_cells, verify_fn=None) -> dict:
    """Re-extract every verified fire's (item, seed, draw) address from
    the exp3 tree's committed raw draws for the four scored cells —
    the second, address-recording pass over the same bytes exp3's own
    loader already recomputed. The two passes must agree on the count;
    disagreement is a loader defect, not data."""
    if verify_fn is None:
        verify_fn = a3.load_verify()
    out = {}
    for key in SCORED_CELLS:
        rung, size, mode = key
        c = exp3_cells[key]
        dpath = (Path(root) / "results" / "sampling" / f"{size}_{mode}"
                 / f"{rung}.draws.jsonl.gz")
        rows = _read_rows(dpath, c["n"], c["seeds"], c["draws_per_seed"])
        t = tally_with_addresses(rows, c["answers"], c["probe_labels"],
                                 c["seeds"],
                                 answer_type=c["answer_type"],
                                 verify_fn=verify_fn)
        got = sum(v["full_string"] for v in t["per_seed"].values())
        if got != c["recomputed"]["full_string_total"]:
            raise ValueError(
                f"address extraction found {got} fires in {_key(key)} "
                f"but the loader recomputed "
                f"{c['recomputed']['full_string_total']} — two passes "
                f"over the same committed bytes disagree")
        out[_key(key)] = [{"item": ad["item"], "seed": ad["seed"],
                           "draw": ad["draw"]} for ad in t["addresses"]]
    return out


# --------------------------------------------------------- prompts

def load_prompts(rungs=REVERSAL_RUNGS) -> dict:
    """The rendered prompts of the scored rungs' committed items, for
    the leak-void check (PROGRESS.md reading 3): 2c's render_prompt on
    the committed item file, first two shots — the runner's exact
    construction (pinned against exp3's own loader in the fixtures)."""
    for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
    import harness
    got = Path(harness.__file__).resolve()
    if (EXPERIMENTS / "exp2c").resolve() not in got.parents:
        raise ImportError(
            f"harness resolved to {got}, which is not under the exp2c "
            f"tree — these would not be the committed prompts")
    out = {}
    for rung in rungs:
        p = harness.ITEMS_DIR / f"{rung}.json"
        if not p.is_file():
            p = EXPERIMENTS / "exp2b" / "battery" / "items" / f"{rung}.json"
        cap = json.loads(p.read_text())
        shots = [tuple(s) for s in cap["shots"]][:2]
        out[rung] = [harness.render_prompt(it["question"], shots)
                     for it in cap["eval_items"]]
    return out


# ----------------------------------------------------------- CI helpers

def rate_entry(k: int, n: int) -> dict:
    """One count as the program reports it: exact rate with a two-sided
    .95 CP interval when nonzero, a one-sided .95 CP upper bound when
    zero (every zero a bound, standing rule since 1c)."""
    if n <= 0:
        raise ValueError(f"no draws to rate a count of {k} against")
    if not 0 <= k <= n:
        raise ValueError(f"count {k} outside [0, {n}]")
    e = {"count": int(k), "n_draws": int(n), "rate": k / n}
    if k == 0:
        e["cp95_upper"] = a3.cp_upper(0, n, level=CI_LEVEL)
    else:
        lo, hi = a3.clopper_pearson(k, n, level=CI_LEVEL)
        e["ci95"] = [lo, hi]
    return e


def strata_of(answers) -> dict:
    """Item indices by answer length — the committed batteries span
    4–6 (reverse_string) and 7 (rev_string7); computed, never assumed."""
    out: dict[int, list] = {}
    for i, ans in enumerate(answers):
        out.setdefault(len(str(ans)), []).append(i)
    return out


# ----------------------------------------------------------- verdict tree

WORLDS_3C = ("DEEPENS", "REPLICATES", "RELOCATES", "LONE-DRAW")


def _shape_check_3c(new_cells, gate1_records, exp3_cells, *,
                    exp3_referent, exp3_fire_addresses, sha_refs) -> None:
    """The battery must be exactly the preregistered 4 + 5 + 16 cells,
    every new cell pinned to its rung's single §4 item file and to the
    exp3 tree's own answers/labels, and the exp3 tree equal to its
    committed referents — fires table, fired addresses, fired answer
    lengths, and the twin record. Anything else is a malformed battery
    or a moved referent: a hard error, never a verdict."""
    if set(new_cells) != set(SCORED_CELLS):
        raise ValueError(
            f"battery is not the preregistered 4 scored cells: missing "
            f"{sorted(set(SCORED_CELLS) - set(new_cells))}, extra "
            f"{sorted(set(new_cells) - set(SCORED_CELLS))}")
    if set(gate1_records) != set(GATE1_CELLS):
        raise ValueError(
            f"battery is not the preregistered 5 gate-1 cells: missing "
            f"{sorted(set(GATE1_CELLS) - set(gate1_records))}, extra "
            f"{sorted(set(gate1_records) - set(GATE1_CELLS))}")
    if set(exp3_cells) != set(a3.SAMPLING_CELLS):
        raise ValueError(
            f"the exp3 tree is not the committed 16 sampling cells: "
            f"missing "
            f"{sorted(set(a3.SAMPLING_CELLS) - set(exp3_cells))}, extra "
            f"{sorted(set(exp3_cells) - set(a3.SAMPLING_CELLS))}")

    # exp3 recompute vs the committed fires table (reading 6a)
    for key in sorted(a3.SAMPLING_CELLS):
        rc = exp3_cells[key]["recomputed"]
        ref = exp3_referent["fires"][_key(key)]
        got = {"full_string_total": rc["full_string_total"],
               "n_draws": rc["n_draws_total"]}
        if got != ref:
            raise ValueError(
                f"exp3 cell {_key(key)} recomputes to {got} against the "
                f"committed verdict record's {ref} — the standing "
                f"referent moved; nothing pooled is interpretable")

    # the twin record, independently (reading 4)
    for key in TWIN_CELLS:
        rc = exp3_cells[key]["recomputed"]
        if rc["full_string_total"] != 0:
            raise ValueError(
                f"exp3 twin cell {_key(key)} recomputes to "
                f"{rc['full_string_total']} fires — the standing "
                f"contamination referent (0 fires across all 8 twin "
                f"cells) no longer holds")
    twin_rev = sum(exp3_cells[(r, s, "untrained")]["recomputed"]
                   ["n_draws_total"] for r in REVERSAL_RUNGS
                   for s in PROBE_SIZES)
    twin_ctrl = sum(exp3_cells[(r, s, "untrained")]["recomputed"]
                    ["n_draws_total"]
                    for r in (a3.POSITIVE_CONTROL, a3.MATCHED_CONTROL)
                    for s in PROBE_SIZES)
    if (twin_rev, twin_ctrl) != (TWIN_REVERSAL_DRAWS, TWIN_CONTROL_DRAWS):
        raise ValueError(
            f"exp3 twin draw counts ({twin_rev} reversal, {twin_ctrl} "
            f"control) against the committed ({TWIN_REVERSAL_DRAWS}, "
            f"{TWIN_CONTROL_DRAWS})")

    # fired-cell addresses and answer lengths (readings 6b, 6c)
    if exp3_fire_addresses != exp3_referent["fire_addresses"]:
        raise ValueError(
            f"exp3 fire addresses re-extracted as {exp3_fire_addresses} "
            f"against the pinned {exp3_referent['fire_addresses']} — "
            f"the committed fire is not where the referent says")
    for k, addrs in exp3_fire_addresses.items():
        rung, size, mode = k.split("/")
        lengths = [len(str(exp3_cells[(rung, size, mode)]["answers"]
                           [ad["item"]])) for ad in addrs]
        if lengths != exp3_referent["fire_answer_lengths"][k]:
            raise ValueError(
                f"exp3 fired answers at {k} have lengths {lengths} "
                f"against the pinned "
                f"{exp3_referent['fire_answer_lengths'][k]}")

    # new cells against the exp3 tree and the §4 pins
    for key in sorted(SCORED_CELLS):
        c, e = new_cells[key], exp3_cells[key]
        rung = key[0]
        if c["items_sha256"] != sha_refs[rung]:
            raise ValueError(
                f"new cell {_key(key)} carries items_sha256 "
                f"{c['items_sha256']!r} against the rung's single §4 "
                f"pin {sha_refs[rung]!r}")
        if c["items_sha256"] != e["items_sha256"]:
            raise ValueError(
                f"new cell {_key(key)} items_sha256 disagrees with the "
                f"exp3 tree's — the pooled set would span two item "
                f"files")
        if c["n"] != e["n"]:
            raise ValueError(
                f"new cell {_key(key)} has n {c['n']} against the exp3 "
                f"tree's {e['n']}")
        for field in ("answers", "probe_labels", "answer_type"):
            if c[field] != e[field]:
                raise ValueError(
                    f"new cell {_key(key)}: {field} disagree with the "
                    f"exp3 tree's — not the same experiment's items")
    for key in sorted(GATE1_CELLS):
        g = gate1_records[key]
        rung = key[0]
        if g["items_sha256"] != sha_refs[rung]:
            raise ValueError(
                f"gate-1 record {_key(key)} carries items_sha256 "
                f"{g['items_sha256']!r} against the rung's single §4 "
                f"pin {sha_refs[rung]!r}")
        if g["n"] != exp3_cells[key]["n"]:
            raise ValueError(
                f"gate-1 record {_key(key)} has n {g['n']} against the "
                f"exp3 tree's {exp3_cells[key]['n']}")


def verdict_3c(new_cells, gate1_records, exp3_cells, *, exp3_referent,
               exp3_fire_addresses, prompts, sha_refs) -> dict:
    """Design §6, adjudicated in precedence order, with everything
    computed and disclosed BEFORE the first branch so no gate can hide
    another's evidence. Provenance failures (§6.2) are hard errors
    raised by the loaders and the shape check, never verdicts."""
    _shape_check_3c(new_cells, gate1_records, exp3_cells,
                    exp3_referent=exp3_referent,
                    exp3_fire_addresses=exp3_fire_addresses,
                    sha_refs=sha_refs)

    # ---- gate 1: stream continuity (computed first, branched first)
    gate1 = {}
    for key in sorted(GATE1_CELLS):
        g = gate1_records[key]
        gate1[_key(key)] = {"draws_compared": g["draws_compared"],
                            "n_diffs": g["n_diffs"], "diffs": g["diffs"],
                            "committed_draws_sha256":
                                g["committed_draws_sha256"]}
    gate1_total_compared = sum(v["draws_compared"] for v in gate1.values())
    gate1_diff_cells = {k: v["n_diffs"] for k, v in gate1.items()
                        if v["n_diffs"] > 0}

    # ---- the new fires, leak-void applied per fire (reading 3)
    fires = {}
    all_new_fires = 0
    all_void = []
    for key in sorted(SCORED_CELLS):
        rung, size, mode = key
        c = new_cells[key]
        rc = c["recomputed"]
        addresses = []
        for ad in c["addresses"]:
            i = ad["item"]
            answer = c["answers"][i]
            void = str(answer).casefold() in prompts[rung][i].casefold()
            entry = {**ad, "answer": answer,
                     "answer_len": len(str(answer)), "void": bool(void)}
            if void:
                entry["void_reason"] = (
                    "the item's answer occurs in its own rendered "
                    "prompt — the leak class the items rule out by "
                    "construction (design §6.3); this fire argues "
                    "nothing")
                all_void.append({**entry, "cell": _key(key)})
            addresses.append(entry)
        non_void = [ad for ad in addresses if not ad["void"]]
        all_new_fires += len(addresses)
        entry = {
            "new": rate_entry(len(non_void), rc["n_draws_total"]),
            "raw_fire_count_pre_void": len(addresses),
            "addresses": addresses,
            "per_seed_full_string": {s: v["full_string"]
                                     for s, v in rc["per_seed"].items()},
            "fired": bool(non_void),
        }
        fires[_key(key)] = entry

    def non_void_count(key) -> int:
        return fires[_key(key)]["new"]["count"]

    # ---- pooled 1024-draw table (§5; reporting, never adjudicated)
    pooled = {}
    for key in sorted(SCORED_CELLS):
        e3 = exp3_cells[key]["recomputed"]
        k_pool = e3["full_string_total"] + non_void_count(key)
        n_pool = e3["n_draws_total"] + \
            new_cells[key]["recomputed"]["n_draws_total"]
        pooled[_key(key)] = {
            **rate_entry(k_pool, n_pool),
            "exp3_count": e3["full_string_total"],
            "new_count": non_void_count(key),
        }

    # ---- length strata (§5 descriptives: exact CIs, NO trend test —
    # §7's honest power numbers forbid one)
    strata = {}
    for key in sorted(SCORED_CELLS):
        c = new_cells[key]
        e3 = exp3_cells[key]
        by_len = strata_of(c["answers"])
        new_by_item = c["recomputed"]["per_item_full_string"]
        void_items = {ad["item"] for ad in fires[_key(key)]["addresses"]
                      if ad["void"]}
        exp3_by_item = e3["recomputed"]["per_item_full_string"]
        cell = {}
        for length in sorted(by_len):
            idx = by_len[length]
            new_fires = sum(new_by_item[i] for i in idx
                            if i not in void_items)
            e3_fires = sum(exp3_by_item[i] for i in idx)
            n_new = len(idx) * K_NEW
            n_pool = len(idx) * K_POOLED
            cell[str(length)] = {
                "n_items": len(idx),
                "new": rate_entry(new_fires, n_new),
                "pooled": rate_entry(e3_fires + new_fires, n_pool),
                "luck_floor": luck_floor(length),
            }
        strata[_key(key)] = cell

    # ---- descriptives (§5: computed, disclosed, adjudicating nothing)
    e3_fired = exp3_cells[FIRED_CELL]["recomputed"]
    descriptives = {
        "mean_draw_len_new": {_key(k): new_cells[k]["mean_draw_len"]
                              for k in sorted(SCORED_CELLS)},
        "per_seed_pooled_view": {
            _key(k): {**{s: v["full_string"] for s, v in
                         exp3_cells[k]["recomputed"]["per_seed"].items()},
                      **{s: v["full_string"] for s, v in
                         new_cells[k]["recomputed"]["per_seed"].items()}}
            for k in sorted(SCORED_CELLS)},
        "fired_cell_comparison": {
            "cell": _key(FIRED_CELL),
            "exp3": rate_entry(e3_fired["full_string_total"],
                               e3_fired["n_draws_total"]),
            "new": fires[_key(FIRED_CELL)]["new"],
            "pooled": pooled[_key(FIRED_CELL)],
            "luck_floor_L4": luck_floor(4),
        },
    }

    # ---- blind region (§7, computed live from the frozen CP form)
    n_new_cell = new_cells[FIRED_CELL]["recomputed"]["n_draws_total"]
    n_pool_cell = n_new_cell + \
        exp3_cells[FIRED_CELL]["recomputed"]["n_draws_total"]
    blind = {
        "new_per_cell_zero_bound": a3.cp_upper(0, n_new_cell),
        "pooled_per_cell_zero_bound": a3.cp_upper(0, n_pool_cell),
        "statement": (
            f"a persistent zero tightens a walled cell's pooled bound "
            f"to ≤ {a3.cp_upper(0, n_pool_cell):.2e} (from exp3's "
            f"≤ {a3.cp_upper(0, exp3_cells[FIRED_CELL]['recomputed']['n_draws_total']):.2e}) "
            f"— the design is blind below that per-draw rate, and "
            f"silence is weak evidence bounded by budget (the "
            f"forward-note's asymmetry rule)"),
    }

    twin_citation = {
        "cells": len(TWIN_CELLS),
        "fires": 0,
        "reversal_twin_draws": TWIN_REVERSAL_DRAWS,
        "control_twin_draws": TWIN_CONTROL_DRAWS,
        "statement": (
            "no new twin was sampled (design §3): exp3's committed twin "
            "record — 0 fires across all 8 untrained cells, 512,000 "
            "reversal-twin draws + 64,000 control-twin draws — is the "
            "standing contamination referent, re-asserted from raw "
            "draws at this load"),
    }

    out = {
        "worlds": list(WORLDS_3C),
        "fired_cell": _key(FIRED_CELL),
        "walled_cells": [_key(k) for k in WALLED_CELLS],
        "gate1": gate1,
        "gate1_total_draws_compared": gate1_total_compared,
        "fires": fires,
        "pooled": pooled,
        "strata": strata,
        "descriptives": descriptives,
        "blind_region": blind,
        "twin_record": twin_citation,
        "leak_voids": all_void,
        "luck_floor_by_length": {str(L): luck_floor(L)
                                 for L in (4, 5, 6, 7)},
    }

    # 1. stream continuity (§6.1): zero tolerance, diffs already
    # disclosed above whatever happens next
    if gate1_diff_cells:
        detail = "; ".join(f"{k} ({n} differing draws)"
                           for k, n in sorted(gate1_diff_cells.items()))
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": (
                    "gate 1 failed — the seed-0 re-derivation differs "
                    f"from exp3's committed bytes at: {detail}. The "
                    "streams are deterministic on this stack (exp3's "
                    "committed determinism reference); a single "
                    "differing byte means the generation law changed, "
                    "and no new draw is interpretable. Differing draws "
                    "disclosed verbatim in the gate1 table.")}

    # 3. contamination/leak (§6.3): every observed fire void → the
    # evidence base was manufactured by leaking items, not sampling
    if all_new_fires > 0 and len(all_void) == all_new_fires:
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": (
                    f"every one of the {all_new_fires} new fired draws "
                    f"is void — each fire's answer occurs in its own "
                    f"prompt (evidence in leak_voids, verbatim). The "
                    f"leak class the items rule out by construction is "
                    f"live, so no fire argues elicitation and no "
                    f"silence argues a wall (PROGRESS.md reading 3).")}

    # 4. adjudicate (§6.4) on the new draws' non-void fire counts
    fired_fires = non_void_count(FIRED_CELL)
    wall_fires = {_key(k): non_void_count(k) for k in WALLED_CELLS}
    fired_again = fired_fires > 0
    any_wall = any(v > 0 for v in wall_fires.values())
    out = {**out, "adjudication": {
        "fired_cell_new_fires": fired_fires,
        "wall_new_fires": wall_fires,
        "fired_again": fired_again, "any_wall_fired": any_wall}}

    pooled_fired = pooled[_key(FIRED_CELL)]

    def _wall_txt(k) -> str:
        e = fires[k]["new"]
        if e["count"]:
            return f"{k} fires {e['count']}/{e['n_draws']}"
        return f"{k} 0/{e['n_draws']} (CP95 ≤ {e['cp95_upper']:.2e})"

    walls_txt = "; ".join(_wall_txt(k) for k in sorted(wall_fires))
    luck_txt = (f"luck floor 26^-4 = {luck_floor(4):.2e} "
                f"(26^-L per stratum in the strata table)")

    if fired_again and any_wall:
        return {**out, "verdict": "DEEPENS",
                "reason": (
                    f"the fired cell fires again in the new draws "
                    f"({fired_fires}/{fires[_key(FIRED_CELL)]['new']['n_draws']}, "
                    f"pooled {pooled_fired['count']}/"
                    f"{pooled_fired['n_draws']}) AND at least one "
                    f"previously walled cell fires ({walls_txt}) — the "
                    f"sampled channel's reach grows with budget in both "
                    f"rate and extent; signature 2's resolution "
                    f"parameter is measurably load-bearing (§1). "
                    f"Every fire disclosed verbatim with its (item, "
                    f"seed, draw) address; {luck_txt}.")}
    if fired_again:
        return {**out, "verdict": "REPLICATES",
                "reason": (
                    f"the fired cell fires again "
                    f"({fired_fires}/{fires[_key(FIRED_CELL)]['new']['n_draws']} "
                    f"new; pooled {pooled_fired['count']}/"
                    f"{pooled_fired['n_draws']}); every previously "
                    f"walled cell stays silent ({walls_txt}) — the exp3 "
                    f"fire was a draw from a stable nonzero rate "
                    f"localized where the mechanism says it should be; "
                    f"the walls stand at 4× resolution (pooled zero "
                    f"bound {blind['pooled_per_cell_zero_bound']:.2e}). "
                    f"{luck_txt}. {blind['statement']}.")}
    if any_wall:
        return {**out, "verdict": "RELOCATES",
                "reason": (
                    f"the fired cell is silent in the new draws (0/"
                    f"{fires[_key(FIRED_CELL)]['new']['n_draws']}, CP95 "
                    f"≤ {fires[_key(FIRED_CELL)]['new']['cp95_upper']:.2e}) "
                    f"but a previously walled cell fires ({walls_txt}). "
                    f"Read as sampling variance at single-event rates, "
                    f"pooled across cells — fires are exact-verified, "
                    f"there is no instrument doubt to resolve (§1): "
                    f"existence extends to the newly fired cell, and "
                    f"the fired cell's pooled rate revises downward to "
                    f"{pooled_fired['count']}/{pooled_fired['n_draws']}. "
                    f"{luck_txt}.")}
    return {**out, "verdict": "LONE-DRAW",
            "reason": (
                f"zero new fires anywhere ({walls_txt}; fired cell 0/"
                f"{fires[_key(FIRED_CELL)]['new']['n_draws']}, CP95 ≤ "
                f"{fires[_key(FIRED_CELL)]['new']['cp95_upper']:.2e}). "
                f"Exp 3's fire STANDS — it is committed, verified, and "
                f"existence is not retractable by later silence (the "
                f"asymmetry rule, applied symmetrically to our own "
                f"result). The pooled rate at the fired cell becomes "
                f"{pooled_fired['count']}/{pooled_fired['n_draws']} "
                f"(point {pooled_fired['rate']:.2e}), and this is the "
                f"single-event regime stated plainly: reachability "
                f"demonstrated, rate below this design's resolving "
                f"power. {luck_txt}. {blind['statement']}.")}


# ----------------------------------------------------------------- driver

def run(root=EXP3C) -> dict:
    """Load both trees through the frozen producers, re-assert every
    standing referent, and adjudicate. No model is loaded; nothing is
    sampled; every input is a committed record or a frozen loader's
    output (design §2.1)."""
    check_frozen_imports()
    check_stream_map()
    verify_fn = a3.load_verify()
    exp3_cells = a3.load_sampling_cells(EXP3, verify_fn=verify_fn)
    addresses = extract_fire_addresses(EXP3, exp3_cells,
                                       verify_fn=verify_fn)
    gate2 = a3.load_gate2_referents()
    sha_refs = a3.items_sha_referents(gate2)
    return verdict_3c(
        load_new_cells(root, verify_fn=verify_fn),
        load_gate1_records(root),
        exp3_cells,
        exp3_referent=load_exp3_referent(),
        exp3_fire_addresses=addresses,
        prompts=load_prompts(),
        sha_refs=sha_refs)


if __name__ == "__main__":
    v = run()
    print(json.dumps({k: v[k] for k in
                      ("verdict", "reason", "adjudication", "pooled",
                       "gate1_total_draws_compared", "leak_voids")
                      if k in v}, indent=1))
