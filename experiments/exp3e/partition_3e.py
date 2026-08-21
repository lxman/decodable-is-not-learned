"""The frozen partition (design §5.1; doc Open item 1) — a total,
model-free function of the input string, committed with its printed
classification BEFORE any new draw.

For an input x (the string the prompt asks to reverse) with reverse a:
  N(x) = { one transposition of two UNEQUAL characters } ∪ { rotate
          left by one, rotate right by one } minus { x }.
  reachable  ⇔  a ∈ N(x).
  M(x) = { s ∈ N(x) minus {a} : s[0] = a[0] and ov(s, x) ≥ ov(a, x) } —
         the one-edit outputs that begin with the reverse's first
         character and are at least as copy-like (§5.1's overlap
         clause). Defined for every item, reachable or not: for a
         non-reachable item a ∉ N(x), so N(x) minus {a} = N(x), which is
         the §5.5 S2 set ('abcd' → {'dabc', 'dbca'}).

The two rejected variants — (i) adjacent transpositions only, (ii)
rotations only — are computed and PRINTED beside the frozen
classification (§5.1: "so the choice is visible"); nothing downstream
reads them. No builder discretion remains: every function here is a
pure map from strings to strings, and the committed partition record
is re-derived from the item file and compared at every load.

The 45-item subset = every len-4 eval item whose answer carries a
repeated character. A palindromic input would make "reverse" equal
"copy" and is refused at build (§3); the committed battery has none.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path

VARIANTS = ("frozen", "adjacent", "rotations")
SUBSET_LENGTH = 4


# ------------------------------------------------------ string algebra

def rotate_left(x: str) -> str:
    return x[1:] + x[0]


def rotate_right(x: str) -> str:
    return x[-1] + x[:-1]


def transpositions(x: str, *, adjacent_only: bool = False) -> dict:
    """{string: (i, j)} for every transposition of two UNEQUAL
    characters (so no entry equals x). Where two position pairs yield
    the same string the lexically first pair is kept — impossible for
    the single-repeat len-4 inputs this design runs on, recorded for
    totality."""
    out: dict[str, tuple] = {}
    L = len(x)
    for i in range(L):
        for j in range(i + 1, L):
            if adjacent_only and j != i + 1:
                continue
            if x[i] == x[j]:
                continue
            s = list(x)
            s[i], s[j] = s[j], s[i]
            out.setdefault("".join(s), (i, j))
    return out


def neighbours(x: str, variant: str = "frozen") -> set:
    """N(x) under the frozen definition or one of the two printed
    variants."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown neighbour-set variant {variant!r}; "
                         f"the frozen choices are {VARIANTS}")
    out: set[str] = set()
    if variant != "rotations":
        out |= set(transpositions(
            x, adjacent_only=(variant == "adjacent")))
    out.add(rotate_left(x))
    out.add(rotate_right(x))
    out.discard(x)
    return out


def overlap(s: str, x: str) -> int:
    """ov(s, x): positions at which the two strings agree."""
    return sum(1 for p, q in zip(s, x) if p == q)


def reach(x: str, variant: str = "frozen") -> dict:
    """Reachability of a = rev(x) from x under one copy edit, with the
    edit named: mechanism 'transposition' (edit = (i, j)) or
    'rotation' (edit = 'left'/'right'); None when a ∉ N(x)."""
    a = x[::-1]
    n = neighbours(x, variant)
    if a not in n:
        return {"reachable": False, "mechanism": None, "edit": None}
    if variant != "rotations":
        tr = transpositions(x, adjacent_only=(variant == "adjacent"))
        if a in tr:
            return {"reachable": True, "mechanism": "transposition",
                    "edit": tr[a]}
    if a == rotate_right(x):
        return {"reachable": True, "mechanism": "rotation",
                "edit": "right"}
    if a == rotate_left(x):
        return {"reachable": True, "mechanism": "rotation",
                "edit": "left"}
    raise AssertionError(f"{a!r} in N({x!r}) by no named edit")


def repeat_pattern(s: str):
    """The (i, j) positions of the one repeated character; None for an
    all-distinct string; refuses anything with more than one repeated
    pair (the battery has none; the §3 claim is asserted, not
    assumed)."""
    pairs = [(i, j) for i in range(len(s)) for j in range(i + 1, len(s))
             if s[i] == s[j]]
    if not pairs:
        return None
    if len(pairs) != 1:
        raise ValueError(f"{s!r} carries {len(pairs)} equal-character "
                         f"pairs; the repeat class is defined for "
                         f"exactly one")
    return pairs[0]


def matched_competitors(x: str) -> list:
    """M(x), sorted: first-character-matched, overlap-at-least-the-
    reverse's one-edit outputs, the reverse itself excluded."""
    a = x[::-1]
    ov_a = overlap(a, x)
    return sorted(s for s in neighbours(x)
                  if s != a and s[0] == a[0] and overlap(s, x) >= ov_a)


def unigram_bits(s: str) -> float:
    """3d's C1 (unigram entropy × length, bits), canonical summation
    order — the entropy both classes share (6.0 for one repeat at
    len 4, 8.0 for all-distinct)."""
    L = len(s)
    counts = Counter(s)
    h1 = -sum((n / L) * math.log2(n / L) for n in sorted(counts.values()))
    return float(L * h1)


# --------------------------------------------------- the subset + record

def repeat_class_len4(answers) -> list:
    """Indices of the len-4 answers with a repeated character, in item
    order — the 3d freeze record's 'repeat class' (§3)."""
    return [i for i, a in enumerate(answers)
            if len(a) == SUBSET_LENGTH and len(set(a)) < SUBSET_LENGTH]


def build_partition(answers) -> dict:
    """The complete printed classification of the subset (§5.1):
    per item its input, answer, repeat pattern, N(x), reachability
    with the named edit, sub-class, M(x), entropy, and the two variant
    reachabilities; plus the class lists and the variant class lists."""
    items = repeat_class_len4(answers)
    entries = []
    for i in items:
        a = str(answers[i])
        x = a[::-1]
        if x == a:
            raise ValueError(
                f"item {i} {a!r} is a palindrome — its reverse is its "
                f"copy and it cannot sit in a reversal partition (§3)")
        pat = repeat_pattern(x)     # stated on the INPUT (§1/§3 tables)
        r = reach(x)
        entry = {
            "item": i, "input": x, "answer": a,
            "repeat_pattern": list(pat),
            "neighbours": sorted(neighbours(x)),
            "reachable": r["reachable"],
            "mechanism": r["mechanism"],
            "edit": (list(r["edit"]) if isinstance(r["edit"], tuple)
                     else r["edit"]),
            "sub_class": (r["mechanism"] if r["reachable"]
                          else "non_reachable"),
            "matched_competitors": matched_competitors(x),
            "overlap_reverse": overlap(a, x),
            "entropy_bits": unigram_bits(a),
            "variants": {v: reach(x, v)["reachable"]
                         for v in VARIANTS if v != "frozen"},
        }
        entries.append(entry)
    out = {
        "definition": {
            "neighbour_set": "all single transpositions of two unequal "
                             "characters ∪ {rotate left by one, rotate "
                             "right by one} \\ {x}",
            "reachable": "reverse(x) ∈ N(x)",
            "matched_competitors": "s ∈ N(x) \\ {reverse}: s[0] == "
                                   "reverse[0] and overlap(s, x) ≥ "
                                   "overlap(reverse, x)",
            "subset": "len-4 eval items whose answer has a repeated "
                      "character",
        },
        "n_items": len(items),
        "items": items,
        "entries": entries,
        "reachable": [e["item"] for e in entries if e["reachable"]],
        "non_reachable": [e["item"] for e in entries
                          if not e["reachable"]],
        "sub_classes": {
            "transposition": [e["item"] for e in entries
                              if e["sub_class"] == "transposition"],
            "rotation": [e["item"] for e in entries
                         if e["sub_class"] == "rotation"],
            "non_reachable": [e["item"] for e in entries
                              if e["sub_class"] == "non_reachable"],
        },
        "pattern_counts": {
            f"{e['repeat_pattern'][0]},{e['repeat_pattern'][1]}": 0
            for e in entries},
        "arm_items": [e["item"] for e in entries
                      if e["reachable"] and e["matched_competitors"]],
        "arm_sit_out": [e["item"] for e in entries
                        if e["reachable"] and not e["matched_competitors"]],
        "variants": {
            v: {"reachable": [e["item"] for e in entries
                              if e["variants"][v]],
                "non_reachable": [e["item"] for e in entries
                                  if not e["variants"][v]],
                "note": {"adjacent": "variant (i): adjacent "
                                     "transpositions only — rejected "
                                     "(§5.1); printed so the choice is "
                                     "visible",
                         "rotations": "variant (ii): rotations only — "
                                      "rejected (§5.1); printed so the "
                                      "choice is visible"}[v]}
            for v in VARIANTS if v != "frozen"},
    }
    for e in entries:
        k = f"{e['repeat_pattern'][0]},{e['repeat_pattern'][1]}"
        out["pattern_counts"][k] += 1
    return out


def canonical_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode()


def partition_sha256(partition: dict) -> str:
    return hashlib.sha256(canonical_bytes(partition)).hexdigest()


def dump_partition(answers, path) -> dict:
    p = build_partition(answers)
    p = {**p, "sha256_of_partition": partition_sha256(p)}
    Path(path).write_text(json.dumps(p, indent=1, ensure_ascii=False))
    return p


def check_partition(answers, path) -> dict:
    """Load the committed partition record and REFUSE unless it is
    exactly the frozen functions' output on the given answers (3a's
    class: a record that does not reproduce has no value)."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"no committed partition record at {path} — the 32/13 "
            f"split has no value (3a's class, refused)")
    rec = json.loads(path.read_text())
    want = build_partition(answers)
    got = {k: v for k, v in rec.items() if k != "sha256_of_partition"}
    if got != want:
        raise ValueError(
            f"committed partition record {path} is not the frozen "
            f"partition recomputed from the answers — the record does "
            f"not reproduce (3a's class, refused)")
    if rec.get("sha256_of_partition") != partition_sha256(want):
        raise ValueError(
            f"committed partition record {path} carries a "
            f"self-sha that does not match its own contents")
    return want
