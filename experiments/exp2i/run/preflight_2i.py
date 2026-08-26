# experiments/exp2i/run/preflight_2i.py
"""Exp 2i preflight (design §7, dial j): the ONE sanctioned pre-tag
model contact — OLMo-2 1B `main` on 2c's harness, 20 items each of
`antonym` and `add3_mid`, a format check that the prompt renders, the
model stops, and the normalizer parses what OLMo emits. Also runs
exp3's frozen `sample_item` once, on antonym item 0 (k=2, seed 0) —
that sampler has never touched an OLMo-2 model, so a shape/API
mismatch surfaces here rather than in stage 1's 7-9 h run (doc slip
(m)); one model load, at the sampling stage's dtype
(`a2d.SAMPLING_DTYPE`, float32), serves both parts, since the format
check does not depend on dtype. Prints prompt tail + continuation +
verify bit per item, and the two sampled draws + their verify bits,
to STDOUT ONLY; nothing is stored anywhere the analyzer reads
(design: "NOT stored anywhere the analyzer reads"). Asserts the
tokenizer deltas live (left padding, OLMo's own pad id, no BOS —
`battery_2i.check_tokenizer`) and, after running, that nothing under
`root/results` was created by it (ruling 9). Runs only on Michael's
word.

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

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i.run._common_2i import (  # noqa: E402
    assert_provenance as _assert_provenance,
    release as _release,
)

PREFLIGHT_RUNGS = ("antonym", "add3_mid")
N_ITEMS_PREFLIGHT = 20

# `_assert_provenance`/`_release` come from `_common_2i` (Task 2 review
# finding 1 — byte-identical across sample_2i.py/endpoint_2i.py/this
# module); local underscore names kept so this module's own calls
# resolve unchanged. Preflight writes no record, so it has no need for
# `_stack`/`_git_sha`.


def real_loaders() -> dict:
    from harness import HFRunner

    def olmo1b_main(commit, device):
        # a2d.SAMPLING_DTYPE (float32) — one load serves both the greedy
        # format check and the sampled item below; the format check does
        # not depend on dtype.
        return bi.load_thin(bi.REPO_1B, commit, device=device,
                            dtype=a2d.SAMPLING_DTYPE)

    return {"olmo1b_main": olmo1b_main, "runner": lambda tok, model: HFRunner(tok, model)}


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

    from harness import MAX_NEW_TOKENS, render_prompt

    # 3c's total wrapper (draw-side IndexError -> False, answer side
    # stays a hard error) — the same verify criterion every stage uses,
    # not `harness.verify` directly: a malformed OLMo continuation the
    # normalizer can't parse prints `verify=0` rather than crashing the
    # preflight (review minor).
    verify_fn = a2d.load_verify()

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
                bit = int(bool(verify_fn(cont, str(it["answer"]), cap["answer_type"])))
                tail = prompt[-80:].replace("\n", "\\n")
                print(f"[2i preflight] {rung} …{tail!r} -> {cont!r} verify={bit}",
                      flush=True)

        # ONE sampled item (design §7, ratified dial j / doc slip (m)):
        # antonym item 0, k=2 draws, seed 0, through exp3's frozen
        # sampler — the same call shape sample_2i.run_sampling_rung
        # uses. Exercised here, before the tag, because that sampler
        # has never touched an OLMo-2 model.
        sampler_fn = loaders.get("sampler")
        if sampler_fn is None:
            from experiments.exp3.sampler import sample_item
            sampler_fn = sample_item
        cap0 = bt.load_item_file("antonym")
        shots0 = [tuple(s) for s in cap0["shots"]][:bt.N_SHOTS]
        item0 = cap0["eval_items"][0]
        prompt0 = render_prompt(item0["question"], shots0)
        terminal_ids = tuple(sorted(set(tok.all_special_ids)))
        got = sampler_fn(model, tok, prompt0, rung="antonym", size=bi.SIZE_PRED,
                         mode="trained", item_idx=0, seeds=(bi.SAMPLING_SEED,),
                         draws_per_seed=2, max_new_tokens=bt.max_new_tokens("antonym"),
                         terminal_ids=terminal_ids)
        for draw in got[bi.SAMPLING_SEED]:
            bit = int(bool(verify_fn(draw, str(item0["answer"]), cap0["answer_type"])))
            print(f"[2i preflight] sampled antonym item=0 seed={bi.SAMPLING_SEED} "
                  f"-> {draw!r} verify={bit}", flush=True)
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
