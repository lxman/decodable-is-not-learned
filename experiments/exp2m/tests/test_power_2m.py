# experiments/exp2m/tests/test_power_2m.py
"""power_2m: block_sd_A's shape; main() refuses when the record exists
/ the rung set is absent, writes once with both tests ON THE BASE
STRATA, the block-SD line and the composite predictor sha, at tiny N."""
from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import power_2i as pw
from experiments.exp2k import battery_2k as bk
from experiments.exp2m import analyze_2m as an
from experiments.exp2m import battery_2m as bm
from experiments.exp2m import power_2m as pm
from experiments.exp2m.tests import full_shape as fs

R_SMALL = ("antonym", "add_base8")


@pytest.fixture(autouse=True)
def _small(monkeypatch):
    monkeypatch.setattr(pw, "N_SIM", 4)
    monkeypatch.setattr(pw, "N_PERM_POWER", 30)
    monkeypatch.setattr(pm, "N_SIM_BLOCKS", 3)


def test_block_sd_A_shape():
    strata = fs.strata()
    seal = json.loads(bk.seal_path(bk.EXP2K).read_text())
    x256 = {r: seal["counts"]["1b"][r] for r in R_SMALL}
    rng = np.random.default_rng(0)
    bits = {r: [[1 if rng.random() < c / 256 else 0 for _ in range(256)] for c in x256[r]] for r in R_SMALL}
    res = pm.block_sd_A(strata, bits, x256, {r: 100 for r in R_SMALL}, R_SMALL, n_steps=bm.n_trained_3b(), n_sim=3)
    assert set(res) >= set(an.BLOCK_SD_FIELDS_2M) and res["blocks"] == 4 and res["n_sim"] == 3
    assert res["mean_block_sd_at_declare"] is not None and res["mean_block_sd_null"] is not None
    assert len(res["per_block_mean_T_at_declare"]) == 4 and 0 < res["calibrated_rho"] < 1


def test_main_writes_once_with_both_tests_on_base_strata(tmp_path, monkeypatch):
    seal = fs.write_world_2m(tmp_path, mode="pythia_only")
    bm.power_path(tmp_path).unlink()
    calls = []
    real = pw._one_test_power

    def _spy(strata, x_real, n_pos, rungs, *, n_steps):
        calls.append(strata)
        return real(strata, x_real, n_pos, rungs, n_steps=n_steps)

    monkeypatch.setattr(pw, "_one_test_power", _spy)
    rec = pm.main(root_2m=tmp_path, **seal)
    assert bm.power_path(tmp_path).is_file()
    assert len(calls) == 2 and calls[0] is calls[1]                  # B on the SAME base strata as A, not a composite
    assert set(rec) >= {"A", "B", "block_sd_A", "predictor_sha256", "r_primary", "primary_is_the_nine"}
    assert rec["predictor_sha256"] == bm.PREDICTOR_SHA_2M and rec["calibration_note"] == an.CALIBRATION_SENTENCE_2M
    for t in ("A", "B"):
        assert rec[t]["n_trained_steps"] == 26 and rec[t]["declared_status"] in an2i.DECLARED_STATUSES_2I
        assert set(rec[t]["rungs"]) == set(fs.RUNGS_PRIMARY)
    assert an.load_power_2m(tmp_path, fs.RUNGS_PRIMARY, bm.PREDICTOR_SHA_2M)["block_sd_A"]["blocks"] == 4
    # Task-4 review carry-over (5): the seam between power_2m's writer and
    # the analyzer's re-derivation of its claims — the REAL record through
    # `check_power_claims_2m` on the same base strata, zero disagreements.
    strata = fs.strata()
    x256 = {r: v for r, v in fs.x_a256_real().items() if r in fs.RUNGS_PRIMARY}
    x_b = {r: v for r, v in fs.x_b_real().items() if r in fs.RUNGS_PRIMARY}
    stage1 = an.load_endpoint_which_2m(tmp_path, "stage1_final", fs.battery(), fs.verify_fn(),
                                       entry=bm.entry_which_3b(fs.manifest(), "stage1_final"))
    assert an.check_power_claims_2m(rec, x256, x_b, strata, fs.RUNGS_PRIMARY, stage1) == []
    with pytest.raises(RuntimeError, match="written ONCE"):
        pm.main(root_2m=tmp_path, **seal)


def test_main_refuses_without_rung_set(tmp_path):
    seal = fs.write_world_2m(tmp_path, mode="pythia_only")
    bm.power_path(tmp_path).unlink()
    bm.rung_set_path(tmp_path).unlink()
    with pytest.raises(FileNotFoundError):
        pm.main(root_2m=tmp_path, **seal)
