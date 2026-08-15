"""Fixture suite for the frozen Exp 3a analysis (design §4, §5).

The experiment adjudicates a claim already in print. Every provision that
could soften an unwelcome outcome is tested in both directions.
"""
import pytest

from experiments.exp3a import analyze_3a as a

REV = ("rev_string7", "reverse_string")


# ------------------------------------------------------------------ floors

def items(first_chars, input_firsts=None):
    ifs = input_firsts or ["z"] * len(first_chars)
    return [{"answer": c + "xxxxxx", "question": f"Spell the string '{i}bcdefg' backwards.",
             "probe_label": c} for c, i in zip(first_chars, ifs)]


def test_floor_is_the_max_of_three_and_names_them():
    f = a.chance_floors(items(["a"] * 60 + ["b"] * 40))
    assert f["uniform"] == pytest.approx(1 / 26)
    assert f["marginal"] == pytest.approx(0.60)
    assert f["primary"] == pytest.approx(0.60)
    assert f["primary_source"] == "marginal"


def test_copy_first_floor_catches_a_model_that_echoes_the_input():
    """A model emitting the input's first char instead of reversing must not
    be scored as capable. Here every item's input starts with its answer's
    first char, so echoing scores 1.0 and the floor must say so."""
    f = a.chance_floors(items(list("abcdefghij") * 10, list("abcdefghij") * 10))
    assert f["copy_first"] == pytest.approx(1.0)
    assert f["primary"] == pytest.approx(1.0)
    assert f["primary_source"] == "copy_first"


# ------------------------------------------------------- first-char scoring

@pytest.mark.parametrize("cont,label,want", [
    (" rcnnbgv", "r", True),
    ("rcnnbgv", "r", True),
    ("\n\n  R", "r", True),          # case-folded
    (" xcnnbgv", "r", False),
    ("", "r", False),               # empty is a failure to emit, not a drop
    ("   ", "r", False),
    ("7abc", "r", False),           # non-alphabetic first char
])
def test_first_char_scoring(cont, label, want):
    assert a.score_first_char(cont, label) is want


def test_scoring_never_silently_drops_an_item():
    """n must equal the item count whatever the model emitted."""
    conts = [" r", "", "   ", "7x", " R"]
    labels = ["r", "r", "r", "r", "r"]
    got = a.score_cell(conts, labels)
    assert got["n"] == 5 and got["correct"] == 2


# --------------------------------------------------------- the verdict tree

def cells(rev_sig=True, ctrl_sig=True, untrained_fires=False, rev_acc=0.60):
    out = []
    for rung in REV:
        for size in a.SIZES:
            out.append({"rung": rung, "size": size, "mode": "trained",
                        "n": 500, "correct": int(500 * (rev_acc if rev_sig else 0.05)),
                        "full_string_acc": 0.0, "committed_2c_acc": 0.0})
    for size in a.SIZES:
        out.append({"rung": "ctrl_copy", "size": size, "mode": "trained",
                    "n": 500, "correct": int(500 * (0.9 if ctrl_sig else 0.05)),
                    "full_string_acc": 0.96, "committed_2c_acc": 0.96})
        out.append({"rung": "clock24_d999", "size": size, "mode": "trained",
                    "n": 500, "correct": 300, "full_string_acc": 0.6,
                    "committed_2c_acc": 0.6})
    for rung in REV + ("ctrl_copy", "clock24_d999"):
        for size in a.SIZES:
            out.append({"rung": rung, "size": size, "mode": "untrained",
                        "n": 500, "correct": int(500 * (0.5 if untrained_fires else 0.04)),
                        "full_string_acc": 0.0, "committed_2c_acc": 0.0})
    return out


FLOORS = {r: {"primary": 0.056} for r in REV + ("ctrl_copy", "clock24_d999")}


def test_positive_control_failure_precedes_everything():
    out = a.verdict(cells(ctrl_sig=False), FLOORS)
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "ctrl_copy" in out["reason"]


def test_replication_failure_precedes_the_claim():
    c = cells()
    for x in c:
        if x["rung"] == "ctrl_copy" and x["mode"] == "trained":
            x["full_string_acc"] = 0.10        # committed 2c says .96
    out = a.verdict(c, FLOORS)
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "replicat" in out["reason"].lower()


def test_reversal_above_floor_everywhere_is_a_units_artifact():
    out = a.verdict(cells(rev_sig=True), FLOORS)
    assert out["verdict"] == "UNITS_ARTIFACT"


def test_reversal_at_floor_everywhere_is_a_dissociation():
    out = a.verdict(cells(rev_sig=False), FLOORS)
    assert out["verdict"] == "DISSOCIATION"


def test_mixed_is_reported_as_partial_with_the_sizes_named():
    c = cells(rev_sig=False)
    for x in c:
        if x["rung"] == "rev_string7" and x["size"] == "12b" and x["mode"] == "trained":
            x["correct"] = 300
    out = a.verdict(c, FLOORS)
    assert out["verdict"] == "PARTIAL"
    assert "12b" in str(out["significant_cells"])


def test_untrained_fire_marks_contamination_without_halting():
    out = a.verdict(cells(untrained_fires=True), FLOORS)
    assert out["contaminated"]
    assert out["verdict"] in ("UNITS_ARTIFACT", "DISSOCIATION", "PARTIAL")


def test_bonferroni_is_applied_across_the_twelve_trained_cells():
    assert a.n_trained_cells(cells()) == 12
    # 43/500 against a .056 floor gives p = .00394: clears alpha=.01 on its
    # own and fails .01/12. Chosen by computing the interval, not guessed --
    # an earlier guess of 38 cleared neither and would have passed this test
    # for the wrong reason.
    assert a.significant(correct=43, n=500, floor=0.056, n_tests=1) is True
    assert a.significant(correct=43, n=500, floor=0.056, n_tests=12) is False


# ------------------------------------- the copy floor must know its own task

def copy_items(n=52):
    """A COPY task: the answer IS the input, so echoing scores 1.0. Answers
    are VARIED so that `marginal` stays low and the test isolates the
    copy_first exclusion rather than tripping on a degenerate marginal."""
    out = []
    for i in range(n):
        w = "abcdefghijklmnopqrstuvwxyz"[i % 26] + "qrst"
        out.append({"answer": w, "question": f"Repeat the string '{w}'.",
                    "probe_label": w[0]})
    return out


def test_copy_first_is_excluded_when_copying_IS_the_task():
    """Caught before freeze. ctrl_copy's copy_first floor is 1.0 by
    construction — the answer is the input. Taking the max would make its
    floor unbeatable, the positive-control gate would fire unconditionally,
    and the experiment could only ever return INSUFFICIENT_DATA. The floor
    exists to bound strategies that score WITHOUT the capability; for a copy
    task, copying is the capability."""
    f = a.chance_floors(copy_items())
    assert f["copy_is_the_task"] is True
    assert f["primary"] != pytest.approx(1.0)
    assert f["primary_source"] != "copy_first"


def test_copy_first_still_applies_where_copying_is_wrong():
    f = a.chance_floors(items(list("abcdefghij") * 5, list("abcdefghij") * 5))
    assert f["copy_is_the_task"] is False
    assert f["primary_source"] == "copy_first"


def test_copy_is_the_task_is_derived_from_items_not_declared():
    """No hand-set flag: a flag is tunable, and this decides a gate."""
    assert a.chance_floors(copy_items())["copy_is_the_task"] is True
    assert a.chance_floors(items(["a"] * 40))["copy_is_the_task"] is False


# ------------------------------- gaps found by mutation testing, now closed

def test_digit_labels_score_correctly():
    """clock24_d999's probe label is a DIGIT. An isalpha() guard zeroed the
    matched control at every cell and looked like a finding."""
    assert a.score_first_char("8", "8") is True
    assert a.score_first_char(" 7 o'clock", "7") is True
    assert a.score_first_char("8", "7") is False


def test_label_case_is_folded_on_both_sides():
    assert a.score_first_char("r", "R") is True
    assert a.score_first_char("R", "r") is True


def test_a_length_mismatch_is_an_error_not_a_truncation():
    with pytest.raises(ValueError, match="dropped"):
        a.score_cell([" r", " x"], ["r"])


def test_the_test_is_one_sided():
    """45/500 against a .056 floor: p = .00137, so p*12 = .0164 fails at
    alpha=.01 while a halved (two-sided) p would pass at .0082."""
    assert a.significant(correct=45, n=500, floor=0.056, n_tests=12) is False
