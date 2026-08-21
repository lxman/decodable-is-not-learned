"""Exp 3e runner: one cell of one kind — gate1 | sampling.

Two cell kinds, one dtype (exp3's ledgered policy: probe-size sampling
is fp32 exact upcast), trained only, reverse_string only, the 45-item
SUBSET only (§3):

- gate1: byte re-derivation of 3d's committed gate-1 seed streams on
  the 45 items through THIS module's production path (rederive_3e.py;
  the record is the comparison, the draws are discarded).
- sampling: the NEW draws — seed BLOCKS of 16 (the durable,
  commit-per-block unit, §10.4: 46,080 draws), 64 draws per seed per
  item, T = 1.0 untruncated, MAX_NEW_TOKENS 12, 16-row chunks —
  exp3's frozen sampler driven at 3e's committed seed sets on the
  subset's ORIGINAL item indices (so every substream is the one the
  stream map pins), every raw draw stored, per-seed convenience
  tallies beside them (the analyzer recomputes and refuses
  disagreement).

THE FROZEN ORDER IS EXECUTABLE (§10): every tier REFUSES to run until
the scorer known-answer gate record exists and reads PASS (no model
contact was needed to produce it); a sampling tier REFUSES to run
until, additionally, both gate-1 records exist with zero diffs. The
analyzer enforces the same rules on whatever exists.

Everything frozen is imported from the exp3/exp3c/exp3d/2c/2b trees,
never copied (§11). NOTHING here runs before tag `exp3e-preregistered`
except the freeze session's single-cell gate-1 rehearsal, on
Michael's word.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP3E = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP3E.parent

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
    _assert_module_provenance, _load_model, load_capability, write_draws,
)
from experiments.exp3.sampler import sample_item  # noqa: E402
from experiments.exp3c.analyze_3c import load_verify_3c  # noqa: E402
from experiments.exp3e import rederive_3e  # noqa: E402
from experiments.exp3e.analyze_3e import (  # noqa: E402
    DRAWS_PER_SEED_3E, ITEMS_SHA_PIN, K_BLOCK, RUNG, SEED_BLOCKS, SIZES_3E,
    SUBSET_ITEMS_PIN, SUBSET_SHA256_PIN, check_frozen_imports_3e,
    shard_name, subset_sha256,
)

KINDS = ("gate1", "sampling")


def sampling_record_path(out_root, size, block) -> Path:
    return (Path(out_root) / "results" / "sampling" / f"{size}_trained"
            / f"{shard_name(block)}.json")


def sampling_draws_path(out_root, size, block) -> Path:
    return (Path(out_root) / "results" / "sampling" / f"{size}_trained"
            / f"{shard_name(block)}.draws.jsonl.gz")


# ------------------------------------------- frozen-order preconditions

def scorer_gates_clean(out_root) -> tuple:
    p = Path(out_root) / "results" / "scorer_gates.json"
    if not p.exists():
        return False, "scorer known-answer gate record missing"
    rec = json.loads(p.read_text())
    if rec.get("passed") is not True or \
            rec.get("gate_a", {}).get("passed") is not True or \
            rec.get("gate_b", {}).get("passed") is not True:
        return False, ("the scorer known-answer gates did not pass — the "
                       "scorer is broken and nothing samples (§5.5)")
    return True, "scorer gates (a) and (b) PASS"


def gate1_clean(out_root) -> tuple:
    for size in SIZES_3E:
        p = rederive_3e.record_path(out_root, size)
        if not p.exists():
            return False, f"gate-1 record missing: {RUNG}/{size}"
        rec = json.loads(p.read_text())
        if rec.get("n_diffs") != 0:
            return False, (f"gate-1 diffs at {RUNG}/{size}: "
                           f"{rec.get('n_diffs')} differing draws — "
                           f"the generation law drifted; no new draw "
                           f"is interpretable")
    return True, "both gate-1 records exist with 0 diffs"


# ------------------------------------------------------- per-seed tallies

def per_seed_tallies_3e(rows, answers, labels, *, answer_type, seeds,
                        verify_fn) -> dict:
    """exp3's per_seed_tallies shape, plain loop, 3c's total verify —
    the convenience tallies stored beside the raw draws. Kept SEPARATE
    from the analyzer's tally_with_addresses so the stored-vs-recompute
    check still crosses two implementations. `answers`/`labels` are
    indexed by ORIGINAL item index."""
    out = {str(s): {"full_string": 0, "first_char": 0, "n_draws": 0}
           for s in seeds}
    for row in rows:
        i = row["item"]
        for s in seeds:
            key = str(s)
            if key not in row["draws"]:
                raise ValueError(f"item {i} carries no stream for "
                                 f"seed {s}")
            for dd in row["draws"][key]:
                out[key]["n_draws"] += 1
                if verify_fn(dd, answers[i], answer_type):
                    out[key]["full_string"] += 1
                if score_first_char(dd, labels[i]):
                    out[key]["first_char"] += 1
    return out


# ----------------------------------------------------------- cell kinds

def run_gate1_cell(size, out_root=EXP3E, model_ctx=None) -> dict:
    ok, why = scorer_gates_clean(out_root)
    if not ok:
        raise RuntimeError(f"§10 order violated: {why} — gate 1 runs only "
                           f"after both scorer gates PASS")
    return rederive_3e.rederive_cell_3e(size, out_root=out_root,
                                        model_ctx=model_ctx)


def run_sampling_block(size, block, out_root=EXP3E,
                       model_ctx=None) -> dict:
    """One seed block's NEW draws on the 45 items: 16 seeds through
    exp3's frozen sampler, raw streams written beside the record,
    skip-if-exists — the durable, resumable, commit-per-block unit."""
    out = sampling_record_path(out_root, size, block)
    dpath = sampling_draws_path(out_root, size, block)
    if out.exists() and dpath.exists():
        return json.loads(out.read_text())
    for check in (scorer_gates_clean, gate1_clean):
        ok, why = check(out_root)
        if not ok:
            raise RuntimeError(f"§10 order violated: {why}")
    check_frozen_imports_3e()
    _assert_module_provenance()
    from harness import render_prompt  # noqa: PLC0415 — 2c's, asserted

    if size not in SIZES_3E or tuple(block) not in SEED_BLOCKS[size]:
        raise ValueError(f"{size}/{block} is not a preregistered 3e "
                         f"seed block")
    cap, items_path = load_capability(RUNG)
    items_sha = hashlib.sha256(items_path.read_bytes()).hexdigest()
    if items_sha != ITEMS_SHA_PIN[RUNG]:
        raise ValueError(
            f"item file {items_path} has sha256 {items_sha} against "
            f"the §4 pin {ITEMS_SHA_PIN[RUNG]} — these are not the "
            f"committed items")
    if subset_sha256(SUBSET_ITEMS_PIN) != SUBSET_SHA256_PIN:
        raise ValueError("the subset literal does not hash to its pin")
    shots = [tuple(s) for s in cap["shots"]][:2]
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    labels = [str(it["probe_label"]) for it in cap["eval_items"]]
    tok, model, model_sha = model_ctx if model_ctx else \
        _load_model(size, "trained", "float32")
    terminal = tuple(sorted(set(tok.all_special_ids)))

    items = [int(i) for i in SUBSET_ITEMS_PIN]
    rows = []
    for j, i in enumerate(items):
        it = cap["eval_items"][i]
        prompt = render_prompt(it["question"], shots)
        got = sample_item(model, tok, prompt, rung=RUNG, size=size,
                          mode="trained", item_idx=i, seeds=tuple(block),
                          draws_per_seed=DRAWS_PER_SEED_3E,
                          terminal_ids=terminal)
        rows.append({"item": i,
                     "draws": {str(s): got[s] for s in block}})
        if (j + 1) % 15 == 0:
            print(f"[3e] {size} s{block[0]}-s{block[-1]}: {j + 1}/"
                  f"{len(items)} items sampled", flush=True)
    write_draws(dpath, rows)

    tallies = per_seed_tallies_3e(rows, answers, labels,
                                  answer_type=cap["answer_type"],
                                  seeds=tuple(block),
                                  verify_fn=load_verify_3c())
    import torch          # noqa: PLC0415
    import transformers   # noqa: PLC0415
    rec = {"rung": RUNG, "size": size, "mode": "trained",
           "n_items": len(items), "items": items,
           "subset_sha256": subset_sha256(items),
           "answers": [answers[i] for i in items],
           "probe_labels": [labels[i] for i in items],
           "answer_type": cap["answer_type"],
           "items_sha256": items_sha,
           "dtype": "float32", "untrained_seed": None,
           "model_sha": model_sha,
           "stack": {"torch": torch.__version__,
                     "transformers": transformers.__version__},
           "seeds": list(block),
           "draws_per_seed": DRAWS_PER_SEED_3E,
           "k_total": K_BLOCK,
           "per_seed_tallies": tallies,
           "draws_file": dpath.name}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    fires = sum(v["full_string"] for v in tallies.values())
    print(f"[3e] {size} s{block[0]}-s{block[-1]}: block done — "
          f"{fires} verified full-string fire(s) in "
          f"{sum(v['n_draws'] for v in tallies.values())} new draws",
          flush=True)
    return rec


def run_tier(kind: str, size: str, out_root=EXP3E) -> list:
    """All of one (kind, size) tier's cells in THIS process — one
    model load, cells sequential, skip-if-exists. The process boundary
    is the driver's job (tier-per-process, exp3's allocator lesson)."""
    if kind not in KINDS:
        raise ValueError(f"unknown 3e cell kind {kind!r}")
    check_frozen_imports_3e()
    _assert_module_provenance()
    # preconditions checked BEFORE the model loads, so a refused tier
    # costs nothing
    checks = [scorer_gates_clean] + ([gate1_clean] if kind == "sampling"
                                     else [])
    for check in checks:
        ok, why = check(out_root)
        if not ok:
            raise RuntimeError(f"§10 order violated: {why}")
    ctx = _load_model(size, "trained", "float32")
    out = []
    if kind == "gate1":
        out.append(run_gate1_cell(size, out_root=out_root, model_ctx=ctx))
    else:
        for block in SEED_BLOCKS[size]:
            out.append(run_sampling_block(size, block, out_root=out_root,
                                          model_ctx=ctx))
    print(f"[3e] {kind}/{size} tier done", flush=True)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--tier":
        run_tier(sys.argv[2], sys.argv[3])
    else:
        kind, size = sys.argv[1:3]
        if kind == "sampling":
            block = tuple(int(x) for x in sys.argv[3].split(","))
            run_sampling_block(size, block)
        else:
            run_gate1_cell(size)
