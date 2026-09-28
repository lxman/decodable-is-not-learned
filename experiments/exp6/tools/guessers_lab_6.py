# experiments/exp6/tools/guessers_lab_6.py
"""FITTED guessers on the unit rungs' options: a disclosure, not an
instrument. Nothing imports this file and no pin names it.

`floors_6` scores FIXED rules — what a reader could apply to one item
with no example before it. A fitted model is a different adversary: it
learns, from a few hundred items of a generator, what that generator's
options give away, which no model scored zero- or two-shot can do. Its
held-out score measures how REGULAR the generator is, and the transfer
to BIG-bench's own 25 items a level says whose regularity it is.

Twenty surface features of an option against the numbers its sentence
prints; a logistic regression and a gradient-boosted classifier, fitted
on half the rung (blocks of ten slots) and scored on the other half,
both ways; then fitted on the whole rung and applied to BIG-bench's
items, and the reverse. Needs scikit-learn and BIG-bench's task files
(the index builder's scratch directory).

The twenty features do not know what a READING of the sentence is, and
a fit that cannot find the candidates among the options says little
about them. A second pass adds twenty-one: which combination of the
text's largest number with its other numbers and its scaling factor an
option is, if any. That fit finds the candidates and can learn how
often each kind is the answer; what it cannot learn, if the numbers and
options say nothing of what is asked, is which one to pick.

    python -m experiments.exp6.tools.guessers_lab_6 <scratch dir>
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp6 import battery_6 as b6  # noqa: E402
from experiments.exp6.battery.make_bigbench_index_6 import local_name  # noqa: E402

FACTOR_WORDS = (("twice", 2), ("three times", 3), ("four times", 4), ("half", 2),
                ("one third", 3), ("one fourth", 4), ("one forth", 4))
LEVELS = (("unit_interp1", "unit_interpretation/lv1"),
          ("unit_interp2", "unit_interpretation/lv2"))


def numbers(text: str) -> list:
    return [int(x) for x in re.findall(r"\d+", text)]


def features(text: str, options: list, x: int) -> list:
    t = [v for v in numbers(text) if v > 1]
    k = next((k for w, k in FACTOR_WORDS if w in text), 1)
    ts = t + [k] if k > 1 else t
    return [
        sum(x % v == 0 for v in t), sum(x % v == 0 for v in ts), x in numbers(text),
        any(x == a * b for i, a in enumerate(ts) for b in ts[i + 1:]),
        any(a % x == 0 for a in t), any(x * v in t or x == v * v for v in t),
        math.log(x + 1), math.log((x + 1) / (max(t) + 1)) if t else 0,
        math.log((x + 1) / (min(t) + 1)) if t else 0, sorted(options).index(x),
        sum(math.gcd(x, v) for v in t) / (sum(t) or 1),
        max((math.gcd(x, v) / v for v in t), default=0), x % 10 == 0, x % 2 == 0,
        len(str(x)), any(x % v == 0 and 2 <= x // v <= 48 for v in t),
        options.index(x), any(a % x == 0 for a in ts) and x not in numbers(text),
        sum(1 for y in options if y != x and (y % x == 0 or x % y == 0)),
        sum(1 for y in options if y != x and y in numbers(text))]


def templates(text: str, x: int) -> list:
    """Which combination of the text's numbers the option is: the
    largest number L alone, times or over another number, times or over
    the factor, and their products — twenty-one, in a fixed order."""
    from fractions import Fraction
    t = [v for v in numbers(text) if v > 1]
    if not t:
        return [False] * 21
    top = max(t)
    rest = [v for v in t if v != top][:2]
    a, b = (rest + [None, None])[:2]
    k = next((k for w, k in FACTOR_WORDS if w in text), None)

    def val(*steps):
        v = Fraction(top)
        for f, e in steps:
            if f is None:
                return None
            v *= Fraction(f) ** e
        return v
    each = [(o, e) for o in (a, b) for e in (1, -1)]
    exprs = [val()] + [val(s) for s in each] + [val((k, 1)), val((k, -1))]
    exprs += [val(s, (k, e)) for s in each for e in (1, -1)]
    exprs += [val((a, 1), (b, -1)), val((b, 1), (a, -1))]
    exprs += [val((a, 1), (b, -1), (k, e)) for e in (1, -1)]
    exprs += [val((b, 1), (a, -1), (k, e)) for e in (1, -1)]
    assert len(exprs) == 21
    return [v is not None and v == x for v in exprs]


def aware(text: str, options: list, x: int) -> list:
    return features(text, options, x) + templates(text, x)


def ours(rung: str) -> list:
    out = []
    for it in b6.load_item_file_6(rung)["eval_items"]:
        text, opts = it["question"].split("\nOptions: ")
        out.append((text, [int(o) for o in opts.split(", ")], int(it["answer"])))
    return out


def bigbench(src, path: str) -> list:
    out = []
    for e in json.loads((Path(src) / local_name(path)).read_text())["examples"]:
        opts = [int(k) for k in e["target_scores"]]
        out.append((e["input"], opts,
                    next(int(k) for k, v in e["target_scores"].items() if v)))
    return out


def table(data, feats=features):
    import numpy as np
    X, y, item = [], [], []
    for i, (text, opts, answer) in enumerate(data):
        for x in opts:
            X.append(feats(text, opts, x))
            y.append(x == answer)
            item.append(i)
    return np.array(X, float), np.array(y), np.array(item)


def score(model, data, feats=features) -> float:
    import numpy as np
    X, y, item = table(data, feats)
    p = model.predict_proba(X)[:, 1]
    return float(sum(y[item == i][np.argmax(p[item == i])] for i in np.unique(item))
                 / len(data))


def models() -> dict:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    return {"logistic": lambda: LogisticRegression(max_iter=5000),
            "boosted": lambda: GradientBoostingClassifier(n_estimators=60, max_depth=3,
                                                          random_state=0)}


def held_out(data, make, feats=features) -> float:
    halves = [[d for i, d in enumerate(data) if (i // 10) % 2 == h] for h in (0, 1)]
    hits = 0.0
    for h in (0, 1):
        X, y, _ = table(halves[1 - h], feats)
        hits += score(make().fit(X, y), halves[h], feats) * len(halves[h])
    return hits / len(data)


def leave_one_out(data, make, feats=features) -> float:
    hits = 0.0
    for i in range(len(data)):
        X, y, _ = table(data[:i] + data[i + 1:], feats)
        hits += score(make().fit(X, y), [data[i]], feats)
    return hits / len(data)


def run(src) -> dict:
    out = {}
    for rung, path in LEVELS:
        mine, theirs = ours(rung), bigbench(src, path)
        rows = {}
        for title, feats in (("models", features),
                             ("models, the candidates known", aware)):
            row = {}
            for name, make in models().items():
                X, y, _ = table(mine, feats)
                Xb, yb, _ = table(theirs, feats)
                row[name] = {
                    "held out, on the battery": round(held_out(mine, make, feats), 3),
                    "leave one out, on BIG-bench": round(
                        leave_one_out(theirs, make, feats), 3),
                    "fitted on the battery, applied to BIG-bench": round(
                        score(make().fit(X, y), theirs, feats), 3),
                    "fitted on BIG-bench, applied to the battery": round(
                        score(make().fit(Xb, yb), mine, feats), 3)}
            rows[title] = row
        out[rung] = {"n": len(mine), "n_bigbench": len(theirs), **rows}
    return out


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        raise SystemExit(__doc__)
    print(json.dumps(run(argv[0]), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
