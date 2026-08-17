"""Gate 1: byte re-derivation of exp3's committed seed-0 streams
(design §6.1, doc Open item 3; PROGRESS.md reading 1).

Before any new draw counts, the ENTIRE generation pipeline — model
load, fp32 upcast, prompt rendering, tokenization, the committed
stream formula, the chunked sampling loop, terminal truncation, decode
— is exercised against 132,000 committed draws: seed 0 of the four
scored cells (64 draws/item) and of ctrl_copy/1b (8 draws/item,
exp3's committed depth for the control — a 64-draw re-derivation
would consume the generator differently at chunk plan (16,16,16,16)
vs (8,) and compare against nothing). ANY differing draw →
INSUFFICIENT_DATA at the verdict; every differing draw is recorded
verbatim with its (item, seed, draw) address regardless of count.

The re-derived draws are DISCARDED after comparison (design §3): what
persists is the comparison record — counts, diffs, and the sha256 of
the committed draws file compared against — which analyze_3c's
loader refuses to accept valueless.

The comparator (`diff_seed0`) is pure and model-free; the cell runner
around it is campaign code. The FREEZE session rehearses the full
path on ONE cell's committed bytes — a read + regenerate + compare
that creates no new quantity, the only sanctioned model contact
before tag `exp3c-preregistered`.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP3C = Path(__file__).resolve().parent
EXPERIMENTS = EXP3C.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from experiments.exp3 import analyze_3 as a3  # noqa: E402
from experiments.exp3c.analyze_3c import (  # noqa: E402
    EXP3, GATE1_CELLS, check_frozen_imports,
)

REDERIVE_SEED = 0    # exp3's committed seed 0 — the only stream re-derived


# ------------------------------------------------------ pure comparator

def diff_seed0(committed_rows, regenerated, *, dps) -> list:
    """Every differing draw between exp3's committed seed-0 streams and
    the regenerated ones, verbatim with addresses. Zero tolerance is
    the VERDICT's job; this function's job is to miss nothing:
    incomplete coverage on either side is a hard error, never a
    silently shorter comparison (a comparison that skipped draws would
    be a valueless gate-1 record — 3a's class)."""
    diffs = []
    seen = set()
    for row in committed_rows:
        i = row["item"]
        seen.add(i)
        committed = row["draws"][str(REDERIVE_SEED)]
        if len(committed) != dps:
            raise ValueError(
                f"committed item {i} carries {len(committed)} seed-0 "
                f"draws against draws_per_seed {dps}")
        got = regenerated.get(i)
        if not isinstance(got, list) or len(got) != dps:
            raise ValueError(
                f"regenerated item {i} carries "
                f"{len(got) if isinstance(got, list) else got!r} draws "
                f"against draws_per_seed {dps} — the comparison would "
                f"be incomplete")
        for d_idx, (g, w) in enumerate(zip(got, committed)):
            if str(g) != str(w):
                diffs.append({"item": i, "seed": REDERIVE_SEED,
                              "draw": d_idx, "got": str(g),
                              "committed": str(w)})
    extra = set(regenerated) - seen
    if extra:
        raise ValueError(
            f"regenerated streams for items {sorted(extra)} that the "
            f"committed record does not carry")
    return diffs


def gate1_record(rung, size, *, n_items, dps, diffs, committed_gz_sha,
                 items_sha, model_sha, stack) -> dict:
    """The comparison record analyze_3c's loader validates (reading 8)."""
    return {
        "rung": rung, "size": size, "mode": "trained",
        "n_items": n_items,
        "seeds_rederived": [REDERIVE_SEED],
        "draws_per_seed": dps,
        "draws_compared": n_items * dps,
        "n_diffs": len(diffs),
        "diffs": diffs,
        "committed_draws_sha256": committed_gz_sha,
        "items_sha256": items_sha,
        "model_sha": model_sha,
        "dtype": "float32",
        "stack": stack,
    }


# --------------------------------------------------------- cell runner

def record_path(out_root, rung, size) -> Path:
    return (Path(out_root) / "results" / "gate1" / f"{size}_trained"
            / f"{rung}.json")


def rederive_cell(rung, size, out_root=EXP3C, exp3_root=EXP3,
                  model_ctx=None) -> dict:
    """Re-derive one gate cell's committed seed-0 stream end to end and
    write its comparison record. Skip-if-exists (the campaign's
    durable, resumable unit). The committed record's item pin must
    match the item file the prompts are built from BEFORE any model
    contact — prompts that drifted make byte comparison meaningless."""
    out = record_path(out_root, rung, size)
    if out.exists():
        return json.loads(out.read_text())
    check_frozen_imports()

    from experiments.exp3.run.run_cell import (  # noqa: PLC0415
        _assert_module_provenance, _load_model, load_capability,
    )
    from experiments.exp3.sampler import sample_item  # noqa: PLC0415
    from harness import render_prompt  # noqa: PLC0415 — 2c's, asserted

    _assert_module_provenance()

    if (rung, size, "trained") not in GATE1_CELLS:
        raise ValueError(f"{rung}/{size} is not a gate-1 cell")

    rec_p = (Path(exp3_root) / "results" / "sampling" / f"{size}_trained"
             / f"{rung}.json")
    gz_p = (Path(exp3_root) / "results" / "sampling" / f"{size}_trained"
            / f"{rung}.draws.jsonl.gz")
    committed = json.loads(rec_p.read_text())
    dps = committed["draws_per_seed"]
    if dps != a3.DRAWS_PER_SEED[rung]:
        raise ValueError(
            f"committed record {rec_p} carries draws_per_seed {dps} "
            f"against exp3's frozen {a3.DRAWS_PER_SEED[rung]}")
    committed_gz_sha = hashlib.sha256(gz_p.read_bytes()).hexdigest()

    cap, items_path = load_capability(rung)
    items_sha = hashlib.sha256(items_path.read_bytes()).hexdigest()
    if items_sha != committed["items_sha256"]:
        raise ValueError(
            f"item file {items_path} has sha256 {items_sha} against the "
            f"committed cell's {committed['items_sha256']} — the prompts "
            f"would not be the committed prompts")
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    if answers != [str(x) for x in committed["answers"]]:
        raise ValueError(
            f"item answers disagree with the committed record's for "
            f"{rung}/{size} — not the committed battery")
    shots = [tuple(s) for s in cap["shots"]][:2]

    import torch          # noqa: PLC0415
    import transformers   # noqa: PLC0415

    tok, model, model_sha = model_ctx if model_ctx else \
        _load_model(size, "trained", "float32")
    terminal = tuple(sorted(set(tok.all_special_ids)))

    from experiments.exp3.run.run_cell import read_draws  # noqa: PLC0415
    committed_rows = read_draws(gz_p)

    regenerated = {}
    for i, it in enumerate(cap["eval_items"]):
        prompt = render_prompt(it["question"], shots)
        got = sample_item(model, tok, prompt, rung=rung, size=size,
                          mode="trained", item_idx=i,
                          seeds=(REDERIVE_SEED,), draws_per_seed=dps,
                          terminal_ids=terminal)
        regenerated[i] = got[REDERIVE_SEED]
        if (i + 1) % 100 == 0:
            print(f"[3c gate1] {rung}/{size}: {i + 1}/{len(answers)} "
                  f"items re-derived", flush=True)

    diffs = diff_seed0(committed_rows, regenerated, dps=dps)
    rec = gate1_record(
        rung, size, n_items=len(answers), dps=dps, diffs=diffs,
        committed_gz_sha=committed_gz_sha, items_sha=items_sha,
        model_sha=model_sha,
        stack={"torch": torch.__version__,
               "transformers": transformers.__version__})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    status = "IDENTICAL" if not diffs else f"{len(diffs)} DIFFS"
    print(f"[3c gate1] {rung}/{size}: {rec['draws_compared']} draws "
          f"compared, {status}", flush=True)
    return rec
