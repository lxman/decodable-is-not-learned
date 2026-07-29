import json
import math
import re
from pathlib import Path

from experiments.exp2c.battery import gen_items
from experiments.exp2c.battery.base import SPECS


def test_generate_mod17(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("mod17")
    assert len(d["probe_items"]) >= 1800
    assert len(d["eval_items"]) >= 500
    it = d["probe_items"][0]
    assert set(it) >= {"question", "answer", "probe_label", "basis"}
    # oracle consistency on every item
    for item in d["probe_items"][:50]:
        a = int(item["basis"][0])
        assert int(item["probe_label"]) == a % 17
    # family fields present (design §2 sixth field)
    assert d["family"] == "modulus" and d["dial_value"] == 17
    assert (tmp_path / "mod17.json").exists()


def test_feasibility_recorded(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("mod17")
    f = d["feasibility"]
    assert f["params"]["min_holdout_values"] == 15
    assert f["params"]["min_val_items"] == 300
    assert set(f["per_seed"]) == {"0", "1", "2", "3", "4"}


# --------------------------------------------------------------------------
# Committed-items answer verification (review fix 2026-07-29, Fix A ruling).
# The original generation stored the PROBE LABEL as `answer` for the 9
# specs whose question text demands the full task result. This test is the
# one that would have caught it: it reads the COMMITTED items/*.json and
# independently recomputes the TRUE answer from the question TEXT alone
# (2b's oracle discipline -- generators.py oracles never see the
# generator's variables), failing on any mismatch, over the shots plus the
# first 25 probe and 25 eval items of every registered spec.

_ITEMS = Path(__file__).parent.parent / "battery" / "items"
_AB = "abcdefghijklmnopqrstuvwxyz"
_ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def _ints(q):
    return [int(x) for x in re.findall(r"\d+", q)]


def _unshift(s, k):
    return "".join(_AB[(_AB.index(c) - k) % 26] for c in s)


def _from_roman(s):
    total = 0
    for a, b in zip(s, s[1:] + " "):
        v = _ROMAN[a]
        total += -v if b in _ROMAN and _ROMAN[b] > v else v
    return total


def _to_base12(n):
    digits, out = "0123456789AB", ""
    while n:
        out, n = digits[n % 12] + out, n // 12
    return out or "0"


def _collatz(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1


def _true_sub_base8(q):
    m = re.search(r"What is (\d+) - (\d+)", q)
    return format(int(m.group(1), 8) - int(m.group(2), 8), "o")


def _true_clock24(q):
    d = int(re.search(r"it (\d+) hours", q).group(1))
    h = int(re.search(r"hour (\d+)\?", q).group(1))
    return str((h + d) % 24)


def _true_count_div13(q):
    m = re.search(r"range (\d+) to (\d+)", q)
    a, b = int(m.group(1)), int(m.group(2))
    return str(b // 13 - (a - 1) // 13)


def _true_isqrt_gap(q):
    n = int(re.search(r"N = (\d+)", q).group(1))
    return str((n - math.isqrt(n) ** 2) % 7)


TRUE_ANSWER = {
    "add4_mid": lambda q: str(_ints(q)[0] + _ints(q)[1]),
    "sub4_mid": lambda q: str(_ints(q)[0] - _ints(q)[1]),
    "base12": lambda q: _to_base12(_ints(q)[0]),
    "sub_base8": _true_sub_base8,
    "mod17": lambda q: str((_ints(q)[0] + _ints(q)[1]) % 17),
    "mod19": lambda q: str((_ints(q)[0] + _ints(q)[1]) % 19),
    "mod13_comp": lambda q: str(
        ((_ints(q)[0] + _ints(q)[1]) * _ints(q)[2]) % 13),
    "caesar_len8": lambda q: _unshift(
        re.search(r"'([a-z]+)'", q).group(1),
        int(re.search(r"forward by (\d)", q).group(1))),
    "count_div13": _true_count_div13,
    "clock24_d999": _true_clock24,
    "rev_string7": lambda q: re.search(r"'([a-z]+)'", q).group(1)[::-1],
    "roman_sum7": lambda q: str(sum(
        _from_roman(r) for r in re.findall(r"\b[IVXLC]+\b", q)) % 7),
    "collatz_step2": lambda q: str(_collatz(_collatz(
        int(re.search(r"twice to (\d+)", q).group(1)))) % 7),
    "isqrt_gap": _true_isqrt_gap,
}


def test_true_answer_covers_every_registered_spec():
    assert set(TRUE_ANSWER) == set(SPECS)


def test_committed_answers_are_true_answers():
    for name, recompute in TRUE_ANSWER.items():
        d = json.loads((_ITEMS / f"{name}.json").read_text())
        sample = ([tuple(s) for s in d["shots"]]
                  + [(it["question"], it["answer"])
                     for it in d["probe_items"][:25]]
                  + [(it["question"], it["answer"])
                     for it in d["eval_items"][:25]])
        for q, a in sample:
            true = recompute(q)
            assert true == a, (f"{name}: {q!r} -> stored answer {a!r}, "
                               f"true answer {true!r}")
