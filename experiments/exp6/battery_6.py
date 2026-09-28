# experiments/exp6/battery_6.py
"""Exp 6 battery constants and the sha-pinned item loader (design §3.1).

Eighteen candidate rungs were designed; seventeen are built (plan delta
B-1: `logic_grid` is excluded under the design's own rule (ii) — its
README publishes the vocabulary and not the clue generator). The two
anchors and the control are 2c's committed files, loaded through 2d's
own sha-pinned loader."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

EXP6 = Path(__file__).resolve().parent
EXPERIMENTS = EXP6.parent
REPO = EXPERIMENTS.parent
ITEMS_DIR = EXP6 / "battery" / "items"
N_ITEMS = 500
N_SHOTS = 2

RUNGS_6 = ("modarith_add1", "modarith_sub1", "modarith_mul1",
           "unscramble_short", "unscramble_long", "ipa_word",
           "sort3", "sort5", "deduction3", "deduction5",
           "ascii_bubble", "ascii_basic", "shapes", "temporal", "lcs",
           "unit_interp1", "unit_interp2")
ANCHORS_6 = ("add_base8", "sub_base8")
CONTROL_6 = "ctrl_copy"
ALL_RUNGS_6 = RUNGS_6 + ANCHORS_6 + (CONTROL_6,)

TASK_OF = {
    "modarith_add1": "modified_arithmetic", "modarith_sub1": "modified_arithmetic",
    "modarith_mul1": "modified_arithmetic",
    "unscramble_short": "word_unscrambling", "unscramble_long": "word_unscrambling",
    "ipa_word": "international_phonetic_alphabet_transliterate",
    "sort3": "word_sorting", "sort5": "word_sorting",
    "deduction3": "logical_deduction", "deduction5": "logical_deduction",
    "ascii_bubble": "ascii_word_recognition", "ascii_basic": "ascii_word_recognition",
    "shapes": "geometric_shapes", "temporal": "temporal_sequences",
    "lcs": "cs_algorithms",
    "unit_interp1": "unit_interpretation", "unit_interp2": "unit_interpretation",
}
WEI_CLASS_OF = {r: ("E.2" if TASK_OF[r] in (
    "modified_arithmetic", "word_unscrambling", "word_sorting",
    "international_phonetic_alphabet_transliterate", "logical_deduction")
    else "E.3") for r in RUNGS_6}
RUNG_TYPE_OF = {
    "modarith_add1": "arithmetic", "modarith_sub1": "arithmetic",
    "modarith_mul1": "arithmetic", "lcs": "arithmetic",
    "unscramble_short": "string", "unscramble_long": "string",
    "ipa_word": "string", "sort3": "string", "sort5": "string",
    "ascii_bubble": "string", "ascii_basic": "string", "shapes": "string",
    "deduction3": "choice", "deduction5": "choice", "temporal": "choice",
    "unit_interp1": "choice", "unit_interp2": "choice",
}
ANSWER_TYPE_OF = {
    "modarith_add1": "number", "modarith_sub1": "number",
    "modarith_mul1": "number", "lcs": "number",
    "unit_interp1": "number", "unit_interp2": "number",
    "unscramble_short": "word", "unscramble_long": "word",
    "ascii_bubble": "word", "ascii_basic": "word", "shapes": "word",
    "deduction3": "word", "deduction5": "word",
    "temporal": "span", "ipa_word": "ipa", "sort3": "sequence",
    "sort5": "sequence",
}
N_OPTIONS_OF = {"deduction3": 3, "deduction5": 5, "shapes": 10, "temporal": 4,
                "unit_interp1": 5, "unit_interp2": 5}

ITEMS_SHA_PIN_6 = {
    "modarith_add1": "8a0e2ae152441d8189603ff8a5f49ce7de62b490c896855548d1912673f32668",
    "modarith_sub1": "1df630360c2992a0172d2e2394a5e9f080fc6274d9280510f40fc96815c975d9",
    "modarith_mul1": "d1501e8be3e2d219917262b80815e26f069cb6a5a7e2eb8045b2351142f7d4c7",
    "unscramble_short": "50a375620de88dabefb3ba372d334ba11c20dc8d2bb80ef8165a97aa6455f2f4",
    "unscramble_long": "636f0ab0ec8b1654aadb8bf1975990c0a97aecc8babd28e048340d24d8d5eb7c",
    "ipa_word": "695a7f13967daa4ddf6e30e62ad0b29da94a0c51017ae250bf31742f43efd0a4",
    "sort3": "a6537391757f6e3283366f058cc107d0b94bd9774d945cf703c217aaa887674b",
    "sort5": "adbab5d0416a47196e9664e5d39fca82701d7d3fc23129e1045586fcaf975fc6",
    "deduction3": "d41ce851a23b63e9a7646ce3709c00e3d0bcb955e36d7c650f4af37b1cea5ec3",
    "deduction5": "34166f6f00817476b41266cbab88c402f11392f6571213ebb1642bc226d36e6f",
    "ascii_bubble": "a01a59cd71644d07719d3d4566905498d042c9ce06205c020aec878e69b1d0c8",
    "ascii_basic": "cfacedd60dfd61f64832922c3d37ed4c85411bd3c3757ac4126f107265363a8e",
    "shapes": "442aa60cf0304129b4b7b7875aa25a654154fe0ef7363b952d95fe46c29a3b36",
    "temporal": "4cce074c7457977ffacc0a39a54a1f80192be362a41a64357ffd942a2f70b5d4",
    "lcs": "3fe081b312056ea4fbe14fad2461d140be0a580d76176f85f7cffba19e872b67",
    "unit_interp1": "6df0f2bc34b34b7d25a58c3742cd7e8e8ee366d76bb42d1054766c854de6fcb4",
    "unit_interp2": "cb88c8b7dca7b8c2690fa0e88882c1d72e372d3a5838364a4f9abdd088c8cd1e",
}


# the copy control: 2c's committed file, the sha exp3's records carry
CONTROL_PATH = EXPERIMENTS / "exp2c" / "battery" / "items" / "ctrl_copy.json"
CONTROL_SHA256 = "b75141477beecbd2933a02d93777bf787a1d39a5693b88436b68d0bdcdab6832"
CONTROL_ANSWER_TYPE = "word"


def _load_control() -> dict:
    raw = CONTROL_PATH.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != CONTROL_SHA256:
        raise ValueError(f"{CONTROL_PATH} has sha256 {got} against the pin "
                         f"{CONTROL_SHA256}")
    cap = json.loads(raw)
    if cap.get("name") != CONTROL_6 or len(cap["eval_items"]) != N_ITEMS:
        raise ValueError(f"{CONTROL_PATH}: not the 500-item copy control")
    cap["answer_type"] = CONTROL_ANSWER_TYPE
    cap["items_sha256"] = got
    cap["battery"] = "2c"
    return cap


def items_path_6(rung: str) -> Path:
    if rung not in RUNGS_6:
        raise ValueError(f"{rung!r} is not an Exp 6 rung")
    return ITEMS_DIR / f"{rung}.json"


def load_item_file_6(rung: str) -> dict:
    """The committed item file, sha-checked BEFORE parsing; the anchors
    and the control go through 2d's own pinned loader."""
    if rung in ANCHORS_6:
        from experiments.exp2d import battery_2d as bt
        cap = bt.load_item_file(rung)
        cap["battery"] = "2c"
        return cap
    if rung == CONTROL_6:
        return _load_control()
    p = items_path_6(rung)
    raw = p.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != ITEMS_SHA_PIN_6[rung]:
        raise ValueError(f"item file {p} has sha256 {got} against the pin "
                         f"{ITEMS_SHA_PIN_6[rung]} — these are not the "
                         f"committed items")
    cap = json.loads(raw)
    if cap.get("name") != rung:
        raise ValueError(f"{p} names {cap.get('name')!r}, not {rung!r}")
    for key, table in (("answer_type", ANSWER_TYPE_OF), ("task", TASK_OF),
                       ("wei_class", WEI_CLASS_OF), ("rung_type", RUNG_TYPE_OF)):
        if cap.get(key) != table[rung]:
            raise ValueError(f"{p}: {key} {cap.get(key)!r} against the pin "
                             f"{table[rung]!r}")
    if cap.get("n_options") != N_OPTIONS_OF.get(rung):
        raise ValueError(f"{p}: n_options {cap.get('n_options')!r} against the "
                         f"pin {N_OPTIONS_OF.get(rung)!r}")
    if len(cap["eval_items"]) != N_ITEMS or len(cap["shots"]) != N_SHOTS:
        raise ValueError(f"{p}: {len(cap['eval_items'])} items, "
                         f"{len(cap['shots'])} shots")
    if len(cap.get("shot_records", ())) != N_SHOTS:
        raise ValueError(f"{p}: {len(cap.get('shot_records', ()))} shot records")
    cap["items_sha256"] = got
    cap["battery"] = "6"
    return cap


def load_battery_6(rungs=ALL_RUNGS_6) -> dict:
    return {r: load_item_file_6(r) for r in rungs}


def max_new_tokens_6(rung: str) -> int:
    from experiments.exp6 import verify_6 as v6
    if rung in ANCHORS_6:
        from experiments.exp2d import battery_2d as bt
        return bt.max_new_tokens(rung)
    if rung == CONTROL_6:
        return v6.MAX_NEW_TOKENS_6[CONTROL_ANSWER_TYPE]
    return v6.MAX_NEW_TOKENS_6[ANSWER_TYPE_OF[rung]]
