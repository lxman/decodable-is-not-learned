# experiments/exp6/battery/gen_words.py
"""Word rungs: unscramble_short/long, sort3/sort5, ipa_word
(BIG-bench word_unscrambling, word_sorting, international_phonetic_
alphabet_transliterate; Wei et al. 2022 class E.2)."""
from __future__ import annotations

from . import words_6 as w6
from .spec import RungSpec, register

UNSCRAMBLE_LENGTHS = {"unscramble_short": (4, 5), "unscramble_long": (6, 7, 8)}
SORT_WORD_LEN = (3, 10)
SORT_CLASSES = (0, 1, 2)          # longest shared prefix between neighbours
IPA_BINS = ((1, 4), (5, 6), (7, 99))   # ipa_len bins, slot-cycled
IPA_WORD_LEN = (3, 10)
UNSCRAMBLE_STEM = "The word {s} is a scrambled version of the English word"
SORT_HEADER = "Sort the following words alphabetically: "
IPA_HEADER = ("Transliterate the following word into the International "
              "Phonetic Alphabet (IPA): ")


def unscramble_key(scrambled: str) -> str:
    """BIG-bench's input ends in a space; the question drops it."""
    return UNSCRAMBLE_STEM.format(s=scrambled) + " "


def sort_key(order) -> str:
    """BIG-bench's word_sorting input is the word list and nothing else."""
    return " ".join(order)


def ipa_key(text: str) -> str:
    """BIG-bench's English-side inputs BEGIN with this prefix and are
    sentences. None is one word, so no BIG-bench string is in this
    rung's support: the key's format is not established by anything and
    the gate cannot fire. The rung's items are fresh by construction,
    not by the gate (disclosed)."""
    return f"English: {text}"


def _pick(rng, seq):
    return seq[int(rng.integers(len(seq)))]


# ------------------------------------------------------------ unscramble
def _draw_unscramble(name):
    lengths = UNSCRAMBLE_LENGTHS[name]

    def draw(rng, ctx, slot):
        n = lengths[slot % len(lengths)]
        pool = ctx["unique_by_len"][n]
        word = _pick(rng, pool)
        perm = rng.permutation(len(word))
        scrambled = "".join(word[int(i)] for i in perm)
        if scrambled == word:
            return None
        return {"question": UNSCRAMBLE_STEM.format(s=scrambled),
                "answer": word,
                "bb_key": unscramble_key(scrambled),
                "meta": {"word": word, "scrambled": scrambled, "length": n,
                         "rank": ctx["rank"][word]}}
    return draw


# ------------------------------------------------------------------ sort
def shared_prefix(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def sort_class(words) -> int:
    s = sorted(words)
    m = max(shared_prefix(a, b) for a, b in zip(s, s[1:]))
    return min(m, 2)


def _draw_sort(n_words):
    def draw(rng, ctx, slot):
        target = SORT_CLASSES[slot % len(SORT_CLASSES)]
        pool = ctx["sort_pool"]
        words = []
        if target > 0:
            # seed a pair sharing the target prefix length, then fill
            first = _pick(rng, pool)
            mates = ctx["sort_by_prefix"][target][first[:target]]
            second = _pick(rng, mates)
            if second == first:
                return None
            words = [first, second]
        while len(words) < n_words:
            w = _pick(rng, pool)
            if w not in words:
                words.append(w)
        if any(a in b or b in a for i, a in enumerate(words)
               for b in words[i + 1:]):
            return None                     # one word a substring of another
        if sort_class(words) != target:
            return None
        order = [words[int(i)] for i in rng.permutation(n_words)]
        if order == sorted(order):
            return None                     # already sorted: copying solves it
        return {"question": SORT_HEADER + sort_key(order),
                "answer": " ".join(sorted(order)),
                "bb_key": sort_key(order),
                "meta": {"words": order, "n_words": n_words,
                         "prefix_class": target}}
    return draw


# ------------------------------------------------------------------- ipa
def _draw_ipa(rng, ctx, slot):
    b = slot % len(IPA_BINS)
    word = _pick(rng, ctx["ipa_by_bin"][b])
    ipa = ctx["ipa"][word]
    return {"question": IPA_HEADER + word,
            "answer": ipa,
            "bb_key": ipa_key(word),
            "meta": {"word": word, "ipa_len": w6.ipa_len(ipa), "ipa_bin": b,
                     "rank": ctx["rank"][word]}}


def context() -> dict:
    """Everything the word rungs draw from, derived from the vendored
    table only. Lists are in rank order, so a seeded draw is stable."""
    v = w6.vocab()
    lo, hi = SORT_WORD_LEN
    sort_pool = [w for w in v["v10"] if lo <= len(w) <= hi]
    by_prefix = {k: {} for k in (1, 2)}
    for w in sort_pool:
        for k in (1, 2):
            by_prefix[k].setdefault(w[:k], []).append(w)
    ilo, ihi = IPA_WORD_LEN
    ipa_words = [w for w in v["v10"] if w in v["ipa"] and ilo <= len(w) <= ihi]
    ipa_by_bin = [[w for w in ipa_words
                   if b_lo <= w6.ipa_len(v["ipa"][w]) <= b_hi]
                  for b_lo, b_hi in IPA_BINS]
    return {"rank": v["rank"], "ipa": v["ipa"],
            "unique_by_len": w6.by_length(v["unique_anagram"], 4, 8),
            "sort_pool": sort_pool, "sort_by_prefix": by_prefix,
            "ipa_by_bin": ipa_by_bin}


register(RungSpec(
    name="unscramble_short", task="word_unscrambling", wei_class="E.2",
    rung_type="string", answer_type="word", seed=20260901,
    description="recover a 4-5 letter English word from a random "
                "permutation of its letters; the word is among the 10,000 "
                "most frequent unigrams and no other word of the vendored "
                "table (the a-z words of three letters or more, in CMUdict, "
                "among the 25,000 most frequent) has the same letters",
    unique_answers=True, draw=_draw_unscramble("unscramble_short")))
register(RungSpec(
    name="unscramble_long", task="word_unscrambling", wei_class="E.2",
    rung_type="string", answer_type="word", seed=20260902,
    description="as unscramble_short, 6-8 letter words",
    unique_answers=True, draw=_draw_unscramble("unscramble_long")))
register(RungSpec(
    name="sort3", task="word_sorting", wei_class="E.2",
    rung_type="string", answer_type="sequence", seed=20260903,
    description="sort three English words alphabetically; the list is "
                "never already sorted",
    draw=_draw_sort(3)))
register(RungSpec(
    name="sort5", task="word_sorting", wei_class="E.2",
    rung_type="string", answer_type="sequence", seed=20260904,
    description="sort five English words alphabetically; the list is "
                "never already sorted",
    draw=_draw_sort(5)))
register(RungSpec(
    name="ipa_word", task="international_phonetic_alphabet_transliterate",
    wei_class="E.2", rung_type="string", answer_type="ipa", seed=20260905,
    description="transliterate one English word into IPA (CMUdict via "
                "eng_to_ipa, words with exactly one pronunciation); scored "
                "per word by exact match where BIG-bench scores sentences "
                "by BLEU; no transcription is the answer of two words",
    unique_answers=True, draw=_draw_ipa))
