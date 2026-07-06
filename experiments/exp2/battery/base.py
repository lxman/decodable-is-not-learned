"""Battery schema, prompt rendering, verification, and the generation driver.

Design doc §2–§3 (experiment-2-design.md): each capability is a spec with
  - a question generator (seeded, deterministic),
  - an ORACLE that recomputes the answer from the question TEXT alone — independent
    of generator internals, so a generator bug cannot certify itself (the
    known-answer gate: oracle must score 100% on every committed item),
  - a probe label per item (the capability's intermediate quantity),
  - a closed-form verifier (normalized exact match; no LLM judging).

Prompts are fully materialized into the committed item files: the file, not the
code, is the operationalization.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ITEMS_DIR = Path(__file__).parent / "items"

N_EVAL = 500      # design §3: reliability bar sits >4 sigma from chance at this n
N_PROBE = 2000    # design §3: probe items, disjoint from eval items


@dataclass
class CapabilitySpec:
    name: str
    description: str
    answer_type: str                      # "number" | "word" | "letters" | "choice"
    probe_label_space: str                # human note: what the probe target is
    shots: list[tuple[str, str]]          # exactly 2 fixed few-shot (q, a) pairs
    gen: Callable                         # (rng) -> (question, answer, probe_label)
    oracle: Callable                      # (question_text) -> answer  (text-only!)
    scored: bool = True                   # False for positive controls
    # positive controls have tiny question spaces; duplicates are allowed there
    # (they are gates, not scored data — noted in the design doc)
    allow_dupes: bool = False


def render_prompt(question: str, shots: list[tuple[str, str]] | None) -> str:
    parts = []
    for q, a in shots or []:
        parts.append(f"Q: {q}\nA: {a}")
    parts.append(f"Q: {question}\nA:")
    return "\n\n".join(parts)


def normalize_answer(text: str, answer_type: str) -> str:
    """First-line, lowercased, punctuation-stripped normalization for verification."""
    s = text.strip().split("\n")[0].strip().lower()
    s = s.strip(".!?\"' ")
    if answer_type == "number":
        m = re.search(r"-?\d[\d,]*", s)
        return m.group(0).replace(",", "") if m else s
    # word/letters/choice: first whitespace-delimited token
    return s.split()[0] if s else s


def verify(pred_text: str, answer: str, answer_type: str) -> bool:
    return normalize_answer(pred_text, answer_type) == normalize_answer(answer, answer_type)


def generate_items(spec: CapabilitySpec, seed: int) -> dict:
    """Generate N_EVAL + N_PROBE unique items; oracle-check every one; split
    eval-first (word-pool tasks enforce pool-level disjointness inside gen)."""
    import numpy as np

    rng = np.random.default_rng(seed)
    # shot questions are excluded from item pools: an item duplicating a shot would
    # hand the model the answer inside its own prompt
    seen, items = {q for q, _ in spec.shots}, []
    attempts = 0
    while len(items) < N_EVAL + N_PROBE:
        attempts += 1
        if attempts > 60 * (N_EVAL + N_PROBE):
            raise RuntimeError(f"{spec.name}: cannot reach item count (space too small?)")
        q, a, lbl = spec.gen(rng, split="eval" if len(items) < N_EVAL else "probe")
        if q in seen and not spec.allow_dupes:
            continue
        if spec.allow_dupes and any(q == sq for sq, _ in spec.shots):
            continue  # a shot question inside the items would carry its own answer
        ora = spec.oracle(q)
        if normalize_answer(ora, spec.answer_type) != normalize_answer(a, spec.answer_type):
            raise AssertionError(
                f"{spec.name}: oracle disagrees with generator on {q!r}: {ora!r} vs {a!r}")
        seen.add(q)
        items.append({"question": q, "answer": a, "probe_label": str(lbl)})
    return {
        "name": spec.name,
        "description": spec.description,
        "answer_type": spec.answer_type,
        "probe_label_space": spec.probe_label_space,
        "scored": spec.scored,
        "seed": seed,
        "shots": [list(s) for s in spec.shots],
        "eval_items": items[:N_EVAL],
        "probe_items": items[N_EVAL:],
    }


def save_items(payload: dict) -> Path:
    ITEMS_DIR.mkdir(exist_ok=True)
    path = ITEMS_DIR / f"{payload['name']}.json"
    path.write_text(json.dumps(payload, indent=1))
    return path


def load_items(name: str) -> dict:
    return json.loads((ITEMS_DIR / f"{name}.json").read_text())
