"""First-character mass to whitespace depth 2 (design §5, Open item 1).

The distribution itself, read exactly: for an item's committed prompt,
one forward pass yields the next-token distribution; the mass on a
character c is the probability the model's next emission BEGINS with c —
position-1 tokens whose decoded text starts (after whitespace) with c,
plus, through each pure-whitespace position-1 token w, the matching
position-2 mass P(w)·P(t|w). Whitespace-path mass still undetermined
after depth 2 is the RESIDUAL: computed, stored per item, disclosed per
cell, and bracketed onto the mass when it exceeds the §5 threshold in an
adjudicated cell. Deterministic, no sampling budget.

ONE WHITESPACE DEFINITION FOR THE WHOLE EXPERIMENT. A token's class is
`analyze_3.first_char` of its single-token decode: None means the token
defers the first visible character (pure whitespace, non-breaking space,
empty decode) and routes to depth 2; anything else is the character
itself, casefolded. The sampled draws are scored by the same
`first_char`. Gate 3's coherence check between the two instruments
therefore tests the code path (BOS, padding, prompt drift), never a
definition mismatch this module could have introduced.

The math core (`depth2_masses`, `item_mass_record`) is model-free and
fixtured on hand-computable synthetic distributions. The model-facing
glue (`classify_tokenizer`, `collect_item`) tokenizes the committed
prompt exactly as the harness does for a batch of one — no padding, no
added BOS — and its cached depth-2 pass is fixtured for equality with
full re-forwards on a synthetic random model (tests/test_mass_glue.py).
No real cell's mass exists before the exp3-preregistered tag.
"""

from __future__ import annotations

import string

from experiments.exp3.analyze_3 import first_char

TRACKED_LETTERS = tuple(string.ascii_lowercase)
_SUM_TOL = 1e-3   # fp16 logits softmaxed in float32 land well inside this


# ------------------------------------------------------------ math core

def token_first_chars(decoded) -> list:
    """Class per token id: first_char of its decode (None = whitespace-
    path). THE single source of truth shared with draw scoring."""
    return [first_char(t) for t in decoded]


def whitespace_ids(first_chars) -> tuple:
    return tuple(i for i, c in enumerate(first_chars) if c is None)


def _check_dist(p, n_classes, what) -> None:
    if len(p) != n_classes:
        raise ValueError(f"{what} has {len(p)} entries against "
                         f"{n_classes} token classes")
    neg = [i for i, v in enumerate(p) if v < 0]
    if neg:
        raise ValueError(f"{what} carries negative probability at ids "
                         f"{neg[:5]}")
    s = float(sum(p))
    if abs(s - 1.0) > _SUM_TOL:
        raise ValueError(f"{what} sums to {s!r}, not 1 — this is not a "
                         f"distribution and nothing computed from it is a "
                         f"mass")


def depth2_masses(probs1, first_chars, ws_ids, probs2_by_w, *, chars,
                  terminal_ids=()) -> dict:
    """Per-character mass to whitespace depth 2, with the residual and
    the terminal bucket.

    `probs2_by_w` maps a whitespace token id to the next-token
    distribution AFTER that token. Every whitespace id carrying
    position-1 mass must have a row — a live whitespace path with no
    depth-2 distribution would silently undercount into the residual's
    blind spot, which is 3a's valueless-input class and is refused.

    `terminal_ids` are the special ids (eos/pad): the sampled channel
    stops there, so no character ever follows — their mass joins
    neither a character nor the residual and is disclosed on its own
    (PROGRESS.md 2026-08-15). They need no depth-2 row.
    """
    _check_dist(probs1, len(first_chars), "position-1 distribution")
    ws = set(ws_ids)
    term = set(terminal_ids)
    if ws & term:
        raise ValueError(f"ids {sorted(ws & term)} classified both "
                         f"whitespace-path and terminal")
    mass = {c: 0.0 for c in chars}
    terminal_mass = 0.0
    for i, p in enumerate(probs1):
        if p == 0.0 or i in ws:
            continue
        if i in term:
            terminal_mass += float(p)
            continue
        c = first_chars[i]
        if c in mass:
            mass[c] += float(p)

    ws_mass_p1 = float(sum(probs1[i] for i in ws))
    residual = 0.0
    for w in ws_ids:
        pw = float(probs1[w])
        if pw == 0.0:
            continue
        if w not in probs2_by_w:
            raise ValueError(
                f"whitespace token id {w} carries position-1 mass {pw} but "
                f"no depth-2 distribution was supplied for it")
        p2 = probs2_by_w[w]
        _check_dist(p2, len(first_chars), f"depth-2 distribution after {w}")
        for i, p in enumerate(p2):
            if p == 0.0:
                continue
            if i in ws:
                residual += pw * float(p)
                continue
            if i in term:
                terminal_mass += pw * float(p)
                continue
            c = first_chars[i]
            if c in mass:
                mass[c] += pw * float(p)

    return {"mass": mass, "residual": residual, "ws_mass_p1": ws_mass_p1,
            "terminal_mass": terminal_mass}


def item_mass_record(probs1, first_chars, ws_ids, probs2_by_w,
                     *, label, terminal_ids=()) -> dict:
    """The per-item stored unit (§5): the full a–z vector, the label's
    own mass (also when the label is outside a–z — clock24_d999's digit
    space), the residual, and the terminal bucket. Everything downstream
    recomputes from this record without re-querying a model."""
    label_char = str(label)[0].casefold()
    chars = TRACKED_LETTERS if label_char in TRACKED_LETTERS \
        else TRACKED_LETTERS + (label_char,)
    got = depth2_masses(probs1, first_chars, ws_ids, probs2_by_w,
                        chars=chars, terminal_ids=terminal_ids)
    letters = {c: got["mass"][c] for c in TRACKED_LETTERS}
    extra = {c: got["mass"][c] for c in chars if c not in TRACKED_LETTERS}
    return {"letters": letters,
            "extra": extra,
            "label_char": label_char,
            "label_mass": got["mass"][label_char],
            "residual": got["residual"],
            "ws_mass_p1": got["ws_mass_p1"],
            "terminal_mass": got["terminal_mass"]}


# ------------------------------------------------------- model-facing glue
#
# Campaign-only path (plus its synthetic-model fixtures). Tokenization
# matches the harness for a batch of one: no padding, no added BOS, the
# continuation position is the sequence's last.

def classify_tokenizer(tok) -> tuple:
    """(first_chars, ws_ids, terminal_ids) over the tokenizer's full
    vocabulary, each id decoded alone with special tokens kept out of
    the text the way the draw decode drops them
    (skip_special_tokens=True). Special ids are terminal — carved out
    of the whitespace-path set (PROGRESS.md 2026-08-15)."""
    n = len(tok)
    decoded = tok.batch_decode([[i] for i in range(n)],
                               skip_special_tokens=True)
    fc = token_first_chars(decoded)
    terminal = tuple(sorted(i for i in set(tok.all_special_ids)
                            if 0 <= i < n))
    ws = tuple(i for i in whitespace_ids(fc) if i not in set(terminal))
    return fc, ws, terminal


def _softmax_probs(logits):
    import torch

    return torch.softmax(logits.detach().to("cpu", torch.float32),
                         dim=-1).tolist()


def collect_item_debug(model, tok, prompt, *, label, first_chars, ws_ids,
                       terminal_ids=(), ws_batch: int = 16) -> tuple:
    """One item's mass record from the live model, returning the raw
    distributions too (the glue fixtures assert them equal to full
    re-forwards).

    One forward on the committed prompt (cache kept), then the depth-2
    distributions for every whitespace token in batched single-token
    steps against the shared prompt cache. Supplying every whitespace
    id's row up front means `depth2_masses` can never hit its
    missing-row refusal on the live path.
    """
    import torch

    enc = tok(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model(**enc, use_cache=True)
    probs1 = _softmax_probs(out.logits[0, -1])
    prompt_len = enc["input_ids"].shape[1]

    # Expand the prompt cache to ws_batch rows ONCE, then per chunk:
    # one single-token step, read the rows, crop back to the prompt.
    # The pinned transformers 5 stack has no legacy tuple cache;
    # batch_repeat_interleave is in-place and crop restores reuse
    # (equality with full re-forwards is fixtured on CPU and MPS).
    live = [w for w in ws_ids if probs1[w] > 0.0]
    probs2_by_w: dict[int, list] = {}
    if live:
        past = out.past_key_values
        past.batch_repeat_interleave(ws_batch)
        attn = torch.ones((ws_batch, prompt_len + 1),
                          device=model.device, dtype=torch.long)
        for i in range(0, len(live), ws_batch):
            chunk = live[i:i + ws_batch]
            padded = chunk + [chunk[-1]] * (ws_batch - len(chunk))
            ids = torch.tensor([[w] for w in padded], device=model.device)
            with torch.no_grad():
                step = model(input_ids=ids, past_key_values=past,
                             attention_mask=attn)
            for row, w in enumerate(chunk):
                probs2_by_w[w] = _softmax_probs(step.logits[row, -1])
            past.crop(prompt_len)

    rec = item_mass_record(probs1, first_chars, ws_ids, probs2_by_w,
                           label=label, terminal_ids=terminal_ids)
    return rec, probs1, probs2_by_w


def collect_item(model, tok, prompt, *, label, first_chars, ws_ids,
                 terminal_ids=(), ws_batch: int = 16) -> dict:
    rec, _, _ = collect_item_debug(
        model, tok, prompt, label=label, first_chars=first_chars,
        ws_ids=ws_ids, terminal_ids=terminal_ids, ws_batch=ws_batch)
    return rec


