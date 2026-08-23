# experiments/exp2g/tests/test_labels_2g.py
"""labels_2g: each rung's label function reproduces the committed
probe_label on every eval AND probe item; classes covered; floors."""
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp2g import labels_2g as lb


@pytest.fixture(scope="module")
def battery():
    return bg.load_battery(bg.PREDICTOR_RUNGS)


def test_kinds_and_classes():
    assert lb.KIND_OF["antonym"] == "position" and lb.n_classes("antonym") == 4
    assert lb.n_classes("antonym6") == 6 and lb.n_classes("median5") == 5
    assert lb.n_classes("odd6") == 6
    assert lb.classes_of("add_base8") == [str(i) for i in range(8)]
    assert lb.classes_of("sub3_mid") == [str(i) for i in range(10)]
    assert lb.classes_of("arith_next") == [str(i) for i in range(10)]
    assert lb.classes_of("count_div13") == [str(i) for i in range(1, 11)]


def test_label_functions_on_examples():
    assert lb.answer_label("antonym", {"question": "Which of these means the opposite of 'awake': asleep, genuine, open, exact?", "answer": "asleep"}) == "1"
    assert lb.answer_label("median5", {"question": "Which of these numbers is the median: 595, 659, 437, 220, 176?", "answer": "437"}) == "3"
    assert lb.answer_label("odd6", {"question": "Which word is not like the others: knee, chin, onyx, thumb, elbow, hip?", "answer": "onyx"}) == "3"
    assert lb.answer_label("add_base8", {"question": "x", "answer": "114"}) == "4"
    assert lb.answer_label("sub_base8", {"question": "x", "answer": "3"}) == "3"
    assert lb.answer_label("add3_mid", {"question": "x", "answer": "1404"}) == "0"
    assert lb.answer_label("sub3_mid", {"question": "x", "answer": "45"}) == "4"
    assert lb.answer_label("sub3_mid", {"question": "x", "answer": "7"}) == "0"
    assert lb.answer_label("sub4_mid", {"question": "x", "answer": "1909"}) == "9"
    assert lb.answer_label("arith_next", {"question": "x", "answer": "74"}) == "4"
    assert lb.answer_label("arith_next", {"question": "x", "answer": "93"}) == "3"  # 93 mod 7 = 2, last digit = 3 — the two conventions diverge here
    assert lb.answer_label("count_div13", {"question": "x", "answer": "7"}) == "7"


def test_label_functions_refuse_outside_domain():
    with pytest.raises(ValueError):
        lb.answer_label("antonym", {"question": "no options here", "answer": "x"})
    with pytest.raises(ValueError):
        lb.answer_label("antonym", {"question": "opposite of 'a': b, c, d, e?", "answer": "zzz"})
    with pytest.raises(ValueError):
        lb.answer_label("add_base8", {"question": "x", "answer": "18"})   # not octal
    with pytest.raises(ValueError):
        lb.answer_label("arith_next", {"question": "x", "answer": "-3"})
    with pytest.raises(ValueError):
        lb.answer_label("count_div13", {"question": "x", "answer": "0"})
    with pytest.raises(ValueError):
        lb.answer_label("nope", {"question": "x", "answer": "1"})


def test_gates_500_500_and_probe_items(battery):
    g = lb.check_label_gates(battery)
    assert set(g) == set(bg.PREDICTOR_RUNGS)
    for r in bg.PREDICTOR_RUNGS:
        n_p = len(battery[r]['probe_items'])
        if r == "arith_next":
            assert g[r] == (f"PASS (500/500 eval; {n_p}/{n_p} probe; "
                             f"last digit == 2f's label; committed "
                             f"probe_label == answer mod 7)")
        else:
            assert g[r] == f"PASS (500/500 eval; {n_p}/{n_p} probe)"


def test_class_coverage(battery):
    cov = lb.check_class_coverage(battery)
    assert all(v["eval_not_in_probe"] == [] for v in cov.values())


def test_floor_table(battery):
    t = lb.floor_table(battery)
    assert t["antonym"]["floor"] == max(t["antonym"]["majority_share"], 0.25)
    assert round(t["antonym"]["majority_share"], 3) == 0.264     # slot 1: 132/500
    assert t["count_div13"]["n_classes"] == 10
    for r, v in t.items():
        assert v["floor"] >= 1.0 / v["n_classes"]


def test_check_label_gates_catches_a_corrupted_probe_label(battery):
    # every real battery is majority-consistent already (the gate never
    # fires on committed data), so corrupt a copy: one eval item's
    # committed probe_label on a non-arith_next rung (the ten-rung
    # branch) no longer matches the label function.
    bad = dict(battery)
    cap = dict(bad["antonym"])
    items = list(cap["eval_items"])
    corrupt = dict(items[0])
    corrupt["probe_label"] = "999"          # not a valid position label
    items[0] = corrupt
    cap["eval_items"] = items
    bad["antonym"] = cap
    with pytest.raises(ValueError, match="antonym/eval_items"):
        lb.check_label_gates(bad)


def test_floor_uses_1_over_k_when_majority_share_is_smaller(monkeypatch):
    # A real battery can never exercise the 1/K arm of max(maj, 1/K):
    # the majority share among K categories is always >= 1/K by the
    # pigeonhole bound, so floor_table's own eval_labels() never
    # produces a case where 1/K wins. Bypass it directly: stub
    # eval_labels to return more distinct labels than the rung's K,
    # forcing majority_share below 1/K.
    rung = "add3_mid"                        # kind tens_digit, K = 10
    fake_y = [str(i) for i in range(20)]     # 20 distinct labels, share 1/20
    monkeypatch.setattr(bg, "PREDICTOR_RUNGS", (rung,))
    monkeypatch.setattr(lb, "eval_labels", lambda cap, r: fake_y)
    t = lb.floor_table({rung: {"eval_items": []}})
    assert t[rung]["majority_share"] == pytest.approx(1 / 20)
    assert t[rung]["floor"] == pytest.approx(0.1)          # 1/K wins
