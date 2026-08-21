"""Synthetic full-shape 2d trees for the freeze rule: the frozen
verdict tree must be EXECUTED to every terminal — PASS, FAIL,
INDETERMINATE, INSUFFICIENT_DATA (gate-1 drift) — end to end through
the frozen loaders, before the tag.

Each world is a complete on-disk 2d tree in the runner's own layout:
pilot + main record/draws pairs for all 34 rungs × 2 sizes, the four
gate-1 records, 68 argmax records and power_2d.json. The OUTCOME is
never synthetic — it is 2c's committed, known record, loaded through
the same sha-pinned path as production. The PREDICTOR is synthetic:
each (rung, size) gets a verified count; the builder writes that many
draws equal to the rung's answer and fills the rest with a string no
answer type verifies. The two reversal rungs' main streams are
exp3's COMMITTED seed-0 bytes (copied row for row), so gate 1 on the
synthetic tree is the real comparison; the drift world mutates one
draw. Stored tallies are computed HERE with 2c's verify in a plain
loop, independently of the analyzer's recompute.
"""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

EXP2D = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2D.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))

from experiments.exp2d import analyze_2d as a  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import rederive_2d as rd  # noqa: E402
from experiments.exp3.run.run_cell import read_draws  # noqa: E402

FILLER = " ~~"          # verifies for no answer type (normalizes to "~~")
FAKE_STACK = {"torch": "synthetic", "transformers": "synthetic"}

_BATTERY = None
_FLOORS = None
_OUTCOME = None
_COMMITTED_ROWS = {}


def battery():
    global _BATTERY, _FLOORS
    if _BATTERY is None:
        _BATTERY = bt.load_battery()
        _FLOORS = bt.floor_table(_BATTERY)
    return _BATTERY, _FLOORS


def outcome():
    global _OUTCOME
    if _OUTCOME is None:
        _, floors = battery()
        _OUTCOME = a.load_outcome(floors)
    return _OUTCOME


def committed_rows(rung, size):
    key = (rung, size)
    if key not in _COMMITTED_ROWS:
        _, gz = rd.committed_shard_paths(rung, size)
        _COMMITTED_ROWS[key] = [
            {"item": r["item"], "draws": {"0": list(r["draws"]["0"])}}
            for r in read_draws(gz)]
    return _COMMITTED_ROWS[key]


# ------------------------------------------------------------- writers

def _model_sha(size):
    from models import PYTHIA_SHAS
    return PYTHIA_SHAS[size]


def synthetic_rows(cap, *, seed, dps, verified) -> list:
    """`verified` draws equal to the answer, spread over the first
    items one per item (then wrapping), rest FILLER."""
    n = len(cap["eval_items"])
    per_item = [0] * n
    for k in range(verified):
        per_item[k % n] += 1
    rows = []
    for i, it in enumerate(cap["eval_items"]):
        v = min(per_item[i], dps)
        draws = [str(it["answer"])] * v + [FILLER] * (dps - v)
        rows.append({"item": i, "draws": {str(seed): draws}})
    return rows


def write_sampling_cell(root, tier, size, rung, rows, *, verify) -> None:
    spec = a.TIERS[tier]
    cap, _ = battery()
    cap = cap[rung]
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    verified = sum(1 for row in rows for d in row["draws"][str(spec["seed"])]
                   if verify(d, answers[row["item"]], cap["answer_type"]))
    n_draws = sum(len(row["draws"][str(spec["seed"])]) for row in rows)
    rec = {"rung": rung, "size": size, "mode": a.MODE, "tier": tier,
           "n_items": len(rows), "answers": answers,
           "answer_type": cap["answer_type"], "n_shots": bt.N_SHOTS,
           "dtype": a.SAMPLING_DTYPE, "untrained_seed": None,
           "model_sha": _model_sha(size),
           "items_sha256": bt.ITEMS_SHA_PIN[rung],
           "stream_namespace": a.STREAM_NAMESPACE,
           "seeds": [spec["seed"]], "draws_per_seed": spec["draws_per_seed"],
           "k_total": spec["draws_per_seed"],
           "max_new_tokens": bt.max_new_tokens(rung),
           "temperature": 1.0, "truncation": "none",
           "per_seed_tallies": {str(spec["seed"]): {
               "full_string": int(verified), "n_draws": int(n_draws)}},
           "draws_file": f"{rung}.draws.jsonl.gz", "stack": FAKE_STACK}
    p = a.tier_record_path(root, tier, size, rung)
    g = a.tier_draws_path(root, tier, size, rung)
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(g, "wt") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    p.write_text(json.dumps(rec, indent=1))


def write_gate1(root, rung, size, rows, *, verify) -> dict:
    cap, _ = battery()
    cap = cap[rung]
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    cmp = rd.compare_rows(rung, size, rows, answers=answers,
                          answer_type=cap["answer_type"], verify_fn=verify)
    rec = rd.gate1_record_2d(rung, size, diffs=cmp["diffs"],
                             fires_reproduced=cmp["fires"],
                             committed_gz_sha=cmp["committed_gz_sha"],
                             items_sha=bt.ITEMS_SHA_PIN[rung],
                             model_sha=_model_sha(size), stack=FAKE_STACK)
    p = a.gate1_record_path(root, size, rung)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1))
    return rec


def write_argmax(root, size, rung, correct, *, verify) -> None:
    cap, _ = battery()
    cap = cap[rung]
    conts = [str(it["answer"]) if i < correct else FILLER
             for i, it in enumerate(cap["eval_items"])]
    got = sum(verify(c, str(it["answer"]), cap["answer_type"])
              for c, it in zip(conts, cap["eval_items"]))
    rec = {"rung": rung, "size": size, "mode": a.MODE, "tier": "argmax",
           "n_items": len(conts), "answer_type": cap["answer_type"],
           "n_shots": bt.N_SHOTS, "dtype": a.ARGMAX_DTYPE,
           "untrained_seed": None, "model_sha": _model_sha(size),
           "items_sha256": bt.ITEMS_SHA_PIN[rung],
           "max_new_tokens": bt.max_new_tokens(rung),
           "continuations": conts, "correct": int(got),
           "acc": got / len(conts), "redecode_diffs": None,
           "stack": FAKE_STACK}
    p = a.argmax_record_path(root, size, rung)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1))


def write_power(root, status="POWERED") -> None:
    rec = {"declared_status": status, "power": {"0.85": {"p_pass": 0.9}},
           "pilot_zero_set": {"z0": 0, "n0": 0}, "synthetic": True}
    (Path(root) / "power_2d.json").write_text(json.dumps(rec, indent=1))


# ------------------------------------------------------------- worlds

def build_world(root, *, main_verified, pilot_verified=None,
                argmax_correct=None, gate1_mutate=None,
                power_status="POWERED", run=True) -> dict:
    """main_verified: {(rung, size): verified count} for the main tier
    (reversal rungs ignored — committed bytes used); pilot_verified:
    same for pilot (default: main // 8); argmax_correct: {(rung,
    size): correct} (default 0); gate1_mutate: (rung, size) whose
    main stream gets one altered draw."""
    root = Path(root)
    verify = a.load_verify()
    caps, _ = battery()
    pilot_verified = pilot_verified or {}
    argmax_correct = argmax_correct or {}
    for size in a.PROBE_SIZES:
        for rung in a.RUNGS:
            if rung in a.REVERSAL_RUNGS:
                rows = [{"item": r["item"], "draws": {"0": list(r["draws"]["0"])}}
                        for r in committed_rows(rung, size)]
                if gate1_mutate == (rung, size):
                    rows[7]["draws"]["0"][11] = rows[7]["draws"]["0"][11] + "!"
                write_sampling_cell(root, "main", size, rung, rows,
                                    verify=verify)
                write_gate1(root, rung, size, rows, verify=verify)
                prow = synthetic_rows(caps[rung], seed=100, dps=8,
                                      verified=pilot_verified.get(
                                          (rung, size), 0))
            else:
                v = int(main_verified.get((rung, size), 0))
                rows = synthetic_rows(caps[rung], seed=0, dps=64, verified=v)
                write_sampling_cell(root, "main", size, rung, rows,
                                    verify=verify)
                prow = synthetic_rows(caps[rung], seed=100, dps=8,
                                      verified=int(pilot_verified.get(
                                          (rung, size), v // 8)))
            write_sampling_cell(root, "pilot", size, rung, prow,
                                verify=verify)
            write_argmax(root, size, rung, int(argmax_correct.get(
                (rung, size), 0)), verify=verify)
    write_power(root, power_status)
    return a.run(root) if run else {}


def rising_rungs():
    o = outcome()
    return [r for r in a.RUNGS if o["rungs"][r]["rising"]]


def flat_rungs():
    o = outcome()
    return [r for r in a.RUNGS if not o["rungs"][r]["rising"]]


def counts_for(rate_by_rung) -> dict:
    """{rung: rate} → {(rung, size): verified} over 32,000 draws."""
    return {(r, s): int(round(rate * a.MAIN_DRAWS_PER_RUNG))
            for r, rate in rate_by_rung.items() for s in a.PROBE_SIZES}


def world_specs() -> list:
    """(name, build_world kwargs, expected verdict). Rates are chosen
    against the REAL floors: a rung clears its floor only with a rate
    comfortably above it at 32,000 draws."""
    _, floors = battery()
    ris, fla = rising_rungs(), flat_rungs()
    specs = []
    # W1 PASS: every rising rung far above its floor, every flat rung
    # at zero (the ladder story in its strongest form)
    specs.append(("W1 PASS clean separation",
                  {"main_verified": counts_for(
                      {r: floors[r]["floor"] + 0.2 for r in ris}),
                   "argmax_correct": {(r, "1b"): 0 for r in a.RUNGS}},
                  "PASS"))
    # W2 FAIL: predictor independent of the label — a handful of flat
    # rungs above floor, rising rungs at zero except two
    specs.append(("W2 FAIL predictor uninformative",
                  {"main_verified": counts_for(
                      {**{r: floors[r]["floor"] + 0.2 for r in fla[:6]},
                       **{r: floors[r]["floor"] + 0.2 for r in ris[:2]}})},
                  "FAIL"))
    # W3 INDETERMINATE: CI excludes .5 but AUC < .75 and block p ≥ .01
    # — six rising rungs above floor, one per family across six
    # families (so almost every family resample carries a rising
    # positive), the other seven rising rungs tied at zero with the flat
    six = ["sub3_mid", "antonym", "arith_next", "count_div13", "median5",
           "odd6"]
    specs.append(("W3 INDETERMINATE partial separation",
                  {"main_verified": counts_for(
                      {r: floors[r]["floor"] + 0.2 for r in six})},
                  "INDETERMINATE"))
    # W4 INSUFFICIENT_DATA: one altered draw in a reversal main stream
    specs.append(("W4 INSUFFICIENT_DATA gate-1 drift",
                  {"main_verified": counts_for(
                      {r: floors[r]["floor"] + 0.2 for r in ris}),
                   "gate1_mutate": ("reverse_string", "1b")},
                  "INSUFFICIENT_DATA"))
    return specs
