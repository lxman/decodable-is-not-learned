# experiments/exp6/tests/test_generators_a_6.py
"""Arithmetic, word and unit rungs, each checked against an INDEPENDENT
recomputation of its answer: the tests never call the generator's own
oracle."""
import re
from collections import Counter
from fractions import Fraction

import pytest

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
    ("modarith_add1", "+", 1000, lambda a, b: a + b + 1),
    ("modarith_sub1", "-", 1000, lambda a, b: a - b + 1),
    ("modarith_mul1", "*", 100, lambda a, b: a * b + 1)])
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
