"""The teacher-forced canonical-path scoring arm (design §5.5) —
committed BEFORE any new sampling in the frozen §10 order: gate 1 →
scoring pass → tranche. One forward chain per (item, size) scores the
canonical path: the rendered prompt (2c's renderer, §4 pins)
concatenated with " " + answer, tokenized as one string; ℓ_i is the
sum of log-probs of the span tokens under THE SAMPLER'S OWN LAW —
each step's probability is exp3's step_probs (CPU float32 softmax of
that position's logits), so exp(ℓ_i) is exactly the probability that
the frozen T = 1.0 sampler emits the canonical token path. The chain
is computed stepwise with logits_to_keep=1 + KV cache — the sampler's
own safe path; the fp16-MPS full-logits multi-token forward is broken
on this stack (masses.py carries the note) and is never used.

THE SPAN RULE (frozen; validated against committed text in
span_validation_3d.py): tokenize(prompt) must be an exact prefix of
tokenize(prompt + " " + answer); the span is the tail; decode(span)
must round-trip to exactly " " + answer. Violations are hard errors
counted in the record (span_round_trip_failures MUST be 0 — the
analyzer refuses anything else).

THE KNOWN-ANSWER GATE (frozen band, analyze_3d): ctrl_copy's
predicted canonical-path rate p̂ = mean_i exp(ℓ_i) must land within
[LOWER_FACTOR × r, r + UPPER_MARGIN] of the cell's committed T = 1.0
SAMPLED verified rate r (§4 pin; NOT the greedy .9940). A scoring arm
that cannot predict the control's near-certain emission is broken and
the campaign does not launch (§5.5).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

EXP3D = Path(__file__).resolve().parent
EXPERIMENTS = EXP3D.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))
for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from experiments.exp3.sampler import step_probs  # noqa: E402
from experiments.exp3d.analyze_3d import (  # noqa: E402
    CTRL_GATE_LOWER_FACTOR, CTRL_GATE_UPPER_MARGIN,
    CTRL_SAMPLED_RATE_PIN, ITEMS_SHA_PIN, N_ITEMS, SCORING_RUNGS,
    SIZES_3D, check_frozen_imports_3d,
)


# ------------------------------------------------- the frozen span rule

class SpanError(ValueError):
    """A prompt whose canonical continuation has no well-defined token
    span — never skipped, always fatal at scoring time."""


def answer_span(tok, prompt: str, answer: str) -> list:
    """The canonical path's token ids past the prompt, under the frozen
    rule. `tok` needs only __call__(text)['input_ids'] and
    decode(ids) — the fixture suite drives it with a synthetic
    tokenizer; the scoring pass drives it with the real one."""
    if not answer:
        raise SpanError("empty answer has no canonical span")
    enc_p = list(tok(prompt)["input_ids"])
    full = prompt + " " + answer
    enc_f = list(tok(full)["input_ids"])
    if enc_f[: len(enc_p)] != enc_p:
        raise SpanError(
            f"tokenization of prompt+answer does not extend the "
            f"prompt's own tokens (prefix violation at "
            f"{prompt[-16:]!r} + {' ' + answer!r}) — the canonical "
            f"span is ill-defined for this item")
    span = enc_f[len(enc_p):]
    if not span:
        raise SpanError(f"empty span for answer {answer!r}")
    got = tok.decode(span)
    if got != " " + answer:
        raise SpanError(
            f"span decode round-trip failed: {got!r} != "
            f"{' ' + answer!r} — the span does not denote the "
            f"canonical continuation")
    return [int(t) for t in span]


# ----------------------------------------------------- the scoring loop

def score_items(model, tok, prompts, answers) -> dict:
    """ℓ for every item: stepwise teacher-forced log-probs of the
    canonical span under the sampler's probability law. Returns ell
    (None where any step's fp32 probability is exactly 0), the span
    table, and per-token log-probs for the record."""
    import torch

    ell = []
    spans = []
    per_token = []
    zero_items = 0
    for i, (prompt, answer) in enumerate(zip(prompts, answers)):
        span = answer_span(tok, prompt, answer)
        spans.append(span)
        enc = tok(prompt, return_tensors="pt").to(model.device)
        prompt_len = enc["input_ids"].shape[1]
        with torch.no_grad():
            out = model(**enc, use_cache=True, logits_to_keep=1)
        past = out.past_key_values
        probs = step_probs(out.logits[0, -1])
        logs = []
        dead = False
        for t, token_id in enumerate(span):
            p = float(probs[token_id])
            if p <= 0.0:
                dead = True
                logs.append(None)
                # remaining tokens are unreachable through this path;
                # record and stop the chain
                break
            logs.append(math.log(p))
            if t + 1 < len(span):
                step_ids = torch.tensor([[token_id]],
                                        device=model.device)
                attn = torch.ones((1, prompt_len + t + 1),
                                  device=model.device, dtype=torch.long)
                with torch.no_grad():
                    out = model(input_ids=step_ids,
                                past_key_values=past,
                                attention_mask=attn)
                probs = step_probs(out.logits[0, -1])
        per_token.append(logs)
        if dead:
            ell.append(None)
            zero_items += 1
        else:
            ell.append(float(sum(logs)))
        if (i + 1) % 100 == 0:
            print(f"[3d scoring] {i + 1}/{len(prompts)} items scored",
                  flush=True)
    return {"ell": ell, "span_token_ids": spans,
            "per_token_logprobs": per_token,
            "zero_probability_items": zero_items,
            "span_round_trip_failures": 0}


# -------------------------------------------------- the known-answer gate

def in_band(p_hat: float, lo: float, hi: float) -> bool:
    """The frozen boundary convention: INCLUSIVE at both edges — a
    predicted rate exactly on the band boundary passes. Pinned by a
    direct edge fixture; the mutation battery carries the exclusive
    misread."""
    return lo <= p_hat <= hi


def ctrl_gate(ell, size: str) -> dict:
    """The §5.5 known-answer gate: p̂ = mean_i exp(ℓ_i) against the
    committed T = 1.0 sampled rate's frozen band."""
    pin = CTRL_SAMPLED_RATE_PIN[size]
    r = pin["count"] / pin["n_draws"]
    p_hat = sum(math.exp(v) for v in ell if v is not None) / len(ell)
    lo = CTRL_GATE_LOWER_FACTOR * r
    hi = r + CTRL_GATE_UPPER_MARGIN
    return {"predicted_rate": p_hat,
            "committed_count": pin["count"],
            "committed_n_draws": pin["n_draws"],
            "committed_rate": r,
            "band": [lo, hi],
            "lower_factor": CTRL_GATE_LOWER_FACTOR,
            "upper_margin": CTRL_GATE_UPPER_MARGIN,
            "passed": in_band(p_hat, lo, hi)}


# --------------------------------------------------------- cell runner

def record_path(out_root, rung: str, size: str) -> Path:
    return (Path(out_root) / "results" / "scoring" / f"{size}_trained"
            / f"{rung}.json")


def run_scoring_cell(rung, size, out_root=EXP3D, model_ctx=None) -> dict:
    """One (rung, size) scoring record: spans, per-token log-probs, ℓ,
    and (ctrl_copy only) the known-answer gate. Skip-if-exists; a
    FAILED gate still writes its record — the campaign driver and the
    analyzer both refuse to proceed past it, and the failure is the
    disclosure."""
    out = record_path(out_root, rung, size)
    if out.exists():
        return json.loads(out.read_text())
    check_frozen_imports_3d()

    from experiments.exp3.run.run_cell import (  # noqa: PLC0415
        _assert_module_provenance, _load_model, load_capability,
    )
    from harness import render_prompt  # noqa: PLC0415 — 2c's, asserted

    _assert_module_provenance()
    if rung not in SCORING_RUNGS or size not in SIZES_3D:
        raise ValueError(f"{rung}/{size} is not a 3d scoring cell")
    import hashlib  # noqa: PLC0415
    cap, items_path = load_capability(rung)
    items_sha = hashlib.sha256(items_path.read_bytes()).hexdigest()
    if items_sha != ITEMS_SHA_PIN[rung]:
        raise ValueError(
            f"item file {items_path} has sha256 {items_sha} against "
            f"the §4 pin {ITEMS_SHA_PIN[rung]} — these are not the "
            f"committed items")
    shots = [tuple(s) for s in cap["shots"]][:2]
    prompts = [render_prompt(it["question"], shots)
               for it in cap["eval_items"]]
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    if len(answers) != N_ITEMS:
        raise ValueError(f"{rung}: {len(answers)} items, not {N_ITEMS}")

    import torch          # noqa: PLC0415
    import transformers   # noqa: PLC0415

    tok, model, model_sha = model_ctx if model_ctx else \
        _load_model(size, "trained", "float32")
    scored = score_items(model, tok, prompts, answers)
    rec = {"rung": rung, "size": size, "mode": "trained",
           "n_items": N_ITEMS,
           "items_sha256": items_sha,
           "answers": answers,
           "dtype": "float32",
           "model_sha": model_sha,
           "stack": {"torch": torch.__version__,
                     "transformers": transformers.__version__},
           **scored}
    if rung == "ctrl_copy":
        rec["known_answer_gate"] = ctrl_gate(scored["ell"], size)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    msg = ""
    if rung == "ctrl_copy":
        g = rec["known_answer_gate"]
        msg = (f" | gate {'PASS' if g['passed'] else 'FAIL'} "
               f"(p̂ {g['predicted_rate']:.4f} vs committed "
               f"{g['committed_rate']:.4f}, band "
               f"[{g['band'][0]:.4f}, {g['band'][1]:.4f}])")
    print(f"[3d scoring] {rung}/{size} done — "
          f"{scored['zero_probability_items']} zero-probability "
          f"item(s){msg}", flush=True)
    return rec
