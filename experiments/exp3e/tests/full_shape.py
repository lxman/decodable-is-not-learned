"""Synthetic full-shape batteries for the Exp 3e freeze rule (doc Open
item 8): the frozen verdict tree must be EXECUTED to every terminal —
SHORTCUT (thin and non-thin, with each specificity annotation),
NO-SHORTCUT, ANTI-SHORTCUT, UNINFORMATIVE, both INSUFFICIENT_DATA
routes (gate-1 stream drift; every-fire-void), and the leak-void-
discloses-and-proceeds route — end to end through the frozen loaders
of ALL FOUR trees, before the tag.

Each world is four complete on-disk trees in the runners' own layouts:
a synthetic exp3 tree (16 sampling cells, seeds 0–3) loaded through
exp3's OWN frozen loader, a synthetic 3c tree (4 scored cells, seeds
4–15) through analyze_3c's loaders, a synthetic 3d tree (per-block
shards, seeds 16–39/16–27) through analyze_3d's loaders, and a
synthetic 3e tree (45-item-subset shards at the new seeds, 2 gate-1
records, the scorer-gate record) through analyze_3e's loaders. The
committed-fire pin, draws-file sha pins, item-sha pin, ctrl-rate pin,
partition record and power record are built from the same world spec,
exactly as run() builds them from the sha-pinned committed records.

The synthetic battery has N = 21 items: a 16-item len-4 repeat class
(11 reachable — 5 by transposition, 6 by rotation — and 5
non-reachable), 3 all-distinct len-4 items, one len-5 and one len-6.
The repeat class is large enough that a non-THIN verdict (n > 10) is
reachable, and its m_min (7) and m_s,min are computed through the
real machinery in the worlds themselves. Every answer is non-
palindromic, distinct, lowercase a–z. Stored per-seed tallies are
computed HERE with 2c's verify in a plain loop — independently of the
analyzer's recompute — so the tally agreement check crosses two
implementations.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

EXP3E = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP3E.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from experiments.exp3 import analyze_3 as a3  # noqa: E402
from experiments.exp3c import analyze_3c as c  # noqa: E402
from experiments.exp3d import analyze_3d as d  # noqa: E402
from experiments.exp3e import analyze_3e as e  # noqa: E402
from experiments.exp3e import partition_3e as pt  # noqa: E402
from experiments.exp3e import scorer_3e as sc  # noqa: E402
from experiments.exp3e.rederive_3e import gate1_record_3e  # noqa: E402

ANSWER_TYPE = "word"
FILLER = " ~z"

# the synthetic reverse_string battery (answers; inputs are reverses)
REVERSE_ANSWERS = [
    # 16-item len-4 repeat class
    "ecde", "dmkd", "wchw",            # mirror (0,3): transposition
    "qffp", "xggy",                    # mirror (1,2): transposition
    "qaba", "aefe", "kbjb",            # (0,2): rotation right
    "mhmp", "pbpd", "iviz",            # (1,3): rotation left
    "cbaa", "wxee", "pehh",            # (0,1): non-reachable
    "qqdn", "bbpc",                    # (2,3): non-reachable
    # 3 all-distinct len-4
    "astu", "dtwc", "tdsa",
    # one len-5, one len-6
    "dyayp", "rxxxxd",
]
N = len(REVERSE_ANSWERS)
SUBSET = list(range(16))
REACHABLE = list(range(11))
NON_REACHABLE = list(range(11, 16))
ARM_ITEMS = [0, 1, 2, 5, 6, 7, 8, 9, 10]        # (1,2) mirrors sit out

# the synthetic committed in-sample record: exp3 + 3c + 3d fires,
# mirroring the real texture (hot item 0, all repeat-class fires on
# reachable items, two all-distinct fires)
SYN_COMMITTED_FIRES = {
    "1b": (
        {"item": 16, "seed": 0, "draw": 6, "source": "exp3"},
        {"item": 0, "seed": 5, "draw": 58, "source": "3c"},
        {"item": 0, "seed": 8, "draw": 53, "source": "3c"},
        {"item": 1, "seed": 13, "draw": 39, "source": "3c"},
        {"item": 20, "seed": 8, "draw": 2, "source": "3c"},
        {"item": 0, "seed": 19, "draw": 21, "source": "3d"},
        {"item": 8, "seed": 20, "draw": 14, "source": "3d"},
        {"item": 9, "seed": 20, "draw": 43, "source": "3d"},
        {"item": 17, "seed": 16, "draw": 11, "source": "3d"},
    ),
    "410m": (
        {"item": 0, "seed": 8, "draw": 6, "source": "3c"},
        {"item": 7, "seed": 15, "draw": 42, "source": "3c"},
        {"item": 0, "seed": 24, "draw": 62, "source": "3d"},
        {"item": 18, "seed": 20, "draw": 28, "source": "3d"},
    ),
}
SYN_ITEMS_SHA = {"reverse_string": "items-reverse_string",
                 "ctrl_copy": "items-ctrl_copy"}
SYN_CTRL_RATE = {s: {"count": 19 * N, "n_draws": 32 * N}
                 for s in e.SIZES_3E}     # ctrl fires on 19 of 32 draws/item


def _run(start: int, length: int) -> str:
    return "".join(chr(ord("a") + (start + j) % 26)
                   for j in range(length))


def rung_items(rung) -> tuple:
    """(labels, answers) for a synthetic rung."""
    if rung == a3.MATCHED_CONTROL:
        answers = [f"{(i % 9) + 1}:4{i % 10} pm" for i in range(N)]
    elif rung == a3.POSITIVE_CONTROL:
        answers = [_run(3 * i, 5) for i in range(N)]
    elif rung == "reverse_string":
        answers = list(REVERSE_ANSWERS)
    else:  # rev_string7
        answers = [_run(3 * i, 7) for i in range(N)]
    return [ans[0] for ans in answers], answers


def prompts_for(answers, leak_items=(), leak_strings=None) -> list:
    """Synthetic reversal prompts in 2c's rendering shape: the quoted
    input is the REVERSED answer, so a non-palindromic answer never
    appears in its own prompt; leak items get their answer planted
    verbatim (or a named competitor string, for the competitor-void
    route)."""
    leak_strings = leak_strings or {}
    out = []
    for i, ans in enumerate(answers):
        hint = ""
        if i in leak_items:
            hint = f" (hint {leak_strings.get(i, ans)})"
        out.append(f"Q: Spell the string '{ans[::-1]}' "
                   f"backwards{hint}.\nA:")
    return out


def build_rows(answers, fire_addresses, seeds, dps, items=None,
               competitor_emissions=()) -> list:
    """Rows for `items` (default all) with ` answer` planted at the
    fire addresses and any competitor string planted at
    competitor_emissions = [(item, seed, draw, string)]."""
    items = list(range(len(answers))) if items is None else list(items)
    fires = set()
    for (i, s, dr) in fire_addresses:
        if not (i in items and s in seeds and 0 <= dr < dps):
            raise ValueError(f"fire address ({i},{s},{dr}) outside the "
                             f"battery")
        fires.add((i, s, dr))
    comp = {}
    for (i, s, dr, text) in competitor_emissions:
        if not (i in items and s in seeds and 0 <= dr < dps):
            raise ValueError(f"competitor address ({i},{s},{dr}) "
                             f"outside the battery")
        comp[(i, s, dr)] = text
    rows = []
    for i in items:
        draws = {}
        for s in seeds:
            stream = []
            for dr in range(dps):
                if (i, s, dr) in fires:
                    stream.append(f" {answers[i]}")
                elif (i, s, dr) in comp:
                    stream.append(f" {comp[(i, s, dr)]}")
                else:
                    stream.append(FILLER)
            draws[str(s)] = stream
        rows.append({"item": i, "draws": draws})
    return rows


def independent_tallies(rows, answers, labels, seeds) -> dict:
    """Stored convenience tallies via 2c's verify in a plain loop —
    NOT the analyzer's recompute (two implementations must agree)."""
    import harness

    out = {str(s): {"full_string": 0, "first_char": 0, "n_draws": 0}
           for s in seeds}
    for row in rows:
        i = row["item"]
        for s in seeds:
            for dr in row["draws"][str(s)]:
                out[str(s)]["n_draws"] += 1
                if harness.verify(dr, answers[i], ANSWER_TYPE):
                    out[str(s)]["full_string"] += 1
                if a3.score_first_char(dr, labels[i]):
                    out[str(s)]["first_char"] += 1
    return out


def _prov(rung, size, mode, *, seeds, dps, k_total, items_sha=None):
    labels, answers = rung_items(rung)
    return {"rung": rung, "size": size, "mode": mode, "n_items": N,
            "probe_labels": labels, "answers": answers,
            "answer_type": ANSWER_TYPE, "n_shots": 2,
            "dtype": "float32",
            "untrained_seed": 0 if mode == "untrained" else None,
            "model_sha": f"synthetic-{size}",
            "items_sha256": items_sha or f"items-{rung}",
            "seeds": list(seeds), "draws_per_seed": dps,
            "k_total": k_total}


def _write_cell(dir_, stem, rec, rows) -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    gz = dir_ / f"{stem}.draws.jsonl.gz"
    with gzip.open(gz, "wt") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    rec = {**rec, "draws_file": f"{stem}.draws.jsonl.gz"}
    (dir_ / f"{stem}.json").write_text(json.dumps(rec))
    return gz


def _fires_from(size, source) -> list:
    return [(a["item"], a["seed"], a["draw"])
            for a in SYN_COMMITTED_FIRES[size] if a["source"] == source]


# ------------------------------------------------------- tree builders

def write_exp3_tree(root: Path) -> dict:
    """The synthetic exp3 tree: 16 sampling cells, seeds 0–3; the
    exp3-source fires planted in the trained reverse_string cells;
    ctrl_copy trained cells emit their answer on 19 of 32 draws per
    item (the gate-(b) referent); twins silent. Returns the true
    draws-file shas the 3e pins stand in for."""
    shas = {}
    for (rung, size, mode) in a3.SAMPLING_CELLS:
        labels, answers = rung_items(rung)
        dps = a3.DRAWS_PER_SEED[rung]
        fires = []
        if mode == "trained" and rung == "reverse_string":
            fires = _fires_from(size, "exp3")
        if mode == "trained" and rung == a3.POSITIVE_CONTROL:
            # 19 of 32 draws per item verify: seeds 0,1 all 8, seed 2
            # three of 8, seed 3 none
            fires = [(i, s, dr) for i in range(N)
                     for (s, cnt) in ((0, 8), (1, 8), (2, 3))
                     for dr in range(cnt)]
        rows = build_rows(answers, fires, a3.SEEDS, dps)
        rec = _prov(rung, size, mode, seeds=a3.SEEDS, dps=dps,
                    k_total=len(a3.SEEDS) * dps)
        rec["per_seed_tallies"] = independent_tallies(rows, answers,
                                                      labels, a3.SEEDS)
        gz = _write_cell(Path(root) / "results" / "sampling"
                         / f"{size}_{mode}", rung, rec, rows)
        shas[(rung, size, mode)] = hashlib.sha256(
            gz.read_bytes()).hexdigest()
    return shas


def write_3c_tree(root: Path) -> dict:
    shas = {}
    for key in c.SCORED_CELLS:
        rung, size, mode = key
        labels, answers = rung_items(rung)
        fires = _fires_from(size, "3c") if rung == "reverse_string" \
            else []
        rows = build_rows(answers, fires, c.NEW_SEEDS, c.DRAWS_PER_SEED_3C)
        rec = _prov(rung, size, mode, seeds=c.NEW_SEEDS,
                    dps=c.DRAWS_PER_SEED_3C, k_total=c.K_NEW)
        rec["per_seed_tallies"] = independent_tallies(rows, answers,
                                                      labels,
                                                      c.NEW_SEEDS)
        gz = _write_cell(Path(root) / "results" / "sampling"
                         / f"{size}_trained", rung, rec, rows)
        shas[key] = hashlib.sha256(gz.read_bytes()).hexdigest()
    return shas


def write_3d_tree(root: Path) -> dict:
    """The synthetic 3d sampling shards (the 3e analyzer reads only
    3d's sampling tree, never its gate-1/scoring records)."""
    shas = {}
    labels, answers = rung_items("reverse_string")
    for size in d.SIZES_3D:
        fires = _fires_from(size, "3d")
        for block in d.SEED_BLOCKS[size]:
            block_fires = [(i, s, dr) for (i, s, dr) in fires
                           if s in block]
            rows = build_rows(answers, block_fires, block,
                              d.DRAWS_PER_SEED_3D)
            rec = _prov("reverse_string", size, "trained", seeds=block,
                        dps=d.DRAWS_PER_SEED_3D, k_total=d.K_BLOCK)
            rec["per_seed_tallies"] = independent_tallies(
                rows, answers, labels, block)
            gz = _write_cell(Path(root) / "results" / "sampling"
                             / f"{size}_trained", d.shard_name(block),
                             rec, rows)
            shas[(size, block)] = hashlib.sha256(
                gz.read_bytes()).hexdigest()
    return shas


def write_3e_tree(root: Path, d_shas: dict, *, new_fires,
                  competitor_emissions=None, gate1_diffs=None,
                  gate1_fires=None, scorer_gates_passed=True) -> dict:
    """The synthetic 3e tree: per-block subset shards with `new_fires`
    per size planted (and competitor emissions for the specificity
    arm), 2 gate-1 records attesting the TRUE hashes of the synthetic
    3d shards they compare against, and the scorer-gate record."""
    gate1_diffs = gate1_diffs or {}
    gate1_fires = gate1_fires or {}
    competitor_emissions = competitor_emissions or {}
    labels, answers = rung_items("reverse_string")
    for size in e.SIZES_3E:
        fires = list(new_fires.get(size, []))
        comps = list(competitor_emissions.get(size, []))
        for block in e.SEED_BLOCKS[size]:
            block_fires = [(i, s, dr) for (i, s, dr) in fires
                           if s in block]
            block_comps = [(i, s, dr, t) for (i, s, dr, t) in comps
                           if s in block]
            rows = build_rows(answers, block_fires, block,
                              e.DRAWS_PER_SEED_3E, items=SUBSET,
                              competitor_emissions=block_comps)
            rec = _prov("reverse_string", size, "trained", seeds=block,
                        dps=e.DRAWS_PER_SEED_3E, k_total=e.K_BLOCK)
            rec = {**rec, "n_items": len(SUBSET), "items": list(SUBSET),
                   "probe_labels": [labels[i] for i in SUBSET],
                   "answers": [answers[i] for i in SUBSET],
                   "subset_sha256": e.subset_sha256(SUBSET)}
            rec["per_seed_tallies"] = independent_tallies(
                rows, answers, labels, block)
            _write_cell(Path(root) / "results" / "sampling"
                        / f"{size}_trained", e.shard_name(block), rec,
                        rows)
    true_shas = {}
    for size in e.SIZES_3E:
        seed = e.GATE1_SEED_3E[size]
        block = next(b for b in d.SEED_BLOCKS[size] if seed in b)
        true_shas[size] = d_shas[(size, block)]
        expected = gate1_fires.get(size, e_expected_gate1_fires(size))
        rec = gate1_record_3e(
            size, items=SUBSET, diffs=list(gate1_diffs.get(size, [])),
            fires_reproduced=expected,
            committed_gz_sha=true_shas[size],
            committed_shard=f"{d.shard_name(block)}.draws.jsonl.gz",
            items_sha=SYN_ITEMS_SHA["reverse_string"],
            model_sha=f"synthetic-{size}",
            stack={"torch": "synthetic", "transformers": "synthetic"})
        p = (Path(root) / "results" / "gate1" / f"{size}_trained"
             / "reverse_string.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec))
    sg = {"gate_a": {"passed": bool(scorer_gates_passed),
                     "addresses": syn_repeat_class_fires(),
                     "expected": syn_repeat_class_fires()},
          "gate_b": {"passed": bool(scorer_gates_passed),
                     "counts": {s: dict(SYN_CTRL_RATE[s])
                                for s in e.SIZES_3E},
                     "expected": {s: dict(SYN_CTRL_RATE[s])
                                  for s in e.SIZES_3E}},
          "passed": bool(scorer_gates_passed)}
    p = Path(root) / "results" / "scorer_gates.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(sg))
    return true_shas


def e_expected_gate1_fires(size) -> list:
    """The synthetic gate-1 expected fires: the committed 3d fires at
    the gate-1 seed on subset items."""
    seed = e.GATE1_SEED_3E[size]
    return sorted(
        [{"item": a["item"], "seed": a["seed"], "draw": a["draw"]}
         for a in SYN_COMMITTED_FIRES[size]
         if a["seed"] == seed and a["item"] in SUBSET],
        key=lambda a: (a["item"], a["seed"], a["draw"]))


def syn_repeat_class_fires() -> dict:
    return {s: sorted(
        [{"item": a["item"], "seed": a["seed"], "draw": a["draw"]}
         for a in SYN_COMMITTED_FIRES[s] if a["item"] in SUBSET],
        key=lambda a: (a["item"], a["seed"], a["draw"]))
        for s in e.SIZES_3E}


def write_partition_and_power(root: Path) -> tuple:
    """The synthetic committed partition + power records, produced
    through the SAME code path the real ones are."""
    _labels, answers = rung_items("reverse_string")
    part_path = Path(root) / "partition_syn.json"
    pt.dump_partition(answers, part_path)
    partition = pt.check_partition(answers, part_path)
    power_path = Path(root) / "power_syn.json"
    power_path.write_text(json.dumps(e.power_pin_entries(partition)))
    return part_path, power_path


# ----------------------------------------------------------- the worlds

def build_world(tmp: Path, *, new_fires, competitor_emissions=None,
                gate1_diffs=None, leak_items=(), leak_strings=None,
                gate1_fires=None) -> dict:
    """Write the four trees and adjudicate through the frozen loaders
    and verdict — the exact shape run() executes, with the world spec
    standing in for the sha-pinned committed records."""
    tmp = Path(tmp)
    exp3_root = tmp / "exp3"
    c3_root = tmp / "exp3c"
    d_root = tmp / "exp3d"
    e_root = tmp / "exp3e"
    e3_shas = write_exp3_tree(exp3_root)
    c3_shas = write_3c_tree(c3_root)
    d_shas = write_3d_tree(d_root)
    true_shas = write_3e_tree(e_root, d_shas, new_fires=new_fires,
                              competitor_emissions=competitor_emissions,
                              gate1_diffs=gate1_diffs,
                              gate1_fires=gate1_fires)
    part_path, power_path = write_partition_and_power(tmp)
    _labels, answers = rung_items("reverse_string")
    labels = _labels
    draws_pins = {
        "reverse_string": {
            size: {"exp3": e3_shas[("reverse_string", size, "trained")],
                   "3c": c3_shas[("reverse_string", size, "trained")],
                   "3d": {d.shard_name(b): d_shas[(size, b)]
                          for b in d.SEED_BLOCKS[size]}}
            for size in e.SIZES_3E},
        "ctrl_copy": {
            size: e3_shas[(a3.POSITIVE_CONTROL, size, "trained")]
            for size in e.SIZES_3E},
    }
    verify_fn = c.load_verify_3c()
    score_fn = sc.load_scorer()
    partition = e.load_partition_3e(answers, part_path,
                                    subset_pin=SUBSET,
                                    file_sha_pin=None)
    power_pin = e.load_power_pin_3e(partition, power_path)
    rows = e.load_committed_rows(
        roots={"exp3": exp3_root, "3c": c3_root, "3d": d_root},
        n_items=N, draws_pins=draws_pins)
    base = e.committed_base_3e(rows, answers, ANSWER_TYPE, score_fn,
                               fires_pin=SYN_COMMITTED_FIRES,
                               subset=SUBSET,
                               ctrl_answers=rung_items(
                                   a3.POSITIVE_CONTROL)[1])
    twin = e.load_twin_record(exp3_root, verify_fn=verify_fn,
                              pins={"reversal": 4 * N * 256,
                                    "control": 4 * N * 32})
    new_cells = e.load_new_cells_3e(e_root, verify_fn=verify_fn,
                                    items=SUBSET, answers=answers,
                                    labels=labels,
                                    answer_type_pin=ANSWER_TYPE)
    gate1 = e.load_gate1_3e(e_root, items=SUBSET,
                            expected_fires={s: e_expected_gate1_fires(s)
                                            for s in e.SIZES_3E})
    e.check_gate1_committed_shas_3e(gate1, d_root, expected=true_shas)
    scorer_gates = e.load_scorer_gates_3e(
        e_root, fires_pin=syn_repeat_class_fires(),
        ctrl_pin=SYN_CTRL_RATE)
    prompts = {e.RUNG: prompts_for(answers, leak_items=leak_items,
                                   leak_strings=leak_strings)}
    return e.verdict_3e(new_cells, gate1, scorer_gates, base, partition,
                        power_pin, prompts, twin, answers=answers,
                        score_fn=score_fn, answer_type=ANSWER_TYPE)


def _fires_on(items, size, seed0=40, draw=0):
    """One fire per item at distinct seeds inside the new range."""
    seeds = e.NEW_SEEDS_3E[size]
    return [(i, seeds[j % len(seeds)], draw) for j, i in enumerate(items)]


# world specs: (name, kwargs, expected verdict)
def world_specs() -> list:
    comps_directed = {"1b": [(8, 41, 1, "mphm"), (9, 42, 2, "pdbp")]}
    return [
        ("W1 shortcut non-thin, 410m replicated, directed",
         {"new_fires": {
             "1b": _fires_on(REACHABLE, "1b") + [(0, 50, 3), (0, 51, 4),
                                                  (8, 52, 5), (9, 53, 6),
                                                  (10, 54, 7)],
             "410m": _fires_on(REACHABLE[:8], "410m")},
          "competitor_emissions": comps_directed},
         "SHORTCUT (directed)"),
        ("W2 shortcut thin, 410m unreplicated, misfire-rate",
         {"new_fires": {"1b": _fires_on(REACHABLE[:8], "1b"),
                        "410m": _fires_on([0, 11], "410m")},
          "competitor_emissions": {
              "1b": [(0, 41, 1, "edec"), (0, 42, 2, "eecd"),
                     (5, 43, 3, "qbaa"), (6, 44, 4, "afee"),
                     (8, 45, 5, "mphm"), (8, 46, 6, "mmhp"),
                     (9, 47, 7, "pdbp"), (10, 48, 8, "izvi")]}},
         "SHORTCUT THIN (misfire-rate)"),
        ("W3 anti-shortcut (thin), sparse",
         {"new_fires": {"1b": _fires_on(NON_REACHABLE, "1b")
                        + [(0, 60, 0)],
                        "410m": []}},
         "ANTI-SHORTCUT THIN (sparse)"),
        ("W4 no-shortcut non-thin",
         {"new_fires": {"1b": _fires_on(REACHABLE, "1b")
                        + _fires_on(NON_REACHABLE[:3], "1b"),
                        "410m": []}},
         "NO-SHORTCUT (directed)"),
        ("W5 no-shortcut thin at n = m_min",
         {"new_fires": {"1b": _fires_on(REACHABLE[:5], "1b")
                        + _fires_on(NON_REACHABLE[:2], "1b"),
                        "410m": []}},
         "NO-SHORTCUT THIN (directed)"),
        ("W6 uninformative at n = 2 < m_min",
         {"new_fires": {"1b": _fires_on([0, 11], "1b"), "410m": []}},
         "UNINFORMATIVE THIN (sparse)"),
        ("W7 insufficient-data: gate-1 drift",
         {"new_fires": {"1b": [(0, 40, 0)], "410m": []},
          "gate1_diffs": {"1b": [{"item": 5, "seed": 20, "draw": 2,
                                  "got": " x", "committed": " y"}]}},
         "INSUFFICIENT_DATA"),
        ("W8 insufficient-data: every fire void",
         {"new_fires": {"1b": [(6, 40, 0)], "410m": []},
          "leak_items": (6,)},
         "INSUFFICIENT_DATA"),
        ("W9 void discloses and proceeds; competitor void disclosed",
         {"new_fires": {"1b": _fires_on(REACHABLE[:8], "1b")
                        + [(6, 60, 0)],
                        "410m": []},
          "competitor_emissions": {"1b": [(8, 41, 1, "mphm")]},
          "leak_items": (6, 8), "leak_strings": {8: "mphm"}},
         "SHORTCUT THIN (directed)"),
    ]
