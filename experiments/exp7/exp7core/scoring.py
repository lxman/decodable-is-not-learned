"""Pure total draw normalizer and exact-rational 2x2 scorer."""
from dataclasses import dataclass
from fractions import Fraction as F
import re
from .contract import ARMS, CAPS, Refusal, integer, require


def normalize(value, kind):
    require(kind in CAPS, "unknown normalization criterion")
    if type(value) is not str:
        return None
    s = value.strip().split("\n")[0].strip().lower().strip(".!?\"' ")
    if kind == "number":
        m = re.search(r"-?\d[\d,]*", s)
        return m.group(0).replace(",", "") if m else s
    if kind == "span":
        return " ".join(s.split())
    parts = s.split()
    return parts[0] if parts else ""


def answer(value, kind):
    got = normalize(value, kind)
    require(bool(got), "empty/nonstring normalized oracle answer")
    whole = " ".join(value.strip().split()).lower().strip(".!?\"' ")
    require(got == whole, "criterion truncates oracle answer")
    return got


@dataclass(frozen=True)
class Table:
    n00: int
    n01: int
    n10: int
    n11: int
    k: int

    def __post_init__(self):
        integer(self.k, 1, 1000000, "draw budget")
        for n in (self.n00, self.n01, self.n10, self.n11):
            integer(n, 0, self.k, "target cell")
        require(self.m0 <= self.k and self.m1 <= self.k, "row exceeds budget")

    @property
    def m0(self):
        return self.n00 + self.n01

    @property
    def m1(self):
        return self.n10 + self.n11

    @property
    def supported(self):
        return self.m0 > 0 and self.m1 > 0

    @property
    def x(self):
        return F(self.n00, self.m0) - F(self.n10, self.m1) if self.supported else F(0)

    def reversed_labels(self):
        return Table(self.n01, self.n00, self.n11, self.n10, self.k)


@dataclass(frozen=True)
class Score:
    canonical: Table
    sham: Table

    def __post_init__(self):
        require(self.canonical.k == self.sham.k, "unequal render budgets")

    @property
    def x(self):
        return (self.canonical.x + self.sham.x) / 2

    @property
    def C(self):
        return sum(t.n00 + t.n11 for t in (self.canonical, self.sham))

    @property
    def W(self):
        return sum(t.n01 + t.n10 for t in (self.canonical, self.sham))

    @property
    def d(self):
        return F(self.C - self.W, 4 * self.canonical.k)

    @property
    def u(self):
        return F(self.C + self.W, 4 * self.canonical.k)

    @property
    def rate(self):
        return F(self.C, 4 * self.canonical.k)

    @property
    def wrong(self):
        return F(self.W, 4 * self.canonical.k)

    @property
    def row_totals(self):
        return (self.canonical.m0, self.canonical.m1, self.sham.m0, self.sham.m1)

    @property
    def unsupported(self):
        return sum(not t.supported for t in (self.canonical, self.sham))

    def reversed_labels(self):
        return Score(self.canonical.reversed_labels(), self.sham.reversed_labels())


def score_draws(draws, targets, kind, *, k):
    require(type(draws) is dict and set(draws) == set(ARMS), "four exact arms")
    require(len(targets) == 2, "two targets")
    a0, a1 = (answer(a, kind) for a in targets)
    require(a0 != a1, "target collision")
    counts = []
    for arm in ARMS:
        row = draws[arm]
        require(type(row) in (list, tuple) and len(row) == k, "exact equal arm coverage")
        require(all(type(v) is str for v in row), "raw draws must be strings")
        norm = [normalize(v, kind) for v in row]
        counts.append((norm.count(a0), norm.count(a1)))
    out = Score(Table(*counts[0], *counts[1], k), Table(*counts[2], *counts[3], k))
    require(out.rate == (out.u + out.d) / 2, "rate identity")
    require(abs(out.d) <= out.u <= 1, "raw range")
    return out


def outcome_counts(rows, targets, kind, *, steps):
    require(type(rows) is dict and set(rows) == set(steps), "complete checkpoint window")
    a0, a1 = (answer(a, kind) for a in targets)
    require(a0 != a1, "target collision")
    bits = []
    for t in steps:
        r = rows[t]
        require(type(r) is dict and set(r) == set(ARMS), "outcome four-arm coverage")
        require(all(type(r[a]) is str for a in ARMS), "outcome raw string")
        bits.append(tuple(int(normalize(r[a], kind) == (a0 if j % 2 == 0 else a1))
                          for j, a in enumerate(ARMS)))
    joint = tuple(b[0] * b[1] for b in bits)
    sham = tuple(b[2] * b[3] for b in bits)
    first = next((i for i, b in enumerate(joint) if b), None)
    return {"bits": tuple(bits), "joint": joint, "sham": sham,
            "y": sum(joint), "y_sham": sum(sham), "first_index": first,
            "first_order_score": 0 if first is None else len(steps) - first,
            "later_losses": 0 if first is None else sum(1 - b for b in joint[first + 1:]),
            "joint_agreement": F(sum(a == b for a, b in zip(joint, sham)), len(steps))}
