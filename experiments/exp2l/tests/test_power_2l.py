# experiments/exp2l/tests/test_power_2l.py
"""power_2l: block_sd_A's shape and monotonicity (null SD ≤ declare SD
is NOT required — only finiteness and four blocks); main() refuses when
the record exists / the rung set is absent, writes once with both
tests, the block-SD line and the composite predictor sha, at tiny N."""
from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp2i import battery_2i as bi
from experiments.exp2i import power_2i as pw
from experiments.exp2k import battery_2k as bk
from experiments.exp2l import analyze_2l as an
from experiments.exp2l import battery_2l as bl
from experiments.exp2l import power_2l as pl
from experiments.exp2l.tests import full_shape as fs

R_SMALL = ("antonym", "add_base8")


@pytest.fixture(autouse=True)
def _small(monkeypatch):
    monkeypatch.setattr(pw, "N_SIM", 4)
    monkeypatch.setattr(pw, "N_PERM_POWER", 30)
    monkeypatch.setattr(pl, "N_SIM_BLOCKS", 3)
    monkeypatch.setattr(bl, "FROZEN_SHA256_2L", bl.frozen_from_disk(strict=False))


def test_block_sd_A_shape():
    strata = fs.strata()
    seal = json.loads(bk.seal_path(bk.EXP2K).read_text())
    x256 = {r: seal["counts"]["1b"][r] for r in R_SMALL}
    rng = np.random.default_rng(0)
    bits = {r: [[1 if rng.random() < c / 256 else 0 for _ in range(256)] for c in x256[r]] for r in R_SMALL}
    n_pos = {r: 100 for r in R_SMALL}
    res = pl.block_sd_A(strata, bits, x256, n_pos, R_SMALL, n_steps=bl.n_trained_13b(), n_sim=3)
    assert set(res) >= set(an.BLOCK_SD_FIELDS_2L) and res["blocks"] == 4 and res["n_sim"] == 3
    assert res["mean_block_sd_at_declare"] is not None and res["mean_block_sd_null"] is not None
    assert len(res["per_block_mean_T_at_declare"]) == 4 and 0 < res["calibrated_rho"] < 1


def test_main_writes_once_with_both_tests_and_block_sd(tmp_path):
    seal = fs.write_world_2l(tmp_path, mode="a_only")
    bl.power_path(tmp_path).unlink()
    rec = pl.main(root_2l=tmp_path, frozen_check=lambda: None, **seal)
    assert bl.power_path(tmp_path).is_file()
    assert set(rec) >= {"A", "B", "block_sd_A", "predictor_sha256", "r_primary", "primary_is_the_nine"}
    assert rec["predictor_sha256"] == bl.PREDICTOR_SHA_2L
    for t in ("A", "B"):
        assert rec[t]["n_trained_steps"] == 16 and rec[t]["declared_status"] in ("POWERED", "DECLARED UNDERPOWERED IN ADVANCE", "THIN")
        assert set(rec[t]["rungs"]) == set(fs.RUNGS_PRIMARY)
    assert an.load_power_2l(tmp_path, fs.RUNGS_PRIMARY, bl.PREDICTOR_SHA_2L)["block_sd_A"]["blocks"] == 4
    with pytest.raises(RuntimeError, match="written ONCE"):
        pl.main(root_2l=tmp_path, frozen_check=lambda: None, **seal)


def test_main_refuses_without_rung_set(tmp_path):
    seal = fs.write_world_2l(tmp_path, mode="a_only")
    bl.power_path(tmp_path).unlink()
    bl.rung_set_path(tmp_path).unlink()
    with pytest.raises(FileNotFoundError):
        pl.main(root_2l=tmp_path, frozen_check=lambda: None, **seal)
