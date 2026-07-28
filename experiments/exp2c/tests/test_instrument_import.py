import math


def test_frozen_instrument_reexported():
    from experiments.exp2c import instrument
    assert callable(instrument.probe_starved)
    assert instrument.probe_starved.__module__ == "probe_starved"


def test_floors_exact():
    from experiments.exp2c import instrument
    assert math.isclose(instrument.FLOORS["410m"], 18 / 2501)
    assert math.isclose(instrument.FLOORS["1b"], 14 / 2501)
