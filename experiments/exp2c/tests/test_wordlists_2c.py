"""Hygiene tests for the two growth wordlists (ruling 3, 2026-08-01):
ANTONYMS_2C (antonym6's cue/distractor pool) and CATEGORIES_2C (odd6's
category vocab). The proposal's hand-review criteria (§2 b/c) made
programmatic where they can be: length/first-letter balance, no
morphological clustering, and the answer-resembles-cue carrier (leak
class 5/6) excluded at the pair level. Pair- and token-level
disjointness from 2b's frozen ANTONYMS is checked by parsing the frozen
file's TEXT (read-only; no exp2b module import, whose battery packages
fire register() side effects)."""

import re
from pathlib import Path

from experiments.exp2c.battery.wordlists_2c import (
    ANTONYMS_2C, ANTONYMS_2C_ADJ, ANTONYMS_2C_NOUN, CATEGORIES_2C)

_2B_WORDLISTS = (Path(__file__).resolve().parents[2]
                 / "exp2b" / "battery" / "wordlists.py")


def _levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _shared_prefix(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def _parse_2b_antonyms() -> list:
    text = _2B_WORDLISTS.read_text()
    block = re.search(r"^ANTONYMS = \[(.*?)^\]", text,
                      re.DOTALL | re.MULTILINE).group(1)
    pairs = re.findall(r'\("([a-z]+)", "([a-z]+)"\)', block)
    assert len(pairs) > 100, "2b ANTONYMS parse failed (block too small)"
    return pairs


# ------------------------------------------------------------- ANTONYMS_2C

def test_antonyms_2c_floors():
    # ruling 3 floor: >= ~90 pairs (antonym6's basis needs >=15 held cues
    # at holdout 0.2 plus >=300 val items). POS sublists each carry >=60
    # pairs so distractor draws can stay within the cue's own POS without
    # starving (5 distractors need only a handful; 60 pairs = 120 words).
    assert len(ANTONYMS_2C) >= 90
    assert len(ANTONYMS_2C_ADJ) >= 60
    assert len(ANTONYMS_2C_NOUN) >= 60
    assert ANTONYMS_2C == ANTONYMS_2C_ADJ + ANTONYMS_2C_NOUN


def test_antonyms_2c_word_hygiene():
    words = [w for p in ANTONYMS_2C for w in p]
    assert all(w.isalpha() and w.islower() for w in words)
    # every token unique across the whole pool (stronger than 2b, which
    # repeated e.g. "sweet"/"gradual"): no word serves two pairs, so a
    # cue's excluded-word set never silently shrinks the distractor pool
    assert len(set(words)) == len(words)
    assert len({frozenset(p) for p in ANTONYMS_2C}) == len(ANTONYMS_2C)


def test_antonyms_2c_no_cue_resemblance_carrier():
    # proposal §2(b): position leaks if the answer is surface-
    # distinguishable from distractors, e.g. "sharing more letters with
    # the cue". Excluded at the pair level: no containment (sane/insane),
    # no shared prefix or suffix >= 3 (import/export, morning/evening),
    # no edit distance < 3 (east/west).
    for cue, ans in ANTONYMS_2C:
        assert cue not in ans and ans not in cue, (cue, ans)
        assert _shared_prefix(cue, ans) < 3, (cue, ans)
        assert _shared_prefix(cue[::-1], ans[::-1]) < 3, (cue, ans)
        assert _levenshtein(cue, ans) >= 3, (cue, ans)


def test_antonyms_2c_length_first_letter_balance():
    # §2(b) hand-review criteria, programmatic side: no pair with a
    # length gap a "pick the long/short one" heuristic could ride
    # (<= 4), answer lengths centered on the pool's own distribution,
    # and both cue and answer first letters spread wide.
    for cue, ans in ANTONYMS_2C:
        assert abs(len(cue) - len(ans)) <= 4, (cue, ans)
    words = [w for p in ANTONYMS_2C for w in p]
    answers = [a for _, a in ANTONYMS_2C]
    pool_mean = sum(map(len, words)) / len(words)
    ans_mean = sum(map(len, answers)) / len(answers)
    assert abs(ans_mean - pool_mean) <= 1.0
    assert len({c[0] for c, _ in ANTONYMS_2C}) >= 15
    assert len({a[0] for _, a in ANTONYMS_2C}) >= 15


def test_antonyms_2c_disjoint_from_2b_frozen():
    # 2c-owned (ruling 3): no pair shared with 2b's frozen ANTONYMS in
    # either order, and no shared token at all -- stronger than the
    # ownership rule needs, so the antonym family's two rungs (reused
    # antonym + antonym6) share zero cue/answer vocabulary and the
    # family-honest correlation cannot ride shared word idiosyncrasies.
    pairs_2b = _parse_2b_antonyms()
    set_2b = {frozenset(p) for p in pairs_2b}
    words_2b = {w for p in pairs_2b for w in p}
    for p in ANTONYMS_2C:
        assert frozenset(p) not in set_2b, p
    overlap = {w for p in ANTONYMS_2C for w in p} & words_2b
    assert overlap == set(), overlap


# ----------------------------------------------------------- CATEGORIES_2C

def test_categories_2c_floors():
    # ruling 3: >= ~8 categories x >= 6 members (odd6 draws 5 + 1)
    assert len(CATEGORIES_2C) >= 8
    for cat, members in CATEGORIES_2C.items():
        assert len(members) >= 6, cat


def test_categories_2c_exactly_eight_members():
    # Wave-2 review M1 (2026-08-02): the committed odd6 generator draws
    # the odd word with rng.integers(8) -- a hardcoded dependency on
    # every category having EXACTLY 8 members (a 7-member category would
    # raise IndexError at generation; a 9-member one would silently make
    # the ninth word unreachable as the odd word). The committed items
    # were generated under this invariant; pin it so any future vocab
    # scrub that breaks it fails loudly here instead of silently
    # shifting the generator's reachable space.
    for cat, members in CATEGORIES_2C.items():
        assert len(members) == 8, cat


def test_categories_2c_word_hygiene():
    all_words = [w for ms in CATEGORIES_2C.values() for w in ms]
    assert all(w.isalpha() and w.islower() for w in all_words)
    # no word in two categories: _CAT_OF-style membership lookup must be
    # single-valued or the odd-one-out oracle is ill-defined
    assert len(set(all_words)) == len(all_words)


def test_categories_2c_no_morphological_clustering():
    # §2(c): categories must be semantically but NOT morphologically
    # clustered -- a category whose members share a visible fragment the
    # odd word lacks turns the position label surface-legible (leak
    # class 5/6). Rule: within a category, no prefix or suffix of length
    # >= 3 shared by >= 3 members.
    for cat, members in CATEGORIES_2C.items():
        for gram_of in (lambda w: w[:3], lambda w: w[-3:]):
            counts = {}
            for w in members:
                if len(w) >= 3:
                    g = gram_of(w)
                    counts[g] = counts.get(g, 0) + 1
            bad = {g: n for g, n in counts.items() if n >= 3}
            assert not bad, (cat, bad)


def test_categories_2c_length_and_letter_balance():
    # §2(c): no category systematically longer (length-magnitude proxy)
    # or letter-narrow. Mean member length within a common band and >= 5
    # distinct first letters per category.
    for cat, members in CATEGORIES_2C.items():
        mean_len = sum(map(len, members)) / len(members)
        assert 4.0 <= mean_len <= 6.0, (cat, mean_len)
        assert len({w[0] for w in members}) >= 5, cat
