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
    "modarith_add1": "54bdb29cc0bfda6de7f97a20b153f8e3b5c4359ac741445a4cc328503b526a06",
    "modarith_sub1": "ac4cf884cad3d2cffc3a9fa23fe7ebfb04a6b652f7eb47817bbfeaa237afc11f",
    "modarith_mul1": "4adefa20d1ba12e690f0d3887b579cfb33d739c3b46a1b0b6ce19f62d305c7a7",
    "unscramble_short": "1fcc4ea90eea13b41efa251dfccc1ba305f9acbcfd9d3a7d9b92e7272c1c7a36",
    "unscramble_long": "ec6df3b0cb6225f5b288c7cf6727ac6adc777e4d2c7e17c26b41414f261aaa4e",
    "ipa_word": "eba6d6eea261715acec118edcbeddcbf629d55055c83f624fc640657e6e97157",
    "sort3": "1668b08a1e052a62fe9275f30db0271706f30a0f1b1d3c33c286aac18e637966",
    "sort5": "41d63836ee9c4f9d04108c857fe23a92d3bfe69ccd7b9acf7a210151a74731d5",
    "deduction3": "1741f51e75ccb1b7043dfd9ac943bbe37fa92a6761d8a831a0c4a5a6534ccf38",
    "deduction5": "3513158a9641ae0d3d0753e2919cd3d516f67b4776dc53a70dab4438e994af05",
    "ascii_bubble": "ca3d84e38aa43de8078081b220a93c39b72baa431e708251e6d46a343aa0b408",
    "ascii_basic": "0dc0bc2c442658fefe737d2d251643e060d9658a4fdd42aa75d82dc3d2dbdae1",
    "shapes": "a40f7c7b0a04145954121a0334de347e3ad8c96ba5f90710d75ff59629086f60",
    "temporal": "0c374aee456d376057409aab834f506b9ca073a7d15611a37e86ea5141da5174",
    "lcs": "b6dfeba59ff7beb25492dc1d2719f90cd45bcbbbbb9be198336e1115f2c8775e",
    "unit_interp1": "182714687a2d9405dd369593ddb055f4c096c28f470268afd60ae56dc22c7f37",
    "unit_interp2": "06fa36a809fd41b1de0a01fd3c5f26cadb41ec127d3d3fb9e5fc9b14c7b46cb8",
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
