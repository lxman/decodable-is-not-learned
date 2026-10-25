"""Synthetic unit tests for `analyses/matched-token-item-order/`."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import analyze as an  # noqa: E402
import verify_outputs as vo  # noqa: E402


def test_build_outcomes_for_rung_encodings():
    steps = (1000, 5000, 143000)
    spine_steps = (1000, 143000)
    sizes = ("410m", "1b", "1.4b", "2.8b", "6.9b", "12b")
    n_items = 6
    bits = {t: {s: [0] * n_items for s in sizes} for t in steps}

    # Item 0: solved at 1.4b, 2.8b, 6.9b, 12b at 143000 (count=4, first_size=4, no28b=3), greedy 1b=1
    for s in ("1b", "1.4b", "2.8b", "6.9b", "12b"):
        bits[143000][s][0] = 1
    # Item 1: first solved at 2.8b and 12b at 143000 (count=2, first_size=3, no28b=1), greedy 410m=0, 1b=0
    bits[143000]["2.8b"][1] = 1
    bits[143000]["12b"][1] = 1
    # Item 2: first solved at 6.9b at 143000 (count=1, first_size=2, no28b=1)
    bits[143000]["6.9b"][2] = 1
    # Item 3: first solved at 12b at 143000 (count=1, first_size=1, no28b=1)
    bits[143000]["12b"][3] = 1
    # Item 4: solved only at 410m at 143000 (outcome count=0, first_size=0, not in greedy_zero)
    bits[143000]["410m"][4] = 1
    # Item 5: solved at step 5000 on 2.8b (not on spine), 0 at 143000
    bits[5000]["2.8b"][5] = 1

    out = an.build_outcomes_for_rung(
        bits,
        steps=steps,
        spine_steps=spine_steps,
        final_step=143000,
        n_items=n_items,
    )

    assert out["y_143k_count"]["y"] == [4, 2, 1, 1, 0, 0]
    assert out["y_143k_count"]["n_pos"] == 4
    assert out["y_143k_first_size"]["y"] == [4, 3, 2, 1, 0, 0]
    assert out["y_143k_no28b"]["y"] == [3, 1, 1, 1, 0, 0]
    # Greedy-zero keep mask: items 0 and 4 had 1b=1 or 410m=1, so keep = [False, True, True, True, False, True]
    assert out["y_143k_greedy_zero"]["keep"] == [False, True, True, True, False, True]
    assert out["greedy_zero_n"] == 4
    assert out["y_143k_greedy_zero"]["n_pos"] == 3
    # Grid vs spine: item 5 has 1 hit at step 5000 (in grid, not in spine)
    assert out["y_grid_40"]["y"] == [4, 2, 1, 1, 0, 1]
    assert out["y_spine_32"]["y"] == [4, 2, 1, 1, 0, 0]


def test_composite_strata_zero_and_median_cuts():
    base = {"r1": {"strata": ["s0", "s0", "s1", "s1"]}}
    cond = {"r1": [0.0, 3.0, 0.0, 10.0]}
    z = an.composite_strata_zero_cut(base, cond, ("r1",))
    assert z["r1"]["strata"] == ["s0|0", "s0|1", "s1|0", "s1|1"]

    # median of [0, 3, 0, 10] is 1.5 -> strictly greater is [0, 1, 0, 1]
    m = an.composite_strata_median_cut(base, cond, ("r1",))
    assert m["r1"]["strata"] == ["s0|0", "s0|1", "s1|0", "s1|1"]


def test_family_bootstrap_t_reproducible_and_empty():
    empty = an.family_bootstrap_t({}, {})
    assert empty["n_rungs"] == 0
    assert empty["rung_mean"] is None

    per_rung = {"r1": 0.20, "r2": 0.40, "r3": 0.60}
    fam_of = {"r1": "fA", "r2": "fA", "r3": "fB"}
    b1 = an.family_bootstrap_t(per_rung, fam_of, n_boot=500, seed=42)
    b2 = an.family_bootstrap_t(per_rung, fam_of, n_boot=500, seed=42)
    assert b1 == b2
    assert np.isclose(b1["rung_mean"], 0.40)
    # fA mean = 0.30, fB mean = 0.60 -> equal-family mean = 0.45
    assert np.isclose(b1["family_mean"], 0.45)
    assert 0.30 <= b1["rung_mean_ci"][0] <= b1["rung_mean"] <= b1["rung_mean_ci"][1] <= 0.60


def test_evaluate_predictor_set_orientation_and_degeneracy():
    with an.pinned_imports(an.REPO):
        from experiments.exp2g import stats_2g as st

        n = 40
        x_pos = list(range(n))
        x_neg = list(reversed(range(n)))
        x_const = [0.0] * n
        y = [0] * (n // 2) + [1] * (n // 2)
        strata = {"r_good": {"strata": ["A" if i % 2 == 0 else "B" for i in range(n)]},
                  "r_thin": {"strata": ["A"] * n},
                  "r_deg": {"strata": ["A"] * n}}
        out = {
            "r_good": {"y": y, "n_pos": n // 2, "n_items": n},
            "r_thin": {"y": [1] * 3 + [0] * (n - 3), "n_pos": 3, "n_items": n},
            "r_deg": {"y": y, "n_pos": n // 2, "n_items": n},
        }
        fam = {"r_good": "f1", "r_thin": "f2", "r_deg": "f3"}

        res_pos = an.evaluate_predictor_set(
            {"r_good": x_pos, "r_thin": x_pos, "r_deg": x_const},
            out,
            strata,
            ("r_good", "r_thin", "r_deg"),
            fam,
            st,
            n_perm=200,
            n_boot=100,
        )
        assert res_pos["defined"] is True
        assert res_pos["eligible"] == ["r_good"]
        assert res_pos["thin"] == ["r_thin"]
        assert res_pos["dropped_degenerate"] == ["r_deg"]
        assert np.isclose(res_pos["stratified"]["T"], 1.0)
        assert res_pos["stratified"]["p"] < 0.02

        res_neg = an.evaluate_predictor_set(
            {"r_good": x_neg},
            {"r_good": out["r_good"]},
            {"r_good": strata["r_good"]},
            ("r_good",),
            fam,
            st,
            n_perm=200,
            n_boot=100,
        )
        assert np.isclose(res_neg["stratified"]["T"], -1.0)

        all_res = an.evaluate_all_rungs_unstratified(
            {"r_good": x_pos, "r_thin": x_pos, "r_deg": x_const},
            out,
            ("r_good", "r_thin", "r_deg"),
            fam,
            st,
        )
        assert all_res["per_rung"]["r_good"]["informative"] is True
        assert all_res["per_rung"]["r_good"]["ge20"] is True
        assert all_res["per_rung"]["r_thin"]["informative"] is True
        assert all_res["per_rung"]["r_thin"]["ge20"] is False
        assert all_res["per_rung"]["r_deg"]["informative"] is False
        assert all_res["informative_summary"]["n_rungs"] == 2
        assert all_res["ge20_summary"]["n_rungs"] == 1


def test_write_once_and_tamper_detection(tmp_path: Path):
    # Construct a minimal synthetic summary matching the schema expected by verify_outputs
    fake_pred_res = {
        "defined": True,
        "eligible": ["add3_mid"],
        "thin": [],
        "dropped_degenerate": [],
        "stratified": {"T": 0.5, "p": 0.01, "n_ge": 1, "n_perm": 100, "null_mean": 0.0, "null_sd": 0.1},
        "raw": {"T": 0.5, "p": 0.01, "n_ge": 1, "n_perm": 100, "null_mean": 0.0, "null_sd": 0.1},
        "pooled_d": 0.5,
        "raw_pooled_d": 0.5,
        "family_bootstrap": {
            "n_rungs": 1,
            "n_families": 1,
            "families": {"arithmetic": 1},
            "rung_mean": 0.5,
            "rung_mean_ci": [0.5, 0.5],
            "family_mean": 0.5,
            "family_mean_ci": [0.5, 0.5],
        },
        "per_rung": {
            "add3_mid": {
                "d": 0.5,
                "n_pairs": 100,
                "n_strata_used": 2,
                "ci_lo": 0.3,
                "ci_hi": 0.7,
                "raw_d": 0.5,
                "raw_n_pairs": 100,
                "n_items": 500,
                "n_pos": 50,
            }
        },
    }
    rcap_block = {
        k: fake_pred_res
        for k in (
            "pythia_1b_k256",
            "olmo2_1b_k64",
            "pythia_1b_k64",
            "pythia_410m_k256",
            "pythia_410m_k64",
            "probe_1b",
            "probe_410m",
            "wrong_prior_1b",
            "wrong_prior_olmo1b",
        )
    }
    r11_block = {
        k: fake_pred_res
        for k in ("pythia_1b_k64", "pythia_410m_k64", "probe_1b", "probe_410m")
    }
    sub_cap = {
        k: fake_pred_res
        for k in ("pythia_1b_k256", "olmo2_1b_k64", "pythia_1b_k64", "pythia_410m_k256", "probe_1b")
    }
    sub_11 = {k: fake_pred_res for k in ("pythia_1b_k64", "pythia_410m_k64", "probe_1b")}
    by_size_cap = {
        s: {k: fake_pred_res for k in ("pythia_1b_k256", "olmo2_1b_k64", "pythia_1b_k64", "probe_1b")}
        for s in an.OUTCOME_SIZES
    }
    by_size_11 = {
        s: {k: fake_pred_res for k in ("pythia_1b_k64", "probe_1b")}
        for s in an.OUTCOME_SIZES
    }
    curve = {
        str(t): {
            "step": t,
            "tokens": t * an.TOKENS_PER_STEP,
            "rcap": {k: fake_pred_res for k in ("pythia_1b_k256", "olmo2_1b_k64", "pythia_1b_k64", "probe_1b")},
            "rpred11": {k: fake_pred_res for k in ("pythia_1b_k64", "probe_1b")},
        }
        for t in an.STEPS
    }
    cond = {
        k: fake_pred_res
        for k in (
            "probe_1b_beyond_pythia_1b_k256_rcap",
            "pythia_1b_k256_beyond_probe_1b_rcap",
            "probe_1b_beyond_pythia_1b_k64_rpred11",
            "pythia_1b_k64_beyond_probe_1b_rpred11",
            "pythia_1b_k256_beyond_olmo2_1b_k64_zero_rcap",
            "pythia_1b_k256_beyond_olmo2_1b_k64_median_rcap",
            "olmo2_1b_k64_beyond_pythia_1b_k256_zero_rcap",
            "olmo2_1b_k64_beyond_pythia_1b_k256_median_rcap",
        )
    }
    all34_per_rung = {
        f"r{i:02d}": {
            "rung": f"r{i:02d}",
            "family": "arithmetic",
            "n_pos": 50,
            "n_neg": 450,
            "x_pos": 30,
            "n_pairs": 100,
            "raw_d": 0.4,
            "informative": True,
            "ge20": True,
        }
        for i in range(an.N_RUNGS)
    }
    all34_entry = {
        "per_rung": all34_per_rung,
        "informative_summary": fake_pred_res["family_bootstrap"],
        "ge20_summary": fake_pred_res["family_bootstrap"],
    }
    rung_meta = {
        r: {
            "rung": r,
            "family": "arithmetic",
            "in_r_cap": r in an.R_CAP,
            "n_pos_143k": 50,
            "greedy_zero_n": 400,
            "greedy_zero_n_pos": 25,
            "counts_143k": {s: 50 for s in an.SIZES},
        }
        for r in an.R_PRED11
    }

    summary = {
        "source_commit": an.SOURCE,
        "parameters": {
            "sizes": list(an.SIZES),
            "predictor_sizes": list(an.PREDICTOR_SIZES),
            "outcome_sizes": list(an.OUTCOME_SIZES),
            "no28b_sizes": list(an.NO28B_SIZES),
            "steps": list(an.STEPS),
            "spine_steps": list(an.SPINE_STEPS),
            "final_step": an.FINAL_STEP,
            "tokens_per_step": an.TOKENS_PER_STEP,
            "r_cap": list(an.R_CAP),
            "r_pred11": list(an.R_PRED11),
            "n_items": an.N_ITEMS,
            "n_perm": 100,
            "perm_seed": an.PERM_SEED,
            "n_boot": 100,
            "family_boot_b": 100,
            "family_boot_seed": an.FAMILY_BOOT_SEED,
        },
        "rung_meta_143k": rung_meta,
        "primary_rcap_143k": rcap_block,
        "primary_rpred11_143k": r11_block,
        "first_size_rcap_143k": sub_cap,
        "first_size_rpred11_143k": sub_11,
        "greedy_zero_rcap_143k": sub_cap,
        "greedy_zero_rpred11_143k": sub_11,
        "by_size_rcap_143k": by_size_cap,
        "by_size_rpred11_143k": by_size_11,
        "no28b_rcap_143k": sub_cap,
        "no28b_rpred11_143k": sub_11,
        "checkpoint_curve": curve,
        "grid_40_rcap": sub_cap,
        "grid_40_rpred11": sub_11,
        "spine_32_rcap": sub_cap,
        "spine_32_rpred11": sub_11,
        "conditioning_143k": cond,
        "all_rungs_143k": {"pythia_1b_k64": all34_entry, "pythia_410m_k64": all34_entry},
    }

    out_dir = tmp_path / "results"
    an.write_results_atomic(out_dir, summary, {"fake.py": "0" * 64})
    info = vo.verify_results_dir(out_dir)
    assert info["verified_outputs"] == 6

    # Write-once check: second write raises FileExistsError
    with pytest.raises(FileExistsError):
        an.write_results_atomic(out_dir, summary, {"fake.py": "0" * 64})

    # Tamper detection check: altering REPORT.md raises ValueError in verify_results_dir
    (out_dir / "REPORT.md").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(ValueError, match="output sha256 mismatch"):
        vo.verify_results_dir(out_dir)
