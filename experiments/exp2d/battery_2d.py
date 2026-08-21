"""The Exp 2d battery: 2c's 34 screened rungs in 16 families, every
input a committed value (design §2, §4).

Nothing here is a dial. The rung set, the family map, the item files,
the answer types and the token budgets are 2c's (imported from the
closed exp2c/exp2b trees, sha-pinned by literal); the one new
quantity — the MAJORITY-ANSWER FLOOR (§5.2, ruling a) — is a pure
function of the committed item file under 2c's own `normalize_answer`.

The rung ORDER is load-bearing: it is the family-contiguous order 2c's
verdict grouped its arrays into (`results/probe_scores.json`'s row
order = family first appearance in `scored_battery_families()`), and
2c's block-permutation machinery exchanges family blocks POSITION-FOR-
POSITION, so the within-block order fixes which rung of a recipient
family inherits which rung's label. 2d pins that order as a literal
and refuses disagreement with either committed source.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

EXP2D = Path(__file__).resolve().parent
EXPERIMENTS = EXP2D.parent
REPO = EXPERIMENTS.parent
EXP2B = EXPERIMENTS / "exp2b"
EXP2C = EXPERIMENTS / "exp2c"

# ORDER MATTERS (exp3's runner, verbatim reasoning): exp2c must win the
# `harness` name; exp2b supplies `models`.
for _p in (EXP2B, EXP2C):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

N_ITEMS = 500
N_SHOTS = 2
PROBE_SIZES = ("410m", "1b")            # §3: the from-below instrument
EVAL_SIZES = ("2.8b", "6.9b", "12b")    # §4: 2c's committed outcome

# ---------------------------------------------------------------- order
#
# (rung, family) in 2c's verdict order — family-contiguous, families in
# first-appearance order of `scored_battery_families()`, rungs within a
# family in that function's iteration order. Checked against BOTH
# committed sources at load (`check_order_against_2c`).
RUNG_ORDER_2D = (
    ("add4_mid", "mid_digit"), ("sub4_mid", "mid_digit"),
    ("add3_mid", "mid_digit"), ("sub3_mid", "mid_digit"),
    ("antonym6", "antonym"), ("antonym", "antonym"),
    ("arith_next", "seq_extrap"), ("quad_next", "seq_extrap"),
    ("base12_digitsum", "base_repr"), ("base13", "base_repr"),
    ("base7", "base_repr"), ("oct2dec", "base_repr"),
    ("caesar_len8", "rotation"), ("caesar", "rotation"),
    ("clock24_d999", "clock"), ("clock24", "clock"),
    ("collatz_step2", "rescue_collatz"),
    ("count_div13", "counting"), ("count_div7", "counting"),
    ("hamming12", "str_align"),
    ("isqrt_gap", "rescue_isqrt"),
    ("median5", "order_stat"), ("median7", "order_stat"),
    ("mod13_comp", "modulus"), ("mod17", "modulus"),
    ("mod19", "modulus"), ("mod13", "modulus"),
    ("odd6", "odd_one_out"), ("odd_one_out", "odd_one_out"),
    ("rev_string7", "reversal"), ("reverse_string", "reversal"),
    ("roman_sum7", "rescue_roman"),
    ("sub_base8", "base_arith"), ("add_base8", "base_arith"),
)
RUNGS = tuple(r for r, _ in RUNG_ORDER_2D)
FAMILY_OF = dict(RUNG_ORDER_2D)
FAMILY_ORDER = tuple(dict.fromkeys(f for _, f in RUNG_ORDER_2D))
FAMILY_SIZES = tuple(sum(1 for _, f in RUNG_ORDER_2D if f == fam)
                     for fam in FAMILY_ORDER)
N_RUNGS = len(RUNGS)            # 34
N_FAMILIES = len(FAMILY_ORDER)  # 16

# 2b survivors (2c's reuse_manifest.json keys): their item files live
# under exp2b and carry answer_type inline; the 22 new rungs take it
# from 2c's SPECS registry.
REUSED = ("mod13", "add3_mid", "sub3_mid", "base7", "oct2dec", "add_base8",
          "caesar", "count_div7", "reverse_string", "clock24", "antonym",
          "odd_one_out")

# §4: every item file, sha-pinned by literal (computed at build from
# the committed trees; the 12 survivors' also cross-checked against
# 2c's reuse manifest — three sources, one value).
ITEMS_SHA_PIN = {
    "add4_mid": "15cb8a7880a845becdfa5131c0bfd6fb2f003a5284fce528bd484f385d1cb83b",
    "sub4_mid": "c9c21663055866ec761668cc7a2e073d8e471bbd0b3994005759e45f8d7bcc50",
    "add3_mid": "7a3342748ae662ff85b3a1d2834fe04f719ef24fec9ccfef03c5f9e40f426408",
    "sub3_mid": "de8a8222b93ac7f0805b387e3981eb69e874bc305d4f803cfbb1a83857151632",
    "antonym6": "6c6d6082c29b4df91f9d5665fb7a6735d699759502fc12523596eca904c3768f",
    "antonym": "2b393de42ac38ca38cb1ccbe6ee8f8d12882c041ed4a4430d0add6287c5c238e",
    "arith_next": "b5dd05a00a14eff319b7e22969aab4c291d332277563ac59eca35aa637da22d5",
    "quad_next": "eac23ad300fad8cd56d41b99f5ed58679ba0681ec1f6efb8a6fe91fda8229c7f",
    "base12_digitsum": "5e4657aac9a20ee818426d23cb7cde8c528973c8ca970303a05c5c5935f97e8a",
    "base13": "5ac79b9e758100303db79eb8eed094d32341ab7efceb18bd4b3e975322e1dcde",
    "base7": "882f40081bc06f387912ff6f8abed6f27ef3a82c96a251c21c500d05f73426e5",
    "oct2dec": "49bfde97c361d3af023009a80f4f0a1db0df0fa6a02fc6a301324e352cd12c2e",
    "caesar_len8": "82e193733cb633db1654cee14e5882ea4d7e32679d576ebd264bc8560e63db1b",
    "caesar": "757a38c839a9564cdcd2ffda84c3f99b59ab03da3d2ff542daa3a4767ea09e49",
    "clock24_d999": "a117c7d58e34c6ecad27b2ed60b3a6b062c9e856d82351e9279883a8510bc1b1",
    "clock24": "58c26efec888cb3cce8d9777b78ede152b1553fdf23dad656ed6045f5cead505",
    "collatz_step2": "d92296c03aa5cba888cdbc7916bdf289ad4f46daf46801d91b400cbcc2c11fcb",
    "count_div13": "a732008b2caef717365853324155c44d73f1c969b657cb059a2be9af02f8f6a9",
    "count_div7": "9d639f432dec66cf669261fc2cebee7cb97399f4d45bb0b56a9a70cb6a142d7a",
    "hamming12": "aef5e465c01e6990df972b0882075477a710d75f7c4a6a3efe836e85377edf6c",
    "isqrt_gap": "26edadc06658ea510961db4315667d03fb7b874f9eb7ad7db8282c4a7dd8d7b5",
    "median5": "368c64ba02d8515bec2db613540635e1e3f45f03399fca4bcd3fb26b91d97165",
    "median7": "4582306952732b746dc8b0ed0f395a73f1ec64719fd50fcef864cae481ae73ac",
    "mod13_comp": "dba8ef287df7f4792c2adef52f33b461b4a1d19fba309038ef76891101ae6147",
    "mod17": "6e091cde5b58bae78806dcc728587d7ebb867c95f38099c2a469211935e230c9",
    "mod19": "1595b5f56de931c7f8ea818a96e12dd867093a3e3a134d0713563b035b5aa2fd",
    "mod13": "1360b89a2b64e757f837279ab0416634f7b6c58ad6411e5e312ab0da166f80c1",
    "odd6": "7eef80d7902eca43751f60601eaf514525806d7d0abc68ac3375efe37186f7ef",
    "odd_one_out": "0c5b90dfa1a932460232924ada815716b74718d32a2326d15a981e5d6a06f2c3",
    "rev_string7": "d0fca235d101e142aabaddbdf5d78e189b7a91c96672364b961e83d1635a83f5",
    "reverse_string": "ad5bdcd944e3b983da42825a493eb813269b0ffebadb64f40fb1ee0f834f68c9",
    "roman_sum7": "62f3373970387a2543960823138b6e8964a1d250470d2a1bf2797fef913ac3af",
    "sub_base8": "d571131db31c40d0019781a64d6e803507434d23a2ea6c50763727aec4fed65e",
    "add_base8": "f7b270d1284107476ead8b8d8a4a0e1aabdfbb42ac69ea13233e6d481252bae1",
}

# §3: the answer type per rung (2c's SPECS / the 2b file), pinned by
# literal and re-asserted against the registry at load. Only TWO types
# occur in this battery — `number` (8 tokens) and `word` (12 tokens);
# 2c's `letters` and `choice` budgets are never used (doc §11 says
# "four answer types"; ledgered).
ANSWER_TYPE_PIN = {
    "add4_mid": "number", "sub4_mid": "number", "add3_mid": "number",
    "sub3_mid": "number", "antonym6": "word", "antonym": "word",
    "arith_next": "number", "quad_next": "number",
    "base12_digitsum": "number", "base13": "number", "base7": "number",
    "oct2dec": "number", "caesar_len8": "word", "caesar": "word",
    "clock24_d999": "word", "clock24": "word", "collatz_step2": "number",
    "count_div13": "number", "count_div7": "number", "hamming12": "number",
    "isqrt_gap": "number", "median5": "number", "median7": "number",
    "mod13_comp": "number", "mod17": "number", "mod19": "number",
    "mod13": "number", "odd6": "word", "odd_one_out": "word",
    "rev_string7": "word", "reverse_string": "word", "roman_sum7": "number",
    "sub_base8": "number", "add_base8": "number",
}
ANSWER_TYPES_PRESENT = ("number", "word")


# ------------------------------------------------------------ 2c imports

def harness_2c():
    """2c's harness, provenance-asserted (3c's discipline): the module
    named `harness` must resolve under exp2c, whose `render_prompt`,
    `normalize_answer` and `MAX_NEW_TOKENS` produced the outcome."""
    import harness
    got = Path(harness.__file__).resolve()
    if EXP2C.resolve() not in got.parents:
        raise ImportError(
            f"harness resolved to {got}, which is not under the exp2c "
            f"tree — 2d would render or score with the wrong code")
    return harness


def family_map_2c():
    from experiments.exp2c.battery import family_map
    return family_map


def items_path(rung: str) -> Path:
    if rung not in ITEMS_SHA_PIN:
        raise ValueError(f"{rung!r} is not a 2d rung")
    if rung in REUSED:
        return EXP2B / "battery" / "items" / f"{rung}.json"
    return EXP2C / "battery" / "items" / f"{rung}.json"


def load_item_file(rung: str) -> dict:
    """The committed item file, sha-checked against the §4 pin BEFORE
    parsing (3c finding A). Returns the capability dict with
    `answer_type` set and the raw sha attached."""
    p = items_path(rung)
    raw = p.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != ITEMS_SHA_PIN[rung]:
        raise ValueError(
            f"item file {p} has sha256 {got} against the §4 pin "
            f"{ITEMS_SHA_PIN[rung]} — these are not the committed items")
    cap = json.loads(raw)
    if rung in REUSED:
        at = cap.get("answer_type")
    else:
        at = harness_2c().answer_type_of(rung)
    if at != ANSWER_TYPE_PIN[rung]:
        raise ValueError(
            f"{rung}: answer_type {at!r} from the registry/file against "
            f"the pinned {ANSWER_TYPE_PIN[rung]!r}")
    cap["answer_type"] = at
    cap.setdefault("name", rung)
    if cap.get("name") != rung:
        raise ValueError(f"{p} names {cap.get('name')!r}, not {rung!r}")
    if len(cap["eval_items"]) != N_ITEMS:
        raise ValueError(f"{rung}: {len(cap['eval_items'])} eval items, "
                         f"not {N_ITEMS}")
    cap["items_sha256"] = got
    return cap


def load_battery() -> dict:
    """All 34 capabilities, keyed by rung, in RUNG_ORDER_2D."""
    return {r: load_item_file(r) for r in RUNGS}


def max_new_tokens(rung: str) -> int:
    """2c's generation cap for the rung's answer type — the budget the
    outcome was measured under (§3)."""
    return int(harness_2c().MAX_NEW_TOKENS[ANSWER_TYPE_PIN[rung]])


# -------------------------------------------------------- order checks

def check_order_against_2c(probe_path=None, manifest_path=None) -> dict:
    """RUNG_ORDER_2D == 2c's two committed sources: the family map
    (membership + family labels + family first-appearance order) and
    probe_scores.json's row order (the order 2c's verdict grouped).
    Also: the 12 survivors' item shas == the reuse manifest's."""
    fm = family_map_2c().scored_battery_families()
    if set(fm) != set(RUNGS):
        raise ValueError(
            f"2c's scored battery {sorted(fm)} is not the pinned 34: "
            f"missing {sorted(set(fm) - set(RUNGS))}, extra "
            f"{sorted(set(RUNGS) - set(fm))}")
    for r, f in RUNG_ORDER_2D:
        if fm[r] != f:
            raise ValueError(f"{r}: family {fm[r]!r} in 2c's map, pinned "
                             f"{f!r}")
    fam_first = tuple(dict.fromkeys(fm.values()))
    if fam_first != FAMILY_ORDER:
        raise ValueError(f"family first-appearance order {fam_first} != "
                         f"pinned {FAMILY_ORDER}")
    probe = json.loads(Path(probe_path or EXP2C / "results"
                            / "probe_scores.json").read_text())
    probe_order = tuple((r["name"], r["family"]) for r in probe["rungs"])
    if probe_order != RUNG_ORDER_2D:
        raise ValueError("probe_scores.json's row order is not the pinned "
                         "RUNG_ORDER_2D — the block layout would differ "
                         "from 2c's verdict")
    if tuple(family_map_2c().family_sizes()) != FAMILY_SIZES:
        raise ValueError("family_sizes() disagrees with the pinned vector")
    manifest = json.loads(Path(manifest_path or EXP2C / "results"
                               / "reuse_manifest.json").read_text())
    for r in REUSED:
        ent = manifest["survivors"][r]["item_file"]
        if ent["sha256"] != ITEMS_SHA_PIN[r]:
            raise ValueError(f"{r}: reuse manifest sha {ent['sha256']} != "
                             f"pinned {ITEMS_SHA_PIN[r]}")
        if (REPO / ent["path"]).resolve() != items_path(r).resolve():
            raise ValueError(f"{r}: manifest path {ent['path']} is not "
                             f"the pinned item path")
    return {"n_rungs": N_RUNGS, "n_families": N_FAMILIES,
            "family_sizes": list(FAMILY_SIZES)}


# ------------------------------------------------------------ the floor

def normalized_answers(cap: dict) -> list:
    h = harness_2c()
    at = cap["answer_type"]
    return [h.normalize_answer(str(it["answer"]), at)
            for it in cap["eval_items"]]


def majority_floor(cap: dict) -> dict:
    """§5.2 / ruling a: c_g = the largest share any single NORMALIZED
    answer string holds among the rung's 500 eval answers — the score
    of 'always emit the most common answer', model-free. Also returns
    |A| (distinct normalized answers) for the §8 descriptive."""
    answers = normalized_answers(cap)
    counts = Counter(answers)
    top, n_top = counts.most_common(1)[0]
    return {"floor": n_top / len(answers), "majority_answer": top,
            "majority_count": int(n_top), "n_items": len(answers),
            "n_distinct_answers": len(counts)}


# ---------------------------------------- option-copy floor (RULED)
#
# RULED by Michael 2026-08-21 (build finding H): six rungs present the
# answer among options LISTED IN THE QUESTION (antonym, antonym6,
# median5, median7, odd6, odd_one_out) — all six rising under the
# majority floor alone. "Copy one listed option at random" scores
# 1/n_options on them, far above the majority share, and the majority
# floor cannot see it. The floor for such a rung is therefore
#     c_g = max(majority-answer share, 1 / n_options),
# applied IDENTICALLY to the outcome and the predictor (ruling a's own
# principle — the dumbest baseline made executable — for the baseline
# that actually exists on those rungs). Membership and n_options are
# pinned by literal and RE-DERIVED from the item file at every load:
# a rung is option-listing iff EVERY eval question lists the normalized
# answer among a colon-introduced, comma-separated option list of one
# uniform length; a partial or non-uniform listing is refused, never
# guessed.
OPTION_LISTING_PIN = {"antonym": 4, "antonym6": 6, "median5": 5,
                      "median7": 7, "odd6": 6, "odd_one_out": 4}


def option_copy_floor(cap: dict) -> dict | None:
    """{n_options, floor = 1/n_options} if every eval question lists
    the normalized answer among a uniform-length option list; None if
    none does; ValueError on anything in between (no silent call)."""
    h = harness_2c()
    at = cap["answer_type"]
    n_listed, n_opts = 0, set()
    for it in cap["eval_items"]:
        q = it["question"]
        if ":" not in q:
            continue
        tail = q.rsplit(":", 1)[1].rstrip("?. ")
        opts = [h.normalize_answer(o, at) for o in tail.split(",")]
        opts = [o for o in opts if o]
        if h.normalize_answer(str(it["answer"]), at) in opts:
            n_listed += 1
            n_opts.add(len(opts))
    if n_listed == 0:
        return None
    if n_listed != len(cap["eval_items"]) or len(n_opts) != 1:
        raise ValueError(
            f"{cap.get('name')}: the answer is listed among options in "
            f"{n_listed} of {len(cap['eval_items'])} questions with option "
            f"counts {sorted(n_opts)} — neither a clean option-listing "
            f"rung nor a clean non-listing one; refusing to guess a floor")
    n = n_opts.pop()
    return {"n_options": int(n), "floor": 1.0 / n, "share_listed": 1.0}


def rung_floor(cap: dict) -> dict:
    """§5.2 as ruled: the majority-answer share, raised to 1/n_options
    on the option-listing rungs; the pin and the re-derivation must
    agree on membership AND n_options."""
    maj = majority_floor(cap)
    oc = option_copy_floor(cap)
    name = cap.get("name")
    pinned = OPTION_LISTING_PIN.get(name)
    if (oc is None) != (pinned is None) or \
            (oc is not None and oc["n_options"] != pinned):
        raise ValueError(
            f"{name}: option-listing re-derivation {oc} disagrees with the "
            f"pin {pinned} — the floor rule's membership is not what was "
            f"frozen")
    floor = max(maj["floor"], oc["floor"]) if oc else maj["floor"]
    return {**maj, "majority_floor": maj["floor"], "option_copy": oc,
            "floor": float(floor),
            "floor_rule": ("max(majority, 1/n_options)" if oc
                           else "majority")}


def floor_table(battery: dict | None = None) -> dict:
    """Per rung: the FROZEN floor (`floor`) with its components."""
    battery = battery or load_battery()
    return {r: rung_floor(battery[r]) for r in RUNGS}


def option_copy_table(battery: dict | None = None) -> dict:
    battery = battery or load_battery()
    out = {}
    for r in RUNGS:
        oc = option_copy_floor(battery[r])
        if oc is not None:
            out[r] = oc
    return out


# §4's printed floors (the doc's paragraph), a known-answer referent
# for the floor rule: the computed table must round to these.
DOC_FLOORS = {
    "antonym": .026, "antonym6": .020, "median5": .008, "hamming12": .226,
    "odd_one_out": .014, "sub3_mid": .014, "arith_next": .020,
    "count_div13": .158, "odd6": .026, "collatz_step2": .166,
    "median7": .010, "sub_base8": .056, "isqrt_gap": .164,
    "roman_sum7": .154, "add_base8": .028, "mod13": .094, "mod17": .076,
    "mod13_comp": .094, "add3_mid": .006, "mod19": .066,
    "clock24_d999": .060, "count_div7": .100, "clock24": .072,
    "sub4_mid": .006, "quad_next": .018,
}
DOC_FLOOR_CAP_REST = .010   # "add4_mid, ..., reverse_string: floors ≤ .010"
# DOC SLIP (build, ledgered for ratification): §4 lists base12_digitsum
# and base13 among the rungs with "floors ≤ .010"; their accuracies ARE
# ≤ .006 at every size as stated, but their majority-answer floors are
# .038 and .068 (answer '2' in both). Pinned here at the computed
# values so the referent check stays exact.
DOC_FLOOR_SLIPS = {"base12_digitsum": .038, "base13": .068}


def check_floors_against_doc(table: dict) -> None:
    """§4's printed table is the MAJORITY component; the six
    option-listing rungs' effective floors are 1/n_options (ruling H)."""
    for r in RUNGS:
        c = table[r]["majority_floor"]
        if r in OPTION_LISTING_PIN:
            if table[r]["floor"] != max(c, 1.0 / OPTION_LISTING_PIN[r]):
                raise ValueError(f"{r}: effective floor {table[r]['floor']} "
                                 f"is not max(majority, 1/n_options)")
        elif table[r]["floor"] != c:
            raise ValueError(f"{r}: effective floor {table[r]['floor']} != "
                             f"majority {c}")
        if r in DOC_FLOORS or r in DOC_FLOOR_SLIPS:
            want = DOC_FLOORS.get(r, DOC_FLOOR_SLIPS.get(r))
            if round(c, 3) != want:
                raise ValueError(f"{r}: computed floor {c} rounds to "
                                 f"{round(c, 3)}, doc §4 prints "
                                 f"{want}")
        elif c > DOC_FLOOR_CAP_REST + 1e-12:
            raise ValueError(f"{r}: computed floor {c} exceeds the doc's "
                             f"'≤ .010' for the unlisted rungs")


if __name__ == "__main__":
    print(json.dumps(check_order_against_2c()))
    t = floor_table()
    check_floors_against_doc(t)
    for r in RUNGS:
        print(f"{r:16s} {FAMILY_OF[r]:15s} {ANSWER_TYPE_PIN[r]:6s} "
              f"tok {max_new_tokens(r):2d}  floor {t[r]['floor']:.3f} "
              f"[{t[r]['floor_rule']}]  "
              f"|A| {t[r]['n_distinct_answers']:3d}  "
              f"majority {t[r]['majority_answer']!r}")
