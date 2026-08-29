# experiments/exp2k/tests/test_power_2k.py
import json
import pytest

from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2k import battery_2k as bk
from experiments.exp2k import power_2k as pw2k
from experiments.exp2k.tests import full_shape as fs


def test_main_writes_once_carries_the_seal_sha_and_2i_reference(tmp_path, monkeypatch):
    monkeypatch.setattr(pw2k.pw, "N_SIM", 4)
    monkeypatch.setattr(pw2k.pw, "N_PERM_POWER", 10)
    monkeypatch.setattr(pw2k.pw, "D_TARGETS", (0.15,))
    fs.write_world_2k(tmp_path, world="density")
    bk.power_path(tmp_path).unlink()                      # the world wrote a literal; main writes the real one
    rec = pw2k.main(root_2i=tmp_path, root_2k=tmp_path, **fs._TAG_OK)
    assert bk.power_path(tmp_path).is_file()
    assert rec["primary"]["declared_status"] in an2i.DECLARED_STATUSES_2I
    assert set(rec["primary"]["rungs"]) == set(bk.R_CAP_DESIGN)
    assert rec["predictor_sha256"] == json.loads(bk.seal_path(tmp_path).read_text())["sha256"]
    committed = json.loads(bi.power_path(bi.EXP2I).read_text())["A"]
    assert rec["reference_2i_A_k64"]["null_sd_T"] == committed["null"]["null_sd_T"]
    assert rec["reference_2i_A_k64"]["p_fires_at_D_0.10"] == committed["targets"]["0.1"]["p_fires"]
    with pytest.raises(RuntimeError, match="written ONCE"):
        pw2k.main(root_2i=tmp_path, root_2k=tmp_path, **fs._TAG_OK)


def test_main_refuses_without_a_seal(tmp_path):
    with pytest.raises((FileNotFoundError, RuntimeError)):
        pw2k.main(root_2i=bi.EXP2I, root_2k=tmp_path, **fs._TAG_OK)
