"""Battery schema, prompt rendering, verification, and the generation driver.

Extends Exp 2's base (whose prompt/answer conventions carry over verbatim) with
the design's five declared fields per capability (experiment-2b-design.md §2):
probe target, surface BASIS (a text-parsed component tuple), starving-split
parameters, composability argument, and feasibility counts. The basis extractor
parses the question TEXT only — same independence discipline as the oracle, so
a generator bug cannot certify its own basis values.

The committed item file is the operationalization: prompts, answers, probe
labels, AND basis tuples are all materialized; the feasibility report for all
5 probe seeds is committed alongside.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# Everything in exp2b runs from the exp2b root (the Exp 2 convention:
# `cd experiments/exp2b && python -m ...`), so top-level modules resolve without
# sys.path games — the shadowing lesson from exp2's campaign abort (018cde3).
from splits import SplitParams, feasibility_report

ITEMS_DIR = Path(__file__).parent / "items"

N_EVAL = 500       # carried from Exp 2: reliability bar > 4 sigma from chance
N_PROBE = 2000     # default; specs with multi-component bases may raise it


@dataclass
class CapabilitySpec:
    name: str
    description: str
    answer_type: str                      # "number" | "word" | "letters" | "choice"
    probe_label_space: str                # design field 1: the probe target
    basis_kind: str                       # design field 2: what the basis IS
    composability: str                    # design field 4: why not sub-basis composable
    shots: list[tuple[str, str]]          # exactly 2 fixed few-shot (q, a) pairs
    gen: Callable                         # (rng, split) -> (question, answer, probe_label)
    oracle: Callable                      # (question_text) -> answer  (text-only!)
    basis_fn: Callable = None             # (question_text) -> tuple of component values
    split_params: SplitParams = field(default_factory=SplitParams)
    n_probe: int = N_PROBE                # raised for multi-component bases
    scored: bool = True                   # False for the positive control
    allow_dupes: bool = False             # controls only (gates, not scored data)


def render_prompt(question: str, shots: list[tuple[str, str]] | None) -> str:
    parts = []
    for q, a in shots or []:
        parts.append(f"Q: {q}\nA: {a}")
    parts.append(f"Q: {question}\nA:")
    return "\n\n".join(parts)


def normalize_answer(text: str, answer_type: str) -> str:
    """First-line, lowercased, punctuation-stripped normalization (Exp 2 verbatim)."""
    s = text.strip().split("\n")[0].strip().lower()
    s = s.strip(".!?\"' ")
    if answer_type == "number":
        m = re.search(r"-?\d[\d,]*", s)
        return m.group(0).replace(",", "") if m else s
    return s.split()[0] if s else s


def verify(pred_text: str, answer: str, answer_type: str) -> bool:
    return normalize_answer(pred_text, answer_type) == normalize_answer(answer, answer_type)


def generate_items(spec: CapabilitySpec, seed: int) -> dict:
    """Generate N_EVAL + spec.n_probe unique items; oracle-check AND basis-parse
    every one; run the 5-seed feasibility report on the probe split (design §2
    field 5) — a capability that cannot satisfy it raises SplitInfeasible and is
    ejected at M0, reported, never silently patched."""
    import numpy as np

    rng = np.random.default_rng(seed)
    seen, items = {q for q, _ in spec.shots}, []
    n_total = N_EVAL + spec.n_probe
    attempts = 0
    while len(items) < n_total:
        attempts += 1
        if attempts > 60 * n_total:
            raise RuntimeError(f"{spec.name}: cannot reach item count (space too small?)")
        q, a, lbl = spec.gen(rng, split="eval" if len(items) < N_EVAL else "probe")
        if q in seen and not spec.allow_dupes:
            continue
        if spec.allow_dupes and any(q == sq for sq, _ in spec.shots):
            continue
        ora = spec.oracle(q)
        if normalize_answer(ora, spec.answer_type) != normalize_answer(a, spec.answer_type):
            raise AssertionError(
                f"{spec.name}: oracle disagrees with generator on {q!r}: {ora!r} vs {a!r}")
        basis = tuple(str(v) for v in spec.basis_fn(q)) if spec.basis_fn else None
        seen.add(q)
        items.append({"question": q, "answer": a, "probe_label": str(lbl),
                      **({"basis": list(basis)} if basis else {})})

    payload = {
        "name": spec.name,
        "description": spec.description,
        "answer_type": spec.answer_type,
        "probe_label_space": spec.probe_label_space,
        "basis_kind": spec.basis_kind,
        "composability": spec.composability,
        "scored": spec.scored,
        "seed": seed,
        "shots": [list(s) for s in spec.shots],
        "eval_items": items[:N_EVAL],
        "probe_items": items[N_EVAL:],
    }
    if spec.scored:
        probe = payload["probe_items"]
        payload["feasibility"] = feasibility_report(
            [tuple(it["basis"]) for it in probe],
            [it["probe_label"] for it in probe],
            spec.split_params)
    return payload


def save_items(payload: dict) -> Path:
    ITEMS_DIR.mkdir(exist_ok=True)
    path = ITEMS_DIR / f"{payload['name']}.json"
    path.write_text(json.dumps(payload, indent=1))
    return path


def load_items(name: str) -> dict:
    return json.loads((ITEMS_DIR / f"{name}.json").read_text())
