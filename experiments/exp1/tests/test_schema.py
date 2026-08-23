"""M1 tests for the frozen RunRecord data contract.

analyze.py depends only on this schema, so the round-trip and validation guarantees
here are what let the analysis be frozen independently of signature internals.
"""

import pytest

from signatures.schema import (
    ForecastResult,
    GTCheck,
    ProbeResult,
    RunRecord,
    SamplingResult,
)


def _record(system="grokking", size="1M", axis="training_steps") -> RunRecord:
    return RunRecord(
        system=system,
        size_bucket=size,
        seed=0,
        git_sha="deadbeef",
        torch_version="2.12.1",
        transformers_version="5.13.0",
        gt_check=GTCheck(certified=True, method="heldout+restricted_loss",
                         details={"heldout_acc": 0.99}),
        s1=ProbeResult(
            present=True, accuracy=0.87, chance=1 / 113, null_p=0.0001,
            null_mean=0.009, ci95=(0.82, 0.91), best_layer=1, best_token=-1,
            n_layers_tested=2, checkpoint_id="step_00500", below_threshold=True,
        ),
        s2=SamplingResult(
            present=True, absent=False, passes=7, n=100_000, rate_point=7e-5,
            cp_lower=2.8e-5, cp_upper=1.4e-4, guessing_floor=1e-5,
            argmax_fails=True, checkpoint_id="step_00500",
        ),
        s3=ForecastResult(
            present=True, predicted_transition=1200.0, true_transition=1150.0,
            interval90=(1000.0, 1400.0), rel_error=0.043, slope_ci=(0.5, 1.5),
            beats_no_transition_baseline=True, axis=axis,
        ),
        config={"lr": 1e-3, "wd": 1.0},
    )


def test_round_trip_dict_equal():
    rec = _record()
    assert RunRecord.from_dict(rec.to_dict()) == rec


def test_round_trip_json_equal():
    rec = _record()
    assert RunRecord.from_json(rec.to_json()) == rec


def test_tuple_fields_survive_json():
    """JSON has no tuples; ci95/interval90/slope_ci must come back as tuples."""
    rec = RunRecord.from_json(_record().to_json())
    assert isinstance(rec.s1.ci95, tuple)
    assert isinstance(rec.s3.interval90, tuple)
    assert isinstance(rec.s3.slope_ci, tuple)


def test_save_and_load(tmp_path):
    rec = _record()
    path = rec.save(tmp_path / "grokking" / "1M" / "0.json")
    assert path.exists()
    assert RunRecord.load(path) == rec


def test_rejects_unknown_system():
    with pytest.raises(ValueError):
        _record(system="not_a_system")


def test_rejects_unknown_size_bucket():
    with pytest.raises(ValueError):
        _record(size="7B")


def test_rejects_unknown_axis():
    with pytest.raises(ValueError):
        _record(axis="parameter_scale")


def test_lubana_s3_may_use_graph_axis():
    """Design §3: Lubana S3 is measured on the graph-structure axis, not training."""
    rec = _record(system="lubana_below", axis="graph_param")
    assert rec.s3.axis == "graph_param"


def test_never_a_claimed_zero_field_present():
    """cp_upper is a mandatory numeric field, so 'absent' can never serialize a zero."""
    rec = _record()
    assert isinstance(rec.s2.cp_upper, float)
    assert rec.s2.cp_upper > 0.0
