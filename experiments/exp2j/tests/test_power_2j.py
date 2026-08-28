# experiments/exp2j/tests/test_power_2j.py
"""power_2j.main: writes the primary's power record ONCE from 2i's
machinery on a full synthetic 2i tree (`full_shape.write_world_2j`),
refuses a second write, and carries the base-strata reference literals
2i's own committed `power_2i.json` (Test B) supplies — read from the
committed file in this test, not re-typed as a second literal."""
from __future__ import annotations

import json

import pytest

from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2j import power_2j as pw2j
from experiments.exp2j.tests import full_shape as fs


def test_main_writes_once_and_matches_2i_reference(tmp_path, monkeypatch):
    monkeypatch.setattr(pw2j.pw, "N_SIM", 4)
    monkeypatch.setattr(pw2j.pw, "N_PERM_POWER", 10)
    monkeypatch.setattr(pw2j.pw, "D_TARGETS", (0.15,))

    world_root = tmp_path / "world"
    fs.write_world_2j(world_root, world="residual")
    rung_set = json.loads(bi.rung_set_path(world_root).read_text())
    r_cap = tuple(rung_set["R_CAP"])

    out_path = tmp_path / "power_out.json"
    rec = pw2j.main(out_path=out_path, root_2i=world_root, root_2j=tmp_path)

    assert out_path.is_file()
    assert rec["primary"]["declared_status"] in an2i.DECLARED_STATUSES_2I
    assert set(rec["primary"]["rungs"]) == set(r_cap)
    assert set(rec["composite_report"]) == set(r_cap)
    assert set(rec["n_composite_strata"]) == set(r_cap)
    assert rec["shape_note"] == pw2j.pw.SHAPE_NOTE_2I
    assert rec["note"] == pw2j.NOTE_2J

    with pytest.raises(RuntimeError, match="written ONCE"):
        pw2j.main(out_path=out_path, root_2i=world_root, root_2j=tmp_path)

    # the base-strata reference: 2i's own committed Test B power record,
    # read here (not re-typed as a second literal that could drift from
    # the committed file's actual value).
    committed = json.loads(bi.power_path(bi.EXP2I).read_text())
    assert rec["base_strata_reference_2i_B"]["null_sd_T"] == \
        round(committed["B"]["null"]["null_sd_T"], 4)
    assert rec["base_strata_reference_2i_B"]["min_detectable_T"] == \
        round(committed["B"]["min_detectable_T"], 5)


def test_main_refuses_when_out_path_exists(tmp_path):
    out_path = tmp_path / "power_out.json"
    out_path.write_text("{}")
    with pytest.raises(RuntimeError, match="written ONCE"):
        pw2j.main(out_path=out_path, root_2i=bi.EXP2I, root_2j=tmp_path)
