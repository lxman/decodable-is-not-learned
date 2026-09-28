# experiments/exp6/run/predict_6.py
"""The predictor stage (design §3.3): exp3's frozen sampler on the Mac,
one predictor per invocation, every unit resumable.

    python -m experiments.exp6.run.predict_6 --predictor pythia_1b

Unit order inside a predictor: the GATED units first (the anchors and
the control regenerate committed streams and must equal them byte for
byte — a mismatch halts before a new rung is sampled), then the pilot,
then the main tier, then the untrained twin (its own model load).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

EXP6 = Path(__file__).resolve().parents[1]
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp6 import battery_6 as b6  # noqa: E402
from experiments.exp6 import records_6 as r6  # noqa: E402
from experiments.exp6 import referents_6 as rf  # noqa: E402
from experiments.exp6 import verify_6 as v6  # noqa: E402
from experiments.exp6.run import _common_6 as cm  # noqa: E402


def real_loader(predictor: str, mode: str, device: str):
    """(tok, model, {"repo","commit","model_sha"}). Pythia goes through
    exp3's loader (fp16 weights upcast exactly to fp32, MPS); OLMo-2 1B
    through 2i's thin loader at fp32."""
    pin = rf.model_pin(predictor)
    if r6.PREDICTORS_6[predictor]["lineage"] == "pythia":
        from experiments.exp3.run.run_cell import _assert_module_provenance, _load_model
        _assert_module_provenance()
        tok, model, sha = _load_model(r6.PREDICTORS_6[predictor]["size"], mode,
                                      r6.SAMPLING_DTYPE)
        return tok, model, {"repo": pin["repo"], "commit": sha, "model_sha": sha}
    if mode != "trained":
        raise ValueError(f"{predictor} has no untrained twin")
    from experiments.exp2i import battery_2i as bi
    model, tok, info = bi.load_thin(bi.REPO_1B, pin["commit"], device=device,
                                    dtype=r6.SAMPLING_DTYPE)
    return tok, model, {"repo": pin["repo"], "commit": info["commit"],
                        "model_sha": info["tensor_digest"]}


def real_sampler():
    from experiments.exp3 import sampler
    return sampler.sample_item


def prompts_of(cap) -> list:
    h = v6.harness_2c()
    shots = [tuple(s) for s in cap["shots"]][:b6.N_SHOTS]
    return [h.render_prompt(it["question"], shots) for it in cap["eval_items"]]


def unit_order(predictor: str) -> list:
    """(tier, rung) in run order for the TRAINED model, then the twin."""
    gated = [(t, r) for p, t, r in rf.gated_units() if p == predictor]
    rest = [(t, r) for p, t, r in r6.predictor_units()
            if p == predictor and (t, r) not in gated and t != "twin"]
    order = {"pilot": 0, "main": 1}
    rest.sort(key=lambda tr: order[tr[0]])          # stable: rung order kept
    twin = [(t, r) for p, t, r in r6.predictor_units()
            if p == predictor and t == "twin"]
    return gated + rest, twin


def unit_complete(root, predictor, tier, rung) -> bool:
    rec = r6.tier_record_path(root, predictor, tier, rung)
    dr = r6.tier_draws_path(root, predictor, tier, rung)
    if rec.exists() != dr.exists():
        raise RuntimeError(f"torn record+draws pair on resume: {rec} / {dr}")
    if not rec.exists():
        return False
    t = r6.tier_shape(predictor, tier)
    r6.read_json(rec)
    r6.read_draws(dr, seeds=t["seeds"], dps=t["dps"])
    return True


def run_unit(predictor, tier, rung, *, root, model_ctx, sampler, stack, git_sha) -> dict:
    tok, model, model_rec = model_ctx
    t = r6.tier_shape(predictor, tier)
    cap = b6.load_item_file_6(rung)
    committed = None
    if (predictor, tier, rung) in rf.gated_units():
        committed = {r["item"]: r for r in rf.committed_rows(predictor, tier, rung)}
    terminal = tuple(sorted(set(tok.all_special_ids)))
    budget = b6.max_new_tokens_6(rung)
    size = r6.PREDICTORS_6[predictor]["size"]
    rows, t0 = [], time.time()
    for i, prompt in enumerate(prompts_of(cap)):
        got = sampler(model, tok, prompt, rung=rung, size=size, mode=t["mode"],
                      item_idx=i, seeds=t["seeds"], draws_per_seed=t["dps"],
                      max_new_tokens=budget, terminal_ids=terminal)
        row = {"item": i, "draws": {str(s): [str(x) for x in got[s]]
                                    for s in t["seeds"]}}
        rows.append(row)
        if committed is not None and row["draws"] != {
                str(s): committed[i]["draws"][str(s)] for s in t["seeds"]}:
            halted = r6.tier_halt_path(root, predictor, tier, rung)
            r6.write_draws(halted.with_name(halted.name + ".jsonl.gz"), rows)
            r6.write_json(halted, {"predictor": predictor, "tier": tier, "rung": rung,
                                   "item": i, "model": model_rec, "stack": stack,
                                   "git_sha": git_sha,
                                   "committed": str(rf.committed_draws_path(
                                       predictor, tier, rung))})
            raise RuntimeError(f"GATE 1-P FIRED: {predictor}/{tier}/{rung} item {i} "
                               f"is not the committed stream")
    dpath = r6.tier_draws_path(root, predictor, tier, rung)
    r6.write_draws(dpath, rows)                     # draws BEFORE the record
    rec = r6.tier_record(predictor=predictor, tier=tier, rung=rung, cap=cap,
                         rows=rows, model=model_rec, stack=stack, git_sha=git_sha,
                         seconds=time.time() - t0,
                         draws_sha256=r6.sha256_file(dpath))
    r6.write_json(r6.tier_record_path(root, predictor, tier, rung), rec)
    return rec


def run(predictor: str, *, root=EXP6, device="mps", loader=None, sampler=None,
        dry_run=False, tag_exists=None, blob_sha=None, frozen_check=None) -> list:
    if predictor not in r6.PREDICTORS_6:
        raise ValueError(f"{predictor!r} is not a predictor")
    cm.gates(tag_exists=tag_exists, blob_sha=blob_sha, frozen_check=frozen_check)
    if r6.seal_path(root).exists():
        raise RuntimeError("the predictor is sealed; nothing may be sampled after it")
    cm.refuse_if_halted(root)
    trained, twin = unit_order(predictor)
    pending = [(t, r) for t, r in trained if not unit_complete(root, predictor, t, r)]
    pending_twin = [(t, r) for t, r in twin
                    if not unit_complete(root, predictor, t, r)]
    if dry_run:
        return [f"{predictor}/{t}/{r}" for t, r in pending + pending_twin]
    loader = real_loader if loader is None else loader
    sampler = real_sampler() if sampler is None else sampler
    stack, sha = cm.short_stack(), cm.p6.git_sha()
    done = []
    for mode, units in (("trained", pending), ("untrained", pending_twin)):
        if not units:
            continue
        ctx = loader(predictor, mode, device)
        pin = rf.model_pin(predictor)
        if ctx[2]["commit"] != pin["commit"] or ctx[2]["model_sha"] != pin["model_sha"]:
            raise RuntimeError(f"{predictor}: the loader reports {ctx[2]} against "
                               f"the pin {pin}")
        try:
            for t, r in units:
                done.append(run_unit(predictor, t, r, root=root, model_ctx=ctx,
                                     sampler=sampler, stack=stack, git_sha=sha))
        finally:
            from experiments.exp6 import families_6 as fm
            fm.release(ctx[1])
    cm.exit_gate(r6.predictor_halt_path(root), frozen_check=frozen_check)
    return done


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictor", required=True, choices=sorted(r6.PREDICTORS_6))
    ap.add_argument("--root", default=str(EXP6))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    out = run(a.predictor, root=Path(a.root), device=a.device, dry_run=a.dry_run)
    for line in out if a.dry_run else [f"{r['predictor']}/{r['tier']}/{r['rung']} "
                                       f"{r['seconds']} s" for r in out]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
