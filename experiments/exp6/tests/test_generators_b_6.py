# experiments/exp6/tests/test_generators_b_6.py
"""ASCII, shapes, deduction and temporal rungs, each checked against an
INDEPENDENT recomputation; then the whole registry and generate.py."""
import hashlib
import math
import re
from collections import Counter
from itertools import permutations

import pytest

from experiments.exp6.battery import (gen_ascii, gen_logic, gen_shapes,
                                      generate as gen, spec as sp)
from experiments.exp6.tests import _build

NAMES_B = ("ascii_bubble", "ascii_basic", "shapes", "deduction3", "deduction5",
           "temporal")


@pytest.fixture(scope="module")
def built():
    return _build.build(NAMES_B, gen_ascii.context())


def _items(built, name):
    return built[name]["eval_items"]


def test_every_rung_is_500_clean_items(built):
    _build.check_clean(built)


def test_registry_is_the_seventeen():
    assert tuple(sorted(sp.SPECS_6)) == tuple(sorted(gen.RUNG_ORDER_6))
    assert len(gen.RUNG_ORDER_6) == 17
    assert len({s.seed for s in sp.SPECS_6.values()}) == 17
    assert "logic_grid" not in sp.SPECS_6                  # plan delta B-1


def test_generate_writes_what_payload_builds(tmp_path):
    ctx = gen.context()
    r = gen.write("lcs", ctx, out_dir=tmp_path)
    raw = (tmp_path / "lcs.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == r["sha256"]
    assert raw.decode("utf-8") == gen.dumps(gen.payload("lcs", ctx))
    assert set(gen.payload("lcs", ctx)["provenance"]) == \
        {"words_6_sha256", "bigbench_index_sha256", "bigbench_commit", "pyfiglet"}


# ----------------------------------------------------------------- ascii
@pytest.mark.parametrize("name,font", [("ascii_bubble", "bubble"),
                                       ("ascii_basic", "basic")])
def test_ascii(built, name, font):
    items = _items(built, name)
    assert Counter(len(it["answer"]) for it in items) == {3: 125, 4: 125, 5: 125, 6: 125}
    assert len({it["answer"] for it in items}) == 500
    for it in items[::5]:
        head, art = it["question"].split("\n", 1)
        assert head == gen_ascii.ASCII_HEADER
        lines = art.split("\n")
        assert len(lines) >= 4 and " " not in art
        assert all(set(ln) - {"."} for ln in (lines[0], lines[-1]))   # no blank edges
        assert art == gen_ascii.render(it["answer"], font)
    if font == "bubble":                                   # the letters appear
        for it in items[::5]:
            assert all(ch in it["question"].split("\n", 1)[1] for ch in it["answer"])


def test_pyfiglet_is_the_pinned_version():
    from importlib.metadata import version
    assert version("pyfiglet") == gen_ascii.PYFIGLET_VERSION == "1.0.4"


# ---------------------------------------------------------------- shapes
_NUM = r"-?\d+\.\d\d"


def _points(path):
    return [(float(x), float(y)) for x, y in
            re.findall(rf"[ML] ({_NUM}),({_NUM})", path)]


def _vertices(path):
    """The polygon's vertices in order, the pen re-statements and the
    closing point dropped."""
    out = []
    for p in _points(path):
        if not out or p != out[-1]:
            out.append(p)
    assert out[0] == out[-1]
    return out[:-1]


def test_shapes(built):
    items = _items(built, "shapes")
    assert Counter(it["answer"] for it in items) == {c: 50 for c in gen_shapes.SHAPES}
    sides = {"triangle": 3, "rectangle": 4, "kite": 4, "pentagon": 5,
             "hexagon": 6, "heptagon": 7, "octagon": 8}
    for it in items:
        m = re.fullmatch(r'This SVG path element <path d="([^"]+)"/> draws a\n'
                         r"Options: (.+)", it["question"])
        path, opts = m.group(1), m.group(2).split(", ")
        assert sorted(opts) == sorted(gen_shapes.SHAPES)
        assert opts.index(it["answer"]) + 1 == it["meta"]["answer_pos"]
        cls = it["answer"]
        n_l, n_a = path.count("L "), path.count("A ")
        for x, y in _points(path):
            assert 0 <= x <= 100 and 0 <= y <= 100
        if cls in sides:
            assert (n_l, n_a) == (sides[cls], 0)
            v = _vertices(path)
            assert len(v) == sides[cls]
            d = [math.dist(v[i], v[(i + 1) % len(v)]) for i in range(len(v))]
            if cls == "rectangle":
                for i in range(4):
                    a, b, c = v[i], v[(i + 1) % 4], v[(i + 2) % 4]
                    dot = (b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1])
                    assert abs(dot) <= 0.02 * d[i] * d[(i + 1) % 4] + 0.02
                assert abs(d[0] - d[2]) < 0.03 and abs(d[1] - d[3]) < 0.03
            if cls == "kite":
                assert abs(d[0] - d[3]) < 0.03 and abs(d[1] - d[2]) < 0.03
                assert abs(d[0] - d[1]) > 0.5                  # not a rhombus
        elif cls == "line":
            assert (n_l, n_a, path.count("M ")) == (1, 0, 1)
        elif cls == "circle":
            assert (n_l, n_a) == (0, 2)
        elif cls == "sector":
            assert (n_l, n_a) == (2, 1)


# ------------------------------------------------------------- deduction
def _solve(objs, clues):
    out = []
    for p in permutations(objs):
        pos = {o: i + 1 for i, o in enumerate(p)}
        ok = True
        for kind, x, y in clues:
            if kind == "at":
                ok &= pos[x] == y
            elif kind == "before":
                ok &= pos[x] < pos[y]
            else:
                ok &= pos[x] > pos[y]
        if ok:
            out.append(list(p))
    return out


@pytest.mark.parametrize("name,n", [("deduction3", 3), ("deduction5", 5)])
def test_deduction(built, name, n):
    items = _items(built, name)
    assert Counter(it["meta"]["context"] for it in items) == \
        {c["key"]: 100 for c in gen_logic.CONTEXTS}
    for it in items:
        m = it["meta"]
        clues = [tuple(c) for c in m["clues"]]
        sol = _solve(m["listed"], clues)
        assert sol == [m["order"]]                          # unique
        for c in clues:                                     # minimal
            assert len(_solve(m["listed"], [k for k in clues if k != c])) > 1
        assert it["answer"] == m["order"][m["asked"] - 1]
        assert sorted(m["options"]) == sorted(m["listed"]) and len(m["listed"]) == n
        assert m["options"][m["answer_pos"] - 1] == it["answer"]
        assert it["question"].endswith("Options: " + ", ".join(m["options"]))
        paragraph = it["question"].split("\nOptions:")[0].rsplit(" Which ", 1)[0]
        assert paragraph.count(".") == 1 + len(clues)       # intro + one per clue


def test_deduction_sentences_say_what_the_clues_say(built):
    cx = {c["key"]: c for c in gen_logic.CONTEXTS}
    for it in _items(built, "deduction5")[::9]:
        m = it["meta"]
        c = cx[m["context"]]
        body = it["question"].split("\nOptions:")[0]
        for kind, x, y in m["clues"]:
            if kind == "at":
                assert c["position"][5][y - 1] in body
            else:
                rel = c["before"] if kind == "before" else c["after"]
                assert f"{x}" in body and rel in body
        assert c["position"][5][m["asked"] - 1] in body.rsplit(". ", 1)[1]


# -------------------------------------------------------------- temporal
def _hour(s):
    m = re.fullmatch(r"(\d+)(am|pm)", s)
    h = int(m.group(1))
    return h if (m.group(2) == "am" or h == 12) else h + 12


def test_clock():
    assert [gen_logic.clock(h) for h in (5, 11, 12, 13, 22)] == \
        ["5am", "11am", "12pm", "1pm", "10pm"]
    assert [_hour(gen_logic.clock(h)) for h in range(5, 23)] == list(range(5, 23))


def test_temporal(built):
    items = _items(built, "temporal")
    assert Counter(it["meta"]["n_events"] for it in items) == {3: 167, 4: 167, 5: 166}
    for it in items:
        body, opts = it["question"].split("\nOptions: ")
        opts = opts.split(", ")
        lines = body.split("\n")
        wake = _hour(re.fullmatch(r"\w+ woke up at (\w+)\.", lines[2]).group(1))
        close = _hour(re.fullmatch(r"The .+ was closed after (\w+)\.", lines[-2]).group(1))
        busy = []
        for ln in lines[3:-2]:
            m = re.fullmatch(r"\w+ saw \w+ .+ from (\w+) to (\w+)\.", ln)
            busy.append((_hour(m.group(1)), _hour(m.group(2))))
        assert busy == sorted(busy) and all(a < b for a, b in busy)
        edges = [wake] + [h for s in busy for h in s] + [close]
        gaps = [(a, b) for a, b in zip(edges[::2], edges[1::2]) if a != b]
        assert len(gaps) == 1                               # exactly one free span
        a, b = (_hour(x) for x in it["answer"].split(" to "))
        assert (a, b) == gaps[0]
        assert opts.count(it["answer"]) == 1 and len(set(opts)) == 4
        assert opts[it["meta"]["answer_pos"] - 1] == it["answer"]
        wrong = [o for o in opts if o != it["answer"]]
        assert all(tuple(_hour(x) for x in o.split(" to ")) in busy for o in wrong)


# ---------------------------------------------------- the collision keys
def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _key_from_meta(name, it):
    """The key rebuilt from the item's own record."""
    m = it["meta"]
    if name.startswith("ascii"):
        return gen_ascii.ascii_key(m["word"])
    if name == "shapes":
        return gen_shapes.shapes_key(m["path"])
    if name.startswith("deduction"):
        cx = next(c for c in gen_logic.CONTEXTS if c["key"] == m["context"])
        return gen_logic.deduction_paragraph(cx, len(m["listed"]), m["listed"],
                                             m["clues"], surface="bigbench")
    return it["question"].split("\nOptions: ")[0]           # temporal: the text


def test_every_item_key_is_the_renderers(built):
    for name in NAMES_B:
        for it in _items(built, name):
            assert _sha(_key_from_meta(name, it)) == it["bb_sha256"], name


def test_what_a_model_reads_against_the_key(built):
    for name in NAMES_B:
        for it in _items(built, name)[::11]:
            q, key = it["question"].split("\nOptions: ")[0], _key_from_meta(name, it)
            if name.startswith("ascii"):
                assert key == it["answer"] and key not in ("", q)
            elif name == "shapes":
                assert q + " " == key
            elif name == "temporal":
                assert q == key
            else:
                read = q.rsplit(" Which ", 1)[0]
                for ours, theirs in gen_logic.BB_NAME.items():
                    read = re.sub(rf"\b{ours}\b", theirs, read)
                read = re.sub(r"\ban (blue jay|station wagon|motorcyle)\b", r"a \1", read)
                assert read == key


def test_no_item_shows_a_name_the_criterion_would_truncate(built):
    """`blue jay` and `station wagon` are in the key and never in what a
    model reads; BIG-bench's misspelling is corrected there too."""
    for name in ("deduction3", "deduction5"):
        seen = Counter()
        for it in _items(built, name):
            assert not re.search(r"blue jay|station wagon|motorcyle", it["question"])
            seen.update(x for x in it["meta"]["listed"] if x in gen_logic.BB_NAME)
        assert set(seen) == set(gen_logic.BB_NAME)          # all three occur
    with pytest.raises(ValueError):
        gen_logic.deduction_paragraph(gen_logic.CONTEXTS[0], 3, ["red", "blue", "gray"],
                                      [["at", "red", 1]], surface="bb")


def test_the_middle_position_is_named_as_bigbench_names_it():
    by = {c["key"]: c["position"] for c in gen_logic.CONTEXTS}
    assert by["vehicles"][3][1] == "the second-newest"
    assert by["vehicles"][5][2] == "the third-newest"
    assert by["fruits"][3][1] == "the second-most expensive"
    assert by["fruits"][5][2] == "the third-most expensive"
    assert by["books"][5][2] == by["birds"][5][2] == "the third from the left"
    for pos in by.values():
        assert len(set(pos[3])) == 3 and len(set(pos[5])) == 5
