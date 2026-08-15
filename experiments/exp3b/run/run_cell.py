"""Exp 3b runner: one (rung, size, mode) cell.

Queries the model on 2c's own committed prompt — `render_prompt(question,
shots)` with the committed 2 shots, greedy decoding, 2c's MAX_NEW_TOKENS —
and stores the RAW CONTINUATION for every item, 3a's runner ported to the
full five-size ladder (410m/1b primary, 2.8b/6.9b/12b descriptive).

WHAT CHANGED FROM 3A'S RUNNER, AND WHY. `committed_2c_acc` is gone: no
branch of 3b's frozen tree reads results/m4/ (design §4), and embedding a
referent in the record is exactly where 3a's None entered its battery. The
record instead carries provenance the analysis can check against the
committed inclusion records: the pinned model revision sha and the sha256
of the item file the prompts were built from. Referents live in
analyze_3b's frozen loaders, not here.

Nothing under experiments/exp2b/ or experiments/exp2c/ is modified.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP3B = Path(__file__).resolve().parents[1]

# ORDER MATTERS AND IS NOT COSMETIC. Both trees carry a `harness`, a `battery`
# package and a `run` package. sys.path.insert(0) puts the LAST inserted
# FIRST, so exp2b goes in first and exp2c ends up ahead of it. exp2c must win:
# only its harness defines ITEMS_DIR, answer_type_of, verify and the
# render_prompt that produced the committed eval numbers this experiment's
# gates check against. exp2b supplies `models`, which exp2c does not define.
#
# 3a shipped this order INVERTED, corrected post-freeze (its PROGRESS.md).
# That crash was lucky: had exp2b's harness defined ITEMS_DIR, every cell
# would have run through the WRONG TREE — a different MAX_NEW_TOKENS and a
# different verify — and produced plausible wrong numbers. The assertion
# below exists so this can never again depend on luck.
for _p in (EXP3B.parent / "exp2b", EXP3B.parent / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def _assert_module_provenance() -> None:
    """Refuse to run unless each module resolved to the tree it must."""
    import harness
    import models

    want = {"harness": EXP3B.parent / "exp2c",
            "models": EXP3B.parent / "exp2b"}
    for name, root in want.items():
        got = Path(sys.modules[name].__file__).resolve()
        if root.resolve() not in got.parents:
            raise ImportError(
                f"{name!r} resolved to {got}, which is not under {root} — "
                f"this cell would be measured with the wrong tree's code")


PROBE_SIZES = ("410m", "1b")          # primary (design §3)
EVAL_SIZES = ("2.8b", "6.9b", "12b")  # descriptive
SIZES = PROBE_SIZES + EVAL_SIZES
MODES = ("trained", "untrained")
UNTRAINED_SEED = 0            # 2c's own, campaign_m4.UNTRAINED_SEED
RUNGS = ("rev_string7", "reverse_string", "ctrl_copy", "clock24_d999")


def record_path(out_root, rung: str, size: str, mode: str) -> Path:
    return Path(out_root) / "results" / f"{size}_{mode}" / f"{rung}.json"


def load_capability(rung: str) -> tuple[dict, Path]:
    """2c rungs take answer_type from SPECS; the 2b survivor carries it
    inline. Mirrors 3a's loader (itself mirroring campaign_m4) and also
    returns the item file's path so the record can pin what it was built
    from."""
    from harness import ITEMS_DIR, answer_type_of

    p = ITEMS_DIR / f"{rung}.json"
    if p.is_file():
        cap = json.loads(p.read_text())
        cap["answer_type"] = answer_type_of(rung)
        return cap, p
    b = EXP3B.parent / "exp2b" / "battery" / "items" / f"{rung}.json"
    return json.loads(b.read_text()), b     # 2b files carry answer_type inline


def run_cell(rung: str, size: str, mode: str, out_root=EXP3B) -> dict:
    out = record_path(out_root, rung, size, mode)
    if out.exists():
        return json.loads(out.read_text())

    _assert_module_provenance()
    # render_prompt comes from 2c's harness, not battery.base: exp2b defines it
    # in battery/base.py and exp2c in harness.py, the two bodies differ, and
    # the committed eval numbers this experiment's gates check against were
    # produced by 2c's.
    from harness import MAX_NEW_TOKENS, HFRunner, render_prompt, verify
    from models import PYTHIA_SHAS, load_pythia

    cap, items_path = load_capability(rung)
    items = cap["eval_items"]
    shots = [tuple(s) for s in cap["shots"]][:2]
    prompts = [render_prompt(it["question"], shots) for it in items]

    tok, model = load_pythia(size, untrained=(mode == "untrained"),
                             seed=UNTRAINED_SEED)
    runner = HFRunner(tok, model)
    conts = runner.generate(prompts, MAX_NEW_TOKENS[cap["answer_type"]])

    full = sum(verify(c, it["answer"], cap["answer_type"])
               for c, it in zip(conts, items))
    rec = {
        "rung": rung, "size": size, "mode": mode,
        "n_items": len(items),
        "continuations": conts,
        "probe_labels": [str(it["probe_label"]) for it in items],
        "answers": [str(it["answer"]) for it in items],
        "full_string_correct": int(full),
        "full_string_acc": full / len(items),
        "max_new_tokens": MAX_NEW_TOKENS[cap["answer_type"]],
        "n_shots": len(shots),
        "untrained_seed": UNTRAINED_SEED if mode == "untrained" else None,
        "model_sha": PYTHIA_SHAS[size],
        "items_sha256": hashlib.sha256(items_path.read_bytes()).hexdigest(),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    return rec


if __name__ == "__main__":
    rung, size, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    r = run_cell(rung, size, mode)
    print(f"[3b] {rung}/{size}/{mode} n={r['n_items']} "
          f"full_string={r['full_string_acc']:.4f}")
