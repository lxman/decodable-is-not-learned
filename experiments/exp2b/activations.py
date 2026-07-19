"""Residual-stream activation collection for the Exp 2 probe side (design §3).

Positions per item (the Bonferroni family's token axis, design §3: "the last
prompt token and the capability's designated intermediate-quantity position"):

  slot 0 — QUESTION END: the last token of the question text itself, before the
           "\\nA:" answer cue. The model has just finished reading the problem;
           the intermediate quantity, if represented, is computed by here.
  slot 1 — PROMPT END: the final prompt token (the ":" of "A:"), where the model
           must hold whatever it is about to say.

Token indices are computed per item by tokenizing the prompt prefix that ends at
the question's last character (BPE-boundary effects at the "\\n" are clean for
GPTNeoX; verified by test against the real tokenizer). Forward passes are batched
right-padded — padding side is irrelevant without generation because indices are
taken from per-item true lengths.

Storage: one .npz per (size, mode, capability) under results/activations/ —
X: float16 [n_items, n_layers, 2, d_model] (hidden_states including embeddings),
y: probe labels (strings), plus provenance. fp16 storage: probes standardize
features anyway; the precision loss is far below feature scale.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from battery.base import render_prompt

EXP_DIR = Path(__file__).resolve().parent
ANSWER_CUE = "\nA:"


def activations_path(size: str, mode: str, cap_name: str) -> Path:
    return EXP_DIR / "results" / "activations" / f"{size}_{mode}" / f"{cap_name}.npz"


def question_end_char(prompt: str) -> int:
    """Character index one past the question's last character (start of ANSWER_CUE
    of the FINAL question block)."""
    idx = prompt.rfind(ANSWER_CUE)
    if idx <= 0:
        raise ValueError("prompt does not end with the answer cue")
    return idx


def position_indices(tok, prompt: str) -> tuple[int, int]:
    """(question_end_index, prompt_end_index) as token indices into the un-padded
    tokenization of `prompt`."""
    full = tok(prompt, add_special_tokens=False)["input_ids"]
    prefix = tok(prompt[: question_end_char(prompt)], add_special_tokens=False)["input_ids"]
    return len(prefix) - 1, len(full) - 1


def collect_capability(model, tok, cap: dict, *, which_items: str = "probe_items",
                       batch_size: int = 32, device: str = "mps") -> dict:
    """Collect residual activations for every item; returns arrays (not yet saved)."""
    import torch

    items = cap[which_items]
    shots = [tuple(s) for s in cap["shots"]]
    prompts = [render_prompt(it["question"], shots) for it in items]
    labels = [it["probe_label"] for it in items]

    old_side = tok.padding_side
    tok.padding_side = "right"  # forwards only; index by true length
    X_chunks = []
    try:
        for i in range(0, len(prompts), batch_size):
            chunk = prompts[i:i + batch_size]
            enc = tok(chunk, return_tensors="pt", padding=True,
                      add_special_tokens=False).to(device)
            with torch.no_grad():
                out = model(**enc, output_hidden_states=True)
            # [n_layers, B, T, d]
            hs = torch.stack(out.hidden_states, dim=0)
            for b, prompt in enumerate(chunk):
                q_idx, p_idx = position_indices(tok, prompt)
                sel = hs[:, b, [q_idx, p_idx], :]          # [n_layers, 2, d]
                X_chunks.append(sel.to(torch.float16).cpu().numpy())
    finally:
        tok.padding_side = old_side

    return {"X": np.stack(X_chunks), "y": np.array(labels, dtype=object)}


def save_activations(path: Path, arrays: dict, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, X=arrays["X"], y=arrays["y"].astype(str),
                        meta=json.dumps(meta))


def load_activation_map(path: Path) -> tuple[dict, np.ndarray, dict]:
    """Load an .npz into the frozen probe module's expected shape:
    {(layer, token_slot): float32 [n, d]}, labels, meta."""
    z = np.load(path, allow_pickle=False)
    X, y = z["X"], z["y"]
    meta = json.loads(str(z["meta"]))
    act = {(layer, slot): X[:, layer, slot, :].astype(np.float32)
           for layer in range(X.shape[1]) for slot in range(X.shape[2])}
    return act, y, meta
