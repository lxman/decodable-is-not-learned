# experiments/exp2i/run/preflight_2i.py
"""Exp 2i preflight (design §7, dial j): the ONE sanctioned pre-tag
model contact — OLMo-2 1B `main` on 2c's harness, 20 items each of
`antonym` and `add3_mid`, a format check that the prompt renders, the
model stops, and the normalizer parses what OLMo emits. Prints prompt
tail + continuation + verify bit per item to STDOUT ONLY; nothing is
stored anywhere the analyzer reads (design: "NOT stored anywhere the
analyzer reads"). Asserts the tokenizer deltas live (left padding,
OLMo's own pad id, no BOS — `battery_2i.check_tokenizer`) and, after
running, that nothing under `root/results` was created by it (ruling
9). Runs only on Michael's word.

Usage: python -m experiments.exp2i.run.preflight_2i
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXP2I = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2I.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402

PREFLIGHT_RUNGS = ("antonym", "add3_mid")
N_ITEMS_PREFLIGHT = 20


def _assert_provenance() -> None:
    import harness
    got = Path(sys.modules["harness"].__file__).resolve()
    if bi.EXP2C.resolve() not in got.parents:
        raise ImportError(f"harness resolved to {got}, not under {bi.EXP2C}")


def real_loaders() -> dict:
    from harness import HFRunner

    def olmo1b_main(commit, device):
        return bi.load_thin(bi.REPO_1B, commit, device=device, dtype="float16")

    return {"olmo1b_main": olmo1b_main, "runner": lambda tok, model: HFRunner(tok, model)}


def _release(model) -> None:
    if model is None:
        return
    try:
        import torch
        del model
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:      # noqa: BLE001 — fakes
        pass


def _results_snapshot(root) -> set:
    d = Path(root) / "results"
    return set(d.rglob("*")) if d.exists() else set()


def run(*, root=EXP2I, device="mps", loaders=None,
        rungs=PREFLIGHT_RUNGS, n_items=N_ITEMS_PREFLIGHT) -> None:
    bi.check_frozen_2i()
    before = _results_snapshot(root)

    manifest = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    commit = bi.entry_main(manifest, bi.REPO_1B)["commit"]
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()

    from harness import MAX_NEW_TOKENS, render_prompt, verify

    model, tok, info = loaders["olmo1b_main"](commit, device)
    try:
        bi.check_tokenizer(tok)
        runner = loaders["runner"](tok, model)
        for rung in rungs:
            cap = bt.load_item_file(rung)
            shots = [tuple(s) for s in cap["shots"]][:bt.N_SHOTS]
            items = cap["eval_items"][:n_items]
            prompts = [render_prompt(it["question"], shots) for it in items]
            conts = runner.generate(prompts, MAX_NEW_TOKENS[cap["answer_type"]])
            if len(conts) != len(prompts):
                raise RuntimeError("generate returned the wrong number of "
                                  "continuations")
            for prompt, cont, it in zip(prompts, conts, items):
                bit = int(bool(verify(cont, str(it["answer"]), cap["answer_type"])))
                tail = prompt[-80:].replace("\n", "\\n")
                print(f"[2i preflight] {rung} …{tail!r} -> {cont!r} verify={bit}",
                      flush=True)
    finally:
        _release(model)

    after = _results_snapshot(root)
    new = after - before
    if new:
        raise RuntimeError(f"preflight wrote under {Path(root) / 'results'}: "
                           f"{sorted(str(p) for p in new)}")
    print(f"[2i preflight] complete: {len(rungs)} rung(s), {n_items} item(s) each; "
          f"nothing written under results/", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2i preflight (dial j) — "
                                             "OLMo-2 1B main, format check only")
    ap.add_argument("--root", default=str(EXP2I),
                    help="test-only override; production leaves this at EXP2I")
    ap.add_argument("--device", default="mps")
    ar = ap.parse_args(argv)
    run(root=Path(ar.root), device=ar.device)
    return 0


if __name__ == "__main__":
    sys.exit(main())
