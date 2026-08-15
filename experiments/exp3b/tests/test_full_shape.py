"""Execute the synthetic full-shape batteries (design §2 item 3): every
terminal branch of the frozen tree, reached end to end through the frozen
loaders. This same run is repeated cold at freeze and its results recorded
in the freeze checklist.
"""
import pytest

from experiments.exp3b.tests import full_shape as fs


@pytest.fixture(scope="module")
def results(tmp_path_factory):
    return fs.run_all(tmp_path_factory.mktemp("full_shape"))


@pytest.mark.parametrize("name", list(fs.BATTERIES))
def test_battery_reaches_its_terminal_branch(results, name):
    spec, v = fs.BATTERIES[name], results[name]
    assert v["verdict"] == spec["expect"], (name, v["verdict"], v["reason"])
    assert spec.get("expect_reason", "") in v.get("reason", ""), \
        (name, v["reason"])
    if "expect_contaminated" in spec:
        assert v["contaminated"] == spec["expect_contaminated"], name


def test_every_terminal_outcome_is_reached(results):
    """The six outcomes of design §8's last row: three INSUFFICIENT_DATA
    routes (plus the contamination-emptied fourth), UNITS_ARTIFACT,
    DISSOCIATION, PARTIAL."""
    verdicts = [v["verdict"] for v in results.values()]
    assert verdicts.count("INSUFFICIENT_DATA") >= 4
    for want in ("UNITS_ARTIFACT", "DISSOCIATION", "PARTIAL"):
        assert want in verdicts


def test_full_shape_batteries_use_the_real_floors(results):
    """The synthetic worlds adjudicate against the committed floors, not
    convenient ones — the counts in fs are chosen against .056/.054/.052/.496
    and a drifted floors file would surface here."""
    out = results["dissociation"]
    assert out["floors"] == {"rev_string7": 0.056, "reverse_string": 0.054,
                             "ctrl_copy": 0.052, "clock24_d999": 0.496}
