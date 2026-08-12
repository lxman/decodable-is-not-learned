"""UntrainedRecord: a probe-only cell.

Deliberately NOT exp1's RunRecord, which mandates s2/s3 results an untrained
cell has no meaning for, and whose SYSTEMS tuple is frozen under the exp1 tag.
Exp 1b does not modify exp1.
"""

import pytest

from experiments.exp1.signatures.schema import ProbeResult
from experiments.exp1b.records import UNTRAINED_SYSTEMS, UntrainedRecord


def _probe(present=False):
    return ProbeResult(present=present, accuracy=0.09, chance=0.10,
                       null_p=0.62, null_mean=0.098, ci95=(0.07, 0.11),
                       best_layer=0, best_token=-1, n_layers_tested=1,
                       checkpoint_id="init", below_threshold=True,
                       signature="S1")


def test_round_trips_through_json(tmp_path):
    r = UntrainedRecord(system="grokking", size_bucket="1M", seed=100,
                        git_sha="abc1234", s1=_probe(), config={"d_model": 128})
    p = r.save(tmp_path / "seed100.json")
    back = UntrainedRecord.load(p)
    assert back.seed == 100
    assert back.s1.present is False
    assert back.s1.accuracy == 0.09
    assert back.config["d_model"] == 128


def test_ci95_round_trips_as_a_tuple():
    """JSON has no tuples; _build coerces list->tuple so equality holds."""
    r = UntrainedRecord(system="grokking", size_bucket="1M", seed=100,
                        git_sha="abc1234", s1=_probe())
    back = UntrainedRecord.from_json(r.to_json())
    assert back.s1.ci95 == (0.07, 0.11)


def test_rejects_a_system_outside_the_untrained_twin_set():
    with pytest.raises(ValueError, match="system"):
        UntrainedRecord(system="phaseA", size_bucket="1M", seed=100,
                        git_sha="abc1234", s1=_probe())


def test_rejects_a_size_outside_the_1b_matrix():
    """100M is not run in 1b; a record claiming it is a collection error."""
    with pytest.raises(ValueError, match="size_bucket"):
        UntrainedRecord(system="grokking", size_bucket="100M", seed=100,
                        git_sha="abc1234", s1=_probe())


def test_untrained_systems_are_the_three_trained_rows():
    assert UNTRAINED_SYSTEMS == ("grokking", "lubana_above", "lubana_below")
