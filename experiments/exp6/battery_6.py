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
    "modarith_add1": "47a88e381a1318e828f1da08de2be70f9efb72e5e6d1c8976b76b4b0898cff9c",
    "modarith_sub1": "e2d5bdbf3060a9720e23dcb439cad2310ea341442322e8bf17b4ee33494c3d77",
    "modarith_mul1": "bf68b1a42a26959913613083c803c149c074b4489b585add5bb0f606922200c5",
    "unscramble_short": "6a3ed835ffb48a9da0cf9d050a5ffe1254939fc9666a08303e9613f9d2c11474",
    "unscramble_long": "ccb1ae923d2f8779c0b59acb7dfa4296eb8b7c8003ab9e897c8101314decb993",
    "ipa_word": "e407ecb8cdc134020c5046f0dde992fa72f8e93698521f0357f47dba95565163",
    "sort3": "ad9c04a7d5542f7040fc2c824f17a066413ef41b744c6ca14d1f3411d3d863e0",
    "sort5": "7b43811d7aec06199bc64a592323df3ade6cd56e6ac479cb4f5265122ff767d8",
    "deduction3": "7b9a7a018c233de482a75212b9a22fd1288308c9d013366f8093c466e680a663",
    "deduction5": "06154a64260665fad60b9033114d6ea72e84472fccb33e048cdbd38c8c9b2270",
    "ascii_bubble": "533bea77a563083e71015e0710d54a228ff14f4742a4e998ae311aa25351fa9e",
    "ascii_basic": "317502cf754f8dbb5b88783567a31bff319151cb67e5429101db8cd419f2ed16",
    "shapes": "6676ad74cda27c751f91ad1865f8933bda5dae0c964b3f23326a31dafbf9042b",
    "temporal": "509111620720f6ea56e5af28291e5c6c1eac03eec7a8c9eb256d680ab17295b3",
    "lcs": "66b702e5c942083b2af3d311d4cf4be995545fde61812e808f2972d8b7e7635b",
    "unit_interp1": "87d4b6c4a6d50c4f0f2581bec37ec180688f566c469345d2aa9e9e70ba2bd8c3",
    "unit_interp2": "397009ced7c91677badc691d15c4274d9623c40a41e77020dfeada7597823c78",
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
