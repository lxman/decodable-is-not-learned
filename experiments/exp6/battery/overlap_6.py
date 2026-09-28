# experiments/exp6/battery/overlap_6.py
"""What the collision gate does NOT establish, counted (run once; the
record is committed and its sha pinned).

The gate is string-level: no item's key is one of BIG-bench's strings.
An item can be a new string and still share CONTENT with BIG-bench — the
word to be unscrambled, the word to be sorted or transliterated, a pair
on a worked line. This tool reads BIG-bench's task files (the index
builder's scratch directory; never committed) beside the committed item
files and counts that overlap, per rung. It excludes nothing and gates
nothing: the counts are a disclosure, and the record is what the
disclosure is read from.

Where the content is a draw from a frame (logical deduction, geometric
shapes, temporal sequences, unit interpretation, ASCII art by target)
the key is the content and the gate is the whole statement; those rungs
carry no row here.

    PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python \\
        -m experiments.exp6.battery.overlap_6 <scratch dir> [--write]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from experiments.exp6 import battery_6 as b6

from . import collisions_6 as c6
from .make_bigbench_index_6 import COMMUTES, local_name

HERE = Path(__file__).resolve().parent
RECORD = HERE / "data" / "overlap_6.json"
OVERLAP_6_SHA256 = "f8861fd0fbfcee85b1add8f04e04e7c9e323326e76e9c9e60e04772e2f299078"
MODARITH_FILE = {
    "modarith_add1": "modified_arithmetic/three_digit_addition_plus_one",
    "modarith_sub1": "modified_arithmetic/three_digit_subtraction_plus_one",
    "modarith_mul1": "modified_arithmetic/two_digit_multiplication_plus_one",
}
IPA_FILE = "international_phonetic_alphabet_transliterate"
PUNCTUATION = ".,;:!?\"'()[]"
RUNGS = ("modarith_add1", "modarith_sub1", "modarith_mul1", "unscramble_short",
         "unscramble_long", "ipa_word", "sort3", "sort5", "lcs")


def _examples(src: Path, task: str, path: str) -> list:
    raw = (Path(src) / local_name(path)).read_bytes()
    if hashlib.sha256(raw).hexdigest() != c6.load_index()["tasks"][task]["files"][path]:
        raise ValueError(f"{path}: not the file the index was built from")
    return json.loads(raw)["examples"]


def _targets(ex: dict) -> list:
    t = ex["target"]
    return list(t) if isinstance(t, list) else [t]


def _pair(line: str) -> str:
    return line.split(" ->")[0]


def _either(pair: str) -> set:
    """The pair, and the pair the other way round where it commutes."""
    a, sym, b = pair.split(" ")
    return {pair, f"{b} {sym} {a}"} if sym in COMMUTES else {pair}


MARKS = ("English:", "IPA:")


def ipa_sides(example: dict) -> dict:
    """The English text and the IPA text of one BIG-bench example. The
    file has two shapes: the input holds one side and ends in the other
    side's marker, the target following bare; or input and target each
    open with their own marker. Input and target are read as one string
    and cut at the markers. An example that does not show both markers
    is refused."""
    target = example["target"]
    target = " ".join(target) if isinstance(target, list) else str(target)
    text = str(example["input"]) + " " + target
    cuts = sorted((m.start(), m.group(0)) for m in re.finditer("|".join(MARKS), text))
    if sorted(m for _, m in cuts) != sorted(MARKS) or cuts[0][0] != 0:
        raise ValueError(f"an example that is not one English and one IPA side: "
                         f"{text[:60]!r}")
    out = {}
    for i, (at, m) in enumerate(cuts):
        end = cuts[i + 1][0] if i + 1 < len(cuts) else len(text)
        out[m] = text[at + len(m):end].strip()
    return {"english": out["English:"], "ipa": out["IPA:"]}


def overlap(src: Path, battery: dict | None = None) -> dict:
    battery = battery or b6.load_battery_6(RUNGS)
    rows = {}
    for rung, path in MODARITH_FILE.items():
        asked, printed = set(), set()
        for ex in _examples(src, "modified_arithmetic", path):
            lines = ex["input"].split("\n")[1:]
            asked.add(_pair(lines[-1]))
            printed.update(_pair(line) for line in lines)
        n = {"asks a pair BIG-bench asks": 0,
             "asks a pair BIG-bench prints on any line": 0,
             "asks a pair BIG-bench prints, in either order": 0,
             "shows a worked pair BIG-bench prints on any line": 0,
             "shows a worked pair BIG-bench prints, in either order": 0}
        for it in battery[rung]["eval_items"]:
            lines = it["question"].split("\n")[1:]
            n["asks a pair BIG-bench asks"] += _pair(lines[-1]) in asked
            n["asks a pair BIG-bench prints on any line"] += _pair(lines[-1]) in printed
            n["asks a pair BIG-bench prints, in either order"] += bool(
                _either(_pair(lines[-1])) & printed)
            n["shows a worked pair BIG-bench prints on any line"] += any(
                _pair(line) in printed for line in lines[:-1])
            n["shows a worked pair BIG-bench prints, in either order"] += any(
                _either(_pair(line)) & printed for line in lines[:-1])
        rows[rung] = {"bigbench": {"pairs asked": len(asked),
                                   "pairs printed": len(printed)}, "items": n}
    words = {t for ex in _examples(src, "word_unscrambling", "word_unscrambling")
             for t in _targets(ex)}
    for rung in ("unscramble_short", "unscramble_long"):
        rows[rung] = {"bigbench": {"distinct target words": len(words)}, "items": {
            "the answer is a BIG-bench target word": sum(
                it["answer"] in words for it in battery[rung]["eval_items"])}}
    english, tokens = set(), set()
    for ex in _examples(src, IPA_FILE, IPA_FILE):
        side = ipa_sides(ex)
        english.update(re.findall(r"[a-z]+", side["english"].lower()))
        tokens.update(t.strip(PUNCTUATION) for t in side["ipa"].split())
    tokens.discard("")
    items = battery["ipa_word"]["eval_items"]
    rows["ipa_word"] = {
        "bigbench": {"words of its English sentences": len(english),
                     "tokens of its IPA text": len(tokens)},
        "items": {"the word occurs in a BIG-bench sentence": sum(
                      it["meta"]["word"] in english for it in items),
                  "the answer is a token of BIG-bench's IPA text": sum(
                      it["answer"] in tokens for it in items)}}
    listed = {w for ex in _examples(src, "word_sorting", "word_sorting")
              for w in ex["input"].split()}
    for rung in ("sort3", "sort5"):
        items = battery[rung]["eval_items"]
        rows[rung] = {"bigbench": {"words of its lists": len(listed)}, "items": {
            "a word of the list is in a BIG-bench list": sum(
                any(w in listed for w in it["meta"]["words"]) for it in items),
            "every word of the list is in a BIG-bench list": sum(
                all(w in listed for w in it["meta"]["words"]) for it in items)}}
    strings = {s for ex in _examples(src, "cs_algorithms", "cs_algorithms/lcs")
               for s in ex["input"].split()}
    rows["lcs"] = {"bigbench": {"strings": len(strings)}, "items": {
        "one of the two strings is a BIG-bench string": sum(
            it["meta"]["a"] in strings or it["meta"]["b"] in strings
            for it in battery["lcs"]["eval_items"])}}
    return {"bigbench_commit": c6.BIGBENCH_COMMIT, "index_sha256": c6.INDEX_6_SHA256,
            "items_sha256": {r: battery[r]["items_sha256"] for r in RUNGS},
            "n_items": b6.N_ITEMS, "rungs": rows}


def dumps(rec: dict) -> str:
    return json.dumps(rec, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def load_record() -> dict:
    """The committed record, refused unless it is the pinned one and is
    of the index and the item files now pinned."""
    raw = RECORD.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != OVERLAP_6_SHA256:
        raise ValueError(f"{RECORD} hashes to {got}, pinned {OVERLAP_6_SHA256}")
    rec = json.loads(raw)
    if rec["index_sha256"] != c6.INDEX_6_SHA256:
        raise ValueError("the overlap record is of another index")
    now = {r: b6.ITEMS_SHA_PIN_6[r] for r in RUNGS}
    if rec["items_sha256"] != now:
        moved = sorted(r for r in now if rec["items_sha256"].get(r) != now[r])
        raise ValueError(f"the overlap record is of other items: {moved} changed "
                         f"since it was counted; re-run it")
    return rec


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    write = "--write" in argv
    src = [a for a in argv if a != "--write"]
    if len(src) != 1:
        raise SystemExit(__doc__)
    rec = overlap(Path(src[0]))
    text = dumps(rec)
    for rung, row in rec["rungs"].items():
        for what, n in row["items"].items():
            print(f"{rung:18s} {n:4d} of {rec['n_items']}  {what}")
    print("record sha256", hashlib.sha256(text.encode("utf-8")).hexdigest())
    if write:
        RECORD.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
