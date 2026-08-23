# experiments/exp2g/tests/test_strata_2g.py
"""strata_2g: the §6.2 covariates reproduce the doc's counts on the
committed items; the merge rule is the doc's."""
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp2g import strata_2g as sg


@pytest.fixture(scope="module")
def battery():
    return bg.load_battery(bg.PREDICTOR_RUNGS)


def test_carries_and_borrows():
    assert sg.carries("744", "660") == 2          # 4+6=10 carry at tens, 7+6+1=14 carry at hundreds
    assert sg.carries("999", "1") == 3
    assert sg.carries("123", "456") == 0
    assert sg.borrows("251", "206") == 1          # 1-6 borrows
    assert sg.borrows("3165", "1256") == 2
    assert sg.borrows("500", "1") == 2


def test_covariate_examples():
    assert sg.covariate("add3_mid", {"question": "What is 744 + 660?", "answer": "1404"}) == 2
    assert sg.covariate("sub3_mid", {"question": "What is 251 - 206?", "answer": "45"}) == 1
    assert sg.covariate("sub4_mid", {"question": "What is 3165 - 1256?", "answer": "1909"}) == 2
    assert sg.covariate("add_base8", {"question": "What is 73 + 21 in base 8 (both numbers are octal)?", "answer": "114"}) == 0
    assert sg.covariate("add_base8", {"question": "What is 75 + 23 in base 8 (both numbers are octal)?", "answer": "120"}) == 1
    assert sg.covariate("sub_base8", {"question": "What is 22 - 17 in base 8 (both numbers are octal)?", "answer": "3"}) == 1
    assert sg.covariate("antonym", {"question": "Which of these means the opposite of 'awake': asleep, genuine, open, exact?", "answer": "asleep"}) == 1
    assert sg.covariate("arith_next", {"question": "x", "answer": "74"}) == 0
    assert sg.covariate("arith_next", {"question": "x", "answer": "100"}) == 1
    assert sg.covariate("count_div13", {"question": "x", "answer": "7"}) == 7
    with pytest.raises(ValueError):
        sg.covariate("sub3_mid", {"question": "What is 206 - 251?", "answer": "-45"})


def test_merge_rule():
    # the doc's count_div13 case: 10 (3 items) -> into 9; 2 (15 items, already
    # >= the floor) stays put
    counts = {2: 15, 3: 78, 4: 56, 5: 79, 6: 73, 7: 68, 8: 67, 9: 61, 10: 3}
    m = sg.merge_levels(counts)
    assert m[10] == "9+10" and m[9] == "9+10" and m[2] == "2" and m[3] == "3"
    assert m[5] == "5"
    # nothing under the floor: identity
    assert sg.merge_levels({0: 77, 1: 155, 2: 184, 3: 84}) == {0: "0", 1: "1", 2: "2", 3: "3"}
    # ties go to the lower neighbour; cascading merges
    assert sg.merge_levels({0: 5, 1: 20, 2: 20}) == {0: "0+1", 1: "0+1", 2: "2"}
    assert sg.merge_levels({0: 20, 1: 3, 2: 20}) == {0: "0+1", 1: "0+1", 2: "2"}
    assert sg.merge_levels({0: 4, 1: 4, 2: 20}) == {0: "0+1+2", 1: "0+1+2", 2: "0+1+2"}
    assert sg.merge_levels({0: 2, 1: 3, 2: 3}) == {0: "0+1+2", 1: "0+1+2", 2: "0+1+2"}


def test_table_reproduces_doc_counts(battery):
    t = sg.build_table(battery)
    assert sg.check_strata_pins(t) == {r: "PASS" for r in bg.PREDICTOR_RUNGS}
    assert t["count_div13"]["counts"]["9+10"] == 64
    assert t["count_div13"]["counts"]["2"] == 15
    assert t["sub3_mid"]["counts"] == {"0": 164, "1": 238, "2": 98}
    assert t["antonym6"]["counts"]["2"] == 73          # nominal, never merged
    assert len(t["antonym"]["strata"]) == 500
    back = sg.from_json(sg.to_json(t))
    assert back == t
