# experiments/exp5/tests/test_analyze_5.py  (fast: the pure pieces)
import pytest

from experiments.exp5 import analyze_5 as an
from experiments.exp5 import battery_5 as b5


def test_collect_total_5_prefix_named_types_and_crash_on_logic_defect():
    v, f = an.collect_total_5(lambda: (_ for _ in ()).throw(OSError("x")), "5 x")
    assert v is None and f == ["5 x: OSError: x"]
    v, f = an.collect_total_5(lambda: 3, "5 y")
    assert v == 3 and f == []
    with pytest.raises(ZeroDivisionError):          # a logic defect is never laundered
        an.collect_total_5(lambda: 1 / 0, "5 z")
    with pytest.raises(ValueError, match="prefix"):
        an.collect_total_5(lambda: 3, "no prefix")


def test_gate1a_failures():
    good = {"digests_equal": True, "continuation_diffs": {r: 0 for r in b5.RUNGS},
            "continuations_compared": {r: 500 for r in b5.RUNGS}, "loss_equal": True,
            "prereg_tag": b5.PREREG_TAG_5, "pass": True}
    assert an.gate1a_failures_5(good) == []
    assert an.gate1a_failures_5({**good, "digests_equal": False})
    assert an.gate1a_failures_5({**good, "continuations_compared": {**good["continuations_compared"], "mod13": 499}})
    assert an.gate1a_failures_5({**good, "loss_equal": False})


def test_licence_block_cells():
    for world, mod in (("MATCHED", None), ("NOT-MATCHED", "LARGE-AHEAD"), ("NOT-MATCHED", "SMALL-AHEAD"),
                       ("NOT-MATCHED", "MIXED"), ("NOT-MATCHED", "THIN"), ("UNDETERMINED", None),
                       ("INSUFFICIENT_DATA", None)):
        lic = an.licence_block_5(world, mod, {"declaration": "POWERED", "min_detectable_T": 0.01})
        assert lic["sentence"] and lic["caveat"].startswith("one family")
    under = an.licence_block_5("MATCHED", None, {"declaration": "DECLARED UNDERPOWERED IN ADVANCE",
                                                 "min_detectable_T": 0.02})
    assert "not distinguishable at this resolution" in under["sentence"]


def test_projection_failures():
    units = {"6.9b": {"git_shas": {1000: "u1", 2000: "u2"}, "whys": {1000: "spine", 2000: "bisect"}},
             "1b": {"git_shas": {143000: "f1"}, "whys": {143000: "final"}}}
    ok = an.projection_failures_5(units, projection_commit="p", is_ancestor=lambda a, b: True,
                                  seal_tag_commit="s")
    assert ok == []
    bad = an.projection_failures_5(units, projection_commit="p",
                                   is_ancestor=lambda a, b: not (a == "p" and b == "u2"),
                                   seal_tag_commit="s")
    assert any("6.9b/step2000" in f for f in bad)
    assert an.projection_failures_5(units, projection_commit=None, is_ancestor=lambda a, b: True,
                                    seal_tag_commit="s")
