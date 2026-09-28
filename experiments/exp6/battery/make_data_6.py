# experiments/exp6/battery/make_data_6.py
"""Exp 6 battery data, built ONCE and vendored (design §3.1).

Inputs (both pinned):
  - Norvig's `count_1w.txt` (the Trillion Word Corpus unigram counts that
    BIG-bench's word_unscrambling README names), sha256 COUNT_1W_SHA256;
  - eng_to_ipa 0.0.2 (the CMUdict wrapper BIG-bench's IPA task names).

Output: `data/words_6.tsv`, one row per kept unigram among the first
TOP_N lines of count_1w.txt: rank, word, count, ipa. `ipa` is the
word's IPA transcription when CMUdict gives EXACTLY one pronunciation,
else the empty string. A row is kept iff the word is lowercase a-z
only, at least 3 letters, and in CMUdict.

The generators read ONLY words_6.tsv (sha-pinned in words_6.py); this
module is never imported by them.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
OUT = DATA / "words_6.tsv"
COUNT_1W_URL = "https://www.norvig.com/ngrams/count_1w.txt"
COUNT_1W_SHA256 = ("51df159fd3de12b20e403c108f526e96dbd723d9cabdd5f17955cdc16059e690")
ENG_TO_IPA_VERSION = "0.0.2"
TOP_N = 25_000
_ALPHA = re.compile(r"[a-z]{3,}")


def build(count_1w: Path, out: Path = OUT) -> dict:
    raw = Path(count_1w).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != COUNT_1W_SHA256:
        raise ValueError(f"{count_1w} hashes to {got}, pinned {COUNT_1W_SHA256}")
    import eng_to_ipa as ipa
    from importlib.metadata import version
    if version("eng_to_ipa") != ENG_TO_IPA_VERSION:
        raise RuntimeError(f"eng_to_ipa {version('eng_to_ipa')} installed, "
                           f"pinned {ENG_TO_IPA_VERSION}")
    rows = []
    for rank, line in enumerate(raw.decode("utf-8").splitlines()[:TOP_N], start=1):
        word, count = line.split("\t")
        if not _ALPHA.fullmatch(word):
            continue
        if not ipa.isin_cmu(word):
            continue
        alts = ipa.ipa_list(word)
        one = alts[0][0] if len(alts) == 1 and len(alts[0]) == 1 else ""
        if one.endswith("*") or any(c.isspace() for c in one):
            one = ""
        rows.append(f"{rank}\t{word}\t{int(count)}\t{one}")
    text = "rank\tword\tcount\tipa\n" + "\n".join(rows) + "\n"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(text, encoding="utf-8")
    return {"n_rows": len(rows), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "path": str(out)}


if __name__ == "__main__":
    print(build(Path(sys.argv[1])))
