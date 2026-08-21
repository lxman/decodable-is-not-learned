"""The target-swapped scorer (design §5.5) — the SAME verify criterion
3/3c/3d used, with the target string as a parameter.

`load_scorer()` returns 3c's ratified total wrapper (`load_verify_3c`)
unchanged: score(draw, target, answer_type) is True iff the draw's
normalized first token equals the normalized target. With target =
the item's answer it IS the fire criterion; with target = a matched
competitor it is the competitor-emission criterion. No branch is added
on the draw side (the standing stop-#1 rule: the freeze fuzzes this
for totality over the emission alphabet).

The leak-void rule is 3c's, applied identically to every target: a
target whose casefolded string occurs in the item's rendered prompt
is void for that item — its emissions are disclosed verbatim and
counted by nothing (§4).
"""

from __future__ import annotations

from experiments.exp3c import analyze_3c as c


def load_scorer():
    """score(draw, target, answer_type) → bool; 3c's total wrapper."""
    return c.load_verify_3c()


def is_void(target: str, prompt: str) -> bool:
    """3c's leak-void rule: the target occurs, casefolded, in the
    item's own rendered prompt."""
    return str(target).casefold() in str(prompt).casefold()


def emissions(rows_by_item, targets_by_item, answer_type, score_fn,
              prompts=None) -> dict:
    """Per item, per target: the emission count and every emitting
    draw's (seed, draw, text) address, plus the void flag.

    rows_by_item: {item: {seed_str: [draw_text, ...]}}
    targets_by_item: {item: [target, ...]} (the first target is the
      item's answer by convention; the function does not care)
    prompts: {item: rendered prompt} — when given, a target occurring
      in its item's prompt is marked void (count kept separately as
      `raw_count`; `count` is 0)."""
    out = {}
    for item, targets in targets_by_item.items():
        streams = rows_by_item[item]
        per_target = {}
        for tgt in targets:
            addresses = []
            for seed_key in sorted(streams, key=lambda k: int(k)):
                for d_idx, text in enumerate(streams[seed_key]):
                    if score_fn(text, tgt, answer_type):
                        addresses.append({"seed": int(seed_key),
                                          "draw": d_idx, "text": text})
            void = bool(prompts is not None
                        and is_void(tgt, prompts[item]))
            per_target[tgt] = {
                "raw_count": len(addresses),
                "count": 0 if void else len(addresses),
                "addresses": addresses,
                "void": void,
            }
        out[item] = per_target
    return out
