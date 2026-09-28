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
    "modarith_add1": "640b3bf47183492d1731b624c2163bbfb558a2f81d952e323849de50e2cc653d",
    "modarith_sub1": "ddb0f68811b9256fa79e7091bb416a9595e5ee1e92dc72c88d734a638eb2efdd",
    "modarith_mul1": "15f7ad8a269407cbf3d27e82eae8c90819ad11073e75f0a4cb92bd8438cb20d4",
    "unscramble_short": "657eeaa3f622296f4b85b3df1c615121c28d9705ff89e5734881368f07c84c47",
    "unscramble_long": "8b6883a4a0acb08b2a713fcf78afbac6fb70f04af9c3e3d78de217c5152f112a",
    "ipa_word": "4a688a20399005d9e59e2b6fae77111fdd967c47fd38709c97e9c561637149d6",
    "sort3": "bbda582a895ed120462de12f590cef7c346bfabcdaaaa708d5331841358fa9e0",
    "sort5": "dfed87d3527b7fd452a386ff73b60f8b08f2dbc46f7794fbfa5d89cbf9cf643d",
    "deduction3": "6c8700408438db2d0504662e933b3cc403bc4a046c53a1f6caeace1caf35cb61",
    "deduction5": "436d8db33b2149ee8185687a8dabcb20e9976631f34016f58b186b97ede7b977",
    "ascii_bubble": "6f339ca66a687dead2c0fbb1b3ac8e1582f06f21e103b9f8193803b887503c96",
    "ascii_basic": "a3b8d7d0d1d98c186ed4696e7a643cf12a432995e6383e8ba66878b3b06bf107",
    "shapes": "7b033b4f7245173df763733ccfba5e7e8c08a51f2c15c222ae0a0236be20c57c",
    "temporal": "145546eff53c34cc116558c25545ecae5253069b624a7d60c915744507c560e6",
    "lcs": "7fb694003134af14118a0364b00b86f3eeae03cf8df83ed5c6530bf72332d152",
    "unit_interp1": "c6b8f6b60a02379e3e622b175eef01e71e0841a7d0e2c3a3d93444e238ab5af3",
    "unit_interp2": "33642854e4d70025b3cd5c9a1c1c20154b7b4b233d24581b9565ace667116e36",
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
