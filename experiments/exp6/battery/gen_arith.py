# experiments/exp6/battery/gen_arith.py
"""Arithmetic rungs: modarith_add1 / sub1 / mul1 (BIG-bench
modified_arithmetic, the three `plus_one` subtasks; Wei class E.2) and
lcs (BIG-bench cs_algorithms/lcs; class E.3)."""
from __future__ import annotations

from .spec import RungSpec, register

MODARITH_HEADER = ("In the following lines, the symbol -> represents a simple "
                   "mathematical operation.")
N_EXAMPLES = 5                      # BIG-bench: five examples, then the query
MODARITH = {                        # name -> (symbol, operand bound, op)
    "modarith_add1": ("+", 1000, lambda a, b: a + b + 1),
    "modarith_sub1": ("-", 1000, lambda a, b: a - b + 1),
    "modarith_mul1": ("*", 100, lambda a, b: a * b + 1),
}
LCS_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LCS_LEN = (4, 31)                   # BIG-bench's observed string lengths
LCS_CLASSES = tuple(range(10))      # answers 0..9, balanced, as BIG-bench's are
LCS_HEADER = ("Given two strings, determine the length of the longest common "
              "subsequence.")


def modarith_text(name: str, pairs) -> str:
    """BIG-bench's prompt: the header, the worked lines, the query line
    (the last pair, its result withheld). The collision key is this text."""
    sym, _, op = MODARITH[name]
    lines = [MODARITH_HEADER]
    lines += [f"{a} {sym} {b} -> {op(a, b)}" for a, b in pairs[:-1]]
    a, b = pairs[-1]
    lines.append(f"{a} {sym} {b} ->")
    return "\n".join(lines)


def modarith_query(name: str, a: int, b: int) -> str:
    """The query line alone. A second collision key: a prompt that asks
    a pair BIG-bench asks, or prints beside its result on a worked line,
    is a new string under other worked lines and the same question."""
    return f"{a} {MODARITH[name][0]} {b} ->"


def lcs_key(a: str, b: str) -> str:
    """BIG-bench's lcs input is the two strings and nothing else."""
    return f"{a} {b}"


def _draw_modarith(name):
    _, bound, op = MODARITH[name]

    def draw(rng, ctx, slot):
        pairs = []
        while len(pairs) < N_EXAMPLES + 1:
            ab = (int(rng.integers(bound)), int(rng.integers(bound)))
            if ab not in pairs:
                pairs.append(ab)
        a, b = pairs[-1]
        text = modarith_text(name, pairs)
        return {"question": text, "answer": str(op(a, b)), "bb_key": text,
                "bb_extra": [modarith_query(name, a, b)],
                "meta": {"a": a, "b": b, "examples": [list(p) for p in pairs[:-1]]}}
    return draw


def lcs_length(a: str, b: str) -> int:
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, start=1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


def _draw_lcs(rng, ctx, slot):
    """The two lengths are drawn WITHOUT regard to the answer, uniform
    on BIG-bench's range, and the draw is kept only if its answer is the
    slot's. The answer still follows the lengths — a longer pair has a
    longer common subsequence — but no more than it does in BIG-bench's
    own 320 items (the first build drew the lengths from a window set by
    the answer, and a length-only guesser scored .47 against BIG-bench's
    .22 to .28)."""
    target = LCS_CLASSES[slot % len(LCS_CLASSES)]
    lo, hi = LCS_LEN
    la, lb = int(rng.integers(lo, hi + 1)), int(rng.integers(lo, hi + 1))
    a = "".join(LCS_ALPHABET[int(i)] for i in rng.integers(26, size=la))
    b = "".join(LCS_ALPHABET[int(i)] for i in rng.integers(26, size=lb))
    if lcs_length(a, b) != target:
        return None
    return {"question": f"{LCS_HEADER}\nStrings: {lcs_key(a, b)}",
            "answer": str(target), "bb_key": lcs_key(a, b),
            "meta": {"a": a, "b": b, "lcs": target}}


for _name, _what in (("modarith_add1", "a + b + 1, operands uniform on [0, 1000)"),
                     ("modarith_sub1", "a - b + 1, operands uniform on [0, 1000); "
                                       "negative answers occur"),
                     ("modarith_mul1", "a * b + 1, operands uniform on [0, 100)")):
    register(RungSpec(
        name=_name, task="modified_arithmetic", wei_class="E.2",
        rung_type="arithmetic", answer_type="number",
        seed={"modarith_add1": 20260906, "modarith_sub1": 20260907,
              "modarith_mul1": 20260908}[_name],
        description=f"infer a modified operation from five in-prompt "
                    f"examples and apply it to a sixth: {_what}",
        draw=_draw_modarith(_name)))
register(RungSpec(
    name="lcs", task="cs_algorithms", wei_class="E.3",
    rung_type="arithmetic", answer_type="number", seed=20260909,
    description="length of the longest common subsequence of two random "
                "uppercase strings, each 4-31 letters long whatever the "
                "answer; answers 0-9 balanced fifty each by rejection",
    draw=_draw_lcs))
