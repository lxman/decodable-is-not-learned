"""labels_2f: the per-rung label functions (§3), readable from an
answer and from an emitted string, their floors, and the known-answer
gates against 2c's committed probe_label fields."""
import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2f import labels_2f as lb


def test_rungs_sizes_and_label_kinds():
    assert lb.RUNGS == ("sub3_mid", "arith_next")
    assert lb.SIZES == ("410m", "1b")
    assert lb.LABEL_KINDS == {"sub3_mid": ("mid_digit",),
                              "arith_next": ("last_digit", "mod7")}
    assert lb.PRIMARY == {"sub3_mid": "mid_digit", "arith_next": "last_digit"}
    assert lb.n_classes("mid_digit") == 10 and lb.n_classes("last_digit") == 10 \
        and lb.n_classes("mod7") == 7


# ------------------------------------------------------------ answers

def test_answer_labels():
    assert lb.answer_label("mid_digit", "45") == "4"       # 045
    assert lb.answer_label("mid_digit", "204") == "0"
    assert lb.answer_label("mid_digit", "4") == "0"        # 004
    assert lb.answer_label("last_digit", "74") == "4"
    assert lb.answer_label("last_digit", "100") == "0"
    assert lb.answer_label("mod7", "74") == "4"            # 74 = 70 + 4
    assert lb.answer_label("mod7", "115") == "3"
    with pytest.raises(ValueError):
        lb.answer_label("mid_digit", "1234")               # not 1–3 digits
    with pytest.raises(ValueError):
        lb.answer_label("last_digit", "x")
    with pytest.raises(ValueError):
        lb.answer_label("nope", "1")


# ---------------------------------------------------------- emissions

def test_emission_labels_through_2c_normalizer():
    # 2c's `number` normalization: first line, first digit run, commas out
    assert lb.emission_label("mid_digit", " 294 (Nazareno v.") == "9"
    assert lb.emission_label("mid_digit", " 4\n\nQ: What is 132") == "0"
    assert lb.emission_label("last_digit", " 93\n\nQ: The sequence") == "3"
    assert lb.emission_label("last_digit", " 1,163\n\n###") == "3"
    assert lb.emission_label("mod7", " 93\n") == str(93 % 7)


def test_emission_miss_cases():
    MISS = lb.MISS
    assert lb.emission_label("mid_digit", " 1163\n") is MISS      # 4 digits
    assert lb.emission_label("mid_digit", " No calculation") is MISS
    assert lb.emission_label("last_digit", " -12\n") is MISS      # negative
    assert lb.emission_label("last_digit", "") is MISS
    assert lb.emission_label("mod7", " #123456\n\nQ") == str(123456 % 7)
    assert lb.emission_label("last_digit", " 10, 26\n") == "0"    # first run
    # totality: never raises on the draw side
    import random
    rng = random.Random(0)
    alphabet = " 0123456789,-.\n#Qabc~"
    for _ in range(20_000):
        s = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 12)))
        for kind in ("mid_digit", "last_digit", "mod7"):
            out = lb.emission_label(kind, s)
            assert out is MISS or (isinstance(out, str) and len(out) == 1)


def test_exact_match_is_2cs_verify():
    """The exact-match gate reads through the same parse: a draw verifies
    iff 2c's normalize of draw and answer agree."""
    assert lb.exact_match("number", " 294 (x", "294")
    assert not lb.exact_match("number", " 29\n", "294")
    assert lb.exact_match("number", " 1,163\n", "1163")


# ------------------------------------------------------------- floors

@pytest.fixture(scope="module")
def battery():
    return {r: bt.load_item_file(r) for r in lb.RUNGS}


def test_floor_table_is_max_of_majority_and_uniform(battery):
    t = lb.floor_table(battery)
    for rung in lb.RUNGS:
        for kind in lb.LABEL_KINDS[rung]:
            f = t[(rung, kind)]
            assert f["n_items"] == 500 and f["n_classes"] == lb.n_classes(kind)
            assert f["floor"] == max(f["majority_share"], 1 / f["n_classes"])
            assert abs(sum(f["class_shares"].values()) - 1.0) < 1e-9
    assert t[("arith_next", "mod7")]["n_classes"] == 7


def test_known_answer_gates_against_2c_probe_labels(battery):
    """sub3_mid's committed probe_label IS the middle digit (500/500);
    arith_next's committed probe_label IS (a+4d) mod 7 == answer mod 7
    (500/500). The gate is executable and exact."""
    g = lb.check_probe_label_gates(battery)
    assert g["sub3_mid/mid_digit"] == "PASS (500/500)"
    assert g["arith_next/mod7"] == "PASS (500/500)"
    bad = {r: dict(c) for r, c in battery.items()}
    bad["sub3_mid"] = dict(bad["sub3_mid"])
    items = [dict(it) for it in bad["sub3_mid"]["eval_items"]]
    items[3]["probe_label"] = "x"
    bad["sub3_mid"]["eval_items"] = items
    with pytest.raises(ValueError, match="probe_label"):
        lb.check_probe_label_gates(bad)


def test_eval_labels_vector(battery):
    y = lb.eval_labels(battery["arith_next"], "last_digit")
    assert len(y) == 500 and y[0] == "4" and all(len(s) == 1 for s in y)
    y7 = lb.eval_labels(battery["arith_next"], "mod7")
    assert y7 == [it["probe_label"] for it in battery["arith_next"]["eval_items"]]


def test_unicode_digits_are_a_miss_for_every_kind():
    """Freeze F-1: int() accepts Arabic-Indic and full-width digits, so
    a unicode run would have matched mod 7 while the digit labels
    could not match an ASCII answer label; the parse is ASCII-only."""
    for s in (" ٧٤\n", " ７４\n", " 7४\n", " ٣"):
        for kind in ("mid_digit", "last_digit", "mod7"):
            assert lb.emission_label(kind, s) is lb.MISS, (s, kind)
    assert lb.emission_label("last_digit", " 74\u200b\n") == "4"   # zero-width space after
