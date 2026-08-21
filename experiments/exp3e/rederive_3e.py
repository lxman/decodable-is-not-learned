"""Gate 1 (design §10.3): byte re-derivation of 3d's committed 1b
seed-20 and 410m seed-24 reverse_string streams, RESTRICTED to the
45-item subset and driven through the PRODUCTION subset path —
2,880 draws per size, coverage pinned to exactly that literal, zero
tolerance.

The seeds are §4's choice because each carries repeat-class fires
(1b: items 348 'mhmp' and 430 'pbpd'; 410m: item 123 'ecde'): the
re-derivation must reproduce those fires at their committed (item,
draw) addresses through the very code path the tranche runs (3c's
lesson: test the path that runs, not a sibling). ANY differing draw →
INSUFFICIENT_DATA at the verdict; every differing draw is recorded
verbatim with its address. The re-derived draws are DISCARDED after
comparison; what persists is the comparison record — counts, diffs,
the fires the regenerated stream carries, and the sha256 of the 3d
shard compared against, which analyze_3e checks against both the
tree on disk and the §4 literal pin (3c finding B, both directions).

The comparator is 3d's own `diff_seed` (frozen, sha-pinned, imported
— never copied); coverage is asserted around it against the subset
literal (3d freeze finding F2: a comparator that only checks
self-consistency passes a truncated re-derivation).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP3E = Path(__file__).resolve().parent
EXPERIMENTS = EXP3E.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from experiments.exp3d import analyze_3d as d  # noqa: E402
from experiments.exp3d.rederive_3d import diff_seed  # noqa: E402
from experiments.exp3e import scorer_3e as sc  # noqa: E402
from experiments.exp3e.analyze_3e import (  # noqa: E402
    COMMITTED_DRAWS_SHA256, DRAWS_PER_SEED_3E, EXP3D, GATE1_SEED_3E,
    ITEMS_SHA_PIN, RUNG, SIZES_3E, SUBSET_ITEMS_PIN,
    check_frozen_imports_3e, gate1_shard_block, subset_sha256,
)


def gate1_record_3e(size, *, items, diffs, fires_reproduced,
                    committed_gz_sha, committed_shard, items_sha,
                    model_sha, stack) -> dict:
    """The comparison record analyze_3e's loader validates."""
    items = [int(i) for i in items]
    return {
        "rung": RUNG, "size": size, "mode": "trained",
        "n_items": len(items),
        "items": items,
        "subset_sha256": subset_sha256(items),
        "seeds_rederived": [GATE1_SEED_3E[size]],
        "draws_per_seed": DRAWS_PER_SEED_3E,
        "draws_compared": len(items) * DRAWS_PER_SEED_3E,
        "n_diffs": len(diffs),
        "diffs": diffs,
        "fires_reproduced": sorted(
            [{"item": int(f["item"]), "seed": int(f["seed"]),
              "draw": int(f["draw"])} for f in fires_reproduced],
            key=lambda a: (a["item"], a["seed"], a["draw"])),
        "committed_draws_sha256": committed_gz_sha,
        "committed_shard": committed_shard,
        "items_sha256": items_sha,
        "model_sha": model_sha,
        "dtype": "float32",
        "stack": stack,
    }


def subset_committed_rows(rows, items) -> list:
    """The committed shard's rows restricted to the subset, in subset
    order; refuses a shard that does not carry every subset item
    (coverage is pinned around the comparator — 3d F2)."""
    by = {int(r["item"]): r for r in rows}
    missing = [int(i) for i in items if int(i) not in by]
    if missing:
        raise ValueError(
            f"committed shard does not carry every subset item "
            f"(missing {missing}) — the comparison would be incomplete")
    return [by[int(i)] for i in items]


def record_path(out_root, size) -> Path:
    return (Path(out_root) / "results" / "gate1" / f"{size}_trained"
            / f"{RUNG}.json")


def rederive_cell_3e(size, out_root=EXP3E, exp3d_root=EXP3D,
                     model_ctx=None, items=SUBSET_ITEMS_PIN) -> dict:
    """Re-derive one cell's committed gate-1 seed for the 45 items
    end to end through the production subset path and write its
    comparison record. Skip-if-exists. The committed 3d shard must
    match the §4 literal pin BEFORE regeneration; the item file must
    match the shard's and the §4 pin BEFORE any model contact."""
    out = record_path(out_root, size)
    if out.exists():
        return json.loads(out.read_text())
    check_frozen_imports_3e()

    from experiments.exp3.run.run_cell import (  # noqa: PLC0415
        _assert_module_provenance, _load_model, load_capability,
        read_draws,
    )
    from experiments.exp3.sampler import sample_item  # noqa: PLC0415
    from harness import render_prompt  # noqa: PLC0415 — 2c's, asserted

    _assert_module_provenance()
    if size not in SIZES_3E:
        raise ValueError(f"{size!r} is not a 3e gate-1 size")
    seed = GATE1_SEED_3E[size]
    block = gate1_shard_block(size)
    shard = d.shard_name(block)
    rec_p = (Path(exp3d_root) / "results" / "sampling"
             / f"{size}_trained" / f"{shard}.json")
    gz_p = (Path(exp3d_root) / "results" / "sampling"
            / f"{size}_trained" / f"{shard}.draws.jsonl.gz")
    committed = json.loads(rec_p.read_text())
    if committed.get("draws_per_seed") != DRAWS_PER_SEED_3E:
        raise ValueError(
            f"committed shard {rec_p} carries draws_per_seed "
            f"{committed.get('draws_per_seed')} against 3d's frozen "
            f"{DRAWS_PER_SEED_3E}")
    if seed not in committed.get("seeds", []):
        raise ValueError(
            f"committed shard {rec_p} carries seeds "
            f"{committed.get('seeds')} — no seed {seed} stream to "
            f"re-derive")
    committed_gz_sha = hashlib.sha256(gz_p.read_bytes()).hexdigest()
    want_sha = COMMITTED_DRAWS_SHA256[RUNG][size]["3d"][shard]
    if Path(exp3d_root) == EXP3D and committed_gz_sha != want_sha:
        raise ValueError(
            f"committed 3d shard {gz_p} has sha256 {committed_gz_sha} "
            f"against the §4 pin {want_sha} — the comparison target is "
            f"not the committed stream")

    cap, items_path = load_capability(RUNG)
    items_sha = hashlib.sha256(items_path.read_bytes()).hexdigest()
    if items_sha != committed["items_sha256"]:
        raise ValueError(
            f"item file {items_path} has sha256 {items_sha} against "
            f"the committed shard's {committed['items_sha256']} — the "
            f"prompts would not be the committed prompts")
    if Path(exp3d_root) == EXP3D and items_sha != ITEMS_SHA_PIN[RUNG]:
        raise ValueError(
            f"item file sha {items_sha} against the §4 pin "
            f"{ITEMS_SHA_PIN[RUNG]}")
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    if answers != [str(x) for x in committed["answers"]]:
        raise ValueError(
            f"item answers disagree with the committed shard's for "
            f"{RUNG}/{size} — not the committed battery")
    shots = [tuple(s) for s in cap["shots"]][:2]
    answer_type = cap["answer_type"]

    import torch          # noqa: PLC0415
    import transformers   # noqa: PLC0415

    tok, model, model_sha = model_ctx if model_ctx else \
        _load_model(size, "trained", "float32")
    terminal = tuple(sorted(set(tok.all_special_ids)))

    items = [int(i) for i in items]
    committed_rows = subset_committed_rows(read_draws(gz_p), items)
    regenerated = {}
    for j, i in enumerate(items):
        it = cap["eval_items"][i]
        prompt = render_prompt(it["question"], shots)
        got = sample_item(model, tok, prompt, rung=RUNG, size=size,
                          mode="trained", item_idx=i, seeds=(seed,),
                          draws_per_seed=DRAWS_PER_SEED_3E,
                          terminal_ids=terminal)
        regenerated[i] = got[seed]
        if (j + 1) % 15 == 0:
            print(f"[3e gate1] {RUNG}/{size}: {j + 1}/{len(items)} "
                  f"items re-derived", flush=True)

    diffs = diff_seed(committed_rows, regenerated, dps=DRAWS_PER_SEED_3E,
                      seed=seed)
    if len(regenerated) != len(items):
        raise ValueError("regenerated coverage is not the subset")
    score = sc.load_scorer()
    fires = [{"item": i, "seed": seed, "draw": d_idx}
             for i in items
             for d_idx, text in enumerate(regenerated[i])
             if score(text, answers[i], answer_type)]
    rec = gate1_record_3e(
        size, items=items, diffs=diffs, fires_reproduced=fires,
        committed_gz_sha=committed_gz_sha,
        committed_shard=f"{shard}.draws.jsonl.gz",
        items_sha=items_sha, model_sha=model_sha,
        stack={"torch": torch.__version__,
               "transformers": transformers.__version__})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    status = "IDENTICAL" if not diffs else f"{len(diffs)} DIFFS"
    print(f"[3e gate1] {RUNG}/{size}: {rec['draws_compared']} draws "
          f"compared, {status}; fires reproduced at "
          f"{[(f['item'], f['draw']) for f in fires]}", flush=True)
    return rec
