"""Gate 1 (design §10.2): byte re-derivation of 3c's committed seed-8
reverse_string streams, both sizes — 64,000 draws total, zero
tolerance.

Before any new draw counts, the ENTIRE generation pipeline — model
load, fp32 upcast, prompt rendering, tokenization, the committed
stream formula at seed 8, the chunked sampling loop, terminal
truncation, decode — is exercised against committed bytes. Seed 8 is
the §4 choice because it CARRIES FIRES at both sizes ('ecde' at 410m,
'ecde'/'rxxxxd'/'fkjes' at 1b): re-deriving a fire-carrying stream is
the strongest byte-identity check available — a drifted law that
still reproduces 64,000 draws including the fires byte-for-byte is
not drifted.

ANY differing draw → INSUFFICIENT_DATA at the verdict; every
differing draw is recorded verbatim with its (item, seed, draw)
address regardless of count. The re-derived draws are DISCARDED after
comparison; what persists is the comparison record — counts, diffs,
and the sha256 of the committed 3c draws file compared against, which
analyze_3d checks against both the tree on disk and the §4 literal
pin (finding B, both directions).

The comparator (`diff_seed`) is pure and model-free; the cell runner
around it is campaign code. The FREEZE session rehearses the full
path on ONE cell's committed bytes — a read + regenerate + compare
that creates no new quantity, the only sanctioned model contact
before tag `exp3d-preregistered`.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP3D = Path(__file__).resolve().parent
EXPERIMENTS = EXP3D.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from experiments.exp3d.analyze_3d import (  # noqa: E402
    COMMITTED_3C_DRAWS_SHA256, DRAWS_PER_SEED_3D, EXP3C, GATE1_SEED_3D,
    ITEMS_SHA_PIN, RUNG, SIZES_3D, check_frozen_imports_3d,
)


# ------------------------------------------------------ pure comparator

def diff_seed(committed_rows, regenerated, *, dps, seed) -> list:
    """Every differing draw between the committed seed-`seed` streams
    and the regenerated ones, verbatim with addresses. Zero tolerance
    is the VERDICT's job; this function's job is to miss nothing:
    incomplete coverage on either side is a hard error, never a
    silently shorter comparison (3a's class)."""
    diffs = []
    seen = set()
    for row in committed_rows:
        i = row["item"]
        seen.add(i)
        stream = row["draws"].get(str(seed))
        if not isinstance(stream, list) or len(stream) != dps:
            raise ValueError(
                f"committed item {i} carries "
                f"{len(stream) if isinstance(stream, list) else stream!r}"
                f" seed-{seed} draws against draws_per_seed {dps}")
        got = regenerated.get(i)
        if not isinstance(got, list) or len(got) != dps:
            raise ValueError(
                f"regenerated item {i} carries "
                f"{len(got) if isinstance(got, list) else got!r} draws "
                f"against draws_per_seed {dps} — the comparison would "
                f"be incomplete")
        for d_idx, (g, w) in enumerate(zip(got, stream)):
            if str(g) != str(w):
                diffs.append({"item": i, "seed": seed, "draw": d_idx,
                              "got": str(g), "committed": str(w)})
    extra = set(regenerated) - seen
    if extra:
        raise ValueError(
            f"regenerated streams for items {sorted(extra)} that the "
            f"committed record does not carry")
    return diffs


def gate1_record_3d(size, *, n_items, diffs, committed_gz_sha,
                    items_sha, model_sha, stack) -> dict:
    """The comparison record analyze_3d's loader validates."""
    return {
        "rung": RUNG, "size": size, "mode": "trained",
        "n_items": n_items,
        "seeds_rederived": [GATE1_SEED_3D],
        "draws_per_seed": DRAWS_PER_SEED_3D,
        "draws_compared": n_items * DRAWS_PER_SEED_3D,
        "n_diffs": len(diffs),
        "diffs": diffs,
        "committed_draws_sha256": committed_gz_sha,
        "items_sha256": items_sha,
        "model_sha": model_sha,
        "dtype": "float32",
        "stack": stack,
    }


# --------------------------------------------------------- cell runner

def record_path(out_root, size) -> Path:
    return (Path(out_root) / "results" / "gate1" / f"{size}_trained"
            / f"{RUNG}.json")


def rederive_cell_3d(size, out_root=EXP3D, exp3c_root=EXP3C,
                     model_ctx=None) -> dict:
    """Re-derive one cell's committed seed-8 stream end to end and
    write its comparison record. Skip-if-exists. The committed
    record's item pin must match the item file the prompts are built
    from BEFORE any model contact, and the committed 3c draws file
    must match the §4 literal pin BEFORE regeneration — a comparison
    against drifted bytes proves nothing either way."""
    out = record_path(out_root, size)
    if out.exists():
        return json.loads(out.read_text())
    check_frozen_imports_3d()

    from experiments.exp3.run.run_cell import (  # noqa: PLC0415
        _assert_module_provenance, _load_model, load_capability,
        read_draws,
    )
    from experiments.exp3.sampler import sample_item  # noqa: PLC0415
    from harness import render_prompt  # noqa: PLC0415 — 2c's, asserted

    _assert_module_provenance()
    if size not in SIZES_3D:
        raise ValueError(f"{size!r} is not a 3d gate-1 size")

    rec_p = (Path(exp3c_root) / "results" / "sampling"
             / f"{size}_trained" / f"{RUNG}.json")
    gz_p = (Path(exp3c_root) / "results" / "sampling"
            / f"{size}_trained" / f"{RUNG}.draws.jsonl.gz")
    committed = json.loads(rec_p.read_text())
    dps = committed["draws_per_seed"]
    if dps != DRAWS_PER_SEED_3D:
        raise ValueError(
            f"committed record {rec_p} carries draws_per_seed {dps} "
            f"against 3c's frozen {DRAWS_PER_SEED_3D}")
    if GATE1_SEED_3D not in committed["seeds"]:
        raise ValueError(
            f"committed record {rec_p} carries seeds "
            f"{committed['seeds']} — no seed {GATE1_SEED_3D} stream to "
            f"re-derive")
    committed_gz_sha = hashlib.sha256(gz_p.read_bytes()).hexdigest()
    if exp3c_root == EXP3C and \
            committed_gz_sha != COMMITTED_3C_DRAWS_SHA256[size]:
        raise ValueError(
            f"committed 3c draws file {gz_p} has sha256 "
            f"{committed_gz_sha} against the §4 pin "
            f"{COMMITTED_3C_DRAWS_SHA256[size]} — the comparison "
            f"target is not the committed stream")

    cap, items_path = load_capability(RUNG)
    items_sha = hashlib.sha256(items_path.read_bytes()).hexdigest()
    if items_sha != committed["items_sha256"]:
        raise ValueError(
            f"item file {items_path} has sha256 {items_sha} against "
            f"the committed cell's {committed['items_sha256']} — the "
            f"prompts would not be the committed prompts")
    if exp3c_root == EXP3C and items_sha != ITEMS_SHA_PIN[RUNG]:
        raise ValueError(
            f"item file sha {items_sha} against the §4 pin "
            f"{ITEMS_SHA_PIN[RUNG]}")
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    if answers != [str(x) for x in committed["answers"]]:
        raise ValueError(
            f"item answers disagree with the committed record's for "
            f"{RUNG}/{size} — not the committed battery")
    shots = [tuple(s) for s in cap["shots"]][:2]

    import torch          # noqa: PLC0415
    import transformers   # noqa: PLC0415

    tok, model, model_sha = model_ctx if model_ctx else \
        _load_model(size, "trained", "float32")
    terminal = tuple(sorted(set(tok.all_special_ids)))

    committed_rows = read_draws(gz_p)
    regenerated = {}
    for i, it in enumerate(cap["eval_items"]):
        prompt = render_prompt(it["question"], shots)
        got = sample_item(model, tok, prompt, rung=RUNG, size=size,
                          mode="trained", item_idx=i,
                          seeds=(GATE1_SEED_3D,), draws_per_seed=dps,
                          terminal_ids=terminal)
        regenerated[i] = got[GATE1_SEED_3D]
        if (i + 1) % 100 == 0:
            print(f"[3d gate1] {RUNG}/{size}: {i + 1}/{len(answers)} "
                  f"items re-derived", flush=True)

    diffs = diff_seed(committed_rows, regenerated, dps=dps,
                      seed=GATE1_SEED_3D)
    rec = gate1_record_3d(
        size, n_items=len(answers), diffs=diffs,
        committed_gz_sha=committed_gz_sha, items_sha=items_sha,
        model_sha=model_sha,
        stack={"torch": torch.__version__,
               "transformers": transformers.__version__})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    status = "IDENTICAL" if not diffs else f"{len(diffs)} DIFFS"
    print(f"[3d gate1] {RUNG}/{size}: {rec['draws_compared']} draws "
          f"compared, {status}", flush=True)
    return rec
