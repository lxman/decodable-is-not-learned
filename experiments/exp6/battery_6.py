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
    "modarith_add1": "a425702b0a8b9391123072c88bc4d52693de2ac698f22b40c2e810001633518b",
    "modarith_sub1": "cf0349e0fa4b5e939f299db8bccd76cf45501374c56b46203f452eb2a2dca872",
    "modarith_mul1": "900c1aa30432c17a5de9cadb3c866da5a27bbca0158246ba7455e82bbce0bb02",
    "unscramble_short": "86bcc3d8606219df2d9b8e6f5fdb67e0fad92ab5d9bb89da6d59213157a7b69d",
    "unscramble_long": "f90e25c1ff08e4c97b59811b97cc568359ed9e79b2f515031aa20c9e5034d2f2",
    "ipa_word": "79b57158fa43bbc7f834de90eebecb4d5a82be93f925bf9f29e8f7561c342e8d",
    "sort3": "5f85efcf268195e8842c4ee83e7beb1ed7cc11c6fe31e80c845f12f3cf8db6aa",
    "sort5": "39b1f9667a55b1b33bc63593a87ef8b144b1ce299ebd80b5aaafd9946103814d",
    "deduction3": "1b06735a830e81596898a0241301b1357502c0d8e6f24c0c08f67104d3d55124",
    "deduction5": "90020e1c984ab4668341e2eb81965aa1514ccb38b7483a6e18b4e8bb8f5415f7",
    "ascii_bubble": "65ecb9ada46f247f2c2f53c37e3ee945ba90b716f11fc1b080bdf5c38d04880c",
    "ascii_basic": "5a4dd2421368ff7b801d0c0056b51092bf4a968d4bef06bb243ef06c070eb9b6",
    "shapes": "d29b1ed5135256a9559b8e8ec92099b2ab6a57dc762ec7adef8910f4f3ee6a7e",
    "temporal": "9c251cdf06fb6e03920f9b8c8966d1d6c7cf33250bed718dbad00041c728c1bd",
    "lcs": "30346b90e1860df842ac89dad1986dd4b5660a2c0e05596b0aae0042a793c948",
    "unit_interp1": "6fd4dfecf95f35a26b8ecb9737dd80c0c4d1e784ddad77eb654d6e46f3957b04",
    "unit_interp2": "b6cb00175b0a9114f157ae98ca3fc27d8660e1063e022bda7cbe9c5eb5cae173",
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
