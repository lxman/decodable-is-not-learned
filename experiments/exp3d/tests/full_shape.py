"""Synthetic full-shape batteries for the Exp 3d freeze rule (doc Open
item 7): the frozen verdict tree must be EXECUTED to every terminal —
STRUCTURED (thin and non-thin, replicated and unreplicated at 410m),
ANTI-STRUCTURED, UNSTRUCTURED, UNINFORMATIVE, both INSUFFICIENT_DATA
routes (gate-1 stream drift; every-fire-void), and the
leak-void-discloses-and-proceeds route — end to end through the
frozen loaders of ALL THREE trees, before the tag.

Each battery is three complete on-disk trees in the runners' own
layouts: a synthetic exp3 tree (16 sampling cells, seeds 0–3) loaded
through exp3's OWN frozen loader, a synthetic 3c tree (4 sampling
cells at seeds 4–15) loaded through analyze_3c's loaders, and a
synthetic 3d tree (per-block shards at seeds 16–39/16–27, 2 gate-1
records, 4 scoring records) loaded through analyze_3d's loaders. The
committed-fire pin, base-draws pin, item-sha pin, ctrl-rate pin, and
selection/power records are built from the same world spec, exactly
as run() builds them from the sha-pinned committed records.

Worlds use n = 20 items per rung. reverse_string's synthetic answers
carry a STRUCTURE GRADIENT — runs, pairs, and all-distinct strings in
every stratum (lengths 4/5/6 at 7/7/6 items) — because the rank
statistic needs real value spread: an all-uniform battery would tie
every midrank and the tree could never reach a rejection terminal.
Every answer is non-palindromic (the reversal prompt quotes the
REVERSED answer, so a palindrome would leak its own answer), distinct
across items, and lowercase a–z. The synthetic m_min is 2 (computed
through the real machinery in the worlds themselves): a single fire's
best placement is 1/7, so UNINFORMATIVE is exercised at |F| = 1, not
just at silence. Stored per-seed tallies are computed HERE with 2c's
verify in a plain loop — independently of the analyzer's recompute —
so the tally agreement check crosses two implementations.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

EXP3D = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP3D.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from experiments.exp3 import analyze_3 as a3  # noqa: E402
from experiments.exp3c import analyze_3c as c  # noqa: E402
from experiments.exp3d import analyze_3d as d  # noqa: E402
from experiments.exp3d import functional_3d as fl  # noqa: E402
from experiments.exp3d import rank_test_3d as rt  # noqa: E402
from experiments.exp3d.rederive_3d import gate1_record_3d  # noqa: E402

N = 20
ANSWER_TYPE = "word"
FILLER = " ~z"

# the structure gradient (module docstring): per stratum, one long-run
# answer, one/two pair answers, the rest all-distinct — non-palindromic
# by construction, pairwise distinct
REVERSE_ANSWERS = [
    "aaab", "ccdd", "eefg", "hijk", "lmno", "pqrs", "tuvw",          # 4
    "aaabc", "ddeef", "gghij", "klmno", "pqrst", "uvwxy", "zabcd",   # 5
    "aaaabc", "ddddee", "ffghij", "klmnop", "qrstuv", "wxyzab",      # 6
]

# the synthetic committed in-sample record (exp3 + 3c fires): cheap
# items fired, mirroring the real texture
EXP3_FIRE_1B = (0, 0, 6)          # item 0 'aaab', seed 0, draw 6
C3_FIRES_1B = ((0, 8, 53), (2, 13, 34))
C3_FIRES_410M = ((1, 8, 6),)
SYN_FIRED_SETS = {"1b": [0, 2], "410m": [1]}
SYN_FIRES_PIN = {
    "1b": tuple(sorted(
        [{"item": EXP3_FIRE_1B[0], "seed": EXP3_FIRE_1B[1],
          "draw": EXP3_FIRE_1B[2], "source": "exp3"}]
        + [{"item": i, "seed": s, "draw": dr, "source": "3c"}
           for (i, s, dr) in C3_FIRES_1B],
        key=lambda a: (a["item"], a["seed"], a["draw"]))),
    "410m": tuple({"item": i, "seed": s, "draw": dr, "source": "3c"}
                  for (i, s, dr) in C3_FIRES_410M),
}
SYN_BASE_DRAWS = {s: N * (a3.K_TOTAL["rev_string7"] + c.K_NEW)
                  for s in d.SIZES_3D}    # 20 × (256 + 768) = 20,480
SYN_ITEMS_SHA = {"reverse_string": "items-reverse_string",
                 "ctrl_copy": "items-ctrl_copy"}
SYN_CTRL_RATE = {s: {"count": 19, "n_draws": 20} for s in d.SIZES_3D}


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


def prompts_for(answers, leak_items=()) -> list:
    """Synthetic reversal prompts in 2c's rendering shape: the quoted
    input is the REVERSED answer, so a non-palindromic answer never
    appears in its own prompt; leak items get it planted verbatim."""
    out = []
    for i, ans in enumerate(answers):
        hint = f" (hint {ans})" if i in leak_items else ""
        out.append(f"Q: Spell the string '{ans[::-1]}' "
                   f"backwards{hint}.\nA:")
    return out


def build_rows(answers, fire_addresses, seeds, dps) -> list:
    fires = set()
    for (i, s, dr) in fire_addresses:
        if not (0 <= i < len(answers) and s in seeds and 0 <= dr < dps):
            raise ValueError(f"fire address ({i},{s},{dr}) outside the "
                             f"battery")
        fires.add((i, s, dr))
    rows = []
    for i in range(len(answers)):
        draws = {}
        for s in seeds:
            draws[str(s)] = [f" {answers[i]}" if (i, s, dr) in fires
                             else FILLER for dr in range(dps)]
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


def _write_cell(dir_, rung, rec, rows, stem=None) -> None:
    dir_.mkdir(parents=True, exist_ok=True)
    stem = stem or rung
    with gzip.open(dir_ / f"{stem}.draws.jsonl.gz", "wt") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    rec = {**rec, "draws_file": f"{stem}.draws.jsonl.gz"}
    (dir_ / f"{stem}.json").write_text(json.dumps(rec))


# ------------------------------------------------------- tree builders

def write_exp3_tree(root: Path, twin_fires=None) -> None:
    """The synthetic exp3 tree: 16 sampling cells, seeds 0–3, the one
    committed 1b fire planted, twins silent — unless `twin_fires`
    plants contamination (the refusal-path fixture)."""
    twin_fires = twin_fires or {}
    for (rung, size, mode) in a3.SAMPLING_CELLS:
        labels, answers = rung_items(rung)
        dps = a3.DRAWS_PER_SEED[rung]
        fires = list(twin_fires.get((rung, size, mode), []))
        if (rung, size, mode) == ("reverse_string", "1b", "trained"):
            fires = [EXP3_FIRE_1B]
        rows = build_rows(answers, fires, a3.SEEDS, dps)
        rec = _prov(rung, size, mode, seeds=a3.SEEDS, dps=dps,
                    k_total=len(a3.SEEDS) * dps)
        rec["per_seed_tallies"] = independent_tallies(rows, answers,
                                                      labels, a3.SEEDS)
        _write_cell(Path(root) / "results" / "sampling"
                    / f"{size}_{mode}", rung, rec, rows)


def write_3c_tree(root: Path) -> None:
    """The synthetic 3c tree: the 4 scored cells' new draws (seeds
    4–15) with the synthetic committed 3c fires planted."""
    fires_by_cell = {
        ("reverse_string", "1b", "trained"): list(C3_FIRES_1B),
        ("reverse_string", "410m", "trained"): list(C3_FIRES_410M),
    }
    for key in c.SCORED_CELLS:
        rung, size, mode = key
        labels, answers = rung_items(rung)
        rows = build_rows(answers, fires_by_cell.get(key, []),
                          c.NEW_SEEDS, c.DRAWS_PER_SEED_3C)
        rec = _prov(rung, size, mode, seeds=c.NEW_SEEDS,
                    dps=c.DRAWS_PER_SEED_3C, k_total=c.K_NEW)
        rec["per_seed_tallies"] = independent_tallies(rows, answers,
                                                      labels,
                                                      c.NEW_SEEDS)
        _write_cell(Path(root) / "results" / "sampling"
                    / f"{size}_trained", rung, rec, rows)


def c3_referent_fires(root: Path) -> dict:
    """The role 3c's sha-pinned verdict record plays in run(), built
    from the synthetic tree spec."""
    out = {}
    counts = {("reverse_string", "1b", "trained"): len(C3_FIRES_1B),
              ("reverse_string", "410m", "trained"):
                  len(C3_FIRES_410M)}
    for key in c.SCORED_CELLS:
        out["/".join(key)] = {
            "new": {"count": counts.get(key, 0), "n_draws": N * c.K_NEW}}
    return out


def write_3d_tree(root: Path, c3_root: Path, *, new_fires,
                  gate1_diffs=None, ell=None,
                  ctrl_gate_passed=True) -> dict:
    """The synthetic 3d tree: per-block shards with `new_fires` per
    size planted, 2 gate-1 records attesting the TRUE hashes of the
    synthetic 3c tree's draws files (finding B, exercised for real),
    and 4 scoring records. Returns the true 3c gz hashes for
    check_gate1_committed_shas_3d."""
    gate1_diffs = gate1_diffs or {}
    labels, answers = rung_items("reverse_string")
    for size in d.SIZES_3D:
        fires = list(new_fires.get(size, []))
        for block in d.SEED_BLOCKS[size]:
            block_fires = [(i, s, dr) for (i, s, dr) in fires
                           if s in block]
            rows = build_rows(answers, block_fires, block,
                              d.DRAWS_PER_SEED_3D)
            rec = _prov("reverse_string", size, "trained", seeds=block,
                        dps=d.DRAWS_PER_SEED_3D, k_total=d.K_BLOCK)
            rec["per_seed_tallies"] = independent_tallies(
                rows, answers, labels, block)
            _write_cell(Path(root) / "results" / "sampling"
                        / f"{size}_trained", "reverse_string", rec,
                        rows, stem=d.shard_name(block))
    true_shas = {}
    for size in d.SIZES_3D:
        gz = (Path(c3_root) / "results" / "sampling"
              / f"{size}_trained" / "reverse_string.draws.jsonl.gz")
        true_shas[size] = hashlib.sha256(gz.read_bytes()).hexdigest()
        rec = gate1_record_3d(
            size, n_items=N, diffs=list(gate1_diffs.get(size, [])),
            committed_gz_sha=true_shas[size],
            items_sha=SYN_ITEMS_SHA["reverse_string"],
            model_sha=f"synthetic-{size}",
            stack={"torch": "synthetic", "transformers": "synthetic"})
        p = (Path(root) / "results" / "gate1" / f"{size}_trained"
             / "reverse_string.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec))
    if ell is None:
        # a mildly structure-agreeing scoring arm: cheaper structure →
        # higher ℓ; one None exercises the zero-probability path
        vals = [fl.c1_unigram_bits(a) for a in answers]
        ell = [None if i == 19 else -float(v) for i, v in
               enumerate(vals)]
    for size in d.SIZES_3D:
        for rung in d.SCORING_RUNGS:
            rec = {"rung": rung, "size": size, "mode": "trained",
                   "n_items": N,
                   "items_sha256": SYN_ITEMS_SHA[rung],
                   "answers": rung_items(rung)[1],
                   "dtype": "float32",
                   "model_sha": f"synthetic-{size}",
                   "stack": {"torch": "synthetic",
                             "transformers": "synthetic"},
                   "ell": list(ell) if rung == "reverse_string"
                   else [-0.05] * N,
                   "span_token_ids": [[1, 2] for _ in range(N)],
                   "per_token_logprobs": [[-0.1] for _ in range(N)],
                   "zero_probability_items":
                       (1 if rung == "reverse_string" else 0),
                   "span_round_trip_failures": 0}
            if rung == "ctrl_copy":
                pin = SYN_CTRL_RATE[size]
                r = pin["count"] / pin["n_draws"]
                rec["known_answer_gate"] = {
                    "predicted_rate": 0.9 if ctrl_gate_passed else 0.1,
                    "committed_count": pin["count"],
                    "committed_n_draws": pin["n_draws"],
                    "committed_rate": r,
                    "band": [d.CTRL_GATE_LOWER_FACTOR * r,
                             r + d.CTRL_GATE_UPPER_MARGIN],
                    "lower_factor": d.CTRL_GATE_LOWER_FACTOR,
                    "upper_margin": d.CTRL_GATE_UPPER_MARGIN,
                    "passed": bool(ctrl_gate_passed)}
            p = (Path(root) / "results" / "scoring" / f"{size}_trained"
                 / f"{rung}.json")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(rec))
    return true_shas


def write_selection_and_power(root: Path) -> tuple:
    """The synthetic committed selection + power records, produced
    through the SAME code path the real ones were (select_winner,
    candidate_values, m_min_of) on the synthetic answers and the
    synthetic committed fired sets."""
    _labels, answers = rung_items("reverse_string")
    sel = fl.select_winner(answers, SYN_FIRED_SETS["1b"],
                           SYN_FIRED_SETS["410m"])
    name, fn = fl.CANDIDATES[sel["winner_index"]]
    values = fl.candidate_values(fn, answers)
    strata = fl.strata_of(answers)
    sel_path = Path(root) / "functional_selection_syn.json"
    sel_path.write_text(json.dumps({
        "winner": sel["winner"],
        "winner_values": values,
        "selection_table": sel["table"],
        "tie_structure": fl.tie_structure(values, strata),
        "decile_bucket": fl.decile_bucket(values, strata),
    }, sort_keys=True))
    power_path = Path(root) / "power_syn.json"
    power_path.write_text(json.dumps(
        {"m_min": rt.m_min_of(values, strata)}))
    return sel_path, power_path


# ----------------------------------------------------------- the worlds

def build_world(tmp: Path, *, new_fires, gate1_diffs=None,
                leak_items=(), ell=None) -> dict:
    """Write the three trees and adjudicate through the frozen loaders
    and verdict — the exact shape run() executes, with the world spec
    standing in for the sha-pinned committed records."""
    tmp = Path(tmp)
    exp3_root = tmp / "exp3"
    c3_root = tmp / "exp3c"
    root_3d = tmp / "exp3d"
    write_exp3_tree(exp3_root)
    write_3c_tree(c3_root)
    true_shas = write_3d_tree(root_3d, c3_root, new_fires=new_fires,
                              gate1_diffs=gate1_diffs, ell=ell)
    sel_path, power_path = write_selection_and_power(tmp)

    verify_fn = c.load_verify_3c()
    exp3_cells = a3.load_sampling_cells(exp3_root, verify_fn=verify_fn)
    addresses = c.extract_fire_addresses(exp3_root, exp3_cells,
                                         verify_fn=verify_fn)
    c3_cells = c.load_new_cells(c3_root, verify_fn=verify_fn)
    base = d.build_committed_base(
        exp3_cells, c3_cells, addresses,
        c3_referent_fires=c3_referent_fires(c3_root),
        fires_pin=SYN_FIRES_PIN, base_draws_pin=SYN_BASE_DRAWS)
    _labels, answers = rung_items("reverse_string")
    selection = d.load_selection(answers, sel_path,
                                 fired_sets=SYN_FIRED_SETS)
    power_pin = d.load_power_pin(selection, power_path)
    new_cells = d.load_new_cells_3d(root_3d, verify_fn=verify_fn,
                                    n_items=N,
                                    answer_type_pin=ANSWER_TYPE)
    gate1 = d.load_gate1_3d(root_3d, n_items=N)
    d.check_gate1_committed_shas_3d(gate1, c3_root, expected=true_shas)
    scoring = d.load_scoring_3d(root_3d, items_sha_pin=SYN_ITEMS_SHA,
                                ctrl_rate_pin=SYN_CTRL_RATE, n_items=N)
    prompts = {d.RUNG: prompts_for(answers, leak_items=leak_items)}
    return d.verdict_3d(new_cells, gate1, scoring, base, selection,
                        power_pin, prompts)


# world specs: (name, kwargs, expected verdict prefix)
def world_specs() -> list:
    return [
        ("W1 structured non-thin, 410m replicated",
         {"new_fires": {
             "1b": [(0, 16, 0), (1, 20, 3), (7, 25, 8), (8, 30, 1),
                    (14, 39, 63)],
             "410m": [(0, 16, 0), (7, 20, 3), (14, 27, 8)]}},
         "STRUCTURED"),
        ("W2 structured thin, 410m unreplicated",
         {"new_fires": {"1b": [(0, 16, 0), (7, 20, 3), (14, 25, 8)],
                        "410m": [(3, 16, 0)]}},
         "STRUCTURED THIN"),
        ("W3 anti-structured (thin)",
         {"new_fires": {"1b": [(3, 16, 0), (4, 20, 3), (5, 25, 8),
                               (6, 30, 1)],
                        "410m": []}},
         "ANTI-STRUCTURED THIN"),
        ("W4 unstructured (thin)",
         {"new_fires": {"1b": [(2, 16, 0), (9, 20, 3)],
                        "410m": []}},
         "UNSTRUCTURED THIN"),
        ("W5 uninformative at |F| = 1 < m_min",
         {"new_fires": {"1b": [(3, 16, 0)], "410m": []}},
         "UNINFORMATIVE THIN"),
        ("W6 insufficient-data: gate-1 drift",
         {"new_fires": {"1b": [(0, 16, 0)], "410m": []},
          "gate1_diffs": {"1b": [{"item": 5, "seed": 8, "draw": 2,
                                  "got": " x", "committed": " y"}]}},
         "INSUFFICIENT_DATA"),
        ("W7 insufficient-data: every fire void",
         {"new_fires": {"1b": [(6, 16, 0)], "410m": []},
          "leak_items": (6,)},
         "INSUFFICIENT_DATA"),
        ("W8 void discloses and proceeds",
         {"new_fires": {"1b": [(0, 16, 0), (6, 18, 2), (7, 20, 3),
                               (14, 25, 8)],
                        "410m": []},
          "leak_items": (6,)},
         "STRUCTURED THIN"),
    ]
