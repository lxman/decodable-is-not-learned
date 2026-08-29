# experiments/exp2k/run/rehearse_2k.py
"""Exp 2k pre-tag rehearsal (design §10 dial i, checklist item 24): the
ONE path element new to this stack is `sample_item` called with FOUR
seeds per item and the per-item gate-1 comparison behind it. Rehearse
it on ONE item of ONE rung at 1b: 256 draws, the seed-0 block required
identical to 2d's committed row, seeds 1–3 printed. Prints to STDOUT
ONLY; asserts afterwards that nothing under `<out_root>/results` was
created. Runs only on Michael's word.

Usage: python -m experiments.exp2k.run.rehearse_2k [--rung antonym] [--item 0]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXP2K = Path(__file__).resolve().parents[1]
REPO = EXP2K.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2i.run._common_2i import release as _release  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2k.run.tier_2k import _prompts, real_loader  # noqa: E402


def _snapshot(root) -> set:
    base = Path(root) / "results"
    return {p for p in base.rglob("*")} if base.exists() else set()


def run(*, rung="antonym", item=0, size="1b", out_root=EXP2K, device="mps", loader=None,
        sampler=None) -> dict:
    before = _snapshot(out_root)
    from experiments.exp3.sampler import sample_item
    sampler_fn = sampler or sample_item
    cap = bt.load_item_file(rung)
    prompt = _prompts(cap)[item]
    answer = str(cap["eval_items"][item]["answer"])
    verify_fn = a2d.load_verify()
    committed = bk.committed_by_item(bk.committed_rows(size, rung))[item]
    tok, model, model_sha = (loader or real_loader)(size, device)
    try:
        terminal = tuple(sorted(set(tok.all_special_ids)))
        got = sampler_fn(model, tok, prompt, rung=rung, size=size, mode=bk.MODE, item_idx=item,
                         seeds=bk.SEEDS_2K, draws_per_seed=bk.DRAWS_PER_SEED,
                         max_new_tokens=bt.max_new_tokens(rung), terminal_ids=terminal)
    finally:
        _release(model)
    mine = [str(x) for x in got[bk.GATE1_SEED]]
    diffs = [(d, g, w) for d, (g, w) in enumerate(zip(mine, committed)) if g != w]
    n_draws = sum(len(got[s]) for s in bk.SEEDS_2K)
    print(f"[2k rehearsal] {rung}/{size} item {item}: model_sha {model_sha}; {n_draws} draws; "
          f"seed-0 block vs 2d's committed row: "
          f"{'IDENTICAL' if not diffs else f'{len(diffs)} DIFFS'}", flush=True)
    for s in bk.SEEDS_2K:
        v = sum(1 for d in got[s] if verify_fn(d, answer, cap["answer_type"]))
        print(f"  seed {s}: {v}/{len(got[s])} verified; first two draws {got[s][:2]!r}",
              flush=True)
    for d, g, w in diffs[:5]:
        print(f"  DIFF draw {d}: got {g!r} committed {w!r}", flush=True)
    after = _snapshot(out_root)
    if after - before:
        raise RuntimeError(f"the rehearsal created files under results/: "
                           f"{sorted(str(p) for p in after - before)[:5]}")
    return {"rung": rung, "size": size, "item": item, "model_sha": model_sha,
            "n_draws": n_draws, "seed0_identical": not diffs, "n_diffs": len(diffs)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2k pre-tag rehearsal (one item)")
    ap.add_argument("--rung", default="antonym")
    ap.add_argument("--item", type=int, default=0)
    ap.add_argument("--size", default="1b", choices=bk.SIZES_2K)
    ap.add_argument("--device", default="mps")
    ar = ap.parse_args(argv)
    r = run(rung=ar.rung, item=ar.item, size=ar.size, device=ar.device)
    return 0 if r["seed0_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
