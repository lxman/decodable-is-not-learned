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


# Label-tail ruling 2026-08-02 (Michael: follow the recommendation): the
# 2026-08-02 infeasibility catch (frozen starving_split demands full
# class coverage; Binomial tails can't supply it) is resolved by
# rejection-sampling the tail at generation -- cap 5 for L=8 (labels
# 0-5 exact), cap 7 for L=12 (labels 0-7 exact). The blocked-pin test
# that recorded the catch is superseded by real generation checks.
def _check_generate_hamming(d, tmp_path, name, L, cap):
    assert len(d["probe_items"]) >= 3600
    assert len(d["eval_items"]) >= 500
    # label recomputed from the two quoted strings in the question text;
    # basis is BOTH strings (shared_components split); answer == label
    # (the question asks for the count directly, surface_answer None)
    for item in d["probe_items"][:50]:
        s1, s2 = re.findall(r"'([a-d]+)'", item["question"])
        assert len(s1) == L and len(s2) == L
        assert item["basis"] == [s1, s2]
        true = sum(a == b for a, b in zip(s1, s2))
        assert item["probe_label"] == str(true)
        assert item["answer"] == item["probe_label"]
    # the ruled cap holds over the WHOLE committed file, not just the
    # spot-checked prefix
    labels = {int(it["probe_label"])
              for grp in ("probe_items", "eval_items") for it in d[grp]}
    assert labels <= set(range(cap + 1)), (name, labels)
    assert d["family"] == "str_align"
    assert d["dial_value"] == L
    assert (tmp_path / f"{name}.json").exists()


def test_generate_hamming8(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("hamming8")
    _check_generate_hamming(d, tmp_path, "hamming8", 8, 5)


def test_generate_hamming12(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("hamming12")
    _check_generate_hamming(d, tmp_path, "hamming12", 12, 7)


def test_hamming_split_plan_pins():
    # proposal §3 F4 feasibility: basis = the two strings,
    # shared_components, override expected (holdout ~0.45, wide n_probe)
    # -- the count_div13/roman_sum7 shared-2-component figures.
    for name in ("hamming8", "hamming12"):
        sp, n_probe = gen_items.SPLIT_PLAN[name]
        assert sp.shared_components is True
        assert sp.holdout_frac == 0.45
        assert sp.min_val_items == 300
        assert n_probe == 4000


# ------------------------------------------------ wave 2 (blessing 2026-08-02)

def test_generate_median5(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("median5")
    assert len(d["probe_items"]) >= 1800 and len(d["eval_items"]) >= 500
    for item in d["probe_items"][:50]:
        nums = [int(x) for x in re.findall(r"\d+", item["question"])]
        assert len(nums) == 5 == len(set(nums))
        med = sorted(nums)[2]
        assert item["answer"] == str(med)
        assert item["probe_label"] == str(nums.index(med) + 1)
        assert item["basis"] == [str(nums[0])]   # first-number basis (blessed)
    assert d["family"] == "order_stat" and d["dial_value"] == 5


def test_generate_median7(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("median7")
    for item in d["probe_items"][:50]:
        nums = [int(x) for x in re.findall(r"\d+", item["question"])]
        assert len(nums) == 7 == len(set(nums))
        med = sorted(nums)[3]
        assert item["answer"] == str(med)
        assert item["probe_label"] == str(nums.index(med) + 1)
        assert item["basis"] == [str(nums[0])]
    assert d["family"] == "order_stat" and d["dial_value"] == 7


def test_generate_arith_next(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("arith_next")
    # reduced pool (blessing: 0.35/1000 -- 1500 of the 1710-run space)
    assert len(d["probe_items"]) == 1000 and len(d["eval_items"]) == 500
    for item in d["probe_items"][:50]:
        t = [int(x) for x in re.findall(r"\d+", item["question"])]
        assert len(t) == 4
        nxt = 2 * t[3] - t[2]
        assert item["answer"] == str(nxt)
        assert item["probe_label"] == str(nxt % 7)
        assert item["basis"] == [str(t[0])]
    assert d["family"] == "seq_extrap" and d["dial_value"] == 1


def test_generate_quad_next(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("quad_next")
    for item in d["probe_items"][:50]:
        t = [int(x) for x in re.findall(r"\d+", item["question"])]
        assert len(t) == 4
        nxt = 3 * t[3] - 3 * t[2] + t[1]     # vanishing third difference
        assert item["answer"] == str(nxt)
        assert item["probe_label"] == str(nxt % 7)
        assert item["basis"] == [str(t[0])]
    assert d["family"] == "seq_extrap" and d["dial_value"] == 2


def test_generate_odd6(tmp_path, monkeypatch):
    from experiments.exp2c.battery.wordlists_2c import CATEGORIES_2C
    cat_of = {w: c for c, ms in CATEGORIES_2C.items() for w in ms}
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("odd6")
    assert len(d["probe_items"]) >= 7200 and len(d["eval_items"]) >= 500
    for item in d["probe_items"][:50]:
        words = re.search(r"others: ([a-z_, ]+)\?", item["question"]) \
                  .group(1).split(", ")
        assert len(words) == 6
        cats = [cat_of[w] for w in words]
        odd = next(w for w, c in zip(words, cats) if cats.count(c) == 1)
        assert item["answer"] == odd
        assert item["probe_label"] == str(words.index(odd) + 1)
        # re-blessing 2026-08-02: basis = the odd word ALONE (the 6-comp
        # shared basis cleared its floors only degenerately -- wave-2
        # review F2, ruled by Michael)
        assert item["basis"] == [odd]
    assert d["family"] == "odd_one_out" and d["dial_value"] == 6


def test_shots_demonstrate_distinct_labels(tmp_path, monkeypatch):
    # Shot-diversity rule (Michael's ruling 2026-08-02, after three
    # seed-luck collisions in the growth build): generate()'s two shots
    # must demonstrate DISTINCT probe labels, redrawing from the same
    # seeded stream until satisfied. Checked here on the two rungs whose
    # committed shots collided (odd6 5/5, antonym6 4/4) plus one
    # already-compliant rung (mod17) whose output must be unchanged.
    from experiments.exp2c.battery.wordlists_2c import CATEGORIES_2C, ANTONYMS_2C
    cat_of = {w: c for c, ms in CATEGORIES_2C.items() for w in ms}
    ant = dict(ANTONYMS_2C)
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)

    d = gen_items.generate("odd6")
    labels = []
    for q, a in d["shots"]:
        words = re.search(r"others: ([a-z_, ]+)\?", q).group(1).split(", ")
        labels.append(words.index(a) + 1)
    assert len(set(labels)) == len(labels), labels

    d = gen_items.generate("antonym6")
    labels = []
    for q, a in d["shots"]:
        opts = re.search(r": ([a-z, ]+)\?", q).group(1).split(", ")
        labels.append(opts.index(a) + 1)
    assert len(set(labels)) == len(labels), labels

    d = gen_items.generate("mod17")
    labels = [int(re.findall(r"\d+", q)[0]) % 17 for q, a in d["shots"]]
    assert len(set(labels)) == len(labels), labels


# ------------------------------------------------------------------ wave 3

def test_generate_base13(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("base13")
    assert len(d["probe_items"]) >= 1800 and len(d["eval_items"]) >= 500
    digits = "0123456789ABC"
    for item in d["probe_items"][:50]:
        n = int(re.search(r"Write (\d+) in base 13", item["question"]).group(1))
        out, m = "", n
        while m:
            out, m = digits[m % 13] + out, m // 13
        assert item["answer"] == out
        assert item["probe_label"] == str(n % 13)
        assert item["basis"] == [str(n)]
    assert d["family"] == "base_repr" and d["dial_value"] == 13


def test_generate_antonym6(tmp_path, monkeypatch):
    from experiments.exp2c.battery.wordlists_2c import ANTONYMS_2C
    ant = dict(ANTONYMS_2C)
    monkeypatch.setattr(gen_items, "ITEMS_DIR", tmp_path)
    d = gen_items.generate("antonym6")
    assert len(d["probe_items"]) >= 1800 and len(d["eval_items"]) >= 500
    for item in d["probe_items"][:50]:
        cue = re.search(r"opposite of '([a-z]+)'", item["question"]).group(1)
        opts = re.search(r": ([a-z, ]+)\?", item["question"]).group(1).split(", ")
        assert len(opts) == 6
        assert item["answer"] == ant[cue]
        assert item["probe_label"] == str(opts.index(ant[cue]) + 1)
        assert item["basis"] == [cue]
    assert d["family"] == "antonym" and d["dial_value"] == 6


def test_wave3_split_plan_pins():
    # blessing table 2026-08-02: both wave-3 rungs take pure defaults
    # (base13 = the base12/base12_digitsum precedent; antonym6's 130-cue
    # pool cleared the sweep at 380-408 val, no override)
    for name in ("base13", "antonym6"):
        sp, n_probe = gen_items.SPLIT_PLAN[name]
        assert sp.holdout_frac == 0.2 and not sp.shared_components
        assert n_probe == 2000


def test_wave2_split_plan_pins():
    # the approved consolidated blessing (PROGRESS 2026-08-02)
    for name in ("median5", "median7", "quad_next"):
        sp, n_probe = gen_items.SPLIT_PLAN[name]
        assert sp.holdout_frac == 0.2 and not sp.shared_components
        assert n_probe == 2000
    sp, n_probe = gen_items.SPLIT_PLAN["arith_next"]
    assert sp.holdout_frac == 0.35 and n_probe == 1000
    # odd6 re-blessed 2026-08-02 (wave-2 review F2): odd-word 1-comp
    # basis at holdout 0.30, n_probe unchanged at 8000
    sp, n_probe = gen_items.SPLIT_PLAN["odd6"]
    assert sp.shared_components is False and sp.holdout_frac == 0.30
    assert n_probe == 8000


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
    "hamming8": lambda q: _true_hamming(q),
    "hamming12": lambda q: _true_hamming(q),
    "median5": lambda q: str(sorted(_ints(q))[2]),
    "median7": lambda q: str(sorted(_ints(q))[3]),
    "arith_next": lambda q: _true_arith_next(q),
    "quad_next": lambda q: _true_quad_next(q),
    "odd6": lambda q: _true_odd6(q),
    "base13": lambda q: _true_base13(q),
    "antonym6": lambda q: _true_antonym6(q),
}


def _true_base13(q):
    n = int(re.search(r"Write (\d+) in base 13", q).group(1))
    digits, out = "0123456789ABC", ""
    while n:
        out, n = digits[n % 13] + out, n // 13
    return out or "0"


def _true_antonym6(q):
    # Wave-3 review M3 sharpening: don't trust a shared direction dict --
    # assert exactly ONE listed option pairs with the cue in ANTONYMS_2C
    # (order-free frozenset membership), and return that option.
    from experiments.exp2c.battery.wordlists_2c import ANTONYMS_2C
    pairs = {frozenset(p) for p in ANTONYMS_2C}
    cue = re.search(r"opposite of '([a-z]+)'", q).group(1)
    opts = re.search(r": ([a-z, ]+)\?", q).group(1).split(", ")
    partners = [w for w in opts if frozenset((cue, w)) in pairs]
    assert len(partners) == 1, (cue, opts)
    return partners[0]


# --------------------------------------------------------------------------
# Committed probe-label sweep (wave-3 review M2): the Fix-A sweep above
# checks ANSWERS only; a hand-edited committed probe_label would pass the
# suite. TRUE_LABEL recomputes the LABEL from the question text alone for
# every registered spec; the sweep below runs it over EVERY item of every
# committed file. Specs whose question asks for the label directly reuse
# TRUE_ANSWER (answer == label there, and the Fix-A sweep already pins
# answer correctness on committed files).

def _true_label_odd6(q):
    return str(re.search(r"others: ([a-z_, ]+)\?", q).group(1)
               .split(", ").index(_true_odd6(q)) + 1)


def _true_label_antonym6(q):
    return str(re.search(r": ([a-z, ]+)\?", q).group(1)
               .split(", ").index(_true_antonym6(q)) + 1)


def _true_label_median(q, mid):
    nums = _ints(q)
    return str(nums.index(sorted(nums)[mid]) + 1)


TRUE_LABEL = {
    "add4_mid": lambda q: str((_ints(q)[0] + _ints(q)[1]) // 100 % 10),
    "sub4_mid": lambda q: str((_ints(q)[0] - _ints(q)[1]) // 100 % 10),
    "base12": lambda q: str(_ints(q)[0] % 12),
    "base12_digitsum": lambda q: str(_b12_digitsum(_ints(q)[0])),
    "sub_base8": lambda q: str((int(re.search(
        r"What is (\d+) - (\d+)", q).group(1), 8) - int(re.search(
        r"What is (\d+) - (\d+)", q).group(2), 8)) % 8),
    "mod17": lambda q: str(_ints(q)[0] % 17),
    "mod19": lambda q: str(_ints(q)[0] % 19),
    "mod13_comp": lambda q: str((_ints(q)[0] + _ints(q)[1]) % 13),
    "caesar_len8": lambda q: TRUE_ANSWER["caesar_len8"](q)[0],
    "count_div13": lambda q: TRUE_ANSWER["count_div13"](q),
    "clock24_d999": lambda q: TRUE_ANSWER["clock24_d999"](q),
    "rev_string7": lambda q: re.search(r"'([a-z]+)'", q).group(1)[-1],
    "roman_sum7": lambda q: TRUE_ANSWER["roman_sum7"](q),
    "collatz_step2": lambda q: TRUE_ANSWER["collatz_step2"](q),
    "isqrt_gap": lambda q: TRUE_ANSWER["isqrt_gap"](q),
    "letter_sum": lambda q: TRUE_ANSWER["letter_sum"](q),
    "letter_prod": lambda q: TRUE_ANSWER["letter_prod"](q),
    "hamming8": lambda q: TRUE_ANSWER["hamming8"](q),
    "hamming12": lambda q: TRUE_ANSWER["hamming12"](q),
    "median5": lambda q: _true_label_median(q, 2),
    "median7": lambda q: _true_label_median(q, 3),
    "arith_next": lambda q: str(int(_true_arith_next(q)) % 7),
    "quad_next": lambda q: str(int(_true_quad_next(q)) % 7),
    "odd6": _true_label_odd6,
    "antonym6": _true_label_antonym6,
    "base13": lambda q: str(_ints(q)[0] % 13),
}


def _b12_digitsum(n):
    total = 0
    while n:
        n, r = divmod(n, 12)
        total += r
    return total % 5


def test_true_label_covers_every_registered_spec():
    assert set(TRUE_LABEL) == set(SPECS)


def test_committed_labels_are_true_labels():
    # every item of every committed file, probe and eval sides both --
    # the freeze-facing pin M2 asked for
    for name, recompute in TRUE_LABEL.items():
        path = _ITEMS / f"{name}.json"
        if not path.exists():
            continue          # only rungs with committed items
        d = json.loads(path.read_text())
        for grp in ("probe_items", "eval_items"):
            for it in d[grp]:
                true = recompute(it["question"])
                assert true == it["probe_label"], (
                    f"{name}: {it['question']!r} -> stored label "
                    f"{it['probe_label']!r}, true label {true!r}")


# Wave-2 review M4 hardening (2026-08-02): recompute seq_extrap answers
# by the difference chain (infer the generator parameters from the
# printed terms), NOT the oracle's own linear functional -- a shared
# error in the 2t3-t2 / 3t3-3t2+t1 identities would otherwise be
# invisible to the Fix-A sweep.

def _true_arith_next(q):
    t = _ints(q)
    d = t[1] - t[0]
    assert t[2] - t[1] == d and t[3] - t[2] == d, q
    return str(t[3] + d)


def _true_quad_next(q):
    t = _ints(q)
    d1 = [t[i + 1] - t[i] for i in range(3)]
    q2 = d1[1] - d1[0]
    assert d1[2] - d1[1] == q2 and q2 % 2 == 0 and q2 >= 2, q
    return str(t[3] + d1[2] + q2)


def _true_odd6(q):
    from experiments.exp2c.battery.wordlists_2c import CATEGORIES_2C
    cat_of = {w: c for c, ms in CATEGORIES_2C.items() for w in ms}
    words = re.search(r"others: ([a-z_, ]+)\?", q).group(1).split(", ")
    cats = [cat_of[w] for w in words]
    return next(w for w, c in zip(words, cats) if cats.count(c) == 1)


def _true_hamming(q):
    s1, s2 = re.findall(r"'([a-d]+)'", q)
    return str(sum(a == b for a, b in zip(s1, s2)))


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
