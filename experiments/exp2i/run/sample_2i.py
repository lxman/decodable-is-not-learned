# experiments/exp2i/run/sample_2i.py
"""Exp 2i stage 1 — the predictor's sampled draws (x_B): OLMo-2 1B at
its stage-1 endpoint, 64 pure T=1.0 draws per item (seed 0), on all 34
rungs (design §3.2, §7). One model load, rungs skip-if-exists,
whole-file writes — 2d's `run_sampling_rung` protocol reproduced with
2i's paths/labels (no tiers: 2i samples once, at 2d's main-tier
(seed, k)).

Order, load-bearing: (1) the prereg refusal (`require_prereg_2i` —
Task 3's `analyze_2i` module if it exists, else the fail-closed stub
at `run/_prereg_stub_2i.py`); (2) `check_frozen_2i()`; (3) refuses if
`predictor_2i.json` already exists (sealed = done, ruling: the
sampling stage runs once). Everything frozen is imported from the
exp2d/exp2c/exp3/exp3c trees, never copied — except `write_draws`,
copied verbatim below (ruling 6) rather than imported through
`exp2d.run.run_cell_2d`, whose own import chain mutates `sys.path` as
a side effect (its module docstring calls the exp2b/exp2c insertion
order "load-bearing, not cosmetic") that this module has no reason to
inherit.

Usage: python -m experiments.exp2i.run.sample_2i [--dry-run]
"""

from __future__ import annotations

import argparse
import gzip
import json
import subprocess
import sys
import time
from pathlib import Path

EXP2I = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2I.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp3.sampler import STREAM_NAMESPACE, sample_item  # noqa: E402

try:
    from experiments.exp2i.analyze_2i import require_prereg_2i  # noqa: E402
except ImportError:
    from experiments.exp2i.run._prereg_stub_2i import require_prereg_2i  # noqa: E402


# ------------------------------------------------- write_draws (ruling 6)
#
# Copied verbatim from experiments/exp3/run/run_cell.py:write_draws
# (sha256 of inspect.getsource(write_draws):
# 664c001a015a9a7d07758605771e8e672cc8cf3045c3e9cf87f03a5138f80511),
# rather than imported through exp2d.run.run_cell_2d (see module
# docstring). `test_write_draws_is_byte_identical_to_exp3_source` in
# test_stages_2i.py re-derives this sha and compares the live source of
# both functions, so a drift in either one is caught, not silently
# tolerated.

def write_draws(path, rows) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


# ------------------------------------------------------------- helpers

def _stack() -> dict:
    try:
        import torch
        import transformers
        return {"torch": torch.__version__, "transformers": transformers.__version__}
    except ImportError:                     # fakes in tests
        return {"torch": "n/a", "transformers": "n/a"}


def _git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()


def _assert_provenance() -> None:
    import harness
    got = Path(sys.modules["harness"].__file__).resolve()
    if bi.EXP2C.resolve() not in got.parents:
        raise ImportError(f"harness resolved to {got}, not under {bi.EXP2C}")


def real_loaders() -> dict:
    def olmo1b(commit, device):
        return bi.load_thin(bi.REPO_1B, commit, device=device, dtype="float32")
    return {"olmo1b": olmo1b}


def _release(model) -> None:
    if model is None:      # a load failure can leave the caller's slot empty
        return
    try:
        import torch
        del model
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:      # noqa: BLE001 — fakes
        pass


def _prompts(cap) -> list:
    from harness import render_prompt   # 2c's, provenance-asserted
    shots = [tuple(s) for s in cap["shots"]][:bt.N_SHOTS]
    return [render_prompt(it["question"], shots) for it in cap["eval_items"]]


# ------------------------------------------------------------ the rung

def run_sampling_rung(rung, *, out_root=EXP2I, model_ctx=None, verify_fn=None,
                      sampler=None) -> dict:
    """One rung's 64 seed-0 draws per item at OLMo-2 1B's stage-1
    endpoint. `model_ctx` = (tok, model, info, commit); `sampler`
    defaults to exp3's frozen `sample_item`, injectable for tests."""
    out = bi.predictor_record_path(out_root, rung)
    dpath = bi.predictor_draws_path(out_root, rung)
    if out.exists() and dpath.exists():
        return json.loads(out.read_text())
    if model_ctx is None:
        raise RuntimeError("run_sampling_rung: no model context — call via run() "
                           "or supply model_ctx=(tok, model, info, commit)")
    bi.check_frozen_2i()
    _assert_provenance()
    sampler_fn = sampler or sample_item
    cap = bt.load_item_file(rung)
    prompts = _prompts(cap)
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    verify_fn = verify_fn or a2d.load_verify()
    tok, model, info, commit = model_ctx
    terminal = tuple(sorted(set(tok.all_special_ids)))
    budget = bt.max_new_tokens(rung)

    rows = []
    for i, prompt in enumerate(prompts):
        got = sampler_fn(model, tok, prompt, rung=rung, size=bi.SIZE_PRED,
                         mode="trained", item_idx=i, seeds=(bi.SAMPLING_SEED,),
                         draws_per_seed=bi.DRAWS_PER_ITEM, max_new_tokens=budget,
                         terminal_ids=terminal)
        rows.append({"item": i,
                    "draws": {str(bi.SAMPLING_SEED): got[bi.SAMPLING_SEED]}})
        if (i + 1) % 100 == 0:
            print(f"[2i sample] {rung}: {i + 1}/{len(prompts)} items", flush=True)

    write_draws(dpath, rows)
    verified = sum(1 for row in rows
                  for d in row["draws"][str(bi.SAMPLING_SEED)]
                  if verify_fn(d, answers[row["item"]], cap["answer_type"]))
    n_draws = sum(len(row["draws"][str(bi.SAMPLING_SEED)]) for row in rows)
    rec = {"rung": rung, "family": bi.FAMILY, "size": bi.SIZE_PRED, "mode": "trained",
          "tier": "main", "revision": bi.REV_1B_ENDPOINT, "commit": commit,
          "n_items": len(rows), "answers": answers, "answer_type": cap["answer_type"],
          "n_shots": bt.N_SHOTS, "dtype": "float32", "untrained_seed": None,
          "model_sha": info.get("tensor_digest"),
          "weight_sha256": info.get("tensor_digest"),
          "items_sha256": cap["items_sha256"], "stream_namespace": STREAM_NAMESPACE,
          "seeds": [bi.SAMPLING_SEED], "draws_per_seed": bi.DRAWS_PER_ITEM,
          "k_total": bi.DRAWS_PER_ITEM, "max_new_tokens": budget,
          "temperature": 1.0, "truncation": "none",
          "per_seed_tallies": {str(bi.SAMPLING_SEED): {"full_string": int(verified),
                                                        "n_draws": int(n_draws)}},
          "draws_file": dpath.name, "stack": _stack(), "git_sha": _git_sha()}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    print(f"[2i sample] {rung}: {verified} verified in {n_draws} draws", flush=True)
    return rec


# ----------------------------------------------------------------- run

def run(*, root=EXP2I, device="mps", rungs=None, loaders=None, dry_run=False,
        tag_exists=None, blob_sha=None, sampler=None) -> None:
    prereg = require_prereg_2i(tag_exists=tag_exists, blob_sha=blob_sha)
    bi.check_frozen_2i()
    seal_path = bi.predictor_seal_path(root)
    if seal_path.exists():
        raise RuntimeError(f"refusing: {seal_path} already exists — the predictor "
                           f"is already sealed; the sampling stage runs once")
    rungs = tuple(rungs) if rungs is not None else tuple(bt.RUNGS)
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    manifest = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    pending = [r for r in rungs if not (bi.predictor_record_path(root, r).exists()
                                        and bi.predictor_draws_path(root, r).exists())]
    if dry_run:
        print(f"[2i sample] prereg tag {prereg['tag']!r}; would sample {len(pending)} "
              f"rung(s): {pending}", flush=True)
        return
    if not pending:
        print(f"[2i sample] nothing to do: all {len(rungs)} rung(s) already sampled",
              flush=True)
        return
    verify_fn = a2d.load_verify()
    entry = bi.entry_1b_endpoint(manifest)
    commit = entry["commit"]
    model, tok, info = loaders["olmo1b"](commit, device)
    try:
        for rung in rungs:
            run_sampling_rung(rung, out_root=root, model_ctx=(tok, model, info, commit),
                              verify_fn=verify_fn, sampler=sampler)
    finally:
        _release(model)
    print(f"[2i sample] complete: {len(rungs)} rung(s)", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2i predictor sampling stage "
                                             "(OLMo-2 1B, x_B)")
    ap.add_argument("--root", default=str(EXP2I))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(root=Path(ar.root), device=ar.device, dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
