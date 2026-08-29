# experiments/exp2k/tests/test_seal_2k.py
import json
import pytest

from experiments.exp2k import analyze_2k as an
from experiments.exp2k import battery_2k as bk
from experiments.exp2k.run import seal_2k
from experiments.exp2k.tests import full_shape as fs


def test_seal_writes_once_reproduces_counts_and_refuses_after(tmp_path):
    fs.write_world_2k(tmp_path, world="null")            # writes the seal through seal_2k
    s = json.loads(bk.seal_path(tmp_path).read_text())
    assert s["tag"] == bk.SEAL_TAG_2K and set(s["counts"]) == set(bk.SIZES_2K)
    assert s["sha256"] == an.seal_sha_of(s["files"])
    assert all(s["gate1"][sz][r]["n_diffs"] == 0 for sz in bk.SIZES_2K for r in bk.R_CAP_DESIGN)
    with pytest.raises(RuntimeError, match="already exists"):
        seal_2k.seal_predictor(tmp_path, **fs._TAG_OK)


def test_seal_refuses_halt_missing_cell_and_gate1_diff(tmp_path):
    fs.write_world_2k(tmp_path, world="null")
    bk.seal_path(tmp_path).unlink()
    m = bk.halt_marker_path(tmp_path, "1b", "odd6")
    m.write_text("{}")
    with pytest.raises(RuntimeError, match="halt"):
        seal_2k.seal_predictor(tmp_path, **fs._TAG_OK)
    m.unlink()
    p = bk.tier_draws_path(tmp_path, "1b", "sub_base8")
    rows = bk.read_rows_2k(p)
    rows[0]["draws"]["0"][0] += "!"
    fs.write_draws(p, rows)
    with pytest.raises(RuntimeError, match="refusing to seal"):
        seal_2k.seal_predictor(tmp_path, **fs._TAG_OK)
    bk.tier_record_path(tmp_path, "410m", "antonym").unlink()
    with pytest.raises(RuntimeError, match="missing a record"):
        seal_2k.seal_predictor(tmp_path, **fs._TAG_OK)
