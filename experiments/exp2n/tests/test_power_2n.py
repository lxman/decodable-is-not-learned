# experiments/exp2n/tests/test_power_2n.py
"""power_2n: block_sd_A's shape; delta_sd_2n's shape and formula; main()
refuses when the record exists / the rung set is absent, writes once
with both tests ON THE BASE STRATA, the block-SD line, the delta_sd
block and the composite predictor sha, at tiny N."""
from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2i import power_2i as pw
from experiments.exp2k import battery_2k as bk
from experiments.exp2n import analyze_2n as an
from experiments.exp2n import battery_2n as bn
from experiments.exp2n import power_2n as pm
from experiments.exp2n.tests import full_shape as fs

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
    res = pm.block_sd_A(strata, bits, x256, {r: 100 for r in R_SMALL}, R_SMALL, n_steps=bn.n_trained_comma(), n_sim=3)
    assert set(res) >= set(an.BLOCK_SD_FIELDS_2N) and res["blocks"] == 4 and res["n_sim"] == 3
    assert res["mean_block_sd_at_declare"] is not None and res["mean_block_sd_null"] is not None
    assert len(res["per_block_mean_T_at_declare"]) == 4 and 0 < res["calibrated_rho"] < 1


def test_delta_sd_2n_shape_and_formula():
    # Test-side correction: `_small` is already `autouse=True` on every
    # test in this module (this pytest version raises on a direct
    # fixture call — "Fixture ... called directly" — so the brief's
    # literal `_small(monkeypatch)` line is redundant and breaks here).
    strata = fs.strata()
    x_a256, x_b = fs.x_a256_real(), fs.x_b_real()
    bits_b, x_a64 = fs.bits_b_real(), bi.sampler_counts_pythia("1b", R_SMALL)
    n_pos = {r: 100 for r in R_SMALL}
    d = pm.delta_sd_2n(strata, bits_b, x_a64, x_a256, x_b, n_pos, R_SMALL, n_steps=bn.n_trained_comma(),
                       n_sim=3, n_boot=5, seed=1)
    assert set(d) >= set(an.DELTA_SD_FIELDS_2N) and d["n_sim"] == 3 and d["rungs"] == list(R_SMALL)
    assert d["formula"] == pm.DELTA_FORMULA_2N == ("min_detectable_delta = 2.63 * delta_boot_sd_null (normal "
                                                    "approximation: CI95 excludes zero with power .75)")
    assert abs(d["min_detectable_delta"] - 2.63 * d["delta_boot_sd_null"]) < 1e-12
    assert set(d["k_by_rung"]) == set(R_SMALL) and d["delta_null_sd"] >= 0


def test_main_writes_once_with_both_tests_on_base_strata(tmp_path, monkeypatch):
    seal = fs.write_world_2n(tmp_path, mode="pythia_only")
    bn.power_path(tmp_path).unlink()
    calls = []
    real = pw._one_test_power

    def _spy(strata, x_real, n_pos, rungs, *, n_steps):
        calls.append(strata)
        return real(strata, x_real, n_pos, rungs, n_steps=n_steps)

    monkeypatch.setattr(pw, "_one_test_power", _spy)
    # Test-side correction (2m's Task 4 pattern, ruling 5): FROZEN_SHA256_2N
    # is still empty pending Task 5, so `main()`'s own frozen-module check
    # needs a no-op override here; Task 5 removes this bypass once the
    # real pin exists (2m's history: "the bypasses this defaulted while
    # they were empty are gone").
    frozen_check = None if bn.FROZEN_SHA256_2N else (lambda: None)
    rec = pm.main(root_2n=tmp_path, frozen_check=frozen_check, **seal)
    assert bn.power_path(tmp_path).is_file()
    assert len(calls) == 2 and calls[0] is calls[1]                  # B on the SAME base strata as A, not a composite
    assert set(rec) >= {"A", "B", "block_sd_A", "delta_sd", "predictor_sha256", "r_primary", "primary_is_the_nine"}
    assert rec["predictor_sha256"] == bn.PREDICTOR_SHA_2N and rec["calibration_note"] == an.CALIBRATION_SENTENCE_2N
    for t in ("A", "B"):
        assert rec[t]["n_trained_steps"] == 24 and rec[t]["declared_status"] in an2i.DECLARED_STATUSES_2I
        assert set(rec[t]["rungs"]) == set(fs.RUNGS_PRIMARY)
    assert an.load_power_2n(tmp_path, fs.RUNGS_PRIMARY, bn.PREDICTOR_SHA_2N)["block_sd_A"]["blocks"] == 4
    # Task-4 review carry-over (5): the seam between power_2n's writer and
    # the analyzer's re-derivation of its claims — the REAL record through
    # `check_power_claims_2n` on the same base strata, zero disagreements.
    strata = fs.strata()
    x256 = {r: v for r, v in fs.x_a256_real().items() if r in fs.RUNGS_PRIMARY}
    x_b = {r: v for r, v in fs.x_b_real().items() if r in fs.RUNGS_PRIMARY}
    x_a64 = {r: v for r, v in fs.x_a64_real().items() if r in fs.RUNGS_PRIMARY}
    bits_b = {r: v for r, v in fs.bits_b_real().items() if r in fs.RUNGS_PRIMARY}
    stage1 = an.load_endpoint_which_2n(tmp_path, "stage1_final", fs.battery(), fs.verify_fn(),
                                       entry=bn.entry_which_comma(fs.manifest(), "stage1_final"))
    assert an.check_power_claims_2n(rec, x256, x_b, strata, fs.RUNGS_PRIMARY, stage1,
                                    bits_b=bits_b, x_a64=x_a64) == []
    # the delta_sd block carries every field, round-tripped through the
    # committed JSON bytes (dial h)
    rec_disk = json.loads(bn.power_path(tmp_path).read_text())
    assert set(rec_disk["delta_sd"]) >= set(an.DELTA_SD_FIELDS_2N)
    with pytest.raises(RuntimeError, match="written ONCE"):
        pm.main(root_2n=tmp_path, frozen_check=frozen_check, **seal)


def test_main_refuses_without_rung_set(tmp_path):
    seal = fs.write_world_2n(tmp_path, mode="pythia_only")
    bn.power_path(tmp_path).unlink()
    bn.rung_set_path(tmp_path).unlink()
    frozen_check = None if bn.FROZEN_SHA256_2N else (lambda: None)
    with pytest.raises(FileNotFoundError):
        pm.main(root_2n=tmp_path, frozen_check=frozen_check, **seal)
