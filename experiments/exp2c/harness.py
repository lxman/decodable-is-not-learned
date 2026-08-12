"""Argmax evaluation harness for 2c (design §3 eval side; used by M1
inclusion now, M2 positive controls and M4 scale ascent later).

Ported from exp2b/harness.py (the proven M1/M2/M4 machinery) with 2b's
prompt/normalize/verify semantics carried VERBATIM -- identical
rendering and scoring is what makes the reused survivors' 2b record
comparable (design §7). Differences from 2b, all mechanical:

- render_prompt / normalize_answer / verify live here (2c's
  battery/base.py is probe-side only and stays untouched);
- answer_type comes from the SPECS registry, not the item file (2c's
  committed item files don't carry it);
- load_items reads 2c's battery/items tree.

Like 2b's, this file is mechanics, not dials: every threshold it is
measured against lives in the design doc and analyze.py.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parent
ITEMS_DIR = EXP_DIR / "battery" / "items"

# Generation caps per answer type (2b verbatim): enough tokens for the
# longest gold answer plus a newline; normalize takes the first line /
# first token, so overshoot is harmless and undershoot is the only risk.
MAX_NEW_TOKENS = {"number": 8, "word": 12, "letters": 12, "choice": 6}

N_SHOTS_PRIMARY = 2  # design §2: 2-shot is the primary variant


def clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Exact binomial CI. Every zero-looking rate ships as a CP bound (design §4)."""
    from scipy.stats import beta

    alpha = 1.0 - level
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


# ------------------------------------------------- 2b scoring, verbatim

def render_prompt(question: str, shots: list | None) -> str:
    parts = []
    for q, a in shots or []:
        parts.append(f"Q: {q}\nA: {a}")
    parts.append(f"Q: {question}\nA:")
    return "\n\n".join(parts)


def normalize_answer(text: str, answer_type: str) -> str:
    """First-line, lowercased, punctuation-stripped normalization (Exp 2
    verbatim, via 2b)."""
    s = text.strip().split("\n")[0].strip().lower()
    s = s.strip(".!?\"' ")
    if answer_type == "number":
        m = re.search(r"-?\d[\d,]*", s)
        return m.group(0).replace(",", "") if m else s
    return s.split()[0] if s else s


def verify(pred_text: str, answer: str, answer_type: str) -> bool:
    return normalize_answer(pred_text, answer_type) == normalize_answer(
        answer, answer_type)


# ----------------------------------------------------- items + registry

def answer_type_of(name: str) -> str:
    """2c item files carry no answer_type; the registry does.

    The relative branch is load-bearing, not cosmetic: once `instrument`
    has prepended exp2b to sys.path, a BARE `from battery import ...`
    resolves to exp2b's battery package, which has no generators_*. That
    only bites when this module is reached by its package path (pytest,
    or any absolute import) rather than by `-m` from exp2c/, where 2c's
    `battery` is already in sys.modules under the bare name."""
    try:  # experiments.exp2c.harness (pytest / absolute import)
        from .battery import generators_controls, generators_rescues, \
            generators_rungs  # noqa: F401  (populate SPECS)
        from .battery.base import SPECS
    except ImportError:  # pragma: no cover - bare `-m` from exp2c/
        from battery import generators_controls, generators_rescues, \
            generators_rungs  # noqa: F401
        from battery.base import SPECS
    return SPECS[name].answer_type


def load_items(name: str) -> dict:
    cap = json.loads((ITEMS_DIR / f"{name}.json").read_text())
    cap["answer_type"] = answer_type_of(name)
    return cap


# ------------------------------------------------------------- running

class HFRunner:
    """Batched greedy continuation for a (tokenizer, model) pair (2b
    verbatim)."""

    def __init__(self, tok, model, batch_size: int = 16):
        self.tok, self.model, self.batch_size = tok, model, batch_size

    def generate(self, prompts: list[str], max_new_tokens: int) -> list[str]:
        import torch

        outs = []
        for i in range(0, len(prompts), self.batch_size):
            chunk = prompts[i:i + self.batch_size]
            enc = self.tok(chunk, return_tensors="pt",
                           padding=True).to(self.model.device)
            with torch.no_grad():
                gen = self.model.generate(
                    **enc, max_new_tokens=max_new_tokens, do_sample=False,
                    pad_token_id=self.tok.pad_token_id)
            cont = gen[:, enc["input_ids"].shape[1]:]
            outs.extend(self.tok.batch_decode(cont, skip_special_tokens=True))
        return outs


def evaluate_argmax(runner, cap: dict, n_shots: int = N_SHOTS_PRIMARY) -> dict:
    """Greedy accuracy of `runner` on a capability's committed eval items."""
    shots = [tuple(s) for s in cap["shots"]][:n_shots]
    items = cap["eval_items"]
    prompts = [render_prompt(it["question"], shots) for it in items]
    preds = runner.generate(prompts, MAX_NEW_TOKENS[cap["answer_type"]])
    assert len(preds) == len(items)
    correct = sum(
        verify(p, it["answer"], cap["answer_type"])
        for p, it in zip(preds, items))
    lo, hi = clopper_pearson(correct, len(items))
    return {"capability": cap["name"], "n": len(items),
            "correct": int(correct), "acc": correct / len(items),
            "cp95": [lo, hi], "n_shots": n_shots}


def result_path(kind: str, size: str, mode: str, cap_name: str) -> Path:
    """results/<kind>/<size>_<mode>/<cap>.json — the durable, resumable
    unit."""
    return EXP_DIR / "results" / kind / f"{size}_{mode}" / f"{cap_name}.json"


def evaluate_to_file(runner_factory, cap: dict, path: Path, meta: dict) -> dict:
    """Skip-if-result-exists evaluation (process rule 7). `runner_factory`
    is called only on a miss, so resumed campaigns never load a model
    needlessly."""
    if path.exists():
        return json.loads(path.read_text())
    result = evaluate_argmax(runner_factory(), cap)
    result.update(meta)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=1))
    return result
