# experiments/exp2h/tests/test_battery_2h.py
"""battery_2h: R_69 re-derives from 2c's committed m4 6.9b counts +
2d's floor; the 6.9b manifest builds from the committed Hub inventory
with clean uniqueness; sampler_counts generalizes analyze_2g's 1b-only
loader to a size argument and reproduces it on the shared rungs; the
frozen exp2g pins hold. Zero model contact, zero network — the
committed `hub_inventory_69.json` is the only Hub data touched."""
import json

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import analyze_2g as an2g
from experiments.exp2g import battery_2g as bg
from experiments.exp2h import battery_2h as bh


def test_size_repo_and_grid():
    assert bh.SIZE == "6.9b"
    assert bh.REPO_69 == "EleutherAI/pythia-6.9b"
    assert bh.GRID_69[0] == 0 and bh.GRID_69[-1] == 143000
    assert len(bh.GRID_69) == 23
    assert bh.n_trained_69() == 22
    assert bh.trained_steps_69() == tuple(s for s in bh.GRID_69 if s != 0)
    assert 64000 in bh.GRID_69                    # unique at 6.9b, no exclusion
    assert bh.EXCLUDED_GRID_69 == {}
    assert bh.revision_of_69(143000) == "main"
    assert bh.revision_of_69(1000) == "step1000"
    assert bh.revision_of_69(0) == "step0"


def test_rung_set_is_the_doc():
    assert bh.R_69 == ("antonym", "antonym6", "add_base8", "sub_base8",
                       "add3_mid", "arith_next", "count_div13", "odd6")
    assert len(bh.R_69) == 8
    assert set(bh.R_69) <= set(bg.PREDICTOR_RUNGS)
    # two rungs never used by 2g's 2.8b primary (R_28)
    assert set(bh.R_69) - set(bg.R_28) == {"count_div13", "odd6"}
    # add3_mid's final count sits under the eligibility floor (disclosed,
    # design §4) — the RUNG SET criterion (clears the floor at all) is a
    # different bar than eligibility (n_pos >= 20 on the realized sweep)
    assert bh.FINAL_COUNT_PIN_69["add3_mid"] < bg.ELIGIBILITY_MIN_POS


def test_final_count_pin_reproduces_m4_all_34_rungs():
    assert len(bh.FINAL_COUNT_PIN_69) == 34
    assert set(bh.FINAL_COUNT_PIN_69) == set(bt.RUNGS)
    counts = bh.load_m4_counts_69()
    assert counts == bh.FINAL_COUNT_PIN_69
    # re-read directly from the committed m4 records, bypassing the pin,
    # so a silently-stale literal cannot pass
    fresh = {}
    for r in bt.RUNGS:
        rec = json.loads(bh.m4_path_69(r).read_text())
        assert rec["capability"] == r and rec["n"] == bt.N_ITEMS
        assert rec["mode"] == "trained" and rec["size"] == "6.9b"
        fresh[r] = rec["correct"]
    assert fresh == bh.FINAL_COUNT_PIN_69


def test_check_rung_set_69_reproduces_from_floors():
    floors = bg.load_floors()
    assert len(floors) == 34
    assert bh.check_rung_set_69(floors) == tuple(bh.R_69)
    # the rung set is exactly what 2d's bar gives on the m4 counts,
    # independent of the pinned tuple's order
    got = bg.rising_by_bar(bh.load_m4_counts_69(), floors)
    assert set(got) == set(bh.R_69)
    with pytest.raises(ValueError):
        bh.check_rung_set_69({**floors, "antonym": 0.99})


def test_frozen_2g_pins():
    bh.check_frozen_2h()
    assert len(bh.FROZEN_2G_SHA256) == 10
    predictor_path = bh.EXP2G / "results" / "predictor" / "predictor.json"
    assert predictor_path in bh.FROZEN_2G_SHA256
    assert bh.FROZEN_2G_SHA256[predictor_path] == bh.PREDICTOR_2G_SHA
    assert bh.PREDICTOR_2G_SHA == \
        "9eadbac316ddc5db7f7af716e406d3434033ccbaceb64a39467febdba757adc7"
    checkpoints_2g_path = bh.EXP2G / "checkpoints_2g.json"
    assert bh.FROZEN_2G_SHA256[checkpoints_2g_path] == an2g.CHECKPOINTS_SHA256
    referents_2g_path = bh.EXP2G / "referents_2g.json"
    assert bh.FROZEN_2G_SHA256[referents_2g_path] == an2g.REFERENTS_FILE_SHA256
    for name in ("battery_2g.py", "labels_2g.py", "strata_2g.py", "stats_2g.py",
                "probe_2g.py", "checkpoints_2g.py", "analyze_2g.py"):
        assert (bh.EXP2G / name) in bh.FROZEN_2G_SHA256


def test_frozen_2g_pins_catch_drift(tmp_path):
    real = dict(bh.FROZEN_2G_SHA256)
    bad_path = next(iter(real))
    bh.FROZEN_2G_SHA256[bad_path] = "0" * 64
    try:
        with pytest.raises(ValueError):
            bh.check_frozen_2h()
    finally:
        bh.FROZEN_2G_SHA256[bad_path] = real[bad_path]
    bh.check_frozen_2h()   # restored — must pass again


# ------------------------------------------------------------- manifest

def test_manifest_from_committed_inventory():
    inv = bh.load_inventory_69()
    manifest = bh.build_manifest_69(inv)
    entries = manifest["entries"]
    assert manifest["size"] == "6.9b" and manifest["repo"] == bh.REPO_69
    assert len(entries) == 23                     # 22 trained + step0
    assert set(entries) == {str(s) for s in bh.GRID_69}
    kinds = {step: e["kind"] for step, e in entries.items()}
    assert kinds["143000"] == "safetensors-shards"
    assert all(k == "bin-shards" for step, k in kinds.items() if step != "143000")
    # uniqueness: every entry's (kind, lfs shas) signature is distinct
    sigs = {step: (e["kind"], tuple(sorted(e["lfs_sha256"].items())))
            for step, e in entries.items()}
    assert len(set(sigs.values())) == len(sigs)
    # the final grid point is 2c's pinned main commit
    from models import PYTHIA_SHAS
    assert entries["143000"]["commit"] == PYTHIA_SHAS["6.9b"]
    assert manifest["main_commit"] == PYTHIA_SHAS["6.9b"]
    # candidate()/signature() are kind-specific: main resolves to
    # safetensors-shards (it publishes safetensor shards) and
    # step143000 resolves to bin-shards (it does not), so `dups_of`'s
    # kind-matched comparison — the SAME rule 2g's own committed
    # manifest uses, where both its 2.8b and 12b `final_duplicates`
    # are also [] despite each having a byte-identical hub_step143000
    # — cannot place step143000 in `final_duplicates`. The
    # byte-identity design §3.2 calls out ("step143000 byte-identical
    # to main") is carried in `hub_step143000.signature_equals_main`
    # instead, exactly where 2g's 12b manifest carries the analogous
    # fact. See task-1-report.md for the full discrepancy note against
    # the plan's literal `final_duplicates == ["step143000"]`.
    assert manifest["final_duplicates"] == []
    assert manifest["hub_step143000"]["signature_equals_main"] is True
    assert manifest["hub_step143000"]["duplicates"] == []
    assert manifest["stale_main_copies"] == {"model.safetensors": 0,
                                             "pytorch_model.bin": 0}
    assert manifest["excluded"] == {} and manifest["exclusion_evidence"] == {}
    assert manifest["grid"] == list(bh.GRID_69)
    assert manifest["trained_steps"] == list(bh.trained_steps_69())


def test_manifest_sha_matches_generated_file():
    # written by the module __main__ (Task 1's last step); if present,
    # it must hash-match a fresh build from the committed inventory
    if not bh.CHECKPOINTS_PATH_69.is_file():
        pytest.skip("checkpoints_2h.json not yet generated")
    inv = bh.load_inventory_69()
    fresh = bh.build_manifest_69(inv)
    on_disk = json.loads(bh.CHECKPOINTS_PATH_69.read_text())
    assert on_disk == fresh
    got = bg.sha256_file(bh.CHECKPOINTS_PATH_69)
    reloaded = bh.load_manifest_69(bh.CHECKPOINTS_PATH_69, sha_pin=got)
    assert reloaded == fresh


def test_load_manifest_69_refuses_wrong_sha(tmp_path):
    inv = bh.load_inventory_69()
    manifest = bh.build_manifest_69(inv)
    p = tmp_path / "checkpoints_2h.json"
    bh.write_manifest_69(p, manifest)
    with pytest.raises(ValueError):
        bh.load_manifest_69(p, sha_pin="0" * 64)
    got = bg.sha256_file(p)
    loaded = bh.load_manifest_69(p, sha_pin=got)
    assert loaded == manifest


def test_entry_69():
    inv = bh.load_inventory_69()
    manifest = bh.build_manifest_69(inv)
    e = bh.entry_69(manifest, 1000)
    assert e["revision"] == "step1000"
    e_final = bh.entry_69(manifest, 143000)
    assert e_final["revision"] == "main"
    with pytest.raises(ValueError):
        bh.entry_69(manifest, 999999)


# --------------------------------------------------------- sampler_counts

def test_sampler_counts_1b_matches_2g_on_overlap_rungs():
    overlap = tuple(sorted(set(bg.R_28) & set(bh.R_69)))
    assert overlap == ("add3_mid", "add_base8", "antonym", "antonym6",
                       "arith_next", "sub_base8")
    from experiments.exp2d import analyze_2d as a2d
    battery = bt.load_battery()
    verify_fn = a2d.load_verify()
    reference = an2g.sampler_counts_1b(bg.EXP2D, battery, verify_fn, overlap)
    got = bh.sampler_counts("1b", overlap)
    assert set(got) == set(reference)
    for r in overlap:
        assert got[r] == reference[r]
    # four named spot values (item 0 of four of the six overlap rungs) —
    # pinned literals, re-derived live above so a stale literal cannot
    # pass silently
    spot = {"antonym": reference["antonym"][0], "antonym6": reference["antonym6"][0],
           "add_base8": reference["add_base8"][0], "arith_next": reference["arith_next"][0]}
    assert got["antonym"][0] == spot["antonym"]
    assert got["antonym6"][0] == spot["antonym6"]
    assert got["add_base8"][0] == spot["add_base8"]
    assert got["arith_next"][0] == spot["arith_next"]


def test_sampler_counts_410m_shape():
    got = bh.sampler_counts("410m", ("antonym",))
    assert set(got) == {"antonym"}
    assert len(got["antonym"]) == bt.N_ITEMS
    assert all(0 <= c <= 64 for c in got["antonym"])


def test_sampler_counts_rejects_bad_size():
    with pytest.raises(ValueError):
        bh.sampler_counts("6.9b", bh.R_69)


# --------------------------------------------------------------- paths

def test_paths(tmp_path):
    assert bh.record_path_2h(tmp_path, 1000, "antonym") == \
        tmp_path / "results" / "sweep" / "6.9b" / "step1000" / "antonym.json"
    assert bh.checkpoint_record_path_2h(tmp_path, 1000).name == "_checkpoint.json"
    assert bh.gate1_path_2h(tmp_path) == \
        tmp_path / "results" / "sweep" / "6.9b" / "gate1.json"
    assert bh.halt_marker_path_2h(tmp_path).name == "HALTED"
    assert bh.CHECKPOINTS_PATH_69.name == "checkpoints_2h.json"
    assert bh.HUB_INVENTORY_PATH_69.name == "hub_inventory_69.json"


# ---------------------------------------------------------------- loader
#
# The loader family is parameterized and imports huggingface_hub/torch
# lazily inside each function body — never at module import — so this
# suite never touches the network or a model. We only assert the
# functions exist with the right shape and that ck.tensor_digest is
# reused (not redefined) by battery_2h.

def test_loader_family_present_and_not_executed():
    for name in ("download_entry_69", "clean_dir_69", "load_checkpoint_69",
                "free_69"):
        assert callable(getattr(bh, name))
    assert not hasattr(bh, "tensor_digest")   # reused via ck import, not redefined
    import experiments.exp2g.checkpoints_2g as ck
    assert bh.ck is ck
