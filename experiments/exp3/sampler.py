"""Seeded ancestral sampler (design §3, §5; doc Open item 2).

T = 1.0 and NO truncation — top-p and top-k off, because truncation
deletes tail mass and tail mass is the question. Draws are taken from
committed RNG streams: one substream per (cell, seed, item), derived by
the frozen formula below (PROGRESS.md reading 4), so every unit
reproduces independently of batch composition and restart order. The
generator lives on CPU and the sampled distribution is the CPU-float32
softmax of the model's logits: given this stack's deterministic
forwards (gate 4's fixture), the draw sequence is byte-reproducible.

A draw stops at the first terminal id (eos/pad) — generate's semantics,
which produced 3b's committed continuations, and the mass module's
terminal bucket mirror. Rows are sampled every step with a fixed
consumption pattern and truncated at decode, so a finished row never
changes any other row's stream.

The campaign-stack determinism artifact (gate 4) is
run/determinism_fixture.py: synthetic pinned prompts, two separate
processes, byte-identical output required. No committed item is
sampled before the exp3-preregistered tag.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from experiments.exp3.analyze_3 import (
    DRAWS_PER_SEED, EXP3, SAMPLING_CELLS, SAMPLING_MAX_NEW_TOKENS, SEEDS,
)

STREAM_NAMESPACE = "exp3"
MAX_ROWS = 16          # §3's batch: rows per forward chunk
_SEED_MASK = (1 << 63) - 1   # torch.Generator takes a signed int64

STREAM_MAP_PATH = EXP3 / "stream_map.json"


# ------------------------------------------------------- stream map

def stream_seed(rung: str, size: str, mode: str, seed: int,
                item_idx: int) -> int:
    """First 8 bytes of sha256("exp3|rung|size|mode|s{seed}|i{item}"),
    big-endian, masked to 63 bits. Frozen: the golden literal in the
    fixture suite and the committed stream_map.json both pin it."""
    tag = f"{STREAM_NAMESPACE}|{rung}|{size}|{mode}|s{seed}|i{item_idx}"
    h = hashlib.sha256(tag.encode()).digest()
    return int.from_bytes(h[:8], "big") & _SEED_MASK


def dump_stream_map(path=STREAM_MAP_PATH) -> dict:
    """The committed (cell, seed) → stream map (§3): formula, mask, and
    the derived endpoints (item 0 and item 499) for every one of the
    16 sampling cells × 4 seeds."""
    cells = {}
    for (rung, size, mode) in SAMPLING_CELLS:
        for s in SEEDS:
            cells[f"{rung}/{size}/{mode}/s{s}"] = {
                "item0": stream_seed(rung, size, mode, s, 0),
                "item499": stream_seed(rung, size, mode, s, 499),
            }
    out = {
        "formula": "int.from_bytes(sha256('exp3|{rung}|{size}|{mode}|"
                   "s{seed}|i{item}').digest()[:8], 'big') & ((1<<63)-1)",
        "per_item_substreams": True,
        "chunk_rows": MAX_ROWS,
        "draw_order": "seeds ascending; within a seed, chunks in index "
                      "order; within a chunk, rows in row order; one "
                      "multinomial call per step over all rows",
        "cells": cells,
    }
    Path(path).write_text(json.dumps(out, indent=1))
    return out


# ------------------------------------------------------- chunk plan

def chunk_plan(draws_per_seed: int) -> tuple:
    """Row counts per forward chunk for one seed's stream. Never pads:
    a padded row would consume generator draws and shift every later
    draw in the stream."""
    full, rem = divmod(draws_per_seed, MAX_ROWS)
    return tuple([MAX_ROWS] * full + ([rem] if rem else []))


# ------------------------------------------------------- truncation

def truncate_at_terminal(tokens, terminal_ids) -> list:
    """A draw's tokens up to (excluding) the first terminal id — the
    sampled channel stops at EOS; whatever the fixed-shape batch
    mechanically sampled after it is bookkeeping, not emission."""
    term = set(terminal_ids)
    out = []
    for t in tokens:
        if int(t) in term:
            break
        out.append(int(t))
    return out


# ------------------------------------------------------- the loop

def step_probs(logits):
    """CPU float32 softmax of one position's logits. T = 1.0 exactly;
    no top-p, no top-k, no floor — the tail stays."""
    import torch

    return torch.softmax(logits.detach().to("cpu", torch.float32), dim=-1)


def sample_item(model, tok, prompt, *, rung, size, mode, item_idx,
                seeds=SEEDS, draws_per_seed=None,
                max_new_tokens=SAMPLING_MAX_NEW_TOKENS,
                terminal_ids=None) -> dict:
    """All committed draws for one item: {seed: [draw_text, ...]}.

    One prompt forward per row-count regime; the cache is expanded in
    place to the chunk's row count and cropped back to the prompt
    between chunks (the transformers-5 pattern the mass module fixtures
    prove equal to full re-forwards). Every step samples every row from
    the seed's generator in row order — fixed consumption, so the
    stream is a pure function of (cell, seed, item).
    """
    import torch

    if draws_per_seed is None:
        draws_per_seed = DRAWS_PER_SEED[rung]
    if terminal_ids is None:
        terminal_ids = tuple(sorted(set(tok.all_special_ids)))

    enc = tok(prompt, return_tensors="pt").to(model.device)
    prompt_len = enc["input_ids"].shape[1]
    plan = chunk_plan(draws_per_seed)

    past = None
    cache_rows = None
    probs1 = None

    def fresh_cache(rows):
        nonlocal past, cache_rows, probs1
        # logits_to_keep=1 is LOAD-BEARING: the fp16-MPS full-logits
        # multi-token forward is broken on this stack (garbage logits;
        # masses.py carries the full note). Last-position-only is both
        # all this sampler needs and the only sane prefill path.
        with torch.no_grad():
            out = model(**enc, use_cache=True, logits_to_keep=1)
        probs1 = step_probs(out.logits[0, -1])
        past = out.past_key_values
        past.batch_repeat_interleave(rows)
        cache_rows = rows

    draws: dict[int, list] = {}
    for seed in seeds:
        gen = torch.Generator().manual_seed(
            stream_seed(rung, size, mode, seed, item_idx))
        texts = []
        for rows in plan:
            if cache_rows != rows:
                fresh_cache(rows)
            first = torch.multinomial(
                probs1.expand(rows, -1), 1, generator=gen)   # [rows, 1] cpu
            tokens = [first]
            step_ids = first.to(model.device)
            for t in range(1, max_new_tokens):
                attn = torch.ones((rows, prompt_len + t),
                                  device=model.device, dtype=torch.long)
                with torch.no_grad():
                    out = model(input_ids=step_ids, past_key_values=past,
                                attention_mask=attn)
                probs = step_probs(out.logits[:, -1])
                nxt = torch.multinomial(probs, 1, generator=gen)
                tokens.append(nxt)
                step_ids = nxt.to(model.device)
            past.crop(prompt_len)
            rowtok = torch.cat(tokens, dim=1).tolist()
            for row in rowtok:
                texts.append(tok.decode(truncate_at_terminal(row, terminal_ids),
                                        skip_special_tokens=True))
        draws[seed] = texts
    return draws


# ---------------------------------------- determinism fixture compare

def fixture_files_identical(p1, p2) -> bool:
    return Path(p1).read_bytes() == Path(p2).read_bytes()
