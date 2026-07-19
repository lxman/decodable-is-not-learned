"""Exp 2b capability specs — tranche 2: word, semantic-choice, and relational
families (design table #12–#15, #18–#25, #27–#29). Imported by generators.py,
which extends SPECS in place; per-spec seeds derive from position in the FULL
list, so the two-tranche split has no effect on item streams.

Format revisions applied here (doc §2 second revision note, 2026-07-19,
mechanism-argued under Michael's standing acceptance):
- #20/#21/#22/#25 become 4-CHOICE questions: hand-authorable ground-truth lists
  (~100–240 cues) cannot reach 2500 unique single-cue questions; combinatorial
  option sets can. The starved basis stays the cue (or answer word for #20) —
  the association a lookup would need.
- #18 probe target becomes count PARITY: a count is an additive sum over
  per-word membership and fails the additive-threshold rule; parity's mod-2
  wrap does not.
- #27/#28 bases are STRUCTURAL PATTERNS (names randomized independently, so
  name lookup is uninformative); #28 needs 4 entities / 4 transfers because 3
  transfers admit only 8 patterns, under the 15-value holdout minimum.
- Eject candidates kept as specs (#14 alphabet_offset, #23/#24 irregular
  forms): their unique-question spaces are too small at full counts; M0
  records the ejection instead of assuming it.
"""

from __future__ import annotations

import re

from splits import SplitParams

from .base import CapabilitySpec
from .wordlists import (ANTONYMS, CAPITALS, CATEGORIES_2B, IRREGULAR_PAST,
                        IRREGULAR_PLURALS, NAMES_2B, RHYME_FAMILIES, UNIT_PAIRS,
                        WORDS)

# NO import from .generators — one-way dependency only (generators.py imports
# this module at its bottom); a two-way import is order-dependent and fragile.
_LET = "abcdefghijklmnopqrstuvwxyz"

# ---------------------------------------------------------------------- pools

_W56 = sorted({w for w in WORDS if 5 <= len(w) <= 6})

# unscramble answers must be multiset-unique in the pool (well-defined answer)
from collections import Counter as _Counter
_MS = _Counter("".join(sorted(w)) for w in _W56)
UNIQ56 = [w for w in _W56 if _MS["".join(sorted(w))] == 1]

_CAT_WORDS = sorted({w for ws in CATEGORIES_2B.values() for w in ws})
_CAT_OF = {w: c for c, ws in CATEGORIES_2B.items() for w in ws}
_DISTRACTORS = sorted(w for w in _W56 if w not in _CAT_OF)[:200]
_ANT = dict(ANTONYMS)
_ALL_ANT_WORDS = sorted({w for p in ANTONYMS for w in p})
_RHYME_OF = {w: f for f, ws in RHYME_FAMILIES.items() for w in ws}
_RHYME_WORDS = sorted(_RHYME_OF)
_COUNTRIES = sorted(CAPITALS)
_ALL_CAPITALS = sorted(set(CAPITALS.values()))
_UNITS = {(a, b): p for a, b, p in UNIT_PAIRS}


def _shuffle_answer_in(rng, answer, distractors):
    """Place answer among 3 distractors at a uniform position; return (options,
    position 1-4)."""
    opts = list(distractors)
    pos = int(rng.integers(4))
    opts.insert(pos, answer)
    return opts, pos + 1


def _caesar(word, k):
    return "".join(_LET[(_LET.index(c) + k) % 26] for c in word)


# ------------------------------------------------------------- #12: unscramble

# Letter-stratified generation (exp2's ledgered trick, applied at the source):
# draw the first letter uniformly over letters with >= 8 pool words, then the
# word — no rare class ever enters the items, so the stratified split always
# has >= 2 basis values per class to put on both sides.
def _by_first_letter(pool, min_n=8):
    d = {}
    for w in pool:
        d.setdefault(w[0], []).append(w)
    return {k: v for k, v in d.items() if len(v) >= min_n}

_UNSC_BY_LETTER = _by_first_letter(UNIQ56)
_UNSC_LETTERS = sorted(_UNSC_BY_LETTER)
_W56_BY_LETTER = _by_first_letter(_W56)
_W56_LETTERS = sorted(_W56_BY_LETTER)


def _gen_unscramble(rng, split):
    letter = _UNSC_LETTERS[int(rng.integers(len(_UNSC_LETTERS)))]
    pool = _UNSC_BY_LETTER[letter]
    w = pool[int(rng.integers(len(pool)))]
    letters = list(w)
    for _ in range(20):
        rng.shuffle(letters)
        if "".join(letters) != w:
            break
    s = "".join(letters)
    return f"Unscramble the letters '{s}' to form an English word.", w, w[0]


def _oracle_unscramble(q):
    s = re.search(r"'([a-z]+)'", q).group(1)
    key = "".join(sorted(s))
    matches = [w for w in UNIQ56 if "".join(sorted(w)) == key]
    assert len(matches) == 1, (s, matches)
    return matches[0]


def _basis_unscramble(q):
    return (_oracle_unscramble(q),)      # the solution word (multiset-unique)


# ----------------------------------------------------------------- #13: caesar

def _gen_caesar(rng, split):
    # letter-stratified over PLAIN first letters (the decoded class)
    letter = _W56_LETTERS[int(rng.integers(len(_W56_LETTERS)))]
    pool = _W56_BY_LETTER[letter]
    w = pool[int(rng.integers(len(pool)))]
    k = int(rng.integers(1, 6))
    enc = _caesar(w, k)
    return (f"The word '{enc}' was made by shifting each letter of a word "
            f"forward by {k}. What was the original word?", w, w[0])


def _oracle_caesar(q):
    enc = re.search(r"'([a-z]+)'", q).group(1)
    k = int(re.search(r"forward by (\d)", q).group(1))
    return _caesar(enc, 26 - k)


def _basis_caesar(q):
    enc = re.search(r"'([a-z]+)'", q).group(1)
    k = re.search(r"forward by (\d)", q).group(1)
    return (f"{enc[0]}{k}",)             # (first cipher letter, shift) combo


# -------------------------------------------------- #14: alphabet offset (eject)

def _gen_alpha_offset(rng, split):
    c = _LET[int(rng.integers(26))]
    k = int(rng.integers(1, 6))
    return (f"What letter comes {k} letters after '{c}' in the alphabet?",
            _LET[(_LET.index(c) + k) % 26], _LET[(_LET.index(c) + k) % 26])


def _oracle_alpha_offset(q):
    c = re.search(r"'([a-z])'", q).group(1)
    k = int(re.search(r"comes (\d) letters", q).group(1))
    return _LET[(_LET.index(c) + k) % 26]


def _basis_alpha_offset(q):
    c = re.search(r"'([a-z])'", q).group(1)
    k = re.search(r"comes (\d) letters", q).group(1)
    return (f"{c}{k}",)


# ---------------------------------------------------------------- #15: acronym

def _gen_acronym(rng, split):
    # w2 letter-stratified (its first letter is the probe class); w1 uniform
    w1 = _W56[int(rng.integers(len(_W56)))]
    letter = _W56_LETTERS[int(rng.integers(len(_W56_LETTERS)))]
    pool = _W56_BY_LETTER[letter]
    w2 = pool[int(rng.integers(len(pool)))]
    if w1 == w2:
        w1 = _W56[(int(rng.integers(len(_W56))) + 1) % len(_W56)]
    return (f"What are the first letters of '{w1} {w2}'? Answer with the two "
            f"letters together.", w1[0] + w2[0], w2[0])


def _oracle_acronym(q):
    w1, w2 = re.search(r"'([a-z]+) ([a-z]+)'", q).groups()
    return w1[0] + w2[0]


def _basis_acronym_2nd_token(q):
    w2 = re.search(r"'([a-z]+) ([a-z]+)'", q).group(2)
    return (_first_chunk_with_space(w2),)


_TOK = None


def _first_chunk_with_space(w: str) -> str:
    """First BPE token of the word as it appears mid-prompt (leading space),
    per the design's tokenizer-keyed basis rule for #15."""
    global _TOK
    if _TOK is None:
        from models import load_tokenizer
        _TOK = load_tokenizer("410m")
    ids = _TOK(f" {w}", add_special_tokens=False)["input_ids"]
    return _TOK.decode([ids[0]])


# ------------------------------------------------------- #18: category parity

def _gen_cat_parity(rng, split):
    cat = list(CATEGORIES_2B)[int(rng.integers(len(CATEGORIES_2B)))]
    members, others = CATEGORIES_2B[cat], _DISTRACTORS
    words, n_in_first3 = [], 0
    for slot in range(6):
        take_member = rng.random() < 0.5
        pool = members if take_member else others
        w = pool[int(rng.integers(len(pool)))]
        while w in words:
            w = pool[int(rng.integers(len(pool)))]
        words.append(w)
        if slot < 3 and take_member:
            n_in_first3 += 1
    q = (f"In the list: {', '.join(words)} — how many of the first three "
         f"words are {cat}?")
    return q, str(n_in_first3), n_in_first3 % 2


def _oracle_cat_parity(q):
    cat = re.search(r"words are (\w+)\?", q).group(1)
    words = re.search(r"list: ([a-z, ]+) —", q).group(1).split(", ")
    return str(sum(1 for w in words[:3] if w in CATEGORIES_2B[cat]))


def _basis_first3(q):
    words = re.search(r"list: ([a-z, ]+) —", q).group(1).split(", ")
    return tuple(sorted(words[:3]))


# --------------------------------------------------------- #19: odd one out

def _gen_odd_one_out(rng, split):
    cats = list(CATEGORIES_2B)
    c1 = cats[int(rng.integers(len(cats)))]
    c2 = cats[int(rng.integers(len(cats)))]
    while c2 == c1:
        c2 = cats[int(rng.integers(len(cats)))]
    trio = list(rng.choice(CATEGORIES_2B[c1], size=3, replace=False))
    odd = CATEGORIES_2B[c2][int(rng.integers(16))]
    opts, pos = _shuffle_answer_in(rng, odd, trio)
    return (f"Which word is not like the others: {', '.join(opts)}?", odd, pos)


def _oracle_odd_one_out(q):
    words = re.search(r"others: ([a-z, ]+)\?", q).group(1).split(", ")
    cats = [_CAT_OF[w] for w in words]
    return next(w for w, c in zip(words, cats) if cats.count(c) == 1)


def _basis_all4(q):
    words = re.search(r"others: ([a-z, ]+)\?", q).group(1).split(", ")
    return tuple(sorted(words))


# ------------------------------------------------- #20: hypernym (4-choice)

def _gen_hypernym(rng, split):
    cats = list(CATEGORIES_2B)
    c = cats[int(rng.integers(len(cats)))]
    answer = CATEGORIES_2B[c][int(rng.integers(16))]
    distractors = []
    while len(distractors) < 3:
        c2 = cats[int(rng.integers(len(cats)))]
        if c2 == c:
            continue
        w = CATEGORIES_2B[c2][int(rng.integers(16))]
        if w not in distractors:
            distractors.append(w)
    opts, pos = _shuffle_answer_in(rng, answer, distractors)
    kind = c[:-1] if c.endswith("s") else c   # "birds" -> "bird"
    return (f"Which of these is a kind of {kind}: {', '.join(opts)}?",
            answer, pos)


def _oracle_hypernym(q):
    kind = re.search(r"kind of (\w+):", q).group(1)
    cat = kind if kind in CATEGORIES_2B else kind + "s"
    words = re.search(r": ([a-z, ]+)\?", q).group(1).split(", ")
    return next(w for w in words if _CAT_OF.get(w) == cat)


def _basis_hypernym_answer(q):
    return (_oracle_hypernym(q),)        # the answer word's association is the lookup


# -------------------------------------------------- #21: antonym (4-choice)

def _gen_antonym(rng, split):
    cue, ans = ANTONYMS[int(rng.integers(len(ANTONYMS)))]
    distractors = []
    while len(distractors) < 3:
        w = _ALL_ANT_WORDS[int(rng.integers(len(_ALL_ANT_WORDS)))]
        if w not in (cue, ans, _ANT.get(cue, "")) and w not in distractors \
                and _ANT.get(w) != cue:
            distractors.append(w)
    opts, pos = _shuffle_answer_in(rng, ans, distractors)
    return (f"Which of these means the opposite of '{cue}': "
            f"{', '.join(opts)}?", ans, pos)


def _oracle_antonym(q):
    cue = re.search(r"opposite of '(\w+)'", q).group(1)
    words = re.search(r": ([a-z, ]+)\?", q).group(1).split(", ")
    return next(w for w in words if w == _ANT[cue])


def _basis_antonym_cue(q):
    return (re.search(r"opposite of '(\w+)'", q).group(1),)


# ---------------------------------------------------- #22: rhyme (4-choice)

def _gen_rhyme(rng, split):
    cue = _RHYME_WORDS[int(rng.integers(len(_RHYME_WORDS)))]
    fam = _RHYME_OF[cue]
    mates = [w for w in RHYME_FAMILIES[fam] if w != cue]
    ans = mates[int(rng.integers(len(mates)))]
    distractors = []
    while len(distractors) < 3:
        w = _RHYME_WORDS[int(rng.integers(len(_RHYME_WORDS)))]
        if _RHYME_OF[w] != fam and w not in distractors:
            distractors.append(w)
    opts, pos = _shuffle_answer_in(rng, ans, distractors)
    return (f"Which of these rhymes with '{cue}': {', '.join(opts)}?", ans, pos)


def _oracle_rhyme(q):
    cue = re.search(r"rhymes with '(\w+)'", q).group(1)
    words = re.search(r": ([a-z, ]+)\?", q).group(1).split(", ")
    return next(w for w in words if _RHYME_OF[w] == _RHYME_OF[cue])


def _basis_rhyme_cue(q):
    return (re.search(r"rhymes with '(\w+)'", q).group(1),)


# ------------------------------------------- #23/#24: irregular forms (eject)

def _gen_plural(rng, split):
    nouns = sorted(IRREGULAR_PLURALS)
    n = nouns[int(rng.integers(len(nouns)))]
    return f"What is the plural of '{n}'?", IRREGULAR_PLURALS[n], 1


def _oracle_plural(q):
    return IRREGULAR_PLURALS[re.search(r"plural of '(\w+)'", q).group(1)]


def _basis_plural(q):
    return (re.search(r"plural of '(\w+)'", q).group(1),)


def _gen_past(rng, split):
    verbs = sorted(IRREGULAR_PAST)
    v = verbs[int(rng.integers(len(verbs)))]
    return f"What is the past tense of '{v}'?", IRREGULAR_PAST[v], 1


def _oracle_past(q):
    return IRREGULAR_PAST[re.search(r"past tense of '(\w+)'", q).group(1)]


def _basis_past(q):
    return (re.search(r"past tense of '(\w+)'", q).group(1),)


# --------------------------------------------------- #25: capital (4-choice)

def _gen_capital(rng, split):
    country = _COUNTRIES[int(rng.integers(len(_COUNTRIES)))]
    ans = CAPITALS[country]
    distractors = []
    while len(distractors) < 3:
        c = _ALL_CAPITALS[int(rng.integers(len(_ALL_CAPITALS)))]
        if c != ans and c not in distractors:
            distractors.append(c)
    opts, pos = _shuffle_answer_in(rng, ans, distractors)
    return (f"Which of these is the capital of {country}: "
            f"{', '.join(opts)}?", ans, pos)


def _oracle_capital(q):
    country = re.search(r"capital of ([A-Za-z ]+):", q).group(1)
    caps = re.search(r": ([A-Za-z ,-]+)\?", q).group(1).split(", ")
    return next(c for c in caps if c == CAPITALS[country])


def _basis_capital_country(q):
    return (re.search(r"capital of ([A-Za-z ]+):", q).group(1),)


# ------------------------------------------------------------- #27: deduce3

_CMP = [("taller", "shorter"), ("older", "younger"), ("faster", "slower")]


def _gen_deduce3(rng, split):
    names = list(rng.choice(NAMES_2B, size=4, replace=False))
    rel = _CMP[int(rng.integers(3))]
    # chain names[0] > names[1] > names[2] > names[3]; premises shuffled;
    # each premise stated forward ("X taller Y") or reversed ("Y shorter X")
    order = list(rng.permutation(3))
    dirs = [int(rng.integers(2)) for _ in range(3)]
    prems = []
    for slot, i in enumerate(order):
        a, b = names[i], names[i + 1]
        if dirs[slot]:
            prems.append(f"{b.capitalize()} is {rel[1]} than {a.capitalize()}.")
        else:
            prems.append(f"{a.capitalize()} is {rel[0]} than {b.capitalize()}.")
    q = " ".join(prems) + f" Who is the second {rel[0].replace('er', 'est')}?"
    # probe target: mention-order position (1-4) of the chain's 2nd element
    mention = []
    for p in prems:
        for w in re.findall(r"[A-Z][a-z]+", p):
            if w.lower() not in mention:
                mention.append(w.lower())
    label = mention.index(names[1]) + 1
    return q, names[1], label


def _oracle_deduce3(q):
    rel_f = next(f for f, _ in _CMP if re.search(rf"second {f[:-2]}est", q))
    greater = {}
    for a, r, b in re.findall(r"([A-Z][a-z]+) is (\w+) than ([A-Z][a-z]+)", q):
        if r == rel_f:
            greater[a.lower()] = b.lower()
        else:
            greater[b.lower()] = a.lower()
    top = next(n for n in greater if n not in greater.values())
    return greater[top].capitalize()


def _basis_deduce3(q):
    # structural pattern recomputed from text: premise order + directions
    rel_f = next(f for f, _ in _CMP if re.search(rf"second {f[:-2]}est", q))
    rel_r = dict(_CMP)[rel_f]
    triples = re.findall(r"([A-Z][a-z]+) is (\w+) than ([A-Z][a-z]+)", q)
    edges = []
    for a, r, b in triples:
        edges.append((a.lower(), b.lower()) if r == rel_f else (b.lower(), a.lower()))
    chain = {}
    for a, b in edges:
        chain[a] = b
    top = next(n for n in chain if n not in chain.values())
    seq = [top]
    while seq[-1] in chain:
        seq.append(chain[seq[-1]])
    order = [seq.index(e[0]) for e in edges]
    dirs = [0 if t[1] == rel_f else 1 for t in triples]
    return ("".join(map(str, order)) + "".join(map(str, dirs)),)


# -------------------------------------------------------- #28: entity track

_OBJECTS = ["ball", "book", "key", "coin", "pen", "cup", "hat", "map"]


def _gen_entity_track(rng, split):
    names = [n.capitalize() for n in rng.choice(NAMES_2B, size=4, replace=False)]
    obj = _OBJECTS[int(rng.integers(len(_OBJECTS)))]
    holder = 0
    sents = [f"{names[0]} has the {obj}."]
    pattern = []
    holders = [0]
    for _ in range(5):
        nxt = int(rng.integers(4))
        while nxt == holder:
            nxt = int(rng.integers(4))
        sents.append(f"{names[holder]} gives the {obj} to {names[nxt]}.")
        pattern.append(f"{holder}{nxt}")
        holder = nxt
        holders.append(holder)
    q = " ".join(sents) + f" Who has the {obj} now?"
    # probe target: holder after the SECOND transfer, as mention-order index 1-4
    return q, names[holder], holders[2] + 1


def _oracle_entity_track(q):
    obj = re.search(r"has the (\w+)\.", q).group(1)
    holder = re.search(r"([A-Z][a-z]+) has the", q).group(1)
    for giver, receiver in re.findall(r"([A-Z][a-z]+) gives the \w+ to ([A-Z][a-z]+)", q):
        holder = receiver
    return holder


def _basis_entity_track(q):
    names, seen = [], set()
    for w in re.findall(r"[A-Z][a-z]+", q):
        if w not in seen:
            seen.add(w)
            names.append(w)
    first = re.search(r"([A-Z][a-z]+) has the", q).group(1)
    idx = {n: i for i, n in enumerate(names)}
    pattern = []
    for giver, receiver in re.findall(r"([A-Z][a-z]+) gives the \w+ to ([A-Z][a-z]+)", q):
        pattern.append(f"{idx[giver]}{idx[receiver]}")
    return ("".join(pattern),)


# ------------------------------------------------------------- #29: units

def _gen_units(rng, split):
    a, b, p = UNIT_PAIRS[int(rng.integers(len(UNIT_PAIRS)))]
    v = int(rng.integers(2, 1000))
    return f"How many {b} are in {v} {a}?", str(v * 10 ** p), p


def _oracle_units(q):
    b, v, a = re.search(r"How many (\w+) are in (\d+) (\w+)\?", q).groups()
    return str(int(v) * 10 ** _UNITS[(a, b)])


def _basis_units(q):
    b, _, a = re.search(r"How many (\w+) are in (\d+) (\w+)\?", q).groups()
    return (f"{a}>{b}",)


# ----------------------------------------------------------------- T2 SPECS

SPECS_T2 = [
    CapabilitySpec(
        name="unscramble", description="unscramble a 5-6 letter word",
        answer_type="word", probe_label_space="first letter of the solution",
        basis_kind="the solution word (multiset-unique pool)",
        composability="a held-out word is an unseen letter multiset; producing "
                      "its first letter requires actually unscrambling",
        shots=[("Unscramble the letters 'tsnoe' to form an English word.", "stone"),
               ("Unscramble the letters 'pplea' to form an English word.", "apple")],
        gen=_gen_unscramble, oracle=_oracle_unscramble, basis_fn=_basis_unscramble,
        split_params=SplitParams(stratify_by_label=True)),
    CapabilitySpec(
        name="caesar", description="decode a Caesar shift (k stated, 1-5)",
        answer_type="word", probe_label_space="first letter of the decoded word",
        basis_kind="(first cipher letter, shift) combo (~130 values)",
        composability="the class for an unseen (letter, k) combo requires the "
                      "alphabet rotation, not a memorized combo table",
        shots=[("The word 'vwrqh' was made by shifting each letter of a word "
                "forward by 3. What was the original word?", "stone"),
               ("The word 'crrng' was made by shifting each letter of a word "
                "forward by 2. What was the original word?", "apple")],
        gen=_gen_caesar, oracle=_oracle_caesar, basis_fn=_basis_caesar,
        split_params=SplitParams(n_holdout=39, min_holdout_values=26,
                                 stratify_by_label=True)),
    CapabilitySpec(
        name="alpha_offset", description="letter k positions later (EJECT expected: "
                                         "130 unique questions < 2500)",
        answer_type="word", probe_label_space="the result letter",
        basis_kind="(letter, offset) combo (130 values)",
        composability="rotation, as caesar",
        shots=[("What letter comes 3 letters after 'm' in the alphabet?", "p"),
               ("What letter comes 2 letters after 'y' in the alphabet?", "a")],
        gen=_gen_alpha_offset, oracle=_oracle_alpha_offset,
        basis_fn=_basis_alpha_offset,
        split_params=SplitParams(n_holdout=39, min_holdout_values=26)),
    CapabilitySpec(
        name="acronym", description="first letters of two words",
        answer_type="letters", probe_label_space="first letter of the 2nd word",
        basis_kind="2nd word's first BPE token (tokenizer-keyed, leading space)",
        composability="first-letter-of-unseen-token requires linking token to "
                      "spelling — model knowledge, not lookup",
        shots=[("What are the first letters of 'stone apple'? Answer with the "
                "two letters together.", "sa"),
               ("What are the first letters of 'mount bread'? Answer with the "
                "two letters together.", "mb")],
        gen=_gen_acronym, oracle=_oracle_acronym, basis_fn=_basis_acronym_2nd_token,
        split_params=SplitParams(stratify_by_label=True)),
    CapabilitySpec(
        name="cat_parity", description="count category members in first 3 of 6",
        answer_type="number",
        probe_label_space="PARITY of the count (0/1) — the count itself is an "
                          "additive sum and fails the additive-threshold rule",
        basis_kind="the first-3 word set (3 shared components over the "
                   "member+distractor vocab)",
        composability="parity's mod-2 wrap is not expressible by additive "
                      "per-word membership scores",
        shots=[("In the list: apple, chair, plum, stone, rose, wagon — how many "
                "of the first three words are fruits?", "2"),
               ("In the list: hammer, saw, drill, tulip, cod, oak — how many of "
                "the first three words are tools?", "3")],
        gen=_gen_cat_parity, oracle=_oracle_cat_parity, basis_fn=_basis_first3,
        split_params=SplitParams(holdout_frac=0.37, min_val_items=300,
                                 shared_components=True),
        n_probe=8000),
    CapabilitySpec(
        name="odd_one_out", description="which of 4 words is not like the others",
        answer_type="word", probe_label_space="answer position (1-4)",
        basis_kind="all 4 words (shared components over the category vocab)",
        composability="requires comparing category memberships — an "
                      "interaction, not an additive score",
        shots=[("Which word is not like the others: robin, eagle, hammer, "
                "crow?", "hammer"),
               ("Which word is not like the others: oak, tulip, pine, "
                "cedar?", "tulip")],
        gen=_gen_odd_one_out, oracle=_oracle_odd_one_out, basis_fn=_basis_all4,
        split_params=SplitParams(holdout_frac=0.45, min_val_items=300,
                                 shared_components=True),
        n_probe=8000),
    CapabilitySpec(
        name="hypernym", description="which option is a kind of X (4-choice)",
        answer_type="word", probe_label_space="answer position (1-4)",
        basis_kind="the ANSWER word (its category association is the lookup)",
        composability="category of an unseen word is semantic knowledge; "
                      "residual channel (elimination via known distractors) "
                      "noted — the untrained gate measures it empirically",
        shots=[("Which of these is a kind of bird: hammer, robin, oak, "
                "apple?", "robin"),
               ("Which of these is a kind of tool: rose, cod, wrench, "
                "banana?", "wrench")],
        gen=_gen_hypernym, oracle=_oracle_hypernym, basis_fn=_basis_hypernym_answer),
    CapabilitySpec(
        name="antonym", description="which option is the opposite of the cue",
        answer_type="word", probe_label_space="answer position (1-4)",
        basis_kind="the cue word (the cue-answer association is the lookup)",
        composability="the opposite of an unseen cue is semantic knowledge",
        shots=[("Which of these means the opposite of 'hot': cold, big, wet, "
                "old?", "cold"),
               ("Which of these means the opposite of 'full': dark, empty, "
                "slow, poor?", "empty")],
        gen=_gen_antonym, oracle=_oracle_antonym, basis_fn=_basis_antonym_cue,
        split_params=SplitParams(holdout_frac=0.2, min_holdout_values=15,
                                 min_val_items=300)),
    CapabilitySpec(
        name="rhyme", description="which option rhymes with the cue",
        answer_type="word", probe_label_space="answer position (1-4)",
        basis_kind="the cue word (240 values across 30 rhyme families)",
        composability="rhyme for an unseen cue requires orthographic/"
                      "phonological analysis of the cue itself",
        shots=[("Which of these rhymes with 'bake': night, cake, gold, "
                "rain?", "cake"),
               ("Which of these rhymes with 'light': bell, jump, sight, "
                "boat?", "sight")],
        gen=_gen_rhyme, oracle=_oracle_rhyme, basis_fn=_basis_rhyme_cue),
    CapabilitySpec(
        name="plural_irreg", description="irregular plural (EJECT expected: 40 "
                                          "unique cues < 2500)",
        answer_type="word", probe_label_space="(eject candidate)",
        basis_kind="the noun", composability="lexical knowledge",
        shots=[("What is the plural of 'mouse'?", "mice"),
               ("What is the plural of 'leaf'?", "leaves")],
        gen=_gen_plural, oracle=_oracle_plural, basis_fn=_basis_plural),
    CapabilitySpec(
        name="past_irreg", description="irregular past tense (EJECT expected: 60 "
                                        "unique cues < 2500)",
        answer_type="word", probe_label_space="(eject candidate)",
        basis_kind="the verb", composability="lexical knowledge",
        shots=[("What is the past tense of 'go'?", "went"),
               ("What is the past tense of 'eat'?", "ate")],
        gen=_gen_past, oracle=_oracle_past, basis_fn=_basis_past),
    CapabilitySpec(
        name="capital", description="which option is the capital of X (4-choice)",
        answer_type="word", probe_label_space="answer position (1-4)",
        basis_kind="the country (116 values; the country-capital association "
                   "is the lookup)",
        composability="the capital of an unseen country is factual knowledge",
        shots=[("Which of these is the capital of France: Paris, Rome, Oslo, "
                "Cairo?", "Paris"),
               ("Which of these is the capital of Japan: Beijing, Seoul, "
                "Tokyo, Hanoi?", "Tokyo")],
        gen=_gen_capital, oracle=_oracle_capital, basis_fn=_basis_capital_country,
        split_params=SplitParams(holdout_frac=0.2, min_holdout_values=15,
                                 min_val_items=300)),
    CapabilitySpec(
        name="deduce3", description="second element of a 4-chain (shuffled premises)",
        answer_type="word",
        probe_label_space="mention-order position of the chain's 2nd element (1-4)",
        basis_kind="structural pattern: premise order x statement directions "
                   "(48 values); names randomized independently",
        composability="the chain position for an unseen premise-order pattern "
                      "requires assembling the chain, not pattern lookup",
        shots=[("Ann is taller than Ben. Ben is taller than Cal. Cal is taller "
                "than Dan. Who is the second tallest?", "Ben"),
               ("Cal is shorter than Ben. Dan is shorter than Cal. Ann is "
                "taller than Ben. Who is the second tallest?", "Ben")],
        gen=_gen_deduce3, oracle=_oracle_deduce3, basis_fn=_basis_deduce3,
        split_params=SplitParams(n_holdout=15, min_holdout_values=15,
                                 min_val_items=300)),
    CapabilitySpec(
        name="entity_track", description="object location after 5 transfers "
                                          "among 4 people",
        answer_type="word",
        probe_label_space="holder after the SECOND transfer as mention-order "
                          "index (1-4)",
        basis_kind="mention-order transfer pattern. NOTE: mention-order "
                   "canonicalization collapses the raw 3^k count (the first "
                   "transfer is always mention-0 -> mention-1); 4 transfers "
                   "yield only 14 canonical patterns (< the 15-value minimum), "
                   "hence 5 transfers (~41)",
        composability="mid-episode state for an unseen transfer pattern "
                      "requires simulating the episode",
        shots=[("Ann has the ball. Ann gives the ball to Ben. Ben gives the "
                "ball to Cal. Cal gives the ball to Dan. Dan gives the ball "
                "to Ann. Who has the ball now?", "Ann"),
               ("Cal has the pen. Cal gives the pen to Dan. Dan gives the pen "
                "to Ann. Ann gives the pen to Cal. Cal gives the pen to Ben. "
                "Who has the pen now?", "Ben")],
        gen=_gen_entity_track, oracle=_oracle_entity_track,
        basis_fn=_basis_entity_track,
        split_params=SplitParams(holdout_frac=0.4, min_holdout_values=15,
                                 min_val_items=300)),
    CapabilitySpec(
        name="units", description="metric conversion (power 1-3)",
        answer_type="number", probe_label_space="power of 10 (1-3)",
        basis_kind="unit pair (16 values; design's 3/16 holdout overrides the "
                   "15-value minimum)",
        composability="the factor for an unseen pair is factual knowledge of "
                      "the metric prefixes",
        shots=[("How many meters are in 3 kilometers?", "3000"),
               ("How many millimeters are in 7 centimeters?", "70")],
        gen=_gen_units, oracle=_oracle_units, basis_fn=_basis_units,
        split_params=SplitParams(n_holdout=3, min_holdout_values=3,
                                 min_val_items=300)),
]
