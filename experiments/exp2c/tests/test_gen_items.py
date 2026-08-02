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


def test_generate_base12_digitsum(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("base12_digitsum")
    assert len(d["probe_items"]) >= 1800
    assert len(d["eval_items"]) >= 500
    it = d["probe_items"][0]
    assert set(it) >= {"question", "answer", "probe_label", "basis"}
    # probe_label consistency, via an independent divmod-loop digit-sum
    # (not the production _to_base12), mirroring test_generate_mod17's
    # oracle-consistency check; answer is the full base-12 string.
    for item in d["probe_items"][:50]:
        n = int(item["basis"][0])
        total, m = 0, n
        while m:
            m, r = divmod(m, 12)
            total += r
        assert int(item["probe_label"]) == total % 5
        assert item["answer"] == _to_base12(n)
    # family fields present (design §2 sixth field)
    assert d["family"] == "base_repr" and d["dial_value"] == "digitsum_mod5"
    assert (tmp_path / "base12_digitsum.json").exists()


def test_feasibility_recorded(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("mod17")
    f = d["feasibility"]
    assert f["params"]["min_holdout_values"] == 15
    assert f["params"]["min_val_items"] == 300
    assert set(f["per_seed"]) == {"0", "1", "2", "3", "4"}


def _check_generate_pos_letter(d, tmp_path, name, op):
    assert len(d["probe_items"]) >= 1800
    assert len(d["eval_items"]) >= 500
    it = d["probe_items"][0]
    assert set(it) >= {"question", "answer", "probe_label", "basis"}
    # label consistency recomputed from the question TEXT (i, j) plus the
    # committed basis string S -- string-as-basis (ruling 2026-08-01), so
    # basis[0] must equal the printed string and the label must be its
    # letter at p = ((i op j) mod 6) + 2, interior positions 2-7 only.
    # surface_answer is None: answer == probe_label (letter asked directly).
    for item in d["probe_items"][:50]:
        s = re.search(r"'([a-z]+)'", item["question"]).group(1)
        assert item["basis"] == [s]
        nums = [int(x) for x in re.findall(r"\d+", item["question"])]
        i, j = nums[0], nums[1]
        p = (op(i, j) % 6) + 2
        assert 2 <= p <= 7
        assert item["probe_label"] == s[p - 1]
        assert item["answer"] == item["probe_label"]
    assert d["family"] == "pos_letter"
    assert (tmp_path / f"{name}.json").exists()


def test_generate_letter_sum(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("letter_sum")
    _check_generate_pos_letter(d, tmp_path, "letter_sum",
                               lambda i, j: i + j)
    assert d["dial_value"] == "sum"


def test_generate_letter_prod(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("letter_prod")
    _check_generate_pos_letter(d, tmp_path, "letter_prod",
                               lambda i, j: i * j)
    assert d["dial_value"] == "prod"


def test_pos_letter_split_plan_pins():
    # caesar precedent: the letter label's 26 classes must survive both
    # sides of the per-string holdout -> stratify_by_label=True; otherwise
    # default SplitParams and the default 2000-probe target (proposal §3
    # F3 feasibility block: "default SplitParams(), N_PROBE 2000").
    for name in ("letter_sum", "letter_prod"):
        sp, n_probe = gen_items.SPLIT_PLAN[name]
        assert sp.stratify_by_label is True
        assert sp.holdout_frac == 0.2
        assert n_probe == 2000


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
    "base12_digitsum": lambda q: _to_base12(_ints(q)[0]),
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
    "letter_sum": lambda q: _true_pos_letter(q, lambda i, j: i + j),
    "letter_prod": lambda q: _true_pos_letter(q, lambda i, j: i * j),
}


def _true_pos_letter(q, op):
    # i and j are the first two integers the question prints (the mod-6
    # and +2 constants and the "counting from 1" clause come after).
    s = re.search(r"'([a-z]+)'", q).group(1)
    i, j = _ints(q)[0], _ints(q)[1]
    return s[((op(i, j)) % 6) + 2 - 1]


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
