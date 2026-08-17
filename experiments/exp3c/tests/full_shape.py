"""Synthetic full-shape batteries for the Exp 3c freeze rule (doc Open
item 4): the frozen verdict tree must be EXECUTED to every terminal —
all four worlds (DEEPENS / REPLICATES / RELOCATES / LONE-DRAW), both
INSUFFICIENT_DATA routes (gate-1 stream drift; every-fire-void), and
the leak-void-discloses-and-proceeds route — end to end through the
frozen loaders of BOTH trees, before the tag.

Each battery is two complete on-disk trees in the runners' own
layouts: a synthetic exp3 tree (16 sampling cells, seeds 0–3, exp3's
committed draw depths 64/8) loaded through exp3's OWN frozen loader,
and a synthetic 3c tree (4 sampling cells at seeds 4–15 plus the 5
gate-1 comparison records) loaded through analyze_3c's loaders. The
exp3-side referent expectations (fires table, fired addresses, fired
answer lengths) are built from the same world spec, exactly as run()
builds them from the sha-pinned committed record.

Worlds use n = 20 items per rung: the loaders pin seed sets, draw
depths, and cross-tree consistency, not the item count, so small
worlds stay honest. reverse_string's synthetic answers span lengths
4–6 (7/7/6 items) so the strata table is exercised; every answer is a
strictly-ascending letter run, so no answer is a palindrome and no
prompt contains its own answer — except where a leak world plants
one. The stored per-seed tallies are computed HERE with 2c's verify
and 3b's first_char in a plain loop — independently of the analyzer's
recompute — so the tally agreement check crosses two implementations.
"""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

EXP3C = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP3C.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))
# 2c must win the `harness` name (exp3's runner ordering, verbatim
# reasoning): only its harness defines the verify the tallies use.
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from experiments.exp3 import analyze_3 as a3  # noqa: E402
from experiments.exp3c import analyze_3c as c  # noqa: E402
from experiments.exp3c.rederive import gate1_record  # noqa: E402

N = 20
ANSWER_TYPE = "word"
FILLER = " ~z"


def _run(start: int, length: int) -> str:
    """A strictly-ascending letter run: never a palindrome, always
    lowercase a–z, distinct across items via the start offset."""
    return "".join(chr(ord("a") + (start + j) % 26) for j in range(length))


def rung_items(rung) -> tuple:
    """(labels, answers) for a synthetic rung. reverse_string spans
    lengths 4–6; rev_string7 is all length 7; the matched control's
    answers begin with digits (the real shape)."""
    if rung == a3.MATCHED_CONTROL:
        answers = [f"{(i % 9) + 1}:4{i % 10} pm" for i in range(N)]
    elif rung == a3.POSITIVE_CONTROL:
        answers = [_run(3 * i, 5) for i in range(N)]
    elif rung == "reverse_string":
        answers = [_run(3 * i, 4 + (i % 3)) for i in range(N)]
    else:  # rev_string7
        answers = [_run(3 * i, 7) for i in range(N)]
    return [ans[0] for ans in answers], answers


def prompts_for(rung, answers, leak_items=()) -> list:
    """Synthetic prompts in 2c's rendering shape. The quoted input is
    the REVERSED answer (the reversal task's real relationship), so a
    non-palindromic answer never appears in its own prompt; leak items
    get the answer planted verbatim (the class the leak-void reads)."""
    out = []
    for i, ans in enumerate(answers):
        hint = f" (hint {ans})" if i in leak_items else ""
        out.append(f"Q: Spell the string '{ans[::-1]}' "
                   f"backwards{hint}.\nA:")
    return out


def build_rows(answers, fire_addresses, seeds, dps) -> list:
    """Draw rows: FILLER everywhere except a verbatim ' {answer}' at
    each planted (item, seed, draw) fire address."""
    fires = set()
    for (i, s, d) in fire_addresses:
        if not (0 <= i < len(answers) and s in seeds and 0 <= d < dps):
            raise ValueError(f"fire address ({i},{s},{d}) outside the "
                             f"battery")
        fires.add((i, s, d))
    rows = []
    for i in range(len(answers)):
        draws = {}
        for s in seeds:
            draws[str(s)] = [f" {answers[i]}" if (i, s, d) in fires
                             else FILLER for d in range(dps)]
        rows.append({"item": i, "draws": draws})
    return rows


def independent_tallies(rows, answers, labels, seeds) -> dict:
    """The stored convenience tallies, computed with 2c's verify and
    3b's first_char in a plain loop — NOT the analyzer's recompute."""
    import harness

    out = {str(s): {"full_string": 0, "first_char": 0, "n_draws": 0}
           for s in seeds}
    for row in rows:
        i = row["item"]
        for s in seeds:
            for d in row["draws"][str(s)]:
                out[str(s)]["n_draws"] += 1
                if harness.verify(d, answers[i], ANSWER_TYPE):
                    out[str(s)]["full_string"] += 1
                if a3.score_first_char(d, labels[i]):
                    out[str(s)]["first_char"] += 1
    return out


def _prov(rung, size, mode, *, seeds, dps, k_total):
    labels, answers = rung_items(rung)
    return {"rung": rung, "size": size, "mode": mode, "n_items": N,
            "probe_labels": labels, "answers": answers,
            "answer_type": ANSWER_TYPE, "n_shots": 2, "dtype": "float32",
            "untrained_seed": 0 if mode == "untrained" else None,
            "model_sha": f"synthetic-{size}",
            "items_sha256": f"items-{rung}",
            "seeds": list(seeds), "draws_per_seed": dps,
            "k_total": k_total}


def _write_cell(d, rung, rec, rows) -> None:
    d.mkdir(parents=True, exist_ok=True)
    with gzip.open(d / f"{rung}.draws.jsonl.gz", "wt") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    rec = {**rec, "draws_file": f"{rung}.draws.jsonl.gz"}
    (d / f"{rung}.json").write_text(json.dumps(rec))


def write_exp3_tree(root: Path, exp3_fires) -> None:
    """A synthetic exp3 tree in the committed layout: 16 sampling
    cells, seeds 0–3, draw depths 64 (reversal) / 8 (controls)."""
    for (rung, size, mode) in a3.SAMPLING_CELLS:
        labels, answers = rung_items(rung)
        dps = a3.DRAWS_PER_SEED[rung]
        rows = build_rows(answers, exp3_fires.get((rung, size, mode), []),
                          a3.SEEDS, dps)
        rec = _prov(rung, size, mode, seeds=a3.SEEDS, dps=dps,
                    k_total=len(a3.SEEDS) * dps)
        rec["per_seed_tallies"] = independent_tallies(rows, answers,
                                                      labels, a3.SEEDS)
        _write_cell(Path(root) / "results" / "sampling"
                    / f"{size}_{mode}", rung, rec, rows)


def write_3c_tree(root: Path, new_fires, gate1_diffs) -> None:
    """A synthetic 3c tree: the 4 scored cells' new draws (seeds 4–15)
    and the 5 gate-1 comparison records."""
    for key in c.SCORED_CELLS:
        rung, size, mode = key
        labels, answers = rung_items(rung)
        rows = build_rows(answers, new_fires.get(key, []),
                          c.NEW_SEEDS, c.DRAWS_PER_SEED_3C)
        rec = _prov(rung, size, mode, seeds=c.NEW_SEEDS,
                    dps=c.DRAWS_PER_SEED_3C, k_total=c.K_NEW)
        rec["per_seed_tallies"] = independent_tallies(rows, answers,
                                                      labels, c.NEW_SEEDS)
        _write_cell(Path(root) / "results" / "sampling"
                    / f"{size}_trained", rung, rec, rows)
    for key in c.GATE1_CELLS:
        rung, size, _mode = key
        dps = a3.DRAWS_PER_SEED[rung]
        rec = gate1_record(
            rung, size, n_items=N, dps=dps,
            diffs=list(gate1_diffs.get(key, [])),
            committed_gz_sha=f"committed-gz-{rung}-{size}",
            items_sha=f"items-{rung}", model_sha=f"synthetic-{size}",
            stack={"torch": "synthetic", "transformers": "synthetic"})
        p = (Path(root) / "results" / "gate1" / f"{size}_trained"
             / f"{rung}.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec))


def build_referent(exp3_fires) -> dict:
    """The exp3-side expectations, from the same spec the tree was
    written from — the role run() fills from the sha-pinned committed
    verdict record."""
    fires_table = {}
    for key in a3.SAMPLING_CELLS:
        rung, _size, _mode = key
        dps = a3.DRAWS_PER_SEED[rung]
        fires_table[c._key(key)] = {
            "full_string_total": len(exp3_fires.get(key, [])),
            "n_draws": N * dps * len(a3.SEEDS)}
    addresses, lengths = {}, {}
    for key in c.SCORED_CELLS:
        rung = key[0]
        _labels, answers = rung_items(rung)
        addrs = sorted(exp3_fires.get(key, []))
        addresses[c._key(key)] = [{"item": i, "seed": s, "draw": d}
                                  for (i, s, d) in addrs]
        lengths[c._key(key)] = [len(answers[i]) for (i, _s, _d) in addrs]
    return {"fires": fires_table, "fire_addresses": addresses,
            "fire_answer_lengths": lengths}


DEFAULT_EXP3_FIRES = {
    # the committed shape in miniature: ONE fire at the fired cell
    # (a length-4 item under the synthetic strata: item 3), walls and
    # every twin silent, both controls modestly loud
    c.FIRED_CELL: [(3, 0, 6)],
    (a3.POSITIVE_CONTROL, "410m", "trained"): [(0, 0, 0), (1, 1, 2)],
    (a3.POSITIVE_CONTROL, "1b", "trained"): [(0, 2, 1)],
    (a3.MATCHED_CONTROL, "410m", "trained"): [(2, 3, 4)],
    (a3.MATCHED_CONTROL, "1b", "trained"): [(4, 1, 7)],
}


def write_world(root: Path, *, exp3_fires=None, new_fires=None,
                gate1_diffs=None, leak_items=None) -> dict:
    """Both trees plus the loader-side context verdict_3c needs.
    Returns the kwargs for run_battery."""
    exp3_fires = {**DEFAULT_EXP3_FIRES, **(exp3_fires or {})}
    new_fires = new_fires or {}
    gate1_diffs = gate1_diffs or {}
    leak_items = leak_items or {}
    root = Path(root)
    write_exp3_tree(root / "exp3", exp3_fires)
    write_3c_tree(root / "exp3c", new_fires, gate1_diffs)
    prompts = {}
    for rung in c.REVERSAL_RUNGS:
        _labels, answers = rung_items(rung)
        prompts[rung] = prompts_for(rung, answers,
                                    leak_items.get(rung, ()))
    return {"root": root,
            "referent": build_referent(exp3_fires),
            "prompts": prompts,
            "sha_refs": {r: f"items-{r}" for r in a3.RUNGS}}


def run_battery(root, referent, prompts, sha_refs) -> dict:
    """End to end through the frozen loaders of both trees."""
    import harness

    verify_fn = harness.verify
    exp3_cells = a3.load_sampling_cells(Path(root) / "exp3",
                                        verify_fn=verify_fn)
    addresses = c.extract_fire_addresses(Path(root) / "exp3", exp3_cells,
                                         verify_fn=verify_fn)
    return c.verdict_3c(
        c.load_new_cells(Path(root) / "exp3c", verify_fn=verify_fn),
        c.load_gate1_records(Path(root) / "exp3c"),
        exp3_cells,
        exp3_referent=referent,
        exp3_fire_addresses=addresses,
        prompts=prompts,
        sha_refs=sha_refs)


def run_world(base, name, spec) -> dict:
    kw = write_world(Path(base) / name, **spec.get("world", {}))
    return run_battery(**kw)


# ------------------------------------------------------- the batteries
#
# Every terminal of design §6, plus the disclosed-but-not-fatal
# provisions. `check` callables assert the world's own provision on
# the verdict record. Synthetic strata note: reverse_string item 0 is
# length 4, item 1 length 5, item 3 length 4.

PLANTED_DIFFS = [
    {"item": 2, "seed": 0, "draw": 5, "got": " drifted",
     "committed": FILLER},
    {"item": 7, "seed": 0, "draw": 0, "got": " x", "committed": FILLER},
    {"item": 19, "seed": 0, "draw": 63, "got": "", "committed": FILLER},
]

BATTERIES = {
    # ---- the four worlds ----
    "lone_draw": {
        "world": {},
        "expect": "LONE-DRAW",
        "check": [
            # the frozen reading: existence stands, stated plainly
            lambda out: "STANDS" in out["reason"],
            lambda out: "resolving power" in out["reason"],
            # pooled table keeps exp3's fire at the fired cell
            lambda out: out["pooled"]["reverse_string/1b/trained"]
            ["count"] == 1,
            lambda out: out["pooled"]["reverse_string/1b/trained"]
            ["n_draws"] == N * c.K_POOLED,
            # every zero ships as a CP bound
            lambda out: 0 < out["fires"]["rev_string7/410m/trained"]
            ["new"]["cp95_upper"] < 1e-3,
            # the luck floor is printed beside the rates (reading 2)
            lambda out: abs(out["luck_floor_by_length"]["4"] - 2.19e-6)
            < 1e-8,
            lambda out: "26^-4" in out["reason"],
            # gate-1 volume: 4 cells × 20×64 + 20×8 (reading 1)
            lambda out: out["gate1_total_draws_compared"] == 5280,
            # strata carry their own floors and bounds
            lambda out: out["strata"]["reverse_string/1b/trained"]["4"]
            ["pooled"]["count"] == 1,
            lambda out: out["strata"]["rev_string7/1b/trained"]["7"]
            ["luck_floor"] < 1e-9,
            # the twin citation is live-computed from the loaded tree
            lambda out: out["twin_record"]["reversal_twin_draws"]
            == 4 * N * 256,
        ]},
    "replicates": {
        # two new fires at the fired cell: a length-4 item (0) on seed
        # 4 and a length-5 item (1) on seed 7's last draw
        "world": {"new_fires": {c.FIRED_CELL: [(0, 4, 0), (1, 7, 63)]}},
        "expect": "REPLICATES",
        "check": [
            lambda out: "stable nonzero rate" in out["reason"],
            lambda out: out["fires"]["reverse_string/1b/trained"]
            ["new"]["count"] == 2,
            lambda out: "ci95" in out["fires"]
            ["reverse_string/1b/trained"]["new"],
            lambda out: out["pooled"]["reverse_string/1b/trained"]
            ["count"] == 3,
            # per-seed spread visible with any fire
            lambda out: out["fires"]["reverse_string/1b/trained"]
            ["per_seed_full_string"]["4"] == 1,
            lambda out: out["fires"]["reverse_string/1b/trained"]
            ["per_seed_full_string"]["7"] == 1,
            # strata: the length-4 and length-5 strata each carry one
            # new fire; length 6 stays a bound
            lambda out: out["strata"]["reverse_string/1b/trained"]["4"]
            ["new"]["count"] == 1,
            lambda out: out["strata"]["reverse_string/1b/trained"]["5"]
            ["new"]["count"] == 1,
            lambda out: "cp95_upper" in out["strata"]
            ["reverse_string/1b/trained"]["6"]["new"],
            # every fired draw disclosed verbatim with its address
            lambda out: out["fires"]["reverse_string/1b/trained"]
            ["addresses"][0]["text"].strip()
            == out["fires"]["reverse_string/1b/trained"]["addresses"][0]
            ["answer"],
        ]},
    "deepens": {
        "world": {"new_fires": {c.FIRED_CELL: [(0, 4, 0)],
                                ("rev_string7", "410m", "trained"):
                                    [(2, 15, 63)]}},
        "expect": "DEEPENS",
        "check": [
            lambda out: "load-bearing" in out["reason"],
            lambda out: out["adjudication"]["fired_again"] is True,
            lambda out: out["adjudication"]["any_wall_fired"] is True,
            lambda out: out["adjudication"]["wall_new_fires"]
            ["rev_string7/410m/trained"] == 1,
        ]},
    "relocates": {
        "world": {"new_fires": {("reverse_string", "410m", "trained"):
                                [(0, 5, 3)]}},
        "expect": "RELOCATES",
        "check": [
            lambda out: "revises downward" in out["reason"],
            lambda out: out["adjudication"]["fired_again"] is False,
            # exp3's fire is not retracted: the pooled fired-cell
            # count keeps it
            lambda out: out["pooled"]["reverse_string/1b/trained"]
            ["count"] == 1,
            lambda out: out["fires"]["reverse_string/410m/trained"]
            ["new"]["count"] == 1,
        ]},
    # ---- INSUFFICIENT_DATA route 1: gate-1 stream drift ----
    "id_gate1": {
        "world": {"gate1_diffs": {("reverse_string", "410m", "trained"):
                                  PLANTED_DIFFS},
                  # fires exist and are still disclosed behind the gate
                  "new_fires": {c.FIRED_CELL: [(0, 4, 0)]}},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "gate 1",
        "check": [
            lambda out: out["gate1"]["reverse_string/410m/trained"]
            ["n_diffs"] == 3,
            # differing draws disclosed verbatim, addresses intact
            lambda out: out["gate1"]["reverse_string/410m/trained"]
            ["diffs"][0]["got"] == " drifted",
            lambda out: out["gate1"]["reverse_string/410m/trained"]
            ["diffs"][2]["draw"] == 63,
            # everything else computed BEFORE the branch (disclosure
            # cannot be hidden by the gate)
            lambda out: out["fires"]["reverse_string/1b/trained"]
            ["new"]["count"] == 1,
            lambda out: "pooled" in out and "strata" in out,
        ]},
    # ---- INSUFFICIENT_DATA route 2: every observed fire void ----
    "id_all_void": {
        "world": {"new_fires": {c.FIRED_CELL: [(0, 4, 0)],
                                ("rev_string7", "410m", "trained"):
                                    [(5, 6, 2)]},
                  "leak_items": {"reverse_string": (0,),
                                 "rev_string7": (5,)}},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "void",
        "check": [
            lambda out: len(out["leak_voids"]) == 2,
            lambda out: all(v["void"] for v in out["leak_voids"]),
            lambda out: out["fires"]["reverse_string/1b/trained"]
            ["new"]["count"] == 0,
            lambda out: out["fires"]["reverse_string/1b/trained"]
            ["raw_fire_count_pre_void"] == 1,
        ]},
    # ---- leak-void discloses and proceeds ----
    "void_discloses_and_proceeds": {
        # two fired-cell fires, ONE leaked: adjudication proceeds on
        # the survivor and the world is REPLICATES with the void its
        # own finding
        "world": {"new_fires": {c.FIRED_CELL: [(0, 4, 0), (1, 7, 63)]},
                  "leak_items": {"reverse_string": (0,)}},
        "expect": "REPLICATES",
        "check": [
            lambda out: len(out["leak_voids"]) == 1,
            lambda out: out["leak_voids"][0]["item"] == 0,
            lambda out: out["fires"]["reverse_string/1b/trained"]
            ["new"]["count"] == 1,
            lambda out: out["fires"]["reverse_string/1b/trained"]
            ["raw_fire_count_pre_void"] == 2,
            # void exclusion is per ADDRESS: the length-4 stratum
            # loses its (voided) fire, length 5 keeps its clean one
            lambda out: out["strata"]["reverse_string/1b/trained"]["4"]
            ["new"]["count"] == 0,
            lambda out: out["strata"]["reverse_string/1b/trained"]["5"]
            ["new"]["count"] == 1,
            # pooled counts non-void new + exp3's committed
            lambda out: out["pooled"]["reverse_string/1b/trained"]
            ["count"] == 2,
        ]},
    # ---- the pre-void mutant killer: fired cell's only fire is
    # void, a wall fires clean → RELOCATES (a tree reading pre-void
    # counts would say DEEPENS) ----
    "fired_void_wall_clean": {
        "world": {"new_fires": {c.FIRED_CELL: [(0, 4, 0)],
                                ("rev_string7", "410m", "trained"):
                                    [(5, 6, 2)]},
                  "leak_items": {"reverse_string": (0,)}},
        "expect": "RELOCATES",
        "check": [
            lambda out: len(out["leak_voids"]) == 1,
            lambda out: out["adjudication"]["fired_again"] is False,
            lambda out: out["adjudication"]["any_wall_fired"] is True,
            # the fired flag reflects NON-VOID fires, like the count
            lambda out: out["fires"]["reverse_string/1b/trained"]
            ["fired"] is False,
        ]},
}


def run_all(base: Path) -> dict:
    out = {}
    for name, spec in BATTERIES.items():
        out[name] = run_world(base, name, spec)
    return out


if __name__ == "__main__":
    import tempfile

    base = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        Path(tempfile.mkdtemp(prefix="exp3c_full_shape_"))
    results = run_all(base)
    ok = True
    for name, spec in BATTERIES.items():
        v = results[name]
        good = (v["verdict"] == spec["expect"]
                and spec.get("expect_reason", "") in v.get("reason", "")
                and all(chk(v) for chk in spec.get("check", [])))
        ok &= good
        print(f"{'ok  ' if good else 'FAIL'} {name}: {v['verdict']}")
    print("ALL TERMINAL BRANCHES REACHED" if ok else
          "FULL-SHAPE RUN FAILED")
    sys.exit(0 if ok else 1)
