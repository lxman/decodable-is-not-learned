"""The scorer's two known-answer gates (design §5.5, §10.2) — run on
COMMITTED BYTES ONLY, before any model contact, and committed as
`results/scorer_gates.json`. The runner refuses every tier while this
record is missing or failed; the analyzer validates the record AND
recomputes both gates from the same bytes at verdict time.

(a) target = answer: scoring the committed exp3/3c/3d draws for the
    45 items reproduces the 19 committed repeat-class fire addresses
    EXACTLY — no more, no fewer, same (item, seed, draw).
(b) target = the copy answer: scoring ctrl_copy's committed T = 1.0
    draws reproduces 12787/16000 (410m) and 13460/16000 (1b) EXACTLY
    (the same computation exp3 committed, so equality is the bar).

A record that fails is still written — the failure IS the disclosure
— and nothing downstream runs on it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXP3E = Path(__file__).resolve().parent
EXPERIMENTS = EXP3E.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))

from experiments.exp3 import analyze_3 as a3  # noqa: E402
from experiments.exp3d import analyze_3d as d  # noqa: E402
from experiments.exp3e import scorer_3e as sc  # noqa: E402
from experiments.exp3e.analyze_3e import (  # noqa: E402
    COMMITTED_DRAWS_SHA256, CTRL_SAMPLED_RATE_PIN, ITEMS_SHA_PIN,
    REPEAT_CLASS_FIRES_PIN, RUNG, SIZES_3E, SUBSET_ITEMS_PIN,
    check_frozen_imports_3e, committed_base_3e, load_committed_rows,
    subset_sha256,
)


def scorer_gate_record(base, *, fires_pin, ctrl_pin, meta) -> dict:
    """Both gates from a committed base (committed_base_3e's output):
    pure comparison, no I/O."""
    gate_a = {"addresses": {}, "expected": {}, "per_size_passed": {}}
    for size in SIZES_3E:
        got = base[size]["subset_addresses"]
        exp = [dict(a) for a in fires_pin[size]]
        gate_a["addresses"][size] = got
        gate_a["expected"][size] = exp
        gate_a["per_size_passed"][size] = bool(got == exp)
    gate_a["passed"] = all(gate_a["per_size_passed"].values())
    gate_a["rule"] = ("target = answer on the committed exp3/3c/3d draws "
                      "of the 45 items reproduces the committed "
                      "repeat-class fire addresses exactly")
    gate_b = {"counts": {}, "expected": {}, "per_size_passed": {}}
    for size in SIZES_3E:
        got = dict(base["ctrl_gate_b"][size])
        exp = dict(ctrl_pin[size])
        gate_b["counts"][size] = got
        gate_b["expected"][size] = exp
        gate_b["per_size_passed"][size] = bool(got == exp)
    gate_b["passed"] = all(gate_b["per_size_passed"].values())
    gate_b["rule"] = ("target = the copy answer on ctrl_copy's committed "
                      "T = 1.0 draws reproduces the committed verified "
                      "counts exactly")
    return {"gate_a": gate_a, "gate_b": gate_b,
            "passed": bool(gate_a["passed"] and gate_b["passed"]),
            "subset_n_draws_scored": {
                s: len(SUBSET_ITEMS_PIN) * base[s]["n_draws_per_item"]
                if s in base else None for s in SIZES_3E},
            **meta}


def write_record(rec, out_root=EXP3E) -> Path:
    p = Path(out_root) / "results" / "scorer_gates.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1))
    return p


def run_scorer_gates(out_root=EXP3E) -> dict:
    """The real thing: committed trees, §4 pins, no model."""
    check_frozen_imports_3e()
    items = d.load_item_file(RUNG)
    ctrl = d.load_item_file(a3.POSITIVE_CONTROL)
    rows = load_committed_rows()
    base = committed_base_3e(rows, items["answers"], items["answer_type"],
                             sc.load_scorer(),
                             ctrl_answers=ctrl["answers"],
                             ctrl_answer_type=ctrl["answer_type"])
    rec = scorer_gate_record(
        base, fires_pin=REPEAT_CLASS_FIRES_PIN, ctrl_pin=CTRL_SAMPLED_RATE_PIN,
        meta={"items_sha256": dict(ITEMS_SHA_PIN),
              "subset_items": list(SUBSET_ITEMS_PIN),
              "subset_sha256": subset_sha256(SUBSET_ITEMS_PIN),
              "committed_draws_sha256": COMMITTED_DRAWS_SHA256,
              "answer_type": {RUNG: items["answer_type"],
                              a3.POSITIVE_CONTROL: ctrl["answer_type"]},
              "model_contact": False})
    p = write_record(rec, out_root)
    print(f"[3e scorer gates] gate (a) {'PASS' if rec['gate_a']['passed'] else 'FAIL'}"
          f" — {sum(len(v) for v in rec['gate_a']['addresses'].values())}"
          f" addresses reproduced; gate (b) "
          f"{'PASS' if rec['gate_b']['passed'] else 'FAIL'} — "
          f"{rec['gate_b']['counts']}; record {p}", flush=True)
    return rec


if __name__ == "__main__":
    r = run_scorer_gates()
    sys.exit(0 if r["passed"] else 1)
