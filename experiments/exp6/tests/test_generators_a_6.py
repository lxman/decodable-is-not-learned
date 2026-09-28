# experiments/exp6/tests/test_generators_a_6.py
"""Arithmetic, word and unit rungs, each checked against an INDEPENDENT
recomputation of its answer: the tests never call the generator's own
oracle."""
import re
from collections import Counter
from fractions import Fraction

import pytest

import hashlib

from experiments.exp6.battery import gen_arith, gen_units, gen_words  # noqa: F401
from experiments.exp6.tests import _build

NAMES_A = ("modarith_add1", "modarith_sub1", "modarith_mul1", "lcs",
           "unscramble_short", "unscramble_long", "sort3", "sort5", "ipa_word",
           "unit_interp1", "unit_interp2")


@pytest.fixture(scope="module")
def built():
    return _build.build(NAMES_A, gen_words.context())


def _items(built, name):
    return built[name]["eval_items"]


def test_every_rung_is_500_clean_items(built):
    _build.check_clean(built)


# ------------------------------------------------------------ arithmetic
@pytest.mark.parametrize("name,sym,bound,op", [
    ("modarith_add1", "+", 999, lambda a, b: a + b + 1),
    ("modarith_sub1", "-", 999, lambda a, b: a - b + 1),
    ("modarith_mul1", "*", 99, lambda a, b: a * b + 1)])
def test_modified_arithmetic(built, name, sym, bound, op):
    for it in _items(built, name):
        lines = it["question"].split("\n")
        assert lines[0] == gen_arith.MODARITH_HEADER and len(lines) == 7
        pairs = []
        for ln in lines[1:6]:
            m = re.fullmatch(rf"(\d+) {re.escape(sym)} (\d+) -> (-?\d+)", ln)
            a, b, r = int(m.group(1)), int(m.group(2)), int(m.group(3))
            assert r == op(a, b)
            pairs.append((a, b))
        m = re.fullmatch(rf"(\d+) {re.escape(sym)} (\d+) ->", lines[6])
        a, b = int(m.group(1)), int(m.group(2))
        pairs.append((a, b))
        assert it["answer"] == str(op(a, b))
        assert (it["meta"]["a"], it["meta"]["b"]) == (a, b)
        assert len(set(pairs)) == 6
        assert all(0 <= v < bound for p in pairs for v in p)


def test_subtraction_has_negative_answers(built):
    n = sum(1 for it in _items(built, "modarith_sub1") if it["answer"].startswith("-"))
    assert 150 < n < 350


def _lcs_recursive(a, b, memo=None):
    memo = {} if memo is None else memo
    if not a or not b:
        return 0
    if (a, b) not in memo:
        memo[(a, b)] = (1 + _lcs_recursive(a[1:], b[1:], memo) if a[0] == b[0]
                        else max(_lcs_recursive(a[1:], b, memo),
                                 _lcs_recursive(a, b[1:], memo)))
    return memo[(a, b)]


def test_lcs(built):
    assert gen_arith.lcs_length("ABCDE", "ACE") == 3          # BIG-bench's example
    assert gen_arith.lcs_length("SZPHKVR", "ECOUO") == 0
    items = _items(built, "lcs")
    assert Counter(it["answer"] for it in items) == {str(k): 50 for k in range(10)}
    for it in items[::7]:
        q = it["question"].split("\n")
        assert q[0] == gen_arith.LCS_HEADER
        a, b = q[1].removeprefix("Strings: ").split(" ")
        assert 4 <= len(a) <= 31 and 4 <= len(b) <= 31
        assert a.isupper() and b.isupper() and a.isalpha() and b.isalpha()
        assert int(it["answer"]) == _lcs_recursive(a, b)


# ----------------------------------------------------------------- words
@pytest.mark.parametrize("name,lengths", [("unscramble_short", {4: 250, 5: 250}),
                                          ("unscramble_long", {6: 167, 7: 167, 8: 166})])
def test_unscramble(built, name, lengths):
    ctx = gen_words.context()
    uniq = {w for ws in ctx["unique_by_len"].values() for w in ws}
    items = _items(built, name)
    assert Counter(len(it["answer"]) for it in items) == lengths
    assert len({it["answer"] for it in items}) == 500
    for it in items:
        m = re.fullmatch(r"The word (\w+) is a scrambled version of the English word",
                         it["question"])
        s = m.group(1)
        assert sorted(s) == sorted(it["answer"]) and s != it["answer"]
        assert it["answer"] in uniq


@pytest.mark.parametrize("name,n", [("sort3", 3), ("sort5", 5)])
def test_sort(built, name, n):
    items = _items(built, name)
    assert Counter(it["meta"]["prefix_class"] for it in items) == {0: 167, 1: 167, 2: 166}
    for it in items:
        words = it["question"].removeprefix(
            "Sort the following words alphabetically: ").split(" ")
        assert len(words) == n == len(set(words))
        assert it["answer"].split(" ") == sorted(words) != words
        s = sorted(words)
        lcp = max(len(os_commonprefix(a, b)) for a, b in zip(s, s[1:]))
        assert min(lcp, 2) == it["meta"]["prefix_class"]
        assert not any(a in b for a in words for b in words if a != b)


def os_commonprefix(a, b):
    out = ""
    for x, y in zip(a, b):
        if x != y:
            break
        out += x
    return out


def test_ipa(built):
    ctx = gen_words.context()
    items = _items(built, "ipa_word")
    assert Counter(it["meta"]["ipa_bin"] for it in items) == {0: 167, 1: 167, 2: 166}
    for it in items:
        word = it["question"].rsplit(": ", 1)[1]
        assert it["answer"] == ctx["ipa"][word]
        n = sum(1 for c in it["answer"] if c not in "ˈˌ")
        lo, hi = gen_words.IPA_BINS[it["meta"]["ipa_bin"]]
        assert lo <= n <= hi


# ----------------------------------------------------------------- units
_WORD_K = {"twice": 2, "three times": 3, "four times": 4, "half": 2,
           "one third": 3, "one fourth": 4}


def test_unit_interp1(built):
    for it in _items(built, "unit_interp1"):
        body, opts = it["question"].split("\nOptions: ")
        opts = [int(o) for o in opts.split(", ")]
        m = re.fullmatch(
            r"A \w+ \w+ (\d+) \w+ every (?:(\d+) )?\w+\. "
            r"(?:If \w+ \w+(?: \w+)? (with intervals )?(twice|three times|four times) "
            r"as (?:often|long), \w+|It|They) will \w+ "
            r"(\d+|\(\)) \w+ in (\d+|\(\)) \w+\.", body)
        assert m, body
        n, p = int(m.group(1)), int(m.group(2) or 1)
        k = _WORD_K[m.group(4)] if m.group(4) else 1
        if m.group(3):                # intervals k times as long
            p *= k
        else:
            n *= k
        if m.group(5) == "()":
            want = n * int(m.group(6)) // p
            assert n * int(m.group(6)) % p == 0
        else:
            want = p * int(m.group(5)) // n
            assert p * int(m.group(5)) % n == 0
        assert it["answer"] == str(want)
        assert len(set(opts)) == 5 and all(o > 0 for o in opts)
        assert opts[it["meta"]["answer_pos"] - 1] == want


def test_unit_interp2(built):
    for it in _items(built, "unit_interp2"):
        body, opts = it["question"].split("\nOptions: ")
        opts = [int(o) for o in opts.split(", ")]
        m = it["meta"]
        r = int(re.search(r"(\d+) \w+ per \w+", body).group(1))
        given = int(re.search(r", and .*? (\d+) ", body).group(1))
        assert r == m["r"] and given == (m["a"] if m["give_a"] else m["b"])
        a = given if m["give_a"] else r * given             # the invariant
        assert a == m["a"] and a == r * m["b"]
        if m["k"]:
            word = re.search(r"If .+? (twice|three times|four times|half|one third|"
                             r"one fourth) as (?:fast|much)", body).group(1)
            k = _WORD_K[word]
            faster = word in ("twice", "three times", "four times")
            assert (k, faster) == (m["k"], m["faster"])
            rate = Fraction(r * k) if faster else Fraction(r, k)
        else:
            rate = Fraction(r)
        want = Fraction(a) if m["ask_a"] else Fraction(a) / rate
        assert want.denominator == 1 and it["answer"] == str(int(want))
        assert len(set(opts)) == 5 and all(o > 0 for o in opts)
        assert opts[m["answer_pos"] - 1] == int(want)
        asked_unit = re.search(r"\(\) (\w+)", body).group(1)
        given_unit = re.search(r", and .*? \d+ (\w+)", body).group(1)
        assert (asked_unit == given_unit) == (m["ask_a"] == m["give_a"])


# ---------------------------------------------------- the collision keys
def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def test_the_two_surfaces_of_a_unit_sentence():
    """The task files' slips are in the key and never in what a model
    reads (the strings themselves: tests/test_bbkeys_6.py, Task 5)."""
    a = (1, 5, 12, 4, True, True, 240)                     # a patient, scaled
    assert gen_units.lv1_sentence(*a) == (
        "A patient takes 5 pills every 12 days. If they take pills four times as "
        "often, they will take 240 pills in () days.")
    assert gen_units.lv1_sentence(*a, surface="bigbench") == (
        "A patient takes 5 pills every 12 days. If they takes pills four times as "
        "often, They will take 240 pills in () days.")
    r = (4, 3, 5, 2, False, False, 120)                    # a reporter, scaled
    assert gen_units.lv1_sentence(*r) == (
        "A reporter speaks 3 words every 5 minutes. If they speak with intervals "
        "twice as long, they will speak () words in 120 minutes.")
    assert gen_units.lv1_sentence(*r, surface="bigbench") == (
        "A reporter speaks 3 words every 5 minutes. If they speaks with intervals "
        "twice as long, they will speak () words in 120 minutes.")
    b = (0, 2, 1, 0, False, True, 48)                      # a bell, unscaled
    assert gen_units.lv1_sentence(*b) == gen_units.lv1_sentence(*b, surface="bigbench") \
        == "A bell rings 2 times every hour. It will ring 48 times in () hours."
    f = (3, 2, 48, True, 4, False, False)                  # fuel, one fourth as fast
    assert "one fourth as fast" in gen_units.lv2_sentence(*f)
    assert "one forth as fast" in gen_units.lv2_sentence(*f, surface="bigbench")
    assert gen_units.lv2_sentence(*f).replace("fourth", "forth") == \
        gen_units.lv2_sentence(*f, surface="bigbench")
    with pytest.raises(ValueError):
        gen_units.lv1_sentence(*b, surface="bb")
    with pytest.raises(ValueError):
        gen_units.lv2_sentence(*f, surface="")


def test_the_lcs_lengths_are_drawn_without_regard_to_the_answer(built):
    """BIG-bench balances the answers and lets the lengths fall where
    they fall. The first build drew them from a window set by the
    answer: no string of an answer-0 item was longer than 8, none of an
    answer-9 item shorter than 18."""
    items = _items(built, "lcs")
    by = {}
    for it in items:
        by.setdefault(it["answer"], []).extend(
            [len(it["meta"]["a"]), len(it["meta"]["b"])])
    assert max(by["0"]) > 12 and min(by["9"]) < 18 and max(by["3"]) >= 28
    assert all(4 <= x <= 31 for v in by.values() for x in v)
    assert built["lcs"]["n_redrawn"]["rejected"] > 5000      # balanced by rejection


def test_the_query_of_a_modified_arithmetic_item_is_a_key_of_its_own(built):
    from experiments.exp6.battery import collisions_6 as c6
    from experiments.exp6.battery import spec as sp
    for name in ("modarith_add1", "modarith_sub1", "modarith_mul1"):
        extra = c6.extra_for_spec(sp.SPECS_6[name])
        for it in _items(built, name):
            q = gen_arith.modarith_query(name, it["meta"]["a"], it["meta"]["b"])
            assert q == it["question"].split("\n")[-1]
            assert it["bb_extra_sha256"] == [_sha(q)]
            assert it["bb_extra_sha256"][0] not in extra
            a, sym, b = q.removesuffix(" ->").split(" ")
            if sym in gen_arith.COMMUTES:              # nor the other way round
                assert _sha(f"{b} {sym} {a} ->") not in extra
    # two-digit pairs are 9,801 and BIG-bench prints 4,500 of them, each
    # beside its result on a worked line or asked; either way round they
    # are two thirds of the space, and the gate fires on two draws in three
    assert 800 < built["modarith_mul1"]["n_redrawn"]["collision"] < 1400
    assert built["modarith_add1"]["n_redrawn"]["collision"] < 30
    assert built["modarith_sub1"]["n_redrawn"]["collision"] < 20


def _key_from_meta(name, it):
    """The key rebuilt from the item's own record."""
    m = it["meta"]
    if name.startswith("modarith"):
        return gen_arith.modarith_text(
            name, [tuple(p) for p in m["examples"]] + [(m["a"], m["b"])])
    if name == "lcs":
        return gen_arith.lcs_key(m["a"], m["b"])
    if name.startswith("unscramble"):
        return gen_words.unscramble_key(m["scrambled"])
    if name.startswith("sort"):
        return gen_words.sort_key(m["words"])
    if name == "ipa_word":
        return gen_words.ipa_key(m["word"])
    if name == "unit_interp1":
        row = [r[0] for r in gen_units.LV1].index(m["subject"])
        n_eff = m["n"] * m["k"] if m["k"] and m["often"] else m["n"]
        p_eff = m["p"] * m["k"] if m["k"] and not m["often"] else m["p"]
        shown = (n_eff if m["ask_time"] else p_eff) * m["m"]
        return gen_units.lv1_sentence(row, m["n"], m["p"], m["k"], m["often"],
                                      m["ask_time"], shown, surface="bigbench")
    (row,) = [i for i, r in enumerate(gen_units.LV2)
              if r[0].split(" at ")[0].split(" costs")[0] == m["subject"]]
    return gen_units.lv2_sentence(row, m["r"], m["a"] if m["give_a"] else m["b"],
                                  m["give_a"], m["k"], m["faster"], m["ask_a"],
                                  surface="bigbench")


def test_every_item_key_is_the_renderers(built):
    for name in NAMES_A:
        for it in _items(built, name):
            assert _sha(_key_from_meta(name, it)) == it["bb_sha256"], name


def test_what_a_model_reads_against_the_key(built):
    """Question and key differ only where stated: a header, a trailing
    space, the options, the corrected wording."""
    for name in NAMES_A:
        for it in _items(built, name)[::11]:
            q, key = it["question"].split("\nOptions: ")[0], _key_from_meta(name, it)
            if name.startswith("modarith"):
                assert q == key
            elif name == "lcs":
                assert q == f"{gen_arith.LCS_HEADER}\nStrings: {key}"
            elif name.startswith("unscramble"):
                assert q + " " == key
            elif name.startswith("sort"):
                assert q == gen_words.SORT_HEADER + key
            elif name == "ipa_word":
                assert q == gen_words.IPA_HEADER + it["meta"]["word"]
            else:
                fixed = (key.replace("they takes", "they take")
                            .replace("they speaks", "they speak")
                            .replace(", They will", ", they will")
                            .replace("one forth", "one fourth"))
                assert q == fixed


def _smooth(x: int) -> bool:
    for q in (2, 3, 5):
        while x % q == 0:
            x //= q
    return x == 1


@pytest.mark.parametrize("name,n_subjects", [("unit_interp1", 5), ("unit_interp2", 6)])
def test_the_answer_is_balanced_by_position_and_by_size(built, name, n_subjects):
    """The answer's list position and its rank by size are both designed
    and are crossed: over twenty-five blocks of slots every pair occurs
    once. Left free, a guesser picking one rank by size scored .45."""
    items = _items(built, name)
    rank, pos, joint = Counter(), Counter(), Counter()
    for slot, it in enumerate(items):
        opts = [int(o) for o in it["question"].split("\nOptions: ")[1].split(", ")]
        assert len(set(opts)) == 5 and all(0 < o <= gen_units.CAP for o in opts)
        assert opts == it["meta"]["options"]
        k = slot // n_subjects
        r = sorted(opts).index(int(it["answer"])) + 1
        assert r == it["meta"]["answer_rank"] == (k // 5 + k) % 5 + 1
        assert opts.index(int(it["answer"])) + 1 == it["meta"]["answer_pos"] == k % 5 + 1
        rank[r] += 1
        pos[it["meta"]["answer_pos"]] += 1
        joint[(it["meta"]["answer_pos"], r)] += 1
    assert set(rank) == set(pos) == {1, 2, 3, 4, 5} and len(joint) == 25
    assert max(rank.values()) <= 102 and max(pos.values()) <= 102
    assert min(rank.values()) >= 96 and min(pos.values()) >= 96
    assert min(joint.values()) >= 18 and max(joint.values()) <= 24
    a, b = [int(a) for _, a in built[name]["shots"]]
    sa, sb = [[int(o) for o in q.split("\nOptions: ")[1].split(", ")]
              for q, _ in built[name]["shots"]]
    assert sa.index(a) != sb.index(b)                        # the shots' positions
    assert sorted(sa).index(a) != sorted(sb).index(b)        # and their ranks


@pytest.mark.parametrize("name", ["unit_interp1", "unit_interp2"])
def test_the_numbers_and_the_wrong_options_follow_the_readme(built, name):
    """The README's steps 3 and 5: numbers without a large prime factor;
    the shown quantity a multiple of every number of the item, so every
    combination is an integer; a wrong option a combination of the
    item's numbers, or a pool number."""
    kinds, below = Counter(), Counter()
    for it in _items(built, name):
        m = it["meta"]
        body = it["question"].split("\nOptions: ")[0]
        if name == "unit_interp1":
            n_eff = m["n"] * m["k"] if m["k"] and m["often"] else m["n"]
            p_eff = m["p"] * m["k"] if m["k"] and not m["often"] else m["p"]
            shown = (n_eff if m["ask_time"] else p_eff) * m["m"]
            numbers = (m["n"], m["p"], m["k"])
            printed = {m["n"], m["p"]} - {1}
            assert _smooth(m["n"]) and _smooth(m["p"]) and 2 <= m["n"] <= 50 >= m["p"]
        else:
            shown = m["a"] if m["give_a"] else m["b"]
            numbers = (m["r"], m["k"])
            printed = {m["r"]}
            assert _smooth(m["r"]) and 2 <= m["r"] <= 30
        assert f" {shown} " in body and all(shown % f == 0 for f in numbers if f > 1)
        combos = gen_units.combinations(shown, numbers) | printed
        assert shown in combos and int(it["answer"]) in combos
        assert max(combos) <= gen_units.CAP
        for x, kind in zip(m["options"], m["option_kinds"]):
            if x == int(it["answer"]):
                assert kind == "answer"
                continue
            assert kind == ("combination" if x in combos else "pool"), (it, x)
            kinds[kind] += 1
            below[(kind, x < int(it["answer"]))] += 1
    n = sum(kinds.values())
    assert n == 2000
    # "most incorrect answers are the wrong combination of the generated
    # numbers": three in four where the item has them to give
    assert 0.55 <= kinds["combination"] / n <= 0.75
    # and either kind falls on either side of the answer
    for kind in ("combination", "pool"):
        share = below[(kind, True)] / kinds[kind]
        assert 0.35 <= share <= 0.65, (kind, share)


def test_the_combinations_of_an_item():
    assert gen_units.combinations(20, (5, 4, 0)) == {1, 4, 5, 16, 20, 25, 80, 100, 400}
    assert gen_units.combinations(36, (12, 3, 2)) >= {9, 18, 72, 144, 288, 36}
    assert gen_units.combinations(48, (2, 1, 0)) == {24, 48, 96}      # a period of one
    assert max(gen_units.combinations(4000, (50, 48, 4))) <= gen_units.CAP
    assert gen_units.smooth(2, 12) == (2, 3, 4, 5, 6, 8, 9, 10, 12)
    assert all(_smooth(x) for x in gen_units.WRONG_POOL) and len(gen_units.WRONG_POOL) > 40


def test_unit_interp2_flags_a_stated_answer(built):
    """BIG-bench's class: the scaled rate leaves the stated quantity
    unchanged and that quantity is asked. Flagged, not excluded."""
    items = _items(built, "unit_interp2")
    flagged = [it for it in items if it["meta"]["answer_stated"]]
    assert len(flagged) == 57
    for it in items:
        m = it["meta"]
        assert m["answer_stated"] == bool(m["k"] and m["give_a"] and m["ask_a"])
        if m["answer_stated"]:
            assert it["answer"] == str(m["a"])
            assert f" {m['a']} " in it["question"].split("\nOptions: ")[0]
