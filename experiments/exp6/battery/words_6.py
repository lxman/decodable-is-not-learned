# experiments/exp6/battery/words_6.py
"""The vendored word table (built once by make_data_6.py) and the
vocabularies the word rungs draw from. Pure: no network, no eng_to_ipa.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
WORDS_PATH = DATA / "words_6.tsv"
WORDS_6_SHA256 = "1e19db04ee3a413f00aa59676a4a9a2b1a359c39f7b2347ce067059d8247d2a0"
TOP_V10 = 10_000          # BIG-bench's unscrambling range
STRESS = "ˈˌ"


@lru_cache(maxsize=1)
def load_words() -> tuple:
    """Rows (rank, word, count, ipa) in rank order, sha-checked."""
    raw = WORDS_PATH.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != WORDS_6_SHA256:
        raise ValueError(f"{WORDS_PATH} hashes to {got}, pinned {WORDS_6_SHA256}")
    lines = raw.decode("utf-8").splitlines()
    if lines[0] != "rank\tword\tcount\tipa":
        raise ValueError(f"unexpected header {lines[0]!r}")
    rows = []
    for ln in lines[1:]:
        rank, word, count, ipa = ln.split("\t")
        rows.append((int(rank), word, int(count), ipa))
    if [r[0] for r in rows] != sorted(r[0] for r in rows):
        raise ValueError("words_6.tsv is not in rank order")
    if len({r[1] for r in rows}) != len(rows):
        raise ValueError("words_6.tsv repeats a word")
    return tuple(rows)


def signature(word: str) -> str:
    return "".join(sorted(word))


def ipa_len(ipa: str) -> int:
    """Characters of the transcription, stress marks excluded."""
    return sum(1 for c in ipa if c not in STRESS)


@lru_cache(maxsize=1)
def vocab() -> dict:
    rows = load_words()
    sig = Counter(signature(w) for _, w, _, _ in rows)
    v10 = [r for r in rows if r[0] <= TOP_V10]
    return {
        "rows": rows,
        "rank": {w: rk for rk, w, _, _ in rows},
        "v10": tuple(w for _, w, _, _ in v10),
        # a word whose letters spell no other word of the table
        "unique_anagram": tuple(w for _, w, _, _ in v10
                                if sig[signature(w)] == 1 and len(set(w)) > 1),
        "ipa": {w: ipa for _, w, _, ipa in v10 if ipa},
    }


def by_length(words, lo: int, hi: int) -> dict:
    out = {}
    for w in words:
        if lo <= len(w) <= hi:
            out.setdefault(len(w), []).append(w)
    return out
