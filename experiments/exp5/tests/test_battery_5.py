import json
import math

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5


def test_sizes_pairs_and_spine_literals():
    assert b5.SIZES_5 == ("160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b")
    assert len(b5.PAIRS_5) == 21
    assert all(b5.SIZES_5.index(s) < b5.SIZES_5.index(L) for s, L in b5.PAIRS_5)
    assert b5.SPINE_5 == (1000, 2000, 4000, 8000, 16000, 32000, 64000, 100000, 143000)
    assert b5.FINAL_STEP_5 == 143000 and b5.S11_STEP_5 == 142000
    assert b5.T_BAR_5 == 0.01 and b5.ALPHA_5 == 0.01 and b5.MODIFIER_ALPHA_5 == 0.05
    assert b5.MIN_LIVE_CELLS_5 == 20 and b5.MIN_LIVE_RUNGS_5 == 5 and b5.MODIFIER_MIN_CELLS_5 == 8
    assert b5.GATE1_TOL_PER_RUNG_5 == 15 and b5.GATE1_TOL_SUM_5 == 120
    assert b5.GATE1_BENCH_5["max_abs_diff"] == 8 and b5.GATE1_BENCH_5["sum_abs_diff"] == 57


def test_main_shas_agree_with_2c_where_2c_pinned():
    from models import PYTHIA_SHAS
    for size, sha in PYTHIA_SHAS.items():
        assert b5.MAIN_SHA_5[size] == sha
    assert b5.MAIN_SHA_5["160m"] == "50f5173d932e8e61f858120bcb800b97af589f46"
    assert b5.MAIN_SHA_5["1.4b"] == "fedc38a16eea3bd36a96b906d78d11d2ce18ed79"
    assert set(b5.MAIN_SHA_5) == set(b5.SIZES_5)


def test_rung_types_partition_the_battery_and_match_exp4():
    from experiments.exp4 import analyze_4
    assert set(b5.RUNG_TYPE_5) == set(bt.RUNGS)
    assert b5.RUNG_TYPE_5 == analyze_4.RUNG_TYPE_4
    assert set(b5.RUNG_TYPE_5.values()) == {"arithmetic", "option", "string"}


def _inv(sizes=("160m",), steps=(0, 1, 2, 1000, 2000, 3000, 143000), stale=None, nocand=None):
    """A synthetic Hub inventory in checkpoints_2g's shape: every revision
    a unique single safetensors, except `stale` (a copy of main's file
    beside its own bin) and `nocand` (main's file only)."""
    inv = {}
    for size in sizes:
        repo = b5.REPO_OF_5[size]
        table = {}
        main_sha = f"main-{size}"
        table["main"] = {"commit": b5.MAIN_SHA_5[size],
                         "files": {"model.safetensors": [main_sha, 10]}}
        for k in steps:
            rev = f"step{k}"
            if k == 143000:
                table[rev] = {"commit": f"c{k}", "files": {"pytorch_model.bin": [f"bin-{size}-{k}", 10]}}
            elif stale and k in stale:
                table[rev] = {"commit": f"c{k}", "files": {"model.safetensors": [main_sha, 10],
                                                          "pytorch_model.bin": [f"bin-{size}-143000", 10]}}
            elif nocand and k in nocand:
                table[rev] = {"commit": f"c{k}", "files": {"model.safetensors": [main_sha, 10]}}
            else:
                table[rev] = {"commit": f"c{k}", "files": {"model.safetensors": [f"st-{size}-{k}", 10]}}
        inv[repo] = table
    return inv


def test_manifest_available_list_excludes_step0_duplicates_and_no_candidate():
    inv = _inv(steps=(0, 1, 2, 1000, 2000, 3000, 64000, 143000), stale=(64000,), nocand=(3000,))
    m = b5.build_manifest_5("160m", inv)
    assert m["available"] == [1, 2, 1000, 2000, 143000]
    assert "64000" in m["excluded"] and m["excluded"]["64000"]["duplicates"] == ["step143000"]
    assert "3000" in m["excluded"] and m["excluded"]["3000"]["reason"].startswith("no candidate")
    assert m["entries"]["143000"]["revision"] == "main"
    assert m["entries"]["143000"]["commit"] == b5.MAIN_SHA_5["160m"]
    assert "0" not in m["entries"] and m["step0"]["commit"] == "c0"
    assert m["hub_step143000"]["signature_equals_main"] in (True, False)


def test_manifest_refuses_wrong_main_commit():
    inv = _inv()
    inv[b5.REPO_OF_5["160m"]]["main"]["commit"] = "deadbeef"
    with pytest.raises(ValueError, match="pinned main commit"):
        b5.build_manifest_5("160m", inv)


def test_spine_substitutes_an_excluded_step_with_the_next_available():
    inv = _inv(steps=(1000, 2000, 4000, 8000, 16000, 32000, 64000, 65000, 66000, 100000, 143000),
               stale=(64000,))
    m = {"160m": b5.build_manifest_5("160m", inv)}
    assert b5.spine_5(m, "160m") == (1000, 2000, 4000, 8000, 16000, 32000, 65000, 100000, 143000)
    assert b5.spine_substitutions_5(m, "160m") == {"64000": 65000}


def test_spine_refuses_when_no_step_above_an_excluded_one():
    inv = _inv(steps=(1000, 2000, 4000, 8000, 16000, 32000, 64000, 143000), stale=(64000,))
    m = {"160m": b5.build_manifest_5("160m", inv)}
    # 100000 is absent from this synthetic list, so the next available step above the excluded
    # 64000 is 143000 — the final itself — and the substitution would collapse two spine points
    with pytest.raises(ValueError, match="spine"):
        b5.spine_5(m, "160m")


def test_lr_schedule_pins():
    assert b5.lr_at_5("12b", 0) == 0.0
    assert math.isclose(b5.lr_at_5("12b", 1430), 1.2e-4)
    assert math.isclose(b5.lr_at_5("12b", 143000), 1.2e-5)
    assert math.isclose(b5.lr_at_5("160m", 143000), 6.0e-5)
    assert b5.tokens_seen_5(143000) == 143000 * 2_097_152


def test_paths_and_unit_files():
    d = b5.unit_dir_5("/r", "12b", 1000)
    assert str(d).endswith("results/units/12b/step1000")
    assert b5.unit_record_path_5("/r", "12b", 1000).name == "_unit.json"
    assert len(b5.unit_files_5()) == 36 and "_unit.json" not in b5.unit_files_5()
    assert b5.halt_marker_path_5("/r", "12b").name == "HALTED"


def test_tolerance_failures():
    ref = {r: 100 for r in bt.RUNGS}
    ok = dict(ref); ok["antonym"] = 115
    assert b5.tolerance_failures_5(ok, ref, label="x") == []
    bad = dict(ref); bad["antonym"] = 116
    assert len(b5.tolerance_failures_5(bad, ref, label="x")) == 1
    spread = {r: 104 for r in bt.RUNGS}          # Σ|Δ| = 136 > 120, every rung ≤ 15
    assert any("sum" in f for f in b5.tolerance_failures_5(spread, ref, label="x"))
    missing = dict(ref); del missing["antonym"]
    assert any("antonym" in f for f in b5.tolerance_failures_5(missing, ref, label="x"))


def test_clears_5_is_a_significance_test_not_a_bare_rate_comparison():
    """Task 6 mutation kill: `clears_5` is the one-sided exact binomial
    bar (p < .01 AND rate > floor, both STRICT) — not a plain rate >=
    floor reading. A count exactly AT the floor must read False (rate >
    floor fails on equality) regardless of any p-value; a mutant that
    reads the rate alone reads it True."""
    assert b5.clears_5(count=50, floor=0.1, n=500) is False
    # a rate comfortably above the floor with n=500 is both statistically
    # significant and numerically over the floor — clears under both readings
    assert b5.clears_5(count=90, floor=0.1, n=500) is True


def test_mac_referents_exist_for_five_sizes_and_none_for_two():
    for size in ("410m", "1b", "2.8b", "6.9b", "12b"):
        c = b5.mac_final_counts_5(size)
        assert set(c) == set(bt.RUNGS) and all(isinstance(v, int) for v in c.values())
    assert b5.mac_final_counts_5("160m") is None and b5.mac_final_counts_5("1.4b") is None
    assert b5.gate1_interior_steps_5("2.8b") == (1000, 2000, 4000, 8000, 16000, 32000, 100000)
    assert b5.gate1_interior_steps_5("6.9b") == (1000, 2000, 4000, 8000, 16000, 32000, 64000, 100000)
    assert b5.gate1_interior_steps_5("12b") == ()
    assert set(b5.mac_interior_counts_5("6.9b", 64000)) == set(bt.RUNGS)
    assert b5.mac_interior_counts_5("2.8b", 64000) is None


def test_require_prereg_5_refuses_missing_tag_and_drift(tmp_path):
    with pytest.raises(RuntimeError, match="does not exist"):
        b5.require_prereg_5(tag_exists=lambda t: False, blob_sha=lambda t, r: None)
    existing = tuple(r for r in b5.INSTRUMENT_BLOBS_5 if (b5.REPO / r).is_file())
    good = b5.require_prereg_5(tag_exists=lambda t: True,
                               blob_sha=lambda t, r: bg.sha256_file(b5.REPO / r),
                               blobs=existing)
    assert good["tag"] == "exp5-preregistered" and set(good["instrument_blobs"]) == set(existing)
    with pytest.raises(RuntimeError, match="does not bind"):
        b5.require_prereg_5(tag_exists=lambda t: True, blob_sha=lambda t, r: "0" * 64, blobs=existing)


def test_require_targets_seal_never_raises(tmp_path):
    out = b5.require_targets_seal_5(tmp_path, tag_exists=lambda t: False)
    assert out["failures"] and "does not exist" in out["failures"][0]
    out = b5.require_targets_seal_5(tmp_path, tag_exists=lambda t: (_ for _ in ()).throw(OSError("x")))
    assert out["failures"]


def test_host_record_failures():
    good = {"stack": {"torch": "2.12.1+cu130", "transformers": "5.13.0", "numpy": "2.4.6",
                      "safetensors": "0.8.0", "tokenizers": "0.22.2", "huggingface_hub": "1.22.0"},
            "device": "cuda", "gpu": "NVIDIA A100 80GB PCIe", "python": "3.11.16",
            "transports": {"classic_mbps": 11.0, "xet_mbps": 300.0, "used": "xet"},
            "hf_hub_disable_xet": None}
    assert b5.host_record_failures_5(good) == []
    bad = dict(good); bad["transports"] = {"classic_mbps": 11.0}
    assert b5.host_record_failures_5(bad)
    bad2 = dict(good); bad2["stack"] = {k: v for k, v in good["stack"].items() if k != "numpy"}
    assert b5.host_record_failures_5(bad2)


@pytest.mark.slow
def test_committed_manifest_loads_and_spines_are_nine_distinct():
    m = b5.load_manifest_5(sha_pin=None)
    for size in b5.SIZES_5:
        sp = b5.spine_5(m, size)
        assert len(sp) == 9 and sp[-1] == 143000 and list(sp) == sorted(set(sp))
        assert b5.available_5(m, size)[-1] == 143000
        assert 0 not in b5.available_5(m, size)
    assert "64000" in m["2.8b"]["excluded"]
