# experiments/exp6/tests/test_generators_b_6.py
"""ASCII, shapes, deduction and temporal rungs, each checked against an
INDEPENDENT recomputation."""
import hashlib
import math
import re
from collections import Counter
from itertools import permutations

import pytest

from experiments.exp6.battery import gen_ascii, gen_logic, gen_shapes
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


def _turns(v):
    """Degrees the path turns by at each vertex (0 = straight on)."""
    out = []
    for i in range(len(v)):
        a, b, c = v[i - 1], v[i], v[(i + 1) % len(v)]
        h1 = math.atan2(b[1] - a[1], b[0] - a[0])
        h2 = math.atan2(c[1] - b[1], c[0] - b[0])
        d = abs(math.degrees(h2 - h1)) % 360
        out.append(min(d, 360 - d))
    return out


def test_every_polygon_has_the_corners_its_name_counts(built):
    """A vertex the path barely turns at draws no corner: the figure
    would read as the class one vertex down. None is nearer to straight
    than 15 degrees (the first build admitted 113 of 350 within 15)."""
    sides = {"triangle": 3, "rectangle": 4, "kite": 4, "pentagon": 5,
             "hexagon": 6, "heptagon": 7, "octagon": 8}
    seen = 0
    for it in _items(built, "shapes"):
        if it["answer"] not in sides:
            continue
        v = _vertices(it["meta"]["path"])
        assert len(v) == sides[it["answer"]]
        assert min(_turns(v)) >= 15.0 - 1e-6, (it["answer"], min(_turns(v)))
        seen += 1
    assert seen == 350
    assert gen_shapes.MIN_TURN_DEG == 15.0
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert [round(t, 6) for t in gen_shapes.turns(square)] == [90.0] * 4
    flat = [(0.0, 0.0), (10.0, 0.0), (20.0, 0.5), (10.0, 10.0)]
    assert round(min(gen_shapes.turns(flat)), 2) == round(min(_turns(flat)), 2) < 3.0


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
def test_no_deduction_shot_gives_an_item_away(built, name, n):
    """The same objects in the same order and the same position asked:
    the same answer, whatever the clues. No shot is such a twin of an
    eval item (the driver's gate); eval items may be."""
    def key(m):
        return m["context"], tuple(m["order"]), m["asked"]
    items = {key(it["meta"]) for it in _items(built, name)}
    assert not {key(r["meta"]) for r in built[name]["shot_records"]} & items
    import numpy as np
    draw = gen_logic._draw_deduction(n)
    for seed in range(40):
        d = draw(np.random.default_rng(seed), None, seed)
        if d is not None:
            m = d["meta"]
            assert d["content_key"] == f"{m['context']}|{'>'.join(m['order'])}|{m['asked']}"
            assert "question_key" not in d and "shows" not in d


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


# What each clue must SAY, written from English and not from the
# generator's tables: position 1 is the leftmost / first / oldest /
# cheapest, and "before" puts x nearer position 1 than y.
_SAYS = {
    "books": ("The {x} book is to the left of the {y} book.",
              "The {x} book is to the right of the {y} book.", "The {x} book is {p}."),
    "birds": ("The {x} is to the left of the {y}.",
              "The {x} is to the right of the {y}.", "The {x} is {p}."),
    "golfers": ("{x} finished above {y}.", "{x} finished below {y}.",
                "{x} finished {p}."),
    "vehicles": ("The {x} is older than the {y}.", "The {x} is newer than the {y}.",
                 "The {x} is {p}."),
    "fruits": ("The {x} are less expensive than the {y}.",
               "The {x} are more expensive than the {y}.", "The {x} are {p}."),
}
_SHELF = {3: ("the leftmost", "the second from the left", "the rightmost"),
          5: ("the leftmost", "the second from the left", "the third from the left",
              "the second from the right", "the rightmost")}
_PLACES = {
    "books": _SHELF, "birds": _SHELF,
    "golfers": {3: ("first", "second", "last"),
                5: ("first", "second", "third", "second-to-last", "last")},
    "vehicles": {3: ("the oldest", "the second-newest", "the newest"),
                 5: ("the oldest", "the second-oldest", "the third-newest",
                     "the second-newest", "the newest")},
    "fruits": {3: ("the cheapest", "the second-most expensive", "the most expensive"),
               5: ("the cheapest", "the second-cheapest", "the third-most expensive",
                   "the second-most expensive", "the most expensive")},
}
_ASKS = {"books": "Which book is {p}?", "birds": "Which bird is {p}?",
         "golfers": "Which golfer finished {p}?", "vehicles": "Which vehicle is {p}?",
         "fruits": "Which fruit is {p}?"}


def _said(context, n, clue):
    kind, x, y = clue
    before, after, at = _SAYS[context]
    if kind == "at":
        return at.format(x=x, p=_PLACES[context][n][y - 1])
    return (before if kind == "before" else after).format(x=x, y=y)


@pytest.mark.parametrize("name,n", [("deduction3", 3), ("deduction5", 5)])
def test_every_sentence_says_what_its_clue_means(built, name, n):
    """The text a model reads, sentence by sentence, against the clue
    the answer was computed from. A relation rendered the wrong way
    round would leave every puzzle internally consistent and every
    answer wrong; this is the test that would see it."""
    for it in _items(built, name):
        m = it["meta"]
        body = it["question"].split("\nOptions:")[0]
        paragraph, ask = body.rsplit(" Which ", 1)
        sentences = paragraph.split(". ")
        assert len(sentences) == 1 + len(m["clues"])
        for sent, clue in zip(sentences[1:], m["clues"]):
            assert sent.rstrip(".") + "." == _said(m["context"], n, clue)
        assert "Which " + ask == _ASKS[m["context"]].format(
            p=_PLACES[m["context"]][n][m["asked"] - 1])
        listed = sentences[0].split(": ", 1)[1]
        for x in m["listed"]:
            assert x in listed


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
