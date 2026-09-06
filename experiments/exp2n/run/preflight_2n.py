# experiments/exp2n/run/preflight_2n.py
"""Exp 2n preflight (design §7, dial j): the ONE sanctioned model
contact before the campaign, on Michael's word — run AFTER
`exp2n-preregistered` is cut, before the endpoint stage — (a) the
released main (`REPO_COMMA` @ its commit) through the thin loader at
`DTYPE_2N`, 2c's harness on 20 items each of `antonym` and `add3_mid`
under TWO renders: the plain render (the convention every stage uses)
and a `<|begin_of_text|>`-prefixed render (dial n, the training
render — pinned, not descriptive); (b) ONE grid checkpoint
(`--checkpoint-step`, default 10000) staged through the candidate-file
loader END TO END — download (≈ 14.0 GB), sha verify, clean dir with
config.json, load, the same 40 items under both renders, free. After
EACH load: the eos facts (dial o — config eos vs the generation config's
eos AFTER the override), peak MPS memory, both renders' ids for "Q:",
then a finiteness probe (one forward pass on one prompt, the logits
scanned for NaN/Inf — any non-finite value REFUSES; the fp32 fallback
is a pre-tag change to `DTYPE_2N` and a re-tag; design §7). Prints
prompt tail + continuation + verify bit per item, to STDOUT ONLY;
nothing is stored anywhere the analyzer reads; asserts afterwards that
nothing under `root/results` was created.

Usage: python -m experiments.exp2n.run.preflight_2n [--batch-size 16] [--checkpoint-step 10000]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXP2N = Path(__file__).resolve().parents[1]
REPO = EXP2N.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2i.run._common_2i import (  # noqa: E402
    assert_provenance as _assert_provenance,
    release as _release,
)
from experiments.exp2n import battery_2n as bn  # noqa: E402

PREFLIGHT_RUNGS = ("antonym", "add3_mid")
N_ITEMS_PREFLIGHT = 20
FINITE_PROBE_TEXT = "Q: What is 2 + 2?\nA:"


def real_loaders(batch_size: int) -> dict:
    from harness import HFRunner

    def thin(repo, commit, device):
        return bn.load_thin_comma(repo, commit, device=device, dtype=bn.DTYPE_2N)

    def checkpoint(entry, cache_root, device):
        return bn.load_checkpoint_comma(entry, cache_root=cache_root, device=device, dtype=bn.DTYPE_2N)

    def memory():
        try:
            import torch
            return {"current": int(torch.mps.current_allocated_memory()),
                    "peak": int(torch.mps.driver_allocated_memory())}
        except Exception:  # noqa: BLE001
            return {"current": -1, "peak": -1}

    def finite(model, tok, prompt):
        import torch
        enc = tok([prompt], return_tensors="pt", padding=True).to(model.device)
        with torch.no_grad():
            logits = model(**enc).logits
        ok = torch.isfinite(logits)
        n_bad = int((~ok).sum().item())
        max_abs = float(logits[ok].abs().max().item()) if ok.any() else float("nan")
        return {"n_nonfinite": n_bad, "max_abs": max_abs}

    def render_ids(tok, text):
        return list(tok(text)["input_ids"])

    return {"thin": thin, "checkpoint": checkpoint, "tokenizer": bn.load_tokenizer_comma,
            "runner": lambda tok, model: bn.BosRunner(HFRunner(tok, model, batch_size)),
            "plain_runner": lambda tok, model: HFRunner(tok, model, batch_size),
            "free": bn.free_checkpoint_comma, "check_tokenizer": bn.check_tokenizer_2n,
            "eos_facts": bn.eos_facts_2n, "memory": memory, "finite": finite,
            "render_ids": render_ids}


def _results_snapshot(root) -> set:
    d = Path(root) / "results"
    return set(d.rglob("*")) if d.exists() else set()


def _print_items(runner, verify_fn, rungs, n_items, label) -> None:
    from harness import MAX_NEW_TOKENS, render_prompt
    for rung in rungs:
        cap = bt.load_item_file(rung)
        shots = [tuple(s) for s in cap["shots"]][:bt.N_SHOTS]
        items = cap["eval_items"][:n_items]
        prompts = [render_prompt(it["question"], shots) for it in items]
        conts = runner.generate(prompts, MAX_NEW_TOKENS[cap["answer_type"]])
        if len(conts) != len(prompts):
            raise RuntimeError("generate returned the wrong number of continuations")
        for prompt, cont, it in zip(prompts, conts, items):
            bit = int(bool(verify_fn(cont, str(it["answer"]), cap["answer_type"])))
            tail = prompt[-60:].replace("\n", "\\n")
            print(f"[2n preflight] {label}{rung} …{tail!r} -> {cont!r} verify={bit}", flush=True)


def _probe(loaders, model, tok, label) -> None:
    res = loaders["finite"](model, tok, FINITE_PROBE_TEXT)
    print(f"[2n preflight] {label}: n_nonfinite {res['n_nonfinite']} max_abs {res['max_abs']}", flush=True)
    if res["n_nonfinite"]:
        raise RuntimeError(f"{label}: {res['n_nonfinite']} non-finite logit(s) at {bn.DTYPE_2N} — "
                           f"the fp32 fallback is a pre-tag change to battery_2n.DTYPE_2N and a re-tag")


def run(*, root=EXP2N, device="mps", loaders=None, rungs=PREFLIGHT_RUNGS,
        n_items=N_ITEMS_PREFLIGHT, batch_size=bn.BATCH_SIZE_2N, checkpoint_step=10000,
        cache_root=bn.CKPT_CACHE_2N) -> None:
    bn.check_frozen_2n()
    before = _results_snapshot(root)
    manifest = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders(batch_size)
    verify_fn = a2d.load_verify()
    print(f"[2n preflight] batch_size {batch_size} dtype {bn.DTYPE_2N}", flush=True)

    # (a) main through the thin loader, both renders
    main = bn.entry_main_comma(manifest)
    model = None
    try:
        model, tok, info = loaders["thin"](main["repo"], main["commit"], device)
        loaders["check_tokenizer"](tok)
        f = loaders["eos_facts"](model)
        print(f"[2n preflight] main: config eos {f['config_eos_token_id']} | generation eos "
              f"{f['generation_eos_token_id']}", flush=True)
        mem = loaders["memory"]()
        print(f"[2n preflight] main loaded (thin): mps_allocated_bytes {mem['current']} "
              f"peak_mps_bytes {mem['peak']}", flush=True)
        print(f"[2n preflight] bos render ids {loaders['render_ids'](tok, bn.BOS_TOKEN_2N + 'Q:')}",
              flush=True)
        print(f"[2n preflight] plain render ids {loaders['render_ids'](tok, 'Q:')}", flush=True)
        _probe(loaders, model, tok, "main")
        runner = loaders["runner"](tok, model)
        plain_runner = loaders["plain_runner"](tok, model)
        _print_items(runner, verify_fn, rungs, n_items, "")
        _print_items(plain_runner, verify_fn, rungs, n_items, "plain ")
    finally:
        _release(model)

    # (b) one grid checkpoint through the candidate-file loader, end to end, both renders
    entry = bn.entry_comma(manifest, checkpoint_step)
    model = None
    try:
        model, info = loaders["checkpoint"](entry, cache_root, device)
        tok = loaders["tokenizer"](entry["repo"], entry["commit"])
        loaders["check_tokenizer"](tok)
        f = loaders["eos_facts"](model)
        print(f"[2n preflight] {entry['revision']}: config eos {f['config_eos_token_id']} | "
              f"generation eos {f['generation_eos_token_id']}", flush=True)
        mem = loaders["memory"]()
        print(f"[2n preflight] {entry['revision']} loaded (candidate files): digest "
              f"{str(info.get('tensor_digest'))[:12]}, mps_allocated_bytes {mem['current']} "
              f"peak_mps_bytes {mem['peak']}", flush=True)
        print(f"[2n preflight] bos render ids {loaders['render_ids'](tok, bn.BOS_TOKEN_2N + 'Q:')}",
              flush=True)
        print(f"[2n preflight] plain render ids {loaders['render_ids'](tok, 'Q:')}", flush=True)
        _probe(loaders, model, tok, entry["revision"])
        runner = loaders["runner"](tok, model)
        plain_runner = loaders["plain_runner"](tok, model)
        _print_items(runner, verify_fn, rungs, n_items, "ckpt ")
        _print_items(plain_runner, verify_fn, rungs, n_items, "ckpt plain ")
    finally:
        _release(model)
        loaders["free"](entry["revision"], cache_root)

    new = _results_snapshot(root) - before
    if new:
        raise RuntimeError(f"preflight wrote under {Path(root) / 'results'}: "
                           f"{sorted(str(p) for p in new)}")
    print(f"[2n preflight] complete: {len(rungs)} rung(s) × {n_items} item(s) × 2 renders on main "
          f"and on {entry['revision']}; nothing written under results/", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2n preflight (dial j) — Comma v0.1-1T main + one "
                                             "checkpoint, format/memory/precision/loader check only")
    ap.add_argument("--root", default=str(EXP2N))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--batch-size", type=int, default=bn.BATCH_SIZE_2N)
    ap.add_argument("--checkpoint-step", type=int, default=10000)
    ap.add_argument("--cache-root", default=str(bn.CKPT_CACHE_2N))
    ar = ap.parse_args(argv)
    run(root=Path(ar.root), device=ar.device, batch_size=ar.batch_size,
        checkpoint_step=ar.checkpoint_step, cache_root=Path(ar.cache_root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
