"""Exp 3c runner: one cell of one kind — gate1 | sampling.

Two cell kinds, one dtype (design §3: fp32 exact upcast, exp3's
ledgered policy unchanged, probe sizes only, trained only):

- gate1: byte re-derivation of exp3's committed seed-0 stream
  (rederive.py; the record is the comparison, the draws are discarded).
- sampling: the NEW draws — seeds 4–15, 64 draws per seed per item,
  T = 1.0 untruncated, MAX_NEW_TOKENS 12, 16-row chunks — exp3's
  frozen sampler driven at 3c's committed seed set, every raw draw
  stored, per-seed convenience tallies beside them (the analyzer
  recomputes and refuses disagreement).

Everything frozen is imported from the exp3/2c/2b trees, never copied
(design §11): the sampler, the prompt rendering, the model loader, the
provenance asserts. Records carry the same provenance block exp3's
carried, with 3c's seed fields. NOTHING here runs before tag
`exp3c-preregistered` except the freeze session's single-cell gate-1
rehearsal (design §10.2).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXP3C = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP3C.parent

# ORDER MATTERS AND IS NOT COSMETIC (exp3's runner, verbatim
# reasoning): exp2c must win the `harness` name; exp2b supplies
# `models`.
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))

from experiments.exp3.analyze_3 import score_first_char  # noqa: E402
from experiments.exp3.run.run_cell import (  # noqa: E402
    _assert_module_provenance, _load_model, _provenance, load_capability,
    write_draws,
)
from experiments.exp3.sampler import sample_item  # noqa: E402
from experiments.exp3c import rederive  # noqa: E402
from experiments.exp3c.analyze_3c import (  # noqa: E402
    DRAWS_PER_SEED_3C, GATE1_CELLS, K_NEW, NEW_SEEDS, REVERSAL_RUNGS,
    SCORED_CELLS, check_frozen_imports, load_verify_3c,
)

KINDS = ("gate1", "sampling")

# gate-1 covers the four scored cells + ctrl_copy at 1b only (§3)
GATE1_RUNGS = {"410m": tuple(r for (r, s, _m) in GATE1_CELLS
                             if s == "410m"),
               "1b": tuple(r for (r, s, _m) in GATE1_CELLS if s == "1b")}
SAMPLING_RUNGS = REVERSAL_RUNGS


def record_path(out_root, kind: str, rung: str, size: str) -> Path:
    return (Path(out_root) / "results" / kind / f"{size}_trained"
            / f"{rung}.json")


def draws_path(out_root, rung: str, size: str) -> Path:
    return (Path(out_root) / "results" / "sampling" / f"{size}_trained"
            / f"{rung}.draws.jsonl.gz")



def per_seed_tallies_3c(rows, answers, labels, *, answer_type, seeds,
                        verify_fn) -> dict:
    """exp3's per_seed_tallies (run_cell.py), verbatim plain loop, with
    STOP #1's total verify passed in instead of the partial
    harness.verify — the convenience tallies stored beside the raw
    draws. Kept as a SEPARATE implementation from the analyzer's
    tally_with_addresses so the stored-vs-recompute agreement check
    still crosses two implementations (full_shape's rule)."""
    out = {str(s): {"full_string": 0, "first_char": 0, "n_draws": 0}
           for s in seeds}
    for row in rows:
        i = row["item"]
        for s in seeds:
            key = str(s)
            if key not in row["draws"]:
                raise ValueError(f"item {i} carries no stream for seed {s}")
            for d in row["draws"][key]:
                out[key]["n_draws"] += 1
                if verify_fn(d, answers[i], answer_type):
                    out[key]["full_string"] += 1
                if score_first_char(d, labels[i]):
                    out[key]["first_char"] += 1
    return out


def run_gate1_cell(rung, size, out_root=EXP3C, model_ctx=None) -> dict:
    return rederive.rederive_cell(rung, size, out_root=out_root,
                                  model_ctx=model_ctx)


def run_sampling_cell_3c(rung, size, out_root=EXP3C,
                         model_ctx=None) -> dict:
    """One scored cell's NEW draws: seeds 4–15 through exp3's frozen
    sampler, raw streams written beside the record, skip-if-exists."""
    out = record_path(out_root, "sampling", rung, size)
    dpath = draws_path(out_root, rung, size)
    if out.exists() and dpath.exists():
        return json.loads(out.read_text())
    check_frozen_imports()
    _assert_module_provenance()
    from harness import render_prompt  # noqa: PLC0415 — 2c's, asserted

    if (rung, size, "trained") not in SCORED_CELLS:
        raise ValueError(f"{rung}/{size} is not a 3c scored cell")
    cap, items_path = load_capability(rung)
    shots = [tuple(s) for s in cap["shots"]][:2]
    tok, model, sha = model_ctx if model_ctx else \
        _load_model(size, "trained", "float32")
    terminal = tuple(sorted(set(tok.all_special_ids)))

    rows = []
    for i, it in enumerate(cap["eval_items"]):
        prompt = render_prompt(it["question"], shots)
        got = sample_item(model, tok, prompt, rung=rung, size=size,
                          mode="trained", item_idx=i, seeds=NEW_SEEDS,
                          draws_per_seed=DRAWS_PER_SEED_3C,
                          terminal_ids=terminal)
        rows.append({"item": i,
                     "draws": {str(s): got[s] for s in NEW_SEEDS}})
        if (i + 1) % 50 == 0:
            print(f"[3c] {rung}/{size}: {i + 1}/{len(cap['eval_items'])} "
                  f"items sampled", flush=True)
    write_draws(dpath, rows)

    prov = _provenance(rung, size, "trained", cap, items_path,
                       "float32", sha)
    tallies = per_seed_tallies_3c(rows, prov["answers"],
                                  prov["probe_labels"],
                                  answer_type=cap["answer_type"],
                                  seeds=NEW_SEEDS,
                                  verify_fn=load_verify_3c())
    rec = {**prov,
           "seeds": list(NEW_SEEDS),
           "draws_per_seed": DRAWS_PER_SEED_3C,
           "k_total": K_NEW,
           "per_seed_tallies": tallies,
           "draws_file": dpath.name}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    fires = sum(v["full_string"] for v in tallies.values())
    print(f"[3c] {rung}/{size}: sampling cell done — "
          f"{fires} verified full-string fire(s) in "
          f"{sum(v['n_draws'] for v in tallies.values())} new draws",
          flush=True)
    return rec


RUN = {"gate1": run_gate1_cell, "sampling": run_sampling_cell_3c}
TIER_RUNGS = {"gate1": GATE1_RUNGS,
              "sampling": {s: SAMPLING_RUNGS for s in ("410m", "1b")}}


def run_tier(kind: str, size: str, out_root=EXP3C) -> list:
    """All of one (kind, size) tier's cells in THIS process — one model
    load, cells sequential, skip-if-exists. The process boundary is
    the driver's job (tier-per-process, exp3's allocator lesson)."""
    if kind not in KINDS:
        raise ValueError(f"unknown 3c cell kind {kind!r}")
    check_frozen_imports()
    _assert_module_provenance()
    ctx = _load_model(size, "trained", "float32")
    out = []
    for rung in TIER_RUNGS[kind][size]:
        r = RUN[kind](rung, size, out_root=out_root, model_ctx=ctx)
        print(f"[3c] {kind}/{size}/{rung} done", flush=True)
        out.append(r)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--tier":
        run_tier(sys.argv[2], sys.argv[3])
    else:
        kind, rung, size = sys.argv[1:4]
        RUN[kind](rung, size)
