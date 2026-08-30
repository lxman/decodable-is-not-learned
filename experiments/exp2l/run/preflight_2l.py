# experiments/exp2l/run/preflight_2l.py
"""Exp 2l preflight (design §7, dial j): the ONE sanctioned pre-tag
model contact, on Michael's word — (a) OLMo-2 13B `main` through the
thin loader at fp16, 2c's harness on 20 items each of `antonym` and
`add3_mid` (format + MEMORY check: 13B fp16 ≈ 26 GB on the 48 GB Mac;
the allocated MPS bytes after load are printed; `--batch-size` is the
dial if 16 does not fit — and if it changes, `battery_2l.BATCH_SIZE_2L`
changes BEFORE the tag, once, for every stage); (b) ONE grid checkpoint
(`--checkpoint-step`, default 1000) staged through the candidate-file
loader END TO END — download (≈ 55 GB), sha verify, clean dir with
config.json, load, the same 40 items, free — the tenth lesson (2i stop
#1 was a loader crash in gate 1's first model load). Prints prompt tail
+ continuation + verify bit per item to STDOUT ONLY; nothing is stored
anywhere the analyzer reads; asserts afterwards that nothing under
`root/results` was created.

Usage: python -m experiments.exp2l.run.preflight_2l [--batch-size 16] [--checkpoint-step 1000]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXP2L = Path(__file__).resolve().parents[1]
REPO = EXP2L.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i.run._common_2i import (  # noqa: E402
    assert_provenance as _assert_provenance,
    release as _release,
)
from experiments.exp2l import battery_2l as bl  # noqa: E402

PREFLIGHT_RUNGS = ("antonym", "add3_mid")
N_ITEMS_PREFLIGHT = 20


def real_loaders(batch_size: int) -> dict:
    from harness import HFRunner

    def thin(commit, device):
        return bl.load_thin_13b(commit, device=device, dtype="float16")

    def checkpoint(entry, cache_root, device):
        return bl.load_checkpoint_13b(entry, cache_root=cache_root, device=device, dtype="float16")

    def memory():
        try:
            import torch
            return int(torch.mps.current_allocated_memory())
        except Exception:  # noqa: BLE001
            return -1

    return {"thin": thin, "checkpoint": checkpoint, "tokenizer": bl.load_tokenizer_13b,
            "runner": lambda tok, model: HFRunner(tok, model, batch_size),
            "free": bl.free_checkpoint_13b, "check_tokenizer": bi.check_tokenizer,
            "memory": memory}


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
            print(f"[2l preflight] {label}{rung} …{tail!r} -> {cont!r} verify={bit}", flush=True)


def run(*, root=EXP2L, device="mps", loaders=None, rungs=PREFLIGHT_RUNGS,
        n_items=N_ITEMS_PREFLIGHT, batch_size=bl.BATCH_SIZE_2L, checkpoint_step=1000,
        cache_root=bl.CKPT_CACHE_2L) -> None:
    bl.check_frozen_2l()
    before = _results_snapshot(root)
    manifest = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders(batch_size)
    verify_fn = a2d.load_verify()
    print(f"[2l preflight] batch_size {batch_size}", flush=True)

    # (a) main through the thin loader
    commit = bl.entry_main_13b(manifest)["commit"]
    model = None
    try:
        model, tok, info = loaders["thin"](commit, device)
        loaders["check_tokenizer"](tok)
        print(f"[2l preflight] main loaded (thin): mps_allocated_bytes {loaders['memory']()}",
              flush=True)
        _print_items(loaders["runner"](tok, model), verify_fn, rungs, n_items, "")
    finally:
        _release(model)

    # (b) one grid checkpoint through the candidate-file loader, end to end
    entry = bl.entry_13b(manifest, checkpoint_step)
    model = None
    try:
        model, info = loaders["checkpoint"](entry, cache_root, device)
        tok = loaders["tokenizer"](entry["commit"])
        loaders["check_tokenizer"](tok)
        print(f"[2l preflight] {entry['revision']} loaded (candidate files): digest "
              f"{str(info.get('tensor_digest'))[:12]}, mps_allocated_bytes {loaders['memory']()}",
              flush=True)
        _print_items(loaders["runner"](tok, model), verify_fn, rungs, n_items, "ckpt ")
    finally:
        _release(model)
        loaders["free"](entry["revision"], cache_root)

    new = _results_snapshot(root) - before
    if new:
        raise RuntimeError(f"preflight wrote under {Path(root) / 'results'}: "
                           f"{sorted(str(p) for p in new)}")
    print(f"[2l preflight] complete: {len(rungs)} rung(s) × {n_items} item(s) on main and on "
          f"{entry['revision']}; nothing written under results/", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2l preflight (dial j) — OLMo-2 13B main + one "
                                             "checkpoint, format/memory/loader check only")
    ap.add_argument("--root", default=str(EXP2L))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--batch-size", type=int, default=bl.BATCH_SIZE_2L)
    ap.add_argument("--checkpoint-step", type=int, default=1000)
    ap.add_argument("--cache-root", default=str(bl.CKPT_CACHE_2L))
    ar = ap.parse_args(argv)
    run(root=Path(ar.root), device=ar.device, batch_size=ar.batch_size,
        checkpoint_step=ar.checkpoint_step, cache_root=Path(ar.cache_root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
