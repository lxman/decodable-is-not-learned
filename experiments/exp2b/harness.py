"""Argmax evaluation harness (design doc §3, eval side; used by M1 inclusion,
M2 positive controls, and M4 scale ascent).

Built AFTER the preregistration freeze — deliberately so: this file is mechanics
(prompting, greedy decoding, counting), not dials. It computes accuracies and
Clopper–Pearson bounds; every threshold it is measured against lives in the
frozen design doc and analyze.py. Operational choices made here (max-new-token
caps, batch size, per-size untrained floors) are recorded in PROGRESS.md.

The model is behind a one-method Runner interface so tests exercise the whole
loop with fakes; HFRunner is the thin transformers implementation.
"""

from __future__ import annotations

import json
from pathlib import Path

from battery.base import render_prompt, verify

EXP_DIR = Path(__file__).resolve().parent

# Generation caps per answer type: enough tokens for the longest gold answer in
# the committed item files plus a newline; normalize_answer() takes the first
# line / first token, so overshoot is harmless and undershoot is the only risk.
MAX_NEW_TOKENS = {"number": 8, "word": 12, "letters": 12, "choice": 6}

N_SHOTS_PRIMARY = 2  # design §2: 2-shot is the primary variant


def clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Exact binomial CI. Every zero-looking rate ships as a CP bound (design §4)."""
    from scipy.stats import beta

    alpha = 1.0 - level
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


class HFRunner:
    """Batched greedy continuation for a (tokenizer, model) pair."""

    def __init__(self, tok, model, batch_size: int = 16):
        self.tok, self.model, self.batch_size = tok, model, batch_size

    def generate(self, prompts: list[str], max_new_tokens: int) -> list[str]:
        import torch

        outs = []
        for i in range(0, len(prompts), self.batch_size):
            chunk = prompts[i:i + self.batch_size]
            enc = self.tok(chunk, return_tensors="pt", padding=True).to(self.model.device)
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
        verify(p, it["answer"], cap["answer_type"]) for p, it in zip(preds, items))
    lo, hi = clopper_pearson(correct, len(items))
    return {"capability": cap["name"], "n": len(items), "correct": int(correct),
            "acc": correct / len(items), "cp95": [lo, hi], "n_shots": n_shots}


def normalized_margin(result: dict, chance_result: dict) -> dict:
    """m = (acc - chance) / (1 - chance), chance = the untrained control model's
    measured accuracy on the SAME items (design §3). CP bounds on the trained
    accuracy are mapped through the chance point estimate; the chance floor's own
    CP bounds are carried alongside rather than compounded."""
    c = chance_result["acc"]
    denom = max(1e-9, 1.0 - c)
    to_m = lambda a: (a - c) / denom  # noqa: E731
    return {
        "margin": to_m(result["acc"]),
        "margin_cp95": [to_m(result["cp95"][0]), to_m(result["cp95"][1])],
        "chance": c,
        "chance_cp95": chance_result["cp95"],
    }


def result_path(kind: str, size: str, mode: str, cap_name: str) -> Path:
    """results/<kind>/<size>_<mode>/<cap>.json — the durable, resumable unit."""
    return EXP_DIR / "results" / kind / f"{size}_{mode}" / f"{cap_name}.json"


def evaluate_to_file(runner_factory, cap: dict, path: Path, meta: dict) -> dict:
    """Skip-if-result-exists evaluation (process rule 7). `runner_factory` is
    called only on a miss, so resumed campaigns never load a model needlessly."""
    if path.exists():
        return json.loads(path.read_text())
    result = evaluate_argmax(runner_factory(), cap)
    result.update(meta)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=1))
    return result
