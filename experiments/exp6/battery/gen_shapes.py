# experiments/exp6/battery/gen_shapes.py
"""Geometric shapes (BIG-bench geometric_shapes; Wei class E.3): name
the shape an SVG path draws, among BIG-bench's ten classes. BIG-bench's
288 shapes were made by hand and no generator is published; this one is
a RECONSTRUCTION from the README (ten classes, a 100 x 100 box, varied
size and orientation, convex and concave polygons) and from the path
syntax of the task file (M/L/A commands, two decimals, the pen
re-stated with M at some vertices)."""
from __future__ import annotations

import math

from .spec import RungSpec, register, with_options

SHAPES = ("circle", "heptagon", "hexagon", "kite", "line", "octagon",
          "pentagon", "rectangle", "sector", "triangle")
N_SIDES = {"triangle": 3, "pentagon": 5, "hexagon": 6, "heptagon": 7,
           "octagon": 8}
BOX = (0.0, 100.0)
P_RESTATE = 0.3            # chance the pen is re-stated (M x,y) at a vertex
MIN_SIDE = 3.0             # no two consecutive vertices closer than this


def _pt(p) -> str:
    return f"{p[0]:.2f},{p[1]:.2f}"


def _inside(points) -> bool:
    return all(BOX[0] <= c <= BOX[1] for p in points for c in p)


def _spread(points, closed=True) -> bool:
    n = len(points)
    pairs = [(points[i], points[(i + 1) % n]) for i in range(n if closed else n - 1)]
    return all(math.dist(a, b) >= MIN_SIDE for a, b in pairs)


def _rot(p, ang, c):
    x, y = p
    ca, sa = math.cos(ang), math.sin(ang)
    return (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)


def _polyline(rng, verts) -> str:
    """M v0 L v1 ... L v0, the pen re-stated at some vertices."""
    ring = list(verts) + [verts[0]]
    parts = [f"M {_pt(ring[0])}"]
    for i, v in enumerate(ring[1:], start=1):
        parts.append(f"L {_pt(v)}")
        if i < len(ring) - 1 and rng.random() < P_RESTATE:
            parts.append(f"M {_pt(v)}")
    return " ".join(parts)


def _star_polygon(rng, n):
    """A simple polygon, star-shaped about its centre: sorted angles,
    free radii — convex or concave as the radii fall."""
    c = (float(rng.uniform(30, 70)), float(rng.uniform(30, 70)))
    base = 2 * math.pi / n
    start = float(rng.uniform(0, 2 * math.pi))
    angs = [start + i * base + float(rng.uniform(-0.3, 0.3)) * base
            for i in range(n)]
    return [(c[0] + r * math.cos(a), c[1] + r * math.sin(a))
            for a, r in zip(angs, (float(rng.uniform(10, 30)) for _ in range(n)))]


def shape_path(rng, cls: str):
    """(path string, vertices or None). None path = reject the draw."""
    if cls == "line":
        a = (float(rng.uniform(0, 100)), float(rng.uniform(0, 100)))
        b = (float(rng.uniform(0, 100)), float(rng.uniform(0, 100)))
        if math.dist(a, b) < 10:
            return None
        return f"M {_pt(a)} L {_pt(b)}"
    if cls in N_SIDES:
        v = _star_polygon(rng, N_SIDES[cls])
    elif cls == "rectangle":
        w, h = float(rng.uniform(6, 50)), float(rng.uniform(6, 50))
        c = (float(rng.uniform(30, 70)), float(rng.uniform(30, 70)))
        ang = float(rng.uniform(0, math.pi))
        v = [_rot(p, ang, c) for p in ((-w / 2, -h / 2), (w / 2, -h / 2),
                                       (w / 2, h / 2), (-w / 2, h / 2))]
    elif cls == "kite":
        a, cc = float(rng.uniform(6, 18)), float(rng.uniform(20, 36))
        b = float(rng.uniform(6, 20))
        c = (float(rng.uniform(35, 65)), float(rng.uniform(35, 65)))
        ang = float(rng.uniform(0, 2 * math.pi))
        v = [_rot(p, ang, c) for p in ((0, a), (b, 0), (0, -cc), (-b, 0))]
    elif cls == "circle":
        r = float(rng.uniform(8, 30))
        c = (float(rng.uniform(r, 100 - r)), float(rng.uniform(r, 100 - r)))
        t = float(rng.uniform(0, 2 * math.pi))
        p1 = (c[0] + r * math.cos(t), c[1] + r * math.sin(t))
        p2 = (c[0] - r * math.cos(t), c[1] - r * math.sin(t))
        rot = float(rng.uniform(0, 360))
        arc = f"A {r:.2f},{r:.2f} {rot:.2f} 1,0"
        return f"M {_pt(p1)} {arc} {_pt(p2)} {arc} {_pt(p1)}"
    elif cls == "sector":
        r = float(rng.uniform(8, 30))
        c = (float(rng.uniform(r, 100 - r)), float(rng.uniform(r, 100 - r)))
        t1 = float(rng.uniform(0, 2 * math.pi))
        span = math.radians(float(rng.uniform(20, 160)))
        p1 = (c[0] + r * math.cos(t1), c[1] + r * math.sin(t1))
        p2 = (c[0] + r * math.cos(t1 + span), c[1] + r * math.sin(t1 + span))
        if math.dist(p1, p2) < MIN_SIDE:
            return None
        rot = float(rng.uniform(0, 360))
        return (f"M {_pt(c)} L {_pt(p1)} A {r:.2f},{r:.2f} {rot:.2f} 0,1 "
                f"{_pt(p2)} L {_pt(c)}")
    else:
        raise ValueError(cls)
    if not _inside(v) or not _spread(v):
        return None
    return _polyline(rng, v)


def shapes_stem(d: str) -> str:
    return f'This SVG path element <path d="{d}"/> draws a'


def shapes_key(d: str) -> str:
    """BIG-bench's input ends in a space; the question drops it."""
    return shapes_stem(d) + " "


def _draw_shapes(rng, ctx, slot):
    cls = SHAPES[slot % len(SHAPES)]
    d = shape_path(rng, cls)
    if d is None:
        return None
    order = [SHAPES[int(i)] for i in rng.permutation(len(SHAPES))]
    return {"question": with_options(shapes_stem(d), order), "answer": cls,
            "bb_key": shapes_key(d),
            "meta": {"cls": cls, "path": d, "options": order,
                     "answer_pos": order.index(cls) + 1}}


register(RungSpec(
    name="shapes", task="geometric_shapes", wei_class="E.3",
    rung_type="string", answer_type="word", seed=20260914,
    n_options=len(SHAPES),
    description="name the shape an SVG path draws, among ten classes "
                "listed in shuffled order; fifty paths per class; a "
                "reconstruction of BIG-bench's hand-made set",
    draw=_draw_shapes))
