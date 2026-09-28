# experiments/exp6/tests/test_generators_a_6.py
"""Arithmetic, word and unit rungs, each checked against an INDEPENDENT
recomputation of its answer: the tests never call the generator's own
oracle."""
import re
import itertools
from collections import Counter, defaultdict
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
    assert built["modarith_add1"]["n_redrawn"]["collision"] < 20
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


SEEDS_TWINS = 2500
CHI2_ORDERS = 60.0


def _options_of(it):
    return [int(o) for o in it["question"].split("\nOptions: ")[1].split(", ")]


_UP = ("twice", "three times", "four times")
# level 2's cycle of twelve slots, written out: (scaling, unit A stated, unit A asked)
_CELLS_LV2 = [("plain", True, False), ("up", True, True), ("up", True, False),
              ("plain", False, True), ("up", False, True), ("up", False, False),
              ("plain", True, False), ("down", True, True), ("down", True, False),
              ("plain", False, True), ("down", False, True), ("down", False, False)]


def _printed(name, body):
    """What a sentence prints, read from its TEXT and from nothing of the
    item's record: its numbers, the factor and direction of its scaling
    (up: the rate scaled up), and the roles of its units."""
    if name == "unit_interp1":
        m = re.fullmatch(
            r"A \w+ \w+ (\d+) \w+ every (?:(\d+) )?\w+\. "
            r"(?:If \w+ \w+(?: \w+)? (with intervals )?(twice|three times|four times) "
            r"as (?:often|long), \w+|It|They) will \w+ "
            r"(\d+|\(\)) \w+ in (\d+|\(\)) \w+\.", body)
        k = _WORD_K[m.group(4)] if m.group(4) else 0
        ask_time = m.group(6) == "()"
        return {"n": int(m.group(1)), "p": int(m.group(2) or 1), "k": k,
                "up": bool(k) and not m.group(3), "ask_time": ask_time,
                "shown": int(m.group(5) if ask_time else m.group(6))}
    word = re.search(r"If .+? (twice|three times|four times|half|one third|"
                     r"one fourth) as (?:fast|much)", body)
    k = _WORD_K[word.group(1)] if word else 0
    asked_unit = re.search(r"\(\) (\w+)", body).group(1)
    given_unit = re.search(r", and .*? \d+ (\w+)", body).group(1)
    unit_a = re.search(r"\d+ (\w+) per \w+", body).group(1)
    return {"r": int(re.search(r"(\d+) \w+ per \w+", body).group(1)), "k": k,
            "up": bool(k) and word.group(1) in _UP,
            "shown": int(re.search(r", and .*? (\d+) ", body).group(1)),
            "give_a": given_unit == unit_a, "ask_a": asked_unit == unit_a}


def _candidates(name, s):
    """The answers of the sentences that print what this one prints and
    differ from it in the roles of their units (level 1: in the
    direction of the scaling too)."""
    g, k = Fraction(s["shown"]), s["k"]
    if name == "unit_interp1":
        rate = Fraction(s["n"], s["p"])
        out = {g * x * y for x in (rate, 1 / rate)
               for y in ((Fraction(k), Fraction(1, k)) if k else (1,))}
    elif not k:
        out = {g * s["r"], g / s["r"]}
    else:
        c = Fraction(1, k) if s["up"] else Fraction(k)
        out = {g, g * s["r"], g * c, g * c / s["r"]}
    assert all(v.denominator == 1 and 0 < v <= gen_units.CAP for v in out)
    return {int(v) for v in out}


def _readings(name, s):
    """Every reading of the sentence, right and wrong: the rate the right
    way round or the wrong (level 2: or left out), the scaling the right
    way round, the wrong, or left out."""
    ks = (Fraction(1, s["k"]), Fraction(1), Fraction(s["k"])) if s["k"] else (Fraction(1),)
    if name == "unit_interp1":
        rate = Fraction(s["n"], s["p"])
        steps = (rate, 1 / rate)
    else:
        steps = (Fraction(1, s["r"]), Fraction(1), Fraction(s["r"]))
    out = {s["shown"] * x * y for x in steps for y in ks}
    assert all(v.denominator == 1 and 0 < v <= gen_units.CAP for v in out)
    return {int(v) for v in out}


@pytest.mark.parametrize("name", ["unit_interp1", "unit_interp2"])
def test_what_the_slot_fixes(built, name):
    """What is asked, the kind of scaling and the answer's list position
    are set by the slot: a rejected draw redraws the numbers and nothing
    else, so no rejection can skew them."""
    items = _items(built, name)
    pos, cell, joint = Counter(), Counter(), Counter()
    for slot, it in enumerate(items):
        m, opts, answer = it["meta"], _options_of(it), int(it["answer"])
        s = _printed(name, it["question"].split("\nOptions: ")[0])
        scaling = "plain" if not s["k"] else "up" if s["up"] else "down"
        if name == "unit_interp1":
            want = {"row": slot % 5, "pos": slot // 5 % 5 + 1,
                    "scaling": ("plain", "up", "down")[slot % 3],
                    "ask_time": bool(slot % 2)}
            assert gen_units.design_lv1(slot) == want
            assert m["subject"] == gen_units.LV1[want["row"]][0]
            role = (s["ask_time"],)
            assert role == (want["ask_time"],) == (m["ask_time"],)
        else:
            c = _CELLS_LV2[slot % 12]
            want = {"row": slot // 12 % 6, "pos": slot % 5 + 1, "scaling": c[0],
                    "give_a": c[1], "ask_a": c[2]}
            assert gen_units.design_lv2(slot) == want
            assert gen_units.LV2[want["row"]][0].startswith(m["subject"])
            role = (s["give_a"], s["ask_a"])
            assert role == c[1:] == (m["give_a"], m["ask_a"])
        assert scaling == want["scaling"]
        assert len(set(opts)) == 5 and all(0 < o <= gen_units.CAP for o in opts)
        assert opts == m["options"]
        assert opts.index(answer) + 1 == m["answer_pos"] == want["pos"]
        assert sorted(opts).index(answer) + 1 == m["answer_rank"]
        pos[want["pos"]] += 1
        cell[(scaling,) + role] += 1
        joint[(want["pos"], scaling) + role] += 1
    assert dict(pos) == {1: 100, 2: 100, 3: 100, 4: 100, 5: 100}
    if name == "unit_interp1":
        assert len(cell) == 6 and set(cell.values()) <= {83, 84}
        assert len(joint) == 30 and set(joint.values()) <= {16, 17}
    else:
        # the unscaled cells twice as often as a scaled one
        plain = {k: v for k, v in cell.items() if k[0] == "plain"}
        scaled = {k: v for k, v in cell.items() if k[0] != "plain"}
        assert len(plain) == 2 and set(plain.values()) <= {82, 83, 84}
        assert len(scaled) == 8 and set(scaled.values()) <= {41, 42}
        assert len(joint) == 50 and all(
            v in ((16, 17, 18) if k[1] == "plain" else (8, 9)) for k, v in joint.items())
    # the two shots: one scaled sentence and one unscaled, at different
    # list positions, neither asking what the other asks
    (qa, a), (qb, b) = built[name]["shots"]
    sa, sb = [[int(o) for o in q.split("\nOptions: ")[1].split(", ")] for q in (qa, qb)]
    assert sa.index(int(a)) != sb.index(int(b))
    pa, pb = (_printed(name, q.split("\nOptions: ")[0]) for q in (qa, qb))
    roles = ("ask_time",) if name == "unit_interp1" else ("give_a", "ask_a")
    assert all(pa[k] != pb[k] for k in roles)
    assert bool(pa["k"]) and not pb["k"]
    # and no item asks what a shot asks under another subject, nor prints
    # a shot's numbers with a shot's answer under another scaling
    asked = [_printed(name, it["question"].split("\nOptions: ")[0]) for it in items]
    assert pa not in asked and pb not in asked

    def shows(q, answer):
        return tuple(re.findall(r"\d+", q.split("\nOptions: ")[0])), str(answer)
    assert not {shows(qa, a), shows(qb, b)} & {
        shows(it["question"], it["answer"]) for it in items}


@pytest.mark.parametrize("name,kinds,share", [
    ("unit_interp1", {"misreading": 1182, "combination": 582, "pool": 236}, (598, 834)),
    ("unit_interp2", {"misreading": 1415, "combination": 335, "pool": 250}, (584, 834))])
def test_the_numbers_and_the_wrong_options_follow_the_readme(built, name, kinds, share):
    """The README's steps 3 and 5: numbers without a large prime factor;
    the shown quantity a multiple of each number of the item; the wrong
    options the wrong readings of the sentence, other combinations of
    its numbers, and pool numbers. Everything is recomputed from the
    sentence's text."""
    got, fills = Counter(), Counter()
    for it in _items(built, name):
        m, answer = it["meta"], int(it["answer"])
        s = _printed(name, it["question"].split("\nOptions: ")[0])
        if name == "unit_interp1":
            numbers, printed = (s["n"], s["p"], s["k"]), {s["n"], s["p"]} - {1}
            assert _smooth(s["n"]) and _smooth(s["p"]) and 2 <= s["n"] <= 50 >= s["p"]
            # a rate of one, or the factor's, prints a reading of the sentence
            rate = Fraction(s["n"], s["p"])
            assert rate != 1 and (not s["k"] or s["k"] not in (rate, 1 / rate))
            assert s["shown"] not in (s["n"], s["p"])      # nor restates its rate
        else:
            numbers, printed = (s["r"], s["k"]), {s["r"]}
            assert _smooth(s["r"]) and 2 <= s["r"] <= 30
        assert s["shown"] == m["shown" if name == "unit_interp1" else "given"]
        assert all(s["shown"] % f == 0 for f in numbers if f > 1)
        cands, every = _candidates(name, s), _readings(name, s)
        # every reading of the sentence is an integer within the cap,
        # whatever it asks: the numbers do not depend on the answer
        assert len(cands) == (4 if s["k"] else 2) and answer in cands
        assert cands <= every and sorted(cands) == m["candidates"]
        # no candidate is a number the sentence prints, level 2's stated
        # quantity aside (a scaled sentence may ask for it), and none is 1
        assert not cands & ({1} | ({s["n"], s["p"], s["shown"]} if name == "unit_interp1"
                                   else {s["r"]}))
        assert (s["shown"] in cands) == (name == "unit_interp2" and bool(s["k"]))
        combos = gen_units.combinations(s["shown"], numbers, depth=2) | printed
        assert every <= combos and max(combos) <= gen_units.CAP
        # every candidate is offered, and 1 never is
        assert cands < set(m["options"]) and 1 not in m["options"], it["question"]
        for x, kind in zip(m["options"], m["option_kinds"]):
            want = ("answer" if x == answer else "misreading" if x in every else
                    "combination" if x in combos else "pool")
            assert kind == want, (it["question"], x, kind)
            if x != answer:
                got[kind] += 1
            if x not in cands:
                fills["pool" if kind == "pool" else "combination"] += 1
    assert dict(got) == kinds and sum(got.values()) == 2000
    # of the fills, three in four are combinations of the item's numbers,
    # fewer where an item has too few (level 2: two numbers, not three)
    assert (fills["combination"], sum(fills.values())) == share


@pytest.mark.parametrize("name", ["unit_interp1", "unit_interp2"])
def test_the_numbers_and_the_options_do_not_say_what_is_asked(name):
    """Sentences that differ in the roles of their units alone (level 1:
    in the direction of the scaling too), drawn from one state of the
    generator: they print the same numbers, offer the same options, are
    refused together — and their answers are the candidates, one each."""
    import numpy as np
    lv1 = name == "unit_interp1"
    draw = gen_units._draw_lv1 if lv1 else gen_units._draw_lv2
    n_drawn = n_refused = 0
    orders = defaultdict(Counter)
    for seed in range(SEEDS_TWINS):
        for kind in (("plain", "scaled") if lv1 else gen_units.SCALINGS):
            if lv1:
                cells = [{"scaling": sc, "ask_time": t}
                         for sc in (("plain",) if kind == "plain" else ("up", "down"))
                         for t in (False, True)]
            else:
                cells = [{"scaling": kind, "give_a": g, "ask_a": a}
                         for g in (True, False) for a in (True, False)
                         if kind != "plain" or g != a]
            out = [draw(np.random.default_rng(seed), None, 0,
                        {"row": seed % 5, "pos": seed % 5 + 1, **c}) for c in cells]
            if any(o is None for o in out):
                assert all(o is None for o in out)
                n_refused += 1
                continue
            n_drawn += 1
            numbers = [tuple(re.findall(r"\d+", o["question"].split("\nOptions: ")[0]))
                       for o in out]
            assert len(set(numbers)) == 1
            assert len({tuple(sorted(o["meta"]["options"])) for o in out}) == 1
            answers = sorted(int(o["answer"]) for o in out)
            assert answers == out[0]["meta"]["candidates"]
            assert len(set(answers)) == len(cells) == (2 if kind == "plain" else 4)
            for c, o in zip(cells, out):                 # the place, and nothing else
                mine = o["meta"]["options"]
                assert mine.index(int(o["answer"])) == seed % 5
                rest = [x for x in mine if x != int(o["answer"])]
                orders[(kind,) + tuple(sorted(c.items()))][
                    tuple(sorted(range(4), key=lambda i: rest[i]))] += 1
            # every other option in one order: what two sentences list,
            # their two answers taken out, is the same list
            for a, b in itertools.combinations(out, 2):
                gone = {int(a["answer"]), int(b["answer"])}
                assert [x for x in a["meta"]["options"] if x not in gone] == \
                    [x for x in b["meta"]["options"] if x not in gone]
    assert n_drawn > 1500 and n_refused > 300
    # and that order says nothing: by size, the four options that are not
    # the answer stand in each of the 24 orders as often as in any other,
    # in every cell (sorted options would give the answer away as the one
    # out of order). Chi-square on 23 degrees of freedom: an innocent
    # stream exceeds 60 in a cell about three times in 100,000.
    assert len(orders) == (6 if lv1 else 10)
    for cell, tally in orders.items():
        n = sum(tally.values())
        assert n > 400 and len(tally) == 24, cell
        chi2 = sum((v - n / 24) ** 2 / (n / 24) for v in tally.values())
        assert chi2 < CHI2_ORDERS, (cell, chi2)


def test_what_a_unit_item_would_give_away():
    """The content key the driver gates the shots on: the numbers a
    sentence prints and its answer. Another subject: the same key.
    Another role: another answer, another key. On level 2, another
    scaling where the asked quantity does not change with it: the same
    answer, the same key."""
    import numpy as np

    def key(name, seed, **d):
        draw = gen_units._draw_lv1 if name == "unit_interp1" else gen_units._draw_lv2
        return draw(np.random.default_rng(seed), None, 0, {"pos": 1, **d})
    n = {"subject": 0, "role": 0, "scaling": 0}
    for seed in range(600):                      # about one scaled draw in four is kept
        a = key("unit_interp1", seed, row=0, scaling="up", ask_time=True)
        if a is not None:
            b = key("unit_interp1", seed, row=3, scaling="up", ask_time=True)
            c = key("unit_interp1", seed, row=0, scaling="up", ask_time=False)
            d = key("unit_interp1", seed, row=0, scaling="down", ask_time=True)
            m = a["meta"]
            assert a["content_key"] == f"lv1|{m['n']}|{m['p']}|{m['shown']}|={a['answer']}"
            assert a["content_key"] == b["content_key"] and a["question"] != b["question"]
            assert len({x["content_key"] for x in (a, c, d)}) == 3
            n["subject"] += 1
        a = key("unit_interp2", seed, row=0, scaling="up", give_a=False, ask_a=True)
        if a is not None:
            b = key("unit_interp2", seed, row=4, scaling="up", give_a=False, ask_a=True)
            c = key("unit_interp2", seed, row=0, scaling="up", give_a=False, ask_a=False)
            d = key("unit_interp2", seed, row=0, scaling="down", give_a=False, ask_a=True)
            m = a["meta"]
            assert a["content_key"] == f"lv2|{m['r']}|{m['given']}|={a['answer']}"
            assert a["content_key"] == b["content_key"] and a["question"] != b["question"]
            assert a["content_key"] != c["content_key"]
            n["role"] += 1
            # the invariant asked, the rate scaled the other way (a draw the
            # other scaling's candidates may refuse): the same answer
            if d is not None:
                assert d["answer"] == a["answer"] and d["question"] != a["question"]
                assert d["content_key"] == a["content_key"]
                n["scaling"] += 1
    assert min(n.values()) > 100


@pytest.mark.parametrize("name,only", [("unit_interp1", 0), ("unit_interp2", 0)])
def test_the_answer_is_not_the_one_option_a_stated_number_divides(built, name, only):
    n = 0
    for it in _items(built, name):
        body = it["question"].split("\nOptions: ")[0]
        stated = [int(x) for x in re.findall(r"\d+", body) if int(x) > 1]
        ok = [o for o in _options_of(it) if any(o % t == 0 for t in stated)]
        n += ok == [int(it["answer"])]
    assert n == only


def test_the_combinations_and_the_readings_of_an_item():
    assert gen_units.combinations(20, (5, 4, 0)) == {1, 4, 5, 16, 20, 25, 80, 100, 400}
    assert gen_units.combinations(48, (2, 1, 0)) == {24, 48, 96}      # a period of one
    assert gen_units.combinations(48, (2, 1, 0), depth=2) == {12, 24, 48, 96, 192}
    assert max(gen_units.combinations(4000, (50, 48, 4), depth=2)) <= gen_units.CAP
    assert gen_units.smooth(2, 12) == (2, 3, 4, 5, 6, 8, 9, 10, 12)
    assert all(_smooth(x) for x in gen_units.WRONG_POOL) and len(gen_units.WRONG_POOL) > 40
    # BIG-bench's own item: "12 times every 3 hours. If it rings twice as
    # often, it will ring () times in 36 hours", options 9, 18, 72, 144, 288
    r = gen_units.readings(36, Fraction(12, 3), 2)
    assert r["all"] == {9, 18, 72, 144, 288} and r["each"] == {18, 72, 288}
    assert r["dropped"] == 1                   # 36 / 4 / 2 is no integer
    # "5 times every 4 hours ... () times in 20 hours": 16 and 25
    assert gen_units.readings(20, Fraction(5, 4), 0) == {
        "all": {16, 25}, "each": {16, 25}, "dropped": 0}
    # level 2: the stated quantity is a reading of its own sentence
    r = gen_units.readings(120, Fraction(30), 2, steps=(-1, 0, 1))
    assert r["all"] == {2, 4, 8, 60, 120, 240, 1800, 3600} and 120 not in r["each"]
    assert r["each"] == {2, 8, 1800} and r["dropped"] == 1     # 7200 is above the cap
    # the candidates: what the same numbers answer under other roles
    assert gen_units.candidates_lv1(48, 12, 3, 2) == {6, 24, 96, 384}
    assert gen_units.candidates_lv1(48, 12, 3, 0) == {12, 192}
    assert gen_units.candidates_lv2(120, 30, 0, False) == {4, 3600}
    assert gen_units.candidates_lv2(120, 30, 2, True) == {2, 60, 120, 3600}
    assert gen_units.candidates_lv2(120, 30, 2, False) == {8, 120, 240, 3600}
    with pytest.raises(AssertionError):
        gen_units.candidates_lv2(7, 2, 0, False)       # 7 / 2
    with pytest.raises(AssertionError):
        gen_units.candidates_lv2(3000, 30, 0, False)   # 90000
    # the options: every candidate, then fills; the answer's place
    import numpy as np
    read = {"all": {16, 25}}
    args = ({16, 25}, read, {20, 80, 100, 400}, {30, 36})
    opts, kinds = gen_units._offer(np.random.default_rng(0), 25, *args, 2)
    assert opts[1] == 25 and len(set(opts)) == 5 and 16 in opts
    assert kinds[1] == "answer" and kinds[opts.index(16)] == "misreading"
    assert set(opts) - {16, 25} < {20, 80, 100, 400, 30, 36}
    assert all(k == ("combination" if x in (20, 80, 100, 400) else "pool")
               for x, k in zip(opts, kinds) if x not in (16, 25))
    other, _ = gen_units._offer(np.random.default_rng(0), 16, *args, 5)
    assert sorted(other) == sorted(opts) and other[4] == 16    # the same five
    assert gen_units._offer(np.random.default_rng(0), 25, {16, 25}, read,
                            set(), {30, 36}, 3) is None        # nothing to fill with
    with pytest.raises(AssertionError):
        gen_units._offer(np.random.default_rng(0), 17, *args, 2)


def test_unit_interp2_flags_a_stated_answer(built):
    """BIG-bench's class: the scaled rate leaves the stated quantity
    unchanged and that quantity is asked. Flagged, not excluded."""
    items = _items(built, "unit_interp2")
    flagged = [it for it in items if it["meta"]["answer_stated"]]
    assert len(flagged) == 84
    for it in items:
        m = it["meta"]
        assert m["answer_stated"] == bool(m["k"] and m["give_a"] and m["ask_a"])
        if m["answer_stated"]:
            assert it["answer"] == str(m["a"])
            assert f" {m['a']} " in it["question"].split("\nOptions: ")[0]
