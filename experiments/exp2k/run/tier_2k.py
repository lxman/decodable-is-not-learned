# experiments/exp2k/run/tier_2k.py
"""Exp 2k — the k = 256 sampling tier for one size (design §3.1–3.2):
nine rungs (2i's committed R_CAP, alphabetical), 500 items, exp3's
frozen sampler at seeds (0, 1, 2, 3) × 64 draws, 2d's main-tier
protocol (fp32, CPU-float32 softmax, T = 1.0, no truncation), every
raw draw stored.

GATE 1 IS CONTINUOUS AND ON THE PRODUCTION PATH: seed 0 of every cell
is 2d's committed main-tier stream regenerated, and after every item's
`sample_item` returns, its 64 seed-0 draws are compared byte for byte
to 2d's committed row. The first mismatch writes `<rung>.HALTED`
(item, diffs) and `<rung>.HALTED.jsonl.gz` (the rows so far), writes
NO normal draws file (so skip-if-exists never treats a halted rung as
done), and raises. Any existing marker under the tier tree refuses
every later call: after a halt nothing is interpretable (2d's rule).

Order, load-bearing: the prereg refusal (`battery_2k.require_prereg_2k`
— the tag must bind analyze/battery/THIS file), 2g/2i/2k frozen pins,
2d's committed draws files at their 2i-pinned shas, the seal-exists
refusal (the tier runs once), the halt scan, seed freshness, THEN one
model load per size.

Usage: python -m experiments.exp2k.run.tier_2k --size 1b [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

EXP2K = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2K.parent
REPO = EXPERIMENTS.parent
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):   # 2d's order: load-bearing
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i.run._common_2i import (  # noqa: E402
    git_sha as _git_sha,
    release as _release,
    stack as _stack,
)
from experiments.exp2i.run.sample_2i import write_draws  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402


def real_loader(size, device):
    """(tok, model, model_sha) — exp3's `_load_model` (2b's `load_pythia`
    at the pinned revision, exact fp32 upcast); `device` is 2b's own
    policy (MPS), kept for the injectable signature."""
    from experiments.exp3.run.run_cell import _assert_module_provenance, _load_model
    _assert_module_provenance()
    return _load_model(size, bk.MODE, a2d.SAMPLING_DTYPE)


def _prompts(cap) -> list:
    from harness import render_prompt   # 2c's, provenance-asserted by bt.harness_2c
    shots = [tuple(s) for s in cap["shots"]][:bt.N_SHOTS]
    return [render_prompt(it["question"], shots) for it in cap["eval_items"]]


def rungs_2k(root_2i=bi.EXP2I) -> tuple:
    """R_CAP from 2i's committed rung-set record, alphabetical; must
    equal the design's literal."""
    try:
        rs = an2i._load_rung_set(root_2i)
    except (OSError, ValueError) as e:
        raise ValueError(f"2i rung set (R_CAP) unreadable: {e}") from e
    got = tuple(sorted(rs["R_CAP"]))
    if got != bk.R_CAP_DESIGN:
        raise ValueError(f"2i's R_CAP {got} != design §3.4's {bk.R_CAP_DESIGN}")
    return got


def tier_complete(root, size) -> bool:
    return all(bk.tier_record_path(root, size, r).exists()
               and bk.tier_draws_path(root, size, r).exists() for r in bk.R_CAP_DESIGN)


def _refuse_if_halted(out_root) -> None:
    m = bk.halt_markers(out_root)
    if m:
        raise RuntimeError(f"halted: gate 1 fired earlier ({[p.name for p in m]}); nothing "
                           f"later is interpretable — INSUFFICIENT_DATA at the verdict")


def run_rung(size, rung, *, out_root=EXP2K, model_ctx, verify_fn, sampler=None,
             committed_root=None) -> dict:
    """One cell: 500 items × 4 seeds × 64 draws, gate 1 item by item."""
    out = bk.tier_record_path(out_root, size, rung)
    dpath = bk.tier_draws_path(out_root, size, rung)
    if out.exists() and dpath.exists():
        return json.loads(out.read_text())
    _refuse_if_halted(out_root)
    from experiments.exp3.sampler import sample_item
    sampler_fn = sampler or sample_item
    cap = bt.load_item_file(rung)                      # sha-pinned
    prompts = _prompts(cap)
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    tok, model, model_sha = model_ctx
    if model_sha != bk.pythia_sha(size):
        raise RuntimeError(f"model_sha {model_sha!r} is not 2b's pinned {bk.pythia_sha(size)!r} "
                           f"for {size} — not the weights 2d sampled")
    # the gate-1 referent: 2d's committed record + rows for this cell
    crec_p = bk.committed_record_path(size, rung)
    cgz_p = bk.committed_draws_path(size, rung)
    crec = json.loads(crec_p.read_text())
    if crec.get("seeds") != [bk.GATE1_SEED] or crec.get("draws_per_seed") != bk.DRAWS_PER_SEED:
        raise RuntimeError(f"{crec_p}: not a seed-0 × 64 main-tier record")
    if crec.get("items_sha256") != cap["items_sha256"] or \
            [str(x) for x in crec.get("answers", [])] != answers or \
            crec.get("answer_type") != cap["answer_type"]:
        raise RuntimeError(f"{crec_p}: provenance disagrees with the pinned item file")
    if crec.get("model_sha") != model_sha:
        raise RuntimeError(f"{crec_p}: model_sha {crec.get('model_sha')} != {model_sha}")
    committed_gz_sha = hashlib.sha256(cgz_p.read_bytes()).hexdigest()
    committed_record_sha = hashlib.sha256(crec_p.read_bytes()).hexdigest()
    if committed_gz_sha != bi.PYTHIA_PREDICTOR_FILES[(size, rung)]:
        raise RuntimeError(f"{cgz_p}: sha {committed_gz_sha[:12]} is not 2i's pin — the "
                           f"comparison target is not the committed stream")
    committed = bk.committed_by_item(bk.committed_rows(size, rung))
    terminal = tuple(sorted(set(tok.all_special_ids)))
    budget = bt.max_new_tokens(rung)

    rows, t0 = [], time.time()
    for i, prompt in enumerate(prompts):
        got = sampler_fn(model, tok, prompt, rung=rung, size=size, mode=bk.MODE, item_idx=i,
                         seeds=bk.SEEDS_2K, draws_per_seed=bk.DRAWS_PER_SEED,
                         max_new_tokens=budget, terminal_ids=terminal)
        row = {"item": i, "draws": {str(s): [str(x) for x in got[s]] for s in bk.SEEDS_2K}}
        rows.append(row)
        mine, theirs = row["draws"][str(bk.GATE1_SEED)], committed[i]
        diffs = [{"item": i, "seed": bk.GATE1_SEED, "draw": d, "got": g, "committed": w}
                 for d, (g, w) in enumerate(zip(mine, theirs)) if g != w]
        if len(mine) != bk.DRAWS_PER_SEED or len(theirs) != bk.DRAWS_PER_SEED:
            diffs.append({"item": i, "seed": bk.GATE1_SEED, "draw": None,
                          "got": f"{len(mine)} draws", "committed": f"{len(theirs)} draws"})
        if diffs:
            # the failure IS the disclosure: marker + rows so far, no normal file
            write_draws(bk.halted_draws_path(out_root, size, rung), rows)
            m = bk.halt_marker_path(out_root, size, rung)
            m.parent.mkdir(parents=True, exist_ok=True)
            m.write_text(json.dumps({"rung": rung, "size": size, "item": i,
                                     "items_compared": i + 1, "n_diffs": len(diffs),
                                     "diffs": diffs[:5], "model_sha": model_sha,
                                     "committed_draws_sha256": committed_gz_sha,
                                     "stack": _stack(), "git_sha": _git_sha()}, indent=1))
            raise RuntimeError(
                f"GATE 1 FIRED at {rung}/{size} item {i}: {len(diffs)} seed-0 draw(s) differ "
                f"from 2d's committed bytes (first: {diffs[0]}). The generation law drifted; "
                f"no later cell is interpretable. Campaign halted; INSUFFICIENT_DATA at "
                f"the verdict.")
        if (i + 1) % 100 == 0:
            print(f"[2k {size}] {rung}: {i + 1}/{len(prompts)} items, gate 1 identical so "
                  f"far ({(time.time() - t0) / 60:.1f} min)", flush=True)

    write_draws(dpath, rows)
    rec = bk.tier_record_2k(rung=rung, size=size, cap=cap, rows=rows, verify_fn=verify_fn,
                            model_sha=model_sha, stack=_stack(), git_sha=_git_sha(),
                            seconds=time.time() - t0, committed_gz_sha=committed_gz_sha,
                            committed_record_sha=committed_record_sha,
                            gate1_items_compared=len(rows),
                            gate1_draws_compared=len(rows) * bk.DRAWS_PER_SEED)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    t = rec["per_seed_tallies"]
    print(f"[2k {size}] {rung}: gate 1 IDENTICAL on {rec['gate1']['draws_compared']} draws; "
          f"verified per seed {[t[str(s)]['full_string'] for s in bk.SEEDS_2K]} of "
          f"{bk.N_ITEMS * bk.DRAWS_PER_SEED} each; {rec['seconds'] / 60:.1f} min", flush=True)
    return rec


def run(size, *, out_root=EXP2K, root_2i=bi.EXP2I, device="mps", loader=None, sampler=None,
        dry_run=False, tag_exists=None, blob_sha=None) -> list:
    if size not in bk.SIZES_2K:
        raise ValueError(f"{size!r} is not one of {bk.SIZES_2K}")
    prereg = bk.require_prereg_2k(tag_exists=tag_exists, blob_sha=blob_sha)
    bg.check_frozen_imports_2g()
    bi.check_frozen_2i()
    bk.check_frozen_2k()
    bi.check_pythia_predictor_files()
    if bk.seal_path(out_root).exists():
        raise RuntimeError(f"refusing: {bk.seal_path(out_root)} exists — the tier is sealed; "
                           f"it runs once")
    _refuse_if_halted(out_root)
    rungs = rungs_2k(root_2i)
    fresh = bk.check_seed_freshness(rungs, sizes=(size,))
    pending = [r for r in rungs if not (bk.tier_record_path(out_root, size, r).exists()
                                        and bk.tier_draws_path(out_root, size, r).exists())]
    if dry_run:
        print(f"[2k {size}] prereg tag {prereg['tag']!r}; seeds {fresh['new_seeds']} fresh on "
              f"{fresh['cells']} cell(s); would sample {len(pending)} rung(s): {pending}",
              flush=True)
        return []
    if not pending:
        print(f"[2k {size}] nothing to do: all {len(rungs)} rung(s) already sampled", flush=True)
        return []
    verify_fn = a2d.load_verify()
    loader = loader or real_loader
    tok, model, model_sha = loader(size, device)
    out = []
    try:
        for rung in rungs:
            out.append(run_rung(size, rung, out_root=out_root, model_ctx=(tok, model, model_sha),
                                verify_fn=verify_fn, sampler=sampler))
    finally:
        _release(model)
    print(f"[2k {size}] tier complete: {len(rungs)} rung(s)", flush=True)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 2k k=256 sampling tier, one size")
    ap.add_argument("--size", required=True, choices=bk.SIZES_2K)
    ap.add_argument("--out-root", default=str(EXP2K))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(ar.size, out_root=Path(ar.out_root), device=ar.device, dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
