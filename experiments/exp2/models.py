"""Pythia loaders for Exp 2, pinned to the ledgered `main`-revision SHAs.

Design doc §2: standard (non-deduped) branch, final checkpoints, fp16 on MPS.
The SHAs below were resolved and recorded in PROGRESS.md on 2026-07-07 (40eca80);
run code loads by SHA so an upstream branch move cannot swap weights silently.

`untrained=True` returns the same architecture with seeded random init and NO
pretrained weights — the empirical-chance control model (design §3: never assume
the theoretical floor) and the M2 untrained-weights probe control.
"""

from __future__ import annotations

import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

PYTHIA_SHAS = {
    "410m": "9879c9b5f8bea9051dcb0e68dff21493d67e9d4f",
    "1b": "f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2",
    "2.8b": "2a259cdd96a4beb1cdf467512e3904197345f6a9",
    "6.9b": "c0e3eee36dc47af0c49f361c74cfe459c09f7f23",
    "12b": "bb1e3e710cdf6b524461d543cfb5ba773f0a81b6",
}

PROBE_SIZES = ("410m", "1b")          # design §2: probe side, below threshold
EVAL_SIZES = ("2.8b", "6.9b", "12b")  # design §2: eval side, scale ascent


def load_tokenizer(size: str):
    repo = f"EleutherAI/pythia-{size}"
    tok = AutoTokenizer.from_pretrained(repo, revision=PYTHIA_SHAS[size])
    # GPTNeoX has no pad token; generation batches are left-padded so the
    # continuation always starts immediately after the prompt's last token.
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def load_pythia(size: str, untrained: bool = False, seed: int = 0,
                device: str = "mps"):
    """Returns (tokenizer, model) in eval mode, fp16, on `device`."""
    repo = f"EleutherAI/pythia-{size}"
    tok = load_tokenizer(size)
    if untrained:
        cfg = AutoConfig.from_pretrained(repo, revision=PYTHIA_SHAS[size])
        torch.manual_seed(seed)
        model = AutoModelForCausalLM.from_config(cfg).to(dtype=torch.float16)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            repo, revision=PYTHIA_SHAS[size], dtype=torch.float16)
    return tok, model.to(device).eval()
