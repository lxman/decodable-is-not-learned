"""Exp 3d runner: one cell of one kind — gate1 | scoring | sampling.

Three cell kinds, one dtype (exp3's ledgered policy: probe-size
sampling and scoring are fp32 exact upcast; the design doc's §3
'fp16' is a ledgered slip, PROGRESS.md), trained only, reverse_string
only (rev_string7 EXCLUDED with bounds standing, §3):

- gate1: byte re-derivation of 3c's committed seed-8 stream
  (rederive_3d.py; the record is the comparison, the draws are
  discarded).
- scoring: the teacher-forced canonical-path pass (scoring_3d.py) —
  reverse_string + ctrl_copy, committed BEFORE any tranche draw.
- sampling: the NEW draws — seed BLOCKS of 4 (the durable,
  commit-per-block unit, §10.4), 64 draws per seed per item,
  T = 1.0 untruncated, MAX_NEW_TOKENS 12, 16-row chunks — exp3's
  frozen sampler driven at 3d's committed seed sets, every raw draw
  stored, per-seed convenience tallies beside them (the analyzer
  recomputes and refuses disagreement).

THE FROZEN ORDER IS EXECUTABLE (§10): a scoring tier REFUSES to run
until both gate-1 records exist with zero diffs; a sampling tier
REFUSES to run until, additionally, all four scoring records exist
and both ctrl_copy known-answer gates read PASS. The analyzer
enforces the same rules on whatever exists.

Everything frozen is imported from the exp3/exp3c/2c/2b trees, never
copied (§11). NOTHING here runs before tag `exp3d-preregistered`
except the freeze session's single-cell gate-1 rehearsal (§10.2).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP3D = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP3D.parent

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
from experiments.exp3d import rederive_3d, scoring_3d  # noqa: E402
from experiments.exp3d.analyze_3d import (  # noqa: E402
    DRAWS_PER_SEED_3D, ITEMS_SHA_PIN, K_BLOCK, RUNG, SCORING_RUNGS,
    SEED_BLOCKS, SIZES_3D, check_frozen_imports_3d, shard_name,
)

KINDS = ("gate1", "scoring", "sampling")


def sampling_record_path(out_root, size, block) -> Path:
    return (Path(out_root) / "results" / "sampling" / f"{size}_trained"
            / f"{shard_name(block)}.json")


def sampling_draws_path(out_root, size, block) -> Path:
    return (Path(out_root) / "results" / "sampling" / f"{size}_trained"
            / f"{shard_name(block)}.draws.jsonl.gz")


# ------------------------------------------- frozen-order preconditions

def gate1_clean(out_root) -> tuple:
    for size in SIZES_3D:
        p = rederive_3d.record_path(out_root, size)
        if not p.exists():
            return False, f"gate-1 record missing: {RUNG}/{size}"
        rec = json.loads(p.read_text())
        if rec.get("n_diffs") != 0:
            return False, (f"gate-1 diffs at {RUNG}/{size}: "
                           f"{rec.get('n_diffs')} differing draws — "
                           f"the generation law drifted; no new draw "
                           f"is interpretable")
    return True, "both gate-1 records exist with 0 diffs"


def scoring_clean(out_root) -> tuple:
    for size in SIZES_3D:
        for rung in SCORING_RUNGS:
            p = scoring_3d.record_path(out_root, rung, size)
            if not p.exists():
                return False, f"scoring record missing: {rung}/{size}"
            rec = json.loads(p.read_text())
            if rung == "ctrl_copy" and \
                    rec.get("known_answer_gate", {}).get("passed") \
                    is not True:
                return False, (f"ctrl_copy known-answer gate did not "
                               f"pass at {size} — the scoring arm is "
                               f"broken and the campaign does not "
                               f"launch (§5.5)")
    return True, "all 4 scoring records exist; both ctrl gates PASS"


# ------------------------------------------------------- per-seed tallies

def per_seed_tallies_3d(rows, answers, labels, *, answer_type, seeds,
                        verify_fn) -> dict:
    """exp3's per_seed_tallies shape, verbatim plain loop, with 3c's
    total verify passed in — the convenience tallies stored beside the
    raw draws. Kept as a SEPARATE implementation from the analyzer's
    tally_with_addresses so the stored-vs-recompute agreement check
    still crosses two implementations (full_shape's rule)."""
    out = {str(s): {"full_string": 0, "first_char": 0, "n_draws": 0}
           for s in seeds}
    for row in rows:
        i = row["item"]
        for s in seeds:
            key = str(s)
            if key not in row["draws"]:
                raise ValueError(f"item {i} carries no stream for "
                                 f"seed {s}")
            for d in row["draws"][key]:
                out[key]["n_draws"] += 1
                if verify_fn(d, answers[i], answer_type):
                    out[key]["full_string"] += 1
                if score_first_char(d, labels[i]):
                    out[key]["first_char"] += 1
    return out


# ----------------------------------------------------------- cell kinds

def run_gate1_cell(size, out_root=EXP3D, model_ctx=None) -> dict:
    return rederive_3d.rederive_cell_3d(size, out_root=out_root,
                                        model_ctx=model_ctx)


def run_scoring_cell(rung, size, out_root=EXP3D, model_ctx=None) -> dict:
    ok, why = gate1_clean(out_root)
    if not ok:
        raise RuntimeError(f"§10 order violated: {why} — the scoring "
                           f"pass runs only after a clean gate 1")
    return scoring_3d.run_scoring_cell(rung, size, out_root=out_root,
                                       model_ctx=model_ctx)


def run_sampling_block(size, block, out_root=EXP3D,
                       model_ctx=None) -> dict:
    """One seed block's NEW draws: 4 seeds through exp3's frozen
    sampler, raw streams written beside the record, skip-if-exists —
    the durable, resumable, commit-per-block campaign unit (§10.4)."""
    out = sampling_record_path(out_root, size, block)
    dpath = sampling_draws_path(out_root, size, block)
    if out.exists() and dpath.exists():
        return json.loads(out.read_text())
    ok, why = gate1_clean(out_root)
    if not ok:
        raise RuntimeError(f"§10 order violated: {why}")
    ok, why = scoring_clean(out_root)
    if not ok:
        raise RuntimeError(f"§10 order violated: {why} — no tranche "
                           f"draw before the committed scoring pass")
    check_frozen_imports_3d()
    _assert_module_provenance()
    from harness import render_prompt  # noqa: PLC0415 — 2c's, asserted

    if size not in SIZES_3D or tuple(block) not in SEED_BLOCKS[size]:
        raise ValueError(f"{size}/{block} is not a preregistered 3d "
                         f"seed block")
    cap, items_path = load_capability(RUNG)
    items_sha = hashlib.sha256(items_path.read_bytes()).hexdigest()
    if items_sha != ITEMS_SHA_PIN[RUNG]:
        raise ValueError(
            f"item file {items_path} has sha256 {items_sha} against "
            f"the §4 pin {ITEMS_SHA_PIN[RUNG]} — these are not the "
            f"committed items")
    shots = [tuple(s) for s in cap["shots"]][:2]
    tok, model, model_sha = model_ctx if model_ctx else \
        _load_model(size, "trained", "float32")
    terminal = tuple(sorted(set(tok.all_special_ids)))

    rows = []
    for i, it in enumerate(cap["eval_items"]):
        prompt = render_prompt(it["question"], shots)
        got = sample_item(model, tok, prompt, rung=RUNG, size=size,
                          mode="trained", item_idx=i, seeds=tuple(block),
                          draws_per_seed=DRAWS_PER_SEED_3D,
                          terminal_ids=terminal)
        rows.append({"item": i,
                     "draws": {str(s): got[s] for s in block}})
        if (i + 1) % 50 == 0:
            print(f"[3d] {size} s{block[0]}-s{block[-1]}: {i + 1}/"
                  f"{len(cap['eval_items'])} items sampled", flush=True)
    write_draws(dpath, rows)

    answers = [str(it["answer"]) for it in cap["eval_items"]]
    labels = [str(it["probe_label"]) for it in cap["eval_items"]]
    tallies = per_seed_tallies_3d(rows, answers, labels,
                                  answer_type=cap["answer_type"],
                                  seeds=tuple(block),
                                  verify_fn=load_verify_3c())
    import torch          # noqa: PLC0415
    import transformers   # noqa: PLC0415
    rec = {"rung": RUNG, "size": size, "mode": "trained",
           "n_items": len(answers),
           "answers": answers, "probe_labels": labels,
           "answer_type": cap["answer_type"],
           "items_sha256": items_sha,
           "dtype": "float32", "untrained_seed": None,
           "model_sha": model_sha,
           "stack": {"torch": torch.__version__,
                     "transformers": transformers.__version__},
           "seeds": list(block),
           "draws_per_seed": DRAWS_PER_SEED_3D,
           "k_total": K_BLOCK,
           "per_seed_tallies": tallies,
           "draws_file": dpath.name}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    fires = sum(v["full_string"] for v in tallies.values())
    print(f"[3d] {size} s{block[0]}-s{block[-1]}: block done — "
          f"{fires} verified full-string fire(s) in "
          f"{sum(v['n_draws'] for v in tallies.values())} new draws",
          flush=True)
    return rec


def run_tier(kind: str, size: str, out_root=EXP3D) -> list:
    """All of one (kind, size) tier's cells in THIS process — one
    model load, cells sequential, skip-if-exists. The process boundary
    is the driver's job (tier-per-process, exp3's allocator lesson)."""
    if kind not in KINDS:
        raise ValueError(f"unknown 3d cell kind {kind!r}")
    check_frozen_imports_3d()
    _assert_module_provenance()
    # preconditions checked BEFORE the model loads, so a refused tier
    # costs nothing
    if kind == "scoring":
        ok, why = gate1_clean(out_root)
        if not ok:
            raise RuntimeError(f"§10 order violated: {why}")
    if kind == "sampling":
        for check in (gate1_clean, scoring_clean):
            ok, why = check(out_root)
            if not ok:
                raise RuntimeError(f"§10 order violated: {why}")
    ctx = _load_model(size, "trained", "float32")
    out = []
    if kind == "gate1":
        out.append(run_gate1_cell(size, out_root=out_root,
                                  model_ctx=ctx))
    elif kind == "scoring":
        for rung in SCORING_RUNGS:
            out.append(scoring_3d.run_scoring_cell(
                rung, size, out_root=out_root, model_ctx=ctx))
    else:
        for block in SEED_BLOCKS[size]:
            out.append(run_sampling_block(size, block,
                                          out_root=out_root,
                                          model_ctx=ctx))
    print(f"[3d] {kind}/{size} tier done", flush=True)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--tier":
        run_tier(sys.argv[2], sys.argv[3])
    else:
        kind, size = sys.argv[1:3]
        if kind == "sampling":
            block = tuple(int(x) for x in sys.argv[3].split(","))
            run_sampling_block(size, block)
        elif kind == "gate1":
            run_gate1_cell(size)
        else:
            run_scoring_cell(sys.argv[3], size)
