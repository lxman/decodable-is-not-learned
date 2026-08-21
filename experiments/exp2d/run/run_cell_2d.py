"""Exp 2d runner: one rung of one tier — pilot | main | argmax.

Tiers (design §3, §10):
- pilot:  k = 8, seed 1000, both sizes, fp32 — feeds the frozen §7 power
          procedure and NOTHING else (never pooled with main).
- main:   k = 64, seed 0, both sizes, fp32 — the predictor. For the two
          reversal rungs the seed-0 streams ARE exp3's committed draws:
          the comparison (gate 1) runs right here, on the production
          output, as the rung lands; any diff halts (rederive_2d).
- argmax: greedy fp16 via 2c's HFRunner on the same items — §5.4
          descriptive, after main. For the four reversal cells the
          continuations are compared to exp3's committed fp16 redecode
          records and the diff count is PRINTED in the record
          (non-gating; build dial, ledgered for ratification).

THE FROZEN ORDER IS EXECUTABLE (§10): main REFUSES to run until both
pilot tiers are complete AND `power_2d.json` exists (the procedure ran
ONCE and printed its declaration — main runs REGARDLESS of what it
says, ruling c); argmax REFUSES until both main tiers are complete.
Every unit is skip-if-exists; the (tier, size, rung) record + draws
pair is the durable, commit-per-rung unit the watcher ships.

Everything frozen is imported from the exp2c/exp2b/exp3/exp3c/exp3d
trees, never copied. NOTHING here runs before tag `exp2d-preregistered`
and Michael's launch word.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2D = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2D.parent
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))

from experiments.exp2d import analyze_2d as a  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import rederive_2d  # noqa: E402
from experiments.exp3.run.run_cell import (  # noqa: E402
    _assert_module_provenance, _load_model, write_draws,
)
from experiments.exp3.sampler import sample_item  # noqa: E402

KINDS = ("pilot", "main", "argmax")
SIZES_ASCENDING = tuple(a.PROBE_SIZES)    # 410m then 1b


# ------------------------------------------- frozen-order preconditions

def tier_complete(out_root, tier, size) -> bool:
    if tier == "argmax":
        return all(a.argmax_record_path(out_root, size, r).exists()
                   for r in a.RUNGS)
    return all(a.tier_record_path(out_root, tier, size, r).exists()
               and a.tier_draws_path(out_root, tier, size, r).exists()
               for r in a.RUNGS)


def pilot_clean(out_root) -> tuple:
    for size in SIZES_ASCENDING:
        if not tier_complete(out_root, "pilot", size):
            return False, f"pilot/{size} incomplete"
    return True, "both pilot tiers complete"


def power_declared(out_root) -> tuple:
    p = Path(out_root) / "power_2d.json"
    if not p.exists():
        return False, ("power_2d.json missing — the frozen §7 procedure "
                       "has not run on the pilot; main starts only after "
                       "the declaration is printed (it runs regardless "
                       "of WHAT it says, ruling c)")
    rec = json.loads(p.read_text())
    if "declared_status" not in rec:
        return False, "power_2d.json carries no declared_status"
    return True, f"power declared: {rec['declared_status']}"


def main_clean(out_root) -> tuple:
    for size in SIZES_ASCENDING:
        if not tier_complete(out_root, "main", size):
            return False, f"main/{size} incomplete"
    for rung in a.REVERSAL_RUNGS:
        for size in SIZES_ASCENDING:
            p = a.gate1_record_path(out_root, size, rung)
            if not p.exists():
                return False, f"gate-1 record missing: {rung}/{size}"
            if json.loads(p.read_text()).get("n_diffs") != 0:
                return False, f"gate-1 diffs at {rung}/{size}"
    return True, "both main tiers complete, gate 1 clean"


def gate1_halted(out_root) -> tuple:
    """Any existing gate-1 record with diffs stops EVERY tier."""
    for rung in a.REVERSAL_RUNGS:
        for size in SIZES_ASCENDING:
            p = a.gate1_record_path(out_root, size, rung)
            if p.exists() and json.loads(p.read_text()).get("n_diffs") != 0:
                return True, f"gate 1 fired at {rung}/{size}; halted"
    return False, "no gate-1 diff on record"


def preconditions(kind, out_root) -> list:
    checks = []
    if kind == "main":
        checks += [pilot_clean, power_declared]
    if kind == "argmax":
        checks += [main_clean]
    return checks


def check_preconditions(kind, out_root) -> None:
    halted, why = gate1_halted(out_root)
    if halted:
        raise RuntimeError(f"§6: {why}")
    for check in preconditions(kind, out_root):
        ok, why = check(out_root)
        if not ok:
            raise RuntimeError(f"§10 order violated: {why}")


# ----------------------------------------------------------- helpers

def _stack() -> dict:
    import torch          # noqa: PLC0415
    import transformers   # noqa: PLC0415
    return {"torch": torch.__version__,
            "transformers": transformers.__version__}


def _prompts(cap) -> list:
    from harness import render_prompt   # 2c's, provenance-asserted
    shots = [tuple(s) for s in cap["shots"]][:bt.N_SHOTS]
    return [render_prompt(it["question"], shots) for it in cap["eval_items"]]


# ------------------------------------------------------- sampling tiers

def run_sampling_rung(tier, size, rung, out_root=EXP2D, model_ctx=None,
                      verify_fn=None) -> dict:
    """One rung's draws for one tier: exp3's frozen sampler at the
    tier's (seed, k), the rung's 2c token budget, every raw draw
    stored, per-seed tally beside it (the analyzer recomputes and
    refuses disagreement). For a reversal rung in main, gate 1 runs
    on the rows before the record is written."""
    if tier not in ("pilot", "main"):
        raise ValueError(f"{tier!r} is not a sampling tier")
    out = a.tier_record_path(out_root, tier, size, rung)
    dpath = a.tier_draws_path(out_root, tier, size, rung)
    if out.exists() and dpath.exists():
        return json.loads(out.read_text())
    check_preconditions(tier, out_root)
    a.check_frozen_imports_2d()
    _assert_module_provenance()
    spec = a.TIERS[tier]
    cap = bt.load_item_file(rung)          # sha-pinned
    prompts = _prompts(cap)
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    verify_fn = verify_fn or a.load_verify()
    tok, model, model_sha = model_ctx if model_ctx else \
        _load_model(size, a.MODE, a.SAMPLING_DTYPE)
    terminal = tuple(sorted(set(tok.all_special_ids)))
    budget = bt.max_new_tokens(rung)

    rows = []
    for i, prompt in enumerate(prompts):
        got = sample_item(model, tok, prompt, rung=rung, size=size,
                          mode=a.MODE, item_idx=i, seeds=(spec["seed"],),
                          draws_per_seed=spec["draws_per_seed"],
                          max_new_tokens=budget, terminal_ids=terminal)
        rows.append({"item": i, "draws": {str(spec["seed"]): got[spec["seed"]]}})
        if (i + 1) % 100 == 0:
            print(f"[2d {tier}] {rung}/{size}: {i + 1}/{len(prompts)} items",
                  flush=True)

    if tier == "main" and rung in a.REVERSAL_RUNGS:
        # GATE 1 ON THE PRODUCTION PATH — halts on any diff. The gate-1
        # record is written first (the failure IS the disclosure); on a
        # diff the rows go to a .HALTED file so they are inspectable,
        # and the normal draws file is NOT written, so skip-if-exists
        # never treats a halted rung as done.
        try:
            rederive_2d.record_and_halt_on_diff(
                rung, size, rows, answers=answers,
                answer_type=cap["answer_type"], verify_fn=verify_fn,
                items_sha=cap["items_sha256"], model_sha=model_sha,
                stack=_stack(), out_root=out_root)
        except RuntimeError:
            write_draws(dpath.with_suffix(".HALTED.jsonl.gz"), rows)
            raise

    write_draws(dpath, rows)
    verified = sum(1 for row in rows
                   for d in row["draws"][str(spec["seed"])]
                   if verify_fn(d, answers[row["item"]], cap["answer_type"]))
    n_draws = sum(len(row["draws"][str(spec["seed"])]) for row in rows)
    rec = {"rung": rung, "size": size, "mode": a.MODE, "tier": tier,
           "n_items": len(rows), "answers": answers,
           "answer_type": cap["answer_type"], "n_shots": bt.N_SHOTS,
           "dtype": a.SAMPLING_DTYPE, "untrained_seed": None,
           "model_sha": model_sha, "items_sha256": cap["items_sha256"],
           "stream_namespace": a.STREAM_NAMESPACE,
           "seeds": [spec["seed"]], "draws_per_seed": spec["draws_per_seed"],
           "k_total": spec["draws_per_seed"], "max_new_tokens": budget,
           "temperature": 1.0, "truncation": "none",
           "per_seed_tallies": {str(spec["seed"]): {
               "full_string": int(verified), "n_draws": int(n_draws)}},
           "draws_file": dpath.name, "stack": _stack()}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    print(f"[2d {tier}] {rung}/{size}: {verified} verified in {n_draws} "
          f"draws (floor {bt.majority_floor(cap)['floor']:.3f})", flush=True)
    return rec


# ------------------------------------------------------------- argmax

def run_argmax_rung(size, rung, out_root=EXP2D, model_ctx=None,
                    verify_fn=None) -> dict:
    """2c's greedy path VERBATIM (fp16, HFRunner.generate, render_prompt,
    MAX_NEW_TOKENS) — the same path that produced the outcome at the
    eval sizes and 3b/exp3's redecode at these sizes."""
    out = a.argmax_record_path(out_root, size, rung)
    if out.exists():
        return json.loads(out.read_text())
    check_preconditions("argmax", out_root)
    a.check_frozen_imports_2d()
    _assert_module_provenance()
    from harness import HFRunner   # 2c's
    cap = bt.load_item_file(rung)
    prompts = _prompts(cap)
    verify_fn = verify_fn or a.load_verify()
    tok, model, model_sha = model_ctx if model_ctx else \
        _load_model(size, a.MODE, a.ARGMAX_DTYPE)
    budget = bt.max_new_tokens(rung)
    conts = HFRunner(tok, model).generate(prompts, budget)
    if len(conts) != len(prompts):
        raise RuntimeError("continuation count != prompt count")
    correct = sum(verify_fn(c, str(it["answer"]), cap["answer_type"])
                  for c, it in zip(conts, cap["eval_items"]))
    redecode_diffs = None
    if rung in a.REVERSAL_RUNGS:
        ref_p = (a.EXP3 / "results" / "redecode" / f"{size}_{a.MODE}"
                 / f"{rung}.json")
        got_sha = hashlib.sha256(ref_p.read_bytes()).hexdigest()
        if got_sha != a.COMMITTED_REDECODE_SHA256[rung][size]:
            raise ValueError(f"{ref_p} is not at its pinned sha")
        ref = json.loads(ref_p.read_text())["continuations"]
        redecode_diffs = int(sum(1 for x, y in zip(conts, ref) if x != y))
    rec = {"rung": rung, "size": size, "mode": a.MODE, "tier": "argmax",
           "n_items": len(prompts), "answer_type": cap["answer_type"],
           "n_shots": bt.N_SHOTS, "dtype": a.ARGMAX_DTYPE,
           "untrained_seed": None, "model_sha": model_sha,
           "items_sha256": cap["items_sha256"], "max_new_tokens": budget,
           "continuations": conts, "correct": int(correct),
           "acc": correct / len(prompts),
           "redecode_diffs": redecode_diffs, "stack": _stack()}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    print(f"[2d argmax] {rung}/{size}: {correct}/{len(prompts)}"
          + (f"; vs exp3 redecode: {redecode_diffs} diffs"
             if redecode_diffs is not None else ""), flush=True)
    return rec


# --------------------------------------------------------------- tiers

def run_tier(kind, size, out_root=EXP2D) -> list:
    """All 34 rungs of one (kind, size) tier in THIS process — one
    model load, rungs in RUNG_ORDER_2D, skip-if-exists. The process
    boundary is the driver's job (tier-per-process)."""
    if kind not in KINDS:
        raise ValueError(f"unknown 2d tier kind {kind!r}")
    check_preconditions(kind, out_root)
    a.check_frozen_imports_2d()
    bt.check_order_against_2c()
    _assert_module_provenance()
    verify_fn = a.load_verify()
    dtype = a.ARGMAX_DTYPE if kind == "argmax" else a.SAMPLING_DTYPE
    ctx = _load_model(size, a.MODE, dtype)
    out = []
    for rung in a.RUNGS:
        if kind == "argmax":
            out.append(run_argmax_rung(size, rung, out_root=out_root,
                                       model_ctx=ctx, verify_fn=verify_fn))
        else:
            out.append(run_sampling_rung(kind, size, rung, out_root=out_root,
                                         model_ctx=ctx, verify_fn=verify_fn))
    print(f"[2d] {kind}/{size} tier done", flush=True)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--tier":
        run_tier(sys.argv[2], sys.argv[3])
    else:
        kind, size, rung = sys.argv[1:4]
        if kind == "argmax":
            run_argmax_rung(size, rung)
        else:
            run_sampling_rung(kind, size, rung)
