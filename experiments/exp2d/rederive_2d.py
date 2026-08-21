"""Gate 1 ON THE PRODUCTION PATH (design §3, §6): the main tier's
seed-0, 64-draw streams for `reverse_string` and `rev_string7` at
410m and 1b ARE exp3's committed streams (same sampler, same formula,
same namespace, same item files, same token budget, same dtype). As
each of those four rungs lands, the runner hands its freshly sampled
rows here; the comparison against exp3's committed bytes is written
as a record beside the rung, and ANY differing draw halts the
campaign (no later rung is interpretable) and is INSUFFICIENT_DATA at
the verdict.

There is no rehearsal cell and no re-derivation run: the comparison
input is the production output itself. The comparator is 3d's
`diff_seed` (frozen, sha-pinned, imported); coverage is asserted
around it against the pinned 500 × 64 (3d freeze F2: a comparator
that only checks self-consistency passes a truncated stream); the
committed shard must hash to the §4 literal BEFORE the comparison
(3c finding B); and the verified draws the regenerated stream carries
are recorded by address and must equal exp3's (item 436 / draw 6 at
reverse_string/1b; none elsewhere).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2D = Path(__file__).resolve().parent
EXPERIMENTS = EXP2D.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))

from experiments.exp2d import analyze_2d as a  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402

DPS = a.TIERS["main"]["draws_per_seed"]
SEED = a.GATE1_SEED


def committed_shard_paths(rung, size, exp3_root=a.EXP3) -> tuple:
    d = Path(exp3_root) / "results" / "sampling" / f"{size}_{a.MODE}"
    return d / f"{rung}.json", d / f"{rung}.draws.jsonl.gz"


def gate1_record_2d(rung, size, *, diffs, fires_reproduced,
                    committed_gz_sha, items_sha, model_sha, stack,
                    n_items=a.N_ITEMS) -> dict:
    """The comparison record analyze_2d's loader validates."""
    return {
        "rung": rung, "size": size, "mode": a.MODE,
        "tier": "main", "on_production_path": True,
        "n_items": int(n_items),
        "seeds_rederived": [SEED],
        "draws_per_seed": DPS,
        "draws_compared": int(n_items) * DPS,
        "n_diffs": len(diffs),
        "diffs": diffs,
        "fires_reproduced": sorted(
            [{"item": int(f["item"]), "seed": int(f["seed"]),
              "draw": int(f["draw"])} for f in fires_reproduced],
            key=lambda x: (x["item"], x["seed"], x["draw"])),
        "committed_draws_sha256": committed_gz_sha,
        "committed_shard": f"{rung}.draws.jsonl.gz",
        "items_sha256": items_sha,
        "model_sha": model_sha,
        "dtype": a.SAMPLING_DTYPE,
        "stack": stack,
    }


def compare_rows(rung, size, rows, *, answers, answer_type, verify_fn,
                 exp3_root=a.EXP3, committed_shas=None) -> dict:
    """Pure comparison of freshly sampled main-tier rows against exp3's
    committed seed-0 streams. Returns (diffs, fires, committed sha).
    Hard errors: committed shard not at its §4 literal; committed
    record's provenance not the battery's; coverage not 500 × 64."""
    from experiments.exp3.run.run_cell import read_draws
    from experiments.exp3d.rederive_3d import diff_seed

    committed_shas = a.COMMITTED_DRAWS_SHA256 if committed_shas is None \
        else committed_shas
    rec_p, gz_p = committed_shard_paths(rung, size, exp3_root)
    committed = json.loads(rec_p.read_text())
    if committed.get("draws_per_seed") != DPS or \
            SEED not in committed.get("seeds", []):
        raise ValueError(f"{rec_p}: seeds {committed.get('seeds')} / dps "
                         f"{committed.get('draws_per_seed')} — no seed-{SEED}"
                         f" {DPS}-draw stream to compare against")
    if committed.get("items_sha256") != bt.ITEMS_SHA_PIN[rung]:
        raise ValueError(f"{rec_p}: items_sha256 "
                         f"{committed.get('items_sha256')} != the §4 pin")
    if [str(x) for x in committed.get("answers", [])] != list(answers):
        raise ValueError(f"{rec_p}: answers disagree with the battery's")
    if committed.get("answer_type") != answer_type:
        raise ValueError(f"{rec_p}: answer_type {committed.get('answer_type')}")
    gz_sha = hashlib.sha256(gz_p.read_bytes()).hexdigest()
    want = committed_shas[rung][size]
    if gz_sha != want:
        raise ValueError(f"committed exp3 shard {gz_p} hashes to {gz_sha} "
                         f"against the §4 literal {want} — the comparison "
                         f"target is not the committed stream")
    committed_rows = read_draws(gz_p)
    if len(committed_rows) != a.N_ITEMS:
        raise ValueError(f"{gz_p}: {len(committed_rows)} committed items")
    regenerated = {}
    for row in rows:
        i = int(row["item"])
        if i in regenerated:
            raise ValueError(f"duplicate regenerated item {i}")
        regenerated[i] = list(row["draws"][str(SEED)])
    if sorted(regenerated) != list(range(a.N_ITEMS)):
        raise ValueError(f"regenerated coverage is {len(regenerated)} items, "
                         f"not the pinned {a.N_ITEMS}")
    diffs = diff_seed(committed_rows, regenerated, dps=DPS, seed=SEED)
    fires = [{"item": i, "seed": SEED, "draw": d_idx}
             for i in sorted(regenerated)
             for d_idx, text in enumerate(regenerated[i])
             if verify_fn(text, answers[i], answer_type)]
    return {"diffs": diffs, "fires": fires, "committed_gz_sha": gz_sha,
            "draws_compared": len(regenerated) * DPS}


def record_and_halt_on_diff(rung, size, rows, *, answers, answer_type,
                            verify_fn, items_sha, model_sha, stack,
                            out_root=a.EXP2D, exp3_root=a.EXP3) -> dict:
    """Write the gate-1 record beside the rung; RAISE on any diff so
    the campaign halts (the record is written first — the failure IS
    the disclosure)."""
    cmp = compare_rows(rung, size, rows, answers=answers,
                       answer_type=answer_type, verify_fn=verify_fn,
                       exp3_root=exp3_root)
    rec = gate1_record_2d(rung, size, diffs=cmp["diffs"],
                          fires_reproduced=cmp["fires"],
                          committed_gz_sha=cmp["committed_gz_sha"],
                          items_sha=items_sha, model_sha=model_sha,
                          stack=stack)
    out = a.gate1_record_path(out_root, size, rung)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    status = "IDENTICAL" if not cmp["diffs"] else f"{len(cmp['diffs'])} DIFFS"
    print(f"[2d gate1] {rung}/{size}: {rec['draws_compared']} draws "
          f"compared on the production path, {status}; fires at "
          f"{[(f['item'], f['draw']) for f in cmp['fires']]}", flush=True)
    if cmp["diffs"]:
        raise RuntimeError(
            f"GATE 1 FIRED at {rung}/{size}: {len(cmp['diffs'])} of "
            f"{rec['draws_compared']} production-path draws differ from "
            f"exp3's committed seed-0 bytes (first: {cmp['diffs'][0]}). "
            f"The generation law drifted; no later rung is interpretable. "
            f"Campaign halted; INSUFFICIENT_DATA at the verdict.")
    return rec
