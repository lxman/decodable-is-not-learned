# experiments/exp6/battery/gen_logic.py
"""Choice rungs built on deduction: deduction3 / deduction5 (BIG-bench
logical_deduction; Wei class E.2) and temporal (BIG-bench
temporal_sequences; class E.3).

logical_deduction's generation rule is the README's: a random target
order; true clues drawn from three classes — "X is at position P"
(20 %), "X is before Y" (40 %), "X is after Y" (40 %) — until the order
is uniquely determined; then pruned to a minimal set. The five contexts,
their sentence frames, their position phrases and 47 of their 50 object
names are the task files'. Three names are this battery's: `sparrow`
for the task files' `blue jay` and `wagon` for `station wagon` (a
two-word answer is truncated by the `word` criterion), and `motorcycle`
for the task files' misspelling `motorcyle`.

A paragraph has two SURFACES. "battery" is what a model reads.
"bigbench" puts the task files' three names back and is what the
collision key is built from, so a puzzle BIG-bench already holds is
excluded whichever name it is written with.

temporal_sequences publishes no rule beyond its sentence pattern; the
generator is a RECONSTRUCTION of that pattern from the README's example
and the task file's structure."""
from __future__ import annotations

from itertools import permutations

from .spec import RungSpec, register, with_options

NUMBER_WORD = {3: "three", 5: "five"}
P_POSITION_CLUE = 0.2
MAX_CLUE_DRAWS = 200

# position phrases, index 0 = position 1 (leftmost / first / oldest / cheapest)
_LEFT = {3: ("the leftmost", "the second from the left", "the rightmost"),
         5: ("the leftmost", "the second from the left", "the third from the left",
             "the second from the right", "the rightmost")}
_RANK = {3: ("first", "second", "last"),
         5: ("first", "second", "third", "second-to-last", "last")}
# the task files name the MIDDLE position from the far end in these two
_AGE = {3: ("the oldest", "the second-newest", "the newest"),
        5: ("the oldest", "the second-oldest", "the third-newest",
            "the second-newest", "the newest")}
_PRICE = {3: ("the cheapest", "the second-most expensive", "the most expensive"),
          5: ("the cheapest", "the second-cheapest", "the third-most expensive",
              "the second-most expensive", "the most expensive")}
BB_NAME = {"sparrow": "blue jay", "wagon": "station wagon",
           "motorcycle": "motorcyle"}
SURFACES = ("battery", "bigbench")

CONTEXTS = (
    {"key": "books", "intro": "On a shelf, there are {n} books: {list}.",
     "noun": "book", "names": ("red", "green", "blue", "orange", "yellow",
                               "purple", "black", "white", "brown", "gray"),
     "phrase": "{name} book", "article": True, "subject": "The {obj}",
     "be": "is", "before": "to the left of", "after": "to the right of",
     "position": _LEFT, "ask": "Which book is {pos}?"},
    {"key": "birds", "intro": "On a branch, there are {n} birds: {list}.",
     "noun": "bird", "names": ("robin", "crow", "owl", "hawk", "falcon",
                               "raven", "quail", "cardinal", "hummingbird",
                               "sparrow"),
     "phrase": "{name}", "article": True, "subject": "The {obj}",
     "be": "is", "before": "to the left of", "after": "to the right of",
     "position": _LEFT, "ask": "Which bird is {pos}?"},
    {"key": "golfers",
     "intro": "In a golf tournament, there were {n} golfers: {list}.",
     "noun": "golfer", "names": ("Amy", "Ana", "Ada", "Dan", "Eli", "Eve",
                                 "Joe", "Mel", "Mya", "Rob"),
     "phrase": "{name}", "article": False, "subject": "{obj}",
     "be": "finished", "before": "above", "after": "below",
     "position": _RANK, "ask": "Which golfer finished {pos}?"},
    {"key": "vehicles",
     "intro": "In an antique car show, there are {n} vehicles: {list}.",
     "noun": "vehicle", "names": ("bus", "convertible", "hatchback",
                                  "limousine", "minivan", "motorcycle",
                                  "sedan", "tractor", "truck", "wagon"),
     "phrase": "{name}", "article": True, "subject": "The {obj}",
     "be": "is", "before": "older than", "after": "newer than",
     "position": _AGE, "ask": "Which vehicle is {pos}?"},
    {"key": "fruits", "intro": "A fruit stand sells {n} fruits: {list}.",
     "noun": "fruit", "names": ("apples", "cantaloupes", "kiwis", "loquats",
                                "mangoes", "oranges", "peaches", "pears",
                                "plums", "watermelons"),
     "phrase": "{name}", "article": False, "subject": "The {obj}",
     "be": "are", "before": "less expensive than", "after": "more expensive than",
     "position": _PRICE, "ask": "Which fruit is {pos}?"},
)


def _article(word: str) -> str:
    return "an" if word[0].lower() in "aeiou" else "a"


def _listing(items) -> str:
    return ", ".join(items[:-1]) + ", and " + items[-1]


def consistent(order, clue) -> bool:
    """`order[i]` is the object at position i+1; a clue is
    ("at", x, p) | ("before", x, y) | ("after", x, y)."""
    kind, x, y = clue
    pos = {o: i + 1 for i, o in enumerate(order)}
    if kind == "at":
        return pos[x] == y
    if kind == "before":
        return pos[x] < pos[y]
    return pos[x] > pos[y]


def solutions(objects, clues) -> list:
    return [p for p in permutations(objects)
            if all(consistent(p, c) for c in clues)]


def minimal_clues(rng, target) -> list:
    """The README's procedure: add true clues until unique, then drop
    every clue the puzzle stays unique without."""
    objs = list(target)
    clues = []
    for _ in range(MAX_CLUE_DRAWS):
        if rng.random() < P_POSITION_CLUE:
            x = objs[int(rng.integers(len(objs)))]
            clue = ("at", x, target.index(x) + 1)
        else:
            i, j = (int(v) for v in rng.choice(len(objs), size=2, replace=False))
            x, y = objs[i], objs[j]
            kind = "before" if rng.random() < 0.5 else "after"
            if consistent(target, (kind, x, y)):
                clue = (kind, x, y)
            else:
                clue = (kind, y, x)
        if clue in clues:
            continue
        clues.append(clue)
        if len(solutions(objs, clues)) == 1:
            break
    else:
        return []
    kept = list(clues)
    for c in list(clues):
        rest = [k for k in kept if k != c]
        if len(solutions(objs, rest)) == 1:
            kept = rest
    return kept


def puzzle_key(context: str, objects, clues, asked: int) -> str:
    """A puzzle as a QUESTION: the context, the objects, the clues as a
    set — "x after y" read as "y before x" — and the position asked.
    The order the intro lists the objects in, the order of the clues and
    the direction a clue is worded in are surface."""
    norm = sorted({("before", y, x) if k == "after" else (k, x, y)
                   for k, x, y in (tuple(c) for c in clues)}, key=str)
    return "|".join([context, ",".join(sorted(objects)),
                     ";".join(f"{k}:{x}:{y}" for k, x, y in norm), str(asked)])


def _namer(surface: str):
    if surface not in SURFACES:
        raise ValueError(f"surface {surface!r} is not one of {SURFACES}")
    if surface == "bigbench":
        return lambda x: BB_NAME.get(x, x)
    return lambda x: x


def _clue_text(cx, n, clue, name=lambda x: x) -> str:
    kind, x, y = clue
    sx = cx["subject"].format(obj=cx["phrase"].format(name=name(x)))
    if kind == "at":
        return f"{sx} {cx['be']} {cx['position'][n][y - 1]}."
    rel = cx["before"] if kind == "before" else cx["after"]
    oy = cx["phrase"].format(name=name(y))
    oy = oy if cx["key"] == "golfers" else f"the {oy}"
    return f"{sx} {cx['be']} {rel} {oy}."


def deduction_paragraph(cx, n: int, listed, clues, *, surface: str = "battery") -> str:
    """The intro sentence (objects in `listed` order) and one sentence per
    clue, in order."""
    name = _namer(surface)
    phrases = [cx["phrase"].format(name=name(x)) for x in listed]
    if cx["article"]:
        phrases = [f"{_article(p)} {p}" for p in phrases]
    intro = cx["intro"].format(n=NUMBER_WORD[n], list=_listing(phrases))
    return " ".join([intro] + [_clue_text(cx, n, tuple(c), name) for c in clues])


def _draw_deduction(n):
    def draw(rng, ctx, slot):
        cx = CONTEXTS[slot % len(CONTEXTS)]
        answer_pos = (slot // len(CONTEXTS)) % n + 1
        idx = rng.choice(len(cx["names"]), size=n, replace=False)
        listed = [cx["names"][int(i)] for i in idx]          # intro order
        target = [listed[int(i)] for i in rng.permutation(n)]
        clues = minimal_clues(rng, target)
        if not clues:
            return None
        paragraph = deduction_paragraph(cx, n, listed, clues)
        q = int(rng.integers(n)) + 1                          # position asked
        answer = target[q - 1]
        others = [x for x in listed if x != answer]
        others = [others[int(i)] for i in rng.permutation(len(others))]
        opts = others[:answer_pos - 1] + [answer] + others[answer_pos - 1:]
        ask = cx["ask"].format(pos=cx["position"][n][q - 1])
        return {"question": with_options(f"{paragraph} {ask}", opts),
                "answer": answer,
                "bb_key": deduction_paragraph(cx, n, listed, clues,
                                              surface="bigbench"),
                "question_key": puzzle_key(cx["key"], listed, clues, q),
                # the same objects in the same order, the same position
                # asked: the same answer, whatever the clues
                "content_key": f"{cx['key']}|{'>'.join(target)}|{q}",
                "meta": {"context": cx["key"], "listed": listed,
                         "order": target, "clues": [list(c) for c in clues],
                         "n_clues": len(clues), "asked": q, "options": opts,
                         "answer_pos": answer_pos,
                         "stated": any(c[0] == "at" and c[2] == q for c in clues)}}
    return draw


# -------------------------------------------------------------- temporal
T_NAMES = ("Susan", "Emily", "James", "Jason", "Elizabeth", "Ashley", "Sarah",
           "Leslie", "Richard", "Hannah", "Betty", "Sean", "Jessica", "Lisa",
           "Tiffany", "Linda", "William", "Andrew", "David", "Samantha",
           "Anthony", "Michael", "Mark", "Thomas", "Nancy", "Kimberly",
           "Jennifer", "Steven", "Mary", "John")
T_PLACES = ("coffee shop", "soccer field", "restaurant", "beach", "movies",
            "amusement park", "bookstore", "construction site",
            "orchestra hall", "art studio", "clothing store",
            "physics classroom", "park", "art show", "basketball court",
            "football field", "market", "gas station", "bakery",
            "swimming pool", "dance studio", "museum", "library")
T_ACTIVITIES = ("driving to the water park", "buying clothes at the mall",
                "taking photos near the Eiffel Tower",
                "buying lunch at the deli", "reading at the library",
                "waiting at the train station",
                "fixing their computer at the electronic store",
                "walking towards the Statue of Liberty",
                "taking photos near the Leaning Tower of Pisa",
                "buying cookies at a bakery", "working at the office",
                "waiting at the airport", "getting a coffee at the cafe",
                "buying a phone at the electronics store",
                "working out at the gym", "watching a movie at the theater",
                "stretching at a yoga studio", "buying a bike at the bike shop",
                "attending class at the school", "walking in the garden",
                "sitting on a rooftop", "playing tennis at the tennis court")
T_EVENTS = (3, 4, 5)
T_HOURS = (5, 22)                 # 5am .. 10pm
T_OPTIONS = 4


def clock(h: int) -> str:
    if not 1 <= h <= 23:
        raise ValueError(h)
    if h < 12:
        return f"{h}am"
    return "12pm" if h == 12 else f"{h - 12}pm"


def temporal_text(name: str, place: str, wake: int, sightings, closed: int) -> str:
    """BIG-bench's input. `sightings` are (witness, activity, from hour,
    to hour) in order; the collision key is this text."""
    lines = [f"Today, {name} went to the {place}. Between what times could "
             f"they have gone?", "We know that: ",
             f"{name} woke up at {clock(wake)}."]
    lines += [f"{w} saw {name} {a} from {clock(s)} to {clock(e)}."
              for w, a, s, e in sightings]
    lines += [f"The {place} was closed after {clock(closed)}.",
              f"Between what times could {name} have gone to the {place}?"]
    return "\n".join(lines)


def _draw_temporal(rng, ctx, slot):
    n = T_EVENTS[slot % len(T_EVENTS)]
    answer_pos = (slot // len(T_EVENTS)) % T_OPTIONS + 1
    hours = sorted(int(h) for h in rng.choice(
        range(T_HOURS[0], T_HOURS[1] + 1), size=n + 2, replace=False))
    spans = list(zip(hours, hours[1:]))                     # n + 1 intervals
    free = int(rng.integers(n + 1))
    people = [T_NAMES[int(i)] for i in rng.choice(len(T_NAMES), size=n + 1,
                                                  replace=False)]
    name, witnesses = people[0], people[1:]
    acts = [T_ACTIVITIES[int(i)] for i in rng.choice(len(T_ACTIVITIES), size=n,
                                                     replace=False)]
    place = T_PLACES[int(rng.integers(len(T_PLACES)))]
    events = [s for i, s in enumerate(spans) if i != free]
    text = temporal_text(name, place, hours[0],
                         [(w, a, s[0], s[1])
                          for w, a, s in zip(witnesses, acts, events)],
                         hours[-1])
    span = lambda s: f"{clock(s[0])} to {clock(s[1])}"
    answer = span(spans[free])
    wrong = [span(events[int(i)]) for i in rng.choice(len(events),
                                                      size=T_OPTIONS - 1,
                                                      replace=False)]
    opts = wrong[:answer_pos - 1] + [answer] + wrong[answer_pos - 1:]
    where = "first" if free == 0 else ("last" if free == n else "middle")
    schedule = "-".join(str(h) for h in hours) + f"|{free}"
    return {"question": with_options(text, opts), "answer": answer,
            "bb_key": text,
            # the hours and the free interval are the question; the
            # names, the place and the activities are surface
            "question_key": schedule, "content_key": schedule,
            "meta": {"n_events": n, "hours": hours, "free": free,
                     "free_position": where, "options": opts,
                     "answer_pos": answer_pos}}


for _n, _seed in ((3, 20260915), (5, 20260916)):
    register(RungSpec(
        name=f"deduction{_n}", task="logical_deduction", wei_class="E.2",
        rung_type="choice", answer_type="word", seed=_seed, n_options=_n,
        description=f"{NUMBER_WORD[_n]} objects in a fixed order, a minimal "
                    f"set of clues that determines it, one position asked; "
                    f"the {NUMBER_WORD[_n]} objects listed as options",
        draw=_draw_deduction(_n)))
register(RungSpec(
    name="temporal", task="temporal_sequences", wei_class="E.3",
    rung_type="choice", answer_type="span", seed=20260917, n_options=T_OPTIONS,
    description="a person's day as consecutive witnessed intervals with one "
                "interval unaccounted for; name it; four intervals listed; "
                "a reconstruction of BIG-bench's sentence pattern",
    draw=_draw_temporal))
