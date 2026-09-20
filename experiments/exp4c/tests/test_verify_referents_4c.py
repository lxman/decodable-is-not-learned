# experiments/exp4c/tests/test_verify_referents_4c.py
"""Fix round 2, item 5: `verify_referents_4c.py`'s item 11 (`_c11`)
compares `results/power_4c.json` to a fresh `power_4c.compute()` the
same way `analyze_4c._reproduce_power_4c` does — restricted to the
keys `rec2` happens to have, so an extra committed key passed silently
before the byte comparison ever ran. `_c1` is exercised separately
(item 3) by the real cold battery, not here, since its whole point is
verifying the REAL committed 68-file pin set — a fast test would just
duplicate `bc.check_frozen_4c()`'s own coverage."""
from __future__ import annotations

import json

import pytest

from experiments.exp4c import verify_referents_4c as vr


def test_c11_catches_an_extra_key_in_the_committed_power_record(tmp_path, monkeypatch):
    monkeypatch.setattr(vr, "EXP4C", tmp_path)
    structure = vr.pw4c.cell_structure_4c()
    rec = vr.pw4c.compute(structure, n_sim=50, seed=0)
    rec["a_key_compute_never_produces"] = 1
    results = tmp_path / "results"
    results.mkdir()
    (results / "power_4c.json").write_text(json.dumps(rec))
    with pytest.raises(AssertionError, match="a_key_compute_never_produces"):
        vr._c11({})


def test_c11_catches_a_missing_key_in_the_committed_power_record(tmp_path, monkeypatch):
    monkeypatch.setattr(vr, "EXP4C", tmp_path)
    structure = vr.pw4c.cell_structure_4c()
    rec = vr.pw4c.compute(structure, n_sim=50, seed=0)
    del rec["arms"]
    results = tmp_path / "results"
    results.mkdir()
    (results / "power_4c.json").write_text(json.dumps(rec))
    with pytest.raises(AssertionError, match="arms"):
        vr._c11({})


def test_c11_skips_when_no_power_record_is_on_disk(tmp_path, monkeypatch):
    monkeypatch.setattr(vr, "EXP4C", tmp_path)
    assert vr._c11({}) == "SKIP"
