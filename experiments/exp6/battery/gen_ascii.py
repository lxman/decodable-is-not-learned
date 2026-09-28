# experiments/exp6/battery/gen_ascii.py
"""ASCII word recognition (BIG-bench ascii_word_recognition; Wei class
E.3): a word drawn in a figlet font, spaces replaced by periods as
BIG-bench does. Two of BIG-bench's five fonts: `bubble` (the letters
appear in the art) and `basic` (the letters are built from other
characters). No word of BIG-bench's own 1,000 is used: a figlet
rendering is deterministic, so the same word in the same font would
reproduce BIG-bench's string."""
from __future__ import annotations

from importlib.metadata import version

from . import words_6 as w6
from .spec import RungSpec, register

PYFIGLET_VERSION = "1.0.4"
ASCII_LENGTHS = (3, 4, 5, 6)
ASCII_HEADER = "What word is displayed in the ASCII art below?"
FIGLET_WIDTH = 200


def render(word: str, font: str) -> str:
    import pyfiglet
    if version("pyfiglet") != PYFIGLET_VERSION:
        raise RuntimeError(f"pyfiglet {version('pyfiglet')} installed, pinned "
                           f"{PYFIGLET_VERSION}")
    art = pyfiglet.figlet_format(word, font=font, width=FIGLET_WIDTH)
    lines = art.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        raise ValueError(f"{word!r} renders to nothing in {font!r}")
    return "\n".join(ln.replace(" ", ".") for ln in lines)


def ascii_key(word: str) -> str:
    """The gate is on the TARGET: the word itself, as BIG-bench spells it."""
    return word


def _draw_ascii(font):
    def draw(rng, ctx, slot):
        n = ASCII_LENGTHS[slot % len(ASCII_LENGTHS)]
        pool = ctx["ascii_by_len"][n]
        word = pool[int(rng.integers(len(pool)))]
        return {"question": f"{ASCII_HEADER}\n{render(word, font)}",
                "answer": word, "bb_key": ascii_key(word),
                "meta": {"word": word, "length": n, "font": font,
                         "rank": ctx["rank"][word]}}
    return draw


def context() -> dict:
    v = w6.vocab()
    return {"rank": v["rank"],
            "ascii_by_len": w6.by_length(v["v10"], ASCII_LENGTHS[0],
                                         ASCII_LENGTHS[-1])}


register(RungSpec(
    name="ascii_bubble", task="ascii_word_recognition", wei_class="E.3",
    rung_type="string", answer_type="word", seed=20260912,
    collision_kind="target", unique_answers=True,
    description="read a 3-6 letter word drawn in figlet's `bubble` font "
                "(the letters appear in the art)",
    draw=_draw_ascii("bubble")))
register(RungSpec(
    name="ascii_basic", task="ascii_word_recognition", wei_class="E.3",
    rung_type="string", answer_type="word", seed=20260913,
    collision_kind="target", unique_answers=True,
    description="read a 3-6 letter word drawn in figlet's `basic` font "
                "(the letters are built from other characters)",
    draw=_draw_ascii("basic")))
