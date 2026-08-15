"""Exp 3a runner: one (rung, size, mode) cell.

Queries the model on 2c's own committed prompt — `render_prompt(question,
shots)` with the committed 2 shots, greedy decoding, 2c's MAX_NEW_TOKENS —
and stores the RAW CONTINUATION for every item.

STORING THE CONTINUATIONS IS THE POINT. 2c stored one aggregate per cell
(n, correct, acc). That is the entire reason this experiment needs new
inference at all: the first-character question could not be asked of the
existing records, because the generations were thrown away. This runner does
not repeat that. Everything downstream — first-character accuracy, the
full-string replication check, "did the token cap truncate before anything
was emitted" — is recomputable from what is written here without querying a
model again.

Nothing under experiments/exp2b/ or experiments/exp2c/ is modified.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXP3A = Path(__file__).resolve().parents[1]

# ORDER MATTERS AND IS NOT COSMETIC. Both trees carry a `harness`, a `battery`
# package and a `run` package. sys.path.insert(0) puts the LAST inserted
# FIRST, so exp2b goes in first and exp2c ends up ahead of it. exp2c must win:
# only its harness defines ITEMS_DIR, answer_type_of, verify and the
# render_prompt that produced 2c's committed eval numbers, and reproducing
# those numbers is this experiment's replication gate. exp2b supplies
# `models`, which exp2c does not define.
#
# Corrected post-freeze, disclosed in PROGRESS.md: the original order was
# reversed, and every cell of the first campaign launch died on
# `ImportError: cannot import name 'ITEMS_DIR' from 'harness'`. That crash was
# lucky. Had exp2b's harness happened to define ITEMS_DIR, all 24 cells would
# have run to completion through the WRONG TREE — a different MAX_NEW_TOKENS
# and a different verify — and produced plausible wrong numbers. The assertion
# below exists so this can never again depend on luck.
for _p in (EXP3A.parent / "exp2b", EXP3A.parent / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def _assert_module_provenance() -> None:
    """Refuse to run unless each module resolved to the tree it must."""
    import harness
    import models

    want = {"harness": EXP3A.parent / "exp2c",
            "models": EXP3A.parent / "exp2b"}
    for name, root in want.items():
        got = Path(sys.modules[name].__file__).resolve()
        if root.resolve() not in got.parents:
            raise ImportError(
                f"{name!r} resolved to {got}, which is not under {root} — "
                f"this cell would be measured with the wrong tree's code")

SIZES = ("2.8b", "6.9b", "12b")
MODES = ("trained", "untrained")
UNTRAINED_SEED = 0            # 2c's own, campaign_m4.UNTRAINED_SEED
RUNGS = ("rev_string7", "reverse_string", "ctrl_copy", "clock24_d999")


def record_path(out_root, rung: str, size: str, mode: str) -> Path:
    return Path(out_root) / "results" / f"{size}_{mode}" / f"{rung}.json"


def load_capability(rung: str) -> dict:
    """2c rungs take answer_type from SPECS; the 2b survivor carries it
    inline. This mirrors campaign_m4.load_capability rather than reimplementing
    the choice."""
    from harness import ITEMS_DIR, answer_type_of

    p = ITEMS_DIR / f"{rung}.json"
    if p.is_file():
        cap = json.loads(p.read_text())
        cap["answer_type"] = answer_type_of(rung)
        return cap
    b = EXP3A.parent / "exp2b" / "battery" / "items" / f"{rung}.json"
    return json.loads(b.read_text())     # 2b files carry answer_type inline


def committed_2c_acc(rung: str, size: str, mode: str) -> float | None:
    p = (EXP3A.parent / "exp2c" / "results" / "m4" / f"{size}_{mode}"
         / f"{rung}.json")
    return json.loads(p.read_text())["acc"] if p.is_file() else None


def run_cell(rung: str, size: str, mode: str, out_root=EXP3A) -> dict:
    out = record_path(out_root, rung, size, mode)
    if out.exists():
        return json.loads(out.read_text())

    _assert_module_provenance()
    # render_prompt comes from 2c's harness, not battery.base: exp2b defines it
    # in battery/base.py and exp2c in harness.py, the two bodies differ, and
    # 2c's committed eval numbers — the ones the replication gate checks
    # against — were produced by 2c's.
    from harness import MAX_NEW_TOKENS, HFRunner, render_prompt, verify
    from models import load_pythia

    cap = load_capability(rung)
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
        "full_string_acc": full / len(items),
        "committed_2c_acc": committed_2c_acc(rung, size, mode),
        "max_new_tokens": MAX_NEW_TOKENS[cap["answer_type"]],
        "n_shots": len(shots),
        "untrained_seed": UNTRAINED_SEED if mode == "untrained" else None,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    return rec


if __name__ == "__main__":
    rung, size, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    r = run_cell(rung, size, mode)
    print(f"[3a] {rung}/{size}/{mode} n={r['n_items']} "
          f"full_string={r['full_string_acc']:.4f} "
          f"(2c committed {r['committed_2c_acc']})")
