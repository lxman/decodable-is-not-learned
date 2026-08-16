"""Exp 3 runner: one cell of one kind — redecode | mass | sampling.

Three cell kinds, one dtype policy (PROGRESS.md 2026-08-15, freeze to
ratify):

- redecode: 3b's greedy path VERBATIM — fp16, HFRunner.generate, 2c's
  render_prompt and MAX_NEW_TOKENS — because gate 2 byte-compares these
  cells against 3b's committed records, and 3b's bytes were made there.
- mass: fp32 (exact upcast of the same fp16 checkpoint), depth-2
  expansion, EXCEPT 12b: fp16 depth-1 (fp32 does not fit; the fp16
  batched-step path is the broken one, and depth-1 needs only the
  verified-sane batch-1 keep1 prompt forward).
- sampling: fp32, probe sizes only, seeded streams from the committed
  map, every raw draw stored.

Records carry provenance the analysis can check (model sha, item-file
sha, dtype, depth); referents live in analyze_3's frozen loaders, not
here (3a's lesson). Nothing under exp2b/ or exp2c/ is modified.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

EXP3 = Path(__file__).resolve().parents[1]

# ORDER MATTERS AND IS NOT COSMETIC (3b's runner, verbatim reasoning):
# exp2c must win the `harness` name — only its harness defines ITEMS_DIR,
# answer_type_of, verify, and the render_prompt that produced the
# committed numbers the gates check against; exp2b supplies `models`.
for _p in (EXP3.parent / "exp2b", EXP3.parent / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
if str(EXP3.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3.parent.parent))

from experiments.exp3.analyze_3 import (  # noqa: E402
    DRAWS_PER_SEED, EVAL_SIZES, PROBE_SIZES, RUNGS, SEEDS, SIZES,
    UNTRAINED_SEED, score_first_char,
)
from experiments.exp3 import masses as masses_mod  # noqa: E402
from experiments.exp3.sampler import sample_item  # noqa: E402

KINDS = ("redecode", "mass", "sampling")


def _assert_module_provenance() -> None:
    """Refuse to run unless each module resolved to the tree it must."""
    import harness
    import models

    want = {"harness": EXP3.parent / "exp2c",
            "models": EXP3.parent / "exp2b"}
    for name, root in want.items():
        got = Path(sys.modules[name].__file__).resolve()
        if root.resolve() not in got.parents:
            raise ImportError(
                f"{name!r} resolved to {got}, which is not under {root} — "
                f"this cell would be measured with the wrong tree's code")


# ------------------------------------------------------- dtype policy

def cell_policy(kind: str, size: str) -> tuple:
    """(dtype, mass_depth) for a cell. The ledgered table, executable."""
    if kind == "mass":
        if size == "12b":
            return ("float16", 1)
        if size not in SIZES:
            raise ValueError(f"unknown mass size {size!r}")
        return ("float32", 2)
    if kind == "sampling":
        if size not in PROBE_SIZES:
            raise ValueError(f"sampling runs at the probe sizes only, "
                             f"not {size!r}")
        return ("float32", None)
    if kind == "redecode":
        if size not in PROBE_SIZES:
            raise ValueError(f"redecode covers the 16 probe-size cells "
                             f"only, not {size!r}")
        return ("float16", None)
    raise ValueError(f"unknown cell kind {kind!r}")


# ------------------------------------------------------------- layout

def record_path(out_root, kind: str, rung: str, size: str, mode: str) -> Path:
    return Path(out_root) / "results" / kind / f"{size}_{mode}" / f"{rung}.json"


def draws_path(out_root, rung: str, size: str, mode: str) -> Path:
    return (Path(out_root) / "results" / "sampling" / f"{size}_{mode}"
            / f"{rung}.draws.jsonl.gz")


# ------------------------------------------------------------ tallies

def per_seed_tallies(rows, answers, labels, *, answer_type, seeds=SEEDS) -> dict:
    """Convenience tallies stored beside the raw draws. The analyzer
    recomputes from the raw draws and refuses disagreement — these
    exist for the ledger and the per-cell commit message, and are
    computed with 2c's own verify and 3b's own first_char."""
    from harness import verify  # noqa: PLC0415 — 2c's, provenance-asserted

    out = {str(s): {"full_string": 0, "first_char": 0, "n_draws": 0}
           for s in seeds}
    for row in rows:
        i = row["item"]
        for s in seeds:
            key = str(s)
            if key not in row["draws"]:
                raise ValueError(f"item {i} carries no stream for seed {s}")
            for d in row["draws"][key]:
                out[key]["n_draws"] += 1
                if verify(d, answers[i], answer_type):
                    out[key]["full_string"] += 1
                if score_first_char(d, labels[i]):
                    out[key]["first_char"] += 1
    return out


# ------------------------------------------------- draws storage

def write_draws(path, rows) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def read_draws(path) -> list:
    rows, seen = [], set()
    with gzip.open(Path(path), "rt") as f:
        for line in f:
            row = json.loads(line)
            if row["item"] in seen:
                raise ValueError(f"duplicate item {row['item']} in {path}")
            seen.add(row["item"])
            rows.append(row)
    return rows


# ---------------------------------------------------------- capability

def load_capability(rung: str) -> tuple:
    """3b's loader verbatim: 2c rungs take answer_type from SPECS; the
    2b survivor carries it inline. Returns (cap, items_path)."""
    from harness import ITEMS_DIR, answer_type_of

    p = ITEMS_DIR / f"{rung}.json"
    if p.is_file():
        cap = json.loads(p.read_text())
        cap["answer_type"] = answer_type_of(rung)
        return cap, p
    b = EXP3.parent / "exp2b" / "battery" / "items" / f"{rung}.json"
    return json.loads(b.read_text()), b


def _load_model(size: str, mode: str, dtype: str):
    import torch

    from models import PYTHIA_SHAS, load_pythia

    tok, model = load_pythia(size, untrained=(mode == "untrained"),
                             seed=UNTRAINED_SEED)
    if dtype == "float32":
        model = model.to(torch.float32)   # exact upcast, same weights
    return tok, model, PYTHIA_SHAS[size]


def _provenance(rung, size, mode, cap, items_path, dtype, model_sha) -> dict:
    return {
        "rung": rung, "size": size, "mode": mode,
        "n_items": len(cap["eval_items"]),
        "probe_labels": [str(it["probe_label"]) for it in cap["eval_items"]],
        "answers": [str(it["answer"]) for it in cap["eval_items"]],
        "answer_type": cap["answer_type"],
        "n_shots": 2,
        "dtype": dtype,
        "untrained_seed": UNTRAINED_SEED if mode == "untrained" else None,
        "model_sha": model_sha,
        "items_sha256": hashlib.sha256(items_path.read_bytes()).hexdigest(),
    }


# ------------------------------------------------------------ the cells

def run_redecode_cell(rung, size, mode, out_root=EXP3, model_ctx=None) -> dict:
    out = record_path(out_root, "redecode", rung, size, mode)
    if out.exists():
        return json.loads(out.read_text())
    _assert_module_provenance()
    from harness import MAX_NEW_TOKENS, HFRunner, render_prompt, verify

    dtype, _ = cell_policy("redecode", size)
    cap, items_path = load_capability(rung)
    shots = [tuple(s) for s in cap["shots"]][:2]
    prompts = [render_prompt(it["question"], shots)
               for it in cap["eval_items"]]
    tok, model, sha = model_ctx if model_ctx else _load_model(size, mode, dtype)
    conts = HFRunner(tok, model).generate(
        prompts, MAX_NEW_TOKENS[cap["answer_type"]])
    full = sum(verify(c, it["answer"], cap["answer_type"])
               for c, it in zip(conts, cap["eval_items"]))
    rec = {**_provenance(rung, size, mode, cap, items_path, dtype, sha),
           "continuations": conts,
           "full_string_correct": int(full),
           "max_new_tokens": MAX_NEW_TOKENS[cap["answer_type"]]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    return rec


def run_mass_cell(rung, size, mode, out_root=EXP3, model_ctx=None,
                  classes=None) -> dict:
    out = record_path(out_root, "mass", rung, size, mode)
    if out.exists():
        return json.loads(out.read_text())
    _assert_module_provenance()
    from harness import render_prompt

    dtype, depth = cell_policy("mass", size)
    cap, items_path = load_capability(rung)
    shots = [tuple(s) for s in cap["shots"]][:2]
    tok, model, sha = model_ctx if model_ctx else _load_model(size, mode, dtype)
    fc, ws, term = classes if classes else masses_mod.classify_tokenizer(
        tok, n_logits=model.config.vocab_size)

    items = []
    for it in cap["eval_items"]:
        prompt = render_prompt(it["question"], shots)
        label = str(it["probe_label"])
        if depth == 2:
            rec = masses_mod.collect_item(
                model, tok, prompt, label=label, first_chars=fc,
                ws_ids=ws, terminal_ids=term)
            rec["depth"] = 2
        else:
            import torch
            enc = tok(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                o = model(**enc, use_cache=False, logits_to_keep=1)
            probs1 = masses_mod._softmax_probs(o.logits[0, -1])
            rec = masses_mod.item_mass_record_depth1(
                probs1, fc, ws, label=label, terminal_ids=term)
        items.append(rec)

    rec = {**_provenance(rung, size, mode, cap, items_path, dtype, sha),
           "depth": depth, "items": items}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    return rec


def run_sampling_cell(rung, size, mode, out_root=EXP3, model_ctx=None) -> dict:
    out = record_path(out_root, "sampling", rung, size, mode)
    dpath = draws_path(out_root, rung, size, mode)
    if out.exists() and dpath.exists():
        return json.loads(out.read_text())
    _assert_module_provenance()
    from harness import render_prompt

    dtype, _ = cell_policy("sampling", size)
    cap, items_path = load_capability(rung)
    shots = [tuple(s) for s in cap["shots"]][:2]
    tok, model, sha = model_ctx if model_ctx else _load_model(size, mode, dtype)
    terminal = tuple(sorted(set(tok.all_special_ids)))

    rows = []
    for i, it in enumerate(cap["eval_items"]):
        prompt = render_prompt(it["question"], shots)
        got = sample_item(model, tok, prompt, rung=rung, size=size,
                          mode=mode, item_idx=i, seeds=SEEDS,
                          draws_per_seed=DRAWS_PER_SEED[rung],
                          terminal_ids=terminal)
        rows.append({"item": i,
                     "draws": {str(s): got[s] for s in SEEDS}})
    write_draws(dpath, rows)

    prov = _provenance(rung, size, mode, cap, items_path, dtype, sha)
    tallies = per_seed_tallies(rows, prov["answers"], prov["probe_labels"],
                               answer_type=cap["answer_type"], seeds=SEEDS)
    rec = {**prov,
           "seeds": list(SEEDS),
           "draws_per_seed": DRAWS_PER_SEED[rung],
           "k_total": DRAWS_PER_SEED[rung] * len(SEEDS),
           "per_seed_tallies": tallies,
           "draws_file": dpath.name}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    return rec


RUN = {"redecode": run_redecode_cell, "mass": run_mass_cell,
       "sampling": run_sampling_cell}


def run_tier(kind: str, size: str, mode: str, out_root=EXP3) -> list:
    """All four rungs' cells of one (kind, size, mode) tier in THIS
    process — one model load, cells sequential, skip-if-exists. The
    process boundary is the driver's job (tier-per-process)."""
    dtype, _ = cell_policy(kind, size)
    _assert_module_provenance()
    ctx = _load_model(size, mode, dtype)
    classes = (masses_mod.classify_tokenizer(
        ctx[0], n_logits=ctx[1].config.vocab_size)
        if kind == "mass" else None)
    out = []
    for rung in RUNGS:
        kw = {"model_ctx": ctx}
        if kind == "mass":
            kw["classes"] = classes
        r = RUN[kind](rung, size, mode, out_root=out_root, **kw)
        print(f"[3] {kind}/{size}/{mode}/{rung} done", flush=True)
        out.append(r)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--tier":
        run_tier(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        kind, rung, size, mode = sys.argv[1:5]
        RUN[kind](rung, size, mode)
